###############################################################################
# This file is part of openWNS (open Wireless Network Simulator)
# _____________________________________________________________________________
#
# Copyright (C) 2004-2007
# Chair of Communication Networks (ComNets)
# Kopernikusstr. 16, D-52074 Aachen, Germany
# phone: ++49-241-80-27910,
# fax: ++49-241-80-22242
# email: info@openwns.org
# www: http://www.openwns.org
# _____________________________________________________________________________
#
# openWNS is free software; you can redistribute it and/or modify it under the
# terms of the GNU Lesser General Public License version 2 as published by the
# Free Software Foundation;
#
# openWNS is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

import os
import datetime

from PyQt4 import QtCore, QtGui

from Tools import URI, Observing

import Models
import Debug
import time

from ui.Dialogues_OpenDatabase_ui import Ui_Dialogues_OpenDatabase
class OpenDatabase(QtGui.QDialog, Ui_Dialogues_OpenDatabase, Observing):

    class URIValidator(QtGui.QRegExpValidator):

        def __init__(self, fileSchemes, hostSchemes, parent = None):
            self.fixupScheme = fileSchemes[0]
            fileSchemeRegExp = "(" + "|".join(fileSchemes) + ")" + "://" + "/[\w/\.]+(\?[\w=]*)?"
            hostSchemeRegExp = "(" + "|".join(hostSchemes) + ")" + "://" + "(\w*(:\w*)?@)?\w+(:\d*)?/[\w/\.]+(\?[\w=]*)?"
            regExp = QtCore.QRegExp("^(" + fileSchemeRegExp + "|" + hostSchemeRegExp + ")")
            QtGui.QRegExpValidator.__init__(self, regExp, parent)

        def validate(self, text, pos):
            return QtGui.QRegExpValidator.validate(self, text, pos)

    fileDatabases = {"SQLite": "sqlite"}
    serverDatabases = {"MySQL": "mysql",
                       "PostreSQL": "postgres",
                       "Firebird": "firebird",
                       "MAX DB": "maxdb",
                       "MSSQL": "mssql",
                       "SyBase": "sybase"}
    schemes = dict(fileDatabases.items() + serverDatabases.items())
    schemeNames = dict(zip(schemes.values(), schemes.keys()))

    fileDatabaseDialogueConfig = {"hostEdit": False,
                                  "portEdit": False,
                                  "databaseOpenButton": True,
                                  "userEdit": False,
                                  "passwordEdit": False}

    serverDatabaseDialogueConfig = {"hostEdit": True,
                                    "portEdit": True,
                                    "databaseOpenButton": False,
                                    "userEdit": True,
                                    "passwordEdit": True}


    def __init__(self, *args):
        QtGui.QDialog.__init__(self, *args)
        self.setupUi(self)

        self.databaseTypeCombo.addItems(self.fileDatabases.keys() + self.serverDatabases.keys())

        self.uriEditValidator = self.__class__.URIValidator(self.fileDatabases.values(), self.serverDatabases.values())
        self.uriEdit.setValidator(self.uriEditValidator)

        self.lineEdits = {"user" : self.userEdit,
                          "password" : self.passwordEdit,
                          "host" : self.hostEdit,
                          "port" : self.portEdit,
                          "database" : self.databaseEdit}

        self.uri = URI(scheme = self.schemes[str(self.databaseTypeCombo.itemText(0))],
                       database = str(self.databaseEdit.text()))

        self.observe(self.on_uri_changed, self.uri)

        self.connect(self.databaseTypeCombo, QtCore.SIGNAL("activated(const QString&)"),
                     self.on_databaseTypeCombo_activated)

        for uriAttrib, lineEdit in self.lineEdits.items():
            handlerName = "on_" + uriAttrib + "Edit_textEdited"
            setattr(self, handlerName, self.onTextEditedHandler(uriAttrib))
            self.connect(lineEdit, QtCore.SIGNAL("textEdited(const QString&)"),
                         getattr(self, handlerName))
        self.on_databaseTypeCombo_activated(self.databaseTypeCombo.currentText())

    def on_uri_changed(self, attrib, value, uri):
        Debug.printCall(self, (attrib, value, uri))
        self.uriEdit.setText(str(uri))
        if attrib == "scheme":
            index = self.databaseTypeCombo.findText(self.schemeNames[value])
            self.databaseTypeCombo.setCurrentIndex(index)
        if self.lineEdits.has_key(attrib):
            lineEdit = self.lineEdits[attrib]
            if not lineEdit.hasFocus():
                lineEdit.setText(value)
        self.uriEdit.emit(QtCore.SIGNAL("textChanged(const QString&)"), str(uri))

    @QtCore.pyqtSignature("const QString&")
    def on_databaseTypeCombo_activated(self, item):
        Debug.printCall(self, item)
        item = str(item)
        if self.fileDatabases.has_key(item):
            for attribName, enabled in self.fileDatabaseDialogueConfig.items():
                widget = getattr(self, attribName)
                widget.setEnabled(enabled)
                if not enabled and isinstance(widget, QtGui.QLineEdit):
                    widget.clear()
        elif self.serverDatabases.has_key(item):
            for attribName, enabled in self.serverDatabaseDialogueConfig.items():
                widget = getattr(self, attribName)
                widget.setEnabled(enabled)
                if not enabled and isinstance(widget, QtGui.QLineEdit):
                    widget.clear()
        else:
            raise Exception("Programming Error")
        self.uri.scheme = self.schemes[item]

    @QtCore.pyqtSignature("")
    def on_uriEdit_editingFinished(self):
        Debug.printCall(self)
        if self.uriEdit.hasAcceptableInput():
            text = str(self.uriEdit.text())
            self.uri.parse(text)

    @QtCore.pyqtSignature("")
    def on_databaseEdit_editingFinished(self):
        Debug.printCall(self)
        text = str(self.databaseEdit.text())
        if self.uri.scheme in self.fileDatabases.values() and not text.startswith("/"):
            text = os.path.abspath(text)
            self.databaseEdit.setText(text)
            self.databaseEdit.emit(QtCore.SIGNAL("textEdited(const QString&)"), text)

    @QtCore.pyqtSignature("bool")
    def on_databaseOpenButton_clicked(self, checked):
        Debug.printCall(self, checked)
        fileDialogue = QtGui.QFileDialog(self, "Select a campaign", os.getcwd(), "Database files (*.db)")
        fileDialogue.setAcceptMode(QtGui.QFileDialog.AcceptOpen)
        fileDialogue.setFileMode(QtGui.QFileDialog.ExistingFile)
        fileDialogue.setViewMode(QtGui.QFileDialog.Detail)
        if fileDialogue.exec_() == QtGui.QDialog.Accepted:
            fileName = fileDialogue.selectedFiles()[0]
            self.databaseEdit.setText(fileName)
            self.databaseEdit.emit(QtCore.SIGNAL("textEdited(const QString&)"), fileName)

    def onTextEditedHandler(self, uriAttrib):

        @QtCore.pyqtSignature("const QString&")
        def onTextEdited(text):
            Debug.printCall(self, (uriAttrib, str(text)))
            setattr(self.uri, uriAttrib, str(text))

        return onTextEdited

    def getURI(self, withPassword = False):
        return self.uri.toString(withPassword)

from ui.Dialogues_Preferences_ui import Ui_Dialogues_Preferences
class Preferences(QtGui.QDialog, Ui_Dialogues_Preferences):

    def __init__(self, *args):
        QtGui.QDialog.__init__(self, *args)
        self.setupUi(self)

    def readFromConfig(self, filename, owner):
        import Configuration
        try:
            c = Configuration.Configuration()
            c.read(filename)
        except Configuration.MissingConfigurationFile, e:
            setattr(c, 'dbHost', "")
            setattr(c, 'dbName', "")
            setattr(c, 'userName', "")
            setattr(c, 'userPassword', "")
            c.writeDbAccessConf(filename, owner)
        except (Configuration.BadConfigurationFile,
                Configuration.MissingConfigurationSection,
                Configuration.MissingConfigurationEntry), e:
            QtGui.QMessageBox.warning(self, "Parse Error", "Cannot read %s. Creating a new one.\n Error is : %s" % (unicode(e.filename), str(e)))
            setattr(c, 'dbHost', "")
            setattr(c, 'dbName', "")
            setattr(c, 'userName', "")
            setattr(c, 'userPassword', "")
            c.writeDbAccessConf(filename, owner)

        self.hostname.setText(c.dbHost)
        self.databasename.setText(c.dbName)
        self.username.setText(c.userName)
        self.password.setText(c.userPassword)
        
        try:
            cSandbox = Configuration.SandboxConfiguration()
            cSandbox.read()
        except Configuration.MissingConfigurationFile, e:
            setattr(cSandbox, 'sandboxPath', "")
            setattr(cSandbox, 'sandboxFlavour', "dbg")
            c.writeDbAccessConf(filename, owner)
        except (Configuration.BadConfigurationFile,
                Configuration.MissingConfigurationSection,
                Configuration.MissingConfigurationEntry), e:
            setattr(cSandbox, 'sandboxPath', "")
            setattr(cSandbox, 'sandboxFlavour', "dbg")
            cSandbox.writeSandboxConf(owner)            
        
        self.sandboxpath.setText(cSandbox.sandboxPath)
        self.sandboxflavour.setCurrentIndex(self.sandboxflavour.findText(QtCore.QString(cSandbox.sandboxFlavour)))

    def writeToConfig(self, filename, owner):
        import Configuration
        c = Configuration.Configuration()
        c.read(filename)

        setattr(c, 'dbHost', str(self.hostname.text()))
        setattr(c, 'dbName', str(self.databasename.text()))
        setattr(c, 'userName', str(self.username.text()))
        setattr(c, 'userPassword', str(self.password.text()))
        c.writeDbAccessConf(filename, owner)
        
        cSandbox = Configuration.SandboxConfiguration()
        cSandbox.read()        
        setattr(cSandbox, 'sandboxPath', str(self.sandboxpath.text()))
        setattr(cSandbox, 'sandboxFlavour', str(self.sandboxflavour.currentText()))
        cSandbox.writeSandboxConf(owner)            

from ui.Dialogues_OpenCampaignDb_ui import Ui_Dialogues_OpenCampaignDb
class OpenCampaignDb(QtGui.QDialog, Ui_Dialogues_OpenCampaignDb):
    def __init__(self, *args):
        from wrowser.simdb import Campaigns

        QtGui.QDialog.__init__(self, *args)
        self.setupUi(self)

        self.campaignsModel = Models.CampaignDb(Campaigns.getCampaignsDict())
        self.campaigns.setModel(self.campaignsModel)
        
        #self.campaigns.expandAll() #self.campaigns is a QTreeView (see /ui/Dialogues_OpenCampaignDb_ui.py
        user = os.getenv("USER")
        userIndex = self.campaignsModel.getUserRow(user)
        if userIndex != -1 :
            self.campaigns.expand(userIndex)
            self.campaigns.scrollTo(userIndex)

        for column in xrange(self.campaignsModel.columnCount()):
            self.campaigns.resizeColumnToContents(column)

    def getCampaign(self):
        return self.campaignsModel.getCampaign(self.campaigns.selectedIndexes()[0])

from ui.Dialogues_OpenDSV_ui import Ui_Dialogues_OpenDSV
class OpenDSV(QtGui.QDialog, Ui_Dialogues_OpenDSV):
    def __init__(self, *args):
        QtGui.QWidget.__init__(self, *args)
        self.setupUi(self)

    @QtCore.pyqtSignature("bool")
    def on_openButton_clicked(self, checked):
        Debug.printCall(self, checked)
        fileDialogue = QtGui.QFileDialog(self, "Select a campaign", os.getcwd(), "DSV files (*.csv *.txt)")
        fileDialogue.setAcceptMode(QtGui.QFileDialog.AcceptOpen)
        fileDialogue.setFileMode(QtGui.QFileDialog.ExistingFile)
        fileDialogue.setViewMode(QtGui.QFileDialog.Detail)
        if fileDialogue.exec_() == QtGui.QDialog.Accepted:
            fileName = fileDialogue.selectedFiles()[0]
            self.fileNameEdit.setText(fileName)

    @QtCore.pyqtSignature("")
    def on_fileNameEdit_editingFinished(self):
        Debug.printCall(self)
        text = str(self.fileNameEdit.text())
        if not text.startswith("/"):
            text = os.path.abspath(text)
            self.fileNameEdit.setText(text)

    def getSettings(self):
        from Tools import Chameleon as Values

        return Values(fileName = str(self.fileNameEdit.text()),
                      delimiter = str(self.delimiterEdit.text()),
                      directoryColumn = str(self.directoryColumnEdit.text()),
                      subDirectory = str(self.subDirectoryEdit.text()))

class Progress(QtGui.QProgressDialog):
    def __init__(self, labelText, minShow, *args):
        QtGui.QProgressDialog.__init__(self, *args)
        self.setCancelButton(None)
        self.labelText = labelText
        self.setLabelText(labelText)
        self.setMinimumDuration(minShow)
        self.setAutoClose(True)
        self.reset()

    def reset(self):
        self.setMinimum(0)
        self.startTime = datetime.datetime.now()
        QtGui.QProgressDialog.reset(self)

    def setCurrentAndMaximum(self, current, maximum, additionalText = ""):
        import Time

        self.setMaximum(maximum)
        self.setValue(current)
        labelText = self.labelText
        if len(additionalText) > 0:
            labelText += "\n" + additionalText
        if maximum > 0 and float(current)/maximum >= 0.01:
            elapsed = datetime.datetime.now() - self.startTime
            total = elapsed * maximum / current
            remaining = total - elapsed
            labelText += "\napprox. " + Time.Delta(remaining).asString() + " left"
        self.setLabelText(labelText)
        if QtGui.QApplication.hasPendingEvents():
            QtGui.QApplication.instance().syncX()
            QtGui.QApplication.instance().processEvents()
        time.sleep(0.006)

from ui.Dialogues_ColumnSelect_ui import Ui_Dialogues_ColumnSelect
class ColumnSelect(QtGui.QDialog, Ui_Dialogues_ColumnSelect):
    def __init__(self, cancelFlag, *args):
        QtGui.QDialog.__init__(self, *args)
        self.cancelFlag = cancelFlag
        self.setupUi(self)

    def do(self, columns, deselectedColumns):
        self.columnList.addItems(columns)
        for row in range(0, self.columnList.count()):
            item = self.columnList.item(row)
            self.columnList.setItemSelected(item, not item.text() in deselectedColumns)
        if self.exec_() == QtGui.QDialog.Accepted:
            parameters = []
            for row in range(0, self.columnList.count()):
                item = self.columnList.item(row)
                if self.columnList.isItemSelected(item):
                    parameters.append(str(item.text()))
            return parameters
        else:
            self.cancelFlag.cancelled = True
            return []

from ui.Dialogues_ConfigureGraph_ui import Ui_Dialogues_ConfigureGraph
class ConfigureGraph(QtGui.QDialog, Ui_Dialogues_ConfigureGraph):

    def __init__(self, figure, *args):
        import matplotlib.numerix as numerix

        self.figure = figure
        self.scales = {"linear": ("linear", None),
                       "ld": ("log", 2),
                       "ln": ("log", numerix.e),
                       "lg": ("log", 10)}
        self.scalesReverse = dict(zip(self.scales.values(),
                                      self.scales.keys()))

        QtGui.QWidget.__init__(self, *args)
        self.setupUi(self)

        if self.figure.grid[0]:
            self.xgridMajor.setCheckState(QtCore.Qt.Checked)
        if self.figure.grid[1]:
            self.xgridMinor.setCheckState(QtCore.Qt.Checked)
        if self.figure.grid[2]:
            self.ygridMajor.setCheckState(QtCore.Qt.Checked)
        if self.figure.grid[3]:
            self.ygridMinor.setCheckState(QtCore.Qt.Checked)

        self.xscale.setCurrentIndex(self.xscale.findText(self.scalesReverse[self.figure.scale[0:2]]))
        self.yscale.setCurrentIndex(self.yscale.findText(self.scalesReverse[self.figure.scale[2:4]]))

        self.marker.setCurrentIndex(self.marker.findText(self.figure.marker))
        if self.figure.legend:
            self.showLegend.setCheckState(QtCore.Qt.Checked)
        self.titleEdit.setText(self.figure.title)

    @QtCore.pyqtSignature("")
    def on_buttonBox_accepted(self):
        self.applyData()

    @QtCore.pyqtSignature("QAbstractButton*")
    def on_buttonBox_clicked(self, button):
        if self.buttonBox.buttonRole(button) == QtGui.QDialogButtonBox.ApplyRole:
            self.applyData()

    def applyData(self):
        grid = (self.xgridMajor.checkState() == QtCore.Qt.Checked,
                self.xgridMinor.checkState() == QtCore.Qt.Checked,
                self.ygridMajor.checkState() == QtCore.Qt.Checked,
                self.ygridMinor.checkState() == QtCore.Qt.Checked)
        if grid != self.figure.grid:
            self.figure.grid = grid
        scale = self.scales[str(self.xscale.currentText())] + \
                            self.scales[str(self.yscale.currentText())]
        if scale != self.figure.scale:
            self.figure.scale = scale

        marker = str(self.marker.currentText())
        if marker == "None":
            marker = ""
        if marker != self.figure.marker:
            self.figure.marker = marker

        legend = self.showLegend.checkState() == QtCore.Qt.Checked
        if legend != self.figure.legend:
            self.figure.legend = legend

        title = str(self.titleEdit.text())
        self.figure.title = title

class SelectItem(QtGui.QDialog):

    class ComboBox(QtGui.QWidget):

        def __init__(self, caption, items, *args):
            QtGui.QWidget.__init__(self, *args)
            self.mylayout = QtGui.QHBoxLayout(self)
            self.mylayout.setMargin(9)
            self.mylayout.setSpacing(6)
            self.mylayout.setObjectName("mylayout")

            self.label = QtGui.QLabel(self)
            self.label.setText(caption)
            self.mylayout.addWidget(self.label)

            self.comboBox = QtGui.QComboBox(self)
            self.comboBox.addItems(items)
            self.mylayout.addWidget(self.comboBox)

        def selectedIndex(self):
            return self.comboBox.currentIndex()

        def selectedText(self):
            return self.comboBox.currentText()

    class RadioButtons(QtGui.QWidget):

        def __init__(self, caption, items, *args):
            QtGui.QWidget.__init__(self, *args)

            self.mylayout = QtGui.QVBoxLayout(self)
            self.mylayout.setMargin(9)
            self.mylayout.setSpacing(6)
            self.mylayout.setObjectName("mylayout")

            self.groupbox = QtGui.QGroupBox(self)
            self.groupbox.setObjectName("groupbox")
            self.groupbox.setTitle(caption)
            self.mylayout.addWidget(self.groupbox)

            self.groupboxlayout = QtGui.QVBoxLayout(self.groupbox)
            self.groupboxlayout.setMargin(9)
            self.groupboxlayout.setSpacing(6)

            self.radiobuttons = []
            for index, item in enumerate(items):
                radiobutton = QtGui.QRadioButton(self.groupbox)
                radiobutton.setObjectName("radiobutton" + str(index))
                radiobutton.setText(item)
                self.groupboxlayout.addWidget(radiobutton)
                self.radiobuttons.append(radiobutton)

            self.radiobuttons[0].setChecked(True)

        def selectedIndex(self):
            for index in xrange(len(self.radiobuttons)):
                if self.radiobuttons[index].isChecked():
                    return index
            raise Exception("SelectItem.RadioButtons instance in invalid state")

        def selectedText(self):
            return self.radiobuttons[self.selectedIndex()].text()

    def __init__(self, title, caption, items, parent = None, selectWidget = ComboBox, *args):
        assert(len(items) > 0)
        self.items = items
        QtGui.QDialog.__init__(self, parent, *args)
        self.setObjectName("SelectItem")
        self.mylayout = QtGui.QVBoxLayout(self)
        self.mylayout.setMargin(9)
        self.mylayout.setSpacing(6)
        self.mylayout.setObjectName("mylayout")

        self.setWindowTitle(title)

        self.selectWidget = selectWidget(caption, items, self)
        self.selectWidget.setObjectName("selectWidget")
        self.mylayout.addWidget(self.selectWidget)

        self.buttonBox = QtGui.QDialogButtonBox(self)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel | QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.mylayout.addWidget(self.buttonBox)

        self.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), self.accept)
        self.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), self.reject)

    def selectedIndex(self):
        if len(self.items) == 1:
            return 0
        else:
            return self.selectWidget.selectedIndex()

    def selectedText(self):
        if len(self.items) == 1:
            return self.items[0]
        else:
            return str(self.selectWidget.selectedText())

    def exec_(self):
        if len(self.items) == 1:
            return QtGui.QDialog.Accepted
        else:
            return QtGui.QDialog.exec_(self)
