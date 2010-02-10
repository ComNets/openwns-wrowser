###############################################################################
# This file is part of openWNS (open Wireless Network Simulator)
# _____________________________________________________________________________
#
# Copyright (C) 2004-2007
# Chair of Communication Networks (ComNets)
# Kopernikusstr. 16, D-52074 Aachen, Germany
# phone: ++49-241-80-27910,
# fax: ++49-241-80-22242
# email: info@openwns.org
# www: http://www.openwns.org
# _____________________________________________________________________________
#
# openWNS is free software; you can redistribute it and/or modify it under the
# terms of the GNU Lesser General Public License version 2 as published by the
# Free Software Foundation;
#
# openWNS is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

import inspect
import wrowser.Tools
import os
import subprocess

class CSV:

    formatName = "CSV"

    @staticmethod
    def export(filename, export , progressNotify = None, progressReset = None):
        graphs = export.graphs
        out = open(filename, "w")
        maxIndex = len(graphs)
        if callable(progressReset):
            progressReset()
        for index, graph in enumerate(graphs):
            if callable(progressNotify):
                msg = "Exporting " + str(graph.identity)
                progressNotify(index, maxIndex, msg)
            for point in graph.points:
                out.write('"' + str(graph.identity) + '", ')
                out.write(repr(point[0]) + ", " + repr(point[1]) + "\n")
        out.close()

class PythExport:

    formatName = "Python"
    
    @staticmethod
    def export(filename, export, progressNotify = None, progressReset = None):
        def writeParam(out, name, value, comment='' ):
            if len(comment)>0:
                  comment = " #"+comment
            if type(value) == str : 
                out.write("  "+name + " = \'" + value + "\'")
            else:
                out.write("  "+name + " = " + str(value))
            out.write(comment+"\n")

        def getDimensions(graphs):
            minX=graphs[0].points[0][0]
            maxX=graphs[0].points[-1][0]
            yvalues = []
            for graph in graphs :
                yvalues.append([y for x,y in graph.points])
            minY=min(min(yvalues))
            maxY=max(max(yvalues))
            return  [minX, maxX, minY, maxY]

 
        graphs = export.graphs
        typ = export.graphType #"param"
        location = filename.rpartition('/')
        file=location[-1]
        path=location[0]
        fullFName=path +"/"+ typ + "_" + file
        out = open(fullFName, "w")
        out.write("class PlotParameters : \n");
        writeParam(out,"probeName",export.probeName)
        writeParam(out,"probeLegendSuffix",wrowser.Tools.uniqElements(export.probeName))

        writeParam(out,"confidence",export.confidence)
        writeParam(out,"aggregate",export.aggregate)
        writeParam(out,"originalPlots",export.originalPlots)
        writeParam(out,"aggrParam",export.aggrParam)
        writeParam(out,"fileName",file)
        writeParam(out,"type", export.graphType)
        writeParam(out,"campaignId", str(export.campaignId))
        writeParam(out,"xLabel",export.graphs[0].axisLabels[0])
        if typ == 'Param':
            writeParam(out,"confidenceLevel",export.confidenceLevel)                
            writeParam(out,"yLabel",export.graphs[0].axisLabels[1])
            writeParam(out,"parameterName",export.paramName)
            writeParam(out,"probeEntry",export.probeEntry)
            writeParam(out,"useXProbe",export.useXProbe)
            writeParam(out,"useYProbe",export.useYProbe)
            if export.useXProbe:
                writeParam(out, "xProbeName",export.xProbeName)
                writeParam(out, "xProbeEntry",export.xProbeEntry)
            plotScript="./exportTemplates/readDBandPlot"
        else:
            writeParam(out,"yLabel","P(X)")
            plotScript="./exportTemplates/readDBandPlotXDF"

        writeParam(out,"filterExpression",export.filterExpr)
        
        dimensions=getDimensions(graphs)
        writeParam(out,"minX",dimensions[0])
        writeParam(out,"maxX",dimensions[1])
        writeParam(out,"minY",0,"min Y value is:"+str(dimensions[2]))
        writeParam(out,"maxY",dimensions[3])
        writeParam(out,"moveX",0)
        writeParam(out,"moveY",0)

        #graph config:
        writeParam(out,"grid",export.grid)
        writeParam(out,"scale",export.scale)
        writeParam(out,"marker",export.marker)
        writeParam(out,"legend", True) #export.legend)
        writeParam(out,"legendPosition","best","alternatives: upper right, upper left, lower left, lower right, right, center left, center right, lower center, upper center, center or (x,y) with x,y in [0-1]")
        writeParam(out,"showTitle",False)                
        writeParam(out,"figureTitle",export.title)                
        writeParam(out,"scaleFactorX",1,"1/1e6 #bit to MBit")                
        writeParam(out,"scaleFactorY",1,"1/1e6 #bit to MBit")                
        writeParam(out,"color",True)                
        out.close()
        if not file.endswith('.py'):
            file += '.py'
        outFName=path+"/"+file
        set_path = """#!/usr/bin/python
import sys
import os
sys.path.insert(0,\""""+ os.getcwd()+"\")\n"
        cmd="outf="+outFName+" ; echo '"+set_path+"' > $outf ; cat "+fullFName+" >> $outf ; cat ./exportTemplates/readDBandPlot >> $outf ; chmod u+x $outf"
#        print "cmd=",cmd
        subprocess.call(cmd, shell=True)
        if not os.path.exists(path+"/plotAll.py") :
            print "create plotAll.py script"
            import shutil
            shutil.copy('./exportTemplates/plotAll.py',path+"/plotAll.py")
        

class Matlab:

    formatName = "Matlab"

    @staticmethod
    def export(filename, export, progressNotify = None, progressReset = None):
        graphs = export.graphs
        if not filename.endswith('.m'):
            filename += '.m'

        out = open(filename, "w")
        out.write(
"""function h = Draw()
% colored linestyles
% linestyles = {'b';'r';'k';'m';'c';'g';'y'};

% monochrome linestyles
linestyles = {'k-'; 'k--';  'k:'; ...
              'k-+'; 'k--+'; 'k:+'; ... 
              'k-o'; 'k--o'; 'k:o'};

% define the fontSize for the labels
fontSize = 16; % Pt
% define the offset for the legend and axis ticks
offset = 4;
% define the default LineWidths
lineWidth = 2.0;
helperLineWidth = 1.0;

leg = {};
h = figure;
hold on
""")
        out.write("filename = '%s';\n" % (os.path.split(filename)[1].strip('.m')))
        maxIndex = len(graphs)
        if callable(progressReset):
            progressReset()
        for index, graph in enumerate(graphs):
            if callable(progressNotify):
                msg = "Exporting " + str(graph.identity)
                progressNotify(index, maxIndex, msg)

            out.write("X = [ ")
            for point in graph.points:
                out.write(repr(point[0]) + " ")
            out.write("];\n")
            out.write("Y = [ ")
            for point in graph.points:
                out.write(repr(point[1]) + " ")
            out.write("];\n")
            out.write("leg{size(leg,1)+1,1}='%s';\n" % wrowser.Tools.dict2string(graph.identity.parameters).replace('_',' '))
            out.write("plot(X,Y, linestyles{%d},'LineWidth',lineWidth)\n" % ((index % 9)+1))
        out.write("legend(leg,'Location','NorthEast')\n")
        graphTitle = graphs[0].identity.probe.replace('_',' ')
        out.write("% "+("title('%s','FontSize',fontSize)\n" % graphTitle))
        out.write("""
set(gca,'Box','on')
set(gca,'Position',[0.15 0.11 0.82 0.86])
set(gca,'FontSize',fontSize-offset)
l= legend(leg,'Location','Best','FontSize',fontSize-offset);
% xlim([xmin xmax])
% ylim([ymin ymax])
xlabel('x label [unit]','FontSize',fontSize)
ylabel('y label [unit]','FontSize',fontSize)
% set(gca,'XScale','log')
% set(gca,'YScale','log')
% print('-dpng', h, strcat(filename,'.png'))
%   pdf export does not get the bounding box right
% print('-dpdf', h, strcat(filename,'.pdf'))
print('-depsc', h, strcat(filename,'.eps'))
if strcmp(getenv('OS'),'Windows_NT')
   print('-dmeta', h, strcat(filename,'.wmf'))
end
"""
                  )
        out.close()




# Module support methods
# Add additional exporters above
directory = dict()

for obj in locals().values():
    if inspect.isclass(obj):
        if hasattr(obj, "formatName"):
            directory[obj.formatName] = obj

