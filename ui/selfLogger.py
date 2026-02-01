from functools import partial
from threading import Thread

from utils.argumentParser import debugMode
from utils.logger import Logger


def debugLog(content: str) -> None:
    if debugMode:
        thread: Thread = Thread(daemon=True)
        thread.run = partial(Logger.debug, content, "SinoteUserInterfaceActivity")
        thread.start()


def debugPluginLog(content: str) -> None:
    if debugMode:
        thread: Thread = Thread()
        thread.run = partial(Logger.debug, content, "SinoteMainPluginLoadActivity")
        thread.start()
