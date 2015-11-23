
"""
    Copyright (C) <2010>  Autin L. TSRI
    
    This file git_upy/examples/export_collada.py is part of upy.

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
Created on Wed Dec  3 22:08:01 2014

@author: ludo
"""
MAYA=False
import sys
import numpy
import math
if MAYA:
    sys.path.append("/Users/ludo/Library/Preferences/Autodesk/maya/2015-x64/plug-ins/MGLToolsPckgs")
    sys.path.append("/Users/ludo/Library/Preferences/Autodesk/maya/2015-x64/plug-ins/MGLToolsPckgs/PIL")
    #maya standalone special
    import maya.standalone
    maya.standalone.initialize()
    #load plugin
    import maya
    maya.cmds.loadPlugin("fbxmaya")

import upy
helper = upy.getHelperClass()()
if MAYA:
    helper.read("/Users/ludo/DEV/autopack_git/autoPACK_database_1.0.0/geometries/HIV1_capsid_3j3q_Rep_Maker_0_1_0.fbx")

def instancesToCollada(self,parent_object,collada_xml=None,instance_node=True,**kw):
    try :
        from upy.transformation import decompose_matrix
        from collada import Collada
        from collada import material
        from collada import source
        from collada import geometry
        from collada import scene
    except :
        return            
    inst_parent=parent_object#self.getCurrentSelection()[0]
    ch=self.getChilds(inst_parent)
    transpose=True
    if "transpose" in kw :
        transpose = kw["transpose"]
    #instance master
    if "mesh" in kw and kw["mesh"] is not None:
        inst_master = kw["mesh"]
        f,v,vn = self.DecomposeMesh(kw["mesh"],edit=False,copy=False,tri=True,
                                transform=False)
    else :
        inst_master = self.getMasterInstance(ch[0])
        print "master is ",inst_master
        #grabb v,f,n of inst_master
        f,v,vn = self.DecomposeMesh(inst_master,edit=False,copy=False,tri=True,
                                transform=False)
        #special case when come from x-z swap 
#        v=[[vv[2],vv[1],vv[0]] for vv in v] # go back to regular
        #-90degree rotation onY 
        mry90 = self.rotation_matrix(-math.pi/2.0, [0.0,1.0,0.0])#?
        v=self.ApplyMatrix(v,mry90)#same for the normal?
        vn=self.ApplyMatrix(vn,mry90)#same for the normal?
    iname  = self.getName( inst_master )       
    pname  = self.getName( inst_parent ) 
    if collada_xml is None:
        collada_xml = Collada()
        collada_xml.assetInfo.unitname="centimeter"
        collada_xml.assetInfo.unitmeter=0.01
    mat = self.getMaterialObject(inst_master)
    if len(mat) :
        mat = mat[0]
    props = self.getMaterialProperty(mat,color=1)#,specular_color=1)
    print "colors is ",props
    effect = material.Effect("effect"+iname, [], "phong", 
                             diffuse=[props["color"][0],props["color"][1],props["color"][2],1.0])
#                                 specular = props["specular_color"])
    mat = material.Material("material"+iname, iname+"material", effect)
    collada_xml.effects.append(effect)
    collada_xml.materials.append(mat)
    matnode = scene.MaterialNode(iname+"material"+"ref", mat, inputs=[])    
    #the geom
    #invert Z ? for C4D?
    vertzyx = numpy.array(v)#* numpy.array([1,1,-1])
    z,y,x=vertzyx.transpose()
    vertxyz = numpy.vstack([x,y,z]).transpose()#* numpy.array([1,1,-1])
    vert_src = source.FloatSource(iname+"_verts-array", vertxyz.flatten(), ('X', 'Y', 'Z'))
    norzyx=numpy.array(vn)
    nz,ny,nx=norzyx.transpose()
    norxyz = numpy.vstack([nx,ny,nz]).transpose()* numpy.array([1,1,-1])
    normal_src = source.FloatSource(iname+"_normals-array", norxyz.flatten(), ('X', 'Y', 'Z'))
    geom = geometry.Geometry(collada_xml, "geometry"+iname, iname, [vert_src,normal_src])# normal_src])
    input_list = source.InputList()
    input_list.addInput(0, 'VERTEX', "#"+iname+"_verts-array")
    input_list.addInput(0, 'NORMAL', "#"+iname+"_normals-array")
    #invert all the face 
    fi=numpy.array(f,int)#[:,::-1]
    triset = geom.createTriangleSet(fi.flatten(), input_list, iname+"materialref")
    geom.primitives.append(triset)
    collada_xml.geometries.append(geom)
    #the  noe
    #instance here ?
    #creae the instance maser node :
    if instance_node:
        master_geomnode = scene.GeometryNode(geom, [matnode])#doesn work ?
        master_node = scene.Node("node_"+iname, children=[master_geomnode,])#,transforms=[tr,rz,ry,rx,s])
    g=[]
    for c in ch :
        #collada.scene.NodeNode
        if instance_node:
            geomnode = scene.NodeNode(master_node)
        else :
            geomnode = scene.GeometryNode(geom, [matnode])
        matrix = self.ToMat(self.getTransformation(c))#.transpose()#.flatten() 
        if transpose:
            matrix = numpy.array(matrix).transpose()
        scale, shear, euler, translate, perspective=decompose_matrix(matrix)
        scale = self.getScale(c)
        p=translate#matrix[3,:3]/100.0#unit problem
        tr=scene.TranslateTransform(p[0],p[1],p[2])
        rx=scene.RotateTransform(1,0,0,numpy.degrees(euler[0]))
        ry=scene.RotateTransform(0,1,0,numpy.degrees(euler[1]))
        rz=scene.RotateTransform(0,0,1,numpy.degrees(euler[2]))
#        rx=scene.RotateTransform(-1,0,0,numpy.degrees(euler[0]))
#        ry=scene.RotateTransform(0,-1,0,numpy.degrees(euler[1]))
#        rz=scene.RotateTransform(0,0,1,numpy.degrees(euler[2]))
        s=scene.ScaleTransform(scale[0],scale[1],scale[2])
        #n = scene.NodeNode(master_node,transforms=[tr,rz,ry,rx,s])
#            gnode = scene.Node(self.getName(c)+"_inst", children=[geomnode,])
        n = scene.Node(self.getName(c), children=[geomnode,],transforms=[tr,rz,ry,rx,s]) #scene.MatrixTransform(matrix)[scene.MatrixTransform(numpy.array(matrix).reshape(16,))]
#            n = scene.Node(self.getName(c), children=[geomnode,],
#                           transforms=[scene.MatrixTransform(numpy.array(matrix).reshape(16,))]) #scene.MatrixTransform(matrix)[scene.MatrixTransform(numpy.array(matrix).reshape(16,))]
        g.append(n)
        
    node = scene.Node(pname, children=g)#,transforms=[scene.RotateTransform(0,1,0,90.0)])
    if "parent_node" in kw :
        kw["parent_node"].children.append(node)
        node = kw["parent_node"]
    if not len(collada_xml.scenes) :
        myscene = scene.Scene("myscene", [node])
        collada_xml.scenes.append(myscene)
        collada_xml.scene = myscene
    else :
        if "parent_node" not in kw :
            collada_xml.scene.nodes.append(node)
    if instance_node:
        collada_xml.nodes.append(master_node)
    return collada_xml




from collada import scene
node = scene.Node("HIV1_capside_3j3q_Rep_Med")
parent_object=helper.getObject("Pentamers")
mesh=None
if MAYA:
    mesh=helper.getObject("HIV1_capsid_3j3q_Rep_Med_Pent_0_1_0_1")
collada_xml=instancesToCollada(helper,parent_object,collada_xml=None,
                                      instance_node=True,parent_node=node,
                                      mesh=mesh,transpose=False)
parent_object=helper.getObject("Hexamers")
mesh=None
if MAYA:
    mesh=helper.getObject("HIV1_capsid_3j3q_Rep_Med_0_1_0")
collada_xml=instancesToCollada(helper,parent_object,collada_xml=collada_xml,
                                      instance_node=True,parent_node=node,
                                      mesh=mesh,transpose=False)
#collada_xml.scene.nodes
#collada_xml.write("/Users/ludo/DEV/autopack_git/autoPACK_database_1.0.0/geometries/HIV1_capside_3j3q_Rep_Med_0_2_1.dae")
collada_xml.write("/Users/ludo/DEV/cellPACK_data/cellPACK_database_1.1.0/geometries/HIV1_capside_3j3q_Rep_Med_0_2_1.dae")
#execfile("/Users/ludo/DEV/git_upy/examples/export_collada.py")
#import upy
#helper = upy.getHelperClass()()
#helper.read("/Users/ludo/DEV/autopack_git/autoPACK_database_1.0.0/geometries/HIV1_capside_3j3q_Rep_Med_0_2_1.dae")
#