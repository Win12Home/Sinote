from PySide6.QtWidgets import QWidget, QLineEdit, QSpinBox
from ui.SettingObject.SettingObject import SettingObject


class LineEditSettingObject(SettingObject):
    def __init__(
        self,
        parent: QWidget = None,
        text: str = "Unknown Text",
        desc: str = "Unknown Description",
    ):
        super().__init__(parent, text, desc)
        self.lineEdit = QLineEdit()
        self.setRightWidget(self.lineEdit)

    def useNormalEdit(self):
        self.lineEdit.deleteLater()
        self.lineEdit = QLineEdit()
        self.setRightWidget(self.lineEdit)

    def useSpinBox(self):
        self.lineEdit.deleteLater()
        self.lineEdit = QSpinBox()
        self.setRightWidget(self.lineEdit)
