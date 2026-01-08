from PySide6.QtWidgets import QWidget, QComboBox, QFontComboBox
from ui.SettingObject.SettingObject import SettingObject


class ComboBoxSettingObject(SettingObject):
    def __init__(
        self,
        parent: QWidget = None,
        text: str = "Unknown Text",
        desc: str = "Unknown Description",
    ):
        super().__init__(parent, text, desc)
        self.comboBox = QComboBox()
        self.setRightWidget(self.comboBox)

    def useNormalBox(self):
        self.comboBox.deleteLater()
        self.comboBox = QComboBox()
        self.setRightWidget(self.comboBox)

    def useFontBox(self):
        self.comboBox.deleteLater()
        self.comboBox = QFontComboBox()
        self.setRightWidget(self.comboBox)
