import re

from PySide6.QtCore import QRegularExpression
from PySide6.QtGui import (
    QColor,
    QFont,
    QSyntaxHighlighter,
    QTextCharFormat,
    QTextDocument,
)
from utils.argumentParser import debugMode
from utils.logger import Logger


class LoadPluginBase:
    functions: dict = {
        # Base Functions
        "print": 0,
        "msgbox": 1,
        "log": 2,
        "var": 3,
        "vpr": 4,
        "msgin": 5,
        "system": 6,
        "usefunc": 7,
        "sleep": 8,
        # Advanced Functions
        "set": 100,
        "mkdir": 101,
        "cfile": 102,
        "efile": 103,
        "pfile": 104,
        "dfile": 105,
        "afile": 106,
        "wfile": 107,
        "rfile": 108,
        # GUI Functions
        "errbox": 200,
    }

    argumentNumber: dict = {
        # Base Functions
        0: [1, 1],
        1: [2, 2],
        2: [2, 2],
        3: [1, 2],
        4: [1, 1],
        5: [3, 3],
        6: [1, 2],
        7: [1, 1],
        8: [1, 1],
        # Advanced Functions
        100: [2, 2],
        101: [1, 1],
        102: [1, 1],
        103: [1, 1],
        104: [2, 3],
        105: [1, 1],
        106: [2, 2],
        107: [2, 2],
        108: [2, 2],
        # GUI Functions
        200: [1, 1],
    }

    class ConfigKeyNotFoundError(Exception): ...

    @staticmethod
    def parseErrCode(code: int) -> str:
        errCodeDefinitions: dict = {
            0: "Missing Ingredients",
            1: "API is too low or high",
            2: "Missing File",
            3: "Not a sure plugin",
            -1: "Unknown Error",
        }
        return errCodeDefinitions.get(code, "SIMPLY_ERROR")

    class CustomizeSyntaxHighlighter(QSyntaxHighlighter):
        def __init__(self, syntaxList: list, parent: QTextDocument = None):
            """
            Initialize Customize Syntax Highlighter
            :param syntaxList: syntax list, lexed from LoadPluginHeader object
            :param parent: QTextDocument of a PlainTextEdit or TextEdit
            """
            super().__init__(parent)

            self.keywords = syntaxList[0] if len(syntaxList) > 0 else []
            self.symbols = syntaxList[1] if len(syntaxList) > 1 else []
            self.remKeywords = syntaxList[2] if len(syntaxList) > 2 else []
            self.remKeywordsMultipleLine = syntaxList[3] if len(syntaxList) > 3 else []
            self.enableSelfColor = syntaxList[4] if len(syntaxList) > 4 else True
            self.textKeywords = syntaxList[5] if len(syntaxList) > 5 else []

            self.highlight_rules = []
            self.multi_line_patterns = []

            self._setup_formats()
            self._setup_highlighting_rules()

            Logger.info(
                f"Syntax highlighter initialized with {len(self.keywords)} keywords, {len(self.symbols)} symbols 😍",
                "LoadPluginBaseActivity",
            )

        def _setup_formats(self):
            self.keyword_format = QTextCharFormat()
            self.keyword_format.setForeground(QColor("#3DACFF"))
            self.keyword_format.setFontWeight(QFont.Weight.Bold)

            self.symbol_format = QTextCharFormat()
            self.symbol_format.setForeground(QColor("#717A2A"))

            self.single_comment_format = QTextCharFormat()
            self.single_comment_format.setForeground(QColor("#009400"))
            self.single_comment_format.setFontItalic(True)

            self.multi_comment_format = QTextCharFormat()
            self.multi_comment_format.setForeground(QColor("#009400"))
            self.multi_comment_format.setFontItalic(True)

            self.string_format = QTextCharFormat()
            self.string_format.setForeground(QColor("#2EFF00"))

        def _setup_highlighting_rules(self):
            self._add_keyword_rules()
            self._add_symbol_rules()
            self._add_single_comment_rules()
            self._add_string_rules()
            self._add_multi_comment_rules()

        def _add_keyword_rules(self):
            for keyword in self.keywords:
                pattern = QRegularExpression(r"\b" + re.escape(keyword) + r"\b")
                self.highlight_rules.append((pattern, self.keyword_format))

        def _add_symbol_rules(self):
            for symbol in self.symbols:
                escaped_symbol = re.escape(symbol)
                pattern = QRegularExpression(escaped_symbol)
                self.highlight_rules.append((pattern, self.symbol_format))

        def _add_single_comment_rules(self):
            for comment_mark in self.remKeywords:
                pattern = QRegularExpression(re.escape(comment_mark) + r"[^\n]*")
                self.highlight_rules.append((pattern, self.single_comment_format))

        def _add_multi_comment_rules(self):
            if len(self.remKeywordsMultipleLine) >= 2:
                start_mark, end_mark = (
                    self.remKeywordsMultipleLine[0],
                    self.remKeywordsMultipleLine[1],
                )
                format_to_use = (
                    self.multi_comment_format
                    if self.enableSelfColor
                    else self.string_format
                )

                self.multi_line_patterns.append(
                    {
                        "start": QRegularExpression(re.escape(start_mark)),
                        "end": QRegularExpression(re.escape(end_mark)),
                        "format": format_to_use,
                    }
                )

        def _add_string_rules(self):
            for string_mark in self.textKeywords:
                pattern = QRegularExpression(
                    re.escape(string_mark) + r'([^"\\]|\\.)*?' + re.escape(string_mark)
                )
                self.highlight_rules.append((pattern, self.string_format))

        def highlightBlock(self, text: str):
            self.setCurrentBlockState(0)
            stringRanges = self._findStringRanges(text)
            for pattern, format in self.highlight_rules:
                matchIterator = pattern.globalMatch(text)
                while matchIterator.hasNext():
                    match = matchIterator.next()
                    startPos = match.capturedStart()
                    endPos = match.capturedStart() + match.capturedLength()
                    if format == self.single_comment_format:
                        if not self._isInString(startPos, stringRanges):
                            self.setFormat(startPos, match.capturedLength(), format)
                    elif format == self.multi_comment_format:
                        continue
                    else:
                        self.setFormat(startPos, match.capturedLength(), format)
            self.highlightMultiLineComments(text)

        def _findStringRanges(self, text: str) -> list:
            """
            Find String ranges
            :param text: text of string
            :return: a list
            """
            stringRanges = []
            i = 0
            n = len(text)

            while i < n:
                if text[i] in self.textKeywords:
                    quoteChar = text[i]
                    start = i
                    i += 1
                    while i < n:
                        if text[i] == "\\":
                            i += 2
                        elif text[i] == quoteChar:
                            i += 1
                            break
                        else:
                            i += 1

                    stringRanges.append((start, i))
                else:
                    i += 1

            return stringRanges

        def _isInString(self, pos: int, stringRanges: list) -> bool:
            for start, end in stringRanges:
                if start <= pos < end:
                    return True
            return False

        def isInMultilineComment(self, start: int, end: int, text: str) -> bool:
            if not self.multi_line_patterns:
                return False
            for multiLine in self.multi_line_patterns:
                startIter = multiLine["start"].globalMatch(text)
                while startIter.hasNext():
                    startMatch = startIter.next()
                    s = startMatch.capturedStart()
                    endMatch = multiLine["end"].match(
                        text, s + startMatch.capturedLength()
                    )
                    if endMatch.hasMatch():
                        e = endMatch.capturedEnd()
                    else:
                        if self.previousBlockState() == 1:
                            s = 0
                        e = len(text)
                    if s <= start and e >= end:
                        return True
            return False

        def highlightMultiLineComments(self, text: str):
            if not self.multi_line_patterns:
                return

            self.setCurrentBlockState(0)

            for multiLine in self.multi_line_patterns:
                startIndex = 0
                if self.previousBlockState() == 1:
                    endMatch = multiLine["end"].match(text, startIndex)
                    if endMatch.hasMatch():
                        endIndex = endMatch.capturedEnd()
                        self.setFormat(0, endIndex, multiLine["format"])
                        startIndex = endIndex
                        self.setCurrentBlockState(0)
                    else:
                        self.setFormat(0, len(text), multiLine["format"])
                        self.setCurrentBlockState(1)
                        return
                while startIndex < len(text):
                    startMatch = multiLine["start"].match(text, startIndex)
                    if not startMatch.hasMatch():
                        break

                    startIdx = startMatch.capturedStart()
                    endMatch = multiLine["end"].match(
                        text, startIdx + startMatch.capturedLength()
                    )
                    if endMatch.hasMatch():
                        endIdx = endMatch.capturedEnd()
                        self.setFormat(startIdx, endIdx - startIdx, multiLine["format"])
                        startIndex = endIdx
                    else:
                        self.setFormat(
                            startIdx, len(text) - startIdx, multiLine["format"]
                        )
                        self.setCurrentBlockState(1)
                        return

    class LazyCustomizeSyntaxHighlighter:
        def __init__(self, syntaxList: list, parent: QTextDocument = None):
            self._syntaxList: list = syntaxList
            self._parent: QTextDocument | None = parent

        def setParent(self, parent: QTextDocument) -> None:
            self._parent = parent

        def getObject(self) -> QSyntaxHighlighter:
            return LoadPluginBase.CustomizeSyntaxHighlighter(
                self._syntaxList, self._parent
            )

    @staticmethod
    def logIfDebug(logText: str) -> None:
        """
        Log out if Debug Mode starts.
        :param logText: text will log out.
        :return: None
        """
        if debugMode:
            Logger.debug(logText, "LoadPluginActivity")
