import os
import wrowser.Configuration as conf
import simdb.Database as db
import simdb.ProbeDB


class Type(object):
    def __init__(self, variableType, sqlParameterType, value):
        self.value = variableType(value)
        self.sqlParameterType = sqlParameterType

    def getType(self):
        return self.sqlParameterType

    def getValue(self):
        return self.value

class Bool(Type):
    def __init__(self, value):
        super(Bool, self).__init__(bool, 'type_bool', value)

class Int(Type):
    def __init__(self, value):
        super(Int, self).__init__(int, 'type_integer', value)

class Float(Type):
    def __init__(self, value):
        super(Float, self).__init__(float, 'type_float', value)

class String(Type):
    def __init__(self, value):
        super(String, self).__init__(str, 'type_string', value)


class WriteResultsHook:
    def __init__(self, campaignName, parameterDict = {}, addScenarioId = True, skipNullTrials = False, description = "Default description of WriteResultHook"):
        self.campaignName = campaignName
        self.parameterDict = parameterDict
        self.addScenarioId = addScenarioId
        self.skipNullTrials = skipNullTrials
        self.matchingScenarios = None

        # get campaignId
        ## get DB connection
        self.conf = conf.Configuration()
        self.conf.read()
        db.Database.connectConf(self.conf)
        self.cursor = db.Database.getCursor()

        ## try to get campaignId
        self.cursor.execute("SELECT id FROM campaigns WHERE title = '%s'" % (self.campaignName))
        result = self.cursor.fetchall()
        ## not in DB -> create new
        if len(result) == 0:
            self.cursor.execute("INSERT INTO campaigns (title, description) VALUES ('%s', '%s')" % (self.campaignName, description))
            self.cursor.execute("SELECT id FROM campaigns WHERE title = '%s'" % (self.campaignName))
            result = self.cursor.fetchall()
            self.campaignId = result[0][0]
        ## found in DB -> use
        elif len(result) == 1:
            self.campaignId = result[0][0]
        ## more than one campaign with this title in DB
        else:
            raise Exception("More than one campaign with title '%s' in database (not allowed)" % (self.campaignName))

        self.conf.campaignId = self.campaignId

        def __buildSqlQuery(table, paramType, paramValue, paramName, campaignId):
            return '(SELECT * FROM parameters WHERE scenario_id IN (SELECT scenario_id FROM %s AS x WHERE %s = \'%s\' AND parameter_name = \'%s\') AND campaign_id = %d)' % (table, paramType, str(paramValue), paramName, campaignId)

        if self.addScenarioId:
            self.matchingScenarios = []
        else:
            if len(self.parameterDict) == 0:
                raise Exception('Cannot write results to database: No parameters specified')

            sqlQuery = 'parameters'
            for key, value in self.parameterDict.iteritems():
                sqlQuery = __buildSqlQuery(sqlQuery, value.getType(), value.getValue(), key, self.conf.campaignId)

            statement = 'SELECT DISTINCT scenario_id FROM %s AS subquery' % sqlQuery
            self.cursor.execute(statement)
            self.matchingScenarios = self.cursor.fetchall()

            if len(self.matchingScenarios) > 1:
                raise Exception('Cannot write results to database: More than one scenario stored in database matches given parameter set')


    def __call__(self, simulator):
        if len(self.matchingScenarios) == 0:
            self.cursor.execute('INSERT INTO scenarios (campaign_id, current_job_id, state, max_sim_time, current_sim_time, sim_time_last_write) ' \
                                'VALUES (%d, 0, \'NotQueued\', 0.0, 0.0, 0.0)' % self.campaignId)
            self.cursor.execute('SELECT currval(\'scenarios_id_seq\')')
            scenarioId = self.cursor.fetchone()[0]

            if self.addScenarioId:
                self.parameterDict.update({'scenarioId' : Int(scenarioId)})

            for key, value in self.parameterDict.iteritems():
                self.cursor.execute('INSERT INTO parameters (campaign_id, scenario_id, parameter_type, parameter_name, %s) VALUES (%d, %d, \'%s\', \'%s\', \'%s\')' % \
                                    (value.getType(), self.campaignId, scenarioId, value.getType(), key, str(value.getValue())))
        elif len(self.matchingScenarios) == 1:
            scenarioId = self.matchingScenarios[0][0]
            pywns.simdb.ProbeDB.removeAllProbesFromDB(scenarioId, config = self.conf)
        elif len(self.matchingScenarios) > 1:
            raise Exception("Cannot write results to database: More than one scenario stored in database matches the given parameter set")

        pywns.simdb.ProbeDB.writeAllProbesIntoDB(simulator.outputDir, scenarioId, skipNullTrials = self.skipNullTrials, config = self.conf)

        db.Database.connectConf(self.conf)
        self.cursor = db.Database.getCursor()
        self.cursor.execute('UPDATE scenarios SET state=\'Finished\' WHERE campaign_id = %i AND id = %i' % (self.campaignId, scenarioId))
        self.cursor.connection.commit()

        return True
