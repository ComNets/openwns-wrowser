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

        if 'Sandbox' in self.parser.sections():
            if 'path' in self.parser.options('Sandbox'):
                setattr(self, 'sandboxPath', str(self.parser.get('Sandbox', 'path')))
            else:
                raise MissingConfigurationEntry(filename, "Sandbox.path")
            if 'flavour' in self.parser.options('Sandbox'):
                setattr(self, 'sandboxFlavour', str(self.parser.get('Sandbox', 'flavour')))
            else:
                raise MissingConfigurationEntry(filename, "Sandbox.flavour")
        else:
            raise MissingConfigurationSection(filename, "Sandbox")

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

        if 'Sandbox' not in self.parser.sections():
            self.parser.add_section('Sandbox')

        self.parser.set('Sandbox', 'path', getattr(self, 'sandboxPath'))
        self.parser.set('Sandbox', 'flavour', getattr(self, 'sandboxFlavour'))

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
