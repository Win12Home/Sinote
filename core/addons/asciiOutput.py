from platform import libc_ver, python_version, system, win32_ver

from rich import print
from utils.argumentParser import colored, debugMode, onlyWarning
from utils.const import apiVersion, sinoteVersion
from utils.logger import Logger, normalLogOutput
from utils.timer import getTotalSeconds


def asciiOutput() -> None:
    if onlyWarning:
        return
    Logger.info(f"Import Modules Finish! Used {getTotalSeconds()}secs")
    Logger.info(r"   _____ _             __          ______    ___ __            ")
    Logger.info(r"  / ___/(_)___  ____  / /____     / ____/___/ (_) /_____  _____")
    Logger.info(r"  \__ \/ / __ \/ __ \/ __/ _ \   / __/ / __  / / __/ __ \/ ___/")
    Logger.info(r" ___/ / / / / / /_/ / /_/  __/  / /___/ /_/ / / /_/ /_/ / /    ")
    Logger.info(r"/____/_/_/ /_/\____/\__/\___/  /_____/\__,_/_/\__/\____/_/     ")
    Logger.info(
        f"Sinote Editor {sinoteVersion}, API Version: {".".join([f"{i}" for i in apiVersion])}"
    )
    (
        print("[blue]============ SINOTE RUN LOG ============[/blue]")
        if colored
        else __import__("builtins").print("============ SINOTE RUN LOG ============")
    )
    normalLogOutput.append("============ SINOTE RUN LOG ============")
    if debugMode:
        Logger.debug(
            "For Developer Debug, Output your own PC's environment! 🤓",
            "OutputDeveloperDebugInformationActivity",
        )
        Logger.debug(
            f"Platform: {system()} Python: {python_version()} Win32 Version*: {" ".join(win32_ver())} | Linux LIBC Ver*: {" ".join(libc_ver())}",
            "OutputDeveloperDebugInformationActivity",
        )
        Logger.debug(
            "Note: If some error occurred, please send log to the developer 💥",
            "OutputDeveloperDebugInformationActivity",
        )
