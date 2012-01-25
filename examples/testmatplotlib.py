# -*- coding: utf-8 -*-
"""
Created on Mon Sep 19 13:32:59 2011

@author: Ludovic Autin
"""

'''
Make a colorbar as a separate figure.=> JPEG
'''
from matplotlib.figure import Figure
from matplotlib.patches import Polygon
from matplotlib.backends.backend_agg import FigureCanvasAgg
import matplotlib.numerix as nx

figsize = (3,8)
dpi = 80

from matplotlib import mpl
fig = Figure(figsize=figsize)
    
#ax = fig.add_subplot(111)
# Make a figure and axes with dimensions as desired.
#fig = pyplot.figure(figsize=(8,3))
#[left, bottom, width, height] 
ax1 = fig.add_axes([0.05, 0.05, 0.15, 0.9])
ax2 = fig.add_axes([0.65, 0.05, 0.15, 0.9])

# Set the colormap and norm to correspond to the data for which
# the colorbar will be used.
cmap = mpl.cm.cool
norm = mpl.colors.Normalize(vmin=5, vmax=10)

# ColorbarBase derives from ScalarMappable and puts a colorbar
# in a specified axes, so it has everything needed for a
# standalone colorbar.  There are many more kwargs, but the
# following gives a basic continuous colorbar with ticks
# and labels.
cb1 = mpl.colorbar.ColorbarBase(ax1, cmap=cmap,
                                   norm=norm,
                                   orientation='vertical')
cb1.set_label('Energies')

# The second example illustrates the use of a ListedColormap, a
# BoundaryNorm, and extended ends to show the "over" and "under"
# value colors.
cmap = mpl.colors.ListedColormap(['r', 'g', 'b', 'c'])
cmap.set_over('0.25')
cmap.set_under('0.75')

# If a ListedColormap is used, the length of the bounds array must be
# one greater than the length of the color list.  The bounds must be
# monotonically increasing.
bounds = [1, 2, 4, 7, 8]
norm = mpl.colors.BoundaryNorm(bounds, cmap.N)
cb2 = mpl.colorbar.ColorbarBase(ax2, cmap=cmap,
                                     norm=norm,
                                     # to use 'extend', you must
                                     # specify two extra boundaries:
                                     boundaries=[0]+bounds+[13],
                                     extend='both',
                                     ticks=bounds, # optional
                                     spacing='proportional',
                                     orientation='vertical')
cb2.set_label('Discrete intervals, some other units')
# Make the PNG
canvas = FigureCanvasAgg(fig)
# The size * the dpi gives the final image size
#   a4"x4" image * 80 dpi ==> 320x320 pixel image
filename = "/Users/ludo/mw_v_xlogp_ellipses.png"
canvas.print_figure(filename, dpi=dpi)


import DejaVu
DejaVu.enableVBO = False    
from DejaVu import Viewer
vi = Viewer()    
filename = "/Users/ludo/mw_v_xlogp_ellipses.png"
figsize = (3,8)
dpi = 80
import upy
helper = upy.getHelperClass()(master=vi)
plane = helper.plane("plotplane",center=[0.,0.,0.],
                size=[dpi*figsize[0]/10.,dpi*figsize[1]/10.],
                subdivision=(1,1),axis="+Z")#-Z c4d, Z maya
mat = helper.createTexturedMaterial("plot",filename)
helper.assignMaterial(plane,mat,texture=True)


