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

import getpass
import pwd
import os
import sys

def searchPath(path, file):
    while file not in os.listdir(path):
        if path == os.sep:
            return None
        path, tail = os.path.split(path)
    return os.path.abspath(path)

searchPath = searchPath(os.getcwd(), 'openwns')

if searchPath is not None:
    print "Local installation of wrowser found."
    print "Prepending %s to sys.path" % searchPath
    sys.path.insert(0, searchPath)

import openwns.wrowser.simdb.Database as db

hostname = 'localhost'
dbName = 'simdb'
password = 'foobar'

userName = getpass.getuser()
if(userName == 'root' or userName == 'postgres'):
	print "ERROR!"
	print "You have tried to call the script ./createUser.py as user %s" % (userName)
	print "* It is strongly recommended that you call the script using the user account"
	print "  with which you plan to do the simulations, i.e., your usual working account."
	print "* It is NOT recommended to call the script as root or as user postgres - or "
	print "  that you do simulations using one of them."
	print "Please login with your usual working account and repeat the procedure!"
	sys.exit()

postgresPassword = getpass.getpass('Please enter the password of the \'postgres\' super user: ')
db.Database.connect(dbName, hostname, 'postgres', postgresPassword)

curs = db.Database.getCursor()
curs.execute('SELECT * FROM administration.users WHERE user_name = \'%s\'' % userName)
if len(curs.fetchall()) != 0:
        print >>sys.stderr, 'User with user name \'%s\' already exists.' % userName
        sys.exit(1)

curs.execute('INSERT INTO administration.users (user_name, full_name, password, group_account) VALUES (\'%s\', \'%s\', \'%s\', \'%s\')' % (userName, pwd.getpwnam(userName)[4], password, False))
curs.connection.commit()

# configuration file is written by the wrowser!
#conf = config.Configuration()
#conf.dbHost = hostname
#conf.dbName = dbName
#conf.userName = userName
#conf.userPassword = password
#conf.writeDbAccessConf(home = os.path.join('/', 'home', userName), user = userName)

print 'User successfully created.'
