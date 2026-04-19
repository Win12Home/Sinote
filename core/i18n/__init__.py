from typing import Any

from core.i18n.getBasicInfo import getBasicInfo
from core.i18n.getLangJson import getLangJson, lang
from core.i18n.setLanguage import setLanguage

__all__ = [
    "getBasicInfo",
    "getLangJson",
    "baseInfo",
    "setLanguage",
    "lang",
]


def baseInfo() -> dict[str, Any]:
    return getLangJson("BaseInfo")
