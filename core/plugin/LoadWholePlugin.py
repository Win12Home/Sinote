from datetime import datetime
from pathlib import Path

from core.plugin.LoadPluginBase import LoadPluginBase
from core.plugin.LoadPluginHeader import LoadPluginHeader
from core.plugin.functionCreator import functionCreator
from utils.argumentParser import debugMode
from utils.jsonLoader import load
from utils.logger import Logger


class LoadWholePlugin:
    def __init__(self, projName: str):
        """
        Load Plugin Information
        :param projName: Project Name
        """
        self.projName = projName
        self.headerPlacePath = f"{projName}/headers"
        self.infoPath = f"{projName}/info.json"
        self.importsPath = f"{projName}/imports.txt"

    def lexImports(self, importText: str) -> list | None:
        """
        Lex imports.txt
        :param importText: the string of imports.txt
        :return: a list or None
        """
        lexedList: list = []
        if debugMode:
            Logger.debug(
                "Attempting to load imports.txt, content: {} 🔎".format(
                    importText.replace("\n", "\\n")
                ),
                "LexImportsActivity",
            )
            for temp in importText.split("\n"):
                Logger.debug(
                    f"Attempting to lex content: {temp.strip()} 🔎",
                    "LexImportsActivity",
                )
                if temp.strip() is None:
                    Logger.debug(
                        "Failed to load content because this content is NULL! ❌",
                        "LexImportsActivity",
                    )
                elif temp.strip().startswith("//"):
                    Logger.debug("Automatic skip note 💥", "LexImportsActivity")
                else:
                    lexedList.append(temp.strip().replace("&space;", " "))
                    Logger.debug("Successfully to lex content ✅", "LexImportsActivity")
            Logger.debug(
                "Lex successfully, program will be import these files: {} 🥳".format(
                    ", ".join(lexedList)
                ),
                "LexImportsActivity",
            )
        else:
            for temp in importText.split("\n"):
                if not (temp.strip() is None or temp.strip().startswith("//")):
                    lexedList.append(temp.strip().replace("&space;", " "))
        return None if (len(lexedList) == 0) else lexedList

    def getValue(self) -> list | int | None:
        try:
            self.info: dict = {
                "icon": None,
                "name": "Unnamed Plugin",
                "objectName": f"sinote.unnamedPlugins.{self.projName}",
                "version": "VER.VER.VER",
                "versionIterate": 99900,
                "customizeRemoveString": {
                    "en_US": "Do you want to remove it? It won't be back!",
                    "zh_CN": "你要永久删除这个插件吗？删除之后就真没了！",
                },
                "author": ["Author not found"],
            }
            errLite: bool = False
            Logger.info(f'Attempting to load plugin "{self.projName}" 🔎')
            beforeDatetime: datetime = datetime.now()
            if (
                not Path(f"./resources/plugins/{self.projName}").is_dir()
                and not Path(f"./resources/plugins/{self.projName}").exists()
            ):
                self.err("Directory not found.")
                return 3
            if not Path(f"./resources/plugins/{self.infoPath}").exists():
                self.err("Missing info.json!")
                return 2
            if not Path(f"./resources/plugins/{self.importsPath}").exists():
                Logger.error(
                    "Missing imports.txt, plugin will continue load but it's not USEFUL.",
                )
                errLite = True
            Logger.info("Attempting to read info.json 🔎")
            info: dict = load(f"./resources/plugins/{self.infoPath}")
            if info.get("versionIterate", None) is None:
                Logger.warning(
                    '"versionIterate" not found! This will be replace to 99900 (Maximum) 😰',
                )
            Logger.info("Successfully to read info.json ✅")
            Logger.info("Attempting to merge info.json 🔎")
            information: dict = self.info | info
            information["icon"] = (
                None
                if not isinstance(information["icon"], str)
                else information["icon"]
                .lower()
                .replace("%pluginpath%", f"./resources/plugins/{self.projName}")
            )
            Logger.info("Successfully to merge info.json ✅")
            if information["versionIterate"] > 99900:
                information["versionIterate"] = 99900
                Logger.info(
                    'Number of "versionIterate" was more than 99900! "versionIterate" adjusted to 99900! 💥',
                )
            imports: list | None = None
            if not errLite:
                Logger.info("Attempting to read imports.txt ✅")
                with open(
                    f"./resources/plugins/{self.projName}/imports.txt",
                    "r",
                    encoding="utf-8",
                ) as f:
                    imports: list | None = self.lexImports(f.read())
                if imports is not None:
                    Logger.info("Load successfully! ✅")
                else:
                    errLite = True
                    Logger.warning(
                        "Cannot load imports.txt, plugin will continue load but it's not USEFUL. 😰"
                    )
            items: list = []
            items.append(information)
            tmp: list = []
            objectName: str = ""
            if not errLite:
                for temp in imports:
                    # For safe
                    LoadPluginBase.logIfDebug(
                        f"Trying to load header file in ./resources/plugins/{self.headerPlacePath}/{temp} 🪲"
                    )
                    temp2 = LoadPluginHeader(
                        f"./resources/plugins/{self.headerPlacePath}/{temp}"
                    )
                    temp2.setFilename(temp)
                    temp3 = temp2.getValue()
                    LoadPluginBase.logIfDebug(f"Loaded Plugin Header! JSON: {temp2} 🤓")
                    if not isinstance(temp3, list):
                        if temp2 is None:
                            Logger.warning(
                                f"Skipped file {temp} because it's a Placeholder File ❌",
                            )
                        elif isinstance(temp3, int):
                            Logger.error(
                                f"Illegal error, returns: {LoadPluginBase.parseErrCode(temp3)} 😰",
                            )
                    else:
                        objectName = f"{information["objectName"]}.{"syntax" if temp3[1] == 1 else "functions" if temp3[1] == 0 else "null"}.{temp3[0]}"
                        LoadPluginBase.logIfDebug(f"Loading {objectName}... 😍")
                        if temp3[1] == 0:
                            LoadPluginBase.logIfDebug(
                                f"Creating function that object name is {temp3[0]}. 🔎"
                            )
                            returned = [functionCreator(i[0]) for i in temp3[2].values() if iter(i) and i[1]]
                            tmp.append([objectName, 0, returned])
                        elif temp3[1] == 1:
                            LoadPluginBase.logIfDebug(
                                "Appending QSyntaxHighlighter and Informations... 🔎"
                            )
                            tmp.append(
                                [
                                    objectName,
                                    1,
                                    temp3[2],
                                    temp3[3],
                                    temp3[4],
                                    temp3[5],
                                    temp3[6],
                                ]
                            )
                            LoadPluginBase.logIfDebug("Successfully to append! ✅")
                # Convert normal value to [<TYPE>,<OBJNAME>,<CONTENT>]
                items.append(tmp)
            else:
                listOfHeaders = None
                items.append(None)
            Logger.info(
                f"Successfully to load {information["objectName"]}! Used {(datetime.now() - beforeDatetime).total_seconds()}secs. ✅",
            )
            return items
        except Exception as e:
            self.err(f"Unknown Error, Python Exception: {e!r}")
            return -1

    def err(self, error: str):
        Logger.error(f'Cannot load plugin that directory name is "{self.projName}"')
        Logger.error(f"Reason: {error}")
