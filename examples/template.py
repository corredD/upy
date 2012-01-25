# -*- coding: utf-8 -*-
"""
Created on Thu Feb 17 10:23:24 2011

@author: -
"""
#example for a script not a plugin ....

import sys,os
#pyubic have to be in the pythonpath, if not add it
pathtoupy = "/Users/ludo/DEV/"
sys.path.insert(0,pathtoupy)

import upy
upy.setUIClass()
from upy import uiadaptor

#get the CGhelper
helperClass = upy.getHelperClass()



class template(uiadaptor):
    def setup(self):
        self.w = 200 
        #define all the widget we want
        self.initWidget(id=10)
        #setup the layout organisation of the define widget
        self.setupLayout()
        #is it a subwindow
        self.subdialog = Flase
        
    #theses two function are for c4d and shouldnt be changed
    def CreateLayout(self):
        self._createLayout()
        return 1

    def Command(self,*args):
#        print args
        self._command(args)
        return 1
        
    def initWidget(self,id=None):
        #this where we define the fileMenu and the required buttons/widgets
        #if you want a menu use theses two variable :
        #self.menuorder which define the order of appearance of the menu item
        #self.MENU_ID that actually define the menu item
        #you can use a subemnu dictionary
        self.menuorder = ["File","Edit","Help"]
        self.submenu = {}
        for i in range(10):
            self.submenu[str(self.id-1)]=self._addElemt(name="file"+str(i),
                                                        action=self.recentfile_cb)
        #menu are always define by the MENU_ID dictionary and the self.menuorder
        self.MENU_ID={"File":
                      [self._addElemt(name="Recent Files",action=None,sub=self.submenu),
                      self._addElemt(name="Open",action=self.open_cb),
                      self._addElemt(name="Save",action=self.save_cb),
                      self._addElemt(name="Exit",action=self.close)],
                       "Edit" :
                      [self._addElemt(name="Options",action=self.options_cb)],
                       "Help" : 
                      [self._addElemt(name="About",action=self.drawAbout),#self.drawAbout},
                       self._addElemt(name="Help",action=self.drawHelp),#self.launchBrowser},
                      ],
                       }
        #now add your widget in any order...
        #check the layout.py exemple where most of the supported widget are presented
        
    def setupLayout(self):
        #this where we define the Layout
        #we currently have two type of layout : rawlayout and framelayout
        #rowlayout :
        #self._layout.append([widget1,]) #first lign 1 column
        #self._layout.append([widget2,widget3]) #second lign 2 column
        #etc...
        #framelayout : 
        #frame_elem = [[widget1,],          #first line in the frame
        #          [widget2,widget3]]  #second line in the frame
        #frame = self._addLayout(id=100,name="frame",elems=frame_elem) #default is collapsable frame
        #self._layout.append(frame)
        self._layout = []

#===============================================================================
#     Callback function
#===============================================================================
    #place here your callback function
    #check the example
    #to close simply call self.close()



#===============================================================================
#    __main__ : just replace 'template' by your class name and mygui by a name
#    of your choice
#===============================================================================
if uiadaptor.host == "tk":
    #from DejaVu import Viewer
    #vi = Viewer()    
    #require a master
    import tkinter
    root = tkinter.Tk()
    mygui = template(master=root,title="templateUI")
    #mygui.display()
elif uiadaptor.host == "qt":
    from PyQt4 import QtGui
    app = QtGui.QApplication(sys.argv)
    mygui = template(title="templateUI")
    #ex.show()
else :
    mygui = template(title="templateUI")
    #call it
mygui.setup()
mygui.display()
if uiadaptor.host == "qt": app.exec_()#work without it ?

#===============================================================================
# How to run
# in C4D : execfile("/Library/MGLTools/1.5.6.up/MGLToolsPckgs/pyubic/examples/layout.py")
# in Blender : open the file in the Text editor and Run Python Script
# in maya open in script command windows and execute the script
# in dejavuTK : run MGLTools/bin/pythonsh -i template.py Or use execfile
#===============================================================================