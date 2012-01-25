# -*- coding: utf-8 -*-
"""
Created on Wed Dec 29 13:09:18 2010

@author: Ludovic Autin
"""

import sys,os
#pyubic have to be in the pythonpath, if not add it
pathtoupy = "/Users/ludo/DEV/"
sys.path.insert(0,pathtoupy)

import upy
upy.setUIClass()

from upy import uiadaptor
#from pyubic.qtUI import qtUIDialog as uiadaptor
#from pyubic.tkUI import tkUIDialog as uiadaptor

#get the helperClass for modeling
helperClass = upy.getHelperClass()

class Cubi(uiadaptor):
    def setup(self):
        #get the helper
        self.helper = helperClass()
        #dont want to dock it ie maya 
        self.dock = False
        #initialize widget and layout
        self.initWidget()
        self.setupLayout()        
        
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
        self.PUSHS["CreateSphere"] = self._addElemt(name="Sphere",width=80,height=10,
                                     action=self.createSphere,type="button",icon=None,
                                     variable=self.addVariable("int",0))
        self.PUSHS["CreateCube"] = self._addElemt(name="Cube",width=80,height=10,
                                     action=self.createCube,type="button",icon=None,
                                     variable=self.addVariable("int",0))

        #the slider scale and radius
        self.SLIDERS = {"sphere":self._addElemt(name="sphere_scale",width=80,height=10,
                                             action=self.scaleSphere,type="sliders",
                                             variable=self.addVariable("float",1.0),
                                             mini=0.01,maxi=5.,step=0.01),
                        "cube":self._addElemt(name="cube_scale",width=80,height=10,
                                             action=self.scaleCube,type="sliders",
                                             variable=self.addVariable("float",1.0),
                                             mini=0.0,maxi=10.,step=0.01)}

        
    def setupLayout(self):
        #this where we define the Layout
        #this wil make three button on a row
        self._layout = []
        elemFrame1=[]
        elemFrame1.append([self.PUSHS["CreateSphere"],self.SLIDERS["sphere"]])
        frame1 = self._addLayout(name="Sphere",elems=elemFrame1)#,type="tab")
        self._layout.append(frame1)
        
        elemFrame2=[]
        elemFrame2.append([self.PUSHS["CreateCube"],self.SLIDERS["cube"]])
        frame2 = self._addLayout(name="Cube",elems=elemFrame2)#,type="tab")
        self._layout.append(frame2)

#===============================================================================
# we define the callback action below
#===============================================================================

    def createSphere(self,*args):
        name = "newSphere"
        o = self.helper.getObject(name)
        if o is None :
           o = self.helper.Sphere(name,res=12)
                
    def createCube(self,*args):
        #create the cube
        name = "newCube"
        o = self.helper.getObject(name)
        if o is None :
           o = self.helper.Cube(name)
        
    def scaleSphere(self,*args):
        #get the stat
        scale = self.getReal(self.SLIDERS["sphere"])
        o = self.helper.getObject("newSphere")
        if o is not None :
            self.helper.scaleObj(o,scale)
    
    def scaleCube(self,*args):
        scale = self.getReal(self.SLIDERS["cube"])
        o = self.helper.getObject("newCube")
        if o is not None :
            self.helper.scaleObj(o,scale)
        
if uiadaptor.host == "tk":
    #from DejaVu import Viewer
    #vi = Viewer()    
    #require a master
    import tkinter #Tkinter if python2.x tkinter for python3.x
    root = tkinter.Tk()
    mygui = Cubi(master=root,title="CubeUI")
    #mygui.display()
elif uiadaptor.host == "qt":
    from PyQt4 import QtGui
    app = QtGui.QApplication(sys.argv)
    mygui = Cubi(title="CubeUI")
    #ex.show()
else :
    mygui = Cubi(title="CubeUI")
    #call it
mygui.setup()
mygui.display()
if uiadaptor.host == "qt": app.exec_()#work without it ?
#
##execfile("/Users/ludo/DEV/pyubic/examples/simpleButtons.py")
#Blender Text Run Python Script
#maya open and run in the console OR execfile("pathto/pyubic/examples/Cube_Sphere.py")
#dejavu mgtloos/bin/pythonsh -i Cube_Sphere.py