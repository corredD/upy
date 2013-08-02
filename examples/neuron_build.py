"""
NeuronBuild | Nick Woolridge | 2013 | n.woolridge@utoronto.ca
version date: March 11 2013
A script to import swc files downloaded from neuromorpho.org, and create accurate
spline-based models of neuronal structure. The original swc file format is detailed here:
Cannon, R.C, Turner, D.A, Pyapali, G.K, Wheal, H.V. An on-line archive of reconstructed
hippocampal neurons. Journal of Neuroscience Methods. 84 1–2. pp 49-54. 1998
The reconstruction units are μm (micrometers).
Note: soma (cell body) definitions vary from file to file; this script assumes a three point spline
(which is very common). The soma object is disabled by default, since they rarely produce acceptable geometry.
Note: use of neuromorpho files may come with an obligation to cite the original publication.

How to use:
- add to your C4D scripts folder (on Mac OS X: Applications/MAXON/CINEMA 4D R14/library/scripts or in the user prefs folder)
- Browse and download a .swc or .swc.txt file from http://neuromorpho.org/
- Open the script manager in C4D, the script should be in the pop-up menu at the top of the window.
- In the Script manager in C4D load the NeuronBuild script and click "Execute".
- An import options dialog should appear; choose options for imported geometry, and click "Import File".
- In the open file dialog, choose the swc file and click "OK".
- A neuron should appear in your viewport.
- If all the geometry options are chosen, the geometry consists of a HyperNURBs object, which contains a Connect object, which 
contains a null object, which contains the sweep objects that define the axons and dendrites. 
Since the Soma (cell body) definition in the swc files is so rudimentary, you may want to 
delete or hide it, and let the soma be defined by the merging dendrite roots. Within the sweep
 objects are n-sided splines (named "Profile") set to 6-sides; you could search for these 
 objects and change the number of sides to 4 to simplify the geometry. Also in the SweepNURBs objects
 are the splines that define the dendrite paths, and rail splines that define their radius.
    
New in 1.4:
    Modifications made by Graham Johnson on March 11, 2013
    – support for Cinema 4D r12 and r13 (Oconnect and AddMultiLineEditText compatibility
    – convert right handed .swc data to Cinema 4D left-handed with coordSystem test
    – added safety test if user hits cancel button while in the system browser. Reports as 'Cancelled in Browser.'
    
This software is open-source under the MIT License.

Copyright (c) 2013 Nicholas Woolridge

Permission is hereby granted, free of charge, to any person obtaining a copy of this
software and associated documentation files (the "Software"), to deal in the Software
without restriction, including without limitation the rights to use, copy, modify, merge,
publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons
to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or
substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE
FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""

#import c4d, os
#from c4d import gui
import upy
import os
#get the ui helper class
upy.setUIClass()
from upy import uiadaptor

#get the helperClass for modeling
helperClass = upy.getHelperClass()

#Welcome to the world of Python

#Create IDs for the GUI elements in the settings dialog
#this is automatic in upy
#DLG_GROUP_1 = 1000
#DLG_GROUP_2 = 1001
#TEXTBOX = 1002
#CANCELBUTTON = 1003
#IMPORTBUTTON = 1004
#HNCHECK = 1005
#CONNECTCHECK = 1006
#RAILCHECK = 1007
#SWEEPCHECK = 1008
#PROFILETEXT = 1009
#PROFILESIDES = 1010

#this is automatic in upy
#coordsystem="left"
#versionNumber=c4d.GetC4DVersion()

#the usual way is :
#make a class that deal with the data
#make a class that deal with the UI

class NeurTools:
    def __init__(self,*args,**kw):
        self.helper = None
        self.data = None
        self.filename = None
        self.name = None
        if "helper" in kw :
            self.helper = kw["helper"]
        else :
            self.helper = helperClass()
        if "filename" in kw :
            self.filename = kw["filename"]
        #need some options 
        self.options = {
            "DoHN":{"name":"DoHN","value":True,"default":True,"type":"bool","description":".....","width":30},
            "DoConnect":{"name":"DoConnect","value":True,"default":True,"type":"bool","description":".....","width":30},
            "DoRail":{"name":"DoRail","value":True,"default":True,"type":"bool","description":".....","width":30},
            "DoSweep":{"name":"DoSweep","value":True,"default":True,"type":"bool","description":".....","width":30},
            "NSides":{"name":"NSides","value":6,"default":6,"type":"int","description":"....","width":30},
        } 
        #create the attributes
        self.resetDefaultOptions()
        if self.filename != None :
            self.readFile(self.filename)
    
    #reset to default options   
    def resetDefaultOptions(self):
        for option in self.options:
            setattr(self,option,self.options[option]["default"])
    
    #set options   
    def setOptions(self,*kw):    
        for k in kw :
            if hasattr(self,k):
                setattr(self,k,kw[k]) 
    
    def somaMake(self,somaLines, neuroFile, fileName):
        """Create splines to make the cell body."""
    
        #reference global variables that set model parameters
        #use the options intead
        #global DoHN, DoConnect, DoRail, DoSweep, NSides
        parent = self.helper.getObject(self.name)
        #create spline
        points = [ [currLine[2],currLine[3],currLine[4]] for currLine in somaLines] 
        Spline,mesh_spline = self.helper.spline("Soma", points,close=0,type=0,parent=parent)#,parent=line)
        if self.DoSweep:
            #default shape is a n-side, not sure why, so will use just a circle
           extruder_spline,shape = self.helper.extrudeSpline(Spline,shape="circle",clone = False) 
           self.helper.reParent(extruder_spline,parent)
#            #create the profile for the sweep This part not covered by upy need to chec what 
#            Profile = c4d.BaseObject(c4d.Osplinenside)
#            Profile[c4d.ID_BASELIST_NAME] = "Profile"
#            Profile[c4d.PRIM_NSIDE_RADIUS] = sRad
#            Profile[c4d.PRIM_NSIDE_SIDES] = NSides
#            doc.InsertObject(Profile)
#            
#            Spline.InsertUnder(Sweep)
#            Profile.InsertUnder(Sweep)
                
    def splineMake(self,splineLines, neuroFile, fileName):
        """Create splines to define the dendrites and axons."""
        
        #reference global variables that set model parameters
        #global DoHN, DoConnect, DoRail, DoSweep, NSides
        parent = self.helper.getObject(self.name)
        shape = None
        #run through the data file, identifying contiguous spline segments. this is possible because
        #the last value in the data refers to the "root" point of that branch segment
        splineSep = [] 
        for n in range(0, len(splineLines)):
            currLine = splineLines[n]
            sIndex = int(currLine[0])  
            sRoot = int(currLine[6])
            if sIndex > sRoot + 1:
                splineSep.append(sIndex)
        
        #now build the spline segments as separate splines
        for n in range(0, len(splineSep)):
            if n < (len(splineSep) - 1):
                
                #determine the offset between segemnts; this is the number of vertices in each spline segment
                offset = splineSep[n+1] - splineSep[n]
                splinePoints=[]
                #create an empty spline
                #Spline = c4d.BaseObject(c4d.Ospline)
                
                #allocate points for the spline
                #Spline.ResizeObject(offset)
                
                #get the data line that starts the segment
                splineStart = neuroFile[splineSep[n]]
                splineType = int(splineStart[1])
                            
                #determine what type of spline it is and name it
                if splineType == 2: 
                    name = "Axon " + str(n)
                elif splineType == 3: 
                    name = "Basal Dendrite " + str(n)
                elif splineType == 4:
                    name = "Apical Dendrite " + str(n)
                    
                #Spline[c4d.ID_BASELIST_NAME] = name
                #Spline[c4d.SPLINEOBJECT_TYPE] = 0
                
                #find the root poiont for this segment by going back to 
                #the line in neuroFile that contains it
                #and then we have to step back one line in the source file
                rootLine = neuroFile[((int(splineStart[6])) - 1)]
                rootRoot = neuroFile[int(rootLine[6]) - 1]
                x, y, z = float(rootRoot[2]), float(rootRoot[3]), float(rootRoot[4])
                splinePoints.append([x,y,z])                
                #rootPos = c4d.Vector(x, y, z)
                #if coordsystem=="left":  #Convert to left-hand for C4D added by GJ March 11, 2013
                #    rootPos = c4d.Vector(x, y, -z)
                #Spline.SetPoint(0, rootPos)
                
                for m in range(1, offset):
                    l = int(splineSep[n]) + (m - 1)
                    currLine = neuroFile[l]
                    
                    #create the variables for positioning the points
                    sx = float(currLine[2])
                    sy = float(currLine[3])
                    sz = float(currLine[4])
                    #if coordsystem=="left":  #Convert to left-hand for C4D added by GJ March 11, 2013
                    #    sz = -sz
                    #radius, not used yet
                    #sRad = float(currLine[5])
                    #pos = c4d.Vector(sx, sy, sz)
                    splinePoints.append([sx, sy, sz]) 
                    #Spline.SetPoint(m, pos)
                Spline,mesh_spline = self.helper.spline(name, splinePoints,close=0,type=0,parent=parent)#
                #create the spline
                #doc.InsertObject(Spline)
                #c4d.EventAdd()
                
                #in order to scale the sweepNURBs object, we create a copy of the spline
                #to act as a rail spline, and then add the radius value to one of the coords
                if self.DoRail:
                    #upy doesnt cover rail,but will look at it.
                    #railSpline = Spline.GetClone()
                    #railSpline[c4d.ID_BASELIST_NAME] = name + " Rail"
                    railPoints=[]
                    #rVector = c4d.Vector((x + (float(rootRoot[5]))), y, z)
                    #if coordsystem == "left":  #Convert to left-hand for C4D added by GJ March 11, 2013
                    #    rVector = c4d.Vector((x + (float(rootRoot[5]))), y, -z)
                    railPoints.append([x + (float(rootRoot[5])), y, z])
                    #railSpline.SetPoint(0, rVector)
                    for m in range(1, offset):
                        l = int(splineSep[n]) + (m - 1)
                        currLine = neuroFile[l]
                        
                        #create the variables for positioning the points
                        sRad = float(currLine[5])
                        #add the radius to the x coord this time
                        sx = (float(currLine[2]) + sRad)
                        sy = float(currLine[3])
                        sz = float(currLine[4])
                        railPoints.append([sx, sy, sz]) 
                        #if coordsystem=="left":  #Convert to left-hand for C4D added by GJ March 11, 2013
                        #   sz = -sz
                        #radius, not used yet
        
                        #pos = c4d.Vector(sx, sy, sz)
                        #railSpline.SetPoint(m, pos)
                    RailSpline,mesh_spline = self.helper.spline(name + "_Rail", railPoints,close=0,type=0,parent=parent)#
                    #doc.InsertObject(railSpline) 
                    #c4d.EventAdd()   
                
                #create the sweep object
                if self.DoSweep:
                    #again the rail/sweep is advance in this script, need to check what it does
                    #and see if feasible in other host
                    extruder_spline,shape = self.helper.extrudeSpline(Spline,shape="circle",clone = False) 
                    self.helper.reParent(extruder_spline,parent)
#                    Sweep = c4d.BaseObject(c4d.Osweep)
#                    Sweep[c4d.ID_BASELIST_NAME] = name
#                    #the seep object needs to have two default settings disabled
#                    Sweep[c4d.SWEEPOBJECT_CONSTANT] = False
#                    Sweep[c4d.SWEEPOBJECT_RAILDIRECTION] = False
#                    Sweep[c4d.CAP_TYPE] = 1
#                    Sweep.SetPhong(True, True, 80)
#        
#                    #create the profile for the sweep
#                    Profile = c4d.BaseObject(c4d.Osplinenside)
#                    Profile[c4d.ID_BASELIST_NAME] = "Profile"
#                    Profile[c4d.PRIM_NSIDE_RADIUS] = sRad
#                    Profile[c4d.PRIM_NSIDE_SIDES] = NSides
#                    doc.InsertObject(Profile)
                
                #insert the splines as children of the sweepNURBs object, in the correct order
                if self.DoRail == True:
                    if self.DoSweep == True:
                        #probably only for C4D
                        self.helper.reParent(RailSpline,extruder_spline)
                        self.helper.reParent(Spline,extruder_spline)
                        self.helper.reParent(shape,extruder_spline)
#                        railSpline.InsertUnder(shape)
#                if DoSweep == True:
#                    Spline.InsertUnder(Sweep)
#                    Profile.InsertUnder(Sweep)
                
                #add undo for spline creation
#                doc.AddUndo(c4d.UNDOTYPE_NEW, Spline)
                
                #insert the spline under the null object
#                if DoSweep == True:
#                    parent = doc.SearchObject(fileName)
#                    Sweep.InsertUnder(parent)
    
#                c4d.EventAdd()
    
    def readFile(self,path):
        """Access the neuromorpho swc file, strip comments, and load it into the neuroFile nested list. """
    
        #reference global variables that set model parameters
        #global DoHN, DoConnect, DoRail, DoSweep
        
        neuroFile = []
        somaLines = []
        splineLines = []
        
        #Get the name of the file and split off the last file extension
        filePath = os.path.basename(path)
        fileName = os.path.splitext(filePath)[0]
        
        #here we read the file, and create two sub lists: one for the soma, and one for the axons and dendrites
        for line in open(path):
            # ignore lines that are comments
            if line.startswith('#'):
                pass
            else:
                # create nested list of data
                 x = [value for value in line.split()]
                 neuroFile.append(x) 
                 #create 
                 if x[1] == "1":
                     somaLines.append(x)
                 else:
                     splineLines.append(x)
    
        #the numlines variable stores the length of the data files (number of points)
        numLines = len(neuroFile)
        self.filename = path
        self.name = fileName
        #create null to contain splines
        Null = self.helper.newEmpty(fileName)#the main parent
#        Null = c4d.BaseObject(c4d.Onull)
#        Null[c4d.ID_BASELIST_NAME] = fileName
#        #insert the null in the scene
#        doc.InsertObject(Null)
#        #add undo for null creation
#        doc.AddUndo(c4d.UNDOTYPE_NEW, Null)
#        c4d.EventAdd()
        
        #call the functions that build the soma and other splines
        self.somaMake(somaLines, neuroFile, fileName)
        self.splineMake(splineLines, neuroFile, fileName)
        
        #create connect object
        if self.DoConnect == True:
            pass
#            if versionNumber >= 14000:
#                Connect = c4d.BaseObject(c4d.Oconnector)
#                Connect[c4d.ID_BASELIST_NAME] = fileName
#                #insert the connector in the scene
#                doc.InsertObject(Connect)
#            else:
#                c4d.CallCommand(1011010)
#                Connect = doc.SearchObject("Connect")
#            if Connect:
#                #add undo for Connect creation
#                doc.AddUndo(c4d.UNDOTYPE_NEW, Connect)
#                c4d.EventAdd()
#    
#                Null.InsertUnder(Connect)
        
        #create HN object
        if self.DoHN == True:
            pass
#            HN = c4d.BaseObject(c4d.Osds)   
#            HN[c4d.ID_BASELIST_NAME] = fileName
#            #insert the HyperNURBs in the scene
#            doc.InsertObject(HN)
#            #add undo for HN creation
#            doc.AddUndo(c4d.UNDOTYPE_NEW, HN)
#            c4d.EventAdd()
#            
#            if DoConnect == True: 
#                Connect.InsertUnder(HN)
#            else:
#                Null.InsertUnder(HN)
        
        #close out the undo stack
#        doc.EndUndo()
        
#now th gui
class NeuroToolsGUI(uiadaptor):
    
    def setup(self,*args,**kw):
        #get the helper
        self.helper = None
        if "helper" in kw :
            self.helper = kw["helper"]
        else :
            self.helper = helperClass()
        #could have a list of NeurTools
        self.ntool=NeurTools(helper=self.helper)
        #dont want to dock it ie maya 
        self.dock = False
        #boolean statut of synchronization
        self.synchronized = False
        self.w=240
        self.h=290
        #initialize widget and layout
        self.initWidget()        
        self.setupLayout()        
        
    #dont touch theses two functions specific for c4d
    def CreateLayout(self):
        self._createLayout()
        return 1
    def Command(self,*args):
#        print args
        self._command(args)
        return 1

    def initWidget(self,id=None):
        #need widget for all options
        self.Widget={}
        self.Widget["labeloptions"]={}
        self.Widget["options"]={}
        self.listAttrOrdered=["DoHN", "DoConnect", "DoRail", "DoSweep", "NSides"]
        dic={"int":"inputInt","float":"inputFloat","bool":"checkbox","liste":"pullMenu","filename":"inputStr"}
        dic2={"int":"int","float":"float","bool":"int","liste":"int","filename":"str"}  
        for option in self.listAttrOrdered:#sqelf.histoVol.OPTIONS:
            o = self.ntool.options[option]
            if o["type"] == "liste": 
                v = o["values"]
            else : 
                v = o["value"]            
            self.Widget["labeloptions"][option] = self._addElemt(name=o["name"]+"Label",label=o["description"],width=120)
            self.Widget["options"][option] = self._addElemt(name=o["name"],value=v,
                                    width=200,height=10,action=None,
                                    variable=self.addVariable(dic2[o["type"]],v),
                                    type=dic[o["type"]])
        #additional widget
        txt = "The NeuronBuild script imports accurate neuromorpho SWC files \n"\
            "and creates spline-based geometry (scale assumes µm as world unit). \nChoose modeling options below;\n" \
            "if all boxes are unchecked, \nonly the base splines will be added to the scene.\n"
        #c4d.DR_MULTILINE_READONLY|c4d.DR_MULTILINE_WORDWRAP not in upy
        self.area = self._addElemt(id=id,name="TextArea",action=None,width=100,
                          value=txt,type="inputStrArea",
                          variable=self.addVariable("str",txt),height=300)
        self.BTN = {
            "Load":self._addElemt(name="browse",width=80,height=10,
                                      action=self.LoadFile,type="button",icon=None),
            "Close" : self._addElemt(name="close",width=80,height=10,
                                     action=self.close,type="button",icon=None),
                    }      
    
    def setupLayout(self,):
        #arrange widget
        self._layout=[]
        self._layout.append([self.area])
        for option in self.listAttrOrdered:
            self._layout.append([self.Widget["labeloptions"][option],self.Widget["options"][option]] )
        self._layout.append([self.BTN["Load"],self.BTN["Close"]])

    def LoadFile_cb(self,filename):
        print (filename)
        self.ntool.readFile(filename)
    
    def LoadFile(self,*args):
        self.fileDialog(label="choose a .swc file",callback=self.LoadFile_cb)

        
#class SettingsDlg(gui.GeDialog):
#    
#    def __init__(self, title=None, input_text=None):
#        self.title = title or "User Input"
#        self.input_text = input_text or ""
#        self.result = None
#
#    def CreateLayout(self):
#        self.SetTitle("NeuronBuild")
#        #creat the layout of the dialog
#        self.GroupBegin(DLG_GROUP_1, flags=c4d.BFH_SCALEFIT|c4d.BFV_SCALEFIT, cols=1, rows=7, title="NeuronBuild", groupflags=5)
#        self.GroupBorderSpace(10, 10, 10, 10)
#        
#        #add multiline edit box for script description
#        if versionNumber >= 13000:
#            self.AddMultiLineEditText(TEXTBOX, flags=c4d.BFH_CENTER|c4d.BFV_TOP, inith=100, initw=300, style=c4d.DR_MULTILINE_READONLY|c4d.DR_MULTILINE_WORDWRAP)
#        else:
#            self.AddMultiLineEditText(TEXTBOX, flags=c4d.BFH_CENTER|c4d.BFV_TOP, inith=100, initw=300)
##            self.AddStaticText(TEXTBOX, flags=c4d.BFH_CENTER|c4d.BFV_TOP, inith=100, initw=300, borderstyle=1)
#        
#        #add check boxes for various construction options
#        self.AddCheckbox(HNCHECK, flags=c4d.BFH_LEFT, initw=300, inith=0, name="Add HyperNURBs object")
#        self.SetBool(HNCHECK, True)
#         
#        self.AddCheckbox(CONNECTCHECK, flags=c4d.BFH_LEFT, initw=300, inith=0, name="Add Connect object")
#        self.SetBool(CONNECTCHECK, True)
#        
#        self.AddCheckbox(RAILCHECK, flags=c4d.BFH_LEFT, initw=300, inith=0, name="Add rail splines (controls thickness)")
#        self.SetBool(RAILCHECK, True)
#        
#        self.AddCheckbox(SWEEPCHECK, flags=c4d.BFH_LEFT, initw=300, inith=0, name="Add SweepNURBs object")
#        self.SetBool(SWEEPCHECK, True)
#        
#        self.AddStaticText(PROFILETEXT, flags=c4d.BFH_LEFT, initw=300, inith=0, name="Sweep profile sides:")
#        
#        self.AddEditSlider(PROFILESIDES, flags=c4d.BFH_FIT, initw=30, inith=0)
#        self.SetLong(PROFILESIDES, 6, min=3, max=8, step=1)
#        
#        self.GroupEnd()
#        
#        
#        self.GroupBegin(DLG_GROUP_2, flags=c4d.BFH_RIGHT|c4d.BFV_BOTTOM, cols=2, rows=1, title="", groupflags=5)
#        self.GroupBorderSpace(10, 10, 10, 10)
#        self.AddButton(CANCELBUTTON, flags=c4d.BFH_RIGHT, name="Cancel")
#        self.AddButton(IMPORTBUTTON, flags=c4d.BFH_RIGHT, name="Import File")
#        self.GroupEnd()
#       
#        return True
#
#    def InitValues(self):
#        #initiate the gadgets with values
#        if versionNumber >= 13000:
#            self.SetString(TEXTBOX, "The NeuronBuild script imports accurate neuromorpho SWC files "\
#            "and creates spline-based geometry (scale assumes µm as world unit). Choose modeling options below; " \
#            "if all boxes are unchecked, only the base splines will be added to the scene.")
#        else:
#            self.SetString(TEXTBOX, "The NeuronBuild script imports\naccurate neuromorpho SWC files\n"\
#                           "and creates spline-based geometry\n(scale assumes µm as world unit).\nChoose modeling options below;\n" \
#                           "if all boxes are unchecked, only\nthe base splines will be added to\nthe scene.")
#        self.result = True
#        return True
#
#    def Command(self, id, msg):
#        #reference global variables that set model parameters
#        global DoHN, DoConnect, DoRail, DoSweep, NSides
#        #handle user input
#        if id==IMPORTBUTTON:
#            close = True
#            DoHN = self.GetBool(HNCHECK)
#            DoConnect = self.GetBool(CONNECTCHECK)
#            DoRail = self.GetBool(RAILCHECK)
#            DoSweep = self.GetBool(SWEEPCHECK)
#            NSides = self.GetLong(PROFILESIDES)
#            self.result = True
#
#        elif id==CANCELBUTTON:
#            close = True
#            self.result = None
#
#        else:
#            close = False
#            DoHN = self.GetBool(HNCHECK)
#            DoConnect = self.GetBool(CONNECTCHECK)
#            DoRail = self.GetBool(RAILCHECK)
#            DoSweep = self.GetBool(SWEEPCHECK)
#            NSides = self.GetLong(PROFILESIDES)
#        
#        if close:
#            self.Close()
#            
#        return True
#    
#def open_settings_dialog(default=None, title=None, width=240, height=290):
#    dialog = SettingsDlg(title, default)
#    dialog.Open(c4d.DLG_TYPE_MODAL, defaultw=width, defaulth=height)
#    return dialog.result
#        
      
def main():
        mygui = NeuroToolsGUI(title="NeuronBuild")
        #call it
        mygui.setup()
        mygui.display()


if __name__=='__main__':
    main()
