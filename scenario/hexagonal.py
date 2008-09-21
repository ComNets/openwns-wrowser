import math
from pylab import *

class ScenarioPlotter:

    def __init__(self, scenario):
        self.scenario = scenario
        self.utPositions = []

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


    def plotScenario(self, canvas):
        """this method should be implemented in any class that derives
from ScenarioFrame to plot special scenarios"""
        axes = canvas.axes
        axes.hold(True)

        # plot buildings, if any
        for building in self.scenario.getMobilityObstructions():
            assert isinstance(building, Shape2D)
            self.plotShape(building,
                           facecolor='gray')

        # plot BS and RN positions
        positions = self.scenario.getPositions()
        stationCounter = 1

        groupcolors = { 1 : 'b', 2:'r', 3:'g', 4:'y', 5:'m', 6:'c' }

        for posAndGroup in positions['BS']:
            try:
                pos = posAndGroup[0]
                grp = posAndGroup[1]
                color = groupcolors[grp]
            except TypeError:
                pos = posAndGroup
                color = 'b'

            axes.plot([pos.x], [pos.y], color+'^')
            axes.text(pos.x, pos.y, 'BS%d'%stationCounter)
            r = self.scenario.dAP_AP/(2*math.cos(2*math.pi/12))

            self.plotPolyEllipse(canvas, (pos.x, pos.y), (r,r), 6, 2*math.pi/12, facecolor="white", edgecolor="blue")
            stationCounter +=1

        for posAndGroup in positions['RN']:
            try:
                pos = posAndGroup[0]
                grp = posAndGroup[1]
                color = groupcolors[grp]
            except TypeError:
                pos = posAndGroup
                color = 'g'

            axes.plot([pos.x], [pos.y], color+'s')
            axes.text(pos.x, pos.y, 'RN%d'%stationCounter)
            #self.plotCircle(pos, self.scenario.getCellRadius() ,'k:')
            stationCounter +=1

        # eventually plot UT positions
        if len(self.utPositions):
            if isinstance(self.utPositions[0], tuple):
                for pos, nr in self.utPositions:
                    assert isinstance(pos, wns.Position)
                    axes.plot([pos.x], [pos.y], 'go')
                    axes.text(pos.x, pos.y, str(nr))
            elif isinstance(self.utPositions[0], wns.Position):
                utX = [ pos.x for pos in self.utPositions ]
                utY = [ pos.y for pos in self.utPositions ]
                axes.plot(utX, utY, 'go')
            else:
                raise "Can't interpret utPositions list: %s" % str(self.utPositions)

        ax = gca()

        canvas.draw()
