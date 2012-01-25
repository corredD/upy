# -*- coding: utf-8 -*-
"""
Created on Sat Feb 26 11:39:17 2011

@author: -
"""
MGL_ROOT="/Library/MGLTools/1.5.6.up"
import sys,os
import math
#pyubic have to be in the pythonpath, if not add it
pyubicpath = "/Library/MGLTools/1.5.6.up/MGLToolsPckgs"
sys.path.append("/Library/MGLTools/dpdtPckgs")
sys.path.append(pyubicpath)
import pyubic

from pyubic.examples import simpleButtons
mg = simpleButtons.myGui()
helper = pyubic.getHelperClass()()
verts = [
                (0, -1 / math.sqrt(3),0),
                (0.5, 1 / (2 * math.sqrt(3)), 0),
                (-0.5, 1 / (2 * math.sqrt(3)), 0),
                (0, 0, math.sqrt(2 / 3)),
                ]
#faces = [[0, 1, 2], [0, 1, 3], [1, 2, 3], [2, 0, 3]]   
hou.helper = helper
from mglutil.util.recentFiles import RecentFiles
from Pmv import moleculeViewer
mv = moleculeViewer.MoleculeViewer(logMode = 'overwrite', customizer=None,master=None,title='pmv', 
                    withShell= 0,verbose=False, gui = False)
hou.mv = mv
rcFile = mv.rcFolder
if rcFile:
    rcFile += os.sep + 'Pmv' + os.sep + "recent.pkl"
    mv.recentFiles = RecentFiles(mv, None, filePath=rcFile,index=0)
else :
    print "no rcFolder??"
#mol = mv.fetch("1crn")
import DejaVu
DejaVu.enableVertexArray = False
mol = mv.readMolecule("/Users/ludo/.mgltools/1.5.6rc1/pdbcache/1crn.pdb")
mv.computeMSMS(mol)
g = mol.geomContainer[0].geoms["MSMS-MOL"] #???
mv.colorByAtomType(mol,[g.name])
colors = mol.geomContainer[0].getGeomColor(g.name)
obj,mesh=helper.createsNmesh("1crnMSMS",g.getVertices(),None,g.getFaces(),color=colors)
mv.computeMSMS(mol,pRadius = 0.5)
mv.colorByAtomType(mol,[g.name])
colors = mol.geomContainer[0].getGeomColor(g.name)
helper.updateMesh("1crnMSMS",vertices=g.getVertices(),faces = g.getFaces(),colors=colors)

fname = "/Library/MGLTools/1.5.6.up/MGLToolsPckgs/pyubic/myGui.ui"
d = hou.ui.createDialog(fname)
import math
MGL_ROOT="/Library/MGLTools/1.5.6.up"
import sys,os
import math
#pyubic have to be in the pythonpath, if not add it
pyubicpath = "/Library/MGLTools/1.5.6.up/MGLToolsPckgs"
sys.path.append("/Library/MGLTools/dpdtPckgs")
sys.path.append(pyubicpath)
import pyubic
helper = pyubic.getHelperClass()()
hou.helper = helper
verts = [
                (0, 10.,0),
                (10., 10., 0),
                (0, 10. , 10.),
                (0, 0, 10.),
                ]
radii = range(1,len(verts)+1)
pesph=helper.newEmpty("base_sphere")
bsph=helper.Sphere("sphere")
helper.reParent(bsph,pesph)
parent=helper.newEmpty("spheres")
sphs=helper.instancesSphere("spheres",verts,radii,pesph,[(1.,0.,.0)],parent)


obj,mesh=helper.createsNmesh("test",verts,None,None,color=None)