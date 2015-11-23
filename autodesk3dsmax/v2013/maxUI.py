
"""
    Copyright (C) <2010>  Autin L. TSRI
    
    This file git_upy/autodesk3dsmax/v2013/maxUI.py is part of upy.

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
import os
import MaxPlus
from upy.uiAdaptor import uiAdaptor

from functools import partial

#XSIUIToolkit

#UI general interface
class maxUI:
    """
    The maya uiAdaptor abstract class
    ====================================
        This Adaptor give access to the basic maya Draw function need for 
        create and display a gui.
    """
    
    host = "3dsmax"
    scale = 2
    maxStrLenght=100
    left, top, right, bottom =(10,10,10,1)
    bid=1
    title=""
    winName=""
    subdialog = False
    dock = True
    w=200
    h=100
    notebook = None
    #colorcmd = cmds.colorSliderGrp
    ystep = 1
    
    def CoreMessage(self, id, msg):
        """ Hanlde the system event such as key or mouse position """
        return True
        
    def SetTitle(self,title):
        """ Initialised the windows and define the windows titles 
        @type  title: string
        @param title: the window title

        """        
        self.title=title
        self.winName= title.replace(" ","_")+"_gui"
        
    def createMenu(self,menuDic,menuOrder=None):
        """ Define and draw the window/widget top file menu
        @type  menuDic: dictionary
        @param menuDic: the menu elements, ie entry, callback and submenu
        @type  menuOrder: array
        @param menuOrder: the menu keys oredered
        """        
        return

    def addVariable(self,type,value):
        """ Create a container for storing a widget states """
        return value
    
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
        pass


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
        pass

    def resetPMenu(self,elem):
        """ Add an entry to the given pulldown menu 
        @type  elem: dictionary
        @param elem: the pulldown dictionary
        """
        pass


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
        #currently use the popupMenu, so this always follow another widget
        pass

    def addItemToPMenu(self,elem,item,w=None,h=None):
        """ Add an entry to the given pulldown menu 
        @type  elem: dictionary
        @param elem: the pulldown dictionary
        @type  item: string
        @param item: the new entry
        """        
        pass

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
        pass
            
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
        pass

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
        pass

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
        pass
    
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
        pass

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
        pass

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
        pass

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
        pass

    def drawInputQuestion(self,title="",question="",callback=None):
        """ Draw an Input Question message dialog, requiring a string answer
        @type  title: string
        @param title: the windows title       
        @type  question: string
        @param question: the question to display
        
        @rtype:   string
        @return:  the answer     
        """                  
        pass

    def drawError(self,errormsg=""):
        """ Draw a error message dialog
        @type  errormsg: string
        @param errormsg: the messag to display
        """          
        pass
 
    def drawQuestion(self,title="",question=""):
        """ Draw a Question message dialog, requiring a Yes/No answer
        @type  title: string
        @param title: the windows title       
        @type  question: string
        @param question: the question to display
        
        @rtype:   bool
        @return:  the answer     
        """        
        return False

    def drawMessage(self,title="",message=""):
        """ Draw a message dialog
        @type  title: string
        @param title: the windows title       
        @type  message: string
        @param message: the message to display   
        """                    
        pass
        
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
        pass

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
        pass

    def saveDialog(self,label="",callback=None):
        """ Draw a File input dialog
        @type  label: string
        @param label: the windows title       
        @type  callback: function
        @param callback: the callback function to call
        """         
        pass

    def fileDialog(self,label="",callback=None):
        """ Draw a File input dialog
        @type  label: string
        @param label: the windows title       
        @type  callback: function
        @param callback: the callback function to call
        """         
        pass

    def waitingCursor(self,toggle):
        """ Toggle the mouse cursor appearance from the busy to idle.
        @type  toggle: Bool
        @param toggle: Weither the cursor is busy or idle 
        """     
        pass
        
    def updateViewer(self):
        """
        update the 3d windows if any
        """        
        MaxPlus.Core.Interface.ForceCompleteRedraw()
        
    def startBlock(self,m=1,n=1):
        #currently i will just make basic layou using the rawLayout
        pass
#        
    def endBlock(self):
        pass

    def startLayout(self,m=1,n=1):
        pass
        
    def endLayout(self):
        pass


    def setReal(self,elem,val):
        """ Set the current Float value of the Float input elem
        @type  elem: dictionary
        @param elem: the elem input dictionary       
        @type  val: Float
        @param val: the new Float value
        """                                
        #to do interpret the elem["type"] to call the correct function
        pass

    def getReal(self,elem):
        """ Return the current Float value of the Input elem
        @type  elem: dictionary
        @param elem: the elem input dictionary       
        
        @rtype:   Float
        @return:  the current Float value input for this specific elem
        """                                
        #to do interpret the elem["type"] to call the correct function
        #have to look at the type too
        pass
        
    def getBool(self,elem):
        """ Return the current Bool value of the Input elem
        @type  elem: dictionary
        @param elem: the elem input dictionary       
        
        @rtype:   Bool
        @return:  the current Bool value input for this specific elem
        """ 
        pass
    
    def setBool(self,elem,val):
        """ Set the current Bool value of the Bool input elem
        @type  elem: dictionary
        @param elem: the elem input dictionary       
        @type  val: Bool
        @param val: the new Bool value
        """                      
        pass

    def getString(self,elem):
        """ Return the current string value of the String Input elem
        @type  elem: dictionary
        @param elem: the elem input dictionary       
        
        @rtype:   string
        @return:  the current string input value for this specific elem
        """  
        pass

    def setString(self,elem,val):
        """ Set the current String value of the string input elem
        @type  elem: dictionary
        @param elem: the elem input dictionary       
        @type  val: string
        @param val: the new string value    
        """         
        pass

    def getStringArea(self,elem):
        """ Return the current string area value of the String area Input elem
        @type  elem: dictionary
        @param elem: the elem input dictionary       
        
        @rtype:   string
        @return:  the current string area input value for this specific elem
        """                
        pass

    def setStringArea(self,elem,val):
        """ Set the current String area value of the string input elem
        @type  elem: dictionary
        @param elem: the elem input dictionary       
        @type  val: string
        @param val: the new string value (multiline)   
        """                        
        pass

    def getLong(self,elem):
        """ Return the current Int value of the Input elem
        @type  elem: dictionary
        @param elem: the elem input dictionary       
        
        @rtype:   Int
        @return:  the current Int value input for this specific elem
        """
        pass

    def setLong(self,elem,val):
        """ Set the current Int value of the Int input elem
        @type  elem: dictionary
        @param elem: the elem input dictionary       
        @type  val: Int
        @param val: the new Int value
        """                                
        pass

    def getColor(self,elem):
        """ Return the current Color value of the Input elem
        @type  elem: dictionary
        @param elem: the elem input dictionary       
        
        @rtype:   Color
        @return:  the current Color array RGB value input for this specific elem
        """                        
        pass

    def setColor(self,elem,val):
        """ Set the current Color rgb arrray value of the Color input elem
        @type  elem: dictionary
        @param elem: the elem input dictionary       
        @type  val: Color
        @param val: the new Color value
        """                        
        pass

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
        pass
                                               
    #@classmethod                                          
    def _restore(self,rkey,dkey=None):
        """
        Function used to restore the windows data, usefull for plugin
        @type  rkey: string
        @param rkey: the key to access the data in the registry/storage       
        @type  dkey: string
        @param dkey: wiether we want a particular data from the stored dic
        """        
        if hasattr(MaxPlus,rkey):
            obj = MaxPlus.__dict__[rkey]
            if dkey is not None:
                if MaxPlus.__dict__[rkey].has_key(dkey) :
                    return  MaxPlus.__dict__[rkey][dkey]       
                else :
                    return None
            return obj
        else :
            return None
    
    #@classmethod
    def _store(self,rkey,dict):
        """
        Function used to store the windows data, usefull for plugin
        @type  rkey: string
        @param rkey: the key to access the data in the registry/storage       
        @type  dict: dictionary
        @param dict: the storage is done throught a dictionary
        """         
        MaxPlus.__dict__[rkey]= dict

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
        pass

    def close(self,*args):
        """ Close the windows"""
        pass

    def display(self):
        """ Create and Open the current gui windows """
        pass

    def getDirectory(self):
        """return software directory for script and preferences"""
        pass

            
class maxUIDialog(maxUI,uiAdaptor):
    def __init__(self,**kw):
        if kw.has_key("title"):
            self.title= kw["title"]
#        
#
#
#class mayaUISubDialog(mayaUIDialog):
#    def __init__(self,):
#        mayaUIDialog.__init__(self,)
#        

