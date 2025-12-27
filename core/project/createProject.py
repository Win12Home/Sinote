"""
Create Project Script
Win12Home (C) 2025, MIT.
Of course, this is the first file after decompose Widgets.py, BasicModule.py
我真求你了，像人机似的，我还是人吗？
"""
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable
from utils.logger import addLog

debugLog: Callable = lambda content: addLog(3, content, "ProjectCreatorActivity")
normalLog: Callable = lambda level, content: addLog(level if isinstance(level, int) else 4, content, "ProjectCreatorActivity")
def createProject(directory: str) -> None | bool:  # If error, return None. If created, return True.
    debugLog(f"Creating project... Where: {directory}")
    normalLog(0, "Creating project...")
    if not Path(directory).exists():
        normalLog(2, f"Error: {directory} is not exists! WTF about it, is it truly be output?")  # Holy crap! 哪个傻子会出现！idk yet.
        return
    if not Path(directory).is_dir():
        normalLog(2, f"Error: {directory} is not a directory!")
        return
    if not (sinoteDir := Path(directory) / ".si").exists():
        try:
            debugLog("Try to create .si directory...")
            sinoteDir.mkdir()
        except PermissionError:
            normalLog(2, f"Error: {sinoteDir} cannot be created! Check \"chmod\"? Or other ways? So check it.")
            return
        except Exception as e:
            normalLog(2, f"Error: {sinoteDir} cannot be created! PyTraceback: {repr(e)}")
            return
        else:
            debugLog("Successfully to create .si directory 😘")
    sinoteProjectDir: Path = Path(directory) / ".si"
    if not sinoteProjectDir.is_dir():
        normalLog(2, f"Error: {sinoteProjectDir} is not a directory! Check needed?")
        return
    struct: dict[str, dict | list] = {
        "settings.siproj": {
            "createdIn": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "normalTime": f"{datetime.now().strftime("%Y-%m-%dT%H:%M:%S")}{getUtcString()}"
        }
    }
    for where in [(sinoteProjectDir / i) for i in struct]:
        debugLog(f"Checking element {where}...")
        if not where.exists():
            try:
                with open(f"{where}", "w", encoding="utf-8") as f:
