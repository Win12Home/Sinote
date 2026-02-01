"""
Easy, wow.
"""

from datetime import datetime, timedelta
from math import ceil


def getUtcString() -> str:
    offset: timedelta = datetime.now() - datetime.utcnow()
    if isinstance(offset, timedelta):
        return f"UTC+{ceil(offset.seconds/3600) if ceil(offset.seconds/3600) < 24 else 0}:00"
    return r"UTC+0:00"
