from datetime import datetime
from utils.timer import beforeDatetime
from utils.logger import addLog, normalLogOutput
from utils.const import apiVersion, sinoteVersion
from utils.argumentParser import debugMode, colored, onlyWarning
from platform import system, libc_ver, win32_ver, python_version
from rich import print


def asciiOutput() -> None:
    if onlyWarning:
        return
    addLog(
        bodyText=f"Import Modules Finish! Used {(datetime.now() - beforeDatetime).total_seconds()}secs"
    )
    addLog(bodyText=r"   _____ _             __          ______    ___ __            ")
    addLog(bodyText=r"  / ___/(_)___  ____  / /____     / ____/___/ (_) /_____  _____")
    addLog(bodyText=r"  \__ \/ / __ \/ __ \/ __/ _ \   / __/ / __  / / __/ __ \/ ___/")
    addLog(bodyText=r" ___/ / / / / / /_/ / /_/  __/  / /___/ /_/ / / /_/ /_/ / /    ")
    addLog(bodyText=r"/____/_/_/ /_/\____/\__/\___/  /_____/\__,_/_/\__/\____/_/     ")
    addLog(
        bodyText=f"Sinote Editor {sinoteVersion}, API Version: {".".join([f"{i}" for i in apiVersion])}"
    )
    (
        print("[blue]============ SINOTE RUN LOG ============[/blue]")
        if colored
        else __import__("builtins").print("============ SINOTE RUN LOG ============")
    )
    normalLogOutput.append("============ SINOTE RUN LOG ============")
    if debugMode:
        addLog(
            3,
            "For Developer Debug, Output your own PC's environment! 🤓",
            "OutputDeveloperDebugInformationActivity",
        )
        addLog(
            3,
            f"Platform: {system()} Python: {python_version()} Win32 Version*: {" ".join(win32_ver())} | Linux LIBC Ver*: {" ".join(libc_ver())}",
            "OutputDeveloperDebugInformationActivity",
        )
        addLog(
            3,
            "Note: If some error occurred, please send log to the developer 💥",
            "OutputDeveloperDebugInformationActivity",
        )
