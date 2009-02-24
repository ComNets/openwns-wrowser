#! /usr/bin/python

import wrowser.Configuration as Configuration
import simdb.Database as db
import os
import sys

conf = Configuration.Configuration()
conf.read()
db.Database.connectConf(conf)
cursor = db.Database.getCursor()

while True:
    choice = int(raw_input('1 Show list of own simulation campaigns\n' \
                           '2 Delete simulation campaign from database\n' \
                           '3 Exit\n'))
    print '--------------------------------------'
    if choice == 1:
        print 'Campaign Id   Title               Description'
        cursor.execute('SELECT id, title, description FROM campaigns')
        campaign = cursor.fetchone()
        while campaign is not None:
            print str(campaign[0]).ljust(14) + str(campaign[1]).ljust(20) + str(campaign[2])
            campaign = cursor.fetchone()
        cursor.connection.commit()
    elif choice == 2:
        campaignId = int(raw_input('Please enter the id of the campaign you want to delete: '))
        cursor.execute('SELECT * FROM campaigns WHERE id = %i' % campaignId)
        if len(cursor.fetchall()) != 1:
            print >>sys.stderr, 'Campaign with id \'%d\' does not exist.' % campaignId
            cursor.connection.commit()
            continue
        print 'Deleting campaign. Please wait...'
        db.Database.deleteCampaign(campaignId)
        print 'Campaign successfully deleted from database.'
        print 'NOTE: This script does not delete any files from simulation \n' \
              '      campaigns. Hence, if you do not need the files from \n' \
              '      campaign %i anymore please remove them manually!' % campaignId
    else:
        cursor.connection.close()
        sys.exit(0)
    print '--------------------------------------'
