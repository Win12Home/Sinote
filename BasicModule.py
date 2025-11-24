from PySide6.QtWidgets import *
from functools import singledispatch
from PySide6.QtCore import *
from PySide6.QtGui import *
from qt_material import *
from json5 import loads
from rich import print
from locale import getdefaultlocale
from warnings import *
from pathlib import Path
from platform import system, python_version, win32_ver, processor, libc_ver
from datetime import datetime
from traceback import format_exception
from typing import *
from psutil import virtual_memory, cpu_percent
from getpass import getuser
import sys, re

filterwarnings("ignore", category=DeprecationWarning)

# Generate QApplication

application = QApplication([])

apply_stylesheet(application,"dark_blue.xml")

apiVersion: tuple = (1,0,1)
sinoteVersion: str = "sinote-2025.01.00842-initial-preview-beta"

normalLogOutput: list[str] = []

def addLog(type: int=0, bodyText:str="N/A"):
    typeOfLog: str = ("INFO" if (type == 0) else "WARN" if (type == 1) else "ERR" if (type == 2) else "DBG" if (type == 3) else"N/A")
    nowTime: str = datetime.now().strftime("%H:%M.%S.%f")[:-3]
    normalLogOutput.append(f"[{nowTime}] [SinoteLog] [{typeOfLog}] {bodyText}")
    print(f"[[blue]{nowTime}[/blue]] [SinoteLog] [[red]{typeOfLog}[/red]] {bodyText}")

addLog(bodyText="Import Modules Finish!")
addLog(bodyText="Loading Language and Basic Information")
addLog(bodyText=r"   _____ _             __          ______    ___ __            ")
addLog(bodyText=r"  / ___/(_)___  ____  / /____     / ____/___/ (_) /_____  _____")
addLog(bodyText=r"  \__ \/ / __ \/ __ \/ __/ _ \   / __/ / __  / / __/ __ \/ ___/")
addLog(bodyText=r" ___/ / / / / / /_/ / /_/  __/  / /___/ /_/ / / /_/ /_/ / /    ")
addLog(bodyText=r"/____/_/_/ /_/\____/\__/\___/  /_____/\__,_/_/\__/\____/_/     ")
addLog(bodyText=f"Sinote Editor {sinoteVersion}, API Version: {".".join([f"{i}" for i in apiVersion])}")

def saveLog():
    if not Path("./log").exists():
        Path("./log").mkdir(exist_ok=True)
    if not Path("./log").is_dir():
        raise IOError("Cannot use ./log to write log! Sinote cannot continue running!")
    with open(datetime.now().strftime("./log/sinote-log-time-%Y-%m-%d-%H.%M.%S-output.log"),"w+",encoding="utf-8") as f:
        f.write("\n".join(normalLogOutput))

def err(error_code:str,parent:QWidget=None,no_occurred:bool=False):
    if not no_occurred:
        addLog(2,bodyText="Error Occurred, Program Used Function err to aborted running! Error Code: {}".format(error_code))
    w = QMessageBox.critical(None,"Error","Sinote has found a error! \nError Code: {}\nPlease contact developer or re-install software!".format(error_code))
    if not no_occurred:
        addLog(2,bodyText="Saving Error to local")
        saveLog()
    """
    Error Codes
    0xffffffff: Unknown Error, Traceback Hook Detected!
    0x00000001: BaseInfo.json not found, re-install software
    0x00000002: Other Language File not found, re-install software
    0x00000003: System isn't support (Only MacOS, Windows and Linux), use --bypass-system-check to bypass system check!
    """

err_exceptionhook_detected:bool = False

def criticalLogSaver(err_type, err_value, err_tb) -> None:
    """
    Save Critical Log Like this:
    Current Log:
      [logs]
    Error:
      [traceback]
    System Core Information:
      [info]
    Firmware Information:
      [info]
    Date:
      [date]
    Please feed back to Developer yet!
    
    And put it in folder ./log/critical
    :param err_type: Error Type
    :param err_value: Error Value
    :param err_tb: Error Traceback, for Format
    :return: NoneType
    """
    Path("./log/").mkdir(exist_ok=True)
    Path("./log/critical/").mkdir(exist_ok=True)
    string: str = f"Current Log:\n  {"\n  ".join(normalLogOutput)}\nError:\n  {"\n  ".join(format_exception(err_value))}\nFirmware Information:\n  CPU: {processor()}\n  CPU Usage: {cpu_percent(interval=1)}\n  RAM Used: {virtual_memory().used / (1024*1024)}MB\n  RAM Total: {virtual_memory().total / (1024*1024)}MB\n  Platform: {system()}\nDate\n  {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\nPlease feedback to developer yet!"
    with open(f"./log/critical/criticalLog-{datetime.now().strftime("%Y-%m-%d %H.%M.%S")}.log","w") as f:
        f.write(string)

def errExceptionHook(err_type, err_value, err_tb) -> None:
    """
    Attempting to cancel crash and pop-up a window, save critical log!
    :param err_type:
    :param err_value:
    :param err_tb:
    :return: NoneType
    """
    global err_exceptionhook_detected
    if err_exceptionhook_detected == False:
        err_exceptionhook_detected = True
        name: str = ""
        if hasattr(err_type, '__class__'):
            name = err_type.__class__.__name__
        else:
            name = type(err_type).__name__
        addLog(2, bodyText="Error occurred by errExceptionHook, please give the error to the author!")
        addLog(0, bodyText=f"Output has printed:\n{str(err_type)[8:-2]}: {err_value}")
        addLog(1, bodyText=f"Starting Window, if error occurred again, it won't write log when quit.")
        err("0xffffffff",None,True)
        addLog(0, bodyText="Attempting to save Critical Log")
        criticalLogSaver(err_type,err_value,err_tb)
        addLog(0,bodyText="It might be successfully to save, please feedback to developer! Program will continue running.")
        err_exceptionhook_detected = False
    else:
        sys.__excepthook__(err_type,err_value,err_tb)


sys.excepthook = lambda a,b,c: errExceptionHook(a,b,c)

debugMode: bool = False

loadedJson: dict = {}

# basicInfo will be BaseInfo.json
basicInfo: dict = {}


lang = "en_US"
try:
    with open("./resources/language/{}/BaseInfo.json".format(lang),"r",encoding="utf-8") as f:
        basicInfo = loads(f.read())
except:
    addLog(2,"BaseInfo.json not found")
    err("0x00000001")
    quit(1)

# Look at the system
args = [i.lower() for i in sys.argv]

if "-h" in args or "--help" in args:
    QMessageBox.information(None,"Help","-h/--help: Arguments Help of Sinote\n-su/--use-root-user: Bypass check for SU User in posix env\n--bypass-system-check: Bypass System Check (Windows, Linux, Mac OS)")

if not system().lower() in ["darwin", "linux", "windows"] and not "--bypass-system-check" in args:
    addLog(2,"Your system isn't a Darwin Based, a Linux Based or Windows, cannot continue run safety, use --bypass-system-check to bypass.")
    err("0x00000003")
    quit(1)

if system().lower() in ["darwin","linux"]:
    if getuser() == "root":
        addLog(1,"We recommend to use Normal User in posix env. But use ROOT User is not SAFE for your OS! Please use Normal User Instead! (Excepted you have known it's unsafe or you wanna edit System File like GRUB)")
        if not ("--use-root-user" in args or "-su" in args):
            QMessageBox.warning(None, "Warning",
                                     "We have noticed you run Sinote by ROOT/SU User, please remove 'sudo' command or exit 'su' environment. \nOr you can append -su for argument to bypass.")

if "--debug-mode" in args or "-db" in args:
    debugMode = True

for temp in basicInfo["item.list.language_files"]:
    if not Path("./resources/language/{}/{}.json".format(lang,temp)).exists():
        addLog(2,"Check Language files failed!")
        err("0x00000002")
        quit(1)


# Check the Beta Version
def checkVersionForPopup():
    if basicInfo["item.bool.isbetaversion"]:
        w = QMessageBox.warning(None,basicInfo["item.text.warn"],basicInfo["item.text.betaverdesc"])

def loadJson(json_name: str):
    if not Path("./resources/language/{}/{}.json".format(lang,json_name)).exists():
        addLog(2, "Failed to load when load this Language File: {}".format(json_name))
        err("0x00000002")
        quit(1)

def outputDeveloperDebugInformation():
    addLog(0, "For Developer Debug, Output your own PC's environment!")
    addLog(0, f"Platform: {system()} Python: {python_version()} Win32 Version*: {" ".join(win32_ver())} | Linux LIBC Ver*: {" ".join(libc_ver())}")
    addLog(0, "Note: If some error occurred, please send log to the developer")


class LoadPluginBase:
    functions: dict = {
        # Base Functions
        "print": 0,
        "msgbox": 1,
        "log": 2,
        "var": 3,
        "vpr": 4,
        "msgin": 5,
        "system": 6,
        "usefunc": 7,
        # Advanced Functions
        "set": 100,
        "mkdir": 101,
        "cfile": 102,
        "efile": 103,
        "pfile": 104,
        "dfile": 105,
        "afile": 106,
        "wfile": 107,
        "rfile": 108,
        # GUI Functions
        "errbox": 200
    }

    class ConfigKeyNotFoundError(Exception): ...

    @staticmethod
    def parseErrCode(code: int):
        errCodeDefinitions: dict = {
            0: "Missing Ingredients",
            1: "API is too low or high",
            2: "Missing File",
            3: "Not a sure plugin",
            -1: "Unknown Error"
        }
        return code

    class CustomizeSyntaxHighlighter(QSyntaxHighlighter):
        def __init__(self, syntaxList: list, parent: QTextDocument = None):
            """
            Initialize Customize Syntax Highlighter
            :param syntaxList: syntax list, lexed from LoadPluginHeader object
            :param parent: QTextDocument of a PlainTextEdit or TextEdit
            """
            super().__init__(parent)

            self.keywords = syntaxList[0] if len(syntaxList) > 0 else []
            self.symbols = syntaxList[1] if len(syntaxList) > 1 else []
            self.remKeywords = syntaxList[2] if len(syntaxList) > 2 else []
            self.remKeywordsMultipleLine = syntaxList[3] if len(syntaxList) > 3 else []
            self.enableSelfColor = syntaxList[4] if len(syntaxList) > 4 else True
            self.textKeywords = syntaxList[5] if len(syntaxList) > 5 else []

            self.highlight_rules = []
            self.multi_line_patterns = []

            self._setup_formats()
            self._setup_highlighting_rules()

            addLog(0, f"Syntax highlighter initialized with {len(self.keywords)} keywords, {len(self.symbols)} symbols")

        def _setup_formats(self):
            self.keyword_format = QTextCharFormat()
            self.keyword_format.setForeground(QColor('#569CD6'))
            self.keyword_format.setFontWeight(QFont.Weight.Bold)

            self.symbol_format = QTextCharFormat()
            self.symbol_format.setForeground(QColor('#D4D4D4'))

            self.single_comment_format = QTextCharFormat()
            self.single_comment_format.setForeground(QColor('#6A9955'))
            self.single_comment_format.setFontItalic(True)

            self.multi_comment_format = QTextCharFormat()
            self.multi_comment_format.setForeground(QColor('#6A9955'))
            self.multi_comment_format.setFontItalic(True)

            self.string_format = QTextCharFormat()
            self.string_format.setForeground(QColor('#CE9178'))

        def _setup_highlighting_rules(self):
            self._add_keyword_rules()
            self._add_symbol_rules()
            self._add_single_comment_rules()
            self._add_multi_comment_rules()
            self._add_string_rules()

        def _add_keyword_rules(self):
            for keyword in self.keywords:
                pattern = QRegularExpression(r'\b' + re.escape(keyword) + r'\b')
                self.highlight_rules.append((pattern, self.keyword_format))

        def _add_symbol_rules(self):
            for symbol in self.symbols:
                escaped_symbol = re.escape(symbol)
                pattern = QRegularExpression(escaped_symbol)
                self.highlight_rules.append((pattern, self.symbol_format))

        def _add_single_comment_rules(self):
            for comment_mark in self.remKeywords:
                pattern = QRegularExpression(re.escape(comment_mark) + r'[^\n]*')
                self.highlight_rules.append((pattern, self.single_comment_format))

        def _add_multi_comment_rules(self):
            if len(self.remKeywordsMultipleLine) >= 2 and self.enableSelfColor:
                start_mark, end_mark = self.remKeywordsMultipleLine[0], self.remKeywordsMultipleLine[1]
                pattern = QRegularExpression(
                    re.escape(start_mark) + r'.*?' + re.escape(end_mark),
                    QRegularExpression.PatternOption.DotMatchesEverythingOption
                )
                self.highlight_rules.append((pattern, self.multi_comment_format))

                self.multi_line_patterns.append({
                    'start': QRegularExpression(re.escape(start_mark)),
                    'end': QRegularExpression(re.escape(end_mark)),
                    'format': self.multi_comment_format
                })

        def _add_string_rules(self):
            for string_mark in self.textKeywords:
                pattern = QRegularExpression(
                    re.escape(string_mark) + r'([^"\\]|\\.)*?' + re.escape(string_mark)
                )
                self.highlight_rules.append((pattern, self.string_format))

        def highlightBlock(self, text: str):
            for pattern, format in self.highlight_rules:
                match_iterator = pattern.globalMatch(text)
                while match_iterator.hasNext():
                    match = match_iterator.next()
                    self.setFormat(match.capturedStart(), match.capturedLength(), format)

            self.setCurrentBlockState(0)
            self.highlight_multi_line_comments(text)

        def highlight_multi_line_comments(self, text: str):
            if not self.multi_line_patterns or not self.enableSelfColor:
                return

            for multi_line in self.multi_line_patterns:
                start_match = multi_line['start'].match(text)
                end_match = multi_line['end'].match(text)

                if start_match.hasMatch():
                    start_index = start_match.capturedStart()
                    if end_match.hasMatch():
                        end_index = end_match.capturedEnd()
                        self.setFormat(start_index, end_index - start_index, multi_line['format'])
                    else:
                        self.setFormat(start_index, len(text) - start_index, multi_line['format'])


class LoadPluginHeader:
    """
    config needed
    Key: type | Header Type, for look please go to ./documentation/pluginEdit/header.md
    """
    def __init__(self, header: AnyStr | dict, filename: AnyStr = None):
        self.filename = filename
        self.header = header if isinstance(header, dict) else loads(header) if filename else self.readFile(header)

    def err(self, error: str):
        addLog(2, f"Error while loading file \"{self.filename}\": {error}")
        addLog(2,f"Cannot continue load plugin!")

    def getValue(self) -> int | list | None:
        """
        Load plugin and return a format like this:
        [<objName>,<type>,{<settings>}]
        :return: Integer (follow LoadPluginBase.parseErrCode) List (plugin)
        """
        items: list = []
        try:
            beforeDatetime = datetime.now()
            addLog(0,f"Attempting to load {self.filename}")
            self.config = {
                "type": 0,
                "api": [1,apiVersion[0]],
                "enableCustomizeCommandRun": False,
                "useSinoteVariableInString": True
            }
            if not self.header.get("config",None):
                self.err("Key \"config\" not found!")
                return 0
            config = self.config | self.header["config"]
            if "objectName" not in config:
                self.err("\"objectName\" is a required item in config.")
                return 0
            if not (config["api"][0] <= apiVersion[0] <= config["api"][1]):
                self.err("This plugin not support API of this version! Please update to new version.")
                return 1
            # Add objectName to the list
            items.append(config["objectName"])
            items.append(config.get("type", 0) if isinstance(self.header["config"].get("type", 0), int) else 0)
            if items[1] == 0:
                # Check functions and runFunc
                functions: dict | None = self.header.get("function", None)
                runFunc: list | None = self.header.get("runFunc",None)
                if not functions or not runFunc or config["enableCustomizeCommandRun"] == False:
                    addLog(1, f"File \"{self.filename}\" is a Placeholder File ('Cause no function and runFunc)")
                    # Interrupt
                    return None
                realFuncs: dict = {}
                for funcName,funcProg in functions.items():
                    if not isinstance(funcName, str):
                        addLog(1, f"Ignored the {funcName} function 'caused not a String function name.")
                        continue
                    if not isinstance(funcProg, list):
                        addLog(1,f"Ignored the {funcName} function 'caused not like this {r"\"String\":[]"}")
                        continue
                    # More safe
                    if isinstance(funcProg, list):
                        temp: list = []
                        for line, k in enumerate(funcProg,1):
                            if not isinstance(k, list):
                                addLog(1,f"Ignored {line}th line in the {funcName} function 'caused isn't a List format.")
                                continue
                            if len(k) < 2:
                                addLog(1,f"Ignored {line}th line in the {funcName} function 'caused isn't a List format.")
                                continue
                            if not isinstance(k[0], str):
                                addLog(1,f"Ignored {line}th line in the {funcName} function 'caused cannot call the System Function. (Reason: Not String)")
                                continue
                            if LoadPluginBase.functions.get(k[0].lower(), None) is None:
                                addLog(1,f"Ignored {line}th line in the {funcName} function 'caused {k[0]} isn't a real function there.")
                                continue
                            k[0] = LoadPluginBase.functions.get(k[0].lower())
                            temp.append(k)
                        realFuncs[funcName] = temp
                # look for runFunc
                items.append({})
                for whichFuncToRun in runFunc:
                    if whichFuncToRun not in realFuncs:
                        addLog(1,f"{whichFuncToRun} defined in runFunc but didn't define in \"functions\".")
                    items[2][whichFuncToRun] = realFuncs[whichFuncToRun]
            elif items[1] == 1:
                # Syntax Highlighter
                coding: dict = self.header.get("coding",None)
                if coding is None:
                    self.err("Key \"coding\" not found")
                    return 0    # Missing Ingredients
                if not isinstance(coding,dict):
                    self.err("\"coding\" need a dict type")
                    return 0    # Missing Ingredients
                self.coding = {
                    "codeName": "Not defined",
                    "fileExtension": [],
                    "keywords": [],
                    "symbols": [],
                    "remKeywords": [],
                    "remKeywordsMultipleLine": [],
                    "enableSelfColorOfRemKeywordsMultipleLine": True,
                    "textKeywords": []
                }
                coding: dict = self.coding | coding
                items.append(coding["codeName"])
                items.append(coding["fileExtension"])
                items.append(LoadPluginBase.CustomizeSyntaxHighlighter(
                    [
                        coding["keywords"],
                        coding["symbols"],
                        coding["remKeywords"],
                        coding["remKeywordsMultipleLine"],
                        coding["enableSelfColorOfRemKeywordsMultipleLine"],
                        coding["textKeywords"]
                    ]
                ))
            else:
                self.err("Type is not support in this version (type==2 also not included)!")
                return 0
            addLog(0, f"Successfully to load {self.filename}! Used {(datetime.now() - beforeDatetime).total_seconds():02f}secs.")
            return items
        except Exception as e:
            self.err("Unknown Error, Python Exception: {}"
                                    .format(repr(e)))
            return -1

    @staticmethod
    def readFile(file_path: str):
        """
        Read a file and return dict.
        :param file_path: File Path
        :return: A dict object.
        """
        with open(file_path,"r",encoding="utf-8") as f:
           readStr: str = f.read()
        # Convert JSON text to dict
        return loads(readStr)

class LoadPluginInfo:
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
            addLog(3, "Attempting to load imports.txt, content: {}".format(importText.replace("\n","\\n")))
            for temp in importText.split("\n"):
                addLog(3, f"Attempting to lex content: {temp.strip()}")
                status: int = 0
                if temp.strip() is None:
                    addLog(3, "Failed to load content because this content is NULL!")
                    status = 1
                else:
                    lexedList.append(importText.strip().replace("&space;"," "))
                    addLog(3, "Successfully to lex content.")
            addLog(3, "Lex successfully, program will be import these files: {}".format(", ".join(lexedList)))
        else:
            for temp in importText.split("\n"):
                status: int = 0
                if temp.strip() is None:
                    status = 1
                else:
                    lexedList.append(importText.strip().replace("&space;"," "))
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
                    "zh_CN": "你要永久删除这个插件吗？删除之后就真没了！"
                },
                "author": [
                    "Author not found"
                ]
            }
            errLite: bool = False
            addLog(bodyText=f"Attempting to load plugin \"{self.projName}\"")
            beforeDatetime: datetime = datetime.now()
            if not Path(f"./resources/plugins/{self.projName}").is_dir() and not Path(f"./resources/plugins/{self.projName}").exists():
                self.err("Directory not found.")
                return 3
            if not Path(f"./resources/plugins/{self.infoPath}").exists():
                self.err("Missing info.json!")
                return 2
            if not Path(f"./resources/plugins/{self.importsPath}").exists():
                addLog(1, "Missing imports.txt, plugin will continue load but it's not USEFUL.")
                errLite = True
            addLog(bodyText="Attempting to read info.json")
            info: dict = LoadPluginHeader.readFile(f"./resources/plugin/{self.infoPath}")
            if info.get("versionIterate", None) is None:
                addLog(1, bodyText="\"versionIterate\" not found! This will be replace to 99900 (Maximum).")
            addLog(bodyText="Successfully to read info.json")
            addLog(bodyText="Attempting to merge info.json")
            information: dict = self.info | info
            addLog(bodyText="Successfully to merge info.json")
            if information["versionIterate"] > 99900:
                information["versionIterate"] = 99900
                addLog(1, "Number of \"versionIterate\" was more than 99900! \"versionIterate\" adjusted to 99900!")
            imports: list | None = None
            if not errLite:
                addLog(bodyText="Attempting to read imports.txt")
                with open(f"./resources/plugins/imports.txt","r",encoding="utf-8") as f:
                    imports: list | None = self.lexImports(f.read())
                if not imports:
                    addLog(bodyText="Load successfully!")
                else:
                    errLite = True
                    addLog(bodyText="Cannot load imports.txt, plugin will continue load but it's not USEFUL.")
            items: list = []
            items.append(information)
            if not errLite:
                for temp in imports:
                    # For safe
                    temp2 = LoadPluginHeader(f"./resources/plugins/{self.headerPlacePath}/{temp}").getValue()
                    if not isinstance(temp2, list):
                        continue
            else:
                listOfHeaders = None
        except Exception as e:
            self.err("Unknown Error, Python Exception: {}"
                                    .format(repr(e)))
            return -1

    def err(self, error: str):
        addLog(2, f"Cannot load plugin that directory name is \"{self.projName}\"")
        addLog(2, f"Reason: {error}")