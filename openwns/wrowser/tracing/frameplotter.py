from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg
import matplotlib.figure
import matplotlib.patches
from PyQt4 import QtCore, QtGui

class FramePlotter(FigureCanvasQTAgg):

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
        # Stale OK disables regeneration of index
        # Just keep in mind that this application is read-only
        # If you modify the db, you need to rebuild the index!!!
        self.data = self.db.execute_view("orderByStartTime", design_doc="wrowser")#, stale='ok')

        self.sendersView = self.db.execute_view("senders", design_doc="wrowser", group=True)#, stale='ok')
        self.receiversView = self.db.execute_view("receivers", design_doc="wrowser", group=True)#, stale='ok')

        self.senders = []
        self.receivers = []
        self.customFilter = None
        self.customFilterCheckbox = None

        for row in self.sendersView:
            self.senders.append(row.key)

        for row in self.receiversView:
            self.receivers.append(row.key)

        self.radioFrameDuration = 0.01
        self.subFrameDuration = 0.001
        self.tolerance = self.subFrameDuration / 14
        self.startFrame = 0
        self.activeWindows = []

        self._makeConnects()

    def _makeConnects(self):
        self.figure.gca().get_figure().canvas.mpl_connect('pick_event', self.onPicked)

    def onPicked(self, event):
        self.emit(QtCore.SIGNAL("itemPicked"), event.artist.data)

    def on_radioFrameChanged(self, value):
        self.figure.clear()
        self.startFrame = value
        self.plotRadioFrame()
        self.figure.canvas.draw()

    def plotRadioFrame(self):
        startTime = (self.subFrameDuration * self.startFrame) - self.tolerance
        stopTime = startTime + self.radioFrameDuration + 2 * self.tolerance

        selectedSenders = self.getSelectedSenders()
        selectedReceivers = self.getSelectedReceivers()

        for entry in self.data[startTime:stopTime]:
            if len(selectedSenders) > 0:
                # Only then we filter by sender
                if not entry.value["Transmission"]["SenderID"] in selectedSenders:
                    continue

            if len(selectedReceivers) > 0:
                # Only then we filter by sender
                if not entry.value["Transmission"]["ReceiverID"] in selectedReceivers:
                    continue


            if not self.applyCustomFilter(entry):
                continue

            v = entry.value

            theColor = self._getColor(v)

            duration = v["Transmission"]["Stop"] - v["Transmission"]["Start"]

            rect=matplotlib.patches.Rectangle((v["Transmission"]["Start"],
                                               v["Transmission"]["Subchannel"]-0.5),
                                              duration,
                                              1,
                                              facecolor=theColor[0], edgecolor=theColor[1], picker=True)
            rect.data=entry
            self.figure.gca().add_patch(rect)
        
        if len(self.figure.axes)>0:
            ax = self.figure.axes[0]
            ax.set_xlim(startTime + self.tolerance, stopTime - self.tolerance)
            ax.set_ylim(-1, 51)
            ax.grid()
            ax.set_title("Radioframe starting at subframe %d" % self.startFrame)
            ax.set_xlabel("Time [s]")
            ax.set_ylabel("Subchannel")

    def _getColor(self, v):
        # returns (facecolor, edgecolor)
        import re
        if v["Transmission"]["SenderID"].startswith("BS"):
            m=re.match('^\D*(\d*)$', v["Transmission"]["ReceiverID"])
        else:
            m=re.match('^\D*(\d*)$', v["Transmission"]["SenderID"])

        userID = int(m.group(1))

        wrapped = userID % 1000

        r = 0.3 + (wrapped % 10) * 0.07
        g = 0.3 + ((wrapped / 10) % 10) * 0.07
        b = 0.3 + ((wrapped / 100) % 10) * 0.07
        facecolor = (r,g,b)

        edgecolor = (0.0, 0.0, 0.0)
        if v.has_key("SchedulingTimeSlot") and v["SchedulingTimeSlot"].has_key("HARQ"):
            if not v["SchedulingTimeSlot"]["HARQ"]["NDI"]:
                edgecolor = (0.8, 0.0, 0.0)

        return (facecolor, edgecolor)

    def setSelectors(self, senderSelector, receiverSelector, customFilterCheckbox, customFilter):
        self.senderSelector = senderSelector
        self.receiverSelector = receiverSelector
        self.customFilterCheckbox = customFilterCheckbox
        self.customFilter = customFilter

    def getSelectedSenders(self):
        selectedSenders = []
        if self.senderSelector is not None:
            items = self.senderSelector.selectedItems()
            for it in items:
                if it.isSelected():
                    selectedSenders.append(str(it.data(0).toString()))
        return selectedSenders

    def getSelectedReceivers(self):
        selectedReceivers = []
        if self.receiverSelector is not None:
            items = self.receiverSelector.selectedItems()
            for it in items:
                if it.isSelected():
                    selectedReceivers.append(str(it.data(0).toString()))
        return selectedReceivers

    def applyCustomFilter(self, entry):
        
        if self.customFilter is None:
            return True

        if self.customFilterCheckbox.checkState() == QtCore.Qt.Unchecked:
            return True

        code = str(self.customFilter.document().toPlainText())

        g ={}
        l={}
        
        try:
            exec code in g,l
        except:
            import sys
            m = ""
            info = sys.exc_info()
            m += "!!!Unexpected Error of type %s!!!" % info[0]
            m += str(info[1])

            if info[2] is not None:
                import traceback
                for entry in traceback.format_tb(info[2]):
                    entry = entry.rstrip("\n")
                    for line in entry.split("\n"):
                        m += line
            print m
  
            f = self.customFilter.document().defaultFont()
            f.setUnderline(True)
            self.customFilter.document().setDefaultFont(f)
            return True

        try:
            toBeCalled = l["filter"]
            r = toBeCalled(entry.key, entry.value)

            f = self.customFilter.document().defaultFont()
            f.setUnderline(False)
            self.customFilter.document().setDefaultFont(f)      
            return r
        except:
            import sys
            m = ""
            info = sys.exc_info()
            m += "!!!Unexpected Error of type %s!!!" % info[0]
            m += str(info[1])

            if info[2] is not None:
                import traceback
                for entry in traceback.format_tb(info[2]):
                    entry = entry.rstrip("\n")
                    for line in entry.split("\n"):
                        m += line
            print m
            #QtGui.QMessageBox.critical(self,
            #                           "Error executing your filter",
            #                           m)

            f = self.customFilter.document().defaultFont()
            f.setUnderline(True)
            self.customFilter.document().setDefaultFont(f)
            return True

        f = self.customFilter.document().defaultFont()
        f.setUnderline(False)
        self.customFilter.document().setDefaultFont(f)

        return True
