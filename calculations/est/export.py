import json, math, os, sys
sys.path.insert(0, os.path.dirname(__file__))
import estimate as E
from coeff import *
OUT={}
# ---------- stage mapping
def stage(it):
    i=it['item']
    if i.startswith(('A',)): return '1. Foundation & plinth'
    if i.startswith('B'): return '5. Plaster, sub-floors & floor bases'
    if i.startswith('F'): return '5. Plaster, sub-floors & floor bases'
    if i.startswith(('G','H')): return '6. External works (boundary, septic, manholes)'
    if i.startswith('I'): return '4. Mumty (2F), parapets & roof tank'
    if i in ('C-P1','C-P2','C-E','D-CP','D-PR'): return '4. Mumty (2F), parapets & roof tank'
    for fl,st in (('GF','2. Ground-floor walls & GF roof'),('FF','3. First-floor walls & FF roof'),('SF','4. Mumty (2F), parapets & roof tank')):
        if i.endswith(fl) or ('-'+fl) in i or i.endswith(fl+'9') or i.endswith(fl+'45') or i=='E-'+fl: return st
    if i in ('D-SF','D-SP'): return '2. Ground-floor walls & GF roof'
    return '2. Ground-floor walls & GF roof'
for it in E.ITEMS: it['stage']=stage(it)
STAGES=sorted(set(it['stage'] for it in E.ITEMS))
def mats(items):
    t,st=E.summarize(items); kg=E.steel_kg(st)
    return dict(cement=t['cement_bags'],sand_c=t['sand_conc'],sand_m=t['sand_mortar'],sand_f=t['sand_fill'],crush=t['crush'],bricks=t['bricks'],steel=kg)
OUT['stages']=[(s,mats([i for i in E.ITEMS if i['stage']==s])) for s in STAGES]
OUT['sections']=[(s,mats([i for i in E.ITEMS if i['sec']==s])) for s in E.SECTIONS]
OUT['total']=mats(E.ITEMS)
# ---------- items
OUT['items']=[]
for it in E.ITEMS:
    m=it['mat']; kg=sum(E.steel_kg(it['steel']).values())
    OUT['items'].append(dict(sec=it['sec'],item=it['item'],desc=it['desc'],qty=it['qty'],unit=it['unit'],
        cement=m.get('cement_bags',0),sand=m.get('sand',0)+m.get('sand_fill',0),crush=m.get('crush',0),bricks=m.get('bricks',0),steel=kg,
        steel_by={str(b):E.steel_lb(b,f)*KG_PER_LB for b,f in it['steel'].items()},note=it['note'],stage=it['stage']))
# ---------- steel by component and bar
comp={}
for it in E.ITEMS:
    for b,f in it['steel'].items():
        k=it['sec']; comp.setdefault(k,{}); comp[k][b]=comp[k].get(b,0)+E.steel_lb(b,f)*KG_PER_LB
OUT['steel_comp']={k:{str(b):v for b,v in d.items()} for k,d in comp.items()}
# ---------- geometry appendices
sys.path.insert(0,os.path.join(os.path.dirname(__file__),'..','geo'))
from gf_network import W
OUT['walls']=[(w[0],w[7],w[5],w[6],math.hypot(w[3]-w[1],w[4]-w[2]),(round(w[1],2),round(w[2],2),round(w[3],2),round(w[4],2))) for w in W]
OUT['layers']=E.LAY; OUT['L']=E.LT
OUT['openings']={'GF':E.GF_OPEN,'FF':E.FF_OPEN,'SF':E.SF_OPEN}
OUT['lintels']=E.LINTELS
OUT['slab_rows']=E.SLAB_ROWS; OUT['slabs']=E.SLAB; OUT['slab_note']=E.SLAB_NOTE
OUT['cb']={b:{fl:v for fl,v in d.items()} for b,d in E.CB.items()}
OUT['floors']={k:{kk:vv for kk,vv in v.items()} for k,v in E.FLOORS.items()}
OUT['heights']=dict(GF=E.GF_H,FF=E.FF_H,SF=E.SF_H,PFF=E.PARA_FF_H,PSF=E.PARA_SF_H)
OUT['pipes']=E.PIPES
OUT['points']=E.PTS
# ---------- optional items (NOT in totals)
opt=[]
area_roof=(1650.7-353.2)+353.2
bed=area_roof/12*DRY_MORTAR; m1=mortar_dry(bed,'1:4')
opt.append(dict(item='O1',desc='Roof insulation/treatment on terrace & mumty roof (%.0f sft): polythene sheet, 4" earth (mud) compacted, 1½" brick tiles in 1" cement mortar 1:4, pointing 1:3'%area_roof,
    cement=m1['cement_bags']+8,sand=m1['sand']+24,crush=0,bricks=math.ceil(area_roof*3.3*1.05),steel=0,other='Polythene %.0f sft; earth %.0f cft'%(area_roof*1.1,area_roof*4/12*1.2)))
ugt_c=concrete(170,'1:1.5:3'); pcc=concrete(12,'1:4:8')
opt.append(dict(item='O2',desc='Underground water tank 1,500 gallons (internal 8\'x6\'x5\'): R.C.C 1:1.5:3 walls/base/top ~170 cft, PCC 12 cft, #3/#4 steel ~400 kg, excavation ~520 cft, inside water-proof plaster',
    cement=ugt_c['cement_bags']+pcc['cement_bags']+4,sand=ugt_c['sand']+pcc['sand']+15,crush=ugt_c['crush']+pcc['crush'],bricks=0,steel=400,other='Excavation ~520 cft'))
pv=concrete(430*0.25,'1:4:8')
opt.append(dict(item='O3',desc='External paving base: side & rear passages + driveway (~430 sft) 3" P.C.C 1:4:8 over 3" sand',
    cement=pv['cement_bags'],sand=pv['sand']+430*0.25,crush=pv['crush'],bricks=0,steel=0,other=''))
OUT['optional']=opt
json.dump(OUT,open(os.path.join(os.path.dirname(__file__),'estimate.json'),'w'),indent=1,default=float)
t=OUT['total']
print("TOTAL net: cement %.1f, sand conc %.1f, sand mortar %.1f, fill %.1f, crush %.1f, bricks %.0f, steel %.1f kg"%(t['cement'],t['sand_c'],t['sand_m'],t['sand_f'],t['crush'],t['bricks'],sum(t['steel'].values())))
for s,m in OUT['stages']: print(s, round(m['cement'],1), round(m['bricks']), round(sum(m['steel'].values()),1))
