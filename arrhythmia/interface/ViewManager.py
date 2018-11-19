import os

from PySide2.QtUiTools import QUiLoader
from PySide2.QtCore import QFile, QObject
from PySide2.QtWidgets import QMainWindow, QStackedWidget

from arrhythmia.interface.ExploreWindow import ExploreWindow
from arrhythmia.interface.PredictWindow import PredictWindow
from arrhythmia.interface.MenuWindow import MenuWindow
from arrhythmia.interface.TypesWindow import TypesWindow


def load_ui(ui_filename):
    ui_dir = os.path.dirname(os.path.realpath(__file__))
    ui_file = QFile(os.path.join(ui_dir, ui_filename))
    ui_file.open(QFile.ReadOnly)

    loader = QUiLoader()
    window = loader.load(ui_file)
    ui_file.close()
    return window


class ViewManager:

    def __init__(self):
        self.menu = MenuWindow(self, load_ui('resources/menu.ui'))
        self.predict = PredictWindow(self, load_ui('resources/predict.ui'))
        self.types = TypesWindow(self, load_ui('resources/types.ui'))
        self.explore = ExploreWindow(self, load_ui('resources/explore.ui'))

        self.window = QStackedWidget()
        self.window.addWidget(self.menu.window)
        self.window.addWidget(self.predict.window)
        self.window.addWidget(self.types.window)
        self.window.addWidget(self.explore.window)

        self.window.resize(800, 600)
        self.window.show()

    def show_menu(self):
        self.window.setCurrentWidget(self.menu.window)

    def show_predict(self):
        self.window.setCurrentWidget(self.predict.window)

    def show_types(self):
        self.window.setCurrentWidget(self.types.window)

    def show_explore(self):
        self.window.setCurrentWidget(self.explore.window)
