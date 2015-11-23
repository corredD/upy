
"""
    Copyright (C) <2010>  Autin L. TSRI
    
    This file git_upy/softimage/v2013/softimageHelper.py is part of upy.

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

#import numpy    
from types import StringType, ListType

#softimage import
from  siutils import si
Application = si()
if type(Application) == unicode :
    import sipyutils
    Application = sipyutils.si()
    #shortcut
    from sipyutils import si		# win32com.client.Dispatch('XSI.Application')
    from sipyutils import siut		# win32com.client.Dispatch('XSI.Utils')
    from sipyutils import siui		# win32com.client.Dispatch('XSI.UIToolkit')
    from sipyutils import simath	# win32com.client.Dispatch('XSI.Math')
    from sipyutils import log		# LogMessage
    from sipyutils import disp		# win32com.client.Dispatch
    from sipyutils import C	 as Constant		# win32com.client.constants
else :
    from siutils import siut      #XSIUtilss   
    from siutils import simath    #XSIMAth    
    from siutils import log       #LogMessage
    from siutils import disp      #win32com.client.Dispatch
    from siutils import C as Constant         #win32com.client.constants
SIUtils = siut()
SIMath = simath()
import random
import gzip
import re
from struct import pack
#import win32com.client
#from win32com.client import constants

#base helper class
from upy import hostHelper
if hostHelper.usenumpy:
    import numpy

from upy.hostHelper import Helper

class softimageHelper(Helper):
    """
    The softimage helper abstract class
    ============================
        This is the softimage helper Object. The helper 
        give access to the basic function need for create and edit a host 3d object and scene.
    """
    
    SPLINE = "kNurbsCurve"
    INSTANCE = "kTransform"
    MESH = "kTransform"
    
    POLYGON = "PolygonMesh"
    MESH = "PolygonMesh"

    EMPTY = "kTransform"
    BONES="kJoint"
    PARTICULE = "kParticle"
    IK="kIkHandle"

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
        self.host = "softimage"
        self.hext = "dae"

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
            return name
        if not len(name):
            print ("empty name",name)
        for i in range(9):
            invalid.append(str(i))       
        if type(name) is list or type(name) is tuple:
            name = name[0]
        if type(name) is not str and type(name) is not unicode:
            name = self.getName(name)
        if len(name) and name[0] in invalid:
            print "add _ to",name
            name= "_"+name
        print "check ", name
        #also remove some character and replace it by _
        name=name.replace(".","_")#.replace(" ","_").replace("'","").replace("-","_")
        return name    
        
    def getCurrentScene(self):
        return Application.Activeproject.Activescene
        
    def fit_view3D(self):
        pass#
        
    def resetProgressBar(self,max=None):
        """reset the Progress Bar, using value"""
        pass
        
    def progressBar(self,progress=None,label=None):
        """ update the progress bar status by progress value and label string
        @type  progress: Int/Float
        @param progress: the new progress
        @type  label: string
        @param label: the new message to put in the progress status
        """                
        pass

    def update(self,):
        #how do I update the redraw
        pass
        
    def updateAppli(self,):
        #how do I update the redraw
        pass

    def setCurrentSelection(self,obj):
        #obj should be  a string
        if type(obj) != str:
            obj = self.getName(obj)
        obj = self.checkName(obj)
        Application.SelectObj(obj,"","")
    
    def getCurrentSelection(self):
        return [Application.Selection(i) for i in range(Application.Selection.Count)]


    def getType(self,object):
        if type(object) == str or type(object) == unicode:
            object=self.getObject(object)
        if hasattr(object,"type"):
            return object.type
        return type(object)

    def setName(self,o,name):
        obj =self.getObject(o)        
        if obj is not None :
            obj.name = name
        
    def getName(self,o):
        if type(o) == str or type(o) == unicode: 
            name = self.checkName(o)
        else :
            if hasattr(o,"Name"):
                name=o.name
            elif hasattr(o,"name"):
                name = o.name
            else :
                name = ""
        return name

    def getFullName(self,o):
        if type(o) == str or type(o) == unicode:
            o = self.checkName(o)
            o = self.getObject(o)
        if hasattr(o,"fullname"):
            name=o.fullname
        elif hasattr(o,"FullName"):
            name = o.FullName
        else :
            name = ""
        return name    
        
    def getObject(self,name,**kw):
        if type(name) == str and type(name) == unicode :
            name = self.checkName(name)
        if type(name) != str and type(name) != unicode :
            return self.getObject(self.getFullName(name))
        oRoot = Application.ActiveProject.ActiveScene.Root
        obj = oRoot.FindChild(name)
        return obj

    def checkIsMesh(self,poly):
        pass

    def getMesh(self,ob,**kw):
        mesh = None
        if type(ob) == str or type(ob) == unicode :
           ob = self.getObject(ob)
        if ob is not None :
            if hasattr(ob,"ActivePrimitive"):
                mesh = ob.ActivePrimitive.Geometry
            else :
                mesh= ob
        return mesh
    
    def getMeshFrom(self,obj):
        if type(ob) == str or type(ob) == unicode :
            obj = self.getObject(obj)
        return self.getMesh(obj)

    def deleteObject(self,obj):
        sc = self.getCurrentScene()
        if type(obj) is str or type(obj) is unicode:
            name = self.checkName(obj)
            #name = obj
        else :
            obj = obj.name()
        try :
            #print "del",obj
            Application.DeleteObj(obj)            
        except:
            print "problem deleting ", obj
    
    def newEmpty(self,name,location=None,**kw):
        if "parent" in kw :
            parent = kw["parent"]
            parent = self.getObject(parent)
            empty=parent.AddNull(name)
        else :
            empty=self.getCurrentScene().Root.AddNull(name)
        return str(empty)


    def newInstance(self,name,object,location=None,hostmatrice=None,matrice=None,
                    parent=None,hidemaster=True,**kw):
        #we need  a model first for creating an instance
        #the object used for instance is placed in a model.
        pname = self.getName(object) 
        mobject = self.getObject(pname+"_model")
        if mobject is None :
            res =Application.CreateModel(pname,pname+"_model","","")
        
        #objectname, instancename, nbinstance, transformation 
        # sx,sy,sz,rx,ry,rz,tx,ty,tz,bool
        sx,sy,sz,rx,ry,rz,tx,ty,tz = ("","","","","","","","","")
        Application.Instantiate(pname+"_model","", "siSharedParent","siShareGrouping","siSetSelection","siApplyRepeatXForm",\
                                        sx,sy,sz,rx,ry,rz,tx,ty,tz,"")
        self.setName(pname+"_model_Instance",name)
        instance = self.getObject(name)
        if location != None :
            #set the position of instance with location
            self.setTranslation(name,location )            
        if matrice is not None :
            if self._usenumpy :
                matrice = numpy.array(matrice)
                hm = matrice.transpose().reshape(16,).tolist()
                matrice = SIMath.CreateMatrix4(hm)
                transform = SIMath.CreateTransform()
                transform.SetMatrix4(matrice)
                instance.Kinematics.Global.PutTransform2(None,transform)
            else :
                self.setTransformation(instance,mat=matrice)
        #set the instance matrice
        #self.setObjectMatrix(self,object,matrice=matrice,hostmatrice=hostmatrice)
        if parent is not None:
            self.reParent(instance,parent)
        if hidemaster :
            self.hideMasterInstance(object,True)
        return instance
#    #alias
#    setInstance = newInstance
#
    def getMasterInstance(self,obj):
        obj = self.getObject()
        if hasattr(obj,"InstanceMaster"):
            return obj.InstanceMaster
        else:
            return obj

    def hideMasterInstance(self,obj,hide):
        obj = self.getObject(obj)
        if obj is None :
            return
        if obj.Type == "#model" :
            if obj.ModelKind == Constant.siModelKind_Instance :
                master = obj.InstanceMaster#.ActvePrimitive.Geometry
                self.hideMasterInstance(master,hide)                     
            elif obj.ModelKind == Constant.siModelKind_Regular :
                if obj.ActivePrimitive.Type == "modelnull" :
                    childs = self.getChilds(obj)
                    for ch in childs:
                        self.hideMasterInstance(ch,hide)
        elif obj.Type == "null" :
            childs = self.getChilds(obj)
            for ch in childs:
                self.hideMasterInstance(ch,hide)
        else :
            obj.Properties("Visibility").Parameters("hidemaster").Value = hide
            self.toggleDisplay(obj,True)
        
    def instancePolygon(self,name, matrices=None,hmatrices=None, mesh=None,parent=None,
                        transpose=False,globalT=True,**kw):
        name = self.checkName(name)
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
                                      parent=parent,globalT=globalT,hidemaster=False)
                else :
                    inst=self.newInstance(name+str(i),mesh,matrice=mat,
                                      parent=parent,globalT=globalT,hidemaster=False)
            instance.append(inst)
        self.hideMasterInstance(mesh,True)
        return instance

    def resetTransformation(self,name):
        m= [1.,0.,0.,0.,
            0.,1.,0.,0.,
            0.,0.,1.,0.,
            0.,0.,0.,0.]
#        cmds.xform(name, a=True, m=m)
#
    def setObjectMatrix(self,object,mat,hostmatrice=None):
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
            #set the instance matrice
            pass
        if mat != None:
            #convert the matrice in host format
            #set the instance matrice
            pass
        matrice = SIMath.CreateMatrix4(mat)
        transform = SIMath.CreateTransform()
        transform.SetMatrix4(matrice)
        object.Kinematics.Global.PutTransform2(None,transform)
    
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
    def addObjectToScene(self,doc,obj,parent=None,**kw):
        #its just namely put the object under a parent
        #return
        #no need in softimage
        if parent is not None :
            self.parent(obj,parent)

    def parent(self,obj,parent,instance=False):
        #usecopypaste
        print "parenting ",obj," to ",parent
        obj = self.getFullName(obj)
        parent = self.getFullName(parent)
        print "obj parent ",obj,"parent",parent
        Application.CopyPaste(obj,"",parent,1)#use name        
        
    def reParent(self,obj,parent,instance=False):
        print "reParent ",obj,"parent",parent
        if parent == None : return
        if type(obj) is not list and type(obj) is not tuple :
            obj = [obj,]
        [self.parent(o,parent,instance=instance) for o in obj]

    def getChilds(self,obj):
        if type(obj) == str or type(obj) == unicode:
            obj = self.getObject(obj)
        nc = obj.Children.Count
        return [obj.Children(i) for i in range(nc)]
#
    def addCameraToScene(self,name,Type='persp',focal=30.0,center=[0.,0.,0.],sc=None,**kw):
        # what a bout the interest
        # Create a camera and get the shape name.
        cameraroot = Application.GetPrimCamera("Camera",name,"","","","")

        # Set the focal length of the camera.
        Application.SetValue(name+".camera.fov",focal,"")
        
        #change the location
        self.setTranslation(name, center)
        #cmds.move(float(center[0]),float(center[1]),float(center[2]), cameraName[0], absolute=True )
        #should I rotate it 
        self.rotateObj(name,[360,0,0])
        return cameraroot

    def addLampToScene(self,name,Type='Area',rgb=[1.,1.,1.],dist=25.0,energy=1.0,
                       soft=1.0,shadow=False,center=[0.,0.,0.],sc=None,**kw):
        #print Type
        #each type have a different cmds
        lcmd = self.LIGHT_OPTIONS[Type]
        light = Application.GetPrimLight(lcmd,name,"","","","")
        
        Application.SetValue(name+".light.soft_light.intensity",float(energy),"")
        Application.SetValue(name+".light.soft_light.rayshadow_softness",float(soft),"")
        Application.SetValue(name+".light.soft_light.color.red",rgb[0],"")#0-1
        Application.SetValue(name+".light.soft_light.color.blue",rgb[1],"")
        Application.SetValue(name+".light.soft_light.color.green",rgb[2],"")
        
        self.setTranslation(name, center)

        return light
#        
##    def toggleDisplay(self,ob,display,**kw):
##        ob = self.getObject(ob)
##        if ob is None :
##            return
##        ob.Properties("Visibility").Parameters("viewvis").Value = display
##        ob.Properties("Visibility").Parameters("rendvis").Value = display
##        #Application.SetValue("Test_Spheres2Dstatic.visibility.viewvis", False, "")

    def toggleDisplay(self,ob,display=True,child=True):
        #print "toggle",ob
        if type(ob) == str or type(ob) == unicode:
            obj=self.getObject(ob)
        elif type(ob) is list and len(ob):
            [self.toggleDisplay(o,display=display) for o in ob]
            return
        else : 
            obj=ob
        if obj is None :
            return
        #print "toggle doit",ob,obj,type(obj)
        obj.Properties("Visibility").Parameters("viewvis").Value = display
        obj.Properties("Visibility").Parameters("rendvis").Value = display
        if child :
            chs = self.getChilds(obj)
            if len(chs):
                self.toggleDisplay(chs,display=display)
        #if the object is a master instance should do the instance Master Hidden on for mesh attached to the model.
        #then the toggle will apply on all isntance    

    def getVisibility(self,obj,editor=True, render=False, active=False):
        ob = self.getObject(ob)
        if ob is None :
            return
        if editor and not render and not active:
            return ob.Properties("Visibility").Parameters("viewvis").Value
        elif not editor and render and not active:
            return ob.Properties("Visibility").Parameters("rendvis").Value
        elif not editor and not render and active:
            return True
        else :
            return  [ob.Properties("Visibility").Parameters("viewvis").Value,
                    ob.Properties("Visibility").Parameters("rendvis").Value,
                    True]

    def getTranslation(self,name,absolue=True):
        obj = self.getObject(name)
        if obj is None :
            return
        if absolue :
            pos = [Application.GetValue(obj.Kinematics.Local.posx),
                   Application.GetValue(obj.Kinematics.Local.posy),
                   Application.GetValue(obj.Kinematics.Local.posz)]
        else :
            pos = [Application.GetValue(obj.Kinematics.Global.posx),
                   Application.GetValue(obj.Kinematics.Global.posy),
                   Application.GetValue(obj.Kinematics.Global.posz)]
        return pos

    def setTranslation_cmd(self,name,pos,local = False):
        if local :
            Application.SetValue(name+".kine.local.posx",pos[0],"")
            Application.SetValue(name+".kine.local.posy",pos[1],"")
            Application.SetValue(name+".kine.local.posz",pos[2],"")
        else :           
            Application.SetValue(name+".kine.global.posx",pos[0],"")
            Application.SetValue(name+".kine.global.posy",pos[1],"")
            Application.SetValue(name+".kine.global.posz",pos[2],"")

    def rotateObj_cmd(self,name,rot,local=False):
        if local :
            Application.SetValue(name+".kine.local.rotx",(float(rot[0])),"")
            Application.SetValue(name+".kine.local.roty",(float(rot[1])),"")
            Application.SetValue(name+".kine.local.rotz",(float(rot[2])),"")
        else :           
            Application.SetValue(name+".kine.global.rotx",(float(rot[0])),"")
            Application.SetValue(name+".kine.global.roty",(float(rot[1])),"")
            Application.SetValue(name+".kine.global.rotz",(float(rot[2])),"")
            
    def setTranslation(self,name,pos,local = False,**kw):
        obj = self.getObject(name)
        if obj is None :
            return
        if local :
            obj.Kinematics.Local.Posx = pos[0]
            obj.Kinematics.Local.Posy = pos[1]
            obj.Kinematics.Local.Posz = pos[2]
        else :           
            obj.Kinematics.Global.Posx = pos[0]
            obj.Kinematics.Global.Posy = pos[1]
            obj.Kinematics.Global.Posz = pos[2]

    def translateObj(self,obj,position,use_parent=False,**kw):
        #is om would be faster ?
        if len(position) == 1 : c = position[0]
        else : c = position
        #print "upadteObj"
        newPos=c#c=c4dv(c)
        o=self.getObject(obj)
        if use_parent : 
            parentPos = self.getPosUntilRoot(obj)#parent.get_pos()
            c = newPos - parentPos
        self.setTranslation(obj, c)
        
    def scaleObj(self,name,sc,local = False,**kw):
        obj = self.getObject(name)
        if obj is None :
            return
        if type(sc) is float :
            sc = [sc,sc,sc]        
        if local :
            obj.Kinematics.Local.sclx = sc[0]
            obj.Kinematics.Local.scly = sc[1]
            obj.Kinematics.Local.sclz = sc[2]
        else :           
            obj.Kinematics.Global.sclx = sc[0]
            obj.Kinematics.Global.scly = sc[1]
            obj.Kinematics.Global.sclz = sc[2]

    def rotateObj(self,name,rot,local=False,**kw):
        #need degreee!
        #if "primitive" in kw :
        obj = self.getObject(name)
        if obj is None :
            return
        if local :
            obj.Kinematics.Local.rotx = math.degrees(rot[0])
            obj.Kinematics.Local.roty = math.degrees(rot[1])
            obj.Kinematics.Local.rotz = math.degrees(rot[2])
        else :           
            obj.Kinematics.Global.rotx = math.degrees(rot[0])
            obj.Kinematics.Global.roty = math.degrees(rot[1])
            obj.Kinematics.Global.rotz = math.degrees(rot[2])


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
        
    #need face indice
    def color_mesh_perVertex(self,mesh,colors,faces=None,perVertex=True,
                             facesSelection=None,faceMaterial=False):
        if colors[0] is not list and len(colors) == 3 :
           colors = [colors,]
        mesh = self.getMesh(mesh)
        print "try coloring ",self.getType(mesh),self.POLYGON,self.MESH
        if self.getType(mesh) != self.POLYGON and self.getType(mesh) != self.MESH:
            return False
        vc = mesh.CurrentVertexColor
        if vc is None :
            vc = mesh.AddVertexColor()
            mesh.CurrentVertexColor = vc
        vcClsElems = vc.parent.elements
        clsElemInde = 0
        nCol = len(vc.Elements.Array[0])
        if self.usenumpy: 
            colorsout = numpy.zeros((nCol,len(vc.Elements.Array))).transpose()
        else :
            colorsout = [[0.]*nCol,[0.]*nCol,[0.]*nCol,[0.]*nCol]#R G B A
        
        nf=mesh.Polygons.Count#mesh.numPolygons()    
        nv=mesh.Vertices.Count            
#        mfaces = self.getMeshFaces(meshnode)
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
#        if perVertex:
#            N=range(nv)
#        else :
#            N=range(nf)
        N=range(nf)
        if facesSelection is not None :
            N = face_sel_indice
            perVertex = False


        for k,i in enumerate(N) :
            face = mesh.Polygons(i)
            vertices = face.Vertices
            nodes = face.Nodes
            for n in range(nodes.Count):
                vertex= vertices(n)
                node = nodes(n)
                if len(colors) == 1 : ncolor = colors[0]
                else :
                    if perVertex : 
                        if vertex.index >= len(colors) : 
                            ncolor = [0.,0.,0.] #problem
                        else : 
                            ncolor = colors[vertex.index]
                    else :
                        if i >= len(colors) : 
                            ncolor = [0.,0.,0.] #problem
                        else : 
                            ncolor = colors[i]
                l = vcClsElems.FindIndex(node.Index)        
                colorsout[0][l]=ncolor[0]
                colorsout[1][l]=ncolor[1]
                colorsout[2][l]=ncolor[2]
                colorsout[3][l]=1.0
        if self.usenumpy:        
            colorsout = colorsout.tolist()
        vc.Elements.Array = colorsout
        mesh.CurrentVertexColor = vc
        return True
        
    ###################MATERIAL CODE FROM Rodrigo Araujo#####################################################################################
    #see http://linil.wordpress.com/2008/01/31/python-maya-part-2/
    def createMaterial(self, name, color, type = "Phong",**kw):
        #type can be lamber phong etc... need a dictionry
        self.addMaterial(name, color,type=type,**kw )

    def addMaterial(self, name, color,type="Phong",**kw ):
        mat= self.getMaterial(name)
        if mat != None : 
            return mat
        matLib = Application.ActiveProject.ActiveScene.ActiveMaterialLibrary        
        mat = matLib.CreateMaterial(type,name)
        mat.Shaders[0].Name = name+"Shader"
        self.colorMaterial(mat, color) 
        return mat

    def createTexturedMaterial_cmd(self,name,filename):
        #cget the image
        oImage = Application.AddImageSource( filename )
        oImageClip = Application.AddImageClip( oImage )
        name = self.checkName(name)
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
        if type(material) == str :
            material = self.getMaterial(material)
            if material is None :
                return
        if hasattr(material,"name"):
            matname = material.name
            matfullname = material.fullName
        else :
            matname = material.Name
            matfullname = material.FullName        
        objectname = self.getName(object)
        print ('doit Application.AssignMaterial('+matfullname+'"+,'+objectname+',"siLetLocalMaterialsOverlap")')
        Application.AssignMaterial(matfullname+","+objectname,"siLetLocalMaterialsOverlap")
        if texture :
            object = self.getObject(object,)
#            Application.CreateProjection(object.name, "siTxtUV", "siTxtDefaultSpherical", "Texture_Support", 
#                                             object.name+"Projection", "", "", "")
            Application.GenerateUniqueUVs(object.name,object.name+"Projection","","","","","","","")
            Application.SetInstanceDataValue("", matfullname+".Image.tspace_id", object.name+"Projection")
      

    def assignNewMaterial(self, matname, color, type, object):
        self.createMaterial (matname, color, type)
        self.assignMaterial (object,matname)
    
    def colorMaterial(self,matname, color):
        mat = self.getMaterial(matname)
        #assume one shader and take the first
        shader = mat.Shaders[0]
        shader.diffuse.red=float(color[0])
        shader.diffuse.green=float(color[1])
        shader.diffuse.blue=float(color[2])

    def getMaterial(self,matname):
        if type(matname) != str and type(matname) != unicode : return matname
        matname = self.checkName(matname)
        matlib = Application.ActiveProject.ActiveScene.ActiveMaterialLibrary
        for mat in matlib.Items:
            if mat.Name == matname :
                return mat
        return None
            
    def getMaterialName(self,mat):
        if type(mat) == str : return mat
        if hasattr(mat,"name"):
            return material.name
        else :
            return material.Name
        
    def getAllMaterials(self):
        return Application.ActiveProject.ActiveScene.ActiveMaterialLibrary.Items

    def getMaterialObject(self,obj):
        obj = self.getObject(obj)
        return [obj.material]

    def changeObjColorMat(self,obj,color):
        #obj should be the object name, in case of mesh
        #in case of spher/cylinder etc...atom name give the mat name
        #thus  matname should be 'mat_'+obj
        obj = self.getObject(obj)
        self.colorMaterial(obj.material,color)
          
    def changeColor(self,mesh,colors,perVertex=True,perObjectmat=None,pb=False,
                    facesSelection=None,faceMaterial=False,**kw):
        #if hasattr(geom,'obj'):obj=geom.obj
        #else : obj=geom
        #mesh = self.getMesh(mesh)
        if colors[0] is not list and len(colors) == 3 :
           colors = [colors,]        
        print "change color",type(mesh),mesh,len(colors)
        
        res = self.color_mesh_perVertex(mesh,colors,perVertex=perVertex,
                                  facesSelection=facesSelection,
                                  faceMaterial=faceMaterial)
        print "color_mesh_perVertex",res,not res,len(colors) 
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
#
    ###################Meshs and Objects#####################################################################################                                                                        
    def Sphere_cmd(self,name,res=16.,radius=1.0,pos=None,color=None,
               mat=None,parent=None,type="nurb"):
        # iMe[atn],node=cmds.sphere(name=name+"Atom_"+atn,r=rad)
        t=res/100.
        p=""
        if parent is not None :
            p=self.getName(parent)
        if type == "nurb" :
            Application.CreatePrim("Sphere", "NurbsSurface", name, p)
            obj = Application.Selection(0)
        elif type == "poly":
            Application.ActiveSceneRoot
            Application.CreatePrim("Sphere", "MeshSurface", name, p)
            obj = Application.Selection(0)
        #set radius ad quality
        Application.SetValue(name+".sphere.radius", radius, "")
        Application.SetValue(name+".geom.subdivu", res, "")
        Application.SetValue(name+".geom.subdivv", res, "")
        
        #shape is name+"Shape"
        if pos is not None :
            self.setTranslation(name, pos)
        if mat is not None :
            mat = self.getMaterial(mat)
            if mat is not None :
                self.assignMaterial(name,mat)
        else :
            if color is not None :
                mat = self.addMaterial("mat"+name,color)
            else :
                mat = self.addMaterial("mat"+name,[1.,1.,0.])
#            mat = self.getMaterial(name)
            self.assignMaterial(name,mat)
        return obj,obj.ActivePrimitive

    def Sphere(self,name,res=16.,radius=1.0,pos=None,color=None,
               mat=None,parent=None,type="nurb"):
        # iMe[atn],node=cmds.sphere(name=name+"Atom_"+atn,r=rad)
        t=res/100.
        p=Application.ActiveSceneRoot
        if parent is not None :
            p=self.getObject(parent)
        if type == "nurb" :
            obj = p.AddGeometry("Sphere", "NurbsSurface")
        elif type == "poly":
            obj = p.AddGeometry("Sphere", "MeshSurface")
        #set radius ad quality
        obj.name=name
        obj.radius = radius
        obj.subdivu = res
        obj.subdivv = res
        
        #shape is name+"Shape"
        if pos is not None :
            self.setTranslation(name, pos)
        if mat is not None :
            mat = self.getMaterial(mat)
            if mat is not None :
                self.assignMaterial(name,mat)
        else :
            if color is not None :
                mat = self.addMaterial("mat"+name,color)
            else :
                mat = self.addMaterial("mat"+name,[1.,1.,0.])
#            mat = self.getMaterial(name)
            self.assignMaterial(name,mat)
        return obj,obj.ActivePrimitive


#
    def updateSphereMesh(self,mesh,verts=None,faces=None,basemesh=None,
                         scale=None,typ=True,**kw):
        mesh = self.checkName(mesh)
        mesh=self.getMesh(mesh)
        if mesh is not None :
            if hasattr(mesh,"radius"):
                mesh.radius = scale
#
    def updateSphereObj(self,obj,coords=None):
        if obj is None or coords is None: return
##        obj = self.getObject(obj)
#        #would it be faster we transform action
        self.setTranslation(obj,coords)
##        cmds.move(float(coords[0]),float(coords[1]),float(coords[2]), obj, absolute=True )
#        
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
#    
#    def instancesCylinder(self,name,points,faces,radii,
#                          mesh,colors,scene,parent=None):
#        cyls=[]
#        mat = None
#        if len(colors) == 1:
#            mat = self.retrieveColorMat(colors[0])
#            if mat == None and colors[0] is not None:        
#                mat = self.addMaterial('mat_'+name,colors[0])
#        for i in range(len(faces)):
#            cyl = self.oneCylinder(name+str(i),points[faces[i][0]],
#                                   points[faces[i][1]],radius=radii[i],
#                                   instance=mesh,material=mat,parent = parent)
#            cyls.append(cyl)
#        return cyls
#    
#    def updateInstancesCylinder(self,name,cyls,points,faces,radii,
#                          mesh,colors,scene,parent=None):
#        mat = None
#        if len(colors) == 1:
#            mat = self.retrieveColorMat(colors[0])
#            if mat == None and colors[0] is not None:        
#                mat = self.addMaterial('mat_'+name,colors[0])
#        for i in range(len(faces)):
#            col=None
#            if i < len(colors):
#                col = colors[i]
#            if i < len(cyls):
#                self.updateOneCylinder(cyls[i],points[faces[i][0]],
#                                   points[faces[i][1]],radius=radii[i],
#                                   material=mat,color=col)
#                self.toggleDisplay(cyls[i],True)
#            else :
#                cyl = self.oneCylinder(name+str(i),points[faces[i][0]],
#                                   points[faces[i][1]],radius=radii[i],
#                                   instance=mesh,material=mat,parent = parent)
#                cyls.append(cyl)
#
#        if len(faces) < len(cyls) :
#            #delete the other ones ?
#            for i in range(len(faces),len(cyls)):
#                if delete : 
#                    obj = cyls.pop(i)
#                    print "delete",obj
#                    self.deleteObject(obj)
#                else :
#                    self.toggleDisplay(cyls[i],False)
#        return cyls
#
#
#    
#    def instancesSphere(self,name,centers,radii,meshsphere,colors,scene,parent=None):
#        name = self.checkName(name)
#        sphs=[]
#        mat = None
#        if len(colors) == 1:
#            mat = self.retrieveColorMat(colors[0])
#            if mat == None:        
#                mat = self.addMaterial('mat_'+name,colors[0])
#        for i in range(len(centers)):
#            sphs.append(cmds.instance(meshsphere,name=name+str(i)))
#            #local transformation ?
#            cmds.move(float(centers[i][0]),float(centers[i][1]),float(centers[i][2]),name+str(i))
#            cmds.scale(float(radii[i]),float(radii[i]),float(radii[i]), name+str(i),absolute=True )
#            if mat == None : mat = self.addMaterial("matsp"+str(i),colors[i])
#            self.assignMaterial(name+str(i),mat)#mat[bl.retrieveColorName(sphColors[i])]
#            self.addObjectToScene(scene,sphs[i],parent=parent)
#        return sphs
#
#    def updateInstancesSphere(self,name,sphs,centers,radii,meshsphere,
#                        colors,scene,parent=None,delete=True):
#        mat = None
#        if len(colors) == 1:
#            mat = self.retrieveColorMat(colors[0])
#            if mat == None and colors[0] is not None:        
#                mat = self.addMaterial('mat_'+name,colors[0])
#        for i in range(len(centers)):
#            if len(radii) == 1 :
#                rad = radii[0]
#            elif i >= len(radii) :
#                rad = radii[0]
#            else :
#                rad = radii[i]            
#            if i < len(sphs):
#                cmds.move(float(centers[i][0]),float(centers[i][1]),float(centers[i][2]),sphs[i])#name+str(i))
#                cmds.scale(float(rad),float(rad),float(rad), sphs[i],absolute=True )
##                sphs[i].SetAbsPos(self.FromVec(centers[i]))
##                sphs[i][905]=c4d.Vector(float(rad),float(rad),float(rad))
#                if mat == None : 
#                    if colors is not None and i < len(colors) and colors[i] is not None : 
#                        mat = self.addMaterial("matsp"+str(i),colors[i])
#                if colors is not None and i < len(colors) and colors[i] is not None : 
#                    self.colorMaterial(mat,colors[i])
#                self.toggleDisplay(sphs[i],True)
#            else :
#                sphs.append(cmds.instance(meshsphere,name=name+str(i)))
#                #local transformation ?
#                cmds.move(float(centers[i][0]),float(centers[i][1]),float(centers[i][2]),name+str(i))
#                cmds.scale(float(rad),float(rad),float(rad), name+str(i),absolute=True )
#                if mat == None : mat = self.addMaterial("matsp"+str(i),colors[i])
#                self.assignMaterial(name+str(i),mat)#mat[bl.retrieveColorName(sphColors[i])]
#                self.addObjectToScene(scene,sphs[i],parent=parent)
#                if mat == None :
#                    if colors is not None and  i < len(colors) and colors[i] is not None : 
#                        mat = self.addMaterial("matsp"+str(i),colors[i])
#                self.addObjectToScene(scene,sphs[i],parent=parent)
#                
#        if len(centers) < len(sphs) :
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

    def box(self,name,center=[0.,0.,0.],size=[1.,1.,1.],cornerPoints=None,visible=1,
                              mat=None,**kw):
        res = 15.
        type = "poly"
        if "type" in kw:
            type = kw["type"]
        p=Application.ActiveSceneRoot
        if "parent" in kw :
            p=self.getObject(kw["parent"])
        if type == "nurb" :
            obj = p.AddGeometry("Cube", "NurbsSurface")
        elif type == "poly":
            obj = p.AddGeometry("Cube", "MeshSurface")
        #set radius ad quality
        obj.name=name
        obj.length = 1 
        obj.subdivu = res
        obj.subdivv = res
        obj.subdivbase = res
        #use the scale instead of the length
        self.scaleObj(obj,size)
        mat = self.addMaterial("mat"+name,[1.,1.,0.])
        self.assignMaterial(obj,mat)
        if cornerPoints != None :
            for i in range(3):
                size[i] = cornerPoints[1][i]-cornerPoints[0][i]
            center=[0.,0.,0.]#(numpy.array(cornerPoints[0])+numpy.array(cornerPoints[1]))/2.
            for i in range(3):
                center[i] = (cornerPoints[0][i]+cornerPoints[1][i])/2.
        self.setTranslation(obj,center)
        return obj,obj.ActivePrimitive

    def getBoxSize(self,name,**kw):
        box=self.getObject(name)
        sc=[0,0,0]
        if hasattr(box,"ActivePrimitive"):
            geom = box#.ActivePrimitive.Geometry
            l = geom.length
            sc[0] = Application.GetValue(geom.Kinematics.Global.sclx)
            sc[1] = Application.GetValue(geom.Kinematics.Global.scly)
            sc[2] = Application.GetValue(geom.Kinematics.Global.sclz)
        return sc
        
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
        type = "poly"
        if "type" in kw:
            type = kw["type"]
        p=Application.ActiveSceneRoot
        if parent is not None:
            p=self.getObject(parent)
        if type == "nurb" :
            obj = p.AddGeometry("Cone", "NurbsSurface")
        elif type == "poly":
            obj = p.AddGeometry("Cone", "MeshSurface")
        #set radius ad quality
        obj.name=name
        obj.height = length
        obj.radius = radius
        obj.subdivu = res
        obj.subdivv = res
        obj.subdivbase = res
        mat = self.addMaterial("mat"+name,[1.,1.,0.])
        self.assignMaterial(obj,mat)
        if pos is not None :
            self.setTranslation(obj,pos)
        return obj,obj.ActivePrimitive
    
    def Cylinder(self,name,radius=1.,length=1.,res=16,pos = None,parent=None,**kw):
        #import numpy
        type = "poly"
        if "type" in kw:
            type = kw["type"]
        p=Application.ActiveSceneRoot
        if parent is not None:
            p=self.getObject(parent)
        if type == "nurb" :
            obj = p.AddGeometry("Cylinder", "NurbsSurface")
        elif type == "poly":
            obj = p.AddGeometry("Cylinder", "MeshSurface")
        #set radius ad quality
        obj.name=name
        obj.height = length
        obj.radius = radius
        obj.subdivu = res
        obj.subdivv = res
        obj.subdivbase = res
        mat = self.addMaterial("mat"+name,[1.,1.,0.])
        self.assignMaterial(obj,mat)
        if pos is not None :
            self.setTranslation(obj,pos)
        return obj,obj.ActivePrimitive
#
#    def oneCylinder(self,name,head,tail,radius=None,instance=None,material=None,
#                    parent = None,color=None):
#        name = self.checkName(name)
#        laenge,wsz,wz,coord=self.getTubeProperties(head,tail)
##        print "oneCylinder instance",instance
#        if instance == None : 
#            obj = self.Cylinder(name)
#        else : 
#            obj = self.newMInstance(name,instance,parent=parent)
##            obj = name
##        self.translateObj(name,coord)
##        self.setTranslation(name,coord)
##        #obj.setLocation(float(coord[0]),float(coord[1]),float(coord[2]))
##        cmds.setAttr(name+'.ry',float(degrees(wz)))
##        cmds.setAttr(name+'.rz',float(degrees(wsz)))
##        cmds.scale( 1, 1, laenge, name,absolute=True )
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
#
#        return obj
#
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
#    def updateTubeObj(self,o,coord1,coord2):
#        laenge,wsz,wz,pos=self.getTubeProperties(coord1,coord2)
#        self.setTransformation(o,trans=pos,scale=[1., 1., laenge],
#                               rot=[0.,wz,wsz])
##        cmds.scale( 1., 1., laenge, o,absolute=True )
##        self.setTranslation(o,pos)
###        cmds.move(float(pos[0]),float(pos[1]),float(pos[2]), o, absolute=True )
##        cmds.setAttr(o+'.ry',float(degrees(wz)))
##        cmds.setAttr(o+'.rz',float(degrees(wsz)))
#            
#    def updateTubeMeshold(self,atm1,atm2,bicyl=False,cradius=1.0,quality=0):
#        self.updateTubeObj(atm1,atm2,bicyl=bicyl,cradius=cradius)
#    
#    def updateTubeMesh(self,mesh,basemesh=None,cradius=1.0,quality=0):
##        print mesh
##        print cradius, mesh
#        mesh = self.getObject(str(mesh))
##        print mesh
#        maya.cmds.polyCylinder(mesh,e=True,r=cradius)
#    
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
        type = "poly"
        if "type" in kw:
            type = kw["type"]
        p=Application.ActiveSceneRoot
        if "parent" in kw :
            p=self.getObject(kw["parent"])
        if type == "nurb" :
            obj = p.AddGeometry("Grid", "NurbsSurface")
        elif type == "poly":
            obj = p.AddGeometry("Grid", "MeshSurface")
        #set radius ad quality
        obj.name=name
        obj.ulength = size[0]
        obj.vlength = size[1]
        
        if "subdivision" in kw :        
            obj.subdivu = kw["subdivision"][0]
            obj.subdivv = kw["subdivision"][1]
        mat = self.addMaterial("mat"+name,[1.,1.,0.])
        self.assignMaterial(obj,mat)
        if cornerPoints != None :
            for i in range(3):
                size[i] = cornerPoints[1][i]-cornerPoints[0][i]
            for i in range(3):
                center[i]=(cornerPoints[0][i]+cornerPoints[1][i])/2.        
        self.setTranslation(obj,center)
        return obj,obj.ActivePrimitive

#==============================================================================
# special function softimage write to cache
# came from PLY import plugin
# http://www.xsidatabase.com/uploads/scripts/create_pointcloud_ply_file
#==============================================================================
    def WriteIceCache(self,plyFilePath, pointDataList, colorsList=None,pointSize=1.0):
        p = SIUtils.Environment('XSI_USERHOME')+os.sep+"CacheTemp"+os.sep
        if not os.path.isdir(p):
            os.mkdir(p)
        
        fileName, ext = os.path.splitext( plyFilePath )
        
        icePath1 = p+fileName + ".1.icecache"
        icePath2 = p+fileName + ".2.icecache"
        returnPath = p+fileName + ".[1..2].icecache"
        
        cachefile1 = gzip.open( icePath1, "wb" )
        cachefile2 = gzip.open( icePath2, "wb" )
        
        nbPoints = len(pointDataList)
        
        data = self.WriteHeader( nbPoints, 3 )
        data += self.WriteAttrDefs()
        
        chunks = self.GetChunks(nbPoints)
        
        # Colors
        for chunk in chunks:
            data += pack("I", 0)    #is constant?
            for i in chunk:
                if colorsList is None :
                    color = [1.,1.,1.,1.]
                else :
                    color = colorsList[i]
                r = color[0]
                g = color[1]
                b = color[2]
                a = 1.0#color[i][3]
                
                #pr(str(i) + ": " + str(r) + " --- " + str(g) + " --- " + str(b) + " --- " + str(a))
                data += pack("4f",r, g, b, a)
                
        # Point positions
        data += pack("I", 0)    #is constant?
        for chunk in chunks:    
            for i in chunk:
                x = pointDataList[i][0]
                y = pointDataList[i][1]
                z = pointDataList[i][2]
                
                #pr(str(i) + ": " + str(x) + " --- " + str(y) + " --- " + str(z))
                data += pack("3f",x, y, z)
                
        # Sizes
        for chunk in chunks:
            data += pack("I", 0)    #is constant?
            for i in chunk:
                data += pack("1f",pointSize)
    
        # Write two cache files.
        cachefile1.write( data )
        cachefile1.close()
        cachefile2.write( data )
        cachefile2.close()
        
        return returnPath
    
    def WriteHeader(self, nbPoints, nbAttributes ):
        data  = pack( "8s", "ICECACHE" )    #header string
        data += pack( "I", 102 )     #version number
        data += pack( "I", 0 )     #object type, pointcloud
        data += pack( "I", nbPoints )     #point count
        data += pack( "I", 0 )    #edge count
        data += pack( "I", 0 )     #polygon count
        data += pack( "I", 0 )     #sample count
        data += pack( "I", 0 )     #don"t know this one
        data += pack( "I", nbAttributes )     #attribute count
        return data
    
    def WriteAttrDefs(self,):
        #particle color
        data  = pack( "L", 5 )    #attribute name length
        data += pack( "8s", "color___" )    #attribute name
        data += pack( "I", 512 )    #data type
        data += pack( "I", 1 )    #structure type
        data += pack( "I", 2 )    #context type
        data += pack( "I", 0 )    #database ID, obsolete
        data += pack( "I", 2 )    #category
                
        #particle position
        data += pack( "L", 13 )    #attribute name length
        data += pack( "16s", "pointposition___" )    #attribute name
        data += pack( "I", 16 )    #data type
        data += pack( "I", 1 )    #structure type
        data += pack( "I", 2 )    #context type
        data += pack( "I", 0 )    #database ID, obsolete
        data += pack( "I", 2 )    #category
    
        #particle size
        data += pack( "L", 4 )    #attribute name length
        data += pack( "4s", "size" )    #attribute name
        data += pack( "I", 4 )    #data type
        data += pack( "I", 1 )    #structure type
        data += pack( "I", 2 )    #context type
        data += pack( "I", 0 )    #database ID, obsolete
        data += pack( "I", 2 )    #category
    
        return data
            
    
    def GetChunks(self,num):
        if num < 4000:
            return [range(num)]
        
        outlist = []
        chunks = num / 4000
        for i in range(chunks):
            outlist.append(range((i)*4000, (i+1)*4000))
        outlist.append(range( (i+1)*4000, (i+1)*4000 + num%4000) )
                    
        return outlist
 
#==============================================================================
#  
#==============================================================================

    def PointCloudObject(self,name,**kw):
        #print "cloud", len(coords)
        coords=kw['vertices']
#        cloudModel = Application.ActiveSceneRoot.AddModel("",name+"ds")
#        pontCloud = cloudModel.AddPrimitive("pontcloud",name)
#        mesh = pontCloud.ActivePrimitive.Geometry
#        Application.FreezeObj(obj)
#        mesh.Set(coords)
#        nface = 0    
#        if kw.has_key("faces"):
#            nface = len(kw['faces'])
				# Write the icecache
        #write in som cach directory?
        cachePath = self.WriteIceCache(name, coords)
				
        # Create an empty pointcloud under a model
        cloudModel = Application.ActiveSceneRoot.AddModel("",name + "_model")
        pointCloud = cloudModel.AddPrimitive("pointcloud", name)
				
        # Load in out newly created icecache
        Application.AddFileCacheSource(pointCloud, cachePath)
				
        # Cleanup...
        Application.FreezeObj(pointCloud)
        Application.DeleteObj(cloudModel.Fullname + ".Mixer")
        # I figure one more command isn't gonna hurt after the 3 above this... ;)
        Application.SetValue(pointCloud.Fullname + ".particledisplay.displaytype", 1, "")
#        f=[]
#        for i in range(len(coords)):
#            f.append([4,i,i,i+1,i+1])
#        obj = self.createsNmesh(name+'ds',coords,None,f)
        return cloudModel,pointCloud

    def Platonic(self,name,Type,radius,**kw):
        dicT={"tetra":"Tetrahedron",
              "hexa":"Tetrahedron",
              "octa":"Octahedron",
              "dodeca":"Dodecahedron",
              "icosa":"Icosahedron"}#BuckyBall ? SoccerBall?
        dicTF={4:0,
              6:1,
              8:2,
              12:3,
              20:4}
        res = 10
        p=Application.ActiveSceneRoot
        if "parent" in kw and kw["parent"] is not None :
            p=self.getObject(kw["parent"])
        if Type in dicT  :
           obj = p.AddGeometry(dicT[Type], "MeshSurface")
        elif Type in dicTF :
            obj = p.AddGeometry(dicTF[Type], "MeshSurface")
         #set radius ad quality
        obj.name=name
        obj.radius = radius
#        obj.subdivu = res
#        obj.subdivv = res
        
        #shape is name+"Shape"
#        if pos is not None :
#            self.setTranslation(name, pos)
        if "material" in kw and kw["material"] is not None :
            mat = self.getMaterial(kw["material"])
            if mat is not None :
                self.assignMaterial(name,kw["material"])
        else :
            if "color" in kw and kw["color"] is not None :
                mat = self.addMaterial("mat"+name,kw["color"])
            else :
                mat = self.addMaterial("mat"+name,[1.,1.,0.])
#            mat = self.getMaterial(name)
            self.assignMaterial(name,mat)
        return obj,obj.ActivePrimitive

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
        shapedic = {"circle":"Circle",
                    "rectangle":"Square"}
                    
        p=Application.ActiveSceneRoot
        if "parent" in kw :
            p=self.getObject(kw["parent"])
        obj = p.AddGeometry(shapedic[type], "NurbsCurve")
        #set radius ad quality
        obj.name=name
        obj.radius = 1.0
#        obj.subdivu = res
        return obj,obj.ActivePrimitive

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
        return p[0]

    def ToFace(self,f):
        r = [len(f),]
        r.extend([int(ff) for ff in f])
        return r

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
        if "parent" in kw :
            parent = kw["parent"]
            print "reparent ", name,parent
            #self.reParent(name,parent)
            Application.SIGetPrim("EmptyPolygonMesh",name,self.getName(parent),"","","")
        else :
            Application.SIGetPrim("EmptyPolygonMesh",name,"","","","")
        name = self.checkName(name)
        #Application.SelectObj(name, "","")
        #obj = Application.Selection(0)
        obj = self.getObject(name)
        mesh = obj.ActivePrimitive.Geometry
        if self.usenumpy:
            vertices = numpy.array(vertices).transpose().tolist()
        else :
            verts = [[],[],[]]
            for v in vertices :
                for i in range(3):
                    verts[i].append(v[i])
            vertices = verts
        fs=[]
        for f in faces:
           fs.extend(self.ToFace(f))
        faces= fs
        
        if len(color) == 3 :
            if type(color[0]) is not list :
                color = [color,]                         
        Application.FreezeObj(obj)
        if not len(faces):    
            mesh.Set(vertices)
        else :
            mesh.Set(vertices,faces)
        
        if color is not None and len(color) > 1:
            self.color_mesh_perVertex(mesh,color)
        doMaterial = True
        if type(material) is bool :
            doMaterial = material        
        if doMaterial:
            if material == None :
                if len(name.split("_")) == 1 : splitname = name
                else :
                    splitname = name.split("_")[1]  
                #print name,name[:4],splitname,splitname[:4]
                self.assignNewMaterial( "mat_"+name, color[0],'lambert' ,name)
            else :
                self.assignMaterial(name,material)    
        return self.getFullName(obj),self.getFullName(obj)#mesh#,outputMesh

    def updatePoly(self,obj,vertices=None,faces=None):
        if type(obj) is str:
            obj = self.getObject(obj)
            if obj is None : return
            node = self.getMShape(self.checkName(obj))
            if node.hasFn(om.MFn.kMesh):
                self.updateMesh(obj,vertices=vertices,faces=faces)
            elif node.hasFn(om.MFn.kParticle):
                self.updateParticle(obj,vertices=vertices,faces=faces)
                
    def updateMesh(self,meshnode,vertices=[],faces=[], smooth=False,obj = None):#chains.residues.atoms.coords,indices
#        print meshnode,type(meshnode)
        if type(meshnode) is str or type(meshnode) is unicode:            
        #    node = self.getMShape(self.checkName(meshnode))#self.getNode(self.checkName(meshnode))
            meshnode = self.getObject(meshnode)
        #Application.SelectObj(self.getFullName(meshnode), "","")
        #obj = Application.Selection(0)
        mesh = self.getMesh(meshnode)#meshnode.ActivePrimitive.Geometry
        print mesh,type(mesh)
        if self.usenumpy:
            vertices = numpy.array(vertices).transpose().tolist()
        else :
            verts = [[],[],[]]
            for v in vertices :
                for i in range(3):
                    verts[i].append(v[i])
            vertices = verts
        fs=[]
        for f in faces:
           fs.extend(self.ToFace(f))
        faces= fs
        
        #if len(color) == 3 :
        #    if type(color[0]) is not list :
        #        color = [color,]                         
        Application.FreezeObj(meshnode)
        if not len(faces):    
            mesh.Set(vertices)
        else :
            mesh.Set(vertices,faces)
        

    def ToVec(self,v,pos=True):
        if hasattr(v,"x"):
            return [v.x,v.y,v.z]
        else :
            return v

#    def arr2marr(self,v):
#        #from http://www.rtrowbridge.com/blog/2009/02/maya-api-docs-demystified-for-python-users/
#        self.msutil.createFromList( v, len(v) )
#        doubleArrayPtr = self.msutil.asDoublePtr()
#        return doubleArrayPtr
#
##    def vecp2m(self,v):
##        #from http://www.rtrowbridge.com/blog/2009/02/maya-api-docs-demystified-for-python-users/
##        doubleArrayPtr = self.arr2marr(v)
##        vec = om.MVector( doubleArrayPtr )
##        return vec
#
#    def FromVec(self,v):
#        if isinstance(v,om.MVector):
#            return v
#        else :
#            return om.MVector(v[0], v[1], v[2])
#   
#    def vec2m(self,v):
#        if isinstance(v,om.MVector):
#            return v
#        else :
#            return om.MVector(v[0], v[1], v[2])
#        
#    def matrixp2m(self,mat):
#        #from http://www.rtrowbridge.com/blog/2009/02/python-api-mtransformationmatrixgetrotation-bug/
#        if isinstance(mat,om.MTransformationMatrix)  :
#            return mat
#        getMatrix = om.MMatrix()
#        matrixList = mat#mat.transpose().reshape(16,)
#        om.MScriptUtil().createMatrixFromList(matrixList, getMatrix)
#        mTM = om.MTransformationMatrix( getMatrix )
#        rotOrder = om.MTransformationMatrix().kXYZ
#        return mTM
#    
#    def m2matrix(self,mMat):
#        #return mMat
#        #do we use numpy
#        if not isinstance(mMat,om.MTransformationMatrix)  :
#            return mMat
#        matrix = mMat.asMatrix()
#        us=om.MScriptUtil()
#        out_mat = [0.0, 0.0, 0.0,0.0,
#           0.0, 0.0, 0.0,0.0,
#           0.0, 0.0, 0.0,0.0,
#           0.0, 0.0, 0.0,0.0]
#        us.createFromList( out_mat, len(out_mat) )   
#        ptr1 = us.asFloat4Ptr()        
#        matrix.get(ptr1)
#        res_mat = [[0.0, 0.0, 0.0,0.0],
#                   [0.0, 0.0, 0.0,0.0],
#                   [0.0, 0.0, 0.0,0.0],
#                   [0.0, 0.0, 0.0,0.0]]
#        for i in range(4):
#            for j in range(4):
#                val = us.getFloat4ArrayItem(ptr1, i,j)
#                res_mat[i][j]=val
#        return res_mat
#  
#
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
#    def getMeshVertices(self,poly,transform=False,selected = False):
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
#    def getMeshNormales(self,poly,selected = False):
#        meshnode = self.checkIsMesh(poly)
#        nv = meshnode.numNormals()
#        normals = om.MFloatVectorArray()
#        meshnode.getVertexNormals(False,normals)
#        vnormals = [self.ToVec(normals[i]) for i in range(nv)]
#        if selected :
#            v,indice = self.getMeshVertices(poly,selected = selected)
#            vn=[]
#            for i in indice:
#                vn.append(vnormals[i])
#            return vn,indice
#        return vnormals
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
#    def getMeshFaces(self,poly,selected = False):
##        meshnode = self.checkIsMesh(poly)
#        nf = mesh.Polygons.count        
#        faces = [mesh.Polygons(i) for i in range(nf)]
##        faceConnects = om.MIntArray()
#        if selected :
#            return faces,range(nf)#mfaces_indice
#        return faces #
##        if self._usenumpy : 
##            return numpy.array(faceConnects).reshape((len(faceConnects)/3,3))
##        else :
##            return faceConnects
#        
    def DecomposeMesh(self,poly,edit=True,copy=True,tri=True,transform=True):
        if tri:
            self.triangulate(poly)
        #need the activeprimitive
        if type(poly) is str or type(poly) is unicode:
            poly = self.getObject(poly)
        obj=poly
        print (self.getName(poly),poly.Type)
        if obj.Type == "#model" :
            if obj.ModelKind == Constant.siModelKind_Instance :
                master = obj.InstanceMaster#.ActvePrimitive.Geometry
#                if poly is None :
                childs = self.getChilds(master)
                if len(childs):
                    poly = childs[0].ActivePrimitive.Geometry                        
            elif obj.ModelKind == Constant.siModelKind_Regular :
                childs = self.getChilds(obj)
                if len(childs):
                    poly = childs[0].ActivePrimitive.Geometry
                    
        if type(poly) is str or type(poly) is unicode or type(poly) is list:
            meshnode = self.getObject(poly).ActivePrimitive.Geometry#dagPath           
        else :
            #have to a object shape node or dagpath
            meshnode = poly
        print (meshnode,type(meshnode),hasattr(meshnode,"Points"))
        nv = meshnode.Points.Count
        nf = meshnode.Triangles.Count
        if self._usenumpy :
            faces = numpy.array(meshnode.Triangles.IndexArray).transpose()
            vertices = numpy.array(meshnode.Points.PositionArray).transpose()
            vnormals = numpy.array(meshnode.Points.NormalArray).transpose()
        else :
            #get the vertices
            vertices=[ self.ToVec(meshnode.Points(i).Position) for i in range(nv) ]
            vnormal =[ self.ToVec(meshnode.Points(i).Normal) for i in range(nv) ]
            faces = [meshnode.Triangles(i).IndexArray for i in range(nf)]
        if transform :
            matrice = SIMath.CreateMatrix4()
            oTrans = obj.Kinematics.Global.GetTransform2(None)
            oTrans.GetMatrix4(matrice)
            mat = matrice.Get2()
            if self._usenumpy :
                vertices = self.ApplyMatrix(vertices,numpy.array(mat).reshape(4,4).transpose())
            else :
                vertices=[ self.ToVec(meshnode.Points(i).Position.MulByMatrix4InPlace(matrice)) for i in range(nv) ]
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
        fileName, fileExtension = os.path.splitext(filename)
        doc = self.getCurrentScene()
        if fileExtension == ".fbx" :
            Application.FBXImport(filename,"")
        elif fileExtension == ".obj":
            Application.ObjImport(filename,1,1,True,True,False,True)
        elif fileExtension == ".dae":
            Application.ImportModel(filename,"","","","","","")
        else :
            print ("format not supported ",fileExtension)
        
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