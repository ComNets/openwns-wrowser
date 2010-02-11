import imp
import wrowser.FigurePlotter
import os

for fileName in os.listdir('.'):
    if fileName.endswith('.py') and fileName!='plotAll.py' :
        print "file:",fileName
        try:
            module = imp.load_module('PlotParameters', file(fileName), '.', ('.py', 'r', imp.PY_SOURCE))
            #module.PlotParameters.color = False #parameter is modified for all plots
            print "going to plot the figure"
            wrowser.FigurePlotter.loadCampaignAndPlotGraphs(module.PlotParameters)
        except ImportError :
            print "this file does not contain PlotParameters class"
