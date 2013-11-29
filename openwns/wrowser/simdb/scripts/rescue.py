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

#! /usr/bin/env python

"""
This script is required to be executed remotely (i.e. per ssh) on the
machine where the simulation to be rescued has been run.

e.g.
ssh <hostname> "/path/to/rescue.py -i 42 -p /path/to/campaign/simulations -n"

For a given simulation id, it tries to import all probes into the db
(thereby deleting all potentially existing data for that simulation id)
And sets the status of the simulation run to 'Finished'.
"""

import sys
import os
import subprocess
import pwd
import shutil
import errno
import platform
import datetime
import optparse
import getpass
import signal
import time

usage = 'This Script MUST be executed on the same host where the simulation has been run!!!\n\nusage: %prog [options]'
parser = optparse.OptionParser(usage)

parser.add_option('-p','',
                  type = 'str', dest = 'campaignPath',
                  help = 'campaign path', metavar = 'PATH')

parser.add_option('-i','',
                  type = 'int', dest = 'simId',
                  help = 'id of simulation', metavar = 'ID')

parser.add_option('-n','',
                  dest = 'skipNullTrials', default = False, action ='store_true',
                  help = 'skip importing probes with zero trials into database')

options, args = parser.parse_args()
if len(args):
    print sys.stderr, 'Invalid argument(s): ' + str(args)
    parser.print_help()
    sys.exit(1)

# first we need to get the execution path in order to find the other imports
os.chdir(options.campaignPath)
sys.path.append(os.getcwd())

import openwns.wrowser.simdb.Database as db
import openwns.wrowser.Configuration as conf
import openwns.wrowser.simdb.ProbeDB

class DatePrepender:
    fileObj = None

    def __init__(self, fileObj):
        self.fileObj = fileObj

    def write(self, content):
        if content == " " or content == "\n":
            self.fileObj.write(content)
        else:
            time = datetime.datetime.now().strftime('%d.%m.%y %H:%M:%S')
            self.fileObj.write(time+" - "+content)

    def fileno(self):
        return self.fileObj.fileno()

a = DatePrepender(fileObj = sys.stdout)
b = DatePrepender(fileObj = sys.stderr)
sys.stdout = a
sys.stderr = b

print >>sys.stdout, "------ Start: %s --------" % time.strftime('%H:%M:%S')
print >>sys.stderr, "------ Start: %s --------" % time.strftime('%H:%M:%S')


class Sim:

    def __init__(self, campaignPath, simId):
        self.simPath = os.path.abspath(os.path.join(str(simId)))
        self.simId = simId
        self.scenario = None
        self.outputPath = None
        self.netPath = None
        self.writingResultsLocal = False


    def setCurrentSimPath(self):
        localScratchPath = os.path.join('/', 'scratch')

        if os.path.exists(localScratchPath):
            user = getpass.getuser()
            localUserSimPath = os.path.join(localScratchPath, user)
            campaign = self.simPath.split('/')[-3]
            self.localCampaignSimPath = os.path.join(localUserSimPath, campaign)
            scenario = str(self.simId)
            self.outputPath = os.path.join(self.localCampaignSimPath, scenario)

            self.netPath = os.path.join('/', 'sim', platform.node(),
                                        user, campaign, scenario)

            self.writingResultsLocal = True
        else:
            self.outputPath = os.path.join(self.simPath, 'output')


    def rescue(self):
        config = conf.Configuration()
        config.read('.campaign.conf')

        db.Database.connectConf(config)
        cursor = db.Database.getCursor()
        cursor.execute('UPDATE scenarios SET state = \'Writing\' WHERE campaign_id = %d AND id = %d' % (config.campaignId, self.simId))
        cursor.execute('UPDATE jobs SET stop_date = \'%s\', stdout = \' \', stderr = \' \' WHERE campaign_id = %d AND scenario_id = %d' % (datetime.datetime.today().isoformat(), config.campaignId, self.simId))
        cursor.connection.commit()

        try:
            openwns.wrowser.simdb.ProbeDB.removeAllProbesFromDB(self.simId)
            openwns.wrowser.simdb.ProbeDB.writeAllProbesIntoDB(self.outputPath, self.simId, options.skipNullTrials)
            statusCode = 0
        except Exception, e:
            print >>sys.stdout, "Probe import for simId %d failed (Exception caught: %s)" % ( self.simId, e)
            openwns.wrowser.simdb.ProbeDB.removeAllProbesFromDB(self.simId)

        if statusCode == 0:
            state = 'Finished'
        else:
            state = 'Crashed'

	print "Setting state to '%s'" % state
        cursor.execute('UPDATE scenarios SET state = \'%s\' WHERE campaign_id = %d AND id = %d' % (state, config.campaignId, self.simId))
        cursor.connection.commit()



    def copyResults(self):
        if self.writingResultsLocal == True:
            if os.path.islink(os.path.join(self.simPath, 'output')):
                os.remove(os.path.join(self.simPath, 'output'))
                shutil.move(self.outputPath, os.path.join(self.simPath, 'output'))
                if len(os.listdir(self.localCampaignSimPath)) == 0:
                    os.removedirs(self.localCampaignSimPath)
            else:
                print "output dir is already local"

sim = Sim(options.campaignPath, options.simId)
sim.setCurrentSimPath()
sim.rescue()
sim.copyResults()

print >>sys.stdout, "------ Stop: %s --------" % time.strftime('%H:%M:%S')
print >>sys.stderr, "------ Stop: %s --------" % time.strftime('%H:%M:%S')
