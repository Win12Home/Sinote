from PySide6.QtCore import QPoint, Qt
from PySide6.QtGui import QResizeEvent
from PySide6.QtWidgets import QMainWindow, QMenuBar, QVBoxLayout, QWidget
from ui.widgets.TitleBar import TitleBar


class FramelessWindow(QMainWindow):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self._layout = QVBoxLayout()
        self.__widget = QWidget()
        self.__menuBar: QMenuBar | QWidget = QWidget()
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
        super().setCentralWidget(self.__widget)

    def analyzeWindowMoving(self, moveOffset: QPoint) -> None:
        if not self.isMaximized():
            self.move(self.pos() + moveOffset)

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

    def resizeEvent(self, event: QResizeEvent, /) -> None:
        self.repaint()
        return super().resizeEvent(event)
