# -*- coding: utf-8 -*-
"""
Created on Wed Jan 12 15:16:58 2011

@author: Ludovic Autin
"""

from distutils.core import setup

import sys

packages=['upy',  'upy.blender', 'upy.dejavuTk',
          'pythonUI']

# Check for Python2
if sys.version_info[0] == 2:
    packages.extend(['upy.autodeskmaya', 'upy.blender.v249','upy.cinema4d', 'houdini'])
elif sys.version_info[0] == 3:
    packages.extend(['upy.blender.v257', 'upy.blender.v262'])

setup(name='upy',
      version='1.0',
      description='uibiquitist UI',
      author='Ludovic Autin',
      author_email='autin@scripps.edu',
      url='https://github.com/corredD/pyubic',
      packages=packages,
      # 'upy.autodeskmaya',],
      package_dir={'upy': '.'},
     )
