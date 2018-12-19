from random import randint

from PySide2.QtGui import QIntValidator
from PySide2.QtWidgets import QPushButton, QGraphicsScene, QGridLayout, QLineEdit, QLabel, QLCDNumber, QSizePolicy
from PySide2.QtCore import QObject
from matplotlib.backends.backend_qt5agg import FigureCanvas
from matplotlib.pyplot import legend

from arrhythmia.experimental.mitdb import get_record
from arrhythmia.interface.LogWindow import LogWindow
from arrhythmia.interface.utils import MyQGraphicsView, update_plot, PLOT_WIDTH, Player, load_datafile_name, plot, \
    FREQUENCY, create_double_validator, MyQLineEdit

from arrhythmia.model import create_prediction_engine, engines, FunctionLayer

STEP = 0.05  # step for '<', '>' buttons and player
MINI_PLOT_WIDTH = 10


def update_mini_plot(fig, values):
    ax = fig.axes[1]
    ax.clear()
    ax.set_ylim(0, 100)
    ax.set_xlim(0, MINI_PLOT_WIDTH)
    ax.set_yticks([100])
    # ax.set_yticklabels(["0","50","100"])
    lines = ax.plot(values)
    lines[0].set_color("r")
    legend(lines, ("sveb", "veb", "f"), loc=3, labelspacing=0.1, fontsize=8)


class PredictWindow(QObject):

    def __init__(self, manager, ui_file, ui_logs, parent=None):
        super(PredictWindow, self).__init__(parent)
        self.window = ui_file
        self.log_window = LogWindow(self, ui_logs)
        self.manager = manager
        self.play_active = False
        self.start = 0
        self.sig_len = 0
        self.out_hist = []
        self.player = Player(self, refresh_interval=0.05)
        self.back_player = Player(self, refresh_interval=0.05)
        self.output_updater = Player(self, refresh_interval=1)
        self.figure = None
        self.graphics = MyQGraphicsView()

        self.graphics.setScene(QGraphicsScene())
        self.player.updated.connect(self.plot_next)
        self.back_player.updated.connect(self.plot_prev)
        self.output_updater.updated.connect(self.update_output)

        # loading components of ui
        layout = self.window.findChild(QGridLayout, 'gridLayout')
        #self.start_line = self.window.findChild(QLineEdit, 'start_line')
        self.start_line = MyQLineEdit()
        self.start_line.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        self.start_label = self.window.findChild(QLabel, 'start_label')
        self.data_label = self.window.findChild(QLabel, 'data_label')
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
        layout.addWidget(self.start_line, 0, 11, 1, 1)
        self.start_line.setValidator(QIntValidator(0, 0))

        # Model integration
        self.model = create_prediction_engine(engines[0])

        def extract_output(value):
            self.set_output(value[0] * 100, value[1] * 100, value[2] * 100)
        self.model.set_next(FunctionLayer(extract_output))

        # handlers
        next_button.pressed.connect(self.start_player)
        next_button.released.connect(self.stop_player)
        prev_button.pressed.connect(self.start_back_player)
        prev_button.released.connect(self.stop_player)
        load_button.clicked.connect(self.load_button_handler)
        back_button.clicked.connect(self.back_handler)
        logs_button.clicked.connect(self.logs_handler)
        self.play_button.clicked.connect(self.play_button_handler)
        self.start_line.editingFinished.connect(self.set_start_from_text_line)
        self.start_line.focused.connect(self.stop_player)

    def update_output(self):
        self.model(self.signal[:int(self.start * FREQUENCY)])
        # self.set_output(randint(0, 100), randint(0, 100), randint(0, 100))

    def logs_handler(self):
        self.log_window.show()

    def load_button_handler(self):
        file_path = load_datafile_name(self.window)
        if file_path != "":
            self.load_plot_from_file(file_path)
            self.set_new_plot()

    def load_plot_from_file(self, file_path):
        filename = file_path.split('/')[-1].split('.')[0]  # getting filename from path without extension
        record = get_record(filename)
        signal = record[0]
        self.signal = signal

        figure = plot(signal, None, None, fig_size=(10.8, 5.4))  # plotting without annotations
        figure.add_axes([.8, .0, .2, .2])  # place for mini plot [left,down,width,height]
        self.figure = figure
        self.sig_len = len(signal) // FREQUENCY

        self.data_label.setText("Data view (record {})".format(filename))
        self.log_window.log("Loaded record: {}, signal length: {} seconds".format(filename, self.sig_len))

    def set_new_plot(self):
        canvas = FigureCanvas(self.figure)
        scene = QGraphicsScene()
        scene.addWidget(canvas)
        self.graphics.setScene(scene)
        self.graphics.fitInView(0, 0, scene.width(), scene.height())

        self.stop_player()
        self.start = 0
        self.start_line.setText(str(self.start))
        validator = create_double_validator(0, self.sig_len - PLOT_WIDTH, 2)
        self.start_line.setValidator(validator)
        self.start_label.setText("Start at (max {}):".format(self.sig_len - PLOT_WIDTH))
        self.out_hist = []
        self.set_output(0, 0, 0)

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
        self.start = float(self.start_line.text())
        print(self.start)
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
        self.output_updater.start()

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
        self.log_window.log("SVEB: {} %, VEB: {} %, F: {} %".format(sveb, veb, f))
        if len(self.out_hist) > MINI_PLOT_WIDTH:
            self.out_hist = self.out_hist[1:] + [(sveb, veb, f)]
        else:
            self.out_hist = self.out_hist + [(sveb, veb, f)]

        update_mini_plot(self.figure, self.out_hist)

    def closeEvent(self):
        self.stop_player()
        self.player.wait()
