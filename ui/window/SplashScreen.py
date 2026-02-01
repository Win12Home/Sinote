from core.i18n import getLangJson
from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QDialog, QLabel, QVBoxLayout


class SplashScreen(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.SplashScreen | Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog
        )
        self.setMinimumWidth(500)
        self.setWindowTitle("Sinote")
        self.layout_: QVBoxLayout = QVBoxLayout()
        self.image = QLabel()
        self.loadedPlugin: int = 0
        self.totals: int = 0
        self.setStyleSheet("background-color:white;color:black;")
        self.nowLoading: str = "null"
        self.pixmap = QPixmap("./resources/icon.png").scaled(QSize(256, 256))
        self.image.setPixmap(self.pixmap)
        self.label = QLabel()
        self.label.setStyleSheet("text-align: center;")
        self.label.setText(
            getLangJson("LoadingScreen")["loading.text.loadplugin"].format(
                "null", "0", "Summing..."
            )
        )
        self.layout_.addWidget(self.image, 1, Qt.AlignmentFlag.AlignHCenter)
        self.layout_.addWidget(self.label, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.setLayout(self.layout_)

    def setTotal(self, total: int):
        self.totals = total
        self.label.setText(
            getLangJson("LoadingScreen")["loading.text.loadplugin"].format(
                self.nowLoading, "0", total
            )
        )
        self.repaint()

    def setPluginName(self, name: str):
        self.nowLoading = name
        self.label.setText(
            getLangJson("LoadingScreen")["loading.text.loadplugin"].format(
                self.nowLoading, self.loadedPlugin, self.totals
            )
        )
        self.repaint()

    def addOne(self):
        self.loadedPlugin += 1
        self.label.setText(
            getLangJson("LoadingScreen")["loading.text.loadplugin"].format(
                self.nowLoading, self.loadedPlugin, self.totals
            )
        )
        self.repaint()

    def finishedPluginLoad(self):
        self.label.setText(getLangJson("LoadingScreen")["loading.text.loadfont"])
        self.repaint()
