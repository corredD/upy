
"""
    Copyright (C) <2010>  Autin L. TSRI
    
    This file git_upy/blender/v249/blenderUI.py is part of upy.

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
Created on Thu Dec  2 13:45:52 2010

@author: -
"""
import Blender
from Blender.Window import Theme
from Blender import BGL 
from Blender.BGL import * 

import bpy
from upy.uiAdaptor import uiAdaptor
from functools import partial
import os


class ReplacementScrollbar:
    """Scrollbar replacement for Draw.Scrollbar
       author: Michael Reimpell
       # Copyright (C) 2004 Michael Reimpell -- <M.Reimpell@tu-bs.de>
       - import Blender
       - call eventFilter and Filter in registered callbacks
    """
    def __init__(self, initialValue, minValue, maxValue, buttonUpEvent, buttonDownEvent,sub=False):
        """Constructor   
           
           Parameters:
               initialValue -  inital value
               minValue - minimum value
               maxValue - maxium value
               buttonUpEvent - unique event number
               buttonDownEvent - unique event number
        """
        self.currentValue = initialValue
        self.minValue = minValue
        if maxValue > minValue:
            self.maxValue = maxValue
        else:
            self.maxValue = self.minValue
            self.minValue = maxValue
        self.buttonUpEvent = buttonUpEvent
        self.buttonDownEvent = buttonDownEvent
        # private
        self.guiRect = [0,0,0,0]
        self.positionRect = [0,0,0,0]
        self.markerRect = [0,0,0,0]
        self.mousePressed = 0
        self.mouseFocusX = 0
        self.mouseFocusY = 0
        self.markerFocusY = 0
        self.mousePositionY = 0
        self.sub = sub
        return
    
    def getCurrentValue(self):
        """current marker position
        """
        return self.currentValue
        
    def up(self,steps=1,*args):
        """move scrollbar up
        """
#        print "up event",steps,args
        if self.sub:
            steps =10
        if (steps > 0):
            if ((self.currentValue - steps) > self.minValue):
                self.currentValue -= steps
            else:
                self.currentValue = self.minValue
        return
    
    def down(self, steps=1,*args):
        """move scrollbar down
        """
#        print "down event",steps,args
        if self.sub:
            steps =10
        if (steps > 0):
            if ((self.currentValue + steps) < self.maxValue): 
                self.currentValue += steps
            else:
                self.currentValue = self.maxValue
        return
    
    def draw(self, x, y, width, height):
        """draw scrollbar
        """
        # get size of the GUI window to translate MOUSEX and MOUSEY events
        guiRectBuffer = Blender.BGL.Buffer(GL_FLOAT, 4)
        Blender.BGL.glGetFloatv(Blender.BGL.GL_SCISSOR_BOX, guiRectBuffer)
        self.guiRect = [int(guiRectBuffer.list[0]), int(guiRectBuffer.list[1]), \
                        int(guiRectBuffer.list[2]), int(guiRectBuffer.list[3])]
        # relative position
        self.positionRect = [ x, y, x + width, y + height]
        # check minimal size:
        # 2 square buttons,4 pixel borders and 1 pixel inside for inner and marker rectangles
        if ((height > (2*(width+5))) and (width > 2*5)):
            # keep track of remaining area
            remainRect = self.positionRect[:]
            # draw square buttons
#            print "arrow",x,y,y + (height-width), width
            if self.sub :
                Blender.Draw.Button("/\\", self.buttonUpEvent, x, y + (height-width), width, width, "scroll up",self.up) 
            else :
                Blender.Draw.Button("/\\", self.buttonUpEvent, x, y + (height-width), width, width, "scroll up") 
            remainRect[3] -=  width + 2
            if self.sub :
                Blender.Draw.Button("\\/", self.buttonDownEvent, x, y, width, width, "scroll down",self.down) 
            else :
                Blender.Draw.Button("\\/", self.buttonDownEvent, x, y, width, width, "scroll down")                 
            remainRect[1] +=  width + 1
            # draw inner rectangle
            if not self.sub :
                Blender.BGL.glColor3f(0.13,0.13,0.13) # dark grey
                Blender.BGL.glRectf(remainRect[0], remainRect[1], remainRect[2], remainRect[3])
                remainRect[0] += 1
                remainRect[3] -= 1
                Blender.BGL.glColor3f(0.78,0.78,0.78) # light grey
                Blender.BGL.glRectf(remainRect[0], remainRect[1], remainRect[2], remainRect[3])
                remainRect[1] += 1
                remainRect[2] -= 1
                Blender.BGL.glColor3f(0.48,0.48,0.48) # grey
                Blender.BGL.glRectf(remainRect[0], remainRect[1], remainRect[2], remainRect[3])
                # draw marker rectangle
                # calculate marker rectangle
                innerHeight = remainRect[3]-remainRect[1]
                markerHeight = innerHeight/(self.maxValue-self.minValue+1.0)
                # markerRect 
                self.markerRect[0] = remainRect[0]
                self.markerRect[1] = remainRect[1] + (self.maxValue - self.currentValue)*markerHeight
                self.markerRect[2] = remainRect[2]
                self.markerRect[3] = self.markerRect[1] + markerHeight
                # clip markerRect to innerRect (catch all missed by one errors)
                if self.markerRect[1] > remainRect[3]:
                    self.markerRect[1] = remainRect[3]
                if self.markerRect[3] > remainRect[3]:
                    self.markerRect[3] = remainRect[3]
                # draw markerRect
                remainRect = self.markerRect
                Blender.BGL.glColor3f(0.78,0.78,0.78) # light grey
                Blender.BGL.glRectf(remainRect[0], remainRect[1], remainRect[2], remainRect[3])
                remainRect[0] += 1
                remainRect[3] -= 1
                Blender.BGL.glColor3f(0.13,0.13,0.13) # dark grey
                Blender.BGL.glRectf(remainRect[0], remainRect[1], remainRect[2], remainRect[3])
                remainRect[1] += 1
                remainRect[2] -= 1
                # check if marker has foucs
                if (self.mouseFocusX and self.mouseFocusY and (self.mousePositionY > self.markerRect[1]) and (self.mousePositionY < self.markerRect[3])):
                    Blender.BGL.glColor3f(0.64,0.64,0.64) # marker focus grey
                else:
                    Blender.BGL.glColor3f(0.60,0.60,0.60) # marker grey
                Blender.BGL.glRectf(remainRect[0], remainRect[1], remainRect[2], remainRect[3])
        else:
            print "scrollbar draw size too small!"
        return
        
    def eventFilter(self, event, value):
        """event filter for keyboard and mouse input events
           call it inside the registered event function
        """
        if (value != 0):
            # Buttons
            if (event == Blender.Draw.PAGEUPKEY):
                self.up(3)
                Blender.Draw.Redraw(1)
            elif (event == Blender.Draw.PAGEDOWNKEY):
                self.down(3)
                Blender.Draw.Redraw(1)
            elif (event == Blender.Draw.UPARROWKEY):
                self.up(1)
                Blender.Draw.Redraw(1)
            elif (event == Blender.Draw.DOWNARROWKEY):
                self.down(1)
                Blender.Draw.Redraw(1)
            # Mouse
            elif (event == Blender.Draw.MOUSEX):
                # check if mouse is inside postionRect
                if (value >= (self.guiRect[0] + self.positionRect[0])) and (value <= (self.guiRect[0] + self.positionRect[2])):
                    # redraw if marker got focus
                    if (not self.mouseFocusX) and self.mouseFocusY:
                        Blender.Draw.Redraw(1)
                    self.mouseFocusX = 1
                else:
                    # redraw if marker lost focus
                    if self.mouseFocusX and self.mouseFocusY:
                        Blender.Draw.Redraw(1)
                    self.mouseFocusX = 0
            elif (event == Blender.Draw.MOUSEY):
                # check if mouse is inside positionRect
                if (value >= (self.guiRect[1] + self.positionRect[1])) and (value <= (self.guiRect[1] + self.positionRect[3])):
                    self.mouseFocusY = 1
                    # relative mouse position
                    self.mousePositionY = value - self.guiRect[1]
                    if ((self.mousePositionY > self.markerRect[1]) and (self.mousePositionY < self.markerRect[3])):
                        # redraw if marker got focus
                        if self.mouseFocusX and (not self.markerFocusY):
                            Blender.Draw.Redraw(1)
                        self.markerFocusY = 1
                    else:
                        # redraw if marker lost focus
                        if self.mouseFocusX and self.markerFocusY:
                            Blender.Draw.Redraw(1)
                        self.markerFocusY = 0
                    # move marker
                    if (self.mousePressed == 1):
                        # calculate step from distance to marker
                        if (self.mousePositionY > self.markerRect[3]):
                            # up
                            self.up(1)
                            Blender.Draw.Draw()
                        elif (self.mousePositionY < self.markerRect[1]):
                            # down
                            self.down(1)
                            Blender.Draw.Draw()
                        # redraw if marker lost focus
                        if self.mouseFocusX and self.mouseFocusY:
                            Blender.Draw.Redraw(1)
                else:
                    # redraw if marker lost focus
                    if self.mouseFocusX and self.markerFocusY:
                        Blender.Draw.Redraw(1)
                    self.markerFocusY = 0
                    self.mouseFocusY = 0
            elif ((event == Blender.Draw.LEFTMOUSE) and (self.mouseFocusX == 1) and (self.mouseFocusY == 1)):
                self.mousePressed = 1
                # move marker
                if (self.mousePositionY > self.markerRect[3]):
                    # up
                    self.up(1)
                    Blender.Draw.Redraw(1)
                elif (self.mousePositionY < self.markerRect[1]):
                    # down
                    self.down(1)
                    Blender.Draw.Redraw(1)
            elif (Blender.Get("version") >= 234):
                if (event == Blender.Draw.WHEELUPMOUSE):
                    self.up(1)
                    Blender.Draw.Redraw(1)
                elif (event == Blender.Draw.WHEELDOWNMOUSE):
                    self.down(1)
                    Blender.Draw.Redraw(1)
        else: # released keys and buttons
            if (event == Blender.Draw.LEFTMOUSE):
                self.mousePressed = 0
                
        return
        
    def buttonFilter(self, event):
        """button filter for Draw Button events
           call it inside the registered button function
        """
        if (event  == self.buttonUpEvent):
            self.up()
            Blender.Draw.Redraw(1)
        elif (event == self.buttonDownEvent):
            self.down()
            Blender.Draw.Redraw(1)
        return

#UI general interface
class blenderUI:
    """
    The blender uiAdaptor abstract class
    ====================================
        This Adaptor give access to the basic blender Draw function need for 
        create and display a gui.
    """

    host = "blender24"
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
    scrolling = False
    block = False
#    w=250
#    h=1
    softdir=None
    prefdir=None
    fileDresult=""
    notebook=None
    currentScroolbar={}
    widgetGap = 6
    limit_scrollbar = 200
    ystep = -30
    
    def no_action(self, *args, **kwargs):pass
    
    def Quit(self):
        """ Close the windows"""
        Blender.Draw.Exit()

    def CoreMessage(self, evt, val):
        """ Hanlde the system event such as key or mouse position """
        #EXIT EVENT
        if len(self.currentScroolbar):
            if self.currentScroolbar["value"] is not None :
                self.currentScroolbar["value"].eventFilter(evt,val)
        if evt == Blender.Draw.ESCKEY or evt == Blender.Draw.QKEY:
           stop = Blender.Draw.PupMenu("OK?%t|Stop the script %x1")
           if stop == 1:
                self.Quit()
        #SCROLLING EVT
#        if (evt == Blender.Draw.WHEELDOWNMOUSE):                         
#            #Scroll area down
#            if (self.ScrollState < 0):
#                self.ScrollPos   = self.ScrollPos+self.ScrollInc
#            Blender.Draw.Draw()
#        elif (evt == Blender.Draw.WHEELUPMOUSE):                         
#            #Scroll area up
#            if (self.ScrollPos > 0):
#                self.ScrollPos = self.ScrollPos-self.ScrollInc
#            else: self.ScrollPos = 0
#            Blender.Draw.Draw()
#        if (evt == Blender.Draw.DOWNARROWKEY):                           
#            #Scroll area down
#            if (self.ScrollState < 0):
#                self.ScrollPos   = self.ScrollPos+self.ScrollInc
#            Blender.Draw.Draw()
#        elif (evt == Blender.Draw.UPARROWKEY):                           
#            #Scroll area up
#            if (self.ScrollPos > 0):
#                self.ScrollPos   = self.ScrollPos-self.ScrollInc
#            else: self.ScrollPos = 0
#            Blender.Draw.Draw()
#        #MOUSE CLICK EVT
        elif (evt == Blender.Draw.LEFTMOUSE and val):                    
            #Calculate mouse position in this area
            areaVert        =  [item["vertices"] \
                for item in Blender.Window.GetScreenInfo() \
                if item["id"] == Blender.Window.GetAreaID()]
            MouseCor        = Blender.Window.GetMouseCoords()
            self.MousePos[0]     = MouseCor[0]-areaVert[0][0]
            self.MousePos[1]     = MouseCor[1]-areaVert[0][1]
#            print "mouse", self.MousePos
            Blender.Draw.Draw()
        elif (evt == Blender.Draw.LEFTMOUSE and not val):                
            #If button up then clear mouse position
            self.MousePos[0]     = 0
            self.MousePos[1]     = 0
        elif (evt == Blender.Draw.RIGHTMOUSE and val):  
#            print "mouse", self.MousePos                 
            #Collapse or expand all subWindows based on popmenu choice
            result = Blender.Draw.PupMenu("Expand all|Collapse all|Exit",27)
            if (result == 1):
                for elem in self._layout:
                    if type(elem) is not list :
                        if elem["type"] == "frame":
                            elem["collapse"] = False
                self.ScrollPos = 0
            if (result == 2):
                for elem in self._layout:
                    if type(elem) is not list :
                        if elem["type"] == "frame":
                            elem["collapse"] = True
                self.ScrollPos = 0
            if (result == 3):
                self.Quit()
            Blender.Draw.Draw()
        elif (evt == Blender.Draw.HKEY and not val):
            pass#ShowHelp()
        elif (evt == Blender.Draw.RKEY and not val):
            pass
        elif (evt == Blender.Draw.AKEY and not val):
            pass
        elif (evt == Blender.Draw.PKEY and not val):
            pass
        elif (evt == Blender.Draw.MOUSEX or evt == Blender.Draw.MOUSEY):              
            pass
            #Update area if mouse is over it and scene or active object has changed
            #Set mouse position to zero to prevent LEFTMOUSE tab collapse flashing while moving
            self.MousePos[0]         = 0                         
            self.MousePos[1]         = 0
#            CurrentScene        = Blender.Scene.GetCurrent()
#            CurrentObject       = CurrentScene.objects.active
#            try:
#                CurrentMaterial = CurrentObject.getMaterials(1)[CurrentObject.activeMaterial-1]
#                if (CurrentMaterial == None):   CurrentMaterial = CurrentObject.getData(False, True).materials[CurrentObject.activeMaterial-1]
#            except:                             CurrentMaterial = ""
#            if ((CurrentScene and LastScene != CurrentScene.name) or (CurrentObject and LastObject != CurrentObject.name) or (CurrentMaterial and LastMaterial != CurrentMaterial.name)):
#                Draw()
      

    def SetTitle(self,title):
        """ Initialised the windows and define the windows titles 
        @type  title: string
        @param title: the window title

        """
        #do we overwrite w and h ?
        self.ScrollState     = 0
        self.AreaDims        = Blender.Window.GetAreaSize()  
#        print self.AreaDims
        #Get AreaSize for widget placement
        if self.block:
            self.top  = self.y
            self.SubPosYInc  = self.AreaDims[1]+self.ScrollPos
        else :
            self.y = self.top  = self.SubPosYInc  = self.AreaDims[1]+self.ScrollPos             
        #Increment by ScrollPos 
        self.TitleHeight     = 25                                
        #Height of top title bar
        self.WindowGap       = 6                                 
        #Distance between and around sub-windows
        self.SubPosXInc      = self.WindowGap
        self.SubPosYStart    = self.SubPosYInc-self.TitleHeight-self.WindowGap
        self.SubMinimum      = 400
        if (self.AreaDims[0] < self.SubMinimum):  
            self.SubWidth = self.AreaDims[0]
        else:                           
            self.SubWidth = self.AreaDims[0]/int(self.AreaDims[0]/self.SubMinimum)
        if not title :
            title  = self.title
        if title:
            TitleColor      = Theme.Get()[0].get("BUTS").header
            TextColor       = Theme.Get()[0].get("ui").menu_text
                #Draw Title
            BGL.glColor3f(TitleColor[0]/256.0, 
                          TitleColor[1]/256.0, 
                          TitleColor[2]/256.0)
            BGL.glRecti(0, self.SubPosYInc, self.AreaDims[0], self.SubPosYInc-self.TitleHeight)
            BGL.glColor3f(TextColor[0]/256.0, 
                          TextColor[1]/256.0, 
                          TextColor[2]/256.0)
            BGL.glRasterPos2d(10, self.SubPosYInc-self.TitleHeight/2-4)
            Blender.Draw.Text(title)
#            BGL.glColor3f(0.,0.,0.)
#            endGap = 5
#            x= 5 
#            BGL.glLineWidth(1)
#            BGL.glBegin(BGL.GL_LINES)
#            BGL.glVertex2i(x, self.SubPosYInc-self.TitleHeight/2-4)
#            BGL.glVertex2i(x, self.SubPosYInc-self.TitleHeight/2-4)
#            BGL.glEnd()            
            self.SubPosYInc = self.SubPosYStart
            if not self.block: self.y = self.SubPosYInc - self.TitleHeight/2
        else :
            if not self.block:  self.y = self.SubPosYInc

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
        for k in lookat:
#            Blender.Draw.PushButton(mitem,menuDic[mitem][0]["id"], x, 
#                                        self.y, 75, 25)
            menuDic[k]
            pos={}
            pos["x"]=x
            pos["y"]=self.SubPosYInc-self.TitleHeight/2-1
            pos["w"]=75
            pos["h"]=25
            item = menuDic[k]
            menuDic[k] = [item,pos]
            self.drawLabel(k, x, self.SubPosYInc-self.TitleHeight/2-1, 75, 25)
            x = x + 75
        for k in lookat:
            mitem=menuDic[k]
            item = mitem[0]
            mitem = mitem[1]
            if (self.MousePos[0] > mitem["x"] and self.MousePos[0] < mitem["x"]+mitem["w"] \
                and self.MousePos[1] > mitem["y"] \
                and self.MousePos[1] < mitem["y"]+mitem["h"]):
                self.MousePos = [0, 0]                    
                self.menu_cb(menuDic,k)
        for k in lookat:
            menuDic[k] = menuDic[k][0]
        
    def menu_cb(self,menu,menuId):
        listOptions =[]
        suboptions={}
        litem = menu[menuId][0]
        for i,item in enumerate(litem):
#            print item
            listOptions.append(item["name"])
            if item["sub"] is not None :
                msubOptions = []
                suboptions[str(i+1)]={}
                for j,sub in enumerate(item['sub']):
                    suboptions[str(i+1)][j]=item['sub'][sub]
                    msubOptions.append(item['sub'][sub]["name"])
        choice = Blender.Draw.PupMenu('|'.join(listOptions))
        if choice == -1 :
            return
        elif str(choice) in suboptions.keys():
            subchoice = Blender.Draw.PupMenu('|'.join(msubOptions))
            action = suboptions[str(choice)][subchoice-1]["action"]
            if action is not None:
                action(suboptions[str(choice)][subchoice-1]["id"])
        else :
            action = menu[menuId][0][choice-1]["action"]
            if action is not None :
                print action,choice
                action(choice)
        
    def handleMenuEvent(self,ev,menu):
        """ This function handle the particular menu event, especially for 
        submenu level action
        @type  ev: int
        @param ev: the current event
        @type  menu: dictionary
        @param menu: the current menu
        """  
        pass
        #get mouse
#        lookat = menu.keys()
#        for k in lookat:
#            mitem=menuDic[k]
#            item = mitem[0]
#            mitem = mitem[1]
#            if (self.MousePos[0] > mitem["x"] and self.MousePos[0] < mitem["x"]+mitem["w"] \
#                and self.MousePos[1] > mitem["y"]-mitem["h"]+10 \
#                and self.MousePos[1] < mitem["y"]+20):
#                    print "OK", mitem["name"]
##        for menuId in menu.keys():
#            if ev ==  menu[menuId][0]["id"]:
#                listOptions =[]
#                suboptions={}
#                for i,item in enumerate(menu[menuId]):
#                    listOptions.append(item["name"])
#                    if item["sub"] is not None :
#                        msubOptions = []
#                        suboptions[str(i+1)]={}
#                        for j,sub in enumerate(item['sub']):
#                            suboptions[str(i+1)][j]=item['sub'][sub]
#                            msubOptions.append(item['sub'][sub]["name"])
#                choice = Blender.Draw.PupMenu('|'.join(listOptions))
##                print choice,suboptions.keys()
#                if str(choice) in suboptions.keys():
#                    subchoice = Blender.Draw.PupMenu('|'.join(msubOptions))
#                    action = suboptions[str(choice)][subchoice-1]["action"]
#                    if action is not None:
#                        action(suboptions[str(choice)][subchoice-1]["id"])
#                else :
#                    action = menu[menuId][choice-1]["action"]
#                    if action is not None :
#                        action(choice)

    def checkwh(self,elem,w,h):
        """ Specific function for blender which check the size of the elem """
#        print "ok",w,h
        #if w is None :
        #    w = elem["width"]*self.scale
        #if h is None:
        #    h = elem["height"]*self.scale
        #if elem["type"] == "pullMenu":
        #    w,h = elem["width"],elem["height"]*self.scale
#        print "use",w,h
        return int(elem["width"]*self.scale), int(elem["height"]*self.scale)
        
    def addVariable(self,type,value):
        """ Create a container for storing a widget states """
        if type == "col" or type == "color":
            return Blender.Draw.Create(value[0],value[1],value[2])
        return Blender.Draw.Create(value)

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
        w,h = self.checkwh(elem,w,h)
        args = (elem["name"], elem["id"], int(x), int(y), int(w), int(h),\
                elem["tooltip"])
        if self.subdialog : 
            return self.check_addAction(Blender.Draw.PushButton, elem["action"],
                                        *args)
        else :
            return Blender.Draw.PushButton(*args)

    def drawButtonToggle(self,elem,x,y,w=None,h=None):
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
        w,h = self.checkwh(elem,w,h)
        args = (elem["name"], elem["id"], int(x), int(y), int(w), int(h),\
                elem["variable"].val, elem["tooltip"])
        if self.subdialog :
            elem["variable"]=self.check_addAction(Blender.Draw.Toggle, \
                                                  elem["action"], *args)
        else :
            elem["variable"]=Blender.Draw.Toggle(*args)

    def drawBOX(self,x1,x2,y1,y2):
        back_color = [col/256. for col in Theme.Get()[0].get("ui").menu_back[:-1]]
        line_color = [col/256.*3/4 for col in Theme.Get()[0].get("ui").outline[:-1]]
        BGL.glColor3f(*back_color)
        BGL.glLineWidth(1)
        BGL.glBegin(BGL.GL_QUADS)
        BGL.glVertex2i(x1, y1)
        BGL.glVertex2i(x2, y1)
        BGL.glVertex2i(x2, y2)
        BGL.glVertex2i(x1, y2)
        BGL.glEnd()        
        BGL.glColor3f(*line_color)
        BGL.glBegin(BGL.GL_LINE_LOOP)
        BGL.glVertex2i(x1, y1)
        BGL.glVertex2i(x2, y1)
        BGL.glVertex2i(x2, y2)
        BGL.glVertex2i(x1, y2)
        BGL.glEnd()        
        BGL.glColor3f(0, 0, 0)

    def drawCROSS(self,x1,x2,y1,y2):
        line_color = [col/256./2 for col in Theme.Get()[0].get("ui").outline[:-1]]
        BGL.glColor3f(*line_color)
        BGL.glLineWidth(2)
        BGL.glBegin(BGL.GL_LINES)
        BGL.glVertex2i(x1, y1)
        BGL.glVertex2i(x2, y2)
        BGL.glVertex2i(x2, y1)
        BGL.glVertex2i(x1, y2)
        BGL.glEnd()        
        BGL.glColor3f(0, 0, 0)

    def drawCheckBox(self,elem,x,y,w=None,h=None):#drawGLCheckBox
        if not elem["show"]:
            return
        w,h = self.checkwh(elem,w,h)
        if self.subdialog :
            elem["variable"]=self.check_addAction(Blender.Draw.Toggle, \
                elem["action"], elem["name"], elem["id"], int(x), int(y), \
                int(w), int(h), elem["variable"].val, elem["tooltip"])
        else :
            box_offset = 2
            box_coordinates = [x+box_offset,x+h-2*box_offset,\
                               y+1+box_offset,y+h+1-2*box_offset]
            doit = False
            if (self.MousePos[0] > x and self.MousePos[0] < x+w \
                and self.MousePos[1] > y-h+10 and self.MousePos[1] < y+20):
                elem["variable"].val = not elem["variable"].val
                self.MousePos = [0, 0]
    #            print elem["variable"].val
                doit = True
            self.drawBOX(*box_coordinates)
            if elem["variable"].val :
                self.drawCROSS(*box_coordinates)
            #need to draw the text
            #Draw Tab Text
            TitleHeight = 15
            TextOffset  = TitleHeight/2+4        
            BGL.glRasterPos2d(x+h, y+3*box_offset)
            Blender.Draw.Text(elem["name"], "normal")        
            #what about the calback?
            if elem["action"] is not None and doit:
                elem["action"]()

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


    def resetPMenu(self,elem):
        """ Add an entry to the given pulldown menu 
        @type  elem: dictionary
        @param elem: the pulldown dictionary
        """
        elem["value"]=[]
        elem["variable"].val = len(elem["value"])

    def addItemToPMenu(self,elem,item):
        """ Add an entry to the given pulldown menu 
        @type  elem: dictionary
        @param elem: the pulldown dictionary
        @type  item: string
        @param item: the new entry
        """
        elem["value"].append(item)
        elem["variable"].val = len(elem["value"])

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

        w,h = self.checkwh(elem,w,h)
        menuitems = ""
        if elem["name"]:
            menuitems += elem["name"]+"%t|"  # if no %xN int is set, indices start from 1
        for i,it in enumerate(elem["value"]):
            menuitems+="|"+it+"%x"+str(i+1)
#        menuitems+='|'.join(elem["value"])
        #name, event, x, y, width, height, default, tooltip=None, callback=None

        args = (menuitems,elem["id"], int(x), int(y), int(w), int(h),
                elem["variable"].val,elem["tooltip"])
        if self.subdialog :
            elem["variable"]=self.check_addAction(Blender.Draw.Menu, elem["action"],
                                                  *args)
        else :
            elem["variable"]=Blender.Draw.Menu(*args)
        
    def drawText(self,elem,x,y,w=None,h=None):
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
#        elem["width"] = len(elem["label"])* 3.
        if type(elem) == str :
            label = elem
        else :
            label = elem["label"]
            w,h = self.checkwh(elem,w,h)
        #Blender.BGL.glRasterPos2i(x,y+5)
        Blender.BGL.glColor3i(0,0,0)
        Blender.Draw.Label(label, x, y, w, h)
#        elem["width"] = len(elem["label"])* 3 #TODO find a more flexible solution

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
        TitleColor  = Theme.Get()[0].get("BUTS").header        
        BGL.glColor3f(TitleColor[0]/256., TitleColor[1]/256.0, TitleColor[2]/256.0)
        endGap      = 5
        w,h = self.checkwh(elem,w,h)
        if elem["value"] == "H":  
            BGL.glLineWidth(1)
            BGL.glBegin(BGL.GL_LINES)
            BGL.glVertex2i(x+endGap, y)
            BGL.glVertex2i(x+self.w-endGap, y)
            BGL.glEnd()
        elif elem["value"] == "V":
            BGL.glLineWidth(1)
            BGL.glBegin(BGL.GL_LINES)
            BGL.glVertex2i(x, y+endGap)
            BGL.glVertex2i(x, y+self.h-endGap)
            BGL.glEnd()
        if elem["label"] is not None :
            self.drawText(elem,x+endGap,y+4,w=w,h=h)

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
#        elem["width"] = 50#len(elem["label"])* 3.       
        if type(elem) == str :
            label = elem
        else :
            label = elem["label"]
            w,h = self.checkwh(elem,w,h)
#        Blender.BGL.glRasterPos2i(x,y+5)
        Blender.Draw.Label(label,x,y,w,h)
#        elem["width"] = 50#len(elem["label"])* 3 #TODO find a more flexible solution

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
        w,h = self.checkwh(elem,w,h)
        args = (elem["name"], elem["id"],int(x), int(y), int(w), int(h),
                elem["variable"].val,self.maxStrLenght,elem["tooltip"])
        if self.subdialog :
            elem["variable"]= self.check_addAction(Blender.Draw.String,
                    elem["action"], *args)
        else :
            elem["variable"]= Blender.Draw.String(*args)
            
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
#        w,h = self.checkwh(elem,w,h)
#        Blender.BGL.glRasterPos2i(x,y+5)
#        Blender.Draw.Text(elem["value"])
        #this could be a Text creation instead
        elem["width"] = 0
        elem["height"] = 0
        self.SetStringArea(elem,elem["value"])
#        texts = list(bpy.data.texts)
#        newText = [tex for tex in texts if tex.name == elem["name"]]
#        print newText
#        if not len(newText) :
#            newText = Blender.Text.New(elem["name"])
#        else :
#            newText[0].clear()
#            for line in elem["value"]: newText[0].write(line)

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
        w,h = self.checkwh(elem,w,h)
        w = max(w, Blender.Draw.GetStringWidth(elem["label"]))
        #name, event, x, y, width, height, initial, min, max, tooltip=None, 
        #callback=None, clickstep=None, precision=None
        clickstep = elem["step"]*100
        args = (elem["label"], elem["id"],int(x), int(y),\
                int(w), int(h), elem["variable"].val, elem["mini"],\
                elem["maxi"], elem["tooltip"], self.no_action, clickstep,\
                elem["precision"])

        if self.subdialog :
            elem["variable"]= self.check_addAction(Blender.Draw.Number,
                    elem["action"],i=-3, *args)
        else  :
            elem["variable"]= Blender.Draw.Number(*args)

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
        w,h = self.checkwh(elem,w,h)
        w = max(w, int(Blender.Draw.GetStringWidth(elem["label"])))
        clickstep = elem["step"]*100
        #name, event, x, y, width, height, initial, min, max, tooltip=None, 
        #callback=None, clickstep=None, precision=None
        args = (elem["label"], elem["id"],int(x), int(y),\
                int(w), int(h), float(elem["variable"].val), float(elem["mini"]),\
                float(elem["maxi"]), elem["tooltip"], self.no_action, clickstep,\
                float(elem["precision"]))
        
        if self.subdialog :
            elem["variable"] = self.check_addAction(Blender.Draw.Number,
                    elem["action"],i=-3, *args)
        else:
            elem["variable"]= Blender.Draw.Number(*args)

    def drawError(self,errormsg=""):
        """ Draw a error message dialog
        @type  errormsg: string
        @param errormsg: the messag to display
        """  
        Blender.Draw.PupMenu("ERROR: "+errormsg)
        
    def drawQuestion(self,title="",question=""):
        """ Draw a Question message dialog, requiring a Yes/No answer
        @type  title: string
        @param title: the windows title       
        @type  question: string
        @param question: the question to display
        
        @rtype:   bool
        @return:  the answer     
        """            
        block=[]
        for line in question.split('\n'):
            if len(line) > 30 :
                block.append(line[0:28]+"-")
                block.append("-"+line[28:])
            else :
                block.append(line)
        return Blender.Draw.PupBlock(title, block)
        
    def drawMessage(self,title="",message=""):
        """ Draw a message dialog
        @type  title: string
        @param title: the windows title       
        @type  message: string
        @param message: the message to display   
        """            
        block=[]
        #need to split the message, as windows length limited, 
        #31car
        for line in message.split('\n'):
            if len(line) >= 30 :
                block.append(line[0:28]+"-")
                block.append("-"+line[28:])
            else :
                block.append(line)
        retval = Blender.Draw.PupBlock(title, block)
        return

    def drawInputQuestion(self,title="",question="",callback=None):
        """ Draw an Input Question message dialog, requiring a string answer
        @type  title: string
        @param title: the windows title       
        @type  question: string
        @param question: the question to display
        
        @rtype:   string
        @return:  the answer     
        """                  
        result = Blender.Draw.PupStrInput(question, "", 100)
        if result :
            if callback is not None :
                callback(result)
            else :
                return result

    def getSelectTxt(self):
        """ specific function that proposed all text open in blender Text windows,
        and return the selected one from a pull-down menu
        """
        
        texts = list(bpy.data.texts)
        textNames = [tex.name for tex in texts]
        if textNames:
            choice = Blender.Draw.PupMenu('|'.join(textNames))
            if choice != -1:
                text = texts[choice-1]
                cmds=""
                for l in text.asLines():
                    cmds+=l+'\n'
                return cmds
        return None

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
        w,h = self.checkwh(elem,w,h)
        #(name, event, x, y, width, height, initial, min, max, 
        #realtime=1, tooltip=None, callback=None)
        #if elem["action"] is not None :
        #    elem["variable"]=Blender.Draw.Slider(elem["label"], elem["id"],x,y, 
        #            elem["width"]*self.scale, elem["height"]*self.scale,
        #            elem["variable"].val, elem["mini"], elem["maxi"],1,
        #            elem["tooltip"],elem["action"])#not sure about action..
        #else :
        if self.subdialog :
            elem["variable"] = self.check_addAction(Blender.Draw.Slider,
                elem["action"], elem["label"], elem["id"], int(x), int(y), \
                int(w), int(h), elem["variable"].val, elem["mini"], \
                elem["maxi"], 0, elem["tooltip"])
        else :#elem["label"]
            elem["variable"] = Blender.Draw.Slider("", elem["id"], int(x),\
                int(y), int(w), int(h), elem["variable"].val, elem["mini"],\
                elem["maxi"], 0, elem["tooltip"])

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
        w,h = self.checkwh(elem,w,h)
        img = Blender.Image.Load(elem["value"])
        #we can add some gl call to make some transparency if we want
        #Blender.BGL.glEnable( Blender.BGL.GL_BLEND ) # Only needed for alpha blending images with background.
        #Blender.BGL.glBlendFunc(Blender.BGL.GL_SRC_ALPHA, Blender.BGL.GL_ONE_MINUS_SRC_ALPHA) 
        #Blender.BGL.glDisable( Blender.BGL.GL_BLEND )
        Blender.Draw.Image(img, x, y-h-10)#, zoomx=1.0, zoomy=1.0, clipx=0, clipy=0, clipw=-1, cliph=-1)

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
        w, h = self.checkwh(elem,w,h)
        #print "color",elem["id"], x, y, w, h, elem["variable"].val,elem["action"]
        args = (elem["id"], int(x), int(y), int(w), int(h), elem["variable"].val)

        if self.subdialog and elem["action"] is not None :
            args += ("c", elem["action"])
        elem["variable"]=Blender.Draw.ColorPicker(*args)

    def handleSCrollEvent(self,evt,*args):
        if len(self.currentScroolbar):
            if self.currentScroolbar["value"] is not None :
                self.currentScroolbar["value"].buttonFilter(evt)
    
    def Tab_cb(self,*args):
        bloc = args[0]
        for tab in self.notebook :
#            print "O",tab["variable"].val
            if tab != bloc :
                tab["variable"].val = False
                tab["collapse"] = True                    
#                print "ok toggle",tab["name"]

    def drawSub(self,bloc,y):
        """
        Function to draw a block as a tab in a notebook layout of the gui. 
        
        @type  block: array or dictionary
        @param block: list or dictionary of item dictionary
        @type  x: int
        @param x: position on x in the gui windows, used for blender
        @type  y: int
        @param y: position on y in the gui windows, used for blender
        
        @rtype:   int
        @return:  the new horizontal position, used for blender
        """ 
        #scroll = self.use_scrollbar
#        print "OK DRAW SUB",bloc
        w = 45
        st= int(len(bloc)*6.4)
        if st > w :
            w = st
        #bloc["width"] = w
        scroll = False
        oriy = self.SubPosYInc - self.TitleHeight/2 - 10
        y = self.SubPosYInc - self.TitleHeight/2 - 10
        if y > self.top:
            y = self.top
        orix=self.x

#        print "oriy",oriy,self.top
        
        size=0
        for i,blc in enumerate(bloc):
            for item in blc:
                print item, item["height"]
                size+=item["height"]*self.scale
#        print (size,self.limit_scrollbar)
        if size > self.limit_scrollbar:
            scroll = True
        if scroll :
            if not hasattr(self,"scrollbar") :
                self.scrollbar= self._addElemt(name=self.title+"scroll")
                self.scrollbar["variable"] = self.addVariable("int",1)
    #            bloc["scrollbar"]["y"] =  self.y
                self.scrollbar["up"] = self.scrollbar["id"]
                self.scrollbar["down"] = self.id 
                self.scrollbar["value"] = ReplacementScrollbar(0,0,100,self.scrollbar["up"],
                                              self.scrollbar["down"],sub= self.subdialog)
                self.id = self.id + 1 
     
            x = orix+20+self.widgetGap
        else :
            x = orix
        startx = x
        #top = y
        oriy = oriy - 30
        if scroll :
            self.currentScroolbar = self.scrollbar
            if self.scrollbar["value"] is not None :
                y = oriy + self.scrollbar["value"].getCurrentValue()*4
#        print (y)
        for i,blc in enumerate(bloc):
            draw = True

            if scroll :
                if self.scrollbar["value"] is not None and \
                (y < oriy - 200 or y > oriy-200+200) :
#                    print "not drawn"
                    draw =False
            if draw :
                for item in blc:
#                    print ("draw item",x,y)
                    ButWidth = item["width"]*self.scale
                    ButtonHeight = item["height"]*self.scale
                    self._drawElem(item,x,y,ButWidth,ButtonHeight)
                    x= x + item["width"]*self.scale + 15
            x=startx
            y = y - 30            
        if scroll :
            self.currentScroolbar["value"].draw(orix, oriy-200, 20, 200)
        return -230
#        return 0
        
    def drawTab(self,bloc,x,y):
        """
        Function to draw a block as a tab in a notebook layout of the gui. 
        
        @type  block: array or dictionary
        @param block: list or dictionary of item dictionary
        @type  x: int
        @param x: position on x in the gui windows, used for blender
        @type  y: int
        @param y: position on y in the gui windows, used for blender
        
        @rtype:   int
        @return:  the new horizontal position, used for blender
        """ 
        #scroll = self.use_scrollbar
        w = 45
        st= int(len(bloc["name"])*6.4)
        if st > w :
            w = st
        bloc["width"] = w
        scroll = False
        oriy = self.SubPosYInc - self.TitleHeight/2 - 10
        y = self.SubPosYInc - self.TitleHeight/2 - 10
        if y > self.top:
            y = self.top
#        print "top",y
        orix=x
#        print "left",x
        #print "0",x
        #print "1",self.notebook
        #print "2",bloc not in self.notebook
        if self.notebook is None:
            self.notebook=[]
        #position
        #x = x + pos
        if bloc not in self.notebook:
            for bl in self.notebook:
                x += bl["width"] + self.widgetGap
            self.notebook.append(bloc)
        else :
            for i in range(0,self.notebook.index(bloc)):
                bl = self.notebook[i]
                x += bl["width"] + self.widgetGap
            
        #print "3",self.notebook.index(bloc)
#        print x,y,oriy,bloc["id"],bloc["name"],bloc["width"]
        if bloc["variable"] is None :
            bloc["variable"] = self.addVariable("bool",False)
        #the toggle should addapt to the size of the string
#        print "size text fpr 45 b ",len(bloc["name"])
        bloc["variable"] = Blender.Draw.Toggle(bloc["name"],
                                bloc["id"], x, y,int(w),20,
                                bloc["variable"].val, 
                                bloc["tooltip"],
                                partial(self.Tab_cb,bloc))
        #find the size of the bloc on Y and decide if scroll is require
        
        size=0
        for i,blk in enumerate(bloc["elems"]):
            for j,item in enumerate(blk):
                size+=item["height"]*self.scale
#        print size
        if size > self.limit_scrollbar:
            scroll = True
        if scroll :
            if not bloc.has_key("scrollbar") :
                bloc["scrollbar"] = self._addElemt(name=bloc["name"]+"scroll")
                bloc["scrollbar"]["variable"] = self.addVariable("int",1)
    #            bloc["scrollbar"]["y"] =  self.y
                bloc["scrollbar"]["up"] = bloc["scrollbar"]["id"]
                bloc["scrollbar"]["down"] = self.id 
                bloc["scrollbar"]["value"] = ReplacementScrollbar(0,0,100,bloc["scrollbar"]["up"],
                                              bloc["scrollbar"]["down"],sub= self.subdialog)
                self.id = self.id + 1 
     
            x = orix+20+self.widgetGap
        else :
            x = orix
        startx = x
        #top = y
        oriy = oriy - 30
        if bloc["variable"].val or not bloc["collapse"]:
#            print "click"
            if scroll :
                self.currentScroolbar = bloc["scrollbar"]
                if bloc["scrollbar"]["value"] is not None :
                    y = oriy + bloc["scrollbar"]["value"].getCurrentValue()*4
            for i,blk in enumerate(bloc["elems"]): #blk is a line
#                Blender.Draw.BeginAlign()
                draw = True
                y = y - 30
                if scroll :
                    if bloc["scrollbar"]["value"] is not None and \
                    (y < oriy - 200 or y > oriy-200+200) :
#                    print "not drawn"
                        draw =False
                for j,item in enumerate(blk):
                    if draw :
                        ButWidth = item["width"]*self.scale
                        ButtonHeight = item["height"]*self.scale
                        self._drawElem(item,x,y,ButWidth,ButtonHeight)
                        x= x + item["width"]*self.scale + 15
                x=startx
            if scroll :
                self.currentScroolbar["value"].draw(orix, oriy-200, 20, 200)
#            print "return ",-230
            return -230
        return 0

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
#        print x,y
        #Draw the Subwindows
#        y = y - self.SubFrame(bloc,x=x, y=y, width=SubWidth-WindowGap*2) - WindowGap 
#        self.SubPosYInc = self.SubPosYInc - self.SubFrame(bloc,self.SubPosXInc, 
#                                            self.SubPosYInc, 
#                                            self.SubWidth-self.WindowGap*2) - self.WindowGap 
        if self.subdialog:
            return y + self.drawTab(bloc,x,y)
        self.SubPosYInc = y
        self.SubPosXInc = x
        self.SubPosYInc = self.SubPosYInc - self.SubFrame(bloc,self.SubPosXInc, 
                                            self.SubPosYInc, 
                                            self.SubWidth-self.WindowGap*2) - self.WindowGap 
        #Draw SubWindow
        if (self.SubPosYInc-self.ScrollPos-self.TitleHeight < 0):
            if (self.ScrollState > self.SubPosYInc):              
                #Stop scrolling at last subwindow
                self.ScrollState = self.SubPosYInc
            if (self.SubPosXInc+self.SubWidth <= self.AreaDims[0]):    
                #If area wide stack subwindows from left to right otherwise top down
                self.SubPosYInc = self.SubPosYStart
                self.SubPosXInc = self.SubPosXInc+self.SubWidth
        y = self.SubPosYInc
        x = self.SubPosXInc
        return y

    def UpdateMenuData(self,blocklayout):
        """ special to update the frame layout """
#        global ButtonData, Filters
        selection       = ""
        
        if blocklayout is not None:
#            ArrayItem   = ButtonData[ArrayIndex]
            #Figure Buttons
            for index, item in enumerate(blocklayout["elems"]):
                buttonCount = len(blocklayout["elems"])
                if (buttonCount and index > buttonCount): break 
                #If buttonCount is specified stop drawing button list past count
                if (item["show"] == True): #Is button set to show
                    if (item["type"] == "pullMenu"): 
                        pass

    def SubFrame(self,blocklayout,x = 0, y = 100, width = 200): 
        """ this is the main code for drawing the collapsable frame
        layout, this code was taken from the Mosaic plugin for Blender"""
        
        #ArrayIndex is the index in ButtonData to the sub-window to draw in ButtonData array
        TitleHeight = 15
        TextOffset  = TitleHeight/2+4
        Bevel       = 6
        ArrowSize   = 4
        WindowGap   = self.widgetGap
        LineGap     = 15
        PosInc      = y
        showSection = True
        lineWidth   = width-WindowGap*2
        
        #Grab colors applied to standard areas of Blender so interface looks built in
        TitleColor  = Theme.Get()[0].get("BUTS").header     #Color of menu title
        TextColor   = [0,0,0]#Theme.Get()[0].get("BUTS").text_hi    #Color of submenu text
        TextColor2  = [0,0,0]#Theme.Get()[0].get("ui").menu_text    #Color of menu text
        TabColor    = [TitleColor[0]/4*3, TitleColor[1]/4*3, TitleColor[2]/4*3] #Color of System submenu tabs
        BackColor   = Theme.Get()[0].get("BUTS").panel      #Color of System submenu backgrounds
#        print blocklayout["wcolor"]
        blocklayout["wcolor"] = [1,1,1,1]
        #Collapse button if left mouse click in title subWindow title area
        if (self.MousePos[0] > x and self.MousePos[0] < x+width \
            and self.MousePos[1] > y-TitleHeight and self.MousePos[1] < y):
            blocklayout["collapse"] = not blocklayout["collapse"]
            self.MousePos = [0, 0]
        
        #Make sure menu data is revised for visible subs
#        if (not blocklayout["collapse"]): self.UpdateMenuData(blocklayout)
        
#        Blender.Draw.BeginAlign()
        #Draw Tab
        BGL.glColor3f(TabColor[0]/256.0*blocklayout["wcolor"][0], 
                      TabColor[1]/256.0*blocklayout["wcolor"][1],
                      TabColor[2]/256.0*blocklayout["wcolor"][2])
        BGL.glBegin(BGL.GL_POLYGON)
        BGL.glVertex2i(x, y-TitleHeight+Bevel)
        BGL.glVertex2i(x, y-Bevel)
        BGL.glVertex2i(x+Bevel/3, y-Bevel/3)
        BGL.glVertex2i(x+Bevel, y)
        BGL.glVertex2i(x+width-Bevel, y)
        BGL.glVertex2i(x+width-Bevel/3, y-Bevel/3)
        BGL.glVertex2i(x+width, y-Bevel)
        if blocklayout["collapse"]:          
            #Change titles bottom radius effect based on collapse state
            BGL.glVertex2i(x+width-Bevel/3, y-TitleHeight+Bevel/3)
            BGL.glVertex2i(x+width-Bevel, y-TitleHeight)
            BGL.glVertex2i(x+Bevel, y-TitleHeight)
            BGL.glVertex2i(x+Bevel/3, y-TitleHeight+Bevel/3)
        else:
            BGL.glVertex2i(x+width, y-TitleHeight)
            BGL.glVertex2i(x, y-TitleHeight)
        BGL.glEnd()
            
        PosInc      -= TitleHeight
        ButX        = x+WindowGap
        
        if (not blocklayout["collapse"]):      
            #Draw Buttons and Background according to Collapse state
            #Draw BackGround Top
            BGL.glEnable(BGL.GL_BLEND)
            BGL.glBlendFunc(BGL.GL_SRC_ALPHA, BGL.GL_ONE_MINUS_SRC_ALPHA)
            BGL.glColor4f(BackColor[0]/256.0*blocklayout["wcolor"][0], 
                          BackColor[1]/256.0*blocklayout["wcolor"][1], 
                          BackColor[2]/256.0*blocklayout["wcolor"][2], 
                          BackColor[3]/256.0*blocklayout["wcolor"][3])
            BGL.glRecti(x, PosInc, x+width, PosInc-WindowGap)
            BGL.glDisable(BGL.GL_BLEND)
            
            PosInc      -= WindowGap
            firstButton = True
            
            #Draw Buttons
            for k,block in enumerate(blocklayout["elems"]):
                #one block is one line
                ButX    = x+WindowGap    
                firstButton = True
                showSection = True
                availWidth  = lineWidth
                for index, item in enumerate(block):
                    buttonCount = len(block)
                    if (buttonCount and index > buttonCount): break 
                    #If buttonCount is specified stop drawing button list if past count
                    if (showSection == False and item["type"] != "line"): 
                        #If showSection is toggled off then hide all buttons up to next section line
                        item["show"] = False
                    else :
                        item["show"] = True
                    if item["show"]: 
                        #Is button set to show              
                        if False :#(firstButton):                       
                            #If first button of line cycle through the rest to 
                            #extract locked button widths from available line width
                            i           = index
                            availWidth  = lineWidth             
                            #Default available width to whole line
                            while firstButton:                  
                                #Look through buttons until end button is reached
    #                            print i,buttonCount
                                if i >= buttonCount : 
                                    break
                                if (block[i]["show"] == True): 
                                    #Only use visible buttons
                                    d  = block[i]["width"]
    #                                print d
                                    if (d > 1.0 and d < 100.0): 
                                        #If fixed width remove from available line width
                                        availWidth  -= d
                                    elif (d >= 100.0):          
                                        #If last button treat any value over 100 as 
                                        #fixed and break loop closing line
                                        availWidth  -= d-100.0
                                        firstButton = False
                                i+= 1
                        Trigger     = item["trigger"]
                        #Are there any special triggers on this button
                        Divider     = item["width"]*self.scale
                        #Get width ratio for this button
                        #ButWidth    = int(availWidth*Divider)  
                        #Figure button with divider as percent of window width
                        
                        #if (Divider > 1.0 and Divider < 100.0): 
                        #    ButWidth = int(Divider) 
                        #If over 1.0 then use as actual width instead of percent
                        #if (Divider >= 100.0):                  
                        #    ButWidth = int(x+width-WindowGap-ButX) 
                        #If last button set to tab width
                        ButWidth = item["width"]*self.scale#50#int(Divider) 
                        if (item["type"] == "line"): #If this is a line
                            if (Trigger):   ButtonHeight = LineGap
                            else:           ButtonHeight = WindowGap
                        else:               
                            ButtonHeight = item["height"]*self.scale#18   #Otherwise this is a button
                            if item["type"] == "inputStrArea":
                                ButtonHeight = 0    
                        
                        if (ButX == x+WindowGap):
                            #Draw Button BackGround
                            BGL.glEnable(BGL.GL_BLEND)
                            BGL.glBlendFunc(BGL.GL_SRC_ALPHA, BGL.GL_ONE_MINUS_SRC_ALPHA)
                            BGL.glColor4f(BackColor[0]/256.0*blocklayout["wcolor"][0], 
                                            BackColor[1]/256.0*blocklayout["wcolor"][1], 
                                            BackColor[2]/256.0*blocklayout["wcolor"][2], 
                                            BackColor[3]/256.0*blocklayout["wcolor"][3])
                            BGL.glRecti(x, PosInc, x+width, PosInc-ButtonHeight)
                            BGL.glDisable(BGL.GL_BLEND)
                            PosInc  -= ButtonHeight
                        if (item["type"] == "button"): 
                            #If this is supposed to be a button...
#                            print item["name"],ButX,PosInc,ButWidth,ButtonHeight
                            self.drawButton(item,ButX,PosInc,w=ButWidth, h=ButtonHeight)
                        elif (item["type"] == "label"): 
                            self.drawText(item,ButX,PosInc,w=ButWidth, h=ButtonHeight)
#                        elif item["type"] == "inputStrArea":
#                            ButtonHeight = 0
#                            self.drawStringArea(item,ButX,PosInc,w=ButWidth, h=ButtonHeight)
#                        elif (item["type"] == "pullMenu"): 
#                            #If this is supposed to be a list menu...
#                            #Draw menu description
#    #                        BGL.glColor3f(TextColor2[0]/256.0, TextColor2[1]/256.0, TextColor2[2]/256.0)
#    #                        BGL.glRasterPos2d(ButX, PosInc+5)
#    #                        if (Trigger):
#    #                            Text(ButtonData[ArrayIndex][WIN_BUTS][index][BUT_PROP], "normal")
#    #                            ButX        += Trigger
#    #                            ButWidth    -= Trigger
#    #                        #Draw Menu
#                            self.drawPMenu(item,ButX,PosInc,w=ButWidth,h=ButtonHeight)
#                        elif (item["type"] == "inputNbr"): 
#                            #If this is supposed to be a number button...
#                            pass
#    #                        ButtonData[ArrayIndex][WIN_BUTS][index][BUTTON] = Number(ButtonData[ArrayIndex][WIN_BUTS][index][BUT_TITLE], ButtonData[ArrayIndex][WIN_EVENT]+index, ButX, PosInc, ButWidth, ButtonHeight, ButtonData[ArrayIndex][WIN_BUTS][index][BUTTON].val, ButtonData[ArrayIndex][WIN_BUTS][index][BUT_MIN], ButtonData[ArrayIndex][WIN_BUTS][index][BUT_MAX], ButtonData[ArrayIndex][WIN_BUTS][index][BUT_TIP])
#                        elif (item["type"] == "checkbox"): 
#                            #If this is supposed to be a toggle button...
#                            if (Trigger == 9):                  
#                                #If toggle is using section hide trigger use 
#                                #button state to turn buttons section on and off
#                                showSection = item["variable"].val
#                            self.drawCheckBox(item,ButX,PosInc,w=ButWidth,h=ButtonHeight)                        
    #                    elif (ButtonData[ArrayIndex][WIN_BUTS][index][BUT_TYPE] == 4): 
    #                        #If this is supposed to be a string button...
    #                        if (Trigger):                       #If text is all on one line separate description, otherwise show in text
    #                            #Draw text description
    #                            BGL.glColor3f(TextColor2[0]/256.0, TextColor2[1]/256.0, TextColor2[2]/256.0)
    #                            BGL.glRasterPos2d(ButX, PosInc+5)
    #                            Text(ButtonData[ArrayIndex][WIN_BUTS][index][BUT_TITLE], "normal")
    #                            ButX        += Trigger
    #                            ButWidth    -= Trigger
    #                            ButtonData[ArrayIndex][WIN_BUTS][index][BUTTON] = String("", ButtonData[ArrayIndex][WIN_EVENT]+index, ButX, PosInc, ButWidth, ButtonHeight, ButtonData[ArrayIndex][WIN_BUTS][index][BUTTON].val, ButtonData[ArrayIndex][WIN_BUTS][index][BUT_MAX], ButtonData[ArrayIndex][WIN_BUTS][index][BUT_TIP])
    #                        else:
    #                            ButtonData[ArrayIndex][WIN_BUTS][index][BUTTON] = String(ButtonData[ArrayIndex][WIN_BUTS][index][BUT_TITLE], ButtonData[ArrayIndex][WIN_EVENT]+index, ButX, PosInc, ButWidth, ButtonHeight, ButtonData[ArrayIndex][WIN_BUTS][index][BUTTON].val, ButtonData[ArrayIndex][WIN_BUTS][index][BUT_MAX], ButtonData[ArrayIndex][WIN_BUTS][index][BUT_TIP])
    #                    elif (ButtonData[ArrayIndex][WIN_BUTS][index][BUT_TYPE] == 5): 
    #                        #If this is supposed to be a line...
    #                        EndAlign()
    #                        showSection     = True              
    #                        #Make all line types determine a new section and therefore 
    # turn section on automatically
    #                        if (Trigger):                       
    #                            #Only draw line if trigger is set
    #                            BGL.glColor3f(TabColor[0]/256.0*ButtonData[ArrayIndex][WIN_COLOR][0], TabColor[1]/256.0*ButtonData[ArrayIndex][WIN_COLOR][1], TabColor[2]/256.0*ButtonData[ArrayIndex][WIN_COLOR][2])
    #                            endGap      = 5
    #                            BGL.glLineWidth(1)
    #                            BGL.glBegin(BGL.GL_LINES)
    #                            BGL.glVertex2i(x+endGap, PosInc+2)
    #                            BGL.glVertex2i(x+width-endGap, PosInc+2)
    #                            BGL.glEnd()
    #                            BGL.glRasterPos2d(x+WindowGap, PosInc+4)
    #                            Text(ButtonData[ArrayIndex][WIN_BUTS][index][BUT_TITLE], "small")
    #                        BeginAlign()
                        else :
                            self._drawElem(item,ButX,PosInc,w=ButWidth,h=ButtonHeight)
#                            if item["type"]=="label":
#                                ButX = ButWidth = len(item["label"])*3.
#                        if (Divider >= 100.0):
#                            ButX    = x+WindowGap               
#                            #If this is the last button on the line...
#                            firstButton = True
#                        else:
#                            ButX    += ButWidth                 
#                            #Otherwise set next button to the end of last
                        ButX    += ButWidth+WindowGap
#                if len(blocklayout["elems"]) > 1 and k < len(blocklayout["elems"]):
                    #new line
                ButX    = x+WindowGap    
                firstButton = True
#                Blender.Draw.EndAlign()
                showSection     = True
#                Blender.Draw.BeginAlign()
            #Draw BackGround Bottom
            BGL.glEnable(BGL.GL_BLEND)
            BGL.glBlendFunc(BGL.GL_SRC_ALPHA, BGL.GL_ONE_MINUS_SRC_ALPHA)
            BGL.glColor4f(BackColor[0]/256.0*blocklayout["wcolor"][0], 
                            BackColor[1]/256.0*blocklayout["wcolor"][1], 
                            BackColor[2]/256.0*blocklayout["wcolor"][2], 
                            BackColor[3]/256.0*blocklayout["wcolor"][3])
            BGL.glRecti(x, PosInc, x+width, PosInc-WindowGap)
            BGL.glDisable(BGL.GL_BLEND)
            PosInc = PosInc-WindowGap
       
        else :
            for block in blocklayout["elems"]:
                for item in block:
                    item["show"] = False
        BGL.glColor3f(TextColor[0]/256.0, TextColor[1]/256.0, TextColor[2]/256.0)
        #Draw Arrow (rotate 90deg according to collapse boolean state)
        BGL.glPushMatrix()
        BGL.glTranslated(x+3*4, y-TitleHeight/2-1, 0)
        BGL.glRotated(-90*blocklayout["collapse"], 0, 0, -1)
        BGL.glBegin(BGL.GL_POLYGON)
        BGL.glVertex2i(0, -ArrowSize)
        BGL.glVertex2i(-ArrowSize, ArrowSize)
        BGL.glVertex2i(ArrowSize, ArrowSize)
        BGL.glEnd()
        BGL.glPopMatrix()
        
        #Draw Tab Text
        BGL.glRasterPos2d(x+4*6, y-TextOffset)
        Blender.Draw.Text(blocklayout["name"], "small")
        Blender.Draw.EndAlign()
#        print y,PosInc
        return y-PosInc                             #Return the final height of sub-window

    def fileDialog_cb(self, filename):
        self.fileDresult = filename
    
    def fileDialog(self, label="", callback=None, suffix=""):
        """ Draw a File input dialog
        @type  label: string
        @param label: the windows title       
        @type  callback: function
        @param callback: the callback function to call
        @type  suffix: string
        @param suffix: suffix of filename
        #work only in main windows..? not from a pull down menu.how to triger?
        """ 
        if callback is not None :
            Blender.Window.FileSelector (callback, label, suffix)
        else :
            Blender.Window.FileSelector (self.fileDialog_cb, label, suffix)
            return self.fileDresult

    def saveDialog(self,label="",callback=None, suffix=""):
        """ Draw a File input dialog
        @type  label: string
        @param label: the windows title       
        @type  callback: function
        @param callback: the callback function to call
        """         
        if callback is not None:
            Blender.Window.FileSelector (callback, label, suffix)
        else :
            Blender.Window.FileSelector (self.fileDialog_cb, label, suffix)
            return self.fileDresult
            
    def waitingCursor(self,toggle):
        """ Toggle the mouse cursor appearance from the busy to idle.
        @type  toggle: Bool
        @param toggle: Weither the cursor is busy or idle 
        """             
        Blender.Window.WaitCursor(toggle)

    def getString(self,elem):
        """ Return the current string value of the String Input elem
        @type  elem: dictionary
        @param elem: the elem input dictionary       
        
        @rtype:   string
        @return:  the current string input value for this specific elem
        """                
        return str(elem["variable"].val)

    def setString(self,elem,val):
        """ Set the current String value of the string input elem
        @type  elem: dictionary
        @param elem: the elem input dictionary       
        @type  val: string
        @param val: the new string value    
        """
        if elem["type"] == "label":
            elem["label"] = str(val)
        else :
            elem["variable"].val = str(val)

    def getStringArea(self,elem):
        """ Return the current string area value of the String area Input elem
        @type  elem: dictionary
        @param elem: the elem input dictionary       
        
        @rtype:   string
        @return:  the current string area input value for this specific elem
        """                
        return self.getSelectTxt()

    def SetStringArea(self,elem,val):
        """ Set the current String area value of the string input elem
        @type  elem: dictionary
        @param elem: the elem input dictionary       
        @type  val: string
        @param val: the new string value (multiline)   
        """                
        
        texts = list(bpy.data.texts)
        newText = [tex for tex in texts if tex.name == elem["name"]]
#        print newText
        if not len(newText) :
            newText = Blender.Text.New(elem["name"])
        else :
            newText[0].clear()
            newText=newText[0]
        for line in val : newText.write(line)
        elem["value"] = val
        
    def getLong(self,elem):
        """ Return the current Int value of the Input elem
        @type  elem: dictionary
        @param elem: the elem input dictionary       
        
        @rtype:   Int
        @return:  the current Int value input for this specific elem
        """   
        if elem["type"] == "pullMenu":
            return int(elem["variable"].val-1) #for menu...as its start at 1
        else :
            return int(elem["variable"].val)

    def setLong(self,elem,val):
        """ Set the current Int value of the Int input elem
        @type  elem: dictionary
        @param elem: the elem input dictionary       
        @type  val: Int
        @param val: the new Int value
        """                        
        if elem["type"] == "pullMenu":
            elem["variable"].val = val+1
        else :
            elem["variable"].val = val
            
    def getReal(self,elem):
        """ Return the current Float value of the Input elem
        @type  elem: dictionary
        @param elem: the elem input dictionary       
        
        @rtype:   Float
        @return:  the current Float value input for this specific elem
        """  
        if elem["type"] == "sliders":
            #check if float or int !
            #print type(elem["variable"].val)
            if type(elem["variable"].val) is int :
                return int(elem["variable"].val)
            else :
                return float(elem["variable"].val)
        else :
            return float(elem["variable"].val)

    def setReal(self,elem,val):
        """ Set the current Float value of the Float input elem
        @type  elem: dictionary
        @param elem: the elem input dictionary       
        @type  val: Float
        @param val: the new Float value
        """                                
        elem["variable"].val = float(val)

    def getBool(self,elem):
        """ Return the current Bool value of the Input elem
        @type  elem: dictionary
        @param elem: the elem input dictionary       
        
        @rtype:   Bool
        @return:  the current Bool value input for this specific elem
        """                        
        return bool(elem["variable"].val)
        
    def setBool(self,elem,val):
        """ Set the current Bool value of the Bool input elem
        @type  elem: dictionary
        @param elem: the elem input dictionary       
        @type  val: Bool
        @param val: the new Bool value
        """                        
        elem["variable"].val = bool(val)

    def getColor(self,elem):
        """ Return the current Color value of the Input elem
        @type  elem: dictionary
        @param elem: the elem input dictionary       
        
        @rtype:   Color
        @return:  the current Color array RGB value input for this specific elem
        """                        
        return elem["variable"].val

    def setColor(self,elem,val):
        """ Set the current Color rgb arrray value of the Color input elem
        @type  elem: dictionary
        @param elem: the elem input dictionary       
        @type  val: Color
        @param val: the new Color value
        """        
        elem["variable"].val = val

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
        if type(step) is int :
            elem["variable"] = Blender.Draw.Create(0)
        else :
            elem["variable"] = Blender.Draw.Create(0.)
        elem["maxi"] = maxi
        elem["mini"] = mini
#        elem["default"] = 
        elem["step"] = step
        
    def updateViewer(self):
        """
        update the 3d windows if any
        """
        Blender.Scene.GetCurrent().update()
        Blender.Draw.Redraw()
        Blender.Window.RedrawAll()
        Blender.Window.QRedrawAll()  
        Blender.Redraw()

    @classmethod
    def _restore(self,rkey,dkey=None):
        """
        Function used to restore the windows data, usefull for plugin
        @type  rkey: string
        @param rkey: the key to access the data in the registry/storage       
        @type  dkey: string
        @param dkey: wiether we want a particular data from the stored dic
        """
        rdict = Blender.Registry.GetKey(rkey, False)
        if rdict:
            if dkey is not None and rdict[dkey] is not None:
                return rdict[dkey]
            else :
                return rdict
        else:
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
        rdict={}
        for dkey in dict:
            rdict[dkey] = dict[dkey]
        Blender.Registry.SetKey(rkey, rdict, False)

    def close(self,*args):
        """ Close the windows"""
        if not self.subdialog :
            self.Quit()
        else :
            #should stop drawing it
            self.drawUIblock = False

    def drawSubDialogUI(self):
        Blender.Draw.UIBlock(self._createLayout, mouse_exit=0)

    def getXYsubWind(self,dial):
        x,y=Blender.Window.GetMouseCoords()
        but = Blender.Window.GetMouseButtons()
        if but == 4:#Blender.Draw.RIGHTMOUSE :#
           dial.x = x#screen_size[0]- self.w/2#x - self.w/2
           dial.y = y#screen_size[1]- self.h/2#y# - self.h/2
        return


    def drawSubDialog(self,dial,id,callback=None,asynchro = True):
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
        sub=[]
        dial.w = self.w
        dial.h = 1
        if dial.block  :
            dial.drawUIblock = True
            #need per button callback...
            x,y=Blender.Window.GetMouseCoords()
            screen_size = Blender.Window.GetScreenSize()
            dial.x = x#screen_size[0]- self.w/2#x - self.w/2
            dial.y = y#screen_size[1]- self.h/2#y# - self.h/2
            w=dial.w
            h=dial.h 
            print "h",h
            if h == 1 :
                h = screen_size[1]/2  
            if x >= screen_size[0] or x+dial.w*4 >= screen_size[0]:
                dial.x = screen_size[0]/2  
            if y > screen_size[1] or y+h*4 > screen_size[1]: 
                if dial.h == 1 :
                    dial.y = screen_size[1]/2
                else :
                    dial.y = screen_size[1]-dial.h*4
            while dial.drawUIblock:
                self.getXYsubWind(dial)
                Blender.Draw.UIBlock(dial._createLayout,0)#self.drawSubDialogUI()
            return
        for block in dial._layout:
            for elem in block :
                if elem["type"] == "inputInt":
                    sub.append((elem["name"],elem["variable"],elem["mini"],elem["maxi"]))
                elif elem["type"] == "inputFloat":
                    sub.append((elem["name"],elem["variable"],elem["mini"],elem["maxi"]))
                elif elem["type"] == "label":
                    sub.append(elem["label"])
                elif elem["type"] == "checkbox":
                    sub.append((elem["name"],elem["variable"]))
#                elif elem["type"] == "button"  :
#                    sub.append((elem["name"],elem["variable"]))
#        print sub
        retval = Blender.Draw.PupBlock(dial.title, sub)
#        print retval
        if callback is not None:
            callback()
        else :
            return retval
        #apply the command?

    def display(self):
        """ Create and Open the current gui windows """        
        Blender.Draw.Register(self.CreateLayout, self.CoreMessage, self.Command)

    def getDirectory(self):
        """return software directory for script and preferences"""
        self.softdir = os.path.abspath(Blender.Get("homedir"))
        self.prefdir = Blender.Get('uscriptsdir')
        if self.prefdir is None:
            self.prefdir = Blender.Get('scriptsdir')
        self.prefdir =os.path.abspath( self.prefdir)
        
class blenderUIDialog(blenderUI,uiAdaptor):
    def __init__(self,**kw):
        #print "init", kw
        if kw.has_key("title"):
            self.title= kw["title"]
            self.SetTitle(self.title)
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


