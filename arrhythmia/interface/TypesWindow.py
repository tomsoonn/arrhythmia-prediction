from PySide2.QtWidgets import QPushButton, QListView, QTextEdit
from PySide2.QtCore import QObject, QStringListModel

from arrhythmia.model.helpers import beat_types


def init_types_list(types_list):
    name_list = ['[' + beat.symbol + ']' + beat.name for beat in beat_types]
    model = QStringListModel()
    model.setStringList(name_list)
    types_list.setModel(model)


def get_type_info(type_name):
    # TODO load and return info
    return type_name


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
