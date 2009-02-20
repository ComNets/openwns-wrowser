import openwns.wrowser.probeselector.Errors as Errors

class XY:
    def __init__(self, x, y):
        self.acquireXData = x
        self.acquireYData = y

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
                graph.points.append((x, y))

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
