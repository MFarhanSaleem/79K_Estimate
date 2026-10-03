# ============================================================================
#  House 79/K (Mr. Saleem), WAPDA City Faisalabad
#  Grey structure MATERIAL estimate - Revision 1
#  Applies the owner's Final Decisions Register (A1-K3) to the Rev 0 take-off.
#  Units: ft / sft / cft unless stated. Levels in inches relative to road crown = 0.
# ============================================================================
import json, math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'est'))
import coeff as C           # standard coefficients (unchanged from Rev 0)
import estimate as R0       # Rev 0 take-off: wall, slab, lintel, stair and pipe geometry is re-used
FND = json.load(open(os.path.join(HERE, 'found_rev1.json')))   # sheet-05 foundation bands (union areas)
ROOF = json.load(open(os.path.join(HERE, 'roof_rev1.json')))   # terrace / mumty roof geometry + screed

SQM = 0.09290304
ADMX_PER_BAG = 1.0          # kg integral waterproofing compound per 50 kg bag of cement (powder type)
BIT_COAT = 0.2              # kg hot bitumen per sft per coat (B6)

# ---------------------------------------------------------------- helpers
def mix(*ds):
    o = {}
    for d in ds:
        for k, v in d.items():
            o[k] = o.get(k, 0) + v
    return o
def conc(v, m, admix=False):
    c, s, g = C.MIX[m]; t = c + s + g; dry = v * C.DRY_CONC
    o = {'CEM': dry*c/t/C.BAG_CFT, 'SNDC': dry*s/t, 'CRS': dry*g/t}
    if admix: o['ADMX'] = o['CEM'] * ADMX_PER_BAG
    return o
def mort(wet, r, sand='SNDM', admix=False):
    c, s = C.MORTAR[r]; dry = wet * C.DRY_MORTAR
    o = {'CEM': dry*c/(c+s)/C.BAG_CFT, sand: dry*s/(c+s)}
    if admix: o['ADMX'] = o['CEM'] * ADMX_PER_BAG
    return o
def bw(v, r):
    o = mort(v * C.MORTAR_PER_CFT, r); o['BRK'] = v * C.BRICKS_PER_CFT; return o
def pl(a, t, r, admix=False):
    return mort(a * t / 12 * C.PLASTER_EXTRA, r, admix=admix)
def st(d):
    return {'ST%d' % b: ft * C.LB_FT[b] * C.KG_PER_LB for b, ft in d.items()}
def r0mat(it):
    """convert a Rev 0 item's materials to Rev 1 keys"""
    m = it['mat']; o = {}
    if m.get('cement_bags'): o['CEM'] = m['cement_bags']
    if m.get('sand'): o['SNDC' if m.get('crush', 0) > 0 else 'SNDM'] = m['sand']
    if m.get('crush'): o['CRS'] = m['crush']
    if m.get('bricks'): o['BRK'] = m['bricks']
    return mix(o, st(it['steel']))
R0I = {i['item']: i for i in R0.ITEMS}
def fi(x): return '{:,.0f}'.format(x)
def f1(x): return '{:,.1f}'.format(x)
def f2(x): return '{:,.2f}'.format(x)

STAGES = [('S1', 'Levels and layout'), ('S2', 'Excavation'), ('S3', 'Anti-termite treatment'),
          ('S4', 'Foundations'), ('S5', 'Plinth beam and DPC'), ('S6', 'Filling and sub-floor'),
          ('S7', 'Masonry'), ('S8', 'RCC (superstructure)'), ('S9', 'Roof waterproofing and tiles'),
          ('S10', 'Chicken mesh and plaster'), ('S11', 'Sewerage and drainage'), ('S12', 'Septic tank'),
          ('S13', 'Water tanks, water and gas pipes'), ('S14', 'Electrical civil provisions and solar plinths'),
          ('S15', 'Boundary walls'), ('S16', 'External works')]
ITEMS = []
def add(stage, code, loc, desc, dims, work, qty, unit, mat=None, reg='', group='', info=None):
    ITEMS.append(dict(stage=stage, code=code, loc=loc, desc=desc, dims=dims, work=work, qty=qty, unit=unit,
                      mat={k: v for k, v in (mat or {}).items() if v > 1e-9}, reg=reg, group=group, info=info or {}))

# ---------------------------------------------------------------- levels (inches, road crown = 0)
NSL = -18                     # A1
PCC_BOT, PCC_TOP = -48, -45   # C2: 2'-6" below NSL; C3: PCC 3"
STEP_TOP = -27                # three 6" brick steps
FFL = 33                      # A3: finished floor (top of tile) +2'-9"
DPC_BOT = 31.5                # B5: top of DPC = FFL, DPC 1.5" thick
BEAM_BOT = 22.5               # 9" plinth beam under the DPC
PORCH, LAWN, PASSAGE = 15, 14, 12
HOUSE_FILL_TOP = FFL - 1.5 - 3 - 1 - 4      # finish 1.5 | PCC 3 | sand 1 | khangar 4  -> +23.5"
PORCH_FILL_TOP = PORCH - 1.5 - 3 - 1 - 4    # -> +5.5"
PASS_FILL_TOP = PASSAGE - 3 - 3 - 2         # finish 3 (finishing est.) | PCC 3 | sand 2 -> +4"
LEVELS = [
    (PCC_BOT, 'Bottom of PCC under house footings (2\'-6" below NSL; ~6" into the firm stratum)', 'C2'),
    (PCC_TOP, 'Top of PCC 3" / bottom of 27" (22½") brick step', 'C3'),
    (STEP_TOP, 'Top of three 6" brick steps; 13½" foundation wall (9" under 4½" walls) starts', 'C1'),
    (-42, 'Firm natural soil starts (about 2\'-0" below NSL)', 'A2'),
    (NSL, 'Natural surface level (NSL)', 'A1'),
    (0, 'Road crown; 13½" wall steps to 9" plinth wall', 'A1, C1'),
    (PASSAGE, 'Finished level of side and rear passages (assumed, sloping 1:60 to drains)', 'G4'),
    (LAWN, 'Finished lawn level (lawn filling excluded)', 'A3, A5'),
    (PORCH, 'Finished level of both car porches; highest adjoining outside level', 'A3'),
    (BEAM_BOT, 'Underside of 9"x9" RCC plinth beam', 'B4'),
    (HOUSE_FILL_TOP, 'Top of compacted earth fill inside the house', 'A3, A5'),
    (HOUSE_FILL_TOP + 4, 'Top of 4" khangar (stone ballast)', 'B2'),
    (HOUSE_FILL_TOP + 5, 'Top of 1" sand blinding; 0.2 mm polythene laid here', 'B2'),
    (DPC_BOT, 'Top of 3" PCC sub-floor = top of plinth beam = underside of DPC', 'B2, B4'),
    (FFL, 'Top of DPC = finished floor level (top of tile, +2\'-9")', 'B4, B5'),
]
DPC_CLEAR = FFL - PORCH          # 18" above highest outside level (>= 9" required)

# ---------------------------------------------------------------- measured quantities
GF_ROOMS = 1362.6                 # clear floor area inside GF walls (Rev 0 raster of S-01)
A_FP = 20.001*16.473 - 7.001*3.0  # front car porch 20'-0" x 16'-7.5" less entrance-lobby notch (sheet 04 / 17 geometry)
A_RP = 16.79*8.5                  # rear car porch 16'-9.5" x 8'-6" (sheets 06, 17, 21)
A_SUB = GF_ROOMS + A_FP + A_RP
A_PASS = 167.3 + 97.7             # left passage (3'-3" to 4'-11", slanted boundary) + rear passage 5'-0" x 19'-6"
A_RAMP = 14.75*7.5 + 9.69*7.5     # ramps outside main gate (12'-9" + flares) and side gate (7'-8.25" + flares), 1:6
EDGE = [('Toe wall: lawn / front car porch (sheet 04)', 9.25), ('Toe wall across left passage at TV-lounge front (sheet 04)', 4.92),
        ('Rear car porch / left passage edge', 3.10), ('Rear car porch / rear passage edge', 5.00),
        ('Main-gate threshold: front porch / ramp', 12.75), ('Side-gate threshold: rear porch / ramp', 7.69)]
L_EDGE = sum(e[1] for e in EDGE)
L_TOT = FND['L_total']; EXT = FND['ext_len']

# =============================================================== S1 LEVELS AND LAYOUT
add('S1', '1.1', 'Whole plot', 'Level survey and setting out (no materials)',
    'Road crown = ±0; NSL = -1\'-6"; FFL +2\'-9"; porches +1\'-3"; lawn +1\'-2"',
    'Take levels at the 4 corners and centre before digging; set out walls from sheets 04/06 (architect\'s dimensions govern)',
    1, 'job', {}, 'A1, A3')

# =============================================================== S2 EXCAVATION
exc_house = FND['pcc'] * 2.5 * 1.10
add('S2', '2.1', 'All house walls', 'Excavation of wall trenches to PCC bottom, 2\'-6" below NSL (4\'-0" below road)',
    'PCC footprint %s sft (3\'-0" under 9" walls, 2\'-6" under 4½" walls; union of all walls, eccentric on property line)' % f1(FND['pcc']),
    '%s sft x 2.50 ft x 1.10 working space' % f1(FND['pcc']), exc_house, 'cft', {}, 'A1, A3, C1, C2, C4',
    info={'EXC': exc_house})
exc_col = 3.5*3.5*2.5*1.10
add('S2', '2.2', 'Car-porch front corner', 'Excavation for isolated column footing', '3\'-6" x 3\'-6" x 2\'-6" deep',
    '3.5 x 3.5 x 2.5 x 1.10', exc_col, 'cft', {}, 'C5', info={'EXC': exc_col})
exc_edge = L_EDGE*2.5*2.25*1.10
add('S2', '2.3', 'Porch, lawn and gate edges', 'Excavation for edge / retaining walls (section D-D), PCC bottom 2\'-3" below NSL',
    '%s ft x 2\'-6" x 2\'-3"' % f1(L_EDGE), '%.2f x 2.5 x 2.25 x 1.10' % L_EDGE, exc_edge, 'cft', {}, 'C6',
    info={'EXC': exc_edge})

# =============================================================== S3 ANTI-TERMITE
# bifenthrin 10% EC diluted 1:200 (0.05% a.i.); 5 L emulsion per m2; 2.25 L per running metre along perimeter
DIL = 200.0
a3 = FND['pcc'] + 2*L_TOT*2.5
em = a3*SQM*5
add('S3', '3.1', 'House trenches', 'Termiticide on trench bottoms and sides, before PCC',
    'bottoms %s sft + sides 2 x %s ft x 2\'-6"' % (fi(FND['pcc']), f1(L_TOT)),
    '%s sft = %s m2 x 5 L/m2 = %s L emulsion; ÷ 200' % (fi(a3), f1(a3*SQM), fi(em)), em/DIL, 'L', {'TERM': em/DIL}, 'B1')
em = A_SUB*SQM*5
add('S3', '3.2', 'House floor + both car porches', 'Termiticide on top of compacted plinth filling, before khangar',
    'rooms %s + front porch %s + rear porch %s sft' % (fi(GF_ROOMS), fi(A_FP), fi(A_RP)),
    '%s sft = %s m2 x 5 L/m2 = %s L emulsion; ÷ 200' % (fi(A_SUB), f1(A_SUB*SQM), fi(em)), em/DIL, 'L', {'TERM': em/DIL}, 'B1')
em = EXT*0.3048*2.25
add('S3', '3.3', 'House perimeter', 'Termiticide in soil along outside of plinth walls, after back-filling',
    'outer walls %s ft' % f1(EXT), '%s m x 2.25 L/m = %s L emulsion; ÷ 200' % (f1(EXT*0.3048), fi(em)),
    em/DIL, 'L', {'TERM': em/DIL}, 'B1')

# =============================================================== S4 FOUNDATIONS
v = FND['pcc']*0.25
add('S4', '4.1', 'All house walls', 'PCC 1:4:8, 3" thick, under brick footings (sheet 05 widths 3\'-0" / 2\'-6")',
    '%s sft x 3"' % f1(FND['pcc']), '%s x 0.25' % f1(FND['pcc']), v, 'cft', conc(v, '1:4:8'), 'C1, C3', 'Foundations')
v_steps = (FND['st1'] + FND['st2'] + FND['st3'])*0.5
add('S4', '4.2', 'All house walls', 'Brick footing in 1:6: steps 27" / 22½" / 18" under 9" walls, 22½" / 18" / 13½" under 4½" walls, 6" each',
    'union plan areas %s + %s + %s sft x 6"' % (f1(FND['st1']), f1(FND['st2']), f1(FND['st3'])),
    '(%s + %s + %s) x 0.5' % (f1(FND['st1']), f1(FND['st2']), f1(FND['st3'])), v_steps, 'cft', bw(v_steps, '1:6'), 'C1, C3')
v135 = FND['w135']*2.25
add('S4', '4.3', 'All house walls', 'Foundation wall in 1:6 from top of steps (-2\'-3") to road level: 13½" under 9" walls, 9" under 4½" walls',
    'plan %s sft x 2\'-3"' % f1(FND['w135']), '%s x 2.25' % f1(FND['w135']), v135, 'cft', bw(v135, '1:6'), 'C1')
v9p = FND['w9']*1.875
add('S4', '4.4', 'All house walls', 'Plinth wall 9" in 1:6 from road level to underside of plinth beam (+1\'-10½")',
    'plan %s sft x 1\'-10½"' % f1(FND['w9']), '%s x 1.875' % f1(FND['w9']), v9p, 'cft', bw(v9p, '1:6'), 'C1, B4')
v = 3.5*3.5*0.25
add('S4', '4.5', 'Car-porch front corner', 'PCC 1:4:8, 3", under isolated column footing', '3\'-6" x 3\'-6" x 3"', '3.5 x 3.5 x 0.25',
    v, 'cft', conc(v, '1:4:8'), 'C5')
add('S4', '4.6', 'Car-porch front corner', 'RCC isolated footing 1:2:4, 3\'-0" x 3\'-0" x 1\'-0", #4 @ 6" both ways (the only RCC footing)',
    '3\' x 3\' x 1\'', '9.0 cft; #4: 2 ways x 7 bars x 2\'-9"', 9.0, 'cft', mix(conc(9.0, '1:2:4'), st({4: 2*7*2.75})),
    'C5', 'Column footing')
v = L_EDGE*2.5*0.25
add('S4', '4.7', 'Porch, lawn and gate edges', 'Edge walls (D-D): PCC 1:4:8, 3" x 2\'-6"', '%s ft x 2\'-6" x 3"' % f1(L_EDGE),
    '%.2f x 2.5 x 0.25' % L_EDGE, v, 'cft', conc(v, '1:4:8'), 'C6, C3')
v = L_EDGE*(1.875 + 1.5 + 1.125)*0.5
add('S4', '4.8', 'Porch, lawn and gate edges', 'Edge walls: brick steps 22½" / 18" / 13½" (6" each) in 1:6',
    '%s ft' % f1(L_EDGE), '%.2f x (1.875 + 1.5 + 1.125) x 0.5' % L_EDGE, v, 'cft', bw(v, '1:6'), 'C6')
v = L_EDGE*0.75*(13.5 + 24)/12
add('S4', '4.9', 'Porch, lawn and gate edges', 'Edge walls: 9" wall in 1:6 from step top (-2\'-0") to +1\'-1½" (under DPC)',
    '%s ft x 9" x 3\'-1½"' % f1(L_EDGE), '%.2f x 0.75 x 3.125' % L_EDGE, v, 'cft', bw(v, '1:6'), 'C6, D1')
v = L_EDGE*0.75*0.125
add('S4', '4.10', 'Porch, lawn and gate edges', 'Edge walls: DPC 1½" 1:2:4 with waterproofing compound + 2 coats hot bitumen, top at porch level',
    '%s ft x 9"' % f1(L_EDGE), '%.2f x 0.75 x 0.125; bitumen %.1f sft x 0.4 kg' % (L_EDGE, L_EDGE*0.75),
    v, 'cft', mix(conc(v, '1:2:4', True), {'BIT': L_EDGE*0.75*2*BIT_COAT}), 'B4, C6')

# =============================================================== S5 PLINTH BEAM AND DPC
v = FND['w9']*0.75
pb_st = {4: 4*(L_TOT*1.05 + 0.5*30), 2: (L_TOT*12/10 + 1)*2.33}
add('S5', '5.1', 'All house walls', 'RCC plinth beam 9" x 9" (1:2:4) at floor level per sheet 05; 2 #4 top + 2 #4 bottom, #2 rings @ 10"',
    'plan %s sft x 9"; centre-line %s ft' % (f1(FND['w9']), f1(L_TOT)),
    'concrete %s x 0.75; #4: 4 x (%s x 1.05 + 15 ends x 1\'); rings (%s x 12/10 + 1) x 2\'-4"' % (f1(FND['w9']), f1(L_TOT), f1(L_TOT)),
    v, 'cft', mix(conc(v, '1:2:4'), st(pb_st)), 'B4', 'Plinth beam')
v = FND['w9']*0.125
add('S5', '5.2', 'All house walls', 'DPC: continuous 1½" 1:2:4 concrete with integral waterproofing compound, + 2 coats hot bitumen, on top of plinth beam; top of DPC = FFL',
    'plan %s sft x 1½"' % f1(FND['w9']), '%s x 0.125; bitumen %s sft x 2 coats x 0.2 kg' % (f1(FND['w9']), f1(FND['w9'])),
    v, 'cft', mix(conc(v, '1:2:4', True), {'BIT': FND['w9']*2*BIT_COAT}), 'B4, B5')
a = EXT*4.125
add('S5', '5.3', 'Outer plinth walls, fill side', 'Vertical DPC: ¾" 1:3 plaster with waterproofing compound + 2 coats hot bitumen (0.2 kg/sft per coat)',
    '%s ft x 4\'-1½" (NSL to top of sub-floor PCC)' % f1(EXT), '%s x 4.125 = %s sft' % (f1(EXT), fi(a)),
    a, 'sft', mix(pl(a, 0.75, '1:3', True), {'BIT': a*2*BIT_COAT}), 'B6')

# =============================================================== S6 FILLING AND SUB-FLOOR
below = FND['pcc']*0.25 + v_steps + FND['w135']*0.75
bf = exc_house - below
add('S6', '6.1', 'All house walls', 'Back-filling of trenches with excavated earth, watered and rammed in 6" layers',
    'trench %s cft less footing below NSL %s cft' % (fi(exc_house), fi(below)), '%s - %s' % (fi(exc_house), fi(below)),
    bf, 'cft', {}, 'A3, A4', info={'BACKFILL': bf})
h = (HOUSE_FILL_TOP - NSL)/12
v = GF_ROOMS*h*1.2
add('S6', '6.2', 'Inside house plinth', 'Earth filling from NSL to underside of khangar (+1\'-11½"), 6" layers watered and rammed',
    '%s sft x %.3f ft' % (fi(GF_ROOMS), h), '%s x %.3f x 1.20 compaction' % (f1(GF_ROOMS), h), v, 'cft', {},
    'A3, A4, A5', info={'EFILL': v})
h = (PORCH_FILL_TOP - NSL)/12
v = A_FP*h*1.2
add('S6', '6.3', 'Front car porch (full area)', 'Earth filling from NSL to underside of porch khangar (+5½")',
    '%s sft (20\'-0" x 16\'-7½" less lobby notch) x %.3f ft' % (fi(A_FP), h), '%s x %.3f x 1.20' % (f1(A_FP), h),
    v, 'cft', {}, 'A5', info={'EFILL': v})
v = A_RP*h*1.2
add('S6', '6.4', 'Rear car porch (full area)', 'Earth filling from NSL to underside of porch khangar (+5½")',
    '%s sft (16\'-9½" x 8\'-6") x %.3f ft' % (fi(A_RP), h), '%s x %.3f x 1.20' % (f1(A_RP), h), v, 'cft', {}, 'A5',
    info={'EFILL': v})
v = A_SUB*(4/12)*1.10
add('S6', '6.5', 'House floor + both car porches', 'Hand-packed stone ballast (khangar) 4", 1½"-2½" crushed stone (capillary break)',
    '%s sft x 4"' % fi(A_SUB), '%s x 0.333 x 1.10 packing' % f1(A_SUB), v, 'cft', {'KHG': v}, 'B2')
v = A_SUB*(1/12)*1.25
add('S6', '6.6', 'House floor + both car porches', 'Sand blinding 1" over khangar', '%s sft x 1"' % fi(A_SUB),
    '%s x 0.0833 x 1.25 (fills top voids)' % f1(A_SUB), v, 'cft', {'SNDM': v}, 'B2')
PERIM_TURN = 576.0
a = A_SUB*1.10 + PERIM_TURN*0.33
add('S6', '6.7', 'House floor + both car porches', 'Polythene sheet 0.2 mm (800 gauge) with 6" laps, turned up 4" against walls',
    '%s sft + turn-up %s ft x 4"' % (fi(A_SUB), fi(PERIM_TURN)), '%s x 1.10 + %s x 0.33 = %s sft x 0.0171 kg/sft' % (f1(A_SUB), fi(PERIM_TURN), fi(a)),
    a, 'sft', {'POLY': a*0.0171}, 'B2, B3')
v = A_SUB*0.25
add('S6', '6.8', 'House floor + both car porches', 'PCC 1:4:8, 3", sub-floor over polythene', '%s sft x 3"' % fi(A_SUB),
    '%s x 0.25' % f1(A_SUB), v, 'cft', conc(v, '1:4:8'), 'B2')

# =============================================================== S7 MASONRY
for fl, name in (('GF', 'Ground floor'), ('FF', 'First floor'), ('SF', 'Mumty (2nd floor)')):
    d = R0.FLOORS[fl]; n9, n45 = R0.BW[fl]
    add('S7', '7.%s9' % fl, name, '%s 9" walls in 1:6' % name,
        'plan %s sft x %.2f ft' % (f1(d['A9']), d['H']),
        'gross %s cft less openings %s, lintels %s, bed plates %s' % (fi(d['A9']*d['H']), fi(d['v9']), fi(d['lv9']), f1(d['bed']*0.5625)),
        n9, 'cft', bw(n9, '1:6'), 'D1, D2')
    add('S7', '7.%s4' % fl, name, '%s 4½" walls in 1:4' % name, 'plan %s sft x %.2f ft' % (f1(d['A45']), d['H']),
        'gross %s cft less openings %s, lintels %s' % (fi(d['A45']*d['H']), fi(d['v45']), fi(d['lv45'])),
        n45, 'cft', bw(n45, '1:4'), 'D1, D2')
for k, loc in (('C-P1', 'Terrace (first-floor roof)'), ('C-P2', 'Mumty roof')):
    it = R0I[k]
    if k == 'C-P1':
        dw = ('%s ft (4½") + %s ft (9") x %.2f ft high (2\'-6" above the finished terrace)' % (f1(R0.PARA_FF_L - R0.P3), f1(R0.P3), R0.PARA_FF_H),
              '(%s x 0.375 + %s x 0.75) x %.2f = %s cft' % (f1(R0.PARA_FF_L - R0.P3), f1(R0.P3), R0.PARA_FF_H, f1(it['qty'])))
    else:
        dw = ('%s ft x 4½" x %.2f ft high (1\'-6" above the finished roof)' % (f1(R0.SF_PERIM), R0.PARA_SF_H),
              '%s x 0.375 x %.2f = %s cft' % (f1(R0.SF_PERIM), R0.PARA_SF_H, f1(it['qty'])))
    add('S7', '7.' + k[-2:], loc, it['desc'].replace(', 1:4', '') + ' in 1:4', dw[0], dw[1], it['qty'], 'cft', bw(it['qty'], '1:4'), 'D1, D2')
it = R0I['C-E']
add('S7', '7.E', 'Front elevation', 'Elevation features allowance 5% of superstructure brickwork (frames, fins, piers, profile-light reveals, planters) in 1:4',
    '', '5% x walls + parapets', it['qty'], 'cft', bw(it['qty'], '1:4'), 'D2')

# =============================================================== S8 RCC
colH = (FFL + 132 - (PCC_TOP + 12))/12      # footing top to GF roof soffit
v = 1.125*1.125*colH
add('S8', '8.1', 'Car-porch front corner', 'RCC column 13½" x 13½" (1:1.5:3), 4 #6, #3 ties @ 6"',
    '13½" x 13½" x %.2f ft (footing top -2\'-9" to slab soffit +13\'-9")' % colH,
    '#6: 4 x (%.1f + 2.5 lap/anchorage); ties (%.1f x 2 + 1) x 4\'-0"' % (colH, colH), v, 'cft',
    mix(conc(v, '1:1.5:3'), st({6: 4*(colH + 2.5), 3: (colH*2 + 1)*4.0})), 'C5, E1', 'Column')
RCC0 = [('D-SGF', 'Slabs'), ('D-SFF', 'Slabs'), ('D-SSF', 'Slabs'), ('D-CB-1-GF', 'Concealed beams'), ('D-CB-1-FF', 'Concealed beams'),
        ('D-CB-2-GF', 'Concealed beams'), ('D-CB-2-FF', 'Concealed beams'), ('D-CB-2-SF', 'Concealed beams'),
        ('D-LGF', 'Lintels'), ('D-LFF', 'Lintels'), ('D-LSF', 'Lintels'), ('D-BP-GF', 'Bed plates'), ('D-BP-FF', 'Bed plates'),
        ('D-BP-SF', 'Bed plates'), ('D-ST-GF', 'Stairs'), ('D-ST-FF', 'Stairs'), ('D-SF', 'Stairs'), ('D-SP', 'Stairs'),
        ('D-SH-GF', 'Chajjas'), ('D-SH-FF', 'Chajjas'), ('D-SH-SF', 'Chajjas'), ('D-PR', 'Elevation RCC'), ('D-CP', 'Coping'),
        ('E-GF', 'Slabs'), ('E-FF', 'Slabs'), ('E-SF', 'Slabs')]
LOC = {'GF': 'Ground-floor roof', 'FF': 'First-floor roof', 'SF': 'Mumty roof'}
def rcc_dw(k, it):
    """Dimensions and working for RCC lines measured in Rev 0 (same formulas as est/estimate.py)."""
    q = it['qty']
    if k in ('D-SGF', 'D-SFF', 'D-SSF'):
        a = R0.SLAB[k[3:]]
        return '%s sft x 5½" thick' % f1(a), '%s x 5.5/12 = %s cft' % (f1(a), f1(q))
    if k.startswith('D-CB'):
        b, fl = k[2:6], k[7:]
        L, nb = R0.CB[b][fl]; wd = 1.0 if b == 'CB-1' else 0.75
        bars = ('#6 + #4: 3 + 3 x (%s + 3 ft anchorage per beam) x 1.03; #3 rings (%s x 12/7 + %d) x 3.21 ft' % (f1(L), f1(L), nb) if b == 'CB-1' else
                '#6: 4 x (%s + 3 ft anchorage per beam) x 1.03; #3 rings (%s x 12/6 + %d) x 2.71 ft' % (f1(L), f1(L), nb))
        return ('%d nos, total %s ft; %s x 9½" deep, 4" upstand above the 5½" slab (S-09)' % (nb, f1(L), '12"' if wd == 1 else '9"'),
                'upstand %s x %s x 4" = %s cft (rest is inside the slab); %s' % (f1(L), '1.0' if wd == 1 else '0.75', f1(q), bars))
    if k.startswith('D-L') and k[3:] in R0.LINTELS:
        agg = {}
        for t, L, n in R0.LINTELS[k[3:]]:
            a = agg.setdefault(t, [0, 0.0]); a[0] += n; a[1] += L*n
        return ('; '.join('%s %d nos / %s ft' % (t, a[0], f1(a[1])) for t, a in agg.items()),
                'sum of width x 9" x length = %s cft; main bars n x (L + 6"), rings (L x 12/spacing + 1) x ring length (S-05)' % f1(q))
    if k.startswith('D-BP'):
        n = {'GF': 9, 'FF': 12, 'SF': 2}[k[5:]]
        return '%d nos x 9" x 3\'-0" x 3"' % n, '%d x 0.75 x 3.0 x 0.25 = %s cft; #4: %d x 3 bars x 2\'-9"' % (n, f2(q), n)
    if k.startswith('D-ST'):
        return ('flights %s + %s ft (on slope) x 3\'-6" x 6" waist; landing 8\'-3" x 3\'-6" x 6"; 21 steps 10½" x 6.57"' % (f2(R0.g1), f2(R0.g2)),
                'waist %s + landing %s + steps %s = %s cft; #4 @ 5" main, #3 @ 9"/12" distribution (S-03)' % (f1(R0.waist), f1(R0.land), f1(R0.steps), f1(q)))
    if k == 'D-SF':
        return 'base 4\'-6" x 3\'-0" x 8" + stem 3\'-6" x 2\'-0" x 6"', '4.5 x 3.0 x 0.667 + 3.5 x 2.0 x 0.5 = %s cft; #4: 180.75 ft' % f1(q)
    if k == 'D-SP':
        return '5\'-0" x 3\'-6" x 3"', '5.0 x 3.5 x 0.25 = %s cft' % f2(q)
    if k.startswith('D-SH'):
        L = q/(1.25/3)
        return '%s ft x 1\'-3" x 4" (tapering to 3")' % f1(L), '%s x 1.25 x 0.333 = %s cft; #3 @ 6" x 2\'-9" + 3 distribution bars' % (f1(L), f2(q))
    if k == 'D-PR':
        return 'provisional allowance (front canopy, fins and projections on the 3D views)', '20 cft concrete + 150 ft of #3'
    if k == 'D-CP':
        L = R0.PARA_FF_L + R0.SF_PERIM
        return ('terrace %s ft + mumty %s ft = %s ft x 9" x 3"' % (f1(R0.PARA_FF_L), f1(R0.SF_PERIM), f1(L)),
                '%s x 0.75 x 0.25 = %s cft; #3: 2 x %s x 1.05' % (f1(L), f1(q), f1(L)))
    if k.startswith('E-'):
        fl = k[2:]; sheet = {'GF': 'S-06', 'FF': 'S-07', 'SF': 'S-08'}[fl]
        kg = sum(v for kk, v in r0mat(it).items() if kk.startswith('ST'))
        return ('%s sft of slab; every bar set on %s (bar size, spacing, width covered, bar length)' % (f1(R0.SLAB[fl]), sheet),
                'bars = width x 12 / spacing + 1; length + 0.6 ft (cranked) or + 0.3 ft (extra top); trimmers; chairs 1.5 ft per 12 sft = %s kg' % f1(kg))
    raise KeyError(k)
for k, g in RCC0:
    it = R0I[k]
    fl = 'GF' if 'GF' in k else ('FF' if 'FF' in k else ('SF' if k.endswith('SF') and k != 'D-SF' else ''))
    loc = LOC.get(fl, 'Stair' if k in ('D-SF', 'D-SP') else ('Front elevation' if k == 'D-PR' else ('All parapets' if k == 'D-CP' else '')))
    reg = 'E1' + (', E2' if k == 'D-LGF' else '') + (', E4' if k.startswith('E-') else '')
    desc = it['desc']
    if k == 'D-LGF': desc += ' - includes the 8\'-0" DL-1 over the 6\'-6" dining opening'
    dims, work = rcc_dw(k, it)
    add('S8', '8.' + k[2:], loc, desc, dims, work, it['qty'], it['unit'], r0mat(it), reg, g)
# E3 sunken slabs
BATHS = [('First-floor bath (rear-left) 8\'-0" x 6\'-4½"', 8.0, 6.375), ('First-floor bath (right) 9\'-0" x 6\'-0"', 9.0, 6.0),
         ('First-floor bath (front-left) 10\'-0" x 6\'-0"', 10.0, 6.0), ('Mumty bath 4\'-9" x 5\'-6"', 4.75, 5.5)]
A_SUNK = sum(a*b for _, a, b in BATHS); P_SUNK = sum(2*(a + b) for _, a, b in BATHS)
v = P_SUNK*0.5*(5.5/12)
sk_st = {3: P_SUNK*12/9*2.5 + 2*P_SUNK}
add('S8', '8.SK1', '3 first-floor baths + mumty bath', 'Sunken slab 6": extra concrete (1:2:4) and steel at the drop (U-bars #3 @ 9" + 2 #3 along each edge)',
    'baths %s sft, perimeter %s ft; drop 6" x slab 5½"' % (fi(A_SUNK), f1(P_SUNK)),
    'concrete %s x 0.5 x 0.458; #3: %s x 12/9 x 2.5 + 2 x %s' % (f1(P_SUNK), f1(P_SUNK), f1(P_SUNK)),
    v, 'cft', mix(conc(v, '1:2:4'), st(sk_st)), 'E3', 'Sunken slabs')
a = A_SUNK + P_SUNK*0.5
add('S8', '8.SK2', '3 first-floor baths + mumty bath', 'Waterproof coating in sunk areas: polymer-modified cementitious, 2 coats (~1.5 kg/m2 per coat)',
    'floor %s sft + sides %s ft x 6"' % (fi(A_SUNK), f1(P_SUNK)), '%s sft = %s m2 x 3.0 kg' % (fi(a), f1(a*SQM)),
    a, 'sft', {'COATW': a*SQM*3.0}, 'E3')
v = A_SUNK*0.75
add('S8', '8.SK3', '3 first-floor baths + mumty bath', 'Lightweight filling in sunk areas: brick-bat coba (broken bricks in 1:6 mortar), 9" deep to underside of floor finish',
    '%s sft x 9" (6" drop + 3" floor base)' % fi(A_SUNK), '%s cft: bats 0.70 cft/cft (9.5 bricks), 1:6 mortar 0.30 cft/cft' % fi(v),
    v, 'cft', mix({'BRK': v*0.70*C.BRICKS_PER_CFT}, mort(v*0.30, '1:6')), 'E3')
A_UF = (1705.0 - 245.0 - (A_SUNK - 26.125)) + (353.2 - 68.0 - 26.125)
v = A_UF*0.25
add('S8', '8.UF', 'First floor + mumty floor', 'Floor sub-base: 3" PCC 1:4:8 over first-floor and mumty floors (levels the 4" beam upstands, covers conduits), excluding sunken baths',
    '%s sft x 3"' % fi(A_UF), '(1,705 - 245 walls - %s baths) + (353 - 68 walls - 26 bath) = %s sft' % (fi(A_SUNK - 26.125), fi(A_UF)),
    v, 'cft', conc(v, '1:4:8'), 'D2 (Rev 0 assumption kept), E3')

# =============================================================== S9 ROOF WATERPROOFING AND TILES
T_A, M_A, B_A = ROOF['T_area'], ROOF['M_inner'], ROOF['BAL_A']
A_ROOF = T_A + M_A + B_A
SC = ROOF['screed']
v_scr = SC['terrace_2outlets']['vol'] + SC['mumty_1outlet']['vol'] + B_A*(1.5/12)
add('S9', '9.1', 'Terrace, mumty roof, first-floor front balcony', 'Slope screed 1:4 cement-sand at 1:100 to the drawn rain-water outlets, min ¾" at outlets',
    'terrace %s sft (avg %.1f", max %.1f"); mumty %s sft (avg %.1f", max %.1f"); balcony %s sft (avg 1½")' % (
        fi(T_A), SC['terrace_2outlets']['avg_in'], SC['terrace_2outlets']['max_in'], fi(M_A), SC['mumty_1outlet']['avg_in'],
        SC['mumty_1outlet']['max_in'], fi(B_A)),
    'grid calculation of screed thickness by outlet catchment = %s cft' % f1(v_scr), v_scr, 'cft', mort(v_scr, '1:4', 'SNDC'), 'F3')
PL_LEN = (ROOF['T_perim'] - ROOF['mumty_edge']) + ROOF['mumty_edge'] + ROOF['M_perim'] + (13.5 + 2*2.83)
N_PLINTH = 34
a_m = A_ROOF*1.10 + PL_LEN*1.0*1.10 + N_PLINTH*5.0*0.67 + 2*(5.75 + 1.5)*1.0
add('S9', '9.2', 'Terrace, mumty roof, balcony', 'Bitumen primer, ~0.3 L/m2', '%s sft roof + upturns' % fi(A_ROOF),
    '%s sft = %s m2 x 0.3 L' % (fi(a_m), f1(a_m*SQM)), a_m*SQM*0.3, 'L', {'PRIM': a_m*SQM*0.3}, 'F3')
add('S9', '9.3', 'Terrace, mumty roof, balcony', '4 mm torch-applied modified-bitumen membrane, 4" laps, turned 12" up parapets and mumty walls into a groove, dressed round solar plinths and tank platform',
    'roof %s sft; upturns %s ft x 12"; 34 plinths; tank platform' % (fi(A_ROOF), fi(PL_LEN)),
    '%s x 1.10 + %s x 1.10 + 34 x 5 ft x 8" + platform = %s sft = %s m2' % (fi(A_ROOF), fi(PL_LEN), fi(a_m), f1(a_m*SQM)),
    a_m*SQM, 'm2', {'MEMB': a_m*SQM}, 'F3, J3')
add('S9', '9.4', 'Terrace, mumty roof, balcony', 'LPG for torching membrane (~0.4 kg per m2)', '', '%s m2 x 0.4 kg' % f1(a_m*SQM),
    a_m*SQM*0.4, 'kg', {'LPG': a_m*SQM*0.4}, 'F3')
v = PL_LEN*(0.5*(4/12)**2)
add('S9', '9.5', 'All parapet and mumty-wall junctions', 'Cement fillet (gola) 4" x 4" in 1:3 at every parapet / wall junction',
    '%s ft' % fi(PL_LEN), '%s x 0.0556 cft/ft' % fi(PL_LEN), v, 'cft', mort(v, '1:3'), 'F3')
A_TILE = A_ROOF - N_PLINTH*1.5625 - 25.0
v_bed = A_TILE*0.75/12 + A_TILE*(1 - 40.5/45.70)*1.5/12
add('S9', '9.6', 'Terrace, mumty roof, balcony', 'Bhatta tiles 9" x 4½" x 1½" laid in 1:4 mortar (¾" bed), joints filled',
    '%s sft (less plinths and tank platform)' % fi(A_TILE),
    'tiles %s x 3.15/sft; mortar bed %s x 0.0625 + joints = %s cft' % (fi(A_TILE), fi(A_TILE), f1(v_bed)),
    A_TILE, 'sft', mix({'TILE': A_TILE*3.15}, mort(v_bed, '1:4')), 'F3')

# =============================================================== S10 CHICKEN MESH AND PLASTER
L_GF = R0.FLOORLEN['GF'][0] + R0.FLOORLEN['GF'][1]
L_FF = R0.FLOORLEN['FF'][0] + R0.FLOORLEN['FF'][1]
L_SF = R0.SF9_L + R0.SF45_L
L_LIN = sum(L*n for fl in R0.LINTELS for t, L, n in R0.LINTELS[fl])
mesh12 = 2*(L_GF + L_FF + L_SF) + 2*L_LIN + EXT + 2*(R0.PARA_FF_L + R0.SF_PERIM) + 26.5 + 22 + 59
CH_EL = 39*7 + 79*6 + 10*3 + 3*12 + 12*8
CH_PL = 0.6*1068 + 0.5*190 + 0.8*200
mesh9 = CH_EL + CH_PL
rolls = mesh12*1.10/300 + mesh9*1.10/400
add('S10', '10.1', 'All brick / RCC junctions, both faces', 'Galvanised chicken mesh strips 12" wide over every brick/RCC junction (slab edges, lintels, plinth beam, coping, chajjas, column, stairs)',
    'slab edges 2 x %s ft; lintels 2 x %s ft; plinth beam %s; coping 2 x %s; chajjas 26.5; column 22; stairs 59' % (
        fi(L_GF + L_FF + L_SF), fi(L_LIN), fi(EXT), fi(R0.PARA_FF_L + R0.SF_PERIM)),
    '%s rft of 12" strip (3 strips per 3-ft-wide roll = 300 rft/roll)' % fi(mesh12), mesh12, 'rft',
    {'MESH': mesh12*1.10/300, 'NAIL': mesh12/300*1.0}, 'D3')
add('S10', '10.2', 'All concealed conduit and pipe chases', 'Galvanised chicken mesh strips 9" wide over every concealed chase',
    'electrical chases %s rft; plumbing / gas / AC-drain chases %s rft' % (fi(CH_EL), fi(CH_PL)),
    '%s rft of 9" strip (4 strips per roll = 400 rft/roll)' % fi(mesh9), mesh9, 'rft',
    {'MESH': mesh9*1.10/400, 'NAIL': mesh9/400*1.0}, 'D3')
def plaster_parts(fl):
    l9, l45, H, ext_l, pl_l = R0.FLOORLEN[fl]
    gross = (l9 + l45)*2*H; inn = gross - pl_l*H - ext_l*H
    od_i = od_e = rev = 0.0
    for (d, w, h, t, n, isext) in R0.OPS[fl]:
        if isext: od_e += w*h*n; od_i += w*h*n
        else: od_i += 2*w*h*n
        rev += (2*h + w)*t*n
    return dict(L=l9 + l45, H=H, gross=gross, inn=inn, ext=ext_l*H, ext_l=ext_l, pl=pl_l*H, od_i=od_i, od_e=od_e, rev=rev)
for fl, name in (('GF', 'Ground floor'), ('FF', 'First floor'), ('SF', 'Mumty')):
    it = R0I['F-I' + fl]; P = plaster_parts(fl)
    add('S10', '10.I' + fl, name, 'Internal plaster ½" 1:4 on all walls',
        'walls %s ft x 2 faces x %.2f ft = %s sft' % (f1(P['L']), P['H'], fi(P['gross'])),
        'less outer faces %s and property-line faces %s = %s; less openings %s; plus 0.6 x reveals %s = %s sft' % (
            fi(P['ext']), fi(P['pl']), fi(P['inn']), fi(P['od_i']), fi(P['rev']), fi(it['qty'])),
        it['qty'], 'sft', pl(it['qty'], 0.5, '1:4'), 'F1, F2')
for fl, name in (('GF', 'Ground floor'), ('FF', 'First floor'), ('SF', 'Mumty')):
    it = R0I['F-E' + fl]; q = it['qty']; P = plaster_parts(fl)
    dims = 'outer walls %s ft x %.2f ft = %s sft' % (f1(P['ext_l']), P['H'], fi(P['ext']))
    w = 'less openings %s; plus 0.4 x reveals %s = %s sft' % (fi(P['od_e']), fi(P['rev']), fi(q))
    if fl == 'GF':
        q = q - 133.4*(R0.FFL_ABOVE_ROAD + 0.5) + 133.4*2.0
        dims += ' + exposed plinth 133.4 ft x 2\'-0" (outside levels now +1\'-0" to +1\'-3"; was 3\'-3")'
        w = 'less openings %s; plus 0.4 x reveals %s; plus plinth 266.8 = %s sft' % (fi(P['od_e']), fi(P['rev']), fi(q))
    add('S10', '10.E' + fl, name, 'External plaster ¾" 1:4 on outer faces%s' % (' incl. exposed plinth' if fl == 'GF' else ''),
        dims, w, q, 'sft', pl(q, 0.75, '1:4'), 'F1, F2')
it = R0I['F-P']
add('S10', '10.P', 'Terrace and mumty parapets', 'Parapet plaster ¾" 1:4, both faces and top',
    'terrace %s ft x (2 x %.2f + 0.75) + mumty %s ft x (2 x %.2f + 0.75)' % (f1(R0.PARA_FF_L), R0.PARA_FF_H, f1(R0.SF_PERIM), R0.PARA_SF_H),
    '%s + %s = %s sft' % (fi(R0.PARA_FF_L*(R0.PARA_FF_H*2 + 0.75)), fi(R0.SF_PERIM*(R0.PARA_SF_H*2 + 0.75)), fi(it['qty'])),
    it['qty'], 'sft', pl(it['qty'], 0.75, '1:4'), 'F1')
A_SOFF = 102.4 + 38.7 + 33.0 + 26.5*1.25 + R0.g2*3.5
add('S10', '10.S', 'Car-porch slab, entrance canopy, chajjas, stair over rear porch', 'External soffit plaster ⅜" 1:3 (separate line - can be deleted)',
    'porch 102 + canopy 39 + entrance 33 + chajjas 33 + stair %s sft' % fi(R0.g2*3.5), '%s sft' % fi(A_SOFF),
    A_SOFF, 'sft', pl(A_SOFF, 0.375, '1:3'), 'F1')

# =============================================================== S11 SEWERAGE AND DRAINAGE
NMH = 9
MH_DW = {'H7': ('9 nos x 4\'-6" x 4\'-6" x 4\'-3" deep (2\'-0" inside + 9" walls + 6" working space each side)', '9 x 4.5 x 4.5 x 4.25 = %s cft'),
         'H8': ('9 nos x 3\'-6" x 3\'-6" x 4"', '9 x 3.5 x 3.5 x 0.333 = %s cft'),
         'H9': ('9 nos, 2\'-0" x 2\'-0" inside, 9" walls, average 3\'-6" deep; centre-line 4 x 2\'-9" = 11 ft',
                '9 x 11 x 0.75 x 3.5 = %s cft (Rev 0 took 9 x 11 x 3.5 = 346.5, missing the 9" thickness - corrected)'),
         'H10': ('9 nos x 1.5 cft (benching and half-round channels)', '9 x 1.5 = %s cft'),
         'H11': ('9 nos x (4 walls x 2\'-0" x 3\'-6" + benching 4 sft)', '9 x 32 = %s sft')}
MH_BRICK = NMH*4*2.75*0.75*3.5
for k in ('H7', 'H8', 'H9', 'H10', 'H11'):
    it = R0I[k]
    info = {'EXC': it['qty']} if k == 'H7' else {}
    q = MH_BRICK if k == 'H9' else it['qty']
    mat = bw(q, '1:4') if k == 'H9' else r0mat(it)
    add('S11', '11.' + k, 'Manholes (9 nos, sheet 17)', it['desc'], MH_DW[k][0], MH_DW[k][1] % f1(q), q, it['unit'], mat, 'H2', 'Manholes', info)
bfm = R0I['H7']['qty'] - NMH*3.5*3.5*3.0
add('S11', '11.MB', 'Manholes', 'Back-filling around manholes with excavated earth', '', '%s - 9 x 3.5 x 3.5 x 3.0' % fi(R0I['H7']['qty']),
    bfm, 'cft', {}, 'H2', info={'BACKFILL': bfm})
v = 7*2.75*2.75*0.25
add('S11', '11.MC', '7 manholes in passages and lawn', 'RCC cover slabs 3" (1:2:4), #3 @ 6" both ways', '7 x 2\'-9" x 2\'-9" x 3"',
    '7 x 2.75 x 2.75 x 0.25; #3: 7 x 35 ft', v, 'cft', mix(conc(v, '1:2:4'), st({3: 7*35})), 'H2', 'Manhole covers')
add('S11', '11.CI', 'Manholes in front and rear car porches', 'Heavy-duty cast-iron manhole cover with frame, 20" x 20"', '2 nos', '2',
    2, 'nos', {'CICOV': 2}, 'H2')
for i, p in enumerate([p for p in R0.PIPES if p['group'].startswith(('Sewerage', 'Rain'))]):
    key = {'5"': 'UP5', '4"': 'UP4', '3"': 'UP3'}[p['size']] if p['group'].startswith('Sewerage') else 'RWP3'
    add('S11', '11.P%d' % (i + 1), 'House, passages, roofs', '%s %s: %s' % (p['group'], p['size'], p['desc']), '', p['basis'],
        p['ft'], 'ft', {key: p['ft']}, 'H2')
add('S11', '11.F', 'Sewer / rain-water system', 'UPVC fittings: 5" (bends 8, Y-tees 6, sockets 9); 4" (WC connectors 8, bends 20, Y-tees 10, sockets 8, vent cowls 4, clean-outs 4); 3" (floor traps 14, gully traps 3, bends 40, Y-tees 20, sockets 15, roof outlets 4, RWP shoes 4)',
    '', 'counts from sanitary and sewerage sheets', 177, 'nos', {'FUP5': 23, 'FUP4': 54, 'FUP3': 100}, 'H2')
add('S11', '11.AC', '10 A.C points to nearest washroom floor trap', 'A.C condensate drains ¾" (20 mm) PVC, concealed; stainless-steel mesh cap on each outlet',
    '10 x ~20 ft', '200 ft; 10 caps', 200, 'ft', {'PVC20': 200, 'SSCAP': 10}, 'H3, J1')

# =============================================================== S12 SEPTIC TANK (3 chambers)
SI_L, SI_W, SI_D = 4.833, 3.417, 5.0      # internal plan read as INTERNAL from sheet 17; 4'-0" liquid + 1'-0" freeboard
SE_L, SE_W = SI_L + 1.5, SI_W + 1.5
pit = (SE_L + 1.0 + 2.0)*(SE_W + 1.0 + 2.0)*3.5
add('S12', '12.1', 'Front lawn (sheet 17 position)', 'Excavation for septic tank, 1\'-0" working space each side',
    'pit %.2f x %.2f x 3\'-6" below NSL' % (SE_L + 3.0, SE_W + 3.0), '(%.2f x %.2f) x 3.5' % (SE_L + 3.0, SE_W + 3.0),
    pit, 'cft', {}, 'H1', info={'EXC': pit})
v = (SE_L + 1.0)*(SE_W + 1.0)*0.25
add('S12', '12.2', 'Septic tank', 'PCC 1:4:8, 3", under base', '%.2f x %.2f x 3"' % (SE_L + 1.0, SE_W + 1.0), '', v, 'cft', conc(v, '1:4:8'), 'H1')
bx, by = SE_L + 0.5, SE_W + 0.5
v = bx*by*0.5
add('S12', '12.3', 'Septic tank', 'RCC base 6" (1:2:4), #3 @ 6" both ways', '%.2f x %.2f x 6"' % (bx, by),
    '#3: (%d + %d) bars x length', v, 'cft',
    mix(conc(v, '1:2:4'), st({3: (math.ceil(by*2) + 1)*(bx - 0.25) + (math.ceil(bx*2) + 1)*(by - 0.25)})), 'H1', 'Septic tank')
v = 2*((SI_L + 0.75) + (SI_W + 0.75))*0.75*SI_D + 2*SI_W*0.375*4.5
add('S12', '12.4', 'Septic tank', '9" brick walls in 1:4 (5\'-0" high) + two 4½" baffle walls (4\'-6" high) forming THREE chambers',
    'internal %s x %s, depth 5\'-0" (4\'-0" liquid + 1\'-0" freeboard)' % ("4'-10\"", "3'-5\""),
    'walls 2 x (%.2f + %.2f) x 0.75 x 5.0 + baffles 2 x %.2f x 0.375 x 4.5' % (SI_L + 0.75, SI_W + 0.75, SI_W),
    v, 'cft', bw(v, '1:4'), 'H1')
v = SE_L*SE_W*(5/12) - 2*1.75*1.75*(5/12)
add('S12', '12.5', 'Septic tank', 'RCC top slab 5" (1:2:4) with two 1\'-9" x 1\'-9" openings, #3 @ 6" both ways + trimmers',
    '%.2f x %.2f x 5"' % (SE_L, SE_W), '', v, 'cft', mix(conc(v, '1:2:4'), st({3: 150})), 'H1', 'Septic tank')
v = 2*2.0*2.0*0.25
add('S12', '12.6', 'Septic tank', 'Two RCC covers 2\'-0" x 2\'-0" x 3" (1:2:4) with lifting hooks', '2 nos', '', v, 'cft',
    mix(conc(v, '1:2:4'), st({3: 2*5*2*2.0})), 'H1', 'Septic tank')
a_in = 2*(SI_L + SI_W)*SI_D + SI_L*SI_W + 2*2*SI_W*4.5
a_out = 2*(SE_L + SE_W)*SI_D
add('S12', '12.7', 'Septic tank', '¾" 1:3 waterproof plaster (with waterproofing compound) inside and outside',
    'inside walls + floor + baffles %s sft; outside %s sft' % (fi(a_in), fi(a_out)), '', a_in + a_out, 'sft',
    pl(a_in + a_out, 0.75, '1:3', True), 'H1')
add('S12', '12.8', 'Septic tank', 'T-pipe inlet and outlet (5" UPVC tees with 2 ft pipe each) and 3" vent pipe 12 ft with cowl',
    '2 tees 5" + 2 x 2 ft of 5" pipe; vent 3" x 12 ft + cowl', 'counted', 1, 'set', {'FUP5': 2, 'UP5': 4.0, 'UP3': 12.0, 'COWL': 1}, 'H1')
disp = (SE_L + 1.0)*(SE_W + 1.0)*0.25 + bx*by*0.5 + SE_L*SE_W*2.75
add('S12', '12.9', 'Septic tank', 'Back-filling around tank with excavated earth', '', '%s - %s (tank below NSL)' % (fi(pit), fi(disp)),
    pit - disp, 'cft', {}, 'H1', info={'BACKFILL': pit - disp})

# =============================================================== S13 WATER TANKS, WATER AND GAS PIPES
UI_L, UI_W, UI_H = 4.833, 3.417, 5.5      # same plan as septic tank; 5'-0" water + 6" freeboard
UE_L, UE_W = UI_L + 1.0, UI_W + 1.0
upit = (UE_L + 1.0 + 2.0)*(UE_W + 1.0 + 2.0)*(40/12)
add('S13', '13.1', 'Rear car porch (back of house)', 'Excavation for underground water tank, 1\'-0" working space each side',
    'pit %.2f x %.2f x 3\'-4" below NSL' % (UE_L + 3.0, UE_W + 3.0), '', upit, 'cft', {}, 'I1', info={'EXC': upit})
v = (UE_L + 1.0)*(UE_W + 1.0)*0.25
add('S13', '13.2', 'Underground water tank', 'PCC 1:4:8, 3", under base', '%.2f x %.2f x 3"' % (UE_L + 1.0, UE_W + 1.0), '', v, 'cft', conc(v, '1:4:8'), 'I2')
ubx, uby = UE_L + 0.5, UE_W + 0.5
v = ubx*uby*0.5
add('S13', '13.3', 'Underground water tank', 'RCC base 6" (1:1.5:3) with integral waterproofing admixture, #3 @ 6" both ways',
    '%.2f x %.2f x 6"' % (ubx, uby), '', v, 'cft',
    mix(conc(v, '1:1.5:3', True), st({3: (math.ceil(uby*2) + 1)*(ubx - 0.25 + 1.0) + (math.ceil(ubx*2) + 1)*(uby - 0.25 + 1.0)})), 'I2', 'Water tank')
pc = 2*((UI_L + 0.5) + (UI_W + 0.5))
v = pc*0.5*UI_H
wst = (pc*2 + 1)*(UI_H + 1.5) + (math.ceil(UI_H*2) + 1)*(pc + 2.0)
add('S13', '13.4', 'Underground water tank', 'RCC walls 6" (1:1.5:3) with integral waterproofing admixture, #3 @ 6" both ways (one central mesh)',
    'centre-line %.1f ft x 6" x %.1f ft' % (pc, UI_H), '#3: verticals %d x %.1f + horizontals %d x %.1f' % (pc*2 + 1, UI_H + 1.5, math.ceil(UI_H*2) + 1, pc + 2.0),
    v, 'cft', mix(conc(v, '1:1.5:3', True), st({3: wst})), 'I2', 'Water tank')
v = UE_L*UE_W*(5/12) - 1.75*1.75*(5/12)
add('S13', '13.5', 'Underground water tank', 'RCC top slab 5" (1:1.5:3) with one 1\'-9" x 1\'-9" opening; top 7" above porch level',
    '%.2f x %.2f x 5"' % (UE_L, UE_W), '', v, 'cft', mix(conc(v, '1:1.5:3', True), st({3: 120})), 'I2', 'Water tank')
add('S13', '13.6', 'Underground water tank', 'PVC water-stop 6" (150 mm) at base-to-wall joint', '%.1f ft + laps' % pc, '',
    pc + 1.5, 'ft', {'WSTOP': pc + 1.5}, 'I2')
a_i = 2*(UI_L + UI_W)*UI_H + 2*UI_L*UI_W
add('S13', '13.7', 'Underground water tank', 'Food-safe cementitious waterproof coating inside (walls, floor, soffit), 2 coats ~1.5 kg/m2 each',
    '%s sft' % fi(a_i), '%s m2 x 3.0 kg' % f1(a_i*SQM), a_i, 'sft', {'COATF': a_i*SQM*3.0}, 'I2')
a_o = 2*(UE_L + UE_W)*5.4
add('S13', '13.8', 'Underground water tank', 'Hot bitumen coat on outside of walls below ground (1 coat, 0.2 kg/sft)', '%s sft' % fi(a_o), '',
    a_o, 'sft', {'BIT': a_o*BIT_COAT}, 'I2')
add('S13', '13.9', 'Underground water tank', 'Lockable steel / CI manhole cover with frame, 2\'-0" x 2\'-0"', '1 no', '', 1, 'nos', {'UGTCOV': 1}, 'I2')
udisp = (UE_L + 1.0)*(UE_W + 1.0)*0.25 + ubx*uby*0.5 + UE_L*UE_W*(31/12)
add('S13', '13.10', 'Underground water tank', 'Back-filling around tank with excavated earth', '', '%s - %s' % (fi(upit), fi(udisp)),
    upit - udisp, 'cft', {}, 'I1', info={'BACKFILL': upit - udisp})
v = 5.0*5.0*(4/12)
add('S13', '13.11', 'Mumty roof, rear-right corner (sheet 24)', 'Plastic roof tank platform: RCC slab 5\'-0" x 5\'-0" x 4" (1:2:4), #3 @ 6" both ways, cast before membrane',
    '5\' x 5\' x 4"', '', v, 'cft', mix(conc(v, '1:2:4'), st({3: 2*11*5.0 + 10})), 'I4', 'Tank platform')
v = 2*5.0*0.75*1.5
add('S13', '13.12', 'Mumty roof', 'Platform supports: two 9" brick walls 1\'-6" high in 1:4, placed directly over the mumty walls below',
    '2 x 5\'-0" x 9" x 1\'-6"', '', v, 'cft', bw(v, '1:4'), 'I4')
a = 2*2*5.0*1.5 + 2*5.0*0.33
add('S13', '13.13', 'Mumty roof', 'Plaster ¾" 1:4 on platform walls and slab edges', '2 walls x 2 faces x 5\'-0" x 1\'-6" + slab edges 2 x 5\'-0" x 4"',
    '2 x 2 x 5.0 x 1.5 + 2 x 5.0 x 0.33 = %s sft' % f1(a), a, 'sft', pl(a, 0.75, '1:4'), 'I4')
WP = [('PPR114', 'Cold water PPR 1¼" PN-16: tank down-take', 38.0),
      ('PPR1', 'Cold water PPR 1" PN-16: pump rising main from UGT at back to roof tank (53 ft) + floor mains (40 ft)', 93.0),
      ('PPR34C', 'Cold water PPR ¾" PN-16: branch lines (measured 370 ft) + society supply to UGT (60 ft)', 430.0),
      ('PPR12C', 'Cold water PPR ½" PN-16: fixture drops 35 x 4 ft', 140.0),
      ('PPR34H', 'Hot water PPR ¾" PN-20: hot lines (measured) + geyser risers 36 ft', 360.0),
      ('PPR12H', 'Hot water PPR ½" PN-20: fixture drops 20 x 4 ft', 80.0),
      ('GI', 'Gas: SNGPL-approved medium-class GI ½"-¾" to kitchens, geyser, heaters + riser from meter', 189.8)]
for i, (k, d, L) in enumerate(WP):
    add('S13', '13.W%d' % (i + 1), 'House', d, '', 'measured on sheets 21-24 + risers (Rev 0), updated for pump at back', L, 'ft', {k: L}, 'I3, I5')
add('S13', '13.WF', 'House', 'PPR fittings (elbows ~120, tees ~60, sockets ~80, adaptors ~55, unions ~20), 24 ball/gate valves, ¾" float valve for UGT; GI fittings ~36',
    '', 'approximate counts', 1, 'set', {'FPPR': 335, 'VALVE': 24, 'FLOAT': 1, 'FGI': 36}, 'I3, I5')

# =============================================================== S14 ELECTRICAL CIVIL PROVISIONS AND SOLAR PLINTHS
PTS = R0.PTS
Lp = sum(p['light'] for p in PTS.values()); Sp = sum(p['socket'] for p in PTS.values()); SB = sum(p['sb'] for p in PTS.values())
AC_FT = 5*45 + 4*30 + 1*40
CONDUITS = [
    ('C34', '¾" PVC conduit: light/fan points %d x 12 ft' % Lp, Lp*12),
    ('C34', '¾" PVC conduit: socket points %d x 8 ft' % Sp, Sp*8),
    ('C34', '¾" PVC conduit: call bells at 2 gates x 40 ft', 80),
    ('C34', '¾" PVC conduit: Cat6 data to 5 Wi-Fi access points (2 GF, 2 FF, 1 mumty) to router point', 2*35 + 2*45 + 60),
    ('C34', '¾" PVC conduit: Cat6 to 7 CCTV cameras to NVR point (gates, porches, back gali, passages)', 7*50),
    ('C1', '1" PVC conduit: DB to %d switch-boards x 25 ft' % SB, SB*25),
    ('C1', '1" PVC conduit: own run to each of 10 A.C points (5 x 45 + 4 x 30 + 1 x 40 ft)', AC_FT),
    ('C1', '1" PVC conduit: earth conductors from 3 earth pits (house 25, lightning/surge 45, solar 55 ft)', 125),
    ('C1', '1" PVC conduit: water pump at UGT from backup DB', 60),
    ('C1', '1" PVC conduit: spare AC conduit, roof to inverter position', 30),
    ('C114', '1¼" PVC conduit: spare DC conduit, roof to inverter position', 30),
    ('C114', '1¼" PVC conduit: inverter AC-out to GF backup DB (45) + grid to inverter AC-in (45)', 90),
    ('C114', '1¼" PVC conduit: backup risers GF->FF backup DB (20) and ->mumty backup DB (32)', 52),
    ('C112', '1½" PVC conduit: meter to main DB + risers to FF and mumty DBs', 85),
    ('C112', '1½" PVC conduit: EV charger at front car porch from main DB (7.4 kW 1-ph / 11 kW 3-ph)', 35)]
CL = {}
for i, (k, d, L) in enumerate(CONDUITS):
    CL[k] = CL.get(k, 0) + L
    add('S14', '14.C%d' % (i + 1), 'House', d, '', 'allowance per point / measured run', L, 'ft', {k: L},
        {'C34': 'J2, J8', 'C1': 'J1, J5, J7, J8', 'C114': 'J4, J5', 'C112': 'J6, J8'}[k] if i not in (0, 1, 5) else 'J8')
acc = {}
for k, L in CL.items():
    s = k[1:]
    acc['BEND' + s] = math.ceil(L/10); acc['CPL' + s] = math.ceil(L/10)
acc['SOLV'] = math.ceil(sum(CL.values())/1000)
add('S14', '14.A', 'House', 'Conduit accessories: one bend and one coupler per 10 ft of conduit; PVC solvent', '', 'by conduit length',
    1, 'set', acc, 'J8')
add('S14', '14.B', 'House', 'Back boxes: 39 switch-board boxes, 79 socket boxes, 10 A.C boxes, 13 fan boxes with hooks, 110 light junction boxes, 5 access-point boxes, 7 CCTV boxes, 1 NVR/router box, 2 bell boxes',
    '', 'point count from sheets 13-16 + J2', 266, 'nos',
    {'BXSB': 39, 'BXSKT': 79, 'BXAC': 10, 'BXFAN': 13, 'BXLT': 110, 'BXAP': 5, 'BXCC': 7, 'BXNVR': 1, 'BXBELL': 2}, 'J1, J2, J8')
add('S14', '14.D', 'GF, FF, mumty', 'DB enclosures (empty): main 12-way GF, 8-way FF, 4-way mumty; backup (essential-load) 8-way GF, 6-way FF, 4-way mumty; EV isolator box',
    'one main + one backup DB per floor + EV box', '3 main + 3 backup + 1 EV = 7 nos', 7, 'nos', {'DB12': 1, 'DB8': 2, 'DB6': 1, 'DB4': 2, 'EVBOX': 1}, 'J5, J6')
add('S14', '14.E', 'Lawn near front door', '3 earth pits (house, solar/inverter, lightning/surge): copper-bonded rod 5/8" x 10 ft, 2 bags earthing compound each, inspection chamber with cover',
    '3 nos', '', 3, 'nos', {'ROD': 3, 'ECMP': 6, 'ECHM': 3}, 'J7')
add('S14', '14.S', 'Mumty and roof walls', '2" PVC sleeves through walls for DC/AC conduits, pump cable and earth leads (6 nos x 1 ft)', '6 nos x 1 ft', '6 x 1 = 6 ft',
    6, 'ft', {'SLV2': 6}, 'J4')
v = N_PLINTH*1.25*1.25*1.0
pst = {3: N_PLINTH*4*1.75, 2: N_PLINTH*2*4.5}
add('S14', '14.P', 'Terrace and mumty roof', 'Solar mounting plinths 15" x 15" x 12" high (1:2:4), 4 #3 starter bars cast into slab + 2 #2 links; 2 cast-in M12 x 250 mm galvanised J-bolts each; cast before membrane',
    '%d nos (23 panels x 650 W = 14.95 kWp)' % N_PLINTH, '%d x 1.25 x 1.25 x 1.0' % N_PLINTH, v, 'cft',
    mix(conc(v, '1:2:4'), st(pst), {'JBOLT': N_PLINTH*2}), 'J3', 'Solar plinths')
v = 3.0*1.5*0.5
add('S14', '14.I', 'Mumty laundry (inverter + sodium-ion battery position)', 'Raised RCC plinth 3\'-0" x 1\'-6" x 6" for battery cabinet (1:2:4)', '3\'-0" x 1\'-6" x 6"', '3.0 x 1.5 x 0.5 = 2.25 cft',
    v, 'cft', conc(v, '1:2:4'), 'J4')

# =============================================================== S15 BOUNDARY WALLS
BWALL = [('Front panels (1\'-6" + 15\'-2" + 3\'-0" + 3\'-11" splay)', 23.59, 6.0, 'street', 1.17),
         ('Left short panel at side gate', 3.0, 6.0, 'street', 1.0),
         ('Left long panel (42\'-3¼" + 1\'-6")', 43.77, 7.25, 'street', 1.0),
         ('Back wall on gali, 37\'-3" (new, G1)', 37.26, 7.0, 'gali', 1.0),
         ('Right side, front stretch (porch to front boundary)', 9.0, 6.0, 'neighbour', 1.25),
         ('Right side, rear-passage stretch', 5.4, 7.0, 'neighbour', 1.0)]
Lpan = sum(b[1] for b in BWALL); NP, NF = 7, 3
Lf = Lpan + NP*1.125 + NF*4.0
v = Lf*2.25*2.25*1.10
add('S15', '15.1', 'All boundary walls', 'Excavation to PCC bottom 2\'-3" below NSL (into firm soil)', '%s ft x 2\'-3" x 2\'-3"' % f1(Lf),
    '%.1f x 2.25 x 2.25 x 1.10' % Lf, v, 'cft', {}, 'G1, G3', info={'EXC': v})
exc_b = v
v = Lf*2.25*0.25
add('S15', '15.2', 'All boundary walls', 'PCC 1:4:8, 3" x 2\'-3"', '%s ft' % f1(Lf), '', v, 'cft', conc(v, '1:4:8'), 'G3')
vb1 = Lf*(1.875 + 1.5 + 1.125)*0.5
add('S15', '15.3', 'All boundary walls', 'Brick footing steps 22½" / 18" / 13½" (6" each) in 1:6, eccentric (all projections inside plot)',
    '%s ft' % f1(Lf), '%.1f x 4.5 x 0.5' % Lf, vb1, 'cft', bw(vb1, '1:6'), 'G3, C4')
vb2 = Lpan*0.75*(7.5 + 24)/12 + NP*1.125*1.125*(31.5/12) + NF*4.0*1.125*(31.5/12)
add('S15', '15.4', 'All boundary walls', 'Wall 9" and pillar bases in 1:6 from step top (-2\'-0") to underside of plinth band (+7½")',
    'panels %s ft x 9" x 2\'-7½"; pillars' % f1(Lpan), '', vb2, 'cft', bw(vb2, '1:6'), 'G3, D1')
v = Lf*0.75*0.5
add('S15', '15.5', 'All boundary walls', 'RCC plinth band 9" x 6" (1:2:4), 4 #3 + #2 rings @ 9" (as before)', '%s ft' % f1(Lf), '', v, 'cft',
    mix(conc(v, '1:2:4'), st({3: 4*Lf*1.05, 2: (Lf*12/9 + 1)*1.83})), 'G3', 'Boundary walls')
v = Lf*0.75*0.125
add('S15', '15.6', 'All boundary walls', 'DPC 1½" 1:2:4 with waterproofing compound + 2 coats hot bitumen on plinth band (top at plinth level +1\'-3")',
    '%s ft x 9"' % f1(Lf), '', v, 'cft', mix(conc(v, '1:2:4', True), {'BIT': Lf*0.75*2*BIT_COAT}), 'G3, B4')
wall = sum(L*0.75*(H - 0.25 - 1.25) for _, L, H, _, _ in BWALL)
add('S15', '15.7', 'All boundary walls', 'Boundary wall 9" in 1:6 from DPC (+1\'-3") to underside of coping; heights per sheets 11-12, back 7\'-0", right 6\'-0" / 7\'-0"',
    '; '.join('%s: %s ft to %s' % (n.split(' (')[0], f1(L), ("%d'-%d\"" % (int(H), round((H % 1)*12)))) for n, L, H, _, _ in BWALL),
    'sum L x 0.75 x (H - 3" coping - 1\'-3")', wall, 'cft', bw(wall, '1:6'), 'G1, G2, D1')
pil = NP*1.125*1.125*5.0 + NF*4.0*1.125*5.0
add('S15', '15.8', 'Gates and corners', 'Brick pillars in 1:4: 7 nos 13½" x 13½" + 3 nos 4\'-0" x 13½" feature pillars, DPC to cap (6\'-6" above road)',
    '', '7 x 1.266 x 5.0 + 3 x 4.5 x 5.0', pil, 'cft', bw(pil, '1:4'), 'G2, D1')
v = Lpan*1.0*0.25 + 10*1.5*1.5*0.25
add('S15', '15.9', 'All boundary walls', 'RCC coping 3" x 12" on panels + 10 pillar caps (1:2:4), 2 #3',
    'panels %s ft x 12" x 3" + 10 caps 1\'-6" x 1\'-6" x 3"' % f1(Lpan), '%s x 1.0 x 0.25 + 10 x 1.5 x 1.5 x 0.25 = %s cft; #3: 2 x %s x 1.05' % (f1(Lpan), f1(v), f1(Lpan)), v, 'cft',
    mix(conc(v, '1:2:4'), st({3: 2*Lpan*1.05})), 'G3', 'Boundary walls')
pb = sum(L*((H + 0.25) + (H - g + 0.25)) for _, L, H, _, g in BWALL) + Lpan*1.5 + NP*0.7*4.5*6.75 + NF*0.8*(2*4.0 + 2*1.125)*6.75
add('S15', '15.10', 'All boundary walls', 'Plaster ¾" 1:4 on BOTH faces of all boundary walls (all sides), coping and pillars',
    'outside face from road / gali / neighbour level, inside face from passage / porch / lawn level', '', pb, 'sft', pl(pb, 0.75, '1:4'), 'F1')
disp_b = Lf*2.25*0.25 + vb1 + Lpan*0.75*0.5
add('S15', '15.11', 'All boundary walls', 'Back-filling with excavated earth', '', '%s - %s' % (fi(exc_b), fi(disp_b)), exc_b - disp_b, 'cft', {},
    'G3', info={'BACKFILL': exc_b - disp_b})

# =============================================================== S16 EXTERNAL WORKS
bfe = exc_edge - (L_EDGE*2.5*0.25 + L_EDGE*2.25 + L_EDGE*0.75*0.5)
add('S16', '16.1', 'Edge walls', 'Back-filling around edge walls with excavated earth', 'trench %s cft less PCC, brick steps and wall below NSL' % f1(exc_edge),
    '%s - (%s x 2.5 x 0.25 + %s x 2.25 + %s x 0.75 x 0.5) = %s cft' % (f1(exc_edge), f1(L_EDGE), f1(L_EDGE), f1(L_EDGE), f1(bfe)), bfe, 'cft', {}, 'C6', info={'BACKFILL': bfe})
bfc = exc_col - (3.5*3.5*0.25 + 9.0 + 1.266*1.25)
add('S16', '16.2', 'Column footing', 'Back-filling around column footing', 'pit %s cft less PCC, footing and column below NSL' % f1(exc_col),
    '%s - (3.5 x 3.5 x 0.25 + 9.0 + 1.266 x 1.25) = %s cft' % (f1(exc_col), f1(bfc)), bfc, 'cft', {}, 'C5', info={'BACKFILL': bfc})
h = (PASS_FILL_TOP - NSL)/12
v = A_PASS*h*1.2
add('S16', '16.3', 'Left and rear passages', 'Earth filling to underside of paving (+4"), compacted', '%s sft x %.3f ft' % (fi(A_PASS), h),
    '%s x %.3f x 1.20' % (f1(A_PASS), h), v, 'cft', {}, 'A5, G4', info={'EFILL': v})
v = A_PASS*(2/12)*1.10
add('S16', '16.4', 'Left and rear passages', 'Sand 2" under paving base', '%s sft x 2"' % fi(A_PASS), '', v, 'cft', {'SNDM': v}, 'G4')
v = A_PASS*0.25
add('S16', '16.5', 'Left and rear passages', 'PCC 1:4:8, 3" paving base sloped 1:60 away from house to drains (tuff-tile finish in finishing estimate)',
    '%s sft x 3"' % fi(A_PASS), '', v, 'cft', conc(v, '1:4:8'), 'G4')
v = A_RAMP*(3.5/12)*1.2
add('S16', '16.6', 'Outside main and side gates', 'Ramps 1:6 (road to porch +1\'-3"): compacted earth fill', '%s sft' % fi(A_RAMP), '', v, 'cft', {},
    'G4', info={'EFILL': v})
v = A_RAMP*(2/12)*1.10
add('S16', '16.7', 'Outside main and side gates', 'Ramps: sand 2"', '%s sft' % fi(A_RAMP), '', v, 'cft', {'SNDM': v}, 'G4')
v = A_RAMP*0.25
add('S16', '16.8', 'Outside main and side gates', 'Ramps: PCC 1:4:8 3" base (finish in finishing estimate)', '%s sft' % fi(A_RAMP), '', v, 'cft',
    conc(v, '1:4:8'), 'G4')
it = R0I['G10']
add('S16', '16.9', 'Entrance, porch, rear and side doors', 'Steps: brick 1:5 + PCC 1:4:8 tread base (allowance, as before)',
    'entrance, two porch, rear-door and side-door steps', 'allowance: brickwork 40 cft (1:5) + PCC 20 cft (1:4:8) under treads',
    it['qty'], 'cft', r0mat(it), 'G4')
a = 22.3*1.25
add('S16', '16.10', 'Toe walls and rear-porch edges', 'Plaster ¾" 1:4 on exposed face of edge walls', '22.3 ft x 1\'-3"', '', a, 'sft',
    pl(a, 0.75, '1:4'), 'C6, F1')

# =============================================================== EARTH BALANCE
EXC = sum(i['info'].get('EXC', 0) for i in ITEMS)
BACK = sum(i['info'].get('BACKFILL', 0) for i in ITEMS)
SURPLUS_LOOSE = (EXC - BACK)*1.25
EFILL = sum(i['info'].get('EFILL', 0) for i in ITEMS)
EARTH_BUY = max(0.0, EFILL - SURPLUS_LOOSE)
add('S6', '6.9', 'Whole site', 'Earth (mitti) to buy for filling = fill required - surplus excavated earth re-used',
    'fill required %s cft (loose); surplus excavation %s cft bank x 1.25 = %s cft loose' % (fi(EFILL), fi(EXC - BACK), fi(SURPLUS_LOOSE)),
    '%s - %s' % (fi(EFILL), fi(SURPLUS_LOOSE)), EARTH_BUY, 'cft', {'EARTH': EARTH_BUY}, 'A4, A5')

# keep stage order and renumber items stage.n (original key kept in 'ref')
ORDER = {s: i for i, (s, _) in enumerate(STAGES)}
ITEMS.sort(key=lambda i: ORDER[i['stage']])
_cnt = {}
for _i in ITEMS:
    _n = _cnt[_i['stage']] = _cnt.get(_i['stage'], 0) + 1
    _i['ref'] = _i['code']; _i['code'] = '%s.%d' % (_i['stage'][1:], _n)
CODE = {i['ref']: i['code'] for i in ITEMS}

# =============================================================== MATERIAL MASTER (rates Oct 2026, Faisalabad)
# key: (name, unit, buy_unit_label, unit_size, wastage, rate PKR per unit, date, source, group)
RATE_SRC_CEM = 'ARY News "Cement Price in Pakistan Today", 15 Aug 2026 (Rs 1,500-1,610/bag); Sep 2026 brand list (Lucky 1,500-1,540, Bestway 1,430-1,570, Maple Leaf 1,570) - Faisalabad estimate'
M = {
 'CEM':  ('Cement OPC, 50 kg bag (Lucky / Bestway / Maple Leaf)', 'bag', 'bag', 1, 0.03, 1560, 'Sep 2026', RATE_SRC_CEM, 'Cement'),
 'BRK':  ('Bricks, first class (awwal), 9" x 4½" x 3"', 'nos', '1,000 bricks', 1000, 0.05, 16.0, 'Jan-Oct 2026', 'The News (PBS) Jan 2026: Lahore Rs 17,463/1,000; Pak Observer: Faisalabad DC-fixed A-class Rs 12,000/1,000 - market estimate Rs 16,000/1,000', 'Bricks'),
 'ST2':  ('Steel Grade 60 deformed, #2 (6 mm) rings', 'kg', '10 kg', 10, 0.04, 270, 'Sep 2026', 'Grade 60 Rs 258-265/kg (Daily Ausaf 19 Sep 2026 / Daily Qudrat 26 Sep 2026 price reports) + small-bar premium (estimated)', 'Steel'),
 'ST3':  ('Steel Grade 60 deformed, #3 (10 mm) (Amreli / Mughal / FF Steel)', 'kg', '10 kg', 10, 0.04, 262, 'Sep 2026', 'Grade 60 Rs 258-265/kg (Daily Ausaf 19 Sep 2026 / Daily Qudrat 26 Sep 2026 price reports)', 'Steel'),
 'ST4':  ('Steel Grade 60 deformed, #4 (12 mm)', 'kg', '10 kg', 10, 0.04, 262, 'Sep 2026', 'as #3', 'Steel'),
 'ST6':  ('Steel Grade 60 deformed, #6 (20 mm)', 'kg', '10 kg', 10, 0.04, 262, 'Sep 2026', 'as #3', 'Steel'),
 'BWIRE':('Binding wire, annealed 18 gauge', 'kg', '5 kg', 5, 0.0, 400, 'Oct 2026', 'estimated', 'Steel'),
 'SNDC': ('Chenab sand (concrete, screed)', 'cft', '50 cft', 50, 0.08, 65, 'Jul 2026', 'toolsfluent.com Pakistan construction cost guide 2026: river sand Rs 65/cft', 'Sand'),
 'SNDM': ('Ravi sand (mortar, plaster, blinding, fill)', 'cft', '50 cft', 50, 0.08, 40, 'Oct 2026', 'estimated (about 60% of Chenab sand rate)', 'Sand'),
 'CRS':  ('Crush ¾" down, Sargodha (bajri)', 'cft', '50 cft', 50, 0.05, 110, 'Jul 2026', 'toolsfluent.com 2026 guide: crush Rs 105/cft + delivery to Faisalabad (estimated)', 'Crush'),
 'KHG':  ('Stone ballast (khangar) 1½"-2½"', 'cft', '50 cft', 50, 0.05, 90, 'Oct 2026', 'estimated', 'Stone ballast'),
 'EARTH':('Earth (mitti) for filling, delivered', 'cft', '50 cft', 50, 0.0, 25, 'Oct 2026', 'estimated (~Rs 2,500 per 100-cft tractor-trolley); 20% compaction already in quantity', 'Earth'),
 'POLY': ('Polythene sheet 0.2 mm (800 gauge)', 'kg', 'kg', 1, 0.05, 550, 'Oct 2026', 'estimated', 'Waterproofing'),
 'BIT':  ('Hot bitumen 60/70 (drum)', 'kg', '10 kg', 10, 0.05, 280, '2025-26', 'Argus Media: NRL 60/70 bitumen FOB Karachi $380-420/t (Sep-Nov 2025) + local drum and dealer margin (estimated)', 'Waterproofing'),
 'ADMX': ('Integral waterproofing compound (powder), 1 kg per bag of cement', 'kg', 'kg', 1, 0.0, 350, 'Oct 2026', 'estimated', 'Waterproofing'),
 'PRIM': ('Bitumen primer', 'L', '4 L tin', 4, 0.05, 900, 'Oct 2026', 'estimated', 'Waterproofing'),
 'MEMB': ('4 mm APP/SBS modified-bitumen membrane (1 m x 10 m roll)', 'm2', 'roll (10 m2)', 10, 0.05, 700, 'Oct 2026', 'estimated, material only', 'Waterproofing'),
 'LPG':  ('LPG for torching (11.8 kg cylinder)', 'kg', 'cylinder (11.8 kg)', 11.8, 0.0, 300, 'Oct 2026', 'estimated (often supplied by applicator)', 'Waterproofing'),
 'COATW':('Polymer-modified cementitious waterproof coating (2-component)', 'kg', '5 kg', 5, 0.05, 450, 'Oct 2026', 'estimated', 'Waterproofing'),
 'COATF':('Food-safe (potable-water) cementitious coating', 'kg', '5 kg', 5, 0.05, 550, 'Oct 2026', 'estimated', 'Waterproofing'),
 'WSTOP':('PVC water-stop 150 mm', 'ft', 'ft', 1, 0.05, 650, 'Oct 2026', 'estimated', 'Waterproofing'),
 'TERM': ('Termiticide: bifenthrin 10% EC (1 L makes 200 L emulsion)', 'L', 'L', 1, 0.05, 3500, 'Oct 2026', 'estimated', 'Anti-termite'),
 'TILE': ('Bhatta (brick) roof tiles 9" x 4½" x 1½"', 'nos', '100 tiles', 100, 0.05, 20, 'Oct 2026', 'estimated', 'Roof tiles'),
 'MESH': ('Galvanised chicken mesh, roll 3 ft x 100 ft', 'roll', 'roll', 1, 0.05, 5500, 'Oct 2026', 'estimated', 'Chicken mesh'),
 'NAIL': ('Concrete nails with washers for mesh', 'kg', 'kg', 1, 0.0, 450, 'Oct 2026', 'estimated', 'Chicken mesh'),
 'UP5':  ('UPVC sewer pipe 5" (Dadex / Beta)', 'ft', '20-ft length', 20, 0.07, 420, 'Oct 2026', 'estimated', 'Sewer pipes'),
 'UP4':  ('UPVC sewer pipe 4"', 'ft', '20-ft length', 20, 0.07, 300, 'Oct 2026', 'estimated', 'Sewer pipes'),
 'UP3':  ('UPVC pipe 3" (waste / vent)', 'ft', '20-ft length', 20, 0.07, 200, 'Oct 2026', 'estimated', 'Sewer pipes'),
 'RWP3': ('UPVC rain-water pipe 3"', 'ft', '20-ft length', 20, 0.07, 200, 'Oct 2026', 'estimated', 'Sewer pipes'),
 'FUP5': ('UPVC fittings 5" (bends, tees, sockets)', 'nos', 'nos', 1, 0.0, 950, 'Oct 2026', 'estimated', 'Sewer pipes'),
 'FUP4': ('UPVC fittings 4"', 'nos', 'nos', 1, 0.0, 600, 'Oct 2026', 'estimated', 'Sewer pipes'),
 'FUP3': ('UPVC fittings 3" incl. floor / gully traps, roof outlets', 'nos', 'nos', 1, 0.0, 380, 'Oct 2026', 'estimated', 'Sewer pipes'),
 'COWL': ('Vent cowl 3"', 'nos', 'nos', 1, 0.0, 600, 'Oct 2026', 'estimated', 'Sewer pipes'),
 'CICOV':('Heavy-duty CI manhole cover with frame 20" x 20"', 'nos', 'nos', 1, 0.0, 15000, 'Oct 2026', 'estimated', 'Covers'),
 'UGTCOV':('Lockable steel / CI tank cover 2\' x 2\'', 'nos', 'nos', 1, 0.0, 12000, 'Oct 2026', 'estimated', 'Covers'),
 'PVC20':('PVC drain pipe ¾" (20 mm) for A.C condensate', 'ft', '10-ft length', 10, 0.07, 35, 'Oct 2026', 'estimated', 'Sewer pipes'),
 'SSCAP':('Stainless-steel mesh cap for A.C drain outlet', 'nos', 'nos', 1, 0.0, 350, 'Oct 2026', 'estimated', 'Sewer pipes'),
 'PPR114':('PPR pipe 1¼" (40 mm) PN-16 (Popular / Dadex / Master)', 'ft', '13-ft length', 13, 0.07, 270, 'May 2026', 'icons.com.pk PPRC price list 25 May 2026 (32 mm Rs 463-751/m) - 40 mm estimated', 'Water pipes'),
 'PPR1': ('PPR pipe 1" (32 mm) PN-16', 'ft', '13-ft length', 13, 0.07, 175, 'May 2026', 'icons.com.pk 25 May 2026: 32 mm Rs 463-751/m', 'Water pipes'),
 'PPR34C':('PPR pipe ¾" (25 mm) PN-16, cold', 'ft', '13-ft length', 13, 0.07, 110, 'May 2026', 'icons.com.pk 25 May 2026: 25 mm Rs 288-462/m', 'Water pipes'),
 'PPR12C':('PPR pipe ½" (20 mm) PN-16, cold', 'ft', '13-ft length', 13, 0.07, 70, 'May 2026', 'icons.com.pk 25 May 2026 (from Rs 186/m) - estimated', 'Water pipes'),
 'PPR34H':('PPR pipe ¾" (25 mm) PN-20, hot', 'ft', '13-ft length', 13, 0.07, 135, 'May 2026', 'icons.com.pk 25 May 2026 upper range - estimated', 'Water pipes'),
 'PPR12H':('PPR pipe ½" (20 mm) PN-20, hot', 'ft', '13-ft length', 13, 0.07, 85, 'May 2026', 'estimated', 'Water pipes'),
 'GI':   ('GI pipe medium class ½"-¾" for gas (SNGPL-approved)', 'ft', '20-ft length', 20, 0.07, 260, 'Oct 2026', 'estimated', 'Gas pipes'),
 'FPPR': ('PPR fittings (average)', 'nos', 'nos', 1, 0.0, 120, 'Oct 2026', 'estimated', 'Water pipes'),
 'VALVE':('Ball / gate valves (average)', 'nos', 'nos', 1, 0.0, 900, 'Oct 2026', 'estimated', 'Water pipes'),
 'FLOAT':('Float valve ¾" for underground tank', 'nos', 'nos', 1, 0.0, 2500, 'Oct 2026', 'estimated', 'Water pipes'),
 'FGI':  ('GI fittings ½"-¾"', 'nos', 'nos', 1, 0.0, 250, 'Oct 2026', 'estimated', 'Gas pipes'),
 'C34':  ('PVC conduit ¾" heavy gauge', 'ft', '10-ft length', 10, 0.07, 25, 'Oct 2026', 'estimated', 'Electrical'),
 'C1':   ('PVC conduit 1" heavy gauge', 'ft', '10-ft length', 10, 0.07, 38, 'Oct 2026', 'estimated', 'Electrical'),
 'C114': ('PVC conduit 1¼" heavy gauge', 'ft', '10-ft length', 10, 0.07, 56, 'Oct 2026', 'estimated', 'Electrical'),
 'C112': ('PVC conduit 1½" heavy gauge', 'ft', '10-ft length', 10, 0.07, 75, 'Oct 2026', 'estimated', 'Electrical'),
 'BEND34':('Conduit bend ¾"', 'nos', 'nos', 1, 0.0, 35, 'Oct 2026', 'estimated', 'Electrical'),
 'BEND1':('Conduit bend 1"', 'nos', 'nos', 1, 0.0, 55, 'Oct 2026', 'estimated', 'Electrical'),
 'BEND114':('Conduit bend 1¼"', 'nos', 'nos', 1, 0.0, 90, 'Oct 2026', 'estimated', 'Electrical'),
 'BEND112':('Conduit bend 1½"', 'nos', 'nos', 1, 0.0, 120, 'Oct 2026', 'estimated', 'Electrical'),
 'CPL34':('Conduit coupler ¾"', 'nos', 'nos', 1, 0.0, 15, 'Oct 2026', 'estimated', 'Electrical'),
 'CPL1': ('Conduit coupler 1"', 'nos', 'nos', 1, 0.0, 25, 'Oct 2026', 'estimated', 'Electrical'),
 'CPL114':('Conduit coupler 1¼"', 'nos', 'nos', 1, 0.0, 40, 'Oct 2026', 'estimated', 'Electrical'),
 'CPL112':('Conduit coupler 1½"', 'nos', 'nos', 1, 0.0, 55, 'Oct 2026', 'estimated', 'Electrical'),
 'SOLV': ('PVC solvent cement (tin)', 'nos', 'nos', 1, 0.0, 600, 'Oct 2026', 'estimated', 'Electrical'),
 'BXSB': ('Switch-board back box (assorted 3"x3" to 12"x3")', 'nos', 'nos', 1, 0.0, 250, 'Oct 2026', 'estimated', 'Electrical'),
 'BXSKT':('Socket back box', 'nos', 'nos', 1, 0.0, 120, 'Oct 2026', 'estimated', 'Electrical'),
 'BXAC': ('A.C point box', 'nos', 'nos', 1, 0.0, 150, 'Oct 2026', 'estimated', 'Electrical'),
 'BXFAN':('Fan box with hook', 'nos', 'nos', 1, 0.0, 180, 'Oct 2026', 'estimated', 'Electrical'),
 'BXLT': ('Round light junction box', 'nos', 'nos', 1, 0.0, 60, 'Oct 2026', 'estimated', 'Electrical'),
 'BXAP': ('Ceiling box for Wi-Fi access point', 'nos', 'nos', 1, 0.0, 150, 'Oct 2026', 'estimated', 'Electrical'),
 'BXCC': ('CCTV camera junction box', 'nos', 'nos', 1, 0.0, 150, 'Oct 2026', 'estimated', 'Electrical'),
 'BXNVR':('NVR / router enclosure box', 'nos', 'nos', 1, 0.0, 400, 'Oct 2026', 'estimated', 'Electrical'),
 'BXBELL':('Bell push box', 'nos', 'nos', 1, 0.0, 120, 'Oct 2026', 'estimated', 'Electrical'),
 'DB12': ('DB enclosure 12-way (empty)', 'nos', 'nos', 1, 0.0, 4500, 'Oct 2026', 'estimated', 'Electrical'),
 'DB8':  ('DB enclosure 8-way (empty)', 'nos', 'nos', 1, 0.0, 3200, 'Oct 2026', 'estimated', 'Electrical'),
 'DB6':  ('DB enclosure 6-way (empty)', 'nos', 'nos', 1, 0.0, 2800, 'Oct 2026', 'estimated', 'Electrical'),
 'DB4':  ('DB enclosure 4-way (empty)', 'nos', 'nos', 1, 0.0, 2000, 'Oct 2026', 'estimated', 'Electrical'),
 'EVBOX':('EV charger isolator enclosure', 'nos', 'nos', 1, 0.0, 2500, 'Oct 2026', 'estimated', 'Electrical'),
 'ROD':  ('Copper-bonded earth rod 5/8" x 10 ft', 'nos', 'nos', 1, 0.0, 9000, 'Oct 2026', 'estimated', 'Earthing'),
 'ECMP': ('Earthing compound, 25 kg bag', 'bag', 'bag', 1, 0.0, 3500, 'Oct 2026', 'estimated', 'Earthing'),
 'ECHM': ('Earth-pit inspection chamber with cover', 'nos', 'nos', 1, 0.0, 3000, 'Oct 2026', 'estimated', 'Earthing'),
 'SLV2': ('PVC sleeve 2"', 'ft', 'ft', 1, 0.0, 120, 'Oct 2026', 'estimated', 'Electrical'),
 'JBOLT':('M12 x 250 mm galvanised J-bolt with nut and washer', 'nos', 'nos', 1, 0.0, 250, 'Oct 2026', 'estimated', 'Solar plinths'),
}
BW_PER_KG = 0.010   # binding wire per kg of steel (10 kg/ton, E4)

# ---------------------------------------------------------------- totals
def totals(items):
    t = {}
    for i in items:
        for k, v in i['mat'].items():
            t[k] = t.get(k, 0) + v
    return t
NET = totals(ITEMS)
STEEL_NET = sum(NET.get(k, 0) for k in ('ST2', 'ST3', 'ST4', 'ST6'))
STEEL_GROSS = sum(NET.get(k, 0)*(1 + M[k][4]) for k in ('ST2', 'ST3', 'ST4', 'ST6'))
NET['BWIRE'] = STEEL_GROSS*BW_PER_KG
ORDER_KEYS = list(M.keys())
def purchase(k, net):
    unit = M[k][3]; w = M[k][4]
    g = net*(1 + w)
    return g, math.ceil(g/unit - 1e-9)*unit
SUMMARY = []
for k in ORDER_KEYS:
    n = NET.get(k, 0)
    if n <= 0: continue
    g, p = purchase(k, n)
    SUMMARY.append(dict(key=k, name=M[k][0], unit=M[k][1], net=n, w=M[k][4], gross=g, buy=p, buy_unit=M[k][2],
                        unit_size=M[k][3], rate=M[k][5], line_cost=g*M[k][5], cost=p*M[k][5], group=M[k][8]))
COST_LINES = sum(s['line_cost'] for s in SUMMARY)
COST_TOTAL = sum(s['cost'] for s in SUMMARY)
COVERED = 1898 + 1844 + 362

def item_cost(i):
    return sum(v*(1 + M[k][4])*M[k][5] for k, v in i['mat'].items())
for i in ITEMS:
    i['cost'] = item_cost(i)
STAGE_COST = {s: sum(i['cost'] for i in ITEMS if i['stage'] == s) for s, _ in STAGES}
STAGE_COST['S5'] += NET['BWIRE']*M['BWIRE'][5]*0   # binding wire shown separately (bought with steel)
BW_COST = NET['BWIRE']*M['BWIRE'][5]

if __name__ == '__main__':
    for i in ITEMS:
        print('%-4s %-7s %10.1f %-4s %10.0f | %s' % (i['stage'], i['code'], i['qty'], i['unit'], i['cost'], i['desc'][:90]))
    print()
    for s in SUMMARY:
        print('%-7s %-55s net %10.1f gross %10.1f buy %10.1f %-4s cost %12.0f' % (s['key'], s['name'][:55], s['net'], s['gross'], s['buy'], s['unit'], s['cost']))
    print('EXC %.0f BACK %.0f surplus loose %.0f EFILL %.0f buy %.0f' % (EXC, BACK, SURPLUS_LOOSE, EFILL, EARTH_BUY))
    print('steel net %.0f kg; gross %.0f; binding wire %.1f' % (STEEL_NET, STEEL_GROSS, NET['BWIRE']))
    print('COST lines %.0f  total (rounded purchases) %.0f  per sft %.0f' % (COST_LINES, COST_TOTAL, COST_TOTAL/COVERED))
    for s, n in STAGES: print(s, n, round(STAGE_COST[s]))
