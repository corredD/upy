# -*- coding: utf-8 -*-
"""
Created on Mon Mar 19 11:36:12 2012

@author: Ludovic Autin
"""
import os

#base helper class
import upy
from upy.pluginAdaptor import pluginAdaptor

import bpy

class general_plugClass(pluginAdaptor):
    
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

    @staticmethod
    def register(classObject,Object=None,**kw):
        #should create some file and folder ?
        #test plugin folder
        self = Object        
        callback = self.runCommands
        idname = "upy.%s" % self.plugin_name.lower().replace(" ","_")# % (self.uiname.lower()+title.lower().replace(" ","_"))
        classname = "%s" % self.plugin_name.lower().replace(" ","_")#self.uiname+label.lower().replace(" ","_")
        
        ldic = locals()
        gdic = globals()
        ldic["runCommand"] = self.runCommand
        gdic["runCommand"] = self.runCommand
        ldic["setgui"] = self.setgui
        gdic["setgui"] = self.setgui        
        ldic["resetgui"] = self.resetgui
        gdic["resetgui"] = self.resetgui
        ldic["gui"] = self.gui
        gdic["gui"] = self.gui        
        ldic["makeop"] = self.makeop
        gdic["makeop"] = self.makeop        

        clascode = ""
#        if not hasattr(bpy.ops,idname) :
        clascode += "class OP_%s (%s):\n" % (classname,self.baseClass)
        clascode += "    bl_label = '%s'\n" % self.plugin_name
        clascode += "    bl_idname =   '%s'\n" %  idname
        clascode += "    bl_optons =   {'UNDO','REGISTER','BLOCKING'}\n"
        if False :
            clascode += "    def draw(self, context):\n"
            clascode += "        layout = self.layout\n"
            clascode += '        lines = self.messageString.split("\\n")\n'
            clascode += "        for line in lines :\n"
            clascode += "            row = layout.row()\n"
            clascode += "            row.label(line)\n"
        clascode += "    def execute(self, context):\n"
        clascode += "        dname='%s'\n" % self.plugin_name
        clascode += "        if runCommand:\n"
        clascode += "            runCommand()\n"
        clascode += "        if %s and gui is None :\n" % self.hasGui
        clascode += "             setgui(dname)\n"
#        clascode += "        if %s : gui.display()\n" % self.hasGui       
        clascode += "        return {'FINISHED'}\n"
#        clascode += "def register():\n"        
        clascode += "bpy.utils.register_class(OP_%s)\n" % classname
        clascode += "def makeop(self,context):\n"
        clascode += "    self.layout.operator('%s',icon='%s')\n" % (idname,self.plugin_icon)
        self.menuadd = kw["menuadd"]
        if "menuadd" in kw:
            if "header" in kw["menuadd"]:
#                if kw["menuadd"]["header"] :
#                    ldic["makeop"] = kw["menuadd"]["header"]
#                    gdic["makeop"] = kw["menuadd"]["header"]               
                clascode += "bpy.types.INFO_HT_header.append(makeop)\n"
            if "mt" in kw["menuadd"]:
#                if kw["menuadd"]["mt"]:
#                    ldic["makeop"] = kw["menuadd"]["mt"]
#                    gdic["makeop"] = kw["menuadd"]["mt"]  
                clascode += "bpy.types.INFO_MT_add.append(makeop)\n"
#            clascode += "    pass\n"
        clascode += "def unregister():\n"
        if "menuadd" in kw:        
            if "header" in kw["menuadd"]:
                if kw["menuadd"]["header"] :
                    ldic["makeop"] = kw["menuadd"]["header"]
                    gdic["makeop"] = kw["menuadd"]["header"]               
                clascode += "    bpy.types.INFO_HT_header.remove(makeop)\n"
            if "mt" in kw["menuadd"]:
                if kw["menuadd"]["mt"]:
                    ldic["makeop"] = kw["menuadd"]["mt"]
                    gdic["makeop"] = kw["menuadd"]["mt"]  
                clascode += "    bpy.types.INFO_MT_add.remove(makeop)\n"
            if "mt" in kw["menuadd"]:
                if kw["menuadd"]["mtmesh"]:
                    ldic["makeop"] = kw["menuadd"]["mtmesh"]
                    gdic["makeop"] = kw["menuadd"]["mtmesh"]  
                clascode += "    bpy.types.INFO_MT_mesh_add.remove(makeop)\n"
            clascode += "    pass\n"
#        clascode += "register()\n"
        print (clascode)
        exec(clascode, gdic,ldic)       
    
    @staticmethod 
    def unregister():
    #    epmvgui.close()
        if self.menuadd is not None:
            if "header" in self.menuadd:
                bpy.types.INFO_HT_header.remove(self.menuadd["header"])
            if "mt" in self.menuadd:
                bpy.types.INFO_MT_add.remove(self.menuadd["mt"])    
            if "mtmesh" in self.menuadd:
                bpy.types.INFO_MT_add.remove(self.menuadd["mtmesh"]) 
    def getType(self):
        pass
 
    def runCommands(self,*args,**kw):
        pass
   
    def setRunCommands(self,runCommands=None):
        self.runCommands = runCommands
    
    def execute(self, context):
        self.runCommands()
        return {'FINISHED'}

    def setgui(self,dname):
        pass
 
    def resetgui(self,dname):
        pass
    
    def makeop(self, context):
        self.layout.operator(self.bl_idname,icon=self.plugin_icon)   
       
class pluginTag(general_plugClass):

    def __init__(self,**kw):
        general_plugClass.__init__(self,**kw)
        self.baseClass = "bpy.types.Operator"
        self.plugin_class= "tag"

class pluginCommand(general_plugClass):

    def __init__(self,**kw):
        general_plugClass.__init__(self,**kw)
        self.baseClass = "bpy.types.Operator"
        self.plugin_class= "commands"
        

def get(pType):
    if pType == "tag":
        return pluginTag,bpy.types.Operator
    elif pType == "command":
        return pluginCommand,bpy.types.Operator#pluginCommand
    return None