# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ds_documents.ui'
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
from PySide6.QtWidgets import (QApplication, QFrame, QHeaderView, QSizePolicy,
    QSplitter, QTreeWidget, QTreeWidgetItem, QVBoxLayout,
    QWidget)

class Ui_DSDocuments(object):
    def setupUi(self, DSDocuments):
        if not DSDocuments.objectName():
            DSDocuments.setObjectName(u"DSDocuments")
        DSDocuments.resize(700, 408)
        DSDocuments.setMinimumSize(QSize(700, 0))
        self.verticalLayout = QVBoxLayout(DSDocuments)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalSplitter = QSplitter(DSDocuments)
        self.horizontalSplitter.setObjectName(u"horizontalSplitter")
        self.horizontalSplitter.setOrientation(Qt.Orientation.Vertical)
        self.splitter = QSplitter(self.horizontalSplitter)
        self.splitter.setObjectName(u"splitter")
        self.splitter.setOrientation(Qt.Orientation.Horizontal)
        self.w_abstraction_tree_widget = QTreeWidget(self.splitter)
        self.w_abstraction_tree_widget.setObjectName(u"w_abstraction_tree_widget")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.w_abstraction_tree_widget.sizePolicy().hasHeightForWidth())
        self.w_abstraction_tree_widget.setSizePolicy(sizePolicy)
        self.w_abstraction_tree_widget.setAlternatingRowColors(True)
        self.splitter.addWidget(self.w_abstraction_tree_widget)
        self.w_key_tree_widget = QTreeWidget(self.splitter)
        self.w_key_tree_widget.setObjectName(u"w_key_tree_widget")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy1.setHorizontalStretch(1)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.w_key_tree_widget.sizePolicy().hasHeightForWidth())
        self.w_key_tree_widget.setSizePolicy(sizePolicy1)
        self.w_key_tree_widget.setAlternatingRowColors(True)
        self.splitter.addWidget(self.w_key_tree_widget)
        self.horizontalSplitter.addWidget(self.splitter)
        self.w_document_tree_widget = QTreeWidget(self.horizontalSplitter)
        self.w_document_tree_widget.setObjectName(u"w_document_tree_widget")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(1)
        sizePolicy2.setHeightForWidth(self.w_document_tree_widget.sizePolicy().hasHeightForWidth())
        self.w_document_tree_widget.setSizePolicy(sizePolicy2)
        self.w_document_tree_widget.setAlternatingRowColors(True)
        self.horizontalSplitter.addWidget(self.w_document_tree_widget)

        self.verticalLayout.addWidget(self.horizontalSplitter)


        self.retranslateUi(DSDocuments)

        QMetaObject.connectSlotsByName(DSDocuments)
    # setupUi

    def retranslateUi(self, DSDocuments):
        DSDocuments.setWindowTitle(QCoreApplication.translate("DSDocuments", u"Frame", None))
        ___qtreewidgetitem = self.w_abstraction_tree_widget.headerItem()
        ___qtreewidgetitem.setText(0, QCoreApplication.translate("DSDocuments", u"Abstraction", None));
        ___qtreewidgetitem1 = self.w_key_tree_widget.headerItem()
        ___qtreewidgetitem1.setText(1, QCoreApplication.translate("DSDocuments", u"Name", None));
        ___qtreewidgetitem1.setText(0, QCoreApplication.translate("DSDocuments", u"Key Instance ID", None));
        ___qtreewidgetitem2 = self.w_document_tree_widget.headerItem()
        ___qtreewidgetitem2.setText(3, QCoreApplication.translate("DSDocuments", u"Type", None));
        ___qtreewidgetitem2.setText(2, QCoreApplication.translate("DSDocuments", u"Path", None));
        ___qtreewidgetitem2.setText(1, QCoreApplication.translate("DSDocuments", u"Value", None));
        ___qtreewidgetitem2.setText(0, QCoreApplication.translate("DSDocuments", u"Component", None));
    # retranslateUi

