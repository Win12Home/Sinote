from datetime import datetime, timezone
from getpass import getuser
from platform import (
    architecture,
    libc_ver,
    mac_ver,
    python_compiler,
    python_version,
    system,
    uname,
    win32_edition,
    win32_ver,
)

from utils.const import *
from utils.getUtcString import getUtcString


def struct(nameOfProject: str = "NULL") -> dict:  # NOQA, I against PEP8
    return {
        "settings.siproj": {  # NOQA, siproj means Sinote Project
            "createdIn": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "normalTime": f"{datetime.now().strftime("%Y-%m-%dT%H:%M:%S")}{getUtcString()}",
            "name": nameOfProject,
            "recentlyWorks": {
                # Look bro, clean~ So clean~ WTF
            },
            "nowWorks": None,
            # "defaultEncoding": "utf-8",
            # "spacing": 4,  # So, this is indent.
        },
        "create-info.json": {
            "NOTE_UNUSED": "You can remove create-info.json. But it will be re-create with an incorrect info.",
            "API_VERSION": apiVersion,
            "SINOTE_VERSION": sinoteVersion,
            "AUTO_CREATE_IN": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "PC_TIMEZONE_CREATE_TIME": f"{datetime.now().strftime('%Y-%m-%dT%H:%M:%S')}{getUtcString()}",
            "PLATFORM": system().upper(),
            "INFORMATION": (
                [libc_ver(), uname()]
                if system().lower() == "linux"
                else (
                    [win32_ver(), win32_edition()]
                    if system().lower() == "windows"
                    else [mac_ver()] if system().lower() == "darwin" else [None]
                )
            ),
            "WHO_CREATED": getuser(),
            "PYTHON_VERSION": python_version(),
            "ARCHITECTURE": architecture(),
            "PY_COMPILER": python_compiler(),
        },
    }
