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
import sys
import pwd
import ConfigParser

class MissingConfigurationFile(Exception):

    def __init__(self, filename):
        self.filename = filename

    def __str__(self):
        return "Cannot open configuration file: " + self.filename


class WrongFilePermissions(Exception):

    def __init__(self, filename):
        self.filename = filename

    def __str__(self):
        msg = "Wrong file access permissions to \'%s\'. Due to security reasons only the owner of the file must have read/write access. Consider changing the database password if unauthorized people might have become aware of it." % self.filename
        return msg

class MissingConfigurationEntry(Exception):

    def __init__(self, filename, entry):
        self.entry = entry
        self.filename = filename

    def __str__(self):
        return "Entry %s is missing in config" % (self.entry, )

class MissingConfigurationSection(Exception):

    def __init__(self, filename,section):
        self.section = section
        self.filename = filename

    def __str__(self):
        return "Section %s is missing in config" % (self.section, )

class BadConfigurationFile(Exception):

    def __init__(self, filename):
        self.filename = filename

    def __str__(self):
        return "The configuration file %s cannot be read." % (self.filename, )

class SandboxConfiguration(object):
  
    def __init__(self):
        self.parser = ConfigParser.SafeConfigParser()
        self.confFile = os.path.join(os.environ['HOME'], '.wns', 'sandbox.conf')
        
    def read(self):

        try:
            self.parser.read([self.confFile])
        except ConfigParser.MissingSectionHeaderError, e:
            raise BadConfigurationFile(self.confFile)        
        
        if 'Sandbox' in self.parser.sections():
            if 'path' in self.parser.options('Sandbox'):
                setattr(self, 'sandboxPath', str(self.parser.get('Sandbox', 'path')))
            else:
                raise MissingConfigurationEntry(self.confFile, "Sandbox.path")
            if 'flavour' in self.parser.options('Sandbox'):
                setattr(self, 'sandboxFlavour', str(self.parser.get('Sandbox', 'flavour')))
            else:
                raise MissingConfigurationEntry(self.confFile, "Sandbox.flavour")
        else:
            raise MissingConfigurationSection(self.confFile, "Sandbox")

    def writeSandboxConf(self, owner):        
        if 'Sandbox' not in self.parser.sections():
            self.parser.add_section('Sandbox')

        self.parser.set('Sandbox', 'path', getattr(self, 'sandboxPath'))
        self.parser.set('Sandbox', 'flavour', getattr(self, 'sandboxFlavour'))

        config = file(self.confFile, 'w')
        self.parser.write(config)
        config.close()
        os.chown(self.confFile, pwd.getpwnam(owner)[2], pwd.getpwnam(owner)[3])
        os.chmod(self.confFile, 0644)



class Configuration(object):

    def __init__(self):
        self.parser = ConfigParser.SafeConfigParser()
        self.dbAccessConfFile = os.path.join(os.environ['HOME'], '.wns', 'dbAccess.conf')

    def read(self, filename = ''):

        try:
            self.parser.read([self.dbAccessConfFile, filename])
        except ConfigParser.MissingSectionHeaderError, e:
            raise BadConfigurationFile(filename)

        if 'DB' in self.parser.sections():
            if 'host' in self.parser.options('DB'):
                setattr(self, 'dbHost', self.parser.get('DB', 'host'))
            else:
                raise MissingConfigurationEntry(filename, "DB.host")

            if 'name' in self.parser.options('DB'):
                setattr(self, 'dbName', self.parser.get('DB', 'name'))
            else:
                raise MissingConfigurationEntry(filename, "DB.name")
        else:
            raise MissingConfigurationSection(filename, "DB")

        if 'User' in self.parser.sections():
            if 'name' in self.parser.options('User'):
                setattr(self, 'userName', self.parser.get('User', 'name'))
            else:
                raise MissingConfigurationEntry(filename, "User.name")

            if 'password' in self.parser.options('User'):
                setattr(self, 'userPassword', self.parser.get('User', 'password'))
            else:
                raise MissingConfigurationEntry(filename, "User.password")
        else:
            raise MissingConfigurationSection(filename, "User")

        if 'Campaign' in self.parser.sections():
            if 'id' in self.parser.options('Campaign'):
                setattr(self, 'campaignId', int(self.parser.get('Campaign', 'id')))
            else:
                raise MissingConfigurationEntry(filename, "Campaign.id")

    def writeDbAccessConf(self, filename, owner):
        dbAccessConfFile = filename
        if 'DB' not in self.parser.sections():
            self.parser.add_section('DB')

        self.parser.set('DB', 'host', getattr(self, 'dbHost'))
        self.parser.set('DB', 'name', getattr(self, 'dbName'))

        if 'User' not in self.parser.sections():
            self.parser.add_section('User')

        self.parser.set('User', 'name', getattr(self, 'userName'))
        self.parser.set('User', 'password', getattr(self, 'userPassword'))

        wnsDir = os.environ['HOME']+"/.wns"
        if not os.path.exists(wnsDir) :
            os.makedirs(wnsDir)

        config = file(dbAccessConfFile, 'w')
        config.write('# Keep this file private. Do NOT change file access permissions. Security hazard!\n\n')
        self.parser.write(config)
        config.close()
        os.chown(dbAccessConfFile, pwd.getpwnam(owner)[2], pwd.getpwnam(owner)[3])
        os.chmod(dbAccessConfFile, 0600)


    def writeCampaignConf(self, filename):
        if 'Campaign' not in self.parser.sections():
            self.parser.add_section('Campaign')

        self.parser.set('Campaign', 'id', str(getattr(self, 'campaignId')))

        config = file(filename, 'w')
        config.write('# Do NOT edit this file manually!\n\n')
        self.parser.write(config)
        config.close()
        os.chmod(filename, 0644)
