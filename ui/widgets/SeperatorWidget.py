from PySide6.QtWidgets import QFrame, QWidget


class SeperatorWidget(QFrame):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.setFrameShape(self.Shape.HLine)
        self.setFrameShadow(self.Shadow.Sunken)
