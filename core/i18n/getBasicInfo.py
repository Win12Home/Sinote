import sys
from pathlib import Path

from json5 import loads
from utils.err import err
from utils.logger import Logger


def getBasicInfo():
    lang: str = "en_US"
    try:
        with open(
            f"./resources/language/{lang}/BaseInfo.json", "r", encoding="utf-8"
        ) as f:
            basicInfo = loads(f.read())
    except Exception:
        Logger.error("BaseInfo.json not found", "FileConfigActivity")
        err("0x00000001")
        sys.exit(1)

    for temp in basicInfo["item.list.language_files"]:
        if not Path(f"./resources/language/{lang}/{temp}.json").exists():
            Logger.error("Check Language files failed! ❌", "FileConfigActivity")
            err("0x00000002")
            sys.exit(1)

    return basicInfo
