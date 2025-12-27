from pathlib import Path
from utils.logger import addLog, normalLogOutput
from platform import processor, system
from psutil import cpu_percent, virtual_memory
from datetime import datetime
from traceback import format_exception
from utils.err import err
import sys

errExceptionhookDetected: bool = False


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
    string: str = (
        f"Current Log:\n  {"\n  ".join(normalLogOutput)}\nError:\n  {"\n  ".join(format_exception(err_value))}\nFirmware Information:\n  CPU: {processor()}\n  CPU Usage: {cpu_percent(interval=1)}\n  RAM Used: {virtual_memory().used / (1024*1024)}MB\n  RAM Total: {virtual_memory().total / (1024*1024)}MB\n  Platform: {system()}\nDate\n  {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\nPlease feedback to developer yet!"
    )
    with open(
        f"./log/critical/criticalLog-{datetime.now().strftime("%Y-%m-%d %H.%M.%S")}.log",
        "w",
        encoding="utf-8",
    ) as f:
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
    global errExceptionhookDetected
    if not errExceptionhookDetected:
        errExceptionhookDetected = True
        name: str = ""
        if hasattr(err_type, "__class__"):
            name = err_type.__class__.__name__
        else:
            name = type(err_type).__name__
        addLog(
            2,
            bodyText="Error occurred by errExceptionHook, please give the error to the author!",
            activity="ExceptionHookActivity",
        )
        addLog(0, bodyText=f"Output has printed:\n{str(err_type)[8:-2]}: {err_value}")
        addLog(
            1,
            bodyText=f"Starting Window, if error occurred again, it won't write log when quit.",
            activity="ExceptionHookActivity",
        )
        err("0xffffffff", None, True)
        addLog(
            0, bodyText="Attempting to save Critical Log", activity="FileConfigActivity"
        )
        criticalLogSaver(err_type, err_value, err_tb)
        addLog(
            0,
            bodyText="It might be successfully to save, please feedback to developer! Program will continue running.",
            activity="ExceptionHookActivity",
        )
        errExceptionhookDetected = False
    else:
        sys.__excepthook__(err_type, err_value, err_tb)


def setExceptionHook() -> None:
    sys.excepthook = errExceptionHook
