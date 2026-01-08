from PySide6.QtWidgets import QApplication
from utils.logger import addLog

__all__ = ["applyStylesheet"]


def getFileContent(file: str) -> str:
    try:
        with open(file, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        addLog(
            2,
            f"Failed to read stylesheet file {file}! Use normalize style instead.",
            "ApplyStylesheetActivity",
        )
        return ""


def applyStylesheet(application: QApplication, theme: int) -> None:
    application.setStyleSheet(
        getFileContent("./resources/theme/light.qss")
        if theme == 0
        else getFileContent("./resources/theme/dark.qss")
    )
