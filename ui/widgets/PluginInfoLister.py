from typing import Any

from core.i18n import getLangJson
from PySide6.QtWidgets import QTextEdit, QWidget


class PluginInfoLister(QTextEdit):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.setStyleSheet(f"{self.styleSheet()} border: none;")
        self.setReadOnly(True)

    def setInformation(self, info: list[Any]) -> None:
        self.clear()
        self.setHtml(
            f"""
<img src="{info[0]}">
<br><h1>{info[1]}</h1>
<h3>{info[2]}</h3>
<p>{getLangJson("EditorUI")["editor.any.version"]}: {info[3]}</p>
<p>{getLangJson("EditorUI")["editor.any.author"]}: {info[4]}</p>
<p>{getLangJson("EditorUI")["editor.any.description"]}: <br>{info[5].replace("\\n", "<br>")}</p>
"""
        )
