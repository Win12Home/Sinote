"""
Get Project Settings
"""
from json import loads, JSONDecodeError
from json5 import loads as json5Loads
from core.project.createProject import createProject
from pathlib import Path
from typing import Callable, Any
from utils.logger import addLog
from utils.argumentParser import debugMode

debugLog: Callable = lambda content: addLog(3, content, "ProjectSettingGetterActivity") if debugMode else None
normalLog: Callable = lambda level, content: addLog(level if isinstance(level, int) else 4, content, "ProjectSettingGetterActivity")
def getProjectSettings(directory: str) -> dict[Any, Any] | None:
    normalLog(0, "Getting Project Settings...")
    debugLog(f"Attempting to get settings in directory {directory}...")
    if not Path(directory).exists():
        debugLog(f"{directory} is not exists, automatically create!")
        Path(directory).mkdir(parents=True, exist_ok=True)
    if not Path(directory).is_dir():
        normalLog(2, f"{directory} is not a directory!")
        return
    debugLog(f"Tried to use \"createProject\" function to check project...")
    if not createProject(directory, Path(directory).name):
        debugLog(f"{directory} is not a valid project! Return false instead.")
        normalLog(2, f"{directory} is not a valid project!")
        return
    debugLog("Attempting to read settings...")
    gotJson: str = ""
    try:
        with open(str(Path(directory) / ".si" / "settings.siproj"), "r", encoding="utf-8") as f:
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
    return gotDict