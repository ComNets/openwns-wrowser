#! /usr/bin/python

import getpass
import pwd
import os
import sys

import simdb.Configuration as config
import simdb.Database as db

hostname = 'postgres'
dbName = 'simdbtest'

postgresPassword = getpass.getpass('Please enter the password of the \'postgres\' super user: ')
db.Database.connect(dbName, hostname, 'postgres', postgresPassword)

userName = getpass.getuser()
curs = db.Database.getCursor()
curs.execute('SELECT * FROM administration.users WHERE user_name = \'%s\'' % userName)
if len(curs.fetchall()) != 0:
        print >>sys.stderr, 'User with user name \'%s\' already exists.' % userName
        sys.exit(1)

fullName = pwd.getpwnam(userName)[4]
password = 'foobar'
curs.execute('INSERT INTO administration.users (user_name, full_name, password, group_account) VALUES (\'%s\', \'%s\', \'%s\', \'%s\')' % (userName, fullName, password, False))
curs.connection.commit()

conf = config.Configuration()
conf.dbHost = hostname
conf.dbName = dbName
conf.userName = userName
conf.userPassword = password
conf.writeDbAccessConf(home = os.path.join('/', 'home', userName), user = userName)

print 'User successfully created.'
