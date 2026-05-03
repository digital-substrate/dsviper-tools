# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ds_connect_to_server.ui'
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
    QGroupBox, QLineEdit, QPushButton, QSizePolicy,
    QSpacerItem, QWidget)

class Ui_DSConnectToServer(object):
    def setupUi(self, DSConnectToServer):
        if not DSConnectToServer.objectName():
            DSConnectToServer.setObjectName(u"DSConnectToServer")
        DSConnectToServer.resize(266, 151)
        self.gridLayout_2 = QGridLayout(DSConnectToServer)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.groupBox = QGroupBox(DSConnectToServer)
        self.groupBox.setObjectName(u"groupBox")
        self.gridLayout = QGridLayout(self.groupBox)
        self.gridLayout.setObjectName(u"gridLayout")
        self.w_host_line_edit = QLineEdit(self.groupBox)
        self.w_host_line_edit.setObjectName(u"w_host_line_edit")
        self.w_host_line_edit.setMinimumSize(QSize(150, 0))

        self.gridLayout.addWidget(self.w_host_line_edit, 0, 0, 1, 1)

        self.w_service_line_edit = QLineEdit(self.groupBox)
        self.w_service_line_edit.setObjectName(u"w_service_line_edit")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.w_service_line_edit.sizePolicy().hasHeightForWidth())
        self.w_service_line_edit.setSizePolicy(sizePolicy)
        self.w_service_line_edit.setMinimumSize(QSize(50, 0))
        self.w_service_line_edit.setMaximumSize(QSize(50, 16777215))

        self.gridLayout.addWidget(self.w_service_line_edit, 0, 1, 1, 1)

        self.w_socket_path_line_edit = QLineEdit(self.groupBox)
        self.w_socket_path_line_edit.setObjectName(u"w_socket_path_line_edit")

        self.gridLayout.addWidget(self.w_socket_path_line_edit, 1, 0, 1, 1)

        self.w_use_socket_path_check_box = QCheckBox(self.groupBox)
        self.w_use_socket_path_check_box.setObjectName(u"w_use_socket_path_check_box")

        self.gridLayout.addWidget(self.w_use_socket_path_check_box, 1, 1, 1, 1)


        self.gridLayout_2.addWidget(self.groupBox, 0, 0, 1, 3)

        self.horizontalSpacer = QSpacerItem(95, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_2.addItem(self.horizontalSpacer, 1, 0, 1, 1)

        self.w_cancel_button = QPushButton(DSConnectToServer)
        self.w_cancel_button.setObjectName(u"w_cancel_button")

        self.gridLayout_2.addWidget(self.w_cancel_button, 1, 1, 1, 1)

        self.w_ok_button = QPushButton(DSConnectToServer)
        self.w_ok_button.setObjectName(u"w_ok_button")

        self.gridLayout_2.addWidget(self.w_ok_button, 1, 2, 1, 1)


        self.retranslateUi(DSConnectToServer)

        self.w_ok_button.setDefault(True)


        QMetaObject.connectSlotsByName(DSConnectToServer)
    # setupUi

    def retranslateUi(self, DSConnectToServer):
        DSConnectToServer.setWindowTitle(QCoreApplication.translate("DSConnectToServer", u"Frame", None))
        self.groupBox.setTitle(QCoreApplication.translate("DSConnectToServer", u"Server", None))
        self.w_host_line_edit.setText(QCoreApplication.translate("DSConnectToServer", u"192.168.1.16", None))
        self.w_service_line_edit.setText(QCoreApplication.translate("DSConnectToServer", u"54321", None))
        self.w_socket_path_line_edit.setText(QCoreApplication.translate("DSConnectToServer", u"/tmp/raptor.sock", None))
        self.w_use_socket_path_check_box.setText("")
        self.w_cancel_button.setText(QCoreApplication.translate("DSConnectToServer", u"Cancel", None))
        self.w_ok_button.setText(QCoreApplication.translate("DSConnectToServer", u"Ok", None))
    # retranslateUi

