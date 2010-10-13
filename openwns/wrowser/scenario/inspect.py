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
import subprocess

import openwns.wrowser.Configuration as Configuration

class SimulatorConfigNotFound:
    pass

class ConfigInspector:

    def __init__(self, configurationFile):
        currentdir = os.getcwd()

        c = Configuration.SandboxConfiguration()
        c.read()

        thisDir = os.path.dirname(__file__)
        templateFilename = os.path.join(thisDir, 'templates', 'inspection.py.tmpl')

        # Create configuration using the template system
        import Cheetah.Template
        import templates.datamodel
        pckfilename = "__wrowser__viewscenario__inspect.pck"
        content = {"filename":pckfilename}

        t = Cheetah.Template.Template(file=templateFilename, searchList=[content])

        f = open(str(configurationFile), "r")
        content = f.read()
        f.close()

        filepath = os.path.dirname(configurationFile)

        os.chdir(filepath)

        instrFilename = "__wrowser__viewscenario__config.py"
        f = open(instrFilename, "w")
        f.write(content)
        f.write("\n")
        f.write(t.respond())
        f.close()

        pypath = os.path.join(c.sandboxPath, c.sandboxFlavour, "lib", "PyConfig")

        subprocess.call(['python', instrFilename], env = { "PYTHONPATH":pypath})

        import pickle

        f = open(pckfilename)
        self.nodelist = pickle.load(f)
        f.close()

        os.chdir(currentdir)
        
    def getNodes(self):
        return self.nodelist

    def getNodeTypeId(self, node):
        """Returns the node type
        0 : Base Station
        1 : User Terminal
        2 : Relay Node
        3 : Unknown
        """

        classname = node["nodeType"]

        if classname in ['BS', 'BaseStation', 'Station']:
            return 0

        if classname in ['MS', 'UserTerminal']:
            return 1

        if classname in ['RN', 'RelayNode']:
            return 2

        return 3

    def getSize(self):
        xMax = None
        xMin = None
        yMax = None
        yMin = None

        for n in self.getNodes():
            if n["hasMobility"]:
                x = n["coords"]["x"]
                y = n["coords"]["y"]
                if xMax is None or xMax < x:
                    xMax = x

                if xMin is None or xMin > x:
                    xMin = x

                if yMax is None or yMax < y:
                    yMax = y

                if yMin is None or yMin > y:
                    yMin = y

        width = xMax - xMin
        height = yMax - yMin

        dw = width * 0.05
        dh = height * 0.05

        if dw < 50:
            dw = 50
        if dh < 50:
            dh = 50

        scenXMin = max(0, xMin - dw)
        scenYMin = max(0, yMin - dh)
        scenXMax = max(0, xMax + dw)
        scenYMax = max(0, yMax + dh)

        return (scenXMin, scenYMin, scenXMax, scenYMax)
