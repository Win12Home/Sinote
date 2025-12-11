"""
Sinote Plugin CLI (spcli)
Win12Home (C) GPL v2.0.
"""
from rich import print
from typing import *
import sys

"""
Initialize
"""

docs: dict[Any, Any] = {
    "help": "Help of Sinote CLI.",
    "create": "Create a plugin template. Required Argument: [1] Object name of this template.",
    "check": "Check this plugin. Required Argument: [1] Directory path of your plugin."
}

commandDocs: dict[Any, Any] = {
    "help": ["Help of Sinote CLI.", [], ["Command name"], True],
    "create": [
        "Create a plugin template.",
        [
            "Directory of this template."
        ],
        [
            "[red]-n/--name[/red]: Plugin name",
            "[red]-v/--version[/red]: Plugin version",
            "[red]-i/--iterate[/red]: Plugin version Iterate (Version Iterate means the Xth Version)",
            "[red]-ic/--icon[/red]: Path of Plugin icon (#space; for one space, like imports.txt)",
            "[red]-on/--object-name[/red]: Customize Object name. (Not exists automatically use directory name for object name)",
            "[purple]--ignore-dir-exists[/purple]: Ignore directory exists. (BOOL Type)"
        ],
        False
    ],
    "check": [
        "Check this plugin.",
        [
            "Directory path of your plugin."
        ],
        [],
        False
    ]
}

primaryArgList: list[str] = [
    "create",
    "check",
    "help"
]

def fatalError(content: AnyStr) -> None:
    print(f"[red]fatal:[/red] {content}")

def lexArgument(content: str) -> list[str]:
    splitted: list[str] = content.split(":")
    return splitted if len(splitted) in [1, 2] else [splitted[0], ":".join(splitted[1:])]

class CLIUsages:
    @staticmethod
    def help(wrongArg: AnyStr=None) -> None:
        if wrongArg == "None":
            fatalError("No any argument input.")
            print()
        elif wrongArg:
            fatalError(f"\"{wrongArg}\" is not a valid argument.")
            print()
        print("Help of [blue]Sinote CLI[/blue]")
        print()
        for k, w in docs.items():
            print(f"  [red]{k}[/red]: {w}")
        print()
        print("[red]Note: [/red] With another argument: --argument:another_argument (Use #space; to split)")

    @staticmethod
    def helpOfOneCommand(command: AnyStr=None) -> None:
        if command not in primaryArgList:
            fatalError(f"{command} is not a valid command.")
            return
        docs: list[str] = commandDocs[command]
        print(f"Help of [red]{command}[/red]")
        print(f"  Description: {docs[0]}")
        print(f"  Required arguments: {", ".join([f"[{iter}] {means}" for iter, means in enumerate(docs[1], 1)]) if docs[1] else "No arguments needed"}")
        if docs[2]:
            print(f"  Not required arguments:")
            for iter, temp in enumerate(docs[2], 1):
                print(f"    {temp if not docs[3] else f"[{iter}] {temp}"}")

    @staticmethod
    def createTemplate(objectName: str, notRequiredArgs: dict[str, str]) -> None:
        from tqdm import tqdm
        from pathlib import Path
        tasks: tqdm = tqdm(total=3, desc="Processing")
        objName: str = Path(objectName).name
        getNotNone: Any = lambda x, y: x if x is not None else y
        # Create directory
        if Path(objectName).exists() and not "--ignore-dir-exists" in notRequiredArgs.keys():
            tasks.close()
            fatalError(f"Folder \"{objectName}\" exists, cannot continue create!")
            return
        Path(objectName).mkdir(exist_ok=True)
        tasks.set_description_str("Making info.json")
        tasks.update(1)
        info: dict[Any, Any] = {
            "icon": None,
            "name": "Unnamed Plugin",
            "objectName": objName,
            "version": "Version Text",
            "versionIterate": 99900,
            "customizeRemoveString": {
                "zh_CN": "自定义删除插件文本",
                "en_US": "Customize Remove String"
            },
            "author": [
                "No authors"
            ],
            "description": "Description"
        }
        from json import dumps
        # Read arguments
        name: str | None = getNotNone(notRequiredArgs.get("-n", None), notRequiredArgs.get("--name", None))
        if name:
            info["name"] = name.replace("#space;", " ")
        ver: str | None = getNotNone(notRequiredArgs.get("-v", None), notRequiredArgs.get("--version", None))
        if ver:
            info["version"] = ver.replace("#space;", " ")
        iterate: str | None = getNotNone(notRequiredArgs.get("-i", None), notRequiredArgs.get("--iterate", None))
        try:
            if iterate:
                info["versionIterate"] = int(iterate)
        except Exception as e:
            tasks.close()
            fatalError(f"Error when making info.json: {repr(e)}")
            sys.exit(1)
        icon: str | None = getNotNone(notRequiredArgs.get("-ic", None), notRequiredArgs.get("--icon", None))
        if icon:
            info["icon"] = icon.replace("#space;", " ")
        objectName_: str | None = getNotNone(notRequiredArgs.get("-on", None), notRequiredArgs.get("--object-name", None))
        if objectName_:
            info["objectName"] = objectName_.replace("#space;", " ")
        infoJson: str = dumps(info, ensure_ascii=False)
        tasks.set_description_str("Making base environment")
        tasks.update(1)
        (Path(objectName) / "headers").mkdir(exist_ok=True)
        with open(str(Path(objectName) / "imports.txt"), "w", encoding="utf-8") as f:
            f.write("// imports.txt has been automatically create by Sinote CLI.")
        tasks.set_description_str("Saving changes")
        tasks.update(1)
        with open(str(Path(objectName) / "info.json"), "w", encoding="utf-8") as f:
            f.write(infoJson)
        tasks.set_description_str("Finished processing")
        tasks.close()
        print("Successfully to make a template.")


class CLIError:
    @staticmethod
    def argumentNumberNotValid(command: AnyStr, min: int, max: int, got: int = None):
        if got is None:
            fatalError(f"{command} need {min} arguments, got {max} arguments.")
            return
        fatalError(f"{command} need {min} to {max} arguments, got {got} arguments.")

version: str = "0.1.0-compatible-with-api-1.0.1"

print(f"[blue]Sinote CLI[/blue] Version {version}")
print(f"Win12Home (C) 2025, MIT. (in project Win12Home/Sinote)")
print()

primaryArgs: list[str] = [i for i in sys.argv[1:] if not i.startswith("-")]
notRequiredArgs: list[str] = [i for i in sys.argv[1:] if i.startswith("-")]

if len(primaryArgs) == 0:
    CLIUsages.help("None")
    sys.exit(1)

command: str = primaryArgs[0].lower()

if command not in primaryArgList:
    CLIUsages.help(wrongArg=command)
    sys.exit(1)
if command == "help" and len(primaryArgs) == 1:
    CLIUsages.help()
    sys.exit(0)
if command == "help" and len(primaryArgs) == 2:
    CLIUsages.helpOfOneCommand(primaryArgs[1])
    sys.exit(0)
if command == "help" and len(primaryArgs) > 2:
    CLIError.argumentNumberNotValid(command, 0, 1, len(primaryArgs) - 1)
    sys.exit(1)
if command == "create" and len(primaryArgs) == 2:
    lexedArguments: dict[str, str] = {}
    for temp in notRequiredArgs:
        temp2: list[str] = lexArgument(temp)
        lexedArguments[temp2[0]] = None if len(temp2) == 1 else temp2[1]
    CLIUsages.createTemplate(primaryArgs[1], lexedArguments)
    sys.exit(0)
if command == "create":
    CLIError.argumentNumberNotValid("create", 1, len(primaryArgs) - 1)
    sys.exit(1)
if command == "check":
    fatalError(f"Command \"check\" did not truly realized.")