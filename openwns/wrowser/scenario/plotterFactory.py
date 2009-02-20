from PyQt4 import QtCore, QtGui

import generic
import inspect

class InvalidConfig:
    pass

def create(scenarioFilename):
    
    try:
        inspector = inspect.ConfigInspector(scenarioFilename)
    except inspect.SimulatorConfigNotFound:
        raise InvalidConfig()

    return generic.GenericPlotter(inspector)
