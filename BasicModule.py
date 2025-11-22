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
import sys

filterwarnings("ignore", category=DeprecationWarning)

# Generate QApplication

application = QApplication([])

apply_stylesheet(application,"dark_blue.xml")

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
            -1: "Unknown Error"
        }
        return code

class LoadPluginHeader:
    """
    config needed
    Key: type | Header Type, for look please go to ./documentation/pluginEdit/header.md
    """
    def __init__(self, header: AnyStr, filename: AnyStr = None):
        self.filename = filename
        self.header = loads(header) if filename else self.readFile(header)

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
        if 1:
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
            addLog(0, f"Successfully to load {self.filename}! Used {(datetime.now() - beforeDatetime).total_seconds():02f}secs.")
            return items

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

print(LoadPluginHeader("""{
  "config": {
    "objectName": "advanced_file_processor",
    "type": 0,
    "api": [1, 1],
    "enableCustomizeCommandRun": true,
    "useSinoteVariableInString": true
  },
  "function": {
    "process_data_files": [
      ["log", 0, "开始处理数据文件"],
      ["var", "processed_count", "0"],
      ["var", "error_count", "0"],
      ["mkdir", "./data/input"],
      ["mkdir", "./data/output"],
      ["mkdir", "./data/backup"],
      
      // 检查输入目录是否存在文件
      ["system", "dir ./data/input /b > ./temp_file_list.txt", {"out2term": false}],
      ["rfile", "./temp_file_list.txt", "file_list"],
      ["log", 0, "找到文件列表: %var:file_list%"],
      
      // 处理每个文件
      ["var", "current_file", ""],
      ["var", "file_index", "0"],
      ["log", 0, "开始批量处理文件"],
      
      // 文件处理循环开始
      ["var", "file_count", "0"],
      ["system", "dir ./data/input /b | find /c /v \\"\\" > ./file_count.txt", {"out2term": false}],
      ["rfile", "./file_count.txt", "file_count"],
      ["log", 0, "总共发现 %var:file_count% 个文件需要处理"],
      
      // 处理第一个文件
      ["log", 0, "处理第1个文件"],
      ["cfile", "./data/input/data_1.txt"],
      ["wfile", "./data/input/data_1.txt", "示例数据内容 1\\n第二行数据\\n第三行数据"],
      ["rfile", "./data/input/data_1.txt", "file_content"],
      ["log", 0, "文件内容: %var:file_content%"],
      ["wfile", "./data/output/processed_1.txt", "处理后的数据: %var:file_content%"],
      ["pfile", "./data/input/data_1.txt", "./data/backup/data_1_backup.txt"],
      ["var", "processed_count", "1"],
      
      // 处理第二个文件  
      ["log", 0, "处理第2个文件"],
      ["cfile", "./data/input/data_2.txt"],
      ["wfile", "./data/input/data_2.txt", "另一个文件的数据\\n更多内容在这里"],
      ["rfile", "./data/input/data_2.txt", "file_content_2"],
      ["wfile", "./data/output/processed_2.txt", "分析结果: %var:file_content_2%"],
      ["pfile", "./data/input/data_2.txt", "./data/backup/data_2_backup.txt"],
      ["var", "processed_count", "2"],
      
      // 处理第三个文件 - 模拟错误情况
      ["log", 0, "处理第3个文件"],
      ["cfile", "./data/input/data_3.txt"],
      ["wfile", "./data/input/data_3.txt", "无效数据格式\\n损坏的文件内容"],
      ["rfile", "./data/input/data_3.txt", "corrupted_content"],
      ["log", 1, "文件 data_3.txt 格式异常，跳过处理"],
      ["var", "error_count", "1"],
      
      // 数据处理和分析
      ["log", 0, "开始数据分析阶段"],
      ["var", "analysis_result", "数据分析完成"],
      ["wfile", "./data/output/analysis_report.txt", "处理报告\\n==========\\n成功处理: %var:processed_count% 个文件\\n处理失败: %var:error_count% 个文件\\n处理时间: 2024年"],
      
      // 生成统计信息
      ["cfile", "./data/output/statistics.json"],
      ["wfile", "./data/output/statistics.json", "{\\n  \\"processed\\": %var:processed_count%,\\n  \\"errors\\": %var:error_count%,\\n  \\"timestamp\\": \\"2024-01-01\\"\\n}"],
      
      // 验证输出文件
      ["log", 0, "验证输出文件"],
      ["system", "dir ./data/output /b > ./output_files.txt", {"out2term": false}],
      ["rfile", "./output_files.txt", "output_files"],
      ["log", 0, "生成的输出文件: %var:output_files%"],
      
      // 清理临时文件
      ["log", 0, "清理临时文件"],
      ["dfile", "./temp_file_list.txt"],
      ["dfile", "./file_count.txt"], 
      ["dfile", "./output_files.txt"],
      
      // 最终报告
      ["log", 0, "文件处理完成"],
      ["msgbox", "处理完成", "成功处理 %var:processed_count% 个文件\\n失败 %var:error_count% 个文件"],
      ["vpr", "processed_count"],
      ["vpr", "error_count"],
      
      // 记录到日志文件
      ["afile", "./processing_log.txt", "=== 处理会话 ===\\n"],
      ["afile", "./processing_log.txt", "时间: 2024-01-01\\n"],
      ["afile", "./processing_log.txt", "处理文件数: %var:processed_count%\\n"],
      ["afile", "./processing_log.txt", "错误数: %var:error_count%\\n"],
      ["afile", "./processing_log.txt", "状态: 完成\\n\\n"],
      
      ["log", 0, "高级文件处理器执行完毕"]
    ],
    
    "cleanup_workspace": [
      ["log", 0, "开始清理工作区"],
      ["msgbox", "确认清理", "即将删除所有生成的文件，确认继续?"],
      ["dfile", "./data/input/data_1.txt"],
      ["dfile", "./data/input/data_2.txt"], 
      ["dfile", "./data/input/data_3.txt"],
      ["dfile", "./data/output/processed_1.txt"],
      ["dfile", "./data/output/processed_2.txt"],
      ["dfile", "./data/output/analysis_report.txt"],
      ["dfile", "./data/output/statistics.json"],
      ["dfile", "./data/backup/data_1_backup.txt"],
      ["dfile", "./data/backup/data_2_backup.txt"],
      ["dfile", "./processing_log.txt"],
      ["log", 0, "工作区清理完成"],
      ["msgbox", "清理完成", "所有临时文件已删除"]
    ]
  },
  "runFunc": [
    "process_data_files"
  ]
}""","filename.json").getValue())