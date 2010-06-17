from PyQt4 import QtCore, QtGui
import json
import desktopcouch

def importFile(filename, dbname):
    progress = QtGui.QProgressDialog("Importing data", "Stop", 0 ,6)
    progress.setWindowModality(QtCore.Qt.WindowModal)
    progress.setCancelButton(None)
    progress.setMinimumDuration(0)

    progress.setValue(1)
    progress.setValue(2)
    f = open(filename)
    c = f.read()
    f.close()

    progress.setValue(3)

    parsed = json.loads(c)["content"]

    progress.setValue(4)

    db = desktopcouch.records.server.CouchDatabase(dbname, create=True)
    
    mapjs="""
function(doc) {
  if (doc.Transmission && doc.Receiver)
  {
      emit(doc.Transmission.Start, doc);
  }
}
"""
    reducejs=""

    db.add_view("orderByStartTime", mapjs, reducejs)

    recordsToAdd = []
    for entry in parsed:
        r = desktopcouch.records.record.Record(record_type="http://openwns.org/couchdb/phytrace")
        r["Transmission"] = entry["Transmission"]
        if entry.has_key("SINREst"):
            r["SINREst"] = entry["SINREst"]
        if entry.has_key("Receiver"):
            r["Receiver"] = entry["Receiver"]
        recordsToAdd.append(r)

    progress.setValue(5)
    db.put_records_batch(recordsToAdd)
    progress.setValue(6)

def deleteDB(dbname):
    import desktopcouch.records.server
    import couchdb.client
    port = desktopcouch.find_port()
    db = desktopcouch.records.server.OAuthCapableServer('http://localhost:%s/' % port)

    del db[dbname]

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
