#! /usr/bin/python
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

from wrowser.simdb.Parameters import Parameters, Bool, Int, Float, String

###################################
# Simple parameter generation HowTo
#
# First, you need to define your simulation parameters in a class derived from Parameters, e.g.
#
class Set(Parameters):
    example = Int()
#
# Then, an instance of Set needs to be created
#

params = Set()

#
# now the Parameters in params get populated with different values. Each time "write" is called the current values fixed.
#

for i in xrange(5):
    params.example = 10**(i)
    params.write()

#
# in your config.py, you need
#

from openwns.wrowser.simdb.SimConfig import params

#
# and then configure using the params instance
#

MyExample.examples = params.example

# That's it
####################################
