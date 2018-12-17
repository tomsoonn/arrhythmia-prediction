import os

from PySide2.QtWidgets import QPushButton, QListView, QTextEdit
from PySide2.QtCore import QObject, QStringListModel, QFile

from arrhythmia.model.helpers import beat_types


def init_types_list(types_list):
    name_list = ['[' + beat.symbol + ']' + beat.name for beat in beat_types]
    model = QStringListModel()
    model.setStringList(name_list)
    types_list.setModel(model)


def get_type_info(type_name):
    type_symbol = type_name.split("]")[0]
    type_symbol = type_symbol.split("[")[1]
    type_symbol = type_symbol.lower()

    dir = os.path.dirname(os.path.realpath(__file__))
    filepath = os.path.join(dir, "resources", type_symbol + '.txt')

    description = ""
    if os.path.isfile(filepath):
        with open(filepath) as f:
            for x in f:
                description += x
    else:
        description = "No data"
    return description


class TypesWindow(QObject):

    def __init__(self, manager, ui_file, parent=None):
        super(TypesWindow, self).__init__(parent)
        self.window = ui_file
        self.manager = manager

        back_button = self.window.findChild(QPushButton, 'back_button')
        self.types_list = self.window.findChild(QListView, 'types_list')
        self.text_field = self.window.findChild(QTextEdit, 'text_field')

        back_button.clicked.connect(self.back_handler)
        self.types_list.clicked.connect(self.type_clicked)

        init_types_list(self.types_list)

    def back_handler(self):
        self.manager.show_menu()

    def type_clicked(self):
        info = get_type_info(self.types_list.currentIndex().data())
        self.text_field.setPlainText(info)
