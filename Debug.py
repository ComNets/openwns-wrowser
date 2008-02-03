import time
import inspect

class Debug:
    output = True

class printCallCounter:
    ctr = 0

def printCall(instance = None, args = ""):
    if Debug.output:
        print printCallCounter.ctr, time.strftime("%c")
        printCallCounter.ctr += 1
        print "instance: ", instance
        function = inspect.stack()[1][3]
        print "function: ", function
        print "args: ", args
        print ""

def debugCall(argFormatter = lambda x: x,
              kwargFormatter = lambda x: x,
              resultFormatter = lambda x: x):

    def wrapCall(func):

        def callFunc(*args, **kwargs):
            if Debug.output:
                print "Calling " + func.func_name
                print "with args", argFormatter(args)
                print " - kwargs", kwargFormatter(kwargs)
            result = func(*args, **kwargs)
            if Debug.output:
                print "yields", resultFormatter(result)
                print ""
            return result

        return callFunc

    return wrapCall
