
"""
    Copyright (C) <2010>  Autin L. TSRI
    
    This file git_upy/houdini/houdiniAdaptor.py is part of upy.

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
"""


from ePMV.epmvAdaptor import epmvAdaptor
import pyubic.houdini.houdiniHelper as houdiniHelper
import DejaVu

class houdiniAdaptor(epmvAdaptor):
    
    def __init__(self,mv=None,debug=0):
        #before editing need to change DejaVu option VBO
        DejaVu.enableVertexArray = False
        epmvAdaptor.__init__(self,mv,host='houdini',debug=debug)
        self.soft = 'houdini'
        self.helper = houdiniHelper
        #scene and object helper function
        self._getCurrentScene = houdiniHelper.getCurrentScene
        self._addObjToGeom = houdiniHelper.addObjToGeom
        self._host_update = houdiniHelper.update
        self._getObjectName = houdiniHelper.getObjectName
        self._parseObjectName = houdiniHelper.parseObjectName
        self._getObject = houdiniHelper.getObject
        self._addObjectToScene = houdiniHelper.addObjectToScene
        self._toggleDisplay = houdiniHelper.toggleDisplay
        self._newEmpty = houdiniHelper.newEmpty 
        #camera and lighting
        self._addCameraToScene = houdiniHelper.addCameraToScene
        self._addLampToScene = houdiniHelper.addLampToScene        
        #display helper function
        self._editLines = houdiniHelper.editLines
        self._createBaseSphere = houdiniHelper.createBaseSphere
        self._instancesAtomsSphere = houdiniHelper.instancesAtomsSphere
        self._Tube = houdiniHelper.Tube
        self._createsNmesh = houdiniHelper.createsNmesh
        self._PointCloudObject = houdiniHelper.PointCloudObject
        #modify/update geom helper function
        self._updateSphereMesh = houdiniHelper.updateSphereMesh
        self._updateSphereObj = houdiniHelper.updateSphereObj
        self._updateSphereObjs = None#houdiniHelper.updateSphereObjs
        self._updateTubeMesh = houdiniHelper.updateTubeMesh
        self._updateTubeObj = houdiniHelper.updateTubeObj
        self._updateMesh = houdiniHelper.updateMesh
        #color helper function
        self._changeColor = houdiniHelper.changeColor
        self._checkChangeMaterial = houdiniHelper.checkChangeMaterial
        self._changeSticksColor = houdiniHelper.changeSticksColor
        self._checkChangeStickMaterial = houdiniHelper.checkChangeStickMaterial
        #overwrite the general option
        self.use_progressBar = False
        self.doCloud = False

    def _resetProgressBar(self,max):
        return
        
    def _progressBar(self,progress,label):
        return
        
    def _makeRibbon(self,name,coords,shape=None,spline=None,parent=None):
        sc=self._getCurrentScene()
        if shape is None :
            # create full circle at origin on the x-y plane
            #return obj (Circle) and makenurbeCircle but not the CircleShape
            shape = "CircleShape"
        if spline is None :
            obSpline,spline = self.helper.spline(name,coords,extrude_obj=shape,scene=sc)
        return obSpline
