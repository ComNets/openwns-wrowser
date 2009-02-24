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

import wrowser.Configuration as Configuration

class SimulatorConfigNotFound:
    pass

class ConfigInspector:

    def __init__(self, configurationFile):
        currentdir = os.getcwd()

        c = Configuration.Configuration()
        c.read(os.path.join(os.environ["HOME"], ".wns", "dbAccess.conf"))

        self.config = {}
        exec("import sys", self.config)
        filepath = os.path.dirname(str(configurationFile))
        exec("sys.path.append('%s')" % filepath, self.config)
        exec("sys.path.insert(0,'%s/%s/lib/PyConfig')" % (c.sandboxPath, c.sandboxFlavour), self.config)

        file = open(str(configurationFile), "r")
        content = file.read()
        file.close()

        os.chdir(filepath)
        exec(content,self.config)
        os.chdir(currentdir)

        self.simulator = self.getSimulator()

    def getSimulator(self):
        import openwns.simulator
        for k,v in self.config.items():
            if isinstance(v, openwns.simulator.OpenWNS):
                return v

        raise SimulatorConfigNotFound

    def getNodes(self):
        sim = self.simulator
        return sim.simulationModel.nodes

    def hasMobility(self, node):
        import rise.Mobility
        for c in node.components:
            if isinstance(c, rise.Mobility.Component):
                return True
        return False

    def getMobility(self, node):
        import rise.Mobility
        assert self.hasMobility(node), "No mobility found"

        for c in node.components:
            if isinstance(c, rise.Mobility.Component):
                return c.mobility

    def getNodeType(self, node):
        
        classname = node.__class__.__name__

        return classname

    def getNodeTypeId(self, node):
        """Returns the node type
        0 : Base Station
        1 : User Terminal
        2 : Relay Node
        3 : Unknown
        """

        classname = self.getNodeType(node)

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
            if self.hasMobility(n):
                m = self.getMobility(n)
                if xMax is None or xMax < m.coords.x:
                    xMax = m.coords.x

                if xMin is None or xMin > m.coords.x:
                    xMin = m.coords.x

                if yMax is None or yMax < m.coords.y:
                    yMax = m.coords.y

                if yMin is None or yMin > m.coords.y:
                    yMin = m.coords.y

        width = xMax - xMin
        height = yMax - yMin

        dw = width * 0.3
        dh = height * 0.3

        if dw < 50:
            dw = 50
        if dh < 50:
            dh = 50

        scenXMin = max(0, xMin - dw)
        scenYMin = max(0, yMin - dh)
        scenXMax = max(0, xMax + dw)
        scenYMax = max(0, yMax + dh)

        return (scenXMin, scenYMin, scenXMax, scenYMax)
