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

import datetime
import time

class Delta:

    def __init__(self, timedelta):
        assert(isinstance(timedelta, datetime.timedelta))
        self.timedelta = timedelta

    def __str__(self):
        return str(self.timedelta)

    def __getYears(self):
        return self.timedelta.days / 365

    def __getDays(self):
        return self.timedelta.days % 365

    def __getHours(self):
        return self.timedelta.seconds / 60 / 24

    def __getMinutes(self):
        return self.timedelta.seconds / 60 - self.hours * 60

    def __getSeconds(self):
        return self.timedelta.seconds % 60

    def __getMicroSeconds(self):
        return self.timedelta.milliseconds

    def asString(self):
        s = str(self.seconds) + "s"
        for value, unit in [(self.minutes, "m"),
                            (self.hours, "h"),
                            (self.days, "d"),
                            (self.years, "y")]:
            if value > 0:
                s = str(value) + unit + " " + s
        return s

    years = property(__getYears)
    days = property(__getDays)
    hours = property(__getHours)
    minutes = property(__getMinutes)
    seconds = property(__getSeconds)
    microseconds = property(__getMicroSeconds)
