import hashlib
import pickle
from base64 import urlsafe_b64encode as b64
from json import JSONDecodeError
from json import loads as normalLoads
from pathlib import Path

from json5 import loads
from utils.argumentParser import debugMode
from utils.logger import Logger

Path("./cache").mkdir(exist_ok=True)


def getFileHash(filePath: str):
    try:
        with open(filePath, "rb") as f:
            return hashlib.md5(f.read()).hexdigest()
    except Exception:
        return ""


def load(filePath: str):  # Use list to save cache, 2026-01-13
    cachePath = (
        Path("./cache")
        / f"{b64(Path(filePath).as_posix().__str__().encode()).decode()}.cache"
    )  # Safety than os.path.abspath, and it's same! (WTF)
    fileHash = getFileHash(filePath)

    if cachePath.exists():
        try:
            with open(cachePath, "rb") as f:
                cachedData: list[str | dict | list] = pickle.load(f)
                if debugMode:
                    Logger.debug(
                        f"File HASH: {cachedData[0]}",
                        "JsonCacheLoadActivity",
                    )
                    Logger.debug(f"Now File HASH: {fileHash}")
                if cachedData[0] == fileHash:
                    if debugMode:
                        Logger.debug(
                            "File HASH is same as the file will be load! Cache hit! 💥",
                            "JsonCacheLoadActivity",
                        )  # Hash is good!
                    return cachedData[1]
        except Exception as e:
            Logger.warning(
                f"Failed to load cache, reason: {e!r}", "JsonCacheLoadActivity"
            )

    try:
        with open(filePath, "r", encoding="utf-8") as f:
            content = f.read()
        try:
            data = normalLoads(content)
        except JSONDecodeError:
            data = loads(content)

        cacheData: list[str | dict | list] = [fileHash, data]

        try:
            with open(cachePath, "wb") as f:
                if debugMode:
                    Logger.debug(
                        "Dumping and writing cache! 🤔", "JsonCacheLoadActivity"
                    )
                pickle.dump(cacheData, f, protocol=pickle.HIGHEST_PROTOCOL)
        except Exception as e:
            Logger.warning(
                f"Cannot write cache file {Path(cachePath).name} of file {Path(filePath).name}: {e!r}",
                "JsonCacheLoadActivity",
            )

        return data
    except Exception:
        return {}
