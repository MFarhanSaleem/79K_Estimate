import pymupdf, math, collections, json, os
# path to the architectural working-drawings PDF (sheets 01-24)
d=pymupdf.open(os.environ.get("WORKING_DRAWINGS_PDF", "79-K_WORKING_DRAWINGS_.pdf"))
def segs_by_color(pg, colors, width=None):
    p=d[pg-1]; out=collections.defaultdict(list)
    for g in p.get_drawings():
        if g['type']!='s' or not g.get('color'): continue
        col=tuple(round(c,2) for c in g['color']); w=round(g.get('width') or 0,2)
        if col in colors and (width is None or w==width):
            for it in g['items']:
                if it[0]=='l': out[colors[col]].append((it[1].x,it[1].y,it[2].x,it[2].y))
    return out
def merge_runs(segs, ang_tol=2.0, gap_tol=12.0, off_tol=1.2):
    # group collinear segments (same direction & line offset), merge along the line if gap < gap_tol
    items=[]
    for (x1,y1,x2,y2) in segs:
        L=math.hypot(x2-x1,y2-y1)
        if L<0.3: continue
        ang=math.degrees(math.atan2(y2-y1,x2-x1))%180
        items.append((ang,x1,y1,x2,y2,L))
    used=[False]*len(items); runs=[]
    for i,(a,x1,y1,x2,y2,L) in enumerate(items):
        if used[i]: continue
        used[i]=True
        ux,uy=math.cos(math.radians(a)),math.sin(math.radians(a))
        nx,ny=-uy,ux
        off=x1*nx+y1*ny
        ts=[(x1*ux+y1*uy),(x2*ux+y2*uy)]
        members=[(min(ts),max(ts))]
        changed=True
        while changed:
            changed=False
            for j,(b,p1,q1,p2,q2,M) in enumerate(items):
                if used[j]: continue
                da=min(abs(b-a),180-abs(b-a))
                if da>ang_tol: continue
                if abs(p1*nx+q1*ny-off)>off_tol: continue
                t=sorted([p1*ux+q1*uy,p2*ux+q2*uy])
                lo=min(m[0] for m in members); hi=max(m[1] for m in members)
                if t[0]<=hi+gap_tol and t[1]>=lo-gap_tol:
                    members.append((t[0],t[1])); used[j]=True; changed=True
        lo=min(m[0] for m in members); hi=max(m[1] for m in members)
        runs.append(dict(ang=round(a,1),len=hi-lo,n=len(members),start=(lo*ux+off*nx,lo*uy+off*ny),end=(hi*ux+off*nx,hi*uy+off*ny)))
    return runs
