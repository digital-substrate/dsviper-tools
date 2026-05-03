# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ds_commit_undo.ui'
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
from PySide6.QtWidgets import (QApplication, QFrame, QListWidget, QListWidgetItem,
    QSizePolicy, QVBoxLayout, QWidget)

class Ui_DSCommitUndo(object):
    def setupUi(self, DSCommitUndo):
        if not DSCommitUndo.objectName():
            DSCommitUndo.setObjectName(u"DSCommitUndo")
        DSCommitUndo.resize(331, 322)
        self.verticalLayout = QVBoxLayout(DSCommitUndo)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.w_list_widget = QListWidget(DSCommitUndo)
        self.w_list_widget.setObjectName(u"w_list_widget")
        self.w_list_widget.setAlternatingRowColors(True)

        self.verticalLayout.addWidget(self.w_list_widget)


        self.retranslateUi(DSCommitUndo)

        QMetaObject.connectSlotsByName(DSCommitUndo)
    # setupUi

    def retranslateUi(self, DSCommitUndo):
        DSCommitUndo.setWindowTitle(QCoreApplication.translate("DSCommitUndo", u"Frame", None))
    # retranslateUi

