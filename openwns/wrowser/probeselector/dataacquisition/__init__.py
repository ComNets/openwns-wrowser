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

import openwns.wrowser.probeselector.Errors as Errors
import openwns.wrowser.probeselector.Interface
import openwns.wrowser.probeselector.Graphs as Graphs

import Probe
import Compose
import Aggregator

class Scenario:

    def __init__(self, probeDataAcquirers, parameterNames, aggregationFunction = None):
        self.probeDataAcquirers = probeDataAcquirers
        self.parameterNames = parameterNames
        self.aggregationFunction = aggregationFunction

    def __call__(self, scenario, graphs, errors):

        def acquire(probe = None):
            scenarioParameterValues = openwns.wrowser.probeselector.Interface.Facade.getScenarioParameterValues(scenario, self.parameterNames)
            graphParameters = dict(zip(self.parameterNames, scenarioParameterValues))
            if probe == None:
                probeName = None
            else:
                probeName = probe.name
            graphIdentity = Graphs.GraphIdentityParameters(probeName, graphParameters)
            graphargs = {"identity" : graphIdentity,
                         "sortkey" : graphParameters,
                         "aggregationFunction" : self.aggregationFunction}
            graph = graphs.getGraphInstance(key = str(graphIdentity), graphargs = graphargs)
            acquireXYData(scenario, probe, graph, errors)

        for probeName, acquireXYData in self.probeDataAcquirers.items():
            if probeName != None:
                try:
                    probe = scenario.probes[probeName]
                except KeyError:
                    errors.append(Errors.ProbeNotFoundInSimulation(probeName, scenario.parameters))
                else:
                    if hasattr(probe.data, "overflows") and probe.data.overflows > 0:
                        errors.append(Errors.Overflows(probeName, scenario.parameters))
                    if hasattr(probe.data, "underflows") and probe.data.underflows > 0:
                        errors.append(Errors.Underflows(probeName, scenario.parameters))
                    acquire(probe)
            else:
                acquire()

