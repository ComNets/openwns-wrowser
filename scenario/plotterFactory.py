from PyQt4 import QtCore, QtGui

import generic
import inspect

def create(scenarioFilename):
    
    inspector = inspect.ConfigInspector(scenarioFilename)

    return generic.GenericPlotter(inspector)
