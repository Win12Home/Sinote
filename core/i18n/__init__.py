from core.i18n.getBasicInfo import getBasicInfo
from core.i18n.loadJson import loadJson, lang
from core.i18n.setLanguage import setLanguage
from typing import Any

__all__ = [
    "getBasicInfo",
    "loadJson",
    "resetBasicInfo",
    "basicInfo",
    "setLanguage",
    "lang",
]

basicInfo: dict[Any, Any] = getBasicInfo()


def resetBasicInfo() -> None:
    global basicInfo
    basicInfo = getBasicInfo() | loadJson("BasicInfo")
