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

"""This modules contains exceptions raised by the other modules.
"""

class InvalidFilterExpression(Exception):
    """Raised by Interfaces.Facade.filteredByExpression.

    The string 'filterExpression' could not be evaluated.
    """
    def __init__(self, filterExpression):
        self.filterExpression = filterExpression

    def __str__(self):
        return "Invalid filter expression: " + self.filterExpression

class ProbeNotFoundInSimulation(Exception):
    """Raised by Interfaces.Facade.getGraphs and getHistograms.

    The probe named 'probeName' could not be found in
    the simulation with parameters 'simulationParameters.
    """
    def __init__(self, probeName, simulationParameters):
        self.probeName = probeName
        self.simulationParameters = simulationParameters

    def __str__(self):
        return "Probe '" + str(self.probeName) + "' not found in simulation " + str(self.simulationParameters)

class NoScenariosFound(Exception):
    """Raised by Interfaces.Facade.getGraphs and getHistograms.

    The campaign contains no scenarios. This may be either because
    it there were none on disk or because all scenarios were filtered
    away.
    """

    def __str__(self):
        return "Tried to draw a graph from an empty campaign."

class Overflows(Exception):
    def __init__(self, probeName, simulationParameters):
        self.probeName = probeName
        self.simulationParameters = simulationParameters

    def __str__(self):
        return "Probe '" + str(self.probeName) + "' had overflows in simulation " + str(self.simulationParameters)

class Underflows(Exception):
    def __init__(self, probeName, simulationParameters):
        self.probeName = probeName
        self.simulationParameters = simulationParameters

    def __str__(self):
        return "Probe '" + str(self.probeName) + "' had underflows in simulation " + str(self.simulationParameters)

class MultipleErrors(Exception):
    """Collects multiple errors.
    """
    def __init__(self, errors, **attribs):
        self.errors = errors
        for attrib, value in attribs.items():
            setattr(self, attrib, value)

    def __str__(self):
        s = "Errors occurred:\n"
        for error in self.errors:
            s += str(error.__class__) + ": " + str(error) + "\n"
        return s
class Aggregation(Exception):

    def __str__(self):
        return "Could not aggregate graphs! The number of y values to aggregate is different for different x values!"
