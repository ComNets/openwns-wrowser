from PyQt4 import QtCore, QtGui
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg
import matplotlib.figure
import os

import inspect
import threads

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

    def clear(self):
        self.fig.clear()
        self.axes = self.fig.add_subplot(111)
        self.axes.hold(False)

class ViewScenario(QtGui.QDockWidget):

    from ui.Widgets_ViewScenario_ui import Ui_Widgets_ViewScenario
    import scenario.generic
    class ViewScenarioWidget(QtGui.QWidget, Ui_Widgets_ViewScenario):
        
        def __init__(self, configFilename, mainWindow, *args):
            QtGui.QWidget.__init__(self, *args)
            self.configFilename = configFilename
            self.workingDir = os.path.dirname(self.configFilename)
            self.inspector = inspect.ConfigInspector(self.configFilename)
            self.mainWindow = mainWindow
            self.simulationThread = threads.SimulationThread(self)
            self.progressTimeout = QtCore.QTimer(self)
            self.progressTimeout.setInterval(1000)

            QtCore.QObject.connect(self.simulationThread, QtCore.SIGNAL("finished()"), self, QtCore.SLOT("on_simulationThread_finished()"))
            QtCore.QObject.connect(self.progressTimeout, QtCore.SIGNAL("timeout()"), self, QtCore.SLOT("on_progressTimeout_timeout()"))
            self.setupUi(self)
            self.updateFileList()

            self.fillValueLineEdit.setValidator(QtGui.QDoubleValidator(self))
            self.powerPerSubBand.setValidator(QtGui.QDoubleValidator(self))

        @QtCore.pyqtSignature("bool")
        def on_redrawButton_clicked(self, checked):
            self.update()            

        def updateFileList(self):
            import pywns.Probe
            self.fileList.clear()

            if os.path.exists(self.workingDir + '/output/'):
                self.viewScenarioProbes = pywns.Probe.readAllProbes(self.workingDir + '/output/')
            else:
                self.viewScenarioProbes = {}

            doNotShowThese = []
            for k,v in self.viewScenarioProbes.items():
                if v.probeType is not 'Table':
                    doNotShowThese.append(k)
            for k in doNotShowThese:
                self.viewScenarioProbes.pop(k)

            self.fileList.addItems(self.viewScenarioProbes.keys())

        def update(self):
            if self.fileList.currentItem() is not None:
                fileToPlot = str(self.fileList.currentItem().text())
                path = os.path.join(self.workingDir, 'output', fileToPlot)
                fillValue = float(self.fillValueLineEdit.text())
                includeContour = self.contourPlotCheckBox.isChecked()
                self.mainWindow.updateScenarioView(path, fillValue, includeContour)

        @QtCore.pyqtSignature("bool")
        def on_scanWinnerButton_clicked(self, checked):
            if not self.simulationThread.isRunning():
                self.scanWinnerButton.setEnabled(False)
                self.scanWinnerButton.setText("Scanning ( 0.00 % )")
                self.simulationThread.start()
                self.progressTimeout.start()
            else:
                QtGui.QMessageBox.critical(self,
                                           "An error occured",
                                           "There is already a simulation running.")

        @QtCore.pyqtSignature("")
        def on_simulationThread_finished(self):
            self.scanWinnerButton.setEnabled(True)
            self.progressTimeout.stop()
            self.scanWinnerButton.setText("Scan")

            if self.simulationThread.success:
                self.updateFileList()
                self.update()
            else:
                QtGui.QMessageBox.critical(self,
                                           "An error occured",
                                           "An error occured when executing the simulator")

        @QtCore.pyqtSignature("")
        def on_progressTimeout_timeout(self):
            if os.path.exists('output/progress'):
                progressFile = open('output/progress')
                progress = float(progressFile.read()) * 100
                progressFile.close()
                self.scanWinnerButton.setText("Scan in progress ( %.2f %%)" % progress)

    def __init__(self, configFilename, parent, *args):
        QtGui.QDockWidget.__init__(self, "View Scenario", parent, *args)
        self.internalWidget = self.__class__.ViewScenarioWidget(configFilename, parent, self)
        self.setWidget(self.internalWidget)
