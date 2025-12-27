from utils.timer import beforeDatetime
from core.addons.setGlobalUIFont import setGlobalUIFont
from utils.argumentParser import args
from ui.window.SplashScreen import SplashScreen
from ui.window.SinoteMainWindow import MainWindow
from utils.logger import setOwLog, addLog, saveLog
from datetime import datetime
from core.addons.loadFonts import loadFonts
from core.AutoLoadPluginThread import AutoLoadPlugin
from utils.application import application
from core.i18n import resetBasicInfo, setLanguage
import sys


def startMainProcess(splashScreen: SplashScreen) -> None:
    loadFonts()
    a = MainWindow()
    splashScreen.close()
    a.show()
    setGlobalUIFont()
    a.themeChanged.connect(
        lambda: {setGlobalUIFont(), addLog(0, "Successfully to change theme!")}
    )


def appStart(silent: bool = False):
    if silent:
        setOwLog()
    if "--only-create-cache" in args:
        LoadPlugin = AutoLoadPlugin()
        LoadPlugin.run()  # Block main process
        addLog(0, "Successfully to create caches!")
        sys.exit(0)
    setLanguage()
    resetBasicInfo()
    splash = SplashScreen()
    splash.show()
    LoadPlugin = AutoLoadPlugin()
    LoadPlugin.loadTotal.connect(splash.setTotal)
    LoadPlugin.loadedOne.connect(splash.addOne)
    LoadPlugin.loadNameChanged.connect(splash.setPluginName)
    LoadPlugin.processFinished.connect(
        lambda: [splash.finishedPluginLoad(), startMainProcess(splash)]
    )
    LoadPlugin.start()
    application.exec()
    addLog(
        0,
        f"Successfully to exit Sinote! Used time: {(datetime.now() - beforeDatetime).total_seconds():.2f}s ✅",
    )
    if "--record-log" in args or "-rl" in args:
        saveLog()
    sys.exit(0)
