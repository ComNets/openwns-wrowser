import os
import shutil
import datetime

import sys

from wnsbase.playground.builtins.Install.Install import InstallCommand

import wnsbase.playground.Core
core = wnsbase.playground.Core.getCore()

class PrepareCampaignCommand(wnsbase.playground.plugins.Command.Command):

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

        print "Preparing simulation campaign. Please wait..."

        # copy simcontrol.py and sim.py to $OPENWNSROOT/bin
        absPathToOpenWNS = os.path.abspath(core.getPathToSDK())

        thisPluginPath = os.path.dirname(__file__)
        shutil.copy(os.path.join(thisPluginPath, 'simcontrol.py'), os.path.join(absPathToOpenWNS,'bin'))
        shutil.copy(os.path.join(thisPluginPath, 'sim.py'), os.path.join(absPathToOpenWNS, 'bin'))

        directory = "".join(self.args)
        # Import playground stuff
        projects = core.getProjects()

        versionInformation = ""

        def createVersionInformation(project):
            return project.getRCS().getTreeVersion() + "--" + \
                project.getRCS().getPatchLevel() + "\n" + \
                str(project.getRCS().status())

        versionInformation += str().join(createVersionInformation(projects.root))
        versionInformation += str().join([ii.result for ii in core.foreachProject(createVersionInformation)])

        absSandboxDir = os.path.abspath(os.path.join(directory, "sandbox"))
        campaignName = os.path.basename(os.path.abspath(directory))
        logFile = os.path.join(directory, campaignName + ".history")

        useDbServer = False

        answer = core.userFeedback.askForReject('Do you want to use the database server for storing simulation campaign related data?')

        if not answer:
            answer2 = raw_input( 'NOTICE: The database server is still in alpha stage. Hence, the consistency of the data stored\n'\
                                     'in the database cannot be guarranted. A complete loss of data is also possible.\n'\
                                     'If you are sure you want to continue, please type \'yes\': ')
            if answer2.lower() == 'yes':
                useDbServer = True
            else:
                sys.exit(1)

        # use sqlite
        if useDbServer == False:
            updating = False

            if os.path.exists(directory):
                if os.path.exists(logFile):
                    print "Found simulation campaign in directory %s." % directory
                    answer = core.userFeedback.askForReject("Shall I try to update sandbox and python dir?")
                    if not answer:
                        if os.path.exists(absSandboxDir):
                            os.system("chmod -R u+w " + absSandboxDir)
                            os.system("rm -rf " + absSandboxDir)
                        if os.path.exists(logFile):
                            os.system("chmod u+w " + logFile)
                        logFileHandle = file(logFile, 'a')
                        updating = True
                    else:
                        sys.exit(0)
                else:
                    print "Directory %s already exists and does not seem to be a simulation campaign directory." % directory
                    print "Please remove the directory or use a different name and try again."
                    sys.exit(0)
            else:
                os.mkdir(directory)
                os.mkdir(os.path.join(directory, "simulations"))
                logFileHandle = file(logFile, 'w')
                logFileHandle.write("Do NOT remove this file!\n\n")
                shutil.copy(wnsrc.wnsrc.rootSign, directory)


            logFileHandle.write("---START---" + datetime.datetime.today().strftime('%d.%m.%y %H:%M:%S') + "---\n\n")
            logFileHandle.write("Setting up simulation campaign directory...\n\n")

            self.installWNS(absSandboxDir)

            if not updating:
                shutil.copy(os.path.join(os.path.dirname(__file__), "campaignConfiguration.py"),
                            os.path.join(directory, "simulations", "campaignConfiguration.py"))
            shutil.copy(os.path.join("bin", "simcontrol.py"),
                        os.path.join(directory, "simulations"))
            shutil.copy(os.path.join("bin", "sim.py"),
                        directory)

            logFileHandle.write("Simulation campaign directory successfully set up.\n\n")
            logFileHandle.write("Installed module versions:\n" + versionInformation + "\n")
            logFileHandle.write("---END---" + datetime.datetime.today().strftime('%d.%m.%y %H:%M:%S') + "---\n")
            logFileHandle.close()

            # make read only
            os.system("chmod -R u-w,g-w,o-w " + absSandboxDir)
            os.system("chmod u-w,g-w,o-w " + logFile)

        else:
            # use db server
            import PrepareCampaign

            updating = False

            if os.path.exists(directory):
                if os.path.exists(logFile):
                    print "Found simulation campaign in directory %s." % directory
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

            PrepareCampaign.updateSubCampaigns(directory)
            shutil.copy(os.path.join(os.path.dirname(__file__),"sim.py"), directory)

            logFileHandle.write("Simulation campaign directory successfully set up.\n\n")
            logFileHandle.write("Installed module versions:\n" + versionInformation + "\n")
            logFileHandle.write("---END---" + datetime.datetime.today().strftime('%d.%m.%y %H:%M:%S') + "---\n")
            logFileHandle.close()

            # make read only
            os.system("chmod -R u-w,g-w,o-w " + absSandboxDir)
            os.system("chmod u-w,g-w,o-w " + logFile)


    def installWNS(self, absSandboxDir):
        commonArgs = ["--sandboxDir="+absSandboxDir, '--scons="preparingcampaign=1"']
        installCommand = InstallCommand()
        # install fresh version
        print "running ./playground.py install --flavour=dbg -f " + self.options.configFile
        installCommand.startup(commonArgs + ["--flavour=dbg"])
        installCommand.run()

        staticString = " "
        if self.options.static:
            staticString = " --static "

        print "running ./playground.py install --flavour=opt" + staticString + "-f " + self.options.configFile
        installCommand.startup(commonArgs + ["--flavour=opt"])
        installCommand.options.static = self.options.static
        installCommand.run()

        if self.options.addProfOpt:
            print "running ./playground.py install --flavour=profOpt" + staticString + "-f " + self.options.configFile
            installCommand.startup(commonArgs + ["--flavour=profOpt"])
            installCommand.options.static = self.options.static
            installCommand.run()

if not core.hasPlugin("SimulationCampaign"):
    core.registerPlugin("SimulationCampaign")

    prepareCommand = PrepareCampaignCommand()

    core.registerCommand(prepareCommand)

