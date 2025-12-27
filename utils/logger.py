from datetime import datetime
from pathlib import Path
from rich import print


__all__ = [
    "setOwLog",
    "addLog",
    "debugMode",
    "colored",
    "normalLogOutput",
    "setNoColor",
    "saveLog",
]

normalLogOutput: list[str] = []
colored: bool = True
debugMode: bool = False


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
    logSender: str = (
        f"SinoteLog/[red]{activity}[/red]" if activity is not None else "SinoteLog"
    )
    normalLogOutput.append(
        f"[{nowTime}] [SinoteLog{f"/{activity}" if activity is not None else ""}] [{typeOfLog}] {bodyText}"
    )
    if colored:
        print(
            f"[[blue]{nowTime}[/blue]] [{logSender}] [[{colorOfType[typeOfLog]}]{typeOfLog}[/{colorOfType[typeOfLog]}]] {bodyText}"
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
