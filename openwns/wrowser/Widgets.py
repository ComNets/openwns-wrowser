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

from PyQt4 import QtCore, QtGui

import Debug
import Data
import Models
from Tools import Observing

class ValidStateMarkingLineEdit(QtGui.QLineEdit):

    def __init__(self, parent = None, *args):
        QtGui.QLineEdit.__init__(self, parent, *args)
        self.connect(self, QtCore.SIGNAL("textChanged(const QString&)"),
                     self.checkState)

    @QtCore.pyqtSignature("const QString&")
    def checkState(self, text):
        Debug.printCall(self, text)
        palette = QtGui.QPalette(QtGui.QApplication.palette())
        if not self.hasAcceptableInput():
            palette.setColor(self.backgroundRole(), QtGui.QColor(255, 64, 64))
        self.setPalette(palette)

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg
class FigureCanvas(FigureCanvasQTAgg):

    def __init__(self, parent=None, width = 5, height = 4, dpi = 100):
        from matplotlib.figure import Figure

        self.fig = Figure(figsize = (width, height),
                          dpi = dpi)
        self.axes = self.fig.add_subplot(111)
        self.axes.hold(True)

        FigureCanvasQTAgg.__init__(self, self.fig)

        FigureCanvasQTAgg.setSizePolicy(self,
                                        QtGui.QSizePolicy.Expanding,
                                        QtGui.QSizePolicy.Expanding)
        FigureCanvasQTAgg.updateGeometry(self)

    def sizeHint(self):
        w, h, = self.get_width_height()
        return QtCore.QSize(w, h)

    def minimumSizeHint(self):
        return QtCore.QSize(10, 10)

from ui.Widgets_ProbeGraphControl_ui import Ui_Widgets_ProbeGraphControl
class ProbeGraphControl(QtGui.QWidget, Ui_Widgets_ProbeGraphControl):

    def __init__(self, *args):
        QtGui.QWidget.__init__(self, *args)
        self.setupUi(self)

        self.probes.addAction(self.actionDisplayProbeInfo)

        self.aggregatecheckBox.setChecked(False)
        self.connect(self.aggregatecheckBox, QtCore.SIGNAL("clicked()"), self.on_aggregatecheckBox_setchecked)
        self.connect(self.confidencecheckBox, QtCore.SIGNAL("clicked()"), self.on_confidencecheckBox_setchecked)
        self.aggregateparameterframe.setEnabled(False)
        self.confidenceparameterframe.setEnabled(False)
        self.originalgraphcheckBox.setChecked(False)
        self.confidencecheckBox.setChecked(False)

        self.connect(self.probeFilter, QtCore.SIGNAL("textEdited(const QString&)"), self.on_probeFilter_textEdited)
        self.setProbeFunctions([])
        self.probeInfoWindows = list()
    def on_aggregatecheckBox_setchecked(self):
        if self.aggregatecheckBox.isChecked():
            self.aggregateparameterframe.setEnabled(True)
            self.confidenceparameterframe.setEnabled(True)
            self.confidenceLevel.setEnabled(False)
            self.confidencelevellabel.setEnabled(False)
        else:
            self.aggregateparameterframe.setEnabled(False)
            self.originalgraphcheckBox.setChecked(False)
            self.confidenceparameterframe.setEnabled(False)
            self.confidencecheckBox.setChecked(False)

    def on_confidencecheckBox_setchecked(self):
        if self.confidencecheckBox.isChecked():
            self.confidenceLevel.setEnabled(True)
            self.confidencelevellabel.setEnabled(True)
        else:
            self.confidenceLevel.setEnabled(False)
            self.confidencelevellabel.setEnabled(False)

    def isShowConfidenceLevels(self):
        return self.confidencecheckBox.isChecked()

    def setModel(self, model):
        from Tools import ProbeFilterValidator
        self.probes.setModel(model)
        self.probes.selectionModel().select(model.index(0, 0),
                                            QtGui.QItemSelectionModel.Select)
        self.probeFilterValidator = ProbeFilterValidator(model, self)
        self.probeFilter.setValidator(self.probeFilterValidator)

    def setAggregateParametersModel(self, model):
        self.aggregateParameter.setModelColumn(0)
        self.aggregateParameter.setModel(model)

    def setProbeFunctions(self, probeFunctions, initialIndex = 0):
        if len(probeFunctions) == 0:
            self.probeFunctions.clear()
            self.probeFunctions.setVisible(False)
        else:
            for item in probeFunctions:
                self.probeFunctions.addItem(str(item))
            self.probeFunctions.setCurrentIndex(initialIndex)
            self.probeFunctions.setVisible(True)

    def probeFunction(self):
        return str(self.probeFunctions.currentText())

    def probeNames(self):
        names = []
        for index in self.probes.selectionModel().selectedIndexes():
            names.append(self.probes.model().getProbeName(index))
        return names

    def probesView(self):
        return self.probes

    @QtCore.pyqtSignature("")
    def on_actionDisplayProbeInfo_triggered(self):
        from Windows import ProbeInfo
        campaign = self.probes.model().campaign
        probeName = self.probes.model().getProbeName(self.probes.currentIndex())
        probeInfo = ProbeInfo(campaign, probeName)
        self.probeInfoWindows.append(probeInfo)
        probeInfo.show()

    @QtCore.pyqtSignature("const QString&")
    def on_probeFilter_textEdited(self, text):
        Debug.printCall(self, str(text))
        if self.probeFilter.hasAcceptableInput():
            self.probes.model().setFilter(str(text))

    def isAggregateParameter(self):
        return self.aggregatecheckBox.isChecked()

    def aggregationParameter(self):
        return str(self.aggregateParameter.currentText())

    def isPlotNotAggregatedGraphs(self):
        return self.originalgraphcheckBox.isChecked()

    def getSelectedProbeName(self):
        return self.probes.model().getProbeName(self.probes.currentIndex()) #"testPDF_Probe"

    def getAllSelectedProbeNames(self):
        return self.probeNames()


from ui.Widgets_ParameterGraphControl_ui import Ui_Widgets_ParameterGraphControl
class ParameterGraphControl(QtGui.QWidget, Ui_Widgets_ParameterGraphControl):

    def __init__(self, *qwidgetArgs):
        QtGui.QWidget.__init__(self, *qwidgetArgs)
        self.setupUi(self)

        self.connect(self.simulationParameter , QtCore.SIGNAL("activated(parameterName)"), self.on_simulationParameter_activated)

        self.xUseParameterValue.setChecked(True)
        self.on_xUseProbeEntry_toggled(False)
        self.yUseProbeEntry.setChecked(True)
        self.on_yUseProbeEntry_toggled(True)
        self.xyTab.setCurrentIndex(1)
        self.xProbesControl.aggregateframe.setVisible(False)

    @QtCore.pyqtSignature("QString")
    def on_simulationParameter_activated(self, parameterName):
        aggrParam = self.yProbesControl.aggregateParameter.currentText()
        self.aggregateParametersModel =  Models.SimulationParameters(self.yProbesControl.probeFilterValidator.probesModel.campaign, onlyNumeric = True)
        self.aggregateParametersModel.parameterNames.remove(parameterName)
        self.setAggregateParametersModel(self.aggregateParametersModel)
        if aggrParam != parameterName :
            for index in range(self.yProbesControl.aggregateParameter.count()) :
                self.yProbesControl.aggregateParameter.setCurrentIndex(index)     
                if self.yProbesControl.aggregateParameter.currentText() == aggrParam :
                    break

    @QtCore.pyqtSignature("bool")
    def on_xUseProbeEntry_toggled(self, checked):
        self.xProbesControl.setEnabled(checked)
        self.xProbeEntry.setEnabled(checked)
        if self.xUseProbeEntry.isChecked() or self.yUseParameterValue.isChecked():
            self.yProbesControl.aggregatecheckBox.setChecked(False)
            self.yProbesControl.aggregateframe.setEnabled(False)
            self.yProbesControl.confidencecheckBox.setChecked(False)
            self.yProbesControl.originalgraphcheckBox.setChecked(False)
        else:
            self.yProbesControl.aggregateframe.setEnabled(True)
            self.yProbesControl.aggregateparameterframe.setEnabled(False)
            self.yProbesControl.confidenceparameterframe.setEnabled(False)

    @QtCore.pyqtSignature("bool")
    def on_yUseProbeEntry_toggled(self, checked):
        self.yProbesControl.setEnabled(checked)
        self.yProbeEntry.setEnabled(checked)
        if self.xUseProbeEntry.isChecked() or self.yUseParameterValue.isChecked():
            self.yProbesControl.aggregatecheckBox.setChecked(False)
            self.yProbesControl.aggregateframe.setEnabled(False)
            self.yProbesControl.confidencecheckBox.setChecked(False)
            self.yProbesControl.originalgraphcheckBox.setChecked(False)
        else:
            self.yProbesControl.aggregateframe.setEnabled(True)
            self.yProbesControl.aggregateparameterframe.setEnabled(False)
            self.yProbesControl.confidenceparameterframe.setEnabled(False)

    @QtCore.pyqtSignature("const QItemSelection&, const QItemSelection&")
    def on_xProbes_selectionChanged(self, selected, deselected):
        selectedEntry = self.xProbeEntryName()
        self.xProbeEntry.model().changeProbes(self.xProbeNames())
        self.xProbeEntry.setCurrentIndex(self.xProbeEntry.model().findProbeEntry(selectedEntry))

    @QtCore.pyqtSignature("const QItemSelection&, const QItemSelection&")
    def on_yProbes_selectionChanged(self, selected, deselected):
        selectedEntry = self.yProbeEntryName()
        self.yProbeEntry.model().changeProbes(self.yProbeNames())
        self.yProbeEntry.setCurrentIndex(self.yProbeEntry.model().findProbeEntry(selectedEntry))

    def setSimulationParametersModel(self, model):
        self.simulationParameter.setModelColumn(0)
        self.simulationParameter.setModel(model)

    def setAggregateParametersModel(self, model):
        self.yProbesControl.aggregateParameter.setModelColumn(0)
        self.yProbesControl.aggregateParameter.setModel(model)

    def setXProbesModel(self, model):
        self.xProbesControl.setModel(model)
        self.connect(self.xProbesView().selectionModel(), QtCore.SIGNAL("selectionChanged(const QItemSelection&, const QItemSelection&)"),
                     self.on_xProbes_selectionChanged)

    def setYProbesModel(self, model):
        self.yProbesControl.setModel(model)
        self.connect(self.yProbesView().selectionModel(), QtCore.SIGNAL("selectionChanged(const QItemSelection&, const QItemSelection&)"),
                     self.on_yProbes_selectionChanged)

    def setXProbeEntriesModel(self, model):
        self.xProbeEntry.setModelColumn(0)
        self.xProbeEntry.setModel(model)
        self.xProbeEntriesView().setCurrentIndex(model.findProbeEntry("mean"))

    def setYProbeEntriesModel(self, model):
        self.yProbeEntry.setModelColumn(0)
        self.yProbeEntry.setModel(model)
        self.yProbeEntriesView().setCurrentIndex(model.findProbeEntry("mean"))

    def parameterName(self):
        return str(self.simulationParameter.currentText())

    def isXUseProbeEntry(self):
        return self.xUseProbeEntry.isChecked()

    def isYUseProbeEntry(self):
        return self.yUseProbeEntry.isChecked()

    def xProbeNames(self):
        return self.xProbesControl.probeNames()

    def yProbeNames(self):
        return self.yProbesControl.probeNames()

    def xProbesView(self):
        return self.xProbesControl.probesView()

    def yProbesView(self):
        return self.yProbesControl.probesView()

    def xProbeEntryName(self):
        return str(self.xProbeEntry.currentText())

    def yProbeEntryName(self):
        return str(self.yProbeEntry.currentText())

    def xProbeEntriesView(self):
        return self.xProbeEntry

    def yProbeEntriesView(self):
        return self.yProbeEntry

    def isAggregateParameter(self):
        return self.yProbesControl.aggregatecheckBox.isChecked()

    def aggregationParameter(self):
        return str(self.yProbesControl.aggregateParameter.currentText())

    def isPlotNotAggregatedGraphs(self):
        return self.yProbesControl.originalgraphcheckBox.isChecked()
    def isShowConfidenceLevels(self):
        return self.yProbesControl.confidencecheckBox.isChecked()

    def getConfidenceLevel(self):
        return self.yProbesControl.confidenceLevel.value()

    def getSelectedProbeName(self):
        return self.yProbeNames()[0]  

    def getAllSelectedProbeNames(self):
        return self.yProbeNames()

class GraphNavigationBar(QtGui.QWidget):
    from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg

    def __init__(self, *qwidgetArgs):
        QtGui.QWidget.__init__(self, *qwidgetArgs)

    def setCanvas(self, canvas):
        self.layout = QtGui.QVBoxLayout(self)
        self.layout.setMargin(0)
        self.layout.setSpacing(0)
        self.layout.setObjectName("layout")

        self.toolbar = self.__class__.NavigationToolbar2QTAgg(canvas, self)
        self.toolbar.setObjectName("toolbar")
        self.toolbar.setFixedHeight(33)
        self.layout.addWidget(self.toolbar)

from ui.Widgets_Graph_ui import Ui_Widgets_Graph
class Graph(QtGui.QWidget, Ui_Widgets_Graph):

    def __init__(self, *qwidgetArgs):
        QtGui.QWidget.__init__(self, *qwidgetArgs)
        self.setupUi(self)
        self.navigationBar.setCanvas(self.canvas)

class LineGraph(Graph, Observing):

    def __init__(self, *qwidgetArgs):
        Graph.__init__(self, *qwidgetArgs)

        self.lines = []
        self.labels = []
        self.legendModel = Models.Legend()

        self.figureConfig = Data.Figure()
        self.observe(self.on_figureConfig_grid_changed, self.figureConfig, "grid")
        self.observe(self.on_figureConfig_scale_changed, self.figureConfig, "scale")
        self.observe(self.on_figureConfig_marker_changed, self.figureConfig, "marker")
        self.observe(self.on_figureConfig_legend_changed, self.figureConfig, "legend")
        self.observe(self.on_figureConfig_graphs_changed, self.figureConfig, "graphs")

        import Dialogues
        self.progressDialogue = Dialogues.Progress("Plotting", 0, self)

    def setGraphs(self, graphs):
        self.figureConfig.graphs = graphs

    def setGrid(self, xmajor, xminor, ymajor, yminor):
        self.canvas.axes.get_xaxis().grid(xmajor, which="major")
        self.canvas.axes.get_xaxis().grid(xminor, which="minor")
        self.canvas.axes.get_yaxis().grid(ymajor, which="major")
        self.canvas.axes.get_yaxis().grid(yminor, which="minor")

    def setScale(self, xscale, xbase, yscale, ybase):
        self.canvas.axes.set_xscale(xscale, basex=xbase)
        self.canvas.axes.set_yscale(yscale, basey=ybase)

    def getLegendModel(self):
        return self.legendModel

    def setLegend(self, show):
        if show:
            from matplotlib.font_manager import FontProperties
            self.canvas.axes.legend(loc = 0, prop = FontProperties(size = "xx-small"))
        else:
            self.plotGraph()

    def configureGraph(self):
        self.setGrid(*(self.figureConfig.grid))
        self.setScale(*(self.figureConfig.scale))
        self.setLegend(self.figureConfig.legend)

    def saveGraph(self,imageFile):
        self.canvas.print_figure(imageFile)

    def plotGraph(self):
        from probeselector.Interface import Facade

        self.canvas.axes.clear()

        lineColours = list("bgrcmyk")
        lineStyles = ["-", "--", "-.", ":"]
        coloursStyles = [colour + style for style in lineStyles for colour in lineColours]
        csIter = iter(coloursStyles)

        self.lines = []
        self.labels = []

        maxIndex = len(self.figureConfig.graphs) - 1
        self.progressDialogue.reset()
        xLabels = set()
        yLabels = set()
        for index, graph in enumerate(self.figureConfig.graphs):
            x = [point[0] for point in graph.points]
            y = [point[1] for point in graph.points]
            label = Facade.getGraphDescription(graph)
            xLabels.add(graph.axisLabels[0])
            yLabels.add(graph.axisLabels[1])
            self.progressDialogue.setCurrentAndMaximum(index, maxIndex, "Preparing: " + label)
           
            try:
                style = csIter.next()
            except StopIteration:
                csIter = iter(coloursStyles)
                style = csIter.next()
            self.lines.append(self.canvas.axes.plot(x, y, style, label = label, marker = self.figureConfig.marker))
            self.labels.append(label)
            try:
                if len(graph.confidenceIntervalDict) > 0 and self.figureConfig.scale[2]=='linear':
                    for i in range(len(x)):
                        e = graph.confidenceIntervalDict[x[i]]
                        self.canvas.axes.errorbar(x[i], y[i], yerr=e , fmt=style)
            except: None
        self.canvas.axes.set_xlabel("\n".join(xLabels))
        self.canvas.axes.set_ylabel("\n".join(yLabels))
        ymin, ymax = self.canvas.axes.get_ylim()
        if ymin > 0:
            self.canvas.axes.set_ylim(0, ymax)
        self.setGrid(*self.figureConfig.grid)
        self.legendModel.updateLinesNLabels(self.lines, self.labels)
        self.setScale(*(self.figureConfig.scale))
        if self.figureConfig.legend:
            self.setLegend(True)

    def on_figureConfig_title_changed(self, value):
        self.canvas.axes.set_title(value)
        self.doDraw()

    def on_figureConfig_graphs_changed(self, value):
        self.plotGraph()
        self.doDraw()

    def on_figureConfig_marker_changed(self, value):
        self.plotGraph()
        self.doDraw()

    def on_figureConfig_legend_changed(self, value):
        self.setLegend(value)
        self.doDraw()

    def on_figureConfig_grid_changed(self, value):
        self.setGrid(*value)
        self.doDraw()

    def on_figureConfig_scale_changed(self, value):
        self.setScale(*value)
        self.plotGraph()
        self.doDraw()

    def doDraw(self):
        self.canvas.draw()


from ui.Widgets_TableGraph_ui import Ui_Widgets_TableGraph
class TableGraph(QtGui.QWidget, Ui_Widgets_TableGraph, Observing):
    def __init__(self, window, *qwidgetArgs):
        QtGui.QWidget.__init__(self, *qwidgetArgs)
        self.setupUi(self)

        self.window = window

        self.graphWidgets = dict()

        self.figureConfig = Data.Figure()
        #self.observe(self.on_figureConfig_grid_changed, self.figureConfig, "grid")
        self.observe(self.on_figureConfig_redraw, self.figureConfig)
        #self.observe(self.on_figureConfig_redraw, self.figureConfig, "colorbar")

        self.connect(self.graphSwitcher, QtCore.SIGNAL("currentIndexChanged(const QString&)"), self.on_graphSwitcher_currentIndexChanged)

    def setGraphs(self, graphs):
        self.graphs = graphs
        self.doDraw()

    def doDraw(self):
        import matplotlib.pylab
        self.graphSwitcher.clear()
        for index in xrange(self.graphStack.count() - 1, -1, -1):
            self.graphStack.removeWidget(self.graphStack.widget(index))
        for graph in self.graphs:
            if len(graph.points) > 1:
                widget = Graph()
                self.graphWidgets[str(graph.identity)] = (widget, graph)
                self.graphStack.addWidget(widget)
                self.graphSwitcher.addItem(str(graph.identity))
                X, Y = matplotlib.pylab.meshgrid(
                    [p[0] for p in graph.points],
                    [p[1] for p in graph.points])
                collection = widget.canvas.axes.pcolor(X,
                                          Y,
                                          matplotlib.pylab.array(graph.colours),
                                          shading = "flat",
                                          cmap = matplotlib.cm.get_cmap(str(self.figureConfig.colormap)))
                if self.figureConfig.colorbar:
                    widget.canvas.fig.colorbar(collection)
                widget.canvas.axes.axis('scaled')
                if self.figureConfig.xAxisTitle == "":
                    widget.canvas.axes.set_xlabel(graph.axisLabels[0])
                else:
                    widget.canvas.axes.set_xlabel(self.figureConfig.xAxisTitle)

                if self.figureConfig.yAxisTitle == "":
                    widget.canvas.axes.set_ylabel(graph.axisLabels[1])
                else:
                    widget.canvas.axes.set_ylabel(self.figureConfig.yAxisTitle)

                if self.figureConfig.title == "":
                    widget.canvas.axes.set_title(graph.title)
                else:
                    widget.canvas.axes.set_title(self.figureConfig.title)

    @QtCore.pyqtSignature("const QString&")
    def on_graphSwitcher_currentIndexChanged(self, text):
        if self.graphWidgets.has_key(str(text)):
            self.graphStack.setCurrentWidget(self.graphWidgets[str(text)][0])
            self.window.setWindowTitle(self.graphWidgets[str(text)][1].title)
            self.window.activateAction.setText(self.graphWidgets[str(text)][1].title)

    def setGrid(self, xmajor, xminor, ymajor, yminor):
        self.canvas.axes.get_xaxis().grid(xmajor, which="major")
        self.canvas.axes.get_xaxis().grid(xminor, which="minor")
        self.canvas.axes.get_yaxis().grid(ymajor, which="major")
        self.canvas.axes.get_yaxis().grid(yminor, which="minor")

    def on_figureConfig_grid_changed(self, value):
        self.setGrid(*value)
        self.doDraw()

    def on_figureConfig_redraw(self, value):
        self.doDraw()

class Legend(QtGui.QListView):
    pass

class TraceNavigation(QtGui.QDockWidget):

    from openwns.wrowser.ui.Widgets_TraceNavigation_ui import Ui_Widgets_TraceNavigation
    class TraceNavigationWidget(QtGui.QWidget, Ui_Widgets_TraceNavigation):
        
        def __init__(self, mainWindow, *args):
            QtGui.QWidget.__init__(self, *args)
            self.setupUi(self)

    def __init__(self, parent, *args):
        QtGui.QDockWidget.__init__(self, "Navigation", parent, *args)
        self.internalWidget = self.__class__.TraceNavigationWidget(parent, self)
        self.setWidget(self.internalWidget)

        self.connect(self.internalWidget.next10, QtCore.SIGNAL("clicked()"), self.on_Next10Clicked)
        self.connect(self.internalWidget.previous10, QtCore.SIGNAL("clicked()"), self.on_Previous10Clicked)

        self.connect(self.internalWidget.radioframe, QtCore.SIGNAL("valueChanged(int)"), self.on_radioFrameChanged)
        self.timer = None

    @QtCore.pyqtSignature("")
    def on_Next10Clicked(self):
        rf = self.internalWidget.radioframe.value()
        rf += 10
        self.internalWidget.radioframe.setValue(rf)

    @QtCore.pyqtSignature("")
    def on_Previous10Clicked(self):
        rf = self.internalWidget.radioframe.value()
        rf -= 10

        if rf < 0:
            rf = 0

        self.internalWidget.radioframe.setValue(rf)

    @QtCore.pyqtSignature("int")
    def on_radioFrameChanged(self, value):
        if self.timer is None:
            self.timer = QtCore.QTimer(self)
            self.timer.setSingleShot(True)
            self.connect(self.timer, QtCore.SIGNAL("timeout()"), self.on_changeTimerExpired)
            
            self.timer.start(500)

        else:
            if self.timer.isActive():
                self.timer.stop()

            self.timer.start(500)

    @QtCore.pyqtSignature("")
    def on_changeTimerExpired(self):
        self.emit(QtCore.SIGNAL("radioFrameChanged(int)"), self.internalWidget.radioframe.value())

class ViewCouchDBTrace(QtGui.QDockWidget):

    from openwns.wrowser.ui.Widgets_ViewCouchDBTrace_ui import Ui_Widgets_ViewCouchDBTrace
    class ViewCouchDBTraceWidget(QtGui.QWidget, Ui_Widgets_ViewCouchDBTrace):
        
        def __init__(self, mainWindow, *args):
            QtGui.QWidget.__init__(self, *args)
            self.setupUi(self)

    def __init__(self, parent, *args):
        QtGui.QDockWidget.__init__(self, "View CouchDB Trace", parent, *args)
        self.internalWidget = self.__class__.ViewCouchDBTraceWidget(parent, self)
        self.setWidget(self.internalWidget)

