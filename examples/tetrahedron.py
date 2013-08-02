# -*- coding: utf-8 -*-
"""
Created on Wed Jan 19 12:12:14 2011

@author: Ludovic Autin - ludovic.autin@gmail.com
this example is really similar to the Cube_sphere one. The purpose is to sho the use of the modellin helper to crate a mesh.

"""
#example for a script not a plugin ....

import sys,os
#pyubic have to be in the pythonpath, if not add it
#pathtoupy = "/Users/ludo/pathtoupy/"
#sys.path.insert(0,pathtoupy)

import upy
upy.setUIClass()

#get the CGhelper
from upy import uiadaptor
helperClass = upy.getHelperClass()

import math



class Tetrahedron(uiadaptor):

    def setup(self,verts=None,faces=None,**kw):
        #get the helper
        self.helper = helperClass(**kw)
        #dont want to dock it ie maya 
        self.dock = False
        self.initWidget(id=10)
        self.setupLayout()
        self.verts = verts
        if self.verts is None :
            self.verts = [
                (0, -1 / math.sqrt(3),0),
                (0.5, 1 / (2 * math.sqrt(3)), 0),
                (-0.5, 1 / (2 * math.sqrt(3)), 0),
                (0, 0, math.sqrt(2 / 3)),
                ]
        self.faces = faces
        if self.faces is None :
            self.faces = [[0, 1, 2], [0, 1, 3], [1, 2, 3], [2, 0, 3]]    
            
    #theses two function are for c4d
    def CreateLayout(self):
        self._createLayout()
        return 1
    def Command(self,*args):
#        print args
        self._command(args)
        return 1

    
    def initWidget(self,id=None):
        #this where we define the buttons
        self.PUSHS = {}
        self.PUSHS["Tetrahedron"] = self._addElemt(id=id,name="Tetrahedron",width=80,height=10,
                                     action=self.createTetrahedron,type="button",icon=None,
                                     variable=self.addVariable("int",0))
        id = id + len(self.PUSHS)
        #the slider scale and radius
        self.SLIDERS = {"Tetrahedron":self._addElemt(id=id,name="Tetrahedron_scale",width=80,height=10,
                                             action=self.scaleTetrahedron,type="sliders",
                                             variable=self.addVariable("float",1.0),
                                             mini=0.01,maxi=5.,step=0.01),}
        id = id + len(self.SLIDERS)
        
    def setupLayout(self):
        #this where we define the Layout
        #this wil make three button on a row
        self._layout = []
        elemFrame1=[]
        elemFrame1.append([self.PUSHS["Tetrahedron"]])
        elemFrame1.append([self.SLIDERS["Tetrahedron"]])
        frame1 = self._addLayout(id=100,name="Tetrahedron",elems=elemFrame1,type="tab")
        self._layout.append(frame1)

#==============================================================================
# create the calback function
#==============================================================================

    def createTetrahedron(self,*args):
        name = "Tetrahedron"
        o = self.helper.getObject(name)
        if o is None :
            object,mesh = self.helper.createsNmesh(name,self.verts,None,self.faces)
            self.helper.addObjectToScene(self.helper.getCurrentScene(),object)
                       
    def scaleTetrahedron(self,*args):
        #get the stat
        scale = self.getReal(self.SLIDERS["Tetrahedron"])
        o = self.helper.getObject("Tetrahedron")
        if o is not None :
            self.helper.scaleObj(o,scale)
            
if uiadaptor.host == "tk":
    #from DejaVu import Viewer
    #vi = Viewer()    
    #require a master
    import tkinter
    root = tkinter.Tk()
    mygui = Tetrahedron(master=root,title="TetrahedronUI")
    #mygui.display()
elif uiadaptor.host == "qt":
    from PyQt4 import QtGui
    app = QtGui.QApplication(sys.argv)
    mygui = Tetrahedron(title="TetrahedronUI")
    #ex.show()
else :
    mygui = Tetrahedron(title="TetrahedronUI")
    #call it
mygui.setup()
mygui.display()
if uiadaptor.host == "qt": app.exec_()#work without it ?

#C4D : execfile("/Users/ludo/DEV/upy/trunk/upy/examples/tetrahedron.py")
#Blender Text Run Python Script
#maya open and run in the console