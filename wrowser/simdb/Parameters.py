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

import copy

import os
import sys

import ConfigParser
configParser = ConfigParser.SafeConfigParser()
configParser.read(os.path.join(os.environ['HOME'], '.wns', 'dbAccess.conf'))
if 'Wrowser' not in configParser.sections():
    print "ERROR! Path to wrowser not in dbAccess.conf"
    exit(0)
sys.path.append(configParser.get('Wrowser', 'path'))

import wrowser.simdb.Database as db
import wrowser.Configuration as config


class Type(object):

    def __init__(self, variableType, sqlParameterType, default = None, parameterRange = None):
        if default is not None:
            self.__default = variableType(default)
        else:
            self.__default = None

        if parameterRange is not None:
            self.__parameterRange = parameterRange
        else:
            self.__parameterRange = None

        self.__variableType = variableType
        self.__sqlParameterType = sqlParameterType

        self.__value = None


    def copy(self):
        print Hallo


    def getType(self):
        return self.__sqlParameterType


    def setValue(self, value):
        if value is None:
            self.__value = None
        else:
#            print 'setValue ', value
            self.__value = self.__variableType(value)


    def setValueProperty(self, clsInstance, value):
        self.setValue(value)


    def getDefault(self):
        return self.__default


    def getValue(self):
#        print 'getValue ', self.__value
        return self.__value


    def getValueProperty(self, clsInstance):
        return self.getValue()

    def getRange(self):
        return self.__parameterRange


class Bool(Type):

    def __init__(self, default = None, parameterRange = None):
        super(Bool, self).__init__(bool, 'type_bool', default, parameterRange)



class Int(Type):

    def __init__(self, default = None, parameterRange = None):
        super(Int, self).__init__(int, 'type_integer', default, parameterRange)



class Float(Type):

    def __init__(self, default = None, parameterRange = None):
        super(Float, self).__init__(float, 'type_float', default, parameterRange)



class String(Type):

    def __init__(self, default = None, parameterRange = None):
        super(String, self).__init__(str, 'type_string', default, parameterRange)



class MetaClass(type):

    __typeClassMapping = { 'type_bool' : Bool,
                           'type_integer' : Int,
                           'type_float' : Float,
                           'type_string' : String }
    conf = None
    cursor = None
    parameterSet = None

    def __call__(self, *args, **kwargs):
        self.conf = config.Configuration()
        self.conf.read('.campaign.conf')
        db.Database.connectConf(self.conf)
        self.cursor = db.Database.getCursor()

        if kwargs.has_key('campaignId'):
            self.conf.campaignId = kwargs['campaignId']
        self.cursor.execute('SELECT DISTINCT parameter_name, parameter_type FROM parameters WHERE campaign_id = %d' % self.conf.campaignId)
        sqlParameterList = self.cursor.fetchall()
        self.cursor.connection.commit()
        self.parameterSet = copy.deepcopy(self.newParameterSet)
        if kwargs.has_key('campaignId'):
            campaignId = Int()
            campaignId.setValue(kwargs.pop('campaignId'))
            self.parameterSet['campaignId'] = campaignId
        for paramName, param in self.parameterSet.items():
            setattr(self, paramName, property(fset = param.setValueProperty, fget = param.getValueProperty))
        for paramName, paramType in sqlParameterList:
            if self.parameterSet.has_key(paramName):
#                print 'Parameter already known'
                if self.parameterSet[paramName].getType() != paramType.strip():
#                    print self.parameterSet[paramName].getType()
#                    print paramType.strip()
                    raise 'Error'
            else:
                param = self.__typeClassMapping[paramType.strip()]()
                self.parameterSet[paramName] = param

#                print 'paramName property', paramName
                setattr(self, paramName, property(fset = param.setValueProperty, fget = param.getValueProperty))

        obj = type.__call__(self, *args, **kwargs)
        return obj


    def __new__(meta, className, bases, newAttrs):
        newParameterSet = {}
        for attrName, attr in newAttrs.items():
            if isinstance(attr, Type):
#                print attrName
#                newAttrs[attrName] = property(fset = attr.setValueProperty, fget = attr.getValueProperty)
                newAttrs.pop(attrName)
                newParameterSet[attrName] = attr
#        print newAttrs
        cls = type.__new__(meta, className, bases, newAttrs)
        cls.newParameterSet = newParameterSet
        return cls



class Parameters(object):

    __metaclass__ = MetaClass


    def __buildSqlQuery(self, table, paramType, paramValue, paramName, campaignId):
        return '(SELECT * FROM parameters WHERE scenario_id IN (SELECT scenario_id FROM %s AS x WHERE %s = \'%s\' AND parameter_name = \'%s\') AND campaign_id = %d)' % (table, paramType, str(paramValue), paramName, campaignId)


    def write(self):
        writeParameterSet = {}
        writeParameterSetWithoutDefaults = {}
        parameterSetWithoutDefaults = copy.deepcopy(self.parameterSet)
        for paramName, param in parameterSetWithoutDefaults.items():
            param.setValue(None)
        sqlQuery = 'parameters'
        sqlQueryWithoutDefaults = 'parameters'

        for paramName, param in self.parameterSet.items():
 #           print 'paramName, param', paramName, param
            if param.getValue() is not None:
                writeParameterSet[paramName] = copy.deepcopy(param)
                sqlQuery = self.__buildSqlQuery(sqlQuery, param.getType(), param.getValue(), paramName, self.conf.campaignId)
                if param.getValue() != param.getDefault():
                    writeParameterSetWithoutDefaults[paramName] = copy.deepcopy(param)
                    parameterSetWithoutDefaults[paramName] = copy.deepcopy(param)
                    sqlQueryWithoutDefaults = self.__buildSqlQuery(sqlQueryWithoutDefaults, param.getType(), param.getValue(), paramName, self.conf.campaignId)

        statement = 'SELECT DISTINCT scenario_id FROM %s AS subquery' % sqlQuery
#        print statement
        self.cursor.execute(statement)
        result = self.cursor.fetchall()
#        print result
        statement2 = 'SELECT DISTINCT scenario_id FROM %s AS subquery' % sqlQueryWithoutDefaults
#        print statement2
        self.cursor.execute(statement2)
        resultWithoutDefaults = self.cursor.fetchall()
#        print resultWithoutDefaults
        self.cursor.connection.commit()

#        print 'writeParameterSet ', writeParameterSet

        if len(result) == 1:
#            print 'Scenario with parameter set already exists'
            return
        elif len(result) == 0:
            parameterSetDefault = []
            for line in resultWithoutDefaults:
#                print parameterSetWithoutDefaults
                equal = True
                for scenario in self.readScenario(line[0], copy.deepcopy(self.parameterSet)).items():
#                    print parameterSetWithoutDefaults[scenario[0]]
#                    print scenario
                    if parameterSetWithoutDefaults[scenario[0]].getValue() != scenario[1].getValue():
                        equal = False
                        break
                if equal:
                    parameterSetDefault.append(line[0])

            if len(parameterSetDefault) == 0:
#                print 'Adding new scenario with parameter set'

                self.cursor.execute('INSERT INTO scenarios (campaign_id, current_job_id, state, max_sim_time, current_sim_time, sim_time_last_write) ' \
                                    'VALUES (%d, 0, \'NotQueued\', 0.0, 0.0, 0.0)' % self.conf.campaignId)
                self.cursor.execute('SELECT currval(\'scenarios_id_seq\')')
                scenarioId = self.cursor.fetchone()[0]

                for paramName, param in writeParameterSet.items():
                    statement = 'INSERT INTO parameters (campaign_id, scenario_id, parameter_type, parameter_name, %s) VALUES (%d, %d, \'%s\', \'%s\', \'%s\')' % \
                                        (param.getType(), self.conf.campaignId, scenarioId, param.getType(), paramName, str(param.getValue()))
#                    print statement
                    self.cursor.execute(statement)

                self.cursor.connection.commit()
            elif len(parameterSetDefault) == 1:
#                print 'Adding defaults to existing scenario'

                for paramName, paramType in writeParameterSet.items():
                    if paramType.getValue() == paramType.getDefault() and paramType.getValue() is not None:
                        self.cursor.execute('INSERT INTO parameters (campaign_id, scenario_id, parameter_type, parameter_name, %s) VALUES (%d, %d, \'%s\', \'%s\', \'%s\')' % \
                                            (paramType.getType(), self.conf.campaignId, parameterSetDefault[0], paramType.getType(), paramName, str(paramType.getValue())))
                self.cursor.connection.commit()
            else:
#                print 'a', parameterSetDefault
                raise 'Error'
        else:
            raise 'Error'


    def __convertFromSql(self, sqlResult, parameterSet):
        typeMapping = { 'type_bool' : 2,
                        'type_integer' : 3,
                        'type_float' : 4,
                        'type_string' : 5 }

#        parameterSet = copy.deepcopy(self.parameterSet)

        for paramName, param in parameterSet.items():
            param.setValue(None)

        for line in sqlResult:
#            print line
            parameterSet[line[0]].setValue(line[typeMapping[line[1].strip()]])

        return parameterSet


    def readScenario(self, scenarioId, parameterSet):
        self.cursor.execute('SELECT parameter_name, parameter_type, type_bool, type_integer, type_float, type_string  FROM parameters WHERE campaign_id = %d AND scenario_id = %d' % (self.conf.campaignId, scenarioId))
        result = self.cursor.fetchall()
        self.cursor.connection.commit()
        return self.__convertFromSql(result, parameterSet)


    def read(self, scenarioId):
        return self.readScenario(scenarioId, self.parameterSet)


    def readAllScenarios(self):
        self.cursor.execute('SELECT parameter_name, parameter_type, type_bool, type_integer, type_float, type_string, scenario_id FROM parameters WHERE campaign_id = %d ORDER BY scenario_id ASC' % self.conf.campaignId)
        result = self.cursor.fetchall()
#        print result

        allParametersDict = {}

        if len(result) > 0:
            scenarioId = result[0][6]
        else:
            return allParametersDict

        scenarioParameterList = []

        for line in result:
            if line[6] == scenarioId:
                scenarioParameterList.append(line)
            else:
                allParametersDict[scenarioId] = self.__convertFromSql(scenarioParameterList, copy.deepcopy(self.parameterSet))
                scenarioId = line[6]
                scenarioParameterList = [line]

        allParametersDict[scenarioId] = self.__convertFromSql(scenarioParameterList,  copy.deepcopy(self.parameterSet))

        return allParametersDict

class AutoSimulationParameters(Parameters):

    def __init__(self, inputVariableName, cursor, campaignId, getResults):
        assert(inputVariableName in self.parameterSet.keys())
        self.__inputVariableName = inputVariableName

        self.__cursor = cursor
        self.__campaignId = campaignId
        self.__getResultsFunction = getResults

        self.__iterationIndex = {}
        for k in sorted(self.parameterSet.keys()):
            if (k == self.__inputVariableName):
                continue
            v = self.parameterSet[k]
            assert(v.getRange() is not None)
            v.setValue(v.getRange()[0])
            self.__iterationIndex[k] = 0
        self.__iterationCompleted = False

        # write inital scenario to create the database
        self.__setInput(self.parameterSet[self.__inputVariableName].getDefault())
        self.write()

        myQuery = "select administration.create_parameter_sets_view(%i);" % campaignId
        cursor.execute(myQuery)
        cursor.fetchall()

        self.__currentValuesFinished = False

    def binarySearch(self, maxError = 0.1, exactness=0.05, createSimulations=True, debug=False, maxNumSimulations=25):
        finalResults = []
        stats = dict()
        stats['finished'] = 0
        stats['waiting'] = 0
        stats['new'] = 0
        for results in self:
            if(debug):
                 print self.__getCurrentParameters(), ":",

            if(self.__currentValuesFinished):
                if(len(results) > 0):
                    inputColumn = [i[1] for i in results]
                    lowerBound = min(inputColumn)/2
                    upperBound = max(inputColumn)*2

                    for(scenarioId, input, output) in results:
                        if(float(output)/input > 1-maxError):
                            lowerBound = max(lowerBound, input)
                        else:
                            upperBound = min(upperBound, input)

                    if(len(results) > maxNumSimulations):
                        print "Reached maximum number of simulations (%d) for the scenario with parameters" % (maxNumSimulations)
                        print self.__getCurrentParameters(onlyRanges = False)
                        print "Current result: ", lowerBound, "...", upperBound
                        finalResults.append(self.__getCurrentParameters())
                        finalResults[-1]['result'] = (upperBound+lowerBound)/2.0
                        finalResults[-1]['scenarioId'] = scenarioId
                        stats['finished'] += 1
                    elif(lowerBound == 0):
                        finalResults.append(self.__getCurrentParameters())
                        finalResults[-1]['result'] = lowerBound
                        finalResults[-1]['scenarioId'] = scenarioId
                        stats['finished'] += 1
                        if debug:
                            print lowerBound, "...", upperBound, "--> No result found, stop!"
                    elif(float(upperBound-lowerBound)/float(lowerBound) < exactness):
                        finalResults.append(self.__getCurrentParameters())
                        finalResults[-1]['result'] = (upperBound+lowerBound)/2.0
                        finalResults[-1]['scenarioId'] = scenarioId
                        stats['finished'] += 1
                        if debug:
                            print lowerBound, "...", upperBound, "--> Exactness <", exactness, ", stop!"
                    else:
                        new = 0
                        if(lowerBound == max(inputColumn)):
                            new = max(inputColumn)*2
                        elif(upperBound == min(inputColumn)):
                            new = min(inputColumn)/2
                        else:
                            new = (upperBound+lowerBound)/2
                        self.__setInput(new)
                        stats['new'] += 1
                        if(createSimulations):
                            self.write()
                        if debug:
                            print lowerBound, "...", upperBound, "--> newValue", new
                else:
                    self.__setInput(self.parameterSet[self.__inputVariableName].getDefault())
                    if(createSimulations):
                        self.write()
                    stats['new'] += 1
                    if debug:
                        print "initial simulation"
            else:
                stats['waiting'] += 1
                if debug:
                    if(len(results) > 0):
                        inputColumn = [i[1] for i in results]
                        lowerBound = min(inputColumn)/2
                        upperBound = max(inputColumn)*2
                        for(scenarioId, input, output) in results:
                            if(float(output)/input > 1-maxError):
                                lowerBound = max(lowerBound, input)
                            else:
                                upperBound = min(upperBound, input)
                        print lowerBound, "...", upperBound," waiting for output"
                    else:
                        print "waiting for output"


        return(stats, finalResults)

    def __iter__(self):
        return self

    def next(self):
        if(self.__iterationCompleted):
            self.__iterationCompleted = False
            raise StopIteration

        # assign the current one
        for k in sorted(self.parameterSet.keys()):
            if(k == self.__inputVariableName):
                continue
            v = self.parameterSet[k]
            v.setValue(v.getRange()[self.__iterationIndex[k]])

        # iterate to the next one
        for (i, k) in enumerate(sorted(self.parameterSet.keys())):
            if(k == self.__inputVariableName):
                continue
            v = self.parameterSet[k]
            if(self.__iterationIndex[k]+1 < len(v.getRange())):
                self.__iterationIndex[k] += 1
                break
            else:
                self.__iterationIndex[k] = 0
                if(i == len(self.parameterSet.keys())-1):
                    self.__iterationCompleted = True

        # check the status of the simulations
        unfinishedId = -1
        myQuery = "SELECT scenario_id FROM parameter_sets WHERE " + self.__getCurrentParametersSQL() + ";"
        self.__cursor.execute(myQuery)
        ids = [el[0] for el in self.__cursor.fetchall()]
        for scenarioId in ids:
            self.__cursor.execute('SELECT state, current_job_id FROM scenarios WHERE campaign_id = %d AND id = %d' % (self.__campaignId, scenarioId))
            results = self.__cursor.fetchall()
            if(results[0][0] != 'Finished'):
                unfinishedId = results[0][1]

        if(unfinishedId > -1):
            # abort for this parameter set until all simulations are ready
            self.__currentValuesFinished = False
        else:
            self.__currentValuesFinished = True

        return(self.__getResultsFunction(self.__getCurrentParametersSQL(), self.__inputVariableName, self.__cursor))

    def __setInput(self, value):
        self.parameterSet[self.__inputVariableName].setValue(value)

    def __getCurrentParameters(self, onlyRanges = True):
        r = {}
        for k in sorted(self.parameterSet.keys()):
            if(k == self.__inputVariableName):
                continue
            v = self.parameterSet[k]
            if(onlyRanges):
                if(len(v.getRange()) > 1):
                    r[k] = v.getValue()
            else:
                r[k] = v.getValue()
        return r

    def __getCurrentParametersSQL(self):
        r = ""
        for (k, v) in self.__getCurrentParameters(onlyRanges=False).items():
            if(isinstance(v, str)):
                r += (k + " = \'" + v + "\' AND ")
            else:
                r += (k + " = " + str(v) + " AND ")
        r = r[0:-5]
        return r






