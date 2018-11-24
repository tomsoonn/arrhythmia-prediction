import os

from matplotlib.backends.backend_qt5agg import FigureCanvas
from matplotlib.figure import Figure

from arrhythmia.experimental.mitdb import get_record

from PySide2.QtWidgets import QPushButton, QGraphicsView, QGraphicsScene, QFileDialog, QGridLayout, QTextEdit
from PySide2.QtCore import QObject

STEP = 36  # step for '<' and '>' buttons
PLOT_WIDTH = STEP * 30  # length of shown plot


# TODO sensible plotting
# as for now matplotlib basic plot, just to see something


def update_plot(start, figure):
    ax = figure.axes[0]
    ax.axis([start, start + PLOT_WIDTH, -1, 2])

    # Matplotlib documentation says it should be
    # ax.axis(start, start + PLOT_WIDTH, -1, 2)
    # but there is a bug in implementation

    ax.autoscale(enable=True, axis='y', tight=True)
    figure.canvas.draw_idle()


def plot(record_signals, start, graphics):
    figure = Figure(dpi=800)
    ax = figure.add_subplot(111)
    ax.plot(record_signals)  # plot 3 seconds of record
    ax.axis([start, start + PLOT_WIDTH, -1, 2])
    ax.grid()
    ax.autoscale(enable=True, axis='y', tight=True)
    figure.tight_layout()
    canvas = FigureCanvas(figure)
    scene = QGraphicsScene()
    scene.addWidget(canvas)
    graphics.setScene(scene)
    return figure


class PredictWindow(QObject):

    def __init__(self, manager, ui_file, parent=None):
        super(PredictWindow, self).__init__(parent)
        self.window = ui_file
        self.manager = manager
        self.play_active = False
        self.start = 0
        self.signals = []
        self.figure = Figure()
        self.graphics = MyQGraphicsView()
        self.text_logs = self.window.findChild(QTextEdit, 'textEdit')

        self.graphics.setScene(QGraphicsScene())

        layout = self.window.findChild(QGridLayout, 'gridLayout')
        layout.addWidget(self.graphics, 4, 0, 1, 5)  # put in layout

        go_next_button = self.window.findChild(QPushButton, 'go_next_button')
        go_prev_button = self.window.findChild(QPushButton, 'go_prev_button')
        back_button = self.window.findChild(QPushButton, 'back_button')
        load_button = self.window.findChild(QPushButton, 'load_button')
        self.play_button = self.window.findChild(QPushButton, 'play_button')

        go_next_button.clicked.connect(self.go_next_handler)
        go_prev_button.clicked.connect(self.go_prev_handler)
        self.play_button.clicked.connect(self.play_handler)
        load_button.clicked.connect(self.load_handler)
        back_button.clicked.connect(self.back_handler)

    def go_next_handler(self):
        if self.start + STEP < len(self.signals):
            self.start += STEP  # step 0.1 sec
            update_plot(self.start, self.figure)

    def go_prev_handler(self):
        if self.start - STEP >= 0:
            self.start -= STEP  # step 0.1 sec
            update_plot(self.start, self.figure)

    def play_handler(self):
        if self.play_active:
            self.play_button.setText('Play')
            self.play_active = False
        else:
            self.play_button.setText('Stop')
            self.play_active = True
            self.start_playing()

    def start_playing(self):
        # while self.start + STEP < len(self.signals) and self.play_active:
        #     self.go_next_handler()
        #     sleep(1)
        # TODO
        pass

    def load_handler(self):
        actual_dir = os.path.dirname(os.path.realpath(__file__))
        # getting main project directory as '.../download/mitdb' is not working
        # so as for now
        project_dir = os.path.join(actual_dir, '../download/mitdb')
        filepath = QFileDialog.getOpenFileName(self.window, 'Load file', project_dir, '*.dat')[0]
        if filepath != "":
            self.set_right_plot(filepath)

    def set_right_plot(self, filepath):
        filename = filepath.split('/')[-1].split('.')[0]  # getting filename from path without extension
        record = get_record(filename)[0]
        self.signals = record.p_signal[:, 0]
        self.start = 0
        self.figure = plot(self.signals, self.start, self.graphics)
        self.text_logs.clear()
        self.text_logs.append("Loaded data from record : %s" % filename)

    def log(self, content):
        self.text_logs.append(content)

    def back_handler(self):
        self.manager.show_menu()


class MyQGraphicsView(QGraphicsView):
    def __init__(self, parent=None):
        super(MyQGraphicsView, self).__init__(parent)

    def resizeEvent(self, event):
        self.fitInView(0, 0, self.scene().width(), self.scene().height())
