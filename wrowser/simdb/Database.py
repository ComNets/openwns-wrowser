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

import psycopg2 as pg
import sys


class Database:
    __connection = None
    __user = None
    __showAllCampaignsSelected = False
    __viewCampaignsSelected = False


    @staticmethod
    def isConnected():
        if Database.__connection == None:
            return False
        return True


    @staticmethod
    def connect(database, host, user, password, debug = False):
        if Database.isConnected():
            return
#            Database.disconnect()

        Database.__connection = pg.connect(database = database,
                                           host = host,
                                           user = user,
                                           password = password)

        Database.__cursor = Database.__connection.cursor()
        Database.__user = user

        if user == 'postgres':
            statement = 'SELECT administrate_db()'
        else:
            statement = 'SELECT set_user_schema()'

        Database.__cursor.execute(statement)
        Database.__cursor.connection.commit()

        if debug:
            print 'Connection to database established.'


    @staticmethod
    def connectConf(conf, debug = False):
        Database.connect(database = conf.dbName,
                         host = conf.dbHost,
                         user = conf.userName,
                         password = conf.userPassword,
                         debug = debug)


    @staticmethod
    def disconnect():
        if not Database.isConnected():
            raise 'Not connected to database'

        Database.__connection.close()
        Database.__connection = None


    @staticmethod
    def getCursor():
        if not Database.isConnected():
            raise 'Not connected to database'

        return Database.__cursor


    @staticmethod
    def showAllCampaigns():
        if Database.__showAllCampaignsSelected:
            Database.showOwnCampaigns()

        Database.__cursor.execute('SELECT %s.show_all_campaigns()' % Database.__user)
        Database.__connection.commit()
        Database.__showAllCampaignsSelected = True


    @staticmethod
    def showOwnCampaigns():
        if not Database.__showAllCampaignsSelected:
            return

        Database.__cursor.execute('SELECT %s.show_own_campaigns()' % Database.__user)
        Database.__connection.commit()
        Database.__showAllCampaignsSelected = False


    @staticmethod
    def viewCampaigns(campaignIdList):
        if Database.__viewCampaignsSelected:
            Database.modifyCampaigns()

        campaignIdStatement = '\'{'
        for campaignId in campaignIdList:
            campaignIdStatement += str(campaignId) + ', '

        campaignIdStatement = campaignIdStatement[:-2] + '}\''

        Database.__cursor.execute('SELECT %s.view_campaigns(%s)' % (Database.__user, campaignIdStatement))
        Database.__connection.commit()
        Database.__viewCampaignsSelected = True


    @staticmethod
    def modifyCampaigns():
        if not Database.__viewCampaignsSelected:
            return

        Database.__cursor.execute('SELECT %s.modify_campaigns()' % Database.__user)
        Database.__connection.commit()
        Database.__viewCampaignsSelected = False


    @staticmethod
    def changePassword(newPassword):
        Database.__cursor.execute('SELECT administration.change_password(\'%s\')' % newPassword)
        Database.__cursor.connection.commit()


    @staticmethod
    def truncateCampaign(campaignId):
        cursor = Database.getCursor()
        cursor.execute('SELECT truncate_pdf_histograms(%d)' % campaignId)
        cursor.connection.commit()
        cursor.execute('SELECT truncate_pd_fs(%d)' % campaignId)
        cursor.connection.commit()
        cursor.execute('SELECT truncate_log_eval_entries(%d)' % campaignId)
        cursor.connection.commit()
        cursor.execute('SELECT truncate_log_evals(%d)' % campaignId)
        cursor.connection.commit()
        cursor.execute('SELECT truncate_moments(%d)' % campaignId)
        cursor.connection.commit()
        cursor.execute('SELECT truncate_batch_means_histograms(%d)' % campaignId)
        cursor.connection.commit()
        cursor.execute('SELECT truncate_batch_means(%d)' % campaignId)
        cursor.connection.commit()
        cursor.execute('SELECT truncate_lre_histograms(%d)' % campaignId)
        cursor.connection.commit()
        cursor.execute('SELECT truncate_lres(%d)' % campaignId)
        cursor.connection.commit()
        cursor.execute('SELECT truncate_dlre_histograms(%d)' % campaignId)
        cursor.connection.commit()
        cursor.execute('SELECT truncate_dlres(%d)' % campaignId)
        cursor.connection.commit()
        cursor.execute('SELECT truncate_table_rows(%d)' % campaignId)
        cursor.connection.commit()
        cursor.execute('SELECT truncate_tables(%d)' % campaignId)
        cursor.connection.commit()
        cursor.execute('SELECT truncate_other_tables(%d)' % campaignId)
        cursor.connection.commit()


    @staticmethod
    def deleteCampaign(campaignId):
        Database.truncateCampaign(campaignId)
        cursor = Database.getCursor()
        cursor.execute('DELETE FROM campaigns WHERE id = %i' % campaignId)
        cursor.connection.commit()
