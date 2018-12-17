import os
from time import sleep

import numpy as np
from PySide2.QtCore import QThread, Signal
from PySide2.QtWidgets import QFileDialog, QGraphicsView

from arrhythmia.experimental.mitdb import data_dir
from arrhythmia.interface.wfdb_plot_patched import plot_items

PLOT_WIDTH = 6  # length of shown plot, in seconds
FREQUENCY = 360
TIME_UNITS = 'seconds'


def update_plot(start, figure):
    ax = figure.axes[0]
    ax.set_xlim(start, start + PLOT_WIDTH)
    # ax.autoscale(enable=True, axis='y', tight=True)
    autoscale_y(ax, margin=0.1)
    figure.canvas.draw_idle()


def plot(signal, samples, symbols, fig_size=(10, 6)):
    figure = plot_items(signal=signal, ann_samp=samples, ann_sym=symbols,
                        sig_units=['mV'], time_units=TIME_UNITS, figsize=fig_size, fs=360,
                        # ecg_grids='all', # not working on this big data
                        return_fig=True)
    figure.tight_layout()
    ax = figure.axes[0]
    ax.set_xlabel("time[{}]".format(TIME_UNITS))
    ax.set_xlim(0, PLOT_WIDTH)
    # ax.autoscale(enable=True, axis='y', tight=True)
    autoscale_y(ax, 0.1)
    ax.grid()

    return figure


def autoscale_y(ax, margin=0.1):
    """This function rescales the y-axis based on the data that is visible given the current xlim of the axis.
    ax -- a matplotlib axes object
    margin -- the fraction of the total height of the y-data to pad the upper and lower ylims"""

    def get_bottom_top(line):
        xd = line.get_xdata()
        yd = line.get_ydata()
        lo, hi = ax.get_xlim()
        y_displayed = yd[((xd > lo) & (xd < hi))]
        h = np.max(y_displayed) - np.min(y_displayed)
        bot = np.min(y_displayed) - margin * h
        top = np.max(y_displayed) + margin * h
        return bot, top

    lines = ax.get_lines()
    bot, top = np.inf, -np.inf

    for line in lines:
        new_bot, new_top = get_bottom_top(line)
        if new_bot < bot:
            bot = new_bot
        if new_top > top:
            top = new_top

    ax.set_ylim(bot, top)


def load_datafile_name(window):
    file_path = QFileDialog.getOpenFileName(window, 'Load file', data_dir, '*.dat')[0]
    return file_path


class MyQGraphicsView(QGraphicsView):
    def __init__(self, parent=None):
        super(MyQGraphicsView, self).__init__(parent)

    def resizeEvent(self, event):
        self.fitInView(0, 0, self.scene().width(), self.scene().height())


class Player(QThread):
    updated = Signal()

    def __init__(self, window, refresh_interval=0.5, parent=None):
        super(Player, self).__init__(parent)
        self.window = window
        self.interval = refresh_interval

    def run(self):
        while self.window.play_active:
            self.updated.emit()
            sleep(self.interval)
