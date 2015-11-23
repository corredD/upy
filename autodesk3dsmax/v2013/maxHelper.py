
"""
    Copyright (C) <2010>  Autin L. TSRI
    
    This file git_upy/autodesk3dsmax/v2013/maxHelper.py is part of upy.

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

from upy.hostHelper import Helper

class maxHelper(Helper):
    """
    The softimage helper abstract class
    ============================
        This is the softimage helper Object. The helper 
        give access to the basic function need for create and edit a host 3d object and scene.
    """
    
    SPLINE = "kNurbsCurve"
    INSTANCE = "dummy"
    
    POLYGON = "TriObj"#TriObj
    MESH = "mesh"

    EMPTY = "dummy"
    
    BONES="kJoint"
    PARTICULE = "kParticle"
    IK="kIkHandle"
#    msutil = om.MScriptUtil()

    pb = False
    pbinited = False
    host = "softimage"
    LIGHT_OPTIONS = {"Area" : "Light_Box.Preset","Sun" : "Infinite.Preset","Spot":"Spot.Preset"}
    
    def __init__(self,master=None,**kw):
        Helper.__init__(self)
        self.updateAppli = self.update
        self.Cube = self.box
        self.Box = self.box
        self.Geom = self.newEmpty
        self.IndexedPolygons = self.polygons
        self.Points = self.PointCloudObject
        self.host = "3dsmax"
        self.dicClassId = {
                      ###########GEOM######################
                      "cylinder":MaxPlus.ClassIds.Cylinder,
                      "poly":MaxPlus.ClassIds.Polyobj,
                      "patch":MaxPlus.ClassIds.Patchobj,
                      "nurbs":MaxPlus.ClassIds.Nurbsobj,
                      "epoly":MaxPlus.ClassIds.Epolyobj,
                      "box":MaxPlus.ClassIds.Boxobj,
                      "sphere":MaxPlus.ClassIds.Sphere,
                      "plane":MaxPlus.ClassIds.Plane,
                      "pyramide":MaxPlus.ClassIds.Pyramid,
                      "gsphere":MaxPlus.ClassIds.Gsphere,
                      "cone":MaxPlus.ClassIds.Cone,
                      "torus":MaxPlus.ClassIds.Torus,
                      "tube":MaxPlus.ClassIds.Tube,
                      "hedra":MaxPlus.ClassIds.Hedra ,
                      ###########ComplexeGeom######################
                      "bool":MaxPlus.ClassIds.Boolobj,
                      "loft":MaxPlus.ClassIds.Loftobj,
                      ###########CAM and Light######################
                      "simple_camera":MaxPlus.ClassIds.SimpleCam,
                      "camera":MaxPlus.ClassIds.Camera,
                      "light":MaxPlus.ClassIds.Light,
                      "omni":MaxPlus.ClassIds.OmniLight,
                      "dirlight":MaxPlus.ClassIds.DirLight,
                      "spot":MaxPlus.ClassIds.SpotLight,
                      ###########MESH And Polygons######################
                      "mesh":MaxPlus.ClassIds.Triobj,
                      "poly":MaxPlus.ClassIds.Polyobj,
                      "nurbs":MaxPlus.ClassIds.Nurbsobj,
                      ###########SHAPE######################
                      "loft":MaxPlus.ClassIds.Loftobj,
                      "text":MaxPlus.ClassIds.Text,
                      "shape":MaxPlus.ClassIds.Shape,
                      "ecurve":MaxPlus.ClassIds.EditableCvcurve,
                      #"spline":MaxPlus.Constants.SplineShapeClassId,
                      "spline3d":MaxPlus.ClassIds.Spline3d,
                      "circle":MaxPlus.ClassIds.Circle,
                      "rectangle":MaxPlus.ClassIds.Rectangle,
                      "arc":MaxPlus.ClassIds.Arc,
                      "dummy":MaxPlus.ClassIds.Dummy,
                      "system":MaxPlus.ClassIds.System,
                      "particule_system":MaxPlus.ClassIds.ParticleSys,
                      ###########MODIFIER######################
                      "smooth":MaxPlus.ClassIds.Smoothosm,
                      }
        self.create_fct = {
                        'animatable':MaxPlus.Factory.CreateAnimatable,
                        'atmosphere':MaxPlus.Factory.CreateAtmospheric,
                        'Gizmo':MaxPlus.Factory.CreateGizmoObject,
                        'boxGizmo':MaxPlus.Factory.CreateBoxGizmoObject,
                        'cylGizmo':MaxPlus.Factory.CreateCylGizmoObject,
                        'light': MaxPlus.Factory.CreateLight,
                        'dirlight':MaxPlus.Factory.CreateDirectionalLight,
                        'omni':MaxPlus.Factory.CreateOmniLight,
                        'tdlight':MaxPlus.Factory.CreateTargetedDirectionalLight,
                        'tslight':MaxPlus.Factory.CreateTargetedSpotLight,                        
                        'dummy' : MaxPlus.Factory.CreateDummyObject,
                        'floatCtrl':MaxPlus.Factory.CreateFloatController,
                        'mat3Ctrl':MaxPlus.Factory.CreateMatrix3Controller,
                        'pointCtrl':MaxPlus.Factory.CreatePoint3Controller,
                        'camera':MaxPlus.Factory.CreateFreeCamera,
                        'pcamera':MaxPlus.Factory.CreateParallelCamera,
                        'tcamera':MaxPlus.Factory.CreateTargetedCamera,
                        'geom':MaxPlus.Factory.CreateGeomObject,
                        'manipulator':MaxPlus.Factory.CreateManipulator,
                        'material':MaxPlus.Factory.CreateMaterial,
                        'morpgCtrl':MaxPlus.Factory.CreateMorphController,
                        'node':MaxPlus.Factory.CreateNode,
                        'object':MaxPlus.Factory.CreateObject,
                        'mod':MaxPlus.Factory.CreateObjectModifier,
                        'posCtrl':MaxPlus.Factory.CreatePositionController,
                        'renderer':MaxPlus.Factory.CreateRenderer,
                        'renderEffect':MaxPlus.Factory.CreateRenderingEffect,
                        'rotCtrl':MaxPlus.Factory.CreateRotationController,
                        'sampler':MaxPlus.Factory.CreateSampler,
                        'scaleCtrl':MaxPlus.Factory.CreateScaleController,
                        'shader':MaxPlus.Factory.CreateShader,
                        'shadow':MaxPlus.Factory.CreateShadowGenerator,
                        'sound':MaxPlus.Factory.CreateSound,
                        'sphereGizmo':MaxPlus.Factory.CreateSphereGizmoObject,
                        'target':MaxPlus.Factory.CreateTargetObject,
                        'texture':MaxPlus.Factory.CreateTextureMap,
                        'utility':MaxPlus.Factory.CreateUtility,
                        'worldmod':MaxPlus.Factory.CreateWorldSpaceModifier,
                        }
  
        self.progress_started = False
        self._usenumpy = hostHelper.usenumpy
        self.hext = "fbx"#"max" is for scene, how do i read a scene ?
        
    def getCurrentScene(self):
        return None
        
    def fit_view3D(self):
        pass#

#a.       BOOL ProgressStart(MCHAR * title, bool dispBar = true) { return GetCOREInterface13()->ProgressStart(title, dispBar ? 1 : 0, dummy_callback, NULL); }
#b.      void ProgressUpdate(int pct, bool showPct, const MCHAR * title) { GetCOREInterface13()->ProgressUpdate(pct, showPct ? 1 : 0, (const wchar_t*)title); }
#c.       void ProgressUpdate(int pct, bool showPct = true) { GetCOREInterface13()->ProgressUpdate(pct, showPct ? 1 : 0, (const wchar_t*)NULL); }
#d.      void ProgressEnd() { GetCOREInterface13()->ProgressEnd(); }
        
    def resetProgressBar(self,max=None):
        """reset the Progress Bar, using value"""
        #MaxPlus.Core.Interface.ProgressEnd()
        self.progress_started = False
        
    def progressBar(self,progress=None,label=None):
        """ update the progress bar status by progress value and label string
        @type  progress: Int/Float
        @param progress: the new progress
        @type  label: string
        @param label: the new message to put in the progress status
        """ 
        return               
        if not self.progress_started :
            MaxPlus.Core.Interface.ProgressStart(u"Progress",True)#,None,None)
        self.progress_started = True
        if progress is not None :
            if label is not None :
                MaxPlus.Core.Interface.ProgressUpdate(int(progress),False, unicode(label))
            else :
                MaxPlus.Core.Interface.ProgressUpdate(int(progress),True)
            
    def output(self,aStr):
        """ 3DsMax use his own console/stdout"""
        MaxPlus.Core.WriteLine(str(aStr))#or unicode ?

    def update(self,):
        #how do I update the redraw
        MaxPlus.Core.Interface.ForceCompleteRedraw(True)
        
    def updateAppli(self,):
        #how do I update the redraw
        MaxPlus.Core.Interface.ForceCompleteRedraw(True)

    def getObjectFromNode(self,node):
        node = self.getObject(node)
        if node is None:
            return None
        return node.GetObject()

    def setCurrentSelection(self,obj):
        #obj should be  a node
        MaxPlus.Core.GetInterface().SelectNode(obj)
    
    def getCurrentSelection(self):
        if MaxPlus.SelectionManager.Count == 0:
            return []
        return [MaxPlus.SelectionManager.GetNode(i) for i in range(MaxPlus.SelectionManager.Count)]

    def createObject(self, sid, cidname):
        if cidname in ["sphere","cube","cylinder","plane","cone","tube"]:
            obj = self.create_fct['geom'](self.dicClassId[cidname])
        elif cidname in self.create_fct :
            obj = self.create_fct()
        elif sid in self.create_fct:
            obj = self.create_fct[sid](self.dicClassId[cidname])
        else :
            obj = self.create_fct['object'](self.dicClassId[cidname])
        #cid = self.getClassId(cidname)
        #obj = MaxPlus.Core.CreateObject( sid, cid )
        #obj = MaxPlus.Factory.CreateGeomObject(self.dicClassId[cidname])
        #difference with MaxPlus.Core.Interface.CreateInstance(sid,cid) ???
        return obj

    def createNode(self,obj,name):
        node = MaxPlus.Factory.CreateNode(obj)#MaxPlus.Core.Interface.CreateObjectNode( obj, name )
        node.SetName(unicode(name))
        return node
        
    def createObjectWithNode(self, sid, cidname, name):
        obj = self.createObject(sid, cidname)
        node = MaxPlus.Factory.CreateNode(obj)
        node.SetName(unicode(name))
        return node,obj

    def getClassId(self, objectType):
        cid = MaxPlus.Class_ID()
        cid.SetPartA(self.dicClassId[objectType])
        cid.SetPartB( 0)
        return cid

    def addMod(self,obj,modType="smooth"):
        node = self.getObject(obj)
        mod = self.createObject('mod',modType)
        node.AddModifier(mod)
        return mod
        #cid = self.getClassId(modType)        
        #sid = MaxPlus.Constants.OsmClassId
        #mod = MaxPlus.Core.CreateObject( sid, cid )
        #self.setCurrentSelection(obj)
        #MaxPlus.Core.Interface.AddModToSelection(mod)
        
    def listNodeParamaters(self,o):
        if not o._IsValidWrapper(): 
            return
        pb = o.GetParameters()
        cnt = pb.GetCount()
        for i in range(cnt):
            param = pb.GetParam(i)
            name = param.GetName().data()
            val = param.GetValue(0)
            self.output('Index = {0}, Name = {1}, Value = {2}'.format(i, name, val ))
            
    def getType(self,object):
        if hasattr(object,"type"):
            return object.type
        return type(object)

    def setName(self,o,name):
        obj =self.getObject(o)        
        if obj is not None :
            obj.SetName(unicode(name))
        
    def getName(self,o):
        if type(o) == str or type(o) == unicode: 
            name = o
        else : 
            if hasattr(o,"GetName"):
                name=o.GetName()
            elif hasattr(o,"GetObjectName") :
                name=o.GetObjectName()
            else :
                name = ""
        return str(name)

    def childNodes(self,node):
##        if not hasattr(node,"NumberOfChildren"):
##            print self.getName(node)
##            return []
        #try :
        #    a = type(node)
        #except :
        #    print "THERE IS SOMETHING WRONG HERE"
        #    return []
        n = node.GetNumChildren()
        #print int(n)
        ch=[]
        #print "childNodes ",n," for ",node.GetName()
        for i in range(n):
            c=node.GetChild(i)
            ch.append(c)
        return ch

    def descendantNodesYeld(self,node):
        child = self.childNodes(node)
        for c in child:
            yield c
            for d in self.descendantNodes(c):
                yield d

    def descendantNodes(self,node):
        childs = []
        child = self.childNodes(node)
        childs.extend(child)
        for c in child:
            d = self.descendantNodes(c)
            childs.extend(d)
        return childs
    
    def allNodes(self):
        return self.descendantNodes(MaxPlus.Core.RootNode)

    def allSelectedNodes(self):
        return [n for n in self.allNodes() if n.IsSelected()]
        
##    def outputAllNodeNames(self,nodes = self.allNodes()):
##        for n in nodes:
##            output(n.Name)
            
    def getObject(self,name,**kw):
        if type(name) != str and type(name) != unicode :
            return name#self.getObject(name.name)
        allnode = self.allNodes()
        for n in allnode :
            if str(n.GetName()) == str(name) :
                return n
        return None

    def checkIsMesh(self,poly):
        pass

    def getMesh(self,ob):
        if ob is str :
           ob = self.getObject(ob)
        #print "getMesh",ob,type(ob),self.getName(ob),isinstance(ob, MaxPlus.TriObject)
        if isinstance(ob, MaxPlus.Mesh) :
            return ob
        if self.getName(ob) == 'Mesh' or isinstance(ob, MaxPlus.TriObject) :
            return ob.GetMesh()
        ob = self.getObjectFromNode(ob)
        #print "getObjectFromNode",ob
        try :
            tri = ob.AsTriObject(MaxPlus.Core.CurrentTime)
        except :
            print ("can't cast to AsTriObject")
            tri = None
        if tri is None :
            return ob
        #if not tri._IsValidWrapper():
        #    return None
        return tri.GetMesh()
  
    def getMeshFrom(self,obj):
        if type(obj) != str :
            obj = self.getObject(obj)
        return self.getMesh(obj)

    def newEmpty(self,name,location=None,**kw):
        obj = MaxPlus.Factory.CreateDummyObject()
        #print ("empty "+name)
        #print obj
        node = MaxPlus.Factory.CreateNode(obj)
        node.SetName(unicode(name))
        #print node,node.GetName()
        #node,obj = self.createObjectWithNode(MaxPlus.Constants.HelperClassId, "dummy", name)
        if location is not  None :
            #print location
            self.setTranslation(node,location)
        if "parent" in kw :
            parent = kw["parent"]
            #print parent
            parent = self.getObject(parent)
            self.reParent(node,parent)
        #print "return ",(node is None)
        return node

    def instance(self,name, node):
        node = self.getObject(node)
        #only get the deepest transformation ?
        object = node.GetObject()
        if object._IsValidWrapper():
           instance = MaxPlus.Factory.CreateNode(object)
           instance.SetName(unicode(name))
        return instance
    
    def instance_nodeTree(self,name, rootNode,parent = None, pmat = None):
        #clone everything
        #the scan then is cumulative ? but not  the rotation ? and translation ?
        rootNode = self.getObject(rootNode)
        #only get the deepest transformation ?
        rootinstance = self.instance(name, rootNode)
        #do it for all child
        ch = self.getChilds(rootNode)
        rootmat = rootNode.GetWorldTM()
        #rootmat.NoScale()
        nc = len(ch)
        for c in ch :
            #p=None
            #childMat = c.GetWorldTM()
            #if childMat != rootmat :
            #    p=rootmat
            i=self.instance_nodeTree(self.getName(c)+"inst", c,parent=rootinstance)
        if parent is not None :
            self.reParent(rootinstance,parent)
        #transformation?
        #if pmat is not None :
        #    pmat.Invert()
        #    rootmat = rootmat * pmat
        if nc :
            #if we have child do not apply scale,should work for dummy
            rootmat.IdentityMatrix()#NoScale()
        self.setObjectMatrix(rootinstance,None,hostmatrice=rootmat)
        return rootinstance
           
    def newInstance(self,name,object,location=None,hostmatrice=None,matrice=None,
                    parent=None,**kw):
        #we need  a model first for creating an instance
        #the object used for insace is placed in a model.
        instance = None
        node = self.getObject(object)
        object = node.GetObject()#this should be a triObj or primitive ..
        master_mat = node.GetWorldTM()
        #print "newInstance from ",self.getName(object)
        if self.getName(object) == "Dummy" :
            #node tree
            #instance = self.instance_nodeTree(name, node)
            #try :
            instance = node.CreateTreeInstance()
            #except :
            #    print "CreateTreeInstance is not working "
            #    instance = self.instance_nodeTree(name, node)
            instance.SetName(unicode(name))
            #unhide
        else :
            if object._IsValidWrapper():
               instance = MaxPlus.Factory.CreateNode(object)
               instance.SetName(unicode(name))
        #rint "ok for instance",name
        if parent is not None:
            self.reParent(instance,parent)
        if instance is None :
            print "ERROR for instance",name
            return
        transpose = False
        if "transpose" in kw :
            transpose = kw["transpose"]
        #master_mat = node.GetWorldTM()
        #print "will apply ",name, master_mat
        #should actually multyply by the matrice of the instancemaster
        #print "transform instance",name
        self.setObjectMatrix(instance,matrice,hostmatrice=hostmatrice,transpose=transpose,composanteMat=master_mat)
        if node.IsObjectHidden() :
            self.toggleDisplay(instance,True)
        if "material" in kw :
            self.assignMaterial(instance,kw["material"])
        if location != None :
            #set the position of instance with location
            self.setTranslation(instance,location )
        #print "return instance",name
        return instance

#newClone
        
    def instancePolygon(self,name, matrices=None,hmatrices=None, mesh=None,parent=None,
                        transpose=False,globalT=True,**kw):
        hm = False
        if hmatrices is not None :
            matrices = hmatrices
            hm = True
        if matrices == None : return None
        if mesh == None : return None
        instance = []
        #print len(matrices)#4,4 mats       
        for i,mat in enumerate(matrices):
            inst = self.getObject(name+str(i))
            if inst is None :
                if hm : 
                    inst=self.newInstance(name+str(i),mesh,hostmatrice=mat,
                                      parent=parent,globalT=globalT,
                                          transpose=transpose,**kw)
                else :
                    inst=self.newInstance(name+str(i),mesh,matrice=mat,
                                      parent=parent,globalT=globalT,
                                          transpose=transpose,**kw)
            instance.append(inst)
        return instance

    def resetTransformation(self,name):
        m= [1.,0.,0.,0.,
            0.,1.,0.,0.,
            0.,0.,1.,0.,
            0.,0.,0.,0.]
        o = self.getObject(name)
        m = o.GetWorldTM()
        if not m.IsIdentity():
            m.ToIdentity()
            o.SetWorldTM(m)

    def setObjectMatrix(self,object,mat,hostmatrice=None,composanteMat=None,**kw):
        """
        set a matrix to an hostObject
        
        @type  object: hostObject
        @param object: the object who receive the transformation 
        @type  hostmatrice: list/Matrix 
        @param hostmatrice: transformation matrix in host format
        @type  matrice: list/Matrix
        @param matrice: transformation matrix in epmv/numpy format
        """
        #have to manipulate the DAG/upper transform node...
        #let just take the owner Transofrm node of the shape
        #we should be able to setAttr either 'matrix' or 'worldMatrix'
        object = self.getObject(object)
        if hostmatrice !=None :
            if composanteMat != None :
                hostmatrice = hostmatrice * composanteMat
            #set the instance matrice
            object.SetWorldTM(hostmatrice)
        elif mat != None:
            if self._usenumpy :
                mat = numpy.array(mat)
                if "transpose" in kw and kw["transpose"]:
                    mat = mat.transpose()
                    #print "transpose",mat
            else :
                if "transpose" in kw and kw["transpose"]:
                    mat[3] = [mat[0][3],mat[1][3],mat[2][3],1.0]
                    mat[0][3],mat[1][3],mat[2][3] = 0.0,0.0,0.0
            hostmatrice = self.FromMat(mat)
            if composanteMat != None :
                hostmatrice = hostmatrice * composanteMat
            object.SetWorldTM(hostmatrice)
        elif composanteMat != None:
            object.SetWorldTM(composanteMat)
#    def concatObjectMatrix(self,object,matrice,hostmatrice=None):
#        """
#        apply a matrix to an hostObject
#    
#        @type  object: hostObject
#        @param object: the object who receive the transformation
#        @type  hostmatrice: list/Matrix 
#        @param hostmatrice: transformation matrix in host format
#        @type  matrice: list/Matrix
#        @param matrice: transformation matrix in epmv/numpy format
#        """
#        #get current transformation
#        if hostmatrice !=None :
#            #compute the new matrix: matrice*current
#            #set the new matrice
#            pass
#        if matrice != None:
#            #convert the matrice in host format
#            #compute the new matrix: matrice*current
#            #set the new matrice
#            pass
#
    def addObject(self,obj,parent=None,**kw):
        #its just namely put the object under a parent
        #return
        #no need in softimage
        if obj is None :
            return
        if type(obj) is list or type(obj) is tuple :
            obj = obj[0]
        if parent is not None :
            if type(parent) is list or type(parent) is tuple :
                parent = parent[0]
            obj = self.getObject(obj)
            parent = self.getObject(parent)
            self.reParent(obj,parent)
            
    def addObjectToScene(self,doc,obj,parent=None,**kw):
        #its just namely put the object under a parent
        #return
        #no need in softimage
        if obj is None :
            return
        if parent is not None :
            #print obj
            #print parent
            o = self.getObject(obj)
            p = self.getObject(parent)
            #print o,p
            self.reParent([o],p)

    def parent(self,obj,parent,instance=False):
##        if not isintance(obj,MaxPlus.INode) :
##            print self.getName(obj),type(obj)
##        if not isinstance(parent,MaxPlus.INode):
##            print self.getName(parent),type(parent)
        #print "reparent "+str(obj)+" "+str(parent)
        obj = self.getObject(obj)
        parent = self.getObject(parent)
        if isinstance(obj, MaxPlus.TriObject) :
            return
        if obj is None or parent is None :
            return
        if type(obj) is list or type(obj) is tuple :
            obj = obj[0]
        if type(parent) is list or type(parent) is tuple :
            parent = parent[0]
        #print "parent1 ", obj,type(obj),parent,type(parent)
        #print "parent2 "+obj.Name+" "+parent.Name
        parent.AttachChild(obj)#,keepTM=1)#should keep TM
        
    def reParent(self,obj,parent,instance=False):
        if parent == None : return
        if type(obj) is not list and type(obj) is not tuple :
            obj = [obj,]
        #print len(obj)
        for i in range(len(obj)):
            #print obj[i]
            self.parent(obj[i],parent,instance=instance)

    def getChilds(self,obj):
        obj = self.getObject(obj)
        nc = obj.GetNumChildren()
        return [obj.GetChild(i) for i in xrange(nc)]
#
    def addCameraToScene(self,name,Type='persp',focal=30.0,center=[0.,0.,0.],sc=None,**kw):
        
        node,obj = self.createObjectWithNode(u"camera", u"simple_camera", unicode(name))
        #params = node.GetParameters() => Crash??
        self.setTranslation(node, center)
        return node

    def addLampToScene(self,name,Type='Area',rgb=[1.,1.,1.],dist=25.0,energy=1.0,
                       soft=1.0,shadow=False,center=[0.,0.,0.],sc=None,**kw):
        dict={"Area":"omni",
              "Sun":"dirlight",
              "Spot":"spot"}
        node,obj = self.createObjectWithNode(u"light", unicode(dict[Type]), unicode(name))
##        Application.SetValue(name+".light.soft_light.intensity",float(energy),"")
##        Application.SetValue(name+".light.soft_light.rayshadow_softness",float(soft),"")
##        Application.SetValue(name+".light.soft_light.color.red",rgb[0],"")#0-1
##        Application.SetValue(name+".light.soft_light.color.blue",rgb[1],"")
##        Application.SetValue(name+".light.soft_light.color.green",rgb[2],"")
        self.setTranslation(node, center)
        return None
    
    def deleteObject(self,obj):
        sc = self.getCurrentScene()
        if type(obj) is str or type(obj) is unicode:
            obj = self.getObject(obj)
        if obj is None :
            return
        ch = self.getChilds(obj)
        for c in ch :
            self.deleteObject(c)
        try :
            obj.Delete(0,1)           
        except:
            print "problem deleting ", obj,self.getName(obj)
            
    def toggleDisplay(self,ob,display,**kw):
        display = bool(display)
        ob = self.getObject(ob)
        if ob is None :
            print "ob is None return"
            return
        if int(display) :
            hide = False
            ob.Hide(False)
        else :
            hide = True
            ob.Hide(True)
        ch = self.getChilds(ob)
        for c in ch :
            self.toggleDisplay(c,display)
        
##    def toggleXray(self,object,xray):
##        o = self.getObject(object)
##        cmds.select(o)
##        cmds.displySurface(xRay = True)XrayMtl
#

    def getVisibility(self,obj,editor=True, render=False, active=False):
        ob = self.getObject(ob)
        if ob is None :
            return
        if editor and not render and not active:
            return ob.Properties(u"Visibility").Parameters(u"viewvis").Value
        elif not editor and render and not active:
            return ob.Properties(u"Visibility").Parameters(u"rendvis").Value
        elif not editor and not render and active:
            return True
        else :
            return  [ob.Properties(u"Visibility").Parameters(u"viewvis").Value,
                    ob.Properties(u"Visibility").Parameters(u"rendvis").Value,
                    True]

    def getTranslation(self,name,absolue=True):
        ob = self.getObject(name)
        if ob is None :
            return
        if absolue :
            pos = ob.GetWorldPosition()
            return pos
        else :
            return ob.GetLocalPosition()
##        if absolue :
##            pos = [obj.Kinematics.Local.posx,obj.Kinematics.Local.posy,obj.Kinematics.Local.posz]
##        else :
##            pos = [obj.Kinematics.Global.posx,obj.Kinematics.Global.posy,obj.Kinematics.Global.posz]
##        return pos
#SetLocalPosition
#SetLocalRotation
#SetLocalScale
#SetLocalTM
#
#SetWorldRotation
#SetWorldScale
#SetWorldTM          
    def setTranslation(self,name,pos,local = False,**kw):
        obj = self.getObject(name)
        if obj is None :
            return
        
        if local :
            m = obj.GetLocalTM()
            m.SetTrans(self.FromVec(pos))#Translate() will append
            obj.SetLocalTM(m)            
            #obj.SetLocalPosition(self.FromVec(pos))
        else :
            m = obj.GetWorldTM()
            m.SetTrans(self.FromVec(pos))#Translate() will append
            obj.SetWorldTM(m)
#        if local :
##            obj.Set                                                                                                                                                                                                                                                                    ObjOffPos(self.FromVec(pos))
##        else : 
##            hm= [[1.,0.,0.,0.],
##                       [ 0.,1.,0.,0.],
##                       [ 0.,0.,1.,0.],
##                       [ 0.,0.,0.,0.]]
##            M=self.FromMat(hm)
##            M.SetAngleAxis(self.FromVec([0.,1.,0.]),0.0)
##            obj.Move(0,M,self.FromVec(pos))#difference with SetWorldPosition?

    def translateObj(self,obj,position,use_parent=False,**kw):
        #is om would be faster ?
        if len(position) == 1 : c = position[0]
        else : c = position
        #print "upadteObj"
        newPos=c#c=c4dv(c)
        o=self.getObject(obj)
        #if use_parent : 
        #    parentPos = self.getPosUntilRoot(obj)#parent.get_pos()
        #    c = newPos - parentPos
        self.setTranslation(obj, c)
        #o.Move(0,MaxPlus.Matrix3(),self.FromVec(position))#local gloa ...0


    def resetScale(self,name):
        obj = self.getObject(name)
        m = obj.GetWorldTM()
        m.NoScale()
        obj.SetWorldTM(m)
   
    def scaleObj(self,name,sc,local = False,**kw):
        obj = self.getObject(name)
        if obj is None :
            return
        if type(sc) is float :
            sc = [sc,sc,sc]
        if local :
            obj.SetLocalScale(self.FromVec(sc))
        else :
            obj.SetWorldScale(self.FromVec(sc))
##            
##        if local :
##            obj.SetObjOffScale(MaxPlus.ScaleValue(self.FromVec(sc)))
##        else :
##            hm= [[1.,0.,0.,0.],
##                   [ 0.,1.,0.,0.],
##                   [ 0.,0.,1.,0.],
##                   [ 0.,0.,0.,0.]]
##            M=self.FromMat(hm)
##            M.SetAngleAxis(self.FromVec([0.,1.,0.]),0.0)
##            obj.Scale(0,M,self.FromVec(sc))

    def rotateObj(self,name,rot,local=False,**kw):
        #need degreee!
        #rot is rot on x on y and on z value
        obj = self.getObject(name)
        if obj is None :
            return
        q=MaxPlus.Quat()
        q.SetEuler(rot[0],rot[1],rot[2])
        if local :
            obj.SetLocalRotation(q)
        else :
            obj.SetWorldRotation(q)

    def setTransformation(self,name,mat=None,rot=None,scale=None,trans=None,order="str",**kw):
        obj = self.getObject(name)
        if mat is not None  :
            self.setObjectMatrix(obj, mat)
        if trans is not None :
            self.translateObj(obj,trans)
        if rot is not None :
            self.rotateObj(obj,rot)
        if scale is not None :
            self.scaleObj(obj,scale)

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
#        dic={"add":True,"new":False}
#        sc = self.getCurrentScene()
#        
#        for obj in listeObjects:
#            cmds.select(self.getObject(obj),add=dic[typeSel])
#    
#        #Put here the code to add/set an object to the current slection
#        #[sc.SetSelection(x,dic[typeSel]) for x in listeObjects]
#    
#    def JoinsObjects(self,listeObjects):
#        """
#        Merge the given liste of object in one unique geometry.
#        
#        @type  listeObjects: list
#        @param listeObjects: list of object to joins
#        """    
#        sc = self.getCurrentScene()
#        #put here the code to add the liste of object to the selection
#        cmds.select(self.getObject(listeObjects[0]))
#        for i in range(1,len(listeObjects)):
#            cmds.select(listeObjects[i],add=True)
#        cmds.polyUnite()
#        #no need to joins? but maybe better
        #then call the command/function that joins the object selected
    #    c4d.CallCommand(CONNECT)

    def printChannelData(self,mc,name):
        print ("Channel " + name)
        if not mc.Enabled:
            print("Not enabled");
            return

        print ("Number of texture vertices ", mc.NumTextureVertices)
        for tv in  mc.TextureVertices :
            print ("Texture vertex", tv.X, tv.Y, tv.Z)

        print ("Number of faces", mc.NumFaces);
        for tf in  mc.TextureFaces:
            print ("Texture vertex indices", tf.A, tf.B, tf.C)
        
    #need face indice
    def color_mesh_perVertex(self,mesh,colors,faces=None,perVertex=True,
                             facesSelection=None,faceMaterial=False):
        if colors[0] is not list and len(colors) == 3 :
           colors = [colors,] 
        nCol = len(colors)
        print "color_mesh_perVertex "
        print mesh
        if type(mesh) is str or type(mesh) is unicode:
            name = mesh
            mesh = self.getObject(mesh)
        else :
            name = self.getName(mesh)
        node = self.getObject(name)
        node.SetCVertMode(1)
        node.SetShadeCVerts(1)
        #shaded ?
        mesh = self.getMesh(mesh)
       
        if  mesh is None:
            return

        #self.addMod(meshnode,modType="smooth")

        nv = mesh.GetNumVertices()
        nf = mesh.GetNumFaces()
        print "mesh has ",nv,nf
        print "color ",nCol

        if  facesSelection is not None :
            if type(facesSelection) is bool :
                fsel,face_sel_indice = self.getMeshFaces(mesh,selected=True)
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
            nf = len(fsel)
            nv = len(vsel)

        if len(colors) == nv:
            perVertex = True
        elif len(colors) == nf:
            perVertex = False
        N=range(nf)
        if facesSelection is not None :
            N = face_sel_indice
            perVertex = False
        print "mesh.ColorPerVertexMap.SetNumTextureVertices"
        nnff = mesh.ColorPerVertexMap.GetNumFaces()
        mesh.ColorPerVertexMap.SetNumTextureVertices(nv)
        for k,i in enumerate(N) :
            face = mesh.GetFace(i)
            #print face,"face i "+str(i)+" on "+str(nf) 
            vertices =[face.getVert(j) for j in range(3)]
            for n in vertices:
                if len(colors) == 1 : ncolor = colors[0]
                else :
                    if perVertex : 
                        if n >= len(colors) : 
                            ncolor = [0.,0.,0.] #problem
                        else : 
                            ncolor = colors[int(n)]
                    else :
                        if i >= len(colors) : 
                            ncolor = [0.,0.,0.] #problem
                        else : 
                            ncolor = colors[i]
                if n < nv :
                    mesh.ColorPerVertexMap.SetTextureVertex(n,self.FromVec(ncolor))
                #print "vertices n "+str(n)+" on "+str(nv) 
            if i < nf :
                mesh.ColorPerVertexMap.SetTextureFace(i, vertices[0], vertices[1], vertices[2]);
        print "mesh.ColorPerVertexMap.SetNumTextureVertices"
        #
        #self.addMod(meshnode,modType="smooth")
        mesh.InvalidateGeomCache()
        mesh.InvalidateTopologyCache()#
        
        try :
            node.NotifyChanged()
        except:
            print  ("update MaxPlus sciviz")
        self.setCurrentSelection(node)

        self.update()
        return True
        
    ###################MATERIAL CODE FROM Rodrigo Araujo#####################################################################################
    def createMaterial(self, name, color, type = "Phong",**kw):
        #type can be lamber phong etc... need a dictionry
        return self.addMaterial(name, color,type=type,**kw )

    def addMaterial(self, name, color,type="Phong",**kw ):
        dicType={"Phong":1,"phong":1,"lambert":0,"Lambert":0}
        mat = MaxPlus.Globals.NewDefaultStdMat()
        mat.SetName(MaxPlus.WStr(name))
        mat.SetShading(dicType[type])
        self.colorMaterial(mat, color)
        MaxPlus.MaterialLibrary.CurrentLibrary.Add(mat)
        #print ("addMAterial",name,mat)
        return mat

    def createTexturedMaterial_cmd(self,name,filename):
        #cget the image
        oImage = Application.AddImageSource( filename )
        oImageClip = Application.AddImageClip( oImage )
        material = self.getMaterial(name)
        if material is None :
            material = self.addMaterial(name,[0.,0.,0.])
        #get the shader
        shader = material.Shaders(0)
        layer = Application.AddTextureLayer("", shader.FullName, "", "", "")
        ports = Application.AddTextureLayerPorts(layer.FullName, shader.FullName+".ambient,"+shader.FullName+".diffuse")
        img = Application.SIApplyShaderToCnxPoint("Image", layer.FullName+".color", "", "")
        Application.DisconnectAndDeleteOrUnnestShaders("Clips.noIcon_pic", material.FullName)
        Application.SIConnectShaderToCnxPoint(oImageClip, material.FullName+".Image.tex", False)
        return material
        
    def createTexturedMaterial(self,name,filename):
        return self.createTexturedMaterial_cmd(name,filename)
    
    def assignMaterial(self,object,material,texture = False,**kw):
        #except material name or ful name ?
        node = self.getObject(object)
        object = node.GetObject()#this should be a triObj or primitive ..
        if self.getName(object) == "Dummy" :
            node = node.GetChild(0)
        object = node
        if type(material) == list or type(material) ==  tuple :
            if material :
                material = material[0]
            else :
                return
        if type(material) == str :
            material = self.getMaterial(material)
            if material is None :
                return
        if material is None :
            return
        object = self.getObject(object)
        object.SetMtl(material)
        if texture :
            pass      

    def assignNewMaterial(self, matname, color, type, object):
        mat = self.createMaterial (matname, color, type)
        self.assignMaterial (object,mat)
    
    def colorMaterial(self,matname, color):
        #t = MaxPlus.Core.CurrentTime
        color = MaxPlus.Color(color[0], color[1], color[2])
        m = self.getMaterial(matname)
        if hasattr(m,"SetAmbient"):
            m.SetAmbient(color)
            m.SetDiffuse(color)
            m.SetSpecular(MaxPlus.Color(1, 1, 1))
            m.SetShininess(0.5)
            m.SetShinyStrength(0.7)
        else :
            print m,type(m)

    def changeMaterialProperty(self,material, **kw):
        """
        Change a material properties.
        
        * overwrited by children class for each host
        
        @type  material: string/Material
        @param material: the material to modify
        @type  kw: dictionary
        @param kw: propertie to modify with new value
            - color
            - specular
            - ...
            
        """
        mat =self.getMaterial(material)
        if mat is None :
            return
        #shader = mat.GetShader()
        if "specular" in kw :
            if type(kw["specular"]) == bool :
                if not kw["specular"] :
                    mat.SetSpecular(MaxPlus.Color(0, 0, 0))
        if "specular_width" in kw :
            #need access to the shader
            pass#mat.SetSpecularLevel(kw["specular_width"])

    def getMaterialProperty(self,material, **kw):
        """
        Get a material properties.
        
        * overwrited by children class for each host
        
        @type  material: string/Material
        @param material: the material to modify
        @type  kw: dictionary
        @param kw: propertie to modify with new value
            - color
            - specular
            - ...
            
        """
        mat =self.getMaterial(material)
        if mat is None :
            return
        res = []
        if "specular" in kw :
            res.append( None )
        if "specular_width" in kw :
            res.append( None)
        if "color" in kw :
            c = mat.GetAmbient()
            res.append([c.Getr(),c.Getg(),c.Getb()])
        return res
    
    def getMaterial(self,matname):
        if type(matname) != str and type(matname) != unicode : return matname
        #matlib = MaxPlus.Core.Interface.GetSceneMtls()
        index = MaxPlus.MaterialLibrary.CurrentLibrary.FindMaterialByName(str(matname))
        if index is None or index == -1:
            return None
        mat = MaxPlus.MaterialLibrary.CurrentLibrary.GetMaterial(index)
        if mat is None :
            return None
        return self.ToStdMat(mat)
            
    def getMaterialName(self,mat):
        if type(mat) == str : return mat
        name = mat.GetName()
        #print "getMaterialName"def,type(name)        
        return name

    def ToStdMat(self,mat):
        if isinstance(mat,MaxPlus.MtlBase):
            return MaxPlus.StdMat._CastFrom(mat)
        return mat

    def getAllMaterials(self):
        lmats = MaxPlus.MaterialLibrary.CurrentLibrary.Materials#MaxPlus.Core.Interface.GetSceneMtls()
        stdmats = [self.ToStdMat(m) for m in lmats]
        return stdmats

    def getMaterialObject(self,obj):
        obj = self.getObject(obj)
        m = obj.GetMtl()
        return [self.ToStdMat(m),]

    def changeObjColorMat(self,obj,color):
        #obj should be the object name, in case of mesh
        #in case of spher/cylinder etc...atom name give the mat name
        #thus  matname should be 'mat_'+obj
        obj = self.getObject(obj)
        mat = self.getMaterialObject(obj)
        self.colorMaterial(mat,color)
          
    def changeColor(self,mesh,colors,perVertex=True,perObjectmat=None,pb=False,
                    facesSelection=None,faceMaterial=False,**kw):
        #if hasattr(geom,'obj'):obj=geom.obj
        #else : obj=geom
        #mesh = self.getMesh(mesh)
        if colors[0] is not list and len(colors) == 3 :
           colors = [colors,]        
        print "change color"+str(type(mesh))
        print (mesh)
            
        res = self.color_mesh_perVertex(mesh,colors,perVertex=perVertex,
                                  facesSelection=facesSelection,
                                  faceMaterial=faceMaterial)
        print str(res)+" "+str(not res)+" n color "+str(len(colors))
        if not res or len(colors) == 1:
            #simply apply the color/material to mesh
            #get object material, if none create one
            print "material assign"
            mats = self.getMaterialObject(mesh)
            print mats
            if not mats :
                self.assignNewMaterial("mat"+self.getName(mesh), colors[0],
                                       'lambert', mesh)
            else :
                self.colorMaterial(mats[0],colors[0])


    ###################Meshs and Objects#####################################################################################                                                                        
    def Sphere(self,name,res=16.,radius=1.0,pos=None,color=None,
               mat=None,parent=None,type="nurb"):
##        Index = 0, Name = Radius, Value = 0.0
##        Index = 1, Name = Segments, Value = 32
##        Index = 2, Name = Smooth, Value = 1
##        Index = 3, Name = Hemisphere, Value = 0.0
##        Index = 4, Name = , Value = 0
##        Index = 5, Name = , Value = 0
##        Index = 6, Name = , Value = 1
##        Index = 7, Name = Slice On, Value = 0
##        Index = 8, Name = Slice From, Value = 0.0
##        Index = 9, Name = Slice To, Value = 0.0
        node,obj = self.createObjectWithNode(u"geom", u"sphere", unicode(name))
        #set radius ad quality
        params = node.GetParameters()
        #params.GetParam(0).SetValue(float(radius),0) #cap_Segments
        #params.GetParam(1).SetValue(int(res),0)
        params.Radius = float(radius)
        params.Segments = int(res)
        #params = node.get_Parameters()
        #params.GetParameters(1).SetValue(res,0) #height_Segments
        #node.get_Parameters().Sides = length
        p=None
        if parent is not None :
            p=self.getObject(parent)
            self.reParent(node,p)
        #shape is name+"Shape"
        #if pos is not None :
        #    self.setTranslation(name, pos)
##        if mat is not None :
##            mat = self.getMaterial(mat)
##            if mat is not None :
##                self.assignMaterial(name,mat)
##        else :
##            if color is not None :
##                mat = self.addMaterial("mat"+name,color)
##            else :
##                mat = self.addMaterial("mat"+name,[1.,1.,0.])
###            mat = self.getMaterial(name)
##            self.assignMaterial(name,mat)
        return node,obj

    def updateSphereMesh(self,mesh,verts=None,faces=None,basemesh=None,
                         scale=None,typ=True):
        #scale or directly the radius..Try the radius
        #scale is actualy the radius
        #print "updateSphereMesh", mesh,type(mesh)
        if mesh is None :
            return
        node = self.getObject(mesh)
        #print "node ", node,type(node),self.getName(node)
        if node is None :
            print ("no object in scene : ",mesh,type(mesh))
            return
        object = node.GetObject()#this should be a Sphere..
        if self.getName(object) == "Dummy" :
            node = node.GetChild(0)
        params = node.GetParameters()
        #params.GetParam(0).SetValue(float(radius),0) #cap_Segments
        #params.GetParam(1).SetValue(int(res),0)
        params.Radius = float(scale)
        
    def updateSphereObj(self,obj,coords=None):
        if obj is None or coords is None: return
        obj = self.getObject(obj)
        #would it be faster we transform action
        self.setTranslation(obj,coords)

##    def updateSphereObjs(self,g,coords=None):
##        if not hasattr(g,'obj') : return
##        if coords == None :
##            newcoords=g.getVertices()
##        else :
##            newcoords=coords
##        #print "upadteObjSpheres"
##        #again map function ?
##        for i,nameo in enumerate(g.obj):
##            c=newcoords[i]
##            o=getObject(nameo)
##            cmds.move(float(c[0]),float(c[1]),float(c[2]), o, absolute=True )
    
    def instancesCylinder(self,name,points,faces,radii,
                          mesh,colors,scene,parent=None):
        cyls=[]
        mat = None
        if len(colors) == 1:
            mat = self.retrieveColorMat(colors[0])
            if mat == None and colors[0] is not None:        
                mat = self.addMaterial('mat_'+name,colors[0])
        for i in range(len(faces)):
            cyl = self.oneCylinder(name+str(i),points[faces[i][0]],
                                   points[faces[i][1]],radius=radii[i],
                                   instance=mesh,material=mat,parent = parent)
            cyls.append(cyl)
        return cyls
    
    def updateInstancesCylinder(self,name,cyls,points,faces,radii,
                          mesh,colors,scene,parent=None):
        mat = None
        if len(colors) == 1:
            mat = self.retrieveColorMat(colors[0])
            if mat == None and colors[0] is not None:        
                mat = self.addMaterial('mat_'+name,colors[0])
        for i in range(len(faces)):
            col=None
            if i < len(colors):
                col = colors[i]
            if i < len(cyls):
                self.updateOneCylinder(cyls[i],points[faces[i][0]],
                                   points[faces[i][1]],radius=radii[i],
                                   material=mat,color=col)
                self.toggleDisplay(cyls[i],True)
            else :
                cyl = self.oneCylinder(name+str(i),points[faces[i][0]],
                                   points[faces[i][1]],radius=radii[i],
                                   instance=mesh,material=mat,parent = parent)
                cyls.append(cyl)

        if len(faces) < len(cyls) :
            #delete the other ones ?
            for i in range(len(faces),len(cyls)):
                if delete : 
                    obj = cyls.pop(i)
                    print "delete",obj
                    self.deleteObject(obj)
                else :
                    self.toggleDisplay(cyls[i],False)
        return cyls


    
    def instancesSphere(self,name,centers,radii,meshsphere,colors,scene,parent=None):
        sphs=[]
        mat = None
        if len(colors) == 1:
            mat = self.retrieveColorMat(colors[0])
            if mat == None:        
                mat = self.addMaterial('mat_'+name,colors[0])
        for i in range(len(centers)):
            sp = self.newInstance(name+str(i),meshsphere)
            sphs.append(sp)
            #local transformation ?
            self.translateObj(sp,centers[i])
            self.scaleObj(sp,[float(radii[i]),float(radii[i]),float(radii[i])])
            if mat == None : mat = self.addMaterial("matsp"+str(i),colors[i])
            self.assignMaterial(name+str(i),mat)#mat[bl.retrieveColorName(sphColors[i])]
            self.addObjectToScene(scene,sphs[i],parent=parent)
        return sphs

    def updateInstancesSphere(self,name,sphs,centers,radii,meshsphere,
                        colors,scene,parent=None,delete=True):
        mat = None
        if len(colors) == 1:
            mat = self.retrieveColorMat(colors[0])
            if mat == None and colors[0] is not None:        
                mat = self.addMaterial('mat_'+name,colors[0])
        for i in range(len(centers)):
            if len(radii) == 1 :
                rad = radii[0]
            elif i >= len(radii) :
                rad = radii[0]
            else :
                rad = radii[i]            
            if i < len(sphs):
                self.translateObj(sphs[i],centers[i])
                self.scaleObj(sphs[i],[float(rad),float(rad),float(rad)])
                if mat == None : 
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
                if mat == None : mat = self.addMaterial("matsp"+str(i),colors[i])
                self.assignMaterial(name+str(i),mat)#mat[bl.retrieveColorName(sphColors[i])]
                if mat == None :
                    if colors is not None and  i < len(colors) and colors[i] is not None : 
                        mat = self.addMaterial("matsp"+str(i),colors[i])
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
            
    def constraintLookAt(self,object):
        """
        Cosntraint an hostobject to llok at the camera
        
        @type  object: Hostobject
        @param object: object to constraint
        """
        self.getObject(object)
        return
#
#    def updateText(self,text,string="",parent=None,size=None,pos=None,font=None):
#        text = self.checkName(text)
#        if string : cmds.textCurves(text, e=1, t=string )
##        if size is not None :  text[c4d.PRIM_TEXT_HEIGHT]= size
##        if pos is not None : self.setTranslation(text,pos)
##        if parent is not None : self.reParent(text,parent)
#
#    def extrudeText(self,text,**kw):
#        tr,parent = self.getTransformNode(text)
#        nChild = parent.childCount()
#        print nChild
#        #dag = om.MFnDagNode(node)
#        dnode = om.MFnDependencyNode(parent.transform())
#        child_path = om.MDagPath()
#        cmd ="constructionHistory=True,normalsOutwards=True,range=False,polygon=1,\
#                        tolerance=0.01,numberOfSides=4 ,js=True,width=0 ,depth=0 ,extrudeDepth=0.5,\
#                            capSides=4 ,bevelInside=0 ,outerStyle=0 ,innerStyle=0 ,\
#                            polyOutMethod=0,polyOutCount=200,polyOutExtrusionType=2 ,\
#                            polyOutExtrusionSamples=3,polyOutCurveType=2 ,\
#                            polyOutCurveSamples=3,polyOutUseChordHeightRatio=0)"
#        for i in range(nChild):
#            #get all curve
#            node_child = parent.child(i)
#            child_tr,child_path = self.getTransformNode(node_child)
#            dnode = om.MFnDependencyNode(node_child)               
#            nChildChild = child_path.childCount()
#            for j in range(nChildChild):
#                cmdchilds="cmds.bevelPlus("
#                node_child_child = child_path.child(j)
#                dnode = om.MFnDependencyNode(node_child_child)
#                cmdchilds+='"'+dnode.name()+'",'
#                cmdchilds+="n='bevel_"+dnode.name()+str(j)+"',"+cmd
#                cmdbis = 'cmds.bevel("'+dnode.name()+'",n="bevel_'+dnode.name()+str(j)+'", ed=0.5)'
#                eval(cmdbis)  
#                cmds.bevel(e=1,w=0,d=0)
#
#

    def setPrimitiveParameters(self,node,params,values):
        params = node.get_Parameters()
        

    def Text(self,name="",string="",parent=None,size=5.,pos=None,font='Courier',
             lookAt=False,**kw):
        return_extruder = False
        s="_RTF_{\\rtf1\\ansi\\deff0{\\fonttbl{\\f0\\fnil\\fcharset0 Arial;}}\r\n\\viewkind4\\uc1\\pard\\lang1033\\fs20 "
        e="\\par\r\n}\r\n"
        textObject = name
        textText = ""
        #name = self.checkName(name)
        if "extrude" in kw :
            extruder = None
            if type(kw["extrude"]) is bool and kw["extrude"]:
                text = Application.CreateMeshText("CurveListToSolidMeshForText")#"siPeristentOperation"
                #this crete the mesh object and the Curve text object
                text= Application.Selection(0)
                #problem how get name of mesh and name of text
                #mesh = text.name
                text.name = name
                textObject = name+".polymsh.CurveListToMesh"
                return_extruder = True
            else :
                text = Application.CreatePrim("Text","NurbsCurve",name,"")
                text = Application.Selection(0)
                text.name = name
                textObject = name
        else :
            text = Application.CreatePrim("Text","NurbsCurve",name,"")
            text = Application.Selection(0)
            text.name = name
            textObject = name
        textText = textObject+".crvlist.TextToCurveList.text"
        Application.SetValue(textText+".text",s+string+e,"")
        ## Result: [u'testShape', u'makeTextCurves2'] # 
        if pos is not None :
            #should add -14
            pos[0] = pos[0]-14.0#not center
            self.setTranslation(name,pos)
#        if parent is not None:
#            self.addObjectToScene(self.getCurrentScene(),name+'Shape',parent=parent)
        if lookAt:
            self.constraintLookAt(name)
        Application.SetValue(textObject+".crvlist.TextToCurveList.fitsize",size,"")
#        self.scaleObj(text[0],[size,size,size])        
        if return_extruder :
            return text,None        
        return text

    def getBoxSize(self,name,**kw):
        """
        Return the current size in x, y and z of the  given Box if applcable
        
        * overwrited by children class for each host
        
        @type  name: hostObject
        @param name: the Box name
       
        @rtype:   3d vector/list
        @return:  the size in x y and z   
        """
        node = self.getObject(name)
        params = node.GetParameters()     
        return [params.Width,params.Length,params.Height]

    def box(self,name,center=[0.,0.,0.],size=[1.,1.,1.],cornerPoints=None,visible=1,
                              mat=None,**kw):
##        Index = 0, Name = Length, Value = 0.0
##        Index = 1, Name = Width, Value = 0.0
##        Index = 2, Name = Height, Value = 0.0
##        Index = 3, Name = Width Segments, Value = 1
##        Index = 4, Name = Length Segments, Value = 1
##        Index = 5, Name = Height Segments, Value = 1
##        Index = 6, Name = , Value = 1
        if cornerPoints != None :
            for i in range(3):
                size[i] = cornerPoints[1][i]-cornerPoints[0][i]
            center=[0.,0.,0.]#(numpy.array(cornerPoints[0])+numpy.array(cornerPoints[1]))/2.
            for i in range(3):
                center[i] = (cornerPoints[0][i]+cornerPoints[1][i])/2.
        res = 15.
        node,obj = self.createObjectWithNode("geom", "box", unicode(name))
        p=None
        if "parent" in kw :
            p=self.getObject(kw["parent"])
            self.reParent(node,p)
        #set radius ad quality
        params = node.GetParameters()#get_Parameters()
        params.Length = float(size[1])
        params.Width = float(size[0])
        params.Height = float(size[2])

        node.CenterPivot(0,0)
        self.resetTransformation(node)       

        #params.GetParameters(0).SetValue(1.0,0)
        #params.GetParameters(1).SetValue(1.0,0)
        #params.GetParameters(2).SetValue(1.0,0) 
    
        #use the scale instead of the length
        #self.scaleObj(obj,size)
        #mat = self.addMaterial("mat"+name,[1.,1.,0.])
        #elf.assignMaterial(obj,mat)

        #self.setTranslation(obj,center)
        return node,obj

#    def updateBox(self,box,center=[0.,0.,0.],size=[1.,1.,1.],cornerPoints=None,
#                    visible=1, mat = None):
#        box=self.getObject(box)
#        if cornerPoints != None :
#            for i in range(3):
#                size[i] = cornerPoints[1][i]-cornerPoints[0][i]
#            for i in range(3):
#                center[i]=(cornerPoints[0][i]+cornerPoints[1][i])/2.
#        cmds.move(float(center[0]),float(center[1]),float(center[2]),box)
#        cmds.polyCube(box,e=1,w=float(size[0]),h=float(size[1]),
#                                    d=float(size[2]))
#
    def Cone(self,name,radius=1.0,length=1.,res=16,pos = None,parent=None,**kw):
##        Index = 0, Name = Radius 1, Value = 0.0
##        Index = 1, Name = Radius 2, Value = 0.0
##        Index = 2, Name = Height, Value = 0.0
##        Index = 3, Name = Height Segments, Value = 5
##        Index = 4, Name = Cap Segments, Value = 1
##        Index = 5, Name = Sides, Value = 24
##        Index = 6, Name = Smooth, Value = 1
##        Index = 7, Name = Slice On, Value = 0
##        Index = 8, Name = Slice From, Value = 0.0
##        Index = 9, Name = Slice To, Value = 0.0
##        Index = 10, Name = , Value = 1
        node,obj = self.createObjectWithNode("geom", "cone", unicode(name))
        p=None
        if parent is not None:
            p=self.getObject(parent)
            self.reParent(node,p)    
        #set radius ad quality
        params = node.GetParameters()
        #params.Radius1 = float(radius)
        #params.Height = float(length)
        #params.HeightSegments
        #params.GetParameters(0).SetValue(float(radius),0)#radius1
       # params.GetParameters(2).SetValue(float(length),0)
        #params.GetParameters(3).SetValue(int(res),0) #height_Segments

        #obj.subdivu = res
        #obj.subdivv = res
        #obj.subdivbase = res
        #mat = self.addMaterial("mat"+name,[1.,1.,0.])
        #self.assignMaterial(obj,mat)
        #if pos is not None :
        #    self.setTranslation(obj,pos)
        return node,obj
    
    def Cylinder(self,name,radius=1.,length=1.,res=16,pos = None,parent=None,**kw):
##        Index = 0, Name = Radius, Value = 0.0
##        Index = 1, Name = Height, Value = 0.0
##        Index = 2, Name = Height Segments, Value = 5
##        Index = 3, Name = Cap Segments, Value = 1
##        Index = 4, Name = Sides, Value = 18
##        Index = 5, Name = Smooth, Value = 1
##        Index = 6, Name = Slice On, Value = 0
##        Index = 7, Name = Slice From, Value = 0.0
##        Index = 8, Name = Slice To, Value = 0.0
##        Index = 9, Name = , Value = 1
        #in 3dsMax cylinder are center at the bottom!
        typ = "poly"
        if "type" in kw:
            typ = kw["type"]
        node,obj = self.createObjectWithNode("geom", "cylinder", name)
        p=None
        if parent is not None:
            p=self.getObject(parent)
            self.reParent(node,p)
        #set radius ad quality
        params = node.GetParameters()
        params.Radius = float(radius)
        params.Height = float(length)
        backToCenter = [0.,0.0,0.]
        #node.CenterPivot(0,0)#we may translate -h/2.0 ? on Y ?
        #self.resetTransformation(node)
        
        #look like the cylinder by default is Z-up
        #params.Sides = int(res)
        #params.GetParam(0).SetValue(float(radius),0) #height_Segments
        #params.GetParam(1).SetValue(float(length),0) #cap_Segments       
        #params.GetParam(2).SetValue(int(res),0) #height_Segments
        #params.GetParam(3).SetValue(int(res),0) #cap_Segments
        #params.GetParam(3).SetValue(int(res),0) #cap_Segments        
        if "axis" in kw :
            #current is 0.,0.,1.
            #kw["axis"]
            #rotate to align to this axis
            axis = kw["axis"]
            if type(axis) == str or type(axis) == unicode :
                dic = {"+X":[1.,0.,0.],"-X":[-1.,0.,0.],"+Y":[0.,1.,0.],"-Y":[0.,-1.,0.],
                    "+Z":[0.,0.,1.],"-Z":[0.,0.,-1.]}
                axis = dix[kw["axis"]]
            angle,axis = self.getAngleAxis([0.,0.,1.],axis)
            m = self.rotation_matrix(angle,axis)
            self.setObjectMatrix(node,m)
            backToCenter = [0.,(length)/2.0,0.]
        #subdivision parameter ?
        #obj.subdivu = res
        #obj.subdivv = res
        #obj.subdivbase = res
        #mat = self.addMaterial("mat"+name,[1.,1.,0.])
        #self.assignMaterial(obj,mat)
        if pos is not None :
            self.setTranslation(node,pos+backToCenter)
        else :
            self.setTranslation(node,backToCenter)#if orientationis good
        return node,obj


    def oneCylinder(self,name,head,tail,radius=None,instance=None,material=None,
                    parent = None,color=None):
        #name = self.checkName(name)
        laenge,wsz,wz,coord=self.getTubeProperties(head,tail)
        #print ("oneCylinder instance",name,instance)
        if instance == None : 
            obj = self.Cylinder(name)
        else : 
            obj = self.newInstance(name,instance,parent=parent)
        if radius is None :
            radius= 1.0
        obj = self.getObject(obj)
        m=obj.GetWorldTM()
        m.ToIdentity()
        m.Scale(self.FromVec([radius,radius,laenge]))
        m.RotateY(wz)    
        m.RotateZ(wsz)    
        m.Translate(self.FromVec(tail))      #or head-tail ? 
        obj.SetWorldTM(m)
        #self.translateObj(name,coord)
        #self.rotateObj(name,[0.,wz,wsz])
        #self.scaleObj(name,[radius, radius, laenge])
        if material is not None :
            self.assignMaterial(obj,material)
        elif color is not None :
            mats = self.getMaterialObject(obj)
            if not mats :
                mat = self.addMaterial("mat_"+name,color)
                self.assignMaterial(obj,mat)
            else :
                self.colorMaterial(mats[0],color)
        return obj

#    def updateOneCylinder(self,name,head,tail,radius=None,material=None,color=None):
#        name = self.checkName(name)
#        laenge,wsz,wz,coord=self.getTubeProperties(head,tail)
#        obj = self.getObject(name)
#        if radius is None :
#            radius= 1.0        
#        self.setTransformation(obj,trans=coord,scale=[radius, radius, laenge],
#                               rot=[0.,wz,wsz])
#        if material is not None :
#            self.assignMaterial(obj,material)
#        elif color is not None :
#            mats = self.getMaterialObject(obj)
#            if not mats :
#                mat = self.addMaterial("mat_"+name,color)
#                self.assignMaterial(obj,mat)
#            else :
#                self.colorMaterial(mats[0],color)
#        return obj
#        
#                            
    def updateTubeObj(self,o,coord1,coord2):
        o = self.getObject(o)
        laenge,wsz,wz,pos=self.getTubeProperties(coord1,coord2)
        self.translateObj(o,coord)
        self.rotateObj(o,[0.,wz,wsz])
        self.scaleObj(o,[1.0, 1.0, laenge])        
        #self.setTransformation(o,trans=pos,scale=[1., 1., laenge],
        #                       rot=[0.,wz,wsz])

#            
#    def updateTubeMeshold(self,atm1,atm2,bicyl=False,cradius=1.0,quality=0):
#        self.updateTubeObj(atm1,atm2,bicyl=bicyl,cradius=cradius)
#    
    def updateTubeMesh(self,mesh,basemesh=None,cradius=1.0,quality=0):
##        print mesh
##        print cradius, mesh
        print mesh,type(mesh)
        if type(mesh) == list or type(mesh) == tuple :
            mesh = mesh[0]
        node = self.getObject(mesh)#what about instance?
        geom = self.getObjectFromNode(node)
        if self.getName(geom) == "Dummy" :
            node = node.GetChild(0)
            geom = self.getObjectFromNode(node)
        if self.getName(geom) != "Cylinder" :
            return
        params = node.GetParameters()
        params.Radius = float(cradius)
        #params.Height = float(length)
 
##    def updateTubeObjs(self,g):
##        if not hasattr(g,'obj') : return
##        newpoints=g.getVertices()
##        newfaces=g.getFaces()
##        #print "upadteObjTubes"
##        for i,o in enumerate(g.obj):
##            laenge,wsz,wz,pos=self.getTubeProperties(points[f[0]],points[f[1]]) 
##            cmds.scale( 1, 1, laenge, o,absolute=True )
##            cmds.move(float(pos[0]),float(pos[1]),float(pos[2]), o, absolute=True )
##            cmds.setAttr(o+'.ry',float(degrees(wz)))
##            cmds.setAttr(o+'.rz',float(degrees(wsz)))         
#
#
    def plane(self,name,center=[0.,0.,0.],size=[1.,1.],cornerPoints=None,visible=1,**kw):
        #polyPlane([axis=[linear, linear, linear]], [
        #    constructionHistory=boolean], [createUVs=int], [height=linear], 
        #    [name=string], [object=boolean], [subdivisionsX=int], 
        #    [subdivisionsY=int], [texture=int], [width=linear])
        if cornerPoints != None :
            for i in range(3):
                size[i] = cornerPoints[1][i]-cornerPoints[0][i]
            for i in range(3):
                center[i]=(cornerPoints[0][i]+cornerPoints[1][i])/2
        node,obj = self.createObjectWithNode("geom", "plane", name)
        p=None
        if parent is not None:
            p=self.getObject(parent)
            self.reParent(node,p)
        #set radius ad quality
        params = node.GetParameters()
        #obj.ulength = size[0]
        #obj.vlength = size[1]
        #
        #if "subdivision" in kw :        
        #    obj.subdivu = kw["subdivision"][0]
        #    obj.subdivv = kw["subdivision"][1]     
        #subdivision parameter ?
        #obj.subdivu = res
        #obj.subdivv = res
        #obj.subdivbase = res
        if "material" in kw :
            self.assignMaterial(node,kw["material"])
        #mat = self.addMaterial("mat"+name,[1.,1.,0.])
        #self.assignMaterial(obj,mat)
        #if pos is not None :

        self.setTranslation(node,center)
        return node,obj


#==============================================================================
#  
#==============================================================================

    def PointCloudObject(self,name,vertices=None,**kw):
        #print "cloud", len(coords)
        coords=vertices
        node,mesh = self.createsNmesh(name,coords,None,None,**kw)
        return None,None

##    def Platonic(self,name,Type,radius,**kw):
##        dicT={"tetra":"Tetrahedron",
##              "hexa":"Tetrahedron",
##              "octa":"Octahedron",
##              "dodeca":"Dodecahedron",
##              "icosa":"Icosahedron"}#BuckyBall ? SoccerBall?
##        dicTF={4:0,
##              6:1,
##              8:2,
##              12:3,
##              20:4}
##        res = 10
##        p=Application.ActiveSceneRoot
##        if "parent" in kw and kw["parent"] is not None :
##            p=self.getObject(kw["parent"])
##        if Type in dicT  :
##           obj = p.AddGeometry(dicT[Type], "MeshSurface")
##        elif Type in dicTF :
##            obj = p.AddGeometry(dicTF[Type], "MeshSurface")
##         #set radius ad quality
##        obj.name=name
##        obj.radius = radius
###        obj.subdivu = res
###        obj.subdivv = res
##        
##        #shape is name+"Shape"
###        if pos is not None :
###            self.setTranslation(name, pos)
##        if "material" in kw and kw["material"] is not None :
##            mat = self.getMaterial(kw["material"])
##            if mat is not None :
##                self.assignMaterial(name,kw["material"])
##        else :
##            if "color" in kw and kw["color"] is not None :
##                mat = self.addMaterial("mat"+name,kw["color"])
##            else :
##                mat = self.addMaterial("mat"+name,[1.,1.,0.])
###            mat = self.getMaterial(name)
##            self.assignMaterial(name,mat)
##        return obj,obj.ActivePrimitive

#
#    def getJointPosition(self,jointname):
#        return self.getTranslation(jointname)
#        #return self.getTranslationOM(jointname)
##        fnJt=oma.MFnIkJoint()
##        mobj = self.getNode(jointname)
##        if not fnJt.hasObj(mobj ) :
##            print "no joint provided!"
##            return None
##        fnJt.setObject(mobj)
##        cvs = om.MPointArray()
##        ncurve.getCVs(cvs,om.MSpace.kPostTransform)
##        return cvs

    def armature(self,basename,coords,scn=None,root=None,**kw):
        #bones are called joint in maya
        #they can be position relatively or globally
        bones=[]
#        center = self.getCenter(coords)
#        parent = self.newEmpty(basename)#this s the root
        p=Application.ActiveSceneRoot
        if "parent" in kw :
            p=self.getObject(kw["parent"])
        if type == "nurb" :
            obj = p.AddGeometry("Grid", "NurbsSurface")
        root = p.Add3dChain()
        root.name =basename
        self.setTranslation(root,coords[0])
        root.Effector.name = basename+"_effector"
        for j in range(1,len(coords)):    
            pos=coords[j]
            #bones.append(c4d.BaseObject(BONE))
            relativePos=[pos[0],pos[1],pos[2]]
            bone = root.AddBone(relativePos,Constant.siChainBonePin,basename+"bone"+str(j))
            bones.append(bone)
        self.setTranslation(root.Effector,coords[-1])
        return root,bones
    
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
#        
#        if len(listeObject) >1:
#            self.JoinsObjects(listeObject)
#        else :
#            self.ObjectsSelection(listeObject,"new")
#        #2- add the joins to the selection
#        self.ObjectsSelection(bones,"add")
#        #3- bind the bones / geoms
#        cmds.bindSkin()
#        #IK:cmds.ikHandle( sj='joint1', ee='joint5', p=2, w=.5 )
#
#    def getParticulesPosition(self,name):
#        name = self.checkName(name)
#        partO=self.getMShape(name) #shape..
#        fnP = omfx.MFnParticleSystem(partO)
#        pos=om.MVectorArray(fnP.count())
#        oriPsType = fnP.renderType()
#        if(oriPsType == omfx.MFnParticleSystem.kTube):
#            fnP.position0(pos);
#        else:
#            fnP.position(pos);
#        return pos
#
#    def setParticulesPosition(self,newPos,PS=None):
#        if PS == None :
#            return
#        obj = self.checkName(PS)
#        partO=self.getMShape(obj) #shape..
#        fnP = omfx.MFnParticleSystem(partO)
#        oriPsType = fnP.renderType()
#        pos=om.MVectorArray(fnP.count())
#        #pts = om.MPointArray(fnP.count())
#        for v in newPos:
#            p = om.MVector( float(v[0]),float(v[1]),float(v[2]) )
#            pos.append(p)
#        #    pts.append(p)
#        #fnP.emit(pts)    
#        fnP.setPerParticleAttribute("position",pos)
#
#    def getParticles(self,name,**kw):
#        PS = self.getObject(name)
#        return PS
#
#    def updateParticles(self,newPos,PS=None,**kw): 
#        if PS == None :
#            return
#        obj = self.checkName(PS)
#        partO=self.getMShape(obj) #shape..
#        fnP = omfx.MFnParticleSystem(partO)
#        oriPsType = fnP.renderType()
#        currentN = fnP.count()
#        N = len(newPos)
#        fnP.setCount(N)
#        pos=om.MVectorArray(fnP.count())
#        #pts = om.MPointArray(fnP.count())
#        for v in newPos:
#            p = om.MVector( float(v[0]),float(v[1]),float(v[2]) )
#            pos.append(p)
#        fnP.setPerParticleAttribute("position",pos)
#        
#    #this update the particle position not the particle number   
#    def updateParticle(self,obj,vertices,faces):
#        obj = self.checkName(obj)
#        partO=self.getMShape(obj) #shape..
#        fnP = omfx.MFnParticleSystem(partO)
#        oriPsType = fnP.renderType()
#        if(oriPsType == omfx.MFnParticleSystem.kTube):
#            if faces is None :
#                return
#            position0 = om.MVectorArray()
#            position1 = om.MVectorArray()
#            for i,f in enumerate(face):
#                coord1 = c = vertices[f[0]]
#                coord2 = vertices[f[1]]
#                p = om.MVector( float(c[0]),float(c[1]),float(c[2]) )
#                #print 'point:: %f, %f, %f' % (p.x, p.y, p.z)
#                position0.append(p)
#                c= coord2
#                p = om.MVector( float(c[0]),float(c[1]),float(c[2]) )
#                #print 'point:: %f, %f, %f' % (p.x, p.y, p.z)
#                position1.append(p)
#            fnP.setPerParticleAttribute("position0",position0)    
#            fnP.setPerParticleAttribute("position1",position1)
#        else :    
#            pos=om.MVectorArray(fnP.count())
#            #pts = om.MPointArray(fnP.count())
#            for v in vertices:
#                p = om.MVector( float(v[0]),float(v[1]),float(v[2]) )
#                pos.append(p)
#            #    pts.append(p)
#            #fnP.emit(pts)    
#            fnP.setPerParticleAttribute("position",pos)
#        #fnP.setPerParticleAttribute? position
#        #stat = resultPs.emit(finalPos);
#
#    def particle(self,name,coord,**kw): 
#        #group_name=None,radius=None,color=None,hostmatrice=None,
#        name = self.checkName(name)
#        if coord is not None :
#            part,partShape=cmds.particle(n=name,p=coord)
#        else :
#            part,partShape=cmds.particle(n=name)
##        instant = cmds.particleInstancer(part, a = 1, object = cyl[0], 
##                position = 'bondPos', aimDirection = 'velocity', 
##                scale = 'bondScaler', 
##                name = (chainName+ '_geoBondsInstances'))
#        return partShape,part
#        
#    def particule(self,name, coord):
#        name = self.checkName(name)
#        if coord is not None :
#            part,partShape=cmds.particle(n=name,p=coord)
#        else :
#            part,partShape=cmds.particle(n=name)
##        instant = cmds.particleInstancer(part, a = 1, object = cyl[0], 
##                position = 'bondPos', aimDirection = 'velocity', 
##                scale = 'bondScaler', 
##                name = (chainName+ '_geoBondsInstances'))
#        return partShape,part
#
#    def metaballs(self,name,coords,radius,scn=None,root=None,**kw):
##        atoms=selection.findType(Atom)
#        #no metaball native in mauya, need to use particle set to blobby surface
#        #use of the point cloud polygon object as the emmiter
#        # name is on the form 'metaballs'+mol.name
##        if scn == None:
##            scn = self.getCurrentScene()
#        #molname = name.split("balls")[1]
#        #emiter = molname+"_cloud"
#        name = self.checkName(name)
#        partShape,part = self.particule(name, coords)
#        #need to change the rep
#        node = self.getNode(partShape)
#        plug = self.getNodePlug("particleRenderType",node) 
#        plug.setInt(7);        #Bloby surface s/w
#        return part,partShape
#        
#    def splinecmds(self,name,coords,type="",extrude_obj=None,scene=None,parent=None):
#        #Type : "sBezier", "tBezier" or ""
#        name = self.checkName(name)
#        if scene is None :
#            scene = self.getCurrentScene()    
#        #parent=newEmpty(name)
#        curve = cmds.curve(n=name,p=coords)
#        #return the name only, but create a transform node with name : name
#        #and create a curveShape named curveShape1
#        objName=cmds.ls("curveShape1")
#        cmds.rename(objName,name+"Shape")
#        cmds.setAttr(name+"Shape"+".dispEP",1)
#        if parent is not None :
#            cmds.parent( name, parent)
#        return name,None

    def extrudeSpline(self,spline,**kw):
        extruder = None
        shape = None
        spline_clone = None
        
        spline = self.getObject(spline)
        spline_name = self.getName(spline)
        
        if "shape" in kw:
            if type(kw["shape"]) == str :
                shape = self.build_2dshape("sh_"+kw["shape"]+"_"+str(spline),
                                           kw["shape"])[0]
            else :
                shape = kw["shape"]        
        if shape is None :
            shape = self.build_2dshape("sh_circle"+str(spline))[0]
        shapename = self.getName(shape)        
        if "extruder" in kw:
            extruder = kw["extruder"]
#        if extruder is None :
#            extruder=self.sweepnurbs("ex_"+spline.GetName())    
#        extrudedmesh = Application.Selection(0)
        if "clone" in kw and kw["clone"] :
            #clon / copy the curve
            Application.Duplicate(spline_name, "", 2, 1, 1, 0, 0, 1, 0, 1, "", "", "", "", "", "", "", "", "", "", 0)
            spline_clone = Application.Selection(0)
            self.resetTransformation(spline_clone)
            spline_clone_name = self.getName(spline_clone)
            #extrude
            Application.ApplyGenOp("Extrusion", "", shapename+";"+spline_clone_name, 3, "siPersistentOperation", "siKeepGenOpInputs", "")
            extruder = Application.Selection(0) 
            self.toggleDisplay(spline_clone_name,False)
            return extruder,shape,spline_clone
        else :
            Application.ApplyGenOp("Extrusion", "", shapename+";"+spline_name, 3, "siPersistentOperation", "siKeepGenOpInputs", "")
            extruder = Application.Selection(0)            
            return extruder,shape
            #setAttr "extrudedSurfaceShape1.simplifyMode" 1;

    def build_2dshape(self,name,type="circle",**kw):
        shapedic = {"circle":"circle",
                    "rectangle":"rectangle"}

        node,obj = h.createObjectWithNode("shape", shapedic[type], name)
        params = node.GetParameters()
        #params.GetParam(0).SetValue(float(radius),0) #cap_Segments
        #params.GetParam(1).SetValue(int(res),0)
        params.Radius = 1.0
        if "parent" in kw :
            p=self.getObject(kw["parent"])
            self.reParent(node,p)
        return node,obj

    def spline(self,name,coords,type="",extrude_obj=None,scene=None,
               parent=None,**kw):
        #Type : 
        if scene is None :
            scene = self.getCurrentScene()    
        p=Application.ActiveSceneRoot
        if parent is not None:
            p=self.getObject(parent)
#        root = scene.Root
        N = len(coords)
        aKnots = [0,0]
        aKnots.extend(range(N-1))
        aKnots.extend([N-2,N-2])
        
        aControlVertex = []
        
        if self.usenumpy:
            coords = numpy.array(coords)
            one = numpy.ones( (coords.shape[0], 1), coords.dtype.char )
            c = numpy.concatenate( (coords, one), 1 )
            aControlVertex = c.flatten().tolist()
        else :
            for c in coords:
                aControlVertex.extend(c+[1])
                
        oNurbsCurve = p.AddNurbsCurve( aControlVertex, aKnots,False, 3, 
                Constant.siNonUniformParameterization, Constant.siSINurbs )
        oNurbsCurve.name = name
        if extrude_obj is not None:
            #means we want to extrude.
            pass
        return oNurbsCurve,oNurbsCurve.ActivePrimitive
        #parent=newEmpty(name)
#        if extrude_obj is not None:
#    Application.ApplyGenOp("Extrusion", "", "circle;arc", 3, "siPersistentOperation", "siKeepGenOpInputs", "")
#            shape,curve = self.omCurve(name+"_spline",coords)
#            #return the name only, but create a transform node with name : name
#            #and create a curveShape named curveShape1
#            if parent is not None :
#                cmds.parent( self.checkName(name)+"_spline", parent)
#            # extrude profile curve along path curve using "flat" method
#            # The extrude type can be distance-0, flat-1, or tube-2
#            extruded=cmds.extrude( extrude_obj,self.checkName(name)+"_spline", 
#                                  et = 2, ucp = 1,n=name, fpt=1,upn=1)
#         
#    
#            #setAttr "extrudedSurfaceShape1.simplifyMode" 1;
#            return name,shape,extruded
#        shape,curve = self.omCurve(name,coords)
#        #return the name only, but create a transform node with name : name
#        #and create a curveShape named curveShape1
#        if parent is not None :
#            cmds.parent( self.checkName(name), parent)
#        return name,shape


#    def getSplinePoints(self,name,convert=False):
#        name = self.checkName(name)
#        ncurve = om.MFnNurbsCurve()
#        mobj = self.getNode(self.checkName(name))
#        if not ncurve.hasObj(mobj ) :
#            mobj = self.getNode(self.checkName(name)+"Shape")
#            if not ncurve.hasObj(mobj) :
#                print "no curve shape provided!"
#                return None
#        ncurve.setObject(mobj)
#        cvs = om.MPointArray()
#        ncurve.getCVs(cvs,om.MSpace.kPostTransform)
#        return cvs
#        
#    def update_spline(self,name,coords):
#        #need to provide the object shape name
#        name = self.checkName(name)
#        ncurve = om.MFnNurbsCurve()
#        mobj = self.getNode(self.checkName(name))
#        if not ncurve.hasObj(mobj ) :
#            mobj = self.getNode(self.checkName(name)+"Shape")
#            if not ncurve.hasObj(mobj) :
#                print "no curve shape provided!"
#                return None
#        ncurve.setObject(mobj)
#        deg = 3; #Curve Degree
#        ncvs = len(coords); #Number of CVs        
#        spans = ncvs - deg # Number of spans
#        nknots = spans+2*deg-1 # Number of knots
#        controlVertices = om.MPointArray()
#        knotSequences = om.MDoubleArray()
#        # point array of plane vertex local positions
#        for c in coords:
#            p = om.MPoint(om.MFloatPoint( float(c[0]),float(c[1]),float(c[2]) ))
#            #print 'point:: %f, %f, %f' % (p.x, p.y, p.z)
#            controlVertices.append(p)
##        for i in range(nknots):
##                knotSequences.append(i)
##                create(controlVertices,knotSequences, deg, 
##                                om.MFnNurbsCurve.kOpen, False, False
#        ncurve.setCVs(controlVertices,om.MSpace.kPostTransform)
##        ncurve.setKnots(knotSequences)
#        ncurve.updateCurve()
#    
#    def omCurve(self,name,coords,**kw):
#        #default value
#        name = self.checkName(name)
#        deg = 3; #Curve Degree
#        ncvs = len(coords); #Number of CVs
#        if kw.has_key("deg"):
#            deg = kw['deg']
#        spans = ncvs - deg # Number of spans
#        nknots = spans+2*deg-1 # Number of knots
#        controlVertices = om.MPointArray()
#        knotSequences = om.MDoubleArray()
#        # point array of plane vertex local positions
#        for c in coords:
#            p = om.MPoint(om.MFloatPoint( float(c[0]),float(c[1]),float(c[2]) ))
#            #print 'point:: %f, %f, %f' % (p.x, p.y, p.z)
#            controlVertices.append(p)
#        
#        for i in range(nknots):
#                knotSequences.append(i)
#            
#        curveFn=om.MFnNurbsCurve()
#
#        curve = curveFn.create(controlVertices,knotSequences, deg, 
#                                om.MFnNurbsCurve.kOpen, False, False)
#        
##        curveFn.setName(name)
#        print (curveFn.partialPathName())
#        print (curveFn.name())
#        shapename = curveFn.name()
#        objName = shapename.split("Shape")[0]
#        n = shapename.split("Shape")[1]
##        objName=cmds.ls("curve1")[0]
#        cmds.rename(objName+n,name)
#        
#        nodeName = curveFn.name() #curveShape
#        cmds.rename(nodeName, name+"Shape")
#    
#        return curveFn, curve
#
#    def createLines(self,name,coords,normal,faces):
#        partShape,part = self.linesAsParticles(name,coords,faces)
#        return part
#        
#    def linesAsParticles(self,name,coords,face):
#        #what about omfx to create the system...
#        name = self.checkName(name)
#        partShape,part = self.particule(name, None)
#        path = self.getMShape(part)
#        node = path.node()
#        depNodeFn = om.MFnDependencyNode( node ) 
#        plug = self.getNodePlug("particleRenderType", node )     
#        plug.setInt(9);        #Tube s/w
#        
#        fnP = omfx.MFnParticleSystem(path)
#        pts = om.MPointArray()
#        position0 = om.MVectorArray()
#        position1 = om.MVectorArray()
#        for i,f in enumerate(face):
#            coord1 = c = coords[f[0]]
#            coord2 = coords[f[1]]
#            p = om.MVector( float(c[0]),float(c[1]),float(c[2]) )
#            #print 'point:: %f, %f, %f' % (p.x, p.y, p.z)
#            position0.append(p)
#            c= coord2
#            p = om.MVector( float(c[0]),float(c[1]),float(c[2]) )
#            #print 'point:: %f, %f, %f' % (p.x, p.y, p.z)
#            position1.append(p)
#            laenge,wsz,wz,c=self.getTubeProperties(coord1,coord2)
#            p = om.MPoint(om.MFloatPoint( float(c[0]),float(c[1]),float(c[2]) ))
#            pts.append(p)
##        fnP.emit(pts)
#        fnP.setPerParticleAttribute("position0",position0)    
#        fnP.setPerParticleAttribute("position1",position1)
#        fnP.emit(pts)
#        return partShape,part
#    
#    def mayaVec(self,v):
#        return om.MFloatPoint( float(v[0]),float(v[1]),float(v[2]) )
#    
#    def getFaces(self,obj,**kw):
##        import numpy
#        pass

    def polygons(self,name,proxyCol=False,smooth=False,color=[[1,0,0],], material=None, **kw):
        normals = kw["normals"]
        p = self.createsNmesh(name,kw['vertices'],normals,kw['faces'],color=color,
                    smooth=smooth,material=material)
        return p

    def ToFace(self,f):
        r = [len(f),]
        r.extend([int(ff) for ff in f])
        return r

    def SetFace(self,mesh,i,f):
        if len(f) == 2 :
            f=[f[0],f[1],f[1]]
            mesh.GetFace(i).setVerts(int(f[0]), int(f[1]), int(f[2]))
        elif len(f) == 4 :
            mesh.GetFace(i).setVerts(int(f[0]), int(f[1]), int(f[2]),int(f[3]))
        else :
            mesh.GetFace(i).setVerts(int(f[0]), int(f[1]), int(f[2]))
         
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
            [ mesh.GetFace(i).setVerts(int(f[0]), int(f[1]), int(f[2])) for i,f in enumerate(nfaces)] 

        mesh.BuildStripsAndEdges()
        mesh.InvalidateGeomCache()
        mesh.InvalidateTopologyCache()
    
        if len(color) == 3 :
            if type(color[0]) is not list :
                color = [color,]                         
        #mesh.SetnumCVerts
        node = self.createNode(obj,name)
        if faces == None or len(faces) == 0 or len(faces[0]) < 3 :
            node.VertTicks(1)#this will show the vertices of the mesh
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
            pass#self.addMod(node)
        return node,tri#,outputMesh
    
    def updatePoly(self,obj,vertices=None,faces=None):
        if type(obj) is str:
            obj = self.getObject(obj)
        if obj is None : return
        #self.updateParticle(obj,vertices=vertices,faces=faces)
        self.updateMesh(obj,vertices=vertices,faces=faces)
                
    def updateMesh(self,meshnode,vertices=None,faces=None, smooth=False,obj=None):#chains.residues.atoms.coords,indices
        #print ("updateMesh ", meshnode,type(meshnode),obj)
        node = None
        #for f in dir(meshnode) : print f
        #remove modifier
        if type(meshnode) is str or type(meshnode) is unicode:
            name = mesh
            node = self.getObject(name)
        else :
            node = meshnode
            name = self.getName(meshnode)
        if type(meshnode) is str or type(meshnode) is unicode:            
            meshnode = self.getObject(meshnode)
        mesh = self.getMesh(meshnode)
        #n = node.GetNumModifiers()
        #for i in range(n):
        #    meshnode.DeleteModifier(0)
        #print "updateMesh mesh", mesh,type(mesh)
        if  mesh is None:
            return
        freed = False
        nv = mesh.GetNumVertices()
        nf = mesh.GetNumFaces()
        print "updateMesh",nv,nf
        if vertices is not None :
            numVertices = len(vertices)
            if numVertices != nv : #especially if less vertex
                mesh.FreeAll()
                freed = True
                print ("reset numVertices")
                mesh.SetNumVerts(numVertices)
            n = mesh.GetNumVertices()
            print (n)
            # point array of plane vertex local positions
            for i in xrange(numVertices):
                if i < n :
                    mesh.SetVert(i,self.FromVec(vertices[i]))
            #[ mesh.SetVert(i, self.FromVec(v)) for i,v in enumerate(vertices)]

        if faces is not None :
            nfaces = self.triangulateFaceArray(faces)
            nF=len(nfaces)
            if nF != nf or freed:
                mesh.SetNumFaces(nF)
            n = mesh.GetNumFaces()
            for i in xrange(nF):
                if i < n :
                    f = nfaces[i]
                    mesh.GetFace(i).setVerts(int(f[0]), int(f[1]), int(f[2]))
                    #mesh.GetFace(i).setEdgeVisFlags(1,1,0)#??
            #[ mesh.GetFace(i).setVerts(int(f[0]), int(f[1]), int(f[2])) for i,f in enumerate(nfaces)] 
        mesh.BuildStripsAndEdges()
        mesh.InvalidateGeomCache()
        mesh.InvalidateTopologyCache()
        #meshnode.TopologyChanged()
        #meshnode.PointsWereChanged()
        #setSmoothFlags
        #mod = self.addMod(meshnode,modType="smooth")
        #should set to auto
        node = None#meshnode.GetWorldSpaceObjectNode()
        if obj is not None :
            node = self.getObject(obj)
        #print ("update mesh",wnode,type(wnode))
        if node is not None and isinstance(node,MaxPlus.INode): #isinstance(ob, MaxPlus.TriObject)
            try :
                node.NotifyChanged()
            except:
                print  ("update MaxPlus sciviz")
            print ("update mesh",name,type(node),type(mesh))
            self.setCurrentSelection(node)
        #meshnode.NotifyDependents(Constants.RefmsgChange)
        #NotifyInputChanged
        self.update()
        
    def ToVec(self,v,pos=True):
        if not isinstance(v,MaxPlus.Point3):
            return v
        return [v.GetX(),v.GetY(),v.GetZ()]

    def FromVec(self,v):
        if isinstance(v,MaxPlus.Point3):
            return v
        else :
            return MaxPlus.Point3(float(v[0]), float(v[1]), float(v[2]))

    def ToMat(self,m,**kw):
        if not isinstance(m,MaxPlus.Matrix3):
            return m
        hm= [[1.,0.,0.,0.],
            [0.,1.,0.,0.],
            [0.,0.,1.,0.],
            [0.,0.,0.,0.]]
        for i,r in enumerate(m) :
            hm[i][:3] = self.ToVec(r)
        return hm

    def FromMat(self,m):
        if isinstance(m,MaxPlus.Matrix3):
            return m
        else :
            return MaxPlus.Matrix3(self.FromVec(m[0][0:3]),
                              self.FromVec(m[1][0:3]),
                              self.FromVec(m[2][0:3]),
                              self.FromVec(m[3][0:3]))

   

#    def alignNormal(self,poly):
#        pass
#
    def triangulate(self,poly):
        pass
#        #select poly
#        doc = self.getCurrentScene()
#        mesh = self.getMShape(poly)
#        meshname= mesh.partialPathName()
#        #checkType
#        if self.getType(meshname) != self.MESH : 
#            return
#        cmds.polyTriangulate(meshname)
#
#GetvertSel
#GetvData
#GetVertex
#GetVertexFloat
#GetFace
#GetFaceCenter
#GetFaceMtlIndex
#GetFaceNormal
#GetFaceVertex
#GetFaceVertices

    def getMeshVertices(self,poly,transform=False,selected = False):
        if type(poly) is str or type(poly) is unicode:
            name = poly
            poly = self.getObject(mesh)
        else :
            name = self.getName(poly)
        node = self.getObject(name)
        #shaded ?
        mesh = self.getMesh(poly)
        m = node.GetWorldTM()
        print "updateMesh mesh", mesh,type(mesh)
        if  mesh is None:
            return
        nv = mesh.GetNumVertices()
        vertices=[]
        for i in xrange(nv):
            v=mesh.GetVertex(i)
            if transform :
                v = m.PointTransform(v)
            vertices.append(self.ToVec(v))
        return vertices
#        meshnode = self.checkIsMesh(poly)
#        if selected :
#            mverts_indice = []
#            verts =[]
#            v = om.MIntArray()
#            vertsComponent = om.MObject()
#            meshDagPath = om.MDagPath()
#            activeList = om.MSelectionList()
#            om.MGlobal.getActiveSelectionList(activeList)
#            selIter = om.MItSelectionList(activeList,om.MFn.kMeshVertComponent)
#            while selIter.isDone():
#                selIter.getDagPath(meshDagPath, vertsComponent);
#                if not vertsComponent.isNull():
#                    # ITERATE THROUGH EACH "FACE" IN THE CURRENT FACE COMPONENT:
#                    vertIter = om.MItMeshVertex(meshDagPath,vertsComponent) 
#                    while vertIter.isDone():
#                        mverts_indice.append(vertIter.index()) #indice of the faces
#                        pts = faceIter.position(om.MSpace.kWorld)
#                        verts.append(self.ToVec(pts))
#                        faces.append(v[0],v[1],v[2])
#                        vertIter.next()
#                selIter.next()
#            return verts,mverts_indice    
#        else :
#            nv = meshnode.numVertices()
#            points = om.MFloatPointArray()
#            meshnode.getPoints(points)
#            vertices = [self.ToVec(points[i]) for i in range(nv)]
#            return vertices
#

    def getMeshNormales(self,poly,transform=False,selected = False):
        if type(poly) is str or type(poly) is unicode:
            name = poly
            poly = self.getObject(mesh)
        else :
            name = self.getName(poly)
        node = self.getObject(name)
        #shaded ?
        mesh = self.getMesh(poly)
        mesh.BuildNormals()#ensure normal are not 0,0,0
        m = node.GetWorldTM()
        print "updateMesh mesh", mesh,type(mesh)
        if  mesh is None:
            return
        nv = mesh.GetNumVertices()
        nn = mesh.GetnormalCount()
        normals=[]
        for i in xrange(nv):
            n=mesh.GetRenderedVertexNormal(i)
            if transform :
                n = m.PointTransform(n)
            normals.append(self.ToVec(n))
        return normals

    def getMeshFaceNormales(self,poly,selected = False,transform=False):
        if type(poly) is str or type(poly) is unicode:
            name = poly
            poly = self.getObject(mesh)
        else :
            name = self.getName(poly)
        node = self.getObject(name)
        #shaded ?
        mesh = self.getMesh(poly)
        m = node.GetWorldTM()
        if  mesh is None:
            return
        nv = mesh.GetNumVertices()
        faces = self.getMeshFaces(poly)
        normals=[[],]*len(faces)
        for j,f in enumerate(faces) :
            #for i in f :
            n=mesh.GetFaceNormal(j)
            if transform :
                n = m.PointTransform(n)
            normals[j] = self.ToVec(n)#should we average ?
##        if selected :
##            v,indice = self.getMeshVertices(poly,selected = selected)
##            vn=[]
##            for i in indice:
##                vn.append(vnormals[i])
##            return vn,indice            
        return normals

#        
#    def getMeshEdges(self,poly,selected = False):
#        #to be tested
#        meshnode = self.checkIsMesh(poly)
#        ne= meshnode.numEdges()
#        edges = []
#        edgeConnects = om.MIntArray()
#        for i in range(ne):
#            meshnode.getEdgeVertices(i,edgeConnects)
#            edges.append(edgeConnects)
#        return edges
#

    def getMeshFaces(self,poly,selected = False):
        if type(poly) is str or type(poly) is unicode:
            name = poly
            poly = self.getObject(mesh)
        else :
            name = self.getName(poly)
        node = self.getObject(name)
        #shaded ?
        mesh = self.getMesh(poly)
        print "updateMesh mesh", mesh,type(mesh)
        if  mesh is None:
            return

        nf = mesh.GetNumFaces()
        faces=[]
        for i in xrange(nf):
            face = mesh.GetFace(i)
            vertices =[face.getVert(j) for j in range(3)]
            faces.append(vertices)
        return faces

    def DecomposeMesh(self,meshnode,edit=True,copy=True,tri=True,transform=True):
##        if tri:
##            self.triangulate(poly)
##        #need the activeprimitive
##        obj = self.getObject(poly)
##        if obj.Type == "#model" :#instance
##            if obj.ModelKind == Constant.siModelKind_Instance :
##                master = obj.InstanceMaster#.ActvePrimitive.Geometry
###                if poly is None :
##                childs = self.getChilds(master)
##                if len(childs):
##                    poly = childs[0].ActivePrimitive.Geometry                        
##            elif obj.ModelKind == Constant.siModelKind_Regular :
##                childs = self.getChilds(obj)
##                if len(childs):
##                    poly = childs[0].ActivePrimitive.Geometry
##                    
##        if type(poly) is str or type(poly) is unicode or type(poly) is list:
##            meshnode = self.getObject(poly).ActivePrimitive.Geometry#dagPath           
##        else :
##            #have to a object shape node or dagpath
##            meshnode = poly

        if type(meshnode) is str or type(meshnode) is unicode:            
            meshnode = self.getObject(meshnode)
        mesh = self.getMesh(meshnode)
        if meshnode is None or mesh is None:
            return


        nv = mesh.GetNumVertices()
        nf = mesh.GetNumFaces()

        if self._usenumpy :
            faces = numpy.array(self.getMeshFaces(meshnode))
            vertices = numpy.array(self.getMeshVertices(meshnode,transform=transform))
            vnormals = numpy.array(self.getMeshNormales(meshnode,transform=transform))#transform normal?
        else :
            faces = self.getMeshFaces(meshnode)
            vertices = self.getMeshVertices(meshnode,transform=transform)
            vnormals = self.getMeshNormales(meshnode,transform=transform)
##        if edit and copy :
##            self.getCurrentScene().SetActiveObject(poly)
##            c4d.CallCommand(100004787) #delete the obj       
        return faces,vertices,vnormals
#
#    def connectAttr(self,shape,i=0,mat=None):
#        if mat is not None :
#            #print shape
#            #print mat+"SG"
#            cmds.isConnected( shape+'.instObjGroups['+i+']', mat+'SG.dagSetMembers')
#            #need to get the shape : name+"Shape"
#            
#    def rotation_matrix(self,angle, direction, point=None,trans=None):
#        """
#        Return matrix to rotate about axis defined by point and direction.
#    
#        """
#        if self._usenumpy:
#            return Helper.rotation_matrix(self,angle, direction, point=point,trans=trans)
#        else :            
#            direction = self.FromVec(direction)
#            direction.normalize()
#            out_mat = [1.0, 0.0, 0.0,0.0,
#                   0.0, 1.0, 0.0,0.0,
#                   0.0, 0.0, 1.0,0.0,
#                   0.0, 0.0, 0.0,1.0]            
#            m = self.matrixp2m(out_mat)
##            m = om.MTransformationMatrix()
#            m.setToRotationAxis (direction,angle)     
#            if point is not None:
#               point = self.FromVec(point) 
#               m.setTranslation(point,om.MSpace.kPostTransform)# = point - (point * m)self.vec2m(trans),om.MSpace.kPostTransform
#            if trans is not None :
#               trans = self.FromVec(trans) 
#               m.setTranslation(trans,om.MSpace.kPostTransform)
##            M = m2matrix(m)               
#            return m        
#                   
#
##===============================================================================
##     Texture Mapping / UV
##===============================================================================
#    def getUV(self,object,faceIndex,vertexIndex,perVertice=True):
#        mesh = self.getMShape(object)
#        meshnode = om.MFnMesh(mesh)
#        #uv=[]
#        u_util = maya.OpenMaya.MScriptUtil()
#        u_util.createFromDouble(0.0)
#        u_ptr = u_util.asFloatPtr()
#        v_util = maya.OpenMaya.MScriptUtil()
#        v_util.createFromDouble(0.0)
#        v_ptr = v_util.asFloatPtr()
#        
#        if perVertice :
#            meshnode.getUV(vertexIndex, u_ptr, v_ptr)            
#            u = u_util.getFloat(u_ptr)
#            v = v_util.getFloat(v_ptr)
#            return [u,v]
#        else :
#            def getuv(faceIndex,iv,u_ptr,v_ptr):
#                meshnode.getPolygonUV(faceIndex,iv,u_ptr,v_ptr)
#                u = u_util.getFloat(u_ptr)
#                v = v_util.getFloat(v_ptr)
#                return [u,v]
#            #uv of the face
#            return [getuv(faceIndex,iv,u_ptr,v_ptr) for iv in range(3)]
##
##
###meshFn = maya.OpenMaya.MFnMesh(node)
###
##u_util = maya.OpenMaya.MScriptUtil()
##u_util.createFromDouble(0.0)
##u_ptr = u_util.asFloatPtr()
##v_util = maya.OpenMaya.MScriptUtil()
##v_util.createFromDouble(0.0)
##v_ptr = v_util.asFloatPtr()
##
##meshFn.getUV(0, u_ptr, v_ptr)
##
##u = u_util.getFloat(u_ptr)
##v = v_util.getFloat(v_ptr))
###getPolygonUVid
###getPolygonUV
##
#    #should be faster ?
#    def setUVs(self,object,uvs):
#        #uvs is a dictionary key are faceindex, values it the actual uv for the 3-4 vertex
#        ob = self.getObject(object)
#        node = self.getNode('mesh_'+ob)
#        meshnode = om.MFnMesh(node)         
#        meshnode.clearUVs()
#        u = om.MFloatArray()
#        v = om.MFloatArray()
#        uvCounts = om.MIntArray()
#        uvIds = om.MIntArray()
#        i = 0
#        for f in uvs:
#            for k,uv in enumerate(uvs[f]):
#                uvIds.append(i)
#                uvCounts.append(len(uvs[f]))
#                u.append(uv[0])
#                v.append(uv[1])
#                #meshnode.setUV(i,uv[0],uv[1])
#                #meshnode.assignUV(f,k,i)
#                i = i +1
#        meshnode.setUVs(u,v)
#        meshnode.assignUVs(uvCounts,uvIds)
#
#    def setUV(self,object,faceIndex,vertexIndex,uv,perVertice=True,uvid=0):
#        ob = self.getObject(object)
#        node = self.getNode('mesh_'+ob)
#        meshnode = om.MFnMesh(node)         
#        for k in range(3):
#            luv = uv[k]
#            meshnode.setUV(uvid,luv[0],luv[1])
#            meshnode.assignUV(faceIndex,k,uvid)
#            uvid = uvid +1
#        return uvid
#
#    def hyperShade_meVertCol(self):
#        #mel command : nodeReleaseCallback graph1HyperShadeEd mentalrayVertexColors1 none;
##        nodeOutlinerInputsCmd connectWindow|tl|cwForm|connectWindowPane|leftSideCW connectWindow|tl|cwForm|connectWindowPane|rightSideCW; nodeOutliner -e -r connectWindow|tl|cwForm|connectWindowPane|rightSideCW;
##        connectAttr -f mesh_MSMS_MOL1crn.colorSet[0].colorName mentalrayVertexColors1.cpvSets[0];
##        // Result: Connected mesh_MSMS_MOL1crn.colorSet.colorName to mentalrayVertexColors1.cpvSets. // 
##        // Result: connectWindow|tl|cwForm|connectWindowPane|rightSideCW // 
#        pass
#                
    def read(self,filename,**kw):
        fileName, fileExtension = os.path.splitext(str(filename))
        doc = self.getCurrentScene()
        r= MaxPlus.FileManager.ImportFromFile(unicode(filename),True)#scale and rotation applyed ??
        #look like there is a 90degree rotation apply
##        if fileExtension == ".fbx" :
##            Application.FBXImport(filename,"")
##        elif fileExtesion == ".obj":
##            Application.ObjImport(filename,1,1,True,True,False,True)
##        elif fileExtesion == ".dae":
##            Application.ImportModel(filename,"","","","","","")

#        else :
#            c4d.documents.LoadFile(filename)
#            doc2 = self.getCurrentScene()
#            #save in c4d
#            c4d.documents.SaveDocument(doc2,fileName+".c4d",c4d.SAVEDOCUMENTFLAGS_DONTADDTORECENTLIST,c4d.FORMAT_C4DEXPORT)
#            #close
#            c4d.documents.KillDocument(doc2)
#            #merge
#            c4d.documents.MergeDocument(doc,fileName+".c4d",c4d.SCENEFILTER_OBJECTS|c4d.SCENEFILTER_MATERIALS)       
    
    def write(self,listObj,**kw):
        pass

