import os
import sys
import imp
import time

import wnsrc
import sqlobject
import sqlobject.sqlbuilder as sqlbuilder
import sqlobject.dbconnection
import _sqlite

import pywns.Scenario as Scenario
import pywns.ProbeDB as ProbeDB


class Parameters(sqlobject.SQLObject):
    campaign = sqlobject.PickleCol()


class __Vars:
    connection = None
    dbPath = None


def __tryAccessDB(func, arg):
    try:
        func(arg)
        return True
    except _sqlite.OperationalError, err:
        print >>sys.stderr, 'NOTICE: ' + str(err)
        if(str(err) == "database is locked"):
            return False
        else:
            raise


def __accessDB(func, arg = None):
    counter = 0
    while(not __tryAccessDB(func, arg)):
        time.sleep(1)
        counter += 1
        if counter >= 1000:
            raise "Could not write to data base, locked for more than 1000s."


def __setPragma(dbConnection):
    curs = dbConnection.getConnection().cursor()
    curs.execute('PRAGMA synchronous = OFF')  # SQLite specific
    curs.close()


def create(path, dbName = 'scenarios.db', debug = False):
    if isConnected():
        disconnect()

    campaignConfigurationPath = os.path.join(os.path.abspath(path), 'campaignConfiguration.py')
    if not os.path.exists(campaignConfigurationPath):
        raise 'File campaignConfiguration.py does not exist in path %s.' % path
    campaignConfiguration = imp.load_module('foo',
                                            file(campaignConfigurationPath),
                                            'foo', ('.py', 'r', imp.PY_SOURCE))

    dbPath = os.path.join(os.path.abspath(path), dbName)
    if os.path.exists(dbPath):
        raise 'Database already exists!'
    __Vars.dbPath = dbPath

    connectionString = 'sqlite:' + dbPath + '?timeout=1000000'
    __Vars.connection = sqlobject.connectionForURI(connectionString)
    sqlobject.sqlhub.processConnection = __Vars.connection

    __accessDB(__setPragma, __Vars.connection)

    for parameter in campaignConfiguration.parameters:
        Scenario.Scenario.sqlmeta.addColumn(parameter)

    Scenario.Scenario.createTable()
    Scenario.Scenario._connection.debug = debug
    Parameters.createTable()

    campaignConfiguration.createCampaign()

    Parameters(campaign = campaignConfiguration.parameters)

    if debug:
        print 'Database %s successfully created.' % dbPath


def connect(path, dbName = 'scenarios.db', debug = False):
    dbPath = os.path.join(os.path.abspath(path), dbName)

    if isConnected():
        if dbPath == __Vars.dbPath:
            return
        else:
            disconnect()

    if not os.path.exists(dbPath):
        raise 'Database not found!'
    __Vars.dbPath = dbPath

    connectionString = 'sqlite:' + dbPath + '?timeout=1000000'
    __Vars.connection = sqlobject.connectionForURI(connectionString)
    sqlobject.sqlhub.processConnection = __Vars.connection

    __accessDB(__setPragma, __Vars.connection)

    Scenario.Scenario._connection.debug = debug

    parameters = Parameters.get(1)
    for parameter in parameters.campaign:
        Scenario.Scenario.sqlmeta.addColumn(parameter)

    if debug:
        print 'Connection to database %s established.' % dbPath


def connectUri(uri):
    __Vars.connection = sqlobject.connectionForURI(uri)
    sqlobject.sqlhub.processConnection = __Vars.connection

    if uri.startswith("sqlite"):
        __accessDB(__setPragma, __Vars.connection)
    else:
        __accessDB(lambda x: None, __Vars.connection)

    Scenario.Scenario._connection.debug = False

    parameters = Parameters.get(1)
    for parameter in parameters.campaign:
        try:
            Scenario.Scenario.sqlmeta.addColumn(parameter)
        except:
            pass


def disconnect(debug = False):
    if not isConnected():
        print >>sys.stderr, 'ERROR: Can\'t disconnect from database because there is no connection.'

    parameters = Parameters.get(1)

    __Vars.connection.close()
    sqlobject.dbconnection.TheURIOpener.cachedURIs.clear()
    __Vars.connection = None
    __Vars.dbPath = None

    for parameter in parameters.campaign:
        Scenario.Scenario.sqlmeta.delColumn(parameter.name)

    if debug:
        print 'Disconnected from database.'


def isConnected():
    if not __Vars.connection == None:
        return True
    return False


def getConnection():
    return __Vars.connection


def resultsAreWrittenIntoDB():
    if __Vars.connection.tableExists(ProbeDB.PDF.sqlmeta.table) \
       or __Vars.connection.tableExists(ProbeDB.LogEval.sqlmeta.table):
        return True
    return False


def addParametersTable(path, dbName = 'scenarios.db', debug = False):
    if isConnected():
        disconnect()

    campaignConfigurationPath = os.path.join(os.path.abspath(path), 'campaignConfiguration.py')
    if not os.path.exists(campaignConfigurationPath):
        raise 'File campaignConfiguration.py does not exist in path %s.' % path
    campaignConfiguration = imp.load_module('foo',
                                            file(campaignConfigurationPath),
                                            'foo', ('.py', 'r', imp.PY_SOURCE))

    dbPath = os.path.join(os.path.abspath(path), dbName)
    if not os.path.exists(dbPath):
        raise 'Database not found!'
    __Vars.dbPath = dbPath

    connectionString = 'sqlite:' + dbPath
    __Vars.connection = sqlobject.connectionForURI(connectionString)

    curs = __Vars.connection.getConnection().cursor()
    curs.execute('PRAGMA synchronous = OFF')  # SQLite specific
    curs.close()

    sqlobject.sqlhub.processConnection = __Vars.connection

    for parameter in campaignConfiguration.parameters:
        Scenario.Scenario.sqlmeta.addColumn(parameter)

    Scenario.Scenario._connection.debug = debug
    Parameters.createTable()
    Parameters(campaign = campaignConfiguration.parameters)

    if debug:
        print 'Parameters table successfully added to %s.' % dbPath
