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

import os
import sys

import wrowser.Configuration as Configuration
import wrowser.simdb.Database as db

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
