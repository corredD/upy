
"""
    Copyright (C) <2010>  Autin L. TSRI
    
    This file git_upy/houdini/houdiniUI.py is part of upy.

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
Created on Wed Feb  9 11:19:17 2011

@author: -
"""
import os
import hou
from functools import partial
import pyubic
from pyubic.uiAdaptor import uiAdaptor

#UI general interface
#setTitle should create the Windows, even if no root ? but then no 3d viewer.
#check also pmv gui and arviwer for example.

class houdiniUI:
    """
    The houdini uiAdaptor abstract class
    ====================================
        This Adaptor give access to the basic ui script function need for 
        create and display a gui. Create the ui file and parse/populate it
    """

    host = "houdini"
    maxStrLenght=100
    scale = 2
#    topLine = 700
    bid=1
    MousePos = [0, 0]
    ScrollPos = 0
    ScrollState = 0
    ScrollInc = 25 
    dock = False
    #special function for subdialog and UIblock
    subdialog = False
    drawUIblock = False
    block = False
    w=300
    h=1
    #need a root
    master = None
    root=None
    root_store = None
    col=0#column
    row=0#row
    ncol=0#column
    nrow=0#row
    #need to store the form layout position
    nlayout=0
    uidialog = None
    uiStr = ""
    menuStr =""
    menusubstr=""
    filename = None
    varStr=""
    
    def close(self):
        self.uidialog.setValue("dialog",0)
        
    def Quit(self):
        """ Close the windows"""
        self.close()

    def CoreMessage(self, evt, val):
        pass

    def SetTitle(self,title):
        """ Initialised the windows and define the windows titles 
        @type  title: string
        @param title: the window title
        """
        if self.subdialog:
            self.uiStr='dial = DIALOG "%s"\n' % title 
        else :
            self.uiStr='dial = NORMAL_WINDOW "%s"{\n' % title
        self.uiStr+="LAYOUT(vertical) STRETCH MARGIN(0.1) SPACING(0.1) LOOK(plain) //EXCLUSIVE\n"
        self.uiStr+="VALUE(dialog) PREF_SIZE(%dp, %dp)\n" % (self.w,self.h)

            
    def createMenu(self,menuDic,menuOrder=None):
        """ Define and draw the window/widget top file menu
        @type  menuDic: dictionary
        @param menuDic: the menu elements, ie entry, callback and submenu
        @type  menuOrder: array
        @param menuOrder: the menu keys oredered
        """        
        #There is no Actual Menu in Blender, bu we can use the Pull Down Menu
        #subMenu: create a callback that create another PupMenu with the subvalue
        #this is the lastine...
        #the menu id is the first elem id
        if menuOrder : 
            lookat = menuOrder
        else :
            lookat = menuDic.keys()
        x=5
        #MENUBAR { menubaritems }
        #MENUBAR_ITEM "Label" MENU(staticmenuref); 
        self.uiStr+="MENUBAR {\n"
        #create var per item
        for mitem in lookat:
            self.menuStr+="%s = MENU{\n" % mitem.replace(" ","_")
            self.uiStr+='MENUBAR_ITEM "%s" MENU(%s);\n' %(mitem,mitem.replace(" ","_"))
            for elem in menuDic[mitem]:            
                if elem["sub"] is not None:
                    self.menusubstr+="%s= MENU{\n" % elem["name"].replace(" ","_")
                    self.menuStr+='MENU_ITEM_PARENT "%s" MENU(%s);\n' % (elem["name"],elem["name"].replace(" ","_"))
                    for sub in elem['sub']:
                        elem['sub'][sub]["variable"] = elem['sub'][sub]["name"].replace(" ","_")+".var"
                        self.menusubstr+='MENU_ITEM_ACTION "%s" VALUE(%s);\n' %(elem['sub'][sub]["name"],elem['sub'][sub]["variable"])
                    self.menusubstr+="}\n"
                else:
                    elem["variable"] = elem["name"].replace(" ","_")+".var"
                    self.menuStr+='MENU_ITEM_ACTION "%s" VALUE(%s);\n' %(elem["name"],elem["variable"])
            self.menuStr+="}\n"
        self.uiStr+='}\n'
        
    def handleMenuEvent(self,ev,menu):
        """ This function handle the particular menu event, especially for 
        submenu level action
        @type  ev: int
        @param ev: the current event
        @type  menu: dictionary
        @param menu: the current menu
        """  
        for mitem in menu:
            #get value of mitem
            val = self.uidialog.value(mitem)
            print mitem,val
            for elem in menu[mitem]:
                if elem["sub"] is not None:
                    val = self.uidialog.value(elem["name"].replace(" ","_"))
                    print elem["name"],val 
                    for sub in elem['sub']:
                        val = self.getLong(elem['sub'][sub])
                        print elem['sub'][sub]["name"],val
                else :
                    val = self.getLong(elem)
                    print elem["name"],val
        

    def addVariable(self,type,value):
        """ Create a container for storing a widget states """
#        if type == "int":
#            self.uiStr+="lod.val := 1.0;"
#        elif type == "float":
#            return Tkinter.DoubleVar(self.root)
#        elif type == "str":
#            return Tkinter.StringVar(self.root)
#        elif type == "bool":
#            return Tkinter.BooleanVar(self.root)
#        elif type == "col":
#            return [0,0,0]
        return None

    def startBlock(self,m=1,n=1):
        self.uiStr+="ROW\n{\n"
        
    def endBlock(self):
        self.uiStr+="}\n"
        
    def drawButton(self,elem,x,y,w=None,h=None):
        """ Draw a Button 
        @type  elem: dictionary
        @param elem: the button dictionary
        @type  x: int
        @param x: position on x in the gui windows
        @type  y: int
        @param y: position on y in the gui windows
        @type  w: int
        @param w: force the width of the item
        @type  h: int
        @param h: force the height of the item
        """
        print x,y,w,h,elem["height"],elem["width"]
        elem["variable"] = elem["name"].replace(" ","_")+".var"
        button = 'ACTION_BUTTON "%s" VALUE(%s) WIDTH(%dp)' %(elem["name"],elem["variable"],
            int(elem["width"]*self.scale))
        self.uiStr+=button+";\n"
        return button
#
#    def drawButtonToggle(self,elem,x,y,w=None,h=None):
#        """ Draw a checkBox 
#        @type  elem: dictionary
#        @param elem: the button dictionary
#        @type  x: int
#        @param x: position on x in the gui windows
#        @type  y: int
#        @param y: position on y in the gui windows
#        @type  w: int
#        @param w: force the width of the item
#        @type  h: int
#        @param h: force the height of the item
#        """     
#        w,h = self.checkwh(elem,w,h)
#        if self.subdialog :
#            elem["variable"]=self.check_addAction(Blender.Draw.Toggle,elem["action"],elem["name"],
#                                elem["id"], x, y, w,h,
#                                elem["variable"].val, 
#                                elem["tooltip"])
#        else :
#            elem["variable"]=Blender.Draw.Toggle(elem["name"], elem["id"], x, y, w,h,
#                                elem["variable"].val, 
#                                elem["tooltip"])

    def drawCheckBox(self,elem,x,y,w=None,h=None):
        elem["variable"] = elem["name"].replace(" ","_")+".var"
        button = 'TOGGLE_BUTTON "%s" VALUE(%s) WIDTH(%dp)' %(elem["name"],elem["variable"],
            int(elem["width"]*self.scale))
        self.uiStr+=button+";\n"
        return button
#
#    def resetPMenu(self,elem):
#        """ Add an entry to the given pulldown menu 
#        @type  elem: dictionary
#        @param elem: the pulldown dictionary
#        """
#        elem["value"]=[]
#        elem["variable"].val = len(elem["value"])
#
#    def addItemToPMenu(self,elem,item):
#        """ Add an entry to the given pulldown menu 
#        @type  elem: dictionary
#        @param elem: the pulldown dictionary
#        @type  item: string
#        @param item: the new entry
#        """
#        elem["value"].append(item)
#        elem["variable"].val = len(elem["value"])
#
    def PM_cb(self,w,elem,item):
        w.configure(text=item)
        #elem["variable"] = Tkinter.IntVar(self.root)
        elem["variable"].set(item)
        if elem["action"] is not None:
            elem["action"](elem,item)
        
    def drawPMenu(self,elem,x,y,w=None,h=None):
        """ Draw a pulldown menu 
        @type  elem: dictionary
        @param elem: the pulldown dictionary
        @type  x: int
        @param x: position on x in the gui windows
        @type  y: int
        @param y: position on y in the gui windows
        @type  w: int
        @param w: force the width of the item
        @type  h: int
        @param h: force the height of the item
        """
        elem["variable"] = elem["name"].replace(" ","_")+".var"
        self.menuStr+="%s = SELECT_MENU{\n" % elem["variable"]
        for x in elem["value"]:
            self.menuStr+='"'+x+'"\n'
        self.menuStr+="}\n"
        w="SELECT_MENU_BUTTON MENU(%s);" % elem["variable"]
        self.uiStr+=w+"\n"
        return w

#        
#    def drawText(self,elem,x,y,w=None,h=None):
#        """ Draw a Label
#        @type  elem: dictionary
#        @param elem: the label dictionary
#        @type  x: int
#        @param x: position on x in the gui windows
#        @type  y: int
#        @param y: position on y in the gui windows
#        @type  w: int
#        @param w: force the width of the item
#        @type  h: int
#        @param h: force the height of the item
#        """     
##        elem["width"] = len(elem["label"])* 3.
#        if type(elem) == str :
#            label = elem
#        else :
#            label =elem["label"]
#            w,h = self.checkwh(elem,w,h)
#        Blender.BGL.glRasterPos2i(x,y+5)
#        Blender.Draw.Text(label)
##        elem["width"] = len(elem["label"])* 3 #TODO find a more flexible solution
#
    def drawObj(self,elem,x,y,w=None,h=None):
        """ Draw an object input where you can drag on object 
        @type  elem: dictionary
        @param elem: the button dictionary
        @type  x: int
        @param x: position on x in the gui windows
        @type  y: int
        @param y: position on y in the gui windows
        @type  w: int
        @param w: force the width of the item
        @type  h: int
        @param h: force the height of the item
        """   
        pass


        """ Draw a Separative Line
        @type  elem: dictionary
        @param elem: the label dictionary
        @type  x: int
        @param x: position on x in the gui windows
        @type  y: int
        @param y: position on y in the gui windows
        @type  w: int
        @param w: force the width of the item
        @type  h: int
        @param h: force the height of the item
        """            
        if elem["value"] == "H":
            hr=True
        elif elem["value"] == "V":
            hr=False
        pass
        
    def drawLabel(self,elem,x,y,w=None,h=None):
        """ Draw a Label
        @type  elem: dictionary
        @param elem: the label dictionary
        @type  x: int
        @param x: position on x in the gui windows
        @type  y: int
        @param y: position on y in the gui windows
        @type  w: int
        @param w: force the width of the item
        @type  h: int
        @param h: force the height of the item
        """  
        w = 'LABEL "%s" WIDTH(%dp)' % (elem["label"],elem["width"])
        self.uiStr+=w+";\n"
        return w
        
    def drawString(self,elem,x,y,w=None,h=None):
        """ Draw a String input elem
        @type  elem: dictionary
        @param elem: the string input dictionary
        @type  x: int
        @param x: position on x in the gui windows
        @type  y: int
        @param y: position on y in the gui windows
        @type  w: int
        @param w: force the width of the item
        @type  h: int
        @param h: force the height of the item
        """  
        elem["variable"] = elem["name"].replace(" ","_")+".var"
        button = 'STRING_FIELD "%s" VALUE(%s) WIDTH(%dp)' %(elem["name"],elem["variable"],
            int(elem["width"]*self.scale))
        self.uiStr+=button+";\n"
        return button 

    def drawStringArea(self,elem,x,y,w=None,h=None):
        """ Draw a String Area input elem, ie multiline
        @type  elem: dictionary
        @param elem: the string area input dictionary
        @type  x: int
        @param x: position on x in the gui windows
        @type  y: int
        @param y: position on y in the gui windows
        @type  w: int
        @param w: force the width of the item
        @type  h: int
        @param h: force the height of the item
        """          
#        elem["variable"] = Tkinter.Text(self.root_frame,maxundo=100,
#                                width = int(elem["width"]*0.3),
#                                height = int(elem["height"]*0.15))
#        if elem["value"] is not None :
#            elem["variable"].insert(Tkinter.END,elem["value"])
#        else :
#            elem["variable"].insert(Tkinter.END,"")
#        elem["variable"].grid(row=self.row,column=self.col,sticky='w')
#        if elem["action"] is not None :
#            elem["variable"].bind('<Key-Return>',elem["action"])        
#        self.col = self.col +1
#        if self.col == self.ncol:
#            self.row = self.row +1 
#            self.col = 0
        return

    def drawNumbers(self,elem,x,y,w=None,h=None):
        """ Draw a Int input elem
        @type  elem: dictionary
        @param elem: the Int input dictionary
        @type  x: int
        @param x: position on x in the gui windows
        @type  y: int
        @param y: position on y in the gui windows
        @type  w: int
        @param w: force the width of the item
        @type  h: int
        @param h: force the height of the item
        """        
        print x,y,w,h,elem["height"],elem["width"]
        elem["variable"] = elem["name"].replace(" ","_")+".var"
        button = 'INT_FIELD "%s" VALUE(%s) WIDTH(%dp)' %(elem["name"],elem["variable"],
            int(elem["width"]*self.scale))
        self.uiStr+=button+";\n"
        return button

    def drawFloat(self,elem,x,y,w=None,h=None):
        """ Draw a Int input elem
        @type  elem: dictionary
        @param elem: the Int input dictionary
        @type  x: int
        @param x: position on x in the gui windows
        @type  y: int
        @param y: position on y in the gui windows
        @type  w: int
        @param w: force the width of the item
        @type  h: int
        @param h: force the height of the item
        """
        elem["variable"] = elem["name"].replace(" ","_")+".var"
        button = 'FLOAT_FIELD "%s" VALUE(%s) WIDTH(%dp)' %(elem["name"],elem["variable"],
            int(elem["width"]*self.scale))
        self.uiStr+=button+";\n"
        return button

    def drawError(self,errormsg=""):
        """ Draw a error message dialog
        @type  errormsg: string
        @param errormsg: the messag to display
        """  
        button_index = hou.ui.displayMessage( message,
                ("OK",),title = title,severity=hou.severityType.Error)
        return

    def drawQuestion(self,title,question=""):
        """ Draw a Question message dialog, requiring a Yes/No answer
        @type  title: string
        @param title: the windows title       
        @type  question: string
        @param question: the question to display
        
        @rtype:   bool
        @return:  the answer     
        """
        #questionDialog(self.root,title=title,question=question)
        button_index = hou.ui.displayMessage( question,
                ("Yes", "No",),
                default_choice = 0,
                title = title,severity=hou.severityType.Warning)
        return  not bool(button_index)#tkMessageBox.askyesno(title, question)
        
    def drawMessage(self,title="",message=""):
        """ Draw a message dialog
        @type  title: string
        @param title: the windows title       
        @type  message: string
        @param message: the message to display   
        """
        button_index = hou.ui.displayMessage( message,
                ("OK",),title = title,severity=hou.severityType.Message)
        return

#    def drawInputQuestion(self,title="",question="",callback=None):
#        """ Draw an Input Question message dialog, requiring a string answer
#        @type  title: string
#        @param title: the windows title       
#        @type  question: string
#        @param question: the question to display
#        
#        @rtype:   string
#        @return:  the answer     
#        """                  
#        result = Blender.Draw.PupStrInput(question, "", 100)
#        if result :
#            if callback is not None :
#                callback(result)
#            else :
#                return result
#
    def drawSliders(self,elem,x,y,w=None,h=None):
        """ Draw a Slider elem, the variable/value of the elem define the slider format
        @type  elem: dictionary
        @param elem: the slider input dictionary
        @type  x: int
        @param x: position on x in the gui windows
        @type  y: int
        @param y: position on y in the gui windows
        @type  w: int
        @param w: force the width of the item
        @type  h: int
        @param h: force the height of the item
        """
        elem["variable"] = elem["name"].replace(" ","_")+".var"
        #var for max iand mini?
        elem["variableminimaxi"]=elem["name"]+".minimaxi.var"
        self.varStr+="%s[0] = %gf\n" % (elem["name"]+".minimaxi.var",elem["mini"])
        self.varStr+="%s[1] = %gf\n" % (elem["name"]+".minimaxi.var",elem["maxi"])
        button = 'FLOAT_SLIDER_FIELD "%s" VALUE(%s) RANGEVALUE(%s:2) WIDTH(%dp)' %(elem["name"],elem["variable"],
            elem["variableminimaxi"], int(elem["width"]*self.scale))
        self.uiStr+=button+";\n"
        self.uiStr+="//%s[0] = %gf\n" % (elem["name"]+".minimaxi.var",elem["mini"])
        self.uiStr+="//%s[1] = %gf\n" % (elem["name"]+".minimaxi.var",elem["maxi"])
        return button

#        
#    def drawImage(self,elem,x,y,w=None,h=None):
#        """ Draw an Image, if the host supported it
#        @type  elem: dictionary
#        @param elem: the image input dictionary
#        @type  x: int
#        @param x: position on x in the gui windows
#        @type  y: int
#        @param y: position on y in the gui windows
#        @type  w: int
#        @param w: force the width of the item
#        @type  h: int
#        @param h: force the height of the item
#        """           
#        w,h = self.checkwh(elem,w,h)
#        img = Blender.Image.Load(elem["value"])
#        #we can add some gl call to make some transparency if we want
#        #Blender.BGL.glEnable( Blender.BGL.GL_BLEND ) # Only needed for alpha blending images with background.
#        #Blender.BGL.glBlendFunc(Blender.BGL.GL_SRC_ALPHA, Blender.BGL.GL_ONE_MINUS_SRC_ALPHA) 
#        #Blender.BGL.glDisable( Blender.BGL.GL_BLEND )
#        Blender.Draw.Image(img, x, y-h-10)#, zoomx=1.0, zoomy=1.0, clipx=0, clipy=0, clipw=-1, cliph=-1)
#
#    def ColorChooser_cb(self,elem):
#        (rgb, hexval)= askcolor(title="choose a Color")
#        elem["variable"] = rgb
#        elem["id"].config(bg=hexval,activebackground=hexval)
#        if elem["action"]:
#            elem["action"]()
#
    def drawColorField(self,elem,x,y,w=None,h=None):
        """ Draw a Color entry Field
        @type  elem: dictionary
        @param elem: the color input dictionary
        @type  x: int
        @param x: position on x in the gui windows
        @type  y: int
        @param y: position on y in the gui windows
        @type  w: int
        @param w: force the width of the item
        @type  h: int
        @param h: force the height of the item
        """ 
        #display the current color
        #and bind to the choose color
        elem["variable"] = elem["name"].replace(" ","_")+".var"
        button = 'COLOR_FIELD "%s" VALUE(%s) WIDTH(%dp)' %(elem["name"],elem["variable"],
            int(elem["width"]*self.scale))
        self.uiStr+=button+";\n"
        return button

    def drawFrame(self,bloc,x,y):
        """
        Function to draw a block as a collapsable frame layout of the gui. 
        
        @type  block: array or dictionary
        @param block: list or dictionary of item dictionary
        @type  x: int
        @param x: position on x in the gui windows, used for blender
        @type  y: int
        @param y: position on y in the gui windows, used for blender
        
        @rtype:   int
        @return:  the new horizontal position, used for blender
        """            
        if bloc["collapse"] :
            collapse = 0
        else :
            collapse = 1
            
        self.uiStr+='COLLAPSER  "%s" { \n' % bloc["name"]
        self.uiStr+='VALUE(%s)  LAYOUT(vertical) STRETCH MARGIN(0.1) SPACING(0.1) LOOK(plain) //EXCLUSIVE\n' % bloc["name"].replace(" ","_")
        for k,blck in enumerate(bloc["elems"]):
            self.startBlock(m=len(blck))
            for index, item in enumerate(blck):
                self._drawElem(item,x,y)
            self.endBlock()
        self.endBlock()
        return y   

#    def frame_cb(self,bloc):
#        print bloc["name"]
#        bloc["collapse"] = bloc["variable"].get()
#        print bloc["collapse"]
#        bloc["id"].destroy()
#        self.Frame(bloc,0,0)
##        bloc["id"].update()
#        self.root_frame.update()
#        
#    def drawFrame(self,bloc,x,y):
#        """
#        Function to draw a block as a collapsable frame layout of the gui. 
#        
#        @type  block: array or dictionary
#        @param block: list or dictionary of item dictionary
#        @type  x: int
#        @param x: position on x in the gui windows, used for blender
#        @type  y: int
#        @param y: position on y in the gui windows, used for blender
#        
#        @rtype:   int
#        @return:  the new horizontal position, used for blender
#        """            
#        bloc["variable"] = Tkinter.IntVar(self.root)
#        bloc["labelwidget"] = Tkinter.Checkbutton(self.root,
#                                              text = bloc["name"],
#                                              command = partial(self.frame_cb,bloc),
#                                              variable = bloc["variable"])
#        bloc["variable"].set(1)
#        bloc["nlayout"] = self.nlayout
#        self.nlayout = self.nlayout + 1
#        self.Frame(bloc,x,y)
##        self.LayoutChanged(bloc["id"])
#        return y
#
#    def Frame(self,bloc,x,y):
#        self.root_store = self.root_frame
#        bloc["id"] = self.root_frame = Tkinter.LabelFrame(self.root_frame, text=bloc["name"], 
#                                             padx=5, pady=5,labelwidget=bloc["labelwidget"],
#                                            height = int(bloc["height"]*self.scale),
#                                            width = int(bloc["width"]*self.scale))
#
#        #self.root_frame.pack(padx=10, pady=10)
#        self.root_frame.grid(sticky='w',row=bloc["nlayout"])  
#        if bloc["collapse"] :
#            self.startBlock(n=len(bloc["elems"]))#,m=len(blck))
#            for k,blck in enumerate(bloc["elems"]):
#                self.ncol=len(blck)
#                print "grid ",self.nrow,self.ncol
#                for index, item in enumerate(blck):
#                #print index,item
#                    self._drawElem(item,0,0)
#            self.endBlock()
#        else :
#            w=Tkinter.Label(self.root_frame,width=bloc["width"])
#            w.pack()        
#        self.root_frame = self.root_store
#        

#    def UpdateMenuData(self,blocklayout):
#        """ special to update the frame layout """
##        global ButtonData, Filters
#        selection       = ""
#        
#        if blocklayout is not None:
##            ArrayItem   = ButtonData[ArrayIndex]
#            #Figure Buttons
#            for index, item in enumerate(blocklayout["elems"]):
#                buttonCount = len(blocklayout["elems"])
#                if (buttonCount and index > buttonCount): break 
#                #If buttonCount is specified stop drawing button list past count
#                if (item["show"] == True): #Is button set to show
#                    if (item["type"] == "pullMenu"): 
#                        pass

#    def fileDialog(self,label="",callback=None):
#        """ Draw a File input dialog
#        @type  label: string
#        @param label: the windows title       
#        @type  callback: function
#        @param callback: the callback function to call
#        """            
#        Blender.Window.FileSelector (callback, label)
#
#    def waitingCursor(self,toggle):
#        """ Toggle the mouse cursor appearance from the busy to idle.
#        @type  toggle: Bool
#        @param toggle: Weither the cursor is busy or idle 
#        """             
#        Blender.Window.WaitCursor(toggle)
#
    def getString(self,elem):
        """ Return the current string value of the String Input elem
        @type  elem: dictionary
        @param elem: the elem input dictionary       
        
        @rtype:   string
        @return:  the current string input value for this specific elem
        """                
        return self.uidialog.value(elem["variable"])

    def setString(self,elem,val):
        """ Set the current String value of the string input elem
        @type  elem: dictionary
        @param elem: the elem input dictionary       
        @type  val: string
        @param val: the new string value    
        """                
        self.uidialog.setValue(elem["variable"],val)

    def getStringArea(self,elem):
        """ Return the current string area value of the String area Input elem
        @type  elem: dictionary
        @param elem: the elem input dictionary       
        
        @rtype:   string
        @return:  the current string area input value for this specific elem
        """                
        return self.uidialog.value(elem["variable"])

    def SetStringArea(self,elem,val):
        """ Set the current String area value of the string input elem
        @type  elem: dictionary
        @param elem: the elem input dictionary       
        @type  val: string
        @param val: the new string value (multiline)   
        """   
        self.uidialog.setValue(elem["variable"],val)
        
    def getLong(self,elem):
        """ Return the current Int value of the Input elem
        @type  elem: dictionary
        @param elem: the elem input dictionary       
        
        @rtype:   Int
        @return:  the current Int value input for this specific elem
        """
        return self.uidialog.value(elem["variable"])
        
    def setLong(self,elem,val):
        """ Set the current Int value of the Int input elem
        @type  elem: dictionary
        @param elem: the elem input dictionary       
        @type  val: Int
        @param val: the new Int value
        """                        
        self.uidialog.setValue(elem["variable"],val)

    def getReal(self,elem):
        """ Return the current Float value of the Input elem
        @type  elem: dictionary
        @param elem: the elem input dictionary       
        
        @rtype:   Float
        @return:  the current Float value input for this specific elem
        """       
        return self.uidialog.value(elem["variable"])

    def setReal(self,elem,val):
        """ Set the current Float value of the Float input elem
        @type  elem: dictionary
        @param elem: the elem input dictionary       
        @type  val: Float
        @param val: the new Float value
        """                                
        self.uidialog.setValue(elem["variable"],val)

    def getBool(self,elem):
        """ Return the current Bool value of the Input elem
        @type  elem: dictionary
        @param elem: the elem input dictionary       
        
        @rtype:   Bool
        @return:  the current Bool value input for this specific elem
        """                        
        return self.uidialog.value(elem["variable"])
        
    def setBool(self,elem,val):
        """ Set the current Bool value of the Bool input elem
        @type  elem: dictionary
        @param elem: the elem input dictionary       
        @type  val: Bool
        @param val: the new Bool value
        """                        
        self.uidialog.setValue(elem["variable"],val)

    def getColor(self,elem):
        """ Return the current Color value of the Input elem
        @type  elem: dictionary
        @param elem: the elem input dictionary       
        
        @rtype:   Color
        @return:  the current Color array RGB value input for this specific elem
        """        
        return self.uidialog.value(elem["variable"])

    def setColor(self,elem,val):
        """ Set the current Color rgb arrray value of the Color input elem
        @type  elem: dictionary
        @param elem: the elem input dictionary       
        @type  val: Color
        @param val: the new Color value
        """     
        self.uidialog.setValue(elem["variable"],val)
        

    def updateSlider(self,elem,mini,maxi,default,step):
        """ Update the state of the given slider, ie format, min, maxi, step
        @type  elem: dictionary
        @param elem: the slider elem dictionary       
        @type  maxi: int/float
        @param maxi: max value for the item, ie slider
        @type  mini: int/float
        @param mini: min value for the item, ie slider
        @type  default: int/float
        @param default: default value for the item, ie slider
        @type  step: int/float
        @param step: step value for the item, ie slider
        """        
        self.uidialog.setValue(elem["variable"],float(default))
        #self.uidialog.setValue(elem["variableminimaxi"],[float(mini),float(maxi)])
        
    def _restore(self,rkey,dkey=None):
        """
        Function used to restore the windows data, usefull for plugin
        @type  rkey: string
        @param rkey: the key to access the data in the registry/storage       
        @type  dkey: string
        @param dkey: wiether we want a particular data from the stored dic
        """
        if hasattr(hou,rkey):
            obj = hou.__dict__[rkey]
            if dkey is not None:
                if hou.__dict__[rkey].has_key(dkey) :
                    return  hou.__dict__[rkey][dkey]       
                else :
                    return None
            return obj
        else :
            return None

    def _store(self,rkey,dict):
        """
        Function used to store the windows data, usefull for plugin
        @type  rkey: string
        @param rkey: the key to access the data in the registry/storage       
        @type  dict: dictionary
        @param dict: the storage is done throught a dictionary
        """         
        hou.__dict__[rkey]= dict
#
#
#    def drawSubDialogUI(self):
#        Blender.Draw.UIBlock(self._createLayout, mouse_exit=0)
#
    def drawSubDialog(self,dial,id,callback=None):
        """
        Draw the given subdialog whit his own element and callback
        
        @type  dial: dialog Object
        @param dial: the dialog object to be draw
        @type  id: int
        @param id: the id of the dialog
        @type  callback: function
        @param callback: the associate callback
        """        
        #dial is an object
        dial.display()

    def startLayout(self):
        self.uiStr+="TOOLSCROLLER{\n"
        self.uiStr+="LAYOUT(vertical) VSTRETCH\n"
#
    def endLayout(self):
        self.uiStr+="}\n}\n" 

    def display(self):
        """ Create and Open the current gui windows """
        self.CreateLayout()
        #parse the ui file
        if self.filename is None :
            self.filename = pyubic.__path__[0]+os.sep+self.title+".ui"
        f = open(self.filename,"w")
        #f.write(self.varStr)
        f.write(self.menusubstr)
        f.write(self.menuStr)
        f.write(self.uiStr)
        f.close()
        if self.uidialog is None :
            self.uidialog = hou.ui.createDialog(self.filename)
            #populate with value and callback
            for block in self._layout:
                if type(block) is list : #one line
                    for elem in block:
                        if elem["type"] == "sliders":
                            self.updateSlider(elem,elem["mini"],elem["maxi"],
                                            elem["value"],0.1)
                        if elem["action"] is not None :
                            self.uidialog.addCallback(elem["variable"],elem["action"])
                else : #dictionary: multiple line / format dict?
                    if block.has_key("0"):
                        for i in range(1,len(block)):
                            for elem in block[str(i)]:
                                if elem["action"] is not None :
                                    self.uidialog.addCallback(elem["variable"],elem["action"])
                    else : #frame -> check collapse statute
                        self.uidialog.setValue(block["name"].replace(" ","_"),int(block["collapse"]))
                        for k,blck in enumerate(block["elems"]):
                            for index, elem in enumerate(blck):
                                if elem["action"] is not None :
                                    self.uidialog.addCallback(elem["variable"],elem["action"])
            #populate file menu if any with callback
            if self.MENU_ID:
                for mitem in self.MENU_ID:
                    for elem in self.MENU_ID[mitem]:
                        if elem["sub"] is not None:
                            for sub in elem['sub']:
                                if elem['sub'][sub]["action"] is not None :
                                    #print elem['sub'][sub]["variable"],elem['sub'][sub]["action"],elem['sub'][sub]["name"]
                                    self.uidialog.addCallback(elem['sub'][sub]["variable"],
                                    partial(elem['sub'][sub]["action"],elem['sub'][sub]["name"]))
                        else :
                            if elem["action"] is not None :
                                self.uidialog.addCallback(elem["variable"],elem["action"])
        #show it
        self.uidialog.setValue("dialog",1)
        #self.uidialog.waitForValueToChangeTo("dialog", 0)
        
class houdiniUIDialog(houdiniUI,uiAdaptor):
    def __init__(self,master=None):
        pass
#
#class blenderUISubDialog(blenderUIDialog):
#    def __init__(self,name):
#        blenderUIDialog.__init__(self,)
#        #a subdialog is a popup
#        self.name = name
#        self.elems = []
#        self.result = None
#    
#    def draw(self):
#        self.result = Blender.Draw.PupBlock(self.name, self.elems)
#


