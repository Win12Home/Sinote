from datetime import datetime
from pathlib import Path
from random import choice

from rich import print

__all__ = [
    "setOwLog",
    "addLog",
    "debugMode",
    "colored",
    "normalLogOutput",
    "setNoColor",
    "saveLog",
    "setFunny",
    "Logger",
]

normalLogOutput: list[str] = []
funnyLogOutput: list[str] = []
colored: bool = True
debugMode: bool = False
funnyMode: bool = False
funnyTypes: list[str] = [
    "BELIEVE",
    "TRUST",
    "HOLY_CRAP",
    "OMG",
    "DONT_DISTURB_ME",
    "REAL_SIGNATURE_UNKNOWN",
    "CYTHON_MY_LIFE",
    "WOW_PYPY_IS_NOT_SUPPORTED",
    "PYSIDE6_MY_LIFE",
    "FREE_TIME_I_LIKE",
    "PEP8_IS_A_FAILURE",
    "ANACONDA_IS_BIG_AND_FUCKING_UNUSABLE",
    "ARRAY_IS_NOT_GOOD",
    "I_USE_ARCH_BTW",
    "MY_CODE_IS_A_FAILURE",
    "SSH_KEYGEN_WOW_GOOD",
    "NO_ITS_A_WILD_PTR",
    "SO_NVIDIA_FUCK_YOU",
    "I_AM_A_LINUX_BOT",
    "MOV_OMG_114514",
    "NOBODY_KNOWS_I_AM_A_ARCH_MAN",
    "USE_MINICONDA_INSTEAD_OF_ANACONDA_BRO",
    "MSG_DB_'I_WANT_TO_EAT_KFC'",
    "MY_HEAP_IS_BIG",
    "CPP23_COPIED_PRINTLN_IN_JAVA",
    "PACMAN_SYU",
    "OW_MY_LEG_BROKE",
    "HUH_SPRINGBOOT_DEP_CRASHED",
    "STACK_OVERFLOWING_PLZ_WAIT",
    "NO_I_AM_AFRAID_BECAUSE_RTX_IS_THE_GPU_OF_MY_NEW_COMPUTER",
    "I_USE_NOUVEAU_BTW",
    "UWU_OWO_TWT_LWL_PWP_VWV_I_AM_CUTE",
    "INFO_WARN_ERR_DBG",
    "I_AM_CRYING_BECAUSE_NVIDIA_IS_EXPENSIVE",
]


def addLogNormalize(  # Changed 'Classic' to 'Normalize', my English is not good bro.
    type: int = 0,
    bodyText: str = "N/A",
    activity: str | None = None,
    placeholder: bool = False,
):
    # typeOfLog: str = ("INFO" if (type == 0) else ("WARN" if (type == 1) else "ERR" if (type == 2) else "DBG" if (type == 3) else "N/A"))
    types: dict[int, str] = {0: "INFO", 1: "WARN", 2: "ERR", 3: "DBG"}
    # Readability counts, use dict to get
    typeOfLog: str = types.get(type, "N/A")
    colorOfType: dict = {
        "INFO": "cyan",
        "WARN": "yellow",
        "ERR": "red",
        "DBG": "green",
        "N/A": "gray",
    }
    nowTime: str = datetime.now().strftime("%H:%M.%S.%f")[:-3]
    theType: str = typeOfLog if not funnyMode else choice(funnyTypes)
    logSender: str = (
        f"SinoteLog/[red]{activity}[/red]" if activity is not None else "SinoteLog"
    )
    normalLogOutput.append(
        # For log saver to save
        f"[{nowTime}] [SinoteLog{f"/{activity}" if activity is not None else ""}] [{theType}] {bodyText}"
    )
    if colored:
        print(
            # Output with color
            f"[[blue]{nowTime}[/blue]] [{logSender}] [[{colorOfType.get(typeOfLog, "grey")}]{theType}[/{colorOfType.get(typeOfLog, "grey")}]] {bodyText}"
        )
    else:
        __import__("builtins").print(
            # Import builtins library to print out NOCOLOR log
            f"{nowTime} {"Main" if not activity else activity} {typeOfLog} {bodyText}"
        )


def owLog(
    type: int = 0,
    bodyText: str = "N/A",
    activity: str | None = None,
    mustToPrint: bool = False,
):
    if type in [1, 2] or mustToPrint:  # Only output WARN&ERR, What the hell of that?
        addLogNormalize(type, bodyText, activity)


addLog = addLogNormalize  # Default: addLogNormalize


def setOwLog() -> None:
    global addLog
    addLog = owLog  # Set value of addLog to owLog, for Only Warning Log Print


def setNoColor() -> None:
    global colored
    colored = False


def setFunny() -> None:
    global funnyMode
    funnyMode = True


def saveLog():
    if not Path("./log").exists():
        Path("./log").mkdir(exist_ok=True)
    if not Path("./log").is_dir():
        raise IOError("Cannot use ./log to write log! Sinote cannot continue running!")
    with open(
        datetime.now().strftime("./log/sinote-log-time-%Y-%m-%d-%H.%M.%S-output.log"),
        "w+",
        encoding="utf-8",
    ) as f:
        f.write("\n".join(normalLogOutput))


class Logger:  # Readability, of course
    @staticmethod
    def info(
        content: str, activity: str | None = None, mustToPrint: bool = False
    ) -> None:
        addLog(0, content, activity, mustToPrint)

    @staticmethod
    def warning(
        content: str, activity: str | None = None, mustToPrint: bool = False
    ) -> None:
        addLog(1, content, activity, mustToPrint)

    @staticmethod
    def error(
        content: str, activity: str | None = None, mustToPrint: bool = False
    ) -> None:
        addLog(2, content, activity, mustToPrint)

    @staticmethod
    def debug(
        content: str, activity: str | None = None, mustToPrint: bool = False
    ) -> None:
        addLog(3, content, activity, mustToPrint)

    # @staticmethod
    # def others(content: str, activity: str | None = None, mustToPrint: bool = False) -> None:
    #    addLog(NUM, content, activity, mustToPrint)
    #
    # For log out other type
