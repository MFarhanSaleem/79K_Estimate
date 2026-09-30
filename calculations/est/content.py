import json, math, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from coeff import *
D=json.load(open(os.path.join(os.path.dirname(__file__),'estimate.json')))
B=[]   # blocks
def blk(**k): B.append(k)
def f0(x): return f"{x:,.0f}"
def f1(x): return f"{x:,.1f}"
def f2(x): return f"{x:,.2f}"
def up(x,step): return math.ceil(x/step-1e-9)*step
def ftin(ft):
    f=int(ft); i=round((ft-f)*12,1)
    if i>=12: f+=1; i-=12
    s=f"{i:.1f}".rstrip('0').rstrip('.')
    return f"{f}'-{s}\""
T=D['total']; ST=T['steel']
W=dict(cement=1+W_CEMENT,sand=1+W_SAND,crush=1+W_CRUSH,bricks=1+W_BRICK,steel=1+W_STEEL)
P=dict(PORTRAIT=9906, LANDSCAPE=15038)
steel_net=sum(ST.values())
bar_name={'2':'6 mm (#2) - rings/stirrups','3':'10 mm (#3)','4':'12 mm (#4)','6':'20 mm (#6)'}
proc_steel={b:up(v*W['steel'],10) for b,v in ST.items()}
proc_steel_tot=sum(proc_steel.values())
cement_p=up(T['cement']*W['cement'],10); bricks_p=up(T['bricks']*W['bricks'],1000)
crush_p=up(T['crush']*W['crush'],50); sandc_p=up(T['sand_c']*W['sand'],50); sandm_p=up(T['sand_m']*W['sand'],50); sandf_p=up(T['sand_f'],50)
items={i['item']:i for i in D['items']}
earth=items['A11']['qty']+items['B3']['qty']
exc_all=items['A1']['qty']+items['G1']['qty']+items['H1']['qty']+items['H7']['qty']
bitumen=items['A8']['qty']*0.5
surplus_bank=(items['A1']['qty']/1.10-items['A12']['qty'])+(items['G2']['qty']+items['G3']['qty'])+7.5*5.5*6.4+9*3.5*3.5*4.25
surplus_loose=surplus_bank*1.25
earth_import=max(0,earth-surplus_loose)
pipes=D['pipes']

# =============================== COVER ===============================
blk(type='section',orientation='PORTRAIT')
blk(type='cover',title='GREY STRUCTURE MATERIAL ESTIMATE',
    subtitle='Double-storey house with mumty (2nd-floor room) - Plot No. 79/K',
    lines=[('Client','Mr. Saleem'),('Architect','Faisal Associates, WAPDA City, Faisalabad - working drawings sheets 01-24 (16-08-2026)'),
           ('Structural engineer','Fakhar Associates - M. Fakhar Iqbal Sheikh (PEC Civil 11697), drawings 2026/L-20/S-01 to S-09 (14-08-2026)'),
           ('Covered area (as per drawings)','Ground 1,898 sft + First 1,844 sft + Second 362 sft = 4,104 sft'),
           ('Scope','Complete grey structure from excavation to roof parapet: foundations, plinth, brickwork, all R.C.C, steel, plaster, sub-floors, boundary walls, septic tank, manholes, overhead water tank, sewerage / rain-water / water-supply / gas pipes and electrical conduits'),
           ('Estimate basis','Upper estimate - quantities measured from the vector drawing files, upper end of standard coefficient ranges, standard wastage added'),
           ('Date','30 September 2026')],
    keys=[('Cement',f0(cement_p),'bags (50 kg)'),('Bricks',f0(bricks_p),'nos'),('Steel (Grade 60)',f"{proc_steel_tot/1000:,.2f}",'tons'),
          ('Crush',f0(crush_p),'cft'),('Sand (all)',f0(sandc_p+sandm_p+sandf_p),'cft')])
blk(type='pagebreak')

# =============================== 1. SUMMARY ===============================
blk(type='h1',text='1. Final material requirement (what to buy)')
blk(type='p',text='The quantities below are the total for the complete grey structure described on the cover, including standard wastage. Where a standard gives a range, the upper value has been used, as requested. "Net" is the measured quantity; "To procure" is the net quantity plus wastage, rounded up. Fill in your local rates to get the cost.')
rows=[]
def r(n,mat,net,wp,proc,unit,guide,kind=None):
    d={'cells':[n,mat,net,wp,proc,unit,guide,'','']}
    if kind: d['kind']=kind
    rows.append(d)
r('1','Cement (OPC, 50 kg bag)',f0(T['cement']),'5%',f0(cement_p),'bags','Buy fresh stock per stage; do not store more than 4-6 weeks')
r('2','Bricks - 1st class burnt clay (9" x 4½" x 3")',f0(T['bricks']),'5%',f0(bricks_p),'nos','Standard 13.5 bricks per cft of brickwork')
for b in ('3','4','6','2'):
    r('3'+{'3':'a','4':'b','6':'c','2':'d'}[b],'Steel Grade 60 deformed - '+bar_name[b],f0(ST[b]),'5%',f0(proc_steel[b]),'kg','Laps & hooks already included in net')
r('3','Steel - TOTAL',f0(steel_net),'5%',f0(proc_steel_tot),'kg',f"= {proc_steel_tot/1000:.2f} metric tons",'subtotal')
r('4','Binding wire (annealed, 18 gauge)',f0(steel_net*0.01),'-',f0(up(steel_net*0.01*1.05,5)),'kg','About 10 kg per ton of steel')
r('5','Crush / coarse aggregate (¾" down)',f0(T['crush']),'5%',f0(crush_p),'cft',f"≈ {crush_p/100:.0f} tractor-trolleys of 100 cft")
r('6','Sand for concrete (Chenab / Lawrencepur)',f0(T['sand_c']),'10%',f0(sandc_p),'cft','Coarse clean sand for RCC & PCC')
r('7','Sand for masonry mortar & plaster (Ravi)',f0(T['sand_m']),'10%',f0(sandm_p),'cft','Fine sand; sieve for plaster')
r('8','Fill sand under ground floors (4")',f0(T['sand_f']),'incl.',f0(sandf_p),'cft','Any clean sand / Ravi sand')
r('9','Earth filling (plinth + porches, compacted)',f0(earth),'incl. 20%',f0(up(earth,50)),'cft',f"Re-use ~{f0(math.floor(surplus_loose/100)*100)} cft surplus excavated earth; import about {f0(up(earth,50)-math.floor(surplus_loose/100)*100)} cft")
r('10','Bitumen (hot, vertical DPC 2 coats)',f0(bitumen),'5%',f0(up(bitumen*1.05,10)),'kg','Inner face of external plinth walls')
_pc={'11':0,'12':0}
def _plab(g):
    k='11' if 'Electrical' not in g else '12'
    _pc[k]+=1
    return k+'abcdefghijklmnop'[_pc[k]-1]
for p in pipes:
    L=20 if 'UPVC' in p['group'] or 'PPR' in p['group'] or 'GI' in p['group'] else 10
    r(_plab(p['group']),f"{p['group']} {p['size']}",f0(p['ft']),'10%',f0(math.ceil(p['ft_w'])),'ft',f"≈ {math.ceil(p['ft_w']/L)} lengths of {L} ft")
blk(type='table',header=['#','Material','Net qty','Waste','To procure','Unit','Remarks / purchase guide','Rate (Rs)','Amount (Rs)'],
    widths=[470,2430,880,760,980,580,1906,860,1040],align=['C','L','R','C','R','C','L','R','R'],rows=rows,font=8)
blk(type='note',text='Pipe lengths are for pipes only; fittings, manhole covers, boxes and accessories are listed in Sections 7 and 8. Optional items (roof insulation with brick tiles, underground water tank, external paving) are NOT included above - see Section 9.')

# =============================== 2. STAGE-WISE ===============================
blk(type='h1',text='2. Stage-wise requirement (order material in phases)')
blk(type='p',text='Buying material stage by stage reduces theft, damage and cement ageing. Quantities include wastage.')
rows=[]
tot=dict(c=0,b=0,s=0,cr=0,sc=0,sm=0)
for s,m in D['stages']:
    c=m['cement']*W['cement']; b=m['bricks']*W['bricks']; stl=sum(m['steel'].values())*W['steel']; cr=m['crush']*W['crush']; sc=m['sand_c']*W['sand']; sm=(m['sand_m']+m['sand_f'])*W['sand']
    for k,v in zip(('c','b','s','cr','sc','sm'),(c,b,stl,cr,sc,sm)): tot[k]+=v
    rows.append({'cells':[s,f0(c),f0(b),f0(stl),f0(cr),f0(sc),f0(sm)]})
rows.append({'cells':['TOTAL (incl. wastage)',f0(tot['c']),f0(tot['b']),f0(tot['s']),f0(tot['cr']),f0(tot['sc']),f0(tot['sm'])],'kind':'total'})
blk(type='table',header=['Stage','Cement (bags)','Bricks (nos)','Steel (kg)','Crush (cft)','Concrete sand (cft)','Mortar/plaster & fill sand (cft)'],
    widths=[3006,1100,1200,1100,1100,1150,1250],align=['L','R','R','R','R','R','R'],rows=rows,font=8.5)

# =============================== 3. PROJECT DATA ===============================
blk(type='h1',text='3. Project data read from the drawings')
L=D['L']; lay=D['layers']; h=D['heights']
rows=[
 ['Structural system','Load-bearing brick masonry (9" external & main walls, 4½" partitions) with 5½" R.C.C slabs; concealed beams CB-1 (12" x 9½") and CB-2 (9" x 9½") carry first-floor walls that do not sit on ground-floor walls; one R.C.C column at the car-porch front corner'],
 ['Plot / building','Plot about 37\' wide x 65\' deep (left boundary skewed); building 37\'-3" x 51\'-7" on ground floor; corner plot with main gate (front) and side gate (left)'],
 ['Levels','Road ±0; car porch +1\'-3"; finished floor +2\'-9"; floor-to-floor 12\'-0" (11\'-0" clear + 1\'-0" slab band); mumty 9\'-0" clear; terrace parapet 2\'-6"; mumty parapet 1\'-6". Natural surface level "as per site" - taken 1\'-6" below road as drawn'],
 ['Specifications (S-01 notes)','Deformed steel Grade 60; slab & beam R.C.C 1:2:4 (3000 psi); column R.C.C 1:1.5:3 (4000 psi); covers: slab ¾", beams, columns & foundation 1½"; foundation masonry 1:6; P.C.C 1:4:8; D.P.C 1½" 1:2:4 with vertical DPC (¾" plaster 1:3 + 2 coats hot bitumen)'],
 ['Foundation types (S-02)','1-1 external property-line wall (eccentric): P.C.C 2\'-9" x 3", R.C.C footing 2\'-6" x 6"; 2-2 external walls: P.C.C 3\'-0", footing 2\'-6"; 3-3 internal 9" walls: P.C.C 3\'-6", footing 3\'-0"; 4-4 4½" walls: P.C.C 2\'-6", footing 2\'-0". Footing steel #3@6"/#3@8". Brick steps 22½" (6"), 18" (6"), 13½" (12"), 9" wall; plinth beam 9"x9" 2#4+2#4, #2@10" rings; depth 2\'-6" below NSL'],
 ['Measured foundation lengths',f"Type 1-1: {L['1']:.1f} ft; type 2-2: {L['2']:.1f} ft; type 3-3: {L['3']:.1f} ft; type 4-4: {L['4']:.1f} ft; total centre-line {sum(L.values()):.1f} ft (38 wall runs - Appendix A)"],
 ['Slabs (S-06/07/08)',f"5½\" thick. GF roof {D['slabs']['GF']:,.1f} sft; FF roof {D['slabs']['FF']:,.1f} sft; mumty roof {D['slabs']['SF']:,.1f} sft (net of stair openings, open shaft and terrace)"],
 ['Concealed beams',f"CB-1: GF roof 81.7 ft (5 beams) + FF roof 15.5 ft (1); CB-2: GF roof 48.5 ft (5) + FF roof 102.0 ft (7) + mumty roof 30.3 ft (2); 23 bed plates 9\"x3'x3\" (3#4)"],
 ['Stair (S-03 + sheet 06/07)','Zig-zag (dog-legged), 2 flights per storey, 22 risers of 6.57", treads 10½", width 3\'-6", 6" waist with #4@5" main bars, #3@9"/12" distribution, 6" landing, base footing'],
 ['Lintels (S-04/S-05)','DL-1 9"x9" 4#4 #3@6"; DL-2 4½"x9" 4#4 #2@6"; WL-1 9"x9" 4#4; WL-2 9"x9" 2#4+4#4; WL-3 4½"x9"; WL&DL-1 9"x9"; VL-1 9"x9" 4#3 #3@10". Key plans show 21 (GF), 24 (FF) and 6 (2F) lintels'],
 ['Wall heights used',f"GF {ftin(h['GF'])} (DPC to slab soffit); FF {ftin(h['FF'])}; mumty {ftin(h['SF'])}; terrace parapet {ftin(h['PFF'])}; mumty parapet {ftin(h['PSF'])} (from slab top, incl. roof build-up)"],
 ['Services on drawings','Sewerage in 3"/4"/5" UPVC with 9 manholes and septic tank connected to main sewer; 4 rain-water pipes in 9"x6" ducts; cold/hot water & gas lines (sheets 21-24); electrical layout with legend (sheets 13-16); overhead water tank on mumty roof'],
]
blk(type='table',header=['Item','Data used in this estimate'],widths=[2300,7606],align=['L','L'],rows=[{'cells':r} for r in rows],font=8.5)

# =============================== 4. METHOD ===============================
blk(type='h1',text='4. How the estimate was prepared')
blk(type='bullets',items=[
 'All 40 sheets were studied: 9 structural sheets (foundation layout & sections, stair, lintel key plans & sections, three slab reinforcement plans, beam sections) and 31 architectural/services sheets (plans, elevations, wall section, boundary walls, bath details, electrical, sewerage, sanitary).',
 'The structural PDFs are AutoCAD vector files, so wall lines were measured directly from the file geometry instead of scaling paper prints. Scale was calibrated on the 13\'-0" x 13\'-0" Bed-1 (1 ft = 33.053 drawing units); 9" and 4½" walls measured 9.0" and 4.5". The hand-built wall network (Appendix A) matches the raster-measured wall area within 1%.',
 'Foundation volumes use exact polygon unions of every layer (PCC, footing, each brick step, plinth), so overlaps at the many T-junctions are not double counted (unions are about 12% less than simple length x width).',
 'First-floor walls were measured from the lintel key plan (S-04) and openings added back; mumty walls from the 2nd-floor plan. Slab outlines, stair openings, beams and bed plates were measured on the slab sheets.',
 'Slab steel: every bar set on S-06/S-07/S-08 (spacing label, its distribution dimension line and bar length) was listed individually - 44 sets (GF roof), 40 sets (FF roof), 11 sets (mumty roof) - see Appendix B.',
 'Sewer, water and gas pipe runs were measured on the colour-coded services sheets (sheet scale calibrated separately); vertical stacks, risers and drops were added. Electrical conduits are based on a point count of the electrical plans.'])
blk(type='h2',text='4.1 Standard coefficients used (upper end of range)')
co=[['Bricks per cft of brickwork','13.5 nos','Standard local brick with ⅜" joints'],
    ['Mortar per cft of brickwork','0.30 cft wet = 0.40 cft dry','Range 0.25-0.30 wet; upper value used'],
    ['Dry volume factor - concrete','1.57','Range 1.52-1.57'],
    ['Dry volume factor - mortar','1.33',''],
    ['Plaster extra for joints/uneven surface','+25%','Range 20-30%'],
    ['Cement bag','50 kg = 1.25 cft',''],
    ['Steel weights (lb/ft)','#2 0.167, #3 0.376, #4 0.668, #6 1.502','1 lb = 0.4536 kg'],
    ['Wastage','Cement 5%, sand 10%, crush 5%, bricks 5%, steel 5%, pipes 10%','Laps, hooks, cranks, chairs are inside the net steel'],
    ['Mortar ratios','Foundation 1:6 (drawing); 9" walls 1:5; 4½" walls, parapets, pillars, tanks 1:4; plaster 1:4 (walls), 1:3 (ceilings, water-retaining)','Superstructure ratios not given on drawings - assumed']]
blk(type='table',header=['Coefficient','Value','Remarks'],widths=[3000,3900,3006],align=['L','L','L'],rows=[{'cells':r} for r in co],font=8.5)
blk(type='h2',text='4.2 Assumptions (please confirm on site)')
blk(type='numbers',items=[
 'Natural surface level taken 1\'-6" below road (drawings: "as per site"). Every 6" higher/lower NSL changes earth filling by about 820 cft and foundation brickwork slightly.',
 'Foundation R.C.C footing concrete taken 1:2:4 (mix not stated).',
 'Septic tank enlarged to a standard 6\'-0" x 4\'-0" x 5\'-6" deep (internal, 2 chambers) - the drawing shows only a 4\'-10" x 3\'-5" symbol, small for 8 WCs.',
 'Overhead water tank taken as R.C.C 1,000 gallons (8\'x5\'x4\'-6" internal) on the mumty roof - drawings show a symbol only. If you use plastic tanks, delete Section I (saves ~34 bags cement, ~230 kg steel).',
 'Back boundary wall (37\'-3") and short right-side walls at the back passage and driveway are not detailed but included (9" x 6\'-6" to 7\'-0"). Delete if neighbours\' walls already exist.',
 'Boundary wall foundation (not detailed) taken as 3" P.C.C + three brick steps + 9"x6" R.C.C plinth band + 3" R.C.C coping.',
 'A 5% brickwork allowance is added for front-elevation frames, fins, piers and profile-light reveals that are not shown in plan.',
 'The car-porch corner (13½" x 13½") is taken as an R.C.C column (4#6, #3@6" ties) as the notes specify column concrete - costlier than a brick pillar.',
 'An 8\'-0" lintel is added over the 6\'-6" dining opening (not shown on the lintel key plan).',
 'A 3" P.C.C 1:4:8 sub-base is included over the first-floor and mumty floors to level the 4" upstand beams and cover conduits.'])
blk(type='h2',text='4.3 Not included (exclusions)')
blk(type='p',text='Labour; shuttering/formwork and scaffolding (contractor\'s items); curing water and construction electricity; all finishing works (tiles/marble, paint, woodwork, aluminium, glass, grills, railings, gates); sanitary fixtures; electrical cables, switches, breakers and DBs (only conduits and boxes included); geyser; termite treatment; and the optional items in Section 9.')

# =============================== 5. DETAILED BOQ (landscape) ===============================
blk(type='section',orientation='LANDSCAPE')
blk(type='h1',text='5. Detailed bill of quantities with material breakdown (net, before wastage)')
blk(type='p',text='Each line shows the measured quantity and the materials it consumes. Section sub-totals are net; wastage is applied only once, in Sections 1 and 2.')
rows=[]
for sec,m in D['sections']:
    rows.append({'cells':[sec,'','','','','','','',''],'kind':'section'})
    for it in D['items']:
        if it['sec']!=sec: continue
        desc=it['desc']+(' ['+it['note']+']' if it['note'] else '')
        rows.append({'cells':[it['item'],desc,f1(it['qty']),it['unit'],
            f1(it['cement']) if it['cement'] else '-', f0(it['sand']) if it['sand'] else '-', f0(it['crush']) if it['crush'] else '-',
            f0(it['bricks']) if it['bricks'] else '-', f0(it['steel']) if it['steel'] else '-']})
    rows.append({'cells':['','Sub-total '+sec.split('.')[0],'','',f1(m['cement']),f0(m['sand_c']+m['sand_m']+m['sand_f']),f0(m['crush']),f0(m['bricks']),f0(sum(m['steel'].values()))],'kind':'subtotal'})
rows.append({'cells':['','GRAND TOTAL (net)','','',f1(T['cement']),f0(T['sand_c']+T['sand_m']+T['sand_f']),f0(T['crush']),f0(T['bricks']),f0(steel_net)],'kind':'total'})
blk(type='table',header=['Item','Description','Quantity','Unit','Cement (bags)','Sand (cft)','Crush (cft)','Bricks (nos)','Steel (kg)'],
    widths=[800,7238,1000,600,1050,1050,1050,1200,1050],align=['L','L','R','C','R','R','R','R','R'],rows=rows,font=7.5,repeat=True)

# =============================== 6. STEEL SCHEDULE ===============================
blk(type='h1',text='6. Reinforcement steel schedule (kg, net)')
rows=[]; tb={'2':0,'3':0,'4':0,'6':0}
for sec,d in D['steel_comp'].items():
    vals=[d.get(b,0) for b in ('2','3','4','6')]
    for b,v in zip(('2','3','4','6'),vals): tb[b]+=v
    rows.append({'cells':[sec]+[f0(v) if v else '-' for v in vals]+[f0(sum(vals))]})
rows.append({'cells':['TOTAL net']+[f0(tb[b]) for b in ('2','3','4','6')]+[f0(sum(tb.values()))],'kind':'subtotal'})
rows.append({'cells':['TOTAL with 5% wastage (to procure)']+[f0(proc_steel[b]) for b in ('2','3','4','6')]+[f0(proc_steel_tot)],'kind':'total'})
blk(type='table',header=['Component','6 mm (#2)','10 mm (#3)','12 mm (#4)','20 mm (#6)','Total (kg)'],
    widths=[5838,1840,1840,1840,1840,1840],align=['L','R','R','R','R','R'],rows=rows,font=8.5)
blk(type='p',text='Bar lengths are generally available in 40 ft (12 m) lengths. Approximate number of bars to buy (with wastage): '+', '.join(f"{bar_name[b].split(' -')[0]}: {math.ceil(proc_steel[b]/(LB_FT[int(b)]*KG_PER_LB*40))} bars" for b in ('3','4','6','2'))+'. Per-component detail: footings '+f0(items['A3']['steel'])+' kg, plinth beams '+f0(items['A6']['steel'])+' kg, slabs '+f0(items['E-GF']['steel']+items['E-FF']['steel']+items['E-SF']['steel'])+' kg, concealed beams '+f0(sum(items[k]['steel'] for k in items if k.startswith('D-CB')))+' kg, lintels '+f0(items['D-LGF']['steel']+items['D-LFF']['steel']+items['D-LSF']['steel'])+' kg, stairs '+f0(items['D-ST-GF']['steel']+items['D-ST-FF']['steel']+items['D-SF']['steel'])+' kg.')

# =============================== 7. SERVICES ===============================
blk(type='section',orientation='PORTRAIT')
blk(type='h1',text='7. Sewerage, rain-water, water-supply and gas pipes')
blk(type='p',text='Horizontal runs were measured on the colour-coded sewerage (sheets 17-20) and sanitary (sheets 21-24) drawings; vertical soil/waste stacks, vent pipes, rain-water pipes, risers and fixture drops were added.')
rows=[]
for p in pipes:
    if 'Electrical' in p['group']: continue
    rows.append({'cells':[p['group'],p['size'],p['desc'],f0(p['ft']),f0(math.ceil(p['ft_w'])),str(math.ceil(p['ft_w']/20))]})
blk(type='table',header=['Service','Size','Run / basis','Net (ft)','+10% (ft)','20-ft lengths'],widths=[1500,700,4506,1000,1100,1100],align=['L','C','L','R','R','R'],rows=rows,font=8)
blk(type='h2',text='7.1 Manholes and septic tank')
blk(type='bullets',items=[
 '9 manholes / inspection chambers (3 in rear passage, 3 in left side passage, 1 front-left lawn corner, 1 patio, 1 car porch): 2\'-0" x 2\'-0" internal, average 3\'-6" deep, 9" brick walls in 1:4 on 4" P.C.C, benching, ½" plaster 1:3 inside, 3" R.C.C cover slab. Buy 9 manhole covers (C.I. or R.C.C, 20"x20").',
 'Septic tank (front lawn, connected to main sewer): internal 6\'-0" x 4\'-0" x 5\'-6", two chambers with 4½" baffle walls, 6" R.C.C base, 9" brick walls 1:4, 5" R.C.C top with two 2\'x2\' openings, ¾" water-proof plaster. Buy 2 covers and 2 x 5" UPVC tees (inlet/outlet).',
 'Rain water: 4 roof sumps (1\'-6" x 1\'-6") and 3" pipes in 9" x 6" wall ducts with 1½" tile cover as drawn.'])
blk(type='h2',text='7.2 Fittings (approximate counts)')
fit=[['UPVC sewer 5"','Bends 8, Y-tees 6, sockets 9, septic inlet/outlet tees 2'],
     ['UPVC 4" (soil)','WC connectors 8, bends 20, Y-tees 10, sockets 8, vent cowls 4, clean-out plugs 4'],
     ['UPVC 3" (waste & rain)','Floor traps (P-traps) 14, gully traps 3, bends 40, Y-tees 20, sockets 15, roof outlets 4, RWP shoes 4'],
     ['PPR water (cold/hot)','Elbows ~120, tees ~60, sockets ~80, male/female adaptors ~55, unions ~20, ball valves ~20, gate valves 4'],
     ['Gas','Elbows ~20, tees ~8, gas cocks 8, meter connection set 1'],
     ['Consumables','UPVC solvent cement 4 kg, PTFE tape, pipe clamps ~120']]
blk(type='table',header=['Group','Fittings'],widths=[2400,7506],align=['L','L'],rows=[{'cells':r} for r in fit],font=8.5)

# =============================== 8. ELECTRICAL ===============================
blk(type='h1',text='8. Electrical conduits and boxes')
pts=D['points']
rows=[]
for fl,lab in (('GF','Ground floor'),('FF','First floor'),('SF','Mumty & terrace')):
    p=pts[fl]; rows.append({'cells':[lab,str(p['light']),str(p['socket']),str(p['ac']),str(p['sb'])]})
rows.append({'cells':['Total',str(sum(p['light'] for p in pts.values())),str(sum(p['socket'] for p in pts.values())),str(sum(p['ac'] for p in pts.values())),str(sum(p['sb'] for p in pts.values()))],'kind':'total'})
blk(type='table',header=['Floor','Light / fan / fancy / profile / CCTV points','Socket points','A.C points','Switch boards'],
    widths=[2106,2700,1700,1600,1800],align=['L','C','C','C','C'],rows=rows,font=8.5)
rows=[]
for p in pipes:
    if 'Electrical' not in p['group']: continue
    rows.append({'cells':[p['size'],p['desc'],f0(p['ft']),f0(math.ceil(p['ft_w'])),str(math.ceil(p['ft_w']/10))]})
blk(type='table',header=['PVC conduit','Basis','Net (ft)','+10% (ft)','10-ft pipes'],widths=[1100,5606,1000,1100,1100],align=['C','L','R','R','R'],rows=rows,font=8)
blk(type='bullets',items=[
 'Back boxes: 39 switch-board boxes (assorted 3"x3" to 12"x3"), ~79 socket boxes, 10 A.C boxes, 13 fan boxes with hooks, ~110 round light junction boxes, 3 DB enclosures (main 12-way GF, 8-way FF, 4-way mumty).',
 'Accessories: ~300 bends ¾", ~100 bends 1", ~350 couplers ¾", ~150 couplers 1", PVC solvent, GI draw wire.',
 'Points were counted from the electrical plans (sheets 13-15, legend sheet 16); per-point conduit allowances: 12 ft per light/fan point, 8 ft per socket, 25 ft per switch-board feeder, 30-45 ft per A.C circuit, 30 ft per low-voltage run (TV, internet, CCTV, intercom, bells), +10% for UPS circuits.'])

# =============================== 9. OPTIONAL ===============================
blk(type='h1',text='9. Optional items (NOT included in the totals)')
rows=[]
for o in D['optional']:
    rows.append({'cells':[o['item'],o['desc'],f0(o['cement']),f0(o['sand']),f0(o['crush']) if o['crush'] else '-',f0(o['bricks']) if o['bricks'] else '-',f0(o['steel']) if o['steel'] else '-',o['other']]})
blk(type='table',header=['Item','Description','Cement (bags)','Sand (cft)','Crush (cft)','Bricks / tiles','Steel (kg)','Other'],
    widths=[640,3666,900,800,800,1000,800,1300],align=['C','L','R','R','R','R','R','L'],rows=rows,font=7.5)
blk(type='p',text='Roof treatment (item O1) is often counted as part of the grey structure in Faisalabad contracts - add it if your contractor\'s scope includes it.')

# =============================== 10. CONFIRM ===============================
blk(type='h1',text='10. Points to confirm with your architect / engineer')
blk(type='p',text='These observations came up while measuring the drawings. None changes the estimate materially, but each should be settled before work starts.')
blk(type='numbers',items=[
 'Natural surface level vs road level is marked "as per site". Have it surveyed; it controls excavation depth and earth filling (about 820 cft per 6").',
 'Ground-floor M-Bed is 14\'-0" x 12\'-0" on the structural layout but labelled 14\'-3" x 12\'-0" on the architectural plan (first floor M-Bed is 14\'-3" x 14\'-0"). The estimate follows the structural geometry.',
 'The septic tank on sheet 17 is only about 4\'-10" x 3\'-5" overall. For 8 WCs a larger tank (estimated 6\'-0" x 4\'-0" x 5\'-6" internal) is advisable.',
 'The overhead water tank is shown only as a symbol (5\'-4" x 3\'-1") on the mumty roof; its support (walls/beams under it) is not designed. Confirm R.C.C vs plastic tanks.',
 'The 6\'-6" dining opening has no lintel on the lintel key plan (S-04); an 8\'-0" DL-1 has been included.',
 'The second stair flight (steps 14-22) passes over the rear car porch (headroom about 7\'). The first-floor stair-hall rear wall there is 4½" thick and sits on CB-1 beams cast with the ground-floor roof - make sure these beams and the stair are cast together as detailed.',
 'The car-porch front corner (13½" square, hatched on S-01) has no column or footing detail. The estimate assumes an R.C.C column with 4#6 bars on a 3\'x3\'x1\' footing.',
 'The ground-floor patio (4\'-0" wide) and the first-floor "open 3\'-6" wide" shaft are open on the neighbour (property-line) side - confirm whether a privacy/boundary wall is required there (not included).',
 'The powder-room wall on the property line is only 4½" thick with a concentric 2\'-0" footing (section 4-4) that would cross the property line; consider an eccentric footing like section 1-1.',
 'Boundary wall foundations and the back boundary wall are not detailed; confirm the assumed details (Section 4.2).',
 'Superstructure mortar ratios are not specified; the estimate assumes 1:5 for 9" and 1:4 for 4½" walls.',
 'Sunken slabs (+0\'-6" depressed) are noted under first-floor baths - ensure the slab steel is detailed through the drops.'])

# =============================== 11. CHECKLIST ===============================
blk(type='h1',text='11. Practical checklist for a first project')
blk(type='bullets',items=[
 'Order in stages (Section 2) and keep a stock register; count bricks and weigh steel on every delivery.',
 'Bricks: first class, uniform size and colour, clear ringing sound, no cracks; soak before laying.',
 'Cement: check the manufacturing date (use within about a month), store on a raised dry platform, not more than 10 bags high.',
 'Sand: do a silt (bottle) test - reject if silt is more than about 8%. Chenab sand for concrete, Ravi sand for mortar and plaster.',
 'Steel: Grade 60 rolling marks on every bar; check weight per foot against the standard (10 mm = 0.376 lb/ft, 12 mm = 0.668 lb/ft, 20 mm = 1.502 lb/ft).',
 'Measure concrete and mortar with gauge boxes (farma), never by shovels; use a vibrator for slabs and beams.',
 'Before every slab pour, have the engineer check bar sizes, spacing, cranked bars, extra top bars, covers (¾" slab, 1½" beams) and chairs.',
 'Place electrical conduits, fan boxes and sewer/water sleeves before casting slabs and before plastering.',
 'Cure slabs and beams for at least 10-14 days, brickwork and plaster for 7 days.'])

# =============================== APPENDICES ===============================
blk(type='section',orientation='LANDSCAPE')
blk(type='h1',text='Appendix A - Measured foundation / ground-floor wall schedule')
blk(type='p',text='Coordinates in feet from the rear-left corner of the building (x to the right, y towards the road), measured from structural drawing S-01. Section = foundation type from S-01/S-02.')
rows=[]
for (wid,desc,t,typ,Lw,xy) in D['walls']:
    rows.append({'cells':[wid,desc,'9"' if t==0.75 else '4½"',f"{typ}-{typ}",f2(Lw),f"({xy[0]}, {xy[1]}) to ({xy[2]}, {xy[3]})"]})
rows.append({'cells':['','Total centre-line length','','',f2(sum(w[4] for w in D['walls'])),''],'kind':'total'})
blk(type='table',header=['Wall','Description','Thickness','Section','Length (ft)','Centre-line coordinates (ft)'],
    widths=[800,6238,1100,1000,1300,4600],align=['L','L','C','C','R','L'],rows=rows,font=7.5,repeat=True)
lay=D['layers']
blk(type='table',header=['Foundation layer','Plan area (sft, union of all walls)','Thickness','Volume (cft)'],
    widths=[4500,4000,2500,4038],align=['L','R','C','R'],rows=[{'cells':r} for r in [
    ['P.C.C 1:4:8',f1(lay['pcc']),'3"',f1(lay['pcc']*0.25)],['R.C.C footing',f1(lay['rccf']),'6"',f1(lay['rccf']*0.5)],
    ['Brick step 22½"',f1(lay['b225']),'6"',f1(lay['b225']*0.5)],['Brick step 18"',f1(lay['b18']),'6"',f1(lay['b18']*0.5)],
    ['Brick step 13½"',f1(lay['b135']),'12"',f1(lay['b135'])],['9" plinth strip (plinth beam, DPC, plinth wall)',f1(lay['p9']),'9" / 1½" / 2\'-9"',f"{f1(lay['p9']*0.75)} / {f1(lay['p9']*0.125)} / {f1(lay['p9']*2.75)}"]]],font=8)

blk(type='h1',text='Appendix B - Slab reinforcement bar sets (from S-06, S-07, S-08)')
blk(type='p',text='B = bottom bars (alternately straight and cranked, +0.6 ft per bar for hooks/cranks); T = extra top bars (+0.3 ft). No. of bars = distribution width / spacing + 1. Trimmer bars (2#6, 2#4) and chairs are added to each floor total.')
for fl,lab in (('GF','Ground-floor roof (S-06)'),('FF','First-floor roof (S-07)'),('SF','Mumty roof (S-08)')):
    rows=[]; kg_t=0
    for (i,bar,s,Wd,Lb,k,n,tl) in D['slab_rows'][fl]:
        kg=tl*LB_FT[bar]*KG_PER_LB; kg_t+=kg
        rows.append({'cells':[i,{3:'10 mm',4:'12 mm',6:'20 mm'}[bar],f'{s}"',f2(Wd),f2(Lb),'Bottom' if k=='B' else 'Extra top',str(n),f1(tl),f1(kg)]})
    rows.append({'cells':['','','','','','Bar sets total','','',f1(kg_t)],'kind':'subtotal'})
    rows.append({'cells':['','','','','','Floor total incl. trimmers & chairs','','',f1(items['E-'+fl]['steel'])],'kind':'total'})
    blk(type='h2',text=lab+f" - slab area {D['slabs'][fl]:,.1f} sft")
    blk(type='table',header=['Set','Bar','Spacing','Distribution width (ft)','Bar length (ft)','Type','No. of bars','Total length (ft)','Weight (kg)'],
        widths=[900,1100,1000,2000,1800,2338,1300,2300,2300],align=['C','C','C','R','R','L','R','R','R'],rows=rows,font=7.5,repeat=True)

blk(type='h1',text='Appendix C - Openings and lintels')
for fl,lab in (('GF','Ground floor'),('FF','First floor'),('SF','Mumty (2nd floor)')):
    rows=[]
    for (d,w,hh,t,n,ext) in D['openings'][fl]:
        rows.append({'cells':[d,ftin(w),ftin(hh),'9"' if t==0.75 else '4½"',str(n),'External' if ext else 'Internal']})
    blk(type='h2',text=lab+' - openings deducted from brickwork')
    blk(type='table',header=['Opening','Width','Height','Wall','Nos','Wall type'],widths=[6538,1500,1500,1500,1500,2500],align=['L','C','C','C','C','C'],rows=rows,font=7.5)
rows=[]
for fl in ('GF','FF','SF'):
    for (t,Ln,n) in D['lintels'][fl]:
        rows.append({'cells':[fl,t,ftin(Ln),str(n),{'DL-1':'9"x9", 4#4, #3@6"','WL-1':'9"x9", 4#4, #3@6"','WL&DL-1':'9"x9", 4#4, #3@6"','WL-2':'9"x9", 2#4+4#4, #3@6"','DL-2':'4½"x9", 4#4, #2@6"','WL-3':'4½"x9", 4#4, #2@6"','VL-1':'9"x9", 4#3, #3@10"'}[t]]})
blk(type='h2',text='Lintel schedule (length = opening + bearing)')
blk(type='table',header=['Floor','Type','Length','Nos','Section & steel (S-05)'],widths=[1500,1800,1800,1200,8738],align=['C','C','C','C','L'],rows=rows,font=7.5)
json.dump(B,open(os.path.join(os.path.dirname(__file__),'blocks.json'),'w'),indent=0)
print(len(B),'blocks')
