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

"""This module contains the interface to the campaign data structure.
"""
import operator

from wrowser.Tools import objectFilter, ObjectFilterError

import Representations
import Errors
import Graphs
import dataacquisition

class Facade:
    """Interface to campaign data structure.
    """
    def __init__(self, campaign):
        self.__campaign = campaign

    def isEmpty(self):
        for parameterName in self.getParameterNames():
            if len(self.getValuesOfParameter(parameterName)) > 0:
                   return False
        return True

    def getScenarios(self):
        return self.campaign.scenarios

    def filteredByExpression(self, filterExpression):
        """Filter campaign by filterExpression.

        Returns a Facade with a campaign containing only the scenarios
        whose simulation parameters match 'filterExpression'

        Raises Errors.InvalidFilterExpression, if 'filterExpression' is
        not a valid python filter expression.
        """
        assert(type(filterExpression) == type(str()))
        try:
            return self.__class__(Representations.Campaign(objectFilter(filterExpression, self.campaign.scenarios, lambda x: x.parameters), self.campaign.parameterNames))
        except ObjectFilterError:
            raise Errors.InvalidFilterExpression(filterExpression)

    def filteredBySelection(self, filterParameters):
        """Filter campaign by allowed parameter values.

        Returns a Facade with a campaign containing only the scenarios
        whose simulation parameter values are contained in 'filterParameters'.

        'filterParameters' must be a dict with the parameter names as keys and
        its values must be lists containing all allowed values for that parameter.
        """
        assert(type(filterParameters) == type(dict()))

        # one could write the following in one line, but no one would understand, me neither
        def scenarioMatches(scenario):

            def parameterMatches(parameter):
                # parameter is a tuple (name, value)
                parameterName = parameter[0]
                parameterValue = parameter[1]
                # filterParameters is a dict with the parameterName as key
                # and the list of allowed values for that parameter as value
                allowedValues = filterParameters[parameterName]
                # calculate ((False or parameterValue == allowedValues[0]) or parameterValue == allowedValues[1]) ...
                return reduce(lambda accu, allowedValue: accu or parameterValue == allowedValue, allowedValues, False)

            # the scenario's parameters as list of tuples (name, value)
            parameters = scenario.parameters.items()
            # calculate ((True and parameterMatches(parameters[0])) and parameterMatches(parameters[1])) ...
            return reduce(lambda accu, parameter: accu and parameterMatches(parameter), parameters, True)

        return self.__class__(Representations.Campaign(filter(scenarioMatches, self.campaign.scenarios), self.campaign.parameterNames))

    def getParameterNames(self):
        """Return the names of the campaign's parameters.
        """
        return self.campaign.parameterNames

    def getValuesOfParameter(self, parameterName):
        """Return all values of a parameter.

        Returns a set of all values for the simulation parameter
        given by 'parameterName'.
        """
        assert(type(parameterName) == type(str()))
        valueSet = set()
        for scenario in self.campaign.scenarios:
            valueSet |= set([scenario.parameters[parameterName]])
        return valueSet

    def isNumericParameter(self, parameterName):
        """Check if 'parameterName' has only numeric values
        """
        # we only check for 1-dimensional numeric types, so no complex no.
        numericTypes = [type(bool()), type(int()), type(long()), type(float())]
        result = True
        for value in self.getValuesOfParameter(parameterName):
            if type(value) not in numericTypes:
                result = False
        return result

    @staticmethod
    def getScenarioParameterValues(scenario, parameterNames):
        """Return the values for a set of parameters in a scenario.

        'parameterNames' must be a sequence containing the names
        of the parameters whose values are to be fetched from 'scenario'.

        Returns a list with the values on the corresponding positions.
        """
        assert(isinstance(scenario, Representations.Scenario))
        assert(operator.isSequenceType(parameterNames))
        values = []
        for parameterName in parameterNames:
            values.append(scenario.parameters[parameterName])
        return values

    def getNotChangingParameterNames(self):
        """Return the names of the parameters that do not vary.

        Returns a set with the names of all parameters that do
        not change across the scenarios.
        """
        if len(self.campaign.scenarios) == 0:
            return set()
        notChangingParameterNames = set(self.campaign.parameterNames)
        initialValues = self.campaign.scenarios[0].parameters
        for scenario in self.campaign.scenarios[1:]:
            # todo: refactor: do not iterate over already marked parameters
            for parameterName in self.campaign.parameterNames:
                if scenario.parameters[parameterName] != initialValues[parameterName]:
                    notChangingParameterNames -= set([parameterName])
        return notChangingParameterNames

    def getChangingParameterNames(self):
        """Return the names of the parameters that do vary.

        Returns a set with the names of all parameters that do
        change across the scenarios.
        """
        return set(self.campaign.parameterNames) - self.getNotChangingParameterNames()

    class __UnionAndIntersection:
        """Helper class for getProbeNames.
        """
        def __init__(self, union, intersection):
            self.union = union
            self.intersection = intersection

    def getProbeNames(self, probeClass = None):
        """Return the probe names of the campaign.

        getProbeNames().union will contain all probe names found, whereas
        getProbeNames().intersection only the names, that are in all scenarios.
        """
        try:
            probeNames = Facade.__UnionAndIntersection(union = set(self.campaign.scenarios[0].probes.keys()),
                                                       intersection = set(self.campaign.scenarios[0].probes.keys()))
        except IndexError:
            return Facade.__UnionAndIntersection(set(), set())
        else:
            for scenario in self.campaign.scenarios[1:]:
                # probeNames.union is a set. A set has a method union...
                probeNames.union = probeNames.union.union(set(scenario.probes.keys()))
                # likewise
                probeNames.intersection = probeNames.intersection.intersection(set(scenario.probes.keys()))
            if probeClass != None:
                probeNames.union = [probeName for probeName in probeNames.union if self.getProbeClass(probeName).probeType == probeClass.probeType]
                probeNames.intersection = [probeName for probeName in probeNames.intersection if self.getProbeClass(probeName).probeType == probeClass.probeType]
            return probeNames

    def getProbeClass(self, probeName):
        """Return the class of a probe.

        Returns the probe class of the specified probe.
        """
        assert(type(probeName) == type(str()))
        # not all scenarios have the same probes, so let's find the first
        # one that contains a probe of the given name
        for scenario in self.campaign.scenarios:
            if scenario.probes.has_key(probeName):
                return scenario.probes[probeName].source.probeClass
        return None

    def getProbeDescription(self, probeName):
        """Return the description of a probe.

        Returns the description of the specified probe.
        """
        assert(type(probeName) == type(str()))
        # not all scenarios have the same probes, so let's find the first
        # one that contains a probe of the given name
        for scenario in self.campaign.scenarios:
            if scenario.probes.has_key(probeName):
                return scenario.probes[probeName].data.description

    def getProbeScenarios(self, probeName):
        """Return which scenarios contain a probe.

        Returns a list of scenarios that contain the
        given probe.
        """
        assert(type(probeName) == type(str()))
        return [scenario for scenario in self.campaign.scenarios if scenario.probes.has_key(probeName)]

    def getProbeParameters(self, probeName):
        """Return for which simulation parameters the given probe was written.

        Returns a dict with the parameters as keys and as values a set
        of the simulation parameter values.
        """
        assert(type(probeName) == type(str()))
        values = {}
        for scenario in self.getProbeScenarios(probeName):
            for parameterName in scenario.parameters.keys():
                if not values.has_key(parameterName):
                    values[parameterName] = set()
                else:
                    values[parameterName].add(scenario.parameters[parameterName])
        return values

    def getAllProbeData(self, probeName):
        assert(type(probeName) == type(str()))
        result = list()
        for scenario in self.campaign.scenarios:
            probeValues = dict()
            for probe in scenario.probes.values():
                if probe.name == probeName:
                    if hasattr(probe.data, "valueNames"):
                        for valueName in probe.data.valueNames:
                            probeValues[valueName] = getattr(probe.data, valueName)
            result.append((scenario.parameters, probeValues))
        return result

    def getAllProbeDataExtended(self, probeName):
        assert(type(probeName) == type(str()))
        result = list()
        for scenario in self.campaign.scenarios:
            probeValues = dict()
            for probe in scenario.probes.values():
                if probe.name == probeName:
                    if hasattr(probe.data, "probeInfoNames"):
                        for probeInfoName in probe.data.probeInfoNames:
                            probeValues[probeInfoName] = getattr(probe.data, probeInfoName)
            result.append((scenario.parameters, probeValues))
        return result

    def getProbeFilterExpression(self, probeName):
        """Construct a filter expression to let a probe appear in all filtered scenarios.
        """
        assert(type(probeName) == type(str()))
        filterExpression = ""
        for name, valuesSet in self.getProbeParameters(probeName).items():
            if valuesSet != self.getValuesOfParameter(name):
                if len(filterExpression) > 0:
                    filterExpression += " and "
                subFilterExpression = ""
                for value in valuesSet:
                    if len(subFilterExpression) > 0:
                        subFilterExpression += " or "
                    subFilterExpression += name + " == "
                    if type(value) == type(str()):
                        subFilterExpression += "'" + value + "'"
                    else:
                        subFilterExpression += str(value)
                filterExpression += "(" + subFilterExpression + ")"
        return filterExpression

    def acquireGraphs(self, acquireScenarioData, progressNotify = None, progressReset = None, graphClass = Graphs.Graph):
        if len(self.campaign.scenarios) == 0:
            raise Errors.NoScenariosFound()
        graphs = Graphs.GraphInstantiator(graphClass)
        errors = list()
        maxIndex = len(self.campaign.scenarios) - 1
        if callable(progressReset):
            progressReset()
        for index, scenario in enumerate(self.campaign.scenarios):
            if callable(progressNotify):
                msg = "Acquiring data..."
                msg += "\n" + self.getParameterString(scenario.parameters)
                progressNotify(index, maxIndex, msg)
            acquireScenarioData(scenario, graphs, errors)
        graphsList = graphs.graphsAsList()
        maxIndex = len(graphsList) - 1
        if graphClass == Graphs.Graph or graphClass == Graphs.AggregatedGraph:
            if callable(progressReset):
                progressReset()
            for index, graph in enumerate(graphsList):
                if callable(progressNotify):
                    msg = "Processing and sorting graph points..."
                    msg += "\n" + str(graph.identity)
                    progressNotify(index, maxIndex, msg)
                graph.process()
        graphsList.sort(key = operator.attrgetter("sortkey"))
        return graphsList, errors

    def getGraphs(self, xParameter, yProbeNames, yProbeEntry, aggregationParameter = '', plotConfidenceIntervals = False, confidenceLevel = 0.95, progressNotify = None, progressReset = None, plotNotAggregatedGraphs = False, useXProbe = False, xProbeName = None, xProbeEntry = None, useYProbe = True):

        graphs = list()
        errors = list()
        parameterName = xParameter
        if aggregationParameter != '' :
            #print "aggregierter graph"
            xAcquirer = dataacquisition.Compose.ParameterValue(parameterName)

            yAcquirer = dataacquisition.Compose.Probe(yProbeEntry)

            probeDataAcquirer = dataacquisition.Compose.XY(x = xAcquirer, y = yAcquirer, graphWriter = dataacquisition.Compose.aggregateGraphWriter)
            probeDataAcquirers = dict([(probeName, probeDataAcquirer) for probeName in yProbeNames])

            parameterNames = list(self.getChangingParameterNames() - set([parameterName, aggregationParameter]))

            showConfidenceLevel = plotConfidenceIntervals
            scenarioDataAcquirer = dataacquisition.Scenario(probeDataAcquirers, parameterNames, dataacquisition.Aggregator.Mean(yProbeEntry, confidenceLevel, showConfidenceLevel))
            #print " aquire graphs 1 aggregated graph"

            graphsHelp, errorsHelp = self.acquireGraphs(acquireScenarioData = scenarioDataAcquirer,
                                                      progressNotify = progressNotify,
                                                      progressReset = progressReset,
                                                      graphClass = Graphs.AggregatedGraph)
            graphs += graphsHelp
            errors += errorsHelp

        if plotNotAggregatedGraphs or aggregationParameter == '':
            #if plotNotAggregatedGraphs: print "plot originals"
            if useXProbe:
                #print " probe fuer x achse"
                xAcquirer = dataacquisition.Compose.ProbeEntryOfProbe(xProbeName, xProbeEntry)
            else:
                #print " parameter fuer x achse"
                xAcquirer = dataacquisition.Compose.ParameterValue(parameterName)

            if useYProbe:
                #print " probe fuer y achse"
                if plotConfidenceIntervals and yProbeEntry == 'mean':
                    #print "  plotte konfidenzintervalle"  
                    yAcquirer = dataacquisition.Compose.Probe(yProbeEntry)
                    probeDataAcquirer = dataacquisition.Compose.XY(x = xAcquirer, y = yAcquirer, graphWriter = dataacquisition.Compose.aggregateGraphWriter)
                else:
                    #print "  plotte keine konfidenzintervalle"  
                    yAcquirer = dataacquisition.Compose.ProbeEntry(yProbeEntry)
                    probeDataAcquirer = dataacquisition.Compose.XY(x = xAcquirer, y = yAcquirer)

                probeDataAcquirers = dict([(probeName, probeDataAcquirer)
                                           for probeName in yProbeNames])
            else:
                #print " parameter fuer y achse"
                yAcquirer = dataacquisition.Compose.ParameterValue(parameterName)

                probeDataAcquirers = {None : dataacquisition.Compose.XY(x = xAcquirer, y = yAcquirer)}

            parameterNames = list(self.getChangingParameterNames() - set([parameterName]))
            if plotConfidenceIntervals and yProbeEntry == 'mean':
                #print " plotte konfidenzintervalle"  
                scenarioDataAcquirer = dataacquisition.Scenario(probeDataAcquirers, parameterNames, dataacquisition.Aggregator.WeightedMeanWithConfidenceInterval(confidenceLevel))
                #print " aquire graphs 2 aggregated "
                graphsHelp, errorsHelp = self.acquireGraphs(acquireScenarioData = scenarioDataAcquirer,
                                                                progressNotify = progressNotify,
                                                                progressReset = progressReset,
                                                                graphClass = Graphs.AggregatedGraph)
            else:
                #print " plotte keine konfidenzintervalle"  
                scenarioDataAcquirer = dataacquisition.Scenario(probeDataAcquirers, parameterNames)
                #print " aquire graphs 3 not aggregated"

                graphsHelp, errorsHelp = self.acquireGraphs(acquireScenarioData = scenarioDataAcquirer,
                                                                progressNotify = progressNotify,
                                                                progressReset = progressReset)

            graphs += graphsHelp
            errors += errorsHelp

        return graphs

    def getHistograms(self, probeNames, function, aggregationParameter = '', progressNotify = None, progressReset = None, plotNotAggregatedGraphs = False):

        funType = function

        graphs = list()
        errors = list()

        if  aggregationParameter != '' :
            probeDataAcquirer = getattr(dataacquisition.Probe, funType)(graphWriter = dataacquisition.Probe.aggregateGraphWriter)
            probeDataAcquirers = dict([(probeName, probeDataAcquirer) for probeName in probeNames])

            parameterNames = list(self.getChangingParameterNames() - set([aggregationParameter]))
            scenarioDataAcquirer = dataacquisition.Scenario(probeDataAcquirers, parameterNames, dataacquisition.Aggregator.weightedXDF)

            graphsHelp, errorsHelp = self.acquireGraphs(acquireScenarioData = scenarioDataAcquirer,
                                                            progressNotify = progressNotify,
                                                            progressReset = progressReset,
                                                            graphClass = Graphs.AggregatedGraph)

            graphs += graphsHelp
            errors += errorsHelp

        if plotNotAggregatedGraphs or aggregationParameter == '' :
            probeDataAcquirer = getattr(dataacquisition.Probe, funType)()
            probeDataAcquirers = dict([(probeName, probeDataAcquirer) for probeName in probeNames])

            parameterNames = list(self.getChangingParameterNames())

            scenarioDataAcquirer = dataacquisition.Scenario(probeDataAcquirers = probeDataAcquirers,
                                                            parameterNames = parameterNames)

            graphsHelp, errorsHelp = self.acquireGraphs(acquireScenarioData = scenarioDataAcquirer,
                                                            progressNotify = progressNotify,
                                                            progressReset = progressReset)


            graphs += graphsHelp
            errors += errorsHelp

        return graphs

    def getLogEvalEntries(self, probeName, progressNotify = None, progressReset = None):
        probeDataAcquirer = dataacquisition.Probe.LogEval()
        parameterNames = list(self.getChangingParameterNames())
        scenarioDataAcquirer = dataacquisition.Scenario(probeDataAcquirers = {probeName : probeDataAcquirer},
                                                        parameterNames = parameterNames)
        graphs, errors =  self.acquireGraphs(progressNotify = progressNotify,
                                             progressReset = progressReset,
                                             acquireScenarioData = scenarioDataAcquirer)
        if len(errors) > 0:
            raise Errors.MultipleErrors(errors, graphs = graphs)
        else:
            return graphs

    @staticmethod
    def getGraphDescription(graph):
        return str(graph.identity)

    @staticmethod
    def getGraphSortKey(graph):
        return graph.sortkey

    @staticmethod
    def getParameterString(parametersDict):
	if len(parametersDict) > 0:
	    s = str(parametersDict.keys()[0]) + ": " + str(parametersDict.values()[0])
	    for parameter in parametersDict.keys()[1:]:
		s += ", " + str(parameter) + ": " + str(parametersDict[parameter])
	    return s
	else:
	    return ""

    def __getCampaign(self):
        return self.__campaign

    def __setCampaign(self, campaign):
        self.__campaign = campaign

    campaign = property(__getCampaign, __setCampaign)

class DoNotSelectProbeSelectUI:
    """A no-user-interface for CampaignReaders.

    Pass an instance of this class to a CampaignReader, if
    you do not want to have an user interface and if you
    want to accept all columns besides the ones passed
    to 'do()' as deselectedColumns (see the CampaignReader's
    docu to know which that are).
    """
    def do(self, columns, deselectedColumns):
        return [column for column in columns if column not in deselectedColumns]
