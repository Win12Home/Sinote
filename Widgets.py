from BasicModule import *

class WelcomeWindowNamespace: # Like a namespace, but cannot using it.
    class WelcomeProjectPage(QWidget):
        def __init__(self,parent: QWidget=None):
            super().__init__(parent)
            self._layout = QHBoxLayout(self)
            self.titleLabel = TitleLabel()
            self.subTitleLabel = SubtitleLabel()
            self.commandBar = QWidget()
            # Command Bar: New Project, Import Project

        def refreshLanguage(self):
            # Refresh Global Language when change language
            # Based by QWidget or et cetera needed
            self.titleLabel