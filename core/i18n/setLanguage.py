from pathlib import Path

from core.i18n.getLangJson import setLang
from utils.config import settingObject


def setLanguage() -> None:
    setLang(
        settingObject.getValue("language")
        if Path(f"./resources/language/{settingObject.getValue("language")}").exists()
        else "en_US"
    )
