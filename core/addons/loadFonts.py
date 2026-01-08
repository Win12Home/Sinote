from PySide6.QtGui import QFontDatabase
from utils.argumentParser import debugMode
from utils.logger import addLog
from pathlib import Path


def loadFonts() -> None:
    fontDatabase = QFontDatabase()
    fontsDir = Path("./resources/fonts")
    if not fontsDir.exists() or not fontsDir.is_dir():
        addLog(
            2,
            "./resources/fonts/ directory isn't exists or it isn't a true directory! ❌",
            "LoadFontActivity",
        )
    if debugMode:
        addLog(3, "Loading fonts in ./resources/fonts... 🤔", "LoadFontActivity")
    loadedFontNums: int = 0
    totalFontNums: int = 0
    for temp in list(fontsDir.rglob("*.ttf")) + list(fontsDir.rglob("*.otf")):
        totalFontNums += 1
        loadReturn: int = fontDatabase.addApplicationFont(str(temp))
        if loadReturn != -1:
            fontDatabase.applicationFontFamilies(loadReturn)
            loadedFontNums += 1
            if debugMode:
                addLog(
                    3, f"Successfully to load font {temp.name} ✅", "LoadFontActivity"
                )
        else:
            addLog(2, f"Failed to load font {temp.name} ❌", "LoadFontActivity")
    if debugMode:
        addLog(
            3,
            f"Successfully to load all the fonts! Total: {totalFontNums} Loaded: {loadedFontNums} Not loaded: {totalFontNums - loadedFontNums}",
            "LoadFontActivity",
        )
