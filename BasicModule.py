from datetime import datetime


# Set beforeDatetime for catalog
beforeDatetime = datetime.now()

from subprocess import Popen
from json import dumps, JSONDecodeError
from json import loads as normalLoads
from threading import Thread
from PySide6.QtWidgets import *
from functools import partial
from signal import SIGINT
from signal import signal as signalConnect
from PySide6.QtCore import *
from PySide6.QtGui import *
from qt_material import *
from json5 import loads
from rich import print
from locale import getdefaultlocale
from warnings import *
from pathlib import Path
from platform import system, python_version, win32_ver, processor, libc_ver
from traceback import format_exception
from typing import *
from psutil import virtual_memory, cpu_percent
from getpass import getuser
from enum import Enum
from multipledispatch import dispatch
import sys, re, pickle, hashlib

filterwarnings("ignore", category=DeprecationWarning)

# Generate QApplication

application = QApplication([])

apiVersion: tuple = (1,0,1)
sinoteVersion: str = "sinote-2025.1.00861-initial-preview-beta-v0.06.26001"

normalLogOutput: list[str] = []

onlyWarning: bool = False

colored: bool = True

class SafetyList(list):
    """
    A Safety dictionary
    """
    class OutErrors(Enum):
        NotFoundInIndex = 0

    def index(self, __value: Any, __start: int = 0, __end: int = None) -> int | OutErrors:
        if __value not in self[__start:__end] if __end is not None else __value not in self[__start:]:
            return self.OutErrors.NotFoundInIndex
        return super().index(__value, __start, __end if __end is not None else len(self))


class SafetyDict(dict):
    """
    A safety dictionary for language load
    It won't be raise KeyError at all!
    Like {"abc":"def"}
    dict_Initialized["abd"] -> return "abd"
    """
    class Properties(Enum):
        ReturnNormalItem = 0
        ReturnNormalize = 1

    def __getitem__(self, item: Any) -> Any:
        if item in self:
            return super().__getitem__(item)
        return item

    @dispatch(object)
    def get(self, _key: Any):
        return super().get(_key)

    @dispatch(object, object)
    def get(self, _key: Any, _default: Any):
        return super().get(_key, _default)

    @dispatch(object, Properties, object)
    def get(self, _key: Any, _prop: Properties, _default: Any = None):
        default: Any = _default if _prop.value == 1 else _key
        return super().get(_key, default)


def addLogClassic(type: int = 0, bodyText: str = "N/A", activity: str | None = None, placeholder: bool = False):
    typeOfLog: str = ("INFO" if (type == 0) else "WARN" if (type == 1) else "ERR" if (type == 2) else "DBG" if (type == 3) else "N/A")
    colorOfType: dict = {
        "INFO": "cyan",
        "WARN": "yellow",
        "ERR": "red",
        "DBG": "green",
        "N/A": "gray"
    }
    nowTime: str = datetime.now().strftime("%H:%M.%S.%f")[:-3]
    logSender: str = f"SinoteLog/[red]{activity}[/red]" if activity is not None else "SinoteLog"
    normalLogOutput.append(f"[{nowTime}] [SinoteLog{f"/{activity}" if activity is not None else ""}] [{typeOfLog}] {bodyText}")
    if colored:
        print(f"[[blue]{nowTime}[/blue]] [{logSender}] [[{colorOfType[typeOfLog]}]{typeOfLog}[/{colorOfType[typeOfLog]}]] {bodyText}")
    else:
        print(f"{nowTime} {"Main" if not activity else activity} {typeOfLog} {bodyText}")

def owLog(type: int = 0, bodyText: str = "N/A", activity: str | None = None, mustToPrint: bool = False):
    if type in [1, 2] or mustToPrint:  # Only output WARN&ERR, What the hell of that? 
        addLogClassic(type, bodyText, activity)

addLog = addLogClassic

def saveLog():
    if not Path("./log").exists():
        Path("./log").mkdir(exist_ok=True)
    if not Path("./log").is_dir():
        raise IOError("Cannot use ./log to write log! Sinote cannot continue running!")
    with open(datetime.now().strftime("./log/sinote-log-time-%Y-%m-%d-%H.%M.%S-output.log"),"w+",encoding="utf-8") as f:
        f.write("\n".join(normalLogOutput))

def err(error_code:str,parent:QWidget=None,no_occurred:bool=False):
    if not no_occurred:
        addLog(2,bodyText="Error Occurred, Program Used Function err to aborted running! Error Code: {}".format(error_code),activity="WindowsActivity")
    w = QMessageBox.critical(None,"Error","Sinote has found a error! \nError Code: {}\nPlease contact developer or re-install software!".format(error_code))
    if not no_occurred:
        addLog(2,bodyText="Saving Error to local",activity="FileConfigActivity")
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
    with open(f"./log/critical/criticalLog-{datetime.now().strftime("%Y-%m-%d %H.%M.%S")}.log","w",encoding="utf-8") as f:
        f.write(string)

keyboardInterruptProcess: bool = False
keyboardInterruptDatetime: datetime | None = None
def errExceptionHook(err_type, err_value, err_tb) -> None:
    """
    Attempting to cancel crash and pop-up a window, save critical log!
    :param err_type:
    :param err_value:
    :param err_tb:
    :return: NoneType
    """
    global err_exceptionhook_detected
    if not err_exceptionhook_detected:
        err_exceptionhook_detected = True
        name: str = ""
        if hasattr(err_type, '__class__'):
            name = err_type.__class__.__name__
        else:
            name = type(err_type).__name__
        addLog(2, bodyText="Error occurred by errExceptionHook, please give the error to the author!",activity="ExceptionHookActivity")
        addLog(0, bodyText=f"Output has printed:\n{str(err_type)[8:-2]}: {err_value}")
        addLog(1, bodyText=f"Starting Window, if error occurred again, it won't write log when quit.",activity="ExceptionHookActivity")
        err("0xffffffff",None,True)
        addLog(0, bodyText="Attempting to save Critical Log",activity="FileConfigActivity")
        criticalLogSaver(err_type,err_value,err_tb)
        addLog(0,bodyText="It might be successfully to save, please feedback to developer! Program will continue running.",activity="ExceptionHookActivity")
        err_exceptionhook_detected = False
    else:
        sys.__excepthook__(err_type,err_value,err_tb)

def interruptSignalBaseFunction(signum, frame) -> None:
    global keyboardInterruptProcess, keyboardInterruptDatetime
    if keyboardInterruptDatetime and keyboardInterruptProcess:
        if (datetime.now() - keyboardInterruptDatetime).seconds > 5:
            keyboardInterruptProcess = False   # Property
    if keyboardInterruptProcess:
        if (datetime.now() - keyboardInterruptDatetime).seconds <= 5:
            addLog(2, "Ctrl+C twice to exit unnormally!")
            addLog(2, "Saving log for a unnormally exit")
            saveLog()
            addLog(2, "Successfully to exit! Sinote will exit with code 100.")
            sys.exit(100)
    addLog(1, "Don't use Ctrl+C to exit unnormally! If you need, please re-enter Ctrl+C to exit.")
    keyboardInterruptProcess = True
    keyboardInterruptDatetime = datetime.now()
    return

def interruptSignal() -> None:
    signalConnect(SIGINT, interruptSignalBaseFunction)
    timer = QTimer()    # Super Qt's Timer
    timer.timeout.connect(lambda: None)
    timer.start(100)

def loadFonts() -> None:
    fontDatabase = QFontDatabase()
    fontsDir = Path("./resources/fonts")
    if not fontsDir.exists() or not fontsDir.is_dir():
        addLog(2, "./resources/fonts/ directory isn't exists or it isn't a true directory! ❌", "LoadFontActivity")
    if debugMode:
        addLog(3, "Loading fonts in ./resources/fonts... 🤔", "LoadFontActivity")
    loadedFontNums: int = 0
    totalFontNums: int = 0
    for temp in list(fontsDir.rglob("*.ttf")) + list(fontsDir.rglob("*.otf")):
        totalFontNums += 1
        loadReturn: int = fontDatabase.addApplicationFont(str(temp))
        if loadReturn != -1:
            fontDatabase.applicationFontFamilies(loadReturn)
            loadedFontNums+=1
            if debugMode:
                addLog(3, f"Successfully to load font {temp.name} ✅", "LoadFontActivity")
        else:
            addLog(2, f"Failed to load font {temp.name} ❌", "LoadFontActivity")
    if debugMode:
        addLog(3, f"Successfully to load all the fonts! Total: {totalFontNums} Loaded: {loadedFontNums} Not loaded: {totalFontNums - loadedFontNums}", "LoadFontActivity")

sys.excepthook = lambda a,b,c: errExceptionHook(a,b,c)

debugMode: bool = False

# basicInfo will be BaseInfo.json
basicInfo: dict = {}

# Check Arguments

lang = "en_US"
try:
    with open("./resources/language/{}/BaseInfo.json".format(lang),"r",encoding="utf-8") as f:
        basicInfo = loads(f.read())
except:
    addLog(2,"BaseInfo.json not found", "FileConfigActivity")
    err("0x00000001")
    sys.exit(1)

# Look at the system
args = [i.lower() for i in sys.argv[1:] if i.lower().startswith("-")]
fileargs = [i.lower() for i in sys.argv[1:] if not i.lower().startswith("-")]

normalSetting: dict = {
    "fontName": "Fira Code",
    "fontSize": 12,
    "useFallback": False,
    "fallbackFont": None,
    "language": getdefaultlocale()[0],
    "debugmode": False,
    "secsave": 10,
    "theme": 1,
    "beforeread": [],
    "disableplugin": []
}

setting: dict = {

}

if "--debug-mode" in args or "-db" in args:
    debugMode = True
    addLog(3, "Debug Mode Started 😍", "ArgumentParser")

if "--no-color" in args or "-nc" in args:
    colored = False
    from builtins import print
    addLog(3, "No color started 🤔", "ArgumentParser")

if "-h" in args or "--help" in args: # HelpActivity
    addLog(0, "Sinote Help is starting...", "HelpActivity")
    QMessageBox.information(None,"Help","-h/--help: Arguments Help of Sinote\n-su/--use-root-user: Bypass check for SU User in posix env\n--bypass-system-check: Bypass System Check (Windows, Linux, Mac OS)\n-db/--debug-mode: Use Debug Mode (I/O Performance will low)\n-ow/--only-warning: Only Warning/Error in LOG\n--no-color/-nc: No color when log output\n--only-create-cache: Only create plugin caches\n--no-theme/-nt: Use default style (Windows)")
    addLog(0, "Sinote Help closed, return to normal enviroment.", "HelpActivity")
    addLog(0, "Exiting...")
    sys.exit(0)

if not system().lower() in ["darwin", "linux", "windows"] and not "--bypass-system-check" in args:
    addLog(3, "Checked not a Darwin, Linux, NT Based, starting error.", "ArgumentParser")
    addLog(2,"Your system isn't a Darwin Based, a Linux Based or Windows, cannot continue run safety, use --bypass-system-check to bypass.")
    addLog(3, "Starting error window...", "ArgumentParser")
    err("0x00000003")
    sys.exit(1)

if system().lower() in ["darwin","linux"]:
    if getuser() == "root":
        addLog(3, "ROOT User detected.", "ArgumentParser")
        addLog(1,"We recommend to use Normal User in posix env. But use ROOT User is not SAFE for your OS! Please use Normal User Instead! (Excepted you have known it's unsafe or you wanna edit System File like GRUB)")
        addLog(3, "Starting warning window...", "ArgumentParser")
        if not ("--use-root-user" in args or "-su" in args):
            QMessageBox.warning(None, "Warning",
                                     "We have noticed you run Sinote by ROOT/SU User, please remove 'sudo' command or exit 'su' environment. \nOr you can append -su for argument to bypass.")

if "-ow" in args or "--only-warning" in args:
    addLog(3, "Only Warning Started 🤓", "ArgumentParser")
    onlyWarning = True
    addLog = owLog

for temp in basicInfo["item.list.language_files"]:
    if not Path("./resources/language/{}/{}.json".format(lang,temp)).exists():
        addLog(2,"Check Language files failed! ❌","FileConfigActivity")
        err("0x00000002")
        sys.exit(1)

# Automatic generate cache directory
Path("./cache").mkdir(exist_ok=True)

# Check the Beta Version
def checkVersionForPopup():
    if basicInfo["item.bool.isbetaversion"]:
        w = QMessageBox.warning(None,basicInfo["item.text.warn"],basicInfo["item.text.betaverdesc"])

alreadyLoaded: SafetyDict[str, dict] = {}   # Cache Language File (What is @lru_cache? I cannot be got it.)
alreadyLoadedBase: SafetyDict[str, dict] = {}    # Whoa en_US is my needed!


def getFileHash(filePath):
    try:
        with open(filePath, "rb") as f:
            return hashlib.md5(f.read()).hexdigest()
    except:
        return ""

def load(filePath):
    cachePath = Path("./cache") / f"{filePath.replace("/", "_").replace("\\", "_")}.cache"
    fileHash = getFileHash(filePath)

    if cachePath.exists():
        try:
            with open(cachePath, "rb") as f:
                cachedData = pickle.load(f)
                if debugMode:
                    addLog(3, f"File HASH: {cachedData["savedHash"]}", "JsonCacheLoadActivity")
                    addLog(3, f"Now File HASH: {fileHash}")
                if cachedData["savedHash"] == fileHash:
                    if debugMode: addLog(3, "File HASH is same as the file will be load! Cache hit! 💥", "JsonCacheLoadActivity")   # Hash is good!
                    return cachedData["ohMyData"]
        except:
            pass

    try:
        with open(filePath, "r", encoding="utf-8") as f:
            content = f.read()
        try:
            data = normalLoads(content)
        except JSONDecodeError:
            data = loads(content)

        cacheData = {
            'savedHash': fileHash,
            'ohMyData': data
        }

        try:
            with open(cachePath, "wb") as f:
                if debugMode: addLog(3, "Dumping and writing cache! 🤔",
                                     "JsonCacheLoadActivity")
                pickle.dump(cacheData, f)
        except Exception as e:
            addLog(1, f"Cannot write cache: {repr(e)}", "JsonCacheLoadActivity")

        return data
    except:
        return {}

def loadJson(jsonName: str):
    global alreadyLoaded
    
    if jsonName in alreadyLoaded.keys():
        if debugMode: addLog(3, f"{jsonName}.json Cache hit 💥", "FileConfigActivity")
        return alreadyLoaded[jsonName]

    if debugMode: addLog(3, f"Reading {jsonName}.json in en_US for support other text of not supported.")
    baseData = load(f"./resources/language/en_US/{jsonName}.json")
    if debugMode: addLog(3, f"Attempting to load {jsonName}.json and cache it ✅", "FileConfigActivity")
    langData = load(f"./resources/language/{lang}/{jsonName}.json")
    
    result = SafetyDict(baseData.copy() | langData.copy())
    
    alreadyLoaded[jsonName] = result   # Cache!
    return result

def oldLoadJson(jsonName: str):
    global alreadyLoaded
    if not Path("./resources/language/{}/{}.json".format(lang,jsonName)).exists():
        addLog(2, "Failed to load when load this Language File: {} ❌".format(jsonName), "FileConfigActivity")
        err("0x00000002")
        sys.exit(1)
    if jsonName in alreadyLoaded.keys():
        if debugMode: addLog(3, f"{jsonName}.json Cache hit 💥", "FileConfigActivity")
        return alreadyLoaded[jsonName]
    temp: dict = {}
    with open("./resources/language/en_US/{}.json".format(jsonName),"r",encoding="utf-8") as f:
        if debugMode: addLog(3, f"Reading {jsonName}.json in en_US for support other text of not supported.")
        temp = loads(f.read())  # Cache it
    with open("./resources/language/{}/{}.json".format(lang, jsonName),"r",encoding="utf-8") as f:
        if debugMode: addLog(3, f"Attempting to load {jsonName}.json and cache it ✅", "FileConfigActivity")
        alreadyLoaded[jsonName] = temp | loads(f.read())
        return alreadyLoaded[jsonName]  # Use cache for file read nullptr

def outputDeveloperDebugInformation():
    addLog(3, "For Developer Debug, Output your own PC's environment! 🤓", "OutputDeveloperDebugInformationActivity")
    addLog(3, f"Platform: {system()} Python: {python_version()} Win32 Version*: {" ".join(win32_ver())} | Linux LIBC Ver*: {" ".join(libc_ver())}", "OutputDeveloperDebugInformationActivity")
    addLog(3, "Note: If some error occurred, please send log to the developer 💥", "OutputDeveloperDebugInformationActivity")

def applyStylesheet(application: QApplication, theme: str) -> None:
    apply_stylesheet(application, theme, extra={"QMenu": {"height": 20, "padding": "5px 10px 7px 10px"}})


class Setting:
    def __init__(self):
        global setting
        # Automatic receive setting
        self.noFileAutoGenerate()
        # Automatic Lex setting file
        try:
            if debugMode:
                addLog(3, "Attempting to load setting.json5...", "SettingLexerActivity")
            with open("./setting.json5", "r", encoding="utf-8") as f:
                lexed: dict = normalSetting | loads(f.read())
            if not lexed.keys() is normalSetting.keys():
                with open("setting.json5", "w", encoding="utf-8") as f:
                    f.write(dumps(normalSetting | lexed, ensure_ascii=True))
            if not isinstance(lexed, dict):
                raise
            else:
                setting = lexed
                if debugMode:
                    addLog(3, "Successfully to load setting.json5!", "SettingLexerActivity")
        except Exception:
            addLog(2, "Cannot load setting.json5!", "SettingLexerActivity")
            self.noFileAutoGenerate(mustToGenerate=True)

    def setValue(self, key: str, value: str) -> None:
        global setting
        if key in normalSetting.keys():
            setting[key] = value
            if debugMode:
                addLog(3, f"Successfully to change {key} to {value}")
            self.saveToConfig()

    def saveToConfig(self) -> None:
        with open("./setting.json5", "w", encoding="utf-8") as f:
            f.write(dumps(setting, ensure_ascii=False))

    def getValue(self, key: str) -> Any | None:
        return setting.get(key, None)

    def noFileAutoGenerate(self, mustToGenerate: bool = False) -> None:
        global setting
        if debugMode:
            addLog(3, "Checking setting.json5 exists, if not exists, automatic generate instead." if not mustToGenerate else "Argument mustToGenerate is true, generating a new setting...")
        if not Path("./setting.json5").exists() or mustToGenerate:
            with open("./setting.json5", "w", encoding="utf-8") as f:
                f.write(dumps(normalSetting, ensure_ascii=False))
            if debugMode:
                addLog(3, "Successfully to generate a new setting!")
        setting = normalSetting


class SinoteErrors:
    class ItemNotValid(Exception): ...


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

    argumentNumber: dict = {
        # Base Functions
        0: [1, 1],
        1: [2, 2],
        2: [2, 2],
        3: [1, 2],
        4: [1, 1],
        5: [3, 3],
        6: [1, 2],
        7: [1, 1],
        # Advanced Functions
        100: [2, 2],
        101: [1, 1],
        102: [1, 1],
        103: [1, 1],
        104: [1, 1],
        105: [1, 1],
        106: [2, 2],
        107: [2, 2],
        108: [2, 2],
        # GUI Functions
        200: [1, 1]
    }

    class ConfigKeyNotFoundError(Exception): ...

    @staticmethod
    def parseErrCode(code: int) -> str:
        errCodeDefinitions: dict = {
            0: "Missing Ingredients",
            1: "API is too low or high",
            2: "Missing File",
            3: "Not a sure plugin",
            -1: "Unknown Error"
        }
        return errCodeDefinitions.get(code,"SIMPLY_ERROR")

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

            addLog(0, f"Syntax highlighter initialized with {len(self.keywords)} keywords, {len(self.symbols)} symbols 😍", "LoadPluginBaseActivity")

        def _setup_formats(self):
            self.keyword_format = QTextCharFormat()
            self.keyword_format.setForeground(QColor('#3DACFF'))
            self.keyword_format.setFontWeight(QFont.Weight.Bold)

            self.symbol_format = QTextCharFormat()
            self.symbol_format.setForeground(QColor('#717A2A'))

            self.single_comment_format = QTextCharFormat()
            self.single_comment_format.setForeground(QColor('#009400'))
            self.single_comment_format.setFontItalic(True)

            self.multi_comment_format = QTextCharFormat()
            self.multi_comment_format.setForeground(QColor('#009400'))
            self.multi_comment_format.setFontItalic(True)

            self.string_format = QTextCharFormat()
            self.string_format.setForeground(QColor('#2EFF00'))

        def _setup_highlighting_rules(self):
            self._add_keyword_rules()
            self._add_symbol_rules()
            self._add_single_comment_rules()
            self._add_string_rules()
            self._add_multi_comment_rules()

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
            if len(self.remKeywordsMultipleLine) >= 2:
                start_mark, end_mark = self.remKeywordsMultipleLine[0], self.remKeywordsMultipleLine[1]
                # 根据enableSelfColor决定使用哪种格式
                format_to_use = self.multi_comment_format if self.enableSelfColor else self.string_format
                
                # 只添加跨行模式，不添加单行规则
                self.multi_line_patterns.append({
                    'start': QRegularExpression(re.escape(start_mark)),
                    'end': QRegularExpression(re.escape(end_mark)),
                    'format': format_to_use
                })

        def _add_string_rules(self):
            for string_mark in self.textKeywords:
                pattern = QRegularExpression(
                    re.escape(string_mark) + r'([^"\\]|\\.)*?' + re.escape(string_mark)
                )
                self.highlight_rules.append((pattern, self.string_format))

        def highlightBlock(self, text: str):
            self.setCurrentBlockState(0)
            stringRanges = self._findStringRanges(text)
            for pattern, format in self.highlight_rules:
                matchIterator = pattern.globalMatch(text)
                while matchIterator.hasNext():
                    match = matchIterator.next()
                    startPos = match.capturedStart()
                    endPos = match.capturedStart() + match.capturedLength()
                    if format == self.single_comment_format:
                        if not self._isInString(startPos, stringRanges):
                            self.setFormat(startPos, match.capturedLength(), format)
                    elif format == self.multi_comment_format:
                        continue
                    else:
                        self.setFormat(startPos, match.capturedLength(), format)
            self.highlightMultiLineComments(text)
        
        def _findStringRanges(self, text: str) -> list:
            """
            Find String ranges
            :param text: text of string
            :return: a list
            """
            stringRanges = []
            i = 0
            n = len(text)
            
            while i < n:
                if text[i] in self.textKeywords:
                    quoteChar = text[i]
                    start = i
                    i += 1
                    while i < n:
                        if text[i] == "\\":
                            i += 2
                        elif text[i] == quoteChar:
                            i += 1
                            break
                        else:
                            i += 1
                    
                    stringRanges.append((start, i))
                else:
                    i += 1
            
            return stringRanges
        
        def _isInString(self, pos: int, stringRanges: list) -> bool:
            for start, end in stringRanges:
                if start <= pos < end:
                    return True
            return False

        def isInMultilineComment(self, start: int, end: int, text: str) -> bool:
            if not self.multi_line_patterns:
                return False
            for multiLine in self.multi_line_patterns:
                startIter = multiLine['start'].globalMatch(text)
                while startIter.hasNext():
                    startMatch = startIter.next()
                    s = startMatch.capturedStart()
                    endMatch = multiLine['end'].match(text, s + startMatch.capturedLength())
                    if endMatch.hasMatch():
                        e = endMatch.capturedEnd()
                    else:
                        if self.previousBlockState() == 1:
                            s = 0
                        e = len(text)
                    if s <= start and e >= end:
                        return True
            return False

        def highlightMultiLineComments(self, text: str):
            if not self.multi_line_patterns:
                return

            self.setCurrentBlockState(0)
            
            for multiLine in self.multi_line_patterns:
                startIndex = 0
                if self.previousBlockState() == 1:
                    endMatch = multiLine['end'].match(text, startIndex)
                    if endMatch.hasMatch():
                        endIndex = endMatch.capturedEnd()
                        self.setFormat(0, endIndex, multiLine['format'])
                        startIndex = endIndex
                        self.setCurrentBlockState(0)
                    else:
                        self.setFormat(0, len(text), multiLine['format'])
                        self.setCurrentBlockState(1)
                        return
                while startIndex < len(text):
                    startMatch = multiLine['start'].match(text, startIndex)
                    if not startMatch.hasMatch():
                        break
                    
                    startIdx = startMatch.capturedStart()
                    endMatch = multiLine['end'].match(text, startIdx + startMatch.capturedLength())
                    if endMatch.hasMatch():
                        endIdx = endMatch.capturedEnd()
                        self.setFormat(startIdx, endIdx - startIdx, multiLine['format'])
                        startIndex = endIdx
                    else:
                        self.setFormat(startIdx, len(text) - startIdx, multiLine['format'])
                        self.setCurrentBlockState(1)
                        return

    class LazyCustomizeSyntaxHighlighter:
        def __init__(self, syntaxList: list, parent: QTextDocument = None):
            self._syntaxList: list = syntaxList
            self._parent: QTextDocument | None = parent

        def setParent(self, parent: QTextDocument) -> None:
            self._parent = parent

        def getObject(self) -> QSyntaxHighlighter:
            return LoadPluginBase.CustomizeSyntaxHighlighter(self._syntaxList, self._parent)

    @staticmethod
    def logIfDebug(logText: str) -> None:
        """
        Log out if Debug Mode starts.
        :param logText: text will log out.
        :return: None
        """
        if debugMode:
            addLog(3, logText, "LoadPluginActivity")


"""
Seperator for LoadPluginBase and ParseFunctions
"""

class Variables:
    def __init__(self, variableDict: dict = None):
        LoadPluginBase.logIfDebug(f"Variables has initializing, the variableDict argument: {"null" if variableDict is None else variableDict} 🥳")
        self._variableDict: dict = variableDict if variableDict else {}
        self._variableMatchPattern = re.compile(r"%var:([^%]+)%")
        LoadPluginBase.logIfDebug("Successfully to initialize Variables object ✅ (OwO)")

    def addVar(self, varName: str, varContent: str = "NULL"):
        """
        Add or Edit Variable
        :param varName: Variable Name
        :param varContent: Variable Content
        :return: None
        """
        LoadPluginBase.logIfDebug(f"Set/Added Variable \"{varName}\" and edit it to \"{varContent}\" ✅ (UwU)")
        self._variableDict[varName] = varContent

    def getVar(self, varName: str) -> str:
        """
        Get the Variable Content
        :param varName: Variable Name
        :return: String
        """
        LoadPluginBase.logIfDebug("少女祈祷中...（不要出|XXX NOT FOUND|）")
        if not varName in self._variableDict.keys():
            LoadPluginBase.logIfDebug(f"Cannot get variable {varName} (TwT)")
            return f"|{varName} NOT FOUND|"
        LoadPluginBase.logIfDebug(f"Successfully to get variable {varName} ✅ (OwO)")
        LoadPluginBase.logIfDebug(f"Variable Content: {self._variableDict[varName]} (-W-)")
        return self._variableDict[varName]

    def removeVar(self, varName: str) -> bool:
        """
        Remove a Variable
        :param varName: Variable Name
        :return: Boolean, False for it was removed, True for Removed
        """
        LoadPluginBase.logIfDebug(f"Successfully to remove variable {varName} ✅ (O_I)")
        if not varName in self._variableDict.keys():
            return False
        self._variableDict.pop(varName)
        return True

    def copyDict(self) -> dict:
        """
        By the way, an easy method.
        Dict.copy()
        :return: Dictionary
        """
        return self._variableDict

    def resolveVarInString(self, string: str) -> str:
        """
        Use Regular Expression to Match in String
        :param string: String
        :return: The new string
        """
        def temporaryReplaceMatch(match):
            LoadPluginBase.logIfDebug(f"Regular Expression Matching: GROUP = {match.group()} -> VAR: {match.group(1)} (UwU)")
            temporary = self.getVar(match.group(1))
            LoadPluginBase.logIfDebug(f"Regular Expression Replaced: {temporary} ✅")
            return temporary

        value = self._variableMatchPattern.sub(temporaryReplaceMatch, string)
        LoadPluginBase.logIfDebug(f"Regular Expression Final Answer: {value} 💥(IwI)")
        return value


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
        self._pressedKeys: set[int] = set()

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if debugMode: addLog(3, f"Key pressed: {event.key()}", "ShortcutActivity")
        if not event.isAutoRepeat() and event.key() not in self._pressedKeys:
            self._pressedKeys.add(event.key())

        if self._pressedKeys in self._shortcutList.values():  # It will be slow when shortcut pressed, but it will be dash! when shortcut not pressed. O(n)
            for itemNumber, key in self._shortcutList.items():
                if key == self._pressedKeys:
                    self.shortcutHandled.emit(itemNumber)
                    break

    def keyReleaseEvent(self, event: QKeyEvent) -> None:
        if debugMode: addLog(3, f"Key released: {event.key()}", "ShortcutActivity")
        if not event.isAutoRepeat() and event.key() in self._pressedKeys:
            self._pressedKeys.discard(event.key())

    def addItem(self, keys: list[Qt.Key], itemNumber: int) -> None:
        if itemNumber not in self._shortcutList:
            self._shortcutList[itemNumber] = set([i.value for i in keys if hasattr(i, "value")])
            return
        raise SinoteErrors.ItemNotValid(f"{itemNumber} has probably in the shortcut list.")

    def discardItem(self, itemNumber: int) -> None:
        self._shortcutList.pop(itemNumber)


class FunctionLexerSet:
    def __init__(self, listOfFunc: list[str | int | dict | dict], translateVariables: bool = True):
        self._listOfFunc = listOfFunc
        self._varObj = Variables()
        self._needVar = translateVariables
        self._if = {
            0: self.print,
            1: self.messageBox,
            2: self.log,
            3: self.addVar,
            4: self.printContentOfVariable,
            5: self.messageInput,
            6: self.system,
            7: self.usefunc
        }
        # self._insideFunction = self._if
        # You can remove # head if you want to use self._insideFunction

    def usefunc(self, funcname: str) -> None:
        addLog(1, "UseFunc Command is not support this version (Wait for 1.0.3)", "FunctionLexerActivity")

    def system(self, command: str) -> None:
        addLog(1, "System Command is not support this version (Wait for 1.0.3)", "FunctionLexerActivity")

    def addVar(self, varName: str, varContent: str) -> None:
        self._varObj.addVar(varName, varContent)

    def messageInput(self, title: str, content: str, varname: str) -> None:
        FunctionLexerSet.debugLog("Preparing to Message Input for a Variable")
        temp, ok = QInputDialog.getText(None, title, content)
        if ok:
            FunctionLexerSet.debugLog("Successfully received input text from InputDialog, content: {}".format(temp))
            self._varObj.addVar(varname, temp)
        else:
            FunctionLexerSet.debugLog("Failed to receive input text from InputDialog, default's only create and set its content to NULL.")
            self._varObj.addVar(varname)

    def lexVariable(self, string: str) -> str:
        return self._varObj.resolveVarInString(string) if self._needVar else string

    def printContentOfVariable(self, variableName: str) -> None:
        FunctionLexerSet.debugLog("Preparing to Print Content")
        print(self._varObj.getVar(variableName))
        FunctionLexerSet.debugLog("Successfully to Print Content")

    def messageBox(self, title: str, content: str) -> None:
        FunctionLexerSet.debugLog("Preparing to Set a Message Box")
        temp = QMessageBox(QMessageBox.Icon.NoIcon, self.lexVariable(title), self.lexVariable(content), QMessageBox.StandardButton.Close)
        temp.exec()
        FunctionLexerSet.debugLog("Successfully to Set a Message Box")

    def print(self, outText: str) -> None:
        FunctionLexerSet.debugLog("Preparing to Print out Customize Text")
        print(self.lexVariable(outText))
        FunctionLexerSet.debugLog("Successfully to Print out Customize Text")

    @staticmethod
    def debugLog(outText: str) -> None:
        if debugMode:
            addLog(3, outText, "FunctionLexerActivity")

    def log(self, level: int, outText: str) -> None:
        FunctionLexerSet.debugLog("Preparing to log out...")
        if level not in (0, 1):
            addLog(2, "Illegal Log Level: {}".format(level), "FunctionLexerActivity")
            return
        addLog(level, self.lexVariable(outText), "FunctionRunnerActivity")
        FunctionLexerSet.debugLog(f"Logged Out Customize Text, LEVEL: {level}.")

    def getValue(self) -> list[partial]:
        """
        Get value
        :return: None
        """
        returnlist: list[partial] = []
        for i in self._listOfFunc:
            if i[0] not in self._if.keys():
                addLog(2, f"Not compatible with this command! Number: {i[0]}", "FunctionLexerActivity")
                continue
            LoadPluginBase.logIfDebug(f"Number: {i[0]}, Function: {self._if[i[0]]}")
            if i[0] == 0:
                returnlist.append(partial(self._if[i[0]], i[1]))
            elif i[0] == 2:
                returnlist.append(partial(self._if[i[0]], i[1], i[2]))
            elif i[0] == 3:
                returnlist.append(partial(self._if[i[0]], i[1], "NULL" if len(i) == 2 else i[2]))
            elif i[0] == 4:
                returnlist.append(partial(self._if[i[0]], i[1]))
            elif i[0] == 5:
                returnlist.append(partial(self._if[i[0]], i[1], i[2], i[3]))
            elif i[0] == 6:
                returnlist.append(partial(self._if[i[0]], i[1]))
            elif i[0] == 7:
                returnlist.append(partial(self._if[i[0]], i[1]))
        return returnlist


class ParseFunctions:
    def __init__(self, list_: dict, customizeVar: bool = True):
        self._list: dict = list_
        self._customizeVar = customizeVar

    def getValue(self) -> list | None:
        """
        Get list[partial]
        :return: list[partial] or None
        """
        verifiedlist: list = []
        LoadPluginBase.logIfDebug(f"Get funcs: {self._list}")
        for funcName, funcContent in self._list.items():
            LoadPluginBase.logIfDebug(f"Checking function {funcName}...")
            for line, temp in enumerate(funcContent, 1):
                LoadPluginBase.logIfDebug(f"Checking line {line}... (OwO)")
                if len(temp) == 0:
                    LoadPluginBase.logIfDebug(f"Error In Line {line}: No any functions")
                    continue
                if temp[0] not in LoadPluginBase.functions.keys():
                    LoadPluginBase.logIfDebug(f"Error In Line {line}: Function {temp[0]} is not defined!")
                    continue
                if temp[0] == 7:
                    addLog(1, f"USEFUNC Function will be define in API 1.0.3, now API Version is {".".join(apiVersion)}")
                    continue
                after: list = temp
                after[0] = LoadPluginBase.functions[temp[0]]
                verifiedlist.append(temp)
                LoadPluginBase.logIfDebug(f"Successfully to Check line {line}! No problem! (UwU) I'm proud!")
            LoadPluginBase.logIfDebug(f"Already checked function {funcName}!")

        LoadPluginBase.logIfDebug(f"Successfully to Check all the Function List, Total: {len(self._list)} Passed: {len(verifiedlist)} Skipped: {len(self._list)-len(verifiedlist)}")

        try:
            temp = FunctionLexerSet(verifiedlist).getValue()
            LoadPluginBase.logIfDebug(f"Successfully to lex! Value: {temp}")
            return temp
        except Exception as e:
            addLog(2, f"Failed to parse! Reason: {repr(e)}")
            return None


class LoadPluginHeader:
    """
    config needed
    Key: type | Header Type, for look please go to ./documentation/pluginEdit/header.md
    """
    def __init__(self, header: AnyStr | dict, filename: AnyStr = None):
        self.filename = filename
        self.header = header if isinstance(header, dict) else loads(header) if filename else self.readFile(header)

    def setFilename(self, filename: AnyStr):
        self.filename = filename

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
            addLog(0,f"Attempting to load {self.filename} 🔎")
            self.config = {
                "type": 0,
                "api": [1,apiVersion[0]],
                "enableCustomizeCommandRun": False,
                "useSinoteVariableInString": True
            }
            if not self.header.get("config",None):
                self.err("Key \"config\" not found! ❌")
                return 0
            config = self.config | self.header["config"]
            if "objectName" not in config:
                self.err("\"objectName\" is a required item in config ❌")
                return 0
            if not (config["api"][0] <= apiVersion[0] <= config["api"][1]):
                self.err("This plugin not support API of this version! Please update to new version.")
                return 1
            # Add objectName to the list
            items.append(config["objectName"])
            items.append(config.get("type", 0) if isinstance(self.header["config"].get("type", 0), int) else 0)
            if items[1] == 0:
                # Check functions and runFunc
                functions: dict | None = self.header.get("functions", None)
                runFunc: list | None = self.header.get("runFunc",None)
                if not functions or not runFunc or config["enableCustomizeCommandRun"] == False:
                    addLog(1, f"File \"{self.filename}\" is a Placeholder File ('Cause no function and runFunc, or \"enableCustomizeCommandRun\" not enabled)")
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
                            k[0] = k[0].lower()
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
                coding: dict | None = self.header.get("coding",None)
                if coding is None:
                    self.err("Key \"coding\" not found 🤓")
                    return 0    # Missing Ingredients
                if not isinstance(coding,dict):
                    self.err("\"coding\" need a dict type ❌")
                    return 0    # Missing Ingredients
                self.coding = {
                    "codeName": "Not defined",
                    "fileExtension": [],
                    "keywords": [],
                    "symbols": [],
                    "remKeywords": [],
                    "remKeywordsMultipleLine": [],
                    "enableSelfColorOfRemKeywordsMultipleLine": True,
                    "textKeywords": [],
                    "defineKeywords": ["{","}"],
                    "pairKeywords": []
                }
                coding: dict = self.coding | coding
                items.append(coding["codeName"])
                items.append(coding["fileExtension"])
                items.append(LoadPluginBase.LazyCustomizeSyntaxHighlighter(
                    [
                        coding["keywords"],
                        coding["symbols"],
                        coding["remKeywords"],
                        coding["remKeywordsMultipleLine"],
                        coding["enableSelfColorOfRemKeywordsMultipleLine"],
                        coding["textKeywords"]
                    ]
                ))
                items.append(coding["defineKeywords"])
                items.append(coding["pairKeywords"])
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
    def readFile(filePath: str):
        """
        Read a file and return dict.
        :param filePath: File Path
        :return: A dict object.
        """
        return load(filePath)

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
            addLog(3, "Attempting to load imports.txt, content: {} 🔎".format(importText.replace("\n","\\n")), "LexImportsActivity")
            for temp in importText.split("\n"):
                addLog(3, f"Attempting to lex content: {temp.strip()} 🔎", "LexImportsActivity")
                if temp.strip() is None:
                    addLog(3, "Failed to load content because this content is NULL! ❌", "LexImportsActivity")
                elif temp.strip().startswith("//"):
                    addLog(3, "Automatic skip note 💥", "LexImportsActivity")
                else:
                    lexedList.append(temp.strip().replace("&space;"," "))
                    addLog(3, "Successfully to lex content ✅", "LexImportsActivity")
            addLog(3, "Lex successfully, program will be import these files: {} 🥳".format(", ".join(lexedList)), "LexImportsActivity")
        else:
            for temp in importText.split("\n"):
                if not (temp.strip() is None or temp.strip().startswith("//")):
                    lexedList.append(temp.strip().replace("&space;"," "))
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
            addLog(bodyText=f"Attempting to load plugin \"{self.projName}\" 🔎")
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
            addLog(bodyText="Attempting to read info.json 🔎")
            info: dict = load(f"./resources/plugins/{self.infoPath}")
            if info.get("versionIterate", None) is None:
                addLog(1, bodyText="\"versionIterate\" not found! This will be replace to 99900 (Maximum) 😰")
            addLog(bodyText="Successfully to read info.json ✅")
            addLog(bodyText="Attempting to merge info.json 🔎")
            information: dict = self.info | info
            information["icon"] = None if not isinstance(information["icon"], str) else information["icon"].lower().replace("%pluginpath%", f"./resources/plugins/{self.projName}")
            addLog(bodyText="Successfully to merge info.json ✅")
            if information["versionIterate"] > 99900:
                information["versionIterate"] = 99900
                addLog(1, "Number of \"versionIterate\" was more than 99900! \"versionIterate\" adjusted to 99900! 💥")
            imports: list | None = None
            if not errLite:
                addLog(bodyText="Attempting to read imports.txt ✅")
                with open(f"./resources/plugins/{self.projName}/imports.txt","r",encoding="utf-8") as f:
                    imports: list | None = self.lexImports(f.read())
                if imports is not None:
                    addLog(bodyText="Load successfully! ✅")
                else:
                    errLite = True
                    addLog(bodyText="Cannot load imports.txt, plugin will continue load but it's not USEFUL. 😰")
            items: list = []
            items.append(information)
            tmp: list = []
            objectName: str = ""
            if not errLite:
                for temp in imports:
                    # For safe
                    LoadPluginBase.logIfDebug(f"Trying to load header file in ./resources/plugins/{self.headerPlacePath}/{temp} 🪲")
                    temp2 = LoadPluginHeader(f"./resources/plugins/{self.headerPlacePath}/{temp}")
                    temp2.setFilename(temp)
                    temp3 = temp2.getValue()
                    LoadPluginBase.logIfDebug(f"Loaded Plugin Header! JSON: {temp2} 🤓")
                    if not isinstance(temp3, list):
                        if temp2 is None:
                            addLog(1, f"Skipped file {temp} because it's a Placeholder File ❌")
                        elif isinstance(temp3, int):
                            addLog(2,f"Illegal error, returns: {LoadPluginBase.parseErrCode(temp3)} 😰")
                    else:
                        objectName = f"{information["objectName"]}.{"syntax" if temp3[1] == 1 else "functions" if temp3[1] == 0 else "null"}.{temp3[0]}"
                        LoadPluginBase.logIfDebug(f"Loading {objectName}... 😍")
                        if temp3[1] == 0:
                            LoadPluginBase.logIfDebug(f"Starting lex that object name is {temp3[0]}. 🔎")
                            returned = self._functionLexer(temp3[2])
                            if len(returned) > 0:
                                tmp.append([objectName,0,returned])
                                LoadPluginBase.logIfDebug("Successfully to lex! ✅")
                            else:
                                tmp.append([objectName,0,None])
                                LoadPluginBase.logIfDebug("Failed to lex, automatic switch to None ❌")
                        elif temp3[1] == 1:
                            LoadPluginBase.logIfDebug("Appending QSyntaxHighlighter and Informations... 🔎")
                            tmp.append([objectName,1,temp3[2],temp3[3], temp3[4], temp3[5], temp3[6]])
                            LoadPluginBase.logIfDebug("Successfully to append! ✅")
                # Convert normal value to [<TYPE>,<OBJNAME>,<CONTENT>]
                items.append(tmp)
            else:
                listOfHeaders = None
                items.append(None)
            addLog(0,
                   f"Successfully to load {information["objectName"]}! Used {(datetime.now() - beforeDatetime).total_seconds()}secs. ✅")
            return items
        except Exception as e:
            self.err("Unknown Error, Python Exception: {}"
                                    .format(repr(e)))
            return -1

    @staticmethod
    def _functionLexer(func: list):
        """
        Lex function to functools.partial method
        Private Function
        :param func: Functions
        :return: Will run in Python
        """
        return ParseFunctions(func).getValue()

    def err(self, error: str):
        addLog(2, f"Cannot load plugin that directory name is \"{self.projName}\"")
        addLog(2, f"Reason: {error}")

settingObject = Setting()
if settingObject.getValue("debugmode"):
    if debugMode:
        addLog(0, "Don't open debug mode twice! (ADVICE)", "SettingLexerActivity")
    debugMode = True
    addLog(3, "Debug mode opened from setting.json5!", "SettingLexerActivity")
lang = settingObject.getValue("language") if Path(f"./resources/language/{settingObject.getValue("language")}").exists() else "en_US"
basicInfo = basicInfo | loadJson("BaseInfo")

addLog(bodyText=f"Import Modules Finish! Used {(datetime.now() - beforeDatetime).total_seconds()}secs")
addLog(bodyText=r"   _____ _             __          ______    ___ __            ")
addLog(bodyText=r"  / ___/(_)___  ____  / /____     / ____/___/ (_) /_____  _____")
addLog(bodyText=r"  \__ \/ / __ \/ __ \/ __/ _ \   / __/ / __  / / __/ __ \/ ___/")
addLog(bodyText=r" ___/ / / / / / /_/ / /_/  __/  / /___/ /_/ / / /_/ /_/ / /    ")
addLog(bodyText=r"/____/_/_/ /_/\____/\__/\___/  /_____/\__,_/_/\__/\____/_/     ")
addLog(bodyText=f"Sinote Editor {sinoteVersion}, API Version: {".".join([f"{i}" for i in apiVersion])}")

interruptSignal()