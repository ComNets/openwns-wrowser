#! /usr/bin/env python

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

#! /usr/bin/env python

import getpass
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

postgresPassword = getpass.getpass('Please enter the password of the \'postgres\' super user: ')
db.Database.connect(dbName, hostname, 'postgres', postgresPassword)
cursor = db.Database.getCursor()

while True:
    choice = int(raw_input('1 Show list of users and groups\n' \
                           '2 Show list of groups and their members\n' \
                           '3 Add user to group\n' \
                           '4 Remove user from group\n' \
                           '5 Exit\n'))
    print '--------------------------------------'
    if choice == 1:
        print 'User    Full Name           Group'
        cursor.execute('SELECT user_name, full_name, group_account FROM users')
        user = cursor.fetchone()
        while user is not None:
            if user[2] is True:
                group = 'Yes'
            else:
                group = 'No'
            print str(user[0]).ljust(8) + str(user[1]).ljust(20) + str(group).center(5)
            user = cursor.fetchone()
        cursor.connection.commit()
    elif choice == 2:
        print 'Group     Member'
        cursor.execute('SELECT group_id, user_id FROM group_members')
        members = cursor.fetchall()
        for member in members:
            cursor.execute('SELECT user_name FROM users WHERE id = %d' % member[0])
            groupName = cursor.fetchone()[0]
            cursor.execute('SELECT user_name FROM users WHERE id = %d' % member[1])
            memberName = cursor.fetchone()[0]
            print str(groupName).ljust(10) + str(memberName).ljust(10)
        cursor.connection.commit()
    elif choice == 3:
        userName = raw_input('Please enter the name of the user you want to add to a group: ')
        cursor.execute('SELECT * FROM users WHERE user_name = \'%s\'' % userName)
        if len(cursor.fetchall()) != 1:
            print >>sys.stderr, 'User with name \'%s\' does not exist.' % userName
            cursor.connection.commit()
            continue
        groupName = raw_input('Please enter the name of the group you want to add the user to: ')
        cursor.execute('SELECT * FROM users WHERE user_name = \'%s\'' % groupName)
        if len(cursor.fetchall()) != 1:
            print >>sys.stderr, 'Group with name \'%s\' does not exist.' % groupName
            cursor.connection.commit()
            continue
        cursor.execute('SELECT id FROM users WHERE user_name = \'%s\'' % userName)
        userId = cursor.fetchone()[0]
        cursor.execute('SELECT id FROM users WHERE user_name = \'%s\'' % groupName)
        groupId = cursor.fetchone()[0]
        cursor.execute('SELECT * FROM group_members WHERE user_id = %d AND group_id = %d' % (userId, groupId));
        if len(cursor.fetchall()) != 0:
            print >>sys.stderr, 'User \'%s\' is already added to group \'%s\'' % (userName, groupName)
            cursor.connection.commit()
            continue
        cursor.execute('INSERT INTO group_members (user_id, group_id) VALUES (%d, %d)' % (userId, groupId))
        cursor.connection.commit()
        print 'User successfully added to group.'
    elif choice == 4:
        userName = raw_input('Please enter the name of the user you want to remove from a group: ')
        cursor.execute('SELECT * FROM users WHERE user_name = \'%s\'' % userName)
        if len(cursor.fetchall()) != 1:
            print >>sys.stderr, 'User with name \'%s\' does not exist.' % userName
            cursor.connection.commit()
            continue
        groupName = raw_input('Please enter the name of the group you want to remove the user from: ')
        cursor.execute('SELECT * FROM users WHERE user_name = \'%s\'' % groupName)
        if len(cursor.fetchall()) != 1:
            print >>sys.stderr, 'Group with name \'%s\' does not exist.' % groupName
            cursor.connection.commit()
            continue
        cursor.execute('SELECT id FROM users WHERE user_name = \'%s\'' % userName)
        userId = cursor.fetchone()[0]
        cursor.execute('SELECT id FROM users WHERE user_name = \'%s\'' % groupName)
        groupId = cursor.fetchone()[0]
        cursor.execute('SELECT * FROM group_members WHERE user_id = %d AND group_id = %d' % (userId, groupId));
        if len(cursor.fetchall()) != 1:
            print >>sys.stderr, 'User \'%s\' is not a member of group \'%s\'' % (userName, groupName)
            cursor.connection.commit()
            continue
        cursor.execute('DELETE FROM group_members WHERE user_id = %d AND group_id = %d' % (userId, groupId))
        cursor.connection.commit()
        print 'User successfully removed from group.'
    elif choice == 5:
        cursor.connection.close()
        sys.exit(0)
    print '--------------------------------------'
