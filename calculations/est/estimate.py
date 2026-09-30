# ============================================================================
#  House 79/K (Mr. Saleem) - Grey structure quantity take-off
#  All dimensions in feet unless noted. Geometry measured from the vector PDFs.
# ============================================================================
import json, math, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from coeff import *
HERE=os.path.dirname(__file__)
GEO=os.path.join(HERE,'..','geo')
FA=json.load(open(os.path.join(GEO,'found_areas.json')))
LAY=FA['layers']; LT=FA['L']

ITEMS=[]     # every BOQ line: dict(sec, item, desc, qty, unit, mat{...}, steel{bar:ft})
def add(sec, item, desc, qty, unit, mat=None, steel=None, note=''):
    ITEMS.append(dict(sec=sec,item=item,desc=desc,qty=qty,unit=unit,mat=mat or {},steel=steel or {},note=note))
def addm(a,b):
    o=dict(a)
    for k,v in b.items(): o[k]=o.get(k,0)+v
    return o

# ---------------------------------------------------------------- levels
NSL_BELOW_ROAD = 1.5        # natural surface 1'-6" below road (as drawn, "as per site")
FFL_ABOVE_ROAD = 2.75       # +2'-9"
FOUND_DEPTH    = 2.5        # PCC bottom 2'-6" below NSL (S-02)
GF_H  = 11.0                # DPC/FFL to FF slab soffit (11'-0" clear, elevations)
SLAB_T= 5.5/12
FF_H  = 12.0 - SLAB_T       # FF slab top to roof slab soffit (floor-to-floor 12')
SF_H  = 9.0 + (1.0-SLAB_T)  # 9'-0" clear + roof build-up
PARA_FF_H = 2.5 + (1.0-SLAB_T)   # 2'-6" parapet above finished terrace
PARA_SF_H = 1.5 + (1.0-SLAB_T)   # 1'-6" parapet on mumty roof

# ============================ A. SUBSTRUCTURE =================================
S='A. Foundations & Plinth'
exc = LAY['pcc']*FOUND_DEPTH
add(S,'A1','Excavation for wall foundations (PCC footprint x 2\'-6" deep below NSL), incl. 10% working space', exc*1.10,'cft',
    note='PCC footprint %.1f sft (types 1-1..4-4 from S-01/S-02)'%LAY['pcc'])
v=LAY['pcc']*0.25
add(S,'A2','P.C.C 1:4:8, 3" thick under footings (widths 2\'-9"/3\'-0"/3\'-6"/2\'-6")',v,'cft',concrete(v,'1:4:8'))
v=LAY['rccf']*0.5
# footing steel: transverse #3@6", longitudinal #3@8"   (cover 1.5")
st3=0
for t,wd in ((1,2.5),(2,2.5),(3,3.0),(4,2.0)):
    L=LT[str(t)]
    trans = (L*12/6+1)*(wd-0.25+0.5)          # bar = width - 2x1.5" cover + 2 hooks
    longi = (math.ceil((wd*12-3)/8)+1)*L*1.05 # 5% laps
    st3 += trans+longi
add(S,'A3','R.C.C 1:2:4 wall footing 6" thick (2\'-6"/2\'-6"/3\'-0"/2\'-0" wide) with #3@6" transverse + #3@8" longitudinal',v,'cft',concrete(v,'1:2:4'),{3:st3})
bf = LAY['b225']*0.5 + LAY['b18']*0.5 + LAY['b135']*1.0
p9=LAY['p9']; share4 = LT['4']/sum(LT.values())
below_pb = p9*(1-share4)*0.5 + p9*share4*1.0
above_pb = p9*(FFL_ABOVE_ROAD)             # plinth beam top = road level, masonry up to FFL (DPC)
add(S,'A4','Brick masonry in foundation 1:6 - stepped footing (22½", 18", 13½") + 9" wall below plinth beam',bf+below_pb,'cft',brickwork(bf+below_pb,'1:6'))
add(S,'A5','Brick masonry 1:6 - 9" plinth wall from plinth beam (road level) to DPC/FFL (2\'-9")',above_pb,'cft',brickwork(above_pb,'1:6'))
v=p9*0.75
Lpb=sum(LT.values())
pb_main = 4*(Lpb*1.05+0.5*30)          # 4#4, 5% laps + end hooks
pb_ring = (Lpb*12/10+1)*2.33           # #2 @10" rings 9x9
add(S,'A6','R.C.C 1:2:4 plinth beam 9"x9" under all walls, 2#4 top + 2#4 bottom, #2@10" rings',v,'cft',concrete(v,'1:2:4'),{4:pb_main,2:pb_ring},
    note='plinth beam centre-line length %.1f ft'%Lpb)
v=p9*0.125
add(S,'A7','D.P.C 1½" thick 1:2:4 at FFL over plinth walls',v,'cft',concrete(v,'1:2:4'))
ext=LT['1']+LT['2']; vd_area=ext*(FFL_ABOVE_ROAD+0.75)
add(S,'A8','Vertical DPC: ¾" plaster 1:3 + 2 coats hot bitumen on inner face of external plinth walls',vd_area,'sft',plaster(vd_area,0.75,'1:3'),
    note='bitumen approx %.0f kg (0.25 kg/sft/coat)'%(vd_area*0.5))
# porch corner column 13.5x13.5 (hatched on S-01; notes specify column RCC 1:1.5:3) - upper estimate as RCC
colH = FOUND_DEPTH-0.75+NSL_BELOW_ROAD+FFL_ABOVE_ROAD+GF_H      # footing top to FF slab soffit
v=1.125*1.125*colH
add(S,'A9','R.C.C column 1:1.5:3 at car-porch front corner 13½"x13½" (%.1f ft high), 4#6 + #3@6" ties'%colH,v,'cft',concrete(v,'1:1.5:3'),{6:4*(colH+2.5),3:(colH*2+1)*4.0})
v=3.0*3.0*1.0
add(S,'A10','Column footing 3\'x3\'x1\' R.C.C 1:2:4 (#4@6" both ways) + 3" P.C.C 1:4:8',v,'cft',addm(concrete(v,'1:2:4'),concrete(3.5*3.5*0.25,'1:4:8')),{4:2*7*2.75})
# earth filling inside plinth
GF_ROOMS = 1362.6                                  # clear floor area inside GF walls (raster of S-01)
floor_build = (1.5+3+4)/12.0
fill_h = NSL_BELOW_ROAD + FFL_ABOVE_ROAD - floor_build
add(S,'A11','Earth filling inside plinth (NSL to underside of sand), compacted in 6" layers - incl. 20% compaction',GF_ROOMS*fill_h*1.2,'cft',
    note='floor area %.0f sft x %.2f ft; NSL assumed 1\'-6" below road (drawings say "as per site")'%(GF_ROOMS,fill_h))
backfill = exc - (LAY['pcc']*0.25+LAY['rccf']*0.5+LAY['b225']*0.5+LAY['b18']*0.5+LAY['b135']*0.75)
add(S,'A12','Back-filling excavated earth around foundations (re-use)',backfill,'cft')
# ============================ B. GF FLOOR BASE ===============================
S='B. Ground-floor sub-floor'
PORCH_A = 13.0*6.37 + 14.9*2.6*0 + 5.9*3.4     # front car porch + entrance landing
BACKPORCH_A = 16.8*8.5
sub = GF_ROOMS+PORCH_A+BACKPORCH_A
add(S,'B1','Sand filling 4" under floors (rooms + car porches)',sub*4/12*1.1,'cft',{'sand_fill':sub*4/12*1.1})
v=sub*0.25
add(S,'B2','P.C.C 1:4:8, 3" thick sub-floor (rooms %.0f + porches %.0f sft)'%(GF_ROOMS,PORCH_A+BACKPORCH_A),v,'cft',concrete(v,'1:4:8'))
fp=(PORCH_A+BACKPORCH_A)*(NSL_BELOW_ROAD+1.25-8/12)*1.2
add(S,'B3','Earth filling under car porches (to porch level +1\'-3")',fp,'cft')

json.dump(dict(),open(os.devnull,'w'))

# ============================ C. SUPERSTRUCTURE WALLS ==========================
# openings: (description, width, height, wall thickness, count, external?)
GF_OPEN=[
 ('S-T lobby rear door',3.5,8,0.75,1,True),('S-T lobby to lobby door',3.5,8,0.75,1,False),
 ('Bed-1 door',3.5,8,0.75,1,False),('M-Bed door',3.5,8,0.75,1,False),('Drawing room door (to porch)',3.5,8,0.75,1,True),
 ('Dining arch opening',6.5,8,0.75,1,False),('Raw-kitchen side door',3.0,8,0.75,1,True),
 ('Main entrance glazed door (5\'-1½" x 20\'-6", GF part)',5.125,GF_H,0.75,1,True),
 ('Bed-1 dress door',2.875,8,0.375,1,False),('Bed-1 bath door',2.5,8,0.375,1,False),('M-Bed dress door',2.5,8,0.375,1,False),
 ('M-Bed bath door',2.5,8,0.375,1,False),('Under-stair store door',2.5,8,0.375,1,False),('Raw to open kitchen door',3.0,8,0.375,1,False),
 ('Powder room door',2.25,8,0.375,1,False),
 ('Bed-1 window',7,7,0.75,1,True),('M-Bed window',7,7,0.75,1,True),('Drawing window',6,7,0.75,1,True),
 ('Dining window (patio)',3.25,7,0.75,1,True),('Raw-kitchen window',3,4.5,0.75,1,True),
 ('TV-lounge front glazing 8\'-6" x 20\' (GF part)',8.5,GF_H-0.5,0.75,1,True),
 ('Ventilators 2\'-6" x 2\'',2.5,2,0.75,3,True),('Exhaust fan openings 1\'x1\'',1,1,0.75,3,True)]
FF_OPEN=[
 ('S-T lobby door',3.5,8,0.75,1,False),('Bed-1 door',3.5,8,0.75,1,False),('M-Bed door',3.5,8,0.75,1,False),
 ('Front bed door',3.5,8,0.75,1,False),('Store door',3.0,8,0.75,1,False),('Kitchen door',3.0,8,0.75,1,False),
 ('Bed-1 dress door',2.875,8,0.375,1,False),('Bed-1 bath door',2.5,8,0.375,1,False),('M-Bed dress door',3.5,8,0.375,1,False),
 ('M-Bed bath door',2.5,8,0.375,1,False),('Front bed dress door',3.0,8,0.375,1,False),('Front bed bath door',2.5,8,0.375,1,False),
 ('Kitchen door/window to terrace 6x8 (sill 6")',6,7.5,0.375,1,True),
 ('Bed-1 window',7,7,0.75,1,True),('M-Bed window',7,7,0.75,1,True),('Front bed side window',7,7,0.75,1,True),
 ('Front bed glazing (upper part of 20\' glazing)',8.5,8.5,0.75,1,True),('TV-lounge window (to open shaft)',8,7,0.75,1,True),
 ('Entrance glazing (upper part)',5.125,8.5,0.75,1,True),
 ('Stair-hall rear windows 3x7',3,7,0.375,2,True),('Stair-hall vertical glazing slot 2\' wide',2,FF_H,0.375,1,True),
 ('Ventilators 2\'-6" x 2\'',2.5,2,0.75,3,True),('Exhaust fan openings 1\'x1\'',1,1,0.75,4,True)]
SF_OPEN=[
 ('Stair-hall door to terrace',3.5,8,0.375,1,True),('Room door',3.5,8,0.75,1,False),('Bath door',2.5,8,0.375,1,False),
 ('Laundry door',2.5,8,0.375,1,False),('Room window 5x7',5,7,0.75,1,True),('Stair-hall rear windows 3x7',3,7,0.375,2,True),
 ('Stair-hall vertical glazing slot',2,SF_H,0.375,1,True),('Bath ventilator',2.5,2,0.75,1,True)]
def open_sum(OP):
    gap=lambda o: not (o[0].startswith('Ventilator') or o[0].startswith('Exhaust') or o[0].startswith('Bath ventilator'))
    w9=sum(o[1]*o[4] for o in OP if o[3]==0.75 and gap(o)); w45=sum(o[1]*o[4] for o in OP if o[3]==0.375 and gap(o))
    v9=sum(o[1]*o[2]*o[4]*0.75 for o in OP if o[3]==0.75); v45=sum(o[1]*o[2]*o[4]*0.375 for o in OP if o[3]==0.375)
    return w9,w45,v9,v45
# lintel schedule per floor (type, length ft, count) - from key plans S-04 + opening sizes
LINT_T={'DL-1':(0.75,4,4,3,6),'WL-1':(0.75,4,4,3,6),'WL&DL-1':(0.75,4,4,3,6),'WL-2':(0.75,6,4,3,6),
        'DL-2':(0.375,4,4,2,6),'WL-3':(0.375,4,4,2,6),'VL-1':(0.75,4,3,3,10)}   # (width, nbars, bar#, ring#, ring spacing in)
RING_LEN={0.75:2.42,0.375:1.58}
LINTELS={
 'GF':[('DL-1',5.0,5),('DL-1',6.63,1),('DL-1',8.0,1),('DL-2',4.375,1),('DL-2',4.0,4),('DL-2',4.5,1),('DL-2',3.75,1),
       ('WL&DL-1',9.37,1),('WL-1',8.69,1),('WL-1',8.84,1),('WL-1',7.5,1),('WL-1',4.75,1),('WL-2',10.34,1),('VL-1',4.0,3)],
 'FF':[('DL-1',5.0,4),('DL-1',4.5,2),('DL-1',5.0,1),('DL-2',4.375,1),('DL-2',4.0,3),('DL-2',5.0,1),('DL-2',4.5,1),
       ('WL-1',8.83,3),('WL-1',6.63,1),('WL-1',8.69,1),('WL-2',10.34,1),('WL-3',3.6,1),('WL-3',4.5,2),('WL-3',8.15,1),('VL-1',4.0,3)],
 'SF':[('DL-1',5.0,1),('DL-2',5.0,1),('DL-2',4.0,2),('WL-1',6.8,1),('WL-3',3.6,1),('WL-3',4.5,2),('VL-1',4.0,1)]}
def lintel_calc(lst):
    vol=0; st={}
    for (t,L,n) in lst:
        b,nb,bar,rb,rs=LINT_T[t]
        vol+=b*0.75*L*n
        st[bar]=st.get(bar,0)+nb*(L+0.5)*n
        st[rb]=st.get(rb,0)+(L*12/rs+1)*RING_LEN[b]*n
    return vol,st
S='C. Brick masonry (superstructure)'
KEY_FF=dict(a9=127.87,a45=48.22)     # net wall plan areas measured on FF key plan (S-04), openings excluded
FLOORS={}
# GF gross plan areas from the foundation network (openings included)
w9,w45,v9,v45=open_sum(GF_OPEN); lv,lst=lintel_calc(LINTELS['GF'])
lv9=sum(LINT_T[t][0]*0.75*L*n for t,L,n in LINTELS['GF'] if LINT_T[t][0]==0.75); lv45=lv-lv9
FLOORS['GF']=dict(A9=FA['gf9'],A45=FA['gf45'],H=GF_H,v9=v9,v45=v45,lv9=lv9,lv45=lv45,bed=9)
w9,w45,v9,v45=open_sum(FF_OPEN); lv,lst=lintel_calc(LINTELS['FF'])
lv9=sum(LINT_T[t][0]*0.75*L*n for t,L,n in LINTELS['FF'] if LINT_T[t][0]==0.75); lv45=lv-lv9
FLOORS['FF']=dict(A9=KEY_FF['a9']+w9*0.75,A45=KEY_FF['a45']+w45*0.375+11*0.375,H=FF_H,v9=v9,v45=v45,lv9=lv9,lv45=lv45,bed=12)
w9,w45,v9,v45=open_sum(SF_OPEN); lv,lst=lintel_calc(LINTELS['SF'])
lv9=sum(LINT_T[t][0]*0.75*L*n for t,L,n in LINTELS['SF'] if LINT_T[t][0]==0.75); lv45=lv-lv9
SF9_L=2.93+12.63+12.13+12.13+5.5+12.63; SF45_L=13.93+7.75+16.86+12.63+5.12+10.0
FLOORS['SF']=dict(A9=SF9_L*0.75,A45=SF45_L*0.375,H=SF_H,v9=v9,v45=v45,lv9=lv9,lv45=lv45,bed=2)
BW={}
for fl,d in FLOORS.items():
    g9=d['A9']*d['H']; g45=d['A45']*d['H']
    n9=g9-d['v9']-d['lv9']-d['bed']*0.5625; n45=g45-d['v45']-d['lv45']
    BW[fl]=(n9,n45)
    name={'GF':'Ground floor','FF':'First floor','SF':'Second floor (mumty/room)'}[fl]
    add(S,'C-'+fl+'9','%s 9" walls, 1:5 - gross %.1f cft (plan %.1f sft x %.2f ft) less openings %.1f, lintels %.1f, bed plates'%(name,g9,d['A9'],d['H'],d['v9'],d['lv9']),n9,'cft',brickwork(n9,'1:5'))
    add(S,'C-'+fl+'45','%s 4½" walls, 1:4 - gross %.1f cft (plan %.1f sft x %.2f ft) less openings %.1f, lintels %.1f'%(name,g45,d['A45'],d['H'],d['v45'],d['lv45']),n45,'cft',brickwork(n45,'1:4'))
PARA_FF_L=125.6; P3=9.75
v=(PARA_FF_L-P3)*0.375*PARA_FF_H + P3*0.75*PARA_FF_H
add(S,'C-P1','Terrace parapets on FF roof (4½", one 9" run) %.1f ft x %.2f ft high, 1:4'%(PARA_FF_L,PARA_FF_H),v,'cft',brickwork(v,'1:4'))
SF_PERIM=94.2
v=SF_PERIM*0.375*PARA_SF_H
add(S,'C-P2','Parapet on mumty roof 4½" %.1f ft x %.2f ft, 1:4'%(SF_PERIM,PARA_SF_H),v,'cft',brickwork(v,'1:4'))
supers=sum(a+b for a,b in BW.values())+ (PARA_FF_L-P3)*0.375*PARA_FF_H + P3*0.75*PARA_FF_H + SF_PERIM*0.375*PARA_SF_H
v=supers*0.05
add(S,'C-E','Elevation features allowance 5% (front frames, fins, piers, profile-light reveals, planters) 1:4',v,'cft',brickwork(v,'1:4'))

# ============================ D. RCC SUPERSTRUCTURE ============================
S='D. R.C.C work (1:2:4 unless noted)'
SLAB={'GF':1705.0,'FF':1650.7,'SF':353.2}
SLAB_NOTE={'GF':'GF roof: outline 1739.1 + porch cantilever 38.7 - stair opening 72.8',
           'FF':'FF roof: outline 1725.0 - stair opening 74.3 (excl. open shaft & terrace)',
           'SF':'Mumty roof: 16.85x7.75 + 17.63x12.63'}
for k,a in SLAB.items():
    v=a*SLAB_T
    add(S,'D-S'+k,'Roof slab 5½" - %s (%.1f sft)'%(SLAB_NOTE[k],a),v,'cft',concrete(v,'1:2:4'))
CB={'CB-1':{'GF':(81.72,5),'FF':(15.5,1)},'CB-2':{'GF':(48.46,5),'FF':(102.02,7),'SF':(30.26,2)}}
for b,d in CB.items():
    for fl,(L,nb) in d.items():
        wd=1.0 if b=='CB-1' else 0.75
        v=L*wd*(4/12)
        if b=='CB-1': st={6:3*(L+1.5*2*nb)*1.03,4:3*(L+1.5*2*nb)*1.03,3:(L*12/7+nb)*3.21}
        else:        st={6:4*(L+1.5*2*nb)*1.03,3:(L*12/6+nb)*2.71}
        add(S,'D-%s-%s'%(b,fl),'%s concealed beam %s x 9½" in %s roof - %d nos, %.1f ft (4" upstand above slab; %s)'%(b,'12"' if wd==1 else '9"',fl,nb,L,'3#6 bottom, 3#4 top, #3@7" rings' if b=='CB-1' else '2#6 top & bottom, #3@6" rings'),v,'cft',concrete(v,'1:2:4'),st)
lin_v=0; lin_st={}
for fl in ('GF','FF','SF'):
    v,st=lintel_calc(LINTELS[fl]); lin_v+=v
    for k2,x in st.items(): lin_st[k2]=lin_st.get(k2,0)+x
    n=sum(x[2] for x in LINTELS[fl])
    add(S,'D-L'+fl,'Door/window/vent lintels %s - %d nos (DL-1, DL-2, WL-1, WL-2, WL-3, VL-1 per S-05)'%(fl,n),v,'cft',concrete(v,'1:2:4'),st)
for fl,n in (('GF',9),('FF',12),('SF',2)):
    v=n*0.75*3.0*0.25
    add(S,'D-BP-'+fl,'Bed plates 9" x 3\'-0" x 3" (1:2:4, 3#4) under beam ends, %s roof - %d nos'%(fl,n),v,'cft',concrete(v,'1:2:4'),{4:n*3*2.75})
# stairs
g1=math.hypot(11*10.5/12,12*6.57/12); g2=math.hypot(9*10.5/12,10*6.57/12)
waist=(g1+g2)*3.5*0.5; land=8.25*3.5*0.5; steps=21*0.5*(10.5/12)*(6.57/12)*3.5
per=waist+land+steps
st_per={4:2*10*((g1+3)+(g2+3)) + 2*nbars(8.25,5)*5.5, 3:(nbars(g1,9)+nbars(g2,9)+nbars(g1,12)+nbars(g2,12))*3.25 + nbars(3.5,7)*8.75+nbars(3.5,12)*8.75}
for fl,lab in (('GF','GF to FF'),('FF','FF to 2nd floor')):
    add(S,'D-ST-'+fl,'Zig-zag stair %s: 6" waist (flights %.2f + %.2f ft), 6" landing 8\'-3"x3\'-6", 21 concrete steps; riser 6.57", tread 10½", width 3\'-6"'%(lab,g1,g2),per,'cft',concrete(per,'1:2:4'),dict(st_per))
v=4.5*3*0.667+3.5*2*0.5
add(S,'D-SF','Stair base footing + stem (8" slab, #4@6" both ways; stem #4@5")',v,'cft',concrete(v,'1:2:4'),{4:180.75})
v=5*3.5*0.25
add(S,'D-SP','P.C.C 1:4:8 under stair footing',v,'cft',concrete(v,'1:4:8'))
shL=4.5+8+8+6
for fl,L in (('GF',12.5),('FF',8.0),('SF',6.0)):
    v=L*1.25*(4/12)
    add(S,'D-SH-'+fl,'R.C.C sunshade (chajja) %s: %.1f ft long x 1\'-3" projection, 4"-3" thick, #3@6" main'%(fl,L),v,'cft',concrete(v,'1:2:4'),{3:nbars(L,6)*2.75+3*L})
add(S,'D-PR','Provisional: front elevation canopy / RCC fins & projections',20.0,'cft',concrete(20,'1:2:4'),{3:150})
v=(PARA_FF_L+SF_PERIM)*0.75*0.25
add(S,'D-CP','Parapet coping 3" x 9" (1:2:4) with 2#3',v,'cft',concrete(v,'1:2:4'),{3:2*(PARA_FF_L+SF_PERIM)*1.05})

# ------------------------------------------------ slab reinforcement schedules
# (id, bar#, spacing in, distribution width ft, bar length ft, kind)  B=bottom (alt. straight/cranked), T=extra top, E=pairs
SL_GF=[('B1',3,8,14.59,13.40,'B'),('B2',3,9,13.33,14.79,'B'),('B3',3,7,14.84,8.25,'B'),('B4',3,10,8.58,14.67,'B'),
 ('B5',3,8,13.59,16.14,'B'),('B6',3,6,16.33,13.54,'B'),('B7',3,10,4.58,46.13,'B'),('B8',3,8,43.71,5.75,'B'),
 ('B9',3,6,46.83,13.75,'B'),('B10',3,10,12.58,13.57,'B'),('B11',3,10,12.58,5.56,'B'),('B12',3,8,12.58,14.14,'B'),
 ('B13',3,10,12.58,8.61,'B'),('B14',4,10,12.96,9.29,'B'),
 ('T1',3,8,14.59,4.16,'T'),('T2',4,10,15.32,6.5,'T'),('T3',4,10,13.44,5.17,'T'),('T4',3,8,8.67,6.83,'T'),('T5',3,8,4.25,4.5,'T'),
 ('T6',3,10,8.58,4.5,'T'),('T7',3,8,8.67,13.17,'T'),('T8',4,10,13.59,7.25,'T'),('T9',4,10,3.96,4.58,'T'),('T10',3,10,11.58,4.16,'T'),
 ('T11',3,8,16.42,12.84,'T'),('T12',3,10,12.32,4.91,'T'),('T13',3,8,6.96,6.25,'T'),('T14',3,10,5.96,3.33,'T'),('T15',3,10,17.96,3.92,'T'),
 ('T16',3,10,3.15,3.33,'T'),('T17',3,8,11.71,6.25,'T'),('T18',3,10,22.96,3.92,'T'),('T19',3,10,12.58,5.26,'T'),('T20',3,10,12.58,8.17,'T'),
 ('T21',3,10,12.58,7.17,'T'),('T22',4,10,12.96,7.54,'T')]
SL_GF_E=[(6,2*2.75),(6,2*(4.03+2.17)),(6,2*7.56),(6,2*8.38),(6,2*6.5),(4,2*4.24),(4,2*9.49),(4,2*6.0)]
SL_FF=[('B1',3,8,14.96,14.31,'B'),('B2',3,9,13.58,14.78,'B'),('B3',3,7,14.84,8.25,'B'),('B4',3,10,8.58,14.67,'B'),
 ('B5',3,8,13.59,16.15,'B'),('B6',3,6,16.33,13.54,'B'),('B7',3,7,18.33,11.72,'B'),('B8',3,8,18.33,7.10,'B'),
 ('B9',3,10,11.58,17.88,'B'),('B10',3,10,5.21,19.5,'B'),('B11',3,8,14.33,12.0,'B'),('B12',3,8,13.21,14.25,'B'),
 ('B13',3,6,19.58,14.83,'B'),('B14',3,8,13.2,19.0,'B'),
 ('T1',3,8,14.96,5.7,'T'),('T2',3,10,13.58,4.5,'T'),('T3',4,10,13.58,9.17,'T'),('T4',4,10,14.96,6.5,'T'),('T5',4,10,8.58,5.17,'T'),
 ('T6',4,10,10.33,7.83,'T'),('T7',4,10,13.59,7.25,'T'),('T8',4,10,4.58,4.7,'T'),('T9',3,10,11.33,4.16,'T'),('T10',3,10,12.32,4.92,'T'),
 ('T11',4,10,4.58,7.5,'T'),('T12',4,10,12.08,8.84,'T'),('T13',3,10,18.33,3.67,'T'),('T14',3,8,18.33,6.0,'T'),('T15',3,8,18.33,6.41,'T'),
 ('T16',3,10,17.96,5.67,'T'),('T17',3,10,6.21,9.55,'T'),('T18',3,10,13.2,4.33,'T'),('T19',4,10,18.33,7.16,'T'),('T20',3,8,13.44,7.38,'T'),
 ('T21',3,8,5.73,4.16,'T'),('T22',4,8,14.9,5.0,'T'),('T23',3,10,13.2,5.67,'T')]
SL_FF_E=[(4,2*7.55),(6,2*9.0),(4,2*4.61)]
SL_SF=[('B1a',3,8,16.28,7.75,'B'),('B1b',3,8,16.67,11.87,'B'),('B2a',3,10,10.71,17.25,'B'),('B2b',3,10,6.58,16.7,'B'),
 ('T1',3,10,16.06,3.33,'T'),('T2',3,10,16.06,3.34,'T'),('T3',3,10,15.71,3.5,'T'),('T4',3,10,15.71,3.5,'T'),
 ('T5',3,10,10.71,4.67,'T'),('T6',3,10,10.71,6.5,'T'),('T7',3,10,6.58,4.75,'T')]
SLAB_SCHED={'GF':(SL_GF,SL_GF_E),'FF':(SL_FF,SL_FF_E),'SF':(SL_SF,[])}
SLAB_ROWS={}
for fl,(rows,extra) in SLAB_SCHED.items():
    st={}; out=[]
    for (i,bar,s,Wd,L,k) in rows:
        n=nbars(Wd,s); Lb=L+(0.6 if k=='B' else 0.3)
        st[bar]=st.get(bar,0)+n*Lb; out.append((i,bar,s,Wd,L,k,n,n*Lb))
    for bar,ft in extra: st[bar]=st.get(bar,0)+ft
    chairs=SLAB[fl]/12*1.5; st[3]=st.get(3,0)+chairs
    SLAB_ROWS[fl]=out
    kg=sum(steel_lb(b,f) for b,f in st.items())*KG_PER_LB
    add('E. Slab reinforcement','E-'+fl,'Slab steel %s roof (%d bar sets incl. cranked, extra top, trimmer 2#6/2#4 & chairs) - %.2f kg/sft'%(fl,len(rows)+len(extra),kg/SLAB[fl]),SLAB[fl],'sft',None,st)

# ============================ F. PLASTER ============================
S='F. Plaster (grey-structure finish)'
FLOORLEN={'GF':(FA['gf9']/0.75,FA['gf45']/0.375,GF_H,133.4,40.3),
          'FF':(FLOORS['FF']['A9']/0.75,FLOORS['FF']['A45']/0.375,FF_H,142.0,36.0),
          'SF':(SF9_L,SF45_L,SF_H,81.6,12.63)}
OPS={'GF':GF_OPEN,'FF':FF_OPEN,'SF':SF_OPEN}
int_tot=0; ext_tot=0
for fl,(l9,l45,H,ext_l,pl_l) in FLOORLEN.items():
    gross=(l9+l45)*2*H; plf=pl_l*H; ext=ext_l*H; inn=gross-plf-ext
    od_i=0; od_e=0; rev=0
    for (d,w,h,t,n,isext) in OPS[fl]:
        if isext: od_e+=w*h*n; od_i+=w*h*n
        else: od_i+=2*w*h*n
        rev+=(2*h+w)*t*n
    inn_n=inn-od_i+rev*0.6; ext_n=ext-od_e+rev*0.4
    if fl=='GF': ext_n+=ext_l*(FFL_ABOVE_ROAD+0.5)   # exposed plinth
    int_tot+=inn_n; ext_tot+=ext_n
    add(S,'F-I'+fl,'Internal plaster ½" 1:4 - %s walls (gross %.0f sft, less openings, plus reveals)'%(fl,inn),inn_n,'sft',plaster(inn_n,0.5,'1:4'))
    add(S,'F-E'+fl,'External plaster ¾" 1:4 - %s outer faces%s'%(fl,' incl. exposed plinth' if fl=='GF' else ''),ext_n,'sft',plaster(ext_n,0.75,'1:4'))
pa=PARA_FF_L*(PARA_FF_H*2+0.75)+SF_PERIM*(PARA_SF_H*2+0.75)
add(S,'F-P','Parapet plaster ¾" 1:4 both faces + coping',pa,'sft',plaster(pa,0.75,'1:4'))
ceil=(SLAB['GF']-FA['gf9']-FA['gf45'])+(SLAB['FF']-FLOORS['FF']['A9']-FLOORS['FF']['A45'])+(SLAB['SF']-FLOORS['SF']['A9']-FLOORS['SF']['A45'])
ceil+=2*(g1+g2+8.25)*3.5+shL*1.25*2
add(S,'F-C','Ceiling plaster ⅜" 1:3 (slab soffits, stair soffits, shades)',ceil,'sft',plaster(ceil,0.375,'1:3'))
v=(1705.0-245.0+353.2-68.0)*0.25
add('B. Ground-floor sub-floor','B4','Upper-floor sub-base: 3" P.C.C 1:4:8 over FF floor & mumty floor (levels 4" upstand CB beams, covers conduits)',v,'cft',concrete(v,'1:4:8'))

# ============================ G. BOUNDARY WALLS ============================
S='G. Boundary walls, gates pillars & external works'
BWALL=[('Front panels (1\'-6"+15\'-2"+3\'+3\'-11" splay)',23.59,6.0),('Left side short panel',3.0,6.0),
       ('Left side long panel (42\'-3¼"+1\'-6")',43.77,7.25),('Back boundary wall (assumed, not detailed)',37.26,7.0),
       ('Right side at back passage & driveway (assumed)',14.4,6.5)]
Lpan=sum(x[1] for x in BWALL); Lpil=7*1.125+3*4.0; Lf=Lpan+Lpil
v=Lf*2.25*2.5*1.1
add(S,'G1','Excavation for boundary wall & pillar foundations 2\'-3" wide x 2\'-6" deep (%.1f ft run)'%Lf,v,'cft')
v=Lf*2.25*0.25
add(S,'G2','P.C.C 1:4:8 3" under boundary wall foundation',v,'cft',concrete(v,'1:4:8'))
v=Lf*(1.875*0.5+1.5*0.5+1.125*0.5)
add(S,'G3','Brick masonry 1:6 stepped foundation (22½", 18", 13½" x 6" each)',v,'cft',brickwork(v,'1:6'))
v=Lf*0.75*0.5
add(S,'G4','R.C.C 1:2:4 plinth band / DPC beam 9"x6" at plinth level, 4#3 + #2@9" rings',v,'cft',concrete(v,'1:2:4'),{3:4*Lf*1.05,2:(Lf*12/9+1)*1.83})
wall=sum(L*0.75*(H+0.75-0.5) for _,L,H in BWALL)
pil=7*1.125*1.125*(6.5+0.75-0.5)+3*4.0*1.125*(6.5+0.75-0.5)
add(S,'G5','Brick masonry 1:5 boundary wall 9" (%.1f ft of panels, 6\'-0" to 7\'-3" above road)'%Lpan,wall,'cft',brickwork(wall,'1:5'))
add(S,'G6','Brick pillars 1:4 - 7 nos 13½"x13½" + 3 nos 4\'-0"x13½" feature pillars, 6\'-6" high',pil,'cft',brickwork(pil,'1:4'))
v=Lpan*1.0*0.25+10*1.5*1.5*0.25
add(S,'G7','R.C.C coping 3" on wall panels + pillar caps (1:2:4), 2#3',v,'cft',concrete(v,'1:2:4'),{3:2*Lpan*1.05})
bpl=(23.59+3.0)*6.75*2+43.77*8.0*2+(37.26+14.4)*7.0+7*4*1.125*7.25+3*(2*4+2*1.125)*7.25+Lpan*1.5
add(S,'G8','Boundary wall plaster ¾" 1:4 (both faces road side, inner face on neighbour side, pillars, top)',bpl,'sft',plaster(bpl,0.75,'1:4'))
v=15*0.75*2.5
add(S,'G9','Lawn toe walls 9" (approx. 15 ft x 2\'-6") 1:5 + 3" PCC base',v,'cft',addm(brickwork(v,'1:5'),concrete(15*1.5*0.25,'1:4:8')))
add(S,'G10','Entrance / porch / rear-door steps (brick 1:5, provisional)',40.0,'cft',addm(brickwork(40,'1:5'),concrete(20,'1:4:8')),note='incl. 20 cft PCC 1:4:8 treads base')

# ============================ H. SEPTIC TANK & MANHOLES ============================
S='H. Septic tank & manholes'
add(S,'H1','Septic tank excavation (internal 6\'-0" x 4\'-0" x 5\'-6" deep, 2 chambers)',8.5*6.5*6.75,'cft',
    note='drawing shows ~4\'-10" x 3\'-5" overall; enlarged to standard size for ~12 users (upper estimate)')
add(S,'H2','P.C.C 1:4:8 3" base',8.0*6.0*0.25,'cft',concrete(8.0*6.0*0.25,'1:4:8'))
add(S,'H3','R.C.C 1:2:4 base slab 6" (#3@6" both ways)',7.5*5.5*0.5,'cft',concrete(7.5*5.5*0.5,'1:2:4'),{3:171})
v=23*5.5+2*4.0*4.5*0.375
add(S,'H4','Brick masonry 1:4 - 9" walls + two 4½" baffle walls',v,'cft',brickwork(v,'1:4'))
v=7.5*5.5*(5/12)-2*2*2*(5/12)
add(S,'H5','R.C.C 1:2:4 cover slab 5" with 2 manhole openings (#3@6" both ways + trimmers)',v,'cft',concrete(v,'1:2:4'),{3:195})
add(S,'H6','Plaster ¾" 1:3 with water-proofing compound inside septic tank',206,'sft',plaster(206,0.75,'1:3'))
NMH=9
add(S,'H7','Manholes / inspection chambers - %d nos 2\'x2\' internal, avg 3\'-6" deep: excavation'%NMH,NMH*4.5*4.5*4.25,'cft')
add(S,'H8','Manholes: P.C.C 1:4:8 4" base',NMH*3.5*3.5*0.333,'cft',concrete(NMH*3.5*3.5*0.333,'1:4:8'))
add(S,'H9','Manholes: 9" brick walls 1:4',NMH*11*3.5,'cft',brickwork(NMH*11*3.5,'1:4'))
add(S,'H10','Manholes: benching/channels 1:2:4',NMH*1.5,'cft',concrete(NMH*1.5,'1:2:4'))
add(S,'H11','Manholes: inside plaster ½" 1:3',NMH*32,'sft',plaster(NMH*32,0.5,'1:3'))
add(S,'H12','Manholes: R.C.C cover slabs 3" (#3@6" both ways)',NMH*2.75*2.75*0.25,'cft',concrete(NMH*2.75*2.75*0.25,'1:2:4'),{3:NMH*35})

# ============================ I. OVERHEAD WATER TANK ============================
S='I. Overhead water tank (R.C.C, 1000 gallons)'
add(S,'I1','R.C.C 1:1.5:3 overhead tank internal 8\'x5\'x4\'-6" (1000 imp. gal): 6" base, 6" walls, 4" top',27+63+16.7,'cft',concrete(106.7,'1:1.5:3'),{3:1336.5},
    note='drawings show tank position only (5\'-4"x3\'-1" symbol) on mumty roof; engineer to confirm support')
add(S,'I2','Brick support walls/piers under tank 9" 1:4 (provisional)',45,'cft',brickwork(45,'1:4'))
add(S,'I3','Tank plaster: inside ¾" 1:3 water-proof (197 sft) + outside ½" 1:4 (204 sft)',401,'sft',addm(plaster(197,0.75,'1:3'),plaster(204,0.5,'1:4')))

# ============================ J. SERVICES (pipes) ============================
SW=json.load(open(os.path.join(GEO,'sewer_runs.json')))
LEG=5.33
sew5 = SW['24']['5in']-LEG + 20.0                       # + connection to road sewer
sew4_h = (SW['24']['4in']-LEG)+(SW['25']['4in']-LEG)+(SW['26']['4in']-LEG)
sew3_h = (SW['24']['3in']-LEG)+(SW['25']['3in']-LEG)+(SW['26']['3in']-LEG)
soil_stack = 3*13 + 1*25 + 4*4                           # FF 3 baths, 2F bath, vent pipes above roof
waste_stack = 4*13 + 2*25                                # FF baths+kitchen, 2F bath+laundry
rwp = 38 + 29 + 29 + 16                                  # 4 rain-water down pipes (mumty roof, 2 terrace sumps, front terrace)
PIPES=[]
def pipe(group,size,desc,ft,basis):
    PIPES.append(dict(group=group,size=size,desc=desc,ft=ft,ft_w=ft*(1+W_PIPE),basis=basis))
pipe('Sewerage (UPVC)','5"','Main sewer: rear manholes -> side passage -> septic tank -> road sewer; car-porch MH -> septic tank',sew5,
     'measured on sewerage drawing (GF %.1f ft) + 20 ft street connection'%(SW['24']['5in']-LEG))
pipe('Sewerage (UPVC)','4"','WC connections GF/FF/2F (horizontal %.1f ft) + soil stacks 3x13 ft (FF), 1x25 ft (2F) + 4 vent pipes x 4 ft'%sew4_h,sew4_h+soil_stack,'measured + vertical stacks')
pipe('Sewerage (UPVC)','3"','Floor traps, basins, showers, sinks (horizontal %.1f ft) + waste stacks 4x13 ft + 2x25 ft'%sew3_h,sew3_h+waste_stack,'measured + vertical stacks')
pipe('Rain water (UPVC)','3"','4 rain-water down pipes in 9"x6" ducts (38+29+29+16 ft)',rwp,'roof sumps on roof plans')
WR=json.load(open(os.path.join(GEO,'water_runs.json')))
cold_h=WR['28']['cold_0.12']+WR['29']['cold_0.12']+WR['30']['cold_0.12']+WR['31']['cold_0.12']
hot_h=WR['28']['hot_0.12']+WR['29']['hot_0.12']+(WR['30']['hot_0.12']-35)
gas_h=(WR['28']['gas_0.12']-26)+(WR['29']['gas_0.12']-14)+WR['30']['gas_0.12']
pipe('Water supply (PPR)','1"-1¼"','Tank down-take to GF (38 ft) + pump rising main to tank (40 ft) + floor mains (40 ft)',118,'vertical risers')
pipe('Water supply (PPR)','¾"','Cold water branch lines (measured on sanitary drawings)',cold_h,'measured GF/FF/2F/roof')
pipe('Water supply (PPR)','½"','Cold fixture drops 35 points x 4 ft',140,'fixture count')
pipe('Hot water (PPR)','¾"','Hot water lines (measured) + geyser risers 36 ft',hot_h+36,'measured')
pipe('Hot water (PPR)','½"','Hot fixture drops 20 points x 4 ft',80,'fixture count')
pipe('Gas (GI/PPR-gas)','½"-¾"','Gas lines to kitchens, geyser, heaters (measured) + riser from meter 30 ft',gas_h+30,'measured')
# electrical conduits
PTS=dict(GF=dict(light=53,socket=41,ac=5,sb=18),FF=dict(light=47,socket=30,ac=4,sb=16),SF=dict(light=15,socket=8,ac=1,sb=5))
Lp=sum(p['light'] for p in PTS.values()); Sp=sum(p['socket'] for p in PTS.values()); SB=sum(p['sb'] for p in PTS.values())
ac_ft=5*45+4*30+1*40
E34 = Lp*12 + Sp*8 + 25*30 + 0.10*Lp*12
E1  = SB*25 + ac_ft + 30
E15 = 85
pipe('Electrical conduit (PVC)','¾"','Light/fan points %d x 12 ft + socket points %d x 8 ft + 25 low-voltage runs x 30 ft (TV, net, CCTV, intercom, bells) + 10%% UPS circuits'%(Lp,Sp),E34,'point count from electrical drawings')
pipe('Electrical conduit (PVC)','1"','DB to %d switch-boards x 25 ft + %d A.C points (%d ft) + earthing 30 ft'%(SB,sum(p['ac'] for p in PTS.values()),ac_ft),E1,'point count')
pipe('Electrical conduit (PVC)','1½"','Meter to main DB + risers to FF & 2F DBs',E15,'layout')

# ============================ SUMMARY ============================
def summarize(items):
    tot=dict(cement_bags=0,sand_conc=0,sand_mortar=0,crush=0,bricks=0,sand_fill=0)
    steel={}
    for it in items:
        m=it['mat']
        tot['cement_bags']+=m.get('cement_bags',0)
        tot['crush']+=m.get('crush',0)
        tot['bricks']+=m.get('bricks',0)
        tot['sand_fill']+=m.get('sand_fill',0)
        if m.get('crush',0)>0: tot['sand_conc']+=m.get('sand',0)
        else: tot['sand_mortar']+=m.get('sand',0)
        for b,ft in it['steel'].items(): steel[b]=steel.get(b,0)+ft
    return tot,steel
def steel_kg(steel): return {b:steel_lb(b,ft)*KG_PER_LB for b,ft in steel.items()}
SECTIONS=[]
for it in ITEMS:
    if it['sec'] not in SECTIONS: SECTIONS.append(it['sec'])
SEC_SUM={}
for s in SECTIONS:
    t,st=summarize([i for i in ITEMS if i['sec']==s]); SEC_SUM[s]=(t,steel_kg(st))
TOT,STEEL=summarize(ITEMS); STEEL_KG=steel_kg(STEEL)
if __name__=='__main__':
    for it in ITEMS:
        m=it['mat']; kg=sum(steel_kg(it['steel']).values())
        print(f"{it['item']:7s} {it['qty']:9.1f} {it['unit']:4s} cem {m.get('cement_bags',0):7.1f} sand {m.get('sand',0):8.1f} crush {m.get('crush',0):8.1f} bricks {m.get('bricks',0):8.0f} steel {kg:7.1f}kg | {it['desc'][:90]}")
    print()
    for s,(t,k) in SEC_SUM.items():
        print(f"{s:45s} cement {t['cement_bags']:7.1f} bags | sand(conc) {t['sand_conc']:7.1f} | sand(mortar) {t['sand_mortar']:7.1f} | crush {t['crush']:7.1f} | bricks {t['bricks']:8.0f} | steel {sum(k.values()):7.1f} kg")
    print()
    print("TOTAL (net):",{k:round(v,1) for k,v in TOT.items()})
    print("STEEL kg by bar:",{k:round(v,1) for k,v in STEEL_KG.items()},"total",round(sum(STEEL_KG.values()),1))
