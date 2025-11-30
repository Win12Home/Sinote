"""
Sinote Widgets
Win12Home (C) 2025, MIT.
"""
from pathlib import PurePath

from BasicModule import * # Note: PySide6 was imported in BasicModule.py

def debugLog(content: str) -> None:
    if debugMode:
        addLog(3, content, "SinoteUserInterfaceActivity")

def debugPluginLog(content: str) -> None:
    if debugMode:
        addLog(3, content, "SinoteMainPluginLoadActivity")

syntaxHighlighter: dict[str, list[LoadPluginBase.CustomizeSyntaxHighlighter | list[str]]] = {}
loadedPlugin: list[dict[str, str | int | None]] = []
autoRun: list[partial] = []
"""
syntaxHighlighter Struct:
{
    "Code Name": [
        <One LoadPluginBase.CustomizeSyntaxHighlighter>,
        ["appendix1","appendix2","appendix3","appendix4","appendix5","appendix6"]
    ]
}
"""

def automaticLoadPlugin() -> None:
    if not Path("./resources/plugins/").exists():
        addLog(1, "Failed to load all the Plugins, Reason: ./resources/plugins/ not exists")
        return
    if not Path("./resources/plugins/").is_dir():
        addLog(1, "Failed to load all the Plugins, Reason: ./resources/plugins/ not a folder")
    dirs = list(Path("./resources/plugins/").iterdir())
    debugPluginLog(f"Total: {len(dirs)}, Starting load...")
    for item in dirs:
        debugPluginLog(f"Loading {item.name}")
        if not item.is_dir():
            addLog(0, f"Automatic skipped {item.name}, Reason: not a folder")
            continue

        infoJson: Path | PurePath = item / "info.json"

        if not (infoJson.exists()):
            addLog(1, f"Automatic skipped {item.name}, Reason: info.json not exists")
            continue
        temp = LoadPluginInfo(item.name).getValue()
        loadedPlugin.append(temp[0])
        debugPluginLog(f"Successfully loaded {item.name}, objectName: {temp[0]["objectName"]}. Preparing to parse...")
        for key in temp[1]:
            debugPluginLog(f"Loading {key[0]}...")
            if key[1] == 1:
                debugPluginLog(f"Checked its property! Type: SyntaxHighlighter")
                debugPluginLog(f"Creating QSyntaxHighlighter...")
                beforeTime = datetime.now()
                syntaxHighlighter[key[2]] = [key[4].getObject(), key[3]]
                debugPluginLog(f"Successfully created QSyntaxHighlighter! Used time: {(datetime.now() - beforeTime).total_seconds()}secs")
            elif key[1] == 0:
                debugPluginLog(f"Checked its property! Type: RunningFunc")
                debugPluginLog(f"Appending to autoRun...")
                [autoRun.append(i) if isinstance(i, partial) else None for i in key[2]]
                """
                This code definitely equals
                for i in key[2]:
                    if isinstance(i, partial):
                        autoRun.append(i)
                """
                debugPluginLog(f"Successfully to append!")
    debugPluginLog("Successfully to load plugins!")

automaticLoadPlugin()