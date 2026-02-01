from PySide6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget


class SettingObject(QWidget):
    def __init__(
        self,
        parent: QWidget = None,
        text: str = "Unknown Text",
        desc: str = "Unknown Description",
    ):
        super().__init__(parent)
        self.mainLayout: QHBoxLayout = QHBoxLayout(self)
        self.mainLayout.setContentsMargins(15, 10, 15, 10)
        self.mainLayout.setSpacing(20)
        self.leftLayout: QVBoxLayout = QVBoxLayout()
        self.leftLayout.setSpacing(5)
        self.titleLabel: QLabel = QLabel(text)
        self.titleLabel.setStyleSheet("font-size: 14pt; font-weight: bold;")
        self.leftLayout.addWidget(self.titleLabel)
        self.descLabel: QLabel = QLabel(desc)
        self.descLabel.setStyleSheet("font-size: 10pt; color: gray;")
        self.descLabel.setWordWrap(True)
        self.leftLayout.addWidget(self.descLabel)
        self.leftLayout.addStretch()
        self.rightWidget: QWidget | None = None
        self.mainLayout.addLayout(self.leftLayout, 3)
        self.mainLayout.addStretch(1)
        self.setMinimumHeight(80)

    def setText(self, text: str) -> None:
        self.titleLabel.setText(text)

    def setDesc(self, desc: str) -> None:
        self.descLabel.setText(desc)

    def setRightWidget(self, widget: QWidget) -> None:
        if self.rightWidget is not None:
            self.mainLayout.removeWidget(self.rightWidget)
            self.rightWidget.deleteLater()
        self.rightWidget = widget
        self.rightWidget.setMinimumWidth(200)
        self.rightWidget.setMaximumWidth(400)
        self.mainLayout.addWidget(self.rightWidget, 2)

    def getRightWidget(self) -> QWidget | None:
        return self.rightWidget
