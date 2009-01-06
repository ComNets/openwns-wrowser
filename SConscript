Import('env')
import os
def registerPyuicBuilder(env, pyuic):
    pyuic_build_str =  pyuic + ' $SOURCE  -o $TARGET';
    pyuic_builder = Builder(action = [pyuic_build_str],
                            src_suffix = '.ui',
                            prefix = '',
                            suffix = '_ui.py');
    env.Append(BUILDERS = {'Pyuic' : pyuic_builder});

def CheckPyQt4(context):
    context.Message('Checking for PyQt4...')
    result = False
    try:
        from PyQt4 import QtGui
        result = True
    except:
        pass
    context.Result(result)
    return result

wrowserEnv = env.Clone()
wrowserEnv["ENV"]["PATH"] = os.environ["PATH"]

pyuic = 'pyuic4'

try:
    import wnsrc
    pyuic = 'pyuic4'
    wrowserEnv["ENV"]["PYTHONPATH"] = os.path.join(wnsrc.pathToSandbox, 'default', 'lib', 'python2.4', 'site-packages') + os.pathsep + os.environ["PYTHONPATH"]
except:
    pass


conf = Configure(wrowserEnv, custom_tests = {'CheckPyQt4' : CheckPyQt4}, conf_dir = ".sconf_temp", log_file = ".sconf.log")

if not conf.CheckPyQt4():
    print "Warning: Cannot find PyQt4. This means you may not be able to start the Wrowser!"

wrowserEnv = conf.Finish()

registerPyuicBuilder(wrowserEnv, pyuic)

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
                   'ui/Widgets_ParameterGraphControl.ui',
		   'ui/Widgets_ViewScenario.ui']

for srcfile in pyuic_src_files:
    wrowserEnv.Pyuic(srcfile)

wrowserEnv.Default(Dir('.'))