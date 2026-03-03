from PySide6.QtCore import QPoint, Qt, QRect, Signal, QMargins
from PySide6.QtGui import QPaintEvent, QPainter, QPen, QColor, QPalette, QResizeEvent, QMouseEvent
from PySide6.QtWidgets import QMainWindow, QMenuBar, QVBoxLayout, QWidget
from ui.widgets.TitleBar import TitleBar


class BorderCentralWidget(QWidget):
    resizeRequest = Signal(QMargins)

    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)
        self.setContentsMargins(1, 1, 1, 1)
        self.notMaximized = True
        self.startResizing = False  # Wow, yeah, just a recording variable

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
            painter.drawRoundedRect(QRect(1, 1, self.width() - 2, self.height() - 2), 12.5, 12.5)

    def mousePressEvent(self, event, /) -> None:
        position = event.position()
        return super().mousePressEvent(event)  # TODO: Resizeable Window


class FramelessWindow(QMainWindow):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self._layout = QVBoxLayout()
        self.__widget: BorderCentralWidget = BorderCentralWidget()
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
        self.__widget.setLayout(self._layout)
        self.__widget.repaint()
        self.__widget.setMouseTracking(True)
        super().setCentralWidget(self.__widget)

    def analyzeWindowMoving(self, moveOffset: QPoint) -> None:
        if not self.isMaximized():
            if hasattr(self.windowHandle(), "startSystemMove"):  # Fix issues that cannot move in Wayland and supported system dragging
                self.windowHandle().startSystemMove()
            else:
                self.move(self.pos() + moveOffset)
            self.repaint()

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
        self.__widget.setLayout(self._layout)

    def setMenuBar(self, menuBar: QMenuBar) -> None:
        self.__menuBar = menuBar
        self.__menuBar.setStyleSheet(
            f"{self.__menuBar.styleSheet()} border-radius: 5px;"
        )

    def resizeEvent(self, event: QResizeEvent) -> None:
        if self.isMaximized():
            self.__widget.notMaximized = False
        else:
            self.__widget.notMaximized = True
        self.__widget.repaint()
        self.repaint()
        return super().resizeEvent(event)