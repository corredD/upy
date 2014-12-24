# -*- coding: utf-8 -*-
"""
Created on Sun Dec  5 23:30:44 2010

@author: Ludovic Autin - ludovic.autin@gmail.com
"""
import sys
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

if sys.version_info >= (3,0,0):
    unicode = str
    
def vdistance(c0,c1):
    """get the distance between two points c0 and c1"""
    d = numpy.array(c1) - numpy.array(c0)
    s = numpy.sum(d*d)
    return math.sqrt(s)
def vdiff(p1, p2):
    # returns p1 - p2
    x1,y1,z1 = p1
    x2,y2,z2 = p2
    return (x1-x2, y1-y2, z1-z2)

def vcross(v1,v2):
    x1,y1,z1 = v1
    x2,y2,z2 = v2
    return (y1*z2-y2*z1, z1*x2-z2*x1, x1*y2-x2*y1)

def dot(v1,v2):
    x1,y1,z1 = v1
    x2,y2,z2 = v2
    return ( x1 * x2 ) + ( y1 * y2 ) +  ( z1 * z2 )
    
from math import sqrt
def vnorm(v1):
    x1,y1,z1 = v1
    n1 = 1./sqrt(x1*x1 + y1*y1 + z1*z1)
    return (x1*n1, y1*n1, z1*n1)


def vlen(v1):
    x1,y1,z1 = v1
    return sqrt(x1*x1 + y1*y1 + z1*z1)
    
class Helper:
    """
    The Helper abstract Object
    ==========================
    This is the main class from which all helper derived. The Helper 
    give access to the basic function need for create and edit object 
    in the host.
    
    Most of the function define at this loevel are overwrite by the class child.
    matrix and transformation came from  http://www.lfd.uci.edu/~gohlke/code/transformations.py.html
    
    >>> import upy
    >>> hClass = upy.getHelperClass()
    >>> helper = helper.hClass()
    
    See examples in upy/examples

    """
    _usenumpy = usenumpy
    _MGLTools = False
    _usePIL = usePIL
    BONES = None
    IK = None
    
    CAM_OPTIONS = {"ortho" :"ortho","persp" : "persp" }#define the type of camera
    LIGHT_OPTIONS = {"Area":"AREA","Sun":"SUN","Spot":"SPOT"}#define the type of light


    dupliVert = False
    
    def __init__(self,):
        try :
            import DejaVu
            _MGLTools = True
        except :
            _MGLTools = False
#        self.createColorsMat()
        self.noise_type ={
              "boxNoise":None,
              "buya":None,
              "cellNoise":None,
              "cellVoronoi":None,
              "cranal":None,
              "dents":None,
              "displacedTurbulence":None,
              "electrico":None,
              "fbm":None,
              "fire":None,
              "gas":None,
              "hama":None,
              "luka":None,
              "modNoie":None,
              "naki":None,
              "noise":None,
              "none":None,
              "nutous":None,
              "ober":None,
              "pezo":None,
              "poxo":None,
              "sema":None,
              "sparseConvolution":None,
              "stupl":None,
              "turbulence":None,
              "vlNoise":None,
              "voronoi1":None,
              "voronoi2":None,
              "voronoi3":None,
              "wavyTurbulence":None,
              "zada":None,       
             }
        self.usenumpy = self._usenumpy
        self.nogui = False
        self.instance_dupliFace = False
        self.quad={"+Z" :[[-1,1,0],[1,1,0],[1,-1,0], [-1,-1,0]],#XY
                   "+Y" :[[-1,0,1],[1,0,1],[1,0,-1], [-1,0,-1]],#XZ
                   "+X" :[[0,-1,1],[0,1,1],[0,1,-1], [0,-1,-1]],#YZ
                   "-Z" :[[-1,1,0],[1,1,0],[1,-1,0], [-1,-1,0]],#XY
                   "-Y" :[[-1,0,1],[1,0,1],[1,0,-1], [-1,0,-1]],#XZ
                   "-X" :[[0,-1,1],[0,1,1],[0,1,-1], [0,-1,-1]],#YZ
                   }
#==============================================================================
# some helper for treading and asynchrone stuff
#==============================================================================
    def testForEscape(self,):
        """    
        return True if ESC is press
        """
        return False
        
#==============================================================================
# mathutils
#==============================================================================

    def norm(self,a ,b,c):
        """    
        return the norm of the vector [a,b,c]  
           
        >>> result = helper.norm(a,b,c) #a,b,c being double
        
        @type a: float
        @param a:  first value of the vector
        @type b: float
        @param b:  second value of the vector
        @type c: float
        @param c:  thid value of the vector
     
        @rtype: float
        @return: the norm of the vector
         
        """
        return (math.sqrt( a*a + b*b + c*c))

    def normalize(self,A):
        """    
        return the normalized vector A [x,y,z] 
           
        >>> a = [1.0,3.0,5.0]
        >>> a_normalized = helper.normalize(a) 
        
        @type A: vector
        @param A:  the 3d vector
        @rtype: vector
        @return: the normalized 3d vecor
        """
        norm = self.norm(A[0],A[1],A[2])
        if (norm ==0.0) : return A
        else :return [A[0]/norm,A[1]/norm,A[2]/norm]
        
    def measure_distance(self,c0,c1,vec=False):
        """ measure distance between 2 point specify by x,y,z
        c0,c1 should be Numeric.array
        
        >>> a = [1.0,3.0,5.0]
        >>> b = [5.0,1.0,2.0]
        >>> distance = helper.measure_distance(a,b) 
        >>> distance, vector_a_to_b = helper.measure_distance(a,b)
        
        @type c0: vector
        @param c0:  the first 3d vector
        @type c1: vector
        @param c1:  the second 3d vector        
        @type vec: Boolean
        @param vec:  if the function return the vector c1-c0          
        @rtype: float ? vector
        @return: the distance, and optionly the distance vetor
        """
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

    #direction, angle authorized
    def advance_randpoint_onsphere(self,radius,marge=pi,vector=None):
        #radius r, inclination θ, azimuth φ 
        r=radius
        azimuth=random.uniform(-1,1) * ( marge * 2.0 )
        inclination=random.uniform(-1,1) * ( marge )     
        x=r*sin(inclination)*cos(azimuth)
        y=r*sin(inclination)*sin(azimuth)
        z=r*cos(inclination)
        pos = [x,y,z]
        if vector is not None :
            absolute_vector=numpy.array([0,0,radius])
            matrice = self.rotVectToVect(absolute_vector,vector)
            pos = self.ApplyMatrix([pos,],matrice)[0]
        return pos
        
    def randpoint_onsphere(self,radius,biased=None):
        """ 
        Generate a random point on the outside of a sphere.
        
        >>> r = 2.0
        >>> bias = 2.0
        >>> point = helper.randpoint_onsphere(r) 
        >>> point2 = helper.randpoint_onsphere(r,bias)
        
        @type radius: float
        @param radius:  the radius of the sphere
        @type biased: float
        @param biased:  optional float vale to use instead of the random function      
        
        @rtype: vector
        @return: a random 3d point on the sphere of the given radius  
        
        -points (x,y,z) so that (x-a)^2 +(y-b)^2 + (z-c)^2 = R^2
        
        -To generate a random point on the sphere, it is necessary only 
        to generate two random numbers, z between -R and R, phi between 
        0 and 2 pi, each with a uniform distribution.
        
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

        """
        if biased is not None:
            theta = biased * ( 2 * pi )
            u = biased * 2 - 1 #represent sin(phi)
        else :
            theta = random.uniform(0.,1.0)* ( 2 * pi )
            u = random.uniform(0.,1.0) * 2 - 1
#        print ("u ",u," theta ",theta)
#        print ("radius ",radius)
#        print ("sqrt ",( 1 - u**2)," sqrt ",sqrt(  1 - u**2))
#        print ("cos ",cos(theta))
        x = radius * sqrt(  1 - u**2) * cos(theta)
        y = radius * sqrt(  1 - u**2) * sin(theta)
        z = radius * u
        return [x,y,z]


    def transposeMatrix(self,matrice):
        if matrice is not None :
            matrice = numpy.array(matrice)
            if isinstance(matrice,numpy.ndarray) :
                mat = matrice.transpose().tolist()
                return mat
            else :
                return matrice#  = mat#numpy.array(matrice)
#            blender_mat=mathutils.Matrix(mat)#from Blender.Mathutils
#            blender_mat.transpose()        
#            return blender_mat
        return matrice

    def rotatePoint(self,pt,m,ax):
        """ 
        Rotate the point pt [x,y,z] around axe ax[0],ax[1],ax[2] by ax[3] radians,
        and translate by m [x,y,z].
        
        >>> point = [1.0,2.0,0.0]
        >>> trans = [5.0,0.0,0.0]
        >>> axes = [1.0,0.0,0.0,math.pi]
        >>> point = helper.rotatePoint(point,trans,axes) 
        >>> print point
        [6.0, -2.0, 2.4492935982947064e-16] #[6.0, -2.0, 0.0]
        
        @type pt: 3d vector
        @param pt:  the 3d point to be rotated
        @type m: 3d vector
        @param m:  translation to apply after rotation      
        @type ax: 4d vector
        @param ax:  axe of rotation ax[0],ax[1],ax[2] and angle ax[3] radians      
        
        @rtype: 3d vector
        @return: the transformed point  
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
        Code from 'http://www.euclideanspace.com/maths/geometry/rotations/conversions/'.
        
        This conversion uses NASA standard aeroplane conventions as described on page:
        'http://www.euclideanspace.com/maths/geometry/rotations/euler/index.htm'
    
        Coordinate System: right hand
    
        Positive angle: right hand
    
        Order of euler angles: heading first, then attitude, then bank
    
        matrix row column ordering:
    
        [m00 m01 m02]
    
        [m10 m11 m12]
    
        [m20 m21 m22]

        >>> euler = [0.8,3.14,2.0]#radians
        >>> emat = helper.eulerToMatrix(euler)
        >>> print emat
        [[-0.69670582573323303, 0.65275180908484898, -0.29751650059422086, 0.0], 
         [0.0015926529164868282, 0.41614630875957009, 0.90929627358879683, 0.0], 
         [0.71735518109654839, 0.6330381706044601, -0.29097116474265428, 0.0], 
         [0.0, 0.0, 0.0, 1.0]]
 
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
        From two point return the length, and the orientation from one to another.
        This function is used to build a cylinder from two points (see oneCylinder function)

        >>> coord1 = [1.0,0.0,0.0]
        >>> coord2 = [2.0,0.0,0.0]
        >>> distance,rsz,rz,coord = helper.getTubeProperties(coord1,coord2)
        >>> helper.setTransformation(obj,trans=coord,scale=[1., 1., distance],
                               rot=[0.,rz,rsz])
        
        @type  coord1: vector
        @param coord1: first point
        @type  coord2: vector
        @param coord2: second point
    
        @rtype:   tupple
        @return:  length, orientation (rotation XY,Z), and intermediate point OR 
         length and matrix of transformation (see getTubePropertiesMatrix that use numpy)
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
        
        * overwrited by children class for each host
        """
        pass
    
    def fit_view3D(self):
        """
        Function that should recenter the viewport to the object in the scene.
        
        * overwrited by children class for each host
        """
        pass

    def checkName(self,name):
        """
        Check the provide name to avoid invalid caracter for the 
        host. ie maya didnt support object name starting with number, and automatically rename the object. 
        In order to retrieve the object use this functon. If a invalid 
        caracter is found, the caracter is removed.
        This function can be change in the features, as it currently only look for number.
        
        
        >>> name = "1sphere"   
        >>> sphere_obj,sphere_mesh = helper.Sphere(name) 
        >>> print (sphere_obj,sphere_mesh)#in maya
        (u'sphere', u'makeNurbSphere1')
        >>> corrected_name  = helper.checkName(name)
        >>> print (corrected_name)
        sphere
        >>> sphere = helper.getObject(name) 
        >>> print (sphere)
        sphere
        
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
        Retrieve an object from his name. 
        
        * overwrited by children class for each host

        >>> oname = "mysphere"
        >>> object= helper.getObject(oname)
        >>> print oname,object#the result depnds on the host
        mysphere <c4d.BaseObject object at 0x1e4fc4b0> # Cinema4D
        mysphere    # Maya
        
        
        @type  name: string
        @param name: request name of an host object
        
        @rtype:   hostObject
        @return:  the object with the requested name or None
        """
        return None

    def getObjectName(self,o):
        """
        Return the name of an host object.
        
        * overwrited by children class for each host
    
        >>> obj = helper.Sphere("mySphere")
        >>> name = helper.getObjectName(obj)
        >>> print (name)
        mySphere
    
        @type  o: hostObject
        @param o: an host object
        @rtype:   string
        @return:  the name of the host object
        """
        pass

    
    @classmethod
    def getCurrentScene(self,):
        """
        Return the current/active working document or scene.
        
        * overwrited by children class for each host
    
        >>> sc = helper.getCurrentScene()
        >>> print (sc)
        None #in maya there is no scene concept
        <bpy_strct, Scene("Scene")  #blender 2.6
        [Scene "Scene"]             #blender 2.49b
        <c4d.documents.BaseDocument object at 0x246c01a0>  #Cinema4D
        
        @rtype:   scene
        @return:  the active scene
        """        
        pass

    @classmethod    
    def getCurrentSceneName(self):
        """
        Return the current/active working document or scene name.
        
        * overwrited by children class for each host

        >>> scname = helper.getCurrentSceneName()
        >>> print (scname)
        None        #maya
        Scene       #blender 2.6
        Scene       #blender 2.49b
        Untitled    #Cinema4D
     
        @rtype:   strng
        @return:  the active scene name
        """        
        pass

    def getCurrentSelection(self,):
        """
        Return the current/active selected object in the document or scene.
        
        * overwrited by children class for each host

        >>> liste_objects = helper.getCurrentSelection()
        >>> print (liste_objects)
        [<c4d.BaseObject object at 0x1e4fd3a0>, <c4d.BaseObject object at 0x1e4fd3d0>] #cinema4D
        
        
        @rtype:   liste
        @return:  the list of selected object
        """        
        pass

    def setCurrentSelection(self,obj):
        """
        Return the current/active selected object in the document or scene.
        
        * overwrited by children class for each host

        >>> liste_objects = [helper.getObject("obj1"),helper.getObject("obj2")]
        >>> helper.setCurrentSelection(liste_objects)
 
        @type  obj: hostObject
        @param obj: the object to be selected  
         """        
        pass
 
 
    def getPosUntilRoot(self,object):
        """
        Go through the hierarchy of the object until reaching the top level, 
        increment the position to get the transformation due to parents. 
        DEPRECATED 
        
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
        at the specified location. This function is used by all the basic object creation function. 
        
        * overwrited by children class for each host
        
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
    
        * overwrited by children class for each host
        
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
        Modify the current object selection. Redundant with setCurrentSelection.
        
        This function make the distinction between adding (typeSel="add") object to the selection and creating
        a new selection (typeSel="new")
        
        * overwrited by children class for each host
        
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
        
        * overwrited by children class for each host
        
        @type  listeObjects: list
        @param listeObjects: list of object to joins
        """    
        sc = self.getCurrentScene()
        
    
    def addCameraToScene(self,name,Type,focal,center,scene,**kw):
        """
        Add a camera object to the scene
        
        * overwrited by children class for each host
        
        >>> sc = helper.getCurrentScene()
        >>> center=[0.,-12.,40.]
        >>> cam = helper.addCameraToScene("cam1","persp",30.,center,sc)    
    
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
        #we  add a **kw for futur arguments
        """    
        pass
#        cam = None
#        self.addObjectToScene(scene,cam)    
    
    def addLampToScene(self,name,Type='Area',rgb=[1.,1.,1.],dist=25.0,energy=1.0,
                       soft=1.0,shadow=False,center=[0.,0.,0.],sc=None,**kw):
        """
        Add a light to the scene

        * overwrited by children class for each host
        
        
        >>> sc = helper.getCurrentScene()
        >>> center=[0.,-12.,40.]
        >>> color = [1.,1.,1.]
        >>> light = helper.addLampToScene("light1","Sun",color,20.,1.0,1.0,True,center,sc)
        
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
        #we  add a **kw for futur arguments
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


    def newEmpty(self,name,location=None,parentCenter=None,**kw):
        """
        Create a new Null/Empty Object
        
        * overwrited by children class for each host

        >>> empty = helper.newEmpty("null1",location=[10.0,0.0,0.0])
        >>> empty_child = helper.newEmpty("null2",location=[15.0,0.0,0.0],parent = empty)
        
        @type  name: string
        @param name: name of the empty
        @type  location: list
        @param location: position of the null object
        @type  parentCenter: list
        @param parentCenter: position of the parent object DEPRECATED
        
        @type kw: dictionary
        @param kw: you can add your own keyword, but it should be interpreted by all host
            -"parent"
        @rtype:   hostObject
        @return:  the null object
        """
        empty=None#
        if location != None :
            if parentCenter != None : 
                location = location - parentCenter
            #set the position of the object to location       
        return empty
    
    def newInstance(self,name,object,location=None,hostmatrice=None,matrice=None,**kw):
        """
        Create a new Instance from another Object
        
        * overwrited by children class for each host
        
        >>> sph = helper.Sphere("sph1")
        >>> instance_sph = helper.newInstance("isph1",sph,location = [10.0,0.0,0.0])
        
    
        @type  name: string
        @param name: name of the instance
        @type  object: hostObject
        @param object: the object to inherit from   
        @type  location: list/Vector
        @param location: position of the null object
        @type  hostmatrice: list/Matrix 
        @param hostmatrice: transformation matrix in host format
        @type  matrice: list/Matrix
        @param matrice: transformation matrix in epmv/numpy format
        @type kw: dictionary
        @param kw: you can add your own keyword, but it should be interpreted by all host
            -"parent"
            -"material"       
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
        return None       

    def getMasterInstance(self,instance,**kw):
        """
        Return the object use for the instanciation
        """
        return instance
        

    def updateMasterInstance(self,instance, objects,add=True,hide=True,**kw):
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
        pass
        

    def toggleDisplay(self,object,display):
        """
        Toggle on/off the display/visibility/rendermode of an hostObject in the host viewport.
                
        * overwrited by children class for each host

        >>> helper.toggleDisplay("polygone1",True)
        >>> obj = helper.getObject("polygone1")
        >>> helper.toggleDisplay(obj,False)       
        
        @type  object: hostObject
        @param object: the object   
        @type  display: boolean
        @param display: if the object is displayed
        """    

    def toggleXray(self,object,xray):
        """
        Toggle on/off the Xray visibility of an hostObject in the host viewport. Currently not supported in Maya
        
        * overwrited by children class for each host

        >>> helper.toggleXray("polygone1",True)
        >>> obj = helper.getObject("polygone1")
        >>> helper.toggleXray(obj,False)       
        
        @type  object: hostObject
        @param object: the object   
        @type  xray: boolean
        @param xray: if the object is Xray displayed
        """    
        print("not supported yet in ",self.host)
    
    def getVisibility(self,obj,editor=True, render=False, active=False):    
        """
        return the editor/renedring/active visibility state of the given object
        
        * overwrited by children class for each host
        
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
    

    def setViewport(self,**kw):
        """
        set the property of the viewport
        
        * overwrited by children class for each host
        
        @type  kw: dictionary
        @param kw: the list of parameter and their value to change   
        """    
        print ("setViewport helper class")
        pass        
    
    def toggleEditMode(self):
        """
        Turn off edit mode (if any)
        
        """
        pass

    def restoreEditMode(self, editmode=1):
        """
        Restor any edit mode (if any)
        """
        pass
    
    def setObjectMatrix(self,object,matrice,hostmatrice=None,absolue=True,**kw):
        """
        Set a matrix to an hostObject
        
        * overwrited by children class for each host
        
        @type  object: hostObject
        @param object: the object who receive the transformation 
        @type  hostmatrice: list/Matrix 
        @param hostmatrice: transformation matrix in host format
        @type  matrice: list/Matrix
        @param matrice: transformation matrix in epmv/numpy format
        @type  absolue: Boolean
        @param absolue: absolute or local transformation        
        @type kw: dictionary
        @param kw: you can add your own keyword, but it should be interpreted by all host

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
        Apply a matrix to an hostObject
        
        * overwrited by children class for each host
        
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

   
    def translateObj(self,object,position,use_parent=True,absolue=True,**kw):
        """
        Global Translation : Move the object to the vector position     
        
        * overwrited by children class for each host
        
        @type  object: hostObject
        @param object: the object   
        @type  position: liste/array
        @param position: the new object position px,py,pz  
        @type  use_parent: boolean
        @param use_parent: if the parent position is used
        @type  absolue: Boolean
        @param absolue: absolute or local transformation        
        @type kw: dictionary
        @param kw: you can add your own keyword, but it should be interpreted by all host
        
        """
        pass
    
    def scaleObj(self,object,absolue=True,**kw):
        """
        Global Scale : scale the object by the vector scale 
        
        * overwrited by children class for each host
        
        @type  object: hostObject
        @param object: the object
        @type  absolue: Boolean
        @param absolue: absolute or local transformation        
        @type kw: dictionary
        @param kw: you can add your own keyword, but it should be interpreted by all host
 
        """
        pass


        
    def rotateObj(self,object,rotation,absolue=True,**kw):
        """
        Global Rotation : Rotate the object 
        This method take a 3d array [rotation_X,rotatio_Y,rotation_Z]
        
        * overwrited by children class for each host
        
        @type  object: hostObject
        @param object: the object   
        @type  rotation: liste/array - matrice
        @param rotation: the new object rotation
        @type  absolue: Boolean
        @param absolue: absolute or local transformation        
        @type kw: dictionary
        @param kw: you can add your own keyword, but it should be interpreted by all host
       
        """
        pass

    def setTranslation(self,name,pos=[0.0,0.,0.],absolue=True,**kw):
        """
        Return the current position (translation)  of the  given object in absolute or local world
        
        * overwrited by children class for each host
        
        @type  name: hostObject
        @param name: the object name
        @type  pos: list<float>
        @param pos: the new position        
        @type  absolue: Boolean
        @param absolue: absolute or local transformation
        @type kw: dictionary
        @param kw: you can add your own keyword, but it should be interpreted by all host
  
        """
        pass

    def getTranslation(self,name,absolue=True,**kw):
        """
        Return the current position (translation)  of the  given object in absolute or local world
        
        * overwrited by children class for each host
        
        @type  name: hostObject
        @param name: the object name
        @type  absolue: Boolean
        @param absolue: absolute or local transformation
        @type kw: dictionary
        @param kw: you can add your own keyword, but it should be interpreted by all host
    
       
        @rtype:   3d vector/list
        @return:  the position   
        """
        return [0.,0.,0.]


    def getSize(self,name,**kw):
        """
        Return the current size in x, y and z of the  given object if applcable
        
        * overwrited by children class for each host
        
        @type  name: hostObject
        @param name: the object name
       
        @rtype:   3d vector/list
        @return:  the size in x y and z   
        """
        return [0.,0.,0.]

    def getScale(self,name,absolue=True,**kw):
        """
        Return the current scale of the  given object in absolute or local world
        
        * overwrited by children class for each host
        
        @type  name: hostObject
        @param name: the object name
        @type  absolue: Boolean
        @param absolue: absolute or local transformation    
       
        @rtype:   3d vector/list
        @return:  the scale   
        """
        return [1.,1.,1.]

    def resetTransformation(self,object,**kw):
        """
        ReSet the transformation of a given Object to identity
        
        * can be overwriten by children class for each host
        
        @type  object: string or Object
        @param object: the object who receive the identity transformation
        """
        m= [[1.,0.,0.,0.],
           [ 0.,1.,0.,0.],
           [ 0.,0.,1.,0.],
           [ 0.,0.,0.,1.]]
        self.setObjectMatrix(object,m)
    
        
    def setTransformation(self,name,mat=None,rot=None,scale=None,trans=None,order="str",**kw):
        """
        Set the transformatio of a given Object
        
        * can be overwriten by children class for each host
        
        @type  name: string
        @param name: the object who receive the transformation 
        @type  mat: list/Matrix 
        @param mat: transformation matrix
        @type  rot: list
        @param rot: rotation along [X,Y,Z]
        @type  scale: list
        @param scale: scale along [X,Y,Z]
        @type  trans: list
        @param trans: translation along [X,Y,Z]
        @type  order: string
        @param order: order of transformation
        @type  kw: Dictionary
        @param kw: additional arguemts      
        """
        obj = self.getObject(name)
        absolue  = True       
        if "abs" in kw :
            absolue=kw["abs"]
        if mat is not None :
            self.setObjectMatrix(obj,mat,absolue=absolue,**kw)
        if rot is not None:
            self.rotateObj(obj,rot,absolue=absolue)
        if scale is not None:
            self.scaleObj(obj,scale,absolue=absolue)
        if trans is not None:
            self.translateObj(obj,trans,absolue=absolue)

    def updateTubeObjs(self,listeObj,listePts,listeInd=None):
        """
        This function will update a liste of Tupe according the given liste of new points.
        One Tube is define by two 3d points. 
        
        """
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
        """
        Add material to the current scene given a dictionary {"name":[r,b,g]}
        
        
        >>> matDic={"mat1":[0,0,0],"mat2":[1,1,1]}
        >>> helper.addMaterialFromDic(matDic)    

        @type  dic: Dictionary
        @param dic: the name:color dictionary for creating materials
        
        """
        #dic: Name:Color
        [self.addMaterial(x,dic[x]) for x in list(dic.keys())]

    def createColorsMat(self):
        """
        Create a Material for all defined colors in upy.colors
    
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
        color is defined in upy.colors
    
        @type  color: array
        @param color: the material color (r,g,b)
    
        @rtype:   hostMaterial
        @return:  the material of color color
        """            
        if color is None :
            return None
        doc = self.getCurrentScene()
        mat = self.getMaterial(color)
        print(mat,color,type(mat)) 
        if mat is not None and type(mat) != list and type(mat) != tuple:
            return mat
        if len(mat) == 1 :
            if mat[0] is not None and type(mat[0]) != list and type(mat[0]) != tuple:
                return mat[0]
        print (type(color) )
        if type(color) == str or type(color) == unicode :
            if color in colors.cnames :
                 if mat is None :
                     return self.addMaterial(color,eval("colors."+col))
            else :
                return mat
        for col in colors.cnames:
            if tuple(color) == eval("colors."+col) :
                mat = self.getMaterial(col)  
                if mat is None :
                     return self.addMaterial(col,eval("colors."+col))
        name= "customMat"+str(color[0])+str(color[1])+str(color[2])
        return self.addMaterial(name.replace(".",""), color)
        
    def addMaterial(self,name, color):
        """
        Add a material in the current document 
        
        * overwrited by children class for each host
        
        @type  name: string
        @param name: the material name
        @type  color: array
        @param color: the material color (r,g,b)
    
        @rtype:   hostMaterial
        @return:  the new material 
        """    
        pass

    def assignMaterial(self,object,matname,texture = True,**kw):
        """
        Assign the provided material to the object 
        
        * overwrited by children class for each host
        
        @type  object: hostApp object
        @param object: the object    
        @type  matname: string
        @param matname: the material name
        @type  texture: Boolean
        @param texture: is the material use a textue
        @type  kw: dictionary
        @param kw: additional keywords options       
        """    
        #verify if the mat exist, if the string.
        #apply it to the object
        pass

    def colorMaterial(self,mat,col):
        """
        Color a given material using the given color (r,g,b).
        
        * overwrited by children class for each host
        
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
        """
        Get the maerial of the given name.
        
        * overwrited by children class for each host
        
        @type  name: string
        @param name: the name of the desired material
        
        @rtype:   hostMaterial
        @return:  the new material 
        """ 
        pass
    

    def getAllMaterials(self):
        """
        Get all the maerials of the current scene.
        
        * overwrited by children class for each host
        
        @rtype:   list
        @return:  the list of all materials available
        """ 

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
        

    def colorObject(self,obj,color,**options):
        """
        Apply the given color to the given object, 
        
        * overwrited by children class for each host
        
        @type  obj: string or hostObject
        @param obj: the object to be colored
        @type  color: list
        @param color: the color to apply [r,g,b]
        @type  options: Dictionary
        @param options: additional keyword options :
            useMaterial : crete a materal with the given color and assign it to the object
            useObjectColors : change the color propertie of the object (Viewport)
        """        
        useMaterial = False
        useObjectColors = False        
        if options.has_key("useMaterial"):
            useMaterial = options["useMaterial"]
        if options.has_key("useObjectColors"):
            useObjectColors = options["useObjectColors"]
        
        
    def changeColor(self,obj,colors,perVertex=False,proxyObject=True,doc=None,pb=False,
                    facesSelection=None,faceMaterial=False):
        """
        Apply the given set of color to the given object, 
        if the object is a mesh this function handle the color per vertex.
        
        * overwrited by children class for each host
        
        @type  obj: string or hostObject
        @param obj: the object to be colored
        @type  colors: list
        @param colors: the list of colors to apply [[r,g,b],[r,g,b],...]
        @type  perVertex: Boolean
        @param perVertex: is it color per Vertex
        @type  proxyObject: Boolean
        @param proxyObject: special keyword for Cinema4D which doesnt support vertex color
        @type  doc: Scene
        @param doc: the current working documents
        @type  pb: Boolean
        @param pb: use the progress bar 
        @type  facesSelection: liste
        @param facesSelection: only assign color to the given face selecion
        @type  faceMaterial: Boolean
        @param faceMaterial: assign color per Face        
        """
        pass
    
    def changeObjColorMat(self,obj,color):
        """
        Change the diffuse color of the object material.
        
        * overwrited by children class for each host
        
        @type  obj: string or hostObject
        @param obj: the object forwhich we want to change e material color
        @type  color: list
        @param color: the new color to apply [r,g,b]       
        """
        pass

    
    def getMesh(self,name):
        """
        Get the mesh of given name
        
        * overwrited by children class for each host

        @type  name: string
        @param name: the name of the deired mesh
        
        @rtype:   hostMesh
        @return:  the mesh
        """ 
        return name


    def getLayers(self, scn):
        """
        Return a list of active layers of a scene or an object
        """
        return []

    def setLayers(self, scn, layers):
        """
        Set the layers of a scene or an object, expects a list of integers
        """

    def checkIsMesh(self,name):
        """
        Verify that name correspond to a valid mesh.
        
        * overwrited by children class for each host

        @type  name: string
        @param name: the name of the deired mesh
        
        @rtype:   hostMesh
        @return:  the mesh
        """ 
        return name

    def getName(self,object):
        """
        Return the name of an host object. Redundant with getObjecName
        
        * overwrited by children class for each host
    
        >>> obj = helper.Sphere("mySphere")
        >>> name = helper.getObjectName(obj)
        >>> print (name)
        mySphere
    
        @type  object: hostObject
        @param object: an host object
        @rtype:   string
        @return:  the name of the host object
        """

    def setName(self,object,name):
        """
        Set the name of an host object. Redundant with getObjecName
        
        * overwrited by children class for each host
    
        >>> obj = helper.Sphere("mySphere")
        >>> name = "mySpinningsphere"
        >>> helper.setName(obj,name)
    
        @type  object: hostObject
        @param object: an host object
        @type  name: string
        @param name: the new name
        """
        
    def reParent(self,objs,parent):
        """
        Change the object parent using the specified parent objects
    
        * overwrited by children class for each host
        
        @type  objs: hostObject
        @param objs: the object or liste of objects to be reparented
        @type  parent: hostObject
        @param parent: the new parent object
        """    
        pass


    def deleteChildrens(self,obj):
        """
        Delete recursively all the children of the given object.
        
        @type  obj: hostObject
        @param obj: the object for which we want to delete the childs
        """    
        
        #recursively delete obj and childrenobject
        obj = self.getObject(obj)
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
        Cosntraint an hostobject to look at the camera. 
        
        * overwrited by children class for each host
        
        @type  object: Hostobject
        @param object: object to constraint
        """
        pass

#===============================================================================
#     Basic object
#===============================================================================
    def Text(self,name="",string="",parent=None,size=5.,pos=None,font=None,lookAt=False,**kw):
        """
        Create a hostobject of type Text.
        
        * overwrited by children class for each host
        
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
        @type  kw: dictionary
        @param kw: additional keywords options 
        
        @rtype:   hostObject
        @return:  the created text object
        """    
        text = None
        return text
        
    def Circle(self,name, rad=1.,**kw):
        """
        Create a hostobject of type 2d circle.
        
        * overwrited by children class for each host
        
        @type  name: string
        @param name: name of the circle
        @type  rad: float
        @param rad: the radius of the cylinder (default = 1.)
        @type  kw: dictionary
        @param kw: additional keywords options 
        
        @rtype:   hostObject
        @return:  the created circle
        """    
        #put the apropriate code here
        circle=None
        #set name and rad for the circle
        return circle

    def rerieveAxis(self,axis):
        """
        Return the axis from the given array (X,Y or Z +/-).
        
        @type  axis: list
        @param axis: the aray [x,y,z]
        
        @rtype:   string
        @return:  the axis of the array
        """            
        dic = {"+X":[1.,0.,0.],"-X":[-1.,0.,0.],"+Y":[0.,1.,0.],"-Y":[0.,-1.,0.],
                    "+Z":[0.,0.,1.],"-Z":[0.,0.,-1.]}
        axis=[float(int(axis[0])),float(int(axis[1])),float(int(axis[2]))]
        for k in dic :
            if list(axis) == dic[k]:
                return k

    def CylinderHeadTails(self,cylinder,**kw):
        res = self.getPropertyObject(cylinder, 
                        key=["pos","rotation","length","axis"])
        if res is None :
            return None,None
        pos,rot,l,axis = res
#        if self.usenumpy :
        h=(numpy.array(axis) * l/2.0)
        t=(numpy.array(axis) * l/2.0)
        m = numpy.matrix(rot)
        h,t=self.ApplyMatrix([h,t],m.I)
        head = numpy.array(pos) + h
        tail = numpy.array(pos) - t
        #self.ToMat(rot))#invert/transpose he matrix?
        return head, tail
    
    def Cylinder(self,name,radius=1.,length=1.,res=16, pos = [0.,0.,0.],**kw):
        """
        Create a hostobject of type cylinder.
        
        * overwrited by children class for each host
        
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
        @type  kw: dictionary
        @param kw: additional keywords options
        
        @rtype:   hostObject,hostMesh
        @return:  the created cylinder object and mesh
        """    
        return None,None
    		
    def Sphere(self,name,radius=1.0,res=0, pos = [0.,0.,0.],**kw):
        """
        Create a hostobject of type sphere.
        
        * overwrited by children class for each host
        
        @type  name: string
        @param name: name of the sphere
        @type  radius: float
        @param radius: the radius of the sphere
        @type  res: float
        @param res: the resolution/quality of the sphere
        @type  pos: array
        @param pos: the position of the cylinder
        @type  kw: dictionary
        @param kw: additional keywords options
        
        @rtype:   hostObject,hostMesh
        @return:  the created sphere object and mesh
        """    
    
        QualitySph={"0":6,"1":4,"2":5,"3":6,"4":8,"5":16} 
        return None,None

    def getBoxSize(self,name,**kw):
        """
        Return the current size in x, y and z of the  given Box if applcable
        
        * overwrited by children class for each host
        
        @type  name: hostObject
        @param name: the Box name
       
        @rtype:   3d vector/list
        @return:  the size in x y and z   
        """        
        return [1.,1.,1.]
        
    def box(self,name,center=[0.,0.,0.],size=[1.,1.,1.],cornerPoints=None,
                visible=1,**kw):
        """
        Create a hostobject of type cube.
        
        * overwrited by children class for each host
        
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
        @type  kw: dictionary
        @param kw: additional keywords options
        
        @rtype:   hostObject,hostMesh
        @return:  the created box object and mesh
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
        return box,None

    def updateBox(self,box,center=[0.,0.,0.],size=[1.,1.,1.],cornerPoints=None,
                    visible=1, mat = None,**kw):
        """
        Update the given box.
        
        * overwrited by children class for each host
        
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
        @type  kw: dictionary
        @param kw: additional keywords options
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
        size = self.ToVec(self.getBoxSize(obj))
#        try :
#            size = self.ToVec(obj[1100])#this will broke other host!
#        except :
#            size = self.ToVec(self.getScale(obj))
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
        
    def spline(self,name, points,close=0,type=1,scene=None,parent=None,**kw):
        """
        This will return a hostApp spline/curve object according the given list
        of point.
        
        * overwrited by children class for each host

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
        @type  kw: dictionary
        @param kw: additional keywords options
        
        @rtype:   hostObject,hostMesh
        @return:  the created spline object and data
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
        
        * overwrited by children class for each host
        
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
        
        @rtype:   hostObject,hostMesh
        @return:  the created plane object and data
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
        return plane,None

    def update_spline(self,name,coords):
        """
        This will update the spline points coordinates
        
        * overwrited by children class for each host
        
        @type  name: string
        @param name: name for the spline to update
        @type  coords: liste/array vector
        @param coords: list of new position coordinate to apply to the curve point
        """
        pass


#===============================================================================
#     Platonic
#===============================================================================
    #this already exist in c4d,overwrite in host if support it
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

    def MidPoint(self, p1, p2):
       return [(p1[0] + p2[0]) / 2.0,(p1[1] + p2[1]) / 2.0,(p1[2] + p2[2]) / 2.0];
        
    def createUnitSphereData(self,iterations):
        """from http://paulbourke.net/geometry/circlesphere/csource2.c"""
        i=0
        j=0
        n=0
        nstart=0
        vertices=[]
        p1 = self.normalize((1.0,1.0,1.0))
        p2 = self.normalize((-1.0,-1.0,1.0))
        p3 = self.normalize((1.0,-1.0,-1.0))
        p4 = self.normalize((-1.0,1.0,-1.0)) 
        vertices.extend([p1,p2,p3,p4])
        facets=numpy.zeros((math.pow(4,iterations),3),'int')
        facets[0] = [0,1,2]#p1; facets[0].p2 = p2; facets[0].p3 = p3;
        facets[1] = [0,1,3]#.p1 = p2; facets[1].p2 = p1; facets[1].p3 = p4;
        facets[2] = [1,3,2]#.p1 = p2; facets[2].p2 = p4; facets[2].p3 = p3;
        facets[3] = [0,2,3]#.p1 = p1; facets[3].p2 = p3; facets[3].p3 = p4;

        n = 4;
        for i in range(1,iterations):# (i=1;i<iterations;i++) {
            nstart = n
            for j in range(nstart):# (j=0;j<nstart;j++) {
                #/* Create initially copies for the new facets */
                facets[n  ] = facets[j];
                facets[n+1] = facets[j];
                facets[n+2] = facets[j];

                #/* Calculate the midpoints */
                p1 = self.MidPoint(vertices[facets[j][0]],vertices[facets[j][1]]);
                p2 = self.MidPoint(vertices[facets[j][1]],vertices[facets[j][2]]);
                p3 = self.MidPoint(vertices[facets[j][2]],vertices[facets[j][0]]);
                vertices.extend([p1,p2,p3])
                ip1=len(vertices)-3
                ip2=len(vertices)-2
                ip3=len(vertices)-1
                #/* Replace the current facet */
                facets[j][1] = ip1;
                facets[j][2] = ip3;
                #/* Create the changed vertices in the new facets */
                facets[n  ][0] = ip1;
                facets[n  ][2] = ip2;
                facets[n+1][0] = ip3;
                facets[n+1][1] = ip2;
                facets[n+2][0] = ip1;
                facets[n+2][1] = ip2;
                facets[n+2][2] = ip3;
                n += 3;
        vertices=[self.normalize(v) for v in vertices]
        return vertices,facets;

    def unitSphere(self,name,iterations,radius):   
        """
        Create the mesh data and the mesh object of a Icosahedron of a given radius
        
        @type  name: string
        @param name: name for the spline to update        
        @type  radius: float
        @param radius: radius of the embeding sphere
        
        @rtype:   Object, Mesh
        @return:  Icosahedron Object and Mesh      
        """     
        v,f = self.createUnitSphereData(iterations)
        ob,obme = self.createsNmesh(name,numpy.array(v)*radius,None,f)
        return ob,obme

    def reporthook(self,count, blockSize, totalSize):
        percent = float(count*blockSize/totalSize)
        self.progressBar(percent,"Downloading...")
        print (percent)
        if percent >=1.:
            self.resetProgressBar()
        
    
    def progressBar(self,progress,label):
        """ 
        Update the progress bar status by progress value and label string
        
        * overwrited by children class for each host
        
        @type  progress: Int/Float
        @param progress: the new progress
        @type  label: string
        @param label: the new message to put in the progress status
        """                
        pass

    def resetProgressBar(self,value=None):
        """
        Reset the Progress Bar, using value

        * overwrited by children class for each host
        
        """
        pass
    
#===============================================================================
#     Texture Mapping / UV
#===============================================================================
    def getUVs(self):
        """
        Reset the Progress Bar, using value

        * overwrited by children class for each host
        
        """
        pass

        
    def setUVs(self):
        """
        Reset the Progress Bar, using value

        * overwrited by children class for each host
        
        """
        pass

        
    def getUV(self,object,faceIndex,vertexIndex,perVertice=True):
        """
        Return the UV coordinate of the given object according faceIndex and vertexIndex 

        * overwrited by children class for each host
        
        @type  object: string/hostObject
        @param object: the object from which we want the UV        
        @type  faceIndex: list
        @param faceIndex: the liste of face index for which we want the UV
        @type  vertexIndex: list
        @param vertexIndex: the liste of vertex index for which we want the UV
        @type  perVertice: Boolean
        @param perVertice: UV coordinate access per verticer or per face
        
        @rtype:   list
        @return:  the list of UV coordinates for the given object according faceIndex and vertexIndex             
        """
        pass

        
    def setUV(self,object,faceIndex,vertexIndex,uv,perVertice=True):
        """
        Update/Set the UV coordinate of the given object according faceIndex and vertexIndex 

        * overwrited by children class for each host
        
        @type  object: string/hostObject
        @param object: the object from which we want to update the UV        
        @type  faceIndex: list
        @param faceIndex: the liste of face index for which we want to update the UV
        @type  vertexIndex: list
        @param vertexIndex: the liste of vertex index for which we want to update the UV
        @type  uv: list
        @param uv: the new uv coordinate [i,j]        
        @type  perVertice: Boolean
        @param perVertice: UV coordinate access per verticer or per face
        
        """
        pass

    
#===============================================================================
#     mesh
#===============================================================================
    


    def findClosestPoint(self,point,object,transform=True):
        """
        Find the closest vertices to the given 3d points in Python implementation 
        
        @type  point: 3 points
        @param point: the point to look up       
        @type  object: hostObj/hostMesh/String
        @param object: the object to scan for closest vertices
        @type  transform: Boolean
        @param transform: take in account the object transformation or not
        
        @rtype  :list
        @return : the minimal distance found and the closest vertices in the given polygon       
        """
        
        #python lookup for closest point,probably not the fastest way
        vertices = self.getMeshVertices(object)
        if transform :
            mat = self.getTransformation(object)
            vertices = self.ApplyMatrix(vertices,self.ToMat(mat))
        #bhtree?
        mini=9999.0
        miniv=vertices[0]
        for v in range(len(vertices)):
            d = self.measure_distance(vertices[v],point)
            if d < mini : 
                mini =d
                miniv = vertices[v]
        return mini,miniv

    def ToMat(self,mat):
        """
        Return a python (4,4) matrice array from a host matrice
    
        * overwrited by children class for each host
    
        @type  mat: host matrice array
        @param mat: host matrice array 
        @rtype:   matrice
        @return:  the converted  matrice array
        """
        return mat
    
    def ToVec(self,v):
        """
        Return a python xyz array from a host xyz array/vector
    
        * overwrited by children class for each host
        
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
                     material=None,proxyCol=False,color=[[1,0,0],],**kw):
        """
        Function that generate a Polygon object from the given vertices, face and normal.
        material or color can be passed and apply to the created polygon.
        Return the object and the mesh.
        
        * overwrited by children class for each host
        
        @type  name: string
        @param name: name of the pointCloud
        @type  vertices: list
        @param vertices: the list of vertices
        @type  vnormals: list
        @param vnormals: the list of vertices normal
        @type  faces: list
        @param faces:  the list of normal
        @type  smooth: string
        @param smooth: smooth the mesh or not
        @type  material: hostMaterial
        @param material: the material to apply to the mesh object
        @type  proxyCol: Boolean
        @param proxyCol: special option for C4D DEPRECATED
        @type  color: list
        @param color: color to apply to the mesh object         
        @type  kw: dictionary
        @param kw: dictionary of arg options, ie :
            'parent'   hostAp parent object
    
        @rtype:   hostObj/hostMesh
        @return:  the polygon object and data
        """        
        pass
    
    def PointCloudObject(self,name,**kw):
        """
        This function create a special polygon which have only point.
        See createsNmesh or particul if the hostdoes no support only point mesh
        
        * overwrited by children class for each host
        
        @type  name: string
        @param name: name of the pointCloud
        @type  kw: dictionary
        @param kw: dictionary of arg options, ie :
            'vertices' array of coordinates ;
            'faces'    int array of faces ;
            'parent'   hostAp parent object
    
        @rtype:   hostApp obj
        @return:  the polygon object and data
        """
        return None,None
    
    def addBone(self,i,armData,headCoord,tailCoord,
                roll=10,hR=0.5,tR=0.5,dDist=0.4,boneParent=None,
                name=None,editMode=True,**kw):
        """
        Add one bone to an armature.
        Optional function for creation of the armature
        
        * overwrited by children class for each host
        
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
        @type  kw: dictionary
        @param kw: dictionary of arg options
    
        @rtype:   bone
        @return:  the created bone
        """        
        eb=None
        return eb

    def updateArmature(self,basename,x,listeName=None,scn=None,root=None,**kw) :
        pass
        
    def armature(self,name,coords,**kw):
        """
        Create an armature along the given coordinates
        
        * overwrited by children class for each host
        
        @type  name: string
        @param name: name of the armature object
        @type  coords: list of array xyz
        @param coords: coordinate foreach bone 
        @type  kw: dictionary
        @param kw: dictionary of arg options
        
        @rtype:   host Object,list of bone
        @return:  the created armature and the created bones      
        """                
        pass
        #return armObj,bones
    
    def oneMetaBall(self,metab,rad,coord,**kw):
        """
        Add one ball to a metaball object.
        Optional function for creation of the metaball
        
        * overwrited by children class for each host
        
        @type  metab: metaball host data
        @param metab: the metaball
        @type  rad: float
        @param rad: radius for the new ball
        @type  coord: array xyz
        @param coord: coordinate of the ball
        @type  kw: dictionary
        @param kw: dictionary of arg options
        
        @rtype:   ball/None
        @return:  the ball or None
        """        
        pass
        
    def metaballs(self,name,listePt,listeR,**kw):
        """
        Create a metaballs along the given coordinates
        
        * overwrited by children class for each host
        
        @type  name: string
        @param name: name of the metaballs object
        @type  listePt: list of array xyz
        @param listePt: coordinate foreach bone  
        @type  listeR: list of float
        @param listeR: radius foreach ball 
        @type  kw: dictionary
        @param kw: dictionary of arg options
               
        @rtype:   host Object,list of bone/metaball data
        @return:  the created metaballs,the created ball     
        """                
        return None,None

#==============================================================================
# Particle
#==============================================================================
    def particle(self,name,coords,group_name=None,radius=None,color=None,hostmatrice=None,**kw):
        """
        Create a particle system along the given coordinates
        
        * overwrited by children class for each host
        
        @type  name: string
        @param name: name of the particle system
        @type  coords: list of array xyz
        @param coords: coordinate foreach particle  
        @type  radius: list of float
        @param radius: radius foreach particle 
        @type  kw: dictionary
        @param kw: dictionary of arg options
        
        @rtype:   host Object,list of bone/metaball data
        @return:  the created metaballs,the created ball     
        """                
        pass

    def updateParticles(self,newPos,PS=None,**kw): 
        """
        Update the particle system along the given new coordinates.
        remove or add particle.
        
        * overwrited by children class for each host
        
        @type  newPos: list of array xyz
        @param newPos: coordinate foreach particle  
        @type  PS: Particle object
        @param PS: the particle system
        @type  kw: dictionary
        @param kw: dictionary of arg options         
        """                
        pass        

    def getParticles(self,name,**kw):
        """
        Return a particle system along the given name
        
        * overwrited by children class for each host
        
        @type  name: string
        @param name: name of the particle system
        @type  kw: dictionary
        @param kw: dictionary of arg options 
        
        @rtype:   host Object particle data
        @return:  the created particle    
        """                
        return None
        
    def setParticulesPosition(self,newPos,PS=None,**kw):    
        """
        Update he particle position of a particle system along the given new coordinates
        
        * overwrited by children class for each host
         
        @type  newPos: list of array xyz
        @param newPos: coordinate foreach particle  
        @type  PS: Particle object
        @param PS: the particle system
        @type  kw: dictionary
        @param kw: dictionary of arg options           
        """                
        pass        

    def getParticulesPosition(self,PS=None,**kw):    
        """
        Get the particle position of a particle system
         
        * overwrited by children class for each host
         
        @type  PS: Particle object
        @param PS: the particle system
        @type  kw: dictionary
        @param kw: dictionary of arg options 
        
        @rtype:   list of array xyz
        @return:  coordinate foreach particle                    
        """                
        pass        

#===============================================================================
# Mesh Function
#===============================================================================
    def getMeshVertice(self,poly,vertex_indice,**kw):
        """
        Get the vertices of the given polygon object data
         
        * overwrited by children class for each host
         
        @type  poly: hostObject
        @param poly: the object from which we want the vertices
        @type  vertex_indice: int
        @param vertex_indice: return only the give vertice coordinates       
        @type  kw: dictionary
        @param kw: dictionary of arg options 
        
        @rtype:   list of float xyz
        @return:  coordinate for one vertice of the given object                    
        """                
        pass

    def getMeshVertices(self,poly,selected=False,**kw):
        """
        Get the vertices of the given polygon object data
         
        * overwrited by children class for each host
         
        @type  poly: hostObject
        @param poly: the object from which we want the vertices
        @type  selected: Boolean
        @param selected: return only the selected vertices or not       
        @type  kw: dictionary
        @param kw: dictionary of arg options 
        
        @rtype:   list of array xyz
        @return:  coordinate for all or for selected vertices of the given object                    
        """                
        pass
        
    def getMeshNormales(self,poly,selected=False,**kw):
        """
        Get the normals of the given polygon object data
         
        * overwrited by children class for each host
         
        @type  poly: hostObject
        @param poly: the object from which we want the normals
        @type  selected: Boolean
        @param selected: return only the selected normals or not       
        @type  kw: dictionary
        @param kw: dictionary of arg options 
        
        @rtype:   list of array xyz
        @return:  coordinate for all or for selected normals of the given object                    
        """                
        pass
        
    def getMeshEdge(self,hostedge,**kw):
        """
        Convert the host edge in python format
         
        * overwrited by children class for each host
         
        @type  hostedge: hostEdge
        @param hostedge: the edge to conver to python 
        @type  kw: dictionary
        @param kw: dictionary of arg options 
        
        @rtype:   list
        @return:  the edge in python format                   
        """                
        pass
        
    def getMeshEdges(self,poly,selected=False,**kw):
        """
        Get the edges of the given polygon object data
         
        * overwrited by children class for each host
         
        @type  poly: hostObject
        @param poly: the object from which we want the edges
        @type  selected: Boolean
        @param selected: return only the selected edges or not       
        @type  kw: dictionary
        @param kw: dictionary of arg options 
        
        @rtype:   list
        @return:  all or selected edges of the given object                    
        """                
        pass

    def getFaceEdges(self, poly, faceindice, selected=False,**kw):
        """
        Get the edges of the given face object data
         
        * overwrited by children class for each host
         
        @type  poly: hostObject
        @param poly: the object from which we want the edges of the face
        @type  faceindice: int
        @param faceindice: the face indice               
        @type  selected: Boolean
        @param selected: return only the selected edges or not       
        @type  kw: dictionary
        @param kw: dictionary of arg options 
        
        @rtype:   list
        @return:  all or selected edges of the given face                    
        """                
        pass
        
    def getFace(self,hostface,r=True,**kw):
        """
        Convert the face edge in python format
         
        * overwrited by children class for each host
         
        @type  hostface: hostFace
        @param hostface: the face to convert to python 
        @type  kw: dictionary
        @param kw: dictionary of arg options. 
            - r=True : Cinema4D reverse face order
        
        @rtype:   list
        @return:  the face in python format [i,j,k]               
        """                
        pass
            
    def getFaces(self,object,selected=False,**kw):
        """
        Get the faces of the given polygon object data
         
        * overwrited by children class for each host
         
        @type  object: hostObject
        @param object: the object from which we want the faces
        @type  selected: Boolean
        @param selected: return only the selected faces or not       
        @type  kw: dictionary
        @param kw: dictionary of arg options 
        
        @rtype:   list
        @return:  all or selected faces of the given object                    
        """                
        pass

        
    def getMeshFaces(self,poly,selected=False,**kw):
        """
        Get the faces of the given polygon object data
         
        * overwrited by children class for each host
         
        @type  poly: hostObject
        @param poly: the object from which we want the faces
        @type  selected: Boolean
        @param selected: return only the selected faces or not       
        @type  kw: dictionary
        @param kw: dictionary of arg options 
        
        @rtype:   list
        @return:  all or selected faces of the given object                    
        """                
        return self.getFaces(poly,selected=selected,**kw)

    def setMeshVertice(self, poly, vertice_indice,vertice_coordinate, select=True,**kw):
        """
        Set the vertice for the given mesh data
         
        * overwrited by children class for each host
         
        @type  poly: hostObject
        @param poly: the object from which we want to set the vertice
        @type  vertice_indice: int
        @param vertice_indice: vertice indice  
        @type  vertice_coordinate: list<float>[3]
        @param vertice_coordinate: x y z coordinate for vertice vertice_indice      
        @type  select: Boolean
        @param select: select status          
        @type  kw: dictionary
        @param kw: dictionary of arg options                   
        """                
        pass

    def setMeshVertices(self, poly, vertices_coordinates, vertices_indices=None, select=True,**kw):
        """
        Set the vertices for the given mesh data
         
        * overwrited by children class for each host
         
        @type  poly: hostObject
        @param poly: the object from which we want to set the vertices 
        @type  vertices_coordinates: list<float>[3]
        @param vertices_coordinates: x y z coordinates for all vertice or vertices_indices  
        @type  vertices_indices: array<int>
        @param vertices_indices: list of vertices indices         
        @type  select: Boolean
        @param select: select status          
        @type  kw: dictionary
        @param kw: dictionary of arg options                   
        """                
        pass

        
    def setMeshFace(self,obj,faceindce,face_vertices_indices,select=True,**kw):
        """
        Set the  face for the given face
         
        * overwrited by children class for each host
         
        @type  obj: hostObject
        @param obj: the object from which we want to set the face
        @type  faceindce: int
        @param faceindce: the face indice  
        @type  vertices_indices: array<int>
        @param vertices_indices: list of vertices indices             
        @type  select: Boolean
        @param select: select status          
        @type  kw: dictionary
        @param kw: dictionary of arg options                   
        """                
        pass
    
    def setMeshFaces(self, obj,faces_vertices_indices,faces=None, select=True,**kw):
        """
        Set the faces  for the given mesh data
         
        * overwrited by children class for each host
         
        @type  obj: hostObject
        @param obj: the object from which we want to set the faces
        @type  faces_vertices_indices: list<array<int>>
        @param faces_vertices_indices: list of faces vertices indices        
        @type  faces: array<int>
        @param faces: list of faces indices    
        @type  select: Boolean
        @param select: select status          
        @type  kw: dictionary
        @param kw: dictionary of arg options                   
        """                
        pass

    def setMeshEdge(self,obj,edgeindce,edge_vertices_indices,select=True,**kw):
        """
        Set the edge for the given mesh data
         
        * overwrited by children class for each host
         
        @type  poly: hostObject
        @param poly: the object from which we want to set the edge
        @type  edgeindce: int
        @param edgeindce: egde indice
        @type  edge_vertices_indices: array<int>
        @param edge_vertices_indices: list of edge vertices indices         
        @type  select: Boolean
        @param select: select status          
        @type  kw: dictionary
        @param kw: dictionary of arg options                   
        """                
        pass


    def setMeshEdges(self, obj, edges_vertices_indices,edges, select=True,**kw):
        """
        Set the edges selecion status  for the given mesh data
         
        * overwrited by children class for each host
         
        @type  poly: hostObject
        @param poly: the object from which we want to select the edges
        @type  edge_vertices_indices: list<array<int>>
        @param edge_vertices_indices: list of edges vertices indices          
        @type  edges: array<int>
        @param edges: list of edges indices    
        @type  select: Boolean
        @param select: select status          
        @type  kw: dictionary
        @param kw: dictionary of arg options                   
        """                
        pass

    def addMeshVertice(self, poly, vertice_coordinate, **kw):
        """
        Add the vertice for the given mesh data
         
        * overwrited by children class for each host
         
        @type  poly: hostObject
        @param poly: the object from which we want to add the vertice
        @type  vertice_coordinate: list<float>[3]
        @param vertice_coordinate: x y z coordinate for the new vertice            
        @type  kw: dictionary
        @param kw: dictionary of arg options                   
        """                
        pass

    def addMeshVertices(self, poly, vertices_coordinates, vertices_indices=None,**kw):
        """
        Add the vertices for the given mesh data
         
        * overwrited by children class for each host
         
        @type  poly: hostObject
        @param poly: the object from which we want to add the vertices 
        @type  vertices_coordinates: list<float>[3]
        @param vertices_coordinates: x y z coordinates for all vertice or vertices_indices     
        @type  kw: dictionary
        @param kw: dictionary of arg options                   
        """                
        pass

        
    def addMeshFace(self,obj,face_vertices_indices,**kw):
        """
        Add the  face for the given face
         
        * overwrited by children class for each host
         
        @type  obj: hostObject
        @param obj: the object from which we want to add the face
        @type  vertices_indices: array<int>
        @param vertices_indices: list of vertices indices                     
        @type  kw: dictionary
        @param kw: dictionary of arg options                   
        """                
        pass
    
    def addMeshFaces(self, obj,faces_vertices_indices,**kw):
        """
        Add the faces  for the given mesh data
         
        * overwrited by children class for each host
         
        @type  obj: hostObject
        @param obj: the object from which we want to add the faces
        @type  faces_vertices_indices: list<array<int>>
        @param faces_vertices_indices: list of faces vertices indices        
        @type  kw: dictionary
        @param kw: dictionary of arg options                   
        """                
        pass

    def addMeshEdge(self,obj,edge_vertices_indices,**kw):
        """
        Set the edge for the given mesh data
         
        * overwrited by children class for each host
         
        @type  poly: hostObject
        @param poly: the object from which we want to add the edge
        @type  edge_vertices_indices: array<int>
        @param edge_vertices_indices: list of edge vertices indices         
        @type  select: Boolean
        @param select: select status          
        @type  kw: dictionary
        @param kw: dictionary of arg options                   
        """                
        pass


    def addMeshEdges(self, obj, edges_vertices_indices,**kw):
        """
        Add the edges selecion status  for the given mesh data
         
        * overwrited by children class for each host
         
        @type  poly: hostObject
        @param poly: the object from which we want to add the edges
        @type  edge_vertices_indices: list<array<int>>
        @param edge_vertices_indices: list of edges vertices indices                
        @type  kw: dictionary
        @param kw: dictionary of arg options                   
        """                
        pass
        
    def selectVertice(self, poly, vertice_indice, select=True,**kw):
        """
        Set the vertice selecion status  for the given mesh data
         
        * overwrited by children class for each host
         
        @type  poly: hostObject
        @param poly: the object from which we want to select the vertice
        @type  vertice_indice: int
        @param vertice_indice: vertice indice    
        @type  select: Boolean
        @param select: select status          
        @type  kw: dictionary
        @param kw: dictionary of arg options                   
        """                
        pass

    def selectVertices(self, poly, vertices_indices, select=True,**kw):
        """
        Set the vertices selecion status  for the given mesh data
         
        * overwrited by children class for each host
         
        @type  poly: hostObject
        @param poly: the object from which we want to select the vertices
        @type  vertices_indices: array<int>
        @param vertices_indices: list of vertices indices    
        @type  select: Boolean
        @param select: select status          
        @type  kw: dictionary
        @param kw: dictionary of arg options                   
        """                
        pass

        
    def selectFace(self,obj,faceindce,select=True,**kw):
        """
        Set the  selecion status  for the given face
         
        * overwrited by children class for each host
         
        @type  poly: hostObject
        @param poly: the object from which we want to select the face
        @type  faceindce: int
        @param faceindce: the face indice  
        @type  select: Boolean
        @param select: select status          
        @type  kw: dictionary
        @param kw: dictionary of arg options                   
        """                
        pass
    
    def selectFaces(self, obj, faces, select=True,**kw):
        """
        Set the faces selecion status  for the given mesh data
         
        * overwrited by children class for each host
         
        @type  poly: hostObject
        @param poly: the object from which we want to select the faces
        @type  faces: array<int>
        @param faces: list of faces indices    
        @type  select: Boolean
        @param select: select status          
        @type  kw: dictionary
        @param kw: dictionary of arg options                   
        """                
        pass

    def selectEdge(self,obj,edgeindce,select=True,**kw):
        """
        Set the edge selecion status  for the given mesh data
         
        * overwrited by children class for each host
         
        @type  poly: hostObject
        @param poly: the object from which we want to select the edge
        @type  edgeindce: int
        @param edgeindce: egde indice
        @type  select: Boolean
        @param select: select status          
        @type  kw: dictionary
        @param kw: dictionary of arg options                   
        """                
        pass


    def selectEdges(self, obj, edges, select=True,**kw):
        """
        Set the edges selecion status  for the given mesh data
         
        * overwrited by children class for each host
         
        @type  poly: hostObject
        @param poly: the object from which we want to select the edges
        @type  edges: array<int>
        @param edges: list of edges indices    
        @type  select: Boolean
        @param select: select status          
        @type  kw: dictionary
        @param kw: dictionary of arg options                   
        """                
        pass

    def deleteMeshVertices(self,poly, vertices=None,select=False,**kw):
        """
        Delete the give vertices indices
         
        * overwrited by children class for each host
         
        @type  poly: hostObject
        @param poly: the object from which we want to delete the vertices
        @type  faces: array<int>
        @param faces: list of vertices indices or None for all    
        @type  select: Boolean
        @param select: delete selected faces         
        @type  kw: dictionary
        @param kw: dictionary of arg options                   
        """                
        pass

    def deleteMeshFaces(self,poly, faces=None,select=False,**kw):
        """
        Delete the give faces indices
         
        * overwrited by children class for each host
         
        @type  poly: hostObject
        @param poly: the object from which we want to delete the faces
        @type  faces: array<int>
        @param faces: list of faces indices or None for all    
        @type  select: Boolean
        @param select: delete selected faces         
        @type  kw: dictionary
        @param kw: dictionary of arg options                   
        """                
        pass

    def deleteMeshEdges(self,poly, edges=None,select=False,**kw):
        """
        Delete the give edges indices
         
        * overwrited by children class for each host
         
        @type  poly: hostObject
        @param poly: the object from which we want to delete the edges
        @type  faces: array<int>
        @param faces: list of edges indices or None for all    
        @type  select: Boolean
        @param select: delete selected faces         
        @type  kw: dictionary
        @param kw: dictionary of arg options                   
        """                
        pass

    def getFacesfromV(self,vindice,faces):
#        print vindice
        ifaces=[]  
        indfaces=[]
        for i,f in enumerate(faces) :
#            print (vindice, f)
            if vindice in f :
#                print "OK"
                ifaces.append(f)
                indfaces.append(i)
        return indfaces,ifaces

    def getFaceNormalsArea(self, vertices, faces):
        """compute the face normal of the compartment mesh"""
        normals = []
        vnormals = numpy.array(vertices[:])
        areas = [] #added by Graham
        face = [[0,0,0],[0,0,0],[0,0,0]]
        v = [[0,0,0],[0,0,0],[0,0,0]]        
        for f in faces:
            for i in range(3) :
                face [i] = vertices[f[i]]
            for i in range(3) :
                v[0][i] = face[1][i]-face[0][i]
                v[1][i] = face[2][i]-face[0][i]                
            normal = vcross(v[0],v[1])
            n = vlen(normal)
            if n == 0. :
                n1=1.
            else :
                n1 = 1./n
            normals.append( (normal[0]*n1, normal[1]*n1, normal[2]*n1) )
    #        The area of a triangle is equal to half the magnitude of the cross product of two of its edges
            for i in range(3) :
                vnormals[f[i]] = [normal[0]*n1, normal[1]*n1, normal[2]*n1]
            areas.append(0.5*vlen(normal)) #added by Graham
        return vnormals,normals, areas
        
    def FixNormals(self,v,f,vn,fn=None):
        newnormals=[]
        for indice,vertex in enumerate(v) :
            ifaces,faces = self.getFacesfromV(indice,f)
            n=[]
#            print len(faces)
            for i,af in enumerate(faces) :
                if fn is not None:
                    n.append(fn[ifaces[i]])
                else :
                    for iv in af :
                        n.append(vn[iv])
            nn=numpy.average(numpy.array(n),0)
#            print nn
            newnormals.append(nn)
        return newnormals

    def matrixToVNMesh(self,name,matrices,vector=[0.,1.,0.],transpose=True,**kw):#edge size ?
        """convert liste of matrix (rotation/position) to point mesh in order to use cloner / dupliVert"""
        pass

    def matrixToFacesMesh(self,name,matrices,vector=[0.,1.,0.],transpose=True,**kw):#edge size ?
        """convert liste of matrix (rotation/position) to quad mesh in order to use cloner / dupliFace"""
        pass
       
    def toggle(self,variable,value):
        variable = value

# Quad
#    0   1
#    3   2
# Tri
#    0   1  3
#    3   1  2
#OR
#   Quad A B C D
#   Triangles A B C / A C D
#   Triangles A B D / D B C (compare A-C B-D)
    def triangulateFace(self,f,vertices):
        A=vertices[f[0]]
        B=vertices[f[1]]
        C=vertices[f[2]]
        D=vertices[f[3]]
        a=self.measure_distance(A,C)
        b=self.measure_distance(B,D)
        if a < b :
            return [[f[0],f[1],f[2]],[f[0],f[2],f[3]]]
        else :
            return [[f[0],f[1],f[3]],[f[3],f[1],f[3]]]

    def triangulateFaceArray(self,faces,vertices):
        trifaces=[]
        for f in faces :
            if len(f) == 2 :
               trifaces.append([f[0],f[1],f[1]])
            elif len(f) == 3 :
               trifaces.append(f)
            elif len(f) == 4 : #triangulate
               trifaces.extend(triangulateFace(f))
#               f1 = [f[0],f[1],f[3]]
#               f2 = [f[3],f[1],f[2]]
#               trifaces.extend([f1,f2])
        return trifaces 
        
    def triangulateFaceArray(self,faces):
        trifaces=[]
        for f in faces :
            if len(f) == 2 :
               trifaces.append([f[0],f[1],f[1]])
            elif len(f) == 3 :
               trifaces.append(f)
            elif len(f) == 4 : #triangulate
               f1 = [f[0],f[1],f[3]]
               f2 = [f[3],f[1],f[2]]
               trifaces.extend([f1,f2])
        return trifaces 

#    from pymunk.vec2d import Vec2d
#    from pymunk.util import is_clockwise, calc_area, is_convex

    ### "hidden" functions
    
    def _is_corner(self,a,b,c):
       # returns if point b is an outer corner
       return not(is_clockwise([a,b,c]))
       
    def _point_in_triangle(self,p,a,b,c):
       # measure area of whole triangle
       whole = abs(calc_area([a,b,c]))
       # measure areas of inner triangles formed by p
       parta = abs(calc_area([a,b,p]))
       partb = abs(calc_area([b,c,p]))
       partc = abs(calc_area([c,a,p]))
       # allow for potential rounding error in area calcs
       # (not that i've encountered one yet, but just in case...)
       thresh = 0.0000001
       # return if the sum of the inner areas = the whole area
       return ((parta+partb+partc) < (whole+thresh))
          
    def _get_ear(self,poly):
       count = len(poly)
       # not even a poly
       if count < 3:
          return [], []
       # only a triangle anyway
       if count == 3:
          return poly, []

       # start checking points
       for i in range(count):
          ia = (i-1) % count
          ib = i
          ic = (i+1) % count
          a = poly[ia]
          b = poly[ib]
          c = poly[ic]
          # is point b an outer corner?
          if _is_corner(a,b,c):
             # are there any other points inside triangle abc?
             valid = True
             for j in range(count):
                if not(j in (ia,ib,ic)):
                   p = poly[j]
                   if _point_in_triangle(p,a,b,c):
                      valid = False
             # if no such point found, abc must be an "ear"
             if valid:
                remaining = []
                for j in range(count):
                   if j != ib:
                      remaining.append(poly[j])
                # return the ear, and what's left of the polygon after the ear is clipped
                return [a,b,c], remaining
                
       # no ear was found, so something is wrong with the given poly (not anticlockwise? self-intersects?)
       return [], []
       
    ### major functions
       
    def _triangulate(self,poly):
       """
       triangulates poly and returns a list of triangles
       poly: list of points that form an anticlockwise polygon (self-intersecting polygons won't work, results are... undefined)
       """
       triangles = []
       remaining = poly[:]
       # while the poly still needs clipping
       while len(remaining) > 2:
          # rotate the list:
          # this stops the starting point from getting stale which sometimes a "fan" of polys, which often leads to poor convexisation
          remaining = remaining[1:]+remaining[:1]
          # clip the ear, store it
          ear, remaining = _get_ear(remaining)
          if ear != []:
             triangles.append(ear)
       # return stored triangles
       return triangles
          
    def triangulate(self,poly,**kw):
        """
        Convert quad to triangle the selected face of the given polygon object.
        
        * overwrited by children class for each host
        
        @type  poly: hostObj
        @param poly: the object to triangulate
        @type  kw: dictionary
        @param kw: dictionary of arg options        
        """
        pass

    def recalc_normals(self,obj,**kw) :
        """
        Recalcul normals mesh outside/inside
        
        * overwrited by children class for each host
        
        @type  poly: hostObj
        @param poly: the object to change the normal
        @type  kw: dictionary
        @param kw: dictionary of arg options        
        """
        pass
       
       
    def IndexedPolgonsToTriPoints(self,geom,transform=True,**kw):
        """
        Convert DejaVu IndexPolygon vertices data in a python list.
        
        * overwrited by children class for each host
        
        @type  geom: DejaVu IndexedPolygon
        @param geom: the object to triangulate
        @type  transform: Boolean
        @param transform: apply the object transformation to the vertices        
        @type  kw: dictionary
        @param kw: dictionary of arg options 

        @rtype  : list
        @return : the vertices data as list    
        """                
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
#==============================================================================
# Object Properties function
#==============================================================================
    #object or scene property ?
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
        return None
        
    def setPropertyObject(self, obj, key, value):
        """
        Create a property "key" for the object obj and set his value
        
        * overwrited by children class for each host
        
        @type  obj: host Obj
        @param obj: the object that contains the property
        @type  key: string
        @param key: name of the property        
        @type  value: int, float, str, dict, list
        @param value: the value of the property
        """          
        
        pass
    
#==============================================================================
# Properties function
#==============================================================================
    #object or scene property ?
    def getProperty(self, obj, key):
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
        return None
        
    def setProperty(self, obj, key, value):
        """
        Create a property "key" for the object obj and set his value
        
        * overwrited by children class for each host
        
        @type  obj: host Obj
        @param obj: the object that contains the property
        @type  key: string
        @param key: name of the property        
        @type  value: int, float, str, dict, list
        @param value: the value of the property
        """          
        
        pass
    
#===============================================================================
# Advanced Function
#===============================================================================
   
    
    def setRigidBody(self,*args,**kw):
        """
        Should set the given object as a rigid body according given options.
        TO DO.
        
        * overwrited by children class for each host
        
        @type  args: list
        @param args: list of arguments options
        @type  kw: dictionary
        @param kw: dictionary of arguments options  
        """                


    def pathDeform(self,*args,**kw):
        """
        Should create a modifierfor the given object using the given path/curve/spline
        TO DO.
        
        * overwrited by children class for each host
        
        @type  args: list
        @param args: list of arguments options
        @type  kw: dictionary
        @param kw: dictionary of arguments options  
        """                
        pass
    
    def updatePathDeform(self,*args,**kw):
        """
        Should update the modifierfor the given object using the given path/curve/spline

        TO DO.
        
        * overwrited by children class for each host
        
        @type  args: list
        @param args: list of arguments options
        @type  kw: dictionary
        @param kw: dictionary of arguments options  
        """                
        pass

#===============================================================================
# numpy dependant function
# we should have alternative from the host
# overwrite if possible by the host math module
#===============================================================================

    def vector_norm(self,data, axis=None, out=None):
        """
        Return length, i.e. eucledian norm, of ndarray along axis.
    
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
    
    @classmethod
    def unit_vector(self,data, axis=None, out=None):
        """
        Return ndarray normalized by length, i.e. eucledian norm, along axis.
    
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
        """
        Return angle (radians) and axis of rotation between two given vectors.
        
        """        
        angle = self.angle_between_vectors(vec1,vec2)
        cr = numpy.cross(vec1,vec2)
        axis = self.unit_vector(cr) 
        return angle,axis

    @classmethod
    def rotation_matrix(self,angle, direction, point=None,trans=None):
        """
        Return matrix to rotate about axis defined by point and direction.
    
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
            point = numpy.array([point[0],point[1],point[2]], dtype=numpy.float64, copy=False)
            M[:3, 3] = point - numpy.dot(R, point)
        if trans is not None :
            M[:3, 3] = numpy.array([trans[0],trans[1],trans[2]], dtype=numpy.float64, copy=False)
        return M

    def rotate_about_axis(self,B,theta,axis=2):
        """
        from http://480.sagenb.org/home/pub/20/ 
        
        Create the rotation matrix for a angle theta around the given axis, and apply it to the given point (B). 
        
        Rotation about 
        
        x-axis corresponds to axis==0, 
        
        y-axis corresponds to axis==1,
        
        z-axis corresponds to axis==2,
        """
        M = numpy.array([]) 
        if axis==0: 
            M = numpy.array([[1,0,0],[0,cos(theta),-sin(theta)],[0,sin(theta),cos(theta)]],dtype=numpy.float64) 
        elif axis==1: 
            M = numpy.array([[cos(theta),0,-sin(theta)],[0,1,0],[sin(theta),0,cos(theta)]],dtype=numpy.float64 )
        elif axis==2: 
            M = numpy.array([[cos(theta),-sin(theta),0],[sin(theta),cos(theta),0],[0,0,1]],dtype=numpy.float64) 
        # Numpy makes large floating point matrix manipulations easy 
        return numpy.dot(M,B)

    def angle_between_vectors(self,v0, v1, directed=True, axis=0):
        """
        Return the angle between vectors.
    
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

    def rotVectToVect(self,vect1, vect2, i=None):
        """returns a 4x4 transformation that will align vect1 with vect2
    vect1 and vect2 can be any vector (non-normalized)
    """
        v1x, v1y, v1z = vect1
        v2x, v2y, v2z = vect2
        
        # normalize input vectors
        norm = 1.0/sqrt(v1x*v1x + v1y*v1y + v1z*v1z )
        v1x *= norm
        v1y *= norm
        v1z *= norm    
        norm = 1.0/sqrt(v2x*v2x + v2y*v2y + v2z*v2z )
        v2x *= norm
        v2y *= norm
        v2z *= norm
        
        # compute cross product and rotation axis
        cx = v1y*v2z - v1z*v2y
        cy = v1z*v2x - v1x*v2z
        cz = v1x*v2y - v1y*v2x
    
        # normalize
        nc = sqrt(cx*cx + cy*cy + cz*cz)
        if nc==0.0:
            return [ [1., 0., 0., 0.],
                     [0., 1., 0., 0.],
                     [0., 0., 1., 0.],
                     [0., 0., 0., 1.] ]
    
        cx /= nc
        cy /= nc
        cz /= nc
        
        # compute angle of rotation
        if nc<0.0:
            if i is not None:
                print ('truncating nc on step:', i, nc)
            nc=0.0
        elif nc>1.0:
            if i is not None:
                print ('truncating nc on step:', i, nc)
            nc=1.0
            
        alpha = asin(nc)
        if (v1x*v2x + v1y*v2y + v1z*v2z) < 0.0:
            alpha = pi - alpha
    
        # rotate about nc by alpha
        # Compute 3x3 rotation matrix
    
        ct = cos(alpha)
        ct1 = 1.0 - ct
        st = sin(alpha)
        
        rot = [ [0., 0., 0., 0.],
                [0., 0., 0., 0.],
                [0., 0., 0., 0.],
                [0., 0., 0., 0.] ]
    
    
        rv2x, rv2y, rv2z = cx*cx, cy*cy, cz*cz
        rv3x, rv3y, rv3z = (1.0-rv2x)*ct, (1.0-rv2y)*ct, (1.0-rv2z)*ct
        rot[0][0] = rv2x + rv3x
        rot[1][1] = rv2y + rv3y
        rot[2][2] = rv2z + rv3z
        rot[3][3] = 1.0;
    
        rv4x, rv4y, rv4z = cx*st, cy*st, cz*st
        rot[0][1] = cx * cy * ct1 - rv4z
        rot[1][2] = cy * cz * ct1 - rv4x
        rot[2][0] = cz * cx * ct1 - rv4y
        rot[1][0] = cx * cy * ct1 + rv4z
        rot[2][1] = cy * cz * ct1 + rv4x
        rot[0][2] = cz * cx * ct1 + rv4y
    
        return rot
    

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
        """
        From two point return the length, and the orientation from one to another.
        This function is used to build a cylinder from two points (see oneCylinder function)

        >>> coord1 = [1.0,0.0,0.0]
        >>> coord2 = [2.0,0.0,0.0]
        >>> distance,matrix = helper.getTubePropertiesMatrix(coord1,coord2)
        >>> helper.setObjectMatrix(obj,matrix)
        
        @type  coord1: vector
        @param coord1: first point
        @type  coord2: vector
        @param coord2: second point
    
        @rtype:   tupple
        @return:  length, 4*4 matrix of rotation
        """        
        #need ot overwrite in C4D
        x1 = float(coord1[0])
        y1 = float(coord1[1])
        z1 = float(coord1[2])
        x2 = float(coord2[0])
        y2 = float(coord2[1])
        z2 = float(coord2[2])
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
# animation features
#===============================================================================
    def setKeyFrame(self,obj,**kw):
        """
        Set a keyframe for the curret object
    
        @type  obj: hostObj
        @param obj: the object
        @type  kw: dictionary
        @param kw: dictionary of arg options                       
        """
        pass        

    def setFrame(self,value,**kw):
        """
        Set the current frame
    
        @type  value: int/float
        @param value: the desired frame
        @type  kw: dictionary
        @param kw: dictionary of arg options                       
        """
        pass

    def frameAdvanced(self,doc=None,duration=None,display=False,cb=None,**kw):
        """
        Play frame for a specifiy duration with/without display and with/without a callbac
    
        @type  doc: document/scene
        @param doc: the desired scene
        @type  duration: float
        @param duration: how long shoud we play
        @type  display: bool
        @param display: toggle the update of the viewport
        @type  cb: function
        @param cb: the callback function to execute at every frame
        @type  kw: dictionary
        @param kw: dictionary of arg options                       
        """

        
    def animationStart(self,doc= None,forward=True,duration = None,**kw):
        """
        Play frame for a specifiy duration 
    
        @type  doc: document/scene
        @param doc: the desired scene
        @type  duration: float
        @param duration: how long shoud we play
        @type  forward: bool
        @param forward: toggle the direction of the animation
        @type  kw: dictionary
        @param kw: dictionary of arg options                       
        """
        
    def animationStop(self,doc=None,**kw):
        """
        Stop the animation
    
        @type  doc: document/scene
        @param doc: the desired scene
        @type  kw: dictionary
        @param kw: dictionary of arg options                       
        """
 #==============================================================================
# Dynamics simulation
#==============================================================================
    def setRigidBody(self,obj,shape="auto",child=False,
                    dynamicsBody="on", dynamicsLinearDamp = 0.0, 
                    dynamicsAngularDamp=0.0, 
                    massClamp = 0.0, rotMassClamp=1.0,**kw):
        """
        Set the curren objec as a rigid body
    
        @type  doc: document/scene
        @param doc: the desired scene
        @type  kw: dictionary
        @param kw: dictionary of arg options                       
        """
        pass
        return None
        
    def setSoftBody(self,obj,**kw):
        """
        Set the curren object as a soft body
    
        @type  doc: document/scene
        @param doc: the desired scene
        @type  kw: dictionary
        @param kw: dictionary of arg options                       
        """
        pass
        return None

    def updateSpring(self,spring,targetA=None,tragetB=None,
                     rlength=0.0,stifness = 1.,damping = 1.0,**kw):
        """
        Update the spring control
    
        @type  doc: document/scene
        @param doc: the desired scene
        @type  kw: dictionary
        @param kw: dictionary of arg options                       
        """
        pass
        return None

        
    def createSpring(self,name,targetA=None,tragetB=None,
                     rlength=0.0,stifness=1.0,damping = 1.0,parent=None,**kw):
        """
        Create a sprin between two physics objects
    
        @type  doc: document/scene
        @param doc: the desired scene
        @type  kw: dictionary
        @param kw: dictionary of arg options                       
        """
        pass
        return None

    def addConstraint(self,obj,type="spring",target=None,**kw):
        """
        Add a constraint to the  given object
    
        @type  doc: document/scene
        @param doc: the desired scene
        @type  kw: dictionary
        @param kw: dictionary of arg options                       
        """
        pass
        return None


#==============================================================================
# Noise and Fractal 
#==============================================================================
    def get_noise(self,point,ntype,nbasis,dimension=1.0,lacunarity=2.0,offset=1.0,octaves=6,gain=1.0,**kw):
        #multi_fractal(position, H, lacunarity, octaves, noise_basis=noise.types.STDPERLIN)
        #NotePlease use InitFbm() before you use one of the following noise types: 
        #NOISE_ZADA, NOISE_DISPL_VORONOI, NOISE_OBER, NOISE_FBM, NOISE_BUYA.
        return 0.0
#===============================================================================
# depends on PIL    
#===============================================================================
    
    def makeTexture(self,object,filename=None,img=None,colors=None,sizex=0,sizey=0,
                    s=20,draw=True,faces=None,invert=False):
        """
        Experiment for baking faces colors using a PIL image
    
        """

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
        """
        Experiment for baking object colors using a PIL image
    
        """                        
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
        """
        Experiment for baking object colors using UV coordinate and PIL image
    
        """                        
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
        """
        Draw and color a Triangle according a color per corner. 
       
        Interpolate the color as OpenGL will do with per vertex
    
        """        
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
        """
        Draw and color a gradient using either PIL rectangle or point drawing methods
    
        """                
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
        """
        Draw  on the given Texture image accordinge en UV coordinates and colors       
        uv is the 3 vertex coordinate in UV 
    
        """                        
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

    
#==============================================================================
# IO / read/write 3D object, cene file etc
#==============================================================================
    def combineDaeMeshData(self,data):
        vertices=[]
        faces=[]
        vnormal=[]
        for i in range(len(data)):
            v,vn,f=data[i]["mesh"]
            if usenumpy : 
                f = numpy.array(f,int)
                faces.extend((f+len(vertices)).tolist())
            else :
                f = [fa + len(vertices) for fa in f ]
            vertices.extend(v)
            if vn != None:
                vnormal.extend(vn)
        return vertices,vnormal,faces

    
    def read(self,filename,**kw):
        pass
    
    def write(self,listObj,**kw):
        pass

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
        if "mesh" in kw :
            inst_master = kw["mesh"]
            f,v,vn = self.DecomposeMesh(kw["mesh"],edit=False,copy=False,tri=True,
                                    transform=True)
        else :
            inst_master = self.getMasterInstance(ch[0])
            #grabb v,f,n of inst_master
            f,v,vn = self.DecomposeMesh(inst_master,edit=False,copy=False,tri=True,
                                    transform=True)

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
        effect = material.Effect("effect"+iname, [], "phong", 
                                 diffuse=props["color"])
#                                 specular = props["specular_color"])
        mat = material.Material("material"+iname, iname+"_material", effect)
        matnode = scene.MaterialNode("material"+iname, mat, inputs=[])
        collada_xml.effects.append(effect)
        collada_xml.materials.append(mat)
        #the geom
        #invert Z 
        vertzyx = numpy.array(v)# * numpy.array([1,1,-1])
        z,y,x=vertzyx.transpose()
        vertxyz = numpy.vstack([x,y,z]).transpose()* numpy.array([1,1,-1])
        vert_src = source.FloatSource(iname+"_verts-array", vertxyz.flatten(), ('X', 'Y', 'Z'))
        norzyx=numpy.array(vn)
        nz,ny,nx=norzyx.transpose()
        norxyz = numpy.vstack([nx,ny,nz]).transpose()* numpy.array([1,1,-1])
        normal_src = source.FloatSource(iname+"_normals-array", norxyz.flatten(), ('X', 'Y', 'Z'))
        geom = geometry.Geometry(collada_xml, "geometry"+iname, iname, [vert_src, normal_src])
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
            master_geomnode = scene.GeometryNode(geom, [matnode])
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
            s=scene.ScaleTransform(scale[0],scale[1],scale[2])
            #n = scene.NodeNode(master_node,transforms=[tr,rz,ry,rx,s])
#            gnode = scene.Node(self.getName(c)+"_inst", children=[geomnode,])
            n = scene.Node(self.getName(c), children=[gnode,],transforms=[tr,rz,ry,rx,s]) #scene.MatrixTransform(matrix)[scene.MatrixTransform(numpy.array(matrix).reshape(16,))]
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
            collada_xml.scene.append(master_node)
        return collada_xml
        
    #DejaVu.indexedPolygon have also this function
    def writeMeshToFile(self,filename,verts=None,faces=None,vnorms=[],fnorms=[]):
        """
        Write the given mesh data (vertices, faces, normal, face normal) in the DejaVu format.
        Create two files : filename.indpolvert and filename.indpolface 
        
        @type  filename: string
        @param filename: the destinaon filename.      
        @type  verts: list
        @param verts: the liste of vertices
        @type  faces: list
        @param faces: the liste of faces
        @type  vnorms: list
        @param vnorms: the liste of vertices normal      
        @type  fnorms: list
        @param fnorms: the liste of faces normal
        
        """                
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
        """
        Given the DejaVu filename return the mesh data (vertices, faces, normal).
        
        Parse two files : filename.indpolvert and filename.indpolface 
        
        @type  filename: string
        @param filename: the destinaon filename.
        
        @rtype  :list
        @return : the liste of vertices,faces and normals
        
        """                        
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
        """
        Write the given polygon mesh data (vertices, faces, normal, face normal) in the DejaVu format.
        
        Create two files : filename.indpolvert and filename.indpolface. 
        
        See writeMeshToFile
        
        @type  polygon: hostObj/hostMesh/String
        @param polygon: the polygon to export in DejaVu format
        @type  filename: string
        @param filename: the destinaon filename.      
        """
        print(polygon,self.getName(polygon))
        #get shild ?
        
        faces,vertices,vnormals,fnormals = self.DecomposeMesh(self.getMesh(polygon),
                                                edit=False,copy=False,tri=True,transform=True,fn=True)
        self.writeMeshToFile(filename,verts=vertices,faces=faces,
                             vnorms=vnormals,fnorms=fnormals)
    @classmethod
    def writeDX(self,filename,gridvalue,gridcenter,gridstep,grisize,commens="")  :     
        nx,ny,nz= grisize
        ox,oy,oz = gridcenter
        sx,sy,sz = gridstep
        N = nx*ny*nz
        aStr="#Data frm upy\n"
        aStr+="#%s\n" % commens
        aStr+="object 1 class gridpositions counts %i %i %i\n" % (nx,ny,nz)
        aStr+="origin %f %f %f\n" % (ox,oy,oz)
        aStr+="delta %f 0.000000e+00 0.000000e+00\n" % sx
        aStr+="delta 0.000000e+00 %f 0.000000e+00\n" % sy
        aStr+="delta 0.000000e+00 0.000000e+00 %f\n" % sz
        aStr+="object 2 class gridconnections counts %i %i %i\n" % (nx,ny,nz)
        aStr+="object 3 class array type double rank 0 items %i data follows\n" % N
        #u(*,*,*)
        #The data values, ordered with the z-index increasing most quickly, followed by the y-index, and then the x-index. 
        counterLine=0
        counter=0
        v=""
        for x in range(nx):
            for y in range(ny):
                for z in range(nz):                    
                    v+="%f " % gridvalue[counter]
                    counter+=1
                    counterLine+=1
                    if counterLine == 2 :
                        aStr+=v+"\n"
                        counterLine = 0
        f = open(filename,"w")
        f.write(aStr)
        f.close()
#==============================================================================
# raycasting RAPID? python ?
#==============================================================================
    def raycast(self,obj,point, direction, length, **kw ):
        intersect = False
        if "count" in kw :
            return intersect,0
        if "fnormal" in kw:
            return intersect,[0,0,0]
        if "hitpos" in kw:
            return intersect,[0,0,0]           
        return intersect
        
        
        
