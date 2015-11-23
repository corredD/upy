
"""
    Copyright (C) <2010>  Autin L. TSRI
    
    This file git_upy/examples/upy_gui.py is part of upy.

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
######################################################
# GAMer gui plugin using upy
#
# Getting GAMer:
# 
#
#
# Getting upy:
#
#
#
# This plugin is protected by the GPL: Gnu Public Licence
# GPL - http://www.gnu.org/copyleft/gpl.html
# Script Copyright (C) Johan Hake <hake.dev@gmail.com>
#                      Ludovic Autin <autin@scripps.edu>
# Importing modules
import sys
import upy

import sys
#sys.path.append("/Users/ludo/DEV/py3.2/gamer/lib/python3.2/site-packages")
sys.path.append("/Users/ludo/DEV/py2.6/gamer/lib/python2.6/site-packages")

if sys.version_info[0] == 2:
    exec("""def myprint(*args):
    print " ".join("%s" % arg for arg in args)""")
elif sys.version_info[0] == 3:
    myprint = eval("print")
    
upy.setUIClass()

# FIXME: Should have a template?
from upy import uiadaptor

# Check for importing within a Host
if uiadaptor is None:
    raise ImportError("upy_gui need to be imported within a host gui.")

helperClass = upy.getHelperClass()

import math
import numpy as np
import re
try:
    import gamer
except:
    gamer = None
    myprint("no gamer")

gray = (.8, .8, .8)

class BoundaryMenu(object):
    "Helper class that is used to generate the boundary menu "
    def __init__(self, ui):
        assert(isinstance(ui, GamerUI))
        self.ui = ui
        self.empty_callback = lambda : None

    def get_names(self):
        obj = self.ui._get_selected_mesh(False)
        if obj is None:
            return []
        boundaries = self.ui.helper.getProperty(obj, "boundaries")
        if not boundaries:
            return []
        names = list(boundaries.keys())
#        names.sort()
        return names
        
    def __iter__(self):
        return iter(self.get_names())

    def append(self, value):
        pass

    def __len__(self):
        length = len(self.get_names())
        if length == 0:
            self.empty_callback()
        return length

    def __getitem__(self, key):
        names = self.get_names()
        if key >= len(names):
            return ""
        return names[key]
        
    def __setitem__(self, key, value):
        pass

class GamerUI(uiadaptor):
    def setup(self, *args, **kwargs):
        #uiadaptor.__init__(self, **kwargs)
        #self.title = "GAMer"
        #self.SetTitle(self.title)
        self.helper = helperClass(**kwargs)

        # Default ui values
        self.widgetGap = 0
        self._width = 60
        self._height = 10
        self.elemt_kwargs = dict(width=self._width, height=self._height)

        # Parameters for Surface mesh imports
        self.mesh_params = {}
        self.mesh_menu_items = ["OFF", "PDB (Surface)", "PDB (Gauss)",
                                "Lattice", "Sphere"]
        
        # Parameters for gamer mesh improvements
        self.gparams = dict()
        self.gparams["coarse_dense"] = {}
        self.gparams["coarse_flat"] = {}
        self.gparams["smooth"] = {}
        self.gparams["normal_smooth"] = {}
        self.gparams["refine"] = {}

        # Marking parameters
        self.mparams = {}
        self.menu_items = BoundaryMenu(self)
        self.menu_items.empty_callback = self._empty_menu_action
        
        # Tetrahedralization paramters
        self.domain_menu_items = []
        self.domains = {}        
        self.tetmesh_options=["FEtk", "DOLFIN"]
        self.tetmesh_formats=["mcsf", "dolfin"]
        self.tetmesh_suffices=[".m", ".xml"]
        self.tetparams = {} 
        self.buttons = {}
        self.labels = {}
        
        self._layout = []
        self.initWidget(id=10)
        self._all_gui_params = dict(gparams=self.gparams,
                                    mparams=self.mparams,
                                    tetparams=self.tetparams,
                                    mesh_params=self.mesh_params)
        self.setupLayout(kwargs.get("use_surface_mesh_generation", True),
                         kwargs.get("use_meshimprovement", True),\
                         kwargs.get("use_boundary_marking", True),\
                         kwargs.get("use_tetrahedralization", True))

    def CreateLayout(self):
        self._createLayout()
        return 1
    
    def Command(self, *args):
        self._command(args)
        return 1
    
    def setupLayout(self, use_surface_mesh_generation, use_meshimprovement,
                    use_boundary_marking, use_tetrahedralization):
        "Setup layout dependent on what the user need"
        self._layout = []
        if use_surface_mesh_generation:
            self._surface_mesh_generation_index = len(self._layout)
            self._layout.append(self.surface_mesh_generation_frame())
        if use_meshimprovement:
            self._layout.append(self.mesh_improvement_frame())
        if use_boundary_marking:
            self._layout.append(self.boundary_marking_frame())
        if use_tetrahedralization:
            self._tetrahedarlization_index = len(self._layout)
            self._layout.append(self.tetrahedralization_frame())
            
    def save_to_registry(self):
        from pickle import dump
        from tempfile import gettempdir
        from os.path import join
        registry_dict = {}
        def to_registry(registry_dict, guiparams):
            for key, value in guiparams.items():
                assert(isinstance(value, dict))
                if "id" in value and "name" in value:
                    registry_dict[key] = self.getVal(value)
                else:
                    registry_dict[key] = {}
                    to_registry(registry_dict[key], value)
        
        to_registry(registry_dict, self._all_gui_params)
        registry_dict["domains"] = self.domains        
        
        self._store("gamer_uiparams", registry_dict)
        

    def load_from_registry(self):
        from tempfile import gettempdir
        from os.path import join

        #myprint("loading")
        def from_registry(registry_dict, guiparams):
            for key, value in guiparams.items():
                assert(isinstance(value, dict))
                if key == "domains":
                    self.domains = values
                elif "id" in value and "name" in value and \
                       key in registry_dict:
                    self.setVal(value, registry_dict[key])
                    #myprint("Set value:", key, value)
                else:
                    from_registry(registry_dict[key], value)

        try:
            #d = load(open(join(gettempdir(), "gamer_uiparams.cpickle")))
            d = self._restore("gamer_uiparams")
            from_registry(d, self._all_gui_params)
        except Exception as e:
            myprint(e)
            self.save_to_registry()
        #myprint("done loading")
        
    def initWidget(self,id=None):
        # Declare UI elements for Surface Mesh imports
        self.buttons["import_surface_mesh"] = self._add_button(\
            "Import Surface Mesh", action=self.import_surface_mesh,\
            tooltip="Import Surface mesh")

        self.mesh_params["surface_mesh_menu"] = self._addElemt(\
            name="Surface mesh:", action=self._update_mesh_import,\
            value=self.mesh_menu_items, width=self._width, \
            height=self._height, variable=self.addVariable("int", 1),\
            type="pullMenu")

        self.mesh_params["Blobbyness"] = self._add_float(\
            "Blobbyness", mini=-1., maxi=-.0001, init=-0.2, step=.0001,\
            tooltip="The blobbyness of the Gaussian scalar function.")
        
        self.mesh_params["Iso_value"] = self._add_float(\
            "Iso value", mini=0.01, maxi=3.0, init=2.5, step=.1,\
            tooltip="The iso value of the Marching Cube algorithm.")

        self.mesh_params["Sphere_divisions"] = self._add_int(\
            "Spehere divisions", mini=1, maxi=9, init=4,\
            tooltip="The number of divisions used to generate a Sphere mesh.")
                
        # Declare UI elements for coarse dense
        self.buttons["coarse_dense"] = self._add_button(\
            "Coarse Dense", action=self.action_closure("coarse_dense"),\
            tooltip="Coarse dense areas of the mesh")
        
        self.gparams["coarse_dense"]["rate"] = self._add_float(\
            "RateDense", mini=0.001, maxi=4.0, init=2.5, step=.05,\
            tooltip="The rate for coarsening dense areas")
        
        self.gparams["coarse_dense"]["numiter"] = self._add_int(\
            "IterDense", mini=1, maxi=15, init=1,\
            tooltip="The number of iteration for coarsening dense areas")
    
        # Declare UI elements for coarse flat
        self.buttons["coarse_flat"] = self._add_button(\
            "Coarse Flat", action=self.action_closure("coarse_flat"),\
            tooltip="Coarse flat areas of the mesh")
        
        self.gparams["coarse_flat"]["rate"] = self._add_float(\
            "RateFlat", mini=0.00001, maxi=0.5, init=0.016, step=.01,\
            tooltip="The rate for coarsening flat areas")

        # Declare UI elements for smooth
        self.buttons["smooth"] = self._add_button(\
            "Smooth", action=self.action_closure("smooth"),\
            tooltip="Smooth the mesh")
        
        self.gparams["smooth"]["max_min_angle"] = self._add_int(\
            "Max min deg:", mini=10, maxi=20, init=15,\
            tooltip="The maximal minimum angle for smoothing")

        self.gparams["smooth"]["min_max_angle"] = self._add_int(\
            "Max min deg:", mini=140, maxi=160, init=150,\
            tooltip="The minimum maximal angle for smoothing",\
            action=self.update_min_max_angle)

        self.gparams["smooth"]["max_iter"] = self._add_int(\
            "IterSmooth", mini=1, maxi=50, init=6,\
            tooltip="The number of iteration for smooting mesh")

        self.gparams["smooth"]["preserve_ridges"] = self._add_check_box(\
            "Preserve ridges", action=None,\
            tooltip="preserve ridges during smoothing")
        
        # Declare UI elements for normal smooth
        self.buttons["normal_smooth"] = self._add_button(\
            "Normal Smooth", action=self.action_closure("normal_smooth"),\
            tooltip="Smooth the normals of the mesh")
        
        # Declare UI elements for refine
        self.buttons["refine"] = self._add_button(\
            "Uniform Refine", action=self.action_closure("refine"),\
            tooltip="Refine mesh uniformly")

       # Declare UI elements for repair
        self.buttons["repair"] = self._add_button(\
            "Repair", action=self.repair_mesh,\
            tooltip="Repair the mesh")
            
       # Declare UI elements for repair
        self.buttons["centralize"] = self._add_button(\
            "Centralize", action=self.centralize,\
            tooltip="Centralize the mesh")
        
        # Declare UI creating new mesh
        self.gparams["create_new_mesh"] = self._add_check_box(\
            "Create new mesh", tooltip="Create a new mesh", \
            init=1)
        
        # Declare UI marking of boundaries
        self.buttons["create_boundary"] = self._add_button(\
            "New", action=self._new_boundary,\
            tooltip="Create a boundary from selected faces",\
            width=self._width)
        
        self.buttons["delete_boundary"] = self._add_button(\
            "Delete", action=self._delete_boundary,\
            tooltip="Delete the selected boundary",\
            width=self._width)
        
        self.buttons["select_boundary"] = self._add_button(\
            "Select", action=self._select_boundary,\
            tooltip="Select faces from the active boundary",\
            width=self._width)
        
        self.buttons["deselect_boundary"] = self._add_button(\
            "Deselect", action=self._deselect_boundary,\
            tooltip="Deselect faces from the active boundary",\
            width=self._width)
        
        self.buttons["hide_boundary"] = self._add_button(\
            "Hide", action=self._hide_boundary,\
            tooltip="Hide faces of the boundary",\
            width=self._width)
        
        self.buttons["unhide_boundary"] = self._add_button(\
            "Unhide", action=self._unhide_boundary,\
            tooltip="Unhide faces of the boundary",\
            width=self._width)
        
        self.buttons["assign_boundary"] = self._add_button(\
            "Assign", action=self._assign_boundary,\
            tooltip="Assign boundary to selected faces",\
            width=self._width*2.0)

        self.buttons["calculate_area"] = self._add_button(\
            "Area", action=self._calculate_area,\
            tooltip="Calculate the area of a boundary",\
            width=self._width)

        self.buttons["calculate_areas"] = self._add_button(\
            "Areas", action=self.calculate_areas,\
            tooltip="Calculate the area of all boundaries",\
            width=self._width)

        self.buttons["delete_faces"] = self._add_button(\
            "Delete", action=self.delete_faces,\
            tooltip="Delete selected faces",\
            width=self._width)

        self.buttons["triangulate_holes"] = self._add_button(\
            "Triangulate holes", action=self.triangulate_holes,\
            tooltip="Triangulate holes",\
            width=self._width)

        # Get any stored Boundaries
        have_boundaries = False
        obj = self._get_selected_mesh(False)
        if obj:
            boundaries = self.helper.getProperty(obj, "boundaries")
            if boundaries:
                have_boundaries = True
                name = list(boundaries.keys())[0]
                boundary = boundaries[name]

        if have_boundaries:
           marker_init = boundary["marker"] 
           color_init = boundary["r"], boundary["g"], boundary["b"],
           name_init = name 
        else:
           marker_init = 1
           color_init = (0.8, 0.8, 0.8)
           name_init = "" 
        
        self.mparams["marker"] = self._add_int(\
            "Marker:", mini=1, maxi=10000, init=marker_init, \
            action=self._update_boundary_marker,\
            tooltip="A marker value for the boundary")
        
        self.mparams["name"] = self._addElemt(\
            name="", action=self._update_boundary_name, \
            variable = self.addVariable("str", name_init),
            type="inputStr", width=self._width, height=self._height)
        
        self.mparams["color"] = self._addElemt(\
            name="Color", action=self._update_boundary_color, \
            variable = self.addVariable("col", color_init),
            type="color", width=self._height, height=self._height)

        self.mparams["boundary_menu"] = self._addElemt(\
            name="boundary_menu", action=self._update_boundary_menu,\
            value=self.menu_items, width=self._height, \
            height=self._height, variable=self.addVariable("int", 1),\
            type="pullMenu")
        
        # Declare UI for tetrahedralizing mesh
        self.tetparams["domain_menu"] = self._addElemt(\
            name="Domains:", action=self._update_domain_menu,\
            value=self.domain_menu_items, width=self._width, \
            height=self._height, variable=self.addVariable("int", 1),\
            type="pullMenu")

        self.tetparams["domainmarker"] = self._add_int(\
            "Marker:", mini=1, maxi=10000, init=1, \
            action=self._update_domain, tooltip="A marker value for a domain")

        self.tetparams["use_volume_constraint"] = self._add_check_box(\
            "Use volume constraint", action=self._update_domain,
            tooltip="Use volume constraint, when generating tetrahedral "\
            "mesh", width=self._width)

        self.tetparams["volume_constraint"] = self._add_float(\
            "Vol constr:", mini=.00001, maxi=1000000,\
            action=self._update_domain, init=100.,\
            tooltip="The volume of a domain", step=1, precision=1.0,\
            width=self._width)

        self.tetparams["domain_as_hole"] = self._add_check_box(\
            "Use domain as a hole", action=self._update_domain,
            tooltip="Decalar a domain as a hole within a tetrahedral mesh",
            width=self._width)

        self.buttons["add_domain"] = self._add_button(\
            "Add selected", action=self._add_domain, width=self._width,\
            tooltip="Add a selected mesh as a domain")
        
        self.buttons["delete_domain"] = self._add_button(\
            "Delete", action=self._delete_domain, width=self._width,\
            tooltip="Delete a selected domain")

        self.buttons["tetrahedralize"] = self._add_button(\
            "Tetrahedralize", action=self.tetrahedralize, width=self._width,\
            tooltip="Tetrahedralize selected mesh")
        
        self.tetparams["format_menu"] = self._addElemt(\
            name="Mesh format:",\
            value=self.tetmesh_options, width=self._width, \
            height=self._height, variable=self.addVariable("int", 1),\
            type="pullMenu")
        
        self.tetparams["dihedral_angle"] = self._add_float(\
            "Min dihed deg:", mini=0.0001, action=None, maxi=20.0, init=10.,\
            tooltip="The minimal dihedral angle", step=.5, precision=1.0,\
            width=self._width)

        
        self.tetparams["aspect_ratio"] = self._add_float(\
            "Min aspec rat:", mini=1.0, maxi=5.0, action=None, init=1.3,\
            tooltip="The minimal aspect ratio", step=.1, precision=1.0,\
            width=self._width)
        
        # Declare UI for exiting
        self.buttons["exit"] = self._add_button(\
            "Exit", action=self.exit_event,\
            tooltip="Exit GAMer mesh improvements")

        # Add labels for sliders
        for operation in ["coarse_dense", "coarse_flat", "smooth"]:
            self.labels[operation] = {}
            for key, elemt in self.gparams[operation].items():
                self.labels[operation][key] = self._add_text(elemt["name"], \
                                                             width=elemt["width"])
        for key, elemt in self.mparams.items():
            if key == "name":
                self.labels[key] = self._add_text("Name:", \
                                                  width=elemt["width"])
            else:
                self.labels[key] = self._add_text(elemt["name"], \
                                                  width=elemt["width"])
        
        for key, elemt in self.tetparams.items():
            self.labels[key] = self._add_text(elemt["name"], \
                                              width=elemt["width"])

        self.labels["empty"] = self._add_text("")
        self.labels["small_empty"] = self._add_text("", width=self._height)
        self.labels["large_empty"] = self._add_text("", width=self._width*1.2)

    def surface_mesh_generation_frame(self):

        if len(self._layout) > self._surface_mesh_generation_index:
            collapse = self._layout[self._surface_mesh_generation_index]["collapse"]
        else:
            collapse = True

        frame_info = []
        frame_info.append([self.mesh_params["surface_mesh_menu"]])
        
        # Build panel based on what menu item is selected
        mesh_type = self.mesh_menu_items[self.getLong(\
            self.mesh_params["surface_mesh_menu"])]
        
        if mesh_type == "Lattice":
            pass
            # FIXME: Add stuff!

        elif mesh_type == "Sphere":
            
            frame_info.append([self.mesh_params["Sphere_divisions"]])

        elif mesh_type == "PDB (Gauss)":

            frame_info.append([self.mesh_params["Blobbyness"]])
            frame_info.append([self.mesh_params["Iso_value"]])
            
        elif mesh_type == "Lattice":
            myprint("Not supported...")
            
        frame_info.append([self.buttons["import_surface_mesh"]])
        return self._addLayout(name="Surface mesh import", elems=frame_info,
                               collapse=collapse)

    def mesh_improvement_frame(self):
        # Inherit the collapse value of the frame if it excists
        frame_info = []
        frame_info.append([self.labels["empty"], \
                           self.labels["coarse_dense"]["rate"],
                           self.labels["coarse_dense"]["numiter"]])
        frame_info.append([self.buttons["coarse_dense"], \
                           self.gparams["coarse_dense"]["rate"], \
                           self.gparams["coarse_dense"]["numiter"]])
        frame_info.append([self.buttons["coarse_flat"], \
                           self.gparams["coarse_flat"]["rate"]])
        frame_info.append([self.labels["empty"], \
                           self.labels["smooth"]["max_min_angle"],
                           self.labels["smooth"]["max_iter"]])
        frame_info.append([self.buttons["smooth"], \
                           self.gparams["smooth"]["max_min_angle"],\
                           self.gparams["smooth"]["max_iter"]])
        frame_info.append([self.gparams["smooth"]["preserve_ridges"]])
        frame_info.append([self.labels["empty"]])
        frame_info.append([self.buttons["normal_smooth"]])
        frame_info.append([self.labels["empty"]])
        frame_info.append([self.gparams["create_new_mesh"]])
        frame_info.append([self.buttons["repair"], self.buttons["centralize"]])
        frame_info.append([self.buttons["delete_faces"], \
                           self.buttons["triangulate_holes"]])
        
        return self._addLayout(name="Surface Mesh Improvements", elems=frame_info)

    def boundary_marking_frame(self):
        frame_info = []
        frame_info.append([self.labels["name"], self.mparams["name"], \
                           self.mparams["boundary_menu"]])
        frame_info.append([self.labels["marker"], \
                           self.mparams["marker"], self.mparams["color"]])
        frame_info.append([self.buttons["create_boundary"],\
                           self.buttons["delete_boundary"]])
        frame_info.append([self.buttons["select_boundary"],\
                           self.buttons["deselect_boundary"]])
# FIXME: These functions does not work...
# FIXME: And they produce large memopry leaks...
#        frame_info.append([self.buttons["hide_boundary"],\
#                           self.buttons["unhide_boundary"]])
        frame_info.append([self.buttons["assign_boundary"]])
        frame_info.append([self.buttons["calculate_areas"]])
        
        return self._addLayout(name="Boundary marking", elems=frame_info)
        
    def tetrahedralization_frame(self, domain=True):
        
        if len(self._layout) > self._tetrahedarlization_index:
            collapse = self._layout[self._tetrahedarlization_index]["collapse"]
        else:
            collapse = True

        frame_info = []
        frame_info.append([self.labels["domain_menu"], \
                           self.buttons["add_domain"]])
        
        # If domain is passed
        if domain:
            frame_info.append([self.tetparams["domain_menu"],
                               self.buttons["delete_domain"]])
            frame_info.append([self.tetparams["domain_as_hole"]])
#            if not domain["as_hole"]:
            frame_info.append([self.labels["domainmarker"], \
                               self.tetparams["domainmarker"]])
            frame_info.append([self.labels["volume_constraint"],
                               self.tetparams["volume_constraint"]])
            frame_info.append([self.tetparams["use_volume_constraint"]])
            
            frame_info.append([self.labels["empty"]])
            frame_info.append([self.labels["dihedral_angle"],\
                               self.labels["aspect_ratio"]])
            frame_info.append([self.tetparams["dihedral_angle"],\
                               self.tetparams["aspect_ratio"]])
            frame_info.append([self.labels["empty"],\
                               self.labels["format_menu"]])
            frame_info.append([self.buttons["tetrahedralize"],\
                               self.tetparams["format_menu"]])
        
        return self._addLayout(name="Tetrahedralization", elems=frame_info,
                               collapse=collapse)
    def _update_mesh_import(self):
        
        self._layout[self._surface_mesh_generation_index] = \
                    self.surface_mesh_generation_frame()
        self.updateViewer()
        

    def import_surface_mesh(self):

        file_type = self.mesh_menu_items[self.getLong(\
            self.mesh_params["surface_mesh_menu"])]

        #myprint("Importing file_type ", file_type)
        
        # Import surface mesh from file
        if file_type in ["OFF", "PDB (Surface)", "PDB (Gauss)", "Lattice"]:
            self.save_to_registry()
            if "PDB" in file_type:
                suffix = "*.pdb"
            elif "OFF" in file_type:
                suffix = "*.off"
            else:
                suffix = "*.lat"
            self.fileDialog(label="Import",
                            callback=self.import_surface_mesh_from_file_action,
                            suffix=suffix)
        
        elif file_type == "Sphere":
            divisions = self.getLong(self.mesh_params["Sphere_divisions"])
            gmesh = gamer.SurfaceMesh(divisions)
            self.gamer_to_host(gmesh, {}, "Sphere", switch_layer=False)

    
    def update_min_max_angle(self, *args):
        self.setReal(self.gparams["smooth"]["min_max_angle"], 180 - \
                     2*self.getVal(self.gparams["smooth"]["max_min_angle"]))
        
    def exit_event(self,*args):
        self.save_to_registry()
        self.close()

    def _get_next_marker(self, marker, boundaries=None):
        if boundaries is None:
            obj = self._get_selected_mesh()
            if obj is None:
                return marker
            boundaries = self.helper.getProperty(obj, "boundaries")
            if boundaries is None:
                return marker
        
        markers = [b["marker"] for b in list(boundaries.values())]
        while marker in markers:
            marker += 1
        return marker

    def _attach_suffix_to_str(self, name):
        suffices = re.findall("\.([0-9]*)", name)
        if suffices:
            num = int(suffices[0])+1
            name = name.replace("."+suffices[0], "")
        else:
            num = 1
        return "%s.%03d"%(name, num)

    def _new_boundary(self):
        "Create a boundary using default name, marker and color"
        
        # Get selected mesh
        obj = self._get_selected_mesh()
        if obj is None:
            return
        
        name = self.getVal(self.mparams["name"])
        if name == "":
            name = "Boundary"
        boundaries = self.helper.getProperty(obj, "boundaries")

        if not boundaries:
            self.helper.setProperty(obj, "boundaries", {})
            boundaries = self.helper.getProperty(obj, "boundaries")
            
        while name in boundaries:
            name = self._attach_suffix_to_str(name)

        marker = self._get_next_marker(self.getVal(self.mparams["marker"]),\
                                       boundaries)
        color = self.getVal(self.mparams["color"])

        # Allways new entitiy
        boundaries[name] = dict(marker=marker, r=color[0], g=color[1], \
                                b=color[2], faces={})
        
        names = self.menu_items.get_names()
        
        self.setVal(self.mparams["boundary_menu"], names.index(name))
        self._update_boundary_menu()
        #self._assign_boundary()
        
    def _repaint_boundaries(self, obj):
        # Grab mesh name
        boundaries = self.helper.getProperty(obj, "boundaries")
        if not boundaries:
            return
        
        # Ensure editmode is off
        editmode = self.helper.toggleEditMode()
        
        # Paint boundaries 
        items = boundaries.items if hasattr(boundaries, "items") \
                else boundaries.iteritems
        for name, boundary in items():
            faces = self._get_boundary_faces(boundary)
            self.helper.changeColor(obj, (boundary["r"], boundary["g"], \
                                          boundary["b"]),\
                                    facesSelection=faces,\
                                    faceMaterial=False)

        # Restore editmode
        self.helper.restoreEditMode(editmode)
        
    def _get_boundary_faces(self, boundary):
        if not "faces" in boundary:
            return []
        all_faces = []
        for faces in list(boundary["faces"].values()):
            all_faces.extend(faces)

        return all_faces

    def _set_boundary_faces(self, boundary, faces):
        "Set faces in boundary props"
        if not "faces" in boundary:
            return
        assert(isinstance(faces, list))
        # Maximal indices in a array prop in Blender is 10000
        max_ind = 10000
        num_sub_arrays = len(faces)/max_ind+1

        # If the faces allready excist delete it and re attach it
        if "faces" in boundary:
            for key in boundary["faces"]:
                del boundary["faces"][key]
            del boundary["faces"]
            
        boundary["faces"] = {}
        for ind in range(num_sub_arrays):
            boundary["faces"]["F%d"%ind] = faces[ind*max_ind: \
                                                 min((ind+1)*max_ind, len(faces))]

    def _empty_menu_action(self):
        self.setVal(self.mparams["boundary_menu"], 0) #why is it comments
        self.setVal(self.mparams["name"], "")
        self.setVal(self.mparams["marker"], 1)
        self.setVal(self.mparams["color"], gray)
        
    def _delete_boundary(self):
        if len(self.menu_items)==0:
            return 
        name = self.menu_items[self.getLong(\
            self.mparams["boundary_menu"])]
        obj = self._get_selected_mesh()
        if obj is None:
            return
        
        boundaries = self.helper.getProperty(obj, "boundaries")
        if name not in boundaries:
            return
        
        names = self.menu_items.get_names()
        if not names:
            return
        
        is_empty = len(names) == 1
        is_last = names[-1] == name
        need_repaint = bool(self._get_boundary_faces(boundaries[name]))
        
        if need_repaint:
            # Ensure editmode is off
            editmode = self.helper.toggleEditMode()
            
            faces = self._get_boundary_faces(boundaries[name])
            self.helper.changeColor(obj, gray,\
                                    facesSelection=faces,\
                                    faceMaterial=False)
            # Restore editmode
            self.helper.restoreEditMode(editmode)

        # Update value of menu
        if is_empty:
            self._empty_menu_action()
        elif is_last:
            self.setVal(self.mparams["boundary_menu"], len(names)-2)
        
        # Do the actuall deletion
        for key in ["marker", "r", "g","b"]:
            del boundaries[name][key]
        for key in boundaries[name]["faces"]:
            del boundaries[name]["faces"][key]
        del boundaries[name]["faces"]
        del boundaries[name]
        
        self._update_boundary_menu()

    def _select_boundary(self, select=True):
        if len(self.menu_items)==0:
            return
        
        boundary = self._get_boundary(self.menu_items\
                                      [self.getLong(\
                                          self.mparams["boundary_menu"])])
        if not boundary:
            return
        
        faces = self._get_boundary_faces(boundary)
        
        obj = self._get_selected_mesh()
        if obj is None:
            return
        
        self.helper.selectFaces(obj, faces, select)
    
    def _deselect_boundary(self):
        self._select_boundary(False)

    def _hide_boundary(self, hide=True):
        if len(self.menu_items)==0:
            return
        
        boundary = self._get_boundary(self.menu_items\
                                      [self.getLong(\
                                          self.mparams["boundary_menu"])])
        if not boundary:
            return
        
        faces = self._get_boundary_faces(boundary)
        
        obj = self._get_selected_mesh()
        if obj is None:
            return
        
        self.helper.hideFaces(obj, faces, hide)
    
    def _unhide_boundary(self):
        self._hide_boundary(False)

    def _calculate_area(self):
        if len(self.menu_items)==0:
            return
        
        name = self.menu_items[self.getLong(self.mparams["boundary_menu"])]

        boundary = self._get_boundary(name)
        if not boundary:
            return
        
        obj = self._get_selected_mesh()
        if obj is None:
            return
        
        faces = self._get_boundary_faces(boundary)
        area = self.helper.faceArea(obj, faces)

        if area > 0:
            print("Area of boundary '%s' %.2e"%(name, area))

    def calculate_areas(self):
        "Calculate areas of all boundaries"
        try :
            from cPickle import dump
        except :
            from pickle import dump
        if len(self.menu_items)==0:
            return

        obj = self._get_selected_mesh()
        if obj is None:
            return
        
        areas = {}
        
        for boundary_name in self.menu_items:
            boundary = self._get_boundary(boundary_name)
            if not boundary:
                continue
            
            faces = self._get_boundary_faces(boundary)
            area = self.helper.faceArea(obj, faces)
            
            if area > 0:
                areas[boundary_name] = area
                myprint("Area of boundary '%s' %.2e"%(boundary_name, area))

        dump(areas, open(self.helper.getName(obj)+".cpickle", "wb"))
                    
    def _assign_boundary(self):
        # Get selected mesh
        if len(self.menu_items)==0:
            return
        
        obj = self._get_selected_mesh()
        if obj is None:
            return

        boundary_name = self.menu_items[self.getLong(\
            self.mparams["boundary_menu"])]
        
        boundaries = self.helper.getProperty(obj, "boundaries")
        if not boundaries:
            return
        
        if boundary_name not in boundaries:
            return
        
        boundary = boundaries[boundary_name]

        # Get all faces and indices of all selected faces
        faces, faces_selected_indice = self.helper.getMeshFaces(obj, \
                                                                selected = True)
        
        # If no faces were selected
        if not faces_selected_indice:
            return

        # Ensure editmode is off
        editmode = self.helper.toggleEditMode()
        
        for bound_name in list(boundaries.keys()):
            if bound_name == boundary_name:
                continue
            bound = boundaries[bound_name]
            other_faces = set(self._get_boundary_faces(bound))
            if not other_faces.isdisjoint(faces_selected_indice):
                other_faces.difference_update(faces_selected_indice)
                self._set_boundary_faces(bound, list(other_faces))

        # Set the selected faces
        self._set_boundary_faces(boundary, faces_selected_indice)
        
        # Restore editmode
        self.helper.restoreEditMode(editmode)
        
        # Repaint
        self._repaint_boundaries(obj)

    def _get_boundary(self, name):
        # Get selected mesh
        obj = self._get_selected_mesh()
        if obj is None:
            return
        
        boundaries = self.helper.getProperty(obj, "boundaries")
        
        if not boundaries:
            return
        
        if name not in boundaries:
            return

        return boundaries[name]

    def _boundary_to_dict(self, boundary):
        pass

    def _update_boundary_menu(self):
        if len(self.menu_items)==0:
            return 
        name = self.menu_items[self.getLong(\
            self.mparams["boundary_menu"])]
        boundary = self._get_boundary(name)
        myprint("update menu boundary ", name)
        if not boundary:
            return
        
        self.setVal(self.mparams["name"], name)
        self.setVal(self.mparams["marker"], boundary["marker"])
        self.setVal(self.mparams["color"], (boundary["r"], boundary["g"], \
                                            boundary["b"]))
        
    def _update_boundary_marker(self):
        if len(self.menu_items)==0:
            return
        old_name = self.menu_items[self.getLong(\
            self.mparams["boundary_menu"])]
        
        boundary = self._get_boundary(old_name)
        if not boundary:
            return
        
        old_marker = boundary["marker"]
        
        new_marker = self.getVal(self.mparams["marker"])
        if old_marker==new_marker:
            return

        new_marker = self._get_next_marker(new_marker)
        self.setVal(self.mparams["marker"], new_marker)

        boundary["marker"] = new_marker

    def _update_boundary_name(self):
        if len(self.menu_items)==0:
            return 
        old_name = self.menu_items[self.getLong(\
            self.mparams["boundary_menu"])]
        
        boundary = self._get_boundary(old_name)
        
        if not boundary:
            return
        
        new_name = self.getVal(self.mparams["name"])
        
        if new_name == old_name:
            return
        
        while new_name in self.menu_items:
            new_name = self._attach_suffix_to_str(new_name)

        obj = self._get_selected_mesh()
        if obj is None:
            return
        
        boundaries = self.helper.getProperty(obj, "boundaries")

        # Copy the boundary to the new name.
        # NOTE: Pretty cumbersum as Blender otherwise leak memory...
        boundaries[new_name] = {}
        for key in ["marker", "r", "g","b"]:
            boundaries[new_name][key] = boundaries[old_name][key]
            del boundaries[old_name][key]
        boundaries[new_name]["faces"] = {}
        for key in boundaries[old_name]["faces"]:
            boundaries[new_name]["faces"][key] = \
                                boundaries[old_name]["faces"][key]
            del boundaries[old_name]["faces"][key]
        del boundaries[old_name]["faces"]
        del boundaries[old_name]

        self.setVal(self.mparams["name"], new_name)
        
        
    def _update_boundary_color(self):
        if len(self.menu_items)==0:
            return 
        boundary = self._get_boundary(self.menu_items[\
            self.getLong(self.mparams["boundary_menu"])])
        
        if not boundary:
            return
        
        color = self.getVal(self.mparams["color"])

        if color == (boundary["r"], boundary["g"], boundary["b"]):
            return
        
        boundary["r"], boundary["g"], boundary["b"] = color
        
        obj = self._get_selected_mesh()

        self._repaint_boundaries(obj)

    def _delete_domain(self):

        # Get number of domains
        num_domains = len(self.domain_menu_items)

        # Sanity check
        if num_domains != len(self.domains):
            return

        # No domains
        if len(self.domain_menu_items)==0:
            return

        # Get index and name of the domain
        index = self.getLong(self.tetparams["domain_menu"])
        name = self.domain_menu_items[index]
        
        # convinient checks for updating the menu after deletion
        is_empty = num_domains == 1
        is_last = index == num_domains -1

        # Update value of menu
        if is_empty:
            domain = None
        elif is_last:
            self.setVal(self.tetparams["domain_menu"], num_domains-2)
            domain = self.domains[self.domain_menu_items[-1]]
        else:
            domain = self.domains[self.domain_menu_items[index]]
        
        # Pop the registered domain
        self.domains.pop(name)
        self.domain_menu_items.remove(name)

        # Update panel
        self._update_domain_frame(domain)

    def _add_domain(self):
        
        obj = self.helper.getCurrentSelection()[0]#self._get_selected_mesh()
        if obj is None:
            return
        
        name = self.helper.getName(obj)

        # Check for registration
        if name in self.domains:
            self.drawError(errormsg="Mesh already registered as a domain.")
            return

        # Update menu value
        self.addItemToPMenu(self.tetparams["domain_menu"],name)
#        self.setVal(self.tetparams["domain_menu"], len(self.domain_menu_items))
        self.domain_menu_items.append(name)

        # Add a default domain dict
        self.domains[name] = dict(marker=1, as_hole=False,
                                  use_volume_constraint=False,
                                  volume_constraint=100,)

        # Re draw interface
        self._update_domain_frame(self.domains[name])

    def _update_domain_menu(self):
        if len(self.domain_menu_items)==0:
            return

        name = self.domain_menu_items[self.getLong(\
            self.tetparams["domain_menu"])]
        
        domain = self.domains[name]
        
        # Get values from GUI
        self.setVal(self.tetparams["domainmarker"], domain["marker"] )
        self.setVal(self.tetparams["domain_as_hole"], domain["as_hole"])
        self.setVal(self.tetparams["use_volume_constraint"],
                    domain["use_volume_constraint"])
        self.setVal(self.tetparams["volume_constraint"], domain["volume_constraint"])

        # Update GUI
        self._update_domain_frame(domain)
        
    def _update_domain(self):
        if len(self.domain_menu_items)==0:
            return

        name = self.domain_menu_items[self.getLong(\
            self.tetparams["domain_menu"])]
        
        domain = self.domains[name]

        # Get values from GUI
        domain["marker"] = self.getLong(self.tetparams["domainmarker"])
        domain["as_hole"] = self.getVal(self.tetparams["domain_as_hole"])
        domain["use_volume_constraint"] = self.getVal(\
            self.tetparams["use_volume_constraint"])
        domain["volume_constraint"] = self.getVal(\
            self.tetparams["volume_constraint"])

        # Update GUI
        self._update_domain_frame(domain)

    def _update_domain_frame(self, domain):
        self._layout[self._tetrahedarlization_index] = \
                                    self.tetrahedralization_frame(domain)
        self.updateViewer()

    def delete_faces(self):
        "delete marked faces"
        # Get selected mesh
        obj = self._get_selected_mesh()
        if obj is None:
            return

        # Get all faces and indices of all selected faces
        faces, faces_remove = self.helper.getMeshFaces(obj, selected = True)
        all_faces = self.helper.getMeshFaces(obj)

        # If no faces were selected
        if not faces_remove:
            return

        # Create face map of old to new faces
        faces_keep = set(range(len(all_faces)))
        faces_keep.difference_update(faces_remove)
        face_map = dict((old, new) for new, old in enumerate(faces_keep))
        
        # An array of bool to indicate if a face should be removed or not
        face_keep_flags = np.ones(len(all_faces), dtype="b")
        face_keep_flags[faces_remove] = False

        new_faces = [all_faces[face] for face in faces_keep]

        # Update boundaries
        for boundary_name in self.menu_items:
            boundary = self._get_boundary(boundary_name)
            if not boundary:
                continue
            
            new_faces = []
            faces = self._get_boundary_faces(boundary)
            
            for face in faces:
                if face_keep_flags[face]:
                    new_faces.append(face_map[face])
            
            if not new_faces:
                myprint("No faces left for boundary:", boundary_name)
            
            self._set_boundary_faces(boundary, new_faces)
        
        bmesh = self.helper.getMeshFrom(obj)
        self.helper.deleteMesFaces(obj,faces=faces_remove)        
#        bmesh.faces.delete(True, faces_remove)

        # Ensure editmode is off
        editmode = self.helper.toggleEditMode()
        
        # Restore editmode
        self.helper.restoreEditMode(editmode)

        # Repaint
        self._repaint_boundaries(obj)

    def repair_mesh(self):
        # Get selected mesh
        obj = self._get_selected_mesh()
        if obj is None:
            self.waitingCursor(0)
            return
        bmesh = self.helper.getMeshFrom(obj)
        
        # Ensure editmode is off
        editmode = self.helper.toggleEditMode()
        
        # Collect quads
        nquads = 0
    
        # Remove free vertices
        vertices = self.helper.getMeshVertices(obj)
        faces = self.helper.getMeshFaces(obj)

        vert_users = np.zeros(len(vertices))
        for i,f in enumerate(faces):
            self.helper.selectFace(obj,i,select=False)
            for v in f:
                vert_users[v] += 1
            if len(f) == 4:
                nquads += 1
#                f.sel = 1
                self.helper.selectFace(obj,i)
        if nquads:
            print ("Found %d quads"%nquads)
        
        meshedges = self.helper.getMeshEdges(obj)
        for e in meshedges:
            for v in e: 
                vert_users[v] += 1
        
        verts_free = (vert_users==0).nonzero()[0].tolist()
    	
        if verts_free:
            myprint("Removed %s vertices"%len(verts_free))
            #bmesh.verts.delete(verts_free)
            self.helper.deleteMeshVertices(obj,vertices=verts_free)
        # Remove edges with no face connected to it
        edges = set() 
    	
        for i in range(len(faces)):
            for edkey in self.helper.getFaceEdges(obj,i):
                edges.add(edkey)
    	
        edges_free = []
        for e in edges :
            if e not in meshedges :
                edges_free.append(e)
#        for e in bmesh.edges:
#            if e.key not in edges:
#                edges_free.append(e)
        if edges_free:
            self.helper.deleteMeshEdges(obj,edges=edges_free)
            #bmesh.edges.delete(edges_free)
            myprint("Removed %s edges"%len(edges_free))
    
        # Convert selected quads to triangles
        #bmesh.quadToTriangle()#Bmeshfor 2.63
        self.helper.triangulate(obj) # this change the mesh data  infomations ?
        # Check for non-manifolds and open edges
        meshedges = self.helper.getMeshEdges(obj)    
        faces = self.helper.getMeshFaces(obj)
        vertices = self.helper.getMeshVertices(obj)
        # print(meshedges)
        edge_map = dict((edge, []) for edge in meshedges)
        #edge_map = dict((edge.key, []) for edge in bmesh.edges)
        print(edge_map)
        for i in range(len(faces)):
            # Unselect all faces
            #face.sel = 0
            self.helper.selectFace(obj,i,select=False)
            for edge in self.helper.getFaceEdges(obj,i) :#face.edge_keys:
                edge_map[edge].append(i)
                #edge_map[tuple(sorted(edge))].append(face.index)        
        open_edges = []
        non_manifold_edges = []
        open_vertices_map = {}
        for edge, faces in edge_map.items():
            if len(faces) == 1:
                open_edges.append(edge)
                for i, vert_id in enumerate(edge):
                    if vert_id not in open_vertices_map:
                        open_vertices_map[vert_id] = [edge[1-i]]
                    else:
                        open_vertices_map[vert_id].append(edge[1-i])
                        open_vertices_map[vert_id].sort()
            if len(faces) > 2:
                non_manifold_edges.append(edge)
        
        myprint("Found %d open edges"%len(open_edges))
        myprint("Found %d non manifold edges"%len(non_manifold_edges))
    
        free_faces = []
        add_faces = []
        for edge in non_manifold_edges:
            for face in edge_map[edge]:
                #bmesh.faces[face].edge_keys\
                open_face_edges = [face_edge for face_edge in 
                                   self.helper.getFaceEdges(obj,face)  
                                   if face_edge in open_edges]
                if len(open_face_edges) == 2:
                    myprint("Found a totally open face")
                    free_faces.append(face)
                    for open_edge in open_face_edges:
                        open_edges.remove(open_edge)
                        for vert_id in open_edge:
                            if len(open_vertices_map[vert_id]) == 1:
                                open_vertices_map.pop(vert_id)
                            else:
                                open_vertices_map[vert_id].pop\
                                            (1-open_edge.index(vert_id))
                if len(open_face_edges) == 1:
                    #bmesh.faces[face].sel = 1
                    self.helper.selectFace(obj,face,select=False)
                    myprint("Found a complex connected face. Selects it!")

        #for vert, edges in open_vertices_map:
        #print open_vertices_map
        open_vertices = sorted(open_vertices_map.keys())
        #print [vert for vert in open_vertices]
        for vert in open_vertices:
            #if vert in open_vertices_map:
            #    print vert, open_vertices_map[vert]
            if vert in open_vertices_map and \
               open_vertices_map[vert][0] in open_vertices_map and \
               open_vertices_map[vert][1] in open_vertices_map and \
               open_vertices_map[open_vertices_map[vert][0]][0] == vert and \
               open_vertices_map[open_vertices_map[vert][1]][0] == vert:
                add_faces.append([vert]+open_vertices_map[vert])
                for vert_ind in open_vertices_map[vert]:
                    open_vertices_map.pop(vert_ind)
                open_vertices_map.pop(vert)
    
        # If not connected all faces
        if open_vertices_map:
            myprint("Found a non trivial connected open edges selects face")
            for vert0, verts in open_vertices_map.items():
                edges = [tuple(sorted([vert0, vert1])) for vert1 in verts]
                for edge in edges:
                    self.helper.selectFace(obj,edge_map[edge][0])
                    #bmesh.faces[edge_map[edge][0]].sel = 1
        
        # Free and add faces
        #self.helper.deleteMeshFaces(obj,faces=free_faces)
        #self.helper.addMeshFaces(obj,add_faces)
        self.helper.updateMesh(obj,vertices=vertices,faces=add_faces)
        #bmesh.faces.delete(1, free_faces)
        #bmesh.faces.extend(add_faces)
        faces = self.helper.getMeshFaces(obj)
        # Remove free vertices
        vert_users = np.zeros(len(vertices))#bmesh.verts))
        for f in faces:#bmesh.faces:
            for v in f:
                vert_users[v] += 1#.index
        meshedges = self.helper.getMeshEdges(obj) 
        for e in meshedges:
            for v in e: 
                vert_users[v] += 1#.index
        
        verts_free = (vert_users==0).nonzero()[0].tolist()
    	
        if verts_free:
            myprint("Removed %s vertices"%len(verts_free))
            self.helper.deleteMeshVertices(obj,vertices=verts_free)
            #bmesh.verts.delete(verts_free)
    
        # Harmonize the normals
        for i in range(len(faces)):#bmesh.faces:
            self.helper.selectFace(obj,i)
        myprint("Recalculate normals")
        self.helper.recalc_normals(obj)
#        bmesh.recalcNormals(0)
        
        # Restore editmode
        self.helper.restoreEditMode(editmode)
        
    def centralize(self):
        # Get selected mesh
        obj = self._get_selected_mesh()
        if obj is None:
            self.waitingCursor(0)
            return
        
        # Ensure editmode is off
        editmode = self.helper.toggleEditMode()
        
        # Grab vertices and Faces
        vertices = self.helper.getMeshVertices(obj)
        
        # Get max and min coordinates
        max_coords = [-1e16]*3
        min_coords = [1e16]*3
        for verts in vertices:
            for i, val in enumerate(verts):
                if val > max_coords[i]:
                    max_coords[i] = val
                if val < min_coords[i]:
                    min_coords[i] = val
        
        # Find midpoint
        midpoint = [(max_coords[i] + min_coords[i])/2 for i in range(3)]
        
        # Centralize the mesh
        for i, verts in enumerate(vertices):
            new_verts = [verts[j]-midpoint[j] for j in range(3)]
            vertices[i] = new_verts
        
        self.helper.updateMesh(obj, vertices)
        self.helper.setTranslation(obj,pos= [0, 0, 0])
        
        # Restore editmode
        self.helper.restoreEditMode(editmode)
        

    def triangulate_holes(self):
        # Get selected mesh
        obj = self._get_selected_mesh()
        if obj is None:
            self.waitingCursor(0)
            return
        bmesh = self.helper.getMeshFrom(obj)

        # Ensure editmode is off
        editmode = self.helper.toggleEditMode()
            
        meshedges = self.helper.getMeshEdges(obj)    
        faces = self.helper.getMeshFaces(obj)
        vertices = self.helper.getMeshVertices(obj)
       
        # Check for non-manifolds and open edges
        edge_map = dict((edge.key, []) for edge in meshedges)#bmesh.edges)
        
        for i,face in enumerate(faces):#bmesh.faces:
            # Unselect all faces
            self.helper.selectFace(obj,edge_map[edge][0],select=False)
            for edge in self.helper.getFaceEdges(obj,face) :#face.edge_keys:
                edge_map[tuple(sorted(edge))].append(i)#face.index
        
        # Build a connectivity map between vertices
        open_edges = []
        vertex_vertex = {}
        for edge, faces in edge_map.items():
            if len(faces) == 1:
                open_edges.append(edge)
                vertex_vertex[edge[0]] = vertex_vertex.get(edge[0], []) + [edge[1]]
                vertex_vertex[edge[1]] = vertex_vertex.get(edge[1], []) + [edge[0]]

        # Sanity checks
        for vertex, neigbors in vertex_vertex.items():
            myprint(vertex, neigbors)
            if neigbors[0] not in vertex_vertex:
                myprint("neigbor not in map:", neigbors[0])
                return
            if neigbors[1] not in vertex_vertex:
                myprint("neigbor not in map:", neigbors[1])
                return
            if len(neigbors) != 2:
                myprint("detected a non closed edge loop at vertex: %d"%vertex)
                return
        
        # Collect edgeloops
        edge_loops = []
        while vertex_vertex:
            edge_loop = []
            first_vertex = vertex_vertex.keys()[0]
            neigbors = vertex_vertex.pop(first_vertex)
            edge_loop.extend([neigbors[0], first_vertex, neigbors[1]])
            while 1:
                vertex = edge_loop[-1]
                if vertex == edge_loop[0]:
                    vertex_vertex.pop(vertex)
                    myprint("Found edge loop:", len(edge_loops), edge_loop)
                    break
                neigbors = vertex_vertex.pop(vertex)
                neigbors.remove(edge_loop[-2])
                edge_loop.append(neigbors[0])
            
            # Append edge loop
            edge_loops.append(edge_loop)

        all_coordinates = []
        # Iterate over the edge loops
        for edge_loop in edge_loops:
            coordinates = np.zeros((len(edge_loop), 3))
            for ind, vertex in enumerate(edge_loop):
                coordinates[ind,:] = vertices[vertex]#bmesh.verts[vertex].co

            # Axis of least and most variation
            axis_least_variation = coordinates.std(0).argmin()
            axis_most_variations = np.fromiter(set(range(3)).difference(\
                [axis_least_variation]), dtype=int)

            # Mean value of the least variation vertices
            mean_new_coord = coordinates[:, axis_least_variation].mean()

            # Get only the coordinates corresponding to the most variations
            trunc_coordinates = coordinates[:, axis_most_variations]

            # Get the distance between all coordinates
            diff_coord = np.diff(trunc_coordinates, axis=0)

            # Get the maximal distance and max area
            max_length = np.sqrt(np.sum(diff_coord**2,1)).max()
            max_area = max_length*max_length*np.sin(np.pi/3)/2

            # Check if start and end points are simimlar
            if np.all(trunc_coordinates[-1] == trunc_coordinates[0]):
                trunc_coordinates = trunc_coordinates[:-1, :].copy()
            else:
                trunc_coordinates = trunc_coordinates.copy()

            num_vertex_in_edge_loop = len(trunc_coordinates)

            # Reshape the coordinates so they corresponds to triangle input
            trunc_coordinates.shape = (num_vertex_in_edge_loop*2,)

            # Trianglulate hole
            surf = gamer.SurfaceMesh(trunc_coordinates, "q20a%f" % max_area)
            
            # Get new vertices
            vertex_offset = len(vertices)#bmesh.verts)
            new_vertices = []
            for i in range(num_vertex_in_edge_loop, surf.num_vertices):

                # Get coordinate for triangulated vertex
                vert = surf.vertex(i)
                new_vertices.append([vert.x, vert.y])

                # Add last 3D coordinate 
                new_vertices[-1].insert(axis_least_variation, mean_new_coord)

            # Get new faces
            new_faces = []
            for face in surf.faces():
                new_face = []

                # Iterate over indices and add correct index
                for index in [face.a, face.b, face.c]:
                    
                    # If index is from old vertex indices
                    if index < num_vertex_in_edge_loop:
                        new_face.append(edge_loop[index])
                    else:
                        new_face.append(vertex_offset + \
                                        index - num_vertex_in_edge_loop)

                new_faces.append(new_face)
            
            # Add the new vertices and faces to the mesh
            faces.extend(new_faces)
            vertices.extend(new_vertices)
            self.helper.updateMesh(obj,vertices=vertices,faces=faces)
#            self.helper.addMeshVertices(obj, new_vertices)
#            self.helper.addMeshFaces(obj, new_faces)
            #or update
            #bmesh.verts.extend(new_vertices)
            #bmesh.faces.extend(new_faces)
            
            all_coordinates.append(coordinates)
        
        # Restore editmode
        self.helper.restoreEditMode(editmode)
        
        try :
            from cPickle import dump
        except :
            from pickle import dump
        dump(dict(edge_loops=edge_loops, coordinates=all_coordinates), \
             open("test_coord.cpickle", "wb"))
            

    def import_surface_mesh_from_file_action(self, filename):
        myprint("filename", filename)        
        # Load options and materials from registry
        self.load_from_registry()
        
        file_type = self.mesh_menu_items[self.getLong(\
            self.mesh_params["surface_mesh_menu"])]
        myprint("file_type", file_type)
        
        # Do the tetrahedralization
        self.waitingCursor(1)
        if file_type == "PDB (Surface)":
            
            gmesh = gamer.read_PDB_molsurf(filename)
            gmesh.centralize()
            self.gamer_to_host(gmesh, {}, filename.replace(".pdb", ""),
                               switch_layer=False)
                    
        elif file_type == "PDB (Gauss)":
            blobbyness = self.getVal(self.mesh_params["Blobbyness"])
            iso_value = self.getVal(self.mesh_params["Iso_value"])
            gmesh = gamer.read_PDB_gauss(filename, blobbyness, iso_value)
            gmesh.centralize()
            self.gamer_to_host(gmesh, {}, filename.replace(".pdb", ""),
                               switch_layer=False)
        elif file_type == "OFF":
            gmesh = gamer.SurfaceMesh(filename)
            self.gamer_to_host(gmesh, {}, filename.replace(".off", ""),
                               switch_layer=False)

        elif file_type == "Lattice":
            myprint("Do nothing...")
        else:
            myprint("Do nothing")

        self.waitingCursor(0)
        
    def tetrahedralize(self):
        # Check we have domains
        if not self.domains:
            self.drawError(errormsg="Expected at least one registered domain")
            return

        if all(domain["as_hole"] for domain in self.domains.values()):
            self.drawError(errormsg="Expected at least one none hole domain ")
            return
        
        # Save all parameters to registry
        self.save_to_registry()
        format_ = self.getLong(self.tetparams["format_menu"])
        self.saveDialog("Tetrahedralize", self.tetrahedralize_action,\
                        suffix="*"+self.tetmesh_suffices[format_])#should be a save dialog


    def tetrahedralize_action(self, filename):
        "Callback function for the tetrahedralize File chooser"

        # Load options and materials from registry
        self.load_from_registry()
        
        # Get gamer mesh
        gmeshes = []
        for i, (name, domain) in enumerate(self.domains.items()):
            obj = self.helper.getObject(name)
            if obj is None:
                self.drawError(errormsg="The domain: '%s' is not a mesh in "\
                               "this scene" % name)
            
            gmesh, boundaries = self.host_to_gamer(obj, False)
            if gmesh is None:
                return

            myprint("\nMesh %d: num verts: %d numfaces: %d" %
                    (i, gmesh.num_vertices, gmesh.num_faces))
            # Set the domain data on the SurfaceMesh
            for name, value in domain.items():
                setattr(gmesh, name, value)
                myprint("%s : %d" %(name, int(value)))

            # Write surface mesh to file for debug
            gmesh.write_off("surfmesh%d.off" % i)

            # Add the mesh
            gmeshes.append(gmesh)
        
        #obj = self._get_selected_mesh(False)
        #if obj is None:
        #    return
        
        # Tetrahedralize mesh
        quality_str = "q%.1fqq%.1faA"%(self.getVal(self.tetparams["aspect_ratio"]),
                                       self.getVal(self.tetparams["dihedral_angle"]))

        myprint("TetGen quality string:", quality_str)
        
        # Do the tetrahedralization
        self.waitingCursor(1)
        gem_mesh = gamer.GemMesh(gmeshes, quality_str)
        
        # Store mesh to files
        format_ = self.tetmesh_formats[self.getLong(self.tetparams["format_menu"])]
        getattr(gem_mesh, "write_%s"%format_)(filename)
        self.waitingCursor(0)
        
        
    def host_to_gamer(self, obj=None, check_for_vertex_selection=True):
        "Transfer the active mesh to a GAMer surface mesh"
        # Take the first one
        #myprint("host_to_gamer ", obj)
        # Get selected mesh
        if obj is None:
            obj = self._get_selected_mesh()
        #myprint("_get_selected_mesh ", obj)
        if obj is None:
            return None, None

        self.waitingCursor(1)
        
        # Grab vertices and Faces
        vertices, selected_vertices = self.helper.getMeshVertices(obj, selected=True)
        vertices = self.helper.getMeshVertices(obj)
        faces = self.helper.getMeshFaces(obj)

        #myprint("verts ",len(vertices), len(faces))
        # Get world location and offset each vertex with this value
        if self.getVal(self.gparams["create_new_mesh"]):
            translation = self.helper.getTranslation(obj)
        else:
            translation = [0., 0., 0.]
            
        # Ensure editmode is off
        editmode = self.helper.toggleEditMode()
        
        # Init gamer mesh
        gmesh = gamer.SurfaceMesh(len(vertices), len(faces))
        def setVert(co, gvert, sel):
            gvert.x = co[0] + translation[0]
            gvert.y = co[1] + translation[1]
            gvert.z = co[2] + translation[2]
            gvert.sel = sel

        # Check we have vertices selected
        if check_for_vertex_selection and not selected_vertices:
            print("No selected vertices")
            return None, None
        
        # If all vertices are selected
        if len(selected_vertices) == len(vertices):
            selected_vertices = np.ones(len(vertices), dtype=bool)
        else:
            selection = np.zeros(len(vertices), dtype=bool)
            selection[selected_vertices] = 1
            selected_vertices = selection
        
        [setVert(*args) for args in zip(vertices, gmesh.vertices(), selected_vertices)]

        # Transfere data from blender mesh to gamer mesh
        for face, gface in zip(faces, gmesh.faces()):
            if len(face) != 3:
                self.drawError(errormsg="expected mesh with only triangles in")
                self.waitingCursor(0)
                self.helper.restoreEditMode(editmode)
                return None, None
            
            gface.a, gface.b, gface.c = face
            gface.m = -1

        # Transfer boundary information
        boundaries = self.helper.getProperty(obj, "boundaries")

        if not boundaries:
            self.helper.setProperty(obj, "boundaries", {})
            boundaries = self.helper.getProperty(obj, "boundaries")
        if boundaries is None :
            boundaries = {}
        # Iterate over the faces and transfer marker information
        for boundary in boundaries.values():
            for face_ind in self._get_boundary_faces(boundary):
                gmesh.face(face_ind).m = boundary["marker"]

        self.waitingCursor(0)
        #myprint(gmesh)
        # Restore editmode
        self.helper.restoreEditMode(editmode)
        return gmesh, boundaries

    def gamer_to_host(self, gmesh, boundaries, mesh_name="gamer_improved",
                      switch_layer=True):
        #myprint("gamer_to_host ",gmesh)
        # Check arguments
        if not isinstance(gmesh, gamer.SurfaceMesh):
            self.drawError(errormsg="expected a SurfaceMesh") 
        
        # Get scene
        scn = self.helper.getCurrentScene()
        self.waitingCursor(1)
        
        verts = [(gvert.x, gvert.y, gvert.z) for gvert in gmesh.vertices()]
        un_selected_vertices = [i for i, gvert in enumerate(gmesh.vertices())
                                if not gvert.sel]
        faces = [(gface.a, gface.b, gface.c) for gface in gmesh.faces()]
        markers = [(i, gface.m) for i, gface in enumerate(gmesh.faces()) \
                   if gface.m != -1]

        # If we create a new mesh we copy the boundaries to a dict
        if self.getVal(self.gparams["create_new_mesh"]):
            new_boundaries = {}
            for boundary_name in boundaries.keys():
                boundary = boundaries[boundary_name]
                new_boundaries[boundary_name] = dict(
                    marker=boundary["marker"], r=boundary["r"], g=boundary["g"], \
                    b=boundary["b"], faces={})
            
            # Do not copy the faces information grab that from the gamer mesh
            boundaries = new_boundaries
        
        # Create marker to boundary map
        face_markers = {}
        for boundary in boundaries.values():
            face_markers[boundary["marker"]] = []

        # Gather all faces of a marker
        for face, marker in markers:
            if marker in face_markers:
                face_markers[marker].append(face)

        # Set the faces of the corresponding boundary
        for boundary in boundaries.values():
            self._set_boundary_faces(boundary, face_markers[boundary["marker"]])
        
        # Ensure editmode is off
        editmode = self.helper.toggleEditMode()

        if self.getVal(self.gparams["create_new_mesh"]):

            # Create new mesh
            #createsNmesh(self,name,vertices,vnormals,faces,color=[1,0,0],
            #                material=None,smooth=True,proxyCol=False, **kw)
            obj, bmesh = self.helper.createsNmesh(mesh_name, verts, None, \
                                                  faces, smooth=0)
            # If not generating a totally new mesh
            switch_to_layer = scn.getLayers()[-1]
            if switch_layer:
                # Switch to another layer
                switch_to_layer += 1
                switch_to_layer = 1 if switch_to_layer > 20 else switch_to_layer

            scn.setLayers([switch_to_layer])
            obj.layers = [switch_to_layer]
            
            self.helper.addObjectToScene(scn, obj)
            self.helper.ObjectsSelection([obj])

            # Set the property dictionary
            # FIXME: Is this safe? Is boundaries always something I can use?
            self.helper.setProperty(obj, "boundaries", boundaries)
        
        else:
            # Get selected mesh
            obj = self._get_selected_mesh()
            #myprint("gamer_to_host_get_selected_mesh ", obj)
            if obj is None:
                self.waitingCursor(0)
                return

            # Update present mesh
            self.helper.updateMesh(obj, vertices=verts, faces=faces)
        
        #myprint("un_selected_vertices ", len(un_selected_vertices))
        self.helper.selectVertices(obj, un_selected_vertices, False)

        # Restore editmode
        self.helper.restoreEditMode(editmode)

        # Repaint boundaries if there were markers in the GAMer data
        if markers:
            self._repaint_boundaries(obj)
        
        self.waitingCursor(0)
        self.updateViewer()

    def action_closure(self, action):
        "Generates an action function"
        assert(action in ["smooth", "refine", "coarse_flat", \
                          "coarse_dense", "normal_smooth"])
        def action_func():
            "The action function"

            gmesh, boundaries = self.host_to_gamer()
            if gmesh is None:
                return
            kwargs = dict((parname, self.getVal(value)) \
                          for parname, value in \
                          self.gparams[action].items())

            getattr(gmesh, action)(**kwargs)
            
            self.gamer_to_host(gmesh, boundaries)

        return action_func
    
    def print_eigenvalues(self, *args):
        gmesh = self.blender_to_gamer()
        if gmesh is None:
            return
        gmesh.eigenvalues()
        
    def _add_float(self, name="float", action=None, init=0.0, mini=0.0, \
                   maxi=1.0, tooltip="", **kwargs):
        call_kwargs = self.elemt_kwargs.copy()
        call_kwargs.update(kwargs)
        return self._addElemt(name=name, action=action, \
                              variable=self.addVariable("float", init),\
                              mini=mini, maxi=maxi, type="sliders",\
                              tooltip=tooltip, label=name,\
                              **call_kwargs)
        
    def _add_int(self, name="int", action=None, init=0, mini=0, maxi=1, \
                 tooltip="", **kwargs):
        call_kwargs = self.elemt_kwargs.copy()
        call_kwargs.update(kwargs)
        return self._addElemt(name=name, action=action, \
                              variable=self.addVariable("int", init),\
                              mini=mini, maxi=maxi, type="slidersInt",\
                              tooltip=tooltip, label=name,\
                              **call_kwargs)
        
    def _add_button(self, name="Button", action=None, tooltip="", **kwargs):
        call_kwargs = self.elemt_kwargs.copy()
        call_kwargs.update(kwargs)
        return self._addElemt(name=name, action=action, type="button", \
                              icon=None, variable=self.addVariable("int",0),\
                              tooltip=tooltip, label=name,\
                              **call_kwargs)

    def _add_check_box(self, name="", action=None, init=0, tooltip="", **kwargs):
        call_kwargs = self.elemt_kwargs.copy()
        call_kwargs.update(kwargs)
        return self._addElemt(name=name, action=action, type="checkbox", \
                              icon=None, variable=self.addVariable("int", init),\
                              tooltip=tooltip, label=name, **call_kwargs)

    def _add_text(self, text, **kwargs):
        call_kwargs = self.elemt_kwargs.copy()
        call_kwargs.update(kwargs)
        return self._addElemt(label=text, **call_kwargs)

    def _get_selected_mesh(self, errorreport=True):
        "Returns the selected mesh"
        objs = self.helper.getCurrentSelection()
        obj = objs[0] if len(objs) else objs
        # myprint(obj)
        # myprint(self.helper.getType(obj))
        if not obj or self.helper.getType(obj) != self.helper.MESH:
            if errorreport:
                self.drawError(errormsg="expected a selected mesh")
            return None
        return obj

mygui = GamerUI()
#call it
mygui.setup()
mygui.display()

#execfile("/Users/ludo/DEV/upy/trunk/upy/examples/upy_gui.py")