from PySide2.QtGui import QIntValidator
from matplotlib.backends.backend_qt5agg import FigureCanvas

from arrhythmia.experimental.mitdb import get_record

from PySide2.QtWidgets import QPushButton, QGraphicsScene, QGridLayout, QTextEdit, QLineEdit, QLabel, QLCDNumber
from PySide2.QtCore import QObject

from arrhythmia.interface.LogWindow import LogWindow
from arrhythmia.interface.utils import MyQGraphicsView, update_plot, PLOT_WIDTH, Player, load_datafile_name, plot, \
    FREQUENCY

STEP = 0.05  # step for '<', '>' buttons and player


class PredictWindow(QObject):

    def __init__(self, manager, ui_file, ui_logs, parent=None):
        super(PredictWindow, self).__init__(parent)
        self.window = ui_file
        self.log_window = LogWindow(self, ui_logs)
        self.manager = manager
        self.play_active = False
        self.start = 0
        self.sig_len = 0
        self.player = Player(self, refresh_interval=0.05)
        self.back_player = Player(self, refresh_interval=0.05)
        self.figure = None
        self.graphics = MyQGraphicsView()

        self.graphics.setScene(QGraphicsScene())
        self.player.updated.connect(self.plot_next)
        self.back_player.updated.connect(self.plot_prev)

        # loading components of ui
        layout = self.window.findChild(QGridLayout, 'gridLayout')
        self.start_line = self.window.findChild(QLineEdit, 'start_line')
        self.start_label = self.window.findChild(QLabel, 'start_label')
        self.play_button = self.window.findChild(QPushButton, 'play_button')
        next_button = self.window.findChild(QPushButton, 'go_next_button')
        prev_button = self.window.findChild(QPushButton, 'go_prev_button')
        back_button = self.window.findChild(QPushButton, 'back_button')
        load_button = self.window.findChild(QPushButton, 'load_button')
        settings_button = self.window.findChild(QPushButton, 'settings_button')
        logs_button = self.window.findChild(QPushButton, 'logs_button')
        self.sveb_lcdnumber = self.window.findChild(QLCDNumber, 'sveb_value')
        self.veb_lcdnumber = self.window.findChild(QLCDNumber, 'veb_value')
        self.f_lcdnumber = self.window.findChild(QLCDNumber, 'f_value')

        layout.addWidget(self.graphics, 5, 0, 1, 15)  # put in layout
        self.start_line.setValidator(QIntValidator(0, 0))

        # handlers
        next_button.pressed.connect(self.start_player)
        next_button.released.connect(self.stop_player)
        prev_button.pressed.connect(self.start_back_player)
        prev_button.released.connect(self.stop_player)
        load_button.clicked.connect(self.load_button_handler)
        back_button.clicked.connect(self.back_handler)
        logs_button.clicked.connect(self.logs_handler)
        self.play_button.clicked.connect(self.play_button_handler)
        self.start_line.returnPressed.connect(self.set_start_from_text_line)

    def logs_handler(self):
        self.log_window.show()

    def load_button_handler(self):
        file_path = load_datafile_name(self.window)
        if file_path != "":
            self.load_plot_from_file(file_path)
            self.set_plot()

    def load_plot_from_file(self, file_path):
        filename = file_path.split('/')[-1].split('.')[0]  # getting filename from path without extension
        record = get_record(filename)
        signal = record[0]

        figure = plot(signal, None, None, (10, 4))  # plotting without annotations
        self.figure = figure
        self.sig_len = len(signal)//FREQUENCY

        self.log_window.log("Loaded record: {}, signal length: {} seconds".format(filename, self.sig_len))

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

    def set_start_from_text_line(self):
        self.start = int(self.start_line.text())
        if self.sig_len > 0:
            update_plot(self.start, self.figure)

    def play_button_handler(self):
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

    def back_handler(self):
        if self.play_active:
            self.play_button_handler()
        self.log_window.close_handler()
        self.manager.show_menu()

    def set_output(self, sveb, veb, f):
        self.sveb_lcdnumber.display(sveb)
        self.veb_lcdnumber.display(veb)
        self.f_lcdnumber.display(f)

    def closeEvent(self):
        self.stop_player()
        self.player.wait()
