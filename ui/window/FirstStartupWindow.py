from PySide6.QtWidgets import (
    QDialog,
    QPushButton,
    QLabel,
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
)
from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon
from ui.selfLogger import debugLog
from core.i18n import loadJson


class FirstStartupWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sinote")
        self.setWindowIcon(QIcon("./resources/icon.png"))
        self.setMinimumSize(QSize(500, 300))
        self.resize(QSize(500, 300))
        self.setMaximumSize(QSize(500, 400))
        self._setupUI()

    def _setupUI(self) -> None:
        debugLog("Setting up UI for travel...")
        self.vLayout = QVBoxLayout()
        self.buttons = QWidget()
        self.hLayout = QHBoxLayout()
        self.addProject: QPushButton = QPushButton(
            loadJson("FirstStartup")["fs.button.newproj"]
        )
        self.addProject.setProperty("class", "chooseButton")
        self.addProject.setIcon(QIcon.fromTheme(QIcon.ThemeIcon.DocumentNew))
        self.importProject: QPushButton = QPushButton(
            loadJson("FirstStartup")["fs.button.importone"]
        )
        self.importProject.setProperty("class", "chooseButton")
        self.importProject.setIcon(QIcon.fromTheme(QIcon.ThemeIcon.DocumentOpen))
        self.hLayout.addWidget(self.addProject, 1)
        self.hLayout.addStretch(2)
        self.hLayout.addWidget(self.importProject, 1)
        self.buttons.setLayout(self.hLayout)
        self.titleLabel = QLabel(loadJson("TrailUI")["trail.text.welcome"])
        self.titleLabel.setStyleSheet("font-size: 30px; font-weight: bold;")
        self.descLabel = QLabel(loadJson("TrailUI")["trail.text.desc01"])
        self.descLabel.setStyleSheet("font-size: 17px; font-weight: bold;")
        self.vLayout.addWidget(self.titleLabel, 1, Qt.AlignmentFlag.AlignHCenter)
        self.vLayout.addWidget(self.descLabel, 1, Qt.AlignmentFlag.AlignHCenter)
        self.vLayout.addWidget(self.buttons, 1)
        self.vLayout.addStretch(2)
        self.setLayout(self.vLayout)
        debugLog("Successfully to set up!")
