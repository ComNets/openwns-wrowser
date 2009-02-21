import Interface
import wrowser.Tools as Tools

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
        self.orderPoints = self.points.sort

class TableGraph(Graph):

    def __init__(self, identity = None, **additionalAttributes):
        additionalAttributes["colours"] = list()
        Graph.__init__(self, identity, **additionalAttributes)
        self.title = ""
