from PySide6.QtWidgets import QWidget, QCheckBox
from ui.SettingObject.SettingObject import SettingObject


class CheckBoxSettingObject(SettingObject):
    def __init__(
        self,
        parent: QWidget = None,
        text: str = "Unknown Text",
        desc: str = "Unknown Description",
    ):
        super().__init__(parent, text, desc)
        self.checkBox = QCheckBox()
        self.setRightWidget(self.checkBox)
