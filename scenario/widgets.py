from PyQt4 import QtCore, QtGui
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg
import matplotlib.figure
import os

import inspect

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
                self.mainWindow.updateScenarioView(path, fillValue)

        @QtCore.pyqtSignature("bool")
        def on_scanWinnerButton_clicked(self, checked):
            print "Starting Simulation"
            print str(self.powerPerSubBand.text())
            import subprocess
            import shutil
            import os

            thisDir = os.path.dirname(__file__)
            shutil.copyfile(os.path.join(thisDir, 'template_WinnerScanner.py'),
                            os.path.join(self.workingDir, 'xyz.py'))

            file = open(os.path.join(self.workingDir, 'xyz.py'), "a")
            file.write('powerPerSubBand = "%s dBm"\n' % str(self.powerPerSubBand.text()))
            file.write('tileWidth = "%s"\n' % str(self.tileWidth.text()))
            (xmin,ymin,xmax,ymax) = self.inspector.getSize()

            file.write('xMin = %f\n' % ( xmin ))
            file.write('xMax = %f\n' % ( xmax ))
            file.write('yMin = %f\n' % ( ymin ))
            file.write('yMax = %f\n' % ( ymax ))

            file.write('baseStations = []\n\n')
            for n in self.inspector.getNodes():
                if self.inspector.hasMobility(n):
                    if self.inspector.getNodeTypeId(n) == 0:
                        m = self.inspector.getMobility(n)
                        file.write("bsPosition = rise.scenario.Nodes.RAP()\n")
                        file.write("bsPosition.position = wns.Position(%f,%f,%f)\n" % (m.coords.x, m.coords.y, m.coords.z))
                        file.write("baseStations.append( bsPosition )\n\n")

            file.write('builder = ScannerScenarioBuilder(maxSimTime=100, scenarioSize=(xMin,yMin,xMax,yMax), tileWidth = tileWidth, powerPerSubBand=powerPerSubBand)\n')
            file.write('for bs in baseStations:\n')
            file.write('    builder.createBaseStation(bs)\n\n')
            file.write('builder.finalizeScenario()\n')
            file.write('WNS = builder.getSimulator()\n')
            file.close()

            currentpath = os.getcwd()
            os.chdir(self.workingDir)
            retcode = subprocess.call(["./wns-core", "-f", "xyz.py"])
            os.remove(os.path.join(self.workingDir, 'xyz.py'))
            os.chdir(currentpath)

            if retcode != 0:
                QtGui.QMessageBox.critical(self,
                                           "An error occured",
                                           "An error occured when executing the simulator")
                
            else:
                self.updateFileList()
                self.update()

    def __init__(self, configFilename, parent, *args):
        QtGui.QDockWidget.__init__(self, "View Scenario", parent, *args)
        self.internalWidget = self.__class__.ViewScenarioWidget(configFilename, parent, self)
        self.setWidget(self.internalWidget)
