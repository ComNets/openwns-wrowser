#! /usr/bin/env python

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

import math
import scipy.special
import scipy.stats


def total(attribute, list):
    return float(reduce(lambda x, y: x + getattr(y, attribute), [0] + list))

def totalSquare(attribute, list):
    return float(reduce(lambda x, y: x + getattr(y, attribute)**2, [0] + list))

class Sum:

    def __init__(self, entryName):
        self.entryName = entryName

    def __call__(self, graph):
        points = list()
        for x, yProbeList in graph.pointsDict.iteritems():
            y = total(self.entryName, yProbeList)
            points.append((x, y))
        return points


class Mean:

    def __init__(self, entryName, confidenceLevel, calculateConfidenceLevel):
        self.entryName = entryName
        self.confidenceLevel = confidenceLevel
        self.calculateConfidenceLevel = calculateConfidenceLevel

    def __call__(self, graph):
        points = list()
        for x, yProbeList in graph.pointsDict.iteritems():
            totalTrials = float(len(yProbeList))
            totalSumOfAllValues = total(self.entryName, yProbeList)
            totalSumOfAllValuesSquare = totalSquare(self.entryName, yProbeList)
            if totalTrials > 0.0:
                y = totalSumOfAllValues/totalTrials
            else:
                y = 0.0
            points.append((x, y))
            if self.calculateConfidenceLevel:
                if totalTrials > 1.0 and (totalSumOfAllValuesSquare - totalSumOfAllValues**2.0/totalTrials) > 0.0:
                    var = 1.0 / (totalTrials - 1.0) * (totalSumOfAllValuesSquare - totalSumOfAllValues**2.0/totalTrials)
                    confInt = math.sqrt(var/totalTrials) * scipy.stats.t.ppf((self.confidenceLevel+1)/2., totalTrials - 1)
                else:
                    confInt = 0.0
                graph.confidenceIntervalDict[x] = confInt
        return points


def weightedMean(graph):
    points = list()
    for x, yProbeList in graph.pointsDict.iteritems():
        totalTrials = total('trials', yProbeList)
        totalSumOfAllValues = total('sum_of_all_values', yProbeList)
        if totalTrials > 0.0:
            y = totalSumOfAllValues/totalTrials
        else:
            y = 0.0
        points.append((x, y))
    return points


class WeightedMeanWithConfidenceInterval:

    def __init__(self, confidenceLevel):
        self.confidenceLevel = confidenceLevel

    def __call__(self, graph):
        points = list()
        for x, yProbeList in graph.pointsDict.iteritems():
            totalTrials = total('trials', yProbeList)
            totalSumOfAllValues = total('sum_of_all_values', yProbeList)
            totalSumOfAllValuesSquare = total('sum_of_all_values_square', yProbeList)
            if totalTrials > 0.0:
                y = totalSumOfAllValues/totalTrials
            else:
                y = 0.0
            points.append((x, y))
            if totalTrials > 1.0 and (totalSumOfAllValuesSquare - totalSumOfAllValues**2.0/totalTrials) > 0.0:
                stdDev = math.sqrt(1.0 / (totalTrials - 1.0) * (totalSumOfAllValuesSquare - totalSumOfAllValues**2.0/totalTrials))
                confInt = math.sqrt(2.0/totalTrials) * stdDev * scipy.special.erfinv(self.confidenceLevel)
            else:
                confInt = 0.0
            graph.confidenceIntervalDict[x] = confInt
        return points


def weightedVariance(graph):
    points = list()
    for x, yProbeList in graph.pointsDict.iteritems():
        totalTrials = total('trials', yProbeList)
        totalSumOfAllValues = total('sum_of_all_values', yProbeList)
        totalSumOfAllValuesSquare = total('sum_of_all_values_square', yProbeList)
        if totalTrials > 1.0:
            y = 1.0 / (totalTrials - 1.0) * (totalSumOfAllValuesSquare - totalSumOfAllValues**2.0/totalTrials)
        else:
            y = 0.0
        points.append((x, y))
    return points


def weightedRelativeVariance(graph):
    points = list()
    for x, yProbeList in graph.pointsDict.iteritems():
        totalTrials = total('trials', yProbeList)
        totalSumOfAllValues = total('sum_of_all_values', yProbeList)
        totalSumOfAllValuesSquare = total('sum_of_all_values_square', yProbeList)
        if totalTrials > 1.0 and totalSumOfAllValues > 0.0:
            y = totalTrials / (totalSumOfAllValues * (totalTrials - 1)) * (totalSumOfAllValuesSquare - totalSumOfAllValues**2.0/totalTrials)
        else:
            y = 0.0
        points.append((x, y))
    return points


def weightedStandardDeviation(graph):
    points = list()
    for x, yProbeList in graph.pointsDict.iteritems():
        totalTrials = total('trials', yProbeList)
        totalSumOfAllValues = total('sum_of_all_values', yProbeList)
        totalSumOfAllValuesSquare = total('sum_of_all_values_square', yProbeList)
        if totalTrials > 1.0 and (totalSumOfAllValuesSquare - totalSumOfAllValues**2.0/totalTrials) > 0.0:
            y = math.sqrt(1.0 / (totalTrials - 1.0) * (totalSumOfAllValuesSquare - totalSumOfAllValues**2.0/totalTrials))
        else:
            y = 0.0
        points.append((x, y))
    return points


def weightedRelativeStandardDeviation(graph):
    points = list()
    for x, yProbeList in graph.pointsDict.iteritems():
        totalTrials = total('trials', yProbeList)
        totalSumOfAllValues = total('sum_of_all_values', yProbeList)
        totalSumOfAllValuesSquare = total('sum_of_all_values_square', yProbeList)
        if totalTrials > 1.0 and totalSumOfAllValues > 0.0 and (totalSumOfAllValuesSquare - totalSumOfAllValues**2.0/totalTrials) > 0.0:
            y = totalTrials / totalSumOfAllValues * math.sqrt(1.0 / (totalTrials - 1.0) * (totalSumOfAllValuesSquare - totalSumOfAllValues**2.0/totalTrials))
        else:
            y = 0.0
        points.append((x, y))
    return points


def weightedSkewness(graph):
    points = list()
    for x, yProbeList in graph.pointsDict.iteritems():
        totalTrials = total('trials', yProbeList)
        totalSumOfAllValues = total('sum_of_all_values', yProbeList)
        totalSumOfAllValuesSquare = total('sum_of_all_values_square', yProbeList)
        totalSumOfAllValuesCubic = total('sum_of_all_values_cubic', yProbeList)
        if totalTrials > 1.0 and totalSumOfAllValues > 0.0 and (totalSumOfAllValuesSquare - totalSumOfAllValues**2.0/totalTrials) > 0.0:
            y = (3.0 * (totalSumOfAllValues/totalTrials)**3.0 - 3.0 * totalSumOfAllValuesSquare/totalTrials * totalSumOfAllValues/totalTrials + totalSumOfAllValuesCubic) /\
            (1.0 / (totalTrials - 1.0) * (totalSumOfAllValuesSquare - totalSumOfAllValues**2.0/totalTrials))**1.5
        else:
            y = 0.0
        points.append((x, y))
    return points



def weightedMoment2(graph):
    points = list()
    for x, yProbeList in graph.pointsDict.iteritems():
        totalTrials = total('trials', yProbeList)
        totalSumOfAllValuesSquare = total('sum_of_all_values_square', yProbeList)
        if totalTrials > 0.0:
            y = totalSumOfAllValuesSquare/totalTrials
        else:
            y = 0.0
        points.append((x, y))
    return points



def weightedMoment3(graph):
    points = list()
    for x, yProbeList in graph.pointsDict.iteritems():
        totalTrials = total('trials', yProbeList)
        totalSumOfAllValuesCubic = total('sum_of_all_values_cubic', yProbeList)
        if totalTrials > 0.0:
            y = totalSumOfAllValuesCubic/totalTrials
        else:
            y = 0.0
        points.append((x, y))
    return points



def minimum(graph):
    points = list()
    for x, yProbeList in graph.pointsDict.iteritems():
        points.append((x, min(yProbeList, key = lambda z: z.minimum)))
    return points



def maximum(graph):
    points = list()
    for x, yProbeList in graph.pointsDict.iteritems():
        points.append((x, max(yProbeList, key = lambda z: z.maximum)))
    return points



def weightedXDF(graph):
    points = list()
    for x, yList in graph.pointsDict.iteritems():
        totalY = reduce(lambda x, y: x + y[0]*y[1].trials, [0] + yList)
        totalTrials = reduce(lambda x, y: x + y[1].trials, [0] + yList)
        points.append((x, totalY/totalTrials))
    return points


class WeightedPercentile:

    def __init__(self, percentile):
        self.percentile = percentile

    def __call__(self, graph):
        pointsList = list()
        for x, probeList in graph.pointsDict.iteritems():
            values = dict()
            totalTrials = 0
            for probe in probeList:
                totalTrials += probe.trials
                for histogramEntry in probe.histogram:
                    if histogramEntry.x in values.keys():
                        values[histogramEntry.x] += histogramEntry.cdf*probe.trials
                    else:
                        values[histogramEntry.x] = histogramEntry.cdf*probe.trials
            valueList = [(xx, yy/totalTrials) for xx, yy in values.iteritems()]
            valueList.sort(key = lambda xx: xx[0])
            for value in valueList:
                if value[1] > self.percentile:
                    pointsList.append((x, value[0]))
                    break
        return pointsList



class AssureEquality:

    def __init__(self, attribute):
        self.attribute = attribute

    def __call__(self, graph):
        points = list()
        for x, yProbeList in graph.pointsDict.iteritems():
            minV = getattr(min(yProbeList, key = lambda x: getattr(x, self.attribute)), self.attribute)
            maxV = getattr(max(yProbeList, key = lambda x: getattr(x, self.attribute)), self.attribute)
            if minV == maxV:
                points.append((x, minV))
            else:
                raise Errors.NotEqual(self.attribute)
        return points



mapping = {'minimum' : minimum,
           'maximum' : maximum,
           'trials' : Sum('trials'),
           'mean': weightedMean,
           'variance': weightedVariance,
           'relative_variance' : weightedRelativeVariance,
           'standard_deviation' : weightedStandardDeviation,
           'relative_standard_deviation' : weightedRelativeStandardDeviation,
           'skewness' : weightedSkewness,
           'moment2' : weightedMoment2,
           'moment3' : weightedMoment3,
           'sum_of_all_values' : Sum('sum_of_all_values'),
           'sum_of_all_values_square' : Sum('sum_of_all_values_square'),
           'sum_of_all_values_cubic' : Sum('sum_of_all_values_cubic'),
           'p01' : WeightedPercentile(0.01),
           'p05' : WeightedPercentile(0.05),
           'p50' : WeightedPercentile(0.50),
           'p95' : WeightedPercentile(0.95),
           'p99' : WeightedPercentile(0.99),
           'min_x' : AssureEquality('min_x'),
           'max_x' : AssureEquality('max_x'),
           'number_of_bins' : AssureEquality('number_of_bins'),
           'underflows' : Sum('underflows'),
           'overflows' : Sum('overflows')}



##### unit tests #####

if __name__ == '__main__':

    import unittest

    class TestWeightedMean(unittest.TestCase):

        class Value:

            def __init__(self, mean, trials):
                self.sum_of_all_values = mean * trials
                self.trials = trials

        class Graph:

            def __init__(self, pointsDict):
                self.pointsDict = pointsDict


        def testOneValue(self):
            a = TestWeightedMean.Value(7.0, 1)
            b = TestWeightedMean.Value(8.0, 1)

            graph = TestWeightedMean.Graph(pointsDict = { 0: [a],
                                                          1: [b]})
            points = weightedMean(graph)
            self.assertEqual(points[0][0], 0)
            self.assertAlmostEqual(points[0][1], 7.0)
            self.assertEqual(points[1][0], 1)
            self.assertAlmostEqual(points[1][1], 8.0)

        def testMultipleValues(self):
            a = TestWeightedMean.Value(7.0, 1)
            b = TestWeightedMean.Value(8.0, 1)

            graph = TestWeightedMean.Graph(pointsDict = { 0: [a, b]})
            points = weightedMean(graph)
            self.assertEqual(points[0][0], 0)
            self.assertAlmostEqual(points[0][1], 7.5)

        def testMultipleValuesTrials(self):
            a = TestWeightedMean.Value(7.0, 1)
            b = TestWeightedMean.Value(8.0, 3)

            graph = TestWeightedMean.Graph(pointsDict = { 0: [a, b]})
            points = weightedMean(graph)
            self.assertEqual(points[0][0], 0)
            self.assertAlmostEqual(points[0][1], 7.75)



    def suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(TestWeightedMean))
        return suite


    unittest.TextTestRunner(verbosity=2).run(suite())
