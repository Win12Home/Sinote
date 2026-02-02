from datetime import datetime
from functools import partial
from pathlib import Path
from typing import Any, Dict, List, Optional

from core.addons.applyStylesheet import applyStylesheet
from core.addons.setGlobalUIFont import isRecommendFont
from core.addons.Shortcut import Shortcut
from core.AutoLoadPluginThread import autoRun, loadedPlugin
from core.AutomaticIterDirectoryThread import AutomaticIterDirectoryThread
from core.i18n import baseInfo, getLangJson
from core.project import ProjectSettings
from ui.msgbox.CreateProjectDialog import CreateProjectDialog
from PySide6.QtCore import QEvent, QObject, Qt, QTimer, Signal
from PySide6.QtGui import (
    QAction,
    QCloseEvent,
    QFont,
    QIcon,
    QKeyEvent,
    QPixmap,
    QTextCursor,
    QCursor,
)
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMenu,
    QMenuBar,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QStackedWidget,
    QTabWidget,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
    QInputDialog,
)
from ui.edit.AutomaticSaveThingsThread import AutomaticSaveThingsThread
from ui.edit.SinotePlainTextEdit import SinotePlainTextEdit
from ui.selfLogger import debugLog
from ui.SettingObject import (
    CheckBoxSettingObject,
    ComboBoxSettingObject,
    LineEditSettingObject,
)
from ui.widgets import PluginInfoLister, SeperatorWidget
from ui.window.FramelessWindow import FramelessWindow
from utils.application import application
from utils.argumentParser import args
from utils.config import settingObject
from utils.logger import Logger
from utils.timer import getTotalSeconds


class MainWindow(FramelessWindow):
    themeChanged: Signal = Signal()

    def __init__(self, initialized: bool = False):
        super().__init__()
        self._project: str | None = None
        self._projectSettings: ProjectSettings | None = None

        self.shortcut = Shortcut()
        self.widget = QStackedWidget()
        self.mainFrame = QWidget()
        self.settingFrame = QWidget()
        self.editorThread = AutomaticSaveThingsThread(
            self, settingObject.getValue("secsave")
        )
        self.dirThread = AutomaticIterDirectoryThread(self)
        self.setWindowIcon(QIcon("./resources/icon.png"))
        if not initialized:
            self._automaticSetTheme()
        self._initBase()
        self._setupUI()
        self._setupProject()
        self._setupTab()
        self.setCentralWidget(self.widget)
        self._autoApplyPluginInfo()

    def _setupProject(self) -> None:
        debugLog("Automatically loading projects...")
        debugLog("Saving changes... 🀄")
        self.editorThread.saveThings()
        debugLog("Save changes successfully! ✔")

        proj: str = settingObject.getValue("recently_project_path")

        if proj is None:
            debugLog('"recently_project_path" is null, quitting...')
            return

        self._openProject(proj)

    def newProject(self) -> None:
        projectCreator = CreateProjectDialog(self)
        projectCreator.setWindowIcon(self.windowIcon())
        if projectCreator.exec():
            self._openProject(projectCreator.path)

    def _setupTab(self) -> None:
        if not isinstance(self._projectSettings, ProjectSettings):
            return

        if not isinstance(self._projectSettings["recentlyWorks"], dict):
            self._projectSettings["recentlyWorks"] = {}

        if not isinstance(
            self._projectSettings["nowWorks"], str
        ):  # None -> None, no any issue there
            self._projectSettings["nowWorks"] = None

        if len(self._projectSettings["recentlyWorks"]) > 0:  # NOQA
            result: Dict[str, int] = {}
            for fileName, pos in self._projectSettings["recentlyWorks"].items():
                if not Path(fileName).exists():
                    self._createRecommendFile()
                    self.tabTextEdits[len(self.tabTextEdits) - 1].setPlainText(
                        getLangJson("EditorUI")["editor.any.cannotreadfile"].format(
                            fileName
                        )
                    )
                else:
                    result[fileName] = pos
                    if isinstance(pos, list) or isinstance(pos, int):
                        self.createTab(fileName, position=pos)
                    else:
                        Logger.error(
                            "Position information has broken! Automatically remove position information.",
                            "TabSetActivity",
                        )
                        self.createTab(fileName)
            self._projectSettings["recentlyWorks"] = result

        for oneFile in self.tabTextEdits:
            if oneFile is None:
                continue

            if oneFile.nowFilename == self._projectSettings["nowWorks"]:
                self.textEditArea.setCurrentWidget(oneFile)
                break

    def updateTree(self, directory: list[Any]) -> None:
        debugLog(
            "Project Tree Update Signal has received, trying to refresh project tree in UI..."
        )
        self.folder.clear()
        QTimer.singleShot(10, lambda: self.updateFromFiles(directory))
        debugLog("Released a QTimer to run it")

    def updateFromFiles(
        self, directory: list[Any], from_where: QTreeWidgetItem = None
    ) -> None:
        debugLog(f"Updating from folder: {directory}")

        if from_where is None:
            from_where = self.folder
        for oneFile in directory:
            debugLog(f"Analyzing file/folder {oneFile}... 🧐")
            if oneFile[0] == QIcon.ThemeIcon.FolderNew:
                item = QTreeWidgetItem(from_where, [oneFile[1]])
                item.where = oneFile[2]
                item.setIcon(0, QIcon.fromTheme(oneFile[0]))
                debugLog("Recursing because of folder type")
                self.updateFromFiles(oneFile[3], item)
            else:
                item = QTreeWidgetItem(from_where, [oneFile[1]])
                item.where = oneFile[2]
                item.setIcon(0, QIcon.fromTheme(oneFile[0]))

            if isinstance(from_where, QTreeWidget):
                from_where.addTopLevelItem(item)
            else:
                from_where.addChild(item)

            debugLog("Well, successfully to analyze it!")

    def addTreeFile(self, path: Path | str | None) -> None:
        if path is None:
            return

        if not isinstance(path, Path):
            path = Path(path)

        window = QInputDialog(parent=self)
        window.setInputMode(QInputDialog.InputMode.TextInput)
        window.setWindowTitle("")
        window.setWindowIcon(self.windowIcon())
        window.setLabelText(getLangJson("MessageBox")["msgbox.request.inputFileName"])
        window.setOkButtonText(getLangJson("MessageBox")["msgbox.button.ok"])
        window.setCancelButtonText(getLangJson("MessageBox")["msgbox.button.cancel"])
        if window.exec():
            try:
                with open(path / window.textValue(), "w", encoding="utf-8") as f:
                    f.write("")
            except Exception as e:
                msgbox = QMessageBox(
                    QMessageBox.Icon.Critical,
                    getLangJson("MessageBox")["msgbox.title.error"],
                    getLangJson("MessageBox")["msgbox.error.cannotCreate"].format(
                        str(path / window.textValue()), repr(e)
                    ),
                    buttons=QMessageBox.StandardButton.Ok,
                    parent=self,
                )
                msgbox.exec()
            else:
                self.dirThread.emitIterDir()

    def addTreeFolder(self, path: Path | str | None) -> None:
        if path is None:
            return

        if not isinstance(path, Path):
            path = Path(path)

        window = QInputDialog(parent=self)
        window.setInputMode(QInputDialog.InputMode.TextInput)
        window.setWindowTitle("")
        window.setWindowIcon(self.windowIcon())
        window.setLabelText(getLangJson("MessageBox")["msgbox.request.inputFolderName"])
        window.setOkButtonText(getLangJson("MessageBox")["msgbox.button.ok"])
        window.setCancelButtonText(getLangJson("MessageBox")["msgbox.button.cancel"])
        if window.exec():
            try:
                (path / window.textValue()).mkdir(exist_ok=True)
            except Exception as e:
                msgbox = QMessageBox(
                    QMessageBox.Icon.Critical,
                    getLangJson("MessageBox")["msgbox.title.error"],
                    getLangJson("MessageBox")["msgbox.error.cannotCreateFolder"].format(
                        str(path / window.textValue()), repr(e)
                    ),
                    buttons=QMessageBox.StandardButton.Ok,
                    parent=self,
                )
                msgbox.exec()
            else:
                self.dirThread.emitIterDir()
    def removeTreeFile(self) -> None:
        if not self.folder.currentItem():
            return

        try:
            location = self.folder.currentItem().where
        except AttributeError:
            return

        try:
            if Path(location).is_file():
                for oneTab in self.tabTextEdits:
                    if oneTab is None:
                        return

                    if Path(oneTab.nowFilename) == Path(location):
                        self.tabTextEdits.remove(oneTab)
                        self.textEditArea.removeTab(self.textEditArea.indexOf(oneTab))
                        break

                Path(location).unlink()
            elif Path(location).is_dir():
                for oneTab in self.tabTextEdits:
                    if oneTab is None:
                        return

                    if Path(oneTab.nowFilename).resolve().is_relative_to(Path(location).resolve()):
                        self.tabTextEdits.remove(oneTab)
                        self.textEditArea.removeTab(self.textEditArea.indexOf(oneTab))

                from shutil import rmtree
                rmtree(location)
            else:
                raise IOError(f"{location} is not a file or a directory")
        except Exception as e:
            msgbox = QMessageBox(
                QMessageBox.Icon.Critical,
                getLangJson("MessageBox")["msgbox.title.error"],
                getLangJson("MessageBox")["msgbox.error.cannotRemove"].format(repr(e)),
                buttons=QMessageBox.StandardButton.Ok,
                parent=self,
            )
            msgbox.exec()
        else:
            self.dirThread.emitIterDir()

    def renameTreeFile(self) -> None:
        if not self.folder.currentItem():
            return

        try:
            location = self.folder.currentItem().where
        except AttributeError:
            return

        window = QInputDialog(parent=self)
        window.setInputMode(QInputDialog.InputMode.TextInput)
        window.setWindowTitle("")
        window.setWindowIcon(self.windowIcon())
        window.setLabelText(getLangJson("MessageBox")["msgbox.request.inputFileName"])
        window.setOkButtonText(getLangJson("MessageBox")["msgbox.button.ok"])
        window.setCancelButtonText(getLangJson("MessageBox")["msgbox.button.cancel"])
        window.setTextValue(Path(location).name)
        if window.exec():
            try:
                Path(location).rename(Path(location).parent / window.textValue())
            except Exception as e:
                msgbox = QMessageBox(
                    QMessageBox.Icon.Critical,
                    getLangJson("MessageBox")["msgbox.title.error"],
                    getLangJson("MessageBox")["msgbox.error.cannotRename"].format(
                        window.textValue(), repr(e)
                    ),
                    buttons=QMessageBox.StandardButton.Ok,
                    parent=self,
                )
                msgbox.exec()
            else:
                for oneTab in self.tabTextEdits:
                    if oneTab is None:
                        continue

                    if Path(oneTab.nowFilename) == Path(location):
                        self.tabTextEdits.remove(oneTab)
                        self.textEditArea.removeTab(self.textEditArea.indexOf(oneTab))
                        break
                self.createTab(str(Path(location).parent / window.textValue()))
                self.dirThread.emitIterDir()

    def analyzeTreeMenu(self) -> None:
        try:
            currentPath: Path = Path(self.folder.currentItem().where)
        except AttributeError:
            return

        menu = QMenu(self)

        addFile = QAction(
            getLangJson("EditorUI")["editor.menu.folder.addfile"],
            icon=QIcon.fromTheme(QIcon.ThemeIcon.DocumentNew),
        )
        addFile.triggered.connect(
            partial(
                self.addTreeFile,
                currentPath if currentPath.is_dir() else currentPath.parent,
            )
        )
        addFolder = QAction(
            getLangJson("EditorUI")["editor.menu.folder.addfolder"],
            icon=QIcon.fromTheme(QIcon.ThemeIcon.FolderNew),
        )
        addFolder.triggered.connect(
            partial(
                self.addTreeFile,
                currentPath if currentPath.is_dir() else currentPath.parent
            )
        )
        rename = QAction(
            getLangJson("EditorUI")["editor.menu.folder.rename"],
            icon=QIcon.fromTheme(QIcon.ThemeIcon.InsertText),
        )
        rename.triggered.connect(
            self.renameTreeFile
        )
        remove = QAction(
            getLangJson("EditorUI")["editor.menu.folder.remove"],
            icon=QIcon.fromTheme(QIcon.ThemeIcon.EditDelete),
        )
        remove.triggered.connect(
            self.removeTreeFile
        )

        menu.addActions([addFile, addFolder, rename, remove])
        menu.exec(QCursor.pos())

    def analyzeOpenItem(self) -> None:
        if not self.folder.currentItem():
            return

        if not hasattr(self.folder.currentItem(), "where"):
            return

        if not Path(self.folder.currentItem().where).is_file():  # NOQA, look down
            return

        for oneTab in self.tabTextEdits:
            if oneTab is None:
                continue

            if Path(oneTab.nowFilename) == Path(self.folder.currentItem().where):  # NOQA
                self.textEditArea.setCurrentWidget(oneTab)
                return

        self.createTab(self.folder.currentItem().where)  # NOQA, checked attribute

    def _setupUI(self) -> None:
        debugLog("Setting up User Interface...")
        debugLog("Setting up Text Edit Area...")
        self.projectArea = QWidget()
        self.projectArea.vLayout = QVBoxLayout()

        self.commandBar: QWidget = QWidget()
        self.commandBar.setSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding
        )
        self.commandBar.hLayout = QHBoxLayout()
        self.commandBar.hLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.commandBar.projectName = QLabel(
            getLangJson("EditorUI")["editor.proj.noproj"]
        )
        self.commandBar.addFile = QPushButton("+")
        self.commandBar.addFile.setFlat(True)
        self.commandBar.addFile.setSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed
        )
        self.commandBar.addFile.clicked.connect(lambda: self.addTreeFile(self._project))
        self.commandBar.addFolder = QPushButton()
        self.commandBar.addFolder.setIcon(QIcon.fromTheme(QIcon.ThemeIcon.FolderNew))
        self.commandBar.addFolder.setFlat(True)
        self.commandBar.addFolder.setSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed
        )
        self.commandBar.addFolder.clicked.connect(lambda: self.addTreeFolder(self._project))
        self.commandBar.hLayout.addWidget(self.commandBar.projectName, stretch=0)
        self.commandBar.hLayout.addWidget(self.commandBar.addFile, stretch=0)
        self.commandBar.hLayout.addWidget(self.commandBar.addFolder, stretch=0)
        self.commandBar.setLayout(self.commandBar.hLayout)

        self.folder: QTreeWidget = QTreeWidget()
        self.folder.setHeaderHidden(True)
        self.folder.setRootIsDecorated(False)
        self.folder.itemDoubleClicked.connect(self.analyzeOpenItem)
        self.folder.installEventFilter(self)
        self.projectArea.vLayout.addWidget(self.commandBar, stretch=0)
        self.projectArea.vLayout.addWidget(self.folder, stretch=1)
        self.projectArea.setLayout(self.projectArea.vLayout)

        self.textEditArea = QTabWidget()
        self.tabTextEdits: list[SinotePlainTextEdit | QWidget | None] = []
        self.textEditArea.tabBar().setMaximumHeight(60)
        self.textEditArea.setTabsClosable(True)
        self.textEditArea.setMovable(True)
        self.textEditArea.tabCloseRequested.connect(self._requestClose)
        debugLog("Successfully to set up Text Edit Area!")
        debugLog("Setting up Layout...")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.addWidget(self.projectArea)
        self.horizontalLayout.addWidget(self.textEditArea)
        self.horizontalLayout.setStretch(0, 1)
        self.horizontalLayout.setStretch(1, 3)
        self.mainFrame.setLayout(self.horizontalLayout)
        self.dirThread.iterChanged.connect(self.updateTree)
        debugLog("Successfully to set up Layout!")
        debugLog("Setting up Menu...")
        self.fileEditMenu = QMenuBar(self)
        self.fileEditMenu.fileEdit = QMenu(getLangJson("EditorUI")["editor.menu.files"])
        self.fileEditMenu.editMenu = QMenu(getLangJson("EditorUI")["editor.menu.edit"])
        # Actions Define
        newProject = QAction(
            getLangJson("EditorUI")["editor.menu.files.newproj"],
            self,
            icon=QIcon.fromTheme(QIcon.ThemeIcon.FolderNew),
        )
        newProject.triggered.connect(self.newProject)
        openProject = QAction(
            getLangJson("EditorUI")["editor.menu.files.openproj"],
            self,
            icon=QIcon.fromTheme(QIcon.ThemeIcon.DocumentOpen),
        )
        openProject.triggered.connect(self.openProject)
        saveAs = QAction(
            getLangJson("EditorUI")["editor.menu.files.saveas"],
            self,
            icon=QIcon.fromTheme(QIcon.ThemeIcon.DocumentSaveAs),
        )
        saveAs.triggered.connect(self.saveAs)
        setting = QAction(
            getLangJson("EditorUI")["editor.menu.files.settings"],
            self,
            icon=QIcon.fromTheme(QIcon.ThemeIcon.Computer),
        )
        setting.triggered.connect(partial(self.widget.setCurrentIndex, 1))
        exitProg = QAction(
            getLangJson("EditorUI")["editor.menu.files.exit"],
            self,
            icon=QIcon.fromTheme(QIcon.ThemeIcon.ApplicationExit),
        )
        exitProg.triggered.connect(self.close)
        self.fileEditMenu.fileEdit.addActions(
            [newProject, openProject, saveAs, setting, exitProg]
        )
        undo = QAction(
            getLangJson("EditorUI")["editor.menu.edit.undo"],
            self,
            icon=QIcon.fromTheme(QIcon.ThemeIcon.EditRedo),
        )
        undo.triggered.connect(lambda: self.textEditArea.currentWidget().undo())  # NOQA
        redo = QAction(
            getLangJson("EditorUI")["editor.menu.edit.redo"],
            self,
            icon=QIcon.fromTheme(QIcon.ThemeIcon.EditUndo),
        )
        redo.triggered.connect(lambda: self.textEditArea.currentWidget().redo())  # NOQA
        self.fileEditMenu.editMenu.addActions([undo, redo])
        self.fileEditMenu.addMenu(self.fileEditMenu.fileEdit)
        self.fileEditMenu.addMenu(self.fileEditMenu.editMenu)
        self.setMenuBar(self.fileEditMenu)
        debugLog("Successfully to set up Menu!")
        debugLog("Setting up Setting Area...")
        self.backToMain = QPushButton("<")
        self.backToMain.setStyleSheet(
            f"{self.backToMain.styleSheet()}background-color: none; border: none;"
        )
        self.backToMain.clicked.connect(partial(self.widget.setCurrentIndex, 0))
        self.backToMain.setMaximumWidth(50)
        self.setArea = QTabWidget()
        self.setArea.setMovable(False)
        self.setArea.setTabsClosable(False)
        # Appearance Setting
        self.setArea.appearance = QScrollArea()
        self.setArea.appearance.vLayout = QVBoxLayout()
        self.setArea.appearance.titleAppearance = QLabel(
            getLangJson("EditorUI")["editor.title.settings.appearance"]
        )
        self.setArea.appearance.titleAppearance.setStyleSheet(
            "font-size: 38px; font-weight: bold; margin-bottom: 10px;"
        )  # QSS
        self.setArea.appearance.seperator = SeperatorWidget()
        self.setArea.appearance.debugMode = CheckBoxSettingObject(
            None,
            getLangJson("EditorUI")["editor.title.setobj.debugmode"],
            getLangJson("EditorUI")["editor.desc.setobj.debugmode"],
        )
        self.setArea.appearance.debugMode.checkBox.setText(
            getLangJson("EditorUI")["editor.desc.setobj.debugmodeopen"]
        )
        self.setArea.appearance.debugMode.checkBox.setChecked(
            settingObject.getValue("debugmode")
        )
        self.setArea.appearance.debugMode.checkBox.checkStateChanged.connect(
            lambda: settingObject.setValue(
                "debugmode", self.setArea.appearance.debugMode.checkBox.isChecked()
            )
        )
        self.setArea.appearance.language = ComboBoxSettingObject(
            None,
            getLangJson("EditorUI")["editor.title.setobj.language"],
            getLangJson("EditorUI")["editor.desc.setobj.language"],
        )
        self.setArea.appearance.language.comboBox.addItems(
            [i for _, i in baseInfo()["item.dict.language_for"].items()]
        )
        try:
            self.setArea.appearance.language.comboBox.setCurrentIndex(
                list(baseInfo()["item.dict.language_for"].keys()).index(
                    settingObject.getValue("language")
                )
            )
        except IndexError:
            self.setArea.appearance.language.comboBox.setCurrentIndex(0)
        self.setArea.appearance.language.comboBox.currentIndexChanged.connect(
            lambda: {
                settingObject.setValue(
                    "language",
                    list(baseInfo()["item.dict.language_for"].keys())[
                        self.setArea.appearance.language.comboBox.currentIndex()
                    ],
                ),
                QMessageBox(
                    QMessageBox.Icon.Information,
                    getLangJson("MessageBox")["msgbox.title.info"],
                    getLangJson("MessageBox")["msgbox.info.restartApplySet"],
                    buttons=QMessageBox.StandardButton.Ok,
                    parent=self,
                ).exec(),
            }
        )
        self.setArea.appearance.theme = ComboBoxSettingObject(
            None,
            getLangJson("EditorUI")["editor.title.setobj.theme"],
            getLangJson("EditorUI")["editor.desc.setobj.theme"],
        )
        self.setArea.appearance.theme.comboBox.addItems(
            [
                getLangJson("EditorUI")[i]
                for i in [f"editor.any.{k}" for k in ["light", "dark"]]
            ]
        )
        self.setArea.appearance.theme.comboBox.setCurrentIndex(
            settingObject.getValue("theme")
            if settingObject.getValue("theme") < 2
            else 0
        )
        self.setArea.appearance.theme.comboBox.currentIndexChanged.connect(
            lambda: self.setTheme(self.setArea.appearance.theme.comboBox.currentIndex())
        )
        self.setArea.appearance.vLayout.addWidget(
            self.setArea.appearance.titleAppearance
        )
        self.setArea.appearance.vLayout.addWidget(self.setArea.appearance.seperator)
        self.setArea.appearance.vLayout.addWidget(self.setArea.appearance.debugMode)
        self.setArea.appearance.vLayout.addWidget(self.setArea.appearance.language)
        self.setArea.appearance.vLayout.addWidget(self.setArea.appearance.theme)
        self.setArea.appearance.vLayout.addStretch(1)
        self.setArea.appearance.setLayout(self.setArea.appearance.vLayout)
        self.setArea.addTab(
            self.setArea.appearance,
            getLangJson("EditorUI")["editor.tab.settings.appearance"],
        )
        # Plugin Setting
        self.setArea.plugins = QScrollArea()
        self.setArea.plugins.vLayout = QVBoxLayout()
        self.setArea.plugins.titlePlugins = QLabel(
            getLangJson("EditorUI")["editor.title.settings.plugin"]
        )
        self.setArea.plugins.titlePlugins.setStyleSheet(
            "font-size: 38px; font-weight: bold; margin-bottom: 10px;"
        )  # Also QSS
        self.setArea.plugins.seperator = SeperatorWidget()
        self.pluginInfo: list[list[Any]] = []
        self.setArea.plugins.set = QWidget()
        self.setArea.plugins.set.hLayout = QHBoxLayout()
        self.setArea.plugins.set.listWidget = QListWidget()
        self.setArea.plugins.set.listWidget.setStyleSheet(
            f"{self.setArea.plugins.set.listWidget.styleSheet()} QListWidget::item::selected {r"{ background-color: lightblue; color: grey;}"}"
        )
        self.setArea.plugins.set.information = PluginInfoLister()
        self.setArea.plugins.set.listWidget.currentTextChanged.connect(
            lambda: {
                self.setArea.plugins.set.information.setInformation(
                    ["null" for i in range(7)]
                    if len(self.pluginInfo) == 0
                    else self.pluginInfo[
                        self.setArea.plugins.set.listWidget.currentRow()
                    ]
                )
            }
        )
        self.setArea.plugins.set.listWidget.itemDoubleClicked.connect(
            lambda: {
                self.setThisPluginAnotherType(
                    self.setArea.plugins.set.listWidget.currentItem()
                )
            }
        )
        self.setArea.plugins.set.hLayout.addWidget(
            self.setArea.plugins.set.listWidget, stretch=1
        )
        self.setArea.plugins.set.hLayout.addWidget(
            self.setArea.plugins.set.information, stretch=2
        )
        self.setArea.plugins.set.setLayout(self.setArea.plugins.set.hLayout)
        self.setArea.plugins.vLayout.addWidget(self.setArea.plugins.titlePlugins)
        self.setArea.plugins.vLayout.addWidget(self.setArea.plugins.seperator)
        self.setArea.plugins.vLayout.addWidget(self.setArea.plugins.set, 1)
        self.setArea.plugins.setLayout(self.setArea.plugins.vLayout)
        self.setArea.addTab(
            self.setArea.plugins, getLangJson("EditorUI")["editor.tab.settings.plugin"]
        )
        # Editor Font Setting
        self.setArea.edfont = QScrollArea()
        self.setArea.edfont.vLayout = QVBoxLayout()
        self.setArea.edfont.titleEditorFont = QLabel(
            getLangJson("EditorUI")["editor.tab.settings.editorfont"]
        )
        self.setArea.edfont.titleEditorFont.setStyleSheet(
            "font-size: 38px; font-weight: bold; margin-bottom: 10px;"
        )
        self.setArea.edfont.seperator = SeperatorWidget()
        self.setArea.edfont.fontSelect = ComboBoxSettingObject(
            None,
            getLangJson("EditorUI")["editor.title.setobj.fontname"],
            getLangJson("EditorUI")["editor.desc.setobj.fontname"],
        )
        self.setArea.edfont.fontSelect.useFontBox()
        self.setArea.edfont.fontSelect.comboBox.setCurrentFont(
            QFont(settingObject.getValue("fontName"))
        )
        self.setArea.edfont.fontSelect.comboBox.currentFontChanged.connect(
            lambda: self.applyFont(
                fontName=self.setArea.edfont.fontSelect.comboBox.currentFont().family()
            )
        )
        self.setArea.edfont.fontSize = LineEditSettingObject(
            None,
            getLangJson("EditorUI")["editor.title.setobj.fontsize"],
            getLangJson("EditorUI")["editor.desc.setobj.fontsize"],
        )
        self.setArea.edfont.fontSize.useSpinBox()
        self.setArea.edfont.fontSize.lineEdit.setMinimum(1)
        self.setArea.edfont.fontSize.lineEdit.setMaximum(99)
        self.setArea.edfont.fontSize.lineEdit.setValue(
            settingObject.getValue("fontSize")
        )
        self.setArea.edfont.fontSize.lineEdit.textChanged.connect(
            lambda: self.applyFont(
                fontSize=self.setArea.edfont.fontSize.lineEdit.value()
            )
        )
        self.setArea.edfont.fontSize.lineEdit.setSuffix(
            getLangJson("EditorUI")["editor.suffix.settings.size"]
        )
        self.setArea.edfont.fallbackSelect = ComboBoxSettingObject(
            None,
            getLangJson("EditorUI")["editor.title.setobj.fbfont"],
            getLangJson("EditorUI")["editor.desc.setobj.fbfont"],
        )
        self.setArea.edfont.fallbackSelect.useFontBox()
        self.setArea.edfont.fallbackSelect.comboBox.currentFontChanged.connect(
            lambda: self.applyFont(
                fallbackFont=self.setArea.edfont.fallbackSelect.comboBox.currentFont().family()
            )
        )
        if settingObject.getValue("fallbackFont"):
            self.setArea.edfont.fallbackSelect.comboBox.setCurrentFont(
                QFont(settingObject.getValue("fallbackFont"))
            )
        else:
            self.setArea.edfont.fallbackSelect.comboBox.setCurrentFont(
                QFont("MiSans VF")
            )
        self.setArea.edfont.useFallbackFont = CheckBoxSettingObject(
            None,
            getLangJson("EditorUI")["editor.title.setobj.usefbfont"],
            getLangJson("EditorUI")["editor.desc.setobj.usefbfont"],
        )
        self.setArea.edfont.useFallbackFont.checkBox.setText(
            getLangJson("EditorUI")["editor.desc.setobj.usefbfontopen"]
        )
        self.setArea.edfont.useFallbackFont.checkBox.stateChanged.connect(
            lambda: {
                settingObject.setValue(
                    "useFallback",
                    self.setArea.edfont.useFallbackFont.checkBox.isChecked(),
                ),
                self.setArea.edfont.fallbackSelect.setDisabled(
                    not self.setArea.edfont.useFallbackFont.checkBox.isChecked()
                ),
                self.applySettings(),
            }
        )
        self.setArea.edfont.useFallbackFont.checkBox.setChecked(
            settingObject.getValue("useFallback")
        )
        self.setArea.edfont.fallbackSelect.setDisabled(
            not self.setArea.edfont.useFallbackFont.checkBox.isChecked()
        )
        self.setArea.edfont.vLayout.addWidget(self.setArea.edfont.titleEditorFont)
        self.setArea.edfont.vLayout.addWidget(self.setArea.edfont.seperator)
        self.setArea.edfont.vLayout.addWidget(self.setArea.edfont.fontSelect)
        self.setArea.edfont.vLayout.addWidget(self.setArea.edfont.fontSize)
        self.setArea.edfont.vLayout.addWidget(self.setArea.edfont.useFallbackFont)
        self.setArea.edfont.vLayout.addWidget(self.setArea.edfont.fallbackSelect)
        self.setArea.edfont.vLayout.addStretch(1)
        self.setArea.edfont.setLayout(self.setArea.edfont.vLayout)
        self.setArea.addTab(
            self.setArea.edfont,
            getLangJson("EditorUI")["editor.tab.settings.editorfont"],
        )
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
        self.dirThread.start()
        debugLog("Successfully to add frame!")
        debugLog("Adding shortcuts...")
        self.shortcut.addItem([Qt.Key.Key_Control, Qt.Key.Key_Alt, Qt.Key.Key_S], 1)
        # self.shortcut.addItem([Qt.Key.Key_Control, Qt.Key.Key_N], 2)  # New File was unused!
        self.shortcut.addItem([Qt.Key.Key_Control, Qt.Key.Key_Shift, Qt.Key.Key_S], 3)
        self.shortcut.addItem([Qt.Key.Key_Control, Qt.Key.Key_Q], 4)
        self.shortcut.shortcutHandled.connect(self._analyzeShortcut)
        debugLog("Successfully to add shortcuts")
        debugLog("Successfully to set up User Interface!")

    def _analyzeShortcut(self, itemNum: int) -> None:
        if itemNum == 1:
            if self.widget.currentIndex() == 0:
                self.widget.setCurrentIndex(1)
                return
            self.widget.setCurrentIndex(0)
        elif itemNum == 3:
            self.saveAs()
        elif itemNum == 4:
            self.close()

    def eventFilter(self, obj: QObject, event: QEvent) -> bool:
        if obj == self.folder and event.type() == QEvent.Type.ContextMenu:
            if self.folder.currentIndex().isValid():
                self.analyzeTreeMenu()

        if event.type() == QEvent.Type.KeyPress:
            self.shortcut.keyPressEvent(event)  # NOQA
        elif event.type() == QEvent.Type.KeyRelease:
            self.shortcut.keyReleaseEvent(event)  # NOQA, shut up
        return False

    def keyPressEvent(self, event: QKeyEvent) -> None:
        self.shortcut.keyPressEvent(event)
        super().keyPressEvent(event)

    def keyReleaseEvent(self, event: QKeyEvent) -> None:
        self.shortcut.keyReleaseEvent(event)
        super().keyReleaseEvent(event)

    def setThisPluginAnotherType(self, item: QListWidgetItem) -> None:
        objectName: str = item.objName  # NOQA
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
            icon: QPixmap = QPixmap(
                "./resources/images/plugins.png"
                if word["icon"] is None or not Path(word["icon"]).exists()
                else word["icon"]
            )
            name: str = word["name"]
            objectName: str = word["objectName"]
            version: str = word["version"]
            author: str = ", ".join(word["author"])
            desc: str = word["description"]
            self.pluginInfo.append(
                [
                    (
                        "./resources/images/plugins.png"
                        if word["icon"] is None or not Path(word["icon"]).exists()
                        else word["icon"]
                    ),
                    name,
                    objectName,
                    version,
                    author,
                    desc,
                ]
            )
            item: QListWidgetItem = QListWidgetItem(
                icon,
                (
                    name
                    if objectName not in settingObject.getValue("disableplugin")
                    else f"[X] {name}"
                ),
            )
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
        if not ("--no-theme" in args or "-nt" in args):
            applyStylesheet(application, 0 if not theme else 1)
            settingObject.setValue("theme", theme)
            self.applySettings()
            self.themeChanged.emit()

    def _automaticSetTheme(self) -> None:
        if not ("--no-theme" in args or "-nt" in args):
            applyStylesheet(
                application,
                (0 if not settingObject.getValue("theme") else 1),
            )

    def applyFont(
        self,
        fontName: Optional[str] = None,
        fontSize: Optional[int] = None,
        fallbackFont: Optional[str] = None,
    ) -> None:
        if fontName:
            settingObject.setValue("fontName", fontName)
        if fontSize:
            settingObject.setValue("fontSize", fontSize)
        if fallbackFont:
            settingObject.setValue("fallbackFont", fallbackFont)
        self.applySettings()

    def show(self) -> None:
        debugLog("Showing Application...")
        super().show()
        Logger.info(
            f"Used {getTotalSeconds():.2f}s to load!",
            "SinoteUserInterfaceActivity",
            True,
        )
        debugLog("Show Application Successfully!")
        self.applySettings()
        debugLog("Preparing to run AutoRuns...")
        QTimer.singleShot(100, lambda: [i() for i in autoRun])
        debugLog(
            "Running AutoRuns by QTimer 👏"
        )  # If you aren't using QTimer, Window will be stuck.
        """
        Easy but it will return a list that per value all is NoneType.
        You can replace it to:
        for i in autoRun:
            if isinstance(i, partial):
                i()
        and use QTimer to run it
        """
        if isRecommendFont() and not Path("./DISABLE-FONT-CHECK-WARNING").exists():
            """
            I want to make user to experience the HURT of the EXTERNALLY_MANAGED! (Of course I use Windows, but now I use arch btw)

            error: externally-managed-environment

            × This environment is externally managed
            ╰─> To install Python packages system-wide, you need to use your system package manager.

            If you want to install pip packages locally, use virtual environments.

            I never use venv, of course.
            """
            print(
                """error: externally-managed-font-src

× This font directory is externally managed
╰─> To use fixed font every time it's not recommend at that.

If you want to use Fixed Font every time or you doesn't know that problem, remove .1 suffix in DISABLE-FONT-CHECK-WARNING.1!
                """
            )
            msgbox: QMessageBox = QMessageBox(
                QMessageBox.Icon.Warning,
                "Warning",
                "(Only English) You are using the Fixed Font/Normal Font in Sinote, this font will be not support some characters like Chinese/Japanese characters!\n"
                "If you would like to disable it forever, rename DISABLE-FONT-CHECK-WARNING.1 to DISABLE-FONT-CHECK-WARNING!\n"
                "Probably, it might generate failed.",
                parent=self,
            )
            msgbox.setWindowIcon(self.windowIcon())
            msgbox.exec()
            try:
                with open("./DISABLE-FONT-CHECK-WARNING.1", "w", encoding="utf-8") as f:
                    f.write("")
            except Exception as e:
                Logger.error(
                    f"Failed to generate DISABLE-FONT-CHECK-WARNING.1! Caused: {e!r}",
                )

        if self._project is None or self._projectSettings is None:
            self.newProject()

    def closeEvent(self, event: QCloseEvent) -> None:
        debugLog("CloseEvent triggered 🤓")
        if self.close():
            event.accept()
            return
        event.ignore()

    def close(self) -> bool:
        debugLog("Creating Message Box to request close...")
        msgbox: QMessageBox = QMessageBox(
            QMessageBox.Icon.Information,
            getLangJson("MessageBox")["msgbox.title.info"],
            getLangJson("MessageBox")["msgbox.info.sureToExit"],
            buttons=QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel,
        )
        msgbox.setWindowIcon(self.windowIcon())
        debugLog("Executing Message Box and asking user done or cancel...")
        if msgbox.exec() == QMessageBox.StandardButton.Yes:

            debugLog("Attmepting to save screen size... 😁")
            settingObject.setValue("screen_size", [self.width(), self.height()])
            debugLog("Saved screen size! 🐔")
            debugLog("Attempting to close threads 🤓")
            self.hide()
            self.editorThread.quit()
            self.editorThread.wait()
            self.dirThread.quit()
            self.dirThread.wait()
            debugLog("Successfully to close threads ✅")
            debugLog("Saving session...")
            beforeRead: Dict[str, int | List[int]] = {}
            for i in self.tabTextEdits:
                if (
                    hasattr(i, "nowFilename")
                    and hasattr(i, "textCursor")
                    and isinstance(i, SinotePlainTextEdit)
                ):
                    if (
                        i.nowFilename is not None
                        and Path(i.nowFilename).exists()
                        and Path(i.nowFilename).is_file()
                    ):
                        result: list[int] | int | None = None
                        cursor = i.textCursor()
                        if len(cursor.selectedText()) > 0:
                            result = [
                                min(cursor.selectionStart(), cursor.selectionEnd()),
                                max(cursor.selectionStart(), cursor.selectionEnd()),
                            ]
                            if result[1] > len(i.toPlainText()):
                                result = 0
                        else:
                            result = cursor.position()
                        beforeRead[i.nowFilename] = result
            if self._projectSettings:
                self._projectSettings["recentlyWorks"] = beforeRead
                if hasattr(self.textEditArea.currentWidget(), "nowFilename"):
                    self._projectSettings["nowWorks"] = (
                        self.textEditArea.currentWidget().nowFilename
                    )
                else:
                    self._projectSettings["nowWorks"] = None
            settingObject.setValue("recently_project_path", self._project)
            debugLog("Saved session!")
            debugLog("Closing window... 🤔")
            self.destroy()
            debugLog("Quitting QApplication... 😄")
            application.quit()
            return True
        return False

    def openProject(
        self,
    ) -> (
        None
    ):  # NOQA, always against PEP 8, who can change my camelCase code to snake_case
        get = QFileDialog.getExistingDirectory(
            self, getLangJson("EditorUI")["editor.window.files.openproj"]
        )
        if get:
            debugLog(f"Got directory: {get} ✔")
            debugLog("Getting project settings...")
            project_setting: dict[str, Any] = ProjectSettings(get).getProjectSettings()

            if project_setting is None:
                QMessageBox.critical(
                    self,
                    getLangJson("MessageBox")["msgbox.title.error"],
                    getLangJson("MessageBox")["msgbox.error.openProjFailed"],
                    buttons=QMessageBox.StandardButton.Ok,
                )
                return

            debugLog("Successfully got!")

            self._openProject(get)

    def _openProject(self, directory: str) -> None:
        debugLog("Saving changes... 🀄")
        self.editorThread.saveThings()
        debugLog("Save changes successfully! ✔")
        debugLog("Clearing all the documents...")
        self.textEditArea.clear()
        for place, widget in enumerate(self.tabTextEdits):
            if hasattr(widget, "deleteLater"):
                try:
                    widget.blockSignals(True)
                    widget.setParent(None)
                    widget.destroy()
                    self.tabTextEdits[place] = None
                except RuntimeError:
                    self.tabTextEdits[place] = None
        debugLog("Cleared all the documents! ✔")
        self._project = directory
        self._projectSettings = ProjectSettings(directory)
        self.dirThread.setDirectory(directory)
        self.commandBar.projectName.setText(self._projectSettings["name"])

    def tempOpenFile(self) -> None:
        """
        Only a port, this function will be removed
        :return: None
        """
        get, _ = QFileDialog.getOpenFileName(
            self,
            getLangJson("EditorUI")["editor.window.temps.openfile"],
            filter="All File (*)",
        )
        if get:
            debugLog(f"Get FileDialog return Information: {get} ✅")
            debugLog("Saving changes... 🪲")
            self.textEditArea.currentWidget().autoSave()
            debugLog("Save changes successfully! ✅")
            self.textEditArea.currentWidget().readFile(get)

    def saveAs(self) -> None:
        get, _ = QFileDialog.getSaveFileName(
            self,
            getLangJson("EditorUI")["editor.window.temps.saveas"],
            filter="All File (*)",
        )
        if get:
            debugLog(f"Get FileDialog return Information: {get} 😍")
            with open(get, "w+", encoding="utf-8") as f:
                f.write(self.textEditArea.currentWidget().toPlainText())
            debugLog("Successfully to save! ✅")

    def _requestClose(self, index: int):
        if 0 <= index < len(self.tabTextEdits):
            self.tabTextEdits.remove(self.textEditArea.widget(index))
            self.textEditArea.removeTab(index)

    def _createRecommendFile(self):
        self.createTab()

    def createTab(
        self, filename: str | None = None, position: int = None
    ) -> SinotePlainTextEdit:
        debugLog(
            f"Creating Tab... Will load file: {filename if filename else "Nothing"} 🤓"
        )
        oldDatetime = datetime.now()
        temp = SinotePlainTextEdit()
        temp.num = len(self.tabTextEdits)
        if not Path(filename if filename else "").exists():
            filename = None
        if filename:
            temp.readFile(filename)
        if position and isinstance(position, int):
            cursor: QTextCursor = temp.textCursor()
            cursor.setPosition(position)
            temp.setTextCursor(cursor)
        elif position and isinstance(position, list):
            cursor: QTextCursor = temp.textCursor()
            cursor.setPosition(position[0])
            cursor.movePosition(
                QTextCursor.MoveOperation.Right,
                QTextCursor.MoveMode.KeepAnchor,
                position[1] - position[0],
            )
            temp.setTextCursor(cursor)
        self.tabTextEdits.append(temp)
        self.textEditArea.addTab(
            temp,
            (
                getLangJson("EditorUI")["editor.tab.new_file"]
                if not filename
                else str(Path(filename).name)
            ),
        )
        temp.setFilename = lambda index, path: self.textEditArea.tabBar().setTabText(
            index, Path(path).name
        )
        debugLog(
            f"Successfully to create tab! Used: {(datetime.now() - oldDatetime).total_seconds():.2f}s ✅"
        )
        debugLog("Attempting to update setting... 😍")
        self.applySettings()
        debugLog("Successfully to update setting! ✅")
        self.textEditArea.setCurrentIndex(self.textEditArea.indexOf(temp))
        return temp

    def applySettings(self):
        fontSize: int = settingObject.getValue("fontSize")
        fontName: str = settingObject.getValue("fontName")
        fallbackFont: str = settingObject.getValue("fallbackFont")
        fallBack: bool = settingObject.getValue("useFallback")
        debugLog(
            f"Font Size: {fontSize}, Font Name: {fontName}, Fallback Font: {fallbackFont} 😍"
        )
        for tab, temp in enumerate(self.tabTextEdits, 1):
            if temp:
                debugLog(f"Setting tab {tab}... 🤔")
                temporary = QFont(fontName, fontSize)
                if fallBack:
                    temporary = QFont(fallbackFont, fontSize)
                    temp.setStyleSheet(
                        f'{temp.styleSheet()} font-family:"{fontName}", "{fallbackFont}"; font-size: {fontSize}pt;'
                    )
                else:
                    temp.setStyleSheet(
                        f"{temp.styleSheet()} font-family: {fontName}; font-size: {fontSize}pt;"
                    )
                temp.setFont(temporary)
        debugLog("Successfully to set tab! ✅")

    def _initBase(self):
        debugLog("Initializing Base Window... 🔎")
        self.setWindowTitle("Sinote")
        width, height = settingObject.getValue("screen_size")
        debugLog(f"Saved size: width {width}, height {height}")
        self.resize(width, height)
        debugLog("Successfully to initialize ✅")
