from datetime import datetime
from typing import AnyStr, Callable

from core.plugin.LoadPluginBase import LoadPluginBase
from json5 import loads
from utils.argumentParser import debugMode
from utils.const import apiVersion
from utils.jsonLoader import load
from utils.logger import Logger

debugLog: Callable = lambda content: (
    Logger.debug(content, "LoadPluginHeaderActivity") if debugMode else None
)


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
        Logger.error(
            f'Error while loading file "{self.filename}": {error}',
            "LoadPluginHeaderActivity",
        )
        Logger.error(f"Cannot continue load plugin!", "LoadPluginHeaderActivity")

    def getValue(self) -> int | list | None:
        """
        Load plugin and return a format like this:
        [<objName>,<type>,{<settings>}]
        :return: Integer (follow LoadPluginBase.parseErrCode) List (plugin)
        """
        items: list = []
        try:
            beforeDatetime = datetime.now()
            Logger.info(
                f"Attempting to load {self.filename} 🔎", "LoadPluginHeaderActivity"
            )
            self.config = {
                "type": 0,
                "api": [1, apiVersion[0]],
                "enableCustomizeCommandRun": False,
                "useSinoteVariableInString": True,
            }
            debugLog(f"Checking header that its path is {self.filename}")
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
            debugLog("No error, continue lex!")
            debugLog("Putting objectName and type into lexed list...")
            # Add objectName to the list
            items.append(config["objectName"])
            items.append(
                config.get("type", 0)
                if isinstance(self.header["config"].get("type", 0), int)
                else 0
            )
            debugLog("Finished putting task!")
            debugLog(f"Header type: Type {items[1]}")
            if items[1] == 0:
                # Check functions and runFunc
                functions: dict | None = self.header.get("functions", None)
                runFunc: list | None = self.header.get("runFunc", None)
                debugLog("Checking functions...")
                if (
                    not functions
                    or not runFunc
                    or config["enableCustomizeCommandRun"] == False
                ):
                    Logger.warning(
                        f'File "{self.filename}" is a Placeholder File (\'Cause no function and runFunc, or "enableCustomizeCommandRun" not enabled)',
                    )
                    # Interrupt
                    return None
                realFuncs: dict = {}
                for funcName, funcProg in functions.items():
                    debugLog(f"Checking function: {funcName}...")
                    if not isinstance(funcName, str):
                        Logger.warning(
                            f"Ignored the {funcName} function 'caused not a String function name.",
                        )
                        continue
                    if not isinstance(funcProg, list):
                        Logger.warning(
                            f"Ignored the {funcName} function 'caused not like this {r"\"String\":[]"}",
                        )
                        continue
                    # More safe
                    if isinstance(funcProg, list):
                        temp: list = []
                        for line, k in enumerate(funcProg, 1):
                            debugLog(f"Checking sentence: {line}")
                            if not isinstance(k, list):
                                Logger.warning(
                                    f"Ignored {line}th line in the {funcName} function 'caused isn't a List format.",
                                )
                                continue
                            if len(k) < 2:
                                Logger.warning(
                                    f"Ignored {line}th line in the {funcName} function 'caused isn't a List format.",
                                )
                                continue
                            if not isinstance(k[0], str):
                                Logger.warning(
                                    f"Ignored {line}th line in the {funcName} function 'caused cannot call the System Function. (Reason: Not String)",
                                )
                                continue
                            if LoadPluginBase.functions.get(k[0].lower(), None) is None:
                                Logger.warning(
                                    f"Ignored {line}th line in the {funcName} function 'caused {k[0]} isn't a real function there.",
                                )
                                continue
                            debugLog(
                                "Valid sentence! Putting it into passed (things) list!"
                            )
                            k[0] = k[0].lower()
                            temp.append(k)
                        realFuncs[funcName] = temp
                # look for runFunc
                items.append({})
                for whichFuncToRun, func in realFuncs.items():
                    if whichFuncToRun not in runFunc:
                        Logger.warning(
                            f'{whichFuncToRun} declared there, but it is not in "runFunc", if you add it to "usefunc", please ignore this.',
                        )
                    items[2][whichFuncToRun] = (
                        func,
                        whichFuncToRun in runFunc,
                        # After 1.0.3, This will be add expression, like ("EXPRESSION", [FUNCLIST], bool IS_IN_AUTORUN)
                    )
            elif items[1] == 1:
                # Syntax Highlighter
                config: dict | None = self.header.get("coding", None)
                debugLog("Checking Syntax Highlighter Header...")
                if config is None:
                    self.err('Key "coding" not found 🤓')
                    return 0  # Missing Ingredients
                if not isinstance(config, dict):
                    self.err('"coding" need a dict type ❌')
                    return 0  # Missing Ingredients
                debugLog("No problem! Start to lex...")
                defaultConfig = {
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
                config: dict = defaultConfig | config
                items.append(config["codeName"])
                items.append(config["fileExtension"])
                items.append(
                    LoadPluginBase.LazyCustomizeSyntaxHighlighter(
                        [
                            config["keywords"],
                            config["symbols"],
                            config["remKeywords"],
                            config["remKeywordsMultipleLine"],
                            config["enableSelfColorOfRemKeywordsMultipleLine"],
                            config["textKeywords"],
                        ]
                    )
                )
                items.append(config["defineKeywords"])
                items.append(config["pairKeywords"])
                debugLog("OK! Successfully to put into lexed list!")
            else:
                self.err(
                    "Type is not support in this version (type==2 also not included)!"
                )
                return 0
            Logger.info(
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
