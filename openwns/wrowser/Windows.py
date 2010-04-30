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

from PyQt4 import QtCore, QtGui

import probeselector.Errors

import Dialogues
import Widgets
import Models
from Tools import Observable, Observing
import Debug

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg

import scenario.plotterFactory
import scenario.widgets
import inspect
import pprint

from ui.Windows_Main_ui import Ui_Windows_Main
class Main(QtGui.QMainWindow, Ui_Windows_Main):

    class CancelFlag:
        cancelled = False

    def __init__(self, *args):
        QtGui.QMainWindow.__init__(self, *args)
        self.setupUi(self)

        self.campaigns = Observable()
        self.reader = None
        self.readerStopped = False
        self.campaignId = None

        self.workspace = QtGui.QWorkspace(self)
        self.setCentralWidget(self.workspace)

        self.windowMapper = QtCore.QSignalMapper(self)
        self.connect(self.windowMapper, QtCore.SIGNAL("mapped(QWidget *)"),
                     self.workspace, QtCore.SLOT("setActiveWindow(QWidget *)"))

        self.cancelButton = QtGui.QPushButton("Cancel")
        progressIndicator = QtGui.QProgressBar()
        progressIndicator.setMaximum(100)
        progressIndicator.setValue(33)
        self.progressIndicator = Dialogues.ProgressStatus()
        #self.statusbar.showMessage("Halllllllooooooooooooo")
        #self.statusbar.addWidget(self.cancelButton)
        #self.statusbar.addWidget(progressIndicator)
        # currently disabled
        self.actionCloseFigure.setVisible(False)
        self.actionConfigure.setVisible(False)
        self.actionRefresh.setVisible(False)

    @QtCore.pyqtSignature("")
    def on_actionPreferences_triggered(self):
        import os
        import os.path
        filename = os.path.join(os.environ["HOME"], ".wns", "dbAccess.conf")
        owner = os.environ["USER"]

        preferencesDialogue = Dialogues.Preferences(self.workspace)
        preferencesDialogue.readFromConfig(filename, owner)
        if preferencesDialogue.exec_() == QtGui.QDialog.Accepted:
            preferencesDialogue.writeToConfig(filename, owner)

    @QtCore.pyqtSignature("")
    def on_actionView_Scenario_triggered(self):

        self.viewScenarioFilename = str(QtGui.QFileDialog.getOpenFileName(
                self.workspace,
                "Open File",
                os.getcwd(),
                "Config Files (*.py)"))
        if self.viewScenarioFilename == '' :  return 
        try:
            p = scenario.plotterFactory.create(self.viewScenarioFilename)
        except scenario.plotterFactory.InvalidConfig:
            QtGui.QMessageBox.critical(self,
                                       "No scenario found",
                                       "Could not find any scenario in this file.\n\nMake sure you have an instance of openwns.simulator.OpenWNS in the global namespace of your configuration file")
            p = None

        if p is not None:
            self.viewScenarioCanvas = scenario.widgets.FigureCanvas(self.workspace)
            self.workspace.addWindow(self.viewScenarioCanvas)
            p.plotScenario(self.viewScenarioCanvas, '', 0.0, False)
            self.viewScenarioCanvas.showMaximized()

            self.viewScenarioWidget = scenario.widgets.ViewScenario(self.viewScenarioFilename, self)
            self.viewScenarioCanvas.registerMotionEventHandler(self.viewScenarioWidget.internalWidget.on_motionEvent)
            self.viewScenarioCanvas.registerButtonPressEventHandler(self.viewScenarioWidget.internalWidget.on_buttonPressEvent)

            self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.viewScenarioWidget)

            self.actionOpenCampaignDatabase.setEnabled(False)
            self.actionOpenDSV.setEnabled(False)
            self.actionOpenDirectory.setEnabled(False)
            self.actionView_Scenario.setEnabled(False)
            self.actionCloseDataSource.setEnabled(True)

    def updateScenarioView(self, fileToPlot, fillValue, includeContour):
        if self.viewScenarioCanvas is not None:
            p = scenario.plotterFactory.create(self.viewScenarioFilename)

            self.viewScenarioCanvas.clear()

            p.plotScenario(self.viewScenarioCanvas, fileToPlot, fillValue, includeContour)

    def updateCutPlot(self, fileToPlot, fillValue, x1, y1, x2, y2):
        if self.viewScenarioCanvas is not None:
            p = scenario.plotterFactory.create(self.viewScenarioFilename)

            self.viewScenarioCanvas.clear()

            p.plotCut(self.viewScenarioCanvas, fileToPlot, fillValue, x1, y1, x2, y2)

    @QtCore.pyqtSignature("")
    def on_actionOpenCampaignDatabase_triggered(self):
        from simdb import Campaigns
        from probeselector import PostgresReader, Representations, Interface

        campaignDbDialogue = Dialogues.OpenCampaignDb(self.workspace)
        self.workspace.addWindow(campaignDbDialogue)
        campaignDbDialogue.showMaximized()
        if campaignDbDialogue.exec_() == QtGui.QDialog.Accepted:
            campaignId = campaignDbDialogue.getCampaign()
            self.campaignId = campaignId
            Campaigns.setCampaign([campaignId])
            self.campaignTitle = Campaigns.getCampaignInfo(campaignId)[0][1]
            windowTitleElements = self.windowTitle().split(' ')
            self.setWindowTitle(windowTitleElements[0]+" "+windowTitleElements[1]+" "+self.campaignTitle)
            #progressDialog = Dialogues.ProgressStatus() #Dialogues.Progress("Reading data", 0, self.workspace)
            self.statusbar.addWidget(self.cancelButton)
            self.statusbar.addWidget(self.progressIndicator)
            self.cancelButton.show()
            self.progressIndicator.show()
            self.cancelButton.connect(self.cancelButton,QtCore.SIGNAL("clicked()"),self.on_cancelClicked)
            #progressDialog.connect(progressDialog, QtCore.SIGNAL("canceled()"),self.on_cancelClicked)
            self.reader = PostgresReader.CampaignReader(campaignId,
                                                        None,
                                                        self.progressIndicator.setCurrentAndMaximum,
                                                        True)
            campaign = Representations.Campaign(*self.reader.read())
            self.statusbar.removeWidget(self.cancelButton)
            self.statusbar.removeWidget(self.progressIndicator)
            self.progressIndicator.reset()
            self.progressIndicator.setValue(0)
            if self.readerStopped:
                self.readerStopped = False
                return
            self.campaigns.original = Interface.Facade(campaign)

            self.simulationParameters = SimulationParameters(self.campaigns, self)
            self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.simulationParameters)
            self.menuNew.setEnabled(True)
            self.actionOpenCampaignDatabase.setEnabled(False)
            self.actionOpenDSV.setEnabled(False)
            self.actionOpenDirectory.setEnabled(False)
            self.actionCloseDataSource.setEnabled(True)

    def on_cancelClicked(self):
        self.readerStopped = True
        self.reader.stop()

    @QtCore.pyqtSignature("")
    def on_actionOpenDSV_triggered(self):
        from probeselector import DSVReaders, Representations, Interface

        dsvDialogue = Dialogues.OpenDSV(self.workspace)
        if dsvDialogue.exec_() == QtGui.QDialog.Accepted:
            settings = dsvDialogue.getSettings()
            cancelFlag = self.__class__.CancelFlag()
            campaign = Representations.Campaign(*DSVReaders.CampaignReader(settings.fileName,
                                                                           Dialogues.ColumnSelect(cancelFlag, self),
                                                                           Dialogues.Progress("Reading data", 0, self).setCurrentAndMaximum,
                                                                           settings.subDirectory,
                                                                           settings.directoryColumn,
                                                                           settings.delimiter,
                                                                           True).read())
            self.campaigns.original = Interface.Facade(campaign)

            if not cancelFlag.cancelled:
                self.simulationParameters = SimulationParameters(self.campaigns, self)
                self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.simulationParameters)
                self.menuNew.setEnabled(True)
                self.actionOpenCampaignDatabase.setEnabled(False)
                self.actionOpenDSV.setEnabled(False)
                self.actionOpenDirectory.setEnabled(False)
                self.actionCloseDataSource.setEnabled(True)


    @QtCore.pyqtSignature("")
    def on_actionOpenDirectory_triggered(self):
        self.directoryNavigation = DirectoryNavigation(self.campaigns, os.getcwd(), self)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.directoryNavigation)
        self.actionOpenCampaignDatabase.setEnabled(False)
        self.actionOpenDSV.setEnabled(False)
        self.actionOpenDirectory.setEnabled(False)
        self.actionCloseDataSource.setEnabled(True)

    QtCore.pyqtSignature("")
    def on_actionCloseDataSource_triggered(self):
        if hasattr(self, "simulationParameters"):
            self.simulationParameters.close()
        if hasattr(self, "directoryNavigation"):
            self.directoryNavigation.close()
        if hasattr(self, "viewScenarioWidget"):
            self.viewScenarioWidget.close()
        for window in self.workspace.windowList():
            window.close()
        self.campaigns = Observable()
        self.actionOpenCampaignDatabase.setEnabled(True)
        self.actionOpenDSV.setEnabled(True)
        self.actionOpenDirectory.setEnabled(True)
        self.actionCloseDataSource.setEnabled(False)
        self.actionNewParameter.setEnabled(True)
        self.actionView_Scenario.setEnabled(True)
        self.menuNew.setEnabled(False)

    @QtCore.pyqtSignature("")
    def on_actionRefresh_triggered(self):
        from probeselector import Representations, Interface

        if self.reader != None:
            self.campaigns.original = Interface.Facade(Representations.Campaign(*self.reader.read()))

    @QtCore.pyqtSignature("")
    def on_actionNewLogEval_triggered(self):
        figureWindow = LogEvalFigure(self.campaigns, self.menuFigure, self, self.workspace)
        self.workspace.addWindow(figureWindow)
        figureWindow.showMaximized()

    @QtCore.pyqtSignature("")
    def on_actionNewTimeSeries_triggered(self):
        figureWindow = TimeSeriesFigure(self.campaigns, self.menuFigure, self, self.workspace)
        self.workspace.addWindow(figureWindow)
        figureWindow.showMaximized()

    @QtCore.pyqtSignature("")
    def on_actionNewXDF_triggered(self):
        figureWindow = XDFFigure(self.campaigns, self.campaignId, self.menuFigure, self, self.workspace)
        self.workspace.addWindow(figureWindow)
        figureWindow.showMaximized()

    @QtCore.pyqtSignature("")
    def on_actionNewLRE_triggered(self):
        figureWindow = LREFigure(self.campaigns, self.menuFigure, self, self.workspace)
        self.workspace.addWindow(figureWindow)
        figureWindow.showMaximized()

    @QtCore.pyqtSignature("")
    def on_actionNewBatchMeans_triggered(self):
        figureWindow = BatchMeansFigure(self.campaigns, self.menuFigure, self, self.workspace)
        self.workspace.addWindow(figureWindow)
        figureWindow.showMaximized()

    @QtCore.pyqtSignature("")
    def on_actionNewTable_triggered(self):
        figureWindow = TableFigure(self.campaigns, self.menuFigure, self, self.workspace)
        self.workspace.addWindow(figureWindow)
        figureWindow.showMaximized()

    @QtCore.pyqtSignature("")
    def on_actionNewParameter_triggered(self):
        figureWindow = ParameterFigure(self.campaigns, self.campaignId, self.menuFigure, self, self.workspace)
        self.workspace.addWindow(figureWindow)
        figureWindow.showMaximized()

    @QtCore.pyqtSignature("")
    def on_actionAboutQt_triggered(self):
	QtGui.QApplication.aboutQt()

    @QtCore.pyqtSignature("")
    def on_actionAboutWrowser_triggered(self):
	QtGui.QMessageBox.about(self,
				"About Wrowser",
				"<h4>Wrowser - The WNS Result Browser</h4>"
				"The Wrowser is a browsing and viewing utility "
				"for results of the WNS simulator.")

class SimulationParameters(QtGui.QDockWidget):

    from ui.Windows_SimulationParameters_ui import Ui_Windows_SimulationParameters
    class Widget(QtGui.QWidget, Ui_Windows_SimulationParameters, Observing):

        class FilterExpressionValidator(QtGui.QValidator):

            def __init__(self, campaign, additionalFilter, parent = None):
                QtGui.QValidator.__init__(self, parent)
                self.campaign = campaign
                self.additionalFilter = additionalFilter

            def validate(self, text, pos):
                filterExpression = str(text)
                if filterExpression == "":
                    filterExpression = "True"
                try:
                    filteredCampaign = self.campaign.filteredByExpression(filterExpression)
                except probeselector.Errors.InvalidFilterExpression:
                    return (QtGui.QValidator.Intermediate, pos)
                else:
                    if self.additionalFilter(filteredCampaign).isEmpty():
                        return (QtGui.QValidator.Intermediate, pos)
                    return (QtGui.QValidator.Acceptable, pos)

        def __init__(self, campaigns, *args):
            QtGui.QWidget.__init__(self, *args)
            self.setupUi(self)
            self.campaigns = campaigns

            self.filterEditValidator = self.__class__.FilterExpressionValidator(self.campaigns.original, self.filterCampaignBySelection)
            self.filterEdit.setValidator(self.filterEditValidator)
            self.connect(self.filterEdit, QtCore.SIGNAL("textEdited(const QString&)"), self.on_filterEdit_textEdited)

            self.simulationParametersModel = Models.SimulationParameters(self.campaigns.original)
            self.simulationParametersView.setModel(self.simulationParametersModel)
            self.connect(self.simulationParametersModel, QtCore.SIGNAL("dataChanged(const QModelIndex&, const QModelIndex&)"), self.on_simulationParametersModel_dataChanged)

            self.observe(self.on_expressionFilteredCampaignChanged, self.campaigns, "expressionFiltered")
            self.observe(self.on_drawCampaignChanged, self.campaigns, "draw")
            self.campaigns.expressionFiltered = self.campaigns.original
            self.campaigns.draw = self.campaigns.original
            self.toggleButtons = { }
            for row in xrange(self.simulationParametersModel.rowCount()):
                node = self.simulationParametersModel.index(row, 0)
                self.simulationParametersView.setExpanded(node , True)
                if self.simulationParametersModel.rowCount(node) > 2 : 
                    toggleButton = QtGui.QPushButton("toggle",self.simulationParametersView)
                    toggleButton.setFixedSize(toggleButton.minimumSizeHint())
                    self.toggleButtons[toggleButton]=row
                    self.connect(toggleButton, QtCore.SIGNAL("clicked()"), self.on_toggle)
                    self.simulationParametersView.setIndexWidget(self.simulationParametersModel.index(row,1),toggleButton)

        @QtCore.pyqtSignature("const QString&")
        def on_filterEdit_textEdited(self, text):
            self.filterCampaigns()

        @QtCore.pyqtSignature("const QModelIndex&, const QModelIndex&")
        def on_simulationParametersModel_dataChanged(self, topLeft, bottomRight):
            self.filterCampaigns()

        def on_toggle(self):
            row = self.toggleButtons[self.sender()]
            self.simulationParametersModel.toggleCheckboxes(row)
            self.filterCampaigns()

        def on_expressionFilteredCampaignChanged(self, campaign):
            Debug.printCall(self, campaign)
            self.expressionFilteredInfoLabel.setText("Filtering leaves " + str(len(campaign.getScenarios())) + " simulations.")
            self.campaigns.draw = self.filterCampaignBySelection(self.campaigns.expressionFiltered)

        def on_drawCampaignChanged(self, campaign):
            Debug.printCall(self, campaign)
            self.selectionFilteredInfoLabel.setText("Selection leaves " + str(len(campaign.getScenarios())) + " simulations.")

        def filterCampaigns(self):
            Debug.printCall(self)
            if self.filterEdit.hasAcceptableInput():
                filterExpression = str(self.filterEdit.text())
                if filterExpression == "":
                    filterExpression = "True"
                self.campaigns.expressionFiltered = self.campaigns.original.filteredByExpression(filterExpression)
                self.simulationParametersModel.setCampaign(self.campaigns.expressionFiltered)
            self.campaigns.draw = self.filterCampaignBySelection(self.campaigns.expressionFiltered)
            self.filterEdit.checkState(self.filterEdit.text())

        def filterCampaignBySelection(self, campaign):
            return campaign.filteredBySelection(self.simulationParametersModel.getValueSelection())

    def closeEvent(self, event):
        self.mainWindow.on_actionCloseDataSource_triggered()

    def __init__(self, campaigns, *args):
        QtGui.QDockWidget.__init__(self, "Simulation Parameters", *args)
        self.mainWindow= args[0]
        self.internalWidget = self.__class__.Widget(campaigns)
        self.setWidget(self.internalWidget)


class DirectoryNavigation(QtGui.QDockWidget,Observing):

    from ui.Windows_DirectoryNavigation_ui import Ui_Windows_DirectoryNavigation
    class Widget(QtGui.QWidget, Ui_Windows_DirectoryNavigation):

        class DirectoryValidator(QtGui.QValidator):

            def validate(self, text, pos):
                if os.path.exists(text):
                    return (QtGui.QValidator.Acceptable, pos)
                else:
                    return (QtGui.QValidator.Intermediate, pos)

        def __init__(self, campaigns, root, mainWindow, *args):
            QtGui.QWidget.__init__(self, *args)
            self.setupUi(self)
            self.campaigns = campaigns
            self.mainWindow = mainWindow

            self.rootEditValidator = self.__class__.DirectoryValidator(self)
            self.rootEdit.setValidator(self.rootEditValidator)
            self.rootEdit.setText(root)
            self.connect(self.rootEdit, QtCore.SIGNAL("textEdited(const QString&)"), self.on_rootEdit_textEdited)
            self.directoryModel = QtGui.QDirModel([], QtCore.QDir.Dirs | QtCore.QDir.NoDotAndDotDot, QtCore.QDir.Name, self)
            self.directoryView.setModel(self.directoryModel)
            self.directoryView.setRootIndex(self.directoryModel.index(root))
            self.directoryView.setColumnHidden(1, True)
            self.directoryView.setColumnHidden(2, True)
            self.directoryView.setColumnHidden(3, True)

        @QtCore.pyqtSignature("const QString&")
        def on_rootEdit_textEdited(self, text):
            if self.rootEdit.hasAcceptableInput():
                self.directoryView.setRootIndex(self.directoryModel.index(text))

        @QtCore.pyqtSignature("bool")
        def on_upButton_clicked(self, checked):
            self.rootEdit.setText(os.path.dirname(str(self.rootEdit.text())))
            self.directoryView.setRootIndex(self.directoryModel.index(self.rootEdit.text()))

        @QtCore.pyqtSignature("bool")
        def on_rootButton_clicked(self, checked):
            dirIndex = self.directoryView.selectionModel().currentIndex()
            self.rootEdit.setText(self.directoryModel.filePath(dirIndex))
            self.directoryView.setRootIndex(self.directoryModel.index(self.rootEdit.text()))

        @QtCore.pyqtSignature("bool")
        def on_scanButton_clicked(self, checked):
            from probeselector import DirectoryReaders, Representations, Interface
            dirIndex = self.directoryView.selectionModel().currentIndex()
            self.rootEdit.setText(self.directoryModel.filePath(dirIndex))
            self.directoryView.setRootIndex(self.directoryModel.index(self.rootEdit.text()))
            directory = str(self.rootEdit.text())
            progressDialogue = Dialogues.Progress("Reading data", 0, self)
            campaign = Representations.Campaign(*DirectoryReaders.CampaignReader(directory,
                                                                                 progressDialogue.setCurrentAndMaximum).read())
            progressDialogue.close()
            self.campaigns.draw = Interface.Facade(campaign)
            self.scanInfoLabel.setText(str(len(self.campaigns.draw.getScenarios())) + " directories with probes.")
            self.mainWindow.menuNew.setEnabled(True)
            self.mainWindow.actionNewParameter.setEnabled(False)

    def closeEvent(self, event):
        self.mainWindow.on_actionCloseDataSource_triggered()

    def __init__(self, campaigns, root, parent, *args):
        QtGui.QDockWidget.__init__(self, "Directory Navigation", parent, *args)
        self.internalWidget = self.__class__.Widget(campaigns, root, parent, self)
        self.mainWindow = parent
        self.setWidget(self.internalWidget)

class Export:
    graphs=[]
    graph = None
    probeName = None
    paramName = None
    probeEntry = None
    useXProbe = False
    useYProbe = True
    xProbeName = None
    xProbeEntry = None
    aggregate = False
    originalPlots = False
    aggrParam = ''
    filterExpr = None
    simParams = None
    confidence = False
    confidenceLevel = None
    graphType = None
    campaignId = None
    #config
    marker = None
    scale = None
    grid = None
    legend = None
    title = None

    def getExpression(self):
        fExpr = ''
        for key in self.simParams :
            fExpr+=key+" in ["
            for value in self.simParams[key]:
                if type(value) == str :
                    fExpr+='"'+value+'", '
                else:
                    fExpr+=str(value)+", "
            fExpr=fExpr[0:len(fExpr)-2] #cut last comma
            fExpr+="] and "
        return fExpr[0:len(fExpr)-5] #cut last conjunction operator

    def __init__(self,graphControl,simParams,graph):
        self.probeName = graphControl.getAllSelectedProbeNames() # graphControl.yProbeNames()[0]
        self.confidence = graphControl.isShowConfidenceLevels()
        self.aggregate = graphControl.isAggregateParameter()
        if self.aggregate :
            self.aggrParam = graphControl.aggregationParameter()
            self.originalPlots = graphControl.isPlotNotAggregatedGraphs()
        self.simParams=simParams
        self.graph=graph
 
        self.filterExpr=self.getExpression() 
        self.marker = graph.figureConfig.marker
        self.scale= graph.figureConfig.scale
        self.grid = graph.figureConfig.grid
        self.legend = graph.figureConfig.legend
        self.title = graph.figureConfig.title
 

from ui.Windows_Figure_ui import Ui_Windows_Figure
class Figure(QtGui.QWidget, Ui_Windows_Figure, Observing):

    def __init__(self, campaigns, menu, windowTitle, mainWindow, *qwidgetArgs):
        QtGui.QWidget.__init__(self, *qwidgetArgs)
        self.setupUi(self)
        self.mainWindow = mainWindow
        self.campaigns = campaigns
        self.menu = menu

        self.setWindowTitle(windowTitle+"campaignTitle")
        self.setupMenu()

        self.graphControlLayout = QtGui.QVBoxLayout(self.graphControl)
        self.graphControlLayout.setMargin(0)
        self.graphControlLayout.setSpacing(0)
        self.graphControlLayout.setObjectName("graphControlLayout")

        self.graphDisplayLayout = QtGui.QVBoxLayout(self.graphDisplay)
        self.graphDisplayLayout.setMargin(0)
        self.graphDisplayLayout.setSpacing(0)
        self.graphDisplayLayout.setObjectName("graphDisplayLayout")

        self.observe(self.on_drawCampaign_changed, self.campaigns, "draw")
        self.painter = QtGui.QPainter()
        self.printer = QtGui.QPrinter(QtGui.QPrinter.HighResolution)
        self.printer.setPageSize(QtGui.QPrinter.Letter)
        self.printer.setPrintProgram("lpr")            
        self.readerStopped = False
 
    @staticmethod
    def cleanLayout(layout):
        for index in xrange(layout.count()):
            layout.removeItem(layout.itemAt(index))

    def setGraphControl(self, widgets):
        self.cleanLayout(self.graphControlLayout)
        for widget in widgets:
            widget.setParent(self.graphControl)
            self.graphControlLayout.addWidget(widget)

    def setGraphDisplay(self, widgets):
        self.cleanLayout(self.graphDisplayLayout)
        for widget in widgets:
            widget.setParent(self.graphDisplay)
            self.graphDisplayLayout.addWidget(widget)

    def setupMenu(self):
        if self.menu == None:
            return
        self.activateAction = QtGui.QAction(self)
        self.activateAction.setObjectName("actionShow" + str(id(self)))
        self.activateAction.setText(self.windowTitle())

        self.menu.addAction(self.activateAction)
        self.connect(self.activateAction, QtCore.SIGNAL("triggered()"), self.toTop)

    def toTop(self):
        Debug.printCall(self)
        self.menu.parent().parent().workspace.setActiveWindow(self)

    def closeEvent(self, event):
        if self.menu != None:
            self.menu.removeAction(self.activateAction)
        QtGui.QWidget.closeEvent(self, event)

    @QtCore.pyqtSignature("")
    def on_configure_clicked(self):
        configureDialogue = Dialogues.ConfigureGraph(self.graph.figureConfig, self)
        configureDialogue.exec_()

    @QtCore.pyqtSignature("")
    def on_export_clicked(self):
        from probeselector import Exporters
        export = self.getExport()

        formatDialogue = Dialogues.SelectItem("Export Format", "Select format", Exporters.directory.keys(), self, Dialogues.SelectItem.RadioButtons)
        if formatDialogue.exec_() == QtGui.QDialog.Accepted:
            format = formatDialogue.selectedText()
            fileDialogue = QtGui.QFileDialog(self, "Export to " + format + " file", os.getcwd(), "Files (*.*)")
            fileDialogue.setAcceptMode(QtGui.QFileDialog.AcceptSave)
            fileDialogue.setFileMode(QtGui.QFileDialog.AnyFile)
            if fileDialogue.exec_() == QtGui.QDialog.Accepted:
                filename = str(fileDialogue.selectedFiles()[0])
                progressDialogue = Dialogues.Progress("Exporting to " + filename, 0)
                Exporters.directory[format].export(filename, export , progressDialogue.setCurrentAndMaximum, progressDialogue.reset) 

    @QtCore.pyqtSignature("")
    def on_printit_clicked(self):
        imageFile="figure.png"
        self.graph.saveGraph(imageFile)
        self.image = QtGui.QImage(imageFile)
        if self.image.isNull(): return
        form = QtGui.QPrintDialog(self.printer, self)
        if form.exec_():
            self.painter.begin(self.printer)
            rect = self.painter.viewport()
            os.putenv("PRINTER",str(self.printer.printerName()))
            size = self.image.size()
            size.scale(rect.size(), QtCore.Qt.KeepAspectRatio)
            self.painter.setViewport(rect.x(),rect.y(),size.width(),size.height())
            self.painter.setWindow(self.image.rect())
            self.painter.drawImage(0,0,self.image)
            self.painter.end()
        os.remove(imageFile)

    @QtCore.pyqtSignature("bool")
    def on_draw_clicked(self, checked):
        self.graph.setGraphs(self.getGraphs())

    def on_cancelClicked(self):
        self.readerStopped = True
        self.campaigns.draw.stopAcquireGraphs()

    def showProgressBar(self):
        self.mainWindow.statusbar.addWidget(self.mainWindow.cancelButton)
        self.mainWindow.statusbar.addWidget(self.mainWindow.progressIndicator)
        self.mainWindow.cancelButton.show()
        self.mainWindow.progressIndicator.show()
        self.mainWindow.cancelButton.connect(self.mainWindow.cancelButton,QtCore.SIGNAL("clicked()"),self.on_cancelClicked)

    def acquireGraphs(self, scenarioDataAcquirer, graphClass = None): 
        campaign = self.campaigns.draw
        if graphClass is None:
           graphsHelp, errorsHelp = campaign.acquireGraphs(acquireScenarioData = scenarioDataAcquirer,
                                                            progressNotify = self.mainWindow.progressIndicator.setCurrentAndMaximum,
                                                            progressReset = self.mainWindow.progressIndicator.reset)
        else:
           graphsHelp, errorsHelp = campaign.acquireGraphs(acquireScenarioData = scenarioDataAcquirer,
                                                            progressNotify = self.mainWindow.progressIndicator.setCurrentAndMaximum,
                                                            progressReset = self.mainWindow.progressIndicator.reset,
                                                            graphClass = probeselector.Graphs.AggregatedGraph)
        return graphsHelp, errorsHelp


    def hideProgressBar(self):
        self.mainWindow.statusbar.removeWidget(self.mainWindow.cancelButton)
        self.mainWindow.statusbar.removeWidget(self.mainWindow.progressIndicator)
        self.mainWindow.progressIndicator.reset()
        self.mainWindow.progressIndicator.setValue(0)

    def getExport(self):
        print "export"
 
class LineGraphs(Observing):

    def __init__(self):
        self.graphDisplaySplitter = QtGui.QSplitter(self.graphDisplay)
        self.graphDisplaySplitter.setOrientation(QtCore.Qt.Vertical)
        self.graphDisplaySplitter.setObjectName("graphDisplaySplitter")

        self.graph = Widgets.LineGraph(self.graphDisplaySplitter)
        self.graph.setObjectName("graph")
        self.observe(self.on_figureConfig_title_changed, self.graph.figureConfig, "title")

        self.legend = Widgets.Legend(self.graphDisplaySplitter)
        self.legend.setObjectName("legend")
        self.legend.setModel(self.graph.getLegendModel())

        self.graphDisplayLayout.addWidget(self.graphDisplaySplitter)

    def on_figureConfig_title_changed(self, value):
        self.setWindowTitle(value)
        self.activateAction.setText(value)

class TableGraphs:

    def __init__(self):
        self.graph = Widgets.TableGraph(window = self)
        self.graphDisplayLayout.addWidget(self.graph)
        self.configure.setVisible(True)
        self.export.setVisible(False)

class ProbeFigure(Figure):

    def __init__(self, campaigns, menu, mainWindow, *qwidgetArgs):
        Figure.__init__(self, campaigns, menu, mainWindow, *qwidgetArgs)
        self.probeGraphControl = Widgets.ProbeGraphControl(self.graphControl)
        self.graphControlLayout.addWidget(self.probeGraphControl)

        self.probesModel = Models.ProbeNames(self.campaigns.draw, self.getProbeTypes())
        self.probeGraphControl.setModel(self.probesModel)

        self.aggregateParametersModel = Models.SimulationParameters(self.campaigns.draw, onlyNumeric = True)
        self.probeGraphControl.setAggregateParametersModel(self.aggregateParametersModel)

    def on_drawCampaign_changed(self, campaign):
        print "ProbeFigure drawCampaign changed"
        selectionModel = self.probeGraphControl.probesView().selectionModel()
        self.probeGraphControl.probesView().clearSelection()
        self.probesModel.setCampaign(self.campaigns.draw)
        itemsToSelect = self.probesModel.getProbeIndexes(selectedProbes)
        for selection in itemsToSelect:
            selectionModel.setCurrentIndex(selection,QtGui.QItemSelectionModel.Select)
 
class LogEvalFigure(ProbeFigure, LineGraphs):

    def __init__(self, campaigns, menu, mainWindow, *qwidgetArgs):
        ProbeFigure.__init__(self, campaigns, menu, "LogEval Probe Figure", mainWindow, *qwidgetArgs)
        LineGraphs.__init__(self)
        self.graph.figureConfig.title = "LogEval Probe Figure"
        self.probeGraphControl.aggregateframe.hide()

    @staticmethod
    def getProbeTypes():
        import Probe
        return [Probe.LogEvalProbe]

    def getGraphs(self):
        dataacquisition = probeselector.dataacquisition
        campaign = self.campaigns.draw

        probeNames = self.probeGraphControl.probeNames()

        probeDataAcquirer = dataacquisition.Probe.LogEval()
        probeDataAcquirers = dict([(probeName, probeDataAcquirer) for probeName in probeNames])

        parameterNames = list(campaign.getChangingParameterNames())

        scenarioDataAcquirer = dataacquisition.Scenario(probeDataAcquirers = probeDataAcquirers,
                                                        parameterNames = parameterNames)

        self.showProgressBar()  
        graphs, errors = self.acquireGraphs(scenarioDataAcquirer)

        self.hideProgressBar()  
        if self.readerStopped:
            self.readerStopped = False

        return graphs

class TimeSeriesFigure(ProbeFigure, LineGraphs):

    def __init__(self, campaigns, menu, mainWindow, *qwidgetArgs):
        ProbeFigure.__init__(self, campaigns, menu, "TimeSeries Probe Figure", mainWindow, *qwidgetArgs)
        LineGraphs.__init__(self)
        self.graph.figureConfig.title = "TimeSeries Probe Figure"
        self.probeGraphControl.aggregateframe.hide()

    @staticmethod
    def getProbeTypes():
        import Probe
        return [Probe.TimeSeriesProbe]

    def getGraphs(self):
        dataacquisition = probeselector.dataacquisition
        campaign = self.campaigns.draw

        probeNames = self.probeGraphControl.probeNames()

        probeDataAcquirer = dataacquisition.Probe.TimeSeries()
        probeDataAcquirers = dict([(probeName, probeDataAcquirer) for probeName in probeNames])

        parameterNames = list(campaign.getChangingParameterNames())

        scenarioDataAcquirer = dataacquisition.Scenario(probeDataAcquirers = probeDataAcquirers,
                                                        parameterNames = parameterNames)

        self.showProgressBar()  

        graphs, errors = self.acquireGraphs(scenarioDataAcquirer)

        self.hideProgressBar()  
        if self.readerStopped:
            self.readerStopped = False

        return graphs

class XDFFigure(ProbeFigure, LineGraphs):

    def __init__(self, campaigns, campaignId, menu, mainWindow, *qwidgetArgs):
        ProbeFigure.__init__(self, campaigns, menu, "PDF/CDF/CCDF Probe Figure", mainWindow, *qwidgetArgs)
        LineGraphs.__init__(self)
        self.graph.figureConfig.title = "PDF/CDF/CCDF Probe Figure"
        self.probeGraphControl.confidenceparameterframe.hide()
        self.campaignId = campaignId

        self.probeGraphControl.setProbeFunctions(["PDF", "CDF", "CCDF"], initialIndex = 1)

    @staticmethod
    def getProbeTypes():
        import Probe
        return [Probe.PDFProbe]

    def getGraphs(self):
        dataacquisition = probeselector.dataacquisition
        campaign = self.campaigns.draw

        funType = self.probeGraphControl.probeFunction()
        probeNames = self.probeGraphControl.probeNames()

        graphs = list()
        errors = list()

        if self.probeGraphControl.isAggregateParameter():
            probeDataAcquirer = getattr(dataacquisition.Probe, funType)(graphWriter = dataacquisition.Probe.aggregateGraphWriter)
            probeDataAcquirers = dict([(probeName, probeDataAcquirer) for probeName in probeNames])

            aggregationParameter = self.probeGraphControl.aggregationParameter()
            parameterNames = list(campaign.getChangingParameterNames() - set([aggregationParameter]))
            scenarioDataAcquirer = dataacquisition.Scenario(probeDataAcquirers, parameterNames, dataacquisition.Aggregator.weightedXDF)

            self.showProgressBar()  

            graphsHelp, errorsHelp = self.acquireGraphs(scenarioDataAcquirer, graphClass = probeselector.Graphs.AggregatedGraph)

            graphs += graphsHelp
            errors += errorsHelp

            self.hideProgressBar()  
        if self.readerStopped:
            self.readerStopped = False
            return graphs
        if self.probeGraphControl.isPlotNotAggregatedGraphs() or not self.probeGraphControl.isAggregateParameter():
            probeDataAcquirer = getattr(dataacquisition.Probe, funType)()
            probeDataAcquirers = dict([(probeName, probeDataAcquirer) for probeName in probeNames])

            parameterNames = list(campaign.getChangingParameterNames())

            scenarioDataAcquirer = dataacquisition.Scenario(probeDataAcquirers = probeDataAcquirers,
                                                            parameterNames = parameterNames)
            self.showProgressBar()  

            graphsHelp, errorsHelp = self.acquireGraphs(scenarioDataAcquirer)

            graphs += graphsHelp
            errors += errorsHelp
            self.hideProgressBar()  

        if self.readerStopped:
            self.readerStopped = False
 
        return graphs

    def getExport(self):
        simParams=Models.SimulationParameters(self.campaigns.draw, onlyNumeric = False).getValueSelection()
        exp = Export(self.probeGraphControl,simParams,self.graph)
        exp.graphs = self.getGraphs()
        exp.graphType=self.probeGraphControl.probeFunction() #"XDF" #self.graph.figureConfig.title[0:5]
        exp.campaignId = self.campaignId
        return exp

class LREFigure(ProbeFigure, LineGraphs):

    def __init__(self, campaigns, menu, mainWindow, *qwidgetArgs):
        ProbeFigure.__init__(self, campaigns, menu, "(D)LRE Probe Figure", mainWindow, *qwidgetArgs)
        LineGraphs.__init__(self)
        self.graph.figureConfig.title = "(D)LRE Probe Figure"
        self.probeGraphControl.aggregateframe.hide()

        self.probeFunctions = ["ordinate",
                               "relative error",
                               "mean local correlation coefficient",
                               "deviation from mean local corelleation coefficient",
                               "number of trials per interval",
                               "number of transitions per interval"]
        self.probeAcquirers = ["LRE_F", "LRE_d", "LRE_rho", "LRE_sigma", "LRE_n", "LRE_t"]
        self.probeFunAcMap = dict(zip(self.probeFunctions, self.probeAcquirers))

        self.probeGraphControl.setProbeFunctions(self.probeFunctions, initialIndex = 0)

    @staticmethod
    def getProbeTypes():
        import Probe
        return [Probe.LreProbe, Probe.DlreProbe]

    def getGraphs(self):
        dataacquisition = probeselector.dataacquisition
        campaign = self.campaigns.draw

        yAxis = self.probeGraphControl.probeFunction()
        probeNames = self.probeGraphControl.probeNames()

        probeDataAcquirer = getattr(dataacquisition.Probe, self.probeFunAcMap[yAxis])()
        probeDataAcquirers = dict([(probeName, probeDataAcquirer) for probeName in probeNames])

        parameterNames = list(campaign.getChangingParameterNames())

        scenarioDataAcquirer = dataacquisition.Scenario(probeDataAcquirers = probeDataAcquirers,
                                                        parameterNames = parameterNames)

        self.showProgressBar()  

        graphs, errors = self.acquireGraphs(scenarioDataAcquirer)

        self.hideProgressBar()  
        if self.readerStopped:
            self.readerStopped = False

        return graphs

class BatchMeansFigure(ProbeFigure, LineGraphs):

    def __init__(self, campaigns, menu, mainWindow, *qwidgetArgs):
        ProbeFigure.__init__(self, campaigns, menu, "BatchMeans Probe Figure", mainWindow, *qwidgetArgs)
        LineGraphs.__init__(self)
        self.probeGraphControl.aggregateframe.hide()
        
        self.graph.figureConfig.title = "BatchMeans Probe Figure"

        self.probeFunctions = ["CDF",
                               "PDF",
                               "relative error",
                               "confidence",
                               "number of trials per interval"]
        self.probeAcquirers = ["BatchMeans_CDF",
                               "BatchMeans_PDF",
                               "BatchMeans_d",
                               "BatchMeans_confidence",
                               "BatchMeans_n"]
        self.probeFunAcMap = dict(zip(self.probeFunctions, self.probeAcquirers))

        self.probeGraphControl.setProbeFunctions(self.probeFunctions, initialIndex = 0)

    @staticmethod
    def getProbeTypes():
        import Probe
        return [Probe.BatchMeansProbe]

    def getGraphs(self):
        dataacquisition = probeselector.dataacquisition
        campaign = self.campaigns.draw

        yAxis = self.probeGraphControl.probeFunction()
        probeNames = self.probeGraphControl.probeNames()

        probeDataAcquirer = getattr(dataacquisition.Probe, self.probeFunAcMap[yAxis])()
        probeDataAcquirers = dict([(probeName, probeDataAcquirer) for probeName in probeNames])

        parameterNames = list(campaign.getChangingParameterNames())

        scenarioDataAcquirer = dataacquisition.Scenario(probeDataAcquirers = probeDataAcquirers,
                                                        parameterNames = parameterNames)

        self.showProgressBar()  

        graphs, errors = self.acquireGraphs(scenarioDataAcquirer)

        self.hideProgressBar()  
        if self.readerStopped:
            self.readerStopped = False

        return graphs

class TableFigure(ProbeFigure, TableGraphs):

    def __init__(self, campaigns, menu, mainWindow, *qwidgetArgs):
        ProbeFigure.__init__(self, campaigns, menu, "Table Probe Figure", mainWindow, *qwidgetArgs)
        TableGraphs.__init__(self)

    @staticmethod
    def getProbeTypes():
        import Probe
        return [Probe.TableProbe]

    def getGraphs(self):
        import probeselector.Graphs

        dataacquisition = probeselector.dataacquisition
        campaign = self.campaigns.draw

        probeNames = self.probeGraphControl.probeNames()

        probeDataAcquirer = dataacquisition.Probe.Table()
        probeDataAcquirers = dict([(probeName, probeDataAcquirer) for probeName in probeNames])

        parameterNames = list(campaign.getChangingParameterNames())

        scenarioDataAcquirer = dataacquisition.Scenario(probeDataAcquirers = probeDataAcquirers,
                                                        parameterNames = parameterNames)

        self.showProgressBar()  

        graphs, errors = self.acquireGraphs(scenarioDataAcquirer, graphClass = probeselector.Graphs.TableGraph)

        self.hideProgressBar()  
        if self.readerStopped:
            self.readerStopped = False

        return graphs

class ParameterFigure(Figure, LineGraphs):
    def __init__(self, campaigns, campaignId, menu, mainWindow, *qwidgetArgs):
        Figure.__init__(self, campaigns, menu, "Parameter Figure", mainWindow, *qwidgetArgs)
        LineGraphs.__init__(self)
        self.observe(self.on_figureConfig_scale_changed, self.graph.figureConfig, "scale")
        self.graph.figureConfig.title = "Parameter Figure "
        self.campaignId = campaignId
        self.parameterGraphControl = Widgets.ParameterGraphControl(self.graphControl)
        self.graphControlLayout.addWidget(self.parameterGraphControl)

        self.simulationParametersModel = Models.SimulationParameters(self.campaigns.draw, onlyNumeric = True)
        self.parameterGraphControl.setSimulationParametersModel(self.simulationParametersModel)
        parameterName = self.parameterGraphControl.parameterName()

        self.aggregateParametersModel = Models.SimulationParameters(self.campaigns.draw, onlyNumeric = True)
        self.aggregateParametersModel.parameterNames.remove(parameterName)
        self.parameterGraphControl.setAggregateParametersModel(self.aggregateParametersModel)

        self.xProbesModel = Models.ProbeNames(self.campaigns.draw)
        self.parameterGraphControl.setXProbesModel(self.xProbesModel)

        self.yProbesModel = Models.ProbeNames(self.campaigns.draw)
        self.parameterGraphControl.setYProbesModel(self.yProbesModel)

        self.xProbeEntriesModel = Models.ProbeEntries(self.campaigns.draw)
        self.xProbeEntriesModel.changeProbes(self.parameterGraphControl.xProbeNames())
        self.parameterGraphControl.setXProbeEntriesModel(self.xProbeEntriesModel)

        self.yProbeEntriesModel = Models.ProbeEntries(self.campaigns.draw)
        self.yProbeEntriesModel.changeProbes(self.parameterGraphControl.yProbeNames())
        self.parameterGraphControl.setYProbeEntriesModel(self.yProbeEntriesModel)

    def on_figureConfig_scale_changed(self, value):
        self.parameterGraphControl.yProbesControl.confidenceparameterframe.setEnabled(self.graph.figureConfig.scale[2]=='linear')

    def on_drawCampaign_changed(self, campaign):
        Debug.printCall(self, campaign)
        self.simulationParametersModel.setCampaign(self.campaigns.draw,True)
        selectedXProbes = self.parameterGraphControl.xProbeNames()
        selectedYProbes = self.parameterGraphControl.yProbeNames()
        selectionModelX = self.parameterGraphControl.xProbesView().selectionModel()
        selectionModelY = self.parameterGraphControl.yProbesView().selectionModel()
        selectedYProbeEntry = self.parameterGraphControl.yProbeEntry.currentIndex()
        selectedXProbeEntry = self.parameterGraphControl.xProbeEntry.currentIndex()
        self.parameterGraphControl.xProbesView().clearSelection()
        self.parameterGraphControl.yProbesView().clearSelection()

        self.xProbesModel.setCampaign(self.campaigns.draw)
        self.yProbesModel.setCampaign(self.campaigns.draw)
        self.xProbeEntriesModel.setCampaign(self.campaigns.draw)
        self.yProbeEntriesModel.setCampaign(self.campaigns.draw)
        
        itemsToSelectX = self.xProbesModel.getProbeIndexes(selectedXProbes)
        for selection in itemsToSelectX:
            selectionModelX.setCurrentIndex(selection,QtGui.QItemSelectionModel.Select)
        self.parameterGraphControl.xProbesView().setSelectionModel(selectionModelX)

        itemsToSelectY = self.yProbesModel.getProbeIndexes(selectedYProbes)
        for selection in itemsToSelectY:
            selectionModelY.setCurrentIndex(selection,QtGui.QItemSelectionModel.Select)
        self.parameterGraphControl.yProbesView().setSelectionModel(selectionModelY)
        self.parameterGraphControl.yProbeEntry.setCurrentIndex(selectedYProbeEntry)
        self.parameterGraphControl.xProbeEntry.setCurrentIndex(selectedXProbeEntry)

    def getGraphs(self):
        import probeselector.Graphs

        dataacquisition = probeselector.dataacquisition
        campaign = self.campaigns.draw

        parameterName = self.parameterGraphControl.parameterName()

        graphs = list()
        errors = list()

        if self.parameterGraphControl.isAggregateParameter():
            assert(self.parameterGraphControl.isXUseProbeEntry(), False)
            assert(self.parameterGraphControl.isYUseProbeEntry(), True)

            xAcquirer = dataacquisition.Compose.ParameterValue(parameterName)

            yProbeNames = self.parameterGraphControl.yProbeNames()
            yProbeEntry = self.parameterGraphControl.yProbeEntryName()
            yAcquirer = dataacquisition.Compose.Probe(yProbeEntry)

            probeDataAcquirer = dataacquisition.Compose.XY(x = xAcquirer, y = yAcquirer, graphWriter = dataacquisition.Compose.aggregateGraphWriter)
            probeDataAcquirers = dict([(probeName, probeDataAcquirer) for probeName in yProbeNames])

            aggregationParameter = self.parameterGraphControl.aggregationParameter()
            parameterNames = list(campaign.getChangingParameterNames() - set([parameterName, aggregationParameter]))

            confidenceLevel = self.parameterGraphControl.getConfidenceLevel()
            showConfidenceLevel = self.parameterGraphControl.isShowConfidenceLevels()
            scenarioDataAcquirer = dataacquisition.Scenario(probeDataAcquirers, parameterNames, dataacquisition.Aggregator.Mean(yProbeEntry, confidenceLevel, showConfidenceLevel))

            self.showProgressBar()  
 
            graphsHelp, errorsHelp = self.acquireGraphs(scenarioDataAcquirer, graphClass = probeselector.Graphs.AggregatedGraph)

            graphs += graphsHelp
            errors += errorsHelp
            self.hideProgressBar()  
 
        if self.readerStopped:
            self.readerStopped = False
            return graphs
 
        if self.parameterGraphControl.isPlotNotAggregatedGraphs() or not self.parameterGraphControl.isAggregateParameter():
            if self.parameterGraphControl.isXUseProbeEntry():
                xProbeName = self.parameterGraphControl.xProbeNames()[0]
                xProbeEntry = self.parameterGraphControl.xProbeEntryName()
                xAcquirer = dataacquisition.Compose.ProbeEntryOfProbe(xProbeName, xProbeEntry)
            else:
                xAcquirer = dataacquisition.Compose.ParameterValue(parameterName)

            if self.parameterGraphControl.isYUseProbeEntry():
                yProbeNames = self.parameterGraphControl.yProbeNames()
                yProbeEntry = self.parameterGraphControl.yProbeEntryName()
                if self.parameterGraphControl.isShowConfidenceLevels() and yProbeEntry == 'mean':
                    yAcquirer = dataacquisition.Compose.Probe(yProbeEntry)
                    probeDataAcquirer = dataacquisition.Compose.XY(x = xAcquirer, y = yAcquirer, graphWriter = dataacquisition.Compose.aggregateGraphWriter)
                else:
                    yAcquirer = dataacquisition.Compose.ProbeEntry(yProbeEntry)
                    probeDataAcquirer = dataacquisition.Compose.XY(x = xAcquirer, y = yAcquirer)

                probeDataAcquirers = dict([(probeName, probeDataAcquirer)
                                           for probeName in yProbeNames])
            else:
                yAcquirer = dataacquisition.Compose.ParameterValue(parameterName)

                probeDataAcquirers = {None : dataacquisition.Compose.XY(x = xAcquirer, y = yAcquirer)}

            parameterNames = list(campaign.getChangingParameterNames() - set([parameterName]))

            if self.parameterGraphControl.isShowConfidenceLevels() and yProbeEntry == 'mean':
                confidenceLevel = self.parameterGraphControl.getConfidenceLevel()
                scenarioDataAcquirer = dataacquisition.Scenario(probeDataAcquirers, parameterNames, dataacquisition.Aggregator.WeightedMeanWithConfidenceInterval(confidenceLevel))

                self.showProgressBar()  
                graphsHelp, errorsHelp = self.acquireGraphs(scenarioDataAcquirer, graphClass = probeselector.Graphs.AggregatedGraph)

            else:
                scenarioDataAcquirer = dataacquisition.Scenario(probeDataAcquirers, parameterNames)

                #progressDialogue = Dialogues.Progress("Fetching graphs", 0, self.parentWidget())
                #progressDialogue.connect(progressDialogue, QtCore.SIGNAL("canceled()"),self.on_cancelClicked)

                self.showProgressBar()  
                graphsHelp, errorsHelp = self.acquireGraphs(scenarioDataAcquirer)

            graphs += graphsHelp
            errors += errorsHelp

            self.hideProgressBar() 
            if self.readerStopped:
                self.readerStopped = False

        return graphs

    def getExport(self):
        simParams=Models.SimulationParameters(self.campaigns.draw, onlyNumeric = False).getValueSelection()
        exp = Export(self.parameterGraphControl,simParams,self.graph)
        exp.paramName=self.parameterGraphControl.parameterName()
        exp.probeEntry=self.parameterGraphControl.yProbeEntryName()
        exp.graphs = self.getGraphs()
        exp.useXProbe = self.parameterGraphControl.isXUseProbeEntry()
        exp.useYProbe = self.parameterGraphControl.isYUseProbeEntry() 
        if exp.useXProbe :
            exp.xProbeName = self.parameterGraphControl.xProbeNames()[0]
            exp.xProbeEntry =  self.parameterGraphControl.xProbeEntryName()
        exp.graphType="Param" 
        exp.confidenceLevel = self.parameterGraphControl.getConfidenceLevel()
        exp.campaignId = self.campaignId

        return exp

from ui.Windows_ProbeInfo_ui import Ui_Windows_ProbeInfo
class ProbeInfo(QtGui.QWidget, Ui_Windows_ProbeInfo):

    def __init__(self, campaign, probeName, *qwidgetArgs):
        QtGui.QWidget.__init__(self, *qwidgetArgs)
        self.setupUi(self)

        self.campaign = campaign
        self.probeName = probeName
        self.setWindowTitle("Probe Info: " + probeName)

        self.model = Models.ProbeData(campaign, probeName)
        self.view.setModel(self.model)
        self.view.addAction(self.actionDisplayErrAndOut)
        for column in xrange(self.model.columnCount()):
            self.view.resizeColumnToContents(column)

    @QtCore.pyqtSignature("")
    def on_actionDisplayErrAndOut_triggered(self):
        def getFileLines(fileName, maxSize):
            f = open(fileName, "r")
            maxChars = int(maxSize)
            size= os.path.getsize(fileName)
            isHuge = False
            if size > maxChars :
                f.seek(maxChars*-1, os.SEEK_END)
                isHuge = True
            return f.readlines(), isHuge

        path=self.view.model().getPath(self.view.currentIndex())
        if path is None:
            QtGui.QMessageBox.information(self, "Error encountered", "Either the scenario is crashed/not terminated or the scenario was queued with an old version of simcontrol. Hence, the database does not contain the correct path to the scenario directory")
        else:
            errFile = path + "/stderr"
            outFile = path + "/stdout"

            listWidget = QtGui.QListWidget(self)
            try :
                stderr_data=file(errFile).readlines()
                item =QtGui.QListWidgetItem("stderr:")
                item.setTextAlignment(QtCore.Qt.AlignHCenter)
                item.setBackgroundColor(QtCore.Qt.yellow)
                listWidget.addItem(item)
                for line in stderr_data :
                    listWidget.addItem(QtGui.QListWidgetItem(line))
            except:
                QtGui.QMessageBox.information(self, "Error encountered", "stderr file is missing or you have no read permission")

            try :
                maxSize = 1e6
                stdout_data, isHuge =getFileLines(outFile, maxSize) 
                if isHuge :
                    message = "only displaying last "+str(int(maxSize))+" characters of the stdout file"
                    QtGui.QMessageBox.information(self, "Big file", message)

                item =QtGui.QListWidgetItem("stdout:")
                item.setTextAlignment(QtCore.Qt.AlignHCenter)
                item.setBackgroundColor(QtCore.Qt.yellow)
                listWidget.addItem(item)
                for line in stdout_data :
                    listWidget.addItem(QtGui.QListWidgetItem(line))
            except:
                QtGui.QMessageBox.information(self, "Error encountered", "stdout file is missing or you have no read permission")

            if  'stderr_data' in locals() or 'stdout_data' in locals() : 
                dialog = QtGui.QDialog(self)
                layout = QtGui.QVBoxLayout()
                layout.addWidget(listWidget)
                dialog.setLayout(layout)
                dialog.showMaximized()

