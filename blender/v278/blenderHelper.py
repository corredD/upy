
"""
    Copyright (C) <2010>  Autin L. TSRI

    This file git_upy/blender/v271/blenderHelper.py is part of upy.

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
import sys
import os
import struct
import math
from math import *
import string
import copy
import gzip
import types

import bpy
from bpy import *

import bmesh

import mathutils
try :
    import noise
except :
    from mathutils import noise

#import numpy #still need to deal with numpy
from upy import hostHelper
#from upy.hostHelper import Helper
from upy.blender.v271.blenderHelper import blenderHelper as Helper
if hostHelper.usenumpy:
    import numpy


class FrameCallBack:
    def __init__(self,cb):
        self.cb=cb
    def doit(self,scene):
        self.cb(scene.frame_current)

class blenderHelper(Helper):
    """
    The blender helper abstract class
    ============================
        This is the blend er helper Object. The helper
        give access to the basic function need for create and edit a host 3d object and scene.
    """
    render = "BLENDER"

    def __init__(self,master=None,**kw):
        Helper.__init__(self,**kw)
        #setup metric unit to centimeter?
        sc=bpy.context.scene
        sc.unit_settings.system = 'METRIC'
        sc.unit_settings.scale_length = 0.01 #centimeter
        sv3d = self.getSpaceView3D()
        sv3d.cursor_location = [0,0,0]
        sv3d.grid_scale = 0.1
        print ("blender unit setup")
        self.setViewport(clipstart=0.001,clipend=10000,shader="solid")
        self.render = bpy.context.scene.render.engine

#==============================================================================
# raycasing
#==============================================================================
    def raycast(self, obj, point, direction, length, **kw ):
        obj = self.getObject(obj)
        ray_p = self.FromVec(point)
        ray_dir = self.FromVec(direction)
        p_to_dir = ray_dir - ray_p
        mat = mathutils.Matrix(obj.matrix_world)#copy the matrix
        mat.invert()
        orig = mat*ray_p#
        p_to_dir = mat*p_to_dir
        count = 0
#        r=helper.oneCylinder("ray",[-0.0931, -0.0578, 0.0336],[0.9315, -0.3362, -10.5780],radiu=0.5)
        while True:
            results = obj.ray_cast(orig,p_to_dir*length) #bool,point,normal,indice
            if not results[0]:#index == -1:
                #no intersection
                intersect = False
                break
            count += 1
            orig = results[1] + p_to_dir*0.00001
        if "count" in kw :
            #print (intersect,count)
            return intersect,count
        return intersect
