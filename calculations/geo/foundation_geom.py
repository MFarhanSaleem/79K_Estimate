import sys, math, os
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from gf_network import W
from shapely.geometry import LineString, Polygon, box
from shapely.ops import unary_union
from shapely.affinity import translate
PL_X=37.256   # right property line (outer face of type-1 walls)
def strip(w, width, inner_offset=0.0):
    """Buffered strip of given width around wall centerline, flat caps extended by half width to fill junctions.
    For type-1 (eccentric) walls the strip is shifted inward so its outer edge stays on the property line."""
    x1,y1,x2,y2=w[1],w[2],w[3],w[4]
    L=math.hypot(x2-x1,y2-y1); ux,uy=(x2-x1)/L,(y2-y1)/L
    ext=min(width/2, 1.6)
    a=(x1-ux*ext, y1-uy*ext); b=(x2+ux*ext, y2+uy*ext)
    ls=LineString([a,b]).buffer(width/2, cap_style=2, join_style=2)
    if inner_offset: ls=translate(ls, xoff=-inner_offset)
    return ls
def layer(width_by_type, clip_extend=True):
    polys=[]
    for w in W:
        t=w[6]; wd=width_by_type[t]
        if wd<=0: continue
        off=0.0
        if t==1:   # eccentric: outer face at property line; centre of strip = PL - wd/2
            off=(w[1]-(PL_X-wd/2))
        polys.append(strip(w, wd, off))
    return unary_union(polys)
# only extend to junctions: to avoid overshoot at free ends we clip to hull of buffered network
net=unary_union([LineString([(w[1],w[2]),(w[3],w[4])]).buffer(3.0,cap_style=2) for w in W])
def A(width_by_type): return layer(width_by_type).intersection(net).area
