
from FileReaders import ProbeReader, ScenarioReader
import Representations

from Tools import convert

import os.path

class CampaignReader:
    """Reads a campaign from a DSV file.

    The DSV file needs to contain the values for the simulation parameters separated
    by a delimiter. The values are converted to the best python representation. Strings
    may not contain newlines. The first line in the file must contain the parameter names.
    One column of the file must contain the (sub-)directory where the results are stored.

    CampaignReader will call back to 'paramSelectUI.do()' to permit interactive
    selection of the simulation parameters from all columns in the file.
    """
    def __init__(self,
                 filepath,
                 paramSelectUI,
                 progressNotify = None,
                 appendToScenarioDirectory = "",
                 directoryEntry = "directory",
                 delimiter = ",",
                 prefetchProbeNames = False):
        """Construct a 'CampaignReader'.

        filepath: path to the DSV file.
        paramSelectUI: call back to user interface for parameter selection.
        appendToScenarioDirectory: the results subdirectory beneath the one from the directory column.
        directoryEntry: name of the directory column.
        delimiter: the delimiter used in the DSV file.
        """
        baseDirectory, filename = os.path.split(filepath)
        self.baseDirectory = os.path.abspath(baseDirectory)
        self.filename = filename
        self.paramSelectUI = paramSelectUI
        self.progressNotify = progressNotify
        self.appendToScenarioDirectory = appendToScenarioDirectory
        self.delimiter = delimiter
        self.directoryEntry = directoryEntry
        self.prefetchProbeNames = prefetchProbeNames

    def read(self):
        """Read campaign from file.

        This calls back to 'paramSelectUI.do(columns, deselectedColumns)' with
        'columns' beeing the columns from the file and 'deselectedColumns' beeing
        the name of the directory column.

        Returns a tuple (scenarios, parameterNames) that can be passed to
        '__init__' of 'Representations.Campaign' by unpacking.
        """
        f = file(os.path.join(self.baseDirectory, self.filename)).readlines()
        columns = map(lambda x: x.strip().strip('"'), f[0].split(self.delimiter))
        scenarios = []
        maxIndex = len(f) - 1
        for index, line in enumerate(f[1:]):
            values = line.strip().split(self.delimiter)
            values = map(lambda x: convert(x.strip('"')), values)
            parameterValues = dict(zip(columns, values))
            directory = str(parameterValues[self.directoryEntry])
            del parameterValues[self.directoryEntry]
            Scenario = Representations.Scenario
            scenario = Scenario(ScenarioReader(os.path.join(os.path.join(self.baseDirectory, directory),
                                                            self.appendToScenarioDirectory)),
                                parameterValues,
                                self.prefetchProbeNames)
            scenarios.append(scenario)
            if callable(self.progressNotify):
                self.progressNotify(index + 1, maxIndex, "reading directory " + directory)
        parameters = self.paramSelectUI.do(columns, [self.directoryEntry])
        if parameters == []:
            return [], []
        return scenarios, [parameter for parameter in parameters if parameter != self.directoryEntry]

