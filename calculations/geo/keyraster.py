import json, numpy as np, cv2
from scipy import ndimage as ndi
def raster(T, ppi=6, pad=30, Wft=39.0, Hft=56.0, xoff=1.0, yoff=1.0, maxR_in=7.5):
    s=ppi*12
    W=int(Wft*s)+2*pad; H=int(Hft*s)+2*pad
    img=np.zeros((H,W),np.uint8)
    for (x1,y1,x2,y2) in T:
        cv2.line(img,(int(round((x1+xoff)*s))+pad,int(round((y1+yoff)*s))+pad),(int(round((x2+xoff)*s))+pad,int(round((y2+yoff)*s))+pad),255,1)
    lines=img>0
    free=(~lines).astype(np.uint8)
    n,lab=cv2.connectedComponents(free,connectivity=4)
    dt=cv2.distanceTransform(free,cv2.DIST_L2,5)
    mx=ndi.maximum(dt,lab,index=np.arange(n))
    ext=lab[0,0]
    good=np.zeros(n,bool)
    for i in range(1,n):
        if i!=ext and mx[i]/ppi<=maxR_in: good[i]=True
    good[0]=False
    wall=good[lab]&~lines
    bnd=(cv2.dilate(wall.astype(np.uint8),np.ones((3,3),np.uint8))>0)&lines
    full=wall|bnd
    r=int(3.4*ppi)
    k=cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(2*r+1,2*r+1))
    t9=cv2.morphologyEx(full.astype(np.uint8),cv2.MORPH_OPEN,k)>0
    t45=full&~t9
    a_tot=(wall.sum()+0.5*bnd.sum())/(ppi*ppi)/144
    a9=(t9&wall).sum()+0.5*(t9&bnd).sum(); a45=(t45&wall).sum()+0.5*(t45&bnd).sum()
    return dict(total=a_tot, a9=a9/(ppi*ppi)/144, a45=a45/(ppi*ppi)/144), full, t9, s, pad
