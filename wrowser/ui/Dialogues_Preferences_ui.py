# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/Dialogues_Preferences.ui'
#
# Created: Sat Feb 21 18:26:10 2009
#      by: PyQt4 UI code generator 4.3.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Dialogues_Preferences(object):
    def setupUi(self, Dialogues_Preferences):
        Dialogues_Preferences.setObjectName("Dialogues_Preferences")
        Dialogues_Preferences.resize(QtCore.QSize(QtCore.QRect(0,0,602,426).size()).expandedTo(Dialogues_Preferences.minimumSizeHint()))

        self.vboxlayout = QtGui.QVBoxLayout(Dialogues_Preferences)
        self.vboxlayout.setObjectName("vboxlayout")

        self.tabWidget = QtGui.QTabWidget(Dialogues_Preferences)
        self.tabWidget.setObjectName("tabWidget")

        self.tab = QtGui.QWidget()
        self.tab.setObjectName("tab")

        self.hboxlayout = QtGui.QHBoxLayout(self.tab)
        self.hboxlayout.setObjectName("hboxlayout")

        self.vboxlayout1 = QtGui.QVBoxLayout()
        self.vboxlayout1.setObjectName("vboxlayout1")

        self.gridlayout = QtGui.QGridLayout()
        self.gridlayout.setObjectName("gridlayout")

        self.label = QtGui.QLabel(self.tab)
        self.label.setObjectName("label")
        self.gridlayout.addWidget(self.label,0,0,1,1)

        self.hostname = QtGui.QLineEdit(self.tab)
        self.hostname.setObjectName("hostname")
        self.gridlayout.addWidget(self.hostname,0,1,1,2)

        self.label_3 = QtGui.QLabel(self.tab)
        self.label_3.setObjectName("label_3")
        self.gridlayout.addWidget(self.label_3,2,0,1,2)

        self.username = QtGui.QLineEdit(self.tab)
        self.username.setObjectName("username")
        self.gridlayout.addWidget(self.username,2,2,1,1)

        self.label_4 = QtGui.QLabel(self.tab)
        self.label_4.setObjectName("label_4")
        self.gridlayout.addWidget(self.label_4,3,0,1,2)

        self.password = QtGui.QLineEdit(self.tab)
        self.password.setEchoMode(QtGui.QLineEdit.Password)
        self.password.setObjectName("password")
        self.gridlayout.addWidget(self.password,3,2,1,1)

        self.databasename = QtGui.QLineEdit(self.tab)
        self.databasename.setObjectName("databasename")
        self.gridlayout.addWidget(self.databasename,1,1,1,2)

        self.label_2 = QtGui.QLabel(self.tab)
        self.label_2.setObjectName("label_2")
        self.gridlayout.addWidget(self.label_2,1,0,1,1)
        self.vboxlayout1.addLayout(self.gridlayout)

        spacerItem = QtGui.QSpacerItem(20,141,QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Expanding)
        self.vboxlayout1.addItem(spacerItem)
        self.hboxlayout.addLayout(self.vboxlayout1)

        self.frame = QtGui.QFrame(self.tab)
        self.frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtGui.QFrame.Raised)
        self.frame.setObjectName("frame")

        self.vboxlayout2 = QtGui.QVBoxLayout(self.frame)
        self.vboxlayout2.setObjectName("vboxlayout2")

        self.textBrowser = QtGui.QTextBrowser(self.frame)
        self.textBrowser.setObjectName("textBrowser")
        self.vboxlayout2.addWidget(self.textBrowser)
        self.hboxlayout.addWidget(self.frame)
        self.tabWidget.addTab(self.tab,"")

        self.tab_2 = QtGui.QWidget()
        self.tab_2.setObjectName("tab_2")

        self.hboxlayout1 = QtGui.QHBoxLayout(self.tab_2)
        self.hboxlayout1.setObjectName("hboxlayout1")

        self.vboxlayout3 = QtGui.QVBoxLayout()
        self.vboxlayout3.setObjectName("vboxlayout3")

        self.gridlayout1 = QtGui.QGridLayout()
        self.gridlayout1.setObjectName("gridlayout1")

        self.label_5 = QtGui.QLabel(self.tab_2)
        self.label_5.setObjectName("label_5")
        self.gridlayout1.addWidget(self.label_5,0,0,1,2)

        self.sandboxpath = QtGui.QLineEdit(self.tab_2)
        self.sandboxpath.setObjectName("sandboxpath")
        self.gridlayout1.addWidget(self.sandboxpath,0,2,1,1)

        self.label_6 = QtGui.QLabel(self.tab_2)
        self.label_6.setObjectName("label_6")
        self.gridlayout1.addWidget(self.label_6,1,0,1,1)

        self.sandboxflavour = QtGui.QComboBox(self.tab_2)
        self.sandboxflavour.setObjectName("sandboxflavour")
        self.gridlayout1.addWidget(self.sandboxflavour,1,2,1,1)
        self.vboxlayout3.addLayout(self.gridlayout1)

        spacerItem1 = QtGui.QSpacerItem(20,40,QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Expanding)
        self.vboxlayout3.addItem(spacerItem1)
        self.hboxlayout1.addLayout(self.vboxlayout3)
        self.tabWidget.addTab(self.tab_2,"")
        self.vboxlayout.addWidget(self.tabWidget)

        self.buttonBox = QtGui.QDialogButtonBox(Dialogues_Preferences)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.NoButton|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.vboxlayout.addWidget(self.buttonBox)

        self.retranslateUi(Dialogues_Preferences)
        self.tabWidget.setCurrentIndex(1)
        QtCore.QObject.connect(self.buttonBox,QtCore.SIGNAL("accepted()"),Dialogues_Preferences.accept)
        QtCore.QObject.connect(self.buttonBox,QtCore.SIGNAL("rejected()"),Dialogues_Preferences.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialogues_Preferences)
        Dialogues_Preferences.setTabOrder(self.hostname,self.databasename)
        Dialogues_Preferences.setTabOrder(self.databasename,self.username)
        Dialogues_Preferences.setTabOrder(self.username,self.password)
        Dialogues_Preferences.setTabOrder(self.password,self.buttonBox)
        Dialogues_Preferences.setTabOrder(self.buttonBox,self.tabWidget)
        Dialogues_Preferences.setTabOrder(self.tabWidget,self.textBrowser)

    def retranslateUi(self, Dialogues_Preferences):
        Dialogues_Preferences.setWindowTitle(QtGui.QApplication.translate("Dialogues_Preferences", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Dialogues_Preferences", "Hostname", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("Dialogues_Preferences", "Username", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setText(QtGui.QApplication.translate("Dialogues_Preferences", "Password", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("Dialogues_Preferences", "Databasename", None, QtGui.QApplication.UnicodeUTF8))
        self.textBrowser.setHtml(QtGui.QApplication.translate("Dialogues_Preferences", "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
        "p, li { white-space: pre-wrap; }\n"
        "</style></head><body style=\" font-family:\'Sans Serif\'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
        "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" color:#000000;\">Wrowser works with Postgresql campaign databases.</span></p>\n"
        "<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; color:#000000;\"></p>\n"
        "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; color:#000000;\">Please provide the hostname, databasename, username and your password</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), QtGui.QApplication.translate("Dialogues_Preferences", "Database", None, QtGui.QApplication.UnicodeUTF8))
        self.label_5.setText(QtGui.QApplication.translate("Dialogues_Preferences", "Sandboxpath", None, QtGui.QApplication.UnicodeUTF8))
        self.label_6.setText(QtGui.QApplication.translate("Dialogues_Preferences", "Flavour", None, QtGui.QApplication.UnicodeUTF8))
        self.sandboxflavour.addItem(QtGui.QApplication.translate("Dialogues_Preferences", "dbg", None, QtGui.QApplication.UnicodeUTF8))
        self.sandboxflavour.addItem(QtGui.QApplication.translate("Dialogues_Preferences", "opt", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), QtGui.QApplication.translate("Dialogues_Preferences", "Sandbox", None, QtGui.QApplication.UnicodeUTF8))

