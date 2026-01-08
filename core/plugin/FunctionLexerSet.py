from core.plugin.Variables import Variables
from core.plugin.LoadPluginBase import LoadPluginBase
from utils.argumentParser import debugMode
from utils.err import err
from utils.logger import addLog
from utils.config import settingObject
from PySide6.QtWidgets import QMessageBox, QInputDialog
from pathlib import Path
from typing import Callable, Any
from functools import partial
from shutil import rmtree, copy2


class FunctionLexerSet:
    def __init__(
        self, listOfFunc: list[str | int | dict | dict], translateVariables: bool = True
    ):
        API_SUPPORT_VERSION = "1.0.1"  # Not used, just a note
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
            7: self.usefunc,
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

    def afile(self, filePath: str, content: str) -> None:
        FunctionLexerSet.debugLog(f"Preparing to append content to file {filePath}")
        try:
            with open(filePath, "a", encoding=self._getFileEncoding(filePath)) as f:
                f.write(content)
        except Exception as e:
            addLog(
                2,
                f"Failed to write file {filePath}: {repr(e)}",
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
            addLog(
                2,
                f"Failed to write file {filePath}: {repr(e)}",
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
            addLog(
                2, f"Cannot read file {filePath}: {repr(e)}", "FunctionLexerActivity"
            )
            self._varObj.addVar(varName, f"err {repr(e)}")
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
                addLog(2, f"Delete file {filePath} failed", "FunctionLexerActivity")
            else:
                success()
        else:
            success()

    def cfile(self, filePath: str) -> None:
        FunctionLexerSet.debugLog(f"Preparing to create a file (Path: {filePath})")
        if not Path(filePath).is_file() and Path(filePath).exists():
            addLog(
                2,
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
                addLog(2, f"Failed to create file: {repr(e)}", "FunctionLexerActivity")
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
                addLog(2, f"Failed to erase file: {repr(e)}", "FunctionLexerActivity")
            else:
                FunctionLexerSet.debugLog(f"Successfully to erase file {filePath}")

    def pfile(self, originalFile: str, movePath: str, allowedExists: bool) -> None:
        FunctionLexerSet.debugLog(f"Preparing to copy {originalFile} to {movePath}")
        if not Path(originalFile).exists():
            addLog(
                2,
                f"Failed to copy file: Original file is not exists",
                "FunctionLexerActivity",
            )
            return
        if not Path(originalFile).is_file():
            addLog(
                2,
                f"Failed to copy file: Original file is not a file",
                "FunctionLexerActivity",
            )
            return
        if Path(movePath).exists() and not allowedExists:
            addLog(
                2,
                f"Failed to copy file: New file already exists",
                "FunctionLexerActivity",
            )
            return
        try:
            copy2(originalFile, movePath)
        except Exception as e:
            addLog(2, f"Failed to copy file: {repr(e)}", "FunctionLexerActivity")
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
            addLog(
                2,
                f"Error occurred when directory make: {repr(e)}",
                "FunctionLexerActivity",
            )
            return
        if Path(dir).is_file():
            addLog(
                2,
                f"Error occurred when directory make: directory is a file.",
                "FunctionLexerActivity",
            )
            return
        FunctionLexerSet.debugLog(f"Make directory successfully!")

    def errbox(self, errCode: str) -> None:
        FunctionLexerSet.debugLog(f"Making a Error Popup Window (errCode={errCode})")
        err(errCode)

    def usefunc(self, funcname: str) -> None:
        addLog(
            1,
            "UseFunc Command is not support this version (Wait for 1.0.3)",
            "FunctionLexerActivity",
        )

    def system(self, command: str) -> None:
        addLog(
            1,
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
            addLog(3, outText, "FunctionLexerActivity")

    def log(self, level: int, outText: str) -> None:
        FunctionLexerSet.debugLog("Preparing to log out...")
        if level not in (0, 1):
            addLog(2, f"Illegal Log Level: {level}", "FunctionLexerActivity")
            return
        addLog(level, self.lexVariable(outText), "FunctionRunnerActivity")
        FunctionLexerSet.debugLog(f"Logged Out Customize Text, LEVEL: {level}.")

    def set(self, setName: str, setContent: Any) -> None:
        settingObject.setValue(setName, setContent)

    def getValue(self) -> list[partial]:
        """
        Get value
        :return: None
        """
        returnlist: list[partial] = []
        for i in self._listOfFunc:
            if i[0] not in self._if.keys():
                addLog(
                    2,
                    f"Not compatible with this command! Number: {i[0]}",
                    "FunctionLexerActivity",
                )
                continue
            LoadPluginBase.logIfDebug(f"Number: {i[0]}, Function: {self._if[i[0]]}")
            if i[0] == 0:
                returnlist.append(partial(self._if[i[0]], i[1]))
            elif i[0] == 2:
                returnlist.append(partial(self._if[i[0]], i[1], i[2]))
            elif i[0] == 3:
                returnlist.append(
                    partial(self._if[i[0]], i[1], "NULL" if len(i) == 2 else i[2])
                )
            elif i[0] == 4:
                returnlist.append(partial(self._if[i[0]], i[1]))
            elif i[0] == 5:
                returnlist.append(partial(self._if[i[0]], i[1], i[2], i[3]))
            elif i[0] == 6:
                returnlist.append(partial(self._if[i[0]], i[1]))
            elif i[0] == 7:
                returnlist.append(partial(self._if[i[0]], i[1]))
            elif i[0] == 100:
                returnlist.append(partial(self._if[i[0]], i[1], i[2]))
            elif i[0] == 101:
                returnlist.append(partial(self._if[i[0]], i[1]))
            elif i[0] == 102:
                returnlist.append(partial(self._if[i[0]], i[1]))
            elif i[0] == 103:
                returnlist.append(partial(self._if[i[0]], i[1]))
            elif i[0] == 104:
                returnlist.append(
                    partial(
                        self._if[i[0]],
                        i[1],
                        i[2],
                        (
                            False
                            if len(i) <= 3
                            else i[3] if isinstance(i[3], bool) else False
                        ),
                    )
                )
        return returnlist
