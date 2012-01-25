# -*- coding: utf-8 -*-
"""
Created on Wed Jan 12 15:16:58 2011

@author: Ludovic Autin
"""

from distutils.core import setup

setup(name='upy',
      version='1.0',
      description='uibiquitist UI',
      author='Ludovic Autin',
      author_email='autin@scripps.edu',
      url='https://github.com/corredD/pyubic',
      packages=['upy','upy.blender','upy.autodeskmaya','upy.cinema4d'],
      package_dir={'upy': '.'},
     )
