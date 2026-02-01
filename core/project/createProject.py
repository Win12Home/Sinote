"""
Create Project Script
Win12Home (C) 2025, MIT.
Of course, this is the first file after decompose Widgets.py, BasicModule.py
我真求你了，像人机似的，我还是人吗？
"""

from datetime import datetime
from json import dumps
from pathlib import Path
from typing import Callable

from core.project.projectStruct import struct
from utils.argumentParser import debugMode
from utils.logger import Logger, addLog  # Add log is needed!

debugLog: Callable = lambda content: (
    Logger.debug(content, "ProjectCreatorActivity") if debugMode else None
)
normalLog: Callable = lambda level, content: addLog(
    level if isinstance(level, int) else 4, content, "ProjectCreatorActivity"
)


def createProject(
    directory: str,
    nameOfProject: str,
) -> bool:
    debugLog(f"Creating project... Where: {directory}")
    normalLog(0, "Creating project...")
    beforeDatetime_: datetime = datetime.now()
    if not Path(directory).exists():
        normalLog(
            1,
            f"{directory} is not exists! WTF about it, is it truly be output?",
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
                f'{sinoteDir} cannot be created! Check "chmod"? Or other ways? So check it.',
            )
            return False
        except Exception as e:
            normalLog(2, f"{sinoteDir} cannot be created! PyTraceback: {e!r}")
            return False
        else:
            debugLog("Successfully to create .si directory 😘")
    sinoteProjectDir: Path = Path(directory) / ".si"
    if not sinoteProjectDir.is_dir():
        normalLog(2, f"Error: {sinoteProjectDir} is not a directory! Check needed?")
        return False

    for where in [(sinoteProjectDir / i) for i in struct(nameOfProject)]:
        debugLog(f"Checking element {where}...")
        if not where.exists():
            try:
                debugLog(f"Creating {where.name}...")
                with open(f"{where}", "w", encoding="utf-8") as f:
                    f.write(
                        dumps(
                            struct(nameOfProject)[where.name],
                            ensure_ascii=False,
                            indent=2,
                        )
                    )
            except Exception as e:
                normalLog(2, f"Excepted error: {e!r} when creating {where.name}")
                return False
            else:
                debugLog(f"Create {where.name} successfully!")
    debugLog("Successfully to create .si directory!")
    debugLog(
        f"Successfully to create Project! Used time: {(datetime.now() - beforeDatetime_).total_seconds() * 1000:.2f}ms"
    )
    normalLog(0, "Successfully to create Project!")
    return True
