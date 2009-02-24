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

import wrowser.Configuration as Configuration

import os.path

class SimulationThread(QtCore.QThread):

    def __init__(self, parent):
        self.parent = parent
        QtCore.QThread.__init__(self, parent)

        c = Configuration.Configuration()
        c.read(os.path.join(os.environ["HOME"], ".wns", "dbAccess.conf"))

        self.simulatorExecutable = os.path.join(c.sandboxPath, c.sandboxFlavour, 'bin', 'openwns')

        if not os.path.exists(self.simulatorExecutable):
            QtGui.QMessageBox.warning(self.parent, "Cannot find simulator executable",
                                      "Cannot find %s. Have you built the flavour that you set in your preferences?" % (unicode(self.simulatorExecutable),))

    def run(self):

        # Choose template
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
        self.retcode = subprocess.call([self.simulatorExecutable, "-f", "xyz.py"])
        if self.retcode == 0:
            self.success = True
            os.remove(os.path.join(self.parent.workingDir, 'xyz.py'))
        else:
            self.success = False

        os.chdir(currentpath)

