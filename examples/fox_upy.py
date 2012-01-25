# -*- coding: utf-8 -*-
"""
Created on Mon Nov 21 13:30:57 2011

@author: -
"""

#fox prototype upy 
#example for a script not a plugin ....
import sys,os
print sys.argv
from math import sqrt

from DejaVu import Viewer
#pyubic have to be in the pythonpath, if not add it
#upypath = "/Users/ludo/DEV/"
#sys.path.append(upypath)

DEBUG = False

import upy
if  "qt" in sys.argv:
    upy.setUIClass("qt")#force qt
else :
    upy.setUIClass()

#should have a template ?
from upy import uiadaptor
helperClass = upy.getHelperClass()

showerror = uiadaptor.drawError

class Fox(object):
    TEMPDIR = ".vs_temp" # move it to the home user path?
    SNAPSHOT_DIR = TEMPDIR+os.sep+"snapshots"
    REC_CACHE_DIR = TEMPDIR+os.sep+"receptor_grid_boxes"
    
    def __init__(self):
        self.setupDefaultOutPut()
        self.LigBook = {}
        self.GridInfo = {} # Global, to be updated when deleting ligands """spacing, [pts], [center],[max],[min]"""
        self.CurrentSessionRMStol = None # initialized as null, then the first ligand found will set the sesion valiue
    #theses two function are for c4d
        self.gui = None
        
    def get_lines(self,filename):
        f = open(filename, 'r')
        lines = f.readlines()
        f.close()
        return lines

    def ExtractResidues(self,ReceptorFilename,RecBoxFilename):
#        global FullResList, BoxResList, NonBoxResList
    
        FullResList = []
        BoxResList = []
    
        rec = ReceptorFilename
        box = RecBoxFilename
        if DEBUG:
            print "ExtractResidues>"
            print "\trec:", rec
            print "\tbox:", box
        if rec is None :
            return None,None,None
        try:
            lines = self.get_lines(rec)
        except:
            if DEBUG: print "ExtractResidues> problems in scanning the file: ",rec
            return False
        for l in lines:
            if l[0:4] == "ATOM" or l[0:6] == "HETATM":
                r = l[21]+"_"+l[17:20].strip()+"_"+l[23:26].strip()
                if not r in FullResList:
                    FullResList.append(r)
        """
        print "BOX == None", (box == None)
        print "BOX == \"\"", (box == "")
        print "BOX == |%s|"% box
        print "Box type = ", type(box)
        """
    
        if not box == "":
            if DEBUG: print "ExtractResidues> we've got the box"
            try:
                lines = self.get_lines(box)
            except:
                print "ExtractResidues> problems in scanning the file: ",box
                return False
            for l in lines:
                if l[0:4] == "ATOM" or l[0:6] == "HETATM":
                    r = l[21]+"_"+l[17:20].strip()+"_"+l[23:26].strip() #CHAIN_RES_NUMB
                    if not r in BoxResList:
                        BoxResList.append(r)
        if DEBUG:
            print "ExtractResidues> found %d residues" % len(FullResList)
            print "ExtractResidues> found %d residues in the box" % len(BoxResList)
        return FullResList,BoxResList
        
    def checkPDBQT_receptor(self,filename): 
        if DEBUG: print "testing the file", filename
        found_ligand = False
        found_receptor = False
        #if True:
        try:
            r = open(filename, 'r')
            buffer = r.readlines()
            r.close()
            for line in buffer:
                if line[0:4] == "ROOT":
                    found_ligand = True
                if line[0:9] == "BEGIN_RES":
                    found_ligand = True
                if line[0:4] == "ATOM" or line[0:6] == "HETATM":
                    found_receptor = True
            if found_ligand:
                showwarning("Error!", "The receptor is not valid.\n[ possibly a ligand file ]")
                return False
            else:
                if not found_receptor:
                    showwarning("Error!", "The receptor is not valid.\n[ possibly not a PDBQT file ]")
                    return False
                else:
                    return True
            
        except:
            showwarning("Error!", "Impossible to read the receptor file.")
            return False
    
    def dist(self,firstatom, secondatom):  
            # INFO   : calculate the atomic distance between two PDB atom lines
            # INPUT  : two pdb lines
            # OUTPUT : a pdb line
            coord1=[]
            coord2=[]
            temp=fistatom[28:56]
            coord1=temp.split()
            temp=secondatom[28:56]
            coord2=temp.split()
            # floating the strings
            for index in range(len(coord1)):
                coord1[index]=float(coord1[index])
                coord2[index]=float(coord2[index])
            measure=sqrt((coord1[0]-coord2[0])**2+(coord1[1]-coord2[1])**2+(coord1[2]-coord2[2])**2)
            return measure
        
    
    
    def pdb_in_the_box(self,ReceptorFilename=None,ReceptorGPF=None,GridInfo={}):
        # tolerance?
        tol = 3 # Angstrom outside the box
        tol = 1.
        
        # to include residues as well?
       
        #if (not ReceptorGPF.get() or len(GridInfo) == 0) or not ReceptorFilename.get():
        if len(GridInfo) == 0 or not ReceptorFilenam:
            if DEBUG: print "pdb_in_the_box> nothing to do for me... returning"
            return False
    
        PDB_IN = []
        PDB_OUT = []
        coord1 = []
        coord2 = []
    
        rec = ReceptorFilename
        filename = os.path.basename(rec)
    
        # purge mechanism to the "IN_THE_BOX" string
        filename = filename.replace("_IN_THE_BOX", "")
        filename = filename.rsplit(".", 1)[0]+'_IN_THE_BOX.pdbqt'
        out_name = self.REC_CACHE_DIR + os.sep + filename
        #REC_CACHE_DIR = TEMPDIR+os.sep+"receptor_grid_boxes"
        
        if out_name == rec:
            if DEBUG: print "pdb_in_the_box> avoiding to overwrite the rec input file (input and output are the same)"
            return True
        
        try: 
            PDB_IN = self.get_lines(rec)
            #PDB_IN_FILE = open(rec, 'r')
        except:
            if DEBUG: print "pdb_in_the_box> error in opening the receptor:", rec
            showerror(root, ("Error!\nImpossible to open the receptor filename:\n%s"% rec))
            return False
        #
        #for line in PDB_IN_FILE:
        #    PDB_IN.append(line)
        #PDB_IN_FILE.close()
    
    
    
        if not len(GridInfo) == 0:
            if DEBUG: print "pdb_in_the_box> using the GRID_INFO"
            min = GridInfo['min']
            max = GridInfo['max']
            for i in range(len(min)):
                min[i] -= tol
                max[i] += tol
            PDB_OUT.append("REMARK   Atoms of "+rec+" contained in the grid box\nREMARK   defined by the following MAX/MIN pair:\nREMARK    "+str(min)+"\nREMARK    "+str(max)+"\n")
    
        else:   
            try:
                GPF = open(ReceptorGPF, 'r')
            except:
                if DEBUG: print "pdb_in_the_box> error in reading the gpf:", ReceptorGPF.get()
                showerror(root,  ("Error!\nProblems trying to open the GPF:\n\n%s"% ReceptorGPF.get()))
                return False
            if DEBUG: print "pdb_in_the_box> using the GPF"
            found = 0
            for line in GPF:
                tmp=line.split()
                if tmp[0] == "gridcenter":
                    center_x = float(tmp[1])
                    center_y = float(tmp[2])
                    center_z = float(tmp[3])
                    found += 1
                if tmp[0] == "npts":
                    pts_x = float(tmp[1])
                    pts_y = float(tmp[2])
                    pts_z = float(tmp[3])
                    found += 1
                if tmp[0] == "spacing":
                    res = float(tmp[1])
                    found += 1
            GPF.close()
            if not found == 3:
                if DEBUG: print " PDB_IN_THE_BOX> error in the gpf content:", ReceptorGPF.get()
                showerror(root, ("Error!\nPotentially invalid GPF:\n\n%s"% ReceptorGPF.get()))
        
                return False
    
    
            step_x = pts_x/2 * res
            step_y = pts_y/2 * res
            step_z = pts_z/2 * res
            
            max = [ center_x + step_x + tol, center_y + step_y + tol, center_z + step_z + tol ]
            min = [ center_x - step_x - tol, center_y - step_y - tol, center_z - step_z - tol ]
        
        
            PDB_OUT.append("REMARK   Atoms of "+rec+" contained in the grid box\nREMARK   defined in "+ReceptorGPF.get()+"\n")
        for line in PDB_IN:
            if line[0:4] == "ATOM" or line[0:6] == "HETATM":
                #x = float(line[28:56].split()[0])
                #y = float(line[28:56].split()[1])
                #z = float(line[28:56].split()[2])
    
                #line = line[30:54] # TODO TESTING CODE!!!
                x = float(line[30:38])
                y = float(line[38:46])
                z = float(line[46:54])
    
                if x < max[0] and x > min[0]:
                    if y < max[1] and y > min[1]:
                        if z < max[2] and z > min[2]:
                            PDB_OUT.append(line)
        if len(PDB_OUT) > 1:
            if DEBUG: print len(PDB_OUT)," atoms accepted"
            try:
                OUT = open(out_name, 'w')
                for line in PDB_OUT:
                    print >> OUT, line[:-1]
                OUT.close()
                if DEBUG: print "PDB_IN_THE_BOX> receptor filename updated:", out_name
                return out_name 
            except:
                if DEBUG: print "PDB_IN_THE_BOX> error in opening the output file:", out_name
                return False
        else:
            if DEBUG: print "PDB_IN_THE_BOX> no atoms in the grid... is this an error? "
            showwarning("Warning", ("Possible receptor mismatch?\n\nNo receptor atoms have been found inside the GPF box or whithin %2.2f Angstrom around it.\n\nCheck if the receptor filename is correct or proceed at your own risk..." % tol) )
            return False                            
    
    
    def get_ligand_info(self,ligand, data = None):
        """ 
            takes a ligand_name or a file_name, and try to dig into
            hay-stack of the PDBQT+ to find the data of the selected pose.
    
            by default energy is provided
            data possible values
    
                   'energy'
                   'ligand_efficiency'
                   'hb_count'            --> total number of HB established
                   'vdw_count'           --> total number of VDW established
                   'hb_atom_count'       --> total number of *atoms* involved in HB interactions
                   'vdw_atom_count'      --> total number of *atoms* involved in VDW interactions
                   'runs
                   'total_clusters'
                   'rmstol'
                   'energy'
                   'cluster_size'
                   'e_range'
                   'active_torsions'
                   'cluster_percent_size'
    
        """
    
        ligand_info = {}
    
        # it's a file or an entry in the LigBook?
        if ligand in self.LigBook.keys():
            """
            if not LigBook[ligand]['vs'] == '':
                filename = LigBook[ligand]['vs']
            else:
                filename = LigBook[ligand][PoseMode.get()] # "le" or "lc"
            """
            filename = self.get_current_pose(ligand)
            if DEBUG:
                l = self.LigBook[ligand]
                print "get_ligand_info> got requested for ligand", ligand
                #print "get_ligand_info> getting energy from %s pose" % PoseChoice.get()
                print "\tpath:", l['path']
                print "\tle:", l['le']
                print "\tlc:", l['lc']
                print "\tdlg:", l['dlg']
                print "\treceptor:", l['rec']
                print "\trecluster:", l['recluster']
                print "\tselect:", l['selected']
        else:
            filename = ligand
            if DEBUG: print "get_ligand_info> got requested for a filename", ligand
    
        try:
            lines = self.get_lines(filename)
        except:
            if DEBUG: print "problem reading file", filename
            return False
        #print "PROCESSING", ligand
    
        IN = False
        IN_hb = False
        IN_vdw = False
        count_hb = 0
        count_vdw = 0
    
        for l in lines:
            if IN_hb:
                if ("USER  AD> " in l) and (':' in l) and (not "macro_close_ats" in l): # very fragile but the only choice with the current PDBQT+ format
                    #print "================= HB count"
                    count_hb += 1
    
            if IN_vdw:
                if ("USER  AD> " in l) and (':' in l) and (not "lig_close_ats:" in l ): # very fragile but the only choice with the current PDBQT+ format
                    #print "================= VDW count"
                    count_vdw += 1
    
            # ligand efficiency
            if "AD> ligand efficiency" in l:
                try:
                    ligand_info['ligand_efficiency'] = float(l.split()[-1])
                except:
                    if DEBUG: print "get_ligand_info> problems in extracting LIGAND efficiency. Line:", l
                    return False
            
            # hb-atoms
            elif "USER  AD> lig_hb_atoms :" in l:
                try:
                    ligand_info['hb_atoms_count'] = int(l.split()[-1])
                    IN_hb = True
                except:
                    if DEBUG: print "get_ligand_info> problems in extracting HB_count. Line:", l
                    return False
    
            # close contacts atoms
            elif "USER  AD> macro_close_ats:" in l:
                try:
                    ligand_info['vdw_atoms_count'] = int(l.split()[-1])
                    IN_vdw = True
                    ligand_info['hb_count'] = count_hb
                    IN_hb = False
                except:
                    if DEBUG: print "get_ligand_info> problems in extracting Contact_count. Line:", l
                    return False
    
            elif "USER  AD> lig_close_ats:" in l:
                # TODO collect the data from VDW
                ligand_info['vdw_count'] = count_vdw 
                IN_vdw = False
    
            # runs and clusters
            elif ("runs" in l) and (" clusters" in l):
                try:
                    l = l.split()
                    ligand_info['runs'] = int(l[4])
                    ligand_info['total_clusters'] = int(l[6])
                    ligand_info['rmstol'] = float(l[3])
                except:
                    if DEBUG: print "get_ligand_info> problems in extracting data from another poorly formatted PDBQT+. Line:", l
                    return False
    
            if IN:
                try:
                    ligand_info['energy']
                except:
                    try:
                        l = l[9:] # remove "USER  AD>"
                        l = l.rstrip("\n") # .... no comment
                        l = l.split(',')
                        #print l
                        #if l[-3] == "1": 
                        if l[-3] == "1": 
                            ligand_info['energy'] = float(l[1])
                            ligand_info['cluster_size'] = int(l[2])
                            ligand_info['e_range'] = float(l[3])
                    except:
                        if DEBUG: print "get_ligand_info> problems in searching the ENERGY. Line:", l
                        return False
    
            if ("clu_size, clu_e_range, dlgfilename, run#") in l:
                IN = True
    
            if "active torsions" in l:
                ligand_info['active_torsions'] = int(l.split()[1])
                break # we've reached the end of the interesting stuff in the file
    
        ligand_info['cluster_percent_size'] = ( float(ligand_info['cluster_size']) / float(ligand_info['runs']) ) *100
        if data:
            return ligand_info[data]
        else:
            return ligand_info
    
    def float_range(self,b, e, s):
        """
        print "float_range> Start", b
        print "float_range> End  ", e
        print "float_range> step ", s
        """
        b = float(b)
        e = float(e)
        s = float(s)
        l = []
        c = b
        if b>e:
            while c >= e:
                l.append(c)
                c -= s
        else:
            while c <= e:
                c += s
        #print l
        return l

#    def vs_energy_profile(self,range_only = False):ui?
        
    def setupDefaultOutPut(self,):
        self.TEMPDIR = os.getcwd()+os.sep+self.TEMPDIR
        if not os.path.exists(self.TEMPDIR):
            try:
                os.makedirs(self.TEMPDIR, 0755)
            except:
                showerror( "Error!", ("Impossible to write in the following path:\n\n%s\n\nBe sure the current user has enough privileges to access to it and that there's enough disk space left.\n\nQuit") % TEMPDIR )
                exit()
            
        if not os.path.exists(self.REC_CACHE_DIR):
            try:
                os.makedirs(self.REC_CACHE_DIR, 0755)
            except:
                showerror("Error!", ("Impossible to write in the following path:\n\n%s\n\nBe sure the current user has enough privileges to access to it and that there's enough disk space left.\n\nQuit") % REC_CACHE_DIR )
                exit()

class VisOptions(uiadaptor):
    def setup(self,fox=None,id=None):
        self.subdialog = True
        self.block = True
        self.fox = fox
        self.title = "Visualizatio options"
        self.SetTitle(self.title)
        witdh=350
        self.h=400
        self.w=600
        if id is not None :
            id=id
        else:
            id = self.bid
        self.id = id
        #define the widget here too
        self.listeNotbeook = ["Ligands", "Target", "3D Viewer"]
        self.notebooklayout = {}
        self.initWidget()
        self.setupLayout()
    
    def initWidget(self):
        #tab Ligands, Target, 3D Viewer
        #puuldown menu and checkbox
        self.LABEL ={}
        self.COLORS = {}        
        self.MENU={}
        self.BTN={}
        self.CHECK={}
        self.empty= self._addElemt(label = "",width=50,height=15)
        #ligands widget
        self.LABEL["representation"] = self._addElemt(label = "Representation",width=60,height=15)
        self.lig_representation = ["Lines","Sticks","Ball'n'Sticks","CPK","MSMS"]
        self.MENU["representation"] = self._addElemt(name="Representation",value=self.lig_representation,
                                    width=60,height=10,action=self.LigStyle,
                                    variable=self.addVariable("int",1) ,
                                    type="pullMenu")  
        self.LABEL["colorby"] = self._addElemt(label = "Color by",width=60,height=15)
        self.color_by = ["Atom type","DG colors"]
        self.MENU["colorby"] = self._addElemt(name="Color by",value=self.color_by,
                                    width=60,height=10,action=self.LigStyle,
                                    variable=self.addVariable("int",1) ,
                                    type="pullMenu")  
        self.LabelColor = (1.,1.,0.)
        self.LABEL["LabelColor"] = self._addElemt(label = "Carbon color",width=60,height=15)
        self.COLORS["LabelColor"] = self._addElemt(name="chooseCol",action=self.LabelColorPicker,
                                       variable = self.addVariable("col",self.LabelColor),
                                       type="color",width=30,height=15)
                                    
        self.BTN["histo"]=self._addElemt(name="Show histogram",width=80,height=10,
                                         action=None,type="checkbox",icon=None,
                                         variable=self.addVariable("int",0))
        self.LABEL["interaction"] = self._addElemt(label = "Interactions",width=50,height=15)
        self.CHECK["interaction"] = {}
        self.CHECK["interaction"]["hb"] = self._addElemt(name="Hydrogen bonds",width=80,height=10,
                                         action=None,type="checkbox",icon=None,
                                         variable=self.addVariable("int",1))
        self.CHECK["interaction"]["vdw"] = self._addElemt(name="VdW contacts",width=80,height=10,
                                         action=None,type="checkbox",icon=None,
                                         variable=self.addVariable("int",1))
        self.CHECK["interaction"]["el"] = self._addElemt(name="Electrostatics",width=80,height=10,
                                         action=None,type="checkbox",icon=None,
                                         variable=self.addVariable("int",1))                                 
        self.CHECK["interaction"]["pi"] = self._addElemt(name="Pi/Pi stacking",width=80,height=10,
                                         action=None,type="checkbox",icon=None,
                                         variable=self.addVariable("int",1))
        self.CHECK["interaction"]["cpi"] = self._addElemt(name="Cation/Pi",width=80,height=10,
                                         action=None,type="checkbox",icon=None,
                                         variable=self.addVariable("int",1))
        self.CHECK["interaction"]["d"] = self._addElemt(name="Distance",width=80,height=10,
                                         action=None,type="checkbox",icon=None,
                                         variable=self.addVariable("int",1))                                 
  
        #Target widget
        self.LABEL["ires"] = self._addElemt(label = "Grid Box/interacting resiues",width=50,height=15)
        self.LABEL["RecSubset"] = self._addElemt(label = "Residues subset",width=50,height=15)
        self._RecSubset = ["inside the grid-box","interacting with ligand","from filters"]
        self.MENU["RecSubset"] = self._addElemt(name="RecSubset",value=self._RecSubset,
                                    width=60,height=10,action=self.RecStyle,
                                    variable=self.addVariable("int",1) ,
                                    type="pullMenu")
        self.LABEL["Rrepresentation"] = self._addElemt(label = "Representation",width=50,height=15)
        self.rec_representation = ["Lines","Sticks","Ball'n'Sticks","CPK","MSMS"]
        self.MENU["Rrepresentation"] = self._addElemt(name="Representation",value=self.rec_representation,
                                    width=60,height=10,action=self.RecStyle,
                                    variable=self.addVariable("int",1) ,
                                    type="pullMenu")  
                                    
        self.LABEL["Rcolorby"] = self._addElemt(label = "Color by",width=50,height=15)
        self.r_color_by = ["Atom type","DG colors","secondary structure"]
        self.MENU["Rcolorby"] = self._addElemt(name="Color by",value=self.r_color_by,
                                    width=60,height=10,action=self.RecStyle,
                                    variable=self.addVariable("int",1) ,
                                    type="pullMenu")  
        self.RLabelColor = (1.,1.,0.)
        self.LABEL["RLabelColor"] = self._addElemt(label = "Carbon color",width=50,height=15)
        self.COLORS["RLabelColor"] = self._addElemt(name="chooseCol",action=self.RLabelColorPicker,
                                       variable = self.addVariable("col",self.RLabelColor),
                                       type="color",width=30,height=15)
                                    
        self.BTN["ires"]=self._addElemt(name="Highlight interacting residues",width=120,height=10,
                                         action=None,type="checkbox",icon=None,
                                         variable=self.addVariable("int",1))
        self.BTN["fres"]=self._addElemt(name="Highlight filter residues",width=120,height=10,
                                         action=None,type="checkbox",icon=None,
                                         variable=self.addVariable("int",1))        
        self.LABEL["labelsr"] = self._addElemt(label = "Label resiudes",width=50,height=15)
        self.LigCarbonColor = (1.,1.,0.)
        self.LABEL["labels"] = self._addElemt(label = "Label color",width=50,height=15)
        self.COLORS["labels"] = self._addElemt(name="chooseCol",action=self.LabelColorPicker,
                                       variable = self.addVariable("col",self.LigCarbonColor),
                                       type="color",width=30,height=15)
        
        self.BTN["allres"]=self._addElemt(name="All residues",width=80,height=10,
                                         action=None,type="checkbox",icon=None,
                                         variable=self.addVariable("int",1))   
        self.LABEL["allresrep"] = self._addElemt(label = "Representation",width=50,height=15)
        self.all_res_representation = ["Lines","Sticks","Ball'n'Sticks","Secondary structure","CPK","MSMS"]
        self.MENU["allresrep"] = self._addElemt(name="Representation",value=self.lig_representation,
                                    width=60,height=10,action=self.LigStyle,
                                    variable=self.addVariable("int",1) ,
                                    type="pullMenu")  
        self.LABEL["allcolorby"] = self._addElemt(label = "Color by",width=50,height=15)
        self.all_color_by = ["Atom type","DG colors","secondary structure","Custom color"]
        self.MENU["allcolorby"] = self._addElemt(name="Color by",value=self.all_color_by,
                                    width=60,height=10,action=self.LigStyle,
                                    variable=self.addVariable("int",1) ,
                                    type="pullMenu")  
        self.customColor = (1.,1.,0.)
        self.LABEL["customColor"] = self._addElemt(label = "Custom color",width=50,height=15)
        self.COLORS["customColor"] = self._addElemt(name="chooseCol",action=self.CustomColorPicker,
                                       variable = self.addVariable("col",self.customColor),
                                       type="color",width=30,height=15)
        
        
        
        self.BTN["close"] = self._addElemt(name="Close",width=40,height=10,
                         action=self.close,type="button")  
                         
        for nb in self.listeNotbeook :
            self.notebooklayout[nb]=[]                    
        self.set_target_layout()
        self.set_ligands_layout()
        self.set_viewer_layout()
        
    def set_target_layout(self,):
        self.notebooklayout["Target"].append([self.LABEL["ires"],])
        self.notebooklayout["Target"].append([self.LABEL["RecSubset"],self.MENU["RecSubset"],])
        self.notebooklayout["Target"].append([self.LABEL["Rrepresentation"],self.MENU["Rrepresentation"],])
        self.notebooklayout["Target"].append([self.LABEL["Rcolorby"],self.MENU["Rcolorby"],])
        self.notebooklayout["Target"].append([self.LABEL["RLabelColor"],self.COLORS["RLabelColor"]]) 
        self.notebooklayout["Target"].append([self.BTN["ires"],])   
        self.notebooklayout["Target"].append([self.BTN["fres"],])   
        
        self.notebooklayout["Target"].append([self.LABEL["labelsr"],])
        self.notebooklayout["Target"].append([self.LABEL["labels"],self.COLORS["labels"],])
        
        self.notebooklayout["Target"].append([self.BTN["allres"],])
        self.notebooklayout["Target"].append([self.LABEL["allresrep"],self.MENU["allresrep"],])
        self.notebooklayout["Target"].append([self.LABEL["allcolorby"],self.MENU["allcolorby"],])
        self.notebooklayout["Target"].append([self.LABEL["customColor"],self.COLORS["customColor"]])        
        

    def set_ligands_layout(self,):
        self.notebooklayout["Ligands"].append([self.LABEL["representation"],self.MENU["representation"],])
        self.notebooklayout["Ligands"].append([self.LABEL["colorby"],self.MENU["colorby"],])
        self.notebooklayout["Ligands"].append([self.LABEL["LabelColor"],self.COLORS["LabelColor"],])
        self.notebooklayout["Ligands"].append([self.empty,self.BTN["histo"]])
        #another group?
        #separtor
        self.notebooklayout["Ligands"].append([self.LABEL["interaction"],])
        for e in [["hb","pi"],["vdw","cpi"],["el","d"]]:
            self.notebooklayout["Ligands"].append([self.CHECK["interaction"][e[0]],
                                                  self.CHECK["interaction"][e[1]]])
         
    def set_viewer_layout(self,):
        self.notebooklayout["3D Viewer"].append([self.LABEL["labels"],self.COLORS["labels"],])
        
    def setupLayout(self):
        #form layout for each SS types ?
        self._layout = []
        for nb in  self.listeNotbeook :
            frame1 = self._addLayout(name=nb,elems=self.notebooklayout[nb],type="tab")
            self._layout.append(frame1)        
#        self._layout.append([self.BTN["close"],])
        
    def CreateLayout(self):
        self._createLayout()
        #self.restorePreferences()
        return True

    def Command(self,*args):
#        print args
        self._command(args)
        return True

    def CustomColorPicker(self,*args):
        """Set the color of ligand carbon atoms"""
        self.customColor = self.getVal(self.COLORS["customColor"])         
        self.LigStyle()
        return

    def LigCarbColorPicker(self,*args):
        """Set the color of ligand carbon atoms"""
        self.LigCarbonColor = self.getVal(self.COLORS["LabelColor"])         
        self.LigStyle()
        return
        
    def RLabelColorPicker(self,*args):
        """set the label color"""
        self.RLabelColor = self.getVal(self.COLORS["RLabelColor"])
        print "color",self.LabelColor #rgb 1-255
        self.fox.gui.RecStyle() 
        
    def LabelColorPicker(self,*args):
        """set the label color"""
        self.LabelColor = self.getVal(self.COLORS["labels"])
        print "color",self.LabelColor #rgb 1-255
        self.fox.gui.RecStyle()
        
#        try :
#            self.fox.gui.RecStyle()
#        except :
#            print "no fox ro no gui"

    def RecStyle(self,*args):
        self.fox.gui.RecStyle()
        
    def LigStyle(self,*args):
        self.fox.gui.LigStyle()

    def getStates(self,**kw):
        states={}
        box_visible=0
        box_mode=0
        box_color=0
        full_rec_visible=0
        full_rec_mode=0
        full_rec_color=0
        full_rec_flat_color=0
        labelset=0
        labelcolor=0
        return states
        
#subdialog
class EnergyPopulation(uiadaptor):
    def setup(self,fox=None,id=None):
        self.subdialog = True
        self.block = True
        self.fox = fox
        self.title = "Energy profile"
        self.SetTitle(self.title)
        witdh=350
        self.h=400
        self.w=600
        if id is not None :
            id=id
        else:
            id = self.bid
        self.id = id
        #define the widget here too
        self.BTN={}
        #seems to be a graph viewer ? 
        self.BTN["cancel"] = self._addElemt(name="Close",width=40,height=10,
                         action=self.close,type="button")
        #should draw an image from matplotlib...
        self.setupLayout()

    def Set(self,data=None,choice = "Lowest energy in largest cluster"):
        if data is not None :
            self.data = data
        self.choice = choice
        
    def setupLayout(self):
        #form layout for each SS types ?
        self._layout = []
        self._layout.append([self.BTN["cancel"],])

    def CreateLayout(self):
        self._createLayout()
        #self.restorePreferences()
        return True

    def Command(self,*args):
#        print args
        self._command(args)
        return True
    
#add slider player for properties
class foxGui(uiadaptor):
    def setup(self,**kw):
        #uiadaptor.__init__(self,**kw)
        #self.title = "Tetrahedron"
        self.fox = Fox()
        self.fox.gui = self
        if not hasattr(self,"master"):
            self.master = None
        self.listeNotbeook = ['Input data','Filter & Analysis','Viewer','Export']        
        self.initWidget(id=10)
        self.initNoteBookLayout()
        self.setupLayout()
        self.CurrentSessionRMStol = None # initialized as null, then the first ligand found will set the sesion valiue
    #theses two function are for c4d
        self.LigBook = self.fox.LigBook
        self.GridInfo = self.fox.GridInfo
        self.ReceptorFilename = ""
        self.ReceptorMolecule = None
        self.mv = None
        self.FullResList=[]
        self.BoxResList=[]
        
    def initialisation(self,):
        # INITIALIZATION
#        self.UpdateLigandInfo()
        self.UpdateLigandInputInfo()
        self.UpdateGridInfo()
        self.reset()
        #where is the viewer
        

    def setViewer(self,type="pmv"):
        #could be dejavu, epmv, etc..
        if type == "pmv" :#require tk
            self.set_PMV()
        elif type == "epmv":
            self.set_ePMV()
        #how to integrate the camera inside the dialog
        
    def set_ePMV(self):
        #should get epmvAdaptor standalone
        #check epmv_qt,with the universa DejaVu
        import ePMV
        epmv = ePMV.epmv_start(self.host,debug=0)
        epmv.gui = None
        epmv.initOption()
        self.mv = epmv.mv
        self.epmv = epmv        

        #take the curret camera and put it in the container
        if self.master is not None :
            self.helper = helperClass(master=self.camera_widget_container["id"])
        else :
            self.helper = helperClass(**kw) 
        
        self.viewer = self.helper.viewer    
        self.viewer.GUI.withdraw()       
#        self.viewer.AddCamera(master=self.camera_widget_container["id"])
        self.camera = self.viewer.cameras[0]
        self.camera.name = "fox"
        self.SetAAlevel()
        self.viewer.SetCurrentCamera(self.camera)
    
    def set_PMV(self):
        from Pmv.moleculeViewer import MoleculeViewer
        from DejaVu import Viewer
        #print "BROKEN? ASK MICHEL HOW TO FIX"
        print "Loading 3D viewer...",
        if '-s' in sys.argv:
            withShell = 1
        else:
            withShell = 0
        from Tkinter import Toplevel
        pmvroot = Toplevel()
        pmvroot.withdraw()
            
        self.mv = MoleculeViewer(logMode = 'overwrite',  customizer=None, master=pmvroot, 
                            title='Coati | AutoDock VS', withShell= withShell, 
                            verbose=False, gui = True,guiVisible=1)
        print "[DONE]"
        self.viewer = self.mv.GUI.VIEWER
        self.viewer.AddCamera(master=self.camera_widget_container["id"])
        self.camera = self.viewer.cameras[1]
        self.viewer.SetCurrentCamera(self.camera)
        self.camera.name = "fox"
#        self.camera.SelectCamera()
#        self.camera.tk.call(self.camera._w, 'makecurrent') 
#        self.camera.focus_set()
        self.viewer.SetCurrentObject(self.viewer.rootObject)        
        #print hex_to_rgb(BGcolor.get())
#        self.viewer.CurrentCameraBackgroundColor( self.hex_to_rgb (BGcolor.get() ) )
        #resetview()
        self.SetAAlevel()#shoul be in another interface/class
        #since we are in tk need to personalize the dialog using another widget
        #how to add custom wodget  in upy?
        #should we create an empty group that will receive it ? 
        #hide PMV
        self.mv.GUI.ROOT.withdraw()
        if self.master is not None :
            self.helper = helperClass(master=self.mv.GUI.VIEWER)
        else :
            self.helper = helperClass(**kw) 
 
    def SetAAlevel(self,val = "medium"):
        aa_levels = { "[off]" : 0,
                      "low"   : 2,
                      "medium": 4,
                      "high"  : 8}
        if DEBUG:
            print "SetAAlevel> antialias :", AAlevel.get()
#        if val is not None :
#            self.mv.setAntialiasing( aa_levels[ val] )
        return
       
    
    def reset(self):    
        self.current_full_rec_visible = None
        self.current_full_rec_mode = None
        self.current_full_rec_color= None
        self.current_full_rec_flat_color = None
        self.current_box_visible= None
        self.current_box_mode = None
        self.current_box_color = None
        self.current_box_c_color= None
        self.current_ligand_interactions= None
        self.current_labelset = None
        self.current_labelcolor = None
        self.IN_residues = None
        self.OUT_residues = None
        
    def CreateLayout(self):
        self._createLayout()
        return 1

    def Command(self,*args):
#        print args
        self._command(args)
        return 1

    def viewer_init_widget(self):
        #if in pmv,epmv etc how to add the camera widget
        self.viewer_widget_lab={}    
        self.viewer_widget_btn={}
        self.viewer_widget_str={}
        self.viewer_widget_istr={}       
        
        self.viewer_widget_btn["vis_options"] = self._addElemt(name='Viewer option',width=60,height=10,
                         action=self.drawViewerOptions,type="button")
        self.camera_widget_container = self._addElemt(name='3Dviewer',width=60,height=10,
                         type="group")
                         
    def viewer_init_layout(self,):
        self.viewer_layout = []
        self.viewer_layout.append([self.camera_widget_container,])
        self.viewer_layout.append([self.viewer_widget_btn["vis_options"] ,])
        
    def ligand_init_widget(self,):
        self.ligand_widget_lab={}    
        self.ligand_widget_btn={}
        self.ligand_widget_str={}
        self.ligand_widget_istr={}    
        self.ligand_widget_lab["ilig"] = self._addElemt(label="Import ligands...",width=120)
        self.ligand_widget_btn["scanDir"]=self._addElemt(name='Scan directories...',width=60,height=10,
                         action=lambda : self.openLigandDir(True),type="button")
        self.ligand_widget_btn["addDir"]=self._addElemt(name='Add single directory...',width=80,height=10,
                         action=self.openLigandDir,type="button")
        self.ligand_widget_btn["Rmsel"]=self._addElemt(name='Remove selected',width=60,height=10,
                         action=self.RemoveLigand,type="button")
        self.ligand_widget_btn["Rmall"]=self._addElemt(name='Remove all',width=60,height=10,
                         action=lambda: self.RemoveLigand(True),type="button")
    
        # ligand info statistics
        # new Group "Clustering info" ?
        # text Area ?
        self.ligand_widget_lab["clinfo"] = self._addElemt(label="Clustering info",width=120)
        self.ligand_widget_str["clinfo"] = self._addElemt(name="Clustering info",width=120,height=40, type="inputStrArea")
        self.ligand_widget_btn["cluster"] = self._addElemt(name='Clustering tool',width=120,height=10,
                         action=self.ImportLigandOptions,type="button")
        

        # target info statistics
        #tag_text = 'Target structure')
        self.ligand_widget_lab["opPDBQT"] = self._addElemt(label="Target structure",width=120)
        self.ligand_widget_btn["opPDBQT"] = self._addElemt(name='Open PDBQT file ...',width=80,height=10,
                         action=self.SelectReceptor,type="button")
        self.ligand_widget_istr["rname"] = self._addElemt(label="",width=120)
        
        #grid info       
        self.ligand_widget_lab["grinfo"] = self._addElemt(label="Grid info",width=120)
        self.ligand_widget_str["grinfo"] = self._addElemt(name="Grid info",width=40,height=40, type="inputStrArea")
                     
    def ligand_init_layout(self,):
        self.ligand_layout = []
        self.ligand_layout.append([self.ligand_widget_lab["ilig"],self.emptyLabel,self.ligand_widget_lab["clinfo"]])
        self.ligand_layout.append([self.ligand_widget_btn["scanDir"],self.ligand_widget_btn["addDir"],self.ligand_widget_str["clinfo"]])
        self.ligand_layout.append([self.emptyLabel,self.emptyLabel,self.ligand_widget_btn["cluster"]])
        self.ligand_layout.append([self.emptyLabel,self.emptyLabel,self.ligand_widget_lab["opPDBQT"]])        
        self.ligand_layout.append([self.emptyLabel,self.emptyLabel,self.ligand_widget_btn["opPDBQT"],self.ligand_widget_istr["rname"]])
        self.ligand_layout.append([self.emptyLabel,self.emptyLabel,self.ligand_widget_lab["grinfo"]])             
        self.ligand_layout.append([self.ligand_widget_btn["Rmsel"],self.ligand_widget_btn["Rmall"],self.ligand_widget_str["grinfo"]])
    
    def filter_init_widget(self,):
        self.filter_widget_lab={}    
        self.filter_widget_btn={}
        self.filter_widget_str={}
        self.filter_widget_istr={} 
        self.filter_widget_ifloat={}         
        self.filter_widget_menu={} 
        self.filter_widget_lab["pose"] =  self._addElemt(label="Pose :",width=80)

        self.filter_widget_pmenu_v=self.addVariable("int",1)        
        self.filter_widget_menu_liste = ["Lowest energy in largese cluster","Absolute lowest energy"]
        self.filter_widget_menu["pose"] = self._addElemt(name="Pose",value=self.filter_widget_menu_liste,
                                    width=60,height=10,action=self.UpdateResults,
                                    variable=self.filter_widget_pmenu_v,
                                    type="pullMenu")        
        self.filter_widget_str["nrj"] = self._addElemt(name="nrj",width=40,height=40, type="inputStrArea")
        self.filter_widget_btn["nrjpro"] = self._addElemt(name='Energy profile',width=120,height=10,
                         action=self.vs_energy_profile,type="button")
        filters = ["energy","cluster","efficiency"]
        for i,f in enumerate(filters) :
            self.filter_widget_lab[f] = self._addElemt(label=str(i+1)+". "+f,width=120)
            self.filter_widget_lab[f+"pie"] = self._addElemt(label="PIE",width=60)
            self.filter_widget_lab[f+"min"] = self._addElemt(label="MIN",width=60)
            self.filter_widget_lab[f+"max"] = self._addElemt(label="MAX",width=60)
            self.filter_widget_ifloat[f+"min"] = self._addElemt(name="float input",#action=self.input_float_cb,
                                    width=50,value=0.0,type="inputFloat",mini=0.,maxi=10.,
                                    variable=self.addVariable("float",0.0)) 
            self.filter_widget_ifloat[f+"max"] = self._addElemt(name="float input",#action=self.input_float_cb,
                                    width=50,value=0.0,type="inputFloat",mini=0.,maxi=10.,
                                    variable=self.addVariable("float",0.0))                                     
            self.filter_widget_btn["dflt"+str(i)] = self._addElemt(name='Default',width=40,height=10,
                         action=lambda : self.DefaultFilterValues(f),type="button")
        
        
    def filter_init_layout(self,):
        self.filter_layout = []
        self.filter_layout.append([self.filter_widget_lab["pose"],self.filter_widget_menu["pose"]])
        self.filter_layout.append([self.filter_widget_str["nrj"],])
        self.filter_layout.append([self.filter_widget_btn["nrjpro"],])
        filters = ["energy","cluster","efficiency"]
        for i,f in enumerate(filters) :        
            self.filter_layout.append([self.filter_widget_lab[f],self.emptyLabel,self.emptyLabel,])
            self.filter_layout.append([self.filter_widget_lab[f+"pie"],self.filter_widget_lab[f+"min"],self.filter_widget_lab[f+"max"]])
            self.filter_layout.append([self.emptyLabel,self.filter_widget_ifloat[f+"min"],self.filter_widget_ifloat[f+"max"]])           
            self.filter_layout.append([self.emptyLabel,self.filter_widget_btn["dflt"+str(i)],])
        
    def initWidget(self,id=None):
        self.emptyLabel = self._addElemt(label="",width=120)
        self.ligand_init_widget()
        self.ligand_init_layout()
        self.filter_init_widget()
        self.filter_init_layout()
        self.viewer_init_widget()
        self.viewer_init_layout()        
        self.setSubDialog()

    def setSubDialog(self):
        self.energyPopulation = EnergyPopulation(master=self.master)
        self.energyPopulation.setup(fox=self.fox)
        self.visOptions = VisOptions(master=self.master)
        self.visOptions.setup(fox=self.fox)        
        self.visOptions_visible = False
        
    def initNoteBookLayout(self):

        self.notebooklayout = {}
        for nb in  self.listeNotbeook : 
            self.notebooklayout[nb]=[]        
        self.notebooklayout['Input data'].extend(self.ligand_layout)
        self.notebooklayout['Filter & Analysis'].extend(self.filter_layout)
        self.notebooklayout['Viewer'].extend(self.viewer_layout)
        
    def setupLayout(self):
        for nb in  self.listeNotbeook :
            frame1 = self._addLayout(name=nb,elems=self.notebooklayout[nb],type="tab")
            self._layout.append(frame1)

    def UpdateResults(self,*args):
        print args

    def ImportLigandOptions(self,*args):
        print args

    def DefaultFilterValues(self,*args):
        print args
        
    def openLigandDir(self,*args):#ligDir = None, recursive = False
        """
        - prompt the user (or not) to [scan a directory containing DLG|import dlgs from a dir] and PDBQT+ files.
        - integrity check:
            - all the ligands found in the DLG must have a PDBQT+ file
            - if not, produce the list of files to be processed
        """
        print args
        

    def RemoveLigand(self,*args):
        print args

    def UpdateLigandInputInfo(self,):
        """
        Update the ligand info panel in the InputData tab
        """
        total = len(self.LigBook)
        txt  = "Ligands:\t\t %d\n" % total
        dlg_tot = 0
        recluster_count = 0
        if total >0 :
            label = "Ligands [ %d ]" % total
            self.setString(self.ligand_widget_lab["ilig"],label)
    
    
            for l in self.LigBook.keys():
                # dlg count
                lig = self.LigBook[l]
                dlg_tot += len(lig['dlg'])
    
                # recluster count
                if lig['recluster']:
                    if DEBUG: print "UpdateLigandInputInfo> reclustering status", LigBook[l]['recluster']
                    recluster_count += 1
        else:
            self.setString(self.ligand_widget_lab["ilig"],"Import ligands...")
        txt += "Total DLG count:\t %d\n" % dlg_tot
        if not self.CurrentSessionRMStol == None:
            txt += "RMS tolerance:\t %2.2f Angstrom\n" % CurrentSessionRMStol
        else:
            txt += "RMS tolerance:\t (none)\n"
        txt += "\nTo be reclustered:\t %d\n" % recluster_count
        
        self.ligand_widget_str["clinfo"]
        self.setStringArea(self.ligand_widget_str["clinfo"],txt)
        self.UpdateEnergyProfile()
        # ToBeReclustered =         

    def UpdateEnergyProfile(self,):
        #global FilterStatText
        total = len(self.LigBook)
        best,worst = (1.0,0.0)#vs_energy_profile(range_only = True)
        txt = "Ligands:\t\t %d\n" % total
        txt +="    Best energy:\t%2.2f\n"% best
        txt +="    Worst energy:\t%2.2f"% worst
        self.setStringArea(self.filter_widget_str["nrj"],txt)   

#        EnergyProfileButton = Button(FilterStatText,text = "Energy profile", command = vs_energy_profile)
#        FilterStatText.window_create(END, window =EnergyProfileButton)
        
#        FilterStatText.config(state = DISABLED)
    
        #FilterStatText = Text(Tab2, height=9, width=40, relief = FLAT)

    def vs_energy_profile(self,range_only = False):
        energy_list = []
        best = 9999
        worst = -9999
        total = len(self.LigBook.keys())
    
    
        for l in self.LigBook.keys():
            e = self.get_ligand_info(l, data = 'energy')
            if e < best:
                best = e
            if e > worst:
                worst = e
            energy_list.append(e)
    
        if DEBUG:
            print "vs_energy_profile> BEST :", best
            print "vs_energy_profile> WORST:", worst
    
        if range_only:
            return best, worst
    
        if total == 0:
            if DEBUG: print "vs_energy_profile> no ligands, returning"
            return
    
        min_cut = int(worst)
        max_cut = int(best)
        #bar_count = abs(max_cut-min_cut)+1
        if DEBUG: print "CUTOFF", min_cut-max_cut
        if (min_cut - max_cut)*2 < 12:
            step = .5
        else:
            step = 1
        #step = .5 # energy step
        bar_count = len(self.fox.float_range(min_cut, max_cut, step))+1
        if DEBUG:
            print "Min_cut", min_cut
            print "Max_cut", max_cut
            print "bar_count", bar_count
        pop = []
        for i in self.fox.float_range(min_cut, max_cut, step):
            pop.append(0)
        #print len(pop)
    
        start = min_cut
        end = min_cut-step
        #print "start", start
        #print "end", end
        count = 0
        for i in self.float_range(min_cut, max_cut, step):
            if DEBUG: print "vs_energy_profile> PROCESSING RANGE %2.2f < e < %2.2f" % (start, end)
            for e in energy_list:
                if e <= start and e > end:
                    pop[count] += 1
            start -= step
            end -= step
            count +=1
        # bests
        if end > max_cut:
            for e in energy_list:
                if e < float(max_cut):
                    pop[-1] += 1
        bars = []
    
        c = 0
        for i in pop:
            bars.append([i, (float(i)/float(total))*100, min_cut-c])
            c += step
        if DEBUG:
            print "vs_energy_profile> bars output:"
            for b in bars:
                print "\t",b
    
    
        """
        # fake
        bars = []
        bars.append([25, 25.00, -3])
        bars.append([20, 20.00, -4])
        bars.append([50, 50.00, -5])
        bars.append([100, 100.00, -6])
        #
        """
    
    
        for i in bars:
            if DEBUG: print "percent : %2.2f, count:  %d"%(i[1], i[0])
    
        #open EneryPopulaton subdialog
        
        # TODO add the check to see if the toplevel is present... blablabla
        #feed the dialog
        posechoice = self.filter_widget_menu_liste[self.getVal(self.filter_widget_menu["pose"])]
        self.energyPopulation.Set(data=bar,choice = posechoice)       
        self.drawSubDialog(self.energyPopulation,25553361)      

    def drawViewerOptions(self,*args):
        #do we want a toggle?
        #toggle view of option
        if self.visOptions_visible:
            self.visOptions.close()
            if isinstance(self.viewer,Viewer) :
                self.visOptions.withdraw()
#                self.viewer.GUI.withdraw()             
        else :
#            if isinstance(self.viewer,Viewer) :
#                self.viewer.GUI.deiconify() 
            self.drawSubDialog(self.visOptions,2555336)
        self.visOptions_visible = not self.visOptions_visible

    def UpdateGridInfo(self,*args):
        if DEBUG: print "UpdateGridInfo> start"
        if len(self.LigBook) == 0 or len(self.GridInfo) < 5:
            null = [0.,0.,0.]
            center = null
            points = null
            min = null
            max = null
            space = 0
    
        else: # len(GridInfo) == 5:
            center = self.GridInfo['center']
            points = self.GridInfo['pts']
            #max = GridInfo['max']
            #min = GridInfo['min']
            space = self.GridInfo['spacing']

    
        text = "\t X\t Y\t Z\n"
        text +="Center:\t%3.2f\t%3.2f\t%3.2f\n" % (center[0], center[1], center[2])
        #text +="Max:\t%3.2f\t%3.2f\t%3.2f\n" % (max[0], max[1], max[2])
        #text +="Min:\t%3.2f\t%3.2f\t%3.2f\n\n" % (min[0], min[1], min[2])
        text +="Points:\t%d\t%d\t%d\n\n" % (points[0], points[1], points[2])
        text +="Spacing:\t%3.3f Angstrom" % space
        self.setStringArea(self.ligand_widget_str["grinfo"],text)   
        # TODO add the tagging

    def SelectReceptor(self,*args):
        self.fileDialog(label="choose a receptor",callback=self.SelectReceptor_cb)
#        try :
#            self.fileDialog(label="choose a receptor",callback=self.SelectReceptor_cb)
#        except :
#            self.drawError("Sorry,problem")
            
    
    def SelectReceptor_cb(self,filename):
        if not filename: return False
        old = self.ReceptorFilename
        if self.fox.checkPDBQT_receptor(filename):
            # reset all the ligand style stuff..
            self.reset()
            self.ReceptorFilename = filename
            if DEBUG:
                print "SetReceptor> found a good one..."
                print "SetReceptor> now checking for residues_in_the_box..."

            """
            if not ReceptorGPF.get() == "" : # GridInfo?
                #print "SetReceptor> receptorGPF.get() seems not to be \"\" or None: ",ReceptorGPF.get() 
                rec_in_the_box = pdb_in_the_box()
                if rec_in_the_box and checkPDBQT_receptor(rec_in_the_box):
                    RecBoxFilename.set(rec_in_the_box)
                else:
                    if DEBUG: print "SetReceptor> it seems something went wrong with the res_in_the_box..."
                    rec_in_the_box = False
                    RecBoxFilename.set("")
                    return False""" # DISABLED CODE 

            if self.GridInfo:
                rec_in_the_box = self.fox.pdb_in_the_box(ReceptorFilename=self.ReceptorFilename,
                                                            ReceptorGPF=None,GridInfo=self.GridInfo)
                if rec_in_the_box and self.checkPDBQT_receptor(rec_in_the_box):
                    self.RecBoxFilename = rec_in_the_box # the file that's actually used for calculating the interactions
                else:
                    if DEBUG: print "SetReceptor> it seems something went wrong with the res_in_the_box..."
                    rec_in_the_box = False
                    self.RecBoxFilename = ""
                    return False              
            else:
                rec_in_the_box = False
                self.RecBoxFilename = ""

            # remove old receptor from the session
            if not old == "":
                old = os.path.basename(old)
                old_name = os.path.splitext(old)[0]
                if DEBUG: print "SelectReceptor> deleting previous receptor", old_name
                self.mv.deleteMol(old_name, log = 0)

            # load the new one # TODO to be reduced to loading function, then RecStyle
            self.ReceptorMolecule = self.mv.readMolecule(self.ReceptorFilename, log = 0)[0]
            name = os.path.basename(self.ReceptorFilename)
            name = os.path.splitext(name)[0]
            print self.ReceptorMolecule
#            cam = self.helper.getCamera(1)
#            cam.SelectCamera()
#            cam.tk.call(cam._w, 'makecurrent') 
#            cam.focus_set()
#            vi.SetCurrentObject(ReceptorMolecule.geomContainer.masterGeom)
#
#            #vi.SelectCamera()
            #mv.colorByAtomType(name, ['lines'], log=0)
            #mv.colorAtomsUsingDG(ReceptorMolecule, ['lines'], log=0)
            #mv.displayExtrudedSS(ReceptorMolecule, negate=False, only=False, log=0)
            #mv.displayCPK(ReceptorMolecule, log=0, cpkRad=0.0, scaleFactor=1.0, only=False, negate=False, quality=0)
            #mv.colorAtomsUsingDG(ReceptorMolecule, ['lines'], log=0)
#            resetview()
#            vi.Redraw()
#            # todo apply all the styles to the receptor
#            vi.SetCurrentObject(vi.rootObject)
#            # generate the list of residues
            self.FullResList, self.BoxResList = self.fox.ExtractResidues(self.ReceptorFilename,self.RecBoxFilename)
            self.RecStyle()
#            resetview('receptor')
            return True
            
    def pmv_name(self,filename):
        if DEBUG: print "pmv_name> got this filename", filename
        name = os.path.basename(filename)
        return os.path.splitext(name)[0]
        
    def GetResInTheBoxSubset(self):
        # subset is in PMV format
        subset = ""
        name = self.pmv_name(self.ReceptorFilename)
        for r in self.BoxResList:
            r = r.replace("_", ":",1)
            r = r.replace("_", "")
            subset += name+":"+r+";"
        if DEBUG: print "GetResInTheBoxSubset> selection [gridbox]", subset
        return subset

    def GetAllResSubset(self):
        subset = ""
        name = self.pmv_name(self.ReceptorFilename)
        for r in self.FullResList:
            r = r.replace("_", ":",1)
            r = r.replace("_", "")
            subset += name+":"+r+";"
        if DEBUG: print "GetAllResSubset> selection [all receptor residues]", subset
        return subset
    
    def ApplyLabel(self,subset):
        # ResidueLabelLevel
        #   all, interacting, filter, none
        if subset == None:
            return
        color = self.hex_to_rgb( LabelColor.get(), pmv = True )
        # show the labels
        mv.labelByProperty(subset, font={'fontRotateAngles':(0.0, 0.0, 0.0),'fontStyle':'solid3d','includeCameraRotationInBillboard':0,
            'fontScales':(0.6, 0.6, 0.02),'fontTranslation':(0.0, 0.0, 3.0),'billboard':1,
            'fontSpacing':0.2,'font':'arial1.glf'}, log=0, format=None, only=0, location='Last', negate=0, textcolor=color, properties=['name'])
            #'fontSpacing':0.2,'font':'arial1.glf'}, log=0, format=None, only=1, location='Last', negate=0, textcolor=(1.0, 1.0, 1.0,), properties=['name'])
        # color them
        # TODO set the correct color on the fly...
        #mv.color(subset, [color] , ['ResidueLabels'], log=0)

    def LigStyle(self,*args):
        pass
 
    def RecStyle(self,*args):
        """Performs receptor-related visualization options:
        	- visualize the selected subset/all 
        	- show representation
        	- apply color scheme
        
    
        # TODO NOTES
    
            - if a special halo style is going to be applied to interacting residues, they need to be *EXTRACTED* from the file
              generating both the "rigid" and the "flex" portions
    
        # for the buried-receptor mode, add the transparency to the sec.structure+backlines with automatically calculated back_color
    
        """    
#        global ReceptorMolecule # TODO possibly replaceable by name = pmv_name(xx)
#        global BoxResList
#        global LabelSTATUS
#        global IN_residues, OUT_residues, ACTIVE_residues, INACTIVE_residues
#        global current_full_rec_visible
#        global current_full_rec_mode 
#        global current_full_rec_color
#        global current_full_rec_flat_color
#        global current_box_visible
#        global current_box_mode
#        global current_box_color
#        global current_box_c_color
#        global current_ligand_interactions
#        global current_labelset
#        global current_labelcolor
#        global current_ACTIVE_residues, current_INACTIVE_residues
        # TODO FIX THE LACK OF 
    
   
        if not self.ReceptorMolecule:
            if DEBUG: print "No receptor yet... [EXIT]"
            return
    
        # get the current status
        name = self.pmv_name( self.ReceptorFilename)
        #get states from viz_option dialog
        print name  
        states = self.visOptions.getStates(box_visible=1,box_mode=1,box_color=1,
                                           full_rec_visible=1,
                                  full_rec_mode=1,full_rec_color=1,
                                  full_rec_flat_color=1,
                                  labelset=1,labelcolor=1)
#        box_visible = RecSubset.get() # which residues inside the box (inside, interacting, from filters) # vs current_showed
#        box_mode = RecBoxRepresentation.get() # style
#        box_color = RecBoxColormode.get() # color mode
#        box_c_color = hex_to_rgb (RecBoxCarbonColor.get() ) # carbon color
#        full_rec_visible = ShowAllRec.get() # visible
#        full_rec_mode = RecAllRepresentation.get() # style      "Lines", "Sticks", "Ball'n'Sticks", "Secondary structure" ,"CPK", "MSMS"
#        full_rec_color = RecAllColormode.get() # color mode     "Atom type", "DG colors", "Custom color" # last == flatcolor)
#        full_rec_flat_color = hex_to_rgb( RecAllFlatColor.get()) # carbon color
#        labelset = ResidueLabelLevel.get()  # labeling level     all, interacting, none
#        labelcolor = LabelColor.get()       # label color
#        if current_ligand:
#            ligand_interactions = current_ligand[0]
#        else:
#            ligand_interactions = None
#    
#        # TODO hic sunt leones: set all the current_* variables to None
#    
#        # define IN and OUT residues
#        if not IN_residues or not OUT_residues:
#            """
#            OUT_residues are always static (defined by the grid box size)
#            IN_residues are always static (defined by the grid box size)
#    
#            ACTIVE_residues are IN_residues that are visible (i.e. ligand-interaction or filter-based) ==> special style
#    
#            [potentially useless ] INACTIVE_residues are IN_residues that are not visible                                     ==> generic style
#    
#            """
#            if DEBUG: print "RecStyle> get the IN residues"
#            IN_residues = ""
#            if not len(GridInfo) < 5:
#                IN_residues = GetResInTheBoxSubset()
#    
#            if DEBUG: print "RecStyle> get the OUT residues"
#            all_protein_res = GetAllResSubset() #  Xtal:B:THR276;...;....; # TO BE USED FOR THE SECONDARY STRUCTURE REPRESENTATION!!!!
#            test_subset = IN_residues.split(";")
#            OUT_residues = ""
#            for res in all_protein_res.split(";"):
#                if res not in test_subset:
#                    OUT_residues += res+";"
#    
#        """
#        Three modes:
#    
#            - inside the grid-box
#                ACTIVE_residues     =   IN_residues
#                INACTIVE_residues   =   [empty]
#                
#            - interacting with the ligand
#                ACTIVE_residues     =   residues in contact (SHOW ONLY?)
#                #INACTIVE_residues  =   IN_residues - contacts
#    
#            - from filters
#                ACTIVE_residues     =   resideus from filters (SHOW ONLY)
#        """
#
#    
#    
#        INACTIVE_residues = ""
#        ACTIVE_residues = ""
#        # define ACTIVE and INACTIVE residues
#        if box_visible == "inside the grid-box":
#            ACTIVE_residues = IN_residues # the full inbox residue set is used
#        if box_visible == "from filters":
#            "extract the residues used in filters"
#            for f in filter_dictionary: # transform this into a separate function
#                r = filter_dictionary[f][0].get()
#                ACTIVE_residues += name+":"+r+";"
#            INACTIVE_residues = ""
#            active_res_list = ACTIVE_residues.split(";")
#            for res_in in IN_residues.split(";"):
#                if not res_in in active_res_list:
#                    INACTIVE_residues += res_in+";"
#        if box_visible == "interacting with ligand":
#            "extract the residues interacting with the ligand"
#            #if current_ligand and not current_ligand == current_ligand_interactions:
#            if current_ligand:
#                ACTIVE_residues = GetInteractions(current_ligand[1], pmv_format = True)
#                #print "Current ligand:", current_ligand[1]
#            #print" active_residues:", ACTIVE_residues
#            active_res_list = ACTIVE_residues.split(";")
#            for res_in in IN_residues.split(";"):
#                if not res_in in active_res_list:
#                    INACTIVE_residues += res_in+";"
#        #print "active:",len(ACTIVE_residues)
#        #print "inactive:",len(INACTIVE_residues)
#    
#    
#        """
#        # TODO use new Michel code...
#        cam = vi.cameras[1]
#        cam.SelectCamera()
#        cam.tk.call(cam._w, 'makecurrent') 
#        cam.focus_set()
#        vi.SetCurrentObject(ReceptorMolecule.geomContainer.masterGeom)
#        """
#    
#        rec_stick_thickness = .15 # cradius
#        rec_bnstick_thickness = 0.1 # cradius
#        # rec_balls_radius = 
#        
#        #raw_input("\n\nFULL_REC")
#        # Full receptor
#        if DEBUG: print "RecStyle> Change in FULL_REC_MODE", full_rec_mode
#        # Remove previous representations
#        if not current_full_rec_mode == full_rec_mode or current_full_rec_visible == full_rec_visible:
#            if current_full_rec_mode == None:
#                mv.displayLines(ReceptorMolecule,negate = True) # Default PMV mode
#            else:
#                mv.displayLines(OUT_residues,negate = True)
#    
#            mv.displaySticksAndBalls(OUT_residues, negate=True)
#            mv.displayCPK(OUT_residues, negate = True)
#            mv.displayMSMS(OUT_residues, negate = True) 
#            mv.displayExtrudedSS(ReceptorMolecule, negate=True, only=False, log=0) # keep ReceptorMolecule or use all_protein_res
#            if ShowAllRec.get():
#                if full_rec_mode == "Lines":
#                    print "\n\n\t\t\t someone asked for LINES on the rec\n\n"
#                    mv.displayLines(OUT_residues, negate=False, displayBO=False, only=False, log=0, lineWidth=1.0)
#                if full_rec_mode == "Sticks": 
#                    mv.displaySticksAndBalls(OUT_residues, log=0, cquality=0, sticksBallsLicorice='Licorice',
#                        bquality=0, cradius=rec_stick_thickness, only=False, bRad=0.3, negate=False, bScale=0.0)
#                if full_rec_mode == "Ball'n'Sticks": 
#                    mv.displaySticksAndBalls(OUT_residues, log=0, cquality=0, sticksBallsLicorice='Sticks and Balls',
#                        bquality=0, cradius=rec_bnstick_thickness, only=False, bRad=0.3, negate=False, bScale=0.0)
#                if full_rec_mode == "CPK":
#                    mv.displayCPK(OUT_residues, log=0, cpkRad=0.0, quality=24, only=False, negate=False, scaleFactor=1.0)
#                if full_rec_mode == "MSMS": # TODO set some transparency if this is True?
#                    mv.computeMSMS(OUT_residues, hdensity=6.0, hdset=None, log=0, density=5.0, pRadius=1.2, perMol=False,
#                        display=True, surfName='full_recMSMS')
#                if full_rec_mode == "Secondary structure":
#                    mv.displayExtrudedSS(ReceptorMolecule, negate=False, only=False, log=0)
#    
#    
#        # Inactive subset
#        #raw_input("\n\nINACTIVE SET")
#        # print "INACTIVE residues", INACTIVE_residues
#        if INACTIVE_residues:
#            #if not INACTIVE_residues == current_INACTIVE_residues or not full_rec_mode == current_full_rec_mode :
#            if True:
#                print "going to say something to the inactive"
#                time.sleep(1) 
#                mv.displayLines(current_INACTIVE_residues+current_ACTIVE_residues,negate = True)
#                mv.displaySticksAndBalls(current_INACTIVE_residues+current_ACTIVE_residues, negate=True)
#                mv.displayCPK(current_INACTIVE_residues+current_ACTIVE_residues, negate = True)
#                mv.displayMSMS(current_INACTIVE_residues+current_ACTIVE_residues, negate = True) 
#                if full_rec_mode == "Lines":
#                    mv.displayLines(INACTIVE_residues, negate=False, displayBO=False, only=False, log=0, lineWidth=1.0)
#                if full_rec_mode == "Sticks": 
#                    mv.displaySticksAndBalls(INACTIVE_residues, log=0, cquality=0, sticksBallsLicorice='Licorice',
#                        bquality=0, cradius= rec_stick_thickness , only=False, bRad=0.3, negate=False, bScale=0.0)
#                if full_rec_mode == "Ball'n'Sticks": 
#                    mv.displaySticksAndBalls(INACTIVE_residues, log=0, cquality=0, sticksBallsLicorice='Sticks and Balls',
#                        bquality=0, cradius=rec_bnstick_thickness, only=False, bRad=0.3, negate=False, bScale=0.0)
#                if full_rec_mode == "CPK":
#                    mv.displayCPK(INACTIVE_residues, log=0, cpkRad=0.0, quality=24, only=False, negate=False, scaleFactor=1.0)
#                if full_rec_mode == "MSMS":
#                    mv.computeMSMS(INACTIVE_residues, hdensity=6.0, hdset=None, log=0, density=5.0, pRadius=1.2, perMol=False,
#                        display=True, surfName='inactiveMSMS')
#        else:
#            mv.displayLines(ACTIVE_residues,negate = True)
#            mv.displaySticksAndBalls(ACTIVE_residues, negate=True)
#            mv.displayCPK(ACTIVE_residues, negate = True)
#            mv.displayMSMS(ACTIVE_residues, negate = True) 
#     
#    
#        # Active subset
#        #raw_input("\n\nACTIVE SET")
#        if box_mode == "Lines":
#            mv.displayLines(ACTIVE_residues, negate=False, displayBO=False, only=False, log=0, lineWidth=1.0)
#        if box_mode == "Sticks": 
#            mv.displaySticksAndBalls(ACTIVE_residues, log=0, cquality=0, sticksBallsLicorice='Licorice',
#                bquality=0, cradius=rec_stick_thickness, only=False, bRad=0.3, negate=False, bScale=0.0)
#        if box_mode == "Ball'n'Sticks": 
#            mv.displaySticksAndBalls(ACTIVE_residues, log=0, cquality=0, sticksBallsLicorice='Sticks and Balls',
#                bquality=0, cradius=rec_bnstick_thickness, only=False, bRad=0.3, negate=False, bScale=0.0)
#        if box_mode == "CPK":
#            mv.displayCPK(ACTIVE_residues, log=0, cpkRad=0.0, quality=24, only=False, negate=False, scaleFactor=1.0)
#        if box_mode == "MSMS":
#            mv.computeMSMS(ACTIVE_residues, hdensity=6.0, hdset=None, log=0, density=5.0, pRadius=1.2, perMol=False,
#                display=True, surfName='activeMSMS')
#         #print "labelset == 'interacting'", labelset == 'interacting'
#        #print "ligand_interactions == current_ligand_interactions", not ligand_interactions == current_ligand_interactions
#    
#        if not labelset == current_labelset or (labelset == 'interacting' and not ligand_interactions == current_ligand_interactions) :
#    
#            #mv.labelByProperty(name+"::", font={'fontRotateAngles':(0, 0, 0),'fontStyle':'solid','includeCameraRotationInBillboard':False,
#            #            'fontScales':(1.2, 1.2, 1.2),'fontTranslation':(0, 0, 3.0),'billboard':True,'fontSpacing':0.2,'font':'arial1.glf'}, log=0,
#            #            format=None, only=0, location='Last', negate=1, textcolor=(1.0, 1.0, 1.0,), properties=[])
#            print "Cleaning up old labels"
#            mv.labelByProperty(name+"::", negate=1)
#            subset = ""
#            if labelset == "all":
#                print "(all)"
#                subset = GetResInTheBoxSubset()
#            if labelset == "interacting":
#                print "(interacting)"
#                if current_ligand:
#                    subset = GetInteractions(current_ligand[1], pmv_format = True)
#            # TODO deal with None and Filters?
#            if not labelset == 'none':
#                print "applying new ones"
#                print "===\n\n", subset, "\n\n"
#                ApplyLabel(subset)
#    
#         #if DEBUG: print "COLOR = ", full_rec_color
#        #if not full_rec_color == current_full_rec_color:
#        # TODO Experimental
#        target = OUT_residues
#        print OUT_residues
#        if INACTIVE_residues:
#            target += INACTIVE_residues
#    
#        print "\n\n###\n"
#        print target
#        print "\n\n"
#        print "\n\n###\n"
#        if not full_rec_color == current_full_rec_color or not INACTIVE_residues == current_INACTIVE_residues:
#            if full_rec_color == "Atom type":
#                mv.colorByAtomType(target, ['lines', 'sticks', 'balls', 'full_recMSMS','inactiveMSMS','cpk', 'secondarystructure' ], log=0)
#            if full_rec_color == "DG colors" : 
#                mv.colorAtomsUsingDG(target, ['lines', 'sticks', 'balls', 'full_recMSMS','inactiveMSMS','cpk', 'secondarystructure' ], log=0)
#            if full_rec_color == "Secondary structure" : 
#                mv.colorBySecondaryStructure(target, ['lines', 'sticks', 'balls', 'full_recMSMS','inactiveMSMS','cpk', 'secondarystructure' ], log=0)
#            if full_rec_color == "Custom color": 
#                mv.color(target, [ full_rec_flat_color ],  ['lines', 'sticks', 'balls', 'full_recMSMS','inactiveMSMS','cpk', 'secondarystructure' ], log=0)
#    
#        # Box rec color 
#        #if not current_box_color == box_color:
#        if not box_color == current_box_color or not ACTIVE_residues == current_ACTIVE_residues or current_box_mode == current_box_mode: # TODO test this
#            if box_color == "Atom type":
#                mv.colorByAtomType(ACTIVE_residues, ['lines', 'sticks', 'balls', 'activeMSMS','cpk' ], log=0)
#                c_subset = ""
#                for x in ACTIVE_residues.split(";")[:-1]:
#                    c_subset += x+":C*;"
#                if DEBUG: print c_subset
#                mv.color(c_subset, [ box_c_color ],  ['lines', 'sticks', 'balls', 'activeMSMS','cpk' ], log=0)
#            if box_color == "DG colors" : 
#                mv.colorAtomsUsingDG(ACTIVE_residues, ['lines', 'sticks', 'balls', 'activeMSMS','cpk'], log=0)
#            if box_color == "secondary structure" : 
#                mv.colorBySecondaryStructure(ACTIVE_residues, ['lines', 'sticks', 'balls', 'activeMSMS','cpk' ], log=0)
#    
#        # TODO Label colors?
#    
#        # TODO verify this...
#        current_full_rec_visible = full_rec_visible 
#        current_full_rec_mode = full_rec_mode 
#        current_full_rec_color = full_rec_color
#        current_full_rec_flat_color = full_rec_flat_color 
#        current_box_visible = box_visible
#        current_box_mode = box_mode
#        current_box_color = box_color
#        current_box_c_color = box_c_color
#        current_ligand_interactions = ligand_interactions
#        current_ACTIVE_residues = ACTIVE_residues
#        current_INACTIVE_residues = INACTIVE_residues
#    
#        #resetview()
#        #vi.Redraw()
#        #vi.SetCurrentObject(vi.rootObject)
#    
#    
#        print " ======================== RecStyle END ======================\n\n\n"
        return

self = None
if self : #if we are n pmv
    #require a master   
    foxui = foxGui(title= "Fox-tk",master=self.GUI.VIEWER)
    foxui.setup()
    #tetraui.helper.setViewer(vi)            
elif uiadaptor.host == "tk":
#    import DejaVu
#    DejaVu.enableVBO = True    
#    from DejaVu import Viewer
#    vi = Viewer()    
    #require a master   
    foxui = foxGui(title= "Fox-tk",master=None)
    foxui.setup()
    #tetraui.helper.setViewer(vi)
elif uiadaptor.host == "qt":
    from PySide import QtGui
    app = QtGui.QApplication(sys.argv)
    foxui = foxGui(title="Fox-qt")
    foxui.setup()
else :
    foxui = foxGui(title= "Fox-"+uiadaptor.host)
    foxui.setup()
#call it
foxui.display()

foxui.initialisation()
if "epmv" in sys.argv :
    foxui.setViewer(type="epmv")
if "pmv" in sys.argv :  
    foxui.setViewer(type="pmv")
if uiadaptor.host == "qt": app.exec_()

#c4d :
#execfile("/Users/ludo/DEV/upy/trunk/upy/examples/fox_upy.py")


