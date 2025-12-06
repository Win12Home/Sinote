"""
Sinote Widgets
Win12Home (C) 2025, MIT.
"""
from pathlib import PurePath
from BasicModule import * # Note: PySide6 was imported in BasicModule.py
import time # Wow, I wanna sleep!

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
loadedPlugin: list[dict[str, str | int | None]] = []
autoRun: list[partial] = []
"""
syntaxHighlighter Struct:
{
    "Code Name": [
        <One LoadPluginBase.CustomizeSyntaxHighlighter>,
        ["appendix1","appendix2","appendix3","appendix4","appendix5","appendix6"],
        ...
    ]
}
"""

outputDeveloperDebugInformation()

def automaticLoadPlugin() -> None:
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
        loadedPlugin.append(temp[0])
        debugPluginLog(f"Successfully loaded {item.name}, objectName: {temp[0]["objectName"]}. Preparing to parse... ✅")
        for key in temp[1]:
            debugPluginLog(f"Loading {key[0]}...")
            if key[1] == 1:
                debugPluginLog(f"Checked its property! Type: SyntaxHighlighter 🔎")
                debugPluginLog(f"Creating QSyntaxHighlighter... 🤓")
                beforeTime = datetime.now()
                syntaxHighlighter[key[2]] = [key[4].getObject(), key[3], key[5], key[6]]
                debugPluginLog(f"Successfully created QSyntaxHighlighter! Used time: {(datetime.now() - beforeTime).total_seconds()}secs ✅")
            elif key[1] == 0:
                debugPluginLog(f"Checked its property! Type: RunningFunc 🤓")
                debugPluginLog(f"Appending to autoRun... 💥")
                [autoRun.append(i) if isinstance(i, partial) else None for i in key[2]]
                """
                This code definitely equals
                for i in key[2]:
                    if isinstance(i, partial):
                        autoRun.append(i)
                """
                debugPluginLog(f"Successfully to append! ✅")
    usedTime: float = (datetime.now() - beforeLoadDatetime).total_seconds()
    debugPluginLog(f"Successfully to load plugins! ✅ Used {usedTime:.3f}s")
    debugPluginLog(f"An assessment for Sinote: {"Use a new computer instead 🤔💀" if usedTime / len(dirs) > 1.0 else "Too slow 💀" if usedTime / len(dirs) > 0.8 else "A bit slow 😰" if usedTime / len(dirs) > 0.65 else "Good load 😍"}")


class AutomaticSaveThingsThread(QThread):
    def __init__(self, parent: QWidget = None, saveSecs: int = 10):
        super().__init__(parent)
        self.saveSecs: int = saveSecs
        self.running: bool = True
        self.ended: bool = False

    def saveThings(self) -> None:
        debugLog(f"Automatic saving every {self.saveSecs} secs 😍")
        if not self.parent() or not hasattr(self.parent(), "tabTextEdits"):
            debugLog("Skipped saveThings because attribute \"tabTextEdits\" destroyed! 😰")  # Automatic skip when not have attribute tabTextEdits
            return
        for temp in (getEditor for getEditor in self.parent().tabTextEdits if getEditor is not None):   # UwU I'm lazy so I tried to use list but my memory is lazy so I edit to Generator
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

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key.Key_Tab:
            cursor = self.textCursor()
            if cursor.hasSelection():
                start = min(cursor.anchor(), cursor.position())
                end = max(cursor.anchor(), cursor.position())
                cursor.setPosition(start)
                cursor.movePosition(QTextCursor.MoveOperation.StartOfLine)
                start = cursor.position()
                cursor.setPosition(end)
                cursor.movePosition(QTextCursor.MoveOperation.EndOfLine)
                end = cursor.position()
                cursor.setPosition(start)
                cursor.setPosition(end, QTextCursor.MoveMode.KeepAnchor)
                selected_text = cursor.selectedText()
                lines = selected_text.split('\u2029')
                stringToIndent = " " * self.spacing
                indentedLines = [stringToIndent + line for line in lines]
                cursor.insertText('\u2029'.join(indentedLines))
            else:
                self.insertPlainText(' ' * self.spacing)
            return
        elif event.key() == Qt.Key.Key_Return:
            cursor = self.textCursor()
            currentBlock = cursor.block()
            currentText = currentBlock.text()
            spaces = 0
            for char in currentText:
                if char == ' ':
                    spaces += 1
                else:
                    break
            indentLevel = spaces // self.spacing
            super().keyPressEvent(event)
            if indentLevel > 0:
                stringToIndent = ' ' * (indentLevel * self.spacing)
                self.insertPlainText(stringToIndent)
            if self.usingCodeControl:
                trimmed = currentText.strip()
                for keyword in self.defineKeywords:
                    if isinstance(keyword, str) and trimmed.endswith(keyword):
                        self.insertPlainText(' ' * self.spacing)
                        break
                else:
                    if any(trimmed.endswith(symbol) for symbol in [':', '{', '(', '[']):
                        self.insertPlainText(' ' * self.spacing)
            return
        elif event.key() == Qt.Key.Key_Backtab:
            cursor = self.textCursor()
            if cursor.hasSelection():
                start = min(cursor.anchor(), cursor.position())
                end = max(cursor.anchor(), cursor.position())
                cursor.setPosition(start)
                cursor.movePosition(QTextCursor.MoveOperation.StartOfLine)
                start = cursor.position()
                cursor.setPosition(end)
                cursor.movePosition(QTextCursor.MoveOperation.EndOfLine)
                end = cursor.position()
                cursor.setPosition(start)
                cursor.setPosition(end, QTextCursor.MoveMode.KeepAnchor)
                selected_text = cursor.selectedText()
                lines = selected_text.split('\u2029')
                notIndentedLines = []
                for line in lines:
                    if line.startswith(' ' * self.spacing):
                        notIndentedLines.append(line[self.spacing:])
                    elif line.startswith(' '):
                        spaces_to_remove = min(self.spacing, len(line) - len(line.lstrip()))
                        notIndentedLines.append(line[spaces_to_remove:])
                    else:
                        notIndentedLines.append(line)

                cursor.insertText('\u2029'.join(notIndentedLines))
            else:
                cursor = self.textCursor()
                block = cursor.block()
                text = block.text()
                spaces_to_remove = min(self.spacing, len(text) - len(text.lstrip()))
                if spaces_to_remove > 0:
                    cursor.movePosition(QTextCursor.MoveOperation.StartOfLine)
                    cursor.movePosition(QTextCursor.MoveOperation.Right, QTextCursor.MoveMode.KeepAnchor,
                                        spaces_to_remove)
                    cursor.removeSelectedText()
            return

        elif event.key() in [Qt.Key.Key_ParenRight, Qt.Key.Key_BracketRight, Qt.Key.Key_BraceRight, Qt.Key.Key_QuoteDbl, Qt.Key.Key_Apostrophe]:
            cursor = self.textCursor()
            characterMap = {
                Qt.Key.Key_ParenRight: ('(', ')'),
                Qt.Key.Key_BracketRight: ('[', ']'),
                Qt.Key.Key_BraceRight: ('{', '}'),
                Qt.Key.Key_QuoteDbl: ('"', '"'),
                Qt.Key.Key_Apostrophe: ("'", "'")
            }
            opening, closing = characterMap.get(event.key(), (None, None))
            if opening and closing:
                text = cursor.block().text()[:cursor.positionInBlock()]
                if not text.rstrip().endswith(('#', '"', "'")):
                    cursor.select(QTextCursor.SelectionType.WordUnderCursor)
                    selectedText = cursor.selectedText()
                    if opening in selectedText:
                        self.insertPlainText(closing)
                        cursor.movePosition(QTextCursor.MoveOperation.Left)
                        self.setTextCursor(cursor)
                        return

            super().keyPressEvent(event)
            return
        elif event.key() == Qt.Key.Key_Backspace:
            cursor = self.textCursor()
            if cursor.hasSelection():
                cursor.removeSelectedText()
                return
            if cursor.position() > 0:
                current_pos = cursor.position()
                cursor.movePosition(QTextCursor.MoveOperation.Left, QTextCursor.MoveMode.KeepAnchor, 2)
                twoChars = cursor.selectedText()
                cursor.clearSelection()
                if twoChars in ['()', '[]', '{}', '""', "''"]:
                    cursor.setPosition(current_pos - 1)
                    cursor.movePosition(QTextCursor.MoveOperation.Left, QTextCursor.MoveMode.KeepAnchor, 1)
                    cursor.removeSelectedText()
                else:
                    cursor.setPosition(current_pos)
                    cursor.movePosition(QTextCursor.MoveOperation.Left, QTextCursor.MoveMode.KeepAnchor, 1)
                    cursor.removeSelectedText()
            else:
                super().keyPressEvent(event)
            return

        super().keyPressEvent(event)


class SinotePlainTextEdit(SpacingSupportEdit):
    def __init__(self):
        super().__init__()
        self.setFilename = None
        self.nowFilename: str | None = None
        self.num: int = -1

    def autoSave(self):
        if self.nowFilename:
            debugLog(f"Automatic saving file {self.nowFilename}")
            with open(self.nowFilename, "w+", encoding="utf-8") as f:
                f.write(self.toPlainText())
            debugLog(f"Successfully to save file {self.nowFilename}")

    def clear(self):
        if self.setFilename is not None:
            self.setFilename(self.num, loadJson("EditorUI")["editor.tab.tab_name_unsaved"].format(self.nowFilename))
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
        foundHighlighter = Signal(LoadPluginBase.CustomizeSyntaxHighlighter)
        setPairKeywords = Signal(list)
        noSyntax = Signal()

        def __init__(self, appendix: str):
            super().__init__()
            self.appendix = appendix

        def run(self) -> None:
            debugLog(f"Finding Highlighter (*.{self.appendix})... (THREAD) 🔎")
            temp: LoadPluginBase.CustomizeSyntaxHighlighter | None = None
            temp2, temp3 = None, None
            for _, i in syntaxHighlighter.items():
                if self.appendix in i[1]:
                    debugLog(f"{self.appendix} is in {i[1]}, successfully to find! ✅")
                    temp = i[0]
                    temp2 = i[2]
                    temp3 = i[3]
                    break
                else:
                    debugLog(f"{self.appendix} isn't in {i[1]}, continue find! 🔎")
            if temp is not None:
                debugLog(r"Emit found Syntax Highlighter 💥")
                self.foundHighlighter.emit(temp)
                temp3.append(temp2)
                self.setPairKeywords.emit(temp3)
            else:
                debugLog(r"Cannot found Syntax Highlighter ❌")
                self.noSyntax.emit()

    def setHighlighter(self, highlighter: LoadPluginBase.CustomizeSyntaxHighlighter | None) -> None:
        debugLog("Setting another Highlighter..." if highlighter else "Cleaning Highlighter...")
        self.highlighter = highlighter if highlighter else LoadPluginBase.CustomizeSyntaxHighlighter([[] for i in range(7)])
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
        self.temp.foundHighlighter.connect(self.setHighlighter)
        self.temp.setPairKeywords.connect(self._setPairKeywords)
        self.temp.noSyntax.connect(self._setNoSyntax)
        self.temp.start()

    def _setPairKeywords(self, arg: list) -> None:
        self.defineKeywords = arg
        self.usingCodeControl = True

    def _setNoSyntax(self) -> None:
        self.defineKeywords = []
        self.setHighlighter(None)
        self.usingCodeControl = False

    def readFile(self, filename: str) -> None:
        addLog(0, f"Attempting to read file {filename}...", "SinoteUserInterfaceActivity")
        if not Path(filename).exists():
            addLog(1, f"Cannot find file {filename}, current file will save.","SinoteUserInterfaceActivity")
        if not Path(filename).is_file():
            addLog(1, f"Are you sure you using a normal file? Cannot read {filename}!", "SinoteUserInterfaceActivity")
        # Try different encodings and support Chinese(GBK/GB2312)
        encodings = ["utf-8", "utf-16", "gbk", "gb2312", "latin-1", "windows-1252", "utf-32", "ascii"]
        content: str | None = None
        usedEnc: str | None = None
        
        for encoding in encodings:
            try:
                debugLog(f"Trying reading with encoding {encoding.upper()} 🤔")
                with open(filename, "r", encoding=encoding) as f:
                    content = f.read()
                    usedEnc = encoding
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
            addLog(0, f"Successfully to read file {filename} using {usedEnc} encoding! ✅", "SinoteUserInterfaceActivity")
        else:
            addLog(2, f"Cannot read file {filename}. Tried all encodings but failed! Or other Exception out! ❌", "SinoteUserInterfaceActivity")
            w = QMessageBox(None, loadJson("MessageBox")["msgbox.title.error"], loadJson("MessageBox")["msgbox.error.fileCannotRead"], buttons=QMessageBox.StandardButton.Ok)
            w.exec()


class SettingObject(QWidget):
    ... # Doing...


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.widget = QStackedWidget()
        self.mainFrame = QWidget()
        self.settingFrame = QWidget()
        self.editorThread = AutomaticSaveThingsThread(self)
        self.setCentralWidget(self.widget)
        self._initBase()
        self._setupUI()

    def _setupUI(self):
        debugLog("Setting up User Interface...")
        debugLog("Setting up Text Edit Area...")
        self.textEditArea = QTabWidget()
        self.tabTextEdits: list[SinotePlainTextEdit | None] = []
        self.textEditArea.tabBar().setMaximumHeight(60)
        self.textEditArea.setTabsClosable(True)
        self.textEditArea.setMovable(True)
        self.textEditArea.tabCloseRequested.connect(self._requestClose)
        self._createRecommendFile()
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
        self.backToMain = QPushButton(loadJson("EditorUI")["editor.button.settings.back"])
        self.backToMain.clicked.connect(partial(self.widget.setCurrentIndex, 0))
        self.backToMain.setMaximumWidth(250)
        self.backToMain.setMinimumWidth(220)
        self.setArea = QTabWidget()
        self.setArea.setMovable(False)
        self.setArea.setTabsClosable(False)
        self.setArea.appearance = QWidget()
        self.setArea.addTab(self.setArea.appearance, loadJson("EditorUI")["editor.tab.settings.appearance"])
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

    def show(self) -> None:
        debugLog("Showing Application...")
        super().show()
        debugLog("Show Application Successfully!")

    def closeEvent(self, event: QCloseEvent) -> None:
        debugLog("CloseEvent triggered 🤓")
        self.close()
        event.accept()

    def close(self) -> None:
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
        self._createTab()

    def _createTab(self, filename: str | None = None):
        debugLog(f"Creating Tab... Will load file: {filename if filename else "Nothing"} 🤓")
        oldDatetime = datetime.now()
        temp = SinotePlainTextEdit()
        temp.num = len(self.tabTextEdits)
        if filename:
            temp.readFile(filename)
        self.tabTextEdits.append(temp)
        self.textEditArea.addTab(temp, loadJson("EditorUI")["editor.tab.new_file"])
        temp.setFilename = self.textEditArea.tabBar().setTabText
        debugLog(f"Successfully to create tab! Used: {(datetime.now() - oldDatetime).total_seconds():.2f}s ✅")
        debugLog("Attempting to update setting... 😍")
        self.applySettings()
        debugLog("Successfully to update setting! ✅")

    def applySettings(self):
        fontSize: int = settingObject.getValue("fontSize")
        fontName: str = settingObject.getValue("fontName")
        debugLog(f"Font Size: {fontSize}, Font Name: {fontName} 😍")
        for tab, temp in enumerate(self.tabTextEdits, 1):
            if temp:
                debugLog(f"Setting tab {tab}... 🤔")
                temporary = QFont(fontName, fontSize)
                temp.setStyleSheet(f"{temp.styleSheet()} font-family: {fontName}; font-size: {fontSize}pt;")
                temp.setFont(temporary)
        debugLog("Successfully to set tab! ✅")

    def _initBase(self):
        debugLog("Initializing Base Window... 🔎")
        self.setWindowTitle("Sinote")
        self.resize(1280, 760)
        debugLog("Successfully to initialize ✅")

automaticLoadPlugin()
if __name__ == "__main__":
    loadFonts()
    a = MainWindow()
    a.show()
    application.exec()
    addLog(0, "Successfully to exit Sinote with Process Code 0 ✅")
    saveLog()
    sys.exit(0)