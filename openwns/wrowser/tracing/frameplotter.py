from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg
import matplotlib.figure
import matplotlib.patches
from PyQt4 import QtCore, QtGui

class FramePlotter(FigureCanvasQTAgg):

    colors={}
    colors[0]="#aa0000"
    colors[1]="#00aa00"
    colors[2]="#0000aa"
    colors[3]="#aa6000"
    colors[4]="#aa0060"
    colors[5]="#aaaa00"
    colors[6]="#aa00aa"
    colors[7]="#aaaaaa"
    colors[8]="#606060"
    colors[9]="#000000"

    """This class implements a QT Widget on which you can draw using the
    MATLAB(R)-style commands provided by matplotlib
    """
    def __init__(self, db, parent=None, width=5, height=4, dpi=100):
        self.figure = matplotlib.figure.Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.figure.add_subplot(111)
        self.axes.hold(False)

        FigureCanvasQTAgg.__init__(self, self.figure)

        FigureCanvasQTAgg.setSizePolicy(self,
                                        QtGui.QSizePolicy.Expanding,
                                        QtGui.QSizePolicy.Expanding)
        FigureCanvasQTAgg.updateGeometry(self)

        self.db = db
        self.data = self.db.execute_view("orderByStartTime", "orderByStartTime")
        #print self.data
        self.radioFrameDuration = 0.01
        self.subFrameDuration = 0.001
        self.tolerance = self.subFrameDuration / 14
        self.startFrame = 0
        self.activeWindows = []

        self._makeConnects()
        self.plotRadioFrame()

    def _makeConnects(self):
        self.figure.gca().get_figure().canvas.mpl_connect('pick_event', self.onPicked)

    def onPicked(self, event):
        self.emit(QtCore.SIGNAL("itemPicked"), event.artist.data)

    def on_radioFrameChanged(self, value):
        self.startFrame = value
        self.plotRadioFrame()
        self.figure.canvas.draw()

    def plotRadioFrame(self):
        startTime = (self.subFrameDuration * self.startFrame) - self.tolerance
        stopTime = startTime + self.radioFrameDuration + 2 * self.tolerance

        for entry in self.data[startTime:stopTime]:
            v = entry.value
            import re
            m=re.match('\D*(\d*)', v["Transmission"]["ReceiverID"])
            cindex=int(m.group(1)) % 10
            theColor = FramePlotter.colors[cindex]
            duration = v["Transmission"]["Stop"] - v["Transmission"]["Start"]

            rect=matplotlib.patches.Rectangle((v["Transmission"]["Start"],
                                               v["Transmission"]["Subchannel"]-0.5),
                                              duration,
                                              1,
                                              facecolor=theColor, picker=True)
            rect.data=entry
            self.figure.gca().add_patch(rect)

        ax = self.figure.axes[0]
        ax.set_xlim(startTime + self.tolerance, stopTime - self.tolerance)
        ax.set_ylim(-1, 10)
        ax.grid()
        ax.set_title("Radioframe starting at subframe %d" % self.startFrame)
        ax.set_xlabel("Time [s]")
        ax.set_ylabel("Subchannel")
