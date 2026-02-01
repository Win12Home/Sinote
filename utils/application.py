from PySide6.QtWidgets import QApplication


class BaseApplication(QApplication):
    quited: bool = False

    def quit(self) -> None:
        self.quited = True
        return super().quit()


application = BaseApplication([])
