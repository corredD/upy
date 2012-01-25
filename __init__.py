# -*- coding: utf-8 -*-
"""
Created on Sun Dec  5 23:30:44 2010

@author: Ludovic Autin - ludovic.autin@gmail.com
"""

uiadaptor = None
helper = None
__version__ = "0.5.4"

def retrieveHost():
    """
    Retrieve the 3d host application where the script is running.

    @rtype:   string
    @return:  the name of the host, ie blender, maya or c4d
    """
    
    host=''
    try :
        import c4d
        host = 'c4d'
    except :
        try :
            import maya
            host = 'maya'
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
        #check version
#        from pyubic.blender.blenderUI import blenderUIDialog as adaptor
        from upy.blender.v257.blenderUI import blenderUIDialog as adaptor
    elif host=='c4d':
        from upy.cinema4d.c4dUI import c4dUIDialog as adaptor
    elif host=='maya':
        from upy.autodeskmaya.mayaUI import mayaUIDialog as adaptor
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
    if host == 'blender24':
        from upy.blender.v249.blenderHelper import blenderHelper as helper
    elif host == 'blender25':
        from upy.blender.v257.blenderHelper import blenderHelper as helper
    elif host=='c4d':
        from upy.cinema4d.c4dHelper import c4dHelper as helper
    elif host=='maya':
        from upy.autodeskmaya.mayaHelper import mayaHelper as helper
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
#        print ( host,host=='dejavu')
    if not host :
        return    
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
        return
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
        return
    helper = getHClass(host)
    return helper