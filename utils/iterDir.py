"""
Full of shit!
"""

from typing import List, Any, Union
from PySide6.QtGui import QIcon
from pathlib import Path


def iterDir(directory: str = None) -> List[Union[QIcon.ThemeIcon, str, List[Any]]]:
    """
    Iter directory
    :param directory: Directory Path
    :return: like that
    if structure:
        proj|
            | abc|
                 abc
            abc
    returns:
    [[QIcon.ThemeIcon.FolderNew, "proj/abc", [[QIcon.ThemeIcon.DocumentNew, "proj/abc/abc"]]], [QIcon.ThemeIcon.DocumentNew, "proj/abc"]]
    :raises: Maybe raise out PermissionError or FileNotFoundError.
    """
    iters: List[QIcon.ThemeIcon, str, List[Any]] = []
    for i in Path(directory).iterdir():
        if i.is_dir():
            iters.append([QIcon.ThemeIcon.FolderNew, str(i), iterDir(str(i))])
            continue
        iters.append([QIcon.ThemeIcon.DocumentNew, str(i)])
    return iters
