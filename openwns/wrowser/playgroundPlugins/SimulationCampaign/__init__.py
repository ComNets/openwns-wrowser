import os
import shutil
import datetime

import sys

import PrepareCampaign

from wnsbase.playground.builtins.Install.Install import InstallCommand

import wnsbase.playground.Core
core = wnsbase.playground.Core.getCore()

class PrepareCampaignCommand(wnsbase.playground.plugins.Command.Command):

    def __getDirectoryProposal(self, directory):
        files = os.listdir(directory)
        filteredFiles = [f[11:] for f in files if f.startswith('simulations')]
        ids = []
        # print filteredFiles
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

    def __init__(self):
        usage = "\n%prog preparecampaign PATH\n\n"
        rationale = "Prepare a simulation campaign."

        usage += rationale

        usage += """

            A directory 'directory' and the sub-directories 'sandbox' as well
            as 'simulations' will be created. 'sandbox' will contain all
            necessary libraries and the openwns. After installation the
            directory will be changed to read-only mode in order to prevent
            accidently removing the directory or altering its content. The
            simulations directory is empty. Directories for different
            simulations should be placed here.
"""
        wnsbase.playground.plugins.Command.Command.__init__(self, "preparecampaign", rationale, usage)

        self.optParser.add_option("-u", "--updateSandbox",
                                  dest = "updateSandbox", default = False, action = "store_true",
                                  help = "Update the sandbox of an existing campaign")

        self.optParser.add_option("-c", "--createSubCampaign",
                                  type = "string", dest = "createSubCampaign", metavar = "NAME",
                                  help = "Create a new sub-campaign in an existing campaign")

        self.optParser.add_option("-f", "--configFile",
                                  type="string", dest = "configFile", metavar = "FILE", default = "config/projects.py",
                                  help = "choose a configuration file (e.g., --configFile=config/projects.py)")

        self.optParser.add_option("", "--addProfOpt",
                                  dest = "addProfOpt", default = False,
                                  action = "store_true",
                                  help = "additionally build and install (static) version for profiling")

        self.optParser.add_option("", "--static",
                                  dest = "static", default = False,
                                  action = "store_true",
                                  help = "build static executable")

        self.optParser.add_option("", "--arch32",
                                  dest = "arch32", default = False,
                                  action = "store_true",
                                  help = "build 32bit executable")

        self.optParser.add_option("", "--noTouch",
                                  dest = "noTouch", default = False,
                                  action = "store_true",
                                  help = "Do not touch existing sim.py/simcontrol.py, only useful for creating a new sub-campaign")

        self.numberOfArgs = 1


    def run(self):
        """ Prepare a directory with a dbg and an opt version.

        A directory 'directory' and the sub-directories 'sandbox' as well
        as 'simulations' will be created. 'sandbox' will contain all
        necessary libraries and the openwns. After installation the
        directory will be changed to read-only mode in order to prevent
        accidently removing the directory or altering its content. The
        simulations directory is empty. Directories for different
        simulations should be placed here.
        """

        if self.options.updateSandbox and self.options.createSubCampaign is not None:
            print "ERROR! The options updateSandbox and createSubCampaign are mutually exclusive. Please use one after the other\n"
            return

        print "Preparing simulation campaign. Please wait..."

        # copy simcontrol.py and sim.py to $OPENWNSROOT/bin
        absPathToOpenWNS = os.path.abspath(core.getPathToSDK())

        thisPluginPath = os.path.dirname(__file__)
        shutil.copy(os.path.join(thisPluginPath, 'simcontrol.py'), os.path.join(absPathToOpenWNS,'bin'))
        shutil.copy(os.path.join(thisPluginPath, 'sim.py'), os.path.join(absPathToOpenWNS, 'bin'))
        os.system("chmod u+x " + os.path.join(absPathToOpenWNS, 'bin', 'sim.py'))

        directory = "".join(self.args)
        # Import playground stuff
        ###projects = core.getProjects()

        absSandboxDir = os.path.abspath(os.path.join(directory, "sandbox"))
        campaignName = os.path.basename(os.path.abspath(directory))
        logFile = os.path.join(directory, campaignName + ".history")

        updating = False

        if (self.options.updateSandbox or self.options.createSubCampaign is not None) and (not os.path.exists(directory)) and (not os.path.exists(logFile)):
            print "ERROR! The directory %s either does not exist or it is not a openWNS campaign directory " % directory
            print "Updating / creation of a new subcampaign is not possible."
            return

        if os.path.exists(directory):
            if os.path.exists(logFile):
                print "Found simulation campaign in directory %s." % directory
                if self.options.updateSandbox:
                    answer = "u"
                elif self.options.createSubCampaign is not None:
                    answer = "c"
                else:
                    answer = raw_input("Shall I try to (U)pdate the sandbox or do you want to (C)reate a new sub campaign? Type \'e\' to exit (u/c/e) [e]: ")
                    answer = answer.lower()

                if answer == "u":
                    if os.path.exists(absSandboxDir):
                        os.system("chmod -R u+w " + absSandboxDir)
                        os.system("rm -rf " + absSandboxDir)
                    if os.path.exists(logFile):
                        os.system("chmod u+w " + logFile)
                    logFileHandle = file(logFile, 'a')
                    updating = True
                elif answer == "c":
                    if self.options.createSubCampaign != "":
                        PrepareCampaign.createNewSubCampaign(directory, self.options.createSubCampaign)
                    else:
                        PrepareCampaign.createNewSubCampaign(directory)
                    sys.exit(0)
                else:
                    sys.exit(0)
            else:
                print "Directory %s already exists and does not seem to be a simulation campaign directory." % directory
                print "Please remove the directory or use a different name and try again."
                sys.exit(0)
        else:
            os.makedirs(directory)
            logFileHandle = file(logFile, 'w')
            logFileHandle.write("Do NOT remove this file!\n\n")
            shutil.copy('.thisIsTheRootOfWNS', directory)

        logFileHandle.write("---START---" + datetime.datetime.today().strftime('%d.%m.%y %H:%M:%S') + "---\n\n")
        logFileHandle.write("Setting up simulation campaign directory...\n\n")

        if not updating:
            PrepareCampaign.createNewSubCampaign(directory)

        if not os.path.exists(absSandboxDir):
            os.makedirs(absSandboxDir)

        self.installWNS(absSandboxDir)

        if (not self.options.noTouch):
            PrepareCampaign.updateSubCampaigns(directory)
            shutil.copy(os.path.join(os.path.dirname(__file__),"sim.py"), directory)
            os.system("chmod u+x " + os.path.join(directory, "sim.py"))

        logFileHandle.write("Simulation campaign directory successfully set up.\n\n")
        logFileHandle.write("---END---" + datetime.datetime.today().strftime('%d.%m.%y %H:%M:%S') + "---\n")
        logFileHandle.close()

        # make read only
        os.system("chmod -R u-w,g-w,o-w " + absSandboxDir)
        os.system("chmod u-w,g-w,o-w " + logFile)


    def installWNS(self, absSandboxDir):
        commonArgs = ["--sandboxDir="+absSandboxDir, '--scons="preparingcampaign=1"']
        installCommand = InstallCommand()

        arch32String = " "
        if self.options.arch32:
            arch32String = " --arch32 "
            commonArgs.append(arch32String)

        # install fresh version
        print "running ./playground.py install --flavour=dbg" + arch32String + "-f " + self.options.configFile
        installCommand.startup(commonArgs + ["--flavour=dbg"])

        installCommand.run()

        staticString = " "
        if self.options.static:
            staticString = " --static "

        print "running ./playground.py install --flavour=opt" + staticString + arch32String + "-f " + self.options.configFile
        installCommand.startup(commonArgs + ["--flavour=opt"])

        installCommand.options.static = self.options.static
        installCommand.run()

        if self.options.addProfOpt:
            print "running ./playground.py install --flavour=profOpt" + staticString + arch32String + "-f " + self.options.configFile
            installCommand.startup(commonArgs + ["--flavour=profOpt"])
            installCommand.options.static = self.options.static
            installCommand.run()


if not core.hasPlugin("SimulationCampaign"):
    core.registerPlugin("SimulationCampaign")

    prepareCommand = PrepareCampaignCommand()

    core.registerCommand(prepareCommand)

