import json, re, math
R=json.load(open('geo/rebar_raw.json'))
S=json.load(open('geo/slab_raw.json'))
U=33.053
frames={'6':(105.56,548.73),'7':(105.56,548.73),'8':(105.5474,429.72)}
WT={2:0.167,3:0.376,4:0.668,5:1.043,6:1.502}   # lb/ft
def analyze(pg, verbose=True):
    x0,y0=frames[pg]
    B=json.load(open(f'geo/bars_{pg}.json'))
    # thin dimension lines (solid, long) in feet
    thin=[]
    for (X1,Y1,X2,Y2) in S[pg]['dims']:
        L=math.hypot(X2-X1,Y2-Y1)
        if L>1.5: thin.append((X1,Y1,X2,Y2))
    labels=[]
    for (t,X,Y,dr) in R[pg]['texts']:
        m=re.match(r'#(\d)@(\d+)"',t)
        if m: labels.append(dict(bar=int(m.group(1)),s=int(m.group(2)),X=X,Y=Y,horiz=abs(dr[0])>0.5,txt=t))
    # bars: H = along X (y,x0,x1,n), V = along Y (x,y0,y1,n)
    H=[h for h in B['H'] if h[2]-h[1]>1.5]; V=[v for v in B['V'] if v[2]-v[1]>1.5]
    solidH=[h for h in H if h[3]==1]; solidV=[v for v in V if v[3]==1]
    dashH=[h for h in H if h[3]>1]; dashV=[v for v in V if v[3]>1]
    rows=[]
    for L in labels:
        # dimension line parallel to text, near label
        best=None
        for (X1,Y1,X2,Y2) in thin:
            if L['horiz'] and abs(Y1-Y2)<0.02:
                dy=Y1-L['Y']
                if -0.2<dy<0.7 and min(X1,X2)-0.2<=L['X']<=max(X1,X2)+0.2:
                    if best is None or dy<best[0]: best=(dy,min(X1,X2),max(X1,X2),Y1)
            if (not L['horiz']) and abs(X1-X2)<0.02:
                dx=X1-L['X']
                if -0.2<dx<0.7 and min(Y1,Y2)-0.2<=L['Y']<=max(Y1,Y2)+0.2:
                    if best is None or dx<best[0]: best=(dx,min(Y1,Y2),max(Y1,Y2),X1)
        if best is None:
            rows.append(dict(L=L,W=None)); continue
        _,a,b,pos=best; W=b-a
        # bars perpendicular to the dimension line crossing it: horizontal dim line => vertical bars (V)
        cand=[]
        if L['horiz']:
            for v in solidV:
                if a-0.1<=v[0]<=b+0.1 and v[1]-0.3<=pos<=v[2]+0.3: cand.append(v)
        else:
            for h in solidH:
                if a-0.1<=h[0]<=b+0.1 and h[1]-0.3<=pos<=h[2]+0.3: cand.append(h)
        rows.append(dict(L=L,W=W,span=(a,b),pos=pos,bars=[(round(c[0],2),round(c[1],2),round(c[2],2)) for c in cand]))
    return rows, dashH, dashV, solidH, solidV
if __name__=='__main__':
    import sys
    pg=sys.argv[1]
    rows,dH,dV,sH,sV=analyze(pg)
    for r in rows:
        L=r['L']
        print(f"{L['txt']:>10} @({L['X']:.2f},{L['Y']:.2f}) {'H' if L['horiz'] else 'V'}  W={r['W'] and round(r['W'],2)} span={r.get('span') and tuple(round(v,2) for v in r['span'])} pos={r.get('pos') and round(r['pos'],2)} bars={r.get('bars')}")
    print("dashed H:",[(round(h[0],2),round(h[1],2),round(h[2],2)) for h in dH])
    print("dashed V:",[(round(v[0],2),round(v[1],2),round(v[2],2)) for v in dV])
