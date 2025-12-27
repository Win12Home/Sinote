from core.plugin.LoadPluginBase import LoadPluginBase
import re


class Variables:
    def __init__(self, variableDict: dict = None):
        LoadPluginBase.logIfDebug(
            f"Variables has initializing, the variableDict argument: {"null" if variableDict is None else variableDict} 🥳"
        )
        self._variableDict: dict = variableDict if variableDict else {}
        self._variableMatchPattern = re.compile(r"%var:([^%]+)%")
        LoadPluginBase.logIfDebug(
            "Successfully to initialize Variables object ✅ (OwO)"
        )

    def addVar(self, varName: str, varContent: str = "NULL"):
        """
        Add or Edit Variable
        :param varName: Variable Name
        :param varContent: Variable Content
        :return: None
        """
        LoadPluginBase.logIfDebug(
            f'Set/Added Variable "{varName}" and edit it to "{varContent}" ✅ (UwU)'
        )
        self._variableDict[varName] = varContent

    def getVar(self, varName: str) -> str:
        """
        Get the Variable Content
        :param varName: Variable Name
        :return: String
        """
        LoadPluginBase.logIfDebug("少女祈祷中...（不要出|XXX NOT FOUND|）")
        if not varName in self._variableDict.keys():
            LoadPluginBase.logIfDebug(f"Cannot get variable {varName} (TwT)")
            return f"|{varName} NOT FOUND|"
        LoadPluginBase.logIfDebug(f"Successfully to get variable {varName} ✅ (OwO)")
        LoadPluginBase.logIfDebug(
            f"Variable Content: {self._variableDict[varName]} (-W-)"
        )
        return self._variableDict[varName]

    def removeVar(self, varName: str) -> bool:
        """
        Remove a Variable
        :param varName: Variable Name
        :return: Boolean, False for it was removed, True for Removed
        """
        LoadPluginBase.logIfDebug(f"Successfully to remove variable {varName} ✅ (O_I)")
        if not varName in self._variableDict.keys():
            return False
        self._variableDict.pop(varName)
        return True

    def copyDict(self) -> dict:
        """
        By the way, an easy method.
        Dict.copy()
        :return: Dictionary
        """
        return self._variableDict

    def resolveVarInString(self, string: str) -> str:
        """
        Use Regular Expression to Match in String
        :param string: String
        :return: The new string
        """

        def temporaryReplaceMatch(match):
            LoadPluginBase.logIfDebug(
                f"Regular Expression Matching: GROUP = {match.group()} -> VAR: {match.group(1)} (UwU)"
            )
            temporary = self.getVar(match.group(1))
            LoadPluginBase.logIfDebug(f"Regular Expression Replaced: {temporary} ✅")
            return temporary

        value = self._variableMatchPattern.sub(temporaryReplaceMatch, string)
        LoadPluginBase.logIfDebug(f"Regular Expression Final Answer: {value} 💥(IwI)")
        return value
