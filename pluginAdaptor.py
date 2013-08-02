# -*- coding: utf-8 -*-
"""
Created on Mon Mar 19 11:32:26 2012

@author: Ludovic Autin
"""

class pluginAdaptor:
    """
    The Plug-in abstract Layer
    ==========================
    This is the main class from which all plugin will derived. The Plugin Class 
    give access to the initialisatio and registratio of plugin for the host.
    
    It currently does not support procedural, and attribute assignement. 
    But with combination of the helper and the uiADaptor, we should be able to provide it in
    the futur.
    
    >>> PLUGIN_ID = 1027431
    >>> import upy
    >>> plugTypeClass,operatorHostClass = upy.getPluginClass(plug="command")
    >>> class MyPlugin(plugTypeClass):
    >>>    plugin_name = "myPlugin"
    >>>    plugin_tooltip= "a general plugin"
    >>>    plugin_id =  PLUGIN_ID
    >>>    def runCommands(self):
    >>>        #put here what should do the plugin. i.e. open a dialog windows
    >>>        #or create some objects...       
    >>>        pass    
    >>>plug = MyPlugin()
    >>>if "__res__" in locals() :
    >>>    plug.register(epmv_Dialog,Object=plug,res=__res__)#add menuadd={"head":None} to add an access to the plugin in Blender
    >>>else :
    >>>    plug.register(epmv_Dialog,Object=plug)
    >>>#do no touch the following lines required by Blender and Maya    
    >>>#Blender Function
    >>>def register():
    >>>    print (__name__)
    >>>def unregister():
    >>>    pass
    >>>
    >>>#Maya function
    >>>def initializePlugin(mobject):
    >>>    pass
    >>>def uninitializePlugin(mobject):
    >>>    pass

    See examples in upy/examples

    """ 
    host = ""
    
    def __init__(self,**kw):
        if "pluginId" in kw :
            self.setId(kw["pluginId"])
        if not hasattr(self,"plugin_name"):
            self.plugin_name = "MyPlugin"
        if "name" in kw :
            self.plugin_name = kw["name"]
        if "plugin_dir" in kw :
            self.plugin_dir = kw["plugin_dir"]
        else :
            self.plugin_dir = self.plugin_name
        if not hasattr(self,"plugin_icon"):
            self.plugin_icon = "PLUG"
        if "icon" in kw :
            self.plugin_icon = kw["icon"]
        if not hasattr(self,"plugin_tooltip"):
            self.plugin_tooltip = "MyPlugin description"
        if "tooltip" in kw :
            self.plugin_tooltip = kw["tooltip"]
        if not hasattr(self,"hasGui"):
            self.hasGui = False
        if "hasGui" in kw :
            self.hasGui = kw["hasGui"]
        if not hasattr(self,"gui"):
            self.gui = None
        self.setup()
        
    def setId(self,ID=None) :
        """ 
        set the ID of the plugin 
        """
        self.plugin_id = ID            
    def register(self,*args,**kw):
        """ 
        Register the plugin  using an instance and the class Object
        
        *overwrite by host specific module
        """
        pass
    def unregister(self):
        """ 
        UnRegister the plugin  using an instance and the class Object
        
        *overwrite by host specific module

        """
        pass
    def getType(self):
        """ 
        Get the type of the module
        
        *overwrite by host specific module

        """
        pass
    def setRunCommands(self):
        pass
    def runCommands(self):
        pass
    def setup(self):
        pass
    def setgui(self,dname):
        pass
    def resetgui(self,dname):
        pass
    def execute(self):
        pass
    def setIcon(self,*args,**kw):
        pass