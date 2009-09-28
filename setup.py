#!/usr/bin/env python

from distutils.core import setup
import subprocess

print "Creating wrowser.ui files"
p = subprocess.call(["scons", "-s"])

setup(name='openWNS-Wrowser',
      version='0.9beta2',
      description='openWNS Wireless Network Simulator Result Browser',
      author='Department of Communication Networks (ComNets), RWTH Aachen University, Germany',
      author_email='info@openwns.org',
      url='http://www.openwns.org',
      packages=['wrowser',
                'wrowser.ui',
                'wrowser.simdb',
                'wrowser.simdb.scripts',
                'wrowser.probeselector',
                'wrowser.probeselector.dataacquisition',
                'wrowser.scenario'],
      scripts=['bin/wrowser'],
     )

