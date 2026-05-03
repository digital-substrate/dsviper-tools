# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ds_commit_program.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QFrame, QGridLayout,
    QGroupBox, QHBoxLayout, QHeaderView, QLabel,
    QSizePolicy, QSpacerItem, QSplitter, QTextEdit,
    QToolButton, QTreeWidget, QTreeWidgetItem, QVBoxLayout,
    QWidget)

class Ui_DSCommitProgram(object):
    def setupUi(self, DSCommitProgram):
        if not DSCommitProgram.objectName():
            DSCommitProgram.setObjectName(u"DSCommitProgram")
        DSCommitProgram.resize(848, 491)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(DSCommitProgram.sizePolicy().hasHeightForWidth())
        DSCommitProgram.setSizePolicy(sizePolicy)
        self.verticalLayout = QVBoxLayout(DSCommitProgram)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.groupBox = QGroupBox(DSCommitProgram)
        self.groupBox.setObjectName(u"groupBox")
        self.gridLayout = QGridLayout(self.groupBox)
        self.gridLayout.setObjectName(u"gridLayout")
        self.label = QLabel(self.groupBox)
        self.label.setObjectName(u"label")
        self.label.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)

        self.w_label_label = QLabel(self.groupBox)
        self.w_label_label.setObjectName(u"w_label_label")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.w_label_label.sizePolicy().hasHeightForWidth())
        self.w_label_label.setSizePolicy(sizePolicy1)

        self.gridLayout.addWidget(self.w_label_label, 0, 1, 1, 5)

        self.label_3 = QLabel(self.groupBox)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.gridLayout.addWidget(self.label_3, 1, 0, 1, 1)

        self.w_date_label = QLabel(self.groupBox)
        self.w_date_label.setObjectName(u"w_date_label")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        sizePolicy2.setHorizontalStretch(10)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.w_date_label.sizePolicy().hasHeightForWidth())
        self.w_date_label.setSizePolicy(sizePolicy2)

        self.gridLayout.addWidget(self.w_date_label, 1, 1, 1, 1)

        self.horizontalSpacer_2 = QSpacerItem(3, 3, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer_2, 1, 2, 1, 1)

        self.label_5 = QLabel(self.groupBox)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.gridLayout.addWidget(self.label_5, 1, 3, 1, 1)

        self.w_commit_id_label = QLabel(self.groupBox)
        self.w_commit_id_label.setObjectName(u"w_commit_id_label")
        sizePolicy.setHeightForWidth(self.w_commit_id_label.sizePolicy().hasHeightForWidth())
        self.w_commit_id_label.setSizePolicy(sizePolicy)

        self.gridLayout.addWidget(self.w_commit_id_label, 1, 4, 1, 1)

        self.w_commit_id_copy_button = QToolButton(self.groupBox)
        self.w_commit_id_copy_button.setObjectName(u"w_commit_id_copy_button")
        self.w_commit_id_copy_button.setMaximumSize(QSize(13, 13))
        icon = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.EditCopy))
        self.w_commit_id_copy_button.setIcon(icon)

        self.gridLayout.addWidget(self.w_commit_id_copy_button, 1, 5, 1, 1)

        self.label_9 = QLabel(self.groupBox)
        self.label_9.setObjectName(u"label_9")
        self.label_9.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.gridLayout.addWidget(self.label_9, 2, 3, 1, 1)

        self.w_parent_id_label = QLabel(self.groupBox)
        self.w_parent_id_label.setObjectName(u"w_parent_id_label")
        sizePolicy.setHeightForWidth(self.w_parent_id_label.sizePolicy().hasHeightForWidth())
        self.w_parent_id_label.setSizePolicy(sizePolicy)

        self.gridLayout.addWidget(self.w_parent_id_label, 2, 4, 1, 1)

        self.w_parent_id_copy_button = QToolButton(self.groupBox)
        self.w_parent_id_copy_button.setObjectName(u"w_parent_id_copy_button")
        self.w_parent_id_copy_button.setMaximumSize(QSize(13, 13))
        self.w_parent_id_copy_button.setIcon(icon)

        self.gridLayout.addWidget(self.w_parent_id_copy_button, 2, 5, 1, 1)

        self.label_8 = QLabel(self.groupBox)
        self.label_8.setObjectName(u"label_8")
        self.label_8.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.gridLayout.addWidget(self.label_8, 3, 0, 1, 1)

        self.w_type_label = QLabel(self.groupBox)
        self.w_type_label.setObjectName(u"w_type_label")
        sizePolicy1.setHeightForWidth(self.w_type_label.sizePolicy().hasHeightForWidth())
        self.w_type_label.setSizePolicy(sizePolicy1)

        self.gridLayout.addWidget(self.w_type_label, 3, 1, 1, 1)

        self.label_13 = QLabel(self.groupBox)
        self.label_13.setObjectName(u"label_13")
        self.label_13.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.gridLayout.addWidget(self.label_13, 3, 3, 1, 1)

        self.w_target_id_label = QLabel(self.groupBox)
        self.w_target_id_label.setObjectName(u"w_target_id_label")
        sizePolicy1.setHeightForWidth(self.w_target_id_label.sizePolicy().hasHeightForWidth())
        self.w_target_id_label.setSizePolicy(sizePolicy1)

        self.gridLayout.addWidget(self.w_target_id_label, 3, 4, 1, 1)

        self.w_target_id_copy_button = QToolButton(self.groupBox)
        self.w_target_id_copy_button.setObjectName(u"w_target_id_copy_button")
        self.w_target_id_copy_button.setMaximumSize(QSize(13, 13))
        self.w_target_id_copy_button.setIcon(icon)

        self.gridLayout.addWidget(self.w_target_id_copy_button, 3, 5, 1, 1)


        self.verticalLayout.addWidget(self.groupBox)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.w_use_commit_state_trace_button = QCheckBox(DSCommitProgram)
        self.w_use_commit_state_trace_button.setObjectName(u"w_use_commit_state_trace_button")

        self.horizontalLayout.addWidget(self.w_use_commit_state_trace_button)

        self.w_use_description_button = QCheckBox(DSCommitProgram)
        self.w_use_description_button.setObjectName(u"w_use_description_button")

        self.horizontalLayout.addWidget(self.w_use_description_button)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.splitter = QSplitter(DSCommitProgram)
        self.splitter.setObjectName(u"splitter")
        self.splitter.setOrientation(Qt.Orientation.Vertical)
        self.w_tree_widget = QTreeWidget(self.splitter)
        self.w_tree_widget.setObjectName(u"w_tree_widget")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy3.setHorizontalStretch(1)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.w_tree_widget.sizePolicy().hasHeightForWidth())
        self.w_tree_widget.setSizePolicy(sizePolicy3)
        self.w_tree_widget.setAlternatingRowColors(True)
        self.splitter.addWidget(self.w_tree_widget)
        self.w_text_edit = QTextEdit(self.splitter)
        self.w_text_edit.setObjectName(u"w_text_edit")
        self.w_text_edit.setMaximumSize(QSize(16777215, 16777215))
        self.w_text_edit.setUndoRedoEnabled(False)
        self.splitter.addWidget(self.w_text_edit)

        self.verticalLayout.addWidget(self.splitter)


        self.retranslateUi(DSCommitProgram)

        QMetaObject.connectSlotsByName(DSCommitProgram)
    # setupUi

    def retranslateUi(self, DSCommitProgram):
        DSCommitProgram.setWindowTitle(QCoreApplication.translate("DSCommitProgram", u"Frame", None))
        self.groupBox.setTitle(QCoreApplication.translate("DSCommitProgram", u"Commit Header", None))
        self.label.setText(QCoreApplication.translate("DSCommitProgram", u"Label:", None))
        self.w_label_label.setText("")
        self.label_3.setText(QCoreApplication.translate("DSCommitProgram", u"Date:", None))
        self.w_date_label.setText(QCoreApplication.translate("DSCommitProgram", u"-", None))
        self.label_5.setText(QCoreApplication.translate("DSCommitProgram", u"Commit:", None))
        self.w_commit_id_label.setText(QCoreApplication.translate("DSCommitProgram", u"0000000000000000000000000000000000000000", None))
        self.w_commit_id_copy_button.setText(QCoreApplication.translate("DSCommitProgram", u"...", None))
        self.label_9.setText(QCoreApplication.translate("DSCommitProgram", u"Parent:", None))
        self.w_parent_id_label.setText(QCoreApplication.translate("DSCommitProgram", u"0000000000000000000000000000000000000000", None))
        self.w_parent_id_copy_button.setText(QCoreApplication.translate("DSCommitProgram", u"...", None))
        self.label_8.setText(QCoreApplication.translate("DSCommitProgram", u"Type:", None))
        self.w_type_label.setText(QCoreApplication.translate("DSCommitProgram", u"-", None))
        self.label_13.setText(QCoreApplication.translate("DSCommitProgram", u"Target:", None))
        self.w_target_id_label.setText(QCoreApplication.translate("DSCommitProgram", u"0000000000000000000000000000000000000000", None))
        self.w_target_id_copy_button.setText(QCoreApplication.translate("DSCommitProgram", u"...", None))
        self.w_use_commit_state_trace_button.setText(QCoreApplication.translate("DSCommitProgram", u"Use Commit State Trace", None))
        self.w_use_description_button.setText(QCoreApplication.translate("DSCommitProgram", u"Use Description", None))
        ___qtreewidgetitem = self.w_tree_widget.headerItem()
        ___qtreewidgetitem.setText(6, QCoreApplication.translate("DSCommitProgram", u"Before Position", None));
        ___qtreewidgetitem.setText(5, QCoreApplication.translate("DSCommitProgram", u"Position", None));
        ___qtreewidgetitem.setText(4, QCoreApplication.translate("DSCommitProgram", u"Path", None));
        ___qtreewidgetitem.setText(3, QCoreApplication.translate("DSCommitProgram", u"Opcode", None));
        ___qtreewidgetitem.setText(2, QCoreApplication.translate("DSCommitProgram", u"Instance ID", None));
        ___qtreewidgetitem.setText(1, QCoreApplication.translate("DSCommitProgram", u"Concept", None));
        ___qtreewidgetitem.setText(0, QCoreApplication.translate("DSCommitProgram", u"Attachment", None));
    # retranslateUi

