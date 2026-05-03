# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ds_commit_sync_log.ui'
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
from PySide6.QtWidgets import (QApplication, QFrame, QHBoxLayout, QPushButton,
    QSizePolicy, QSpacerItem, QTextEdit, QVBoxLayout,
    QWidget)

class Ui_DSCommitSyncLog(object):
    def setupUi(self, DSCommitSyncLog):
        if not DSCommitSyncLog.objectName():
            DSCommitSyncLog.setObjectName(u"DSCommitSyncLog")
        DSCommitSyncLog.resize(624, 258)
        self.verticalLayout = QVBoxLayout(DSCommitSyncLog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.w_text_edit = QTextEdit(DSCommitSyncLog)
        self.w_text_edit.setObjectName(u"w_text_edit")
        self.w_text_edit.setMinimumSize(QSize(600, 0))
        self.w_text_edit.setUndoRedoEnabled(False)
        self.w_text_edit.setReadOnly(True)

        self.verticalLayout.addWidget(self.w_text_edit)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.w_clear_button = QPushButton(DSCommitSyncLog)
        self.w_clear_button.setObjectName(u"w_clear_button")

        self.horizontalLayout.addWidget(self.w_clear_button)


        self.verticalLayout.addLayout(self.horizontalLayout)


        self.retranslateUi(DSCommitSyncLog)

        QMetaObject.connectSlotsByName(DSCommitSyncLog)
    # setupUi

    def retranslateUi(self, DSCommitSyncLog):
        DSCommitSyncLog.setWindowTitle(QCoreApplication.translate("DSCommitSyncLog", u"Frame", None))
        self.w_clear_button.setText(QCoreApplication.translate("DSCommitSyncLog", u"Clear", None))
    # retranslateUi

