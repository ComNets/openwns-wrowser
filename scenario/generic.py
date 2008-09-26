import math
from pylab import *
import wnsrc
wnsrc.wnsrc.setPathToPyConfig('dbg')
from rise.scenario.Shadowing import Shape2D
import openwns.simulator


class GenericPlotter:

    def __init__(self, inspector):
        self.inspector = inspector

    def plotCircle(self, canvas, center, radius, *args, **kwargs):
        x = []
        y = []
        n = 360
        for i in xrange(n):
            angle = 2.0  * math.pi / n
            x.append(round(center.x+radius*math.sin(i*angle), 6))
            y.append(round(center.y+radius*math.cos(i*angle), 6))

        canvas.axes.plot(x, y, *args, **kwargs)

    def plotLine(self, canvas, endPoints, *args, **kwargs):
        """the endPoints parameter must be a list of instances of type wns.Position"""
        canvas.axes.plot([ endPoints[0].x, endPoints[1].x ],
                              [ endPoints[0].y, endPoints[1].y ],
                              *args,
                              **kwargs)

    def plotShape(self, canvas, shape, *args, **kwargs):
        """the shape parameter must be an instance of type rise.scenario.Shadowing.Shape2D"""
        canvas.axes.fill([shape.pointA[0], shape.pointB[0], shape.pointB[0], shape.pointA[0] ],
                              [shape.pointA[1], shape.pointA[1], shape.pointB[1], shape.pointB[1] ],
                              *args, **kwargs)
        return

    def plotPolyEllipse(self, canvas, (x,y), (rx, ry), resolution=20, orientation=0, **kwargs):
        theta = 2*math.pi/resolution*arange(resolution) + orientation
        xs = x + rx * cos(theta)
        ys = y + ry * sin(theta)
        canvas.axes.add_patch(Polygon(zip(xs, ys), **kwargs))


    def loadImage(self):
        filename = "output/Scanner_RxPwr_BSID0"
        what= "_mean.m"

        try:
            map_raw = load(filename + what, comments='%')
            trials_raw = load(filename + '_trials.m', comments='%')
        except IOError:
            return None

        map_parsed = rec.fromrecords(map_raw, names = 'x,y,z')
        numXEntries = len(unique(map_parsed['x']))
        minX = min(map_parsed['x'])
        maxX = max(map_parsed['x'])

        numYEntries = len(unique(map_parsed['y']))
        minY = min(map_parsed['y'])
        maxY = max(map_parsed['y'])

        print "The map is (%dx%d)" % (numXEntries+1, numYEntries+1)
        map = ones((numXEntries+1, numYEntries+1)) * (-174)
        
        for i in xrange(len(map_parsed['x'])):
            xIndex = int(numXEntries * (map_parsed['x'][i] - minX) / (maxX-minX))
            yIndex = int(numYEntries * (map_parsed['y'][i] - minY) / (maxY-minY))
            map[xIndex][yIndex] = map_parsed['z'][i]

        return map

    def plotScenario(self, canvas):
        """this method should be implemented in any class that derives
from ScenarioFrame to plot special scenarios"""
        axes = canvas.axes
        axes.hold(True)

        scenarioSize = self.inspector.getSize()

        axes.grid(True)

        groupcolors = { 1 : 'b', 2:'r', 3:'g', 4:'y', 5:'m', 6:'c' }

        shapes = { 0 : '^', 1 : 'o', 2 : 's'}

        for n in self.inspector.getNodes():
            if self.inspector.hasMobility(n):
                pos = self.inspector.getMobility(n).coords
                type = self.inspector.getNodeTypeId(n)
                color = groupcolors[1]
                axes.plot([pos.x], [pos.y], color+shapes[type])

                import random
                x=random.randint(-10,10)
                y=random.randint(-10,10)
                axes.text(pos.x + x, pos.y + y, n.name)

        map = self.loadImage()
        if map is not None:
            axes.imshow(map,
                        extent= (scenarioSize[0], scenarioSize[2],
                                 scenarioSize[1], scenarioSize[3])
                        )

        axes.set_xlim(scenarioSize[0], scenarioSize[2])
        axes.set_ylim(scenarioSize[1], scenarioSize[3])


        canvas.draw()
