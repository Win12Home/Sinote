from typing import Any

from core.plugin.FunctionLexerSet import FunctionLexerSet
from core.plugin.LoadPluginBase import LoadPluginBase
from utils.const import apiVersion
from utils.logger import Logger


class ParseFunctions:
    def __init__(self, funcs: dict, customizeVar: bool = True):
        self._funcs: dict = funcs
        self._customizeVar = customizeVar

    def getValue(self) -> list | None:
        """
        Get list[partial]
        :return: list[partial] or None
        """
        verified: dict[str, tuple[list[Any] | bool]] = {}
        LoadPluginBase.logIfDebug(f"Get funcs: {self._funcs}")
        for funcName, funcContent in self._funcs.items():
            LoadPluginBase.logIfDebug(f"Checking function {funcName}...")
            lexedFunc: list[Any] = []
            for line, temp in enumerate(funcContent[0], 1):
                LoadPluginBase.logIfDebug(f"Checking line {line}... (OwO)")
                if len(temp) == 0:
                    LoadPluginBase.logIfDebug(f"Error In Line {line}: No any functions")
                    continue
                LoadPluginBase.logIfDebug(f"Built-in Function Name: {temp[0]}")
                if not temp[0] in LoadPluginBase.functions.keys():
                    LoadPluginBase.logIfDebug(
                        f"Error In Line {line}: Function {temp[0]} is not defined!"
                    )
                    continue
                if temp[0] == 7:
                    Logger.warning(
                        f"USEFUNC Function will be define in API 1.0.3, now API Version is {".".join(apiVersion)}",
                    )
                    continue
                after: list[Any] = temp
                after[0] = LoadPluginBase.functions[temp[0]]
                lexedFunc.append(after)
                LoadPluginBase.logIfDebug(
                    f"Successfully to Check line {line}! No problem! (OwO)"
                )
            LoadPluginBase.logIfDebug(f"Already checked function {funcName}!")
            verified[funcName] = (lexedFunc, funcContent[1])

        LoadPluginBase.logIfDebug(
            f"Successfully to Check all the Function List, Total: {len(self._funcs)} Passed: {len(verified)} Skipped: {len(self._funcs)-len(verified)}"
        )

        LoadPluginBase.logIfDebug(f"Verified and Lexed list value: {verified}")

        try:
            temp = FunctionLexerSet(verified).getValue()
            LoadPluginBase.logIfDebug(f"Successfully to lex! Value: {temp}")
            return temp
        except Exception as e:
            Logger.error(f"Failed to parse! Reason: {e!r}")
            return None
