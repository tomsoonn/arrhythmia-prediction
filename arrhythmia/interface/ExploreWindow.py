import numpy as np
from PySide2.QtGui import QIntValidator

from PySide2.QtWidgets import QPushButton, QGraphicsScene, QGridLayout, QLineEdit, QLabel
from PySide2.QtCore import QObject

from matplotlib.backends.backend_qt5agg import FigureCanvas

from arrhythmia.experimental.mitdb import get_record
from arrhythmia.interface.utils import update_plot, plot, load_datafile_name, MyQGraphicsView, Player, PLOT_WIDTH, \
    FREQUENCY

STEP = 0.1  # step for '<' and '>' buttons


class ExploreWindow(QObject):

    def __init__(self, manager, ui_file, parent=None):
        super(ExploreWindow, self).__init__(parent)
        self.window = ui_file
        self.manager = manager
        self.play_active = False
        self.start = 0
        self.sig_len = 0
        self.player = Player(self)
        self.back_player = Player(self)
        self.figure = None
        self.graphics = MyQGraphicsView()

        self.graphics.setScene(QGraphicsScene())
        self.player.updated.connect(self.plot_next)
        self.back_player.updated.connect(self.plot_prev)

        # loading components of ui
        layout = self.window.findChild(QGridLayout, 'gridLayout')
        back_button = self.window.findChild(QPushButton, 'back_button')
        load_button = self.window.findChild(QPushButton, 'load_button')
        next_button = self.window.findChild(QPushButton, 'next_button')
        prev_button = self.window.findChild(QPushButton, 'prev_button')
        self.play_button = self.window.findChild(QPushButton, 'play_button')
        self.start_label = self.window.findChild(QLabel, 'start_label')
        self.start_line = self.window.findChild(QLineEdit, 'start_line')

        layout.addWidget(self.graphics, 2, 0, 1, 8)  # put in layout
        self.start_line.setValidator(QIntValidator(0, 0))

        back_button.clicked.connect(self.back_to_menu_handler)
        load_button.clicked.connect(self.load_button_handler)
        next_button.pressed.connect(self.start_player)
        next_button.released.connect(self.stop_player)
        prev_button.pressed.connect(self.start_back_player)
        prev_button.released.connect(self.stop_player)
        self.play_button.clicked.connect(self.play_handler)
        self.start_line.returnPressed.connect(self.set_start_from_text_line)

    def load_button_handler(self):
        file_path = load_datafile_name(self.window)
        if file_path != "":
            self.load_plot_from_file(file_path)
            self.set_plot()

    def load_plot_from_file(self, file_path):
        filename = file_path.split('/')[-1].split('.')[0]  # getting filename from path without extension
        record = get_record(filename)
        signal = record[0]

        samples = record[1]
        samples = np.asarray([samples])

        symbols = [beat.symbol for beat in record[2]]
        symbols = [symbols]

        figure = plot(signal, samples, symbols)
        self.figure = figure
        self.sig_len = len(signal)//FREQUENCY

    def set_plot(self):
        canvas = FigureCanvas(self.figure)
        scene = QGraphicsScene()
        scene.addWidget(canvas)
        self.graphics.setScene(scene)
        self.graphics.fitInView(0, 0, scene.width(), scene.height())

        self.start = 0
        self.start_line.setValidator(QIntValidator(0, self.sig_len - PLOT_WIDTH))
        self.start_line.setText(str(self.start))
        self.start_label.setText("Start at(max {}):".format(self.sig_len - PLOT_WIDTH))

    def set_start_from_text_line(self):
        self.start = int(self.start_line.text())
        if self.sig_len > 0:
            update_plot(self.start, self.figure)

    def plot_next(self):
        if self.start + STEP < self.sig_len - PLOT_WIDTH:
            self.update_start_and_plot(STEP)
        else:
            self.stop_player()

    def plot_prev(self):
        if self.start - STEP >= 0:
            self.update_start_and_plot(-STEP)
        else:
            self.stop_player()

    def update_start_and_plot(self, update):
        self.start += update  # step 0.1 sec
        self.start = round(self.start, 2)
        update_plot(self.start, self.figure)
        self.start_line.setText(str(self.start))

    def play_handler(self):
        if self.play_active:
            self.stop_player()
        elif self.sig_len > 0:
            self.start_player()
            self.play_button.setText('Stop')

    def start_player(self):
        self.play_active = True
        self.player.start()

    def start_back_player(self):
        self.play_active = True
        self.back_player.start()

    def stop_player(self):
        self.play_active = False
        self.play_button.setText('Play')

    def back_to_menu_handler(self):
        if self.play_active:
            self.play_handler()
        self.manager.show_menu()

    def closeEvent(self):
        self.stop_player()
        self.player.wait()
