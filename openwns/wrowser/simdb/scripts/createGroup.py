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

#! /usr/bin/python

import simdb.Database as db
import getpass
import os
import sys

hostname = 'localhost'
dbName = 'simdb'

postgresPassword = getpass.getpass('Please enter the password of the \'postgres\' super user: ')
db.Database.connect(dbName, hostname, 'postgres', postgresPassword)

groupName = raw_input('Please enter the group name of the new group: ')

curs = db.Database.getCursor()
curs.execute('SELECT * FROM administration.users WHERE user_name = \'%s\'' % groupName)
if len(curs.fetchall()) != 0:
        print >>sys.stderr, 'Group with group name \'%s\' already exists.' % groupName
        sys.exit(1)

groupDescription = raw_input('Please enter a short description of the new group: ')

curs.execute('INSERT INTO administration.users (user_name, full_name, password, group_account) VALUES (\'%s\', \'%s\', \'None\', TRUE)' % (groupName, groupDescription))
curs.connection.commit()

print 'Group successfully created.'
