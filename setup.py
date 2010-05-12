#!/usr/bin/env python

from distutils.core import setup
import subprocess

print "Creating wrowser.ui files"
p = subprocess.call(["scons", "-s"])

setup(name='openWNS-Wrowser',
      version='0.9beta2',
      description='openWNS Wireless Network Simulator Result Browser',
      author='ComNets Research Group, RWTH Aachen University, Germany',
      author_email='info@openwns.org',
      url='http://www.openwns.org',
      packages=['openwns.wrowser',
                'openwns.wrowser.ui',
                'openwns.wrowser.simdb',
                'openwns.wrowser.simdb.scripts',
                'openwns.wrowser.probeselector',
                'openwns.wrowser.probeselector.dataacquisition',
                'openwns.wrowser.scenario'],
      scripts=['bin/wrowser'],
      data_files=[("exportTemplates",["readDBandPlot", "plotAll.py"])]
     )

#package_data = {"openwns.wrowser.probeselector" : [      
