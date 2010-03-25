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

"""Read campaign from files/directories.
"""
import os.path
import openwns.wrowser.Probe as Probe
import Representations

# matches filename parts to their respective Probe classes
probeTypes = {}
probeTypes[Probe.MomentsProbe.fileNameSig] = Probe.MomentsProbe
probeTypes[Probe.PDFProbe.fileNameSig] = Probe.PDFProbe
probeTypes[Probe.LogEvalProbe.fileNameSig] = Probe.LogEvalProbe
probeTypes[Probe.TimeSeriesProbe.fileNameSig] = Probe.TimeSeriesProbe
probeTypes[Probe.BatchMeansProbe.fileNameSig] = Probe.BatchMeansProbe
for fileNameSig in Probe.LreProbe.fileNameSigs:
    probeTypes[fileNameSig] = Probe.LreProbe
for fileNameSig in Probe.DlreProbe.fileNameSigs:
    probeTypes[fileNameSig] = Probe.DlreProbe
for fileNameSig in Probe.TableProbe.fileNameSigs:
    probeTypes[fileNameSig] = Probe.TableProbe

class ProbeReader:
    """Reads a probe from a file.

    To be used as 'source' for 'Representations.Probe'.
    """
    def __init__(self, path, probeClass):
        self.path = path
        self.probeClass = probeClass

    def getData(self):
        return self.probeClass(self.path)

    def getName(self):
        return os.path.split(self.path)[1]

class ScenarioReader:
    """Reads a probe list from a directory.

    To be used as 'source' for 'Representations.Scenario'.
    """
    def __init__(self, path):
        self.path = path

    def getProbes(self):
        probes = {}
        try:
            for name in os.listdir(self.path):
                path = os.path.join(self.path, name)
                if os.path.isfile(path):
                    for probeType in probeTypes.keys():
                        if path.endswith(probeType):
                            probe = Representations.Probe(ProbeReader(path, probeTypes[probeType]))
                            probes[probe.name] = probe
        except OSError:
            # There are no probes in this scenario,
            # so silently return the empty dict
            pass
        return probes

