from core.plugin.LoadPluginBase import LoadPluginBase
from utils.logger import addLog
from utils.jsonLoader import load
from utils.const import apiVersion
from json5 import loads
from typing import AnyStr
from datetime import datetime


class LoadPluginHeader:
    """
    config needed
    Key: type | Header Type, for look please go to ./documentation/pluginEdit/header.md
    """

    def __init__(self, header: AnyStr | dict, filename: AnyStr = None):
        self.filename = filename
        self.header = (
            header
            if isinstance(header, dict)
            else loads(header) if filename else self.readFile(header)
        )

    def setFilename(self, filename: AnyStr):
        self.filename = filename

    def err(self, error: str):
        addLog(2, f'Error while loading file "{self.filename}": {error}')
        addLog(2, f"Cannot continue load plugin!")

    def getValue(self) -> int | list | None:
        """
        Load plugin and return a format like this:
        [<objName>,<type>,{<settings>}]
        :return: Integer (follow LoadPluginBase.parseErrCode) List (plugin)
        """
        items: list = []
        try:
            beforeDatetime = datetime.now()
            addLog(0, f"Attempting to load {self.filename} 🔎")
            self.config = {
                "type": 0,
                "api": [1, apiVersion[0]],
                "enableCustomizeCommandRun": False,
                "useSinoteVariableInString": True,
            }
            if not self.header.get("config", None):
                self.err('Key "config" not found! ❌')
                return 0
            config = self.config | self.header["config"]
            if "objectName" not in config:
                self.err('"objectName" is a required item in config ❌')
                return 0
            if not (config["api"][0] <= apiVersion[0] <= config["api"][1]):
                self.err(
                    "This plugin not support API of this version! Please update to new version."
                )
                return 1
            # Add objectName to the list
            items.append(config["objectName"])
            items.append(
                config.get("type", 0)
                if isinstance(self.header["config"].get("type", 0), int)
                else 0
            )
            if items[1] == 0:
                # Check functions and runFunc
                functions: dict | None = self.header.get("functions", None)
                runFunc: list | None = self.header.get("runFunc", None)
                if (
                    not functions
                    or not runFunc
                    or config["enableCustomizeCommandRun"] == False
                ):
                    addLog(
                        1,
                        f'File "{self.filename}" is a Placeholder File (\'Cause no function and runFunc, or "enableCustomizeCommandRun" not enabled)',
                    )
                    # Interrupt
                    return None
                realFuncs: dict = {}
                for funcName, funcProg in functions.items():
                    if not isinstance(funcName, str):
                        addLog(
                            1,
                            f"Ignored the {funcName} function 'caused not a String function name.",
                        )
                        continue
                    if not isinstance(funcProg, list):
                        addLog(
                            1,
                            f"Ignored the {funcName} function 'caused not like this {r"\"String\":[]"}",
                        )
                        continue
                    # More safe
                    if isinstance(funcProg, list):
                        temp: list = []
                        for line, k in enumerate(funcProg, 1):
                            if not isinstance(k, list):
                                addLog(
                                    1,
                                    f"Ignored {line}th line in the {funcName} function 'caused isn't a List format.",
                                )
                                continue
                            if len(k) < 2:
                                addLog(
                                    1,
                                    f"Ignored {line}th line in the {funcName} function 'caused isn't a List format.",
                                )
                                continue
                            if not isinstance(k[0], str):
                                addLog(
                                    1,
                                    f"Ignored {line}th line in the {funcName} function 'caused cannot call the System Function. (Reason: Not String)",
                                )
                                continue
                            if LoadPluginBase.functions.get(k[0].lower(), None) is None:
                                addLog(
                                    1,
                                    f"Ignored {line}th line in the {funcName} function 'caused {k[0]} isn't a real function there.",
                                )
                                continue
                            k[0] = k[0].lower()
                            temp.append(k)
                        realFuncs[funcName] = temp
                # look for runFunc
                items.append({})
                for whichFuncToRun in runFunc:
                    if whichFuncToRun not in realFuncs:
                        addLog(
                            1,
                            f'{whichFuncToRun} defined in runFunc but didn\'t define in "functions".',
                        )
                    items[2][whichFuncToRun] = realFuncs[whichFuncToRun]
            elif items[1] == 1:
                # Syntax Highlighter
                coding: dict | None = self.header.get("coding", None)
                if coding is None:
                    self.err('Key "coding" not found 🤓')
                    return 0  # Missing Ingredients
                if not isinstance(coding, dict):
                    self.err('"coding" need a dict type ❌')
                    return 0  # Missing Ingredients
                self.coding = {
                    "codeName": "Not defined",
                    "fileExtension": [],
                    "keywords": [],
                    "symbols": [],
                    "remKeywords": [],
                    "remKeywordsMultipleLine": [],
                    "enableSelfColorOfRemKeywordsMultipleLine": True,
                    "textKeywords": [],
                    "defineKeywords": ["{", "}"],
                    "pairKeywords": [],
                }
                coding: dict = self.coding | coding
                items.append(coding["codeName"])
                items.append(coding["fileExtension"])
                items.append(
                    LoadPluginBase.LazyCustomizeSyntaxHighlighter(
                        [
                            coding["keywords"],
                            coding["symbols"],
                            coding["remKeywords"],
                            coding["remKeywordsMultipleLine"],
                            coding["enableSelfColorOfRemKeywordsMultipleLine"],
                            coding["textKeywords"],
                        ]
                    )
                )
                items.append(coding["defineKeywords"])
                items.append(coding["pairKeywords"])
            else:
                self.err(
                    "Type is not support in this version (type==2 also not included)!"
                )
                return 0
            addLog(
                0,
                f"Successfully to load {self.filename}! Used {(datetime.now() - beforeDatetime).total_seconds():02f}secs.",
            )
            return items
        except Exception as e:
            self.err(f"Unknown Error, Python Exception: {e!r}")
            return -1

    @staticmethod
    def readFile(filePath: str):
        """
        Read a file and return dict.
        :param filePath: File Path
        :return: A dict object.
        """
        return load(filePath)
