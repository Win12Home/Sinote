from time import sleep

from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import QWidget
from utils.iterDir import iterDir


class AutomaticIterDirectoryThread(QThread):
    iterChanged: Signal = Signal(list)

    def __init__(self, parent: QWidget = None, directory: str = None):
        super().__init__(parent)
        self._directory = directory
        self._oldIter: list = []
        self._running: bool = True

    def run(self) -> None:
        while True:
            if self._directory is None:
                continue
            newIter: list = iterDir(self._directory)
            if newIter != self._oldIter:
                self._oldIter = newIter
                self.iterChanged.emit(newIter)
            for i in range(1000):  # Check every 1s
                sleep(0.001)
                if not self._running:
                    return

    def emitIterDir(self) -> None:
        self._oldIter = iterDir(self._directory)
        self.iterChanged.emit(self._oldIter)

    def setDirectory(self, directory: str | None) -> None:
        self._oldIter = []
        self._directory = directory

    def quit(self, /) -> None:
        self._running = False
