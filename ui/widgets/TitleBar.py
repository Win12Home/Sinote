from PySide6.QtCore import QPoint, Qt, Signal
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget
from ui.widgets.SeperatorWidget import SeperatorWidget


class TitleBar(QWidget):
    closeTriggered = Signal()
    minimizeTriggered = Signal()
    maximizeTriggered = Signal()
    windowsMoveRequest = Signal(QPoint)

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self._draggingEvent: bool = False
        self._firstRecordPosition: QPoint | None = None
        self._otherButtonStyleSheet: str = (
            r"QPushButton {"
            r"    border: none;"
            r"    width: 10%;"
            r"}"
            r"QPushButton::hover {"
            r"    color: gray;"
            r"}"
            r"QPushButton::pressed {}"
        )
        self._closeButtonStyleSheet: str = (
            r"QPushButton {"
            r"    border: none;"
            r"    width: 10%;"
            r"}"
            r"QPushButton::hover {"
            r"    background-color: red;"
            r"    color: white;"
            r"}"
            r"QPushButton::pressed {}"
        )
        self._vLayout: QVBoxLayout = QVBoxLayout()
        self._vLayout.setContentsMargins(0, 0, 0, 0)
        self._vLayout.setSpacing(0)
        self._layout: QHBoxLayout = QHBoxLayout()
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)
        self._title: QLabel = QLabel("Frameless Window")
        self._title.setStyleSheet(f"font-size: 13px;")
        self._minimize: QPushButton = QPushButton()
        self._minimize.setText("—")
        self._minimize.setStyleSheet(
            f"{self._minimize.styleSheet()}{self._otherButtonStyleSheet}"
        )
        self._minimize.clicked.connect(lambda: self.minimizeTriggered.emit())
        self._minimize.font().setPixelSize(8)
        self._maximize: QPushButton = QPushButton()
        self._maximize.setText("□")  # Magically
        self._maximize.setStyleSheet(
            f"{self._maximize.styleSheet()}{self._otherButtonStyleSheet}"
        )
        self._maximize.clicked.connect(lambda: self.maximizeTriggered.emit())
        self._maximize.font().setPixelSize(8)
        self._close: QPushButton = QPushButton()
        self._close.setText("X")  # UTF-8 need
        self._close.setStyleSheet(
            f"{self._close.styleSheet()}{self._closeButtonStyleSheet}"
        )
        self._close.font().setPixelSize(8)
        self._close.clicked.connect(lambda: self.closeTriggered.emit())
        self._layout.addWidget(
            self._title, alignment=Qt.AlignmentFlag.AlignLeft, stretch=2
        )
        self._layout.addWidget(
            self._minimize, alignment=Qt.AlignmentFlag.AlignRight, stretch=0
        )
        self._layout.addWidget(
            self._maximize, alignment=Qt.AlignmentFlag.AlignRight, stretch=0
        )
        self._layout.addWidget(
            self._close, alignment=Qt.AlignmentFlag.AlignRight, stretch=0
        )
        self._seperator: SeperatorWidget = SeperatorWidget()
        self._vLayout.addLayout(self._layout)
        self._vLayout.addWidget(self._seperator)
        self.setLayout(self._vLayout)
        self.setMinimumHeight(30)
        self.setMaximumHeight(30)
        self.setMinimumWidth(400)
        self.setContentsMargins(0, 0, 0, 0)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._draggingEvent = True
            self._firstRecordPosition = event.globalPosition().toPoint()
        return super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if (
            self._draggingEvent
            and (event.buttons() & Qt.MouseButton.LeftButton)
            == Qt.MouseButton.LeftButton
        ):
            currentPosition: QPoint = event.globalPosition().toPoint()
            offset: QPoint = currentPosition - self._firstRecordPosition
            self.windowsMoveRequest.emit(offset)
            self._firstRecordPosition = currentPosition
        return super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._firstRecordPosition = None
            self._draggingEvent = False
        return super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
        self.maximizeTriggered.emit()
        return super().mouseDoubleClickEvent(event)

    def setWindowTitle(self, content: str) -> None:
        self._title.setText(content)
        self._title.repaint()

    def setOnlyCloseButton(self) -> None:
        self._maximize.setVisible(False)
        self._minimize.setVisible(False)
        self._close.setVisible(True)
