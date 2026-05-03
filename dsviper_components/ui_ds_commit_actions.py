# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ds_commit_actions.ui'
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
from PySide6.QtWidgets import (QApplication, QFrame, QLabel, QListWidget,
    QListWidgetItem, QSizePolicy, QVBoxLayout, QWidget)

class Ui_DSCommitActions(object):
    def setupUi(self, DSCommitActions):
        if not DSCommitActions.objectName():
            DSCommitActions.setObjectName(u"DSCommitActions")
        DSCommitActions.resize(227, 453)
        self.verticalLayout = QVBoxLayout(DSCommitActions)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.w_label = QLabel(DSCommitActions)
        self.w_label.setObjectName(u"w_label")
        font = QFont()
        font.setBold(True)
        self.w_label.setFont(font)

        self.verticalLayout.addWidget(self.w_label)

        self.w_list_widget = QListWidget(DSCommitActions)
        self.w_list_widget.setObjectName(u"w_list_widget")
        self.w_list_widget.setAlternatingRowColors(True)
        self.w_list_widget.setIconSize(QSize(13, 8))

        self.verticalLayout.addWidget(self.w_list_widget)


        self.retranslateUi(DSCommitActions)

        QMetaObject.connectSlotsByName(DSCommitActions)
    # setupUi

    def retranslateUi(self, DSCommitActions):
        DSCommitActions.setWindowTitle(QCoreApplication.translate("DSCommitActions", u"Frame", None))
        self.w_label.setText(QCoreApplication.translate("DSCommitActions", u"Actions", None))
    # retranslateUi

