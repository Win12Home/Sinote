from typing import Any

from core.i18n.getBasicInfo import getBasicInfo
from core.i18n.loadJson import lang, getLangJson
from core.i18n.setLanguage import setLanguage

__all__ = [
    "getBasicInfo",
    "getLangJson",
    "resetBasicInfo",
    "basicInfo",
    "setLanguage",
    "lang",
]

basicInfo: dict[Any, Any] = getBasicInfo()


def resetBasicInfo() -> None:
    global basicInfo
    basicInfo = getBasicInfo() | getLangJson("BasicInfo")
