
"""
    Copyright (C) <2010>  Autin L. TSRI
    
    This file git_upy/examples/layout.py is part of upy.

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
Created on Wed Dec 29 13:09:18 2010

@author: Ludovic Autin
"""

#example for a script not a plugin ....

import sys,os
#pyubic have to be in the pythonpath, if not add it
#pathtopyubic = "/Users/ludo/DEV/upy/trunk/"
#sys.path.insert(0,pathtopyubic)

import upy
upy.setUIClass()
from upy import uiadaptor

#weonly import the adaptor as thsi examl will only show widget features.

class LayoutUI(uiadaptor):
    def setup(self):
        self.w = 400
        self.initWidget(id=10)
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
        #self.menuorder = ["File","Edit","Help"]
        #self.submenu = {}
        #for i in range(10):
        #    self.submenu[str(self.id-1)]=self._addElemt(name="file"+str(i),
        #                                                action=self.recentfile_cb)
        #menu are always define by the MENU_ID dictionary and the self.menuorder
        #self.MENU_ID={"File":
        #              [self._addElemt(name="Recent Files",action=None,sub=self.submenu),
        #              self._addElemt(name="Open",action=self.open_cb),
        #              self._addElemt(name="Save",action=self.save_cb),
        #              self._addElemt(name="Exit",action=self.close)],
        #               "Edit" :
        #              [self._addElemt(name="Options",action=self.options_cb)],
        #               "Help" : 
        #              [self._addElemt(name="About",action=self.drawAbout),#self.drawAbout},
        #               self._addElemt(name="Help",action=self.drawHelp),#self.launchBrowser},
        #              ],
        #               }
        #if self.host == "blender25":
        #    self.setupMenu()
        self.CHECKBOXS ={
            "checkbox1":self._addElemt(name="checkbox1",width=80,height=10,
                                      action=self.checkbox1_cb,type="checkbox",icon=None,
                                      variable=self.addVariable("int",0)),
            "checkbox2":self._addElemt(name="checkbox2",width=80,height=10,
                                     action=self.checkbox2_cb,type="checkbox",icon=None,
                                     variable=self.addVariable("int",0)),
            "checkbox3":self._addElemt(name="checkbox3",width=80,height=10,
                                     action=self.checkbox3_cb,type="checkbox",icon=None,
                                     variable=self.addVariable("int",0))
                                     }
        self.BTN = {
            "button1":self._addElemt(name="button1",width=80,height=10,
                                      action=self.button1_cb,type="button",icon=None),
            "button2":self._addElemt(name="button2",width=80,height=10,
                                     action=self.button2_cb,type="button",icon=None),
            "close" : self._addElemt(name="close",width=80,height=10,
                                     action=self._close,type="button",icon=None),
                    }
        self.INPUT={
            "string":self._addElemt(name="string input",action=self.input_string_cb,
                                    width=50,value="enter a string",type="inputStr",
                                    variable=self.addVariable("str","test")),
            "int":self._addElemt(name="integer input",action=self.input_int_cb,
                                    width=50,value=0,type="inputInt",mini=0,maxi=10,
                                    variable=self.addVariable("int",0)),
            "float":self._addElemt(name="float input",action=self.input_float_cb,
                                    width=50,value=0.0,type="inputFloat",mini=0.,maxi=10.,
                                    variable=self.addVariable("float",0.0)),
        }
        self.LABEL_INPUT = {
            "string":self._addElemt(label="Enter a string",width=120),
            "int":self._addElemt(label="Enter a integer",width=120),
            "float":self._addElemt(label="Enter a float",width=120),
        }
        txt = "default text area"
        self.area = self._addElemt(id=id,name="TextArea",action=None,width=100,
                          value=txt,type="inputStrArea",
                          variable=self.addVariable("str",txt),height=100)
        
        self.SLIDERS={"slider1":self._addElemt(name="slider1",width=80,height=10,
                                             action=self.slider1_cb,type="slidersInt",label="slider 1",
                                             variable=self.addVariable("int",1),
                                             mini=0,maxi=20,step=1),#self.displayCPK},
                        "slider2":self._addElemt(name="slider2",width=80,height=10,
                                             action=self.slider2_cb,type="sliders",label="slider 2",
                                             variable=self.addVariable("float",1.0),
                                             mini=0.0,maxi=10.,step=0.01),#self.displayBS},
                    }
        self.COLFIELD = self._addElemt(id=id,name="chooseCol",action=self.color_cb,
                                       variable = self.addVariable("col",(0.,0.,0.)),
                                       type="color",width=30,height=15)
        self.vliste2 = ["choice1","choice2","choice3"]
        
        self._vliste1=self.addVariable("int",1)
        self._vliste2=self.addVariable("int",1)        
        self.COMB_BOX = {"menu1":self._addElemt(name="Liste1",value=["None"],
                                    width=60,height=10,action=self.liste1_cb,
                                    variable=self._vliste1,
                                    type="pullMenu"),#self.setCurMol
                         "menu2":self._addElemt(name="Liste2",
                                    value=self.vliste2,
                                    width=80,height=10,action=self.liste2_cb,
                                    variable=self._vliste2,
                                    type="pullMenu",),}
        #And the pop-up
    def _close(self,*args):
        self.close()

    def setupLayout(self):
        #this where we define the Layout
        #this wil make three button on a row
        typeLayout = "tab"
        self._layout = []
        #checkbox frame
        elemFrame1=[]
        elemFrame1.append([self.CHECKBOXS["checkbox1"],self.CHECKBOXS["checkbox2"],
                                   self.CHECKBOXS["checkbox3"]])
        frame1 = self._addLayout(id=100,name="CheckBox",elems=elemFrame1,type=typeLayout)
        self._layout.append(frame1)

        elemFrame1=[]
        elemFrame1.append([self.BTN["button1"],self.BTN["button2"],])
        frame1 = self._addLayout(id=110,name="Buttons",elems=elemFrame1,type=typeLayout)
        self._layout.append(frame1)

        elemFrame1=[]
        elemFrame1.append([self.LABEL_INPUT["string"],self.INPUT["string"]])
        elemFrame1.append([self.LABEL_INPUT["int"],self.INPUT["int"]])
        elemFrame1.append([self.LABEL_INPUT["float"],self.INPUT["float"]])
        frame1 = self._addLayout(id=120,name="Inputs",elems=elemFrame1,type=typeLayout)
        self._layout.append(frame1)

        elemFrame1=[]
        elemFrame1.append([self.area,])
        frame1 = self._addLayout(id=130,name="TextArea",elems=elemFrame1,type=typeLayout)
        self._layout.append(frame1)

        elemFrame1=[]
        elemFrame1.append([self.SLIDERS["slider1"],])
        elemFrame1.append([self.SLIDERS["slider2"],])
        frame1 = self._addLayout(id=140,name="Sliders",elems=elemFrame1,type=typeLayout)
        self._layout.append(frame1)

        elemFrame1=[]
        elemFrame1.append([self.COLFIELD,])
        frame1 = self._addLayout(id=150,name="Color",elems=elemFrame1,type=typeLayout)
        self._layout.append(frame1)

        elemFrame1=[]
        elemFrame1.append([self.COMB_BOX["menu1"],self.COMB_BOX["menu2"]])
        frame1 = self._addLayout(id=160,name="PullDown Menu",elems=elemFrame1,type=typeLayout)
        self._layout.append(frame1)
        self._layout.append([self.BTN["close"]])
#===============================================================================
#     Callback function
#===============================================================================   
    def checkbox1_cb(self,*args):
        #get the stat
        isCheck=self.getBool(self.CHECKBOXS["button1"])
        print("button1 ", isCheck)
                
    def checkbox2_cb(self,*args):
        #get the stat
        isCheck=self.getBool(self.CHECKBOXS["button2"])
        print("button2 ", isCheck)
        
    def checkbox3_cb(self,*args):
        #get the stat
        isCheck=self.getBool(self.CHECKBOXS["button3"])
        print("button3 ", isCheck)

    def recentfile_cb(self,*args):
        print("recent_file ",args, " args")
        print(args,self.submenu[str(args[0]-1)])

    def open_cb(self,*args):
        print("Open")
        
    def save_cb(self,*args):
        print("save_cb")
        
    def options_cb(self,*args):
        print("options")
    
    def drawAbout(self,*args):
        print("drawAbout")
        
    def drawHelp(self,*args):
        print("drawHelp")
        
    def checkbox1_cb(self,*args):
        #get the stat
        isCheck=self.getBool(self.CHECKBOXS["checkbox1"])
        print("checkbox1 ", isCheck)
#        self.drawMessage("button1 "+str(isCheck))
                
    def checkbox2_cb(self,*args):
        #get the stat
        isCheck=self.getBool(self.CHECKBOXS["checkbox2"])
        print("checkbox2 ", isCheck)
        
    def checkbox3_cb(self,*args):
        #get the stat
        isCheck=self.getBool(self.CHECKBOXS["checkbox3"])
        print("checkbox3 ", isCheck)

    def button1_cb(self,*args):
        print("button1 push")
                
    def button2_cb(self,*args):
        print("button2 push")
    
    def input_string_cb(self,*args):
        aStr=self.getString(self.INPUT["string"])
        print(aStr,type(aStr))
        
    def input_int_cb(self,*args):
        aInt=self.getLong(self.INPUT["int"])
        print(aInt,type(aInt))
        
    def input_float_cb(self,*args):
        aFloat=self.getReal(self.INPUT["float"])
        print(aFloat,type(aFloat))

    def slider1_cb(self,*args):
        aFloat=self.getReal(self.SLIDERS["slider1"])
        print(aFloat,type(aFloat))
        
    def slider2_cb(self,*args):
        aFloat=self.getReal(self.SLIDERS["slider2"])
        print(aFloat,type(aFloat))
        
    def color_cb(self,*args):
        col= self.getColor(self.COLFIELD)
        print(col)

    def liste1_cb(self,*args):
        #print args[0]
        i= self.getLong(self.COMB_BOX["menu1"])
        print(i,self.COMB_BOX["menu1"]["value"][i])
        
    def liste2_cb(self,*args):
        #print args[0]
        i=self.getLong(self.COMB_BOX["menu2"])
        print(i,self.COMB_BOX["menu2"]["value"][i])


print ("uiadaptor host is ",uiadaptor.host)
if uiadaptor.host == "tk":
    #from DejaVu import Viewer
    #vi = Viewer()    
    #require a master
    try :
        import tkinter #python3
    except :
        import Tkinter as tkinter
 
    root = tkinter.Tk()
    mygui = LayoutUI(master=root,title="LayoutUI-tk")
    #mygui.display()
elif uiadaptor.host == "qt":
    try :
        from PyQt4 import QtGui
    except :
        try :
            from PySide import QtGui
        except :
            print ("noQt support")
            exit()
    app = QtGui.QApplication(sys.argv)
    mygui = LayoutUI(title="LayoutUI-qt")
    #ex.show()
else :
    mygui = LayoutUI(title="LayoutUI_"+uiadaptor.host)
    #call it
mygui.setup()
mygui.display()
if uiadaptor.host == "qt": app.exec_()#work without it ?

##execfile("/Users/ludo/DEV/upy/trunk/upy/examples/layout.py")
##in Max python.executeFile  "upy/examples/layout.py"