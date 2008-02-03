from Tools import Observable

class Figure(Observable):
    def __init__(self):
        Observable.__init__(self)
        self.graphs = []
        self.grid = (False, False, False, False)
        self.marker = "."
        self.scale = ("linear", None, "linear", None)
        self.legend = False
        self.title = ""

