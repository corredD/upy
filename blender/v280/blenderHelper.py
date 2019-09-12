
"""
    Copyright (C) <2010>  Autin L. TSRI
    
    This file git_upy/blender/v271/blenderHelper.py is part of upy.

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
from bpy import *

import bmesh

import mathutils
try :
    import noise
except :
    from mathutils import noise

#import numpy #still need to deal with numpy
from upy import hostHelper
#from upy.hostHelper import Helper
from upy.blender.v263.blenderHelper import blenderHelper as Helper
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
    render = "BLENDER"
    
    def __init__(self,master=None,**kw):
        Helper.__init__(self,**kw)
        #setup metric unit to centimeter?
        sc=bpy.context.scene
        sc.unit_settings.system = 'METRIC'
        sc.unit_settings.scale_length = 0.01 #centimeter
        #sv3d = self.getSpaceView3D()
        sc.cursor.location = [0,0,0]
        print ("blender unit setup")
        self.setViewport(clipstart=0.001,clipend=10000,shader="solid")
        self.render = bpy.context.scene.render.engine

    def getSpaceView3D(self):
        screen = bpy.context.screen
        for area in screen.areas[:]:
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
        #if "center" in kw :
        #    if kw["center"] :
        #        bpy.ops.view3d.view_all(center=False)
        bpy.context.scene.cursor.location = [0,0,0]
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
            #shading.type
            #bpy.data.screens["Scripting"].shading.type = 'SOLID'
            #if engine == 'CYCLE':
            #    sv3d.viewport_shade = self.vshade[kw["shader"]]
            #    sv3d.show_textured_solid = True
            #else :
                #Doest work in the blender console
                #bpy.context.screen.shading.type = 'SOLID'
            #    sv3d.show_textured_solid = True
            #print ("shader ",kw["shader"],self.vshade[kw["shader"]])
            
    def setObjectActive(self,aObject):
        bpy.context.view_layer.objects.active = aObject
        
    def getObjectActive(self):
        return bpy.context.view_layer.objects.active

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
        if obj is None :
            return
        if type(obj) == bpy.types.Mesh:
            return obj
        else :
            return self.getMesh(obj)
#        obj = self.getObject(obj)
#        obj.select = True
#        self.getCurrentScene().objects.active = obj
#        mesh = obj.data
#        return mesh

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
        print ("checkIsMesh",mesh,type(mesh))
        if type(mesh) is str :
            return self.getMesh(mesh)
        if type(mesh) == bpy.types.Object:
            print ("object of type",mesh.type)
            return self.getMeshFrom(mesh) 
        if type(mesh) == bpy.types.Mesh:
            print ("its a mesh")
            return mesh

    def getFirstMesh (self,m,**kw):
        im=True
        if "instance_master" in kw :
            im = kw["instance_master"]        
        if m is None :
            return None
        print ("getFirstMesh",m,type(m),im)
        if type(m)  == bpy.types.Mesh :
            return m
        elif type(m) == bpy.types.Object :
            #what kind
            print ("type of m is ",type(m),m.type)
            if m.type == self.EMPTY :
                n=self.getChilds(m)[0] 
                return self.getFirstMesh(n,instance_master=im)
            else :
                return m.data 
        #elif type(m) == c4d.Oinstance :
#       #     print ("do instance ?",im,m)
        #    if im :
        #        return self.getFirstMesh(m[c4d.INSTANCEOBJECT_LINK])
        #    else :
#       #         print ("instance ",m)
        #        return m
        else :
            #print ("what ? getFirstMesh",m,m.GetType())
            return m#can be cylinder#cself.getFirstMesh(m.GetDown())

    def getMesh(self,name,**kw):
        im = True #go until instance master if any
        if "instance_master" in kw :
            im = kw["instance_master"]
        print ("getMesh of ",name,type(name))
        if type(name) is str:
            mesh = bpy.data.meshes.get(name)
            if mesh is None : 
                print ("mesh is none")
                obj = bpy.data.objects.get(name)
                if obj is not None :
                    print ("whats the data",obj,type(obj),obj.type)
                    return self.getFirstMesh(obj,instance_master=im)
            else :
                return mesh
        elif type(name) != str :
            if type(name) == bpy.types.Object:
                if name.data is not None :
                    print ("whats the name data",name.data,type(name.data))
                    return name.data
                else :
                    return self.getFirstMesh(name,instance_master=im)
            elif type(name) == bpy.types.Mesh:
                return name
        return None

    def newEmpty(self,name,location=(0.,0.,0.),visible=0,**kw):
        res = bpy.ops.object.add(type='EMPTY',location=location)
        obj = bpy.context.object
        obj.name = name
        parent = None
        if "parent" in kw :
            parent = kw["parent"]
        self.addObjectToScene(self.getCurrentScene(),obj,parent=parent)
        #obj.empty_draw_size = 1.0
        obj.empty_display_size = 1.0
        return obj

    def addLampToScene(self,name,Type='Area',rgb=[1.,1.,1.],dist=25.0,energy=1.0,
                       soft=1.0,shadow=False,center=[0.,0.,0.],sc=None,**kw):
        res = bpy.ops.object.add(type='LIGHT',location=(center[0],center[1],center[2]))
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
            lampe.use_shadow = True

    def Sphere(self,name,res=16,radius=1.0,pos=None,color=None,mat=None,parent=None):
        #segments=32, ring_count=16, radius=1.0, calc_uvs=True, enter_editmode=False, align='WORLD', location=(0.0, 0.0, 0.0), rotation=(0.0, 0.0, 0.0)
        res = bpy.ops.mesh.primitive_uv_sphere_add(segments=res, ring_count=res, radius=radius) 
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

    def updateSphereMesh(self,mesh,verts=None,faces=None,basemesh=None,
                         scale=None,typ=None,**kw):
        if verts is None :
            if basemesh is not None :
                baseobj = self.getObjectFromMesh(basemesh)
                print ("updateSphereMesh",baseobj,basemesh)
                #obj.select_set(True)
                self.setObjectActive (baseobj)
                #bpy.context.scene.objects.active = baseobj
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

    def Cone(self,name,radius=1.,length=1.,res=9, pos = [0.,0.,0.],parent=None):
        #(vertices=32, radius1=1.0, radius2=0.0, depth=2.0, end_fill_type='NGON', calc_uvs=True, enter_editmode=False, align='WORLD', location=(0.0, 0.0, 0.0), rotation=(0.0, 0.0, 0.0))
        res = bpy.ops.mesh.primitive_cone_add(vertices=res, radius1=radius,radius2=0.0, 
                                depth=length,
                                location = (float(pos[0]),float(pos[1]),float(pos[2]))) 
        obj = bpy.context.object
        obj.name = name
        mesh = obj.data
        mesh.name = "mesh_"+name
        if parent is not None:
            obj.parent = parent        
        return obj,mesh

    def updateTubeMesh(self,mesh,basemesh=None,verts=None,faces=None,cradius=1.0,quality=1.):
        if verts is None :
            if basemesh is not None :
                baseobj = self.getObjectFromMesh(basemesh)
#                print (baseobj,basemesh)
                self.setObjectActive (baseobj)
                #bpy.context.scene.objects.active = baseobj
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

    def addMaterial(self,name,col):
        mat = bpy.data.materials.new(name)
        mat.diffuse_color = (col[0],col[1],col[2],1)
        return mat

    def setOneMaterial(self,obj,mat,objmode = False):
        #if not obj.material_slots.__len__():
#        obj.select = True
#        bpy.ops.object.mode_set(mode='OBJECT')
        if mat is None :return
        if type(mat) is list: mat = mat[0]
        # And finally select it and make it active.
        obj.select_set(True)
        self.setObjectActive (obj)    
        if objmode :
            bpy.ops.object.mode_set(mode='OBJECT')
        if obj.material_slots.__len__() == 0 :
            bpy.ops.object.material_slot_add()
        try :
            if objmode :
                obj.material_slots[-1].link = "OBJECT"
            obj.material_slots[-1].material = mat
        except :
            print ("no material?")
            print (obj.material_slots.__len__())
            print (self.getName(obj),obj)
    
    def colorMaterial(self,mat,color):
        #mat input is a material name or a material object
        #color input is three rgb value array
        print ("mat ",mat,color)
        if type(mat) is str or type(mat) is bytes : 
            mat = bpy.data.materials.get(mat)
        ncolors=self.convertColor(color,toint=False)  #blenderColor(color)
        mat.diffuse_color = [ncolors[0],ncolors[1],ncolors[2],1]

    def createTexturedMaterial(self,name,filename,normal=False,mat=None,w=640,h=480):    
        #bpy.ops.texture.new() 
        footex = bpy.data.textures.new(name+"texture",type = 'IMAGE' )             
        footex.use_normal_map = normal
        # make foo be an image texture
        if filename is None:
            img = bpy.data.images.new(name,width=w, height = h)        
            img.filepath = name
            img.save()
        else :
            img = bpy.data.images.load(filename)           # load an image
        footex.image = img                   # link the image to the texture
        if mat is None :
            mat = bpy.data.materials.new(name)    # get a material
        #texture_paint_slots
        #Tslot = mat.texture_slots.add()
        #Tslot.texture = footex 
        return mat,footex
#   
    def color_per_vertex(self,mesh,colors,perVertex=True,perObjectmat=None,pb=False,
                    facesSelection=None,faceMaterial=False):
        mesh=self.getMesh(mesh)
        #if len(mesh.materials):
        #    mesh.materials[0].use_vertex_color_paint = True
        #bpy.ops.paint.vertex_paint_toggle()
        if type(colors[0]) is float or type(colors[0]) is int and len(colors) == 3 :
           colors = [colors,]
        
        colors = numpy.array(colors)
        one = numpy.ones( (colors.shape[0], 1), colors.dtype.char )
        colors = numpy.concatenate( (colors, one), 1 )
        #material ->use_vertex_color_paint
        if not hasattr(mesh,"vertex_colors"):
            return False
        if not len(mesh.vertex_colors) or mesh.vertex_colors.active is None:
            colormap = mesh.vertex_colors.new()
            vertexColour = colormap.data# enable vertex colors
        else :
            vertexColour = mesh.vertex_colors.active.data#mesh.vertex_colors[0].data

        mfaces = mesh.polygons
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
#        print ("faceMaterial",faceMaterial,"perVertex",perVertex,len(mfaces),unic)
        # asign colours to verts
        if not faceMaterial:
            j =0
            for k, f in enumerate(mfaces):
                v = vertexColour[k]
                vi = f.vertices#vertices_raw
                if not unic and not perVertex : 
                    if f.index <= len(colors):
                        ncolor = self.convertColor(colors[f.index],toint=False)
#                        print ("uniq",ncolor)
                #if unic or not perVertex :                      
                for l in range(len(f.vertices)):             
                    v = vertexColour[j]
                    if unic or not perVertex : 
                        v.color = ncolor
                    else :
                        v.color = self.convertColor(colors[vi[l]],toint=False)
#                    print ("vertice",v.color)
                    j+=1        
                if pb and (k%70) == 0:
                    progress = float(k) / (len( mesh.polygons ))
#                print ("color progress",float(k) / (len( mesh.polygons )))
#                    Window.DrawProgressBar(progress, 'color mesh')
                    
        if unic and facesSelection is None :
           if len(mesh.materials):
               mat = mesh.materials[0]
               if perObjectmat != None : mat = perObjectmat.materials[0]
               mat.diffuse_color = (colors[0][0],colors[0][1],colors[0][2],1)
        mesh.update()
        #self.restoreEditMode(editmode)
#        try :
#            bpy.ops.paint.vertex_paint_toggle()
#        except :
#            print ("v context problem")
        return True
 
#

    def getPropertyObject(self, obj, key=["radius"]):
        """
        Return the  property "key" of the object obj
        
        * overwrited by children class for each host
        
        @type  obj: host Obj
        @param obj: the object that contains the property
        @type  key: string
        @param key: name of the property        

        @rtype  : int, float, str, dict, list
        @return : the property value    
        """          
        allk=[]
        for k in key:
            if k == "pos":
                k = "location"
            v = self.getProperty(obj, k)
            if k == "location":
                v = self.ToVec(v)
            allk.append(v)
        return allk

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
        #face can be a numpy array need  the list
        if isinstance(faces,numpy.ndarray):
            faces = numpy.array(faces).tolist()
        if faces and len(faces[0]) == 2 :
            newF = [(f[0],f[1],f[1]) for f in faces]
            faces = newF
        # Make a mesh from a list of verts/edges/faces. float, int, int
        #        print (type(vertices[0][0]))
        if self.usenumpy :
            faces=numpy.array(faces,"int").tolist()
        if type(faces[0][0]) != int:        
            if not self.usenumpy :
                faces=[ [int(f[0]),int(f[1]),int(f[2])] for f in faces ]
        if type(vertices[0][0]) != float :
            if self.usenumpy :
                vertices = numpy.array(vertices,'f')
            else :
                vertices = [[float(v[0]),float(v[1]),float(v[2])] for v in vertices]
        #        print(type(faces),type(faces[0]),type(faces[0][0]),faces)
        polygon.from_pydata(vertices, [], faces)
        # Update mesh geometry after adding stuff.
        polygon.update()

        #smooth face : the vertex normals are averaged to make this face look smooth
        polygon.calc_normals()
        if dejavu :
            obpolygon = bpy.data.objects.new(name,polygon)
            bpy.context.view_layer.active_layer_collection.collection.objects.link(obpolygon)
            obpolygon.select_set(True)
            return obpolygon
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
        pt=False
        if isinstance(faces,numpy.ndarray):
            faces = numpy.array(faces).tolist()
#        print (faces)
        if not faces or len(faces[0]) == 2:
            pt= True
        polygon = self.polygons("M_"+name, vertices=vertices, normals=vnormals,
                                faces=faces, material=material, color=color,
                                smooth=smooth, proxyCol=proxyCol, **kw)
        
        obpolygon = bpy.data.objects.new(name, polygon)
        #bpy.ops.object.add_named(linked=False, name=name)
        bpy.context.view_layer.active_layer_collection.collection.objects.link(obpolygon)
#        obpolygon.draw_type = 'SMOOTH'
        parent = None
        if "parent" in kw :
            parent = kw["parent"]
        
        if parent is not None:
            obpolygon.parent = parent        
        #bpy.context.scene.objects.active = obpolygon
        obpolygon.select_set(True)
        self.setObjectActive (obpolygon)  

        if smooth:
            bpy.ops.object.shade_smooth()
        else:
            bpy.ops.object.shade_flat()
        if pt:
            bpy.context.object.show_wire = True
            #obpolygon.empty_display_type = 'WIRE'
        if type(material) is bool :
            doMaterial = material        
        if doMaterial:
            if material is None or type(material) is bool :
                mat = self.addMaterial("mat_"+name,color)
            else :
                mat = self.getMaterial(material)
            self.setOneMaterial(obpolygon,mat)
        return obpolygon,polygon

    def updateMesh(self, mesh, vertices=None,faces=None, smooth=True,**kw):
        # must delete the mesh data first or add vert/face
        # Delete all geometry from the object.
        # Select the object
        togleDs = False
        mesh = self.checkIsMesh(mesh)
        mesh.update()
        bm = bmesh.new()
#        bm = bmesh.from_edit_mesh(mesh)
        print (mesh,type(mesh))
        #should compare newV and curV mnumber
        obj = self.getObjectFromMesh(mesh)
        self.setObjectActive (obj)  
        #bpy.context.scene.objects.active = obj
        #bpy.context.scene.update()
        # The object need to be visible
        if obj.hide_viewport :
            togleDs = True
        self.toggleDisplay(obj,display=True)
        print ("object mode")
        # Add the mesh data.
        if faces is None or len(faces) == 0 :
            #faces = [[0,1,2],] *  len(mesh.faces)
            #me.faces.foreach_get(f,'vertices')
            faces = [list(f.vertices) for f in mesh.polygons]
        elif len(faces[0]) == 2 :
            newF = [(f[0],f[1],f[1]) for f in faces]
            faces = newF
#        if self.usenumpy :
#            print (type(faces),faces)
#            faces=numpy.array(faces,"int").tolist()
        if len(faces) and len(faces[0]):
            if type(faces[0][0]) != int:        
                if not self.usenumpy :
                    faces=[ [int(f[0]),int(f[1]),int(f[2])] for f in faces ]  
            if isinstance(faces,numpy.ndarray) and type(faces[0][0]) == numpy.int32:
                faces = numpy.array(faces,"int").tolist()
        #mesh.from_pydata(vertices, [], faces) 
        if vertices is not None :
            bvs = [bm.verts.new(c) for c in vertices]   
            bm.verts.index_update()
        nov=False    
        if faces is not None and len(faces) :
            for face in faces :
                vv=[]
                if face is None or not len(face) : 
                    continue
                nov=False 
                for v in face :
                    if v < len(bvs):
                        vv.append(bvs[v])
                    else :
                        nov=True
                if nov:
                    continue
                try :
                    bm.faces.new(vv)
                except :
                    continue
        if vertices is None and faces is None :
            bm.free()
            bm = bmesh.from_edit_mesh(mesh)
#        bmesh.update_edit_mesh(bpy.context.object.data)
        bm.to_mesh(mesh)
        bm.free()
        # smooth 
        mesh.update()
        if smooth:
            bpy.ops.object.shade_smooth()
        else:
            bpy.ops.object.shade_flat()
        if togleDs :
            self.toggleDisplay(obj,display=False)


    def DecomposeMesh(self,poly,edit=True,copy=True,tri=True,transform=True,**kw):
        print ("what is the poly",poly)
        if poly is None :
            return [],[],[]
        ob = self.getObject(poly)
        print ("Decompos Mesh",poly,ob)
        mesh = self.getMeshFrom(ob)
        print ("Found mesh ",mesh)
        vertices = self.getMeshVertices(mesh)
        faces = self.getMeshFaces(mesh)
        vnormals = self.getMeshNormales(mesh)
        if type(ob) == bpy.types.Mesh:
            ob = self.getObjectFromMesh(ob)
        if transform :
            #node = self.getNode(mesh)
            #fnTrans = om.MFnTransform(mesh)
#            ob = self.getObject(poly)
#            bpy.context.scene.objects.active = ob
#            ob = bpy.context.object
            mat = self.getObjectMatrix(ob)#ob.matrix_world #cache problem ?
            #no transpose, from blender matrix is column major
            #mat.transpose()# numpy.array(mmat).transpose()#self.m2matrix(mmat)
            #print (ob,poly,mat)
            vertices = self.ApplyMatrix(vertices,mat)
        if "fn" in kw and kw["fn"] :
            fnormals = self.getMeshFaceNormales(mesh)
            return faces,vertices,vnormals,fnormals
        else :
            return faces,vertices,vnormals   

    def addToGroup(self,master,objects,group=None):
        #master = self.getObject(master) 
        #if group == None:
        #    group = self.getName(master)+"_gr"
        if group is None :
            master = self.getObject(master) 
            namegroup = self.getName(master)+"_gr"
            if not namegroup in bpy.data.collections: 
                group = bpy.data.collections.new(namegroup)
                group.objects.link(master)
            else :
                group = bpy.data.collections[namegroup]
        #    if not len(master.users_group):
        #        group.objects.link(master)
        for o in objects :
            o =  self.getObject(o)
            try :
                group.objects.link(o)
                #self.setObjectActive(o)
                #bpy.ops.object.collection_link(collection=namegroup) 
                #group.objects.link(o)
            except:
                print ("in group already",o,o.name)
            chs = self.getChilds(o)
            self.addToGroup(master,chs,group=group)    

    def drawQuestion(self,*args,**kw)            :
        return False
 
    def setCurrentSelections(self, listeobj):
#        if obj is None :
        bpy.ops.object.select_all(action='DESELECT')
        for o in listeobj:
            o.select_set(True)

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
            self.setObjectActive (spline)
            bpy.ops.object.duplicate_move()
            spline_clone = self.getObjectActive()#bpy.context.object
            spline_clone.name = "exd"+spline.name
            curveData = spline_clone.data
            curveData.bevel_object = shape
            return spline_clone,shape,spline_clone
        curveData.bevel_object = shape
        return spline,shape

        #bpy.context.object.show_in_front = True
    def armature(self,name,x,hR=0.5,tR=0.5,dDist=0.4,roll=10,scn=None,root=None,
                 listeName=None):
        if scn is None:
            scn = self.getCurrentScene()
        res = bpy.ops.object.add(type='ARMATURE')
        armObj = bpy.context.object
        armObj.name = name
        bpy.context.object.show_in_front = True
        armData = armObj.data
        armData.name = name
        #armData.use_auto_ik=bool(1) standard IK 
        #armData.use_deform_vertex_groups=bool(1) DEPRECATED ?
        bpy.ops.object.mode_set(mode='EDIT')
        if listeName is not None :
            bones=[]
            for i in range(len(x)-1):
                b=self.addBone(i,armData,x[i],x[i+1],
                    hR=hR,tR=tR,dDist=dDist,roll=roll,name=listeName[i],editMode=False)
                bones.append(b)
                print ("one bone")
#            bones = [self.addBone(i,armData,x[i],x[i+1],
#                    hR=hR,tR=tR,dDist=dDist,roll=roll,name=listeName[i]) for i in range(len(x)-1)]
        else :
            bones=[]
            for i in range(len(x)-1):
                b=self.addBone(i,armData,x[i],x[i+1],
                    hR=hR,tR=tR,dDist=dDist,roll=roll,editMode=False)
                bones.append(b)
                print ("one bone")
#            bones = [self.addBone(i,armData,x[i],x[i+1],
#                    hR=hR,tR=tR,dDist=dDist,roll=roll) for i in range(len(x)-1)]
                    
        bpy.ops.object.mode_set(mode='OBJECT')
        #for bone in armData.bones.values():
        #   #print bone.matrix['ARMATURESPACE']
        #   print bone.parent, bone.name
        #   print bone.options, bone.name
#        armData.update()
#        self.addObjectToScene(scn,armObj,parent=root)
        #scn.objects.link(armObj)
        return armObj,bones
        
    def getObjectMatrix(self,obj):
        t = obj.location
        s = obj.scale
        mat_rot = obj.rotation_euler.to_matrix().to_4x4()
        scalem = [[s[0],0.,0.],[0.,s[1],0.],[0.,0.,s[2]]]
        mat_scale = mathutils.Matrix(scalem).to_4x4()
        mat_trans = mathutils.Matrix.Translation(t)
        mat = mat_trans @ mat_rot @ mat_scale
        return mat


    def newInstance(self,name,ob,location=None,hostmatrice=None,
                    matrice=None,parent=None,**kw): 
        dupligroup = False
        mesh = None
        for me in bpy.data.meshes:
            if ob == me :
                mesh = ob
                break
        if mesh is None :
            ob=self.getObject(ob)
            childs = self.getChilds(ob)
            if len(childs) : #need to group and then dupligroup
                dupligroup = True
                #select paren and children
                #should actually get recursvly all childs not first level!
                #childs.extend([ob]) #so we can translate out of he view the masterinstance
                self.setCurrentSelections([ob])#theses object have to be visible to make it work!
                #                print ("selected childs",childs)
                #check if the group exist
                #bpy.ops.collection.create(name="group1")
                #bpy.ops.object.move_to_collection(collection_index=0, is_new=True, new_collection_name="Collection 2")
                namegroup = self.getName(ob)+"_gr"
                if not namegroup in bpy.data.collections: 
                    group = bpy.data.collections.new(namegroup)
                    bpy.context.scene.collection.children.link(group)
                    #bpy.ops.object.move_to_collection(collection_index=0,is_new=True, new_collection_name=namegroup)
                    #bpy.ops.group.create(name=namegroup)
                    #print ("group  created",namegroup)
                    self.addToGroup(ob,childs,group=group)  
                #bpy.ops.object.collection_link(collection='HIV1_ENV_4nco_0_1_1_gr')                   
                #create the instance
                #bpy.ops.outliner.collection_instance()
                bpy.ops.object.collection_instance_add(collection=namegroup, location=(0, 0, 0))
                #bpy.ops.object.collection_instance_add(name=name, collection=namegroup, align='WORLD', location=(0.0, 0.0, 0.0), rotation=(0.0, 0.0, 0.0))
                #bpy.ops.object.group_instance_add(group=namegroup,location=[0,0,0],rotation=[0,0,0])#'INVOKE_DEFAULT'?ix400_n25MeshsParent_gr
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
                mesh=ob.data
                OBJ=bpy.data.objects.new(name,mesh)
                #bpy.ops.object.add_named(linked=False, name=name)
                bpy.context.view_layer.active_layer_collection.collection.objects.link(OBJ)
                self.setObjectActive  (OBJ)        
                if parent is not None:
                    OBJ.parent = parent
        else :
            OBJ=bpy.data.objects.new(name,mesh)
            #bpy.ops.object.add_named(linked=False, name=name)
            bpy.context.view_layer.active_layer_collection.collection.objects.link(OBJ)
            self.setObjectActive  (OBJ)        
            if parent is not None:
                OBJ.parent = parent
        #print ("OBJ created",OBJ) 
        #set the instance matrice
        transpose = False
        if "transpose" in kw :
            transpose = kw["transpose"]
            #        print ("set objecMatrix")
            #        if matrice is not None and hostmatrice is None :
        
        if location is not None :
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
                        transpose=False,globalT=True,dupliVert=True,**kw):
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
                self.setObjectActive  (o)
                bpy.context.object.instance_type = 'FACES'
                #o.dupli_type = "FACES"
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
                #o.dupli_type = "VERTS"
                self.setObjectActive (o)
                bpy.context.object.instance_type = 'VERTS'
                bpy.context.object.use_instance_vertices_rotation = True
                #o.use_dupli_vertices_rotation = True
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

    def toggleDisplay(self,ob,display=True,child=True):
        if type(ob) == str : obj=self.getObject(ob)
        elif type(ob) is list :
            [self.toggleDisplay(o,display=display) for o in ob]
            return
        else : 
            obj=ob
        if obj is None :
            return            
        obj.hide_viewport=not display#bpy.context.object.hide_viewport = False
        obj.hide_render=not display#bpy.context.object.hide_render = False
        if child :
            chs = self.getChilds(obj)
            self.toggleDisplay(chs,display=display)

    def toggleXray(self,object,xray):
        obj = self.getObject(object)
        if obj is None :
            return
        obj.show_in_front = xray

    def setLayers(self, scn, layers):
        """
        Set the layers of a scene or an object, expects a list of integers
        """
        return
        if scn is None :
            return
        chs = self.getChilds(scn)
        for ch in chs:
            self.setLayers(ch,layers)
        for ind in layers:
            #bpy.context.object.
            scn.layers[ind] = True
        for unset in set(range(20)).difference(layers):
            scn.layers[unset] = False

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
                cloud.instance_type = "VERTS"
        return cloud        
        