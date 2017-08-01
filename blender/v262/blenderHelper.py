
"""
    Copyright (C) <2010>  Autin L. TSRI
    
    This file git_upy/blender/v262/blenderHelper.py is part of upy.

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

import bpy
import bpy_types

from bpy import *
import mathutils
try :
    import noise
except :
    from mathutils import noise

#import numpy #still need to deal with numpy
from upy import hostHelper
from upy.hostHelper import Helper
if hostHelper.usenumpy:
    import numpy


class FrameCallBack:
    def __init__(self,cb):
        self.cb=cb
    def doit(self,scene):
        self.cb(scene.frame_current)

class blenderHelper(Helper):
    """
    The blender helper abstract class
    ============================
        This is the blend er helper Object. The helper 
        give access to the basic function need for create and edit a host 3d object and scene.
    """
    SPHERE = 'Sphere'
    CYLINDER = "Cylinder"
    CUBE = 'Cube'
    SPLINE = 'Curve'
    INSTANCE = 'Mesh'
    MESH = bpy_types.Mesh
    EMPTY = 'EMPTY'
    POLYGON = 'MESH'
    host = "blender25"
    pb = False
    BONES=""
    IK=""
    MAX_LENGTH_NAME = 21
    #there is limit in the length of the material name ....

    #dic options
    CAM_OPTIONS = {"ortho" :"ortho","persp" : "persp" }
    LIGHT_OPTIONS = {"Area":"AREA","Sun":"SUN","Spot":"SPOT"}#POINT’, ‘SUN’, ‘SPOT’, ‘HEMI’, ‘AREA’
    editmode = 0
    vshade = {"glsl":"MATERIAL","box":"BOUNDBOX","wire":"WIREFRAME","solid":"SOLID","texture":"TEXTURED","render":"RENDERED"}
    
    pbstarted = False
    
    def __init__(self,master=None,**kw):
        Helper.__init__(self)
        self.updateAppli = self.update
        self.Cube = self.box
        self.timeline_cb = {}
        #self.getCurrentScene = Blender.Scene.GetCurrent
        #self.setTranslation=self.setTranslationObj
        self.Box = self.box
        self.Geom = self.newEmpty
        #self.getCurrentScene = c4d.documents.GetActiveDocument
        self.IndexedPolygons = self.polygons
        self.Points = self.PointCloudObject 
        self.hext = "blend"
        self.editmode = False
        self.instance_dupliFace = True
        self.track_axis_dic = {
            "NEG_Z" : [0.,0.,-1],
            "POS_Z" : [0.,0.,1],
            "NEG_Y" : [0.,-1.,0.],
            "POS_Y" : [0.,1.,0.],
            "NEG_X" : [-1.,0.,0.],
            "POS_X" : [1.,0.,0.],        
        }
        self.quad={"-Z" :[[1,1,0],[1,-1,0], [-1,-1,0],[-1,1,0]],#XY
                   "+Y" :[[-1,0,1],[1,0,1],[1,0,-1], [-1,0,-1]],#XZ
                   "-X" :[[0,-1,1],[0,1,1],[0,1,-1], [0,-1,-1]],#YZ
#                   "-Z" :[[-1,1,0],[1,1,0],[1,-1,0], [-1,-1,0]],#XY
#                   "-Y" :[[-1,0,1],[1,0,1],[1,0,-1], [-1,0,-1]],#XZ
#                   "-X" :[[0,-1,1],[0,1,1],[0,1,-1], [0,-1,-1]],#YZ
                   "+Z" :[[-1,-1,0],[1,-1,0], [1,1,0],[-1,1,0]],#XY
                   "-Y" :[[-1,0,1],[-1,0,-1],[1,0,-1], [1,0,1]],#XZ
                   "+X" :[[0,-1,1],[0,-1,-1],[0,1,-1], [0,1,1]],#YZ
                  }
        
        self.noise_type ={
              "boxNoise":noise.types.BLENDER,
              "buya":noise.types.STDPERLIN,
              "cellNoise":noise.types.CELLNOISE,
              "cellVoronoi":noise.types.VORONOI_CRACKLE,
              "cranal":noise.types.STDPERLIN,
              "dents":noise.types.STDPERLIN,
              "displacedTurbulence":noise.types.STDPERLIN,
              "electrico":noise.types.STDPERLIN,
              "fbm":noise.types.STDPERLIN,
              "fire":noise.types.STDPERLIN,
              "gas":noise.types.STDPERLIN,
              "hama":noise.types.STDPERLIN,
              "luka":noise.types.STDPERLIN,
              "modNoie":noise.types.STDPERLIN,
              "naki":noise.types.STDPERLIN,
              "noise":noise.types.STDPERLIN,
              "none":noise.types.STDPERLIN,
              "nutous":noise.types.NEWPERLIN,
              "ober":noise.types.NEWPERLIN,
              "pezo":noise.types.NEWPERLIN,
              "poxo":noise.types.NEWPERLIN,
              "sema":noise.types.NEWPERLIN,
              "sparseConvolution":noise.types.NEWPERLIN,
              "stupl":noise.types.NEWPERLIN,
              "turbulence":noise.types.NEWPERLIN,
              "vlNoise":noise.types.NEWPERLIN,
              "voronoi1":noise.types.VORONOI_F1,
              "voronoi2":noise.types.VORONOI_F2,
              "voronoi3":noise.types.VORONOI_F3,
              "wavyTurbulence":noise.types.VORONOI_F4,
              "zada":noise.types.VORONOI_F4,       
             }
#            usenumpy
             
    @classmethod     
    def getCurrentScene(self):
#        return bpy.data.scenes[0] #or bpy.context.scene
        return bpy.context.scene

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
        if not self.pbstarted :
            bpy.context.window_manager.progress_begin(0, 100)
            self.pbstarted= True
        if label is None :
            label =""
        if progress is None :
            progress = 0.0
        print (progress, label)
        bpy.context.window_manager.progress_update(progress)

    def resetProgressBar(self,*args,**kwargs):
        if self.pbstarted : 
            bpy.context.window_manager.progress_end()
        self.pbstarted = False

#    def Compose4x4(self,rot,tr,sc):
#        """ compose a blender matrix of shape (16,) from  a rotation (shape (16,)),
#        translation (shape (3,)), and scale (shape (3,)) """
#        translation=Mathutils.Vector(tr[0],tr[1],tr[2])
#        scale = Mathutils.Vector(sc[0],sc[1],sc[2])
#        mat=rot.reshape(4,4)
#        mat=mat.transpose()
#        mt=Mathutils.TranslationMatrix(translation)
#        mr=Mathutils.Matrix(mat[0],mat[1],mat[2],mat[3])
#        ms=Mathutils.ScaleMatrix(scale.length, 4, scale.normalize())
#        Transformation = mt*mr#*ms
#        return Transformation
# 
    def setCurrentSelection(self, obj):
        if obj is None :
            bpy.ops.object.select_all(action='DESELECT')
        bpy.context.scene.objects.active = obj
   
    def getCurrentSelection(self,sc=None):
        if sc is None :
            sc = bpy.context.scene
        return bpy.context.selected_objects

    def setCurrentSelections(self, listeobj):
#        if obj is None :
        bpy.ops.object.select_all(action='DESELECT')
        for o in listeobj:
            o.select = True
#        print ("ok selection")
        #bpy.context.scene.objects.active = obj

    def getCurrentSelections(self,sc=None):
        if sc is None :
            sc = bpy.context.scene
        liste = [o for o in bpy.context.scene.objects if o.select]
        return bpy.context.selected_objects

#    
#    def updateAppli(self,):
#        Blender.Scene.GetCurrent().update()
#        Blender.Draw.Redraw()
#        Blender.Window.RedrawAll()
#        Blender.Window.QRedrawAll()  
#        Blender.Redraw()
#    
#    def update(self,):
#        import Blender
#        Blender.Scene.GetCurrent().update()
#        Blender.Draw.Redraw()
#        Blender.Window.RedrawAll()
#        Blender.Window.QRedrawAll()  
#        Blender.Redraw()
#
    def setEditMode(self):
        if not self.editmode:
            bpy.ops.object.editmode_toggle()
    def setObjectMode(self):
        bpy.ops.object.mode_set(mode='OBJECT')
        self.editmode = False
        
    def toggleEditMode(self):
        bpy.ops.object.editmode_toggle()
        self.editmode = not self.editmode
#        bpy.ops.object.editmode_toggle()
#        editmode = Blender.Window.EditMode()    # are we in edit mode?  If so ...
#        if editmode: 
#            Blender.Window.EditMode(0)
        return 1
#
    def restoreEditMode(self,editmode=1):
#        bpy.ops.object.mode_set(mode='OBJECT')
        pass
#        bpy.ops.object.editmode_toggle()
#        Blender.Window.EditMode(editmode)

    def synchronize(self,cb):
        self.timeline_cb[cb] = FrameCallBack(cb)
        bpy.app.handlers.frame_change_post.append(self.timeline_cb[cb].doit)

    def unsynchronize(self,cb):
        i = bpy.app.handlers.frame_change_post.index(self.timeline_cb[cb].doit)
        bpy.app.handlers.frame_change_post.pop(i)
        
    def updateViewer(self):
        bpy.context.scene.update()

    def getSpaceView3D(self):
        for area in bpy.data.screens['Default'].areas[:]:
            if area.type == "VIEW_3D":
                print(area.spaces.active.lens)
                return area.spaces.active
                
    def setViewport(self,**kw):
        """
        set the property of the viewport
        
        * overwrited by children class for each host
        >>>helper.setViewport(clipstart=0,clipend=diag,shader="GLSL")
        
        @type  kw: dictionary
        @param kw: the list of parameter and their value to change   
        """  
        print (kw)
        sv3d = self.getSpaceView3D()
        if "center" in kw :
            if kw["center"] :
                bpy.ops.view3d.view_all(center=False)
        if "clipstart" in kw :
            if kw["clipstart"] == 0 :
                kw["clipstart"]= 0.001
            sv3d.clip_start = kw["clipstart"]
            print ("clipstart ",kw["clipstart"])
        if "clipend" in kw :
            sv3d.clip_end = kw["clipend"]
            print ("clipend ",kw["clipend"])
        if "shader" in kw :
            engine = bpy.context.scene.render.engine
            if engine == 'CYCLE':
                sv3d.viewport_shade = self.vshade[kw["shader"]]
                sv3d.show_textured_solid = True
            else :
                sv3d.viewport_shade = self.vshade["solid"]
                sv3d.show_textured_solid = True
            print ("shader ",kw["shader"],self.vshade[kw["shader"]])
            
           
    def getType(self, object):
        if type(object) is str:
            object = self.getObject(object)
        #test if sphere
        #if empty dont check if sphere
        atype=""
        if hasattr(object,"type"):
            atype=object.type
        else :
            atype = type(object)
        if atype == self.EMPTY:
            return atype
        isph = self.isSphere(object)
        if isph :
            return self.SPHERE
        else :
            if hasattr(object,"type"):
                return object.type
            else :
                return type(object)

    def getName(self,o):
        if type(o) is str:
            return o
        else:
            return o.name

    def getMaterial(self,name):
        return bpy.data.materials.get(name)
#
    def getMaterialObject(self,o):
        return [slot.material for slot in o.material_slots]
        
    def getMaterialName(self,mat):
        return mat.name

    def updateObject(self,obj):
        pass
#        obj = self.getObject(obj)
#        obj.makeDisplayList()
#
    def getObject(self,name):
        obj=None
        if type(name) is not str:
            return name
        try :
            obj= bpy.data.objects.get(name)
        except : 
            obj=None
#        #print obj
        return obj
#

    def getObjectFromMesh(self,mesh):
        #what if mesh is already an object
        if isinstance(mesh,bpy.types.Object) and mesh.type ==  'MESH':
            return mesh
        if type(mesh) is str :
            mesh = self.getMesh(mesh)
        for obj in bpy.data.objects:
            if obj.type == 'MESH':
                if obj.data == mesh :
                    return obj

    def getMeshFrom(self,obj):
        #obj = self.getObject(obj)
        obj.select = True
        self.getCurrentScene().objects.active = obj
        mesh = obj.data
        return mesh

    def getProperty(self, obj, key):
        if not isinstance(obj, bpy.types.Object):
            raise Exception("expected an Object for the obj argument")
        if not isinstance(key, str):
            raise Exception("expected a str for the key argument")
        if not key in obj:
            if not hasattr(obj,key):
                return None
            else :
                return getattr(obj,key)
        return obj[key]
        
    def setProperty(self, obj, key, value):
        cool_value_types = (int, float, str, dict, list)
        def check_property_values(value, name):
            """Recursively check property types and values"""
            if not isinstance(value, (int, float, str, dict, list)):
                raise Exception("expected a %s for the property: %s"%\
                      (", ".join("%s"%t.__name__ for t in cool_value_types), name))
#            
            if isinstance(value, dict):
                for key, val in list(value.items()):
                    check_properties(val, name+"['%s']"%key)
            if isinstance(value, (list, str)) and len(value) > 10000:
                raise Exception("property: %s is a %s which is "\
                      "too long. Max size: 10000 "%(name, str(type(value))))
#        
        if not isinstance(obj, bpy.types.Object):
            raise Exception("expected an Object for the obj argument")
        if not isinstance(key, str):
            raise Exception("expected a str for the key argument")

        check_property_values(value, key)
        
        obj[key] = value
 
    def setPropertyObject(self,obj,**kw):
        for k in kw :
            if hasattr(obj,k):
                setattr(obj,k,kw[k])                   
#
    def checkIsMesh(self,mesh):
        #verify that we are not in editModes
#        o=mesh
#        mods = o.modifiers
#        if mods:
#            print("Attention: Modifiers on ", mesh)
#            try:
#                mesh = Blender.Mesh.Get('container')
#            except:
#                mesh = Blender.Mesh.New('container')
#            mesh.getFromObject(o)
#            return mesh
#        print (mesh,type(mesh))
        if type(mesh) is str :
            return self.getMesh(mesh)
        if type(mesh) == bpy.types.Object: # should we check that its not an empty ?
            return self.getMeshFrom(mesh) 
        if type(mesh) == bpy.types.Mesh:
            return mesh
#
    def getMesh(self,name,**kw):
        if type(name) != str :
            if type(name) == bpy.types.Object:
                return name.data
            elif type(name) == bpy.types.Mesh:
                return name
        else :
            #name of the mesh or the object?
            mesh = bpy.data.meshes.get(name)
            if mesh is None : 
                obj = bpy.data.objects.get(name)
                if obj is not None :
                    return obj.data
                else :
                    return None
            return mesh
#
#    def getNMesh(self,name):
#        mesh = None
#        if type(name) != str:
#            return name
#        try :
#           mesh = NMesh.GetRaw(name)
#        except:
#            mesh = None
#        return mesh
#
    def getChilds(self,obj):
        scn= self.getCurrentScene()
#        childs = [ob_child for ob_child in Blender.Object.Get() if ob_child.parent == obj]
        childs = [ob_child for ob_child in list(scn.objects.values()) if ob_child.parent == obj]
        return childs
#
    def reParent(self,obj,parent):
        #should I apply scale/rotation...
        parent = self.getObject(parent)
        if type(obj) == list or type(obj) == tuple: 
            for o in obj :
                o = self.getObject(o)
                o.parent = parent
        else : 
            obj = self.getObject(obj)
            if obj is not None :
                obj.parent = parent#.makeParent([obj,])
#
    def getTransformation(self,name,**kw):
        obj = self.getObject(name)
        return obj.matrix_world

    def getTrackAxis(self,v):
        #problem with neer zero value
        nearZero=6.123233995736766e-10
        for i in range(3):
            if abs(v[i])<=nearZero : 
                v[i]=0.0
        for a in self.track_axis_dic:
            if self.FromVec(self.track_axis_dic[a]) == self.FromVec(v) :
                return a
        return "POS_Z"

    def transposeMatrix(self,matrice):
        if matrice is not None :
            if isinstance(matrice,numpy.ndarray) :
#                mat = matrice.tolist()
                mat = matrice.transpose().tolist()
                return mat
            blender_mat=mathutils.Matrix(mat)#from Blender.Mathutils
            blender_mat.transpose()        
            return blender_mat
        return matrice
        
    def getObjectMatrix(self,obj):
        t = obj.location
        s = obj.scale
        mat_rot = obj.rotation_euler.to_matrix().to_4x4()
        scalem = [[s[0],0.,0.],[0.,s[1],0.],[0.,0.,s[2]]]
        mat_scale = mathutils.Matrix(scalem).to_4x4()
        mat_trans = mathutils.Matrix.Translation(t)
        mat = mat_trans * mat_rot * mat_scale
        return mat

    def setObjectMatrix(self,o,matrice=None,hostmatrice=None,transpose = False):
        if matrice == None and hostmatrice == None :
            return
        if type(o) == str : obj=self.getObject(o)
        else : obj=o
        #matrix(16,)
        if matrice is not None :
            if isinstance(matrice,numpy.ndarray) :
                mat = matrice.transpose().tolist()
            else :
                mat = matrice#  = mat#numpy.array(matrice)
            #m=matrice.reshape(4,4)
            #if transpose : m = m.transpose()
            #mat=m.tolist()
            blender_mat=mathutils.Matrix(mat)#from Blender.Mathutils
            
        elif hostmatrice is not None :
            blender_mat=hostmatrice
        #if transpose :  
        #blender_mat.transpose()#change nothing ?
#        print (blender_mat)
        if transpose : blender_mat.transpose()
        obj.matrix_world = blender_mat
        #Sets the object's matrix and updates its transformation. 
        #If the object has a parent, the matrix transform is relative to the parent.
#
    def setTranslation(self,obj,pos=[0.0,0.,0.],**kw):
        obj=self.getObject(obj)
        obj.location = (pos[0],pos[1],pos[2])

    def setTranslationObj(self,obj,coord):
        obj=self.getObject(obj)
        obj.location = (coord[0],coord[1],coord[2])
#
    def getTranslation(self,name):
        obj = self.getObject(name)
        return obj.location#("worldspace")#[obj.LocX,obj.LocY,obj.LocZ]#obj.matrixWorld[3][0:3] 
#        
    def translateObj(self,obj,coord,use_parent=False):
        obj.location=obj.location+mathutils.Vector((float(coord[0]),float(coord[1]),float(coord[2])))

#    
    def scaleObj(self,obj,sc):
        if type(sc) is float :
            sc = [sc,sc,sc]        
        obj.scale = sc
#        obj.dimensions = sc
        #what about the dimension ? 
        #if the dimensio are not equal should take it in account or actually use the dimension
#        obj.SizeX=float(sc[0])
#        obj.SizeY=float(sc[1])
#        obj.SizeZ=float(sc[2])
#    
    def rotateObj(self,obj,rot):
        #radians
        obj.rotation_euler.x=float(rot[0])
        obj.rotation_euler.y=float(rot[1])
        obj.rotation_euler.z=float(rot[2])

    def getScale(self,name,absolue=True):
        obj = self.getObject(name)     
        return obj.scale
#    
    def newEmpty(self,name,location=(0.,0.,0.),visible=0,**kw):
        res = bpy.ops.object.add(type='EMPTY',location=location)
        obj = bpy.context.object
        obj.name = name
        parent = None
        if "parent" in kw :
            parent = kw["parent"]
        self.addObjectToScene(self.getCurrentScene(),obj,parent=parent)        
        return obj


    def updateMasterInstance(self,master, newMesh,**kw):
        #if master is group then remove it from group and put the other gjec in the group
        #ew mesis a list
        master = self.getObject(master) 
        if len(master.users_group):
            if len(master.users_group) > 1 :
                group = master.users_group[-1]
            else :
                group = master.users_group[0]
#            group.objects.unlink(master)#is thi
            self.addToGroup(master,newMesh,group=group)
            self.removeToGroup(master,[master],group=group)  
        else :
            print ("no group ? ",master, master.name)
#        for o in newMesh :
#            o =  self.getObject(o)
#            group.objects.link(o)
        #should we use the layer of group here 
        #group.layers
#        self.setLayers(newMesh,[1])?
#        groupname = master.users_group[0].name       
#        self.setCurrentSelections(master)
#        bpy.ops.group.objects_remove()
#        self.setCurrentSelections(newMesh)
#        bpy.ops.object.group_link(groupname)
#        #group_link
        
        #newInstance(name,instance,coord,parent=parent)
    def removeToGroup(self,master,objects,group=None):
        if group is None :
            master = self.getObject(master)         
            group = master.users_group[0]
        for o in objects :
            o =  self.getObject(o)
            try :
                group.objects.unlink(o)
            except:
                print ("in group already unlink",o,o.name)
            chs = self.getChilds(o)
            self.removeToGroup(master,chs,group=group) 
            
    def addToGroup(self,master,objects,group=None):
        if group is None :
            master = self.getObject(master) 
            group = master.users_group[0]
        for o in objects :
            o =  self.getObject(o)
            try :
                group.objects.link(o)
            except:
                print ("in group already",o,o.name)
            chs = self.getChilds(o)
            self.addToGroup(master,chs,group=group)       

    def newInstanceGroup(self,name,ob,location=None,hostmatrice=None,
                    matrice=None,parent=None,**kw):
        #check the type of mesh
#        print ("instance of ",ob)
        #first needto check if ob have child or just one object        
        dupligroup = False
        mesh = None
        if mesh is None :
#            if type(ob) is str:
            ob=self.getObject(ob)
#            print "type",ob,self.getType(ob)
            childs = self.getChilds(ob)
            if len(childs) : #need to group and then dupligroup
                dupligroup = True
                #select paren and children
                #should actually get recursvly all childs not first level!
                #childs.extend([ob]) #so we can translate out of he view the masterinstance
                self.setCurrentSelections([ob])#theses object have to be visible to make it work!
#                print ("selected childs",childs)
                #check if the group exist
                namegroup = self.getName(ob)+"_gr"
                if not namegroup in bpy.data.groups: 
                    bpy.ops.group.create(name=namegroup)
                    #print ("group  created",namegroup)
                    self.addToGroup(ob,childs)  
                #create the instance
                bpy.ops.object.group_instance_add(group=namegroup,location=[0,0,0],rotation=[0,0,0])#'INVOKE_DEFAULT'?ix400_n25MeshsParent_gr
                #print ("group  group_instance_add")
                OBJ = bpy.context.object
                OBJ.name = name
                if parent is not None:
#                    print (OBJ,parent)
                    if OBJ != parent :
                        OBJ.parent = parent
                if matrice is None and hostmatrice is None :
                        hostmatrice = mathutils.Matrix.Identity(4)
                #print ("group  instance created",name,namegroup)
            else :
#            if self.getType(ob) == self.EMPTY:
#                get the child mesh
#                childs = self.getChilds(ob)#should have one
#                print childs
#                mesh=childs[0].data
#            else :
                mesh=ob.data
                #mesh=obj.getData(False,True)
                OBJ=bpy.data.objects.new(name,mesh)
                self.addObjectToScene(self.getCurrentScene(),OBJ)
                bpy.context.scene.objects.active = OBJ        
                if parent is not None:
                    OBJ.parent = parent
        else :
            OBJ=bpy.data.objects.new(name,mesh)
            self.addObjectToScene(self.getCurrentScene(),OBJ)
            bpy.context.scene.objects.active = OBJ        
            if parent is not None:
                OBJ.parent = parent
        #print ("OBJ created",OBJ) 
        #set the instance matrice
        transpose = False
        if "transpose" in kw :
            transpose = kw["transpose"]
#        print ("set objecMatrix")
#        if matrice is not None and hostmatrice is None :
        
        if location != None :
            self.translateObj(OBJ,location)
        else :
            self.setObjectMatrix(OBJ,matrice=matrice,
                         hostmatrice=hostmatrice,transpose=transpose)
#        print ("transformed")
        if "material" in kw :
            mat = kw["material"]
            if not dupligroup : self.assignMaterial(OBJ,[mat])
        
        return OBJ
                
    def newInstance(self,name,ob,location=None,hostmatrice=None,
                    matrice=None,parent=None,**kw):
        #check the type of mesh
#        print ("instance of ",ob)
        #first needto check if ob have child or just one object        
        dupligroup = False
        mesh = None
        for me in bpy.data.meshes:
            if ob == me :
                mesh = ob
                break
        if mesh is None :
#            if type(ob) is str:
            ob=self.getObject(ob)
#            print "type",ob,self.getType(ob)
            childs = self.getChilds(ob)
            if len(childs) : #need to group and then dupligroup
                dupligroup = True
                #select paren and children
                #should actually get recursvly all childs not first level!
                #childs.extend([ob]) #so we can translate out of he view the masterinstance
                self.setCurrentSelections([ob])#theses object have to be visible to make it work!
#                print ("selected childs",childs)
                #check if the group exist
                namegroup = self.getName(ob)+"_gr"
                if not namegroup in bpy.data.groups: 
                    bpy.ops.group.create(name=namegroup)
                    #print ("group  created",namegroup)
                    self.addToGroup(ob,childs)  
                #create the instance
                bpy.ops.object.group_instance_add(group=namegroup,location=[0,0,0],rotation=[0,0,0])#'INVOKE_DEFAULT'?ix400_n25MeshsParent_gr
                #print ("group  group_instance_add")
                OBJ = bpy.context.object
                OBJ.name = name
                if parent is not None:
#                    print (OBJ,parent)
                    if OBJ != parent :
                        OBJ.parent = parent
                if matrice is None and hostmatrice is None :
                        hostmatrice = mathutils.Matrix.Identity(4)
                #print ("group  instance created",name,namegroup)
            else :
#            if self.getType(ob) == self.EMPTY:
#                get the child mesh
#                childs = self.getChilds(ob)#should have one
#                print childs
#                mesh=childs[0].data
#            else :
                mesh=ob.data
                #mesh=obj.getData(False,True)
                OBJ=bpy.data.objects.new(name,mesh)
                self.addObjectToScene(self.getCurrentScene(),OBJ)
                bpy.context.scene.objects.active = OBJ        
                if parent is not None:
                    OBJ.parent = parent
        else :
            OBJ=bpy.data.objects.new(name,mesh)
            self.addObjectToScene(self.getCurrentScene(),OBJ)
            bpy.context.scene.objects.active = OBJ        
            if parent is not None:
                OBJ.parent = parent
        #print ("OBJ created",OBJ) 
        #set the instance matrice
        transpose = False
        if "transpose" in kw :
            transpose = kw["transpose"]
#        print ("set objecMatrix")
#        if matrice is not None and hostmatrice is None :
        
        if location != None :
            self.translateObj(OBJ,location)
        else :
            self.setObjectMatrix(OBJ,matrice=matrice,
                         hostmatrice=hostmatrice,transpose=transpose)
#        print ("transformed")
        if "material" in kw :
            mat = kw["material"]
            if not dupligroup : self.assignMaterial(OBJ,[mat])
        
        return OBJ
#    #alias
    setInstance = newInstance
#    def setInstance(self,name,obj, matrix):
#        mesh=obj.getData(False,True)
#        o = Blender.Object.New("Mesh",name)
#        o.link(mesh)
#        o.setMatrix(matrix)
#        return o
#

    def instancePolygon(self,name, matrices=None,hmatrices=None, 
                        mesh=None,parent=None,
                        transpose=True,globalT=True,dupliVert=True,**kw):
        hostM= False
        if hmatrices is not None :
            matrices = hmatrices
            hostM = True
        if matrices == None : return None
        if mesh == None : return None
        instance = []
#        print ("ok", len(matrices))#4,4 mats
#        if isinstance(matrices,numpy.ndarray) :
#            matrices = matrices.tolist()
#        if isinstance(matrices[0],numpy.ndarray) :
#            matrices = numpy.array(matrices).tolist()
        print (self.instance_dupliFace)
        if self.instance_dupliFace:
            v=[0.,1.,0.]
            if "axis" in kw and kw["axis"] is not None:
                v=kw["axis"]
            print ("axis",v)
            o = self.getObject(name+"ds") 
            if o is None :
#                o,m=self.matrixToVNMesh(name,matrices,vector=v)
                o,m=self.matrixToFacesMesh(name,matrices,vector=v,transpose=transpose)
                if parent is not None :
                    o.parent = parent
                #put the object to be instanced child of it
                mesh.parent = o
                #mesh need to be in main layer
    #            self.setLayers(mesh,[0])
                instance=[o]
                o.dupli_type = "FACES"
#                o.use_dupli_vertices_rotation = True
#                kw = {"track_axis":self.getTrackAxis(v)}
#                self.applyToRec(mesh,self.setPropertyObject,**kw)
            else :
                #update
                pass
            return o
            #rotation checkbox->use normal
        elif self.dupliVert:
            v=[0.,1.,0.]
            if "axis" in kw and kw["axis"] is not None:
                v=kw["axis"]
            print ("axis",v)
            o = self.getObject(name) 
            if o is None :
                o,m=self.matrixToVNMesh(name,matrices,vector=v,transpose=transpose)
                if parent is not None :
                    o.parent = parent
                #put the object to be instanced child of it
                mesh.parent = o
                #mesh need to be in main layer
    #            self.setLayers(mesh,[0])
                instance=[o]
                o.dupli_type = "VERTS"
                o.use_dupli_vertices_rotation = True
                kw = {"track_axis":self.getTrackAxis(v)}
                self.applyToRec(mesh,self.setPropertyObject,**kw)
#                mesh.track_axis = self.getTrackAxis(v)
                #apply to children
                
            else :
                #update
                pass
            #rotation checkbox->use normal
        else :
            for i in range(len(matrices)):
                self.progressBar(float(i)/len(matrices),label=str(i)+"/"+str(len(matrices)))
    #            print (i)
    #            print (name+str(i))
                mat = matrices[i]
    #            print (mat)
            #for i,mat in enumerate(matrices):
    #            print (mat) 
                inst = self.getObject(name+str(i)) 
                #print (inst)
                if inst is None :
                    if hostM :
                        inst = self.newInstance(name+str(i),mesh,
                                            hostmatrice=mat,matrice=None,
                                            parent=parent,transpose=transpose)
                    else :
                        inst = self.newInstance(name+str(i),mesh,
                                            hostmatrice=None,matrice=mat,
                                            parent=parent,transpose=transpose)
                else :
                    #updateInstanceShape ?
                    if hostM :
                        self.setObjectMatrix(inst,hostmatrice=mat,transpose=transpose)
                    else :
                        self.setObjectMatrix(inst,matrice=mat,transpose=transpose)
                instance.append(inst)
            #instance[-1].MakeTag(c4d.Ttexture)
        return instance

    def addObjectToScene(self,sc,obj,parent=None,centerRoot=True,rePos=None):
        #objects must first be linked to a scene before they can become parents of other objects.
        if sc is None :
            sc = self.getCurrentScene()
        if type(obj) == list or type(obj) == tuple: 
            for o in obj : 
                if o not in list(sc.objects.values()) : sc.objects.link(o)
        else : 
            if obj not in list(sc.objects.values()) : 
                sc.objects.link(obj)
        if parent != None: 
            parent = self.getObject(parent)
            self.reParent(obj,parent)
            #if type(obj) == list or type(obj) == tuple: parent.makeParent(obj)
            #else : parent.makeParent([obj,])

    def addCameraToScene(self,name,Type='persp',focal=30.0,center=[0.,0.,0.],sc=None):
        res = bpy.ops.object.add(type='CAMERA',location=(center[0],center[1],center[2]))
        obj = bpy.context.object
        obj.name = name
        obj.rotation_euler[2] = 2.*math.pi # rotZ
#        obj.hide_select=True
        cam = obj.data
        cam.name = name
        cam.lens = focal
        #cam.type 'PERSP'/'ORTHO'
        cam.clip_end=1000.    #clip_start
        bpy.context.scene.camera = obj
        #Window.CameraView()
        return obj

    def addLampToScene(self,name,Type='Area',rgb=[1.,1.,1.],dist=25.0,energy=1.0,
                       soft=1.0,shadow=False,center=[0.,0.,0.],sc=None,**kw):
        res = bpy.ops.object.add(type='LAMP',location=(center[0],center[1],center[2]))
        obj = bpy.context.object
        obj.name = name
        lampe = obj.data
        lampe.name = name
        lampe.color = (rgb[0],rgb[1],rgb[2])
        lampe.distance = dist
        lampe.energy = energy
        lampe.type = self.LIGHT_OPTIONS[Type]
        #lampe.setSoftness(soft)
        if shadow : 
            lampe.shadow_method = 'RAY_SHADOW'
#        obj.hide_select=True#?

    def deleteObject(self,obj):
        sc = self.getCurrentScene()
        try :
            sc.objects.unlink(obj)
            bpy.data.objects.remove(obj)
        except:
            print(("problem deleting ", obj))

#    
#    def ObjectsSelection(self,listeObjects,typeSel="new"):
#        """
#        Modify the current object selection.
#        
#        @type  listeObjects: list
#        @param listeObjects: list of object to joins
#        @type  typeSel: string
#        @param listeObjects: type of modification: new,add,...
#    
#        """    
#        dic={"add":None,"new":None}
#        sc = self.getCurrentScene()
#        if typeSel == "new" :
#            sc.objects.selected = listeObjects
#        elif typeSel == "add":
#            sc.objects.selected.extend(listeObjects)
#    
#    def JoinsObjects(self,listeObjects):
#        """
#        Merge the given liste of object in one unique geometry.
#        
#        @type  listeObjects: list
#        @param listeObjects: list of object to joins
#        """    
#        sc = getCurrentScene()
#        #put here the code to add the liste of object to the selection
#        listeObjects[0].join(listeObjects[1:])
#        for ind in range(1,len(listeObjects)):
#            sc.unlink(listeObjects[ind])  
#
#
    def getMaterial(self,mat):
        if type(mat) is str:
            if len(mat) > self.MAX_LENGTH_NAME:
                mat = mat[:self.MAX_LENGTH_NAME]
            try :
                return bpy.data.materials.get(mat)
            except :
                return None
        else :
            return mat

    def getAllMaterials(self):
        return list(bpy.data.materials.keys())

#http://wiki.blender.org/index.php/Dev:2.5/Py/Scripts/Cookbook/Materials/Multiple_Materials
    def addMaterial(self,name,col):
        #need toc heck if mat already exist\
        #mats = Material.Get()
        #if name not in mats :
        #    mat = Material.New(name)
        #else :
        mat = bpy.data.materials.new(name)
        #mat.diffuse_shader = 'MINNAERT'
        #mat.darkness = 0.8
        mat.diffuse_color = (col[0],col[1],col[2])
        return mat

    def createVolumeMaterial(self,name,mat=None,**kw):     
        textType ='POINT_DENSITY'
        if 'type' in kw :
            textType = kw["type"]            
        footex = bpy.data.textures.new(name+"volume",type = textType)             
        if mat is None :
            mat = bpy.data.materials.new(name)    # get a material
        mat.type='VOLUME'
        Tslot = mat.texture_slots.add()
        Tslot.texture = footex 
        return mat,footex
    
    def createTexturedMaterial(self,name,filename,normal=False,mat=None,w=640,h=480):
      
        footex = bpy.data.textures.new(name+"texture",type = 'IMAGE' )             
        # get texture named 'foo'
        #footex = footex.recast_type()
        footex.use_normal_map = normal
        # make foo be an image texture
        if filename is None:
            img = bpy.data.images.new(name,width=w, height = h)
            #img = bpy.data.images[f]            
            img.filepath = name
            img.save()
        else :
            img = bpy.data.images.load(filename)           # load an image
        footex.image = img                   # link the image to the texture
        if mat is None :
            mat = bpy.data.materials.new(name)    # get a material
        
        Tslot = mat.texture_slots.add()
        Tslot.texture = footex 
#        Tslot.texture_coords  #default is ORCO    
#        use_texture
#        use_face_texture
#        use_face_texture_alpha
#        mtextures = mat.getTextures()
#        mtextures[0].texco = Blender.Texture.TexCo.UV#16
#        if normal:
#            mtextures[0].mapto = Blender.Texture.MapTo.NOR#2
#        else :
#            mtextures[0].mapto = Blender.Texture.MapTo.COL#1
        return mat,footex
#

    def applyToRec(self,obj, cb, **kw):
        cb(obj,**kw)
        chs = self.getChilds(obj)
        for ch in chs :
            cb(ch,**kw)

    def toggleDisplay(self,ob,display=True,child=True):
        if type(ob) == str : obj=self.getObject(ob)
        elif type(ob) is list :
            [self.toggleDisplay(o,display=display) for o in ob]
            return
        else : 
            obj=ob
        if obj is None :
            return            
        obj.hide=not display
        obj.hide_render=not display
        if child :
            chs = self.getChilds(obj)
            self.toggleDisplay(chs,display=display)
            #for ch in chs:
                
        #obj.makeDisplayList()

    def toggleXray(self,object,xray):
        obj = self.getObject(object)
        if obj is None :
            return
        obj.show_x_ray = xray

    def getVisibility(self,obj,editor=True, render=False, active=False):
        #0 off, 1#on, 2 undef
        #active = restriceted selection ?
        display = {0:True,1:False,2:True}
        if type (obj) == str :
            obj = self.getObject(obj)
        if editor and not render and not active:
            return obj.hide
        elif not editor and render and not active:
            return obj.hide_render
        else :
            return obj.hide,obj.hide_render,False

#    
#    def b_matrix(self,array):
#        return Mathutils.Matrix(array)
#    
#    def b_toEuler(self,bmatrix):
#        return bmatrix.toEuler()
#    
#    def Compose4x4BGL(self,rot,trans,scale):
#        """ compose a matrix of shape (16,) from  a rotation (shape (16,)),
#        translation (shape (3,)), and scale (shape (3,)) """
#        GL.glMatrixMode(GL.GL_MODELVIEW)
#        GL.glPushMatrix()
#        GL.glLoadIdentity()
#        GL.glTranslatef(float(trans[0]),float(trans[1]),float(trans[2]))
#        GL.glMultMatrixf(rot)
#        GL.glScalef(float(scale[0]),float(scale[1]),float(scale[2]))
#        m = numpy.array(GL.glGetDoublev(GL.GL_MODELVIEW_MATRIX)).astype('f')
#        GL.glPopMatrix()
#        return numpy.reshape(m,(16,))
#
    def bezFromVecs(self,vecs0,vecs1):
       '''
       Bezier triple from 3 vecs, shortcut functon
       '''
       dd=[0.,0.,0.]
       vecs=[0.,0.,0.]
       for i in range(3): dd[i]=vecs1[i]-vecs0[i]
       for i in range(3): vecs[i]=vecs1[i]+dd[i]
       #vecs2=vecs1+(vecs0*-1)
       return vecs0,vecs1,vecs
#       bt= BezTriple.New(vecs0[0],vecs0[1],vecs0[2],vecs1[0],vecs1[1],
#                            vecs1[2],vecs[0],vecs[1],vecs[2])
#       bt.handleTypes= (BezTriple.HandleTypes.AUTO, BezTriple.HandleTypes.AUTO)
#       return bt
#       
#    def bezFromVecs2(self,vecs0,vecs1,vecs):
#       '''
#       Bezier triple from 3 vecs, shortcut functon
#       '''
#       #projection of v1 on v0->v2
#       #
#       B=numpy.array([0.,0.,0.])
#       H1=numpy.array([0.,0.,0.])
#       H2=numpy.array([0.,0.,0.])
#       for i in range(3): B[i]=vecs1[i]-vecs0[i]                      
#       A=numpy.array([0.,0.,0.])
#       for i in range(3): A[i]=vecs[i]-vecs0[i]
#       #Projection B on A
#       scalar=(((A[0]*B[0])+(A[1]*B[1])+(A[2]*B[2]))/((A[0]*A[0])+(A[1]*A[1])+(A[2]*A[2])))
#       C=scalar*A
#       #vector C->A
#       dep=A-C
#       for i in range(3):
#            vecs0[i]=(vecs0[i]+dep[i])
#            vecs[i]=(vecs[i]+dep[i])
#       for i in range(3): H1[i]=(vecs[i]-vecs1[i])
#       for i in range(3): H2[i]=(-vecs[i]+vecs1[i])
#       H1=self.normalize(H1.copy())*3.
#       H2=self.normalize(H2.copy())*3.
#       vecs0=Vector(vecs1[0]-H1[0],vecs1[1]-H1[1],vecs1[2]-H1[2])
#       vecs=Vector(vecs1[0]-H2[0],vecs1[1]-H2[1],vecs1[2]-H2[2])
#       #vecs2=vecs1+(vecs0*-1)
#       bt= BezTriple.New(vecs0[0],vecs0[1],vecs0[2],vecs1[0],vecs1[1],vecs1[2],vecs[0],vecs[1],vecs[2])
#       bt.handleTypes= (BezTriple.HandleTypes.FREE , BezTriple.HandleTypes.FREE )
#       return bt
#
    def bez2FromVecs(self,vecs1):
        return None,vecs1,None
#       bt= BezTriple.New(vecs1[0],vecs1[1],vecs1[2])
#       bt.handleTypes= (BezTriple.HandleTypes.AUTO  , BezTriple.HandleTypes.AUTO  )
#       
#       return bt
                      
    def bezFromVecs1(self,vecs0,vecs1,vecs): #tYPE vECTOR
       '''
       Bezier triple from 3 vecs, shortcut functon
       '''
       #rotatePoint(pt,m,ax)
       A=mathutils.Vector((0.,0.,0.))
       B=mathutils.Vector((0.,0.,0.))
       H2=mathutils.Vector((0.,0.,0.))
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
       vecs0=self.FromVec(nA)
       vecs=self.FromVec(nB)
       #vecs2=vecs1+(vecs0*-1)
       return vecs0,vecs1,vecs
#       bt= BezTriple.New(vecs0[0],vecs0[1],vecs0[2],vecs1[0],vecs1[1],vecs1[2],vecs[0],vecs[1],vecs[2])
#       bt.handleTypes= (BezTriple.HandleTypes.FREE , BezTriple.HandleTypes.FREE )
#       
#       return bt
#        
#    def bezSquare(self,r,name):
#          kappa=4*((math.sqrt(2)-1)/3)
#          l = r * kappa
#          pt1=[0.,r,0.]
#          pt1h=[-l,r,0.]
#          pt2=[r,0.,0.]
#          pt2h=[r,l,0.]
#          pt3=[0.,-r,0.]
#          pt3h=[l,-r,0.]
#          pt4=[-r,0.,0.]
#          pt4h=[-r,-l,0.]
#          cu= Blender.Curve.New(name)
#          coord1=pt1
#          cu.appendNurb(self.bez2FromVecs(pt1))
#          cu_nurb=cu[0]
#          coord1=pt2
#          cu_nurb.append(self.bez2FromVecs(pt2))
#          coord1=pt3
#          cu_nurb.append(self.bez2FromVecs(pt3))
#          coord1=pt4
#          cu_nurb.append(self.bez2FromVecs(pt4))
#          cu_nurb.append(self.bez2FromVecs(pt1))
#          #scn= Scene.GetCurrent()
#          #ob = scn.objects.new(cu)
#          return cu
#
#    def bezCircle(self,r,name):
#          kappa=4*((math.sqrt(2)-1)/3)
#          l = r * kappa
#          pt1=[0.,r,0.]
#          pt1h=[-l,r,0.]
#          pt2=[r,0.,0.]
#          pt2h=[r,l,0.]
#          pt3=[0.,-r,0.]
#          pt3h=[l,-r,0.]
#          pt4=[-r,0.,0.]
#          pt4h=[-r,-l,0.]
#          cu= Blender.Curve.New(name)
#          coord1=pt1
#          cu.appendNurb(self.bezFromVecs(pt1h,pt1))
#          cu_nurb=cu[0]
#          coord1=pt2
#          cu_nurb.append(self.bezFromVecs(pt2h,pt2))
#          coord1=pt3
#          cu_nurb.append(self.bezFromVecs(pt3h,pt3))
#          coord1=pt4
#          cu_nurb.append(self.bezFromVecs(pt4h,pt4))
#          cu_nurb.append(self.bezFromVecs(pt1h,pt1))
#          #scn= Scene.GetCurrent()
#          #ob = scn.objects.new(cu)
#          return cu
#
#    def createShapes2D(self,doc=None,parent=None):
#        if doc is None :
#            doc = self.getCurrentScene()    
#        circle = doc.objects.new(self.bezCircle(0.3,'Circle'))
#        square = doc.objects.new(self.bezSquare(0.3,'Square'))
#        return [circle,square]
#        
    def bezList2Curve(self,x,curveData,cType):
        '''
        Take a list or vector triples and converts them into a bezier curve object
        '''
        # Create the curve data with one point
        typeC=""
        cu = curveData.splines.new(cType)
        cu.bezier_points.add(len(x)-1)
        #cu.bezier_points.foreach_set("co",coords)


        #coord0=x[0].atms[(x[0].atms.Cpos())-1].xyz()
        #coord1=x[0].atms[(x[0].atms.Cpos())].xyz()
        #need to check the type of x :atom list or coord list
 
        coord1=self.FromVec(x[0])
        coord2=self.FromVec(x[1])    
    
        coord0=coord1-(coord2-coord1)
    
#        if typeC == "tBezier" : 
#            cu.appendNurb(self.bezFromVecs(Vector(coord0[0],coord0[1],coord0[2]),
#                                           Vector(coord1[0],coord1[1],coord1[2]))) 
#                                           # We must add with a point to start with
#        elif typeC == "sBezier" : 
#            cu.appendNurb(self.bez2FromVecs(Vector(coord1[0],coord1[1],coord1[2])))
#        else : 
#        vecs0,vecs1,vecs = self.bezFromVecs1(self.FromVec(coord0),
#                                            self.FromVec(coord1),
#                                            self.FromVec(coord2))
#                                            # We must add with a point to start with
        vecs0,vecs1,vecs = self.bez2FromVecs(coord1)
        self.setBezierPoint(cu.bezier_points[0],vecs0,vecs1,vecs)
        
#        cu_nurb= cu[0] # Get the first curve just added in the CurveData
                   
                   
        i= 1 # skip first vec triple because it was used to init the curve
        while i<(len(x)-1):
            coord0=x[i-1]#atms[(x[i].atms.Cpos())-1].xyz()
            coord1=x[i]#atms[(x[i].atms.Cpos())].xyz()
            coord2=x[i+1]
            bt_vec_tripleAv= self.FromVec(coord0)
            bt_vec_triple  = self.FromVec(coord1)
            bt_vec_tripleAp= self.FromVec(coord2)
            vecs0,vecs1,vecs = self.bezFromVecs(bt_vec_tripleAv,bt_vec_triple)
            vecs0,vecs1,vecs = self.bezFromVecs1(bt_vec_tripleAv,bt_vec_triple,bt_vec_tripleAp)
#            if typeC == "tBezier" : cu_nurb.append(bt)
#            elif typeC == "sBezier" : cu_nurb.append(self.bez2FromVecs(Vector(coord1[0],coord1[1],coord1[2])))
#            else : 
            self.setBezierPoint(cu.bezier_points[i],vecs0,vecs1,vecs)
            i+=1              
            
        coord0=self.FromVec(x[len(x)-2])
        coord1=self.FromVec(x[len(x)-1])       
        coord2=coord1+(coord1-coord0)
    
#        if typeC == "tBezier" : cu_nurb.append(self.bezFromVecs(Vector(coord0[0],coord0[1],coord0[2]),Vector(coord1[0],coord1[1],coord1[2]))) # We must add with a point to start with
#        elif typeC == "sBezier" : cu_nurb.append(self.bez2FromVecs(Vector(coord1[0],coord1[1],coord1[2])))
#        else : 
        vecs0,vecs1,vecs = self.bez2FromVecs(coord1)
        #self.setBezierPoint(cu.bezier_points[-1],vecs0,vecs1,vecs)
        self.setBezierPoint(cu.bezier_points[-1],vecs0,vecs1,vecs)
        #else : cu_nurb.append(bezFromVecs1(Vector(coord0[0],coord0[1],coord0[2]),Vector(coord1[0],coord1[1],coord1[2]),Vector(coord2[0],coord2[1],coord2[2]))) # We must add with a point to start with
                    
        return cu
#        
##    def makeRuban(x,str_type,r,name,scene):
##        #rename by Extrude and give a spline
##        #the bezierCurve"tBezier"
##        cu=self.bezList2Curve(x,str_type)
##        #the circle
##        if name == "Circle" : ob1 = scene.objects.new(bezCircle(r,name))
##        if name == "Square" : ob1 = scene.objects.new(bezSquare(r,name))
##        #extrude
##        cu.setBevOb(ob1)
##        cu.setFlag(1)
##        #make the object
##        ob = scene.objects.new(cu)
##        return ob
##        
#    def update_spline(self,name,coords):
#        pass
#

    def setBezierPoint(self,point,vec1,vec2,vec3):
        #["FREE", "AUTO", "VECTOR", "ALIGNED"]
        point.co = vec2
        if vec1 is not None :
            point.handle_left = vec1
            point.handle_left_type= "AUTO"
        else :
            point.handle_left = vec2
        if vec3 is not None :
            point.handle_right= vec3
            point.handle_right_type= "AUTO"
        else :
            point.handle_right = vec2

    def addBezierPoint(self,prop,newCo):
        pass

    def addCurvePoint(self,prop,newCo):
        pass

    def setCoordinate(self,prop,newCo):
        prop.co = self.ToVec(newCo)

    def build_2dshape(self,name,type="circle",**kw):
        shapedic = {"circle":{"obj":bpy.ops.curve.primitive_bezier_circle_add,"size":["r",]},
#                    "rectangle":{"obj":self.bezSquare,"size":["r",]}
                    }
        dopts = [1.,1.]
        if "opts" in kw :
            dopts = kw["opts"]
        if len(shapedic[type]["size"]) == 1 :
            pass
#            shape[shapedic[type]["size"][0]] = dopts[0]
        else :
            for i in range(len(shapedic[type]["size"])) :
                pass
#                shape[shapedic[type]["size"][i]] = dopts[i]
        res = shapedic[type]["obj"]()
        shape = bpy.context.object
        shape.name = name
        #whats the current unit?
        shape.scale *= bpy.context.scene.unit_settings.scale_length
        shape.scale *= dopts[0]
#        [bpy.context.scene.unit_settings.scale_length,
#                       bpy.context.scene.unit_settings.scale_length,
#                       bpy.context.scene.unit_settings.scale_length]
        return shape,None
        
    def extrudeSpline(self,spline,**kw):
        extruder = None
        shape = None
        spline_clone = None
        curveData = spline.data
        if "shape" in kw:
            if type(kw["shape"]) == str :
                shape = self.build_2dshape("sh_"+kw["shape"]+"_"+str(spline),
                                           kw["shape"])[0]
            else :
                shape = kw["shape"]        
        if shape is None :
            shape = self.build_2dshape("sh_circle"+str(spline))[0]
      
        if "clone" in kw and kw["clone"] :
            bpy.ops.object.select_all(action='DESELECT')
            bpy.ops.object.select_pattern(pattern=spline.name)
            bpy.context.scene.objects.active = spline
            bpy.ops.object.duplicate_move()
            spline_clone = bpy.context.scene.objects.active#bpy.context.object
            spline_clone.name = "exd"+spline.name
            curveData = spline_clone.data
            curveData.bevel_object = shape
            return spline_clone,shape,spline_clone
        curveData.bevel_object = shape
        return spline,shape

    def spline(self,name,coords,type="",extrude_obj=None,scene=None,parent=None,**kw):
        lType = ["POLY", "BEZIER", "BSPLINE", "CARDINAL", "NURBS"]
        cType = "BEZIER"
        nbPts = len(coords)
        if scene is None :
            scene = self.getCurrentScene()
        faces=numpy.array([range(0,nbPts-1),range(1,nbPts)]).transpose().tolist()
        poly,mesh = self.createsNmesh(name,coords,None,faces) 
        self.setCurrentSelections([poly,])
        #convertToCurve:1   
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.delete(type='ONLY_FACE')
        bpy.ops.object.mode_set()
        bpy.ops.object.convert(target='CURVE')
        for sp in bpy.context.object.data.splines:sp.type =lType[4]#POLY,NURBS,BEZIER
        obj = bpy.context.object
        # Set spline type to custom property in panel
        bpy.ops.object.editmode_toggle()
        bpy.ops.curve.spline_type_set(type=lType[4]) 
        # Set handle type to custom property in panel
        bpy.ops.curve.handle_type_set(type="AUTOMATIC") #ALIGNED,AUTOMATIC,FREE_ALIGN,VECTOR
        bpy.ops.object.editmode_toggle()
        obj.data.fill_mode = 'FULL'
        # Set resolution to custom property in panel
        obj.data.bevel_resolution = 4 #curve_resolution
        obj.data.resolution_u = 12 #curve_u
        # Set depth to custom property in panel
        obj.data.bevel_depth = 0.1#Btrace.curve_depth 
        # Smooth object
        bpy.ops.object.shade_smooth()
        # Modulate curve radius and add distortion
#        if Btrace.distort_curve: 
#            scale = Btrace.distort_modscale
#            if scale == 0:
#                return {'FINISHED'}
#            for u in obj.data.splines:
#                for v in u.bezier_points:
#                    v.radius = scale*round(random.random(),3) 
        return poly,poly        
        
    def spline_bezier(self,name,coords,type="",extrude_obj=None,scene=None,parent=None,**kw):
        #Type : "sBezier", "tBezier" or ""
        lType = ["POLY", "BEZIER", "BSPLINE", "CARDINAL", "NURBS"]
        cType = "BEZIER"
        nbPts = len(coords)
        if scene is None :
            scene = self.getCurrentScene()
        res = bpy.ops.object.add(type="CURVE")
        curveObj = bpy.context.object
        curveObj.name = name
        curveData = curveObj.data
        curveData.name = name
        curveData.dimensions="3D"
        if cType == "BEZIER" :
            spline = self.bezList2Curve(coords,curveData,cType)
        
#        cu=self.bezList2Curve(coords,type)
#        cu.name = name
        if extrude_obj is not None :
            curveData.bevel_object = extrude_obj
#            cu.setBevOb(extrude_obj)
#        cu.setFlag(1)
#        ob = scene.objects.new(cu)
        if parent is not None :
            oparent = self.getObject(parent)
            curveObj.parent = oparent
        return curveObj,curveData
#
#    def getBoneMatrix(self,bone,arm_mat=None):
#        bone_mat= bone.matrix['ARMATURESPACE']
#        if arm_mat is not None :
#            bone_mat= bone_mat*arm_mat
#        return bone_mat
#
    def addBone(self,i,armData,headCoord,tailCoord,
                roll=10,hR=0.5,tR=0.5,dDist=0.4,boneParent=None,
                name=None,editMode=True):
        #armData.makeEditable()
        if not editMode :
            bpy.ops.object.mode_set(mode='EDIT')
        if name is None :
            name = "bone"+str(i)
        eb = armData.edit_bones.new(name)
        if name is not None :
            eb.name = name
        eb.roll = roll
        eb.head = mathutils.Vector((headCoord[0],headCoord[1],headCoord[2]))
        eb.tail = mathutils.Vector((tailCoord[0],tailCoord[1],tailCoord[2]))
        eb.head_radius=hR
        eb.tail_radius=tR
        eb.envelope_distance=dDist
        eb.use_connect = True
        #if ( (i % 2) == 1 ) : eb.options = [Armature.HINGE, Armature.CONNECTED]
        #if ( (i % 2) == 0 ) : eb.options = [Armature.HINGE, Armature.CONNECTED,Armature.NO_DEFORM]
#        bpy.ops.object.mode_set(mode='OBJECT')
        if boneParent is not None :
#            eb.options = [Armature.HINGE, Armature.CONNECTED]
            eb.parent = boneParent
            eb.use_connect = False
        elif i != 0 and len(armData.edit_bones):
#            eb.options = [Armature.HINGE, Armature.CONNECTED]
            eb.parent = list(armData.edit_bones.items())[i-1][1] #0 is the name 1 is the bone
            eb.use_connect = True
        #armData.bones['bone'+str(i)] = eb
#        bpy.ops.object.mode_set(mode='EDIT')
        if not editMode :
            bpy.ops.object.mode_set(mode='OBJECT')
        return eb
        
    def armature(self,name,x,hR=0.5,tR=0.5,dDist=0.4,roll=10,scn=None,root=None,
                 listeName=None):
        if scn is None:
            scn = self.getCurrentScene()
        res = bpy.ops.object.add(type='ARMATURE',location=(0.0, 0.0, 0.0))
        armObj = bpy.context.object
        armObj.name = name
        armObj.show_x_ray = True
        armData = armObj.data
        armData.name = name
        armData.use_auto_ik=bool(1)
        armData.use_deform_vertex_groups=bool(1)
        bpy.ops.object.mode_set(mode='EDIT')
        if listeName is not None :
            bones = [self.addBone(i,armData,x[i],x[i+1],
                    hR=hR,tR=tR,dDist=dDist,roll=roll,name=listeName[i]) for i in range(len(x)-1)]
        else :
            bones = [self.addBone(i,armData,x[i],x[i+1],
                    hR=hR,tR=tR,dDist=dDist,roll=roll) for i in range(len(x)-1)]
        bpy.ops.object.mode_set(mode='OBJECT')
        #for bone in armData.bones.values():
        #   #print bone.matrix['ARMATURESPACE']
        #   print bone.parent, bone.name
        #   print bone.options, bone.name
#        armData.update()
#        self.addObjectToScene(scn,armObj,parent=root)
        #scn.objects.link(armObj)
        return armObj,bones
    
#    def add_armature(self,armObj,obj):
#         mods = obj.modifiers
#         mod=mods.append(Modifier.Types.ARMATURE)
#         mod[Modifier.Settings.OBJECT] = armObj
#         obj.addVertexGroupsFromArmature(armObj)
#        
#    def bindGeom2Bones(self,listeObject,bones):
#        """
#        Make a skinning. Namely bind the given bones to the given list of geometry.
#        This function will joins the list of geomtry in one geometry
#        
#        @type  listeObjects: list
#        @param listeObjects: list of object to joins
#        @type  bones: list
#        @param bones: list of joins
#        """    
#        #the joins dont work using non interactive mode
#        if len(listeObject) >1:
#            self.JoinsObjects(listeObject)
#        else :
#            self.ObjectsSelection(listeObject,"new")
#        #2- add the joins to the selection
#        self.ObjectsSelection(bones,"add")
#        #3- bind the bones / geoms
#        #put the code to bind here
#    #    add_armature(armObj,obj)
#
    def oneMetaBall(self,metab,rad,coord):
        #add one ball
        me=metab.elements.new()
        me.radius=float(rad) *3. # 
        me.co = (coord[0], coord[1], coord[2])  
    
    def metaballs(self,name,listePt,listeR,scn=None,root=None,**kw):
        if scn == None:
            scn = self.getCurrentScene()
        res = bpy.ops.object.add(type='META',location=(0.0, 0.0, 0.0))
        objm = bpy.context.object
        objm.name = name
        metab = objm.data
        metab.name = name
        metab.resolution = 1.0
        metab.update_method = "HALFRES"
        if listeR is None :
            listeR = [1.]*len(listePt)
        [self.oneMetaBall(metab,listeR[x],listePt[x]) for x in range(len(listePt))]
        if root is not None :
            objm.parent = root
        return objm,metab
#
#
    def constraintLookAt(self,object):
        """
        Cosntraint an hostobject to llok at the camera
        
        @type  object: Hostobject
        @param object: object to constraint
        """
        object=self.getObject(object)
        
#
    def updateText(self,text,string="",parent=None,size=None,pos=None,font=None):
        pass
##        print text , string
#        if type(text) == list or type(text) == tuple:
#            txt,otxt =text
#        else :
#            txt = text  
#            otxt = None          
#        if string : 
#            txt.setText(string)
#        if size is not None :  
#            txt.setSize(size)
#        if pos is not None : 
#            self.setTranslation(otxt,pos)
#        if parent is not None : 
#            self.reParent(otxt,parent)
#        otxt.makeDisplayList()
#
    def Text(self,name="",string="",parent=None,size=5.,pos=None,font='Courier',
             lookAt=False,**kw):
        return_extruder = False
        if pos is None :
            pos = [0.,0.,0.]
        pos[0] = pos[0]-6.0#not center
        res = bpy.ops.object.text_add(location = (float(pos[0]),float(pos[1]),float(pos[2])))
        obj = bpy.context.object
        obj.name = name
        mesh = obj.data
        mesh.name = "mesh_"+name
        mesh.size = size
        if parent is not None:
            obj.parent = parent
        #toggle to edit mode
        self.toggleEditMode()
        #should remove the default text
        bpy.ops.font.delete()
        bpy.ops.font.text_insert(text=string)
        self.restoreEditMode()
        if lookAt:
            self.constraintLookAt(name)
        if "extrude" in kw :
            extruder = None
            #create an extruder
            if type(kw["extrude"]) is bool and kw["extrude"]:
#                extruder = c4d.BaseObject(self.EXTRUDER)
#                self.addObjectToScene(self.getCurrentScene(),extruder,parent=parent)
                return_extruder = True
            else :
                extruder = kw["extrude"]
#            if extruder is not None :
#                extruder[c4d.EXTRUDEOBJECT_MOVE] = self.FromVec([0.5,0.,0.]) # if x 180.0
#                extruder[c4d.EXTRUDEOBJECT_HIERARCHIC] = 1
#                parent = extruder       
        if return_extruder :
            return obj,extruder
        else :
            return obj

    def getBoxSize(self,name):
        box=self.getObject(name)
        return box.dimensions

    def box(self,name,center=[0.,0.,0.],size=[1.,1.,1.],cornerPoints=None,visible=1,
                              mat =None,**kw):
                                  
        res = bpy.ops.mesh.primitive_cube_add()
        obj = bpy.context.object
        obj.name = name
        mesh = obj.data
        mesh.name = "m_"+name   
        #self.addMaterial(name,[1.,1.,0.])

        if cornerPoints != None :
            for i in range(3):
                size[i] = cornerPoints[1][i]-cornerPoints[0][i]
            center=(self.FromVec(cornerPoints[0])+self.FromVec(cornerPoints[1]))/2.
        obj.location = (float(center[0]),float(center[1]),float(center[2]))
        obj.dimensions = (float(size[0]),float(size[1]),float(size[2]))
        parent= None
        if "parent" in kw :
            parent = kw["parent"]
        if mat is not None :
            self.assignMaterial(obj,mat)                
        else :
            self.addMaterial(name+"mat",[1.,1.,0.])        
        self.addObjectToScene(self.getCurrentScene(),obj,parent=parent)        
        return obj,mesh

    def updateBox(self,box,center=[0.,0.,0.],size=[1.,1.,1.],cornerPoints=None,visible=1,
                              mat = None):
        box=self.getObject(box)
        if cornerPoints != None :
            for i in range(3):
                size[i] = cornerPoints[1][i]-cornerPoints[0][i]
            for i in range(3):
                center[i]=(cornerPoints[0][i]+cornerPoints[1][i])/2.
        box.location = (float(center[0]),float(center[1]),float(center[2]))
        box.dimensions = (float(size[0]),float(size[1]),float(size[2]))
        
    def plane(self,name,center=[0.,0.,0.],size=[1.,1.],cornerPoints=None,visible=1,**kw):
        #plane or grid
        xres = 2
        yres = 2
        if "subdivision" in kw :
            xres = kw["subdivision"][0]
            yres = kw["subdivision"][1]
            if xres == 1 : xres = 2                      
            if yres == 1 : yres = 2
        res = bpy.ops.mesh.primitive_grid_add(x_subdivisions=xres,
                                              y_subdivisions=yres,
                                              size=1.0)
        obj = bpy.context.object
        obj.name = name
        mesh = obj.data
        mesh.name = "m_"+name   

        if cornerPoints != None :
            for i in range(3):
                size[i] = cornerPoints[1][i]-cornerPoints[0][i]
            center=(self.FromVec(cornerPoints[0])+self.FromVec(cornerPoints[1]))/2.
        obj.location = (float(center[0]),float(center[1]),float(center[2]))
        obj.dimensions = (float(size[0])*0.5,float(size[1])*0.5,1.0)
        
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
            obj.parent = parent
#        self.addObjectToScene(self.getCurrentScene(),obj)
        return obj,mesh
    
    def Sphere(self,name,res=16,radius=1.0,pos=None,color=None,mat=None,parent=None):
         #res = bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=res, size=radius)
        res = bpy.ops.mesh.primitive_uv_sphere_add(segments=res, ring_count=res, size=radius) 
#        print (res)
        obj = bpy.context.object
        obj.name = name
        mesh = obj.data
        mesh.name = "mesh_"+name
        #smooth ?
        bpy.ops.object.shade_smooth()
#        print ("smooth")
        if mat is not None :
            mat = self.getMaterial(mat)
        else :
            if color == None :
                color = [1.,1.,0.]
            mat = self.addMaterial(name,color)
        self.setOneMaterial(obj,mat)
#        print (mat)
        if pos == None : pos = [0.,0.,0.]
        obj.location = (float(pos[0]),float(pos[1]),float(pos[2]))
#        print (pos)
        if parent is not None:
            obj.parent = parent
#        print (obj.parent)
        return obj,mesh

    def Cone(self,name,radius=1.,length=1.,res=9, pos = [0.,0.,0.],parent=None):
        res = bpy.ops.mesh.primitive_cone_add(vertices=res, radius=radius, 
                                depth=length,
                                location = (float(pos[0]),float(pos[1]),float(pos[2]))) 
        obj = bpy.context.object
        obj.name = name
        mesh = obj.data
        mesh.name = "mesh_"+name
        if parent is not None:
            obj.parent = parent        
        return obj,mesh

    def Cylinder(self,name,radius=1.,length=1.,res=16,pos = None,parent = None,**kw):
        #import numpy
#        diameter = radius#2*radius??
        res = bpy.ops.mesh.primitive_cylinder_add(vertices=res, radius=radius, 
                        depth=length, cap_ends=True)
        obj = bpy.context.object
        obj.name = name
        mesh = obj.data
        mesh.name = "mesh_"+name

        if pos != None : obj.location = (float(pos[0]),float(pos[1]),float(pos[2]))
        if parent is not None:
            obj.parent = self.getObject(parent)
        return obj,mesh
#    
#    """
#    def createMeshSphere(self,**kwargs):
#            # default the values
#            radius = kwargs.get('radius',1.0)
#            diameter = radius *2.0
#            segments = kwargs.get('segments',8)
#            rings = kwargs.get('rings',8)
#            loc   = kwargs.get('location',[0,0,0])
#            useIco = kwargs.get('useIco',False)
#            useUV = kwargs.get('useUV',True)
#            subdivisions = kwargs.get('subdivisions',2)
#            if useIco:
#                sphere = Blender.Mesh.Primitives.Icosphere(subdivisions,diameter)
#            else:    
#                sphere = Blender.Mesh.Primitives.UVsphere(segments,rings,diameter)
#            #ob = self.scene.objects.new(item,name)    
#            #ob.setLocation(loc)
#            return sphere
#    """
#        
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
        
    def updateTubeMesh(self,mesh,basemesh=None,verts=None,faces=None,cradius=1.0,quality=1.):
        if verts is None :
            if basemesh is not None :
                baseobj = self.getObjectFromMesh(basemesh)
#                print (baseobj,basemesh)
                bpy.context.scene.objects.active = baseobj
                verts = self.getMeshVertices(baseobj.data)
                faces = self.getMeshFaces(baseobj.data)
            else :
                print("error need verts or basemesh")
                return
        obj = self.getObjectFromMesh(mesh)
        if obj is not None:
#            mesh.verts = verts[:]
#            mesh.faces = faces[:]
#            mats=obj.data.materials
            self.updateMesh(obj,vertices=verts,faces=faces)
            if  cradius != 1. :
                #new scale
#                cradius = cradius*2.0
                Smatrix=mathutils.Matrix.Scale(cradius, 4)
                Smatrix[2][2] = 1.
                obj.data.transform(Smatrix)
#                obj.data.materials = mats
                #update
                obj.data.update()
                #print "done"
                
    def updateTubeObj(self,o,coord1,coord2):
        laenge,wsz,wz,coord=self.getTubeProperties(coord1,coord2)
        o.scale[2] = laenge
        self.setTranslationObj(o,coord)
        #o.setLocation(coord[0],coord[1],coord[2])
        o.rotation_euler[2] = wz
        o.rotation_euler[2] = wsz
#    
#    def instancesCylinder(self,name,points,faces,radii,mesh,colors,scene,parent=None):
#        cyls=[]
#        mat = None
#        if len(colors) == 1:
#            mat = self.addMaterial('mat_'+name,colors[0])
#        for i in range(len(faces)):
#            laenge,wsz,wz,coord=self.getTubeProperties(points[faces[i][0]],points[faces[i][1]])     
#            cname=name+str(i)
#            mesh=Mesh.Get("mesh_"+mesh.getName().split("_")[1])    #"mesh_"+name
#            if mat == None : mat = self.addMaterial("matcyl"+str(i),colors[i])
#            me.materials=[mat]
#            obj=Object.New('Mesh',spname)
#            obj.link(mesh)
#            #obj=scene.objects.new(mesh,cname)
#            obj.setLocation(float(coord[0]),float(coord[1]),float(coord[2]))
#            obj.RotY = wz
#            obj.RotZ = wsz
#            obj.setSize(float(radii[i]),float(radii[i]),float(laenge))
#            cyls.append(obj)
#        self.AddObject(cyls,parent=parent)
#        return cyls
#    
    def oneCylinder(self,name,head,tail,radius=None,instance=None,material=None,
                    parent = None,color=None,**kw):
        laenge,wsz,wz,coord=self.getTubeProperties(head,tail)
        if instance == None : 
            obj = self.Cylinder(name,parent=parent,pos=coord)[0]
        else : 
            obj=self.newInstance(name,instance,parent=parent)
            self.translateObj(obj,coord)
        obj.rotation_euler[1] = wz
        obj.rotation_euler[2] = wsz
        if radius is None :
            radius = 1.0
        self.scaleObj(obj,[radius,radius,float(laenge)])
        #obj.setSize(1.,1.,float(laenge))

        if material != None :
            mat = self.getMaterial(material)  
            self.setOneMaterial(obj,mat,objmode=True)
        elif color is not None :
            mats = self.getMaterialObject(obj)
            if not mats :
                mat = self.addMaterial("mat_"+name,color)
                self.setOneMaterial(obj,mat,objmode=True)
            else :
                self.colorMaterial(mats[0],color)            
        return obj

    def updateOneCylinder(self,name,head,tail,radius=None,material=None,color=None):
        laenge,wsz,wz,coord=self.getTubeProperties(head,tail)
        obj = self.getObject(name)
        self.setTranslationObj(obj,coord)
        if radius is None :
            radius= 1.0        
        obj.rotation_euler[1] = wz
        obj.rotation_euler[2] = wsz
        self.scaleObj(obj,[radius,radius,float(laenge)])
        if material != None :
            mat = self.getMaterial(material)
            self.setOneMaterial(obj,mat,objmode=True)
        elif color is not None :
            mats = self.getMaterialObject(obj)
            if not mats :
                mat = self.addMaterial("mat_"+name,color)
                self.setOneMaterial(obj,mat,objmode=True)
            else :
                self.colorMaterial(mats[0],color)  
        return obj
        
    def updateSphereMesh(self,mesh,verts=None,faces=None,basemesh=None,
                         scale=None,typ=None,**kw):

        
        
#        obj.data.user_clear()
#        bpy.data.meshes.remove(obj.data)
#        obj.data = baseobj.data.copy()
#        obj.data.update()

        if verts is None :
            if basemesh is not None :
                baseobj = self.getObjectFromMesh(basemesh)
                print ("updateSphereMesh",baseobj,basemesh)
                bpy.context.scene.objects.active = baseobj
                verts = self.getMeshVertices(baseobj.data)
                faces = self.getMeshFaces(baseobj.data)
            else :
                print("error need verts or basemesh")
                return
        #compute the scale transformation matrix
        obj = self.getObjectFromMesh(mesh)
        if obj is not None:
#            mesh.verts = verts[:]
#            mesh.faces = faces[:]
            self.updateMesh(obj,vertices=verts,faces=faces)
            if  scale != None :
#                print ("scale ??",scale)
                factor=float(scale)
#                #verify the *2 ?
                #Scale(factor, size, axis)
                Smatrix=mathutils.Matrix.Scale(factor, 4)
                obj.data.transform(Smatrix)
                obj.data.update()
#        
    def updateSphereObj(self,o,c):
        if type(o) == str or type(o) == unicode :
            o = self.getObject(o)
        o.location = (float(c[0]),float(c[1]),float(c[2]))

    
    def instancesSphere(self,name,centers,radii,meshsphere,colors,scene,parent=None):
        sphs=[]
        #k=0
        rad=1
        mat = None
        #if len(colors) == 1:
        #    mat = self.addMaterial('mat_'+name,colors[0])
        for j in range(len(centers)):
            spname = name+str(j)
            atC=centers[j]
            #meshsphere is the object which is link to the mesh
            mesh=meshsphere.data#Mesh.Get("mesh_"+meshsphere.getName().split("_")[1])   
            OBJ=bpy.data.objects.new(spname,mesh)
            #"mesh_"+name     OR use shareFrom    
            #mesh=Mesh.Get(mesh)
            #OBJ=Object.New('Mesh',spname)
            #OBJ.link(mesh)
            #OBJ=scene.objects.new(mesh,spname)
            OBJ.location=(float(atC[0]),float(atC[1]),float(atC[2]))
            if len(radii) == 1 :
                rad = radii[0]
            elif j >= len(radii) :
                rad = radii[0]
            else :
                rad = radii[j]            
            OBJ.scale=(float(rad),float(rad),float(rad))
            #OBJ=Object.New('Mesh',"S_"+fullname)   
#            if mat == None : mat = self.addMaterial("matsp"+str(j),colors[j])
#            OBJ.setMaterials([mat])
#            OBJ.colbits = 1<<0
            sphs.append(OBJ)
        self.AddObject(sphs,parent=parent)
        return sphs

    def updateInstancesSphere(self,name,sphs,centers,radii,meshsphere,
                        colors,scene,parent=None,delete=True,**kw):
        mat = None
#        if len(colors) == 1:
#            mat = self.retrieveColorMat(colors[0])
#            if mat == None and colors[0] is not None:        
#                mat = self.addMaterial('mat_'+name,colors[0])
        delete = True
        if "delete" in kw :
            delete = kw["delete"]
        for i in range(len(centers)):
            if len(radii) == 1 :
                rad = radii[0]
            elif i >= len(radii) :
                rad = radii[0]
            else :
                rad = radii[i]            
            if i < len(sphs):
                sphs[i].location=(float(centers[i][0]),float(centers[i][1]),float(centers[i][2]))
                sphs[i].scale=(float(rad),float(rad),float(rad))
#                if mat == None : 
#                    if colors is not None and i < len(colors) and colors[i] is not None : 
#                        mat = self.addMaterial("matsp"+str(i),colors[i])
#                if colors is not None and i < len(colors) and colors[i] is not None : 
#                    self.colorMaterial(mat,colors[i])
                #texture[1010] = mat
                self.toggleDisplay(sphs[i],True)
            else :
                sphs.append(bpy.data.objects.new(name+str(i),meshsphere.data))
                sphs[i].location=(float(centers[i][0]),float(centers[i][1]),float(centers[i][2]))
                sphs[i].scale=(float(rad),float(rad),float(rad))
#                if mat == None :
#                    if colors is not None and  i < len(colors) and colors[i] is not None : 
#                        mat = self.addMaterial("matsp"+str(i),colors[i])
#                sphs[i].setMaterials([mat])
                self.addObjectToScene(scene,sphs[i],parent=parent)
        if len(centers) < len(sphs) and delete :
            #delete the other ones ?
            for i in range(len(centers),len(sphs)):
                if delete : 
                    obj = sphs.pop(i)
                    self.deleteObject(obj)
                else :
                    self.toggleDisplay(sphs[i],False)
        return sphs
        
#    def clonesAtomsSphere(self,name,iMe,x,scn,armObj,scale,Res=32,R=None,join=0):
#        pass
#         
#    def duplicateIndices(self,indices,n):
#        newindices = [ (i[0],i[1],i[1]+n,i[0]+n) for i in indices ]
#        return newindices
#    
#    def duplicateCoords(self,coords):
#        newcoords = [(x[0],x[1],x[2]-0.1) for x in coords]
#        return newcoords
#    
    def PointCloudObject(self,name,**kw):
        #print "cloud", len(coords)
        coords=kw['vertices']
        faces = []
        if 'faces' in kw:
            if kw['faces']:
                faces = [(x,x+1,x+2) for x in range(1,len(me.verts)-3) ]
        
        res = bpy.ops.object.add(type='MESH')
        obj = bpy.context.object
        obj.name = name+"ds"
        me = obj.data
        me.name = name
        me.from_pydata(coords, [], faces)
        me.update()
        me.calc_normals()
       
        if 'parent' in kw and kw['parent'] is not None: 
            parent = self.getObject(kw['parent'])
            obj.parent = parent
        return obj,me

    def matrixToEdgeMesh(self,name,matrices,**kw):#edge size ?
        #blender user verex normal for rotated the instance
        pt1=[0.,0.,0.]
        pt2=[0.,10.,0.]#normale
        v=[]
        f=[]
        e=[]
        i=0
        for m in matrices:
            p1,p2=self.ApplyMatrix([pt1,pt2],matrices)
            v.extend([p1,p2])
            e.append([i,i+1])
            i+=2        
        res = bpy.ops.object.add(type='MESH')
        obj = bpy.context.object
        obj.name = name+"ds"
        me = obj.data
        me.name = name
        me.from_pydata(v, e, f)
        me.update()
        me.calc_normals()       
        if 'parent' in kw and kw['parent'] is not None: 
            parent = self.getObject(kw['parent'])
            obj.parent = parent
        return obj,me

    def matrixToVNMesh(self,name,matrices,vector=[0.,1.,0.],transpose=True,**kw):#edge size ?
        #blender user verex normal for rotated the instance
        pt1=[0.,0.,0.]#pos
        pt2=vector#[0.,1.,0.]#normal should be given ?
        v=[]
        f=[]
        e=[]
        n=[]        
#        i=0
#       why -90 ?
        vi=0
        for m in matrices:
#            p1=m[:3, 3]
#            m[:3, 3]=[0.,0.,0.]
            #p1,p2=self.ApplyMatrix([pt1,pt2],m)
            if transpose :
                m =self.transposeMatrix(m)
            p1=self.ApplyMatrix([pt1],m)[0]            
            mr=m[:]
            mr[:3,:3]=[0.,0.,0.]
            p2=self.ApplyMatrix([pt2],mr)[0]            
            v.append(p1)
            n.append(p2)#should only get the rotation part of the  matrix
#            v.extend([p1,p2*2.0])
#            f.append([vi,vi+1,vi+1,vi])
#            e.append([vi,vi+1])
            vi+=2
#            i+=2        
        res = bpy.ops.object.add(type='MESH')
        obj = bpy.context.object
        obj.name = name+"ds"
        me = obj.data
        me.name = name
#        print (v[0],len(v),type(v),type(v[0]))
        me.from_pydata(v, [], [])
        points = me.vertices
        me.update()
        me.calc_normals()
        for i,v in enumerate(points) :
            v.normal = self.FromVec(n[i])
        if 'parent' in kw and kw['parent'] is not None: 
            parent = self.getObject(kw['parent'])
            obj.parent = parent
        return obj,me

    def matrixToFacesMesh(self,name,matrices,vector=[0.,1.,0.],transpose=True,**kw):#edge size ?
        #blender user verex normal for rotated the instance
        #quad up vector should use the inpu vector
        axe=self.rerieveAxis(vector)
        #axe="+Y"??
        #so far I did +X and +Y
        #need all the other
        eq={"+X":"+Z",
            "+Y":"+X",
            "+Z":"+Z",
            "-X":"+Z",
            "-Y":"-X",
            "-Z":"+Z"}
        quad=numpy.array(self.quad[eq[axe]])#*50.0
#        mX=self.rotation_matrix(-math.pi/2.0,eq[axe])#why that ?
#        quad=self.ApplyMatrix(quad,mX)
        print ("matrixToFacesMesh",axe,vector,quad,eq[axe])
#        f=[0,1,2,3]
        v=[]
        f=[]
        e=[]
        n=[]        
        vi=0
        for i,m in enumerate(matrices):
            if transpose :
                m =self.transposeMatrix(m)
            new_quad=self.ApplyMatrix(quad,m)            
            v.extend(new_quad)
            f.append([i*4+0,i*4+1,i*4+2,i*4+3])
        res = bpy.ops.object.add(type='MESH')
        obj = bpy.context.object
        obj.name = name+"ds"
        me = obj.data
        me.name = name
        me.from_pydata(v, [], f)
#        points = me.vertices
        me.update()
#        me.calc_normals()
#        for i,v in enumerate(points) :
#            v.normal = self.FromVec(n[i])
        if 'parent' in kw and kw['parent'] is not None: 
            parent = self.getObject(kw['parent'])
            obj.parent = parent
        return obj,me
            
#    def updateCloudObject(self,name,coords):
#        #print "updateMesh ",geom,geom.mesh
#        #getDataFrom object or gerNRAW?
#        #mesh=NMesh.GetRaw(geom.mesh)
#        mesh=Mesh.Get(name)
#        #print mesh
#        #mesh=geom.mesh
#        #remove previous vertice and face
#        mats=mesh.materials
#        mesh.verts=None
#        mesh.faces.delete(1,list(range(len(mesh.faces))))
#        #add the new one
#        mesh.verts.extend(coords)            # add vertices to mesh
#        #set by default the smooth
#        mesh.materials=mats
#        mesh.update()
#
#    
    def polygons(self,name, proxyCol=False, smooth=True, color=None, dejavu=False,
                 material=None, **kw):
        vertices=None
        faces=[]
        doMaterial = True
        if 'vertices' in kw:
            if kw['vertices'] is not None:
                vertices = kw["vertices"]
        if 'faces' in kw:
            if kw['faces'] is not None:
                faces = kw["faces"]
                if type(faces) not in [list, tuple]:
                    faces = faces.tolist()
        if 'normals' in kw:
            if kw['normals'] is not None:
                normals = kw["normals"]
        frontPolyMode = 'fill'
        if "frontPolyMode" in kw : 
            frontPolyMode = kw["frontPolyMode"]
        shading = 'flat'
        if "shading" in kw : 
            shading=kw["shading"]#'flat'
        #vlist = []
        polygon=bpy.data.meshes.new(name)

        if kw['vertices'] is not None: 
            vertices = vertices#kw['vertices']        # add vertices to mesh
        if kw['faces'] is not None: 
            faces = faces     # add faces to the mesh (also adds edges)
        # if faces length is <= 2 need to add a 0
        if faces and len(faces[0]) == 2 :
            newF = [(f[0],f[1],f[1]) for f in faces]
            faces = newF
        # Make a mesh from a list of verts/edges/faces.
        polygon.from_pydata(vertices, [], faces)
        # Update mesh geometry after adding stuff.
        polygon.update()

        #smooth face : the vertex normals are averaged to make this face look smooth
        polygon.calc_normals()
#        if smooth:
#            if kw['faces'] is not None: 
#                for face in polygon.faces:
#                    face.smooth=1
#        if type(material) is bool :
#            doMaterial = material        
#        if doMaterial:
#            if material is None :
#                mat = self.addMaterial("mat"+name[:4],(1.,0.,0.))
#            else :
#                mat = self.getMaterial(material)
#                self.setOneMaterial(o,mat)
#            polygon.materials=[mat]
#        if color != None :
#            self.changeColor(polygon,color)
#        if frontPolyMode == "line" :
#            #drawtype,and mat ->wire
#            mat.setMode("Wire")    
        if dejavu :
            obpolygon = bpy.data.objects.new(name,polygon)
    #        obpolygon.draw_type = 'SMOOTH'
            obpolygon.select = True
    #        bpy.ops.object.mode_set(mode='OBJECT')        
            #add the object to the scene...
          
#            obpolygon = Blender.Object.New("Mesh",name)
#            obpolygon.link(polygon)
#            if frontPolyMode == "line" :
#                obpolygon.setDrawType(2)
            return obpolygon
#        else :
        return polygon
    
    def createsNmesh(self, name, vertices, vnormals, faces, color=[1,0,0],
                            material= None, smooth=True, proxyCol=False, **kw):
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
        doMaterial = True
        polygon = self.polygons("M_"+name, vertices=vertices, normals=vnormals,
                                faces=faces, material=material, color=color,
                                smooth=smooth, proxyCol=proxyCol, **kw)
        
        obpolygon = bpy.data.objects.new(name, polygon)
#        obpolygon.draw_type = 'SMOOTH'
        obpolygon.select = True
#        bpy.ops.object.mode_set(mode='OBJECT')        
        #add the object to the scene...
        parent = None
        if "parent" in kw :
            parent = kw["parent"]
        
        self.addObjectToScene(self.getCurrentScene(), obpolygon, parent=parent)
        bpy.context.scene.objects.active = obpolygon
        if smooth:
            bpy.ops.object.shade_smooth()
        else:
            bpy.ops.object.shade_flat()
            
        if type(material) is bool :
            doMaterial = material        
        if doMaterial:
            if material is None or type(material) is bool :
                mat = self.addMaterial("mat_"+name,color)
            else :
                mat = self.getMaterial(material)
            self.setOneMaterial(obpolygon,mat)
            #polygon.materials=[mat]
#        if color != None :
#            self.changeColor(polygon,color)

        return obpolygon,polygon

    def updatePoly(self,obj,vertices=None,faces=None):
        if type(obj) is str:
            obj = self.getObject(obj)
        if obj is None : return
        mesh=self.getMeshFrom(obj)#Mesh.Get("Mesh_"+obj.name)
        self.updateMesh(mesh,vertices=vertices,faces=faces)
        self.updateObject(obj)

    def getLayers(self, scn):
        """
        Return a list of active layers of a scene or an object
        """
        if scn is None :
            return
        layers = [ind for ind in range(20) if scn.layers[ind]]
        return layers

    def setLayers(self, scn, layers):
        """
        Set the layers of a scene or an object, expects a list of integers
        """
        if scn is None :
            return
        chs = self.getChilds(scn)
        for ch in chs:
            self.setLayers(ch,layers)
        for ind in layers:
            scn.layers[ind] = True
        for unset in set(range(20)).difference(layers):
            scn.layers[unset] = False
        
        
    def updateFaces(self,mesh,faces):
        # eekadoodle prevention
        for i in range(len(faces)):
            if not faces[i][-1]:
                if faces[i][0] == faces[i][-1]:
                    faces[i] = [faces[i][1], faces[i][2], faces[i][3], faces[i][1]]
                else:
                    faces[i] = [faces[i][-1]] + faces[i][:-1]
        if len(mesh.faces) == len(faces):
            for i in range(len(faces)):
                mesh.faces[i].vertices_raw = faces[i]
        elif len(mesh.faces) < len(faces):
            start_faces = len(mesh.faces)
            mesh.faces.add(len(faces))
            for i in range(len(faces)):
                mesh.faces[i].vertices_raw = faces[i]
        else :
            end_faces = len(faces)
            #mesh.faces.add(len(faces))
            for i in range(len(faces)):
                mesh.faces[start_faces + i].vertices_raw = faces[i]
        mesh.update(calc_edges = True) # calc_edges prevents memory-corruption            
        
    def updateVerts(self,mesh,vertices):
        if len(mesh.vertices) == len(vertices):
            for i in range(len(vertices)):
                mesh.vertices[i].co = vertices[i]
        elif len(mesh.vertices) < len(vertices):
            start_index = len(mesh.vertices)
            mesh.vertices.add(len(vertices))
            for i in range(len(vertices)):
                mesh.vertices[i].co = vertices[i]
        else :
            end_index = len(vertices)
            mesh.vertices.remove(len(mesh.vertices)-len(vertices))
            for i in range(len(vertices)):
                mesh.vertices[start_index + i].co = vertices[i]


    def updateMesh(self, mesh, vertices=None,faces=None, smooth=True,**kw):
        # must delete the mesh data first or add vert/face
        # Delete all geometry from the object.
        # Select the object
        togleDs = False
        mesh = self.checkIsMesh(mesh)

        # print (mesh,type(mesh))
        obj = self.getObjectFromMesh(mesh)
        bpy.context.scene.objects.active = obj

        # The object need to be visible
        if obj.hide :
            togleDs = True
        self.toggleDisplay(obj,display=True)
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        #[‘VERT’, ‘EDGE’, ‘FACE’, ‘ALL’, ‘EDGE_FACE’, ‘ONLY_FACE’, ‘EDGE_LOOP’]
        if vertices != None and faces is None :
            bpy.ops.mesh.delete(type='VERT')
        elif vertices is None and faces != None :
            bpy.ops.mesh.delete(type='FACE')
        elif vertices != None and faces != None :
            bpy.ops.mesh.delete(type='ALL')
        else :
            bpy.ops.object.mode_set(mode='OBJECT')
            return
        # Must be in object mode for from_pydata to work
        bpy.ops.object.mode_set(mode='OBJECT')

        # Add the mesh data.
        if faces is None or len(faces) == 0 :
            #faces = [[0,1,2],] *  len(mesh.faces)
            #me.faces.foreach_get(f,'vertices')
            faces = [list(f.vertices) for f in mesh.faces]
        elif len(faces[0]) == 2 :
            newF = [(f[0],f[1],f[1]) for f in faces]
            faces = newF
        mesh.from_pydata(vertices, [], faces)

        # smooth 
        mesh.update()
        if smooth:
            bpy.ops.object.shade_smooth()
        else:
            bpy.ops.object.shade_flat()
    
        if togleDs :
            self.toggleDisplay(obj,display=False)
#        # Update mesh geometry after adding stuff.
#        mesh.update()
#
#        #smooth face : the vertex normals are averaged to make this face look smooth
#        mesh.calc_normals()

        #mats=mesh.materials
        #check if len vertices is =
#        if len(mesh.data.vertices) == len(vertices):
#            [self.setMeshVerticesCoordinates(v,c) for v,c in zip(mesh.data.vertices,vertices)]
#        elif len(mesh.data.vertices) < len(vertices): 
#            mesh.data.vertices.add(len(vertices)-len(mesh.data.vertices))
#            #add the new one
#            #mesh.verts.extend(vertices)            # add vertices to mesh
#            [self.setMeshVerticesCoordinates(v,c) for v,c in zip(mesh.data.vertices,vertices)]
#        elif len(mesh.data.vertices) > len(vertices): 
#            pass
##        if faces is not None:
##            if type(faces) is not list:
##                faces = faces.tolist()
##            if len(mesh.faces) == len(faces) :
##                [self.setMeshFace(mesh,f,indexes) for f,indexes in zip(mesh.faces,faces)]
##            else : 
##                mesh.faces.delete(1,list(range(len(mesh.faces))))
##                mesh.faces.extend(faces) # add faces to the mesh (also adds edges)
##            #set by default the smooth
##            for face in mesh.faces: face.smooth=1
##            mesh.calcNormals()

#        mesh.materials=mats
#        if mods:
#            for mod in mods:
#                mod[Modifier.Settings.RENDER] = True
#                mod[Modifier.Settings.REALTIME] = True
#                mod[Modifier.Settings.EDITMODE] = False
        #        
#    def alignNormal(self,poly):
#        pass    
#
#    def getFace(self,face):
#        return [v.index for v in face.verts]
#
#    def getFaces(self,object):
#        #get the mesh
#        if type(obj) is str:
#            obj = self.getObject(obj)
#        if obj is None : return
#        mesh=Mesh.Get("Mesh_"+obj.name)
#        bfaces = mesh.faces
#        faces = list(map(self.getFace,c4dfaces))
#        return faces
#        
#
#    def getMatFromColorComparison(self,listMat, color):
#        for i,mat in enumerate(listMat) :
#            col = self.convertColor(mat.getRGBCol())
#            col = [int(col[0]),int(col[1]),int(col[2])]
#            if col == color :
#                return i,mat
#        return 0,None
#    
#    def applyMultiMat(self,mesh,colors):
#        mesh.vertexColors = 1
#        for k,f in enumerate(mesh.faces):
#            #a face have three color...
#            #ncolor = util.convertColor([f.col[0][0],f.col[0][1],f.col[0][2]],toint=False)
#            ncolor = [f.col[0][0],f.col[0][1],f.col[0][2]]
#            i,mat=self.getMatFromColorComparison(mesh.materials, ncolor)
#            if mat is None :
#                print(ncolor,k)
#            f.mat = i
#    
    def color_per_vertex(self,mesh,colors,perVertex=True,perObjectmat=None,pb=False,
                    facesSelection=None,faceMaterial=False):
        mesh=self.getMesh(mesh)
        #self.setEditMode()
        if len(mesh.materials):
            mesh.materials[0].use_vertex_color_paint = True
#        try :
#            bpy.ops.paint.vertex_paint_toggle()
#        except:
#            print ("v context problem")
        if type(colors[0]) is float or type(colors[0]) is int and len(colors) == 3 :
           colors = [colors,]
        #material ->use_vertex_color_paint
        if not hasattr(mesh,"vertex_colors"):
            return False
        if not len(mesh.vertex_colors):
            mesh.vertex_colors.new()# enable vertex colors
        vertexColour = mesh.vertex_colors[0].data

        mfaces = mesh.faces
        mverts = mesh.vertices
        if facesSelection is not None :
            if type(facesSelection) is bool :
                face_sel_indice = self.getMeshFaces(mesh,selected=True)
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
        #verfify perVertex flag
        unic=False
        ncolor=None
#        print("c,v,f ",len(colors), len(mverts), len(mfaces))
        if len(colors) != len(mverts) and len(colors) == len(mfaces): 
            perVertex=False
        elif len(colors) == len(mverts) and len(colors) != len(mfaces): 
            perVertex=True
        else :
            if (len(colors) - len(mverts)) > (len(colors) - len(mfaces)) : 
                perVertex=True
            else :
                perVertex=False            
#        print("perVertex", perVertex)
        if len(colors)==1 : 
            unic=True
            ncolor = self.convertColor(colors[0],toint=False)
        
        # asign colours to verts
        if not faceMaterial:
            for k, f in enumerate(mfaces):
                v = vertexColour[k]
                vi = f.vertices_raw
                if not unic and not perVertex : 
                    if f.index <= len(colors):
                        ncolor = self.convertColor(colors[f.index],toint=False)
                if unic or not perVertex :  
#                    print (colors[f.index],ncolor)
                    v.color1 = ncolor
                    v.color2 = ncolor
                    v.color3 = ncolor
                    v.color4 = ncolor
                else :
                    v.color1 = self.convertColor(colors[vi[0]],toint=False)
                    v.color2 = self.convertColor(colors[vi[1]],toint=False)
                    v.color3 = self.convertColor(colors[vi[2]],toint=False)
                    v.color4 = self.convertColor(colors[vi[3]] ,toint=False)                           
                if pb and (k%70) == 0:
                    progress = float(k) / (len( mesh.faces ))
#                    Window.DrawProgressBar(progress, 'color mesh')

        if unic and facesSelection is None :
           if len(mesh.materials):
               mat = mesh.materials[0]
               if perObjectmat != None : mat = perObjectmat.materials[0]
               mat.diffuse_color = (colors[0][0],colors[0][1],colors[0][2])
        mesh.update()
        #self.restoreEditMode(editmode)
#        try :
#            bpy.ops.paint.vertex_paint_toggle()
#        except :
#            print ("v context problem")
        return True
        
    def changeColor(self,mesh,colors,perVertex=True,perObjectmat=None,pb=False,
                    facesSelection=None,faceMaterial=False):
        if type(colors[0]) is float or type(colors[0]) is int and len(colors) == 3 :
           colors = [colors,]  
        res = self.color_per_vertex(mesh,colors,perVertex=perVertex,
                                    perObjectmat=perObjectmat,pb=pb,
                    facesSelection=facesSelection,faceMaterial=faceMaterial)
        if not res or len(colors) == 1:
            #apply mat to the mesh
            
            o = self.getObject(mesh)
            print ("changeColor",mesh,self.getObject(mesh))
            if o is None :
                o = self.getObjectFromMesh(mesh)
            print ("changeColor",mesh,o)                
            self.changeObjColorMat(o,colors[0])

    def colorMaterial(self,mat,color):
        #mat input is a material name or a material object
        #color input is three rgb value array
        print ("mat ",mat,color)
        try :
            mat = self.getMaterial(mat)
            ncolors=self.convertColor(color,toint=False)  #blenderColor(color)
            mat.diffuse_color = (ncolors[0],ncolors[1],ncolors[2])
        except :
            print(("no mat"))
#  
    def setOneMaterial(self,obj,mat,objmode = False):
        #if not obj.material_slots.__len__():
#        obj.select = True
#        bpy.ops.object.mode_set(mode='OBJECT')
        if mat is None :return
        if type(mat) is list: mat = mat[0]
        bpy.context.scene.objects.active = obj
        if objmode :
#            if len(obj.material_slots.__len__() == 0) 
            bpy.ops.object.mode_set(mode='OBJECT')
        if obj.material_slots.__len__() == 0 :
            bpy.ops.object.material_slot_add()
#            print (obj.material_slots.__len__())
#            print (obj.material_slots)
        #Assign a material to the last slot
        try :
            if objmode :
                obj.material_slots[-1].link = "OBJECT"
            obj.material_slots[-1].material = mat
        except :
            print ("no material?")
            print (obj.material_slots.__len__())
            print (self.getName(obj),obj)
#        #Go to Edit mode
#        bpy.ops.object.mode_set(mode='EDIT')
#         
#        #Select all the vertices
#        bpy.ops.mesh.select_all(action='SELECT') 
#         
#        #Assign the material on all the vertices
#        bpy.ops.object.material_slot_assign() 
#         
#        #Return to Object Mode
#        bpy.ops.object.mode_set(mode='OBJECT')        

    def assignMaterial(self,obj,mat,texture=False,**kw):
        #whatabou objec mode
        objmode = False
        if "objmode" in kw :
            objmode = kw["objmode"]
        if texture :
            if type(mat) is list or type(mat) is tuple:
                mat = mat[0]
#            #need the mesh
#            mesh=obj.getData(False,True)
#            mesh.addUVLayer(obj.name+"UV")
#            print("faceUV ",mesh.faceUV)
        if type(obj) is list:
            for o in obj:
                if  type(mat) == list :
                    for m in mat :
                        self.setOneMaterial(o,m,objmode = objmode)
                else :
                    self.setOneMaterial(o,mat,objmode = objmode)
        else :
            if  type(mat) == list :
                for m in mat :
                    self.setOneMaterial(obj,m,objmode = objmode)
            else :
                self.setOneMaterial(obj,mat,objmode = objmode)
    
    def changeObjColorMat(self,obj,color):
        if obj is None :
            print ("changeObjColorMat obj is None")
            return
        mats=self.getMaterialObject(obj)
        if len(mats) == 0 : 
            mat = self.retrieveColorMat(color)
            if mat == None : 
                mat = self.addMaterial("newColor",color)
            self.setOneMaterial(obj,mat)
        else :
            self.colorMaterial(mats[0],color)
#        obj.colbits = 1<<0
#                    
#    ######ANIMATION FUNCTION########################
#    def insertKeys(self,obj,step=5):
#        curFrame=self.getCurrentScene().getRenderingContext().currentFrame()#Blender.Get('curframe')
#        #print "#######################",curFrame
#        if type(obj) == list or type(obj) == tuple:
#            for o in obj:
#                if type(o) == str : o=getObject(o)
#                o.insertIpoKey(Blender.Object.LOCROT)
#        else :
#            if type(o) == str : o=getObject(o)
#            o.insertIpoKey(Blender.Object.LOCROT)
#        self.getCurrentScene().getRenderingContext().currentFrame(curFrame+step)
#    
#    #############PARTICLE####################################
    #From a pointcloud-yes
    def particle(self,name,coords,group_name=None,radius=None,color=None,hostmatrice=None,**kw):
        doc = self.getCurrentScene()
        cloud = self.PointCloudObject(name+"_cloud",
                                        vertices=coords,
                                        parent=None)[0]
        n = len(coords)
        res = bpy.ops.object.particle_system_add()
        mods = cloud.modifiers
        psm = mods[0]
        PS = psm.particle_system
        set = PS.settings
        set.name = name
        set.count = n
        set.lifetime = 3000
        set.physics_type = 'NO'
        set.frame_start = 0
        set.frame_end = 0
        
        set.emit_from = 'VERT'#Particle.EMITFROM[ 'PARTICLE' | 'VOLUME' | 'FACES' | 'VERTS' ]
        
#        o.glBrown=5.0 #brownian motion brownian_factor
        if "display" in kw :
            if kw["display"] == "cross":
                #place an empty as child of cloud
                #specify duplivert
                cross = self.newEmpty("cross",parent=cloud)
                cloud.dupli_type = "VERTS"
        return cloud

    def getParticles(self,name):
        ob=self.getObject(name+"_cloudds")        
        return ob

    def updateParticles(self,newPos,PS=None): 
        #ps could be  the name too
        #update he point could that have he paricle...
        self.updatePoly(PS,vertices=newPos)
        
    def volume(self,name="",source_object=None,source_particle=None,
               source_type="particle",box=None,
               bounding_box = [[0.,0.,0.],[1.,1.,1.]],mat =None, **kw):
        #create a cube bouding box, 
        #create a volume material with a pointdensity texture
        #attach the PS-Object to the point density
        sType = {"particle":"PARTICLE_SYSTEM","object":"OBJECT"}
        if source_object is None :
            return
        if mat is None :
            mat,texture = self.createVolumeMaterial(name+"vMat")#default is 'POINT_DENSITY'
        else :
            texture = mat.texture_slots[0].texture
        tslot = mat.texture_slots[0]
        mat.density = 0.5
        mat.scattering = 15.0
        if box is None :
            #create box or hexaedre?
            box,mesh = self.box(name+"vBox",cornerPoints=bounding_box,mat = mat)
        try :
            pointds = texture.point_density
        except :
            print ("probleme volume texture")
            return
        
        pointds.point_source = sType[source_type]
        pointds.object = source_object
        pointds.radius = 1.0
        if source_particle is None :
            #try to get the source_particle from the object
            mods = source_object.modifiers
            for m in mods :
                if m.type == "PARTICLE_SYSTEM" :
                    psm = m
                    source_particle = psm.particle_system           
                    set = source_particle.settings
                    set.use_render_emitter = 0
                    set.render_type = None
                    set.draw_method = "POINT"
                    break
            if source_particle is None :
                pointds.point_source = "OBJECT"
        pointds.particle_system = source_particle
        #pointds.color_source #[‘CONSTANT’, ‘PARTICLE_AGE’, ‘PARTICLE_SPEED’, ‘PARTICLE_VELOCITY’]
        tslot.use_color_ramp = 1
        tslot.use_map_density = 1
        tslot.use_map_color_emission = 0
        tslot.blend_type = "MULTIPLY"
        #pointds.color_ramp
        return box,mat,texture
        
#    #From a pointcloud-yes
#    def newParticleSystem(self,name,object,n):
#        o=Blender.Particle.new(object)
#        o.setName(name)
#        o.particleDistribution=3 #Particle.EMITFROM[ 'PARTICLE' | 'VOLUME' | 'FACES' | 'VERTS' ]
#        o.amount = n
#        o.glBrown=5.0
#        
#
#    def addTextFile(self,name="",file=None,text=None):
#        if file is None and text is None :
#            return
#        if file is not None :
#            try:
#                f = open(file,'r')
#                script = f.read()
#                f.close()
#            except:
#                return
#        elif text is not None :
#            script = text
#        texts = list(bpy.data.texts)
#        newText = [tex for tex in texts if tex.name == name]
#        if not len(newText) :
#            newText = Blender.Text.New(name)
#        else :
#            newText[0].clear()
#            newText=newText[0]
#        for line in script : newText.write(line)
#
    def FromVec(self,v,pos=False):
        return mathutils.Vector((v[0],v[1],v[2]))

    def ToVec(self,v,pos=False):
        return [v[0],v[1],v[2]]

#    def getUV(self,object,faceIndex,vertexIndex,perVertice=True):
#        ob = self.getObject(object)
#        #uv is per polygon
#        mesh=ob.getData(False,True)
#        #print mesh.faceUV
#        face = mesh.faces[faceIndex]
#        uvs = face.uv
#        if perVertice :
#            for j,k in enumerate(uvs):
#                if j == vertexIndex :
#                    return self.ToVec(uvs[k])
#        else :
#            return [self.ToVec(uvs[k]) for k in uvs]
#
#    def setUV(self,object,faceIndex,vertexIndex,uv,perVertice=True,uvid=0):
#        #triangle 
#        ob = self.getObject(object)
#        #uv is per polygon
#        mesh=ob.getData(False,True)
#        #print mesh.faceUV
#        face = mesh.faces[faceIndex]
#        if perVertice :
#            uvs = face.uv#tag.GetSlow(faceIndex)
#            for j,k in enumerate(uvs):
#                if j == vertexIndex :
#                    uvs[k] = self.FromVec(uv)
#            face.uv = uvs
#        else :
#            uvs = [self.FromVec(x) for x in uv[0:len(face)]]
#            face.uv = uvs
#        mesh.update()
#
#    def ToMat(self,host_mat):
#        return host_mat[:]
#
    def setMeshVerticesCoordinates(self,v,coordinate):
        v.co = self.FromVec(coordinate)

    def deleteMeshVertices(self,poly, vertices=None):
        bpy.ops.object.mode_set(mode='EDIT')
        #bpy.ops.mesh.select_all(action='DESELECT')
        if vertices is not None :
            bpy.ops.mesh.select_all(action='DESELECT')
            self.selectVertices(poly, vertices)
        bpy.ops.mesh.delete(type='VERT')
        bpy.ops.object.mode_set(mode='OBJECT')

    def getMeshVertice(self,poly,vindice,**kw):
#        self.toggleEditMode()
        mesh = self.checkIsMesh(poly)
        return self.ToVec(mesh.vertices[vindice].co)
        
    def getMeshVertices(self,poly,transform=False,selected = False):
#        self.toggleEditMode()
        mesh = self.checkIsMesh(poly)
        points = mesh.vertices
        if selected:
            listeindice = [v.index for v in mesh.vertices if v.select and not v.hide]
#            listeindice = mesh.verts.selected()       
            vertices = [self.ToVec(points[v].co) for v in listeindice]
#            self.restoreEditMode(editmode)
            return vertices, listeindice        
        else:
            vertices = [self.ToVec(v.co) for v in points]
            return vertices
        
    def getMeshNormales(self,poly,selected = False):
#        editmode = self.toggleEditMode()
        mesh = self.checkIsMesh(poly)
        points = mesh.vertices
        mesh.calc_normals()
        if selected:
            listeindice = [v.index for v in mesh.vertices if v.select and not v.hide]
            vnormals = [self.ToVec(points[v].normal) for v in listeindice]
#            self.restoreEditMode(editmode)
            return vnormals, listeindice           
        else :
            vnormals = [self.ToVec(v.normal) for v in points]
            return vnormals

        mesh = self.checkIsMesh(poly)
        mfaces = mesh.faces
        if selected :
            mfaces_indice = [face.index for face in mesh.faces
                             if face.select and not face.hide]
            faces = [self.getMeshFace(mfaces[f]) for f in mfaces_indice]
            return faces, mfaces_indice
        else :
            faces = [self.getMeshFace(f) for f in mfaces]    
            return faces

    def getMeshFaceNormales(self,poly,selected = False):
#        editmode = self.toggleEditMode()
        mesh = self.checkIsMesh(poly)
        mfaces = mesh.faces
        mesh.calc_normals()
        facesnormals=[]
        if selected :
            mfaces_indice = [face.index for face in mesh.faces
                             if face.select and not face.hide]
            facesnormals = [self.ToVec(mfaces[f].normal) for f in mfaces_indice]
            return facesnormals,mfaces_indice
        else :
            facesnormals = [self.ToVec(f.normal) for f in mfaces]    
            return facesnormals
            
    def getMeshEdge(self,e):
        return e.vertices[0],e.vertices[1]

    def getMeshEdges(self, poly, selected=False):
        editmode = self.toggleEditMode()
        mesh = self.checkIsMesh(poly)
        medges = mesh.edges
        if selected:
            medges_indice = [e.index for e in mesh.edges if e.select and not e.hide]#mesh.edges.selected()
            edges = [self.getMeshEdge(medges[e]) for e in medges_indice]
            self.restoreEditMode(editmode)
            return edges,medges_indice
        else :
            edges = [self.getMeshEdge(e) for e in medges]
            return edges

    def deleteMeshEdges(self,poly, edges=None):
        bpy.ops.object.mode_set(mode='EDIT')
        #bpy.ops.mesh.select_all(action='DESELECT')
        if vertices is not None :
            bpy.ops.mesh.select_all(action='DESELECT')
            self.selectEdges(poly, edges)
        bpy.ops.mesh.delete(type='EDGE')
        bpy.ops.object.mode_set(mode='OBJECT')

    def getFaceEdges(self, poly, faceindice, selected=False):
        mesh = self.checkIsMesh(poly)
        return mesh.faces[faceindice].edge_keys    
#
#    def setMeshFace(self,mesh,f,indexes):
#        print(indexes)
##        f.v = None
#        listeV=[]
#        for i,v in enumerate(indexes):
#            listeV.append(mesh.verts[v])
#        f.v = tuple(listeV)
#        
    def getMeshFace(self, f):
        return f.vertices#difference with f.vertices_raw?s
#        if len(f.vertices) == 3:
#            return f.vertices[0], f.vertices[1], f.vertices[2]
#        elif len(f.vertices) == 4:
#            return f.vertices[0], f.vertices[1], f.vertices[2],f.vertices[3]

    def getMeshFaces(self, poly, selected = False):
        mesh = self.checkIsMesh(poly)
        mfaces = mesh.faces
        if selected :
            mfaces_indice = [face.index for face in mesh.faces
                             if face.select and not face.hide]
            faces = [self.getMeshFace(mfaces[f]) for f in mfaces_indice]
            return faces, mfaces_indice
        else :
            faces = [self.getMeshFace(f) for f in mfaces]    
            return faces

    def deleteMeshFaces(self,poly, faces=None):
        bpy.ops.object.mode_set(mode='EDIT')
        #bpy.ops.mesh.select_all(action='DESELECT')
        if faces is not None :
            bpy.ops.mesh.select_all(action='DESELECT')
            self.selectFaces(poly, faces)
        bpy.ops.mesh.delete(type='FACE')
        bpy.ops.object.mode_set(mode='OBJECT')

    def addMeshVertices(self, poly, vertices_coordinates, vertices_indices=None,**kw):
        togleDs = False
        mesh = self.checkIsMesh(poly)

        # print (mesh,type(mesh))
        obj = self.getObjectFromMesh(mesh)
        bpy.context.scene.objects.active = obj

        # The object need to be visible
        if obj.hide :
            togleDs = True
        self.toggleDisplay(obj,display=True)
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        #[‘VERT’, ‘EDGE’, ‘FACE’, ‘ALL’, ‘EDGE_FACE’, ‘ONLY_FACE’, ‘EDGE_LOOP’]
        vertices = self.getMeshVertices(poly) 
        faces = self.getMeshVertices(poly) 
        bpy.ops.mesh.delete(type='VERT')
        bpy.ops.object.mode_set(mode='OBJECT')
        vertices.extend(vertices_coordinates)
        mesh.from_pydata(vertices, [], faces)
        if togleDs :
            self.toggleDisplay(obj,display=False) 

    def addMeshFaces(self, poly, faces_vertices_indices,**kw):
        togleDs = False
        mesh = self.checkIsMesh(poly)

        # print (mesh,type(mesh))
        obj = self.getObjectFromMesh(mesh)
        bpy.context.scene.objects.active = obj

        # The object need to be visible
        if obj.hide :
            togleDs = True
        self.toggleDisplay(obj,display=True)
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        #[‘VERT’, ‘EDGE’, ‘FACE’, ‘ALL’, ‘EDGE_FACE’, ‘ONLY_FACE’, ‘EDGE_LOOP’]
        vertices = self.getMeshVertices(poly) 
        faces = self.getMeshVertices(poly) 
        bpy.ops.mesh.delete(type='FACE')
        bpy.ops.object.mode_set(mode='OBJECT')
        faces.extend(faces_vertices_indices)
        mesh.from_pydata(vertices, [], faces)
        if togleDs :
            self.toggleDisplay(obj,display=False) 
              
    def selectFace(self, obj, index, select=True):
        curr = bpy.context.tool_settings.mesh_select_mode
        bpy.context.tool_settings.mesh_select_mode = (curr[0], curr[1], True)
        mesh = self.checkIsMesh(obj)
        mesh.faces[index].select = select
    
    def selectFaces(self, obj, indices, select=True):
        editmode=self.toggleEditMode()
        curr = bpy.context.tool_settings.mesh_select_mode
        bpy.context.tool_settings.mesh_select_mode = (curr[0], curr[1], True)
        
        mesh = self.checkIsMesh(obj)
        for ind in indices:
            if ind >= len(mesh.faces):
                continue
            mesh.faces[ind].select = select
        self.restoreEditMode(editmode)

    def selectEdge(self, obj, index, select=True):
        curr = bpy.context.tool_settings.mesh_select_mode
        bpy.context.tool_settings.mesh_select_mode = (curr[0], True, curr[2])
        mesh = self.checkIsMesh(obj)
        mesh.edges[index].select = select

    def selectEdges(self, obj, indices, select=True):
        editmode=self.toggleEditMode()
        curr = bpy.context.tool_settings.mesh_select_mode
        bpy.context.tool_settings.mesh_select_mode = (curr[0], True, curr[2])
        
        mesh = self.getMeshFrom(obj)
        for ind in indices:
            if ind >= len(mesh.edges):
                continue
            mesh.edges[ind].select = select
        self.restoreEditMode(editmode)

    def selectVertex(self, obj, index, select=True, **kw):
        curr = bpy.context.tool_settings.mesh_select_mode
        bpy.context.tool_settings.mesh_select_mode = (True, curr[1], curr[2])
        mesh = self.getMeshFrom(obj)
        mesh.vertices[index].select = select
        
        
    def selectVertices(self, obj, indices, select=True, **kw):         
        editmode=self.toggleEditMode()
        curr = bpy.context.tool_settings.mesh_select_mode
        bpy.context.tool_settings.mesh_select_mode = (True, curr[1], curr[2])
        mesh = self.getMeshFrom(obj)
        for ind in indices:
            if ind >= len(mesh.vertices):
                continue
            mesh.vertices[ind].select = select
        self.restoreEditMode(editmode)

    def DecomposeMesh(self,poly,edit=True,copy=True,tri=True,transform=True,**kw):
        mesh = self.getMeshFrom(poly)
        vertices = self.getMeshVertices(mesh)
        faces = self.getMeshFaces(mesh)
        vnormals = self.getMeshNormales(mesh)
        print ("########################################") 
        if transform :
            #node = self.getNode(mesh)
            #fnTrans = om.MFnTransform(mesh)
            ob = self.getObject(poly)
#            bpy.context.scene.objects.active = ob
#            ob = bpy.context.object
            mat = self.getObjectMatrix(ob)#ob.matrix_world #cache problem ?
            print ("########################################")            
            print (ob,poly,mat)
            #mat.transpose()# numpy.array(mmat).transpose()#self.m2matrix(mmat)
            #print (ob,poly,mat)
            vertices = self.ApplyMatrix(vertices,mat)
#        if edit and copy :
#            self.getCurrentScene().SetActiveObject(poly)
#            c4d.CallCommand(100004787) #delete the obj       
        if "fn" in kw and kw["fn"] :
            fnormals = self.getMeshFaceNormales(mesh)
            return faces,vertices,vnormals,fnormals
        else :
            return faces,vertices,vnormals

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
    
        #4x4matrix"
#        mat = numpy.array(mat)
        if self._usenumpy:
            return Helper.ApplyMatrix(self,coords,mat)
        else :            
            return [self.FromVec(c)*mat for c in coords]

    def rotation_matrix(self,angle, direction, point=None,trans=None):
        """
        Return matrix to rotate about axis defined by point and direction.
    
        """
        if self._usenumpy:
            return Helper.rotation_matrix(angle, direction, point=point,trans=trans)
        else :            
            direction = self.FromVec(direction[:3])
            direction.normalize()
            m = mathutils.Matrix.Rotation(angle,4,direction)
            M = m.copy()
            if point is not None:
               point = self.FromVec(point[:3]) 
               M.translation = point - (point * m)
            if trans is not None :
               M.translation = trans
            return M        
        
    def triangulate(self,poly):
        #select poly
        baseobj = self.getObjectFromMesh(poly)
        bpy.context.scene.objects.active = baseobj
        #toggle edit mode 
        bpy.ops.object.mode_set(mode='EDIT')
        #select all face
        bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.mesh.quads_convert_to_tris()
        bpy.ops.object.mode_set(mode='OBJECT')


#==============================================================================
# Noise
#==============================================================================
    
    def get_noise(self,point,ntype,nbasis,dimension=1.0,lacunarity=2.0,offset=1.0,octaves=6,gain=1.0,**kw):
        #multi_fractal(position, H, lacunarity, octaves, noise_basis=noise.types.STDPERLIN)
  
        depth = octaves
        value = 0.0        
        x,y,z = point  
#        nbasis = self.noise_type[nbasis]
        vlbasis = nbasis
        hardnoise =False
        if "hardnoise" in kw :
            hardnoise = kw["hardnoise"]
        distortion = 1.0
        if "distortion" in kw :
            distortion = kw["distortion"]
            
        if ntype == 0 :  value = noise.multi_fractal(        point, dimension, lacunarity, depth, nbasis ) * 0.5
        elif ntype == 1: value = noise.ridged_multi_fractal( point, dimension, lacunarity, depth, offset, gain, nbasis ) * 0.5
        elif ntype == 2: value = noise.hybrid_multi_fractal( point, dimension, lacunarity, depth, offset, gain, nbasis ) * 0.5
        elif ntype == 3: value = noise.hetero_terrain(       point, dimension, lacunarity, depth, offset, nbasis ) * 0.25
        elif ntype == 4: value = noise.fractal(              point, dimension, lacunarity, depth, nbasis )
        elif ntype == 5: value = noise.turbulence_vector(    point, depth, hardnoise, nbasis )[0]
        elif ntype == 6: value = noise.variable_lacunarity(  point, distortion, nbasis, vlbasis ) + 0.5
#        elif ntype == 7: value = self.marble_noise( x*2.0/falloffsize,y*2.0/falloffsize,z*2/falloffsize, origin, nsize, marbleshape, marblebias, marblesharpnes, distortion, depth, hardnoise, nbasis )
#        elif ntype == 8: value = self.shattered_hterrain( point[0], point[1], point[2], dimension, lacunarity, depth, offset, distortion, nbasis )
#        elif ntype == 9: value = self.strata_hterrain( point[0], point[1], point[2], dimension, lacunarity, depth, offset, distortion, nbasis )
        return value
        
        
#==============================================================================
# import / expor / read load / save
#==============================================================================

    def read(self,filename,**kw):
        fileName, fileExtension = os.path.splitext(filename)
#        print (fileName, fileExtension)
        if fileExtension == ".dae" :
            bpy.ops.wm.collada_import(filepath=filename)#, filter_blender=False, filter_image=False, 
#                                      filter_movie=False, filter_python=False, filter_font=False, 
#                                      filter_sound=False, filter_text=False, filter_btx=False, 
#                                      filter_collada=True, filter_folder=True, filemode=8, 
#                                      display_type='FILE_DEFAULTDISPLAY')
        elif fileExtension == ".blend":
#            bpy.ops.wm.open_mainfile(filepath=filename, filter_blender=True, 
#                                     filter_image=False, filter_movie=False, 
#                                     filter_python=False, filter_font=False, 
#                                     filter_sound=False, filter_text=False, 
#                                     filter_btx=False, filter_collada=False, 
#                                     filter_folder=True, filemode=8, 
#                                     load_ui=False, use_scripts=True)
#            ["Scene/Scene","Object/*"]
#             bpy.ops.wm.link_append(filepath=filename, directory="Object", filename="*", 
#                                    files=None, filter_blender=True, filter_image=False, 
#                                    filter_movie=False, filter_python=False, filter_font=False, 
#                                    filter_sound=False, filter_text=False, filter_btx=False,
#                                    filter_collada=False, filter_folder=False, filemode=1, 
#                                    relative_path=False, link=False, autoselect=True, 
#                                    active_layer=True, instance_groups=False)
#             f="/Users/ludo/DEV/Blender/blender-2.62release-OSX_10.6_x86_64/MGLToolsPckgs/AutoFill/cache_ingredients/HIV_1_1_NucleocapsidHostMesh.blend"
#             bpy.ops.wm.link_append(filepath=f, directory=f+"/Object/",filename="*")
            with bpy.data.libraries.load(filename) as (src, _):
                try:
                    objlist = [{'name':obj} for obj in src.objects]
                except UnicodeDecodeError as detail:
                    print(detail)
            bpy.ops.wm.link_append(directory=filename + '/Object/', link=False, autoselect=True, files=objlist) 
            print (objlist)
#            with bpy.data.libraries.load(f) as (data_from, data_to):
#                data_to.objects = data_from.objects
#                data_to.materials = data_from.materials
#            for obj in data_to.objects: bpy.context.scene.objects.link(bpy.data.objects[obj])    

#    def write(self,listObj,*args, **kw):
#        pass


#==============================================================================
# raycasing                
#==============================================================================
    def raycast(self, obj, point, direction, length, **kw ):
        obj = self.getObject(obj)
        #from http://blenderartists.org/forum/showthread.php?195605-Detecting-if-a-point-is-inside-a-mesh-2-5-API
        # @Atom you're right, ray_cast is in object_space
        # http://www.blender.org/documentation/250PythonDoc/bpy.types.Object.html#bpy.types.Object.ray_cast
#        direction = [0.,1.,0.]
#        if length < 1.0 :
#            length = 10.0
        ray_p = self.FromVec(point)
        ray_dir = self.FromVec(direction)
        p_to_dir = ray_dir - ray_p
        mat = mathutils.Matrix(obj.matrix_world)#copy the matrix
        mat.invert()
        orig = mat*ray_p#
        p_to_dir = mat*p_to_dir
        count = 0
#        r=helper.oneCylinder("ray",[-0.0931, -0.0578, 0.0336],[0.9315, -0.3362, -10.5780],radiu=0.5)
        while True:            
            location,normal,index = obj.ray_cast(orig,p_to_dir*length)
            if index == -1: 
                #no intersection
                intersect = False
                break
            count += 1
            orig = location + p_to_dir*0.00001
        if "count" in kw :
            #print (intersect,count)
            return intersect,count
        return intersect

#    def backingVertexColor(self,obj,name="bakeColor",filename="~/color.png"):
#        #need unwrapped mesh ie in selection the second one or the only one
#        #then need to create the image texture
#        #then back
#        #then link texture to material
#        obj = self.getObject(obj)
#        mesh = obj.getData(mesh=1)
#        nmesh = NMesh.GetRaw(mesh.name)
#        mats = self.getMaterialObject(obj)
#        if not len(mats):
#            mats = self.getMaterialObject(nmesh) #this work on NMesh not Mesh
#        print(mats)
#        mat = None
#        if len(mats):
#            mat = mats[0]
#        scn = self.getCurrentScene()
#        #compute UV unwrapping
#        #select the object
#        self.ObjectsSelection([obj,],typeSel="new")
#        #execute the 
#        import pyubic.blender.uvcalc_smart_project as uvc
#        Blender.Window.EditMode(1)
#        #this should create the UV coordinate of the unfold surface
#        if not mesh.faceUV:
#            uvc.doit()
#        #now we have uv coordinate, need an image to bake
#        #mat = self.createTexturedMaterial("uvMat","/Users/Shared/uv.png")
#        img = Blender.Image.New(name, 800, 800, 32)
#        img.setFilename(filename)
#        img.save()
#        #problem for make image current in UV editor
#        img.makeCurrent()
#        bpy.data.images.active = img
#        #need an update?
#        #self.assignMaterial([mat,],obj,texture=True)
#        #now we can bake
#        Blender.Window.EditMode(0)
#        context = scn.getRenderingContext()
#        context.bakeClear = True
#        context.bakeMode = Render.BakeModes.TEXTURE #NORMALS
#        context.bakeNormalSpace = Render.BakeNormalSpaceModes.CAMERA #TANGENT
#        context.bake()
#        img.save()
#        #now link to the objetc with a new material ? or the current material
#        nmat = self.createTexturedMaterial("uvMat",filename,mat=mat)
#        if mat is None :
#            self.assignMaterial(obj,[nmat,],texture=True)
#        #context.bakeToActive = True
#        

