
"""
    Copyright (C) <2010>  Autin L. TSRI
    
    This file git_upy/uiAdaptor.py is part of upy.

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
Created on Thu Dec  2 14:25:17 2010

@author: Ludovic Autin - ludovic.autin@gmail.com
#to do :
add Group
add more layout support
"""
import sys
from time import time
import math

if sys.version > '3.3.0' :
    unicode = str

class uiAdaptor(object):
    """
    The uiAdaptor abstract class
    ============================
        This is the main class from which all adaptor derived. The uiAdaptor 
        give access to the basic function need for create and display a gui.

        @ivar _layout: the array of block that will define the gui windows layout
        @type _layout: array Object 
        @ivar _menu: the menu of the gui windows
        @type _menu: menu Object 
        @ivar _timer: Whether callback execution time is mesured
        @type _timer: Bool
    """
 
    _layout = []
    _menu = None
    _timer = False
    x = 5
    y = 800
    title = ""
    MENU_ID = {}
    bid=1
    id=1
    notebookend = False
    widgetGap =6
    
    def __init__(self,**kw):
        pass

#    def getFlagAlignement(self,options):
#        return options
        
    def timeFunction(self,function,*args):
        """
        Mesure the time for performing the provided function. 
    
        @type  function: function
        @param function: the function to execute
        @type  args: liste
        @param args: the liste of arguments for the function
        
    
        @rtype:   list/array
        @return:  the center of mass of the coordinates
        """
         
        t1=time()
        function(args)
        print("time ", time()-t1)

    def callbackaction(self,item,*args):
        """
        Abstract function to call the item callback function, with the given args
    
        @type  item: dictionary
        @param item: the widget for which we want to call the action callback
        @type  args: liste
        @param args: the liste of arguments for the function
        """ 
        #print ("action ", item["name"], item["action"])
        if item["action"] is not None:
            item['action'](*args)

    def check_addAction(self,funct,action,*args,**kw):
        #nned to replace no_action with callback
        larg = list(args)
        if action is not None :
            if "i" in kw and kw["i"] != None :
                larg[kw["i"]] = action
            else :
                larg.append(action)
        larg = tuple(larg)
#        print "args",larg
        return funct(*larg)

    def _callElemAction(self,item):
        """
        Abstract function to call the item callback function, with the given args.
        If timer is defined, the execution time will be mesured and printed.
    
        @type  item: dictionary
        @param item: the widget for which we want to call the action callback
        """
        import os
        #print os.curdir
        if self._timer : 
            self.timeFunction(item["action"])
        else : 
            self.callbackaction(item)
     
    def _callElem(self,block,evt):
        """
        Abstract function to call the item callback function that correspond to 
        the given event.
    
        @type  block: array of item dictionary
        @param block: the block layout
        @type  evt: Int
        @param evt: the event
        """                
        called= False
        for elem in block:
            if elem["id"] == evt : #the event
#                print (elem["name"],elem["id"])
                self._callElemAction(elem)
                called = True
        return called

    def _command(self,*args):
        """
        Main function to handle the event from the gui. The function loop over all
        block's item, and will call the function according the current event.
    
        @type  args: list or args
        @param args: depending of the host the event's format is not the same.
        """
        #print ("_commands ",args)
        evt = None
        if len(args):
            evt=args[0]
            #return
        if type(evt) is list or type(evt) is tuple:
            evt= evt[0]
        self.waitingCursor(1)
        #what about the Menu in Blender
        called = False
        for block in self._layout:
            if type(block) is list :
                self._callElem(block,evt)
            else :
                if "0" in block:
                    for k in block:
                        if k != "0":
                            called = self._callElem(block[k],evt)
                else :
                    for line in block["elems"]:
                        if type(line) is list :
                            self._callElem(line,evt)
                        else :
                            if "0" in line:
                                for k in line:
                                    if k != "0":
                                        called = self._callElem(line[k],evt)
                            else :
                                for l in line["elems"]:
                                    called = self._callElem(l,evt)
        if self.host == 'blender':
            self.handleSCrollEvent(evt,args)
        if self.MENU_ID and not called:
            self.handleMenuEvent(evt,self.MENU_ID)
        #EXTRA CALLBACK?
        self.updateViewer()
   
    
    def _addLayout(self,id=0,name="",width=0,height=0,label="",tooltip="",
                   elems=None,type="frame",wcolor=[1.,0.,0.,1.],collapse=True,
                   scrolling=False, variable=None,alignement=None):
        """
        Return a dictionary reprensenting one sublayout, such as the collapsable 
        frame.
    
        @type  id: int
        @param id: the Id of the layout
        @type  name: string
        @param name: name of the layout
        @type  width: int
        @param width: width  of the layout
        @type  height: int
        @param height: height of the layout
        @type  label: string
        @param label: label of the layout
        @type  tooltip: string
        @param tooltip: tooltip to display for the layout
        @type  elems: list or dictionary
        @param elems: list or dictionary of item dictionary to put in the layout
        @type  type: string
        @param type: type of layout. ie frame or tab
        @type  wcolor: array
        @param wcolor: color of the layout
        @type  collapse: boolean
        @param collapse: used for the collapsable frame
        
        @rtype:   dictionary
        @return:  the layout to be draw
        """
        for line in elems:
            for el in line :
                if el is None :
                    continue
#                el["show"] = not collapse #check if work with otherhost that blender2.6
        if self.host == "dejavu":
            collapse=True
        elem = {"id":self.id,"name":name,"width":width,"height":height,"label":label,
                "tooltip":tooltip,"elems":elems,"type":type,"wcolor":wcolor,"width":width,"height":height,
                "collapse":collapse,"variable":variable,"scrolling":scrolling,"alignement":alignement}
        self.id = self.id + 1
#        print ("host",self.host)
        if self.host in ['blender25', 'blender262','blender263'] :#or self.host == 'blender':
            if elem["type"] == "frame":#TAB?
                self.addVariablePropToSc(elem,"bool",collapse)#[type,val]
            if elem["type"] == "tab" :
                elem["type"] = "frame"
                self.addVariablePropToSc(elem,"bool",collapse)
        return elem

    def _addElemt(self,id=0,name="",width=10,height=10,label=None,tooltip="",
                  action=None,value=None,variable=None,type="label",icon=None,
                  maxi=10,mini=0,step=1,show=True,trigger=False,sub=None,
                  precision=4.,alignement="hfit_scale"):
        """
        Return a dictionary reprensenting one sublayout, such as the collapsable 
        frame.
    
        @type  id: int
        @param id: the Id of the layout
        @type  name: string
        @param name: name of the layout
        @type  action: function
        @param action: the function callback
        @type  width: int
        @param width: width  of the layout
        @type  height: int
        @param height: height of the layout
        @type  value: int/str/float/bool
        @param value: the default value of the items
        @type  variable: python variable
        @param variable: the variable storing the state of the item
        @type  type: string
        @param type: type of items, ie button,label,slider,...        
        @type  label: string
        @param label: label of the layout
        @type  tooltip: string
        @param tooltip: tooltip to display for the layout
        @type  icon: string
        @param icon: filename for bitmap used as an icon for the item, if its supported by the host.
        @type  maxi: int/float
        @param maxi: max value for the item, ie slider
        @type  mini: int/float
        @param mini: min value for the item, ie slider
        @type  step: int/float
        @param step: step value for the item, ie slider
        @type  show: boolean
        @param show: hide/shot the items
        @type  trigger: 
        @param trigger: 
        @type  sub: dictionary
        @param sub: used for subitems
        @type  precision: float
        @param precision: How many decimals will be displayed
        
        @rtype:   dictionary
        @return:  the item to be draw
        """   
        elem = {"id":self.id,"name":name,"action":action,"width":width,"height":height,
                "value":value,"variable":variable,"type":type,"tooltip":tooltip,
                "label":label,"icon":icon,"maxi":maxi,"mini":mini,"step":step,
                "show":show,"trigger":trigger,"sub":sub,
                "precision":precision,"alignement":alignement}
        self.id = self.id + 1              
#        print ("host"+self.host)
        if self.host in ['blender25', 'blender262', 'blender263'] :#or self.host == 'blender':
#            print ("blender2.5 we will setup the Scene properties",variable)
            if variable is not None : #[type,val]
                self.addVariablePropToSc(elem,variable[0],variable[1])#not for button
        elif self.host == "tk":
            if variable is None :
                elem["variable"] = self.addVar(type,value)
        return elem
        
    def _draw(self,block,y):
        """
        Function to draw a block by line in the main layout of the gui. 
        block is an array. [c1,c2,c3] or {0:[c1,c2,c3],1:[c1,c2,c3]} 
        for two lines with same height.
        
        @type  block: array or dictionary
        @param block: list or dictionary of item dictionary
        @type  y: int
        @param y: position on y in the gui windows, used for blender
        
        @rtype:   int
        @return:  the new horizontal position, used for blender
        """
        x=self.x
        if type(block) is list : #one line
            #unable the last tab
            if self.notebook is not None and not self.notebookend:
                self.notebookend = True
                self.endBlock()
            y = y +self.ystep
            self.startBlock(m=len(block))
            for elem in block:
                if elem is None :
                    continue
                #if self.subdialog: print "draw",elem["type"]
                self._drawElem(elem, x, y)
                x += int(elem["width"]*self.scale) + 15
            self.endBlock()
        else : #dictionary: multiple line / format dict?
            if "0" in block:
                y = self._drawGroup(block,x,y)
            else :
                y = self._drawFrame(block,x,y)
                #self.endBlock()
        return y
    
    def _drawGroup(self,block,x,y):
        #can beoverwritten by child class
        y = y +self.ystep
        if self.host != "maya" :
            self.startBlock(m=block["0"][0])
        for i in range(1,len(block)):
            x=5
            if self.host == "maya" and self.host == "houdini":
                self.startBlock(m=len(block[str(i)]))
            for elem in block[str(i)]:
                if elem is None :
                    continue
                self._drawElem(elem,x,y)
                x += int(elem["width"]*self.scale) + 15
            if self.host == "maya" and self.host == "houdini":
                self.endBlock()
        if self.host != "maya" : self.endBlock()
        return y

    def _drawFrame(self,bloc,x,y):
        """
        Function to draw a block as a frame layout of the gui. 
        
        @type  bloc: array or dictionary
        @param bloc: list or dictionary of item dictionary
        @type  x: int
        @param x: position on x in the gui windows, used for blender
        @type  y: int
        @param y: position on y in the gui windows, used for blender
        
        @rtype:   int
        @return:  the new horizontal position, used for blender
        """                               
        if bloc["type"] == "frame":
            y = self.drawFrame(bloc,x,y)
            return y
        elif bloc["type"] == "tab":
            y += self.drawTab(bloc,x,y)
            return y

    def _drawElem(self,elem,x,y,w=None,h=None):
        """
        Function to draw a elem/item in function of his type
        
        @type  elem: array or dictionary
        @param elem: list or dictionary of item dictionary
        @type  x: int
        @param x: position on x in the gui windows
        @type  y: int
        @param y: position on y in the gui windows
        @type  w: int
        @param w: force the width of the item
        @type  h: int
        @param h: force the height of the item
        """ 
#        print (elem)
#        print elem["alignement"]
#        print "dElem",elem["name"],x,y,w,h       
        if elem is None :
            return
        if elem["alignement"] is not None :
            elem["alignement"] = self.getFlagAlignement(elem["alignement"])
        if elem["type"] == "button":
            self.drawButton(elem,x,y,w=w,h=h)
        elif elem["type"] == "pullMenu":
            self.drawPMenu(elem,x,y,w=w,h=h)
        elif elem["type"] == "inputStr":
            self.drawString(elem,x,y,w=w,h=h)
        elif elem["type"] == "inputStrArea":
            self.drawStringArea(elem,x,y,w=w,h=h)
        elif elem["type"] == "checkbox":
            self.drawCheckBox(elem,x,y,w=w,h=h)
        elif elem["type"] == "sliders" or elem["type"] == "slidersInt":
            self.drawSliders(elem,x,y,w=w,h=h)        
        elif elem["type"] == "inputInt":
            self.drawNumbers(elem,x,y,w=w,h=h)
        elif elem["type"] == "inputFloat":
            self.drawFloat(elem,x,y,w=w,h=h)  
#        elif elem["type"] == "image":
#            self.drawImage(elem,x,y,w=w,h=h)        
        elif elem["type"] == "color":
            self.drawColorField(elem,x,y,w=w,h=h)
        elif elem["type"] == "label": 
            self.drawLabel(elem,x,y,w=w,h=h)
        elif elem["type"] == "group": 
            self.drawGroup(elem,x,y,w=w,h=h)
        elif elem["type"] == "line": 
            self.drawLine(elem,x,y,w=w,h=h)
#        elif elem["type"] == "obj": 
#            self.drawObj(elem,x,y,w=w,h=h)
            
    def addVar(self,typ,val):
        if type(val) is list :
            if type(val[0]) is str:
                val = 0
#        if type == "button":
#            self.drawButton(elem,x,y,w=w,h=h)
        if typ == "pullMenu":
            if val is None : val = 0
            return self.addVariable("int",val)
        elif typ == "inputStr" or type == "label":
            if val is None : val = ""
            return self.addVariable("str",val)
#        elif elem["type"] == "inputStrArea":
#            self.drawStringArea(elem,x,y,w=w,h=h)
        elif typ == "checkbox":
            if val is None : val = 0
            return self.addVariable("int",val)
        elif typ == "sliders":
            if val is None : val = 0
            return self.addVariable("int",val)       
        elif typ == "inputInt":
            if val is None : val = 0
            return self.addVariable("int",val)     
        elif typ == "inputFloat":
            if val is None : val = 0.0
            return self.addVariable("float",val)     
#        elif elem["type"] == "image":
#            return self.getBool(elem)             
        elif typ == "color":
            if val is None : val = (0,0,0)
            return self.addVariable("col",val)       
#        elif elem["type"] == "label": 
#            return self.getBool(elem)       

    def getVal(self,elem):
        """
        Return the value of the given widget
        
        @type  elem: dictionary widget
        @param elem: the widget        
        @rtype:   X
        @return:  dependin on the type of widget will return a float, int, bool, or string
        """
#        if elem["type"] == "button":
#            self.drawButton(elem,x,y,w=w,h=h)
        try :
            if elem["type"] == "pullMenu":
                ind = self.getLong(elem)
                if ind is None or len(elem["value"]) == 0 :
                    return None
                else :
                    return elem["value"][ind]
            if elem["type"] == "inputStr" or elem["type"] == "label":
                return self.getString(elem)
    #        elif elem["type"] == "inputStrArea":
    #            self.drawStringArea(elem,x,y,w=w,h=h)
            elif elem["type"] == "checkbox":
                return self.getBool(elem)
            elif elem["type"] == "sliders":
                return self.getReal(elem)        
            elif elem["type"] == "slidersInt":
                return self.getLong(elem)        
            elif elem["type"] == "inputInt":
                return self.getLong(elem)       
            elif elem["type"] == "inputFloat":
                return self.getReal(elem)       
    #        elif elem["type"] == "image":
    #            return self.getBool(elem)             
            elif elem["type"] == "color":
                return self.getColor(elem)       
#        elif elem["type"] == "label": 
#            return self.getBool(elem)       
        except :
            return elem["value"]
            
    def setVal(self,elem,val):
        """
        Set the value of the given widget
        
        @type  elem: dictionary widget
        @param elem: the widget    
        @type  val: X
        @param val: the new value for the widget
        """
        try :
            if elem["type"] == "pullMenu":
                if type(val) is str or type(val) is unicode:
                    val = list(elem["value"]).index(str(val))#or values?
                elif type(val) is list :
                    val = 0
                return self.setLong(elem,val)
            elif elem["type"] == "inputStr" or elem["type"] == "label":
                return self.setString(elem,str(val))
    #        elif elem["type"] == "inputStrArea":
    #            self.drawStringArea(elem,x,y,w=w,h=h)
            elif elem["type"] == "checkbox":
                return self.setBool(elem,val)
            elif elem["type"] == "sliders":
                return self.setReal(elem,val)        
            elif elem["type"] == "slidersInt":
                return self.setLong(elem,val)        
            elif elem["type"] == "inputInt":
                return self.setLong(elem,val)       
            elif elem["type"] == "inputFloat":
                return self.setReal(elem,val)       
    #        elif elem["type"] == "image":
    #            return self.getBool(elem)             
            elif elem["type"] == "color":
                return self.setColor(elem,val)
    #        elif elem["type"] == "label": 
    #            return self.getBool(elem)       
        except :
            pass
        
    def _createLayout(self):
        """
        Main function to initialised and draw the gui. The function setup the 
        windows, the tite, the menu, and call the draw function.
        
        @rtype:   boolean
        @return:  True
        """
        if self.title and (self.host == "blender24" or self.host == "maya" or self.host == 'c4d'):
            self.SetTitle(self.title) #set the title #in maya this will also setup the windows
        if self.MENU_ID :
            self.createMenu(self.MENU_ID,self.menuorder)
        self.startLayout()
        y=self.y
        if self.host == "blender24" and self.scrolling and self.block and self.subdialog:
            y = y +self.ystep
            self.drawSub(self._layout,y)
        else :
            for block in self._layout:
#                print type(block)
                y=self._draw(block,y)
        self.endLayout()
        return True

    def drawError(self,errormsg=""):
        """
        Open a dialog windows display the given error message.
        * overwrited by children class for each host
        """
        pass
    
    def startLayout(self,m=1,n=1):
        """
        Start the layout of the dialog
        * overwrited by children class for each host
        @type  m: int
        @param m: number of columns   
        @type  n: int
        @param n: number of rows         
        """
        pass
        
    def endLayout(self):
        """
        End the layout of the dialog
        * overwrited by children class for each host
        """
        pass

    def startBlock(self,m=1,n=1):
        """
        Start a block or group of widget in the current layout
        * overwrited by children class for each host
        
        @type  m: int
        @param m: number of columns   
        @type  n: int
        @param n: number of rows 
        """
        pass

    def endBlock(self):
        """
        End a block or group of widget in the current layout
        * overwrited by children class for each host
        """
        pass

    def handleMenuEvent(self,ev,menu):
        """ This function handle the particular menu event, especially for 
        submenu level action
        @type  ev: int
        @param ev: the current event
        @type  menu: dictionary
        @param menu: the current menu
        """ 
#        print ("menu",ev)
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


    def fileDialog(self,label="",callback=None):
        """
        Open a file dialog windows letting browse to a particular file.
        * overwrited by children class for each host
        
        @rtype:   string
        @return:  absolute filname
        """
        return None


    def close(self):
        """
        Close the dialog windows.
        * overwrited by children class for each host
        """
        pass

    def getDirectory(self):
        """
        Rreturn software directory for script and preferences
        * overwrited by children class for each host    
        """
        pass

    def SetTitle(self,title):
        """
        Change the name of the dialog, which will appear at the top of the dialog
        * overwrited by children class for each host
        
        @type  title: string
        @param title: the title of the dialog  
        """
        pass

    def drawGroup(self,elem,x,y,w=10,h=10):
        """
        Start a group of widget in the current layout
        * overwrited by children class for each host
        ***Not yet implemented***
        @type  elem: array or dictionary
        @param elem: list or dictionary of item dictionary
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

    def getHeightElems(self,bloc):
        """
        Return the sum of elem height for the give blocks
        Or return bloc heigh if any
        """
        if bloc["height"] is not None:
            return bloc["height"]
        H=0
        for k,blck in enumerate(bloc["elems"]):
            if type(blck) is list :
                if len(blck) == 0 :
                    continue
                ih=0
                for index, item in enumerate(blck):
                    ih+=item["height"]*self.scale
                if ih :
                    H+=math.ceil(float(ih)/len(blck))
            else : #dictionary: multiple line / format dict?
                H+=self.getHeightElems(blck)
        return int(H)
