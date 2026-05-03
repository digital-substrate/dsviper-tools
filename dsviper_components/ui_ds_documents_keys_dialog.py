# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ds_documents_keys_dialog.ui'
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
from PySide6.QtWidgets import (QApplication, QDialog, QHBoxLayout, QHeaderView,
    QPushButton, QSizePolicy, QSpacerItem, QTreeWidget,
    QTreeWidgetItem, QVBoxLayout, QWidget)

class Ui_DSDocumentsKeysDialog(object):
    def setupUi(self, DSDocumentsKeysDialog):
        if not DSDocumentsKeysDialog.objectName():
            DSDocumentsKeysDialog.setObjectName(u"DSDocumentsKeysDialog")
        DSDocumentsKeysDialog.resize(519, 257)
        self.verticalLayout = QVBoxLayout(DSDocumentsKeysDialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.w_tree_widget = QTreeWidget(DSDocumentsKeysDialog)
        self.w_tree_widget.setObjectName(u"w_tree_widget")
        self.w_tree_widget.setAlternatingRowColors(True)

        self.verticalLayout.addWidget(self.w_tree_widget)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.w_cancel_button = QPushButton(DSDocumentsKeysDialog)
        self.w_cancel_button.setObjectName(u"w_cancel_button")
        self.w_cancel_button.setMinimumSize(QSize(70, 0))
        self.w_cancel_button.setAutoDefault(False)

        self.horizontalLayout.addWidget(self.w_cancel_button)

        self.w_ok_button = QPushButton(DSDocumentsKeysDialog)
        self.w_ok_button.setObjectName(u"w_ok_button")
        self.w_ok_button.setMinimumSize(QSize(70, 0))
        self.w_ok_button.setAutoDefault(False)

        self.horizontalLayout.addWidget(self.w_ok_button)


        self.verticalLayout.addLayout(self.horizontalLayout)


        self.retranslateUi(DSDocumentsKeysDialog)

        QMetaObject.connectSlotsByName(DSDocumentsKeysDialog)
    # setupUi

    def retranslateUi(self, DSDocumentsKeysDialog):
        DSDocumentsKeysDialog.setWindowTitle(QCoreApplication.translate("DSDocumentsKeysDialog", u"Dialog", None))
        ___qtreewidgetitem = self.w_tree_widget.headerItem()
        ___qtreewidgetitem.setText(1, QCoreApplication.translate("DSDocumentsKeysDialog", u"Name", None));
        ___qtreewidgetitem.setText(0, QCoreApplication.translate("DSDocumentsKeysDialog", u"Key Instance ID", None));
        self.w_cancel_button.setText(QCoreApplication.translate("DSDocumentsKeysDialog", u"Cancel", None))
        self.w_ok_button.setText(QCoreApplication.translate("DSDocumentsKeysDialog", u"Ok", None))
    # retranslateUi

