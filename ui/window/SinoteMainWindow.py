from PySide6.QtWidgets import (
    QMainWindow,
    QStackedWidget,
    QWidget,
    QTreeWidget,
    QTabWidget,
    QPushButton,
    QMenu,
    QMenuBar,
    QHBoxLayout,
    QVBoxLayout,
    QScrollArea,
    QLabel,
    QMessageBox,
    QListWidgetItem,
    QFileDialog,
    QListWidget,
)
from core.addons.applyStylesheet import applyStylesheet
from ui.edit.SinotePlainTextEdit import SinotePlainTextEdit
from PySide6.QtCore import Qt, Signal, QObject, QEvent
from core.addons.Shortcut import Shortcut
from ui.edit.AutomaticSaveThingsThread import AutomaticSaveThingsThread
from utils.argumentParser import fileargs, args
from functools import partial
from utils.logger import addLog
from PySide6.QtGui import (
    QIcon,
    QAction,
    QFont,
    QKeyEvent,
    QPixmap,
    QCloseEvent,
    QTextCursor,
)
from ui.SettingObject import *
from ui.widgets import PluginInfoLister, SeperatorWidget
from utils.application import application
from ui.selfLogger import debugLog
from utils.config import settingObject
from pathlib import Path
from core.i18n import loadJson, basicInfo, lang
from core.AutoLoadPluginThread import loadedPlugin, autoRun
from utils.timer import beforeDatetime
from core.addons.setGlobalUIFont import isRecommendFont
from utils.iterDir import iterDir
from typing import Dict, Any, List, Optional
from datetime import datetime


class MainWindow(QMainWindow):
    themeChanged: Signal = Signal()

    def __init__(self, initialized: bool = False):
        super().__init__()
        self.shortcut = Shortcut()
        self.widget = QStackedWidget()
        self.mainFrame = QWidget()
        self.settingFrame = QWidget()
        self.editorThread = AutomaticSaveThingsThread(
            self, settingObject.getValue("secsave")
        )
        self.setWindowIcon(QIcon("./resources/icon.png"))
        self.setCentralWidget(self.widget)
        self._initBase()
        self._setupUI()
        self._setupTab()
        if not initialized:
            self._automaticSetTheme()
        self._autoApplyPluginInfo()

    def _setupTab(self):
        if not isinstance(settingObject.getValue("beforeread"), dict):
            settingObject.setValue("beforeread", dict({}))
        if len(settingObject.getValue("beforeread")) or len(fileargs) > 0:
            result: Dict[str, int] = {}
            for fileName, pos in settingObject.getValue("beforeread").items():
                if not Path(fileName).exists():
                    self._createRecommendFile()
                    self.tabTextEdits[len(self.tabTextEdits) - 1].setPlainText(
                        loadJson("EditorUI")["editor.any.cannotreadfile"].format(
                            fileName
                        )
                    )
                else:
                    result[fileName] = pos
                    if isinstance(pos, list) or isinstance(pos, int):
                        self.createTab(fileName, position=pos)
                    else:
                        addLog(
                            2,
                            "Position information has broken! Automatically remove position information.",
                        )
                        self.createTab(fileName)
            for temp in [str(Path(i)) for i in fileargs]:
                if Path(temp).exists():
                    self.createTab(temp)
                else:
                    self._createRecommendFile()
                    self.tabTextEdits[len(self.tabTextEdits) - 1].setPlainText(
                        loadJson("EditorUI")["editor.any.cannotreadfile2"].format(temp)
                    )
            settingObject.setValue("beforeread", result)
        else:
            self._createRecommendFile()

    def _setupUI(self):
        debugLog("Setting up User Interface...")
        debugLog("Setting up Text Edit Area...")
        self.folder: QTreeWidget = QTreeWidget()
        self.folder.setHeaderHidden(True)
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
        # self.horizontalLayout.addWidget(self.folder) Not finished
        self.horizontalLayout.addWidget(self.textEditArea)
        self.horizontalLayout.setStretch(0, 1)
        self.horizontalLayout.setStretch(1, 3)
        self.mainFrame.setLayout(self.horizontalLayout)
        debugLog("Successfully to set up Layout!")
        debugLog("Setting up Menu...")
        self.fileEditMenu = QMenuBar()
        self.fileEditMenu.fileEdit = QMenu(loadJson("EditorUI")["editor.menu.files"])
        self.fileEditMenu.editMenu = QMenu(loadJson("EditorUI")["editor.menu.edit"])
        # Actions Define
        createFile = QAction(
            loadJson("EditorUI")["editor.menu.files.newfile"],
            self,
            icon=QIcon.fromTheme(QIcon.ThemeIcon.DocumentNew),
        )
        createFile.triggered.connect(
            lambda: self.textEditArea.currentWidget().newFile()
        )
        openFile = QAction(
            loadJson("EditorUI")["editor.menu.temps.openfile"],
            self,
            icon=QIcon.fromTheme(QIcon.ThemeIcon.DocumentOpen),
        )
        openFile.triggered.connect(self.tempOpenFile)
        saveAs = QAction(
            loadJson("EditorUI")["editor.menu.files.saveas"],
            self,
            icon=QIcon.fromTheme(QIcon.ThemeIcon.DocumentSaveAs),
        )
        saveAs.triggered.connect(self.saveAs)
        setting = QAction(
            loadJson("EditorUI")["editor.menu.files.settings"],
            self,
            icon=QIcon.fromTheme(QIcon.ThemeIcon.Computer),
        )
        setting.triggered.connect(partial(self.widget.setCurrentIndex, 1))
        exitProg = QAction(
            loadJson("EditorUI")["editor.menu.files.exit"],
            self,
            icon=QIcon.fromTheme(QIcon.ThemeIcon.ApplicationExit),
        )
        exitProg.triggered.connect(self.close)
        self.fileEditMenu.fileEdit.addActions(
            [createFile, openFile, saveAs, setting, exitProg]
        )
        undo = QAction(
            loadJson("EditorUI")["editor.menu.edit.undo"],
            self,
            icon=QIcon.fromTheme(QIcon.ThemeIcon.EditRedo),
        )
        undo.triggered.connect(lambda: self.textEditArea.currentWidget().undo())
        redo = QAction(
            loadJson("EditorUI")["editor.menu.edit.redo"],
            self,
            icon=QIcon.fromTheme(QIcon.ThemeIcon.EditUndo),
        )
        redo.triggered.connect(lambda: self.textEditArea.currentWidget().redo())
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
            loadJson("EditorUI")["editor.title.settings.appearance"]
        )
        self.setArea.appearance.titleAppearance.setStyleSheet(
            "font-size: 38px; font-weight: bold; margin-bottom: 10px;"
        )  # QSS
        self.setArea.appearance.seperator = SeperatorWidget()
        self.setArea.appearance.debugMode = CheckBoxSettingObject(
            None,
            loadJson("EditorUI")["editor.title.setobj.debugmode"],
            loadJson("EditorUI")["editor.desc.setobj.debugmode"],
        )
        self.setArea.appearance.debugMode.checkBox.setText(
            loadJson("EditorUI")["editor.desc.setobj.debugmodeopen"]
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
            loadJson("EditorUI")["editor.title.setobj.language"],
            loadJson("EditorUI")["editor.desc.setobj.language"],
        )
        self.setArea.appearance.language.comboBox.addItems(
            [i for _, i in basicInfo["item.dict.language_for"].items()]
        )
        try:
            self.setArea.appearance.language.comboBox.setCurrentIndex(
                list(basicInfo["item.dict.language_for"].keys()).index(lang)
            )
        except Exception:
            self.setArea.appearance.language.comboBox.setCurrentIndex(0)
        self.setArea.appearance.language.comboBox.currentIndexChanged.connect(
            lambda: {
                settingObject.setValue(
                    "language",
                    list(basicInfo["item.dict.language_for"].keys())[
                        self.setArea.appearance.language.comboBox.currentIndex()
                    ],
                ),
                QMessageBox(
                    QMessageBox.Icon.Information,
                    loadJson("MessageBox")["msgbox.title.info"],
                    loadJson("MessageBox")["msgbox.info.restartApplySet"],
                    buttons=QMessageBox.StandardButton.Ok,
                    parent=self,
                ).exec(),
            }
        )
        self.setArea.appearance.theme = ComboBoxSettingObject(
            None,
            loadJson("EditorUI")["editor.title.setobj.theme"],
            loadJson("EditorUI")["editor.desc.setobj.theme"],
        )
        self.setArea.appearance.theme.comboBox.addItems(
            [
                loadJson("EditorUI")[i]
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
            loadJson("EditorUI")["editor.tab.settings.appearance"],
        )
        # Plugin Setting
        self.setArea.plugins = QScrollArea()
        self.setArea.plugins.vLayout = QVBoxLayout()
        self.setArea.plugins.titlePlugins = QLabel(
            loadJson("EditorUI")["editor.title.settings.plugin"]
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
            self.setArea.plugins, loadJson("EditorUI")["editor.tab.settings.plugin"]
        )
        # Editor Font Setting
        self.setArea.edfont = QScrollArea()
        self.setArea.edfont.vLayout = QVBoxLayout()
        self.setArea.edfont.titleEditorFont = QLabel(
            loadJson("EditorUI")["editor.tab.settings.editorfont"]
        )
        self.setArea.edfont.titleEditorFont.setStyleSheet(
            "font-size: 38px; font-weight: bold; margin-bottom: 10px;"
        )
        self.setArea.edfont.seperator = SeperatorWidget()
        self.setArea.edfont.fontSelect = ComboBoxSettingObject(
            None,
            loadJson("EditorUI")["editor.title.setobj.fontname"],
            loadJson("EditorUI")["editor.desc.setobj.fontname"],
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
            loadJson("EditorUI")["editor.title.setobj.fontsize"],
            loadJson("EditorUI")["editor.desc.setobj.fontsize"],
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
            loadJson("EditorUI")["editor.suffix.settings.size"]
        )
        self.setArea.edfont.fallbackSelect = ComboBoxSettingObject(
            None,
            loadJson("EditorUI")["editor.title.setobj.fbfont"],
            loadJson("EditorUI")["editor.desc.setobj.fbfont"],
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
            loadJson("EditorUI")["editor.title.setobj.usefbfont"],
            loadJson("EditorUI")["editor.desc.setobj.usefbfont"],
        )
        self.setArea.edfont.useFallbackFont.checkBox.setText(
            loadJson("EditorUI")["editor.desc.setobj.usefbfontopen"]
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
            self.setArea.edfont, loadJson("EditorUI")["editor.tab.settings.editorfont"]
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
        debugLog("Successfully to add frame!")
        debugLog("Adding shortcuts...")
        self.shortcut.addItem([Qt.Key.Key_Control, Qt.Key.Key_Alt, Qt.Key.Key_S], 1)
        self.shortcut.addItem([Qt.Key.Key_Control, Qt.Key.Key_N], 2)
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
        elif itemNum == 2:
            self.textEditArea.currentWidget().newFile()
        elif itemNum == 3:
            self.saveAs()
        elif itemNum == 4:
            self.close()

    def eventFilter(self, obj: QObject, event: QEvent) -> bool:
        if event.type() == QEvent.Type.KeyPress:
            self.shortcut.keyPressEvent(event)
        elif event.type() == QEvent.Type.KeyRelease:
            self.shortcut.keyReleaseEvent(event)
        return False

    def keyPressEvent(self, event: QKeyEvent) -> None:
        self.shortcut.keyPressEvent(event)
        super().keyPressEvent(event)

    def keyReleaseEvent(self, event: QKeyEvent) -> None:
        self.shortcut.keyReleaseEvent(event)
        super().keyReleaseEvent(event)

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
            applyStylesheet(
                application, 0 if not theme else 1
            )
            settingObject.setValue("theme", theme)
            self.applySettings()
            self.themeChanged.emit()

    def _automaticSetTheme(self) -> None:
        if not ("--no-theme" in args or "-nt" in args):
            applyStylesheet(
                application,
                (
                    0
                    if not settingObject.getValue("theme")
                    else 1
                ),
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
        addLog(
            0,
            f"Used {(datetime.now() - beforeDatetime).total_seconds():.2f}s to load!",
            "SinoteUserInterfaceActivity",
            True,
        )
        debugLog("Show Application Successfully!")
        debugLog("Preparing to run AutoRuns...")
        [i() for i in autoRun if isinstance(i, partial)]
        """
        Easy but it will return a list that per value all is NoneType.
        You can replace it to:
        for i in autoRun:
            if isinstance(i, partial):
                i()
        """
        self.applySettings()
        if isRecommendFont() and not Path("./DISABLE-FONT-CHECK-WARNING").exists():
            """
            I want to make user to experience the HURT of the EXTERNALLY_MANAGED! (Of course I use Windows)

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
            msgbox = QMessageBox(
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
                addLog(
                    2,
                    f"Failed to generate DISABLE-FONT-CHECK-WARNING.1! Caused: {repr(e)}",
                )

    def closeEvent(self, event: QCloseEvent) -> None:
        debugLog("CloseEvent triggered 🤓")
        if self.close():
            event.accept()
            return
        event.ignore()

    def close(self) -> bool:
        msgbox: QMessageBox = QMessageBox(
            QMessageBox.Icon.Information,
            loadJson("MessageBox")["msgbox.title.info"],
            loadJson("MessageBox")["msgbox.info.sureToExit"],
            buttons=QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel,
        )
        msgbox.setWindowIcon(self.windowIcon())
        if msgbox.exec() == QMessageBox.StandardButton.Yes:
            debugLog("Saving session...")
            beforeRead: Dict[str, int | List[int]] = {}
            for i in self.tabTextEdits:
                if hasattr(i, "nowFilename") and hasattr(i, "textCursor"):
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
            settingObject.setValue("beforeread", beforeRead)
            debugLog("Saved session!")
            debugLog("Attempting to close 🤓")
            self.hide()
            self.editorThread.quit()
            self.editorThread.wait()
            debugLog("Successfully to close ✅")
            self.destroy()
            application.quit()
            return True
        return False

    def openProject(self) -> None:
        raise NotImplementedError('Function "openProject" isn\'t implemented.')

    def tempOpenFile(self) -> None:
        """
        This method will be replaced by openProject
        :return: None
        """
        get, _ = QFileDialog.getOpenFileName(
            self,
            loadJson("EditorUI")["editor.window.temps.openfile"],
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
            loadJson("EditorUI")["editor.window.temps.saveas"],
            filter="All File (*)",
        )
        if get:
            debugLog(f"Get FileDialog return Information: {get} 😍")
            with open(get, "w+", encoding="utf-8") as f:
                f.write(self.textEditArea.currentWidget().toPlainText())
            debugLog("Successfully to save! ✅")

    def _requestClose(self, index: int):
        if index >= 0 and index < len(self.tabTextEdits):
            self.tabTextEdits[index] = None
            self.textEditArea.removeTab(index)
            if self.textEditArea.tabBar().count() == 0:
                self.close()

    def _createRecommendFile(self):
        self.createTab()

    def createTab(self, filename: str | None = None, position: int = None):
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
                loadJson("EditorUI")["editor.tab.new_file"]
                if not filename
                else str(Path(filename))
            ),
        )
        temp.setFilename = self.textEditArea.tabBar().setTabText
        self.textEditArea.setCurrentIndex(len(self.tabTextEdits) - 1)
        debugLog(
            f"Successfully to create tab! Used: {(datetime.now() - oldDatetime).total_seconds():.2f}s ✅"
        )
        debugLog("Attempting to update setting... 😍")
        self.applySettings()
        debugLog("Successfully to update setting! ✅")

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
        self.resize(1280, 760)
        debugLog("Successfully to initialize ✅")
