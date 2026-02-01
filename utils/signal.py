"""
Signal Analyzer
"""

import os
import signal
from datetime import datetime
from typing import Any

from PySide6.QtWidgets import QApplication
from utils.logger import Logger

__all__ = ["analyzeAllSignal"]

interruptTime: datetime = datetime(1, 1, 1, 0, 0, 0)


def executeInterruptSignal(*args: Any) -> None:  # NOQA, args was unused
    global interruptTime
    if (datetime.now() - interruptTime).total_seconds() >= 5:
        Logger.error(
            "Don't use Ctrl+C to quit forcibly, else you wanna be forgot your data",
            "SignalAnalyzer",
        )
        Logger.warning("If you want, please try Ctrl+C again", "SignalAnalyzer")
        interruptTime = datetime.now()
        return
    Logger.error(
        "Quiting Sinote forcibly with SIGINT exit code 130...", "SignalAnalyzer"
    )
    if QApplication.instance():
        QApplication.instance().quit()
    os._exit(130)


def analyzeInterruptSignal() -> None:
    signal.signal(signal.SIGINT, executeInterruptSignal)


def executeTerminateSignal(*args: Any) -> None:  # NOQA, args was unused
    Logger.error("Sinote has been terminated", "SignalAnalyzer")
    if QApplication.instance():
        QApplication.instance().deleteLater()
    os._exit(142)


def analyzeTerminateSignal() -> None:
    signal.signal(signal.SIGTERM, executeTerminateSignal)


def executePipeKillSignal(*args: Any, isSIGHUP: bool) -> None:  # NOQA, args was unused
    Logger.error("Sinote has been killed by PIPE", "SignalAnalyzer")
    if QApplication.instance():
        QApplication.instance().deleteLater()
    os._exit(129 if isSIGHUP else 141)


def analyzePipeKillSignal() -> None:
    try:
        signal.signal(signal.SIGHUP, lambda *args: executePipeKillSignal(args, True))
        signal.signal(signal.SIGPIPE, lambda *args: executePipeKillSignal(args, False))
    except: pass

def analyzeAllSignal() -> None:
    analyzeInterruptSignal()
    analyzeTerminateSignal()
    analyzePipeKillSignal()
