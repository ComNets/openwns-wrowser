###############################################################################
# This file is part of openWNS (open Wireless Network Simulator)
# _____________________________________________________________________________
#
# Copyright (C) 2004-2007
# Chair of Communication Networks (ComNets)
# Kopernikusstr. 16, D-52074 Aachen, Germany
# phone: ++49-241-80-27910,
# fax: ++49-241-80-22242
# email: info@openwns.org
# www: http://www.openwns.org
# _____________________________________________________________________________
#
# openWNS is free software; you can redistribute it and/or modify it under the
# terms of the GNU Lesser General Public License version 2 as published by the
# Free Software Foundation;
#
# openWNS is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

import copy
import wrowser.Tools


from PyQt4 import QtCore, QtGui

import Debug

class CampaignDb(QtCore.QAbstractItemModel):

    headerNames = ["User", "Campaign Title", "Campaign Description", "Campaign Size"]

    def __init__(self, campaignIds, parent = None):
        QtCore.QAbstractItemModel.__init__(self, parent)
        self.campaignIds = campaignIds
        for username, campaigns in self.campaignIds.items():
            if None in campaigns.keys():
                del self.campaignIds[username]
        self.sortedCampaignIdsKeys = sorted(campaignIds.keys())

    def getCampaign(self, index):
        userName = self.sortedCampaignIdsKeys[index.internalId()]
        return map(lambda x: x[0], sorted(self.campaignIds[userName].items(), key = lambda x: x[1][0].lower()))[index.row()]

    def columnCount(self, parent = QtCore.QModelIndex()):
        return len(self.headerNames)

    def rowCount(self, parent = QtCore.QModelIndex()):
        if parent.isValid() and parent.internalId() == 1000000001:
            userName = self.sortedCampaignIdsKeys[parent.row()]
            return len(self.campaignIds[userName])
        elif not parent.isValid():
            return len(self.sortedCampaignIdsKeys)
        else:
            return 0

    def parent(self, index = QtCore.QModelIndex()):
        if not index.isValid():
            return QtCore.QModelIndex()
        elif index.internalId() == 1000000001:
            return QtCore.QModelIndex()
        elif index.internalId() < 1000000000:
            return self.index(index.internalId(), 0, QtCore.QModelIndex())
        return QtCore.QModelIndex()

    def index(self, row, column, parent = QtCore.QModelIndex()):
        if not parent.isValid():
            return self.createIndex(row, column, 1000000001)
        elif parent.internalId() == 1000000001:
            return self.createIndex(row, column, parent.row())
        else:
            return self.createIndex(row, column, 1000000000)

    def flags(self, index):
        if not index.isValid():
            return QtCore.Qt.ItemIsEnabled
        if index.internalId() < 1000000000:
            userName = self.sortedCampaignIdsKeys[index.internalId()]
            if sorted(self.campaignIds[userName].values(), key = lambda x: x[0].lower())[index.row()][3]:
                return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable
            else:
                return QtCore.Qt.ItemFlags()
        return QtCore.Qt.ItemIsEnabled

    def headerData(self, section, orientation, role):
        if role != QtCore.Qt.DisplayRole or orientation != QtCore.Qt.Horizontal:
            return QtCore.QVariant()
        return QtCore.QVariant(self.headerNames[section])

    def data(self, index, role = QtCore.Qt.DisplayRole):
        if not index.isValid() or index.internalId() == 1000000000:
            return QtCore.QVariant()

        if role == QtCore.Qt.DisplayRole:
            if index.internalId() == 1000000001 and index.column() == 0:
                return QtCore.QVariant(self.sortedCampaignIdsKeys[index.row()])
            elif index.internalId() < 1000000000 and index.column() == 1:
                userName = self.sortedCampaignIdsKeys[index.internalId()]
                return QtCore.QVariant(sorted(self.campaignIds[userName].values(), key = lambda x: x[0].lower())[index.row()][0])
            elif index.internalId() < 1000000000 and index.column() == 2:
                userName = self.sortedCampaignIdsKeys[index.internalId()]
                return QtCore.QVariant(sorted(self.campaignIds[userName].values(), key = lambda x: x[0].lower())[index.row()][1])
            elif index.internalId() < 1000000000 and index.column() == 3:
                userName = self.sortedCampaignIdsKeys[index.internalId()]
                return QtCore.QVariant(sorted(self.campaignIds[userName].values(), key = lambda x: x[0].lower())[index.row()][2])

        return QtCore.QVariant()

    def getUserRow(self, user):
        for i in range(self.rowCount()):
            desc = str(self.data(self.index(i,0)).toString()) 
            if desc.find(user) != -1 :
                return self.index(i,0)
        return -1
 
class SimulationParameters(QtCore.QAbstractItemModel):

    headerNames = ["Parameter", "Values"]

    def __init__(self, campaign, onlyNumeric = False, parent = None):
        QtCore.QAbstractItemModel.__init__(self, parent)
        self.onlyNumeric = onlyNumeric
        self.setCampaign(campaign, onlyNumeric)
        self.parameterValueCheckStates = {}
        for parameterName in self.parameterNames:
            self.parameterValueCheckStates[parameterName] = {}
            for value in self.parameterValues[parameterName]:
                self.parameterValueCheckStates[parameterName][value] = True

    def setCampaign(self, campaign, onlyNumeric = False):
        Debug.printCall(self, (campaign, onlyNumeric))
        self.emit(QtCore.SIGNAL("layoutAboutToBeChanged()"))
        self.campaign = campaign
        if onlyNumeric:
            self.parameterNames = sorted([name for name in campaign.getParameterNames() if self.campaign.isNumericParameter(name)])
        else:
            self.parameterNames = sorted(list(campaign.getParameterNames()))
        self.parameterValues = {}
        for parameterName in self.parameterNames:
            self.parameterValues[parameterName] = sorted(list(campaign.getValuesOfParameter(parameterName)))
        self.emit(QtCore.SIGNAL("layoutChanged()"))

    def __getValueSelection(self, checkStates):
        selection = {}
        for parameterName in self.parameterNames:
            selection[parameterName] = [value for value in self.parameterValues[parameterName] if checkStates[parameterName][value]]
        return selection

    def getValueSelection(self):
        return self.__getValueSelection(self.parameterValueCheckStates)

    def getParameterValues(self):
        return self.parameterValues

    def getCheckStates(self):
        return self.parameterValueCheckStates

    def columnCount(self, parent = QtCore.QModelIndex()):
        return len(self.headerNames)

    def rowCount(self, parent = QtCore.QModelIndex()):
        if parent.isValid() and parent.internalId() == 1000000001:
            parameterName = self.parameterNames[parent.row()]
            return len(self.parameterValues[parameterName])
        elif not parent.isValid():
            return len(self.parameterNames)
        else:
            return 0

    def parent(self, index = QtCore.QModelIndex()):
        if not index.isValid():
            return QtCore.QModelIndex()
        elif index.internalId() == 1000000001:
            return QtCore.QModelIndex()
        elif index.internalId() < 1000000000:
            return self.index(index.internalId(), 0, QtCore.QModelIndex())
        return QtCore.QModelIndex()

    def index(self, row, column, parent = QtCore.QModelIndex()):
        if not parent.isValid():
            return self.createIndex(row, column, 1000000001)
        elif parent.internalId() == 1000000001:
            return self.createIndex(row, column, parent.row())
        else:
            return self.createIndex(row, column, 1000000000)

    def flags(self, index):
        if not index.isValid():
            return QtCore.Qt.ItemIsEnabled
        if index.internalId() < 1000000000:
            return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsUserCheckable
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def headerData(self, section, orientation, role):
        if role != QtCore.Qt.DisplayRole or orientation != QtCore.Qt.Horizontal:
            return QtCore.QVariant()
        return QtCore.QVariant(self.headerNames[section])

    def data(self, index, role = QtCore.Qt.DisplayRole):
        if not index.isValid() or index.internalId() == 1000000000:
            return QtCore.QVariant()

        if role == QtCore.Qt.DisplayRole:
            if index.internalId() == 1000000001 and index.column() == 0:
                return QtCore.QVariant(self.parameterNames[index.row()])
            elif index.internalId() < 1000000000 and index.column() == 1:
                parameterName = self.parameterNames[index.internalId()]
                values = self.parameterValues[parameterName]
                return QtCore.QVariant(values[index.row()])
        elif role == QtCore.Qt.CheckStateRole and index.internalId() < 1000000000 and index.column() == 1:
            parameterName = self.parameterNames[index.internalId()]
            value = self.parameterValues[parameterName][index.row()]
            if self.parameterValueCheckStates[parameterName][value]:
                return QtCore.QVariant(QtCore.Qt.Checked)
            else:
                return QtCore.QVariant(QtCore.Qt.Unchecked)

        return QtCore.QVariant()

    def setData(self, index, value, role):
        if not index.isValid():
            return False

        if role == QtCore.Qt.CheckStateRole and index.internalId() < 1000000000 and index.column() == 1:
            state = value.toInt()[0]
            parameterName = self.parameterNames[index.internalId()]
            parameterValue = self.parameterValues[parameterName][index.row()]
            if state == QtCore.Qt.Unchecked:
                checkStates = copy.deepcopy(self.parameterValueCheckStates)
                checkStates[parameterName][parameterValue] = False
                if self.campaign.filteredBySelection(self.__getValueSelection(checkStates)).isEmpty():
                    return False
                self.parameterValueCheckStates = checkStates
            elif state == QtCore.Qt.Checked:
                checkStates = copy.deepcopy(self.parameterValueCheckStates)
                checkStates[parameterName][parameterValue] = True
                if self.campaign.filteredBySelection(self.__getValueSelection(checkStates)).isEmpty():
                    return False
                self.parameterValueCheckStates = checkStates
            else:
                return False
            self.emit(QtCore.SIGNAL("dataChanged(const QModelIndex&, const QModelIndex&)"), index, index)
            return True
        return False

    def toggleCheckboxes(self,row=10):
        toggleParam=self.parameterNames[row]
        for value in self.parameterValues[toggleParam] :
            newValue = not self.parameterValueCheckStates[toggleParam][value] 
            self.parameterValueCheckStates[toggleParam][value] = newValue
        if self.campaign.filteredBySelection(self.__getValueSelection(self.parameterValueCheckStates)).isEmpty():
            for value in self.parameterValues[toggleParam] :
                if self.parameterValueCheckStates[toggleParam][value]==False :
                    self.parameterValueCheckStates[toggleParam][value]=True 
                    if not self.campaign.filteredBySelection(self.__getValueSelection(self.parameterValueCheckStates)).isEmpty():
                        break
                    self.parameterValueCheckStates[toggleParam][value]=False


class ProbeNames(QtCore.QAbstractListModel):
    def __init__(self, campaign, probeClasses = [None], parent = None):
        QtCore.QAbstractListModel.__init__(self, parent)
        self.campaign = campaign
        self.probeClasses = probeClasses
        self.filterText = ""
        self.__setupProbeNames()

    def __setupProbeNames(self):
        self.probeNamesUnion = sorted(list(reduce(set.union, [set(self.campaign.getProbeNames(probeClass).union) for probeClass in self.probeClasses])))
        self.probeNamesUnionFiltered = self.getFilteredProbeNames()
        self.probeNamesIntersection = reduce(set.intersection, [set(self.campaign.getProbeNames(probeClass).intersection) for probeClass in self.probeClasses])

    def rowCount(self, parent = QtCore.QModelIndex()):
        if parent.isValid():
            return 0
        else:
            return len(self.probeNamesUnionFiltered)

    def data(self, index, role = QtCore.Qt.DisplayRole):
        if not index.isValid():
            return QtCore.QVariant()

        if role == QtCore.Qt.DisplayRole:
            return QtCore.QVariant(self.getProbeName(index))
        elif role == QtCore.Qt.TextColorRole:
            if self.getProbeName(index) in self.probeNamesIntersection:
                return QtCore.QVariant(QtGui.QColor("black"))
            else:
                return QtCore.QVariant(QtGui.QColor("grey"))

        return QtCore.QVariant()

    def getFilteredProbeNames(self):
        return self.getProbeNamesFilteredBy(self.filterText)

    def getProbeNamesFilteredBy(self, filterText):
        return [probeName for probeName in self.probeNamesUnion if filterText.lower() in probeName.lower()]

    def getProbeName(self, index):
        return self.probeNamesUnionFiltered[index.row()]

    def setFilter(self, filterText):
        self.emit(QtCore.SIGNAL("modelAboutToBeReset()"))
        self.filterText = filterText
        self.probeNamesUnionFiltered = self.getFilteredProbeNames()
        self.emit(QtCore.SIGNAL("modelReset()"))

    def setCampaign(self, campaign):
        self.emit(QtCore.SIGNAL("modelAboutToBeReset()"))
        self.campaign = campaign
        self.__setupProbeNames()
        self.emit(QtCore.SIGNAL("modelReset()"))

    def getProbeIndexes(self, probeList):
        indexes = []
        for probe in probeList :
            if probe in self.probeNamesUnionFiltered: 
                indexes.append(self.createIndex(self.probeNamesUnionFiltered.index(probe),0))
        return indexes            

class ProbeEntries(QtCore.QAbstractListModel):
    def __init__(self, campaign, parent = None):
        QtCore.QAbstractListModel.__init__(self, parent)
        self.campaign = campaign
        self.probeEntries = []

    def rowCount(self, parent = QtCore.QModelIndex()):
        if parent.isValid():
            return 0
        else:
            return len(self.probeEntries)

    def data(self, index, role = QtCore.Qt.DisplayRole):
        if not index.isValid() or index.row() >= self.rowCount():
            return QtCore.QVariant()
        if role == QtCore.Qt.DisplayRole:
            return QtCore.QVariant(self.getProbeEntry(index))
        return QtCore.QVariant()

    def getProbeEntry(self, index):
        return self.probeEntries[index.row()]

    def findProbeEntry(self, text):
        for index, entry in enumerate(self.probeEntries):
            if entry == text:
                return index
        return 1000000001

    def changeProbes(self, probeNames):
        self.probeNames = probeNames
        self.emit(QtCore.SIGNAL("modelAboutToBeReset()"))
        if len(probeNames):
            probeEntries = set(self.__getProbeClassEntries(probeNames[0]))
            for probeName in probeNames[1:]:
                probeEntries &= set(self.__getProbeClassEntries(probeName))
        else:
            probeEntries = set([])
        self.probeEntries = sorted(list(probeEntries))
        self.emit(QtCore.SIGNAL("modelReset()"))

    def setCampaign(self, campaign):
        self.campaign = campaign
        self.changeProbes(self.probeNames)

    def __getProbeClassEntries(self, probeName):
        probeClass = self.campaign.getProbeClass(probeName)
        if probeClass == None:
            return []
        probeEntries = probeClass.valueNames
        probeEntries.sort()
        return probeEntries

class ProbeData(QtCore.QAbstractTableModel):

    def __init__(self, campaign, probeName, parent = None):
        QtCore.QAbstractListModel.__init__(self, parent)
        self.campaign = campaign
        self.probeName = probeName
        self.probeData = campaign.getAllProbeDataExtended(probeName)
        self.parameterNames = list(campaign.getParameterNames())
        #self.valueNames = set()
        self.probeInfoNames = set()
        for data in self.probeData:
            self.probeInfoNames |= set(data[1].keys())
        self.headerNames = self.parameterNames + list(self.probeInfoNames)

    def rowCount(self, parent = QtCore.QModelIndex()):
        if parent.isValid():
            return 0
        else:
            return len(self.probeData)

    def columnCount(self, parent = QtCore.QModelIndex()):
        if parent.isValid():
            return 0
        else:
            return len(self.headerNames)

    def headerData(self, section, orientation, role):
        if role != QtCore.Qt.DisplayRole or orientation != QtCore.Qt.Horizontal:
            return QtCore.QVariant()
        return QtCore.QVariant(self.headerNames[section])

    def data(self, index, role = QtCore.Qt.DisplayRole):
        if not index.isValid() or index.row() >= self.rowCount():
            return QtCore.QVariant()
        if role == QtCore.Qt.DisplayRole:
            key = self.headerNames[index.column()]
            if key in self.parameterNames:
                return QtCore.QVariant(self.probeData[index.row()][0][key])
            elif key in self.probeInfoNames:
                if self.probeData[index.row()][1].has_key(key):
                    return QtCore.QVariant(self.probeData[index.row()][1][key])
        if role == QtCore.Qt.ForegroundRole:
            key = self.headerNames[index.column()]
            if key in self.probeInfoNames:
                return QtCore.QVariant(QtGui.QColor("blue"))
        return QtCore.QVariant()

    def getPath(self, index):
        print "get path to scenario"
        try:
            path = self.probeData[index.row()][1]['filename'] 
            if path.find('scratch') != -1 :
                #print "the scenario was queued with an old simcontrol.py, hence the database does not contain the path to your scenario folder"
                return None 
            return path
        except:
            #print "the scenario has no entry for the probe file, it seems that the scenario is crashed or not finished"
            return None

    def printTable(self):
        for row in range(self.rowCount()):
            for col in range(self.columnCount()):
                desc = str(self.data(self.index(row,col)).toString()) 
                print "col:",col
                print "desc:",desc

class Legend(QtCore.QAbstractListModel):

    def __init__(self, lineWidth = 70, lines = [], labels = [], *args):
        QtCore.QAbstractListModel.__init__(self, *args)
        self.lineWidth = lineWidth
        self.updateLinesNLabels(lines, labels)

    def updateLinesNLabels(self, lines, labels):
        from Tools import renderLineSampleImage
        if len(labels)>0 :
            labels = wrowser.Tools.uniqElements(labels)
        
        if len(lines) != len(labels):
            raise Exception("Models.Legend: " + str(len(lines)) + " graphs, but " + str(len(labels)) + " labels!?")

        self.emit(QtCore.SIGNAL("modelAboutToBeReset()"))
        self.linesLabels = []
        for line, label in zip(lines, labels):
            image = renderLineSampleImage(line[0], self.lineWidth)
            self.linesLabels.append((image, label))
        self.emit(QtCore.SIGNAL("modelReset()"))

    def rowCount(self, parent):
        if parent.isValid():
            return 0
        return len(self.linesLabels)

    def headerData(self, section, orientation, role = QtCore.Qt.DisplayRole):
        return QtCore.QVariant()

    def data(self, index, role = QtCore.Qt.DisplayRole):
        if not index.isValid() or index.column() != 0:
            return QtCore.QVariant()
        line, label = self.linesLabels[index.row()]
        if role == QtCore.Qt.DisplayRole:
            return QtCore.QVariant(label)
        elif role == QtCore.Qt.DecorationRole:
            return QtCore.QVariant(line)
        return QtCore.QVariant()
