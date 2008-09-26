from PyQt4 import QtCore, QtGui

def create(scenarioInspector):
    from generic import GenericPlotter
    return GenericPlotter(scenarioInspector)
