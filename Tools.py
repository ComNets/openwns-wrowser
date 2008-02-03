from PyQt4 import QtCore, QtGui

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
    from matplotlib.transforms import Value

    from PyQt4 import QtGui

    attributes = ["antialiased", "color", "dash_capstyle", "dash_joinstyle",
                  "linestyle", "linewidth", "marker", "markeredgecolor",
                  "markeredgewidth", "markerfacecolor", "markersize",
                  "solid_capstyle", "solid_joinstyle"]

    lineAttributes = dict()
    for attribute in attributes:
        lineAttributes[attribute] = getattr(line, "get_" + attribute)()

    height = lineAttributes["linewidth"]
    renderer = Renderer(width, height, Value(dpi))

    linePos = height / 2 + 1
    sampleLine = Line2D([0, width], [linePos, linePos], **lineAttributes)
    sampleLine.draw(renderer)

    lineImageStr = renderer.tostring_argb()
    lineARGB = [map(ord, lineImageStr[i:i+4]) for i in xrange(0, len(lineImageStr), 4)]

    image = QtGui.QImage(width, height, QtGui.QImage.Format_ARGB32)
    for x in xrange(width):
        for y in xrange(int(height)):
            argb = lineARGB[x + y * width]
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
