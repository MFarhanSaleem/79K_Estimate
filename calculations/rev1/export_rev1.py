# Builds rev1.json: everything the Word and Excel builders need (single source of truth).
import json, math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rev1 as R
R0 = R.R0
M = R.M

def gross(k, v): return v*(1 + M[k][4])
def costof(mat): return sum(gross(k, v)*M[k][5] for k, v in mat.items())

# ---------------- steel schedule: member group x bar size (net kg)
STEEL_KEYS = ['ST2', 'ST3', 'ST4', 'ST6']
groups = {}
for i in R.ITEMS:
    s = {k: i['mat'].get(k, 0) for k in STEEL_KEYS}
    if sum(s.values()) <= 0: continue
    g = i['group'] or 'Other'
    gg = groups.setdefault(g, {k: 0.0 for k in STEEL_KEYS})
    for k in STEEL_KEYS: gg[k] += s[k]
GROUP_ORDER = ['Column footing', 'Plinth beam', 'Column', 'Slabs', 'Concealed beams', 'Lintels', 'Bed plates', 'Stairs', 'Chajjas',
               'Elevation RCC', 'Coping', 'Sunken slabs', 'Manhole covers', 'Septic tank', 'Water tank', 'Tank platform',
               'Solar plinths', 'Boundary walls', 'Other']
steel_rows = [(g, groups[g]) for g in GROUP_ORDER if g in groups]

# ---------------- stage purchase schedule (gross = net x (1 + wastage)), per stage and material
stage_buy = {}
for s, _ in R.STAGES:
    t = {}
    for i in R.ITEMS:
        if i['stage'] != s: continue
        for k, v in i['mat'].items():
            t[k] = t.get(k, 0) + gross(k, v)
    stage_buy[s] = t
# binding wire goes with the steel stages pro rata
for s in stage_buy:
    stw = sum(stage_buy[s].get(k, 0) for k in STEEL_KEYS)
    if stw > 0: stage_buy[s]['BWIRE'] = stw*R.BW_PER_KG

# ---------------- brick split for the thumb-rule check
def bricks_where(pred): return sum(i['mat'].get('BRK', 0) for i in R.ITEMS if pred(i))
br_house = bricks_where(lambda i: i['stage'] in ('S4', 'S5', 'S7', 'S8') and not i['loc'].startswith('Porch, lawn'))
br_ext = bricks_where(lambda i: i['loc'].startswith('Porch, lawn') or i['stage'] == 'S16')
br_sew = bricks_where(lambda i: i['stage'] in ('S11', 'S12'))
br_bnd = bricks_where(lambda i: i['stage'] == 'S15')
br_tank = bricks_where(lambda i: i['stage'] == 'S13')

# ---------------- Rev 0 reference values (procure quantities printed in Rev 0 report)
it0 = R.R0I
def r0q(k): return it0[k]['qty']
REV0_BUY = {'Cement (bags)': 1560, 'Bricks (nos)': 125000, 'Steel (kg)': 8080, 'Binding wire (kg)': 85, 'Crush (cft)': 4200,
            'Sand for concrete (cft)': 2250, 'Sand for mortar/plaster (cft)': 4900, 'Fill sand under floors (cft)': 600,
            'Earth filling (cft, total)': 6450, 'Bitumen (kg)': 320}

def S(k): return next((x for x in R.SUMMARY if x['key'] == k), None)
def buy(k): x = S(k); return x['buy'] if x else 0
steel_buy = sum(buy(k) for k in STEEL_KEYS)
it1 = {i['ref']: i for i in R.ITEMS}
def q1(ref): return it1[ref]['qty']
def code(ref): return it1[ref]['code']

REVLOG = [
 # (area, item, Rev 0, Rev 1, register, note)
 ('Foundations', 'Excavation of house trenches (cft)', r0q('A1'), q1('2.1'), 'C1, C2', 'sheet-05 widths 3\'-0" / 2\'-6"; PCC bottom 2\'-6" below NSL'),
 ('Foundations', 'PCC 1:4:8 3" under footings (cft)', r0q('A2'), q1('4.1'), 'C1, C3', 'narrower sheet-05 PCC'),
 ('Foundations', 'RCC strip footing 6" (cft) - S-02', r0q('A3'), 0, 'C1', 'removed; its 673 kg of #3 steel removed too'),
 ('Foundations', 'Foundation brickwork 1:6 below road (cft)', r0q('A4'), q1('4.2') + q1('4.3'), 'C1', 'steps 27" / 22½" / 18" + 13½" wall up to road level'),
 ('Foundations', 'Plinth brickwork above road (cft)', r0q('A5'), q1('4.4'), 'B4', 'now from road level to underside of beam at floor level'),
 ('Foundations', 'RCC plinth beam 9" x 9" (cft)', r0q('A6'), q1('5.1'), 'B4', 'moved from road level to floor level (sheet 05); steel per S-02'),
 ('Foundations', 'DPC 1½" 1:2:4 (cft)', r0q('A7'), q1('5.2'), 'B4, B5', 'now with waterproofing compound + 2 coats bitumen; top = FFL'),
 ('Foundations', 'Vertical DPC (sft)', r0q('A8'), q1('5.3'), 'B6', 'height 4\'-1½" (was 3\'-6"); bitumen at 0.2 kg/sft/coat (was 0.25)'),
 ('Foundations', 'Car-porch column (cft)', r0q('A9'), q1('8.1'), 'C5', 'height 16\'-6" with new levels'),
 ('Foundations', 'Edge / toe walls (cft of brickwork)', r0q('G9'), it1['4.8']['qty'] + it1['4.9']['qty'], 'C6', '6 edge walls 42\'-9" (D-D) replace 15 ft lawn toe wall'),
 ('Earthwork', 'Back-filling of house trenches (cft)', r0q('A12'), q1('6.1'), 'A3', 'from the sheet-05 profile'),
 ('Earthwork', 'Earth filling inside house (cft)', r0q('A11'), q1('6.2'), 'A3, A5', 'floor build-up now 9½"'),
 ('Earthwork', 'Earth filling under car porches (cft)', r0q('B3'), q1('6.3') + q1('6.4'), 'A5', 'both porches full area (451 sft, was 246)'),
 ('Earthwork', 'Earth to buy (cft)', 3250, R.EARTH_BUY, 'A3-A5, G4', 'porches, passages and ramps now filled'),
 ('Anti-termite', 'Termiticide concentrate (L)', 0, R.NET['TERM'], 'B1', 'new: trenches, plinth fill, perimeter'),
 ('Sub-floor', 'Sand fill 4" under floors (cft)', r0q('B1'), 0, 'B2', 'replaced by khangar + sand blinding + polythene'),
 ('Sub-floor', 'Khangar 4" (cft)', 0, q1('6.5'), 'B2', 'new capillary break'),
 ('Sub-floor', 'Sand blinding 1" (cft)', 0, q1('6.6'), 'B2', 'new'),
 ('Sub-floor', 'Polythene 0.2 mm (sft)', 0, q1('6.7'), 'B2, B3', 'new ("graphite sheet")'),
 ('Sub-floor', 'PCC 3" sub-floor, rooms + porches (cft)', r0q('B2'), q1('6.8'), 'A5, B2', 'porches full area'),
 ('Sub-floor', 'Upper-floor 3" PCC sub-base (cft)', r0q('B4'), q1('8.UF'), 'E3', 'less sunken bath areas'),
 ('Masonry', '9" walls GF+FF+mumty: cement (bags)', sum(r0q(k) for k in ('C-GF9', 'C-FF9', 'C-SF9'))*0 + sum(it0[k]['mat']['cement_bags'] for k in ('C-GF9', 'C-FF9', 'C-SF9')),
  sum(it1[k]['mat']['CEM'] for k in ('7.GF9', '7.FF9', '7.SF9')), 'D1', 'mortar 1:6 (was 1:5); brick volume unchanged'),
 ('RCC', 'Superstructure RCC (slabs, beams, lintels, stairs, chajjas, coping)', 1, 1, 'E1, E2', 'unchanged; dining-opening 8\'-0" lintel kept'),
 ('RCC', 'Sunken bath slabs: extra concrete (cft)', 0, q1('8.SK1'), 'E3', 'new: + steel, coating and brick-bat fill'),
 ('Roof', 'Roof waterproofing and tiles (sft of roof)', 0, R.A_ROOF, 'F3', 'was optional item O1 (not in total); now screed + membrane + gola + bhatta tiles'),
 ('Plaster', 'Ceiling plaster (sft)', r0q('F-C'), 0, 'F1', 'deleted (false ceilings)'),
 ('Plaster', 'External soffit plaster (sft)', 0, q1('10.S'), 'F1', 'new separate line'),
 ('Plaster', 'GF external plaster (sft)', r0q('F-EGF'), q1('10.EGF'), 'A3, F1', 'exposed plinth 2\'-0" (was 3\'-3")'),
 ('Plaster', 'Chicken mesh (rolls 3\' x 100\')', 0, R.NET['MESH'], 'D3', 'new: all junctions and chases'),
 ('Boundary', 'Boundary excavation (cft)', r0q('G1'), q1('15.1'), 'G3', 'PCC bottom 2\'-3" below NSL'),
 ('Boundary', 'Boundary brickwork below DPC (cft)', r0q('G3'), q1('15.3') + q1('15.4'), 'G3', 'measured from natural ground (adds wall below band)'),
 ('Boundary', 'Boundary wall above DPC (cft)', r0q('G5'), q1('15.7'), 'D1, G1, G2', 'mortar 1:6 (was 1:5); own back and right walls'),
 ('Boundary', 'Boundary DPC on plinth band (cft)', 0, q1('15.6'), 'G3', 'new'),
 ('Boundary', 'Boundary plaster (sft)', r0q('G8'), q1('15.10'), 'F1', 'both faces on all sides'),
 ('Septic tank', 'Septic tank internal size', '6\'-0" x 4\'-0" x 5\'-6", 2 chambers', '4\'-10" x 3\'-5" x 5\'-0", 3 chambers', 'H1', 'drawing size, read as internal'),
 ('Sewerage', 'Manhole covers', '9 RCC', '7 RCC + 2 cast iron', 'H2', 'heavy covers in car porches'),
 ('Sewerage', 'Manhole 9" brickwork (cft)', 346.5, R.MH_BRICK, 'H2', 'arithmetic corrected: 9 x centre-line 11 ft x 9" x 3\'-6" (Rev 0 left out the 9" thickness)'),
 ('Sewerage', 'A.C condensate drains ¾" (ft)', 0, 200, 'H3', 'new, with stainless mesh caps'),
 ('Water', 'RCC overhead tank 1,000 gal (cft RCC)', r0q('I1'), 0, 'I4', 'deleted; plastic tank (finishing) on RCC platform'),
 ('Water', 'Roof-tank platform (cft RCC)', 0, q1('13.11'), 'I4', 'new'),
 ('Water', 'Underground water tank (cft RCC)', 0, q1('13.3') + q1('13.4') + q1('13.5'), 'I1, I2', 'was optional O2; now ~515 gal, at back'),
 ('Water', 'PPR ¾" cold incl. society supply line (ft)', 369.7, 430, 'I3, I5', '+60 ft supply to UGT'),
 ('Water', 'PPR 1"-1¼" mains (ft)', 118, 131, 'I3', 'pump at back'),
 ('Electrical', '¾" conduit (ft)', 2900, R.CL['C34'], 'J2, J8', 'no TV / intercom / +10% UPS; data + CCTV added'),
 ('Electrical', '1" conduit (ft)', 1390, R.CL['C1'], 'J1, J5, J7', 'earth pits, pump, spare roof AC'),
 ('Electrical', '1¼" conduit (ft)', 0, R.CL['C114'], 'J4, J5', 'inverter, backup DBs, DC spare'),
 ('Electrical', '1½" conduit (ft)', 85, R.CL['C112'], 'J6', 'EV charger run added'),
 ('Electrical', 'DB enclosures (nos)', 3, 6, 'J5', '3 backup (essential-load) DBs added + EV box'),
 ('Electrical', 'Earth pits (nos)', 0, 3, 'J7', 'new'),
 ('Electrical', 'Solar mounting plinths (nos)', 0, R.N_PLINTH, 'J3', 'new, 23 panels x 650 W'),
 ('External', 'Passage paving base (sft)', 0, R.A_PASS, 'G4', 'was optional O3'),
 ('External', 'Ramps at both gates (sft)', 0, R.A_RAMP, 'G4', 'new'),
 ('Standards', 'Wastage cement / sand / steel / pipes', '5% / 10% / 5% / 10%', '3% / 8% / 4% / 7%', 'K2', 'crush and bricks stay 5%'),
 ('Standards', 'Binding wire (kg)', 85, buy('BWIRE'), 'E4', '10 kg per ton of steel'),
]

# ---------------- recommended additions (NOT in total), priced at Rev 1 rates incl. wastage
scr_save = (R.SC['terrace_2outlets']['vol'] - R.SC['terrace_4outlets']['vol']) + (R.SC['mumty_1outlet']['vol'] - R.SC['mumty_2outlets']['vol'])
c_save = costof(R.mort(scr_save, '1:4', 'SNDC'))
c_add = costof({'FUP3': 3, 'RWP3': 37})
REC = [
 ('Two more terrace outlets (front-right, rear-right) and one mumty-roof spout', round(c_add - c_save),
  'with the drawn outlets the slope screed reaches ~5⅜" and the build-up ~7¾" at the far corner (over the 6½" allowed); 4 terrace outlets keep it within 5¾" and save ~%d cft of screed' % scr_save),
 ('Three 13½" pillars in the new 37\'-3" back wall (about every 10 ft)', round(costof(R.bw(11.1, '1:4')) + costof(R.bw(3.0, '1:6')) + costof(R.pl(30, 0.75, '1:4'))),
  'a free-standing 9" wall 7\'-0" high and 37 ft long needs pillars for stability against wind and impact'),
 ('Roof thermal insulation: 1" XPS board under the bhatta tiles (~1,581 sft)', round(1581*95),
  'cuts summer heat gain on the top floor; needs the extra outlets above so the build-up still fits'),
 ('Second (double) mesh of #3 @ 6" in the underground tank walls', round(costof(R.st({3: 512}))),
  'better crack control for a water-retaining wall'),
 ('Enlarge septic tank to a practical 3-chamber size, 7\'-0" x 3\'-6" internal', 30000,
  'the drawing size gives chambers only ~1\'-0" long, too small to clean'),
 ('Vent / overflow pipe 1½" with insect mesh for the underground tank', 2000, 'lets air out while filling; prevents insects'),
 ('Pump plinth 2\'-0" x 1\'-6" x 6" RCC at the back', round(costof(R.conc(1.5, '1:2:4'))), 'keeps the pump off a wet floor'),
 ('ISP fibre / internet entry conduit 1" from front wall to router point (~60 ft)', round(costof({'C1': 60, 'BEND1': 6})),
  'lets the internet cable come in concealed'),
]

# ---------------- remaining assumptions
RA = [
 'The filled questionnaire was not attached to this session. The Final Decisions Register (which combines your answers) was used as the only record of your answers.',
 'Plinth beam: sheet 05 gives size only (9" x 9"). Steel 2 #4 top + 2 #4 bottom with #2 rings @ 10" and mix 1:2:4 are taken from the engineer\'s S-02 plinth beam.',
 'DPC is 9" wide on top of the plinth beam under ALL house walls, including 4½" walls (sheet 05 section C-C shows the 9" beam under 4½" walls).',
 'Finished level of side and rear passages taken as +1\'-0" (not drawn), sloping 1:60 to drains; paving finish allowance 3" (finishing estimate).',
 'Porch finish taken 1½" thick (as house floor), so porch sub-floor PCC top is +1\'-1½".',
 'Edge walls are founded like the boundary walls (PCC bottom 2\'-3" below NSL) and use the D-D section (steps 22½"/18"/13½", 9" wall, DPC at porch level).',
 'Edge walls identified from the levels: toe wall lawn/porch 9\'-3", toe wall across left passage 4\'-11", rear porch edges 3\'-1" and 5\'-0", gate thresholds 12\'-9" and 7\'-8¼" = 42\'-9".',
 'Ramps are built outside the main and side gates on the road verge, slope 1:6, 7\'-6" long with 1\'-0" flares (gate thresholds stay at porch level +1\'-3").',
 'Front car porch: 20\'-0" x 16\'-7½" (sheet 04, confirmed by measurement) less the entrance-lobby notch = %d sft. The 8\'-0" "drive way" on the plans lies inside this zone and gets the porch sub-floor.' % R.A_FP,
 'Rear car porch 16\'-9½" x 8\'-6" (sheets 06, 17, 21).',
 'Right-side boundary walls: front stretch 9\'-0" long x 6\'-0" high, rear-passage stretch 5\'-5" x 7\'-0" high. The open patio stretch (4\'-9") stays open (D2: no privacy walls).',
 'All boundary-wall footings are eccentric (projections inside the plot) because every boundary wall stands on a property line (C4).',
 'Septic tank: the 4\'-10" x 3\'-5" rectangle on sheet 17 is read as the INTERNAL size. With two 4½" baffles, three chambers come out about 2\'-0", 1\'-0" and 1\'-0" long - too small to clean. Drawing size used as instructed; enlargement listed in Recommended additions.',
 'Septic tank liquid depth 4\'-0" + freeboard 1\'-0" (internal depth 5\'-0"); capacity ~410 gal liquid.',
 'Underground tank: internal 4\'-10" x 3\'-5" (same as septic tank), 5\'-0" water + 6" freeboard = about 515 imperial gallons; in the rear car porch, top 7" above porch level.',
 'Underground tank distance: no spot at the back is 10 ft from every manhole, because three manholes run along the rear. The chosen spot (rear car porch, toward the house) is about 8½ ft (centre to centre) from the two nearest rear manholes - see points to confirm.',
 'Plastic roof tank recommended 500 gallons. Platform 5\'-0" x 5\'-0" x 4" RCC on two 9" brick walls 1\'-6" high, set directly over the mumty walls at the sheet-24 position.',
 'Solar: the drawings have no north arrow. The layout assumes the front (road side) faces south; if not, the rows must be re-placed (the plinth count stays about the same).',
 'Solar: 650 W panels 2,384 x 1,303 mm, 2-high landscape tables tilted 15°, low edge about 1\'-6" above the roof tiles; row pitch 11\'-6" (no row-to-row shading at noon on 21 December, sun about 35° high); front row set 2\'-3" back from the 3\'-0" front parapet so the parapet shadow stays off the panels; walkways 1\'-6" along the side parapets.',
 'Anti-termite: bifenthrin 10% EC diluted 1:200 (0.05%), 5 L of emulsion per m2 on trench surfaces and plinth fill, 2.25 L per running metre along the perimeter (IS 6313-2 rates). If imidacloprid 30.5% SC is used, dilute 1:400 (about 5.6 L concentrate).',
 'Roof build-up: screed 1:4 cement-sand (min ¾"), 4 mm membrane, ¾" mortar bed, 1½" bhatta tiles; membrane laps +10%; LPG 0.4 kg per m2.',
 'Upper-floor 3" PCC sub-base kept from Rev 0 (the Register does not mention it; it covers the 4" concealed-beam upstands and conduits).',
 'Sunken slabs: 3 first-floor baths + mumty bath (laundry not sunk); filling 9" deep (6" drop + 3" floor base) with brick-bat coba.',
 'Chicken-mesh lengths for chases are allowances (electrical drops per point, 60% of water pipe length, 50% of gas pipe, 80% of A.C drains).',
 'Electrical positions proposed: Wi-Fi access points - GF front lounge/drawing and GF rear lobby, FF lounge and FF rear lobby, mumty stair lobby (also covers the terrace); CCTV - main gate (outside), front porch, side gate / rear porch, back gali (from first-floor rear wall), rear passage, left passage front, left passage rear; NVR/router point in the GF lobby near the stair.',
 'Inverter + sodium-ion battery position: mumty laundry (roofed, out of sun, ventilated on the terrace side) with a 6" RCC plinth for the battery cabinet and wall space for the inverter.',
 'Earth pits: copper-bonded rod 5/8" x 10 ft in an augered bore with 2 bags of earthing compound each; chamber with cover.',
 'Wall, slab, lintel and opening geometry is re-used from Rev 0 (measured from S-01 / S-04 to S-08). The architect\'s ground-floor master bedroom is 3" longer (14\'-3" vs 14\'-0"); effect on quantities is under 0.1%.',
 'Society water supply enters at the front; 60 ft of ¾" PPR runs to the underground tank at the back; pump rising main 53 ft.',
 'Lawn filling to +1\'-2" is not included (A5); it belongs to landscaping.',
 'Steps (entrance, porches, rear and side doors) kept as the Rev 0 allowance: 40 cft brickwork + 20 cft PCC.',
 'Many rates are estimates (marked in the Rates sheet). Cement, steel, bricks, sand, crush and PPR rates come from 2026 published reports (sources listed).',
]

POINTS = [
 'Plinth beam steel and mix: sheet 05 shows size only. Confirm 2 #4 top + 2 #4 bottom, #2 @ 10", 1:2:4 (from S-02) for the beam at floor level.',
 'Eccentric plain brick footings on the right property line (house wall and powder-room wall) and under all boundary walls: confirm they are acceptable without the RCC footing of S-02, and whether the plinth beam should be tied to them.',
 'Car-porch corner column sits on the property line: its 3\' x 3\' footing must be placed eccentric (edge on the line). Confirm a tie to the plinth beam.',
 'Roof drainage: the drawn outlets make the slope screed too thick at the far corners (build-up ~7¾" vs 6½"). Approve two more terrace outlets and one mumty spout.',
 'Underground water tank is about 8½ ft from the two nearest rear manholes (less than 10 ft). Approve, or shift the rear-middle manhole about 2 ft to the right.',
 'Septic tank at the drawing size is too small for three practical chambers. Confirm the drawing size or the enlarged 7\'-0" x 3\'-6" tank.',
 'Sunken bath slabs (6"): ask the engineer to detail the bars at the drop (S-06 / S-07 show no drop).',
 'Upper-floor 3" PCC sub-base adds about 37 kg/m2. Confirm, or specify a lighter fill.',
 'Solar: confirm the roof slab can take the panels, frames and wind uplift on 34 plinths; place 4 #3 starter bars at each plinth position before the slab is cast. Confirm true north on site.',
 'Roof tank platform: confirm the two support walls sit over mumty walls at the sheet-24 tank position.',
 'Car-porch size: sheet 04 shows 16\'-7½" deep, other sheets 17\'-9". Confirm (estimate uses 16\'-7½", which matches the plot measurement).',
 'Ground-floor master bedroom 14\'-3" (architect) vs 14\'-0" (structural layout): ask the engineer to update S-01 so setting-out matches.',
 'Second stair flight passes over the rear car porch with about 7 ft headroom: check car height.',
]

EXCL = [
 ('Excluded by K1', 'Labour, shuttering and formwork, scaffolding, tools, curing water and construction electricity.'),
 ('Finishing estimate', 'Floor finishes (tiles / marble in house, tuff tiles on porches, passages, driveway strip and ramps); skirting; wall and ceiling finishes; false ceilings; paint.'),
 ('Finishing estimate', 'Doors, windows, glazing, grills, railings (incl. glass railing on the front balcony), main and side steel gates.'),
 ('Finishing estimate', 'Plastic roof water tank (500 gal recommended), pump, float switch, geyser, sanitary fixtures and taps, kitchen work.'),
 ('Finishing estimate', 'Electrical wires and cables (incl. Cat6, PV and earth cables), switches, sockets, breakers, DB internals, inverter, sodium-ion batteries, solar panels and mounting frames, EV charger, CCTV cameras, NVR, Wi-Fi access points.'),
 ('Finishing estimate', 'Lawn soil and landscaping (lawn filling to +1\'-2"), planters, external lights.'),
 ('Not included', 'Recommended additions in Section 9 (they are not in the total).'),
]

# ---------------- solar summary
SOLAR = dict(panels=23, w=650, kwp=23*0.65, module='2,384 x 1,303 mm (7\'-9¾" x 4\'-3¼") bifacial', tilt=15,
             rows=[('Terrace row 1 (front)', 8, '4 panels across x 2 high (landscape)', 'x 1\'-6" to 33\'-0" from left parapet; 2\'-3" behind the front parapet', 10),
                   ('Terrace row 2 (beside open shaft)', 6, '3 across x 2 high', 'clear of the shaft by 1\'-6"', 8),
                   ('Terrace row 3 (rear)', 6, '3 across x 2 high', '2\'-1½" walkway behind, in front of mumty', 8),
                   ('Mumty roof - room block', 2, '2 panels portrait, 1 high', 'west of the water-tank platform', 4),
                   ('Mumty roof - stair block', 1, '1 panel landscape', '', 4)],
             footprint=749.5, terrace_zone=980, terrace_area=R.T_A, mumty_area=R.M_A, plinths=R.N_PLINTH,
             plinth='15" x 15" x 12" high, 1:2:4, 4 #3 starter bars + 2 #2 links, 2 cast-in M12 x 250 mm galvanised J-bolts',
             pitch='11\'-6"', walkways='2\'-3" behind the front parapet; 1\'-6" along the side parapets; 3\'-3" clear between rows; 2\'-1½" behind the rear row')

# ---------------- thumb rules
cov = R.COVERED
TH = dict(cement=buy('CEM')/cov, steel=steel_buy/cov, bricks_all=buy('BRK')/cov,
          bricks_house=br_house*(1.05)/cov, br_house=br_house, br_ext=br_ext, br_sew=br_sew, br_bnd=br_bnd, br_tank=br_tank,
          cost_sft=R.COST_TOTAL/cov)

OUT = dict(
    stages=R.STAGES, items=R.ITEMS, summary=R.SUMMARY, rates={k: list(v) for k, v in M.items()},
    cost_lines=R.COST_LINES, cost_total=R.COST_TOTAL, covered=cov, stage_cost=R.STAGE_COST, bw_cost=R.BW_COST,
    steel_rows=steel_rows, steel_keys=STEEL_KEYS, stage_buy=stage_buy, levels=R.LEVELS, dpc_clear=R.DPC_CLEAR,
    revlog=REVLOG, rec=REC, ra=RA, points=POINTS, excl=EXCL, solar=SOLAR, thumb=TH, rev0_buy=REV0_BUY,
    earth=dict(exc=R.EXC, back=R.BACK, surplus_loose=R.SURPLUS_LOOSE, efill=R.EFILL, buy=R.EARTH_BUY),
    screed=R.SC, roof=dict(A_ROOF=R.A_ROOF, T=R.T_A, M=R.M_A, B=R.B_A, PL_LEN=R.PL_LEN, A_TILE=R.A_TILE),
    steel_net=R.STEEL_NET, steel_gross=R.STEEL_GROSS, steel_buy=steel_buy,
    misc=dict(A_FP=R.A_FP, A_RP=R.A_RP, A_SUB=R.A_SUB, A_PASS=R.A_PASS, A_RAMP=R.A_RAMP, L_EDGE=R.L_EDGE, EDGE=R.EDGE,
              A_SUNK=R.A_SUNK, P_SUNK=R.P_SUNK, mesh12=R.mesh12, mesh9=R.mesh9, BWALL=R.BWALL, Lf=R.Lf, Lpan=R.Lpan,
              BATHS=R.BATHS, colH=R.colH, A_SOFF=R.A_SOFF))
json.dump(OUT, open(os.path.join(HERE, 'rev1.json'), 'w'), indent=1, default=float)
print('items', len(R.ITEMS), 'total', round(R.COST_TOTAL), 'per sft', round(R.COST_TOTAL/cov), 'thumb', {k: round(v, 3) for k, v in TH.items()})
