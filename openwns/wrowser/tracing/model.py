from PyQt4 import QtCore, QtGui

def importFile(filename, dbname):
    print "Needs to be implemented, but importing %s to %s" % (filename, dbname)

class TraceEntryTableModel(QtCore.QAbstractTableModel):

    def __init__(self, parent = None):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self.headerNames = []
        self.headerNames.append("Transmission.Start")
        self.headerNames.append("Transmission.Stop")
        self.headerNames.append("Transmission.SC")
        self.headerNames.append("Receiver.ID")
        self.theData=[]

    def rowCount(self, parent = QtCore.QModelIndex()):
        if parent.isValid():
            return 0
        else:
            return len(self.theData)

    def columnCount(self, parent = QtCore.QModelIndex()):
        if parent.isValid():
            return 0
        else:
            return len(self.headerNames)

    def headerData(self, section, orientation, role):
        if role == QtCore.Qt.DisplayRole:
            return QtCore.QVariant(self.headerNames[section])
        return QtCore.QVariant()

    def data(self, index, role = QtCore.Qt.DisplayRole):
        if not index.isValid() or index.row() >= self.rowCount():
            return QtCore.QVariant()

        if role == QtCore.Qt.DisplayRole:
            key = self.headerNames[index.column()]
            if self.theData[index.row()].has_key(key):
                    return QtCore.QVariant(self.theData[index.row()][key])

        return QtCore.QVariant()


    def addItem(self, item):
        i = {}

        for e in self.theData:
            if e["_data"] == item:
                # No duplicates
                return
            
        i["Transmission.Start"] = item.value["Transmission"]["Start"]
        i["Transmission.Stop"] = item.value["Transmission"]["Stop"]
        i["Transmission.SC"] = item.value["Transmission"]["Subchannel"]
        i["Receiver.ID"] = item.value["Receiver"]["ID"]
        i["_data"] = item

        self.theData.append(i)
        self.reset()

    def clear(self):
        self.theData = []
        self.reset()
    
    def sort(self, column, order):
        if order == 0:
            reverse = False
        else:
            reverse = True

        key = self.headerNames[column]

        self.theData = sorted(self.theData, key=lambda i:i[key], reverse=reverse)
        self.reset()
