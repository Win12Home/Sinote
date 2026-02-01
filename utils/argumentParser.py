import sys
from getpass import getuser
from platform import system

from PySide6.QtWidgets import QApplication, QMessageBox
from utils.err import err
from utils.logger import Logger, setFunny, setNoColor, setOwLog

debugMode: bool = False
onlyWarning: bool = False
colored: bool = True

# basicInfo will be BaseInfo.json
basicInfo: dict = {}


# Look at the system
args = [i.lower() for i in sys.argv[1:] if i.lower().startswith("-")]

# Look arguments

if "--debug-mode" in args or "-db" in args:
    debugMode = True
    Logger.debug("Debug Mode Started 😍", "ArgumentParser")

if "--no-color" in args or "-nc" in args:
    colored = False
    setNoColor()

    Logger.debug("No color started 🤔", "ArgumentParser")

if "-h" in args or "--help" in args:  # HelpActivity
    Logger.info("Sinote Help is starting...", "HelpActivity")
    application: QApplication = QApplication()
    QMessageBox.information(
        None,
        "Help",
        "-h/--help: Arguments Help of Sinote\n-su/--use-root-user: Bypass check for SU User in posix env\n--bypass-system-check: Bypass System Check (Windows, Linux, Mac OS)\n-db/--debug-mode: Use Debug Mode (I/O Performance will low)\n-ow/--only-warning: Only Warning/Error in LOG\n--no-color/-nc: No color when log output\n--only-create-cache: Only create plugin caches\n--no-theme/-nt: Use default style (Windows)\n--joking-bro: Try it!",
    )
    Logger.info("Sinote Help closed, return to normal enviroment.", "HelpActivity")
    Logger.info("Exiting...")
    sys.exit(0)

if (
    not system().lower() in ["darwin", "linux", "windows"]
    and not "--bypass-system-check" in args
):
    Logger.debug(
        "Checked not a Darwin, Linux, NT Based, starting error.", "ArgumentParser"
    )
    Logger.error(
        "Your system isn't a Darwin Based, a Linux Based or Windows, cannot continue run safety, use --bypass-system-check to bypass.",
    )
    Logger.debug("Starting error window...", "ArgumentParser")
    application: QApplication = QApplication()
    err("0x00000003")
    application.exec()
    sys.exit(1)

if "--joking-bro" in args:
    setFunny()

if system().lower() in ["darwin", "linux"]:
    if getuser() == "root":
        Logger.debug("ROOT User detected.", "ArgumentParser")
        Logger.warning(
            "We recommend to use Normal User in posix env. But use ROOT User is not SAFE for your OS! Please use Normal User Instead! (Excepted you have known it's unsafe or you wanna edit System File like GRUB)",
        )
        Logger.debug("Starting warning window...", "ArgumentParser")
        if not ("--use-root-user" in args or "-su" in args):
            from utils.application import application  # NOQA, QApplication

            QMessageBox.warning(
                None,
                "Warning",
                "We have noticed you run Sinote by ROOT/SU User, please remove 'sudo' command or exit 'su' environment. \nOr you can append -su for argument to bypass.",
            )

if "-ow" in args or "--only-warning" in args:
    Logger.debug("Only Warning Started 🤓", "ArgumentParser")
    onlyWarning = True
    setOwLog()
