import upy
import math
from random import random
helper = upy.getHelperClass()()
Y=0
basic = helper.newEmpty("BasicObject",location=[0.,Y,0.])
s,ms = helper.Sphere("sphere",radius=2.0,res=12,pos = [4.,Y,0.],parent=basic)
tetra,mtetra = helper.Platonic("Tetra","tetra",2.0,parent=basic)
helper.setTranslation(tetra,[ -8.0, Y,0.])
inst = helper.newInstance("instanceOfIco",basic,location=[ -8.0, Y,0.])
v,f,n = helper.tetrahedron(5.0)
for i,v in enumerate(v):
    instsph = helper.newInstance("instOfTetra"+str(i),s,location=v,parent = basic)
    helper.scaleObj(instsph,[ 0.1, 0.1,0.1])

listM = []
for i in range(len(v)):
        m = helper.rotation_matrix(random()*math.pi, [random(),random(),random()],trans=v[i])
    listM.append(m)
ax=[0.,1.,0.]
o,m=helper.matrixToFacesMesh("quad",listM,vector=ax,transpose=False)

#ipoly = helper.instancePolygon("instOfTetra", matrices=listM, mesh=tetra,parent = basic,transpose = False)
#helper.setTranslation(itetra,[ 6.0, -14,0.])#?