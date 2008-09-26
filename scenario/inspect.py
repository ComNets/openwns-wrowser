import wnsrc
wnsrc.wnsrc.setPathToPyConfig('dbg')
import rise.Mobility
import openwns.simulator
import os

class ConfigInspector:

    def __init__(self, configurationFile):
        currentdir = os.getcwd()

        self.config = {}
        exec("import sys", self.config)
        filepath = os.path.dirname(str(configurationFile))
        exec("sys.path.append('%s')" % filepath, self.config)

        file = open(str(configurationFile), "r")
        content = file.read()
        file.close()

        os.chdir(filepath)
        exec(content,self.config)
        os.chdir(currentdir)

    def getSimulator(self):
        for k,v in self.config.items():
            if isinstance(v, openwns.simulator.OpenWNS):
                return v
        return None

    def getNodes(self):
        sim = self.getSimulator()
        return sim.nodes

    def hasMobility(self, node):
        for c in node.components:
            if isinstance(c, rise.Mobility.Component):
                return True
        return False

    def getMobility(self, node):
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
        
        if classname in ['BS', 'BaseStation']:
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
