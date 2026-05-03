# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ds_commit_blobs.ui'
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
from PySide6.QtWidgets import (QApplication, QFrame, QGroupBox, QHBoxLayout,
    QHeaderView, QLabel, QSizePolicy, QSpacerItem,
    QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget)

class Ui_DSCommitBlobs(object):
    def setupUi(self, DSCommitBlobs):
        if not DSCommitBlobs.objectName():
            DSCommitBlobs.setObjectName(u"DSCommitBlobs")
        DSCommitBlobs.resize(781, 283)
        self.verticalLayout = QVBoxLayout(DSCommitBlobs)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.groupBox = QGroupBox(DSCommitBlobs)
        self.groupBox.setObjectName(u"groupBox")
        self.horizontalLayout = QHBoxLayout(self.groupBox)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label = QLabel(self.groupBox)
        self.label.setObjectName(u"label")

        self.horizontalLayout.addWidget(self.label)

        self.w_count_label = QLabel(self.groupBox)
        self.w_count_label.setObjectName(u"w_count_label")

        self.horizontalLayout.addWidget(self.w_count_label)

        self.horizontalSpacer = QSpacerItem(43, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.label_3 = QLabel(self.groupBox)
        self.label_3.setObjectName(u"label_3")

        self.horizontalLayout.addWidget(self.label_3)

        self.w_total_label = QLabel(self.groupBox)
        self.w_total_label.setObjectName(u"w_total_label")

        self.horizontalLayout.addWidget(self.w_total_label)

        self.label_5 = QLabel(self.groupBox)
        self.label_5.setObjectName(u"label_5")

        self.horizontalLayout.addWidget(self.label_5)

        self.w_min_label = QLabel(self.groupBox)
        self.w_min_label.setObjectName(u"w_min_label")

        self.horizontalLayout.addWidget(self.w_min_label)

        self.label_7 = QLabel(self.groupBox)
        self.label_7.setObjectName(u"label_7")

        self.horizontalLayout.addWidget(self.label_7)

        self.w_max_label = QLabel(self.groupBox)
        self.w_max_label.setObjectName(u"w_max_label")

        self.horizontalLayout.addWidget(self.w_max_label)


        self.verticalLayout.addWidget(self.groupBox)

        self.w_tree_widget = QTreeWidget(DSCommitBlobs)
        self.w_tree_widget.setObjectName(u"w_tree_widget")
        self.w_tree_widget.setSortingEnabled(True)

        self.verticalLayout.addWidget(self.w_tree_widget)


        self.retranslateUi(DSCommitBlobs)

        QMetaObject.connectSlotsByName(DSCommitBlobs)
    # setupUi

    def retranslateUi(self, DSCommitBlobs):
        DSCommitBlobs.setWindowTitle(QCoreApplication.translate("DSCommitBlobs", u"Frame", None))
        self.groupBox.setTitle(QCoreApplication.translate("DSCommitBlobs", u"Statistics", None))
        self.label.setText(QCoreApplication.translate("DSCommitBlobs", u"Count:", None))
        self.w_count_label.setText(QCoreApplication.translate("DSCommitBlobs", u"-", None))
        self.label_3.setText(QCoreApplication.translate("DSCommitBlobs", u"Total:", None))
        self.w_total_label.setText(QCoreApplication.translate("DSCommitBlobs", u"-", None))
        self.label_5.setText(QCoreApplication.translate("DSCommitBlobs", u"Min:", None))
        self.w_min_label.setText(QCoreApplication.translate("DSCommitBlobs", u"-", None))
        self.label_7.setText(QCoreApplication.translate("DSCommitBlobs", u"Max:", None))
        self.w_max_label.setText(QCoreApplication.translate("DSCommitBlobs", u"-", None))
        ___qtreewidgetitem = self.w_tree_widget.headerItem()
        ___qtreewidgetitem.setText(4, QCoreApplication.translate("DSCommitBlobs", u"RowId", None));
        ___qtreewidgetitem.setText(3, QCoreApplication.translate("DSCommitBlobs", u"Chunked", None));
        ___qtreewidgetitem.setText(2, QCoreApplication.translate("DSCommitBlobs", u"Size", None));
        ___qtreewidgetitem.setText(1, QCoreApplication.translate("DSCommitBlobs", u"Layout", None));
        ___qtreewidgetitem.setText(0, QCoreApplication.translate("DSCommitBlobs", u"BlobId", None));
    # retranslateUi

