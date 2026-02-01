from datetime import datetime
from functools import partial
from pathlib import Path
from shutil import copy2, rmtree
from typing import Any, Callable

from core.plugin.LoadPluginBase import LoadPluginBase
from core.plugin.Variables import Variables
from PySide6.QtWidgets import QInputDialog, QMessageBox
from utils.application import BaseApplication
from utils.argumentParser import debugMode
from utils.config import settingObject
from utils.err import err
from utils.logger import Logger


class FunctionLexerSet:
    def __init__(
        self,
        dictOfFunc: dict[str, tuple[list[Any] | bool]],
        translateVariables: bool = True,
    ):
        API_SUPPORT_VERSION = "1.0.2"  # Not used, just a note
        self._dictOfFunc = dictOfFunc
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
            7: self.usefunc,
            8: self.sleep,
            100: self.set,
            101: self.mkdir,
            102: self.cfile,
            103: self.efile,
            104: self.pfile,
            105: self.dfile,
            106: self.afile,
            107: self.wfile,
            108: self.rfile,
            200: self.errbox,
        }
        # self._insideFunction = self._if
        # You can remove # head if you want to use self._insideFunction

    def sleep(self, msecs: int) -> None:
        if not BaseApplication.instance():
            Logger.warning("QApplication has not create yet", "FunctionLexerActivity")
            __import__("time").sleep(msecs / 1000)
            return
        time: datetime = datetime.now()
        FunctionLexerSet.debugLog(f"Sleeping {msecs} msecs...")
        while (datetime.now() - time).total_seconds() * 1000 < msecs:
            __import__("time").sleep(0.01)  # Sleep 10ms
            if BaseApplication.instance().quited:
                return
            BaseApplication.instance().processEvents()  # Update
        FunctionLexerSet.debugLog(f"Sleep {msecs} successfully, exited.")

    def afile(self, filePath: str, content: str) -> None:
        FunctionLexerSet.debugLog(f"Preparing to append content to file {filePath}")
        try:
            with open(filePath, "a", encoding=self._getFileEncoding(filePath)) as f:
                f.write(content)
        except Exception as e:
            Logger.error(
                f"Failed to write file {filePath}: {e!r}",
                "FunctionLexerActivity",
            )
        else:
            FunctionLexerSet.debugLog(f"Append content to file {filePath} successfully")

    def wfile(self, filePath: str, content: str) -> None:
        FunctionLexerSet.debugLog(f"Preparing to write file {filePath}")
        try:
            with open(filePath, "w", encoding=self._getFileEncoding(filePath)) as f:
                f.write(content)
        except Exception as e:
            Logger.error(
                f"Failed to write file {filePath}: {e!r}",
                "FunctionLexerActivity",
            )
        else:
            FunctionLexerSet.debugLog(f"Wrote file successfully!")

    def rfile(self, filePath: str, varName: str) -> None:
        FunctionLexerSet.debugLog(
            f"Preparing to read file {filePath} to variable {varName}"
        )
        try:
            with open(filePath, "r", encoding=self._getFileEncoding(filePath)) as f:
                self._varObj.addVar(varName, f.read())
        except Exception as e:
            Logger.error(f"Cannot read file {filePath}: {e!r}", "FunctionLexerActivity")
            self._varObj.addVar(varName, f"err {e!r}")
        else:
            FunctionLexerSet.debugLog(r"Read file successfully!")

    def dfile(self, filePath: str) -> None:
        FunctionLexerSet.debugLog(f"Preparing to delete file {filePath}")
        success: Callable = partial(
            FunctionLexerSet.debugLog, f"Delete file {filePath} successfully!"
        )
        if Path(filePath).exists():
            try:
                if Path(filePath).is_dir():
                    rmtree(filePath)
                else:
                    Path(filePath).unlink(True)
            except Exception as e:
                Logger.error(f"Delete file {filePath} failed", "FunctionLexerActivity")
            else:
                success()
        else:
            success()

    def cfile(self, filePath: str) -> None:
        FunctionLexerSet.debugLog(f"Preparing to create a file (Path: {filePath})")
        if not Path(filePath).is_file() and Path(filePath).exists():
            Logger.error(
                f"{filePath} is not a file, automatically skipped!",
                "FunctionLexerActivity",
            )
        elif Path(filePath).exists():
            FunctionLexerSet.debugLog(f"Automatically skipped because file exists")
        else:
            try:
                with open(filePath, "w", encoding="utf-8") as f:
                    f.write("")
            except Exception as e:
                Logger.error(f"Failed to create file: {e!r}", "FunctionLexerActivity")
            else:
                FunctionLexerSet.debugLog(f"Successfully to create file!")

    def efile(self, filePath: str) -> None:
        FunctionLexerSet.debugLog(f"Preparing to erase content of file {filePath}")
        if not Path(filePath).exists():
            FunctionLexerSet.debugLog(
                f"File {filePath} not exists, automatically generate!"
            )
            self.cfile(filePath)
        else:
            try:
                with open(filePath, "w", encoding=self._getFileEncoding(filePath)) as f:
                    f.write("")
            except Exception as e:
                Logger.error(f"Failed to erase file: {e!r}", "FunctionLexerActivity")
            else:
                FunctionLexerSet.debugLog(f"Successfully to erase file {filePath}")

    def pfile(self, originalFile: str, movePath: str, allowedExists: bool) -> None:
        FunctionLexerSet.debugLog(f"Preparing to copy {originalFile} to {movePath}")
        if not Path(originalFile).exists():
            Logger.error(
                f"Failed to copy file: Original file is not exists",
                "FunctionLexerActivity",
            )
            return
        if not Path(originalFile).is_file():
            Logger.error(
                f"Failed to copy file: Original file is not a file",
                "FunctionLexerActivity",
            )
            return
        if Path(movePath).exists() and not allowedExists:
            Logger.error(
                f"Failed to copy file: New file already exists",
                "FunctionLexerActivity",
            )
            return
        try:
            copy2(originalFile, movePath)
        except Exception as e:
            Logger.error(f"Failed to copy file: {e!r}", "FunctionLexerActivity")
        else:
            FunctionLexerSet.debugLog(
                f"Successfully to copy {originalFile} to {movePath}"
            )

    def _getFileEncoding(self, filePath: str) -> str:
        if not Path(filePath).exists():
            return "utf-8"
        if not Path(filePath).is_file():
            return "utf-8"
        encodingList: list[str] = [
            "utf-8",
            "gbk",
            "gb2312",
            "latin-1",
            "utf-16",
            "ascii",
            "unicode",
        ]
        for encoding in encodingList:
            try:
                with open(filePath, "r", encoding=encoding) as f:
                    pass
            except Exception:
                continue
            else:
                return encoding
        return "utf-8"

    def mkdir(self, dir: str) -> None:
        FunctionLexerSet.debugLog(f"Preparing to Make a directory (Path: {dir})")
        try:
            Path(dir).mkdir(exist_ok=True)
        except Exception as e:
            Logger.error(
                f"Error occurred when directory make: {e!r}",
                "FunctionLexerActivity",
            )
            return
        if Path(dir).is_file():
            Logger.error(
                f"Error occurred when directory make: directory is a file.",
                "FunctionLexerActivity",
            )
            return
        FunctionLexerSet.debugLog(f"Make directory successfully!")

    def errbox(self, errCode: str) -> None:
        FunctionLexerSet.debugLog(f"Making a Error Popup Window (errCode={errCode})")
        err(errCode)

    def usefunc(self, funcName: str, lexed: dict[str, Any]) -> None:  # NOQA
        # Logger.warning(
        #    "UseFunc Command is not support this version (Wait for 1.0.3)",
        #    "FunctionLexerActivity",
        # )
        #
        # Now realized (API: 1.0.2)
        if funcName not in lexed.copy():
            Logger.error(
                f"{funcName} is not defined here, try define earlier than this function?",
                "FunctionLexerActivity",
            )
            return
        for line, callableFunc in enumerate(lexed[funcName], 1):
            if isinstance(callableFunc, Callable):
                FunctionLexerSet.debugLog(
                    f"Attempting to run command at line {line} in function {funcName}"
                )
                try:
                    callableFunc()
                except Exception as e:
                    Logger.error(
                        f"Failed to run command at line {line} in function {funcName}",
                        "FunctionRunnerActivity",
                    )
                    Logger.error(
                        f'Error reason: {e!r} "usefunc" will exit because error occurred!'
                    )  # NOQA
                    break
                else:
                    FunctionLexerSet.debugLog(
                        f"Successfully to run command declared at line {line}!"
                    )
            else:
                Logger.error(
                    f"Failed to run command at line {line} in function {funcName}",
                    "FunctionRunnerActivity",
                )
                Logger.error(
                    f'Error reason: SinoteError declared there: Function is not callable in Python Runtime "usefunc" will exit because error occured!'
                )  # NOQA, always
                break  # OwO break break!

    def system(self, command: str) -> None:
        Logger.warning(
            "System Command is not support this version (Wait for 1.0.3)",
            "FunctionLexerActivity",
        )

    def addVar(self, varName: str, varContent: str) -> None:
        self._varObj.addVar(varName, varContent)

    def messageInput(self, title: str, content: str, varname: str) -> None:
        FunctionLexerSet.debugLog("Preparing to Message Input for a Variable")
        temp, ok = QInputDialog.getText(None, title, content)
        if ok:
            FunctionLexerSet.debugLog(
                f"Successfully received input text from InputDialog, content: {temp}"
            )
            self._varObj.addVar(varname, temp)
        else:
            FunctionLexerSet.debugLog(
                "Failed to receive input text from InputDialog, default's only create and set its content to NULL."
            )
            self._varObj.addVar(varname)

    def lexVariable(self, string: str) -> str:
        return self._varObj.resolveVarInString(string) if self._needVar else string

    def printContentOfVariable(self, variableName: str) -> None:
        FunctionLexerSet.debugLog("Preparing to Print Content")
        print(self._varObj.getVar(variableName))
        FunctionLexerSet.debugLog("Successfully to Print Content")

    def messageBox(self, title: str, content: str) -> None:
        FunctionLexerSet.debugLog("Preparing to Set a Message Box")
        temp = QMessageBox(
            QMessageBox.Icon.NoIcon,
            self.lexVariable(title),
            self.lexVariable(content),
            QMessageBox.StandardButton.Close,
        )
        temp.exec()
        FunctionLexerSet.debugLog("Successfully to Set a Message Box")

    def print(self, outText: str) -> None:
        FunctionLexerSet.debugLog("Preparing to Print out Customize Text")
        print(self.lexVariable(outText))
        FunctionLexerSet.debugLog("Successfully to Print out Customize Text")

    @staticmethod
    def debugLog(outText: str) -> None:
        if debugMode:
            Logger.debug(outText, "FunctionLexerActivity")

    def log(self, level: int, outText: str) -> None:
        FunctionLexerSet.debugLog("Preparing to log out...")
        if level not in (0, 1):
            Logger.error(f"Illegal Log Level: {level}", "FunctionLexerActivity")
            return
        logFunc: Callable = lambda: None
        if level == 1:
            logFunc = Logger.warning
        elif level == 2:
            logFunc = Logger.error
        elif level == 3:
            logFunc = Logger.debug
        else:
            logFunc = Logger.info
        logFunc(self.lexVariable(outText), "FunctionRunnerActivity")
        FunctionLexerSet.debugLog(f"Logged Out Customize Text, LEVEL: {level}.")

    def set(self, setName: str, setContent: Any) -> None:
        settingObject.setValue(setName, setContent)

    def getValue(self) -> list[partial]:
        """
        Get value
        :return: None
        """
        lexed: dict[str, list[partial]] = {}
        inRunFunc: dict[str, bool] = {}
        for funcName, funcContent in self._dictOfFunc.items():
            thisLexed: list[partial] = []
            for oneFunc in funcContent[0]:
                if oneFunc[0] not in self._if.keys():
                    Logger.error(
                        f"Not compatible with this command! Number: {oneFunc[0]}",
                        "FunctionLexerActivity",
                    )
                    continue
                LoadPluginBase.logIfDebug(
                    f"Number: {oneFunc[0]}, Function: {self._if[oneFunc[0]]}"
                )
                if oneFunc[0] in [0, 4, 6, 8, 101, 102, 103]:
                    thisLexed.append(partial(self._if[oneFunc[0]], oneFunc[1]))
                elif oneFunc[0] in [1, 2, 100]:
                    thisLexed.append(
                        partial(self._if[oneFunc[0]], oneFunc[1], oneFunc[2])
                    )
                elif oneFunc[0] == 3:
                    thisLexed.append(
                        partial(
                            self._if[oneFunc[0]],
                            oneFunc[1],
                            "NULL" if len(oneFunc) == 2 else oneFunc[2],
                        )
                    )
                elif oneFunc[0] == 5:
                    thisLexed.append(
                        partial(
                            self._if[oneFunc[0]], oneFunc[1], oneFunc[2], oneFunc[3]
                        )
                    )
                elif oneFunc[0] == 7:
                    thisLexed.append(partial(self._if[oneFunc[0]], oneFunc[1], lexed))
                elif oneFunc[0] == 104:
                    thisLexed.append(
                        partial(
                            self._if[oneFunc[0]],
                            oneFunc[1],
                            oneFunc[2],
                            (
                                False
                                if len(oneFunc) <= 3
                                else (
                                    oneFunc[3]
                                    if isinstance(oneFunc[3], bool)
                                    else False
                                )
                            ),
                        )
                    )
            lexed[funcName] = thisLexed
            inRunFunc[funcName] = funcContent[1]
        returnLexed: list[partial] = []
        for funcName, funcContent in lexed.items():
            if not inRunFunc.get(funcName, False):
                continue  # Pass, because it is not in runFunc
            for oneFunc in funcContent:
                returnLexed.append(oneFunc)
        return returnLexed
