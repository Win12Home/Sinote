from PySide6.QtWidgets import *
from functools import singledispatch
from PySide6.QtCore import *
from PySide6.QtGui import *
from qt_material import *
from json import loads
from rich import print
from locale import getdefaultlocale
from warnings import *
from pathlib import Path
from platform import system, python_version, win32_ver, processor, libc_ver
from datetime import datetime
from traceback import format_exception
from typing import *
from psutil import virtual_memory, cpu_percent
import re,json,sys

filterwarnings("ignore", category=DeprecationWarning)

# Generate QApplication

application = QApplication([])

apply_stylesheet(application,"light_teal.xml")

apiVersion: tuple = (1,0,1)
sinoteVersion: str = "sinote-2025.01.00842-initial-preview-beta"

normalLogOutput: list[str] = []

def addLog(type: int=0, bodyText:str="N/A"):
    typeOfLog: str = ("INFO" if (type == 0) else "WARN" if (type == 1) else "ERR" if (type == 2) else "N/A")
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
    Please feedback to Developer yet!
    
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

if not system().lower() in ["darwin", "linux", "windows"] and not "--bypass-system-check" in args:
    addLog(2,"Your system isn't a Darwin Based, a Linux Based or Windows, cannot continue run safety, use --bypass-system-check to bypass.")
    err("0x00000003")
    quit(1)
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
    addLog(0, "For Developer Debug, Output your own PC's enviroment!")
    addLog(0, f"Platform: {system()} Python: {python_version()} Win32 Version*: {" ".join(win32_ver())} | Linux LIBC Ver*: {" ".join(libc_ver())}")
    addLog(0, "Note: If some error occurred, please send log to the developer")


class LoadPluginBase:
    class ConfigKeyNotFoundError(Exception): ...

    @staticmethod
    def parseErrCode(code: int):
        errCodeDefinitions: dict = {
            0: "Missing Ingredients",
            1: "API is too low or high"
        }
        return code

class LoadPluginHeader:
    """
    config needed
    Key: type | Header Type, for look please go to ./documentation/pluginEdit/header.md
    """
    def __init__(self, header: AnyStr | Dict, filename: AnyStr):
        self.filename = filename
        self.header = header if isinstance(header, dict) else self.readFile(header)

    def err(self, error: str):
        addLog(2, f"Error while loading file \"{self.filename}\": {error}")
        addLog(2,f"Cannot continue load plugin!")

    def getValue(self) -> int | list:
        """
        Load plugin and return a format like this:
        [<objName>,<type>,{<settings>}]
        :return: Integer (follow LoadPluginBase.parseErrCode) List (plugin)
        """
        self.config = {
            "type": 0,
            "api": [1,apiVersion[0]],
            "enableCustomizeCommandRun": False,
            "useSinoteVariableInString": True
        }
        flag: bool = False
        items: list = []
        for k in (items := [k for k,_ in self.header.items()]):
            if k == "config":
                flag = True
        if not flag:
            self.err("Key \"config\" not found!")
            return 0
        if "objectName" not in self.header["config"]:
            self.err("\"objectName\" is a required item in config.")
            return 0
        if "api" in self.header["config"]:
            if not apiVersion[0] in range(self.header["config"]["api"][0],self.header["config"]["api"][1],1):
                self.err("This plugin isn't support this version of API! Please update to new version!")
                return 1


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
        return json.loads(readStr)

raise Exception("A Exception")