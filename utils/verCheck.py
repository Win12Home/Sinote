from rich import print
import sys


def verCheck() -> None:
    # Check version
    try:
        if int(sys.version.split(" ")[0].split(".")[1]) < 13:
            raise SystemError(
                f"Sinote needed Python 3.13 and above, not {sys.version.split(" ")[0]}, Python 3.12 will be halted when loading fonts."
            )
    except SystemError as e:
        print(f"[red]Error:[/red] {e!r}")
        sys.exit(1)
    except Exception as e:
        print(f"[red]Error when resolving python version:[/red] {e!r}")
        print(f"[blue]Sinote[/blue] will be [yellow]continue[/yellow] running")
