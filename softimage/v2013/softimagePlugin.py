
"""
    Copyright (C) <2010>  Autin L. TSRI
    
    This file git_upy/softimage/v2013/softimagePlugin.py is part of upy.

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
"""
Created on Tue Mar 20 10:05:03 2012

@author: Ludovic Autin
"""

import os
import win32com.client
from win32com.client import constants
import sys

#base helper class
from upy.pluginAdaptor import pluginAdaptor
null = None
false = 0
true = 1

import inspect

global registeredCommands
registeredCommands = []
 
class general_plugClass(pluginAdaptor):
    registeredCommands = []    
    host = "softimage"
    def __init__(self,**kw):
        pluginAdaptor.__init__(self,**kw)
        self.setup()
        self.gui = None
        
    #@classmethod
    def creator(cls):
        return #OpenMayaMPx.asMPxPtr( cls() )
  
    #@classmethod
    def register(self,classObject,Object=None,**kw):
        """
        by default the command will be registered to a dummy plugin provided by pymel.
  
        If you
        if using from within a plugin's initializePlugin or uninitializePlugin callback, pass along the
        MObject given to these functions
        """
        if Object is None :
            Object = self
        if Object is not None :
            plug_name = Object.plugin_name
        mobject = None   
        regfunction = 'def XSILoadPlugin( in_reg ):\n'
        #regfunction+= '\tin_reg.Author = "ludo"\n'
        regfunction+= '\tin_reg.Name = "'+plug_name+'"\n'
        #regfunction+= '\tin_reg.Major = 1\n'
        #regfunction+= '\tin_reg.Minor = 0\n'
        if self.hasGui :
            regfunction+= '\tin_reg.RegisterProperty("'+plug_name+'_gui")\n'
        regfunction+= '\tin_reg.RegisterCommand("ePMV","'+plug_name+'")#RegisterProperty\n'
        regfunction+= '\tin_reg.RegisterMenu(constants.siMenuMainFileImportID,"'+plug_name+'_Menu",false,false)\n'
        exec(regfunction,globals(),locals())
        
    # @classmethod
    def deregister(self, object=None,**kw):
        """
        if using from within a plugin's initializePlugin or uninitializePlugin callback, pass along the
        MObject given to these functions
        """
        uregfunction ="""def XSIUnloadPlugin( in_reg ):
    strPluginName = in_reg.Name
    Application.LogMessage(str(strPluginName) + str(" has been unloaded."),constants.siVerbose)
    return true\n"""
        exec(uregfunction,globals(),locals())

    def doIt(self,argList):
         #dname=doc.GetDocumentName()
         print argList
         print self
         print dir(self)
         self.runCommands() 
         if self.hasGui and self.gui is None :
             self.setgui("")
    

class pluginTag(general_plugClass):
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
            
class pluginCommand(general_plugClass):
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