import openwns.wrowser.probeselector.Errors as Errors
import openwns.wrowser.probeselector.Interface
import openwns.wrowser.probeselector.Graphs as Graphs

import Probe
import Compose

class Scenario:

    def __init__(self, probeDataAcquirers, parameterNames):
        self.probeDataAcquirers = probeDataAcquirers
        self.parameterNames = parameterNames

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
                         "sortkey" : graphParameters}
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

