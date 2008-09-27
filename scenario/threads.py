from PyQt4 import QtCore, QtGui

class SimulationThread(QtCore.QThread):

    def __init__(self, parent):
        self.parent = parent
        QtCore.QThread.__init__(self, parent)

    def run(self):

        print str(self.parent.powerPerSubBand.text())
        import subprocess
        import shutil
        import os

        thisDir = os.path.dirname(__file__)
        shutil.copyfile(os.path.join(thisDir, 'template_WinnerScanner.py'),
                        os.path.join(self.parent.workingDir, 'xyz.py'))

        file = open(os.path.join(self.parent.workingDir, 'xyz.py'), "a")
        file.write('powerPerSubBand = "%s dBm"\n' % str(self.parent.powerPerSubBand.text()))
        file.write('tileWidth = "%s"\n' % str(self.parent.tileWidth.text()))
        (xmin,ymin,xmax,ymax) = self.parent.inspector.getSize()

        file.write('xMin = %f\n' % ( xmin ))
        file.write('xMax = %f\n' % ( xmax ))
        file.write('yMin = %f\n' % ( ymin ))
        file.write('yMax = %f\n' % ( ymax ))

        file.write('baseStations = []\n\n')
        for n in self.parent.inspector.getNodes():
            if self.parent.inspector.hasMobility(n):
                if self.parent.inspector.getNodeTypeId(n) == 0:
                    m = self.parent.inspector.getMobility(n)
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
        os.chdir(self.parent.workingDir)
        self.retcode = subprocess.call(["./wns-core", "-y", "WNS.masterLogger.enabled = False", "-f", "xyz.py"])
        if self.retcode == 0:
            self.success = True
            os.remove(os.path.join(self.parent.workingDir, 'xyz.py'))
        else:
            self.success = False

        os.chdir(currentpath)

