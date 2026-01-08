from PySide6.QtWidgets import QWidget
from PySide6.QtCore import QThread
from ui.selfLogger import debugLog
from utils.config import settingObject
import time


class AutomaticSaveThingsThread(QThread):
    def __init__(self, parent: QWidget = None, saveSecs: int = 10):
        super().__init__(parent)
        self.saveSecs: int = saveSecs
        self.running: bool = True
        self.ended: bool = False

    def reset(self) -> None:
        self.saveSecs = settingObject.getValue("secsave")

    def saveThings(self) -> None:
        debugLog(f"Automatic saving every {self.saveSecs} secs 😍")
        if not self.parent() or not hasattr(self.parent(), "tabTextEdits"):
            debugLog(
                'Skipped saveThings because attribute "tabTextEdits" destroyed! 😰'
            )  # Automatic skip when not have attribute tabTextEdits
            return
        for temp in (
            getEditor
            for getEditor in self.parent().tabTextEdits
            if getEditor is not None and hasattr(getEditor, "autoSave")
        ):  # UwU I'm lazy, so I tried to use list but my memory is lazy, so I edit to Generator
            debugLog(f"Saving file {temp.nowFilename} ✅")
            temp.autoSave()
        debugLog("Save successfully! ✅")
        debugLog("Waiting for next cycle... 💥")

    def run(self) -> None:
        while self.running:
            for temp in range(self.saveSecs * 10):
                time.sleep(0.1)
                if not self.running:
                    self.saveThings()
                    break
            if self.running:
                self.saveThings()
        debugLog("AutomaticSaveThingsThread ended")
        self.ended = True
        super().quit()

    def quit(self):
        self.running = False
        debugLog("AutomaticSaveThingsThread has closed by this->quit 💥")
