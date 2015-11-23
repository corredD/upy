
"""
    Copyright (C) <2010>  Autin L. TSRI
    
    This file git_upy/dejavuTk/dejavuHelper_mgl.py is part of upy.

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
Created on Wed Feb  9 11:18:03 2011

@author: -
"""

# -*- coding: utf-8 -*-
"""
Created on Sun Dec  5 23:30:44 2010

@author: Ludovic Autin - ludovic.autin@gmail.com
"""
#DejaVu module
import DejaVu
from DejaVu.Viewer import Viewer
from DejaVu.Geom import Geom
from DejaVu.Spheres import Spheres
from DejaVu.Cylinders import Cylinders
from DejaVu.Box import Box
from DejaVu.glfLabels import GlfLabels as Labels
from DejaVu.IndexedPolygons import IndexedPolygons
from DejaVu.Polylines import Polylines
from DejaVu.Texture import Texture
from DejaVu import Viewer
#standardmodule
import sys
import os
import struct
import string
import types
import math
from math import *
#from types import StringType, ListType

#from DejaVu import Viewer
           
import numpy
from numpy import matrix
import Image
#base helper class
from upy import hostHelper
#from upy import ray

try :
    import collada
except :
    collada = None
    print ("can't import pycollada ")

#Problem instance doesnt really exist as its. Or its instance of mesh/sphere/cylinder directly.
#check autofill display
#we need to create a new class of object that will represent an instance...
class Instance:
    def __init__(self,name,geom,position=None, matrice=None):
        self.name = name        
        self.geom = geom
        self.id = len(geom.instanceMatricesFortran)
        self.matrice = [ 1.,  0.,  0.,  0.,  0.,  1.,  0.,  0.,  0.,  0.,  1.,  0.,  0.,
         0.,  0.,  1.]
        self.isinstance = True
        if matrice is not None :
           self.matrice = numpy.array(matrice).reshape((16,))#need to beflatten (16,) 
        matrices =  geom.instanceMatricesFortran.tolist()
        matrices.append(self.matrice)
        m=[numpy.array(mat).reshape((4,4)) for mat in matrices]
        geom.Set(instanceMatrices=numpy.array(m))

    def SetTransformation(self,matrice):
        matrices =  self.geom.instanceMatricesFortran.tolist()
        matrices[self.id] = numpy.array(matrice).reshape((16,))
        #print (matrices)
        m=[numpy.array(mat).reshape((4,4)) for mat in matrices]
        print ("set")
        self.geom.Set(instanceMatrices=numpy.array(m), visible=1)

    def SetTranslation(self,pos):
        pass
                
class dejavuHelper(hostHelper.Helper):
    """
    The DejaVu helper abstract class
    ============================
        This is the DejaVu helper Object. The helper 
        give access to the basic function need for create and edit a host 3d object and scene.
    """    
    #this id can probably found in c4d.symbols
    #TAG ID
    SPLINE = "kNurbsCurve"
    INSTANCE = "Dejavu.Geom"
    EMPTY = "Dejavu.Geom"
    SPHERE = 'DejaVu.Spheres'
    POLYGON = "DejaVu.IndexedPolygons"
    #msutil = om.MScriptUtil()
    pb = False
    VERBOSE=0
    DEBUG=0
    viewer = None
    host = "dejavu"
    
    def __init__(self,master=None,vi=None):
        hostHelper.Helper.__init__(self)
        #we can define here some function alias
        self.nogui = False        
        
        print ("INITHELPER1")
        if master is not None :
            if type(master) is dict :
                self.viewer = master["master"]
            else :
                self.viewer = master
            if self.viewer == "nogui" :
                self.nogui = True
            elif not isinstance(self.viewer,Viewer) or self.viewer is None :
                self.viewer = Viewer(master)              
        if vi is not None :
            self.viewer = vi
            if self.viewer == "nogui" :
                self.nogui = True
            elif not isinstance(self.viewer,Viewer) or self.viewer is None :
                print ("no Viewer pass")
        if self.viewer is None:
            print ("no Viewer golboals")
            dicG = globals()
            for d in dicG: 
               if isinstance(dicG[d],Viewer):
                    self.viewer = dicG[d]
                    break
        if self.viewer is None:
            self.viewer = Viewer()
        
        #self.getCurrentScene = c4d.documents.GetActiveDocument
        if self.viewer is not None and not self.nogui:
            self.AddObject = self.viewer.AddObject
        self.hext = "dae"

    def updateAppli(self,*args,**kw):
        return self.update(*args,**kw)
    
    def Cube(self,*args,**kw):
        return self.box(*args,**kw)
        
    def Box(self,*args,**kw):
        return self.box(*args,**kw)
    
    def Polylines(self,*args,**kw):
        return Polylines(*args,**kw) 

    def Spheres(self,*args,**kw):
        return Spheres(*args,**kw)
        
    def Cylinders(self,*args,**kw):
        return Cylinders(*args,**kw)

    def Geom(self,*args,**kw):
        return Geom(*args,**kw)

    def Labels(self,*args,**kw):
        return Labels(*args,**kw)

    def IndexedPolygons(self,*args,**kw):
        return IndexedPolygons(*args,**kw)
        
    def setViewer(self,vi):
        self.viewer = vi
        self.AddObject = self.viewer.AddObject
        self.Labels = self.viewer.Labels

    def getCurrentScene(self):
        #actually return the Viewer instance
        return self.viewer

    def progressBar(self,progress=None,label=None):
        """ update the progress bar status by progress value and label string
        @type  progress: Int/Float
        @param progress: the new progress
        @type  label: string
        @param label: the new message to put in the progress status
        """   
        #resetProgressBar
        print ("Progress ",str(progress),label)
        return
        from mglutil.gui.BasicWidgets.Tk.progressBar import ProgressBar
        if not hasattr(self.viewer,"Bar"):
            bar = ProgressBar(master=self.viewer.master,width=150, height=18)
            bar.configure(mode='percent', progressformat='ratio')
            self.viewer.Bar = bar
        if progress is not None :
            self.viewer.Bar.set(progress)
        if label is not None:
            self.viewer.Bar.configure(labeltext=label)
        self.update()
        
    def resetProgressBar(self):
        """reset the Progress Bar, using value"""
        return
        if hasattr(self.viewer,"Bar"):
            self.viewer.Bar.reset()
        self.update()
        
    def update(self):
        vi = self.getCurrentScene()
        vi.OneRedraw()
        vi.update()
#        vi.Redraw()

    def getType(self,object):
        return object.__module__

    def getMesh(self,m,**kw):
        if type(m) is str:
            m = self.getCurrentScene().findGeomsByName(m)
        if m is not None :
            return m
        else :
            return None
            
    def getName(self,o):
        if type(o) is str:
            o = self.getCurrentScene().findGeomsByName(o)
        else :
            print ("getName",o,type(o))
        return o.name
    
    def getObject(self,name):
        obj=None
        if type(name) != str and type(name) != unicode: 
            return name
        try :
            obj=self.getCurrentScene().findGeomsByName(name)
            if len(obj) == 0 : 
                obj = None
            else :
                for o in obj :
                    if o.name == name :
                        return o
                return None
        except : 
            print ("problem get Object",name)
            obj=None
        return obj

    def getChilds(self,obj):
        return obj.children

    def deleteObject(self,obj):
        vi= self.getCurrentScene()
        if hasattr(obj,"isinstance"):
            self.deleteInstance(obj)
            return
        try :
#            print obj.name
            vi.RemoveObject(obj)
        except Exception as e:
            print("problem deleting ", obj,e)
    
    def newEmpty(self,name,location=None,parentCenter=None,display=1,visible=0,**kw):
        empty = Geom(name, visible=display)
        if location != None :
            if parentCenter != None : 
                location = location - parentCenter
            empty.SetTranslation(numpy.array(location))
        parent = None
        if "parent" in kw :
            parent = kw["parent"]
        self.addObjectToScene(None,empty,parent=parent)    
        return empty

    def updateMasterInstance(self,master, newMesh,**kw):
        #get the instancematrix frommaster
        #apply them to new newMesh
        pass

    def deleteInstance(self,instance):
        #pop the instance from the instanceMatrice
        #delete the object
        m=instance.geom.instanceMatricesFortran[:]
        m=numpy.delete(m,instance.id,0)
        m=m.tolist()
#        m.pop(instance.id)
        matrice=[numpy.array(mat).reshape((4,4)) for mat in m]
        instance.geom.Set(instanceMatrices=numpy.array(matrice))
        del instance
        
    def newInstance(self,name,object,location=None,c4dmatrice=None,matrice=None,
                    parent = None,material=None):
        object = self.getObject(object)
        if isinstance(object,Spheres):
            #create a sphere
            c=object.materials[1028].getState()['diffuse'][0][:3]
            geom = self.Spheres(name+"copy",radii=[object.radius],centers=[[0,0,0]],
                                visible=1,inheritMaterial = False,)
            geom.Set(materials=[c,])
            self.addObjectToScene(None,geom,parent=parent)
        elif isinstance(object,IndexedPolygons):    
            geom = IndexedPolygons(name, vertices=object.getVertices(),
                      faces=object.getFaces(), vnormals=object.getVNormals(),
                      inheritMaterial = False,)
            geom.materials[1028].Set(object.materials[1028].getState())
            geom.materials[1029].Set(object.materials[1028].getState())
            self.addObjectToScene(None,geom,parent=parent) 
        else :
            geom = Instance(name,object,position=location)
            #currentMatrices = geom.instanceMatricesFortran
            #currentMatrices.append(numpy.identity)
        if location != None :
            self.setTranslation(geom,pos=location)
        return geom
#        instance = c4d.BaseObject(c4d.Oinstance)
#        instance[1001]=iMe[atN[0]]        
#        instance.SetName(n+"_"+fullname)#.replace(":","_")
#        if location != None :
#            instance.SetAbsPos(self.FromVec(location))
#        if c4dmatrice !=None :
#            #type of matre
#            instance.SetMg(c4dmatrice)
#        if matrice != None:
#            mx = self.matrix2c4dMat(matrice)
#            instance.SetMg(mx)
#        return instance
#        return object
        
    def setObjectMatrix(self,object,matrice,c4dmatrice=None,**kw):
#            print (object, matrice)
            if "transpose" in kw and not hasattr(object,"isinstance"):
                if kw["transpose"]:
                    matrice = numpy.array(matrice).transpose()                
            object.SetTransformation(matrice)
#        if c4dmatrice !=None :
#            #type of matre
#            object.SetMg(c4dmatrice)
#        else :
#            mx = self.matrix2c4dMat(matrice,transpose=False)
#            object.SetMg(mx)
    
    def concatObjectMatrix(self,object,matrice,c4dmatrice=None,local=True):
#        #local or global?
#        cmg = object.GetMg()
#        cml = object.GetMl()
#        if c4dmatrice !=None :
#            #type of matrice
#            if local :
#                object.SetMl(cml*c4dmatrice)
#            else :
#                object.SetMg(cmg*c4dmatrice)
#        else :
#            mx = self.matrix2c4dMat(matrice,transpose=False)
#            if local :
#                object.SetMl(cml*mx)
#            else :
#                object.SetMg(cmg*mx)
        pass
        
    def GetAbsPosUntilRoot(self,obj):
#        stop = False
#        parent = obj.GetUp()
#        pos=self.FromVec((0.,0.,0.))
#        while not stop :
#            pos = pos + parent.GetAbsPos()
#            parent = parent.GetUp()
#            if parent is None :
#                stop = True
        return [0,0.,0.]                                            
        
    def addObjectToScene(self,doc,obj,parent=None,centerRoot=True,rePos=None):
        #doc.start_undo()
        if self.nogui :
            return
        if doc is None :
            if self.viewer is None :
                print ("#ERROR there is no viewer setup")
                return
            doc = self.viewer
        if parent != None : 
            if type(parent) == str : parent = self.getObject(parent)
            doc.AddObject(obj,parent=parent)
            if centerRoot :
                currentPos = obj.translation      
                if rePos != None : 
                    parentPos = rePos
                else :
                    parentPos = self.GetAbsPosUntilRoot(obj)#parent.GetAbsPos()                            
                obj.SetTranslation(currentPos-parentPos)                
        else : 
#                print doc,obj
            doc.AddObject(obj)
        #verify the viewer
        if obj.viewer is None :
            obj.viewer = doc
            
    def addCameraToScene(self,name,Type,focal,center,sc):
        pass    
    
    def addLampToScene(self,name,Type,rgb,dist,energy,soft,shadow,center,sc):
        pass
    
    def reParent(self,obj,parent):
        vi = self.getCurrentScene()
        parent = self.getObject(parent)
        if parent is None :
            return
        if type(obj) == list or type(obj) == tuple:
            [vi.ReparentObject(self.getObject(o),parent,objectRetainsCurrentPosition=True) for o in obj]
        else :
            obj = self.getObject(obj)
            if obj.viewer is None :
                obj.viewer = vi            
            vi.ReparentObject(obj,parent,objectRetainsCurrentPosition=True)
    
    def setInstance(self,name,object,location=None,c4dmatrice=None,matrice=None):
#        instance = c4d.BaseObject(c4d.Oinstance)
#        instance[1001]=object        
#        instance.SetName(name)#.replace(":","_")
#        if location != None :
#            instance.SetAbsPos(self.FromVec(location))
#        if c4dmatrice !=None :
#            #type of matre
#            instance.SetMg(c4dmatrice)
#        if matrice != None:
#            mx = self.matrix2c4dMat(matrice)
#            instance.SetMl(mx)
#            p = instance.GetAbsPos()
#            instance.SetAbsPos(c4d.Vector(p.y,p.z,p.x))
#        return instance
        return None

    def getTranslation(self,name):
        return self.getObject(name).translation #or getCumulatedTranslation

    def setTranslation(self,name,pos=[0.,0.,0.]):
        self.getObject(name).SetTranslation(self.FromVec(pos))

    def translateObj(self,obj,position,use_parent=True):
        if len(position) == 1 : c = position[0]
        else : c = position
        #print "upadteObj"
        newPos=self.FromVec(c)
        
        if use_parent : 
            parentPos = self.GetAbsPosUntilRoot(obj)#parent.GetAbsPos()
            newPos = newPos - parentPos
        obj.ConcatTranslation(newPos)
        
    def scaleObj(self,obj,sc):
        if type(sc) is float :
            sc = [sc,sc,sc]
        #obj.scale = sc #SetScale()?
#        obj.SetScale(numpy.array(sc))
        obj.Set(scale=numpy.array(sc))

    def rotateObj(self,obj,rot):
        #take radians, give degrees
        mat  = self.eulerToMatrix(rot)
        obj.Set(rotation = numpy.array(mat).flatten()) #obj.rotation 

    def getTransformation(self,geom):
        if self.nogui :
            return numpy.identity(4)
        geom = self.getObject(geom)
        return geom.GetMatrix(geom.LastParentBeforeRoot())

    def toggleDisplay(self,obj,display,**kw):
        obj = self.getObject(obj)
        if obj is None :
            return
        obj.Set(visible = display)

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


    def getCurrentSelection(self,):
        """
        Return the current/active selected object in the document or scene
        DejaVu support only one object at a time. 
        @rtype:   liste
        @return:  the list of selected object
        """        
        return [self.getCurrentScene().currentObject]
        
    #####################MATERIALS FUNCTION########################
    def addMaterial(self,name,color):
        return color

    def createTexturedMaterial(self,name,filename,normal=False,mat=None):
        footex = Texture()
        im = Image.open(filename)
        footex.Set(enable=1, image=im)
        return footex

    def assignMaterial(self,object,mat,texture= False):
        if texture :
            object.Set(texture=mat)
        else :
            object.Set(materials=[mat,])

    def changeObjColorMat(self,obj,color):
#        doc = self.getCurrentScene()
        obj.Set(inheritMaterial = False,materials=[color],redo=1)
    
    def getMaterialObject(self,o):
        pass
        return None

    def getMaterial(self,mat):
        return mat

    def getAllMaterials(self):
        return []
        
    def getMaterialName(self,mat):
        return None

    def ObjectsSelection(self,listeObjects,typeSel="new"):
        """
        Modify the current object selection.
        
        @type  listeObjects: list
        @param listeObjects: list of object to joins
        @type  typeSel: string
        @param listeObjects: type of modification: new,add,...
    
        """    
        pass
#        dic={"add":c4d.SELECTION_ADD,"new":c4d.SELECTION_NEW}
#        sc = self.getCurrentScene()
#        [sc.SetSelection(x,dic[typeSel]) for x in listeObjects]
    

    def oneCylinder(self,name,head,tail,radius=None,instance=None,material=None,
                    parent = None,color=None):
        #laenge,mx=self.getTubeProperties(head,tail)
        lenght = self.measure_distance(head,tail)
        if True:#instance is None:
            stick = self.getObject(name)
            if stick is None :
                v = numpy.array([tail,head])
                f = numpy.arange(len(v))
                f.shape=(-1,2)
                stick = Cylinders(name,inheritMaterial = False,
                            vertices=v,faces=f,
                               radii=[1])
                #stick = self.Cylinder(name,length=lenght,pos =head)
                self.addObjectToScene(self.getCurrentScene(),stick,parent=parent)
            else :
                pos = numpy.array(head)
                v = numpy.array([tail,head])
                f = numpy.arange(len(v))
                f.shape=(-1,2)
                stick.Set(vertices=v,faces=f,redo=1)
        else :
            stick = instance
            v = instance.vertexSet.vertices.array
            i = len(v)
#            v = numpy.concatenate((v,numpy.array([head,tail])))
            instance.vertexSet.vertices.AddValues([head,tail])
            instance.faceSet.faces.AddValues([i,i+1])
            r = instance.vertexSet.radii.array[0]
            instance.vertexSet.radii.AddValues(r)
            instance.Set(redo=1)
        return stick
        
    def Cylinder(self,name,radius=1.,length=1.,res=0, pos = [0.,0.,0.],parent=None,**kw):
#        QualitySph={"0":16,"1":3,"2":4,"3":8,"4":16,"5":32}
        pos = numpy.array(pos)
        v = numpy.array([pos,pos + numpy.array([0.,length,0.])])
        f = numpy.arange(len(v))
        f.shape=(-1,2)
        baseCyl = Cylinders(name,inheritMaterial = False,quality=res,
                            vertices=v,faces=f,
                               radii=[radius])#, visible=1)
        #if str(res) not in QualitySph.keys():
        self.addObjectToScene(self.getCurrentScene(),baseCyl,parent=parent)
        return [baseCyl,baseCyl]

    def updateTubeMesh(self,mesh,cradius=1.0,quality=0,**kw):
        #change the radius to cradius
        mesh=self.getMesh(mesh)
        if type(mesh) is list :
            mesh= mesh[0]
#        mesh=geom.mesh.GetDown()#should be the cylinder
        #mesh[5000]=cradius
#        cradius = cradius*1/0.2
        #should used current Y scale too
        mesh.Set(radii=[cradius],quality=quality)

        
    def Sphere(self,name,radius=1.0,res=0,parent=None,color=None,mat=None,pos=None):
        QualitySph={"0":6,"1":4,"2":5,"3":6,"4":8,"5":16} 
        baseSphere = self.Spheres(name,radii=[radius,],centers=[[0.,0.,0.]],
                                quality=res,inheritMaterial = False, visible=1)
        if mat is not None :
            mat = self.getMaterial(mat)
            self.assignMaterial(mat, baseSphere)
        else :
            if color != None :
                #color = [1.,1.,0.]
                baseSphere.Set(materials=[color,])
#                mat = self.addMaterial(name,color)
#                self.assignMaterial(mat, baseSphere)
        self.addObjectToScene(None,baseSphere,parent=parent)
        if pos != None :
            self.setTranslation(baseSphere,pos)
        return [baseSphere,baseSphere]
    		              
#    def updateSphereMesh(self,mesh,verts=None,faces=None,basemesh=None,
#                         scale=1.,**kw):
#        mesh=self.getMesh(mesh)
#        mesh[905]=self.FromVec([scale,scale,scale])
#        mesh.Message(c4d.MSG_UPDATE)
#        
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
#    
##    def clonesAtomsSphere(self,name,x,iMe,doc,mat=None,scale=1.0,
##                          Res=32,R=None,join=0):
##        spher=[]
##        k=0
##        n='S'
##        AtmRadi = {"A":1.7,"N":1.54,"C":1.7,"P":1.7,"O":1.52,"S":1.85,"H":1.2}
##        
##        if scale == 0.0 : scale = 1.0
##        if mat == None : mat=create_Atoms_materials()
##        if name.find('balls') != (-1) : n='B'
##        for j in range(len(x)): spher.append(None)
##        for j in range(len(x)):
##            #at=res.atoms[j]
##            at=x[j]
##            atN=at.name
##            #print atN
##            fullname = at.full_name()
##            #print fullname
##            atC=at._coords[0]
##            spher[j] = iMe[atN[0]].GetClone()
##            spher[j].SetName(n+"_"+fullname)#.replace(":","_"))
##            spher[j].SetAbsPos(c4d.Vector(float(atC[2]),float(atC[1]),float(atC[0])))
##            spher[j][905]=c4d.Vector(float(scale),float(scale),float(scale))
##            #
##            #print atN[0]
##            #print mat[atN[0]]    
##            texture = spher[j].MakeTag(c4d.Ttexture)
##            texture[1010] = mat[atN[0]]
##            k=k+1
##        return spher
#        
    def instancesSphere(self,name,centers,radii,meshsphere,
                        colors,scene,parent=None):
        sphs=[]
        vertices = []
        for i in range(len(centers)):
            vertices.append(centers[i])        
        meshsphere.Set(vertices=vertices,materials=colors,radii=radii)
        return meshsphere
            
##    def spheresMesh(self,name,x,mat=None,scale=1.0,Res=32,R=None,join=0):
##        if scale == 0.0 : scale =1.
##        scale = scale *2.
##        spher=[]
##        if Res == 0 : Res = 10.
##        else : Res = Res *5.
##        k=0
##        if mat == None : mat=self.create_Atoms_materials()
##        #print len(x)
##        for j in range(len(x)): spher.append(None)
##        for j in range(len(x)):
##            #at=res.atoms[j]
##            at=x[j]
##            atN=at.name
##            #print atN
##            fullname = at.full_name()
##            #print fullname
##            atC=at._coords[0]
##            #if R !=None : rad=R
##            #elif AtmRadi.has_key(atN[0]) : rad=AtmRadi[atN[0]]
##            #else : rad=AtmRadi['H']
##            #print  at.vdwRadius
##            rad=at.vdwRadius
##            #print rad
##            spher[j] = c4d.BaseObject(c4d.Osphere)
##            spher[j].SetName(fullname.replace(":","_"))
##            spher[j][PRIM_SPHERE_RAD] = float(rad)*float(scale)
##            spher[j].SetAbsPos(c4d.Vector(float(atC[0]),float(atC[1]),float(atC[2])))
##            spher[j].MakeTag(c4d.Tphong)
##            # create a texture tag on the PDBgeometry object
##            #texture = spher[j].MakeTag(c4d.Ttexture)
##            #create the dedicayed material
##            #print mat[atN[0]]
##            #texture[1010] = mat[atN[0]]
##            #spher.append(me)
##        k=k+1
##        return spher
#
    def instancesCylinder(self,name,points,faces,radii,
                          mesh,colors,scene,parent=None):
        mesh.Set(vertices=points,faces=faces,radii=radii,materials=colors)
        return mesh

#    def updateTubeMesh(self,mesh,cradius=1.0,quality=0,**kw):
#        mesh=self.getMesh(mesh)
##        mesh=geom.mesh.GetDown()#should be the cylinder
#        #mesh[5000]=cradius
##        cradius = cradius*1/0.2
#        mesh[905]=c4d.Vector(float(cradius),1.,float(cradius))
#        mesh.Message(c4d.MSG_UPDATE)
#        #pass
#      
#    def updateTubeObj(self,coord1,coord2,bicyl=False):
#        laenge,mx=self.getTubeProperties(coord1,coord2)
#        o.SetMl(mx)
#        o[905,1001]=float(laenge)
#        parentPos = self.GetAbsPosUntilRoot(o)#parent.GetAbsPos()
#        currentPos = o.GetAbsPos()
#        o.SetAbsPos(currentPos - parentPos)      
#    	
##    def oldTube(set,atms,points,faces,doc,mat=None,res=32,size=0.25,sc=1.,join=0,instance=None,hiera = 'perRes'):
##     bonds, atnobnd = set.bonds
##     backbone = ['N', 'CA', 'C', 'O']
##     stick=[]
##     tube=[]
##     #size=size*2.
##     #coord1=x[0].atms[x[0].atms.CApos()].xyz() #x.xyz()[i].split()
##     #coord2=x[1].atms[x[1].atms.CApos()].xyz() #x.xyz()[i+1].split()
##     #print len(points)
##     #print len(faces)
##     #print len(atms)
##     atm1=bonds[0].atom1#[faces[0][0]]
##     atm2=bonds[0].atom2#[faces[0][1]]
##     #name="T_"+atm1.name+str(atm1.number)+"_"+atm2.name+str(atm2.number) 
##     name="T_"+atm1.full_name()+"_"+atm2.name
##     mol=atm1.getParentOfType(Protein)
##     laenge,mx=getStickProperties(points[faces[0][0]],points[faces[0][1]]) 
##     if mat == None : mat=create_sticks_materials()
##     if instance == None :
##         stick.append(c4d.BaseObject(CYLINDER))#(res, size, laenge/sc) #1. CAtrace, 0.25 regular |sc=1 CATrace, 2 regular
##         stick[0].SetMg(mx)
##         stick[0][5005]=laenge/sc#size
##         stick[0][5000]=size#radius
##         stick[0][5008]=res#resolution
##         stick[0][5006]=2#heght segment
##     else :
##         stick.append(c4d.BaseObject(INSTANCE))
##         stick[0][1001]=instance
##         stick[0].SetMg(mx)     
##         stick[0][905,1001]=float(laenge)
##     texture=stick[0].MakeTag(c4d.Ttexture)
##     #print  atms[faces[0][0]].name[0]+atms[faces[0][1]].name[0]
##     name1=atms[faces[0][0]].name[0]
##     name2=atms[faces[0][1]].name[0]
##     if name1 not in AtmRadi.keys(): name1="A"
##     if name2 not in AtmRadi.keys(): name2="A"
##     texture[1010]=mat[name1+name2]              
##     stick[0].SetName(name)
##     #stick[0].SetAbsPos(c4d.Vector(float(z1+z2)/2,float(y1+y2)/2,float(x1+x2)/2))
##     #stick[0].set_rot(c4d.Vector(float(wz),float(0),float(wsz)))
##     #stick[0][904,1000] = wz #RY/RH
##     #stick[0][904,1002] = wsz #RZ/RB
##     stick[0].MakeTag(c4d.Tphong)
##     hierarchy=parseObjectName("B_"+atm1.full_name())
##     #parent=getObject(mol.geomContainer.masterGeom.chains_obj[hierarchy[1]+"_balls"])
##     if hiera == 'perRes' :
##         parent = getObject(mol.geomContainer.masterGeom.res_obj[hierarchy[2]])
##     elif hiera == 'perAtom' :
##         if atm1.name in backbone : 
##             parent = getObject(atm1.full_name()+"_bond")
##         else :
##             parent = getObject(atm1.full_name()+"_sbond")
##     else :
##         parent=getObject(mol.geomContainer.masterGeom.chains_obj[hierarchy[1]+"_balls"])
##     addObjectToScene(doc,stick[0],parent=parent)
##     for i in range(1,len(faces)):
##      atm1=bonds[i].atom1#[faces[i][0]]
##      atm2=bonds[i].atom2#[faces[i][1]]
##      #name="T_"+atm1.name+str(atm1.number)+"_"+atm2.name+str(atm2.number)
##      name="T_"+atm1.full_name()+"_"+atm2.name
##      laenge,mx=getStickProperties(points[faces[i][0]],points[faces[i][1]])
##      if instance == None :
##         stick.append(c4d.BaseObject(CYLINDER))#(res, size, laenge/sc) #1. CAtrace, 0.25 regular |sc=1 CATrace, 2 regular
##         stick[i].SetMl(mx)
##         stick[i][5005]=laenge/sc#radius
##         stick[i][5000]=size#height/size
##         stick[i][5008]=res#resolution rotation segment
##         stick[i][5006]=2#heght segment     
##      else :
##         stick.append(c4d.BaseObject(INSTANCE))
##         stick[i][1001]=instance
##         stick[i].SetMl(mx)
##         stick[i][905,1001]=float(laenge)
##      texture=stick[i].MakeTag(c4d.Ttexture)
##      #print i,i+1
##      name1=atms[faces[i][0]].name[0]
##      name2=atms[faces[i][1]].name[0]
##      if name1 not in AtmRadi.keys(): name1="A"
##      if name2 not in AtmRadi.keys(): name2="A"
##    
##      if i < len(atms) :
##         #print  name1+name2
##         texture[1010]=mat[name1+name2]
##      else :
##         texture[1010]=mat[name1+name2]                                 
##      stick[i].SetName(name)
##      #stick[i].SetAbsPos(c4d.Vector(float(z1+z2)/2,float(y1+y2)/2,float(x1+x2)/2))
##      #stick[i].set_rot(c4d.Vector(float(wz),float(0.),float(wsz)))
##      stick[i].SetMl(mx)
##      stick[i].MakeTag(c4d.Tphong)
##      hierarchy=parseObjectName("B_"+atm1.full_name())
##      #parent=getObject(mol.geomContainer.masterGeom.chains_obj[hierarchy[1]+"_balls"])
##      if hiera == 'perRes' :
##         parent = getObject(mol.geomContainer.masterGeom.res_obj[hierarchy[2]])
##      elif hiera == 'perAtom' :
##         if atm1.name in backbone : 
##             parent = getObject(atm1.full_name()+"_bond")
##         else :
##             parent = getObject(atm1.full_name()+"_sbond")
##      else :
##         parent=getObject(mol.geomContainer.masterGeom.chains_obj[hierarchy[1]+"_balls"])
##    
##      addObjectToScene(doc,stick[i],parent=parent)
##    
##     #if join==1 : 
##     #    stick[0].join(stick[1:])
##     #    for ind in range(1,len(stick)):
##            #obj[0].join([obj[ind]])
##    #        scn.unlink(stick[ind])
##        #obj[0].setName(name)
##     return [stick]
##    
##     
    def FromVec(self,points,pos=True):
        return numpy.array(points)#numpy.array(float(points[0]),float(points[1]),float(points[2]))
#    
    def ToVec(self,v):
        return v
#    
#    def getCoordinateMatrix(self,pos,direction):
#      offset=pos
#      v_2=direction
#      v_2.Normalize()
#      v_1=c4d.Vector(float(1.),float(0.),float(0.))
#      v_3=c4d.Vector.Cross(v_1,v_2)
#      v_3.Normalize()
#      v_1=c4d.Vector.Cross(v_2,v_3)
#      v_1.Normalize()
#     #from mglutil.math import rotax
#     #pmx=rotax.rotVectToVect([1.,0.,0.], [float(z1-z2),float(y1-y2),float(x1-x2)], i=None)
#      return c4d.Matrix(offset,v_1, v_2, v_3)
#    
#    def getCoordinateMatrixBis(self,pos,v1,v2):
#      offset=self.FromVec(pos)
#      v_2=self.FromVec(v2)
#      v_1=self.FromVec(v1)
#      v_3=c4d.Vector.Cross(v_1,v_2)
#      v_3.Normalize()
#     #from mglutil.math import rotax
#     #pmx=rotax.rotVectToVect([1.,0.,0.], [float(z1-z2),float(y1-y2),float(x1-x2)], i=None)
#      return c4d.Matrix(offset,v_1, v_2, v_3)
#    
#    def loftnurbs(self,name,mat=None):
#        loft=c4d.BaseObject(self.LOFTNURBS)
#        loft[1008]=0 #adaptive UV false
#        loft.SetName(name)
#        loft.MakeTag(c4d.Tphong)
#        texture = loft.MakeTag(c4d.Ttexture)
#        texture[1004]=6 #UVW Mapping
#        #create the dedicayed material
#        if mat is not None : 
#            texture[1010] = mat
#        return loft
#    
#    def sweepnurbs(self,name,mat=None):
#        loft=c4d.BaseObject(c4d.Osweep)
#        loft.SetName(name)
#        loft.MakeTag(c4d.Tphong)
#        #create the dedicayed material
##        if mat == None : 
##                texture[1010] = self.create_loft_material(name='mat_'+name)
##        else : texture[1010] = mat
#        if mat is not None : 
#            texture = loft.MakeTag(c4d.Ttexture)
#            texture[1010] = mat
#        return loft
#    
#    def addShapeToNurb(self,loft,shape,position=-1):
#        list_shape=loft.GetChilds()
#        shape.insert_after(list_shape[position])
#    
#    #def createShapes2D()
#    #    sh=c4d.BaseObject(dshape)
#    
    def spline(self,name, points,close=0,type=1,scene=None,parent=None):
        f=[[x,x+1] for x in range(len(points))]
        spline=self.Polylines(name, vertices=points,faces=f)
        self.AddObject(spline, parent=parent)
        return spline,None

    def update_spline(self,name,new_points):
        spline=self.getObject(name)
        if spline is None : 
            return False
        f=[[x,x+1] for i in range(len(new_points))]
        spline.Set(vertices=new_points,faces=f)
        return True
#        
#    def createShapes2Dspline(self,doc=None,parent=None):
#        circle=c4d.BaseObject(self.CIRCLE)
#        circle[2012]=float(0.3)
#        circle[2300]=1
#        if doc : addObjectToScene(doc,circle,parent=parent )
#        rectangle=c4d.BaseObject(self.RECTANGLE)
#        rectangle[2060]=float(2.2)
#        rectangle[2061]=float(0.7)
#        rectangle[2300]=1
#        if doc : addObjectToScene(doc,rectangle,parent=parent )
#        fourside=c4d.BaseObject(self.FOURSIDE)
#        fourside[2121]=float(2.5)
#        fourside[2122]=float(0.9)
#        fourside[2300]=1
#        if doc : addObjectToScene(doc,fourside,parent=parent )
#        shape2D={}
#        pts=[[0,0,0],[0,1,0],[0,1,1],[0,0,1]]
#        #helixshape
#        helixshape=fourside.get_real_spline()#spline('helix',pts,close=1,type=2)#AKIMA
#        helixshape.SetName('helix')
#        shape2D['Heli']=helixshape
#        #sheetshape
#        sheetshape=rectangle.get_real_spline()#spline('sheet',pts,close=1,type=0)#LINEAR
#        sheetshape.SetName('sheet')
#        shape2D['Shee']=sheetshape
#        #strandshape
#        strandshape=sheetshape.GetClone()
#        strandshape.SetName('strand')
#        shape2D['Stra']=strandshape
#        #coilshape
#        coilshape=circle.get_real_spline()#spline('coil',pts,close=1,type=4)#BEZIER
#        coilshape.SetName('coil')
#        shape2D['Coil']=coilshape
#        #turnshape
#        turnshape=coilshape.GetClone()
#        turnshape.SetName('turn')
#        shape2D['Turn']=turnshape
#        if doc : 
#            for o in shape2D.values() :
#                self.addObjectToScene(doc,o,parent=parent )    
#        return shape2D,[circle,rectangle,fourside,helixshape,sheetshape,strandshape,coilshape,turnshape]
#
#
#    def constraintLookAt(self,object):
#        """
#        Cosntraint an hostobject to llok at the camera
#        
#        @type  object: Hostobject
#        @param object: object to constraint
#        """
#        self.getObject(object)
#        object.MakeTag(self.LOOKATCAM)
#
#    def updateText(self,text,string="",parent=None,size=None,pos=None,font=None):
#        text = self.getObject(text)
#        if text is None :
#            return
#        if string : text[c4d.PRIM_TEXT_TEXT] = string
#        if size is not None :  text[c4d.PRIM_TEXT_HEIGHT]= size
#        if pos is not None : self.setTranslation(text,pos)
#        if parent is not None : self.reParent(text,parent)
#        
#    def Text(self,name="",string="",parent=None,size=5.,
#pos=None,font=None,lookAt=False):
#        text = c4d.BaseObject(self.TEXT)
#        text.SetName(name)
#        text[c4d.PRIM_TEXT_TEXT] = string        #Text
#        text[c4d.PRIM_TEXT_HEIGHT]= size
#        text[c4d.ID_BASEOBJECT_REL_ROTATION,c4d.VECTOR_X] = 3.14      #inverse
##        if font is not None:
##            text[c4d.PRIM_TEXT_FONT]
#        if pos is not None :
#            self.setTranslation(text,pos)
#        if parent is not None:
#            self.addObjectToScene(self.getCurrentScene(),text,parent=parent)
#        if lookAt:
#            self.constraintLookAt(text)
#        return text
#
#    def Circle(self,name, rad=1.):
#        circle=c4d.BaseObject(c4d.Osplinecircle)
#        circle.SetName(name)
#        circle[2012]=float(rad)
#        circle[2300]=0
#        return circle
#    
#    def createShapes2D(self,doc=None,parent=None):
#        if doc is None :
#            doc = self.getCurrentScene()    
#        shape2D={}
#        circle=c4d.BaseObject(self.CIRCLE)
#        circle[2012]=float(0.3)
#        circle[2300]=0
#        circle.SetName('Circle1')
#        circle2=circle.GetClone()
#        circle2.SetName('Circle2')
#        
#        coil=c4d.BaseObject(c4d.Onull)
#        coil.SetName('coil')    
#        turn=c4d.BaseObject(c4d.Onull)
#        turn.SetName('turn')
#        shape2D['Coil']=coil
#        shape2D['Turn']=turn        
#    
#        self.addObjectToScene(doc,coil,parent=parent )
#        self.addObjectToScene(doc,circle,parent=coil )
#        self.addObjectToScene(doc,turn,parent=parent )
#        self.addObjectToScene(doc,circle2,parent=turn )
#    
#        rectangle=c4d.BaseObject(RECTANGLE)
#        rectangle[2060]=float(2.2)
#        rectangle[2061]=float(0.7)
#        rectangle[2300]=0
#        rectangle.SetName('Rectangle1')
#        rectangle2=rectangle.GetClone()
#        rectangle2.SetName('Rectangle2')
#        
#        stra=c4d.BaseObject(c4d.Onull)
#        stra.SetName('stra')    
#        shee=c4d.BaseObject(c4d.Onull)
#        shee.SetName('shee')
#        shape2D['Stra']=stra
#        shape2D['Shee']=shee        
#    
#        self.addObjectToScene(doc,stra,parent=parent )
#        self.addObjectToScene(doc,rectangle,parent=stra )
#        self.addObjectToScene(doc,shee,parent=parent )
#        self.addObjectToScene(doc,rectangle2,parent=shee )
#        
#        fourside=c4d.BaseObject(FOURSIDE)
#        fourside[2121]=float(2.5)
#        fourside[2122]=float(0.9)
#        fourside[2300]=0
#        heli=c4d.BaseObject(c4d.Onull)
#        heli.SetName('heli')    
#        shape2D['Heli']=heli    
#    
#        self.addObjectToScene(doc,heli,parent=parent )
#        self.addObjectToScene(doc,fourside,parent=heli)
#        
#        return shape2D,[circle,rectangle,fourside]
#    
#    def getShapes2D(self):
#        shape2D={}
#        shape2D['Coil']=getObject('coil')
#        shape2D['Turn']=getObject('turn')
#        shape2D['Heli']=getObject('heli')
#        shape2D['Stra']=getObject('stra')        
#        return shape2D
#    
#    def morph2dObject(self,name,objsrc,target):
#        obj=objsrc.GetClone()
#        obj.SetName(name)
#        mixer=obj.MakeTag(self.POSEMIXER)
#        mixer[1001]=objsrc    #the default pose
#        #for i,sh in enumerate(shape2D) :
#        #    mixer[3002,1000+int(i)]=shape2D[sh]
#        mixer[3002,1000]=target#shape2D[sh] target 1
#        return obj
#        
#    def c4dSpecialRibon(self,name,points,dshape=CIRCLE,shape2dlist=None,mat=None):
#        #if loft == None : loft=loftnurbs('loft',mat=mat)
#        shape=[]
#        pos=c4d.Vector(float(points[0][2]),float(points[0][1]),float(points[0][0]))
#        direction=c4d.Vector(float(points[0][2]-points[1][2]),float(points[0][1]-points[1][1]),float(points[0][0]-points[1][0]))
#        mx=self.getCoordinateMatrix(pos,direction)
#        if shape2dlist : shape.append(morph2dObject(dshape+str(0),shape2dlist[dshape],shape2dlist['Heli']))
#        else : 
#            shape.append(c4d.BaseObject(dshape))
#            if dshape == self.CIRCLE :
#                shape[0][2012]=float(0.3)
#                #shape[0][2300]=1
#            if dshape == self.RECTANGLE :
#                shape[0][2060]=float(0.3*4.)
#                shape[0][2061]=float(0.3*3.)
#                #shape[0][2300]=1
#            if dshape == self.FOURSIDE:
#                shape[0][2121]=float(0.3*4.)
#                shape[0][2122]=float(0.1)
#                #shape[0][2300]=0            
#        shape[0].SetMg(mx)
#        if len(points)==2: return shape
#        i=1
#        while i < (len(points)-1):
#            #print i
#            pos=c4d.Vector(float(points[i][2]),float(points[i][1]),float(points[i][0]))
#            direction=c4d.Vector(float(points[i-1][2]-points[i+1][2]),float(points[i-1][1]-points[i+1][1]),float(points[i-1][0]-points[i+1][0]))
#            mx=self.getCoordinateMatrix(pos,direction)
#            if shape2dlist : shape.append(morph2dObject(dshape+str(i),shape2dlist[dshape],shape2dlist['Heli']))
#            else : 
#                shape.append(c4d.BaseObject(dshape))    
#                if dshape == self.CIRCLE :
#                    shape[i][2012]=float(0.3)
#                    shape[i][2300]=2
#                if dshape == self.RECTANGLE :
#                    shape[i][2060]=float(0.3*4.)
#                    shape[i][2061]=float(0.3*3.)
#                    shape[i][2300]=2
#                if dshape == self.FOURSIDE:
#                    shape[i][2121]=float(0.3*4.)
#                    shape[i][2122]=float(0.1)
#                    shape[i][2300]=2            
#            shape[i].SetMg(mx)
#            i=i+1
#        pos=c4d.Vector(float(points[i][2]),float(points[i][1]),float(points[i][0]))
#        direction=c4d.Vector(float(points[i-1][2]-points[i][2]),float(points[i-1][1]-points[i][1]),float(points[i-1][0]-points[i][0]))
#        mx=self.getCoordinateMatrix(pos,direction)
#        if shape2dlist : shape.append(morph2dObject(dshape+str(i),shape2dlist[dshape],shape2dlist['Heli']))
#        else : 
#            shape.append(c4d.BaseObject(dshape))
#            if dshape == self.CIRCLE :
#                shape[i][2012]=float(0.3)
#                shape[i][2300]=2
#            if dshape == self.RECTANGLE :
#                shape[i][2060]=float(0.3*4.)
#                shape[i][2061]=float(0.3*3.)
#                shape[i][2300]=2        
#            if dshape == self.FOURSIDE:
#                shape[i][2121]=float(0.3*4.)
#                shape[i][2122]=float(0.1)
#                shape[i][2300]=2
#        shape[i].SetMg(mx)
#        return shape
#        
#    def c4dSecondaryLofts(self,name,matrices,dshape=CIRCLE,mat=None):
#        #if loft == None : loft=loftnurbs('loft',mat=mat)
#        shape=[]            
#        i=0
#        while i < (len(matrices)):
#            #pos=c4d.Vector(float(points[i][2]),float(points[i][1]),float(points[i][0]))
#            #direction=c4d.Vector(float(points[i-1][2]-points[i+1][2]),float(points[i-1][1]-points[i+1][1]),float(points[i-1][0]-points[i+1][0]))
#            mx=self.getCoordinateMatrixBis(matrices[i][2],matrices[i][0],matrices[i][1])
#            #mx=getCoordinateMatrix(pos,direction)
#            shape.append(c4d.BaseObject(dshape))    
#            shape[i].SetMg(mx)
#            if dshape == self.CIRCLE :
#                shape[i][2012]=float(0.3)
#                shape[i][2300]=0
#            if dshape == self.RECTANGLE :
#                shape[i][2060]=float(2.2)
#                shape[i][2061]=float(0.7)
#                shape[i][2300]=0
#            if dshape == self.FOURSIDE:
#                shape[i][2121]=float(2.5)
#                shape[i][2122]=float(0.9)
#                shape[i][2300]=0            
#            i=i+1
#        return shape
#    
#    def instanceShape(self,ssname,shape2D):
#        #if shape2D=None : shape2D=createShapes2D()
#        shape=c4d.BaseObject(c4d.Oinstance)
#        shape[1001]=shape2D[ssname[:4]]
#        shape.SetName(ssname[:4])
#        return shape
#        
#    def makeShape(self,dshape,ssname):
#        shape=c4d.BaseObject(dshape)
#        if dshape == self.CIRCLE :
#                    shape[2012]=float(0.3)
#                    shape[2300]=0
#                    shape.SetName(ssname[:4])                
#        if dshape == self.RECTANGLE :
#                    shape[2060]=float(2.2)
#                    shape[2061]=float(0.7)
#                    shape[2300]=0
#                    shape.SetName(ssname[:4])                    
#        if dshape == self.FOURSIDE:
#                    shape[2121]=float(2.5)
#                    shape[2122]=float(0.9)
#                    shape[2300]=0
#                    shape.SetName(ssname[:4])                
#        return shape
#        
#    def c4dSecondaryLoftsSp(self,name,atoms,dshape=CIRCLE,mat=None,shape2dmorph=None,shapes2d=None,instance=False):
#        #print "ok build loft shape"
#        #if loft == None : loft=loftnurbs('loft',mat=mat)
#        shape=[]
#        prev=None    
#        ssSet=atoms[0].parent.parent.secondarystructureset
#        molname=atoms[0].full_name().split(":")[0]
#        chname=    atoms[0].full_name().split(":")[1]        
#        i=0
#        iK=0
#        #get The pmv-extruder    
#        sheet=atoms[0].parent.secondarystructure.sheet2D
#        matrices=sheet.matrixTransfo
#        if mat == None : mat = c4d.documents.GetActiveDocument().SearchMaterial('mat_loft'+molname+'_'+chname)
#        while i < (len(atoms)):
#            ssname=atoms[i].parent.secondarystructure.name
#            dshape=SSShapes[ssname[:4]]#ssname[:4]
#            #print ssname,dshape        
#            #pos=c4d.Vector(float(points[i][2]),float(points[i][1]),float(points[i][0]))
#            #direction=c4d.Vector(float(points[i-1][2]-points[i+1][2]),float(points[i-1][1]-points[i+1][1]),float(points[i-1][0]-points[i+1][0]))
#            mx=self.getCoordinateMatrixBis(matrices[i][2],matrices[i][0],matrices[i][1])
#            #mx=getCoordinateMatrix(pos,direction)
#            #iK=iK+1
#            if shape2dmorph :
#                shape.append(self.morph2dObject(dshape+str(i),shape2dmorph[dshape],shape2dmorph['Heli']))
#                shape[-1].SetMg(mx)
#            else :
#                #print str(prev),ssname         
#                if prev != None: #end of loop 
#                    if ssname[:4] != prev[:4]:
#                        if not instance : shape.append(self.makeShape(SSShapes[prev[:4]],prev))
#                        else : shape.append(self.instanceShape(prev,shapes2d))                    
#                        shape[-1].SetMg(mx)
#                if not instance : shape.append(self.makeShape(dshape,ssname))
#                else : shape.append(self.instanceShape(ssname,shapes2d))
#                shape[-1].SetMg(mx)
#            prev=ssname
#            i=i+1
#        if mat != None:
#            prev=None
#            #i=(len(shape))
#            i=0
#            while i < (len(shape)):
#                ssname=shape[i].GetName()
#                #print ssname            
#                pos=1-((((i)*100.)/len(shape))/100.0)
#                if pos < 0 : pos = 0.
#                #print pos
#                #change the material knote according ss color / cf atom color...
#                #col=atoms[i].colors['secondarystructure']
#                col=self.c4dColor(SSColor[ssname])
#                nc=c4d.Vector(col[0],col[1],col[2])
#                ncp=c4d.Vector(0,0,0)            
#                if prev != None :
#                    pcol=self.c4dColor(SSColor[prev])
#                    ncp=c4d.Vector(pcol[0],pcol[1],pcol[2])        
#                #print col
#                #print ssname[:4]
#                #print prev
#                if ssname != prev : #new ss
#                    grad=mat[8000][1007]    
#                #iK=iK+1
#                    nK=grad.GetKnotCount()
#                #print "knot count ",nK,iK                
#                    if iK >= nK :
#                        #print "insert ",pos,nK
#                        #print "grad.insert_knot(c4d.Vector("+str(col[0])+str(col[1])+str(col[2])+"), 1.0, "+str(pos)+",0.5)"
#                        if prev != None :
#                            grad.InsertKnot(ncp, 1.0, pos+0.01,0.5)
#                            iK=iK+1                                                
#                        grad.InsertKnot(nc, 1.0, pos-0.01,0.5)
#                        #grad.insert_knot(ncp, 1.0, pos+0.1,0.5)                    
#                        iK=iK+1                    
#                    else :
#                        #print "set ",iK,pos    
#                        if prev != None :grad.SetKnot(iK-1,ncp,1.0,pos,0.5)                            
#                        grad.SetKnot(iK,nc,1.0,pos,0.5)
#                    mat[8000][1007]=grad
#                prev=ssname
#                mat.Message(c4d.MSG_UPDATE)
#                i=i+1            
#        #mx=getCoordinateMatrixBis(matrices[i][2],matrices[i][0],matrices[i][1])
#        #if shape2dlist : shape.append(morph2dObject(dshape+str(i),shape2dlist[shape],shape2dlist['Heli']))
#        return shape
#    
#    def LoftOnSpline(self,name,chain,atoms,Spline=None,dshape=CIRCLE,mat=None,
#                     shape2dmorph=None,shapes2d=None,instance=False):
#        #print "ok build loft/spline"
#        molname = atoms[0].full_name().split(":")[0]
#        chname = atoms[0].full_name().split(":")[1]        
#        #we first need the spline
#        #if loft == None : loft=loftnurbs('loft',mat=mat)
#        shape=[]
#        prev=None
#        #mol = atoms[0].top	    
#        ssSet=chain.secondarystructureset#atoms[0].parent.parent.secondarystructureset
#        i=0
#        iK=0
#        #get The pmv-extruder    
#        sheet=chain.residues[0].secondarystructure.sheet2D
#        matrices=sheet.matrixTransfo
#        ca=atoms.get('CA')
#        o =atoms.get('O') 
#        if Spline is None :
#            parent=atoms[0].parent.parent.parent.geomContainer.masterGeom.chains_obj[chname]
#            Spline,ospline = spline(name+'spline',ca.coords)#
#            addObjectToScene(getCurrentScene(),Spline,parent=parent) 
#        #loftname = 'loft'+mol.name+'_'+ch.name 
#        #matloftname = 'mat_loft'+mol.name+'_'+ch.name
#        if mat == None : 
#            mat = c4d.documents.GetActiveDocument().SearchMaterial('mat_loft'+molname+'_'+chname)
#            if  mat is not None :
#                if DEBUG : print "ok find mat"
#            #if mat == None :
#            #    mat = create_loft_material(name='mat_loft'+molname+'_'+chname)
#        if DEBUG : print "CA",len(ca)
#        while i < (len(ca)):
#            pos= float(((i*1.) / len(ca)))
#            #print str(pos)+" %"  
#            #print atoms[i],atoms[i].parent,hasattr(atoms[i].parent,'secondarystructure')				      
#            if hasattr(ca[i].parent,'secondarystructure') : ssname=ca[i].parent.secondarystructure.name
#            else : ssname="Coil"
#            dshape=SSShapes[ssname[:4]]#ssname[:4]
#            #mx =getCoordinateMatrixBis(matrices[i][2],matrices[i][0],matrices[i][1])
#            #have to place the shape on the spline    
#            if shape2dmorph :
#                shape.append(morph2dObject(dshape+str(i),shape2dmorph[dshape],shape2dmorph['Heli']))
#                path=shape[i].MakeTag(Follow_PATH)
#                path[1001] = Spline
#                path[1000] = 0#tangantial
#                path[1003] = pos
#                path[1007] = 2#1		axe	            
#                #shape[-1].SetMg(mx)
#            else :
#                #print str(prev),ssname         
#                #if prev != None: #end of loop 
#                #    if ssname[:4] != prev[:4]: #newSS need transition
#                #        if not instance : shape.append(makeShape(SSShapes[prev[:4]],prev))
#                #        else : shape.append(instanceShape(prev,shapes2d))                    
#                #        #shape[-1].SetMg(mx)
#                #        path=shape[-1].MakeTag(Follow_PATH)
#                #        path[1001] = Spline
#                #        path[1000] = 1    
#                #        path[1003] = pos                
#                if not instance : shape.append(makeShape(dshape,ssname))
#                else : shape.append(instanceShape(ssname,shapes2d))
#                path=shape[i].MakeTag(Follow_PATH)
#                path[1001] = Spline
#                path[1000] = 0  
#                path[1003] = pos                                           
#                path[1007] = 2#1
#                #shape[-1].SetMg(mx)        
#            if i >=1  : 
#                laenge,mx=getStickProperties(ca[i].coords,ca[i-1].coords)
#                #if i > len(o) : laenge,mx=getStickProperties(ca[i].coords,o[i-1].coords)
#                #else :laenge,mx=getStickProperties(ca[i].coords,o[i].coords)
#                shape[i].SetMg(mx)	
#            prev=ssname
#            i=i+1
#        laenge,mx=getStickProperties(ca[0].coords,ca[1].coords) 
#        #laenge,mx=getStickProperties(ca[0].coords,o[0].coords) 
#        shape[0].SetMg(mx)  		
#        if False :#(mat != None):
#            prev=None
#            #i=(len(shape))
#            i=0
#            while i < (len(shape)):
#                ssname=shape[i].GetName()
#                #print ssname            
#                pos=1-((((i)*100.)/len(shape))/100.0)
#                if pos < 0 : pos = 0.
#                #print pos
#                #change the material knote according ss color / cf atom color...
#                #col=atoms[i].colors['secondarystructure']
#                col=c4dColor(SSColor[ssname])
#                nc=c4d.Vector(col[0],col[1],col[2])
#                ncp=c4d.Vector(0,0,0)            
#                if prev != None :
#                    pcol=c4dColor(SSColor[prev])
#                    ncp=c4d.Vector(pcol[0],pcol[1],pcol[2])        
#                #print col
#                #print ssname[:4]
#                #print prev
#                if ssname != prev : #new ss
#                    grad=mat[8000][1007]    
#                #iK=iK+1
#                    nK=grad.GetKnotCount()
#                #print "knot count ",nK,iK                
#                    if iK >= nK :
#                        #print "insert ",pos,nK
#                        #print "grad.insert_knot(c4d.Vector("+str(col[0])+str(col[1])+str(col[2])+"), 1.0, "+str(pos)+",0.5)"
#                        if prev != None :
#                            grad.InsertKnot(ncp, 1.0, pos+0.01,0.5)
#                            iK=iK+1                                                
#                        grad.InsertKnot(nc, 1.0, pos-0.01,0.5)
#                        #grad.insert_knot(ncp, 1.0, pos+0.1,0.5)                    
#                        iK=iK+1                    
#                    else :
#                        #print "set ",iK,pos    
#                        if prev != None :grad.SetKnot(iK-1,ncp,1.0,pos,0.5)                            
#                        grad.SetKnot(iK,nc,1.0,pos,0.5)
#                    mat[8000][1007]=grad
#                prev=ssname
#                mat.Message(c4d.MSG_UPDATE)
#                i=i+1            
#        #mx=getCoordinateMatrixBis(matrices[i][2],matrices[i][0],matrices[i][1])
#        #if shape2dlist : shape.append(morph2dObject(dshape+str(i),shape2dlist[shape],shape2dlist['Heli']))
#        return shape
#    
#    def update_2dsheet(shapes,builder,loft):
#        dicSS={'C':'Coil','T' : 'Turn', 'H':'Heli','E':'Stra','P':'Coil'}
#        shape2D=getShapes2D()
#        for i,ss in enumerate(builder):
#            if     shapes[i].GetName() != dicSS[ss]:
#                shapes[i][1001]=shape2D[dicSS[ss]]#ref object
#                shapes[i].SetName(dicSS[ss])    
#    
#        texture = loft.GetTags()[0]
#        mat=texture[1010]
#        grad=mat[8000][1007]
#        grad.delete_all_knots()
#        mat[8000][1007]=grad
#    
#        prev=None
#        i = 0
#        iK = 0    
#        while i < (len(shapes)):
#                ssname=shapes[i].GetName()
#                #print ssname            
#                pos=1-((((i)*100.)/len(shapes))/100.0)
#                if pos < 0 : pos = 0.
#                #print pos
#                #change the material knote according ss color / cf atom color...
#                #col=atoms[i].colors['secondarystructure']
#                col=c4dColor(SSColor[ssname])
#                nc=c4d.Vector(col[0],col[1],col[2])
#                ncp=c4d.Vector(0,0,0)            
#                if prev != None :
#                    pcol=c4dColor(SSColor[prev])
#                    ncp=c4d.Vector(pcol[0],pcol[1],pcol[2])        
#                #print col
#                #print ssname[:4]
#                #print prev
#                if ssname != prev : #new ss
#                    grad=mat[8000][1007]    
#                #iK=iK+1
#                    nK=grad.get_knot_count()
#                #print "knot count ",nK,iK                
#                    if iK >= nK :
#                        #print "insert ",pos,nK
#                        #print "grad.insert_knot(c4d.Vector("+str(col[0])+str(col[1])+str(col[2])+"), 1.0, "+str(pos)+",0.5)"
#                        if prev != None :
#                            grad.insert_knot(ncp, 1.0, pos+0.01,0.5)
#                            iK=iK+1                                                
#                        grad.insert_knot(nc, 1.0, pos-0.01,0.5)
#                        #grad.insert_knot(ncp, 1.0, pos+0.1,0.5)                    
#                        iK=iK+1                    
#                    else :
#                        #print "set ",iK,pos    
#                        if prev != None :grad.set_knot(iK-1,ncp,1.0,pos,0.5)                            
#                        grad.set_knot(iK,nc,1.0,pos,0.5)
#                    mat[8000][1007]=grad
#                prev=ssname
#                mat.Message(c4d.MSG_UPDATE)
#                i=i+1            
#        
#    def makeLines(self,name,points,faces,parent=None):
#        rootLine = self.newEmpty(name)
#        self.addObjectToScene(self.getCurrentScene(),rootLine,parent=parent)
#        spline=c4d.BaseObject(c4d.Ospline)
#        #spline[1000]=type
#        #spline[1002]=close
#        spline.SetName(name+'mainchain')
#        spline.ResizeObject(int(len(points)))
#        cd4vertices = map(self.FromVec,points)
#        map(polygon.SetPoint,range(len(points)),cd4vertices)    
#        #for i,p in enumerate(points):
#        #    spline.SetPoint(i, c4dv(p))
#        self.addObjectToScene(self.getCurrentScene(),spline,parent=rootLine)
#        spline=c4d.BaseObject(c4d.Ospline)
#        #spline[1000]=type
#        #spline[1002]=close
#        spline.SetName(name+'sidechain')
#        spline.ResizeObject(int(len(points)))
#        for i,p in enumerate(points):
#            spline.SetPoint(i, self.FromVec(p))
#        self.addObjectToScene(self.getCurrentScene(),spline,parent=rootLine)    
#    
#    def updateLines(self,lines, chains=None):
#    	#lines = getObject(name)	
#    	#if lines == None or chains == None:
#    	    #print lines,chains	
#    	    #parent = getObject(chains.full_name())	
#    	    #print parent		
#    #    bonds, atnobnd = chains.residues.atoms.bonds
#    #    indices = map(lambda x: (x.atom1._bndIndex_,
#    #    							x.atom2._bndIndex_), bonds)
#    #    updatePoly(lines,vertices=chains.residues.atoms.coords,faces=indices)
#        self.updatePoly(self,lines,vertices=chains.residues.atoms.coords)
#    
##    def getCoordByAtomType(chain):
##        dic={}
##        #extract the different atomset by type
##        for i,atms in enumerate(AtomElements.keys()):
##            atomset = chain.residues.atoms.get(atms)
##            bonds, atnobnd = atomset.bonds
##            indices = map(lambda x: (x.atom1._bndIndex_,
##                                 x.atom2._bndIndex_), bonds)
##            dic[atms] = [atomset]
##        
##    def stickballASmesh(molecules,atomSets):
##        bsms=[]
##        for mol, atms, in map(None, molecules, atomSets):
##            for ch in mol.chains:
##                parent = getObject(ch.full_name())
##                lines = getObject(ch.full_name()+'_bsm')
##                if lines == None :
##                    lines=newEmpty(ch.full_name()+'_bsm')
##                    addObjectToScene(getCurrentScene(),lines,parent=parent)
##                    dic = getCoordByAtomType(ch)
##                    for type in dic.keys():
##                        bsm = createsNmesh(ch.full_name()+'_bsm'+type,dic[type][0],
##                                         None,dic[type][1])
##                        bsms.append(bsm)
##                        addObjectToScene(getCurrentScene(),bsm,parent=lines)
#    
##    def editLines(molecules,atomSets):
##        for mol, atms, in map(None, molecules, atomSets):
##            #check if line exist
##            for ch in mol.chains:
##                parent = getObject(ch.full_name())
##                lines = getObject(ch.full_name()+'_line')
##                if lines == None :
##                    arr = c4d.BaseObject(ATOMARRAY)
##                    arr.SetName(ch.full_name()+'_lineds')
##                    arr[1000] = 0.1 #radius cylinder
##                    arr[1001] = 0.1 #radius sphere
##                    arr[1002] = 3 #subdivision
##                    addObjectToScene(getCurrentScene(),arr,parent=parent)                
##                    bonds, atnobnd = ch.residues.atoms.bonds
##                    indices = map(lambda x: (x.atom1._bndIndex_,
##                                             x.atom2._bndIndex_), bonds)
##    
##                    lines = createsNmesh(ch.full_name()+'_line',ch.residues.atoms.coords,
##                                         None,indices)
##                    addObjectToScene(getCurrentScene(),lines[0]	,parent=arr)
##                    mol.geomContainer.geoms[ch.full_name()+'_line'] = lines
##                    #display using AtomArray
##                else : #need to update
##                    updateLines(lines, chains=ch)
#    				
    def Points(self,name,**kw):
        #need to add the AtomArray modifier....
        parent = None
        if "parent" in kw:
            parent = kw.pop("parent")
        from DejaVu.Points import Points
        obj= Points(name,**kw)
        self.addObjectToScene(self.getCurrentScene(),obj,parent=parent)
        return obj
#    
#    def PolygonColorsObject(self,name,vertColors):
#          obj= c4d.PolygonObject(len(vertColors), len(vertColors)/2.)
#          obj.SetName(name+'_color')
#          cd4vertices = map(self.FromVec,vertColors)
#          map(obj.SetPoint,range(len(vertColors)),cd4vertices)
#        #for k,v in enumerate(vertColors) :   
#        #      obj.SetPoint(k, c4dv(v))
#          return obj
#    
    def updatePoly(self,polygon,faces=None,vertices=None):
        if type(polygon) == str:
            polygon = self.getObject(polygon)
        if polygon == None : return		
        if vertices != None:
            polygon.Set(vertices=vertices)
        if faces != None:
            polygon.Set(faces=faces)
#    
#    def redoPoly(self,poly,vertices,faces,proxyCol=False,colors=None,parent=None,mol=None):
#        doc = self.getCurrentScene()
#        doc.SetActiveObject(poly)
#        name=poly.GetName()
#        texture = poly.GetTags()[0]
#        c4d.CallCommand(100004787) #delete the obj
#        obj=self.createsNmesh(name,vertices,None,faces,smooth=False,material=texture[1010],proxyCol=proxyCol)
#        self.addObjectToScene(doc,obj[0],parent=parent)
#        if proxyCol and colors!=None:
#            pObject=self.getObject(name+"_color")
#            doc.SetActiveObject(pObject)
#            c4d.CallCommand(100004787) #delete the obj    
#            pObject=PolygonColorsObject(name,colors)
#            self.addObjectToScene(doc,pObject,parent=parent)
#    
#    def reCreatePoly(self,poly,vertices,faces,proxyCol=False,colors=None,parent=None,mol=None):
#        doc = self.getCurrentScene()
#        doc.SetActiveObject(poly)
#        name=poly.GetName()
#        texture = poly.GetTags()[0]
#        c4d.CallCommand(100004787) #delete the obj
#        obj=self.createsNmesh(name,vertices,None,faces,smooth=False,material=texture[1010],proxyCol=proxyCol)
#        self.addObjectToScene(doc,obj[0],parent=parent)
#        if proxyCol and colors!=None:
#            pObject=self.getObject(name+"_color")
#            doc.SetActiveObject(pObject)
#            c4d.CallCommand(100004787) #delete the obj    
#            pObject=self.PolygonColorsObject(name,colors)
#            self.addObjectToScene(doc,pObject,parent=parent)
#    	
#    """def UVWColorTag(obj,vertColors):
#          uvw=obj.MakeTag(c4d.Tuvw)
#        
#          obj= c4d.PolygonObject(len(vertColors), len(vertColors)/2.)
#          obj.SetName(name+'_color')
#          k=0
#          for v in vertColors :
#              print v      
#              obj.SetPoint(k, c4d.Vector(float(v[0]), float(v[1]), float(v[2])))
#              k=k+1
#          return obj
#    """
#    
    def updateMesh(self,obj,vertices=None,faces = None, smooth=False):
        if type(obj) == str:
            obj = self.getObject(obj)
        if obj == None : return        
        self.updatePoly(obj,faces=faces,vertices=vertices)

#    def updateMeshProxy(self,obj,proxyCol=False,parent=None,mol=None):
#        doc = getCurrentScene()
#        doc.SetActiveObject(g.obj)
#        name=obj.GetName()   
#        texture = obj.GetTags()[0]
#        c4d.CallCommand(100004787) #delete the obj
#        vertices=g.getVertices()
#        faces=g.getFaces()
##        if DEBUG : print len(vertices),len(faces)
#        sys.stderr.write('\nnb v %d f %d\n' % (len(vertices),len(faces))) 
#        #if     proxyCol : o=PolygonColorsObject
#        obj=self.createsNmesh(name,vertices,None,faces,smooth=False,material=texture[1010],proxyCol=proxyCol)
#        self.addObjectToScene(doc,obj[0],parent=parent)
#        #obj.Message(c4d.MSG_UPDATE)
#        return obj[0]
#    #    if proxyCol :
#    #        colors=mol.geomContainer.getGeomColor(g.name)
#    #        if hasattr(g,'color_obj'):
#    #            pObject=g.color_obj#getObject(name+"_color")
#    #            doc.SetActiveObject(pObject)
#    #            c4d.CallCommand(100004787) #delete the obj 
#    #        pObject=PolygonColorsObject(name,colors)
#    #        g.color_obj=pObject
#    #        addObjectToScene(doc,pObject,parent=parent)
#    
#    def c4df(self,face,g,polygon):
#        A = int(face[0])
#        B = int(face[1])
#        if len(face)==2 :
#            C = B
#            D = B
#            poly=c4d.CPolygon(A, B, C)
#        elif len(face)==3 : 
#            C = int(face[2])
#            D = C
#            poly=c4d.CPolygon(A, B, C)
#        elif len(face)==4 : 
#            C = int(face[2])
#            D = int(face[3])
#            poly=c4d.CPolygon(A, B, C, D)
#        polygon.SetPolygon(id=g, polygon=poly)
#        return [A,B,C,D]
#    
#    def polygons(self,name,proxyCol=False,smooth=False,color=None, material=None, **kw):
#          import time
#          t1 = time.time()
#          vertices = kw["vertices"]
#          faces = kw["faces"]
#          normals = kw["normals"]
#          frontPolyMode='fill'
#          if kw.has_key("frontPolyMode"):	  
#              frontPolyMode = kw["frontPolyMode"]
#          if kw.has_key("shading") :  
#              shading=kw["shading"]#'flat'
#          if frontPolyMode == "line" : #wire mode
#              material = self.getCurrentScene().SearchMaterial("wire")
#              if material == None:
#                  material = self.addMaterial("wire",(0.5,0.5,0.5))		  		  	  	  	    	  
#          polygon = c4d.PolygonObject(len(vertices), len(faces))
#          polygon.SetName(name)      
#          k=0
#          #map function is faster than the usual for loop
#          #what about the lambda?
#          cd4vertices = map(self.FromVec,vertices)
#          map(polygon.SetPoint,range(len(vertices)),cd4vertices)
#          #for v in vertices :
#              #print v      
#          #    polygon.SetPoint(k, c4dv(v))
#              #polygon.SetPoint(k, c4d.Vector(float(v[0]), float(v[1]), float(v[2])))
#          #    k=k+1
#          #c4dfaces = map(c4df,faces,range(len(faces)),[polygon]*len(faces))
#          #map(polygon.SetPolygon,range(len(faces)),c4dfaces)
#          for g in range(len(faces)):
#              A = int(faces[g][0])
#              B = int(faces[g][1])
#              if len(faces[g])==2 :
#                C = B
#                D = B
#                polygon.SetPolygon(id=g, polygon=c4d.CPolygon( A, B, C))
#              elif len(faces[g])==3 : 
#                C = int(faces[g][2])
#                D = C
#                polygon.SetPolygon(id=g, polygon=c4d.CPolygon( A, B, C))
#              elif len(faces[g])==4 : 
#                C = int(faces[g][2])
#                D = int(faces[g][3])
#                #print A
#                polygon.SetPolygon(id=g, polygon=c4d.CPolygon( A, B, C, D ))    
#          t2=time.time()
#          #print "time to create Mesh", (t2 - t1)
#          #sys.stderr.write('\ntime to create Mesh %f\n' % (t2-t1))
#          polygon.MakeTag(c4d.Tphong) #shading ?
#          # create a texture tag on the PDBgeometry object
#          if not proxyCol : 
#              texture = polygon.MakeTag(c4d.Ttexture)
#              #create the dedicayed material
#              if material == None :
#                  texture[1010] = self.addMaterial("mat_"+name,color[0])
#              else : texture[1010] = material
#          polygon.Message(c4d.MSG_UPDATE)
#          return polygon
#    
#            
    def createsNmesh(self,name,vertices,vnormals,faces,smooth=False,
                     material=None,proxyCol=False,color=[[1,1,1],],**kw):
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
        shading='flat'
        if  smooth :
            shading = 'smooth'                
        PDBgeometry = IndexedPolygons(name, vertices=vertices,
                          faces=faces, vnormals=vnormals,materials=color,shading=shading,
                          )
        parent = None
        if "parent" in kw :
            parent = kw["parent"]
        self.addObjectToScene(None,PDBgeometry,parent = parent)
        return [PDBgeometry,PDBgeometry]

    def instancePolygon(self,name, matrices=None, mesh=None,parent=None,
                        transpose= False,colors=None,**kw):
        if matrices == None : return None
        if mesh == None : return None
        instance = []	  
        geom = None
        if mesh is None or not isinstance(mesh,IndexedPolygons):
            print("no mesh???",mesh,isinstance(mesh,Spheres))
            if isinstance(mesh,Spheres):
                #need only the tranlation for the matrix 
                centers = [m[:3,3] for m in matrices ]
                #mesh.Set(centers=centers)
                if parent is not None :
                    self.reParent(mesh, parent)
                    parent.Set(instanceMatrices=matrices, visible=1)  
                else :
                    mesh.Set(centers=centers)
                return mesh
            elif isinstance(mesh,Geom):
                if parent is not None :
                    print ("instancePolygon",parent,mesh)
                    if parent != mesh :
                        self.reParent(mesh, parent)
                        parent.Set(instanceMatrices=matrices, visible=1)  
                    else :
                        mesh.Set(instanceMatrices=matrices, visible=1) 
                else :
                    mesh.Set(instanceMatrices=matrices, visible=1) 
            #justgetthe pass mes
            geom = self.getObject(mesh)
            if geom is None :
                return
#            return None
        else:
            geom = IndexedPolygons(name, vertices=mesh.getVertices(),
                          faces=mesh.getFaces(), vnormals=mesh.getVNormals()
                          )
            geom.materials[1028].prop =mesh.materials[1028].prop
            geom.materials[1029].prop =mesh.materials[1029].prop
            self.addObjectToScene(None,geom,parent=parent)
        print("geom",geom)
        geom.Set(instanceMatrices=matrices, visible=1)
#        if colors is not None :
#            geom.Set(materials=colors, inheritMaterial=0)
        return geom
    
    def changeColor(self,obj,colors,perVertex=False,
                    proxyObject=False,doc=None,pb=False):
        mesh=self.getMesh(obj)
        unic=False
        ncolor=None
        faces = mesh.getVertices()
        vertices = mesh.getFaces()
        #print len(colors),len(mesh.verts),len(mesh.faces)
        if len(colors) != len(vertices) and len(colors) == len(faces): 
            perVertex=False
        elif len(colors) == len(vertices) and len(colors) != len(faces): 
            perVertex=True
        else :
            if (len(colors) - len(vertices)) > (len(colors) - len(faces)) : 
                perVertex=True
            else :
                perVertex=False
        #print perVertex
#        if len(colors)==1 : 
#            #print colors    
#            unic=True
#            ncolor = self.convertColor(colors[0])#blenderColor(colors[0])
#        else :
#            colors = [self.convertColor(c) for c in colors]
        mesh.Set(materials = colors,inheritMaterial=False)   
    
    def box(self,name,center=[0.,0.,0.],size=[1.,1.,1.],cornerPoints=None,visible=1,
                              mat = None,**kw):
        #import numpy
        box=Box(name,frontPolyMode='fill')#, cornerPoints=bb, visible=1
        if cornerPoints != None :
            for i in range(3):
                size[i] = cornerPoints[1][i]-cornerPoints[0][i]
            center=(numpy.array(cornerPoints[0])+numpy.array(cornerPoints[1]))/2.
            box.Set(cornerPoints=list(cornerPoints))
        else : 
            box.Set(center=center,xside=size[0],yside=size[1],zside=size[2])
        #material is a liste of color per faces.
        #aMat=addMaterial("wire")
        parent = None
        if "parent" in kw :
            parent = kw["parent"]
        self.addObjectToScene(self.getCurrentScene(),box,parent=parent)         
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
            box.Set(cornerPoints=list(cornerPoints))
        else : 
            box.Set(center=center,xside=size[0],yside=size[1],zside=size[2])

    def getCornerPointCube(self,cube):
        if hasattr(cube,"size"):
            size = cube.side
        else :
            size = (cube.xside,cube.yside,cube.zside)
        center = cube.center
        cornerPoints=[]
        #lowCorner
        lc = [center[0] - size[0]/2.,
              center[1] - size[1]/2.,
              center[2] - size[2]/2.]
        uc = [center[0] + size[0]/2.,
              center[1] + size[1]/2.,
              center[2] + size[2]/2.]
        cornerPoints=[[lc[0],lc[1],lc[2]],[uc[0],uc[1],uc[2]]]
        return cornerPoints
    
    
    
    def plane(self,name,center=[0.,0.,0.],size=[1.,1.],cornerPoints=None,visible=1,**kw):
        #plane or grid
        xres = 2
        yres = 2
        if "subdivision" in kw :
            xres = kw["subdivision"][0]
            yres = kw["subdivision"][1]
            if xres == 1 : xres = 2                      
            if yres == 1 : yres = 2
        
        #need to build vertices/faces for the plane
        #4corner points
        #  *--*
        #  |\ |
        #  | \|
        #  *--*
        #basic plane, no subdivision
        #what about subdivision
        vertices =[ (-0.5,0.5,0.0),
                (0.5,0.5,0.0),
                (0.5,-0.5,0.0),
                (-0.5,-0.5,0.0)]
        vnormals =[ (0.0,0.0,1.0),
                (0.0,0.0,1.0),
                (0.0,0.0,1.0),
                (0.0,0.0,1.0)]        
        faces = ((2,1,0),(3,2,0))
        
        obj = IndexedPolygons(name, vertices=vertices,
                          faces=faces, vnormals=None,shading='flat',
                          materials=[[1,0,0],]
                          )
        
        if cornerPoints != None :
            for i in range(3):
                size[i] = cornerPoints[1][i]-cornerPoints[0][i]
            center=(numpy.array(cornerPoints[0])+numpy.array(cornerPoints[1]))/2.
        obj.translation = (float(center[0]),float(center[1]),float(center[2]))
        obj.Set(scale = (float(size[0]),float(size[1]),1.0))
        
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
            #plane[c4d.PRIM_AXIS]=axis
            #should rotate around the axis
        
        if "material" in kw :
            if type(kw["material"]) is not bool :
                self.assignMaterial(plane,[kw["material"],])                
            else :
                self.addMaterial(name,[1.,1.,0.])
        parent = None
        if "parent" in kw :
            parent = kw["parent"]
        self.addObjectToScene(self.getCurrentScene(),obj,parent=parent)
        return obj
    
    def getFace(self,face):
        return face

#    def triangulate(self,poly):
#        #select poly
#        doc = self.getCurrentScene()
#        doc.SetActiveObject(poly)
#        c4d.CallCommand(14048)#triangulate
#        
#    def makeEditable(self,object,copy=True):
#        doc = self.getCurrentScene()
#        #make a copy?
#        if copy:
#            clone = object.GetClone()
#            clone.SetName("clone")
#            doc.InsertObject(clone)
#            doc.SetActiveObject(clone)
#            c4d.CallCommand(12236)#make editable
#            clone.Message(c4d.MSG_UPDATE)
#            return clone
#        else :
#            doc.SetActiveObject(object)
#            c4d.CallCommand(12236)
#            return object
#   

    def getMeshVertices(self,poly,transform=False):
        mesh = self.checkIsMesh(poly)
        return mesh.getVertices()
        
    def getMeshNormales(self,poly):
        mesh = self.checkIsMesh(poly)
        return mesh.getVNormals()
        
    def getMeshEdges(self,poly):
        mesh = self.checkIsMesh(poly)
        return None

    def getMeshFaces(self,poly):
        mesh = self.checkIsMesh(poly)
        return mesh.getFaces()

    def DecomposeMesh(self,poly,edit=True,copy=True,tri=True,transform=True):
        #get infos
        if not isinstance(poly,IndexedPolygons):
            if isinstance(poly,Cylinders):
                poly = poly.asIndexedPolygons()
            elif isinstance(poly,Geom) :
                #getfirst child
                child = self.getChilds(poly)
                if len(child):
                    poly=child[0]
                elif isinstance(poly,Cylinders):
                    poly = poly.asIndexedPolygons()
                else :
                    return [],[],[]
            else :
                return [],[],[]
        faces = poly.getFaces()
        vertices = poly.getVertices()
        vnormals = poly.getVNormals()
        if transform :
            mat = poly.GetMatrix(poly.LastParentBeforeRoot())
            vertices = self.ApplyMatrix(vertices,mat)
        return faces,vertices,vnormals
 
    def changeColorO(self,object,colors):
        object.Set(materials=colors)

    def setRigidBody(self,*args,**kw):
        pass

    def pathDeform(self,*args,**kw):
        pass
    
    def updatePathDeform(self,*args,**kw):
        pass

#==============================================================================
# IO / read/write 3D object, cene file etc  
#==============================================================================
    def getColladaMaterial(self,geom,col):
        #get the bound geometries
        mat = None        
        boundg = list(col.scene.objects('geometry'))
        for bg in boundg:
#            print bg.original,geom
            if bg.original == geom :
               m = bg.materialnodebysymbol.values()
               if len(m):
                   mat = bg.materialnodebysymbol.values()[0].target
        return mat
    
    def TextureFaceCoordintesToVertexCoordinates(self,v,f,t,ti):
        textureuv_vertex = numpy.zeros((len(v),2))        
        for i,indice_verex in enumerate(f):
            for j in range(3):
                if len(ti) == (len(f)*3) :
                    indice = ti[i+j]
                else :
                    indice = ti[i][j]
                textureuv_vertex[indice_verex[j]] = t[indice]#(t[ti[i][j]]+1.0)/2.0
        return textureuv_vertex        

    def getNormals(self,f,v,n,ni):
        if len(ni.shape) == 1 :
            if max(ni) == (len(v) -1) :
                return n[ni]
            else : 
                return None
        normals_vertex = numpy.zeros((len(v),3))   
        for i,indice_vertex in enumerate(f):
            if len(f.shape) == 2:
                for j in range(3):
                    normals_vertex[indice_vertex[j]] = n[ni[i][j]]#(t[ti[i][j]]+1.0)/2.0
            else :
                normals_vertex[indice_vertex] = n[ni[i]]
        return normals_vertex        
        

    def nodeToGeom(self,node,i,col,nodexml,parentxml=None,parent=None,dicgeoms=None,uniq=False):
        name = nodexml.get("name")
        if name is None :
            name = nodexml.get("id")
        pname=""
        if parentxml is not None :
            pname = parentxml.get("name")
            if pname is None or pname == '':
                pname = parentxml.get("id")        
#        print "pname",name
        onode=None      
#        print "nodeToGeom type", type(node)
        if dicgeoms is None :
            dicgeoms = {}
        if (type(node)==collada.scene.ExtraNode):
            return
        elif (type(node)==collada.scene.GeometryNode):
            #create a mesh under parent
            g = node.geometry
            if g.id not in dicgeoms.keys():
                dicgeoms[g.id]={}
                dicgeoms[g.id]["id"]=g.id
                onode,mesh = self.oneColladaGeom(g,col)
                dicgeoms[g.id]["node"]=onode
                dicgeoms[g.id]["mesh"]=mesh
                dicgeoms[g.id]["instances"]=[]
                dicgeoms[g.id]["parentmesh"]=None
                if parentxml is not None :
                    dicgeoms[gname]["parentmesh"]= self.getObject(parentxml.get("id"))                
        else :
#            print "else ",len(node.children)
#            print "instance_geometry",nodexml.get("instance_geometry")
            #create an empty
#            print "else ",name ,type(node),parent
            if len(node.children) == 1 and (type(node.children[0])==collada.scene.GeometryNode):
                    #no empty just get parent name ?
#                    print "ok one children geom ",node.children[0]
                    gname = node.children[0].geometry.id
                    if parentxml is not None :
                        if gname in dicgeoms.keys():
#                            print dicgeoms[gname]["parentmesh"]
                            if dicgeoms[gname]["parentmesh"] is None :
                                dicgeoms[gname]["parentmesh"]= self.getObject(pname)
#                            print dicgeoms[gname]["parentmesh"]
                    if uniq :
                        onode = self.newEmpty(name)
        #                print "ok new empty name",onode, name
                        rot,trans,scale = self.Decompose4x4(node.matrix.transpose().reshape(16))
                        if parent is not None and onode is not None:
                            self.reParent(onode, parent )
                        onode.Set(translation = trans)
                        onode.Set(rotation = rot)#.reshape(4,4).transpose())                
                        dicgeoms[gname]["parentmesh"]=onode
            else :
                onode = self.newEmpty(name)
#                print "ok new empty name",onode, name
                rot,trans,scale = self.Decompose4x4(node.matrix.transpose().reshape(16))
                if parent is not None and onode is not None:
                    self.reParent(onode, parent )
                onode.Set(translation = trans)
                onode.Set(rotation = rot)#.reshape(4,4).transpose())                
            if hasattr(node, 'children') and len(node.children) :
                for j,ch in enumerate(node.children) :
    #                print "children ",ch.xmlnode.get("name")
                    ##node,i,col,nodexml,parentxml=None,parent=None,dicgeoms=None
                    dicgeoms=self.nodeToGeom(ch,j,col,ch.xmlnode,parentxml=nodexml,parent=onode,dicgeoms=dicgeoms)
        return dicgeoms

    def transformNode(self,node,i,col,parentxmlnode,parent=None) :
        name = parentxmlnode.get("name")
#        print "pname",name
        if name is None :
            name = parentxmlnode.get("id")
#        print "transformNode parent",name
#        print "transformNode type", type(node)
        if (type(node)==collada.scene.GeometryNode):
            pass
        elif (type(node)==collada.scene.ExtraNode):
            pass
        else :
                #create an empty
                onode = self.getObject(name)
                rot,trans,scale = self.Decompose4x4(node.matrix.transpose().reshape(16))
#                trans = [node.transforms[0].x,node.transforms[0].y,node.transforms[0].z]
#                rot = []
#                for i in range(1,4):
#                    rot.extend([node.transforms[i].x,node.transforms[i].y,node.transforms[i].z,0.0])
#                rot.extend([0.,0.,0.,1.0])
#                print "rotation ",rot
#                print "trans ", trans/1000.0
#                scale = [node.transforms[4].x,node.transforms[4].y,node.transforms[4].z]
#                onode.Set(translation = trans)#, rotation=rot*0,scale=scale)
                onode.Set(translation = trans)
                onode.Set(rotation = rot)#.reshape(4,4).transpose())
#                onode.ConcatRotation(rot)
#                onode.ConcatTranslation(trans)
#                onode.Set(matrix)
                self.update()
#                print onode.translation
        if hasattr(node, 'children') and len(node.children) : 
            for j,ch in enumerate(node.children) :
#                print "children ",ch.xmlnode.get("name")
                self.transformNode(ch,j,col,ch.xmlnode,parent=onode)                

    def decomposeColladaGeom(self,g,col):
        name = g.name
        if name == '' :
            name = g.id
        v=g.primitives[0].vertex#multiple primitive ?
        nf = len(g.primitives[0].vertex_index)
        sh = g.primitives[0].vertex_index.shape
        if len(sh) == 2 and sh[1] == 3 :
            f= g.primitives[0].vertex_index
        else :
            f=g.primitives[0].vertex_index[:(nf/3*3)].reshape((nf/3,3))
        n=g.primitives[0].normal
        ni = g.primitives[0].normal_index
        vn = self.getNormals(f,v,n,ni)            
        return v,vn,f.tolist()

    def oneColladaGeom(self,g,col):
        name = g.name
        if name == '' :
            name = g.id
        v=g.primitives[0].vertex#multiple primitive ?
        nf = len(g.primitives[0].vertex_index)
        sh = g.primitives[0].vertex_index.shape
        if len(sh) == 2 and sh[1] == 3 :
            f= g.primitives[0].vertex_index
        else :
            f=g.primitives[0].vertex_index.reshape((nf/3,3))
        n=g.primitives[0].normal
        ni = g.primitives[0].normal_index
        vn = self.getNormals(f,v,n,ni)            
        onode,mesh = self.createsNmesh(name,v,vn,f.tolist(),smooth=True)
        mesh.inheritMaterial = False
        color = [1.,1.,1.]                
        mat = self.getColladaMaterial(g,col)
        if mat is not None :
            if type(mat.effect.diffuse) == collada.material.Map:
                color = [1,1,1]
                #get he uvset
#                        uvset = (1.0+node.geometry.primitives[0].texcoordset[0])/2.0 #-1.0 -> 1.0 to 0.0 -> 1.0
                uvset = g.primitives[0].texcoordset[0]
                uvseti = g.primitives[0].texcoord_indexset[0]
                uv = self.TextureFaceCoordintesToVertexCoordinates(v,f,uvset,uvseti)
#                        mesh.Set(textureCoords = uv)
                impath  = mat.effect.diffuse.sampler.surface.image.path
                #clean the path
                impath=impath.replace("file:////","")
#                        texture = self.createTexturedMaterial(mat.effect.diffuse.sampler.surface.image.id,impath)
#                        self.assignMaterial(mesh,texture,texture=True)
#                        self.changeObjColorMat(mesh,color)
#                        mesh.Set(textureCoords = uv)
            else :
                color = mat.effect.diffuse[0:3]
                self.changeObjColorMat(mesh,color)
            matd = mesh.materials[1028]
            if mat.effect.ambient != None and type(mat.effect.ambient) != collada.material.Map:
                matd.prop[matd.AMBI] = mat.effect.ambient[0:3]            
        return onode,mesh
        
    def buildGeometries(self,col):
        dicgeoms={}
        geoms=col.geometries
        meshDic={}
        for g in geoms:
            meshDic[g.id]={}
            dicgeoms[g.id]={}
            dicgeoms[g.id]["id"]=g.id
            v,vn,f = self.decomposeColladaGeom(g,col)
            if self.nogui:                
                dicgeoms[g.id]["node"]=None
                dicgeoms[g.id]["mesh"]=v,vn,f
            else :
                onode,mesh = self.oneColladaGeom(g,col)
                dicgeoms[g.id]["node"]=onode
                dicgeoms[g.id]["mesh"]=mesh
            meshDic[g.id]["mesh"]=v,vn,f
            dicgeoms[g.id]["instances"]=[]
            dicgeoms[g.id]["parentmesh"]=None
        return dicgeoms,meshDic
                
    def read(self,filename,**kw):
        fileName, fileExtension = os.path.splitext(filename)
#        import collada
#        print "load ",filename
        if fileExtension == ".dae" :
            daeDic=None
            col = collada.Collada(filename)#, ignore=[collada.DaeUnsupportedError,
                                            #collada.DaeBrokenRefError])
            dicgeoms,daeDic =  self.buildGeometries(col)
            
            if self.nogui : 
                return dicgeoms

            boundgeoms = list(col.scene.objects('geometry'))
            for bg in boundgeoms:
                if bg.original.id in dicgeoms:
                    node = dicgeoms[bg.original.id]["node"]
                    dicgeoms[bg.original.id]["instances"].append(bg.matrix)
            #for each nodein the scene creae an empty 
            #for each primtive in the scene create an indeedPolygins-
            uniq = False
            if len(col.scene.nodes) == 1 :
                uniq = True
            for i,node in enumerate(col.scene.nodes) : 
                #node,i,col,nodexml,parentxml=None,parent=None,dicgeoms=None
                dicgeoms=self.nodeToGeom(node,i,col,col.scene.xmlnode[i],
                                         parentxml=None,dicgeoms=dicgeoms,uniq =uniq)
            for g in dicgeoms :
                node = dicgeoms[g]["node"]
                i = dicgeoms[g]["instances"]
#                print node,g,i
                if len(i) :
                    if dicgeoms[g]["parentmesh"]  is not None :
                        self.reParent(node, dicgeoms[g]["parentmesh"] )
                        node.Set(instanceMatrices = i)
            return boundgeoms,dicgeoms,col,daeDic
#            for i,node in enumerate(col.scene.nodes) : 
#                self.transformNode(node,i,col,col.scene.xmlnode[i])
        else :
            from DejaVu.IndexedPolygons import IndexedPolygonsFromFile
            geoms = IndexedPolygonsFromFile(filename, fileName)
            self.AddObject(geoms)             
#        raw_input()
        
    def write(self,listObj,**kw):
        pass
    #DejaVu.indexedPolygon have also this function

    def writeToFile(self,polygon,filename):
        """
        Write the given polygon mesh data (vertices, faces, normal, face normal) in the DejaVu format.
        
        Create two files : filename.indpolvert and filename.indpolface. 
        
        See writeMeshToFile
        
        @type  polygon: hostObj/hostMesh/String
        @param polygon: the polygon to export in DejaVu format
        @type  filename: string
        @param filename: the destinaon filename.      
        """
        print(polygon,self.getName(polygon))
        #get shild ?
        if isinstance(polygon,IndexedPolygons):
            polygon.writeToFile(filename)


    def raycast(self,obj,point, direction, length, **kw ):
        intersect = False
        if "count" in kw :
            return intersect,0
        if "fnormal" in kw:
            return intersect,[0,0,0]
        if "hitpos" in kw:
            return intersect,[0,0,0]           
        return intersect

    def raycast_test(self, obj, start, end, length, **kw ):
        return
        from numpy import matrix
        obj = self.getObject(obj)
        mat = self.getTransformation(obj)
        mmat = matrix(mat)
        immat = mmat.I
        mat = numpy.array(immat.tolist())
        start = self.ApplyMatrix([start,],mat)[0]
        end = self.ApplyMatrix([numpy.array(end)-numpy.array(start),],mat)[0]
        vertices=[]
        faces=[]        
        if "vertices" in kw :
            vertices = kw["vertices"]
        if "faces" in kw :
            faces = kw["faces"]
        if not len(vertices):
            faces,vertices,vnormals = self.DecomposeMesh(obj,
                           edit=False,copy=False,tri=True,transform=False)
        print ("raycast",start,self.unit_vector(end)*length)
        vHitCount = 0#ray.ray_intersect_polyhedron(start, self.unit_vector(end)*length, vertices, faces,False)
        intersect = vHitCount > 0
        if "count" in kw :
            return intersect,vHitCount
        return intersect

#        
#    ##############################AR METHODS#######################################
#    def ARstep(mv):
#        #from Pmv.hostappInterface import comput_util as C
#        mv.art.beforeRedraw()
#        #up(self,dialog)
#        for arcontext in mv.art.arcontext :
#            for pat in arcontext.patterns.values():
#                if pat.isdetected:
#                    #print pat
#                    geoms_2_display = pat.geoms
#                    transfo_mat = pat.mat_transfo[:]
#                    #print transfo_mat[12:15]
#                    for geom in geoms_2_display :
#                            if hasattr(pat,'offset') : offset = pat.offset[:]
#                            else : offset =[0.,0.,0.]
#                            transfo_mat[12] = (transfo_mat[12]+offset[0])* mv.art.scaleDevice
#                            transfo_mat[13] = (transfo_mat[13]+offset[1])* mv.art.scaleDevice
#                            transfo_mat[14] = (transfo_mat[14]+offset[2])* mv.art.scaleDevice
#                            mat = transfo_mat.reshape(4,4)
#                            model = geom.obj
#    #                        print obj.GetName()
#                            #r,t,s = C.Decompose4x4(Numeric.array(mat).reshape(16,))
#                            #print t
#                            #newPos = c4dv(t)
#                            #model.SetAbsPos(newPos)
#                            #model.Message(c4d.MSG_UPDATE)
#                            setObjectMatrix(model,mat)
#                            #updateAppli()
#     
#    def ARstepM(mv):
#        #from Pmv.hostappInterface import comput_util as C
#        from mglutil.math import rotax
#        mv.art.beforeRedraw()
#        #up(self,dialog)
#        for arcontext in mv.art.arcontext :
#            for pat in arcontext.patterns.values():
#                if pat.isdetected:
#                    #print pat
#                    geoms_2_display = pat.geoms
#    
#                    #m = pat.mat_transfo[:]#pat.moveMat[:]
#                    if mv.art.concat : 
#                        m = pat.moveMat[:].reshape(16,)
#                    else :
#                        m = pat.mat_transfo[:].reshape(16,)
#                    #print transfo_mat[12:15]
#                    for geom in geoms_2_display :
#                        scale = float(mv.art.scaleObject)
#                        model = geom.obj
#                        if mv.art.patternMgr.mirror:
#                            #apply scale transformation GL.glScalef(-1.,1.,1)
#                            scaleObj(model,[-1.,1.,1.])
#                        if mv.art.concat :
#                            if hasattr(pat,'offset') : offset = pat.offset[:]
#                            else : offset =[0.,0.,0.]
#                            m[12] = (m[12]+offset[0])#* mv.art.scaleDevice
#                            m[13] = (m[13]+offset[1])#* mv.art.scaleDevice
#                            m[14] = (m[14]+offset[2])#* mv.art.scaleDevice
#                            newMat=rotax.interpolate3DTransform([m.reshape(4,4)], [1], 
#                                                            mv.art.scaleDevice)
#                            concatObjectMatrix(model,newMat)
#                        else :
#                            if hasattr(pat,'offset') : offset = pat.offset[:]
#                            else : offset =[0.,0.,0.]
#                            m[12] = (m[12]+offset[0])* mv.art.scaleDevice
#                            m[13] = (m[13]+offset[1])* mv.art.scaleDevice
#                            m[14] = (m[14]+offset[2])* mv.art.scaleDevice
#                            #r1=m.reshape(4,4)
#                            #newMat=rotax.interpolate3DTransform([r1], [1], 
#                            #                                mv.art.scaleDevice)
#                            #m[0:3][0:3]=newMat[0:3][0:3]
#                            setObjectMatrix(model,m.reshape(4,4))
#                        scaleObj(model,[scale,scale,scale])
#                        #updateAppli()
#     
#    def ARloop(mv,ar=True,im=None,ims=None,max=1000):
#        count = 0	
#        while count < max:
#            #print count
#            if im is not None:
#                updateImage(mv,im,scale=ims)
#            if ar : 
#                ARstep(mv)
#            update()
#            count = count + 1
#    
#    def AR(mv,v=None,ar=True):#,im=None,ims=None,max=1000):
#        count = 0	
#        while 1:
#            #print count
#            if v is not None:
#                #updateBmp(mv,bmp,scale=None,show=False,viewport=v)
#                updateImage(mv,viewport=v)
#            if ar : 
#                ARstepM(mv)
#            #update()
#            count = count + 1
#    
#    
#    Y=range(480)*640
#    Y.sort()
#    
#    X=range(640)*480
#    
#    
#    #import StringIO
#    #im = Image.open(StringIO.StringIO(buffer))
#    #helper.updateImage(self,viewport=Right,order=[1, 2, 3, 1])
#    def updateImage(mv,viewport=None,order=[1, 2, 3, 1]):
#        #debug image is just white...
#        try :
#            if viewport is not None :
#                viewport[c4d.BASEDRAW_DATA_SHOWPICTURE] = bool(mv.art.AR.show_tex)
#            import Image
#            cam = mv.art.arcontext[0].cam
#            cam.lock.acquire()
#            #print "acquire"
#            #arcontext = mv.art.arcontext[0]
#            #array = Numeric.array(cam.im_array[:])    
#            #n=int(len(array)/(cam.width*cam.height))
#            if mv.art.AR.debug : 
#                array = cam.imd_array[:]#.tostring()
#                #print "debug",len(array)
#            else :
#                array = cam.im_array[:]#.tostring()
#                #print "normal",len(array)
#            #img=Numeric.array(array[:])
#            #n=int(len(img)/(arcontext.cam.width*arcontext.cam.height))
#            #img=img.reshape(arcontext.cam.height,arcontext.cam.width,n)
#            #if n == 3 : 
#            #    mode = "RGB"
#            #else : 
#            #    mode = "RGBA"
#            #im = Image.fromarray(img, mode)#.resize((160,120),Image.NEAREST).transpose(Image.FLIP_TOP_BOTTOM)
#            im = Image.fromstring("RGBA",(mv.art.video.width,mv.art.video.height),
#                                  array.tostring() ).resize((320,240),Image.NEAREST)
#            #cam.lock.release()
#            #scale/resize image ?
#            #print "image"
#            rgba = im.split()
#            new = Image.merge("RGBA", (rgba[order[0]],rgba[order[1]],rgba[order[2]],rgba[order[3]]))
#            #print "save"
#            if mv.art.patternMgr.mirror :
#                import ImageOps
#                im=ImageOps.mirror(pilImage)
#                imf=ImageOps.flip(im)
#                imf.save("/tmp/arpmv.jpg")
#            else :
#                new.save("/tmp/arpmv.jpg")
#            if viewport is not None : 
#                viewport[c4d.BASEDRAW_DATA_PICTURE] = "/tmp/arpmv.jpg"
#            #print "update"
#            cam.lock.release()
#        except:
#            print "PROBLEM VIDEO"
#            
#            
#    def updateBmp(mv,bmp,scale=None,order=[3, 2, 2, 1],show=True,viewport=None):
#        #cam.lock.acquire()
#        #dialog.keyModel.Set(imarray=cam.im_array.copy())
#        #cam.lock.release()
#        #import Image
#        cam = mv.art.arcontext[0].cam
#        mv.art.arcontext[0].cam.lock.acquire()
#        array = Numeric.array(cam.im_array[:])
#        mv.art.arcontext[0].cam.lock.release()
#        n=int(len(array)/(cam.width*cam.height))
#        array.shape = (-1,4)
#        map( lambda x,y,v,bmp=bmp: bmp.SetPixel(x, y, v[1], v[2], v[3]),X, Y, array)
#    
#        if scale != None :
#            bmp.Scale(scale,256,False,False)
#            if show : c4d.bitmaps.ShowBitmap(scale)
#            scale.Save(name="/tmp/arpmv.jpg", format=c4d.symbols.FILTER_JPG)
#        else :
#            if show : c4d.bitmaps.ShowBitmap(bmp) 
#            bmp.Save(name="/tmp/arpmv.jpg", format=c4d.symbols.FILTER_JPG)
#        if viewport is not None:
#            viewport[c4d.symbols.BASEDRAW_DATA_PICTURE] = "/tmp/arpmv.jpg"
#           
#        
#            
#    def render(name,w,h):
#        doc = c4d.documents.GetActiveDocument()
#        rd = doc.GetActiveRenderData().GetData()
#        bmp = c4d.bitmaps.BaseBitmap()
#        #Initialize the bitmap with the result size.
#        #The resolution must match with the output size of the render settings.
#        bmp.Init(x=w, y=h, depth=32)
#        c4d.documents.RenderDocument(doc, rd, bmp, c4d.RENDERFLAGS_EXTERNAL)
#        #bitmaps.ShowBitmap(bmp)
#        bmp.Save(name,c4d.FILTER_TIF)
#    

    


    
