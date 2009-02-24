#! /usr/bin/python
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

import os
import pwd
import sys
import shutil
import subprocess
import optparse
import re
import datetime
import time

import wrowser.Configuration as conf
import wroswer.simdb.Database as db
import wrowser.simdb.Parameters as params
import wrowser.simdb.ProbeDB
import wrowser.Tools


config = conf.Configuration()
config.read('.campaign.conf')
db.Database.connectConf(config)

def createDatabase(arg = 'unused'):
    subprocess.call(['./campaignConfiguration.py'], shell = True)
    print 'Database entries successfully created.'


def createScenarios(arg = 'unused'):
    cursor = db.Database.getCursor()
    cursor.execute('SELECT id FROM scenarios WHERE campaign_id = %d' % config.campaignId)
    scenarioIds = [ entry[0] for entry in cursor.fetchall() ]
    scenarioIds.sort()
    cursor.connection.commit()

    for scenario in scenarioIds:
        simId = str(scenario)
        simPath = os.path.abspath(os.path.join(os.getcwd(), simId))
        if os.path.exists(simPath):
            if options.forceOverwrite:
                shutil.rmtree(simPath)
            else:
                print "Skipping %s, it already exists (consider --force switch)" % simPath
                continue
        os.mkdir(simPath)
        os.symlink(os.path.join('..', '..', 'sandbox', options.flavor, 'bin', 'openwns'), os.path.join(simPath, 'openwns'))
        if options.flavor == 'opt':
            os.symlink(os.path.join('..', '..', 'sandbox', 'dbg', 'bin', 'openwns'), os.path.join(simPath, 'openwns-dbg'))

        os.symlink(os.path.join('..', '.campaign.conf'), os.path.join(simPath, '.campaign.conf'))

        for f in os.listdir(os.getcwd()):
            if f.endswith('.py') or f.endswith('.probes') or f.endswith('.ini'):
                if not f == 'simcontrol.py' and not f == 'campaignConfiguration.py' and not f == 'ProbeDB.py':
                    os.symlink(os.path.join('..', f), os.path.join(simPath, f))

    print 'Scenarios successfully created.'


def removeDatabase(arg = 'unused'):
    db.Database.truncateCampaign(config.campaignId)
    print 'Campaign results successfully removed from database.'


def removeScenarios(arg = 'unused'):
    cursor = db.Database.getCursor()
    cursor.execute('SELECT id FROM scenarios WHERE campaign_id = %d' % config.campaignId)
    scenarioIds = cursor.fetchall()
    cursor.connection.commit()

    for scenario in scenarioIds:
        simPath = os.path.abspath(os.path.join(os.getcwd(), str(scenario[0])))
        if os.path.exists(simPath):
            shutil.rmtree(simPath)
    print 'Scenarios successfully removed.'

def removeScenariosFiltered(stringexpression):
    cursor = db.Database.getCursor()
    cursor.execute('SELECT id FROM scenarios WHERE campaign_id = %d' % config.campaignId)
    scenarioIds = [element[0] for element in cursor.fetchall()]
    cursor.connection.commit()

    filteredScenarios = wrowser.Tools.objectFilter(stringexpression, scenarioIds, viewGetter = __parametersDict)

    for scenarioId in filteredScenarios:
        answer = raw_input("Do you want to remove scenario " + str(scenarioId) + "? (Y/n) ")
        while answer.lower() not in  ["n", "y", '']:
            answer = raw_input(question + " (Y/n) ")
        answer = ((answer.lower() == 'y') or (answer == ''))
        if answer:
            simPath = os.path.abspath(os.path.join(os.getcwd(), str(scenarioId)))
            if os.path.exists(simPath):
                shutil.rmtree(simPath)
            print 'Removed scenario with id ', scenarioId

def __submitJob(scenarioId):
    cursor = db.Database.getCursor()
    cursor.execute('SELECT state FROM scenarios WHERE id = %d AND campaign_id = %d' % (scenarioId, config.campaignId))
    state = cursor.fetchone()[0]

    if state == 'Queued':
        print >>sys.stderr, 'ERROR: Job is already in queue'
    elif state == 'Running':
        print >>sys.stderr, 'ERROR: Job is currently running'
    simId = str(scenarioId)
    simPath = os.path.abspath(os.path.join(os.getcwd(), simId))
    if simPath.startswith('/local'):
        raise Exception('\n\nYour current dir starts with "/local/...". You must chdir to /net/<hostname>/.... Otherwise your simulations will fail.\n')
    print 'Submitting job with scenario id ' + simId
    command = os.path.abspath(os.path.join('..', 'sim.py')) + ' -p ' + os.path.abspath(os.getcwd()) + ' -i ' + simId
    if options.skipNullTrials == True:
        command += ' -n'
    process = subprocess.Popen(['qsub -q %s -N job%s -l s_cpu=%i:%i:00 -l h_cpu=%i:%i:00 -o %s -e %s -m a -M %s@comnets.rwth-aachen.de -v PYTHONPATH=%s %s' % (options.queue,
                                                                                                                                             simId,
                                                                                                                                             options.cpuTime,
                                                                                                                                             options.cpuMinutes,
                                                                                                                                             options.cpuTime,
                                                                                                                                             options.cpuMinutes + 15,
                                                                                                                                             os.path.join(simPath, 'stdout'),
                                                                                                                                             os.path.join(simPath, 'stderr'),
                                                                                                                                             pwd.getpwuid(os.getuid())[0],
                                                                                                                                             os.environ['PYTHONPATH'],
                                                                                                                                             command)],
                         stdout = subprocess.PIPE,
                         stderr = subprocess.STDOUT,
                         shell = True)
    status = process.wait()
    if not status == 0:
        print >>sys.stderr, 'ERROR: qsub failed!'
        print >>sys.stderr, process.stdout.read()
        sys.exit(1)
    state = 'Queued'
    startDate = None
    stopDate = None
    hostname = None
    try:
        jobId = int(process.stdout.read().split()[2])
    except:
        print >>sys.stderr, 'ERROR: Could not get job id. Output of qsub has probably changed'
        sys.exit(1)

    cursor.execute('UPDATE scenarios SET state = \'Queued\', max_sim_time = 0.0, current_sim_time = 0.0, sim_time_last_write = 0.0 WHERE id = %d AND campaign_id = %d' % (scenarioId, config.campaignId))
    cursor.execute('INSERT INTO jobs (campaign_id, scenario_id, sge_job_id, queue_date, start_date, stop_date, hostname, stdout, stderr) VALUES ' \
                   '(%d, %d, %d, \'%s\', \'1900-01-01\' , \'1900-01-01\', \'\', \'\', \'\')' % (config.campaignId, scenarioId, jobId, datetime.datetime.today().isoformat()))
    cursor.connection.commit()


def queueAllScenarios(arg):
    cursor = db.Database.getCursor()
    cursor.execute('SELECT id FROM scenarios WHERE campaign_id = %d AND state != \'Queued\' AND state != \'Running\'' % config.campaignId)
    scenarioIds = cursor.fetchall()
    cursor.connection.commit()

    for scenario in scenarioIds:
        __submitJob(scenario[0])


def queueSingleScenario(scenarioId):
    cursor = db.Database.getCursor()
    cursor.execute('SELECT state FROM scenarios WHERE campaign_id = %d AND id = %d' % (config.campaignId, scenarioId))
    state = cursor.fetchone()[0]
    cursor.connection.commit()
    if state == 'Queued' or state == 'Running':
        print >>sys.stderr, 'Job already queued/running.'
        sys.exit(1)
    __submitJob(scenarioId)


def __parametersDict(scenarioId):
    cursor = db.Database.getCursor()
    cursor.execute('SELECT state FROM scenarios WHERE campaign_id = %d AND id = %d' % (config.campaignId, scenarioId))
    state = cursor.fetchone()[0]
    cursor.connection.commit()

    p = params.Parameters()
    parameters = dict([[paramName, param.getValue()] for paramName, param in p.read(scenarioId).items()])
    parameters['state'] = state
    parameters['id'] = scenarioId
    return parameters


def queueScenarios(stringexpression):
    cursor = db.Database.getCursor()
    cursor.execute('SELECT id FROM scenarios WHERE campaign_id = %d AND state != \'Queued\' AND state != \'Running\'' % config.campaignId)
    scenarioIds = [element[0] for element in cursor.fetchall()]
    cursor.connection.commit()

    filteredScenarios = wrowser.Tools.objectFilter(stringexpression, scenarioIds, viewGetter = __parametersDict)

    for scenarioId in filteredScenarios:
        __submitJob(scenarioId)

def queueScenariosState(stringexpression):
    if stringexpression == 'Queued' or stringexpression == 'Running':
        print >> sys.stderr, 'Cannot queue jobs which are already queue/running.'
        sys.exit(1)

    cursor = db.Database.getCursor()
    cursor.execute('SELECT id FROM scenarios WHERE campaign_id = %d AND state = \'%s\' ' % (config.campaignId, stringexpression))
    scenarioIds = [element[0] for element in cursor.fetchall()]
    cursor.connection.commit()

    if len(scenarioIds) < 1:
        print  >>sys.stderr, 'No scenarios found with state ', stringexpression
        print  >>sys.stderr, 'Valid states are Crashed and NotQueued'
        sys.exit(1)

    for scenarioId in scenarioIds:
        __submitJob(scenarioId)

def requeueCrashedScenarios(arg = 'unused'):
    cursor = db.Database.getCursor()
    cursor.execute('SELECT id FROM scenarios WHERE campaign_id = %d AND state = \'Crashed\'' % config.campaignId)
    scenarioIds = cursor.fetchall()
    cursor.connection.commit()
    for scenario, in scenarioIds:
        # remove results from previous simulation runs
        wrowser.simdb.ProbeDB.removeAllProbesFromDB(scenarioId = scenario)
        __submitJob(scenario)


def __deleteJob(scenarioId):
    cursor = db.Database.getCursor()
    cursor.execute('SELECT state, current_job_id FROM scenarios WHERE campaign_id = %d AND id = %d' % (config.campaignId, scenarioId))
    (state, sgeJobId) = cursor.fetchone()
    simId = str(scenarioId)

    if state.strip() != 'Running' and state.strip() != 'Queued':
        print >>sys.stderr, 'Job is not queued/running.'

    print 'Deleting job with scenario id ' + simId
    process = subprocess.Popen(['qdel ' + str(sgeJobId)],
                               stdout = subprocess.PIPE,
                               stderr = subprocess.STDOUT,
                               shell = True)
    status = process.wait()
    if not status == 0:
        print >>sys.stderr, 'ERROR: qdel failed!'
        print >>sys.stderr, process.stdout.read()
        sys.exit(1)

    if state == 'Running':
        stopDate = datetime.datetime.today()
        state = 'Aborted'
    elif state == 'Queued':
        state = 'NotQueued'
    cursor.execute('UPDATE scenarios SET state = \'%s\', current_job_id = 0 WHERE campaign_id = %d AND id = %d' % (state, config.campaignId, scenarioId))
    cursor.execute('UPDATE jobs SET stop_date = \'%s\' WHERE sge_job_id = %d' % (datetime.datetime.today().isoformat(), sgeJobId))
    cursor.connection.commit()


def dequeueAllScenarios(arg = 'unused'):
    cursor = db.Database.getCursor()
    cursor.execute('SELECT id FROM scenarios WHERE campaign_id = %d AND (state = \'Queued\' OR state = \'Running\')' % config.campaignId)
    scenarioIds = [element[0] for element in cursor.fetchall()]
    cursor.connection.commit()

    for scenario in scenarioIds:
        __deleteJob(scenario)


def dequeueScenarios(stringexpression):
    cursor = db.Database.getCursor()
    cursor.execute('SELECT id FROM scenarios WHERE campaign_id = %d AND (state = \'Queued\' OR state = \'Running\')' % config.campaignId)
    scenarioIds = [element[0] for element in cursor.fetchall()]
    cursor.connection.commit()

    filteredScenarios = wrowser.Tools.objectFilter(stringexpression, scenarioIds, viewGetter = __parametersDict)

    for scenario in filteredScenarios:
        __deleteJob(scenario)


def consistencyCheck(arg = 'unused'):
    cursor = db.Database.getCursor()
    cursor.execute('SELECT id, current_job_id, state FROM scenarios WHERE campaign_id = %d AND current_job_id != 0' % config.campaignId)
    sqlResults = cursor.fetchall()

    for scenario, sgeJobId, state in sqlResults:
        tmp = os.tmpfile()
        status = subprocess.call(['qstat -j %i' % sgeJobId],
                                 shell = True,
                                 stderr = subprocess.STDOUT,
                                 stdout = tmp)
        tmp.seek(0)
        if status != 0 and state in ['Running', 'Queued'] and 'Following jobs do not exist' in tmp.read(30):
            cursor.execute('UPDATE scenarios SET state=\'Crashed\' WHERE campaign_id=%d AND id=%d' % (config.campaignId, scenario))
            cursor.execute('UPDATE jobs SET stderr =\'Consistency check failed. Simulation has crashed!\' WHERE sge_job_id = %d' % sgeJobId)
            stderrFile = file(os.path.join(os.getcwd(), str(scenario), 'stderr'), 'a')
            stderrFile.write('Consistency check failed. Simulation has crashed!')
            stderrFile.close()
    cursor.connection.commit()


def __getSimTime(fileName):
    currentSimTimeExpression = re.compile('.*Simulation time: ([0-9.]*).*')
    maxSimTimeExpression = re.compile('.*Max. simulation time: ([0-9.]*).*')
    try:
        f = file(fileName)
    except:
        return None, None

    cst = 0
    progress = 0
    for line in f:
        currentSimTime = currentSimTimeExpression.match(line)
        maxSimTime = maxSimTimeExpression.match(line)
        if currentSimTime is not None:
            cstMatch, = currentSimTime.groups(1)
            cst = float(cstMatch)
        if maxSimTime is not None:
            mstMatch, = maxSimTime.groups(1)
            mst = float(mstMatch)
            if not mst == 0:
                progress = cst / mst * 100
            cstStr = '%.2fs' % cst
            progressStr = '%.2f%%' % progress
            return cstStr, progressStr


def jobInfo(arg = 'unused'):
    consistencyCheck()
    parameters = params.Parameters()
    parameterNames = parameters.parameterSet.keys()
    parameterNames.sort()
    campaignParameters = parameters.readAllScenarios()
    title = ' id    state          start                 stop              duration    simTime   prog   sgeId       host      '
    parameterWidth = {}
    for parameterName in parameterNames:
        lengthAllValues = [len(parameterName)]
        for scenarioId, parameters in campaignParameters.items():
            lengthAllValues.append(len(str(parameters[parameterName].getValue())))
        parameterWidth[parameterName] = max(lengthAllValues) + 2
        title += parameterName.center(parameterWidth[parameterName])
    print title
    cursor = db.Database.getCursor()
    for scenarioId in sorted(campaignParameters):
        cursor.execute('SELECT state, current_job_id FROM scenarios WHERE scenarios.campaign_id = %d AND scenarios.id = %d' % (config.campaignId, scenarioId))
        (state, sgeJobId) = cursor.fetchone()
        startDate = stopDate = datetime.datetime(1900, 1, 1)
        hostname = None
        if sgeJobId != 0:
            cursor.execute('SELECT start_date, stop_date, hostname FROM jobs WHERE sge_job_id = %d' % sgeJobId)
            (startDate, stopDate, hostname) = cursor.fetchone()
        line = str(scenarioId).rjust(3) + '  '
        line += state.center(10)
        if not startDate.year == 1900:
                line += startDate.strftime('%d.%m.%y %H:%M:%S').center(20)
        else:
            line += str().center(20)
        if not stopDate.year == 1900:
                line += stopDate.strftime('%d.%m.%y %H:%M:%S').center(20)
        else:
            line += str().center(20)
        if not startDate.year == 1900:
            if not stopDate.year == 1900:
                duration = stopDate - startDate
            else:
                duration = datetime.datetime.now() - startDate
            line += str(duration).split('.')[0].rjust(17)
        else:
            line += str().rjust(17)

        simTime, progress = __getSimTime(os.path.join(os.getcwd(), str(scenarioId), 'output', 'WNSStatus.dat'))
        if not simTime == None:
            line += simTime.rjust(8)
            line += progress.rjust(9)
        else:
            line += str().center(17)
        if not sgeJobId == 0:
            line += str(sgeJobId).rjust(7)
        else:
            line += str().rjust(7)
        if not hostname == None:
            line += hostname.center(17)
        else:
            line += str().center(17)
        for parameter in parameterNames:
            value = str(campaignParameters[scenarioId][parameter].getValue())
            if not value == None:
                line += str(value).center(parameterWidth[parameter])
            else:
                line += str().center(parameterWidth[parameter])
        print line
    cursor.connection.commit()


def executeLocally(expression):
    cursor = db.Database.getCursor()
    cursor.execute('SELECT id FROM scenarios WHERE campaign_id = %d AND (state != \'Queued\' OR state != \'Running\')' % config.campaignId)
    scenarioIds = [element[0] for element in cursor.fetchall()]
    cursor.connection.commit()

    filteredScenarios = [instance for instance in scenarioIds if eval(expression, {}, __parametersDict(instance))]

    for scenario in filteredScenarios:
        __execute(scenario)

def executeLocallyState(stringexpression):
    cursor = db.Database.getCursor()
    cursor.execute('SELECT id FROM scenarios WHERE campaign_id = %d AND state = \'%s\' ' % (config.campaignId, stringexpression))
    scenarioIds = [element[0] for element in cursor.fetchall()]
    cursor.connection.commit()

    if len(scenarioIds) < 1:
        print  >>sys.stderr, 'No scenarios found with state ', stringexpression
        print  >>sys.stderr, 'Valid states are Crashed and NotQueued'
        sys.exit(1)

    for scenarioId in scenarioIds:
        __execute(scenarioId)

def __execute(scenario):
    print 'Executing scenario with id: %i' % scenario
    stdout = open(os.path.join(os.getcwd(), str(scenario), 'stdout'), 'w')
    stderr = open(os.path.join(os.getcwd(), str(scenario), 'stderr'), 'w')

    process = subprocess.Popen(['nice -n 19 ../sim.py -p %s -i %i -f' % (os.getcwd(), scenario)],
                               stdout = stdout,
                               stderr = stderr,
                               shell = True)
    process.wait()

    stdout.close()
    stderr.close()

class CommandQueue:
    def __init__(self):
        self.queue = []

    def append(self, option, opt, arg, parser, command):
        self.queue.append((command, arg))

    def run(self):
        for command, arg in self.queue:
            command(arg)

queue = CommandQueue()


usage = 'usage: %prog [options]'
parser = optparse.OptionParser(usage)

parser.add_option('', '--create-database',
                  action = 'callback', callback = queue.append,
                  callback_args = (createDatabase,),
                  help = 'create scenario database')

parser.add_option('', '--create-scenarios',
                  action = 'callback', callback = queue.append,
                  callback_args = (createScenarios,),
                  help = 'create scenario folders')

parser.add_option('', '--flavor',
                  type = 'str', dest = 'flavor', default = 'opt',
                  help = 'chose flavor for simulation (default: opt)\n' +
                  'option may only be used together with \'--create-scenarios\'', metavar = 'FLAVOR')

parser.add_option('', '--remove-database',
                  action = 'callback', callback = queue.append,
                  callback_args = (removeDatabase,),
                  help = 'remove results from database')

parser.add_option('', '--remove-scenarios',
                  action = 'callback', callback = queue.append,
                  callback_args = (removeScenarios,),
                  help = 'remove scenario folders')

parser.add_option('', '--remove-scenariosFiltered',
                  type = 'str', metavar = 'EXPRESSION',
                  action = 'callback', callback = queue.append,
                  callback_args = (removeScenariosFiltered,),
                  help = 'remove scenarios matching EXPRESSION')

parser.add_option('-q', '--queue',
                  type = 'str', dest = 'queue', default = 'cqStadt',
                  help = 'chose queue for jobs (default: cqStadt)', metavar = 'QUEUE')

parser.add_option('-t', '--cpu-time',
                  type = 'int', dest = 'cpuTime', default = 100,
                  help = 'chose time for jobs in hours (default: 100h)', metavar = 'HOURS')

parser.add_option('', '--minutes',
                  type = 'int', dest = 'cpuMinutes', default = 0,
                  help = 'chose time for jobs in minutes (default: 0m), can be combined with --cpu-time', metavar = 'MINUTES')

parser.add_option('-f', '--force',
                  dest = 'forceOverwrite', default = False, action ='store_true',
                  help = 'force overwriting existing scenario subdirs')

parser.add_option('-n', '--skipNullTrials',
                  dest = 'skipNullTrials', default = False, action ='store_true',
                  help = 'skip importing probes with zero trials into database')

parser.add_option('', '--execute-locally',
                  type = 'str', metavar = 'EXPRESSION',
                  action = 'callback', callback = queue.append,
                  callback_args = (executeLocally,),
                  help = 'executes scenarios matching EXPRESSION on the local machine')

parser.add_option('', '--execute-locally-with-state',
                  type = 'str', metavar = 'EXPRESSION',
                  action = 'callback', callback = queue.append,
                  callback_args = (executeLocallyState,),
                  help = 'executes scenarios where the state (NotQueued, Finished, Running, Crashed) matches EXPRESSION')

parser.add_option('', '--queue-all-scenarios',
                  action = 'callback', callback = queue.append,
                  callback_args = (queueAllScenarios,),
                  help = 'queue all scenarios')

parser.add_option('', '--queue-single-scenario',
                  type = "int", metavar = "SCENARIOID",
                  action = 'callback', callback = queue.append,
                  callback_args = (queueSingleScenario,),
                  help = 'queue scenario with id SCENARIOID')

parser.add_option('', '--queue-scenarios',
                  type = 'str', metavar = 'EXPRESSION',
                  action = 'callback', callback = queue.append,
                  callback_args = (queueScenarios,),
                  help = 'queue scenarios matching EXPRESSION')

parser.add_option('', '--queue-scenarios-with-state',
                  type = 'str', metavar = 'EXPRESSION',
                  action = 'callback', callback = queue.append,
                  callback_args = (queueScenariosState,),
                  help = 'queue scenarios where the state (NotQueued, Finished, Running, Crashed) matches EXPRESSION')

parser.add_option('', '--requeue-crashed-scenarios',
                  action = 'callback', callback = queue.append,
                  callback_args = (requeueCrashedScenarios,),
                  help = 'requeue all crashed scenarios')

parser.add_option('', '--dequeue-all-scenarios',
                  action = 'callback', callback = queue.append,
                  callback_args = (dequeueAllScenarios,),
                  help = 'dequeue all scenarios of this campaign')

parser.add_option('', '--dequeue-scenarios',
                  type = 'str', metavar = 'EXPRESSION',
                  action = 'callback', callback = queue.append,
                  callback_args = (dequeueScenarios,),
                  help = 'dequeue scenarios matching EXPRESSION')

parser.add_option('', '--consistency-check',
                  action = 'callback', callback = queue.append,
                  callback_args = (consistencyCheck,),
                  help = 'solve inconsistencies between the sge job database and the scenario database')

parser.add_option('-i', '--info',
                  action = 'callback', callback = queue.append,
                  callback_args = (jobInfo,),
                  help = 'show information about all jobs')

parser.add_option('', '--interval',
                  dest = 'interval',
                  type = 'int', metavar = 'INTERVAL',
                  action = 'store',
                  default = 0,
                  help = 'run command in endless loop with interval length in between')

options, args = parser.parse_args()
if len(args):
    parser.print_help()
    sys.exit(1)

if not len(queue.queue):
    parser.print_help()
    sys.exit(0)

if options.interval != 0:
    while True:
        print "Running command ..."
        queue.run()
        until = time.localtime(time.time()+options.interval)
        print "Sleeping until %d:%d %d-%d-%d..." % (until[3], until[4], until[0], until[1], until[2])
        time.sleep(options.interval)
else:
        queue.run()

sys.exit(0)
