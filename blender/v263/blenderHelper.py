
"""
    Copyright (C) <2010>  Autin L. TSRI
    
    This file git_upy/blender/v263/blenderHelper.py is part of upy.

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
from upy.blender.v262.blenderHelper import blenderHelper as Helper
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
        if type(mesh) == bpy.types.Object:
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
    def getObjectMatrix(self,obj):
        t = obj.location
        s = obj.scale
        mat_rot = obj.rotation_euler.to_matrix().to_4x4()
        scalem = [[s[0],0.,0.],[0.,s[1],0.],[0.,0.,s[2]]]
        mat_scale = mathutils.Matrix(scalem).to_4x4()
        mat_trans = mathutils.Matrix.Translation(t)
        mat = mat_trans * mat_rot * mat_scale
        return mat
        
    def setObjectMatrix1(self,o,matrice=None,hostmatrice=None,transpose = False):
        if matrice is None and hostmatrice is None :
            return
        if type(o) == str : obj=self.getObject(o)
        else : obj=o
        #matrix(16,)
        if matrice is not None :
            mat = matrice#  = mat#numpy.array(matrice)
            #m=matrice.reshape(4,4)
            #if transpose : m = m.transpose()
            #mat=m.tolist()
#            print (o,obj.name,matrice,mat,type(mat))            
            blender_mat=mathutils.Matrix(mat) #from Blender.Mathutils
        elif hostmatrice is not None :
            blender_mat=hostmatrice
#        if transpose :  
#        blender_mat.transpose()
        print (blender_mat)
        obj.matrix_world = blender_mat
        #Sets the object's matrix and updates its transformation. 
        #If the object has a parent, the matrix transform is relative to the parent.

    def setObjectMatrix(self,o,matrice=None,hostmatrice=None,transpose = False):
        if matrice is None and hostmatrice is None :
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
#            print (o,obj.name,matrice,mat,type(mat))            
            blender_mat=mathutils.Matrix(mat) #from Blender.Mathutils
        elif hostmatrice is not None :
            blender_mat=hostmatrice
        #if transpose :  
        #blender_mat.transpose()#change nothing ?
#        print (blender_mat)
        if transpose : 
            blender_mat.transpose()
        obj.matrix_world = blender_mat
        #Sets the object's matrix and updates its transformation. 
        #If the object has a parent, the matrix transform is relative to the parent.
#
    def setTranslation(self,obj,pos=[0.0,0.,0.],**kw):
        obj=self.getObject(obj)
        obj.location = (pos[0],pos[1],pos[2])


    def Cylinder(self,name,radius=1.,length=1.,res=16,pos = None,parent = None,**kw):
        #import numpy
#        diameter = radius#2*radius??
        res = bpy.ops.mesh.primitive_cylinder_add(vertices=res, radius=radius, 
                        depth=length)#, cap_ends=True)
        obj = bpy.context.object
        obj.name = name
        mesh = obj.data
        mesh.name = "mesh_"+name

        if pos != None : obj.location = (float(pos[0]),float(pos[1]),float(pos[2]))
        if parent is not None:
            obj.parent = self.getObject(parent)
        return obj,mesh

    
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
            obpolygon.select = True
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
        if pt:
            obpolygon.draw_type = 'WIRE'
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


    def updateFaces(self,mesh,faces):
        # eekadoodle prevention
        for i in range(len(faces)):
            if not faces[i][-1]:
                if faces[i][0] == faces[i][-1]:
                    faces[i] = [faces[i][1], faces[i][2], faces[i][3], faces[i][1]]
                else:
                    faces[i] = [faces[i][-1]] + faces[i][:-1]
        if len(mesh.polygons) == len(faces):
            for i in range(len(faces)):
                mesh.polygons[i].vertices = faces[i]
        elif len(mesh.polygons) < len(faces):
            start_faces = len(mesh.polygons)
            mesh.polygons.add(len(faces))
            for i in range(len(faces)):
                mesh.polygons[i].vertices = faces[i]
        else :
            end_faces = len(faces)
            #mesh.faces.add(len(faces))
            for i in range(len(faces)):
                mesh.polygons[start_faces + i].vertices = faces[i]
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

    #maybe use bm = bmesh.from_edit_mesh(mesh)
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
        bpy.context.scene.objects.active = obj
        bpy.context.scene.update()
        # The object need to be visible
        if obj.hide :
            togleDs = True
        self.toggleDisplay(obj,display=True)

#        bpy.ops.object.mode_set(mode='EDIT')
#        bpy.ops.mesh.select_all(action='SELECT')
#        bpy.context.scene.update()
        #[‘VERT’, ‘EDGE’, ‘FACE’, ‘ALL’, ‘EDGE_FACE’, ‘ONLY_FACE’, ‘EDGE_LOOP’]
        #[‘VERT’, ‘EDGE’, ‘FACE’, ‘EDGE_FACE’, ‘ONLY_FACE’],
#        print (vertices != None,faces != None)
#        if vertices != None and faces is None :
#            bpy.ops.mesh.delete(type='VERT')
#        elif vertices is None and faces != None :
#            bpy.ops.mesh.delete(type='FACE')
#        elif vertices != None and faces != None :
#            print (len(vertices),len(faces))
#            bpy.ops.mesh.delete()#type='ALL'
#            print ("OK")
#        else :
#            bpy.ops.object.mode_set(mode='OBJECT')
#            return
        # Must be in object mode for from_pydata to work
#        bpy.ops.object.mode_set(mode='OBJECT')
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

    def colorMaterial(self,mat,color):
        #mat input is a material name or a material object
        #color input is three rgb value array
        print ("mat ",mat,color)
        if type(mat) is str or type(mat) is bytes : 
            mat = bpy.data.materials.get(mat)
        ncolors=self.convertColor(color,toint=False)  #blenderColor(color)
        mat.diffuse_color.r = ncolors[0]
        mat.diffuse_color.g = ncolors[1]
        mat.diffuse_color.b = ncolors[2]

#    
    def color_per_vertex(self,mesh,colors,perVertex=True,perObjectmat=None,pb=False,
                    facesSelection=None,faceMaterial=False):
        mesh=self.getMesh(mesh)
        if len(mesh.materials):
            mesh.materials[0].use_vertex_color_paint = True
        #bpy.ops.paint.vertex_paint_toggle()
        if type(colors[0]) is float or type(colors[0]) is int and len(colors) == 3 :
           colors = [colors,]
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
               mat.diffuse_color = (colors[0][0],colors[0][1],colors[0][2])
        mesh.update()
        #self.restoreEditMode(editmode)
#        try :
#            bpy.ops.paint.vertex_paint_toggle()
#        except :
#            print ("v context problem")
        return True
 
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

    def getMeshFaceNormales(self,poly,selected = False):
#        editmode = self.toggleEditMode()
        mesh = self.checkIsMesh(poly)
        mfaces = mesh.polygons
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
        return mesh.polygons[faceindice].edge_keys    
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
#        return f.vertices#difference with f.vertices_raw?s
        if len(f.vertices) == 3:
            return [f.vertices[0], f.vertices[1], f.vertices[2]]
        elif len(f.vertices) == 4:
            return [f.vertices[0], f.vertices[1], f.vertices[2],f.vertices[3]]

    def getMeshFaces(self, poly, selected = False):
        mesh = self.checkIsMesh(poly)
        mfaces = mesh.polygons
        if selected :
            mfaces_indice = [face.index for face in mesh.polygons
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
        mesh.polygons[index].select = select
    
    def selectFaces(self, obj, indices, select=True):
        editmode=self.toggleEditMode()
        curr = bpy.context.tool_settings.mesh_select_mode
        bpy.context.tool_settings.mesh_select_mode = (curr[0], curr[1], True)
        
        mesh = self.checkIsMesh(obj)
        for ind in indices:
            if ind >= len(mesh.polygons):
                continue
            mesh.polygons[ind].select = select
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

#    def DecomposeMesh(self,poly,edit=True,copy=True,tri=True,transform=True):
#        mesh = self.getMeshFrom(poly)
#        vertices = self.getMeshVertices(mesh)
#        faces = self.getMeshFaces(mesh)
#        vnormals = self.getMeshNormales(mesh)
#
#        if transform :
#            #node = self.getNode(mesh)
#            #fnTrans = om.MFnTransform(mesh)
#            ob = self.getObject(poly)
##            bpy.context.scene.objects.active = ob
##            ob = bpy.context.object
#            mat = self.getObjectMatrix(ob)#ob.matrix_world #cache problem ?
#            mat.transpose()# numpy.array(mmat).transpose()#self.m2matrix(mmat)
#            #print (ob,poly,mat)
#            vertices = self.ApplyMatrix(vertices,mat)
##        if edit and copy :
##            self.getCurrentScene().SetActiveObject(poly)
##            c4d.CallCommand(100004787) #delete the obj       
#        return faces,vertices,vnormals

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

#    def rotation_matrix(self,angle, direction, point=None,trans=None):
#        """
#        Return matrix to rotate about axis defined by point and direction.
#    
#        """
#        if self._usenumpy:
#            return Helper.rotation_matrix(angle, direction, point=point,trans=trans)
#        else :            
#            direction = self.FromVec(direction[:3])
#            direction.normalize()
#            m = mathutils.Matrix.Rotation(angle,4,direction)
#            M = m.copy()
#            if point is not None:
#               point = self.FromVec(point[:3]) 
#               M.translation = point - (point * m)
#            if trans is not None :
#               M.translation = trans
#            return M        
        
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

    def armature(self,name,x,hR=0.5,tR=0.5,dDist=0.4,roll=10,scn=None,root=None,
                 listeName=None):
        if scn is None:
            scn = self.getCurrentScene()
        res = bpy.ops.object.add(type='ARMATURE')
        armObj = bpy.context.object
        armObj.name = name
        armObj.show_x_ray = True
        armData = armObj.data
        armData.name = name
        armData.use_auto_ik=bool(1)
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
        
#==============================================================================
# import / expor / read load / save
#==============================================================================

    def read(self,filename,**kw):
        fileName, fileExtension = os.path.splitext(filename)
        if fileExtension == ".dae" :
            bpy.ops.wm.collada_import(filepath=filename)#, filter_blender=False, filter_image=False, 
#                                      filter_movie=False, filter_python=False, filter_font=False, 
#                                      filter_sound=False, filter_text=False, filter_btx=False, 
#                                      filter_collada=True, filter_folder=True, filemode=8, 
#                                      display_type='FILE_DEFAULTDISPLAY')
    
#    def write(self,listObj,**kw):
#        pass
#                

