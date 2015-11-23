
"""
    Copyright (C) <2010>  Autin L. TSRI
    
    This file git_upy/blender/v249/blenderHelper.py is part of upy.

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
import sys
import os
import struct
import math
from math import *
import string
import copy
import gzip
import types
from types import StringType, ListType

import Blender
import bpy
from Blender import *
from Blender.Mathutils import *
from Blender import Mesh
from Blender import BezTriple
from Blender import Object
from Blender import Material
from Blender import Mathutils
from Blender import Window, Scene, Draw
from Blender.Scene import Render
from Blender.Draw import *

import numpy

GL=Blender.BGL

#TODO clean up...and fix with the epmvBHelper etc..
from upy.hostHelper import Helper
from upy.bitoperators import *

class blenderHelper(Helper):
    """
    The blender helper abstract class
    ============================
        This is the blender helper Object. The helper give access to the
        basic function need for create and edit a host 3d object and scene.
    """

    SPLINE = 'Curve'
    CURVE = Curve
    INSTANCE = 'Mesh'
    MESH = 'Mesh'
    EMPTY = 'Empty'
    host = "blender"
    pb = False
    BONES=""
    IK=""

    # Dic options
    CAM_OPTIONS = {"ortho" :"ortho","persp" : "persp" }
    LIGHT_OPTIONS = {"Area" : "Area","Sun" : "Sun","Spot":"Spot"}
    
    def __init__(self,master=None):
        Helper.__init__(self)
        self.updateAppli = self.update
        self.Cube = self.box
        self.getCurrentScene = Blender.Scene.GetCurrent
        #self.setTranslation=self.setTranslationObj
        self.Box = self.box
        self.Geom = self.newEmpty
        #self.getCurrentScene = c4d.documents.GetActiƒveDocument
        self.IndexedPolygons = self.polygons
        self.Points = self.PointCloudObject        
    
    @classmethod 
    def getCurrentScene(self):
        return Blender.Scene.GetCurrent()
    
    @classmethod    
    def getCurrentSceneName(self):
        doc = self.getCurrentScene()
        return doc.name
            
    def progressBar(self,progress=None,label=None):
        """ update the progress bar status by progress value and label string
        @type  progress: Int/Float
        @param progress: the new progress
        @type  label: string
        @param label: the new message to put in the progress status
        """
        if label is None :
            label =""
        if progress != None and label != None :
            Blender.Window.DrawProgressBar(progress, label)


    def Compose4x4(self,rot,tr,sc):
        """
        compose a blender matrix of shape (16,) from  a rotation 
        (shape (16,)), translation (shape (3,)), and scale (shape (3,))
        """
        translation=Mathutils.Vector(tr[0],tr[1],tr[2])
        scale = Mathutils.Vector(sc[0],sc[1],sc[2])
        mat=rot.reshape(4,4)
        mat=mat.transpose()
        mt=Mathutils.TranslationMatrix(translation)
        mr=Mathutils.Matrix(mat[0],mat[1],mat[2],mat[3])
        ms=Mathutils.ScaleMatrix(scale.length, 4, scale.normalize())
        Transformation = mt*mr#*ms
        return Transformation

    def setCurrentSelection(self,obj):
        sc = Blender.Scene.GetCurrent()
        obj = self.getObject(obj)
        if obj is None :
            return        
        if type (obj) is list or type (obj) is tuple :
            sc.objects.selected = obj
        else :
            sc.objects.selected = [obj]
        self.update()
    
    def getCurrentSelection(self,sc=None):
        if sc is None :
            sc = Blender.Scene.GetCurrent()
        return sc.objects.selected
    
    def updateAppli(self,):
        Blender.Scene.GetCurrent().update()
        Blender.Draw.Redraw()
        Blender.Window.RedrawAll()
        Blender.Window.QRedrawAll()  
        Blender.Redraw()
    
    def update(self,):
        import Blender
        Blender.Scene.GetCurrent().update()
        Blender.Draw.Redraw()
        Blender.Window.RedrawAll()
        Blender.Window.QRedrawAll()  
        Blender.Redraw()

    def toggleEditMode(self):
        editmode = Blender.Window.EditMode()
        if editmode: 
            Blender.Window.EditMode(0)
        return editmode

    def restoreEditMode(self,editmode=1):
        Blender.Window.EditMode(editmode)

    def getType(self,object):
        if type(object) is str:
            object = self.getObject(object)
        return object.type

    def getName(self,o):
        if type(o) is str:
            return o
        else :
            return o.name

    def getMaterial(self,name):
        return Material.Get(name)

    def getMaterialObject(self,o):
        return o.getMaterials()

    def getMaterialName(self,mat):
        return mat.getName()

    def updateObject(self,obj):
        obj = self.getObject(obj)
        obj.makeDisplayList()

    def getObject(self,name):
        obj=None
        if type(name) is not str:
            return name
        try :
            obj=Blender.Object.Get(name)
        except : 
            obj=None
        if obj is None :
            try :
              ob=self.getMesh(name)
            except :
              ob= None  
        return obj

    def getMeshFrom(self,obj):
        obj = self.getObject(obj)
        me = obj.getData(mesh=1)
        return me

    #object or scene property ?
    def getProperty(self, obj, key):
        from Blender.Types import ObjectType
        if not isinstance(obj, ObjectType):
            raise TypeError, "expected an Object for the obj argument"
        if not isinstance(key, str):
            raise TypeError, "expected a str for the key argument"
        if not key in obj.properties:
            return 
        return obj.properties[key]
        
    def setProperty(self, obj, key, value):
        from Blender.Types import ObjectType
        cool_value_types = (int, float, str, dict, list)
        def check_property_values(value, name):
            "Recursively check property types and values"
            if not isinstance(value, cool_value_types):
                raise TypeError, "expected a %s for the property: %s"%\
                      (", ".join("%s"%t.__name__ for t in cool_value_types), name)
            
            if isinstance(value, dict):
                for key, val in value.iteritems():
                    check_property_values(val, name+"['%s']"%key)
            if isinstance(value, (list, str)) and len(value) > 10000:
                raise ValueError, "property: %s is a %s which is "\
                      "too long. Max size: 10000 "%(name, str(type(value)))
        
        if not isinstance(obj, ObjectType):
            raise TypeError, "expected an Object for the obj argument"
        if not isinstance(key, str):
            raise TypeError, "expected a str for the key argument"

        check_property_values(value, key)
        
        obj.properties[key] = value

    def checkIsMesh(self,mesh):
        # Verify that we are not in editModes
        o=mesh
        mods = None
        if hasattr(o,"modifiers"):
            mods = o.modifiers
        if mods:
            print "Attention: Modifiers on ", mesh
            try:
                mesh = Blender.Mesh.Get('container')
            except:
                mesh = Blender.Mesh.New('container')
            mesh.getFromObject(o)
            return mesh
        if type(mesh) is str :
            mesh=self.getMesh(mesh)
        else :
            if not hasattr(mesh,"verts"):
                mesh=self.getMeshFrom(mesh)
        
        # If there is modifier need to get from
        return mesh

    def getMesh(self,name):
        mesh = None
        if type(name) != str:
            return name
        try :
           mesh = Mesh.Get(name)
        except:
            mesh = None
        return mesh

    def getNMesh(self,name):
        mesh = None
        if type(name) != str:
            return name
        try :
           mesh = NMesh.GetRaw(name)
        except:
            mesh = None
        return mesh

    def getChilds(self,obj):
        scn= bpy.data.scenes.active
        childs = [ob_child for ob_child in scn.objects if ob_child.parent == obj]
        return childs

    def reParent(self,obj,parent):
        if type(obj) == list or type(obj) == tuple: parent.makeParent(obj)
        else : parent.makeParent([obj,])
            
    def setObjectMatrix(self,o,matrice=None,hostmatrice=None,transpose=False,
                        local=False):
        if matrice == None and hostmatrice == None :
            return
        if type(o) == str : obj=getObject(o)
        else : obj=o
        # matrix(16,)
        if matrice is not None :
            m=numpy.array(matrice).reshape(4,4)
            if transpose : m=m.transpose()
            mat=m.tolist()
            blender_mat=Matrix(mat[0],mat[1],mat[2],mat[3])
        elif hostmatrice is not None :
            blender_mat=hostmatrice
            if transpose : blender_mat.transpose() 
        o.setMatrix(blender_mat)
        # Sets the object's matrix and updates its transformation. 
        # If the object has a parent, the matrix transform is relative to
        # the parent.
    
    def setTranslation(self,name,pos=[0.,0.,0.],absolue=True):
        obj = self.getObject(name)        
        self.setTranslationObj(obj,pos)
        
    def setTranslationObj(self,obj,coord):
        if type(obj) == self.CURVE:
            obj.setLoc(coord)
        else :
            obj.LocX=float(coord[0])
            obj.LocY=float(coord[1])
            obj.LocZ=float(coord[2])

    def getTranslation(self,name):
        obj = self.getObject(name)
        # [obj.LocX,obj.LocY,obj.LocZ]#obj.matrixWorld[3][0:3] 
        return obj.getLocation("worldspace")
        
    def translateObj(self,obj,coord,use_parent=False):
        obj.LocX=obj.LocX+float(coord[0])
        obj.LocY=obj.LocY+float(coord[1])
        obj.LocZ=obj.LocZ+float(coord[2])
    
    def scaleObj(self,obj,sc):
        if type(sc) is float :
            sc = [sc,sc,sc]        
        obj.SizeX=float(sc[0])
        obj.SizeY=float(sc[1])
        obj.SizeZ=float(sc[2])
    
    def rotateObj(self,obj,rot):
        obj.RotX=float(rot[0])
        obj.RotY=float(rot[1])
        obj.RotZ=float(rot[2])


    def newEmpty(self,name,location=None,visible=0,**kw):
        empty=Blender.Object.New("Empty", name)
        if location is not None:
            empty.setLocation(location[0],location[1],location[2])
        parent = None
        
        if "parent" in kw :
            parent = kw["parent"]
        self.addObjectToScene(self.getCurrentScene(),empty,parent=parent)
        return empty

    def newInstance(self,name,ob,location=None,hostmatrice=None,matrice=None,
                    parent=None,**kw):
        # Check the type of mesh
        mesh = None
        for me in bpy.data.meshes:
            if ob == me :
                mesh = ob
                break
        if mesh is None :
            if type(ob) is str:
                ob=self.getObject(ob)
            if self.getType(ob) == self.EMPTY:
                # Get the child mesh
                childs = self.getChilds(ob) # should have one
                mesh=childs[0].getData(mesh=1)
            else :
                mesh=ob.getData(mesh=1)
        if mesh is None :
            return None
        OBJ=self.getCurrentScene().objects.new(mesh,name)
        if parent is not None:
            parent.makeParent([OBJ,])
        
        if "material" in kw :
            mat = kw["material"]
            self.assignMaterial(OBJ,[mat])
            
        if location != None :
            self.translateObj(OBJ,location)
        #set the instance matrice
        transpose = False
        if "transpose" in kw : transpose = kw["transpose"]
        self.setObjectMatrix(OBJ,matrice=matrice,hostmatrice=hostmatrice,
                             transpose=transpose)
        return OBJ

    def setInstance(self,name,obj, matrix):
        mesh=obj.getData(False,True)
        o = Blender.Object.New("Mesh",name)
        o.link(mesh)
        o.setMatrix(matrix)
        return o

    def addObjectToScene(self,sc,obj,parent=None,centerRoot=True,rePos=None):
        # objects must first be linked to a scene before they can become
        # parents of other objects.
        if sc is None :
            sc = self.getCurrentScene()
        if type(obj) == list or type(obj) == tuple: 
            for o in obj : 
                if o not in sc.objects : sc.link(o)
        else : 

            if obj not in sc.objects : sc.link(obj)
        if parent != None: 
            parent = self.getObject(parent)
            if type(obj) == list or type(obj) == tuple: parent.makeParent(obj)
            else : parent.makeParent([obj,])
    
    def addCameraToScene(self,name,Type='persp',focal=30.0,
                         center=[0.,0.,0.],sc=None):
        cam = Blender.Camera.New(Type,name)
        cam.setScale(focal*2.)
        cam.clipEnd=1000.
        # make a new object in this scene using the camera data'
        obc = sc.objects.new(cam) 
        obc.setLocation (center[0],center[1],center[2])
        obc.RotZ=2*math.pi
        obc.restrictSelect=True
        sc.objects.camera = obc
        #Window.CameraView()
        return obc

    def addLampToScene(self,name,Type='Area',rgb=[1.,1.,1.],dist=25.0,energy=1.0,
                       soft=1.0,shadow=False,center=[0.,0.,0.],sc=None,**kw):
        lampe=Lamp.New(Type,name)
        lampe.R=rgb[0]
        lampe.G=rgb[1]
        lampe.B=rgb[2]
        lampe.setDist(dist)
        lampe.setEnergy(energy)
        lampe.setSoftness(soft)
        if shadow : lampe.setMode("Shadows")
        obj = sc.objects.new(lampe)
        obj.loc=(center[0],center[1],center[2])
        obj.restrictSelect=True
        return obj

    def deleteObject(self,obj):
        sc = self.getCurrentScene()
        #print obj
        try :
            sc.objects.unlink(obj)
        except:
            print "problem deleting ", obj
    
    def ObjectsSelection(self,listeObjects,typeSel="new"):
        """
        Modify the current object selection.
        
        @type  listeObjects: list
        @param listeObjects: list of object to joins
        @type  typeSel: string
        @param listeObjects: type of modification: new,add,...
    
        """    
        dic={"add":None,"new":None}
        sc = self.getCurrentScene()
        if typeSel == "new" :
            sc.objects.selected = listeObjects
        elif typeSel == "add":
            sc.objects.selected.extend(listeObjects)
    
    def JoinsObjects(self,listeObjects):
        """
        Merge the given liste of object in one unique geometry.
        
        @type  listeObjects: list
        @param listeObjects: list of object to joins
        """    
        sc = self.getCurrentScene()
        #put here the code to add the liste of object to the selection
        #duplicate first one and then join ?
        #
        o=self.getObject(self.getName(listeObjects[-1])+"j")
        if o is not None :
            self.deleteObject(o)
        o = self.newInstance(self.getName(listeObjects[-1])+"j",listeObjects[-1])
        self.addObjectToScene(sc,o,parent=listeObjects[-1].parent)
        o.join(listeObjects[1:])
        #for ind in range(1,len(listeObjects)):
        #    sc.objects.unlink(listeObjects[ind])


    def getMaterial(self,mat):
        if type(mat) is str:
            try :
                return Material.Get(mat)
            except :
                return None
        else :
            return mat

    def getAllMaterials(self):
        return str(Material.Get ())

    def addMaterial(self,name,col):
        #need toc heck if mat already exist\
        #mats = Material.Get()
        #if name not in mats :
        #    mat = Material.New(name)
        #else :
        try :
            mat = Material.New(name)
            mat.setRGBCol(col[0],col[1],col[2])
        except :
            mat = None
        return mat

    def createTexturedMaterial(self,name,filename,normal=False,mat=None):
        # get texture named 'foo'
        footex = Blender.Texture.New(name+"texture")
        footex.setType('Image') 
        footex.normalMap = normal
        # make foo be an image texture
        if filename is None:
            img = Blender.Image.New(name, 800, 800, 32)
            img.setFilename(name)
            img.save()

        # Load an image
        img = Blender.Image.Load(filename)
        
        # Link the image to the texture
        footex.setImage(img) 
        if mat is None :
            # Get a material
            mat = Material.New(name)
        
        # set the material's first texture
        mat.setTexture(0, footex)               

        mat.mode |= Material.Modes.TEXFACE
        mat.mode |= Material.Modes.TEXFACE_ALPHA
        mtextures = mat.getTextures()
        mtextures[0].texco = Blender.Texture.TexCo.UV#16
        if normal:
            mtextures[0].mapto = Blender.Texture.MapTo.NOR#2
        else :
            mtextures[0].mapto = Blender.Texture.MapTo.COL#1
        return mat

    def toggleDisplay(self,ob,display=True):
        if type(ob) == str : obj=self.getObject(ob)
        elif type(ob) is list :
            [self.toggleDisplay(o,display=display) for o in ob]
            return
        else : 
            obj=ob
        if obj is None :
            return            
        obj.restrictDisplay=not display
        obj.restrictRender=not display
        chs = self.getChilds(obj)
        for ch in chs:
            self.toggleDisplay(chs,display=display)
        #obj.makeDisplayList()

    def toggleXray(self,object,xray):
        obj = self.getObject(object)
        if obj is None :
            return
        if xray : 
            obj.drawMode = obj.drawMode | Blender.Object.DrawModes.XRAY
        else :
            obj.drawMode = obj.drawMode - Blender.Object.DrawModes.XRAY

    def getVisibility(self,obj,editor=True, render=False, active=False):
        #0 off, 1#on, 2 undef
        #active = restriceted selection ?
        display = {0:True,1:False,2:True}
        if type (obj) == str :
            obj = self.getObject(obj)
        if editor and not render and not active:
            return obj.restrictDisplay
        elif not editor and render and not active:
            return obj.restrictRender
        else :
            return obj.restrictDisplay,obj.restrictRender,False

    def b_matrix(self,array):
        return Mathutils.Matrix(array)
    
    def b_toEuler(self,bmatrix):
        return bmatrix.toEuler()
    
    def Compose4x4BGL(self,rot,trans,scale):
        """
        compose a matrix of shape (16,) from  a rotation (shape (16,)),
        translation (shape (3,)), and scale (shape (3,))
        """
        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glPushMatrix()
        GL.glLoadIdentity()
        GL.glTranslatef(float(trans[0]),float(trans[1]),float(trans[2]))
        GL.glMultMatrixf(rot)
        GL.glScalef(float(scale[0]),float(scale[1]),float(scale[2]))
        m = numpy.array(GL.glGetDoublev(GL.GL_MODELVIEW_MATRIX)).astype('f')
        GL.glPopMatrix()
        return numpy.reshape(m,(16,))

    def bezFromVecs(self,vecs0,vecs1):
       """
       Bezier triple from 3 vecs, shortcut functon
       """
       dd=[0.,0.,0.]
       vecs=[0.,0.,0.]
       for i in range(3): dd[i]=vecs1[i]-vecs0[i]
       for i in range(3): vecs[i]=vecs1[i]+dd[i]
       #vecs2=vecs1+(vecs0*-1)
       bt= BezTriple.New(vecs0[0],vecs0[1],vecs0[2],vecs1[0],vecs1[1],
                            vecs1[2],vecs[0],vecs[1],vecs[2])
       bt.handleTypes= (BezTriple.HandleTypes.AUTO, BezTriple.HandleTypes.AUTO)
       return bt
       
    def bezFromVecs2(self,vecs0,vecs1,vecs):
       """
       Bezier triple from 3 vecs, shortcut functon
       """
       #projection of v1 on v0->v2
       #
       B=numpy.array([0.,0.,0.])
       H1=numpy.array([0.,0.,0.])
       H2=numpy.array([0.,0.,0.])
       for i in range(3): B[i]=vecs1[i]-vecs0[i]                      
       A=numpy.array([0.,0.,0.])
       for i in range(3): A[i]=vecs[i]-vecs0[i]
       #Projection B on A
       scalar=(((A[0]*B[0])+(A[1]*B[1])+(A[2]*B[2]))/\
               ((A[0]*A[0])+(A[1]*A[1])+(A[2]*A[2])))
       C=scalar*A
       #vector C->A
       dep=A-C
       for i in range(3):
            vecs0[i]=(vecs0[i]+dep[i])
            vecs[i]=(vecs[i]+dep[i])
       for i in range(3): H1[i]=(vecs[i]-vecs1[i])
       for i in range(3): H2[i]=(-vecs[i]+vecs1[i])
       H1=self.normalize(H1.copy())*3.
       H2=self.normalize(H2.copy())*3.
       vecs0=Vector(vecs1[0]-H1[0],vecs1[1]-H1[1],vecs1[2]-H1[2])
       vecs=Vector(vecs1[0]-H2[0],vecs1[1]-H2[1],vecs1[2]-H2[2])
       #vecs2=vecs1+(vecs0*-1)
       bt= BezTriple.New(vecs0[0],vecs0[1],vecs0[2],vecs1[0],vecs1[1],
                         vecs1[2],vecs[0],vecs[1],vecs[2])
       bt.handleTypes= (BezTriple.HandleTypes.FREE , BezTriple.HandleTypes.FREE)
       return bt

    def bez2FromVecs(self,vecs1):
       bt= BezTriple.New(vecs1[0],vecs1[1],vecs1[2])
       bt.handleTypes=(BezTriple.HandleTypes.AUTO, BezTriple.HandleTypes.AUTO)
       return bt
                      
    def bezFromVecs1(self,vecs0,vecs1,vecs):
       """
       Bezier triple from 3 vecs, shortcut functon
       """
       #rotatePoint(pt,m,ax)
       A=Vector(0.,0.,0.)
       B=Vector(0.,0.,0.)
       H2=Vector(0.,0.,0.)
       A=vecs0-vecs1                     
       B=vecs-vecs1
       crP=A.cross(B)
       crP.normalize()
       A.normalize()
       B.normalize()
       #angleA,B: acos of the dot product of the two (normalised) vectors:
       dot=A.dot(B)
       angle=math.acos(dot)

       newA=(math.radians(90)-angle/2)
       nA=self.rotatePoint(A*1.35,vecs1,[crP[0],crP[1],crP[2],-newA])
       nB=self.rotatePoint(B*1.35,vecs1,[crP[0],crP[1],crP[2],newA])
       vecs0=Vector(nA[0],nA[1],nA[2])
       vecs=Vector(nB[0],nB[1],nB[2])
       #vecs2=vecs1+(vecs0*-1)
       bt= BezTriple.New(vecs0[0],vecs0[1],vecs0[2],vecs1[0],vecs1[1],
                         vecs1[2],vecs[0],vecs[1],vecs[2])
       bt.handleTypes= (BezTriple.HandleTypes.FREE, BezTriple.HandleTypes.FREE)
       
       return bt
        
    def bezSquare(self,r,name):
          kappa=4*((math.sqrt(2)-1)/3)
          l = r * kappa
          pt1=[0.,r,0.]
          pt1h=[-l,r,0.]
          pt2=[r,0.,0.]
          pt2h=[r,l,0.]
          pt3=[0.,-r,0.]
          pt3h=[l,-r,0.]
          pt4=[-r,0.,0.]
          pt4h=[-r,-l,0.]
          cu= Blender.Curve.New(name)
          coord1=pt1
          cu.appendNurb(self.bez2FromVecs(pt1))
          cu_nurb=cu[0]
          coord1=pt2
          cu_nurb.append(self.bez2FromVecs(pt2))
          coord1=pt3
          cu_nurb.append(self.bez2FromVecs(pt3))
          coord1=pt4
          cu_nurb.append(self.bez2FromVecs(pt4))
          cu_nurb.append(self.bez2FromVecs(pt1))
          #scn= Scene.GetCurrent()
          #ob = scn.objects.new(cu)
          return cu

    def bezCircle(self,r,name):
          kappa=4*((math.sqrt(2)-1)/3)
          l = r * kappa
          pt1=[0.,r,0.]
          pt1h=[-l,r,0.]
          pt2=[r,0.,0.]
          pt2h=[r,l,0.]
          pt3=[0.,-r,0.]
          pt3h=[l,-r,0.]
          pt4=[-r,0.,0.]
          pt4h=[-r,-l,0.]
          cu= Blender.Curve.New(name)
          coord1=pt1
          cu.appendNurb(self.bezFromVecs(pt1h,pt1))
          cu_nurb=cu[0]
          coord1=pt2
          cu_nurb.append(self.bezFromVecs(pt2h,pt2))
          coord1=pt3
          cu_nurb.append(self.bezFromVecs(pt3h,pt3))
          coord1=pt4
          cu_nurb.append(self.bezFromVecs(pt4h,pt4))
          cu_nurb.append(self.bezFromVecs(pt1h,pt1))
          return cu

    def createShapes2D(self,doc=None,parent=None):
        if doc is None :
            doc = self.getCurrentScene()    
        circle = doc.objects.new(self.bezCircle(0.3,'Circle'))
        square = doc.objects.new(self.bezSquare(0.3,'Square'))
        return [circle,square]
        
    def bezList2Curve(self,x,typeC):
        """
        Take a list or vector triples and converts them into a bezier curve object
        """
        # Create the curve data with one point
        cu= Blender.Curve.New()
        #need to check the type of x :atom list or coord list
 
        coord1=numpy.array(x[0])
        coord2=numpy.array(x[1])    
    
        coord0=coord1-(coord2-coord1)
    
        if typeC == "tBezier":
            # We must add with a point to start with
            cu.appendNurb(self.bezFromVecs(\
                Vector(coord0[0],coord0[1],coord0[2]),
                Vector(coord1[0],coord1[1],coord1[2]))) 
        elif typeC == "sBezier":
            cu.appendNurb(self.bez2FromVecs(\
                Vector(coord1[0],coord1[1],coord1[2])))
        else:
            cu.appendNurb(self.bezFromVecs1(\
                Vector(coord0[0],coord0[1],coord0[2]),
                Vector(coord1[0],coord1[1],coord1[2]),
                Vector(coord2[0],coord2[1],coord2[2]))) 

        # Get the first curve just added in the CurveData
        cu_nurb= cu[0] 

        # skip first vec triple because it was used to init the curve
        i=1 
        while i < (len(x)-1):
            coord0=x[i-1] # atms[(x[i].atms.Cpos())-1].xyz()
            coord1=x[i] # atms[(x[i].atms.Cpos())].xyz()
            coord2=x[i+1]
            bt_vec_tripleAv= Vector(coord0[0],coord0[1],coord0[2])
            bt_vec_triple  = Vector(coord1[0],coord1[1],coord1[2])
            bt_vec_tripleAp= Vector(coord2[0],coord2[1],coord2[2])
            bt= self.bezFromVecs(bt_vec_tripleAv,bt_vec_triple)
    
            if typeC == "tBezier":
                cu_nurb.append(bt)
            elif typeC == "sBezier":
                cu_nurb.append(self.bez2FromVecs(\
                    Vector(coord1[0],coord1[1],coord1[2])))
            else:
                cu_nurb.append(self.bezFromVecs1(\
                    bt_vec_tripleAv,bt_vec_triple,bt_vec_tripleAp))
            i+=1              
    
        coord0=numpy.array(x[len(x)-2])
        coord1=numpy.array(x[len(x)-1])        
        coord2=coord1+(coord1-coord0)
    
        if typeC == "tBezier":
            # We must add with a point to start with
            cu_nurb.append(self.bezFromVecs(
                Vector(coord0[0],coord0[1],coord0[2]),
                Vector(coord1[0],coord1[1],coord1[2]))) 
        elif typeC == "sBezier":
            cu_nurb.append(self.bez2FromVecs(
                Vector(coord1[0],coord1[1],coord1[2])))
        else:
            cu_nurb.append(self.bez2FromVecs(
                Vector(coord1[0],coord1[1],coord1[2])))
                    
        return cu
        
#    def makeRuban(x,str_type,r,name,scene):
#        #rename by Extrude and give a spline
#        #the bezierCurve"tBezier"
#        cu=self.bezList2Curve(x,str_type)
#        #the circle
#        if name == "Circle" : ob1 = scene.objects.new(bezCircle(r,name))
#        if name == "Square" : ob1 = scene.objects.new(bezSquare(r,name))
#        #extrude
#        cu.setBevOb(ob1)
#        cu.setFlag(1)
#        #make the object
#        ob = scene.objects.new(cu)
#        return ob
        
    def build_2dshape(self,name,type="circle",**kw):
        shapedic = {"circle":{"obj":self.bezCircle,"size":["r",]},
                    "rectangle":{"obj":self.bezSquare,"size":["r",]}
                    }
        dopts = [1.,1.]
        if "opts" in kw :
            dopts = kw["opts"]
        if len(shapedic[type]["size"]) == 1 :
            # shape[shapedic[type]["size"][0]] = dopts[0]
            pass
        else :
            for i in range(len(shapedic[type]["size"])) :
                # shape[shapedic[type]["size"][i]] = dopts[i]
                pass

        mesh_shape = shapedic[type]["obj"](dopts[0],"m_"+name)
        shape = self.getCurrentScene().objects.new(mesh_shape,name)
        return shape,mesh_shape
        
    def extrudeSpline(self,spline,**kw):
        extruder = None
        shape = None
        spline_clone = None
        mspline = spline.getData()
        if "shape" in kw:
            if type(kw["shape"]) == str :
                shape = self.build_2dshape("sh_"+kw["shape"]+"_"+self.getName(spline),
                                           kw["shape"])[0]
            else :
                shape = kw["shape"]        
        if shape is None :
            shape = self.build_2dshape("sh_circle"+self.getName(spline))[0]
      
        if "clone" in kw and kw["clone"] :
            spline = self.getCurrentScene().objects.new(mspline.__copy__())
            spline.getData().setBevOb(shape)
            # spline_clone = cmds.duplicate(spline,n="exd"+str(spline))
            # extruder=cmds.extrude( shape[1],spline_clone, 
            # et = 2, ucp = 1,n="ex_"+str(spline), fpt=1,upn=1)
            # return extruder,shape,spline_clone
        else :
            mspline.setBevOb(shape)
        return spline,shape,spline

    def update_spline(self,name,coords):
        pass

    def spline(self,name,coords,type="",extrude_obj=None,
               scene=None,parent=None,**kw):
        # Type : "sBezier", "tBezier" or ""
        if scene is None :
            scene = self.getCurrentScene()
        cu=self.bezList2Curve(coords,type)
        cu.name = name
        if extrude_obj is not None :
            cu.setBevOb(extrude_obj)
        cu.setFlag(1)
        ob = scene.objects.new(cu)
        if parent is not None :
            oparent = self.getObject(parent)
            oparent.makeParent([ob])
        return ob,cu

    def getBoneMatrix(self,bone,arm_mat=None):
        bone_mat= bone.matrix['ARMATURESPACE']
        if arm_mat is not None :
            bone_mat= bone_mat*arm_mat
        return bone_mat

    def addBone(self,i,armData,headCoord,tailCoord,
                roll=10,hR=0.5,tR=0.5,dDist=0.4,boneParent=None,
                name=None):
        armData.makeEditable()
        eb = Armature.Editbone()
        if name is not None :
            eb.name = name
        eb.roll = roll
        eb.head = Vector(headCoord[0],headCoord[1],headCoord[2])
        eb.tail = Vector(tailCoord[0],tailCoord[1],tailCoord[2])
        eb.headRadius=hR
        eb.tailRadius=tR
        eb.deformDist=dDist
        #if ( (i % 2) == 1 ) : eb.options = [Armature.HINGE, Armature.CONNECTED]
        #if ( (i % 2) == 0 ) : eb.options = [Armature.HINGE, Armature.CONNECTED,Armature.NO_DEFORM]
        if boneParent is not None :
            eb.options = [Armature.HINGE, Armature.CONNECTED]
            eb.parent = boneParent
        elif i != 0 :
            eb.options = [Armature.HINGE, Armature.CONNECTED]
            eb.parent = armData.bones['bone'+str(i-1)]
        armData.bones['bone'+str(i)] = eb
        return eb
        
    def armature(self,name,x,hR=0.5,tR=0.5,dDist=0.4,roll=10,scn=None,root=None,
                 listeName=None):
        if scn is None:
            scn = self.getCurrentScene()
        armObj = Object.New('Armature', name)
        armData = Armature.New()
        armData.makeEditable()
        armData.autoIK=bool(1)
        armData.vertexGroups=bool(1)
        if listeName is not None :
            bones = [self.addBone(i,armData,x[i],x[i+1],
                                  hR=hR,tR=tR,dDist=dDist,roll=roll,
                                  name=listeName[i]) for i in range(len(x)-1)]
        else :
            bones = [self.addBone(i,armData,x[i],x[i+1],
                    hR=hR,tR=tR,dDist=dDist,roll=roll) for i in range(len(x)-1)]
        #for bone in armData.bones.values():
        #   #print bone.matrix['ARMATURESPACE']
        #   print bone.parent, bone.name
        #   print bone.options, bone.name
        armObj.link(armData)
        armData.update()
        self.addObjectToScene(scn,armObj,parent=root)
        #scn.objects.link(armObj)
        return armObj,bones
    
    def add_armature(self,armObj,obj):
         mods = obj.modifiers
         mod=mods.append(Modifier.Types.ARMATURE)
         mod[Modifier.Settings.OBJECT] = armObj
         obj.addVertexGroupsFromArmature(armObj)
        
    def bindGeom2Bones(self,listeObject,bones):
        """
        Make a skinning. Namely bind the given bones to the given list of geometry.
        This function will joins the list of geomtry in one geometry
        
        @type  listeObjects: list
        @param listeObjects: list of object to joins
        @type  bones: list
        @param bones: list of joins
        """    
        #the joins dont work using non interactive mode
        if len(listeObject) >1:
            self.JoinsObjects(listeObject)
        else :
            self.ObjectsSelection(listeObject,"new")
        #2- add the joins to the selection
        self.ObjectsSelection(bones,"add")
        #3- bind the bones / geoms
        #put the code to bind here
    #    add_armature(armObj,obj)

    def oneMetaBall(self,metab,rad,coord):
        #raoplce atoms
        me=metab.elements.add()
        me.radius=float(rad) *3.  
        me.co = Vector(coord[0], coord[1], coord[2])  
    
    def metaballs(self,name,listePt,listeR,scn=None,root=None,**kw):
        if scn == None:
            scn = self.getCurrentScene()
        metab = Blender.Metaball.New()
        metab.name = name
        if listeR is None :
            listeR = [1.]*len(listePt)        
        [self.oneMetaBall(metab,listeR[x],listePt[x]) for x in range(len(listePt))]
        ob_mb = scn.objects.new(metab)
        if root is not None :
            root.makeParent([ob_mb,])
        return ob_mb,metab


    def constraintLookAt(self,object):
        """
        Constraint an hostobject to llok at the camera
        
        @type  object: Hostobject
        @param object: object to constraint
        """
        object=self.getObject(object)

    def updateText(self,text,string="",parent=None,size=None,pos=None,font=None):
        if type(text) == list or type(text) == tuple:
            txt,otxt =text
        else :
            otxt = text             
            txt = text.getData() 
        if string : 
            txt.setText(string)
        if size is not None :  
            txt.setSize(size)
        if pos is not None : 
            self.setTranslation(otxt,pos)
        if parent is not None and otxt is not None: 
            self.reParent(otxt,parent)
        if otxt is not None :
            otxt.makeDisplayList()

    def Text(self,name="",string="",parent=None,size=5.,pos=None,font='Courier',
             lookAt=False,**kw):
        return_extruder = False
        
        # create a new Text3d object called MyText
        txt = Text3d.New(name+"Text")

        # create an object from the obdata in the current scene
        otxt=self.getCurrentScene().objects.new(txt,name)   
        txt.setText(string)
        txt.setSize(size)
        
        ## Result: [u'testShape', u'makeTextCurves2'] # 
        if pos is not None:
            pos[0] = pos[0] - 4
            self.setTranslation(otxt,pos)
        if parent is not None:
            self.addObjectToScene(self.getCurrentScene(),otxt,parent=parent)
        if lookAt:
            self.constraintLookAt(name)
        if "extrude" in kw:
            extruder = None
            #create an extruder
            if type(kw["extrude"]) is bool and kw["extrude"]:
                return_extruder = True
            else :
                extruder = kw["extrude"]
        if return_extruder:
            return otxt, extruder
        else :
            return otxt          

    def box(self,name,center=[0.,0.,0.],size=[1.,1.,1.],cornerPoints=None,visible=1,
                              mat =None,**kw):
        me=Mesh.Primitives.Cube(1.0)
        me.name = "mesh_"+name   
        self.addMaterial(name,[1.,1.,0.])
        bx=self.getCurrentScene().objects.new(me,name)

        if cornerPoints != None :
            for i in range(3):
                size[i] = cornerPoints[1][i]-cornerPoints[0][i]
            center=(numpy.array(cornerPoints[0])+numpy.array(cornerPoints[1]))/2.
            
        bx.setLocation(float(center[0]),float(center[1]),float(center[2]))
        bx.setSize(float(size[0]),float(size[1]),float(size[2]))

#         bx.setDrawType(2) #wire
        parent= None
        if "parent" in kw :
            parent = kw["parent"]
        self.addObjectToScene(self.getCurrentScene(),bx,parent=parent)
        return bx,me

    def updateBox(self,box,center=[0.,0.,0.],size=[1.,1.,1.],
                  cornerPoints=None,visible=1, mat = None):
        box=self.getObject(box)
        if cornerPoints != None :
            for i in range(3):
                size[i] = cornerPoints[1][i]-cornerPoints[0][i]
            for i in range(3):
                center[i]=(cornerPoints[0][i]+cornerPoints[1][i])/2.
        box.setLocation(float(center[0]),float(center[1]),float(center[2]))
        box.setSize(float(size[0]),float(size[1]),float(size[2]))

    def plane(self,name,center=[0.,0.,0.],size=[1.,1.],cornerPoints=None,
              visible=1,**kw):
        #plane or grid
        xres = 2
        yres = 2
        if "subdivision" in kw :
            xres = kw["subdivision"][0]
            yres = kw["subdivision"][1]
            if xres == 1 : xres = 2
            if yres == 1 : yres = 2
        me=Mesh.Primitives.Grid(xres, yres, 1.0)
        me.name = "mesh_"+name   

        plane=self.getCurrentScene().objects.new(me,name)
        if cornerPoints != None :
            for i in range(3):
                size[i] = cornerPoints[1][i]-cornerPoints[0][i]
            center=(numpy.array(cornerPoints[0])+numpy.array(cornerPoints[1]))/2.
        plane.setLocation(float(center[0]),float(center[1]),float(center[2]))
        plane.setSize(float(size[0]),float(size[1]),1.0)
        
        if "axis" in kw : #orientation
            dic = { "+X":[1.,0.,0.],"-X":[-1.,0.,0.],
                    "+Y":[0.,1.,0.],"-Y":[0.,-1.,0.],
                    "+Z":[0.,0.,1.],"-Z":[0.,0.,-1.]}
            idic = { 0:[1.,0.,0.],1:[-1.,0.,0.],
                     2:[0.,1.,0.],3:[0.,-1.,0.],
                     4:[0.,0.,1.],5:[0.,0.,-1.]}
            if type(kw["axis"]) is str :
                axis = dic[kw["axis"]]
            else : #int
                axis = idic[kw["axis"]]
        
        if "material" in kw :
            if type(kw["material"]) is not bool :
                self.assignMaterial(plane,[kw["material"],])                
            else :
                self.addMaterial(name,[1.,1.,0.])

        parent = None
        if "parent" in kw :
            parent = kw["parent"]                
        self.addObjectToScene(self.getCurrentScene(),plane,parent=parent)
        return plane,me
        
    def Sphere(self,name,res=16.,radius=0.5,pos=None,
               color=None,mat=None,parent=None):
     	diameter = 2*radius
        #res need to be between 3 and 1000
        if res < 3 : res = 3 
        me=Mesh.Primitives.UVsphere(int(res),int(res),diameter)#diameter
     	me.name = "mesh_"+name
        for face in me.faces:
            face.smooth=1

     	if mat is not None :
            mat = self.getMaterial(mat)
        else :
            if color == None :
                color = [1.,1.,0.]
            self.addMaterial(name,color)
            mat = Material.Get(name)
        
    	me.materials=[mat]
    	OBJ=self.getCurrentScene().objects.new(me,name)
     	if pos == None : pos = [0.,0.,0.]
    	OBJ.setLocation(float(pos[0]),float(pos[1]),float(pos[2]))
        if parent is not None:
            self.reParent(OBJ,parent)
    	return OBJ,me

    def Cone(self,name,radius=0.5,length=1.,res=9, pos = [0.,0.,0.],parent=None):
        diameter = 2*radius
        me = Mesh.Primitives.Cone(res, diameter, length)
        me.name = "mesh_"+name
        cone=self.getCurrentScene().objects.new(me,name)

        if pos != None:
            cone.setLocation(float(pos[0]),float(pos[1]),float(pos[2]))

        if parent is not None:
            parent.makeParent([cone,])
        return cone,me

    def Cylinder(self,name,radius=0.5,length=1.,res=16,pos = None,parent = None):
        diameter = 2*radius
        res = 3 if res < 3 else res

        me=Mesh.Primitives.Cylinder(res, diameter, length)#
        me.name = "mesh_"+name
        #addMaterial(name,[1.,1.,0.])
        cyl=self.getCurrentScene().objects.new(me,name)
        if pos != None:
            cyl.setLocation(float(pos[0]),float(pos[1]),float(pos[2]))
        if parent is not None:
            parent.makeParent([cyl,])
        return cyl,me
    
    """
    def createMeshSphere(self,**kwargs):
            # default the values
            radius = kwargs.get('radius',1.0)
            diameter = radius *2.0
            segments = kwargs.get('segments',8)
            rings = kwargs.get('rings',8)
            loc   = kwargs.get('location',[0,0,0])
            useIco = kwargs.get('useIco',False)
            useUV = kwargs.get('useUV',True)
            subdivisions = kwargs.get('subdivisions',2)
            if useIco:
                sphere = Blender.Mesh.Primitives.Icosphere(subdivisions,diameter)
            else:    
                sphere = Blender.Mesh.Primitives.UVsphere(segments,rings,diameter)
            #ob = self.scene.objects.new(item,name)    
            #ob.setLocation(loc)
            return sphere
    """
        
    def getTubeProperties(self,coord1,coord2):
        x1 = float(coord1[0])
        y1 = float(coord1[1])
        z1 = float(coord1[2])
        x2 = float(coord2[0])
        y2 = float(coord2[1])
        z2 = float(coord2[2])
        laenge = math.sqrt((x1-x2)*(x1-x2)+(y1-y2)*(y1-y2)+(z1-z2)*(z1-z2))
        wsz = atan2((y1-y2), (x1-x2))
        wz = acos((z1-z2)/laenge)
        return laenge,wsz,wz,[float(x1+x2)/2,(y1+y2)/2,(z1+z2)/2]
        
    def updateTubeMesh(self,mesh,basemesh=None,verts=None,faces=None,
                       cradius=1.0,quality=1.):
        mesh = NMesh.GetRaw(mesh)
        mats=mesh.materials
        if verts is None :
            if basemesh is not None:
                basemesh = NMesh.GetRaw(basemesh) #this one should never modified
                verts = basemesh.verts
                faces = basemesh.faces
            else:
                print "need verts and face or a the mesh_baseCyl object"
                return
        #reset mesh
        mats=mesh.materials
        mesh.verts=verts[:]
        mesh.faces=faces[:]
        #new sacle
        cradius = cradius*2.0
        Smatrix=Mathutils.ScaleMatrix(cradius, 4)
        Smatrix[2][2] = 1.
        mesh.transform(Smatrix)
        mesh.materials = mats
        #update
        mesh.update()
        #print "done"

    def updateTubeObj(self,o,coord1,coord2):
        laenge,wsz,wz,coord=self.getTubeProperties(coord1,coord2)
        o.SizeZ = laenge
        self.setTranslationObj(o,coord)
        #o.setLocation(coord[0],coord[1],coord[2])
        o.RotY = wz
        o.RotZ = wsz
    
    def instancesCylinder(self,name,points,faces,radii,mesh,colors,scene,parent=None):
        cyls=[]
        mat = None
        if len(colors) == 1:
            mat = self.addMaterial('mat_'+name,colors[0])
        for i in xrange(len(faces)):
            laenge,wsz,wz,coord=self.getTubeProperties(points[faces[i][0]],points[faces[i][1]]) 	
            cname=name+str(i)
            mesh=Mesh.Get("mesh_"+mesh.getName().split("_")[1])    #"mesh_"+name
            if mat == None : mat = self.addMaterial("matcyl"+str(i),colors[i])
            me.materials=[mat]
            obj=Object.New('Mesh',spname)
            obj.link(mesh)
            #obj=scene.objects.new(mesh,cname)
            obj.setLocation(float(coord[0]),float(coord[1]),float(coord[2]))
            obj.RotY = wz
            obj.RotZ = wsz
            obj.setSize(float(radii[i]),float(radii[i]),float(laenge))
            cyls.append(obj)
        self.AddObject(cyls,parent=parent)
        return cyls
    
    def oneCylinder(self,name,head,tail,radius=None,instance=None,material=None,
                    parent = None,color=None):
        laenge,wsz,wz,coord=self.getTubeProperties(head,tail)
        if instance == None : 
            obj = self.Cylinder(name,parent=parent,pos =coord)[0]
        else : 
            obj=self.newInstance(name,instance,coord,parent=parent)
        obj.RotY = wz
        obj.RotZ = wsz
        if radius is None :
            radius= 1.0           
        self.scaleObj(obj,[radius,radius,float(laenge)])
        #obj.setSize(1.,1.,float(laenge))
        if material is not None :
            self.assignMaterial(obj,material)
            obj.colbits = 1<<0
        elif color is not None :
            mats = self.getMaterialObject(obj)
            if not mats :
                mat = self.addMaterial("mat_"+name,color)
                self.assignMaterial(obj,mat)
                obj.colbits = 1<<0
            else :
                self.colorMaterial(mats[0],color)
            #print obj,material
        return obj

    def updateOneCylinder(self,name,head,tail,radius=None,material=None,color=None):
        laenge,wsz,wz,coord=self.getTubeProperties(head,tail)
        stick = self.getObject(name)
        stick.setLocation(float(coord[0]),float(coord[1]),float(coord[2]))
        if radius is None :
            radius= 1.0        
        stick.RotY = wz
        stick.RotZ = wsz
        self.scaleObj(stick,[radius,radius,float(laenge)])

        if material is not None :
            self.assignMaterial(stick,material)
            stick.colbits = 1<<0
        elif color is not None :
            mats = self.getMaterialObject(stick)
            if not mats :
                mat = self.addMaterial("mat_"+name,color)
                self.assignMaterial(stick,mat)
                stick.colbits = 1<<0
            else :
                self.colorMaterial(mats[0],color)
        return stick
            
    def updateSphereMesh(self,name,verts=None,faces=None,basemesh=None,
                         scale=None):
        if verts is None :
            if basemesh is not None :
                basemesh=NMesh.GetRaw(basemesh)
                verts = basemesh.verts
                faces = basemesh.faces
            else :
                print "error need verts or basemesh"
                return
        #compute the scale transformation matrix
        if type(name) is str :
            mesh=NMesh.GetRaw(name)#self.getMesh(mesh)
            if mesh is None :
                mesh = self.getMeshFrom(name)
                mesh=NMesh.GetRaw(mesh.name)
        if mesh is not None:
            mesh.verts = verts[:]
            mesh.faces = faces[:]
#            self.updateMesh(mesh,vertices=verts,faces=faces)
            if  scale != None :
                factor=float(scale*2.)
                #verify the *2 ?
                Smatrix=Mathutils.ScaleMatrix(factor, 4)
                mesh.transform(Smatrix)
                mesh.update()
        
    def updateSphereObj(self,obj,coord):
        c=coord
        o=obj#getObject(nameo)
        #o.setLocation(float(c[0]),float(c[1]),float(c[2]))
        o.LocX = float(c[0])
        o.LocY = float(c[1])
        o.LocZ = float(c[2])
    
    def instancesSphere(self,name,centers,radii,meshsphere,colors,scene,parent=None):
        sphs=[]
        k=0
        mat = None
        if len(colors) == 1:
            mat = self.addMaterial('mat_'+name,colors[0])
        for j in xrange(len(centers)):
            spname = name+str(j)
            atC=centers[j]
            #meshsphere is the object which is link to the mesh
            mesh=Mesh.Get("mesh_"+meshsphere.getName().split("_")[1])    
            #"mesh_"+name     OR use shareFrom    
            #mesh=Mesh.Get(mesh)
            OBJ=Object.New('Mesh',spname)
            OBJ.link(mesh)
            #OBJ=scene.objects.new(mesh,spname)
            OBJ.setLocation(float(atC[0]),float(atC[1]),float(atC[2]))
            OBJ.setSize(float(radii[j]),float(radii[j]),float(radii[j]))
            #OBJ=Object.New('Mesh',"S_"+fullname)   
            if mat == None : mat = self.addMaterial("matsp"+str(j),colors[j])
            OBJ.setMaterials([mat])
            OBJ.colbits = 1<<0
            sphs.append(OBJ)
        self.AddObject(sphs,parent=parent)
        return sphs
    
    def clonesAtomsSphere(self,name,iMe,x,scn,armObj,scale,Res=32,R=None,join=0):
        pass
         
    def duplicateIndices(self,indices,n):
        newindices = [ (i[0],i[1],i[1]+n,i[0]+n) for i in indices ]
        return newindices
    
    def duplicateCoords(self,coords):
        newcoords = [(x[0],x[1],x[2]-0.1) for x in coords]
        return newcoords
    
    def PointCloudObject(self,name,**kw):
        #print "cloud", len(coords)
        coords=kw['vertices']
        me=bpy.data.meshes.new(name)
        me.verts.extend(coords)
        if kw.has_key('faces'):
            if kw['faces']:
                me.faces.extend([(x,x+1,x+2) for x in range(1,len(me.verts)-3) ])
        ob = Blender.Object.New("Mesh",name+"ds")
        ob.link(me)
        if kw.has_key("parent"):
            parent = kw["parent"]
        else :
            parent = None
        self.addObjectToScene(self.getCurrentScene(),ob,parent=parent)
        return ob,me
    
    def updateCloudObject(self,name,coords):
        #print "updateMesh ",geom,geom.mesh
        #getDataFrom object or gerNRAW?
        #mesh=NMesh.GetRaw(geom.mesh)
        mesh=Mesh.Get(name)
        #print mesh
        #mesh=geom.mesh
        #remove previous vertice and face
        mats=mesh.materials
        mesh.verts=None
        mesh.faces.delete(1,range(len(mesh.faces)))
        #add the new one
        mesh.verts.extend(coords)            # add vertices to mesh
        #set by default the smooth
        mesh.materials=mats
        mesh.update()

    
    def polygons(self, name, proxyCol=False, smooth=True, color=None, dejavu=False,
                 material=None, **kw):
        doMaterial = True
        if kw.has_key('vertices'):
            if kw['vertices'] is not None:
                vertices = kw["vertices"]
        if kw.has_key('faces'):
            if kw['faces'] is not None:
                faces = kw["faces"]
                if type(faces) not in [types.ListType, types.TupleType]:
                    faces = faces.tolist()
        if kw.has_key('normals'):
            if kw['normals'] is not None:
                normals = kw["normals"]
        frontPolyMode = 'fill'
        if kw.has_key("frontPolyMode") : 
            frontPolyMode = kw["frontPolyMode"]
        shading = 'flat'
        if kw.has_key("shading") : 
            shading=kw["shading"]#'flat'
        #vlist = []
        polygon=bpy.data.meshes.new(name)
        if kw['vertices'] is not None: 
            polygon.verts.extend(vertices)    	# add vertices to mesh
        if kw['faces'] is not None: 
            polygon.faces.extend(faces)     # add faces to the mesh (also adds edges)
        #smooth face : the vertex normals are averaged to make this face look smooth
        polygon.calcNormals()
        if kw['faces'] is not None: 
            for face in polygon.faces:
                face.smooth=smooth
        
        if type(material) is bool :
            doMaterial = material        
        if doMaterial:
            if material is None :
                mat = Material.New("mat"+name[:4])
            else :
                mat = self.getMaterial(material)
            polygon.materials=[mat]
            if color != None and len(color) == 1:
                self.colorMaterial(mat,color[0])
        if color != None and len(color) > 1:
            self.changeColor(polygon,color)
        if frontPolyMode == "line" :
            #drawtype,and mat ->wire
            mat.setMode("Wire")    
        if dejavu :
            obpolygon = Blender.Object.New("Mesh",name)
            obpolygon.link(polygon)
            if frontPolyMode == "line" :
                obpolygon.setDrawType(2)
            return obpolygon
        else :
            return polygon
    
    def createsNmesh(self, name, vertices, vnormals, faces,color=[[1,0,0],],
                            material=None, smooth=True, proxyCol=False, **kw):
        """
        This is the main function that create a polygonal mesh.
        
        @type  name: string
        @param name: name of the pointCloud
        @type  vertices: array
        @param vertices: list of x,y,z vertices points
        @type  vnormals: array
        @param vnormals: list of x,y,z vertex normals vector
        @type  faces: array
        @param faces: list of i,j,k indice of vertex by face
        @type  smooth: boolean
        @param smooth: smooth the mesh
        @type  material: hostApp obj
        @param material: material to apply to the mesh    
        @type  proxyCol: booelan
        @param proxyCol: do we need a special object for color by vertex (ie C4D)
        @type  color: array
        @param color: r,g,b value to color the mesh
    
        @rtype:   hostApp obj
        @return:  the polygon object
        """
                                
        polygon = self.polygons("Mesh_"+name, vertices=vertices, normals=vnormals,
                                faces=faces, material=material, color=color,
                                smooth=smooth, proxyCol=proxyCol, **kw)
        
        obpolygon = Blender.Object.New("Mesh",name)
        obpolygon.link(polygon)
        parent = None
        if "parent" in kw :
            parent = kw["parent"]
        self.addObjectToScene(None,obpolygon,parent = parent)
        return obpolygon,polygon
    
    def getLayers(self, scn):
        """
        Return a list of active layers of a scene or an object
        """
        from Blender.Types import ObjectType

        # Expecting an object or a Scene
        if isinstance(scn, ObjectType):
            return  [ind for ind in scn.layers]
        
        return [ind for ind in scn.getLayers()]

    def setLayers(self, scn, layers):
        """
        Set the layers of a scene or an object, expects a list of integers
        """
        from Blender.Types import ObjectType

        # Expecting an object or a Scene
        if isinstance(scn, ObjectType):
            scn.layers = layers
        else:
            scn.setLayers(layers)

    def updatePoly(self, obj, vertices=None, faces=None):
        if type(obj) is str:
            obj = self.getObject(obj)
        if obj is None : return
        mesh=self.getMeshFrom(obj)#Mesh.Get("Mesh_"+obj.name)
        self.updateMesh(mesh, vertices=vertices, faces=faces)
        self.updateObject(obj)

    def updateMesh(self, mesh, vertices=None, faces=None, smooth=True):
        # need to keep the materials, but what if material is on the obj..
        # remove previous vertice and face
        # if there is a modifier we may not modif it ?
        # or we can inactivate it while we modify
        if type(mesh) is str :
            mesh = self.getMesh(mesh)
        else:
            if not hasattr(mesh, "verts"):
                mesh=self.getMeshFrom(mesh)

        mats = mesh.materials
        
        # check if len vertices is =
        if len(mesh.verts) == len(vertices):
            [self.setMeshVerticesCoordinates(v,c) for v,c in zip(mesh.verts,vertices)]
        else :
            mesh.verts=None

            # Add the new one
            mesh.verts.extend(vertices) # add vertices to mesh
            
        if faces is not None:
            if type(faces) is not list:
                faces = faces.tolist()
            if len(mesh.faces) == len(faces) :
                [self.setMeshFace(mesh, f, indexes) for f, indexes in \
                 zip(mesh.faces, faces)]
            else : 
                mesh.faces.delete(1, range(len(mesh.faces)))
                mesh.faces.extend(faces) # add faces to the mesh (also adds edges)
                
            # Set by default the smooth
            for face in mesh.faces:
                face.smooth=smooth
            
            #mesh.calcNormals()
        
        mesh.materials=mats
        mesh.update()

    def instancePolygon(self,name, matrices=None, hmatrices=None, 
                        mesh=None, parent=None,
                        transpose=True, globalT=True, **kw):
        hostM= False
        if hmatrices is not None :
            matrices = hmatrices
            hostM = True
        if matrices == None : return None
        if mesh == None : return None
        instance = []
        for i,mat in enumerate(matrices):
            inst = self.getObject(name+str(i))          
            if inst is None :
                if hostM :
                    inst = self.newInstance(\
                        name+str(i),mesh, hostmatrice=mat, matrice=None,
                        transpose=transpose, parent=parent)
                else :
                    inst = self.newInstance(\
                        name+str(i),mesh, hostmatrice=None, matrice=mat,
                        transpose=transpose, parent=parent)                    
            else :
                # UpdateInstanceShape ?
                self.setObjectMatrix(inst, matrice=matrice,\
                                     hostmatrice=hostmatrice, transpose=transpose)
            instance.append(inst)
            #instance[-1].MakeTag(c4d.Ttexture)
        return instance

    def alignNormal(self,poly):
        pass    

    def getFace(self,face,**kw):
        return [v.index for v in face.verts]

    def getFaces(self,object):
        # Get the mesh
        if type(obj) is str:
            obj = self.getObject(obj)
        if obj is None : return
        mesh=Mesh.Get("Mesh_"+obj.name)
        bfaces = mesh.faces
        faces = map(self.getFace,c4dfaces)
        return faces
        

    def getMatFromColorComparison(self,listMat, color):
        for i,mat in enumerate(listMat) :
            col = self.convertColor(mat.getRGBCol())
            col = [int(col[0]),int(col[1]),int(col[2])]
            if col == color :
                return i,mat
        return 0,None
    
    def applyMultiMat(self,mesh,colors):
        mesh.vertexColors = 1
        for k,f in enumerate(mesh.faces):
            ncolor = [f.col[0][0],f.col[0][1],f.col[0][2]]
            i,mat=self.getMatFromColorComparison(mesh.materials, ncolor)
            if mat is None :
                print ncolor,k
            f.mat = i

    def color_per_vertex(self,mesh,colors,perVertex=True,perObjectmat=None,pb=False,
                    facesSelection=None,faceMaterial=False):
        editmode = self.toggleEditMode()
        if type(colors[0]) is float or type(colors[0]) is int and len(colors) == 3 :
           colors = [colors,]
        m=self.getMesh(mesh)
        if m is None or type(m) is str :
            mesh = self.getMeshFrom(mesh)
        else:
            if not hasattr(m,'vertexColors'):
                mesh = self.getMeshFrom(mesh)
            else:
                mesh = m
        try:
            mesh.vertexColors = 1  # enable vertex colors
        except:
            print "no vertexColors"
            return False

        # Get the working v an f
        mfaces = mesh.faces
        mverts = mesh.verts
        if facesSelection is not None :
            if type(facesSelection) is bool :
                face_sel_indice = self.getMeshFace(mesh,selected=True)
            else :
                face_sel_indice = facesSelection
            fsel = []
            vsel = set()
            for i in face_sel_indice:
                fsel.append(mfaces[i])
                for v in mfaces[i].v:
                        vsel.add(v)
            mfaces = fsel
            mverts = list(vsel)

        # Verfify perVertex flag
        unic=False
        ncolor=None
        if len(colors) != len(mverts) and len(colors) == len(mfaces): 
            perVertex=False
        elif len(colors) == len(mverts) and len(colors) != len(mfaces): 
            perVertex=True
        else :
            if (len(colors) - len(mverts)) > (len(colors) - len(mfaces)) : 
                perVertex=True
            else :
                perVertex=False            

        if len(colors)==1 : 
            unic=True
            ncolor = self.convertColor(colors[0])
        for k, f in enumerate(mfaces):
            if not unic and not perVertex : 
                if f.index < len(colors):
                    ncolor = self.convertColor(colors[f.index],)
            for i, v in enumerate(self.getMeshFace(f)):
                if not faceMaterial:
                    col= f.col[i]
                    if not unic and perVertex : 
                        if v < len(colors):
                            #print colors[v.index]
                            ncolor = self.convertColor(colors[v])
                        else :
                            print f.index,v, len(colors)
                    col.r= int(ncolor[0])
                    col.g= int(ncolor[1])
                    col.b= int(ncolor[2])
                    #print int(ncolor[0]),int(ncolor[1]),int(ncolor[2])
                else :
                    pass
            if pb and (k%70) == 0:
                progress = float(k) / (len( mesh.faces ))
                Window.DrawProgressBar(progress, 'color mesh')
        if len(mesh.materials):
            mesh.materials[0].setMode("VColPaint")
        if unic and facesSelection is None :
           if len(mesh.materials):
               mat = mesh.materials[0]
               if perObjectmat != None : mat = perObjectmat.getMaterials()[0]
               mat.setRGBCol([colors[0][0],colors[0][1],colors[0][2]])
        mesh.update()
        self.restoreEditMode(editmode)
        return True

    def changeColor(self, mesh, colors, perVertex=True, perObjectmat=None,
                    pb=False, facesSelection=None, faceMaterial=False):
        
        res = self.color_per_vertex(mesh,colors, perVertex=perVertex,
                                    perObjectmat=perObjectmat, pb=pb,
                                    facesSelection=facesSelection,
                                    faceMaterial=faceMaterial)
        
        if not res or len(colors) == 1:
            #need the object not the mesh
            self.changeObjColorMat(mesh, colors[0])
        
    def colorMaterial(self,mat,color):
        # mat input is a material name or a material object
        # color input is three rgb value array
        try :
            mat = Material.Get(mat)
            ncolors=color#blenderColor(color)
            mat.setRGBCol([ncolors[0],ncolors[1],ncolors[2]])
        except :
            pass
            #print "no mat "
            #print mat
    
    def assignMaterial(self,obj,mat,texture=False,**kw):
        if texture :
            # need the mesh
            mesh=obj.getData(False,True)
            mesh.addUVLayer(obj.name+"UV")
            print "faceUV ",mesh.faceUV
            obj.colbits = 1<<0
        if type(obj) is list:
            if  type(mat) == list :
                for o in obj:
                    o.setMaterials(mat)
                    o.colbits = 1<<0#
            else :
                for o in obj:
                    o.setMaterials([mat,])
                    o.colbits = 1<<0#
        else :
            if  type(mat) == list :
                obj.setMaterials(mat)
            else :
                obj.setMaterials([mat,])
            obj.colbits = 1<<0#
    
    def changeObjColorMat(self,obj,color):
        if len(color) == 1 :
            color = color[0]
        obj = self.getObject(obj)
        mats=obj.getMaterials()
        if len(mats) == 0 : 
            mat = self.retrieveColorMat(color)
            if mat == None : 
                mat = self.addMaterial("newColor",color)
            obj.setMaterials([mat])
        else :
            self.colorMaterial(mats[0],color)
        obj.colbits = 1<<0#
                    
    ######ANIMATION FUNCTION########################
    def insertKeys(self,obj,step=5):
        curFrame=self.getCurrentScene().getRenderingContext().currentFrame()
        if type(obj) == list or type(obj) == tuple:
            for o in obj:
                if type(o) == str : o=getObject(o)
                o.insertIpoKey(Blender.Object.LOCROT)
        else :
            if type(o) == str : o=getObject(o)
            o.insertIpoKey(Blender.Object.LOCROT)
        self.getCurrentScene().getRenderingContext().currentFrame(curFrame+step)
    
    #############PARTICLE####################################
    #From a pointcloud-yes
    def particle(self,name,coords,group_name=None,radius=None,color=None,hostmatrice=None,**kw):
        doc = self.getCurrentScene()
        cloud = self.PointCloudObject(name,
                                        vertices=coords,
                                        parent=None)[0]
        n = len(coords)
        o=Blender.Particle.New(cloud)
        o.setName(name)
        
        # Particle.EMITFROM[ 'PARTICLE' | 'VOLUME' | 'FACES' | 'VERTS' ]
        o.particleDistribution=3 
        o.amount = n
        o.glBrown=5.0 #brownian motion
        return cloud
        
    def newParticleSystem(self,name,object,n):
        o=Blender.Particle.new(object)
        o.setName(name)
        # Particle.EMITFROM[ 'PARTICLE' | 'VOLUME' | 'FACES' | 'VERTS' ]
        o.particleDistribution=3 
        o.amount = n
        o.glBrown=5.0

    def getParticles(self,name):
        ob=self.getObject(name+"ds")        
        return ob

    def updateParticles(self,newPos,PS=None): 
        # ps could be the name too
        # update he point could that have he paricle...
        self.updatePoly(PS,vertices=newPos)

    @classmethod
    def addTextFile(self,name="",file=None,text=None):
        if file is None and text is None :
            return
        if file is not None :
            try:
                f = open(file,'r')
                script = f.read()
                f.close()
            except:
                return
        elif text is not None :
            script = text
        texts = list(bpy.data.texts)
        newText = [tex for tex in texts if tex.name == name]
        if not len(newText) :
            newText = Blender.Text.New(name)
        else :
            newText[0].clear()
            newText=newText[0]
        for line in script : newText.write(line)

    def FromVec(self,v,pos=False):
        return Mathutils.Vector(v[0],v[1],v[2])

    def ToVec(self,v,pos=False):
        return [v[0],v[1],v[2]]

    def getUV(self,object,faceIndex,vertexIndex,perVertice=True):
        ob = self.getObject(object)
        # uv is per polygon
        mesh=ob.getData(False,True)
        # print mesh.faceUV
        face = mesh.faces[faceIndex]
        uvs = face.uv
        if perVertice :
            for j,k in enumerate(uvs):
                if j == vertexIndex :
                    return self.ToVec(uvs[k])
        else :
            return [self.ToVec(uvs[k]) for k in uvs]

    def setUV(self,object,faceIndex,vertexIndex,uv,perVertice=True,uvid=0):
        # triangle 
        ob = self.getObject(object)
        # uv is per polygon
        mesh=ob.getData(False,True)
        # print mesh.faceUV
        face = mesh.faces[faceIndex]
        if perVertice :
            uvs = face.uv
            for j,k in enumerate(uvs):
                if j == vertexIndex :
                    uvs[k] = self.FromVec(uv)
            face.uv = uvs
        else :
            uvs = [self.FromVec(x) for x in uv[0:len(face)]]
            face.uv = uvs
        mesh.update()

    def ToMat(self,host_mat):
        return host_mat[:]

    def FromMat(self,matrice,transpose=True):
        #matrix(16,)
        if matrice is not None :
            m=numpy.array(matrice).reshape(4,4)
            if transpose :
                m=m.transpose()
            mat=m.tolist()
            return Matrix(mat[0],mat[1],mat[2],mat[3])

    def setMeshVerticesCoordinates(self,v,coordinate):
        v.co = self.FromVec(coordinate)
        
    def getMeshVertices(self,poly,transform=False,selected = False):
        editmode = self.toggleEditMode()
        mesh = self.checkIsMesh(poly)
        points = mesh.verts
        if selected:
            listeindice = mesh.verts.selected()       
            vertices = [self.ToVec(points[v].co) for v in listeindice]
            self.restoreEditMode(editmode)
            return vertices, listeindice        
        else:
            vertices = [self.ToVec(v.co) for v in points]
            return vertices
        
    def getMeshNormales(self,poly,selected = False):
        editmode = self.toggleEditMode()
        mesh = self.checkIsMesh(poly)
        points = mesh.verts
        mesh.calcNormals()
        if selected:
            listeindice = mesh.verts.selected()
            vnormals = [points[v].no for v in listeindice]
            self.restoreEditMode(editmode)
            return vnormals, listeindice           
        else :
            vnormals = [v.no for v in points]
            return vnormals

    def getMeshEdge(self,e):
        return e.v1.index,e.v2.index

    def getMeshEdges(self, poly, selected=False):
        editmode = self.toggleEditMode()
        mesh = self.checkIsMesh(poly)
        medges = mesh.edges
        if selected:
            medges_indice = mesh.edges.selected()
            edges = [self.getMeshEdge(medges[e]) for e in medges_indice]
            self.restoreEditMode(editmode)
            return edges,medges_indice
        else :
            edges = [self.getMeshEdge(e) for e in medges]
            return edges

    def setMeshFace(self, mesh, f, indexes):
        #print indexes
        listeV=[]
        for i,v in enumerate(indexes):
            listeV.append(mesh.verts[v])
        f.v = tuple(listeV)
        
    def getMeshFace(self,f):
        if len(f) == 3:
            return f.v[0].index, f.v[1].index, f.v[2].index
        elif len(f) == 4:
            return f.v[0].index, f.v[1].index, f.v[2].index,f.v[3].index

    def getMeshFaces(self,poly,selected = False):
        editmode = self.toggleEditMode()
        mesh = self.checkIsMesh(poly)
        mfaces = mesh.faces
        if selected :
            mfaces_indice = mesh.faces.selected()
            faces = [self.getMeshFace(mfaces[f]) for f in mfaces_indice]
            self.restoreEditMode(editmode)
            return faces, mfaces_indice
        else :
            faces = [self.getMeshFace(f) for f in mfaces]    
            return faces
    
    def selectFaces(self, obj, faces, select=True):
        editmode=self.toggleEditMode()
        
        # Toggle vertex select mode on
        Blender.Mesh.Mode(setBit(Blender.Mesh.Mode(), 2))

        # Blender.Mesh.SelectModes["VERTEX"] == 1 -> bit 0
        # Blender.Mesh.SelectModes["EDGE"] == 2 -> bit 1
        # Blender.Mesh.SelectModes["FACE"] == 4 -> bit 2
        
        mesh = self.getMeshFrom(obj)
        for face in faces:
            if face >= len(mesh.faces):
                continue
            mesh.faces[face].sel = select

        self.restoreEditMode(editmode)
                
    def selectEdges(self, obj, edges, select=True):
        editmode=self.toggleEditMode()
        
        # Toggle vertex select mode on
        Blender.Mesh.Mode(setBit(Blender.Mesh.Mode(), 1))

        # Blender.Mesh.SelectModes["VERTEX"] == 1 -> bit 0
        # Blender.Mesh.SelectModes["EDGE"] == 2 -> bit 1
        # Blender.Mesh.SelectModes["FACE"] == 4 -> bit 2
        
        mesh = self.getMeshFrom(obj)
        for edge in edges:
            if edge >= len(mesh.edges):
                continue
            mesh.edges[edge].sel = select

        self.restoreEditMode(editmode)
   
    def selectVertices(self, obj, vertices, select=True): 
        editmode=self.toggleEditMode()

        # Toggle vertex select mode on
        Blender.Mesh.Mode(setBit(Blender.Mesh.Mode(), 0))

        # Blender.Mesh.SelectModes["VERTEX"] == 1 -> bit 0
        # Blender.Mesh.SelectModes["EDGE"] == 2 -> bit 1
        # Blender.Mesh.SelectModes["FACE"] == 4 -> bit 2
        
        mesh = self.getMeshFrom(obj)

        for vertex in vertices:
            if vertex >= len(mesh.verts):
                continue
            mesh.verts[vertex].sel = select

        self.restoreEditMode(editmode)

    def DecomposeMesh(self,poly,edit=True,copy=True,tri=True,transform=True):
        import numpy
        print poly
        mesh = self.getMeshFrom(poly)
        print mesh
        points = mesh.verts
        faces = self.getMeshFaces(mesh)
        mesh.calcNormals()
        vnormals = [v.no for v in points]
        vertices = [v.co for v in points]
        if transform :
            mmat = self.getObject(poly).getMatrix()
            mat = mmat.transpose()
            vertices = self.ApplyMatrix(vertices,mat)
        return faces,numpy.array(vertices),numpy.array(vnormals)
    
    def triangulate(self,poly):
        # select poly
        editmode=self.toggleEditMode()
        mesh = self.checkIsMesh(poly)      
        mesh.quadToTriangle()
        self.restoreEditMode(editmode)
        
    def backingVertexColor(self,obj,name="bakeColor",filename="~/color.png"):
        #need unwrapped mesh ie in selection the second one or the only one
        #then need to create the image texture
        #then back
        #then link texture to material
        obj = self.getObject(obj)
        mesh = obj.getData(mesh=1)
        nmesh = NMesh.GetRaw(mesh.name)
        mats = self.getMaterialObject(obj)
        if not len(mats):
            mats = self.getMaterialObject(nmesh) #this work on NMesh not Mesh
        print mats
        mat = None
        if len(mats):
            mat = mats[0]
        scn = self.getCurrentScene()
        #compute UV unwrapping
        #select the object
        self.ObjectsSelection([obj,],typeSel="new")
        #execute the 
        import upy.blender.uvcalc_smart_project as uvc
        Blender.Window.EditMode(1)
        #this should create the UV coordinate of the unfold surface
        if not mesh.faceUV:
            uvc.doit()
        #now we have uv coordinate, need an image to bake
        #mat = self.createTexturedMaterial("uvMat","/Users/Shared/uv.png")
        img = Blender.Image.New(name, 800, 800, 32)
        img.setFilename(filename)
        img.save()
        #problem for make image current in UV editor
        img.makeCurrent()
        bpy.data.images.active = img
        #need an update?
        #self.assignMaterial([mat,],obj,texture=True)
        #now we can bake
        Blender.Window.EditMode(0)
        context = scn.getRenderingContext()
        context.bakeClear = True
        context.bakeMode = Render.BakeModes.TEXTURE #NORMALS
        context.bakeNormalSpace = Render.BakeNormalSpaceModes.CAMERA #TANGENT
        context.bake()
        img.save()
        #now link to the objetc with a new material ? or the current material
        nmat = self.createTexturedMaterial("uvMat",filename,mat=mat)
        if mat is None :
            self.assignMaterial(obj,[nmat,],texture=True)
        #context.bakeToActive = True
        
