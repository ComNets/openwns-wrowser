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

class Histogram:
    def __init__(self, histogramAttr, xDataAttr, yDataAttr, yLabel, reversePoints = False):
        self.histogramAttr = histogramAttr
        self.xDataAttr = xDataAttr
        self.yDataAttr = yDataAttr
        self.yLabel = yLabel
        self.reversePoints = reversePoints

    def __call__(self, scenario, probe, graph, errors):
        def graphReverse(graph):
            def reverse(key):
                graph.points.reverse()
            return reverse

        for histogramEntry in getattr(probe.data, self.histogramAttr):
            x = getattr(histogramEntry, self.xDataAttr)
            y = getattr(histogramEntry, self.yDataAttr)
            graph.points.append((x, y))
        graph.axisLabels = (probe.data.description,
                            self.yLabel)
        if self.reversePoints:
            graph.orderPoints = graphReverse(graph)
        else:
            graph.orderPoints = graph.points.sort

class PDF(Histogram):

    def __init__(self):
        Histogram.__init__(self, "pureHistogram", "x", "pdf", "p(x)")

class CDF(Histogram):

    def __init__(self):
        Histogram.__init__(self, "pureHistogram", "x", "cdf", "P(X <= x)")

class CCDF(Histogram):

    def __init__(self):
        Histogram.__init__(self, "pureHistogram", "x", "ccdf", "P(X > x)")

class LRE_F(Histogram):

    def __init__(self):
        Histogram.__init__(self, "histogram", "abscissa", "ordinate", "F(x)", reversePoints = True)

class LRE_d(Histogram):

    def __init__(self):
        Histogram.__init__(self, "histogram", "abscissa", "relativeError", "d(x)", reversePoints = True)

class LRE_rho(Histogram):

    def __init__(self):
        Histogram.__init__(self, "histogram", "abscissa", "meanLocalCorrelationCoefficient", "rho(x)", reversePoints = True)

class LRE_sigma(Histogram):

    def __init__(self):
        Histogram.__init__(self, "histogram", "abscissa", "deviationFromMeanLocalCC", "sigma(x)", reversePoints = True)

class LRE_n(Histogram):

    def __init__(self):
        Histogram.__init__(self, "histogram", "abscissa", "numberOfTrialsPerInterval", "n(x)", reversePoints = True)

class LRE_t(Histogram):

    def __init__(self):
        Histogram.__init__(self, "histogram", "abscissa", "numberOfTransitionsPerInterval", "t(x)", reversePoints = True)

class BatchMeans_CDF(Histogram):

    def __init__(self):
        Histogram.__init__(self, "histogram", "x", "cdf", "P(X >= x)")

class BatchMeans_PDF(Histogram):

    def __init__(self):
        Histogram.__init__(self, "histogram", "x", "pdf", "p(x)")

class BatchMeans_d(Histogram):

    def __init__(self):
        Histogram.__init__(self, "histogram", "x", "relativeError", "d(x)")

class BatchMeans_confidence(Histogram):

    def __init__(self):
        Histogram.__init__(self, "histogram", "x", "relativeError", "confidence")

class BatchMeans_n(Histogram):

    def __init__(self):
        Histogram.__init__(self, "histogram", "x", "numberOfTrialsPerInterval", "d(x)")

class LogEval:
    def __call__(self, scenario, probe, graph, errors):
        for entry in probe.data.entries:
            x = entry.x
            y = entry.y
            graph.points.append((x, y))
        graph.axisLabels = ("t",
                            probe.data.description)

class TimeSeries:
    def __call__(self, scenario, probe, graph, errors):
        for entry in probe.data.entries:
            x = entry.x
            y = entry.y
            graph.points.append((x, y))
        graph.axisLabels = ("t",
                            probe.data.description)

class Table:
    def __call__(self, scenario, probe, graph, errors):
        graph.points = zip(probe.data.tableParser.getXValues(),
                           probe.data.tableParser.getYValues())
        graph.colours = probe.data.tableParser.getArray()
        graph.axisLabels = (probe.data.tableParser.getColumnIdName(),
                            probe.data.tableParser.getRowIdName())
        graph.title = (probe.data.tableParser.getDescription())
