#! /usr/bin/env python2.4

import sys
import os
import subprocess
import pwd
import shutil
import errno
import platform
import datetime
import optparse

usage = 'usage: %prog [options]'
parser = optparse.OptionParser(usage)

parser.add_option('-p','',
                  type = 'str', dest = 'campaignPath',
                  help = 'campaign path', metavar = 'PATH')

parser.add_option('-i','',
                  type = 'str', dest = 'simId',
                  help = 'id of simulation', metavar = 'ID')

options, args = parser.parse_args()
if len(args):
    print sys.stderr, 'Invalid argument(s): ' + str(args)
    parser.print_help()
    sys.exit(1)

# first we need to get the execution path in order to find the other imports
os.chdir(options.campaignPath)
import wnsrc
from pywns.Database import *


class Sim:

    def __init__(self, campaignPath, simId):
        self.simPath = os.path.abspath(os.path.join(campaignPath, 'simulations', simId))
        self.simId = int(os.path.basename(self.simPath))
        self.scenario = None
        self.outputPath = None
        self.netPath = None
        self.writingResultsLocal = False

        dbPath = os.path.abspath(os.path.join(campaignPath, 'simulations'))
        connect(dbPath)


    def getScenario(self):
        self.scenario = Scenario.Scenario.get(self.simId)


    def setCurrentSimPath(self):
        localScratchPath = os.path.join('/', 'local', 'scratch')

        if os.path.exists(localScratchPath):
            user = pwd.getpwuid(os.getuid())[0]
            localUserSimPath = os.path.join(localScratchPath, user)
            campaign = self.simPath.split('/')[-3]
            self.localCampaignSimPath = os.path.join(localUserSimPath, campaign)
            scenario = str(self.simId)
            self.outputPath = os.path.join(self.localCampaignSimPath, scenario)
            shutil.rmtree(self.outputPath, ignore_errors = True)
            try:
                os.mkdir(localUserSimPath, 0755)
            except OSError, (err, errstring):
                if err != errno.EEXIST:
                    raise
            try:
                os.mkdir(self.localCampaignSimPath, 0755)
            except OSError, (err, errstring):
                if err != errno.EEXIST:
                    raise
            os.mkdir(self.outputPath, 0755)
            remoteOutputPath = os.path.join(self.simPath, 'output')
            self.netPath = os.path.join('/', 'net', platform.node(), 'scratch',
                                        user, campaign, scenario)

            if os.path.islink(remoteOutputPath):
                os.remove(remoteOutputPath)
            else:
                shutil.rmtree(path = remoteOutputPath, ignore_errors = True)

            os.symlink(self.netPath, remoteOutputPath)
            self.writingResultsLocal = True
        else:
            self.outputPath = os.path.join(self.simPath, 'output')


    def run(self):
        self.scenario.set(state = 'Running',
                          hostname = platform.node(),
                          startDate = datetime.datetime.today())

        # symlink progress file
        if self.netPath != None and os.environ.has_key('JOB_ID'):
            command = 'ln -sf ' + os.path.join(self.netPath, 'progress') + ' ' + os.path.join('/net', 'sge', 'progress', str(os.environ['JOB_ID'])+'.progress &>/dev/null')
            process = subprocess.Popen([command], shell = True)
            process.wait()

        command = [os.path.join('.', 'openwns') + ' -y \'WNS.masterLogger.enabled=False; WNS.outputDir=\"%s\"\'' % self.outputPath]
        process = subprocess.Popen(command,
                                   close_fds = True,
                                   shell = True,
                                   cwd = self.simPath)
        statusCode = process.wait()
        try:
            stdoutFile = open(os.path.join(self.simPath, 'stdout'), 'r')
            self.stdout = stdoutFile.read(10000)
            stdoutFile.close()
        except IOError, err:
            if err.errno == 2:
                self.stdout = ''
        try:
            stderrFile = open(os.path.join(self.simPath, 'stderr'), 'r')
            self.stderr = stderrFile.read(10000)
            stderrFile.close()
        except IOError, err:
            if err.errno == 2:
                self.stderr = ''

        if statusCode == 0:
            newState = 'Finished'
        else:
            newState = 'Crashed'

        self.scenario.set(stdout = self.stdout,
                          stderr = self.stderr,
                          stopDate = datetime.datetime.today(),
                          sgeJobId = None,
                          state = newState)


    def copyResults(self):
        if self.writingResultsLocal == True:
            os.remove(os.path.join(self.simPath, 'output'))
            shutil.move(self.outputPath, os.path.join(self.simPath, 'output'))
            if len(os.listdir(self.localCampaignSimPath)) == 0:
                os.removedirs(self.localCampaignSimPath)

sim = Sim(options.campaignPath, options.simId)
sim.getScenario()
sim.setCurrentSimPath()
sim.run()
sim.copyResults()
