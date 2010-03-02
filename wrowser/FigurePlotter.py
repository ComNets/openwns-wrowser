import optparse
import sys
import os
import math
import wrowser.Configuration as simDbConf
import wrowser.simdb.Database as simDb
from wrowser.simdb.Campaigns import setCampaign as simDbSetCampaign

from wrowser.probeselector import PostgresReader
from wrowser.probeselector import Interface
from wrowser.probeselector import Representations
from wrowser.probeselector import Errors
from wrowser.probeselector.Interface import Facade

from matplotlib import rc
from matplotlib.figure import Figure
from matplotlib.backends.backend_pdf import FigureCanvasPdf as FigureCanvas
from matplotlib.font_manager import FontProperties
from pylab import *

from scipy.special import erf

def loadCampaignAndPlotGraphs(PlotParameters):
    def lineStyle():

        for style in PlotParameters.color_styles :
            yield style

    def lineStyleBW():

        for style in PlotParameters.bw_styles :
            yield style

    def markerBW():

        for marker in PlotParameters.bw_markers :
            yield marker

    def hatches():

        for hatch in ['/','\\','|','-','+','x','.','//','\\' ]:
            yield hatch

    ## Get the campaign
    dbConfig = simDbConf.Configuration()
    dbConfig.read()
    simDb.Database.connectConf(dbConfig)
    simDbSetCampaign([int(PlotParameters.campaignId)])
    campaignReader = PostgresReader.CampaignReader(int(PlotParameters.campaignId), Interface.DoNotSelectProbeSelectUI())
    print 'Accessing charts from database server with campaignId: ' + str(PlotParameters.campaignId)


    print "Reading Campaign"
    campaign = Representations.Campaign(*campaignReader.read())
    print "Creating Facade:",
    ch = Interface.Facade(campaign)
    print "done"

    outputdir = 'figures'
    if not os.path.exists(outputdir) :
        os.makedirs(outputdir)

    font = FontProperties()
    font.set_size('x-large')

    filteredFacade = ch.filteredByExpression(PlotParameters.filterExpression)
    print "Found " + str(len(filteredFacade.getScenarios())) + " scenarios"

    figure(figsize=(9, 8))
    xlabel(PlotParameters.xLabel,fontproperties = font)
    ylabel(PlotParameters.yLabel,fontproperties = font)

    labels=[]

    if PlotParameters.color:
        ls = lineStyle()
    else:
        markerBW = markerBW()

    probeNr = 0
    try:
     if PlotParameters.type == 'Param':
        if PlotParameters.useXProbe:
            graphList = filteredFacade.getGraphs(PlotParameters.parameterName, PlotParameters.probeName, PlotParameters.probeEntry, PlotParameters.aggrParam, PlotParameters.confidence, PlotParameters.confidenceLevel, plotNotAggregatedGraphs=PlotParameters.originalPlots, useXProbe = PlotParameters.useXProbe, xProbeName = PlotParameters.xProbeName, xProbeEntry = PlotParameters.xProbeEntry)
        else:
            graphList = filteredFacade.getGraphs(PlotParameters.parameterName, PlotParameters.probeName, PlotParameters.probeEntry, PlotParameters.aggrParam, PlotParameters.confidence, PlotParameters.confidenceLevel, plotNotAggregatedGraphs=PlotParameters.originalPlots)
     else:
        graphList = filteredFacade.getHistograms( PlotParameters.probeName, PlotParameters.type, PlotParameters.aggrParam, plotNotAggregatedGraphs=PlotParameters.originalPlots) #, PlotParameters.aggrParam, PlotParameters.confidence)
    except Errors.MultipleErrors, e:
     graphList = e.graphs

    i=0
    if len(graphList)==0:
        print "no graphs to plot"
    marker=PlotParameters.marker
    for graphNum in PlotParameters.plotOrder :
        graph = graphList[graphNum]
        labels.append(str(graph.sortkey))

        try:
            if PlotParameters.color:
                style=ls.next()
            else:
                style='k'
                marker=markerBW.next()
        except StopIteration:
            print "You need to define more linestyles or reduce the number of plotted graphs"
            os._exit(1)
        X=[x  for x,y in graph.points]
        Y=[y*PlotParameters.scaleFactorY+PlotParameters.moveY  for x,y in graph.points]
        key = Facade.getGraphDescription(graph) #PlotParameters.legendLabelMapping.keys()[i]
        plot([x*PlotParameters.scaleFactorX+PlotParameters.moveX  for x in X ], Y , style , label=PlotParameters.legendLabelMapping[key],marker=marker)
        try:
          if PlotParameters.type == 'Param':
            if PlotParameters.confidence :
                for i in range(len(X)):
                    e = graph.confidenceIntervalDict[X[i]]
                    errorbar(X[i]*PlotParameters.scaleFactorX+PlotParameters.moveX, Y[i], yerr=e , fmt=style)
        except: None
        i+=1
    for additional in PlotParameters.additional_plots :
        plot(additional['x'], additional['y'] , additional['style'] , label=additional['label'])

    if PlotParameters.doClip:
        axis([PlotParameters.minX,PlotParameters.maxX,PlotParameters.minY,PlotParameters.maxY])
    scalex = PlotParameters.scale[0]
    scaley = PlotParameters.scale[2]
    if scalex != 'linear' :
        xbase = PlotParameters.scale[1]
        xscale('log',basex=xbase)
    if scaley != 'linear' :
        ybase= PlotParameters.scale[3]
        yscale('log',basey=ybase)
    a = gca()
    a.get_xaxis().grid(PlotParameters.grid[0], which="major")
    a.get_xaxis().grid(PlotParameters.grid[1], which="minor")
    a.get_yaxis().grid(PlotParameters.grid[2], which="major")
    a.get_yaxis().grid(PlotParameters.grid[3], which="minor")

    if PlotParameters.showTitle :
        title(PlotParameters.figureTitle)
    if PlotParameters.legend:
        legend(prop = font, loc=PlotParameters.legendPosition) # (0.9, 0.01))
    print 'Plotting: ',PlotParameters.fileName
    for format in PlotParameters.outputFormats :
        savefig(os.path.join(outputdir, PlotParameters.fileName+'.'+format))
