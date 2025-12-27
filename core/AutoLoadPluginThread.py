from PySide6.QtCore import QThread, Signal
from utils.argumentParser import args
from core.plugin import LoadPluginBase
from ui.selfLogger import debugPluginLog
from utils.logger import addLog
from utils.config import settingObject
from core.plugin import LoadPluginInfo
from functools import partial
from typing import List, Any
from pathlib import Path, PurePath
from datetime import datetime

syntaxHighlighter: dict[
    str, list[LoadPluginBase.CustomizeSyntaxHighlighter | str | List[Any]]
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


class AutoLoadPlugin(QThread):
    loadedOne = Signal()
    loadNameChanged = Signal(str)
    loadTotal = Signal(int)
    processFinished = Signal()

    def run(self) -> None:
        if "--dont-load-any-plugin" in args or "-displug" in args:
            addLog(
                0,
                "--dont-load-any-plugin or -displug activated, no any plugins will be loaded!",
            )
            self.processFinished.emit()
            return
        if not Path("./resources/plugins/").exists():
            addLog(
                1,
                "Failed to load all the Plugins, Reason: ./resources/plugins/ not exists ❌",
            )
            self.processFinished.emit()
            return
        if not Path("./resources/plugins/").is_dir():
            addLog(
                1,
                "Failed to load all the Plugins, Reason: ./resources/plugins/ not a folder ❌",
            )
            self.processFinished.emit()
            return
        dirs = list(Path("./resources/plugins/").iterdir())
        self.loadTotal.emit(len(dirs))
        debugPluginLog(f"Total: {len(dirs)}, Starting load... 💥")
        beforeLoadDatetime: datetime = datetime.now()
        for item in dirs:
            debugPluginLog(f"Loading {item.name}")
            if not item.is_dir():
                addLog(0, f"Automatic skipped {item.name}, Reason: not a folder ❌")
                continue

            infoJson: Path | PurePath = item / "info.json"
            if not (infoJson.exists()):
                addLog(
                    1, f"Automatic skipped {item.name}, Reason: info.json not exists ❌"
                )
                continue
            self.loadNameChanged.emit(item.name)
            temp = LoadPluginInfo(item.name).getValue()
            loadedPlugin[temp[0]["objectName"]] = temp[0]
            self.loadNameChanged.emit(temp[0]["name"])
            if temp[0]["objectName"] in settingObject.getValue("disableplugin"):
                debugPluginLog(
                    f"Automatic skip plugin {temp[0]["objectName"]} (DISABLED)"
                )
                self.loadedOne.emit()
                continue
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
                            autoRun.append(i) if isinstance(i, partial) else None
                            for i in key[2]
                        ]
                    """
                    This code definitely equals
                    for i in key[2]:
                        if isinstance(i, partial):
                            autoRun.append(i)
                    But it's will create a unused list ([None if isinstance(i, partial) for i in key[2]])
                    """
                    debugPluginLog("Successfully to append! ✅")
            self.loadedOne.emit()
        usedTime: float = (datetime.now() - beforeLoadDatetime).total_seconds()
        debugPluginLog(f"Successfully to load plugins! ✅ Used {usedTime:.3f}s")
        assessment = ""
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
