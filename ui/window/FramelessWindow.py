from enum import Enum
from platform import system

from PySide6.QtCore import QPoint, QRect, Qt, QTimer, Signal, QObject, QEvent, QSize
from PySide6.QtGui import (
    QColor,
    QMouseEvent,
    QPainter,
    QPaintEvent,
    QPalette,
    QPen,
    QResizeEvent,
)
from PySide6.QtWidgets import QMainWindow, QMenuBar, QVBoxLayout, QWidget, QApplication

from ui.widgets.TitleBar import TitleBar
from utils.logger import Logger


isWayland: bool = QApplication.platformName().lower() == "wayland"  # Fix issue that Windows, XCB(X11) and other system will not change shape when cursor is at the border of the window.
isX11: bool = QApplication.platformName().lower() in ["x11", "xcb"]

def mapToSelf(self: QWidget, pos: QPoint) -> QPoint:
    return pos if isWayland else pos - self.pos()  # Wayland is locality position, but others not.

class Edge(Enum):
    TopLeft = 0
    TopRight = 1
    BottomRight = 2
    BottomLeft = 3
    Top = 4
    Bottom = 5
    Left = 6
    Right = 7


class BorderCentralWidget(QWidget):
    resizeRequest = Signal(Edge)

    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)
        self.setContentsMargins(1, 1, 1, 1)
        self.notMaximized = True
        self.dragMaximumSize = 10  # px
        self.cursorShapeChangeDisabled = False
        self.scalingDisabled = False
        self.lastCursorPos = None
        self.nowCursorPos = None
        self.shapeChecker = QTimer(self)
        self.shapeChecker.timeout.connect(
            lambda: self.analyzeMouseCursorAndEdge(mapToSelf(self, self.cursor().pos()).toTuple())
        )
        self.shapeChecker.start(10)

    def paintEvent(self, event: QPaintEvent) -> None:
        if not self.notMaximized:
            painter = QPainter(self)
            painter.setBrush(self.palette().color(QPalette.ColorRole.Window))
            painter.setPen(self.palette().color(QPalette.ColorRole.Window))
            painter.drawRect(self.rect())
        else:
            painter = QPainter(self)
            painter.setPen(QPen(QColor(Qt.GlobalColor.lightGray), 3))
            painter.setBrush(self.palette().color(QPalette.ColorRole.Window))
            painter.drawRoundedRect(
                QRect(1, 1, self.width() - 2, self.height() - 2), 12.5, 12.5
            )

    def analyzeMouseCursorAndEdge(self, pointTuple: tuple[float, float]) -> Edge | None:
        if self.cursorShapeChangeDisabled or self.scalingDisabled:
            return None

        x, y = pointTuple
        inLeft: bool = x <= self.dragMaximumSize
        inRight: bool = (
            self.width() - self.dragMaximumSize
            <= x
            <= self.width() + self.dragMaximumSize
        )
        inTop: bool = y <= self.dragMaximumSize
        inBottom: bool = (
            self.height() - self.dragMaximumSize
            <= y
            <= self.height() + self.dragMaximumSize
        )

        # NOTE: I really hasn't known any methods to improve my if-elif-else code QwQ

        cursorShapes: list[Qt.CursorShape] = [
            Qt.CursorShape.SizeFDiagCursor,
            Qt.CursorShape.SizeBDiagCursor,
            Qt.CursorShape.SizeHorCursor,
            Qt.CursorShape.SizeVerCursor,
        ]

        edge: Edge | None = None

        if inLeft and inTop or inRight and inBottom:  # There wasn't any readable, em...
            self.setCursor(cursorShapes[0])
            edge = Edge.TopLeft if inLeft else Edge.BottomRight
        elif inLeft and inBottom or inRight and inTop:
            self.setCursor(cursorShapes[1])
            edge = Edge.BottomLeft if inBottom else Edge.TopRight
        elif inLeft or inRight:
            self.setCursor(cursorShapes[2])
            edge = Edge.Left if inLeft else Edge.Right
        elif inTop or inBottom:
            self.setCursor(cursorShapes[3])
            edge = Edge.Top if inTop else Edge.Bottom
        elif self.cursor().shape() in cursorShapes:
            self.setCursor(Qt.CursorShape.ArrowCursor)

        return edge

    def mousePressEvent(self, event: QMouseEvent, /) -> None:
        if event.button() != Qt.MouseButton.LeftButton or self.scalingDisabled:
            return super().mousePressEvent(event)

        shape = self.analyzeMouseCursorAndEdge(mapToSelf(self, self.cursor().pos()).toTuple())
        self.cursorShapeChangeDisabled = True

        self.resizeRequest.emit(shape)

        return super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent, /) -> None:
        if self.scalingDisabled:
            return super().mouseReleaseEvent(event)

        self.cursorShapeChangeDisabled = False

        if event.button() == Qt.MouseButton.LeftButton and self.cursor().shape() in [
            Qt.CursorShape.SizeFDiagCursor,
            Qt.CursorShape.SizeBDiagCursor,
            Qt.CursorShape.SizeHorCursor,
            Qt.CursorShape.SizeVerCursor,
        ]:
            self.cursor().setShape(Qt.CursorShape.ArrowCursor)

        return super().mouseReleaseEvent(event)


class FramelessWindow(QMainWindow):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self._lastCursorPosition: QPoint | None = None
        self._nowCursorPosition: QPoint | None = None

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self._layout = QVBoxLayout()
        self._widget: BorderCentralWidget = BorderCentralWidget()
        self._widget.resizeRequest.connect(self.analyzeWindowResizing)
        self.__menuBar: QMenuBar | QWidget = QWidget()
        self.__painter: QPainter | None = None
        self.titleBar = TitleBar()
        self.titleBar.closeTriggered.connect(lambda: self.close())
        self.titleBar.minimizeTriggered.connect(lambda: self.showMinimized())
        self.titleBar.maximizeTriggered.connect(lambda: self.__maximized())
        self.titleBar.windowsMoveRequest.connect(self.analyzeWindowMoving)
        self.titleBar.raise_()
        self._layout.addWidget(
            self.titleBar, alignment=Qt.AlignmentFlag.AlignTop, stretch=0
        )
        self._layout.addWidget(self.__menuBar, stretch=0)
        self._widget.setLayout(self._layout)
        self._widget.repaint()
        self._widget.setMouseTracking(True)
        self.installEventFilter(self)

        for item in self.children():
            item.installEventFilter(self)

        super().setCentralWidget(self._widget)

    def eventFilter(self, obj: QObject, event: QEvent) -> bool:
        if event.type() in [
            QEvent.Type.MouseButtonPress,
            QEvent.Type.MouseButtonRelease,
            QEvent.Type.MouseMove,
        ]:
            if mapToSelf(self, self.cursor().pos()) != self._nowCursorPosition:
                self._lastCursorPosition = self._nowCursorPosition
                self._nowCursorPosition = mapToSelf(self, self.cursor().pos())
        return False

    def setScalingDisabled(self, value: bool) -> None:
        self._widget.scalingDisabled = value

    def analyzeWindowMoving(self, moveOffset: QPoint) -> None:
        if not self.isMaximized():
            if hasattr(self.windowHandle(), "startSystemMove") and system().lower() in [
                "windows",
                "linux",
            ] and not isX11:  # Fix issues that cannot move in Wayland and supported system dragging
                self.windowHandle().startSystemMove()
            else:
                self.move(self.pos() + moveOffset)
            self.repaint()

    def analyzeWindowResizing(self, resizeEdge: Edge) -> None:
        if hasattr(self.windowHandle(), "startSystemResize") and system().lower() in [
            "windows",
            "linux",
        ] and not isX11:
            edgeInQt: Qt.Edge | None = None
            if resizeEdge == Edge.Left:
                edgeInQt = Qt.Edge.LeftEdge
            elif resizeEdge == Edge.Right:
                edgeInQt = Qt.Edge.RightEdge
            elif resizeEdge == Edge.Bottom:
                edgeInQt = Qt.Edge.BottomEdge
            elif resizeEdge == Edge.Top:
                edgeInQt = Qt.Edge.TopEdge
            elif resizeEdge == Edge.TopLeft:
                edgeInQt = Qt.Edge.TopEdge | Qt.Edge.LeftEdge  # NOQA
            elif resizeEdge == Edge.TopRight:
                edgeInQt = Qt.Edge.TopEdge | Qt.Edge.RightEdge  # NOQA
            elif resizeEdge == Edge.BottomLeft:
                edgeInQt = Qt.Edge.BottomEdge | Qt.Edge.LeftEdge  # NOQA
            elif resizeEdge == Edge.BottomRight:
                edgeInQt = Qt.Edge.BottomEdge | Qt.Edge.RightEdge  # NOQA

            if edgeInQt:
                self.windowHandle().startSystemResize(edgeInQt)
        elif system().lower() not in ["windows", "linux"]:
            if not (self._nowCursorPosition and self._lastCursorPosition):
                return

            difference: QPoint = self._nowCursorPosition - self._lastCursorPosition
            self.resize(self.size() + QSize(difference.x(), difference.y()))
            self.move(self.pos() + difference)
        else:
            Logger.error(
                '"startSystemResize" function is not in "QWindow" object, make sure you are using Qt 5.15+.',
                "MainWindowActivity",
            )

    def setWindowTitle(self, title: str) -> None:
        self.titleBar.setWindowTitle(title)
        return super().setWindowTitle(title)

    def __maximized(self) -> None:
        if self.isMaximized():
            self.showNormal()
            return
        self.showMaximized()

    def setCentralWidget(self, widget: QWidget) -> None:
        while self._layout.count() != 1:
            gotItem = self._layout.takeAt(1)
            if not gotItem:
                continue
            if gotItem.widget():
                gotItem.widget().deleteLater()
        self._layout.addWidget(self.__menuBar, stretch=0)
        self._layout.addWidget(widget, stretch=2)
        self._widget.setLayout(self._layout)

    def setMenuBar(self, menuBar: QMenuBar) -> None:
        self.__menuBar = menuBar
        self.__menuBar.setStyleSheet(
            f"{self.__menuBar.styleSheet()} border-radius: 5px;"
        )

    def resizeEvent(self, event: QResizeEvent) -> None:
        if self.isMaximized():
            self._widget.notMaximized = False
        else:
            self._widget.notMaximized = True
        self._widget.repaint()
        self.repaint()
        return super().resizeEvent(event)
