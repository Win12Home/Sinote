import sys

from PySide6.QtWidgets import QMessageBox, QWidget, QApplication
from utils.logger import Logger, saveLog


def err(errorCode: str, parent: QWidget = None, no_occurred: bool = False) -> None:
    if QApplication.instance() is None:
        app = QApplication([])
    if not no_occurred:
        Logger.error(
            "Error Occurred, Program Used Function err to aborted running! Error Code: {}".format(
                errorCode
            ),
            "WindowsActivity",
        )
        w = QMessageBox.critical(
            None,
            "Error",
            "Sinote has found a error! \nError Code: {}\nPlease contact developer or re-install software!".format(
                errorCode
            ),
        )
    if not no_occurred:
        Logger.error("Saving Error to local", "FileConfigActivity")
        saveLog()
    """
    Error Codes
    0xffffffff: Unknown Error, Traceback Hook Detected!
    0x00000001: BaseInfo.json not found, re-install software
    0x00000002: Other Language File not found, re-install software
    0x00000003: System isn't support (Only MacOS, Windows and Linux), use --bypass-system-check to bypass system check!
    """
