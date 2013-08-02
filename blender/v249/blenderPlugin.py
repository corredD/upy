# -*- coding: utf-8 -*-
"""
Created on Mon Mar 19 11:36:12 2012

@author: Ludovic Autin
"""
import os

#base helper class
import upy
from upy.pluginAdaptor import pluginAdaptor
from upy.blender.v249.blenderHelper import blenderHelper
from upy.blender.v249.blenderUI import blenderUIDialog

import Blender
from Blender import Draw

class general_plugClass(pluginAdaptor):
    host = "blender"
    def __init__(self,**kw):
        pluginAdaptor.__init__(self,**kw)
        self.plugin_id =  1025244
        self.setup()
        self.gui = None
        self.menuadd = None
        self.bl_idname = "upy."+self.plugin_name.lower()
        self.bl_label = self.plugin_name
 
    
    def setIcon(self,image_filename=None,image_name=None):
#        dir, file = os.path.split(__file__)
#        self.plugin_icon = c4d.bitmaps.BaseBitmap()
        if image_filename is not None :
            pass
        elif image_name is not None :
            pass

#    @staticmethod
    def register(self,classObject,Object=None,**kw):
        #need the object
        if Object is None :  
            Object = classObject()
            #and this should be a dialog
        Object.setgui("")
        if Object.gui is None :
            return        
        Draw.Register(Object.gui.CreateLayout, Object.gui.CoreMessage, Object.gui.Command)
    
#    @staticmethod 
    def unregister(self):
        pass
    
    def getType(self):
        pass
 
    def runCommands(self,*args,**kw):
        pass
   
    def setRunCommands(self,runCommands=None):
        self.runCommands = runCommands
    
    def execute(self, context):
        self.runCommands()

    def setgui(self,dname):
        pass
 
    def resetgui(self,dname):
        pass
       
class pluginTag(general_plugClass):
    def __init__(self,**kw):
        general_plugClass.__init__(self,**kw)
        self.baseClass = general_plugClass
        self.plugin_class= "tag"

    def createStringRep(self):
        script_str="import upy\n"
        script_str+="from upy.blender.v249.blenderUI import blenderUIDialog\n"
        script_str+="plugin = blenderUIDialog._restore('upy_plugin',dkey='"+self.plugin_name+"')\n"
        script_str+="plugin.execute()"
        return script_str

#    @staticmethod
    def register(self,classObject,Object=None,**kw):
        blenderUIDialog._store("upy_plugin",{self.plugin_name:Object})
        prefdir = Blender.Get('uscriptsdir')
        if prefdir is None:
            prefdir = Blender.Get('scriptsdir')    
        #need to wrote the script as a text file that will be link to the object/scene
        blenderHelper.addTextFile(name=Object.plugin_name,
                                text=self.string_representation)
        scene = blenderHelper.getCurrentScene()
        #should load the script for scene update...
        scene.addScriptLink(Object.plugin_name, "FrameChanged")

#    @staticmethod 
    def unregister(self,):
        scene = blenderHelper.getCurrentScene()
        scene.clearScriptLinks()

class pluginCommand(general_plugClass):

    def __init__(self,**kw):
        general_plugClass.__init__(self,**kw)
        self.baseClass = general_plugClass
        self.plugin_class= "commands"
        

def get(pType):
    if pType == "tag":
        return pluginTag,general_plugClass
    elif pType == "command":
        return pluginCommand,general_plugClass#pluginCommand
    return None