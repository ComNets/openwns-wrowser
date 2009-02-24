#! /usr/bin/env python

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
import threading

usage = 'usage: %prog [options]'
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

parser.add_option('-f','',
                  dest = 'skipProgressFileWriting', default = False, action ='store_true',
                  help = 'skip writing of progress file to /net/sge')

options, args = parser.parse_args()
if len(args):
    print sys.stderr, 'Invalid argument(s): ' + str(args)
    parser.print_help()
    sys.exit(1)

# first we need to get the execution path in order to find the other imports
os.chdir(options.campaignPath)
sys.path.append(os.getcwd())

import simdb.Database as db
import wrowser.Configuration as conf
import ProbeDB

class DatePrepender(object):
    __slots__= [ 'fileObj' ]

    def __init__(self, fileObj):
        self.fileObj = fileObj

    def write(self, content):
        if content == " " or content == "\n":
            self.fileObj.write(content)
            self.fileObj.flush()
        else:
            time = datetime.datetime.now().strftime('%d.%m.%y %H:%M:%S')
            self.fileObj.write(time+" - "+content)
            self.fileObj.flush()

    def flush(self):
        self.fileObj.flush()

    def fileno(self):
        return self.fileObj.fileno()

a = DatePrepender(fileObj = sys.stdout)
b = DatePrepender(fileObj = sys.stderr)
sys.stdout = a
sys.stderr = b

print >>sys.stdout, "------ Start: %s --------" % time.strftime('%H:%M:%S')
print >>sys.stderr, "------ Start: %s --------" % time.strftime('%H:%M:%S')

class PID:
    pass

# only handle the first received signal
usr2called = False
xcpucalled = False

def usr2Handler(signum, frame):
    global usr2called
    assert signum==signal.SIGUSR2
    if not usr2called:
        print >>sys.stdout, 'SIGUSR2 Signal handler called at %s with signal %d' % ( time.strftime('%H:%M:%S'), signum)
        print >>sys.stdout, 'Shutting down openwns ...'
        usr2called = True # ignore subsequent signals
        subprocess.call(['kill', '-'+str(signal.SIGUSR2), str(PID.pid)])
    return

def sigxcpuHandler(signum, frame):
    global xcpucalled
    assert signum==signal.SIGXCPU
    if not xcpucalled:
        print >>sys.stdout, 'SIGXCPU Signal handler called at %s with signal %d' % ( time.strftime('%H:%M:%S'), signum)
        print >>sys.stdout, 'Shutting down openwns ...'
        xcpucalled = True # ignore subsequent signals
        subprocess.call(['kill', '-'+str(signal.SIGXCPU), str(PID.pid)])
    return

signal.signal(signal.SIGUSR2, usr2Handler)
signal.signal(signal.SIGXCPU, sigxcpuHandler)

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
            self.netPath = os.path.join('/', 'sim', platform.node(),
                                        user, campaign, scenario)

            if os.path.islink(remoteOutputPath):
                os.remove(remoteOutputPath)
            else:
                shutil.rmtree(path = remoteOutputPath, ignore_errors = True)

            os.symlink(self.netPath, remoteOutputPath)
            self.writingResultsLocal = True
        else:
            self.outputPath = os.path.join(self.simPath, 'output')

    def copyProgressFile(self):
        localProgressFile = os.path.join(self.outputPath, 'progress')
        remoteProgressFile = os.path.join('/net', 'sge', 'progress', str(os.environ['JOB_ID'])+'.progress')
        while True:
            try:
                shutil.copy(localProgressFile, remoteProgressFile)
            except:
                pass
            # wait 10 minutes
            time.sleep(600)

    def run(self):
        config = conf.Configuration()
        config.read('.campaign.conf')
        db.Database.connectConf(config)
        cursor = db.Database.getCursor()
        cursor.execute('UPDATE scenarios SET state = \'Running\' WHERE campaign_id = %d AND id = %d' % (config.campaignId, self.simId))
        cursor.execute('SELECT current_job_id FROM scenarios WHERE campaign_id = %d AND id = %d' % (config.campaignId, self.simId))
        current_job_id = cursor.fetchone()[0]
        cursor.execute('UPDATE jobs SET hostname = \'%s\', start_date = \'%s\' WHERE sge_job_id = %d' % (platform.node(), datetime.datetime.today().isoformat(), current_job_id))
        cursor.connection.commit()

        # symlink progress file
        #if self.netPath != None and os.environ.has_key('JOB_ID'):
        #    command = 'ln -sf ' + os.path.join(self.netPath, 'progress') + ' ' + os.path.join('/net', 'sge', 'progress', str(os.environ['JOB_ID'])+'.progress &>/dev/null')
        #    process = subprocess.Popen([command], shell = True)
        #    process.wait()

        command = [os.path.join('.', 'openwns') + ' -y \'WNS.masterLogger.enabled=False; WNS.outputDir=\"%s\"\'' % self.outputPath]
        process = subprocess.Popen(args = command,
                                   stdout = subprocess.PIPE,
                                   stderr = subprocess.PIPE,
                                   close_fds = True,
                                   shell = True,
                                   cwd = self.simPath)
        PID.pid = process.pid
        print >>sys.stdout, "openwns PID is: %d" % PID.pid

        if not options.skipProgressFileWriting:
            # this thread copies the progress file to /net/sge/progress
            thread = threading.Thread(target = self.copyProgressFile)
            # This causes the interpreter to shutdown although the thread is still alive
            thread.setDaemon(True)
            thread.start()

        while process.returncode == None:
            try:
                process.wait()
            except OSError, e:
                print >>sys.stdout, "openwns is now shutting down ... (Exception caught: ", e.strerror, ")"

        for line in process.stdout:
            sys.stdout.write(line)
            sys.stdout.flush()
        for line in process.stderr:
            sys.stderr.write(line)
            sys.stderr.flush()

        statusCode = process.returncode
        print >>sys.stdout, "Process exited with Status Code %d" % statusCode

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

        db.Database.connectConf(config)
        cursor = db.Database.getCursor()
        cursor.execute('UPDATE scenarios SET state = \'Writing\' WHERE campaign_id = %d AND id = %d' % (config.campaignId, self.simId))
        cursor.execute('UPDATE jobs SET stop_date = \'%s\', stdout = \' \', stderr = \' \' WHERE campaign_id = %d AND scenario_id = %d' % (datetime.datetime.today().isoformat(), config.campaignId, self.simId))
        cursor.connection.commit()

        try:
            ProbeDB.removeAllProbesFromDB(self.simId)
            ProbeDB.writeAllProbesIntoDB(self.outputPath, self.simId, options.skipNullTrials)
        except Exception, e:
            print >>sys.stdout, "Probe import for simId %d failed (Exception caught: %s)" % ( self.simId, e)
            ProbeDB.removeAllProbesFromDB(self.simId)

        if statusCode == 0:
            state = 'Finished'
        elif statusCode == 2 or statusCode == -24:
            state = 'Aborted'
        else:
            state = 'Crashed'

	print "Setting state to '%s'" % state
        cursor.execute('UPDATE scenarios SET state = \'%s\' WHERE campaign_id = %d AND id = %d' % (state, config.campaignId, self.simId))
        cursor.connection.commit()



    def copyResults(self):
        if self.writingResultsLocal == True:
            os.remove(os.path.join(self.simPath, 'output'))
            shutil.move(self.outputPath, os.path.join(self.simPath, 'output'))
            if len(os.listdir(self.localCampaignSimPath)) == 0:
                os.removedirs(self.localCampaignSimPath)

sim = Sim(options.campaignPath, options.simId)
sim.setCurrentSimPath()
sim.run()
sim.copyResults()

print >>sys.stdout, "------ Stop: %s --------" % time.strftime('%H:%M:%S')
print >>sys.stderr, "------ Stop: %s --------" % time.strftime('%H:%M:%S')
