from PyQt6.QtWidgets import QMessageBox

def show_custom_msg(parent, title, text, is_error=False):
    msg = QMessageBox(parent)
    msg.setWindowTitle(title)
    msg.setText(text)
    msg.setStandardButtons(QMessageBox.StandardButton.NoButton)
    msg.addButton("OK", QMessageBox.ButtonRole.AcceptRole)
    msg.exec()
