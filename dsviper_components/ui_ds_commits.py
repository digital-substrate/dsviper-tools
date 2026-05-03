# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ds_commits.ui'
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
from PySide6.QtWidgets import (QApplication, QFrame, QGridLayout, QGroupBox,
    QHBoxLayout, QLabel, QPushButton, QScrollArea,
    QSizePolicy, QSpacerItem, QToolButton, QVBoxLayout,
    QWidget)

class Ui_DSCommits(object):
    def setupUi(self, DSCommits):
        if not DSCommits.objectName():
            DSCommits.setObjectName(u"DSCommits")
        DSCommits.resize(475, 761)
        self.verticalLayout = QVBoxLayout(DSCommits)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.w_delete_button = QPushButton(DSCommits)
        self.w_delete_button.setObjectName(u"w_delete_button")

        self.horizontalLayout.addWidget(self.w_delete_button)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.w_reset_button = QPushButton(DSCommits)
        self.w_reset_button.setObjectName(u"w_reset_button")

        self.horizontalLayout.addWidget(self.w_reset_button)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.scrollarea = QScrollArea(DSCommits)
        self.scrollarea.setObjectName(u"scrollarea")
        self.scrollarea.setMinimumSize(QSize(0, 200))
        self.scrollarea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 449, 261))
        self.scrollarea.setWidget(self.scrollAreaWidgetContents)

        self.verticalLayout.addWidget(self.scrollarea)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.w_merge_button = QPushButton(DSCommits)
        self.w_merge_button.setObjectName(u"w_merge_button")

        self.horizontalLayout_2.addWidget(self.w_merge_button)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_2)

        self.w_enable_button = QPushButton(DSCommits)
        self.w_enable_button.setObjectName(u"w_enable_button")

        self.horizontalLayout_2.addWidget(self.w_enable_button)

        self.w_disable_button = QPushButton(DSCommits)
        self.w_disable_button.setObjectName(u"w_disable_button")

        self.horizontalLayout_2.addWidget(self.w_disable_button)


        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.groupBox = QGroupBox(DSCommits)
        self.groupBox.setObjectName(u"groupBox")
        self.gridLayout = QGridLayout(self.groupBox)
        self.gridLayout.setObjectName(u"gridLayout")
        self.label_9 = QLabel(self.groupBox)
        self.label_9.setObjectName(u"label_9")
        self.label_9.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.gridLayout.addWidget(self.label_9, 4, 0, 1, 1)

        self.label_7 = QLabel(self.groupBox)
        self.label_7.setObjectName(u"label_7")
        self.label_7.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.gridLayout.addWidget(self.label_7, 2, 0, 1, 1)

        self.w_current_label_label = QLabel(self.groupBox)
        self.w_current_label_label.setObjectName(u"w_current_label_label")

        self.gridLayout.addWidget(self.w_current_label_label, 4, 1, 1, 1)

        self.w_current_parent_id_label = QLabel(self.groupBox)
        self.w_current_parent_id_label.setObjectName(u"w_current_parent_id_label")

        self.gridLayout.addWidget(self.w_current_parent_id_label, 1, 1, 1, 1)

        self.w_current_parent_id_button = QToolButton(self.groupBox)
        self.w_current_parent_id_button.setObjectName(u"w_current_parent_id_button")
        self.w_current_parent_id_button.setMaximumSize(QSize(16, 16))
        icon = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.EditCopy))
        self.w_current_parent_id_button.setIcon(icon)

        self.gridLayout.addWidget(self.w_current_parent_id_button, 1, 2, 1, 1)

        self.w_current_type_label = QLabel(self.groupBox)
        self.w_current_type_label.setObjectName(u"w_current_type_label")

        self.gridLayout.addWidget(self.w_current_type_label, 2, 1, 1, 1)

        self.label_3 = QLabel(self.groupBox)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.gridLayout.addWidget(self.label_3, 1, 0, 1, 1)

        self.w_current_date_label = QLabel(self.groupBox)
        self.w_current_date_label.setObjectName(u"w_current_date_label")

        self.gridLayout.addWidget(self.w_current_date_label, 5, 1, 1, 1)

        self.w_current_id_button = QToolButton(self.groupBox)
        self.w_current_id_button.setObjectName(u"w_current_id_button")
        self.w_current_id_button.setMaximumSize(QSize(16, 16))
        self.w_current_id_button.setIcon(icon)

        self.gridLayout.addWidget(self.w_current_id_button, 0, 2, 1, 1)

        self.w_current_id_label = QLabel(self.groupBox)
        self.w_current_id_label.setObjectName(u"w_current_id_label")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.w_current_id_label.sizePolicy().hasHeightForWidth())
        self.w_current_id_label.setSizePolicy(sizePolicy)

        self.gridLayout.addWidget(self.w_current_id_label, 0, 1, 1, 1)

        self.label_11 = QLabel(self.groupBox)
        self.label_11.setObjectName(u"label_11")
        self.label_11.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.gridLayout.addWidget(self.label_11, 5, 0, 1, 1)

        self.w_current_target_id_button = QToolButton(self.groupBox)
        self.w_current_target_id_button.setObjectName(u"w_current_target_id_button")
        self.w_current_target_id_button.setMaximumSize(QSize(16, 16))
        self.w_current_target_id_button.setIcon(icon)

        self.gridLayout.addWidget(self.w_current_target_id_button, 3, 2, 1, 1)

        self.w_current_target_id_label = QLabel(self.groupBox)
        self.w_current_target_id_label.setObjectName(u"w_current_target_id_label")

        self.gridLayout.addWidget(self.w_current_target_id_label, 3, 1, 1, 1)

        self.label = QLabel(self.groupBox)
        self.label.setObjectName(u"label")
        self.label.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)

        self.label_25 = QLabel(self.groupBox)
        self.label_25.setObjectName(u"label_25")
        self.label_25.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.gridLayout.addWidget(self.label_25, 3, 0, 1, 1)


        self.verticalLayout.addWidget(self.groupBox)

        self.groupBox_2 = QGroupBox(DSCommits)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.gridLayout_2 = QGridLayout(self.groupBox_2)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.w_marked_id_label = QLabel(self.groupBox_2)
        self.w_marked_id_label.setObjectName(u"w_marked_id_label")
        sizePolicy.setHeightForWidth(self.w_marked_id_label.sizePolicy().hasHeightForWidth())
        self.w_marked_id_label.setSizePolicy(sizePolicy)

        self.gridLayout_2.addWidget(self.w_marked_id_label, 0, 1, 1, 1)

        self.label_23 = QLabel(self.groupBox_2)
        self.label_23.setObjectName(u"label_23")
        self.label_23.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.gridLayout_2.addWidget(self.label_23, 5, 0, 1, 1)

        self.w_marked_parent_id_button = QToolButton(self.groupBox_2)
        self.w_marked_parent_id_button.setObjectName(u"w_marked_parent_id_button")
        self.w_marked_parent_id_button.setMaximumSize(QSize(16, 16))
        self.w_marked_parent_id_button.setIcon(icon)

        self.gridLayout_2.addWidget(self.w_marked_parent_id_button, 1, 2, 1, 1)

        self.w_marked_parent_id_label = QLabel(self.groupBox_2)
        self.w_marked_parent_id_label.setObjectName(u"w_marked_parent_id_label")

        self.gridLayout_2.addWidget(self.w_marked_parent_id_label, 1, 1, 1, 1)

        self.w_marked_date_label = QLabel(self.groupBox_2)
        self.w_marked_date_label.setObjectName(u"w_marked_date_label")

        self.gridLayout_2.addWidget(self.w_marked_date_label, 5, 1, 1, 1)

        self.w_marked_label_label = QLabel(self.groupBox_2)
        self.w_marked_label_label.setObjectName(u"w_marked_label_label")

        self.gridLayout_2.addWidget(self.w_marked_label_label, 4, 1, 1, 1)

        self.w_marked_id_button = QToolButton(self.groupBox_2)
        self.w_marked_id_button.setObjectName(u"w_marked_id_button")
        self.w_marked_id_button.setMaximumSize(QSize(16, 16))
        self.w_marked_id_button.setIcon(icon)

        self.gridLayout_2.addWidget(self.w_marked_id_button, 0, 2, 1, 1)

        self.label_27 = QLabel(self.groupBox_2)
        self.label_27.setObjectName(u"label_27")
        self.label_27.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.gridLayout_2.addWidget(self.label_27, 3, 0, 1, 1)

        self.label_19 = QLabel(self.groupBox_2)
        self.label_19.setObjectName(u"label_19")
        self.label_19.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.gridLayout_2.addWidget(self.label_19, 2, 0, 1, 1)

        self.label_21 = QLabel(self.groupBox_2)
        self.label_21.setObjectName(u"label_21")
        self.label_21.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.gridLayout_2.addWidget(self.label_21, 4, 0, 1, 1)

        self.label_15 = QLabel(self.groupBox_2)
        self.label_15.setObjectName(u"label_15")
        self.label_15.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.gridLayout_2.addWidget(self.label_15, 1, 0, 1, 1)

        self.w_marked_target_id_button = QToolButton(self.groupBox_2)
        self.w_marked_target_id_button.setObjectName(u"w_marked_target_id_button")
        self.w_marked_target_id_button.setMaximumSize(QSize(16, 16))
        self.w_marked_target_id_button.setIcon(icon)

        self.gridLayout_2.addWidget(self.w_marked_target_id_button, 3, 2, 1, 1)

        self.label_13 = QLabel(self.groupBox_2)
        self.label_13.setObjectName(u"label_13")
        self.label_13.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.gridLayout_2.addWidget(self.label_13, 0, 0, 1, 1)

        self.w_marked_type_label = QLabel(self.groupBox_2)
        self.w_marked_type_label.setObjectName(u"w_marked_type_label")

        self.gridLayout_2.addWidget(self.w_marked_type_label, 2, 1, 1, 1)

        self.w_marked_target_id_label = QLabel(self.groupBox_2)
        self.w_marked_target_id_label.setObjectName(u"w_marked_target_id_label")

        self.gridLayout_2.addWidget(self.w_marked_target_id_label, 3, 1, 1, 1)


        self.verticalLayout.addWidget(self.groupBox_2)


        self.retranslateUi(DSCommits)

        QMetaObject.connectSlotsByName(DSCommits)
    # setupUi

    def retranslateUi(self, DSCommits):
        DSCommits.setWindowTitle(QCoreApplication.translate("DSCommits", u"Frame", None))
        self.w_delete_button.setText(QCoreApplication.translate("DSCommits", u"Delete", None))
        self.w_reset_button.setText(QCoreApplication.translate("DSCommits", u"Reset", None))
        self.w_merge_button.setText(QCoreApplication.translate("DSCommits", u"Merge", None))
        self.w_enable_button.setText(QCoreApplication.translate("DSCommits", u"Enable", None))
        self.w_disable_button.setText(QCoreApplication.translate("DSCommits", u"Disable", None))
        self.groupBox.setTitle(QCoreApplication.translate("DSCommits", u"Selected Commit", None))
        self.label_9.setText(QCoreApplication.translate("DSCommits", u"Label:", None))
        self.label_7.setText(QCoreApplication.translate("DSCommits", u"Type:", None))
        self.w_current_label_label.setText(QCoreApplication.translate("DSCommits", u"-", None))
        self.w_current_parent_id_label.setText(QCoreApplication.translate("DSCommits", u"0000000000000000000000000000000000000000", None))
        self.w_current_parent_id_button.setText(QCoreApplication.translate("DSCommits", u"...", None))
        self.w_current_type_label.setText(QCoreApplication.translate("DSCommits", u"-", None))
        self.label_3.setText(QCoreApplication.translate("DSCommits", u"Parent:", None))
        self.w_current_date_label.setText(QCoreApplication.translate("DSCommits", u"-", None))
        self.w_current_id_button.setText(QCoreApplication.translate("DSCommits", u"...", None))
        self.w_current_id_label.setText(QCoreApplication.translate("DSCommits", u"0000000000000000000000000000000000000000", None))
        self.label_11.setText(QCoreApplication.translate("DSCommits", u"Date:", None))
        self.w_current_target_id_button.setText(QCoreApplication.translate("DSCommits", u"...", None))
        self.w_current_target_id_label.setText(QCoreApplication.translate("DSCommits", u"0000000000000000000000000000000000000000", None))
        self.label.setText(QCoreApplication.translate("DSCommits", u"Commit:", None))
        self.label_25.setText(QCoreApplication.translate("DSCommits", u"Target:", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("DSCommits", u"Marked Commit", None))
        self.w_marked_id_label.setText(QCoreApplication.translate("DSCommits", u"0000000000000000000000000000000000000000", None))
        self.label_23.setText(QCoreApplication.translate("DSCommits", u"Date:", None))
        self.w_marked_parent_id_button.setText(QCoreApplication.translate("DSCommits", u"...", None))
        self.w_marked_parent_id_label.setText(QCoreApplication.translate("DSCommits", u"0000000000000000000000000000000000000000", None))
        self.w_marked_date_label.setText(QCoreApplication.translate("DSCommits", u"-", None))
        self.w_marked_label_label.setText(QCoreApplication.translate("DSCommits", u"-", None))
        self.w_marked_id_button.setText(QCoreApplication.translate("DSCommits", u"...", None))
        self.label_27.setText(QCoreApplication.translate("DSCommits", u"Target:", None))
        self.label_19.setText(QCoreApplication.translate("DSCommits", u"Type:", None))
        self.label_21.setText(QCoreApplication.translate("DSCommits", u"Label:", None))
        self.label_15.setText(QCoreApplication.translate("DSCommits", u"Parent:", None))
        self.w_marked_target_id_button.setText(QCoreApplication.translate("DSCommits", u"...", None))
        self.label_13.setText(QCoreApplication.translate("DSCommits", u"Commit:", None))
        self.w_marked_type_label.setText(QCoreApplication.translate("DSCommits", u"-", None))
        self.w_marked_target_id_label.setText(QCoreApplication.translate("DSCommits", u"0000000000000000000000000000000000000000", None))
    # retranslateUi

