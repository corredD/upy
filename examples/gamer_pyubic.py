#!BPY
"""
Name: 'GAMer mesh improvments (upy)'
Group: 'Mesh'
Tooltip: 'GAMer mesh improvments, mesh annotations and volumetric mesh generation'
"""
######################################################
# GAMer plugin using upy
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
######################################################
# Importing modules
######################################################
#where is gamer
import sys
#sys.path.pop(1)
#for blender2.5
sys.path.append("/Users/ludo/DEV/py3.2/gamer/lib/python3.2/site-packages")
#for py2.6
#sys.path.append("/Users/ludo/DEV/py2.6/gamer/lib/python2.6/site-packages")
#where is upy
#upypath = "/Users/ludo/DEV/"#"/Library/MGLTools/1.5.6.up/MGLToolsPckgs"
#sys.path.insert(0,upypath)

import upy
upy.setUIClass()

# should have a template ?
from upy import uiadaptor
helperClass = upy.getHelperClass()
print (uiadaptor)
print (helperClass)

import math
import re
try:
    import gamer
except:
    gamer = None
    print ("no gamer")

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
        names.sort()
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
        self.tetmesh_options=["FEtk", "DOLFIN"]
        self.tetmesh_formats=["mcsf", "dolfin"]
        self.tetmesh_suffices=[".m", ".xml.gz"]
        self.tetparams = {} 
        self.buttons = {}
        self.labels = {}
        
        self._layout = []
        self.initWidget(id=10)
        self._all_gui_params = dict(gparams=self.gparams,
                                    mparams=self.mparams,
                                    tetparams=self.tetparams)
        self.setupLayout(kwargs.get("use_meshimprovement", True),\
                         kwargs.get("use_boundary_marking", True),\
                         kwargs.get("use_tetrahedralization", True))

    def CreateLayout(self):
        self._createLayout()
        return 1
    
    def Command(self, *args):
        self._command(args)
        return 1
    
    def setupLayout(self, use_meshimprovement, use_boundary_marking, \
                    use_tetrahedralization):
        "Setup layout dependent on what the user need"
        if use_meshimprovement:
            self.mesh_improvement_layout()
        if use_boundary_marking:
            self.boundary_marking_layout()
        if use_tetrahedralization:
            self.tetrahedralization_layout()
            
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
        self._store("gamer_uiparams", registry_dict)
        #dump(registry_dict, open(join(gettempdir(), \
        #                              "gamer_uiparams.cpickle"), "w"))
        

    def load_from_registry(self):
        from pickle import load
        from tempfile import gettempdir
        from os.path import join
        
        def from_registry(registry_dict, guiparams):
            for key, value in guiparams.items():
                assert(isinstance(value, dict))
                if "id" in value and "name" in value and \
                       key in  registry_dict:
                    self.setVal(value, registry_dict[key])
                else:
                    from_registry(registry_dict[key], value)

        try:
            #d = load(open(join(gettempdir(), "gamer_uiparams.cpickle")))
            d = self._restore("gamer_uiparams")
            from_registry(d, self._all_gui_params)
        except :
            print ("ERROR")
            self.save_to_registry()
        
    def initWidget(self,id=None):
        # Declare UI elements for coarse dense
        self.buttons["coarse_dense"] = self._add_button(\
            "Coarse Dense", action=self.action_closure("coarse_dense"),\
            tooltip="Coarse dense areas of the mesh")
        
        self.gparams["coarse_dense"]["rate"] = self._add_float(\
            "Rate:", mini=0.001, maxi=4.0, init=2.5, step=.05,\
            tooltip="The rate for coarsening dense areas")
        
        self.gparams["coarse_dense"]["numiter"] = self._add_int(\
            "Iter:", mini=1, maxi=15, init=1,\
            tooltip="The number of iteration for coarsening dense areas")
    
        # Declare UI elements for coarse flat
        self.buttons["coarse_flat"] = self._add_button(\
            "Coarse Flat", action=self.action_closure("coarse_flat"),\
            tooltip="Coarse flat areas of the mesh")
        
        self.gparams["coarse_flat"]["rate"] = self._add_float(\
            "Rate:", mini=0.00001, maxi=0.5, init=0.016, step=.01,\
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
            "Iter:", mini=1, maxi=50, init=6,\
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

        # Get any stored Boundaries
        have_boundaries = False
        obj = self._get_selected_mesh()
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
            name="mparams", action=self._update_boundary_name, \
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

        self.tetparams["use_volume_constraint"] = self._add_check_box(\
            "Use volume constraint", tooltip="Use volume constraint, when"\
            " generating tetrahedral mesh", width=self._width)

        self.tetparams["volume_constraint"] = self._add_float(\
            "Vol constr:", mini=.0001, maxi=1000000, action=None, init=100.,\
            tooltip="The minimal aspect ratio", step=1, precision=1.0,\
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

    def mesh_improvement_layout(self):
        frame_info = []
        frame_info.append([self.labels["empty"], \
                           self.labels["coarse_dense"]["rate"],
                           self.labels["coarse_dense"]["numiter"]])
        frame_info.append([self.buttons["coarse_dense"], \
                           self.gparams["coarse_dense"]["rate"], \
                           self.gparams["coarse_dense"]["numiter"]])
        frame_info.append([self.buttons["coarse_flat"], \
                           self.gparams["coarse_flat"]["rate"],\
                           self.labels["empty"]])
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
        frame = self._addLayout(name="Mesh Improvements", elems=frame_info)
        self._layout.append(frame)

    def boundary_marking_layout(self):
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
        frame_info.append([self.buttons["calculate_area"]])
        
        frame = self._addLayout(name="Boundary marking", elems=frame_info)
        self._layout.append(frame)
        
    def tetrahedralization_layout(self):
        frame_info = []
        frame_info.append([self.labels["volume_constraint"], \
                           self.labels["empty"]])
        frame_info.append([self.tetparams["volume_constraint"],\
                           self.tetparams["use_volume_constraint"]])
        frame_info.append([self.labels["dihedral_angle"],\
                           self.labels["aspect_ratio"]])
        frame_info.append([self.tetparams["dihedral_angle"],\
                           self.tetparams["aspect_ratio"]])
        frame_info.append([self.labels["empty"],\
                           self.labels["format_menu"]])
        frame_info.append([self.buttons["tetrahedralize"],\
                           self.tetparams["format_menu"]])
        frame = self._addLayout(name="Tetrahedralization", elems=frame_info)
        self._layout.append(frame)

    
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
        for name, boundary in boundaries.items():
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
#        self.setVal(self.mparams["boundary_menu"], 0)
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
        print ("update menu boundary ",name)
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

    def tetrahedralize(self):
        # Save all parameters to registry
        #self.save_to_registry()
        format_ = self.getLong(self.tetparams["format_menu"])
        self.fileDialog("Tetrahedralize", self.tetrahedralize_action,\
                        suffix="*"+self.tetmesh_suffices[format_])

    def tetrahedralize_action(self, filename):
        "Callback function for the tetrahedralize File chooser"

        # Load options and materials from registry
        #self.load_from_registry()
        
        # Get gamer mesh
        gmesh = self.host_to_gamer()
        if gmesh is None:
            return
        
        obj = self._get_selected_mesh(False)
        if obj is None:
            return
        boundaries = self.helper.getProperty(obj, "boundaries")
        
        # If there are materials defined in the mesh convert the marker information
        # to the gamer mesh
        if boundaries:
            gmesh.reset_face_markers()
            for boundary in list(boundaries.values()):
                for face in self._get_boundary_faces(boundary):
                    gmesh.set_face_marker(face, boundary["marker"])
        
        # Tetrahedralize mesh
        quality_str = "q%.1fqq%.1f"%(self.getVal(self.tetparams["aspect_ratio"]),
                                     self.getVal(self.tetparams["dihedral_angle"]))
        if self.getVal(self.tetparams["use_volume_constraint"]):
            quality_str += "a%.1f"%(self.getVal(self.tetparams["volume_constraint"]))

        # Do the tetrahedralization
        self.waitingCursor(1)
        gem_mesh = gamer.GemMesh(gmesh, quality_str)

        # Store mesh to files
        format_ = self.tetmesh_formats[self.getLong(self.tetparams["format_menu"])]
        getattr(gem_mesh, "write_%s"%format_)(filename)
        self.waitingCursor(0)
        
    def host_to_gamer(self, *args):
        "Transfer the active mesh to a GAMer surface mesh"
        # Take the first one

        # Get selected mesh
        obj = self._get_selected_mesh()
        if obj is None:
            return

        self.waitingCursor(1)
        
        # Grab vertices and Faces
        vertices = self.helper.getMeshVertices(obj)
        faces = self.helper.getMeshFaces(obj)

        # Ensure editmode is off
        editmode = self.helper.toggleEditMode()
        
        # Init gamer mesh
        gmesh = gamer.SurfaceMesh(len(vertices), len(faces))
        def setVert(gvert, co):
            gvert.x, gvert.y, gvert.z = co
        [setVert(gvert, co) for co, gvert in zip(vertices, gmesh.vertices()) ]
        
        # Transfere data from blender mesh to gamer mesh
        for face, gface in zip(faces, gmesh.faces()):
            if len(face) != 3:
                self.drawError(errormsg="expected mesh with only triangles in")
                self.waitingCursor(0)
                self.helper.restoreEditMode(editmode)
                return
            gface.a, gface.b, gface.c = face

        self.waitingCursor(0)
        
        # Restore editmode
        self.helper.restoreEditMode(editmode)
        
        return gmesh

    def gamer_to_host(self, gmesh, mesh_name="gamer_improved"):
        # Check arguments
        if not isinstance(gmesh, gamer.SurfaceMesh):
            raise TypeError("expected a SurfaceMesh")
        
        verts = [(gvert.x, gvert.y, gvert.z) for gvert in gmesh.vertices()]
        faces = [(gface.a, gface.b, gface.c) for gface in gmesh.faces()]

        # Get scene
        scn = self.helper.getCurrentScene()
        self.waitingCursor(1)
        
        # Ensure editmode is off
        editmode = self.helper.toggleEditMode()
        
        if self.getVal(self.gparams["create_new_mesh"]):
            # Switch to another layer
            print (self.helper)
            switch_to_layer = self.helper.getLayer(-1) + 1
            print ("scene switchTo layer ",switch_to_layer)
            switch_to_layer = 1 if switch_to_layer >= 20 else switch_to_layer
            print ("scene switchTo layer ",switch_to_layer)
            self.helper.switchToLayer(switch_to_layer)
            
            # Create new mesh
            #self,name,vertices,vnormals,faces,color=[1,0,0],
            #material=None,smooth=True,proxyCol=False, **kw
            obj, bmesh = self.helper.createsNmesh(mesh_name, verts, None, \
                                                  faces, None, None, False)
            #obj.layers = [switch_to_layer]
            print ("obj switchTo layer ",obj.name,switch_to_layer)
            self.helper.switchToLayer(switch_to_layer,obj=obj)
            self.helper.addObjectToScene(scn, obj)
            self.helper.ObjectsSelection([obj])
        
        else:
            # Get selected mesh
            obj = self._get_selected_mesh()
            if obj is None:
                self.waitingCursor(0)
                return

            # Update present mesh
            self.helper.updateMesh(obj, vertices=verts, faces=faces)
            
        # Restore editmode
        self.helper.restoreEditMode(editmode)
        
        self.waitingCursor(0)
        self.updateViewer()

    def action_closure(self, action):
        "Generates an action function"
        assert(action in ["smooth", "refine", "coarse_flat", \
                          "coarse_dense", "normal_smooth"])
        
        def action_func():
            "The action function"
            gmesh = self.host_to_gamer()
            if gmesh is None:
                return
            kwargs = dict((parname, self.getVal(value)) \
                          for parname, value in \
                          self.gparams[action].items())
            getattr(gmesh, action)(**kwargs)
            self.gamer_to_host(gmesh)

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
        obj = objs[0] if objs else objs
        print(obj)
        #print (self.helper.getType(obj))
        if not obj or self.helper.getType(obj) != self.helper.MESH:
            if errorreport:
                self.drawError(errormsg="expected a selected mesh")
            return None
        return obj

if uiadaptor.host == "tk":
    from DejaVu import Viewer
    vi = Viewer()    
    #require a master   
    gamerui = GamerUI(title = "GAMer")
    gamerui.setup(master=vi)
    	
else :
    gamerui = GamerUI(title = "GAMer")
    gamerui.setup()

#call it
gamerui.display()
#execute in the shell
#execfile("/Users/ludo/DEV/upy/examples/gamer_pyubic.py")