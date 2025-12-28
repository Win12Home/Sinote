from platform import mac_ver, system, python_version, win32_ver, win32_edition, libc_ver
from utils.getUtcString import getUtcString
from datetime import datetime, timezone
from utils.const import *
from getpass import getuser

def struct(nameOfProject: str="NULL") -> dict:
    return {
            "settings.siproj": {
                "createdIn": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "normalTime": f"{datetime.now().strftime("%Y-%m-%dT%H:%M:%S")}{getUtcString()}",
                "name": nameOfProject,
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