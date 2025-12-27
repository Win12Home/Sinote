from core.plugin.LoadPluginBase import LoadPluginBase
from core.plugin.FunctionLexerSet import FunctionLexerSet
from utils.logger import addLog
from utils.const import apiVersion


class ParseFunctions:
    def __init__(self, list_: dict, customizeVar: bool = True):
        self._list: dict = list_
        self._customizeVar = customizeVar

    def getValue(self) -> list | None:
        """
        Get list[partial]
        :return: list[partial] or None
        """
        verifiedlist: list = []
        LoadPluginBase.logIfDebug(f"Get funcs: {self._list}")
        for funcName, funcContent in self._list.items():
            LoadPluginBase.logIfDebug(f"Checking function {funcName}...")
            for line, temp in enumerate(funcContent, 1):
                LoadPluginBase.logIfDebug(f"Checking line {line}... (OwO)")
                if len(temp) == 0:
                    LoadPluginBase.logIfDebug(f"Error In Line {line}: No any functions")
                    continue
                if temp[0] not in LoadPluginBase.functions.keys():
                    LoadPluginBase.logIfDebug(
                        f"Error In Line {line}: Function {temp[0]} is not defined!"
                    )
                    continue
                if temp[0] == 7:
                    addLog(
                        1,
                        f"USEFUNC Function will be define in API 1.0.3, now API Version is {".".join(apiVersion)}",
                    )
                    continue
                after: list = temp
                after[0] = LoadPluginBase.functions[temp[0]]
                verifiedlist.append(temp)
                LoadPluginBase.logIfDebug(
                    f"Successfully to Check line {line}! No problem! (UwU) I'm proud!"
                )
            LoadPluginBase.logIfDebug(f"Already checked function {funcName}!")

        LoadPluginBase.logIfDebug(
            f"Successfully to Check all the Function List, Total: {len(self._list)} Passed: {len(verifiedlist)} Skipped: {len(self._list)-len(verifiedlist)}"
        )

        try:
            temp = FunctionLexerSet(verifiedlist).getValue()
            LoadPluginBase.logIfDebug(f"Successfully to lex! Value: {temp}")
            return temp
        except Exception as e:
            addLog(2, f"Failed to parse! Reason: {repr(e)}")
            return None
