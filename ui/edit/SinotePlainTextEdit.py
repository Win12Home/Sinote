from pathlib import Path
from typing import Any

from core.AutoLoadPluginThread import syntaxHighlighter
from core.i18n import getLangJson
from core.plugin import LoadPluginBase
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QSyntaxHighlighter
from PySide6.QtWidgets import QMessageBox, QWidget
from ui.edit.SpacingSupportEdit import SpacingSupportEdit
from ui.selfLogger import debugLog
from utils.logger import Logger


class SinotePlainTextEdit(SpacingSupportEdit):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.setFilename = None
        self.nowFilename: str | None = None
        self.plName: str | None = None
        self.finalEncoding: str | None = None
        self.highlighter: QSyntaxHighlighter | None = None
        self.temp: QThread | None = None
        self.num: int = -1
        self.setStyleSheet(f"{self.styleSheet()}border: none;")

    def autoSave(self):
        if self.nowFilename:
            debugLog(f"Automatic saving file {self.nowFilename}")
            with open(self.nowFilename, "w+", encoding="utf-8") as f:
                f.write(self.toPlainText())
            debugLog(f"Successfully to save file {self.nowFilename}")

    def clear(self):
        self.finalEncoding = None
        self.plName = None
        self.nowFilename = None
        super().clear()

    def newFile(self):
        self.clear()
        if self.setFilename is not None and hasattr(self.parent(), "indexOf"):
            self.setFilename(
                self.parent().indexOf(self),
                getLangJson("EditorUI")["editor.tab.new_file"],
            )
        self.nowFilename = None

    class _LoadHighlighter(QThread):
        foundHighlighter = Signal(LoadPluginBase.LazyCustomizeSyntaxHighlighter)
        setPairKeywords = Signal(list)
        noSyntax = Signal()
        test = Signal()

        def __init__(self, appendix: str):
            super().__init__()
            self.appendix = appendix

        def run(self) -> None:
            debugLog(f"Finding Highlighter (*.{self.appendix})... (THREAD) 🔎")
            temp: LoadPluginBase.LazyCustomizeSyntaxHighlighter | None = None
            temp2, temp3 = None, None
            # name: str | None = None
            for k, i in syntaxHighlighter.items():
                if self.appendix in i[1]:
                    debugLog(f"{self.appendix} is in {i[1]}, successfully to find! ✅")
                    temp = i[0]
                    temp2 = i[2]
                    temp3 = i[3]
                    # name = k.strip()
                    break
                else:
                    debugLog(f"{self.appendix} isn't in {i[1]}, continue find! 🔎")
            self.test.emit()
            if temp is not None:
                debugLog(r"Emit found Syntax Highlighter 💥")
                self.foundHighlighter.emit(temp)
                temp3.append(temp2)
                self.setPairKeywords.emit(temp3)
            else:
                debugLog(r"Cannot found Syntax Highlighter ❌")
                self.noSyntax.emit()

    def setHighlighter(self, highlighter: Any) -> None:
        debugLog(
            "Setting another Highlighter..."
            if highlighter
            else "Cleaning Highlighter..."
        )
        self.highlighter = (
            highlighter.getObject()
            if highlighter is not None
            else LoadPluginBase.CustomizeSyntaxHighlighter([])  # For disable number highlighting
        )
        self.highlighter.setDocument(self.document())

    def setFileAppendix(self, fileAppendix: str) -> None:
        debugLog(f"Attempting to set file appendix to {fileAppendix} 🪲")
        debugLog("Finding Children of Document and remove Highlighter")
        for i in self.findChildren(LoadPluginBase.CustomizeSyntaxHighlighter):
            i.setDocument(None)
            i.deleteLater()
        debugLog("Successfully remove Highlighter ✅")
        debugLog("Searching Highlighter 🔎")
        self.temp = self._LoadHighlighter(fileAppendix)
        self.temp.foundHighlighter.connect(
            lambda a: self.setHighlighter(a), Qt.ConnectionType.SingleShotConnection
        )
        self.temp.setPairKeywords.connect(
            lambda a: self._setPairKeywords(a), Qt.ConnectionType.QueuedConnection
        )
        self.temp.noSyntax.connect(
            self._setNoSyntax, Qt.ConnectionType.QueuedConnection
        )
        self.temp.start()

    def _setPairKeywords(self, arg: list) -> None:
        self.defineKeywords = arg
        self.usingCodeControl = True

    def _setNoSyntax(self) -> None:
        self.defineKeywords = []
        self.setHighlighter(None)
        self.usingCodeControl = False
        self.plName = None

    def readFile(self, filename: str) -> None:
        Logger.info(
            f"Attempting to read file {filename}...", "SinoteUserInterfaceActivity"
        )
        if not Path(filename).exists():
            Logger.warning(
                f"Cannot find file {filename}, current file will save.",
                "SinoteUserInterfaceActivity",
            )
            return
        if not Path(filename).is_file():
            Logger.warning(
                f"Are you sure you using a normal file? Cannot read {filename}!",
                "SinoteUserInterfaceActivity",
            )
            return
        # Try different encodings and support Chinese(GBK/GB2312)
        encodings = [
            "utf-8",
            "utf-16",
            "gbk",
            "gb2312",
            "latin-1",
            "windows-1252",
            "utf-32",
            "ascii",
            "utf-8-sig",
            "utf-16-le",
            "utf-16-be",
        ]
        content: str | None = None

        for encoding in encodings:
            try:
                debugLog(f"Trying reading with encoding {encoding.upper()} 🤔")
                with open(filename, "r", encoding=encoding) as f:
                    content = f.read()
                    self.finalEncoding = encoding.upper()
                    debugLog(
                        f"Successfully to read {filename} with {encoding} encoding! {len(content) / 8 / 1024:.2f}KiB {len(content.splitlines())} lines"
                    )
                break
            except (UnicodeDecodeError, LookupError):
                debugLog(f"Failed to read with encoding {encoding.upper()} 💀")
                continue
            except PermissionError:
                Logger.error(
                    f"Cannot read file {filename}. Permission Denied!",
                    "SinoteUserInterfaceActivity",
                )
                break
            except IOError:
                Logger.error(
                    f"Cannot read file {filename}. IOError at Python!",
                    "SinoteUserInterfaceActivity",
                )
                break
            except Exception as e:
                Logger.warning(
                    f"Failed to read {filename} with {encoding}: {e!r}",
                    "SinoteUserInterfaceActivity",
                )
                continue
        if content is not None:
            self.setPlainText(content)
            self.setFileAppendix(Path(filename).suffix[1:])
            if self.setFilename is not None:
                self.setFilename(
                    self.parent().indexOf(self),
                    getLangJson("EditorUI")["editor.tab.tab_name"].format(
                        Path(filename).name
                    ),
                )
            self.nowFilename = str(Path(filename))
            Logger.info(
                f"Successfully to read file {filename} using {self.finalEncoding} encoding! ✅",
                "SinoteUserInterfaceActivity",
            )
        else:
            Logger.error(
                f"Cannot read file {filename}. Tried all encodings but failed! Or other Exception out! ❌",
                "SinoteUserInterfaceActivity",
            )
            w = QMessageBox(
                QMessageBox.Icon.Critical,
                getLangJson("MessageBox")["msgbox.title.error"],
                getLangJson("MessageBox")["msgbox.error.fileCannotRead"],
                buttons=QMessageBox.StandardButton.Ok,
            )
            w.exec()
