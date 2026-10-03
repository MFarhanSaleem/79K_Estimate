# Writes blocks_rev1.json for build_docx_rev1.js.
# Every money figure and purchase quantity is read from the RECALCULATED Excel workbook, so the
# Word report and the Excel BOQ give identical totals. Descriptions come from rev1.json.
# usage: python3 content_rev1.py <recalculated.xlsx> <recalc_result.json> <solar.png> <out_blocks.json>
import json, os, sys, math
from collections import OrderedDict, defaultdict
import openpyxl

HERE = os.path.dirname(os.path.abspath(__file__))
R = json.load(open(os.path.join(HERE, 'rev1.json')))
XLSX, RECALC, IMG, OUT = sys.argv[1:5]
RC = json.load(open(RECALC))
LS = ' '

def f0(x): return '{:,.0f}'.format(x)
def f1(x): return '{:,.1f}'.format(x)
def f2(x): return '{:,.2f}'.format(x)
def rs(x): return 'Rs ' + f0(x)
def blank0(x, fmt=f1): return '' if not x or abs(x) < 1e-9 else fmt(x)
def ftin(x):
    s = '-' if x < 0 else '+'
    a = abs(x); f = int(a // 12); i = a - f * 12
    return '%s%d\'-%s"' % (s, f, ('%g' % i).replace('.5', '½'))

# ------------------------------------------------------------------ read the recalculated workbook
wb = openpyxl.load_workbook(XLSX, data_only=True)
wt = wb['Totals']
T = OrderedDict()
r = 5
while wt.cell(r, 1).value:
    c = [wt.cell(r, j).value for j in range(1, 15)]
    T[c[0]] = dict(name=c[1], unit=c[2], net=c[3], w=c[4], gross=c[5], bunit=c[6], usize=c[7], buy=c[8], nunits=c[9],
                   rate=c[10], cost=c[11], trolleys=c[12], group=c[13])
    r += 1
LAB = {}
for rr in range(r, r + 60):
    v = wt.cell(rr, 2).value
    if v: LAB[v] = wt.cell(rr, 12).value
TOTAL = LAB['TOTAL MATERIAL COST (purchase quantities)']
COVER = LAB['Covered area (sft) - GF 1,898 + FF 1,844 + mumty 362']
PER_SFT = LAB['Cost per sft of covered area (PKR)']
LINES = LAB['Total of BOQ lines before purchase rounding (incl. binding wire gross)']
ROUNDING = LAB['Rounding to buying units']
GROUP_COST = OrderedDict()
for k, t in T.items():
    GROUP_COST[t['group']] = GROUP_COST.get(t['group'], 0) + t['cost']
assert abs(sum(t['cost'] for t in T.values()) - TOTAL) < 0.5
GORDER = list(dict.fromkeys(t['group'] for t in T.values()))
KEYS_BY_GROUP = sorted(T.keys(), key=lambda k: (GORDER.index(T[k]['group']), list(T.keys()).index(k)))

wq = wb['BOQ']
BROWS = []
BOQ_TOTAL = None
for rr in range(5, wq.max_row + 1):
    st = wq.cell(rr, 1).value
    if st:
        BROWS.append(dict(stage=st, code=wq.cell(rr, 3).value, key=wq.cell(rr, 13).value, net=wq.cell(rr, 15).value or 0,
                          gross=wq.cell(rr, 18).value or 0, amt=wq.cell(rr, 20).value or 0))
    elif wq.cell(rr, 5).value and str(wq.cell(rr, 5).value).startswith('Total of BOQ lines'):
        BOQ_TOTAL = wq.cell(rr, 20).value
ws_ = wb['Stages']
STAGE_COST = OrderedDict()
STAGE_STEEL = OrderedDict()
for rr in range(4, 4 + len(R['stages'])):
    STAGE_COST[ws_.cell(rr, 1).value] = ws_.cell(rr, 3).value
    STAGE_STEEL[ws_.cell(rr, 1).value] = [ws_.cell(rr, j).value for j in (6, 7, 8, 9)]
BW_COST = ws_.cell(4 + len(R['stages']), 3).value
STAGES_TOTAL = ws_.cell(5 + len(R['stages']), 3).value
wst = wb['Steel']
STEEL = []
rr = 4
while wst.cell(rr, 1).value != 'TOTAL net':
    STEEL.append([wst.cell(rr, j).value for j in range(1, 7)])
    rr += 1
STEEL_TOT = [wst.cell(rr, j).value for j in range(1, 7)]
STEEL_BUY = [wst.cell(rr + 1, j).value for j in range(1, 7)]
BW_BUY = wst.cell(rr + 2, 6).value

# ---- consistency checks (Word figures = Excel figures)
item_amt = defaultdict(float); item_mat = defaultdict(lambda: defaultdict(float)); item_gross = defaultdict(lambda: defaultdict(float))
stage_amt = defaultdict(float); stage_gross = defaultdict(lambda: defaultdict(float)); stage_net = defaultdict(lambda: defaultdict(float))
for b in BROWS:
    item_amt[b['code']] += b['amt']; stage_amt[b['stage']] += b['amt']
    if b['key']:
        item_mat[b['code']][b['key']] += b['net']; item_gross[b['code']][b['key']] += b['gross']
        stage_gross[b['stage']][b['key']] += b['gross']; stage_net[b['stage']][b['key']] += b['net']
for s in STAGE_COST:
    assert abs(stage_amt[s] - STAGE_COST[s]) < 0.01, s
assert abs(sum(STAGE_COST.values()) - BOQ_TOTAL) < 0.01
assert abs(BOQ_TOTAL + BW_COST - LINES) < 0.01 and abs(LINES + ROUNDING - TOTAL) < 0.01
assert abs(STAGES_TOTAL - LINES) < 0.01
assert abs(TOTAL - R['cost_total']) < 0.5, (TOTAL, R['cost_total'])
assert RC.get('status') == 'success' and RC.get('total_errors') == 0
ITEMS = R['items']
IT = {it['code']: it for it in ITEMS}
assert set(item_amt) == set(IT), set(item_amt) ^ set(IT)

STEEL_KEYS = ['ST2', 'ST3', 'ST4', 'ST6']
SIZE = {'ST2': '#2', 'ST3': '#3', 'ST4': '#4', 'ST6': '#6'}
BULK = ['CEM', 'SNDC', 'SNDM', 'CRS', 'KHG', 'BRK']
SHORT = {
    'TERM': 'Termiticide', 'POLY': 'Polythene', 'BIT': 'Bitumen', 'ADMX': 'WP compound', 'PRIM': 'Primer', 'MEMB': 'Membrane',
    'LPG': 'LPG', 'COATW': 'WP coating', 'COATF': 'Food-safe coating', 'WSTOP': 'Water-stop', 'TILE': 'Bhatta tiles',
    'MESH': 'Chicken mesh', 'NAIL': 'Nails', 'EARTH': 'Earth (mitti)', 'BWIRE': 'Binding wire',
    'UP5': 'UPVC 5"', 'UP4': 'UPVC 4"', 'UP3': 'UPVC 3"', 'RWP3': 'RWP 3"', 'FUP5': 'Fittings 5"', 'FUP4': 'Fittings 4"',
    'FUP3': 'Fittings 3"', 'COWL': 'Vent cowl', 'CICOV': 'CI cover', 'UGTCOV': 'Lockable cover', 'PVC20': 'PVC ¾" drain',
    'SSCAP': 'SS mesh cap', 'PPR114': 'PPR 1¼"', 'PPR1': 'PPR 1"', 'PPR34C': 'PPR ¾"', 'PPR12C': 'PPR ½"', 'PPR34H': 'PPR ¾" hot',
    'PPR12H': 'PPR ½" hot', 'GI': 'GI gas pipe', 'FPPR': 'PPR fittings', 'VALVE': 'Valves', 'FLOAT': 'Float valve',
    'FGI': 'GI fittings', 'C34': 'Conduit ¾"', 'C1': 'Conduit 1"', 'C114': 'Conduit 1¼"', 'C112': 'Conduit 1½"',
    'BEND34': 'Bends ¾"', 'BEND1': 'Bends 1"', 'BEND114': 'Bends 1¼"', 'BEND112': 'Bends 1½"', 'CPL34': 'Couplers ¾"',
    'CPL1': 'Couplers 1"', 'CPL114': 'Couplers 1¼"', 'CPL112': 'Couplers 1½"', 'SOLV': 'Solvent tins',
    'BXSB': 'Switch-board boxes', 'BXSKT': 'Socket boxes', 'BXAC': 'A.C boxes', 'BXFAN': 'Fan boxes', 'BXLT': 'Light boxes',
    'BXAP': 'Wi-Fi AP boxes', 'BXCC': 'CCTV boxes', 'BXNVR': 'NVR box', 'BXBELL': 'Bell boxes', 'DB12': 'DB 12-way',
    'DB8': 'DB 8-way', 'DB6': 'DB 6-way', 'DB4': 'DB 4-way', 'EVBOX': 'EV isolator box', 'ROD': 'Earth rods',
    'ECMP': 'Earth compound', 'ECHM': 'Earth chambers', 'SLV2': 'Sleeve 2"', 'JBOLT': 'J-bolts M12'}
def unit(k): return R['rates'][k][1]
def qfmt(v, u):
    return f0(v) if u in ('nos', 'bag', 'roll', 'job', 'set') and abs(v - round(v)) < 1e-6 else f1(v)
def amt(x): return '-' if abs(x) < 0.5 else f0(x)
def it(code): return IT[code]
def q(code): return IT[code]['qty']

def compress(codes):
    """['4.1','4.2','4.3','5.1'] → '4.1-4.4' style ranges, in BOQ order."""
    order = {c: i for i, c in enumerate(i['code'] for i in ITEMS)}
    cs = sorted(set(codes), key=lambda c: order[c])
    out, run = [], []
    for c in cs:
        if run and c.split('.')[0] == run[-1].split('.')[0] and int(c.split('.')[1]) == int(run[-1].split('.')[1]) + 1:
            run.append(c)
        else:
            if run: out.append(run)
            run = [c]
    if run: out.append(run)
    return ', '.join(r[0] if len(r) == 1 else '%s-%s' % (r[0], r[-1]) for r in out)

REG_ITEMS = defaultdict(list)
for i in ITEMS:
    for code in [x.strip().split(' ')[0] for x in i['reg'].split(',') if x.strip()]:
        REG_ITEMS[code].append(i['code'])

B = []
def blk(**k): B.append(k)
def table(header, widths, rows, align=None, font=8):
    blk(type='table', header=header, widths=widths, rows=rows, align=align or [], font=font)
def row(*cells, kind=''):
    return dict(cells=[str(c) for c in cells], kind=kind)

PW, LW = 9906, 15038          # content widths, portrait / landscape (DXA)
steel_buy = sum(T[k]['buy'] for k in STEEL_KEYS)
steel_cost = sum(T[k]['cost'] for k in STEEL_KEYS)
EARTH = R['earth']
TH = R['thumb']
REV0 = R['rev0_buy']
plaster_int = q('10.3') + q('10.4') + q('10.5')
plaster_ext = q('10.6') + q('10.7') + q('10.8')
mesh_rft = q('10.1') + q('10.2')
DPC_CLEAR = R['dpc_clear']

# =================================================================== 1. SUMMARY
blk(type='section', orientation='PORTRAIT')
blk(type='title', title='House No. 79/K, WAPDA City, Faisalabad',
    subtitle='Grey Structure MATERIAL Estimate, Revision 1  |  Final Decisions Register applied  |  3 October 2026', before=0, size=34)
blk(type='h1', text='1. One-page summary')
blk(type='keys', keys=[
    ('Total material cost', rs(TOTAL), 'purchase quantities incl. wastage'),
    ('Covered area', f0(COVER) + ' sft', 'GF 1,898 + FF 1,844 + mumty 362'),
    ('Cost per sft', rs(PER_SFT), 'material only, no labour'),
    ('Steel (sariya)', f0(steel_buy) + ' kg', 'Grade 60, incl. 4% wastage')])
blk(type='p', size=17, text='Material only (no labour) at Faisalabad prices of October 2026; dimensions from the architect\'s drawings, RCC sizes and steel from the structural drawings, '
    'every line revised to the Final Decisions Register. Rev 0 was not priced, so it is compared by quantity. Recommended extras (Section 9) are NOT in the total.')
srows = []
def srow(name, keys_or_groups, unit_, rev0, qty=None, trolleys=None, by='key'):
    if by == 'key':
        cost = sum(T[k]['cost'] for k in keys_or_groups)
        if qty is None: qty = sum(T[k]['buy'] for k in keys_or_groups)
        if trolleys is None:
            tl = [T[k]['trolleys'] for k in keys_or_groups if isinstance(T[k]['trolleys'], (int, float))]
            trolleys = f0(sum(tl)) if tl else ''
    else:
        cost = sum(GROUP_COST[g] for g in keys_or_groups)
    srows.append((name, '' if qty is None else (f0(qty) if isinstance(qty, (int, float)) else qty), unit_, trolleys or '', cost, rev0))
srow('Cement OPC 50 kg (Lucky / Bestway / Maple Leaf)', ['CEM'], 'bags', f0(REV0['Cement (bags)']))
srow('Bricks, awwal (first class) 9" x 4½" x 3"', ['BRK'], 'nos', f0(REV0['Bricks (nos)']))
srow('Steel Grade 60 (sariya): #2 %s, #3 %s, #4 %s, #6 %s kg' % tuple(f0(T[k]['buy']) for k in STEEL_KEYS), STEEL_KEYS, 'kg', f0(REV0['Steel (kg)']))
srow('Binding wire (10 kg per ton of steel)', ['BWIRE'], 'kg', f0(REV0['Binding wire (kg)']))
srow('Crush ¾" Sargodha (bajri)', ['CRS'], 'cft', f0(REV0['Crush (cft)']))
srow('Chenab sand (concrete, screed)', ['SNDC'], 'cft', f0(REV0['Sand for concrete (cft)']))
srow('Ravi sand (mortar, plaster, blinding)', ['SNDM'], 'cft', '%s + %s fill sand' % (f0(REV0['Sand for mortar/plaster (cft)']), f0(REV0['Fill sand under floors (cft)'])))
srow('Khangar (stone ballast) 1½"-2½"', ['KHG'], 'cft', 'none')
srow('Earth (mitti) to buy for filling', ['EARTH'], 'cft', '3,250')
srow('Waterproofing: bitumen %s kg, membrane %s m2, polythene, compound, coatings, primer, LPG, water-stop' % (f0(T['BIT']['buy']), f0(T['MEMB']['buy'])),
     ['Waterproofing'], '', 'bitumen 320 kg', by='group')
srow('Bhatta roof tiles 9" x 4½" x 1½"', ['TILE'], 'nos', 'none')
srow('Anti-termite (%s L) and chicken mesh (%s rolls) with nails' % (f0(T['TERM']['buy']), f0(T['MESH']['buy'])), ['Anti-termite', 'Chicken mesh'], '', 'none', by='group')
srow('Sewer, water and gas pipes, fittings and covers', ['Sewer pipes', 'Covers', 'Water pipes', 'Gas pipes'], '', 'pipes only', by='group')
srow('Electrical conduits, boxes, DBs, earth pits, solar-plinth bolts', ['Electrical', 'Earthing', 'Solar plinths'], '', 'conduits only', by='group')
assert abs(sum(x[4] for x in srows) - TOTAL) < 0.5, (sum(x[4] for x in srows), TOTAL)
rows_ = [row(a, b, c, d, f0(e), f) for a, b, c, d, e, f in srows]
rows_.append(row('TOTAL MATERIAL COST', '', '', '', f0(TOTAL), '', kind='total'))
table(['Material (purchase quantity incl. wastage)', 'Buy', 'Unit', 'Trolley loads*', 'Cost (Rs)', 'Rev 0 qty'],
      [4800, 850, 500, 700, 1150, 1906], rows_, ['L', 'R', 'C', 'R', 'R', 'R'], font=7.5)
blk(type='note', size=15, text='* Tractor-trolley load = 100 cft (sand, crush, khangar, earth) or 2,000 bricks. Purchase = quantity with wastage rounded up to buying units (Section 5).')
blk(type='h2', text='Ten biggest changes from Rev 0')
blk(type='numbers', size=15, items=[
    'Foundation now exactly as sheet 05 (C1-C3): the S-02 RCC strip footing (417 cft concrete, 673 kg steel) is deleted; PCC 1:4:8 at -4\'-0", '
    'brick steps and 13½" wall to road level; foundation brickwork 1,075 → 1,717 cft.',
    'Plinth beam 9" x 9" moved to floor level with a proper DPC on top (B4, B5): 1½" 1:2:4 + waterproofing compound + 2 coats hot bitumen; '
    'top of DPC = FFL +2\'-9", %d" above the highest outside level.' % DPC_CLEAR,
    'Raised levels and full filling (A3-A5): house %s cft, both car porches %s cft, passages and ramps filled; earth to buy 3,250 → %s cft.' % (
        f0(q('6.2')), f0(q('6.3') + q('6.4')), f0(EARTH['buy'])),
    'New moisture-proof sub-floor (B2, B3): 4" khangar + 1" sand + 0.2 mm polythene + 3" PCC 1:4:8, no roṛi: %s cft khangar, %s sft polythene.' % (
        f0(q('6.5')), f0(q('6.7'))),
    'Roof waterproofing now in the total (F3): slope screed, primer, 4 mm torch-on membrane, gola and bhatta tiles on %s sft - %s.' % (
        f0(R['roof']['A_ROOF']), rs(STAGE_COST['S9'])),
    'Water storage (I1-I4): RCC overhead tank deleted; watertight ~515-gallon underground tank added at the back; RCC platform for a 500-gallon plastic roof tank.',
    'Plaster (F1, F2, D3): ceiling plaster deleted (-3,442 sft); soffits a separate line; boundary walls plastered both faces; chicken mesh on all junctions and chases (%s rolls).' % f0(T['MESH']['buy']),
    'Anti-termite treatment added (B1): %s L of bifenthrin 10%% EC concentrate for trenches, plinth fill and the outside perimeter.' % f0(T['TERM']['buy']),
    'Electrical civil works expanded (J1-J8): own 1" conduit to each of 10 A.C points, data and CCTV conduits, backup DBs, EV conduit, 3 earth pits, 34 solar plinths.',
    'Standards (D1, K2, E4): 9" walls in 1:6, lower wastage (cement 3%%, sand 8%%, steel 4%%, pipes 7%%): steel 8,080 → %s kg and cement 1,560 → %s bags despite the added work.' % (
        f0(steel_buy), f0(T['CEM']['buy'])),
])

# =================================================================== 2. BASIS
blk(type='h1', text='2. Basis of the estimate', newpage=True)
blk(type='h2', text='2.1 Documents, order of authority and scope')
blk(type='kv', size=17, lw=2500, lines=[
    ('Project', 'House No. 79/K, WAPDA City, Faisalabad, for Mr. Saleem. Ground floor, first floor and mumty (2nd-floor stair tower). Covered area %s sft.' % f0(COVER)),
    ('This revision', 'Rev 1, 3 October 2026. Replaces Rev 0 (30 September 2026) completely.'),
    ('Architect\'s working drawings', 'Faisal Associates, sheets 01-24 (16-08-2026), with 3D views and five bath-detail pages. They govern ALL dimensions and levels.'),
    ('Structural drawings', 'Fakhar Associates (M. Fakhar Iqbal Sheikh, PEC Civil 11697), 2026/L-20/S-01 to S-09 (14-08-2026). They govern ONLY the size and reinforcement of superstructure RCC members.'),
    ('Owner\'s decisions', 'Final Decisions Register A1-K3 (50 lines). Order of authority: (1) Register, (2) questionnaire answers, (3) earlier assumptions. '
     'The filled questionnaire itself was not attached, so the Register was used as the record of the answers.'),
    ('Scope (K1)', 'Grey-structure MATERIALS only. No labour, shuttering, scaffolding or finishes (Section 8).'),
    ('Prices', 'Faisalabad market, October 2026. Each rate has its date and source in 2.9; rates with no published source are marked "estimated". Rates and wastage can be changed in the Excel file (Rates sheet).'),
    ('Design approach', 'Sound, not over-built. Sheet 05 is followed with only the DPC added. Nothing is added "just in case": extra items are listed in Section 9 with cost and reason and are not in the total. '
     'No compromise on damp-proofing, termite protection, watertight tanks or superstructure RCC.'),
])
blk(type='h2', text='2.2 Materials and conversion factors (K3, as Rev 0)')
table(['Item', 'Specification / factor used'], [3000, 6906], [
    row('Cement', 'Ordinary Portland Cement (OPC) 50 kg bag - Lucky, Bestway, Maple Leaf or DG Khan. Soil is not saline and there is no ground water (A2), so sulphate-resisting cement is not needed.'),
    row('Sand', 'Chenab sand for concrete and roof screed; Ravi sand for mortar, plaster, blinding and under paving.'),
    row('Crush (bajri)', '¾" down, Sargodha.'),
    row('Stone ballast (khangar)', '1½"-2½" crushed stone, hand packed (no brick ballast / roṛi).'),
    row('Steel (sariya)', 'Grade 60 deformed bars - Amreli, Mughal or FF Steel. Weights: #2 (6 mm) 0.167, #3 (10 mm) 0.376, #4 (12 mm) 0.668, #6 (20 mm) 1.502 lb/ft.'),
    row('Bricks', 'Awwal (first class) burnt clay 9" x 4½" x 3"; 13.5 bricks per cft of brickwork including joints.'),
    row('Pipes', 'UPVC sewer pipes Dadex or Beta; PPR PN-16 cold / PN-20 hot - Popular, Dadex or Master; SNGPL-approved medium-class GI for gas.'),
    row('Concrete', 'Dry volume = wet volume x 1.57; 1 bag = 1.25 cft; mixes 1:1.5:3 (column, water tank), 1:2:4 (RCC), 1:4:8 (PCC).'),
    row('Mortar and plaster', 'Dry volume = wet x 1.33; 0.30 cft wet mortar per cft of brickwork; plaster +25% for uneven brick surface.'),
    row('Steel laps and binding wire', 'Laps, hooks, cranks and chairs included in net steel (laps 5%, as Rev 0); binding wire 10 kg per ton of gross steel (E4).'),
    row('Waterproofing compound', '1 kg per bag of cement in DPC, vertical DPC, septic plaster and water-tank concrete.'),
    row('Earth (mitti)', 'Excavated earth bulks 25% (loose = 1.25 x dug); filling quantities include 20% for compaction in 6" layers (A4).'),
    row('Trolley loads', 'One tractor-trolley = 100 cft of sand, crush, khangar or earth, or 2,000 bricks.'),
], ['L', 'L'], font=8)
blk(type='h2', text='2.3 Wastage (K2)')
table(['Material', 'Rev 0', 'Rev 1', 'Note'], [3300, 1300, 1300, 4006], [
    row('Cement', '5%', '3%', 'buy fresh stock per stage'), row('Sand (Chenab and Ravi)', '10%', '8%', ''),
    row('Crush, khangar', '5%', '5%', ''), row('Bricks', '5%', '5%', 'includes bats used in the work'),
    row('Steel', '5%', '4%', 'cut lengths planned from the bar schedule'), row('Pipes and conduits', '10%', '7%', 'fittings counted separately (no wastage)'),
    row('Bitumen, membrane, coatings, primer, mesh, tiles', '-', '5%', 'membrane laps are inside the quantity'),
    row('Earth, binding wire, fittings, boxes, covers', '-', '0%', 'counted items / compaction already allowed'),
], ['L', 'C', 'C', 'L'], font=8)

blk(type='h2', text='2.4 Level table - foundation to finished floor (B5)')
lev = sorted(R['levels'], key=lambda x: x[0])
table(['Level (in)', 'Level', 'What is at this level', 'Register'], [1000, 1200, 6306, 1400],
      [row(('%g' % l).replace('.5', '½'), ftin(l), t, g) for l, t, g in lev] +
      [row('', '', 'B5 check: top of DPC = FFL +2\'-9"; highest outside level = car porch +1\'-3"; clearance %d" (minimum 9") - PASS' % DPC_CLEAR, 'B5', kind='pass')],
      ['C', 'C', 'L', 'C'], font=8)
blk(type='note', text='Floor build-up above the compacted fill: khangar 4" + sand 1" + PCC 3" + DPC 1½" = 9½" (+1\'-11½" to +2\'-9"). The 1½" DPC concrete is laid continuous over the plinth beam and wall tops; the floor tile and its bed sit on the PCC inside the rooms so that the finished tile level equals the top of the DPC.')

blk(type='h2', text='2.5 Roof build-up check (F3): must fit within 6½"')
sc = R['screed']
def bu(m): return m + 0.16 + 0.75 + 1.5
table(['Roof', 'Rain-water outlets', 'Max. screed', 'Membrane + bed + tile', 'Max. build-up', 'Limit', 'Result'],
      [2100, 2000, 1000, 1500, 1100, 700, 1506], [
    row('Terrace (first-floor roof)', '2 (as drawn)', '%.1f"' % sc['terrace_2outlets']['max_in'], '0.16 + ¾ + 1½"', '%.1f"' % bu(sc['terrace_2outlets']['max_in']), '6½"', 'Too thick - used in total'),
    row('Terrace (first-floor roof)', '4 (recommended)', '%.1f"' % sc['terrace_4outlets']['max_in'], '0.16 + ¾ + 1½"', '%.1f"' % bu(sc['terrace_4outlets']['max_in']), '6½"', 'Fits - Section 9', kind='pass'),
    row('Mumty roof', '1 (as drawn)', '%.1f"' % sc['mumty_1outlet']['max_in'], '0.16 + ¾ + 1½"', '%.1f"' % bu(sc['mumty_1outlet']['max_in']), '6½"', 'Too thick - used in total'),
    row('Mumty roof', '2 (recommended)', '%.1f"' % sc['mumty_2outlets']['max_in'], '0.16 + ¾ + 1½"', '%.1f"' % bu(sc['mumty_2outlets']['max_in']), '6½"', 'Fits - Section 9', kind='pass'),
], ['L', 'C', 'C', 'C', 'C', 'C', 'L'], font=8)
blk(type='note', text='Screed slope 1:100 (within the 1:80-1:100 range), minimum ¾" at outlets, thickness found on a 6" grid by outlet catchment. '
    'The total uses the drawn outlets (more screed); approving the extra outlets keeps the build-up within 6½" and saves screed (Section 9, point 4 in Section 11).')

blk(type='h2', text='2.6 Edge and retaining walls (C6)')
edge_rows = [row(i + 1, n, '%s ft' % f1(L), 'D-D') for i, (n, L) in enumerate(R['misc']['EDGE'])]
edge_rows.append(row('', 'Total length', '%s ft' % f1(R['misc']['L_EDGE']), '', kind='subtotal'))
table(['No.', 'Edge wall (where the outside level changes)', 'Length', 'Section'], [600, 6306, 1700, 1300], edge_rows, ['C', 'L', 'R', 'C'], font=8)
blk(type='note', text='Built to sheet-05 section D-D on PCC 2\'-3" below NSL, 9" wall to the porch level with a DPC (items 4.7-4.10, 16.1, 16.10).')

blk(type='h2', text='2.7 Drawing register and where each sheet is used')
dr = [
    ('Pages 1-2', '3D front views', 'Elevation features 7.9; elevation RCC 8.23'),
    ('01', 'Ground floor plan (furnished)', 'Rooms and openings: walls 7.1-7.2; plaster 10.3, 10.6'),
    ('02', 'First floor plan (furnished)', 'Walls 7.3-7.4; plaster 10.4, 10.7'),
    ('03', 'Second floor (mumty) plan (furnished)', 'Walls 7.5-7.6; plaster 10.5, 10.8'),
    ('04', 'Ground floor plan with site levels', 'Levels A3; porch filling 6.3-6.4; edge walls 4.7-4.10; passages and ramps 16.3-16.8'),
    ('05', 'Foundation sections A-A to D-D', 'Excavation 2.1-2.3; footings 4.1-4.10; plinth beam and DPC 5.1-5.3'),
    ('06', 'Ground floor working plan', 'Walls 7.1-7.2; GF lintels 8.10; rear car porch 6.4'),
    ('07', 'First floor working plan', 'Walls 7.3-7.4; FF lintels 8.11; front balcony roof 9.1-9.6'),
    ('08', 'Second floor working plan', 'Walls and parapets 7.5-7.8; lintels 8.12'),
    ('09-10', 'Elevations', 'Elevation allowance 7.9, 8.23; parapets 7.7-7.8; external plaster 10.6-10.9'),
    ('11', 'Front boundary wall', 'Boundary walls 15.1-15.11 (heights G2)'),
    ('12', 'Left-side boundary wall', 'Boundary walls 15.1-15.11 (heights G2)'),
    ('5 pages', 'Bath details', 'Sunken baths 8.28-8.30; water points 13.17-13.19; floor traps 11.13'),
    ('13-15', 'Electrical plans GF, FF, 2F', 'Conduits, boxes, DBs 14.1-14.18'),
    ('16', 'Electrical legend', 'Box types 14.17'),
    ('17', 'Ground floor sewerage (manholes, septic tank)', 'Manholes and sewers 11.1-11.13; septic tank 12.1-12.9'),
    ('18-19', 'First and second floor sewerage', 'Soil and waste stacks 11.10-11.11'),
    ('20', 'Roof drainage', 'Rain-water pipes 11.12; outlets and screed 9.1'),
    ('21-23', 'Water supply and gas plans', 'PPR and GI pipes 13.14-13.21'),
    ('24', 'Top roof plan (water tank)', 'Tank platform 13.11-13.13; roof waterproofing 9.1-9.6; solar plinths 14.21'),
    ('S-01', 'Foundation layout plan and notes', 'Wall centre-lines (geometry); specifications 2.2'),
    ('S-02', 'Foundation sections 1-1 to 4-4, plinth beam', 'Plinth-beam steel 5.1 only (RCC strip footing not used - C1)'),
    ('S-03', 'Stair plan and reinforcement', 'Stairs 8.16-8.19'),
    ('S-04', 'Lintel key plans GF, FF, 2F', 'Lintels 8.10-8.12'),
    ('S-05', 'Door and window lintel details', 'Lintels 8.10-8.12'),
    ('S-06', 'Ground floor roof slab', 'Slab 8.2, beams 8.5, 8.7, bed plates 8.13, slab steel 8.25'),
    ('S-07', 'First floor roof slab', 'Slab 8.3, beams 8.6, 8.8, bed plates 8.14, slab steel 8.26'),
    ('S-08', 'Second floor (mumty) roof slab', 'Slab 8.4, beam 8.9, bed plates 8.15, slab steel 8.27'),
    ('S-09', 'Roof slab beam sections CB-1, CB-2', 'Concealed beams 8.5-8.9'),
]
table(['Sheet', 'Content', 'Used for (BOQ items)'], [1200, 3500, 5206], [row(*d) for d in dr], ['C', 'L', 'L'], font=7.5)
blk(type='h2', text='2.8 Building elements and where they are in the BOQ')
el = [
    ('Rooms and walls', 'All rooms of GF, FF and mumty; 9" and 4½" walls; parapets', '7.1-7.8 (masonry), 10.1-10.9 (mesh and plaster)'),
    ('Openings and lintels', '58 lintels (S-04 key plans + openings without marks, incl. 8\'-0" dining lintel)', '8.10-8.12; openings deducted in 7.1-7.6'),
    ('Slabs', '3 roof slabs (GF, FF, mumty) + porch cantilever; 4 sunken bath areas', '8.2-8.4, 8.25-8.27, 8.28-8.31'),
    ('Beams, bed plates, chajjas', 'CB-1, CB-2 concealed beams; 23 bed plates; 3 chajjas; parapet coping', '8.5-8.9, 8.13-8.15, 8.20-8.22, 8.24'),
    ('Stairs', 'Two zig-zag stairs (GF-FF, FF-mumty) with base footing', '8.16-8.19'),
    ('Column', 'Car-porch corner column 13½" with footing', '2.2, 4.5-4.6, 8.1, 16.2'),
    ('Tanks', 'Septic tank; underground water tank; roof-tank platform', '12.1-12.9; 13.1-13.10; 13.11-13.13'),
    ('Manholes', '9 manholes (7 RCC covers + 2 cast-iron covers)', '11.1-11.8'),
    ('Boundary walls', '6 stretches, %s ft of panels, 10 pillars, 2 gates' % f1(R['misc']['Lpan']), '15.1-15.11'),
    ('External works', 'Edge walls, passages, ramps, steps', '4.7-4.10, 16.1-16.10'),
]
table(['Element', 'On the drawings', 'BOQ items'], [2200, 4500, 3206], [row(*e) for e in el], ['L', 'L', 'L'], font=7.5)

blk(type='h2', text='2.9 Rates used - Faisalabad, October 2026 (rate, date, source)')
rr_ = []
grp = None
for k in KEYS_BY_GROUP:
    t = T[k]
    if t['group'] != grp:
        grp = t['group']; rr_.append(row(grp, kind='section'))
    v = R['rates'][k]
    rr_.append(row(t['name'], t['unit'], f2(t['rate']) if t['rate'] < 100 and t['rate'] != int(t['rate']) else f0(t['rate']), v[6], v[7]))
table(['Material', 'Unit', 'Rate (Rs)', 'Date', 'Source / note'], [3500, 600, 900, 1000, 3906], rr_, ['L', 'C', 'R', 'C', 'L'], font=7)
n_est = sum(1 for v in R['rates'].values() if 'estimated' in v[7])
blk(type='note', text='%d of %d rates are wholly or partly estimated and are marked "estimated" (local market judgement, mostly small items). The main cost items - cement, bricks, steel, Chenab sand, crush and PPR pipes - '
    'are based on 2026 published reports and make up about %d%% of the total.' % (n_est, len(R['rates']),
    round(100 * sum(T[k]['cost'] for k in ('CEM', 'BRK', 'ST2', 'ST3', 'ST4', 'ST6', 'SNDC', 'CRS', 'PPR114', 'PPR1', 'PPR34C', 'PPR12C', 'PPR34H')) / TOTAL)))

# =================================================================== 3. REVISION LOG
blk(type='section', orientation='LANDSCAPE')
blk(type='h1', text='3. Revision log - what changed from Rev 0 and why')
blk(type='h2', text='3.1 Quantity changes')
rl = []
area = None
for a, item, r0, r1, reg, note in R['revlog']:
    if a != area:
        area = a; rl.append(row(a, kind='section'))
    if isinstance(r0, (int, float)) and isinstance(r1, (int, float)):
        if item.startswith('Superstructure RCC'):
            s0, s1, ch = 'as Rev 0', 'as Rev 0', 'nil'
        elif item.startswith('Roof waterproofing'):
            s0, s1, ch = 'optional (not in total)', f1(r1), 'now in total'
        else:
            s0, s1 = f1(r0), f1(r1)
            d = r1 - r0
            ch = 'nil' if abs(d) < 0.05 else ('%+.1f' % d if abs(d) < 1000 else ('+' if d > 0 else '-') + f0(abs(d)))
    else:
        s0, s1, ch = str(r0), str(r1), 'changed'
    rl.append(row(item, s0, s1, ch, reg, note))
table(['Item', 'Rev 0', 'Rev 1', 'Change', 'Register', 'Why'], [4200, 1500, 1500, 1100, 1000, 5738], rl,
      ['L', 'R', 'R', 'R', 'C', 'L'], font=7.5)

blk(type='h2', text='3.2 Register compliance - every line A1 to K3, how it is applied and where')
REG = [
 ('A1', 'Road crown = ±0; natural surface level (NSL) 1\'-6" below road.', 'All levels in this estimate are from the road crown; NSL -1\'-6" (level table 2.4).'),
 ('A2', 'Firm soil about 2\'-0" below NSL; not saline; no ground water; use OPC.', 'PCC bottom about 6" into firm soil; OPC throughout; no sulphate-resisting cement or dewatering.'),
 ('A3', 'FFL +2\'-9", car porches +1\'-3", lawn +1\'-2"; recalculate excavation, back-filling and filling.', 'Excavation, back-filling and filling recomputed for the new levels.'),
 ('A4', 'Re-use clean excavated earth, buy the balance, 6" layers, 20% compaction.', 'Dug %s cft, back-filled %s cft, surplus re-used %s cft (loose); fill %s cft incl. 20%%; earth to buy %s cft (live formula in Excel).' % (
     f0(EARTH['exc']), f0(EARTH['back']), f0(EARTH['surplus_loose']), f0(EARTH['efill']), f0(EARTH['buy']))),
 ('A5', 'Fill house and both porches (full area) to sub-floor; passages, driveway and ramps to underside of paving; lawn not filled.', 'House %s, porches %s, passages %s, ramps %s cft; lawn excluded.' % (
     f0(q('6.2')), f0(q('6.3') + q('6.4')), f0(q('16.3')), f0(q('16.6')))),
 ('B1', 'Termiticide (bifenthrin or imidacloprid) on trenches, plinth fill and outside perimeter; give litres of concentrate.', 'Bifenthrin 10%% EC at 1:200: trenches %.1f L, plinth fill %.1f L, perimeter %.1f L = %.1f L (buy %s L).' % (
     q('3.1'), q('3.2'), q('3.3'), q('3.1') + q('3.2') + q('3.3'), f0(T['TERM']['buy']))),
 ('B2', 'Sub-floor: compacted earth, 4" khangar, 1" sand, polythene 0.2 mm (6" laps, turned up), 3" PCC 1:4:8; no roṛi.', 'Khangar %s cft, sand %s cft, polythene %s sft, PCC %s cft.' % (
     f0(q('6.5')), f0(q('6.6')), f0(q('6.7')), f0(q('6.8')))),
 ('B3', '"Graphite sheet" means the polythene.', '0.2 mm (800 gauge) polythene, %s kg.' % f0(T['POLY']['net'])),
 ('B4', 'Architect\'s beam at floor level plus 1½" 1:2:4 DPC with waterproofing admixture and 2 coats hot bitumen over all walls.', 'Plinth beam at floor level; DPC on house walls, edge walls and boundary walls.'),
 ('B5', 'Top of DPC = FFL (top of tile), at least 9" above the highest outside level; give a level table.', 'DPC top +2\'-9"; porch +1\'-3"; clearance %d" - PASS (table 2.4).' % DPC_CLEAR),
 ('B6', 'Vertical DPC: ¾" 1:3 plaster with waterproofing compound + 2 coats bitumen at 0.2 kg/sft per coat.', '%s sft on the fill side of the outer plinth walls (NSL to top of sub-floor).' % f0(q('5.3'))),
 ('C1', 'Sheet 05 footing; no RCC strip footing.', 'Sheet-05 brick footing; S-02 RCC strip footing (417 cft, 673 kg steel) deleted.'),
 ('C2', 'PCC bottom 2\'-6" below NSL (-4\'-0" from road).', 'PCC bottom -4\'-0" under all house walls.'),
 ('C3', 'PCC 1:4:8, 3" thick; foundation brickwork 1:6.', 'As decided in all footing items.'),
 ('C4', 'Eccentric footings on all property-line walls, including the powder-room wall.', 'Footing bands cut at the property line (right side incl. powder room); all boundary-wall footings eccentric.'),
 ('C5', 'Porch column 13½", 4 #6, #3 ties @ 6", 1:1.5:3, on 3\' x 3\' x 1\' footing with #4 @ 6", on 3" PCC.', 'As decided; column height 16\'-6" with the new levels.'),
 ('C6', 'Identify and list edge / retaining walls.', '6 walls, %s ft (table 2.6), to section D-D.' % f1(R['misc']['L_EDGE'])),
 ('D1', '9" walls 1:6; 4½" walls, parapets, pillars 1:4; boundary walls 1:6 with pillars 1:4.', 'Mortar ratios as decided in every wall item.'),
 ('D2', 'Awwal bricks at 13.5/cft; heights, parapets and elevation allowance as before; no privacy walls.', 'As decided; elevation allowance 5% kept; no privacy walls.'),
 ('D3', 'Chicken mesh strips on all junctions and chases; give running feet and rolls.', '12" strips %s rft + 9" strips %s rft = %s rolls (buy %s).' % (
     f0(q('10.1')), f0(q('10.2')), f1(T['MESH']['net']), f0(T['MESH']['buy']))),
 ('E1', 'Superstructure RCC as before.', 'Slabs, beams, lintels, stairs, chajjas, coping as Rev 0 (S-03 to S-09).'),
 ('E2', '8\'-0" dining lintel; 9" bearing; no lintel band.', 'DL-1 8\'-0" in GF lintels; 9" bearings; no lintel band.'),
 ('E3', '6" sunken slabs under FF and mumty baths: extra concrete and steel, coating, lightweight fill.', '%s sft sunk: concrete %s cft + %s kg #3; coating %s kg; brick-bat fill %s cft.' % (
     f0(R['misc']['A_SUNK']), f1(q('8.28')), f0(item_mat['8.28']['ST3']), f0(item_mat['8.29']['COATW']), f0(q('8.30')))),
 ('E4', 'Laps as before; binding wire 10 kg/ton; steel by size and member group.', 'Laps 5%% as Rev 0; binding wire %s kg; schedule in Section 6.' % f0(T['BWIRE']['buy'])),
 ('F1', 'Plaster all walls, parapets and boundary walls on both faces on all sides; no ceiling plaster; soffits separate.', 'Ceiling plaster deleted; soffits %s sft separate (10.10); boundary walls both faces.' % f0(q('10.10'))),
 ('F2', 'Internal ½" 1:4; external ¾" 1:4.', 'Internal %s sft; external %s sft; parapets %s sft.' % (f0(plaster_int), f0(plaster_ext), f0(q('10.9')))),
 ('F3', 'Roof: screed 1:80-1:100, primer, 4 mm torch membrane (4" laps, 12" upturn into groove), gola, bhatta tiles in 1:4; check 6½"; insulation only as a recommendation.', '%s sft of roof; build-up check 2.5; extra outlets and insulation in Section 9.' % f0(R['roof']['A_ROOF'])),
 ('G1', 'Own boundary walls on all sides: back 37\'-3" x 7\'-0" (gali), right walls on open stretches.', 'Back wall and right-side walls (9\'-0" and 5\'-5") added.'),
 ('G2', 'Street wall heights per drawing.', 'Front 6\'-0", left long panel 7\'-3" (sheets 11-12).'),
 ('G3', 'Boundary footing from NSL, PCC bottom about 2\'-3" below NSL; DPC at plinth-band level.', 'As decided; DPC on the plinth band (15.6).'),
 ('G4', 'Passages and driveway: fill, sand and PCC base sloped 1:60; ramps at both gates; steps as before.', 'Passages %s sft and ramps %s sft: fill, 2" sand, 3" PCC; steps 40 cft.' % (f0(R['misc']['A_PASS']), f0(R['misc']['A_RAMP']))),
 ('H1', 'Septic tank: 3 chambers at drawing size, liquid depth + freeboard, 3" PCC + 6" RCC base, 9" brick 1:4, baffles, RCC top with 2 openings and covers, ¾" 1:3 WP plaster in and out, T-pipes, vent.', 'Drawing size read as INTERNAL 4\'-10" x 3\'-5", 5\'-0" deep; all parts included; enlargement in Section 9.'),
 ('H2', 'Manholes as before; name two UPVC brands; CI / heavy covers in porches and driveway.', '9 manholes as Rev 0, with the Rev 0 brickwork arithmetic corrected (table 3.1); Dadex or Beta UPVC; 2 heavy-duty CI covers in the car porches.'),
 ('H3', '¾" A.C drains to floor traps with stainless-steel mesh caps.', '%s ft ¾" PVC, %d caps.' % (f0(q('11.14')), 10)),
 ('I1', 'Underground tank at the back, about septic size, at least 10 ft from septic tank and manholes.', 'Rear car porch, internal 4\'-10" x 3\'-5" x 5\'-6"; about 8½ ft from two rear manholes (Section 11).'),
 ('I2', 'Watertight: 6" RCC 1:1.5:3 + admixture, PVC water-stop, food-safe coating inside, bitumen outside, lockable cover, top 6"-9" above ground.', 'All included; top 7" above porch level.'),
 ('I3', 'Society supply → underground tank (float valve) → pump → plastic roof tank.', 'Float valve; 60 ft supply line; rising main 53 ft of 1" PPR.'),
 ('I4', 'No RCC overhead tank; plastic tank on a platform over walls; recommend capacity.', 'RCC tank deleted; 5\' x 5\' RCC platform on two 9" walls over mumty walls; 500-gallon tank recommended.'),
 ('I5', 'PPR PN-20 hot, PN-16 cold; SNGPL-approved gas pipe; brands; update rising main.', 'As decided (Popular / Dadex / Master).'),
 ('J1', '10 A.C points, each on its own 1" conduit.', '10 separate runs, %s ft.' % f0(q('14.7'))),
 ('J2', 'No TV / intercom; data conduits to Wi-Fi APs, CCTV conduits to one NVR point; propose positions.', '5 access points, 7 cameras, 1 NVR point (positions in Section 10).'),
 ('J3', 'Solar 15 kW, about 23 x 650 W on terrace and mumty roof; area; RCC plinths with cast-in bolts before the membrane.', '23 panels = 14.95 kWp; 34 plinths, 68 J-bolts (Section 7).'),
 ('J4', 'Two spare conduits (DC and AC); inverter and sodium-ion battery position on the 2nd floor.', '1¼" DC + 1" AC spares; inverter and battery in the mumty laundry with RCC plinth.'),
 ('J5', 'Backup sub-DB scheme.', 'Backup DBs on GF, FF and mumty fed from the inverter.'),
 ('J6', 'EV charger conduit for 7.4 kW single-phase or 11 kW three-phase.', '1½" conduit to the front car porch + isolator box.'),
 ('J7', 'Separate earth pits; state how many.', '3 pits: house, solar / inverter, lightning / surge.'),
 ('J8', 'Other electrical allowances kept; meter at the front.', 'Lights, fans, sockets, feeders and bells as Rev 0; meter at the front.'),
 ('K1', 'Material only; list exclusions.', 'No labour anywhere; exclusions in Section 8.'),
 ('K2', 'Wastage: cement 3%, sand 8%, crush 5%, bricks 5%, steel 4%, pipes 7%.', 'Applied per material (table 2.3; editable on the Excel Rates sheet).'),
 ('K3', 'Conversion factors as before; OPC, Chenab and Ravi sand, ¾" Sargodha crush, Grade-60 steel; name brands.', 'Table 2.2; brands in the material names.'),
]
assert len(REG) == 50 and len(set(c for c, _, _ in REG)) == 50
GLOBAL = {'A2': 'all concrete and mortar', 'K1': 'whole BOQ', 'K2': 'whole BOQ (Rates sheet)', 'K3': 'whole BOQ'}
for c in REG_ITEMS:
    assert c in {x[0] for x in REG}, c
reg_rows = []
for c, d, how in REG:
    if c[0] != (reg_rows and reg_rows[-1].get('_g')):
        pass
    where = compress(REG_ITEMS[c]) if REG_ITEMS.get(c) else GLOBAL.get(c, 'table 2.4')
    reg_rows.append(row(c, d, how, where))
table(['Line', 'Decision (Register)', 'How it is applied in Rev 1', 'BOQ items'], [650, 5300, 5600, 3488], reg_rows, ['C', 'L', 'L', 'L'], font=7)
REG_LOGGED = sum(1 for c, _, _ in REG if REG_ITEMS.get(c) or c in GLOBAL or c == 'B5')

# =================================================================== 4. DETAILED BOQ
blk(type='h1', text='4. Detailed BOQ by construction stage, with workings', newpage=True)
blk(type='p', size=17, text='Order of work: levels → excavation → anti-termite → foundations → plinth beam and DPC → filling and sub-floor → masonry → RCC → '
    'roof waterproofing and tiles → plaster → sewerage → septic tank → water tank → electrical and solar plinths → boundary walls → external works.')
blk(type='note', text='Material columns are NET quantities (before wastage). Each stage closes with its net total and its total with wastage (2.3). Amount = quantity with wastage x rate (Rs, shown to the rupee; '
    'subtotals are exact sums, so a column of rounded amounts can differ from its subtotal by a rupee; the closing block is shown to the paisa). Purchase rounding to buying units and trolley loads are in Section 5. Steel is by bar size: #2 = 6 mm, #3 = 10 mm, #4 = 12 mm, #6 = 20 mm.')
bq = []
for s, sname in R['stages']:
    bq.append(row('%s  %s' % (s, sname), kind='section'))
    st_items = [i for i in ITEMS if i['stage'] == s]
    for i in st_items:
        m = item_mat[i['code']]
        loc = '§' + i['loc'] + LS + i['desc']
        dw = LS.join(x for x in [i['dims'], ('= ' + i['work']) if i['work'] else ''] if x)
        steel = LS.join('%s %s' % (SIZE[k], f1(m[k])) for k in STEEL_KEYS if m.get(k))
        other = LS.join('%s %s %s' % (SHORT[k], qfmt(v, unit(k)), unit(k)) for k, v in m.items() if k not in BULK and k not in STEEL_KEYS)
        bq.append(row(i['code'], loc, dw, qfmt(i['qty'], i['unit']), i['unit'],
                      blank0(m.get('CEM')), blank0(m.get('SNDC')), blank0(m.get('SNDM')), blank0(m.get('CRS')), blank0(m.get('KHG')),
                      blank0(m.get('BRK'), f0), steel, other, i['reg'], amt(item_amt[i['code']])))
    n, g = stage_net[s], stage_gross[s]
    stn = LS.join('%s %s' % (SIZE[k], f1(n[k])) for k in STEEL_KEYS if n.get(k))
    stg = LS.join('%s %s' % (SIZE[k], f1(g[k])) for k in STEEL_KEYS if g.get(k))
    bq.append(row('', '%s total - net' % s, '', '', '', blank0(n.get('CEM')), blank0(n.get('SNDC')), blank0(n.get('SNDM')), blank0(n.get('CRS')),
                  blank0(n.get('KHG')), blank0(n.get('BRK'), f0), stn, '', '', f0(STAGE_COST[s]) if STAGE_COST[s] else '-', kind='subtotal'))
    if any(g.get(k) for k in BULK + STEEL_KEYS):
        bq.append(row('', '%s total - with wastage' % s, '', '', '', blank0(g.get('CEM')), blank0(g.get('SNDC')), blank0(g.get('SNDM')), blank0(g.get('CRS')),
                      blank0(g.get('KHG')), blank0(g.get('BRK'), f0), stg, '', '', '', kind='gross'))
alln = defaultdict(float); allg = defaultdict(float)
for s in STAGE_COST:
    for k, v in stage_net[s].items(): alln[k] += v
    for k, v in stage_gross[s].items(): allg[k] += v
bq.append(row('All stages', kind='section'))
bq.append(row('', 'All stages - net', '', '', '', f1(alln['CEM']), f1(alln['SNDC']), f1(alln['SNDM']), f1(alln['CRS']), f1(alln['KHG']), f0(alln['BRK']),
              LS.join('%s %s' % (SIZE[k], f1(alln[k])) for k in STEEL_KEYS), '', '', f2(BOQ_TOTAL), kind='subtotal'))
bq.append(row('', 'All stages - with wastage', '', '', '', f1(allg['CEM']), f1(allg['SNDC']), f1(allg['SNDM']), f1(allg['CRS']), f1(allg['KHG']), f0(allg['BRK']),
              LS.join('%s %s' % (SIZE[k], f1(allg[k])) for k in STEEL_KEYS), '', '', '', kind='gross'))
bq.append(row('', 'Binding wire, 10 kg per ton of gross steel (E4)', '', '%s' % f1(T['BWIRE']['net']), 'kg', '', '', '', '', '', '', '', 'Binding wire %s kg' % f1(T['BWIRE']['net']), 'E4', f2(BW_COST)))
bq.append(row('', 'Total of BOQ lines (before purchase rounding)', '', '', '', '', '', '', '', '', '', '', '', '', f2(LINES), kind='subtotal'))
bq.append(row('', 'Rounding up to buying units (Section 5.1)', '', '', '', '', '', '', '', '', '', '', '', '', f2(ROUNDING)))
bq.append(row('', 'TOTAL MATERIAL COST', '', '', '', '', '', '', '', '', '', '', '', '', f2(TOTAL), kind='total'))
table(['Item', 'Location / description', 'Dimensions / working', 'Qty', 'Unit', 'Cement (bags)', 'Chenab sand (cft)', 'Ravi sand (cft)', 'Crush (cft)',
       'Khangar (cft)', 'Bricks (nos)', 'Steel (kg)', 'Other materials', 'Register', 'Amount (Rs)'],
      [520, 2830, 2830, 700, 430, 620, 640, 640, 640, 620, 720, 900, 1508, 540, 900], bq,
      ['C', 'L', 'L', 'R', 'C', 'R', 'R', 'R', 'R', 'R', 'R', 'L', 'L', 'C', 'R'], font=6.5)

# =================================================================== 5. PURCHASE SCHEDULE
blk(type='h1', text='5. Purchase schedule', newpage=True)
blk(type='h2', text='5.1 Whole job - quantities to buy (governs the budget)')
pr = []
grp = None
for k in KEYS_BY_GROUP:
    t = T[k]
    if t['group'] != grp:
        grp = t['group']; pr.append(row(grp, kind='section'))
    tl = t['trolleys'] if isinstance(t['trolleys'], (int, float)) else ''
    pr.append(row(t['name'], qfmt(t['net'], t['unit']), '%d%%' % round(t['w'] * 100), qfmt(t['gross'], t['unit']),
                  '%s %s' % (qfmt(t['buy'], t['unit']), t['unit']), t['bunit'], f0(t['nunits']), f0(tl) if tl != '' else '',
                  f2(t['rate']) if t['rate'] != int(t['rate']) else f0(t['rate']), f0(t['cost'])))
pr.append(row('TOTAL MATERIAL COST', '', '', '', '', '', '', '', '', f0(TOTAL), kind='total'))
table(['Material', 'Net', 'Waste', 'With wastage', 'Purchase', 'Buying unit', 'No. of units', 'Trolley loads', 'Rate (Rs)', 'Cost (Rs)'],
      [5000, 1100, 650, 1150, 1450, 1500, 900, 850, 1000, 1438], pr, ['L', 'R', 'C', 'R', 'R', 'C', 'R', 'R', 'R', 'R'], font=7)
blk(type='note', text='Trolley loads: 100 cft per tractor-trolley (sand, crush, khangar, earth), 2,000 bricks per trolley. LPG is bought in 11.8 kg cylinders.')

blk(type='h2', text='5.2 Stage by stage - what to order before each stage')
blk(type='note', text='Quantities include wastage and are rounded up to buying units for each stage on its own, so the stage orders add up to slightly more than the whole-job figures in 5.1 '
    '(which govern the budget). Order the next stage\'s cement in time but do not store cement for more than 4-6 weeks.')
sp = []
KORDER = list(T.keys())
for s, sname in R['stages']:
    g = stage_gross[s]
    keys = [k for k in KORDER if g.get(k, 0) > 1e-9]
    stl = sum(g.get(k, 0) for k in STEEL_KEYS)
    if not keys:
        continue
    sp.append(row('%s  %s  (material cost %s)' % (s, sname, rs(STAGE_COST[s])), kind='section'))
    for k in keys + (['BWIRE'] if stl > 0 else []):
        t = T[k]
        gross = stl * 0.01 if k == 'BWIRE' else g[k]
        order = math.ceil(gross / t['usize'] - 1e-9) * t['usize']
        nun = order / t['usize']
        tl = ''
        if k == 'BRK': tl = f0(math.ceil(order / 2000))
        elif k in ('SNDC', 'SNDM', 'CRS', 'KHG', 'EARTH'): tl = f0(math.ceil(order / 100))
        sp.append(row(t['name'], qfmt(gross, t['unit']), qfmt(order, t['unit']), t['unit'], '%s x %s' % (f0(nun), t['bunit']) if t['usize'] != 1 else f0(nun), tl))
table(['Material', 'Needed (with wastage)', 'Order', 'Unit', 'Buying units', 'Trolley loads'], [5900, 1700, 1600, 900, 3300, 1638], sp,
      ['L', 'R', 'R', 'C', 'L', 'R'], font=7)

# =================================================================== 6. STEEL
blk(type='section', orientation='PORTRAIT')
blk(type='h1', text='6. Steel (sariya) schedule by bar size and member group')
srows_ = [row(g, *[blank0(v) for v in vals], f1(sum(vals))) for g, *vals in [(x[0], x[1], x[2], x[3], x[4]) for x in STEEL]]
srows_.append(row('TOTAL net', *[f1(v) for v in STEEL_TOT[1:5]], f1(STEEL_TOT[5]), kind='subtotal'))
srows_.append(row('With 4% wastage', *[f1(T[k]['gross']) for k in STEEL_KEYS], f1(sum(T[k]['gross'] for k in STEEL_KEYS)), kind='gross'))
srows_.append(row('PURCHASE (rounded to 10 kg)', *[f0(v) for v in STEEL_BUY[1:5]], f0(STEEL_BUY[5]), kind='total'))
srows_.append(row('Cost (Rs)', *[f0(T[k]['cost']) for k in STEEL_KEYS], f0(steel_cost)))
table(['Member group (net kg)', '#2 (6 mm)', '#3 (10 mm)', '#4 (12 mm)', '#6 (20 mm)', 'Total (kg)'], [2900, 1250, 1250, 1250, 1250, 2006],
      srows_, ['L', 'R', 'R', 'R', 'R', 'R'], font=8)
blk(type='p', size=17, text='Binding wire: %s kg (10 kg per ton of gross steel, E4). Laps, hooks, cranks and chairs are included in the net weights (laps as Rev 0). '
    'The S-02 RCC strip footing steel (673 kg of #3) is no longer required (C1).' % f0(BW_BUY))
blk(type='h2', text='Steel by construction stage (kg, with wastage)')
ss = []
for s, sname in R['stages']:
    v = STAGE_STEEL[s]
    if sum(v) > 0:
        ss.append(row('%s %s' % (s, sname), *[blank0(x) for x in v], f1(sum(v))))
ss.append(row('TOTAL with wastage', *[f1(sum(STAGE_STEEL[s][j] for s in STAGE_STEEL)) for j in range(4)],
              f1(sum(sum(v) for v in STAGE_STEEL.values())), kind='subtotal'))
table(['Stage', '#2', '#3', '#4', '#6', 'Total (kg)'], [3700, 1150, 1150, 1150, 1150, 1606], ss, ['L', 'R', 'R', 'R', 'R', 'R'], font=8)
blk(type='note', text='Main bar details are in each BOQ description (Section 4): slabs per S-06 to S-08 bar sets; concealed beams CB-1/CB-2 per S-09; lintels per S-05; stair per S-03; plinth beam 2 #4 top + 2 #4 bottom with #2 rings @ 10".')

# =================================================================== 7. SOLAR
SO = R['solar']
blk(type='h1', text='7. Solar layout summary (J3, J4)', newpage=True)
blk(type='image', path=IMG, width=430, height=440, alt='Schematic solar layout on the terrace and mumty roof')
so_rows = [row(a, b, c, d, e) for a, b, c, d, e in SO['rows']]
so_rows.append(row('Total', SO['panels'], '%d x %d W = %.2f kWp' % (SO['panels'], SO['w'], SO['kwp']), '', SO['plinths'], kind='subtotal'))
table(['Location', 'Panels', 'Arrangement', 'Position', 'Plinths'], [2600, 800, 2600, 2906, 1000], so_rows, ['L', 'C', 'L', 'L', 'C'], font=8)
blk(type='kv', size=16, lw=2400, lines=[
    ('Panels', '%d x %d W (%s), tilted %d° facing the front (assumed south - confirm north on site).' % (SO['panels'], SO['w'], SO['module'], SO['tilt'])),
    ('Area', 'Panels cover about %s sft in plan. Terrace %s sft, mumty roof %s sft.' % (f0(SO['footprint']), f0(SO['terrace_area']), f0(SO['mumty_area']))),
    ('Spacing', 'Row pitch %s (no row-to-row shading at winter noon); %s.' % (SO['pitch'], SO['walkways'])),
    ('RCC plinths', '%d nos, %s. Cast on the roof slab BEFORE the membrane; the membrane is dressed round each plinth (item 9.3). Item 14.21: %s cft concrete, %s kg #3 + %s kg #2, %d J-bolts.' % (
        SO['plinths'], SO['plinth'], f1(q('14.21')), f1(item_mat['14.21']['ST3']), f1(item_mat['14.21']['ST2']), round(item_mat['14.21']['JBOLT']))),
    ('Conduits (J4)', 'Spare 1¼" DC and 1" AC conduits from the roof to the inverter (items 14.10-14.11); 2" sleeves through walls (14.20).'),
    ('Inverter and battery', 'Mumty laundry (2nd floor): wall space for the inverter and a 3\'-0" x 1\'-6" x 6" RCC plinth for the sodium-ion battery cabinet (14.22).'),
    ('Backup scheme (J5)', 'Inverter AC-out feeds backup (essential-load) DBs on GF, FF and mumty (items 14.12-14.13, 14.18); grid feeds the main DBs.'),
    ('Earthing (J7)', 'Separate earth pit for solar / inverter (one of 3 pits, item 14.19).'),
])

# =================================================================== 8. EXCLUSIONS
blk(type='h1', text='8. Exclusions and items moved to the finishing estimate', newpage=True)
table(['Category', 'Items'], [2300, 7606], [row(a, b) for a, b in R['excl']] + [
    row('Deleted from Rev 0', 'Ceiling plaster (F1 - false ceilings are finishing work); RCC overhead tank (I4 - replaced by a plastic tank, which is finishing); TV and intercom conduits (J2).'),
], ['L', 'L'], font=8)

# =================================================================== 9. RECOMMENDED ADDITIONS
blk(type='h1', text='9. Recommended additions (NOT in the total)')
blk(type='p', size=17, text='These are not decided in the Register, so they are kept out of the total. Each is worth doing for the reason given; approve any of them and add its cost.')
rec_rows = [row(i + 1, a, c, f0(b) if b >= 0 else '-%s (saving)' % f0(-b)) for i, (a, b, c) in enumerate(R['rec'])]
rec_sum = sum(b for _, b, _ in R['rec'])
rec_rows.append(row('', 'Net effect if all are approved', '', f0(rec_sum), kind='subtotal'))
table(['No.', 'Addition', 'Reason', 'Material cost (Rs)'], [500, 3300, 4506, 1600], rec_rows, ['C', 'L', 'L', 'R'], font=8)

# =================================================================== 10. ASSUMPTIONS
AREA = ['General', 'Plinth beam', 'DPC', 'Levels', 'Levels', 'Edge walls', 'Edge walls', 'Ramps', 'Car porch', 'Car porch', 'Boundary walls',
        'Boundary walls', 'Septic tank', 'Septic tank', 'Water tank', 'Water tank', 'Roof tank', 'Solar', 'Solar', 'Anti-termite', 'Roof', 'Floors',
        'Sunken baths', 'Chicken mesh', 'Electrical', 'Electrical', 'Earthing', 'Geometry', 'Water supply', 'Lawn', 'Steps', 'Rates']
assert len(AREA) == len(R['ra'])
blk(type='h1', text='10. Remaining assumptions (each marked ASSUMED)', newpage=True)
blk(type='p', size=17, text='Where the drawings and the Register are silent, sensible Faisalabad practice was used without over-building. Each item below is an assumption to be confirmed on site or by the designers.')
table(['No.', 'Area', 'Assumption', 'Status'], [500, 1400, 7006, 1000], [row(i + 1, AREA[i], t, 'ASSUMED') for i, t in enumerate(R['ra'])],
      ['C', 'L', 'L', 'C'], font=7.5)

# =================================================================== 11. POINTS
WHO = ['Engineer', 'Engineer', 'Engineer', 'Architect', 'Architect', 'Architect + Engineer', 'Engineer', 'Engineer', 'Engineer',
       'Architect + Engineer', 'Architect', 'Engineer', 'Architect']
assert len(WHO) == len(R['points'])
blk(type='h1', text='11. Points for the architect and structural engineer to confirm')
table(['No.', 'For', 'Point'], [500, 1700, 7706], [row(i + 1, WHO[i], t) for i, t in enumerate(R['points'])], ['C', 'L', 'L'], font=8)

# =================================================================== FINAL CHECK
blk(type='h1', text='Thumb-rule check, double counting and final check', newpage=True)
sand_sft = (T['SNDC']['buy'] + T['SNDM']['buy']) / COVER
RCC_GROUPS = {'Column footing', 'Plinth beam', 'Column', 'Slabs', 'Concealed beams', 'Lintels', 'Bed plates', 'Stairs', 'Chajjas', 'Elevation RCC',
              'Coping', 'Sunken slabs', 'Manhole covers', 'Septic tank', 'Water tank', 'Tank platform', 'Solar plinths', 'Boundary walls'}
rcc_cft = sum(i['qty'] for i in ITEMS if i['group'] in RCC_GROUPS and i['unit'] == 'cft' and any(k in i['mat'] for k in ('CEM',)) and
              not i['desc'].startswith('P.C.C'))
kg_m3 = STEEL_TOT[5] / (rcc_cft * 0.0283168)
vals = [T['CEM']['buy'] / COVER, steel_buy / COVER, kg_m3, TH['bricks_house'], T['BRK']['buy'] / COVER, sand_sft, T['CRS']['buy'] / COVER, PER_SFT]
thumb = [  # (indicator, this estimate, normal range, low, high, note)
    ('Cement per sft of covered area', '%.2f bags' % vals[0], '0.35-0.45 bags', 0.35, 0.45, ''),
    ('Steel per sft of covered area', '%.2f kg' % vals[1], '1.5-2.5 kg', 1.5, 2.5, 'load-bearing walls + RCC slabs (framed houses 3-4 kg)'),
    ('Steel per m3 of RCC', '%.0f kg/m3' % vals[2], '80-130 kg/m3', 80, 130, 'all RCC members (%s cft of RCC)' % f0(rcc_cft)),
    ('Bricks per sft - house only', '%.1f' % vals[3], '22-30', 22, 30, 'with wastage'),
    ('Bricks per sft - all work', '%.1f' % vals[4], '28-38', 28, 38, 'incl. boundary walls, manholes, tanks'),
    ('Sand per sft (Chenab + Ravi)', '%.2f cft' % vals[5], '1.6-2.4 cft', 1.6, 2.4, ''),
    ('Crush per sft', '%.2f cft' % vals[6], '0.8-1.2 cft', 0.8, 1.2, ''),
    ('Material cost per sft', rs(vals[7]), 'Rs 2,000-2,700', 2000, 2700, 'grey structure, material only, Faisalabad late 2026 (estimated range)'),
]
thumb_ok = all(lo <= v <= hi for v, (_, _, _, lo, hi, _) in zip(vals, thumb))
assert thumb_ok, [(t[0], v) for v, t in zip(vals, thumb) if not (t[3] <= v <= t[4])]
blk(type='h2', text='Thumb-rule sanity check')
table(['Indicator', 'This estimate', 'Normal range', 'Result', 'Note'], [3000, 1500, 1600, 900, 2906],
      [row(a, b, c, 'PASS', d) for a, b, c, lo, hi, d in thumb], ['L', 'R', 'C', 'C', 'L'], font=8)
blk(type='note', text='Ranges are common Pakistani rules of thumb for a double-storey load-bearing brick house with RCC slabs, measured on covered area; they are a sanity check, not a design standard.')
blk(type='h2', text='Double-counting checks')
blk(type='bullets', size=17, items=[
    'Foundation brickwork stops at road level; the plinth wall runs from road level to the underside of the plinth beam; the beam and the DPC are separate layers.',
    'Earth is counted once: %s cft dug, %s cft back-filled, %s cft (loose) re-used in filling, %s cft bought.' % (f0(EARTH['exc']), f0(EARTH['back']), f0(EARTH['surplus_loose']), f0(EARTH['buy'])),
    'Sub-floor layers add up exactly to the finished floor: fill to +1\'-11½", khangar 4", sand 1", PCC 3", DPC 1½" = +2\'-9".',
    'The upper-floor 3" sub-base excludes the sunken bath areas, which have their own brick-bat fill.',
    'Ceiling plaster is deleted; soffit plaster is a separate line; parapet and boundary-wall plaster are not inside the house-wall plaster.',
    'Roof tiles exclude the 34 solar plinths and the tank platform; membrane upturns are counted once.',
    'Slab steel is measured once by bar set; concealed beams, lintels and bed plates are separate members with their own bars.',
    'Binding wire is calculated once, on the total gross steel.',
    'Manhole, septic-tank and water-tank excavations are separate from the house trenches, and their back-filling is subtracted from the surplus earth.',
])
blk(type='h2', text='Final check')
fc = [
    ('1', 'All Register lines A1-K3 applied and logged', 'PASS', 'All %d lines are in table 3.2 with how each is applied and the BOQ items where it is used; quantity changes are in table 3.1.' % REG_LOGGED),
    ('2', 'Every drawing sheet, room, wall, opening, slab, stair, tank, manhole and boundary wall is in the BOQ', 'PASS',
     'Table 2.7 maps all 24 architect\'s sheets (plus 3D views and 5 bath-detail pages) and all 9 structural sheets to BOQ items; table 2.8 lists 3 slabs, 2 stairs, 58 lintels, 9 manholes, septic tank, underground tank, tank platform, 6 boundary-wall stretches and 6 edge walls.'),
    ('3', 'Sheet 05 followed exactly, with only the DPC added', 'PASS',
     'PCC 3" 1:4:8 at -4\'-0"; brick steps and 13½" wall to road level; 9" plinth wall; 9" x 9" RCC plinth beam at floor level. The only addition is the DPC (B4, with the vertical DPC B6). The S-02 RCC strip footing is not used.'),
    ('4', 'Arithmetic correct; Word and Excel totals identical', 'PASS',
     'Excel recalculated: %s formulas, %d errors. Excel total (Totals sheet) %s = this report %s = take-off engine. Every figure in this report is read from the recalculated workbook; stage, steel and line totals reconcile exactly. One Rev 0 slip was found and corrected (manhole brickwork, table 3.1).' % (
         f0(RC['total_formulas']), RC['total_errors'], rs(TOTAL), rs(TOTAL))),
    ('5', 'Proper construction order', 'PASS', 'BOQ stages S1-S16 follow the required order (Section 4); the purchase schedule (5.2) follows the same order.'),
    ('6', 'Thumb-rule check passed', 'PASS' if thumb_ok else 'CHECK', 'Cement %.2f bags/sft, steel %.2f kg/sft, house bricks %.0f/sft, %s/sft - all within normal ranges (table above).' % (
        T['CEM']['buy'] / COVER, steel_buy / COVER, TH['bricks_house'], rs(PER_SFT))),
]
table(['No.', 'Check', 'Result', 'Evidence'], [500, 3000, 900, 5506], [row(*x, kind='pass') for x in fc], ['C', 'L', 'C', 'L'], font=8)

json.dump(B, open(OUT, 'w'), indent=0, ensure_ascii=False)
print('blocks', len(B), 'total', TOTAL, 'per sft', round(PER_SFT, 2), 'reg logged', REG_LOGGED, 'kg/m3', round(kg_m3), 'rcc cft', round(rcc_cft))
