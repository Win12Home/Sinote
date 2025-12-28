"""
Sinote: Code Smartly, User Interface Intuitive
Sinote Version 0.06.26001
3rd Party License saved at ./3rd-party-license

Win12Home (C) 2025, MIT.

Sorry, my english bad OvO.
Because I'm a child TAT.
AI help me to finish 15% of these code! (Not included plugins, before 25%, rewrite SpacingSupportEdit object!!!!!!!!!!!!!!! UwU I'm proud)
"""

### The Sinote Main Script

from core.excepthook import setExceptionHook
from core.addons.asciiOutput import asciiOutput
from utils.verChecker import verChecker
from utils.sinoteScript import appStart


if __name__ == "__main__":
    verChecker()
    setExceptionHook()
    asciiOutput()
    appStart(silent=False)
