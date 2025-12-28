"""
Easy, wow.
"""

from datetime import datetime, timedelta


def getUtcString() -> str:
    timezoneOffset: timedelta | None = datetime.now().utcoffset()
    if timezoneOffset:
        hours, ignoredMinutes = divmod(
            timezoneOffset.total_seconds(), 60 * 60
        )  # Always equals 3600.
        minutes, _ = divmod(ignoredMinutes, 60)  # Seconds? Ignore it!
        return f"UTC{"+" if hours >= 0 else "-"}{int(abs(hours)):02}:{int(abs(minutes)):02}"
    return f"UTC+0:00"
