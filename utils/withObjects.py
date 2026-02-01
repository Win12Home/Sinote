import sys


class RecursionLimitChanger:  # with RecursionLimitChanger() for change recursion limit and left changes when exit
    def __init__(self, limit: int = 10000):
        self._limit: int = limit
        self._originalLimit: int = sys.getrecursionlimit()

    def __enter__(self) -> None:
        sys.setrecursionlimit(self._limit)

    def __exit__(self, type, value, tb) -> None:
        sys.setrecursionlimit(self._originalLimit)
