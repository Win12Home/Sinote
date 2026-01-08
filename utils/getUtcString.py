"""
Easy, wow.
"""

from datetime import datetime, timedelta, timezone
from math import ceil


def getUtcString() -> str:
    offset: timedelta = datetime.now() - datetime.utcnow()
    if isinstance(offset, timedelta):
        return f"UTC+{ceil(offset.seconds/3600)}:00"
    return r"UTC+0:00"
