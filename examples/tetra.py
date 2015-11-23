
"""
    Copyright (C) <2010>  Autin L. TSRI
    
    This file git_upy/examples/tetra.py is part of upy.

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
Created on Thu Feb 17 10:02:01 2011

@author: -
"""
#example for a script not a plugin ....
import sys,os
#pyubic have to be in the pythonpath, if not add it
#upypath = "/Users/ludo/pathtoupy/"
#sys.path.append(upypath)

import upy
upy.setUIClass()

from upy import uiadaptor
helperClass = upy.getHelperClass()

import numpy
import math

import os
import types
#import Tkinter
import Pmw
from weakref import ref 
from copy import deepcopy
import string

#from mglutil.gui.BasicWidgets.Tk.thumbwheel import ThumbWheel
#from DejaVu.viewerFns import checkKeywords
#from opengltk.OpenGL import GL
#from DejaVu.IndexedGeom import IndexedGeom
#from DejaVu.colorTool import RGBRamp, resetMaterialMemory
#from DejaVu.Insert2d import Insert2d
#import DejaVu.viewerConst
#from pyglf import glf


#class ColorMapLegend(Insert2d):
#    """Class for displaying a colormap legend.
#    arguments for the constructor or Set method are:
#       ramp: Numeric array of shape Nx3 or Nx4 (default is RBGRamp())
#       height: height of colormap legend
#       width:  width of colormap legend
#       interp: 1 or 0 to turn color interpolation on and off resp.
#       mini:   minimum values (i.e which corresponds to the first color)
#       maxi:   maximum values (i.e which corresponds to the last color)
#    
#    If interp is set to 1 QUAD_STRIPS are used and colors are interpolated,
#    else one QUAD is drawn for each entry in the colormap.
#    If the color provide alpha values, a chechered background is drawn.
#    """
#
#    keywords = Insert2d.keywords + [
#        'ramp',
#        'height',
#        'width',
#        'interp',       # 1: for color interpolation, or 0
#        'mini',         # 
#        'maxi',         #
#        'labelValues',  # floating point numbers to be written below cml
#        'glfFont',
#        'fontScale',
#        'numOfLabels',
#        'unitsString',
#        'interp',
#        'visibleFrame',
#        'invertLabelsColor',
#        ]    
#
#    glfVectorFontList = [
#        'arial1.glf',
#        'courier1.glf',
#        'crystal1.glf',
#        'techno0.glf',
#        'techno1.glf',
#        'times_new1.glf',
#        'aksent1.glf',
#        'alpine1.glf',
#        'broadway1.glf',
#        'chicago1.glf',
#        'compact1.glf',
#        'cricket1.glf',
#        'garamond1.glf',
#        'gothic1.glf',
#        'penta1.glf',
#        'present_script1.glf'
#    ]
#
#
#    def __init__(self, name='color map legend', check=1, **kw):
#
#        # GLF FONTS Initialisations
#        glf.glfInit()
#        glf.glfEnable(glf.GLF_CONSOLE_MESSAGES)
#        lGlfModulePath = os.path.split(glf.__file__)[-2]
#        lPathToFonts = lGlfModulePath+os.sep+'fonts'+os.sep
#        self.glfVectorFontLoadIdDict = {}
#        for font in self.glfVectorFontList:
#            self.glfVectorFontLoadIdDict[font] = glf.glfLoadFont(lPathToFonts+font)   
#        self.fontScale = 8
#        self.glfFontID = 0
#
#        # other initialisations
##        self.colormapguiRef = ref(colormapgui) 
#        self.resizeSpotRadius = 5 
#        self.resizeSpot = None
#        self.verticalLegend = True
#
#        self.mini = None
#        self.maxi = None
#        
#        kw['ramp'] = RGBRamp()
#        kw['height'] = 1.
#        kw['width'] = len(kw['ramp'])
#        kw['interp'] = 1
##        kw['mini'] = None
##        kw['maxi'] = None
#        kw['labelValues'] = []
#        kw['numOfLabels'] = 5
#        kw['unitsString'] = 'law'
#        kw['invertLabelsColor'] = False
#        kw['visibleFrame'] = True
#
#        #kw['protected'] = True
#        kw['immediateRendering'] = False
#        kw['visible'] = False
#        kw['transparent'] = True
#
#        kw['size'] = [12, 120] # override the default value in Insert2d
#
#        self.clickPosFromLegendBottomLeft = [0, 0]
#
#        apply( Insert2d.__init__, (self, name, check), kw)
#
#        # Insert2d initialisations 
#        # (need to be done after the Insert2d.__init__ otherwise it overrides)
#        self.needsRedoDpyListOnResize = True
#        self.initialPosition = [1, 350] # override the default value in Insert2d
#        self.coord2d = deepcopy(self.initialPosition) # 2d coordinates in pixels from top left
#        self.animatable = False
#
#
#    def Set(self, check=1, redo=1, updateOwnGui=True, **kw):
#        """set data for this object: add faces (polygon or lines) to this object
#        check=1 : verify that all the keywords present can be handle by this func 
#        redo=1 : append self to viewer.objectsNeedingRedo
#        updateOwnGui=True : allow to update owngui at the end this func
#        """
#        #print "colorMapLegend.Set"
#        redoFlags = apply( Insert2d.Set, (self, check, 0), kw)
#        
#        ramp=kw.get('ramp')
#        if ramp is not None:
#            assert len(ramp) > 0
#            assert len(ramp[0])==3 or len(ramp[0])==4
#            self.ramp = ramp
#            redoFlags |= self._redoFlags['redoDisplayListFlag']
#
#        height = kw.get('height')
#        if height:
#            assert height > 0.0
#            self.height = height
#            redoFlags |= self._redoFlags['redoDisplayListFlag']
#
#        width = kw.get('width')
#        if width:
#            assert width > 0.0
#            self.width = width
#            redoFlags |= self._redoFlags['redoDisplayListFlag']
#
#        mini = kw.get('mini')
#        if mini is not None:
#            #assert isinstance(mini, types.FloatType)
#            self.mini = mini
#            redoFlags |= self._redoFlags['redoDisplayListFlag']
#
#        maxi = kw.get('maxi')
#        if maxi is not None:
#            #assert isinstance(maxi, types.FloatType)
#            self.maxi = maxi
#            redoFlags |= self._redoFlags['redoDisplayListFlag']
#
#        labelValues = kw.get('labelValues')
#        if labelValues is not None:
#            # for v in labelValues:
#            #    assert isinstance(v, types.FloatType)
#            self.labelValues = labelValues
#            redoFlags |= self._redoFlags['updateOwnGuiFlag']
#            redoFlags |= self._redoFlags['redoDisplayListFlag']
#
#        glfFont = kw.get('glfFont')
#        if glfFont is not None:
#            if glfFont in self.glfVectorFontLoadIdDict.keys():
#                self.glfFontID = self.glfVectorFontLoadIdDict[glfFont]
#                redoFlags |= self._redoFlags['updateOwnGuiFlag']
#                redoFlags |= self._redoFlags['redoDisplayListFlag']
#
#        fontScale = kw.get('fontScale')
#        if fontScale is not None:
#            assert isinstance(fontScale, types.IntType)
#            self.fontScale = fontScale
#            redoFlags |= self._redoFlags['updateOwnGuiFlag']
#            redoFlags |= self._redoFlags['redoDisplayListFlag']
#
#        numOfLabels = kw.get('numOfLabels')
#        if numOfLabels is not None:
#            assert isinstance(numOfLabels, types.IntType)
#            self.numOfLabels = numOfLabels
#            redoFlags |= self._redoFlags['updateOwnGuiFlag']
#            redoFlags |= self._redoFlags['redoDisplayListFlag']
#
#        unitsString = kw.get('unitsString')
#        if unitsString is not None:
#            self.unitsString = unitsString
#            redoFlags |= self._redoFlags['updateOwnGuiFlag']
#            redoFlags |= self._redoFlags['redoDisplayListFlag']
#
#        interp = kw.get('interp')
#        if interp is not None:
#            assert interp in (0, 1)
#            self.interp = interp
#            redoFlags |= self._redoFlags['updateOwnGuiFlag']
#            redoFlags |= self._redoFlags['redoDisplayListFlag']
#
#        visibleFrame = kw.get('visibleFrame')
#        if visibleFrame is not None:
#            self.visibleFrame = visibleFrame
#            redoFlags |= self._redoFlags['updateOwnGuiFlag']
#            redoFlags |= self._redoFlags['redoDisplayListFlag']
#
#        invertLabelsColor = kw.get('invertLabelsColor')
#        if invertLabelsColor is not None:
#            self.invertLabelsColor = invertLabelsColor
#            redoFlags |= self._redoFlags['updateOwnGuiFlag']
#            redoFlags |= self._redoFlags['redoDisplayListFlag']
#
#        return self.redoNow(redo, updateOwnGui, redoFlags)
#
#
#    def Draw(self):
#        #print "colorMapLegend.Draw", self
#
#        if self.viewer.tileRender:
#            tile = self.getTile()
#            #print "tile", tile
#        else:
#            tile = None
#
#        fullWidth = self.viewer.currentCamera.width
#        fullHeight = self.viewer.currentCamera.height
#
#        if self.invertLabelsColor is False:
#            backgroundColor = (
#                           self.viewer.currentCamera.backgroundColor[0],
#                           self.viewer.currentCamera.backgroundColor[1],
#                           self.viewer.currentCamera.backgroundColor[2],
#                           .5)
#        else:
#            backgroundColor = (
#                           1-self.viewer.currentCamera.backgroundColor[0],
#                           1-self.viewer.currentCamera.backgroundColor[1],
#                           1-self.viewer.currentCamera.backgroundColor[2],
#                           .5)
#
#        from DejaVu.Legend import drawSelfOrientedLegend
#        self.polygonContour , self.resizeSpot , self.verticalLegend = drawSelfOrientedLegend( 
#                fullWidth=fullWidth,
#                fullHeight=fullHeight,
#                tile=tile,
#                ramp=self.ramp,
#                mini=self.mini,
#                maxi=self.maxi,
#                name=self.name,
#                unit=self.unitsString,
#                labelValues=self.labelValues,
#                roomLeftToLegend=self.coord2d[0],
#                roomBelowLegend=fullHeight-self.coord2d[1],
#                legendShortSide=self.size[0],
#                legendLongSide=self.size[1],
#                significantDigits=3,
#                backgroundColor=backgroundColor,
#                interpolate=self.interp,
#                frame=self.visibleFrame,
#                selected=(self.viewer.currentObject == self),
#                numOfLabels=self.numOfLabels,
#                resizeSpotRadius=self.resizeSpotRadius,
#                fontScale=self.fontScale,
#                glfFontID=self.glfFontID,
#        )
#
#        return 1
#
#
#    def pickDraw(self):
#        """called by the picking process to operate the selection
#        """
#        #print "colorMapLegend.pickDraw", self
#        # we draw just flat quad of the insert2d
#        GL.glMatrixMode(GL.GL_PROJECTION)
#        GL.glPushMatrix()       
#        #GL.glLoadIdentity()
#        GL.glLoadMatrixf(self.viewer.currentCamera.pickMatrix) 
#        GL.glOrtho(0, float(self.viewer.currentCamera.width),
#                   0, float(self.viewer.currentCamera.height), -1, 1)
#        GL.glMatrixMode(GL.GL_MODELVIEW)
#        GL.glPushMatrix()
#        GL.glLoadIdentity()
#        GL.glPolygonMode(GL.GL_FRONT, GL.GL_FILL)
#        #GL.glColor3f(1,0,0)
#
#        if self.resizeSpot is not None:
#            GL.glPushName(1)
#            GL.glBegin(GL.GL_QUADS)
#            GL.glVertex2f(float(self.resizeSpot[0]+self.resizeSpotRadius),
#                          float(self.resizeSpot[1]-self.resizeSpotRadius))
#            GL.glVertex2f(float(self.resizeSpot[0]+self.resizeSpotRadius),
#                          float(self.resizeSpot[1]+self.resizeSpotRadius))
#            GL.glVertex2f(float(self.resizeSpot[0]-self.resizeSpotRadius),
#                          float(self.resizeSpot[1]+self.resizeSpotRadius))
#            GL.glVertex2f(float(self.resizeSpot[0]-self.resizeSpotRadius),
#                          float(self.resizeSpot[1]-self.resizeSpotRadius))
#            GL.glEnd()
#            GL.glPopName()
#
#        GL.glPushName(0)
#        GL.glBegin(GL.GL_QUADS)
#        GL.glVertex2fv(self.polygonContour[0])
#        GL.glVertex2fv(self.polygonContour[1])
#        GL.glVertex2fv(self.polygonContour[2])
#        GL.glVertex2fv(self.polygonContour[3])
#        GL.glEnd()
#        GL.glPopName()
#
#        GL.glMatrixMode(GL.GL_PROJECTION)
#        GL.glPopMatrix()
#        GL.glMatrixMode(GL.GL_MODELVIEW)
#        GL.glPopMatrix()
#
#
#    def setPosition(self, event, redo=1):
#        """the trackball transmit the translation info
#        """
#        #print "colorMapLegend.setPosition", event.x, event.y
#        self.coord2d[0] = event.x - self.clickPosFromLegendBottomLeft[0]
#        self.coord2d[1] = event.y - self.clickPosFromLegendBottomLeft[1]
#
#        if self.coord2d[0] < 0:
#            self.coord2d[0] = 0
#        if self.coord2d[1] < 0:
#            self.coord2d[1] = 0
#
#        if self.coord2d[0] > self.viewer.currentCamera.width:
#            self.coord2d[0] = self.viewer.currentCamera.width
#        if self.coord2d[1] > self.viewer.currentCamera.height:
#            self.coord2d[1] = self.viewer.currentCamera.height
#
#        self.viewer.objectsNeedingRedo[self] = None
#
#
#    def setSize(self, event, redo=1):
#        """override the Insert2d function
#        """
#        #print "colorMapLegend.setSize", self
#        if self.verticalLegend is True:
#            self.size[0] = event.x - self.coord2d[0]        
#            self.size[1] = self.coord2d[1] - event.y
#
#            if self.size[0] > self.viewer.currentCamera.width:
#                self.size[0] = self.viewer.currentCamera.width
#            if self.size[1] > self.viewer.currentCamera.height:
#                self.size[1] = self.viewer.currentCamera.height
#        else:
#            self.size[1] = event.x - self.coord2d[0]        
#            self.size[0] = self.coord2d[1] - event.y
#
#            if self.size[1] > self.viewer.currentCamera.width:
#                self.size[1] = self.viewer.currentCamera.width
#            if self.size[0] > self.viewer.currentCamera.height:
#                self.size[0] = self.viewer.currentCamera.height
#
#        if self.size[0] < 1:
#            self.size[0] = 1
#        if self.size[1] < 1:
#            self.size[1] = 1
#
#        if self.needsRedoDpyListOnResize and self.viewer:
#            self.viewer.objectsNeedingRedo[self] = None
#
#
#    def ResetPosition(self):
#        self.coord2d = deepcopy(self.initialPosition)
#        if self.viewer:
#            self.viewer.objectsNeedingRedo[self] = None
#
#
#    def respondToDoubleClick(self, event):
#        """
#        """
#        self.showOwnGui()
#
#        if self.needsRedoDpyListOnResize and self.viewer:
#            self.viewer.objectsNeedingRedo[self] = None
#
#
#    def processHit_cb(self, pick):
#        #print "colorMapLegend.processHit_cb", self
#        #print "pick",pick
#        #print "pick.event",dir(pick)
#        #print "pick.type",pick.type
#        #print "pick.event",dir(pick.event)
#        #print "pick.event",pick.event
#        #print "pick.event.type",pick.event.type
#        #print "pick.event.state",pick.event.state
#        #print "pick.event.time",pick.event.time
#        #print "pick.hits",pick.hits
#
#        if ( len(pick.hits) == 1) and  pick.hits.has_key(self):
#            if self.viewer.currentObject != self:
#                    # if the only hit is the legend, 
#                    # it becomes the current object
#                    self.viewer.SetCurrentObject(self)
#                    self.isMoving = True
#            elif pick.event.time - self.lastPickEventTime < 200: #double click
#                self.viewer.SetCurrentObject(self.viewer.rootObject)
#                self.respondToDoubleClick(pick.event)
#            elif pick.hits[self][0][0] == 1:
#                # the click in inside the resize button
#                #print "resize"
#                self.isMoving = False
#            elif pick.hits[self][0][0] == 0:
#                # the click in inside the legend but outside 
#                # the resize button
#                self.isMoving = True
#                self.clickPosFromLegendBottomLeft = [pick.event.x - self.coord2d[0],
#                                                     pick.event.y - self.coord2d[1]]
#                #print "self.clickPosFromLegendBottomLeft", self.clickPosFromLegendBottomLeft
#
#            if self.viewer:
#                self.viewer.objectsNeedingRedo[self] = None
#
#        elif self.viewer.currentObject == self:
#            #print "the insert2d is selected, but picking is outside"
#            self.isMoving = None
#            self.viewer.SetCurrentObject(self.viewer.rootObject)
#            if self.needsRedoDpyListOnResize and self.viewer:
#                self.viewer.objectsNeedingRedo[self] = None
#
#        self.lastPickEventTime = pick.event.time
#
#
#    def createOwnGui(self):
#        self.ownGui = Tkinter.Toplevel()
#        self.ownGui.title(self.name)
#        self.ownGui.protocol('WM_DELETE_WINDOW', self.ownGui.withdraw )
#
#        frame1 = Tkinter.Frame(self.ownGui)
#        frame1.pack(side='top')
#
#        #unit
#        self.unitsEnt = Pmw.EntryField(frame1, 
#                                       label_text='Units  ',
#                                       labelpos='w',
#                                       value=self.unitsString,
#                                       command=self.setWithOwnGui)
#        self.unitsEnt.pack(side='top', fill='x')
#
#        #glf vector font
#        self.glfFont = Tkinter.StringVar()
#        self.glfFont.set('chicago1.glf')
#        self.glfFontCB = Pmw.ComboBox(frame1, label_text='Font    ',
#                                   labelpos='w',
#                                   entryfield_value=self.glfFont.get(),
#                                   scrolledlist_items=self.glfVectorFontList,
#                                   selectioncommand=self.setWithOwnGui)
#        self.glfFontCB.pack(side='top', fill='x')
#
#        #fontScale
#        self.fontScaleThumb = ThumbWheel(frame1,
#                                    labCfg={'text':'font scale            ', 'side':'left'},
#                                    showLabel=1, 
#                                    width=90,
#                                    height=14,
#                                    min=0, 
#                                    max=200,
#                                    type=int, 
#                                    value=self.fontScale,
#                                    callback=self.setWithOwnGui,
#                                    continuous=True,
#                                    oneTurn=10,
#                                    wheelPad=0)
#        self.fontScaleThumb.pack(side='top')
#
#        #label
#        lLabelValuesString = ''
#        for lLabelValue in self.labelValues:
#            lLabelValuesString += str(lLabelValue) + ' '
#        self.labelValsEnt = Pmw.EntryField(
#                                frame1, 
#                                label_text='Numeric labels    ',
#                                labelpos='w',
#                                value=lLabelValuesString,
#                                command=self.setWithOwnGui)
#        self.labelValsEnt.component('entry').config(width=6)
#        self.labelValsEnt.pack(side='top', fill='x')
#
#        #numOfLabel
#        self.numOfLabelsCtr = ThumbWheel(frame1,
#                                    labCfg={'text':'Automatic labels', 'side':'left'},
#                                    showLabel=1, 
#                                    width=90,
#                                    height=14,
#                                    min=0, 
#                                    max=200,
#                                    type=int, 
#                                    value=self.numOfLabels,
#                                    callback=self.setWithOwnGui,
#                                    continuous=True,
#                                    oneTurn=20,
#                                    wheelPad=0)
#        self.numOfLabelsCtr.pack(side='top')
#
#        # Interpolate
#        self.interpVar = Tkinter.IntVar()
#        self.interpVar.set(0)
#        self.checkBoxFrame = Tkinter.Checkbutton(
#                                frame1, 
#                                text='Interpolate',
#                                variable=self.interpVar, 
#                                command=self.setWithOwnGui)
#        self.checkBoxFrame.pack(side='top')
#
#        # frame
#        self.frameVar = Tkinter.IntVar()
#        self.frameVar.set(1)
#        self.checkBoxFrame = Tkinter.Checkbutton(
#                                frame1, 
#                                text='Frame',
#                                variable=self.frameVar, 
#                                command=self.setWithOwnGui)
#        self.checkBoxFrame.pack(side='top')
#
#        # invert labels color
#        self.invertLabelsColorVar = Tkinter.IntVar()
#        self.invertLabelsColorVar.set(0)
#        self.checkBoxinvertLabelsColor = Tkinter.Checkbutton(
#                                frame1, 
#                                text='Invert labels color',
#                                variable=self.invertLabelsColorVar, 
#                                command=self.setWithOwnGui)
#        #self.checkBoxFrame.pack(side='top')
#        self.checkBoxinvertLabelsColor.pack(side='top')
#
#        # colormapguiwidget:
##        self.launchColormapWidget = Tkinter.Button(
##                                        frame1, 
##                                        text="Show colormap settings",
##                                        command=self.colormapguiRef().showColormapSettings_cb 
##                                        )
##        self.launchColormapWidget.pack(side='top', fill='x')
#
#
#    def setWithOwnGui(self, event=None):
#        #print "setWithOwnGui"
#
#        glfFont = self.glfFontCB.get()
#        fontScale = int(self.fontScaleThumb.get())
#        labelValues = map(float, string.split(self.labelValsEnt.get()))
#        unitsString = self.unitsEnt.get()
#        numOfLabels = int(self.numOfLabelsCtr.get())
#
#        if self.interpVar.get() == 1:
#            interp = True
#        else:
#            interp = False
#
#        if self.frameVar.get() == 1:
#            visibleFrame = True
#        else:
#            visibleFrame = False
#
#        if self.invertLabelsColorVar.get() == 1:
#            invertLabelsColor = True
#        else:
#            invertLabelsColor = False
#
#        self.Set(
#                glfFont=glfFont,
#                fontScale=fontScale,
#                labelValues=labelValues, 
#                numOfLabels=numOfLabels,
#                unitsString=unitsString,
#                interp=interp,
#                visibleFrame=visibleFrame,
#                invertLabelsColor=invertLabelsColor,
#                updateOwnGui=False)
#        self.viewer.Redraw()
#
#
#    def updateOwnGui(self):
#        if self.ownGui is None:
#            return
#        self.ownGui.title(self.name)
#        self.glfFontCB.selectitem(self.glfFont.get())
#        self.fontScaleThumb.set(self.fontScale)
#        lLabelValuesString = ''
#        for lLabelValue in self.labelValues:
#            lLabelValuesString += str(lLabelValue) + ' '
#        self.labelValsEnt.setentry(lLabelValuesString)
#        self.unitsEnt.setentry(self.unitsString)
#        self.numOfLabelsCtr.set(self.numOfLabels)
#        self.interpVar.set(self.interp)
#        self.invertLabelsColorVar.set(self.visibleFrame)
#        self.invertLabelsColorVar.set(self.invertLabelsColor)
#
#def animateColors(listeColor,obj,nb=None):
#    #require DejaVu object, didnt work properly yet
#    from opengltk.extent import _glextlib
#    from opengltk.OpenGL import GL
#    from opengltk.extent import _gllib
#    import numpy
#    N = len(listeColor)
#    if nb is not None:
#        N =nb
#    #loop over?
#    i=0
#    icolor = 0
#    while  i < N:
#        col1 = listeColor[icolor]
#        length = 4*len(col1)*len(col1[0])
#        _glextlib.glBindBufferARB(_glextlib.GL_ARRAY_BUFFER_ARB,
#                                  int(obj.vertexArrayFlagBufferList[3]))
#        _glextlib.glBufferDataARB(_glextlib.GL_ARRAY_BUFFER_ARB, length, col1,
#                                  _glextlib.GL_STATIC_DRAW_ARB)
#        _gllib.glColorPointer(4, GL.GL_FLOAT, 0, 0)
#        vi.OneRedraw()
#        vi.update()
#        i+=1
#        icolor += 1
#        if icolor >= len(listeColor):
#            icolor=0

class Tetra:
    def __init__(self,name=None,filename=None,helper=None,**kw):
        self.filename=filename
        self.name=name
        self.nodes=None
        self.cells=None
        self.nvars=None
        self.cvars=None
        self.ncolors={}
        self.ccolors={}
        self.mesh = {}
        #self.meshs= None
        self.faces = None
        self.helper = helper
        self.mode ='gmv'
        self.current_mesh= ""
        if helper is None :
            self.helper = helperClass(**kw)
        if self.filename is not None:
            fileName, fileExtension = os.path.splitext(self.filename)
            if fileExtension == ".gmv":
                self.nodes, self.cells, self.nvars, self.cvars = self.parse()
                self.getColors()
            elif fileExtension == "" :
                self.mode ='c'
                self.nodes, self.cells, self.nvars, self.cvars = self.parseTxt() 
                self.getColors()
            if self.name is None:
                self.name = os.path.splitext(os.path.basename(filename))[0]

    def setFromArray(self,nodes=None,cells=None,nvars=None,cvars=None):
        if nodes is not None:
            self.setNodes(nodes)
        if cells is not None:
            self.setCells(cells)
        if nvars is not None:
            for k in nvars.keys():
                self.setNodeVars(k,nvars[k])
        if cvars is not None:
            for k in cvars.keys():
                self.setCellVars(k,nvars[k])

    def setNodeVars(self,name,values):
        self.nvars[name] = values
        
    def setCellVars(self,name,values):
        self.cvars[name] = values
        
    def setNodes(self,values):
        self.nodes = values
        
    def setCells(self,values):
        self.cells = values
        
    def Set(self,**kw):
        if kw.has_key("name"):
            self.name = kw["name"]
        if kw.has_key("filename"):
            self.filename = kw["filename"]
        if kw.has_key("parse"):
            if kw["parse"] :
                if self.filename is not None:
                    fileName, fileExtension = os.path.splitext(self.filename)
                    if fileExtension == ".gmv":
                        self.nodes, self.cells, self.nvars, self.cvars = self.parse()
                        self.getColors()
                    elif fileExtension == "" :
                        self.mode ='c'
                        self.nodes, self.cells, self.nvars, self.cvars = self.parseTxt() 
                        self.getColors()
                    if self.name is None:
                        self.name = os.path.splitext(os.path.basename(filename))[0]
    
    def parseTxt(self,filename=None):
        if filename is None :
            filename = self.filename
        if filename is None :
            return None,None,None,None
        #parse the vertices
        f = open(filename+"_vertices.txt")
        lines = f.readlines()
        f.close()
        nodes =[]
        for i in range(1,len(lines)) :
            l = lines[i].split()
            nodes.append([float(l[0]),float(l[1]),float(l[2])])
        #parse the quad
        f = open(filename+"_elements.txt")
        lines = f.readlines()
        f.close()
        quads=[]
        for i in range(1,len(lines)) :
            l = lines[i].split()
            quads.append([int(l[3])-1,int(l[1])-1,int(l[0])-1,int(l[2])-1])
        nvars = {}
        data = numpy.load(filename+"_wave.npy")
        dt = data.transpose()#invert ?
        for i in range(len(dt)):
            nvars[str(i)] = dt[i]
        return nodes,quads,nvars,None
        
    def parse(self,filename=None):
        if filename is None :
            filename = self.filename
        if filename is None :
            return None,None,None,None
        f = open(filename)
        lines = f.readlines()
        f.close()
    
        cells = []
        nvars = {}
        cvars = {}
    
        mode = None
        for line in lines:
            if len(line)<2:
                continue
    
            if line[:6]=='nodes ':
                mode='nodesX'
            elif line[:6]=='cells ':
                mode='cells'
            #elif line[:8]=='variable':
            #    mode='variable'
            elif line[:5]=='node_': #FIXME handle the following number
                mode='nvar'
                name = line.split()[0]
            elif line[:5]=='cell_': #FIXME handle the following number
                mode='cvar'
                name = line.split()[0]
            elif line[:7]=='endvars' or line[:7]=='endgmv':
                mode = None
    
            elif mode=='nodesX':
                nodesX = [float(x) for x in line.split()]
                mode='nodesY'
            elif mode=='nodesY':
                nodesY = [float(x) for x in line.split()]
                mode='nodesZ'
            elif mode=='nodesZ':
                nodesZ = [float(x) for x in line.split()]
                mode = None
            elif mode=='cells':
                tet = [int(x)-1 for x in line.split()[2:]]
                if len(tet)==4:
                    cells.append(tet)
            #elif mode=='variable':
            #    name = line[:-1]
            elif mode=='nvar':
                nvars[name] = [float(x) for x in line.split()]
            elif mode=='cvar':
                cvars[name] = [float(x) for x in line.split()]
    
        nodes = zip(nodesX, nodesY, nodesZ)
        return nodes, cells, nvars, cvars

    def getColors(self):
        from DejaVu.colorTool import Map, RGBRamp#,RedWhiteBlueRamp
        from DejaVu.colorMap import ColorMap
        from upy.colors import RedWhiteBlueRamp
        #from DejaVu.colorMapLegend import ColorMapLegend
        ramp = RedWhiteBlueRamp()#RGBRamp()
        self.cmap = ColorMap(name="tetra", ramp=ramp)
        cmlOptions = {'width':10, 'height':1,
                      'name':"tetra", 'ramp':ramp,"visible":True}
#        self.legend = ColorMapLegend(**cmlOptions)
#        self.helper.AddObject(self.legend)
        self.ncolors = {}
        if self.nvars is not None :
            for k,v in self.nvars.items():
                self.ncolors[k] = Map(v, ramp)
        
        self.ccolors = {}
        if self.cvars is not None :
            for k,v in self.cvars.items():
                colors = Map(v, ramp)
                cols = []
                for c in colors:
                    cols.extend( (c,)*4 )
                self.ccolors[k] = cols
   
    def makeFaces(self,cells=None):
        if cells is None :
            cells = self.cells
            if self.cells is None :
                return None
        if self.mode =='c' : 
            return cells
        # faces are counter clockwise in the file
        faces = {} # dict used to avoid duplicates
        allFaceList = [] # list of triangular faces
        allTetFaces = [] # list of face indices for faces of each tet
                         # negative index means reverse indices to make clockwise
        nbf = 0
        nbt = 0
        n = 0
        allTetFaces = []
        for i,j,k,l in cells:
            allTetFaces.extend([ [i,k,j], [k,l,j], [l,k,i] , [l,i,j] ])
        return allTetFaces
        
    def createMesh(self,name=None,cells=None):
        if self.helper is None :
            return  
        if name is None:
            name = self.name
        if name not in self.mesh:
            if cells is None:
                f = self.faces
                if f is None :
                    f = self.makeFaces()
            else :
                f = self.makeFaces(cells=cells)
#            if cells is not None :
#                v=[]
#                for c in cells :
#                    for vi in c :
#                        if vi not in v :
#                            v.append(self.nodes[vi])
#                numpy.array([self.getVerticesTetra(c) for c in cells]).flatten()
#            else :
#                v = self.nodes
            self.mesh[name] = self.helper.createsNmesh(name,self.nodes,None,f)
            self.helper.addObjectToScene(None,self.mesh[name][0])
        else :
            #update ?
            pass

    def retrievePropertiesFromName(self,name):
        for k in self.ncolors:
            if k == name :
                return self.nvars[k]
        for k in self.ccolors:
            if k == name :
                return self.cvars[k]
                
    def retrieveColorFromName(self,name):
        for k in self.ncolors:
            if k == name :
                return self.ncolors[k]
        for k in self.ccolors:
            if k == name :
                return self.ccolors[k]
        
    def setMeshColor(self,name,key):
        if self.helper is None :
            return
        var = self.retrieveColorFromName(key)
        if name in self.mesh:
            self.helper.changeColor(self.mesh[name][1],var)#front Line, back fill??
            self.current_colors=var

    def loopOverColor(self,meshname,listeColors=None,nb=None,interpolate=False,interpolateR=10):
        if listeColors is None:
            listeColors = list(self.ncolors.values())
        N = len(listeColors)
        if nb is not None:
            N =nb
        #loop over?
        i=0
        icolor = 0
        curentcol = self.current_colors#self.mesh[meshname][1].materials[1028].GetProperty(1)[1][:,:3]#current vcolor ?
        while  i < N:
            col1 = listeColors[icolor]
            if interpolate :
                for j in range(interpolateR):
                    rcol = curentcol + float(j)/float(interpolateR)*(col1-curentcol) 
                    self.helper.changeColor(self.mesh[meshname][1],rcol)
                    self.updateViewer()
#                    vi.OneRedraw()
#                    vi.update()
            else :
                self.helper.changeColor(self.mesh[meshname][1],col1)
                self.updateViewer()
#                vi.OneRedraw()
#                vi.update()
            i+=1
            icolor += 1
            if icolor >= len(listeColors):
                icolor=0
            curentcol = col1
            
    def selectCells(self,var,cutoff,cells=None):
        #ex:cellsOn, cellsOff = selectCells(cells, nvars['node_0'], 0.2)
        if cells is None:
            cells = self.cells
        selectedCells = []
        notSelected = []
        for cell in cells:
            i,j,k,l = cell
            if var[i]>cutoff or var[j]>cutoff or var[k]>cutoff or var[l]>cutoff:
                selectedCells.append(cell)
            else:
                notSelected.append(cell)
        return selectedCells, notSelected

    def setColorPropertyInt(self,i):
        if self.mode == 'c':
            c=self.ncolors[str(i)]
        else :
            c=list(self.ncolors.values())[i]        
        self.helper.changeColor(self.mesh[self.current_mesh][1],c)                

class TetraTools:
    def __init__(self):
        self.listTetra=[]
        self.listMesh=[]
        

#add slider player for properties
class TetraToolsGui(uiadaptor):
    def setup(self,**kw):
        #uiadaptor.__init__(self,**kw)
        #self.title = "Tetrahedron"
        self.initWidget(id=10)
        self.setupLayout()
        self.helper = helperClass(**kw) 
        self.listeTetra={}
        self.listeTetraName=[]
        self.currentTetra = None
        self.listeColors=[]
        self.currentColor=None
        
    #theses two function are for c4d
    def CreateLayout(self):
        self._createLayout()
        return 1

    def Command(self,*args):
#        print args
        self._command(args)
        return 1

            
    def initWidget(self,id=None):
        #this where we define the buttons
        if id is not None :
            id=id
        else:
            id = self.bid
        self.id = id   
        self.LABELS={}
        self.LABELS["load"] = self._addElemt(label="to a GMV file",width=60)
        self.LABELS["curT"] = self._addElemt(label="current tetrahedre",width=60)
        self.LABELS["curP"] = self._addElemt(label="current properties",width=60)
        
        self.LABELS["min"] = self._addElemt(label="min:",width=60)
        self.LABELS["max"] = self._addElemt(label="max:",width=60)
        self.LABELS["makeOff"] = self._addElemt(label="Make cells using cutoff",width=60)
        self.LABELS["lengthInter"] = self._addElemt(label="Interpolation length",width=60)
        self.LABELS["nLoop"] = self._addElemt(label="Nb of loop",width=60)

        #we need a File load 
        self.LOADFILE = self._addElemt(name="Browse",width=40,height=10,
                         action=self.browseGMV,type="button")
        #we need a File load 
        self.CLOSEBTN = self._addElemt(name="Close",width=40,height=10,
                         action=self.close,type="button")
                         
        self.PMENU={}
        #current Tetra menu
        self._cTetra = self.addVariable("int",1)
        self.PMENU["tetra"] = self._addElemt(name="Current",value=[],
                                    width=60,height=10,action=self.setCurTetra,
                                    variable=self._cTetra,
                                    type="pullMenu")
        #we need pulldown for color method
        self._colors = self.addVariable("int",1)
        self.PMENU["properties"] = self._addElemt(name="Properties",value=[],
                                    width=60,height=10,action=self.setCurTetraProperties,
                                    variable=self._colors,
                                    type="pullMenu")
        #we need pulldown for color method
        self._comp = self.addVariable("int",1)
        self.listeMesh=[]
        self.PMENU["comp"] = self._addElemt(name="Meshes",value=[],
                                    width=60,height=10,action=None,#self.setCurCompMesh,
                                    variable=self._comp,
                                    type="pullMenu")
        self.IN={}
        self.IN["nbComp"] = self._addElemt(name='nbComp',width=100,height=10,
                                              action=None,
                                              type="inputInt",icon=None,
                                              value = 100.,
                                              variable=self.addVariable("int",1),
                                              mini=1,maxi=10,step=1)
        self.IN["lengthInter"] = self._addElemt(name='lengthInter',width=100,height=10,
                                              action=None,
                                              type="inputInt",icon=None,
                                              value = 5,
                                              variable=self.addVariable("int",5),
                                              mini=1,maxi=50,step=1)
        self.IN["nLoop"] = self._addElemt(name='nLoop',width=100,height=10,
                                              action=None,
                                              type="inputInt",icon=None,
                                              value = 10,
                                              variable=self.addVariable("int",10),
                                              mini=1,maxi=100,step=1)
        #we need separator ? different mesh?
        self.BTN={}
        self.BTN["build"] = self._addElemt(name="Build All",width=40,height=10,
                         action=self.buildMesh,type="button")
        self.BTN["buildC"] = self._addElemt(name="Build Compartiments",width=40,height=10,
                         action=self.buildPropertiesMesh,type="button")
        self.BTN["color"] = self._addElemt(name="Apply Properties as VColors",width=40,height=10,
                         action=self.setCurTetraColors,type="button")
        self.BTN["loopcolor"] = self._addElemt(name="Loop over Properties as VColors",width=40,height=10,
                         action=self.loopOverPropertiesColor,type="button")
        #need the slider with min max display to build need a properties and a cutoff
        self.IN["cutoff"] = self._addElemt(name='cutoff',width=20,height=10,
                                              action=None,
                                              type="inputFloat",icon=None,
                                              value = 0.,
                                              variable=self.addVariable("float",0.),
                                              mini=0.,maxi=0.1,step=0.1)
        self.IN["makeOff"] = self._addElemt(name="OffCells",width=80,height=10,
                                              action=None,type="checkbox",icon=None,
                                              variable=self.addVariable("int",0))
        self.IN["interpolate"] = self._addElemt(name="Interpolate",width=80,height=10,
                                              action=None,type="checkbox",icon=None,
                                              variable=self.addVariable("int",0))
        self.IN["timeline"]= self._addElemt(name="Timeline",width=80,height=10,
                                              action=self.toggleSynchroTimeLine,type="checkbox",icon=None,
                                              variable=self.addVariable("int",0))
    def setupLayout(self):
        #this where we define the Layout
        #this wil make three button on a row
        self._layout = []
        self._layout.append([self.LOADFILE,self.LABELS["load"],self.CLOSEBTN])
        #Mesh options layout
        elemFrame1=[]
        elemFrame1.append([self.LABELS["curT"],self.PMENU["tetra"],])
        elemFrame1.append([self.LABELS["curP"],self.PMENU["properties"]])
        elemFrame1.append([self.BTN["build"]])
        elemFrame1.append([self.LABELS["min"],self.IN["cutoff"],self.LABELS["max"]])
        elemFrame1.append([self.LABELS["makeOff"],self.BTN["buildC"],self.IN["makeOff"]])
        elemFrame1.append([self.PMENU["comp"],self.BTN["color"]])
        elemFrame1.append([self.IN["interpolate"],self.LABELS["lengthInter"],self.IN["lengthInter"],])
        elemFrame1.append([self.BTN["loopcolor"],self.LABELS["nLoop"],self.IN["nLoop"],self.IN["timeline"]])
        frame1 = self._addLayout(name="Mesh options",elems=elemFrame1)
        self._layout.append(frame1)
        
    def loadGMV(self,filename):
        if not filename : return
        gmvname,ext=os.path.splitext(os.path.basename(filename))
#        if ext != ".gmv":
#            self.drawError("Sorry, the plugin required a file withj gmv extension\n")
#            return
        tetra = Tetra(name = gmvname,filename = filename,helper=self.helper)
        self.listeTetra[gmvname] = tetra
        self.listeTetraName.append(gmvname)
        self.currentTetra = tetra
        self.addItemToPMenu(self.PMENU["tetra"],str(gmvname))
        #need to update the color PMENU
        self.listeColors=[]
        key=None
        for key in tetra.ccolors :
            self.listeColors.append(key)
            self.addItemToPMenu(self.PMENU["properties"],str(key))
        for key in tetra.ncolors :
            self.listeColors.append(key)
            self.addItemToPMenu(self.PMENU["properties"],str(key))
        self.currentColor = key
        #create the mesh, need the split option? or later
        #tetra.createMesh()
        self.updateViewer()
        
    def browseGMV(self,*args):
        #first need to call the ui fileDialog
        self.fileDialog(label="choose a file",callback=self.loadGMV)
        return True

    def buildMesh(self,*args):
        #get curren tetra
        self.currentTetra.createMesh()
        name = self.currentTetra.name
        self.addItemToPMenu(self.PMENU["comp"],str(name))
        self.listeMesh.append(name)
        self.updateViewer()

    def buildPropertiesMesh(self,*args):
        cutoff=self.getReal(self.IN["cutoff"])
        key = self.listeColors[self.getLong(self.PMENU["properties"])]
        var = self.currentTetra.retrievePropertiesFromName(key)
        cellsOn, cellsOff = self.currentTetra.selectCells(var,cutoff)
        doCellOff = self.getBool(self.IN["makeOff"])
        #make selected cells
#        print len(cellsOn),len(self.currentTetra.cells)
        name = key+"_"+str(cutoff)+"_On"
        self.currentTetra.createMesh(name=name,cells=cellsOn)
        self.addItemToPMenu(self.PMENU["comp"],str(name))
        self.listeMesh.append(name)
        if doCellOff:
#            print doCellOff
            name = key+"_"+str(cutoff)+"_Off"
            self.currentTetra.createMesh(name=name,cells=cellsOff)
            self.addItemToPMenu(self.PMENU["comp"],str(name))
            self.listeMesh.append(name)
        self.updateViewer()

    def setCurTetra(self,*args):
        name = self.listeTetraName[self.getLong(self.PMENU["tetra"])]
        self.currentTetra = self.listeTetra[name]
        self.currentTetra.current_mesh = self.getVal(self.PMENU["comp"])
        #what else to do , update slider ? and other pulldown menu
        return True

    def setCurTetraProperties(self,*args):
        key = self.listeColors[self.getLong(self.PMENU["properties"])]
        var = self.currentTetra.retrievePropertiesFromName(key)
        mini = min(var)
        maxi = max(var)
        self.updateSlider(self.IN["cutoff"],mini,maxi,0.,1.)
        self.setString(self.LABELS["min"],str(mini))
        self.setString(self.LABELS["max"],str(maxi))
        if hasattr(self.currentTetra,"legend") and self.currentTetra.legend is not None:
            #update cmLegend
            self.currentTetra.legend.Set(mini=mini,maxi=maxi,visible=1)
        self.updateViewer()
        
    def setCurTetraColors(self,*args):
        tetra = self.currentTetra
        key = self.getVal(self.PMENU["properties"])#self.listeColors[self.getLong(self.PMENU["properties"])]
        name = self.getVal(self.PMENU["comp"])#self.listeMesh[self.getLong(self.PMENU["comp"])]
        self.current_mesh = self.getVal(self.PMENU["comp"])
        tetra.setMeshColor(name,key)
        self.updateViewer()

    def loopOverPropertiesColor(self,*args):
        #whats the list
        tetra = self.currentTetra
        name = self.getVal(self.PMENU["comp"])#self.listeMesh[self.getLong(self.PMENU["comp"])]
        self.current_mesh = self.getVal(self.PMENU["comp"])
        interpolate = self.getBool(self.IN["interpolate"])
        nbLoop = self.getLong(self.IN["nLoop"])
        nbInter = self.getLong(self.IN["lengthInter"])
        tetra.loopOverColor(name,nb=nbLoop,interpolate=interpolate,interpolateR=nbInter)

    def toggleSynchroTimeLine(self,*args):
        tetra = self.currentTetra
        name = self.getVal(self.PMENU["comp"])#self.listeMesh[self.getLong(self.PMENU["comp"])]
        tetra.current_mesh = self.getVal(self.PMENU["comp"])
        interpolate = self.getBool(self.IN["interpolate"])
        nbLoop = self.getLong(self.IN["nLoop"])
        nbInter = self.getLong(self.IN["lengthInter"])
        toggle = self.getBool(self.IN["timeline"])     
        cb = tetra.setColorPropertyInt
        if toggle :
            self.helper.synchronize(cb)
        else :
            self.helper.unsynchronize(cb)
            
        
if uiadaptor.host == "tk":
    import DejaVu
    DejaVu.enableVBO = True    
    from DejaVu import Viewer
    vi = Viewer()    
    #require a master   
    tetraui = TetraToolsGui(title= "Tetrahedron",master=vi)
    tetraui.setup(master=vi)
    #tetraui.helper.setViewer(vi)
else :
    tetraui = TetraToolsGui(title= "Tetrahedron")
    tetraui.setup()
#call it
tetraui.display()
#tetraui.loadGMV("/Users/ludo/DEV/upy/trunk/upy/examples/out_010.gmv")
tetraui.loadGMV("/Users/ludo/DEV/continuity/quads800")
tetraui.buildMesh()
lcolors=list(tetraui.currentTetra.ncolors.values())
#tetra = tetraui.currentTetrams=tetraui.currentTetra.mesh.values()[0][0]
#T=tetraui.currentTetra

#execfile("/Users/ludo/testTetraPanda.py")
#this is the command to loop over the different colors properties
#if the colors is not provide the script will loop over all properties associate to the mesh.
#tetra.loopOverColor("out_010",listeColors=lcolors,nb=10,interpolate=True,interpolateR=10)
#execfile("/Users/ludo/DEV/upy/examples/tetra.py")
