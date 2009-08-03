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


def total(attribute, list):
    return float(reduce(lambda x, y: x + getattr(y, attribute), [0] + list))


class Sum:

    def __init__(self, entryName):
        self.entryName = entryName

    def __call__(self, pointsDict):
        points = list()
        for x, yProbeList in pointsDict.iteritems():
            y = total(self.entryName, yProbeList)
            points.append((x, y))
        return points



def weightedMean(pointsDict):
    points = list()
    for x, yProbeList in pointsDict.iteritems():
        totalTrials = total('trials', yProbeList)
        totalSumOfAllValues = total('sum_of_all_values', yProbeList)
        y = totalSumOfAllValues/totalTrials
        points.append((x, y))
    return points



def weightedVariance(pointsDict):
    points = list()
    for x, yProbeList in pointsDict.iteritems():
        totalTrials = total('trials', yProbeList)
        totalSumOfAllValues = total('sum_of_all_values', yProbeList)
        totalSumOfAllValuesSquare = total('sum_of_all_values_square', yProbeList)
        if totalTrials > 1.0:
            y = 1.0 / (totalTrials - 1.0) * (totalSumOfAllValuesSquare - totalSumOfAllValues**2.0/totalTrials)
        else:
            y = 0.0
        points.append((x, y))
    return points


def weightedRelativeVariance(pointsDict):
    points = list()
    for x, yProbeList in pointsDict.iteritems():
        totalTrials = total('trials', yProbeList)
        totalSumOfAllValues = total('sum_of_all_values', yProbeList)
        totalSumOfAllValuesSquare = total('sum_of_all_values_square', yProbeList)
        if totalTrials > 1.0 and totalSumOfAllValues > 0.0:
            y = totalTrials / (totalSumOfAllValues * (totalTrials - 1)) * (totalSumOfAllValuesSquare - totalSumOfAllValues**2.0/totalTrials)
        else:
            y = 0.0
        points.append((x, y))
    return points


def weightedStandardDeviation(pointsDict):
    points = list()
    for x, yProbeList in pointsDict.iteritems():
        totalTrials = total('trials', yProbeList)
        totalSumOfAllValues = total('sum_of_all_values', yProbeList)
        totalSumOfAllValuesSquare = total('sum_of_all_values_square', yProbeList)
        if totalTrials > 1.0:
            y = math.sqrt(1.0 / (totalTrials - 1.0) * (totalSumOfAllValuesSquare - totalSumOfAllValues**2.0/totalTrials))
        else:
            y = 0.0
        points.append((x, y))
    return points


def weightedRelativeStandardDeviation(pointsDict):
    points = list()
    for x, yProbeList in pointsDict.iteritems():
        totalTrials = total('trials', yProbeList)
        totalSumOfAllValues = total('sum_of_all_values', yProbeList)
        totalSumOfAllValuesSquare = total('sum_of_all_values_square', yProbeList)
        if totalTrials > 1.0 and totalSumOfAllValues > 0.0:
            y = totalTrials / totalSumOfAllValues * math.sqrt(1.0 / (totalTrials - 1.0) * (totalSumOfAllValuesSquare - totalSumOfAllValues**2.0/totalTrials))
        else:
            y = 0.0
        points.append((x, y))
    return points


def weightedSkewness(pointsDict):
    points = list()
    for x, yProbeList in pointsDict.iteritems():
        totalTrials = total('trials', yProbeList)
        totalSumOfAllValues = total('sum_of_all_values', yProbeList)
        totalSumOfAllValuesSquare = total('sum_of_all_values_square', yProbeList)
        totalSumOfAllValuesCubic = total('sum_of_all_values_cubic', yProbeList)
        if totalTrials > 1.0 and totalSumOfAllValues > 0.0:
            y = (3.0 * (totalSumOfAllValues/totalTrials)**3.0 - 3.0 * totalSumOfAllValuesSquare/totalTrials * totalSumOfAllValues/totalTrials + totalSumOfAllValuesCubic) /\
            (1.0 / (totalTrials - 1.0) * (totalSumOfAllValuesSquare - totalSumOfAllValues**2.0/totalTrials))**1.5
        else:
            y = 0.0
        points.append((x, y))
    return points



def weightedMoment2(pointsDict):
    points = list()
    for x, yProbeList in pointsDict.iteritems():
        totalTrials = total('trials', yProbeList)
        totalSumOfAllValuesSquare = total('sum_of_all_values_square', yProbeList)
        y = totalSumOfAllValuesSquare/totalTrials
        points.append((x, y))
    return points



def weightedMoment3(pointsDict):
    points = list()
    for x, yProbeList in pointsDict.iteritems():
        totalTrials = total('trials', yProbeList)
        totalSumOfAllValuesCubic = total('sum_of_all_values_cubic', yProbeList)
        y = totalSumOfAllValuesCubic/totalTrials
        points.append((x, y))
    return points



def minimum(pointsDict):
    points = list()
    for x, yProbeList in pointsDict.iteritems():
        points.append((x, min(yProbeList, key = lambda z: z.minimum)))
    return points



def maximum(pointsDict):
    points = list()
    for x, yProbeList in pointsDict.iteritems():
        points.append((x, max(yProbeList, key = lambda z: z.maximum)))
    return points



def weightedXDF(pointsDict):
    points = list()
    for x, yList in pointsDict.iteritems():
        totalY = reduce(lambda x, y: x + y[0]*y[1].trials, [0] + yList)
        totalTrials = reduce(lambda x, y: x + y[1].trials, [0] + yList)
        points.append((x, totalY/totalTrials))
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
           'p01' : None,
           'p05' : None,
           'p50' : None,
           'p95' : None,
           'p99' : None,
           'min_x' : None,
           'max_x' : None,
           'number_of_bins' : None,
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


        def testOneValue(self):
            a = TestWeightedMean.Value(7.0, 1)
            b = TestWeightedMean.Value(8.0, 1)

            pointsDict = { 0: [a],
                           1: [b]}
            points = weightedMean(pointsDict)
            self.assertEqual(points[0][0], 0)
            self.assertAlmostEqual(points[0][1], 7.0)
            self.assertEqual(points[1][0], 1)
            self.assertAlmostEqual(points[1][1], 8.0)

        def testMultipleValues(self):
            a = TestWeightedMean.Value(7.0, 1)
            b = TestWeightedMean.Value(8.0, 1)

            pointsDict = { 0: [a, b]}
            points = weightedMean(pointsDict)
            self.assertEqual(points[0][0], 0)
            self.assertAlmostEqual(points[0][1], 7.5)

        def testMultipleValuesTrials(self):
            a = TestWeightedMean.Value(7.0, 1)
            b = TestWeightedMean.Value(8.0, 3)

            pointsDict = { 0: [a, b]}
            points = weightedMean(pointsDict)
            self.assertEqual(points[0][0], 0)
            self.assertAlmostEqual(points[0][1], 7.75)



    def suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(TestWeightedMean))
        return suite


    unittest.TextTestRunner(verbosity=2).run(suite())
