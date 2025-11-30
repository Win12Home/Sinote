from datetime import datetime


# Set beforeDatetime for catalog
beforeDatetime = datetime.now()

from subprocess import Popen
from json import dumps
from PySide6.QtWidgets import *
from functools import partial
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
import sys, re

filterwarnings("ignore", category=DeprecationWarning)

# Generate QApplication

application = QApplication([])

apply_stylesheet(application,"dark_blue.xml")

apiVersion: tuple = (1,0,1)
sinoteVersion: str = "sinote-2025.01.00842-initial-preview-beta"

normalLogOutput: list[str] = []

onlyWarning: bool = False

def addLog(type: int=0, bodyText: str="N/A", activity: str | None = None):
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
    normalLogOutput.append(f"[{nowTime}] [{logSender}] [{typeOfLog}] {bodyText}")
    if onlyWarning and typeOfLog not in ["WARN", "ERR"]:
        return
    print(f"[[blue]{nowTime}[/blue]] [{logSender}] [[{colorOfType[typeOfLog]}]{typeOfLog}[/{colorOfType[typeOfLog]}]] {bodyText}")


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
    addLog(2,"BaseInfo.json not found", "FileConfigActivity")
    err("0x00000001")
    quit(1)

# Check Arguments

# Look at the system
args = [i.lower() for i in sys.argv]

if "--debug-mode" in args or "-db" in args:
    debugMode = True
    addLog(3, "Debug Mode Started...", "ArgumentParser")

if "-h" in args or "--help" in args: # HelpActivity
    addLog(0, "Sinote Help is starting...", "HelpActivity")
    QMessageBox.information(None,"Help","-h/--help: Arguments Help of Sinote\n-su/--use-root-user: Bypass check for SU User in posix env\n--bypass-system-check: Bypass System Check (Windows, Linux, Mac OS)\n-db/--debug-mode: Use Debug Mode (I/O Performance will low)\n-ow/--only-warning: Only Warning/Error in LOG")
    addLog(0, "Sinote Help closed, return to normal enviroment.", "HelpActivity")
    addLog(0, "Exiting...")
    sys.exit(0)

if not system().lower() in ["darwin", "linux", "windows"] and not "--bypass-system-check" in args:
    addLog(3, "Checked not a Darwin, Linux, NT Based, starting error.", "ArgumentParser")
    addLog(2,"Your system isn't a Darwin Based, a Linux Based or Windows, cannot continue run safety, use --bypass-system-check to bypass.")
    addLog(3, "Starting error window...", "ArgumentParser")
    err("0x00000003")
    quit(1)

if system().lower() in ["darwin","linux"]:
    if getuser() == "root":
        addLog(3, "ROOT User detected.", "ArgumentParser")
        addLog(1,"We recommend to use Normal User in posix env. But use ROOT User is not SAFE for your OS! Please use Normal User Instead! (Excepted you have known it's unsafe or you wanna edit System File like GRUB)")
        addLog(3, "Starting warning window...", "ArgumentParser")
        if not ("--use-root-user" in args or "-su" in args):
            QMessageBox.warning(None, "Warning",
                                     "We have noticed you run Sinote by ROOT/SU User, please remove 'sudo' command or exit 'su' environment. \nOr you can append -su for argument to bypass.")

if "-ow" in args or "--only-warning" in args:
    addLog(3, "Only Warning Started.", "ArgumentParser")
    onlyWarning = True

for temp in basicInfo["item.list.language_files"]:
    if not Path("./resources/language/{}/{}.json".format(lang,temp)).exists():
        addLog(2,"Check Language files failed!","FileConfigActivity")
        err("0x00000002")
        quit(1)


# Check the Beta Version
def checkVersionForPopup():
    if basicInfo["item.bool.isbetaversion"]:
        w = QMessageBox.warning(None,basicInfo["item.text.warn"],basicInfo["item.text.betaverdesc"])

def loadJson(json_name: str):
    if not Path("./resources/language/{}/{}.json".format(lang,json_name)).exists():
        addLog(2, "Failed to load when load this Language File: {}".format(json_name), "FileConfigActivity")
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
        LoadPluginBase.logIfDebug(f"Variables has initializing, the variableDict argument: {"null" if variableDict is None else variableDict}")
        self._variableDict: dict = variableDict if variableDict else {}
        self._variableMatchPattern = re.compile(r"%var:([^%]+)%")
        LoadPluginBase.logIfDebug("Successfully to initialize Variables object. (OwO)")

    def addVar(self, varName: str, varContent: str = "NULL"):
        """
        Add or Edit Variable
        :param varName: Variable Name
        :param varContent: Variable Content
        :return: None
        """
        LoadPluginBase.logIfDebug(f"Set/Added Variable \"{varName}\" and edit it to \"{varContent}\" (UwU)")
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
        LoadPluginBase.logIfDebug(f"Successfully to get variable {varName} (OwO)")
        LoadPluginBase.logIfDebug(f"Variable Content: {self._variableDict[varName]} (-W-)")
        return self._variableDict[varName]

    def removeVar(self, varName: str) -> bool:
        """
        Remove a Variable
        :param varName: Variable Name
        :return: Boolean, False for it was removed, True for Removed
        """
        LoadPluginBase.logIfDebug(f"Successfully to remove variable {varName} (O_I)")
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
            LoadPluginBase.logIfDebug(f"Regular Expression Replaced: {temporary}")
            return temporary

        value = self._variableMatchPattern.sub(temporaryReplaceMatch, string)
        LoadPluginBase.logIfDebug(f"Regular Expression Final Answer: {value} (IwI)")
        return value


class FunctionLexerSet:
    def __init__(self, listOfFunc: list[str | int | dict], translateVariables: bool = True):
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
            if not i[0] in self._if.keys():
                addLog(2, "Not compatible with this command!", "FunctionLexerActivity")
                continue
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
    def __init__(self, list_: list, customizeVar: bool = True):
        self._list: list = list_
        self._customizeVar = customizeVar

    def getValue(self) -> list | None:
        """
        Get list[partial]
        :return: list[partial] or None
        """
        verifiedlist: list = []
        for line, temp in enumerate(self._list, 1):
            LoadPluginBase.logIfDebug(f"Checking line {line}... (OwO)")
            if temp[0] not in LoadPluginBase.functions.keys():
                LoadPluginBase.logIfDebug(f"Error In Line {line}: Functions is not defined!")
                continue
            if temp[0] == 7:
                addLog(1, f"USEFUNC Function will be define in API 1.0.3, now API Version is {".".join(apiVersion)}")
                continue
            verifiedlist.append(temp)
            LoadPluginBase.logIfDebug(f"Successfully to Check line {line}! No problem! (UwU) I'm proud!")

        LoadPluginBase.logIfDebug(f"Successfully to Check all the Function List, Total: {len(self._list)} Passed: {len(verifiedlist)} Skipped: {len(self._list)-len(verifiedlist)}")

        try:
            temp = FunctionLexerSet(verifiedlist).getValue()
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
                coding: dict | None = self.header.get("coding",None)
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
            addLog(3, "Attempting to load imports.txt, content: {}".format(importText.replace("\n","\\n")), "LexImportsActivity")
            for temp in importText.split("\n"):
                addLog(3, f"Attempting to lex content: {temp.strip()}", "LexImportsActivity")
                if temp.strip() is None:
                    addLog(3, "Failed to load content because this content is NULL!", "LexImportsActivity")
                elif temp.strip().startswith("//"):
                    addLog(3, "Automatic skip note", "LexImportsActivity")
                else:
                    lexedList.append(temp.strip().replace("&space;"," "))
                    addLog(3, "Successfully to lex content.", "LexImportsActivity")
            addLog(3, "Lex successfully, program will be import these files: {}".format(", ".join(lexedList)), "LexImportsActivity")
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
            info: dict = LoadPluginHeader.readFile(f"./resources/plugins/{self.infoPath}")
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
                with open(f"./resources/plugins/{self.projName}/imports.txt","r",encoding="utf-8") as f:
                    imports: list | None = self.lexImports(f.read())
                if imports is not None:
                    addLog(bodyText="Load successfully!")
                else:
                    errLite = True
                    addLog(bodyText="Cannot load imports.txt, plugin will continue load but it's not USEFUL.")
            items: list = []
            items.append(information)
            tmp: list = []
            objectName: str = ""
            if not errLite:
                for temp in imports:
                    # For safe
                    LoadPluginBase.logIfDebug(f"Trying to load header file in ./resources/plugins/{self.headerPlacePath}/{temp}")
                    temp2 = LoadPluginHeader(f"./resources/plugins/{self.headerPlacePath}/{temp}")
                    temp2.setFilename(temp)
                    temp3 = temp2.getValue()
                    LoadPluginBase.logIfDebug(f"Loaded Plugin Header! JSON: {temp2}")
                    if not isinstance(temp3, list):
                        if temp2 is None:
                            addLog(1, f"Skipped file {temp} because it's a Placeholder File")
                        elif isinstance(temp3, int):
                            addLog(2,f"Illegal error, returns: {LoadPluginBase.parseErrCode(temp3)}")
                    else:
                        objectName = f"{information["objectName"]}.{"syntax" if temp3[1] == 1 else "functions" if temp3[1] == 0 else "null"}.{temp3[0]}"
                        LoadPluginBase.logIfDebug(f"Loading {objectName}...")
                        if temp3[1] == 0:
                            LoadPluginBase.logIfDebug(f"Starting lex that object name is {temp3[0]}.")
                            returned = self._functionLexer(temp3[2])
                            if len(returned.keys()) > 0:
                                tmp.append([objectName,0,returned])
                                LoadPluginBase.logIfDebug("Successfully to lex!")
                            else:
                                tmp.append([objectName,0,None])
                                LoadPluginBase.logIfDebug("Failed to lex, automatic switch to None.")
                        elif temp3[1] == 1:
                            LoadPluginBase.logIfDebug("Appending QSyntaxHighlighter and Informations...")
                            tmp.append([objectName,1,temp3[2],temp3[3],temp3[4]])
                            LoadPluginBase.logIfDebug("Successfully to append!")
                # Convert normal value to [<TYPE>,<OBJNAME>,<CONTENT>]
                items.append(tmp)
            else:
                listOfHeaders = None
                items.append(None)
            addLog(0,
                   f"Successfully to load {information["objectName"]}! Used {(datetime.now() - beforeDatetime).total_seconds()}secs.")
            return items
        except Exception as e:
            self.err("Unknown Error, Python Exception: {}"
                                    .format(repr(e)))
            return -1

    @staticmethod
    def _functionLexer(func: dict):
        """
        Lex function to functools.partial method
        Private Function
        :param func: Functions
        :return: Will run in Python
        Not completed
        """
        return func

    def err(self, error: str):
        addLog(2, f"Cannot load plugin that directory name is \"{self.projName}\"")
        addLog(2, f"Reason: {error}")


addLog(bodyText=f"Import Modules Finish! Used {(datetime.now() - beforeDatetime).total_seconds()}secs")
addLog(bodyText=r"   _____ _             __          ______    ___ __            ")
addLog(bodyText=r"  / ___/(_)___  ____  / /____     / ____/___/ (_) /_____  _____")
addLog(bodyText=r"  \__ \/ / __ \/ __ \/ __/ _ \   / __/ / __  / / __/ __ \/ ___/")
addLog(bodyText=r" ___/ / / / / / /_/ / /_/  __/  / /___/ /_/ / / /_/ /_/ / /    ")
addLog(bodyText=r"/____/_/_/ /_/\____/\__/\___/  /_____/\__,_/_/\__/\____/_/     ")
addLog(bodyText=f"Sinote Editor {sinoteVersion}, API Version: {".".join([f"{i}" for i in apiVersion])}")