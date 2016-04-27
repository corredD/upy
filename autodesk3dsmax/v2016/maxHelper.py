
"""
    Copyright (C) <2010>  Autin L. TSRI
    
    This file git_upy/autodesk3dsmax/v2015/maxHelper.py is part of upy.

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
@author: Ludovic Autin - ludovic.autin@gmail.com
"""
import sys, os, os.path, struct, math, string
from math import *
import random
import gzip
import re
from struct import pack
#import numpy    
from types import StringType, ListType

#3dsmax import
import MaxPlus
import _MaxPlus

              
class STDOutHook(object):
    def __init__(self, filename = None):
        self.log = None
        self.filename = None
        if filename is not None : self.filename = filename
        
    def write(self, data):
        # py engine adds a newline at the end of the data except if\n" +
        # the statement was ended by a comma.\n" +
        data = '' if data == '\\n' else data
        data = '' if data == '\n' else data
        if data != '':
            MaxPlus.Core.WriteLine(str(data))            
            if self.filename is not None :
                MaxPlus.Core.WriteLine("logging filename "+str(len(data)))
                #f = open(self.filename,"w")
                #try :
                #    f.write(str(data))
                #finally :
                #    f.close()
                #    MaxPlus.Core.WriteLine("closing")
                with open(self.filename,"w") as f :
                    #MaxPlus.Core.WriteLine("with "+str(f))
                    f.write(str(data))
                MaxPlus.Core.WriteLine("done")
            if self.log is not None :
                MaxPlus.Core.WriteLine("logging log "+str(self.log))
                self.log.write(str(data))
                self.log.flush()
        return None
    


#base helper class
from upy import hostHelper
if hostHelper.usenumpy:
    import numpy

#from upy.hostHelper import Helper
from upy.autodesk3dsmax.v2015.maxHelper import maxHelper as Helper

class maxHelper(Helper):
    
    POLYGON = "TriObj"#TriObj
    MESH = MaxPlus.Mesh

    def __init__(self,master=None,**kw):
        Helper.__init__(self)
        
    def toggleDisplay(self,ob,display,**kw):
        display = bool(display)
        ob = self.getObject(ob)
        if ob is None :
            print "ob is None return"
            return
        if int(display) :
            hide = False
            #ob.Hide=0
            #_MaxPlus.INode_Hide(ob, False)
            ob.UnhideObjectAndLayer()
        else :
            hide = True
            ob.Hide=1
            #_MaxPlus.INode_Hide(ob, True)
        ch = self.getChilds(ob)
        for c in ch :
            self.toggleDisplay(c,display)
            
    def createsNmesh(self,name,vertices,normal,faces,color=[[1,0,0],],smooth=True,
                     material=None,proxyCol=False,**kw):
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
        obj = self.createObject("geom", "mesh")
        #node = self.createNode(obj,name)
        #node,obj = self.createObjectWithNode(MaxPlus.SuperClassIdConstants.GeomObject, "mesh", name)
        tri = MaxPlus.TriObject._CastFrom(obj)
        mesh = tri.GetMesh() 

        nV=len(vertices)
        mesh.SetNumVerts(nV)
        [ mesh.SetVert(i, self.FromVec(v)) for i,v in enumerate(vertices)]
        
        if not faces is None:
            nfaces = self.triangulateFaceArray(faces)
            nF=len(nfaces)
            mesh.SetNumFaces(nF)
            [ mesh.GetFace(i).SetVerts(int(f[0]), int(f[1]), int(f[2])) for i,f in enumerate(nfaces)] 

        #mesh.BuildStripsAndEdges()?
        mesh.InvalidateGeomCache()
        mesh.InvalidateTopologyCache()
    
        if len(color) == 3 :
            if type(color[0]) is not list :
                color = [color,]                         
        #mesh.SetnumCVerts
        node = self.createNode(obj,name)
        node.SetDisplayByLayer(False)
        if faces == None or len(faces) == 0 or len(faces[0]) < 3 :
            print node,type(node),obj,type(obj),tri,type(tri)
            #print (hasattr("VertTicks",node),hasattr("VertTicks",obj),hasattr("VertTicks",tri))
            node.SetVertTicks(True)#this will show the vertices of the mesh
        #if color is not None and len(color) > 1:
        #    self.color_mesh_perVertex(mesh,color)
        doMaterial = True
        if type(material) is bool :
            doMaterial = material        
        if doMaterial:
            if material == None :
                if len(name.split("_")) == 1 : splitname = name
                else :
                    splitname = name.split("_")[1]  
                self.assignNewMaterial( "mat_"+name, color[0],'lambert' ,node)
            else :
                self.assignMaterial(node,material)
        if "parent" in kw :
            parent = kw["parent"]
            self.reParent(node,parent)
        #ad the smooth mod
        if smooth:
            self.mesh_autosmooth(node)
        return node,tri#,outputMesh     
        
    def getMeshVertices(self,poly,transform=False,selected = False):
        #what if already a mesh
        if type(poly) is str or type(poly) is unicode:
            name = poly
            #poly = self.getObject(name)
        else :
            name = self.getName(poly)       
        node = self.getObject(name)
        print ("get ",name,poly,node)        
        m = node.GetWorldTM()
        if not isinstance(poly, MaxPlus.Mesh) :            
            #shaded ?
            mesh = self.getMesh(node)
            print "getMeshVertice ",name,poly,node,mesh           
        else :
            mesh = poly
        print "getMeshVertices mesh", mesh,type(mesh),poly,type(poly)
        if  mesh is None:
            return []
        nv = mesh.GetNumVertices()
        vertices=[]
        for i in xrange(nv):
            v=mesh.GetVertex(i)
            if transform :
                v = m.PointTransform(v)
            vertices.append(self.ToVec(v))
        return vertices

    def oneCylinder(self,name,head,tail,radius=None,instance=None,material=None,
                    parent = None,color=None):
        #name = self.checkName(name)
        laenge,wsz,wz,coord=self.getTubeProperties(head,tail)
        #print ("oneCylinder instance",name,instance)
        ainstance=False
        try :
            ainstance = (instance == None)
        except :
            pass
        if ainstance : 
            obj = self.Cylinder(name)[0]#node , obj
        else : 
            obj = self.newInstance(name,instance,parent=parent)#node ,obj
        if radius is None :
            radius= 1.0
        print ("oneCylinder ",obj)
        #obj = obj[0]#self.getObject(obj)
        #print ("omeCylinder ",obj)        
        m=obj.GetWorldTM()
        m.ToIdentity()
        #SetWorldScale? which is actually working
        #_MaxPlus.Matrix3_Scale(m,self.FromVec([radius,radius,laenge]))
        m.SetToScale(self.FromVec([radius,radius,laenge]))
        #m.SetScale(self.FromVec([radius,radius,laenge]))#access m.Scale
        m.RotateY(wz)    
        m.RotateZ(wsz)    
        m.Translate(self.FromVec(tail))      #or head-tail ? SetTranslate
        obj.SetWorldTM(m)
        #self.translateObj(name,coord)
        #self.rotateObj(name,[0.,wz,wsz])
        #self.scaleObj(name,[radius, radius, laenge])
        amat = True
        try :
            amat = material != None
        except :
            pass
        if amat :
            self.assignMaterial(obj,material)
        elif color is not None :
            mats = self.getMaterialObject(obj)
            if not mats :
                mat = self.addMaterial("mat_"+name,color)
                self.assignMaterial(obj,mat)
            else :
                self.colorMaterial(mats[0],color)
        return obj    

    def updateOneCylinder(self,name,head,tail,radius=None,material=None,color=None):
        laenge,wsz,wz,coord=self.getTubeProperties(head,tail)
        obj = self.getObject(name)
        if radius is None :
            radius= 1.0        
        m=obj.GetWorldTM()
        m.ToIdentity()
        #SetWorldScale? which is actually working
        #_MaxPlus.Matrix3_Scale(m,self.FromVec([radius,radius,laenge]))
        m.SetToScale(self.FromVec([radius,radius,laenge]))
        #m.SetScale(self.FromVec([radius,radius,laenge]))#access m.Scale
        m.RotateY(wz)    
        m.RotateZ(wsz)    
        m.Translate(self.FromVec(tail))      #or head-tail ? SetTranslate
        obj.SetWorldTM(m)

        amat = True
        try :
            amat = material != None
        except :
            pass
        if amat :
            self.assignMaterial(obj,material)
        elif color is not None :
            mats = self.getMaterialObject(obj)
            if not mats :
                mat = self.addMaterial("mat_"+name,color)
                self.assignMaterial(obj,mat)
            else :
                self.colorMaterial(mats[0],color)

    def instancesSphere(self,name,centers,radii,meshsphere,colors,scene,parent=None):
        sphs=[]
        mat = None
        amat = True
        if len(colors) == 1:
            mat = self.retrieveColorMat(colors[0])
            try :
                amat = mat != None
            except :
                pass
            if amat:        
                mat = self.addMaterial('mat_'+name,colors[0])
        try :
            amat = mat != None
        except :
            pass
        print ("instances with ",radii)
        for i in range(len(centers)):
            sp = self.newInstance(name+str(i),meshsphere)
            sphs.append(sp)
            #local transformation ?
            self.scaleObj(sp,[float(radii[i]),float(radii[i]),float(radii[i])])
            self.translateObj(sp,centers[i])
            if not amat : mat = self.addMaterial("matsp"+str(i),colors[i])
            self.assignMaterial(name+str(i),mat)#mat[bl.retrieveColorName(sphColors[i])]
            self.addObjectToScene(scene,sphs[i],parent=parent)
        return sphs

    def updateInstancesSphere(self,name,sphs,centers,radii,meshsphere,
                        colors,scene,parent=None,delete=True):
        print ("instances with ",radii)        
        mat = None
        amat = True
        if len(colors) == 1:
            mat = self.retrieveColorMat(colors[0])
            try :
                amat = mat != None
            except :
                pass
            if amat and colors[0] is not None:        
                mat = self.addMaterial('mat_'+name,colors[0])
        try :
            amat = mat != None
        except :
            pass
        for i in range(len(centers)):
            if len(radii) == 1 :
                rad = radii[0]
            elif i >= len(radii) :
                rad = radii[0]
            else :
                rad = radii[i]            
            if i < len(sphs):
                self.scaleObj(sphs[i],[float(rad),float(rad),float(rad)])
                self.translateObj(sphs[i],centers[i])
                if not amat :
                    if colors is not None and i < len(colors) and colors[i] is not None : 
                        mat = self.addMaterial("matsp"+str(i),colors[i])
                if colors is not None and i < len(colors) and colors[i] is not None : 
                    self.colorMaterial(mat,colors[i])
                self.toggleDisplay(sphs[i],True)
            else :
                sp = self.newInstance(name+str(i),meshsphere)
                sphs.append(sp)
                #local transformation ?
                self.translateObj(sp,centers[i])
                self.scaleObj(sp,[float(rad),float(rad),float(rad)])
                if not amat :
                    if colors is not None and  i < len(colors) and colors[i] is not None : 
                        mat = self.addMaterial("matsp"+str(i),colors[i])
                self.assignMaterial(name+str(i),mat)#mat[bl.retrieveColorName(sphColors[i])]
                self.addObjectToScene(scene,sp,parent=parent)
                
        if len(centers) < len(sphs) :
            #delete the other ones ?
            for i in range(len(centers),len(sphs)):
                if delete : 
                    obj = sphs.pop(i)
                    print "delete",obj
                    self.deleteObject(obj)
                else :
                    self.toggleDisplay(sphs[i],False)
        return sphs
            