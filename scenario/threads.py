from PyQt4 import QtCore, QtGui

class SimulationThread(QtCore.QThread):

    def __init__(self, parent):
        self.parent = parent
        QtCore.QThread.__init__(self, parent)

    def run(self):

        # Choose template
        import os
        import subprocess

        thisDir = os.path.dirname(__file__)
        templateFilename = os.path.join(thisDir, 'templates', 'WinnerScanner.py.tmpl')

        # Create configuration using the template system
        import Cheetah.Template
        import templates.datamodel

        bsPositions = []
        for n in self.parent.inspector.getNodes():
            if self.parent.inspector.hasMobility(n):
                if self.parent.inspector.getNodeTypeId(n) == 0:
                    m = self.parent.inspector.getMobility(n)
                    bsPositions.append(templates.datamodel.BSPosition(m.coords.x, m.coords.y, m.coords.z))

        content = {}
        content["powerPerSubBand"] = str(self.parent.powerPerSubBand.text())
        content["numXBins"] = int(self.parent.xBinsEdit.text())
        content["numYBins"] = int(self.parent.yBinsEdit.text())
        content["scenario"] = templates.datamodel.Scenario(*self.parent.inspector.getSize())
        content["baseStations"] = bsPositions

        t = Cheetah.Template.Template(file=templateFilename, searchList=[content])

        output = file(os.path.join(self.parent.workingDir, 'xyz.py'), "w")
        output.write(t.respond())
        output.close()

        # Execute the simulation
        currentpath = os.getcwd()
        os.chdir(self.parent.workingDir)
        self.retcode = subprocess.call(["./wns-core", "-f", "xyz.py"])
        if self.retcode == 0:
            self.success = True
            os.remove(os.path.join(self.parent.workingDir, 'xyz.py'))
        else:
            self.success = False

        os.chdir(currentpath)

