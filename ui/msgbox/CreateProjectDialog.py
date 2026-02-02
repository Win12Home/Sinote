from PySide6.QtWidgets import (
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QSizePolicy,
    QWidget,
    QFileDialog,
    QMessageBox,
)
from PySide6.QtCore import Qt, QEventLoop
from ui.window.FramelessWindow import FramelessWindow
from core.i18n import getLangJson
from pathlib import Path
from core.project import createProject


class CreateProjectDialog(FramelessWindow):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.titleBar.setOnlyCloseButton()
        self.setWindowFlag(Qt.WindowType.Dialog, True)
        self.raise_()
        self.setWindowTitle("")  # Set to no title

        self._accepted = False
        self._looper: QEventLoop = QEventLoop()
        self.path: str = ""

        self.widget = QWidget()
        self.vLayout = QVBoxLayout()
        self.vLayout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.createProjectLabel = QLabel(
            getLangJson("EditorUI")["editor.title.proj.createproj"]
        )  # NOQA, against PEP 8 rules in string
        self.createProjectLabel.setSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed
        )

        self.pathChooseArea = QWidget()
        self.pathChooseLayout = QHBoxLayout()
        self.pathChooseLabel = QLabel(
            getLangJson("EditorUI")["editor.any.path"]
        )  # NOQA
        self.pathChooseLabel.setSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed
        )
        self.pathLineEdit = QLineEdit()
        self.pathLineEdit.setPlaceholderText(
            getLangJson("EditorUI")["editor.placeholder.proj.enterpath"]
        )
        self.pathChooser = QPushButton(
            getLangJson("EditorUI")["editor.button.proj.choose"]
        )
        self.pathChooser.setFlat(True)
        self.pathChooser.clicked.connect(self.choosePath)
        self.pathChooser.setSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed
        )
        self.pathChooseLayout.addWidget(self.pathChooseLabel, stretch=1)
        self.pathChooseLayout.addWidget(self.pathLineEdit, stretch=5)
        self.pathChooseLayout.addWidget(self.pathChooser, stretch=1)
        self.pathChooseArea.setLayout(self.pathChooseLayout)

        self.projectNameArea = QWidget()
        self.projectNameLayout = QHBoxLayout()
        self.projectNameLabel = QLabel(
            getLangJson("EditorUI")["editor.title.proj.projname"]
        )  # NOQA
        self.projectNameLabel.setSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed
        )
        self.projectNameEdit = QLineEdit()
        self.projectNameEdit.setPlaceholderText(
            getLangJson("EditorUI")["editor.placeholder.proj.entername"]
        )
        self.projectNameLayout.addWidget(self.projectNameLabel, stretch=1)
        self.projectNameLayout.addWidget(self.projectNameEdit, stretch=5)
        self.projectNameArea.setLayout(self.projectNameLayout)

        self.buttonArea = QWidget()
        self.buttonLayout = QHBoxLayout()
        self.buttonAccept = QPushButton(getLangJson("MessageBox")["msgbox.button.ok"])
        self.buttonAccept.clicked.connect(self.accept)
        self.buttonAccept.setProperty("class", "primary")
        self.buttonReject = QPushButton(
            getLangJson("MessageBox")["msgbox.button.cancel"]
        )
        self.buttonReject.clicked.connect(self.reject)
        self.buttonLayout.addWidget(self.buttonAccept)
        self.buttonLayout.addWidget(self.buttonReject)
        self.buttonArea.setLayout(self.buttonLayout)

        self.vLayout.addWidget(self.createProjectLabel)
        self.vLayout.addWidget(self.pathChooseArea)
        self.vLayout.addWidget(self.projectNameArea)
        self.vLayout.addWidget(self.buttonArea)
        self.widget.setLayout(self.vLayout)
        self.setCentralWidget(self.widget)

    def exec(self) -> bool:  # Fake exec
        self.show()
        self._looper.exec()
        self.hide()
        if self._accepted:
            createProject(
                self.pathLineEdit.text(), self.projectNameEdit.text()
            )  # Analyze Project Creating
            self.path = self.pathLineEdit.text()
        self.destroy()
        return self._accepted

    def accept(self) -> None:
        self._accepted = True
        if (
            not Path(self.pathLineEdit.text()).is_dir()
            or self.pathLineEdit.text().strip() == ""
        ):
            QMessageBox.critical(
                self,
                getLangJson("MessageBox")["msgbox.title.error"],
                getLangJson("MessageBox")["msgbox.error.pathNotValid"].format(
                    self.pathLineEdit.text().strip()
                ),
                buttons=QMessageBox.StandardButton.Ok,
            )
            return
        self.close()

    def reject(self) -> None:
        # self._accepted = False  # Am I a stupid guy? self._accepted has been set to False, why I need to re-set it?
        self.close()

    def close(self) -> None:
        self._looper.quit()

    def choosePath(self) -> None:  # NOQA, f**k off PEP 8
        directory: str | None = QFileDialog.getExistingDirectory(
            self, getLangJson("EditorUI")["editor.window.proj.choose"]
        )
        if directory:
            self.pathLineEdit.setText(directory)
