from datetime import datetime
from functools import partial
from pathlib import Path, PurePath
from typing import Any, List

from PySide6.QtCore import Signal, QThread

from core.plugin import LoadPluginBase, LoadWholePlugin
from ui.selfLogger import debugPluginLog
from utils.argumentParser import args
from utils.config import settingObject
from utils.logger import Logger

syntaxHighlighter: dict[
    str, list[LoadPluginBase.LazyCustomizeSyntaxHighlighter | str | List[Any]]
] = {}
loadedPlugin: dict[str, dict[str, str | int | None]] = {}
autoRun: list[partial] = []
"""
syntaxHighlighter Struct:
{
    "Code Name": [
        <One LoadPluginBase.LazyCustomizeSyntaxHighlighter>,
        ["appendix1","appendix2","appendix3","appendix4","appendix5","appendix6"],
        ...
    ]
}
"""


class PluginsLoadThread(QThread):
    allLoaded = Signal()

    def __init__(self, filePaths: list[Path], name: str = None):
        super().__init__()
        self.filePaths = filePaths
        self.name = name if name else str(__import__("random").randint(10000, 99999))

    def run(self) -> None:
        debugPluginLog(f"Thread #{self.name} started!")
        for path in self.filePaths:
            item: Path = Path(path)
            debugPluginLog(f"Loading {item.name}")
            if not item.is_dir():
                Logger.info(f"Automatic skipped {item.name}, Reason: not a folder ❌")
                return

            infoJson: Path | PurePath = item / "info.json"
            if not (infoJson.exists()):
                Logger.warning(
                    f"Automatic skipped {item.name}, Reason: info.json not exists ❌"
                )
                return
            temp = LoadWholePlugin(item.name).getValue()
            debugPluginLog(f"Get value: {temp}")
            if temp == -1:
                Logger.error(
                    f"Failed to load plugin that its name is {item.name}. Error occurred."
                )
                return
            elif not isinstance(temp, list):
                Logger.error(f"Returned value is not a list! Plugin name: {item.name}")
                return
            loadedPlugin[temp[0]["objectName"]] = temp[0]
            if temp[0]["objectName"] in settingObject.getValue("disableplugin"):
                debugPluginLog(
                    f"Automatic skip plugin {temp[0]["objectName"]} (DISABLED)"
                )
                return
            debugPluginLog(
                f"Successfully loaded {item.name}, objectName: {temp[0]["objectName"]}. Preparing to parse... ✅"
            )
            for key in temp[1]:
                debugPluginLog(f"Loading {key[0]}...")
                if key[1] == 1:
                    debugPluginLog("Checked its property! Type: SyntaxHighlighter 🔎")
                    before: datetime = datetime.now()
                    syntaxHighlighter[key[2]] = [key[4], key[3], key[5], key[6]]
                elif key[1] == 0:
                    debugPluginLog("Checked its property! Type: RunningFunc 🤓")
                    debugPluginLog("Appending to autoRun... 💥")
                    if isinstance(key[2], list):
                        [
                            autoRun.append(i) if callable(i) else None
                            for i in key[2]
                        ]
                    """
                    This code definitely equals
                    for i in key[2]:
                        if isinstance(i, partial):
                            autoRun.append(i)
                    But it's will create a unused list ([None if isinstance(i, partial) else None for i in key[2]])
                    """
                    debugPluginLog("Successfully to append! ✅")
        debugPluginLog(f"Thread #{self.name} has been finished its work!")


class AutoLoadPlugin(QThread):
    loadedOne = Signal()
    loadNameChanged = Signal(str)
    loadTotal = Signal(int)
    processFinished = Signal()

    def run(self) -> None:
        MAX_WORK_THREAD = 4

        if "--dont-load-any-plugin" in args or "-displug" in args:
            Logger.debug(
                "--dont-load-any-plugin or -displug activated, no any plugins will be loaded! 🤔",
            )
            self.processFinished.emit()
            return
        if not Path("./resources/plugins/").exists():
            Logger.warning(
                "Failed to load all the Plugins, Reason: ./resources/plugins/ not exists ❌",
            )
            self.processFinished.emit()
            return
        if not Path("./resources/plugins/").is_dir():
            Logger.error(
                "Failed to load all the Plugins, Reason: ./resources/plugins/ not a folder ❌",
            )
            self.processFinished.emit()
            return
        dirs = list(Path("./resources/plugins/").iterdir())
        self.loadTotal.emit(len(dirs))
        debugPluginLog(f"Total: {len(dirs)}, Starting load... 💥")
        beforeLoadDatetime: datetime = datetime.now()
        plugins: list[QThread] = []

        if MAX_WORK_THREAD < len(dirs):
            # Super 贪心

            base, remainder = divmod(len(dirs), MAX_WORK_THREAD)
            wannaAllocate = []
            for i in range(MAX_WORK_THREAD):
                if i < remainder:
                    wannaAllocate.append(base + 1)
                else:
                    wannaAllocate.append(base)

            copiedList = dirs.copy()

            for name, i in enumerate(wannaAllocate):
                plugins.append(PluginsLoadThread(copiedList[:i], str(name + 1)))
                copiedList = copiedList[i:]

        else:
            plugins = [
                PluginsLoadThread([i], str(name + 1)) for name, i in enumerate(dirs)
            ]

        for item in plugins:
            item.start()

        for item in plugins:
            item.wait()

        usedTime: float = (datetime.now() - beforeLoadDatetime).total_seconds()
        debugPluginLog(f"Successfully to load plugins! ✅ Used {usedTime:.3f}s")
        if usedTime / len(dirs) > 1.0:
            assessment = "Use a new computer instead 🤔💀"
        elif usedTime / len(dirs) > 0.8:
            assessment = "Too slow 💀"
        elif usedTime / len(dirs) > 0.65:
            assessment = "A bit slow 😰"
        else:
            assessment = "Good load 😍"
        debugPluginLog(f"An assessment for Sinote: {assessment}")
        self.processFinished.emit()
