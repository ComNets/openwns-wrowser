#! /usr/bin/python

import simdb.Database as db
import getpass
import os
import sys

hostname = 'postgres'
dbName = 'simdbtest'

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
