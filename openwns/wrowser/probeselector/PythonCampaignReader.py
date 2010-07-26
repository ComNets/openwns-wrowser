import os
import collections
import Representations

class NoScenarioDir(Exception):
    def __int__(self, dirName):
        self.dirName = dirName

    def __str_(self):
        return 'Directory "%s" is not a scenario directory!'


class Value:

    valueNames = ['value']

    def __init__(self, value, name):
        self.value = value
        self.description = name

class Probe:
    def __init__(self, value, name):
        self.value = value
        self.name = name
        self.probeClass = Value

    def getData(self):
        return Value(self.value, self.name)

    def getName(self):
        return self.name


class PythonCampaignScenario:

    def __init__(self, directoryName, resultsFileName):
        self.directoryName = directoryName
        self.resultsFileName = resultsFileName

    def getProbes(self):
        probesDict = {}
        globals = {}
        results = {}

        resultsFileName = os.path.join(self.directoryName, self.resultsFileName)
        if os.path.exists(resultsFileName):
            try:
                execfile(resultsFileName, globals, results)
            except Exception:
                raise NoScenarioDir(self.directoryName)
        else:
            raise NoScenarioDir(self.directoryName)

        for key, value in results.iteritems():
            print key, value
            probesDict[key] = Representations.Probe(Probe(value, key))

        return probesDict


class PythonCampaignCampaignReader:

    def __init__(self,
                 directoryName,
                 parametersFileName = 'parameters',
                 resultsFileName = 'results'):
        self.directoryName = directoryName
        self.parametersFileName = parametersFileName
        self.resultsFileName = resultsFileName

    def read(self):
        scenarioList = []
        parametersDict = collections.defaultdict(list)

        for fileName in os.listdir(self.directoryName):
            filePath = os.path.join(self.directoryName, fileName)
            print filePath, self.parametersFileName
            if os.path.isdir(filePath):
                try:
                    paramsFileName = os.path.join(filePath, self.parametersFileName)
                    print paramsFileName
                    if os.path.exists(paramsFileName):
                        try:
                            globals = {}
                            parameters = {}
                            execfile(paramsFileName, globals, parameters)
                            print parameters
                        except Exception:
                            raise NoScenarioDir(filePath)
                        print parameters

                        scenarioList.append(Representations.Scenario(PythonCampaignScenario(filePath,
                                                                                           self.resultsFileName),
                                                                    parameters))

                    for paramName, paramValue in parameters.iteritems():
                        print parameters, paramName, paramValue
                        if paramValue not in parametersDict[paramName]:
                            parametersDict[paramName].append(paramValue)
                except NoScenarioDir:
                    pass

        print scenarioList, parametersDict
        return scenarioList, parametersDict
