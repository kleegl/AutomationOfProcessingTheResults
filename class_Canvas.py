import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.transforms import Affine2D
import mpl_toolkits.axisartist.floating_axes as floating_axes
from matplotlib import transforms
import matplotlib.ticker as ticker
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import *
import sys

class Canvas(FigureCanvas):
    def __init__(self, parent, df, row, temperature, items, deep): #, deep
        row = row
        temperature = temperature
        items = items
        deep = deep

        fig, self.ax = plt.subplots(figsize=(6,7))
        super().__init__(fig)
        self.setParent(parent)
        self.ax.clear()

        # fig = plt.figure()
        #
        # plot_extents = 0, 10, 0, 10
        # transform = Affine2D().rotate_deg(90)
        # helper = floating_axes.GridHelperCurveLinear(transform, plot_extents)
        # self.ax = floating_axes.FloatingSubplot(fig, 111, grid_helper=helper)

        # fig.add_subplot(self.ax)
        # plt.show()

        self.ax.set(title=f'График по {row} строке')
        self.ax.set_xlabel("Температура, °C", fontweight='bold', fontsize=16)
        self.ax.set_ylabel("Глубина, м", fontweight='bold', fontsize=16)

        self.ax.invert_yaxis()
        self.ax.xaxis.set_label_position('bottom')
        self.ax.yaxis.set_label_position('left')
        # self.ax.invert_yaxis()

        self.ax.xaxis.set_major_locator(ticker.AutoLocator())
        self.ax.xaxis.set_minor_locator(ticker.AutoLocator())
        self.ax.yaxis.set_major_locator(ticker.AutoLocator())
        self.ax.yaxis.set_minor_locator(ticker.AutoLocator())
        self.ax.grid()
        self.ax.minorticks_on()

        self.ax.plot(items, list(range(len(items))), marker='.')
        # self.ax.plot(items, marker='.')
        plt.show()

class AppDemo(QWidget):
    def __init__(self, df, row, temperature, items, deep): #, deep
        super().__init__()
        self.resize(650, 750)
        chart = Canvas(self, df, row, temperature, items, deep) #, deep