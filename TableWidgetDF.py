from PyQt5.QtWidgets import *
from PyQt5.QtGui import QDoubleValidator
from datetime import datetime

class FloatDelegate(QItemDelegate):
    def __init__(self, parent=None):
        super().__init__()

    def createEditor(self, parent, option, index):
        editor = QLineEdit(parent)
        validator = QDoubleValidator()
        validator.setBottom(0)
        validator.setDecimals(2)
        editor.setValidator(validator)

        return editor

class TableWidgetDF(QTableWidget):
    def __init__(self, df):
        super().__init__()
        # self.cellChanged[int, int].connect(self.updateDF)

    #
    #
    # def setDF(self, df):
    #     self.df = df
    #
    #     # set table dimension
    #     nRows, nColumns = self.df.shape
    #     self.setColumnCount(nColumns)
    #     self.setRowCount(nRows)
    #
    #     self.setItemDelegate(FloatDelegate())
    #
    def updateDF(self, row, column):
        text = self.item(row[1], column[5]).text().replace(',','.')
        self.df.iloc[row[1], column[5]] = float(text)