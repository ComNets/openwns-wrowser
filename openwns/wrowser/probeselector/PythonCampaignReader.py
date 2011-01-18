import os
import collections
import Representations
from .. import Probe

class NoScenarioDir(Exception):
    def __int__(self, dirName):
        self.dirName = dirName

    def __str_(self):
        return 'Directory "%s" is not a scenario directory!'


class MomentsPythonCampaign(Probe.MomentsProbeBase):

    valueNames = ['value']

    def __init__(self, value, name):
        self.value = value
        self.description = name


class PDFPythonCampaignHistogramEntry:
    def __init__(self, listOfValues):
        self.x = float(listOfValues[0])
        self.cdf = float(listOfValues[1])
        self.ccdf = float(listOfValues[2])
        self.pdf = float(listOfValues[3])


class PDFPythonCampaign(Probe.PDFProbeBase):

    valueNames = []

    def __init__(self, path, name):
        self.path = path
        self.__histogram = []
        self.__histogramRead = False
        self.description = name

    def __getHistogram(self):
        if self.__histogramRead == False:
            self.__histogram = []
            fh = open(self.path, 'r')
            for line in fh.readlines():
                if line.startswith(self.description):
                    histogramData = eval(line.split('=')[1])
                    break
            fh.close()
            for histoBin in histogramData:
                self.__histogram.append(PDFPythonCampaignHistogramEntry(histoBin))
            self.__histogramRead = True
        return self.__histogram

    histogram = property(__getHistogram)
    pureHistogram = property(__getHistogram)


class TimeSeriesPythonCampaignEntry(object):
    def __init__(self, listOfValues):
        self.x = float(listOfValues[0])
        self.y = float(listOfValues[1])


class TimeSeriesPythonCampaign(Probe.TimeSeriesProbeBase):

    valueNames = []

    def __init__(self, entriesData, name):
        self.entriesData = entriesData
        self.__entries = []
        self.__entriesRead = False
        self.description = name

    def __getEntries(self):
        if self.__entriesRead == False:
            self.__entries = []
            for entry in self.entriesData:
                self.__entries.append(TimeSeriesPythonCampaignEntry(entry))
            self.__entriesRead = True
        return self.__entries

    entries = property(__getEntries)



class Probe:
    def __init__(self, name, probeClass, probe):
        self.name = name
        self.probeClass = probeClass
        self.probe = probe

    def getData(self):
        return self.probe

    def getName(self):
        return self.name


class PythonCampaignScenario:

    def __init__(self, directoryName, resultsFileName, pdfsFileName, timeSeriesFileName):
        self.directoryName = directoryName
        self.resultsFileName = resultsFileName
        self.pdfsFileName = pdfsFileName
        self.timeSeriesFileName = timeSeriesFileName
        self.__probesDict = None

    def getProbes(self):
        if self.__probesDict == None:
            probesDict = {}
            results = {}

            resultsFileName = os.path.join(self.directoryName, self.resultsFileName)
            if os.path.exists(resultsFileName):
                try:
                    fh = open(resultsFileName, 'r')
                    for line in fh.readlines():
                        results[line.split('=')[0].strip(' ')] = eval(line.split('=')[1])
                    fh.close()
                except Exception:
                    raise NoScenarioDir(self.directoryName)

            for key, value in results.iteritems():
                probesDict[key] = Representations.Probe(Probe(key, MomentsPythonCampaign, MomentsPythonCampaign(value, key)))

            pdfs = []
            pdfsFileName = os.path.join(self.directoryName, self.pdfsFileName)
            if os.path.exists(pdfsFileName):
                try:
                    fh = open(pdfsFileName, 'r')
                    for line in fh.readlines():
                        pdfs.append(line.split('=')[0].strip(' '))
                    fh.close()
                except Exception:
                    raise NoScenarioDir(self.directoryName)

            for key in pdfs:
                probesDict[key] = Representations.Probe(Probe(key, PDFPythonCampaign, PDFPythonCampaign(pdfsFileName, key)))


            globals = {}
            timeSeries = {}
            timeSeriesFileName = os.path.join(self.directoryName, self.timeSeriesFileName)
            if os.path.exists(timeSeriesFileName):
                try:
                    execfile(timeSeriesFileName, globals, timeSeries)
                except Exception:
                    raise NoScenarioDir(self.directoryName)

            for key, value in timeSeries.iteritems():
                probesDict[key] = Representations.Probe(Probe(key, TimeSeriesPythonCampaign, TimeSeriesPythonCampaign(value, key)))
            self.__probesDict = probesDict

        return self.__probesDict


class PythonCampaignCampaignReader:

    def __init__(self,
                 directoryName,
                 parametersFileName = 'parameters',
                 resultsFileName = 'results',
                 pdfsFileName = 'pdfs',
                 timeSeries = 'timeSeries'):
        self.directoryName = directoryName
        self.parametersFileName = parametersFileName
        self.resultsFileName = resultsFileName
        self.pdfsFileName = pdfsFileName
        self.timeSeries = timeSeries

    def read(self):
        scenarioList = []
        parametersDict = collections.defaultdict(list)

        for fileName in os.listdir(self.directoryName):
            filePath = os.path.join(self.directoryName, fileName)
            if os.path.isdir(filePath):
                try:
                    paramsFileName = os.path.join(filePath, self.parametersFileName)
                    if os.path.exists(paramsFileName):
                        try:
                            parameters = {}
                            fh = open(paramsFileName, 'r')
                            for line in fh.readlines():
                                parameters[line.split('=')[0].strip(' ')] = eval(line.split('=')[1])
                            fh.close()

                            if len(parameters) != 0:
                                scenarioList.append(Representations.Scenario(PythonCampaignScenario(filePath,
                                                                                                    self.resultsFileName,
                                                                                                    self.pdfsFileName,
                                                                                                    self.timeSeries),
                                                                             parameters))

                        except Exception:
                            raise NoScenarioDir(filePath)

                        for paramName, paramValue in parameters.iteritems():
                            if paramValue not in parametersDict[paramName]:
                                parametersDict[paramName].append(paramValue)
                except NoScenarioDir:
                    pass

        return scenarioList, parametersDict
