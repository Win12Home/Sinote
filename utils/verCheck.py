import sys


def verCheck() -> None:
    # Check version
    try:
        if int(sys.version.split(" ")[0].split(".")[1]) < 12:
            raise SystemError(
                f"Sinote needed Python 3.12 and above, not {sys.version.split(" ")[0]}"
            )
    except Exception as e:
        print(f"[red]Error:[/red] {e!r}")
        sys.exit(1)
