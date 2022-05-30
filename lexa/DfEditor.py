from PySide2.QtWidgets import *
from PySide2.QtGui import QDoubleValidator

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
        self.cellChanged[int, int].connect(self.updateDF)

    def setDF(self, df):
        self.df = df

        # set table dimension
        nRows, nColumns = self.df.shape
        self.setColumnCount(nColumns)
        self.setRowCount(nRows)

        headers = [str(i) for i in df.columns.tolist()]

        self.setHorizontalHeaderLabels(headers)
        self.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.setItemDelegate(FloatDelegate())

        # data insertion
        for i in range(self.rowCount()):
            for j in range(self.columnCount()):
                self.setItem(i, j, QTableWidgetItem(str(round(self.df.iloc[i, j],2)).replace('.',',')))


    def updateDF(self, row, column):
        text = self.item(row, column).text().replace(',','.')
        self.df.iloc[row, column] = float(text)