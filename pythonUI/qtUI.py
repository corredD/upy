
"""
    Copyright (C) <2010>  Autin L. TSRI
    
    This file git_upy/pythonUI/qtUI.py is part of upy.

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
Created on Tue Apr 26 22:58:30 2011

@author: -
"""

import os

try :
    from PyQt4 import QtGui,QtCore
    QtCore.Signal = QtCore.pyqtSignal
    QtCore.Slot = QtCore.pyqtSlot    
except :
    try :
        from PySide import QtGui,QtCore
    except :
        print ("noQt support ")
print ("ok Qt ")        
#from PyQt4.Qwt5 import QwtSlider
#QtGui.QMainWindow
#QtGui.QWidget
from upy.uiAdaptor import uiAdaptor
from functools import partial
#TODO 
# -add validator
#

mainRoot = None
class SlidersGroup(QtGui.QWidget):

    valueChanged = QtCore.pyqtSignal(int)

    def __init__(self, orientation, title, stype="int", parent=None,min=0,max=10,step=1):
        super(SlidersGroup, self).__init__( parent)

        self.stype = stype
        self.min=min
        self.max=max
        self.step=step
        
        self.slider = QtGui.QSlider(orientation)
        self.slider.setFocusPolicy(QtCore.Qt.StrongFocus)
        #self.slider.setTickPosition(QtGui.QSlider.TicksBothSides)
        #self.slider.setTickInterval(10)
        #self.slider.setSingleStep(1)

        if self.stype == "float":
            self.valueSpinBox = QtGui.QDoubleSpinBox()
        else :
            self.valueSpinBox = QtGui.QSpinBox()
        #self.valueSpinBox.setRange(-100, 100)
        #self.valueSpinBox.setSingleStep(1)
        #self.valueSpinBox.setValue = self.spinerSetValue
        #self.horizontalSliders.valueChanged.connect(self.verticalSliders.setValue)
        #self.verticalSliders.valueChanged.connect(self.valueSpinBox.setValue)

        #self.valueSpinBox.valueChanged.connect(self.slider.setValue)

        #self.scrollBar = QtGui.QScrollBar(orientation)
        #self.scrollBar.setFocusPolicy(QtCore.Qt.StrongFocus)

        #self.dial = QtGui.QDial()
        #self.dial.setFocusPolicy(QtCore.Qt.StrongFocus)

        #self.slider.valueChanged.connect(self.valueSpinBox.setValue)
        self.slider.valueChanged.connect(self.spinerSetValue)
        self.valueSpinBox.valueChanged.connect(self.sliderSetValue)
        #self.valueSpinBox.editingFinished.connect(self.sliderSetValue)
        #self.connect(self.valueSpinBox, QtCore.SIGNAL('valueChanged'), self.sliderSetValue)
        
        #self.scrollBar.valueChanged.connect(self.dial.setValue)
        #self.dial.valueChanged.connect(self.slider.setValue)
        #self.dial.valueChanged.connect(self.valueChanged)

        slidersLayout = QtGui.QHBoxLayout()
        slidersLayout.addWidget(self.valueSpinBox)
        slidersLayout.addWidget(self.slider)
        #slidersLayout.addWidget(self.scrollBar)
        #slidersLayout.addWidget(self.dial)
        self.setLayout(slidersLayout)    
        self.setRange(self.min,self.max)
        self.setSingleStep(self.step)

    def sliderSetValue(self,*args):
        #print "sliderSetValue",self,args
        value = self.valueSpinBox.value()
        if self.stype == "float":
            value = int(value*(1./self.step))
        self.slider.setValue(value)

    def spinerSetValue(self,value):
        #print "spinerSetValue",value
        if self.stype == "float":
            value = float(value*float(self.step))
        self.valueSpinBox.setValue(value)
        if self.stype == "float":
            signal = 'valueChanged(double)'
        elif self.stype == "int":
            signal = 'valueChanged(int)'       
        self.emit(QtCore.SIGNAL(signal) , value)
        
    def setValue(self, value):
        self.sliderSetValue(value)
        self.valueSpinBox.setValue(value)
        if self.stype == "float":
            signal = 'valueChanged(double)'
        elif self.stype == "int":
            signal = 'valueChanged(int)'       
        self.emit(QtCore.SIGNAL(signal) , value)
        
    def convertValue(self,value):
        #float is range 0-100 with step = 1 an
        elem["id"].setRange(elem["mini"]*(1/elem["step"]), elem["maxi"]*(1/elem["step"]))#,elem["step"])
        elem["id"].setSingleStep(elem["id"].maximum()/100.0)#elem["step"]
        if stype == "float":
            value = value

    def setRange(self, valuemin,valuemax):
        if self.stype == "float":
            valuemin = valuemin * (1.0/self.step)
            valuemax = valuemax * (1.0/self.step)
        self.slider.setRange(valuemin,valuemax)
        self.valueSpinBox.setRange(valuemin,valuemax)
        #self.scrollBar.setMinimum(value)
        #self.dial.setMinimum(value)
        
    def setMinimum(self, value):    
        self.slider.setMinimum(value)
        self.valueSpinBox.setMinimum(value)
        #self.scrollBar.setMinimum(value)
        #self.dial.setMinimum(value)    

    def setMaximum(self, value):    
        self.slider.setMaximum(value)
        self.valueSpinBox.setMaximum(value)
        #self.scrollBar.setMaximum(value)
        #self.dial.setMaximum(value)    
        
    def invertAppearance(self, invert):
        self.slider.setInvertedAppearance(invert)
        #self.scrollBar.setInvertedAppearance(invert)
        #self.dial.setInvertedAppearance(invert)    

    def setSingleStep(self,step):
        self.valueSpinBox.setSingleStep(step)
        if self.stype == "float":
            step = step * (1.0/self.step)
        self.slider.setSingleStep(step)
        
    def value(self):
        v = self.slider.value()
        if self.stype == "float":
            return float(v)*self.step
        else :
            return int(v)
        
    def invertKeyBindings(self, invert):
        self.slider.setInvertedControls(invert)
        #self.scrollBar.setInvertedControls(invert)
        #self.dial.setInvertedControls(invert)

    #def valueChanged(self,value):
    #    print "valueChanged",value
    #    print self.slider.value()
    #   print self.valueSpinBox.value()
    
class ColorButton(QtGui.QPushButton):

        StyleSheet = 'background-color: %s;'
        colorChanged = QtCore.Signal(QtGui.QColor)

        def __init__(self, parent=None, color=None, toolTip='',callback=None):
                QtGui.QPushButton.__init__(self, parent)
                self._color = QtGui.QColor() if color is None else color
                #NOTE: tool tips derrive style sheets from our button, so we can not really use it here
                self._toolTip = toolTip
                self.clicked.connect(self.onButtonClicked)
                self._cb = callback

        def getColor(self):
            return self._color

        def setColor(self, color):
            self._color = color
            if color.isValid():
                self.setStyleSheet(self.StyleSheet % color.name() )
            else:
                self.setStyleSheet('')
            self.colorChanged.emit(color)

        def resetColor(self):
            self.setColor(QtGui.QColor() )

        def toolTip(self):
            return self._toolTip

        def setToolTip(self, text):
            self._toolTip = text

        def onButtonClicked(self):
            #NOTE: the dialog derrives its style sheet from the button, so we have to
            # use our parent as parent for the dialog
            color = QtGui.QColorDialog.getColor(self.getColor(), self.parent(), self.toolTip() )
            if color.isValid():
                self.setColor(color)
                if self._cb is not None :
                    self._cb(color)
                        


#UI general interface
class qtUI(QtGui.QDialog,QtGui.QMainWindow,QtGui.QWidget):
    """
    The qt uiAdaptor abstract class
    ====================================
        This Adaptor give access to the basic maya Draw function need for 
        create and display a gui.
    """
    
    host = "qt" #or sonething else like dejavu or ?
    scale = 2
    maxStrLenght=100
    left, top, right, bottom =(10,10,10,1)
    bid=1
    title=""
    winName=""
    subdialog = False
    dock = True
    w=400
    h=100
    notebook = None
    x=20
    y=0
    ystep = 30
    collapsible_frame = None
        
        
    def keyPressEvent(self, event):
            if event.key() == QtCore.Qt.Key_Escape:
                self.close()

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
        self.winName= title.replace(" ","_")+"_gui"
#        print winName
#        print cmds.window(winName, q=1, exists=1)
        self.resize(self.w*self.scale,self.h*self.scale)
        self.setWindowTitle(title)
        self.mainlayout = QtGui.QVBoxLayout(self)
        self.setLayout(self.mainlayout)
        #self.winName = winName
#        print self.winName, " created"

    def ctxMenu(self,menu_entry,menuDictionary):
        menu = QtGui.QMenu()  
        for elem in menuDictionary:
            if elem["sub"] is not None:
                submenu = menu.addMenu(elem["name"])
                for sub in elem['sub'].keys():
                    if elem['sub'][sub]["action"] is not None :
                        sube = QtGui.QAction(elem['sub'][sub]["name"],self)
                        self.connect(sube, QtCore.SIGNAL('triggered()'),partial(elem['sub'][sub]["action"],sub))
                        submenu.addAction(sube)
                    else :
                        submenu.addAction(elem['sub'][sub]["name"])
            else:
                if elem["action"] is not None :
                    ac=QtGui.QAction(elem["name"],self)#uItem( label=elem["name"],c=elem["action"])
                    self.connect(ac, QtCore.SIGNAL('triggered()'),elem["action"])
                    menu.addAction(ac)
                else :
                    menu.addAction(elem["name"])        
        menu.exec_(QtGui.QCursor.pos())
              
    def createMenu(self,menuDic,menuOrder=None):
        """ Define and draw the window/widget top file menu
        @type  menuDic: dictionary
        @param menuDic: the menu elements, ie entry, callback and submenu
        @type  menuOrder: array
        @param menuOrder: the menu keys oredered
        """        
        #always use toolbar except if specify
        #if self.subdialog :
        #    return 
#        self.exit = QtGui.QAction(QtGui.QIcon('icons/exit.png'), 'Exit', self)
#        self.exit.setShortcut('Ctrl+Q')
#        self.connect(self.exit, QtCore.SIGNAL('triggered()'), QtCore.SLOT('close()'))
        self.toolBar = QtGui.QToolBar(self)
        self.toolBar.setObjectName(self.winName+"toolBar")
        self.mainlayout.addWidget(self.toolBar)
        #self.addToolBar(self.toolBar)
        if menuOrder : 
            lookat = menuOrder
        else :
            lookat = menuDic.keys()
        for mitem in lookat:
            action = QtGui.QPushButton(mitem, self)
            self.toolBar.addWidget(action)
            action.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
            self.connect(action,QtCore.SIGNAL('clicked()'),partial(self.ctxMenu,mitem,menuDic[mitem]))

    def addVariable(self,type,value):
        """ Create a container for storing a widget states """
        if type == "col" :
            print (value)
            col = QtGui.QColor()
            col.setRgbF(value[0],value[1],value[2])
            return col
        else :
            return value

    def getFlagAlignement(self,alignement):
        pass

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
        #if elem["alignement"] is None :
        #    elem["alignement"] = c4d.BFH_CENTER | c4d.BFV_MASK
        name = elem["name"]
        if elem["label"] != None:
            name = elem["label"]
        elem["id"] = QtGui.QPushButton(name, self)
        #elem["id"].setGeometry(x, y,elem["width"]*self.scale,elem["height"]*self.scale)
        if elem["action"] is not None :
            self.connect(elem["id"], QtCore.SIGNAL('clicked()'),partial(elem["action"],elem))
        print (x,y, elem["name"])


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
        name = elem["name"]
        if elem["label"] != None:
            name = elem["label"]
        elem["id"] = QtGui.QCheckBox(name, self)#or name
        elem["id"].setFocusPolicy(QtCore.Qt.NoFocus)
        elem["id"].setGeometry(x, y,elem["width"]*self.scale,elem["height"]*self.scale)
        #elem["id"].toggle() #default uncheck
        if elem["action"] is not None :
            self.connect(elem["id"], QtCore.SIGNAL('stateChanged(int)'), 
                         partial(elem["action"],elem))
        val = elem["variable"]
#        state = 2 if val else 0
        state = QtCore.Qt.Checked if val else QtCore.Qt.Unchecked      
        elem["id"].setCheckState(state)
        print (x,y, elem["name"])

    def resetPMenu(self,elem):
        """ Add an entry to the given pulldown menu 
        @type  elem: dictionary
        @param elem: the pulldown dictionary
        """
        elem["value"]=[]
        elem["id"].clear()

    def c_updatePMenu(self,*args):
        """ callback for the pulldown menu 
        @type  id: int
        @param id: id of the text widget that represent the pull-down menu
        @type  elem: dictionary
        @param elem: the pulldown dictionary
        @type  action: function
        @param action: the callback associate to the pulldown menu entry
        @type  arg: args
        @param arg: argument for the callback associate to the pulldown menu entry
        """
        print (args)
        elem = args[0]
        text = args[1] 
        if elem["action"] is not None :
            elem["action"](text)

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
        elem["id"] = QtGui.QComboBox(self)
        [elem["id"].addItem(e) for e in elem["value"]]
        elem["id"].setGeometry(x, y,elem["width"]*self.scale,elem["height"]*self.scale)
        self.connect(elem["id"], QtCore.SIGNAL('activated(QString)'), 
                                             partial(self.c_updatePMenu,elem))

    def addItemToPMenu(self,elem,item,w=None,h=None):
        """ Add an entry to the given pulldown menu 
        @type  elem: dictionary
        @param elem: the pulldown dictionary
        @type  item: string
        @param item: the new entry
        """        
        elem["value"].append(item)
        elem["id"].addItem(item)
        
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
        label["id"]= QtGui.QLabel(self)
        label["id"].setGeometry(x, y,label["width"]*self.scale,label["height"]*self.scale)
        label["id"].setText(label["label"])
        label["id"].adjustSize()

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
        elem["id"] = QtGui.QLineEdit(self)
        elem["id"].setGeometry(x, y,elem["width"]*self.scale,elem["height"]*self.scale)
        elem["id"].setMaxLength(100)
        if elem["action"] is not None :
            self.connect(elem["id"], QtCore.SIGNAL('textChanged(QString)'), 
                         partial(elem["action"],elem))
        if elem["value"] :
            elem["id"].setText(elem["value"])

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
        """       #textEdit = QtGui.QTextEdit()   
        elem["id"] = QtGui.QPlainTextEdit(self) 
        elem["id"].setGeometry(x, y,elem["width"]*self.scale,elem["height"]*self.scale)
        elem["id"].appendPlainText(elem["value"])

           
    def drawSliders1(self,elem,x,y,w=None,h=None):
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
        if elem["type"] == "sliders":
            elem["id"] = QtGui.QSlider(QtCore.Qt.Horizontal,self)#QwtSlider(self,QtCore.Qt.Horizontal)
            elem["id"].setRange(elem["mini"]*(1/elem["step"]), elem["maxi"]*(1/elem["step"]))#,elem["step"])
            elem["id"].setSingleStep(elem["id"].maximum()/100.0)#elem["step"]
        elif elem["type"] == "slidersInt":
            elem["id"] = QtGui.QSlider(QtCore.Qt.Horizontal,self)
            elem["id"].setRange(elem["mini"], elem["maxi"])
            elem["id"].setSingleStep(elem["step"])
        elem["id"].setGeometry(x+(elem["width"]*self.scale/2.0), y,(elem["width"]*self.scale/2.0),elem["height"]*self.scale)
        elem["id"].spin = QtGui.QSpinBox(self)
        elem["id"].spin.setGeometry(x, y,(elem["width"]*self.scale/2.0),elem["height"]*self.scale)
        elem["id"].spin.setRange(elem["mini"], elem["maxi"])
        elem["id"].spin.setSingleStep(elem["step"])
        elem["id"].spin.setValue(elem["value"])     
        elem["id"].spin.valueChanged.connect(elem["id"].setValue)
        elem["id"].valueChanged.connect(elem["id"].spin.setValue)
        if elem["action"] is not None :
            signal = 'valueChanged(int)'
            if elem["type"] == "slidersInt":
                signal = 'valueChanged(int)'
            elif elem["type"] == "sliders":
                signal = 'valueChanged(double)'
            signal = 'valueChanged(int)'
            self.connect(elem["id"], QtCore.SIGNAL(signal), 
                         partial(elem["action"],elem))

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
        if elem["variable"] is None :
            elem["variable"] =0.0
        if elem["value"] is None :
            elem["value"] = 0
        if elem["value"] > elem["maxi"] :
            elem["maxi"] = elem["value"]+10
        if elem["value"] < elem["mini"] :
            elem["mini"] = elem["value"]-10        
        elem["label"] = "A" 
        if elem["type"] == "sliders":
            elem["id"] = SlidersGroup(QtCore.Qt.Horizontal, "Horizontal",stype="float",
                                                min=elem["mini"],max=elem["maxi"],step=elem["step"])
        elif elem["type"] == "slidersInt":
            elem["id"] = SlidersGroup(QtCore.Qt.Horizontal, "Horizontal",stype="int",
                                                min=elem["mini"],max=elem["maxi"],step=elem["step"])
        elem["id"].setGeometry(x+(elem["width"]*self.scale/2.0), y,(elem["width"]*self.scale/2.0),elem["height"]*self.scale)
        elem["id"].setValue(elem["variable"])
        if elem["action"] is not None :
            signal = 'valueChanged(int)'
            if elem["type"] == "slidersInt":
                signal = 'valueChanged(int)'
            elif elem["type"] == "sliders":
                signal = 'valueChanged(double)'
            self.connect(elem["id"], QtCore.SIGNAL(signal), 
                         partial(elem["action"],elem))

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
        elem["id"] =QtGui.QSpinBox(self)
        elem["id"].setGeometry(x, y,elem["width"]*self.scale,elem["height"]*self.scale)
        elem["id"].setRange(elem["mini"], elem["maxi"])
        elem["id"].setSingleStep(elem["step"])
        elem["id"].setValue(elem["value"])     
        if elem["action"] is not None :
            self.connect(elem["id"], QtCore.SIGNAL('valueChanged(int)'), 
                         partial(elem["action"],elem))

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
        elem["id"] =QtGui.QDoubleSpinBox(self)
        elem["id"].setGeometry(x, y,elem["width"]*self.scale,elem["height"]*self.scale)
        elem["id"].setRange(elem["mini"], elem["maxi"])
        elem["id"].setSingleStep(elem["step"])
        elem["id"].setValue(elem["value"])
        elem["id"].setDecimals(elem["precision"])     
        if elem["action"] is not None :
            self.connect(elem["id"], QtCore.SIGNAL('valueChanged(double)'), 
                         partial(elem["action"],elem))

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
        elem["variable"] = QtGui.QPixmap(elem["value"])
        elem["id"] = QtGui.QLabel(self)
        elem["id"].setPixmap(elem["variable"])
        #elem["id"].setGeometry(x, y,elem["width"]*self.scale,elem["height"]*self.scale)
        
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
        #should be a color background widget clicakble
        #using a variable of type : self.color = QtGui.QColor(0, 0, 0)
        elem["label"] = None
        if elem["width"] == 10:
            elem["width"] = 25
        #or a colored push button
        elem["id"] = ColorButton(self, color=elem["variable"], toolTip=elem["tooltip"],
                                                  callback=elem["action"])
        elem["id"].setGeometry(x, y,elem["width"]*self.scale,elem["height"]*self.scale)
        if elem["value"] is not None:
            self.setColor(elem,elem["value"])

    def drawInputQuestion(self,title="",question="",callback=None):
        """ Draw an Input Question message dialog, requiring a string answer
        @type  title: string
        @param title: the windows title       
        @type  question: string
        @param question: the question to display
        
        @rtype:   string
        @return:  the answer     
        """        
        text, ok = QtGui.QInputDialog.getText(self, title, 
            question)
        if ok:
            if callback is not None :
                callback(text)
            else :
                return text

    def drawError(self,errormsg=""):
        """ Draw a error message dialog
        @type  errormsg: string
        @param errormsg: the messag to display
        """  
        res = QtGui.QMessageBox.information(self, 'ERROR:', errormsg,QtGui.QMessageBox.Ok)
 
    def drawQuestion(self,title="",question=""):
        """ Draw a Question message dialog, requiring a Yes/No answer
        @type  title: string
        @param title: the windows title       
        @type  question: string
        @param question: the question to display
        
        @rtype:   bool
        @return:  the answer     
        """   
        res = QtGui.QMessageBox.question(self, title,
            question, QtGui.QMessageBox.Yes | 
            QtGui.QMessageBox.No, QtGui.QMessageBox.No)
     
        if res == QtGui.QMessageBox.Yes: 
            return True
        else :
            return False

    def drawMessage(self,title="",message=""):
        """ Draw a message dialog
        @type  title: string
        @param title: the windows title       
        @type  message: string
        @param message: the message to display   
        """                    
        res = QtGui.QMessageBox.information(self, title, message,QtGui.QMessageBox.Ok)

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
        #need a QtGui.QMdiArea(), but is it working for subwindows         
        listes_x=[]
        if self.notebook is None :
            mdiarea = QtGui.QTabWidget(self)
            self.mainlayout.addWidget(mdiarea)
            #tab_bar = QtGui.QTabBar(mdiarea)
            #self.setCentralWidget( mdiarea )
            self.notebook = {}
            self.notebook["id"] = mdiarea
#            print "ok", self.notebook["id"]
            self.notebook["tab"]={}#.append(bloc["name"])
            #self.mainlayout.addWidget(mdiarea)
        self.notebook["tab"][bloc["name"]] =  bloc

        #bloc["id"] = QtGui.QSplitter(self,)
        #frame = QtGui.QFrame(bloc["id"])
        #bloc["id"].setWindowTitle(bloc["name"])
        bloc["id"] = QtGui.QWidget()
        bloc["layout"] = QtGui.QVBoxLayout(bloc["id"])
        for k,blck in enumerate(bloc["elems"]):
            if type(blck) is list :
                #add the widget to the layout
                #one blk is a line
                layout = QtGui.QHBoxLayout()
                bloc["layout"].addLayout(layout)
                y = y +self.ystep
                for index, item in enumerate(blck):
                    self._drawElem(item,x,y)
                    x += int(item["width"]*self.scale) + 15
                    layout.addWidget(item["id"])
                    if item["type"] != "inputStrArea":
                        item["id"].setFixedHeight(item["height"]*self.scale)
                        item["id"].setFixedWidth(item["width"]*self.scale)
                self.endBlock()
            else : #dictionary: multiple line / format dict?
                if "0" in blck:
                    y = self._drawGroup(blck,x,y)
                else :
                    y = self._drawFrame(blck,x,y)
           
        self.notebook["id"].addTab(bloc["id"],bloc["name"])
        #if bloc["name"] not in self.notebook["tab"].values():
        self.notebook["tab"][bloc["name"]] =  bloc
        self.endBlock()
        #bloc["id"].setSizes(listes_x)
        return y

    def drawTabW(self,bloc,x,y):
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
        #need a QtGui.QMdiArea(), but is it working for subwindows

        
        listes_x=[]
        if self.notebook is None :
            mdiarea = QtGui.QMdiArea(self)
            mdiarea.setTabPosition( QtGui.QTabWidget.North )
            mdiarea.setTabShape( QtGui.QTabWidget.Rounded )
            mdiarea.setViewMode( QtGui.QMdiArea.TabbedView )
            mdiarea.show()
            #self.setCentralWidget( mdiarea )
            self.notebook = {}
            self.notebook["id"] = mdiarea
#            print "ok", self.notebook["id"]
            self.notebook["tab"]={}#.append(bloc["name"])
        self.notebook["tab"][bloc["name"]] =  bloc["id"]

        bloc["id"] = QtGui.QSplitter(self,)
        #frame = QtGui.QFrame(bloc["id"])
        bloc["id"].setWindowTitle(bloc["name"])

        for k,blck in enumerate(bloc["elems"]):
            #add the widget to the layout
            y = y +self.ystep
            for index, item in enumerate(blck):
                self._drawElem(item,x,y)
                x += int(item["width"]*self.scale) + 15
                bloc["id"].addWidget(item["id"])
                if item["type"] != "inputStrArea":
                    item["id"].setFixedHeight(item["height"]*self.scale)
                    item["id"].setFixedWidth(item["width"]*self.scale)
            self.endBlock()
        self.notebook["id"].addSubWindow(bloc["id"])
        #if bloc["name"] not in self.notebook["tab"].values():
        self.notebook["tab"][bloc["name"]] =  bloc["id"]
        self.endBlock()
        #bloc["id"].setSizes(listes_x)
        return y

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
        listes_x=[]
        
        if self.collapsible_frame is None :
            from upy.pythonUI.qtCollapsible import AccordianWidget 
            mdiarea = AccordianWidget(self)#QtGui.QTreeWidget(self)
            self.mainlayout.addWidget(mdiarea)
#            mdiarea.setWidgetResizable(True)
#            mdiarea.setAlignment(QtCore.Qt.AlignmentFlag.AlignJustify)
            #mdiarea.setResizeMode(QtGui.QListView.Adjust)            
            #self.setCentralWidget( mdiarea )
            self.collapsible_frame = {}
            self.collapsible_frame["id"] = mdiarea
#            print "ok", self.notebook["id"]
            self.collapsible_frame["tab"]={}#.append(bloc["name"])
#            self.notebook["id"].show()
        bloc["id"] = QtGui.QGroupBox()
        bloc["id"].setFlat(True)
        bloc["layout"] = QtGui.QVBoxLayout(bloc["id"])
#        formLayout = QtGui.QFormLayout()
#        formLayout.setFieldGrowthPolicy(QtGui.QFormLayout.AllNonFixedFieldsGrow)
        self.collapsible_frame["tab"][bloc["name"]] =  bloc["id"]
        #bloc["layout"] = QtGui.QVBoxLayout(bloc["id"])
        oriy = y
        x=self.x
    
        for k,blck in enumerate(bloc["elems"]):
            #add the widget to the layout
            layout = QtGui.QHBoxLayout()
            bloc["layout"].addLayout(layout)
            y = y +self.ystep
            for index, item in enumerate(blck):
                self._drawElem(item,x,y)
                x += int(item["width"]*self.scale) + 15
                layout.addWidget(item["id"])
                if item["type"] == "inputStrArea":
#                    item["id"].setFixedHeight(item["height"]*self.scale)
#                    item["id"].setFixedWidth(item["width"]*self.scale)
                    y = item["height"]*self.scale
                    oriy = 0
            #self.endBlock()
        self.collapsible_frame["id"].addItem(bloc["name"], bloc["id"])
        return y
        
    def drawFrameList(self,bloc,x,y):
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
        listes_x=[]
        if self.notebook is None :
            mdiarea = QtGui.QTreeWidget(self)
            #mdiarea.setResizeMode(QtGui.QListView.Adjust)            
            #self.setCentralWidget( mdiarea )
            self.notebook = {}
            self.notebook["id"] = mdiarea
#            print "ok", self.notebook["id"]
            self.notebook["tab"]={}#.append(bloc["name"])
        self.notebook["tab"][bloc["name"]] =  bloc["id"]
        bloc["id"] = QtGui.QTreeWidgetItem(self.notebook["id"])
        bloc["id"].setText(0,bloc["name"])   #Sets the "header" for your [+] box
        list1 = QtGui.QListWidget(self)                #This will contain your icon list
        list1.setMovement(QtGui.QListView.Static)  #otherwise the icons are draggable
        #list1.setResizeMode(QtGui.QListView.Adjust)  
        #list1.setViewMode(QtGui.QListView.IconMode) #Layout left-to-right, not top-to-bottom
        
        #list1.doItemsLayout()
        #list1.setModelColumn(2)
        
        #list1.setLayoutMode(QtGui.QListView.Batched)
        #list1.setSizeHint(QtCore.QSize(50,50))
        #list1.setBatchSize(5)
        #list1.setGridSize(QtCore.QSize(50,50))
        #list1.setSpacing(20)
        #list1.setUniformItemSizes(True)
#        blc = QtGui.QSplitter(self,)
#        #frame = QtGui.QFrame(bloc["id"])
#        blc.setWindowTitle(bloc["name"])
        oriy = y
        for k,blck in enumerate(bloc["elems"]):
            #add the widget to the layout
            y = y +self.ystep
            for index, item in enumerate(blck):
                self._drawElem(item,x,y)
                x += int(item["width"]*self.scale) + 15
                listItem = QtGui.QListWidgetItem(list1)
                #listItem.setSizeHint(QtCore.QSize(item["width"]*self.scale,item["height"]*self.scale)) 
                #Or else the widget items will overlap (irritating bug)
#                blc.addWidget(item["id"])
                list1.setItemWidget(listItem,item["id"])
                #bloc["id"].addWidget(item["id"])
                if item["type"] == "inputStrArea":
                    item["id"].setFixedHeight(item["height"]*self.scale)
                    item["id"].setFixedWidth(item["width"]*self.scale)
                    y = item["height"]*self.scale
                    oriy = 0
            self.endBlock()
        #bloc["id"].setSizeHint(0,QtCore.QSize(200,y-oriy))
        self.notebook["tab"][bloc["name"]] =  bloc["id"]
        treeSubItem1 = QtGui.QTreeWidgetItem(bloc["id"])  #Make a subitem to hold our list
        #treeSubItem1.setColumnWidth(0,self.w*self.scale)
        #treeSubItem1.setBackgroundColor(0,QtGui.QColor(0, 0, 0))
        #treeSubItem1.setSizeHint(0,QtCore.QSize(50,50))
        self.notebook["id"].setItemWidget(treeSubItem1,0,list1)       #Assign this list as a tree item
        self.notebook["id"].setColumnWidth(0,self.w*self.scale)
        self.notebook["id"].setColumnWidth(1,self.w*self.scale)
        print dir(self.notebook["id"])
        #list1.setGeometry(0, 0,50,50)
        #list1.setFixedHeight(y-oriy)
        self.endBlock()
        #bloc["id"].setSizes(listes_x)
        return y



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
    def fileDialog(self,label="",callback=None):
        """ Draw a File input dialog
        @type  label: string
        @param label: the windows title       
        @type  callback: function
        @param callback: the callback function to call
        """         
        filename = QtGui.QFileDialog.getOpenFileName(self, 'Open file','/')
        if callback is not None :
            callback(str(filename))
        else :
            return filename

    def saveDialog(self,label="",callback=None):
        """ Draw a File input dialog
        @type  label: string
        @param label: the windows title       
        @type  callback: function
        @param callback: the callback function to call
        """         
        filename = QtGui.QFileDialog.getSaveFileName(self, 'Save file','/')
        if callback is not None :
            callback(str(filename))
        else :
            return filename

    def waitingCursor(self,toggle):
        """ Toggle the mouse cursor appearance from the busy to idle.
        @type  toggle: Bool
        @param toggle: Weither the cursor is busy or idle 
        """     
        pass#Qt.WaitCursor-Qt.ArrowCursor
        
    def updateViewer(self):
        """
        update the 3d windows if any
        """        
        pass#cmds.refresh()
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
    def endLayout(self):
        #cmds.window( gMainWindow, edit=True, widthHeight=(900, 777) )
        if self.subdialog:
#            self.widget.show()
            self.show()
        elif self.dock  :
            allowedAreas = ['right', 'left']
            #drag and dock to the parent?
            pass 
        else :
            self.show()
#
#
    def setReal(self,elem,val):
        """ Set the current Float value of the Float input elem
        @type  elem: dictionary
        @param elem: the elem input dictionary       
        @type  val: Float
        @param val: the new Float value
        """                                
        #to do interpret the elem["type"] to call the correct function
        if elem["type"] == 'sliders':
            elem["id"].setValue(val)
        elif elem["type"] == "inputInt":
            elem["id"].setValue(val)
        elif elem["type"] == "inputFloat":
            elem["id"].setValue(val)

    def getReal(self,elem):
        """ Return the current Float value of the Input elem
        @type  elem: dictionary
        @param elem: the elem input dictionary       
        
        @rtype:   Float
        @return:  the current Float value input for this specific elem
        """                                
        #to do interpret the elem["type"] to call the correct function
        #have to look at the type too
#        return elem["id"].value()

        return elem["id"].value()
#            return float(cmds.intField(elem["id"],q=1,v=1))
#        elif elem["type"] == "inputFloat":
#            return float(cmds.floatField(elem["id"],q=1,v=1))
        
    def getBool(self,elem):
        """ Return the current Bool value of the Input elem
        @type  elem: dictionary
        @param elem: the elem input dictionary       
        
        @rtype:   Bool
        @return:  the current Bool value input for this specific elem
        """ 
        if elem["type"] == 'checkbox':
            return bool(elem["id"].isChecked())

    def setBool(self,elem,val):
        """ Set the current Bool value of the Bool input elem
        @type  elem: dictionary
        @param elem: the elem input dictionary       
        @type  val: Bool
        @param val: the new Bool value
        """                      
        if elem["type"] == 'checkbox':
#            state = 0 if val else 2
            state = QtCore.Qt.Checked if val else QtCore.Qt.Unchecked  
            elem["id"].setCheckState(state)

    def getString(self,elem):
        """ Return the current string value of the String Input elem
        @type  elem: dictionary
        @param elem: the elem input dictionary       
        
        @rtype:   string
        @return:  the current string input value for this specific elem
        """  
        return str(elem["id"].text())

    def setString(self,elem,val):
        """ Set the current String value of the string input elem
        @type  elem: dictionary
        @param elem: the elem input dictionary       
        @type  val: string
        @param val: the new string value    
        """         
        elem["id"].setText(val)

    def getStringArea(self,elem):
        """ Return the current string area value of the String area Input elem
        @type  elem: dictionary
        @param elem: the elem input dictionary       
        
        @rtype:   string
        @return:  the current string area input value for this specific elem
        """                
        return elem["id"].toPlainText()

    def setStringArea(self,elem,val):
        """ Set the current String area value of the string input elem
        @type  elem: dictionary
        @param elem: the elem input dictionary       
        @type  val: string
        @param val: the new string value (multiline)   
        """                        
        elem["id"].setPlainText(val)

    def getLong(self,elem):
        """ Return the current Int value of the Input elem
        @type  elem: dictionary
        @param elem: the elem input dictionary       
        
        @rtype:   Int
        @return:  the current Int value input for this specific elem
        """                
        elem["id"].setFocus()
        if elem["type"] == "inputInt":
            return elem["id"].value()
        elif elem["type"] == "sliders":
            return elem["id"].value()
        elif elem["type"] == "inputFloat":
            return elem["id"].value()
        else:
            #specific command for menulike
            #str = elem["id"].value
            return elem["id"].currentIndex()#elem["value"].index(str) #maya combo menu is a txt + pulldown menu

    def setLong(self,elem,val):
        """ Set the current Int value of the Int input elem
        @type  elem: dictionary
        @param elem: the elem input dictionary       
        @type  val: Int
        @param val: the new Int value
        """                                
        if elem["type"] == "inputInt" or elem["type"] == "inputFloat" or elem["type"] == "inputFloat":
            elem["id"].setValue(val)
        else:
            elem["id"].setCurrentIndex(val)

    def getColor(self,elem,rgb=True):
        """ Return the current Color value of the Input elem
        @type  elem: dictionary
        @param elem: the elem input dictionary       
        
        @rtype:   Color
        @return:  the current Color array RGB value input for this specific elem
        """         
        color = elem["id"].getColor()#255.255.255=>convert to 1.0 1.0 1.0
        if rgb :
            return color.getRgbF()[0:3]
        else : 
            return color.getHsvF()[0:3]

    def setColor(self,elem,val,rgb=True):
        """ Set the current Color rgb arrray value of the Color input elem
        @type  elem: dictionary
        @param elem: the elem input dictionary       
        @type  val: Color
        @param val: the new Color value
        """ 
        color = elem["id"].getColor()
        if rgb :
            color.setRgbF(val[0], val[1], val[2]) 
        else :
            color.setHsvF(val[0], val[1], val[2]) 
        elem["id"].setColor(color)
        
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
    def _restore(self,rkey,dkey=None):
        """
        Function used to restore the windows data, usefull for plugin
        @type  rkey: string
        @param rkey: the key to access the data in the registry/storage       
        @type  dkey: string
        @param dkey: wiether we want a particular data from the stored dic
        """        
        if hasattr(QtCore,rkey):
            obj = QtCore.__dict__[rkey]
            if dkey is not None:
                if QtCore.__dict__[rkey].has_key(dkey) :
                    return  QtCore.__dict__[rkey][dkey]       
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
        QtCore.__dict__[rkey]= dict
#
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
        dial.display()
        #dial.CreateLayout()
        #dial.show()

#    already define 
#    def close(self,*args):
#        """ Close the windows"""
#        self._close()
#        cmds.window(self.winName,e=1,vis=False)
#
    def display(self):
        """ Create and Open the current gui windows """
        self._createLayout()
        self.show() #endlayout do the show
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
#                self.softdir = plugdirs[0]
#        print plugdirs
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
            layout = QtGui.QHBoxLayout()
            self.mainlayout.addLayout(layout)
            x=self.x
            for elem in block:
                if elem is None :
                    continue
                #if self.subdialog: print "draw",elem["type"]
                self._drawElem(elem, x, y)
                if type(elem["id"]) == int :
                    print elem
                else :
                    layout.addWidget(elem["id"])                        
                x += int(elem["width"]*self.scale) + 15
            self.endBlock()
        else : #dictionary: multiple line / format dict?
            if "0" in block:
                y = self._drawGroup(block,x,y)
            else :
                y = self._drawFrame(block,x,y)
                #self.endBlock()
        return y
    
            
class qtUIDialog(qtUI,uiAdaptor):
    def __init__(self,**kw):
        parent = mainRoot
    #def __init__(self, parent=None,subdialog=False):
        self.subdialog = False
        if "subdialog" in kw :
            self.subdialog = kw["subdialog"]
        if "parent" in kw :
            parent = kw["parent"]
        #QtGui.QWidget.__init__(self, parent)
        #QtGui.QMainWindow.__init__(self,kw["parent"])
        #print ("setCentralWidget",self.setCentralWidget)
        #close_old = self.close
        if self.subdialog :
            QtGui.QWidget.__init__(self,parent)
        else :
            QtGui.QDialog.__init__(self,parent)
        #close_widget = self.close
        #self.close = close_old
        #self._close = close_widget
        #self._createLayout()         
        if kw.has_key("title"):
            self.title= kw["title"]
            self.SetTitle(self.title)
        print ("ok diag inited")            
#        
#
#
#class mayaUISubDialog(mayaUIDialog):
#    def __init__(self,):
#        mayaUIDialog.__init__(self,)