from PySide2.QtWidgets import QPushButton
from PySide2.QtCore import QObject


# TODO everything here

class ExploreWindow(QObject):

    def __init__(self, manager, ui_file, parent=None):
        super(ExploreWindow, self).__init__(parent)
        self.window = ui_file
        self.manager = manager

        back_button = self.window.findChild(QPushButton, 'back_button')

        back_button.clicked.connect(self.back_handler)

    def back_handler(self):
        self.manager.show_menu()
