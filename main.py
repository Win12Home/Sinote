"""
Sinote: Code Smartly, User Interface Intuitive
Sinote Version 0.06.26017
3rd Party License saved at ./3rd-party-license

Win12Home (C) 2025, 2026. MIT License.

Sorry, my english bad OvO.
Because I'm a child TAT.
AI help me to finish 15% of these code, WTF (BABABOY)
"""

# The Sinote Main Script

from core.addons.asciiOutput import asciiOutput
from core.excepthook import setExceptionHook
from utils.signal import analyzeAllSignal
from utils.sinoteScript import appStart
from utils.verCheck import verCheck

if __name__ == "__main__":
    verCheck()
    setExceptionHook()
    asciiOutput()
    analyzeAllSignal()
    appStart(silent=False)
