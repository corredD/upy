
"""
    Copyright (C) <2010>  Autin L. TSRI
    
    This file git_upy/autodesk3dsmax/v2015/maxPlugin.py is part of upy.

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
Created on Tue Mar 20 10:05:03 2012

@author: Ludovic Autin

From PyMel:
from pymel.api.plugins import Command
class testCmd(Command):
    def doIt(self, args):
        print "doIt..."
  
testCmd.register()
cmds.testCmd()
testCmd.deregister()
"""

import os

#base helper class
from upy.pluginAdaptor import pluginAdaptor

 
import sys
import inspect

global registeredCommands
registeredCommands = []
  
#def _pluginModule():
#    return inspect.getmodule( lambda: None )
#  
#def _pluginName():
#    return _pluginModule().__name__.split('.')[-1]
#  
#def _pluginFile():
#    return inspect.getsourcefile( lambda:None )
##    module = sys.modules[__name__]
##    print module, __name__
##    return module.__file__
#  
#def _loadPlugin():
#    thisFile = _pluginFile()
#    if not maya.cmds.pluginInfo( thisFile, query=1, loaded=1 ):
#        maya.cmds.loadPlugin( thisFile )
#  
#def _unloadPlugin():
#    thisFile = _pluginFile()
#    if maya.cmds.pluginInfo( thisFile, query=1, loaded=1 ):
#        maya.cmds.unloadPlugin( thisFile )
#  
#  
#def _getPlugin():
#    _loadPlugin()
#    mobject = OpenMayaMPx.MFnPlugin.findPlugin( _pluginName() )
#    return OpenMayaMPx.MFnPlugin(mobject)
#  
class general_plugClass(pluginAdaptor):
    registeredCommands = []    
    host = "softimage"
    def __init__(self,**kw):
        pluginAdaptor.__init__(self,**kw)
        self.setup()
        self.gui = None
        
    @classmethod
    def creator(cls):
        return #OpenMayaMPx.asMPxPtr( cls() )
  
    @classmethod
    def register(cls,classe,Object=None,**kw):
        """
        by default the command will be registered to a dummy plugin provided by pymel.
  
        If you
        if using from within a plugin's initializePlugin or uninitializePlugin callback, pass along the
        MObject given to these functions
        """
        pass
#        plug_name=cls.__name__
#        if Object is not None :
#            plug_name = Object.plugin_name
#        mobject = None
#        if "mobject" in kw :
#            mobject = kw["mobject"]
#        if mobject is None:
#            plugin = _getPlugin()
#            cls.registeredCommands.append( plug_name )
#        else:
#            plugin = OpenMayaMPx.MFnPlugin(mobject)
#        if hasattr(cls, 'createSyntax'):
#            plugin.registerCommand( plug_name, cls.creator, cls.createSyntax )
#        else:
#            plugin.registerCommand( plug_name, cls.creator )
  
    @classmethod
    def deregister(cls, object=None,**kw):
        """
        if using from within a plugin's initializePlugin or uninitializePlugin callback, pass along the
        MObject given to these functions
        """
        pass
#        if object is None:
#            plugin = _getPlugin()
#            cls.registeredCommands.pop(cls.__name__)
#        else:
#            plugin = OpenMayaMPx.MFnPlugin(object)
#        plugin.deregisterCommand( cls.__name__ )
#        if self.plugin_class :
#            self.remove_callback()
        
    def doIt(self,argList):
         #dname=doc.GetDocumentName()
         print argList
         print self
         print dir(self)
         self.runCommands() 
         if self.hasGui and self.gui is None :
             self.setgui("")
    

class pluginTag(general_plugClass,OpenMayaMPx.MPxCommand):
    plugin_class = "tag"
    def __init__(self,**kw):
        pass
#        general_plugClass.__init__(self,**kw)
#        OpenMayaMPx.MPxCommand.__init__(self)   
#        self.period = 0.1
#        self.timeControl = oma.MAnimControl()
#        self.callback = None
        
    def change_period(self,newP):
        self.period = newP
        self.remove_callback()
        self.set_callback()
     
    @classmethod 
    def set_callback(self):
        pass
#        self.callback = OpenMaya.MTimerMessage.addTimerCallback(self.period,self.execute)
    
    @classmethod
    def remove_callback(self):
        pass
#        OpenMaya.MMessage.removeCallback(self.callback)

    def execute(self,*args,**kw):        
        self.runCommands()
    
    def doIt(self,argList):
        pass
#        if argList.length() > 0 :
#            if not argList.asBool(0) : 
#                self.remove_callback()
#        else :
#            self.set_callback()
            
class pluginCommand(general_plugClass,OpenMayaMPx.MPxCommand):
    plugin_class = "commands"
#    def __init__(self,**kw):
#        general_plugClass.__init__(self,**kw)
#        OpenMayaMPx.MPxCommand.__init__(self)

#def initializePlugin(mobject):
#    print "int ",mobject.apiTypeStr()
#    
#def uninitializePlugin(mobject):
#    pass
    

def get(pType):
    if pType == "tag":
        return None#pluginTag,OpenMayaMPx.MPxCommand
    elif pType == "command":
        return None#pluginCommand,OpenMayaMPx.MPxCommand
    return None