from enum import Enum
from typing import Any


class SafetyList(list):
    """
    A Safety dictionary
    """

    class OutErrors(Enum):
        NotFoundInIndex = -1

    def index(
        self, __value: Any, __start: int = 0, __end: int = None
    ) -> int | OutErrors:
        """
        Like dict.get, index the __value if __value in the list. If not, return SafetyList.OutErrors.NotFoundInIndex
        :param __value: restored from __doc__
        :param __start: restored from __doc__
        :param __end: restored from __doc__
        :return: restored from __doc___
        """
        if (
            __value not in self[__start:__end]
            if __end is not None
            else __value not in self[__start:]
        ):
            return self.OutErrors.NotFoundInIndex
        return super().index(
            __value, __start, __end if __end is not None else len(self)
        )


class SafetyDict(dict):
    """
    A safety dictionary for language load
    It won't be raise KeyError at all!
    Like {"abc":"def"}
    dict_Initialized["abd"] -> return "abd"
    """

    class Properties(Enum):
        ReturnNormalItem = 0
        ReturnNormalize = 1

    def __getitem__(self, item: Any) -> Any:
        return self.get(item, item)
