import sys
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvas
from matplotlib.figure import Figure

from arrhythmia.experimental.mitdb import ds1, ds2, get_records

from PySide2.QtWidgets import QPushButton, QGraphicsView, QGraphicsScene
from PySide2.QtCore import QObject


class PredictWindow(QObject):

    def __init__(self, manager, ui_file, parent=None):
        super(PredictWindow, self).__init__(parent)
        self.window = ui_file
        self.manager = manager

        self.line = self.window.findChild(QGraphicsView, 'graphicsView')

        predict_button = self.window.findChild(QPushButton, 'predict_button')
        back_button = self.window.findChild(QPushButton, 'back_button')

        predict_button.clicked.connect(self.predict_handler)
        back_button.clicked.connect(self.back_handler)

    def predict_handler(self):
        # plot anything as for now, will be changed
        train_records = get_records(ds1)
        record_signals = [record.p_signal[:, 0] for record, a, b in train_records]
        figure = Figure()
        canvas = FigureCanvas(figure)
        ax = figure.add_subplot(111)
        ax.plot(record_signals[0][:350])
        canvas.resize(200, 200)
        scene = QGraphicsScene()
        scene.addWidget(canvas)
        self.line.setScene(scene)

    def back_handler(self):
        self.manager.show_menu()
