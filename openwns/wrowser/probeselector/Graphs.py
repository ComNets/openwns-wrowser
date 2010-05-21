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

import Interface
import openwns.wrowser.Tools as Tools
import Errors

class GraphInstantiator:

    def __init__(self, graphClass):
        self.graphs = dict()
        self.graphClass = graphClass

    def getGraphInstance(self, key, graphargs):
        if not self.graphs.has_key(key):
            self.graphs[key] = self.graphClass(**graphargs)
        return self.graphs[key]

    def graphsAsList(self):
        return self.graphs.values()

class GraphIdentityParameters:

    def __init__(self, probe, parameters):
        self.probe = probe
        self.parameters = parameters

    def __str__(self):
        if self.probe == None:
            return Tools.dict2string(self.parameters)
        else:
            s = self.probe
            if len(self.parameters) > 0:
                s += "; " + Tools.dict2string(self.parameters)
            return s

class Graph(Tools.Chameleon):

    def __init__(self, identity = None, **additionalAttributes):
        Tools.Chameleon.__init__(self, **additionalAttributes)
        self.points = list()
        self.identity = identity
        self.axisLabels = ("", "")
        self.reversePoints = False

    def process(self):
        if self.reversePoints:
            self.points.reverse()
        self.points.sort(key = lambda x: x[0])


class AggregatedGraph(Graph):

    def __init__(self, identity = None, **additionalAttributes):
        Graph.__init__(self, identity, **additionalAttributes)
        self.pointsDict = dict()
        self.confidenceIntervalDict = dict()

    def process(self):
        numberOfPoints = map(lambda x: len(x), self.pointsDict.values())
        if min(numberOfPoints) != max(numberOfPoints):
            raise Errors.Aggregation()
            print "Fehler bei der Aggregierung"
        print "probeSelector-Graphs-AggregatedGraph-process"
        self.points = self.aggregationFunction(self)
        Graph.process(self)


class TableGraph(Graph):

    def __init__(self, identity = None, **additionalAttributes):
        additionalAttributes["colours"] = list()
        Graph.__init__(self, identity, **additionalAttributes)
        self.title = ""
