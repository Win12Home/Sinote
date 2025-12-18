"""
Sinote: Code Smartly, User Interface Intuitive
Sinote Version 0.06.25530 (Real Version: sinote-2025.1.00842-initial-preview-beta)
3rd Party License saved at ./3rd-party-license

Win12Home (C) 2025, MIT.

Sorry, my english bad OvO.
Because I'm a child TAT.
AI help me to finish 15% of these code! (Not included plugins, before 25%, rewrite SpacingSupportEdit object!!!!!!!!!!!!!!! UwU I'm proud)
"""
### The Sinote Main Script
from Widgets import MainWindow, addLog, saveLog, application, loadFonts, setGlobalUIFont, AutoLoadPlugin, args, \
    beforeDatetime, datetime, SplashScreen, AutoLoadPlugin, autoRun, partial, owLog, addLogClassic
import sys

def startMainProcess(splashScreen: SplashScreen):
    loadFonts()
    a = MainWindow()
    splashScreen.close()
    a.show()
    setGlobalUIFont()
    a.themeChanged.connect(lambda: {
        setGlobalUIFont(),
        addLog(0, "Successfully to change theme!")
    })

def appStart(silent: bool = False):
    if silent:
        addLog = owLog
    else:
        addLog = addLogClassic
    if "--only-create-cache" in args:
        LoadPlugin = AutoLoadPlugin()
        LoadPlugin.run()  # Block main process
        addLog(0, "Successfully to create caches!")
        sys.exit(0)
    splash = SplashScreen()
    splash.show()
    LoadPlugin = AutoLoadPlugin()
    LoadPlugin.loadTotal.connect(splash.setTotal)
    LoadPlugin.loadedOne.connect(splash.addOne)
    LoadPlugin.loadNameChanged.connect(splash.setPluginName)
    LoadPlugin.processFinished.connect(lambda: [
        splash.finishedPluginLoad(),
        startMainProcess(splash)
    ])
    LoadPlugin.start()
    application.exec()
    addLog(0, f"Successfully to exit Sinote! Used time: {(datetime.now() - beforeDatetime).total_seconds():.2f}s ✅")
    if "--record-log" in args or "-rl" in args:
        saveLog()
    sys.exit(0)

if __name__ == "__main__":
    appStart()