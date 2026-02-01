from PySide6.QtCore import QRect, Qt
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QPlainTextEdit, QWidget


class LineNumberWidget(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor
        self.setFixedWidth(40)
        self.setCursor(Qt.CursorShape.IBeamCursor)
        self.borderWidth = 1
        self.borderColor = QColor("#ABABAB")

    def paintEvent(self, event):
        painter = QPainter(self)
        # Draw Border at right
        painter.setPen(QPen(self.borderColor, self.borderWidth))
        painter.drawLine(self.width() - 1, 0, self.width() - 1, self.height())
        block = self.editor.firstVisibleBlock()  # Magic Line
        blockNumber = block.blockNumber()
        top = (
            self.editor.blockBoundingGeometry(block)
            .translated(self.editor.contentOffset())
            .top()
        )
        bottom = top + self.editor.blockBoundingRect(block).height()
        painter.setPen(self.palette().mid().color())
        font = self.editor.font()
        painter.setFont(font)

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(blockNumber + 1)
                painter.drawText(
                    0,
                    int(top),
                    self.width() - 5,
                    self.editor.fontMetrics().height(),
                    Qt.AlignmentFlag.AlignRight,
                    number,
                )
            block = block.next()
            top = bottom
            bottom = top + self.editor.blockBoundingRect(block).height()
            blockNumber += 1


class LineShowTextEdit(QPlainTextEdit):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.lineNumberShowWidget = LineNumberWidget(self)
        self.setViewportMargins(40, 0, 0, 0)
        self.blockCountChanged.connect(self.updateLineShowerWidth)
        self.updateRequest.connect(self.updateLineShowerNumbers)
        self.cursorPositionChanged.connect(self.highlightThisLine)
        self.updateLineShowerWidth()
        self.highlightThisLine()

    def updateLineShowerWidth(self):
        digits = len(str(max(1, self.blockCount())))
        space = 10 + self.fontMetrics().horizontalAdvance("9") * digits
        self.setViewportMargins(space, 0, 0, 0)
        self.lineNumberShowWidget.setFixedWidth(space)

    def updateLineShowerNumbers(self, rect, dy):
        if dy:
            self.lineNumberShowWidget.scroll(0, dy)
        else:
            self.lineNumberShowWidget.update(
                0, rect.y(), self.lineNumberShowWidget.width(), rect.height()
            )

        if rect.contains(self.viewport().rect()):
            self.updateLineShowerWidth()

    def highlightThisLine(self):
        self.lineNumberShowWidget.update()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.lineNumberShowWidget.setGeometry(
            QRect(cr.left(), cr.top(), self.lineNumberShowWidget.width(), cr.height())
        )
