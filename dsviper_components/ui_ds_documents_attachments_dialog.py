# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ds_documents_attachments_dialog.ui'
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
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QDialog, QGridLayout,
    QHBoxLayout, QHeaderView, QLineEdit, QPushButton,
    QSizePolicy, QSpacerItem, QToolButton, QTreeWidget,
    QTreeWidgetItem, QWidget)

class Ui_DSDocumentsAttachmentsDialog(object):
    def setupUi(self, DSDocumentsAttachmentsDialog):
        if not DSDocumentsAttachmentsDialog.objectName():
            DSDocumentsAttachmentsDialog.setObjectName(u"DSDocumentsAttachmentsDialog")
        DSDocumentsAttachmentsDialog.resize(348, 300)
        self.gridLayout = QGridLayout(DSDocumentsAttachmentsDialog)
        self.gridLayout.setObjectName(u"gridLayout")
        self.w_instance_line_edit = QLineEdit(DSDocumentsAttachmentsDialog)
        self.w_instance_line_edit.setObjectName(u"w_instance_line_edit")

        self.gridLayout.addWidget(self.w_instance_line_edit, 0, 0, 1, 1)

        self.w_generate_button = QToolButton(DSDocumentsAttachmentsDialog)
        self.w_generate_button.setObjectName(u"w_generate_button")

        self.gridLayout.addWidget(self.w_generate_button, 0, 1, 1, 1)

        self.w_tree_widget = QTreeWidget(DSDocumentsAttachmentsDialog)
        self.w_tree_widget.setObjectName(u"w_tree_widget")
        self.w_tree_widget.setAlternatingRowColors(True)
        self.w_tree_widget.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)

        self.gridLayout.addWidget(self.w_tree_widget, 1, 0, 1, 2)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.w_cancel_button = QPushButton(DSDocumentsAttachmentsDialog)
        self.w_cancel_button.setObjectName(u"w_cancel_button")
        self.w_cancel_button.setAutoDefault(False)

        self.horizontalLayout.addWidget(self.w_cancel_button)

        self.w_create_button = QPushButton(DSDocumentsAttachmentsDialog)
        self.w_create_button.setObjectName(u"w_create_button")
        self.w_create_button.setAutoDefault(False)

        self.horizontalLayout.addWidget(self.w_create_button)


        self.gridLayout.addLayout(self.horizontalLayout, 2, 0, 1, 2)


        self.retranslateUi(DSDocumentsAttachmentsDialog)

        QMetaObject.connectSlotsByName(DSDocumentsAttachmentsDialog)
    # setupUi

    def retranslateUi(self, DSDocumentsAttachmentsDialog):
        DSDocumentsAttachmentsDialog.setWindowTitle(QCoreApplication.translate("DSDocumentsAttachmentsDialog", u"Dialog", None))
        self.w_instance_line_edit.setText(QCoreApplication.translate("DSDocumentsAttachmentsDialog", u"00000000-0000-0000-0000-000000000000", None))
        self.w_generate_button.setText(QCoreApplication.translate("DSDocumentsAttachmentsDialog", u"...", None))
        ___qtreewidgetitem = self.w_tree_widget.headerItem()
        ___qtreewidgetitem.setText(0, QCoreApplication.translate("DSDocumentsAttachmentsDialog", u"Attachments", None));
        self.w_cancel_button.setText(QCoreApplication.translate("DSDocumentsAttachmentsDialog", u"Cancel", None))
        self.w_create_button.setText(QCoreApplication.translate("DSDocumentsAttachmentsDialog", u"Create", None))
    # retranslateUi

