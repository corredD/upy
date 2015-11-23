
"""
    Copyright (C) <2010>  Autin L. TSRI
    
    This file git_upy/cinema4d/r12/c4dUI.py is part of upy.

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
Created on Thu Dec  2 18:17:17 2010

@author: -
"""

# -*- coding: utf-8 -*-
"""
Created on Thu Dec  2 13:45:52 2010

@author: -
"""
import sys,os
import c4d
from c4d import plugins
from c4d import utils
from c4d import bitmaps
from c4d import gui

import random

from upy.uiAdaptor import uiAdaptor

#UI general interface
class c4dUI(gui.GeDialog):
    """
    The cinema4d uiAdaptor abstract class
    ====================================
        This Adaptor give access to the basic cinema4d Draw function need for 
        create and display a gui.
    """
    
    host = "c4d"
    scale = 1
    maxStrLenght=100
    left, top, right, bottom =(25,1,1,1)
    oid=1005
    bid=1005
    id = 1005
    plugid = int(random.random()*10000000)
    dock = False
    w=100
    h=100
    tab=False
    notebook = None
    ystep = 0
    scrolling = False
    
    def addVariablePropToSc (self, *args):
        #ghost function 
        pass
    
    def CoreMessage(self, id, msg):
        """ Hanlde the system event such as key or mouse position """
#        print "coremessage"
#        print "id",id
#        print "msg",msg
        return True
        #-1008
        #20000000073

    def _setTitle(self,title):
        self.SetTitle(title)
        
    def createMenu(self,menuDic,menuOrder=None):
        """ Define and draw the window/widget top file menu
        @type  menuDic: dictionary
        @param menuDic: the menu elements, ie entry, callback and submenu
        @type  menuOrder: array
        @param menuOrder: the menu keys oredered
        """                
        if menuOrder : 
            lookat = menuOrder
        else :
            lookat = menuDic.keys()
        self.MenuFlushAll()
        for mitem in lookat:
            self.MenuSubBegin(mitem)
            for elem in menuDic[mitem]:            
                if elem["sub"] is not None:
                    self.MenuSubBegin(elem["name"])
                    for sub in elem['sub']:
                        self.MenuAddString(elem['sub'][sub]["id"],
                                        elem['sub'][sub]["name"])
                    self.MenuSubEnd()
                else:
                    self.MenuAddString(elem["id"],elem["name"])
            self.MenuSubEnd()
        self.MenuFinished()

    def handleMenuEvent(self,ev,menu):
        """ This function handle the particular menu event, especially for 
        submenu level action
        @type  ev: int
        @param ev: the current event
        @type  menu: dictionary
        @param menu: the current menu
        """    
        #verify Enter?
        print "menu",ev
        if ev == 1056 : 
            return
        for menuId in menu.keys():
            for elem in menu[menuId]:
                if elem["sub"] is not None:
                    for sub in elem['sub'].keys():
                        #print ev,elem['sub'][sub]["id"]
                        if ev == elem['sub'][sub]["id"] :
                            #print elem['sub'][sub]
                            if self._timer : 
                                self.timeFunction(elem['sub'][sub]["action"],ev)
                            else : 
                                self.callbackaction(elem['sub'][sub],ev)                       
                else :
                    if ev==elem["id"] :
                        if self._timer : 
                            self.timeFunction(elem["action"],ev)
                        else : 
                            self.callbackaction(elem,ev)

    def addVariable(self,type,value):
        """ Create a container for storing a widget states """
        return value

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
        #elem["id"] = gui.LinkBoxGui()
        

    def getFlagAlignement(self,options):
        alignement = {"hleft_scale":c4d.BFH_LEFT|c4d.BFH_SCALE| c4d.BFV_MASK,
                  "hcenter_scale":c4d.BFH_CENTER|c4d.BFH_SCALE| c4d.BFV_MASK,
                  "hleft":c4d.BFH_LEFT| c4d.BFV_MASK,
                  "hfit":c4d.BFH_FIT| c4d.BFV_MASK,
                  "hfit_scale":c4d.BFH_SCALEFIT| c4d.BFV_MASK,
                  "hcenter":c4d.BFH_CENTER| c4d.BFV_MASK,
                  }
        if type(options) is int or options not in alignement :
            return options
        return alignement[options]

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
        if elem["alignement"] is None :
            elem["alignement"] = c4d.BFH_CENTER | c4d.BFV_MASK
        name = elem["name"]
        if elem["label"] != None:
            name = elem["label"]
        self.AddButton(id=elem["id"], flags=elem["alignement"],
                            initw=elem["width"]*self.scale,
                            inith=elem["height"]*self.scale,
                            name=name)

    def drawCheckBox(self,elem,x,y,w=None,h=None):
        """ Draw a checkBox 
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
        if elem["alignement"] is None :
            elem["alignement"] = c4d.BFH_CENTER | c4d.BFV_MASK    
        name = elem["name"]
        if elem["label"] != None:
            name = elem["label"]
        self.AddCheckbox(id=elem["id"],flags=elem["alignement"],#BFH_SCALEFIT,
                                name=name,
                                initw=elem["width"]*self.scale,
                                inith=elem["height"]*self.scale)
        if elem["value"] is not None :
            self.SetBool(elem["id"],elem["value"])
        
                                
    def resetPMenu(self,elem):
        """ Add an entry to the given pulldown menu 
        @type  elem: dictionary
        @param elem: the pulldown dictionary
        """
        elem["value"]=[]
        self.FreeChildren(elem["id"])

    def addItemToPMenu(self,elem,item):
        """ Add an entry to the given pulldown menu 
        @type  elem: dictionary
        @param elem: the pulldown dictionary
        @type  item: string
        @param item: the new entry
        """        
        self.AddChild(elem["id"],len(elem["value"]),item)
        elem["value"].append(item)
        self.SetLong(elem["id"],len(elem["value"])-1)

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
        if elem["alignement"] is None :
            elem["alignement"] = c4d.BFH_LEFT|c4d.BFH_SCALEFIT

        self.AddComboBox(id=elem["id"],flags=elem["alignement"],                            
                         initw=elem["width"]*self.scale)
#                         inith=elem["height"]*self.scale)
        [self.AddChild(elem["id"],x[0],x[1]) for x in enumerate(elem["value"])]

    def drawLine(self,elem,x,y,w=None,h=None):
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
            self.AddSeparatorH(self.w,flags=c4d.BFH_SCALEFIT | c4d.BFV_MASK)
        elif elem["value"] == "V":
            self.AddSeparatorV(self.w,flags=c4d.BFH_SCALEFIT | c4d.BFV_MASK)
            
    def drawLabel(self,label,x,y,w=None,h=None):
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
        if label["alignement"] is None :
            label["alignement"] = c4d.BFH_CENTER | c4d.BFV_MASK
        self.AddStaticText(label["id"],flags=label["alignement"])#BFH_SCALEFIT)#|c4d.BFV_SCALEFIT)#c4d.BFH_LEFT)c4d.BFH_LEFT|
        self.SetString(label["id"],label["label"])

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
        if elem["alignement"] is None :
            elem["alignement"] = c4d.BFH_CENTER | c4d.BFV_MASK
        self.AddMultiLineEditText(id=elem["id"],
                            flags=elem["alignement"],
                            initw=elem["width"]*self.scale,
                            inith=elem["height"]*self.scale,                              
                            style=c4d.DR_MULTILINE_SYNTAXCOLOR)
        self.SetString(elem["id"],elem["value"])

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
        if elem["alignement"] is None :
            elem["alignement"] = c4d.BFH_CENTER | c4d.BFV_MASK
        self.AddEditText(id=elem["id"], 
                            flags=elem["alignement"],#| c4d.BFV_MASK,#BFH_CENTER
                            initw=elem["width"]*self.scale,
                            inith=elem["height"]*self.scale)
        self.SetString(elem["id"],elem["value"])

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
        if elem["alignement"] is None :
            elem["alignement"] = c4d.BFH_CENTER | c4d.BFV_MASK
        self.AddEditSlider(id=elem["id"], 
                            flags=elem["alignement"],
                            initw=elem["width"]*self.scale,
                            inith=elem["height"]*self.scale)
        self.SetReal(elem["id"],float(elem["variable"]),float(elem["mini"]),  
                    float(elem["maxi"]), float(elem["step"]))

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
        if elem["alignement"] is None :
            elem["alignement"] = c4d.BFH_CENTER | c4d.BFV_MASK
        if elem["value"] is None :
            elem["value"] = elem["variable"]
        self.AddEditNumberArrows(id=elem["id"], 
                            flags=elem["alignement"],
                            initw=elem["width"]*self.scale,
                            inith=elem["height"]*self.scale)
        self.SetLong(elem["id"],int(elem["value"]),int(elem["mini"]),
                                    int(elem["maxi"]))

    def drawFloat(self,elem,x,y,w=None,h=None):
        """ Draw a float input elem
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
        if elem["alignement"] is None :
            elem["alignement"] = c4d.BFH_CENTER | c4d.BFV_MASK
        if elem["value"] is None :
            elem["value"] = elem["variable"]
        if elem["value"] is None :
            elem["value"] =0.0
        if elem["maxi"] is None :
            elem["maxi"] =0.0
        if elem["mini"] is None :
            elem["mini"] =0.0            
        #print (elem["name"],elem["value"],elem["variable"],type(elem["variable"]),type(elem["value"]))
        self.AddEditNumberArrows(id=elem["id"], 
                            flags=elem["alignement"],
                            initw=elem["width"]*self.scale,
                            inith=elem["height"]*self.scale)
        #print float(elem["value"]),float(elem["mini"]),float(elem["maxi"])
        self.SetReal(elem["id"],float(elem["value"]),float(elem["mini"]),
                                    float(elem["maxi"]))

    def drawImage(self,elem,x,y,w=None,h=None):
        """ Draw an Image, if the host supported it
        @type  elem: dictionary
        @param elem: the image input dictionary
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
#       bmp = c4d.bitmaps.BaseBitmap()
#        bmp.InitWith(elem["value"])
#        bc = c4d.BaseContainer()
        #        need to use userarea
#        area = c4d.gui.GeUserArea()        
#        self.AddUserArea(5000,flags=c4d.BFH_SCALEFIT,initw=100, inith=150)
#        self.AttachUserArea(area, id=10, userareaflags=c4d.USERAREA_COREMESSAGE)
#        self.area.DrawBitmap(bmp, 0, 0, 396, 60, 0, 0, 396, 60, mode=c4d.BMP_NORMALSCALED)#396 × 60
##        self.area.DrawText('welcome to ePMV '+__version__, 0, 0, flags=c4d.DRAWTEXT_STD_ALIGN)
#        self.area.Init()
#        self.area.InitValues()

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
        if elem["alignement"] is None :
            elem["alignement"] = elem["alignement"]
#        print elem
        self.AddColorField(id=elem["id"],flags=elem["alignement"],
                            initw=elem["width"]*self.scale,
                            inith=elem["height"]*self.scale)
        if elem["value"]is not None:
#            print "v",elem["value"]
            self.setColor(elem,elem["value"])
#            print "n",elem["name"]
                                                    
    def drawError(self,errormsg=""):
        """ Draw a error message dialog
        @type  errormsg: string
        @param errormsg: the messag to display
        """          
        c4d.gui.MessageDialog("ERROR: "+errormsg)
 
    def drawQuestion(self,title="",question="",callback=None):
        """ Draw a Question message dialog, requiring a Yes/No answer
        @type  title: string
        @param title: the windows title       
        @type  question: string
        @param question: the question to display
        
        @rtype:   bool
        @return:  the answer     
        """
        res = c4d.gui.QuestionDialog(question)
        if  callback is not None :           
            callback(res)
        else :
            return res
            
    def drawMessage(self,title="",message=""):
        """ Draw a message dialog
        @type  title: string
        @param title: the windows title       
        @type  message: string
        @param message: the message to display   
        """                    
        c4d.gui.MessageDialog(message)

    def drawInputQuestion(self,title="",question="",callback=None):
        """ Draw an Input Question message dialog, requiring a string answer
        @type  title: string
        @param title: the windows title       
        @type  question: string
        @param question: the question to display
        
        @rtype:   string
        @return:  the answer     
        """                  
        result = c4d.gui.InputDialog(question,"")
        if result :
            if callback is not None :
                callback(result)
            else :
                return result

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
        grFlag  = c4d.BFH_SCALEFIT |c4d.BFV_MASK
        if bloc["scrolling"]:
            self.ScrollGroupBegin(id=50000, flags=c4d.BFH_SCALEFIT|c4d.BFV_SCALEFIT,
                             scrollflags=c4d.SCROLLGROUP_VERT|c4d.SCROLLGROUP_AUTOVERT,)
#                             inith=100,initw=1000)              
            grFlag  = c4d.BFH_SCALEFIT |c4d.BFV_SCALEFIT
#            self.GroupBegin(id=50001,cols=1,flags=grFlag)    
        if bloc["collapse"] :
            collapse = c4d.BFV_BORDERGROUP_FOLD#|c4d.BFV_GRIDGROUP_EQUALCOLS
        else :
            collapse = c4d.BFV_BORDERGROUP_FOLD|c4d.BFV_BORDERGROUP_FOLD_OPEN#|c4d.BFV_GRIDGROUP_EQUALCOLS
        self.GroupBegin(id=bloc["id"],title=bloc["name"],cols=1,
                                flags=grFlag,#c4d.BFV_MASK,
                                groupflags=collapse)
        self.GroupBorder(c4d.BORDER_THIN_IN|c4d.BORDER_WITH_TITLE|c4d.BORDER_MASK)
#            self.GroupBorderSpace(self.left, self.top, self.right, self.bottom)
        for k,blck in enumerate(bloc["elems"]):
            self.startBlock(m=len(blck))
#            self.GroupBegin(id=int(k*25),title=str(k),cols=len(blck),
#                                                   flags=c4d.BFH_SCALEFIT)
#            self.GroupBorderSpace(self.left, self.top, self.right, self.bottom)
            for index, item in enumerate(blck):
                self._drawElem(item,x,y)
            self.endBlock()
#        self.endBlock()
        self.endBlock()
        if bloc["scrolling"]:
            self.endBlock()#scroll
#            self.endBlock()#main
        return y

    def drawTab(self,bloc,x,y):
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
        #TODO the Group system is confusin and nee to be improved inuPy
        #can we change color?
        if not self.tab :
            self.notebook = self.TabGroupBegin(id=bloc["id"]*1000,#title=bloc["name"],cols=1,
                                flags=c4d.BFH_SCALEFIT | c4d.BFV_SCALEFIT,
                                tabtype=c4d.TAB_TABS)
            self.GroupBorder(c4d.BORDER_THIN_IN|c4d.BORDER_MASK)#c4d.BORDER_BLACK|BORDER_WITH_TITLE
            self.tab = True
#            self.GroupBorderSpace(self.left, self.top, self.right, self.bottom)
        grFlag  = c4d.BFH_SCALEFIT |c4d.BFV_MASK
        if bloc["scrolling"]:
            self.ScrollGroupBegin(id=50000, flags=c4d.BFH_SCALEFIT|c4d.BFV_SCALEFIT,
                             scrollflags=c4d.SCROLLGROUP_VERT|c4d.SCROLLGROUP_AUTOVERT)
#                             inith=100,initw=1000)              
            grFlag  = c4d.BFH_SCALEFIT |c4d.BFV_SCALEFIT
#            self.GroupBorderNoTitle(c4d.BORDER_NONE|c4d.BORDER_WITH_TITLE)
        #should use max number of column?
        #get max nb elem:
        max = 0
        for k,blck in enumerate(bloc["elems"]):
            if len(blck) > max :
                maxi = len(blck)
        self.GroupBegin(id=bloc["id"],title=bloc["name"],cols=1,#initw=self.w,inith=self.h,
                            flags=grFlag)#c4d.BFH_SCALEFIT|c4d.BFV_SCALEFIT)#BFH_CENTER)
        if bloc["scrolling"]:
            self.GroupBorder(c4d.BORDER_THIN_IN|c4d.BORDER_WITH_TITLE|c4d.BORDER_WITH_TITLE_BOLD| c4d.BORDER_MASK)
        else :
            self.GroupBorderNoTitle(c4d.BORDER_THIN_IN|c4d.BORDER_MASK)
#        if self.scrolling:
#            self.ScrollGroupBegin(id=bloc["id"]*5000, flags=c4d.BFH_CENTER | c4d.BFV_MASK,#initw=self.w,inith=self.h,
#    scrollflags=c4d.SCROLLGROUP_VERT|c4d.SCROLLGROUP_AUTOVERT|c4d.SCROLLGROUP_BORDERIN|c4d.SCROLLGROUP_STATUSBAR |  c4d.SCROLLGROUP_NOBLIT)  
#        BFV_SCALEFIT | BFH_SCALEFIT,
#                       SCROLLGROUP_STATUSBAR | SCROLLGROUP_BORDERIN |
#                       SCROLLGROUP_NOBLIT
        
        for k,blck in enumerate(bloc["elems"]):
            if type(blck) is list :
                self.GroupBegin(id=int(k*25),cols=len(blck),title=str(k),
                        flags=c4d.BFH_SCALEFIT)#c4d.BFH_CENTER)
                for index, item in enumerate(blck):
                    self._drawElem(item,x,y)
                self.endBlock()
            else : #dictionary: multiple line / format dict?
                if "0" in blck:
                    y = self._drawGroup(blck,x,y)
                else :
                    y = self._drawFrame(blck,x,y)
#        if self.scrolling:
#            self.endBlock()        
        if bloc["scrolling"]:
           self.endBlock()
        self.endBlock()
#        self.LayoutChanged(bloc["id"])
        return y

    def saveDialog(self,label="",callback=None, suffix=""):
        """ Draw a File input dialog
        @type  label: string
        @param label: the windows title       
        @type  callback: function
        @param callback: the callback function to call
        """         
        filename = c4d.storage.SaveDialog(c4d.FSTYPE_ANYTHING,label)
        if callback is not None:
            return callback(filename)
        else :
            return filename

    def fileDialog(self,label="",callback=None, suffix=""):
        """ Draw a File input dialog
        @type  label: string
        @param label: the windows title       
        @type  callback: function
        @param callback: the callback function to call
        """         
        filename = c4d.storage.LoadDialog(c4d.FSTYPE_ANYTHING,label)
        if callback is not None:
            return callback(filename)
        else :
            return filename
        
    def waitingCursor(self,toggle):
        """ Toggle the mouse cursor appearance from the busy to idle.
        @type  toggle: Bool
        @param toggle: Weither the cursor is busy or idle 
        """             
        if not toggle : 
            c4d.gui.SetMousePointer(c4d.MOUSE_NORMAL)
        else :
            c4d.gui.SetMousePointer(c4d.MOUSE_BUSY)

    def updateViewer(self):
        """
        update the 3d windows if any
        """
        c4d.EventAdd()
        c4d.DrawViews(c4d.DRAWFLAGS_ONLY_ACTIVE_VIEW|c4d.DRAWFLAGS_NO_THREAD|c4d.DRAWFLAGS_NO_ANIMATION)          
        c4d.GeSyncMessage(c4d.EVMSG_TIMECHANGED)
 
    def startBlock(self,m=1,n=1):
        if m == 0:
            m = 1  
        self.GroupBegin(id=1,flags=c4d.BFH_SCALEFIT | c4d.BFV_MASK,
                           cols=m, rows=n)
        self.GroupBorderSpace(self.left, self.top, self.right, self.bottom)
#        self.bid+=1
        
    def endBlock(self):
        self.GroupEnd()
        #self.GroupEnd()

    def startLayout(self):
        grFlag  = c4d.BFH_SCALEFIT |c4d.BFV_MASK
        if self.scrolling:
            self.ScrollGroupBegin(id=50000, flags=c4d.BFH_SCALEFIT|c4d.BFV_SCALEFIT,
                             scrollflags=c4d.SCROLLGROUP_VERT|c4d.SCROLLGROUP_AUTOVERT,
                             inith=self.h,initw=self.w)  
            grFlag  = c4d.BFH_SCALEFIT |c4d.BFV_SCALEFIT
        
#        self.GroupBegin(id=1,flags=grFlag ,
#                   cols=1)
    def endLayout(self):
#        self.GroupEnd()
        if self.scrolling:
            self.GroupEnd()

##        SCROLLGROUP_VERT 	Allow the group to scroll vertically.
##        SCROLLGROUP_HORIZ 	Allow the group to scroll horizontally.
##        SCROLLGROUP_NOBLIT 	Always redraw the whole group, not just new areas, when scrolling.
##        SCROLLGROUP_LEFT 	Create the vertical slider to the left.
##        SCROLLGROUP_BORDERIN 	Display a small border around the scroll group.
##        SCROLLGROUP_STATUSBAR 	Create a status bar for the scroll group.
##        SCROLLGROUP_AUTOHORIZ 	Only show horizontal slider if needed.
##        SCROLLGROUP_AUTOVERT 	Only show vertical slider if needed.
##        SCROLLGROUP_NOSCROLLER 	No scroller.
##        SCROLLGROUP_NOVGAP 	No vertical gap.
##        SCROLLGROUP_STATUSBAR_EXT_GROUP 	Creates an extern group within the statusbar.
#        if self.scrolling:
#            self.ScrollGroupBegin(id=50000, flags=c4d.BFH_SCALEFIT | c4d.BFV_SCALEFIT,
#                             scrollflags=c4d.SCROLLGROUP_VERT|c4d.SCROLLGROUP_AUTOVERT)  
#            self.GroupBorderSpace(self.left, self.top, self.right, self.bottom)
##        
#        if self.tab:
#            self.GroupEnd()#self.Activate(1)#GroupEnd()
#        
    def getString(self,elem):
        """ Return the current string value of the String Input elem
        @type  elem: dictionary
        @param elem: the elem input dictionary       
        
        @rtype:   string
        @return:  the current string input value for this specific elem
        """                
        return self.GetString(elem["id"])

    def setString(self,elem,val):
        """ Set the current String value of the string input elem
        @type  elem: dictionary
        @param elem: the elem input dictionary       
        @type  val: string
        @param val: the new string value    
        """                        
        self.SetString(elem["id"],val)

    def getStringArea(self,elem):
        """ Return the current string area value of the String area Input elem
        @type  elem: dictionary
        @param elem: the elem input dictionary       
        
        @rtype:   string
        @return:  the current string area input value for this specific elem
        """                
        return self.GetString(elem["id"])

    def setStringArea(self,elem,val):
        """ Set the current String area value of the string input elem
        @type  elem: dictionary
        @param elem: the elem input dictionary       
        @type  val: string
        @param val: the new string value (multiline)   
        """                        
        self.SetString(elem["id"],val)

    def getReal(self,elem):
        """ Return the current Float value of the Input elem
        @type  elem: dictionary
        @param elem: the elem input dictionary       
        
        @rtype:   Float
        @return:  the current Float value input for this specific elem
        """
        val = self.GetReal(elem["id"])
        #check if its a real actually
        if isinstance(val, float):
            return val

    def setReal(self,elem,val):
        """ Set the current Float value of the Float input elem
        @type  elem: dictionary
        @param elem: the elem input dictionary       
        @type  val: Float
        @param val: the new Float value
        """
        return self.SetReal(elem["id"],float(val))

    def getBool(self,elem):
        """ Return the current Bool value of the Input elem
        @type  elem: dictionary
        @param elem: the elem input dictionary       
        
        @rtype:   Bool
        @return:  the current Bool value input for this specific elem
        """                                
        return self.GetBool(elem["id"])

    def setBool(self,elem,val):
        """ Set the current Bool value of the Bool input elem
        @type  elem: dictionary
        @param elem: the elem input dictionary       
        @type  val: Bool
        @param val: the new Bool value
        """                                
        return self.SetBool(elem["id"],bool(val))

    def getLong(self,elem):
        """ Return the current Int value of the Input elem
        @type  elem: dictionary
        @param elem: the elem input dictionary       
        
        @rtype:   Int
        @return:  the current Int value input for this specific elem
        """
        val = self.GetLong(elem["id"])
        if isinstance(val, int):
            return val

    def setLong(self,elem,val):
        """ Set the current Int value of the Int input elem
        @type  elem: dictionary
        @param elem: the elem input dictionary       
        @type  val: Int
        @param val: the new Int value
        """ 
        return self.SetLong(elem["id"],int(val))
        
    def getColor(self,elem):
        """ Return the current Color value of the Input elem
        @type  elem: dictionary
        @param elem: the elem input dictionary       
        
        @rtype:   Color
        @return:  the current Color array RGB value input for this specific elem
        """                        
        c4dcol = self.GetColorField(elem["id"])['color']
        return [c4dcol.x,c4dcol.y,c4dcol.z]

    def setColor(self,elem,val):
        """ Set the current Color rgb arrray value of the Color input elem
        @type  elem: dictionary
        @param elem: the elem input dictionary       
        @type  val: Color
        @param val: the new Color value
        """
#        print "in setColor",elem
        c4dcol = self.GetColorField(elem["id"])
#        print elem["id"]
        c4dcol['color'].x=val[0]
        c4dcol['color'].y=val[1]
        c4dcol['color'].z=val[2]
        self.SetColorField(elem["id"],c4dcol['color'],1.0,1.0,0)

    def setAction(self,elem,callback):
        elem["action"] = callback
                
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
        if type(step) is int:
            doit = self.SetLong
        else :
            doit = self.SetReal
        doit(elem["id"],default,mini,maxi,step)  
     
    @classmethod 
    def _restore(self,rkey,dkey=None):
        """
        Function used to restore the windows data, usefull for plugin
        @type  rkey: string
        @param rkey: the key to access the data in the registry/storage       
        @type  dkey: string
        @param dkey: wiether we want a particular data from the stored dic
        """        
        if hasattr(c4d,rkey):
            obj = c4d.__dict__[rkey]
            if dkey is not None:
                if c4d.__dict__[rkey].has_key(dkey) :
                    return  c4d.__dict__[rkey][dkey]       
                else :
                    return None
            return obj
        else :
            return None
            
    @classmethod
    def _store(self,rkey,dict):
        """
        Function used to store the windows data, usefull for plugin
        @type  rkey: string
        @param rkey: the key to access the data in the registry/storage       
        @type  dict: dictionary
        @param dict: the storage is done throught a dictionary
        """         
        c4d.__dict__[rkey]= dict

    def drawSubDialog(self,dial,id,callback = None,asynchro = True):
        """
        Draw the given subdialog whit his own element and callback
        
        @type  dial: dialog Object
        @param dial: the dialog object to be draw
        @type  id: int
        @param id: the id of the dialog
        @type  callback: function
        @param callback: the associate callback
        """     
        print (dial,id,asynchro)
        if asynchro :
            dial.Open(c4d.DLG_TYPE_ASYNC, pluginid=id, defaultw=dial.w, defaulth=dial.h)
        else :
            dial.Open(c4d.DLG_TYPE_MODAL, pluginid=id, defaultw=dial.w, defaulth=dial.h)
    
    def close(self,*args):
        """ Close the windows"""
        self.Close()

    def display(self):
        """ Create and Open the current gui windows """
        #how to display it/initialize it ?
        self.Open(c4d.DLG_TYPE_ASYNC, pluginid=self.plugid, 
                  defaultw=self.w, defaulth=self.h)

    def getDirectory(self):
        """return software directory for script and preferences"""
        prefpath=c4d.storage.GeGetC4DPath(1)
        os.chdir(prefpath)
        os.chdir(".."+os.sep)
        self.prefdir = os.path.abspath(os.curdir)
        if sys.platform == "darwin" :
        	self.softdir = c4d.storage.GeGetC4DPath(4)
        elif sys.platform == "win32":
        	self.softdir = c4d.storage.GeGetC4DPath(2)


class c4dUIDialog(c4dUI,uiAdaptor):
    def __init__(self,**kw):
        if kw.has_key("title"):
            self.title= kw["title"]
            self._setTitle(self.title)
        

#class c4dUISubDialog(c4dUI,uiAdaptor):
#    def __init__(self,):
#        c4dUIDialog.__init__(self,)
#        
###############WIDGET####################################
import time
class TimerDialog(c4d.gui.SubDialog):
    """
    Timer dialog for c4d, wait time for user input.
    from Pmv.hostappInterface.cinema4d_dev import helperC4D as helper
    dial = helper.TimerDialog()
    dial.cutoff = 30.0
    dial.Open(c4d.DLG_TYPE_ASYNC, pluginid=3555550, defaultw=250, defaulth=100)
    """
    def init(self):
        self.startingTime = time.time()
        self.dT = 0.0
        self._cancel = False
        self.SetTimer(100) #miliseconds
        #self.cutoff = ctime #seconds
        #self.T = int(ctime)
       
    def initWidgetId(self):
        id = 1000
        self.BTN = {"No":{"id":id,"name":"No",'width':50,"height":10,
                           "action":self.continueFill},
                    "Yes":{"id":id+1,"name":"Yes",'width':50,"height":10,
                           "action":self.stopFill},
                    }
        id += len(self.BTN)
        self.LABEL_ID = [{"id":id,"label":"Did you want to Cancel the Job:"},
                         {"id":id+1,"label":str(self.cutoff) } ]
        id += len(self.LABEL_ID)
        return True
        
    def CreateLayout(self):
        ID = 1
        self.SetTitle("Cancel?")
        self.initWidgetId()
        #minimize otin/button
        self.GroupBegin(id=ID,flags=c4d.BFH_SCALEFIT | c4d.BFV_MASK,
                           cols=2, rows=10)
        self.GroupBorderSpace(10, 10, 5, 10)
        ID +=1
        self.AddStaticText(self.LABEL_ID[0]["id"],flags=c4d.BFH_LEFT)
        self.SetString(self.LABEL_ID[0]["id"],self.LABEL_ID[0]["label"])   
        self.AddStaticText(self.LABEL_ID[1]["id"],flags=c4d.BFH_LEFT)
        self.SetString(self.LABEL_ID[1]["id"],self.LABEL_ID[1]["label"])  
        ID +=1
        
        for key in self.BTN.keys():
            self.AddButton(id=self.BTN[key]["id"], flags=c4d.BFH_LEFT | c4d.BFV_MASK,
                            initw=self.BTN[key]["width"],
                            inith=self.BTN[key]["height"],
                            name=self.BTN[key]["name"])
        self.init()
        return True

    def open(self):
        self.Open(c4d.DLG_TYPE_MODAL, pluginid=25555589, defaultw=120, defaulth=100)

    def Timer(self,val):
        #print val val seem to be the gadget itself ?
        #use to se if the user answer or not...like of nothing after x ms
        #close the dialog
#        self.T -= 1.0
        curent_time = time.time()
        self.dT = curent_time - self.startingTime
#        print self.dT, self.T
        self.SetString(self.LABEL_ID[1]["id"],str(self.cutoff-self.dT ))
        if self.dT > self.cutoff :
            self.continueFill()
            
    def stopFill(self):
        self._cancel = True
        self.Close()
        
    def continueFill(self):
        self._cancel = False
        self.Close()
        
    def Command(self, id, msg):
        for butn in self.BTN.keys():
            if id == self.BTN[butn]["id"]:
                self.BTN[butn]["action"]()
        return True
        


