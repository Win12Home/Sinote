from datetime import datetime

beforeDatetime: datetime = datetime.now()


def getTotalSeconds() -> float:  # All right, clearly function!
    return (datetime.now() - beforeDatetime).total_seconds()
