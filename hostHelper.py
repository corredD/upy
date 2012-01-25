# -*- coding: utf-8 -*-
"""
Created on Sun Dec  5 23:30:44 2010

@author: Ludovic Autin - ludovic.autin@gmail.com
matrix and transformation came from 
http://www.lfd.uci.edu/~gohlke/code/transformations.py.html
"""
import os
import math
import random
from math import *

usenumpy = False
try :
    import numpy
    import numpy.oldnumeric as Numeric
    usenumpy = True
except :
    usenumpy = False

usePIL = False
try :
    import Image
    usePIL = True
except:
    usePIL = False  
    
from upy import colors

class Helper:
    """
    The Helper abstract Object
    ==========================
    This is the main class from which all helper derived. The Helper 
    give access to the basic function need for create and edit object 
    in the host.
    Most of the function define at this loevel are overwrite by the class child.
    """
    _usenumpy = usenumpy
    _MGLTools = False
    _usePIL = usePIL
    BONES = None
    IK = None
    
    def __init__(self,):
        try :
            import DejaVu
            _MGLTools = True
        except :
            _MGLTools = False
        self.createColorsMat()

    def fit_view3D(self,):
        pass

    
    def norm(self,a ,b,c):
        """ result = math.sqrt( a*a + b*b + c*c)
        a,b,c being double
        """
        return (math.sqrt( a*a + b*b + c*c))

    def normalize(self,A):
        """Normalize the Vector A"""
        norm = math.sqrt( A[0]*A[0] + A[1]*A[1] + A[1]*A[1])
        if (norm ==0.0) : return A
        else :return A/norm
        
    def measure_distance(self,c0,c1,vec=False):
        """ measure distance between 2 point specify by x,y,z
        c0,c1 should be Numeric.array"""
        if usenumpy :
            d = numpy.array(c1) - numpy.array(c0)
            s = numpy.sum(d*d)
        else :
            s=0.
            d=[0.,0.,0.]
            for i in range(3):
                d[i] = c1[i] - c0[i]
                s += d[i]^2
        if vec :
            return d,math.sqrt(s)
        else :
            return math.sqrt(s)




    def randpoint_onsphere(self,radius,biased=None):
        """ 
        Generate a random point on the outside of a sphere.
        -points (x,y,z) so that (x-a)^2 +(y-b)^2 + (z-c)^2 = R^2
        -To generate a random point on the sphere, it is necessary only 
        to generate two random numbers, z between -R and R, phi between 
        0 and 2 pi, each with a uniform distribution
        To find the latitude (theta) of this point, note that z=R*sin(theta), 
        so theta=sin-1(z/R); its longitude is (surprise!) phi.
        In rectilinear coordinates, 
        tetha = asin-1(z/R)
        x=R*cos(theta)*cos(phi), 
        y=R*cos(theta)*sin(phi), 
        z=R*sin(theta)= (surprise!) z.
        -hemispher
        theta (0 <= theta < 360) and phi (0 <= phi <= pi/2)
        x = cos(sqrt(phi)) cos(theta)
        y = cos(sqrt(phi)) sin(theta)
        z = sin(sqrt(phi)) 
        A whole sphere is obtained by simply randomising the sign of z. 
        -Azimuth axis is X axis. The elevation angle is measured as the angle 
        between the Z-axis pointing upwards and the radius vector. 
        From elementary spherical geometry:
        X coordinate=r*cos(pi/2-el)*cos(az)
        Y coordinate=r*cos(pi/2-el)*sin(az)
        Z Coordinate=r*sin(pi/2-el)

        r=1.1;
        az=pi/4;
        el=pi/4;
        plot3(r*sin(az)*cos(el), r*sin(az)*sin(el), r*cos(az), 'k*', 'MarkerSize',10
        """
        if biased is not None:
            theta = biased * ( 2 * pi )
            u = biased * 2 - 1 #represent sin(phi)
        else :
            theta = random.random() * ( 2 * pi )
            u = random.random() * 2 - 1
        x = radius * sqrt(  1 - u**2) * cos(theta)
        y = radius * sqrt(  1 - u**2) * sin(theta)
        z = radius * u
        return [x,y,z]



    def rotatePoint(self,pt,m,ax):
        """ rotate the point pt [x,y,z] around axe ax[0],ax[1],ax[2] by ax[3] radians,
        and translate by m [x,y,z].
        """
        x=pt[0]
        y=pt[1]
        z=pt[2]
        u=ax[0]
        v=ax[1]
        w=ax[2]
        ux=u*x
        uy=u*y
        uz=u*z
        vx=v*x
        vy=v*y
        vz=v*z
        wx=w*x
        wy=w*y
        wz=w*z
        sa=sin(ax[3])
        ca=cos(ax[3])
        pt[0]=(u*(ux+vy+wz)+(x*(v*v+w*w)-u*(vy+wz))*ca+(-wy+vz)*sa)+ m[0]
        pt[1]=(v*(ux+vy+wz)+(y*(u*u+w*w)-v*(ux+wz))*ca+(wx-uz)*sa)+ m[1]
        pt[2]=(w*(ux+vy+wz)+(z*(u*u+v*v)-w*(ux+vy))*ca+(-vx+uy)*sa)+ m[2]
        return pt

    def eulerToMatrix(self,euler): #double heading, double attitude, double bank
        """
        code from 'http://www.euclideanspace.com/maths/geometry/rotations/conversions/'.
        this conversion uses NASA standard aeroplane conventions as described on page:
        'http://www.euclideanspace.com/maths/geometry/rotations/euler/index.htm'
    
        Coordinate System: right hand
    
        Positive angle: right hand
    
        Order of euler angles: heading first, then attitude, then bank
    
        matrix row column ordering:
    
        [m00 m01 m02]
    
        [m10 m11 m12]
    
        [m20 m21 m22]
    
        @type euler:   3d array
        @param euler:  the euler angle to convert in matrice
    
        @rtype: 4x4array
        @return: the matrix computed from the euler angle
    
        """
        # Assuming the angles are in radians.
        heading=euler[0]
        attitude=euler[1]
        bank=euler[2]
        m=[[ 1.,  0.,  0.,  0.],
           [ 0.,  1.,  0.,  0.],
           [ 0.,  0.,  1.,  0.],
           [ 0.,  0.,  0.,  1.]]
        ch = math.cos(heading)
        sh = math.sin(heading)
        ca = math.cos(attitude)
        sa = math.sin(attitude)
        cb = math.cos(bank)
        sb = math.sin(bank)
        m[0][0] = ch * ca
        m[0][1] = sh*sb - ch*sa*cb
        m[0][2] = ch*sa*sb + sh*cb
        m[1][0] = sa
        m[1][1] = ca*cb
        m[1][2] = -ca*sb
        m[2][0] = -sh*ca
        m[2][1] = sh*sa*cb + ch*sb
        m[2][2] = -sh*sa*sb + ch*cb
        return m
        


    def getTubeProperties(self,coord1,coord2):
        """
        From two point return the length, and the orientation from one to another
        @type  coord1: vector
        @param coord1: first point
        @type  coord2: vector
        @param coord2: second point
    
        @rtype:   tupple
        @return:  length, orientation, and intermediate point
        """
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




    def update(self,):
        """
        Update the host viewport, ui or gl draw
        This function can't be call in a thread.
        """
        pass
    def fit_view3D(self):
        """
        Function that should recenter the viewport to the object in the scene
        """
        pass

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
        invalid=[] 
        for i in range(9):
            invalid.append(str(i))       
        if name[0] in invalid:
            name= name[1:]    
        return name   
        
    def getObject(self,name):
        """
        retrieve an object from his name. 
    
        @type  name: string
        @param name: request name of an host object
        
        @rtype:   hostObject
        @return:  the object with the requested name or None
        """
        return None

    def getObjectName(self,o):
        """
        Return the name of an host object
    
        @type  o: hostObject
        @param o: an host object
        @rtype:   string
        @return:  the name of the host object
        """
        pass

    def getCurrentScene(self,):
        """
        Return the current/active working document or scene
    
        @rtype:   scene
        @return:  the active scene
        """        
        pass

    def getCurrentSelection(self,):
        """
        Return the current/active selected object in the document or scene
    
        @rtype:   liste
        @return:  the list of selected object
        """        
        pass

    def getPosUntilRoot(self,object):
        """
        Go through the hierarchy of the object until reaching the top level, 
        increment the position to get the transformation due to parents. 
    
        @type  object: hostObject
        @param object: the object   
    
       
        @rtype:   list
        @return:  the cumulative translation along the parenting hierarchy   
        """
        
        stop = False
        #get the first parent
        pos=[0,0,0]
        while not stop :
            #get the parent position, and add it to pos
            #get the parent of the previous parent
            parent=None
            if parent is None :
                stop = True
        return pos        
        
    def addObjectToScene(self,doc,object,parent=None,centerRoot=True,rePos=None):
        """
        Insert/add an object to the current document under the specified parent, and
        at the specified location
    
    
        @type  doc: hostScene
        @param doc: the scene where to insert the object   
        @type  object: hostObject
        @param object: the object to insert
        @type  parent: hostObject
        @param parent: the parent of the object to insert under  
        @type  centerRoot: boolean
        @param centerRoot: if the object have to be recentered according the top-level  
        @type  rePos: list
        @param rePos: the location of the object in the scene 
        """
        #get the object name
        name=""
        #if the object is not already in the scene
        if self.getObject(name) == None:
            if parent != None : 
                if type(parent) == str : parent = self.getObject(parent)
                #if parent exist, insert the object under it
                pass
                if centerRoot :
                    #get the current position of the object
                    currentPos = []
                    if rePos != None : 
                        parentPos = rePos          
                    else :
                        parentPos = self.getPosUntilRoot(obj)#parent.GetPos()
                    #set the new position of the object
                    pass
            else :    
                #insert the object
                pass
    
    
    def AddObject(self,object,parent=None,centerRoot=True,rePos=None):
        """
        Insert/add an object to the current document under the specified parent, and
        at the specified location. This function is an alias for addObjectToScene to
        permit to some script to work either in dejavu and the host.
    
    
        @type  object: hostObject
        @param object: the object to insert
        @type  parent: hostObject
        @param parent: the parent of the object to insert under  
        @type  centerRoot: boolean
        @param centerRoot: if the object have to be recentered according the top-level  
        @type  rePos: list
        @param rePos: the location of the object in the scene 
        """
    
        doc = self.getCurrentScene()
        self.addObjectToScene(doc,object,parent=parent,centerRoot=centerRoot,
                              rePos=rePos)

    def ObjectsSelection(self,listeObjects,typeSel="new"):
        """
        Modify the current object selection.
        
        @type  listeObjects: list
        @param listeObjects: list of object to joins
        @type  typeSel: string
        @param listeObjects: type of modification: new,add,...
    
        """    
#        dic={"add":c4d.SELECTION_ADD,"new":c4d.SELECTION_NEW}
        sc = self.getCurrentScene()
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
    #    sc.SetSelection(listeObjects[0],c4d.SELECTION_NEW)
    #    for i in range(1,len(listeObjects)):
    #        sc.SetSelection(listeObjects[i],c4d.SELECTION_ADD)
        #then call the command/function that joins the object selected
    #    c4d.CallCommand(CONNECT)
        
    
    
    def addCameraToScene(self,name,Type,focal,center,scene):
        """
        Add a camera object to the scene
    
        @type  name: string
        @param name: name of the camera
        @type  Type: cameraType
        @param Type: perspective, orthogonale etc...
        @type  focal: float
        @param focal: the focal of the camera
        @type  center: list
        @param center: the position of the camera
        @type  scene: host scene
        @param scene: the scene
        
        """    
         
        cam = None
        #cam.SetPos(center)
        #cam perspective or parrallel
        #cam focal = float(focal)  #
        #most of the time we apply a rotation to get the same result as in PMV
        #cam rotZ = pi/2.
        self.addObjectToScene(scene,cam,centerRoot=False)    
    
    def addLampToScene(name,Type,rgb,dist,energy,soft,shadow,center,scene):
        """
        Add a light to the scene
    
        @type  name: string
        @param name: name of the instance
        @type  Type: light hostType/int etc..
        @param Type: the light type : spot,sun,omni,etc..
        @type  rgb: list of int 0-255
        @param rgb: color of the light in rgb
        @type  dist: float
        @param dist: light distance of attenuation
        @type  energy: float
        @param energy: intensity of the light
        @type  soft: bool
        @param soft: soft light
        @type  shadow: boolean
        @param shadow: does the light produce shadow
        @type  scene: host scene
        @param scene: the scene
        """    
        dicType={'Area':0,'Sun':3}
        lamp = None#c4d.BaseObject(LIGHT)
        #lamp name (name)
        #lamp position (center)
        #lamp color (float(rgb[0]), float(rgb[1]), float(rgb[2]))#color
        #lamp energy  float(energy) #intensity
        #lamp type dicType[Type] #type
        if shadow : 
            #lampe shadow 
            pass
        self.addObjectToScene(scene,lamp,centerRoot=False)    
        """
        lampe.setDist(dist)
        lampe.setSoftness(soft)
        """

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
        empty=None#
        if location != None :
            if parentCenter != None : 
                location = location - parentCenter
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
        #instance = None#
        #instance parent = object  
        #instance name = name
        if location != None :
            #set the position of instance with location
            pass
        #set the instance matrice
        self.setObjectMatrix(object,matrice=matrice,hostmatrice=hostmatrice)
        return instance
   
    def translateObj(self,object,position,use_parent=True):
        """
        Translation : Move the object to the vector position 
    
        @type  object: hostObject
        @param object: the object   
        @type  position: liste/array
        @param position: the new object position px,py,pz  
        @type  use_parent: boolean
        @param use_parent: if the parent position is used
        """
        pass
    
    def scaleObj(self,object,sc):
        """
        Scale : scale the object by the vector scale 
    
        @type  object: hostObject
        @param object: the object   
        @type  sc: float or liste/array
        @param sc: the scale vector s,s,s or sx,sy,sz  
        """
        pass
        
    def rotateObj(self,object,rotation):
        """
        Translation : Move the object to the vector position 
        This method could take either, a matrice, a euler array, a quaternion...
    
        @type  object: hostObject
        @param object: the object   
        @type  rotation: liste/array - matrice
        @param rotation: the new object rotation  
        """
        pass


    def getTranslation(self,name,absolue=True):
        """
        Return the current position (translation)  of the  given object in absolute or local world
        
        @type  name: hostObject
        @param name: the object name
    
       
        @rtype:   3d vector/list
        @return:  the position   
        """
        return [0.,0.,0.]
        

    def toggleDisplay(self,object,display):
        """
        Toggle on/off the display/visibility/rendermode of an hostObject in the host viewport
    
        @type  object: hostObject
        @param object: the object   
        @type  display: boolean
        @param display: if the object is displayed
        """    

    
    def getVisibility(self,obj,editor=True, render=False, active=False):    
        """
        return the editor/renedring/active visibility state of the given object
    
        @type  obj: hostObject
        @param obj: the object   
        @type  editor: boolean
        @param editor: request editor visibility
        @type  render: boolean
        @param render: request rendering visibility
        @type  active: boolean
        @param active: request active states ie C4D
        
        @rtype:   bool/array of bool
        @return:  the current visibility state of the object
        """    
        pass
    
    
    def toggleEditMode(self):
        """Turn off edit mode (if any)"""
        pass

    def restoreEditMode(self, editmode=1):
        """Restor any edit mode"""
        pass
    
    def setObjectMatrix(self,object,matrice,hostmatrice=None):
        """
        set a matrix to an hostObject
    
        @type  object: hostObject
        @param object: the object who receive the transformation 
        @type  hostmatrice: list/Matrix 
        @param hostmatrice: transformation matrix in host format
        @type  matrice: list/Matrix
        @param matrice: transformation matrix in epmv/numpy format
        """
    
        if hostmatrice !=None :
            #set the instance matrice
            pass
        if matrice != None:
            #convert the matrice in host format
            #set the instance matrice
            pass

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

    def updateTubeObjs(self,listeObj,listePts,listeInd=None):
        if listeInd is None :
            [self.updateTubeObj(listeObj[i],listePts[j],listePts[j+1]) \
                for i,j in zip(list(range(len(listeObj))),list(range(len(listePts))))]
        else :
            [self.updateTubeObj(listeObj[i],listePts[listeInd[i][0]],listePts[listeInd[i][1]]) \
                for i,j in range(len(listeObj))]

    def convertColor(self,col,toint=True):
        """
        This function will convert a color array [r,g,b] from range 1-255 
        to range 0.-1 (vice/versa)
        
        @type  col: array
        @param col: the color [r,g,b]
        @type  toint: boolean
        @param toint: way of the convertion, if true convert to 1-255, if false
        convert to range 0-1
       
        @rtype:   array
        @return:  the converted color [0-1.,0-1.,0-1.] or [1-255,1-255,1-255]
        """
        #its seems that pymol color for instance are in range 0. 1.00001 ?
        if toint and max(col)<=1.00001: col = [int(x*255) for x in col]
        elif not toint and max(col)>1.00001: col = [x/255. for x in col]
        return col
        
    def addMaterialFromDic(self,dic):
        #dic: Name:Color
        [self.addMaterial(x,dic[x]) for x in list(dic.keys())]

    def createColorsMat(self):
        """
        Create a Material for all defined colors
    
        @rtype:   list
        @return:  the list of the new colors material 
        """            
        Mat=[]
        for col in colors.cnames:
            Mat.append(self.addMaterial(col,eval("colors."+col)))
        return Mat
    
    def retrieveColorMat(self,color):
        """
        Retrieve a material in the current document from his color (r,g,b), if his 
        color correpond to a DejaVu color
    
        @type  color: array
        @param color: the material color (r,g,b)
    
        @rtype:   hostMaterial
        @return:  the material of color color
        """            
        doc = self.getCurrentScene()
        for col in colors.cnames:
            if color == eval("colors."+col) :
                return self.getMaterial(col)    
        return None
        
    def addMaterial(self,name, color):
        """
        Add a material in the current document 
    
        @type  name: string
        @param name: the material name
        @type  color: array
        @param color: the material color (r,g,b)
    
        @rtype:   hostMaterial
        @return:  the new material 
        """    
        pass

    def assignMaterial (self,mat, object):
        """
        Assign the provided material to the object 
    
        @type  mat: mat
        @param mat: the material
        @type  object: hostApp object
        @param object: the object
        """    
        #verify if the mat exist, if the string.
        #apply it to the object
        pass

    def colorMaterial(self,mat,col):
        """
        Color a given material using the given color (r,g,b).
    
        @type  mat: hostMaterial
        @param mat: the material to change
        @type  col: array
        @param col: the color (r,g,b)
        """ 
        #put your code here
        #get the materiel if mat is a string for instance
        #or verify if the material exist in the current document
        #then change his color channel using 'col'
        pass

    def getMaterial(self,name):
        pass

    def getAllMaterials(self):
        pass

    def colorObject(self,obj,color,**options):
        """Apply the given color to the given object, 
        """        
        useMaterial = False
        useObjectColors = False        
        if options.has_key("useMaterial"):
            useMaterial = options["useMaterial"]
        if options.has_key("useObjectColors"):
            useObjectColors = options["useObjectColors"]
        
        
    def changeColor(self,obj,colors,perVertex=False,proxyObject=True,doc=None,pb=False,
                    facesSelection=None,faceMaterial=False):
        """Apply the given set of color to the given object, 
        if the object is a mesh this functino handle the color per vertex
        """
        pass
    
    def changeObjColorMat(self,obj,color):
        """change the diffuse color of the object material"""
        pass

    
    def getMesh(self,name):
        return name

    def checkIsMesh(self,name):
        return name

    def getName(self,object):
        return ""
        
    def reParent(self,objs,parent):
        """
        Change the object parent using the specified parent objects
    
        @type  objs: hostObject
        @param objs: the object to be reparented
        @type  parent: hostObject
        @param parent: the new parent object
        """    
        pass


    def deleteChildrens(self,obj):
        #recursively delete childrenobject
        childs = self.getChilds(obj)
#        print childs
        if childs :
            if type(childs) is list or type(childs) is tuple:
                [self.deleteChildrens(ch) for ch in childs]
            else :
                self.deleteChildrens(childs)
#        else :
        self.deleteObject(obj)

    def constraintLookAt(self,object):
        """
        Cosntraint an hostobject to llok at the camera
        
        @type  object: Hostobject
        @param object: object to constraint
        """
        pass

#===============================================================================
#     Basic object
#===============================================================================
    def Text(self,name="",string="",parent=None,size=5.,pos=None,font=None,lookAt=False):
        """
        Create a hostobject of type Text.
        
        @type  name: string
        @param name: name of the circle
        @type  string: string
        @param string: text to display
        @type  parent: Hostobject
        @param parent: parent of the text
        @type  size: Float
        @param size: height of the text
        @type  pos: Vector
        @param pos: position of the text
        @type  font: ?
        @param font: the font to use
        @type  lookAt: boolean
        @param lookAt: either the text  is constraint to look at the camera/view
        
        @rtype:   hostObject
        @return:  the created text object
        """    
        text = None
        return text
        
    def Circle(self,name, rad=1.):
        """
        Create a hostobject of type 2d circle.
        
        @type  name: string
        @param name: name of the circle
        @type  rad: float
        @param rad: the radius of the cylinder (default = 1.)
        
        @rtype:   hostObject
        @return:  the created circle
        """    
        #put the apropriate code here
        circle=None
        #set name and rad for the circle
        return circle
    
    def Cylinder(self,name,radius=1.,length=1.,res=16, pos = [0.,0.,0.]):
        """
        Create a hostobject of type cylinder.
        
        @type  name: string
        @param name: name of the cylinder
        @type  radius: float
        @param radius: the radius of the cylinder
        @type  length: float
        @param length: the length of the cylinder
        @type  res: float
        @param res: the resolution/quality of the cylinder
        @type  pos: array
        @param pos: the position of the cylinder
        
        @rtype:   hostObject
        @return:  the created cylinder
        """    
    
        baseCyl = None #use the hostAPI
    #    baseCyl radius = radius
    #    baseCyl length = length
    #    baseCyl resolution = res
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
        baseSphere = None#c4d.BaseObject(c4d.Osphere)
    #    baseSphere radius = radius
    #    baseSphere resolution = QualitySph[str(res)]
    #    baseSphere position = position
        return baseSphere
        
    def box(self,name,center=[0.,0.,0.],size=[1.,1.,1.],cornerPoints=None,visible=1):
        """
        Create a hostobject of type cube.
        
        @type  name: string
        @param name: name of the box
        @type  center: array
        @param center: the center of the box
        @type  size: array
        @param size: the size in x y z direction
        @type  cornerPoints: array list
        @param cornerPoints: the upper-left and bottom right corner point coordinates
        @type  visible: booelan
        @param visible: visibility of the cube after creation (deprecated)
        
        @rtype:   hostObject
        @return:  the created box
        """    
        #put your code
        box=None
        #set the name 'name'
        #if corner is provided compute the cube dimension in x,y,z, and the center
        if cornerPoints != None :
            for i in range(3):
                size[i] = cornerPoints[1][i]-cornerPoints[0][i]
            center=(numpy.array(cornerPoints[0])+numpy.array(cornerPoints[1]))/2.
        #position the cube to center
        #set the dimension to size
        #return the box
        return box

    def updateBox(self,box,center=[0.,0.,0.],size=[1.,1.,1.],cornerPoints=None,
                    visible=1, mat = None):
        """
        Update the given box.
        
        @type  box: string 
        @param box: name of the box
        @type  center: array
        @param center: the new center of the box
        @type  size: array
        @param size: the new size in x y z direction
        @type  cornerPoints: array list
        @param cornerPoints: the new upper-left and bottom right corner point coordinates
        @type  visible: booelan
        @param visible: visibility of the cube after creation (deprecated)

        """    
        #put your code
        box=None
        #set the name 'name'
        #if corner is provided compute the cube dimension in x,y,z, and the center
        if cornerPoints != None :
            for i in range(3):
                size[i] = cornerPoints[1][i]-cornerPoints[0][i]
            center=(numpy.array(cornerPoints[0])+numpy.array(cornerPoints[1]))/2.
        #position the cube to center
        #set the dimension to size

    def getCornerPointCube(self,obj):
        """
        Return the corner Point of the Given Cube/Box
        
        @type  obj: string
        @param obj: name of the box
         
        @rtype:   array 2x3
        @return:  the upper-left and bottom right corner point coordinates
        """    
        
        size = self.ToVec(obj[1100])#this will broke other host!
        center = self.ToVec(self.getTranslation(obj))
#        print center
        cornerPoints=[]
        #lowCorner
        lc = [center[0] - size[0]/2.,
              center[1] - size[1]/2.,
              center[2] - size[2]/2.]
        #upperCorner
        uc = [center[0] + size[0]/2.,
              center[1] + size[1]/2.,
              center[2] + size[2]/2.]
        cornerPoints=[[lc[0],lc[1],lc[2]],[uc[0],uc[1],uc[2]]]
        return cornerPoints
        
    def spline(self,name, points,close=0,type=1,scene=None,parent=None):
        """
        This will return a hostApp spline/curve object according the given list
        of point.
        
        @type  name: string
        @param name: name for the object
        @type  points: liste/array vector
        @param points: list of position coordinate of the curve point
        @type  close: bool/int
        @param close: is the curve is closed
        @type  type: int/string
        @param type: ususally describe type of curve, ie : bezier, linear, cubic, etc...
        @type  scene: hostApp scene
        @param scene: the current scene
        @type  parent: hostObject
        @param parent: the parent for the curve
    
        @rtype:   hostObject
        @return:  the created spline
        """
        #create the spline
        spline=None
        #define type, close, name
        #set the points
        for i,p in enumerate(points):
            #set every i point
            pass 
        #add the object to the scene
        if scene != None :
            self.addObjectToScene(scene,spline,parent=parent)
        return spline,None

    def plane(self,name,center=[0.,0.,0.],size=[1.,1.],cornerPoints=None,visible=1,**kw):
        """
        Create a hostobject of type cube.
        
        @type  name: string
        @param name: name of the plane
        @type  center: array
        @param center: the center of the plane
        @type  size: array
        @param size: the size in x y z direction
        @type  cornerPoints: array list
        @param cornerPoints: the upper-left and bottom right corner point coordinates
        @type  visible: booelan
        @param visible: visibility of the plane after creation (deprecated)
        @type  kw: dictionary
        @param kw: list of additional arguments : "material", subdivision", axis"
        
        @rtype:   hostObject
        @return:  the created plane
        """    
        #put your code
        plane=None
        #set the name 'name'
        #if corner is provided compute the cube dimension in x,y,z, and the center
        if cornerPoints != None :
            for i in range(3):
                size[i] = cornerPoints[1][i]-cornerPoints[0][i]
            center=(numpy.array(cornerPoints[0])+numpy.array(cornerPoints[1]))/2.
        #position the cube to center
        #set the dimension to size
        #return the box
        return plane

    def update_spline(self,name,coords):
        """
        This will update the spline point coordinate
        
        @type  name: string
        @param name: name for the spline to update
        @type  coords: liste/array vector
        @param coords: list of new position coordinate to apply to the curve point
        """
        pass


#===============================================================================
#     Platonic
#===============================================================================
    #this already exist in c4d
    #also exist in glut
    def Platonic(self,name,Type,radius,**kw):
        """ Generate one of the 5 platonic solid. The name of each figure is derived from its number of faces: respectively "tetra" 4, "hexa" 6, "ocata" 8, "dodeca" 12, and 20.
        @type  name: string
        @param name: name of the platonic
        @type  Type: string or int
        @param Type: type of the platonic, can be tetra" 4, "hexa" 6, "ocata" 8, "dodeca" 12, and "ico" 20.
        @type  radius: float
        @param radius: radius of the embeding sphere
        @type  kw: dictionary
        @param kw: additional arguement such as meterial,parent
        
        @rtype:   hostObject
        @return:  the created platonic
        """
        dicT={"tetra":self.tetrahedron,
              "hexa":self.hexahedron,
              "octa":self.octahedron,
              "dodeca":self.dodecahedron,
              "icosa":self.icosahedron}#BuckyBall ?
        dicTF={4:self.tetrahedron,
              6:self.hexahedron,
              8:self.octahedron,
              12:self.dodecahedron,
              20:self.icosahedron}
        parent = None
        if "parent" in kw :
            parent = kw["parent"]
        if Type in dicT  :
            v,f,n = dicT[Type](radius)
            return self.createsNmesh(name,v,None,f,parent = parent)
        elif Type in dicTF :
            v,f,n = dicTF[Type](radius)
            return self.createsNmesh(name,v,None,f,parent = parent)            
        else :
            return None,None
            
    def tetrahedron(self,radius):
        """
        Create the mesh data of a tetrahedron of a given radius
        
        @type  radius: float
        @param radius: radius of the embeding sphere
        
        @rtype:   array
        @return:  vertex,face, face normal of the tetrahedron        
        """
        
        faceIndices = ( (0,2,3), (3,2,1), #bot
                        (3, 1, 4), 
                        (3, 4, 0), 
                        (2, 4, 1), 
                        (2, 0, 4), 
                        )
        a = 1 / sqrt(3)
        faceNormals = ( ( a,  a, -a),
                        (-a,  a, -a), 
                        ( a, -a, -a),
                        (-a, -a, -a), )        
        diameter = radius * 2
        width  = diameter
        height = diameter
        depth  = diameter     
        boundingRadius = radius
        surfaceArea = (sqrt(3) / 2) * (radius ** 2)
        volume = (4/3) * (radius ** 3)
        _corners = (
            (-radius, 0.0, 0.0), (radius, 0.0, 0.0),
            (0.0, radius, 0.0), (0.0, -radius, 0.0),
            (0.0, 0.0, radius), )#(0.0, 0.0, radius))
        return _corners,faceIndices,faceNormals
        
    def Tetrahedron(self,name,radius):
        """
        Create the mesh data and the mesh object of a Tetrahedron of a given radius
        
        @type  name: string
        @param name: name for the spline to update        
        @type  radius: float
        @param radius: radius of the embeding sphere
        
        @rtype:   Object, Mesh
        @return:  Tetrahedron Object and Mesh      
        """          
        v,f,n = self.tetrahedron(radius)
        ob,obme = self.createsNmesh(name,v,None,f)
        return ob,obme
        
    
    def hexahedron(self,radius):
        """
        Create the mesh data of a hexahedron of a given radius
        
        @type  radius: float
        @param radius: radius of the embeding sphere
        
        @rtype:   array
        @return:  vertex,face, face normal of the hexahedron        
        """        
        faceIndices = ( (3,2,0), (1,2,3), #bot
                        (4,6,7), (7,6,5), #top
                        (0,2,6), (6,4,0), #front
                        (2,1,5), (5,6,2), #right
                        (1,3,7), (7,5,1), #rear
                        (3,0,4), (4,7,3), #left
                        )
        a = 1.0
        faceNormals = None
        diameter = radius * 2
        width  = diameter
        height = diameter
        depth  = radius*sin(radians(45.))
        boundingRadius = radius
        surfaceArea = (sqrt(3) / 2) * (radius ** 2)
        volume = (4/3) * (radius ** 3)
        _corners = (
            (-radius, 0.0, -depth), (radius, 0.0, -depth),
            (0.0, -radius, -depth), (0.0, radius, -depth),
            (-radius, 0.0, depth), (radius, 0.0, depth),
            (0.0, -radius, depth), (0.0, radius, depth),)

        return _corners,faceIndices,faceNormals
        
    def Hexahedron(self,name,radius):  
        """
        Create the mesh data and the mesh object of a Hexahedron of a given radius
        
        @type  name: string
        @param name: name for the spline to update        
        @type  radius: float
        @param radius: radius of the embeding sphere
        
        @rtype:   Object, Mesh
        @return:  Hexahedron Object and Mesh      
        """          

        v,f,n = self.hexahedron(radius)
        ob,obme = self.createsNmesh(name,v,None,f)
        return ob,obme    
    
    def octahedron(self,radius):
        """
        Create the mesh data of a octahedron of a given radius
        
        @type  radius: float
        @param radius: radius of the embeding sphere
        
        @rtype:   array
        @return:  vertex,face, face normal of the octahedron        
        """        

        
        faceIndices = ((3, 5, 1), (3, 1, 4), (3, 4, 0), (3, 0, 5),
                             (2, 1, 5), (2, 4, 1), (2, 0, 4), (2, 5, 0))
        a = 1 / sqrt(3)
        faceNormals = (( a,  a,  a), ( a,  a, -a),
                             (-a,  a, -a), (-a,  a,  a),
                             ( a, -a,  a), ( a, -a, -a),
                             (-a, -a, -a), (-a, -a,  a))
        diameter = radius * 2
        width  = diameter
        height = diameter
        depth  = diameter     
        boundingRadius = radius
        surfaceArea = (sqrt(3) / 2) * (radius ** 2)
        volume = (4/3) * (radius ** 3)
        _corners = (
            (-radius, 0.0, 0.0), (radius, 0.0, 0.0),
            (0.0, -radius, 0.0), (0.0, radius, 0.0),
            (0.0, 0.0, -radius), (0.0, 0.0, radius))

        return _corners,faceIndices,faceNormals
        
    def Octahedron(self,name,radius): 
        """
        Create the mesh data and the mesh object of a Octahedron of a given radius
        
        @type  name: string
        @param name: name for the spline to update        
        @type  radius: float
        @param radius: radius of the embeding sphere
        
        @rtype:   Object, Mesh
        @return:  Octahedron Object and Mesh      
        """       
        v,f,n = self.octahedron(radius)
        ob,obme = self.createsNmesh(name,v,None,f)
        return ob,obme


    
    def dodecahedron(self,radius):
        """
        Create the mesh data of a dodecahedron of a given radius
        
        @type  radius: float
        @param radius: radius of the embeding sphere
        
        @rtype:   array
        @return:  vertex,face, face normal of the dodecahedron        
        """        

        #from http://www.cs.umbc.edu/~squire/reference/polyhedra.shtml#dodecahedron
        vertices=[]#; /* 20 vertices with x, y, z coordinate */
        Pi = math.pi
        phiaa = 52.62263590; #/* the two phi angles needed for generation */
        phibb = 10.81231754;
        r = radius; #/* any radius in which the polyhedron is inscribed */
        phia = Pi*phiaa/180.0; #/* 4 sets of five points each */
        phib = Pi*phibb/180.0;
        phic = Pi*(-phibb)/180.0;
        phid = Pi*(-phiaa)/180.0;
        the72 = Pi*72.0/180;
        theb = the72/2.0#; /* pairs of layers offset 36 degrees */
        the = 0.0;
        for i in range(5):
            x=r*cos(the)*cos(phia);
            y=r*sin(the)*cos(phia);
            z=r*sin(phia);
            vertices.append([x,y,z])
            the = the+the72;
  
        the=0.0;
        for i in range(5,10):#(i=5; i<10; i++)
            x=r*cos(the)*cos(phib);
            y=r*sin(the)*cos(phib);
            z=r*sin(phib);
            vertices.append([x,y,z])
            the = the+the72;
  
        the = theb;
        for i in range(10,15):#for(i=10; i<15; i++)
            x=r*cos(the)*cos(phic);
            y=r*sin(the)*cos(phic);
            z=r*sin(phic);
            vertices.append([x,y,z])
            the = the+the72;
            
        the=theb;
        for i in range(15,20):#for(i=15; i<20; i++)
            x=r*cos(the)*cos(phid);
            y=r*sin(the)*cos(phid);
            z=r*sin(phid);
            vertices.append([x,y,z])
            the = the+the72;
  
        #/* map vertices to 12 faces */
        #these are the ngons
        ngonsfaces = ((0,1,2,3,4),(0,1,6,10,5),(1,2,7,11,6),
                (2,3,8,12,7),(3,4,9,13,8),(4,0,5,14,9),
                (15,16,11,6,10),(16,17,12,7,11),(17,18,13,8,12),
                (18,19,14,9,13),(19,15,10,5,14), (15,16,17,18,19))
        #triangualte
        faces=[]
        #wrong sense for some face
        for i,f in enumerate(ngonsfaces):
            #create three faces from one ngonsface
            if i in [1,2,3,4,5,len(ngonsfaces)-1]:#last one
                faces.append( [f[2],f[1],f[0]] )
                faces.append( [f[2],f[0],f[3]] )
                faces.append( [f[3],f[0],f[4]] )               
            else :
                faces.append( [f[0],f[1],f[2]] )
                faces.append( [f[3],f[0],f[2]] )
                faces.append( [f[4],f[0],f[3]] )
        return vertices,faces,None
        
    def Dodecahedron(self,name,radius):  
        """
        Create the mesh data and the mesh object of a Dodecahedron of a given radius
        
        @type  name: string
        @param name: name for the spline to update        
        @type  radius: float
        @param radius: radius of the embeding sphere
        
        @rtype:   Object, Mesh
        @return:  Dodecahedron Object and Mesh      
        """               
        v,f,n = self.dodecahedron(radius)
        ob,obme = self.createsNmesh(name,v,None,f)
        return ob,obme


    def icosahedron(self,radius):
        """
        Create the mesh data of a icosahedron of a given radius
        
        @type  radius: float
        @param radius: radius of the embeding sphere
        
        @rtype:   array
        @return:  vertex,face, face normal of the icosahedron        
        """    
        
        #from http://www.cs.umbc.edu/~squire/reference/polyhedra.shtml#dodecahedron
        vertices=[]#; /* 20 vertices with x, y, z coordinate */
        Pi = math.pi
        phiaa  = 26.56505; #/* the two phi angles needed for generation */
        
        r = radius; #/* any radius in which the polyhedron is inscribed */
        phia = Pi*phiaa/180.0; #/* 2 sets of four points */
        theb = Pi*36.0/180.0;  #/* offset second set 36 degrees */
        the72 = Pi*72.0/180;   #/* step 72 degrees */
        
        vertices.append([0.0,0.0,r])
        
        the = 0.0;
        for i in range(1,6):
            x=r*cos(the)*cos(phia);
            y=r*sin(the)*cos(phia);
            z=r*sin(phia);
            vertices.append([x,y,z])
            the = the+the72;
        
        the = theb;
        for i in range(6,11):#for(i=10; i<15; i++)
            x=r*cos(the)*cos(-phia);
            y=r*sin(the)*cos(-phia);
            z=r*sin(-phia);
            vertices.append([x,y,z])
            the = the+the72;  
        
        vertices.append([0.0,0.0,-r])
  
        #/* map vertices to 12 faces */
        #these are the ngons
        faces = [[ 0,  1,  2],
       [ 0,  2,  3],
       [ 0,  3,  4],
       [ 0,  4,  5],
       [ 0,  5,  1],
       [ 7,  6, 11],
       [ 8,  7, 11],
       [ 9,  8, 11],
       [10,  9, 11],
       [ 6, 10, 11],
       [ 6,  2,  1],
       [ 7,  3,  2],
       [ 8,  4,  3],
       [ 9,  5,  4],
       [10,  1,  5],
       [ 6,  7,  2],
       [ 7,  8,  3],
       [ 8,  9,  4],
       [ 9, 10,  5],
       [10,  6,  1]]

        return vertices,faces,None
        
    def Icosahedron(self,name,radius):   
        """
        Create the mesh data and the mesh object of a Icosahedron of a given radius
        
        @type  name: string
        @param name: name for the spline to update        
        @type  radius: float
        @param radius: radius of the embeding sphere
        
        @rtype:   Object, Mesh
        @return:  Icosahedron Object and Mesh      
        """     
        v,f,n = self.icosahedron(radius)
        ob,obme = self.createsNmesh(name,v,None,f)
        return ob,obme
        
    
    def progressBar(self,progress,label):
        """ update the progress bar status by progress value and label string
        @type  progress: Int/Float
        @param progress: the new progress
        @type  label: string
        @param label: the new message to put in the progress status
        """                
        pass

    def resetProgressBar(self,value):
        """reset the Progress Bar, using value"""
        pass

        
#===============================================================================
#     Texture Mapping / UV
#===============================================================================
    def getUVs(self):
        pass
        
    def setUVs(self):
        pass
        
    def getUV(self,object,faceIndex,vertexIndex,perVertice=True):
        pass
        
    def setUV(self,object,faceIndex,vertexIndex,uv,perVertice=True):
        pass

    
    
#===============================================================================
#     mesh
#===============================================================================
    
    def writeMeshToFile(self,filename,verts=None,faces=None,vnorms=[],fnorms=[]):
        file = open(filename+'.indpolvert', 'w')
        [(file.write("%f %f %f %f %f %f\n"%tuple(tuple(v)+tuple(n))))
             for v,n in zip(verts, vnorms) ] 
##        map( lambda v, n, f=file: \
##                 f.write("%f %f %f %f %f %f\n"%tuple(tuple(v)+tuple(n))),
##             verts, vnorms)
        file.close()

        file = open(filename+'.indpolface', 'w')
        for v, face in zip(fnorms, faces):
            [file.write("%d "%ind ) for ind in face]
            #map( lambda ind, f=file: f.write("%d "%ind ), face )
            file.write("%f %f %f\n"%tuple(v))
        file.close()        
    
    def readMeshFromFile(self,filename):
        filename = os.path.splitext(filename)[0]
        f = open(filename+'.indpolvert')
        lines = f.readlines()
        data = [l.split() for l in lines]
        f.close()
        
        verts = [(float(x[0]), float(x[1]), float(x[2])) for x in data]
        norms = [(float(x[3]), float(x[4]), float(x[5])) for x in data]
        
        f = open(filename+'.indpolface')
        lines = f.readlines()
        data = [l.split() for l in lines]
        f.close()

        faces = []
        fnorms = []
        for line in data:
            faces.append( list(map( int, line[:-3])) )
            fnorms.append( list(map( float, line[-3:])) )
        return verts,faces,norms

    def writeToFile(self,polygon,filename):
        """swriteToFile(filename)
        Creates a .vert and a face file describing this indexed polygons geoemtry.
        only vertices, and noramsl are saved the the .vert file (x y z nx ny nz)
        and 0-based topoly in the .face file (i, j, k, ... ).
        """
        print(polygon,self.getName(polygon))
        faces,vertices,vnormals,fnormals = self.DecomposeMesh(self.getMesh(polygon),
                                                edit=False,copy=False,tri=True,transform=True,fn=True)
        self.writeMeshToFile(filename,verts=vertices,faces=faces,
                             vnorms=vnormals,fnorms=fnormals)

    def findClosestPoint(self,point,object,transform=True):
        #python lookup for closest point,probably not the fastest way
        vertices = self.getMeshVertices(object)
        if transform :
            mat = self.getTransformation(object)
            vertices = self.ApplyMatrix(vertices,self.ToMat(mat))
        #bhtree?
        mini=9999.0
        for v in range(len(vertices)):
            d = self.measure_distance(vertices[v],point)
            if d < mini : 
                mini =d
        return mini

    def ToMat(self,mat):
        """
        Return a python (4,4) matrice array from a host matrice
    
        @type  mat: host matrice array
        @param mat: host matrice array 
        @rtype:   matrice
        @return:  the converted  matrice array
        """
        return mat
    
    def ToVec(self,v):
        """
        Return a python xyz array from a host xyz array/vector
    
        @type  v: host vector array
        @param v: host vector array 
        @rtype:   array
        @return:  the converted  vector array
        """
        return v
        
#===============================================================================
# Advanced Objects
#===============================================================================
    def createsNmesh(self,name,vertices,vnormals,faces,smooth=False,
                     material=None,proxyCol=False,color=[[1,0,0],],):
        """function that generate a Polygon object from the given vertices, face and normal.
        material or color can be passed and apply to the created polygon.
        Return the object and the mesh
        """
        pass
    
    def PointCloudObject(self,name,**kw):
        """
        This function create a special polygon which have only point.
        
        @type  name: string
        @param name: name of the pointCloud
        @type  kw: dictionary
        @param kw: dictionary of arg options, ie :
            'vertices' array of coordinates ;
            'faces'    int array of faces ;
            'parent'   hostAp parent object
    
        @rtype:   hostApp obj
        @return:  the polygon object
        """
        pass
        
        
    
    
    def addBone(self,i,armData,headCoord,tailCoord,
                roll=10,hR=0.5,tR=0.5,dDist=0.4,boneParent=None,
                name=None,editMode=True):
        """
        Add one bone to an armature.
        Optional function for creation of the armature
        
        @type  i: int
        @param i: indice for the new bone
        @type  armData: armature host data
        @param armData: the armature
        @type  headCoord: array xyz
        @param headCoord: coordinate of the head of the bone
        @type  tailCoord: array xyz
        @param tailCoord: coordinate of the tail of the bone
        @type  boneParent: bone
        @param boneParent: the parent for the created bone
    
        @rtype:   bone
        @return:  the created bone
        """        
        eb=None
        return eb
        
    def armature(self,name,coords,**kw):
        """
        Create an armature along the given coordinates
        
        @type  name: string
        @param name: name of the armature object
        @type  coords: list of array xyz
        @param coords: coordinate foreach bone   
        @rtype:   host Object,list of bone
        @return:  the created armature and the created bones      
        """                
        pass
        #return armObj,bones
    
    def oneMetaBall(self,metab,rad,coord):
        """
        Add one ball to a metaball object.
        Optional function for creation of the metaball
        
        @type  metab: metaball host data
        @param metab: the metaball
        @type  rad: float
        @param rad: radius for the new ball
        @type  coord: array xyz
        @param coord: coordinate of the ball
    
        @rtype:   ball/None
        @return:  the ball or None
        """        
        pass
        
    def metaballs(self,name,listePt,listeR,**kw):
        """
        Create a metaballs along the given coordinates
        
        @type  name: string
        @param name: name of the metaballs object
        @type  listePt: list of array xyz
        @param listePt: coordinate foreach bone  
        @type  listeR: list of float
        @param listeR: radius foreach ball 
        @rtype:   host Object,list of bone/metaball data
        @return:  the created metaballs,the created ball     
        """                
        pass

#===============================================================================
# Mesh Function
#===============================================================================

    def getMeshVertices(self,poly,selected=False):
        #return selected vertices of the given polygon in python format
        pass
        
    def getMeshNormales(self,poly,selected=False):
        #return selected normals of the given polygon in python format
        pass
        
    def getMeshEdge(self,hostedge):
        #return the host edge of the given polygon in python format
        pass
        
    def getMeshEdges(self,poly,selected=False):
        #return selected edges of the given polygon in python format
        pass
        
    def getFace(self,hostface,r=True):
        #return the host face of the given polygon in python format
        pass
            
    def getFaces(self,object,selected=False):
        #return selected faces of the given polygon in python format
        pass
        
    def getMeshFaces(self,poly,selected=False):
        #return selected faces of the given polygon in python format
        return self.getFaces(poly,selected=selected)

    def triangulate(self,poly):
        """
        Convert quad to triangle the selected face of the given polygon object
        @type  poly: hostObj
        @param poly: the object to triangulate
        """
        pass
        
    def IndexedPolgonsToTriPoints(self,geom,transform=True):
        verts = self.getMeshVertices(geom)
        tri = self.getMeshFaces(geom)
        assert tri.shape[1]==3
        if transform :
            mat = self.getTransformation(geom)
            verts = self.ApplyMatrix(verts,mat)
        triv = []
        for t in tri:
           triv.append( [verts[i].tolist() for i in t] )
        return triv
    
#===============================================================================
# Advanced Function
#===============================================================================
   
    
    def setRigidBody(self,*args,**kw):
        pass

    def pathDeform(self,*args,**kw):
        pass
    
    def updatePathDeform(self,*args,**kw):
        pass


#===============================================================================
# numpy dependant function
# we should have alternative from the host
#===============================================================================

    def vector_norm(self,data, axis=None, out=None):
        """Return length, i.e. eucledian norm, of ndarray along axis.
    
        >>> v = numpy.random.random(3)
        >>> n = vector_norm(v)
        >>> numpy.allclose(n, numpy.linalg.norm(v))
        True
        >>> v = numpy.random.rand(6, 5, 3)
        >>> n = vector_norm(v, axis=-1)
        >>> numpy.allclose(n, numpy.sqrt(numpy.sum(v*v, axis=2)))
        True
        >>> n = vector_norm(v, axis=1)
        >>> numpy.allclose(n, numpy.sqrt(numpy.sum(v*v, axis=1)))
        True
        >>> v = numpy.random.rand(5, 4, 3)
        >>> n = numpy.empty((5, 3), dtype=numpy.float64)
        >>> vector_norm(v, axis=1, out=n)
        >>> numpy.allclose(n, numpy.sqrt(numpy.sum(v*v, axis=1)))
        True
        >>> vector_norm([])
        0.0
        >>> vector_norm([1.0])
        1.0
    
        """
        data = numpy.array(data, dtype=numpy.float64, copy=True)
        if out is None:
            if data.ndim == 1:
                return math.sqrt(numpy.dot(data, data))
            data *= data
            out = numpy.atleast_1d(numpy.sum(data, axis=axis))
            numpy.sqrt(out, out)
            return out
        else:
            data *= data
            numpy.sum(data, axis=axis, out=out)
            numpy.sqrt(out, out)

    def unit_vector(self,data, axis=None, out=None):
        """Return ndarray normalized by length, i.e. eucledian norm, along axis.
    
        >>> v0 = numpy.random.random(3)
        >>> v1 = unit_vector(v0)
        >>> numpy.allclose(v1, v0 / numpy.linalg.norm(v0))
        True
        >>> v0 = numpy.random.rand(5, 4, 3)
        >>> v1 = unit_vector(v0, axis=-1)
        >>> v2 = v0 / numpy.expand_dims(numpy.sqrt(numpy.sum(v0*v0, axis=2)), 2)
        >>> numpy.allclose(v1, v2)
        True
        >>> v1 = unit_vector(v0, axis=1)
        >>> v2 = v0 / numpy.expand_dims(numpy.sqrt(numpy.sum(v0*v0, axis=1)), 1)
        >>> numpy.allclose(v1, v2)
        True
        >>> v1 = numpy.empty((5, 4, 3), dtype=numpy.float64)
        >>> unit_vector(v0, axis=1, out=v1)
        >>> numpy.allclose(v1, v2)
        True
        >>> list(unit_vector([]))
        []
        >>> list(unit_vector([1.0]))
        [1.0]
    
        """
        if out is None:
            data = numpy.array(data, dtype=numpy.float64, copy=True)
            if data.ndim == 1:
                data /= math.sqrt(numpy.dot(data, data))
                return data
        else:
            if out is not data:
                out[:] = numpy.array(data, copy=False)
            data = out
        length = numpy.atleast_1d(numpy.sum(data*data, axis))
        numpy.sqrt(length, length)
        if axis is not None:
            length = numpy.expand_dims(length, axis)
        data /= length
        if out is None:
            return data

    def getAngleAxis(self,vec1,vec2):
        angle = self.angle_between_vectors(vec1,vec2)
        cr = numpy.cross(vec1,vec2)
        axis = self.unit_vector(cr) 
        return angle,axis

    def rotation_matrix(self,angle, direction, point=None):
        """Return matrix to rotate about axis defined by point and direction.
    
        >>> R = rotation_matrix(math.pi/2.0, [0, 0, 1], [1, 0, 0])
        >>> numpy.allclose(numpy.dot(R, [0, 0, 0, 1]), [ 1., -1.,  0.,  1.])
        True
        >>> angle = (random.random() - 0.5) * (2*math.pi)
        >>> direc = numpy.random.random(3) - 0.5
        >>> point = numpy.random.random(3) - 0.5
        >>> R0 = rotation_matrix(angle, direc, point)
        >>> R1 = rotation_matrix(angle-2*math.pi, direc, point)
        >>> is_same_transform(R0, R1)
        True
        >>> R0 = rotation_matrix(angle, direc, point)
        >>> R1 = rotation_matrix(-angle, -direc, point)
        >>> is_same_transform(R0, R1)
        True
        >>> I = numpy.identity(4, numpy.float64)
        >>> numpy.allclose(I, rotation_matrix(math.pi*2, direc))
        True
        >>> numpy.allclose(2., numpy.trace(rotation_matrix(math.pi/2,
        ...                                                direc, point)))
        True
    
        """
        sina = math.sin(angle)
        cosa = math.cos(angle)
        direction = self.unit_vector(direction[:3])
        # rotation matrix around unit vector
        R = numpy.array(((cosa, 0.0,  0.0),
                         (0.0,  cosa, 0.0),
                         (0.0,  0.0,  cosa)), dtype=numpy.float64)
        R += numpy.outer(direction, direction) * (1.0 - cosa)
        direction *= sina
        R += numpy.array((( 0.0,         -direction[2],  direction[1]),
                          ( direction[2], 0.0,          -direction[0]),
                          (-direction[1], direction[0],  0.0)),
                         dtype=numpy.float64)
        M = numpy.identity(4)
        M[:3, :3] = R
        if point is not None:
            # rotation not around origin
            point = numpy.array(point[:3], dtype=numpy.float64, copy=False)
            M[:3, 3] = point - numpy.dot(R, point)
        return M

    def rotate_about_axis(self,B,theta,axis=2):
        #from http://480.sagenb.org/home/pub/20/ 
        # Create the rotation matrix. Rotation about the x-axis corresponds 
        #to axis==0, y-axis to axis==1 and 
        # z-axis to axis==2 
        M = numpy.array([]) 
        if axis==0: 
            M = numpy.array([[1,0,0],[0,cos(theta),-sin(theta)],[0,sin(theta),cos(theta)]],dtype='float128') 
        elif axis==1: 
            M = numpy.array([[cos(theta),0,-sin(theta)],[0,1,0],[sin(theta),0,cos(theta)]],dtype='float128') 
        elif axis==2: 
            M = numpy.array([[cos(theta),-sin(theta),0],[sin(theta),cos(theta),0],[0,0,1]],dtype='float128') 
        # Numpy makes large floating point matrix manipulations easy 
        return numpy.dot(M,B)

    def angle_between_vectors(self,v0, v1, directed=True, axis=0):
        """Return angle between vectors.
    
        If directed is False, the input vectors are interpreted as undirected axes,
        i.e. the maximum angle is pi/2.
    
        >>> a = angle_between_vectors([1, -2, 3], [-1, 2, -3])
        >>> numpy.allclose(a, math.pi)
        True
        >>> a = angle_between_vectors([1, -2, 3], [-1, 2, -3], directed=False)
        >>> numpy.allclose(a, 0)
        True
        >>> v0 = [[2, 0, 0, 2], [0, 2, 0, 2], [0, 0, 2, 2]]
        >>> v1 = [[3], [0], [0]]
        >>> a = angle_between_vectors(v0, v1)
        >>> numpy.allclose(a, [0., 1.5708, 1.5708, 0.95532])
        True
        >>> v0 = [[2, 0, 0], [2, 0, 0], [0, 2, 0], [2, 0, 0]]
        >>> v1 = [[0, 3, 0], [0, 0, 3], [0, 0, 3], [3, 3, 3]]
        >>> a = angle_between_vectors(v0, v1, axis=1)
        >>> numpy.allclose(a, [1.5708, 1.5708, 1.5708, 0.95532])
        True
    
        """
        v0 = numpy.array(v0, dtype=numpy.float64, copy=False)
        v1 = numpy.array(v1, dtype=numpy.float64, copy=False)
        dot = numpy.sum(v0 * v1, axis=axis)
        dot /= self.vector_norm(v0, axis=axis) * self.vector_norm(v1, axis=axis)
        return numpy.arccos(dot if directed else numpy.fabs(dot))

    def ApplyMatrix(self,coords,mat):
        """
        Apply the 4x4 transformation matrix to the given list of 3d points
    
        @type  coords: array
        @param coords: the list of point to transform.
        @type  mat: 4x4array
        @param mat: the matrix to apply to the 3d points
    
        @rtype:   array
        @return:  the transformed list of 3d points
        """
    
        #4x4matrix"
        mat = numpy.array(mat)
        coords = numpy.array(coords)
        one = numpy.ones( (coords.shape[0], 1), coords.dtype.char )
        c = numpy.concatenate( (coords, one), 1 )
        return numpy.dot(c, numpy.transpose(mat))[:, :3]


    def Decompose4x4(self,matrix):
        """
        Takes a matrix in shape (16,) in OpenGL form (sequential values go
        down columns) and decomposes it into its rotation (shape (16,)),
        translation (shape (3,)), and scale (shape (3,))
    
        @type  matrix: 4x4array
        @param matrix: the matrix to decompose
    
        @rtype:   list of array
        @return:  the decomposition of the matrix ie : rotation,translation,scale
        """
        m = matrix
        transl = numpy.array((m[12], m[13], m[14]), 'f')
        scale0 = numpy.sqrt(m[0]*m[0]+m[4]*m[4]+m[8]*m[8])
        scale1 = numpy.sqrt(m[1]*m[1]+m[5]*m[5]+m[9]*m[9])
        scale2 = numpy.sqrt(m[2]*m[2]+m[6]*m[6]+m[10]*m[10])
        scale = numpy.array((scale0,scale1,scale2)).astype('f')
        mat = numpy.reshape(m, (4,4))
        rot = numpy.identity(4).astype('f')
        rot[:3,:3] = mat[:3,:3].astype('f')
        rot[:,0] = (rot[:,0]/scale0).astype('f')
        rot[:,1] = (rot[:,1]/scale1).astype('f')
        rot[:,2] = (rot[:,2]/scale2).astype('f')
        rot.shape = (16,)
        #rot1 = rot.astype('f')
        return rot, transl, scale
        
    def getTubePropertiesMatrix(self,coord1,coord2):
        #need ot overwrite in C4D
        #print coord1,coord1[0],type(coord1[0])
        x1 = float(coord1[0])
        y1 = float(coord1[1])
        z1 = float(coord1[2])
        x2 = float(coord2[0])
        y2 = float(coord2[1])
        z2 = float(coord2[2])
#        length = math.sqrt((x1-x2)*(x1-x2)+(y1-y2)*(y1-y2)+(z1-z2)*(z1-z2))
#        wsz = atan2((y1-y2), (z1-z2))
#        wz = acos((x1-x2)/laenge)
#        offset=numpy.array([float(x1+x2)/2,float(y1+y2)/2,float(z1+z2)/2])
#        v_2=numpy.array([float(x1-x2),float(y1-y2),float(z1-z2)])
#        v_2 = numpy.array(self.normalize(v_2))
#        v_1=numpy.array([float(0.),float(1.),float(2.)])
#        v_3=numpy.cross(v_1,v_2)
#        v_3 = numpy.array(self.normalize(v_3))
#        v_1=numpy.cross(v_2,v_3)
#        v_1 = numpy.array(self.normalize(v_1))
#        M=numpy.identity(4)
#        M[0,:3] = v_1
#        M[1,:3] = v_2
#        M[2,:3] = v_3
#        M[3,:3] = offset
#        m = numpy.identity(4)
#        m[:3,:3] = M[:3,:3]
#        row_max = m.max(axis=1).reshape((-1, 1))
#        m = numpy.absolute((m / row_max))
#        M[:3,:3] = m[:3,:3]
        v,length = self.measure_distance(coord2,coord1,vec=True)
        vx,vy,vz = v
        offset=numpy.array([float(x1+x2)/2,float(y1+y2)/2,float(z1+z2)/2])      
        v_2 = self.unit_vector(v,axis=1)
        v_1 = numpy.array([float(0.),float(1.),float(2.)])
        v_3 = numpy.cross(v_1,v_2)
        v_3 = self.unit_vector(v_3,axis=1)
        v_1 = numpy.cross(v_2,v_3)
        v_1 = self.unit_vector(v_1,axis=1)
        M=numpy.identity(4)
        M[0,:3] = v_1
        M[1,:3] = v_2
        M[2,:3] = v_3
        M[3,:3] = offset        
#        sx = 1
#        nx = 0
#        ny = 1
#        #this is probably dependant on the princpal axis of the cylinder
#        if (vx != 0 or vy != 0):
#            alpha = (1. - vz) / (vx*vx + vy*vy)
#            sx = -vy*vy*alpha - vz
#            nx = alpha*vx*vy
#            ny = -vx*vx*alpha - vz
#        M = [[sx, nx, vx,offset[0]],
#            [nx, ny, vy,offset[1]],
#            [vx, vy, vz,offset[2]],
#            [0.,0.,0.,1.],]
        return length,numpy.array(M).transpose()     
     
     
    def getCenter(self,coords):
        """
        Get the center from a 3d array of coordinate x,y,z.
    
        @type  coords: liste/array
        @param coords: the coordinates
    
        @rtype:   list/array
        @return:  the center of mass of the coordinates
        """
#        if len(coords) == 3 :
#            if type(coords[0]) is int or type(coords[0]) is float :
#                coords = [coords,]      
        coords = numpy.array(coords)#self.allAtoms.coords
        center = sum(coords)/(len(coords)*1.0)
        center = list(center)
        for i in range(3):
            center[i] = round(center[i], 4)
#        print "center =", center
        return center

#===============================================================================
# depends on PIL    
#===============================================================================
    
    def makeTexture(self,object,filename=None,img=None,colors=None,sizex=0,sizey=0,
                    s=20,draw=True,faces=None,invert=False):
        invert = False
        if img is None and draw:
            if not self._usePIL :
                return None            
            img = Image.new("RGB", (int(sizex), int(sizey)),(0, 0, 0))
        elif not draw and usenumpy :
            img = numpy.zeros((int(sizex), int(sizey),3))
            #ramp = numpy.ones( (size, n), 'd')
        if draw and self._usePIL:
            import ImageDraw
            imdraw = ImageDraw.Draw(img)
        #object handling
        if faces is None :
            faces = self.getFaces(object)
        order = [2,1,0]
        if self.host != 'c4d':
            invert = True
            order = [0,1,2]
        x=0
        y=0
        s=s
        uvindex=0
        self.resetProgressBar(0)
        for i,f in enumerate(faces) :
            xys = [(x,y),(x+s,y+s),(x+s,y)]
            box= [(x,y),(x+s,y+s)]
            c1=numpy.array(self.convertColor(colors[f[order[0]]]))
            c2=numpy.array(self.convertColor(colors[f[order[1]]]))
            c3=numpy.array(self.convertColor(colors[f[order[2]]]))
            if draw :
                self.drawGradientLine(imdraw,c1,c2,c3,xys)
                #self.drawPtCol(imdraw,numpy.array([c1,c2,c3]),xys,debug=0)
            else :
                if usenumpy :
                    img=self.fillTriangleColor(img,c1,c2,c3,xys)
            if invert :
                uv=[[(x+2)/sizex,1-((y+2)/sizey),0], 
                    [(x+s-2)/sizex,1-((y+s-2)/sizey),0], 
                    [(x+s-2)/sizex,1-((y+2)/sizey),0],
                    [(x+s-2)/sizex,1-((y+2)/sizey),0]]                
            else :
                uv=[[(x+2)/sizex,(y+2)/sizey,0], 
                    [(x+s-2)/sizex,(y+s-2)/sizey,0], 
                    [(x+s-2)/sizex,(y+2)/sizey,0],
                    [(x+s-2)/sizex,(y+2)/sizey,0]]
            uvindex=self.setUV(object,i,0, uv,perVertice=False,uvid=uvindex)#perFaces give 3-4 uv
            self.progressBar(i/len(faces),"faces "+str(i)+"/"+str(len(faces))+" done")
            x = x + s
            if x >=sizex or x +s >=sizex:
                x = 0
                y = y + s
        if draw :
            img.save(filename)
        else :
            #what to do with the array - > build image using host or PIL
            #n=int(len(img)/(sizex*sizey))
            #img=img.reshape(sizex,sizey,n)
            mode = "RGB"
            #else : mode = "RGBA"
            print(mode)
            import Image
            pilImage = Image.fromstring(mode,img.shape[0:2],img.tostring())
            #img=numpy.array(img)
            #pilImage = Image.fromarray(img, mode)
            pilImage.save(filename)
        self.resetProgressBar(0)
        return img
        
    def makeTextureM(self,object,filename=None,img=None,colors=None,sizex=0,sizey=0,
                    s=20,draw=True,faces=None,
                    invert=False):
        if img is None and draw and self._usePIL:
            import Image
            img = Image.new("RGB", (int(sizex), int(sizey)),(0, 0, 0))
        elif not draw and usenumpy :
            img = numpy.zeros((int(sizex), int(sizey),3))
        if draw and self._usePIL:
            import ImageDraw
            imdraw = ImageDraw.Draw(img)
        else :
            return None
        #object handling
        if faces==None:
            faces = self.getFaces(object)
        x=0
        y=0
        s=s
        self.resetProgressBar(0)
        uv={}
        for i,f in enumerate(faces) :
            xys = [(x,y),(x+s,y+s),(x+s,y)]
            box= [(x,y),(x+s,y+s)]
            c1=numpy.array(self.convertColor(colors[f[0]]))
            c2=numpy.array(self.convertColor(colors[f[1]]))
            c3=numpy.array(self.convertColor(colors[f[2]]))
            if draw :
                self.drawGradientLine(imdraw,c1,c2,c3,xys)
                #self.drawPtCol(imdraw,numpy.array([c1,c2,c3]),xys,debug=0)
            if invert :
                uv[i]=[[(x+2)/sizex,1-((y+2)/sizey),0], 
                    [(x+s-2)/sizex,1-((y+s-2)/sizey),0], 
                    [(x+s-2)/sizex,1-((y+2)/sizey),0],
                    [(x+s-2)/sizex,1-((y+2)/sizey),0]]                
            else :
                uv[i]=[[(x+2)/sizex,(y+2)/sizey,0], 
                    [(x+s-2)/sizex,(y+s-2)/sizey,0], 
                    [(x+s-2)/sizex,(y+2)/sizey,0],
                    [(x+s-2)/sizex,(y+2)/sizey,0]]
            self.progressBar(i/len(faces)," draw faces "+str(i)+" done")
            x = x + s
            if x >=sizex or x +s >=sizex:
                x = 0
                y = y + s
        self.setUVs(object,uv)
        img.save(filename)
        self.resetProgressBar(0)
        
    def makeTextureFromUVs(self,object,filename=None,img=None,colors=None,
                    sizex=0,sizey=0,
                    s=20,draw=True,
                    invert=False):
        if not self._usePIL :
            return None
        if img is None and draw:
            import Image
            img = Image.new("RGB", (int(sizex), int(sizey)),(0, 0, 0))
        elif not draw and usenumpy :
            img = numpy.zeros((int(sizex), int(sizey),3))
        if draw :
            import ImageDraw
            imdraw = ImageDraw.Draw(img)
        uvs=[]
        if self.host == 'maya':
            invert = True        
        faces = self.getFaces(object)
        self.resetProgressBar(0)
        for faceindex,f in enumerate(faces) :
            uv=self.getUV(object,faceindex,0,perVertice=False)
#            print "uv ",faceindex,uv,f
            uvs=[]
            color = []
            for i in range( len(f) ): # 3 vertex
                #print "vi",itPoly.vertexIndex(i)
                vertexindex = f[i]
                color.append(self.convertColor(colors[vertexindex]))
                if invert :
                    uvs.append( [uv[i][0]*sizex, (1-(uv[i][1]))*sizex] )#order?
                else :
                    uvs.append( [uv[i][0]*sizex, uv[i][1]*sizex] )#order?
            self.drawPtCol(imdraw,numpy.array(color),numpy.array(uvs),debug=0)
            self.progressBar((float(faceindex)/len(faces)),"faces "+str(faceindex)+" done")
        img.save(filename)
        self.resetProgressBar(0)     

    def fillTriangleColor(self,array,col1,col2,col3,xys):
        for i in range(20):
            a=i/20.
            for j in range(20):
                b = j/20.
                xy = (xys[0][0]+j,xys[0][1]+i)
                xcol = col1+b*(col3-col1)
                ycol = xcol+a*(col2-xcol)
                array[xys[0][0]+j][xys[0][1]+i][:] = [ycol[0],ycol[1],ycol[2]]
                #imdraw.point((xys[0][0]+j,xys[0][1]+i),fill=(ycol[0],ycol[1],ycol[2]))
        return array
        
    def drawGradientLine(self,imdraw,col1,col2,col3,xys):
        if not self._usePIL :
            return None
        if col1 is col2 and col2 is col3 :
            imdraw.rectangle([xys[0],xys[1]], fill=(col1[0], col1[1], col1[2]))
        else:
            for i in range(20):
                a=i/20.
                for j in range(20):
                    b = j/20.
                    xy = (xys[0][0]+j,xys[0][1]+i)
                    xcol = col1+b*(col3-col1)
                    ycol = xcol+a*(col2-xcol)
                    imdraw.point((xys[0][0]+j,xys[0][1]+i),fill=(ycol[0],ycol[1],ycol[2]))
    

    def drawPtCol(self,imdraw,color,uv,debug=0):
        #uv is the 3 vertex coordinate in UV 
        if not self._usenumpy :
            return
        if debug :
            print(uv)
#        uv=extendUV(uv)
        uv = numpy.array(uv)
        u=uv[0][0]
        v=uv[0][1]
        a=[0,0,0]
        #color = [c0,c1,c2] 
        distu = [[0.,0,0],[0,0.,0],[-0,-0,0.]]
        distv = [[0.,0,0],[0,0.,0],[-0,-0,0.]]
        for i in range(3):#points
            for j in range(3):
#                print i,j
                distu[i][j] = (uv[i][0] - uv[j][0])
                distv[i][j] = (uv[i][1] - uv[j][1])
        order=[0,1,2]
    #    print distu
    #    print distv
        order = self.getOrder(distu,uv)
    #    orderv = getOrder(distv,uv=uv)
        ab=[]
        ab.append(self.getA(uv[order[0]],uv[order[1]]))
        ab.append(self.getA(uv[order[1]],uv[order[2]]))
        ab.append(self.getA(uv[order[0]],uv[order[2]]))
        uv = numpy.array(uv,int)
        u = uv[order[0]][0] 
        v = uv[order[0]][1]
        up = False
        if distv[order[0]][order[1]] <= 0 :
            up = True#second pt up
        if debug :
            print(up,distv[order[0]][order[1]])
        #distu=numpy.array(distu,int)
        #distv=numpy.array(distv,int)
        rgu = list(range(u,uv[order[2]][0]))
        if u-1 == -1 :
            rgu = rgu[1:]
        if debug :
            print(rgu)    
            print("1x ",uv[order[1]][1],v)
            print("1x ",uv[order[2]][1],v) 
        maxv = uv[order[1]][1]
        if uv[order[1]][1] == v:
           d = distv[order[0]][order[2]]
           maxv = uv[order[2]][1]
        else :
            d=distv[order[0]][order[1]]
        if d < 0. :
            d = d *-1
        rgv = list(range(d))
        if debug :
            print(maxv,rgv)
        if len(rgv) == 0 :
            rgv = [0,1]
        ycol = color[order[0]]            
        if debug :
            print("draw first point",order,u,v,len(rgu),len(rgv))#
        #imdraw.point((u,v),fill=(ycol[0],ycol[1],ycol[2]))
    #    print "line eq",ab,order,orderv
        indice1 = 0 #more on right
        indice2 = 2 #midlle which can be up/down compare to 1
        x=0.
        if debug:
            print(order)
            print(uv)
            print(color[order[0]],color[order[1]],color[order[2]])
            print(ab)
        ca=0.
        for gg in rgu:
            #range of v
            if debug:
                print("eq ",u , ab[indice1],u * ab[indice1][0]+ab[indice1][1],ab[indice2],u * ab[indice2][0] + ab[indice2][1])
            #y = ax+b
            va = int(u * ab[indice1][0] + ab[indice1][1])
            if ab[indice1][0] == 0. and u == uv[order[0]][0] :
                vb = uv[order[1]][1]# - distv[order[0]][order[1]]     
            else :
                vb = int(u * ab[indice2][0] + ab[indice2][1])
            #if up :
            rg = list(range(va,vb))
            #else :
            #    rg = range(vb,va+1)
            if len(rg) == 0 :
                rg = list(range(vb,va))
            n = len(rg)        
            if debug:
                print("range V ",u,va,vb,rg)
            xcola = x/len(rgu) #* ab[2][0] + ab[2][1] #
            if debug :
                print("xcola",xcola, x,len(rgu),ca/len(rgu))
            
            y=0.
            for cb,v in enumerate(rg):
                k = float(maxv)-float(v)
                if k < 0 :
                    k = k*-1.
                ycola = k/float(len(rgv))#(x/len(rgu) * ab[indice1][0] + ab[indice1][1])/len(rgv) #
                if debug :
                    print("ycola",y,len(rgv),y/len(rgv),ycola)
                if (color[order[2]]-color[order[0]]).sum() == 0.: 
                    #if up:
                    xcol = color[order[0]]
                    #else :
                    #    xcol = color[order[2]]
                else :
                    #if up:
                    #    xcol = color[order[2]]+x/len(rgu)*(color[order[0]]-color[order[2]])
                    #else :
                    xcol = color[order[0]]+xcola*(color[order[2]]-color[order[0]])
                if (color[order[1]]-color[order[0]]).sum() == 0.:
                    ycol = xcol
                else :
                    #if up :
                    ycol = xcol+(1-ycola)*(color[order[1]]-xcol)
                    #else :
                    #ycol = color[order[1]]+y/n*(xcol-color[order[1]])
                if debug :
                    print(v,xcol,ycol)
                imdraw.point((u,v),fill=(ycol[0],ycol[1],ycol[2]))
                y = y + 1.
            if u == uv[order[1]][0]:
                if debug :
                    print("end",u,uv[order[1]][0])
    #            if y == uv[order[1]][1] :
    #                print "change line eq",y , uv[order[1]][1],indice1,indice2
                indice1 = 1
    #                if order[0] == orderv[0] :
    #                    indice1 = orderv[0]
                indice2 = 2
    
    #                print indice1,indice2
            u = u + 1  
            x =x +1.
            
    def getOrder(self,distu,uv):
        if not self._usenumpy :
            return        
        order = [0,1,2]
        u,v = uv.transpose()
        imaxu = numpy.nonzero(u == u.max() )[0]#[0]
        imaxv = numpy.nonzero(v == v.max() )[0]#[0]
        iminu = numpy.nonzero(u == u.min() )[0]#[0]
        iminv = numpy.nonzero(v == v.min() )[0]#[0]
        #order0 should be left/top
        if len(iminu) == 1 : #
            order[0] = iminu[0]
        else :
            #different max,top one is the one with v mini
            min=[9999,0]
            for ind in iminu:
                if v[ind] < min[0] :
                    min=[v[ind],ind]
            order[0] = min[1]
        #order1
        #closest u from order[0]
        #print distu[order[0]]
        min = [9999,0]
        ds=[]
        for i,d in enumerate(distu[order[0]]):
            if i != order[0] :
                ds.append(d)
                if -d < min[0] :  
                    min = [-d,i]
        if ds[0] == ds[1]:
            min=[9999,0]
            for ind,val in enumerate(v):
                if ind != order[0] :
                    print(ind,val)
                    if val < min[0] :
                        min=[val,ind]
        order[1] = min[1]
        #order2
        if len(imaxu) == 1 :
            order[2] = imaxu[0]
        else :
            min=[9999,0]
            for ind in imaxu:
                if v[ind] < min[0] and ind !=  order[1]:
                    min=[v[ind],ind]
            order[2] = min[1]
        #print order
        return order

    def getA(self,pt1,pt2):
        if pt2[0]-pt1[0] == 0. :
            a=0.
        else :
            a=(pt2[1]-pt1[1])/(pt2[0]-pt1[0])
        #solve y = ax+b
        #b = y - ax
        b=pt1[1]-a*pt1[0]
        return (a,b)

    
    
    #DejaVu.indexedPolygon have also this function
