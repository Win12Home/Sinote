"""
Sinote: Code Smartly, User Interface Intuitive
Sinote Version 0.06.25530 (Real Version: sinote-2025.1.00842-initial-preview-beta)
3rd Party License saved at ./3rd-party-license

Win12Home (C) 2025, MIT.

Sorry, my english bad OvO.
Because I'm a child TAT.
AI help me to finish 25% of these code! (Not included plugins)
"""
### The Sinote Main Script
from Widgets import MainWindow, addLog, saveLog, application, loadFonts, setGlobalUIFont, automaticLoadPlugin, args, beforeDatetime, datetime
import sys

if __name__ == "__main__":
    automaticLoadPlugin()
    if "--only-create-cache" in args:
        addLog(0, "Successfully to create caches!")
        sys.exit(0)
    loadFonts()
    setGlobalUIFont()
    a = MainWindow()
    a.show()
    application.exec()
    addLog(0, f"Successfully to exit Sinote! Used time: {(datetime.now() - beforeDatetime).total_seconds():.2f}s ✅")
    sys.exit(0)