# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ds_commit_settings.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QDoubleSpinBox,
    QFrame, QGridLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QSizePolicy, QSpacerItem,
    QTabWidget, QToolButton, QVBoxLayout, QWidget)

class Ui_DSCommitSettings(object):
    def setupUi(self, DSCommitSettings):
        if not DSCommitSettings.objectName():
            DSCommitSettings.setObjectName(u"DSCommitSettings")
        DSCommitSettings.resize(316, 252)
        self.gridLayout_2 = QGridLayout(DSCommitSettings)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.tabwidget = QTabWidget(DSCommitSettings)
        self.tabwidget.setObjectName(u"tabwidget")
        self.tab = QWidget()
        self.tab.setObjectName(u"tab")
        self.gridLayout = QGridLayout(self.tab)
        self.gridLayout.setObjectName(u"gridLayout")
        self.label = QLabel(self.tab)
        self.label.setObjectName(u"label")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)

        self.w_sync_source_combo_box = QComboBox(self.tab)
        self.w_sync_source_combo_box.addItem("")
        self.w_sync_source_combo_box.addItem("")
        self.w_sync_source_combo_box.addItem("")
        self.w_sync_source_combo_box.addItem("")
        self.w_sync_source_combo_box.setObjectName(u"w_sync_source_combo_box")

        self.gridLayout.addWidget(self.w_sync_source_combo_box, 0, 1, 1, 1)

        self.label_2 = QLabel(self.tab)
        self.label_2.setObjectName(u"label_2")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy1)
        self.label_2.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)

        self.w_sync_file_label = QLabel(self.tab)
        self.w_sync_file_label.setObjectName(u"w_sync_file_label")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.w_sync_file_label.sizePolicy().hasHeightForWidth())
        self.w_sync_file_label.setSizePolicy(sizePolicy2)

        self.gridLayout.addWidget(self.w_sync_file_label, 1, 1, 1, 1)

        self.w_sync_file_button = QToolButton(self.tab)
        self.w_sync_file_button.setObjectName(u"w_sync_file_button")

        self.gridLayout.addWidget(self.w_sync_file_button, 1, 2, 1, 1)

        self.label_4 = QLabel(self.tab)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.gridLayout.addWidget(self.label_4, 2, 0, 1, 1)

        self.w_sync_socket_label = QLabel(self.tab)
        self.w_sync_socket_label.setObjectName(u"w_sync_socket_label")

        self.gridLayout.addWidget(self.w_sync_socket_label, 2, 1, 1, 1)

        self.w_sync_socket_button = QToolButton(self.tab)
        self.w_sync_socket_button.setObjectName(u"w_sync_socket_button")

        self.gridLayout.addWidget(self.w_sync_socket_button, 2, 2, 1, 1)

        self.label_6 = QLabel(self.tab)
        self.label_6.setObjectName(u"label_6")
        self.label_6.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.gridLayout.addWidget(self.label_6, 3, 0, 1, 1)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.w_sync_hostname_line_edit = QLineEdit(self.tab)
        self.w_sync_hostname_line_edit.setObjectName(u"w_sync_hostname_line_edit")

        self.horizontalLayout.addWidget(self.w_sync_hostname_line_edit)

        self.w_sync_service_line_edit = QLineEdit(self.tab)
        self.w_sync_service_line_edit.setObjectName(u"w_sync_service_line_edit")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.w_sync_service_line_edit.sizePolicy().hasHeightForWidth())
        self.w_sync_service_line_edit.setSizePolicy(sizePolicy3)
        self.w_sync_service_line_edit.setMaximumSize(QSize(50, 16777215))

        self.horizontalLayout.addWidget(self.w_sync_service_line_edit)


        self.gridLayout.addLayout(self.horizontalLayout, 3, 1, 1, 2)

        self.tabwidget.addTab(self.tab, "")
        self.tab_2 = QWidget()
        self.tab_2.setObjectName(u"tab_2")
        self.verticalLayout = QVBoxLayout(self.tab_2)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.label_7 = QLabel(self.tab_2)
        self.label_7.setObjectName(u"label_7")

        self.horizontalLayout_3.addWidget(self.label_7)

        self.w_live_update_interval_spin_box = QDoubleSpinBox(self.tab_2)
        self.w_live_update_interval_spin_box.setObjectName(u"w_live_update_interval_spin_box")
        self.w_live_update_interval_spin_box.setMinimumSize(QSize(100, 0))
        self.w_live_update_interval_spin_box.setReadOnly(False)
        self.w_live_update_interval_spin_box.setKeyboardTracking(True)
        self.w_live_update_interval_spin_box.setDecimals(1)
        self.w_live_update_interval_spin_box.setMinimum(0.100000000000000)
        self.w_live_update_interval_spin_box.setMaximum(100.000000000000000)
        self.w_live_update_interval_spin_box.setSingleStep(0.100000000000000)
        self.w_live_update_interval_spin_box.setValue(1.000000000000000)

        self.horizontalLayout_3.addWidget(self.w_live_update_interval_spin_box)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_2)


        self.verticalLayout.addLayout(self.horizontalLayout_3)

        self.w_live_sync_with_source_check_box = QCheckBox(self.tab_2)
        self.w_live_sync_with_source_check_box.setObjectName(u"w_live_sync_with_source_check_box")

        self.verticalLayout.addWidget(self.w_live_sync_with_source_check_box)

        self.verticalSpacer = QSpacerItem(20, 66, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)

        self.tabwidget.addTab(self.tab_2, "")

        self.gridLayout_2.addWidget(self.tabwidget, 0, 0, 1, 2)

        self.horizontalSpacer = QSpacerItem(147, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_2.addItem(self.horizontalSpacer, 1, 0, 1, 1)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.w_cancel_button = QPushButton(DSCommitSettings)
        self.w_cancel_button.setObjectName(u"w_cancel_button")

        self.horizontalLayout_2.addWidget(self.w_cancel_button)

        self.w_ok_button = QPushButton(DSCommitSettings)
        self.w_ok_button.setObjectName(u"w_ok_button")
        self.w_ok_button.setAutoDefault(False)
        self.w_ok_button.setFlat(False)

        self.horizontalLayout_2.addWidget(self.w_ok_button)


        self.gridLayout_2.addLayout(self.horizontalLayout_2, 1, 1, 1, 1)


        self.retranslateUi(DSCommitSettings)

        self.tabwidget.setCurrentIndex(1)
        self.w_ok_button.setDefault(True)


        QMetaObject.connectSlotsByName(DSCommitSettings)
    # setupUi

    def retranslateUi(self, DSCommitSettings):
        DSCommitSettings.setWindowTitle(QCoreApplication.translate("DSCommitSettings", u"Frame", None))
        self.label.setText(QCoreApplication.translate("DSCommitSettings", u"Source:", None))
        self.w_sync_source_combo_box.setItemText(0, QCoreApplication.translate("DSCommitSettings", u"None", None))
        self.w_sync_source_combo_box.setItemText(1, QCoreApplication.translate("DSCommitSettings", u"File", None))
        self.w_sync_source_combo_box.setItemText(2, QCoreApplication.translate("DSCommitSettings", u"Socket", None))
        self.w_sync_source_combo_box.setItemText(3, QCoreApplication.translate("DSCommitSettings", u"Host", None))

        self.label_2.setText(QCoreApplication.translate("DSCommitSettings", u"File:", None))
        self.w_sync_file_label.setText(QCoreApplication.translate("DSCommitSettings", u"-", None))
        self.w_sync_file_button.setText(QCoreApplication.translate("DSCommitSettings", u"...", None))
        self.label_4.setText(QCoreApplication.translate("DSCommitSettings", u"Socket:", None))
        self.w_sync_socket_label.setText(QCoreApplication.translate("DSCommitSettings", u"-", None))
        self.w_sync_socket_button.setText(QCoreApplication.translate("DSCommitSettings", u"...", None))
        self.label_6.setText(QCoreApplication.translate("DSCommitSettings", u"Host:", None))
        self.w_sync_hostname_line_edit.setText(QCoreApplication.translate("DSCommitSettings", u"localhost", None))
        self.w_sync_service_line_edit.setText(QCoreApplication.translate("DSCommitSettings", u"54321", None))
        self.tabwidget.setTabText(self.tabwidget.indexOf(self.tab), QCoreApplication.translate("DSCommitSettings", u"Tab 1", None))
        self.label_7.setText(QCoreApplication.translate("DSCommitSettings", u"Update Interval (sec)", None))
        self.w_live_sync_with_source_check_box.setText(QCoreApplication.translate("DSCommitSettings", u"Sync with secondary source", None))
        self.tabwidget.setTabText(self.tabwidget.indexOf(self.tab_2), QCoreApplication.translate("DSCommitSettings", u"Tab 2", None))
        self.w_cancel_button.setText(QCoreApplication.translate("DSCommitSettings", u"Cancel", None))
        self.w_ok_button.setText(QCoreApplication.translate("DSCommitSettings", u"Ok", None))
    # retranslateUi

