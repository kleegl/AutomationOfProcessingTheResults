from pulp import *
from PySide2.QtGui import (QColor)
from PySide2.QtWidgets import *

from CourseY.mainwindow import Ui_MainWindow
import re
import sys
import pandas as pd
#pyside2-uic mainwindow.ui -o mainwindow.py
# app init

class App:
    def __init__(self):
        # super().__init__()
        self.app = QApplication(sys.argv)

        Form = QMainWindow()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(Form)

        self.ui.action.triggered.connect(self.fillDF)
        self.ui.action_2.triggered.connect(self.saveExcel)
        self.ui.action_3.triggered.connect(self.clearTable)
        self.ui.action_4.triggered.connect(self.aboutAutor)
        self.ui.action_5.triggered.connect(self.aboutProg)
        self.ui.pushButton.clicked.connect(self.solve)
        Form.show()
        sys.exit(self.app.exec_())


    def fillDF(self):
        fname = QFileDialog.getOpenFileName()
        if fname == '':
            self.error('Файл не выбран')
            return
        try:
            xl = pd.ExcelFile(fname[0])
        except:
            self.error('Неверный файл')
            return
        try:
            self.df1 = xl.parse('План раскроя',index_col=0)
            self.ui.tableWidget.setDF(self.df1)
            self.df2 = xl.parse('Требования',index_col=0)
            self.ui.tableWidget_2.setDF(self.df2)
            self.ui.tableWidget_2.setVerticalHeaderLabels(['Требуется бруса'])
        except:
            self.error('Файл не выбран')
            return

    def clearTable(self):
        self.ui.tableWidget.clearContents()
        self.ui.tableWidget_2.clearContents()
        self.ui.tableWidget_3.clearContents()

    def aboutProg(self):
        mbox = QMessageBox()
        mbox.setText('Программа разработана для решения задачи раскроя')
        mbox.setWindowTitle('Информация')
        mbox.setStandardButtons(QMessageBox.Ok)
        mbox.exec_()

    def aboutAutor(self):
        mbox = QMessageBox()
        mbox.setText('Ященко Никита ИЭУИС III-4')
        mbox.setWindowTitle('Автор: ')
        mbox.setStandardButtons(QMessageBox.Ok)
        mbox.exec_()

    def solve(self):
        typeMass = self.df1.columns.tolist()[:-1]
        print('TypeMass:')
        print(typeMass)

        cutDict = {i: {j: self.df1[j][i] for j in typeMass} for i in self.df1.index}
        print('CutDictKeys')
        print(cutDict)

        overageDict = {i: self.df1['Остаток'][i] for i in cutDict.keys()}
        print('overageDict')
        print(overageDict)

        reqDict = {i: self.df2[i][0] for i in typeMass}
        print('reqDict')
        print(reqDict)


        problem = LpProblem("Profit", LpMinimize)

        variables = LpVariable.dicts("Раскрой№", cutDict.keys(), 0, cat=LpInteger)

        problem += lpSum(variables[i] * overageDict[i] for i in cutDict.keys())

        for i in typeMass:
            problem += lpSum(variables[j] * cutDict[j][i] for j in cutDict.keys()) == reqDict[i]

        status = problem.solve()
        print("План:")
        varMass = []
        varNames = []
        varDict = {}
        for variable in problem.variables():
            print(variable.name, "=", variable.varValue)
            varNames.append(variable.name)
            varDict[int(re.findall('\d+',variable.name)[0])] = variable.varValue
        print(varDict)

        for i in sorted(varDict.keys()):
            varMass.append(varDict[i])

        print(varMass)
        self.df3 = pd.DataFrame.from_dict(columns=varNames,data={1:varMass},orient='index')
        self.df3.rename(columns=lambda x:  int(re.findall('\d+',x)[0]), inplace=True)
        self.df3.columns = sorted(self.df3.columns)
        cols = [str(i) for i in self.df3.columns]
        print(self.df3)
        self.ui.tableWidget_3.setDF(self.df3)
        self.ui.tableWidget_3.setHorizontalHeaderLabels(cols)
        print("Суммарный остаток: ")
        print(value(problem.objective))
        self.ui.label_5.setText(str(value(problem.objective)))

    def error(self,message):
        mbox = QMessageBox()
        mbox.setText(message)
        mbox.setWindowTitle('Ошибка')
        mbox.setStandardButtons(QMessageBox.Ok)
        mbox.exec_()

    def saveExcel(self):
        if self.ui.tableWidget_3.columnCount() != 0:
            try:
                fname = QFileDialog.getSaveFileName()
                if fname == '':
                    self.error('Файл не выбран')
                    return
                self.df3.to_excel(fname[0])
            except AttributeError:
                self.error('Итоговая таблица пуста')
                return
        else:
            self.error('Итоговая таблица пуста')
            return


app = App()





