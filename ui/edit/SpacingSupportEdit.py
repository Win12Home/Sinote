from ui.edit.LineShowTextEdit import LineShowTextEdit
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCursor, QKeyEvent
from utils.SafetyMutable import SafetyList


class SpacingSupportEdit(LineShowTextEdit):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.defineKeywords: list[str] = []
        self.charSymbols: list[str] = []
        self.usingCodeControl: bool = False
        self.spacing: int = 4

    def getPosInLine(self) -> int:
        cursor = self.textCursor()
        originalPos: int = cursor.position()
        cursor.movePosition(QTextCursor.MoveOperation.StartOfLine)
        afterPos: int = cursor.position()
        cursor.setPosition(originalPos)
        return originalPos - afterPos

    def getLineNumber(self) -> int:
        cursor = self.textCursor()
        originalPos: int = cursor.position()
        cursor.movePosition(
            QTextCursor.MoveOperation.Start, QTextCursor.MoveMode.KeepAnchor
        )
        lineNumber: int = len(cursor.selectedText().splitlines())
        cursor.clearSelection()
        cursor.setPosition(originalPos)
        lineNumber: int = 1 if lineNumber == 0 else lineNumber
        return lineNumber

    def _getBeforeText(self, position: int) -> str:
        cursor = self.textCursor()
        originalPos: int = cursor.position()
        cursor.setPosition(position)
        cursor.movePosition(
            QTextCursor.MoveOperation.StartOfLine, QTextCursor.MoveMode.KeepAnchor
        )
        text: str = cursor.selectedText()
        cursor.clearSelection()
        cursor.setPosition(originalPos)
        return text

    def backIndent(self) -> None:
        cursor = self.textCursor()
        originalPos: int = cursor.position()
        if not self._getBeforeText(originalPos).strip() and self.getPosInLine() >= 1:
            inlinePos: int = self.getPosInLine()
            returnPos: int = (
                self.spacing
                if inlinePos % self.spacing == 0
                else self.spacing - (inlinePos % self.spacing)
            )
            cursor.movePosition(
                QTextCursor.MoveOperation.Left,
                QTextCursor.MoveMode.KeepAnchor,
                returnPos,
            )
            cursor.removeSelectedText()
            cursor.clearSelection()
            cursor.setPosition(originalPos - returnPos)

    def _multilineIndent(self, back: bool = False) -> None:
        cursor = self.textCursor()
        selectionStart: int = cursor.selectionStart()
        text: list[str] = cursor.selectedText().splitlines()
        after: list[str] = []
        for temp in text:
            space: int = len(temp) - len(temp.lstrip())
            if back:
                oneSpace: int = (
                    space % self.spacing if space % self.spacing else self.spacing
                )
                backSpacing: int = space - oneSpace
                after.append(f"{backSpacing * " "}{temp[space:]}")
            else:
                spacing: int = (
                    self.spacing if space % self.spacing == 0 else space % self.spacing
                )
                after.append(f"{spacing * " "}{temp}")
        answer: str = "\n".join(after)
        cursor.removeSelectedText()
        cursor.setPosition(selectionStart)
        cursor.insertText(answer)
        cursor.setPosition(selectionStart)
        cursor.movePosition(
            QTextCursor.MoveOperation.Right,
            QTextCursor.MoveMode.KeepAnchor,
            len(answer),
        )
        self.setTextCursor(cursor)

    def _thisLineContent(self, position: int) -> str:
        cursor = self.textCursor()
        cursor.setPosition(position)
        cursor.movePosition(QTextCursor.MoveOperation.StartOfLine)
        cursor.movePosition(
            QTextCursor.MoveOperation.EndOfLine, QTextCursor.MoveMode.KeepAnchor
        )
        getText: str = cursor.selectedText()
        cursor.clearSelection()
        cursor.setPosition(position)
        return getText

    def keyPressEvent(self, event: QKeyEvent) -> None:
        # Rewrite keyPressEvent, AI Generate? Unuse!
        if event.key() == Qt.Key.Key_Home:
            cursor = self.textCursor()
            originalPos: int = cursor.position()
            if self._getBeforeText(originalPos).strip() == "":
                cursor.movePosition(QTextCursor.MoveOperation.StartOfLine)
            else:
                lineSpace: int = len(self._thisLineContent(originalPos)) - len(
                    self._thisLineContent(originalPos).lstrip()
                )
                cursor.movePosition(QTextCursor.MoveOperation.StartOfLine)
                cursor.movePosition(
                    QTextCursor.MoveOperation.Right,
                    QTextCursor.MoveMode.MoveAnchor,
                    lineSpace,
                )
            self.setTextCursor(cursor)
            return
        elif event.key() == Qt.Key.Key_End:
            cursor = self.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.EndOfLine)
            self.setTextCursor(cursor)
            return
        elif event.key() == Qt.Key.Key_Clear:
            # What the hell? Who've got a keyboard that has a Clear Key? I will steal it. (Joking bro)
            self.clear()
            return
        elif event.key() == Qt.Key.Key_Backtab:
            # Same as Backspace
            cursor = self.textCursor()
            if len(cursor.selectedText()) > 0:
                self._multilineIndent(True)
            else:
                self.backIndent()
            return
        elif event.key() == Qt.Key.Key_Tab:
            cursor = self.textCursor()
            originalPos: int = cursor.position()
            if len(cursor.selectedText()) > 0:
                self._multilineIndent()
                return
            else:
                posInLine: int = self.getPosInLine()
                spacing: int = (
                    self.spacing
                    if posInLine % self.spacing == 0
                    else self.spacing - (posInLine % self.spacing)
                )  # 3-->3 4-->4(not zero) 5-->4
                cursor.insertText(" " * spacing)
                cursor.setPosition(originalPos + spacing)
                return
        elif event.key() == Qt.Key.Key_Return:
            cursor = self.textCursor()
            originalPos: int = cursor.position()
            cursor.movePosition(
                QTextCursor.MoveOperation.Left, QTextCursor.MoveMode.KeepAnchor
            )
            leftStr = cursor.selectedText()
            cursor.clearSelection()
            cursor.setPosition(originalPos)
            cursor.movePosition(
                QTextCursor.MoveOperation.Right, QTextCursor.MoveMode.KeepAnchor
            )
            rightStr = cursor.selectedText()
            cursor.clearSelection()
            cursor.setPosition(originalPos)
            defineKeywords: list[list[str]] = [
                [i[0], i[1]] for i in self.defineKeywords
            ]
            index = SafetyList([i[0] for i in defineKeywords]).index(leftStr)
            if index != SafetyList.OutErrors.NotFoundInIndex and (
                defineKeywords[index][1] == rightStr
                or defineKeywords[index][1].strip() == ""
            ):
                cursor.movePosition(
                    QTextCursor.MoveOperation.EndOfLine, QTextCursor.MoveMode.KeepAnchor
                )
                afterText: str = cursor.selectedText()
                cursor.removeSelectedText()
                cursor.setPosition(originalPos)
                content: str = self._thisLineContent(cursor.position())
                lineSpace: int = len(content) - len(content.lstrip())
                cursor.insertText(
                    f"\n{" " * (lineSpace + self.spacing)}{f"\n{' ' * lineSpace}{afterText}" if not (defineKeywords[index][1].strip() == "") else afterText}"
                )
                cursor.clearSelection()
                cursor.setPosition(
                    originalPos
                    + lineSpace
                    + (len(afterText) if defineKeywords[index][1].strip() == "" else 0)
                    + self.spacing
                    + 1
                )
                self.setTextCursor(cursor)
            else:
                content: str = self._thisLineContent(cursor.position())
                lineSpace: int = len(content) - len(content.lstrip())
                cursor.insertText("\n")
                cursor.insertText(" " * lineSpace)
                cursor.setPosition(originalPos + lineSpace + 1)
                self.setTextCursor(cursor)
            return
        elif event.text() in [i[0] for i in self.defineKeywords] or event.text() in [
            "(",
            "[",
            "{",
        ]:
            super().keyPressEvent(event)
            cursor = self.textCursor()
            normals: list = ["()", "[]", "{}"]
            defineKeywords: list[list[str]] = [
                [i[0], i[1]] for i in self.defineKeywords
            ] + [[i[0], i[1]] for i in normals]
            index = SafetyList([i[0] for i in defineKeywords]).index(event.text())
            if index != SafetyList.OutErrors.NotFoundInIndex:
                if defineKeywords[index][1].strip() == "":
                    return
            if event.text() in [i[0] for i in self.defineKeywords]:
                cursor.insertText(
                    [i[1] for i in self.defineKeywords][
                        [i[0] for i in self.defineKeywords].index(event.text())
                    ]
                )
            elif event.text() in [i[0] for i in normals]:
                cursor.insertText(
                    [i[1] for i in normals][[i[0] for i in normals].index(event.text())]
                )
            else:
                return
            cursor.movePosition(QTextCursor.MoveOperation.Left)
            self.setTextCursor(cursor)
            return
        elif event.key() == Qt.Key.Key_Delete:
            cursor = self.textCursor()
            originalPos = cursor.position()
            if cursor.hasSelection():
                cursor.removeSelectedText()
                return
            cursor.movePosition(
                QTextCursor.MoveOperation.Right, QTextCursor.MoveMode.KeepAnchor
            )
            cursor.removeSelectedText()
            cursor.setPosition(originalPos)
            return
        elif event.key() == Qt.Key.Key_Backspace:
            cursor = self.textCursor()
            originalPos = cursor.position()
            if cursor.hasSelection():
                cursor.removeSelectedText()
                return
            if cursor.position() > 0:
                if self.getPosInLine() >= self.spacing:
                    self.backIndent()
                    if self.textCursor().position() != originalPos:
                        return
                if self.getPosInLine() >= 1:
                    cursor.movePosition(
                        QTextCursor.MoveOperation.Left, QTextCursor.MoveMode.KeepAnchor
                    )
                    left: str = cursor.selectedText()
                    cursor.clearSelection()
                    cursor.setPosition(originalPos)
                    cursor.movePosition(
                        QTextCursor.MoveOperation.Right, QTextCursor.MoveMode.KeepAnchor
                    )
                    right: str = cursor.selectedText()
                    cursor.clearSelection()

                    if f"{left}{right}" in self.defineKeywords or f"{left}{right}" in [
                        "()",
                        "[]",
                        "{}",
                    ]:
                        cursor.movePosition(QTextCursor.MoveOperation.Left)
                        cursor.movePosition(
                            QTextCursor.MoveOperation.Right,
                            QTextCursor.MoveMode.KeepAnchor,
                            2,
                        )
                        cursor.removeSelectedText()
                        cursor.setPosition(originalPos - 1)
                    else:
                        super().keyPressEvent(event)
                        return
                else:
                    super().keyPressEvent(event)
                    return
            else:
                super().keyPressEvent(event)
                return

        super().keyPressEvent(event)
