"""
Sinote Widgets
Win12Home (C) 2025, MIT.
"""
from pathlib import PurePath
from BasicModule import * # Note: PySide6 was imported in BasicModule.py
import time # Wow, I want to sleep!

def debugLog(content: str) -> None:
    if debugMode:
        thread: Thread = Thread(daemon=True)
        thread.run = partial(addLog,  3, content, "SinoteUserInterfaceActivity")
        thread.start()

def debugPluginLog(content: str) -> None:
    if debugMode:
        thread: Thread = Thread()
        thread.run = partial(addLog, 3, content, "SinoteMainPluginLoadActivity")
        thread.start()

syntaxHighlighter: dict[str, list[LoadPluginBase.CustomizeSyntaxHighlighter | list[str]]] = {}
loadedPlugin: dict[str, dict[str, str | int | None]] = {}
autoRun: list[partial] = []
"""
syntaxHighlighter Struct:
{
    "Code Name": [
        <One LoadPluginBase.LazyCustomizeSyntaxHighlighter>,
        ["appendix1","appendix2","appendix3","appendix4","appendix5","appendix6"],
        ...
    ]
}
"""

outputDeveloperDebugInformation()

class AutoLoadPlugin(QThread):
    loadedOne = Signal()
    loadNameChanged = Signal(str)
    loadTotal = Signal(int)
    processFinished = Signal()

    def run(self) -> None:
        global loadedPlugin, syntaxHighlighter, autoRun
        if "--dont-load-any-plugin" in args or "-displug" in args:
            addLog(0, "--dont-load-any-plugin or -displug activated, no any plugins will be loaded!")
            return
        if not Path("./resources/plugins/").exists():
            addLog(1, "Failed to load all the Plugins, Reason: ./resources/plugins/ not exists ❌")
            return
        if not Path("./resources/plugins/").is_dir():
            addLog(1, "Failed to load all the Plugins, Reason: ./resources/plugins/ not a folder ❌")
            return
        dirs = list(Path("./resources/plugins/").iterdir())
        self.loadTotal.emit(len(dirs))
        debugPluginLog(f"Total: {len(dirs)}, Starting load... 💥")
        beforeLoadDatetime: datetime = datetime.now()
        for item in dirs:
            debugPluginLog(f"Loading {item.name}")
            if not item.is_dir():
                addLog(0, f"Automatic skipped {item.name}, Reason: not a folder ❌")
                continue

            infoJson: Path | PurePath = item / "info.json"
            if not (infoJson.exists()):
                addLog(1, f"Automatic skipped {item.name}, Reason: info.json not exists ❌")
                continue
            temp = LoadPluginInfo(item.name).getValue()
            loadedPlugin[temp[0]["objectName"]] = temp[0]
            self.loadNameChanged.emit(temp[0]["name"])
            if temp[0]["objectName"] in settingObject.getValue("disableplugin"):
                debugPluginLog(f"Automatic skip plugin {temp[0]["objectName"]} (DISABLED)")
                self.loadedOne.emit()
                continue
            debugPluginLog(f"Successfully loaded {item.name}, objectName: {temp[0]["objectName"]}. Preparing to parse... ✅")
            for key in temp[1]:
                debugPluginLog(f"Loading {key[0]}...")
                if key[1] == 1:
                    debugPluginLog(f"Checked its property! Type: SyntaxHighlighter 🔎")
                    before: datetime = datetime.now()
                    syntaxHighlighter[key[2]] = [key[4], key[3], key[5], key[6]]
                elif key[1] == 0:
                    debugPluginLog(f"Checked its property! Type: RunningFunc 🤓")
                    debugPluginLog(f"Appending to autoRun... 💥")
                    [autoRun.append(i) if isinstance(i, partial) else None for i in key[2]]
                    """
                    This code definitely equals
                    for i in key[2]:
                        if isinstance(i, partial):
                            autoRun.append(i)
                    But it's will create a unused list ([None if isinsta for i in key[2]])
                    """
                    debugPluginLog(f"Successfully to append! ✅")
            self.loadedOne.emit()
        usedTime: float = (datetime.now() - beforeLoadDatetime).total_seconds()
        debugPluginLog(f"Successfully to load plugins! ✅ Used {usedTime:.3f}s")
        debugPluginLog(f"An assessment for Sinote: {"Use a new computer instead 🤔💀" if usedTime / len(dirs) > 1.0 else "Too slow 💀" if usedTime / len(dirs) > 0.8 else "A bit slow 😰" if usedTime / len(dirs) > 0.65 else "Good load 😍"}")
        self.processFinished.emit()


class AutomaticSaveThingsThread(QThread):
    def __init__(self, parent: QWidget = None, saveSecs: int = 10):
        super().__init__(parent)
        self.saveSecs: int = saveSecs
        self.running: bool = True
        self.ended: bool = False

    def reset(self) -> None:
        self.saveSecs = settingObject.getValue("secsave")

    def saveThings(self) -> None:
        debugLog(f"Automatic saving every {self.saveSecs} secs 😍")
        if not self.parent() or not hasattr(self.parent(), "tabTextEdits"):
            debugLog("Skipped saveThings because attribute \"tabTextEdits\" destroyed! 😰")  # Automatic skip when not have attribute tabTextEdits
            return
        for temp in (getEditor for getEditor in self.parent().tabTextEdits if getEditor is not None):   # UwU I'm lazy, so I tried to use list but my memory is lazy, so I edit to Generator
            debugLog(f"Saving file {temp.nowFilename} ✅")
            temp.autoSave()
        debugLog("Save successfully! ✅")
        debugLog("Waiting for next cycle... 💥")

    def run(self) -> None:
        while self.running:
            for temp in range(self.saveSecs * 10):
                time.sleep(0.1)
                if not self.running:
                    self.saveThings()
                    break
            if self.running:
                self.saveThings()
        debugLog("AutomaticSaveThingsThread ended")
        self.ended = True
        super().quit()

    def quit(self):
        self.running = False
        debugLog("AutomaticSaveThingsThread has closed by this->quit 💥")


class SeperatorWidget(QFrame):
    def __init__(self, parent: QWidget=None):
        super().__init__(parent)
        self.setFrameShape(self.Shape.HLine)
        self.setFrameShadow(self.Shadow.Sunken)
        

class LineNumberWidget(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor
        self.setFixedWidth(40)
        self.setCursor(Qt.CursorShape.IBeamCursor)
        self.borderWidth = 1
        self.borderColor = QColor("#ABABAB")

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setPen(QPen(self.borderColor, self.borderWidth)) # Draw Border at right
        painter.drawLine(self.width() - 1, 0, self.width() - 1, self.height())
        block = self.editor.firstVisibleBlock() # Magic Line
        blockNumber = block.blockNumber()
        top = self.editor.blockBoundingGeometry(block).translated(self.editor.contentOffset()).top()
        bottom = top + self.editor.blockBoundingRect(block).height()
        painter.setPen(self.palette().mid().color())
        font = self.editor.font()
        painter.setFont(font)

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(blockNumber + 1)
                painter.drawText(0, int(top), self.width() - 5, self.editor.fontMetrics().height(),
                                 Qt.AlignmentFlag.AlignRight, number)
            block = block.next()
            top = bottom
            bottom = top + self.editor.blockBoundingRect(block).height()
            blockNumber += 1


class LineShowTextEdit(QPlainTextEdit):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.lineNumberShowWidget = LineNumberWidget(self)
        self.setViewportMargins(40, 0, 0, 0)
        self.blockCountChanged.connect(self.updateLineShowerWidth)
        self.updateRequest.connect(self.updateLineShowerNumbers)
        self.cursorPositionChanged.connect(self.highlightThisLine)
        self.updateLineShowerWidth()
        self.highlightThisLine()

    def updateLineShowerWidth(self):
        digits = len(str(max(1, self.blockCount())))
        space = 10 + self.fontMetrics().horizontalAdvance('9') * digits
        self.setViewportMargins(space, 0, 0, 0)
        self.lineNumberShowWidget.setFixedWidth(space)

    def updateLineShowerNumbers(self, rect, dy):
        if dy:
            self.lineNumberShowWidget.scroll(0, dy)
        else:
            self.lineNumberShowWidget.update(0, rect.y(), self.lineNumberShowWidget.width(), rect.height())

        if rect.contains(self.viewport().rect()):
            self.updateLineShowerWidth()

    def highlightThisLine(self):
        self.lineNumberShowWidget.update()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.lineNumberShowWidget.setGeometry(QRect(cr.left(), cr.top(), self.lineNumberShowWidget.width(), cr.height()))


class SpacingSupportEdit(LineShowTextEdit):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.defineKeywords: list[str] = []
        self.usingCodeControl: bool = False
        self.spacing: int = 4

    def getPosInLine(self) -> int:
        cursor = self.textCursor()
        originalPos: int = cursor.position()
        cursor.movePosition(QTextCursor.MoveOperation.StartOfLine)
        afterPos: int = cursor.position()
        cursor.setPosition(originalPos)
        return originalPos - afterPos

    def getLineNumber(self) -> int:
        cursor = self.textCursor()
        originalPos: int = cursor.position()
        cursor.movePosition(QTextCursor.MoveOperation.Start, QTextCursor.MoveMode.KeepAnchor)
        lineNumber: int = len(cursor.selectedText().splitlines())
        cursor.clearSelection()
        cursor.setPosition(originalPos)
        lineNumber: int = 1 if lineNumber == 0 else lineNumber
        return lineNumber

    def _getBeforeText(self, position: int) -> str:
        cursor = self.textCursor()
        originalPos: int = cursor.position()
        cursor.setPosition(position)
        cursor.movePosition(QTextCursor.MoveOperation.StartOfLine, QTextCursor.MoveMode.KeepAnchor)
        text: str = cursor.selectedText()
        cursor.clearSelection()
        cursor.setPosition(originalPos)
        return text

    def backIndent(self) -> None:
        cursor = self.textCursor()
        originalPos: int = cursor.position()
        if not self._getBeforeText(originalPos).strip() and self.getPosInLine() >= 1:
            inlinePos: int = self.getPosInLine()
            returnPos: int = self.spacing if inlinePos % self.spacing == 0 else self.spacing - (inlinePos % self.spacing)
            cursor.movePosition(QTextCursor.MoveOperation.Left, QTextCursor.MoveMode.KeepAnchor, returnPos)
            cursor.removeSelectedText()
            cursor.clearSelection()
            cursor.setPosition(originalPos - returnPos)

    def _multilineIndent(self, back: bool = False) -> None:
        cursor = self.textCursor()
        selectionStart: int = cursor.selectionStart()
        originalPos: int = cursor.position()
        text: list[str] = cursor.selectedText().splitlines()
        after: list[str] = []
        for temp in text:
            space: int = len(temp) - len(temp.lstrip())
            if back:
                oneSpace: int = space % self.spacing if space % self.spacing else self.spacing
                backSpacing: int = space - oneSpace
                after.append(f"{backSpacing * " "}{temp[space:]}")
            else:
                spacing: int = self.spacing if space % self.spacing == 0 else space % self.spacing
                after.append(f"{spacing * " "}{temp}")
        answer: str = "\n".join(after)
        cursor.removeSelectedText()
        cursor.setPosition(selectionStart)
        cursor.insertText(answer)
        cursor.setPosition(selectionStart)
        cursor.movePosition(QTextCursor.MoveOperation.Right, QTextCursor.MoveMode.KeepAnchor, len(answer))
        self.setTextCursor(cursor)

    def _thisLineContent(self, position: int) -> str:
        cursor = self.textCursor()
        cursor.setPosition(position)
        cursor.movePosition(QTextCursor.MoveOperation.StartOfLine)
        cursor.movePosition(QTextCursor.MoveOperation.EndOfLine, QTextCursor.MoveMode.KeepAnchor)
        getText: str = cursor.selectedText()
        cursor.clearSelection()
        cursor.setPosition(position)
        return getText

    def keyPressEvent(self, event: QKeyEvent) -> None:
        # Rewrite keyPressEvent, AI Generate? Unuse!
        if event.key() == Qt.Key.Key_Backtab:
            # Same as Backspace
            cursor = self.textCursor()
            if len(cursor.selectedText()) > 0:
                self._multilineIndent(True)
            else:
                self.backIndent()
            return
        elif event.key() == Qt.Key.Key_Tab:
            cursor = self.textCursor()
            originalPos: int = cursor.position()
            if len(cursor.selectedText()) > 0:
                self._multilineIndent()
                return
            else:
                posInLine: int = self.getPosInLine()
                spacing: int = self.spacing if posInLine % self.spacing == 0 else self.spacing - (posInLine % self.spacing)
                cursor.insertText(" " * spacing)
                cursor.setPosition(originalPos + spacing)
                return
        elif event.key() == Qt.Key.Key_Return:
            cursor = self.textCursor()
            originalPos: int = cursor.position()
            content: str = self._thisLineContent(cursor.position())
            lineSpace: int = len(content) - len(content.lstrip())
            cursor.insertText("\n")
            cursor.insertText(" " * lineSpace)
            cursor.setPosition(originalPos + lineSpace + 1)
            self.setTextCursor(cursor)
            return
        elif event.text() in [i[0] for i in self.defineKeywords] or event.text() in ["(","[","{"]:
            super().keyPressEvent(event)
            cursor = self.textCursor()
            normals: list = ["()","[]","{}"]
            if event.text() in [i[0] for i in self.defineKeywords]:
                cursor.insertText([i[1] for i in self.defineKeywords][[i[0] for i in self.defineKeywords].index(event.text())])
            elif event.text() in [i[0] for i in normals]:
                cursor.insertText([i[1] for i in normals][[i[0] for i in normals].index(event.text())])
            else:
                return
            cursor.movePosition(QTextCursor.MoveOperation.Left)
            self.setTextCursor(cursor)
            return
        elif event.key() == Qt.Key.Key_Backspace:
            cursor = self.textCursor()
            originalPos = cursor.position()
            if cursor.hasSelection():
                cursor.removeSelectedText()
                return
            if cursor.position() > 0:
                if self.getPosInLine() >= self.spacing:
                    self.backIndent()
                    if self.textCursor().position() != originalPos:
                        return
                if self.getPosInLine() >= 1:
                    cursor.movePosition(QTextCursor.MoveOperation.Left, QTextCursor.MoveMode.KeepAnchor)
                    left: str = cursor.selectedText()
                    cursor.clearSelection()
                    cursor.setPosition(originalPos)
                    cursor.movePosition(QTextCursor.MoveOperation.Right, QTextCursor.MoveMode.KeepAnchor)
                    right: str = cursor.selectedText()
                    cursor.clearSelection()

                    if f"{left}{right}" in self.defineKeywords or f"{left}{right}" in ["()", "[]", "{}"]:
                        cursor.movePosition(QTextCursor.MoveOperation.Left)
                        cursor.movePosition(QTextCursor.MoveOperation.Right, QTextCursor.MoveMode.KeepAnchor, 2)
                        cursor.removeSelectedText()
                        cursor.setPosition(originalPos - 1)
                    else:
                        super().keyPressEvent(event)
                        return
                else:
                    super().keyPressEvent(event)
                    return
            else:
                super().keyPressEvent(event)
                return

        super().keyPressEvent(event)


class SinotePlainTextEdit(SpacingSupportEdit):
    def __init__(self):
        super().__init__()
        self.setFilename = None
        self.nowFilename: str | None = None
        self.plName: str | None = None
        self.finalEncoding: str | None = None
        self.num: int = -1
        self.setStyleSheet(f"{self.styleSheet()}border: none;")

    def autoSave(self):
        if self.nowFilename:
            debugLog(f"Automatic saving file {self.nowFilename}")
            with open(self.nowFilename, "w+", encoding="utf-8") as f:
                f.write(self.toPlainText())
            debugLog(f"Successfully to save file {self.nowFilename}")

    def clear(self):
        if self.setFilename is not None:
            self.setFilename(self.num, loadJson("EditorUI")["editor.tab.tab_name_unsaved"].format(self.nowFilename))
        self.finalEncoding = None
        self.plName = None
        self.nowFilename = None
        super().clear()

    def newFile(self):
        self.clear()
        if self.setFilename is not None:
            self.setFilename(self.num, loadJson("EditorUI")["editor.tab.new_file"])
        self.nowFilename = None

    def undo(self):
        if self.setFilename is not None:
            self.setFilename(self.num, loadJson("EditorUI")["editor.tab.tab_name_unsaved"].format(self.nowFilename))
        super().undo()

    def redo(self):
        if self.setFilename is not None:
            self.setFilename(self.num, loadJson("EditorUI")["editor.tab.tab_name_unsaved"].format(self.nowFilename))
        super().redo()

    def paste(self):
        if self.setFilename is not None:
            self.setFilename(self.num, loadJson("EditorUI")["editor.tab.tab_name_unsaved"].format(self.nowFilename))
        super().paste()

    class _LoadHighlighter(QThread):
        foundHighlighter = Signal(LoadPluginBase.LazyCustomizeSyntaxHighlighter)
        setPairKeywords = Signal(list)
        noSyntax = Signal()
        test = Signal()

        def __init__(self, appendix: str):
            super().__init__()
            self.appendix = appendix

        def run(self) -> None:
            global syntaxHighlighter
            debugLog(f"Finding Highlighter (*.{self.appendix})... (THREAD) 🔎")
            temp: LoadPluginBase.CustomizeSyntaxHighlighter | None = None
            temp2, temp3 = None, None
            name: str | None = None
            for k, i in syntaxHighlighter.items():
                if self.appendix in i[1]:
                    debugLog(f"{self.appendix} is in {i[1]}, successfully to find! ✅")
                    temp = i[0]
                    temp2 = i[2]
                    temp3 = i[3]
                    name = k.strip()
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
        debugLog("Setting another Highlighter..." if highlighter else "Cleaning Highlighter...")
        self.highlighter = highlighter.getObject() if highlighter is not None else LoadPluginBase.CustomizeSyntaxHighlighter([[] for i in range(7)])
        self.highlighter.setDocument(self.document())

    def setFileAppendix(self, fileAppendix: str) -> None:
        debugLog(f"Attempting to set file appendix to {fileAppendix} 🪲")
        debugLog(f"Finding Children of Document and remove Highlighter")
        for i in self.findChildren(LoadPluginBase.CustomizeSyntaxHighlighter):
            i.setDocument(None)
            i.deleteLater()
        debugLog("Successfully remove Highlighter ✅")
        debugLog("Searching Highlighter 🔎")
        self.temp = self._LoadHighlighter(fileAppendix)
        self.temp.foundHighlighter.connect(lambda a: self.setHighlighter(a), Qt.ConnectionType.SingleShotConnection)
        self.temp.setPairKeywords.connect(lambda a: self._setPairKeywords(a), Qt.ConnectionType.QueuedConnection)
        self.temp.noSyntax.connect(self._setNoSyntax, Qt.ConnectionType.QueuedConnection)
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
        addLog(0, f"Attempting to read file {filename}...", "SinoteUserInterfaceActivity")
        if not Path(filename).exists():
            addLog(1, f"Cannot find file {filename}, current file will save.","SinoteUserInterfaceActivity")
        if not Path(filename).is_file():
            addLog(1, f"Are you sure you using a normal file? Cannot read {filename}!", "SinoteUserInterfaceActivity")
        # Try different encodings and support Chinese(GBK/GB2312)
        encodings = ["utf-8", "utf-16", "gbk", "gb2312", "latin-1", "windows-1252", "utf-32", "ascii"]
        content: str | None = None
        
        for encoding in encodings:
            try:
                debugLog(f"Trying reading with encoding {encoding.upper()} 🤔")
                with open(filename, "r", encoding=encoding) as f:
                    content = f.read()
                    self.finalEncoding = encoding.upper()
                    debugLog(f"Successfully to read {filename} with {encoding} encoding! {len(content) / 8 / 1024:.2f}KiB {len(content.splitlines())} lines")
                break
            except UnicodeDecodeError or LookupError:
                debugLog(f"Failed to read with encoding {encoding.upper()} 💀")
                continue
            except PermissionError:
                addLog(2, f"Cannot read file {filename}. Permission Denied!", "SinoteUserInterfaceActivity")
                break
            except IOError:
                addLog(2, f"Cannot read file {filename}. IOError at Python!", "SinoteUserInterfaceActivity")
                break
            except Exception as e:
                addLog(1, f"Failed to read {filename} with {encoding}: {repr(e)}", "SinoteUserInterfaceActivity")
                continue
        if content is not None:
            self.setPlainText(content)
            self.setFileAppendix(Path(filename).suffix[1:])
            if self.setFilename is not None:
                self.setFilename(self.num, loadJson("EditorUI")["editor.tab.tab_name"].format(Path(filename).name))
            self.nowFilename = str(Path(filename))
            addLog(0, f"Successfully to read file {filename} using {self.finalEncoding} encoding! ✅", "SinoteUserInterfaceActivity")
        else:
            addLog(2, f"Cannot read file {filename}. Tried all encodings but failed! Or other Exception out! ❌", "SinoteUserInterfaceActivity")
            w = QMessageBox(None, loadJson("MessageBox")["msgbox.title.error"], loadJson("MessageBox")["msgbox.error.fileCannotRead"], buttons=QMessageBox.StandardButton.Ok)
            w.exec()


class SettingObject(QWidget):
    def __init__(self, parent: QWidget = None, text: str = "Unknown Text", desc: str = "Unknown Description"):
        super().__init__(parent)
        self.mainLayout: QHBoxLayout = QHBoxLayout(self)
        self.mainLayout.setContentsMargins(15, 10, 15, 10)
        self.mainLayout.setSpacing(20)
        self.leftLayout: QVBoxLayout = QVBoxLayout()
        self.leftLayout.setSpacing(5)
        self.titleLabel: QLabel = QLabel(text)
        self.titleLabel.setStyleSheet("font-size: 14pt; font-weight: bold;")
        self.leftLayout.addWidget(self.titleLabel)
        self.descLabel: QLabel = QLabel(desc)
        self.descLabel.setStyleSheet("font-size: 10pt; color: gray;")
        self.descLabel.setWordWrap(True)
        self.leftLayout.addWidget(self.descLabel)
        self.leftLayout.addStretch()
        self.rightWidget: QWidget | None = None
        self.mainLayout.addLayout(self.leftLayout, 3)
        self.mainLayout.addStretch(1)
        self.setMinimumHeight(80)
    
    def setText(self, text: str) -> None:
        self.titleLabel.setText(text)
    
    def setDesc(self, desc: str) -> None:
        self.descLabel.setText(desc)
    
    def setRightWidget(self, widget: QWidget) -> None:
        if self.rightWidget is not None:
            self.mainLayout.removeWidget(self.rightWidget)
            self.rightWidget.deleteLater()
        self.rightWidget = widget
        self.rightWidget.setMinimumWidth(200)
        self.rightWidget.setMaximumWidth(400)
        self.mainLayout.addWidget(self.rightWidget, 2)
    
    def getRightWidget(self) -> QWidget | None:
        return self.rightWidget


class ComboBoxSettingObject(SettingObject):
    def __init__(self, parent: QWidget = None, text: str = "Unknown Text", desc: str = "Unknown Description"):
        super().__init__(parent, text, desc)
        self.comboBox = QComboBox()
        self.setRightWidget(self.comboBox)

    def useNormalBox(self):
        self.comboBox.deleteLater()
        self.comboBox = QComboBox()
        self.setRightWidget(self.comboBox)

    def useFontBox(self):
        self.comboBox.deleteLater()
        self.comboBox = QFontComboBox()
        self.setRightWidget(self.comboBox)

class LineEditSettingObject(SettingObject):
    def __init__(self, parent: QWidget = None, text: str = "Unknown Text", desc: str = "Unknown Description"):
        super().__init__(parent, text, desc)
        self.lineEdit = QLineEdit()
        self.setRightWidget(self.lineEdit)

    def useNormalEdit(self):
        self.lineEdit.deleteLater()
        self.lineEdit = QLineEdit()
        self.setRightWidget(self.lineEdit)

    def useSpinBox(self):
        self.lineEdit.deleteLater()
        self.lineEdit = QSpinBox()
        self.setRightWidget(self.lineEdit)


class PluginInfoLister(QTextEdit):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.setStyleSheet(f"{self.styleSheet()} border: none;")
        self.setReadOnly(True)

    def setInformation(self, info: list[Any]) -> None:
        self.clear()
        self.setHtml(f"""
<img src="{info[0]}">
<br><h1>{info[1]}</h1>
<h3>{info[2]}</h3>
<p>{loadJson("EditorUI")["editor.any.version"]}: {info[3]}</p>
<p>{loadJson("EditorUI")["editor.any.author"]}: {info[4]}</p>
<p>{loadJson("EditorUI")["editor.any.description"]}: <br>{info[5].replace("\\n", "<br>")}</p>
""")


class CheckBoxSettingObject(SettingObject):
    def __init__(self, parent: QWidget = None, text: str = "Unknown Text", desc: str = "Unknown Description"):
        super().__init__(parent, text, desc)
        self.checkBox = QCheckBox()
        self.setRightWidget(self.checkBox)


class SplashScreen(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowFlag(Qt.WindowType.SplashScreen)
        self.setMinimumWidth(500)
        self.layout_: QVBoxLayout = QVBoxLayout()
        self.image = QLabel()
        self.loadedPlugin: int = 0
        self.totals: int = 0
        self.setStyleSheet("background-color:white;color:black;")
        self.nowLoading: str = "IDLE"
        self.pixmap = QPixmap("./resources/icon.png").scaled(QSize(256, 256))
        self.image.setPixmap(self.pixmap)
        self.label = QLabel()
        self.label.setStyleSheet("text-align: center;")
        self.label.setText(loadJson("LoadingScreen")["loading.text.loadplugin"].format("IDLE", "0", "Summing..."))
        self.layout_.addWidget(self.image, 1, Qt.AlignmentFlag.AlignHCenter)
        self.layout_.addWidget(self.label, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.setLayout(self.layout_)

    def setTotal(self, total: int):
        self.totals = total
        self.label.setText(loadJson("LoadingScreen")["loading.text.loadplugin"].format(self.nowLoading, "0", total))
        self.repaint()

    def setPluginName(self, name:str):
        self.nowLoading = name
        self.label.setText(
            loadJson("LoadingScreen")["loading.text.loadplugin"].format(self.nowLoading, self.loadedPlugin,
                                                                        self.totals))
        self.repaint()

    def addOne(self):
        self.loadedPlugin += 1
        self.label.setText(loadJson("LoadingScreen")["loading.text.loadplugin"].format(self.nowLoading, self.loadedPlugin, self.totals))
        self.repaint()

    def finishedPluginLoad(self):
        self.label.setText(loadJson("LoadingScreen")["loading.text.loadfont"])
        self.repaint()


class MainWindow(QMainWindow):
    themeChanged: Signal = Signal()

    def __init__(self):
        super().__init__()
        self.widget = QStackedWidget()
        self.mainFrame = QWidget()
        self.settingFrame = QWidget()
        self.editorThread = AutomaticSaveThingsThread(self, settingObject.getValue("secsave"))
        self.setWindowIcon(QIcon("./resources/icon.png"))
        self.setCentralWidget(self.widget)
        self._initBase()
        self._setupUI()
        self._setupTab()
        self._automaticSetTheme()
        self._autoApplyPluginInfo()

    def _setupTab(self):
        if len(settingObject.getValue("beforeread")) or len(fileargs) > 0:
            for temp in settingObject.getValue("beforeread"):
                if not Path(temp).exists():
                    self._createRecommendFile()
                    self.tabTextEdits[len(self.tabTextEdits) - 1].setPlainText(
                        loadJson("EditorUI")["editor.any.cannotreadfile"].format(temp))
                else:
                    self.createTab(temp)
            for temp in [str(Path(i)) for i in fileargs]:
                if Path(temp).exists():
                    self.createTab(temp)
                else:
                    self._createRecommendFile()
                    self.tabTextEdits[len(self.tabTextEdits) - 1].setPlainText(
                        loadJson("EditorUI")["editor.any.cannotreadfile2"].format(temp))
            settingObject.setValue("beforeread", [i for i in settingObject.getValue("beforeread") if Path(i).exists()])
        else:
            self._createRecommendFile()

    def _setupUI(self):
        debugLog("Setting up User Interface...")
        debugLog("Setting up Text Edit Area...")
        self.textEditArea = QTabWidget()
        self.addTabButton = QPushButton("+")
        self.addTabButton.setFlat(True)
        self.addTabButton.clicked.connect(self._createRecommendFile)
        self.textEditArea.setCornerWidget(self.addTabButton, Qt.Corner.TopRightCorner)
        self.tabTextEdits: list[SinotePlainTextEdit | None] = []
        self.textEditArea.tabBar().setMaximumHeight(60)
        self.textEditArea.setTabsClosable(True)
        self.textEditArea.setMovable(True)
        self.textEditArea.tabCloseRequested.connect(self._requestClose)
        debugLog("Successfully to set up Text Edit Area!")
        debugLog("Setting up Layout...")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.addWidget(self.textEditArea)
        self.horizontalLayout.setStretch(0, 1)
        self.mainFrame.setLayout(self.horizontalLayout)
        debugLog("Successfully to set up Layout!")
        debugLog("Setting up Menu...")
        self.fileEditMenu = QMenuBar()
        self.fileEditMenu.fileEdit = QMenu(loadJson("EditorUI")["editor.menu.files"])
        # Actions Define
        createFile = QAction(loadJson("EditorUI")["editor.menu.files.newfile"], self)
        createFile.triggered.connect(lambda: self.textEditArea.currentWidget().newFile())
        openFile = QAction(loadJson("EditorUI")["editor.menu.temps.openfile"], self)
        openFile.triggered.connect(self.tempOpenFile)
        saveAs = QAction(loadJson("EditorUI")["editor.menu.files.saveas"], self)
        saveAs.triggered.connect(self.saveAs)
        setting = QAction(loadJson("EditorUI")["editor.menu.files.settings"], self)
        setting.triggered.connect(partial(self.widget.setCurrentIndex, 1))
        exitProg = QAction(loadJson("EditorUI")["editor.menu.files.exit"], self)
        exitProg.triggered.connect(self.close)
        self.fileEditMenu.fileEdit.addActions([createFile, openFile, saveAs, setting, exitProg])
        self.fileEditMenu.addMenu(self.fileEditMenu.fileEdit)
        self.setMenuBar(self.fileEditMenu)
        debugLog("Successfully to set up Menu!")
        debugLog("Setting up Setting Area...")
        self.backToMain = QPushButton("<")
        self.backToMain.setStyleSheet(f"{self.backToMain.styleSheet()}background-color: none; border: none;")
        self.backToMain.clicked.connect(partial(self.widget.setCurrentIndex, 0))
        self.backToMain.setMaximumWidth(50)
        self.setArea = QTabWidget()
        self.setArea.setMovable(False)
        self.setArea.setTabsClosable(False)
        # Appearance Setting
        self.setArea.appearance = QScrollArea()
        self.setArea.appearance.vLayout = QVBoxLayout()
        self.setArea.appearance.titleAppearance = QLabel(loadJson("EditorUI")["editor.title.settings.appearance"])
        self.setArea.appearance.titleAppearance.setStyleSheet(
            "font-size: 38px; font-weight: bold; margin-bottom: 10px;")  # QSS
        self.setArea.appearance.seperator = SeperatorWidget()
        self.setArea.appearance.debugMode = CheckBoxSettingObject(None,
                                                                  loadJson("EditorUI")["editor.title.setobj.debugmode"],
                                                                  loadJson("EditorUI")["editor.desc.setobj.debugmode"])
        self.setArea.appearance.debugMode.checkBox.setText(loadJson("EditorUI")["editor.desc.setobj.debugmodeopen"])
        self.setArea.appearance.debugMode.checkBox.setChecked(settingObject.getValue("debugmode"))
        self.setArea.appearance.debugMode.checkBox.checkStateChanged.connect(
            lambda: settingObject.setValue("debugmode", self.setArea.appearance.debugMode.checkBox.isChecked()))
        self.setArea.appearance.language = ComboBoxSettingObject(None,
                                                                 loadJson("EditorUI")["editor.title.setobj.language"],
                                                                 loadJson("EditorUI")["editor.desc.setobj.language"])
        self.setArea.appearance.language.comboBox.addItems([i for _, i in basicInfo["item.dict.language_for"].items()])
        try:
            self.setArea.appearance.language.comboBox.setCurrentIndex(
                list(basicInfo["item.dict.language_for"].keys()).index(lang))
        except Exception:
            self.setArea.appearance.language.comboBox.setCurrentIndex(0)
        self.setArea.appearance.language.comboBox.currentIndexChanged.connect(lambda: {
            settingObject.setValue("language", list(basicInfo["item.dict.language_for"].keys())[
                self.setArea.appearance.language.comboBox.currentIndex()]),
            QMessageBox(QMessageBox.Icon.Information, loadJson("MessageBox")["msgbox.title.info"],
                        loadJson("MessageBox")["msgbox.info.restartApplySet"], buttons=QMessageBox.StandardButton.Ok,
                        parent=self).exec()
        })
        self.setArea.appearance.theme = ComboBoxSettingObject(None, loadJson("EditorUI")["editor.title.setobj.theme"],
                                                              loadJson("EditorUI")["editor.desc.setobj.theme"])
        self.setArea.appearance.theme.comboBox.addItems(
            [loadJson("EditorUI")[i] for i in [f"editor.any.{k}" for k in ["light", "dark"]]])
        self.setArea.appearance.theme.comboBox.setCurrentIndex(
            settingObject.getValue("theme") if settingObject.getValue("theme") < 2 else 0)
        self.setArea.appearance.theme.comboBox.currentIndexChanged.connect(
            lambda: self.setTheme(self.setArea.appearance.theme.comboBox.currentIndex()))
        self.setArea.appearance.vLayout.addWidget(self.setArea.appearance.titleAppearance)
        self.setArea.appearance.vLayout.addWidget(self.setArea.appearance.seperator)
        self.setArea.appearance.vLayout.addWidget(self.setArea.appearance.debugMode)
        self.setArea.appearance.vLayout.addWidget(self.setArea.appearance.language)
        self.setArea.appearance.vLayout.addWidget(self.setArea.appearance.theme)
        self.setArea.appearance.vLayout.addStretch(1)
        self.setArea.appearance.setLayout(self.setArea.appearance.vLayout)
        self.setArea.addTab(self.setArea.appearance, loadJson("EditorUI")["editor.tab.settings.appearance"])
        # Plugin Setting
        self.setArea.plugins = QScrollArea()
        self.setArea.plugins.vLayout = QVBoxLayout()
        self.setArea.plugins.titlePlugins = QLabel(loadJson("EditorUI")["editor.title.settings.plugin"])
        self.setArea.plugins.titlePlugins.setStyleSheet(
            "font-size: 38px; font-weight: bold; margin-bottom: 10px;")  # Also QSS
        self.setArea.plugins.seperator = SeperatorWidget()
        self.pluginInfo: list[list[Any]] = []
        self.setArea.plugins.set = QWidget()
        self.setArea.plugins.set.hLayout = QHBoxLayout()
        self.setArea.plugins.set.listWidget = QListWidget()
        self.setArea.plugins.set.listWidget.setStyleSheet(
            f"{self.setArea.plugins.set.listWidget.styleSheet()} QListWidget::item::selected {r"{ background-color: lightblue; }"}")
        self.setArea.plugins.set.information = PluginInfoLister()
        self.setArea.plugins.set.listWidget.currentTextChanged.connect(lambda: {
            self.setArea.plugins.set.information.setInformation(
                ["null" for i in range(7)] if len(self.pluginInfo) == 0 else self.pluginInfo[
                    self.setArea.plugins.set.listWidget.currentRow()])
        })
        self.setArea.plugins.set.listWidget.itemDoubleClicked.connect(lambda: {
            self.setThisPluginAnotherType(self.setArea.plugins.set.listWidget.currentItem())
        })
        self.setArea.plugins.set.hLayout.addWidget(self.setArea.plugins.set.listWidget, stretch=1)
        self.setArea.plugins.set.hLayout.addWidget(self.setArea.plugins.set.information, stretch=2)
        self.setArea.plugins.set.setLayout(self.setArea.plugins.set.hLayout)
        self.setArea.plugins.vLayout.addWidget(self.setArea.plugins.titlePlugins)
        self.setArea.plugins.vLayout.addWidget(self.setArea.plugins.seperator)
        self.setArea.plugins.vLayout.addWidget(self.setArea.plugins.set, 1)
        self.setArea.plugins.setLayout(self.setArea.plugins.vLayout)
        self.setArea.addTab(self.setArea.plugins, loadJson("EditorUI")["editor.tab.settings.plugin"])
        # Editor Font Setting
        self.setArea.edfont = QScrollArea()
        self.setArea.edfont.vLayout = QVBoxLayout()
        self.setArea.edfont.titleEditorFont = QLabel(loadJson("EditorUI")["editor.tab.settings.editorfont"])
        self.setArea.edfont.titleEditorFont.setStyleSheet("font-size: 38px; font-weight: bold; margin-bottom: 10px;")
        self.setArea.edfont.seperator = SeperatorWidget()
        self.setArea.edfont.fontSelect = ComboBoxSettingObject(None, loadJson("EditorUI")["editor.title.setobj.fontname"], loadJson("EditorUI")["editor.desc.setobj.fontname"])
        self.setArea.edfont.fontSelect.useFontBox()
        self.setArea.edfont.fontSelect.comboBox.setCurrentFont(QFont(settingObject.getValue("fontName")))
        self.setArea.edfont.fontSelect.comboBox.currentFontChanged.connect(lambda: self.applyFont(fontName=self.setArea.edfont.fontSelect.comboBox.currentFont().family()))
        self.setArea.edfont.fontSize = LineEditSettingObject(None, loadJson("EditorUI")["editor.title.setobj.fontsize"], loadJson("EditorUI")["editor.desc.setobj.fontsize"])
        self.setArea.edfont.fontSize.useSpinBox()
        self.setArea.edfont.fontSize.lineEdit.setMinimum(1)
        self.setArea.edfont.fontSize.lineEdit.setMaximum(99)
        self.setArea.edfont.fontSize.lineEdit.setValue(settingObject.getValue("fontSize"))
        self.setArea.edfont.fontSize.lineEdit.textChanged.connect(lambda: self.applyFont(fontSize=self.setArea.edfont.fontSize.lineEdit.value()))
        self.setArea.edfont.fontSize.lineEdit.setSuffix(loadJson("EditorUI")["editor.suffix.settings.size"])
        self.setArea.edfont.fallbackSelect = ComboBoxSettingObject(None, loadJson("EditorUI")["editor.title.setobj.fbfont"], loadJson("EditorUI")["editor.desc.setobj.fbfont"])
        self.setArea.edfont.fallbackSelect.useFontBox()
        self.setArea.edfont.fallbackSelect.comboBox.currentFontChanged.connect(lambda: self.applyFont(fallbackFont=self.setArea.edfont.fallbackSelect.comboBox.currentFont().family()))
        if settingObject.getValue("fallbackFont"):
            self.setArea.edfont.fallbackSelect.comboBox.setCurrentFont(QFont(settingObject.getValue("fallbackFont")))
        else:
            self.setArea.edfont.fallbackSelect.comboBox.setCurrentFont(QFont("MiSans VF"))
        self.setArea.edfont.useFallbackFont = CheckBoxSettingObject(None, loadJson("EditorUI")["editor.title.setobj.usefbfont"], loadJson("EditorUI")["editor.desc.setobj.usefbfont"])
        self.setArea.edfont.useFallbackFont.checkBox.setText(loadJson("EditorUI")["editor.desc.setobj.usefbfontopen"])
        self.setArea.edfont.useFallbackFont.checkBox.checkStateChanged.connect(lambda: {
            settingObject.setValue("useFallback", self.setArea.edfont.useFallbackFont.checkBox.isChecked()),
            self.setArea.edfont.fallbackSelect.setDisabled(not self.setArea.edfont.useFallbackFont.checkBox.isChecked()),
            self.applySettings()
        })
        self.setArea.edfont.useFallbackFont.checkBox.setChecked(settingObject.getValue("useFallback"))
        self.setArea.edfont.vLayout.addWidget(self.setArea.edfont.titleEditorFont)
        self.setArea.edfont.vLayout.addWidget(self.setArea.edfont.seperator)
        self.setArea.edfont.vLayout.addWidget(self.setArea.edfont.fontSelect)
        self.setArea.edfont.vLayout.addWidget(self.setArea.edfont.fontSize)
        self.setArea.edfont.vLayout.addWidget(self.setArea.edfont.useFallbackFont)
        self.setArea.edfont.vLayout.addWidget(self.setArea.edfont.fallbackSelect)
        self.setArea.edfont.vLayout.addStretch(1)
        self.setArea.edfont.setLayout(self.setArea.edfont.vLayout)
        self.setArea.addTab(self.setArea.edfont, loadJson("EditorUI")["editor.tab.settings.editorfont"])
        self.setVerticalLayout = QVBoxLayout()
        self.setVerticalLayout.addWidget(self.backToMain)
        self.setVerticalLayout.addWidget(self.setArea)
        self.settingFrame.setLayout(self.setVerticalLayout)
        debugLog("Successfully to set up Setting Area...")
        debugLog("Adding Frames to StackedWidget...")
        self.widget.addWidget(self.mainFrame)
        self.widget.addWidget(self.settingFrame)
        self.widget.setCurrentIndex(0)
        self.editorThread.start()
        debugLog("Successfully to add frame!")
        debugLog("Successfully to set up User Interface!")

    def setThisPluginAnotherType(self, item: QListWidgetItem) -> None:
        objectName: str = item.objName
        name: str = item.name
        if objectName in settingObject.getValue("disableplugin"):
            item.setText(name)
            disabledPlugin: list[str] = settingObject.getValue("disableplugin")
            disabledPlugin.remove(objectName)
            settingObject.setValue("disableplugin", disabledPlugin)
        else:
            item.setText(f"[X] {name}")
            disabledPlugin: list[str] = settingObject.getValue("disableplugin")
            disabledPlugin.append(objectName)
            settingObject.setValue("disableplugin", disabledPlugin)

    def _autoApplyPluginInfo(self) -> None:
        self.pluginInfo.clear()
        self.setArea.plugins.set.listWidget.clear()
        for key, word in loadedPlugin.items():
            debugLog(f"Applying Plugin Info... Current: {key} 😁")
            icon: QPixmap = QPixmap("./resources/images/plugins.png" if word["icon"] is None or not Path(word["icon"]).exists() else word["icon"])
            name: str = word["name"]
            objectName: str = word["objectName"]
            version: str = word["version"]
            author: str = ", ".join(word["author"])
            desc: str = word["description"]
            self.pluginInfo.append(["./resources/images/plugins.png" if word["icon"] is None or not Path(word["icon"]).exists() else word["icon"], name, objectName, version, author, desc])
            item: QListWidgetItem = QListWidgetItem(icon, name if objectName not in settingObject.getValue("disableplugin") else f"[X] {name}")
            item.objName = objectName
            item.name = name
            self.setArea.plugins.set.listWidget.addItem(item)
        self.setArea.plugins.set.listWidget.setCurrentRow(0)

    def setTheme(self, theme: int = 0) -> None:
        """
        Set theme (0 for light, 1 for dark)
        :param theme: Theme number
        :return: NoneType
        """
        if not "--no-theme" in args and not "-nt" in args:
            apply_stylesheet(application, "light_blue.xml" if not theme else "dark_blue.xml")
            settingObject.setValue("theme", theme)
            self.applySettings()
            self.themeChanged.emit()

    def _automaticSetTheme(self) -> None:
        apply_stylesheet(application, "light_blue.xml" if not settingObject.getValue("theme") else "dark_blue.xml")

    def applyFont(self, fontName: str = None, fontSize: int = None, fallbackFont: str = None) -> None:
        if fontName:
            settingObject.setValue("fontName", fontName)
        if fontSize:
            settingObject.setValue("fontSize", fontSize)
        if fallbackFont:
            settingObject.setValue("fallbackFont", fallbackFont)
        self.applySettings()

    def show(self) -> None:
        global beforeDatetime
        debugLog("Showing Application...")
        super().show()
        addLog(0, f"Used {(datetime.now() - beforeDatetime).total_seconds():.2f}s to load!", "SinoteUserInterfaceActivity", True)
        debugLog("Show Application Successfully!")
        del beforeDatetime

    def closeEvent(self, event: QCloseEvent) -> None:
        debugLog("CloseEvent triggered 🤓")
        self.close()
        event.accept()

    def close(self) -> None:
        debugLog("Saving session...")
        settingObject.setValue("beforeread", [(i.nowFilename if system().lower() != "windows" else i.nowFilename.replace("/","\\"))
                                              for i in [i for i in self.tabTextEdits if hasattr(i, "nowFilename")] if
                                              (i.nowFilename is not None and Path(i.nowFilename).exists())])
        debugLog("Saved session!")
        debugLog("Attempting to close 🤓")
        self.hide()
        self.editorThread.quit()
        self.editorThread.wait()
        debugLog("Successfully to close ✅")
        super().close()
        application.quit()

    def tempOpenFile(self) -> None:
        """
        This method will be replaced by openProject
        :return: None
        """
        get, _ = QFileDialog.getOpenFileName(self, loadJson("EditorUI")["editor.window.temps.openfile"], filter = "All File (*)")
        if get:
            debugLog(f"Get FileDialog return Information: {get} ✅")
            debugLog("Saving changes... 🪲")
            self.textEditArea.currentWidget().autoSave()
            debugLog("Save changes successfully! ✅")
            self.textEditArea.currentWidget().readFile(get)

    def saveAs(self) -> None:
        get, _ = QFileDialog.getSaveFileName(self, loadJson("EditorUI")["editor.window.temps.saveas"], filter = "All File (*)")
        if get:
            debugLog(f"Get FileDialog return Information: {get} 😍")
            with open(get, "w+", encoding="utf-8") as f:
                f.write(self.textEditArea.currentWidget().toPlainText())
            debugLog(f"Successfully to save! ✅")

    def _requestClose(self, index: int):
        if index >= 0 and index < len(self.tabTextEdits):
            self.tabTextEdits[index] = None
            self.textEditArea.removeTab(index)
            if self.textEditArea.tabBar().count() == 0:
                self.close()

    def _createRecommendFile(self):
        self.createTab()

    def createTab(self, filename: str | None = None):
        debugLog(f"Creating Tab... Will load file: {filename if filename else "Nothing"} 🤓")
        oldDatetime = datetime.now()
        temp = SinotePlainTextEdit()
        temp.num = len(self.tabTextEdits)
        if not Path(filename if filename else "").exists():
            filename = None
        if filename:
            temp.readFile(filename)
        self.tabTextEdits.append(temp)
        self.textEditArea.addTab(temp, loadJson("EditorUI")["editor.tab.new_file"] if not filename else str(Path(filename)))
        temp.setFilename = self.textEditArea.tabBar().setTabText
        self.textEditArea.setCurrentIndex(len(self.tabTextEdits)-1)
        debugLog(f"Successfully to create tab! Used: {(datetime.now() - oldDatetime).total_seconds():.2f}s ✅")
        debugLog("Attempting to update setting... 😍")
        self.applySettings()
        debugLog("Successfully to update setting! ✅")

    def applySettings(self):
        fontSize: int = settingObject.getValue("fontSize")
        fontName: str = settingObject.getValue("fontName")
        fallbackFont: str = settingObject.getValue("fallbackFont")
        fallBack: bool = settingObject.getValue("useFallback")
        debugLog(f"Font Size: {fontSize}, Font Name: {fontName}, Fallback Font: {fallbackFont} 😍")
        for tab, temp in enumerate(self.tabTextEdits, 1):
            if temp:
                debugLog(f"Setting tab {tab}... 🤔")
                temporary = QFont(fontName, fontSize)
                if fallBack:
                    temporary = QFont(fallbackFont, fontSize)
                    temp.setStyleSheet(
                        f"{temp.styleSheet()} font-family:\"{fontName}\", \"{fallbackFont}\"; font-size: {fontSize}pt;")
                else:
                    temp.setStyleSheet(
                        f"{temp.styleSheet()} font-family: {fontName}; font-size: {fontSize}pt;")
                temp.setFont(temporary)
        debugLog("Successfully to set tab! ✅")

    def _initBase(self):
        debugLog("Initializing Base Window... 🔎")
        self.setWindowTitle("Sinote")
        self.resize(1280, 760)
        debugLog("Successfully to initialize ✅")

def setGlobalUIFont() -> None:
    debugLog("Setting global UI font to MiSans... 🎨")
    selectedFont = "MiSans VF"      # Customize!
    globalFont = QFont(selectedFont)
    globalFont.setPointSize(10)
    globalFont.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
    application.setFont(globalFont)
    application.setStyleSheet(f"""
        {application.styleSheet()}
        * {{
            font-family: "{selectedFont}";
        }}
        QWidget {{
            font-family: "{selectedFont}";
        }}
        QLabel {{
            font-family: "{selectedFont}";
        }}
        QPushButton {{
            font-family: "{selectedFont}";
        }}
        QComboBox {{
            font-family: "{selectedFont}";
        }}
        QSpinBox {{
            font-family: "{selectedFont}";
        }}
        QCheckBox {{
            font-family: "{selectedFont}";
        }}
        QMenuBar {{
            font-family: "{selectedFont}";
        }}
        QMenu {{
            font-family: "{selectedFont}";
        }}
        QTabWidget {{
            font-family: "{selectedFont}";
        }}
    """)
    
    addLog(0, f"Global UI font set to: {selectedFont} ✅", "LoadFontActivity")