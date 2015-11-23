
"""
    Copyright (C) <2010>  Autin L. TSRI
    
    This file git_upy/houdini/houdiniHelper.py is part of upy.

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
Created on Tue Jul 20 23:03:07 2010

@author: Ludovic Autin
@copyright: Ludovic Autin TSRI 2010

Library of houdini helper function to permit the communication and synchronisation
between houdini and a pmv cession.
"""
#base helper class
from pyubic import hostHelper

#host software import
import hou
import toolutils

#Houdini : name problem as maya does..not : or " " etc...
#GLOBAL VARIABLE
VERBOSE=0
DEBUG=1
#houdini is special as they froze geometry, and made it only readable.
#turn around is to trigger the sop cooking. The helper function will toggle 
#hou.pyubic[objname][parmas] and
#feed it by data. for instance createMesh and updateMesh...
#need to have the python sope in the custom library
class houMesh:
    def __init__(self,name,vertices=[],faces=[],colors=[],sopnode=None,
                    for_instance=False):
        self.name = name
        self.verts=vertices
        self.faces=faces
        self.colors=colors
        self.sop = sopnode
        self.for_instance = for_instance

class houdiniHelper(hostHelper.Helper):
    """
    The DejaVu helper abstract class
    ============================
        This is the DejaVu helper Object. The helper 
        give access to the basic function need for create and edit a host 3d object and scene.
    """    
    #this id can probably found in c4d.symbols
    #TAG ID
    SPLINE = "kNurbsCurve"
    INSTANCE = "kTransform"
    EMPTY = "kTransform"
    #msutil = om.MScriptUtil()
    pb = False
    VERBOSE=0
    DEBUG=0
    viewer = None
    host = "houdini"
    
    def __init__(self,master=None):
        hostHelper.Helper.__init__(self)
        #we can define here some function alias
        self.updateAppli = self.update
        self.Cube = self.box
        self.setInstance = self.newInstance
        self.getCurrentScene = toolutils.sceneViewer
        self.mesh={}#all geom in hou from helper
        self.reParent = self.reparent
        
    def addObjectToScene(self,sc,obj,parent=None):
        if parent is not None:
            self.reParent(obj,parent)

    def loadIntoAsset(self,otl_file_path,node_type_name, source):
        # Find the asset definition in the otl file.
        definitions = [definition
            for definition in hou.hda.definitionsInFile(otl_file_path)
            if definition.nodeTypeName() == node_type_name]
        assert(len(definitions) == 1)
        definition = definitions[0]
    
        # Store the source code into the PythonCook section of the asset.
        definition.addSection("PythonCook", source)

    def loadPythonSourceIntoAsset(self,otl_file_path, node_type_name, source_file_path):
        #usually CustomOtl ,"geom or obj",pyubic/houdini/sop.py
        # Load the Python source code., 
        source_file = open(source_file_path, "rb")
        source = source_file.read()
        source_file.close()
        self.loadIntoAsset(otl_file_path, node_type_name, source)

    def update(self):
        """
        Update the host viewport, ui or gl draw
        This function can't be call in a thread.
        """
        hou.ui.triggerUpdate()
        
    def checkName(self,name):
        """
        Check the name of the molecule/filename to avoid invalid caracter for the 
        host. ie maya didnt support object name starting with number. If a invalid 
        caracter is found, the caracter is removed.
    
        @type  name: string
        @param name: name of the molecule.
        @rtype:   string
        @return:  corrected name of the molecule.
        """    
    #    invalid=[] 
    #    for i in range(9):
    #        invalid.append(str(i))
        name = name.replace(":",".")
        name = name.replace(" ","")
    #    nonecar=[" ",":"]      
    #    for n in nonecar:
    #        if name.find(n) != -1 :
    #            name.replace(n,".")
    #    if name[0] in invalid:
    #        name= name[1:]    
        return name    

    def getName(self,o):
        """
        Return the name of an host object
    
        @type  o: hostObject
        @param o: an host object
        @rtype:   string
        @return:  the name of the host object
        """    
        if type(o) is str : return o
        return o.name()

    def getObjectName(self,o):
        """
        Return the name of an host object
    
        @type  o: hostObject
        @param o: an host object
        @rtype:   string
        @return:  the name of the host object
        """    
        if type(o) is str : return o
        return o.name()

    def getType(self,object):
        return object.type().name()

    def getMesh(self,m):
        if type(m) is str:
            m = self.getObject(m)
        if m is not None :
            if self.getType(m) == "null" :
                return m
            else :
                return m
        else :
            return None
            
    def getObject(self,name):
        """
        retrieve an object from his name. 
    
        @type  name: string
        @param name: request name of an host object
        
        @rtype:   hostObject
        @return:  the object with the requested name or None
        """
        if type(name) is str :
            return hou.node('/obj/'+self.checkName(name))
        else :
            return name

    def getTranslation(self,name):
        return self.getObject(name).parmTuple('t').eval()

    def setTranslation(self,name,pos=[0.,0.,0.]):
        self.getObject(name).parmTuple('t').set(pos)

    def translateObj(self,obj,position,use_parent=True):
        pass
#        if len(position) == 1 : c = position[0]
#        else : c = position
#        #print "upadteObj"
#        newPos=self.FromVec(c)
#        if use_parent : 
#            parentPos = self.GetAbsPosUntilRoot(obj)#parent.GetAbsPos()
#            newPos = newPos - parentPos
#            obj.SetAbsPos(newPos)
#        else :
#            pmx = obj.GetMg()
#            mx = c4d.Matrix()
#            mx.off = pmx.off + self.FromVec(position)
#            obj.SetMg(mx)
    
    def scaleObj(self,obj,sc):
        if type(obj) is str : 
            obj = self.getObject(obj)
        if type(sc) is float :
            sc = [sc,sc,sc]
        if type(sc) is int:
            sc = [sc,sc,sc]
        obj.parmTuple('s').set(sc)
    
    def rotateObj(self,obj,rot):
        #take radians, give degrees
        if type(obj) is str : 
            obj = self.getObject(obj)
        obj.parmTuple('r').set(rot) #Rx Ry Rz

    def newEmpty(self,name,location=None,parentCenter=None,**kw):
        """
        Create a new Null Object
    
        @type  name: string
        @param name: name of the empty
        @type  location: list
        @param location: position of the null object
        @type  parentCenter: list
        @param parentCenter: position of the parent object
        
        @type kw: dictionary
        @param kw: you can add your own keyword
       
        @rtype:   hostObject
        @return:  the null object
        """
        #null or subnet?
        typ='null' #null subnet 
        empty=hou.node('/obj').createNode(typ,self.checkName(name), run_init_scripts=False)
        #empty.setName(checkName(name))
        # delete default file node
        # empty.node('file1').destroy()
        if location != None :
            if parentCenter != None : 
                location = location - parentCenter
            empty.parmTuple("t").set(location)
            #set the position of the object to location       
        return empty
    
    def newInstance(self,name,object,location=None,hostmatrice=None,matrice=None):
        """
        Create a new Instance from another Object
    
        @type  name: string
        @param name: name of the instance
        @type  object: hostObject
        @param object: the object to herit from   
        @type  location: list/Vector
        @param location: position of the null object
        @type  hostmatrice: list/Matrix 
        @param hostmatrice: transformation matrix in host format
        @type  matrice: list/Matrix
        @param matrice: transformation matrix in epmv/numpy format
       
        @rtype:   hostObject
        @return:  the instance object
        """
        #actualy create a geom and then change to isntance, so we can have the MAterial tab
        instance = hou.node('/obj').createNode('geo',self.checkName(name), run_init_scripts=True)
        #need to delete the file
        #instance.children()[0].destroy()
        instance = instance.changeNodeType("instance")
        instance.setParms({"instancepath":object.path()})
        
        #instance parent = object  
        #instance name = name
        if location != None :
            #set the position of instance with location
            instance.parmTuple("t").set(location)
        #set the instance matrice
        self.setObjectMatrix(instance,matrice=matrice,hostmatrice=hostmatrice)
        return instance
    #alias

    def CopyAlonPoints(self,name,object,points=None,colors=None,location=None,
                     hostmatrice=None,matrice=None):
        """
        Create a new Instances from another Object along points. 
        Main problem, appear only at rendering time.
    
        @type  name: string
        @param name: name of the instance
        @type  object: hostObject
        @param object: the object to herit from   
        @type  location: list/Vector
        @param location: position of the null object
        @type  hostmatrice: list/Matrix 
        @param hostmatrice: transformation matrix in host format
        @type  matrice: list/Matrix
        @param matrice: transformation matrix in epmv/numpy format
       
        @rtype:   hostObject
        @return:  the instance object
        """
        if points is None :
            inst = self.newInstance(name,object,location=location,
                             hostmatrice=hostmatrice,matrice=matrice)
            return inst

        name = self.checkName(name)
        instance = hou.node('/obj').createNode('instance',name, run_init_scripts=True)
        instance.setParms({"instancepath":'/obj/'+object.name()})
        instance.parmTuple("ptinstance").set(1)
        addPtNode = instance.allSubChildren()[0]
        mesh = instance.createNode('mesh',"mesh_"+name)        
        houmesh = houMesh("mesh_"+name,vertices=vertices,faces=faces,
                          colors=color,sopnode = mesh,for_instance=True)
        self.mesh["mesh_"+name]  = houmesh
        #need to connect to addPoint node and mesh
        addPtNode.insertInput(0,mesh)
        #should be able to overwrite material for each instance appearly
        return instance

    def newInstances(self,name,object,points=None,colors=None,location=None,
                     hostmatrice=None,matrice=None):
        """
        Create a new Instances from another Object along points. 
        Main problem, appear only at rendering time.
    
        @type  name: string
        @param name: name of the instance
        @type  object: hostObject
        @param object: the object to herit from   
        @type  location: list/Vector
        @param location: position of the null object
        @type  hostmatrice: list/Matrix 
        @param hostmatrice: transformation matrix in host format
        @type  matrice: list/Matrix
        @param matrice: transformation matrix in epmv/numpy format
       
        @rtype:   hostObject
        @return:  the instance object
        """
        if points is None :
            inst = self.newInstance(name,object,location=location,
                             hostmatrice=hostmatrice,matrice=matrice)
            return inst

        name = self.checkName(name)
        instance = hou.node('/obj').createNode('instance',name, run_init_scripts=True)
        instance.setParms({"instancepath":'/obj/'+object.name()})
        instance.parmTuple("ptinstance").set(1)
        addPtNode = instance.allSubChildren()[0]
        mesh = instance.createNode('mesh',"mesh_"+name)        
        houmesh = houMesh("mesh_"+name,vertices=vertices,faces=faces,
                          colors=color,sopnode = mesh,for_instance=True)
        self.mesh["mesh_"+name]  = houmesh
        #need to connect to addPoint node and mesh
        addPtNode.insertInput(0,mesh)
        #should be able to overwrite material for each instance appearly
        return instance
    #alias
        
    def setObjectMatrix(self,object,matrice,hostmatrice=None):
        """
        set a matrix to an hostObject
    
        @type  object: hostObject
        @param object: the object who receive the transformation 
        @type  hostmatrice: hou.Matrix4 
        @param hostmatrice: transformation matrix in host format
        @type  matrice: list/Matrix
        @param matrice: transformation matrix in epmv/numpy format
        """
    
        if hostmatrice !=None :
            #set the instance matrice (hou.Matrix4)
            object.setWorldTransform(hostmatrice)
        if matrice != None:
            #convert the matrice in host format
            hm=hou.Matrix4(matrice.tolist())
            #set the instance matrice
            object.setWorldTransform(hm)
    
    def reparent(self,obj,parent):
        """
        Change the object parent using the specified parent objects
    
        @type  obj: hostObject
        @param obj: the object to be reparented
        @type  parent: hostObject
        @param parent: the new parent object
        """    
#        if type(obj) is str:
#            obj = getObject(obj)
#        if type(parent) is str:
#            parent = getObject(parent)
#        if parent.type().name() == 'subnet':
#            pass
        obj.setFirstInput(parent)
    
    def toggleDisplay(self,object,display):
        """
        Toggle on/off the display/visibility/rendermode of an hostObject in the host viewport
    
        @type  object: hostObject
        @param object: the object   
        @type  display: boolean
        @param display: if the object is displayed
        """    
        object.setDisplayFlag(display)
        object.setRenderFlag(display)

    def getVisibility(self,obj,editor=True, render=False, active=False):
        #0 off, 1#on, 2 undef
        #active = restriceted selection ?
        display = {0:True,1:False,2:True}
        if type (obj) == str :
            obj = self.getObject(obj)
        if editor and not render and not active:
            return obj.getDisplayFlag()
        elif not editor and render and not active:
            return obj.getRenderFlag()
        else :
            return obj.getDisplayFlag(),obj.getRenderFlag(),False
            
    def box(self,name,center=[0.,0.,0.],size=[1.,1.,1.],cornerPoints=None,visible=1,
                              mat = None):
        #import numpy
        box = hou.node('/obj').createNode('geo',name, run_init_scripts=False)
        meshbox = box.createNode('box',name+"_shape")
        if cornerPoints != None :
            for i in range(3):
                size[i] = cornerPoints[1][i]-cornerPoints[0][i]
            for i in range(3):
                center[i]=(cornerPoints[0][i]+cornerPoints[1][i])/2.
        meshbox.parmTuple('size').set(size)
        meshbox.parmTuple('t').set(center)
        return box

    def Cylinder(self,name,radius=1.,length=1.,res=0, pos = [0.,0.,0.]):
#        QualitySph={"0":16,"1":3,"2":4,"3":8,"4":16,"5":32}
        baseCyl = hou.node('/obj').createNode('geo',name, run_init_scripts=False)
        baseCylshape = baseCyl.createNode("tube",name+"_shape")
        #baseSphere.moveToGoodPosition()
        baseCylshape.parmTuple('radius').set([radius,radius])
        baseCylshape.parmTuple('t').set(pos)
        baseCylshape.parmTuple('height').set(length)
        baseCylshape.parmTuple('cap').set([1,])
        #as a Primitive by Default no quality ...
    #    baseSphere resolution = QualitySph[str(res)]
        return baseCyl

    def Sphere(self,name,radius=1.0,res=0, pos = [0.,0.,0.]):
        """
        Create a hostobject of type sphere.
        
        @type  name: string
        @param name: name of the sphere
        @type  radius: float
        @param radius: the radius of the sphere
        @type  res: float
        @param res: the resolution/quality of the sphere
        @type  pos: array
        @param pos: the position of the cylinder
        
        @rtype:   hostObject
        @return:  the created sphere
        """    
    
        QualitySph={"0":6,"1":4,"2":5,"3":6,"4":8,"5":16} 
        baseSphere = hou.node('/obj').createNode('geo',name, run_init_scripts=False)
        sph = baseSphere.createNode("sphere",name+"_shape")
        #baseSphere.moveToGoodPosition()
        sph.parmTuple('rad').set([radius,radius,radius])
        sph.parmTuple('t').set(pos)
        #as a Primitive by Default no quality ...
    #    baseSphere resolution = QualitySph[str(res)]
        return baseSphere

    def instancesSphere(self,name,centers,radii,oshsphere,
                        colors,scene,parent=None):
        #test the object to  be isntanciated
        #oshsphere#
        t=self.getType(oshsphere)
        if t == "null":
            obsphere = oshsphere.outputs()[0]
            meshsphere = obsphere.allSubChildren()[0]
        elif t == "geo" :
            obsphere = oshsphere
        else :
            if hasattr(oshsphere,"creator"):
                obsphere = oshsphere.creator()
            else :
                print t,oshsphere
        sphs=[]
        mat = None
        if len(colors) == 1:
            mat = self.retrieveColorMat(colors[0])
            if mat == None:		
                mat = self.addMaterial('mat_'+name,colors[0])
        for i in range(len(centers)):
            #check if exist
            sp = self.getObject(name+str(i))
            if sp is None :
                sp = self.newInstance(name+str(i),obsphere,location=centers[i])
                sphs.append(sp)
                if parent is not None :
                    self.reParent(sp,parent)
                sp.parmTuple("shop_materialpath").set('/shop/clay')
            else :
                self.translateObj(sp,centers[i])
            
            self.scaleObj(sp,radii[i])
        return sphs

    def updatePoly(self,polygon,faces=None,vertices=None,colors = None):
        if type(polygon) == str:
            polygon= self.mesh["mesh_"+polygon]
        else :
            polygon = self.mesh["mesh_"+self.getName(polygon)]
        if polygon == None : return		
        if vertices != None:
            polygon.verts = vertices
        if faces != None:
            polygon.faces = faces
        if colors != None:
            polygon.colors = colors
        polygon.sop.cook(force = True)

    def updateMesh(self,obj,vertices=None,faces = None,colors = None, smooth=False):
        if type(obj) == str:
            mesh = self.mesh["mesh_"+obj]
        else :
            mesh = self.mesh["mesh_"+self.getName(obj)]
        if obj == None : return     
        self.updatePoly(obj,faces=faces,vertices=vertices,colors=colors)
        #sys.stderr.write('\nnb v %d %d f %d' % (oldN,len(vertices),len(faces)))

    def polygons(self,name,proxyCol=False,smooth=False,color=None, material=None, **kw):
        import time
        t1 = time.time()
        vertices = kw["vertices"]
        faces = kw["faces"]
        normals = kw["normals"]
        frontPolyMode='fill'
        obj=hou.node('/obj').createNode("geo",name, run_init_scripts=False)
        mesh = obj.createNode('mesh',"mesh_"+name)        
        houmesh = houMesh("mesh_"+name,vertices=vertices,faces=faces,colors=color,sopnode = mesh)
        self.mesh["mesh_"+name]  = houmesh                            
        return obj,mesh
        
    def createsNmesh(self,name,vertices,vnormals,faces,smooth=False,
                     material=None,proxyCol=False,color=[[1,0,0],]):
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
        obj,mesh = self.polygons(name, vertices=vertices,normals=vnormals,
                                      faces=faces,material=material,color=color,
                                      smooth=smooth,proxyCol=proxyCol)
        return [obj,mesh]


#    
