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


from FileReaders import ProbeReader, ScenarioReader
import Representations

import os

class CampaignReader:

    def __init__(self,
                 directory,
                 progressNotify = None):

        self.path = os.path.abspath(directory)
        self.progressNotify = progressNotify

    def read(self):
        directories = [self.path]
        for base, subDirs, files in os.walk(self.path):
            if callable(self.progressNotify):
                self.progressNotify(1, 1000, "scanning\n" + base)
            for subDir in subDirs:
                directories += [os.path.join(base, subDir)]
        scenarios = []
        maxIndex = len(directories)
        for index, directory in enumerate(directories):
            Scenario = Representations.Scenario
            scenario = Scenario(ScenarioReader(os.path.abspath(directory)),
                                {"directory": directory},
                                True)
            if len(scenario.probes) > 0:
                scenarios.append(scenario)
            if callable(self.progressNotify):
                self.progressNotify(index + 1, maxIndex, "reading\n" + directory)
        return scenarios, ["directory"]
