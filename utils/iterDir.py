"""
Full of shit!
"""

from pathlib import Path
from typing import Any, List

from PySide6.QtGui import QIcon
from utils.withObjects import RecursionLimitChanger


def iterDirCore(
    directory: str = None,
) -> List[List[QIcon.ThemeIcon | str | List[Any]]]:  # NOQA, Trying typing module
    iters: List[List[QIcon.ThemeIcon | str | List[Any]]] = []
    for i in Path(directory).iterdir():
        if i.is_dir():
            iters.append(
                [QIcon.ThemeIcon.FolderNew, str(i.name), str(i), iterDirCore(str(i))]
            )
            continue
        iters.append([QIcon.ThemeIcon.DocumentNew, str(i.name), str(i)])
    return iters


def iterDir(
    directory: str = None,
) -> List[List[QIcon.ThemeIcon | str | List[Any]]]:  # NOQA, against PEP 8
    """
    Iter directory
    :param directory: Directory Path
    :return: like that
    if structure:
        proj|
            | abc1|
                 abc
            abc2
    returns:
    [[QIcon.ThemeIcon.FolderNew, "proj/abc", [[QIcon.ThemeIcon.DocumentNew, "proj/abc/abc"]]], [QIcon.ThemeIcon.DocumentNew, "proj/abc"]]
    :raises: Maybe raise out PermissionError or FileNotFoundError. However, you only need to add a try-except check.
    """
    with RecursionLimitChanger(pow(2, 31) - 1):
        return iterDirCore(directory)
