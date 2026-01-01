"""
Get Project Settings
"""

from json import loads, JSONDecodeError, dumps
from json5 import loads as json5Loads
from core.project.createProject import createProject
from pathlib import Path
from typing import Callable, Any
from utils.logger import addLog
from utils.argumentParser import debugMode

debugLog: Callable = lambda content: (
    addLog(3, content, "ProjectSettingGet&WriterActivity") if debugMode else None
)
normalLog: Callable = lambda level, content: addLog(
    level if isinstance(level, int) else 4, content, "ProjectSettingGet&WriterActivity"
)


class ProjectSettings:
    def __init__(self, directory: str):
        debugLog(f"Initializing project settings object...")
        self._dir: str = directory
        self._settings: dict[Any, Any]
        self.getProjectSettings()
        debugLog(
            f"Initialized Project Settings object with argument directory={directory}"
        )

    def __setitem__(self, key: str, value: Any) -> Any:
        self._settings[key] = value
        self.__sync()

    def __sync(self) -> None:
        debugLog("Synchronizing Project Setting...")
        try:
            with open(
                f"{Path(self._dir) / ".si" / "settings.siproj"}", "w", encoding="utf-8"
            ) as f:
                f.write(dumps(self._settings, ensure_ascii=False, indent=2))
        except Exception as e:
            normalLog(
                2,
                f"Error: Synchronize Project Setting failed: {repr(e)} (for a known python traceback)",
            )
        else:
            debugLog("Synchronize successfully!")

    def __getitem__(self, item: str) -> Any:
        return self._settings.get(item, None)

    def getProjectSettings(self) -> dict[Any, Any] | None:
        directory: str = self._dir
        normalLog(0, "Getting Project Settings...")
        debugLog(f"Attempting to get settings in directory {directory}...")
        if not Path(directory).exists():
            debugLog(f"{directory} is not exists, automatically create!")
            Path(directory).mkdir(parents=True, exist_ok=True)
        if not Path(directory).is_dir():
            normalLog(2, f"{directory} is not a directory!")
            return
        debugLog(f'Tried to use "createProject" function to check project...')
        if not createProject(directory, Path(directory).name):
            debugLog(f"{directory} is not a valid project! Return false instead.")
            normalLog(2, f"{directory} is not a valid project!")
            return
        debugLog("Attempting to read settings...")
        gotJson: str = ""
        try:
            with open(
                str(Path(directory) / ".si" / "settings.siproj"), "r", encoding="utf-8"
            ) as f:
                gotJson = f.read()
        except Exception as e:
            normalLog(2, f"Cannot read settings: {repr(e)}")
            return
        else:
            debugLog("Successfully to read settings!")
        gotDict: dict[Any, Any] = {}
        try:
            gotDict = loads(gotJson)
        except JSONDecodeError:
            gotDict = json5Loads(gotJson)
        except Exception as e:
            normalLog(2, f"Failed to convert string to dict: {repr(e)}")
        self._settings = gotDict
        return gotDict
