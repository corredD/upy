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
        
