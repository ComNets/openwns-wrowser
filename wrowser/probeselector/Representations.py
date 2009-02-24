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

"""This module contains classes to represent a simulation campaign
and its results.

A simulation campaign is represented by a tree like structure,
where a 'Campaign' instance is the root. A campaign consists
of simulation runs represented by a 'Scenario' instance and the
simulation parameter names and values that were varied across the
simulations.

A 'Scenario' is a single simulation run and contains the
concrete values of the simulation parameters and the results
of the simulation represented by 'Probe' instances.

A 'Probe' is a result of a simulation run. The actual data
is represented by instances of the classes in either 'pywns.Probe'
or 'pywns.ProbeDB'.

Both 'Scenario' and 'Probe' follow a read-on-demand policy: Their
'__init__' function gets a data source that handles the data access.
This way the data only needs to be read on first access and not on
object construction time. Especially not all probes - which may be
many - are read when the campaign data structure is constructed.

Probe, Scenario and Campaign publish their data as properties and
provide the least possible functionality beyond that, i.e. only
what is necessary to initialize and represent the data and for
the functionality of the father classes.

The class 'Graph' represents a graph drawn from a campaign.
"""
import os.path

class Probe(object):
    """Represents a probe.

    A 'Probe' in this context consists of a source and the
    data in it, that is read on first access.

    Properties:
    source: (rw) The data source
    name:   (ro) The probe's name
    data:   (ro) The probe's data, instance of pywns.Probe.Probe or
                   pywns.ProbeDB.Probe
    """
    def __init__(self, source):
        """Construct Probe object.

        The source instance must provide a function
        getData() that returns the data of the probe
        and getName() that returns the name of the probe.
        """
        self.__data = None
        self.__source = source

    def __getSource(self):
        return self.__source

    def __setSource(self, source):
        self.__source = source

    def __getName(self):
        return self.source.getName()

    def __getData(self):
        if self.__data == None:
            self.__data = self.source.getData()
        return self.__data

    source = property(__getSource, __setSource)
    name = property(__getName)
    data = property(__getData)


class Scenario(object):
    """Represents a simulation run.

    A 'Scenario' is a simulation run using a given
    set of simulation parameters

    Properties:
    source:          (rw) The data source
    parameters:      (ro) A dict with the simulation parameters
    probes:          (ro) A dict with the probe names as keys and
                          'Probe' instances as values
    """
    def __init__(self, source, parameters, prefetchProbeNames = False):
        self.__source = source
        self.__parameters = parameters
        if prefetchProbeNames:
            self.__probes = self.source.getProbes()
        else:
            self.__probes = None
        for attr in parameters.items():
            setattr(self, attr[0], attr[1])

    def __getSource(self):
        return self.__source

    def __setSource(self, source):
        self.__source = source

    def __getParameters(self):
        return self.__parameters

    def __getProbes(self):
        if self.__probes == None:
            self.__probes = self.source.getProbes()
        return self.__probes

    source = property(__getSource, __setSource)
    parameters = property(__getParameters)
    probes = property(__getProbes)


class Campaign:
    """Represents a simulation run and its results.

    A campaign is a list of simulation parameter
    names and a list of scenarios that were run
    with different values for these parameters.

    Properties:
    parameterNames: (ro) A list of the simulation parameter names
    scenarios:      (ro) A list of the scenarios
    """
    def __init__(self, scenarioList, parameterNames):
        self.__scenarios = scenarioList
        self.__parameterNames = parameterNames

    def __getParameterNames(self):
        return self.__parameterNames

    def __getScenarios(self):
        return self.__scenarios

    parameterNames = property(__getParameterNames)
    scenarios = property(__getScenarios)

