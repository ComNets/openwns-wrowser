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

import wrowser.probeselector.Errors as Errors

def defaultGraphWriter(x, y, graph):
    graph.points.append((x, y))

def aggregateGraphWriter(x, y, graph):
    if x in graph.pointsDict.keys():
        graph.pointsDict[x].append(y)
    else:
        graph.pointsDict[x] = [y]

class XY:
    def __init__(self, x, y, graphWriter = defaultGraphWriter):
        self.acquireXData = x
        self.acquireYData = y
        self.graphWriter = graphWriter

    def __call__(self, scenario, probe, graph, errors):
        try:
            x = self.acquireXData(scenario, probe)
        except Errors.ProbeNotFoundInSimulation, e:
            errors.append(e)
        else:
            try:
                y = self.acquireYData(scenario, probe)
            except Errors.ProbeNotFoundInSimulation, e:
                errors.append(e)
            else:
                graph.axisLabels = (self.acquireXData.label,
                                    self.acquireYData.label)
                self.graphWriter(x, y, graph)

class ParameterValue:
    def __init__(self, parameterName):
        self.parameterName = parameterName
        self.label = parameterName

    def __call__(self, scenario, probe):
        return scenario.parameters[self.parameterName]

class ProbeEntry:
    def __init__(self, entryName):
        self.entryName = entryName

    def __call__(self, scenario, probe):
        self.label = self.entryName + " of " + probe.data.description
        return getattr(probe.data, self.entryName)

class Probe:
    def __init__(self, entryName):
        self.entryName = entryName

    def __call__(self, scenario, probe):
        self.label = self.entryName + " of " + probe.data.description
        return probe.data

class ProbeEntryOfProbe:
    def __init__(self, probeName, entryName):
        self.probeName = probeName
        self.entryName = entryName

    def __call__(self, scenario, probeNotUsed):
        try:
            probe = scenario.probes[self.probeName]
        except KeyError:
            raise Errors.ProbeNotFoundInSimulation(self.probeName, scenario.parameters)
        else:
            self.label = self.entryName + " of " + probe.data.description
            return getattr(probe.data, self.entryName)
