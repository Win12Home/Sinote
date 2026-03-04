"""
Signal Analyzer
"""

import os
import signal as sig
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
            "Don't use Ctrl+C to quit forcibly, else you wanna unuse your data",
            "SignalAnalyzer",
        )
        Logger.warning("If you want, please try Ctrl+C again", "SignalAnalyzer")
        interruptTime = datetime.now()
        return
    Logger.error(
        "Quiting Sinote forcibly with SIGINT exit code 130...", "SignalAnalyzer"
    )
    if QApplication.instance():
        QApplication.instance().deleteLater()
    os._exit(130)


def analyzeInterruptSignal() -> None:
    sig.signal(sig.SIGINT, executeInterruptSignal)


def executeTerminateSignal(*args: Any) -> None:  # NOQA, args was unused
    Logger.error("Sinote has been terminated", "SignalAnalyzer")
    if QApplication.instance():
        QApplication.instance().deleteLater()
    os._exit(142)


def analyzeTerminateSignal() -> None:
    sig.signal(sig.SIGTERM, executeTerminateSignal)


def executePipeKillSignal(isSIGHUP: bool) -> None:  # NOQA, args was unused
    Logger.error("Sinote has been killed by PIPE/HUP signal", "SignalAnalyzer")
    if QApplication.instance():
        QApplication.instance().deleteLater()
    os._exit(129 if isSIGHUP else 141)


def analyzePipeKillSignal() -> None:
    try:
        sig.signal(
            sig.SIGHUP, lambda *args: executePipeKillSignal(isSIGHUP=True)
        )  # NOQA
        sig.signal(
            sig.SIGPIPE, lambda *args: executePipeKillSignal(isSIGHUP=False)
        )  # NOQA
    except (AttributeError, TypeError):
        pass


def analyzeAllSignal() -> None:
    analyzeInterruptSignal()
    analyzeTerminateSignal()
    analyzePipeKillSignal()
