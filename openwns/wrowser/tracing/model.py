from PyQt4 import QtCore, QtGui
import json
import desktopcouch

def importFile(filename, dbname):
    progress = QtGui.QProgressDialog("Importing data", "Stop", 0 ,3)
    progress.setWindowModality(QtCore.Qt.WindowModal)
    progress.setCancelButton(None)
    progress.setMinimumDuration(0)

    progress.setValue(1)
    f = open(filename)
    c = f.read()
    f.close()

    progress.setValue(2)

    parsed = json.loads(c)["content"]

    progress.setValue(3)

    
    progress = QtGui.QProgressDialog("Writing %d entries to database" % len(parsed), "Stop", 0, int(len(parsed)/500) +1)
    progress.setWindowModality(QtCore.Qt.WindowModal)
    progress.setCancelButton(None)
    progress.setMinimumDuration(0)

    db = desktopcouch.records.server.CouchDatabase(dbname, create=True)
    
    db.add_view("orderByStartTime",
"""
function(doc) {
  if (doc.Transmission)
  {
      emit(doc.Transmission.Start, doc);
  }
}
""", "", "wrowser")

    db.add_view("senders",
"""
function(doc) {
  emit(doc.Transmission.SenderID, null);
}
""", 
"""
function(keys, values) {
   return true;
}
""",
"wrowser")

    db.add_view("receivers",
"""
function(doc) {
  emit(doc.Transmission.ReceiverID, null);
}
""", 
"""
function(keys, values) {
   return true;
}
""",
"wrowser")



    i = 1
    recordsToAdd = []
    for entry in parsed:
        r = desktopcouch.records.record.Record(record_type="http://openwns.org/couchdb/phytrace")
        r["Transmission"] = entry["Transmission"]
        if entry.has_key("SINREst"):
            r["SINREst"] = entry["SINREst"]
        if entry.has_key("SchedulingTimeSlot"):
            r["SchedulingTimeSlot"] = entry["SchedulingTimeSlot"]
        recordsToAdd.append(r)
        if len(recordsToAdd) > 500:
            db.put_records_batch(recordsToAdd)
            recordsToAdd = []
            progress.setValue(i)
            i = i + 1

    progress.setValue(i+1)
    db.put_records_batch(recordsToAdd)


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
        self.headerNames.append("Source.ID")
        self.headerNames.append("Destination.ID")
        self.headerNames.append("SINR")
        self.headerNames.append("TS.HARQ.NDI")
        self.headerNames.append("TS.HARQ.Process")
        self.headerNames.append("TS.HARQ.TID")
        self.headerNames.append("TS.HARQ.RetryCounter")
        self.headerNames.append("Transmission.Start")
        self.headerNames.append("Transmission.Stop")
        self.headerNames.append("Transmission.SC")
        self.headerNames.append("Receiver.ID")
        self.headerNames.append("Sender.ID")


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
        i["Receiver.ID"] = item.value["Transmission"]["ReceiverID"]
        i["Sender.ID"] = item.value["Transmission"]["SenderID"]
        i["Source.ID"] = item.value["Transmission"]["SourceID"]
        i["Destination.ID"] = item.value["Transmission"]["DestinationID"]
        i["SINR"] = str(float(item.value["Transmission"]["RxPower"]) - float(item.value["Transmission"]["InterferencePower"]))

        if item.value.has_key("SchedulingTimeSlot"):
            if item.value["SchedulingTimeSlot"]["HARQ"]["enabled"]:
                i["TS.HARQ.NDI"] = str(item.value["SchedulingTimeSlot"]["HARQ"]["NDI"])
                i["TS.HARQ.Process"] = str(item.value["SchedulingTimeSlot"]["HARQ"]["ProcessID"])
                i["TS.HARQ.TID"] = str(item.value["SchedulingTimeSlot"]["HARQ"]["TransportBlockID"])
                i["TS.HARQ.RetryCounter"] = str(item.value["SchedulingTimeSlot"]["HARQ"]["RetryCounter"])
        else:
                i["TS.HARQ.NDI"] = ""
                i["TS.HARQ.Process"] = ""
                i["TS.HARQ.TID"] = ""
                i["TS.HARQ.RetryCounter"] = ""

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

class CodeSnippetModel(QtCore.QAbstractItemModel):

    def __init__(self, parent=None):
        QtCore.QAbstractItemModel.__init__(self, parent)

        import os

        self.dir = os.path.join(os.environ['HOME'], '.wns', 'traceFilters')

        if not os.path.exists(self.dir):
            os.mkdir(self.dir)

        self.snippets = []

        self.load()

        if len(self.snippets) == 0:

            self.snippets.append(["Example", """
def filter(key, value):
   # The function named filter will be called from wrowser
   # do not rename it or change the number of mandatory parameters
   # Return True if you want to include this element in the frame viewer
   # Return False otherwise

   # Look in the console output to see fields
   print key
   print value

   # Check if element exists before accessing it
   if value.has_key("Transmission"):
      if value["Transmission"].has_key("SenderID"):
          return value["Transmission"]["SenderID"] == "BS2"
   return False
"""])
            self.save()

    def load(self):
        import os
        oldpath = os.getcwd()
        os.chdir(self.dir)
        import glob
        files = glob.glob("*.py")
        for filename in files:
            key = filename.rstrip("y")
            key = key.rstrip("p")
            key = key.rstrip(".")

            f = open(filename)
            c = f.read()
            f.close()
            self.snippets.append([key, c])

        os.chdir(oldpath)

    def save(self):
        import os
        oldpath = os.getcwd()
        os.chdir(self.dir)

        for (k,v) in self.snippets:
            f = open(k+".py","w")
            f.write(v)
            f.close()

        os.chdir(oldpath)

    def delete(self, key):
        import os
        oldpath = os.getcwd()
        os.chdir(self.dir)

        os.remove(str(key)+".py")

        os.chdir(oldpath)
        
        
        
    def rowCount(self, parent = QtCore.QModelIndex()):
        if parent.isValid():
            return 0
        else:
            return len(self.snippets)

    def columnCount(self, parent = QtCore.QModelIndex()):
        if parent.isValid():
            return 0
        else:
            return 2

    def data(self, index, role = QtCore.Qt.DisplayRole):
        if not index.isValid() or index.row() >= self.rowCount():
            return QtCore.QVariant()

        if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:
            return QtCore.QVariant(self.snippets[index.row()][index.column()])

        return QtCore.QVariant()

    def index(self, row, column, parent = QtCore.QModelIndex()):
        return self.createIndex(row, column, 0)

    def parent(self, index):
        return QtCore.QModelIndex()

    def setData(self, index, data, role = QtCore.Qt.EditRole):
        if role == QtCore.Qt.EditRole:
            self.snippets[index.row()][index.column()] = data.toString()
            self.save()
            self.emit(QtCore.SIGNAL("dataChanged(const QModelIndex&,const QModelIndex&)"), index, index)
            return True
        return False

    def flags(self, index):
        if not index.isValid():
            return QtCore.Qt.ItemIsEnabled

        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable

    def insertRows(self, row, count, parent):
        self.beginInsertRows(QtCore.QModelIndex(), row, row+count)

        for i in xrange(count):
            print "Inserting %d" % i
            self.snippets.insert(row+i, ["", "def filter(key, value):\n   return True"])

        self.endInsertRows()

        return True

    def remove(self, rowindex):

        msgBox = QtGui.QMessageBox()
        msgBox.setText("Remove %s" % self.snippets[rowindex][0])
        msgBox.setInformativeText("This will permanently delete the filter. Make sure you have a copy.")
        msgBox.setStandardButtons(QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel);
        msgBox.setDefaultButton(QtGui.QMessageBox.Cancel);
        ret = msgBox.exec_();
        
        if ret == QtGui.QMessageBox.Ok:
            e = self.snippets.pop(rowindex)
            self.delete(e[0])
            self.emit(QtCore.SIGNAL("modelReset()"))
