#! /usr/bin/python

import os
import pwd
import sys
import shutil
import subprocess
import optparse
import re
import profile
import datetime
import time

import wnsrc
from pywns.Database import *
import pywns.Tools


def __connectDatabase(database = "scenarios.db"):
    connect(os.getcwd(), database)


def createDatabase(arg = 'unused'):
    create(os.getcwd())
    print 'Database successfully created.'


def createScenarios(arg = 'unused'):
    __connectDatabase()
    for scenario in Scenario.Scenario.select():
        simId = str(scenario.id)
        simPath = os.path.abspath(os.path.join('..', 'simulations', simId))
        if os.path.exists(simPath):
            shutil.rmtree(simPath)
        os.mkdir(os.path.join('..', 'simulations', simId))
        os.symlink(os.path.join('..', '..', 'sandbox', options.flavor, 'bin', 'openwns'), os.path.join('..', 'simulations', simId, 'openwns'))
        if options.flavor == 'opt':
            os.symlink(os.path.join('..', '..', 'sandbox', 'dbg', 'bin', 'openwns'), os.path.join('..', 'simulations', simId, 'openwns-dbg'))
        os.symlink(os.path.join('..', '..', 'sandbox', 'default', 'lib', 'python2.4', 'site-packages', 'pywns', 'SimConfig.py'), os.path.join('..', 'simulations', simId, 'SimConfig.py'))

        for f in os.listdir(os.path.join('..', 'simulations')):
            if f.endswith('.py') or f.endswith('.probes') or f.endswith('.ini'):
                if not f == 'simcontrol.py' and not f == 'campaignConfiguration.py':
                    os.symlink(os.path.join('..', f), os.path.join('..', 'simulations', simId, f))

    print 'Scenarios successfully created.'


def removeScenarios(arg = 'unused'):
    __connectDatabase()
    for scenario in Scenario.Scenario.select():
        simPath = os.path.abspath(os.path.join('..', 'simulations', str(scenario.id)))
        if os.path.exists(simPath):
            shutil.rmtree(simPath)
    print 'Scenarios successfully removed.'


def __submitJob(scenario):
    if scenario.state == 'Queued':
        print >>sys.stderr, 'ERROR: Job is already in queue'
    elif scenario.state == 'Running':
        print >>sys.stderr, 'ERROR: Job is currently running'
    simId = str(scenario.id)
    simPath = os.path.abspath(os.path.join('..', 'simulations', simId))
    if simPath.startswith('/local'):
        raise Exception('\n\nYour current dir starts with "/local/...". You must chdir to /net/<hostname>/.... Otherwise your simulations will fail.\n')
    print 'Submitting job with scenario id ' + simId
    command = os.path.abspath(os.path.join('..', 'sim.py')) + ' -p ' + os.path.abspath('..') + ' -i ' + simId
    process = subprocess.Popen(['qsub -q %s -N job%s -l h_cpu=%i:00:00 -o %s -e %s -m a -M %s@comnets.rwth-aachen.de -v PYTHONPATH=%s %s' % (options.queue,
                                                                                                                                             simId,
                                                                                                                                             options.cpuTime,
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
    scenario.state = 'Queued'
    scenario.startDate = None
    scenario.stopDate = None
    scenario.hostname = None
    try:
        jobId = int(process.stdout.read().split()[2])
    except:
        print >>sys.stderr, 'ERROR: Could not get job id. Output of qsub has probably changed'
        sys.exit(1)
    scenario.sgeJobId = jobId


def queueAllScenarios(arg):
    __connectDatabase()
    for scenario in Scenario.Scenario.select(sqlobject.AND(Scenario.Scenario.q.state != 'Running',
                                                           Scenario.Scenario.q.state != 'Queued')):
        __submitJob(scenario)


def queueSingleScenario(scenarioId):
    __connectDatabase()
    __submitJob(Scenario.Scenario.get(scenarioId))


def __parametersDict(scenario):
    parameters = {}
    for parameter in Scenario.Scenario.sqlmeta.columns.keys():
        parameters[parameter] = getattr(scenario, parameter)
    parameters['id'] = scenario.id
    return parameters


def queueScenarios(stringexpression):
    __connectDatabase()
    scenarios = list(Scenario.Scenario.select(sqlobject.AND(Scenario.Scenario.q.state != 'Running',
                                                            Scenario.Scenario.q.state != 'Queued')))

    filteredScenarios = pywns.Tools.objectFilter(stringexpression, scenarios, viewGetter = __parametersDict)

    for scenario in filteredScenarios:
        __submitJob(scenario)


def requeueCrashedScenarios(arg = 'unused'):
    __connectDatabase()
    for scenario in Scenario.Scenario.select(Scenario.Scenario.q.state == 'Crashed'):
        __submitJob(scenario)


def __deleteJob(scenario):
    simId = str(scenario.id)
    print 'Deleting job with scenario id ' + simId
    process = subprocess.Popen(['qdel ' + str(scenario.sgeJobId)],
                               stdout = subprocess.PIPE,
                               stderr = subprocess.STDOUT,
                               shell = True)
    status = process.wait()
    if not status == 0:
        print >>sys.stderr, 'ERROR: qdel failed!'
        print >>sys.stderr, process.stdout.read()
        sys.exit(1)

    if scenario.state == 'Running':
        scenario.stopDate = datetime.datetime.today()
    scenario.state = 'Aborted'
    scenario.sgeId = None


def dequeueAllScenarios(arg = 'unused'):
    __connectDatabase()
    for scenario in Scenario.Scenario.select(sqlobject.OR(Scenario.Scenario.q.state == 'Queued',
                                                          Scenario.Scenario.q.state == 'Running')):
        __deleteJob(scenario)


def dequeueScenarios(stringexpression):
    __connectDatabase()
    scenarios = list(Scenario.Scenario.select(sqlobject.OR(Scenario.Scenario.q.state == 'Queued',
                                                           Scenario.Scenario.q.state == 'Running')))

    filteredScenarios = pywns.Tools.objectFilter(stringexpression, scenarios, viewGetter = __parametersDict)

    for scenario in filteredScenarios:
        __deleteJob(scenario)


def __consistencyCheck():
    for scenario in Scenario.Scenario.select(Scenario.Scenario.q.sgeJobId != None):
        tmp = os.tmpfile()
        status = subprocess.call(['qstat -j %i' % scenario.sgeJobId],
                                 shell = True,
                                 stderr = subprocess.STDOUT,
                                 stdout = tmp)
        tmp.seek(0)
        if status != 0 and scenario.state != 'Aborted' and 'Following jobs do not exist' in tmp.read(30):
            scenario.state = 'Crashed'
            scenario.sgeJobId = None
            error = 'Consistency check failed. Simulation has crashed!'
            scenario.stderr = error
            stderrFile = file(os.path.join(os.getcwd(), str(scenario.id), 'stderr'), 'a')
            stderrFile.write(error)
            stderrFile.close()


def consistencyCheck(arg = 'unused'):
    __connectDatabase()
    __consistencyCheck()


def writeResultsIntoDB(dataBase):
    if not os.path.exists(dataBase):
        print 'Database "' + dataBase + '" does not exists. Copying from "scenarios.db".'
        shutil.copy('scenarios.db', dataBase)

    __connectDatabase(dataBase)

    ProbeDB.Moments.dropTable('ifExists')
    ProbeDB.PDF.dropTable('ifExists')
    ProbeDB.PDFHistogramPickle.dropTable('ifExists')
    ProbeDB.LogEval.dropTable('ifExists')
    ProbeDB.LogEvalEntryPickle.dropTable('ifExists')
    ProbeDB.PDFHistogram.dropTable('ifExists')
    ProbeDB.LogEvalEntry.dropTable('ifExists')

    for scenario in Scenario.Scenario.select():
        scenario.resultsMerged = 'notMerged'

    ProbeDB.Moments.createTable()
    ProbeDB.PDF.createTable()
    ProbeDB.PDFHistogramPickle.createTable()
    ProbeDB.LogEval.createTable()
    ProbeDB.LogEvalEntryPickle.createTable()

    if options.allValues:
        ProbeDB.PDFHistogram.createTable()
        ProbeDB.LogEvalEntry.createTable()

    for scenario in Scenario.Scenario.select(Scenario.Scenario.q.state == 'Finished'):
        simId = str(scenario.id)
        simPath = os.path.abspath(os.path.join('..', 'simulations', simId, 'output'))

        print 'Writing results of simulation with scenario id %s to database...' % simId
        transaction = getConnection().transaction()

        ProbeDB.writeAllProbesIntoDB(simPath, scenario, transaction, options.allValues, options.skipLogEval)

        if options.allValues:
            scenario.resultsMerged = 'allValues'
        else:
            scenario.resultsMerged = 'pickleOnly'

        transaction.rollback()
        transaction.cache.clear()

    print 'Results successfully written to database.'


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
    __connectDatabase()
    __consistencyCheck()
    scenarioColumns = Scenario.Scenario.sqlmeta.columns.keys()
    excludeColumns = ['hostname', 'id', 'probes', 'resultsMerged',
                      'sgeJobId', 'startDate', 'state', 'stderr', 'stdout', 'stopDate']
    parameterColumns = [x for x in scenarioColumns if x not in excludeColumns]
    parameterColumns.sort()
    title = ' id    state          start               stop         simTime   prog   sgeId       host      '
    parameterWidth = {}
    for parameter in parameterColumns:
        lengthAllValues = [len(parameter)]
        for scenario in Scenario.Scenario.select():
            lengthAllValues.append(len(str(eval('scenario.' + parameter))))
        parameterWidth[parameter] = max(lengthAllValues) + 2
        title += parameter.center(parameterWidth[parameter])
    print title
    for scenario in Scenario.Scenario.select():
        line = str(scenario.id).rjust(3) + '  '
        line += scenario.state.center(10)
        if not scenario.startDate == None:
            line += scenario.startDate.strftime('%d.%m.%y %H:%M:%S').center(20)
        else:
            line += str().center(20)
        if not scenario.stopDate == None:
            line += scenario.stopDate.strftime('%d.%m.%y %H:%M:%S').center(20)
        else:
            line += str().center(20)
        simTime, progress = __getSimTime(os.path.join(os.getcwd(), str(scenario.id), 'output', 'WNSStatus.dat'))
        if not simTime == None:
            line += simTime.rjust(7)
            line += progress.rjust(8)
        else:
            line += str().center(15)
        if not scenario.sgeJobId == None:
            line += str(scenario.sgeJobId).rjust(7)
        else:
            line += str().rjust(7)
        if not scenario.hostname == None:
            line += scenario.hostname.center(17)
        else:
            line += str().center(17)
        for parameter in parameterColumns:
            value = eval('scenario.' + parameter)
            if not value == None:
                line += str(value).center(parameterWidth[parameter])
            else:
                line += str().center(parameterWidth[parameter])
        print line


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

parser.add_option('', '--remove-scenarios',
                  action = 'callback', callback = queue.append,
                  callback_args = (removeScenarios,),
                  help = 'remove scenario folders')

parser.add_option('-q', '--queue',
                  type = 'str', dest = 'queue', default = 'cqStadt',
                  help = 'chose queue for jobs (default: cqStadt)', metavar = 'QUEUE')

parser.add_option('-t', '--cpu-time',
                  type = 'int', dest = 'cpuTime', default = 100,
                  help = 'chose time for jobs in hours (default: 100h)', metavar = 'HOURS')

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

parser.add_option('', '--write-results',
                  type = 'str', metavar = 'DATABASE',
                  action = 'callback', callback = queue.append,
                  callback_args = (writeResultsIntoDB,),
                  help = 'write Moments, PDF and LogEval probe results of all finished simulations into DATABASE')

parser.add_option('', '--no-logeval-entries',
                  dest = 'skipLogEval', default = False,
                  action = 'store_true',
                  help = 'Skip LogEval Entries, only import LogEval statistics\n' +
                  'option only has effect together with \'--write-results\'')

parser.add_option('', '--all-values',
                  dest = 'allValues', default = False,
                  action = 'store_true',
                  help = 'write all PDF histograms and LogEval entries into DB tables (May take a while!)\n' +
                  'option only has effect together with \'--write-results\'')

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
        print "Sleeping ..."
        time.sleep(options.interval)
else:
        queue.run()

sys.exit(0)
