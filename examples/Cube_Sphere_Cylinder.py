
"""
    Copyright (C) <2010>  Autin L. TSRI
    
    This file git_upy/examples/Cube_Sphere_Cylinder.py is part of upy.

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
Created on Wed Dec 29 13:09:18 2010

@author: Ludovic Autin
"""

import sys,os
#pyubic have to be in the pythonpath, if not add it
#pathtoupy = "/Users/ludo/pathtoupy/"
#sys.path.insert(0,pathtoupy)
#if you want to use numpy, numpy have to be in the pythonpath to

import numpy

import upy
upy.setUIClass()

from upy import uiadaptor
#you can import the daptor directly
#from pyubic.qtUI import qtUIDialog as uiadaptor
#from pyubic.tkUI import tkUIDialog as uiadaptor

#get the helperClass for modeling
helperClass = upy.getHelperClass()

class SphereCubeCylUI(uiadaptor):
    def setup(self,vi=None):
        #get the helper
        self.helper = helperClass(vi=vi)
        #dont want to dock it ie maya 
        self.dock = False
        #boolean statut of synchronization
        self.synchronized = False
        #initialize widget and layout
        self.initWidget()        
        self.setupLayout_simple()        
#        self.setupLayout(ftype="frame")        
#        self.setupLayout(ftype="tab")        
        
    #dont touch theses two functions specific for c4d
    def CreateLayout(self):
        self._createLayout()
        return 1
    def Command(self,*args):
#        print args
        self._command(args)
        return 1


    def initWidget(self,id=None):
        #this is where we define the widhet such as buttons and siders
        self.PUSHS = {}
        #first  add a button that will trigger the creation of the sphere
        self.PUSHS["CreateSphere"] = self._addElemt(name="Sphere",width=80,height=10,
                                     action=self.createSphere,type="button",icon=None,
                                     variable=self.addVariable("int",0),label="create Sphere")
        #then  add a button that will trigger the creation of the cube
        self.PUSHS["CreateCube"] = self._addElemt(name="Cube",width=80,height=10,
                                     action=self.createCube,type="button",icon=None,
                                     variable=self.addVariable("int",0),label="create Cube")
        #then  add a button that will trigger the creation of the cube
        self.PUSHS["CreateCone"] = self._addElemt(name="Cone",width=80,height=10,
                                     action=self.createCone,type="button",icon=None,
                                     variable=self.addVariable("int",0),label="create Cone")

        #we add then the slider widget for changing  the scale of both the sphere and the cube
        self.SLIDERS = {"sphere":self._addElemt(name="sphere_scale",width=80,height=10,
                                             action=self.scaleSphere,type="sliders",
                                             variable=self.addVariable("float",1.0),
                                             mini=0.01,maxi=5.,step=0.01),
                        "cube":self._addElemt(name="cube_scale",width=80,height=10,
                                             action=self.scaleCube,type="sliders",
                                             variable=self.addVariable("float",1.0),
                                             mini=0.0,maxi=10.,step=0.01),
                        "coneH":self._addElemt(name="cone_height",width=80,height=10,
                                             action=self.scaleCone,type="sliders",
                                             variable=self.addVariable("float",1.0),
                                             mini=0.0,maxi=10.,step=0.01),
                        "coneR":self._addElemt(name="cone_radius",width=80,height=10,
                                             action=self.scaleCone,type="sliders",
                                             variable=self.addVariable("float",1.0),
                                             mini=0.0,maxi=10.,step=0.01)}
                             
        self.synchro = self._addElemt(name="synchroPos",width=80,height=10,
                                             action=self.setSynchro,type="checkbox",
                                             variable=self.addVariable("int",0),
                                             label="synchro position")
        self.userDialogPercentage=self._addElemt(name="scaleTrans",width=80,height=10,
                                             action=None,type="sliders",
                                             variable=self.addVariable("float",1.0),
                                             mini=0.0,maxi=10.,step=0.1)
                                             
        self.selectedObject = self._addElemt(name="selObj",width=80,height=10,
                                             action=None,type="inputStr",
                                             variable=self.addVariable("str",""),
                                             )
        self.translateObjX = self._addElemt(name="selObjX",width=80,height=10,
                                             action=self.translateSel,type="inputFloat",
                                             variable=self.addVariable("float",0.0),
                                             mini=-100000.0,maxi=100000.,step=1.0)
        self.labelSel = self._addElemt(label="Move X-position of :",width=80,height=10)
        self.labelTranslate = self._addElemt(label="by :",width=80,height=10)
    def setupLayout_simple(self,ftype="frame"):
        self._layout = []
        self._layout.append([self.PUSHS["CreateSphere"],self.SLIDERS["sphere"]])
        self._layout.append([self.PUSHS["CreateCube"],self.SLIDERS["cube"]])
        self._layout.append([self.PUSHS["CreateCone"],])
        self._layout.append([self.SLIDERS["coneR"],self.SLIDERS["coneH"]])
        self._layout.append([self.labelSel,self.selectedObject])
        self._layout.append([self.labelTranslate,self.translateObjX])
        self._layout.append([self.synchro,self.userDialogPercentage])
        
    def setupLayout(self,ftype="frame"):
        #this where we define the Layout
        #this wil make three button on a row
        #self._layout is a class variable that you need to use
        #you may use your own, but remember to reassign to self._layou at the end.
        #for instance:
        #mylayout=[]
        #mylayout.append([widget])
        #self._layout=mylayout
        self._layout = []
        #we creat a first "frame" for the first line of the dialog.
        #the frame can be collapse, and will present the creation button and the slider on the
        #same line        
        elemFrame1=[]
        elemFrame1.append([self.PUSHS["CreateSphere"],self.SLIDERS["sphere"]])
        frame1 = self._addLayout(name="Sphere",elems=elemFrame1,
                                     type=ftype,collapse=False)
        #we add the frame to the layout        
        self._layout.append(frame1)
        
        #we reapeat for the cube
        elemFrame2=[]
        elemFrame2.append([self.PUSHS["CreateCube"],self.SLIDERS["cube"]])
        frame2 = self._addLayout(name="Cube",elems=elemFrame2,
                                 type=ftype,collapse=False)
        self._layout.append(frame2)

        #we reapeat for the cone
        elemFrame3=[]
        elemFrame3.append([self.PUSHS["CreateCone"],])
        elemFrame3.append([self.SLIDERS["coneR"],self.SLIDERS["coneH"]])
        frame3 = self._addLayout(name="Cone",elems=elemFrame3,
                                 type=ftype,collapse=False)
        self._layout.append(frame3)
        elemFrame4=[]
        elemFrame4.append([self.labelSel,self.selectedObject])
        elemFrame4.append([[self.labelTranslate,self.translateObjX]])
        frame4 = self._addLayout(name="selection Object",elems=elemFrame4,
                                 type=ftype,collapse=False)
        self._layout.append(frame4)
        self._layout.append([self.synchro,self.userDialogPercentage])
#===============================================================================
# we define the callback action below
#===============================================================================

    def createSphere(self,*args):
        #call back trigger by the push button
        name = "newSphere"
        #use the helpr to verify if we alredy have create the sphere
        o = self.helper.getObject(name)
        if o is None :
           #if not create it, using default value
           o = self.helper.Sphere(name,res=12)
                
    def createCube(self,*args):
        #create the cube
        name = "newCube"
        #use the helpr to verify if we alredy have create the cube
        o = self.helper.getObject(name)
        if o is None :
           #if not create it, using default value
           o = self.helper.Cube(name)

    def createCone(self,*args):
        #create the cube
        name = "newCone"
        #use the helpr to verify if we alredy have create the cube
        o = self.helper.getObject(name)
        if o is None :
           #if not create it, using default value
           o = self.helper.Cone(name)
           #Cone(self,name,radius=1.,length=1.,res=9, pos = [0.,0.,0.],parent=None)
           
    def scaleSphere(self,*args):
        #get the stat
        #this function is trigger when the slider value change.
        scale = self.getReal(self.SLIDERS["sphere"])
        #get the current slider value
        o = self.helper.getObject("newSphere")
        #get the sphere
        if o is not None :
            #if the sphere exists change the scale value
            self.helper.scaleObj(o,scale)
            self.helper.update()
    
    def scaleCube(self,*args):
        #this function is trigger when the slider value change.
        scale = self.getReal(self.SLIDERS["cube"])
         #get the current slider value
        o = self.helper.getObject("newCube")
        #get the cube
        if o is not None :
            #if the cube exists change the scale value
            self.helper.scaleObj(o,scale)
            self.helper.update()

    def scaleCone(self,*args):
        #this function is trigger when the slider value change.
        scaleH = self.getReal(self.SLIDERS["coneH"])
        scaleR = self.getReal(self.SLIDERS["coneR"])
         #get the current slider value
        o = self.helper.getObject("newCone")
        #get the cube
        scale = [scaleR,scaleH,scaleR]
        if o is not None :
            #if the cube exists change the scale value
            #assuming the cone principal acis is [0.,1.,0.]
            #blender default axis for cone is 0.,0.,1.0
            #this example show how you can deal with host exception
            if self.helper.host.find("blender") != -1 :
                scale = [scaleR,scaleR,scaleH]
            self.helper.scaleObj(o,scale)
            self.helper.update()

    def translateSel(self,*args):
        nameSel = self.getVal(self.selectedObject)
        if nameSel != None and nameSel != "":
            o=self.helper.getObject(nameSel)
            if o is not None :
                xpos = self.getVal(self.translateObjX)
                cpos = self.helper.ToVec(self.helper.getTranslation(o))
                self.helper.setTranslation(o,[xpos,cpos[1],cpos[2]])
                self.helper.update()
                
    def callBackForsynchro(self,*args,**kw):
        #print ("time",time)
        userDialogPercentage = self.getVal(self.userDialogPercentage)
        print ("userDialogPercentage",userDialogPercentage)
#        cube = self.helper.getObject("newCube")
#        sphere = self.helper.getObject("newSphere")
#        cone = self.helper.getObject("newCone")
        posCube=self.helper.ToVec(self.helper.getTranslation("newCube"))
        posSphere=self.helper.ToVec(self.helper.getTranslation("newSphere"))
        posCone=[0,0,0]
        for i in range(3):
            posCone[i]=(posCube[i]+posSphere[i])*userDialogPercentage
        print ("posCone",posCone) 
        self.helper.setTranslation("newCone",pos=posCone)
        
    def setSynchro(self,*args):
        #this will synchronize the position of the cone as follow
        #Position cone = (GetVector sphere + getVector cube)*userDialogPercentage
        dosynchro=self.getVal(self.synchro)
        if dosynchro and not self.synchronized: 
            self.helper.synchronize(self.callBackForsynchro)
            self.synchronized = True
        elif not dosynchro and self.synchronized: 
            self.helper.unsynchronize(self.callBackForsynchro)
            self.synchronized = False            

#this is a script, we need some special code for the Tk and the Qt case.
#the most important part are the instanciation of our dialog class, 
#and the two functio setup and display
#setup initialise the widget and the layout
#display wil actually show the dialog.       
if uiadaptor.host == "tk":
    from DejaVu import Viewer
    vi = Viewer()    
    #require a master
    #import Tkinter #Tkinter if python2.x tkinter for python3.x
    #root = Tkinter.Tk()
    mygui = SphereCubeCylUI(title="SphereCubeCylUI",master=vi)
    mygui.setup(vi=vi)
    #mygui.display()
elif uiadaptor.host == "qt":
    from PyQt4 import QtGui
    app = QtGui.QApplication(sys.argv)
    mygui = SphereCubeCylUI(title="SphereCubeCylUI")
    mygui.setup()
    #ex.show()
else :
    mygui = SphereCubeCylUI(title="SphereCubeCylUI")
    mygui.setup()
    #call it
mygui.display()
if uiadaptor.host == "qt": app.exec_()#work without it ?
#
##execfile("/Users/ludo/DEV/pyubic/examples/Cube_Sphere.py")
#Blender Text Run Python Script
#maya open and run in the console OR execfile("pathto/pyubic/examples/Cube_Sphere.py")
#dejavu mgtloos/bin/pythonsh -i Cube_Sphere.py