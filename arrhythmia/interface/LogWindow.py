import datetime
import time

from PySide2.QtCore import QObject
from PySide2.QtWidgets import QPushButton, QTextEdit, QMessageBox


class LogWindow(QObject):

    def __init__(self, manager, ui_file, parent=None):
        super(LogWindow, self).__init__(parent)
        self.window = ui_file
        self.manager = manager

        close_button = self.window.findChild(QPushButton, 'close_button')
        clear_button = self.window.findChild(QPushButton, 'clear_button')
        save_button = self.window.findChild(QPushButton, 'save_button')

        self.text_field = self.window.findChild(QTextEdit, 'log_area')

        close_button.clicked.connect(self.close_handler)
        clear_button.clicked.connect(self.clear_handler)
        save_button.clicked.connect(self.save_handler)

    def show(self):
        self.window.show()

    def log(self, content):
        self.text_field.append(str(content))

    def close_handler(self):
        self.window.close()

    def clear_handler(self):
        self.text_field.clear()

    def save_handler(self):
        filename = "log_{}".format(time.strftime("%Y%m%d-%H%M%S"))
        logs = self.text_field.toPlainText()
        msg_window = QMessageBox()
        if logs != "":
            with open(filename, "w") as text_file:
                text_file.write("Created on " + str(datetime.datetime.now()) + "\n")
                text_file.write(logs)

            msg_window.setWindowTitle("Information")
            msg_window.setText("Logs have been saved to a file.")
        else:
            msg_window.setWindowTitle("Information")
            msg_window.setText("Nothing to save.")
        msg_window.exec()
