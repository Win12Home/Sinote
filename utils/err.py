from PySide6.QtWidgets import QWidget, QMessageBox
from utils.logger import addLog, saveLog


def err(error_code: str, parent: QWidget = None, no_occurred: bool = False) -> None:
    if not no_occurred:
        addLog(
            2,
            bodyText="Error Occurred, Program Used Function err to aborted running! Error Code: {}".format(
                error_code
            ),
            activity="WindowsActivity",
        )
        w = QMessageBox.critical(
            None,
            "Error",
            "Sinote has found a error! \nError Code: {}\nPlease contact developer or re-install software!".format(
                error_code
            ),
        )
    if not no_occurred:
        addLog(2, bodyText="Saving Error to local", activity="FileConfigActivity")
        saveLog()
    """
    Error Codes
    0xffffffff: Unknown Error, Traceback Hook Detected!
    0x00000001: BaseInfo.json not found, re-install software
    0x00000002: Other Language File not found, re-install software
    0x00000003: System isn't support (Only MacOS, Windows and Linux), use --bypass-system-check to bypass system check!
    """
