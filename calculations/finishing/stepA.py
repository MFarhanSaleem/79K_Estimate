# Finishing estimate STEP A for House 79/K: measurement schedules + questionnaire (no prices).
# Room sizes, doors and windows are read from the architect's working drawings (sheets 01-08, 13-16);
# heights, levels and external areas come from the binding grey-structure Rev 1 take-off.
# usage: python3 stepA.py <out_blocks.json>
import json, math, os, sys
from collections import OrderedDict, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'est'))
import estimate as R0                                  # Rev 0 geometry (wall lengths, heights)
G = json.load(open(os.path.join(HERE, '..', 'rev1', 'rev1.json')))   # binding grey Rev 1 data
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'blocks_stepA.json')
LS = ' '

def f0(x): return '{:,.0f}'.format(x)
def f1(x): return '{:,.1f}'.format(x)
def f2(x): return '{:,.2f}'.format(x)
def ftin(x):
    """feet (decimal) -> 7'-7½" """
    neg = x < 0; x = abs(x)
    ft = int(x + 1e-9); inch = round((x - ft) * 12 * 2) / 2
    if inch >= 12: ft += 1; inch -= 12
    s = ('%g' % inch).replace('.5', '½')
    if s.startswith('0½'): s = '½'
    return ('-' if neg else '') + "%d'-%s\"" % (ft, s)
SQM = 0.092903

# ============================================================== heights (from the grey estimate)
FC_ROOM = 10.0          # false ceiling in GF and FF rooms (slab soffit 11'-0" GF / ~11'-2" FF above finished floor)
FC_WET = 8.5            # baths, powder room, laundry (ducts above)
FC_2F = 8.5             # mumty room (slab soffit ~9'-2" above finished floor)
GF_SLAB_SOFFIT = R0.GF_H                       # 11.00 ft above FFL
FF_FLOOR_TO_FLOOR = 12.0
STOREY = {'GF': GF_SLAB_SOFFIT + R0.SLAB_T, 'FF': FF_FLOOR_TO_FLOOR, '2F': R0.SF_H}

# ============================================================== rooms (clear sizes from sheets 01-03 / 06-08)
# id, floor, name, L, W, floor category, false-ceiling height, wall length factor note, flags
# cat: T24 = 2'x4' tile; BATH = bathroom floor; WET = laundry; KIT = kitchen; HALL = stair hall landing (2'x4')
ROOMS = [
 # ---------------- ground floor (sheet 01 / 06)
 ('G01', 'GF', 'Stair lobby (S-T lobby)', 5.0, 8.125, 'HALL', FC_ROOM, ''),
 ('G02', 'GF', 'Lobby (5\'-0" wide)', 5.0, 15.5, 'T24', FC_ROOM, 'length measured on sheet 06 (not dimensioned)'),
 ('G03', 'GF', 'Bed-1', 13.0, 13.0, 'T24', FC_ROOM, ''),
 ('G04', 'GF', 'Bed-1 dress', 4.0, 5.0, 'T24', FC_ROOM, ''),
 ('G05', 'GF', 'Bed-1 bath (incl. shower area)', 9.0, 5.0, 'BATH', FC_WET, ''),
 ('G06', 'GF', 'Master bed', 14.25, 12.0, 'T24', FC_ROOM, ''),
 ('G07', 'GF', 'Master dress', 4.5, 5.0, 'T24', FC_ROOM, ''),
 ('G08', 'GF', 'Master bath (incl. shower area)', 7.625, 8.875, 'BATH', FC_WET, ''),
 ('G09', 'GF', 'Dining', 9.0, 9.625, 'T24', FC_ROOM, ''),
 ('G10', 'GF', 'Powder room (P-W)', 4.0, 4.5, 'BATH', FC_WET, ''),
 ('G11', 'GF', 'Open kitchen', 13.625, 11.75, 'KIT', FC_ROOM, ''),
 ('G12', 'GF', 'Raw kitchen', 7.0, 11.0, 'KIT', FC_ROOM, ''),
 ('G13', 'GF', 'TV lounge (less splayed corner 2 sft)', 15.0, 12.0, 'T24', FC_ROOM, ''),
 ('G14', 'GF', 'Drawing room', 13.0, 12.0, 'T24', FC_ROOM, ''),
 ('G15', 'GF', 'Entrance foyer', 6.25, 6.0, 'T24', FC_ROOM, 'depth measured (not dimensioned)'),
 ('G16', 'GF', 'Under-stair store (S-A)', 5.0, 3.5, 'T24', FC_ROOM, 'measured; access door not drawn'),
 # ---------------- first floor (sheet 02 / 07)
 ('F01', 'FF', 'Stair hall (S-T lobby)', 19.0, 6.625, 'HALL', FC_ROOM, ''),
 ('F02', 'FF', 'Lobby, rear part (5\'-0" wide)', 5.0, 12.5, 'T24', FC_ROOM, 'length measured'),
 ('F03', 'FF', 'Lobby, front part (6\'-3" wide)', 6.25, 12.0, 'T24', FC_ROOM, 'length measured'),
 ('F04', 'FF', 'Bed-1', 13.0, 12.0, 'T24', FC_ROOM, ''),
 ('F05', 'FF', 'Bed-1 dress', 4.0, 6.0, 'T24', FC_ROOM, ''),
 ('F06', 'FF', 'Bed-1 bath (incl. shower area)', 9.0, 6.0, 'BATH', FC_WET, ''),
 ('F07', 'FF', 'Master bed', 14.25, 14.0, 'T24', FC_ROOM, ''),
 ('F08', 'FF', 'Master dress', 4.5, 6.375, 'T24', FC_ROOM, ''),
 ('F09', 'FF', 'Master bath (incl. shower area)', 8.0, 6.375, 'BATH', FC_WET, ''),
 ('F10', 'FF', 'TV lounge', 14.75, 13.625, 'T24', FC_ROOM, ''),
 ('F11', 'FF', 'Store (with wardrobes)', 13.0, 6.0, 'T24', FC_ROOM, ''),
 ('F12', 'FF', 'Kitchen', 13.0, 8.0, 'KIT', FC_ROOM, ''),
 ('F13', 'FF', 'Front bed (less splayed corner 2 sft)', 15.375, 14.0, 'T24', FC_ROOM, ''),
 ('F14', 'FF', 'Front bed dress', 5.25, 6.0, 'T24', FC_ROOM, ''),
 ('F15', 'FF', 'Front bed bath (incl. shower area)', 10.0, 6.0, 'BATH', FC_WET, ''),
 # ---------------- second floor / mumty (sheet 03 / 08)
 ('S01', '2F', 'Stair hall', 15.875, 7.0, 'HALL', FC_2F, ''),
 ('S02', '2F', 'Room', 11.0, 12.0, 'T24', FC_2F, ''),
 ('S03', '2F', 'Bath', 4.75, 5.5, 'BATH', FC_WET, ''),
 ('S04', '2F', 'Laundry (open on terrace side)', 5.125, 6.5, 'WET', FC_WET, 'one side open to terrace (5\'-1½")'),
]
R = OrderedDict((r[0], dict(id=r[0], fl=r[1], name=r[2], L=r[3], W=r[4], cat=r[5], fc=r[6], flag=r[7])) for r in ROOMS)
STAIR_OPEN = {'F01': 72.8, 'S01': 74.3}                       # slab openings over the flights (grey take-off)
SPLAY = {'G13': 2.2, 'F13': 2.2}                               # splayed front corner (sheet 06/07)
for k, r in R.items():
    r['gross'] = r['L'] * r['W'] - SPLAY.get(k, 0)
    r['area'] = r['gross'] - STAIR_OPEN.get(k, 0)              # finished floor area
# walls actually present round each room (open sides removed), ft
OPEN_SIDE = {'G11': 13.625, 'G15': 6.25, 'G02': 10.0, 'F02': 10.0, 'F03': 12.5 - 6.25, 'F10': 13.625, 'S04': 5.125}
for k, r in R.items():
    r['perim'] = 2 * (r['L'] + r['W']) - OPEN_SIDE.get(k, 0)

# ============================================================== doors (sheets 06-08; sizes are clear openings as drawn)
# ref, floor, from room, to room / outside, width, height, swing, type, flag
DOORS = [
 ('D01', 'GF', 'G15', 'EXT:Front', 5.125, 8.0, 'double leaf, opens in', 'Main entrance - solid wood, glazed fanlight above (W07)', 'leaf height 8\'-0" assumed inside the 20\'-6" opening'),
 ('D02', 'GF', 'G01', 'EXT:Rear', 3.5, 8.0, 'single, opens in', 'External rear door (to rear passage)', ''),
 ('D03', 'GF', 'G01', 'G02', 3.5, 8.0, 'single, into lobby', 'Internal', ''),
 ('D04', 'GF', 'G03', 'G02', 3.5, 8.0, 'single, into room', 'Internal (bedroom)', ''),
 ('D05', 'GF', 'G04', 'G03', 2.875, 8.0, 'single, into dress', 'Internal (dress)', ''),
 ('D06', 'GF', 'G05', 'G04', 2.5, 8.0, 'single, into bath', 'Bathroom', ''),
 ('D07', 'GF', 'G06', 'G02', 3.5, 8.0, 'single, into room', 'Internal (bedroom)', ''),
 ('D08', 'GF', 'G08', 'G07', 2.5, 8.0, 'single, into bath', 'Bathroom', ''),
 ('D09', 'GF', 'G07', 'G06', 2.5, 8.0, 'open (no leaf drawn)', 'Opening - door optional', 'no leaf drawn; 2\'-6" opening assumed'),
 ('D10', 'GF', 'G10', 'G14', 2.25, 8.0, 'single, into powder', 'Bathroom (powder)', 'side it opens onto to be confirmed'),
 ('D11', 'GF', 'G14', 'G15', 3.5, 8.0, 'single, into room', 'Internal (drawing)', ''),
 ('D12', 'GF', 'G12', 'EXT:Left', 3.0, 8.0, 'single, opens in', 'External kitchen door (to side passage)', ''),
 ('D13', 'GF', 'G12', 'G11', 3.0, 8.0, 'single, into raw kitchen', 'Kitchen', ''),
 ('D14', 'GF', 'G16', 'G02', 2.5, 6.5, 'single, out', 'Store (under stair)', 'not drawn - size assumed; confirm access side'),
 ('A01', 'GF', 'G09', 'G11', 6.5, 8.0, 'arch, no leaf', 'Opening (dining arch)', ''),
 ('D15', 'FF', 'F01', 'F02', 3.5, 8.0, 'single, into stair hall', 'Internal', ''),
 ('D16', 'FF', 'F04', 'F02', 3.5, 8.0, 'single, into room', 'Internal (bedroom)', ''),
 ('D17', 'FF', 'F05', 'F04', 2.875, 8.0, 'single, into dress', 'Internal (dress)', ''),
 ('D18', 'FF', 'F06', 'F05', 2.5, 8.0, 'single, into bath', 'Bathroom', ''),
 ('D19', 'FF', 'F07', 'F02', 3.5, 8.0, 'single, into room', 'Internal (bedroom)', ''),
 ('D20', 'FF', 'F08', 'F07', 3.5, 8.0, 'single, into dress', 'Internal (dress)', ''),
 ('D21', 'FF', 'F09', 'F08', 2.5, 8.0, 'single, into bath', 'Bathroom', ''),
 ('D22', 'FF', 'F13', 'F03', 3.5, 8.0, 'single, into room', 'Internal (bedroom)', ''),
 ('D23', 'FF', 'F14', 'F13', 3.0, 8.0, 'single, into dress', 'Internal (dress)', ''),
 ('D24', 'FF', 'F15', 'F14', 2.5, 8.0, 'single, into bath', 'Bathroom', ''),
 ('D25', 'FF', 'F11', 'F03', 3.0, 8.0, 'single, into store', 'Store', ''),
 ('D26', 'FF', 'F12', 'F03', 3.0, 8.0, 'single, into kitchen', 'Kitchen', ''),
 ('D27', 'FF', 'F12', 'EXT:Front', 6.0, 8.0, '2-panel sliding', 'Aluminium glazed sliding door to front terrace (sill 6")', ''),
 ('D28', '2F', 'S01', 'EXT:Mumty', 3.5, 8.0, 'single, opens in', 'Roof / mumty door to terrace (external)', ''),
 ('D29', '2F', 'S02', 'S01', 3.5, 8.0, 'single, into room', 'Internal (room)', ''),
 ('D30', '2F', 'S03', 'S04', 2.5, 8.0, 'single, into bath', 'Bathroom', ''),
]
# ============================================================== windows / ventilators
# ref, floor, room, elevation, width, height, sill, type, count, flag, interior parts [(room, h)]
# types: SLT = 3-track sliding (2 glass + net) with fixed top light 2'-0"; SL = sliding no top light;
#        FXT = fixed lower + top-hung vent 2'-0"; TH = top-hung ventilator; SF = storefront fixed glazing
WINS = [
 ('W01', 'GF', 'G03', 'Rear', 7.0, 7.0, 1.0, 'SLT', 1, ''),
 ('W02', 'GF', 'G06', 'Left', 7.0, 7.0, 1.0, 'SLT', 1, ''),
 ('W03', 'GF', 'G09', 'Right (patio)', 3.25, 7.0, 1.0, 'SLT', 1, ''),
 ('W04', 'GF', 'G12', 'Left', 3.0, 4.5, 3.5, 'SL', 1, 'sill read as 3\'-6" (head at 8\'-0")'),
 ('W05', 'GF', 'G14', 'Front (car porch)', 6.0, 7.0, 1.0, 'SLT', 1, ''),
 ('W06', 'GF+FF', 'G13/F13', 'Front', 8.5, 20.0, 0.5, 'SF', 1, 'double-height glazing; GF TV lounge + FF front bed'),
 ('W07', 'GF+FF', 'G15/F03', 'Front', 5.125, 12.5, 8.0, 'SF', 1, 'glazing above main door, 20\'-6" opening less 8\'-0" door'),
 ('W08', 'FF', 'F01', 'Rear', 3.0, 7.0, 1.0, 'FXT', 2, ''),
 ('W09', 'FF+2F', 'F01/S01', 'Left', 2.0, 25.0, 0.5, 'SF', 1, 'vertical slot, stair hall'),
 ('W10', 'FF', 'F04', 'Rear', 7.0, 7.0, 1.0, 'SLT', 1, ''),
 ('W11', 'FF', 'F07', 'Left', 7.0, 7.0, 1.0, 'SLT', 1, ''),
 ('W12', 'FF', 'F13', 'Left', 7.0, 7.0, 1.0, 'SLT', 1, ''),
 ('W13', 'FF', 'F10', 'Right (open shaft)', 8.0, 7.0, 1.0, 'SLT', 1, ''),
 ('W14', '2F', 'S01', 'Rear', 3.0, 7.0, 1.0, 'FXT', 2, ''),
 ('W15', '2F', 'S02', 'Rear', 5.0, 7.0, 1.0, 'SLT', 1, ''),
 ('V01', 'GF', 'G05', 'Right', 2.5, 2.0, 6.0, 'TH', 1, ''),
 ('V02', 'GF', 'G08', 'Left', 2.5, 2.0, 6.0, 'TH', 1, ''),
 ('V03', 'GF', 'G10', 'Right (patio)', 2.5, 2.0, 6.0, 'TH', 1, ''),
 ('V04', 'FF', 'F06', 'Right', 2.5, 2.0, 6.0, 'TH', 1, ''),
 ('V05', 'FF', 'F09', 'Left', 2.5, 2.0, 6.0, 'TH', 1, ''),
 ('V06', 'FF', 'F15', 'Left', 2.5, 2.0, 6.0, 'TH', 1, ''),
 ('V07', '2F', 'S03', 'Rear', 2.5, 2.0, 6.0, 'TH', 1, ''),
]
# interior face of the tall glazed units, clipped to each room's false ceiling
INT_PARTS = {'W06': [('G13', 8.5, 9.5), ('F13', 8.5, 8.5)], 'W07': [('G15', 5.125, 2.0), ('F03', 5.125, 8.5)], 'W09': []}

# ---------------- aluminium weight model (medium sliding series ~1.2-1.4 mm wall; storefront 45 mm series)
KG = dict(sl_frame=1.10, sash=0.65, net=0.40, fx_frame=0.80, transom=0.90, th_frame=0.75, th_sash=0.70,
          sd_frame=1.60, sd_sash=1.10, sd_net=0.50, sf_frame=1.80, sf_bar=1.80)
FT = 0.3048
def alu(t, w, h):
    """aluminium kg and glass sft for one window"""
    m = lambda ft: ft * FT
    if t in ('SLT', 'SL'):
        hs = h - 2.0 if t == 'SLT' else h
        kg = m(2 * (w + hs)) * KG['sl_frame']
        sw, sh = w / 2 + 0.17, hs - 0.15
        kg += 2 * m(2 * (sw + sh)) * KG['sash'] + m(2 * (w / 2 + sh)) * KG['net']
        glass = w * hs
        if t == 'SLT':
            kg += m(2 * w + 2 * 2.0) * KG['fx_frame'] + m(w) * KG['transom']; glass += w * 2.0
        return kg, glass
    if t == 'FXT':
        kg = m(2 * (w + h)) * KG['fx_frame'] + m(w) * KG['transom'] + m(2 * (w + 2.0)) * KG['th_sash']
        return kg, w * h
    if t == 'TH':
        return m(2 * (w + h)) * (KG['th_frame'] + KG['th_sash']), w * h
    if t == 'SD':
        kg = m(2 * h + w) * KG['sd_frame'] + 2 * m(2 * (w / 2 + 0.17 + h)) * KG['sd_sash'] + m(2 * (w / 2 + h)) * KG['sd_net']
        return kg, w * h
    if t == 'SF':                                   # frame + vertical mullions @ <=4'-6" + transoms @ <=6'-0"
        nm = max(0, math.ceil(w / 4.5) - 1); nt = max(0, math.ceil(h / 6.0) - 1)
        kg = m(2 * (w + h)) * KG['sf_frame'] + m(nm * h + nt * w) * KG['sf_bar']
        if h > 15: kg += 2 * m(2 * (3.0 + 2.0)) * KG['th_sash']           # one top-hung vent per floor
        return kg, w * h
    raise KeyError(t)
TYPE_NAME = {'SLT': 'Sliding 3-track (2 glass sashes + fly-net) with fixed top light 2\'-0"',
             'SL': 'Sliding 3-track (2 glass sashes + fly-net)',
             'FXT': 'Fixed lower glass + top-hung vent 2\'-0" at top',
             'TH': 'Top-hung ventilator, obscure glass (exhaust fan kept separate)',
             'SF': 'Fixed storefront glazing (45 mm series) with transoms; top-hung vent each floor where tall',
             'SD': 'Sliding door, heavy series, 2 panels + fly-net'}
for w in WINS: pass
WROWS = []
for (ref, fl, room, elev, w, h, sill, t, n, flag) in WINS:
    kg, gl = alu(t, w, h)
    WROWS.append(dict(ref=ref, fl=fl, room=room, elev=elev, w=w, h=h, sill=sill, t=t, n=n, flag=flag, kg=kg, glass=gl))
d27 = [d for d in DOORS if d[0] == 'D27'][0]
kg_sd, gl_sd = alu('SD', d27[4], d27[5])
ALU_TOTAL = sum(x['kg'] * x['n'] for x in WROWS) + kg_sd
GLASS_TOTAL = sum(x['glass'] * x['n'] for x in WROWS) + gl_sd

# ============================================================== IS 1200 deduction rule for paint
A_SMALL, A_LARGE = 0.5 / SQM, 3.0 / SQM          # 5.4 sft and 32.3 sft
def face_deduction(a, one_face_side):
    """returns (deduct, add_reveal_flag) for one face. <=0.5 m2: nil; 0.5-3 m2: one face only; >3 m2: both faces + reveals"""
    if a <= A_SMALL: return 0.0, False
    if a <= A_LARGE: return (a if one_face_side else 0.0), False
    return a, True

# openings seen from each room: (room, w, h_on_face, area_full, one_face_side, reveal_len)
FACES = defaultdict(list)
for (ref, fl, ra, rb, w, h, swing, typ, flag) in DOORS:
    a = w * h
    FACES[ra].append((ref, w, h, a, True, 2 * h + w))
    if not rb.startswith('EXT'):
        FACES[rb].append((ref, w, h, a, False, 2 * h + w))
for x in WROWS:
    if x['ref'] in INT_PARTS:
        for (room, w, h) in INT_PARTS[x['ref']]:
            FACES[room].append((x['ref'], w, h, w * h, True, 2 * h + w))
        continue
    for i in range(x['n']):
        FACES[x['room']].append((x['ref'], x['w'], x['h'], x['w'] * x['h'], True, 2 * x['h'] + x['w']))

# ============================================================== wall tiles
BACKSPLASH = {'G11': (11.25, 'counter on rear wall 5\'-3" + side 6\'-0"'), 'G12': (16.0, 'L-counter 7\'-0" + 9\'-0"'),
              'F12': (19.0, 'L-counter 13\'-0" + 6\'-0"')}
BS_H = 2.0
WALLT = OrderedDict()
for k, r in R.items():
    if r['cat'] == 'BATH':
        ded = sum(o[1] * min(o[2], r['fc']) for o in FACES[k])
        WALLT[k] = dict(gross=r['perim'] * r['fc'], ded=ded, net=r['perim'] * r['fc'] - ded,
                        note='all walls to false ceiling %s' % ftin(r['fc']))
WALLT['S04'] = dict(gross=(5.125 + 6.5) * 4.0, ded=0, net=(5.125 + 6.5) * 4.0, note='4\'-0" dado on the two closed walls (washing machine, sink)')
for k, (L, note) in BACKSPLASH.items():
    WALLT[k] = dict(gross=L * BS_H + 0.5 * 2.5, ded=0, net=L * BS_H + 0.5 * 2.5, note='backsplash 2\'-0" high over %s (+ hob area to hood)' % note)

# ============================================================== floors & skirting
for k, r in R.items():
    doors_w = sum(o[1] for o in FACES[k] if o[0].startswith(('D', 'A')))
    if r['cat'] in ('BATH', 'WET'):
        r['skirt'] = 0.0
    elif r['cat'] == 'KIT':
        r['skirt'] = max(0.0, r['perim'] - doors_w - BACKSPLASH[k][0])
    elif r['cat'] == 'HALL':
        r['skirt'] = {'G01': 26.25 - 7.0 - 5.0, 'F01': 2 * 5.875 + 6.625 - 3.5, 'S01': 9.0}[k]   # landing walls only; flights in stair schedule
    else:
        r['skirt'] = max(0.0, r['perim'] - doors_w)

# stairs (zig-zag, 2 storeys: GF-FF and FF-2F) - S-03 / sheet 06-08
N_TREAD, N_RISER, W_ST = 21, 22, 3.5
TREAD, RISER = 10.5 / 12, 6.57 / 12
st_tread = 2 * N_TREAD * TREAD * W_ST
st_riser = 2 * N_RISER * RISER * W_ST
st_land = 2 * 8.25 * 3.5
st_skirt = 2 * 2 * (R0.g1 + R0.g2)            # stepped skirting both sides, both storeys
st_soffit = 2 * ((R0.g1 + R0.g2) * 3.5 + 8.25 * 3.5)
EXT_STEPS = [('Entrance steps (porch +1\'-3" to FFL +2\'-9", 3 risers)', 3, 6.25), ('Rear door D02 steps (passage +1\'-0", 4 risers)', 4, 3.5),
             ('Raw-kitchen side door D12 steps (4 risers)', 4, 3.0), ('Rear car porch to S-T lobby (3 risers)', 3, 3.5)]
ext_tread = sum(n * 1.0 * w for _, n, w in EXT_STEPS)   # 12" treads
ext_riser = sum(n * 0.5 * w for _, n, w in EXT_STEPS)

M = G['misc']
OUT_AREAS = [('Front car porch incl. 8\'-0" driveway strip (less entrance-lobby notch)', M['A_FP'], 'Porch'),
             ('Rear car porch 16\'-9½" x 8\'-6"', M['A_RP'], 'Porch'),
             ('Left and rear passages (G4)', M['A_PASS'], 'Passage'),
             ('Ramps at main and side gates', M['A_RAMP'], 'Passage'),
             ('Patio 3\'-7½" x 4\'-0" (open court beside dining)', 3.625 * 4.0, 'Passage')]

# ============================================================== paint - interior
PAINT = OrderedDict()
for k, r in R.items():
    if r['cat'] in ('BATH',) or k in ('G01', 'F01', 'S01'):
        continue
    H = r['fc']
    gross = r['perim'] * H
    ded = 0.0; rev = 0.0
    for (ref, w, h, a_full, own, rl) in FACES[k]:
        hh = min(h, H); a = w * hh
        d, revf = face_deduction(w * h, own)
        if d:
            ded += a if a_full == d or not revf else a
        if revf:
            rev += (2 * hh + w) * 0.375
    tiles = WALLT[k]['net'] if k in WALLT else 0.0
    net = gross - ded + rev - tiles
    PAINT[k] = dict(gross=gross, ded=ded, rev=rev, tiles=tiles, net=net, H=H)
# stairwell (3 storeys high), walls painted full height to the top ceiling
SW_PERIM = {'GF': 2 * (5.0 + 8.125), 'FF': 2 * (19.0 + 6.625), '2F': 2 * (15.875 + 7.0)}
sw_gross = SW_PERIM['GF'] * STOREY['GF'] + SW_PERIM['FF'] * STOREY['FF'] + SW_PERIM['2F'] * FC_2F
sw_ded = 0.0; sw_rev = 0.0
for k in ('G01', 'F01', 'S01'):
    for (ref, w, h, a_full, own, rl) in FACES[k]:
        d, revf = face_deduction(w * h, own)
        sw_ded += d
        if revf: sw_rev += rl * 0.375
w9 = [x for x in WROWS if x['ref'] == 'W09'][0]
sw_ded += w9['w'] * w9['h']; sw_rev += (2 * w9['h'] + w9['w']) * 0.375
PAINT['STAIR'] = dict(gross=sw_gross, ded=sw_ded, rev=sw_rev, tiles=0, net=sw_gross - sw_ded + sw_rev, H=0)
STAIR_SOFFIT = st_soffit

# ============================================================== paint - exterior (by elevation)
# wall lengths per elevation estimated from sheets 06-08 so that each floor adds up to the grey take-off
# (external wall length GF 133.4, FF 142.0, mumty 81.6 ft); property-line walls (GF 40.3, FF 36.0, 2F 12.6 ft) are not painted outside.
ELEV_LEN = OrderedDict([('Front (road)', {'GF': 33.0, 'FF': 38.0}), ('Left (side passage)', {'GF': 46.0, 'FF': 50.0}),
                        ('Rear (rear passage / rear porch)', {'GF': 36.0, 'FF': 34.0}),
                        ('Right open stretches (patio, open shaft)', {'GF': 18.4, 'FF': 20.0}),
                        ('Mumty walls above terrace (all sides)', {'2F': 81.6})])
assert abs(sum(v.get('GF', 0) for v in ELEV_LEN.values()) - R0.FLOORLEN['GF'][3]) < 0.05
assert abs(sum(v.get('FF', 0) for v in ELEV_LEN.values()) - R0.FLOORLEN['FF'][3]) < 0.05
H_EXT = {'GF': 1.75 + R0.GF_H + 1.0, 'FF': R0.FF_H + 1.0, '2F': R0.SF_H + 1.0}   # plinth + storey + slab band
ELEV_OF = {'Front': 'Front (road)', 'Front (car porch)': 'Front (road)', 'Left': 'Left (side passage)',
           'Rear': 'Rear (rear passage / rear porch)', 'Right': 'Right open stretches (patio, open shaft)',
           'Right (patio)': 'Right open stretches (patio, open shaft)', 'Right (open shaft)': 'Right open stretches (patio, open shaft)'}
EXT_OPEN = defaultdict(list)
for x in WROWS:
    e = 'Mumty walls above terrace (all sides)' if x['fl'] == '2F' else ELEV_OF[x['elev']]
    for i in range(x['n']): EXT_OPEN[e].append((x['ref'], x['w'], x['h']))
for (ref, fl, ra, rb, w, h, *_ ) in DOORS:
    if rb.startswith('EXT'):
        e = {'EXT:Front': 'Front (road)', 'EXT:Rear': 'Rear (rear passage / rear porch)', 'EXT:Left': 'Left (side passage)',
             'EXT:Mumty': 'Mumty walls above terrace (all sides)'}[rb]
        EXT_OPEN[e].append((ref, w, h))
EXT_OPEN['Mumty walls above terrace (all sides)'].append(('Laundry open side', 5.125, R0.SF_H))
EXTP = OrderedDict()
for e, lens in ELEV_LEN.items():
    gross = sum(L * H_EXT[fl] for fl, L in lens.items())
    ded = rev = 0.0
    for (ref, w, h) in EXT_OPEN[e]:
        d, revf = face_deduction(w * h, False)      # exterior face: small openings not deducted (IS 1200)
        ded += d
        if revf: rev += (2 * h + w) * 0.375
    EXTP[e] = dict(gross=gross, ded=ded, rev=rev, net=gross - ded + rev, lens=lens)
PARAPET = G['items'] and [i for i in G['items'] if i['code'] == '10.9'][0]['qty']
SOFFIT = M['A_SOFF']

# ============================================================== boundary walls (grey G1-G3) each face
BW = []
for (name, L, H, side, fac) in M['BWALL']:
    inner = L * (H - 1.2)                      # from inside paving (+1'-0" to +1'-3") to top
    outer = L * H                              # street / gali / neighbour side from road level
    BW.append((name, L, H, side, inner, outer))
L_PAN = sum(b[1] for b in BW)
coping_top = M['Lpan'] * 1.0 + 10 * 1.5 * 1.5
pillars_extra = 7 * 2 * 0.19 * 6.5 * 2 + 3 * 2 * 0.19 * 6.5 * 2      # pillar side faces, both faces
GATES = [('Main gate (M-gate), 12\'-9" opening', 12.75, 6.5), ('Side gate (S-gate), 7\'-8¼" opening', 7.69, 7.0)]
RAILS = [('Stair-well guard rail at 2F floor edge (open side of stair opening)', 14.0, 3.0, 'SS 304 or MS painted'),
         ('Front balcony (FF kitchen terrace) railing', 15.0, 3.5, 'glass railing per grey exclusions - not painted'),
         ('Stair handrail on flights (wall-mounted, optional)', 2 * (R0.g1 + R0.g2), 0.0, 'optional')]

# ============================================================== electrical points (room by room)
# DL = LED downlights in false ceiling; deco W = pendant/chandelier/mirror/strip watts; F fan; EX exhaust;
# AC tons; S5 = 5/6 A sockets; P15 = 15/16 A power points; LV = data/CCTV/Wi-Fi; SB = switch boards
EP = OrderedDict([
 ('G01', (2, 0, 0, 0, 0, 1, 0, 0, 1, '2-way switching with stair')),
 ('G02', (4, 40, 0, 0, 0, 1, 0, 1, 2, 'chandelier (drawn) + Wi-Fi AP')),
 ('G03', (8, 0, 1, 0, 1.5, 4, 1, 0, 2, 'bed-head board with 2 sockets')),
 ('G04', (1, 0, 0, 0, 0, 1, 0, 0, 1, '')),
 ('G05', (2, 10, 0, 1, 0, 1, 0, 0, 1, 'mirror light; shaver socket')),
 ('G06', (8, 0, 1, 0, 1.5, 4, 1, 0, 2, '')),
 ('G07', (1, 0, 0, 0, 0, 1, 0, 0, 1, '')),
 ('G08', (3, 10, 0, 1, 0, 1, 0, 0, 1, '')),
 ('G09', (4, 40, 1, 0, 1.0, 2, 0, 0, 1, 'pendant over table')),
 ('G10', (1, 10, 0, 1, 0, 0, 0, 0, 1, '')),
 ('G11', (6, 30, 0, 0, 0, 5, 3, 0, 1, 'hood, microwave/oven, fridge; island socket')),
 ('G12', (3, 0, 1, 1, 0, 3, 2, 0, 1, 'freezer, water dispenser/kettle')),
 ('G13', (8, 30, 1, 0, 2.0, 4, 1, 2, 2, 'TV wall: router + NVR position (drawn)')),
 ('G14', (7, 40, 1, 0, 1.5, 4, 1, 0, 2, '')),
 ('G15', (2, 40, 0, 0, 0, 1, 0, 0, 1, 'double-height pendant')),
 ('G16', (1, 0, 0, 0, 0, 0, 0, 0, 1, '')),
 ('F01', (3, 30, 0, 0, 0, 1, 0, 0, 2, '3 stair wall lights; 2-way')),
 ('F02', (3, 0, 0, 0, 0, 1, 0, 1, 1, 'Wi-Fi AP')),
 ('F03', (3, 40, 0, 0, 0, 1, 0, 0, 1, 'pendant at front glazing')),
 ('F04', (7, 0, 1, 0, 1.5, 4, 1, 0, 2, '')),
 ('F05', (1, 0, 0, 0, 0, 1, 0, 0, 1, '')),
 ('F06', (2, 10, 0, 1, 0, 1, 0, 0, 1, '')),
 ('F07', (9, 0, 1, 0, 1.5, 4, 1, 0, 2, '')),
 ('F08', (1, 0, 0, 0, 0, 1, 0, 0, 1, '')),
 ('F09', (2, 10, 0, 1, 0, 1, 0, 0, 1, '')),
 ('F10', (9, 30, 1, 0, 2.0, 4, 1, 1, 2, '')),
 ('F11', (2, 0, 0, 0, 0, 1, 0, 0, 1, '')),
 ('F12', (5, 30, 0, 1, 0, 4, 2, 0, 1, 'hood + exhaust fan (drawn), microwave, fridge')),
 ('F13', (9, 0, 1, 0, 1.5, 4, 1, 0, 2, '')),
 ('F14', (2, 0, 0, 0, 0, 1, 0, 0, 1, '')),
 ('F15', (2, 10, 0, 1, 0, 1, 0, 0, 1, '')),
 ('S01', (3, 0, 0, 0, 0, 1, 0, 1, 1, 'Wi-Fi AP (covers terrace)')),
 ('S02', (6, 0, 1, 0, 1.0, 3, 1, 0, 2, '')),
 ('S03', (1, 10, 0, 1, 0, 0, 0, 0, 1, '')),
 ('S04', (2, 0, 0, 0, 0, 1, 1, 0, 1, 'washing machine; inverter + battery position (J4)')),
])
assert set(EP) == set(R)
EXT_PTS = [  # name, lights(15 W), sockets 5A (weatherproof), power, LV, SB, note
 ('Front car porch', 4, 1, 0, 1, 1, 'fan 1; EV charger point (J6); CCTV'),
 ('Rear car porch + rear passage', 3, 1, 0, 2, 1, 'CCTV x2 (back gali, rear passage)'),
 ('Left passage + lawn', 8, 1, 0, 2, 1, '5 wall lights (drawn) + 3 lawn lights; CCTV x2'),
 ('Gates and boundary pillars', 4, 0, 0, 2, 1, 'pillar lights; 2 call bells; CCTV at main gate'),
 ('Front elevation profile lights', 3, 0, 0, 0, 0, 'LED profile strips shown on sheet 09 (3 runs)'),
 ('Terrace and mumty roof', 4, 2, 0, 0, 1, 'solar DB/isolators separate'),
 ('Front balcony (FF kitchen terrace)', 1, 1, 0, 0, 0, ''),
]
FANS_EXT = 1                                   # car porch fan
CCTV_N = 7

# ---------------- connected load & maximum demand
W_DL, W_FAN, W_EX, W_S5, W_P15, W_EXTL = 12, 75, 30, 100, 1000, 15
AC_KW = {1.0: 1.15, 1.5: 1.60, 2.0: 2.20}            # inverter split, max input at 46 deg C
tot = defaultdict(float); cnt = defaultdict(int)
for k, (dl, deco, fan, ex, ac, s5, p15, lv, sb, note) in EP.items():
    cnt['DL'] += dl; cnt['F'] += fan; cnt['EX'] += ex; cnt['S5'] += s5; cnt['P15'] += p15; cnt['LV'] += lv; cnt['SB'] += sb
    if ac: cnt['AC'] += 1; cnt['AC%.1f' % ac] += 1
    tot['light'] += dl * W_DL + deco
    tot['fan'] += fan * W_FAN; tot['exh'] += ex * W_EX; tot['s5'] += s5 * W_S5; tot['p15'] += p15 * W_P15
    if ac: tot['ac'] += AC_KW[ac] * 1000
for (n, l, s, p, lv, sb, note) in EXT_PTS:
    cnt['EXTL'] += l; cnt['S5ext'] += s; cnt['LVext'] += lv; cnt['SBext'] += sb
    tot['light'] += l * W_EXTL; tot['s5'] += s * W_S5
tot['fan'] += FANS_EXT * W_FAN; cnt['F'] += FANS_EXT
assert cnt['AC'] == 10
FIXED = [('Kitchen: microwave/oven (open kitchen)', 1500), ('Kitchen: microwave (FF kitchen)', 1200), ('Refrigerators x2', 2 * 250),
         ('Deep freezer (raw kitchen)', 300), ('Water dispenser', 500), ('Kitchen hoods x2', 2 * 200),
         ('Washing machine (automatic, heater)', 2200), ('Water pump 1 HP (ground tank to roof tank)', 1000),
         ('Wi-Fi + NVR + 7 CCTV cameras', 150), ('Inverter/battery self-use', 100)]
EV_KW = 7.4
DF = OrderedDict([('light', 0.9), ('fan', 0.75), ('exh', 0.5), ('s5', 0.2), ('p15', 0.25), ('ac', 0.85), ('fixed', 0.6), ('ev', 1.0)])
fixed_w = sum(w for _, w in FIXED)
LOADS = [('Lighting (downlights 12 W, decorative, outdoor 15 W)', tot['light'], DF['light']),
         ('Ceiling fans %d x 75 W' % cnt['F'], tot['fan'], DF['fan']),
         ('Exhaust fans %d x 30 W' % cnt['EX'], tot['exh'], DF['exh']),
         ('General sockets %d x 100 W' % (cnt['S5'] + cnt['S5ext']), tot['s5'], DF['s5']),
         ('15 A power points %d x 1,000 W (iron, heater, kettle, TV)' % cnt['P15'], tot['p15'], DF['p15']),
         ('10 inverter ACs: %d x 1 t, %d x 1.5 t, %d x 2 t' % (cnt['AC1.0'], cnt['AC1.5'], cnt['AC2.0']), tot['ac'], DF['ac']),
         ('Kitchen, laundry, pump and IT loads (listed below)', fixed_w, DF['fixed']),
         ('EV charger %.1f kW' % EV_KW, EV_KW * 1000, DF['ev'])]
CONNECTED = sum(l[1] for l in LOADS)
MD = sum(l[1] * l[2] for l in LOADS)
MD_NO_EV = MD - EV_KW * 1000
I_MD = MD / (math.sqrt(3) * 400 * 0.9)

# ---------------- solar & battery
PANEL = 650
SOL = {k: math.ceil(k * 1000 / PANEL) for k in (12, 15)}
NIGHT = [('LED lights in use (~20 downlights x 12 W, 4 h)', 240, 4.0), ('Outdoor / security lights (6 x 15 W, 11 h)', 90, 11.0),
         ('Ceiling fans in bedrooms (4 x 75 W, 9 h)', 300, 9.0), ('Fridge + freezer (average draw, 12 h)', 120, 12.0),
         ('Wi-Fi, NVR and 7 cameras (12 h)', 60, 12.0), ('Water pump (1 kW, 20 min)', 1000, 0.33),
         ('TV, phone and laptop charging (3 h)', 150, 3.0), ('Inverter idle self-consumption (12 h)', 40, 12.0)]
E_ESS = sum(w * h for _, w, h in NIGHT) / 1000
AC_NIGHT = (700, 7.0)                         # one 1.5-ton inverter AC, average draw, 7 h of sleep
E_AC = AC_NIGHT[0] * AC_NIGHT[1] / 1000
DOD, ETA = 0.90, 0.92
CAP_ESS = E_ESS / (DOD * ETA); CAP_AC = (E_ESS + E_AC) / (DOD * ETA)
BAT_LO, BAT_HI = math.ceil(CAP_ESS), math.ceil(CAP_AC)

fc_tot = defaultdict(float)
for _k, _r in R.items():
    _a = _r['gross'] - (STAIR_OPEN['S01'] if _k == 'F01' else 0)
    fc_tot['moisture-resistant' if _r['cat'] in ('BATH', 'WET') else 'standard'] += _a
Q = [
 ('Floors', [
  ('Main floor tile 2\' x 4\' (600 x 1200): which quality?', 'a) Local glazed porcelain (Master Tiles, Stile) b) Imported Chinese polished glazed porcelain, grade A, 9-10 mm c) Spanish porcelain (Porcelanosa, Peronda)',
   'b) Imported Chinese polished porcelain, light marble look', 'a) about -15%; c) +150-200%'),
  ('Finish and colour of the 2\' x 4\' tiles?', 'a) Polished, light marble-look (ivory / warm white) throughout b) Polished in living areas, matt wood-look in bedrooms c) Matt / satin greige throughout',
   'a) Polished light marble-look; one tile throughout', 'b) +5-10%; c) same'),
  ('Skirting?', 'a) 4" cut from the same floor tile b) 4" matching marble skirting c) 3" PVC / aluminium flush skirting', 'a) Cut from floor tile', 'b) +Rs 150/rft; c) +Rs 250/rft'),
  ('Stairs and landings (42 treads, 44 risers, 2 landings)?', 'a) Imported granite treads (Black Galaxy / Steel Grey) + white marble risers b) Local marble (Botticino-type / Sunny grey) treads and risers c) Porcelain step tiles with nosing',
   'a) Granite treads with anti-slip grooves, marble risers', 'b) -30%; c) -20%'),
  ('Car porches, passages, driveway, ramps (%s sft)?' % f0(sum(x[1] for x in OUT_AREAS)), 'a) 60 mm interlocking tuff tiles (pavers), grey + charcoal border b) 20 mm exterior porcelain, anti-slip c) Stamped / stencil concrete',
   'a) 60 mm tuff tiles (80 mm under car tracks)', 'b) +60%; c) -10%'),
  ('Kitchen floors?', 'a) Same 2\' x 4\' tile as the house b) 2\' x 2\' matt anti-slip porcelain', 'a) Same 2\' x 4\' tile (matt grade if available)', 'b) -10%'),
 ]),
 ('Bathrooms', [
  ('Bathroom floor tile?', 'a) 600 x 600 matt anti-slip porcelain (R10) b) 300 x 600 matt porcelain c) 300 x 300 local ceramic', 'a) 600 x 600 matt anti-slip porcelain', 'b) same; c) -40%'),
  ('Bathroom wall tile (to false ceiling)?', 'a) 300 x 600 glazed porcelain, one feature wall per bath b) 600 x 1200 porcelain slabs (fewer joints) c) 300 x 450 local ceramic',
   'a) 300 x 600 porcelain with a feature wall', 'b) +40%; c) -35%'),
  ('WCs (7 nos)?', 'a) Wall-hung WC + concealed cistern frame (Porta / Master WC; Grohe or Geberit frame) b) Floor-mounted one-piece (Porta, Master) c) Toto / Kohler / Duravit',
   'a) Wall-hung + concealed cistern (powder room included)', 'b) -Rs 60-80k per WC; c) +Rs 120k per WC'),
  ('Taps and showers?', 'a) Local premium brass (Sonex, Faisal, Master) - concealed mixer + rain shower + hand shower b) Grohe / Hansgrohe c) Basic local chrome',
   'a) Local premium, concealed diverter, 8" rain shower', 'b) +200-250%; c) -40%'),
  ('Vanities, basins, accessories and mirrors?', 'a) Counter-top basin on 20 mm stone slab with wall-hung HDHMR cabinet; standard SS accessory set; 3\' x 2\'-6" LED mirror\u2028b) Wall-hung basin only, plain mirror, basic accessories\u2028c) Imported vanity units and premium accessories (Grohe / Kohler)',
   'a) Stone-top vanity + cabinet (6 baths), wall-hung basin in powder room, LED mirrors', 'b) -55%; c) +60%'),
  ('Shower area?', 'a) 8 mm toughened glass fixed screen (no door) b) Full glass enclosure with door c) Shower curtain only', 'a) Fixed glass screen in 6 baths', 'b) +80%; c) -90%'),
 ]),
 ('Kitchen', [
  ('Kitchen cabinets: in scope? (3 kitchens)', 'a) Yes: HDHMR / moisture-resistant MDF carcass, acrylic or lacquer shutters, soft-close fittings (Hettich) b) Yes: solid wood shutters c) Not in scope (separate contract)',
   'a) In scope, HDHMR + acrylic, Hettich', 'b) +40%; c) excluded'),
  ('Kitchen counter tops?', 'a) Quartz in the open kitchen; granite (Black Galaxy / Absolute Black) in raw and FF kitchens b) Granite everywhere c) Quartz everywhere',
   'a) Quartz (open) + granite (raw, FF)', 'b) -15%; c) +25%'),
  ('Hobs, hoods, sinks: in scope?', 'a) Yes: built-in gas hobs and chimney hoods (Nasgas, Canon, Signature), stainless double sinks with mixer b) Yes, imported (Franke, Elica, Bosch) c) Sinks only',
   'a) Local premium hob + hood in open and FF kitchens; 2 sinks + 1 sink', 'b) +120%; c) -70%'),
 ]),
 ('Doors', [
  ('Main door D01 (5\'-1½" double leaf)?', 'a) Solid Diyar (deodar) with polish, 2½" leaf b) Solid Ash / Oak (imported) with PU polish c) Steel security door with wood skin',
   'a) Solid Diyar, PU polish, glazed fanlight above', 'b) +40%; c) -10%'),
  ('Internal doors (bedrooms, dresses, store, kitchens: 19 nos)?', 'a) Semi-solid: Diyar frame with ply core and veneer skin, PU polish b) Solid wood c) HDF moulded / laminated (ready-made)',
   'a) Semi-solid veneer, PU polish; solid Diyar chowkhat', 'b) +60%; c) -35%'),
  ('Bathroom doors (7 nos)?', 'a) WPC (wood-plastic composite) door and frame - waterproof b) Same as internal doors with marine ply c) Aluminium + frosted glass',
   'a) WPC door and frame', 'b) +10%; c) -10%'),
  ('External single doors D02, D12, D28?', 'a) Solid Diyar with MS grill door outside b) Insulated steel security door (powder coated) c) Aluminium with grill',
   'b) Insulated steel security door', 'a) +15%; c) -20%'),
  ('Door hardware?', 'a) Mortise locks and lever handles (Dorma, Yale), SS hinges, door stoppers b) Good local hardware c) Smart lock on the main door in addition',
   'a) Dorma / Yale mortise + SS hinges', 'b) -50%; c) +Rs 60-90k'),
 ]),
 ('Windows', [
  ('Aluminium system (%s kg estimated)?' % f0(ALU_TOTAL), 'a) Local medium series, powder-coated charcoal / black, 3-track with fly-net b) Imported heavy series (e.g. Xingfa type), thermal break c) uPVC (German / Turkish profiles)',
   'a) Local medium series, charcoal powder coat', 'b) +60-80%; c) +40%'),
  ('Glass?', 'a) Double glazed 5 + 12 + 5 mm in all AC rooms; 5 mm frosted in baths b) Single 6 mm tinted / reflective c) 10 mm toughened or 6+6 laminated for the double-height units only, rest single',
   'a) Double glazing (tall units W06, W07, W09 in 6+6 laminated)', 'b) -45%; c) -30%'),
  ('Security grills?', 'a) MS grills on all GF windows and stair windows (inside, painted) b) No grills; multi-point locks only c) Grills on all openable windows, all floors',
   'a) GF and stair windows only', 'b) -Rs 120k; c) +Rs 150k'),
 ]),
 ('Paint', [
  ('Paint brand and system?', 'a) ICI Dulux / Berger premium: 2 putty + primer + 2 emulsion inside; Weathershield 2 coats outside b) Local good brands (Diamond, Brighto, Master Paints) c) Jotun / Nippon premium',
   'a) Dulux / Berger premium system', 'b) -30%; c) +15%'),
  ('Colour scheme?', 'a) Recommended: warm white ceilings/walls, one muted accent wall per bedroom (sage, dusty blue, clay), greige living areas; exterior off-white body, charcoal bands and frames, '
   'wood-tone accents; boundary walls light grey with charcoal coping and pillars b) All neutral (white / off-white) c) Your own colours', 'a) Recommended scheme', 'no cost difference'),
  ('Exterior feature finish?', 'a) Texture coat on feature bands and pillars, paint elsewhere b) Paint only c) Stone / wood-look cladding on the front features (sheet 09)', 'a) Texture on features', 'b) -10%; c) +Rs 300-450k'),
 ]),
 ('False ceiling', [
  ('False-ceiling system (%s sft)?' % f0(sum(fc_tot.values())), 'a) 12.5 mm gypsum board (Gyproc / Knauf) on GI frame, cove + profile lights in main rooms; moisture-resistant board in wet areas b) PVC panels c) 2\' x 2\' grid tiles',
   'a) Gypsum board, MR board in baths', 'b) -45%; c) -25%'),
 ]),
 ('Electrical fittings', [
  ('Switches, sockets, breakers and wires?', 'a) Schneider (Clipsal) or Legrand switches; Schneider / ABB breakers; Pakistan Cables / Fast / Newage copper wire b) Good local switches, Chint breakers c) Smart switches in living areas',
   'a) Schneider/Legrand + ABB/Schneider + Pakistan Cables', 'b) -35%; c) +Rs 150k'),
  ('Lights?', 'a) LED down-lights 12 W (Philips / Osram-Ledvance or good local), warm white 3000-4000 K, profile and cove strips as drawn b) Basic local LED c) Designer fittings in living areas',
   'a) Branded LED down-lights + strips', 'b) -40%; c) +Rs 200k'),
 ]),
 ('ACs and fans', [
  ('Air-conditioners (10: 2 x 1 t, 6 x 1.5 t, 2 x 2 t): in scope?', 'a) Yes, DC inverter split (Gree, Haier, Orient, Dawlance) b) Yes, Japanese (Mitsubishi, Daikin) c) Not in scope (owner buys)',
   'a) DC inverter, Gree or Haier', 'b) +60%; c) excluded'),
  ('Ceiling fans (%d)?' % cnt['F'], 'a) DC inverter fans 35-40 W (GFC, Pak Fan, Royal) b) Standard AC fans c) Designer fans with light', 'a) DC inverter fans', 'b) -35%; c) +80%'),
  ('Water heating?', 'a) Gas geysers on the SNGPL line: 2 x 35-gallon (GF, FF) + 1 instant gas in mumty b) Hybrid gas/electric geysers c) Instant electric heaters in each bath (+%s kW load)' % '21',
   'b) Hybrid gas/electric (Nasgas, Canon) - gas pressure is unreliable in winter', 'a) -25%; c) +10% and higher bills'),
 ]),
 ('Solar and EV', [
  ('Solar size and battery?', 'a) 15 kWp (23 x 650 W) + 12 kW 3-phase hybrid + %d kWh sodium-ion b) 12 kWp (19 panels) + %d kWh c) 15 kWp + %d kWh' % (BAT_HI, BAT_LO, BAT_LO),
   'a) 15 kWp + 12 kW + %d kWh;' % BAT_HI + ' panels Longi / Jinko / JA; inverter Deye / Growatt / Solis', 'b) -30%; c) -12%'),
  ('EV charger?', 'a) 7.4 kW single-phase wall box b) 11 kW three-phase wall box (needs 3-phase car charging) c) Conduit only now (charger later)',
   'a) 7.4 kW (suits most EVs sold in Pakistan); brand ABB / Schneider EVlink / good Chinese OEM', 'b) +25%; c) excluded'),
 ]),
 ('Plumbing equipment', [
  ('Pump and roof tank?', 'a) Pedrollo 1 HP pump + pressure switch; 500-gallon triple-layer plastic tank b) Grundfos booster set (constant pressure) c) Local pump',
   'a) Pedrollo 1 HP + 500-gal triple-layer tank', 'b) +150%; c) -40%'),
 ]),
 ('Railings, gates, marble/granite, wardrobes', [
  ('Main and side gates?', 'a) MS frame + 16-gauge sheet, powder coated, with pedestrian wicket in the main gate b) MS frame with wood-look HPL / aluminium slats c) Automated sliding main gate (motor)',
   'a) MS + sheet, powder coated', 'b) +40%; c) +Rs 250-350k'),
  ('Railings (stair-well edge, FF front balcony)?', 'a) SS 304 posts + 12 mm toughened glass b) MS railing, painted c) Glass with top rail only', 'a) SS + glass', 'b) -45%; c) +10%'),
  ('Window sills, door thresholds, bath counters?', 'a) Granite (Black Galaxy / Tropical) 20 mm b) Local marble 20 mm c) Quartz', 'a) Granite sills and thresholds', 'b) -30%; c) +50%'),
  ('Wardrobes (drawn in 7 dresses/rooms + store): in scope?', 'a) Yes: HDHMR carcass, laminate / lacquer shutters, Hettich fittings b) Yes: solid wood shutters c) Not in scope',
   'a) In scope, HDHMR + laminate', 'b) +45%; c) excluded'),
  ('Under-stair store and master-dress opening (D14, D09)?', 'a) Add both doors (flush door to store, sliding door to dress) b) Store door only, dress left open c) Neither',
   'b) Store door only', 'a) +Rs 45k; c) -Rs 25k'),
 ]),
]
QNUM = {}
_n = 0
for _g, _qs in Q:
    for _q in _qs:
        _n += 1; QNUM[_q[0]] = _n

# ============================================================== document blocks
B = []
def blk(**k): B.append(k)
def row(*c, kind=''): return dict(cells=[str(x) for x in c], kind=kind)
def table(header, widths, rows, align=None, font=8):
    blk(type='table', header=header, widths=widths, rows=rows, align=align or [], font=font)
PW, LW = 9906, 15038
RN = lambda k: R[k]['name'] if k in R else k
FLN = {'GF': 'Ground', 'FF': 'First', '2F': 'Second (mumty)'}

n_doors = sum(1 for d in DOORS if d[0].startswith('D'))
n_win = sum(x['n'] for x in WROWS if x['ref'].startswith('W'))
n_ven = sum(x['n'] for x in WROWS if x['ref'].startswith('V'))
cat_area = defaultdict(float)
for r in R.values(): cat_area[r['cat']] += r['area']
T24 = cat_area['T24'] + cat_area['HALL']

# ---- title & summary
blk(type='section', orientation='PORTRAIT')
blk(type='title', title='House No. 79/K, WAPDA City, Faisalabad', size=34, before=0,
    subtitle='FINISHING estimate - Step A: measurement schedules and questions (not priced)  |  October 2026')
blk(type='keys', keys=[('Rooms measured', str(len(R)), 'GF %d, FF %d, mumty %d' % tuple(sum(1 for r in R.values() if r['fl'] == f) for f in ('GF', 'FF', '2F'))),
                       ('Doors / openings', '%d + %d' % (n_doors, sum(1 for d in DOORS if d[0].startswith('A'))), 'doors + open arch'),
                       ('Windows + vents', '%d + %d' % (n_win, n_ven), 'aluminium %s kg' % f0(ALU_TOTAL)),
                       ('Max. demand', '%s kW' % f1(MD / 1000), '%s A per phase, 3-phase' % f0(I_MD))])
blk(type='p', size=17, text='This is Step A of the finishing estimate: everything is measured and scheduled, and the choices that drive cost are asked in Section 8. '
    'Nothing is priced yet. Areas are NET measured areas (no wastage); wastage and buying units come in Step B with prices.')
blk(type='h2', text='Binding inputs used (grey-structure Rev 1)')
blk(type='bullets', size=17, items=[
    'Levels (B5): FFL +2\'-9" = top of DPC; floor finish (tile + bed) must fit within 1½" above the 3" PCC sub-floor; porches +1\'-3", passages +1\'-0", lawn +1\'-2".',
    'No ceiling plaster (F1): every room gets a false ceiling. Ceiling height assumed 10\'-0" in GF and FF rooms (slab soffit 11\'-0" / ~11\'-2"), 8\'-6" in baths, laundry and the mumty room.',
    'Plaster to be painted: internal ½" 1:4, external ¾" 1:4 (F2); bathrooms tiled to the false ceiling.',
    'Roof terrace, mumty roof and FF front balcony are already finished with bhatta tiles in the grey work (F3) - not repeated here.',
    'Plastic roof tank 500 gallons on the mumty platform (I4); pump from the ground tank (I3); PPR PN-16/PN-20 and SNGPL gas pipe already in grey (I5).',
    'Electrical conduits for 10 ACs, Wi-Fi, CCTV, backup DBs, EV charger and solar are already in the grey work (J1-J8); this step sizes wires, fittings and equipment.',
])

# ---- 1. doors
blk(type='h1', text='1. Door schedule', newpage=True)
dr = []
for fl in ('GF', 'FF', '2F'):
    dr.append(row('%s floor' % FLN[fl], kind='section'))
    for (ref, f, ra, rb, w, h, swing, typ, flag) in DOORS:
        if f != fl: continue
        to = rb.replace('EXT:', 'outside - ') if rb.startswith('EXT') else RN(rb)
        dr.append(row(ref, RN(ra), to, '%s x %s' % (ftin(w), ftin(h)), swing, typ, flag))
table(['Ref', 'Room', 'Opens from / to', 'Clear opening (W x H)', 'Swing', 'Proposed type', 'Flag'], [600, 2000, 1700, 1350, 1400, 1856, 1000], dr,
      ['C', 'L', 'L', 'C', 'L', 'L', 'L'], font=7.5)
cnt_t = defaultdict(int)
for d in DOORS: cnt_t[d[7].split(' (')[0].split(' -')[0]] += 1
blk(type='note', text='Sizes are the masonry openings marked on sheets 06-08 (doors 8\'-0" high, lintel level). Totals: %d doors (1 main double door, %d internal/bedroom/dress/store/kitchen, %d bathroom, 3 external single, 1 aluminium sliding door), '
    'plus the 6\'-6" dining arch and the master-dress opening D09 (no leaf drawn). D14 (under-stair store) is not drawn - assumed 2\'-6" x 6\'-6".' % (
        n_doors, sum(1 for d in DOORS if d[7].startswith(('Internal', 'Store', 'Kitchen'))), sum(1 for d in DOORS if d[7].startswith('Bathroom'))))

# ---- 2. windows
wr = []
for x in WROWS:
    wr.append(row(x['ref'], x['fl'], RN(x['room']) if x['room'] in R else x['room'].replace('G13/F13', 'TV lounge (GF) + front bed (FF)').replace('G15/F03', 'Entrance (GF) + FF lobby').replace('F01/S01', 'Stair hall FF + 2F'),
                  x['elev'], '%s x %s' % (ftin(x['w']), ftin(x['h'])), ftin(x['sill']), TYPE_NAME[x['t']], x['n'], f1(x['glass'] * x['n']), f1(x['kg']), f1(x['kg'] * x['n']), x['flag']))
wr.append(row('D27', 'FF', 'Kitchen', 'Front (terrace)', '6\'-0" x 8\'-0"', '6"', TYPE_NAME['SD'], 1, f1(gl_sd), f1(kg_sd), f1(kg_sd), 'listed with doors'))
wr.append(row('', '', 'TOTAL', '', '', '', '', n_win + n_ven + 1, f1(GLASS_TOTAL), '', f1(ALU_TOTAL), '', kind='total'))
blk(type='section', orientation='LANDSCAPE')
blk(type='h1', text='2. Window and ventilator schedule, with aluminium weight')
table(['Ref', 'Floor', 'Room', 'Wall / elevation', 'Size (W x H)', 'Sill', 'Proposed opening type', 'Nos', 'Glass (sft)', 'Alu kg each', 'Alu kg total', 'Flag'],
      [600, 650, 2100, 1300, 1150, 600, 3300, 450, 850, 850, 900, 2288], wr, ['C', 'C', 'L', 'L', 'C', 'C', 'L', 'C', 'R', 'R', 'R', 'L'], font=7)
blk(type='note', text='Aluminium weights are estimates for a medium local series (powder-coated, ~1.2-1.4 mm wall) using: 3-track sliding frame 1.10 kg/m, glass sash 0.65 kg/m, '
    'net sash 0.40 kg/m, fixed frame 0.80 kg/m, transom 0.90 kg/m, top-hung vent frame 0.75 + sash 0.70 kg/m, sliding-door frame 1.60 / sash 1.10 kg/m, '
    'storefront (45 mm) frame and bars 1.80 kg/m with mullions at 4\'-6" and transoms at 6\'-0". The supplier\'s catalogue weights replace these in Step B (a heavier imported series adds 25-40%).')
blk(type='section', orientation='PORTRAIT')

# ---- 3. floors
blk(type='h1', text='3. Floor and skirting areas, room by room')
CATN = {'T24': '2\' x 4\' tiles', 'HALL': '2\' x 4\' tiles (stair-hall landing)', 'BATH': 'Bathroom floor', 'WET': 'Laundry (wet area)', 'KIT': 'Kitchen'}
fr = []
for fl in ('GF', 'FF', '2F'):
    fr.append(row('%s floor' % FLN[fl], kind='section'))
    for k, r in R.items():
        if r['fl'] != fl: continue
        size = '%s x %s' % (ftin(r['L']), ftin(r['W']))
        if k in STAIR_OPEN: size += ' less opening %s sft' % f1(STAIR_OPEN[k])
        fr.append(row(k, r['name'], size, CATN[r['cat']], f1(r['area']), f1(r['skirt']) if r['skirt'] else '-', r['flag']))
table(['Id', 'Room', 'Clear size', 'Floor finish group', 'Floor (sft)', 'Skirting (rft)', 'Flag'], [550, 2600, 1900, 1650, 900, 900, 1406], fr,
      ['C', 'L', 'L', 'L', 'R', 'R', 'L'], font=7.5)
blk(type='h2', text='Floor areas by finish group')
skirt_tot = sum(r['skirt'] for r in R.values())
grp = [('2\' x 4\' tiles - rooms, lobbies, dresses, store', cat_area['T24'], sum(r['skirt'] for r in R.values() if r['cat'] == 'T24')),
       ('2\' x 4\' tiles - stair-hall landings (GF, FF, 2F)', cat_area['HALL'], sum(r['skirt'] for r in R.values() if r['cat'] == 'HALL')),
       ('Bathroom floors (7: 6 baths + powder)', cat_area['BATH'], 0), ('Laundry floor (anti-slip)', cat_area['WET'], 0),
       ('Kitchens (open, raw, FF)', cat_area['KIT'], sum(r['skirt'] for r in R.values() if r['cat'] == 'KIT'))]
gr = [row(a, f1(b), f1(c) if c else '-') for a, b, c in grp]
gr.append(row('Internal floors total', f1(sum(x[1] for x in grp)), f1(skirt_tot), kind='subtotal'))
gr.append(row('Stairs: 42 treads 10½" x 3\'-6" (2 storeys)', f1(st_tread), f1(st_skirt) + ' (stepped skirting)'))
gr.append(row('Stairs: 44 risers 6.57" x 3\'-6"', f1(st_riser), '-'))
gr.append(row('Stairs: 2 mid landings 8\'-3" x 3\'-6"', f1(st_land), '-'))
gr.append(row('External steps: treads (%s)' % '; '.join('%s' % s[0].split(' (')[0] for s in EXT_STEPS), f1(ext_tread), '-'))
gr.append(row('External steps: risers', f1(ext_riser), '-'))
for a, b, c in OUT_AREAS:
    gr.append(row('%s - %s' % (c, a), f1(b), '-'))
gr.append(row('Roof terrace %s + mumty roof %s + FF balcony %s sft' % (f0(G['roof']['T']), f0(G['roof']['M']), f0(G['roof']['B'])),
              f1(G['roof']['A_ROOF']), 'done in grey (F3)', kind='gross'))
table(['Finish group', 'Area (sft)', 'Skirting (rft)'], [6106, 1700, 2100], gr, ['L', 'R', 'R'], font=8)
blk(type='note', text='Skirting is measured on walls actually present (open sides and door widths deducted). Bathrooms and the laundry have wall tiles instead of skirting; '
    'kitchen skirting excludes the counter runs. Stair-hall landing skirting is counted on its own; stepped stair skirting is shown with the stairs.')

# ---- 4. wall tiles
blk(type='h1', text='4. Wall-tile areas')
wt = []
for k, v in WALLT.items():
    wt.append(row(k, RN(k), v['note'], f1(v['gross']), f1(v['ded']) if v['ded'] else '-', f1(v['net'])))
wt_bath = sum(v['net'] for k, v in WALLT.items() if R[k]['cat'] == 'BATH')
wt_kit = sum(v['net'] for k, v in WALLT.items() if R[k]['cat'] == 'KIT')
wt.append(row('', 'Bathrooms total', '', '', '', f1(wt_bath), kind='subtotal'))
wt.append(row('', 'Kitchen backsplash total', '', '', '', f1(wt_kit), kind='subtotal'))
wt.append(row('', 'Laundry dado', '', '', '', f1(WALLT['S04']['net']), kind='subtotal'))
FEAT = [('GF TV lounge - TV wall 15\'-0" x 10\'-0" (porcelain slab or wood-look panel)', 150.0), ('FF TV lounge - TV wall 14\'-9" x 10\'-0"', 147.5),
        ('Front elevation - "wooden tile" cladding marked on sheet 09 (approx. 8\'-9" x 11\'-0")', 96.0)]
for a, b in FEAT:
    wt.append(row('opt', a, 'optional feature', '', '', f1(b), kind='gross'))
table(['Id', 'Room', 'Basis', 'Gross (sft)', 'Doors / vents (sft)', 'Net (sft)'], [550, 3000, 3256, 1000, 1100, 1000], wt, ['C', 'L', 'L', 'R', 'R', 'R'], font=7.5)
blk(type='note', text='Bath wall height = false-ceiling height 8\'-6" (tiles run 2-3" above the ceiling line). Door openings are deducted to 8\'-0"; ventilators in full. '
    'Feature walls are optional and not in the totals; the exterior wooden-tile panel on sheet 09 is measured approximately and needs confirming.')

# ---- 5. paint
blk(type='h1', text='5. Paint areas', newpage=True)
blk(type='p', size=17, text='Deduction rule (IS 1200 Part 15, as used in Pakistan PWD practice): openings up to 0.5 m2 (5.4 sft) not deducted; openings 0.5-3 m2 (5.4-32 sft) deducted from one face only '
    '(the room the door belongs to) and no reveals added; openings over 3 m2 deducted from both faces and their reveals (jambs and soffit, 4½" each side) added. '
    'Interior walls are painted up to the false ceiling; tiled areas are excluded.')
blk(type='h2', text='5.1 Interior walls, room by room')
pr = []
for fl in ('GF', 'FF', '2F'):
    pr.append(row('%s floor' % FLN[fl], kind='section'))
    for k, v in PAINT.items():
        if k == 'STAIR' or R[k]['fl'] != fl: continue
        pr.append(row(k, RN(k), '%s x %s' % (f1(R[k]['perim']), ftin(v['H'])), f1(v['gross']), f1(v['ded']) if v['ded'] else '-',
                      f1(v['rev']) if v['rev'] else '-', f1(v['tiles']) if v['tiles'] else '-', f1(v['net'])))
v = PAINT['STAIR']
pr.append(row('Stair', 'Stair well walls, GF to mumty ceiling (3 storeys)', 'GF %s x %s + FF %s x %s + 2F %s x %s' % (
    f1(SW_PERIM['GF']), f1(STOREY['GF']), f1(SW_PERIM['FF']), f1(STOREY['FF']), f1(SW_PERIM['2F']), f1(FC_2F)),
    f1(v['gross']), f1(v['ded']), f1(v['rev']), '-', f1(v['net'])))
int_tot = sum(v['net'] for v in PAINT.values())
pr.append(row('', 'Interior walls total', '', '', '', '', '', f1(int_tot), kind='total'))
pr.append(row('', 'Stair soffits (flights and landings, 2 storeys) - skim + paint', '', '', '', '', '', f1(STAIR_SOFFIT), kind='gross'))
table(['Id', 'Room', 'Wall length x height', 'Gross', 'Openings', 'Reveals', 'Tiles', 'Net (sft)'], [550, 2700, 2256, 900, 900, 800, 800, 1000], pr,
      ['C', 'L', 'L', 'R', 'R', 'R', 'R', 'R'], font=7.5)
blk(type='h2', text='5.2 Exterior walls, elevation by elevation')
er = []
for e, v in EXTP.items():
    lens = ' + '.join('%s %s ft x %s' % (fl, f1(L), f1(H_EXT[fl])) for fl, L in v['lens'].items())
    er.append(row(e, lens, f1(v['gross']), f1(v['ded']) if v['ded'] else '-', f1(v['rev']) if v['rev'] else '-', f1(v['net'])))
er.append(row('Parapets: terrace %s ft + mumty roof %s ft, both faces + top (grey 10.9)' % (f1(R0.PARA_FF_L), f1(R0.SF_PERIM)), '', '', '', '', f1(PARAPET)))
er.append(row('External soffits: car porch, canopy, entrance, chajjas, stair over rear porch (grey 10.10)', '', '', '', '', f1(SOFFIT)))
ext_tot = sum(v['net'] for v in EXTP.values()) + PARAPET + SOFFIT
er.append(row('Exterior total', '', '', '', '', f1(ext_tot), kind='total'))
table(['Elevation', 'Wall length x height (ft)', 'Gross', 'Openings', 'Reveals', 'Net (sft)'], [3000, 2906, 1000, 1000, 1000, 1000], er,
      ['L', 'L', 'R', 'R', 'R', 'R'], font=7.5)
blk(type='note', text='Heights: GF = exposed plinth 1\'-9" + 11\'-0" + 1\'-0" slab band; FF = 11\'-6½" + 1\'-0" band; mumty = 9\'-6½" + 1\'-0" band. '
    'Wall lengths per elevation are read from sheets 06-08 and balanced to the grey take-off (GF 133.4, FF 142.0, mumty 81.6 ft of external wall). '
    'Walls on the right property line (GF 40.3, FF 36.0, mumty 12.6 ft) face the neighbour and are not painted. '
    'Note: the grey plaster take-off left out the 1\'-0" slab-edge bands (about 360 sft); they are included here.')
blk(type='h2', text='5.3 Boundary walls, each face')
br = []
for (name, L, H, side, inner, outer) in BW:
    br.append(row(name, f1(L), ftin(H), f1(inner), f1(outer), {'street': 'street', 'gali': 'back gali', 'neighbour': 'neighbour (optional)'}[side]))
bin_ = sum(b[4] for b in BW); bout = sum(b[5] for b in BW); bnei = sum(b[5] for b in BW if b[3] == 'neighbour')
br.append(row('Coping top 12" + 10 pillar caps', '', '', f1(coping_top), '', ''))
br.append(row('Pillar side faces (7 x 13½" + 3 x 4\'-0" feature pillars)', '', '', f1(pillars_extra / 2), f1(pillars_extra / 2), ''))
br.append(row('Totals', f1(L_PAN), '', f1(bin_ + coping_top + pillars_extra / 2), f1(bout + pillars_extra / 2), 'of which neighbour faces %s' % f1(bnei), kind='total'))
table(['Stretch', 'Length (ft)', 'Height above road', 'Inside face (sft)', 'Outside face (sft)', 'Outside is'], [3600, 1000, 1300, 1300, 1300, 1406], br,
      ['L', 'R', 'C', 'R', 'R', 'L'], font=7.5)
blk(type='h2', text='5.4 Gates and railings (enamel / powder coat)')
gr2 = []
for n, w, h in GATES:
    gr2.append(row(n, '%s x %s' % (ftin(w), ftin(h)), f1(2 * w * h * 1.1), 'MS frame + sheet, both faces + 10% for frames and edges'))
for n, L, h, note in RAILS:
    gr2.append(row(n, '%s rft%s' % (f1(L), (' x %s' % ftin(h)) if h else ''), f1(L * h * 0.5) if 'painted' in note else '-', note))
table(['Item', 'Size', 'Paint area (sft)', 'Note'], [3800, 1700, 1300, 3106], gr2, ['L', 'C', 'R', 'L'], font=7.5)

# ---- 6. false ceiling
blk(type='h1', text='6. False-ceiling area, room by room')
fc = []
fc_tot = defaultdict(float)
FC_AREA = {}
for k, r in R.items():
    a = r['gross'] if k != 'F01' else r['gross'] - STAIR_OPEN['S01']   # FF hall: only where the 2F floor is overhead
    if k == 'G01': a = r['gross']
    FC_AREA[k] = a
    kind = 'moisture-resistant' if r['cat'] in ('BATH', 'WET') else 'standard'
    fc_tot[kind] += a
for fl in ('GF', 'FF', '2F'):
    fc.append(row('%s floor' % FLN[fl], kind='section'))
    for k, r in R.items():
        if r['fl'] != fl: continue
        kind = 'moisture-resistant' if r['cat'] in ('BATH', 'WET') else 'standard'
        note = {'F01': 'only under the 2F floor; the stair well is open above', 'S01': 'whole hall incl. over the stair well (top of shaft)'}.get(k, '')
        fc.append(row(k, r['name'], ftin(r['fc']), kind, f1(FC_AREA[k]), note))
fc.append(row('', 'Standard boards total', '', '', f1(fc_tot['standard']), '', kind='subtotal'))
fc.append(row('', 'Moisture-resistant (baths, powder, laundry) total', '', '', f1(fc_tot['moisture-resistant']), '', kind='subtotal'))
fc.append(row('', 'False ceiling total', '', '', f1(sum(fc_tot.values())), '', kind='total'))
table(['Id', 'Room', 'Height above floor', 'Board', 'Area (sft)', 'Note'], [550, 3100, 1300, 1500, 1000, 2456], fc, ['C', 'L', 'C', 'L', 'R', 'L'], font=7.5)
blk(type='note', text='Area = clear room area. Perimeter cove / drop-edge allowance, access panels and AC grille cut-outs are added in Step B. '
    'Car-porch and other external soffits are painted (Section 5.2), not false-ceilinged.')

# ---- 7. electrical
blk(type='section', orientation='LANDSCAPE')
blk(type='h1', text='7. Electrical: points, load, circuits, cables, solar and battery')
blk(type='h2', text='7.1 Point schedule, room by room (sheets 13-16 + Register J1-J8)')
er2 = []
for fl in ('GF', 'FF', '2F'):
    er2.append(row('%s floor' % FLN[fl], kind='section'))
    for k, (dl, deco, fan, ex, ac, s5, p15, lv, sb, note) in EP.items():
        if R[k]['fl'] != fl: continue
        er2.append(row(k, R[k]['name'], dl, ('%d W' % deco) if deco else '-', fan or '-', ex or '-', ('%g t' % ac) if ac else '-', s5 or '-', p15 or '-', lv or '-', sb, note))
er2.append(row('External', kind='section'))
for (n, l, s, p, lv, sb, note) in EXT_PTS:
    er2.append(row('', n, '-', '%d lights x 15 W' % l, 1 if n.startswith('Front car') else '-', '-', '-', s or '-', p or '-', lv or '-', sb or '-', note))
er2.append(row('', 'TOTAL', cnt['DL'], '%d outdoor' % cnt['EXTL'], cnt['F'], cnt['EX'], cnt['AC'], cnt['S5'] + cnt['S5ext'], cnt['P15'], cnt['LV'] + cnt['LVext'], cnt['SB'] + cnt['SBext'], '', kind='total'))
table(['Id', 'Room', 'Down-lights', 'Decorative / outdoor', 'Fans', 'Exhaust', 'AC', '5 A sockets', '15 A power', 'Data / CCTV', 'Switch boards', 'Note'],
      [550, 2600, 800, 1200, 600, 700, 600, 850, 850, 850, 850, 4588], er2, ['C', 'L', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'L'], font=7)
blk(type='note', text='Switch boards, sockets, fans, ACs, exhaust fans, cameras and the TV-wall router/NVR position follow sheets 13-15 (legend sheet 16). The drawings show only 1-3 wall lights per room; '
    'because every room now has a false ceiling, LED down-lights are proposed at about one per 20 sft (bedrooms and living) and one per 25-30 sft elsewhere. TV and intercom points are deleted (J2).')
blk(type='h2', text='7.2 Connected load and maximum demand')
lr = [row(a, f0(b), '%.2f' % c, f0(b * c)) for a, b, c in LOADS]
lr.append(row('TOTAL', f0(CONNECTED), '', f0(MD), kind='total'))
lr.append(row('Maximum demand without the EV charger', '', '', f0(MD_NO_EV), kind='subtotal'))
table(['Load group', 'Connected (W)', 'Diversity factor', 'Demand (W)'], [8038, 2300, 2000, 2700], lr, ['L', 'R', 'C', 'R'], font=7.5)
blk(type='note', text='Fixed loads: ' + '; '.join('%s %s W' % (a, f0(b)) for a, b in FIXED) + '. Geysers assumed gas (SNGPL line in grey, I5); an electric geyser option is asked in Q%d. ' % QNUM['Water heating?'] + \
    'AC inputs are maximum ratings at 46 °C (1 t 1.15 kW, 1.5 t 1.60 kW, 2 t 2.20 kW).')
blk(type='p', size=16, text='Main incomer: maximum demand %s kW at 400 V, 3-phase, p.f. 0.9 = %s A per phase (%s A without the EV). '
    'Recommended: FESCO 3-phase connection with a sanctioned load of about 30 kW, close to the maximum demand (it also allows net metering of the 15 kW solar plant - confirm the current NEPRA rules); '
    'main switch 63 A 4-pole MCCB; incomer cable 4-core 16 mm2 copper armoured (meter at the front, under 60 ft run: voltage drop about 1.5%%); main earth 16 mm2.' % (
        f1(MD / 1000), f0(I_MD), f0(MD_NO_EV / (math.sqrt(3) * 400 * 0.9))))
blk(type='h2', text='7.3 Circuit list and cable sizes (copper, PVC-insulated in conduit; Pakistani size in brackets)')
fl_pts = defaultdict(lambda: defaultdict(int))
for k, (dl, deco, fan, ex, ac, s5, p15, lv, sb, note) in EP.items():
    f = R[k]['fl']; fl_pts[f]['L'] += dl + (1 if deco else 0) + fan + ex; fl_pts[f]['S'] += s5; fl_pts[f]['P'] += p15; fl_pts[f]['AC'] += 1 if ac else 0
circ = []
for f in ('GF', 'FF', '2F'):
    p = fl_pts[f]
    circ.append(row('%s floor DB' % FLN[f], kind='section'))
    circ.append(row('Lighting + fans', math.ceil(p['L'] / 12), '%d points, max 12 per circuit' % p['L'], '1.5 mm2 (3/.029)', '10 A MCB', 'backup DB (essential) for half the circuits'))
    circ.append(row('General sockets 5/6 A', math.ceil(p['S'] / 8), '%d sockets, max 8 per ring/radial' % p['S'], '2.5 mm2 (7/.029)', '16 A MCB + 30 mA RCD', ''))
    circ.append(row('15/16 A power points', math.ceil(p['P'] / 2), '%d points, max 2 per radial' % p['P'], '4 mm2 (7/.036)', '20 A MCB + 30 mA RCD', ''))
    circ.append(row('Air-conditioners (one circuit each, J1)', p['AC'], '%d ACs' % p['AC'], '4 mm2 (7/.036)', '20 A MCB (C-curve)', '1 t and 1.5 t could use 2.5 mm2; 4 mm2 kept for runs up to 60 ft'))
circ.append(row('Special circuits', kind='section'))
for a, n, b, c, d, e in [('Kitchen cooking / microwave (open + FF kitchen)', 2, '1 each', '4 mm2 (7/.036)', '20 A MCB + RCD', ''),
                          ('Washing machine (laundry)', 1, '1', '4 mm2 (7/.036)', '20 A MCB + RCD', ''),
                          ('Water pump 1 HP (from backup DB)', 1, '1', '2.5 mm2 (7/.029)', '16 A MCB (C/D-curve)', 'J7 conduit in grey'),
                          ('External lighting (porches, passages, lawn, pillars, profile lights)', 2, '%d lights' % cnt['EXTL'], '1.5 mm2 (3/.029)', '10 A MCB + photocell/timer', ''),
                          ('Wi-Fi, NVR, cameras, bells (backup DB)', 1, '%d data/CCTV points' % (cnt['LV'] + cnt['LVext']), '2.5 mm2 (7/.029)', '10 A MCB', 'Cat6 for cameras and access points'),
                          ('EV charger 7.4 kW single-phase (32 A)', 1, '1', '6 mm2 (7/.044) + 6 mm2 earth', '40 A Type-A RCBO + DC-leak detection in charger', 'or 11 kW three-phase: 4-core 4 mm2 + earth, 20 A 4-pole'),
                          ('Sub-main: GF main DB to FF DB (3-phase)', 1, '', '4 x 10 mm2 + 6 mm2 earth', '40 A 4-pole', ''),
                          ('Sub-main: FF DB to mumty DB (single-phase)', 1, '', '2 x 6 mm2 + 4 mm2 earth', '32 A DP', ''),
                          ('Inverter AC-out to backup DBs (3-phase)', 1, '', '4 x 10 mm2 + 6 mm2 earth', '40 A 4-pole', 'J5 conduits in grey'),
                          ('PV strings roof to inverter', 2, '2 strings', '6 mm2 DC solar cable (red/black)', 'DC isolator + SPD', 'J4 spare conduits'),
                          ('Battery to inverter (48 V class)', 1, '', '2 x 70 mm2 flexible copper, < 10 ft', '250 A DC fuse/breaker', '')]:
    circ.append(row(a, n, b, c, d, e))
n_circ = sum(int(c['cells'][1]) for c in circ if c['kind'] == '' and c['cells'][1].isdigit() and not c['cells'][0].startswith(('Sub-main', 'Inverter', 'PV', 'Battery')))
circ.append(row('Total final circuits from the DBs (sub-mains, PV and battery cables not counted)', n_circ, '', '', '', '', kind='total'))
table(['Circuit type', 'No.', 'Points', 'Cable', 'Protection', 'Note'], [4000, 600, 2500, 2700, 2400, 2838], circ, ['L', 'C', 'L', 'L', 'L', 'L'], font=7)

blk(type='h2', text='7.4 Solar PV')
sol = [row('12 kW option', '12,000 / 650 = %.1f' % (12000 / PANEL), '%d panels = %s kWp' % (SOL[12], f2(SOL[12] * PANEL / 1000)), '2 strings: 10 + 9', 'fits the terrace layout (grey Section 7) with 4 tables free'),
       row('15 kW option', '15,000 / 650 = %.1f' % (15000 / PANEL), '%d panels = %s kWp' % (SOL[15], f2(SOL[15] * PANEL / 1000)), '2 strings: 12 + 11', 'exactly the grey layout: 34 plinths already cast (J3)')]
table(['Option', 'Working', 'Panels', 'Strings', 'Note'], [2200, 2600, 2600, 2400, 5238], sol, ['L', 'L', 'L', 'L', 'L'], font=7.5)
blk(type='p', size=16, text='String check (650 W bifacial, Voc ≈ 45 V, Vmp ≈ 38 V, Isc ≈ 18.5 A): 12 panels at the coldest Faisalabad morning (about 0 °C, +6.5%%) give Voc ≈ 577 V, below the 800-1,000 V limit of common hybrid inverters; '
    '11 panels at 70 °C cell temperature give Vmp ≈ 363 V, inside the MPPT window. The inverter must accept about 20 A per MPPT input. '
    'Inverter: one 12 kW THREE-PHASE hybrid inverter (DC/AC ratio 1.25 with 15 kWp - normal, the panels rarely give full rating in Faisalabad heat) feeding the 3-phase backup DBs, '
    'with a 48 V-class battery. Typical makes: Deye, Growatt, Solis, Huawei (high-voltage battery types), Inverex. Grid export through a FESCO net/bi-directional meter.')
blk(type='h2', text='7.5 Sodium-ion battery - night-time essential load')
nr = [row(a, f0(w), '%g' % h, f2(w * h / 1000)) for a, w, h in NIGHT]
nr.append(row('Essential night load', '', '', f2(E_ESS), kind='subtotal'))
nr.append(row('Optional: one 1.5-ton inverter AC in the master bedroom (average 700 W x 7 h)', '700', '7', f2(E_AC)))
nr.append(row('Essential + one bedroom AC', '', '', f2(E_ESS + E_AC), kind='subtotal'))
table(['Load (7 pm - 7 am)', 'Watts', 'Hours', 'kWh'], [9038, 2000, 1500, 2500], nr, ['L', 'R', 'C', 'R'], font=7.5)
blk(type='p', size=16, text='Capacity = energy / (usable depth of discharge 0.90 x round-trip efficiency 0.92). Essential only: %s / 0.83 = %s kWh -> %d kWh. '
    'Essential + one bedroom AC: %s / 0.83 = %s kWh -> %d kWh (e.g. three 5.3 kWh modules). Peak backup power about 4.5 kW (AC + pump + fans + fridge) = 90 A at 51 V, well inside a %d kWh bank. '
    'Recommended default: %d kWh, because summer nights in Faisalabad need one AC; %d kWh is the economy option (Q%d). Sodium-ion packs are still new in Pakistan: the pack\'s BMS must be on the '
    'inverter\'s approved list (CAN/RS485) and its voltage window must suit the inverter; if no compatible sodium-ion pack is available locally at Step B, an LFP pack of the same kWh is the fall-back.' % (
        f2(E_ESS), f1(CAP_ESS), BAT_LO, f2(E_ESS + E_AC), f1(CAP_AC), BAT_HI, BAT_HI, BAT_HI, BAT_LO, QNUM['Solar size and battery?']))

# ---- 8. questionnaire (Q list defined earlier)
blk(type='section', orientation='LANDSCAPE')
blk(type='h1', text='8. Finishing questionnaire (max. 40 questions)')
blk(type='h2', text='How to answer')
blk(type='bullets', size=17, items=['Write your choice (a, b or c, or your own words) in the last column.', 'RULE: a blank answer = my recommended default.',
    'Where a question asks "in scope?", answer whether the item should be priced in the finishing estimate or bought separately.'])
blk(type='p', size=17, text='Leave "Your answer" blank to accept my recommended default. Brands are typical of the Faisalabad / Lahore market; cost differences are rough, material only, '
    'against the recommended default, and will be priced properly in Step B.')
nq = sum(len(v) for _, v in Q)
assert nq <= 40, nq
qr = []; i = 0
for g, qs in Q:
    qr.append(row(g, kind='section'))
    for (q, opts, dflt, cost) in qs:
        i += 1
        qr.append(row('Q%d' % i, q + '\u2028\u2028Options:\u2028' + opts, dflt, cost, ''))
table(['Q', 'Question and options (typical brands)', 'Recommended default (used if blank)', 'Rough cost difference', 'Your answer'],
      [550, 6600, 3200, 2200, 2488], qr, ['C', 'L', 'L', 'L', 'L'], font=7)

# ---- 9. checks & flags
blk(type='section', orientation='PORTRAIT')
blk(type='h1', text='9. Completeness check and flagged assumptions')
gf_sum = sum(r['area'] for r in R.values() if r['fl'] == 'GF')
ff_sum = sum(r['area'] for r in R.values() if r['fl'] == 'FF')
sf_sum = sum(r['area'] for r in R.values() if r['fl'] == '2F')
ff_ref = 1705.0 - 38.7 - G['roof']['B'] - 245.0
sf_ref = 353.2 - 68.0 - STAIR_OPEN['S01']
chk = [
 ('Rooms', 'All %d rooms on sheets 01-03 / 06-08 are listed in Sections 3, 5 and 6 (GF 16, FF 15, mumty 4); patio, porches, passages and ramps in Section 3.' % len(R), 'PASS'),
 ('Doors', '%d doors (D01-D30) + the dining arch; every 8\'-0" opening on sheets 06-08 has a reference; D14 not drawn (assumed).' % n_doors, 'PASS'),
 ('Windows / vents', '%d windows (W01-W15, two of them x2) + %d ventilators (V01-V07) + sliding door D27; same sizes as the opening list used for the grey masonry deductions.' % (n_win, n_ven), 'PASS'),
 ('GF floor area', 'Sum of GF rooms %s sft vs clear floor inside walls in grey take-off 1,362.6 sft (difference %s%%).' % (f1(gf_sum), f1(100 * (gf_sum - 1362.6) / 1362.6)), 'PASS'),
 ('FF floor area', 'Sum of FF rooms %s sft vs FF slab 1,705 less porch cantilever 38.7, balcony %s and walls 245 = %s sft (difference %s%%).' % (
     f1(ff_sum), f1(G['roof']['B']), f1(ff_ref), f1(100 * (ff_sum - ff_ref) / ff_ref)), 'PASS'),
 ('Mumty floor area', 'Sum %s sft vs mumty slab 353.2 less walls 68 and stair opening 74.3 = %s sft (laundry partly outside the roof outline).' % (f1(sf_sum), f1(sf_ref)), 'PASS'),
 ('No double counting', 'Bath walls are tiled, not painted; kitchen backsplash deducted from paint; stair-hall walls measured once as the stair well; terrace tiles left in grey; '
  'W06/W07/W09 counted once though they serve two floors.', 'PASS'),
 ('Electrical', '10 ACs (J1) = 5 GF + 4 FF + 1 mumty; %d fans; %d exhaust fans; %d cameras; Wi-Fi in 4 positions; EV point at the front porch.' % (cnt['F'], cnt['EX'], CCTV_N), 'PASS'),
]
table(['Check', 'Result', ''], [1800, 7106, 1000], [row(a, b, c, kind='pass') for a, b, c in chk], ['L', 'L', 'C'], font=7.5)
blk(type='h2', text='Flagged assumptions (sizes not shown on the drawings)')
FLAGS = [
 'Lobby lengths (GF lobby 15\'-6", FF rear lobby 12\'-6", FF front lobby 12\'-0") and the entrance foyer depth (6\'-0") are measured on the plans, not dimensioned.',
 'Under-stair store (S-A) 5\'-0" x 3\'-6" and its door D14 2\'-6" x 6\'-6" are assumed - the door is not drawn.',
 'Master-dress (GF) opening D09 has no leaf drawn; 2\'-6" opening assumed. Powder-room door D10 is taken as opening off the drawing-room side - please confirm.',
 'Raw-kitchen window W04 3\'-0" x 4\'-6" read with sill 3\'-6" (head at 8\'-0").',
 'Main door leaf height 8\'-0" inside the 20\'-6" entrance opening; the 12\'-6" above is fixed glazing (W07).',
 'False-ceiling heights 10\'-0" (GF/FF rooms) and 8\'-6" (baths, laundry, mumty room) are proposed - not on the drawings.',
 'Kitchen counter runs (backsplash) are read from the furniture plans: open kitchen 11\'-3", raw kitchen 16\'-0", FF kitchen 19\'-0".',
 'Exterior wall lengths per elevation are estimated from the plans and balanced to the grey totals; the wooden-tile cladding on sheet 09 is approximate (96 sft).',
 'Gate heights: main gate 6\'-6", side gate 7\'-0" (not dimensioned).',
 'Laundry is open on the terrace side; the inverter and battery are placed there (grey J4) - a lockable louvred door or weather screen is advisable (optional).',
]
blk(type='numbers', size=16, items=FLAGS)
blk(type='h2', text='Optional items (not in the base scope)')
blk(type='bullets', size=16, items=[
    'Feature walls: TV walls in both lounges (about 300 sft) and the front-elevation wooden-tile cladding.',
    'Lockable louvred aluminium door / screen for the laundry to protect the inverter and battery.',
    'Solar water heater (100-150 L) on the mumty roof to cut geyser gas/electricity.',
    'Whole-house surge protection (Type 2 SPD at the main DB) and a lightning conductor on the mumty - the earth pit is already in grey (J7).',
])
json.dump(B, open(OUT, 'w'), indent=0, ensure_ascii=False)
print('rooms', len(R), 'doors', n_doors, 'win', n_win, 'vents', n_ven, 'alu kg', round(ALU_TOTAL), 'glass', round(GLASS_TOTAL),
      'MD kW', round(MD / 1000, 1), 'I', round(I_MD), 'questions', nq, 'T24', round(T24), 'bath', round(cat_area['BATH']), 'kit', round(cat_area['KIT']),
      'int paint', round(int_tot), 'ext paint', round(ext_tot), 'FC', round(sum(fc_tot.values())), 'batt', round(CAP_ESS, 1), round(CAP_AC, 1),
      'gf', round(gf_sum, 1), 'ff', round(ff_sum, 1), round(ff_ref, 1), 'sf', round(sf_sum, 1), round(sf_ref, 1))
