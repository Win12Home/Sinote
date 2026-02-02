import sys
from datetime import datetime

from core.addons.loadFonts import loadFonts
from core.addons.setGlobalUIFont import setGlobalUIFont
from core.AutoLoadPluginThread import AutoLoadPlugin
from core.i18n import setLanguage, baseInfo
from ui.window.SinoteMainWindow import MainWindow
from ui.window.SplashScreen import SplashScreen
from utils.application import application
from utils.argumentParser import args
from utils.logger import Logger, saveLog, setOwLog
from utils.timer import beforeDatetime


def startMainProcess(splashScreen: SplashScreen) -> None:
    loadFonts()
    a = MainWindow()
    splashScreen.close()
    setGlobalUIFont()
    a.show()
    a.themeChanged.connect(
        lambda: {setGlobalUIFont(), Logger.info("Successfully to change theme!")}
    )


def appStart(silent: bool = False):
    if silent:
        setOwLog()
    if "--only-create-cache" in args:
        LoadPlugin = AutoLoadPlugin()
        LoadPlugin.run()  # Block main process
        Logger.info("Successfully to create caches!")
        sys.exit(0)
    setLanguage()
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
    Logger.info(
        f"Successfully to exit Sinote! Used time: {(datetime.now() - beforeDatetime).total_seconds():.2f}s ✅",
    )
    if "--record-log" in args or "-rl" in args:
        saveLog()
    sys.exit(0)
