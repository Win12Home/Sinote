from datetime import datetime

from PySide6.QtCore import QObject, Qt, Signal
from PySide6.QtGui import QKeyEvent
from utils.argumentParser import debugMode
from utils.errors import SinoteErrors
from utils.logger import Logger


class Shortcut(QObject):
    """
    How to use it?
    put this->keyPressEvent to your own keyPressEvent function. （不是从Stack overflow里抄来的）
    put this->keyReleaseEvent to your own keyReleaseEvent function.
    """

    shortcutHandled: Signal = Signal(int)

    def __init__(self):
        super().__init__()
        self._shortcutList: dict[int, set[int]] = {}
        self._pressedKeys: set[tuple[int, datetime]] = set()

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if debugMode:
            Logger.debug(f"Key pressed: {event.key()}", "ShortcutActivity")
        if event.isAutoRepeat():
            return
        if event.key() not in self._pressedKeys:
            self._pressedKeys.add((event.key(), datetime.now()))

        for key, time in self._pressedKeys.copy():  # O(n) alright
            if (datetime.now() - time).total_seconds() >= 10:
                if debugMode:
                    Logger.debug(
                        f"Key {key} is out-time! Automatically remove it! (10secs)",
                        "ShortcutActivity",
                    )
                self._pressedKeys.discard((key, time))

        if (
            self._pressedKeys
            in self._shortcutList.values()
            # It will be slow when shortcut pressed, but it will be dash! when shortcut not pressed. O(n)
        ):
            for itemNumber, key in self._shortcutList.items():
                if key == [i[0] for i in self._pressedKeys]:
                    if debugMode:
                        Logger.debug(
                            f"Shortcut triggered! Triggered item: {itemNumber}\n    Automatically clear pressed key",
                            "ShortcutActivity",
                        )
                    self.shortcutHandled.emit(itemNumber)
                    self._pressedKeys.clear()
                    break

    def keyReleaseEvent(self, event: QKeyEvent) -> None:
        if debugMode:
            Logger.debug(f"Key released: {event.key()}", "ShortcutActivity")
        if not event.isAutoRepeat() and event.key() in self._pressedKeys:
            self._pressedKeys.discard(event.key())

    def addItem(self, keys: list[Qt.Key], itemNumber: int) -> None:
        if itemNumber not in self._shortcutList:
            self._shortcutList[itemNumber] = set(
                [i.value for i in keys if hasattr(i, "value")]
            )
            return
        raise SinoteErrors.ItemNotValid(
            f"{itemNumber} has probably in the shortcut list."
        )

    def discardItem(self, itemNumber: int) -> None:
        self._shortcutList.pop(itemNumber)
