from datetime import datetime
from pathlib import Path
from rich import print
from random import choice


__all__ = [
    "setOwLog",
    "addLog",
    "debugMode",
    "colored",
    "normalLogOutput",
    "setNoColor",
    "saveLog",
    "setFunny",
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
]


def addLogClassic(
    type: int = 0,
    bodyText: str = "N/A",
    activity: str | None = None,
    placeholder: bool = False,
):
    typeOfLog: str = (
        "INFO"
        if (type == 0)
        else (
            "WARN"
            if (type == 1)
            else "ERR" if (type == 2) else "DBG" if (type == 3) else "N/A"
        )
    )
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
        f"[{nowTime}] [SinoteLog{f"/{activity}" if activity is not None else ""}] [{theType}] {bodyText}"
    )
    if colored:
        print(
            f"[[blue]{nowTime}[/blue]] [{logSender}] [[{colorOfType[typeOfLog]}]{theType}[/{colorOfType[typeOfLog]}]] {bodyText}"
        )
    else:
        __import__("builtins").print(
            f"{nowTime} {"Main" if not activity else activity} {typeOfLog} {bodyText}"
        )


def owLog(
    type: int = 0,
    bodyText: str = "N/A",
    activity: str | None = None,
    mustToPrint: bool = False,
):
    if type in [1, 2] or mustToPrint:  # Only output WARN&ERR, What the hell of that?
        addLogClassic(type, bodyText, activity)


addLog = addLogClassic


def setOwLog() -> None:
    global addLog
    addLog = owLog


def setNoColor() -> None:
    global colored
    colored = False


def setDebugMode() -> None:
    global debugMode
    debugMode = True


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
