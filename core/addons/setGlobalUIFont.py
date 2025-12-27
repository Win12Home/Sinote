from PySide6.QtGui import QFontDatabase, QFont
from ui.selfLogger import debugLog  # UwU I'm lazy
from utils.application import application
from typing import Callable
from utils.logger import addLog
from core.i18n import basicInfo
from platform import system

recommendFont: bool = False

isRecommendFont: Callable = lambda: recommendFont


def setGlobalUIFont(font: str = None, recursion: bool = False) -> None:
    global recommendFont
    debugLog("Setting global UI font to MiSans... 🎨")
    selectedFont: str = "MiSans VF" if not font else font  # Customize!
    if selectedFont.lower().strip() not in [
        i.lower().strip() for i in QFontDatabase.families() if isinstance(i, str)
    ]:
        debugLog(
            f"{r"MiSans" if not font else font} isn't in font database! Try to use system recommend font. (Or Fixed font)"
        )
        fnt: str = QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont).family()
        if recursion and fnt.lower() == font.lower():
            addLog(
                2,
                "Cool! We think fixed font is the best option! What's your system? That's so suspend!",
                "SinoteUserInterfaceActivity",
            )
            return
        if (
            recursion
        ):  # Why? If it is not in font database (Recommend font in macOS/Windows), use FixedFont!
            recommendFont = True
            debugLog(
                "Oh my god! Recommend font is not in the database! We think use Fixed font instead!"
            )
            setGlobalUIFont(fnt, recursion=True)
            return
        if system().lower() == "windows":
            fnt = (
                "Segoe UI"
                if not basicInfo.get("item.option.neededmorechar", False)
                else "Microsoft YaHei UI"
            )
        elif system().lower() == "darwin":
            fnt = (
                "San Francisco"
                if not basicInfo.get("item.option.neededmorechar", False)
                else "Heiti SC"
            )
        setGlobalUIFont(fnt, recursion=True)
        return
    globalFont = QFont(selectedFont)
    globalFont.setPointSize(10)
    application.setFont(globalFont)
    application.setStyleSheet(
        f"""
        {application.styleSheet()}
        * {{
            font-family: "{selectedFont}";
        }}
        QWidget {{
            font-family: "{selectedFont}";
        }}
        QLabel {{
            font-family: "{selectedFont}";
        }}
        QPushButton {{
            font-family: "{selectedFont}";
        }}
        QComboBox {{
            font-family: "{selectedFont}";
        }}
        QSpinBox {{
            font-family: "{selectedFont}";
        }}
        QCheckBox {{
            font-family: "{selectedFont}";
        }}
        QMenuBar {{
            font-family: "{selectedFont}";
        }}
        QMenu {{
            font-family: "{selectedFont}";
        }}
        QTabWidget {{
            font-family: "{selectedFont}";
        }}
    """
    )

    addLog(0, f"Global UI font set to: {selectedFont} ✅", "LoadFontActivity")
