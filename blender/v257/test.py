# -*- coding: utf-8 -*-
"""
Created on Wed Jul  6 12:37:23 2011

@author: -
"""

#----------------------------------------------------------
# File layout.py
#----------------------------------------------------------
import bpy

import pyubic
pyubic.setUIClass()#pref="qt"

#should have a template ?
from pyubic import uiadaptor
helperClass = pyubic.getHelperClass()

class cubi(uiadaptor):
    def __init__(self,**kw):
        uiadaptor.__init__(self,kw)
        self.initWidget()
        self.setupLayout()
#        self.y = 200 #top line
        self.title = "cubi"
        #we need the helper
        self.helper = helperClass(kw)
        self.dock = False
        #self.widgetGap = 0
        
    #theses two function are for c4d
    def CreateLayout(self):
        self._createLayout()
        return 1

    def Command(self,*args):
#        print args
        self._command(args)
        return 1
    
    def initWidget(self,id=None):
        self.PUSHS = {}
        self.PUSHS["CreateSphere"] = self._addElemt(name="Sphere",width=80,height=10,
                                     action=self.createSphere,type="button",icon=None,
                                     variable=self.addVariable("int",0))
        
    def setupLayout(self):
        self._layout = []
        self._layout.append([self.PUSHS["CreateSphere"],])
        
bpy.mygui = cubi()

#call it
#mygui.display()


#   Layout panel
class LayoutPanel(bpy.types.Panel):
    bl_label = "Panel with funny layout"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOL_PROPS"
 
    def draw(self, context):
        layout = self.layout
 
        layout.label("First row")
        row = layout.row(align=True)
        row.alignment = 'EXPAND'
        row.operator("my.button", text="1").number=1
        row.operator("my.button", text="2", icon='MESH_DATA').number=2
        row.operator("my.button", icon='LAMP_DATA').number=3
 
        row = layout.row(align=False)
        row.alignment = 'LEFT'
        row.operator("my.button", text="4").number=4
        row.operator("my.button", text="", icon='MATERIAL').number=5
        row.operator("my.button", text="6", icon='BLENDER').number=6
        row.operator("my.button", text="7", icon='WORLD').number=7
 
        layout.label("Third row", icon='TEXT')
        row = layout.row()
        row.alignment = 'RIGHT'
        row.operator("my.button", text="8").row=3
        row.operator("my.button", text="9", icon='SCENE').row=3
        row.operator("my.button", text="10", icon='BRUSH_INFLATE').row=3
 
        layout.label("Fourth row", icon='ACTION')
        row = layout.row()
        box = row.box()
        box.operator("my.button", text="11", emboss=False).loc="4 11"
        box.operator("my.button", text="12", emboss=False).loc="4 12"
        col = row.column()
        subrow = col.row()
        subrow.operator("my.button", text="13").loc="4 13"
        subrow.operator("my.button", text="14").loc="4 14"
        subrow = col.row(align=True)
        subrow.operator("my.button", text="15").loc="4 15"
        subrow.operator("my.button", text="16").loc="4 16"
        box = row.box()
        box.operator("my.button", text="17").number=17
        box.separator()
        box.operator("my.button", text="18")
        box.operator("my.button", text="19")
 
        layout.label("Fifth row")
        row = layout.row()
        split = row.split(percentage=0.25)
        col = split.column()
        col.operator("my.button", text="21").loc="5 21"
        col.operator("my.button", text="22")
        split = split.split(percentage=0.3)
        col = split.column()
        col.operator("my.button", text="23")
        split = split.split(percentage=0.5)
        col = split.column()
        col.operator("my.button", text="24")
        col.operator("my.button", text="25")
 
#   Button
class OBJECT_OT_Button(bpy.types.Operator):
    bl_idname = "my.button"
    bl_label = "Button"
    number = bpy.props.IntProperty()
    row = bpy.props.IntProperty()
    loc = bpy.props.StringProperty()
 
    def execute(self, context):
        if self.loc:
            words = self.loc.split()
            self.row = int(words[0])
            self.number = int(words[1])
        print("Row %d button %d" % (self.row, self.number))
        return{'FINISHED'}    
 
#    Registration
bpy.utils.register_module(__name__)
#bpy.utils.register_class(cubi)
#mygui = cubi()
#call it
#mygui.display()