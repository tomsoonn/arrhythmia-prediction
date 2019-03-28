import sys

from PySide2.QtWidgets import QPushButton
from PySide2.QtCore import QObject


class MenuWindow(QObject):

    def __init__(self, manager, ui_file, parent=None):
        super(MenuWindow, self).__init__(parent)
        self.window = ui_file
        self.manager = manager

        exit_button = self.window.findChild(QPushButton, 'exit_button')
        types_button = self.window.findChild(QPushButton, 'types_button')
        explore_button = self.window.findChild(QPushButton, 'explore_button')
        predict_button = self.window.findChild(QPushButton, 'predict_button')

        exit_button.clicked.connect(self.exit_handler)
        types_button.clicked.connect(self.types_handler)
        explore_button.clicked.connect(self.explore_handler)
        predict_button.clicked.connect(self.predict_handler)

    def predict_handler(self):
        self.manager.show_predict()

    def explore_handler(self):
        self.manager.show_explore()

    def types_handler(self):
        self.manager.show_types()

    @staticmethod
    def exit_handler():
        sys.exit()
