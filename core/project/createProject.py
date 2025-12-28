"""
Create Project Script
Win12Home (C) 2025, MIT.
Of course, this is the first file after decompose Widgets.py, BasicModule.py
我真求你了，像人机似的，我还是人吗？
"""

from datetime import datetime, timezone
from pathlib import Path
from platform import system, libc_ver, win32_ver, win32_edition, mac_ver, python_version
from typing import Callable
from utils.const import apiVersion, sinoteVersion
from utils.argumentParser import debugMode
from utils.getUtcString import getUtcString
from getpass import getuser
from json import dumps
from utils.logger import addLog
from utils.timer import beforeDatetime

debugLog: Callable = lambda content: addLog(3, content, "ProjectCreatorActivity") if debugMode else None
normalLog: Callable = lambda level, content: addLog(
    level if isinstance(level, int) else 4, content, "ProjectCreatorActivity"
)


def createProject(
    directory: str,
) -> bool:
    debugLog(f"Creating project... Where: {directory}")
    normalLog(0, "Creating project...")
    beforeDatetime_: datetime = datetime.now()
    if not Path(directory).exists():
        normalLog(
            1, f"Warning: {directory} is not exists! WTF about it, is it truly be output?"
        )  # Holy crap! 哪个傻子会出现！idk yet.
        Path(directory).mkdir(parents=True, exist_ok=True)
    if not Path(directory).is_dir():
        normalLog(2, f"Error: {directory} is not a directory!")
        return False
    if not (sinoteDir := Path(directory) / ".si").exists():
        try:
            debugLog("Try to create .si directory...")
            sinoteDir.mkdir()
        except PermissionError:
            normalLog(
                2,
                f'Error: {sinoteDir} cannot be created! Check "chmod"? Or other ways? So check it.',
            )
            return False
        except Exception as e:
            normalLog(
                2, f"Error: {sinoteDir} cannot be created! PyTraceback: {repr(e)}"
            )
            return False
        else:
            debugLog("Successfully to create .si directory 😘")
    sinoteProjectDir: Path = Path(directory) / ".si"
    if not sinoteProjectDir.is_dir():
        normalLog(2, f"Error: {sinoteProjectDir} is not a directory! Check needed?")
        return False
    struct: dict[str, dict | list] = {
        "settings.siproj": {
            "createdIn": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "normalTime": f"{datetime.now().strftime("%Y-%m-%dT%H:%M:%S")}{getUtcString()}",
            "recentlyWorks": {
                # Look bro
            },
            "defaultEncoding": "utf-8",
            "spacing": 4,  # So, this is indent.
        },
        "create-info.json": {
            "NOTE": "You can remove create-info.json. But it will be re-create with a incorrect info.",
            "API_VERSION": apiVersion,
            "SINOTE_VERSION": sinoteVersion,
            "AUTO_CREATE_IN": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "PC_TIMEZONE_CREATE_TIME": f"{datetime.now().strftime('%Y-%m-%dT%H:%M:%S')}{getUtcString()}",
            "PLATFORM": system().upper(),
            "INFORMATION": (
                [libc_ver()]
                if system().lower() == "linux"
                else (
                    [win32_ver(), win32_edition()]
                    if system().lower() == "windows"
                    else [mac_ver()] if system().lower() == "darwin" else [None]
                )
            ),
            "WHO_CREATED": getuser(),
            "PYTHON_VERSION": python_version()
        },
    }
    for where in [(sinoteProjectDir / i) for i in struct]:
        debugLog(f"Checking element {where}...")
        if not where.exists():
            try:
                debugLog(f"Creating {where.name}...")
                with open(f"{where}", "w", encoding="utf-8") as f:
                    f.write(dumps(struct[where.name], ensure_ascii=False, indent=2))
            except Exception as e:
                normalLog(2, f"Excepted error: {repr(e)} when creating {where.name}")
                return False
            else:
                debugLog(f"Create {where.name} successfully!")
    debugLog("Successfully to create .si directory!")
    debugLog(f"Successfully to create Project! Used time: {(datetime.now() - beforeDatetime_).total_seconds() * 1000:.2f}ms")
    normalLog(0, "Successfully to create Project!")
    return True