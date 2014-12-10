# -*- coding: utf-8 -*-
"""
Created on Wed Dec  3 22:08:01 2014

@author: ludo
"""
MAYA=False
import sys
if MAYA:
    sys.path.append("/Users/ludo/Library/Preferences/Autodesk/maya/2015-x64/plug-ins/MGLToolsPckgs")
    sys.path.append("/Users/ludo/Library/Preferences/Autodesk/maya/2015-x64/plug-ins/MGLToolsPckgs/PIL")
    #maya standalone special
    import maya.standalone
    maya.standalone.initialize()
    #load plugin
    import maya
    maya.cmds.loadPlugin("fbxmaya")

import upy
helper = upy.getHelperClass()()
if MAYA:
    helper.read("/Users/ludo/DEV/autopack_git/autoPACK_database_1.0.0/geometries/HIV1_capsid_3j3q_Rep_Maker_0_1_0.fbx")
from collada import scene
node = scene.Node("HIV1_capside_3j3q_Rep_Med")
parent_object=helper.getObject("Pentamers")
mesh=None
if MAYA:
    mesh=helper.getObject("HIV1_capsid_3j3q_Rep_Med_Pent_0_1_0_1")
collada_xml=helper.instancesToCollada(parent_object,collada_xml=None,instance_node=True,parent_node=node,mesh=mesh)
parent_object=helper.getObject("Hexamers")
mesh=None
if MAYA:
    mesh=helper.getObject("HIV1_capsid_3j3q_Rep_Med_0_1_0")
collada_xml=helper.instancesToCollada(parent_object,collada_xml=collada_xml,instance_node=True,parent_node=node,mesh=mesh)
#collada_xml.scene.nodes
collada_xml.write("/Users/ludo/DEV/autopack_git/autoPACK_database_1.0.0/geometries/HIV1_capside_3j3q_Rep_Med_0_2_1.dae")
#execfile("/Users/ludo/DEV/git_upy/examples/export_collada.py")
#import upy
#helper = upy.getHelperClass()()
#helper.read("/Users/ludo/DEV/autopack_git/autoPACK_database_1.0.0/geometries/HIV1_capside_3j3q_Rep_Med_0_2_1.dae")
#