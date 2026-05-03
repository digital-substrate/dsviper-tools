# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ds_database_select_dialog.ui'
##
## Created by: Qt User Interface Compiler version 6.10.1
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
from PySide6.QtWidgets import (QApplication, QDialog, QGroupBox, QHBoxLayout,
    QListWidget, QListWidgetItem, QPushButton, QSizePolicy,
    QSpacerItem, QVBoxLayout, QWidget)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(286, 263)
        self.verticalLayout_2 = QVBoxLayout(Dialog)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.groupBox = QGroupBox(Dialog)
        self.groupBox.setObjectName(u"groupBox")
        self.verticalLayout = QVBoxLayout(self.groupBox)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.w_databases_list_widget = QListWidget(self.groupBox)
        self.w_databases_list_widget.setObjectName(u"w_databases_list_widget")

        self.verticalLayout.addWidget(self.w_databases_list_widget)


        self.verticalLayout_2.addWidget(self.groupBox)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.w_cancel_button = QPushButton(Dialog)
        self.w_cancel_button.setObjectName(u"w_cancel_button")

        self.horizontalLayout.addWidget(self.w_cancel_button)

        self.w_ok_button = QPushButton(Dialog)
        self.w_ok_button.setObjectName(u"w_ok_button")
        self.w_ok_button.setAutoDefault(False)

        self.horizontalLayout.addWidget(self.w_ok_button)


        self.verticalLayout_2.addLayout(self.horizontalLayout)


        self.retranslateUi(Dialog)

        self.w_ok_button.setDefault(True)


        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Select Database", None))
        self.groupBox.setTitle(QCoreApplication.translate("Dialog", u"Databases", None))
        self.w_cancel_button.setText(QCoreApplication.translate("Dialog", u"Cancel", None))
        self.w_ok_button.setText(QCoreApplication.translate("Dialog", u"Select", None))
    # retranslateUi

