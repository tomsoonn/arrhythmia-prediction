from PySide2.QtGui import QIntValidator
from matplotlib.backends.backend_qt5agg import FigureCanvas
from matplotlib.figure import Figure

from arrhythmia.experimental.mitdb import get_record

from PySide2.QtWidgets import QPushButton, QGraphicsScene, QGridLayout, QTextEdit, QLineEdit, QLabel
from PySide2.QtCore import QObject

from arrhythmia.interface.utils import MyQGraphicsView, update_plot, PLOT_WIDTH, STEP, Player, load_datafile_name, plot


class PredictWindow(QObject):

    def __init__(self, manager, ui_file, parent=None):
        super(PredictWindow, self).__init__(parent)
        self.window = ui_file
        self.manager = manager
        self.play_active = False
        self.start = 0
        self.sig_len = 0
        self.player = Player(self)
        self.back_player = Player(self)
        self.player.updated.connect(self.next_handler)
        self.back_player.updated.connect(self.prev_handler)
        self.figure = Figure()
        self.graphics = MyQGraphicsView()
        self.text_logs = self.window.findChild(QTextEdit, 'textEdit')

        self.graphics.setScene(QGraphicsScene())

        layout = self.window.findChild(QGridLayout, 'gridLayout')
        layout.addWidget(self.graphics, 1, 0, 1, 8)  # put in layout

        self.start_line = self.window.findChild(QLineEdit, 'start_line')
        self.start_line.setValidator(QIntValidator(0, 0))
        self.start_label = self.window.findChild(QLabel, 'start_label')

        next_button = self.window.findChild(QPushButton, 'go_next_button')
        prev_button = self.window.findChild(QPushButton, 'go_prev_button')
        back_button = self.window.findChild(QPushButton, 'back_button')
        load_button = self.window.findChild(QPushButton, 'load_button')
        settings_button = self.window.findChild(QPushButton, 'settings_button')
        self.play_button = self.window.findChild(QPushButton, 'play_button')

        next_button.pressed.connect(self.start_player)
        next_button.released.connect(self.stop_player)
        prev_button.pressed.connect(self.start_back_player)
        prev_button.released.connect(self.stop_player)
        self.play_button.clicked.connect(self.play_handler)
        load_button.clicked.connect(self.load_handler)
        back_button.clicked.connect(self.back_handler)
        self.start_line.returnPressed.connect(self.change_start)

    def next_handler(self):
        if self.start + STEP < self.sig_len - PLOT_WIDTH:
            self.start += STEP  # step 0.1 sec
            update_plot(self.start, self.figure)
            self.start_line.setText(str(self.start))

    def prev_handler(self):
        if self.start - STEP >= 0:
            self.start -= STEP  # step 0.1 sec
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

    def stop_player(self):
        self.play_active = False
        self.play_button.setText('Play')

    def load_handler(self):
        file_path = load_datafile_name(self.window)
        if file_path != "":
            self.load_plot_from_file(file_path)
            self.set_plot()

    def start_back_player(self):
        self.play_active = True
        self.back_player.start()

    def change_start(self):
        self.start = int(self.start_line.text())
        update_plot(self.start, self.figure)

    def load_plot_from_file(self, file_path):
        filename = file_path.split('/')[-1].split('.')[0]  # getting filename from path without extension
        record = get_record(filename)
        signal = record[0].p_signal[:, 0]

        figure = plot(signal, None, None, (10, 3.5))  # plotting without annotations
        self.figure = figure
        self.sig_len = len(signal)
        self.start_line.setValidator(QIntValidator(0, self.sig_len - PLOT_WIDTH))
        self.log("Loaded record: {}, signal length: {} samples".format(filename, self.sig_len))

    def set_plot(self):
        canvas = FigureCanvas(self.figure)
        scene = QGraphicsScene()
        scene.addWidget(canvas)
        self.graphics.setScene(scene)
        self.graphics.fitInView(0, 0, scene.width(), scene.height())
        self.start_line.setText(str(self.start))
        self.start_label.setText("Start at(max {}):" .format(self.sig_len-PLOT_WIDTH))

    def log(self, content):
        self.text_logs.append(content)

    def back_handler(self):
        if self.play_active:
            self.play_handler()
        self.manager.show_menu()
