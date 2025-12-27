from utils.argumentParser import debugMode
from utils.SafetyMutable import SafetyDict
from utils.jsonLoader import load
from utils.logger import addLog

alreadyLoaded: SafetyDict[str, dict] = {}
# Cache Language File (What is @lru_cache? I cannot be got it.)
alreadyLoadedBase: SafetyDict[str, dict] = {}  # Whoa en_US is my needed!

lang: str = "en_US"


def loadJson(jsonName: str) -> SafetyDict:
    if jsonName in alreadyLoaded.keys():
        if debugMode:
            addLog(3, f"{jsonName}.json Cache hit 💥", "FileConfigActivity")
        return alreadyLoaded[jsonName]

    if debugMode:
        addLog(
            3,
            f"Reading {jsonName}.json in en_US for support other text of not supported.",
        )
    baseData = load(f"./resources/language/en_US/{jsonName}.json")
    if debugMode:
        addLog(
            3,
            f"Attempting to load {jsonName}.json and cache it ✅",
            "FileConfigActivity",
        )
    langData = load(f"./resources/language/{lang}/{jsonName}.json")

    result = SafetyDict(baseData.copy() | langData.copy())

    alreadyLoaded[jsonName] = result  # Cache!
    return result


def setLang(lang_: str) -> None:
    global lang
    lang = lang_


"""
Olds:
def loadJson(jsonName: str) -> Any:
    if not Path(f"./resources/language/{lang}/{jsonName}.json").exists():
        addLog(
            2,
            f"Failed to load when load this Language File: {jsonName} ❌",
            "FileConfigActivity",
        )
        err("0x00000002")
        sys.exit(1)
    if jsonName in alreadyLoaded.keys():
        if debugMode:
            addLog(3, f"{jsonName}.json Cache hit 💥", "FileConfigActivity")
        return alreadyLoaded[jsonName]
    temp: dict = {}
    with open(
        f"./resources/language/en_US/{jsonName}.json", "r", encoding="utf-8"
    ) as f:
        if debugMode:
            addLog(
                3,
                f"Reading {jsonName}.json in en_US for support other text of not supported.",
            )
        temp = loads(f.read())  # Cache it
    with open(
        f"./resources/language/{lang}/{jsonName}.json", "r", encoding="utf-8"
    ) as f:
        if debugMode:
            addLog(
                3,
                f"Attempting to load {jsonName}.json and cache it ✅",
                "FileConfigActivity",
            )
        alreadyLoaded[jsonName] = temp | loads(f.read())
        return alreadyLoaded[jsonName]  # Use cache for file read nullptr
"""
