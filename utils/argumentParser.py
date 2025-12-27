from utils.logger import setOwLog, addLog, setNoColor
from utils.err import err
from PySide6.QtWidgets import QMessageBox, QApplication
from getpass import getuser
from platform import system
import sys

debugMode: bool = False
onlyWarning: bool = False
colored: bool = True

# basicInfo will be BaseInfo.json
basicInfo: dict = {}

# Check Arguments


# Look at the system
args = [i.lower() for i in sys.argv[1:] if i.lower().startswith("-")]
fileargs = [i.lower() for i in sys.argv[1:] if not i.lower().startswith("-")]

if "--debug-mode" in args or "-db" in args:
    debugMode = True
    addLog(3, "Debug Mode Started 😍", "ArgumentParser")

if "--no-color" in args or "-nc" in args:
    colored = False
    setNoColor()

    addLog(3, "No color started 🤔", "ArgumentParser")

if "-h" in args or "--help" in args:  # HelpActivity
    addLog(0, "Sinote Help is starting...", "HelpActivity")
    application: QApplication = QApplication()
    QMessageBox.information(
        None,
        "Help",
        "-h/--help: Arguments Help of Sinote\n-su/--use-root-user: Bypass check for SU User in posix env\n--bypass-system-check: Bypass System Check (Windows, Linux, Mac OS)\n-db/--debug-mode: Use Debug Mode (I/O Performance will low)\n-ow/--only-warning: Only Warning/Error in LOG\n--no-color/-nc: No color when log output\n--only-create-cache: Only create plugin caches\n--no-theme/-nt: Use default style (Windows)",
    )
    addLog(0, "Sinote Help closed, return to normal enviroment.", "HelpActivity")
    addLog(0, "Exiting...")
    sys.exit(application.exec())

if (
    not system().lower() in ["darwin", "linux", "windows"]
    and not "--bypass-system-check" in args
):
    addLog(
        3, "Checked not a Darwin, Linux, NT Based, starting error.", "ArgumentParser"
    )
    addLog(
        2,
        "Your system isn't a Darwin Based, a Linux Based or Windows, cannot continue run safety, use --bypass-system-check to bypass.",
    )
    addLog(3, "Starting error window...", "ArgumentParser")
    application: QApplication = QApplication()
    err("0x00000003")
    application.exec()
    sys.exit(1)

if system().lower() in ["darwin", "linux"]:
    if getuser() == "root":
        addLog(3, "ROOT User detected.", "ArgumentParser")
        addLog(
            1,
            "We recommend to use Normal User in posix env. But use ROOT User is not SAFE for your OS! Please use Normal User Instead! (Excepted you have known it's unsafe or you wanna edit System File like GRUB)",
        )
        addLog(3, "Starting warning window...", "ArgumentParser")
        if not ("--use-root-user" in args or "-su" in args):
            from utils.application import application

            QMessageBox.warning(
                None,
                "Warning",
                "We have noticed you run Sinote by ROOT/SU User, please remove 'sudo' command or exit 'su' environment. \nOr you can append -su for argument to bypass.",
            )

if "-ow" in args or "--only-warning" in args:
    addLog(3, "Only Warning Started 🤓", "ArgumentParser")
    onlyWarning = True
    setOwLog()
