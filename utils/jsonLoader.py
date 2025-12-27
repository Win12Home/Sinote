from pathlib import Path
from json import JSONDecodeError
from json import loads as normalLoads
from json5 import loads
from utils.argumentParser import debugMode
from utils.logger import addLog
import hashlib
import pickle

Path("./cache").mkdir(exist_ok=True)


def getFileHash(filePath: str):
    try:
        with open(filePath, "rb") as f:
            return hashlib.md5(f.read()).hexdigest()
    except Exception:
        return ""


def load(filePath: str):
    cachePath = (
        Path("./cache") / f"{filePath.replace("/", "_").replace("\\", "_")}.cache"
    )
    fileHash = getFileHash(filePath)

    if cachePath.exists():
        try:
            with open(cachePath, "rb") as f:
                cachedData = pickle.load(f)
                if debugMode:
                    addLog(
                        3,
                        f"File HASH: {cachedData["savedHash"]}",
                        "JsonCacheLoadActivity",
                    )
                    addLog(3, f"Now File HASH: {fileHash}")
                if cachedData["savedHash"] == fileHash:
                    if debugMode:
                        addLog(
                            3,
                            "File HASH is same as the file will be load! Cache hit! 💥",
                            "JsonCacheLoadActivity",
                        )  # Hash is good!
                    return cachedData["ohMyData"]
        except Exception:
            pass

    try:
        with open(filePath, "r", encoding="utf-8") as f:
            content = f.read()
        try:
            data = normalLoads(content)
        except JSONDecodeError:
            data = loads(content)

        cacheData = {"savedHash": fileHash, "ohMyData": data}

        try:
            with open(cachePath, "wb") as f:
                if debugMode:
                    addLog(3, "Dumping and writing cache! 🤔", "JsonCacheLoadActivity")
                pickle.dump(cacheData, f)
        except Exception as e:
            addLog(1, f"Cannot write cache: {repr(e)}", "JsonCacheLoadActivity")

        return data
    except Exception:
        return {}
