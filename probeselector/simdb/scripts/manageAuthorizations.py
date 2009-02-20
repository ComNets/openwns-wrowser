#! /usr/bin/python

import simdb.Configuration as Configuration
import simdb.Database as db
import os
import sys

conf = Configuration.Configuration()
conf.read()
db.Database.connectConf(conf)
cursor = db.Database.getCursor()

while True:
    choice = int(raw_input('1 Show list of users and groups\n' \
                           '2 Show list of own simulation campaigns\n' \
                           '3 Show list of authorizations\n' \
                           '4 Add authorization\n' \
                           '5 Remove authorization\n' \
                           '6 Exit\n'))
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
        print 'Campaign Id   Title               Description'
        cursor.execute('SELECT id, title, description FROM campaigns')
        campaign = cursor.fetchone()
        while campaign is not None:
            print str(campaign[0]).ljust(14) + str(campaign[1]).ljust(20) + str(campaign[2])
            campaign = cursor.fetchone()
        cursor.connection.commit()
    elif choice == 3:
        print 'Campaign Id   Auhorized User/Group'
        cursor.execute('SELECT authorizations.campaign_id, users.user_name FROM authorizations INNER JOIN users ON authorizations.authorized_id = users.id')
        authorization = cursor.fetchone()
        while authorization is not None:
            print str(authorization[0]).ljust(14) + str(authorization[1])
            authorization = cursor.fetchone()
        cursor.connection.commit()
    elif choice == 4:
        authorizedUser = raw_input('Please enter the name of the user/group you want to authorize: ')
        cursor.execute('SELECT * FROM users WHERE user_name = \'%s\'' % authorizedUser)
        if len(cursor.fetchall()) != 1:
            print >>sys.stderr, 'User/group with name \'%s\' does not exist.' % authorizedUser
            cursor.connection.commit()
            continue
        campaignId = int(raw_input('Please enter the id of the campaign for that you want to grant access: '))
        cursor.execute('SELECT * FROM campaigns WHERE id = %d' % campaignId)
        if len(cursor.fetchall()) != 1:
            print >>sys.stderr, 'Campaign with id \'%d\' does not exist.' % campaignId
            cursor.connection.commit()
            continue
        cursor.execute('SELECT id FROM users WHERE user_name = \'%s\'' % authorizedUser)
        authorizedUserId = cursor.fetchone()[0]
        cursor.execute('SELECT id FROM users WHERE user_name = \'%s\'' % conf.userName)
        userId = cursor.fetchone()[0]
        cursor.execute('SELECT * FROM authorizations WHERE user_id = %d AND campaign_id = %d AND authorized_id = %d' % (userId, campaignId, authorizedUserId));
        if len(cursor.fetchall()) != 0:
            print >>sys.stderr, 'User/group \'%s\' is already authorized to access the campaign with id \'%d\'' % (authorizedUser, campaignId)
            cursor.connection.commit()
            continue

        cursor.execute('INSERT INTO authorizations (user_id, campaign_id, authorized_id) VALUES (%d, %d, %d)' % (userId, campaignId, authorizedUserId))
        cursor.connection.commit()
        print 'Authorizations successfully granted.'
    elif choice == 5:
        authorizedUser = raw_input('Please enter the name of the user/group whose authorization you want to remove: ')
        cursor.execute('SELECT * FROM users WHERE user_name = \'%s\'' % authorizedUser)
        if len(cursor.fetchall()) != 1:
            print >>sys.stderr, 'User/group with name \'%s\' does not exist.' % authorizedUser
            cursor.connection.commit()
            continue
        campaignId = int(raw_input('Please enter the id of the campaign for that you want to revoke access: '))
        cursor.execute('SELECT * FROM campaigns WHERE id = %d' % campaignId)
        if len(cursor.fetchall()) != 1:
            print >>sys.stderr, 'Campaign with id \'%d\' does not exist.' % campaignId
            cursor.connection.commit()
            continue
        cursor.execute('SELECT id FROM users WHERE user_name = \'%s\'' % authorizedUser)
        authorizedUserId = cursor.fetchone()[0]
        cursor.execute('SELECT id FROM users WHERE user_name = \'%s\'' % conf.userName)
        userId = cursor.fetchone()[0]
        cursor.execute('SELECT * FROM authorizations WHERE user_id = %d AND campaign_id = %d AND authorized_id = %d' % (userId, campaignId, authorizedUserId));
        if len(cursor.fetchall()) != 1:
            print >>sys.stderr, 'User/group \'%s\' was not authorized to access the campaign with id \'%d\'' % (authorizedUser, campaignId)
            cursor.connection.commit()
            continue

        cursor.execute('DELETE FROM authorizations WHERE user_id = %d AND campaign_id = %d AND authorized_id = %d' % (userId, campaignId, authorizedUserId))
        cursor.connection.commit()
        print 'Authorizations successfully revoked.'
    elif choice == 6:
        cursor.connection.close()
        sys.exit(0)
    print '--------------------------------------'
