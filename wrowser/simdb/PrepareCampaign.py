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

import os
import shutil

import Database as db
import wrowser.Configuration as conf

__config = conf.Configuration()
__config.read()
db.Database.connectConf(__config)


def __getDirectoryProposal(directory):
    files = os.listdir(directory)
    filteredFiles = [f[11:] for f in files if f.startswith('simulations')]
    ids = []
#    print filteredFiles
    for f in filteredFiles:
        print f
        if f == '':
            f = 1
        try:
            print ids
            ids.append(int(f))
        except ValueError:
            pass
#    print ids
    proposedDirectory = 'simulations'
    if len(ids) > 0:
        proposedDirectory += str(max(ids)+1)
    return proposedDirectory


def createNewSubCampaign(directory):
    proposedDirectory = __getDirectoryProposal(directory)
    while True:
        subCampaign = raw_input('Please enter the name of the directory the simulations shall be stored in [%s]: ' % proposedDirectory)
        if subCampaign == '':
            subCampaign = proposedDirectory

        subCampaignDir = os.path.join(directory, subCampaign)
#        print subCampaignDir

        if os.path.exists(subCampaignDir):
            print 'Path already exists. Please use a different name'
        else:
            break

    os.mkdir(subCampaignDir)
    shutil.copy(os.path.join('sandbox', 'default', 'lib', 'python2.4', 'site-packages', 'pywns', 'simdb', 'scripts', 'simcontrol.py'), subCampaignDir)
    shutil.copy(os.path.join('sandbox', 'default', 'lib', 'python2.4', 'site-packages', 'pywns', 'simdb', 'scripts', 'campaignConfiguration.py'), subCampaignDir)

    campaignTitle = raw_input('Please enter a name for the campaign: ')
    campaignDescription = raw_input('Please enter a short description of the campaign: ')
    cursor = db.Database.getCursor()
    cursor.execute('INSERT INTO campaigns (title, description) VALUES (\'%s\', \'%s\')' % (campaignTitle, campaignDescription))
    cursor.execute('SELECT currval(\'administration.campaigns_id_seq\')')
    campaignConfig = conf.Configuration()
    campaignConfig.campaignId = cursor.fetchone()[0]
    campaignConfig.writeCampaignConf(os.path.join(subCampaignDir, '.campaign.conf'))
    cursor.connection.commit()


def updateSubCampaigns(directory):
    dirs = [f for f in os.listdir(directory) if os.path.isdir(f)]
    for d in dirs:
        path = os.path.join(directory, d, 'simcontrol.py')
        if os.path.exists(path):
            shutil.copy(os.path.join('sandbox', 'default', 'lib', 'python2.4', 'site-packages', 'pywns', 'simdb', 'scripts', 'simcontrol.py'),
                        os.path.join(path))
