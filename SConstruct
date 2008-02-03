import SCons
import sys
import os
import string
import wnsrc

def registerPyuicBuilder(env):
    pyuic_build_str =  os.path.join(wnsrc.pathToSandbox, 'default', 'bin', 'pyuic4') + ' $SOURCE  -o $TARGET';
    pyuic_builder = Builder(action = [pyuic_build_str],
                            src_suffix = '.ui',
                            prefix = '',
                            suffix = '_ui.py');
    env.Append(BUILDERS = {'Pyuic' : pyuic_builder});

def CheckPyQt4(context):
    context.Message('Checking for PyQt4...')
    result = False
    for path in sys.path:
	if os.path.exists(os.path.join(path, "PyQt4")):
	    result = True
    context.Result(result)
    return result

env = Environment()

env["ENV"]["PYTHONPATH"] = os.path.join(wnsrc.pathToSandbox, 'default', 'lib', 'python2.4', 'site-packages') + os.pathsep + os.environ["PYTHONPATH"]

conf = Configure(env, custom_tests = {'CheckPyQt4' : CheckPyQt4}, conf_dir = ".sconf_temp", log_file = ".sconf.log")

if not conf.CheckPyQt4():
    print "Not building Wrowser because PyQt4 is not installed!"
    Exit(0) # we do not want to abort building the testbed

registerPyuicBuilder(env)

pyuic_src_files = ['ui/Windows_Main.ui',
                   'ui/Dialogues_ColumnSelect.ui',
                   'ui/Dialogues_ConfigureGraph.ui',
                   'ui/Dialogues_OpenDatabase.ui',
                   'ui/Dialogues_OpenCampaignDb.ui',
                   'ui/Dialogues_OpenDSV.ui',
                   'ui/Windows_SimulationParameters.ui',
                   'ui/Windows_DirectoryNavigation.ui',
                   'ui/Windows_Figure.ui',
                   'ui/Windows_ProbeInfo.ui',
                   'ui/Widgets_Graph.ui',
                   'ui/Widgets_TableGraph.ui',
                   'ui/Widgets_ProbeGraphControl.ui',
                   'ui/Widgets_ParameterGraphControl.ui']

for srcfile in pyuic_src_files:
    env.Pyuic(srcfile)

env.Alias("install-python", ".")
env.Default("install-python")
env.Alias("docu", [])
env.Alias("install-docu", [])
