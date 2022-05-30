from PyQt5 import *
from vkr import Ui_MainWindow
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import *
import sys
import pandas as pd
from class_Canvas import *
import openpyxl
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from datetime import datetime
import os
import shutil
import re
import pyodbc
import sqlite3

class App():
    def __init__(self):
        super(App, self).__init__()

        app = QtWidgets.QApplication(sys.argv)
        MainWindow = QtWidgets.QMainWindow()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(MainWindow)
        MainWindow.show()

        self.button_pressed()
        self.file_name = ''
        self.df_global = pd.DataFrame({'A': []})
        self.critical_temperature = ''
        self.items_for_canvas = list()
        self.deep = list()

        self.error_when_open = QMessageBox()
        self.msg_exit = QMessageBox()

        sys.exit(app.exec_())

    def button_pressed(self):
        self.ui.actionOpen.triggered.connect(lambda: self.open_file())
        self.ui.actionOpen.setShortcut('space')

        # self.ui.actionSave.triggered.connect(lambda: self.save_file())
        self.ui.actionSave_As.triggered.connect(lambda: self.save_file_as())

        self.ui.actionGuide.triggered.connect(lambda: self.open_guide())

        self.ui.actionAbout.triggered.connect(lambda: self.about())
        self.ui.actionExit.triggered.connect(lambda: self.exit())

        self.ui.actionCreate.triggered.connect(lambda: self.create_canvas())

        # self.ui.lineEdit_temp.editingFinished.connect(lambda: self.enter_critical_temperature())
        # self.ui.lineEdit_row.editingFinished.connect(lambda: self.enter_row_for_parsing())

        # self.ui.lineEdit_temp.textChanged[str].connect(lambda: self.enter_critical_temperature(self.ui.lineEdit_temp.text()))
        self.ui.lineEdit_temp.editingFinished.connect(
            lambda: self.enter_critical_temperature(self.ui.lineEdit_temp.text()))

        # self.ui.lineEdit_temp.textChanged[str].connect(lambda: self.enter_critical_temperature())
        # self.ui.lineEdit_row.editingFinished.connect(lambda: self.enter_row_for_parsing())

        self.ui.pushButton.clicked.connect(lambda: self.start_analysis(self.ui.lineEdit_row.text()))
        self.ui.actionCreate.setShortcut('alt+r')

    def open_file(self):
        filter = "All files (*.*);;Csv file (*.csv);;Text files (*.txt);;Xls (*.xls);;Xlsx (*.xlsx)"
        self.file_name = QFileDialog().getOpenFileName(None, 'Открыть', '', filter)[0]
        path = os.path.abspath(self.file_name)
        if self.file_name == '':
            self.error_when_open.setWindowTitle('Ошибка')
            self.error_when_open.setStandardButtons(QMessageBox.Close)
            self.error_when_open.setText('Вы не открыли файл')
            self.error_when_open.exec()
        else:
            self.read_file(path)

    def read_file(self, path):
        if self.file_name.count('.xlsx') == 1:
            self.df_global = pd.read_excel(self.file_name, engine='openpyxl', header=None)
        elif self.file_name.count('.xls') == 1:
            self.df_global = pd.read_excel(self.file_name, engine='xlrd', header=None)
        elif self.file_name.count('.csv') == 1:
            self.df_global = pd.read_csv(self.file_name, header=None, thousands=';')
        elif self.file_name.count('.txt') == 1:
            self.df_global = pd.read_table(self.file_name, header=None, sep=';', engine='python', thousands=';')
            self.df_global.replace(',', '.')

        elif self.file_name.count('.mdf') == 1:
            cnxn_str = (
                r'DRIVER=(localDB)\DKCL_DB;'
                r'SERVER=(localDB)\DKCL_DB;'
                r'Trusted_Connection=yes;'
                r'AttachDbFileName='+self.file_name)

            cnxn = pyodbc.connect(cnxn_str)
            self.df_global = pd.read_sql("SELECT * FROM Table1", cnxn)

            # self.file_name = self.file_name.split('/')
            # f = shutil.copy(path, path + '.csv')
            # self.df_global = pd.read_csv(f, header=None)

        if self.df_global.size == 0:
            self.error_when_open.setWindowTitle('Ошибка')
            self.error_when_open.setStandardButtons(QMessageBox.Close)
            self.error_when_open.setText('Файл пуст')
            self.error_when_open.exec()
        else:
            self.ui.statusbar.showMessage(self.file_name)
            self.show_df()

    def show_df(self):
        self.df_global = self.df_global.fillna('')
        self.df_global.round(decimals=4)
        self.df_global = self.df_global.apply(pd.to_numeric, errors='ignore')

        # self.tableItem = QTableWidgetItem(str(value))
        # self.tableItem.setTextColor(QtGui.QColor(255, 255, 255))
        # self.ui.tableWidget.setItem(row[0], index, self.tableItem)


        # self.df_global.dropna(1, inplace=True)  # удаление пустых строк
        self.ui.tableWidget.setRowCount(self.df_global.shape[0])
        self.ui.tableWidget.setColumnCount(self.df_global.shape[1])

        for row in self.df_global.iterrows():  # индексировать строку как пару (индекс, ряд)
            values = row[1]
            for col_index, value in enumerate(values):  # получаем индекс столбца и значение по диапазону values
                if isinstance(value, (float)):  # проверяет, есть ли первый аругумент во втором
                    value = round(value, 4)
                    self.tableItem = QTableWidgetItem(str(value))  # экземпляр класса
                    self.ui.tableWidget.setItem(row[0], col_index, self.tableItem)
                elif isinstance(value, (int, datetime, str)):
                        self.tableItem = QTableWidgetItem(str(value))
                        # if pd.notnull(value):
                        #     self.tableItem.setTextColor(QtGui.QColor(255, 255, 255))
                        #     self.ui.tableWidget.setItem(row[0], col_index, self.tableItem)
                        self.ui.tableWidget.setItem(row[0], col_index, self.tableItem)

    def enter_critical_temperature(self, temperature):
        if temperature == '':
            while self.ui.tableWidget.rowCount() > 0:
                self.ui.tableWidget.removeRow(0)
            self.show_df()

        elif temperature.find(',') == -1:
            self.critical_temperature = float(temperature)
        # elif temperature.startswith('-') is True:
        #     minus = '-'
        #     temperature.
        else:
            temperature = temperature.replace(',', '.')
            self.critical_temperature = float(temperature)

            # if self.ui.lineEdit_row.text() == '':
            #     self.parsing_all_rows(critical_temperature)
            # else:
            #     self.parsing_select_row(self.ui.lineEdit_row.text(), critical_temperature)

    def start_analysis(self, row):
        if self.ui.lineEdit_temp.text() == '':
            self.error_when_open.setWindowTitle('Ошибка')
            self.error_when_open.setStandardButtons(QMessageBox.Close)
            self.error_when_open.setText('Вы не ввели контрольное значение температуры!')
            self.error_when_open.exec()
            return
        if len(row) == 0:
            while self.ui.tableWidget.rowCount() > 0:
                self.ui.tableWidget.removeRow(0)
            self.show_df()
            self.parsing_all_rows()
        else:
            row = int(row)
            if row > len(self.df_global.index) or row <= 1:
                self.error_when_open.setWindowTitle('Ошибка')
                self.error_when_open.setStandardButtons(QMessageBox.Close)
                self.error_when_open.setText('Эту строки нельзя проанализировать')
                self.error_when_open.exec()
                return
            while self.ui.tableWidget.rowCount() > 0:
                self.ui.tableWidget.removeRow(0)
            self.show_df()
            self.parsing_select_row(row)

    def parsing_all_rows(self):
        self.ui.label_2.setText(' ')
        item_list = list()
        rows_with_err = list()
        if self.file_name == '':
            self.error_when_open.setWindowTitle('Ошибка')
            self.error_when_open.setStandardButtons(QMessageBox.Close)
            self.error_when_open.setText('Вы не открыли файл')
            self.error_when_open.exec()
        else:
            self.ui.statusbar.showMessage('Анализ всех строк')

            # parsing

            # columns = len(self.df_global.count())
            items_err = list()

            # self.ui.tableWidget.setStyleSheet("background-color: #FFFFFF")
            for row in range(1, len(self.df_global)):
                col = self.df_global.iloc[row][5:]
                columns = (col != '').sum() + 5
                for column in range(5, columns):
                    item = self.df_global.iat[row, column].astype('float64')  # single value: .at, .iat
                    if item > self.critical_temperature:

                        self.tableItem = QTableWidgetItem(str(item))  # экземпляр класса
                        self.ui.tableWidget.setItem(row, column, self.tableItem)
                        self.tableItem.setBackground(QtGui.QColor(100, 100, 150))
                        item_list.append(self.tableItem)

                        items_err.append(self.ui.tableWidget.item(row, column))
                        if rows_with_err.count(row + 1) == 0:
                            rows_with_err.append(row + 1)
                    if len(rows_with_err) != 0:
                        self.ui.label_2.setText(
                            f'Значения, превышающие контрольную температуру, найдены в строках: {str(rows_with_err)} ')
                    else:
                        self.ui.label_2.setText('Значения, превышающие контрольное, не найдены')
        self.ui.statusbar.showMessage('Анализ завершен')

    def parsing_select_row(self, row):
        self.items_for_canvas.clear()
        item_list = list()
        row_with_err = list()
        if self.file_name == '':
            self.error_when_open.setWindowTitle('Ошибка')
            self.error_when_open.setStandardButtons(QMessageBox.Close)
            self.error_when_open.setText('Вы не открыли файл')
            self.error_when_open.exec()
        elif self.critical_temperature == '':
            self.error_when_open.setWindowTitle('Ошибка')
            self.error_when_open.setStandardButtons(QMessageBox.Close)
            self.error_when_open.setText('Вы не ввели контрольное значение температуры')
            self.error_when_open.exec()
        else:
            row = int(row) - 1
            # col = self.df_global.iloc[row][5:]
            # columns = (col != '').sum()
            # if len(self.df_global) != columns:
            #     columns = columns + 5
            items_err = list()
            columns = len(self.df_global.count())
            for column in range(5, columns):
                flag = 0
                # item = self.df_global.iat[row, column].astype('float64').dtypes  # single value: .at, .iat
                item = self.df_global.iat[row, column]
                if item == '':
                    flag = 1
                item = round(item, 5)
                self.items_for_canvas.append(item)
                if item > self.critical_temperature and flag == 0:
                    self.tableItem = QTableWidgetItem(str(item))  # экземпляр класса
                    self.ui.tableWidget.setItem(row, column, self.tableItem)
                    self.tableItem.setBackground(QtGui.QColor(100, 100, 150))
                    item_list.append(self.tableItem)
                    items_err.append(self.ui.tableWidget.item(row, column))

                    if row_with_err.count(row + 1) == 0:
                        row_with_err.append(row + 1)

                if len(row_with_err) != 0:
                    self.ui.label_2.setText(
                                f'Значения, превышающие контрольную температуру, найдены в строке: {str(row_with_err)} ')
                else:
                    self.ui.label_2.setText('Значения, превышающие контрольное, не найдены')
            self.ui.statusbar.showMessage('Анализ завершен')
        self.take_deep(row)

    def take_deep(self, row):
        self.deep.append(self.df_global.iloc[0][5:])

    def create_canvas(self):
        row = self.ui.lineEdit_row.text()
        if self.df_global.empty is True:
            error_when_create_canvas = QMessageBox()
            error_when_create_canvas.setWindowTitle('Ошибка')
            error_when_create_canvas.setStandardButtons(QMessageBox.Close)
            error_when_create_canvas.setText('Файл не открыт!')
            error_when_create_canvas.exec()
        elif len(row) == 0:
            error_when_create_canvas = QMessageBox()
            error_when_create_canvas.setWindowTitle('Ошибка')
            error_when_create_canvas.setStandardButtons(QMessageBox.Close)
            error_when_create_canvas.setText('Вы не ввели номер строки для создания графика!')
            error_when_create_canvas.exec()
        else:
            self.demo = AppDemo(self.df_global, row, self.critical_temperature, self.items_for_canvas, self.deep)
            # self.demo = AppDemo(self.df_global, row, self.critical_temperature, self.items_for_canvas)
            self.demo.show()

    def open_guide(self):
        guide = QMessageBox()
        guide.setWindowTitle('Руководство')
        guide.setText(f'Программный продукт предназначен для автоматизации обработки результатов геотехнического мониторинга в криолитозоне.\n\n '
                      ' Для того, чтобы провести анализ температур, считанных термокосами, необходимо загрузить в программу файл с данными, записанными в логгер.\n '
                      ' После этого следует ввести контрольно значение температуры и нажать на кнопку "Анализ".\n\n'
                      ' Если номер строки в соотвествующем поле оставить пустым, то анализ будет произведен по всем данным.\n\n'
                      ' Если ввести номер строки - анализ осуществится только в заданной строке.'
                      ' Значения, превышающие контрольное значение температуры, будут выделены после анализа.\n\n'
                      ' При изменениях в полях ввода выделенные ячейки принимают первоначальный цвет.\n\n'
                      ' Для отображения графика необходимо провести анализ по выбранной строке, затем в строке меню нажать "График" -> "Создать"')
        guide.exec()

    # def cell_changed(self):
    #     nRows, nColumns = self.df_global.shape
    #     self.df_global.setColumnCount(nColumns)
    #     self.df_global.setRowCount(nRows)
    #     text = self.ui.tableWidget.item(nRows, nColumns).text().replace(',', '.')
    #     self.df_global.iloc[nRows, nColumns] = float(text)
    #     print(self.df_global)

    def save_file_as(self):
        if self.ui.tableWidget.columnCount() != 0:
            filter = "Excel файл (*.xlsx);;Текстовый файл (*.txt)"
            fname = QFileDialog.getSaveFileName(None, 'Сохранить как', '', filter)
            if fname == '':
                self.error_when_open.setWindowTitle('Ошибка')
                self.error_when_open.setStandardButtons(QMessageBox.Close)
                self.error_when_open.setText('Имя файла не введено')
                self.error_when_open.exec()
                return
            if 'Текстовый файл (*.txt)' in fname:
                np.savetxt(fname[0], self.df_global, fmt='%s', delimiter=';')
                self.ui.statusbar.showMessage('Файл успешно сохранен')
            else:
                self.df_global.to_excel(fname[0], header=False, index=False)
            self.ui.statusbar.showMessage('Файл успешно сохранен')
        else:
            self.error_when_open.setWindowTitle('Ошибка')
            self.error_when_open.setStyleSheet("QLabel{min-width: 120px;}")
            self.error_when_open.setStandardButtons(QMessageBox.Close)
            self.error_when_open.setText('Файл пуст')
            self.error_when_open.exec()
            return

    # def save_file(self):
    #     if self.df_global.empty is False:
    #         self.df_global.to_excel(self.file_name[0], header=False, index=False, engine='openpyxl')
    #         self.ui.statusbar.showMessage('Файл успешно сохранен')
    #         return
    #     else:
    #         self.error_when_open.setWindowTitle('Ошибка')
    #         self.error_when_open.setStandardButtons(QMessageBox.Close)
    #         self.error_when_open.setStyleSheet("QLabel{min-width: 120px;}");
    #         self.error_when_open.setText('Файл пуст')
    #         self.error_when_open.exec()
    #         return

    def about(self):
        about = QMessageBox()
        about.setWindowTitle('О программе')
        about.setText('Программу создал студент ИЭУИС 4-2 Мефедов Е.С. в рамкам выпускной квалификационной работы.')
        about.exec()

    def exit(self):
        sys.exit()

app = App()
