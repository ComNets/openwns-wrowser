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


    def loadImage(self, fileToPlot, fillValue):
        baseFilename = '_'.join(fileToPlot.split("_")[:-1])
        what= '_' + fileToPlot.split("_")[-1]

        try:
            filename = baseFilename + what
            trialFilename = baseFilename + '_trials.m'
            print "Loading %s" % filename
            map_raw = load(filename, comments='%')
            print "Loading %s" % trialFilename
            trials_raw = load(trialFilename, comments='%')
        except IOError:
            return None

        map_parsed = rec.fromrecords(map_raw, names = 'x,y,z')
        self.numXEntries = len(unique(map_parsed['x']))
        self.minX = min(map_parsed['x'])
        self.maxX = max(map_parsed['x'])

        self.numYEntries = len(unique(map_parsed['y']))
        self.minY = min(map_parsed['y'])
        self.maxY = max(map_parsed['y'])

        print "The map is (%dx%d)" % (self.numYEntries+1, self.numXEntries+1)
        map = ones((self.numYEntries, self.numXEntries)) * fillValue

        for i in xrange(len(map_parsed['x'])):
            xIndex = int(floor((self.numXEntries-1) * (map_parsed['x'][i] - self.minX) / (self.maxX-self.minX)))
            yIndex = int(floor((self.numYEntries-1) * (map_parsed['y'][i] - self.minY) / (self.maxY-self.minY)))

            map[yIndex][xIndex] = map_parsed['z'][i]

        return map

    def plotScenario(self, canvas, fileToPlot, fillValue, includeContour):
        """this method should be implemented in any class that derives
from ScenarioFrame to plot special scenarios"""
        axes = canvas.axes
        axes.hold(True)

        scenarioSize = self.inspector.getSize()

        axes.grid(True)

        groupcolors = { 1 : 'b', 2:'r', 3:'g', 4:'y', 5:'m', 6:'c' }

        shapes = { 0 : '^', 1 : 'o', 2 : 's', 3: 'x'}

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

        map = self.loadImage(fileToPlot, fillValue)
        if map is not None:
            im = axes.imshow(map,
                             origin = 'lower',
                             extent= (scenarioSize[0], scenarioSize[2],
                                      scenarioSize[1], scenarioSize[3])
                             )
            canvas.fig.colorbar(im)

            if includeContour:
                cs = axes.contour(map,
                                  extent= (scenarioSize[0], scenarioSize[2],
                                           scenarioSize[1], scenarioSize[3])
                                  )
                axes.clabel(cs)

        axes.set_xlim(scenarioSize[0], scenarioSize[2])
        axes.set_ylim(scenarioSize[1], scenarioSize[3])

        canvas.draw()

    def plotCut(self, canvas, fileToPlot, fillValue, x1, y1, x2, y2):

        map = self.loadImage(fileToPlot, fillValue)

        axes = canvas.axes
        axes.hold(True)

        x1Index = self.numXEntries * (x1 - self.minX) / (self.maxX-self.minX)
        y1Index = self.numYEntries * (y1 - self.minY) / (self.maxY-self.minY)
        x2Index = self.numXEntries * (x2 - self.minX) / (self.maxX-self.minX)
        y2Index = self.numYEntries * (y2 - self.minY) / (self.maxY-self.minY)

        print "Coordinates (%d,%d,%d,%d)" % (x1Index, y1Index, x2Index, y2Index)

        lenX = x2Index - x1Index
        lenY = y2Index - y1Index

        length = (lenX**2 + lenY**2)**0.5
        
        # line equation r = b + m * i
        b = zeros(2)
        b[0] = x1Index
        b[1] = y1Index

        m = zeros(2)
        m[0] = lenX
        m[1] = lenY

        x = []
        y = []
        d = []
        for i in arange(0, 1, 0.001):
            offset = m * i
            r = b + offset

            x.append(r[0])
            y.append(r[1])
            travelled = (offset[0]**2 + offset[1]**2)**0.5
            d.append( travelled )

        from scipy import ndimage
        values = ndimage.map_coordinates(map, [y,x])
        axes.plot(d, values)

        canvas.draw()
