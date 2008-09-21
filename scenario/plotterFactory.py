from PyQt4 import QtCore, QtGui

import wnsrc
wnsrc.wnsrc.setPathToPyConfig('dbg')
import rise.scenario.Hexagonal
import rise.scenario.Manhattan

def create(configurationDict):
    for v in configurationDict.values():
        if isinstance(v, rise.scenario.Hexagonal.Hexagonal):
            from hexagonal import ScenarioPlotter
            return ScenarioPlotter(v)
        if isinstance(v, rise.scenario.Manhattan.Manhattan):
            from manhattan import ScenarioPlotter
            return ScenarioPlotter(v)

    return None
