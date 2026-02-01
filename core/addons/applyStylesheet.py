from PySide6.QtWidgets import QApplication
from utils.argumentParser import debugMode
from utils.logger import Logger

__all__ = ["applyStylesheet"]


def getFileContent(file: str) -> str:
    try:
        with open(file, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        Logger.warning(
            f"Failed to read stylesheet file {file}! Reason: {e!r}",
            "ApplyStylesheetActivity",
        )
        return ""


def applyStylesheet(application: QApplication, theme: int) -> None:
    if debugMode:
        Logger.debug(
            f"Applying stylesheet number {theme}...", "ApplyStylesheetActivity"
        )
    defaultThemes: dict[int, str] = {0: "light", 1: "dark"}
    application.setStyleSheet(
        getFileContent(f"./resources/theme-{defaultThemes.get(theme, 1)}/theme.qss")
    )
