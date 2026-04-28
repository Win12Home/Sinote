from rich import print
from rich.syntax import Syntax
from utils.logger import Logger
from typing import Callable


def execFunction(script: str, namespace: dict) -> None:
    Logger.debugLog(f"Executing Python Scripts...")

    from utils.argumentParser import debugMode
    if debugMode:
        print(Syntax(script, "python", theme="monokai", line_numbers=True))

    exec(
        script, namespace, locals()
    )  # Yep, Users' safe is their own safe, look at this.


def functionCreator(script: str) -> Callable:
    return lambda mainWindow, script=script: execFunction(
        script, {"mainWindow": mainWindow, "selfScript": script}
    )
