# -*- coding: utf-8 -*-
"""
Created on Wed Dec 29 13:09:18 2010

@author: Ludovic Autin
"""

#example for a script not a plugin ....
import sys
#pyubic have to be in the pythonpath, if not add it
pathtoupy = "/Users/ludo/DEV/"
sys.path.insert(0,pathtoupy)

import upy
upy.setUIClass("qt")
#this will automatically recognize the host and define the class uiadaptor
#from upy.pythonUI.qtUI import qtUIDialog as uiadaptor
from upy import uiadaptor
#but you can directly import the one you want like :
#from pyubic.dejavuTk.tkUI import tkUIDialog as uiadaptor
#from pyubic.blender.blenderUI import blenderUIDialog as uiadaptor
print (upy)
print (uiadaptor)
print (uiadaptor.__init__)
class simpleButtonsGUI(uiadaptor):

    def setup(self):
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

    def button1_cb(self,*args):
        #get the stat
        isCheck=self.getBool(self.CHECKBOXS["button1"])
        print("button1 ", isCheck)
#        self.drawMessage("button1 "+str(isCheck))
                
    def button2_cb(self,*args):
        #get the stat
        isCheck=self.getBool(self.CHECKBOXS["button2"])
        print("button2 ", isCheck)
        
    def button3_cb(self,*args):
        #get the stat
        isCheck=self.getBool(self.CHECKBOXS["button3"])
        print("button3 ", isCheck)

    def okButton(self,*args):
        print("ok")
        result= ""
        #overall state 
        isCheck=self.getBool(self.CHECKBOXS["button1"])
        result +="button1 "+str(isCheck)+"\n"
        isCheck=self.getBool(self.CHECKBOXS["button2"])
        result +="button2 "+str(isCheck)+"\n"
        isCheck=self.getBool(self.CHECKBOXS["button3"])
        result +="button3 "+str(isCheck)+"\n"
        self.drawMessage(title="myGuiResult",message=result)
            
    def quitButton(self,*args):
        answer = self.drawQuestion("Quit",question="Are You sure?")
        if answer :
            self.close()
        
    def initWidget(self,id=None):
        #this where we define the buttons
        self.CHECKBOXS ={
            "button1":self._addElemt(id=id,name="button1",width=80,height=10,
                                      action=self.button1_cb,type="checkbox",icon=None,
                                      variable=self.addVariable("int",0)),
            "button2":self._addElemt(id=id+1,name="button2",width=80,height=10,
                                     action=self.button2_cb,type="checkbox",icon=None,
                                     variable=self.addVariable("int",0)),
            "button3":self._addElemt(id=id+2,name="button3",width=80,height=10,
                                     action=self.button3_cb,type="checkbox",icon=None,
                                     variable=self.addVariable("int",0))
                                     }
        id = id + len(self.CHECKBOXS)
        self.PUSHS = {}
        self.PUSHS["OK"] = self._addElemt(id=id,name="OK",width=80,height=10,
                                     action=self.okButton,type="button",icon=None,
                                     variable=self.addVariable("int",0))
        self.PUSHS["QUIT"] = self._addElemt(id=id+1,name="QUIT",width=80,height=10,
                                     action=self.quitButton,type="button",icon=None,
                                     variable=self.addVariable("int",0))
        
    def setupLayout(self):
        #this where we define the Layout
        #this wil make three button on a row
        self._layout = []
        self._layout.append([self.CHECKBOXS["button1"],self.CHECKBOXS["button2"],self.CHECKBOXS["button3"]])
        self._layout.append([self.PUSHS["OK"],self.PUSHS["QUIT"]])

if uiadaptor.host == "tk":
    #from DejaVu import Viewer
    #vi = Viewer()    
    #require a master
    try :
        import tkinter
    except :
        import Tkinter as tkinter
    root = tkinter.Tk()
    mygui = simpleButtonsGUI(master=root,title="buttonsUI")
    #mygui.display()
elif uiadaptor.host == "qt":
    from PySide import QtGui
    app = QtGui.QApplication(sys.argv)
    mygui = simpleButtonsGUI(title="buttonsUI")
    #ex.show()
else :
    mygui = simpleButtonsGUI(title="buttonsUI")
    #call it
mygui.setup()
mygui.display()
if uiadaptor.host == "qt": app.exec_()

##execfile("/Users/ludo/DEV/pyubic/examples/simpleButtons.py")
