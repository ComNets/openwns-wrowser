import os

from PyQt4 import QtCore, QtGui

import pywns.probeselector.Errors

import Dialogues
import Widgets
import Models
import scenario.plotterFactory
from Tools import Observable, Observing

import Debug


from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg
import matplotlib.figure
from PyQt4 import QtGui, QtCore

class FigureCanvas(FigureCanvasQTAgg):
    """This class implements a QT Widget on which you can draw using the
    MATLAB(R)-style commands provided by matplotlib
    """
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = matplotlib.figure.Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        self.axes.hold(False)

        FigureCanvasQTAgg.__init__(self, self.fig)

        FigureCanvasQTAgg.setSizePolicy(self,
                                   QtGui.QSizePolicy.Expanding,
                                   QtGui.QSizePolicy.Expanding)
        FigureCanvasQTAgg.updateGeometry(self)

    def sizeHint(self):
        w, h = self.get_width_height()
        return QtCore.QSize(w, h)

    def minimumSizeHint(self):
        return QtCore.QSize(10, 10)

from ui.Windows_Main_ui import Ui_Windows_Main
class Main(QtGui.QMainWindow, Ui_Windows_Main):

    class CancelFlag:
        cancelled = False

    def __init__(self, *args):
        QtGui.QMainWindow.__init__(self, *args)
        self.setupUi(self)

        self.campaigns = Observable()
        self.reader = None

        self.workspace = QtGui.QWorkspace(self)
        self.setCentralWidget(self.workspace)

        self.windowMapper = QtCore.QSignalMapper(self)
        self.connect(self.windowMapper, QtCore.SIGNAL("mapped(QWidget *)"),
                     self.workspace, QtCore.SLOT("setActiveWindow(QWidget *)"))

        # currently disabled
        self.actionCloseFigure.setVisible(False)
        self.actionConfigure.setVisible(False)
        self.actionRefresh.setVisible(False)

    @QtCore.pyqtSignature("")
    def on_actionView_Scenario_triggered(self):
        
        filename = QtGui.QFileDialog.getOpenFileName(
            self.workspace,
            "Open File",
            os.getcwd(),
            "Config Files (*.py)")

        globals = {}
        exec("import sys",globals)
        exec("sys.path.append('/home/dbn/src/wns/openWNS--main--1.0/sandbox/dbg/lib/PyConfig')", globals)

        file = open(str(filename), "r")
        content = file.read()
        file.close()

        exec(content,globals)

        p = scenario.plotterFactory.create(globals)
        if p is not None:
            canvas = FigureCanvas(self.workspace)
            self.workspace.addWindow(canvas)
            p.plotScenario(canvas)
            canvas.showMaximized()
        else:
            QtGui.QMessageBox.critical(self,
                                       "No scenario found",
                                       "Make sure the scenario is accessible in the global namespace via a variable named 'scenario'")


    @QtCore.pyqtSignature("")
    def on_actionOpenDatabase_triggered(self):
        from pywns.probeselector import SQLReaders, Representations, Interface

        databaseDialogue = Dialogues.OpenDatabase(self.workspace)
        if databaseDialogue.exec_() == QtGui.QDialog.Accepted:
            uri = databaseDialogue.getURI(withPassword = True)
            noPasswordUri = databaseDialogue.getURI(withPassword = False)
            self.reader = SQLReaders.CampaignReader(uri,
                                                    Interface.DoNotSelectProbeSelectUI(),
                                                    Dialogues.Progress("Reading data", 0, self.workspace).setCurrentAndMaximum,
                                                    True)
            campaign = Representations.Campaign(*self.reader.read())
            self.campaigns.original = Interface.Facade(campaign)

            self.simulationParameters = SimulationParameters(self.campaigns, self)
            self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.simulationParameters)
            self.menuNew.setEnabled(True)
            self.actionOpenDatabase.setEnabled(False)
            self.actionOpenCampaignDatabase.setEnabled(False)
            self.actionOpenDSV.setEnabled(False)
            self.actionOpenDirectory.setEnabled(False)
            self.actionCloseDataSource.setEnabled(True)

    @QtCore.pyqtSignature("")
    def on_actionOpenCampaignDatabase_triggered(self):
        from pywns.simdb import Campaigns
        from pywns.probeselector import PostgresReader, Representations, Interface

        campaignDbDialogue = Dialogues.OpenCampaignDb(self.workspace)
        self.workspace.addWindow(campaignDbDialogue)
        campaignDbDialogue.showMaximized()
        if campaignDbDialogue.exec_() == QtGui.QDialog.Accepted:
            campaignId = campaignDbDialogue.getCampaign()
            Campaigns.setCampaign([campaignId])
            self.reader = PostgresReader.CampaignReader(campaignId,
                                                        None,
                                                        Dialogues.Progress("Reading data", 0, self.workspace).setCurrentAndMaximum,
                                                        True)
            campaign = Representations.Campaign(*self.reader.read())
            self.campaigns.original = Interface.Facade(campaign)

            self.simulationParameters = SimulationParameters(self.campaigns, self)
            self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.simulationParameters)
            self.menuNew.setEnabled(True)
            self.actionOpenDatabase.setEnabled(False)
            self.actionOpenCampaignDatabase.setEnabled(False)
            self.actionOpenDSV.setEnabled(False)
            self.actionOpenDirectory.setEnabled(False)
            self.actionCloseDataSource.setEnabled(True)

    @QtCore.pyqtSignature("")
    def on_actionOpenDSV_triggered(self):
        from pywns.probeselector import DSVReaders, Representations, Interface

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
                self.actionOpenDatabase.setEnabled(False)
                self.actionOpenCampaignDatabase.setEnabled(False)
                self.actionOpenDSV.setEnabled(False)
                self.actionOpenDirectory.setEnabled(False)
                self.actionCloseDataSource.setEnabled(True)


    @QtCore.pyqtSignature("")
    def on_actionOpenDirectory_triggered(self):
        self.directoryNavigation = DirectoryNavigation(self.campaigns, os.getcwd(), self)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.directoryNavigation)
        self.actionOpenDatabase.setEnabled(False)
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
        for window in self.workspace.windowList():
            window.close()
        self.campaigns = Observable()
        self.actionOpenDatabase.setEnabled(True)
        self.actionOpenCampaignDatabase.setEnabled(True)
        self.actionOpenDSV.setEnabled(True)
        self.actionOpenDirectory.setEnabled(True)
        self.actionCloseDataSource.setEnabled(False)
        self.actionNewParameter.setEnabled(True)
        self.menuNew.setEnabled(False)

    @QtCore.pyqtSignature("")
    def on_actionRefresh_triggered(self):
        from pywns.probeselector import Representations, Interface

        if self.reader != None:
            self.campaigns.original = Interface.Facade(Representations.Campaign(*self.reader.read()))

    @QtCore.pyqtSignature("")
    def on_actionNewLogEval_triggered(self):
        figureWindow = LogEvalFigure(self.campaigns, self.menuFigure, self.workspace)
        self.workspace.addWindow(figureWindow)
        figureWindow.show()

    @QtCore.pyqtSignature("")
    def on_actionNewTimeSeries_triggered(self):
        figureWindow = TimeSeriesFigure(self.campaigns, self.menuFigure, self.workspace)
        self.workspace.addWindow(figureWindow)
        figureWindow.show()

    @QtCore.pyqtSignature("")
    def on_actionNewXDF_triggered(self):
        figureWindow = XDFFigure(self.campaigns, self.menuFigure, self.workspace)
        self.workspace.addWindow(figureWindow)
        figureWindow.show()

    @QtCore.pyqtSignature("")
    def on_actionNewLRE_triggered(self):
        figureWindow = LREFigure(self.campaigns, self.menuFigure, self.workspace)
        self.workspace.addWindow(figureWindow)
        figureWindow.show()

    @QtCore.pyqtSignature("")
    def on_actionNewBatchMeans_triggered(self):
        figureWindow = BatchMeansFigure(self.campaigns, self.menuFigure, self.workspace)
        self.workspace.addWindow(figureWindow)
        figureWindow.show()

    @QtCore.pyqtSignature("")
    def on_actionNewTable_triggered(self):
        figureWindow = TableFigure(self.campaigns, self.menuFigure, self.workspace)
        self.workspace.addWindow(figureWindow)
        figureWindow.show()

    @QtCore.pyqtSignature("")
    def on_actionNewParameter_triggered(self):
        figureWindow = ParameterFigure(self.campaigns, self.menuFigure, self.workspace)
        self.workspace.addWindow(figureWindow)
        figureWindow.show()

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
                except pywns.probeselector.Errors.InvalidFilterExpression:
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
            for row in xrange(self.simulationParametersModel.rowCount()):
                self.simulationParametersView.setExpanded(self.simulationParametersModel.index(row, 0), True)

        @QtCore.pyqtSignature("const QString&")
        def on_filterEdit_textEdited(self, text):
            self.filterCampaigns()

        @QtCore.pyqtSignature("const QModelIndex&, const QModelIndex&")
        def on_simulationParametersModel_dataChanged(self, topLeft, bottomRight):
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

    def __init__(self, campaigns, *args):
        QtGui.QDockWidget.__init__(self, "Simulation Parameters", *args)
        self.internalWidget = self.__class__.Widget(campaigns)
        self.setWidget(self.internalWidget)


class DirectoryNavigation(QtGui.QDockWidget):

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
            from pywns.probeselector import DirectoryReaders, Representations, Interface

            directory = str(self.rootEdit.text())
            progressDialogue = Dialogues.Progress("Reading data", 0, self)
            campaign = Representations.Campaign(*DirectoryReaders.CampaignReader(directory,
                                                                                 progressDialogue.setCurrentAndMaximum).read())
            progressDialogue.close()
            self.campaigns.draw = Interface.Facade(campaign)
            self.scanInfoLabel.setText(str(len(self.campaigns.draw.getScenarios())) + " directories with probes.")
            self.mainWindow.menuNew.setEnabled(True)
            self.mainWindow.actionNewParameter.setEnabled(False)

    def __init__(self, campaigns, root, parent, *args):
        QtGui.QDockWidget.__init__(self, "Directory Navigation", parent, *args)
        self.internalWidget = self.__class__.Widget(campaigns, root, parent, self)
        self.setWidget(self.internalWidget)

from ui.Windows_Figure_ui import Ui_Windows_Figure
class Figure(QtGui.QWidget, Ui_Windows_Figure, Observing):

    def __init__(self, campaigns, menu, windowTitle, *qwidgetArgs):
        QtGui.QWidget.__init__(self, *qwidgetArgs)
        self.setupUi(self)

        self.campaigns = campaigns
        self.menu = menu

        self.setWindowTitle(windowTitle)
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
        from pywns.probeselector import Exporters

        formatDialogue = Dialogues.SelectItem("Export Format", "Select format", Exporters.directory.keys(), self, Dialogues.SelectItem.RadioButtons)
        if formatDialogue.exec_() == QtGui.QDialog.Accepted:
            format = formatDialogue.selectedText()
            fileDialogue = QtGui.QFileDialog(self, "Export to " + format + " file", os.getcwd(), "Files (*.*)")
            fileDialogue.setAcceptMode(QtGui.QFileDialog.AcceptSave)
            fileDialogue.setFileMode(QtGui.QFileDialog.AnyFile)
            if fileDialogue.exec_() == QtGui.QDialog.Accepted:
                filename = str(fileDialogue.selectedFiles()[0])
                progressDialogue = Dialogues.Progress("Exporting to " + filename, 0)
                Exporters.directory[format].export(filename, self.getGraphs(), progressDialogue.setCurrentAndMaximum, progressDialogue.reset)

    @QtCore.pyqtSignature("bool")
    def on_draw_clicked(self, checked):
        self.graph.setGraphs(self.getGraphs())

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
        self.configure.setVisible(False)
        self.export.setVisible(False)

class ProbeFigure(Figure):

    def __init__(self, campaigns, menu, *qwidgetArgs):
        Figure.__init__(self, campaigns, menu, *qwidgetArgs)
        self.probeGraphControl = Widgets.ProbeGraphControl(self.graphControl)
        self.graphControlLayout.addWidget(self.probeGraphControl)

        self.probesModel = Models.ProbeNames(self.campaigns.draw, self.getProbeTypes())
        self.probeGraphControl.setModel(self.probesModel)

    def on_drawCampaign_changed(self, campaign):
        self.probesModel.setCampaign(self.campaigns.draw)

class LogEvalFigure(ProbeFigure, LineGraphs):

    def __init__(self, campaigns, menu, *qwidgetArgs):
        ProbeFigure.__init__(self, campaigns, menu, "LogEval Probe Figure", *qwidgetArgs)
        LineGraphs.__init__(self)
        self.graph.figureConfig.title = "LogEval Probe Figure"

    @staticmethod
    def getProbeTypes():
        import pywns.Probe
        return [pywns.Probe.LogEvalProbe]

    def getGraphs(self):
        dataacquisition = pywns.probeselector.dataacquisition
        campaign = self.campaigns.draw

        probeNames = self.probeGraphControl.probeNames()

        probeDataAcquirer = dataacquisition.Probe.LogEval()
        probeDataAcquirers = dict([(probeName, probeDataAcquirer) for probeName in probeNames])

        parameterNames = list(campaign.getChangingParameterNames())

        scenarioDataAcquirer = dataacquisition.Scenario(probeDataAcquirers = probeDataAcquirers,
                                                        parameterNames = parameterNames)

        progressDialogue = Dialogues.Progress("Fetching graphs", 0, self.parentWidget())

        graphs, errors = campaign.acquireGraphs(acquireScenarioData = scenarioDataAcquirer,
                                                progressNotify = progressDialogue.setCurrentAndMaximum,
                                                progressReset = progressDialogue.reset)

        return graphs

class TimeSeriesFigure(ProbeFigure, LineGraphs):

    def __init__(self, campaigns, menu, *qwidgetArgs):
        ProbeFigure.__init__(self, campaigns, menu, "TimeSeries Probe Figure", *qwidgetArgs)
        LineGraphs.__init__(self)
        self.graph.figureConfig.title = "TimeSeries Probe Figure"

    @staticmethod
    def getProbeTypes():
        import pywns.Probe
        return [pywns.Probe.TimeSeriesProbe]

    def getGraphs(self):
        dataacquisition = pywns.probeselector.dataacquisition
        campaign = self.campaigns.draw

        probeNames = self.probeGraphControl.probeNames()

        probeDataAcquirer = dataacquisition.Probe.TimeSeries()
        probeDataAcquirers = dict([(probeName, probeDataAcquirer) for probeName in probeNames])

        parameterNames = list(campaign.getChangingParameterNames())

        scenarioDataAcquirer = dataacquisition.Scenario(probeDataAcquirers = probeDataAcquirers,
                                                        parameterNames = parameterNames)

        progressDialogue = Dialogues.Progress("Fetching graphs", 0, self.parentWidget())

        graphs, errors = campaign.acquireGraphs(acquireScenarioData = scenarioDataAcquirer,
                                                progressNotify = progressDialogue.setCurrentAndMaximum,
                                                progressReset = progressDialogue.reset)

        return graphs

class XDFFigure(ProbeFigure, LineGraphs):

    def __init__(self, campaigns, menu, *qwidgetArgs):
        ProbeFigure.__init__(self, campaigns, menu, "PDF/CDF/CCDF Probe Figure", *qwidgetArgs)
        LineGraphs.__init__(self)
        self.graph.figureConfig.title = "PDF/CDF/CCDF Probe Figure"

        self.probeGraphControl.setProbeFunctions(["PDF", "CDF", "CCDF"], initialIndex = 1)

    @staticmethod
    def getProbeTypes():
        import pywns.Probe
        return [pywns.Probe.PDFProbe]

    def getGraphs(self):
        dataacquisition = pywns.probeselector.dataacquisition
        campaign = self.campaigns.draw

        funType = self.probeGraphControl.probeFunction()
        probeNames = self.probeGraphControl.probeNames()

        probeDataAcquirer = getattr(dataacquisition.Probe, funType)()
        probeDataAcquirers = dict([(probeName, probeDataAcquirer) for probeName in probeNames])

        parameterNames = list(campaign.getChangingParameterNames())

        scenarioDataAcquirer = dataacquisition.Scenario(probeDataAcquirers = probeDataAcquirers,
                                                        parameterNames = parameterNames)

        progressDialogue = Dialogues.Progress("Fetching graphs", 0, self.parentWidget())

        graphs, errors = campaign.acquireGraphs(acquireScenarioData = scenarioDataAcquirer,
                                                progressNotify = progressDialogue.setCurrentAndMaximum,
                                                progressReset = progressDialogue.reset)

        return graphs

class LREFigure(ProbeFigure, LineGraphs):

    def __init__(self, campaigns, menu, *qwidgetArgs):
        ProbeFigure.__init__(self, campaigns, menu, "(D)LRE Probe Figure", *qwidgetArgs)
        LineGraphs.__init__(self)
        self.graph.figureConfig.title = "(D)LRE Probe Figure"

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
        import pywns.Probe
        return [pywns.Probe.LreProbe, pywns.Probe.DlreProbe]

    def getGraphs(self):
        dataacquisition = pywns.probeselector.dataacquisition
        campaign = self.campaigns.draw

        yAxis = self.probeGraphControl.probeFunction()
        probeNames = self.probeGraphControl.probeNames()

        probeDataAcquirer = getattr(dataacquisition.Probe, self.probeFunAcMap[yAxis])()
        probeDataAcquirers = dict([(probeName, probeDataAcquirer) for probeName in probeNames])

        parameterNames = list(campaign.getChangingParameterNames())

        scenarioDataAcquirer = dataacquisition.Scenario(probeDataAcquirers = probeDataAcquirers,
                                                        parameterNames = parameterNames)

        progressDialogue = Dialogues.Progress("Fetching graphs", 0, self.parentWidget())

        graphs, errors = campaign.acquireGraphs(acquireScenarioData = scenarioDataAcquirer,
                                                progressNotify = progressDialogue.setCurrentAndMaximum,
                                                progressReset = progressDialogue.reset)

        return graphs

class BatchMeansFigure(ProbeFigure, LineGraphs):

    def __init__(self, campaigns, menu, *qwidgetArgs):
        ProbeFigure.__init__(self, campaigns, menu, "BatchMeans Probe Figure", *qwidgetArgs)
        LineGraphs.__init__(self)
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
        import pywns.Probe
        return [pywns.Probe.BatchMeansProbe]

    def getGraphs(self):
        dataacquisition = pywns.probeselector.dataacquisition
        campaign = self.campaigns.draw

        yAxis = self.probeGraphControl.probeFunction()
        probeNames = self.probeGraphControl.probeNames()

        probeDataAcquirer = getattr(dataacquisition.Probe, self.probeFunAcMap[yAxis])()
        probeDataAcquirers = dict([(probeName, probeDataAcquirer) for probeName in probeNames])

        parameterNames = list(campaign.getChangingParameterNames())

        scenarioDataAcquirer = dataacquisition.Scenario(probeDataAcquirers = probeDataAcquirers,
                                                        parameterNames = parameterNames)

        progressDialogue = Dialogues.Progress("Fetching graphs", 0, self.parentWidget())

        graphs, errors = campaign.acquireGraphs(acquireScenarioData = scenarioDataAcquirer,
                                                progressNotify = progressDialogue.setCurrentAndMaximum,
                                                progressReset = progressDialogue.reset)

        return graphs

class TableFigure(ProbeFigure, TableGraphs):

    def __init__(self, campaigns, menu, *qwidgetArgs):
        ProbeFigure.__init__(self, campaigns, menu, "Table Probe Figure", *qwidgetArgs)
        TableGraphs.__init__(self)

    @staticmethod
    def getProbeTypes():
        import pywns.Probe
        return [pywns.Probe.TableProbe]

    def getGraphs(self):
        import pywns.probeselector.Graphs

        dataacquisition = pywns.probeselector.dataacquisition
        campaign = self.campaigns.draw

        probeNames = self.probeGraphControl.probeNames()

        probeDataAcquirer = dataacquisition.Probe.Table()
        probeDataAcquirers = dict([(probeName, probeDataAcquirer) for probeName in probeNames])

        parameterNames = list(campaign.getChangingParameterNames())

        scenarioDataAcquirer = dataacquisition.Scenario(probeDataAcquirers = probeDataAcquirers,
                                                        parameterNames = parameterNames)

        progressDialogue = Dialogues.Progress("Fetching graphs", 0, self.parentWidget())

        graphs, errors = campaign.acquireGraphs(acquireScenarioData = scenarioDataAcquirer,
                                                progressNotify = progressDialogue.setCurrentAndMaximum,
                                                progressReset = progressDialogue.reset,
                                                graphClass = pywns.probeselector.Graphs.TableGraph)

        return graphs

class ParameterFigure(Figure, LineGraphs):

    def __init__(self, campaigns, menu, *qwidgetArgs):
        Figure.__init__(self, campaigns, menu, "Parameter Figure", *qwidgetArgs)
        LineGraphs.__init__(self)
        self.graph.figureConfig.title = "Parameter Figure"

        self.parameterGraphControl = Widgets.ParameterGraphControl(self.graphControl)
        self.graphControlLayout.addWidget(self.parameterGraphControl)

        self.simulationParametersModel = Models.SimulationParameters(self.campaigns.draw, onlyNumeric = True)
        self.parameterGraphControl.setSimulationParametersModel(self.simulationParametersModel)

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

    def on_drawCampaign_changed(self, campaign):
        self.simulationParametersModel.setCampaign(self.campaigns.draw)
        self.xProbesModel.setCampaign(self.campaigns.draw)
        self.yProbesModel.setCampaign(self.campaigns.draw)
        self.xProbeEntriesModel.setCampaign(self.campaigns.draw)
        self.yProbeEntriesModel.setCampaign(self.campaigns.draw)

    def getGraphs(self):
        dataacquisition = pywns.probeselector.dataacquisition
        campaign = self.campaigns.draw

        parameterName = self.parameterGraphControl.parameterName()

        if self.parameterGraphControl.isXUseProbeEntry():
            xProbeName = self.parameterGraphControl.xProbeNames()[0]
            xProbeEntry = self.parameterGraphControl.xProbeEntryName()
            xAcquirer = dataacquisition.Compose.ProbeEntryOfProbe(xProbeName, xProbeEntry)
        else:
            xAcquirer = dataacquisition.Compose.ParameterValue(parameterName)

        if self.parameterGraphControl.isYUseProbeEntry():
            yProbeNames = self.parameterGraphControl.yProbeNames()
            yProbeEntry = self.parameterGraphControl.yProbeEntryName()
            yAcquirer = dataacquisition.Compose.ProbeEntry(yProbeEntry)

            probeDataAcquirer = dataacquisition.Compose.XY(x = xAcquirer, y = yAcquirer)
            probeDataAcquirers = dict([(probeName, probeDataAcquirer)
                                       for probeName in yProbeNames])
        else:
            yAcquirer = dataacquisition.Compose.ParameterValue(parameterName)

            probeDataAcquirers = {None : dataacquisition.Compose.XY(x = xAcquirer, y = yAcquirer)}

        parameterNames = list(campaign.getChangingParameterNames() - set([parameterName]))
        scenarioDataAcquirer = dataacquisition.Scenario(probeDataAcquirers, parameterNames)

        progressDialogue = Dialogues.Progress("Fetching graphs", 0, self.parentWidget())

        graphs, errors = campaign.acquireGraphs(acquireScenarioData = scenarioDataAcquirer,
                                                progressNotify = progressDialogue.setCurrentAndMaximum,
                                                progressReset = progressDialogue.reset)

        return graphs

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
        for column in xrange(self.model.columnCount()):
            self.view.resizeColumnToContents(column)

