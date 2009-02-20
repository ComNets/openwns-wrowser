
from FileReaders import ProbeReader, ScenarioReader
import Representations

import os

class CampaignReader:

    def __init__(self,
                 directory,
                 progressNotify = None):

        self.path = os.path.abspath(directory)
        self.progressNotify = progressNotify

    def read(self):
        directories = [self.path]
        for base, subDirs, files in os.walk(self.path):
            if callable(self.progressNotify):
                self.progressNotify(1, 1000, "scanning\n" + base)
            for subDir in subDirs:
                directories += [os.path.join(base, subDir)]
        scenarios = []
        maxIndex = len(directories)
        for index, directory in enumerate(directories):
            Scenario = Representations.Scenario
            scenario = Scenario(ScenarioReader(os.path.abspath(directory)),
                                {"directory": directory},
                                True)
            if len(scenario.probes) > 0:
                scenarios.append(scenario)
            if callable(self.progressNotify):
                self.progressNotify(index + 1, maxIndex, "reading\n" + directory)
        return scenarios, ["directory"]
