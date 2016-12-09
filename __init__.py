
"""
    Copyright (C) <2010>  Autin L. TSRI
    
    This file git_upy/__init__.py is part of upy.

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

    This is the main uPy module initialisation
    
    >>> import upy
    >>> hClass = upy.getHelperClass()
    >>> helper = hClass()
    >>> upy.setUIClass()
    >>> from upy import uiadaptor
    
    See examples in upy/examples
    
"""
import os
import sys
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning) 

uiadaptor = None
helper = None
host = None
if not os.path.isfile(os.path.abspath(__path__[0])+os.sep+"version.txt"):
    f=open(os.path.abspath(__path__[0])+os.sep+"version.txt","w")
    f.write("0.0.0")
    f.close()
f = open(os.path.abspath(__path__[0])+os.sep+"version.txt","r")
__version__ = f.readline()#"0.6.304"
f.close()

def getExecutable():
    host = retrieveHost()
    path_to_exe = "python"
    if host  == "c4d":
        if sys.platform == "win32":
            path_to_exe = os.path.dirname(sys.executable)+os.sep+"resource"+os.sep+"modules"+os.sep+"python"+os.sep+"Python.win64.framework"+os.sep+"python.exe"
        #mac?
    elif host == 'blender25':
        path_to_exe = sys.executable
    elif host == 'maya':
        path_to_exe = "python"
    elif host == 'maya':
        path_to_exe = "python"     
    return path_to_exe
       
def retrieveHost():
    """
    Retrieve the 3d host application where the script is running.

    @rtype:   string
    @return:  the name of the host, ie blender, maya or c4d
    """
    global host
    host=''
    try :
        import c4d
        host = 'c4d'
    except :
        try :
            import MaxPlus
            host = '3dsmax'
        except:
            try :
                import Blender
                host = 'blender24'
                #Text->Open->Execute Python Script
            except:
                try :
                    import bpy
                    host = 'blender25'
                    #Text->Open->Execute Python Script
                except:              
                    try :
                        import hou
                        host = 'houdini'
                        #Text->Open->Execute Python Script
                    except:
                        try :
                            import siutils
                            host = 'softimage'
                        except:  
                            try :
                                import maya
                                host = 'maya'
                            except:
                                try :
                                    import chimera
                                    host = 'chimera'
                                except :                      
                                    try :
                                        import DejaVu
                                        host = 'dejavu'
                                    except :
                                        print('host not supported')
    return host

def getUClass(host,pref=None):
    """
    Return the base class for UI design according the provide host.
        
    @type  host: string
    @param host: name of the host application
    @type  pref: string
    @param pref: UI interface prefernce for instance qt
    
    @rtype:   Class
    @return:  the specific ui class
    """         
    if host == 'blender24':
        #check version
#        from pyubic.blender.blenderUI import blenderUIDialog as adaptor
        from upy.blender.v249.blenderUI import blenderUIDialog as adaptor
    elif host == 'blender25':
        import bpy
        blender_version = bpy.app.version
        if blender_version < (2,60,0):
            from upy.blender.v257.blenderUI import blenderUIDialog as adaptor
        elif blender_version >= (2,60,0) and blender_version < (2,63,0): #2.62
            from upy.blender.v262.blenderUI import blenderUIDialog as adaptor
        elif blender_version >= (2,63,0) and blender_version < (2,71,0): #2.63 and more
            from upy.blender.v263.blenderUI import blenderUIDialog as adaptor
        elif blender_version >= (2,71,0): #2.63 and more
            from upy.blender.v271.blenderUI import blenderUIDialog as adaptor
        else :
            print (blender_version,blender_version < (2,60,0))
    elif host=='c4d':
        import c4d
        c4d_version = c4d.GetC4DVersion()
        if c4d_version > 12000 and c4d_version < 13000 :
            from upy.cinema4d.r12.c4dUI import c4dUIDialog as adaptor
        elif c4d_version > 13000  and c4d_version < 14000:
            from upy.cinema4d.r13.c4dUI import c4dUIDialog as adaptor
        elif c4d_version > 14000:
            from upy.cinema4d.r14.c4dUI import c4dUIDialog as adaptor
    elif host=='maya':
        from upy.autodeskmaya.mayaUI import mayaUIDialog as adaptor
    elif host=='softimage':
        from  siutils import si
        Application = si()
        if type(Application) == unicode :
            import sipyutils
            Application = sipyutils.si()
        v = Application.version()
        if v >= (11,0,525,0):
            #from upy.softimage.v2013.softimageUI import softimageUIDialog as adaptor
            from upy.pythonUI.qtUI import qtUIDialog as adaptor          
    elif host=='3dsmax':
        import MaxPlus
        release = MaxPlus.Core.EvalMAXScript("getDir #maxData").Get()
        #from upy.autodesk3dsmax.v2013.maxUI import maxUIDialog as adaptor
        if release.find("2015") != -1 :
            from upy.autodesk3dsmax.v2015.maxUI import maxUI as adaptor
        elif release.find("2016") != -1 :
            from upy.autodesk3dsmax.v2016.maxUI import maxUI as adaptor            
        else :
            print (release)
            print ("not suppported")
            adaptor = None
    elif host=='dejavu':
        from upy.dejavuTk.dejavuUI import dejavuUIDialog as adaptor
#        print ("ok",adaptor)
    elif host=='houdini':
        if pref is not  None :
            if pref == "qt" :
                from upy.pythonUI.qtUI import qtUIDialog as adaptor        
            else :    
                from upy.houdini.houdiniUI import houdiniUIDialog as adaptor           
##        elif host == 'chimera':
#            from ePMV.Chimera.chimeraUI import chimeraAdaptor as uiadaptor
#        elif host == 'houdini':
#            from ePMV.houdini.houdiniUI import houdiniAdaptor as uiadaptor
    elif host =="qt" :
        from upy.pythonUI.qtUI import qtUIDialog as adaptor
    else :
        adaptor = None
    return adaptor    

def getHClass(host):
    """
    Return the base class for modelling design according the provide host.
        
    @type  host: string
    @param host: name of the host application
    
    @rtype:   Class
    @return:  the specific ui class
    """
    #print globals()
    if host == 'blender24':
        from upy.blender.v249.blenderHelper import blenderHelper as helper
    elif host == 'blender25':
        import bpy
        blender_version = bpy.app.version
        if blender_version < (2,60,0):
            from upy.blender.v257.blenderHelper import blenderHelper as helper
        elif blender_version >= (2,60,0) and blender_version < (2,63,0): #2.62
            from upy.blender.v262.blenderHelper import blenderHelper as helper
        elif blender_version >= (2,63,0) and blender_version < (2,71,0): #2.62
            from upy.blender.v263.blenderHelper import blenderHelper as helper
        elif blender_version >= (2,71,0): #2.62
            from upy.blender.v271.blenderHelper import blenderHelper as helper
        else :
            print (blender_version)
    elif host=='c4d':
        import c4d
        c4d_version = c4d.GetC4DVersion()
        if c4d_version > 12000 and c4d_version < 13000:
            from upy.cinema4d.r12.c4dHelper import c4dHelper as helper
        elif c4d_version > 13000 and c4d_version < 14000:
            from upy.cinema4d.r13.c4dHelper import c4dHelper as helper
        elif c4d_version > 14000:
            from upy.cinema4d.r14.c4dHelper import c4dHelper as helper
    elif host=='maya':
        from upy.autodeskmaya.mayaHelper import mayaHelper as helper
    elif host=='softimage':
        from  siutils import si
        Application = si()               
        if type(Application) == unicode :
            import sipyutils
            Application = sipyutils.si()
        v = Application.version()
        if v >= (11,0,525,0):
            from upy.softimage.v2013.softimageHelper import softimageHelper as helper
    elif host=='3dsmax':
        import MaxPlus
        release = MaxPlus.Core.EvalMAXScript("getDir #maxData").Get()
        #from upy.autodesk3dsmax.v2013.maxUI import maxUIDialog as adaptor
        if release.find("2015") != -1 :
            from upy.autodesk3dsmax.v2015.maxHelper import maxHelper as helper
        elif release.find("2016") != -1 :
            from upy.autodesk3dsmax.v2016.maxHelper import maxHelper as helper   
        else :
            print (release)
            print ("not suppported")
            helper = None        
    elif host=='dejavu':
        from upy.dejavuTk.dejavuHelper import dejavuHelper as helper
    elif host == 'chimera':
        from upy.ucsfchimera.chimeraHelper import chimeraHelper as helper
    elif host == 'houdini': 
        from upy.houdini.houdiniHelper import houdiniHelper as helper
    else :
        helper = None
    return helper    

def getUIClass(host=None):
    """
    Return and define the base class for UI design according the provide host.
    If the host is not provide,retrieveHost() will be called to guess the host.
    
    @type  host: string
    @param host: name of the host application
    
    @rtype:   Class
    @return:  the specific ui class
    """ 
    global uiadaptor   
    if host is None:
        host = retrieveHost()
        print ("getUIClass ",host)
    if host == '' :
        from upy.dejavuTk.dejavuUI import dejavuUIDialog as adaptor
        uiadaptor = adaptor
        return uiadaptor
    uiadaptor = getUClass(host)
    return uiadaptor

def setUIClass(host=None,pref=None):
    """
    Set the base class for UI design according the provide host.
    If the host is not provide,retrieveHost() will be called to guess the host.
    
    @type  host: string
    @param host: name of the host application
    @type  pref: string
    @param pref: UI interface prefernce for instance qt    
    """ 
    global uiadaptor  
    if host is None:
        host = retrieveHost()
    if not host :
        return None
    uiadaptor = getUClass(host,pref=pref)

def getHelperClass(host=None):
    """
    Return the base class for modelling design according the provide host.
    If the host is not provide,retrieveHost() will be called to guess the host.
    
    @type  host: string
    @param host: name of the host application
    
    @rtype:   Class
    @return:  the specific ui class
    """ 
    global helper
    if host is None:
        host = retrieveHost()
    if not host :
        return None
    helper = getHClass(host)
    return helper

def getPClass(host):
    """
    Return the base class for plugin type provided.
        
    @type  host: string
    @param host: name of the host application
    
    @rtype:   Class
    @return:  the specific ui class
    """     
    if host == 'blender24':
        from upy.blender.v249 import blenderPlugin as plugClass
    elif host == 'blender25':
        import bpy
        blender_version = bpy.app.version
        if blender_version < (2,60,0):
            from upy.blender.v257 import blenderPlugin as plugClass
        elif blender_version >= (2,60,0) and blender_version < (2,63,0): #2.62
            from upy.blender.v262 import blenderPlugin as plugClass
        elif blender_version >= (2,63,0) and blender_version < (2,71,0): #2.63
            from upy.blender.v263 import blenderPlugin as plugClass
        elif blender_version >= (2,63,0): #2.63
            from upy.blender.v271 import blenderPlugin as plugClass
        else :
            print (blender_version,blender_version < (2,60,0))
    elif host=='c4d':
        import c4d
        c4d_version = c4d.GetC4DVersion()
        if c4d_version > 12000 and c4d_version < 13000:
            from upy.cinema4d.r12 import c4dPlugin as plugClass
        elif c4d_version > 13000 and c4d_version < 14000:
            from upy.cinema4d.r13 import c4dPlugin as plugClass
        elif c4d_version > 14000:
            from upy.cinema4d.r14 import c4dPlugin as plugClass
    elif host=='maya':
        from upy.autodeskmaya import mayaPlugin as plugClass
    elif host=='softimage':
        from  siutils import si
        Application = si()        
        if type(Application) == unicode :
            import sipyutils
            Application = sipyutils.si()
        v = Application.version()
        if v >= (11,0,525,0) :
            from upy.softimage.v2013 import softimagePlugin as plugClass
    elif host=='3dsmax':
        import MaxPlus
        release = MaxPlus.Core.EvalMAXScript("getDir #maxData").Get()
        #from upy.autodesk3dsmax.v2013.maxUI import maxUIDialog as adaptor
        if release.find("2015") != -1 :
            from upy.autodesk3dsmax.v2015 import maxPlugin as plugClass
        elif release.find("2016") != -1 :
            from upy.autodesk3dsmax.v2016 import maxPlugin as plugClass   
        else :
            print (release)
            print ("not suppported")
            plugClass = None                  
    elif host=='dejavu':
        from upy.dejavuTk import dejavuPlugin as plugClass
    elif host == 'chimera':
        from upy.ucsfchimera import chimeraPlugin as plugClass
    elif host == 'houdini': 
        from upy.houdini import houdiniPlugin as plugClass
    else :
        plugClass = None
    return plugClass    
    
def getPluginClass(host=None,plug = None):
    global pluginType
    if host is None:
        host = retrieveHost()
    if not host :
        return
    pluginType = getPClass(host)
    if plug is not None :
        return pluginType.get(plug)
    else :
        return pluginType.general_plugClass
    
