
"""
    Copyright (C) <2010>  Autin L. TSRI
    
    This file git_upy/cinema4d/r13/c4dHelper.py is part of upy.

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
Created on Sun Dec  5 23:30:44 2010

@author: Ludovic Autin - ludovic.autin@gmail.com
"""
#C4d module
import c4d
from c4d.utils.noise import C4DNoise
#standardmodule
import sys
import os
import struct
import string
import types
import math
from math import *
from types import StringType, ListType

#usenumpy = False
#try :
#    import numpy
#    usenumpy = True
#except :
#    usenumpy = False
#    print("no numpy")

#base helper class
from upy import hostHelper
#from upy.hostHelper import Helper
if hostHelper.usenumpy:
    import numpy

from upy.cinema4d.r12.c4dHelper import c4dHelper as Helper

class c4dHelper(Helper):
    """
    The cinema4d helper abstract class
    ============================
        This is the cinema4d helper Object. The helper 
        give access to the basic function need for create and edit a host 3d object and scene.
    """    
    #this id can probably found in c4d.symbols
    #TAG ID
    import c4d    
    POSEMIXER = 100001736
    POSEMORPH = 1024237
    IK = 1019561
    PYTAG = 1022749
    Follow_PATH = 5699
    LOOKATCAM = 1001001
    SUNTAG=5678
    DYNAMIC=180000102
    CONTRAINT = 1019364 #Tcaconstraint
    
    #OBJECT ID
    BONE = 1019362
    CYLINDER = 5170
    CONE = c4d.Ocone
    CIRCLE = 5181
    RECTANGLE = 5186
    FOURSIDE = 5180
    LOFTNURBS= 5107
    EXTRUDER = 5116
    SWEEPNURBS=5118
    TEXT = 5178
    CLONER = 1018544
    MOINSTANCE = 1018957
    ATOMARRAY = 1001002
    METABALLS = 5125
    LIGHT = 5102
    CAMERA = 5103
    SPRING = 180000010
    PATHDEFORM = 1019221
    PLATONIC = c4d.Oplatonic
    POLYGON = c4d.Opolygon
    MESH = c4d.Opolygon
    SPLINE = c4d.Ospline
    INSTANCE = c4d.Oinstance
    SPHERE = c4d.Osphere
    EMPTY = c4d.Onull
    BONES=1019362
    IK=1019362
    PARTICLES = 1001381
    #PARAMS ID
    PRIM_SPHERE_RAD = 1110
    
    #MATERIAL ATTRIB
    LAYER=1011123
    GRADIANT=1011100
    FUSION = 1011109
    
    #COMMAND ID 
    OPTIMIZE = 14039
    RECORD = 12410
    CONNECT = 12144
    CONNECT_DEL = 16768
    BIND = 1019881
    CREATEIKCHAIN = 1019884
    DESELECTALL = 12113
    SELCHILDREN = 16388
    FITTOVIEW = 430000774
    #need an axis dictionary
    
    #PARTICULE DATA DIC
    CH_DAT_TYPE={"Real":19,"String":130,"Int":15,"Object":400006009}
    
    #dic options
    CAM_OPTIONS = {"ortho" : 1,"persp" : 0}
    LIGHT_OPTIONS = {"Area" : 0,"Sun" : 3,"Spot":1}
    #type of light 0 :omni, 1:spot,2:squarespot,3:infinite,4:parralel,
    #5:parrallel spot,6:square parral spot 8:area
    
    #I can record pos/rot/scale and APA for selected object using this commands.
    VERBOSE=0
    DEBUG=0
    host = "c4d"
    
    def __init__(self,master=None,**kw):
        Helper.__init__(self)
        #we can define here some function alias
        self.updateAppli = self.update
        #some synonym,dejaVu compatilbity->should disappear later
        self.Cube = self.box
        self.Box = self.box
        self.Geom = self.newEmpty
        #self.getCurrentScene = c4d.documents.GetActiveDocument
        self.IndexedPolygons = self.polygons
        self.Points = self.PointCloudObject
        self.hext = "c4d"
        self.noise_type ={
              "boxNoise":c4d.NOISE_BOX_NOISE,
              "buya":c4d.NOISE_BUYA,
              "cellNoise":c4d.NOISE_CELL_NOISE,
              "cellVoronoi":c4d.NOISE_CELL_VORONOI,
              "cranal":c4d.NOISE_CRANAL,
              "dents":c4d.NOISE_DENTS,
              "displacedTurbulence":c4d.NOISE_DISPL_TURB,
              "electrico":c4d.NOISE_ELECTRIC,
              "fbm":c4d.NOISE_FBM,
              "fire":c4d.NOISE_FIRE,
              "gas":c4d.NOISE_GASEOUS,
              "hama":c4d.NOISE_HAMA,
              "luka":c4d.NOISE_LUKA,
              "modNoie":c4d.NOISE_MOD_NOISE,
              "naki":c4d.NOISE_NAKI,
              "noise":c4d.NOISE_NOISE,
              "none":c4d.NOISE_NONE,
              "nutous":c4d.NOISE_NUTOUS,
              "ober":c4d.NOISE_OBER,
              "pezo":c4d.NOISE_PEZO,
              "poxo":c4d.NOISE_POXO,
              "sema":c4d.NOISE_SEMA,
              "sparseConvolution":c4d.NOISE_SPARSE_CONV,
              "stupl":c4d.NOISE_STUPL,
              "turbulence":c4d.NOISE_TURBULENCE,
              "vlNoise":c4d.NOISE_VL_NOISE,
              "voronoi1":c4d.NOISE_VORONOI_1,
              "voronoi2":c4d.NOISE_VORONOI_2,
              "voronoi3":c4d.NOISE_VORONOI_3,
              "wavyTurbulence":c4d.NOISE_WAVY_TURB,
              "zada":c4d.NOISE_ZADA,       
             }


    def fit_view3D(self):
        c4d.CallCommand(self.FITTOVIEW)

    def progressBar(self,progress=None,label=None):
        """ update the progress bar status by progress value and label string
        @type  progress: Int/Float
        @param progress: the new progress
        @type  label: string
        @param label: the new message to put in the progress status
        NOT WORKING IN R13
        """        
        #the progessbar use the StatusSetBar
        if progress is not None :
            c4d.StatusSetBar(progress*100.)
        if label is not None :
            c4d.StatusSetText(label)
        if progress == 1.0 :
            self.resetProgressBar()
    
    def resetProgressBar(self,value=None):
        """reset the Progress Bar, using value"""
        c4d.StatusClear()
    
    def update(self):
        #getCurrentScene().GeSyncMessage(c4d.MULTIMSG_UP)     
        c4d.DrawViews(c4d.DRAWFLAGS_ONLY_ACTIVE_VIEW|c4d.DRAWFLAGS_NO_THREAD|c4d.DRAWFLAGS_NO_ANIMATION)          
        c4d.GeSyncMessage(c4d.EVMSG_TIMECHANGED)
        #c4d.DrawViews(c4d.DRAWFLAGS_NO_THREAD|c4d.DRAWFLAGS_FORCEFULLREDRAW)

    def setCurrentSelection(self,obj):
        #obj have  be c4d.object
        if obj is None :
            return
        if type (obj) is list or type (obj) is tuple :
            self.getCurrentScene().SetSelection(obj[0],c4d.SELECTION_NEW)            
            for o in obj[1:] :
                self.getCurrentScene().SetSelection(o,c4d.SELECTION_ADD)
        else :
            self.getCurrentScene().SetSelection(obj,c4d.SELECTION_NEW)
        self.update()
#        if type(obj) == c4d.BaseObject :
#            sc.SetSelection(listeObjects[0],c4d.SELECTION_NEW)
#            self.getCurrentScene().SetActiveObject(obj)

    def getCurrentSelection(self,):
        """
        Return the current/active selected object in the document or scene
    
        @rtype:   liste
        @return:  the list of selected object
        """        
        return self.getCurrentScene().GetSelection()

    def clearSelection(self,):
        c4d.CallCommand(self.DESELECTALL)

    def getType(self,object):
        if object is None : return None
        try :
            return object.GetType()
        except :
            return None



    def getBoundingBox(self,o,**kw):
        if o is None :
            return
        if type(o) is str:
            o = self.getObject(o)
        #if o is an instance the BB is 0,0,0
        o=self.getMesh(o)
        r= o.GetRad()#size on X,Y,and Z
        c= o.GetMp()*o.GetMg()
        bb1=c-r
        bb2=c+r
        return [self.ToVec(bb1),self.ToVec(bb2)]
                    
    def setName(self,o,name):
        if name is None :
            return
        if type(o) is str:
            o = self.getObject(o)
        o.SetName(name)
    
    def deleteObject(self,obj):
        sc = self.getCurrentScene()
        currentsel = self.getCurrentSelection()
        try :
            obj = self.getObject(obj)
            #print obj,obj.GetName()
            if obj is None :
                return
            sc.SetActiveObject(obj)
            c4d.CallCommand(100004787) #delete the obj
        except:
            print "problem deleting ", obj
        #restore the selection
        if currentsel:
            self.ObjectsSelection(currentsel,"new")
            
    def newEmpty(self,name,location=None,parentCenter=None,display=0,visible=0,**kw):
        empty=c4d.BaseObject(c4d.Onull)
        empty.SetName(name)
        empty[1000] = display
        empty[1001] = 1.0
        if location != None :
            if parentCenter != None : 
                location = location - parentCenter
            empty.SetAbsPos(self.FromVec(location))        
        parent = None
        if "parent" in kw :
            parent = kw["parent"]        
        self.addObjectToScene(self.getCurrentScene(),empty,parent=parent)
        return empty
    
#    def newInstance(self,name,object,location=None,c4dmatrice=None,matrice=None,
#                    parent = None,material=None,**kw):
#        instance = c4d.BaseObject(c4d.Oinstance)
#        instance[1001]=object       
#        instance.SetName(name)#.replace(":","_")
#        if c4dmatrice !=None :
#            #type of matre
#            instance.SetMg(c4dmatrice)
#        if matrice != None:
#            mx = self.matrix2c4dMat(matrice,transpose=True)
#            instance.SetMg(mx)
#        if location != None :
#            instance.SetAbsPos(self.FromVec(location))            
#        self.addObjectToScene(None,instance,parent=parent)
#        if material is not None:
#            self.assignMaterial(instance,material)
#        return instance

    def newClone(self,name,object,location=None,c4dmatrice=None,matrice=None,
                    parent = None,material=None,**kw):
        clone = object.GetClone()
        clone.SetName(name)#.replace(":","_")
        if c4dmatrice !=None :
            #type of matre
            clone.SetMg(c4dmatrice)
        if matrice != None:
            mx = self.matrix2c4dMat(matrice,transpose=True)
            clone.SetMg(mx)
        if location != None :
            clone.SetAbsPos(self.FromVec(location))            
        self.addObjectToScene(None,clone,parent=parent)
        if material is not None:
            self.assignMaterial(clone,material)
        return clone
     
    def setObjectMatrix(self,object,matrice=None,hostmatrice=None,
                        transpose=False,local=False,**kw):
        if hostmatrice !=None :
            #type of matre
            if local :
                object.SetMl(hostmatrice)
            else :
                object.SetMg(hostmatrice)
        else :
            mx = self.matrix2c4dMat(matrice,transpose=transpose)
            if local :
                object.SetMl(mx)
            else :
                object.SetMg(mx)
    
    def concatObjectMatrix(self,object,matrice,c4dmatrice=None,local=True):
        #local or global?
        cmg = object.GetMg()
        cml = object.GetMl()
        if c4dmatrice !=None :
            #type of matrice
            if local :
                object.SetMl(cml*c4dmatrice)
            else :
                object.SetMg(cmg*c4dmatrice)
        else :
            mx = self.matrix2c4dMat(matrice,transpose=False)
            if local :
                object.SetMl(cml*mx)
            else :
                object.SetMg(cmg*mx)

    def AddObject(self,ob,parent=None,centerRoot=True,rePos=None):
        if type(ob) is list:
            obj = ob[0]
        else :
            obj = ob
        doc = self.getCurrentScene()
        #doc.start_undo()
        if self.getObject(obj.GetName()) != None:
            return
        if parent != None : 
            if type(parent) == str : parent = self.getObject(parent)
            doc.InsertObject(obj,parent=parent)
            if centerRoot :
                currentPos = obj.GetAbsPos()         
                if rePos != None : 
                    parentPos = self.FromVec(rePos)          
                else :
                    parentPos = self.GetAbsPosUntilRoot(obj)#parent.GetAbsPos()                            
                obj.SetAbsPos(currentPos-parentPos)                
        else :    doc.InsertObject(obj)
        #add undo support
        #doc.add_undo(c4d.UNDO_NEW, obj)    
        #doc.end_undo()
    
    def makeHierarchy(self,listObj,listName, makeTagIK=False):
        for i,name in enumerate(listName) :
            o = self.getObject(listObj[name])
            if makeTagIK :
                o.MakeTag(IK)
            if i < len(listObj)-1 :
                child = self.getObject(listObj[listName[i+1]]) 
                child.InsertUnder(o)
    
    def addIKTag(self,object):
        object.MakeTag(IK)
        
    def addCameraToScene(self,name,Type='persp',focal=30.0,center=[0.,0.,0.],sc=None):
        if sc == None :
            sc = self.getCurrentScene()
        cam = c4d.BaseObject(self.CAMERA)
        cam.SetName(name)
        cam.SetAbsPos(self.FromVec(center))
        cam[1001] = self.CAM_OPTIONS[Type]#1 #0:perspective, 1 :parrallel
        cam[1000] = float(focal)  #parrallel zoom
        cam[1006] = 2*float(focal)#perspective focal
        #rotation?
        cam[904,1000] = pi/2.
        self.addObjectToScene(sc,cam,centerRoot=False)    
        return cam
        
    def addLampToScene(self,name,Type='Area',rgb=[1.,1.,1.],dist=25.0,energy=1.0,
                       soft=1.0,shadow=False,center=[0.,0.,0.],sc=None,**kw):
        #type of light 0 :omni, 1:spot,2:squarespot,3:infinite,4:parralel,
        #5:parrallel spot,6:square parral spot 8:area
        #light sun type is an infinite light with a sun tag type
        lamp = c4d.BaseObject(self.LIGHT)
        lamp.SetName(name)
        lamp.SetAbsPos(self.FromVec(center))
        lamp[c4d.ID_BASEOBJECT_REL_ROTATION, c4d.VECTOR_X] = pi/2.
        lamp[c4d.LIGHT_COLOR]= c4d.Vector(float(rgb[0]), float(rgb[1]), float(rgb[2]))#color
        lamp[c4d.LIGHT_BRIGHTNESS]= float(energy) #intensity
        lamp[c4d.LIGHT_TYPE]= self.LIGHT_OPTIONS[Type] #type
        if shadow : lamp[c4d.LIGHT_SHADOWTYPE]=1 #soft shadow map
        if Type == "Sun":
            suntag = lamp.MakeTag(self.SUNTAG)
        self.addObjectToScene(sc,lamp,centerRoot=False)    
        return lamp
            
    def setInstance(self,name,object,location=None,c4dmatrice=None,matrice=None):
        instance = c4d.BaseObject(c4d.Oinstance)
        instance[1001]=object        
        instance.SetName(name)#.replace(":","_")
        if location != None :
            instance.SetAbsPos(self.FromVec(location))
        if c4dmatrice !=None :
            #type of matre
            instance.SetMg(c4dmatrice)
        if matrice != None:
            mx = self.matrix2c4dMat(matrice)
            instance.SetMl(mx)
            p = instance.GetAbsPos()
            instance.SetAbsPos(c4d.Vector(p.y,p.z,p.x))
        return instance

    def getTranslation(self,name,absolue=True):
        obj = self.getObject(name)
        objdcache=obj.GetDeformCache()
        objcache=obj.GetCache()
        if objdcache is not None:
            if absolue : 
                m = objdcache.GetMg()
            else :
                m = objdcache.GetMl()
        elif objcache is not None:
            if absolue : 
                m = objcache.GetMg()
            else :
                m = objcache.GetMl()
#            print "trans cache ",m.off
        else :
            if absolue : 
                m = obj.GetMg()
            else :
                m = obj.GetMl()
        return m.off
#        return obj.GetAbsPos()

    def resetTransformation(self,name):
        obj = self.getObject(name)
        objdcache=obj.GetDeformCache()
        objcache=obj.GetCache()
        m = c4d.Matrix()
        if objdcache is not None:
            objdcache.SetMg(m)
        elif objcache is not None:
            objcache.SetMg(m)
        else :
            obj.SetMg(m)
        
    def getTransformation(self,name):
        obj = self.getObject(name)
        objdcache=obj.GetDeformCache()
        objcache=obj.GetCache()
        if objdcache is not None:
            m = objdcache.GetMg()
        elif objcache is not None:
            m = objcache.GetMg()
#            print "trans cache ",m.off
        else :
            m = obj.GetMg()
        return m

    def setTranslation(self,name,pos=[0.,0.,0.],absolue=True):
        if absolue : 
            self.getObject(name).SetAbsPos(self.FromVec(pos))
        else :
            self.getObject(name).SetRelPos(self.FromVec(pos))

    def translateObj(self,obj,position,use_parent=True):
        if len(position) == 1 : c = position[0]
        else : c = position
        #print "upadteObj"
        newPos=self.FromVec(c)
        if use_parent : 
            parentPos = self.GetAbsPosUntilRoot(obj)#parent.GetAbsPos()
            newPos = newPos - parentPos
            obj.SetAbsPos(newPos)
        else :
            pmx = obj.GetMg()
            mx = c4d.Matrix()
            mx.off = pmx.off + self.FromVec(position)
            obj.SetMg(mx)
    
    def scaleObj(self,obj,sc):
        if type(sc) is float :
            sc = [sc,sc,sc]
        obj.SetAbsScale(self.FromVec(sc))
    
#    def rotateObj(self,obj,rot):
#        #take radians, give degrees
#        obj[c4d.ID_BASEOBJECT_ROTATION, c4d.VECTOR_X]=float(rot[1]) #rotation about Y #H
#        obj[c4d.ID_BASEOBJECT_ROTATION, c4d.VECTOR_Y]=float(rot[2]) #rotation about X #P
#        obj[c4d.ID_BASEOBJECT_ROTATION, c4d.VECTOR_Z]=float(rot[0]) #rotation about Z #B


    def getSize(self,obj):
        #take degree
        obj = self.getObject(obj)
        if obj is None :
            return
        return obj[1100]

    def getScale(self,obj):
        return self.ToVec(self.getObject(obj).GetAbsScale())
 
    def toggleDisplay(self,obj,display,**kw):
        obj = self.getObject(obj)
        if obj is None :
            return
        if self.getType(obj) == self.PARTICLES :
            return
        if display : obj.SetEditorMode(c4d.MODE_UNDEF)
        else :     obj.SetEditorMode(c4d.MODE_OFF)            
        if display : obj.SetRenderMode(c4d.MODE_UNDEF)
        else :     obj.SetRenderMode(c4d.MODE_OFF)            
        if display : obj[906]=1
        else :     obj[906]=0

    def toggleXray(self,object,xray):
        obj = self.getObject(object)
        if obj is None :
            return
        obj[c4d.ID_BASEOBJECT_XRAY] = xray

    def getVisibility(self,obj,editor=True, render=False, active=False):
        #0 off, 1#on, 2 undef
        display = {0:True,1:False,2:True}
        if type (obj) == str :
            obj = self.getObject(obj)
        if editor and not render and not active:
            return display[obj.GetEditorMode()]
        elif not editor and render and not active:
            return display[obj.GetRenderMode()]
        elif not editor and not render and active:
            return bool(obj[906])
        else :
            return display[obj.GetEditorMode()],display[obj.GetRenderMode()],bool(obj[906])
    
    #####################MATERIALS FUNCTION########################
#    def addMaterial(self,name,color):
#          import c4d
#          import c4d.documents
#          doc = c4d.documents.GetActiveDocument()
#          # create standard material
#          __mat = doc.SearchMaterial(name) 
#          if __mat != None :
#              return __mat              
#          else :
#              __mat = c4d.BaseMaterial(c4d.Mmaterial)
#              # set the default color
#              __mat[2100] = c4d.Vector(float(color[0]),float(color[1]),float(color[2]))
#              __mat[c4d.ID_BASELIST_NAME] = name #900
#              # insert the material into the current document
#              doc.InsertMaterial(__mat)
#              return __mat
    
    def assignMaterial(self,object,mat,texture=False,**kw):
        if type(object) is list:
            m = mat
            mat = object[0]
            object = m
        if type(mat) is list :
            mat = mat[0]
        tag = object.GetTag(c4d.Ttexture)
        if tag is None:
            tag = object.MakeTag(c4d.Ttexture)
        #check the mat?
        if type(mat) is string:
            mat=self.getCurrentScene().SearchMaterial(mat)
        if mat is not None :
            tag[c4d.TEXTURETAG_MATERIAL] = mat
        if texture :
            tag[c4d.TEXTURETAG_PROJECTION]= 6
    
    def getMaterialObject(self,o):
        tags = o.GetTags()#[0]
        #havbe to be sure its Ttexture tag
        mat=[]
        for tag in tags :
            if tag.CheckType(c4d.Ttexture):
                mat.append(tag[c4d.TEXTURETAG_MATERIAL])
        return mat

    def getMaterial(self,mat):
        if type(mat) is str:
            return self.getCurrentScene().SearchMaterial(mat)
        else :
            return mat

    def getAllMaterials(self):
        return self.getCurrentScene().GetMaterials()
        
    def getMaterialName(self,mat):
        return mat[900]

    def createTexturedMaterial(self,name,filename):
        #create the material
        Mat = c4d.BaseMaterial(c4d.Mmaterial)
        Mat.SetName(name)
        #link the texture to the material
        text = c4d.BaseList2D(c4d.Xbitmap)
        text[c4d.BITMAPSHADER_FILENAME] = filename
        Mat[c4d.MATERIAL_COLOR_SHADER] = text
        Mat.InsertShader(text)
        Mat.Message(c4d.MSG_UPDATE)
        Mat.Update(True, True)
        c4d.EventAdd()
        c4d.documents.GetActiveDocument().InsertMaterial(Mat)
        return Mat

    def create_layers_material(self,name):
          import c4d
          import c4d.documents
          # create standard material
          __mat = c4d.BaseMaterial(c4d.Mmaterial)
          __mat[2100] = c4d.Vector(0.,0.,0.)
          __mat[900] = name
          __mat[8000]= c4d.BaseList2D(LAYER)
    
    def create_loft_material(self,doc=None,name='loft'):
          if doc == None : doc= c4d.documents.GetActiveDocument()
          #c4d.CallCommand(300000109,110)
          GradMat=doc.SearchMaterial('loft')
          if GradMat == None :
             #c4d.documents.load_file(plugDir+'/LoftGradientMaterial1.c4d')
             bd=c4d.documents.MergeDocument(doc,plugDir+'/LoftGradientMaterial1.c4d',
                                            loadflags=c4d.SCENEFILTER_MATERIALS|c4d.SCENEFILTER_MERGESCENE)   
             GradMat=doc.SearchMaterial('loft')
             #c4d.CallCommand(300000109,110)-> preset material n110 in the demo version
          #GradMat                          
          GradMat[2004]=0#refletion turn off
          GradMat[2003]=0#refletion turn off      
          GradMat[8000][1001]=2001 #type 2d-V
          mat=GradMat.GetClone()
          mat[900]=name
          #grad=mat[8000][1007]
          #grad.delete_all_knots()
          #mat[8000][1007]=grad
          doc.InsertMaterial(mat)                      
          #mat = create_gradiant_material(doc=doc,name=name)
          return mat 
    
    def create_gradiant_material(self,doc=None,name='grad'):
        if doc == None : doc= c4d.documents.GetActiveDocument()
        mat = c4d.BaseMaterial(c4d.Mmaterial)
        mat[900]=name
        #grad = c4d.Gradient()
        shader = c4d.BaseList2D(GRADIANT)
        mat[8000]= shader
        #mat[8000][1007] = grad
        mat[2004]=0#refletion turn off
        mat[2003]=0#refletion turn off      
        mat[8000][1001]=2001 #type 2d-V
        doc.InsertMaterial(mat) 
        return mat 
    
    def create_environment(self,type,**kw):
        Environment = c4d.BaseObject(c4d.Oenvironment)
        if type == "depthQ":
            Environment[c4d.ENVIRONMENT_AMBIENT] = self.FromVec((1.,1.,1.))
            Environment[c4d.ENVIRONMENT_AMBIENTSTRENGTH] = 1.0
            Environment[c4d.ENVIRONMENT_FOGENABLE] = 1
            Environment[c4d.ENVIRONMENT_FOG] = self.FromVec((1.,1.,1.))
            Environment[c4d.ENVIRONMENT_FOGSTRENGTH] = 1.0
            if kw.has_key('distance') :
                Environment[c4d.ENVIRONMENT_FOGDISTANCE] = kw['distance']
            Environment.SetName(type)
            self.AddObject(Environment)

    def updateRTSpline(self,spline,selectedPoint,distance = 2.0,
                       DistanceBumping = 1.85):
        #from Graham code 
        #print "before loop"
        nb_points = spline.GetPointCount()
        for j in xrange(selectedPoint,nb_points-1):
            leaderB = spline.GetPointAll(j)
            myPos = spline.GetPointAll(j+1)      
            deltaB = myPos-leaderB
            newPosB = leaderB + deltaB*distance/deltaB.len()
            newPosA = c4d.Vector(0.,0.,0.)
            k = j        
            while k >=0 :
                leaderA = spline.GetPointAll(k)
                deltaA = myPos-leaderA;
                if ( deltaA.len() <= DistanceBumping and deltaA.len() >0):
                            newPosA = ((DistanceBumping-deltaA.len())*deltaA/deltaA.len());
                newPos = newPosB + newPosA
                spline.SetPoint(j+1,newPos)
                k=k-1
        jC = selectedPoint;
        while jC >0 :
            leaderBC = spline.GetPointAll(jC);
            myPosC = spline.GetPointAll(jC-1);              
            deltaC = myPosC-leaderBC;
            newPosBC = leaderBC + deltaC*distance/deltaC.len();
            newPosAC = c4d.Vector(0.,0.0,0.)
            k = jC
            while k < nb_points :
                leaderAC = spline.GetPointAll(k)
                deltaAC = myPosC-leaderAC;
                if ( deltaAC.len() <= DistanceBumping and deltaAC.len() >0.):
                            newPosAC = ((DistanceBumping-deltaAC.len())*deltaAC/deltaAC.len());
                newPosC = newPosBC + newPosAC
                spline.SetPoint(jC-1,newPosC)
                k=k+1
            jC=jC-1
               
    def ObjectsSelection(self,listeObjects,typeSel="new"):
        """
        Modify the current object selection.
        
        @type  listeObjects: list
        @param listeObjects: list of object to joins
        @type  typeSel: string
        @param listeObjects: type of modification: new,add,...
    
        """    
        
        dic={"add":c4d.SELECTION_ADD,"new":c4d.SELECTION_NEW}
        sc = self.getCurrentScene()
        [sc.SetSelection(x,dic[typeSel]) for x in listeObjects]
    
    def JoinsObjects(self,listeObjects,delete=False):
        """
        Merge the given liste of object in one unique geometry.
        
        @type  listeObjects: list
        @param listeObjects: list of object to joins
        """    
#        print self.getName(listeObjects[-1])
#        print self.getName(listeObjects[0])
        self.clearSelection()
        sc = self.getCurrentScene()
        o=self.getObject(self.getName(listeObjects[-1])+".1")
        print "get ",o
        if o is not None :
            self.deleteObject(o)
        [self.makeEditable(o,copy=False) for o in listeObjects]
        sc.SetSelection(listeObjects[0],c4d.SELECTION_NEW)
        for i in range(1,len(listeObjects)):
#            ob = self.makeEditable(listeObjects[i],copy=False)
#            print listeObjects[i].GetName(),ob.GetName()
            sc.SetSelection(listeObjects[i],c4d.SELECTION_ADD)
            [sc.SetSelection(x,c4d.SELECTION_ADD) for x in self.getChilds(listeObjects[i])]
        c4d.CallCommand(self.SELCHILDREN)
        if delete:
            c4d.CallCommand(self.CONNECT_DEL)          
        else :
            c4d.CallCommand(self.CONNECT)
                

    def getCylinderAxis(self,cyl):
        #return the VECTOR_ indice
        listeAxis=[c4d.VECTOR_X,c4d.VECTOR_X,
                   c4d.VECTOR_Y,c4d.VECTOR_Y,
                   c4d.VECTOR_Z,c4d.VECTOR_Z]
        #cyl = self.getObject(cyl)
        if cyl is None :
            return c4d.VECTOR_Y
        if self.getType(cyl) == self.INSTANCE :
            cyl = cyl[c4d.INSTANCEOBJECT_LINK]
        if self.getType(cyl) != self.CYLINDER :
            cyl = cyl.GetDown()
            if self.getType(cyl) != self.CYLINDER :
                return c4d.VECTOR_Y
        return listeAxis[cyl[c4d.PRIM_AXIS]]

    def setCylinderAxis(self,cyl,axis=0):
#        listeAxis=[+x,-x,
#                   +y,-y
#                   +z,-z]
        cyl = self.getObject(cyl)
        if self.getType(cyl) == self.INSTANCE :
            cyl = cyl[c4d.INSTANCEOBJECT_LINK]
        if self.getType(cyl) != self.CYLINDER :
            cyl = cyl.GetDown()
            if self.getType(cyl) != self.CYLINDER :
                return
        cyl[c4d.PRIM_AXIS] = axis

    def oneCylinder(self,name,head,tail,radius=None,instance=None,material=None,
                    parent = None,color=None):
        laenge,mx=self.getTubeProperties(head,tail)
        if instance is None:
            stick = self.Cylinder(name,parent=parent)[0]
        else :
            stick = c4d.BaseObject(c4d.Oinstance)
            stick[c4d.INSTANCEOBJECT_LINK]=instance
            stick.SetName(name)
            self.addObjectToScene(self.getCurrentScene(),stick,parent=parent)
        stick.SetMg(mx)
        axe = self.getCylinderAxis(stick)
        if  radius != None :
            stick[c4d.ID_BASEOBJECT_REL_SCALE]= c4d.Vector(float(radius),
                                                    float(radius),float(radius))
        stick[c4d.ID_BASEOBJECT_REL_SCALE,axe]=float(laenge)#should scale the axis instead .scale Y
        texture=stick.MakeTag(c4d.Ttexture)
        if material is not None :
            texture[1010]=material
        elif color is not None :
            mat = texture[1010]
            if mat is None :
                mat = self.addMaterial("mat_"+name,color)
                texture[1010] = mat
            else :
                self.colorMaterial(mat,color)
        return stick

    def updateOneCylinder(self,name,head,tail,radius=None,material=None,color=None):
        laenge,mx=self.getTubeProperties(head,tail)
        stick = self.getObject(name)
        stick.SetMg(mx)
        axe = self.getCylinderAxis(stick)
        if  radius != None :
            stick[c4d.ID_BASEOBJECT_REL_SCALE]= c4d.Vector(float(radius),
                                                    float(radius),float(radius))
        stick[c4d.ID_BASEOBJECT_REL_SCALE,axe]=float(laenge)#should scale the axis instead .scale Y
        texture = stick.GetTag(c4d.Ttexture)
        if material == None and color is not None: 
            material = self.addMaterial("mat"+name,color)
        if color is not None :
            self.colorMaterial(material,color)
        if material is not None :
            texture[1010] = material
        return stick

    def Cone(self,name,radius=1.,length=1.,res=9, pos = [0.,0.,0.],parent=None,**kw):
        baseCone = c4d.BaseObject(self.CONE)
        baseCone.SetName(name)
        baseCone[c4d.PRIM_CONE_TRAD] = 0.
        baseCone[c4d.PRIM_CONE_BRAD] = radius
        baseCone[c4d.PRIM_CONE_HEIGHT] = length
        baseCone[c4d.PRIM_CONE_HSUB] = int(res)
        baseCone[c4d.PRIM_CONE_SEG] = int(3*res)
        if "axis" in kw : #orientation
            dic = {"+X":0,"-X":1,"+Y":2,"-Y":3,"+Z":4,"-Z":5}
            if type(kw["axis"]) is str :
                axis = dic[kw["axis"]]
            else : 
                axis = kw["axis"]
            baseCone[c4d.PRIM_AXIS]=axis
        else :
            baseCone[c4d.PRIM_AXIS]=1
        #else :
        #    baseCyl[c4d.PRIM_CYLINDER_SEG] = QualitySph[str(res)]
        #sy.PRIM_CYLINDER_HSUB
        baseCone.SetAbsPos(self.FromVec(pos))
        baseCone.MakeTag(c4d.Tphong)
        #addObjectToScene(getCurrentScene(),baseCyl)
        self.addObjectToScene(self.getCurrentScene(),baseCone,parent=parent)
        return baseCone,baseCone
                          
#    def updateSphereMesh(self,mesh,verts=None,faces=None,basemesh=None,
#                         scale=1.):
#        mesh=self.getMesh(mesh)
##        print mesh,mesh.GetName(),scale
##        print mesh[905]
#        mesh[905]=self.FromVec([scale,scale,scale])
#        mesh.Message(c4d.MSG_UPDATE)
        
#    def updateSphereObj(self,obj,coord):
#        self.updateObjectPos(obj,coord)
#    
#    def updateObjectPos(self,object,position):
#        if len(position) == 1 : c = position[0]
#        else : c = position
#        #print "upadteObj"
#        newPos=self.FromVec(c)
#        parentPos = self.GetAbsPosUntilRoot(object)#parent.GetAbsPos()
#        object.SetAbsPos(newPos-parentPos)
    
#    def clonesAtomsSphere(self,name,x,iMe,doc,mat=None,scale=1.0,
#                          Res=32,R=None,join=0):
#        spher=[]
#        k=0
#        n='S'
#        AtmRadi = {"A":1.7,"N":1.54,"C":1.7,"P":1.7,"O":1.52,"S":1.85,"H":1.2}
#        
#        if scale == 0.0 : scale = 1.0
#        if mat == None : mat=create_Atoms_materials()
#        if name.find('balls') != (-1) : n='B'
#        for j in range(len(x)): spher.append(None)
#        for j in range(len(x)):
#            #at=res.atoms[j]
#            at=x[j]
#            atN=at.name
#            #print atN
#            fullname = at.full_name()
#            #print fullname
#            atC=at._coords[0]
#            spher[j] = iMe[atN[0]].GetClone()
#            spher[j].SetName(n+"_"+fullname)#.replace(":","_"))
#            spher[j].SetAbsPos(c4d.Vector(float(atC[2]),float(atC[1]),float(atC[0])))
#            spher[j][905]=c4d.Vector(float(scale),float(scale),float(scale))
#            #
#            #print atN[0]
#            #print mat[atN[0]]    
#            texture = spher[j].MakeTag(c4d.Ttexture)
#            texture[1010] = mat[atN[0]]
#            k=k+1
#        return spher
        
#    def instancesSphere(self,name,centers,radii,meshsphere,
#                        colors,scene,parent=None):
#        sphs=[]
#        mat = None
#        if len(colors) == 1:
#            mat = self.retrieveColorMat(colors[0])
#            if mat == None and colors[0] is not None:        
#                mat = self.addMaterial('mat_'+name,colors[0])
#        for i in range(len(centers)):
#            sphs.append(c4d.BaseObject(c4d.Oinstance))
#            sphs[i][1001]=meshsphere
#            sphs[i].SetName(name+str(i))        
#            sphs[i].SetAbsPos(self.FromVec(centers[i]))
#            #sphs[i].SetAbsPos(c4d.Vector(float(centers[i][0]),float(centers[i][1]),float(centers[i][2])))
#            if len(radii) == 1 :
#                rad = radii[0]
#            elif i >= len(radii) :
#                rad = radii[0]
#            else :
#                rad = radii[i]
#            sphs[i][905]=c4d.Vector(float(rad),float(rad),float(rad))
#            texture = sphs[i].MakeTag(c4d.Ttexture)
#            if mat == None :
#                if colors is not None and  i < len(colors) and colors[i] is not None :
#                    mat = self.addMaterial("matsp"+str(i),colors[i])
#            texture[1010] = mat#mat[bl.retrieveColorName(sphColors[i])]
#            self.addObjectToScene(scene,sphs[i],parent=parent)
#        return sphs
#
#    def updateInstancesSphere(self,name,sphs,centers,radii,meshsphere,
#                        colors,scene,parent=None,delete=True,**kw):
#        mat = None
#        if len(colors) == 1:
#            mat = self.retrieveColorMat(colors[0])
#            if mat == None and colors[0] is not None:        
#                mat = self.addMaterial('mat_'+name,colors[0])
#        delete = True
#        if "delete" in kw :
#            delete = kw["delete"]
#        for i in range(len(centers)):
#            if len(radii) == 1 :
#                rad = radii[0]
#            elif i >= len(radii) :
#                rad = radii[0]
#            else :
#                rad = radii[i]            
#            if i < len(sphs):
#                sphs[i].SetAbsPos(self.FromVec(centers[i]))
#                sphs[i][905]=c4d.Vector(float(rad),float(rad),float(rad))
#                texture = sphs[i].GetTag(c4d.Ttexture)
#                if mat == None : 
#                    if colors is not None and i < len(colors) and colors[i] is not None : 
#                        mat = self.addMaterial("matsp"+str(i),colors[i])
#                if colors is not None and i < len(colors) and colors[i] is not None : 
#                    self.colorMaterial(mat,colors[i])
#                texture[1010] = mat
#                self.toggleDisplay(sphs[i],True)
#            else :
#                sphs.append(c4d.BaseObject(c4d.Oinstance))
#                sphs[i][1001]=meshsphere
#                sphs[i].SetName(name+str(i))
#                sphs[i].SetAbsPos(self.FromVec(centers[i]))
#                sphs[i][905]=c4d.Vector(float(rad),float(rad),float(rad))
#                texture = sphs[i].MakeTag(c4d.Ttexture)
#                if mat == None :
#                    if colors is not None and  i < len(colors) and colors[i] is not None : 
#                        mat = self.addMaterial("matsp"+str(i),colors[i])
#                texture[1010] = mat#mat[bl.retrieveColorName(sphColors[i])]
#                self.addObjectToScene(scene,sphs[i],parent=parent)
#        if len(centers) < len(sphs) and delete :
#            #delete the other ones ?
#            for i in range(len(centers),len(sphs)):
#                if delete : 
#                    obj = sphs.pop(i)
#                    print "delete",obj
#                    self.deleteObject(obj)
#                else :
#                    self.toggleDisplay(sphs[i],False)
#        return sphs
#        
#                                    
#    def spheresMesh(self,name,x,mat=None,scale=1.0,Res=32,R=None,join=0):
#        if scale == 0.0 : scale =1.
#        scale = scale *2.
#        spher=[]
#        if Res == 0 : Res = 10.
#        else : Res = Res *5.
#        k=0
#        if mat == None : mat=self.create_Atoms_materials()
#        #print len(x)
#        for j in range(len(x)): spher.append(None)
#        for j in range(len(x)):
#            #at=res.atoms[j]
#            at=x[j]
#            atN=at.name
#            #print atN
#            fullname = at.full_name()
#            #print fullname
#            atC=at._coords[0]
#            #if R !=None : rad=R
#            #elif AtmRadi.has_key(atN[0]) : rad=AtmRadi[atN[0]]
#            #else : rad=AtmRadi['H']
#            #print  at.vdwRadius
#            rad=at.vdwRadius
#            #print rad
#            spher[j] = c4d.BaseObject(c4d.Osphere)
#            spher[j].SetName(fullname.replace(":","_"))
#            spher[j][PRIM_SPHERE_RAD] = float(rad)*float(scale)
#            spher[j].SetAbsPos(c4d.Vector(float(atC[0]),float(atC[1]),float(atC[2])))
#            spher[j].MakeTag(c4d.Tphong)
#            # create a texture tag on the PDBgeometry object
#            #texture = spher[j].MakeTag(c4d.Ttexture)
#            #create the dedicayed material
#            #print mat[atN[0]]
#            #texture[1010] = mat[atN[0]]
#            #spher.append(me)
#        k=k+1
#        return spher

    def getTubeProperties(self,coord1,coord2):
        #need ot overwrite in C4D
#        print coord1,coord1[0],type(coord1[0])
        coord1 = self.ToVec(coord1)
        coord2 = self.ToVec(coord2)
        x1 = float(coord1[0])
        y1 = float(coord1[1])
        z1 = float(coord1[2])
        x2 = float(coord2[0])
        y2 = float(coord2[1])
        z2 = float(coord2[2])
        laenge = math.sqrt((x1-x2)*(x1-x2)+(y1-y2)*(y1-y2)+(z1-z2)*(z1-z2))
        wsz = atan2((y1-y2), (z1-z2))
        wz = acos((x1-x2)/laenge)
        offset=c4d.Vector(float(z1+z2)/2,float(y1+y2)/2,float(x1+x2)/2)
        v_2=c4d.Vector(float(z1-z2),float(y1-y2),float(x1-x2))
        v_2.Normalize()
        v_1=c4d.Vector(float(1.),float(0.),float(2.))
        v_3=c4d.Vector.Cross(v_1,v_2)
        v_3.Normalize()
        v_1=c4d.Vector.Cross(v_2,v_3)
        v_1.Normalize()
        mx=c4d.Matrix(offset,v_1, v_2, v_3)
        return laenge,mx
    
    def updateTubeMesh(self,mesh,cradius=1.0,quality=0,**kw):
        #change the radius to cradius
        mesh=self.getMesh(mesh)
        print mesh.GetName(),cradius
#        mesh=geom.mesh.GetDown()#should be the cylinder
        #mesh[5000]=cradius
#        cradius = cradius*1/0.2
        #should used current Y scale too
        axe = self.getCylinderAxis(mesh) #principal axis
        back = mesh[905]
#        mesh[905]=mesh[905]^c4d.Vector(float(cradius),1.,float(cradius))
        mesh[905]=c4d.Vector(float(cradius),float(cradius),float(cradius))
        #restore length
        if axe is c4d.VECTOR_X :
            mesh[905,axe] = back.x
        elif axe is c4d.VECTOR_Y :
            mesh[905,axe] = back.y
        elif axe is c4d.VECTOR_Z :
            mesh[905,axe] = back.z
        mesh.Message(c4d.MSG_UPDATE)
        #pass
      
#    def updateTubeObj(self,*args,**kw):#obj,coord1,coord2,bicyl=False):
#        #if self.DEBUG :
#        #print "updateTubeObj", args
#        o = args[0]
#        coord1 = args[1]
#        coord2 = args[2]        
#        laenge,mx=self.getTubeProperties(coord1,coord2)
#        o.SetMl(mx)
#        o[905,1001]=float(laenge)
#        parentPos = self.GetAbsPosUntilRoot(o)#parent.GetAbsPos()
#        currentPos = o.GetAbsPos()
#        o.SetAbsPos(currentPos - parentPos)      
        
#    def oldTube(set,atms,points,faces,doc,mat=None,res=32,size=0.25,sc=1.,join=0,instance=None,hiera = 'perRes'):
#     bonds, atnobnd = set.bonds
#     backbone = ['N', 'CA', 'C', 'O']
#     stick=[]
#     tube=[]
#     #size=size*2.
#     #coord1=x[0].atms[x[0].atms.CApos()].xyz() #x.xyz()[i].split()
#     #coord2=x[1].atms[x[1].atms.CApos()].xyz() #x.xyz()[i+1].split()
#     #print len(points)
#     #print len(faces)
#     #print len(atms)
#     atm1=bonds[0].atom1#[faces[0][0]]
#     atm2=bonds[0].atom2#[faces[0][1]]
#     #name="T_"+atm1.name+str(atm1.number)+"_"+atm2.name+str(atm2.number) 
#     name="T_"+atm1.full_name()+"_"+atm2.name
#     mol=atm1.getParentOfType(Protein)
#     laenge,mx=getStickProperties(points[faces[0][0]],points[faces[0][1]]) 
#     if mat == None : mat=create_sticks_materials()
#     if instance == None :
#         stick.append(c4d.BaseObject(CYLINDER))#(res, size, laenge/sc) #1. CAtrace, 0.25 regular |sc=1 CATrace, 2 regular
#         stick[0].SetMg(mx)
#         stick[0][5005]=laenge/sc#size
#         stick[0][5000]=size#radius
#         stick[0][5008]=res#resolution
#         stick[0][5006]=2#heght segment
#     else :
#         stick.append(c4d.BaseObject(INSTANCE))
#         stick[0][1001]=instance
#         stick[0].SetMg(mx)     
#         stick[0][905,1001]=float(laenge)
#     texture=stick[0].MakeTag(c4d.Ttexture)
#     #print  atms[faces[0][0]].name[0]+atms[faces[0][1]].name[0]
#     name1=atms[faces[0][0]].name[0]
#     name2=atms[faces[0][1]].name[0]
#     if name1 not in AtmRadi.keys(): name1="A"
#     if name2 not in AtmRadi.keys(): name2="A"
#     texture[1010]=mat[name1+name2]              
#     stick[0].SetName(name)
#     #stick[0].SetAbsPos(c4d.Vector(float(z1+z2)/2,float(y1+y2)/2,float(x1+x2)/2))
#     #stick[0].set_rot(c4d.Vector(float(wz),float(0),float(wsz)))
#     #stick[0][904,1000] = wz #RY/RH
#     #stick[0][904,1002] = wsz #RZ/RB
#     stick[0].MakeTag(c4d.Tphong)
#     hierarchy=parseObjectName("B_"+atm1.full_name())
#     #parent=getObject(mol.geomContainer.masterGeom.chains_obj[hierarchy[1]+"_balls"])
#     if hiera == 'perRes' :
#         parent = getObject(mol.geomContainer.masterGeom.res_obj[hierarchy[2]])
#     elif hiera == 'perAtom' :
#         if atm1.name in backbone : 
#             parent = getObject(atm1.full_name()+"_bond")
#         else :
#             parent = getObject(atm1.full_name()+"_sbond")
#     else :
#         parent=getObject(mol.geomContainer.masterGeom.chains_obj[hierarchy[1]+"_balls"])
#     addObjectToScene(doc,stick[0],parent=parent)
#     for i in range(1,len(faces)):
#      atm1=bonds[i].atom1#[faces[i][0]]
#      atm2=bonds[i].atom2#[faces[i][1]]
#      #name="T_"+atm1.name+str(atm1.number)+"_"+atm2.name+str(atm2.number)
#      name="T_"+atm1.full_name()+"_"+atm2.name
#      laenge,mx=getStickProperties(points[faces[i][0]],points[faces[i][1]])
#      if instance == None :
#         stick.append(c4d.BaseObject(CYLINDER))#(res, size, laenge/sc) #1. CAtrace, 0.25 regular |sc=1 CATrace, 2 regular
#         stick[i].SetMl(mx)
#         stick[i][5005]=laenge/sc#radius
#         stick[i][5000]=size#height/size
#         stick[i][5008]=res#resolution rotation segment
#         stick[i][5006]=2#heght segment     
#      else :
#         stick.append(c4d.BaseObject(INSTANCE))
#         stick[i][1001]=instance
#         stick[i].SetMl(mx)
#         stick[i][905,1001]=float(laenge)
#      texture=stick[i].MakeTag(c4d.Ttexture)
#      #print i,i+1
#      name1=atms[faces[i][0]].name[0]
#      name2=atms[faces[i][1]].name[0]
#      if name1 not in AtmRadi.keys(): name1="A"
#      if name2 not in AtmRadi.keys(): name2="A"
#    
#      if i < len(atms) :
#         #print  name1+name2
#         texture[1010]=mat[name1+name2]
#      else :
#         texture[1010]=mat[name1+name2]                                 
#      stick[i].SetName(name)
#      #stick[i].SetAbsPos(c4d.Vector(float(z1+z2)/2,float(y1+y2)/2,float(x1+x2)/2))
#      #stick[i].set_rot(c4d.Vector(float(wz),float(0.),float(wsz)))
#      stick[i].SetMl(mx)
#      stick[i].MakeTag(c4d.Tphong)
#      hierarchy=parseObjectName("B_"+atm1.full_name())
#      #parent=getObject(mol.geomContainer.masterGeom.chains_obj[hierarchy[1]+"_balls"])
#      if hiera == 'perRes' :
#         parent = getObject(mol.geomContainer.masterGeom.res_obj[hierarchy[2]])
#      elif hiera == 'perAtom' :
#         if atm1.name in backbone : 
#             parent = getObject(atm1.full_name()+"_bond")
#         else :
#             parent = getObject(atm1.full_name()+"_sbond")
#      else :
#         parent=getObject(mol.geomContainer.masterGeom.chains_obj[hierarchy[1]+"_balls"])
#    
#      addObjectToScene(doc,stick[i],parent=parent)
#    
#     #if join==1 : 
#     #    stick[0].join(stick[1:])
#     #    for ind in range(1,len(stick)):
#            #obj[0].join([obj[ind]])
#    #        scn.unlink(stick[ind])
#        #obj[0].setName(name)
#     return [stick]
#    
#  

    def FromFace(self,f):
        A = int(f[0])
        B = int(f[1])
        if len(f)==2 :
            C = B
            D = B
            return c4d.CPolygon( C, B, A)
        elif len(f)==3 : 
            C = int(f[2])
            D = C
            return c4d.CPolygon( C, B, A)
        elif len(f)==4 : 
            C = int(f[2])
            D = int(f[3])
            return c4d.CPolygon( D,C, B, A)

    def FromVec(self,points,pos=True):
        if type(points) == c4d.Vector:
            return points
        if not pos :
            return c4d.Vector(float(points[0]),float(points[1]),float(points[2]))
        else :
            return c4d.Vector(float(points[2]),float(points[1]),float(points[0]))
        #return c4d.Vector(float(points[0]),float(points[1]),float(points[2]))
    
    def ToVec(self,v,pos=True):
        if type(v) != c4d.Vector:
            return v
        if not pos :
            return [v.x,v.y,v.z]
        else:
            return [v.z,v.y,v.x]
        
    def getCoordinateMatrix(self,pos,direction):
      offset=pos
      v_2=direction
      v_2.Normalize()
      v_1=c4d.Vector(float(1.),float(0.),float(0.))
      v_3=c4d.Vector.Cross(v_1,v_2)
      v_3.Normalize()
      v_1=c4d.Vector.Cross(v_2,v_3)
      v_1.Normalize()
     #from mglutil.math import rotax
     #pmx=rotax.rotVectToVect([1.,0.,0.], [float(z1-z2),float(y1-y2),float(x1-x2)], i=None)
      return c4d.Matrix(offset,v_1, v_2, v_3)
    
    def getCoordinateMatrixBis(self,pos,v1,v2):
      offset=self.FromVec(pos)
      v_2=self.FromVec(v2)
      v_1=self.FromVec(v1)
      v_3=c4d.Vector.Cross(v_1,v_2)
      v_3.Normalize()
     #from mglutil.math import rotax
     #pmx=rotax.rotVectToVect([1.,0.,0.], [float(z1-z2),float(y1-y2),float(x1-x2)], i=None)
      return c4d.Matrix(offset,v_1, v_2, v_3)
    
    def loftnurbs(self,name,mat=None):
        loft=c4d.BaseObject(self.LOFTNURBS)
        loft[1008]=0 #adaptive UV false
        loft.SetName(name)
        loft.MakeTag(c4d.Tphong)
        texture = loft.MakeTag(c4d.Ttexture)
        texture[1004]=6 #UVW Mapping
        #create the dedicayed material
        if mat is not None : 
            texture[1010] = mat
        return loft

#    def sweepnurbs(self,name,mat=None,parent=None):
#        loft=c4d.BaseObject(c4d.Osweep)
#        loft.SetName(name)
#        loft.MakeTag(c4d.Tphong)
#        #create the dedicayed material
##        if mat == None : 
##                texture[1010] = self.create_loft_material(name='mat_'+name)
##        else : texture[1010] = mat
#        self.addObjectToScene(None,loft,parent=parent)
#        if mat is not None : 
#            texture = loft.MakeTag(c4d.Ttexture)
#            texture[1010] = mat
#        return loft
    
    def addShapeToNurb(self,loft,shape,position=-1):
        list_shape=loft.GetChilds()
        shape.insert_after(list_shape[position])
    
    #def createShapes2D()
    #    sh=c4d.BaseObject(dshape)
    
#    def extrudeSpline(self,spline,**kw):
#        extruder = None
#        shape = None
#        spline_clone = None
#        if "extruder" in kw:
#            extruder = kw["extruder"]
#        if extruder is None :
#            extruder=self.sweepnurbs("ex_"+spline.GetName())
#        if "shape" in kw:
#            if type(kw["shape"]) == str :
#                shape = self.build_2dshape("sh_"+kw["shape"]+"_"+spline.GetName(),
#                                           kw["shape"])
#            else :
#                shape = kw["shape"]
#        if shape is None :
#            shape = self.build_2dshape("sh_circle"+spline.GetName())
#        if "clone" in kw and kw["clone"] :
#            spline_clone = spline.GetClone()
#            self.resetTransformation(spline_clone)
#            self.reParent(spline_clone,extruder)
#        else :
#            self.reParent(spline,extruder)
#        self.reParent(shape,extruder)          
#        if spline_clone is not None :
#            return extruder,shape,spline_clone
#        return extruder,shape
        
    def spline(self,name, points,close=0,type=1,extrude_obj=None,
                               scene=None,parent=None):
        spline=c4d.BaseObject(c4d.Ospline)
        spline[1000]=type
        spline[1002]=close
        spline.SetName(name)
        spline.ResizeObject(int(len(points)))
        for i,p in enumerate(points):
            spline.SetPoint(i, self.FromVec(p))
        self.addObjectToScene(scene,spline,parent=parent)            
        if extrude_obj is not None :
            extruder=self.helper.sweepnurbs(name)
            self.reParent(spline,nurb)
            self.reParent(extrude_obj,nurb)            
            return spline,spline,extruder
        return spline,spline
    
    def update_spline(self,name,new_points):
        spline=self.getObject(name)
        if spline is None : 
            return False
        spline.ResizeObject(int(len(new_points)))
        for i,p in enumerate(new_points):
            spline.SetPoint(i, self.FromVec(p))
        spline.Message(c4d.MSG_UPDATE)
        return True
    
#    def build_2dshape(self,name,type="circle",**kw):
#        shapedic = {"circle":{"obj":self.CIRCLE,"size":[c4d.PRIM_CIRCLE_RADIUS,]},
#                    "rectangle":{"obj":self.RECTANGLE,
#                    "size":[c4d.PRIM_RECTANGLE_WIDTH,c4d.PRIM_RECTANGLE_HEIGHT]}
#                    }
#        shape = c4d.BaseObject(shapedic[type]["obj"])
#        shape[c4d.PRIM_PLANE]=0#0 XY, 1 ZY, 2 XZ
#        dopts = [1.,1.]
#        if "opts" in kw :
#            dopts = kw["opts"]
#        if len(shapedic[type]["size"]) == 1 :
#            shape[shapedic[type]["size"][0]] = dopts[0]
#        else :
#            for i in range(len(shapedic[type]["size"])) :
#                shape[shapedic[type]["size"][i]] = dopts[i]
#        self.addObjectToScene(None,shape)
#        return shape
#        
    def createShapes2Dspline(self,doc=None,parent=None):
        circle=c4d.BaseObject(self.CIRCLE)
        circle[2012]=float(0.3)
        circle[2300]=1
        if doc : addObjectToScene(doc,circle,parent=parent )
        rectangle=c4d.BaseObject(self.RECTANGLE)
        rectangle[2060]=float(2.2)
        rectangle[2061]=float(0.7)
        rectangle[2300]=1
        if doc : addObjectToScene(doc,rectangle,parent=parent )
        fourside=c4d.BaseObject(self.FOURSIDE)
        fourside[2121]=float(2.5)
        fourside[2122]=float(0.9)
        fourside[2300]=1
        if doc : addObjectToScene(doc,fourside,parent=parent )
        shape2D={}
        pts=[[0,0,0],[0,1,0],[0,1,1],[0,0,1]]
        #helixshape
        helixshape=fourside.get_real_spline()#spline('helix',pts,close=1,type=2)#AKIMA
        helixshape.SetName('helix')
        shape2D['Heli']=helixshape
        #sheetshape
        sheetshape=rectangle.get_real_spline()#spline('sheet',pts,close=1,type=0)#LINEAR
        sheetshape.SetName('sheet')
        shape2D['Shee']=sheetshape
        #strandshape
        strandshape=sheetshape.GetClone()
        strandshape.SetName('strand')
        shape2D['Stra']=strandshape
        #coilshape
        coilshape=circle.get_real_spline()#spline('coil',pts,close=1,type=4)#BEZIER
        coilshape.SetName('coil')
        shape2D['Coil']=coilshape
        #turnshape
        turnshape=coilshape.GetClone()
        turnshape.SetName('turn')
        shape2D['Turn']=turnshape
        if doc : 
            for o in shape2D.values() :
                self.addObjectToScene(doc,o,parent=parent )    
        return shape2D,[circle,rectangle,fourside,helixshape,sheetshape,strandshape,coilshape,turnshape]


    def constraintLookAt(self,object):
        """
        Cosntraint an hostobject to llok at the camera
        
        @type  object: Hostobject
        @param object: object to constraint
        """
        self.getObject(object)
        object.MakeTag(self.LOOKATCAM)

    def updateText(self,text,string="",parent=None,size=None,pos=None,font=None,
                   absolue=True):
        text = self.getObject(text)
        if text is None :
            return
        if string : text[c4d.PRIM_TEXT_TEXT] = string
        if size is not None :  text[c4d.PRIM_TEXT_HEIGHT]= size
        if pos is not None : self.setTranslation(text,pos,absolue=absolue)
        if parent is not None : self.reParent(text,parent)
        
    def Text(self,name="",string="",parent=None,size=5.,pos=None,font=None,lookAt=False,
                 absolue=True,**kw):
        #extrude options here ?
        return_extruder = False
        text = c4d.BaseObject(self.TEXT)
        text.SetName(name)
        text[c4d.PRIM_TEXT_TEXT] = string        #Text
        text[c4d.PRIM_TEXT_HEIGHT]= size
        #text[c4d.ID_BASEOBJECT_REL_ROTATION,c4d.VECTOR_X] = 3.14      #inverse
        text[c4d.PRIM_PLANE] = 1 #ZY
#        if font is not None:
#            text[c4d.PRIM_TEXT_FONT]
        if pos is not None :
            self.setTranslation(text,pos,absolue=absolue)
#        if parent is not None:
        if lookAt:
            self.constraintLookAt(text)
        if "extrude" in kw :
            extruder = None
            #create an extruder
            if type(kw["extrude"]) is bool and kw["extrude"]:
                extruder = c4d.BaseObject(self.EXTRUDER)
                self.addObjectToScene(self.getCurrentScene(),extruder,parent=parent)
                return_extruder = True
            else :
                extruder = kw["extrude"]
            if extruder is not None :
                extruder[c4d.EXTRUDEOBJECT_MOVE] = self.FromVec([0.0,0.,0.5]) # if x 180.0
                extruder[c4d.EXTRUDEOBJECT_HIERARCHIC] = 1
                parent = extruder
        self.addObjectToScene(self.getCurrentScene(),text,parent=parent)            
        if return_extruder :
            return text,extruder
        else :
            return text

    def createShapes2D(self,doc=None,parent=None):
        if doc is None :
            doc = self.getCurrentScene()    
        shape2D={}
        circle=c4d.BaseObject(self.CIRCLE)
        circle[2012]=float(0.3)
        circle[2300]=0
        circle.SetName('Circle1')
        circle2=circle.GetClone()
        circle2.SetName('Circle2')
        
        coil=c4d.BaseObject(c4d.Onull)
        coil.SetName('coil')    
        turn=c4d.BaseObject(c4d.Onull)
        turn.SetName('turn')
        shape2D['Coil']=coil
        shape2D['Turn']=turn        
    
        self.addObjectToScene(doc,coil,parent=parent )
        self.addObjectToScene(doc,circle,parent=coil )
        self.addObjectToScene(doc,turn,parent=parent )
        self.addObjectToScene(doc,circle2,parent=turn )
    
        rectangle=c4d.BaseObject(RECTANGLE)
        rectangle[2060]=float(2.2)
        rectangle[2061]=float(0.7)
        rectangle[2300]=0
        rectangle.SetName('Rectangle1')
        rectangle2=rectangle.GetClone()
        rectangle2.SetName('Rectangle2')
        
        stra=c4d.BaseObject(c4d.Onull)
        stra.SetName('stra')    
        shee=c4d.BaseObject(c4d.Onull)
        shee.SetName('shee')
        shape2D['Stra']=stra
        shape2D['Shee']=shee        
    
        self.addObjectToScene(doc,stra,parent=parent )
        self.addObjectToScene(doc,rectangle,parent=stra )
        self.addObjectToScene(doc,shee,parent=parent )
        self.addObjectToScene(doc,rectangle2,parent=shee )
        
        fourside=c4d.BaseObject(FOURSIDE)
        fourside[2121]=float(2.5)
        fourside[2122]=float(0.9)
        fourside[2300]=0
        heli=c4d.BaseObject(c4d.Onull)
        heli.SetName('heli')    
        shape2D['Heli']=heli    
    
        self.addObjectToScene(doc,heli,parent=parent )
        self.addObjectToScene(doc,fourside,parent=heli)
        
        return shape2D,[circle,rectangle,fourside]
    
    def getShapes2D(self):
        shape2D={}
        shape2D['Coil']=getObject('coil')
        shape2D['Turn']=getObject('turn')
        shape2D['Heli']=getObject('heli')
        shape2D['Stra']=getObject('stra')        
        return shape2D
    
    def morph2dObject(self,name,objsrc,target):
        obj=objsrc.GetClone()
        obj.SetName(name)
        mixer=obj.MakeTag(self.POSEMIXER)
        mixer[1001]=objsrc    #the default pose
        #for i,sh in enumerate(shape2D) :
        #    mixer[3002,1000+int(i)]=shape2D[sh]
        mixer[3002,1000]=target#shape2D[sh] target 1
        return obj
        
    def c4dSpecialRibon(self,name,points,dshape=CIRCLE,shape2dlist=None,mat=None):
        #if loft == None : loft=loftnurbs('loft',mat=mat)
        shape=[]
        pos=c4d.Vector(float(points[0][2]),float(points[0][1]),float(points[0][0]))
        direction=c4d.Vector(float(points[0][2]-points[1][2]),float(points[0][1]-points[1][1]),float(points[0][0]-points[1][0]))
        mx=self.getCoordinateMatrix(pos,direction)
        if shape2dlist : shape.append(morph2dObject(dshape+str(0),shape2dlist[dshape],shape2dlist['Heli']))
        else : 
            shape.append(c4d.BaseObject(dshape))
            if dshape == self.CIRCLE :
                shape[0][2012]=float(0.3)
                #shape[0][2300]=1
            if dshape == self.RECTANGLE :
                shape[0][2060]=float(0.3*4.)
                shape[0][2061]=float(0.3*3.)
                #shape[0][2300]=1
            if dshape == self.FOURSIDE:
                shape[0][2121]=float(0.3*4.)
                shape[0][2122]=float(0.1)
                #shape[0][2300]=0            
        shape[0].SetMg(mx)
        if len(points)==2: return shape
        i=1
        while i < (len(points)-1):
            #print i
            pos=c4d.Vector(float(points[i][2]),float(points[i][1]),float(points[i][0]))
            direction=c4d.Vector(float(points[i-1][2]-points[i+1][2]),float(points[i-1][1]-points[i+1][1]),float(points[i-1][0]-points[i+1][0]))
            mx=self.getCoordinateMatrix(pos,direction)
            if shape2dlist : shape.append(morph2dObject(dshape+str(i),shape2dlist[dshape],shape2dlist['Heli']))
            else : 
                shape.append(c4d.BaseObject(dshape))    
                if dshape == self.CIRCLE :
                    shape[i][2012]=float(0.3)
                    shape[i][2300]=2
                if dshape == self.RECTANGLE :
                    shape[i][2060]=float(0.3*4.)
                    shape[i][2061]=float(0.3*3.)
                    shape[i][2300]=2
                if dshape == self.FOURSIDE:
                    shape[i][2121]=float(0.3*4.)
                    shape[i][2122]=float(0.1)
                    shape[i][2300]=2            
            shape[i].SetMg(mx)
            i=i+1
        pos=c4d.Vector(float(points[i][2]),float(points[i][1]),float(points[i][0]))
        direction=c4d.Vector(float(points[i-1][2]-points[i][2]),float(points[i-1][1]-points[i][1]),float(points[i-1][0]-points[i][0]))
        mx=self.getCoordinateMatrix(pos,direction)
        if shape2dlist : shape.append(morph2dObject(dshape+str(i),shape2dlist[dshape],shape2dlist['Heli']))
        else : 
            shape.append(c4d.BaseObject(dshape))
            if dshape == self.CIRCLE :
                shape[i][2012]=float(0.3)
                shape[i][2300]=2
            if dshape == self.RECTANGLE :
                shape[i][2060]=float(0.3*4.)
                shape[i][2061]=float(0.3*3.)
                shape[i][2300]=2        
            if dshape == self.FOURSIDE:
                shape[i][2121]=float(0.3*4.)
                shape[i][2122]=float(0.1)
                shape[i][2300]=2
        shape[i].SetMg(mx)
        return shape
        
    def c4dSecondaryLofts(self,name,matrices,dshape=CIRCLE,mat=None):
        #if loft == None : loft=loftnurbs('loft',mat=mat)
        shape=[]            
        i=0
        while i < (len(matrices)):
            #pos=c4d.Vector(float(points[i][2]),float(points[i][1]),float(points[i][0]))
            #direction=c4d.Vector(float(points[i-1][2]-points[i+1][2]),float(points[i-1][1]-points[i+1][1]),float(points[i-1][0]-points[i+1][0]))
            mx=self.getCoordinateMatrixBis(matrices[i][2],matrices[i][0],matrices[i][1])
            #mx=getCoordinateMatrix(pos,direction)
            shape.append(c4d.BaseObject(dshape))    
            shape[i].SetMg(mx)
            if dshape == self.CIRCLE :
                shape[i][2012]=float(0.3)
                shape[i][2300]=0
            if dshape == self.RECTANGLE :
                shape[i][2060]=float(2.2)
                shape[i][2061]=float(0.7)
                shape[i][2300]=0
            if dshape == self.FOURSIDE:
                shape[i][2121]=float(2.5)
                shape[i][2122]=float(0.9)
                shape[i][2300]=0            
            i=i+1
        return shape
    
    def instanceShape(self,ssname,shape2D):
        #if shape2D=None : shape2D=createShapes2D()
        shape=c4d.BaseObject(c4d.Oinstance)
        shape[1001]=shape2D[ssname[:4]]
        shape.SetName(ssname[:4])
        return shape
        
    def makeShape(self,dshape,ssname):
        shape=c4d.BaseObject(dshape)
        if dshape == self.CIRCLE :
                    shape[2012]=float(0.3)
                    shape[2300]=0
                    shape.SetName(ssname[:4])                
        if dshape == self.RECTANGLE :
                    shape[2060]=float(2.2)
                    shape[2061]=float(0.7)
                    shape[2300]=0
                    shape.SetName(ssname[:4])                    
        if dshape == self.FOURSIDE:
                    shape[2121]=float(2.5)
                    shape[2122]=float(0.9)
                    shape[2300]=0
                    shape.SetName(ssname[:4])                
        return shape
        
    def c4dSecondaryLoftsSp(self,name,atoms,dshape=CIRCLE,mat=None,shape2dmorph=None,shapes2d=None,instance=False):
        #print "ok build loft shape"
        #if loft == None : loft=loftnurbs('loft',mat=mat)
        shape=[]
        prev=None    
        ssSet=atoms[0].parent.parent.secondarystructureset
        molname=atoms[0].full_name().split(":")[0]
        chname=    atoms[0].full_name().split(":")[1]        
        i=0
        iK=0
        #get The pmv-extruder    
        sheet=atoms[0].parent.secondarystructure.sheet2D
        matrices=sheet.matrixTransfo
        if mat == None : mat = c4d.documents.GetActiveDocument().SearchMaterial('mat_loft'+molname+'_'+chname)
        while i < (len(atoms)):
            ssname=atoms[i].parent.secondarystructure.name
            dshape=SSShapes[ssname[:4]]#ssname[:4]
            #print ssname,dshape        
            #pos=c4d.Vector(float(points[i][2]),float(points[i][1]),float(points[i][0]))
            #direction=c4d.Vector(float(points[i-1][2]-points[i+1][2]),float(points[i-1][1]-points[i+1][1]),float(points[i-1][0]-points[i+1][0]))
            mx=self.getCoordinateMatrixBis(matrices[i][2],matrices[i][0],matrices[i][1])
            #mx=getCoordinateMatrix(pos,direction)
            #iK=iK+1
            if shape2dmorph :
                shape.append(self.morph2dObject(dshape+str(i),shape2dmorph[dshape],shape2dmorph['Heli']))
                shape[-1].SetMg(mx)
            else :
                #print str(prev),ssname         
                if prev != None: #end of loop 
                    if ssname[:4] != prev[:4]:
                        if not instance : shape.append(self.makeShape(SSShapes[prev[:4]],prev))
                        else : shape.append(self.instanceShape(prev,shapes2d))                    
                        shape[-1].SetMg(mx)
                if not instance : shape.append(self.makeShape(dshape,ssname))
                else : shape.append(self.instanceShape(ssname,shapes2d))
                shape[-1].SetMg(mx)
            prev=ssname
            i=i+1
        if mat != None:
            prev=None
            #i=(len(shape))
            i=0
            while i < (len(shape)):
                ssname=shape[i].GetName()
                #print ssname            
                pos=1-((((i)*100.)/len(shape))/100.0)
                if pos < 0 : pos = 0.
                #print pos
                #change the material knote according ss color / cf atom color...
                #col=atoms[i].colors['secondarystructure']
                col=self.c4dColor(SSColor[ssname])
                nc=c4d.Vector(col[0],col[1],col[2])
                ncp=c4d.Vector(0,0,0)            
                if prev != None :
                    pcol=self.c4dColor(SSColor[prev])
                    ncp=c4d.Vector(pcol[0],pcol[1],pcol[2])        
                #print col
                #print ssname[:4]
                #print prev
                if ssname != prev : #new ss
                    grad=mat[8000][1007]    
                #iK=iK+1
                    nK=grad.GetKnotCount()
                #print "knot count ",nK,iK                
                    if iK >= nK :
                        #print "insert ",pos,nK
                        #print "grad.insert_knot(c4d.Vector("+str(col[0])+str(col[1])+str(col[2])+"), 1.0, "+str(pos)+",0.5)"
                        if prev != None :
                            grad.InsertKnot(ncp, 1.0, pos+0.01,0.5)
                            iK=iK+1                                                
                        grad.InsertKnot(nc, 1.0, pos-0.01,0.5)
                        #grad.insert_knot(ncp, 1.0, pos+0.1,0.5)                    
                        iK=iK+1                    
                    else :
                        #print "set ",iK,pos    
                        if prev != None :grad.SetKnot(iK-1,ncp,1.0,pos,0.5)                            
                        grad.SetKnot(iK,nc,1.0,pos,0.5)
                    mat[8000][1007]=grad
                prev=ssname
                mat.Message(c4d.MSG_UPDATE)
                i=i+1            
        #mx=getCoordinateMatrixBis(matrices[i][2],matrices[i][0],matrices[i][1])
        #if shape2dlist : shape.append(morph2dObject(dshape+str(i),shape2dlist[shape],shape2dlist['Heli']))
        return shape
    
    def LoftOnSpline(self,name,chain,atoms,Spline=None,dshape=CIRCLE,mat=None,
                     shape2dmorph=None,shapes2d=None,instance=False):
        #print "ok build loft/spline"
        molname = atoms[0].full_name().split(":")[0]
        chname = atoms[0].full_name().split(":")[1]        
        #we first need the spline
        #if loft == None : loft=loftnurbs('loft',mat=mat)
        shape=[]
        prev=None
        #mol = atoms[0].top        
        ssSet=chain.secondarystructureset#atoms[0].parent.parent.secondarystructureset
        i=0
        iK=0
        #get The pmv-extruder    
        sheet=chain.residues[0].secondarystructure.sheet2D
        matrices=sheet.matrixTransfo
        ca=atoms.get('CA')
        o =atoms.get('O') 
        if Spline is None :
            parent=atoms[0].parent.parent.parent.geomContainer.masterGeom.chains_obj[chname]
            Spline,ospline = spline(name+'spline',ca.coords)#
            addObjectToScene(getCurrentScene(),Spline,parent=parent) 
        #loftname = 'loft'+mol.name+'_'+ch.name 
        #matloftname = 'mat_loft'+mol.name+'_'+ch.name
        if mat == None : 
            mat = c4d.documents.GetActiveDocument().SearchMaterial('mat_loft'+molname+'_'+chname)
            if  mat is not None :
                if DEBUG : print "ok find mat"
            #if mat == None :
            #    mat = create_loft_material(name='mat_loft'+molname+'_'+chname)
        if DEBUG : print "CA",len(ca)
        while i < (len(ca)):
            pos= float(((i*1.) / len(ca)))
            #print str(pos)+" %"  
            #print atoms[i],atoms[i].parent,hasattr(atoms[i].parent,'secondarystructure')                      
            if hasattr(ca[i].parent,'secondarystructure') : ssname=ca[i].parent.secondarystructure.name
            else : ssname="Coil"
            dshape=SSShapes[ssname[:4]]#ssname[:4]
            #mx =getCoordinateMatrixBis(matrices[i][2],matrices[i][0],matrices[i][1])
            #have to place the shape on the spline    
            if shape2dmorph :
                shape.append(morph2dObject(dshape+str(i),shape2dmorph[dshape],shape2dmorph['Heli']))
                path=shape[i].MakeTag(Follow_PATH)
                path[1001] = Spline
                path[1000] = 0#tangantial
                path[1003] = pos
                path[1007] = 2#1        axe                
                #shape[-1].SetMg(mx)
            else :
                #print str(prev),ssname         
                #if prev != None: #end of loop 
                #    if ssname[:4] != prev[:4]: #newSS need transition
                #        if not instance : shape.append(makeShape(SSShapes[prev[:4]],prev))
                #        else : shape.append(instanceShape(prev,shapes2d))                    
                #        #shape[-1].SetMg(mx)
                #        path=shape[-1].MakeTag(Follow_PATH)
                #        path[1001] = Spline
                #        path[1000] = 1    
                #        path[1003] = pos                
                if not instance : shape.append(makeShape(dshape,ssname))
                else : shape.append(instanceShape(ssname,shapes2d))
                path=shape[i].MakeTag(Follow_PATH)
                path[1001] = Spline
                path[1000] = 0  
                path[1003] = pos                                           
                path[1007] = 2#1
                #shape[-1].SetMg(mx)        
            if i >=1  : 
                laenge,mx=getStickProperties(ca[i].coords,ca[i-1].coords)
                #if i > len(o) : laenge,mx=getStickProperties(ca[i].coords,o[i-1].coords)
                #else :laenge,mx=getStickProperties(ca[i].coords,o[i].coords)
                shape[i].SetMg(mx)    
            prev=ssname
            i=i+1
        laenge,mx=getStickProperties(ca[0].coords,ca[1].coords) 
        #laenge,mx=getStickProperties(ca[0].coords,o[0].coords) 
        shape[0].SetMg(mx)          
        if False :#(mat != None):
            prev=None
            #i=(len(shape))
            i=0
            while i < (len(shape)):
                ssname=shape[i].GetName()
                #print ssname            
                pos=1-((((i)*100.)/len(shape))/100.0)
                if pos < 0 : pos = 0.
                #print pos
                #change the material knote according ss color / cf atom color...
                #col=atoms[i].colors['secondarystructure']
                col=c4dColor(SSColor[ssname])
                nc=c4d.Vector(col[0],col[1],col[2])
                ncp=c4d.Vector(0,0,0)            
                if prev != None :
                    pcol=c4dColor(SSColor[prev])
                    ncp=c4d.Vector(pcol[0],pcol[1],pcol[2])        
                #print col
                #print ssname[:4]
                #print prev
                if ssname != prev : #new ss
                    grad=mat[8000][1007]    
                #iK=iK+1
                    nK=grad.GetKnotCount()
                #print "knot count ",nK,iK                
                    if iK >= nK :
                        #print "insert ",pos,nK
                        #print "grad.insert_knot(c4d.Vector("+str(col[0])+str(col[1])+str(col[2])+"), 1.0, "+str(pos)+",0.5)"
                        if prev != None :
                            grad.InsertKnot(ncp, 1.0, pos+0.01,0.5)
                            iK=iK+1                                                
                        grad.InsertKnot(nc, 1.0, pos-0.01,0.5)
                        #grad.insert_knot(ncp, 1.0, pos+0.1,0.5)                    
                        iK=iK+1                    
                    else :
                        #print "set ",iK,pos    
                        if prev != None :grad.SetKnot(iK-1,ncp,1.0,pos,0.5)                            
                        grad.SetKnot(iK,nc,1.0,pos,0.5)
                    mat[8000][1007]=grad
                prev=ssname
                mat.Message(c4d.MSG_UPDATE)
                i=i+1            
        #mx=getCoordinateMatrixBis(matrices[i][2],matrices[i][0],matrices[i][1])
        #if shape2dlist : shape.append(morph2dObject(dshape+str(i),shape2dlist[shape],shape2dlist['Heli']))
        return shape
    
    def update_2dsheet(shapes,builder,loft):
        dicSS={'C':'Coil','T' : 'Turn', 'H':'Heli','E':'Stra','P':'Coil'}
        shape2D=getShapes2D()
        for i,ss in enumerate(builder):
            if     shapes[i].GetName() != dicSS[ss]:
                shapes[i][1001]=shape2D[dicSS[ss]]#ref object
                shapes[i].SetName(dicSS[ss])    
    
        texture = loft.GetTags()[0]
        mat=texture[1010]
        grad=mat[8000][1007]
        grad.delete_all_knots()
        mat[8000][1007]=grad
    
        prev=None
        i = 0
        iK = 0    
        while i < (len(shapes)):
                ssname=shapes[i].GetName()
                #print ssname            
                pos=1-((((i)*100.)/len(shapes))/100.0)
                if pos < 0 : pos = 0.
                #print pos
                #change the material knote according ss color / cf atom color...
                #col=atoms[i].colors['secondarystructure']
                col=c4dColor(SSColor[ssname])
                nc=c4d.Vector(col[0],col[1],col[2])
                ncp=c4d.Vector(0,0,0)            
                if prev != None :
                    pcol=c4dColor(SSColor[prev])
                    ncp=c4d.Vector(pcol[0],pcol[1],pcol[2])        
                #print col
                #print ssname[:4]
                #print prev
                if ssname != prev : #new ss
                    grad=mat[8000][1007]    
                #iK=iK+1
                    nK=grad.get_knot_count()
                #print "knot count ",nK,iK                
                    if iK >= nK :
                        #print "insert ",pos,nK
                        #print "grad.insert_knot(c4d.Vector("+str(col[0])+str(col[1])+str(col[2])+"), 1.0, "+str(pos)+",0.5)"
                        if prev != None :
                            grad.insert_knot(ncp, 1.0, pos+0.01,0.5)
                            iK=iK+1                                                
                        grad.insert_knot(nc, 1.0, pos-0.01,0.5)
                        #grad.insert_knot(ncp, 1.0, pos+0.1,0.5)                    
                        iK=iK+1                    
                    else :
                        #print "set ",iK,pos    
                        if prev != None :grad.set_knot(iK-1,ncp,1.0,pos,0.5)                            
                        grad.set_knot(iK,nc,1.0,pos,0.5)
                    mat[8000][1007]=grad
                prev=ssname
                mat.Message(c4d.MSG_UPDATE)
                i=i+1            
        
    def makeLines(self,name,points,faces,parent=None):
        rootLine = self.newEmpty(name)
        self.addObjectToScene(self.getCurrentScene(),rootLine,parent=parent)
        spline=c4d.BaseObject(c4d.Ospline)
        #spline[1000]=type
        #spline[1002]=close
        spline.SetName(name+'mainchain')
        spline.ResizeObject(int(len(points)))
        cd4vertices = map(self.FromVec,points)
        map(polygon.SetPoint,range(len(points)),cd4vertices)    
        #for i,p in enumerate(points):
        #    spline.SetPoint(i, c4dv(p))
        self.addObjectToScene(self.getCurrentScene(),spline,parent=rootLine)
        spline=c4d.BaseObject(c4d.Ospline)
        #spline[1000]=type
        #spline[1002]=close
        spline.SetName(name+'sidechain')
        spline.ResizeObject(int(len(points)))
        for i,p in enumerate(points):
            spline.SetPoint(i, self.FromVec(p))
        self.addObjectToScene(self.getCurrentScene(),spline,parent=rootLine)    
    
    def updateLines(self,lines, chains=None):
        #lines = getObject(name)    
        #if lines == None or chains == None:
            #print lines,chains    
            #parent = getObject(chains.full_name())    
            #print parent        
    #    bonds, atnobnd = chains.residues.atoms.bonds
    #    indices = map(lambda x: (x.atom1._bndIndex_,
    #                                x.atom2._bndIndex_), bonds)
    #    updatePoly(lines,vertices=chains.residues.atoms.coords,faces=indices)
        self.updatePoly(self,lines,vertices=chains.residues.atoms.coords)
    
#    def getCoordByAtomType(chain):
#        dic={}
#        #extract the different atomset by type
#        for i,atms in enumerate(AtomElements.keys()):
#            atomset = chain.residues.atoms.get(atms)
#            bonds, atnobnd = atomset.bonds
#            indices = map(lambda x: (x.atom1._bndIndex_,
#                                 x.atom2._bndIndex_), bonds)
#            dic[atms] = [atomset]
#        
#    def stickballASmesh(molecules,atomSets):
#        bsms=[]
#        for mol, atms, in map(None, molecules, atomSets):
#            for ch in mol.chains:
#                parent = getObject(ch.full_name())
#                lines = getObject(ch.full_name()+'_bsm')
#                if lines == None :
#                    lines=newEmpty(ch.full_name()+'_bsm')
#                    addObjectToScene(getCurrentScene(),lines,parent=parent)
#                    dic = getCoordByAtomType(ch)
#                    for type in dic.keys():
#                        bsm = createsNmesh(ch.full_name()+'_bsm'+type,dic[type][0],
#                                         None,dic[type][1])
#                        bsms.append(bsm)
#                        addObjectToScene(getCurrentScene(),bsm,parent=lines)
    
#    def editLines(molecules,atomSets):
#        for mol, atms, in map(None, molecules, atomSets):
#            #check if line exist
#            for ch in mol.chains:
#                parent = getObject(ch.full_name())
#                lines = getObject(ch.full_name()+'_line')
#                if lines == None :
#                    arr = c4d.BaseObject(ATOMARRAY)
#                    arr.SetName(ch.full_name()+'_lineds')
#                    arr[1000] = 0.1 #radius cylinder
#                    arr[1001] = 0.1 #radius sphere
#                    arr[1002] = 3 #subdivision
#                    addObjectToScene(getCurrentScene(),arr,parent=parent)                
#                    bonds, atnobnd = ch.residues.atoms.bonds
#                    indices = map(lambda x: (x.atom1._bndIndex_,
#                                             x.atom2._bndIndex_), bonds)
#    
#                    lines = createsNmesh(ch.full_name()+'_line',ch.residues.atoms.coords,
#                                         None,indices)
#                    addObjectToScene(getCurrentScene(),lines[0]    ,parent=arr)
#                    mol.geomContainer.geoms[ch.full_name()+'_line'] = lines
#                    #display using AtomArray
#                else : #need to update
#                    updateLines(lines, chains=ch)

    def matrixToEdgeMesh(self,name,matrices,**kw):#edge size ?
        pt1=[0.,-5.,0.]
        pt2=[0.,5.,0.]#edgelength
        v=[]
        f=[]
        e=[]
        i=0
        ie=0
        for n,m in enumerate(matrices):
            p1,p2=self.ApplyMatrix([pt1,pt2],m)
            v.extend([p1,p2])#edge we want
            e.extend([ie,ie+1])
            face1 = [i,i+1]
            f.append(face1)
            ie+=4
#            face2 = [i+3,i+4]
            #everyt thre matrices make tow triangle ?
#            if n < len(matrices)-2 :
#                face1 = [i,i+1,i+2]
#                face2 = [i+3,i+4,i]
#                f.extend([face1,face2])
            i+=2     
        #need to create triangle    
        obj= c4d.PolygonObject(len(v), len(f))
        print len(v),len(f)
        obj.SetName(name)
        cd4vertices = map(self.FromVec,v)
        #map(obj.SetPoint,range(len(v)),cd4vertices)  
        [obj.SetPoint(k, self.FromVec(av)) for k,av in enumerate(v)]
        for k,af in enumerate(f) :
            #print k,af
            obj.SetPolygon(k, self.FromFace(af))
#        [obj.SetPolygon(k, self.FromFace(af)) for k,af in enumerate(f)]
        stag = c4d.SelectionTag(c4d.Tedgeselection)
        obj.InsertTag(stag)        
        c4d.EventAdd()        
#        vtag.SetName(tagName)
        self.addObjectToScene(self.getCurrentScene(),obj)
        if 'parent' in kw and kw['parent'] is not None: 
            parent = self.getObject(kw['parent'])
            obj.parent = parent
        #select the edge
        nbr = c4d.utils.Neighbor()
        nbr.Init(obj) # Initialize neighbor with a polygon object
    
        edges = c4d.BaseSelect()
        edges.SelectAll(nbr.GetEdgeCount()) # Select all edges in the range [0, nbr.GetEdgeCount()]
        states=[]
        for index, selected in enumerate(edges.GetAll(nbr.GetEdgeCount())):
            if index in edge :
                states.append(1)
            else :
                states.append(0)        
        #    print index,bsel.IsSelected(index)
        edges.SetAll(states)
        obj.SetSelectedEdges(nbr, edges, c4d.EDGESELECTIONTYPE_SELECTION) # Select edges from our edges selection
        c4d.EventAdd() # Update CINEMA
        return obj,obj
                    
    def PointCloudObject(self,name,**kw):
        #need to add the AtomArray modifier....
        pointWidth = 0.1
        doatom = True
        if kw.has_key("pointWidth"):
            pointWidth = float(kw["pointWidth"])
        if kw.has_key("parent"):
            parent = kw["parent"]
        else :
            parent = None        
        if kw.has_key("atomarray"):
            doatom = kw["atomarray"]
        if doatom :
            atom = c4d.BaseObject(c4d.Oatomarray)
            atom.SetName(name+"ds")
            atom[1000] = 0. #radius cylinder
            atom[1001] = pointWidth #radius sphere
            atom[1002] = 3 #subdivision
            self.addObjectToScene(self.getCurrentScene(),atom,parent=parent)
            parent = atom
        if kw.has_key("materials"):
            texture = parent.MakeTag(c4d.Ttexture)
            texture[1010] = self.addMaterial("mat"+name,kw["materials"][0])
        coords=kw['vertices']
        nface = 0    
        if kw.has_key("faces"):
            nface = len(kw['faces'])
        visible = 1    
        if kw.has_key("visible"):
            visible = kw['visible']     
        obj= c4d.PolygonObject(len(coords), nface)
        obj.SetName(name)
        cd4vertices = map(self.FromVec,coords)
        map(obj.SetPoint,range(len(coords)),cd4vertices)    
        #for k,v in enumerate(coords) :
        #    obj.SetPoint(k, c4dv(v))
        self.addObjectToScene(self.getCurrentScene(),obj,parent=parent)
        if parent is not None:
            self.toggleDisplay(parent,bool(visible))
        if doatom : 
            return obj,atom
        else :
            return obj,None
    
    def PolygonColorsObject(self,name,vertColors):
        obj= c4d.PolygonObject(len(vertColors), len(vertColors)/2.)
        obj.SetName(name+'_color')
        cd4vertices = map(self.FromVec,vertColors)
        map(obj.SetPoint,range(len(vertColors)),cd4vertices)
        #for k,v in enumerate(vertColors) :   
        #      obj.SetPoint(k, c4dv(v))
        return obj

    def updatePoly(self,polygon,faces=None,vertices=None):
        if type(polygon) == str:
            polygon = self.getObject(polygon)
        if polygon == None : return
        #check if polygon
        if self.getType(polygon) != self.POLYGON:
            #try to get the childs
            polygon=polygon.GetDown()
            if self.getType(polygon) != self.POLYGON:
                print "not a polygon",polygon.GetName()
                return
        if vertices != None:
            [polygon.SetPoint(k, self.FromVec(v)) for k,v in enumerate(vertices)]
#            for k,v in enumerate(vertices) :
#                polygon.SetPoint(k, self.FromVec(v))
        if faces != None:
            [polygon.SetPolygon(k, self.FromFace(f)) for k,f in enumerate(faces)]
        polygon.Message(c4d.MSG_UPDATE)
        c4d.EventAdd()
        #should we send other message?
#        self.update()
        
    def redoPoly(self,poly,vertices,faces,proxyCol=False,colors=None,parent=None,mol=None):
        doc = self.getCurrentScene()
        doc.SetActiveObject(poly)
        name=poly.GetName()
        texture = poly.GetTags()[0]
        c4d.CallCommand(100004787) #delete the obj
        obj=self.createsNmesh(name,vertices,None,faces,smooth=False,material=texture[1010],proxyCol=proxyCol)
        self.addObjectToScene(doc,obj[0],parent=parent)
        if proxyCol and colors!=None:
            pObject=self.getObject(name+"_color")
            doc.SetActiveObject(pObject)
            c4d.CallCommand(100004787) #delete the obj    
            pObject=PolygonColorsObject(name,colors)
            self.addObjectToScene(doc,pObject,parent=parent)
    
    def reCreatePoly(self,poly,vertices,faces,proxyCol=False,colors=None,parent=None,mol=None):
        doc = self.getCurrentScene()
        doc.SetActiveObject(poly)
        name=poly.GetName()
        texture = poly.GetTags()[0]
        c4d.CallCommand(100004787) #delete the obj
        obj=self.createsNmesh(name,vertices,None,faces,smooth=False,material=texture[1010],proxyCol=proxyCol)
        self.addObjectToScene(doc,obj[0],parent=parent)
        if proxyCol and colors!=None:
            pObject=self.getObject(name+"_color")
            doc.SetActiveObject(pObject)
            c4d.CallCommand(100004787) #delete the obj    
            pObject=self.PolygonColorsObject(name,colors)
            self.addObjectToScene(doc,pObject,parent=parent)
        
    """def UVWColorTag(obj,vertColors):
          uvw=obj.MakeTag(c4d.Tuvw)
        
          obj= c4d.PolygonObject(len(vertColors), len(vertColors)/2.)
          obj.SetName(name+'_color')
          k=0
          for v in vertColors :
              print v      
              obj.SetPoint(k, c4d.Vector(float(v[0]), float(v[1]), float(v[2])))
              k=k+1
          return obj
    """
#    def updateMesh(self,obj,vertices=None,faces = None, smooth=False,**kw):
#        if type(obj) == str:
#            obj = self.getObject(obj)
#        if obj == None : return        
##        objdcache=obj.GetDeformCache()
##        objcache=obj.GetCache()
##        if objdcache is not None:
##            obj = objdcache
##        elif objcache is not None:
##            obj = objcache
#        oldN=obj.GetPointCount()
#        newN=len(vertices)  
#        obj.ResizeObject(newN,len(faces))
#        self.updatePoly(obj,faces=faces,vertices=vertices)
#        sys.stderr.write('\nnb v %d %d f %d' % (oldN,len(vertices),len(faces)))
        
    def updateMeshProxy(self,obj,proxyCol=False,parent=None,mol=None):
        doc = getCurrentScene()
        doc.SetActiveObject(g.obj)
        name=obj.GetName()   
        texture = obj.GetTags()[0]
        c4d.CallCommand(100004787) #delete the obj
        vertices=g.getVertices()
        faces=g.getFaces()
#        if DEBUG : print len(vertices),len(faces)
        sys.stderr.write('\nnb v %d f %d\n' % (len(vertices),len(faces))) 
        #if     proxyCol : o=PolygonColorsObject
        obj=self.createsNmesh(name,vertices,None,faces,smooth=False,material=texture[1010],proxyCol=proxyCol)
        self.addObjectToScene(doc,obj[0],parent=parent)
        #obj.Message(c4d.MSG_UPDATE)
        return obj[0]
    #    if proxyCol :
    #        colors=mol.geomContainer.getGeomColor(g.name)
    #        if hasattr(g,'color_obj'):
    #            pObject=g.color_obj#getObject(name+"_color")
    #            doc.SetActiveObject(pObject)
    #            c4d.CallCommand(100004787) #delete the obj 
    #        pObject=PolygonColorsObject(name,colors)
    #        g.color_obj=pObject
    #        addObjectToScene(doc,pObject,parent=parent)
        
    def c4df(self,face,g,polygon):
        A = int(face[0])
        B = int(face[1])
        if len(face)==2 :
            C = B
            D = B
            poly=c4d.CPolygon(A, B, C)
        elif len(face)==3 : 
            C = int(face[2])
            D = C
            poly=c4d.CPolygon(A, B, C)
        elif len(face)==4 : 
            C = int(face[2])
            D = int(face[3])
            poly=c4d.CPolygon(A, B, C, D)
        polygon.SetPolygon(id=g, polygon=poly)
        return [A,B,C,D]
    
#    def polygons(self,name,proxyCol=False,smooth=False,color=[[1,0,0],], material=None, **kw):
#        import time
#        t1 = time.time()
#        vertices = kw["vertices"]
#        faces = kw["faces"]
#        normals = kw["normals"]
#        frontPolyMode='fill'
#        if kw.has_key("frontPolyMode"):      
#            frontPolyMode = kw["frontPolyMode"]
#        if kw.has_key("shading") :  
#            shading=kw["shading"]#'flat'
##          if frontPolyMode == "line" : #wire mode
##              material = self.getCurrentScene().SearchMaterial("wire")
##              if material == None:
##                  material = self.addMaterial("wire",(0.5,0.5,0.5))                                              
#        polygon = c4d.PolygonObject(len(vertices), len(faces))
#        polygon.SetName(name)      
#        k=0
#
#        [polygon.SetPoint(k, self.FromVec(v)) for k,v in enumerate(vertices)]
#        [polygon.SetPolygon(k, self.FromFace(f)) for k,f in enumerate(faces)]
#
#        t2=time.time()
#        polygon.MakeTag(c4d.Tphong) #shading ?
#          # create a texture tag on the PDBgeometry object
#        doMaterial = True
#        if type(material) is bool or not proxyCol:
#            doMaterial = material
#        elif material is None :
#            doMaterial = False
#        if not proxyCol :#and doMaterial:
#            texture = polygon.MakeTag(c4d.Ttexture)
#              #create the dedicayed material
#            if material == None :
#                texture[1010] = self.addMaterial("mat_"+name,color[0])
#            else : texture[1010] = material
##          else :
##            if color is not None:
##                self.changeColor(polygon,color,proxyObject=True)
#        polygon.Message(c4d.MSG_UPDATE)
#        return polygon

            
#    def createsNmesh(self,name,vertices,vnormals,faces,smooth=False,
#                     material=None,proxyCol=False,color=[[1,0,0],],**kw):
#        """
#        This is the main function that create a polygonal mesh.
#        
#        @type  name: string
#        @param name: name of the pointCloud
#        @type  vertices: array
#        @param vertices: list of x,y,z vertices points
#        @type  vnormals: array
#        @param vnormals: list of x,y,z vertex normals vector
#        @type  faces: array
#        @param faces: list of i,j,k indice of vertex by face
#        @type  smooth: boolean
#        @param smooth: smooth the mesh
#        @type  material: hostApp obj
#        @param material: material to apply to the mesh    
#        @type  proxyCol: booelan
#        @param proxyCol: do we need a special object for color by vertex (ie C4D)
#        @type  color: array
#        @param color: r,g,b value to color the mesh
#    
#        @rtype:   hostApp obj
#        @return:  the polygon object
#        """
#        if len(color) == 3 :
#            if type(color[0]) is not list :
#                color = [color,]
#        PDBgeometry = self.polygons(name, vertices=vertices,normals=vnormals,
#                                      faces=faces,material=material,color=color,
#                                      smooth=smooth,proxyCol=proxyCol)
#        parent = None
#        if "parent" in kw:
#            parent = kw["parent"]
#        self.addObjectToScene(None,PDBgeometry,parent=parent)
#        return [PDBgeometry,PDBgeometry]
##    
#    def instancePolygon(self,name, matrices=None,hmatrices=None, mesh=None,parent=None,
#                        transpose=False,globalT=True,**kw):
#        if hmatrices is not None :
#            matrices = hmatrices
#        if matrices == None : return None
#        if mesh == None : return None
#        instance = []
#        #print len(matrices)#4,4 mats
#        for i,mat in enumerate(matrices):
#            inst = self.getObject(name+str(i))
#            if inst is None :
#                inst = c4d.BaseObject(c4d.Oinstance)
#                inst.SetName(name+str(i))
#                self.AddObject(inst,parent=parent)
#            instance.append(inst)
#            instance[-1][1001]=mesh
#            if hmatrices is not None :
#                mx = mat            
#            elif matrices is not None :
#                if type(mat) != c4d.Matrix:
#                    mx = self.matrix2c4dMat(mat,transpose=transpose)
#                else :
#                    mx = mat 
#            if globalT :
#                instance[-1].SetMg(mx)
#            else :
#                instance[-1].SetMl(mx)
#            #instance[-1].MakeTag(c4d.Ttexture)
#        return instance
#
#    def updateInstancePolygon(self,name,instance, matrices=None,hmatrices=None,mesh=None,
#                              parent=None,transpose=False,globalT=True):
#        if matrices == None : return None
#        if mesh == None : return None
#        #instance = []      
#        #print len(matrices)#4,4 mats
#        if instance is None:
#            instance = []
#        if hmatrices is not None :
#            matrices = hmatrices
#        for i,mat in enumerate(matrices):
#            inst = self.getObject(name+str(i))
#            if i > len(instance) or inst is None:
#                inst = c4d.BaseObject(c4d.Oinstance)
#                inst.SetName(name+str(i))
#                self.AddObject(inst,parent=parent)
#                instance.append(inst)
#            inst[1001]=mesh
#            if hmatrices is not None :
#                mx = mat            
#            elif matrices is not None :
#                mx = self.matrix2c4dMat(mat,transpose=transpose)
#            if globalT :
#                inst.SetMg(mx)
#            else :
#                inst.SetMl(mx)
#            #instance[-1].MakeTag(c4d.Ttexture)
#        return instance
#        
    def setVColor(self,j,ncolor):
        _colsc = 1.0
        if ncolor is None :
            return 0.
        if (j==0) : return ncolor.x/_colsc
        if (j==1) : return ncolor.y/_colsc
        if (j==2) : return ncolor.z/_colsc
    
    def CreateVertexRGBmaps(self,mesh,proxy=None,vcolors=None):
        
        pcnt = mesh.GetPointCount()
        unic = False
        useProxy=True
        createV=True
        createM=True
        colsc = 1.0
        
        if vcolors is None : 
            vcolors=[c4d.Vector(0.,0.,0.),]*pcnt
            unic= True
        else :
            #print "vcolors", len(vcolors)
            if len(vcolors) == 1:
                unic= True
        useProxy=False
        
        if mesh.GetTag(c4d.Ttexture) != None :
            createM=False
        
        for j in range(3):
            createV=True
            vFirstTag = mesh.GetFirstTag()
            vLastTag = None;
            if (j==0) : vColor = "_Red"
            if (j==1) : vColor = "_Green"
            if (j==2) : vColor = "_Blue"
            tagName = vColor #MoleculeName +
            
            while (vFirstTag is not None) : 
                vLastTag = vFirstTag
                if vLastTag.GetName() == tagName : 
                    createV=False
                    vtag = vLastTag
                    break
                vFirstTag = vFirstTag.GetNext()
            if createV : 
                vtag = mesh.MakeVariableTag(c4d.Tvertexmap,pcnt,vLastTag)
                vtag.SetName(tagName)
            if vtag is None : 
                return False
            
            mesh.Message(c4d.MSG_UPDATE)
            #get the vertex map tag's size (should be same as vertex (point) count
            vcnt = vtag.GetDataCount()
            #get the pointer to the vertex map array
            vmap = vtag.GetAllHighlevelData()
            vmap=[self.setVColor(j,y) for y in vcolors]
#            vmap=map(lambda x,y,j=j: setVColor(x,j,y),vmap,vcolors)
            vtag.SetAllHighlevelData(vmap)
            vtag.Message(c4d.MSG_UPDATE)
            c4d.EventAdd()
            if createM :
                MatMemb=self.CreateVertexColorMaterials(0, mesh, vtag)
                MatTag = c4d.TextureTag()
                if (MatTag) :
                    MatTag.SetMaterial(MatMemb)
                    if j != 0 : 
                        MatTag[c4d.TEXTURETAG_MIX]= 1
                    mesh.InsertTag(MatTag, vLastTag)
    
    def CreateVertexColorMaterials(self,ID_MEMBMAT, pPolyObject, vtag):
        vColor = vtag.GetName()
        Mat = c4d.BaseMaterial(c4d.Mmaterial)
        Mat.SetName(vColor)
        
        Mat[c4d.MATERIAL_COLOR_COLOR] = c4d.Vector(0.902, 0.730,0.659)
    #    MatMemb->SetParameter(MATERIAL_COLOR_COLOR, Vector(0.902, 0.730,0.659), NULL);
    #    MatMemb->SetParameter(MATERIAL_USE_TRANSPARENCY, 1, NULL);
    #    MatMemb->SetParameter(MATERIAL_USE_BUMP, 1, NULL);
    #    MatMemb->SetParameter(MATERIAL_BUMP_STRENGTH, 0.25, NULL);
        Mat[c4d.MATERIAL_TRANSPARENCY_BRIGHTNESS] = 0.2
        Mat[c4d.MATERIAL_SPECULAR_WIDTH] = 0.29
    #    MatMemb->SetParameter(MATERIAL_SPECULAR_HEIGHT, 0.65, NULL);
        data = Mat.GetDataInstance()
        
        col = c4d.BaseList2D(c4d.Xfusion)
        blend = c4d.BaseList2D(c4d.Xcolor)
        
        blenddata = blend.GetDataInstance()
        #Set here your texture path, relative or absolute doesn't matter
        if vColor == "_Red" : 
            blenddata.SetData(c4d.COLORSHADER_COLOR, c4d.Vector(1, 0, 0) )
        if vColor == "_Green" :
            blenddata.SetData(c4d.COLORSHADER_COLOR, c4d.Vector(0, 1, 0) )
        if vColor == "_Blue" : 
            blenddata.SetData(c4d.COLORSHADER_COLOR, c4d.Vector(0, 0, 1) )
        blend.Message(c4d.MSG_UPDATE)
        Mat.InsertShader(blend)
        
        mask = c4d.BaseList2D(c4d.Xvertexmap)
        base = c4d.BaseList2D(c4d.Xcolor)
        
        maskdata = mask.GetDataInstance()
        objParent = pPolyObject
        objTag = vtag
        maskdata.SetLink(c4d.SLA_DIRTY_VMAP_OBJECT, objTag)
        mask.Message(c4d.MSG_UPDATE)
        data.SetLink(c4d.MATERIAL_BUMP_SHADER, mask)
        Mat.InsertShader(mask)
        basedata = base.GetDataInstance()
        basedata.SetData(c4d.COLORSHADER_COLOR, c4d.Vector(0, 0, 0) )
        base.Message(c4d.MSG_UPDATE)
        Mat.InsertShader(base)    
    
        coldata = col.GetDataInstance()
        #Set here your texture path, relative or absolute doesn't matter
        coldata.SetData(c4d.SLA_FUSION_USE_MASK, 1) 
        coldata.SetLink(c4d.SLA_FUSION_BLEND_CHANNEL, blend)
        coldata.SetLink(c4d.SLA_FUSION_MASK_CHANNEL, mask)
        coldata.SetLink(c4d.SLA_FUSION_BASE_CHANNEL, base)
        col.Message(c4d.MSG_UPDATE)
        data.SetLink(c4d.MATERIAL_COLOR_SHADER, col)
        Mat.InsertShader(col)
    
        Mat.Message(c4d.MSG_UPDATE)
        Mat.Update(True, True)
        c4d.EventAdd()
        
        doc = c4d.documents.GetActiveDocument()
        doc.InsertMaterial(Mat)
        doc.AddUndo( c4d.UNDO_NEW, Mat )
        return Mat
        
    def colorbyvertex(self,mesh,proxy=None,vcolors=None):
        if mesh.GetTag(c4d.Tphong)==None :  
            mesh.MakeTag(c4d.Tphong)
        if mesh.GetTag(c4d.Tbaketexture)==None :
            vBakeTexTag =   mesh.MakeTag(c4d.Tbaketexture)
            vBakeTexTag[c4d.BAKETEXTURE_CHANNEL_COLOR] = 0
            vBakeTexTag[c4d.BAKETEXTURE_CHANNEL_S_COLOR] = 1 
            vBakeTexTag[c4d.BAKETEXTURE_MAPPING] = c4d.BAKETEXTURE_MAPPING_CUBIC
            vBakeTexTag[c4d.BAKETEXTURE_PIXELBORDER] = 3
            vBakeTexTag[c4d.BAKETEXTURE_BACKGROUND] = c4d.Vector(0.6,1.0,0.0)
            vBakeTexTag[c4d.BAKETEXTURE_RELAXCOUNT]=2
            vBakeTexTag.Message(c4d.MSG_UPDATE)
            c4d.EventAdd()
        self.CreateVertexRGBmaps(mesh,proxy,vcolors)
        doc = c4d.documents.GetActiveDocument()
        doc.AddUndo( c4d.UNDO_NEW, mesh )
    
    def colorMaterial(self,mat,col):
        #mat input is a material name or a material object
        #color input is three rgb value array
        if col == None:
            return
        doc= c4d.documents.GetActiveDocument()
        if type(mat)==str : 
            material = doc.SearchMaterial(mat)
            if material is None :
                material = self.addMaterial(mat,col)
            mat = material
        mat[2100] = c4d.Vector(col[0],col[1],col[2])

    def c4dColor(self,col):
            #c4d color rgb range[0-1]
            if max(col)>1.0: 
                col = [ (x/255.) for x in col ]
#                col = map( lambda x: x/255., col)
            return col
            
    def changeColor(self,obj,colors,perVertex=False,proxyObject=True,doc=None,pb=False,
                    facesSelection=None,faceMaterial=False):
#        print colors
        if colors[0] is not list and len(colors) == 3 :
           colors = [colors,]
#        print colors
        if doc == None : 
            doc = self.getCurrentScene()
        if type(obj) == str:
            obj = self.getMesh(obj)
        print obj,self.getName(obj)
        if self.getType(obj) != self.POLYGON:
            proxyObject=False
        defaultColor=(0.25,0.25,0.25)
        doProxy = False
        #verfify perVertex flag
        unic=False
        ncolor=self.convertColor(colors[0],toint=False)
        if len(colors)==1 :
            unic=True
            ncolor = self.convertColor(colors[0],toint=False)
        proxy = None
        vcolor = None
        #lets not doing it for see
        if proxyObject :     
            nf=obj.GetPolygonCount()
            nv=obj.GetPointCount()
            mfaces = obj.GetAllPolygons() 
            if  facesSelection is not None :
                if type(facesSelection) is bool :
                    fsel,face_sel_indice = self.getMeshFace(obj,selected=True)
                else :
                    face_sel_indice = facesSelection
                    fsel=[]
                    for i in face_sel_indice:
                        fsel.append(mfaces[i])
                vsel=[]
                for f in fsel:
                    for v in f:
                        if v not in vsel:
                            vsel.append(v)
                mfaces = fsel
                nf = len(fsel)
                nv = len(vsel)
            if len(colors) != nv and \
                len(colors) == nf: 
                    perVertex=False
            if len(colors) == nv and \
                len(colors) != nf: 
                    perVertex=True
            #get the list of color in c4d format
            vcolor = [c4d.Vector(0.25,0.25,0.25)]*obj.GetPointCount() #default color is grey
            #if DEBUG : 
            #print "nb Faces ",len(faces)
            if pb :
                self.resetProgressBar()
                self.progressBar(label="color per Vertex : convert Color to C4D")
            for i,g in enumerate(mfaces):#faces
                if not unic and not perVertex : 
                    ncolor = self.convertColor(colors[i],toint=False)
                elif unic : 
                    ncolor = self.convertColor(colors[0],toint=False)
                for j in [g.a,g.b,g.c,g.d]:#vertices
                    if not unic and perVertex : 
                        ncolor = self.convertColor(colors[j],toint=False)
#                    print j,ncolor
                    vcolor[j] = c4d.Vector(float(ncolor[0]), 
                                            float(ncolor[1]), 
                                            float(ncolor[2]))
                if pb :
                    self.progressBar(progress = float(i)/float(len(faces)))
            if pb :
               self.progressBar(label="color per Vertex : create Vmap Tag") 
            self.colorbyvertex(obj,proxy,vcolor)
            if pb :
                self.resetProgressBar()
        else :
            self.changeObjColorMat(obj,ncolor)
            texture = obj.GetTags()[0] #should be the textureFlag
    
    def changeObjColorMat(self,obj,color):
        doc = self.getCurrentScene()
#        texture = obj.GetTags()[0]
        texture = obj.GetTag(c4d.Ttexture)
        if texture is None :
            texture = obj.MakeTag(c4d.Ttexture)
        rMat=texture[c4d.TEXTURETAG_MATERIAL]
        if rMat is None :
            rMat = self.addMaterial("mat_"+self.getName(obj),color)
            texture[c4d.TEXTURETAG_MATERIAL] = rMat
        else :  
            self.colorMaterial(rMat,color)
        
    def armature(self,basename,x,listeName=None,scn=None,root=None,**kw):
        bones=[]
#        mol = x[0].top
        center = [0,0,0]#self.getCenter(x)
#        if scn != None:
        parent = c4d.BaseObject(c4d.Onull)
        parent.SetName(basename)
        self.addObjectToScene(scn,parent,parent=root)
        for j in range(len(x)):    
            name = basename+'bone'+str(j)
            if listeName is not None:
                name = listeName[j]
            atC=x[j]
            bones.append(c4d.BaseObject(self.BONE))
            bones[j].SetName(name)
            relativePos=[0.,0.,0.]
            if j>0 :
                patC=x[j-1]
                for i in range(3):relativePos[i]=(atC[i]-patC[i])
            else : #the first atom
                #relative should be against the master
#                center=Numeric.array(center)
                for i in range(3):relativePos[i]=(atC[i]-center[i])#??
            bones[j].SetAbsPos(self.FromVec(relativePos))
            mx = c4d.Matrix()
            mx.off = self.FromVec(atC)
            bones[j].SetMg(mx)
#            if scn != None :
            if j==0 : self.addObjectToScene(scn,bones[j],parent=parent)
            else : self.addObjectToScene(scn,bones[j],parent=bones[j-1])     
        return parent,bones
    
    def bindGeom2Bones(self,listeObject,bones,delete=False):
        """
        Make a skinning. Namely bind the given bones to the given list of geometry.
        This function will joins the list of geomtry in one geometry
        
        @type  listeObjects: list
        @param listeObjects: list of object to joins
        @type  bones: list
        @param bones: list of joins
        """    
        
        if len(listeObject) >1:
            self.JoinsObjects(listeObject,delete=delete)
        else :
            self.ObjectsSelection(listeObject,"new")
        #2- add the joins to the selection
        self.ObjectsSelection(bones,"add")
        #3- bind the bones / geoms
        c4d.CallCommand(self.BIND)

    def metaballs(self,name,listePt,listeR,scn=None,root=None,**kw):
        doc = self.getCurrentScene()
        cloud = self.PointCloudObject(name+"_cloud",
                                        vertices=listePt,
                                        parent=root,atomarray=False)[0]
        metab=self.create_metaballs(name,sourceObj=cloud,parent=root)
        return metab,cloud

    def create_metaballs(self,name,sourceObj=None,source="",parent=None,coords=None):
        doc = self.getCurrentScene()
        metab = c4d.BaseObject(c4d.Ometaball)
        metab.SetName(name)
        metab[c4d.METABALLOBJECT_EXPONENTIAL] = 1
        metab[c4d.METABALLOBJECT_THRESHOLD] = 0.1 #Hull Value
        metab[c4d.METABALLOBJECT_SUBEDITOR] = 2
        metab[c4d.METABALLOBJECT_SUBRAY] =  2
        metab.MakeTag(c4d.Tphong)
        self.addObjectToScene(doc,metab,parent=parent)
        #radius ?
        #get the could from mol
        if source :
            if source == "clouds" :
                cloud = self.getObject(name+"_cloud")
                if cloud is None :
                    cloud = self.PointCloudObject(name+"_cloud",
                                                vertices=coords,
                                                parent=metab,atomarray=False)[0]
                else :#insertUnder Metaball Object
                    self.reParent(cloud,metab)
                #add the metaball Tag
                tag = cloud.MakeTag(c4d.Tmetaball)
                tag[c4d.METABALLTAG_RADIUS] = 1.0
    #            return metab
            elif sourceObj == "cpk":
                self.cpk_metaballs(name,coords,scn=doc,root=parent)
        elif sourceObj is not None :
            self.reParent(sourceObj,metab)
            tag = sourceObj.MakeTag(c4d.Tmetaball)
            tag[c4d.METABALLTAG_RADIUS] = 1.0
            #tag[c4d.METABALLTAG_STRENGTH]
        return metab
    
    def cpk_metaballs(self,name,atoms,scn=None,root=None):
        if scn == None:
            scn = self.getCurrentScene()
        parent = c4d.BaseObject(c4d.Onull)
        parent.SetName(name)
        self.addObjectToScene(scn,parent,parent=root)
        #mol = atoms[0].top
        #copy of the cpk ?-> point cloud is nice too...
        #create the metaball objects child of the null
        meta=c4d.BaseObject(self.METABALLS)
        self.addObjectToScene(scn,meta,parent=parent)
        #change the metaball parameter
        meta[1000]=9.0#Hull Value
        meta[1001]=0.5#editor subdivision
        meta[1002]=0.5#render subdivision    
        #coloring ?
        return meta,parent

    def getBoxSize(self,obj):
        #take degree
        obj = self.getObject(obj)
        if obj is None :
            return
        return obj[1100]
    
    def box(self,name,center=[0.,0.,0.],size=[1.,1.,1.],cornerPoints=None,visible=1,
                              mat = None,**kw):
        #import numpy
        box=c4d.BaseObject(c4d.Ocube)#Object.New('Mesh',name)
        box.SetName(name)
        if cornerPoints != None :
            for i in range(3):
                size[i] = cornerPoints[1][i]-cornerPoints[0][i]
            for i in range(3):
                center[i]=(cornerPoints[0][i]+cornerPoints[1][i])/2.
        box.SetAbsPos(self.FromVec(center))
        box[1100] = self.FromVec(size)
        #aMat=addMaterial("wire")
        texture = box.MakeTag(c4d.Ttexture)
        if mat == None:
            texture[1010] = self.addMaterial("cube",[1.,1.,0.])
        else :
            texture[1010] = mat
        parent= None
        if "parent" in kw :
            parent = kw["parent"]
        self.addObjectToScene(self.getCurrentScene(),box,parent=parent)
        box[c4d.ID_BASEOBJECT_XRAY] = bool(visible)     
        return box,box

    def updateBox(self,box,center=[0.,0.,0.],size=[1.,1.,1.],cornerPoints=None,visible=1,
                              mat = None):
        #import numpy
        box=self.getObject(box)
        if cornerPoints != None :
            for i in range(3):
                size[i] = cornerPoints[1][i]-cornerPoints[0][i]
            for i in range(3):
                center[i]=(cornerPoints[0][i]+cornerPoints[1][i])/2.
        box.SetAbsPos(self.FromVec(center))
        box[1100] = self.FromVec(size)
        #aMat=addMaterial("wire")
#        texture = box.MakeTag(c4d.Ttexture)
#        if mat == None:
#            texture[1010] = self.addMaterial("cube",[1.,1.,0.])
#        else :
#            texture[1010] = mat
#        self.addObjectToScene(self.getCurrentScene(),box)
#        return box

#    def getCornerPointCube(self,obj):
#        size = obj[1100]
#        center = obj.GetAbsPos()
#        cornerPoints=[]
#        #lowCorner
#        lc = [center.x - size.x/2.,
#              center.y - size.y/2.,
#              center.z - size.z/2.]
#        uc = [center.x + size.x/2.,
#              center.y + size.y/2.,
#              center.z + size.z/2.]
#        cornerPoints=[[lc[2],lc[1],lc[0]],[uc[2],uc[1],uc[0]]]
#        return cornerPoints

    def plane(self,name,center=[0.,0.,0.],size=[1.,1.],cornerPoints=None,visible=1,**kw):
        #import numpy
        plane=c4d.BaseObject(c4d.Oplane)#Object.New('Mesh',name)
        plane.SetName(name)
        if cornerPoints != None :
            for i in range(3):
                size[i] = cornerPoints[1][i]-cornerPoints[0][i]
            for i in range(3):
                center[i]=(cornerPoints[0][i]+cornerPoints[1][i])/2.
        plane.SetAbsPos(self.FromVec(center))
        
        plane[c4d.PRIM_PLANE_WIDTH] = size[0]
        plane[c4d.PRIM_PLANE_HEIGHT] = size[1]
        
        if "subdivision" in kw :
            plane[c4d.PRIM_PLANE_SUBW] = kw["subdivision"][0]
            plane[c4d.PRIM_PLANE_SUBH] = kw["subdivision"][1]
        
        if "axis" in kw : #orientation
            dic = {"+X":0,"-X":1,"+Y":2,"-Y":3,"+Z":4,"-Z":5}
            if type(kw["axis"]) is str :
                axis = dic[kw["axis"]]
            else : 
                axis = kw["axis"]
            plane[c4d.PRIM_AXIS]=axis
        else :
            plane[c4d.PRIM_AXIS]=1
        if "material" in kw :
            texture = plane.MakeTag(c4d.Ttexture)
            if type(kw["material"]) is c4d.BaseMaterial :
                texture[1010] = kw["material"]
            else :
                texture[1010] = self.addMaterial("plane",[1.,1.,0.])           
        parent = None
        if "parent" in kw :
            parent = kw["parent"]
        self.addObjectToScene(self.getCurrentScene(),plane,parent=parent)
        return plane,plane


    def Platonic(self,name,Type,radius,**kw):
        dicT={"tetra":0,
              "hexa":1,
              "octa":2,
              "dodeca":3,
              "icosa":4}#BuckyBall ?
        dicTF={4:0,
              6:1,
              8:2,
              12:3,
              20:4}
        platonic  = c4d.BaseObject(self.PLATONIC)       
        platonic.SetName(name)
        if Type in dicT  :
            platonic[c4d.PRIM_PLATONIC_TYPE] = dicT[Type]
        elif Type in dicTF :
            platonic[c4d.PRIM_PLATONIC_TYPE] = dicTF[Type]    
        platonic[c4d.PRIM_PLATONIC_RAD] = radius
        parent= None
        if "parent" in kw :
            parent = kw["parent"]        
        self.addObjectToScene(self.getCurrentScene(),platonic,parent=parent)
        if "material" in kw :
            texture = platonic.MakeTag(c4d.Ttexture)
            if type(kw["material"]) is c4d.BaseMaterial :
                texture[1010] = kw["material"]
            else :
                texture[1010] = self.addMaterial(name+"_mat",[1.,1.,0.])          
        return platonic,platonic

    def alignNormal(self,poly):
        #select poly
        doc = self.getCurrentScene()
        doc.SetActiveObject(poly)
        c4d.CallCommand(14023)#alignNormal

    def triangulate(self,poly):
        #select poly
        doc = self.getCurrentScene()
        doc.SetActiveObject(poly)
        c4d.CallCommand(14048)#triangulate
        
    def makeEditable(self,object,copy=True):
        doc = self.getCurrentScene()
        #make a copy?
        if object is None : 
            return
        if copy:
            clone = object.GetClone()
            clone.SetName(object.GetName()+"clone")
            doc.InsertObject(clone)
            doc.SetActiveObject(clone)
            c4d.CallCommand(12236)#make editable can create a child
            clone.Message(c4d.MSG_UPDATE)
            clone = self.getObject(object.GetName()+"clone")
            print clone.GetType(),clone.GetType() == c4d.Oinstance
            if clone.GetType() != self.POLYGON :
                print "do editable"
                c4d.CallCommand(12236)#make editable   
                clone = self.getObject(object.GetName()+"clone")
#            print clone
            return clone
        else :
            if object.GetType() != self.POLYGON  :
                doc.SetActiveObject(object)
                c4d.CallCommand(12236)
                object.Message(c4d.MSG_UPDATE)
#                object = self.getObject(object.GetName())
                if object.GetType() != self.POLYGON  :
                    #should wedo it recursivey untilfindn a polygon?
                    #chec the child
                    ch=self.getChilds(object)
                    if len(ch) != 0 :
                        object = ch[0]                        
                        if object.GetType() != self.POLYGON  :
                            doc.SetActiveObject(object)
                            c4d.CallCommand(12236)#make editable             
                            object.Message(c4d.MSG_UPDATE)
#                            object = self.getObject(ch[0].GetName())
                            ch=self.getChilds(object)
                            if len(ch) != 0 : 
                                object = self.makeEditable(ch[0],copy=False)
            return object

#    def getMeshVertices(self,poly,selected=False):
#        c4dvertices = poly.GetAllPoints()
#        if selected :
#            sel= poly.GetPointS()
#            nv = poly.GetPointCount()
#            point_index = [i for i,e in enumerate(sel.GetAll(nv)) if e == 1]
#            vertices = [self.ToVec(c4dvertices[v]) for v in point_index]
#            return vertices,point_index
#        else :
#            vertices = map(self.ToVec,c4dvertices)
#            return vertices
#        
    def getMeshNormales(self,poly,selected=False):
        c4dvnormals = poly.CreatePhongNormals()
        vnormals=vertices[:]
        for i,f in enumerate(faces):
            #one face : 4 vertices
            for k,j in enumerate(f):
                #print i,j,(i*4)+k
                vnormals[j] = self.ToVec(c4dvnormals[(i*4)+k])
        return vnormals

    def getMeshEdge(self,c4dedge):
        return None#[c4dedge.a,c4dedge.b]
            
    def getMeshEdges(self,poly,selected=False):
        return None
#        c4dedges = object.GetEdge()
#        faces = [self.getMeshEdge(e) for e in c4dedges]
#        return faces
        
    def getFace(self,c4dface,r=True,**kw):
        if r :
            if c4dface.c == c4dface.d:
                return [c4dface.c,c4dface.b,c4dface.a]
            else :
                return [c4dface.d,c4dface.c,c4dface.b,c4dface.a]
        else :
            if c4dface.c == c4dface.d:
                return [c4dface.a,c4dface.b,c4dface.c]
            else :
                return [c4dface.a,c4dface.b,c4dface.c,c4dface.d]
            
    def getFaces(self,object,selected=False):
        print object,object.GetName()
        c4dfaces = object.GetAllPolygons()
        if selected :
            nf = object.GetPolygonCount()
            sel= object.GetPolygonS()
            c4dfaces_index = [i for i,e in enumerate(sel.GetAll(nf)) if e == 1] #only want wen val = 1
            faces = [self.getFace(c4dfaces[f]) for f in c4dfaces_index]
            return faces,c4dfaces_index
        else :
            c4dfaces = object.GetAllPolygons()
            faces = [self.getFace(f) for f in c4dfaces]
            return faces
        
    def getMeshFaces(self,poly,selected=False):
        return self.getFaces(poly,selected=selected)


    #################################################################################
#    def setupAmber(mv,name,mol,prmtopfile, type,add_Conf=True,debug = False):
#        if not hasattr(mv,'setup_Amber94'):
#            mv.browseCommands('amberCommands', package='Pmv')
#        from Pmv import amberCommands
#        amberCommands.Amber94Config = {}
#        amberCommands.CurrentAmber94 = {}
#    
#        mv.energy = C.EnergyHandler(mv)
#        mv.energy.amber = True
#        mv.energy.mol = mol
#        mol.prname = prmtopfile
#        mv.energy.name=name    
#        def doit():
#            c1 = mv.minimize_Amber94
#            c1(name, dfpred=10.0, callback_freq='10', callback=1, drms=1e-06, maxIter=10, log=0)
#        mv.energy.doit=doit
#        if add_Conf:
#                confNum = 1
#                # check number of conformations available
#                current_confNum = len(mol.allAtoms[0]._coords) -1
#                if  current_confNum < confNum:
#                    # we need to add conformation
#                    for i in range((confNum - current_confNum)):
#                        mol.allAtoms.addConformation(mol.allAtoms.coords)
#                        # uses the conformation to store the transformed data
#                        #mol.allAtoms.updateCoords(vt,ind=confNum)
#                        # add arconformationIndex to top instance ( molecule)
#                        mol.cconformationIndex = confNum
#        mv.setup_Amber94(mol.name+":",name,prmtopfile,indice=mol.cconformationIndex)
#        mv.minimize_Amber94(name, dfpred=10.0, callback_freq='10', callback=1, drms=1e-06, maxIter=100., log=0)    
#        
#    def cAD3Energies(mv,mols,atomset1,atomset2,add_Conf=False,debug = False):
#        mv.energy = C.EnergyHandler(mv)
#        mv.energy.add(atomset1,atomset2)#type=c_ad3Score by default
#        #mv.energy.add(atomset1,atomset2,type = "ad4Score")
#        if add_Conf:
#            confNum = 1
#            for mol in mols:
#                # check number of conformations available
#                current_confNum = len(mol.allAtoms[0]._coords) -1
#                #if  current_confNum < confNum:
#                # we need to add conformation
#                #for i in range((confNum - current_confNum)):
#                mol.allAtoms.addConformation(mol.allAtoms.coords)
#                        # uses the conformation to store the transformed data
#                        #mol.allAtoms.updateCoords(vt,ind=confNum)
#                        # add arconformationIndex to top instance ( molecule)
#                mol.cconformationIndex = len(mol.allAtoms[0]._coords) -1
#        if debug :
#            s1=c4d.BaseObject(c4d.Osphere)
#            s1.SetName("sphere_rec")
#            s1[PRIM_SPHERE_RAD]=2.
#            s2=c4d.BaseObject(c4d.Osphere)
#            s2.SetName("sphere_lig")
#            s2[PRIM_SPHERE_RAD]=2.
#            addObjectToScene(getCurrentScene(),s1)
#            addObjectToScene(getCurrentScene(),s2)        
#            #label
#            label = newEmpty("label")
#            label.MakeTag(LOOKATCAM)
#            addObjectToScene(getCurrentScene(),label)
#            text1 =  c4d.BaseObject(TEXT)
#            text1.SetName("score")
#            text1[2111] = "score : 0.00"
#            text1[2115] = 5.
#            text1[904,1000] = 3.14
#            text1[903,1001] = 4.
#            text2 =  c4d.BaseObject(TEXT)
#            text2.SetName("el")
#            text2[2111] = "el : 0.00"
#            text2[2115] = 5.0
#            text2[904,1000] = 3.14
#            text3 =  c4d.BaseObject(TEXT)
#            text3.SetName("hb")
#            text3[2111] = "hb : 0.00"
#            text3[2115] = 5.0
#            text3[904,1000] = 3.14
#            text3[903,1001] = -4.
#            text4 =  c4d.BaseObject(TEXT)
#            text4.SetName("vw")
#            text4[2111] = "vw : 0.00"
#            text4[2115] = 5.0
#            text4[904,1000] = 3.14
#            text4[903,1001] = -8.
#            text5 =  c4d.BaseObject(TEXT)
#            text5.SetName("so")
#            text5[2111] = "so : 0.00"
#            text5[2115] = 5.0
#            text5[904,1000] = 3.14
#            text5[903,1001] = -12.
#            addObjectToScene(getCurrentScene(),text1,parent=label)
#            addObjectToScene(getCurrentScene(),text2,parent=label)
#            addObjectToScene(getCurrentScene(),text3,parent=label)
#            addObjectToScene(getCurrentScene(),text4,parent=label)
#            addObjectToScene(getCurrentScene(),text5,parent=label)       
#        #return energy
#    
#    def changeColorO(self,object,colors):
#        object.GetTags()[0][1010][2100]= c4d.Vector( colors[0],colors[1],colors[2])
#    
#    def colorByEnergy(vf,atomSet,scorer,property):
#        mini = min(getattr(atomSet,scorer.prop))
#        #geomsToColor = vf.getAvailableGeoms(scorer.mol2)
#        vf.colorByProperty(atomSet,['cpk'],property,
#                                mini=-1.0, maxi=1.0,
#                                colormap='rgb256',log=1)#,
#    #                            createEvents=False)
#        #then i should manually apply all the color on sph
#    #    mol = atomSet[0].getParentOfType(Protein)
#    #    sph = mol.geomContainer.geoms['cpk'].obj
#    #    #should change the material color for all sph.obj
#    #    #map or new function ?
#    ##    map( lambda x.foo, list)
#    ##    by
#    ##    [x.foo for x in list]
#    #    #map(lambda x,y: x.GetTags()[0][1010][2100]= c4d.Vector( y.colors['cpk'][0],y.colors['cpk'][1],y.colors['cpk'][2]),sph,atomSet)
#    #    #for i,atm in enumerate(atomSet):
#    #    #    sph[i].GetTags()[0][1010][2100]= c4d.Vector( atm.colors['cpk'][0],atm.colors['cpk'][1],atm.colors['cpk'][2])
#    #    [changeColorO(x,a.colors['cpk']) for x,a in zip(sph,atomSet)]
#        #col = atomSet[0].colors['cpk']
#        #mat = o.GetTags()[0][1010][2100] = c4d.Vector(col[0],col[1],col[2])
#        
##    def get_nrg_score(energy,display=True):
#        #print "get_nrg_score"
#        status = energy.compute_energies()
#        print status
#        if status is None: return
#        #print energy.current_scorer
#        print energy.current_scorer.score
#        vf = energy.viewer
#        if energy.label:
#            text = getObject("score")
#            if text != None :
#                text[2111] = "score :"+str(energy.current_scorer.score)[0:5]
#                for i,term in enumerate(['el','hb','vw','so']):
#                    labelT = getObject(term)
#                    labelT[2111] = term+" : "+str(energy.current_scorer.scores[i])[0:5]
#        #should make multi label for multi terms    
#        # change color of ligand with using scorer energy
#        if energy.color[0] or energy.color[1] :
#            # change selection level to Atom
#            prev_select_level = vf.getSelLev()
#            vf.setSelectionLevel(Atom,log=0)
#            scorer = energy.current_scorer
#            property = scorer.prop
#            if energy.color[0] :
#                atomSet1 = vf.expandNodes(scorer.mol1.name).findType(Atom) # we pick the rec
#                if hasattr(atomSet1,scorer.prop):
#                    colorByEnergy(vf,atomSet1,scorer,property)
#            if energy.color[1] :
#                atomSet2 = vf.expandNodes(scorer.mol2.name).findType(Atom) # we pick the ligand
#                if hasattr(atomSet2,scorer.prop):
#                    colorByEnergy(vf,atomSet2,scorer,property)
#                # get the geometries of colormap to be display
#                #if vf.colorMaps.has_key('rgb256'):
#                    #cmg = vf.colorMaps['rgb256']
#                    #from DejaVu.ColormapGui import ColorMapGUI
#                    #if not isinstance(cmg,ColorMapGUI):
#                    #    cmg.read(self.colormap_file)
#                    #    self.vf.showCMGUI(cmap=cmg, topCommand=0)
#                    #    cmg = self.vf.colorMaps['rgb256']
#                    #    cmg.master.withdraw()
#                        # create the color map legend
#                    #    cmg.createCML()
#                        
#                    #cml = cmg.legend
#                    #cml.Set(visible=True,unitsString='kcal/mol')
#                    #if cml not in self.geom_without_pattern:
#                    #    self.geom_without_pattern.append(cml)
    #################################################################################
    
#    def updateLigCoord(mol):
#        #fake update...reset coord to origin
#        mol.allAtoms.setConformation(0)
#        #get the transformation
#        name = mol.geomContainer.masterGeom.chains_obj[mol.chains[0].name]
#        mx = getObject(name).get_ml()
#        mat,imat = c4dMat2numpy(mx)
#        vt = C.transformedCoordinatesWithMatrice(mol,mat)
#        mol.allAtoms.updateCoords(vt,ind=mol.cconformationIndex)
#        #coords = mol.allAtoms.coords        
#        #mol.allAtoms.updateCoords(coords,ind=mol.cconformationIndex)
#        mol.allAtoms.setConformation(0)
    

        
    ##############################AR METHODS#######################################
    def ARstep(mv):
        #from Pmv.hostappInterface import comput_util as C
        mv.art.beforeRedraw()
        #up(self,dialog)
        for arcontext in mv.art.arcontext :
            for pat in arcontext.patterns.values():
                if pat.isdetected:
                    #print pat
                    geoms_2_display = pat.geoms
                    transfo_mat = pat.mat_transfo[:]
                    #print transfo_mat[12:15]
                    for geom in geoms_2_display :
                            if hasattr(pat,'offset') : offset = pat.offset[:]
                            else : offset =[0.,0.,0.]
                            transfo_mat[12] = (transfo_mat[12]+offset[0])* mv.art.scaleDevice
                            transfo_mat[13] = (transfo_mat[13]+offset[1])* mv.art.scaleDevice
                            transfo_mat[14] = (transfo_mat[14]+offset[2])* mv.art.scaleDevice
                            mat = transfo_mat.reshape(4,4)
                            model = geom.obj
    #                        print obj.GetName()
                            #r,t,s = C.Decompose4x4(Numeric.array(mat).reshape(16,))
                            #print t
                            #newPos = c4dv(t)
                            #model.SetAbsPos(newPos)
                            #model.Message(c4d.MSG_UPDATE)
                            setObjectMatrix(model,mat)
                            #updateAppli()
     
    def ARstepM(mv):
        #from Pmv.hostappInterface import comput_util as C
        from mglutil.math import rotax
        mv.art.beforeRedraw()
        #up(self,dialog)
        for arcontext in mv.art.arcontext :
            for pat in arcontext.patterns.values():
                if pat.isdetected:
                    #print pat
                    geoms_2_display = pat.geoms
    
                    #m = pat.mat_transfo[:]#pat.moveMat[:]
                    if mv.art.concat : 
                        m = pat.moveMat[:].reshape(16,)
                    else :
                        m = pat.mat_transfo[:].reshape(16,)
                    #print transfo_mat[12:15]
                    for geom in geoms_2_display :
                        scale = float(mv.art.scaleObject)
                        model = geom.obj
                        if mv.art.patternMgr.mirror:
                            #apply scale transformation GL.glScalef(-1.,1.,1)
                            scaleObj(model,[-1.,1.,1.])
                        if mv.art.concat :
                            if hasattr(pat,'offset') : offset = pat.offset[:]
                            else : offset =[0.,0.,0.]
                            m[12] = (m[12]+offset[0])#* mv.art.scaleDevice
                            m[13] = (m[13]+offset[1])#* mv.art.scaleDevice
                            m[14] = (m[14]+offset[2])#* mv.art.scaleDevice
                            newMat=rotax.interpolate3DTransform([m.reshape(4,4)], [1], 
                                                            mv.art.scaleDevice)
                            concatObjectMatrix(model,newMat)
                        else :
                            if hasattr(pat,'offset') : offset = pat.offset[:]
                            else : offset =[0.,0.,0.]
                            m[12] = (m[12]+offset[0])* mv.art.scaleDevice
                            m[13] = (m[13]+offset[1])* mv.art.scaleDevice
                            m[14] = (m[14]+offset[2])* mv.art.scaleDevice
                            #r1=m.reshape(4,4)
                            #newMat=rotax.interpolate3DTransform([r1], [1], 
                            #                                mv.art.scaleDevice)
                            #m[0:3][0:3]=newMat[0:3][0:3]
                            setObjectMatrix(model,m.reshape(4,4))
                        scaleObj(model,[scale,scale,scale])
                        #updateAppli()
     
    def ARloop(mv,ar=True,im=None,ims=None,max=1000):
        count = 0    
        while count < max:
            #print count
            if im is not None:
                updateImage(mv,im,scale=ims)
            if ar : 
                ARstep(mv)
            update()
            count = count + 1
    
    def AR(mv,v=None,ar=True):#,im=None,ims=None,max=1000):
        count = 0    
        while 1:
            #print count
            if v is not None:
                #updateBmp(mv,bmp,scale=None,show=False,viewport=v)
                updateImage(mv,viewport=v)
            if ar : 
                ARstepM(mv)
            #update()
            count = count + 1
    
    
    Y=range(480)*640
    Y.sort()
    
    X=range(640)*480
    
    
    #import StringIO
    #im = Image.open(StringIO.StringIO(buffer))
    #helper.updateImage(self,viewport=Right,order=[1, 2, 3, 1])
    def updateImage(mv,viewport=None,order=[1, 2, 3, 1]):
        #debug image is just white...
        try :
            if viewport is not None :
                viewport[c4d.BASEDRAW_DATA_SHOWPICTURE] = bool(mv.art.AR.show_tex)
            import Image
            cam = mv.art.arcontext[0].cam
            cam.lock.acquire()
            #print "acquire"
            #arcontext = mv.art.arcontext[0]
            #array = Numeric.array(cam.im_array[:])    
            #n=int(len(array)/(cam.width*cam.height))
            if mv.art.AR.debug : 
                array = cam.imd_array[:]#.tostring()
                #print "debug",len(array)
            else :
                array = cam.im_array[:]#.tostring()
                #print "normal",len(array)
            #img=Numeric.array(array[:])
            #n=int(len(img)/(arcontext.cam.width*arcontext.cam.height))
            #img=img.reshape(arcontext.cam.height,arcontext.cam.width,n)
            #if n == 3 : 
            #    mode = "RGB"
            #else : 
            #    mode = "RGBA"
            #im = Image.fromarray(img, mode)#.resize((160,120),Image.NEAREST).transpose(Image.FLIP_TOP_BOTTOM)
            im = Image.fromstring("RGBA",(mv.art.video.width,mv.art.video.height),
                                  array.tostring() ).resize((320,240),Image.NEAREST)
            #cam.lock.release()
            #scale/resize image ?
            #print "image"
            rgba = im.split()
            new = Image.merge("RGBA", (rgba[order[0]],rgba[order[1]],rgba[order[2]],rgba[order[3]]))
            #print "save"
            if mv.art.patternMgr.mirror :
                import ImageOps
                im=ImageOps.mirror(pilImage)
                imf=ImageOps.flip(im)
                imf.save("/tmp/arpmv.jpg")
            else :
                new.save("/tmp/arpmv.jpg")
            if viewport is not None : 
                viewport[c4d.BASEDRAW_DATA_PICTURE] = "/tmp/arpmv.jpg"
            #print "update"
            cam.lock.release()
        except:
            print "PROBLEM VIDEO"
            
            
    def updateBmp(mv,bmp,scale=None,order=[3, 2, 2, 1],show=True,viewport=None):
        #cam.lock.acquire()
        #dialog.keyModel.Set(imarray=cam.im_array.copy())
        #cam.lock.release()
        #import Image
        cam = mv.art.arcontext[0].cam
        mv.art.arcontext[0].cam.lock.acquire()
        array = Numeric.array(cam.im_array[:])
        mv.art.arcontext[0].cam.lock.release()
        n=int(len(array)/(cam.width*cam.height))
        array.shape = (-1,4)
        map( lambda x,y,v,bmp=bmp: bmp.SetPixel(x, y, v[1], v[2], v[3]),X, Y, array)
    
        if scale != None :
            bmp.Scale(scale,256,False,False)
            if show : c4d.bitmaps.ShowBitmap(scale)
            scale.Save(name="/tmp/arpmv.jpg", format=c4d.symbols.FILTER_JPG)
        else :
            if show : c4d.bitmaps.ShowBitmap(bmp) 
            bmp.Save(name="/tmp/arpmv.jpg", format=c4d.symbols.FILTER_JPG)
        if viewport is not None:
            viewport[c4d.symbols.BASEDRAW_DATA_PICTURE] = "/tmp/arpmv.jpg"
           
        
    from c4d import threading
    class c4dThread(threading.C4DThread):
        def __init__(self,func=None,arg=None):
            threading.C4DThread.__init__(self)
            self.func = func
            self.arg = arg
            
        def Main(self):
            self.func(self.arg)
            
    def render(self,name,w,h):
        doc = c4d.documents.GetActiveDocument()
        rd = doc.GetActiveRenderData().GetData()
        bmp = c4d.bitmaps.BaseBitmap()
        #Initialize the bitmap with the result size.
        #The resolution must match with the output size of the render settings.
        bmp.Init(x=w, y=h, depth=32)
        c4d.documents.RenderDocument(doc, rd, bmp, c4d.RENDERFLAGS_EXTERNAL)
        #bitmaps.ShowBitmap(bmp)
        bmp.Save(name,c4d.FILTER_TIF)
    
    #this should be in ePMV not in the helper
    def renderDynamic(epmv,traj,timeWidget=False,timeLapse=5):
        if timeWidget:
            dial= TimerDialog()
            dial.cutoff = 15.0
        if traj[0] is not None :
            if traj[1] == 'traj':
                mol = traj[0].player.mol
                maxi=len(traj[0].coords)
                mname = mol.name
                for i in range(maxi):
                    if timeWidget and (i % timeLapse) == 0 :
                        dial.open()
                        if dial._cancel :
                            return False
                    traj[0].player.applyState(i)
                    updateDataGeom(epmv,mol)
                    update()
                    render("md%.4d" % i,640,480)
        
    #PARTICULE
    #this should be in a Tag, like redo all the particule at frame 0
    def getParticles(self,name,**kw):
        doc = self.getCurrentScene()
        PS = doc.GetParticleSystem()
        root = PS.GetRootGroup()
        if name is not None or name != "all":
            tpg = self.checkTPG(PS,name)
            return tpg           
        if "group_name" in kw and kw["group_name"] is not None:
            #check if already exist
            tpg = self.checkTPG(PS,group_name)
            return tpg
        return PS
        
    def particle(self,name,coords,**kw):
        #default is all
        
        N = len(coords)
        doc = self.getCurrentScene()
        PS = doc.GetParticleSystem()
        root = PS.GetRootGroup()
        #if grp==None: grp = PS.GetRootGroup()
        #grp.GetParticles() return indice of all particle of this group
        #uid = PS.GetPData(i, channelid)
        ids = PS.AllocParticles(N)
        if "hostmatrice" in kw and kw["hostmatrice"] is not None:
            c4dC = [self.FromVec(c)*hostmatrice for c in coords]
        else :
            c4dC = map(self.FromVec,coords)
        map(PS.SetPosition,ids,c4dC)
        life = [c4d.BaseTime(360000.0)]*N
        map(PS.SetLife,ids,life)
        if "radius" in kw and kw["radius"] is not None:
            map(PS.SetSize,ids,radius) #or vdwRadius?
        else :
            map(PS.SetSize,ids,[1.0]*N) #or vdwRadius?
        map(PS.SetMass,ids,[1.0]*N) #or atom mass?
        c4dV = map(self.FromVec,[(0.,0.0,0.),]*N)
        map(PS.SetVelocity,ids,c4dV) #or atom mass?
        if name != "all" or ("group_name" in kw and kw["group_name"] is not None):
            #check if already exist
            group_name = name             
            tpg = self.checkTPG(PS,group_name)
            if tpg is None :
                tpg = PS.AllocParticleGroup()
                PS.SetPGroupHierarchy(root,tpg,c4d.TP_INSERT_UNDERLAST)
                tpg[c4d.PGROUP_NAME] = group_name
#            tpg.SetTitle(group_name)
            map(PS.SetGroup,ids,[tpg,]*N)
            if "color" in kw and kw["color"] is  not None :
                tpg[c4d.PGROUP_COLOR] = c4d.Vector(kw["color"][0],kw["color"][1],kw["color"][2])
            return tpg
        if "color" in kw and kw["color"] is not None:
            root[c4d.PGROUP_COLOR] = c4d.Vector(kw["color"][0],kw["color"][1],kw["color"][2])
        return PS

    def updateParticles(self,newPos,PS=None,**kw): 
        #remove extra part lloc if need more  
        group = None 

        doc = self.getCurrentScene()        
        GPS =  doc.GetParticleSystem()
        if type(PS) == c4d.modules.thinkingparticles.TP_PGroup:
            group = PS
            PS = GPS

#            doc = self.getCurrentScene()
#            PS = doc.GetParticleSystem()
        Total = GPS.NumParticles()         
        if group : 
            currentN = group.NumParticles()     
        else :
            currentN = PS.NumParticles()    
        N = len(newPos)
        print("A ",currentN,N) 
        ids = range(currentN)
        if group : ids = group.GetParticles()
        #reset life for current particle
        if group and Total < currentN :
            for i in range(Total,currentN):
                GPS.AllocParticle()
        if len(newPos) == 0 :
            val= [-1,]*len(ids)
            life = [c4d.BaseTime(-1)]*len(ids)
            map(PS.SetLife,ids,life)
#            if group: GPS.FreeParticleGroup(group)
#            else  : GPS.FreeAllParticles() 
            return        
        life = [c4d.BaseTime(360000.0)]*currentN
        map(PS.SetLife,ids,life)
        #need to create some and attach to group if any
        if N > currentN:
            for i in range(currentN,N):
                ids.append(GPS.AllocParticle())
                if group : 
                    PS.SetGroup(ids[-1],group)
            cn = PS.NumParticles()
            if group : cn = group.NumParticles()
            life = [c4d.BaseTime(360000.0)]*cn
            map(PS.SetLife,range(cn),life)
        elif N < currentN:
            #removethe extra ne
            rids  = range(N,currentN)
            val= [-1,]*len(rids)
#            map(PS.FreeParticle,rids)
            life = [c4d.BaseTime(-1)]*len(rids)
            map(PS.SetLife,rids,life)
#            ids = range(PS.AllocParticle())#shuld be N
        c4dC = map(self.FromVec,newPos)        
        ids = range(N)   #should bee <= to group.NumParticles()
        map(PS.SetPosition,ids,c4dC)
        
        
    def grid_particle(self,name,dimensions,origin,step,group_name=None,
                      radius=None,hostmatrice=None,**kw):
        #default is all        
        NX,NY,NZ = dimensions
        N = dimensions[0]*dimensions[1]*dimensions[2]
        doc = self.getCurrentScene()
        PS = doc.GetParticleSystem()
        root = PS.GetRootGroup()
        #if grp==None: grp = PS.GetRootGroup()
        #grp.GetParticles() return indice of all particle of this group
        #uid = PS.GetPData(i, channelid)
        ids = PS.AllocParticles(N)       
#        indi, indj, indk = [range( N )]*3
        if hostmatrice is not None:
            c4dC = [self.FromVec([origin[0]+i*step[0], origin[1]+j*step[1], origin[2]+k*step[2]])*hostmatrice for i, j, k in zip( indi, indj, indk)]
        else :
            for i in range(NX):
                for j in range(NY):
                    for k in range(NZ):
                        u = int(k*NX*NY + j*NX + i)
                        xyz = [origin[0]+i*step[0], origin[1]+j*step[1], origin[2]+k*step[2]]
                        c = self.FromVec(xyz)
                        PS.SetPosition(u,c)
                        PS.SetSize(u,1.)
                        PS.SetMass(u,1.)
                        PS.SetVelocity(u,self.FromVec([0.,0.0,0.]))
        if group_name is not None :
            #check if already exist
            tpg = self.checkTPG(PS,group_name)
            if tpg is None :
                tpg = PS.AllocParticleGroup()
                PS.SetPGroupHierarchy(root,tpg,c4d.TP_INSERT_UNDERLAST)
                tpg[c4d.PGROUP_NAME] = group_name
#            tpg.SetTitle(group_name)
            map(PS.SetGroup,ids,[tpg,]*N)
            if color is not None :
                tpg[c4d.PGROUP_COLOR] = c4d.Vector(color[0],color[1],color[2])
            return tpg
#        if color is not None :
#            root[c4d.PGROUP_COLOR] = c4d.Vector(color[0],color[1],color[2])
        return PS

    def checkTPG(self,PS,group_name):
        groups = PS.GetParticleGroups()
        for g in groups:
            if g[c4d.PGROUP_NAME] == group_name:
                return g
        return None

    def createGroup(self,group_name,color=None,PS=None,parent = None):
        if PS is None :
            doc = self.getCurrentScene()
            PS = doc.GetParticleSystem()
        tpg = self.checkTPG(PS,group_name)           
        if tpg is None :
            tpg = PS.AllocParticleGroup()
            tpg[c4d.PGROUP_NAME] = group_name
        if parent is None :
            parent = PS.GetRootGroup()
        PS.SetPGroupHierarchy(parent,tpg,c4d.TP_INSERT_UNDERLAST)
        if color is not None :
            tpg[c4d.PGROUP_COLOR] = c4d.Vector(color[0],color[1],color[2])
        return tpg
        
   
    def setParticlProperty(self,property,ids,values,PS=None):
        if PS == None :
            doc = self.getCurrentScene()
            PS = doc.GetParticleSystem()
        funct={"group":PS.SetGroup,
               "size":PS.SetSize,
               "velocity":PS.SetVelocity,
               "position":PS.SetPosition,
               "life":PS.SetLife,
               "age":PS.SetAge,
               }
        map(funct[property],ids,values)

    def setParticulesPosition(self,newPos,PS=None):
        self.setParticlProperty("position",range(len(newPos)),newPos,PS=PS)
         
    def addDataChannel(self,PS,name,type="Real"):
        #type is 
        PS.AddDataChannel(self.CH_DAT_TYPE[type],name)
        return PS.NumDataChannels()-1
        
    def assignDataChannel(self,PS,channelid,listPID,listValue):
        uniq = False
        if len(listValue) == 1 :
            uniq = True
        for i,id in enumerate(listPID):
            if uniq :
                val = listValue[0]
            else :
                val = listValue[i]
            PS.SetPData(id, channelid,val)
    
    def getDataChannel(self,PS,channelid,listPID):
        return [PS.GetData(id,channelid) for id in listPID]


#===============================================================================
# specific C4D PARTICLE ie PyroCluster
#===============================================================================
    
    def newTPgeometry(self,name,group=None,material=None,pyro=False,parent=None):
        tpgeom = c4d.BaseObject(1001414)
        tpgeom.SetName(name)
        self.addObjectToScene(self.getCurrentScene(),tpgeom,parent=parent)
        if group is not None:
            tpgeom[c4d.PGEOM_LINK] = group
#        if pyro :
#            tpgeom.MakeTag(c4d.Ttexture)
#            tag[1010] = c4d.BaseMaterial(1001005)

    def pyro(self):
        pass

    ############DYNAMICS ##############################

    def setRigidBody(self,obj,shape="auto",child=False,
                    dynamicsBody="on", dynamicsLinearDamp = 0.0, 
                    dynamicsAngularDamp=0.0, 
                    massClamp = 0.0, rotMassClamp=1.0):
        if type(obj) is str:
            obj=self.getObject(obj)
        #The object 'Dynamics Body' (DynRigidBodyTag) was added as 'DynamicsBody'.
        tag = obj.MakeTag(self.DYNAMIC)
        if child :
            tag[c4d.RIGID_BODY_HIERARCHY]=1 #for cpk
            tag[c4d.RIGID_BODY_SPLIT_CACHE]=0 #None
        else :
            tag[c4d.RIGID_BODY_HIERARCHY]=2 #for cpk
            tag[c4d.RIGID_BODY_SPLIT_CACHE]=1 #Top level
            tag[c4d.RIGID_BODY_LINEAR_FOLLOW_STRENGTH]=  60
            tag[c4d.RIGID_BODY_ANGULAR_FOLLOW_STRENGTH]= 60
        tag[c4d.RIGID_BODY_SELF_COLLISIONS] = 0
        if shape == "auto":
            tag[c4d.RIGID_BODY_SHAPE] = 11 #automatic , 4-static shape
        elif shape == "static":
            tag[c4d.RIGID_BODY_SHAPE] = 4 #automatic , 4-static shape
        if dynamicsLinearDamp > 0:
            tag[c4d.RIGID_BODY_LINEAR_DAMPING] = dynamicsLinearDamp
        if dynamicsAngularDamp > 0:
            tag[c4d.RIGID_BODY_ANGULAR_DAMPING] = dynamicsAngularDamp
        if massClamp > 0:
            tag[c4d.RIGID_BODY_MASS_SWITCH] = 2  
            tag[c4d.RIGID_BODY_MASS] = massClamp  
            tag[c4d.RIGID_BODY_INERTIA_FACTOR] = rotMassClamp
            tag[c4d.RIGID_BODY_SELF_COLLISIONS] = 1
        if dynamicsBody == "off":
            tag[c4d.RIGID_BODY_DYNAMIC] = 0 #2=ghost, 1= on, 0= off    
        return tag
        
    def setSoftBody(self,obj):
        #The object 'Dynamics Body' (DynRigidBodyTag) was added as 'DynamicsBody'.
        if type(obj) is str:
            obj=self.getObject(obj)
        tag = obj.MakeTag(self.DYNAMIC)
        tag[c4d.RIGID_BODY_HIERARCHY]=0 #
        tag[c4d.RIGID_BODY_SPLIT_CACHE]=0 #
        tag[c4d.RIGID_BODY_LINEAR_FOLLOW_STRENGTH]=  0
        tag[c4d.RIGID_BODY_ANGULAR_FOLLOW_STRENGTH]= 10
        tag[c4d.RIGID_BODY_SELF_COLLISIONS] = 0
        tag[c4d.RIGID_BODY_SPECIFIC_MARGIN] = 1
        tag[c4d.RIGID_BODY_MARGIN] = 1.8
        tag[c4d.RIGID_BODY_SOFT] = 1 #made of polygin/lines
        tag[c4d.RIGID_BODY_SB_SHAPE_CONSERVATION] = 20.0
        return tag

    def updateSpring(self,spring,targetA=None,tragetB=None,
                     rlength=0.0,stifness = 1.,damping = 1.0):
        if targetA is not None  :
            spring[c4d.FORCE_OBJECT_A] = targetA
        spring[c4d.FORCE_APPLICATION_A]= 0 #center of Mass
        if tragetB is not None :
            spring[c4d.FORCE_OBJECT_B] = tragetB
        spring[c4d.FORCE_APPLICATION_B]= 1 #offset
        spring[c4d.FORCE_APPLY] = 1 #only to B
        spring[c4d.SPRING_LINEAR_REST_LENGTH] = rlength
        spring[c4d.SPRING_LINEAR_STIFFNESS] = stifness
        spring[c4d.SPRING_LINEAR_DAMPING] = damping

        
    def createSpring(self,name,targetA=None,tragetB=None,
                     rlength=0.0,stifness=1.0,damping = 1.0,parent=None):
        spring=c4d.BaseObject(self.SPRING)
        spring.SetName(name)
        spring[c4d.FORCE_TYPE] = 0 #linear
        if targetA is not None  :
            spring[c4d.FORCE_OBJECT_A] = targetA
        spring[c4d.FORCE_APPLICATION_A]= 0 #center of Mass
        if tragetB is not None :
            spring[c4d.FORCE_OBJECT_B] = tragetB
        spring[c4d.FORCE_APPLICATION_B]= 1 #offset
        spring[c4d.FORCE_APPLY] = 1 #only to B
        spring[c4d.SPRING_LINEAR_REST_LENGTH] = rlength
        spring[c4d.SPRING_LINEAR_STIFFNESS] = stifness
        spring[c4d.SPRING_LINEAR_DAMPING] = damping
        self.addObjectToScene(None,spring,parent=parent)
        return spring

    def addConstraint(self,obj,type="spring",target=None):
        if type(obj) is str:
            obj=self.getObject(obj)
        tag = obj.MakeTag(self.CONTRAINT)
        if type == "spring":
            tag[c4d.ID_CA_CONSTRAINT_TAG_SPRING]
            tag[c4d.ID_CA_CONSTRAINT_TAG_SPRING_TWEIGHT]#strenghth
            tag[c4d.ID_CA_CONSTRAINT_TAG_SPRING_DRAG]#drag
            #offset can be P,S,R X,Y,Z
            tag[c4d.ID_CA_CONSTRAINT_TAG_SPRING_P_OFFSET, VECTOR_X] #offset X, 
            if target is not None :
                #id are [60006] based
                #how to add a target
                tag[c4d.ID_CA_CONSTRAINT_TAG_SPRING_TARGET_COUNT] = len(target)
                id = 60000
                for t in target:
                    tag[id+1] = self.getObject(t) #target object first target
                    tag[id+2] #weigth first target
                    tag[id+4] #length first target
                    tag[id+5] #stiffness first target
                    tag[id+6] #position toggle first target
                    tag[id+7] #scale toggle first target
                    tag[id+8] #rotation toggle first target
                    id +=10

#===============================================================================
# animation features
#===============================================================================
    def setKeyFrame(self,obj,**kw):
        self.setCurrentSelection(obj)
        c4d.CallCommand(self.RECORD)
        
    def setFrame(self,value):
        doc = self.getCurrentScene()        
        fps = doc.GetFps()
        t=c4d.BaseTime(float(value)/float(fps))
        doc.SetTime(t)
        self.update()
        

    def frameAdvanced(self,doc=None,duration=None,display=False,cb=None):
        if doc is None:
            doc = self.getCurrentScene()        
        fps = doc.GetFps()
        done = False
        i=0
        while not done :
        #for i in range(duration):
            if duration is not None :
                if i>=duration :
                    done = True 
                    break
            t=c4d.BaseTime(float(i)/float(fps))
            doc.SetTime(t)
            c4d.DrawViews(c4d.DRAWFLAGS_NO_THREAD|c4d.DRAWFLAGS_NO_REDUCTION|c4d.DRAWFLAGS_STATICBREAK)
            #c4d.DRAWFLAGS_PRIVATE_OPENGLHACK)#|c4d.DRAWFLAGS_NO_THREAD|c4d.DRAWFLAGS_NO_REDUCTION|c4d.DRAWFLAGS_STATICBREAK)#|c4d.DRAWFLAGS_ONLY_ACTIVE_VIEW
            #c4d.EventAdd(c4d.EVENT_ANIMATE)
            # do your caching here. 'f' is the current frame
            if cb is not None:
                done=cb()            
#            c4d.EventAdd(c4d.EVENT_0)
            #c4d.EventAdd(c4d.EVENT_ANIMATE|c4d.EVENT_GLHACK)
            #c4d.DrawViews(c4d.DRAWFLAGS_PRIVATE_OPENGLHACK)
            c4d.GeSyncMessage(c4d.EVMSG_TIMECHANGED)
#            c4d.EventAdd(c4d.EVENT_ANIMATE)
            if display :
                self.update()
            i=i+1
        #t=c4d.BaseTime(0.)
        #doc.SetTime(t)
        c4d.EventAdd(c4d.EVENT_ANIMATE)        
        
    def animationStart(self,doc= None,forward=True,duration = None):
        if doc is None:
            doc = self.getCurrentScene()
        from time import time
        starttime = time()
        c4d.documents.RunAnimation(doc, False, forward)
        if duration is not None :
            done = False
            #fps = doc.GetFps()
            #startframe=doc.GetTime().GetFrame(fps)
            while not done :
#                t=c4d.BaseTime()
#                fps = doc.GetFps()
#                #getCurrent time
#                frame=doc.GetTime().GetFrame(fps)
                newtime = time()
                if newtime - starttime >= 10.0:
                    done = True
                    break
            self.animationStop()
        
    def animationStop(self,doc=None):
        if doc is None:
            doc = self.getCurrentScene()
        c4d.documents.RunAnimation(doc, True)
        
#===============================================================================
#     Texture Mapping / UV
#===============================================================================
    def getUV(self,object,faceIndex,vertexIndex,perVertice=True):
        ob = self.getObject(object)
        #uv=[]
        tag = ob.GetTag(c4d.Tuvw)
        if tag is None :
            tag = object.MakeVariableTag(c4d.Tuvw,ob.GetPolygonCount(),object.GetFirstTag())
            #vtag.SetName("uvTag")
        uvs = tag.GetSlow(faceIndex)
        if perVertice :
            for j,k in enumerate(uvs):
                if j == vertexIndex :
                    return self.ToVec(uvs[k],pos=False)
        else :
            return [self.ToVec(uvs[k],pos=False) for k in uvs]

    def setUV(self,object,faceIndex,vertexIndex,uv,perVertice=True,uvid=0):
        ob = self.getObject(object)
        #uv is per polygon
        tag = ob.GetTag(c4d.Tuvw)
        if tag is None :
            tag = object.MakeVariableTag(c4d.Tuvw,ob.GetPolygonCount(),object.GetFirstTag())
            #vtag.SetName("uvTag")
        if perVertice :
            uvs = tag.GetSlow(faceIndex)
            for j,k in enumerate(uvs):
                if j == vertexIndex :
                    uvs[k] = self.FromVec(uv,pos=False)
            tag.SetSlow(faceIndex,uvs["a"],uvs["b"],uvs["c"],uvs["d"])
        else :
            uvs = [self.FromVec(x,pos=False) for x in uv]
            tag.SetSlow(faceIndex,uvs[0],uvs[1],uvs[2],uvs[3]) #for a face
        #print faceIndex
        tag.Message(c4d.MSG_UPDATE)
  
#===============================================================================
# userData property for object, persistent in scene saved
#===============================================================================

    def retrievePropertiesFromContainer(self,container,typ):
        pass

    def getProperty(self, obj, key,typ=dict):
        obj = self.getObject(obj)
        if not isinstance(key, str):
            raise TypeError, "expected a str for the key argument"
        #get object userDAta
        propertiesListe = obj.GetUserDataContainer()
        for bc in propertiesListe:
            if bc[c4d.DESC_NAME] == key:
                return self.retrievePropertiesFromContainer(bc,typ)
        return None
        
    #from r13 documentation
    def AddLongDataType(obj):
        if obj is None: return
    
        bc = c4d.GetCustomDatatypeDefault(c4d.DTYPE_LONG) #create default container
        bc[c4d.DESC_NAME] = "Test"                    #rename the entry
    
        element = obj.AddUserData(bc)     #add userdata container
        obj[element] = 30                         #assign a value
        c4d.EventAdd()                           #update
#===============================================================================
# deformer
#===============================================================================
    def pathDeform(self,name,obj,curve,**kw):
        """ deform an object along a path
        @type  obj: hostObj
        @param obj: the object to be deform
        @type  curve: hostObj
        @param curve: the path
        
        @rtype:   hostObj
        @return:  the path deformer modifier
        """
        #create the path deformer object
        pathD = self.getObject(name)
        if pathD is None :
            pathD = c4d.BaseObject(self.PATHDEFORM)
            pathD.SetName(name)
            self.addObjectToScene(pathD,parent=obj)
        pathD[c4d.MGSPLINEWRAPDEFORMER_SPLINE] = curve
        pathD[c4d.MGSPLINEWRAPDEFORMER_LENMODE] = 1 #Keep Length
        return pathD
        
    def updatePathDeform(self,name,**kw):
        """ update a path deformer 
        @type  name: hostObj/string
        @param obj: the object to be deform
        @type  kw: dictionary
        @param kw: the attributes to change
        
        @rtype:   hostObj
        @return:  the path deformer modifier
        """
        pathD = self.getObject(name)
        if pathD is None :
            return
        if kw.has_key("spline"):
            pathD[c4d.MGSPLINEWRAPDEFORMER_SPLINE] = kw["spline"]
        if kw.has_key("keep_length"):
            pathD[c4d.MGSPLINEWRAPDEFORMER_LENMODE] = kw["keep_length"] #0 or 1
        if kw.has_key("object"):
            self.reParent(pathD,kw["object"])

#==============================================================================
# Noise
#==============================================================================

    def get_noise(self,point,ntype,nbasis,dimension=1.0,lacunarity=2.0,offset=1.0,octaves=6,gain=1.0,**kw):
        #multi_fractal(position, H, lacunarity, octaves, noise_basis=noise.types.STDPERLIN)
        #NotePlease use InitFbm() before you use one of the following noise types: 
        #NOISE_ZADA, NOISE_DISPL_VORONOI, NOISE_OBER, NOISE_FBM, NOISE_BUYA.
        
        nbasis = self.noise_type.values()[nbasis]
        
        theNoise = C4DNoise(nbasis)
        #InitFbm(lMaxOctaves, rLacunarity, h)
        theNoise.InitFbm(21, lacunarity, dimension)
         
        depth = octaves
        value = 0.0        
        x,y,z = point  
        vlbasis = nbasis
        point =self.FromVec(point)
        if ntype == 0 :
            #Noise(t, two_d, p[, time=0.0][, octaves=4.0][, absolute=False][, sampleRad=0.25][, detailAtt=0.25][, repeat=0])
            #r = p.Noise(noisetype, False, c4d.Vector(x/rw, y/rh, 0) * 7.0, octaves=5)            
            value = theNoise.Noise(nbasis,False,point, octaves=float(depth)) * 0.5
        elif ntype == 1:
            value = theNoise.RidgedMultifractal(point, depth, offset, gain,1) * 0.5
#            value = ridged_multi_fractal( point, dimension, lacunarity, depth, offset, gain, nbasis ) * 0.5
        elif ntype == 2: 
            #Turbulence(p, rOctaves, bAsolute[, t=0.0])
            value =  theNoise.Turbulence(point, depth, offset, gain) * 0.5
        elif ntype == 3: 
            #SNoise(p, lRepeat[, t=0.0])
            value =  theNoise.SNoise(point,offset, gain) * 0.5
        elif ntype == 4: 
            #Fbm(p, rOctaves, lRepeat[, t=0.0])
            value = theNoise.Fbm(point, depth,offset,gain)
#            value = fractal(point, dimension, lacunarity, depth, nbasis )
#        elif ntype == 5: value = turbulence_vector(    point, depth, hardnoise, nbasis )[0]
#        elif ntype == 6: value = variable_lacunarity(  point, distortion, nbasis, vlbasis ) + 0.5
#        elif ntype == 7: value = self.marble_noise( x*2.0/falloffsize,y*2.0/falloffsize,z*2/falloffsize, origin, nsize, marbleshape, marblebias, marblesharpnes, distortion, depth, hardnoise, nbasis )
#        elif ntype == 8: value = self.shattered_hterrain( point[0], point[1], point[2], dimension, lacunarity, depth, offset, distortion, nbasis )
#        elif ntype == 9: value = self.strata_hterrain( point[0], point[1], point[2], dimension, lacunarity, depth, offset, distortion, nbasis )
        return value
#===============================================================================
# Function dependant on numpy 
#===============================================================================
#    if usenumpy:
    def matrix2c4dMat(self,mat,transpose = True):
        #Scale Problem, but shouldnt as I decompose???
        #why do I transpose ?? => fortran matrix ..
            if not self._usenumpy : 
                return self.FromMat(mat,transpose = transpose)
            if transpose :
                mat = numpy.array(mat).transpose().reshape(16,)
            else :
                mat = numpy.array(mat).reshape(16,)
            r,t,s = self.Decompose4x4(mat)    
    #        print s
            #Order of euler angles: heading first, then attitude/pan, then bank
#            axis = self.ApplyMatrix(numpy.array([[1.,0.,0.],[0.,1.,0.],[0.,0.,1.]]),r.reshape(4,4))
            #r = numpy.identity(4).astype('f')
            #M = matrix(matr)
            #euler = C.matrixToEuler(mat[0:3,0:3])
            #mx=c4d.tools.hpb_to_matrix(c4d.Vector(euler[0],euler[1]+(3.14/2),euler[2]), c4d.tools.ROT_HPB)
            v_1 = self.FromVec(r.reshape(4,4)[2,:3])
            v_2 = self.FromVec(r.reshape(4,4)[1,:3])
            v_3 = self.FromVec(r.reshape(4,4)[0,:3])
            offset = self.FromVec(t)
            mx = c4d.Matrix(offset,v_1, v_2, v_3)
            #mx.off = offset
            return mx
        
    def FromMat(self,matrice,transpose=True):
#            import numpy
            #Scale Problem, but shouldnt as I decompose???
            #why do I transpose ?? => fortran matrix ..
            if self._usenumpy :            
                v_1 = self.FromVec(matrice[2,:3])
                v_2 = self.FromVec(matrice[1,:3])
                v_3 = self.FromVec(matrice[0,:3])
                offset = self.FromVec(matrice[3,:3])
            else :
                v_1 = self.FromVec(matrice[2][:3])
                v_2 = self.FromVec(matrice[1][:3])
                v_3 = self.FromVec(matrice[0][:3])
                offset = self.FromVec(matrice[3][:3])                
            mx = c4d.Matrix(offset,v_1, v_2, v_3) 
#            
#            if transpose :
#                mat = numpy.array(matrice).transpose().reshape(16,)
#            else :
#                mat = numpy.array(matrice).reshape(16,)
#            r,t,s = self.Decompose4x4(mat)    
#    #        print s
#            #Order of euler angles: heading first, then attitude/pan, then bank
#            axis = self.ApplyMatrix(numpy.array([[1.,0.,0.],[0.,1.,0.],[0.,0.,1.]]),r.reshape(4,4))
#            #r = numpy.identity(4).astype('f')
#            #M = matrix(matr)
#            #euler = C.matrixToEuler(mat[0:3,0:3])
#            #mx=c4d.tools.hpb_to_matrix(c4d.Vector(euler[0],euler[1]+(3.14/2),euler[2]), c4d.tools.ROT_HPB)
#            v_1 = self.FromVec(r.reshape(4,4)[2,:3])
#            v_2 = self.FromVec(r.reshape(4,4)[1,:3])
#            v_3 = self.FromVec(r.reshape(4,4)[0,:3])
#            offset = self.FromVec(t)
#            mx = c4d.Matrix(offset,v_1, v_2, v_3)
#            #mx.off = offset
            return mx            
        

  
    def ApplyMatrix(self,coords,mat):
        """
        Apply the 4x4 transformation matrix to the given list of 3d points.
    
        @type  coords: array
        @param coords: the list of point to transform.
        @type  mat: 4x4array
        @param mat: the matrix to apply to the 3d points
    
        @rtype:   array
        @return:  the transformed list of 3d points
        """
        if self._usenumpy:
            return Helper.ApplyMatrix(self,coords,mat)
        else :            
            mat = self.FromMat(mat)          
            return [mat.Mul(self.FromVec(c)) for c in coords]


            
    def ToMat(self,m,transpose=True):
        if type(m) != c4d.Matrix :
            return m       
        if self._usenumpy :
           return self.c4dMat2numpy(m,transpose=transpose)
        M=[[1.0,0.,0.0,0.0],
           [0.0,1.,0.0,0.0],
           [0.0,0.,1.0,0.0],
           [0.0,0.,0.0,1.0]]
        M[2][:3]=self.ToVec(m.v1)
        M[1][:3]=self.ToVec(m.v2)
        M[0][:3]=self.ToVec(m.v3)
        M[3][:3]=self.ToVec(m.off)
        if transpose : 
            return M#.transpose()
        else :
            return M
            
    def c4dMat2numpy(self,c4dmat,transpose=True,center=None):
        """a c4d matrice is 
        v1     X-Axis
        v2     Y-Axis
        v3     Z-Axis
        off     Position
        a numpy matrice is a regular 4x4 matrice (3x3rot+trans)
        """
        import numpy
        #print "ok convertMAtrix"
        from numpy import matrix
        M = numpy.identity(4)
        M[2,:3]=self.ToVec(c4dmat.v1)
        M[1,:3]=self.ToVec(c4dmat.v2)
        M[0,:3]=self.ToVec(c4dmat.v3)
        trans = self.ToVec(c4dmat.off)
        if center != None :
            for i in range(3):
                trans[i] = trans[i] - center[i]
        M[3,:3] = trans
        if transpose :
            M = M.transpose()
        return M
              
    def getMatRotation(self,obj,transpose=True):
        R = numpy.identity(4)
#        R=[[1.0,0.,0.0,0.0],
#           [0.0,1.,0.0,0.0],
#           [0.0,0.,1.0,0.0],
#           [0.0,0.,0.0,1.0]]
        obj = self.getObject(obj)
        objdcache=obj.GetDeformCache()
        objcache=obj.GetCache()
#        print "cache1",objdcache,"cache2",objcache
#        print "dirty MAtrix",obj.IsDirty(c4d.DIRTY_MATRIX)
        if objdcache is not None:
            print "cache1"
            m = objdcache.GetMg()
        elif objcache is not None:
            print "cache2"
            m = objcache.GetMg()
        else :
            m = obj.GetMg()
#        R = self.ToMat(m,transpose=transpose)
        R[2,:3]=self.ToVec(m.v1)
        R[1,:3]=self.ToVec(m.v2)
        R[0,:3]=self.ToVec(m.v3)
        #euler = c4d.utils.MatrixToHPB(c4dmat) #heading,att,bank need to inverse y/z left/righ hand problem
        #print "euler",euler
        #matr = numpy.array(self.eulerToMatrix([euler.x,euler.z,euler.y]))
        if transpose :
            return R.transpose()
        else :
            return R          



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
        self.LABEL_ID = [{"id":id,"label":"Did you want to Cancel the Filling Job:"},
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
        




    


       


    
