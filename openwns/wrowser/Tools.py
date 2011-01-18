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

from PyQt4 import QtCore, QtGui

def classAndInstanceDict(instance):
    """Join class and instance attribute dicts.
    """
    return dict(instance.__class__.__dict__.items() + instance.__dict__.items())

def uniqElements(probeNames):
    def numCommonElements(probeNames):
        for i in range(len(probeNames[0].split(';')[0].split('.'))) :
            prefix = probeNames[0].split('.')[0:i]
            for probe in probeNames :
                if prefix != probe.split('.')[0:i] :
                    return i-1
            i+=1 
        return i-1

    uniqParts = []
    uniqStart = numCommonElements(probeNames)
    for probe in probeNames :
       probeNameParts=len(probe.split('.'))  
       uniqParts.append(".".join(probe.split('.')[uniqStart:]))
    return uniqParts

class ParameterWriter:
    out = None
    def __init__(self, outstream):
        self.out = outstream

    def write(self, name, value, comment=''):
        if len(comment)>0:
            comment = " #"+comment
        if type(value) == str : 
            self.out.write("  "+name + " = \'" + value + "\'")
        else:
            self.out.write("  "+name + " = " + str(value))
        self.out.write(comment+"\n")


class Chameleon:
    """Class with variable attributes.

    On instantiation of Chameleon, the object will get as attributes all keyword parameters
    you specify.
    """
    def __init__(self, **attribs):
        for name, value in attribs.items():
            setattr(self, name, value)

def dict2string(dic, separator = "; ", displayNoneValue = False):
    """Convert a dict to a nice string.
    """
    s = ""
    for key, value in dic.items():
        if len(s) > 0:
            s += separator
        if key != None or displayNoneValue:
            s += str(key)
        if value != None or displayNoneValue:
            s += ": " + str(value)
    return s

class ObjectFilterError(Exception):
    """Raised, if the stringexpression could not be evaluated.
    """
    def __init__(self, stringexpression):
        self.stringexpression = stringexpression

    def __str__(self):
        return "Could not evaluate '" + self.stringexpression + "'"

def objectFilter(stringexpression, objectList, viewGetter = classAndInstanceDict):
    """Return all objects in 'objectList' for which 'stringexpression' applies.

    'stringexpression' must be a string containing a valid python expression that
    can be evaluated against the entries in the dict returned by 'viewGetter'
    for all instances in 'objectList'. 'viewGetter' defaults to returning the
    attributes of each object. If you want to specify that 'stringexpression'
    should be checked against the dict attribute foo, use 'viewGetter = lambda x: x.foo'.
    Or if you want to check against the attributes of the attribute foo (which
    then is a class instance), use 'viewGetter = lambda x: classAndInstanceDict(x.foo)'.
    """
    instanceList = []
    for instance in objectList:
        try:
            if eval(stringexpression,
                    # we don't want globals...
                    {},
                    viewGetter(instance)):
                instanceList.append(instance)
        except NameError:
            instanceList.append(instance)
        except:
            raise ObjectFilterError(stringexpression)
    return instanceList

def convert(expression):
    """Convert the string 'expression' to its best python representation.

    convert('1') will return an int, convert('2.3') will return a float and so on.
    If 'expression' cannot be converted returns 'expression' as string.
    """
    try:
        return eval(expression, {}, {})
    except:
        return expression

class Observable(object):

    def __init__(self):
        self.emitter = QtCore.QObject()

    def __setattr__(self, name, value):
        object.__setattr__(self, name, value)
        self.emitter.emit(QtCore.SIGNAL("changed"), name, value, self)
        self.emitter.emit(QtCore.SIGNAL(name + "_changed"), value)

class Observing:

    def observe(self, callable, subject, attribName = ""):
        if attribName != "":
            self.connect(subject.emitter, QtCore.SIGNAL(attribName + "_changed"), callable)
        else:
            self.connect(subject.emitter, QtCore.SIGNAL("changed"), callable)

class URI(Observable):
    def __init__(self,
                 scheme = "",
                 user = "",
                 password = "",
                 host = "",
                 port = "",
                 database = "",
                 parameters = ""):

        Observable.__init__(self)
        self.scheme = scheme
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.database = database
        self.parameters = parameters

    def toString(self, withPassword = False):
        uri = self.scheme + "://"
        if len(self.user) > 0:
            uri += self.user
            if withPassword and len(self.password) > 0:
                uri += ":" + self.password
            uri += "@"
        if len(self.host) > 0:
            uri += self.host
            if len(self.port) > 0:
                uri +=":" + self.port
        if not self.database.startswith("/"):
            uri += "/"
        uri += self.database
        if len(self.parameters) > 0:
            uri += "?" + self.parameters
        return uri

    def __str__(self):
        return self.toString()

    def parse(self, uri):

        def split(s, sep, minsplit, maxsplit):
            l = s.split(sep, maxsplit - 1)
            while len(l) < minsplit:
                l += [""]
            return l

        self.scheme, location = split(uri, "://", 2, 2)
        loginHostPort, databaseParameters = split(location, "/", 2, 2)
        self.database, self.parameters = split(databaseParameters, "?", 2, 2)
        if "@" in loginHostPort:
            login, hostPort = split(loginHostPort, "@", 2, 2)
        else:
            login = ""
            hostPort = loginHostPort
        if ":" in login:
            self.user, self.password = split(login, ":", 2, 2)
        else:
            self.user = login
        self.host, self.port = split(hostPort, ":", 2, 2)


def renderLineSampleImage(line, width, dpi = 100):
    import Debug
#    Debug.printCall(None, (line, width))
    from matplotlib.backends.backend_agg import RendererAgg as Renderer
    from matplotlib.lines import Line2D
    useValue = True
    try:
        from matplotlib.transforms import Value
    except ImportError:
        useValue = False

    from PyQt4 import QtGui

    attributes = ["antialiased", "color", "dash_capstyle", "dash_joinstyle",
                  "linestyle", "linewidth", "marker", "markeredgecolor",
                  "markeredgewidth", "markerfacecolor", "markersize",
                  "solid_capstyle", "solid_joinstyle"]

    lineAttributes = dict()
    for attribute in attributes:
        lineAttributes[attribute] = getattr(line, "get_" + attribute)()

    height = max(lineAttributes["linewidth"], lineAttributes["markersize"] * 1.4 + 2 + 2*lineAttributes["markeredgewidth"])
    pixmapWidth = int(width + lineAttributes["markersize"] * 1.4 + 2 + 2*lineAttributes["markeredgewidth"]) + 1
    markerSize = lineAttributes["markersize"]
    if(useValue):
        renderer = Renderer(pixmapWidth, height, Value(dpi))
    else:
        renderer = Renderer(pixmapWidth, height, dpi)

    linePos = int(height / 2 + 1)
    sampleLine = Line2D([markerSize, pixmapWidth - markerSize], [linePos, linePos], **lineAttributes)
    sampleLine.draw(renderer)

    lineImageStr = renderer.tostring_argb()
    lineARGB = [map(ord, lineImageStr[i:i+4]) for i in xrange(0, len(lineImageStr), 4)]

    image = QtGui.QImage(pixmapWidth, height, QtGui.QImage.Format_ARGB32)
    for x in xrange(pixmapWidth):
        for y in xrange(int(height)):
            argb = lineARGB[x + y * pixmapWidth]
            image.setPixel(x, y, QtGui.qRgba(argb[1], argb[2], argb[3], argb[0]))
    return image

class ProbeFilterValidator(QtGui.QValidator):

    def __init__(self, probesModel, parent):
        QtGui.QValidator.__init__(self, parent)
        self.probesModel = probesModel

    def validate(self, input, pos):
        if len(self.probesModel.getProbeNamesFilteredBy(str(input))) == 0:
            return (QtGui.QValidator.Intermediate, pos)
        else:
            return (QtGui.QValidator.Acceptable, pos)
