# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'primer.ui'
##
## Created by: Qt User Interface Compiler version 6.12.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QGroupBox, QLabel, QMainWindow,
    QMenuBar, QPushButton, QSizePolicy, QStatusBar,
    QTextEdit, QWidget)

class Ui_MainWindow(object):

    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(800, 535)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.widget = QWidget(self.centralwidget)
        self.widget.setObjectName(u"widget")
        self.widget.setGeometry(QRect(120, 140, 581, 401))
        font = QFont()
        font.setBold(True)
        self.widget.setFont(font)
        self.widget.setStyleSheet(u"background-color: rgb(0, 0, 0);\n"
"background-color: rgb(145, 65, 172);")
        self.groupBox = QGroupBox(self.centralwidget)
        self.groupBox.setObjectName(u"groupBox")
        self.groupBox.setGeometry(QRect(120, 10, 581, 121))
        self.groupBox.setStyleSheet(u"QGroupBox {\n"
"	background-color: rgb(87, 227, 137);\n"
"    border: 1px solid #40E0D0; /* Color verde agua */\n"
"    border-radius: 0px;        /* Sin espacio entre 0 y px */\n"
"    margin-top: 12px;\n"
"    padding-top: 10px;         /* Corregido: era padding, no passing */\n"
"}")
        self.label = QLabel(self.groupBox)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(80, 20, 91, 21))
        font1 = QFont()
        font1.setPointSize(13)
        font1.setBold(True)
        self.label.setFont(font1)
        self.label_2 = QLabel(self.groupBox)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(390, 20, 121, 21))
        self.label_2.setFont(font1)
        self.textEdit = QTextEdit(self.groupBox)
        self.textEdit.setObjectName(u"textEdit")
        self.textEdit.setGeometry(QRect(50, 40, 141, 31))
        self.textEdit.setStyleSheet(u"background-color: rgb(220, 138, 221);")
        self.textEdit_2 = QTextEdit(self.groupBox)
        self.textEdit_2.setObjectName(u"textEdit_2")
        self.textEdit_2.setGeometry(QRect(380, 40, 141, 31))
        self.textEdit_2.setStyleSheet(u"background-color: rgb(220, 138, 221);")
        self.pushButton_Actualizar = QPushButton(self.groupBox)
        self.pushButton_Actualizar.setObjectName(u"pushButton_Actualizar")
        self.pushButton_Actualizar.setGeometry(QRect(80, 80, 411, 31))
        font2 = QFont()
        font2.setFamilies([u"Noto Sans Adlam"])
        font2.setPointSize(12)
        font2.setBold(True)
        font2.setItalic(True)
        self.pushButton_Actualizar.setFont(font2)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 800, 22))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.groupBox.setTitle(QCoreApplication.translate("MainWindow", u"Parametros de la se\u00f1al", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"Amplitud", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"Frecuencia [hz]", None))
        self.pushButton_Actualizar.setText(QCoreApplication.translate("MainWindow", u"Actualzador grafico", None))
    # retranslateUi




