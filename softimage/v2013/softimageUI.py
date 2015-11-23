
"""
    Copyright (C) <2010>  Autin L. TSRI
    
    This file git_upy/softimage/v2013/softimageUI.py is part of upy.

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
..............................c_updatePMenu
.


# -*- coding: utf-8 -*-
"""
Created on Thu Dec  2 13:45:52 2010

@author: -
"""
import os

from upy.uiAdaptor import uiAdaptor

from functools import partial

#XSIUIToolkit

#UI general interface
class softimageUI:
    """
    The maya uiAdaptor abstract class
    ====================================
        This Adaptor give access to the basic maya Draw function need for 
        create and display a gui.
    """
    
    host = "softimage"
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
    colorcmd = cmds.colorSliderGrp
    ystep = 1
    
#    def CoreMessage(self, id, msg):
#        """ Hanlde the system event such as key or mouse position """
##        print "id",id
##        print "msg",msg
#        return True
#        
#    def SetTitle(self,title):
#        """ Initialised the windows and define the windows titles 
#        @type  title: string
#        @param title: the window title
#
#        """        
#        self.title=title
#        self.winName= title.replace(" ","_")+"_gui"
##        print winName
##        print cmds.window(winName, q=1, exists=1)
#        res = cmds.window(self.winName, q=1, exists=1)
##        print res
#        if bool(res):
##            print winName, " exist"
#            cmds.deleteUI(self.winName, window=True)
##            print winName, " deleted"
#        winName = cmds.window(self.winName, menuBar=True,title=title,
#                    w=self.w*self.scale,h=self.h*self.scale)
#        self.winName = winName
##        cmds.window(self.winName,e=1,vis=True)
#        print self.winName, " created"
#        
#    def createMenu(self,menuDic,menuOrder=None):
#        """ Define and draw the window/widget top file menu
#        @type  menuDic: dictionary
#        @param menuDic: the menu elements, ie entry, callback and submenu
#        @type  menuOrder: array
#        @param menuOrder: the menu keys oredered
#        """        
#        
#        if menuOrder : 
#            lookat = menuOrder
#        else :
#            lookat = menuDic.keys()
#        for mitem in lookat:
#            cmds.menu( label=mitem, tearOff=True , parent = self.winName)
#            for elem in menuDic[mitem]:            
#                if elem["sub"] is not None:
#                    elem['id']=cmds.menuItem(subMenu=True, label=elem["name"])
#                    for sub in elem['sub'].keys():
#                        checkBox = False#elem['sub'][sub]['checkBox']
#                        if elem['sub'][sub]["action"] is not None :
#                            elem['sub'][sub]['id']=cmds.menuItem( label=elem['sub'][sub]["name"],
##                                                            checkBox=checkBox,
#                                                            c=partial(elem['sub'][sub]["action"],sub))
#                        else :
#                            elem['sub'][sub]['id']=cmds.menuItem( label=elem['sub'][sub]["name"],)
##                                                            checkBox=checkBox,)
##                        if checkBox and elem['sub'][sub].has_key("var"):
##                            cmds.menuItem(elem['sub'][sub]['id'],e=1,checkBox=bool(elem['sub'][sub]['var']))
#                    cmds.setParent( '..', menu=True )
#                else:
#                    if elem["action"] is not None :
#                        elem['id']=cmds.menuItem( label=elem["name"],c=elem["action"])
#                    else :
#                        elem['id']=cmds.menuItem( label=elem["name"])
#
#    def addVariable(self,type,value):
#        """ Create a container for storing a widget states """
#        return value
#    
#    def drawButton(self,elem,x,y,w=None,h=None):
#        """ Draw a Button 
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
#        if elem["action"] is not None :
#            elem["id"] = cmds.button( label=elem["name"], 
#                        w=elem["width"]*self.scale,
#                        h=elem["height"]*self.scale,
#                        c=partial(elem["action"],))
#        else :
#            elem["id"] = cmds.button( label=elem["name"],
#                        w=elem["width"]*self.scale,
#                        h=elem["height"]*self.scale)
#
#
#    def drawCheckBox(self,elem,x,y,w=None,h=None):
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
##        cmds.iconTextCheckBox( label='Sticks',style='iconAndTextHorizontal', 
##                                       image1=ICONSDIR+'bs.xpm', cc=self._displayBS )
#        if elem["action"] is not None :
#            elem["id"] = cmds.checkBox(label=elem["name"],cc=elem["action"])
#        else  :
#            elem["id"] = cmds.checkBox(label=elem["name"])
#
#    def resetPMenu(self,elem):
#        """ Add an entry to the given pulldown menu 
#        @type  elem: dictionary
#        @param elem: the pulldown dictionary
#        """
#        elem["value"]=[]
##        elem["variable"].val = len(elem["value"])
#        cmds.popupMenu(elem["id"],e=1,deleteAllItems=1)
#
#    def c_updatePMenu(self,id,item,action,arg=None):
#        """ special maya callback for the pulldown menu 
#        @type  id: int
#        @param id: id of the text widget that represent the pull-down menu
#        @type  elem: dictionary
#        @param elem: the pulldown dictionary
#        @type  action: function
#        @param action: the callback associate to the pulldown menu entry
#        @type  arg: args
#        @param arg: argument for the callback associate to the pulldown menu entry
#        """
#        cmds.text(id,e=1,l=str(item))
#        if action is not None :
#            action(item)
#
#    def drawPMenu(self,elem,x,y,w=None,h=None):
#        """ Draw a pulldown menu 
#        @type  elem: dictionary
#        @param elem: the pulldown dictionary
#        @type  x: int
#        @param x: position on x in the gui windows
#        @type  y: int
#        @param y: position on y in the gui windows
#        @type  w: int
#        @param w: force the width of the item
#        @type  h: int
#        @param h: force the height of the item
#        """                    
#        #currently use the popupMenu, so this always follow another widget
#        val = ""
#        if elem["value"] is not None :
#           if type(elem["value"]) is list or type(elem["value"]) is tuple:
#               if len(elem["value"]):
#                   val = elem["value"][0]
#        else :
#            val= ""
#        elem["variable"] = cmds.text( label=val )
#        elem["id"]=cmds.popupMenu( button=1 )
#        for item in elem["value"] :
#            cmds.menuItem(item,c=partial(self.c_updatePMenu,
#                                    elem["variable"],item,elem["action"]))
#
#    def addItemToPMenu(self,elem,item,w=None,h=None):
#        """ Add an entry to the given pulldown menu 
#        @type  elem: dictionary
#        @param elem: the pulldown dictionary
#        @type  item: string
#        @param item: the new entry
#        """        
#        elem["value"].append(item)
#        cmds.menuItem(p=elem["id"],l=str(item),c=partial(self.c_updatePMenu,
#                                          elem["variable"],item,elem["action"]))
#        cmds.text(elem["variable"],e=1,l=str(item))
#
#    def drawObj(self,elem,x,y,w=None,h=None):
#        """ Draw an object input where you can drag on object 
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
#        pass
#
#    def drawLine(self,elem,x,y,w=None,h=None):
#        """ Draw a Separative Line
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
#        if elem["value"] == "H":
#            hr=True
#        elif elem["value"] == "V":
#            hr=False
#        cmds.separator(w=self.w,style='single',hr=hr,ann=elem["label"])
#            
#    def drawLabel(self,label,x,y,w=None,h=None):
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
#        label["id"] = cmds.text( label=label["label"],
#                    w=label["width"]*self.scale,#*2,
#                    h=label["height"]*self.scale,
#                    align="left",
#                    recomputeSize=True)
#
#    def drawString(self,elem,x,y,w=None,h=None):
#        """ Draw a String input elem
#        @type  elem: dictionary
#        @param elem: the string input dictionary
#        @type  x: int
#        @param x: position on x in the gui windows
#        @type  y: int
#        @param y: position on y in the gui windows
#        @type  w: int
#        @param w: force the width of the item
#        @type  h: int
#        @param h: force the height of the item
#        """         
#        if elem["action"] is not None :
#            elem["id"] = cmds.textField(aie=True,
#                        w=elem["width"]*self.scale,
#                        h=elem["height"]*self.scale,
#                        enterCommand=elem["action"])
#        else :
#            elem["id"] = cmds.textField(aie=True,
#                        w=elem["width"]*self.scale,
#                        h=elem["height"]*self.scale)
#        if elem["value"] :
#            cmds.textField(elem["id"],e=True,tx=elem["value"])
#
#    def drawStringArea(self,elem,x,y,w=None,h=None):
#        """ Draw a String Area input elem, ie multiline
#        @type  elem: dictionary
#        @param elem: the string area input dictionary
#        @type  x: int
#        @param x: position on x in the gui windows
#        @type  y: int
#        @param y: position on y in the gui windows
#        @type  w: int
#        @param w: force the width of the item
#        @type  h: int
#        @param h: force the height of the item
#        """          
#        elem["id"] = cmds.cmdScrollFieldExecuter(w=elem["width"]*self.scale,
#                                                 h=elem["height"]*self.scale, 
#                                                 sourceType="python")
#        cmds.cmdScrollFieldExecuter(elem["id"],e=1,t=elem["value"])
#    
#    def drawSliders(self,elem,x,y,w=None,h=None):
#        """ Draw a Slider elem, the variable/value of the elem define the slider format
#        @type  elem: dictionary
#        @param elem: the slider input dictionary
#        @type  x: int
#        @param x: position on x in the gui windows
#        @type  y: int
#        @param y: position on y in the gui windows
#        @type  w: int
#        @param w: force the width of the item
#        @type  h: int
#        @param h: force the height of the item
#        """                
#        if elem["value"] is None :
#            elem["value"] = 0
#        if elem["value"] > elem["maxi"] :
#            elem["maxi"] = elem["value"]+10
#        if elem["value"] < elem["mini"] :
#            elem["mini"] = elem["value"]-10        
#        elem["label"] = "A"       
#        if elem["type"] == "slidersInt":
#            cmd = cmds.intSliderGrp
#            if elem["action"] is not None : #label=elem["label"],
#                elem["id"] = cmd(  field=True,
#                                                w=elem["width"]*self.scale,
#                                                h=elem["height"]*self.scale,
#                                                  minValue=elem["mini"], 
#                                                  maxValue=elem["maxi"], 
#                                                  fieldMinValue=elem["mini"], 
#                                                  fieldMaxValue=elem["maxi"],
#                                                  value=elem["variable"] , 
#                                                  step=elem["step"],
#                                                  dc=elem["action"],
#                                                  cc=elem["action"],
#                                                  cal=[1,"left"],
#                                                  cat=[1,"left",0])
#            else :
#                elem["id"] = cmds.floatSliderGrp(  field=True,
#                                                w=elem["width"]*self.scale,
#                                                h=elem["height"]*self.scale,            
#                                                  minValue=elem["mini"], 
#                                                  maxValue=elem["maxi"], 
#                                                  fieldMinValue=elem["mini"], 
#                                                  fieldMaxValue=elem["maxi"], 
#                                                  value=elem["variable"] , 
#                                                  step=elem["step"],
#                                                  cal=[1,"left"])
#        else :
#            cmd = cmds.floatSliderGrp
#            if elem["action"] is not None : #label=elem["label"],
#                elem["id"] = cmd(  field=True,
#                                                w=elem["width"]*self.scale,
#                                                h=elem["height"]*self.scale,
#                                                  minValue=elem["mini"], 
#                                                  maxValue=elem["maxi"], 
#                                                  fieldMinValue=elem["mini"], 
#                                                  fieldMaxValue=elem["maxi"],
#                                                  precision = int(elem["precision"]), 
#                                                  value=elem["variable"] , 
#                                                  step=elem["step"],
#                                                  dc=elem["action"],
#                                                  cc=elem["action"],
#                                                  cal=[1,"left"],
#                                                  cat=[1,"left",0])
#            else :
#                elem["id"] = cmds.floatSliderGrp(  field=True,
#                                                w=elem["width"]*self.scale,
#                                                h=elem["height"]*self.scale,            
#                                                  minValue=elem["mini"], 
#                                                  maxValue=elem["maxi"], 
#                                                  fieldMinValue=elem["mini"], 
#                                                  fieldMaxValue=elem["maxi"],
#                                                  precision = int(elem["precision"]), 
#                                                  value=elem["variable"] , 
#                                                  step=elem["step"],
#                                                  cal=[1,"left"])
#
#    def drawNumbers(self,elem,x,y,w=None,h=None):
#        """ Draw a Int input elem
#        @type  elem: dictionary
#        @param elem: the Int input dictionary
#        @type  x: int
#        @param x: position on x in the gui windows
#        @type  y: int
#        @param y: position on y in the gui windows
#        @type  w: int
#        @param w: force the width of the item
#        @type  h: int
#        @param h: force the height of the item
#        """
#        if elem["value"] is None :
#            elem["value"] = 0
#        if elem["value"] > elem["maxi"] :
#            elem["maxi"] = elem["value"]+10
#        if elem["value"] < elem["mini"] :
#            elem["mini"] = elem["value"]-10        
#        #print int(elem["mini"]),int(elem["maxi"]),int(elem["value"]),int(elem["step"])
#        if elem["action"] is not None :
#            elem["id"] = cmds.intField(w=elem["width"]*self.scale,
#                                h=elem["height"]*self.scale,            
#                                minValue=int(elem["mini"]), 
#                                maxValue=int(elem["maxi"]),
#                                value=int(elem["value"]) , 
#                                step=int(elem["step"]),
#                                dc=elem["action"],
#                                cc=elem["action"],
#                                ec=elem["action"],)
#        else :                        
#            elem["id"] = cmds.intField(w=elem["width"]*self.scale,
#                                h=elem["height"]*self.scale,            
#                                minValue=int(elem["mini"]), 
#                                maxValue=int(elem["maxi"]),
#                                value=int(elem["value"]) , 
#                                step=int(elem["step"]),
#                                )
#
#    def drawFloat(self,elem,x,y,w=None,h=None):
#        """ Draw a Int input elem
#        @type  elem: dictionary
#        @param elem: the Int input dictionary
#        @type  x: int
#        @param x: position on x in the gui windows
#        @type  y: int
#        @param y: position on y in the gui windows
#        @type  w: int
#        @param w: force the width of the item
#        @type  h: int
#        @param h: force the height of the item
#        """  
#        if elem["value"] is None :
#            elem["value"] = 0
#        if elem["value"] > elem["maxi"] :
#            elem["maxi"] = elem["value"]+10
#        if elem["value"] < elem["mini"] :
#            elem["mini"] = elem["value"]-10        
#        if elem["maxi"] < elem["mini"] :
#            elem["maxi"] = elem["mini"]
#        if elem["step"] >= float(elem["maxi"]-elem["mini"]):
#            elem["step"] = float(elem["maxi"]-elem["mini"])/2.
#            #print "step",elem["step"]
#        #print "ok",elem["mini"],elem["maxi"],elem["step"]
#        if elem["action"] is not None :
#            elem["id"] = cmds.floatField(w=elem["width"]*self.scale,
#                                h=elem["height"]*self.scale,            
#                                minValue=float(elem["mini"]), 
#                                maxValue=float(elem["maxi"]),
#                                value=float(elem["value"]) , 
#                                step=float(elem["step"]),
#                                dc=elem["action"],
#                                cc=elem["action"],
#                                ec=elem["action"],)
#        else :                        
#            elem["id"] = cmds.floatField(w=elem["width"]*self.scale,
#                                h=elem["height"]*self.scale,            
#                                minValue=float(elem["mini"]), 
#                                maxValue=float(elem["maxi"]),
#                                value=float(elem["value"]) , 
#                                step=float(elem["step"]),
#                                )
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
#        cmds.picture( image=elem["value"])
#
#    def drawColorField(self,elem,x,y,w=None,h=None):
#        """ Draw a Color entry Field
#        @type  elem: dictionary
#        @param elem: the color input dictionary
#        @type  x: int
#        @param x: position on x in the gui windows
#        @type  y: int
#        @param y: position on y in the gui windows
#        @type  w: int
#        @param w: force the width of the item
#        @type  h: int
#        @param h: force the height of the item
#        """
#        elem["label"] = None
#        if elem["width"] == 10:
#            elem["width"] = 25
#        if elem["action"] is not None :
#            if elem["label"]is not None:
#                elem["id"] = self.colorcmd(elem["name"],w=50,
#                                #h=elem["height"]*self.scale,  
#                                label=elem["label"],
#                                            rgb=(1, 0, 0), 
#                                            #symbolButtonDisplay=False,
#                                            #bl = 'color',
#                                            #bc = elem["action"],
#                                            cc = elem["action"])
#            else:
#                elem["id"] = self.colorcmd(elem["name"],#symbolButtonDisplay=False,bl = 'color',
#                rgb=(1, 0, 0),w=50,cc = elem["action"])
#        else :
#            if elem["label"] is not None:
#                elem["id"] = self.colorcmd(elem["name"],w=50,
#                                #h=elem["height"]*self.scale,  
#                                label=elem["label"],
#                                            rgb=(1, 0, 0), bl = 'color',)
#                                            #symbolButtonDisplay=False,)
#                                            #bl = 'color')
#            else :
#                elem["id"] = self.colorcmd(elem["name"],#symbolButtonDisplay=False,bl = 'color',
#                rgb=(1, 0, 0),w=50,)
#        if elem["value"] is not None:
#            self.setColor(elem,elem["value"][0:3])
#
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
#        result = cmds.promptDialog(title=title,
#                message=question,
#                button=['OK', 'Cancel'],
#                defaultButton='OK',
#                cancelButton='Cancel',
#                dismissString='Cancel')
#        if result == 'OK':
#            text = cmds.promptDialog(query=True, text=True)
#            if callback is not None :
#                callback(text)
#            else :
#                return text
#
#    def drawError(self,errormsg=""):
#        """ Draw a error message dialog
#        @type  errormsg: string
#        @param errormsg: the messag to display
#        """          
#        cmds.confirmDialog(title='ERROR:', message=errormsg, button=['OK'], 
#                           defaultButton='OK')
# 
#    def drawQuestion(self,title="",question=""):
#        """ Draw a Question message dialog, requiring a Yes/No answer
#        @type  title: string
#        @param title: the windows title       
#        @type  question: string
#        @param question: the question to display
#        
#        @rtype:   bool
#        @return:  the answer     
#        """        
#        res = cmds.confirmDialog( title=title, message=question, 
#                                button=['Yes','No'],
#                                defaultButton='Yes',
#                                cancelButton='No', dismissString='No')
#        if res == 'Yes': 
#            return True
#        else :
#            return False
#
#    def drawMessage(self,title="",message=""):
#        """ Draw a message dialog
#        @type  title: string
#        @param title: the windows title       
#        @type  message: string
#        @param message: the message to display   
#        """                    
#        cmds.confirmDialog( title=title, message=message, 
#                            button=['OK'], 
#                            defaultButton='OK')
#        
#    def drawTab(self,bloc,x,y):
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
#        print "drawTab",bloc["name"]
#        print "nb",self.notebook
#        if self.notebook is None :
#            self.notebook = {}
#            self.notebook["id"] = cmds.tabLayout(w=self.w*self.scale*2)#borderStyle='in' ,
#            print "ok", self.notebook["id"]
#            self.notebook["tab"]={}#.append(bloc["name"])
#        self.notebook["tab"][bloc["name"]] =  bloc["id"]
##        bloc["id"] = cmds.shelfLayout(bloc["name"],w=self.w*self.scale)
#        bloc["id"] = cmds.scrollLayout(bloc["name"],w=self.w*self.scale,h=200)
##        bloc["id"] = cmds.frameLayout(bloc["name"],w=self.w*self.scale,
##                        labelVisible=False,borderVisible=False)
#        for k,blck in enumerate(bloc["elems"]):
#            #print bloc["name"],len(blck)
#            cmds.rowLayout(numberOfColumns=len(blck),w=self.w*self.scale)
#            for index, item in enumerate(blck):
#                self._drawElem(item,x,y)
#            self.endBlock()
#        #if bloc["name"] not in self.notebook["tab"].values():
#        self.notebook["tab"][bloc["name"]] =  bloc["id"]
#        self.endBlock()
##        self.endBlock()
#        cmds.tabLayout( self.notebook["id"], edit=True, tabLabel=(bloc["id"], bloc["name"]) )
#        return y
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
#        cmds.frameLayout( label=bloc["name"], collapsable=True,
#                             cl=bloc["collapse"],borderVisible=False,
#                             w=self.w*self.scale)#borderStyle='in' ,
#        for k,blck in enumerate(bloc["elems"]):
#            #print bloc["name"],len(blck)
#            cmds.rowLayout(numberOfColumns=len(blck),w=self.w*self.scale)
#            for index, item in enumerate(blck):
#                self._drawElem(item,x,y)
#            self.endBlock()
#        self.endBlock()
#        return y
#
#    def saveDialog(self,label="",callback=None):
#        """ Draw a File input dialog
#        @type  label: string
#        @param label: the windows title       
#        @type  callback: function
#        @param callback: the callback function to call
#        """         
#        filename = cmds.fileDialog(t=label,m=1)
#        callback(str(filename))
#
#    def fileDialog(self,label="",callback=None):
#        """ Draw a File input dialog
#        @type  label: string
#        @param label: the windows title       
#        @type  callback: function
#        @param callback: the callback function to call
#        """         
#        filename = cmds.fileDialog(t=label)
#        callback(str(filename))
#
#    def waitingCursor(self,toggle):
#        """ Toggle the mouse cursor appearance from the busy to idle.
#        @type  toggle: Bool
#        @param toggle: Weither the cursor is busy or idle 
#        """     
#        pass
#        
#    def updateViewer(self):
#        """
#        update the 3d windows if any
#        """        
#        cmds.refresh()
#        
#    def startBlock(self,m=1,n=1):
#        #currently i will just make basic layou using the rawLayout
##        columnWidth=[]
##        for i in range(1,m):
##            columnWidth.append([i,80])#[(1, 60), (2, 80), (3, 100)]
##        cmds.rowColumnLayout(numberOfColumns=m,columnWidth=columnWidth)
##        cmds.flowLayout(wr=True)
#        if m==0:
#            cmds.flowLayout(wr=True,w=self.w*self.scale)
#        else :
#            cmds.rowLayout(numberOfColumns=m,w=self.w*self.scale)
##            cmds.gridLayout(numberOfColumns=m,autoGrow=True,columnsResizable=True)
##        if m==2 :
##            cmds.rowLayout(numberOfColumns=2)
##        else :
###            cmds.flowLayout(wr=True)
##            cmds.gridLayout(numberOfColumns=m,autoGrow=True,columnsResizable=True)
###            cmds.rowLayout(numberOfColumns=m,adjustableColumn=m)
###        
#    def endBlock(self):
#        cmds.setParent('..')
#
#    def startLayout(self,m=1,n=1):
##        cmds.frameLayout( cll=True,label='ePMV')
#        cmds.scrollLayout( 'scrollLayout',w=self.w*self.scale)
##        cmds.columnLayout( adjustableColumn=True )
#        
#    def endLayout(self):
#        #cmds.window( gMainWindow, edit=True, widthHeight=(900, 777) )
#        if self.subdialog:
#            cmds.showWindow(self.winName)
#        elif self.dock  :
#            allowedAreas = ['right', 'left']
#            cmds.dockControl(self.winName, l=self.title,area='left', content=self.winName, 
#                         allowedArea=allowedAreas )
#        else :
#            cmds.showWindow(self.winName)
#
#
#    def setReal(self,elem,val):
#        """ Set the current Float value of the Float input elem
#        @type  elem: dictionary
#        @param elem: the elem input dictionary       
#        @type  val: Float
#        @param val: the new Float value
#        """                                
#        #to do interpret the elem["type"] to call the correct function
#        if elem["type"] == 'sliders':
#            cmds.floatSliderGrp(elem["id"],e=1,v=val)
#        elif elem["type"] == "inputInt":
#            cmds.intField(elem["id"],e=1,v=val)
#        elif elem["type"] == "inputFloat":
#            cmds.floatField(elem["id"],e=1,v=val)
#
#    def getReal(self,elem):
#        """ Return the current Float value of the Input elem
#        @type  elem: dictionary
#        @param elem: the elem input dictionary       
#        
#        @rtype:   Float
#        @return:  the current Float value input for this specific elem
#        """                                
#        #to do interpret the elem["type"] to call the correct function
#        #have to look at the type too
#        if elem["type"] == 'sliders':
#            return cmds.floatSliderGrp(elem["id"],q=1,v=1)
#        elif elem["type"] == "inputInt":
#            return float(cmds.intField(elem["id"],q=1,v=1))
#        elif elem["type"] == "inputFloat":
#            return float(cmds.floatField(elem["id"],q=1,v=1))
#        
#    def getBool(self,elem):
#        """ Return the current Bool value of the Input elem
#        @type  elem: dictionary
#        @param elem: the elem input dictionary       
#        
#        @rtype:   Bool
#        @return:  the current Bool value input for this specific elem
#        """ 
#        if elem["type"] == 'checkbox':
#            return cmds.checkBox(elem["id"],q=1,v=1)
#
#    def setBool(self,elem,val):
#        """ Set the current Bool value of the Bool input elem
#        @type  elem: dictionary
#        @param elem: the elem input dictionary       
#        @type  val: Bool
#        @param val: the new Bool value
#        """                      
#        cmds.checkBox(elem["id"],e=1,v=val)
#
#    def getString(self,elem):
#        """ Return the current string value of the String Input elem
#        @type  elem: dictionary
#        @param elem: the elem input dictionary       
#        
#        @rtype:   string
#        @return:  the current string input value for this specific elem
#        """  
#        if elem["type"] =="label":
#            return str(cmds.text(elem["id"],q=1,label=1))
#        else :
#            return str(cmds.textField(elem["id"],q=1,tx=1))
#
#    def setString(self,elem,val):
#        """ Set the current String value of the string input elem
#        @type  elem: dictionary
#        @param elem: the elem input dictionary       
#        @type  val: string
#        @param val: the new string value    
#        """         
#        if elem["type"] =="label":
#            cmds.text(elem["id"],e=1,label=val)
#        else :
#            cmds.textField(elem["id"],e=1,tx=val)
#
#    def getStringArea(self,elem):
#        """ Return the current string area value of the String area Input elem
#        @type  elem: dictionary
#        @param elem: the elem input dictionary       
#        
#        @rtype:   string
#        @return:  the current string area input value for this specific elem
#        """                
#        return cmds.cmdScrollFieldExecuter(elem["id"],q=1,t=1)
#
#    def setStringArea(self,elem,val):
#        """ Set the current String area value of the string input elem
#        @type  elem: dictionary
#        @param elem: the elem input dictionary       
#        @type  val: string
#        @param val: the new string value (multiline)   
#        """                        
#        cmds.cmdScrollFieldExecuter(elem["id"],e=1,tx=val)
#
#    def getLong(self,elem):
#        """ Return the current Int value of the Input elem
#        @type  elem: dictionary
#        @param elem: the elem input dictionary       
#        
#        @rtype:   Int
#        @return:  the current Int value input for this specific elem
#        """
#        print elem["type"]
#        if elem["type"] == "inputInt":
#            return cmds.intField(elem["id"],q=1,v=1)
#        elif elem["type"] == "sliders":
#            return int(cmds.floatSliderGrp(elem["id"],q=1,v=1))
#        elif elem["type"] == "inputFloat":
#            return int(cmds.floatField(elem["id"],q=1,v=1))
#        else:
#            #specific command for menulike
#            str = cmds.text(elem["variable"],q=1,l=1)
#            return elem["value"].index(str) #maya combo menu is a txt + pulldown menu
#
#    def setLong(self,elem,val):
#        """ Set the current Int value of the Int input elem
#        @type  elem: dictionary
#        @param elem: the elem input dictionary       
#        @type  val: Int
#        @param val: the new Int value
#        """                                
#        if elem["type"] == "inputInt":
#            cmds.intField(elem["id"],e=1,v=val)
#        elif elem["type"] == "inputFloat":
#            cmds.floatField(elem["id"],e=1,v=val)
#        else:
#            if type(val) is int  :
#                val = elem["value"][val]
#            cmds.text(elem["variable"],e=1,l=val)
#
#    def getColor(self,elem):
#        """ Return the current Color value of the Input elem
#        @type  elem: dictionary
#        @param elem: the elem input dictionary       
#        
#        @rtype:   Color
#        @return:  the current Color array RGB value input for this specific elem
#        """                        
#        return self.colorcmd(elem["id"],q=1,rgb=1)
#
#    def setColor(self,elem,val):
#        """ Set the current Color rgb arrray value of the Color input elem
#        @type  elem: dictionary
#        @param elem: the elem input dictionary       
#        @type  val: Color
#        @param val: the new Color value
#        """                        
#        self.colorcmd(elem["id"],e=1,rgb=val[0:3])
#
#    def updateSlider(self,elem,mini,maxi,default,step):
#        """ Update the state of the given slider, ie format, min, maxi, step
#        @type  elem: dictionary
#        @param elem: the slider elem dictionary       
#        @type  maxi: int/float
#        @param maxi: max value for the item, ie slider
#        @type  mini: int/float
#        @param mini: min value for the item, ie slider
#        @type  default: int/float
#        @param default: default value for the item, ie slider
#        @type  step: int/float
#        @param step: step value for the item, ie slider
#        """                
#        cmds.floatSliderGrp(elem["id"],e=1,minValue=float(mini), maxValue=float(maxi), 
#                                               fieldMinValue=float(mini), 
#                                               fieldMaxValue=float(maxi),
#                                               value=float(default),
#                                               step=float(step))
#                                               
#    @classmethod                                          
#    def _restore(self,rkey,dkey=None):
#        """
#        Function used to restore the windows data, usefull for plugin
#        @type  rkey: string
#        @param rkey: the key to access the data in the registry/storage       
#        @type  dkey: string
#        @param dkey: wiether we want a particular data from the stored dic
#        """        
#        if hasattr(maya,rkey):
#            obj = maya.__dict__[rkey]
#            if dkey is not None:
#                if maya.__dict__[rkey].has_key(dkey) :
#                    return  maya.__dict__[rkey][dkey]       
#                else :
#                    return None
#            return obj
#        else :
#            return None
#    
#    @classmethod
#    def _store(self,rkey,dict):
#        """
#        Function used to store the windows data, usefull for plugin
#        @type  rkey: string
#        @param rkey: the key to access the data in the registry/storage       
#        @type  dict: dictionary
#        @param dict: the storage is done throught a dictionary
#        """         
#        maya.__dict__[rkey]= dict
#
#    def drawSubDialog(self,dial,id,callback=None,asynchro = True):
#        """
#        Draw the given subdialog whit his own element and callback
#        
#        @type  dial: dialog Object
#        @param dial: the dialog object to be draw
#        @type  id: int
#        @param id: the id of the dialog
#        @type  callback: function
#        @param callback: the associate callback
#        """        
#        dial.CreateLayout()
#
#    def close(self,*args):
#        """ Close the windows"""
##        res = cmds.window(self.winName, q=1, exists=1)
##        print res
##        if bool(res):
##            print winName, " exist"
##            cmds.deleteUI(self.winName, window=True)
##            cmds.window(self.winName,e=1,vis=False)#this delete the windows...
#        if self.subdialog:
#            cmds.window(self.winName,e=1,vis=False)
#        elif self.dock  :
#            cmds.dockControl(self.winName, e=1,vis=False)
#        else :
#            cmds.window(self.winName,e=1,vis=False)
#
#    def display(self):
#        """ Create and Open the current gui windows """
#        self.CreateLayout()
#
#    def getDirectory(self):
#        """return software directory for script and preferences"""
#        self.prefdir=cmds.internalVar(userPrefDir=True)
#        os.chdir(self.prefdir)
#        os.chdir('../')
#        self.softdir = os.path.abspath(os.curdir)+os.sep+"plug-ins"
#        print "soft ",self.softdir 
#        plugdirs = os.environ['MAYA_PLUG_IN_PATH'].split(":")     
#        if self.softdir not in plugdirs :
#            if plugdirs[0].find("mMaya") != -1 :
#                self.softdir = plugdirs[1]
#            else :
#                if type(plugdirs) is list or type(plugdirs) is tuple:
#                    self.softdir = plugdirs[0]
#                else :
#                    self.softdir = plugdirs
#        print plugdirs

            
class softimageUIDialog(mayaUI,uiAdaptor):
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

