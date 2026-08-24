# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main.ui'
##
## Created by: Qt User Interface Compiler version 6.11.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QApplication, QLabel, QMainWindow, QMenu,
    QMenuBar, QPushButton, QScrollArea, QSizePolicy,
    QStatusBar, QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(390, 540)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        self.actionCreate_Backup = QAction(MainWindow)
        self.actionCreate_Backup.setObjectName(u"actionCreate_Backup")
        self.actionDriveAccount = QAction(MainWindow)
        self.actionDriveAccount.setObjectName(u"actionDriveAccount")
        self.actionHowtouse = QAction(MainWindow)
        self.actionHowtouse.setObjectName(u"actionHowtouse")
        self.actionGithub = QAction(MainWindow)
        self.actionGithub.setObjectName(u"actionGithub")
        self.actionDownload_Backup = QAction(MainWindow)
        self.actionDownload_Backup.setObjectName(u"actionDownload_Backup")
        self.actionDelete = QAction(MainWindow)
        self.actionDelete.setObjectName(u"actionDelete")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.foldersList = QScrollArea(self.centralwidget)
        self.foldersList.setObjectName(u"foldersList")
        self.foldersList.setGeometry(QRect(10, 30, 361, 181))
        self.foldersList.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 357, 177))
        self.verticalLayoutWidget = QWidget(self.scrollAreaWidgetContents)
        self.verticalLayoutWidget.setObjectName(u"verticalLayoutWidget")
        self.verticalLayoutWidget.setGeometry(QRect(0, 0, 361, 181))
        self.verticalLayout = QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.foldersList.setWidget(self.scrollAreaWidgetContents)
        self.label = QLabel(self.centralwidget)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(10, 10, 200, 16))
        self.label_2 = QLabel(self.centralwidget)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(10, 250, 200, 16))
        self.excludedList = QScrollArea(self.centralwidget)
        self.excludedList.setObjectName(u"excludedList")
        self.excludedList.setGeometry(QRect(10, 270, 361, 181))
        self.excludedList.setWidgetResizable(True)
        self.scrollAreaWidgetContents_2 = QWidget()
        self.scrollAreaWidgetContents_2.setObjectName(u"scrollAreaWidgetContents_2")
        self.scrollAreaWidgetContents_2.setGeometry(QRect(0, 0, 357, 177))
        self.verticalLayoutWidget_2 = QWidget(self.scrollAreaWidgetContents_2)
        self.verticalLayoutWidget_2.setObjectName(u"verticalLayoutWidget_2")
        self.verticalLayoutWidget_2.setGeometry(QRect(0, 0, 361, 181))
        self.verticalLayout_2 = QVBoxLayout(self.verticalLayoutWidget_2)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.excludedList.setWidget(self.scrollAreaWidgetContents_2)
        self.addFolder = QPushButton(self.centralwidget)
        self.addFolder.setObjectName(u"addFolder")
        self.addFolder.setGeometry(QRect(290, 220, 81, 26))
        self.addFolder.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.addExcluded = QPushButton(self.centralwidget)
        self.addExcluded.setObjectName(u"addExcluded")
        self.addExcluded.setGeometry(QRect(290, 460, 81, 26))
        self.addExcluded.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 390, 33))
        self.menuBackup = QMenu(self.menubar)
        self.menuBackup.setObjectName(u"menuBackup")
        self.menuHelp = QMenu(self.menubar)
        self.menuHelp.setObjectName(u"menuHelp")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menuBackup.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())
        self.menuBackup.addAction(self.actionCreate_Backup)
        self.menuBackup.addSeparator()
        self.menuBackup.addAction(self.actionDownload_Backup)
        self.menuBackup.addSeparator()
        self.menuBackup.addAction(self.actionDelete)
        self.menuHelp.addAction(self.actionHowtouse)
        self.menuHelp.addAction(self.actionGithub)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Cloud Backup", None))
        self.actionCreate_Backup.setText(QCoreApplication.translate("MainWindow", u"Subir", None))
        self.actionHowtouse.setText(QCoreApplication.translate("MainWindow", u"Cómo usar", None))
        self.actionGithub.setText(QCoreApplication.translate("MainWindow", u"Abrir Github", None))
        self.actionDownload_Backup.setText(QCoreApplication.translate("MainWindow", u"Descargar", None))
        self.actionDelete.setText(QCoreApplication.translate("MainWindow", u"Borrar", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"Carpetas incluidas en el backup:", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"Carpetas excluidas:", None))
        self.addFolder.setText(QCoreApplication.translate("MainWindow", u"Agregar", None))
        self.addExcluded.setText(QCoreApplication.translate("MainWindow", u"Agregar", None))
        self.menuBackup.setTitle(QCoreApplication.translate("MainWindow", u"Backup", None))
        self.menuHelp.setTitle(QCoreApplication.translate("MainWindow", u"Ayuda", None))
    # retranslateUi

