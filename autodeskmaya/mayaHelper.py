
"""
    Copyright (C) <2010>  Autin L. TSRI
    
    This file git_upy/autodeskmaya/mayaHelper.py is part of upy.

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
import sys, os, os.path, struct, math, string
from math import *
#import numpy    
from types import StringType, ListType

import maya
from maya import cmds,mel,utils
import maya.OpenMaya as om
import maya.OpenMayaAnim as oma
import maya.OpenMayaFX as omfx
import pymel.core as pm

#base helper class
from upy import hostHelper
if hostHelper.usenumpy:
    import numpy
    from numpy import matrix

from upy.hostHelper import Helper

lefthand =[[ 1, 0, 0, 0],
[0, 1, 0, 0],
[0, 0, -1, 0],
[0, 0, 0, 1]]

from upy.transformation import decompose_matrix

class MayaSynchro:
    #period problem
    def __init__(self,cb=None, period=0.1):
        self.period = period
        self.callback = None
        self.timeControl = oma.MAnimControl()
        if cb is not None :
            self.doit = cb

    def change_period(self,newP):
        self.period = newP
        self.remove_callback()
        self.set_callback()
        
    def set_callback(self):
        self.callback = om.MTimerMessage.addTimerCallback(self.period,self.doit)

    def remove_callback(self):
        om.MMessage.removeCallback(self.callback)
        
    def doit(self,*args,**kw):#period,time,userData=None):
        pass


class mayaHelper(Helper):
    """
    The maya helper abstract class
    ============================
        This is the maya helper Object. The helper 
        give access to the basic function need for create and edit a host 3d object and scene.
    """
    
    SPLINE = "kNurbsCurve"
    INSTANCE = "kTransform"
    MESH = "kTransform"
    POLYGON = "kMesh"#"kTransform"
#    MESH = "kMesh"
    EMPTY = "kTransform"
    BONES="kJoint"
    PARTICULE = "kParticle"
    SPHERE = "sphere"
    CYLINDER = "cylinder"
    CUBE = "cube"
    IK="kIkHandle"
    msutil = om.MScriptUtil()
    pb = False
    pbinited = False
    host = "maya"
    
    def __init__(self,master=None,**kw):
        Helper.__init__(self)
        self.updateAppli = self.update
        self.Cube = self.box
        self.Box = self.box
        self.Geom = self.newEmpty
        #self.getCurrentScene = c4d.documents.GetActiveDocument
        self.IndexedPolygons = self.polygons
        self.Points = self.PointCloudObject
        self.pb = True
        self.hext = "ma"
        self.timeline_cb={}
        self.LIGHT_OPTIONS = {"Area" : maya.cmds.ambientLight,
                     "Sun" : maya.cmds.directionalLight,
                     "Spot":maya.cmds.spotLight}
        
    def fit_view3D(self):
        pass#
        
    def resetProgressBar(self,max=None):
        """reset the Progress Bar, using value"""
        if self.pb :
            gMainProgressBar = maya.mel.eval('$tmp = $gMainProgressBar');
            maya.cmds.progressBar(gMainProgressBar, edit=True, endProgress=True)
            self.pbinited = False
#            self.pb = False
#        maya.cmds.progressBar(maya.pb, edit=True, maxValue=max,progress=0)
        
    def progressBar(self,progress=None,label=None):
        """ update the progress bar status by progress value and label string
        @type  progress: Int/Float
        @param progress: the new progress
        @type  label: string
        @param label: the new message to put in the progress status
        """                
        
        if self.pb :
            gMainProgressBar = maya.mel.eval('$tmp = $gMainProgressBar');
            if not self.pbinited :
                cmds.progressBar( gMainProgressBar,
                                edit=True,
                                beginProgress=True,
                                isInterruptable=False,
                                status=label,
                                maxValue=100)
#            if progress == 1 :
#                prev = cmds.progressBar(gMainProgressBar,q=1,progress=1)
#                progress = prev/100. + 0.1
#            progress*=100.
            if label is not None and progress is None :
                cmds.progressBar(gMainProgressBar, edit=True, status = label)
            elif label is not None and progress is not None:
                cmds.progressBar(gMainProgressBar, edit=True, progress=progress*100.,status = label)
            elif label is None and progress is not None:
                cmds.progressBar(gMainProgressBar, edit=True, progress=progress*100.)
            if progress == 1 or progress == 100.:
                self.resetProgressBar()
        #maxValue = 100    
        #did not work    
        #maya.cmds.progressBar(maya.pb, edit=True, progress=progress*100)
#            cmds.progressBar(maya.pb, edit=True, step=1)
        #maya.cmds.progressBar(maya.pb, edit=True, step=1)

    def synchronize(self,cb):
        self.timeline_cb[cb] = MayaSynchro(cb=cb,period=0.05)
        self.timeline_cb[cb].set_callback()

    def unsynchronize(self,cb):
        self.timeline_cb[cb].remove_callback()

    def update(self,):
        #how do I update the redraw
        cmds.refresh()
        
    def updateAppli(self,):
        #how do I update the redraw
        cmds.refresh()
        
    def checkName(self,name):
        invalid=[] 
        if type(name) is None :
            print ("None name or not a string",name)
            return ""
        #sometime the name is a list ie [u'name']
        if type(name) is list or type(name) is tuple :
            if len(name) == 1 :
                name = name[0]
            elif len(name) == 2 :
                name = name[1]#transform node
            else :
                name = name[0] #?        
        if  (type(name) is not str and type(name) is not unicode) :
            print ("not a string",name,type(name))
            return ""
        if not len(name):
            print ("empty name",name)
        for i in range(9):
            invalid.append(str(i))       
        if type(name) is list or type(name) is tuple:
            name = name[0]
        if type(name) is not str and type(name) is not unicode:
            name = name.name()
        if len(name) and name[0] in invalid:
            name= name[1:]
        #also remove some character and replace it by _
        name=name.replace(":","_").replace(" ","_").replace("'","").replace("-","_")
        return name    

    def setCurrentSelection(self,obj):
        if obj is None :
            return
        if type (obj) is list or type (obj) is tuple :
            for o in obj :
                cmds.select(self.getObject(o))
        else :
            cmds.select(self.getObject(obj))
    
    def getCurrentSelection(self):
        slist = om.MSelectionList()
        if not slist : 
            return []
        om.MGlobal.getActiveSelectionList(slist)
        selection = []
        slist.getSelectionStrings(selection)
        return selection

    def checkPrimitive(self,object):
        try :
            cmds.polySphere(object,q=1,r=1)
            return "sphere"
        except :
            pass
        try :
            cmds.sphere(object,q=1,r=1)
            return "sphere"
        except :
            pass
        try :
            cmds.polyCube(object,q=1,w=1)
            return "cube"
        except :
            pass
        try :
            cmds.polyCylinder(object,q=1,r=1)
            return "cylinder"
        except :
            pass
        return None
            
    def getType(self,object):
        #first tryto see if  isa primitive
        prim = self.checkPrimitive(object)
        if prim is not None :
            return prim
        object = self.getNode(object)
        if hasattr(object,"apiTypeStr"):
#            print (object.apiTypeStr())
            return object.apiTypeStr()
        else :
#            print (type(object))
            return type(object)
#        return type(object)

    def getMName(self,o):
        return o.name()

    def setName(self,o,name):
        if o is None :
            return
        cmds.rename( self.checkName(o), name, ignoreShape=False) 

    def getName(self,o):
        if o is None: return ""
        if type(o) == str or type(o) == unicode : 
            name = o.replace(":","_").replace(" ","_").replace("'","").replace("-","_")
        elif type(o) == unicode : name = o
        elif type(o) is om.MFnMesh:
            return o
        elif hasattr(o,"name") :
            if type(o.name) == str :
                return o.name
            else : return o.name()
        elif type(o) is list or type(o) is tuple:
            name=o[0]
        else : name=o
        return name

    def getMObject(self,name):
#        Create a selection list, get an MObject of the nodes which name is name
        selectionList = om.MSelectionList() 
        selectionList.add( name ) #should be unic..
        node = om.MObject() 
        selectionList.getDependNode( 0, node )
        #//Create a function set, connect to it,
        fnDep = om.MFnDependencyNode(node)
        #print fnDep.name() #object name
        #print fnDep.typeName() #type name ie mesh, transform etc..
        return node,fnDep
        
    def getObject(self,name,doit=True):
        if type(name) is list or type(name) is tuple :
            if len(name) == 1 :
                name = name[0]
            elif len(name) == 2 :
                name = name[1]#transform node
            else :
                name = name[0] #?
        name=self.checkName(name)
        if name.find(":") != -1 :
            name=name.replace(":","_").replace(" ","_").replace("'","").replace("-","_")
        if doit :
                name=cmds.ls(name)
                if len(name)==0:
                    return None
                if len(name) == 1 :
                    return name[0]
        return name

    def checkIsMesh(self,poly):
        if type(poly) is str or type(poly) is unicode :
            mesh = self.getMShape(poly)#dagPath
        else :
            #have to a object shape node or dagpath
            mesh = poly
        try :
            meshnode = om.MFnMesh(mesh)
            return meshnode
        except :
            return mesh

    def getMesh(self,name):
        mesh = None
        if type(name) != str:
            return name
#        path = om.MDagPath()
        
        try :
            name = self.checkName(name)
            mesh = cmds.ls(name)#NMesh.GetRaw(name)
        except:
            mesh = None
        return mesh
    
    def getMeshFrom(self,obj):
        if type(obj) is not str and type(obj) is not unicode:
            obj = self.getMName(obj)
        return self.getMShape(obj)

    def getTransformNode(self,name):
        if type(name) is list :
            name = name[0]
        if type(name) is str or type(name) is unicode :        
            name = self.checkName(name)
            node = self.getNode(name)
        else :
            node = name        
        dag = om.MFnDagNode(node)
        path = om.MDagPath()
        dag.getPath(path)
        return path.transform(),path
        
    def getMShape(self,name,):
#        print name,type(name)
        if type(name) is list :
            name = name[0]
        if type(name) is str or type(name) is unicode :        
            name = self.checkName(name)
            node = self.getNode(name)
        else :
            node = name        
        dag = om.MFnDagNode(node)
        path = om.MDagPath()
        dag.getPath(path)
#        self.msutil.createFromInt(0) 
#        pInt = self.msutil.asUintPtr() 
#        path.numberOfShapesDirectlyBelow(pInt)
        try :
            path.extendToShape()
            return path
        except :
#            if self.msutil.getUint(pInt)  == 0 :
                node = path.child(0)
                return self.getMShape(node)
        #problem with primitive
#        try :
#            path.extendToShape()
#        except :
#            path = None
#        return path

    def deleteObject(self,obj):
        sc = self.getCurrentScene()
        if type(obj) is str or type(obj) is unicode:
            obj=self.checkName(obj)
        else :
            if type(obj) is list or type(obj) is tuple :
                for o in obj :
                    self.deleteObject(o)
            else :
                obj = obj.name()
        try :
            #print "del",obj
            cmds.delete(obj)
        except:
            print "problem deleting ", obj
    
    #######Special for maya#######################
    def getNode( self,name ):
#        print "getNode",type(name)
#        if type(name) != str :
#            return name
        name = self.checkName(name)
        selectionList = om.MSelectionList() 
        selectionList.add( name ) 
        node = om.MObject() 
        selectionList.getDependNode( 0, node )
        return node
    
    def getNodePlug(self, attrName, nodeObject ):
        """
        example:
        translatePlug = nameToNodePlug( "translateX", perspNode ) 
        print "Plug name: %s" % translatePlug.name() 
        print "Plug value %g" % translatePlug.asDouble()
        """
        depNodeFn = om.MFnDependencyNode( nodeObject ) 
        attrObject = depNodeFn.attribute( attrName ) 
        plug = om.MPlug( nodeObject, attrObject )
        return plug
    ################################################

    def newLocator(self,name,location=None,**kw):
        name = self.checkName(name)
        if name.find(":") != -1 : name=name.replace(":","_")                
        empty=cmds.spaceLocator( n=name, a=True)
        parent = None
        if "parent" in kw :
            parent = kw["parent"]
            self.reParent(empty,parent)
        return str(empty) 
    
    def newEmpty(self,name,location=None,**kw):
        #return self.newLocator(name,location=location, **kw)
        name = self.checkName(name)
        if name.find(":") != -1 : name=name.replace(":","_")
        empty=cmds.group( em=True, n=name)
        parent = None
        if "parent" in kw :
            parent = kw["parent"]
            self.reParent(empty,parent)
        return str(empty)

    def updateMasterInstance(self,master, newobjects,instance=True, **kw):
        """
        Update the reference of the passed instance by adding/removing-hiding objects
        
        * overwrited by children class for each host
        
        >>> sph = helper.Sphere("sph1")
        >>> instance_sph = helper.newInstance("isph1",sph,location = [10.0,0.0,0.0])
        
    
        @type  instance: string/hostObj
        @param instance: name of the instance
        @type  objects: list hostObject/string
        @param objects: the list of object to remove/add to the instance reference   
        @type  add: bool
        @param add: if True add the objec else remove
        @type  hide: bool 
        @param hide: hide instead of remove
        @type kw: dictionary
        @param kw: you can add your own keyword, but it should be interpreted by all host
        """
        #the instance shoud point to an empy that have shape as child
        #what we should do is eitherduplicae or reParent the the new object under this master parent
        #or usethe replace command ? use particule ?
        #replace the mesh node of the master by the given ones....
        #hide and remove every previous children....
        chs = self.getChilds(master)
        for o in chs :
            r=cmds.duplicate(o, renameChildren=True)
            print r
        cmds.delete(chs)#or move or uninstance ?
        if instance :
            n=[]
            for o in newobjects :
                name = self.getName(master)+"Instance"
                i1=self.getObject(name+"1")
                if i1 is not None :
                   cmds.delete(i1) 
                i=self.newInstance(name,o,parent=master)                
        else :
            self.reParent(newobjects,master)
        

    def newMInstance(self,name,object,location=None,
                     hostmatrice=None,matrice=None,parent=None,**kw):
        #first create a MObject?
        #only work on Mes
        name = self.checkName(name)
        fnTrans = om.MFnTransform()
        minstance = fnTrans.create()
        fnTrans.setName(name)
        #now add the child as an instance.
        #print fnTrans.name()
        #is this will work withany object ?
        object=self.getNode(object)#or the shape ?
        fnTrans.addChild(object,fnTrans.kNextPos,True)
        #print name, object , fnTrans
        if matrice is not None  and isinstance(matrice,om.MTransformationMatrix):
            hostmatrice=matrice
            matrice = None
        if hostmatrice is not None  and not isinstance(hostmatrice,om.MTransformationMatrix):
            matrice = hostmatrice
            hostmatrice = None 
        if location is not None :
            fnTrans.setTranslation(self.vec2m(location),om.MSpace.kPostTransform)
        elif hostmatrice is not None :
            fnTrans.set(hostmatrice)
        elif matrice is not None :
            #first convert
            hmatrice = self.matrixp2m(matrice)
            fnTrans.set(hmatrice)
        if parent is not None:
            mparent = self.getNode(parent)
#        onode = om.MFnDagNode(mobj)
#            print "name",fnTrans.name()
            oparent = om.MFnDagNode(mparent)
            oparent.addChild(self.getNode(fnTrans.name()),oparent.kNextPos,False)      
        return fnTrans.name()

    def newInstance(self,name,object,location=None,hostmatrice=None,matrice=None,
                    parent=None,material=None,**kw):
        #instance = None#
        #instance parent = object  
        #instance name = name
#        return  self.newMInstance(name,object,location=location,
#                     hostmatrice=hostmatrice,matrice=matrice,parent=parent,**kw)      
#        
        name = self.checkName(name)
        instance = cmds.instance(object,name=name)  
        if location != None :
            #set the position of instance with location
            cmds.move(float(location[0]),float(location[1]),float(location[2]), name,
                                               absolute=True )
        if matrice is not None :
            if self._usenumpy :
                #matrice = numpy.array(matrice)#matrix(matrice)*matrix(lefthand)#numpy.array(matrice)
                #transpose only rotation
                matrice = numpy.array(matrice).transpose()#we do transpoe hee
                #m = matrice.copy()              
#                m[0,:3]=matrice[0,:3]#thi work with numpy
#                m[1,:3]=matrice[1,:3]
#                m[2,:3]=matrice[2,:3]
                #matrice[:3,:3] = matrice[:3,:3].transpose()
                hm = matrice.reshape(16,).tolist()
                #shoudl I apply some transformatio first ?
                cmds.xform(name, a=True, m=hm,roo="xyz")#a for absolute
            else :
                self.setTransformation(instance[0],mat=matrice)
        #set the instance matrice
        #self.setObjectMatrix(self,object,matrice=matrice,hostmatrice=hostmatrice)
        if parent is not None:
            self.reParent(instance,parent)
        if material is not None:
            self.assignMaterial(instance,material)
        return instance
    #alias
    setInstance = newInstance

    def matrixToParticles(self,name,matrices,vector=[0.,1.,0.],transpose=True,**kw):#edge size ?
        #blender user verex normal for rotated the instance
        #quad up vector should use the inpu vector
        axe=self.rerieveAxis(vector)
        #axe="+Y"
        quad=numpy.array(self.quad[axe])#*10.0
        print ("matrixToParticles",axe,vector,quad)
#        f=[0,1,2,3]
        v=[]
        f=[]
        e=[]
        n=[]        
        vi=0
        #one mat is 
        #rot[3][:3] tr
        # rot[:3,:3] rot
        #create particle system
#        obj = self.checkName(obj)
#        partO=self.getMShape(obj) #shape..
#        fnP = omfx.MFnParticleSystem(partO)
#        oriPsType = fnP.renderType()
        rot=om.MVectorArray()#fnP.count())
        pos=om.MVectorArray()#fnP.count())
        tr=[]
        #set position and rotation
        for i,m in enumerate(matrices):
            mat = numpy.array(m)
            if transpose :
                mat = numpy.array(m).transpose()
#                t = m[3][:3]
#                rot = m[:3,:3]
            scale, shear, euler, translate, perspective=decompose_matrix(mat)
            tr.append(translate.tolist())
            #need euler angle
#            e=self.FromMat(rot).rotation().asEulerRotation()
            p = om.MVector( float(translate[0]),float(translate[1]),float(translate[2]) )
            pos.append(p)
            r = om.MVector( float(euler[0]),float(euler[1]),float(euler[2]) )/(math.pi) *180
            rot.append(r)
#        fnP.setPerParticleAttribute("rotationPP",rot)
#        fnP.setPerParticleAttribute("position",pos)
        part,partShape= pm.nParticle(n=name+"_ps",position = tr)
#        part,partShape=cmds.particle(n=name+"_ps",p=list(tr))
        pm.setAttr('nucleus1.gravity', 0.0)#?
#        cmds.setAttr(partShape+'.computeRotation',1)
        partShape.computeRotation.set(True)
        pm.addAttr(partShape, ln = 'rotationPP', dt = 'vectorArray')
        pm.addAttr(partShape, ln = 'rotationPP0', dt = 'vectorArray')
        particle_fn = omfx.MFnParticleSystem(partShape.__apimobject__())
        particle_fn.setPerParticleAttribute('rotationPP', rot)
        particle_fn.setPerParticleAttribute('rotationPP0', rot)        
        if 'parent' in kw and kw['parent'] is not None: 
            parent = self.getObject(kw['parent'])
            self.reParent(name+"_ps",parent)
        return part,partShape
            
    #particleInstancer  -addObject 
    #-object locator1 -cycle None -cycleStep 1 -cycleStepUnits Frames 
    #-levelOfDetail Geometry -rotationUnits Degrees 
    #-rotationOrder XYZ -position worldPosition -age age crn_A_clouddsShape;
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
        if self.instance_dupliFace:
            v=[0.,1.,0.]
            if "axis" in kw and kw["axis"] is not None:
                v=kw["axis"]
            print ("axis",v)
            o = self.getObject(name+"_pis") 
            if o is None :
#                o,m=self.matrixToVNMesh(name,matrices,vector=v)
                particle,partShape=self.matrixToParticles(name,matrices,vector=v,
                                        transpose=transpose,parent=parent)
                p_instancer = pm.PyNode(pm.particleInstancer(
                    partShape, addObject=True, object=pm.ls(mesh),name=name+"_pis",
                    cycle='None', cycleStep=1, cycleStepUnits='Frames',
                    levelOfDetail='Geometry', rotationUnits='Degrees',
                    rotationOrder='XYZ', position='worldPosition', age='age'))
                pm.particleInstancer(partShape, name = p_instancer, edit = True, rotation = "rotationPP")
                if parent is not None :
                    self.reParent(name+"_pis",parent)
#                cmds.particleInstancer(
#                    partShape, addObject=True, object=self.getMShape(mesh),
#                    cycle='None', cycleStep=1, cycleStepUnits='Frames',
#                    levelOfDetail='Geometry', rotationUnits='Degrees',
#                    rotationOrder='XYZ', position='worldPosition', age='age')        
#                cmds.particleInstancer(partShape, name = "p_instancer", 
#                                       edit = True, rotation = "rotationPP")
            else :
                #update
                pass
            return name+"_pis"
            #rotation checkbox->use normal
        else :
            for i,mat in enumerate(matrices):
                inst = self.getObject(name+str(i))
                if inst is None :
                    #Minstance?
                    if hm : 
                        inst=self.newInstance(name+str(i),mesh,hostmatrice=mat,
                                          parent=parent,globalT=globalT)
                    else :
                        inst=self.newInstance(name+str(i),mesh,matrice=mat,
                                          parent=parent,globalT=globalT)
                instance.append(inst)
            return instance

    def resetTransformation(self,name):
        m= [1.,0.,0.,0.,
            0.,1.,0.,0.,
            0.,0.,1.,0.,
            0.,0.,0.,0.]
        cmds.xform(name, a=True, m=m)

    def setObjectMatrix(self,object,matrice,hostmatrice=None,**kw):
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
        object    = self.getObject(object)     
        if hostmatrice !=None :
            #set the instance matrice
            matrice=hostmatrice
        if matrice != None:
            #convert the matrice in host format
            #set the instance matrice
            pass
        transpose = True
        if "transpose" in kw :
            transpose = kw["transpose"]
        if matrice is not None :
            if self._usenumpy :
                #matrice = numpy.array(matrice)#matrix(matrice)*matrix(lefthand)#numpy.array(matrice)
                #transpose only rotation
                matrice = numpy.array(matrice)
                if transpose :
                    matrice=matrice.transpose()#we do transpoe hee
                #m = matrice.copy()              
    #                m[0,:3]=matrice[0,:3]#thi work with numpy
    #                m[1,:3]=matrice[1,:3]
    #                m[2,:3]=matrice[2,:3]
                #matrice[:3,:3] = matrice[:3,:3].transpose()
                hm = matrice.reshape(16,).tolist()
                #shoudl I apply some transformatio first ?
                cmds.xform(object, a=True, m=hm,roo="xyz")#a for absolute
            else :
                self.setTransformation(object,mat=matrice)
    
    def concatObjectMatrix(self,object,matrice,hostmatrice=None):
        """
        apply a matrix to an hostObject
    
        @type  object: hostObject
        @param object: the object who receive the transformation
        @type  hostmatrice: list/Matrix 
        @param hostmatrice: transformation matrix in host format
        @type  matrice: list/Matrix
        @param matrice: transformation matrix in epmv/numpy format
        """
        #get current transformation
        if hostmatrice !=None :
            #compute the new matrix: matrice*current
            #set the new matrice
            pass
        if matrice != None:
            #convert the matrice in host format
            #compute the new matrix: matrice*current
            #set the new matrice
            pass
    
    def addObjectToScene(self,doc,obj,parent=None,**kw):
        #its just namely put the object under a parent
        #return
        if obj == None : return    
        if parent is not None :
            if type(obj) is list or type(obj) is tuple : 
                if len(obj) == 1 :
                    obj = obj[0]
                elif len(obj) == 2 :
                    obj = obj[1]#transform node
                else :
                    obj = obj[0] #? 
            obj=self.checkName(obj)
            parent=self.checkName(parent)
            #print obj,parent
#            cmds.parent( obj, parent)
            self.parent(obj, parent)

    def parent(self,obj,parent,instance=False):
        if type(parent) == unicode :
            parent = str(parent)
        if type(parent) != str :
            print ("parent is not String ",type(parent)) 
            return
#        print ("parenting ", obj,parent, instance )
        mobj = self.getNode(obj)
        mparent = self.getNode(parent)
#        onode = om.MFnDagNode(mobj)
        oparent = om.MFnDagNode(mparent)
#        print ("parenting dag node", obj,parent, mobj,oparent.kNextPos,instance )
        oparent.addChild(mobj,oparent.kNextPos,instance)      

    def reParent(self,obj,parent,instance=False):
        if parent == None : 
            print ("parent is None")
            return  
        if type(obj) is not list and type(obj) is not tuple :
            obj = [obj,]
        try :
            [self.parent(o,parent,instance=instance) for o in obj]
        except :
            print ("failure")
    def getChilds(self,obj):
        if type(obj) is str or type(obj) is unicode:
            o = self.checkName(obj)
        else :
            o = self.getName(obj)
        childs= cmds.listRelatives(o, c=True)
        if childs is None :
            return []
        else :
            return childs

    def addCameraToScene(self,name,Type='persp',focal=30.0,center=[0.,0.,0.],sc=None):
        # Create a camera and get the shape name.
        cameraName = cmds.camera(n=name)
        cameraShape = cameraName[1]
        
        # Set the focal length of the camera.
        cmds.camera(cameraShape, e=True, fl=focal)
        
        #change the location
        cmds.move(float(center[0]),float(center[1]),float(center[2]), cameraName[0], absolute=True )
        #should I rotate it 
        cmds.rotate( 0, '0', '360deg',cameraName[0] )
        # Change the film fit type.
        #cmds.camera( cameraShape, e=True, ff='overscan' )
        return cameraName

    def addLampToScene(self,name,Type='Area',rgb=[1.,1.,1.],dist=25.0,energy=1.0,
                       soft=1.0,shadow=False,center=[0.,0.,0.],sc=None,**kw):
        #print Type
        #each type have a different cmds
        lcmd = self.LIGHT_OPTIONS[Type]
        light = lcmd(n=name)
#        light = cmds.pointLight(n=name)
        #cmds.pointLight(light,e=1,i=energy,rgb=rgb,ss=soft,drs=dist)
        lcmd(light,e=1,i=energy)
        lcmd(light,e=1,ss=soft)
    #    cmds.pointLight(light,e=1,drs=dist)
        lcmd(light,e=1,rgb=rgb)    
        cmds.move(float(center[0]),float(center[1]),float(center[2]), light, absolute=True )
        return light
        
    def toggleDisplay(self,ob,display,**kw):
#        ob = self.getObject(ob)
#        if ob is None :
#            return
#        ob=self.checkName(ob)
#        if display : 
#            cmds.showHidden(ob)
#        else :     
#            cmds.hide(ob)
        if ob is None :
            return
        node = self.getNode(self.checkName(ob))
        if node is None :
            return        
        attrDis = self.getNodePlug("visibility",node)
        attrDis.setBool(bool(display))

#    def toggleXray(self,object,xray):
#        o = self.getObject(object)
#        cmds.select(o)
#        cmds.displySurface(xRay = True)

    def getVisibility(self,obj,editor=True, render=False, active=False):
        #0 off, 1#on, 2 undef
        node = self.getNode(self.checkName(obj))
        attrDis = self.getNodePlug("visibility",node)
        if editor and not render and not active:
            return attrDis.asBool()
        elif not editor and render and not active:
            return attrDis.asBool()
        elif not editor and not render and active:
            return attrDis.asBool()
        else :
            return attrDis.get(),attrDis.get(),attrDis.get()

    def getTranslation(self,name,absolue=True):
        name = self.checkName(name)
        return self.FromVec(cmds.xform(name,q=1,ws=int(absolue),t=1))

    def getTranslationOM(self,name):
        node = self.getNode(name)
        fnTrans = om.MFnTransform(node,)
        return fnTrans.getTranslation(om.MSpace.kWorld)#kPostTransform)

    def setTranslation(self,name,pos):
        node = self.getNode(name)
        fnTrans = om.MFnTransform(node,)
        newT = self.vec2m(pos)
        fnTrans.setTranslation(newT,om.MSpace.kPostTransform)

    def translateObj(self,obj,position,use_parent=False):
        #is om would be faster ?
        if len(position) == 1 : c = position[0]
        else : c = position
        #print "upadteObj"
        newPos=c#c=c4dv(c)
        o=self.getObject(obj)
        if use_parent : 
            parentPos = self.getPosUntilRoot(obj)#parent.get_pos()
            c = newPos - parentPos
            cmds.move(float(c[0]),float(c[1]),float(c[2]), o, absolute=True )
        else :
            cmds.move(float(c[0]),float(c[1]),float(c[2]), o, absolute=True )
    
    def scaleObj(self,obj,sc):
        obj = self.checkName(obj)
        if type(sc) is float :
            sc = [sc,sc,sc]
        cmds.scale(float(sc[0]),float(sc[1]),float(sc[2]), obj,absolute=True )

    def getScale(self,name,absolue=True,**kw):
        node = self.getNode(name)
        fnTrans = om.MFnTransform(node,)
        # First create an array and a pointer to it
        scaleDoubleArray = om.MScriptUtil()
        scaleDoubleArray.createFromList( [0.0, 0.0, 0.0], 3 )
        scaleDoubleArrayPtr = scaleDoubleArray.asDoublePtr()
        
        # Now get the scale
        fnTrans.getScale( scaleDoubleArrayPtr )
        
        # Each of these is a decimal number reading from the pointer's reference
        x_scale = om.MScriptUtil().getDoubleArrayItem( scaleDoubleArrayPtr, 0 )
        y_scale = om.MScriptUtil().getDoubleArrayItem( scaleDoubleArrayPtr, 1 )
        z_scale = om.MScriptUtil().getDoubleArrayItem( scaleDoubleArrayPtr, 2 )

        return [x_scale,y_scale,z_scale]#kPostTransform) or om.MVector(v[0], v[1], v[2])?

    def getSize(self,obj):
        #take degree
        obj = self.checkName(obj)
        meshnode = self.getMShape(obj)
        try :
            mesh = om.MFnMesh(meshnode)
        except :
            return [1,1,1]
        obj = self.getMName(mesh)
        x=cmds.getAttr(obj+'.width')
        y=cmds.getAttr(obj+'.height')
        z=cmds.getAttr(obj+'.depth') 
        return [x,y,z]
       
    def rotateObj(self,obj,rot):
        #take degree
        obj = self.checkName(obj)  
        cmds.setAttr(obj+'.rx',degrees(float(rot[0])))
        cmds.setAttr(obj+'.ry',degrees(float(rot[1])))
        cmds.setAttr(obj+'.rz',degrees(float(rot[2]))) 

    def getTransformation(self,name):
        node = self.getNode(name)
        fnTrans = om.MFnTransform(node)
        mmat = fnTrans.transformation()
        #maya matrix
        return mmat

    def setTransformation(self,name,mat=None,rot=None,scale=None,trans=None,order="str",**kw):
        node = self.getNode(name)
        fnTrans = om.MFnTransform(node)
        if mat is not None  :
            if isinstance(mat,om.MTransformationMatrix):
                fnTrans.set(mat)
            else :
                fnTrans.set(self.matrixp2m(mat))    
        if trans is not None :
            fnTrans.setTranslation(self.vec2m(trans),om.MSpace.kPostTransform)
        if rot is not None :
            rotation = om.MEulerRotation (rot[0], rot[1], rot[2])
            fnTrans.setRotation(rotation)
        if scale is not None :
            fnTrans.setScale(self.arr2marr(scale))

    def ObjectsSelection(self,listeObjects,typeSel="new"):
        """
        Modify the current object selection.
        
        @type  listeObjects: list
        @param listeObjects: list of object to joins
        @type  typeSel: string
        @param listeObjects: type of modification: new,add,...
    
        """    
        dic={"add":True,"new":False}
        sc = self.getCurrentScene()
        
        for obj in listeObjects:
            cmds.select(self.getObject(obj),add=dic[typeSel])
    
        #Put here the code to add/set an object to the current slection
        #[sc.SetSelection(x,dic[typeSel]) for x in listeObjects]
    
    def JoinsObjects(self,listeObjects):
        """
        Merge the given liste of object in one unique geometry.
        
        @type  listeObjects: list
        @param listeObjects: list of object to joins
        """    
        sc = self.getCurrentScene()
        #put here the code to add the liste of object to the selection
        cmds.select(self.getObject(listeObjects[0]))
        for i in range(1,len(listeObjects)):
            cmds.select(listeObjects[i],add=True)
        cmds.polyUnite()
        #no need to joins? but maybe better
        #then call the command/function that joins the object selected
    #    c4d.CallCommand(CONNECT)
        
    #need face indice
    def color_mesh_perVertex(self,mesh,colors,faces=None,perVertex=True,
                             facesSelection=None,faceMaterial=False):
        if colors[0] is not list and len(colors) == 3 :
           colors = [colors,] 
        if not isinstance(mesh,maya.OpenMaya.MFnMesh):                  
            if self.getType(mesh) != self.POLYGON and self.getType(mesh) != self.MESH:
                return False
        mcolors=om.MColorArray()
        iv=om.MIntArray()
        meshnode = mesh
#        print mesh
        if type(mesh) is str or  type(mesh) is unicode :
            meshnode = self.getMShape(mesh)
            try :
                mesh = om.MFnMesh(meshnode)
            except:
                return False
        mesh.findPlug('displayColors').setBool(True)
        if not isinstance(mesh,maya.OpenMaya.MFnMesh):
            return
        nv=mesh.numVertices()
        nf=mesh.numPolygons()
        mfaces = self.getMeshFaces(meshnode)
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
            mfaces = fsel
            nf = len(fsel)
            nv = len(vsel)
#            print "selected ",face_sel_indice
        #check if its ok
        if len(colors) == nv:
            perVertex = True
        elif len(colors) == nf:
            perVertex = False
        if perVertex:
            N=range(nv)
        else :
            N=range(nf)
        if facesSelection is not None :
            N = face_sel_indice
            perVertex = False
        for k,i in enumerate(N) :
            if len(colors) == 1 : ncolor = colors[0]
            else :
                if k >= len(colors) : 
                    ncolor = [0.,0.,0.] #problem
                else : 
                    ncolor = colors[i]
            #print ncolor
            #if max(ncolor) < 1 : ncolor = map( lambda x: x*255, ncolor)
            col=om.MColor(float(ncolor[0]),float(ncolor[1]),float(ncolor[2]))
            #print ncolor
            mcolors.append(col)
            iv.append(int(i))
#            print "i",i,ncolor
            #mesh.setVertexColor(col,int(i))
        if perVertex:
            mesh.setVertexColors(mcolors,iv)
        else :
#            print iv#should be the fdace index
            mesh.setFaceColors(mcolors,iv)
        return True
        
    ###################MATERIAL CODE FROM Rodrigo Araujo#####################################################################################
    #see http://linil.wordpress.com/2008/01/31/python-maya-part-2/
    def createMaterial(self, name, color, type ):
        name = self.checkName(name)
        mat=cmds.ls(name, mat=True)
        if len(mat)==0: #create only if mat didnt exist already
            #shading group
            shaderSG = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, 
                      name=name+"SG" )
            #material
            cmds.shadingNode( type, asShader=True, name=name )
            #phong ?
            #cmds.setAttr((shader+ '.reflectivity'), 0)# no rayTrace
            #cmds.setAttr((shader+ '.cosinePower'), 3)
            cmds.setAttr( name+".color", color[0], color[1], color[2], 
                                                         type="double3")
            cmds.connectAttr(name+".outColor", shaderSG+".surfaceShader")

    def createTexturedMaterial(self,name,filename):
        name = self.checkName(name)
        mat=cmds.ls(name, mat=True)
        if len(mat)==0: #create only if mat didnt exist already
            #shading group
            shaderSG = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, 
                      name=name+"SG" )
            #material
            cmds.shadingNode("lambert", asShader=True, name=name )
            cmds.connectAttr(name+".outColor", shaderSG+".surfaceShader")
            #create the texture and connect it
            texture = cmds.shadingNode('file', asTexture=True,name=name+"Texture")
            cmds.connectAttr(name+"Texture"+'.outColor', name+".color")
            cmds.setAttr(name+"Texture"+'.fileTextureName', filename, type='string')
        return name

    def create_mMayaMaterials(self):
        existingSGs = cmds.ls(type = 'shadingEngine')
        shaderHits = 0;
        shaderSG, shaderSGAmbOcc, ambOcc, ramp = '', '', '', ''
        for existingSG in existingSGs:
            if mel.eval('attributeExists mMaya_atomShaderSG ' +existingSG):
                shaderSG = existingSG
                shaderHits += 1
            if mel.eval('attributeExists mMaya_atomShaderSGAmbOcc ' +existingSG):
                shaderSGAmbOcc = existingSG
                shaderHits += 1
        
        existingAmbOccs = cmds.ls(type = 'mib_amb_occlusion')
        for existingAmbOcc in existingAmbOccs:
            if mel.eval('attributeExists mMaya_atomShaderAmbOcc ' +existingAmbOcc):
                ambOcc = existingAmbOcc
                shaderHits += 1
        
        existingRamps = cmds.ls(type = 'ramp')
        for existingRamp in existingRamps:
            if mel.eval('attributeExists mMaya_atomShaderRGBRamp ' +existingRamp):
                ramp = existingRamp
                shaderHits += 1
        
        
        if shaderHits == 4:
            return shaderSG, shaderSGAmbOcc, ambOcc, ramp
        elif shaderHits == 0:
            shader = cmds.shadingNode('phong', asShader = 1, name = ("atomShader"))
            cmds.setAttr((shader+ '.reflectivity'), 0)# no rayTrace
            cmds.setAttr((shader+ '.cosinePower'), 3)
            shaderSG = cmds.sets(renderable = 1, noSurfaceShader = 1, empty = 1)
            cmds.addAttr(shaderSG, ln = 'mMaya_atomShaderSG', at = 'bool', h = 1)
            cmds.connectAttr((shader+ '.outColor'), (shaderSG+ '.surfaceShader'))
            
            shaderAmbOcc = cmds.shadingNode('phong', asShader = 1, name = ("atomShaderAmbOcc"))
            cmds.setAttr((shaderAmbOcc+ '.reflectivity'), 0)
            cmds.setAttr((shaderAmbOcc+ '.cosinePower'), 3)
            cmds.setAttr((shaderAmbOcc+ '.ambientColor'), 0.7, 0.7, 0.7)
            cmds.setAttr((shaderAmbOcc+ '.diffuse'), 0.2)
            
            ambOcc = cmds.createNode('mib_amb_occlusion')
            cmds.addAttr(ambOcc, ln = 'mMaya_atomShaderAmbOcc', at = 'bool', h = 1)
            cmds.connectAttr((ambOcc+ '.outValue'), (shaderAmbOcc+ '.color'))
            cmds.connectAttr((shaderAmbOcc+ '.color'), (shaderAmbOcc+ '.specularColor'))
            
            partySampler = cmds.createNode('particleSamplerInfo')
            cmds.connectAttr((partySampler+ '.outTransparency'), (shader+ '.transparency'))
            cmds.connectAttr((partySampler+ '.outIncandescence'), (shader+ '.incandescence'))
            cmds.connectAttr((partySampler+ '.outColor'), (shader+ '.color'))
            
            cmds.connectAttr((partySampler+ '.outTransparency'), (shaderAmbOcc+ '.transparency'))
            cmds.connectAttr((partySampler+ '.outIncandescence'), (shaderAmbOcc+ '.incandescence'))
            cmds.connectAttr((partySampler+ '.outColor'), (ambOcc+ '.bright'))
            
            shaderSGAmbOcc = cmds.sets(renderable = 1, noSurfaceShader = 1, empty = 1)
            cmds.addAttr(shaderSGAmbOcc, ln = 'mMaya_atomShaderSGAmbOcc', at = 'bool', h = 1)
            cmds.connectAttr((shaderAmbOcc+ '.outColor'), (shaderSGAmbOcc+ '.surfaceShader'))
            
            ramp = cmds.createNode('ramp')
            cmds.setAttr((ramp + '.interpolation'), 0)
            cmds.addAttr(ramp, ln = 'mMaya_atomShaderRGBRamp', at = 'bool', h = 1)
            valChangePMA = cmds.createNode('plusMinusAverage')
            cmds.addAttr(valChangePMA, ln = 'mMaya_atomShaderRGBRampPMA', at = 'bool', h = 1)
            cmds.connectAttr((ramp+ '.mMaya_atomShaderRGBRamp'), (valChangePMA+ '.mMaya_atomShaderRGBRampPMA'))
            
            indexDivFactor = 1000.0;
            for elem in elems:
                indexElem = vanRad_CPK[elem][4]
                col = vanRad_CPK[elem][1:-1]
                cmds.setAttr((ramp + '.colorEntryList[' +str(indexElem)+ '].position'), (indexElem/indexDivFactor))
                #cmds.setAttr((ramp + '.colorEntryList[' +str(indexElem)+ '].color'), col[0], col[1], col[2], type = 'double3')
                shade = cmds.shadingNode('surfaceShader', asTexture = 1)
                cmds.setAttr((shade + '.outColor'), col[0], col[1], col[2], type = 'double3')
                cmds.connectAttr((shade+ '.outColor'), (ramp+ '.colorEntryList[' +str(indexElem)+ '].color'))
                cmds.connectAttr((shade+ '.outColor'), (valChangePMA+ '.input3D[' +str(indexElem)+ ']'))
                cmds.rename(shade, elems[elem])
            
            return shaderSG, shaderSGAmbOcc, ambOcc, ramp
        else:
            mel.eval('error "a mMaya default shader has been deleted"')
        
    def addMaterial(self, name, color ):
        if color is None :
            color = (1.,0.,0.)
        name = self.checkName(name)
        mat=cmds.ls(name, mat=True)
        if len(mat)==0: #create only if mat didnt exist already
            #shading group
            cmds.sets( renderable=True, noSurfaceShader=True, empty=True, name=name+"SG" )
            #material
            # = name[1:]
            cmds.shadingNode( 'lambert', asShader=True, name=name )
            cmds.setAttr( name+".color", color[0], color[1], color[2], type="double3")
            cmds.connectAttr(name+".outColor", name+"SG.surfaceShader")
            mat = cmds.ls(name, mat=True)
        return mat
    
    def assignMaterial(self,object,matname,texture = True,**kw):
        object = self.getObject(object,doit=True)
        #print "assign " , matname
        #print matname
        if type(matname) != list :
#            name = name.replace(":","_")
            matname = self.checkName(matname)
            mat=cmds.ls(matname, mat=True)
        else :
            if type(matname[0]) is list :
                mat = matname[0]
                matname = str(matname[0][0])
            else :
                mat = matname
                matname = str(matname[0])
        #print "find " ,mat
        matname = self.checkName(matname)
#        if not mat:
#            self.createMaterial (matname, (1.,1.,1.), 'lambert')
#        conn = cmds.listConnections(cmds.listHistory(object))
##        if len(conn) >= 2:
#            shade = cmds.listHistory(object)[0].split('|')[1]
#            cmds.hyperShade( matname,o=shade,assign=True )
        #print 'assign ',object,matname
#        print mat,matname
        try :
            cmds.sets(object, edit=True, forceElement=matname+"SG")
        except :
            print "problem assigning mat" + matname + " to object "+object
    
    def assignNewMaterial(self, matname, color, type, object):
        print matname, color, type, object
        self.createMaterial (matname, color, type)
        self.assignMaterial (object,matname)
    
    def colorMaterial(self,matname, color):
        matname=self.getMaterial(matname)
        if len(matname)==1:
            matname=matname[0]
        cmds.setAttr( str(matname)+".color", color[0], color[1], color[2], type="double3")

    def getMaterial(self,matname):
        if type(matname) != str :
            return matname
        matname = self.checkName(matname)
        mat=cmds.ls(matname, mat=True)
        if len(mat)==0:
            return None
        else :
            return mat
            
    def getMaterialName(self,mat):
        return str(mat)
        
    def getAllMaterials(self):
        #return unicode list of material
        #mat=getMaterials()
        matlist=cmds.ls(mat=True)#[]
        return matlist

    def getMaterialObject(self,obj):
        obj = self.getObject(obj)
        matnames = cmds.listConnections(cmds.listHistory(obj,f=1),type='lambert')
        return matnames

    def changeObjColorMat(self,obj,color):
        #obj should be the object name, in case of mesh
        #in case of spher/cylinder etc...atom name give the mat name
        #thus  matname should be 'mat_'+obj
        obj = self.checkName(obj)
        matname = "mat_"+str(obj)
        self.colorMaterial(matname,color)
          
    def changeColor(self,mesh,colors,perVertex=True,perObjectmat=None,pb=False,
                    facesSelection=None,faceMaterial=False):
        #if hasattr(geom,'obj'):obj=geom.obj
        #else : obj=geom
        #mesh = self.getMesh(mesh)
        if colors[0] is not list and len(colors) == 3 :
           colors = [colors,]        
        print "change color",type(mesh),mesh
            
        res = self.color_mesh_perVertex(mesh,colors,perVertex=perVertex,
                                  facesSelection=facesSelection,
                                  faceMaterial=faceMaterial)
        
        if not res or len(colors) == 1:
            #simply apply the color/material to mesh
            #get object material, if none create one
#            print "material assign"
            mats = self.getMaterialObject(mesh)
#            print mats
            if not mats :
                self.assignNewMaterial("mat"+self.getName(mesh), colors[0],
                                       'lambert', mesh)
            else :
                self.colorMaterial(mats[0],colors[0])

    def getMaterialProperty(self,material, **kw):
        """
        Change a material properties.
        
        * overwrited by children class for each host
        
        @type  material: string/Material
        @param material: the material to modify
            - color
            - specular
            - ...
        """
        mat =self.getMaterial(material)
        if len(mat)==1:
            mat=mat[0]
        res = {}
        if mat is None :
            return
        if "specular" in kw :
            res["specular"] = True#mat[c4d.MATERIAL_USE_SPECULAR]
        if "specular_color" in kw :
            res["specular_color"] = [0,0,0]#self.ToVec(mat[c4d.MATERIAL_SPECULAR_COLOR],pos=False)
        if "specular_width" in kw :
            res["specular_width"] = 0#mat[c4d.MATERIAL_SPECULAR_WIDTH]
        if "color" in kw :
            res["color"] = cmds.getAttr( str(mat)+".color")[0]
        if "diffuse" in kw :
            res["diffuse"] = cmds.getAttr( str(mat)+".diffuse")[0]
        return res
    
    ###################Meshs and Objects#####################################################################################                                                                        
    def Sphere(self,name,res=16.,radius=1.0,pos=None,color=None,
               mat=None,parent=None,type="nurb"):
        # iMe[atn],node=cmds.sphere(name=name+"Atom_"+atn,r=rad)
        name = self.checkName(name)
        t=res/100.
        if type == "nurb" :
            transform_node,shape = cmds.sphere(name=name,r=radius,sections=int(res),
                                           spans=int(res)) #NurbSphere
        elif type == "poly":
            transform_node,shape = cmds.polySphere( n=name, r=radius,sx=int(res), sy=int(res))

        #shape is name+"Shape"
        if pos is not None :
            cmds.move(float(pos[0]),float(pos[1]),float(pos[2]), 
                    transform_node,absolute=True )
        if mat is not None :
            mat = self.getMaterial(mat)
            if mat is not None :
                self.assignMaterial(transform_node,mat)
        else :
            if color is not None :
                mat = self.addMaterial("mat"+name,color)
            else :
                mat = self.addMaterial("mat"+name,[1.,1.,0.])
#            mat = self.getMaterial(name)
            self.assignMaterial(transform_node,mat)
        if parent is not None :
            self.reParent(transform_node,parent)
        return transform_node,shape

    def updateSphereMesh(self,mesh,verts=None,faces=None,basemesh=None,
                         scale=None,typ=True,**kw):
        #scale or directly the radius..Try the radius
        #scale is actualy the radius
#        name = self.getObject(mesh)
        #would it be faster with openMaya
        mesh = self.checkName(mesh)
        if typ:
            cmds.sphere(mesh,e=1,r=scale)
        else :
            cmds.polySphere(mesh,e=1,r=scale)

    def updateSphereObj(self,obj,coords=None):
        if obj is None or coords is None: return
        obj = self.getObject(obj)
        #would it be faster we transform action
        self.setTranslation(obj,coords)
#        cmds.move(float(coords[0]),float(coords[1]),float(coords[2]), obj, absolute=True )
        
#    def updateSphereObjs(self,g,coords=None):
#        if not hasattr(g,'obj') : return
#        if coords == None :
#            newcoords=g.getVertices()
#        else :
#            newcoords=coords
#        #print "upadteObjSpheres"
#        #again map function ?
#        for i,nameo in enumerate(g.obj):
#            c=newcoords[i]
#            o=getObject(nameo)
#            cmds.move(float(c[0]),float(c[1]),float(c[2]), o, absolute=True )
    
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
                          mesh,colors,scene,parent=None,delete = True):
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
                    self.deleteObject(obj)
                else :
                    self.toggleDisplay(cyls[i],False)
        return cyls


    
    def instancesSphere(self,name,centers,radii,meshsphere,colors,scene,parent=None):
        name = self.checkName(name)
        sphs=[]
        mat = None
        if len(colors) == 1:
            print (colors)
            mat = self.retrieveColorMat(colors[0])
            if mat == None:        
                mat = self.addMaterial('mat_'+name,colors[0])
        for i in range(len(centers)):
            sphs.append(cmds.instance(meshsphere,name=name+str(i)))
            #local transformation ?
            cmds.move(float(centers[i][0]),float(centers[i][1]),float(centers[i][2]),name+str(i))
            cmds.scale(float(radii[i]),float(radii[i]),float(radii[i]), name+str(i),absolute=True )
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
                cmds.move(float(centers[i][0]),float(centers[i][1]),float(centers[i][2]),sphs[i])#name+str(i))
                cmds.scale(float(rad),float(rad),float(rad), sphs[i],absolute=True )
#                sphs[i].SetAbsPos(self.FromVec(centers[i]))
#                sphs[i][905]=c4d.Vector(float(rad),float(rad),float(rad))
                if mat == None : 
                    if colors is not None and i < len(colors) and colors[i] is not None : 
                        mat = self.addMaterial("matsp"+str(i),colors[i])
                if colors is not None and i < len(colors) and colors[i] is not None : 
                    self.colorMaterial(mat,colors[i])
                self.toggleDisplay(sphs[i],True)
            else :
                sphs.append(cmds.instance(meshsphere,name=name+str(i)))
                #local transformation ?
                cmds.move(float(centers[i][0]),float(centers[i][1]),float(centers[i][2]),name+str(i))
                cmds.scale(float(rad),float(rad),float(rad), name+str(i),absolute=True )
                if mat == None : mat = self.addMaterial("matsp"+str(i),colors[i])
                self.assignMaterial(name+str(i),mat)#mat[bl.retrieveColorName(sphColors[i])]
                self.addObjectToScene(scene,sphs[i],parent=parent)
                if mat == None :
                    if colors is not None and  i < len(colors) and colors[i] is not None : 
                        mat = self.addMaterial("matsp"+str(i),colors[i])
                self.addObjectToScene(scene,sphs[i],parent=parent)
                
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
        cmds.orientConstraint( 'persp', object )

    def updateText(self,text,string="",parent=None,size=None,pos=None,font=None):
        text = self.checkName(text)
        if string : cmds.textCurves(text, e=1, t=string )
#        if size is not None :  text[c4d.PRIM_TEXT_HEIGHT]= size
#        if pos is not None : self.setTranslation(text,pos)
#        if parent is not None : self.reParent(text,parent)

    def extrudeText(self,text,**kw):
        tr,parent = self.getTransformNode(text)
        nChild = parent.childCount()
        print nChild
        #dag = om.MFnDagNode(node)
        dnode = om.MFnDependencyNode(parent.transform())
        child_path = om.MDagPath()
        cmd ="constructionHistory=True,normalsOutwards=True,range=False,polygon=1,\
                        tolerance=0.01,numberOfSides=4 ,js=True,width=0 ,depth=0 ,extrudeDepth=0.5,\
                            capSides=4 ,bevelInside=0 ,outerStyle=0 ,innerStyle=0 ,\
                            polyOutMethod=0,polyOutCount=200,polyOutExtrusionType=2 ,\
                            polyOutExtrusionSamples=3,polyOutCurveType=2 ,\
                            polyOutCurveSamples=3,polyOutUseChordHeightRatio=0)"
        for i in range(nChild):
            #get all curve
            node_child = parent.child(i)
            child_tr,child_path = self.getTransformNode(node_child)
            dnode = om.MFnDependencyNode(node_child)               
            nChildChild = child_path.childCount()
            for j in range(nChildChild):
                cmdchilds="cmds.bevelPlus("
                node_child_child = child_path.child(j)
                dnode = om.MFnDependencyNode(node_child_child)
                cmdchilds+='"'+dnode.name()+'",'
                cmdchilds+="n='bevel_"+dnode.name()+str(j)+"',"+cmd
                cmdbis = 'cmds.bevel("'+dnode.name()+'",n="bevel_'+dnode.name()+str(j)+'", ed=0.5)'
                eval(cmdbis)  
                cmds.bevel(e=1,w=0,d=0)


    def Text(self,name="",string="",parent=None,size=5.,pos=None,font='Courier',
             lookAt=False,**kw):
        return_extruder = False
        name = self.checkName(name)
        if "extrude" in kw :
            extruder = None
            if type(kw["extrude"]) is bool and kw["extrude"]:
                pass
        text = cmds.textCurves( n= name, f=font, t=string )
        ## Result: [u'testShape', u'makeTextCurves2'] # 
        if pos is not None :
            #should add -14
            pos[0] = pos[0]-14.0#not center
            self.setTranslation(name+'Shape',pos)
#        if parent is not None:
            self.addObjectToScene(self.getCurrentScene(),name+'Shape',parent=parent)
        if lookAt:
            self.constraintLookAt(name)
        self.scaleObj(text[0],[size,size,size])        
        if "extrude" in kw :
            extruder = None
            #create an extruder
            if type(kw["extrude"]) is bool and kw["extrude"]:
                self.extrudeText(text)
#                extruder = cmds.bevelPlus( text[1], ed=0.5)
#                extruder = cmds.bevel( text, ed=0.5,w=0.0,d=0.0)
                #reparent the extruder ?
#                self.reParent(extruder,parent)
                #po=1, cap=4,
#                extruded=cmds.extrude( extrude_obj,self.checkName(name)+"_spline", 
#                                  et = 2, ucp = 1,n=name, fpt=1,upn=1)    
                return_extruder = True
            else :
                self.extrudeText(text)
#                extruder = cmds.bevel( text, ed=0.5,w=0.0,d=0.0)
                self.reParent(extruder,parent)
#            if extruder is not None :
#                pass
        self.addObjectToScene(self.getCurrentScene(),name+'Shape',parent=parent)
        if return_extruder :
            return text,None        
        return text

    def getBoxSize(self,name):
        #kPolyCube
#        cmds.select(name)
#        print(name)
        sx = cmds.polyCube(name, q=True,w=True)
        sy = cmds.polyCube(name, q=True,h=True)
        sz = cmds.polyCube(name, q=True,d=True)
        return [sx,sy,sz]
        
    def box(self,name,center=[0.,0.,0.],size=[1.,1.,1.],cornerPoints=None,visible=1,
                              mat=None,**kw):
        if cornerPoints != None :
            for i in range(3):
                size[i] = cornerPoints[1][i]-cornerPoints[0][i]
            for i in range(3):
                center[i]=(cornerPoints[0][i]+cornerPoints[1][i])/2.
        res = 15.
        name = self.checkName(name)
        box,shape = cmds.polyCube(name=name,w=float(size[0]),h=float(size[1]),
                                    d=float(size[2]), sx=res, sy=res, sz=res )
        mat = self.addMaterial("mat"+name,[1.,1.,0.])
        self.assignMaterial(box,mat)

        cmds.move(float(center[0]),float(center[1]),float(center[2]),box) 

        parent = None
        if "parent" in kw :
            parent = kw["parent"]
        self.addObjectToScene(self.getCurrentScene(),box,parent=parent)        
        return box,shape

    def updateBox(self,box,center=[0.,0.,0.],size=[1.,1.,1.],cornerPoints=None,
                    visible=1, mat = None):
        box=self.getObject(box)
        if cornerPoints != None :
            for i in range(3):
                size[i] = cornerPoints[1][i]-cornerPoints[0][i]
            for i in range(3):
                center[i]=(cornerPoints[0][i]+cornerPoints[1][i])/2.
        cmds.move(float(center[0]),float(center[1]),float(center[2]),box)
        cmds.polyCube(box,e=1,w=float(size[0]),h=float(size[1]),
                                    d=float(size[2]))

    def Cone(self,name,radius=1.0,length=1.,res=16,pos = None,parent=None):
        name = self.checkName(name)
        diameter = 2*radius
        cone,mesh=cmds.cone(name=name,axis=[0.0,1.0,0.0],hr=length,
                                        r=radius,s=res,nsp=res)
        if pos != None : cmds.move(float(pos[0]),float(pos[1]),float(pos[2]),cone)
        if parent is not None:
            self.reParent(cone,parent)
#        self.addObjectToScene(self.getCurrentScene(),instance)  
        return str(cone),mesh
    
    def Cylinder(self,name,radius=1.,length=1.,res=16,pos = None,parent=None,**kw):
        #import numpy
        name = self.checkName(name)
        diameter = 2*radius
        axis = [0.0,0.0,1.0]
        if "axis" in kw : #orientation
            dic = {"+X":[1.,0.,0.],"-X":[-1.,0.,0.],"+Y":[0.,1.,0.],"-Y":[0.,-1.,0.],
                    "+Z":[0.,0.,1.],"-Z":[0.,0.,-1.]}
            if type(kw["axis"]) is str :
                axis = dic[kw["axis"]]
            else : 
                axis = kw["axis"]        
        cyl,mesh=cmds.polyCylinder(name=name,axis=axis,
                                        r=radius, sx=res, sy=res, sz=5, h=length)
        if pos != None : cmds.move(float(pos[0]),float(pos[1]),float(pos[2]),cyl)
        if parent is not None:
            self.reParent(cyl,parent)
#        self.addObjectToScene(self.getCurrentScene(),instance)  
        return str(cyl),mesh#,mesh

    def oneCylinder(self,name,head,tail,radius=None,instance=None,material=None,
                    parent = None,color=None):
        name = self.checkName(name)
        laenge,wsz,wz,coord=self.getTubeProperties(head,tail)
#        print "oneCylinder instance",instance
        if instance == None : 
            obj = self.Cylinder(name)
        else : 
            obj = self.newMInstance(name,instance,parent=parent)
#            obj = name
#        self.translateObj(name,coord)
#        self.setTranslation(name,coord)
#        #obj.setLocation(float(coord[0]),float(coord[1]),float(coord[2]))
#        cmds.setAttr(name+'.ry',float(degrees(wz)))
#        cmds.setAttr(name+'.rz',float(degrees(wsz)))
#        cmds.scale( 1, 1, laenge, name,absolute=True )
        if radius is None :
            radius= 1.0
        self.setTransformation(obj,trans=coord,scale=[radius, radius, laenge],
                               rot=[0.,wz,wsz])
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

    def updateOneCylinder(self,name,head,tail,radius=None,material=None,color=None):
        name = self.checkName(name)
        laenge,wsz,wz,coord=self.getTubeProperties(head,tail)
        obj = self.getObject(name)
        if radius is None :
            radius= 1.0        
        self.setTransformation(obj,trans=coord,scale=[radius, radius, laenge],
                               rot=[0.,wz,wsz])
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
        
                            
    def updateTubeObj(self,o,coord1,coord2):
        laenge,wsz,wz,pos=self.getTubeProperties(coord1,coord2)
        self.setTransformation(o,trans=pos,scale=[1., 1., laenge],
                               rot=[0.,wz,wsz])
#        cmds.scale( 1., 1., laenge, o,absolute=True )
#        self.setTranslation(o,pos)
##        cmds.move(float(pos[0]),float(pos[1]),float(pos[2]), o, absolute=True )
#        cmds.setAttr(o+'.ry',float(degrees(wz)))
#        cmds.setAttr(o+'.rz',float(degrees(wsz)))
            
    def updateTubeMeshold(self,atm1,atm2,bicyl=False,cradius=1.0,quality=0):
        self.updateTubeObj(atm1,atm2,bicyl=bicyl,cradius=cradius)
    
    def updateTubeMesh(self,mesh,basemesh=None,cradius=1.0,quality=0):
#        print mesh
#        print cradius, mesh
        mesh = self.getObject(str(mesh))
#        print mesh
        maya.cmds.polyCylinder(mesh,e=True,r=cradius)
    
#    def updateTubeObjs(self,g):
#        if not hasattr(g,'obj') : return
#        newpoints=g.getVertices()
#        newfaces=g.getFaces()
#        #print "upadteObjTubes"
#        for i,o in enumerate(g.obj):
#            laenge,wsz,wz,pos=self.getTubeProperties(points[f[0]],points[f[1]]) 
#            cmds.scale( 1, 1, laenge, o,absolute=True )
#            cmds.move(float(pos[0]),float(pos[1]),float(pos[2]), o, absolute=True )
#            cmds.setAttr(o+'.ry',float(degrees(wz)))
#            cmds.setAttr(o+'.rz',float(degrees(wsz)))         


    def plane(self,name,center=[0.,0.,0.],size=[1.,1.],cornerPoints=None,visible=1,**kw):
        #polyPlane([axis=[linear, linear, linear]], [
        #    constructionHistory=boolean], [createUVs=int], [height=linear], 
        #    [name=string], [object=boolean], [subdivisionsX=int], 
        #    [subdivisionsY=int], [texture=int], [width=linear])
        plane,shape = cmds.polyPlane(name=name,w=float(size[0]),h=float(size[1]),
                                                       ax=[0.,0.,1.])
        if cornerPoints != None :
            for i in range(3):
                size[i] = cornerPoints[1][i]-cornerPoints[0][i]
            for i in range(3):
                center[i]=(cornerPoints[0][i]+cornerPoints[1][i])/2.
        cmds.move(float(center[0]),float(center[1]),float(center[2]),plane)
        
        if "subdivision" in kw :
            cmds.polyPlane(plane,e=1,
                           sx=kw["subdivision"][0],sy=kw["subdivision"][1])
        
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
            cmds.polyPlane(plane,e=1,ax=axis)
#        if "material" in kw :
#            texture = plane.MakeTag(c4d.Ttexture)
#            if type(kw["material"]) is c4d.BaseMaterial :
#                texture[1010] = kw["material"]
#            else :
#                texture[1010] = self.addMaterial("plane",[1.,1.,0.])           
        parent = None
        if "parent" in kw :
            parent = kw["parent"]
        self.addObjectToScene(self.getCurrentScene(),plane,parent=parent)
        return plane,shape


    def PointCloudObject(self,name,**kw):
        #print "cloud", len(coords)
        name = self.checkName(name)
        coords=kw['vertices']
#        nface = 0    
#        if kw.has_key("faces"):
#            nface = len(kw['faces'])
#        obj = self.createsNmesh(name+'ds',coords,None,[])
#        return obj[0]
        partShape,part = self.particule(name+"ds", coords)
        return part,partShape

    def getJointPosition(self,jointname):
        return self.getTranslation(jointname)
        #return self.getTranslationOM(jointname)
#        fnJt=oma.MFnIkJoint()
#        mobj = self.getNode(jointname)
#        if not fnJt.hasObj(mobj ) :
#            print "no joint provided!"
#            return None
#        fnJt.setObject(mobj)
#        cvs = om.MPointArray()
#        ncurve.getCVs(cvs,om.MSpace.kPostTransform)
#        return cvs

    def updateArmature(self,basename,coords,listeName=None,scn=None,root=None,**kw):
        for j in range(len(coords)):
            atC=coords[j]
            name = basename+'bone'+str(j)
            if listeName is not None:
                name = listeName[j]
            relativePos=[atC[0],atC[1],atC[2]]
            cmds.joint(self.checkName(name),e=1, p=relativePos)        

    def armature(self,basename,coords,listeName=None,scn=None,root=None,**kw):
        #bones are called joint in maya
        #they can be position relatively or globally
        basename = self.checkName(basename)
        bones=[]
#        center = self.getCenter(coords)
        parent = self.newEmpty(basename)
        self.addObjectToScene(scn,parent,parent=root)
        for j in range(len(coords)):    
            atC=coords[j]
            #bones.append(c4d.BaseObject(BONE))
            relativePos=[atC[0],atC[1],atC[2]]
            name = basename+'bone'+str(j)
            if listeName is not None:
                name = listeName[j]
                
            joint=cmds.joint(n=self.checkName(name), p=relativePos) #named "joint1"
            bones.append(joint)
            if scn != None :
                 if j==0 : self.addObjectToScene(scn,bones[j],parent=parent)
                 else : self.addObjectToScene(scn,bones[j],parent=bones[j-1])
        return parent,bones
    
    def bindGeom2Bones(self,listeObject,bones):
        """
        Make a skinning. Namely bind the given bones to the given list of geometry.
        This function will joins the list of geomtry in one geometry
        
        @type  listeObjects: list
        @param listeObjects: list of object to joins
        @type  bones: list
        @param bones: list of joins
        """    
        
        if len(listeObject) >1:
            self.JoinsObjects(listeObject)
        else :
            self.ObjectsSelection(listeObject,"new")
        #2- add the joins to the selection
        self.ObjectsSelection(bones,"add")
        #3- bind the bones / geoms
        cmds.bindSkin()
        #IK:cmds.ikHandle( sj='joint1', ee='joint5', p=2, w=.5 )

    def getParticulesPosition(self,name):
        name = self.checkName(name)
        partO=self.getMShape(name) #shape..
        fnP = omfx.MFnParticleSystem(partO)
        pos=om.MVectorArray(fnP.count())
        oriPsType = fnP.renderType()
        if(oriPsType == omfx.MFnParticleSystem.kTube):
            fnP.position0(pos);
        else:
            fnP.position(pos);
        return pos

    def setParticulesPosition(self,newPos,PS=None):
        if PS == None :
            return
        obj = self.checkName(PS)
        partO=self.getMShape(obj) #shape..
        fnP = omfx.MFnParticleSystem(partO)
        oriPsType = fnP.renderType()
        pos=om.MVectorArray(fnP.count())
        #pts = om.MPointArray(fnP.count())
        for v in newPos:
            p = om.MVector( float(v[0]),float(v[1]),float(v[2]) )
            pos.append(p)
        #    pts.append(p)
        #fnP.emit(pts)    
        fnP.setPerParticleAttribute("position",pos)

    def getParticles(self,name,**kw):
        PS = self.getObject(name)
        return PS

    def updateParticles(self,newPos,PS=None,**kw): 
        if PS == None :
            return
        obj = self.checkName(PS)
        partO=self.getMShape(obj) #shape..
        fnP = omfx.MFnParticleSystem(partO)
        oriPsType = fnP.renderType()
        currentN = fnP.count()
        N = len(newPos)
        fnP.setCount(N)
        pos=om.MVectorArray(fnP.count())
        #pts = om.MPointArray(fnP.count())
        for v in newPos:
            p = om.MVector( float(v[0]),float(v[1]),float(v[2]) )
            pos.append(p)
        fnP.setPerParticleAttribute("position",pos)

    #this update the particle position not the particle number   
    def updateParticleRotation(self,obj,rotation):
        obj = self.checkName(obj)
        partO=self.getMShape(obj) #shape..
        fnP = omfx.MFnParticleSystem(partO)
        oriPsType = fnP.renderType()
        rot=om.MVectorArray(fnP.count())
        #euler angle?
        for v in rotation:
            p = om.MVector( float(v[0]),float(v[1]),float(v[2]) )
            pos.append(p)
        fnP.setPerParticleAttribute("rotationPP",rot)
        
    #this update the particle position not the particle number   
    def updateParticle(self,obj,vertices,faces):
        obj = self.checkName(obj)
        partO=self.getMShape(obj) #shape..
        fnP = omfx.MFnParticleSystem(partO)
        oriPsType = fnP.renderType()
        if(oriPsType == omfx.MFnParticleSystem.kTube):
            if faces is None :
                return
            position0 = om.MVectorArray()
            position1 = om.MVectorArray()
            for i,f in enumerate(face):
                coord1 = c = vertices[f[0]]
                coord2 = vertices[f[1]]
                p = om.MVector( float(c[0]),float(c[1]),float(c[2]) )
                #print 'point:: %f, %f, %f' % (p.x, p.y, p.z)
                position0.append(p)
                c= coord2
                p = om.MVector( float(c[0]),float(c[1]),float(c[2]) )
                #print 'point:: %f, %f, %f' % (p.x, p.y, p.z)
                position1.append(p)
            fnP.setPerParticleAttribute("position0",position0)    
            fnP.setPerParticleAttribute("position1",position1)
        else :    
            pos=om.MVectorArray(fnP.count())
            #pts = om.MPointArray(fnP.count())
            for v in vertices:
                p = om.MVector( float(v[0]),float(v[1]),float(v[2]) )
                pos.append(p)
            #    pts.append(p)
            #fnP.emit(pts)    
            fnP.setPerParticleAttribute("position",pos)
        #fnP.setPerParticleAttribute? position
        #stat = resultPs.emit(finalPos);

    def particule(self,name, coord,**kw):
        name = self.checkName(name)
        if coord is not None :
            try :
                coord = numpy.array(coord).tolist()
            except :
                pass
            part,partShape=cmds.particle(n=name,p=list(coord))
        else :
            part,partShape=cmds.particle(n=name)
#        instant = cmds.particleInstancer(part, a = 1, object = cyl[0], 
#                position = 'bondPos', aimDirection = 'velocity', 
#                scale = 'bondScaler', 
#                name = (chainName+ '_geoBondsInstances'))
        return partShape,part

    def updateMetaball(self,name,vertices=None):
        if vertices is None :
            return
        self.updateParticle(name,vertices=vertices,faces=None)
        
    def metaballs(self,name,coords,radius,scn=None,root=None,**kw):
#        atoms=selection.findType(Atom)
        #no metaball native in mauya, need to use particle set to blobby surface
        #use of the point cloud polygon object as the emmiter
        # name is on the form 'metaballs'+mol.name
#        if scn == None:
#            scn = self.getCurrentScene()
        #molname = name.split("balls")[1]
        #emiter = molname+"_cloud"
        name = self.checkName(name)
        partShape,part = self.particule(name, coords)
        #need to change the rep
        node = self.getNode(partShape)
        plug = self.getNodePlug("particleRenderType",node) 
        plug.setInt(7);        #Bloby surface s/w
        return part,partShape
        
    def splinecmds(self,name,coords,type="",extrude_obj=None,scene=None,parent=None):
        #Type : "sBezier", "tBezier" or ""
        name = self.checkName(name)
        if scene is None :
            scene = self.getCurrentScene()    
        #parent=newEmpty(name)
        curve = cmds.curve(n=name,p=coords)
        #return the name only, but create a transform node with name : name
        #and create a curveShape named curveShape1
        objName=cmds.ls("curveShape1")
        cmds.rename(objName,name+"Shape")
        cmds.setAttr(name+"Shape"+".dispEP",1)
        if parent is not None :
            cmds.parent( name, parent)
        return name,None

    def extrudeSpline(self,spline,**kw):
        extruder = None
        shape = None
        spline_clone = None

        if "shape" in kw:
            if type(kw["shape"]) == str :
                shape = self.build_2dshape("sh_"+kw["shape"]+"_"+str(spline),
                                           kw["shape"])[0]
            else :
                shape = kw["shape"]        
        if shape is None :
            shapes = self.build_2dshape("sh_circle"+str(spline))[0]
        if "extruder" in kw:
            extruder = kw["extruder"]
#        if extruder is None :
#            extruder=self.sweepnurbs("ex_"+spline.GetName())            
        if "clone" in kw and kw["clone"] :
            spline_clone = cmds.duplicate(spline,n="exd"+str(spline))
            self.resetTransformation(spline_clone)
            extruder=cmds.extrude( shape[0],spline_clone, 
                                  et = 2, ucp = 1,n="ex_"+str(spline), fpt=1,upn=1)
            self.toggleDisplay(spline_clone,False)
            return extruder,shape,spline_clone
        else :
            extruder=cmds.extrude( shape[0],spline, 
                                  et = 2, ucp = 1,n="ex_"+str(spline), fpt=1,upn=1)
            return extruder,shape
            #setAttr "extrudedSurfaceShape1.simplifyMode" 1;

    def build_2dshape(self,name,type="circle",**kw):
        shapedic = {"circle":{"obj":cmds.circle,"size":["r",]},
#                    "rectangle":{"obj":None,"size":[0,0]}
                    }
        shape = shapedic[type]["obj"](n=name, nr=(1, 0, 0), c=(0, 0, 0),r=0.3)
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
        self.addObjectToScene(None,shape)
        return shape,name+"Shape"

    def spline(self,name,coords,type="",extrude_obj=None,scene=None,
               parent=None,**kw):
        #Type : 
        name = self.checkName(name)
        if scene is None :
            scene = self.getCurrentScene()    
        #parent=newEmpty(name)
        if extrude_obj is not None:
            shape,curve = self.omCurve(name+"_spline",coords)
            #return the name only, but create a transform node with name : name
            #and create a curveShape named curveShape1
            if parent is not None :
                cmds.parent( self.checkName(name)+"_spline", parent)
            # extrude profile curve along path curve using "flat" method
            # The extrude type can be distance-0, flat-1, or tube-2
            extruded=cmds.extrude( extrude_obj,self.checkName(name)+"_spline", 
                                  et = 2, ucp = 1,n=name, fpt=1,upn=1)
         
    
            #setAttr "extrudedSurfaceShape1.simplifyMode" 1;
            return name,shape,extruded
        shape,curve = self.omCurve(name,coords)
        #return the name only, but create a transform node with name : name
        #and create a curveShape named curveShape1
        if parent is not None :
            cmds.parent( self.checkName(name), parent)
        return name,shape

    def getSplinePoints(self,name,convert=False):
        name = self.checkName(name)
        ncurve = om.MFnNurbsCurve()
        mobj = self.getNode(self.checkName(name))
        if not ncurve.hasObj(mobj ) :
            mobj = self.getNode(self.checkName(name)+"Shape")
            if not ncurve.hasObj(mobj) :
                print "no curve shape provided!"
                return None
        ncurve.setObject(mobj)
        cvs = om.MPointArray()
        ncurve.getCVs(cvs,om.MSpace.kPostTransform)
        return cvs
        
    def update_spline(self,name,coords):
        #need to provide the object shape name
        name = self.checkName(name)
        ncurve = om.MFnNurbsCurve()
        mobj = self.getNode(self.checkName(name))
        if not ncurve.hasObj(mobj ) :
            mobj = self.getNode(self.checkName(name)+"Shape")
            if not ncurve.hasObj(mobj) :
                print "no curve shape provided!"
                return None
        ncurve.setObject(mobj)
        deg = 3; #Curve Degree
        ncvs = len(coords); #Number of CVs        
        spans = ncvs - deg # Number of spans
        nknots = spans+2*deg-1 # Number of knots
        controlVertices = om.MPointArray()
        knotSequences = om.MDoubleArray()
        # point array of plane vertex local positions
        for c in coords:
            p = om.MPoint(om.MFloatPoint( float(c[0]),float(c[1]),float(c[2]) ))
            #print 'point:: %f, %f, %f' % (p.x, p.y, p.z)
            controlVertices.append(p)
#        for i in range(nknots):
#                knotSequences.append(i)
#                create(controlVertices,knotSequences, deg, 
#                                om.MFnNurbsCurve.kOpen, False, False
        ncurve.setCVs(controlVertices,om.MSpace.kPostTransform)
#        ncurve.setKnots(knotSequences)
        ncurve.updateCurve()
    
    def omCurve(self,name,coords,**kw):
        #default value
        name = self.checkName(name)
        deg = 3; #Curve Degree
        ncvs = len(coords); #Number of CVs
        if kw.has_key("deg"):
            deg = kw['deg']
        spans = ncvs - deg # Number of spans
        nknots = spans+2*deg-1 # Number of knots
        controlVertices = om.MPointArray()
        knotSequences = om.MDoubleArray()
        # point array of plane vertex local positions
        for c in coords:
            p = om.MPoint(om.MFloatPoint( float(c[0]),float(c[1]),float(c[2]) ))
            #print 'point:: %f, %f, %f' % (p.x, p.y, p.z)
            controlVertices.append(p)
        
        for i in range(nknots):
                knotSequences.append(i)
            
        curveFn=om.MFnNurbsCurve()

        curve = curveFn.create(controlVertices,knotSequences, deg, 
                                om.MFnNurbsCurve.kOpen, False, False)
        
#        curveFn.setName(name)
        print (curveFn.partialPathName())
        print (curveFn.name())
        shapename = curveFn.name()
        objName = shapename.split("Shape")[0]
        n = shapename.split("Shape")[1]
#        objName=cmds.ls("curve1")[0]
        cmds.rename(objName+n,name)
        
        nodeName = curveFn.name() #curveShape
        cmds.rename(nodeName, name+"Shape")
    
        return curveFn, curve

    def createLines(self,name,coords,normal,faces):
        partShape,part = self.linesAsParticles(name,coords,faces)
        return part
        
    def linesAsParticles(self,name,coords,face):
        #what about omfx to create the system...
        name = self.checkName(name)
        partShape,part = self.particule(name, None)
        path = self.getMShape(part)
        node = path.node()
        depNodeFn = om.MFnDependencyNode( node ) 
        plug = self.getNodePlug("particleRenderType", node )     
        plug.setInt(9);        #Tube s/w
        
        fnP = omfx.MFnParticleSystem(path)
        pts = om.MPointArray()
        position0 = om.MVectorArray()
        position1 = om.MVectorArray()
        for i,f in enumerate(face):
            coord1 = c = coords[f[0]]
            coord2 = coords[f[1]]
            p = om.MVector( float(c[0]),float(c[1]),float(c[2]) )
            #print 'point:: %f, %f, %f' % (p.x, p.y, p.z)
            position0.append(p)
            c= coord2
            p = om.MVector( float(c[0]),float(c[1]),float(c[2]) )
            #print 'point:: %f, %f, %f' % (p.x, p.y, p.z)
            position1.append(p)
            laenge,wsz,wz,c=self.getTubeProperties(coord1,coord2)
            p = om.MPoint(om.MFloatPoint( float(c[0]),float(c[1]),float(c[2]) ))
            pts.append(p)
#        fnP.emit(pts)
        fnP.setPerParticleAttribute("position0",position0)    
        fnP.setPerParticleAttribute("position1",position1)
        fnP.emit(pts)
        return partShape,part
    
    def mayaVec(self,v):
        return om.MFloatPoint( float(v[0]),float(v[1]),float(v[2]) )
    
    def getFaces(self,obj,**kw):
#        import numpy
        node = self.getNode('mesh_'+obj)
        meshnode = om.MFnMesh(node) 
        triangleCounts  =om.MIntArray()
        triangleVertices= om.MIntArray()     
        meshnode.getTriangles(triangleCounts,triangleVertices)        
        if self._usenumpy :
            return numpy.array(triangleVertices).reshape((len(triangleVertices)/3,3))
        else :
            return triangleVertices

    def polygons(self,name,proxyCol=False,smooth=False,color=[[1,0,0],], material=None, **kw):
        normals = kw["normals"]
        name,meshFS = self.createsNmesh(name,kw['vertices'],normals,kw['faces'],color=color,
                    smooth=smooth,material=material)
        return name

    def createsNmesh(self,name,vertices,normal,faces,color=[[1,0,0],],smooth=False,
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
        if len(color) == 3 :
            if type(color[0]) is not list :
                color = [color,]                         
        outputMesh = om.MObject()
        #print outputMesh.name()
        #cmds.rename(outputMesh.name(), name)
        #test=cmds.createNode( 'transform', n='transform1' )
        name=name.replace(":","_")
        name=name.replace("-","_")
        name=name.replace("'","")
        name=name.replace('"',"")
        name=self.checkName(name)
        #print "NMesh ",name
        numFaces = 0
        if faces is not None :
            numFaces = len(faces)
        numVertices = len(vertices)
        # point array of plane vertex local positions
        points = om.MFloatPointArray()
        for v in vertices:
            points.append(self.mayaVec(v))
        #mayaVertices=map(mayaVec,vertices)
        #map(points.append,mayaVertices)
        # vertex connections per poly face in one array of indexs into point array given above
        faceConnects = om.MIntArray()
        for f in faces:
            for i in f : 
                 faceConnects.append(int(i))
        # an array to hold the total number of vertices that each face has
        faceCounts = om.MIntArray()    
        for c in range(0,numFaces,1):
            faceCounts.append(int(len(f)))
        
        #create mesh object using arrays above and get name of new mesh
        meshFS = om.MFnMesh()
        newMesh = meshFS.create(numVertices, numFaces, points, faceCounts, 
                                faceConnects, outputMesh)
        #    meshFS.updateSurface()
        nodeName = meshFS.name()
        cmds.rename(nodeName, "mesh_"+name)
        #print 'Mesh node name is: %s' % nodeName
        objName=cmds.ls("polySurface1")[0]
        cmds.rename(objName,name)
        #newName should bydefault polySurface something
        #     assign new mesh to default shading group
        if color is not None and len(color) > 1:
            self.color_mesh_perVertex(meshFS,color)
        doMaterial = True
        if type(material) is bool :
            doMaterial = material        
        if doMaterial:
            if material == None :
                if len(name.split("_")) == 1 : splitname = name
                else :
                    splitname = name.split("_")[1]  
                #print name,name[:4],splitname,splitname[:4]
                self.assignNewMaterial( "mat_"+name, color[0],'lambert' ,"mesh_"+name)
            else :
                self.assignMaterial("mesh_"+name,material)    
        if "parent" in kw :
            parent = kw["parent"]
#            print "reparent ", name,parent
            self.reParent(name,parent)
        return name,meshFS#,outputMesh

    def updatePoly(self,obj,vertices=None,faces=None):
        if type(obj) is str:
            obj = self.getObject(obj)
            if obj is None : return
            node = self.getMShape(self.checkName(obj))
            if node.hasFn(om.MFn.kMesh):
                self.updateMesh(obj,vertices=vertices,faces=faces)
            elif node.hasFn(om.MFn.kParticle):
                self.updateParticle(obj,vertices=vertices,faces=faces)
                
    def updateMesh(self,meshnode,vertices=None,faces=None, smooth=False,**kw):#chains.residues.atoms.coords,indices
#        print meshnode,type(meshnode)
        if type(meshnode) is str or type(meshnode) is unicode:            
            node = self.getMShape(self.checkName(meshnode))#self.getNode(self.checkName(meshnode))
            meshnode = om.MFnMesh(node)
#            meshnode = self.getObject(meshnode,doit=True)
        if meshnode is None:
            return
        nv = meshnode.numVertices()
        nf = meshnode.numPolygons()
        if vertices is not None :
            numVertices = len(vertices)
            # point array of plane vertex local positions
            points = om.MFloatPointArray()
            for v in vertices:
                points.append(self.mayaVec(v))
        else :
            return
            #numVertices = nv
        if faces is not None :
            numFaces = len(faces)
        else :
            numFaces = nf
            faces = []
        faceConnects = om.MIntArray()
        for f in faces:
            for i in f : 
                 faceConnects.append(int(i))
        # an array to hold the total number of vertices that each face has
        faceCounts = om.MIntArray()    
        for c in range(0,numFaces,1):
            faceCounts.append(int(len(f)))
        #newMesh = meshFS.create(numVertices, numFaces, points, faceCounts, faceConnects, outputMesh)
        result = meshnode.createInPlace(numVertices, numFaces, points, faceCounts, faceConnects)
        meshnode.updateSurface()

    def ToVec(self,v,**kw):
        if hasattr(v,"x") :
            return [v.x,v.y,v.z]
        else :
            return v

    def arr2marr(self,v):
        #from http://www.rtrowbridge.com/blog/2009/02/maya-api-docs-demystified-for-python-users/
        self.msutil.createFromList( v, len(v) )
        doubleArrayPtr = self.msutil.asDoublePtr()
        return doubleArrayPtr

#    def vecp2m(self,v):
#        #from http://www.rtrowbridge.com/blog/2009/02/maya-api-docs-demystified-for-python-users/
#        doubleArrayPtr = self.arr2marr(v)
#        vec = om.MVector( doubleArrayPtr )
#        return vec

    def FromVec(self,v,pos=True):
        if isinstance(v,om.MVector):
            return v
        else :
            return om.MVector(v[0], v[1], v[2])
   
    def vec2m(self,v):
        if isinstance(v,om.MVector):
            return v
        else :
            return om.MVector(float(v[0]), float(v[1]), float(v[2]))

    def ToMat(self,mat,**kw):
        #maya - > python
        return self.m2matrix(mat)

    def FromMat(self,mat,**kw):
        #pythn->maya
        return self.matrixp2m(mat)
        
    def matrixp2m(self,mat):
        #from http://www.rtrowbridge.com/blog/2009/02/python-api-mtransformationmatrixgetrotation-bug/
        if isinstance(mat,om.MTransformationMatrix)  :
            return mat
        getMatrix = om.MMatrix()
        matrixList = mat#mat.transpose().reshape(16,)
        om.MScriptUtil().createMatrixFromList(matrixList, getMatrix)
        mTM = om.MTransformationMatrix( getMatrix )
        rotOrder = om.MTransformationMatrix().kXYZ
        return mTM
    
    def m2matrix(self,mMat):
        #return mMat
        #do we use numpy
        if isinstance(mMat,om.MTransformationMatrix)  :
            matrix = mMat.asMatrix()
        elif isinstance(mMat,om.MMatrix):
            matrix = mMat
        else :
            return mMat
        us=om.MScriptUtil()
        out_mat = [0.0, 0.0, 0.0,0.0,
           0.0, 0.0, 0.0,0.0,
           0.0, 0.0, 0.0,0.0,
           0.0, 0.0, 0.0,0.0]
        us.createFromList( out_mat, len(out_mat) )   
        ptr1 = us.asFloat4Ptr()        
        matrix.get(ptr1)
        res_mat = [[0.0, 0.0, 0.0,0.0],
                   [0.0, 0.0, 0.0,0.0],
                   [0.0, 0.0, 0.0,0.0],
                   [0.0, 0.0, 0.0,0.0]]
        for i in range(4):
            for j in range(4):
                val = us.getFloat4ArrayItem(ptr1, i,j)
                res_mat[i][j]=val
        return res_mat
  

    def alignNormal(self,poly):
        pass

    def triangulate(self,poly):
        #select poly
        doc = self.getCurrentScene()
        mesh = self.getMShape(poly)
        meshname= mesh.partialPathName()
        #checkType
        if self.getType(meshname) != self.MESH : 
            return
        cmds.polyTriangulate(meshname)

    def getMeshVertices(self,poly,transform=False,selected = False):
        meshnode = self.checkIsMesh(poly)
        if selected :
            mverts_indice = []
            verts =[]
            v = om.MIntArray()
            vertsComponent = om.MObject()
            meshDagPath = om.MDagPath()
            activeList = om.MSelectionList()
            om.MGlobal.getActiveSelectionList(activeList)
            selIter = om.MItSelectionList(activeList,om.MFn.kMeshVertComponent)
            while selIter.isDone():
                selIter.getDagPath(meshDagPath, vertsComponent)
                if not vertsComponent.isNull():
                    # ITERATE THROUGH EACH "FACE" IN THE CURRENT FACE COMPONENT:
                    vertIter = om.MItMeshVertex(meshDagPath,vertsComponent) 
                    while vertIter.isDone():
                        mverts_indice.append(vertIter.index()) #indice of the faces
                        pts = faceIter.position(om.MSpace.kWorld)
                        verts.append(self.ToVec(pts))
                        faces.append(v[0],v[1],v[2])
                        vertIter.next()
                selIter.next()
            return verts,mverts_indice    
        else :
            nv = meshnode.numVertices()
            points = om.MFloatPointArray()
            meshnode.getPoints(points)
            vertices = [self.ToVec(points[i]) for i in range(nv)]
            return vertices
        
    def getMeshNormales(self,poly,selected = False):
        meshnode = self.checkIsMesh(poly)
        nv = meshnode.numNormals()
        normals = om.MFloatVectorArray()
        meshnode.getVertexNormals(False,normals)
        vnormals = [self.ToVec(normals[i]) for i in range(nv)]
        if selected :
            v,indice = self.getMeshVertices(poly,selected = selected)
            vn=[]
            for i in indice:
                vn.append(vnormals[i])
            return vn,indice
        return vnormals
        
    def getMeshEdges(self,poly,selected = False):
        #to be tested
        meshnode = self.checkIsMesh(poly)
        ne= meshnode.numEdges()
        edges = []
        edgeConnects = om.MIntArray()
        for i in range(ne):
            meshnode.getEdgeVertices(i,edgeConnects)
            edges.append(edgeConnects)
        return edges
        
    def getMeshFaces(self,poly,selected = False):
        meshnode = self.checkIsMesh(poly)
        faceConnects = om.MIntArray()
        faceCounts = om.MIntArray()
        meshnode.getTriangles(faceCounts,faceConnects)
        if selected :
            mfaces_indice = []
            faces =[]
            v = om.MIntArray()
            faceComponent = om.MObject()
            meshDagPath = om.MDagPath()
            activeList = om.MSelectionList()
            om.MGlobal.getActiveSelectionList(activeList)
            selIter = om.MItSelectionList(activeList,om.MFn.kMeshPolygonComponent)            
#            print "itersel",selIter.isDone()
            while 1:
                selIter.getDagPath(meshDagPath, faceComponent);
#                print "faces ?",faceComponent.isNull()
                if not faceComponent.isNull():
#                    print ' ITERATE THROUGH EACH "FACE" IN THE CURRENT FACE COMPONENT:'
                    faceIter = om.MItMeshPolygon(meshDagPath,faceComponent) 
                    while 1:
                        mfaces_indice.append(faceIter.index()) #indice of the faces
                        faceIter.getVertices(v)
                        faces.append([v[0],v[1],v[2]])
                        faceIter.next()
                        if faceIter.isDone() : break
                selIter.next()
                if selIter.isDone() : break
            return faces,mfaces_indice
        if self._usenumpy : 
            return numpy.array(faceConnects).reshape((len(faceConnects)/3,3))
        else :
            return faceConnects
        
    def DecomposeMesh(self,poly,edit=True,copy=True,tri=True,transform=True,**kw):
#        import numpy
        if tri:
            self.triangulate(poly)
        if type(poly) is str or type(poly) is unicode or type(poly) is list:
            mesh = self.getMShape(poly)#dagPath           
        else :
            #have to a object shape node or dagpath
            mesh = poly
        print ("mesh ", mesh)
        if self.getType(mesh.partialPathName()) != self.POLYGON :
            if self.getType(mesh.partialPathName()) == self.PARTICULE:
                v = self.getParticulesPosition(mesh.partialPathName())
                return None,v,None
            return None,None,None
        #again problem with instance.....
        meshnode = om.MFnMesh(mesh)
        print ("meshnode",meshnode)
        fnTrans = om.MFnTransform(self.getTransformNode(poly)[0])
        print ("fnTrans",fnTrans)
#        fnTrans = om.MFnTransform(mesh.transform())
       #get infos
        nv = meshnode.numVertices()
        nf = meshnode.numPolygons()
#        m = om.MFloatMatrix()
        points = om.MFloatPointArray()
        normals = om.MFloatVectorArray()
        faceConnects = om.MIntArray()
        faceCounts = om.MIntArray()
        meshnode.getPoints(points)
        #meshnode.getNormals(normals)
        meshnode.getVertexNormals(False,normals)
        meshnode.getTriangles(faceCounts,faceConnects)  
        fnormals=[]
        if self._usenumpy :
            faces = numpy.array(faceConnects).reshape((len(faceConnects)/3,3))
        else :
            faces = faceConnects
        vertices = [self.ToVec(points[i]) for i in range(nv)]
        vnormals = [self.ToVec(normals[i]) for i in range(nv)]
        #remove the copy if its exist? or keep it ?
        #need to apply the transformation
        if transform :
            #node = self.getNode(mesh)
            #fnTrans = om.MFnTransform(mesh)
            mmat = fnTrans.transformation()           
            if self._usenumpy :            
                mat = self.m2matrix(mmat)
                vertices = self.ApplyMatrix(vertices,numpy.array(mat).transpose())
                vnormals = self.ApplyMatrix(vnormals,numpy.array(mat).transpose())#??
            else :
                out_mat = [0.0, 0.0, 0.0,0.0,
                   0.0, 0.0, 0.0,0.0,
                   0.0, 0.0, 0.0,0.0,
                   0.0, 0.0, 0.0,0.0]
                self.msutil.createFromList( out_mat, len(out_mat) )   
                ptr1 = self.msutil.asFloat4Ptr()                    
                mmat.asMatrix().get(ptr1)
                m = om.MFloatMatrix(ptr1)
                vertices = []                
                for i in range(nv) :
                    v = points[i]*m
                    vertices.append(self.ToVec(v))
#                vertices = [self.ToVec(p*m) for p in points]
#        if edit and copy :
#            self.getCurrentScene().SetActiveObject(poly)
#            c4d.CallCommand(100004787) #delete the obj       
        print ("ok",len(faces),len(vertices),len(vnormals))        
        if "fn" in kw and kw["fn"] :
            fnormals = []
            p = om.MVector( 0.,0.,0. )
            for i in range(len(faces)) :
                meshnode.getPolygonNormal(i,p,om.MSpace.kWorld)#kPostTransform
                fnormals.append(self.ToVec(p))
            return faces,vertices,vnormals,fnormals
        else :
            return faces,vertices,vnormals

    def connectAttr(self,shape,i=0,mat=None):
        if mat is not None :
            #print shape
            #print mat+"SG"
            cmds.isConnected( shape+'.instObjGroups['+i+']', mat+'SG.dagSetMembers')
            #need to get the shape : name+"Shape"
            
    def rotation_matrix(self,angle, direction, point=None,trans=None):
        """
        Return matrix to rotate about axis defined by point and direction.
    
        """
        if self._usenumpy:
            return Helper.rotation_matrix(angle, direction, point=point,trans=trans)
        else :            
            direction = self.FromVec(direction)
            direction.normalize()
            out_mat = [1.0, 0.0, 0.0,0.0,
                   0.0, 1.0, 0.0,0.0,
                   0.0, 0.0, 1.0,0.0,
                   0.0, 0.0, 0.0,1.0]            
            m = self.matrixp2m(out_mat)
#            m = om.MTransformationMatrix()
            m.setToRotationAxis (direction,angle) 	
            if point is not None:
               point = self.FromVec(point) 
               m.setTranslation(point,om.MSpace.kPostTransform)# = point - (point * m)self.vec2m(trans),om.MSpace.kPostTransform
            if trans is not None :
               trans = self.FromVec(trans) 
               m.setTranslation(trans,om.MSpace.kPostTransform)
#            M = m2matrix(m)               
            return m        
                   
#==============================================================================
# properties objec
#==============================================================================
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
        res = []
        if "pos" in key :
            res.append(self.ToVec(self.getTranslation(obj)))
        if "scale" in key :
            res.append(self.ToVec(self.getScale(obj)))

        if "rotation" in key :
            mo = self.getTransformation(obj)
            m = self.ToMat(mo)#.transpose()
            mws = m.transpose()
            rotMatj = mws[:]
            rotMatj[3][:3]*=0.0
            res.append(rotMatj)
        if self.getType(obj) == self.SPHERE :
            for k in key :
                if k == "radius" :
                    try :
                        r=cmds.polySphere(obj,q=1,r=1)
                    except :
                        r=cmds.sphere(obj,q=1,r=1) 
                    res.append(r)
        if self.getType(obj) == self.CYLINDER :
            for k in key :
                if k == "radius" :
                    r=cmds.polyCylinder(obj,q=1,r=1)
                    res.append(r)
                elif k == "length" :
                    h=cmds.polyCylinder(obj,q=1,h=1)
                    res.append(h)
                elif k == "axis" :
                    ax = cmds.polyCylinder(obj,q=1,axis=1)
                    res.append(ax)
        if self.getType(obj) == self.CUBE :
            for k in key :
                if k == "length" :
                    l = self.getBoxSize(obj)#cmds.polyCube(obj, q=True,h=True)
                    res.append(l)
        return res

#===============================================================================
#     Texture Mapping / UV
#===============================================================================
    def getUV(self,object,faceIndex,vertexIndex,perVertice=True):
        mesh = self.getMShape(object)
        meshnode = om.MFnMesh(mesh)
        #uv=[]
        u_util = maya.OpenMaya.MScriptUtil()
        u_util.createFromDouble(0.0)
        u_ptr = u_util.asFloatPtr()
        v_util = maya.OpenMaya.MScriptUtil()
        v_util.createFromDouble(0.0)
        v_ptr = v_util.asFloatPtr()
        
        if perVertice :
            meshnode.getUV(vertexIndex, u_ptr, v_ptr)            
            u = u_util.getFloat(u_ptr)
            v = v_util.getFloat(v_ptr)
            return [u,v]
        else :
            def getuv(faceIndex,iv,u_ptr,v_ptr):
                meshnode.getPolygonUV(faceIndex,iv,u_ptr,v_ptr)
                u = u_util.getFloat(u_ptr)
                v = v_util.getFloat(v_ptr)
                return [u,v]
            #uv of the face
            return [getuv(faceIndex,iv,u_ptr,v_ptr) for iv in range(3)]
#
#
##meshFn = maya.OpenMaya.MFnMesh(node)
##
#u_util = maya.OpenMaya.MScriptUtil()
#u_util.createFromDouble(0.0)
#u_ptr = u_util.asFloatPtr()
#v_util = maya.OpenMaya.MScriptUtil()
#v_util.createFromDouble(0.0)
#v_ptr = v_util.asFloatPtr()
#
#meshFn.getUV(0, u_ptr, v_ptr)
#
#u = u_util.getFloat(u_ptr)
#v = v_util.getFloat(v_ptr))
##getPolygonUVid
##getPolygonUV
#
    #should be faster ?
    def setUVs(self,object,uvs):
        #uvs is a dictionary key are faceindex, values it the actual uv for the 3-4 vertex
        ob = self.getObject(object)
        node = self.getNode('mesh_'+ob)
        meshnode = om.MFnMesh(node)         
        meshnode.clearUVs()
        u = om.MFloatArray()
        v = om.MFloatArray()
        uvCounts = om.MIntArray()
        uvIds = om.MIntArray()
        i = 0
        for f in uvs:
            for k,uv in enumerate(uvs[f]):
                uvIds.append(i)
                uvCounts.append(len(uvs[f]))
                u.append(uv[0])
                v.append(uv[1])
                #meshnode.setUV(i,uv[0],uv[1])
                #meshnode.assignUV(f,k,i)
                i = i +1
        meshnode.setUVs(u,v)
        meshnode.assignUVs(uvCounts,uvIds)

    def setUV(self,object,faceIndex,vertexIndex,uv,perVertice=True,uvid=0):
        ob = self.getObject(object)
        node = self.getNode('mesh_'+ob)
        meshnode = om.MFnMesh(node)         
        for k in range(3):
            luv = uv[k]
            meshnode.setUV(uvid,luv[0],luv[1])
            meshnode.assignUV(faceIndex,k,uvid)
            uvid = uvid +1
        return uvid

    def hyperShade_meVertCol(self):
        #mel command : nodeReleaseCallback graph1HyperShadeEd mentalrayVertexColors1 none;
#        nodeOutlinerInputsCmd connectWindow|tl|cwForm|connectWindowPane|leftSideCW connectWindow|tl|cwForm|connectWindowPane|rightSideCW; nodeOutliner -e -r connectWindow|tl|cwForm|connectWindowPane|rightSideCW;
#        connectAttr -f mesh_MSMS_MOL1crn.colorSet[0].colorName mentalrayVertexColors1.cpvSets[0];
#        // Result: Connected mesh_MSMS_MOL1crn.colorSet.colorName to mentalrayVertexColors1.cpvSets. // 
#        // Result: connectWindow|tl|cwForm|connectWindowPane|rightSideCW // 
        pass

#==============================================================================
# import / expor / read load / save
#==============================================================================

    def readFile(self,filename,**kw):
        fileName, fileExtension = os.path.splitext(filename)
        fileExtension=fileExtension.replace(".","")
        fileExtension=fileExtension.upper()
        if fileExtension  == "MA":
            fileExtension = "mayaAscii"
        elif fileExtension == "DAE":
            fileExtension = "DAE_FBX"
        elif fileExtension == "FBX":
            pass
        else :
            print ("not supported by uPy, contact us!")
            return
#        doc = self.getCurrentScene()
        cmds.file(filename ,type=fileExtension,loadReferenceDepth="all", i=True ) #merge the documets
#        c4d.documents.MergeDocument(doc,filename,c4d.SCENEFILTER_OBJECTS|c4d.SCENEFILTER_MATERIALS)

    def read(self,filename,**kw):
        fileName, fileExtension = os.path.splitext(filename)
        fileExtension=fileExtension.replace(".","")
        fileExtension=fileExtension.upper()
        if fileExtension  == "MA":
            fileExtension = "mayaAscii"
            cmds.file(filename ,type=fileExtension,loadReferenceDepth="all", i=True )
        elif fileExtension == "DAE" or fileExtension == "FBX":
            import maya.mel as mel
            #mel.eval('FBXImportMode -v exmerge;')
            filename = filename.replace("\\","\\\\")
            mel.eval('FBXImport -f "%s" -t 0;' % filename)#FBXGetTakeName ?
        else :
            print ("not supported by uPy, contact us!")
            return
    
    def write(self,listObj,**kw):
        pass
                
#==============================================================================
# raycasting
#==============================================================================
    def raycast(self,obj,start, end, length, **kw ):
        #posted on cgtalk.com
        #part of http://code.google.com/p/dynamica/               
        mo = self.getTransformation(obj)
        mi = mo.asMatrixInverse()
        mat = self.ToMat(mi)#.transpose()
        point = self.ApplyMatrix([start],numpy.array(mat).transpose())[0]
        direction = self.ApplyMatrix([end],numpy.array(mat).transpose())[0]
        
        #om.MGlobal.clearSelectionList()       
        om.MGlobal.selectByName(obj)
        sList = om.MSelectionList()
        #Assign current selection to the selection list object
        om.MGlobal.getActiveSelectionList(sList)
       
        item = om.MDagPath()
        sList.getDagPath(0, item)
        item.extendToShape()
       
        fnMesh = om.MFnMesh(item)
        
        raySource = om.MFloatPoint(float(point[0]), float(point[1]), float(point[2]), 1.0)
        rayDir = om.MFloatVector(float(direction[0]-point[0]), float(direction[1]-point[1]), float(direction[2]-point[2]))

        faceIds = None
        triIds = None
        idsSorted = False
        testBothDirections = False
        worldSpace = om.MSpace.kWorld
        maxParam = length#999999
        accelParams = None
        sortHits = True
        hitPoints = om.MFloatPointArray()
        #hitRayParams = om.MScriptUtil().asFloatPtr()
        hitRayParams = om.MFloatArray()
        hitFaces = om.MIntArray()
        hitTris = None
        hitBarys1 = None
        hitBarys2 = None
        tolerance = 0.0001
        #http://download.autodesk.com/us/maya/2010help/API/class_m_fn_mesh.html#114943af4e75410b0172c58b2818398f
        hit = fnMesh.allIntersections(raySource, rayDir, faceIds, triIds, idsSorted, worldSpace, 
                                      maxParam, testBothDirections, accelParams, sortHits, 
                                      hitPoints, hitRayParams, hitFaces, hitTris, hitBarys1, 
                                      hitBarys2, tolerance)       
        om.MGlobal.clearSelectionList()
        #print hit, len(hitFaces)
        if "count" in kw :
            #result = int(fmod(len(hitFaces), 2))
            return hit, len(hitFaces)
        #clear selection as may cause problem if the function is called multiple times in succession        
        return result