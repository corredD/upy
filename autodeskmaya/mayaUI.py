
"""
    Copyright (C) <2010>  Autin L. TSRI
    
    This file git_upy/autodeskmaya/mayaUI.py is part of upy.

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
import maya
import maya.cmds as cmds
import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx

from upy.uiAdaptor import uiAdaptor

from functools import partial

#UI general interface
class mayaUI:
    """
    The maya uiAdaptor abstract class
    ====================================
        This Adaptor give access to the basic maya Draw function need for 
        create and display a gui.
    """
    
    host = "maya"
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
    created = False
    inNotebook= False
    afterNoteBook = None
    mainlayout = None
    
    def CoreMessage(self, id, msg):
        """ Hanlde the system event such as key or mouse position """
#        print "id",id
#        print "msg",msg
        return True
        
    def SetTitle(self,title):
        """ Initialised the windows and define the windows titles 
        @type  title: string
        @param title: the window title

        """        
        self.title=title
        self.winName= title.replace(" ","_").replace(".","_")+"_gui"
#        print winName
#        print cmds.window(winName, q=1, exists=1)
        res = cmds.window(self.winName, q=1, exists=1)
#        print res
        if bool(res):
#            print self.winName, " exist"
            cmds.deleteUI(self.winName, window=True)
#            print self.winName, " deleted"
        #chec for the dock one
        res = cmds.dockControl(self.winName, q=1, exists=1)
#        print res
        if bool(res):
#            print self.winName+"dock", " exist"
            cmds.deleteUI(self.winName, control=True)
#            print self.winName, " deleted"
        winName = cmds.window(self.winName, menuBar=True,title=title,
                    w=self.w*self.scale,h=self.h*self.scale)
        print ("settitle ",winName, self.winName, winName==self.winName)
        self.winName = winName
#        cmds.window(self.winName,e=1,vis=True)
        print self.winName, " created"
        
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
        for mitem in lookat:
            cmds.menu( label=mitem, tearOff=True , parent = self.winName)
            for elem in menuDic[mitem]:            
                if elem["sub"] is not None:
                    elem['id']=cmds.menuItem(subMenu=True, label=elem["name"])
                    for sub in elem['sub'].keys():
                        checkBox = False#elem['sub'][sub]['checkBox']
                        if elem['sub'][sub]["action"] is not None :
                            elem['sub'][sub]['id']=cmds.menuItem( label=elem['sub'][sub]["name"],
#                                                            checkBox=checkBox,
                                                            c=partial(elem['sub'][sub]["action"],sub))
                        else :
                            elem['sub'][sub]['id']=cmds.menuItem( label=elem['sub'][sub]["name"],)
#                                                            checkBox=checkBox,)
#                        if checkBox and elem['sub'][sub].has_key("var"):
#                            cmds.menuItem(elem['sub'][sub]['id'],e=1,checkBox=bool(elem['sub'][sub]['var']))
                    cmds.setParent( '..', menu=True )
                else:
                    if elem["action"] is not None :
                        elem['id']=cmds.menuItem( label=elem["name"],c=elem["action"])
                    else :
                        elem['id']=cmds.menuItem( label=elem["name"])

    def addVariable(self,type,value):
        """ Create a container for storing a widget states """
        return value

    def getFlagAlignement(self,options):
        alignement = {"hleft_scale":"",
                  "hcenter_scale":"",
                  "hleft":"",
                  "hfit":"",
                  "hfit_scale":"",
                  "hcenter":"",
                  }
        return ""#alignement[options]
    
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
        name = elem["name"]
        if elem["label"] != None:
            name = elem["label"]
        if elem["action"] is not None :
            elem["id"] = cmds.button( label=name, 
                        w=elem["width"]*self.scale,
                        h=elem["height"]*self.scale,
                        c=partial(elem["action"],),
                        recomputeSize=False)
        else :
            elem["id"] = cmds.button( label=name,
                        w=elem["width"]*self.scale,
                        h=elem["height"]*self.scale,recomputeSize=False)


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
#        cmds.iconTextCheckBox( label='Sticks',style='iconAndTextHorizontal', 
#                                       image1=ICONSDIR+'bs.xpm', cc=self._displayBS )
        name = elem["name"]
        if elem["label"] != None:
            name = elem["label"]
        if elem["value"] is None :  
            elem["value"] = False
        print (name,elem["value"],bool(elem["value"]),elem["width"]*self.scale,elem["height"]*self.scale,self.scale) 
        if elem["action"] is not None :
            elem["id"] = cmds.checkBox(label=name,cc=elem["action"],
                            v=bool(elem["value"]),w=elem["width"]*self.scale,
                            h=elem["height"]*self.scale,recomputeSize=False)
        else  :
            elem["id"] = cmds.checkBox(label=name,v=bool(elem["value"]), 
                        w=elem["width"]*self.scale,
                        h=elem["height"]*self.scale,recomputeSize=False)

    def resetPMenu(self,elem):
        """ Add an entry to the given pulldown menu 
        @type  elem: dictionary
        @param elem: the pulldown dictionary
        """
        elem["value"]=[]
#        elem["variable"].val = len(elem["value"])
        cmds.popupMenu(elem["id"],e=1,deleteAllItems=1)

    def c_updatePMenu(self,id,item,action,arg=None):
        """ special maya callback for the pulldown menu 
        @type  id: int
        @param id: id of the text widget that represent the pull-down menu
        @type  elem: dictionary
        @param elem: the pulldown dictionary
        @type  action: function
        @param action: the callback associate to the pulldown menu entry
        @type  arg: args
        @param arg: argument for the callback associate to the pulldown menu entry
        """
        cmds.text(id,e=1,l=str(item))
        if action is not None :
            action(item)

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
        val = ""
        if elem["value"] is not None :
           if type(elem["value"]) is list or type(elem["value"]) is tuple:
               if len(elem["value"]):
                   val = elem["value"][0]
        else :
            val= ""
        print ("pMenu",val)
        elem["variable"] = cmds.text( label=val, bgc=[0.38,0.38,0.38],
                    w=elem["width"]*self.scale,#*2,
                    h=elem["height"]*self.scale,
                    align="left",
                    recomputeSize=False)#bgc=97,97,97?
        elem["id"]=cmds.popupMenu( button=1 )
        for item in elem["value"] :
            print ("menu",item)
            cmds.menuItem(item,c=partial(self.c_updatePMenu,
                                    elem["variable"],item,elem["action"]))

    def addItemToPMenu(self,elem,item,w=None,h=None):
        """ Add an entry to the given pulldown menu 
        @type  elem: dictionary
        @param elem: the pulldown dictionary
        @type  item: string
        @param item: the new entry
        """        
        elem["value"].append(item)
        cmds.menuItem(p=elem["id"],l=str(item),c=partial(self.c_updatePMenu,
                                          elem["variable"],item,elem["action"]))
        cmds.text(elem["variable"],e=1,l=str(item))

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
        if elem["value"] == "H":
            hr=True
        elif elem["value"] == "V":
            hr=False
        cmds.separator(w=self.w,style='single',hr=hr,ann=elem["label"])
            
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
        label["id"] = cmds.text( label=label["label"],
                    w=label["width"]*self.scale,#*2,
                    h=label["height"]*self.scale,
                    align="left",
                    recomputeSize=False)#True work ?

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
        if elem["action"] is not None :
            elem["id"] = cmds.textField(aie=True,
                        w=elem["width"]*self.scale,
                        h=elem["height"]*self.scale,
                        enterCommand=elem["action"])
        else :
            elem["id"] = cmds.textField(aie=True,
                        w=elem["width"]*self.scale,
                        h=elem["height"]*self.scale)
        if elem["value"] :
            cmds.textField(elem["id"],e=True,tx=elem["value"])

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
        elem["id"] = cmds.cmdScrollFieldExecuter(w=elem["width"]*self.scale,
                                                 h=elem["height"]*self.scale, 
                                                 sourceType="python")
        cmds.cmdScrollFieldExecuter(elem["id"],e=1,t=elem["value"])
    
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
        if elem["value"] is None :
            elem["value"] = 0
        if elem["value"] > elem["maxi"] :
            elem["maxi"] = elem["value"]+10
        if elem["value"] < elem["mini"] :
            elem["mini"] = elem["value"]-10        
        elem["label"] = "A"       
        if elem["type"] == "slidersInt":
            cmd = cmds.intSliderGrp
            if elem["action"] is not None : #label=elem["label"],
                elem["id"] = cmd(  field=True,
                                                w=elem["width"]*self.scale,
                                                h=elem["height"]*self.scale,
                                                  minValue=elem["mini"], 
                                                  maxValue=elem["maxi"], 
                                                  fieldMinValue=elem["mini"], 
                                                  fieldMaxValue=elem["maxi"],
                                                  value=elem["variable"] , 
                                                  step=elem["step"],
                                                  dc=elem["action"],
                                                  cc=elem["action"],
                                                  cal=[1,"left"],
                                                  cat=[1,"left",0])
            else :
                elem["id"] = cmds.floatSliderGrp(  field=True,
                                                w=elem["width"]*self.scale,
                                                h=elem["height"]*self.scale,            
                                                  minValue=elem["mini"], 
                                                  maxValue=elem["maxi"], 
                                                  fieldMinValue=elem["mini"], 
                                                  fieldMaxValue=elem["maxi"], 
                                                  value=elem["variable"] , 
                                                  step=elem["step"],
                                                  cal=[1,"left"])
        else :
            cmd = cmds.floatSliderGrp
            if elem["action"] is not None : #label=elem["label"],
                elem["id"] = cmd(  field=True,
                                                w=elem["width"]*self.scale,
                                                h=elem["height"]*self.scale,
                                                  minValue=elem["mini"], 
                                                  maxValue=elem["maxi"], 
                                                  fieldMinValue=elem["mini"], 
                                                  fieldMaxValue=elem["maxi"],
                                                  precision = int(elem["precision"]), 
                                                  value=elem["variable"] , 
                                                  step=elem["step"],
                                                  dc=elem["action"],
                                                  cc=elem["action"],
                                                  cal=[1,"left"],
                                                  cat=[1,"left",0])
            else :
                elem["id"] = cmds.floatSliderGrp(  field=True,
                                                w=elem["width"]*self.scale,
                                                h=elem["height"]*self.scale,            
                                                  minValue=elem["mini"], 
                                                  maxValue=elem["maxi"], 
                                                  fieldMinValue=elem["mini"], 
                                                  fieldMaxValue=elem["maxi"],
                                                  precision = int(elem["precision"]), 
                                                  value=elem["variable"] , 
                                                  step=elem["step"],
                                                  cal=[1,"left"])

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
        if elem["value"] is None :
            elem["value"] = 0
        if elem["value"] > elem["maxi"] :
            elem["maxi"] = elem["value"]+10
        if elem["value"] < elem["mini"] :
            elem["mini"] = elem["value"]-10        
        #print int(elem["mini"]),int(elem["maxi"]),int(elem["value"]),int(elem["step"])
        if elem["action"] is not None :
            elem["id"] = cmds.intField(w=elem["width"]*self.scale,
                                h=elem["height"]*self.scale,            
                                minValue=int(elem["mini"]), 
                                maxValue=int(elem["maxi"]),
                                value=int(elem["value"]) , 
                                step=int(elem["step"]),
                                dc=elem["action"],
                                cc=elem["action"],
                                ec=elem["action"],)
        else :                        
            elem["id"] = cmds.intField(w=elem["width"]*self.scale,
                                h=elem["height"]*self.scale,            
                                minValue=int(elem["mini"]), 
                                maxValue=int(elem["maxi"]),
                                value=int(elem["value"]) , 
                                step=int(elem["step"]),
                                )

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
        if elem["value"] is None :
            elem["value"] = 0
        if elem["value"] > elem["maxi"] :
            elem["maxi"] = elem["value"]+10
        if elem["value"] < elem["mini"] :
            elem["mini"] = elem["value"]-10        
        if elem["maxi"] < elem["mini"] :
            elem["maxi"] = elem["mini"]
        if elem["step"] >= float(elem["maxi"]-elem["mini"]):
            elem["step"] = float(elem["maxi"]-elem["mini"])/2.
            #print "step",elem["step"]
        #print "ok",elem["mini"],elem["maxi"],elem["step"]
        if elem["action"] is not None :
            elem["id"] = cmds.floatField(w=elem["width"]*self.scale,
                                h=elem["height"]*self.scale,            
                                minValue=float(elem["mini"]), 
                                maxValue=float(elem["maxi"]),
                                value=float(elem["value"]) , 
                                step=float(elem["step"]),
                                dc=elem["action"],
                                cc=elem["action"],
                                ec=elem["action"],
                                precision = int(elem["precision"]))#precision=2
        else :                        
            elem["id"] = cmds.floatField(w=elem["width"]*self.scale,
                                h=elem["height"]*self.scale,            
                                minValue=float(elem["mini"]), 
                                maxValue=float(elem["maxi"]),
                                value=float(elem["value"]) , 
                                step=float(elem["step"]),
                                precision = int(elem["precision"]))#precision=2

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
        cmds.picture( image=elem["value"])

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
        elem["label"] = None
        if elem["width"] == 10:
            elem["width"] = 25
        if elem["action"] is not None :
            if elem["label"]is not None:
                elem["id"] = self.colorcmd(elem["name"],w=50,
                                #h=elem["height"]*self.scale,  
                                label=elem["label"],
                                            rgb=(1, 0, 0), 
                                            #symbolButtonDisplay=False,
                                            #bl = 'color',
                                            #bc = elem["action"],
                                            cc = elem["action"])
            else:
                elem["id"] = self.colorcmd(elem["name"],#symbolButtonDisplay=False,bl = 'color',
                rgb=(1, 0, 0),w=50,cc = elem["action"])
        else :
            if elem["label"] is not None:
                elem["id"] = self.colorcmd(elem["name"],w=50,
                                #h=elem["height"]*self.scale,  
                                label=elem["label"],
                                            rgb=(1, 0, 0), bl = 'color',)
                                            #symbolButtonDisplay=False,)
                                            #bl = 'color')
            else :
                elem["id"] = self.colorcmd(elem["name"],#symbolButtonDisplay=False,bl = 'color',
                rgb=(1, 0, 0),w=50,)
        if elem["value"] is not None:
            self.setColor(elem,elem["value"][0:3])

    def drawInputQuestion(self,title="",question="",callback=None):
        """ Draw an Input Question message dialog, requiring a string answer
        @type  title: string
        @param title: the windows title       
        @type  question: string
        @param question: the question to display
        
        @rtype:   string
        @return:  the answer     
        """                  
        result = cmds.promptDialog(title=title,
                message=question,
                button=['OK', 'Cancel'],
                defaultButton='OK',
                cancelButton='Cancel',
                dismissString='Cancel')
        if result == 'OK':
            text = cmds.promptDialog(query=True, text=True)
            if callback is not None :
                callback(text)
            else :
                return text

    def drawError(self,errormsg=""):
        """ Draw a error message dialog
        @type  errormsg: string
        @param errormsg: the messag to display
        """          
        cmds.confirmDialog(title='ERROR:', message=errormsg, button=['OK'], 
                           defaultButton='OK')
 
    def drawQuestion(self,title="",question="",callback=None):
        """ Draw a Question message dialog, requiring a Yes/No answer
        @type  title: string
        @param title: the windows title       
        @type  question: string
        @param question: the question to display
        
        @rtype:   bool
        @return:  the answer     
        """        
        res = cmds.confirmDialog( title=title, message=question, 
                                button=['Yes','No'],
                                defaultButton='Yes',
                                cancelButton='No', dismissString='No')
        if res == 'Yes': 
            res = True
        else :
            res = False
        if  callback is not None   :         
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
        cmds.confirmDialog( title=title, message=message, 
                            button=['OK'], 
                            defaultButton='OK')
        
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
#        print "drawTab",bloc["name"]
#        print "nb",self.notebook
#        form = cmds.formLayout()
        oriscale= self.scale
        self.scale = 3
        TabH=self.getHeightElems(bloc)
        wh = cmds.window(self.winName, q=1,h=1)
        ww = cmds.window(self.winName, q=1,w=1)
        if TabH == 0 :
            TabH = wh
        self.scale = oriscale
        print ("tab heigh",TabH)
        if self.mainscroll is not None:
            cmds.deleteUI(self.mainscroll)
            self.mainscroll = None
        if self.notebook is None :
            self.notebook = {}
            self.notebook["id"] = cmds.tabLayout(p=self.form,h=TabH+30,w=ww)#,w=self.w*self.scale*2.5,h=TabH+30,scrollable=True)#borderStyle='in' ,
            print "ok notebook", self.notebook["id"]
            self.notebook["tab"]={}#.append(bloc["name"])
            cmds.formLayout( self.form, edit=True, attachForm=((self.notebook["id"], 'top', 0), 
                            (self.notebook["id"], 'left', 0), #(self.notebook["id"], 'bottom', 0), 
                                (self.notebook["id"], 'right', 0)) )
        else :
            th = cmds.tabLayout(self.notebook["id"],q=1,h=1)
            wh = cmds.window(self.winName, q=1,h=1)#or dockcontrol ?
            if th < TabH :
                print ("tab heigh resize ",TabH,wh)
                if TabH > wh : TabH = wh
                cmds.tabLayout(self.notebook["id"],e=1,h=TabH)
        self.notebook["tab"][bloc["name"]] =  bloc["id"]
        bloc["id"] = cmds.scrollLayout(bloc["name"])
#        bloc["id"] = cmds.shelfLayout(bloc["name"],w=self.w*self.scale)
#        bloc["id"] = cmds.frameLayout(bloc["name"],w=self.w*self.scale,
#                        labelVisible=False,borderVisible=False)
        self.inNotebook = True
        for k,blck in enumerate(bloc["elems"]):
            if type(blck) is list :
                if len(blck) == 0 :
                    continue
                cmds.rowLayout(numberOfColumns=len(blck),w=self.w*self.scale*2.5)
                for index, item in enumerate(blck):
                    self._drawElem(item,x,y)
                self.endBlock()
                #formLayout??    
            else : #dictionary: multiple line / format dict?
                if "0" in blck:
                    y = self._drawGroup(blck,x,y)
                else :
                    y = self._drawFrame(blck,x,y)
        #if bloc["name"] not in self.notebook["tab"].values():
        self.notebook["tab"][bloc["name"]] =  bloc["id"]
        self.endBlock()
#        self.endBlock()
        cmds.tabLayout( self.notebook["id"], edit=True, tabLabel=(bloc["id"], bloc["name"]) ,scrollable=True)
        self.inNotebook = False
        return y

    def getColAlign(self,N):
        kw = {}
        kw ["columnAlign"+str(N)] = "left" if N == 1 else ["left",]*N
        #kw ["adjustableColumn"+str(N)] =
        return kw
        
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
        
#        cmds.scrollLayout(bloc["name"]+"_scrol",w=self.w*self.scale)
        cmds.frameLayout( label=bloc["name"], collapsable=True,
                             cl=bloc["collapse"],borderVisible=False,
                             w=self.w*self.scale*2.5)#borderStyle='in' ,
        for k,blck in enumerate(bloc["elems"]):
#            print bloc["name"],len(blck),blck
            if len(blck) == 0 :
                continue
            kw = {}
            N = len(blck)
            if N < 6 :
                kw ["columnAlign"+str(N)] = "left" if N == 1 else ["left",]*N
            cmds.rowLayout(numberOfColumns=N,w=self.w*self.scale*2.5,**kw)
            for index, item in enumerate(blck):
                self._drawElem(item,x,y)
            self.endBlock()
        self.endBlock()
#        self.endBlock()
        return y

    def saveDialog(self,label="",callback=None):
        """ Draw a File input dialog
        @type  label: string
        @param label: the windows title       
        @type  callback: function
        @param callback: the callback function to call
        """         
        filename = cmds.fileDialog(t=label,m=1)
        callback(str(filename))

    def fileDialog(self,label="",callback=None):
        """ Draw a File input dialog
        @type  label: string
        @param label: the windows title       
        @type  callback: function
        @param callback: the callback function to call
        """         
        filename = cmds.fileDialog(t=label)
        callback(str(filename))

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
        cmds.refresh()
        
    def startBlock(self,m=1,n=1):
        #currently i will just make basic layou using the rawLayout
#        columnWidth=[]
#        for i in range(1,m):
#            columnWidth.append([i,80])#[(1, 60), (2, 80), (3, 100)]
#        cmds.rowColumnLayout(numberOfColumns=m,columnWidth=columnWidth)
#        cmds.flowLayout(wr=True)
        if not self.inNotebook and self.notebook is not None:    
            if self.afterNoteBook is None:
                c=self.afterNoteBook = cmds.flowLayout(wr=True,p=self.form)
                cmds.formLayout( self.form, edit=True, attachForm=((c, 'left', 0),(c, 'bottom', 0),
                                              (c, 'right', 0)),attachControl = ((c,'top',5,self.notebook["id"])) )
            if m==0:
                c=cmds.flowLayout(wr=True,w=self.w*self.scale,p=self.afterNoteBook)
            else :
                c=cmds.rowLayout(numberOfColumns=m,w=self.w*self.scale,p=self.afterNoteBook)            
        else : 
#            if self.mainlayout is None:
#                c=self.mainlayout = cmds.scrollLayout('scrollLayout',p=self.form)#cmds.flowLayout(wr=True,p=self.form)
#                cmds.formLayout( self.form, edit=True, attachForm=((c, 'left', 0),(c, 'bottom', 0),
#                                              (c, 'right', 0),(c, 'top', 0),) )
                
            if m==0:
                cmds.flowLayout(wr=True,w=self.w*self.scale)#,p=self.mainlayout)
            else :
                cmds.rowLayout(numberOfColumns=m,w=self.w*self.scale)#,p=self.mainlayout)

#            cmds.gridLayout(numberOfColumns=m,autoGrow=True,columnsResizable=True)
#        if m==2 :
#            cmds.rowLayout(numberOfColumns=2)
#        else :
##            cmds.flowLayout(wr=True)
#            cmds.gridLayout(numberOfColumns=m,autoGrow=True,columnsResizable=True)
##            cmds.rowLayout(numberOfColumns=m,adjustableColumn=m)
##        
    def endBlock(self):
        cmds.setParent('..')

    def startLayout(self,m=1,n=1):
#        cmds.frameLayout( cll=True,label='ePMV')
        self.form = cmds.formLayout(numberOfDivisions=100)#the main form ?
        self.mainscroll = cmds.scrollLayout('scrollLayout')#,w=self.w*self.scale)#,p=self.winName)
        cmds.formLayout( self.form, edit=True, attachForm=((self.mainscroll, 'top', 0), 
                                                           (self.mainscroll, 'left', 0),
                                             (self.mainscroll, 'bottom', 0), (self.mainscroll, 'right', 0)) )
#        cmds.columnLayout( adjustableColumn=True )
        
    def endLayout(self):
        #cmds.window( gMainWindow, edit=True, widthHeight=(900, 777) )
        if self.subdialog:
            cmds.showWindow(self.winName)
        elif self.dock  :
            allowedAreas = ['right', 'left']
            cmds.dockControl(self.winName, l=self.title,area='left', content=self.winName, 
                         allowedArea=allowedAreas )
        else :
            cmds.showWindow(self.winName)
        #toggle the visibiliy of it ..?
        #cmds.window(self.winName,e=1,vis=True)


    def setReal(self,elem,val):
        """ Set the current Float value of the Float input elem
        @type  elem: dictionary
        @param elem: the elem input dictionary       
        @type  val: Float
        @param val: the new Float value
        """    
        #to do interpret the elem["type"] to call the correct function
        if elem["type"] == 'sliders':
            cmds.floatSliderGrp(elem["id"],e=1,v=val)
        elif elem["type"] == "inputInt":
            cmds.intField(elem["id"],e=1,v=val)
        elif elem["type"] == "inputFloat":
            cmds.floatField(elem["id"],e=1,v=val)

    def getReal(self,elem):
        """ Return the current Float value of the Input elem
        @type  elem: dictionary
        @param elem: the elem input dictionary       
        
        @rtype:   Float
        @return:  the current Float value input for this specific elem
        """                                
        #to do interpret the elem["type"] to call the correct function
        #have to look at the type too

        if elem["type"] == 'sliders':
            return cmds.floatSliderGrp(elem["id"],q=1,v=1)
        elif elem["type"] == "inputInt":
            return float(cmds.intField(elem["id"],q=1,v=1))
        elif elem["type"] == "inputFloat":
            return float(cmds.floatField(elem["id"],q=1,v=1))
            
    def getBool(self,elem):
        """ Return the current Bool value of the Input elem
        @type  elem: dictionary
        @param elem: the elem input dictionary       
        
        @rtype:   Bool
        @return:  the current Bool value input for this specific elem
        """ 
        if elem["type"] == 'checkbox':
            if cmds.checkBox(elem["id"],q=1,ex=1):
                return cmds.checkBox(elem["id"],q=1,v=1)#width and height ? 
            else :
                return elem["value"]
                
    def setBool(self,elem,val):
        """ Set the current Bool value of the Bool input elem
        @type  elem: dictionary
        @param elem: the elem input dictionary       
        @type  val: Bool
        @param val: the new Bool value
        """                      
        if cmds.checkBox(elem["id"],q=1,ex=1):
            cmds.checkBox(elem["id"],e=1,v=val)

    def getString(self,elem):
        """ Return the current string value of the String Input elem
        @type  elem: dictionary
        @param elem: the elem input dictionary       
        
        @rtype:   string
        @return:  the current string input value for this specific elem
        """  
        if elem["type"] =="label":
            if cmds.text(elem["id"],q=1,ex=1):
                return str(cmds.text(elem["id"],q=1,label=1))
            else :
                return elem["value"]
        else :
            if cmds.textField(elem["id"],q=1,ex=1):            
                return str(cmds.textField(elem["id"],q=1,tx=1))
            else :
                return elem["value"]
            

    def setString(self,elem,val):
        """ Set the current String value of the string input elem
        @type  elem: dictionary
        @param elem: the elem input dictionary       
        @type  val: string
        @param val: the new string value    
        """         
        if elem["type"] =="label":
            cmds.text(elem["id"],e=1,label=val)
        else :
            cmds.textField(elem["id"],e=1,tx=val)

    def getStringArea(self,elem):
        """ Return the current string area value of the String area Input elem
        @type  elem: dictionary
        @param elem: the elem input dictionary       
        
        @rtype:   string
        @return:  the current string area input value for this specific elem
        """                
        return cmds.cmdScrollFieldExecuter(elem["id"],q=1,t=1)

    def setStringArea(self,elem,val):
        """ Set the current String area value of the string input elem
        @type  elem: dictionary
        @param elem: the elem input dictionary       
        @type  val: string
        @param val: the new string value (multiline)   
        """                        
        cmds.cmdScrollFieldExecuter(elem["id"],e=1,tx=val)

    def getLong(self,elem):
        """ Return the current Int value of the Input elem
        @type  elem: dictionary
        @param elem: the elem input dictionary       
        
        @rtype:   Int
        @return:  the current Int value input for this specific elem
        """
        print elem["type"]
        if elem["type"] == "inputInt":
            return cmds.intField(elem["id"],q=1,v=1)
        elif elem["type"] == "sliders":
            return int(cmds.floatSliderGrp(elem["id"],q=1,v=1))
        elif elem["type"] == "inputFloat":
            return int(cmds.floatField(elem["id"],q=1,v=1))
        else:
            #specific command for menulike
            str = cmds.text(elem["variable"],q=1,l=1)
            if str in elem["value"] :
                return elem["value"].index(str) #maya combo menu is a txt + pulldown menu
            else :
                return 0

    def setLong(self,elem,val):
        """ Set the current Int value of the Int input elem
        @type  elem: dictionary
        @param elem: the elem input dictionary       
        @type  val: Int
        @param val: the new Int value
        """                                
        if elem["type"] == "inputInt":
            cmds.intField(elem["id"],e=1,v=val)
        elif elem["type"] == "inputFloat":
            cmds.floatField(elem["id"],e=1,v=val)
        else:
            if type(val) is int  :
                val = elem["value"][val]
            cmds.text(elem["variable"],e=1,l=val)

    def getColor(self,elem):
        """ Return the current Color value of the Input elem
        @type  elem: dictionary
        @param elem: the elem input dictionary       
        
        @rtype:   Color
        @return:  the current Color array RGB value input for this specific elem
        """                        
        return self.colorcmd(elem["id"],q=1,rgb=1)

    def setColor(self,elem,val):
        """ Set the current Color rgb arrray value of the Color input elem
        @type  elem: dictionary
        @param elem: the elem input dictionary       
        @type  val: Color
        @param val: the new Color value
        """                        
        self.colorcmd(elem["id"],e=1,rgb=val[0:3])

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
        cmds.floatSliderGrp(elem["id"],e=1,minValue=float(mini), maxValue=float(maxi), 
                                               fieldMinValue=float(mini), 
                                               fieldMaxValue=float(maxi),
                                               value=float(default),
                                               step=float(step))
                                               

    def setAction(self,elem,callback):
        """
        Set the value of the given widget
        
        @type  elem: dictionary widget
        @param elem: the widget    
        @type  val: X
        @param val: the new value for the widget
        """        
        elem["action"] = callback
        #if elem["type"] == "pullMenu":
            #if type(val) is str or type(val) is unicode:
                #val = list(elem["value"]).index(str(val))#or values?
            #elif type(val) is list :
                #val = 0
            #return self.setLong(elem,val)
        #elif elem["type"] == "inputStr" or elem["type"] == "label":
            #return self.setString(elem,str(val))
##        elif elem["type"] == "inputStrArea":
##            self.drawStringArea(elem,x,y,w=w,h=h)
        if elem["type"] == "checkbox":
            cmds.checkBox(elem["id"],e=1,cc=callback)
        #elif elem["type"] == "sliders":
            #return self.setReal(elem,val)        
        #elif elem["type"] == "slidersInt":
            #return self.setLong(elem,val)        
        #elif elem["type"] == "inputInt":
            #return self.setLong(elem,val)       
        #elif elem["type"] == "inputFloat":
            #return self.setReal(elem,val)       
##        elif elem["type"] == "image":
##            return self.getBool(elem)             
        #elif elem["type"] == "color":
            #return self.setColor(elem,val)        
                                               
    @classmethod                                          
    def _restore(self,rkey,dkey=None):
        """
        Function used to restore the windows data, usefull for plugin
        @type  rkey: string
        @param rkey: the key to access the data in the registry/storage       
        @type  dkey: string
        @param dkey: wiether we want a particular data from the stored dic
        """        
        if hasattr(maya,rkey):
            obj = maya.__dict__[rkey]
            if dkey is not None:
                if maya.__dict__[rkey].has_key(dkey) :
                    return  maya.__dict__[rkey][dkey]       
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
        maya.__dict__[rkey]= dict

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
        res = cmds.window(dial.winName, exists=True)
        print ("will draw ",dial.winName, res," created ?",dial.created) 
        if res and dial.created:
            if dial.subdialog:
                cmds.window(dial.winName,e=1,vis=True)
            elif dial.dock  :
                cmds.dockControl(dial.winName, e=1,vis=True)
            else :
                cmds.window(dial.winName,e=1,vis=True)
        else :    
            dial.CreateLayout()
            dial.created = True
            print ("dialog created",dial.winName)
#            self.drawSubDialog(dial,id,callback=callback,asynchro=asynchro)
            
    def close(self,*args):
        """ Close the windows"""
#        res = cmds.window(self.winName, q=1, exists=1)
#        print res
#        if bool(res):
#            print winName, " exist"
#            cmds.deleteUI(self.winName, window=True)
#            cmds.window(self.winName,e=1,vis=False)#this delete the windows...
        if self.subdialog:
            cmds.window(self.winName,e=1,vis=False)
        elif self.dock  :
            cmds.dockControl(self.winName, e=1,vis=False)
        else :
            cmds.window(self.winName,e=1,vis=False)

    def display(self):
        """ Create and Open the current gui windows """
        res = cmds.window(self.winName, exists=True)
        print (self.winName, res) 
        if res and self.created:
            if self.subdialog:
                cmds.window(self.winName,e=1,vis=True)
            elif self.dock  :
                cmds.dockControl(self.winName, e=1,vis=True)
            else :
                cmds.window(self.winName,e=1,vis=True)
        else :    
            self.CreateLayout()
            self.created = True

    def getDirectory(self):
        """return software directory for script and preferences"""
        self.prefdir=cmds.internalVar(userPrefDir=True)
        os.chdir(self.prefdir)
        os.chdir('../')
        self.softdir = os.path.abspath(os.curdir)+os.sep+"plug-ins"
        print "soft ",self.softdir 
        plugdirs = os.environ['MAYA_PLUG_IN_PATH'].split(":")     
        if self.softdir not in plugdirs :
            if plugdirs[0].find("mMaya") != -1 :
                self.softdir = plugdirs[1]
            else :
                if type(plugdirs) is list or type(plugdirs) is tuple:
                    self.softdir = plugdirs[0]
                else :
                    self.softdir = plugdirs
        print plugdirs

            
class mayaUIDialog(mayaUI,uiAdaptor):
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

