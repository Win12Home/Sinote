from utils.argumentParser import debugMode
from utils.logger import addLog, setDebugMode
from typing import Any
from json import loads
from pathlib import Path
from locale import getdefaultlocale
from json import dumps
from warnings import filterwarnings

__all__ = ["Setting", "settingObject"]

# Automatically ignore warning

filterwarnings("ignore", category=DeprecationWarning)

normalSetting: dict = {
    "fontName": "Fira Code",
    "fontSize": 12,
    "useFallback": False,
    "fallbackFont": None,
    "language": getdefaultlocale()[0],
    "debugmode": False,
    "secsave": 10,
    "theme": 1,
    "beforeread": {},
    "disableplugin": [],
}

setting: dict = {}


class Setting:
    def __init__(self):
        global setting
        # Automatic receive setting
        self.noFileAutoGenerate()
        # Automatic Lex setting file
        try:
            if debugMode:
                addLog(3, "Attempting to load setting.json5...", "SettingLexerActivity")
            with open("./setting.json5", "r", encoding="utf-8") as f:
                lexed: dict = normalSetting | loads(f.read())
            if not lexed.keys() is normalSetting.keys():
                with open("setting.json5", "w", encoding="utf-8") as f:
                    f.write(
                        dumps(
                            normalSetting | lexed,
                            ensure_ascii=True,
                            indent=2,
                            sort_keys=True,
                        )
                    )
            if not isinstance(lexed, dict):
                raise
            else:
                setting = lexed
                if debugMode:
                    addLog(
                        3, "Successfully to load setting.json5!", "SettingLexerActivity"
                    )
        except Exception:
            addLog(2, "Cannot load setting.json5!", "SettingLexerActivity")
            self.noFileAutoGenerate(mustToGenerate=True)

    def setValue(self, key: str, value: Any) -> None:
        global setting
        if key in normalSetting.keys():
            setting[key] = value
            if debugMode:
                addLog(3, f"Successfully to change {key} to {value}")
            self.saveToConfig()

    def saveToConfig(self) -> None:
        with open("./setting.json5", "w", encoding="utf-8") as f:
            f.write(dumps(setting, ensure_ascii=False, sort_keys=True, indent=2))

    def getValue(self, key: str) -> Any | None:
        return setting.get(key, None)

    def noFileAutoGenerate(self, mustToGenerate: bool = False) -> None:
        global setting
        if debugMode:
            addLog(
                3,
                (
                    "Checking setting.json5 exists, if not exists, automatic generate instead."
                    if not mustToGenerate
                    else "Argument mustToGenerate is true, generating a new setting..."
                ),
            )
        if not Path("./setting.json5").exists() or mustToGenerate:
            with open("./setting.json5", "w", encoding="utf-8") as f:
                f.write(
                    dumps(normalSetting, ensure_ascii=False, sort_keys=True, indent=2)
                )
            if debugMode:
                addLog(3, "Successfully to generate a new setting!")
        setting = normalSetting


settingObject: Setting = Setting()

if settingObject.getValue("debugmode"):
    if debugMode:
        addLog(0, "Don't open debug mode twice! (ADVICE)", "SettingLexerActivity")
    setDebugMode()
    addLog(3, "Debug mode opened from setting.json5!", "SettingLexerActivity")
