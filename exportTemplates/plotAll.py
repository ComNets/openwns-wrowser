#!/usr/bin/python

import imp
import wrowser.FigurePlotter
import pprint
import os

for fileName in os.listdir('.'):
    if fileName.endswith('Plot.py'):
        print "file:",fileName
        module = imp.load_module('PlotParameters', file(fileName), '.', ('.py', 'r', imp.PY_SOURCE))
        #module.PlotParameters.color = False #parameter is modified for all plots
        wrowser.FigurePlotter.plotGraphs(module.PlotParameters)

