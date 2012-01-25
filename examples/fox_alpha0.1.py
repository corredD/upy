#!/usr/bin/env python
# Tk Virtual Screening Interface for AutoDock
#
# v.0.0.1  Stefano Forli
#
# Copyright 2010, Molecular Graphics Lab
# 	The Scripps Research Institute
#	    _  
# 	   (,)  T  h e
#	  _/
#	 (.)    S  c r i p p s
#	   \_
#	   (,)  R  e s e a r c h
#	  ./  
#	 ( )    I  n s t i t u t e
#	  '
#
#

# Project Coati 2010

# TODO add the try/except mode for the imports
from Tkinter import *
from tkFileDialog   import *
from tkMessageBox import *
import Pmw
from glob import glob
import tkColorChooser
import os
import Image
import ImageTk
from sys import argv
import shutil
from numpy import array

from MolKit import Read
from AutoDockTools.Docking import Docking
from mglutil.math.rmsd import RMSDCalculator
from AutoDockTools.InteractionDetector import InteractionDetector
from AutoDockTools import VSResultFilters
import time
from operator import itemgetter # used for sorting ligands by energy

from AutoDockTools.VSResultFilters import EnergyFilter, ClusterSizeFilter, ClusterPercentageFilter, LigandEfficiencyFilter, HydrogenBondInteractionFilter, CloseContactInteractionFilter 


from string import find
from MolKit import Read
from MolKit.pdbWriter import PdbWriter



DEBUG = False
try:
    if argv[1]:
        print "\n\n##################################\n # DEBUG MODE ACTIVATED\n####################################\n\n"
        DEBUG = True
except:
    pass




root = Tk()
root.title('Fox | AutoDock VS')


#root.option_add("*Font", "helvetica 9") # bold")
#root.option_add("*Font", "arial 9 bold")



pmvroot = Toplevel()
pmvroot.withdraw()

Pmw.initialise()

nb = Pmw.NoteBook(root)
Tab1 = nb.add('Input data')
Tab2 = nb.add('Filter & Analysis')
Tab3 = nb.add('Viewer')
Tab4 = nb.add('Export')
#Tab5 = nb.add('EXPERIMENTS')

nb.pack(padx=3, pady=5, fill=BOTH, expand=1)





##########################
### Visualization options
###

#AAlevel = IntVar(value = 0)
AAlevel = StringVar(value = "low")
# style
PresetStyle = StringVar(value = "Default")

# ligand
LigRepresentation = StringVar(value = "Sticks") # default ligand representation
LigColormode = StringVar(value = "Atom type") # default ligand color scheme
LigCarbonColor = StringVar(value = "#ffcc00") # default ligand carbon atoms (green)

# receptor

RecBoxRepresentation = StringVar(value = "Sticks")
RecBoxColormode = StringVar(value = "Atom type")
RecBoxCarbonColor = StringVar(value = "#00ff00")
RecAllRepresentation = StringVar(value = "Secondary structure")
RecAllColormode = StringVar(value = "Custom color")
RecAllFlatColor = StringVar(value = "#888888")
RecSubset = StringVar(value = "inside the grid-box") # default subset of receptor that's visible
ShowAllRec = BooleanVar(value = True) # Show or not the entire receptor structure
LabelColor = StringVar(value = "#ffff00") # default yellow

# interactions
IntShowHB = BooleanVar(value = True)
IntShowVDW = BooleanVar(value = True)
IntShowElec = BooleanVar(value = True)
IntShowCatP = BooleanVar(value = True)
IntShowPP = BooleanVar(value = True)
IntShowDist = BooleanVar(value = True)
ResidueLabelLevel = StringVar(value = "none") # "all" = all residues in the grid box; "interacting" = close contact residues; "none" = off
SetHighlightRes = BooleanVar(value = True) # TODO probably obsolete
SetHighlightRes_interacting = BooleanVar(value = True)
SetHighlightRes_filtering = BooleanVar(value = True)


CenterViewOption = StringVar(value = "grid box")
CenterViewOption = StringVar(value = "[ off ]")

#########################
# Names and file handles

# receptor
ReceptorFilename = StringVar(value = "")
ReceptorFilenameLabel = StringVar(value = "")
RecBoxFilename = StringVar()
ReceptorGPF = StringVar(value = "")
ReceptorGPFLabel = StringVar(value = "")
GPFpdbFilename = StringVar()


###################################
# defaults ########################

DefaultRMStol = 2.0
#PoseMode = StringVar(value = "le") # clarify? TODO
PoseChoice = StringVar(value = "Lowest energy in largest cluster") # clarify? TODO
IgnoreGPFmismatch = BooleanVar(value = False)

CurrentSessionRMStol = None # initialized as null, then the first ligand found will set the sesion valiue
ClusTolerance = DoubleVar(value = DefaultRMStol)
ForceReclustering = BooleanVar(value = False) # default for forcing reclustering of all dlgs [ openLigandDirRecursive]
if ForceReclustering.get():
    print "forcerecluster is true!"
LigandListLabel = StringVar(value = "Import ligands...")
SimpleBool = StringVar(value="all") # default Boolean value for the interaction filter

ClusterGenPose = StringVar(value = "LE and LC") # "LE and LC", "LE only", "LC only"
ClusterSaveInter = BooleanVar(value = True)
ClusterHB = BooleanVar(value = True)
ClusterVDW = BooleanVar(value = True)
ClusterPP = BooleanVar(value = False)
BGcolor = StringVar(value = "#aaaaaa")

MAX_BUTTONS = 10


# Default filter values

default_EnergyMinimum = -3.
default_EnergyMaximum = -30.
default_Cluster_percent_min = 0.
default_Cluster_percent_max = 100
default_Cluster_pop_min = 0
default_Cluster_pop_max = 9999
default_Cluster_mode = "%"
default_LigEfficiency_min = 0.
default_LigEfficiency_max = -9.

# Inizialization of filtering + defaults
Emin = DoubleVar(value = default_EnergyMinimum)
Emax = DoubleVar(value = default_EnergyMaximum)
ClustCount = StringVar(value = default_Cluster_mode)
if default_Cluster_mode == "#":
    ClustMin = DoubleVar(value = default_Cluster_pop_min)
    ClustMax = DoubleVar(value = default_Cluster_pop_max)
else:
    ClustMin = DoubleVar(value = default_Cluster_percent_min)
    ClustMax = DoubleVar(value = default_Cluster_percent_max)
LEmin = DoubleVar(value = default_LigEfficiency_min)
LEmax = DoubleVar(value = default_LigEfficiency_max)


# import DLG options
IgnoreIncomplete = BooleanVar(value = True)
IgnoreRecMismatch = BooleanVar(value = False)

# export defaults
ExportLevel = StringVar(value = "selected only")

ExportDockings = BooleanVar(value = True)
ExportReport = BooleanVar(value = True)
ExportLigList = BooleanVar(value = True)

ExportBox = BooleanVar(value = True)
ExportRec = BooleanVar(value = True)
ExportParm = BooleanVar(value = True)
ExportMap = BooleanVar(value = True)

ExportReportFormat = StringVar(value = 'HTML') # "PDF", "HTML", "[ off ]"
Export2Dpic = BooleanVar(value = False)
Export3Dpic = BooleanVar(value = True)
ExportNotes = BooleanVar(value = True)
ExportStructureFormat = StringVar(value = 'PDBQT')
ExportListFormat = StringVar(value = 'CSV') # "CSV", "names list", "[ off ]"
SnapshotFormat = StringVar(value = 'jpg')


#######################
#### END VARIABLES ####
#######################



# runtime variables
to_be_reclustered = []
current_ligand = None
CurrentPage = 0 # CIntVar()
TEMPDIR = ".vs_temp" # move it to the home user path?
SNAPSHOT_DIR = TEMPDIR+os.sep+"snapshots"
REC_CACHE_DIR = TEMPDIR+os.sep+"receptor_grid_boxes"
snapshot_list = {}
NotesList = {}
ViewerLabel = StringVar(value = "Viewer options>>")
ReceptorMolecule = None
FilteredLigands = None
GPFboxMolName = None
#ligand_mol = None
ligand_filename = None
sticky_ligands = []
LigandName = StringVar(value ="") # name of the ligand in the Viewer info panel
ReferenceLigand = None # 

EnergySurvivors = StringVar(value = "     \t     ")
ClusterSurvivors = StringVar(value = "     \t     ")
LESurvivors = StringVar(value = "     \t     ")
InFilterSurvivors = StringVar(value = "     \t     ")
GridInfo = {} # Global, to be updated when deleting ligands """spacing, [pts], [center],[max],[min]"""
IN_residues, OUT_residues = None, None

current_full_rec_visible = None
current_full_rec_mode = None
current_full_rec_color= None
current_full_rec_flat_color = None
current_box_visible= None
current_box_mode = None
current_box_color = None
current_box_c_color= None
current_ligand_interactions= None
current_labelset = None
current_labelcolor = None
IN_residues = None
OUT_residues = None

LigBook = {} # The Great Book of Results
"""
The format is:
	{ lig_name : { path : "/full/path/to/the/folder/with_dlg/"
				   vs : "/full/path/to/the/xxx_vs.pdbqt"
				   le : "/full/path/to/the/xxx_le.pdbqt"
				   lc : "/full/path/to/the/xxx_vs_lc.pdbqt"
                   # TODO ADD GRID CHECK?
				   dlg: "[ list of dlg filenames ]"
				   rec: "/full/path/to/the/receptor.pdbqt"
				   recluster : True/False
				   selected : True/False
                   passed : True/False # if the filters are passed (default: True)
                   snapshot : path? TODO check if we want this and if this can store a temp-file name
				}
	}

"""

# TODO set up a generalized output dir creation

TEMPDIR = os.getcwd()+os.sep+TEMPDIR

if not os.path.exists(TEMPDIR):
    try:
        os.makedirs(TEMPDIR, 0755)
    except:
        showerror(root, "Error!", ("Impossible to write in the following path:\n\n%s\n\nBe sure the current user has enough privileges to access to it and that there's enough disk space left.\n\nQuit") % TEMPDIR )
        exit()
    
if not os.path.exists(REC_CACHE_DIR):
    try:
        os.makedirs(REC_CACHE_DIR, 0755)
    except:
        showerror(root, "Error!", ("Impossible to write in the following path:\n\n%s\n\nBe sure the current user has enough privileges to access to it and that there's enough disk space left.\n\nQuit") % REC_CACHE_DIR )
        exit()
    



def get_lines(filename):
    f = open(filename, 'r')
    lines = f.readlines()
    f.close()
    return lines

def dist(firstatom, secondatom):  
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



def pdb_in_the_box():
    # tolerance?
    tol = 3 # Angstrom outside the box
    tol = 1.
    
    # to include residues as well?
   
    #if (not ReceptorGPF.get() or len(GridInfo) == 0) or not ReceptorFilename.get():
    if len(GridInfo) == 0 or not ReceptorFilename.get():
        if DEBUG: print "pdb_in_the_box> nothing to do for me... returning"
        return False

    PDB_IN = []
    PDB_OUT = []
    coord1 = []
    coord2 = []

    rec = ReceptorFilename.get()
    filename = os.path.basename(rec)

    # purge mechanism to the "IN_THE_BOX" string
    filename = filename.replace("_IN_THE_BOX", "")
    filename = filename.rsplit(".", 1)[0]+'_IN_THE_BOX.pdbqt'
    out_name = REC_CACHE_DIR + os.sep + filename
    #REC_CACHE_DIR = TEMPDIR+os.sep+"receptor_grid_boxes"
    
    if out_name == rec:
        if DEBUG: print "pdb_in_the_box> avoiding to overwrite the rec input file (input and output are the same)"
        return True
    
    try: 
        PDB_IN = get_lines(rec)
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
            GPF = open(ReceptorGPF.get(), 'r')
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
    
    
    



def get_ligand_info(ligand, data = None):
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
    if ligand in LigBook.keys():
        """
        if not LigBook[ligand]['vs'] == '':
            filename = LigBook[ligand]['vs']
        else:
            filename = LigBook[ligand][PoseMode.get()] # "le" or "lc"
        """
        filename = get_current_pose(ligand)
        if DEBUG:
            l = LigBook[ligand]
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
        lines = get_lines(filename)
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
        
    #if DEBUG: print "get_ligand_info> No energy found! not a PDBQT+ file :\t", filename
    #return False



def get_ligand_info_new(ligand, data = None):
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
    if ligand in LigBook.keys():
        """
        if not LigBook[ligand]['vs'] == '':
            filename = LigBook[ligand]['vs']
        else:
            filename = LigBook[ligand][PoseMode.get()] # "le" or "lc"
        """
        filename = get_current_pose(ligand)
        if DEBUG:
            l = LigBook[ligand]
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
        lines = get_lines(filename)
    except:
        if DEBUG: print "problem reading file", filename
        return False
    #print "PROCESSING", ligand

    IN = False
    IN_hb = False
    IN_vdw = False
    count_hb = 0
    count_vdw = 0

    for l in lines: # TODO OBSOLETE, THIS SHOUOLD BE MADE WITH THE DICTIONARY!
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
        
    #if DEBUG: print "get_ligand_info> No energy found! not a PDBQT+ file :\t", filename
    #return False





def about():  
	Pmw.aboutversion('0.0.1')
	Pmw.aboutcontact(
	    'Stefano Forli\n' +
	    '  email: forli@scripps.edu\n\n' +
	    'Ruth Huey\n' +
	    '  email: rhuey@scripps.edu\n' 
	    )
	Pmw.aboutcopyright('Copyright MGL Lab 2009\nThe Scripps Research Institute\nAll rights reserved')
	about = Pmw.AboutDialog(root, applicationname='AutoDockVS Interface')

#root.mainloop()


def makemenu(win):
	return
"""
    top = Menu(win)       
    win.config(menu=top)
    
    file = Menu(top, tearoff=0)
    file.add_command(label='New...',  command=notdone,  underline=0)
    file.add_command(label='Open job configuration...', command=notdone,  underline=0)
    file.add_command(label='Save job configuration...', command=notdone,  underline=0)
    file.add_command(label='Quit',    command=win.quit, underline=0)
    top.add_cascade(label='File',     menu=file,        underline=0)

    setup = Menu(top, tearoff=0)
    setup.add_command(label='Specify prepare script location',     command=notdone,  underline=0)
    setup.add_command(label='Specify Babel binary location',   command=notdone,  underline=0)
    setup.add_separator()
    top.add_cascade(label='Setup',     menu=setup,        underline=0)

    submenu = Menu(setup, tearoff=0)
    submenu.add_command(label='A', command=win.quit, underline=0)
    submenu.add_command(label='B', command=notdone,  underline=0)
    setup.add_cascade(label='Stuff',   menu=submenu,     underline=0)

    help = Menu(top, tearoff=0)
    help.add_command(label='Help (on line)',  command=notdone,  underline=0)
    help.add_command(label='About VS_prepare',  command=about,  underline=0)
    top.add_cascade(label='Help',     menu=help,        underline=0)"""

def addPmvCamera(pmv,master,stereo=None):
        #print "dockCamera"
        self = pmv.GUI
        # to avoid going twice in the func at startup as it creates 
        # problems if _pmvrc contains a call to dockCamera()
        if     self.vwrCanvasDocked.winfo_ismapped() == 0 \
           and self.vwrCanvasFloating.winfo_ismapped() == 0 \
           and self.floatCamVariable.get() == 0 :
                return

        #if self.vwrCanvasDocked.winfo_ismapped():
            # the camera is already docked
        #    return
        #else:
        if self.floatCamVariable.get() == 1:
                self.floatCamVariable.set(0)
        vi = self.VIEWER
        vi.stopAutoRedraw()

        # get the position and the height of the floating camera
        cam = vi.currentCamera
        camx = cam.rootx
        camy = cam.rooty
        camheight = cam.height
        camwidth = cam.width
        # the currentCamera is floating
        # save the floating camera state
        camState = cam.getState()
        fogState = cam.fog.getState()
        camCallbacks = cam.eventManager.eventHandlers
        if stereo is None:
            if cam.stereoMode == 'STEREO_BUFFERS':
                stereo = 'native'
            else:
                stereo = 'none'
        self.vwrCanvasFloating.withdraw()
        print "TRACER ###########################"
        # withdraw the trackball gui (because it belongs to the camera)
        cam.trackball.hideSpinGui()

        # Create a new camera in a frame?
        print master
        lNewCam = vi.AddCamera(master=master, stereo=stereo)
        
        # attach the new trackball gui to the viewergui
        vi.GUI.spinMenuButton.configure(command=lNewCam.trackball.toggleSpinGui)
        lNewCam.trackball.set(cam.trackball)

        # Delete the floating camera
        lNewCamIndex = len(vi.cameras) - 1
        #lNewCam = vi.cameras[lNewCamIndex]
        lNewCam.shareCTXWith = vi.cameras[0].shareCTXWith
        lNewCam.shareCTXWith.remove(lNewCam)
        lNewCam.shareCTXWith.append(vi.cameras[0])
        del(vi.cameras[0].shareCTXWith)
        lNewCam.SelectCamera()
        cam.Set(height=vi.cameras[0].height, width=vi.cameras[0].width)
        lCamTemp = vi.cameras[0]
        vi.cameras[0] = vi.cameras[lNewCamIndex]
        vi.cameras[lNewCamIndex] = lCamTemp
        vi.DeleteCamera(vi.cameras[lNewCamIndex])
        cam = vi.currentCamera
        print master

        # Restore the state of the floating camera
        lNewCamState = cam.getState()
        for key, value in lNewCamState.items():
            if camState.has_key(key) and value == camState[key]:
                camState.pop(key)
        apply(cam.Set,(1, 0),camState )
        apply(cam.fog.Set,(), fogState)
        vi.startAutoRedraw()
        # See if infobar then need to pack it before infobar.
        if hasattr(self,'infoBar'):
            infobar = self.infoBar
            w1 = self.vf.showHideGUI.getWidget('MESSAGE_BOX')
            if w1.winfo_ismapped():
                self.vwrCanvasDocked.pack(before=w1,anchor='n',
                                          expand=1, fill='both')            
            elif infobar.winfo_ismapped():
                self.vwrCanvasDocked.pack(before=infobar,anchor='n',
                                          expand=1, fill='both')
            else:
                self.vwrCanvasDocked.pack(anchor='n', expand=1, fill='both')
        else:
            self.vwrCanvasDocked.pack(anchor='n',expand=1, fill='both')

        cam.Expose()  #to update projection
        cam.Enter_cb() # as current Camera
        #self.addCameraCallback('<KeyPress>', self.updateInfoBar)
        #self.addCameraCallback('<KeyRelease>',self.updateInfoBar)
        events = ['<KeyPress>', '<KeyRelease>']
        for event in events:
            for cb in camCallbacks[event]:
                if not cb in cam.eventManager.eventHandlers[event]:
                    self.addCameraCallback(event, cb)

        # Overwrite the Camera DoPick by the viewerFramework DoPick method.
        cam.DoPick = self.vf.DoPick

        # Need to reposition and resize the menubar.
        menux, menuy, menuw, menuh = self.getGeom()

        width = max(menuw, camwidth)
        height = menuh + camheight
        self.setGeom(camx, 0, width, height)
        crooty = menuy+menuh-30
        cam.Set(rootx=camx, rooty=crooty,
                             width=width, height=camheight)
        if self.vf.logMode != 'no':
            txt = "self.GUI.dockCamera(stereo=\""+str(stereo)+"\")"
            self.vf.log(txt)
            self.MESSAGE_BOX.append(txt+"\n")
  


def UpdateGridInfo():
    global TargetInputInfo
    if DEBUG: print "UpdateGridInfo> start"
    if len(LigBook) == 0 or len(GridInfo) < 5:
        null = [0.,0.,0.]
        center = null
        points = null
        min = null
        max = null
        space = 0

    else: # len(GridInfo) == 5:
        center = GridInfo['center']
        points = GridInfo['pts']
        #max = GridInfo['max']
        #min = GridInfo['min']
        space = GridInfo['spacing']
    """
    else:
        null = [0.,0.,0.]
        center = null
        points = null
        min = null
        max = null
        space = 0
    """

    text = "\t X\t Y\t Z\n"
    text +="Center:\t%3.2f\t%3.2f\t%3.2f\n" % (center[0], center[1], center[2])
    #text +="Max:\t%3.2f\t%3.2f\t%3.2f\n" % (max[0], max[1], max[2])
    #text +="Min:\t%3.2f\t%3.2f\t%3.2f\n\n" % (min[0], min[1], min[2])
    text +="Points:\t%d\t%d\t%d\n\n" % (points[0], points[1], points[2])
    text +="Spacing:\t%3.3f Angstrom" % space


    TargetInputInfo.config(state = NORMAL)
    TargetInputInfo.delete(1.0,END)
    TargetInputInfo.insert(END, text)
    TargetInputInfo.config(state = DISABLED)
    # TODO add the tagging

def openLigandDir(ligDir = None, recursive = False):
    """
    - prompt the user (or not) to [scan a directory containing DLG|import dlgs from a dir] and PDBQT+ files.
    - integrity check:
        - all the ligands found in the DLG must have a PDBQT+ file
        - if not, produce the list of files to be processed
    """


    # TODO make a function to parse DLG automatically?


    VS_results_list = []
    LE_results_list = []
    LC_results_list = []
    dlg_list = []
    ligands_list = [] # TODO potentially useless

    global to_be_reclustered, CurrentSessionRMStol
    global GridInfo # initialized with the first dlg to contain all GPF relevant info

    if not ligDir:
        ligDir = askdirectory(title = "Select a directory to be scanned")
    if not ligDir:
        return
    else:
        if recursive:
            for root, subFolders, files in os.walk(ligDir):
                for file in files:
                    if file[-9:] == "_vs.pdbqt": # ./faah8621_ZINC02026051_xJ1_xtal/ZINC02026051_vs.pdbqt
                        VS_results_list.append(os.path.join(root,file))
                    if file[-12:] == "_vs_le.pdbqt": # ./faah8621_ZINC02026051_xJ1_xtal/ZINC02026051_vs_le.pdbqt
                        LE_results_list.append(os.path.join(root,file))
                    if file[-12:] == "_vs_lc.pdbqt": # ./faah8621_ZINC02026051_xJ1_xtal/ZINC02026051_vs_lc.pdbqt
                        LC_results_list.append(os.path.join(root,file))
                    if file[-3:] == "dlg": 
                        dlg_list.append(os.path.join(root,file))
        else:
            VS_results_list = glob(os.path.join(ligDir, "*_vs.pdbqt"))
            LE_results_list = glob(os.path.join(ligDir, "*_vs_le.pdbqt"))
            LC_results_list = glob(os.path.join(ligDir, "*_vs_lc.pdbqt"))
            dlg_list = glob(os.path.join(ligDir, "*.dlg"))
            # print len(VS_results_list), len(LE_results_list), len(LC_results_list), len(dlg_list)

        problematic_dlg = []
        # identify the ligands
        ignore_grid_problems = IgnoreGPFmismatch.get()
        recently_added = []
        for d in dlg_list:
            name, rec = None, None
            #if True:
            try:
                #file = open(d, 'r')
                #dlg = file.readlines()
                #file.close()
                dlg = get_lines(d)

                if not IgnoreIncomplete.get():
                    success = False
                    for i in dlg[-5:]:
                        if "Success" in i:
                            success = True
                            break
                else:
                    success = True
                if not success: # TODO to be mapped with the button
                    if DEBUG: print "openLigand> unsuccessfull DLG ignored..."
                    break 
                current_ligand_GridInfo = {}
                for l in dlg:


                    if "DPF> move" in l:
                        name = l.split()[2] # DPF> move 001717_MC.pdbqt
                        name = name.split(".")[0]  # 001717_MC

                    if "Macromolecule file used to create Grid Maps" in l:
                        rec = l.split()[-1]


                    """
                    if "DPF> map" in l:
                        rec = l.split()[2]
                        rec = rec.rsplit(".",2)[0]+".pdbqt" # Check this!
                    """


                    if not len(current_ligand_GridInfo) == 5: # populate the GridInfo for the current ligand
                        if "Grid Point Spacing" in l:
                            if not 'spacing' in current_ligand_GridInfo.keys():
                                if DEBUG: print "OpenLigandDir> updating current ligand GridInfo dictionary... [spacing]"
                                current_ligand_GridInfo['spacing'] = float(l.split()[-2])
                        if "Even Number of User-specified Grid Points" in l and "x-points" in l:
                            if not 'pts' in current_ligand_GridInfo.keys():
                                if DEBUG: print "\n\nOpenLigandDir> updating the current ligand GridInfo dictionary... [x_pts]"
                                x = [ float(l.split()[-2]) ]
                                current_ligand_GridInfo['pts'] = x
                        if " y-points" in l:
                            if DEBUG: print "\n\nOpenLigandDir> updating the current ligand GridInfo dictionary... [y_pts]"
                            y = float(l.split()[-2])
                            current_ligand_GridInfo['pts'].append(y)
                        if " z-points" in l:
                            if DEBUG: print "\n\nOpenLigandDir> updating the current ligand GridInfo dictionary... [z_pts]"
                            z = float(l.split()[-2])
                            current_ligand_GridInfo['pts'].append(z)
                        if "Coordinates of Central Grid Point of Maps" in l:
                            if DEBUG: print "\n\nOpenLigandDir> updating the current ligand GridInfo dictionary... [center]"
                            # Coordinates of Central Grid Point of Maps = (23.882, -5.295, -0.726)
                            l = l.split("=")[1]
                            l = l.replace("(", "")
                            l = l.replace(")", "")
                            l = l.split(",")
                            current_ligand_GridInfo['center'] = [ float(l[0]), float(l[1]), float(l[2]) ]
                        if "Minimum coordinates in grid" in l:
                            if DEBUG: print "\n\nOpenLigandDir> updating the current ligand GridInfo dictionary... [min]"
                            l = l.split("=")[1]
                            l = l.replace("(", "")
                            l = l.replace(")", "")
                            l = l.split(",")
                            current_ligand_GridInfo['min'] = [ float(l[0]), float(l[1]), float(l[2]) ]
                        if "Maximum coordinates in grid" in l:
                            if DEBUG: print "\n\nOpenLigandDir> updating the current ligand GridInfo dictionary... [max]"
                            l = l.split("=")[1]
                            l = l.replace("(", "")
                            l = l.replace(")", "")
                            l = l.split(",")
                            current_ligand_GridInfo['max'] = [ float(l[0]), float(l[1]), float(l[2]) ]

                    # TODO TODO TODO BUGGY BUGGY
                    if len(current_ligand_GridInfo) == 5 and not len(GridInfo) == 5:
                        if DEBUG: print "openLigandDir> First GridInfo population completed. Initialized GridInfo with the current ligand" 
                        GridInfo = current_ligand_GridInfo
                        if DEBUG: print "GI",GridInfo
                        if DEBUG: print "cGI",current_ligand_GridInfo
                    
                    if not ignore_grid_problems:
                        # TODO This doesn't work... FIND A MORE ROBUST METHOD (gives always false positive when importing two dir series)
                        if len(current_ligand_GridInfo) == 5 and not GridInfo == current_ligand_GridInfo:
                            if DEBUG:
                                print "openLigandDir> Grid data mismatch!"
                                print GridInfo
                                print current_ligand_GridInfo
                            text = "The grid data from a DLG doesn't match with the current session grid data.\n\n"
                            text +="File: "+d
                            text +="\n\nCurrent session:\n"
                            text +="    Center   [%3.2f,%3.2f,%3.2f]\n" % (GridInfo['center'][0],GridInfo['center'][1], GridInfo['center'][2] )
                            text +="    Points   [%d,%d,%d]\n" % (GridInfo['pts'][0], GridInfo['pts'][1], GridInfo['pts'][2])
                            text +="    Spacing  %3.3f\n" % GridInfo['spacing']
                            text +="\nDLG values:\n"
                            text +="    Center   [%3.2f,%3.2f,%3.2f]\n" % (current_ligand_GridInfo['center'][0],current_ligand_GridInfo['center'][1], current_ligand_GridInfo['center'][2] )
                            text +="    Points   [%d,%d,%d]\n" % (current_ligand_GridInfo['pts'][0], current_ligand_GridInfo['pts'][1], current_ligand_GridInfo['pts'][2])
                            text +="    Spacing  %3.3f\n" % current_ligand_GridInfo['spacing']
                            text +="\n\nStop the current import process?"

                            if askyesno(title = "Grid data mismatch", message = text):
                                if DEBUG: print "openLigandDir> USER INTERRUPTION"
                                #showinfo(title = "Results import process", message = "Import process aborted by the user.\nrid mismatches, disable the option in the Import Menu.")
                                return False
                            else:
                                showwarning(title = "Results import process", message = "Ignoring further grid data mismatches.\n\n [be sure you know what you're doing]")
                                ignore_grid_problems = True

                    if len(GridInfo) == 5 and name and rec:
                        if not name in LigBook:
                            if DEBUG: print "openLigandDir> new ligand, initialized", name
                            path = os.path.dirname(d)
                            le = ""
                            lc = ""
                            vs = "" 
                            #dlg_files = [d]
                            LigBook[name] = { "path" : path,
                                              "le" : le,
                                              "lc" : lc,
                                              "vs" : vs,
                                              "dlg": [d],
                                              "rec": rec, 
                                              "recluster" : True,   #False, # True by default?
                                              "rmstol" : -1,
                                              "selected" : False,
                                              "passed" : True}
                            recently_added.append(name)
                        else:
                            if not d in LigBook[name]["dlg"]:
                                if LigBook[name]["rec"] == rec or IgnoreRecMismatch.get():
                                    if not d in LigBook[name]["dlg"]:
                                        LigBook[name]["dlg"].append(d)
                                else:
                                    if DEBUG: print "######################\nWARNING! receptor inconsistency found!\n########################3"
                                        
                        #DPF> map receptor.A.map                   # atom-specific affinity map
                        UpdateGridInfo()
                        break
            except:
            #else:
                if DEBUG: print "WARNING: problems in reading %s [skipping]" % d
                problematic_dlg.append(d)
        if len(problematic_dlg):
            if DEBUG: print "openLigandDir> %d problematics DLGs" % len(problematic_dlg)
            showwarning(title = "Results import process", message = "%d DLGs have been ignored for problems." % len(problematic_dlg))
            # TODO add a tool for inspecting...

        if DEBUG: print "found %d dlgs => %d ligands" % ( len(dlg_list), len(LigBook))
        for i in recently_added:
            LigandScrolledListBox.insert('end', i)


            
    if not ForceReclustering.get(): # TODO do I want to have this here? this will affect all the newly loaded ligands...!!!!
        # populate the LE and LELC entries for every ligand
        # global to_be_reclustered ?
        rms_found = None
        for n in recently_added:
            if DEBUG: print "openLigandDir> Scanning RECENTLY ADDED ligand ", n
            found = 0
            for vs in VS_results_list:
                vs_path =  os.path.dirname(vs)    
                vs_name =  os.path.basename(vs)[:-9]  # ./faah8621_ZINC02026051_xJ1_xtal/ZINC02026051_vs.pdbqt -> ZINC02026051
                if vs_name == n:
                    found = 2
                    LigBook[n]["vs"] = vs
                    if DEBUG: print "\n\tfound the UNIQUE conformation result", vs
                    break
                #else:
                #    if DEBUG: print "\n\tNAME MISMATCH", vs_name, n

            if found == 0:
                for lc in LC_results_list:
                    lc_path =  os.path.dirname(lc)   
                    lc_name =  os.path.basename(lc)[:-12]  # ./faah8621_ZINC02026051_xJ1_xtal/ZINC02026051_vs_lc.pdbqt -> ZINC02026051
                    if lc_name == n:
                        LigBook[n]["lc"] = lc
                        found += 1
                        if DEBUG: print lc_name, "\n\tfound the LC conformation result", vs
                        break
                    #else:
                    #    if DEBUG: print "\n\tNAME MISMATCH", lc_name, n

                for le in LE_results_list:
                    le_path =  os.path.dirname(le)   
                    le_name =  os.path.basename(le)[:-12]  # ./faah8621_ZINC02026051_xJ1_xtal/ZINC02026051_vs_le.pdbqt -> ZINC02026051
                    if le_name == n:
                        found += 1
                        LigBook[n]["le"] = le
                        if DEBUG: print le_name, "\n\tfound the LE conformation result", vs
                        break
                    #else:
                    #    if DEBUG: print "\n\tNAME MISMATCH", le_name, n
            if DEBUG: print "The status for the ligand %s is %d" % ( n, found)

            if found < 1:
                to_be_reclustered.append(n)

                if DEBUG:
                    print n, "needs to be reclustered"
                    print LigBook[n]['path']
            else:
                # check the RMS consistency (LE ONLY FOR NOW)
                if not LigBook[n]["vs"] == "":
                    source = "vs"
                else:
                    source = "le"
                pose = LigBook[n][source]
                f = open(pose, 'r')
                lines = f.readlines()
                f.close()
                for l in lines:
                    if "USER  AD> binding " in l:
                        #USER  AD> binding 2.00 112 runs  59 clusters
                        rms_found = float(l.split()[3]) # CHECK THIS!!! it's changed
                        LigBook[n]['rmstol'] = rms_found
                        if DEBUG: print "\tfound rms and assigned", rms_found,
                        break
                if not CurrentSessionRMStol and rms_found:
                    CurrentSessionRMStol = rms_found
                    if DEBUG: print "openLigandDir> ################## INITIALIZED THE RMS TOLERANCE:", rms_found,
    
                if not CurrentSessionRMStol == rms_found:
                    if DEBUG: print "found a clustering_RMS inconsistancy", le
                    LigBook[n]["recluster"] = True
                    to_be_reclustered.append(n)
                else:
                    LigBook[n]["recluster"] = False
                    #LigBook[name]["rmstol"] = CurrentSessionRMStol
                    if DEBUG: print "rms set to :", LigBook[n]["rmstol"]
                            
    else:
        #LigBook[name]["recluster"] = ForceReclustering.get()
        to_be_reclustered = LigBook.keys()

    if to_be_reclustered:
        if DEBUG: print "\t%d ligands needs to be reclustered" % len(to_be_reclustered)
    else:
        if DEBUG: print "\tgood, no ligands needs to be reclustered"
        
    UpdateLigandInputInfo() # file, name
    SetGPFdata() # name, file, name
    UpdateResults() # name
    return True



def UpdateVSresults(lig = None, dir = None):
    if lig and dir:
        VS_results_list = glob(os.path.join(dir, "*_vs.pdbqt"))
        LE_results_list = glob(os.path.join(dir, "*_vs_le.pdbqt"))
        LC_results_list = glob(os.path.join(dir, "*_vs_lc.pdbqt"))
    if len(VS_results_list) == 0 and len (LE_results_list) == 0:
        if DEBUG:
            print "UpdateVSresults> warning! missing VS/LE/LC result\n"
            print "\tlig:", lig
            print "\tdir:", dir
            print "\tvs results: ", VS_results_list
            print "\tle results: ", LE_results_list
            print "\tlc results: ", LC_results_list
        return False
    found = 0

    if VS_results_list:
        for vs in VS_results_list:
            vs_path = os.path.dirname(vs)    # TODO do we want to match the path too? not for now
            vs_name = os.path.basename(vs)[:-9]  # ./faah8621_ZINC02026051_xJ1_xtal/ZINC02026051_vs.pdbqt -> ZINC02026051 TODO 
            # TODO change with the more robust
            """
                                    name = os.path.basename(i)
                        if "_vs_lc" in i:
                            name = name.replace("_vs_lc", "")
                        elif "_vs_le" in i:
                            name = name.replace("_vs_le", "")
                        elif "_vs." in i:
                            name = name.replace("_vs", "")
                        name = os.path.splitext(name)[0]"""

            if vs_name == lig:
                LigBook[lig]["vs"] = vs
                found += 2
                break
    else:
        for lc in LC_results_list:
            lc_path =  os.path.dirname(lc)    # TODO do we want to match the path too? not for now 
            lc_name =  os.path.basename(lc)[:-12]  # ./faah8621_ZINC02026051_xJ1_xtal/ZINC02026051_vs_lc.pdbqt -> ZINC02026051
            if lc_name == lig:
                LigBook[lig]["lc"] = lc
                found += 1
                break
        for le in LE_results_list:
            le_path = os.path.dirname(le)    # TODO do we want to match the path too? not for now
            le_name =  os.path.basename(le)[:-12]  # ./faah8621_ZINC02026051_xJ1_xtal/ZINC02026051_vs_lc.pdbqt -> ZINC02026051
            if le_name == lig:
                LigBook[lig]["le"] = le
                found += 1
                break
    if found == 0:
        if DEBUG:
            print "UpdateVSresults> warning! apparent filename mismatch in result files..."
            print "\tlig:", lig
            print "\tdir:", dir
        return False
    return True



def RemoveLigand(item_list = None, nuke = False):
    global FilteredLigands
    global GridInfo
    if not item_list and not nuke:
    	return
    if not len(LigBook) > 0:
    	return
    if nuke:
    	if not askokcancel('Delete all the ligands','Do you really want to\nremove all the ligands\nfrom the list?'):
    		return
    	LigandScrolledListBox.delete(0, END) 
    	LigBook.clear()
        if current_ligand:
            mv.deleteMol(pmv_name(current_ligand[1]), log = 0)
        #UpdateLigandCount()
        to_be_reclusterd = []
        FilteredLigands = []
        UpdateButtons()
        GridInfo = {}
        CurrentSessionRMStol = None
        UpdateResults()
        # emtpy the pies...
        UpdateLigandInputInfo()
        UpdateGridInfo()

    # TODO trigger the deletion of all the ligands in the viewer too

def vs_energy_profile(range_only = False):

    def float_range(b, e, s):
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

    energy_list = []
    best = 9999
    worst = -9999
    total = len(LigBook.keys())


    for l in LigBook.keys():
        e = get_ligand_info(l, data = 'energy')
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
    bar_count = len(float_range(min_cut, max_cut, step))+1
    if DEBUG:
        print "Min_cut", min_cut
        print "Max_cut", max_cut
        print "bar_count", bar_count
    pop = []
    for i in float_range(min_cut, max_cut, step):
        pop.append(0)
    #print len(pop)



    start = min_cut
    end = min_cut-step
    #print "start", start
    #print "end", end
    count = 0
    for i in float_range(min_cut, max_cut, step):
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

    # TODO add the check to see if the toplevel is present... blablabla
    try:
        EnergyPopulation.lift()
    except:
        EnergyPopulation = Toplevel(root)
        EnergyPopulation.title("Energy profile")
        EnergyPopulation.winfo_toplevel().resizable(NO,NO)

    w = 600 #50*len(bars)+3
    h = 400
    canvas = Canvas(EnergyPopulation, height = h, width = w, bg = 'gray90')
    canvas.grid()

    # colors
    # min_pixel
    # 

    
    xbord = 15 # extra tolerance
    ybord = 15

    # origin
    x0 = 30 + xbord
    y0 = h-30-ybord
    x_buffer = 3 # distance between bars

    x_max = w-50
    y_max = 50
    y_span = y0-y_max

    x_mid = x0+int((x_max-x0)/2)
    y_mid = y0-int((y0-y_max)/2)

    tick_size = int( (x_max-x0)/len(bars)   )
    bar_size = int(tick_size/2)

    y50 = int(y0+y_max)/2
    y25_l = int((y50+y0)/2)
    y25_u = int((y_max+y50)/2)

    start_tick = x0 + 5
    start_bar = start_tick + bar_size

    #canvas.create_line(x0, y0 , x_max, y0, width = 2) # x-axis
    canvas.create_line(x0, y0, x0, y_max, width = 2)  # y-axis 
    # TODO convert to a box and that's it?

    canvas.create_line(x0, y50, x_max, y50, dash = (1,1), fill = 'gray') # 50% line
    canvas.create_line(x0, y25_l, x_max, y25_l, dash = (1,1), fill = 'gray', ) # 25% lower
    canvas.create_line(x0, y25_u, x_max, y25_u, dash = (1,1), fill = 'gray') # 25% upper
    canvas.create_line(x0, y_max, x_max, y_max, width = 2)
    canvas.create_line(x_max, y0, x_max, y_max, width = 2)
    # title
    choice = PoseChoice.get()
    canvas.create_text( x_mid, y_max-32, font = 'helvetica 22 bold', fill = 'black', text = 'Energy profile')
    if choice == "Lowest energy in largest cluster":
        txt = str(total)+" ligands, "+choice+" ( "+str(CurrentSessionRMStol)+"A RMSD )"
    else:
        txt = str(total)+" ligands, "+choice
    canvas.create_text( x_mid, y_max-10, font = 'helvetica 13 bold', fill = 'black', text = txt)


    # labels
    canvas.create_text( x_mid, y0+32, font = 'helvetica 16 bold', fill = 'black', text = 'Kcal/mol')
    canvas.create_text( x0-20, y_mid, font = 'helvetica 18 bold', fill = 'black', text = '%')
    canvas.create_text( x_max+12, y50, font = 'helvetica 10 bold',  text = '50', fill = 'gray')
    canvas.create_text( x_max+12, y25_l, font = 'helvetica 10 bold',  text = '25', fill = 'gray')
    canvas.create_text( x_max+12, y25_u, font = 'helvetica 10 bold',  text = '75', fill = 'gray')
    canvas.create_text( x_max+12, y_max, font = 'helvetica 10 bold',  text = '100', fill = 'gray')


    #canvas.create_line(start_bar, y0 , start_bar, y_max, width = 2, fill = 'red')# test

    count = 1
    for b in bars:
        bar_h = int(y_span*(b[1]/100))
        """
        if bar_h < 1:
            bar_h = 2
        """
        if DEBUG: print "Energy[%d]: percent %2.2f\t=> %d pixels" % (b[0], b[1], bar_h)
        # ticks
        canvas.create_line( start_tick+((count-1)*tick_size), y0-7, start_tick+((count-1)*tick_size), y0+7) # tickmark
        # ticks labels
        canvas.create_text( start_tick+((count-1)*tick_size), y0+15, font = 'helvetica 10 bold', fill = 'black', text = b[2]) # energy value

        #canvas.create_rectangle( (start_bar-bar_size+2)+((count-1)*tick_size), y0-2, (start_bar+bar_size-2)+((count-1)*tick_size), y0-2-bar_h,
        #        fill = 'steel blue', outline = 'light cyan' )

        # bars
        canvas.create_rectangle( (start_bar-bar_size+4)+((count-1)*tick_size), y0, (start_bar+bar_size-3)+((count-1)*tick_size), y0-bar_h-1,
                fill = 'SteelBlue1', outline = 'steel blue', width = 2 )
                #fill = 'SteelBlue1', outline = 'steel blue' )

        # bar percentage # TODO add as a tooltip?
        # canvas.create_text(start_bar+((count-1)*tick_size), y0-6-bar_h, font = 'helvetica 10', fill = 'SteelBlue1', text = ("%2.2f" % b[1]))

        ### bar label values
        # shadow
        canvas.create_text(start_bar+((count-1)*tick_size), y0-10, font = 'helvetica 10 bold', fill = 'white', text = b[0])
        # text
        #canvas.create_text(start_bar+1+((count-1)*tick_size), y0-11, font = 'helvetica 10 bold', fill = 'gray85', text = b[0])
        canvas.create_text(start_bar+1+((count-1)*tick_size), y0-11, font = 'helvetica 10 bold', fill = 'red', text = b[0])
        count += 1

    canvas.create_line(x0, y0 , x_max, y0, width = 2) # x-axis
    Button(EnergyPopulation, text = "Close", command = lambda: EnergyPopulation.destroy(), height = 2).grid(row = 9, column = 0, sticky = W+E)


def UpdateLigandInputInfo():
    """
    Update the ligand info panel in the InputData tab
    """
    total = len(LigBook)
    txt  = "Ligands:\t\t %d\n" % total
    dlg_tot = 0
    recluster_count = 0
    if total >0 :
        label = "Ligands [ %d ]" % total
        LigandListLabel.set( label )


        for l in LigBook.keys():
            # dlg count
            lig = LigBook[l]
            dlg_tot += len(lig['dlg'])

            # recluster count
            if lig['recluster']:
                if DEBUG: print "UpdateLigandInputInfo> reclustering status", LigBook[l]['recluster']
                recluster_count += 1
    else:
        LigandListLabel.set("Import ligands...")

    txt += "Total DLG count:\t %d\n" % dlg_tot
    if not CurrentSessionRMStol == None:
        txt += "RMS tolerance:\t %2.2f Angstrom\n" % CurrentSessionRMStol
    else:
        txt += "RMS tolerance:\t (none)\n"
    txt += "\nTo be reclustered:\t %d\n" % recluster_count

    LigandInputInfo.config(state = NORMAL)
    LigandInputInfo.delete(1.0,END)
    LigandInputInfo.insert(END, txt)
    LigandInputInfo.config(state = DISABLED)
    UpdateEnergyProfile()
    # ToBeReclustered = 

def UpdateEnergyProfile():
    #global FilterStatText
    total = len(LigBook)
    best,worst = vs_energy_profile(range_only = True)
    txt = "Ligands:\t\t %d\n" % total
    txt +="    Best energy:\t%2.2f\n"% best
    txt +="    Worst energy:\t%2.2f"% worst
    FilterStatText.config(state = NORMAL)
    FilterStatText.delete(1.0, END)
    FilterStatText.insert(END, txt)
    EnergyProfileButton = Button(FilterStatText,text = "Energy profile", command = vs_energy_profile)
    FilterStatText.window_create(END, window =EnergyProfileButton)
    
    FilterStatText.config(state = DISABLED)

    #FilterStatText = Text(Tab2, height=9, width=40, relief = FLAT)
    

def ValidateClusTolerance(event = None):
	try:
		rms = ClusTolerance.get()
		if DEBUG: print "ValidateClusTolerance> got this value", rms
		if rms < 0:
			showwarning("RMS tolerance", "The RMS tolerance must be > 0.\n\n[Reset to the default : 2.0]")
			ClusTolerance.set(DefaultRMStol)
			return False
		if rms > 3:
			showwarning("RMS tolerance", "Unusually big value.\n\nThe common RMS tolerance value is between 0.5 and 2.5 Angstrom.\n\n Use it at your own risk...")
	except:
		showerror("RMS value", "The RMS tolerance value is not correct.\n\nIt must be a number between 0.5 and 2.5 Angstrom.\n\n [Reset to the default : 2.0]")
		ClusTolerance.set(DefaultRMStol)
		return False



def ImportLigandOptions():
    global LigOptionsWin
    try:
        LigOptionsWin.deiconify()
        LigOptionsWin.lift()
    except:
        LigOptionsWin = Toplevel(master = root, takefocus = True)
        LigOptionsWin.title("Clustering tool")
        LigOptionsWin.winfo_toplevel().resizable(NO,NO)
    
    def close():
        ValidateClusTolerance()
        # finally...
        LigOptionsWin.destroy()

    Frame1 = Pmw.Group(LigOptionsWin, tag_text = "Re-clustering : " )
    #LigandGroup = Pmw.Group(Tab1, tag_textvariable = LigandListLabel)

    Radiobutton(Frame1.interior(), text = "if necessary", var = ForceReclustering, value = False).grid(row = 0, column = 0, padx = 5, pady = 5, sticky = W, columnspan = 2)
    Radiobutton(Frame1.interior(), text = "always", var = ForceReclustering, value = True).grid(row = 1, column = 0, padx = 5, pady = 5, sticky = W, columnspan = 2)
    Label(Frame1.interior(), text = "RMS tolerance").grid(row = 2, column = 0, pady = 5, padx = 5, sticky = W+E)
    ClusterEntry = Entry(Frame1.interior(), textvariable = ClusTolerance, width = 10)
    ClusterEntry.grid(row = 2, column = 1, pady = 5, padx = 5, sticky = W)
    ClusterEntry.bind("<Button-1>", ValidateClusTolerance)
    ClusterEntry.bind("<Return>", ValidateClusTolerance)
    ClusterEntry.bind("<Tab>", ValidateClusTolerance)
    ClusterEntry.bind("<FocusIn>", ValidateClusTolerance)
    ClusterEntry.bind("<FocusOut>", ValidateClusTolerance)
    #ClusterEntry.bind("<Leave>", ValidateClusTolerance) # DANGEROUS!!!
    Button(Frame1.interior(), text = "Re-cluster now...", command = Recluster).grid(row = 4, column = 0, columnspan = 2, sticky = W+E, padx = 5, pady = 5)
    

    #Checkbutton(Frame1.interior(), text = "always", var = ForceReclustering, onvalue = True, offvalue = False).grid(row = 0, column = 0, padx = 5, pady = 5)
    # TODO add a more less button for the extra optiosn

    def SetOpts(value):
        if value == 1:
            #print "more"
            OptButton.configure(text = "Less options <<", command = lambda : SetOpts(0))
            Frame2.grid(row = 5, column = 0, sticky = W+E, padx = 10, pady = 10)
            Frame3.grid(row = 6, column = 0, sticky = W+E, padx = 10, pady = 10)
        if value == 0:
            #print "less"
            OptButton.configure(text = "More options >>", command = lambda : SetOpts(1))
            Frame2.grid_forget()
            Frame3.grid_forget()

    Frame1.grid(row = 3, column = 0, sticky = W+E, padx = 10, pady = 10)

    OptButton = Button(LigOptionsWin, text = "More options >>", command = lambda : SetOpts(1))
    OptButton.grid(row = 4, column = 0, sticky = E, padx = 5, pady = 5)
    
    Frame2 = Pmw.Group(LigOptionsWin, tag_text = "Options" )

    Label(Frame2.interior(), text = "Create pose(s) :").grid(row = 1, column = 0, columnspan = 1, sticky = W+E)
    #Radiobutton(Frame2.interior(), text = "LE and LC", var = ClusterGenPose, value = 2).grid(row = 2, column = 0)
    #Radiobutton(Frame2.interior(), text = "LE only", var = ClusterGenPose).grid(row = 2, column = 1)
    #Radiobutton(Frame2.interior(), text = "LC only", var = ClusterGenPose).grid(row = 2, column = 2)
    #clustering_option = StringVar(value = "LE and LC")
    OptionMenu(Frame2.interior(), ClusterGenPose, "LE and LC", "LE only", "LC only").grid(row = 1, column = 1, sticky = W)

    Checkbutton(Frame2.interior(), text = "Save interactions in PDBQT+", variable = ClusterSaveInter).grid(row = 6, column = 0, sticky = W, columnspan = 2)
    Checkbutton(Frame2.interior(), text = "Detect H-bonds", variable = ClusterHB).grid(row = 3, column = 0, sticky = W, columnspan = 2)
    Checkbutton(Frame2.interior(), text = "Detect close contacts", variable = ClusterVDW).grid(row = 4, column = 0, sticky = W, columnspan = 2)
    Checkbutton(Frame2.interior(), text = "Detect P-P interactions", variable = ClusterPP).grid(row = 5, column = 0, sticky = W, columnspan = 2)

    #Frame2.grid(row = 5, column = 0, sticky = W+E, padx = 10, pady = 10)



    Frame3 = Pmw.Group(LigOptionsWin, tag_text = "Warnings & errors" )
    Checkbutton(Frame3.interior(), text = "Ignore receptor\nname mismatch", indicatoron = False, variable = IgnoreRecMismatch).grid(row = 1, column = 0, sticky = W+E, ipadx = 10, ipady = 7, padx = 5, pady = 5)
    Checkbutton(Frame3.interior(), text = "Import incomplete DLG", indicatoron = False, variable = IgnoreIncomplete).grid(row = 2, column = 0, sticky = W+E, ipadx = 10, ipady = 7, padx = 5, pady = 5)
    


    Button(LigOptionsWin, text = "Close", command = lambda : close(), height = 2).grid(row = 9 , column = 0, columnspan = 2, padx = 5, pady = 5, sticky = E+W)




def checkPDBQT_receptor(filename): 
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


def checkGPF(filename):
    if DEBUG: print "checkGPF> got filename", filename
    f = open(filename, 'r')
    lines = f.readlines()
    f.close()
    npts, spacing, center = False, False, False
    for l in lines:
        if "npts" in l: npts = True
        if "spacing" in l: spacing = True
        if "gridcenter" in l: center = True
        if center and npts and spacing:
            return True
    print "checkGPF> this seems to be an incomplete/invalid GPF"
    return False

def ExtractResidues():
    global FullResList, BoxResList, NonBoxResList

    FullResList = []
    BoxResList = []

    rec = ReceptorFilename.get()
    box = RecBoxFilename.get()
    if DEBUG:
        print "ExtractResidues>"
        print "\trec:", rec
        print "\tbox:", box

    try:
        lines = get_lines(rec)
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
            lines = get_lines(box)
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
    return True


def SelectReceptor(filename = None):
    global ReceptorMolecule
    global current_full_rec_visible
    global current_full_rec_mode 
    global current_full_rec_color
    global current_full_rec_flat_color 
    global current_box_visible
    global current_box_mode 
    global current_box_color
    global current_box_c_color
    global current_ligand_interactions
    global current_labelset
    global current_labelcolor 
    global IN_residues
    global OUT_residues

    if not filename:
        filename = askopenfilename(parent = root, title = "Select the receptor structure file...", filetypes = [("Receptor PDBQT", "*.pdbqt"), ("Any file", "*")])
    if not filename:
        return False
    else:
        old = ReceptorFilename.get()
        if checkPDBQT_receptor(filename):
            # reset all the ligand style stuff..
            current_full_rec_visible = None
            current_full_rec_mode = None
            current_full_rec_color= None
            current_full_rec_flat_color = None
            current_box_visible= None
            current_box_mode = None
            current_box_color = None
            current_box_c_color= None
            current_ligand_interactions= None
            current_labelset = None
            current_labelcolor = None
            IN_residues = None
            OUT_residues = None

            SetReceptorFilename(filename)
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

            if GridInfo:
                rec_in_the_box = pdb_in_the_box()
                if rec_in_the_box and checkPDBQT_receptor(rec_in_the_box):
                    RecBoxFilename.set(rec_in_the_box) # the file that's actually used for calculating the interactions
                else:
                    if DEBUG: print "SetReceptor> it seems something went wrong with the res_in_the_box..."
                    rec_in_the_box = False
                    RecBoxFilename.set("")
                    return False              
            else:
                rec_in_the_box = False
                RecBoxFilename.set("")

            # remove old receptor from the session
            if not old == "":
                old = os.path.basename(old)
                old_name = os.path.splitext(old)[0]
                if DEBUG: print "SelectReceptor> deleting previous receptor", old_name
                mv.deleteMol(old_name, log = 0)

            # load the new one # TODO to be reduced to loading function, then RecStyle
            ReceptorMolecule = mv.readMolecule(ReceptorFilename.get(), log = 0)[0]
            name = os.path.basename(ReceptorFilename.get())
            name = os.path.splitext(name)[0]
            cam = vi.cameras[1]
            cam.SelectCamera()
            cam.tk.call(cam._w, 'makecurrent') 
            cam.focus_set()
            vi.SetCurrentObject(ReceptorMolecule.geomContainer.masterGeom)

            #vi.SelectCamera()
            #mv.colorByAtomType(name, ['lines'], log=0)
            #mv.colorAtomsUsingDG(ReceptorMolecule, ['lines'], log=0)
            #mv.displayExtrudedSS(ReceptorMolecule, negate=False, only=False, log=0)
            #mv.displayCPK(ReceptorMolecule, log=0, cpkRad=0.0, scaleFactor=1.0, only=False, negate=False, quality=0)
            #mv.colorAtomsUsingDG(ReceptorMolecule, ['lines'], log=0)
            resetview()
            vi.Redraw()
            # todo apply all the styles to the receptor
            vi.SetCurrentObject(vi.rootObject)
            # generate the list of residues
            ExtractResidues()
            RecStyle()
            resetview('receptor')
            return True

def SetReceptorFilename(filename):
    ReceptorFilename.set(filename)
    max_len = 60
    if len(filename) > max_len:
        label = "..."+filename[-max_len:]
    else:
        label = filename
    ReceptorFilenameLabel.set(label)
    return    
	


def gpf2pdb(filename = None, center = False):
    atype = " C"
    out_name = TEMPDIR+os.path.sep+"grid_box.pdb"
    pdb_out = []
    corners = []
    temp = []

    if filename:
        if DEBUG: print "gpf2pdb> FILENAME mode"
        try:
            f = open(filename, 'r')
            lines = f.readlines()
            f.close()
            pdb_out.append("REMARK   This is the box from the file :  "+filename)
        except:
           if DEBUG: print "gpf2pdb> error in reading gpf!", filename
           GPFpdbFilename.set(None)
           return False
        for l in lines:
            if len(l) > 3:
                tmp=l.split()
                if tmp[0] == "gridcenter":
                    center_x = float(tmp[1])
                    center_y = float(tmp[2])
                    center_z = float(tmp[3])
                if tmp[0] == "npts":
                    pts_x = float(tmp[1])
                    pts_y = float(tmp[2])
                    pts_z = float(tmp[3])
                if tmp[0] == "spacing":
                    res = float(tmp[1])


        step_x = pts_x/2 * res
        step_y = pts_y/2 * res
        step_z = pts_z/2 * res
    
        # 1 
        corners.append([ center_x-step_x, center_y-step_y, center_z-step_z] )
        # 2
        corners.append([ center_x+step_x, center_y-step_y, center_z-step_z] )
        # 3
        corners.append([ center_x+step_x, center_y+step_y, center_z-step_z] )
        # 4
        corners.append([ center_x-step_x, center_y+step_y, center_z-step_z] )
        # 5 
        corners.append([ center_x-step_x, center_y-step_y, center_z+step_z] )
        # 6
        corners.append([ center_x+step_x, center_y-step_y, center_z+step_z] )
        # 7
        corners.append([ center_x+step_x, center_y+step_y, center_z+step_z] )
        # 8
        corners.append([ center_x-step_x, center_y+step_y, center_z+step_z] )
        #print corners
        
    else:
        if len(GridInfo) == 0:
            if DEBUG: print "gpf2pdb> No GRID_DATA available"
            return

        if DEBUG: print "gpf2pdb> GRID_DATA mode"
        #"""spacing, [pts], [center],[max],[min]"""
        min = GridInfo['min']
        max = GridInfo['max']
        pdb_out.append("REMARK   This is the box from the following Min/Max values :"+str(min)+"|"+str(max))
        corners.append( [ min[0], min[1], min[2] ] )
        corners.append( [ max[0], min[1], min[2] ] )
        corners.append( [ max[0], max[1], min[2] ] )
        corners.append( [ min[0], max[1], min[2] ] )
        corners.append( [ min[0], min[1], max[2] ] )
        corners.append( [ max[0], min[1], max[2] ] )
        corners.append( [ max[0], max[1], max[2] ] )
        corners.append( [ min[0], max[1], max[2] ] )
        center_x = GridInfo['center'][0]
        center_y = GridInfo['center'][1]
        center_z = GridInfo['center'][2]


    count = 1
    res = "BOX"
    chain = "X"
    for idx in range(len(corners)):
    	x = corners[idx][0]
    	y = corners[idx][1]
    	z = corners[idx][2]
    	line = "ATOM  %5d %4s %3s %1s%4d    %8.3f%8.3f%8.3f  1.00 10.00          %1s" % (count, atype, res, chain, idx+1, x, y, z, atype)
    	pdb_out.append(line)
    	count += 1
    
    # center
    if center:
        pdb_out.append( ("ATOM  %5d %4s %3s %1s%4d    %8.3f%8.3f%8.3f  1.00 10.00          %1s") % (count, atype, res, chain, idx+2, center_x, center_y, center_z, atype) )
    
    pdb_out.append("CONECT    1    2")
    pdb_out.append("CONECT    1    4")
    pdb_out.append("CONECT    1    5")
    pdb_out.append("CONECT    2    3")
    pdb_out.append("CONECT    2    6")
    pdb_out.append("CONECT    3    4")
    pdb_out.append("CONECT    3    7")
    pdb_out.append("CONECT    4    8")
    pdb_out.append("CONECT    5    6")
    pdb_out.append("CONECT    5    8")
    pdb_out.append("CONECT    6    7")
    pdb_out.append("CONECT    7    8")
    
    
    try:
        OUT = open(out_name, 'w')
        for line in pdb_out:
        	print >> OUT, line
        OUT.close()
    except:
        if DEBUG: print "gpf2pdb> error in writing the output file", out_name
        GPFpdbFilename.set(None)
        return False
    
    if DEBUG: print "gpf2pdb> saved", out_name
    GPFpdbFilename.set(out_name)

    return out_name

def LoadGPFbox(file):
    # TODO modify when find out how to load a molecule with a give name
    # TODO add a delete function for the previous
    global GPFboxMolName

    if not GPFboxMolName == None:
        mv.deleteMol(GPFboxMolName, log = 0)
        
    try:
        GPFboxMolName = mv.readMolecule(file, log = 0)[0]
        #mv.displayLines(GPFboxMolName, negate = True) # Default PMV mode
        line_style = GPFbox.geomContainer.geoms['bonded']
        # TODO it doesnt work...
        line_style.Set(stippleLines=1, inheritStippleLines = 0, immediateRendering = 1)
        vi.Redraw()
        #mv.displayLines(GPFboxMolName, negate=False, displayBO=False, only=False, log=0, lineWidth=1.0)

        if DEBUG: print "LoadGPFbox> loaded the GPF box file"
        print GPFboxMolName
    except:
        GPFboxMolName = None
        if DEBUG: print "LoadGPFbox> error loading the GPF pdb box"

def SetGPFFilename(filename = None):
    # TODO see if necessary...
    # As an option to speed up the interaction calculation
    if not filename:
        filename = askopenfilename(parent = root, title = "Select the GPF...", filetypes = [("Grid Parameter File", "*.gpf", "*.GPF"), ("Any file", "*")])
    if not filename:
        ReceptorGPF.set("")
        ReceptorGPFLabel.set("")
        return
    else:
        if checkGPF(filename):
            if DEBUG: print "SetGPFFilename> found GPF"
            ReceptorGPF.set(filename)

            if not GPFpdbFilename.get():
                gpf_box = gpf2pdb(filename)
                if gpf_box:
                    LoadGPFbox(gpf_box)

            if len(filename) > 32:
                label = "..."+filename[-32:]
            else:
                label = filename
            ReceptorGPFLabel.set(label)
            rec = ReceptorFilename.get()
            if rec:
                if DEBUG: print "SetGPFFilename> triggering residues inside the box"
                SelectReceptor(rec)
                #ExtractResidues()
        return    

def SetGPFdata():
    if not GridInfo:
        if DEBUG: print "SetGPFdata> nothing do do for me... returning"
        return

    gpf_box = gpf2pdb()
    if gpf_box:
        LoadGPFbox(gpf_box)
        rec = ReceptorFilename.get()
        if rec:
           if DEBUG: print "SetGPFFilename> triggering residues inside the box"
           ExtractResidues()
           SelectReceptor(rec) #disabled check!
           #ExtractResidues()
    



def Recluster(force = False):
    global CurrentSessionRMStol 
        
    # TODO ADD Timing function as:
    # http://www.tutorialspoint.com/python/time_clock.htm
    #
    # http://www.ibm.com/developerworks/linux/library/l-cpnum.html#N100C5
    # AWESOME LINK, BY THE WAY!
    if DEBUG: print "Recluster> called with the param:", force
    if not force:
        force = ForceReclustering.get()
        if DEBUG: print "Recluster> ForceReclustering.get() =", ForceReclustering.get()
    if force:
        if DEBUG: print "Recluster> FORCED ANYWAY by ForceReclustering"

    """ catch closing windows
        top = Toplevel(...)
        # make sure widget instances are deleted
        top.protocol("WM_DELETE_WINDOW", top.destroy)
    """

    if not ReceptorFilename.get():
        if DEBUG: print "Recluster> missing receptor, exiting..."
        showinfo(master = LigOptionsWin, title = "Re-clustering", message = ("Re-clustering require the target structure.\n\nSpecify the PDBQT file in the \'Target structure' frame."))
        if not SelectReceptor():
            return False
    if ReceptorFilename.get():
        if not RecBoxFilename.get() == "": # or RecBoxFilename.get() == None:
            receptor_filename = RecBoxFilename.get()
            if DEBUG: print "Recluster> using the receptor subset from the gridbox", receptor_filename
        else:
            receptor_filename = ReceptorFilename.get()
            if DEBUG: print "Recluster> using the full receptor", receptor_filename
    if DEBUG: print "Recluster> using the following receptor", receptor_filename


    if force:
        if DEBUG: print "Recluster> using the Force... all the ligands will be reclustered"
        c = len(LigBook)
        recluster_list = LigBook.keys()
    else:
        if DEBUG: print "Recluster> finding ligands without a PDBQT+/with wrong RMSD"
        recluster_list = []
        for l in LigBook.keys():
            ok = True
            try:
                if DEBUG: print l, LigBook[l]['rmstol'], LigBook[l]['recluster']
                if LigBook[l]['recluster']:
                    if DEBUG: print "ligand requested to be reclustered"
                    ok = False
                if not LigBook[l]['rmstol'] == ClusTolerance.get():
                    ok = False
                    if DEBUG: print "rmstol inconsistancy",l, ClusTolerance.get(), LigBook[l]['rmstol']
                if not ok: recluster_list.append(l)
            except:
                print "error"
                for i in LigBook[l]:
                    print i
        c = len(recluster_list)
        #print c
    if c == 0:
        if DEBUG: print "Recluster> no ligands seems to require my attention"
        showinfo(master = LigOptionsWin, title = "Re-clustering", message = ("No ligands require re-clustering.\n\nUse the 'always' option to force the process"))
        return
    if askyesno(master = LigOptionsWin, title = "Re-clustering", message = "%d are going to be reclustered with RMSD tolerance of %1.2f Angstrom.\n\n[ this may take a while ]\n\nProceed?" % ( c, ClusTolerance.get() ) ):
        
        t0 = time.time()

        HANDBRAKE = BooleanVar(value = False)
     
        if DEBUG: print "Recluster> GOING!"
        # close the other window
        LigOptionsWin.destroy()

        ProgWin = Toplevel()
        ProgWin.title("Results extraction")
        ProgWin.config(width = 150)
        ProgWin.winfo_toplevel().resizable(NO,NO)
        Label(ProgWin, text = ( "Re-clustering:") ).grid(row = 2, column = 0, sticky = W, padx = 5, pady = 5)
        Label(ProgWin, text = ( " - cluster tolerance : "+str(ClusTolerance.get())) ).grid(row = 3, column = 0, sticky = W, padx = 5, pady = 5)
        if ClusterSaveInter.get():
            Label(ProgWin, text = " - interactions : saved (PDBQT+)").grid(row = 4, column = 0, sticky = W, padx = 5, pady = 5)
        else:
            Label(ProgWin, text = " - interactions : not saved").grid(row = 4, column = 0, sticky = W, padx = 5, pady = 5)
            
        recluster_status = Label(ProgWin, text = ( "Processing...") )
        recluster_status.grid(row = 5, column = 0, columnspan = 1, sticky = W+E, padx = 5, pady = 5)

        def stop():
            if DEBUG: print "Recluster> exiting!"
            HANDBRAKE.set(True)
            #print "stop> this is HANDBRAKE", HANDBRAKE

        def close():
            ProgWin.destroy()

        tic = ""

        framebar = Frame(ProgWin)
        framebar.config(bd = 1, relief = SUNKEN)
        Label(framebar, text = (" " * 50), anchor = W, justify = LEFT).grid(row = 1, column = 0)
        Bar = Label(ProgWin, text = tic, bg = 'blue', fg = 'red', anchor = W)
        Bar.grid(row = 6, column = 0, sticky = W, padx = 15, pady = 5) #, sticky = W)
        framebar.grid(row = 6, column = 0, sticky = W+E, padx = 15, pady = 5)
        percent = Label(ProgWin, text = "0 %")
        percent.grid(row = 7, column = 0, sticky = E+W)

        count = 0
        tot = len(recluster_list)
        #print "========= TOTAL", tot

        control = Button(ProgWin, text = "Stop", command = stop, width = 26)
        control.grid(row = 9, column = 0, sticky = E+W, padx = 15, pady = 15)

        final = 50


        # Initialize the DockingProcessor object 
        # maybe move?
        from MolKit import Read
        from AutoDockTools.Docking import Docking, DockingResultProcessor
        from mglutil.math.rmsd import RMSDCalculator
        from AutoDockTools.InteractionDetector import InteractionDetector

        # Values used for the PDBQT+
        write_both = False
        best_only = False
        largestCl_only = False
        max_cl_to_write = 1000

        if ClusterGenPose.get() == "LE and LC":
            write_both = True
        if ClusterGenPose.get() == "LE only":
            best_only = True
            write_both = False
        if ClusterGenPose.get() == "LC only":
            largestCl_only = True
            write_both = False
        lc_stem = ""

        if DEBUG:
            print "Recluster> generating poses:\n"
            print "\t write_both:", write_both
            print "\t best_only:", best_only
            print "\t largestCl_only:", largestCl_only


        include_interactions = ClusterSaveInter.get()
        build_hbonds = ClusterHB.get()
        detect_close_contacts = ClusterVDW.get()
        detect_pi = ClusterPP.get()
        verbose = True
        verbose = False
        if DEBUG: print "\tCHECK>", receptor_filename

        for l in recluster_list:
            DockingProcessor = DockingResultProcessor(rms_tolerance=ClusTolerance.get(),
                                                    rms_reference=None,
                                                    receptor_filename=receptor_filename,
                                                    write_both=write_both,
                                                    best_only=best_only,
                                                    largestCl_only=largestCl_only,
                                                    lc_stem=lc_stem, 
                                                    #max_cl_to_write=max_cl_to_write, 
                                                    include_interactions=include_interactions, 
                                                    detect_pi=detect_pi, 
                                                    build_hbonds=build_hbonds, 
                                                    detect_close_contacts=detect_close_contacts)
            if HANDBRAKE.get():
                showwarning(master = ProgWin, title = "Re-clustering terminated", message ="User stopped the re-clustering process")
                break

            #if True:
            try:
                directory = LigBook[l]['path']
                if DEBUG:
                    print "Recluster> CLUSTERING"
                    print "\tligand  :", l
                    print "\tshort   :", directory[-20:]
                    print "\tdir    :", directory
                    print "\treceptor:", receptor_filename
                DockingProcessor.process(directory, verbose=verbose)

                # update the percentage
                count += 1
                pc = int ( (float(count)/float(tot))*100 )
                tic = " " * (pc/2)
                Bar.config(text = tic)
                x = str(pc)+" %"
                recluster_status.config(text = "Processing... [ "+str(count+0)+" / "+str(tot)+" ]" )
                recluster_status.update()
                Bar.update()
                ProgWin.update()
                percent.config(text = x)
                percent.update()

                
                # test the output:
                if DEBUG:
                    print "\n\n######## sanity check #########"
                    print "LIGAND:   ", l
                    f = glob(os.path.join(directory, "*_vs*.pdbqt"))
                    for i in f:
                        name = os.path.basename(i)
                        if "_vs_lc" in i:
                            name = name.replace("_vs_lc", "")
                        elif "_vs_le" in i:
                            name = name.replace("_vs_le", "")
                        elif "_vs." in i:
                            name = name.replace("_vs", "")
                        name = os.path.splitext(name)[0]

                        print "FILE:     ", name
                        if not name == l:
                            print "ERROR!!!!"
                            print "PATH: ", LigBook[name]['path']
                            for d in LigBook[name]['dlg']:
                                print "DLG found:", d
                            return
                    print "\n\n######## sanity check #########"

                if UpdateVSresults(lig = l, dir = directory):
                    idx = to_be_reclustered.index(l)
                    del to_be_reclustered[idx]
                    LigBook[l]['recluster'] = False

            except:
                if DEBUG:
                    print "#################################################################### PROBLEMS IN RECLUSTERIN!!!! ####"
                    print "problematic ligand", l

        # TODO add a garbage collector here?
        if DEBUG:
            print "Recluster>\n\n\n#######################################"
            print " Ligands without a cluster solution:", len(to_be_reclustered)
            print "#######################################\n\n\n\n\n"

        if not HANDBRAKE.get():
            control.config(text = "Close", command = close)
            #print len(tic)
            recluster_status.config(text = "[ DONE ]")
            recluster_status.update()
            if DEBUG: print "Recluster>", time.time() - t0, " seconds wall time"
            # TODO add here the update function?
            UpdateLigandInputInfo()

            return True
        else:
            CurrentSessionRMStol = ClusTolerance.get()
            UpdateLigandInputInfo()
            ProgWin.destroy()
            return False
    else:
        UpdateLigandInputInfo()
        return False





###########################################################################################################################
###########################################################################################################################
###########################################################################################################################
###########################################################################################################################
###########################################################################################################################









################################
################################
######## TAB 1 
########

# Ligand frame ###################################################
"""
Tab3.grid_rowconfigure(1, weight = 1)
Tab3.grid_columnconfigure(0, weight = 1)

LigandListGroup.grid(row = 1, column = 0, sticky = E+W+N+S)

LigandListGroup.grid_columnconfigure(3, weight = 1)
LigandListGroup.grid_rowconfigure(0, weight = 1)
"""

Tab1.grid_rowconfigure(0, weight = 1)
Tab1.grid_columnconfigure(0, weight = 1)



LigandGroup = Pmw.Group(Tab1, tag_textvariable = LigandListLabel)
#LigandGroup.interior().grid_rowconfigure(0, weight = 1)
LigandGroup.interior().grid_rowconfigure(1, weight = 1)
#LigandGroup.interior().grid_rowconfigure(2, weight = 1)
LigandGroup.interior().grid_columnconfigure(0, weight = 1)
LigandGroup.interior().grid_columnconfigure(1, weight = 1)
#LigandGroup.interior().grid_columnconfigure(2, weight = 1)
#LigandGroup.interior().grid_columnconfigure(3, weight = 1)
Button(LigandGroup.interior(), text='Scan directories...', command = lambda : openLigandDir(recursive = True) ).grid(row = 0, column = 0, sticky = W+E+N)
Button(LigandGroup.interior(), text='Add single directory...', command = openLigandDir).grid(row = 0, column = 1, columnspan = 2, sticky = W+E+N)
Button(LigandGroup.interior(), text='Remove selected', command= RemoveLigand ).grid(row = 2, column = 0, sticky = W+E+S)
Button(LigandGroup.interior(), text='Remove all', command= lambda: RemoveLigand(nuke = True)).grid(row = 2, column = 1, columnspan = 2, sticky = W+E+S)
#Button(group1.interior(), text='Import reference ligand...', command=opendir).grid(row = 11, column = 0, columnspan = 1, sticky = W)

#Results_infotext = Text(Infobar.interior(), height=9, width=40, relief = FLAT)


LigandScrolledListBox = Listbox(LigandGroup.interior(), selectmode=EXTENDED)
LigandScroll = Scrollbar(LigandGroup.interior(), command=LigandScrolledListBox.yview)
LigandScroll.grid(row = 1, column = 2, sticky = N+S)
LigandScrolledListBox.configure(yscrollcommand=LigandScroll.set)
LigandScrolledListBox.grid(row = 1, column = 0, columnspan = 2, sticky = N+S+W+E)
LigandScrolledListBox.config(fg = 'black', font = ("Helvetica", 10, "bold"))
LigandGroup.grid(row = 0, column = 0, sticky = N+W+E+S, rowspan = 5)

# ligand info statistics
ClusteringGroup = Pmw.Group(Tab1, tag_text = "Clustering info")
LigandInputInfo = Text(ClusteringGroup.interior(), height = 5, width = 40, relief = FLAT)
LigandInputInfo.grid(row = 1, column = 0, sticky = N)
LigandInputInfo.config(state = DISABLED)
Button(ClusteringGroup.interior(), text='Clustering tool', command= ImportLigandOptions ).grid(row = 3, column = 0, sticky = W+E+S, rowspan = 2)
ClusteringGroup.grid(row = 0, column = 2, sticky =N+W+E)

# Receptor frame #################################################
TargetGroup = Pmw.Group(Tab1, tag_text = 'Target structure')
TargetGroup.interior().grid_rowconfigure(0, weight = 1)
Button(TargetGroup.interior(), text='Open PDBQT file...', command=SelectReceptor).grid(row = 0, column = 0, sticky = W, pady = 3)
Label(TargetGroup.interior(), textvar = ReceptorFilenameLabel).grid(row = 1, column = 0, sticky = W+N, columnspan = 2)
#Button(group2.interior(), text='Open GPF...', command=SetGPFFilename).grid(row = 1, column = 0, sticky = E+W, pady = 3)
#Label(group2.interior(), textvar = ReceptorGPFLabel).grid(row = 1, column = 1, sticky = W)
TargetGroup.grid(row = 1, column = 2, columnspan = 1, sticky = N+W+E+S)

# target info statistics
TargetInfo = Pmw.Group(Tab1, tag_text = "Grid info")
TargetInputInfo = Text(TargetInfo.interior(), height = 7, width = 40, relief = FLAT)
TargetInputInfo.grid(row = 1, column = 0, sticky = N)
TargetInputInfo.config(state = DISABLED)
#Button(TargetInfo.interior(), text='Clustering tool', command= ImportLigandOptions ).grid(row = 1, column = 0, sticky = W+E+S, rowspan = 2)
TargetInfo.grid(row = 2, column = 2, sticky = N+W+E+S)
#Button(Tab1, text='Select a map directory...', command=opendir).grid(row = 10, column = 0, columnspan = 2, sticky = S)




################################
################################
######## TAB 2 
########

#############################################
####### Default filter values and validators

def DefaultFilterValues(field = None):
    if field == None or field == "energy":
        Emin.set(default_EnergyMinimum)
        Emax.set(default_EnergyMaximum)
    if field == None or field == "cluster":
        ClustCount.set(default_Cluster_mode)
        if default_Cluster_mode == "%":
            ClustMin.set(default_Cluster_percent_min)
            ClustMax.set(default_Cluster_percent_max)
        else:
            ClustMin.set(default_Cluster_pop_min)
            ClustMax.set(default_Cluster_pop_max)
    
    if field == None or field == "efficiency":
        LEmin.set(default_LigEfficiency_min)
        LEmax.set(default_LigEfficiency_max)
    UpdateResults()
    return True

def Evalidate(event = None):
    try:
        min = Emin.get()
        max = Emax.get()
        return True
    except:
        showerror("Energy values", "The energy value are not correct.\n\nAccepted values are (usually) negative numbers, like \"-7.42\"\n\n [ Reset to the default ]")
        Emin.set(default_EnergyMinimum)
        Emax.set(default_EnergyMaximum)
        return False

def Cvalidate(event = None):
    mode = ClustCount.get()
    if mode == "%":
        d_min = default_Cluster_percent_min
        d_max = default_Cluster_percent_max
        error = "Percentage value are not correct.\n\nAccepted values are numbers between 1 and 100.\n\n [Reset to default]"
    
    if mode == "#":
        d_min = default_Cluster_pop_min
        d_max = default_Cluster_pop_max
        error = "The number of individuals in the cluster is not correct.\n\nAccepted values are numbeers between 1 and +oO.\n\n [Reset to default]"
    try:
        min = ClustMin.get()
        max = ClustMax.get()
        if mode == "%":
            if min < 0 or max > 100:
                raise
            return True
    except:
        showerror("Cluster size", error)
        ClustMin.set(d_min)
        ClustMax.set(d_max)
        return False

def LEvalidate(event = None):
    try:
        min = LEmin.get()
        max = LEmax.get()
        return True
    except:
        showerror("Ligand efficiency values", "The values are not correct.\n\nAccepted values are (usually) negative numbers, like \"-0.42\"\n\n [ Reset to the default ]")
        LEmin.set(default_LigEfficiency_min)
        LEmax.set(default_LigEfficiency_max)
        return False

##################################################














def test(event):
    print "__________________TESTING"
    print "CGET", event.widget.keys()
    print "CGET2", event.widget.destroy()

def ResidueList(event):
    # TODO add buttons to view polar residues, aromatic, bla blabla
    # ...and in the box (remove the tabs)
    # ...chains pulldown menus?
    
    def Select1(x = None):
        # TODO return the correct syntax?
        pos = FullScrolled.curselection()
        res = FullScrolled.get(pos)
        event.widget.delete(0,END)
        event.widget.insert(0, res)
        ResList.destroy()

    def Select2(x = None):
        # TODO return the correct syntax?
        pos = BoxScrolled.curselection()
        res = BoxScrolled.get(pos)
        event.widget.delete(0,END)
        event.widget.insert(0, res)
        ResList.destroy()



    if not len(FullResList):
        if DEBUG: print "ResidueList> nothing in the receptor"
        return False

    if DEBUG: print "ResidueList> called residueList"

    global ResList
    try:
        ResList.deiconify()
        ResList.lift()
    except:
        ResList = Toplevel(master = root, takefocus = True)
        ResList.title("Select a residue...")
        ResList.winfo_toplevel().resizable(NO,NO)
        r_nbook = Pmw.NoteBook(ResList)
        tab1 = r_nbook.add('All residues')

        # full residues
        FullScrolled = Listbox(tab1, selectmode = SINGLE)
        FullScrolled.grid(row = 1, column = 0, sticky = N+S+W+E)
        scroll1 = Scrollbar(tab1, command=FullScrolled.yview)
        scroll1.grid(row = 1, column = 1, sticky = N+S+E)
        FullScrolled.configure(yscrollcommand=scroll1.set)
        FullScrolled.bind('<Double-Button-1>', Select1)
        frame1 = Frame(tab1)
        Button(frame1, text = "Select", command = Select1).grid(row = 10, column = 0)
        Button(frame1, text = "Cancel", command = lambda: ResList.destroy()).grid(row = 10, column = 1)
        frame1.grid(row = 9, column = 0, columnspan = 2)

        r_nbook.pack()
        r_nbook.setnaturalsize() # Resize automatically the window
        
        for i in FullResList:
            i = i.replace("_", ":",1)
            i = i.replace("_", "")

            FullScrolled.insert('end', i)
    
    
        if len(BoxResList):
            tab2 = r_nbook.add('In the grid')
            BoxScrolled = Listbox(tab2, selectmode = SINGLE)
            BoxScrolled.grid(row = 1, column = 0, sticky = N+S+W+E)
            scroll2 = Scrollbar(tab2, command=BoxScrolled.yview)
            scroll2.grid(row = 1, column = 1, sticky = N+S+E)
            BoxScrolled.configure(yscrollcommand=scroll2.set)
            BoxScrolled.bind('<Double-Button-1>', Select2)
            frame2 = Frame(tab2)
            Button(frame2, text = "Select", command = Select2).grid(row = 10, column = 0)
            Button(frame2, text = "Cancel", command = lambda: ResList.destroy()).grid(row = 10, column = 1)
            frame2.grid(row = 9, column = 0, columnspan = 2)

            r_nbook.pack()
            r_nbook.setnaturalsize() # Resize automatically the window
            
            for i in BoxResList:
                i = i.replace("_", ":",1)
                i = i.replace("_", "")

                BoxScrolled.insert('end', i)
    return



filter_place = 0
filter_dictionary = {}

class NewFilter:
    """
    create a residue filter object
    """

    def __init__(self, master):
        
        global filter_place, filter_dictionary # TODO maybe this one is usless...
        def RemoveFilter(event = None, place = None):
            global active_filters
            frame.destroy()
            if DEBUG: print "RemoveFilter> called with ", place

            del filter_dictionary[place]
            active_filters = len(filter_dictionary)
            UpdateResults()


        def ValidateResName(event):
            print "A residue name validation request has been made"
            print "...maybe next time..."
            # TODO add a validation code
            pass


        def CreateFilter():
            global filter_place
            filter_place += 1
            Label(frame, text = "residue").grid(row = 0, column = 1)
            # Interact_with_residue, resname_entry, interaction_type_option
            res = StringVar()
            self.res = res
            value = Entry(frame, textvar = res, width = 10)
            value.grid(row = 0, column = 2)
            value.bind('<Double-Button-1>', ResidueList)
            value.bind("<Button-1>", ValidateResName)
            value.bind("<Return>", UpdateResults)
            value.bind("<Tab>", ValidateResName)
            #value.bind("<FocusIn>", ValidateResName)
            #value.bind("<FocusOut>", ValidateResName)


            interact = StringVar(value = "HB")
            OptionMenu(frame, interact, "HB", "vdW").grid(row = 0, column = 3) # TODO include Distance, P/P, Cat/P?
            #status_var = StringVar(value = "initialized")
            #Label(frame, textvar = status_var).grid(row = 0, column = 4, sticky = W) # % survivors label
            filter_dictionary[str(filter_place)] = [res, interact]
            active_filters = len(filter_dictionary)

        frame = Frame(master)
        #frame.grid(row = 1 + len(filter_dictionary), column = 0, sticky = W) # <-- Buggy
        frame.grid(row = 1 + filter_place, column = 0, sticky = W)
        self.button = Button(frame, text = "x") 
        a = str(filter_place+1) # ugly workaround
        self.button.bind("<Button-1>", lambda x: RemoveFilter(place = a))


        self.button.grid(row = 0, column = 0)
        CreateFilter()
        """
        print "NewFilter> creating button with following properties:"
        print "\t filter_place", filter_place
        print "===bound the button to delete", a
        print "\n\n---------------------------------"
        print "status of filters"
        for i in filter_dictionary:
            print "name : ", i
            print "value: ", filter_dictionary[i]
        print "---------------------------------\n\n" 
        """

def AddFilter():
    global FilterContainer, Filter_starter, filter_type

    if len(filter_dictionary) > 9:
        showwarning("Too many filters!", "The maximum number of filters is already applied. Delete some or...")
        return
    if ReceptorFilename.get() == "":
        showwarning("Receptor not defined", "To set a residue interaction filter, it's necessary to specify the receptor filename.")
        if not SelectReceptor():
            return False
        return
        

    #FFF = NewFilter(FilterContainer)
    NewFilter(FilterContainer)


def get_current_pose(ligand):
    choice = PoseChoice.get()
    if choice == "Absolute lowest energy":
        pose = "le"
    else:
        pose = "lc"
    try:
        if not LigBook[ligand]['vs'] == "":
            return LigBook[ligand]['vs']
        else:
            return LigBook[ligand][pose]
    except:
        if DEBUG: print "get_current_pose> problems in finding the ligand pose:\n\tlig: %s\n\tpose: %s" % (ligand, pose)
        return False




def FilterLigands():
    """
        generate the filters basing on the user inputs and filter the ligands list
        return the ligands that passed the filtering

        OUTPUT: returns the list of ligand names sorted by energy
    """

    
    def SortLigandsByEnergy(list, pose_name_dict): # TODO OBSOLETE
        """
        in:     list of ligand names
        out:    input list sorted by energy (got from the pose mode *currently selected*)
        """
        d = {}
        for l in list:
            ligand_info = get_ligand_info(l)
            e = ligand_info['energy']
            leff = ligand_info['ligand_efficiency']
            d[e] = l
        values = d.keys()
        values.sort() # ascending order
        out = []
        for v in values:
            out.append( pose_name_dict[d[v]] )
        return out

    def SortLigands(list, key = 'energy'):
        """
        in:     list of ligand names
        out:    input list sorted by energy (got from the pose mode *currently selected*)

        for the alternative keys, see get_ligand_info
        """

        def find_name(pose):
            return [NAME for NAME in LigBook.keys() if get_current_pose(NAME) == pose][0]

        d = {}
        for l in list:
            d[l] = get_ligand_info(l, data = key)

        result = []
        for sorted_ligand in sorted(d.items(), key=itemgetter(1)):
            result.append(find_name(sorted_ligand[0]))
        return result

    if not len(LigBook):
        if DEBUG: print "FilterLigands> no ligands, returning shamelessly"
        EnergySurvivors.set(value = "")
        ClusterSurvivors.set(value = "")
        LESurvivors.set(value = "")
        InFilterSurvivors.set(value = "")
        Epiechart.set_percent(0.)
        Cpiechart.set_percent(0.)
        LEpiechart.set_percent(0.)
        RESpiechart.set_percent(0.)

        return False
    # 
    """
    choice = PoseChoice.get()
    if choice == "LE/LC":
        pose = "lc"
    else:
        pose = "le"
    """

    ligand_list = []
    pose_name_dict = {}

    ############################################################
    ################## FAKING CODE #############################
    fake = False
    #fake = True
    if fake: 
        dict = {}
        #sort the results by energy
        for l in LigBook.keys():
            ligand_info = get_ligand_info(l)
            e = ligand_info['energy']
            leff = ligand_info['ligand_efficiency']
            dict[e] = l
        values = dict.keys()
        values.sort() # ascending order
    
        result = []
        for v in values:
            result.append( dict[v] )
        if DEBUG: print "Filter> TEMPORARY returning SORTED! dict keys"
        return result
    ############################################################
    ################## FAKE CODE ###############################
   

    # get the list of ligands to be filtered
    if len(to_be_reclustered) > 0:
        if DEBUG: print "FilterLigands> there are %d ligands to be reclustered, hand-bracking right here..." % len(to_be_reclustered)
        if askyesno('Missing poses',"There are %d ligands that need to be re-clustered before being filtered.\n\nProceed with the re-cluster?" % len(to_be_reclustered)):
            ImportLigandOptions()
            return False
        else:
            if DEBUG: print "FilterLigands> user gave up reclustering"
            return False

    for l in LigBook:
        """
        if not LigBook[l]['vs'] == "":
            p = LigBook[l]['vs']
            if DEBUG: print "FilterLigands> ligand: %s => pose: %s" % (l, p)
        else:
            p = LigBook[l][pose]
            if DEBUG: print "FilterLigands> ligand: %s => pose: %s" % (l, p)
        """
        p = get_current_pose(l)
        ligand_list.append(p)
        pose_name_dict[ p ] = l # TODO probably obsolete
        if DEBUG: print "FilterLigands> using this pose", p

    if DEBUG: print "FilterLigands> Len of pose_name_dict: ", len(pose_name_dict) 
    if DEBUG: print "FilterLigands> got %d ligands" % len(ligand_list)

    tot_ligands = len(ligand_list)

    # create standard filters
    if DEBUG: print "FilterLigands> initialize pre-filters"
    # Energy filter
    if Evalidate():
        Femin = EnergyFilter(Emin.get())
        Femax = EnergyFilter(Emax.get())
    else:
        return False

    # cluster size
    if ClustCount.get() ==  "%":
        if Cvalidate():
            Fcmin = ClusterPercentageFilter( ClustMin.get()+0.01 ) # Add a small off-set to cope with lack of ranges in the the ADT filters
            Fcmax = ClusterPercentageFilter( ClustMax.get()+0.01 ) # Add a small off-set to cope with lack of ranges in the the ADT filters
        else:
            return False
    
    if ClustCount.get() ==  "#":
        if Cvalidate():
            Fcmin = ClusterSizeFilter( ClustMin.get()+1 ) # Add a small off-set to cope with lack of ranges in the the ADT filters
            Fcmax = ClusterSizeFilter( ClustMax.get()+1 ) # Add a small off-set to cope with lack of ranges in the the ADT filters
        else:
            return False

    
    # Ligand efficiency
    if LEvalidate():
        Flemin = LigandEfficiencyFilter( LEmin.get() )
        Flemax = LigandEfficiencyFilter( LEmax.get() )  
    else:
        return False



    ##########################################################
    # Ligand properties filtering
    current_total = len(ligand_list)

    # filtering by energy...
    pre_filt_min = filter(Femin.filter, ligand_list)
    pre_filt_max = filter(Femax.filter, ligand_list)

    prefiltering = []
    for l in pre_filt_min:
        if not l in pre_filt_max:
            prefiltering.append(l)
    count = len(prefiltering)
    if DEBUG: print "FilterLigands> ENERGY FILTER :\t%d" % count
    if count:
        count_pc = (float(count)/ tot_ligands)* 100
    else:
        count_pc = 0.
    string = "\t%d accepted\n\t%d rejected" % (count, tot_ligands-count)
    EnergySurvivors.set(string)
    Epiechart.set_percent(count_pc)


    # filtering by cluster size
    if len(prefiltering):
        pre_filt_min = filter(Fcmin.filter, prefiltering)
        pre_filt_max = filter(Fcmax.filter, prefiltering)
        if DEBUG:
            if DEBUG: print "FilterLigands> prefilter_MIN", len(pre_filt_min)
            if DEBUG: print "FilterLigands> prefilter_MAX", len(pre_filt_max)
        print pre_filt_max
        prefiltering = []
        # TODO TODO TODO use the intersect(pre_filt_min, prefilt_max) function
        for l in pre_filt_min:
            if not l in pre_filt_max:
                prefiltering.append(l)
    count = len(prefiltering)
    if DEBUG: print "FilterLigands> CLUSTER FILTER :\t%d" % count
    if count:
        count_pc = (float(count)/ tot_ligands)* 100
    else:
        count_pc = 0.
    string = "\t%d accepted\n\t%d rejected" % (count, tot_ligands-count)
    ClusterSurvivors.set(string)
    Cpiechart.set_percent(count_pc)

    # filtering by ligand efficiency
    if len(prefiltering):
        pre_filt_min = filter(Flemin.filter, prefiltering)
        pre_filt_max = filter(Flemax.filter, prefiltering)
        prefiltering = []
        for l in pre_filt_min:
            if not l in pre_filt_max:
                prefiltering.append(l)
    count = len(prefiltering)
    if DEBUG: print "FilterLigands> L_EFF FILTER :\t%d" % count
    if count:
        count_pc = (float(count)/ tot_ligands)* 100
    else:
        count_pc = 0.
    string = "\t%d accepted\n\t%d rejected" % (count, tot_ligands-count)
    LESurvivors.set(string)
    LEpiechart.set_percent(count_pc)


    if DEBUG:
        print "FilterLigands> %d survived the standard filtering process" % count

    #############################################
    # Interaction filters
    if len(prefiltering):
        if len(filter_dictionary):
            if DEBUG: print "#######\n\nTHERE IS AT LEAST A FILTER\n\n#########"
            FilteredLigands = []
            interaction_filter = []
            # TODO use the molecule name from MolKit?
            rec = os.path.basename(ReceptorFilename.get())
            rec = os.path.splitext(rec)[0]

            if DEBUG: print "FilterLigands> generating the interaction filters for %d interactions with receptor: %s" % (len(filter_dictionary), rec)
        
            for f in filter_dictionary:
                if DEBUG: print "FilterLigands> CREATING FILTER #", f
                res = filter_dictionary[f][0].get()
                i_type = filter_dictionary[f][1].get()
                # pattern = "USER  AD> " + rec + ":" + res + ":" TODO TO BE FIXED WITH RECEPTOR/BOX NAMING ISSUE
                pattern = ":" + res + ":"

                if DEBUG:
                    print "FilterLigands> \tresidue:", res
                    print "FilterLigands> \tinterac:", i_type
                if not res == "":
                    if i_type == "HB":
                        if DEBUG: print "FilterLigands> generate interaction filter HB+",pattern
                        interaction_filter.append( HydrogenBondInteractionFilter( receptor_str = pattern) )
                        #interaction_filter.append( HydrogenBondResidueFilter( receptor_str = rec, res_name = res, verbose = True) )
                    if i_type == "vdW":
                        #interaction_filter.append( CloseContactResidueFilter( receptor_str = rec, res_name = res, verbose = True) )
                        if DEBUG: print "FilterLigands> generate interaction filter vdW+",pattern
                        interaction_filter.append( CloseContactInteractionFilter( receptor_str = pattern) )

            # boolean operations
            bool_status = SimpleBool.get() 
            if DEBUG: print "FilterLigands> boolean mode |%s|" % bool_status
            if SimpleBool.get() == "all":
                for fx in interaction_filter:
                    if DEBUG: print "FilterLigands> filter :", fx
                    prefiltering = filter(fx.filter, prefiltering)
                FilteredLigands = prefiltering

            if SimpleBool.get() == "any":
                if DEBUG: print "FilterLigands> boolean mode *ANY*"
                for l in prefiltering:
                    for fx in interaction_filter:
                        if DEBUG: print "FilterLigands> filter :", fx
                        if filter(fx.filter, [l]):
                            if not l in FilteredLigands:
                                FilteredLigands.append(l)
                            break

            if DEBUG: print "FilterLigands> ligands that passed the interaction filters:", len(FilteredLigands)
        else:
            FilteredLigands = prefiltering
    else:
        FilteredLigands = []

    if DEBUG: print "Len filtered ligands pre", len(FilteredLigands)

    #FilteredLigands = SortLigandsByEnergy(FilteredLigands, pose_name_dict)
    FilteredLigands = SortLigands(FilteredLigands)
    if DEBUG: print "Len filtered ligands post", len(FilteredLigands)
    if DEBUG: print FilteredLigands

    count = len(FilteredLigands)
    #rejected_count -= count
    if count:
        count_pc = (float(count)/ tot_ligands)* 100
    else:
        count_pc = 0.
    string = "\t%d accepted\n\t%d rejected" % (count, tot_ligands-count)
    InFilterSurvivors.set(string)
    RESpiechart.set_percent(count_pc)
    #UpdateButtons()
    return FilteredLigands # energy sorted list of ligand names
        

    

def TagCurrentLigand(parent):
    global current_ligand
    if not current_ligand:
        return False

    curr_courier = "Courier 10"
    parent.tag_remove("current_ligand", 1.0, END)
    #print "Tagging current ligand... |%s|" % name
    word = current_ligand[0]+" "
    idx = '1.0'
    while 1:
        idx = parent.search(word, idx, stopindex = END)
        if not idx :
            break
        else:
            # print "TagCurrentLigand> Found!"
            pass
        #last_idx = '%s+%dc' % (idx, len(word))
        last_idx = idx.split(".")[0]+".end" # make a bar colored 'til the end of the line
        parent.tag_add("current_ligand", idx, last_idx)
        break
    parent.tag_config('current_ligand', font = curr_courier+" bold", foreground = 'white', background = 'SteelBlue1', borderwidth = 1) # Add bold!
    #parent.tag_bind(ligand, "<Button-1>", lambda x: LoadLigand(ligand_name = ligand) )  
    

def HideStickyLigands(show_only = False):
    for l in sticky_ligands:
        print "\nHideStickyLigands>\n\tLigand: ", l[0],
        name = pmv_name(l[1])
        print "\n\tName: ", name, "\n"
        if not name == current_ligand[0]:
            mv.deleteMol(name, log = 0)
    del sticky_ligands[:]
    

def MakeLigandSticky(ligand):
    global sticky_ligands

    #pose = get_current_pose(ligand)
    #name = os.path.basename(pose)
    #name = os.path.splitext(name)[0]

    if not ligand in sticky_ligands:
        if ligand == current_ligand[0]:
            print "this ligand is officially sticky:", ligand
            sticky_ligands.append(current_ligand)
        else:
            print "Only visible ligands can be made sticky"
    else:
        print "this ligand is already sticky:", ligand
        



def UpdateButtons():
    """
        For moving in the list with keys...
        http://effbot.org/tkinterbook/tkinter-events-and-bindings.htm

           TODO potential optimization if memory is not enough...
           def execute(self):
            print 'Return pressed, destroying EntryField.'
            self.entryfield.destroy()
    """
    # TODO add here the check: if there's a current ligand, change it's color
    # TODO if the current ligand is not in the viewer, set current_ligand = None and delete it!

    #print "UpdateButtons> PROBLEMATIC POINT: current_ligand", current_ligand
    if current_ligand and FilteredLigands:
        if not current_ligand[0] in FilteredLigands:
            mv.deleteMol(pmv_name(current_ligand[1]), log = 0)

    curr_courier = "Courier 10"

    def SelectLigand(name):
        if DEBUG: print "SelectLigand> got request for ", name
        LigBook[name]['selected'] = not LigBook[name]['selected']
        if current_ligand:
            if name == current_ligand[0]:
                Cheese()
        UpdateSelected()

    """
    # disabled, substituted by the tagging
    def BakeLigandButton(ligand, parent, width = None):
        button =  Button(parent, text = ligand, command = lambda : LoadLigand(ligand),
        relief = FLAT, height = 1, activebackground = 'SteelBlue1', activeforeground = 'white', width = width, justify = LEFT )
        #button.bind('<Button-2>', 
        return button
    """

    def TagLoadLigand(parent, ligand):
        word = ligand+" "
        idx = '1.0'
        while 1:
            idx = parent.search(word, idx, stopindex = END)
            if not idx :
                break
            else:
                if DEBUG: print "TagLigand> found ", idx
            last_idx = '%s+%dc' % (idx, len(word))
            last_idx = idx.split(".")[0]+".end"
            parent.tag_add(ligand, idx, last_idx)
            break
        parent.tag_bind(ligand, "<Button-1>", lambda x: LoadLigand( ligand ) )
        #parent.tag_bind('sticky', "<Button-3>", lambda x: sticky_ligands.append(ligand) if not ligand in sticky_ligands ligand )
        parent.tag_bind(ligand, "<Button-3>", lambda x: MakeLigandSticky(ligand))

    def TagStickyLigand(parent, ligand):
        word = ligand+" "
        idx = '1.0'
        while 1:
            idx = parent.search(word, idx, stopindex = END)
            if not idx :
                break
            else:
                if DEBUG: print "TagStickyLigand> found ", idx
            last_idx = idx.split(".")[0]+".end"
            parent.tag_add('sticky', idx, last_idx)
            break

        parent.tag_config('current_ligand', relief = SUNKEN, background = 'OrangeRed1')
        #font = curr_courier+" bold", foreground = 'white', background = 'SteelBlue1', borderwidth = 1) # Add bold!

        #return [NAME for NAME in LigBook.keys() if get_current_pose(NAME) == pose][0]


    def BakeSelLigandButton(ligand,parent, status, counter):
        #    checkvar = BooleanVar(value = False)
        #    chk = Checkbutton(master, variable = checkvar, state = DISABLED)
        #    chk.bind('<Button-1>', lambda x : SelectThisLigand( c ) )
        #    chk.grid(row = c + r_offset, column = 0)
    
        sel_variable = BooleanVar()
        check = Checkbutton(parent, text = counter, variable = sel_variable, onvalue=True, 
            indicatoron = False, height = 1, selectcolor = "SteelBlue1",
            activeforeground = 'white', activebackground = 'SteelBlue1', offrelief=FLAT, justify = CENTER,
            )
        check.bind('<Button-1>', lambda x: SelectLigand(ligand) )
        sel_variable.set(status)
        """
        if status:
            check.config(relief=SUNKEN)
            check.config(bg='red')
            check.invoke()
        """
        return check

    parent = ResultScrolledFrame
    
    parent.config(state = NORMAL)
    parent.delete(1.0, END)
    if not FilteredLigands:
        parent.insert(END, "\n\n\n\t\t[ no ligands ]")
        parent.config(state = DISABLED)
        return
    parent.config(state = NORMAL)
    c = 1

    max_name_len = 0
    for l in FilteredLigands:
        if len(l) > max_name_len:
            max_name_len = len(l)

    sel_bar_len = len(str(len(FilteredLigands)))

    for l in FilteredLigands:
        info = get_ligand_info(l)
        e = "%2.2f" % info['energy']
        leff = "%2.2f" % info['ligand_efficiency']
        tors = str(info['active_torsions'])
        sel_status = LigBook[l]['selected']

        selector  = BakeSelLigandButton(l, parent, sel_status, counter = ("% 4d" % c ))
        if sel_status:
            selector.config(relief=SUNKEN)
            selector.invoke()
        parent.window_create(END, window = selector)

        # normalize name lenght
        name = l
        while len(name) < max_name_len:
            name +=" "

        while len(e)< 6:
            e = " "+e

        # normalize tors
        if len(tors) < 2:
            tors = " "+tors


        text = " "+name+"  "+e+"  "+leff+"  "+tors
        parent.insert(END, text)

        # add newline
        if c < len(FilteredLigands):
            parent.insert(END, "\n")
        c += 1
 
    
    # Tagging ligands
    for l in FilteredLigands:
        if DEBUG: print "UpdateButtons> PROCESSING LIGAND", l
        TagLoadLigand(parent, l)
        TagStickyLigand(parent, l)

    TagCurrentLigand(parent)
            

    parent.config(state = DISABLED)



    # TODO remove BUTTONS, and add the text tagging for hyperlinking the ligand:
    # http://effbot.org/zone/tkinter-text-hyperlink.htm



    pass

def KeepInViewer(ligand):
    """ 
        Add the ligand to the viewer and keep it even
            if other ligands will be loaded (by adding it to a safe list)

        It can be reverted only by the showonly/hide-all buttons

    """
    print "KeepInViewer> keep this ligand in the viewer", ligand
    pass






def UpdateSelected():
    if DEBUG: print "UpdateSelected> got a request of selection update"
    c = 0
    if FilteredLigands:
        tot = len(FilteredLigands)
        for l in FilteredLigands:
            if LigBook[l]['selected']:
                c+=1
    else:
        tot = 0
    text = "Selected ligands :\t\t%d / %d" % (c,tot)
    CountSelLigands.set(text)
       


def UpdateResults(for_real = True):
    # used by the FILTER button
    # provide the False value for the Preview
    global FilteredLigands # list of ligand names
    if DEBUG:
        print "UpdateResults> Residue interactions"
        for i in filter_dictionary.keys():
            print "    Name", i
            print "    Res", filter_dictionary[i][0].get()
            print "    int", filter_dictionary[i][1].get()
        print "UpdateResults> let's testing"
    try:
        ValidateResName()
    except:
        pass
    Cvalidate()
    #UpdateEnergyProfile()
    FilteredLigands = FilterLigands()
    if DEBUG: print "UpdateResults> ligands that passed the filters", FilteredLigands
    if for_real:
        #UpdateButtons(True)
        UpdateButtons()
    UpdateSelected()







# Filters page #####################################################


# TODO Provide max/min values found in ligand set for each of the criteria?

#FilterGraphicsStats = Pmw.Group(Tab2, tag_text = 'Filter stats')

PoseFrame = Frame(Tab2)
Tab2.grid_rowconfigure(0, weight = 1)
Tab2.grid_rowconfigure(1, weight = 1)
Tab2.grid_rowconfigure(2, weight = 1)
Tab2.grid_rowconfigure(3, weight = 1)
Tab2.grid_rowconfigure(4, weight = 1)
Tab2.grid_rowconfigure(5, weight = 1)
Tab2.grid_rowconfigure(20, weight = 1)
PoseFrame.grid_rowconfigure(1, weight = 1)
#PoseFrame.grid_rowconfigure(1, weight = 1)
Label(PoseFrame, text = "Pose : ").grid(row = 1, column = 0, sticky = E)
OptionMenu(PoseFrame, PoseChoice, "Lowest energy in largest cluster", "Absolute lowest energy", command = UpdateResults ).grid(row = 1, column = 1, sticky = W)

#Radiobutton(PoseFrame, text='Lowest energy in largest cluster', value='LE/LC', variable=PoseChoice, command = UpdateResults).grid(row = 1, column = 1, sticky = W)
#Radiobutton(PoseFrame, text='Absolute lowest energy', value='LE', variable=PoseChoice, command = UpdateResults).grid(row = 1, column = 2, sticky = W)
PoseFrame.grid(row = 0, column = 0, columnspan = 3, sticky = W+E)

#FilterGraphicsStats.grid(row = 0, column = 0, columnspan = 2, padx = 3)


FilterStatFrame = Frame(Tab2)
FilterStatText = Text(Tab2, height=5, width=40, relief = FLAT)
FilterStatText.config(state = DISABLED)
# TODO add here the Energy profile? Static position with updated bars?
FilterStatText.grid(row = 1, column = 0,sticky = W)
#Label(FilterStatFrame, textvar = LigandsTotalCount)
FilterStatFrame.grid(row = 1, column = 1, columnspan = 4, sticky = W+E)



        

class PercentPie(Canvas):
    #is it using Pmw or only Tk ?
    #def __init__(self, master, name, h = 100, w = 100, center = [0,0], radius = 75, pad = 3, percent = 15):
    def __init__(self, master, name, h = 100, w = 100, center = [0,0], radius = 75, pad = 3):
        Canvas.__init__(self,master)
        self.frame = Frame(self)
        self.canvas = Canvas(self.frame, width = w, height = h)

        self.bg = self.canvas.create_oval(center[0]+pad-1, center[1]+pad-1, center[0]+pad+1+radius, center[1]+pad+1+radius, fill = 'red', outline = 'black')
        self.bg = self.canvas.create_oval(center[0]+pad, center[1]+pad, center[0]+pad+radius, center[1]+pad+radius, outline = 'DarkSalmon')
        #self.bg = self.canvas.create_oval(center[0]+pad, center[1]+pad, center[0]+pad+radius, center[1]+pad+radius, outline = 'light coral')
        self.arc = self.canvas.create_arc(center[0]+pad, center[1]+pad, center[0]+pad+radius, center[1]+pad+radius,
                                         start = 0, extent = 0, fill = 'red', outline = 'red', tags = name)
        self.text_shadow = self.canvas.create_text(center[0]-1+pad+radius/1.8, center[1]+1+pad+radius/2, font = 'helvetica 9 bold', fill = 'steel blue', text = ( "000.000%") )
        self.text = self.canvas.create_text(center[0]+pad+radius/1.8, center[1]+pad+radius/2, font = 'helvetica 9 bold', fill = 'white', text = ( "000.000%") )
        self.frame.grid(row = 0, column = 0, sticky = N+W+E+S)
        self.canvas.grid(row = 0, column = 0, sticky = N+W+E+S)
    def set_percent(self, percent):

        if percent == 0.00:
            if DEBUG: print "PercentPie> got a ZERO percent"
            self.canvas.itemconfig(self.arc, start = 0, extent = 0, fill = 'red', outline = 'red')
        else:
            if DEBUG: print "PercentPie> got a non-ZERO percent,"
            if percent == 100:
                if DEBUG: print "100!"
                angle = 359.9
                start = -0.1
                self.canvas.itemconfig(self.arc, start = start, extent = angle, fill = 'SteelBlue1', outline = 'SteelBlue1')
            else:
                if DEBUG: print percent
                angle = (float(percent)/float(100))*float(360)
                start = -angle/2.
            #print "CONFIGURE ME!", self.canvas.itemconfig(self.arc)
                self.canvas.itemconfig(self.arc, start = start, extent = angle, fill = 'SteelBlue1', outline = 'steel blue')
            if DEBUG: print "\n\n\n\n\nPercentPie> the arc" ,self.arc, "\n\n\n\n\n"
            if DEBUG: print "CONFIGURE ME!"
            if DEBUG:
                for i in self.canvas.itemconfig(self.arc):
                    print i, "=", self.canvas.itemconfig(self.arc, i)
                print "\n\n\n\n\nPercentPie> the arc" ,self.arc, "\n\n\n\n\n"
        self.canvas.itemconfig(self.text, text = ( ("%3.3f %s") % ( percent, "%") )) 
        self.canvas.itemconfig(self.text_shadow, text = ( ("%3.3f %s") % ( percent, "%") )) 
        


# Energy filter field
EnergyFilterFrame = Pmw.Group(Tab2, tag_text = '1.Energy')

Epiechart = PercentPie(EnergyFilterFrame.interior(), 'energy_pie')
Epiechart.grid(row = 0, column = 0, rowspan = 5, sticky = W+N+S+E)

Label(EnergyFilterFrame.interior(), text = "MIN").grid(row = 0, column = 2, sticky = N)
Label(EnergyFilterFrame.interior(), text = "MAX").grid(row = 0, column = 3, sticky = N)

emin = Entry(EnergyFilterFrame.interior(), textvar = Emin, width = 8, justify = RIGHT)
emin.grid(row = 1, column = 2, sticky = W+E+N+S)
emax = Entry(EnergyFilterFrame.interior(), textvar = Emax, width = 8, justify = RIGHT)
emax.grid(row = 1, column = 3, sticky = W+E+N+S)
Label(EnergyFilterFrame.interior(), text = "Kcal/mol").grid(row = 1, column = 4, sticky = W+N)
for i in emin, emax:
    i.bind("<Button-1>", Evalidate)
    i.bind("<Return>", UpdateResults)
    i.bind("<Tab>", Evalidate)
    i.bind("<FocusIn>", Evalidate)
    i.bind("<FocusOut>", Evalidate)
Button(EnergyFilterFrame.interior(), text = "Default", command = lambda : DefaultFilterValues('energy')).grid(row = 2, column = 2, columnspan = 2, sticky = E+W+N)
#Label(EnergyFilterFrame.interior(), text ="  ").grid(row = 3, column = 2, columnspan = 2, sticky = N+S+W+E) # trick for Tk limitations
#Label(EnergyFilterFrame.interior(), text ="  ").grid(row = 4, column = 2, columnspan = 2, sticky = N+S+W+E) # trick for Tk limitations
#Label(EnergyFilterFrame.interior(), text ="  ").grid(row = 5, column = 2, columnspan = 2, sticky = N+S+W+E) # trick for Tk limitations

Label(EnergyFilterFrame.interior(), textvar = EnergySurvivors, justify = LEFT).grid(row = 4, column = 2, columnspan = 2, sticky = W)
#Label(Epiechart.frame, textvar = EnergySurvivors).grid(row = 1, column = 0, columnspan = 1, sticky = N+E)

EnergyFilterFrame.grid(row = 2, column = 0, sticky = 'WENS', columnspan = 3)

# cluster fields
ClusterFilterFrame = Pmw.Group(Tab2, tag_text = '2.Clustering')

Cpiechart = PercentPie(ClusterFilterFrame.interior(), 'cluster_pie')
Cpiechart.grid(row = 0, column = 0, rowspan = 5, sticky = W+N+S+E)

Label(ClusterFilterFrame.interior(), text = "MIN").grid(row = 0, column = 2, sticky = N)
Label(ClusterFilterFrame.interior(), text = "MAX").grid(row = 0, column = 3, sticky = N)

cmin = Entry(ClusterFilterFrame.interior(), textvar = ClustMin, width = 8, justify = RIGHT)
cmin.grid(row = 1, column = 2, sticky = W+E+N+S)
cmax = Entry(ClusterFilterFrame.interior(), textvar = ClustMax, width = 8, justify = RIGHT)
cmax.grid(row = 1, column = 3, sticky = W+E+N+S)
OptionMenu(ClusterFilterFrame.interior(), ClustCount, "%", "#", command = Cvalidate ).grid(row = 1, column = 4, sticky = W+N+E+S)
for i in cmin, cmax:
    i.bind("<Button-1>", Cvalidate)
    i.bind("<Return>", UpdateResults)
    i.bind("<Tab>", Cvalidate)
    i.bind("<FocusIn>", Cvalidate)
    i.bind("<FocusOut>", Cvalidate)

Button(ClusterFilterFrame.interior(), text = "Default", command = lambda : DefaultFilterValues('cluster')).grid(row = 2, column = 2, columnspan = 2, sticky = E+W+N)
Label(ClusterFilterFrame.interior(), textvar = ClusterSurvivors, justify = LEFT).grid(row = 4, column = 2, sticky = W, columnspan = 2)
ClusterFilterFrame.grid(row = 3, column = 0, sticky = 'WENS', columnspan = 3)


# efficiency fields
LEfficiencyFilterFrame = Pmw.Group(Tab2, tag_text = '3.Ligand efficiency')

LEpiechart = PercentPie(LEfficiencyFilterFrame.interior(), 'leffic_pie')
LEpiechart.grid(row = 0, column = 0, rowspan = 5, sticky = W+N+S+E)

Label(LEfficiencyFilterFrame.interior(), text = "MIN").grid(row = 0, column = 2, sticky = N)
Label(LEfficiencyFilterFrame.interior(), text = "MAX").grid(row = 0, column = 3, sticky = N)
lemin = Entry(LEfficiencyFilterFrame.interior(), textvar = LEmin, width = 8, justify = RIGHT)
lemin.grid(row = 1, column = 2, sticky = W+E+N+S)
lemax = Entry(LEfficiencyFilterFrame.interior(), textvar = LEmax, width = 8, justify = RIGHT)
lemax.grid(row = 1, column = 3, sticky = W+E+N+S)
Label(LEfficiencyFilterFrame.interior(), text ="             ").grid(row = 1, column = 4, sticky = W+E) # trick to deal with Tk limitations
for i in lemin, lemax:
    i.bind("<Button-1>", LEvalidate)
    i.bind("<Return>", UpdateResults)
    i.bind("<Tab>", LEvalidate)
    i.bind("<FocusIn>", LEvalidate)
    i.bind("<FocusOut>", LEvalidate)

Button(LEfficiencyFilterFrame.interior(), text = "Default", command = lambda : DefaultFilterValues('efficiency')).grid(row = 2, column = 2, columnspan = 2, sticky = E+W+N)
Label(LEfficiencyFilterFrame.interior(), textvar = LESurvivors, justify = LEFT).grid(row = 4, column = 2, sticky = W+N, columnspan = 2)
LEfficiencyFilterFrame.grid(row = 4, column = 0, sticky = 'WENS', columnspan = 3)


# residue filters

InteractionFilterFrame = Pmw.Group(Tab2, tag_text = '4.Interaction filters')
PieFrame = Frame(InteractionFilterFrame.interior())
RESpiechart = PercentPie(PieFrame, 'interaction_pie')
RESpiechart.grid(row = 0, column = 0, columnspan = 1, rowspan = 2, sticky = N+W+E)
Label(PieFrame, textvar = InFilterSurvivors, justify = LEFT).grid(row= 2, column = 0, sticky = W+E, padx = 3, pady = 3)
PieFrame.grid(row = 0, column = 0, columnspan = 3, sticky = N+W+E)

bool_frame = Frame(InteractionFilterFrame.interior())
Radiobutton(bool_frame, text = "all", variable = SimpleBool, value = "all").grid(row = 0, column = 1, sticky = E+N)
Radiobutton(bool_frame, text = "any", variable = SimpleBool, value = "any").grid(row = 0, column = 2, sticky = W+N)
# TODO the radiobuttons should trigger the filter updates
bool_frame.grid(row = 4, column = 0, sticky = W+E, columnspan = 2)

FilterContainer = Frame(InteractionFilterFrame.interior())
active_filters = 0
Filter_starter = Button(FilterContainer, text = "Add a filter...", command = AddFilter) # TO BE UPDATED AS GRAY WHEN TOO MANY FILTERS ARE ACTIVATED
Filter_starter.grid(row = 999, column = 0, sticky = W+E, padx = 5, pady = 5)
FilterContainer.grid(row = 5, column = 0, columnspan = 3)


InteractionFilterFrame.grid(row = 2, column = 3, rowspan = 3, pady = 0, padx = 4, ipadx = 5, ipady = 5, sticky = W+E+N+S)




Button(Tab2, text='Filter', command=UpdateResults, width = 30, height = 2).grid(row = 20, column = 0, columnspan = 4, sticky = W+E)


####################################### Viewer

def next_page(step = 1):
    global CurrentPage
    CurrentPage += step
    UpdateButtons()

def prev_page(step = 1):
    global CurrentPage
    CurrentPage -= step
    UpdateButtons()


def Update2Dligand(event):
	#event.widget.
	
	ligand_name = 1 # event_something?
	


def resetview(force = None):
    # force = "grid box", "ligand", "receptor"
    global vi
    if not force:
        who = CenterViewOption.get() # "grid box", "ligand", "receptor"
    else:
        who = force
    if DEBUG: print "resetview> centering on ", who

    #vi.GUI.VIEWER.Reset_cb()
    #vi.GUI.VIEWER.Normalize_cb()
    #vi.GUI.VIEWER.Center_cb()
    #vi.Reset_cb()
    #vi.Normalize_cb()
    #vi.Redraw()

    if who == "[ off ]":
        return

    if who == "grid box":
        if GPFboxMolName:
            vi.SetCurrentObject(GPFboxMolName.geomContainer.masterGeom)
        else:
            pass
            # center on receptor
    if who == "ligand":

        if current_ligand:
            name = pmv_name(current_ligand[1])
            ligand_instance = mv.Mols.objectsFromString(name)[0]
            #print "TRYING TO CENTER ON THE LIGAND WITH AN INSTANCE", ligand_instance
            vi.SetCurrentObject(ligand_instance.geomContainer.masterGeom)
        else:
            pass
            # center on receptor
    if who == "receptor":
            vi.SetCurrentObject(ReceptorMolecule.geomContainer.masterGeom)

    vi.Reset_cb()
    vi.Normalize_cb()
    vi.Center_cb()
    # todo apply all the styles to the receptor
    vi.SetCurrentObject(vi.rootObject)
    # set view clipping planes 
    CAMERA.Set(far = 200)
    CAMERA.Set(near = 0.1)
    #CAMERA.fog.Set(enabled = 1)
    #CAMERA.fog.Set(start = 60)
    #CAMERA.fog.Set(end = 90)


    vi.Redraw()

    return



def pmv_name(filename):
    if DEBUG: print "pmv_name> got this filename", filename
    name = os.path.basename(filename)
    return os.path.splitext(name)[0]
    
    

def LoadLigand(ligand, force_pose = None): 
    DEBUG = True

    """
    load the ligand in the viewer and update the status of current_ligand

    current_ligand = [ligand_name, loaded_ligand_pose]
    """

    global current_ligand
    # TODO SwitchLCradio.invoke()
    # TODO SwitchLEradio.invoke()
    # show interactions? 
    # center the viewer on the ligand?

    if not ReceptorMolecule:
        if askyesno("Show ligand", "The receptor has not been defined.\n\nDo you want to load it now?"):
            if not SelectReceptor():
                return False
        else:
            return False

    if current_ligand:
        if ligand == current_ligand[0]:
            return
    # check for sticky ligands # 
    if current_ligand:
        if DEBUG:
            print "LoadLigand> I would delete this:"
            print "\tFILENAME:\t",current_ligand[1]
            print "\tNAME:\t",pmv_name(current_ligand[1])

        if not current_ligand in sticky_ligands:
            if DEBUG: print "deleting", pmv_name(current_ligand[1])
            mv.deleteMol(pmv_name(current_ligand[1]), log = 0)
            if DEBUG: print "\t\t[DONE]"
        else:
            if DEBUG: print "\t\t ..oh-wait. STICKY LIGAND!"

    #top = None # toplevel window for the histogram

    if not force_pose:
        ligand_filename = get_current_pose(ligand)
    else:
        ligand_filename = force_pose


    if not current_ligand:
         mv.readMolecule(ligand_filename, "ligand", log = 0)
    else:
        if not ligand == current_ligand[0]:
            mv.readMolecule(ligand_filename, "ligand", log = 0)
    current_ligand = [ligand, ligand_filename]

    TagCurrentLigand(ResultScrolledFrame) #, ligand = ligand)

    cam = vi.cameras[1]
    cam.SelectCamera()
    cam.tk.call(cam._w, 'makecurrent') 
    cam.focus_set()

    LigStyle()
                          
    if RecSubset.get() == "interacting with ligand" or ResidueLabelLevel.get() == 'interacting':
        print "LoadLigand> updating the interacting residues"
        RecStyle()

    resetview() # center the view

    if DEBUG: print "\n\nGot here"
    UpdateLigandInfo(ligand_filename)


def showPmv():
    global mv
    mv.GUI.ROOT.deiconify()

def hidePmv():
    global mv
    mv.GUI.ROOT.withdraw()



# TODO maybe obsolete
def dockCamera():
    global mv, group_VIEWER
    addPmvCamera(mv,group_VIEWER)
# TODO maybe obsolete



def hex_to_rgb(string, base = 1, pmv = True):
    """
    convert hex color value to rgb base 1 or 255
       -TkInter works in HEX or RGB_255
       -PMV works with RGB_1

    "string" usually equal to "#00ff00"
    """
    #string = string[1:]
    r = int(string[1:3], 16)
    g = int(string[3:5], 16)
    b = int(string[5:7], 16)
    if base == 1:
        #print "hex_to_rgb> returning base_1 color"
        r = float(r)/255.
        g = float(g)/255.
        b = float(b)/255.
        if not pmv:
            return array( [r,g,b], 'f' )
        else:
            return (r,g,b)

        #return  [ float(r)/255. , float(g)/255., float(b)/255. ]
    if base == 255:
        return array( [ r, g, b ], 'f')
    print "Madeeche', aho'..."
    return False



def Style(event):
	""" apply a combination of preset styles to both ligand and receptors"""
	# TODO remember to have the default mode (e.g. to restore stick color)
	pass
    








def LigStyle(event = None, target = None, mode = None):
    # TODO implement support for stick colors?
    # TODO Set a different style for STICKY LIGAND

    global current_ligand
    representation = LigRepresentation.get()
    color = LigColormode.get()
    c_color = hex_to_rgb( LigCarbonColor.get() )
    if DEBUG: print "\n\n\n\nLigStyle> C_color", c_color

    if not target:
        target = pmv_name(current_ligand[1])
        if DEBUG:print "LigStyle> [LIGAND_MOL] Running with ", target
    else:
        if DEBUG: print "LigStyle> [TARGET] Running with ", target

    # cleanup: removing all previous representations
    # TODO show only doesn't work.. ??
    mv.displayMSMS(target, negate = True)
    mv.displayCPK(target, negate = True)
    mv.displaySticksAndBalls(target, negate=True)
    mv.displayLines(target,negate = True)

    ############################################################
    # REPRESENTATIONS
    if not mode:
        mode = LigRepresentation.get()
    if mode == "Lines":
        mv.displayLines(target, negate=False, displayBO=False,log=0, lineWidth=2.0)
    if mode == "Sticks": 
        mv.displaySticksAndBalls(target, log=0, cquality=0, sticksBallsLicorice='Licorice',
            bquality=0, cradius=0.3, bRad=0.3, negate=False, bScale=0.0)
    if mode == "Ball'n'Sticks": 
        mv.displaySticksAndBalls(target, log=0, cquality=0, sticksBallsLicorice='Sticks and Balls',
            bquality=0, cradius=0.2, bRad=0.4, negate=False, bScale=0.0)
    if mode == "CPK":
        mv.displayCPK(target, log=0, cpkRad=0.0, quality=24, negate=False, scaleFactor=1.0)
    if mode == "MSMS":
        mv.computeMSMS(target, hdensity=6.0, hdset=None, log=0, density=5.0, pRadius=1.2, perMol=True,
            display=True, surfName='MSMS-MOL')

    ############################################################
    # COLORING SCHEME
    set = LigColormode.get()
    if current_ligand:
        if set == "DG colors" : 
            mv.colorAtomsUsingDG(target, ['sticks', 'lines', 'balls', 'MSMS-MOL', 'cpk'], log=0)
        if set == "Atom type": 
            mv.colorByAtomType(target, ['lines', 'sticks', 'balls', 'MSMS-MOL','cpk', ], log=0)
            mv.color(target+":::C*", [ c_color ], ['sticks', 'lines', 'balls', 'cpk', 'MSMS-MOL'], log=0)

    
    if DEBUG:
        print "LigStyle> going to use this values:", mode, set
        print "Setting the ligand style"
        print "\trepresentation", representation
        print "\tcolor mode", color
        print "\tcarbon color", c_color
    return

    # TODO add the text tagging for hyperlinking the ligand:
    # http://effbot.org/zone/tkinter-text-hyperlink.htm




def GetInteractions(l, pmv_format = False):
    """
    identify the current ligand pose selection,
    extract and report the contact residues
    """

    # TODO add a check for receptor name match?
    # name = os.path.basename(ReceptorFilename.get())
    # name = os.path.splitext(name)[0]

    if len(LigBook) == 0:
        return []

    OUT = "USER  AD> lig_close_ats:"
    IN  = "USER  AD> macro_close_ats:"

    """
    choice = PoseChoice.get()
    if choice == "LE/LC":
        pose = "lc"
    else:
        pose = "le"

    if not LigBook[l]['vs'] == "":
        file = LigBook[l]['vs']
    else:
        file = LigBook[l][pose]
    """


    lines = get_lines(l)
    #f = open(l, 'r')
    #lines = f.readlines()
    #f.close()

    inside = False
    output = []
    for l in lines:
        if DEBUG: print "GetInteractions> processing line ", l

        if OUT in l:
            if DEBUG:
                print "\n\n\nGetInteractions> found the following interactions:\n"
                print output
                print "\n\n"
            if not pmv_format:
                return output # list
            else:
                subset = ""
                name = pmv_name(ReceptorFilename.get())
                for r in output:
                    subset += name+":"+r+";"

                return subset

        if inside and "USER  AD>" in l:
            res = l.split(":", 1)[1]
            res = res.rsplit(":",1)[0]
            if DEBUG: print "===",res
            if not res in output:
                output.append(res)

        if IN in l:
            if DEBUG: print "GetInteractions> IN!!!!!!"
            inside = True



def RecStyle(event = None):
    """Performs receptor-related visualization options:
    	- visualize the selected subset/all 
    	- show representation
    	- apply color scheme
    

    # TODO NOTES

        - if a special halo style is going to be applied to interacting residues, they need to be *EXTRACTED* from the file
          generating both the "rigid" and the "flex" portions

    # for the buried-receptor mode, add the transparency to the sec.structure+backlines with automatically calculated back_color

    """

    global ReceptorMolecule # TODO possibly replaceable by name = pmv_name(xx)
    global BoxResList
    global LabelSTATUS
    global IN_residues, OUT_residues, ACTIVE_residues, INACTIVE_residues
    global current_full_rec_visible
    global current_full_rec_mode 
    global current_full_rec_color
    global current_full_rec_flat_color
    global current_box_visible
    global current_box_mode
    global current_box_color
    global current_box_c_color
    global current_ligand_interactions
    global current_labelset
    global current_labelcolor
    global current_ACTIVE_residues, current_INACTIVE_residues
    # TODO FIX THE LACK OF 

    def GetResInTheBoxSubset():
        # subset is in PMV format
        subset = ""
        name = pmv_name(ReceptorFilename.get())
        for r in BoxResList:
            r = r.replace("_", ":",1)
            r = r.replace("_", "")
            subset += name+":"+r+";"
        if DEBUG: print "GetResInTheBoxSubset> selection [gridbox]", subset
        return subset


    def GetAllResSubset():
        subset = ""
        name = pmv_name(ReceptorFilename.get())
        for r in FullResList:
            r = r.replace("_", ":",1)
            r = r.replace("_", "")
            subset += name+":"+r+";"
        if DEBUG: print "GetAllResSubset> selection [all receptor residues]", subset
        return subset
    
    def ApplyLabel(subset):
        # ResidueLabelLevel
        #   all, interacting, filter, none
        if subset == None:
            return
        color = hex_to_rgb( LabelColor.get(), pmv = True )
        # show the labels
        mv.labelByProperty(subset, font={'fontRotateAngles':(0.0, 0.0, 0.0),'fontStyle':'solid3d','includeCameraRotationInBillboard':0,
            'fontScales':(0.6, 0.6, 0.02),'fontTranslation':(0.0, 0.0, 3.0),'billboard':1,
            'fontSpacing':0.2,'font':'arial1.glf'}, log=0, format=None, only=0, location='Last', negate=0, textcolor=color, properties=['name'])
            #'fontSpacing':0.2,'font':'arial1.glf'}, log=0, format=None, only=1, location='Last', negate=0, textcolor=(1.0, 1.0, 1.0,), properties=['name'])
        # color them
        # TODO set the correct color on the fly...
        #mv.color(subset, [color] , ['ResidueLabels'], log=0)

    if not ReceptorMolecule:
        if DEBUG: print "No receptor yet... [EXIT]"
        return

    # get the current status
    name = pmv_name( ReceptorFilename.get() )
    box_visible = RecSubset.get() # which residues inside the box (inside, interacting, from filters) # vs current_showed
    box_mode = RecBoxRepresentation.get() # style
    box_color = RecBoxColormode.get() # color mode
    box_c_color = hex_to_rgb (RecBoxCarbonColor.get() ) # carbon color
    full_rec_visible = ShowAllRec.get() # visible
    full_rec_mode = RecAllRepresentation.get() # style      "Lines", "Sticks", "Ball'n'Sticks", "Secondary structure" ,"CPK", "MSMS"
    full_rec_color = RecAllColormode.get() # color mode     "Atom type", "DG colors", "Custom color" # last == flatcolor)
    full_rec_flat_color = hex_to_rgb( RecAllFlatColor.get()) # carbon color
    labelset = ResidueLabelLevel.get()  # labeling level     all, interacting, none
    labelcolor = LabelColor.get()       # label color
    if current_ligand:
        ligand_interactions = current_ligand[0]
    else:
        ligand_interactions = None

    # TODO hic sunt leones: set all the current_* variables to None

    # define IN and OUT residues
    if not IN_residues or not OUT_residues:
        """
        OUT_residues are always static (defined by the grid box size)
        IN_residues are always static (defined by the grid box size)

        ACTIVE_residues are IN_residues that are visible (i.e. ligand-interaction or filter-based) ==> special style

        [potentially useless ] INACTIVE_residues are IN_residues that are not visible                                     ==> generic style

        """
        if DEBUG: print "RecStyle> get the IN residues"
        IN_residues = ""
        if not len(GridInfo) < 5:
            IN_residues = GetResInTheBoxSubset()

        if DEBUG: print "RecStyle> get the OUT residues"
        all_protein_res = GetAllResSubset() #  Xtal:B:THR276;...;....; # TO BE USED FOR THE SECONDARY STRUCTURE REPRESENTATION!!!!
        test_subset = IN_residues.split(";")
        OUT_residues = ""
        for res in all_protein_res.split(";"):
            if res not in test_subset:
                OUT_residues += res+";"

    """
    Three modes:

        - inside the grid-box
            ACTIVE_residues     =   IN_residues
            INACTIVE_residues   =   [empty]
            
        - interacting with the ligand
            ACTIVE_residues     =   residues in contact (SHOW ONLY?)
            #INACTIVE_residues  =   IN_residues - contacts

        - from filters
            ACTIVE_residues     =   resideus from filters (SHOW ONLY)
    """

    #
    #          _____                    _____                    _____                    _____          
    #         /\    \                  /\    \                  /\    \                  /\    \         
    #        /::\    \                /::\    \                /::\    \                /::\    \        
    #       /::::\    \              /::::\    \              /::::\    \              /::::\    \       
    #      /::::::\    \            /::::::\    \            /::::::\    \            /::::::\    \      
    #     /:::/\:::\    \          /:::/\:::\    \          /:::/\:::\    \          /:::/\:::\    \     
    #    /:::/__\:::\    \        /:::/__\:::\    \        /:::/__\:::\    \        /:::/__\:::\    \    
    #   /::::\   \:::\    \      /::::\   \:::\    \      /::::\   \:::\    \      /::::\   \:::\    \   
    #  /::::::\   \:::\    \    /::::::\   \:::\    \    /::::::\   \:::\    \    /::::::\   \:::\    \  
    # /:::/\:::\   \:::\____\  /:::/\:::\   \:::\    \  /:::/\:::\   \:::\____\  /:::/\:::\   \:::\____\ 
    #/:::/  \:::\   \:::|    |/:::/__\:::\   \:::\____\/:::/  \:::\   \:::|    |/:::/  \:::\   \:::|    |
    #\::/   |::::\  /:::|____|\:::\   \:::\   \::/    /\::/    \:::\  /:::|____|\::/   |::::\  /:::|____|
    # \/____|:::::\/:::/    /  \:::\   \:::\   \/____/  \/_____/\:::\/:::/    /  \/____|:::::\/:::/    / 
    #       |:::::::::/    /    \:::\   \:::\    \               \::::::/    /         |:::::::::/    /  
    #       |::|\::::/    /      \:::\   \:::\____\               \::::/    /          |::|\::::/    /   
    #       |::| \::/____/        \:::\   \::/    /                \::/____/           |::| \::/____/    
    #       |::|  ~|               \:::\   \/____/                  ~~                 |::|  ~|          
    #       |::|   |                \:::\    \                                         |::|   |          
    #       \::|   |                 \:::\____\                                        \::|   |          
    #        \:|   |                  \::/    /                                         \:|   |          
    #         \|___|                   \/____/                                           \|___|          
    #                                                                                                    

    """

    Previous representations should be removed when:
        - change in the box_residues
        - change in the full_rec representation

    """

    """
    Residue sets should be updated with:
        - change in the box_residues
        - new ligand is loaded (if interaction mode?)
    """


    INACTIVE_residues = ""
    ACTIVE_residues = ""
    # define ACTIVE and INACTIVE residues
    if box_visible == "inside the grid-box":
        ACTIVE_residues = IN_residues # the full inbox residue set is used
    if box_visible == "from filters":
        "extract the residues used in filters"
        for f in filter_dictionary: # transform this into a separate function
            r = filter_dictionary[f][0].get()
            ACTIVE_residues += name+":"+r+";"
        INACTIVE_residues = ""
        active_res_list = ACTIVE_residues.split(";")
        for res_in in IN_residues.split(";"):
            if not res_in in active_res_list:
                INACTIVE_residues += res_in+";"
    if box_visible == "interacting with ligand":
        "extract the residues interacting with the ligand"
        #if current_ligand and not current_ligand == current_ligand_interactions:
        if current_ligand:
            ACTIVE_residues = GetInteractions(current_ligand[1], pmv_format = True)
            #print "Current ligand:", current_ligand[1]
        #print" active_residues:", ACTIVE_residues
        active_res_list = ACTIVE_residues.split(";")
        for res_in in IN_residues.split(";"):
            if not res_in in active_res_list:
                INACTIVE_residues += res_in+";"
    #print "active:",len(ACTIVE_residues)
    #print "inactive:",len(INACTIVE_residues)


    """
    # TODO use new Michel code...
    cam = vi.cameras[1]
    cam.SelectCamera()
    cam.tk.call(cam._w, 'makecurrent') 
    cam.focus_set()
    vi.SetCurrentObject(ReceptorMolecule.geomContainer.masterGeom)
    """

    rec_stick_thickness = .15 # cradius
    rec_bnstick_thickness = 0.1 # cradius
    # rec_balls_radius = 
    
    #raw_input("\n\nFULL_REC")
    # Full receptor
    if DEBUG: print "RecStyle> Change in FULL_REC_MODE", full_rec_mode
    # Remove previous representations
    if not current_full_rec_mode == full_rec_mode or current_full_rec_visible == full_rec_visible:
        if current_full_rec_mode == None:
            mv.displayLines(ReceptorMolecule,negate = True) # Default PMV mode
        else:
            mv.displayLines(OUT_residues,negate = True)

        mv.displaySticksAndBalls(OUT_residues, negate=True)
        mv.displayCPK(OUT_residues, negate = True)
        mv.displayMSMS(OUT_residues, negate = True) 
        mv.displayExtrudedSS(ReceptorMolecule, negate=True, only=False, log=0) # keep ReceptorMolecule or use all_protein_res
        if ShowAllRec.get():
            if full_rec_mode == "Lines":
                print "\n\n\t\t\t someone asked for LINES on the rec\n\n"
                mv.displayLines(OUT_residues, negate=False, displayBO=False, only=False, log=0, lineWidth=1.0)
            if full_rec_mode == "Sticks": 
                mv.displaySticksAndBalls(OUT_residues, log=0, cquality=0, sticksBallsLicorice='Licorice',
                    bquality=0, cradius=rec_stick_thickness, only=False, bRad=0.3, negate=False, bScale=0.0)
            if full_rec_mode == "Ball'n'Sticks": 
                mv.displaySticksAndBalls(OUT_residues, log=0, cquality=0, sticksBallsLicorice='Sticks and Balls',
                    bquality=0, cradius=rec_bnstick_thickness, only=False, bRad=0.3, negate=False, bScale=0.0)
            if full_rec_mode == "CPK":
                mv.displayCPK(OUT_residues, log=0, cpkRad=0.0, quality=24, only=False, negate=False, scaleFactor=1.0)
            if full_rec_mode == "MSMS": # TODO set some transparency if this is True?
                mv.computeMSMS(OUT_residues, hdensity=6.0, hdset=None, log=0, density=5.0, pRadius=1.2, perMol=False,
                    display=True, surfName='full_recMSMS')
            if full_rec_mode == "Secondary structure":
                mv.displayExtrudedSS(ReceptorMolecule, negate=False, only=False, log=0)


    # Inactive subset
    #raw_input("\n\nINACTIVE SET")
    # print "INACTIVE residues", INACTIVE_residues
    if INACTIVE_residues:
        #if not INACTIVE_residues == current_INACTIVE_residues or not full_rec_mode == current_full_rec_mode :
        if True:
            print "going to say something to the inactive"
            time.sleep(1) 
            mv.displayLines(current_INACTIVE_residues+current_ACTIVE_residues,negate = True)
            mv.displaySticksAndBalls(current_INACTIVE_residues+current_ACTIVE_residues, negate=True)
            mv.displayCPK(current_INACTIVE_residues+current_ACTIVE_residues, negate = True)
            mv.displayMSMS(current_INACTIVE_residues+current_ACTIVE_residues, negate = True) 
            if full_rec_mode == "Lines":
                mv.displayLines(INACTIVE_residues, negate=False, displayBO=False, only=False, log=0, lineWidth=1.0)
            if full_rec_mode == "Sticks": 
                mv.displaySticksAndBalls(INACTIVE_residues, log=0, cquality=0, sticksBallsLicorice='Licorice',
                    bquality=0, cradius= rec_stick_thickness , only=False, bRad=0.3, negate=False, bScale=0.0)
            if full_rec_mode == "Ball'n'Sticks": 
                mv.displaySticksAndBalls(INACTIVE_residues, log=0, cquality=0, sticksBallsLicorice='Sticks and Balls',
                    bquality=0, cradius=rec_bnstick_thickness, only=False, bRad=0.3, negate=False, bScale=0.0)
            if full_rec_mode == "CPK":
                mv.displayCPK(INACTIVE_residues, log=0, cpkRad=0.0, quality=24, only=False, negate=False, scaleFactor=1.0)
            if full_rec_mode == "MSMS":
                mv.computeMSMS(INACTIVE_residues, hdensity=6.0, hdset=None, log=0, density=5.0, pRadius=1.2, perMol=False,
                    display=True, surfName='inactiveMSMS')
    else:
        mv.displayLines(ACTIVE_residues,negate = True)
        mv.displaySticksAndBalls(ACTIVE_residues, negate=True)
        mv.displayCPK(ACTIVE_residues, negate = True)
        mv.displayMSMS(ACTIVE_residues, negate = True) 
 

    # Active subset
    #raw_input("\n\nACTIVE SET")
    if box_mode == "Lines":
        mv.displayLines(ACTIVE_residues, negate=False, displayBO=False, only=False, log=0, lineWidth=1.0)
    if box_mode == "Sticks": 
        mv.displaySticksAndBalls(ACTIVE_residues, log=0, cquality=0, sticksBallsLicorice='Licorice',
            bquality=0, cradius=rec_stick_thickness, only=False, bRad=0.3, negate=False, bScale=0.0)
    if box_mode == "Ball'n'Sticks": 
        mv.displaySticksAndBalls(ACTIVE_residues, log=0, cquality=0, sticksBallsLicorice='Sticks and Balls',
            bquality=0, cradius=rec_bnstick_thickness, only=False, bRad=0.3, negate=False, bScale=0.0)
    if box_mode == "CPK":
        mv.displayCPK(ACTIVE_residues, log=0, cpkRad=0.0, quality=24, only=False, negate=False, scaleFactor=1.0)
    if box_mode == "MSMS":
        mv.computeMSMS(ACTIVE_residues, hdensity=6.0, hdset=None, log=0, density=5.0, pRadius=1.2, perMol=False,
            display=True, surfName='activeMSMS')
    #if box_mode == "Secondary structure":
    #    mv.displayExtrudedSS(IN_residues, negate=False, only=False, log=0)

    #raw_input("\n\nEND")

    #    **                 **               **
    #   /**                /**              /**
    #   /**        ******  /**       *****  /**
    #   /**       //////** /******  **///** /**
    #   /**        ******* /**///**/******* /**
    #   /**       **////** /**  /**/**////  /**
    #   /********//********/****** //****** ***
    #   ////////  //////// /////    ////// /// 
    #   

    #print "LABELSET\t\t%s\t%s"% (labelset, current_labelset)
    #print "LIGAND_INTERACTIONS\t%s\t%s" % ( ligand_interactions, current_ligand_interactions)
    #print "labelset == 'interacting'", labelset == 'interacting'
    #print "ligand_interactions == current_ligand_interactions", not ligand_interactions == current_ligand_interactions

    if not labelset == current_labelset or (labelset == 'interacting' and not ligand_interactions == current_ligand_interactions) :

        #mv.labelByProperty(name+"::", font={'fontRotateAngles':(0, 0, 0),'fontStyle':'solid','includeCameraRotationInBillboard':False,
        #            'fontScales':(1.2, 1.2, 1.2),'fontTranslation':(0, 0, 3.0),'billboard':True,'fontSpacing':0.2,'font':'arial1.glf'}, log=0,
        #            format=None, only=0, location='Last', negate=1, textcolor=(1.0, 1.0, 1.0,), properties=[])
        print "Cleaning up old labels"
        mv.labelByProperty(name+"::", negate=1)
        subset = ""
        if labelset == "all":
            print "(all)"
            subset = GetResInTheBoxSubset()
        if labelset == "interacting":
            print "(interacting)"
            if current_ligand:
                subset = GetInteractions(current_ligand[1], pmv_format = True)
        # TODO deal with None and Filters?
        if not labelset == 'none':
            print "applying new ones"
            print "===\n\n", subset, "\n\n"
            ApplyLabel(subset)

    #      ******    *******   **         *******   *******  
    #     **////**  **/////** /**        **/////** /**////** 
    #    **    //  **     //**/**       **     //**/**   /** 
    #   /**       /**      /**/**      /**      /**/*******  
    #   /**       /**      /**/**      /**      /**/**///**  
    #   //**    **//**     ** /**      //**     ** /**  //** 
    #    //******  //*******  /******** //*******  /**   //**
    #     //////    ///////   ////////   ///////   //     // 


    # Full rec color
    #if not current_full_rec_color == full_rec_color or not current_full_rec_mode:
    #if DEBUG: print "COLOR = ", full_rec_color
    #if not full_rec_color == current_full_rec_color:
    # TODO Experimental
    target = OUT_residues
    print OUT_residues
    if INACTIVE_residues:
        target += INACTIVE_residues

    print "\n\n###\n"
    print target
    print "\n\n"
    print "\n\n###\n"
    if not full_rec_color == current_full_rec_color or not INACTIVE_residues == current_INACTIVE_residues:
        if full_rec_color == "Atom type":
            mv.colorByAtomType(target, ['lines', 'sticks', 'balls', 'full_recMSMS','inactiveMSMS','cpk', 'secondarystructure' ], log=0)
        if full_rec_color == "DG colors" : 
            mv.colorAtomsUsingDG(target, ['lines', 'sticks', 'balls', 'full_recMSMS','inactiveMSMS','cpk', 'secondarystructure' ], log=0)
        if full_rec_color == "Secondary structure" : 
            mv.colorBySecondaryStructure(target, ['lines', 'sticks', 'balls', 'full_recMSMS','inactiveMSMS','cpk', 'secondarystructure' ], log=0)
        if full_rec_color == "Custom color": 
            mv.color(target, [ full_rec_flat_color ],  ['lines', 'sticks', 'balls', 'full_recMSMS','inactiveMSMS','cpk', 'secondarystructure' ], log=0)

    # Box rec color 
    #if not current_box_color == box_color:
    if not box_color == current_box_color or not ACTIVE_residues == current_ACTIVE_residues or current_box_mode == current_box_mode: # TODO test this
        if box_color == "Atom type":
            mv.colorByAtomType(ACTIVE_residues, ['lines', 'sticks', 'balls', 'activeMSMS','cpk' ], log=0)
            c_subset = ""
            for x in ACTIVE_residues.split(";")[:-1]:
                c_subset += x+":C*;"
            if DEBUG: print c_subset
            mv.color(c_subset, [ box_c_color ],  ['lines', 'sticks', 'balls', 'activeMSMS','cpk' ], log=0)
        if box_color == "DG colors" : 
            mv.colorAtomsUsingDG(ACTIVE_residues, ['lines', 'sticks', 'balls', 'activeMSMS','cpk'], log=0)
        if box_color == "secondary structure" : 
            mv.colorBySecondaryStructure(ACTIVE_residues, ['lines', 'sticks', 'balls', 'activeMSMS','cpk' ], log=0)

    # TODO Label colors?

    # TODO verify this...
    current_full_rec_visible = full_rec_visible 
    current_full_rec_mode = full_rec_mode 
    current_full_rec_color = full_rec_color
    current_full_rec_flat_color = full_rec_flat_color 
    current_box_visible = box_visible
    current_box_mode = box_mode
    current_box_color = box_color
    current_box_c_color = box_c_color
    current_ligand_interactions = ligand_interactions
    current_ACTIVE_residues = ACTIVE_residues
    current_INACTIVE_residues = INACTIVE_residues

    #resetview()
    #vi.Redraw()
    #vi.SetCurrentObject(vi.rootObject)


    print " ======================== RecStyle END ======================\n\n\n"
    return

def ShowInteractions():
	print "ShowInteractions> something"	
	return


# TODO TODO TODO
# unify the color picker?
# see the TRACER for the variable
# http://effbot.org/tkinterbook/variable.htm
# TODO TODO TODO

def LigCarbColorPicker(event):
    """Set the color of ligand carbon atoms"""
    color_output = tkColorChooser.askcolor(parent = VisOptionsWin, color = LigCarbonColor.get())
    # contains RBG tuple and hex-value as rrggbb
    #colorTuple # for red = ((255, 0, 0), '#ff0000')
    print "==========", color_output
    if color_output[0]:
    	print color_output
    	print color_output[1]
    	LigCarbonColor.set(color_output[1])
    	event.widget.config(bg = LigCarbonColor.get())
    	#event.widget.config(bg = color_output[1])
    LigStyle()
    return

def RecCarbColorPicker(event):
    """Set the color of receptor subset carbon atoms
    (residues inside the box or in close contact) """
    color_output = tkColorChooser.askcolor(parent = VisOptionsWin, color = RecBoxCarbonColor.get())
    if color_output[0]:
    	RecBoxCarbonColor.set(color_output[1])
    	event.widget.config(bg = RecBoxCarbonColor.get())
    RecStyle()
    return

def RecFlatcolorPicker(event):
    """set the custom color for the rest of 
    the receptor representations"""
    color_output = tkColorChooser.askcolor(parent = VisOptionsWin, color = RecAllFlatColor.get())
    if color_output[0]:
    	RecAllFlatColor.set(color_output[1])
    	event.widget.config(bg = RecAllFlatColor.get())
    RecStyle()
    return

def SetBGcolor(event):
    global vi
    """set the custom color for the rest of 
    the receptor representations"""
    color_output = tkColorChooser.askcolor(parent = VisOptionsWin, color = BGcolor.get())
    #print color_output
    #print "IT DOESNT WORK YET..."
    #return
    if color_output[0]:
    	BGcolor.set(color_output[1])
    	event.widget.config(bg = color_output[1])
        c = hex_to_rgb( BGcolor.get() )
        #print "C now is ", c
        #print "elements", c[0], c[1], c[2]
        #print "type", type(c)
        #x =  [1.0, 1.0, 1.0]
        #print "----------"
        #vi.currentCamera.Set(color = c)
        #vi.Redraw()
        vi.CurrentCameraBackgroundColor( c)
    return


def HighlightRes():
    """
    highlight residues used for filtering

    SetHighlightRes_interacting = BooleanVar(value = True)
    SetHighlightRes_filtering = BooleanVar(value = True)
    

    filtering residues should have a different color/label size...
    """
    pass

def LabelColorPicker(event):
    """set the label color"""
    color_output = tkColorChooser.askcolor(parent = VisOptionsWin, color = LabelColor.get())
    if color_output[0]:
    	LabelColor.set(color_output[1])
    	event.widget.config(bg = LabelColor.get())
    RecStyle()
    return
    pass


def VisOptions():

    # TODO implement support for stick colors?
    # TODO convert to a notebook?

    global VisOptionsWin
    try:
        VisOptionsWin.deiconify()
        VisOptionsWin.lift()
        ViewerLabel.set("Viewer options>>")
        VisOptionsWin.destroy()
    except:
        ViewerLabel.set("Viewer option<<")
        VisOptionsWin = Toplevel(master = root, takefocus = True)
        VisOptionsWin.title("Visualization options")
        VisOptionsWin.winfo_toplevel().resizable(NO,NO)
        #VisOptionsWin.wm_attributes("-topmost", 1)
        #VisOptionsWin.wm_attributes('-topmost', 1)
        #VisOptionsWin.grid_rowconfigure(2, weight = 9)
        global LigCarbColorSample, RecCarbColorSample
        def LoadViewPreset():
            pass
        def SaveViewPreset():
            pass
    
        # TODO disabled feature
        Preset = Frame(VisOptionsWin)
        Label(Preset, text = "Visualization style preset : ").grid(row = 0, column = 0, sticky = E, pady = 15)
        PresetOptions = OptionMenu(Preset, PresetStyle, "Default", "Green sticks", "Surface halo", "Buried binding site" , command=Style).grid(row = 0, column = 1, sticky = W, padx = 15)
        Button(Preset, text = "Load", command = LoadViewPreset).grid(row = 0, column = 2, sticky = E)
        Button(Preset, text = "Save", command = SaveViewPreset).grid(row = 0, column = 3, sticky = E)
        #Frame(Preset, height=2, bd=1, relief=SUNKEN).grid(row = 1, column = 0, sticky = E+W, columnspan = 9, padx = 5, pady = 5)
        Preset.grid(row = 0, column = 0, sticky = W+E, columnspan = 2, padx = 5)

        vis_book = Pmw.NoteBook(VisOptionsWin)
        Lstructures = vis_book.add('Ligands')
        Rstructures = vis_book.add('Target')
        #Maps = vis_book.add('Grid maps')
        GenOptions = vis_book.add('3D viewer')
 
        ##### LIGAND

        #Lstructures = Pmw.Group(VisOptionsWin, tag_text = 'Ligand')
        Label(Lstructures, text = "Representation").grid(row = 0, column = 0, sticky = E)
        OptionMenu(Lstructures, LigRepresentation, "Lines", "Sticks", "Ball'n'Sticks", "CPK", "MSMS", command=LigStyle).grid(row = 0, column = 1, sticky = W+E)
        Label(Lstructures, text = "Color by").grid(row = 1, column = 0, sticky = E)
        OptionMenu(Lstructures, LigColormode, "Atom type", "DG colors", command=LigStyle).grid(row = 1, column = 1, sticky = W+E)
        Label(Lstructures, text = "Carbon color").grid(row = 2, column = 0, sticky = E)
        LigCarbColorSample = Button(Lstructures, bg = LigCarbonColor.get(), command = LigCarbColorPicker, relief = RIDGE, state = DISABLED)
        LigCarbColorSample.grid(row = 2, column = 1, sticky = W+E)
        LigCarbColorSample.bind("<Button-1>", LigCarbColorPicker)
        Checkbutton(Lstructures, text = "Show histogram").grid(row = 5, column = 1, columnspan = 2) # TODO not working
        #Lstructures.grid(row = 2, column = 0, padx = 5, pady = 5, sticky = W+E+N+S, ipadx = 5, ipady = 5)
    
     
        interactions = Pmw.Group(Lstructures, tag_text = 'Interactions')
        Checkbutton(interactions.interior(), text = "Hydrogen bonds", var = IntShowHB, command = ShowInteractions).grid(row = 0, column = 0, sticky = W, padx = 5,pady = 3)
        Checkbutton(interactions.interior(), text = "VdW contacts", var = IntShowVDW, command = ShowInteractions).grid(row = 1, column = 0, sticky = W, padx = 5,pady = 3)
        Checkbutton(interactions.interior(), text = "Electrostatics", var = IntShowElec, command = ShowInteractions).grid(row = 2, column = 0, sticky = W, padx = 5,pady = 3)
        Checkbutton(interactions.interior(), text = "Pi/Pi stacking", var = IntShowPP, command = ShowInteractions).grid(row = 0, column = 1, sticky = W, padx = 5,pady = 3)
        Checkbutton(interactions.interior(), text = "Cation/Pi", var = IntShowCatP, command = ShowInteractions).grid(row = 1, column = 1, sticky = W, padx = 5,pady = 3)
        Checkbutton(interactions.interior(), text = "Distance", var = IntShowDist, command = ShowInteractions).grid(row = 2, column = 1, sticky = W, padx = 5,pady = 3)
        interactions.grid(row = 6, column = 0, padx = 5 , pady = 5, columnspan = 2)
              

        ##### TARGET
        KeyResiduesFrame = Pmw.Group(Rstructures, tag_text = 'Grid box/interacting residues')
        #KeyResiduesFrame = Pmw.Group(Rstructures, tag_text = 'Grid box/interacting residues', tag_pyclass = Checkbutton) # TODO FIX FIX!, tag_variable = ShowAllRec, tag_command = RecStyle)
        Label(KeyResiduesFrame.interior(), text = "Residues subset").grid(row = 2, column = 0, sticky = E)
        OptionMenu(KeyResiduesFrame.interior(), RecSubset, "inside the grid-box", "interacting with ligand",
                    "from filters", command = RecStyle).grid(row = 2, column = 1, sticky = W+E)
        # separator
        Label(KeyResiduesFrame.interior(), text = "Representation").grid(row = 3, column = 0, sticky = E)
        OptionMenu(KeyResiduesFrame.interior(), RecBoxRepresentation, "Lines", "Sticks", "Ball'n'Sticks",
                    "CPK", "MSMS", command=RecStyle).grid(row = 3, column = 1, sticky = W+E)

        Label(KeyResiduesFrame.interior(), text = "Color by").grid(row = 4, column = 0, sticky = E)
        OptionMenu(KeyResiduesFrame.interior(), RecBoxColormode, "Atom type", "DG colors", "Secondary structure", command=RecStyle).grid(row = 4, column = 1, sticky = W+E)
        Label(KeyResiduesFrame.interior(), text = "Carbon color").grid(row = 5, column = 0, sticky = E)
        RecCarbColorSample = Button(KeyResiduesFrame.interior(), bg = RecBoxCarbonColor.get(), command = RecCarbColorPicker, relief = RIDGE)
        RecCarbColorSample.grid(row = 5, column = 1, sticky = W+E)
        RecCarbColorSample.bind("<Button-1>", RecCarbColorPicker)

        Checkbutton(KeyResiduesFrame.interior(), text = "Highlight interacting residues", var = SetHighlightRes_interacting,
                    command = HighlightRes).grid(row = 6, column = 0, columnspan = 3, sticky = W, padx = 5)
        
        Checkbutton(KeyResiduesFrame.interior(), text = "Highlight filter residues", var = SetHighlightRes_filtering,
                    command = HighlightRes).grid(row = 7, column = 0, columnspan = 3, sticky = W, padx = 5)
    
        # separator
        Frame(KeyResiduesFrame.interior(), height=2, bd=1, relief=SUNKEN).grid(row = 8, column = 0, sticky = E+W, columnspan = 9, padx = 10, pady = 15)
        Label(KeyResiduesFrame.interior(), text = " Label residues ").grid(row = 8, column = 0, columnspan = 2, padx = 5)
        Radiobutton(KeyResiduesFrame.interior(), text = "inside\nthe box", value = "all", var = ResidueLabelLevel, command = RecStyle).grid(row = 9, column = 0, padx = 5)
        Radiobutton(KeyResiduesFrame.interior(), text = "interacting\nwith ligand", value = "interacting",
                    var = ResidueLabelLevel, command = RecStyle).grid(row = 9, column = 1, padx = 5)
        Radiobutton(KeyResiduesFrame.interior(), text = "[ off ]", value = "none", var = ResidueLabelLevel, command = RecStyle).grid(row = 9, column = 2, padx = 5)


        Label(KeyResiduesFrame.interior(), text = "Label color").grid(row = 10, column = 0, sticky = E)
        LabelColorSample = Button(KeyResiduesFrame.interior(), bg = LabelColor.get(), command = LabelColorPicker, relief = RIDGE)
        LabelColorSample.grid(row = 10, column = 1, sticky = W+E, pady = 3)
        LabelColorSample.bind("<Button-1>", LabelColorPicker)

        KeyResiduesFrame.grid(row = 2, column = 0, columnspan = 2, sticky = W+E, padx = 5)
        # separator
        #Frame(Rstructures, height=2, bd=1, relief=SUNKEN).grid(row = 10, column = 0, sticky = E+W, columnspan = 9, padx = 10, pady = 15)
        #Label(Rstructures, text = " All residues ").grid(row = 10, column = 0, columnspan = 2)

        AllResiduesFrame = Pmw.Group(Rstructures, tag_text = 'All residues', tag_pyclass = Checkbutton, tag_variable = ShowAllRec, tag_command = RecStyle)

        Label(AllResiduesFrame.interior(), text = "Representation").grid(row = 11, column = 0, sticky = E)
        OptionMenu(AllResiduesFrame.interior(), RecAllRepresentation, "Lines", "Sticks", "Ball'n'Sticks", "Secondary structure" ,"CPK", "MSMS", command= RecStyle ).grid(row = 11, column = 1, sticky = W+E)
        Label(AllResiduesFrame.interior(), text = "Color by").grid(row = 12, column = 0, sticky = E)
        OptionMenu(AllResiduesFrame.interior(), RecAllColormode, "Atom type", "DG colors", "Custom color", "Secondary structure", command=RecStyle).grid(row = 12, column = 1, sticky = W+E)
        Label(AllResiduesFrame.interior(), text = "Custom color").grid(row = 13, column = 0, sticky = E)
        RecFlatColorSample = Button(AllResiduesFrame.interior(), bg = RecAllFlatColor.get(), command = RecFlatcolorPicker, relief = RIDGE)
        RecFlatColorSample.grid(row = 13, column = 1, sticky = W+E, pady = 3)
        RecFlatColorSample.bind("<Button-1>", RecFlatcolorPicker)
    
    
        AllResiduesFrame.grid(row = 3, column = 0, columnspan = 2, sticky = W+E, padx = 5, pady = 5)

        # Grid Maps ########################################################
        # NONE SO FAR...
        #########################

        # general options
        gen_options = Pmw.Group(VisOptionsWin, tag_text = 'Default options')
        Label(GenOptions, text = "Background color").grid(row = 1, column = 0, sticky = E)
        BGColorSample = Button(GenOptions, bg = BGcolor.get(), command = SetBGcolor, relief = RIDGE)
        BGColorSample.grid(row = 1, column = 1, sticky = W+E )
        BGColorSample.bind("<Button-1>", SetBGcolor)
        Label(GenOptions, text = "Auto center view on :").grid(row = 2, column = 0)
        OptionMenu(GenOptions, CenterViewOption, "grid box", "ligand", "receptor", "[ off ]").grid(row = 2, column = 1, sticky = W+E)
        Label(GenOptions, text = "Anti-alias level").grid(row = 3, column = 0, sticky = E)
        OptionMenu(GenOptions, AAlevel, "[off]", "low", "medium", "high", command = SetAAlevel).grid(row = 3, column = 1, sticky = W+E) # TODO change to Off, Low, Med, Hi

        Label(GenOptions, text = "Snapshot file format").grid(row = 4, column=0, sticky = W+E)
        OptionMenu(GenOptions, SnapshotFormat,  "jpg", "png", "tif").grid(row = 4, column = 1, sticky = W+E)
        #SnapshotFormat = StringVar(value = 'jpg')
  


        #gen_options.grid(row = 5, column = 0, padx = 5, pady = 5, sticky = W+E)

        vis_book.setnaturalsize()
        vis_book.grid(row = 2, column = 0, columnspan = 4, rowspan = 2, stick = N+W+S+E)
    
        # bird's view : points
        # labels (come out with a interaction-based color style?)
    
        Button(VisOptionsWin, text = "Close", command = lambda : VisOptionsWin.destroy(), height = 2).grid(row = 9 , column = 0, columnspan = 3, padx = 5, pady = 5, sticky = E+W)



def CenterView():
    return

def SetAAlevel(event = None):
    aa_levels = { "[off]" : 0,
                  "low"   : 2,
                  "medium": 4,
                  "high"  : 8}
    if DEBUG:
        print "SetAAlevel> antialias :", AAlevel.get()
    mv.setAntialiasing( aa_levels[ AAlevel.get()] )
    return

def MapOptions():
	# temporary variable
    # TODO create 10 map buttons and use the voodoo magic to transform a [+] button to a full set of buttons and sliders
	Map1Style = StringVar(value = "Surface")
	Map1Color = StringVar(value = "#00ff00")
	Map2Style = StringVar(value = "Surface")
	Map2Color = StringVar(value = "#00ff00")

	global MapOptionsWin
	try:
		MapOptionsWin.deiconify()
		MapOptionsWin.lift()
	except:
		MapOptionsWin = Toplevel(master = root)
		MapOptionsWin.title("Grid maps visualization")
		MapOptionsWin.winfo_toplevel().resizable(NO,NO)
		MapsFrame = Pmw.Group(MapOptionsWin, tag_text = 'Maps')
		# TODO add here the dynamic code for populating the buttons
		Label(MapsFrame.interior(), text = "Probe").grid(row = 0, column = 0)
		Label(MapsFrame.interior(), text = "Isocontour value").grid(row = 0, column = 1)
		Label(MapsFrame.interior(), text = "Style").grid(row = 0, column = 2)
		Label(MapsFrame.interior(), text = "Color").grid(row = 0, column = 3)
		# separator
		#Frame(MapsFrame.interior(), height=2, bd=1, relief=SUNKEN).grid(row = 1, column = 0, sticky = E+W, columnspan = 9, padx = 10, pady = 15)

		# Map entry prototype
		MIN = -1.2; MAX = 0
		map1 = IntVar()
		map1_visibility = BooleanVar()
		Map1Name = Checkbutton(MapsFrame.interior(), text = "C", indicatoron = False, variable = map1_visibility)
		Map1Name.grid(row = 5, column = 0, padx = 5, sticky = E+W, ipadx = 20, ipady = 10)
		Map1Scale = Scale(MapsFrame.interior(), command = MapRepresentation, digits = 3, orient = HORIZONTAL, 
								repeatdelay = 100, resolution = 0.01, to = MAX, from_ = MIN, variable = map1, length = 250, tickinterval = MAX-MIN/2)
		Map1Scale.grid(row = 5, column = 1, padx = 3)
		Map1Style = OptionMenu(MapsFrame.interior(), Map1Style, "Surface", "Lines", "Points", command=MapRepresentation).grid(row = 5, column = 2, sticky = W+E)
		Map1ColorChoose = Button(MapsFrame.interior(), bg = Map1Color.get(), command = RecFlatcolorPicker, relief = RIDGE)
		Map1ColorChoose.grid(row = 5, column = 3)


		map2 = IntVar()
		map2_visibility = BooleanVar()
		Map2Name = Checkbutton(MapsFrame.interior(), text = "OA", indicatoron = False, variable = map2_visibility)
		Map2Name.grid(row = 6, column = 0, padx = 5, sticky = E+W, ipadx = 20, ipady = 10)
		Map2Scale = Scale(MapsFrame.interior(), command = MapRepresentation, digits = 3, orient = HORIZONTAL, 
								repeatdelay = 100, resolution = 0.01, to = MAX, from_ = MIN, variable = map2, length = 250, tickinterval = MAX-MIN/2)
		Map2Scale.grid(row = 6, column = 1, padx = 3)
		Map2Style = OptionMenu(MapsFrame.interior(), Map1Style, "Surface", "Lines", "Points", command=MapRepresentation).grid(row = 6, column = 2, sticky = W+E)
		Map2ColorChoose = Button(MapsFrame.interior(), bg = Map1Color.get(), command = RecFlatcolorPicker, relief = RIDGE)
		Map2ColorChoose.grid(row = 6, column = 3)


		MapsFrame.grid(row = 2, column = 0, sticky = W+E, padx = 10)
		MapsFrame.grid_propagate()
		
		Checkbutton(MapOptionsWin, text = "Show grid box").grid(row = 4, column = 0, padx = 10,pady = 3)



		Button(MapOptionsWin, text = "Close", command = lambda : MapOptionsWin.destroy(), width = 40, height = 2).grid(row = 9 , column = 0, columnspan = 2, padx = 5, pady = 5)



def MapColorPicker(event):
	"""
    set the custom color for the rest of 
	the receptor representations
    """
	color_output = tkColorChooser.askcolor(parent = VisOptionsWin, color = RecAllFlatColor.get())
	if color_output[0]:
		Map1color.set(color_output[1])
		event.widget.config(bg = Map1Color.get())
	return



def MapRepresentation(maptype):
	pass

def SaveCSV(file = None):
    if not FilteredLigands:
        return
    if not file:
        file = asksaveasfilename(parent = root, 
            title = "Select the CVS filename to save...", filetypes = [('CSV file', '*.csv'), ("Any file...", "*")],
            defaultextension=".csv")
    if not file:
        return
    labels = [["energy", "Energy", "%3.2f,"],
              ["ligand_efficiency", "ligand efficiency", "%3.2f,"],
              ["active_torsions", "active torsions", "%d,"],
              ["rmstol","RMS tolerance", "%3.2f,"], 
              ["runs", "Runs", "%d,"], 
              ["total_clusters","total cluster number", "%d,"],
              ["cluster_percent_size","% cluster size", "%3.2f,"],
              ["cluster_size", "poses in the cluster", "%d,"],
              ["e_range", "energy range", "%3.2f,"],      
              ["hb_count","hydrogen bond count", "%d,"],
              ["vdw_count","close atomic contacts", "%d"],
              ]
    output = []
    first_line = "#name,"
    for lab in labels:
        first_line += lab[1]+","
    output.append(first_line)
    for l in get_ligands():
        #print l
        info = get_ligand_info(l)
        line = l+","
        for lab in labels:
            #print lab[2], lab[0]
            line += lab[2] % info[lab[0]]
        output.append(line)
    SAVE = open(file, 'w')
    for o in output:
        print >>SAVE, o
    SAVE.close()
    return


def ExportMenu(parent = None, dir = None):
    """
    Implement two different styles of report:
        brief: two columns of ligands in a table similar to molecules from Theresa Tiefenbrun...
        I.e. energy, efficiency

        complete: the all whistle-and-bells
    """

    if parent == None:
        return

    def MoreLessOptions(type, value):
        if value == 0:
            if type == 'docking':
                ExportDockingFrameCONTAINER.grid_forget()
                ExportDockingOptionsButton.config(text = 'More options>>', command = lambda: MoreLessOptions('docking', 1) )
            if type == 'report':
                ExportReportFrameCONTAINER.grid_forget()
                ExportReportOptionsButton.config(text = 'More options>>', command = lambda: MoreLessOptions('report', 1) )
                pass
            if type == 'list':
                ExportListFrameCONTAINER.grid_forget()
                ExportListOptionsButton.config(text = 'More options>>', command = lambda: MoreLessOptions('list', 1) )

        if value == 1:
            if type == 'docking':
                ExportDockingFrameCONTAINER.grid(row = 4, column = 0, columnspan = 5)
                ExportDockingOptionsButton.config(text = 'Less options<<', command = lambda: MoreLessOptions('docking', 0) )
            if type == 'report':
                ExportReportFrameCONTAINER.grid(row = 4, column = 0, columnspan = 5)
                ExportReportOptionsButton.config(text = 'Less options<<', command = lambda: MoreLessOptions('report', 0) )
            if type == 'list':
                ExportListFrameCONTAINER.grid(row = 4, column = 0, columnspan = 5)
                ExportListOptionsButton.config(text = 'Less options<<', command = lambda: MoreLessOptions('list', 0) )



    Label(parent, text = "Ligands set").grid(row = 6, column = 0, sticky = E, padx = 1)
    OptionMenu(parent, ExportLevel, "selected only", "filtered").grid(row = 6, column = 1, sticky = W, padx = 1)



    Frame1 = Pmw.Group(parent, tag_text = "Docking files", tag_pyclass = Checkbutton, tag_variable =  ExportDockings)

    Label(Frame1.interior(), text = 'Format:').grid(row = 1, column = 0, sticky = E)
    OptionMenu(Frame1.interior(), ExportStructureFormat, 'PDBQT', 'PDB').grid(row = 1, column = 1, sticky = W) 
    ExportDockingOptionsButton = Button(Frame1.interior(), text = "Options>>", command = lambda: MoreLessOptions('docking', 0) )
    #Label(Frame1.interior(), text = " ").grid(row = 2, column = 0)
    ExportDockingOptionsButton.grid(row = 1, column = 2, sticky = W, columnspan = 2)
    Label(Frame1.interior(), text = " ").grid(row = 2, column = 0)
    Button(Frame1.interior(), text = "Save", command = lambda: StartExport('docking') ).grid(row = 10, column = 3, sticky = E)

    ExportDockingFrameCONTAINER = Frame(Frame1.interior())
    Label(ExportDockingFrameCONTAINER, text = "   Save ligand poses +").grid(row = 3, column = 0, sticky = W)
    Checkbutton(ExportDockingFrameCONTAINER, text = "receptor PDBQT", variable = ExportRec).grid(row = 4, column = 0, sticky = W, padx = 25)
    Checkbutton(ExportDockingFrameCONTAINER, text = "grid box", variable = ExportBox).grid(row = 5, column = 0, sticky = W, padx = 25)
    Checkbutton(ExportDockingFrameCONTAINER, text = "parameter files (DPF, GPF)", variable = ExportParm).grid(row = 6, column = 0 , sticky = W, padx = 25)
    Checkbutton(ExportDockingFrameCONTAINER, text = "map files", variable = ExportMap).grid(row = 7, column = 0, sticky = W, padx = 25)

    ExportDockingFrameCONTAINER.grid(row = 0, column = 0)

    Frame1.grid(row = 9, column = 0, sticky = W+E+N+S, padx = 3, ipadx = 10, ipady = 10, columnspan = 2)
    ExportDockingOptionsButton.invoke()




    Frame3 =Pmw.Group(parent, tag_text = 'Ligand list', tag_pyclass = Checkbutton, tag_variable = ExportLigList)

    Label(Frame3.interior(), text = "Format:").grid(row = 5, column = 0, sticky = W, columnspan = 1, ipadx = 10)
    list_options = OptionMenu(Frame3.interior(), ExportListFormat, "CSV", "name list only")
    list_options.grid(row = 5, column = 1, sticky = W)
    Label(Frame3.interior(), text = "   ").grid(row = 5, column = 2)

    #ExportListFrameCONTAINER = Frame(Frame3.interior())
    #Label(ExportListFrameCONTAINER, text = "Format:").grid(row = 5, column = 0, sticky = W, columnspan = 1, ipadx = 10)
    #list_options = OptionMenu(ExportListFrameCONTAINER, ExportListFormat, "CSV", "name list only")
    #list_options.grid(row = 5, column = 1, sticky = W)
    #Label(ExportListFrameCONTAINER, text = "                       ").grid(row = 5, column = 3)
    #ExportListFrameCONTAINER.grid(row =0, column =  0, sticky = W+E)

    Frame3.grid(row = 10, column = 0, sticky = W+E, padx = 3, ipadx = 10, ipady = 10, columnspan = 2)

    #ExportListOptionsButton = Button(Frame3.interior(), text = "Options>>", command = lambda: MoreLessOptions('list', 0) )
    Button(Frame3.interior(), text = "Save", command = lambda: StartExport('list') ).grid(row = 7, column = 3)
    #ExportListOptionsButton.grid(row = 10, column = 3, sticky = E)
    #ExportListOptionsButton.invoke()

    Frame2 = Pmw.Group(parent, tag_text = "Report", tag_pyclass = Checkbutton, tag_variable = ExportReport)
    Label(Frame2.interior(), text = "Format:").grid(row = 0, column = 0, sticky = W, columnspan = 1)
    OptionMenu(Frame2.interior(), ExportReportFormat, "PDF", "HTML").grid(row = 0, column = 1, sticky = W)

    ExportReportFrameCONTAINER = Frame(Frame2.interior())
    #Label(ExportReportFrameCONTAINER, text = "Format:").grid(row = 0, column = 0, sticky = W, columnspan = 1)
    #OptionMenu(ExportReportFrameCONTAINER, ExportReportFormat, "PDF", "HTML").grid(row = 0, column = 1, sticky = W)
    Label(ExportReportFrameCONTAINER, text = "Include:").grid(row = 0, column = 1, sticky = W)
    Checkbutton(ExportReportFrameCONTAINER, text = "2D structures", variable = Export2Dpic).grid(row = 1, column = 1, sticky = W, padx = 10)
    Checkbutton(ExportReportFrameCONTAINER, text = "3D viewer snapshots", variable = Export3Dpic).grid(row = 2, column = 1, sticky = W, padx = 10)
    Checkbutton(ExportReportFrameCONTAINER, text = "notes", variable = ExportNotes).grid(row = 3, column = 1, sticky = W, padx = 10)

    Frame2.grid(row = 11, column = 0, sticky = W+E,  padx = 3, ipadx = 10, ipady = 10, columnspan = 2)

    ExportReportOptionsButton = Button(Frame2.interior(), text = "Options>>", command = lambda: MoreLessOptions('report', 0) )
    Label(Frame2.interior(), text = "   ").grid(row = 1, column = 2)
    Button(Frame2.interior(), text = "Save", command = lambda: StartExport('report') ).grid(row = 10, column = 2,sticky = E)
    ExportReportOptionsButton.grid(row = 0, column = 2, sticky = W)
    ExportReportOptionsButton.invoke()

    ExportMainButton = Button(parent, text = "Generate full report", command = StartExport, height = 2)
    ExportMainButton.grid(row = 20, column = 0, sticky = E+W+N+S, padx = 5, pady = 5, columnspan = 2)


def get_ligands():
    """
    Retrieve the list of ligand names from the currently specified set (selected/all)

    """
    if not FilteredLigands:
        return False
    if ExportLevel.get() == 'selected only':
        return filter( lambda l: LigBook[l]['selected'], FilteredLigands)
    else:
        return FilteredLigands


def SaveLigandList(file = None):
    if not file:
        file = asksaveasfilename(parent = root, 
            title = "Select the ligand list filename to save...", filetypes = [('Text file', '*.txt'), ("Any file...", "*")],
            defaultextension=".txt")
        if not file:
            return
    list = get_ligands()
    print "got these ligands", list
    try:
        output = open(file, 'w')
        for l in list:
            print >> output, l #+"\n"
        output.close()
        return True
    except:
        if DEBUG: print "GenerateList> error in saving the file %s" % file
        showerror("Export data", ('Error in generating the list file\nBe sure the curreng user has permissions to\
        access this path and enough disk space is available'))
        return False


def StartExport(target = None):

    def GenDir(DIR):
        try:
            os.makedirs(DIR, 0755)
            return DIR
        except:
            showerror("Output directory", ('An error occurred when creating the directory:\n\n%s\n\nBe sure the curreng user\
            has permissions to access this path and enough disk space is available' % DIR))
            print "GenDir> error in creating the directory " % DIR
            return False

    def AskOutputDir():
        DIR = askdirectory()
        if DIR:
            try:
                if os.path.exists(DIR):
                    if len(glob(os.path.join(DIR, "*"))):
                        showerror("Output directory", 'The selected directory is not empty:\n\n - specify another directory\n - type in a new name to create one.' )
                        return False

                else:
                    if askokcancel('Output directory','The selected directory doesn\'t exist.\nDo you want to create it?'):
                        if GenDir(DIR):
                            return DIR
                    return False
            except:
                showerror("Output directory", ('Error reading directory:\n\n%s\n\nBe sure the curreng user has permissions to\
                            access this path' % DIR))
                if DEBUG: print "AskOutputDir> error in reading the directory %s " % DIR
                return False
        else:
            return False

    def GenerateExportDockings(DIR):
        if ExportBox.get():
            # get the gridBox filename
            pass
        if ExportParm.get():
            gpf = gen_gpf_from_grid_info()
        if ExportMap.get():
            mapfiles_list = getMapFilenames()

        format = ExportStructureFormat.get() # PDBQT, PDB
        if format == "PDB":
            try:
                pdb_writer
            except:
                pdb_writer = PdbWriter()

        for l in get_ligands():
            if DEBUG: print "\tcopying the file", l
            if format == "PDBQT":
                try:
                    shutil.copy2(get_current_pose(l), DOCKING_DIR)
                except:
                    if DEBUG: print "ExportMenu> error copying the ligand [PDBQT] :", get_current_pose(l)
                    showerror("Export data", ('Error in copying the ligand PDBQT\nBe sure the curreng user has permissions to\
                    access this path and enough disk space is available'))
                    return False
            elif format == "PDB":
                try:
                    file_org = get_current_pose(l)
                    mol = Read(file_org)[0]
                    mol.buildBondsByDistance()
                    mol.allAtoms.number = range(1, len(mol.allAtoms)+1)
                    name = os.path.basename(file_org)
                    name = DOCKING_DIR + os.sep + os.path.splitext(name)[0] + ".pdb"
                    pdb_writer.write(name, mol.allAtoms, records =['ATOM', 'HETATM', 'USER', 'REMARK'])
                except:
                    if DEBUG: print "ExportMenu> error saving the ligand [PDB] :", get_current_pose(l)
                    showerror("Export data", ('Error in saving the ligand PDB\nBe sure the curreng user has permissions to\
                    access this path and enough disk space is available'))
                    return False


        # receptor
        if ExportRec.get() and ReceptorFilename.get():
            if DEBUG: print "ExportMenu> copying receptor..."
            if format == "PDBQT":
                try:
                    shutil.copy2(ReceptorFilename.get(), DOCKING_DIR)
                except:
                    if DEBUG: print "ExportMenu> error copying the receptor:", ReceptorFilename.get()
                    showerror("Export data", ('Error in copying the receptor file\nBe sure the curreng user has permissions to\
                    access this path and enough disk space is available'))
                    return False
            elif format == "PDB":
                try:
                    file_org = ReceptorFilename.get()
                    mol = Read(file_org)[0]
                    mol.buildBondsByDistance()
                    mol.allAtoms.number = range(1, len(mol.allAtoms)+1)
                    name = os.path.basename(file_org)
                    name = DOCKING_DIR + os.sep + os.path.splitext(name)[0] + ".pdb"
                    pdb_writer.write(name, mol.allAtoms, records =['ATOM', 'HETATM', 'USER', 'REMARK'])
                except:
                    if DEBUG: print "ExportMenu> error saving the receptor [PDB] :", get_current_pose(l)
                    showerror("Export data", ('Error in saving the receptor PDB\nBe sure the curreng user has permissions to\
                    access this path and enough disk space is available'))
                    return False
        else:
            if DEBUG: print "ExportMenu> no receptor!!!! \n\n\n"
            pass

        # grid box PDB
        if ExportBox.get() and GPFpdbFilename.get():
            print "ExportMenu> copying Grid Box (PDB)..."
            try:
                shutil.copy2(GPFpdbFilename.get(), DOCKING_DIR)
            except:
                if DEBUG: print "ExportMenu> error copying the receptor:", GPFpdbFilename.get()
                showerror("Export data", ('Error in copying the receptor file\nBe sure the curreng user has permissions\
                to access this path and enough disk space is available'))
                return False
            #RecBoxFilename.set(rec_in_the_box)
        else:
            if DEBUG: print "ExportMenu> no grid box is present"

    def gen_gpf_from_grid_info(file = None):
        pass

    def getMapFilenames():
        print "gridMapFilenames> not implemented yet"
        pass


    """
    Include the following info:

        INPUT
        ----------------------------
        LigandInputInfo
        Grid parms data
        Receptor name
        DPF data? (from the first ligand?)





        PROCESS
        ----------------------------
        Filters
        Energy Profile
        Survival percentages
        Best
        Worst energy


        SELECTED LIGANDS
        ----------------------------
        Snapshot
        Comments

    """

    if not get_ligands():
        showwarning("Export results", 'No ligands have been selected.\n\nTo save all the filtered ligands, change the setting of "Ligands set" or select at least a ligand')
        return False

    if not target:
        DIR = AskOutputDir()
        if not DIR:
            return
        if ExportDockings.get():
            DOCKING_DIR = GenDir(DIR+os.sep+"dockings")
            if DOCKING_DIR:
                GenerateExportDockings(DOCKING_DIR)

        if ExportLigList.get():
            if ExportListFormat.get() == "CSV":
                SaveCSV(DIR+os.sep+"ligand_list.csv")
            else:
                SaveLigandList(DIR+os.sep+"ligand_list.txt")

        if ExportReport.get():
            if ExportReportFormat.get() == "PDF":
                #print "PDF"
                GenerateReportPDF(DIR+os.sep+"report.pdf")
            if ExportReportFormat.get() == "HTML":
                #print "HTML"
                GenerateReportHTML(DIR+os.sep+"report.html")
        return

    if target == "docking":
        DOCKING_DIR = AskOutputDir()
        if DOCKING_DIR:
           GenerateExportDockings(DOCKING_DIR)
        return

    if target == "list":
        print "exportliglist"
        if ExportListFormat.get() == "CSV":
            SaveCSV()
        else:
            SaveLigandList()
        return

    if target == "report":
        if ExportReportFormat.get() == "PDF":
            GenerateReportPDF()
        if ExportReportFormat.get() == "HTML":
            #print "HTML"
            DIR = AskOutputDir()
            if DIR:
                GenerateReportHTML(DIR)
        return

def GenerateReportPDF(dir = None):
    pass


def GenerateReportHTML(DIR):
    """
    Format:
        column1 : ligand name
        column2 : properties
        column3 : 2D/3D pictures [optional]

    """

    def get_ligand_image(ligand, type = "3D"):
        if type == "3D":
            try:
                return snapshot_list[ligand]
            except:
                return False

        if type == "2D":
            print "getting 2D image [FAKE]" 
            # use the vs_temp variable
            return "/entropia/scripts/coati/example.jpg"

    if DEBUG: print "GenerateReportHTML> report generation on dir", DIR
    output_FILE = DIR+os.sep+"report.html"



    ExportNotes.get() # !!!! TODO

    # calculate dynamically
    width = "50" # percentage
    cell_count = 2
    if Export3Dpic.get() or ExportNotes.get():
        cell_count = 3

    if cell_count == 2:
        width = "50%"
    if cell_count == 3:
        width = "33%"
        width = "50%"


    OUTPUT = ""
    header='<html>\n<body>\n<TABLE WIDTH=100% BORDER=1 BORDERCOLOR="#000000" CELLPADDING=3 CELLSPACING=0><COL WIDTH=128*><COL WIDTH=128*>\n'
    header+= "<tr> <th>LIGAND NAME</th> <th>RESULTS DATA</th>"
    if Export3Dpic.get():
        header+= "<th>DOCKING VIEW</th>"
    #elif ExportNotes.get():
    #    header+= "<th>NOTES</th>"
    #else Export3Dpic.get() and ExportNotes.get():
    #    header+= "<th>DOCKING VIEW AND NOTES</th>"
        

    header+="</tr>\n"

    row_BEGIN='<TR VALIGN=TOP>\n'
       
    cell = '    <TD WIDTH=%s><P>%s</P></TD>\n'
    ligand_name = "<b><h1> %s </h1></b></br>\n"

    image2D_height = " HEIGHT=200 "
    image2D_width =  " WIDTH=240 "

    image3D_height = " HEIGHT=400 "
    image3D_width =  " WIDTH=240 "

    image = '<IMG SRC="%s" ALIGN=CENTER VALIGN=CENTER %s %s BORDER=0><BR></P>\n'  # filename, image_width, image_height

    spacer = '<tr><td><br></td></tr>\n'
    row_END  ='\n</TR>\n'
    OUTPUT += header+"\n"

    images_dir_name = "images_html" 
    images_dir = DIR+os.sep+images_dir_name
    try:
        os.makedirs(images_dir, 0755)
    except:
        print "problems in generating the images directory"
        return False

    # TODO 
    # add HERE all the data about the criteria
   
    for l in get_ligands():

        OUTPUT += row_BEGIN

        # cell 1
        current_ligand = ligand_name % l
        
        if Export2Dpic.get():
            file = get_ligand_image(l, type = "2D")
            filename = name = os.path.basename(file)
            try:
                shutil.copy2(file, images_dir)
            except:
                showerror("Export data HTML", ('Error in copying the 3D image\nBe sure the curreng user has permissions\
                to access this path and enough disk space is available'))
                return False
            image2D = image % (images_dir_name+"/"+filename, image2D_height, "") 
            current_ligand += image2D # add the 2D image to the ligand name

        current_row = cell % (width, current_ligand) # initialize the current row with the first cell
        # cell 2
        info = get_ligand_info(l)
        current_ligand_info = '<BR><code><table border ="0"'

        current_ligand_info += '<tr>\n'
        current_ligand_info += '    <td><b>Energy</b></td>\n'
        current_ligand_info += '    <td>%3.2f <small><sup>kcal</sup>/<sub>mol<sub></small></td>\n' % info['energy']
        current_ligand_info += '</tr>\n'

        current_ligand_info += '<tr>\n'
        current_ligand_info += '    <td>ligand efficiency</td>\n'
        current_ligand_info += '    <td>%3.2f</td>\n' % (info['ligand_efficiency'])
        current_ligand_info += '</tr>\n'

        current_ligand_info += '<tr>\n'
        current_ligand_info += '    <td>Active torsions</td>\n'
        current_ligand_info += '    <td>%d</td>\n' % (info['active_torsions'])
        current_ligand_info += '</tr>\n'

        current_ligand_info += spacer

        current_ligand_info += '<tr>\n'
        current_ligand_info += '    <td colspan="2"><b>Clustering </b>&nbsp %d runs @ %2.2f A RMSD</td>\n' % (info['runs'], info['rmstol'] )
        current_ligand_info += '</tr>\n'

        current_ligand_info += '<tr>\n'
        current_ligand_info += '    <td>&nbsp cluster size [poses] </td>\n'
        current_ligand_info += '    <td> %2.2f%% [%d]</td>' % (info['cluster_percent_size'], info['cluster_size'])
        current_ligand_info += '</tr>\n'

        current_ligand_info += '<tr>\n'
        current_ligand_info += '    <td>&nbsp energy range</td>\n'
        current_ligand_info += '    <td>%2.2f</td>' % (info['e_range'])
        current_ligand_info += '</tr>\n'

        current_ligand_info += '<tr>\n'
        current_ligand_info += '    <td>&nbsp number of clusters</td>\n'
        current_ligand_info += '    <td>%d</td>' % (info['total_clusters'])
        current_ligand_info += '</tr>\n'

        """
        current_ligand_info += '<tr>\n'
        current_ligand_info += '    <td><b>   </b></td>\n'
        current_ligand_info += '    <td>%d<BR></td>' % (info[''])
        current_ligand_info += '</tr>\n'
        """

        current_ligand_info += spacer

        current_ligand_info += '<BR><tr>\n'
        current_ligand_info += '    <td><b>Hydrogen bonds  </b></td>\n'
        current_ligand_info += '    <td>%d</td>\n' % (info['hb_count'])
        current_ligand_info += '</tr>\n'


        current_ligand_info += '<tr>\n'
        current_ligand_info += '    <td><b>vdW contacts</b></td>\n'
        current_ligand_info += '    <td>%d</td>\n' % (info['vdw_count'])
        current_ligand_info += '</tr>\n'


        current_ligand_info +='</table></code>'




        if ExportNotes.get() and not len(NotesList) == 0:
            note_line = ""
            try:
                #note = NotesList[current_ligand[0]] 
                #FAKE!"
                note = "test\ntext of description of a given ligand whenever it takes\nALOHA"
                note = note.replace("\n", "<BR>")
                note_line += "<BR><BR><small><b>Notes:</b><BR>"+note+"</small>"
            except:
                cell_3 += "<BR><small> </small>"
                current_row += cell % (width, (" "))
            current_ligand_info += note_line




        current_row += cell % (width, current_ligand_info)

        # cell 3 (optional)
        if Export3Dpic.get() or ExportNotes.get():
            cell_3 = ""
            if Export3Dpic.get():
                file = get_ligand_image(l, type = "3D")
                if file:
                    filename = os.path.basename(file)
                    try:
                        shutil.copy2(file, images_dir)
                    except:
                        showerror("Export data HTML", ('Error in copying the 3D image\nBe sure the curreng user has permissions\
                        to access this path and enough disk space is available'))
                        return False
                    #image3D = image % (images_dir_name+"/"+filename, image3D_height, "")
                    #current_row += cell % (width, image3D)
                    cell_3 += image % (images_dir_name+"/"+filename, image3D_height, "")
                else:
                    cell_3 += "<BR><BR>[ NO PICTURE ]<BR><BR>"
                    #current_row += cell % (width, " [ NO PICTURE ]")
        current_row += cell % (width, cell_3)

                

        OUTPUT += current_row+row_END+"\n"

    OUTPUT += '</body></html>'

    try:
        file = open(output_FILE, 'w')
        print >> file, OUTPUT
        file.close()
        return True
    except:
        showerror("Export data HTML", ('Error in saving the output file:\n%s\n\nBe sure the curreng user has permissions\
        to access this path and enough disk space is available' % output_FILE))
        if DEBUG: print "GenerateReportHTML> Problems in saving he file %s ", output_FILE
        return False










def SetReferenceLigand(hide_only = False):
    global ReferenceLigand
    global visible
    reference_filename = None
    RefLigandButton.config(relief=RAISED)

    # get the name if present
    if ReferenceLigand:
        #print "LOOKING FOR THE NAME"
        idx = mv.Mols.index(ReferenceLigand)
        name = mv.Mols[idx].name
        #print "REFERENCE", idx, name

    if hide_only:
        #print "SetReferenceLigand> show_hide ligand" 
        #idx = mv.Mols.index(ReferenceLigand)
        #name = mv.Mols[idx].name
        try:
            if visible:
                mv.showMolecules([name], negate = True, log = 0)
                visible = False
                if DEBUG: print "HIDE"
                RefLigandButton.config(text='Show')
            else:
                mv.showMolecules([name], negate = False, log = 0)
                #RefLigandButton.config(relief=RAISED)
                RefLigandButton.config(text=' Hide ')
                visible = True
                if DEBUG: print "SHOW"
        except:
            return
            
        RefLigandButton.config(relief=RAISED)
        return True
    else:
        #print "needs a reference"
        reference_filename = askopenfilename(parent = root, title = "Select the ligand reference structure...", filetypes = [("Ligand PDBQT", "*.pdbqt"), ("Any file", "*")])
        if not reference_filename:
            RefLigandButton.config(relief=RAISED)
            return False
        else:
            lines = get_lines(reference_filename)
            c = 0
            for l in lines:
                if "ATOM" in l or "HETATM" in l:
                   c += 1 
            if DEBUG: print "SetReferenceLigand> size of the reference ligand:", c
            if c > 100: # arbitrary atom count
                if not askyesno(title ="Reference ligand", message = "The file seems to be too big to be a ligand.\n\nContinue importing?"):
                    return False
                
    if ReferenceLigand:
        #print "I would delete", name
        if DEBUG: print "ReferenceLigand> I would delete this", ReferenceLigand
        mv.deleteMol(name, log = 0)       
        #print "delete reference"

    ReferenceLigand = mv.readMolecule(reference_filename, "reference_ligand", log = 0)[0]
    idx = mv.Mols.index(ReferenceLigand)
    name = mv.Mols[idx].name
    mv.colorAtomsUsingDG(name, ['sticks', 'lines', 'balls', 'MSMS-MOL', 'cpk'], log=0)
    visible = True
    RefLigandButton.config(text=' Hide ')
    RefLigandButton.config(relief=RAISED)

    cam = vi.cameras[1]
    cam.SelectCamera()
    cam.tk.call(cam._w, 'makecurrent') 
    cam.focus_set()
    """
    this function should do
    - load on demand (first time, RMB)
    - show/hide (LMB)
    """
    # bound to RefLigandButton
    #print " SAVED", ReferenceLigand
    return


#######################################################################
# VIEWER page ########################################################
LigandListGroup = Frame(Tab3)

Tab3.grid_rowconfigure(1, weight = 1)
Tab3.grid_columnconfigure(0, weight = 1)

LigandListGroup.grid(row = 1, column = 0, sticky = E+W+N+S)

LigandListGroup.grid_columnconfigure(3, weight = 1)
LigandListGroup.grid_rowconfigure(0, weight = 1)

# 2D viewer =============================== ROW 0
"""
viewer2Dframe = Pmw.Group(LigandListGroup, tag_text = "2D structure")

#widget = viewer2Dframe.component('hull')
#Pmw.Color.changecolor(widget, background = 'white')
ligand_picture = Canvas(viewer2Dframe.interior(), height = 150, width = 250, bg = "#ffffff")
image = Image.open("/entropia/scripts/coati/examples/example.png")
photo = ImageTk.PhotoImage(image)
item = ligand_picture.create_image(10,10, anchor = NW, image=photo)
ligand_picture.grid(row = 1, column = 0, columnspan = 3, sticky = W+E)

viewer2Dframe.grid(row = 0, column = 0, sticky = N) #  TODO disabled so far...
"""

def find_name(pose):
    """
    Returns the ligand name as registered in the Great Book of Ligands for the given pose
    """
    if DEBUG: print "find_name> got request for ", pose
    try:
        return [NAME for NAME in LigBook.keys() if get_current_pose(NAME) == pose][0]
    except:
        return False

def UpdateLigandInfo(ligand_filename = None):
    global Results_infotext
    global SwitchLEradio 
    global SwitchLCradio


    #TODO Add the ShowHistogram button?
    #TODO add the full clustering info? (the text entry is scrollable)

    if ligand_filename:
        if DEBUG: print "UpdateLigandInfo> updating ligand data [ %s ]" % ligand_filename

        # TODO put here the function to get the ligand info...
        ligand_info = get_ligand_info(ligand_filename)

        #def find_name(pose):
        #    return [NAME for NAME in LigBook.keys() if get_current_pose(NAME) == pose][0]

        name = find_name(ligand_filename)

        LigandName.set(name) #+("   [ %d active tors]" % tors))
        text = "Energy\t\t%2.2f\n" % ligand_info['energy']
        text += "Ligand efficiency\t%2.2f\n" % ligand_info['ligand_efficiency']
        text += "Active torsions\t%2d\n" % ligand_info['active_torsions']
        text += "Clustering [ %d runs @ %2.2f A tolerance]\n" % (ligand_info['runs'], ligand_info['rmstol'])
        text += "    # clusters\t%d\n" % ligand_info['total_clusters']
        text += "    cluster size\t%3.2f %s\t[ %d ]\n" % (ligand_info['cluster_percent_size'], "%", ligand_info['cluster_size'])
        text += "    E_range\t%2.2f Kcal/mol\n" % ligand_info['e_range']
        text += "Hydrogen bonds\t%d\n" % ligand_info['hb_count']
        text += "vdW contacts\t%d" % ligand_info['vdw_count']
        Results_infotext.config(foreground = 'black')


        # let's start tagging...
        bold_words = ['Active torsions',
                      'Energy',
                      'Ligand efficiency',
                      'Clustering ',
                      'Hydrogen bonds',
                      'vdW contacts']
        italic_words = [ '# clusters',
                         'cluster size',
                         'E_range']
        for word in bold_words:
            idx = '1.0'
            while 1:
                idx = Results_infotext.search(word, idx, stopindex = END)
                if not idx : break
                last_idx = '%s+%dc' % (idx, len(word))
                if idx.split('.')[1] == "0":
                    Results_infotext.tag_add('boldy', idx, last_idx)
                idx = last_idx
            Results_infotext.tag_config('boldy', font = ('helvetica', 9, 'bold'))

        for word in italic_words:
            idx = '1.0'
            while 1:
                idx = Results_infotext.search(word, idx, stopindex = END)
                if not idx : break
                last_idx = '%s+%dc' % (idx, len(word))
                if idx.split('.')[1] == "0":
                    Results_infotext.tag_add('cursive', idx, last_idx)
                idx = last_idx
            Results_infotext.tag_config('cursive', font = ('helvetica', 9, 'italic'))

        #SwitchLEradio.config(state = NORMAL)
        #SwitchLCradio.config(state = NORMAL)



    else:
        if DEBUG: print "UpdateLigandInfo> clearing ligand data"
        LigandName.set('')
        """
        text = "Energy\n" 
        text += "Ligand efficiency\n" 
        text += "Active torsions\n" 
        text += "Clustering \n" 
        text += "    # clusters\n" 
        text += "    cluster size\n"
        text += "    E_rangen"
        text += "Hydrogen bonds\n" 
        text += "vdW contacts" """
        text = "\n\n\n\n\n\n\n\n\n"
        Results_infotext.config(foreground = 'gray')
        #SwitchLEradio.config(state = DISABLED)
        #SwitchLCradio.config(state = DISABLED)


    Results_infotext.config(state = NORMAL)
    Results_infotext.delete(1.0,END)
    #print "Text = ", text
    Results_infotext.insert(END, text)
    Results_infotext.config(state = DISABLED)





    #HistogramButton = Button(Results_infotext, text = 'Show histogram')
    #Results_infotext.window_create(END, window = HistogramButton)


    return

def TagThis(textwidget, bold_words):
    pass






#Infobar = LabelFrame(LigandListGroup, labelwidget = LigandName)
Infobar = Pmw.Group(LigandListGroup,  tag_textvariable = LigandName)

"""
# 2D picture of the ligand
ligand_picture = Canvas(Infobar.interior(), height = 150, width = 250, bg = "#ffffff")
image = Image.open("/entropia/scripts/coati/examples/example.png")
photo = ImageTk.PhotoImage(image)
#item = ligand_picture.create_image(10,10, anchor = NW, image=photo)
ligand_picture.grid(row = 0, column = 0, columnspan = 1, sticky = W+E)"""

# statistics and general ligand data
Results_infotext = Text(Infobar.interior(), height=10, width=40, relief = FLAT, font = 'helvetica 9')
Results_infotext.grid(row = 1, column = 0,sticky = W+N)
# TODO disabled feature
#AlternateLigPoses = Frame(Infobar.interior())
#SwitchLEradio = Radiobutton(AlternateLigPoses, text = "Lowest Energy", value = 0, command = lambda: LoadLigand(force_pose = "le") )
#SwitchLCradio = Radiobutton(AlternateLigPoses, text = "Largest Cluster", value = 1, command = lambda: LoadLigand(force_pose = "lc") )
#SwitchLEradio.grid(row = 9, column = 0, sticky = E)
#SwitchLCradio.grid(row = 9, column = 1, sticky = W)
#AlternateLigPoses.grid(row = 9, column = 0, sticky = W+E)

Infobar.grid(row = 0, column = 0, columnspan = 2, sticky = W+E+N)


# Ligand list labels =============================== ROW 1
ligand_picker_frame = Frame(LigandListGroup)

Label(ligand_picker_frame, text = "Select").grid(row = 1,      column = 0, columnspan = 1,sticky = W)
ResLigandLabel = Label(ligand_picker_frame, text = "Ligand")
ResLigandLabel.grid(row = 1, column = 1, columnspan = 1, sticky  = W)
ResLigandLabel.bind('<Return>', lambda  : NextLigand("+"))
Label(ligand_picker_frame, text = "       E").grid(row = 1, column = 2, columnspan = 1, sticky = W)
Label(ligand_picker_frame, text = "L.eff.").grid(row = 1, column = 3, columnspan = 1, sticky = W)
Label(ligand_picker_frame, text = "Tors").grid(row = 1, column = 4, columnspan = 1 , sticky = W) # TODO transform it as a pull-down?
Label(ligand_picker_frame, text = "                ").grid(row = 1, column = 5, columnspan = 1 , sticky = W+E)

ligand_picker_frame.grid(row = 2, column = 0, sticky = N+W)
ligand_picker_frame.grid_columnconfigure(80, weight = 1)


def NextLigand(increment):
    print "loading another ligand"
    if not current_ligand or not FilteredLigands:
        return
    idx = FilteredLigands.index(current_ligand[0])
    if increment == "+":
        idx += 1
    if increment == "-":
        idx -= 1
    if idx < len(FilteredLigands) or idx > len(FilteredLigands):
        return
    LoadLigand( FilteredLigands[idx] )



##############################################################
# Scrolled list of results
ResultScrolledFrame = Text(ligand_picker_frame, width = 42)# , relief = FLAT)
ResultScroll = Scrollbar(ligand_picker_frame, command = ResultScrolledFrame.yview)
ResultScroll.grid(row = 80, column = 5, columnspan = 1, sticky = N+S+W+S)
ResultScrolledFrame.configure(yscrollcommand = ResultScroll.set)
ResultScrolledFrame.grid(row = 80, column = 0, columnspan = 5, sticky = N+S+E+W)
ResultScrolledFrame.grid_rowconfigure(80, weight = 1)
ResultScrolledFrame.bind('<Up>', lambda x : NextLigand("+") )
ResultScrolledFrame.bind('<Down>', lambda x: NextLigand("-") )
ResultScrolledFrame.bind('<Return>', lambda x: NextLigand("-") )



# selected label
CountSelLigands = StringVar(value = "Selected ligands :\t")
Label(LigandListGroup, textvar = CountSelLigands).grid(row = 11, column = 0)
SelectionFrame = Frame(LigandListGroup)
Button(SelectionFrame, text = "Select all", command = lambda : ResultsSelection("all")).grid(row = 90, column = 0, sticky = W+E)
Button(SelectionFrame, text = "Invert", command = lambda : ResultsSelection("invert")).grid(row = 90, column = 1, sticky = W+E)
Button(SelectionFrame, text = "Deselect all", command = lambda : ResultsSelection("none")).grid(row = 90, column = 2, sticky = W+E)
Button(SelectionFrame, text = "Show only", command = HideStickyLigands).grid(row = 90, column = 3, sticky =W+E)
#Button(SelectionFrame, text = "Hide all").grid(row = 90, column = 3, sticky = W+E)
SelectionFrame.grid(row = 10, column = 0, sticky = W+E+N)



def ResultsSelection(mode = None):
    if mode == "all":
        if askyesno(title ="Select results", message = "All the ligands are going to be selected.\n\nAre you sure?"):
            for l in FilteredLigands:
                LigBook[l]['selected'] = True
    if mode == "invert":
        for l in FilteredLigands:
            LigBook[l]['selected'] = not LigBook[l]['selected']
    if mode == "none":
        if askyesno(title ="Deselect results", message = "All the ligands are going to be de-selected.\n\nAre you sure?"):
            for l in FilteredLigands:
                LigBook[l]['selected'] = False
    UpdateButtons()
    UpdateSelected()
        


viewer3D = Pmw.Group(LigandListGroup, tag_text = "3D viewer") 


# 3D toolbar
Toolbar3D = Frame(viewer3D.interior())
#Toolbar3D = LabelFrame(viewer3D.interior(), text = "Show")

Centerbar = LabelFrame(Toolbar3D, text = "Center")


def Cheese():
    """
    SnapshotFormat = StringVar(value = 'jpg')
    Use the current ligand to get the filename to be saved...
    
    The file format is set in the VisOptions
    png,
    tiff
    jpeg
    eps

    """

    if not current_ligand:
        return False

    SNAPSHOT_DIR = TEMPDIR+os.sep+"snapshots"
    if not os.path.exists(SNAPSHOT_DIR):
        try:
            os.makedirs(SNAPSHOT_DIR, 0755)
        except:
            showerror("Snapshots directory", ('An error occurred when creating the directory:\n\n%s\n\nBe sure the curreng user\
            has permissions to access this path and enough disk space is available' % SNAPSHOT_DIR))
            if DEBUG: print "StartExport> error in creating the directory " % SNAPSHOT_DIR
            return False
   
    if DEBUG: print "Cheese> taking a picture of ", current_ligand[0]
    format = SnapshotFormat.get()
    filename  = SNAPSHOT_DIR+os.sep+current_ligand[0]+"."+format
    try:
        mv.saveImage(filename, 0, log=0)
        snapshot_list[current_ligand[0] ] = filename
    except:
        if DEBUG: print "Cheese> problems in exporting the picture!"
        showerror("Snapshots", ('An error occurred when saving the image\n %s \n' % filename))
        return False
    return True

Button(Centerbar, text = "Tgt", command = lambda: resetview('receptor')).grid(row = 0, column = 0, sticky = W+E) # center TARGET
Button(Centerbar, text = "Grd", command = lambda: resetview('grid box')).grid(row = 1, column = 0, sticky = W+E) # center BOX
Button(Centerbar, text = "Lig", command = lambda: resetview('ligand')).grid(row = 2, column = 0, sticky = W+E) # center LIGAND
Centerbar.grid(row = 1, column = 0, sticky = N)

Button(Toolbar3D, text = "Snap!", command = Cheese).grid(row = 3, column = 0, sticky = S, padx = 3) # Snapshot!
#Button(Toolbar3D, text = "Opt>>", command = VisOptions).grid(row = 4, column = 0, columnspan = 1, padx = 3)

RefLigandButton = Button(Toolbar3D, text = "Load")
RefLigandButton.grid(row = 5, column = 0, columnspan = 1, padx = 3, pady = 3)
RefLigandButton.bind('<Button-1>', lambda x: SetReferenceLigand() )
RefLigandButton.bind('<Button-3>', lambda x: SetReferenceLigand(hide_only = True))
#RefLigandButton.config(state = DISABLED)


def FindSimilarLigand():
    """
    Find ligand that's similar to the one in the current view.

    Similar...

    Same chemical groups?
    Same interactions?

    HOW:
    - parse the current ligand file loaded to find the list of interactions
    - generate residues filter objects (new function?)
    - create an interactive toplevel window with selection functions
    - provide optional criteria? (energy too? 
    - ...
    - PROFIT!

    """
    if DEBUG: print "FindSimilarLigand> find similar request"
    pass


def AddNote():
    """
    -get the current ligand and add notes

    - if the toplevel window exist and there's data on it, save the content before:
        -switching to another ligand
        -close the window
        -(ignore if empty)

    """

#Button(Toolbar3D, text = "Find similar...", command = FindSimilarLigand).grid(row = 9, column = 0, padx = 3, sticky = W+E)
#Button(Toolbar3D, text = "Add notes...", command = AddNote).grid(row = 10, column = 0, padx = 3, sticky = W+E)

# DISABLED BUTTONS
#Button(viewer3D.interior(), text = "Find similar...", command = FindSimilarLigand).grid(row = 99, column = 1, padx = 3, sticky = W+E)
#Button(viewer3D.interior(), text = "Add notes...", command = AddNote).grid(row = 99, column = 2, padx = 3, sticky = W+E)
Button(viewer3D.interior(), textvar = ViewerLabel, command = VisOptions).grid(row = 99, column = 2, columnspan = 1, padx = 3, sticky = E)

Toolbar3D.grid(row = 5, column = 0, sticky = N+W, padx = 3)



#########################################
##### 3D viewer##########################
#########################################




group_VIEWER = Frame(viewer3D.interior()) 
print "initialize the 3D viewer"

from Pmv.moleculeViewer import MoleculeViewer
from DejaVu import Viewer

#print "BROKEN? ASK MICHEL HOW TO FIX"
print "Loading 3D viewer...",
if '-s' in sys.argv:
    withShell = 1
else:
    withShell = 0
mv = MoleculeViewer(logMode = 'overwrite',  customizer=None, master=pmvroot, 
                    title='Coati | AutoDock VS', withShell= withShell, 
                    verbose=False, gui = True,guiVisible=1)
print "[DONE]"
vi = mv.GUI.VIEWER
vi.AddCamera(master=group_VIEWER) #, title="test")
CAMERA = vi.cameras[1]
vi.SetCurrentCamera(CAMERA)
CAMERA.name = "fox"
#print hex_to_rgb(BGcolor.get())
vi.CurrentCameraBackgroundColor( hex_to_rgb (BGcolor.get() ) )
#resetview()
SetAAlevel()

group_VIEWER.grid(row = 5, column = 1 , columnspan = 10, ipadx = 5, ipady = 5, padx = 5, pady = 5, sticky = W+E+N+S)



#	GPFframe = Pmw.Group(p3, tag_text = 'GPF template')
#	GPFframe.interior().grid_columnconfigure(1, weight = 1) # make the grid items flexible
#	GPFframe.interior().grid_rowconfigure(1,weight = 1)     # make the grid items flexible  
viewer3D.interior().grid_columnconfigure(1, weight = 1)
viewer3D.interior().grid_rowconfigure(5, weight = 1)

viewer3D.grid(row = 0, column = 3, rowspan = 20, sticky = W+E+N+S)


# Export data frame
ExportMenu(Tab4)
#ExportGroup = Pmw.Group(Tab4, tag_text = 'Export')
#Button(ExportGroup.interior(), text = "Save CSV list", command = SaveCSV).grid(row = 1, column = 0)

#Button(ExportGroup.interior(), text = "Save results folder", command = ExportMenu).grid(row = 1, column = 1)
#ExportGroup.grid(row = 6, column = 0, sticky = E+W+S, ipadx = 5)




#populate()"""
print "ce provo"
#CreateButtons(ligand_picker_frame)  # <-class
#CreateButtons(ligand_picker_frame)


# here should be the 3D viewer


if DEBUG:
    def DAMN():
        #ligand_buttons[i]['name'][0].bind('<Button-1>', lambda x : LoadLigand(index = i))
        for i in ligand_buttons:
            print "button ",1, ligand_buttons[i]['name'][1].get()
            print "button ",1, ligand_buttons[i]['name'][0].cget("command")
        return
    
        for l in LigBook:
            #print i, LigBook[i]["path"][-20:], LigBook[i]["le"]
            #print i, LigBook[i]["selected"]
    
           # sanity check
    
            # TODO temporary code
            for d in LigBook[l]['dlg']:
                fname = os.path.basename(d)
                #fname = os.path.splitext(name)[0]
                fname = fname.split("_", 2)[1]
                print l, fname
                if not l == fname:
                    print "ERROR IN THIS FILE! [ %s ]" % l
                    print dlg
                    print LigBook[l]
            # TODO temporary code 
    
    #Button(root, text = "DAMN", command = DAMN).grid(row = 99, column = 0)
    Button(root, text = "DAMN", command = DAMN).pack()
    Button(root, text = "show PMV", command = showPmv ).pack()
    Button(root, text = "hide PMV", command = hidePmv ).pack()



# INITIALIZATION
UpdateLigandInfo()
UpdateLigandInputInfo()
UpdateGridInfo()




# AutoDock Logo
#canvas = Canvas(root, width =282, height=69)
#img = PhotoImage(file='./logo.gif')
#canvas.create_image(145,40, image=img, anchor=CENTER)
#canvas.pack(anchor=CENTER)
nb.setnaturalsize() # Resize automatically the window
makemenu(root)

#root.bind('<Escape>', lambda: showPmv())
root.bind('<Escape>', lambda x: showPmv())
root.bind('<BackSpace>', lambda x: hidePmv())

if not "-i" in sys.argv:
    root.mainloop()
else:
    print "\n\n################################\n\n Interactive mode!\n\n########################"

print "Removing temp dir", TEMPDIR
if DEBUG: print "shutil.rmtree(%s)" % TEMPDIR
shutil.rmtree(TEMPDIR)

#exit()


