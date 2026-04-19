import sys

from PySide6.QtWidgets import QApplication, QMessageBox, QWidget
from PySide6.QtGui import QIcon

from utils.logger import Logger, saveLog


def err(errorCode: str, parent: QWidget = None, noSaveLog: bool = False) -> None:
    if QApplication.instance() is None:
        app = QApplication([])
    Logger.error(
        "Error Occurred, Program Used Function err to aborted running! Error Code: {}".format(
            errorCode
        ),
        "WindowsActivity",
    )
    w = QMessageBox(
        QMessageBox.Icon.Critical,
        "Error",
        "Sinote has found a error! \nError Code: {}\nPlease contact developer or re-install software!".format(
            errorCode
        ),
        buttons=QMessageBox.StandardButton.Ok,
        parent=None,
    )
    w.setWindowIcon(QIcon("resources/icon.png"))
    w.exec()
    if not noSaveLog:
        Logger.error("Saving Error to local", "FileConfigActivity")
        saveLog()
    """
    Error Codes
    0xffffffff: Unknown Error, Traceback Hook Detected!
    0x00000001: BaseInfo.json not found, re-install software
    0x00000002: Other Language File not found, re-install software
    0x00000003: System isn't support (Only MacOS, Windows and Linux), use --bypass-system-check to bypass system check!
    """
