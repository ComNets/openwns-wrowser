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

from openwns.wrowser.simdb.Parameters import Parameters
from openwns.wrowser.simdb.ProbeObjects import getSingleResult, getMultipleResults, Moments, PDFs, LogEvals, BatchMeans, Lres, Dlres, Tables
from openwns.wrowser.simdb.Database import Database
from openwns.wrowser.Configuration import Configuration

import Representations

class ProbeReader:

    def __init__(self, campaignId, scenarioId, probeName, probeClass):
        self.campaignId = campaignId
        self.scenarioId = scenarioId
        self.probeName = probeName
        self.probeClass = probeClass

    def getName(self):
        return self.probeName

    def getData(self):
        if self.probeClass.probeType in ['Moments', 'PDF', 'LogEval', 'BatchMeans', 'LRE', 'DLRE']:
            probe = getSingleResult(self.probeClass, "campaign_id = %d AND scenario_id = %d AND alt_name = \'%s\'" % (self.campaignId, self.scenarioId, self.probeName))
        else:
            probe = self.probeClass(self.campaignId, self.scenarioId, self.probeName)
        return probe

class ScenarioReader:

    def __init__(self, campaignId, scenarioId):
        self.campaignId = campaignId
        self.scenarioId = scenarioId

    def getProbes(self):
        probes = {}
        cursor = Database.getCursor()
        cursor.execute("SELECT DISTINCT alt_name FROM pd_fs WHERE campaign_id=%d AND scenario_id=%d" % (self.campaignId, self.scenarioId))
        pdfProbes = [(it[0], PDFs) for it in cursor.fetchall()]
        cursor.execute("SELECT DISTINCT alt_name FROM moments WHERE campaign_id=%d AND scenario_id=%d" % (self.campaignId, self.scenarioId))
        momentProbes = [(it[0], Moments) for it in cursor.fetchall()]
        cursor.execute("SELECT DISTINCT alt_name FROM log_evals WHERE campaign_id=%d AND scenario_id=%d" % (self.campaignId, self.scenarioId))
        logEvalProbes = [(it[0], LogEvals) for it in cursor.fetchall()]
        cursor.execute("SELECT DISTINCT alt_name FROM batch_means WHERE campaign_id=%d AND scenario_id=%d" % (self.campaignId, self.scenarioId))
        batchMeansProbes = [(it[0], BatchMeans) for it in cursor.fetchall()]
        cursor.execute("SELECT DISTINCT alt_name FROM lres WHERE campaign_id=%d AND scenario_id=%d" % (self.campaignId, self.scenarioId))
        lreProbes = [(it[0], Lres) for it in cursor.fetchall()]
        cursor.execute("SELECT DISTINCT alt_name FROM dlres WHERE campaign_id=%d AND scenario_id=%d" % (self.campaignId, self.scenarioId))
        dlreProbes = [(it[0], Dlres) for it in cursor.fetchall()]
        cursor.execute("SELECT DISTINCT name, type FROM tables WHERE campaign_id=%d AND scenario_id=%d" % (self.campaignId, self.scenarioId))
        tableProbes = [(it[0] + " " + it[1], Tables) for it in cursor.fetchall()]
        for probeName, probeClass in pdfProbes + momentProbes + logEvalProbes + batchMeansProbes + lreProbes + dlreProbes + tableProbes:
            probes[probeName] = Representations.Probe(ProbeReader(self.campaignId, self.scenarioId, probeName, probeClass))
        return probes

class HighLatencyScenarioReader:

    def __init__(self, campaignId, scenarioId, campaignProbes):
        self.campaignId = campaignId
        self.scenarioId = scenarioId
        self.campaignProbes = campaignProbes

    def getProbes(self):
        return self.campaignProbes.getProbesOfScenario(self.scenarioId)

class CampaignProbes:
    def __init__(self, campaignId, progressNotify = None):
        self.campaignId = campaignId
        self.scenarios = {}

        cursor = Database.getCursor()
        tables = [("pd_fs", PDFs), ("moments", Moments), ("log_evals", LogEvals), ("batch_means", BatchMeans), ("lres", Lres), ("dlres", Dlres)]
        index = 0
        maxIndex = len(tables) + 1
        for table in tables:
            if callable(progressNotify):
                progressNotify(index, maxIndex, "reading probes of table '" + table[0] + "'")
            cursor.execute("SELECT DISTINCT alt_name, scenario_id FROM %s WHERE campaign_id=%d" % (table[0], self.campaignId))
            for it in cursor.fetchall():
                if not self.scenarios.has_key(it[1]):
                    self.scenarios[it[1]] = []
                self.scenarios[it[1]].append((it[0], table[1]))
            index += 1
            if callable(progressNotify):
                progressNotify(index, maxIndex, "read probes of table '" + table[0] + "'")
        if callable(progressNotify):
             progressNotify(index, maxIndex, "reading probes of table 'tables'")
        cursor.execute("SELECT DISTINCT name, type, scenario_id FROM tables WHERE campaign_id=%d" % (self.campaignId))
        for it in cursor.fetchall():
            if not self.scenarios.has_key(it[1]):
                self.scenarios[it[1]] = []
            self.scenarios[it[1]].append((it[0] + " " + it[1], Tables))
        if callable(progressNotify):
             progressNotify(index+1, maxIndex, "read probes of table 'tables'")

    def getProbesOfScenario(self, scenarioId):
        probes = {}
        # if scenarioID is not available, not probes are written for this scenarios -> return empty dict
        if self.scenarios.has_key(scenarioId):
            for probeName, probeClass in self.scenarios[scenarioId]:
                probes[probeName] = Representations.Probe(ProbeReader(self.campaignId, scenarioId, probeName, probeClass))
        return probes

class CampaignReader:

    def __init__(self, campaignId, paramSelectUi, progressNotify = None, prefetchProbeNames = False):
        self.campaignId = campaignId
        self.progressNotify = progressNotify
        self.prefetchProbeNames = prefetchProbeNames
        self.stopped = False

    def stop(self):
        self.stopped = True

    def read(self):
        parametersReader = Parameters(campaignId = self.campaignId)
        scenarioParametersDict = parametersReader.readAllScenarios()
        parameters = set()
        scenarios = []
        campaignProbes = CampaignProbes(self.campaignId, self.progressNotify)
        maxIndex = len(scenarioParametersDict.items())
        for index, scenario in enumerate(scenarioParametersDict.items()):
            if self.stopped :
                break
            scenarioId, scenarioParameters = scenario
            del scenarioParameters["campaignId"]
            scenarioParameters2 = dict()
            for parameter in scenarioParameters:
                parameters |= set(scenarioParameters.keys())
                scenarioParameters2[parameter] = scenarioParameters[parameter].getValue()
            scenarioData = Representations.Scenario(HighLatencyScenarioReader(self.campaignId, scenarioId, campaignProbes), scenarioParameters2, self.prefetchProbeNames)
            scenarios.append(scenarioData)
            if callable(self.progressNotify) and ( (index % 10) == 0 or index==(maxIndex-1)) :
                self.progressNotify(index + 1, maxIndex, "reading id " + str(scenarioId))
        #self.progressNotify(maxIndex, maxIndex, "reading id " + str(scenarioId))
        return scenarios, parameters
