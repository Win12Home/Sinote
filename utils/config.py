from json import dumps, loads
from locale import getdefaultlocale
from pathlib import Path
from typing import Any
from warnings import filterwarnings

from darkdetect import isLight
from utils.argumentParser import debugMode, setDebugMode
from utils.logger import Logger

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
    "theme": 0 if isLight() else 1,
    "disableplugin": [],
    "screen_size": [1280, 760],
    "recently_project_path": None,
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
                Logger.debug(
                    "Attempting to load setting.json5...", "SettingLexerActivity"
                )
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
                    Logger.debug(
                        "Successfully to load setting.json5!", "SettingLexerActivity"
                    )
        except Exception:
            Logger.error("Cannot load setting.json5!", "SettingLexerActivity")
            self.noFileAutoGenerate(mustToGenerate=True)

    def setValue(self, key: str, value: Any) -> None:
        global setting
        if key in normalSetting.keys():
            setting[key] = value
            if debugMode:
                Logger.debug(f"Successfully to change {key} to {value}")
            self.saveToConfig()

    def saveToConfig(self) -> None:
        with open("./setting.json5", "w", encoding="utf-8") as f:
            f.write(dumps(setting, ensure_ascii=False, sort_keys=True, indent=2))

    def getValue(self, key: str) -> Any | None:
        return setting.get(key, None)

    def noFileAutoGenerate(self, mustToGenerate: bool = False) -> None:
        global setting
        if debugMode:
            Logger.debug(
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
                Logger.debug("Successfully to generate a new setting!")
        setting = normalSetting


settingObject: Setting = Setting()

if settingObject.getValue("debugmode"):
    if debugMode:
        Logger.info("Don't open debug mode twice! (ADVICE)", "SettingLexerActivity")
    setDebugMode()
    Logger.debug("Debug mode opened from setting.json5!", "SettingLexerActivity")
