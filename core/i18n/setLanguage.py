from core.i18n.loadJson import setLang
from utils.config import settingObject
from pathlib import Path


def setLanguage() -> None:
    setLang(
        settingObject.getValue("language")
        if Path(f"./resources/language/{settingObject.getValue("language")}").exists()
        else "en_US"
    )
