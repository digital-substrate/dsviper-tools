# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ds_inspect.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QFrame,
    QGridLayout, QGroupBox, QHBoxLayout, QLabel,
    QSizePolicy, QTextEdit, QVBoxLayout, QWidget)
import resources_rc

class Ui_DSInspect(object):
    def setupUi(self, DSInspect):
        if not DSInspect.objectName():
            DSInspect.setObjectName(u"DSInspect")
        DSInspect.resize(600, 600)
        DSInspect.setMinimumSize(QSize(600, 600))
        self.gridLayout_3 = QGridLayout(DSInspect)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.metadataGroupBox = QGroupBox(DSInspect)
        self.metadataGroupBox.setObjectName(u"metadataGroupBox")
        self.gridLayout = QGridLayout(self.metadataGroupBox)
        self.gridLayout.setObjectName(u"gridLayout")
        self.label_1 = QLabel(self.metadataGroupBox)
        self.label_1.setObjectName(u"label_1")
        self.label_1.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.gridLayout.addWidget(self.label_1, 0, 0, 1, 1)

        self.w_path_label = QLabel(self.metadataGroupBox)
        self.w_path_label.setObjectName(u"w_path_label")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.w_path_label.sizePolicy().hasHeightForWidth())
        self.w_path_label.setSizePolicy(sizePolicy)

        self.gridLayout.addWidget(self.w_path_label, 0, 1, 1, 1)

        self.label_2 = QLabel(self.metadataGroupBox)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)

        self.w_documentation_label = QLabel(self.metadataGroupBox)
        self.w_documentation_label.setObjectName(u"w_documentation_label")
        sizePolicy.setHeightForWidth(self.w_documentation_label.sizePolicy().hasHeightForWidth())
        self.w_documentation_label.setSizePolicy(sizePolicy)

        self.gridLayout.addWidget(self.w_documentation_label, 1, 1, 1, 1)

        self.label_3 = QLabel(self.metadataGroupBox)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.gridLayout.addWidget(self.label_3, 2, 0, 1, 1)

        self.w_uuid_label = QLabel(self.metadataGroupBox)
        self.w_uuid_label.setObjectName(u"w_uuid_label")
        sizePolicy.setHeightForWidth(self.w_uuid_label.sizePolicy().hasHeightForWidth())
        self.w_uuid_label.setSizePolicy(sizePolicy)

        self.gridLayout.addWidget(self.w_uuid_label, 2, 1, 1, 1)

        self.label_4 = QLabel(self.metadataGroupBox)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.gridLayout.addWidget(self.label_4, 3, 0, 1, 1)

        self.w_codec_label = QLabel(self.metadataGroupBox)
        self.w_codec_label.setObjectName(u"w_codec_label")
        sizePolicy.setHeightForWidth(self.w_codec_label.sizePolicy().hasHeightForWidth())
        self.w_codec_label.setSizePolicy(sizePolicy)

        self.gridLayout.addWidget(self.w_codec_label, 3, 1, 1, 1)

        self.label_5 = QLabel(self.metadataGroupBox)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.gridLayout.addWidget(self.label_5, 4, 0, 1, 1)

        self.w_definitions_hexdigest_label = QLabel(self.metadataGroupBox)
        self.w_definitions_hexdigest_label.setObjectName(u"w_definitions_hexdigest_label")
        sizePolicy.setHeightForWidth(self.w_definitions_hexdigest_label.sizePolicy().hasHeightForWidth())
        self.w_definitions_hexdigest_label.setSizePolicy(sizePolicy)

        self.gridLayout.addWidget(self.w_definitions_hexdigest_label, 4, 1, 1, 1)


        self.gridLayout_3.addWidget(self.metadataGroupBox, 0, 0, 1, 1)

        self.definitionsGroupBox = QGroupBox(DSInspect)
        self.definitionsGroupBox.setObjectName(u"definitionsGroupBox")
        self.gridLayout_2 = QGridLayout(self.definitionsGroupBox)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.w_concepts_image_label = QLabel(self.definitionsGroupBox)
        self.w_concepts_image_label.setObjectName(u"w_concepts_image_label")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.w_concepts_image_label.sizePolicy().hasHeightForWidth())
        self.w_concepts_image_label.setSizePolicy(sizePolicy1)
        self.w_concepts_image_label.setMinimumSize(QSize(16, 16))
        self.w_concepts_image_label.setMaximumSize(QSize(16, 16))
        self.w_concepts_image_label.setPixmap(QPixmap(u":/dsviper_components/images/concept.png"))
        self.w_concepts_image_label.setScaledContents(True)

        self.gridLayout_2.addWidget(self.w_concepts_image_label, 0, 0, 1, 1)

        self.w_concepts_label = QLabel(self.definitionsGroupBox)
        self.w_concepts_label.setObjectName(u"w_concepts_label")

        self.gridLayout_2.addWidget(self.w_concepts_label, 0, 1, 1, 1)

        self.w_club_image_label = QLabel(self.definitionsGroupBox)
        self.w_club_image_label.setObjectName(u"w_club_image_label")
        sizePolicy1.setHeightForWidth(self.w_club_image_label.sizePolicy().hasHeightForWidth())
        self.w_club_image_label.setSizePolicy(sizePolicy1)
        self.w_club_image_label.setMinimumSize(QSize(16, 16))
        self.w_club_image_label.setMaximumSize(QSize(16, 16))
        self.w_club_image_label.setPixmap(QPixmap(u":/dsviper_components/images/club.png"))
        self.w_club_image_label.setScaledContents(True)

        self.gridLayout_2.addWidget(self.w_club_image_label, 1, 0, 1, 1)

        self.w_clubs_label = QLabel(self.definitionsGroupBox)
        self.w_clubs_label.setObjectName(u"w_clubs_label")

        self.gridLayout_2.addWidget(self.w_clubs_label, 1, 1, 1, 1)

        self.w_enumeration_image_label = QLabel(self.definitionsGroupBox)
        self.w_enumeration_image_label.setObjectName(u"w_enumeration_image_label")
        sizePolicy1.setHeightForWidth(self.w_enumeration_image_label.sizePolicy().hasHeightForWidth())
        self.w_enumeration_image_label.setSizePolicy(sizePolicy1)
        self.w_enumeration_image_label.setMinimumSize(QSize(16, 16))
        self.w_enumeration_image_label.setMaximumSize(QSize(16, 16))
        self.w_enumeration_image_label.setPixmap(QPixmap(u":/dsviper_components/images/enumeration.png"))
        self.w_enumeration_image_label.setScaledContents(True)

        self.gridLayout_2.addWidget(self.w_enumeration_image_label, 2, 0, 1, 1)

        self.w_enumerations_label = QLabel(self.definitionsGroupBox)
        self.w_enumerations_label.setObjectName(u"w_enumerations_label")

        self.gridLayout_2.addWidget(self.w_enumerations_label, 2, 1, 1, 1)

        self.w_structures_image_label = QLabel(self.definitionsGroupBox)
        self.w_structures_image_label.setObjectName(u"w_structures_image_label")
        sizePolicy1.setHeightForWidth(self.w_structures_image_label.sizePolicy().hasHeightForWidth())
        self.w_structures_image_label.setSizePolicy(sizePolicy1)
        self.w_structures_image_label.setMinimumSize(QSize(16, 16))
        self.w_structures_image_label.setMaximumSize(QSize(16, 16))
        self.w_structures_image_label.setPixmap(QPixmap(u":/dsviper_components/images/structure.png"))
        self.w_structures_image_label.setScaledContents(True)

        self.gridLayout_2.addWidget(self.w_structures_image_label, 3, 0, 1, 1)

        self.w_structures_label = QLabel(self.definitionsGroupBox)
        self.w_structures_label.setObjectName(u"w_structures_label")

        self.gridLayout_2.addWidget(self.w_structures_label, 3, 1, 1, 1)

        self.w_attachments_image_label = QLabel(self.definitionsGroupBox)
        self.w_attachments_image_label.setObjectName(u"w_attachments_image_label")
        sizePolicy1.setHeightForWidth(self.w_attachments_image_label.sizePolicy().hasHeightForWidth())
        self.w_attachments_image_label.setSizePolicy(sizePolicy1)
        self.w_attachments_image_label.setMinimumSize(QSize(16, 16))
        self.w_attachments_image_label.setMaximumSize(QSize(16, 16))
        self.w_attachments_image_label.setPixmap(QPixmap(u":/dsviper_components/images/attachment.png"))
        self.w_attachments_image_label.setScaledContents(True)

        self.gridLayout_2.addWidget(self.w_attachments_image_label, 4, 0, 1, 1)

        self.w_attachments_label = QLabel(self.definitionsGroupBox)
        self.w_attachments_label.setObjectName(u"w_attachments_label")

        self.gridLayout_2.addWidget(self.w_attachments_label, 4, 1, 1, 1)


        self.gridLayout_3.addWidget(self.definitionsGroupBox, 0, 1, 1, 1)

        self.dsmDefinitionsGroupBox = QGroupBox(DSInspect)
        self.dsmDefinitionsGroupBox.setObjectName(u"dsmDefinitionsGroupBox")
        self.verticalLayout = QVBoxLayout(self.dsmDefinitionsGroupBox)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.w_show_documentation_check_box = QCheckBox(self.dsmDefinitionsGroupBox)
        self.w_show_documentation_check_box.setObjectName(u"w_show_documentation_check_box")
        sizePolicy1.setHeightForWidth(self.w_show_documentation_check_box.sizePolicy().hasHeightForWidth())
        self.w_show_documentation_check_box.setSizePolicy(sizePolicy1)

        self.horizontalLayout.addWidget(self.w_show_documentation_check_box)

        self.w_show_runtime_id_check_box = QCheckBox(self.dsmDefinitionsGroupBox)
        self.w_show_runtime_id_check_box.setObjectName(u"w_show_runtime_id_check_box")
        sizePolicy1.setHeightForWidth(self.w_show_runtime_id_check_box.sizePolicy().hasHeightForWidth())
        self.w_show_runtime_id_check_box.setSizePolicy(sizePolicy1)

        self.horizontalLayout.addWidget(self.w_show_runtime_id_check_box)

        self.label_11 = QLabel(self.dsmDefinitionsGroupBox)
        self.label_11.setObjectName(u"label_11")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.label_11.sizePolicy().hasHeightForWidth())
        self.label_11.setSizePolicy(sizePolicy2)

        self.horizontalLayout.addWidget(self.label_11)

        self.w_attachment_combo_box = QComboBox(self.dsmDefinitionsGroupBox)
        self.w_attachment_combo_box.setObjectName(u"w_attachment_combo_box")
        self.w_attachment_combo_box.setEditable(True)
        self.w_attachment_combo_box.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)

        self.horizontalLayout.addWidget(self.w_attachment_combo_box)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.w_dsm_textedit = QTextEdit(self.dsmDefinitionsGroupBox)
        self.w_dsm_textedit.setObjectName(u"w_dsm_textedit")
        self.w_dsm_textedit.setEnabled(True)
        self.w_dsm_textedit.setReadOnly(True)

        self.verticalLayout.addWidget(self.w_dsm_textedit)


        self.gridLayout_3.addWidget(self.dsmDefinitionsGroupBox, 1, 0, 1, 2)


        self.retranslateUi(DSInspect)

        QMetaObject.connectSlotsByName(DSInspect)
    # setupUi

    def retranslateUi(self, DSInspect):
        DSInspect.setWindowTitle(QCoreApplication.translate("DSInspect", u"Frame", None))
        self.metadataGroupBox.setTitle(QCoreApplication.translate("DSInspect", u"Metadata", None))
        self.label_1.setText(QCoreApplication.translate("DSInspect", u"Path:", None))
        self.w_path_label.setText("")
        self.label_2.setText(QCoreApplication.translate("DSInspect", u"Documentation:", None))
        self.w_documentation_label.setText("")
        self.label_3.setText(QCoreApplication.translate("DSInspect", u"UUID:", None))
        self.w_uuid_label.setText("")
        self.label_4.setText(QCoreApplication.translate("DSInspect", u"Codec:", None))
        self.w_codec_label.setText("")
        self.label_5.setText(QCoreApplication.translate("DSInspect", u"Def.HexDigest:", None))
        self.w_definitions_hexdigest_label.setText("")
        self.definitionsGroupBox.setTitle(QCoreApplication.translate("DSInspect", u"Definitions Report", None))
        self.w_concepts_image_label.setText("")
        self.w_concepts_label.setText(QCoreApplication.translate("DSInspect", u"0 concepts", None))
        self.w_club_image_label.setText("")
        self.w_clubs_label.setText(QCoreApplication.translate("DSInspect", u"0 clubs", None))
        self.w_enumeration_image_label.setText("")
        self.w_enumerations_label.setText(QCoreApplication.translate("DSInspect", u"0 enumerations", None))
        self.w_structures_image_label.setText("")
        self.w_structures_label.setText(QCoreApplication.translate("DSInspect", u"0 structures", None))
        self.w_attachments_image_label.setText("")
        self.w_attachments_label.setText(QCoreApplication.translate("DSInspect", u"0 attachments", None))
        self.dsmDefinitionsGroupBox.setTitle(QCoreApplication.translate("DSInspect", u"DSM Definitions", None))
        self.w_show_documentation_check_box.setText(QCoreApplication.translate("DSInspect", u"Show Documentation", None))
        self.w_show_runtime_id_check_box.setText(QCoreApplication.translate("DSInspect", u"Show Runtime ID", None))
        self.label_11.setText(QCoreApplication.translate("DSInspect", u"Attachment:", None))
    # retranslateUi

