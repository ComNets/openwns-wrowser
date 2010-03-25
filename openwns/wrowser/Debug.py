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
