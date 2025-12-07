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
from Widgets import MainWindow, addLog, saveLog, application, loadFonts, setGlobalUIFont
import sys

if __name__ == "__main__":
    loadFonts()
    setGlobalUIFont()
    a = MainWindow()
    a.show()
    application.exec()
    addLog(0, "Successfully to exit Sinote with Process Code 0 ✅")
    saveLog()
    sys.exit(0)