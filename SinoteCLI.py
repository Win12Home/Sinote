"""
Sinote Plugin CLI (spcli)
Win12Home (C) MIT.
"""
# Huh, I even not notice I edit MIT to GPL v2.0. Now I have edited.
from json import JSONDecodeError
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
        "Check plugins.",
        [
            "Directory path of your plugin. (1 to 50)"
        ],
        [
            "[purple]-npb/--no-progress-bar[/purple] Disable Progress bar when loading files that more than 2 (Include 2).",
            "[purple]-q/--quiet[/purple] Quiet to load",
            "[purple]--no-limit[/purple] Remove limit (once) to check lots of plugins."
        ],
        False
    ]
}

primaryArgList: list[str] = [
    "create",
    "check",
    "help"
]

hidedPrint: list[str] = []

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

    @staticmethod
    def print(*values):
        hidedPrint.append(" ".join(values))

    @staticmethod
    def checkTemplate(where: str, quiet: bool = False) -> Any:
        if quiet:
            print = CLIUsages.print
        else:
            from rich import print as print_
            print = print_
        print("[red]Attempting[/red] to check normal structure")
        from pathlib import Path
        from json import loads
        from json5 import loads as json5loads
        if not Path(where).exists():
            fatalError(f"{where} does not exist.")
            return [1, 0]
        if not Path(where).is_dir():
            fatalError(f"{where} is not a directory or it's a link.")
            return [1, 0]
        print("[green]Successfully[/green] to check normal structure")
        print("[red]Attempting[/red] to check plugin")
        errors: int = 0
        warns: int = 0
        whereImports: Path = Path(where) / "imports.txt"
        whereInfo: Path = Path(where) / "info.json"
        whereHeaders: Path = Path(where) / "headers"
        if not whereInfo.exists():
            print("[red]Error: [/red]info.json does not exist.")
            return [1, 0]
        elif not whereInfo.is_file():
            print("[red]Error: [/red]info.json is not a file.")
            return [1, 0]
        else:
            info: dict[str, Any] = {}
            try:
                with open(str(whereInfo), "r", encoding="utf-8") as f:
                    info = loads(f.read())
            except JSONDecodeError:
                with open(str(whereInfo), "r", encoding="utf-8") as f:
                    info = json5loads(f.read())
            except Exception as e:
                print(f"[red]Reading Error:[/red] Reason (__repr__): {repr(e)} (info.json)")
                errors += 1
            if len(info.keys()) != 0:
                infoKeys: dict[Any, Any] = {
                    "icon": lambda x: x is None or isinstance(x, str),
                    "name": lambda x: isinstance(x, str),
                    "objectName": lambda x: isinstance(x, str),
                    "version": lambda x: isinstance(x, str),
                    "versionIterate": lambda x: isinstance(x, int)
                }
                notNeeded: dict[Any, Any] = {
                    "customizeRemoveString": lambda x: isinstance(x, dict),
                    "author": lambda x: isinstance(x, list),
                    "description": lambda x: isinstance(x, str)
                }
                for k, w in info.items():
                    if not k in infoKeys.keys() and not k in notNeeded.keys():
                        print(f"[yellow]Warning: [/yellow]{k} is not a valid header key. (Of course you can keep it)")
                        warns += 1
                    elif k in infoKeys.keys():
                        if not infoKeys[k](w):
                            print(f"[yellow]Error: [/yellow]{str(type(w))} is not a valid type for {k}.")
                            errors += 1
                    elif k in notNeeded.keys():
                        if not notNeeded[k](w):
                            print(f"[yellow]Error: [/yellow]{str(type(w))} is not a valid type for {k}.")
                            errors += 1
            else:
                print("[red]Error: [/red]info.json has no keys or read failed!")
                errors += 1
        if not whereImports.exists():
            print("[yellow]Warning: [/yellow]imports.txt does not exist.")
            warns += 1
        elif whereImports.exists() and whereImports.is_file():
            if not whereHeaders.exists():
                print("[red]Error:[/red] header directory does not exist.")
                errors += 1
                return [errors, warns]
            if not whereHeaders.is_dir():
                print("[red]Error:[/red] header directory is not a directory.")
                errors += 1
                return [errors, warns]
            try:
                imports: list[Path] = []
                with open(str(whereImports), "r", encoding="utf-8") as f:
                    imports = [whereHeaders / i.replace("$space;"," ") for i in f.read().splitlines() if not i.strip().startswith("//")]
                for i in imports:
                    success: bool = True
                    print(f"[blue]Checking[/blue] header file {i.name}")
                    if not i.exists():
                        print(f"[yellow]Warning: [/yellow]{str(i)} do not exist.")
                        warns += 1
                    elif not i.is_file():
                        print(f"[yellow]Warning: [/yellow]{str(i)} do not a file.")
                        warns += 1
                    else:
                        if i.suffix.lower()[1:] not in ["sph", "si_plug_h", "spheader", "sinote_plugin_header"]:
                            print(f"[yellow]Warning: [/yellow]There is a good new and a bad new. The good one is your suffix is creative! The bad one is {i.name}'s suffix is not valid!")
                        headerStruct: dict[str, Any] = {
                            "type": lambda x: isinstance(x, int),
                            "api": lambda x: isinstance(x, list),
                            "objectName": lambda x: isinstance(x, str)
                        }
                        notNeeded: dict[str, Any] = {
                            "enableCustomizeCommandRun": lambda x: isinstance(x, bool),
                            "useSinoteVariableInString": lambda x: isinstance(x, bool),
                        }
                        finallyGet: dict[str, Any] = {}
                        try:
                            with open(str(i), "r", encoding="utf-8") as f:
                                finallyGet = loads(f.read())
                        except (JSONDecodeError, ValueError):
                            with open(str(i), "r", encoding="utf-8") as f:
                                finallyGet = json5loads(f.read())
                        except Exception as e:
                            print(f"[red]Reading Error:[/red] Reason (__repr__): {repr(e)}")
                            errors += 1
                            success = False
                            continue
                        if "config" not in finallyGet.keys():
                            print("[red]Header Error: [/red] \"config\" item is needed in per header!")
                            errors += 1
                            success = False
                            continue
                        if not isinstance(finallyGet["config"], dict):
                            print("[red]Header Error: [/red] \"config\" item must be a Dict in per header!")
                            errors += 1
                            success = False
                            continue
                        for k, w in finallyGet["config"].items():
                            if k not in headerStruct.keys() and k not in notNeeded.keys():
                                print(f"[yellow]Warning: [/yellow]{k} is not a valid header key. (Of course you can keep it)")
                                warns += 1
                                success = False
                            if k in headerStruct.keys():
                                if not headerStruct[k](w):
                                    print(f"[yellow]Error: [/yellow]{str(type(w))} is not a valid type for {k}.")
                                    errors += 1
                                    success = False
                            if k in notNeeded.keys():
                                if not notNeeded[k](w):
                                    print(f"[yellow]Error: [/yellow]{str(type(w))} is not a valid type for {k}.")
                                    errors += 1
                                    success = False
                    print(f"{i.name} is {"[green]a normal header file :)[/green]" if success else "[red]not valid.[/red]"}")
            except Exception as e:
                print(f"[red]Reading Error:[/red] Reason (__repr__): {repr(e)}")
                errors += 1
        print("[green]Successfully[/green] to check plugin")
        return [errors, warns]


class CLIError:
    @staticmethod
    def argumentNumberNotValid(command: AnyStr, min: int, max: int, got: int = None):
        if got is None:
            fatalError(f"{command} need {min} arguments, got {max} arguments.")
            return
        fatalError(f"{command} need {min} to {max} arguments, got {got} arguments.")


class ArgumentParser:
    @staticmethod
    def checkArgumentOfCommandCheck(args: list[str]) -> list[bool] | None:
        parsed: list[list[str]] = [lexArgument(i) for i in args]
        valids: list[str] = [
            "-q",
            "--quiet",
            "-npb",
            "--no-progress-bar",
            "--no-limit"
        ]
        normal: list[bool] = [
            False,
            False,
            False
        ]
        for temp in parsed:
            if not temp[0] in valids:
                print(f"[yellow]warn: [/yellow]{temp[0]} is not a valid option.")
                continue
            elif len(temp) >= 2:
                print(f"[yellow]warn: [/yellow]{temp[0]} is only a boolean option, not an argument-needed option.")
                continue
            if temp[0] in ["--no-progress-bar", "-npb"]:
                normal[1] = True
            elif temp[0] in ["--quiet", "-q"]:
                normal[0] = True
            elif temp[0] == "--no-limit":
                normal[2] = True
        return normal


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
    args: list[bool] = ArgumentParser.checkArgumentOfCommandCheck(notRequiredArgs)
    if len(primaryArgs) == 2 and not args[0]:
        a = CLIUsages.checkTemplate(primaryArgs[1])
        if isinstance(a, list):
            print()
            print(f"[red]Errors:[/red] {a[0]} [yellow]Warnings:[/yellow] {a[1]} {"\nThis plugin was [green]passed[/green]!" if a[0] == 0 and a[1] == 0 else "\nThis plugin[red] is not valid[/red]"}")
    elif ((len(primaryArgs) > 2 and len(primaryArgs) <= 51) or args[2]) and not args[1]:
        totals: list[list[str | int]] = []
        from pathlib import Path
        from tqdm import tqdm
        for i in tqdm(primaryArgs[1:], desc="Checking plugins...", unit=" plugins"):
            a = CLIUsages.checkTemplate(i, True)
            if isinstance(a, list):
                totals.append([
                    str(Path(i)),
                    a[0],
                    a[1]
                ])
        print()
        allPassed: bool = True
        for i in totals:
            if i[1] + i[2] != 0:
                allPassed = False
            print(f"Plugin in [green]{i[0]}[/green]: [red]Errors: [/red]{i[1]} [yellow]Warning: [/yellow]{i[2]}")
        if not allPassed:
            print("\n".join(hidedPrint))
        print()
        print(f"All {len(totals)} plugins [green]passed[/green]." if allPassed else "Someone plugins [red]failed[/red]! Check your plugin [strong]please![/strong]")
    elif (len(primaryArgs) > 1 and len(primaryArgs) <= 51) or args[2]:
        from tqdm import tqdm
        if len(primaryArgs) > 2:
            allPassed: bool = True
            if args[1]:
                for i in primaryArgs[1:]:
                    a = CLIUsages.checkTemplate(i, args[0])
                    if a[0] + a[1] != 0:
                        allPassed = False
            else:
                for i in tqdm(primaryArgs[1:], desc="Checking plugins...", unit=" plugins"):
                    a = CLIUsages.checkTemplate(i, args[0])
                    if a[0] + a[1] != 0:
                        allPassed = False
            print()
            print(
                f"All {len(primaryArgs) - 1} plugins [green]passed[/green]." if allPassed else "Someone plugins [red]failed[/red]! Check your plugin [strong]please![/strong]")
        else:
            a = CLIUsages.checkTemplate(primaryArgs[1], args[0])
            print(f"[red]Error:[/red] {a[0]} [yellow]Warning:[/yellow] {a[1]} {"\nThis plugin was [green]passed[/green]!" if a[0] == 0 and a[1] == 0 else "\nThis plugin[red] is not valid[/red]"}")
    else:
        CLIError.argumentNumberNotValid("check", 1, 50, len(primaryArgs) - 1)
        sys.exit(1)
    sys.exit(0)