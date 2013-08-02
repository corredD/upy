# -*- coding: utf-8 -*-
"""
Created on Tue Nov  1 15:27:38 2011

@author: Michel Sanner - TSRI
"""


SMALL_NUM = 0.00000001 #anything that avoids division overflow
from math import fabs

## intersect_RayTriangle(): intersect a ray with a 3D triangle
##    Input:  a ray R, and a triangle T
##    Returns -1, None = triangle is degenerate (a segment or point)
##             0, None = disjoint (no intersect)
##             1, I    = intersect in unique point I
##             2, None = are in the same plane


def intersect_RayTrianglePy( ray, Triangle):
    point1 = ray[0]
    point2 = ray[1]
    # get triangle edge vectors and plane normal
    t0 = Triangle[0]
    t1 = Triangle[1]
    t2 = Triangle[2]
    u = [ t1[0]-t0[0], t1[1]-t0[1], t1[2]-t0[2] ] 
    v = [ t2[0]-t0[0], t2[1]-t0[1], t2[2]-t0[2] ]
    # cross product
    n = ( u[1]*v[2]-u[2]*v[1], u[2]*v[0]-u[0]*v[2], u[0]*v[1]-u[1]*v[0])
    if n[0]*n[0]+n[1]*n[1]+n[2]*n[2]<SMALL_NUM:   # triangle is degenerate
        return -1,None                            # do not deal with this case

    # ray direction vector
    dir = ( point2[0]-point1[0], point2[1]-point1[1], point2[2]-point1[2])
    w0 = ( point1[0]-t0[0], point1[1]-t0[1], point1[2]-t0[2] )
    a = -n[0]*w0[0] - n[1]*w0[1] - n[2]*w0[2]
    b = n[0]*dir[0] + n[1]*dir[1] + n[2]*dir[2]
    if fabs(b) < SMALL_NUM:  # ray is parallel to triangle plane
        if a == 0:           # ray lies in triangle plane
            return 2,None
        else:
            return 0 ,None   # ray disjoint from plane

    # get intersect point of ray with triangle plane
    r = a / b
    if r < 0.0:      # ray goes away from triangle => no intersect
        return 0,None

    #if r > 1.0:      # segment too short => no intersect
    #    return 0,None
    # intersect point of ray and plane
    I = (point1[0] + r*dir[0], point1[1] + r*dir[1], point1[2] + r*dir[2] )

    # is I inside Triangle?
    uu = u[0]*u[0]+u[1]*u[1]+u[2]*u[2]
    uv = u[0]*v[0]+u[1]*v[1]+u[2]*v[2]
    vv = v[0]*v[0]+v[1]*v[1]+v[2]*v[2]
    w = ( I[0] - t0[0], I[1] - t0[1], I[2] - t0[2] )
    wu = w[0]*u[0]+w[1]*u[1]+w[2]*u[2]
    wv = w[0]*v[0]+w[1]*v[1]+w[2]*v[2]
    D = uv * uv - uu * vv

    # get and test parametric coords
    s = (uv * wv - vv * wu) / D
    if s < 0.0 or s > 1.0:        # I is outside Triangle
        return 0,None
    t = (uv * wu - uu * wv) / D
    if t < 0.0 or (s + t) > 1.0:  # I is outside Triangle
        return 0,None

    return 1, I                   # I is in Triangle

try:
    from geomutils.geomalgorithms import intersect_RayTriangle
except ImportError:
    print ("shapefit.intersect_RayTriangle.py: defaulting  to python implementation")

    intersect_RayTriangle = intersect_RayTrianglePy


def intersectRayPolyhedron( pol, pt1, pt2):
    # compute intersection points between a polyhedron defined by a list
    # of triangles (p0, p1, p2) and a ray starting at pt1 and going through pt2
    inter = []
    interi = []
    ray = [list(pt1), list(pt2)]
    for ti, t in enumerate(pol):
        interPt = intersect_RayTriangle(ray, t)
        #if status==1:
        inter.append(interPt)
        interi.append(ti)
    if len(inter)>1:  # find closest to pt1
        mini=9999999999.0
        miniInd = None 
        for i, p in enumerate(inter):
            v = ( p[0]-pt1[0], p[1]-pt1[1], p[2]-pt1[2] )
            d = v[0]*v[0]+v[1]*v[1]+v[2]*v[2]
            if d < mini:
                mini = d
                interPt = inter[i]
                tind = interi[i]
    return tind, interPt

def intersectRayPolyhedronPy( pol, pt1, pt2):
    # compute intersection points between a polyhedron defined by a list
    # of triangles (p0, p1, p2) and a ray starting at pt1 and going through pt2
    inter = []
    interi = []
    ray = [list(pt1), list(pt2)]
    for ti, t in enumerate(pol):
        status,interPt = intersect_RayTrianglePy(ray, t)
        if status==1:
            inter.append(interPt)
            interi.append(ti)
    if len(inter)>1:  # find closest to pt1
        mini=9999999999.0
        miniInd = None 
        for i, p in enumerate(inter):
            v = ( p[0]-pt1[0], p[1]-pt1[1], p[2]-pt1[2] )
            d = v[0]*v[0]+v[1]*v[1]+v[2]*v[2]
            if d < mini:
                mini = d
                interPt = inter[i]
                tind = interi[i]
    return tind, interPt

def IndexedPolgonsToTriPoints(geom,transform=True):
    verts = geom.getVertices()
    tri = geom.getFaces()
    assert tri.shape[1]==3
    triv = []
    for t in tri:
       triv.append( [verts[i].tolist() for i in t] )
    return triv

#from upy.intersect_RayTriangle import intersectRayPolyhedron, IndexedPolgonsToTriPoints
#triP = IndexedPolgonsToTriPoints(geom)
#res = intersectRayPolyhedron( triP, facesCenter, peomCenter)
#
