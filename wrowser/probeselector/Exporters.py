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

class CSV:

    formatName = "CSV"

    @staticmethod
    def export(filename, graphs, progressNotify = None, progressReset = None):
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

class Matlab:

    formatName = "Matlab"

    @staticmethod
    def export(filename, graphs, progressNotify = None, progressReset = None):
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

