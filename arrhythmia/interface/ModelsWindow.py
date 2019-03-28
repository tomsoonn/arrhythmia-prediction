from PySide2.QtWidgets import QPushButton, QListView, QTextEdit
from PySide2.QtCore import QObject, QStringListModel

from arrhythmia.model import engines


def init_types_list(types_list):
    name_list = [engine.name for engine in engines]
    model = QStringListModel()
    model.setStringList(name_list)
    types_list.setModel(model)


def get_model_info(model_index):
    description = engines[model_index].description
    return description


class ModelsWindow(QObject):

    def __init__(self, predict, ui_file, parent=None):
        super(ModelsWindow, self).__init__(parent)
        self.window = ui_file
        self.predict = predict

        ok_button = self.window.findChild(QPushButton, 'ok_button')
        self.types_list = self.window.findChild(QListView, 'types_list')
        self.text_field = self.window.findChild(QTextEdit, 'text_field')

        ok_button.clicked.connect(self.ok_handler)
        self.types_list.clicked.connect(self.type_clicked)

        init_types_list(self.types_list)

    def ok_handler(self):
        self.predict.change_model(self.types_list.currentIndex().row())
        self.window.close()

    def type_clicked(self):
        info = get_model_info(self.types_list.currentIndex().row())
        self.text_field.setPlainText(info)

    def show(self):
        self.window.show()
