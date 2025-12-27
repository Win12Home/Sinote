from PySide6.QtWidgets import QApplication
from qt_material import apply_stylesheet


def applyStylesheet(application: QApplication, theme: str) -> None:
    apply_stylesheet(
        application,
        theme,
        extra={"QMenu": {"height": 20, "padding": "5px 10px 7px 10px"}},
        invert_secondary=True,
    )
    customizeCss: str = """
    .chooseButton {
        height: 128px;
        width: 128px;
        font-size: 15px;
        font-weight: bold;
    }
    """
    application.setStyleSheet(application.styleSheet() + customizeCss)
