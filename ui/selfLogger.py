from utils.argumentParser import debugMode
from utils.logger import addLog
from threading import Thread
from functools import partial


def debugLog(content: str) -> None:
    if debugMode:
        thread: Thread = Thread(daemon=True)
        thread.run = partial(addLog, 3, content, "SinoteUserInterfaceActivity")
        thread.start()


def debugPluginLog(content: str) -> None:
    if debugMode:
        thread: Thread = Thread()
        thread.run = partial(addLog, 3, content, "SinoteMainPluginLoadActivity")
        thread.start()
