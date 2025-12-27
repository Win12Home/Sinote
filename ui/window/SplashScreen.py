from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QPixmap
from core.i18n import loadJson


class SplashScreen(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowFlag(Qt.WindowType.SplashScreen)
        self.setMinimumWidth(500)
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
            loadJson("LoadingScreen")["loading.text.loadplugin"].format(
                "null", "0", "Summing..."
            )
        )
        self.layout_.addWidget(self.image, 1, Qt.AlignmentFlag.AlignHCenter)
        self.layout_.addWidget(self.label, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.setLayout(self.layout_)

    def setTotal(self, total: int):
        self.totals = total
        self.label.setText(
            loadJson("LoadingScreen")["loading.text.loadplugin"].format(
                self.nowLoading, "0", total
            )
        )
        self.repaint()

    def setPluginName(self, name: str):
        self.nowLoading = name
        self.label.setText(
            loadJson("LoadingScreen")["loading.text.loadplugin"].format(
                self.nowLoading, self.loadedPlugin, self.totals
            )
        )
        self.repaint()

    def addOne(self):
        self.loadedPlugin += 1
        self.label.setText(
            loadJson("LoadingScreen")["loading.text.loadplugin"].format(
                self.nowLoading, self.loadedPlugin, self.totals
            )
        )
        self.repaint()

    def finishedPluginLoad(self):
        self.label.setText(loadJson("LoadingScreen")["loading.text.loadfont"])
        self.repaint()
