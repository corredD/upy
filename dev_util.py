
"""
    Copyright (C) <2010>  Autin L. TSRI
    
    This file git_upy/dev_util.py is part of upy.

    upy is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    upy is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with upy.  If not, see <http://www.gnu.org/licenses/gpl-3.0.html>.
"""
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 20 11:10:17 2011

@author: Ludovic Autin
utilities for adding function or host
"""
import os
import upy
UPY_PATH = upy.__path__[0]

HOST = {"blender24":"blender"+os.sep+"v249",
        "blender25":"blender"+os.sep+"v257",
        "maya":"autodeskmaya",
        "c4d":"cinema4d",
        "dejavu":"dejavuTk",
        "qt":"pythonUI"+os.sep,
        "tk":"pythonUI"+os.sep,
}

class Tools:
    def __init__(self,**kw):
        self.functionCode=""
        self.classType="helper" #or adaptor
        self.functionName=""
        self.anchor=""

    def deploy(self,position=None):
        #will write everywhere?
        if position == None :
            #append at the end
            position = self.anchor
        f = open(UPY_PATH+os.sep+HOST[host]+os.sep+host+self.classType)
    
    def write(self,host,position=None):        
        #will write everywhere?
        if position == None :
            #append at the end
            position = self.anchor
        f = open(UPY_PATH+os.sep+HOST[host]+os.sep+host+self.classType)
        f.replace(self.anchor,self.functionCode+self.anchor)#indentation?
        
