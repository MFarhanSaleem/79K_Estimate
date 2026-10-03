# Finishing estimate STEP B for House 79/K: priced MATERIAL estimate (no labour), Word report only.
# Quantities come from the Step A take-off (stepA.py, run in-process) and the owner's answers to the
# 40-question finishing questionnaire. Rates are Faisalabad / Lahore retail, October 2026; every rate
# carries its source and date, or is marked "estimated" where no published 2026 price was found.
# usage: python3 stepB.py <out_blocks.json>
import json, math, os, sys, runpy, tempfile
from collections import OrderedDict, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'blocks_stepB.json')
_argv = sys.argv
sys.argv = ['stepA.py', os.path.join(tempfile.gettempdir(), 'blocks_stepA_via_stepB.json')]
A = runpy.run_path(os.path.join(HERE, 'stepA.py'), run_name='stepA')
sys.argv = _argv

R, DOORS, WROWS, EP, cnt = A['R'], A['DOORS'], A['WROWS'], A['EP'], A['cnt']
R0, G, M = A['R0'], A['G'], A['M']
ftin = A['ftin']
LS = ' '                     # line break inside a table cell
COVERED = 4104.0                  # GF 1,898 + FF 1,844 + mumty 362 sft
GREY_TOTAL = 9189795              # grey-structure material estimate Rev 1
FLOORS = ('GF', 'FF', '2F')
FLN = {'GF': 'Ground floor', 'FF': 'First floor', '2F': 'Second floor (mumty)'}

def f0(x): return '{:,.0f}'.format(x)
def f1(x): return '{:,.1f}'.format(x)
def f2(x): return '{:,.2f}'.format(x)
def fq(x):
    if abs(x - round(x)) < 0.005: return f0(x)
    return f2(x) if abs(x) < 10 else f1(x)
def pct(w): return ('%g%%' % round(w * 100, 1)) if w else '-'
def rn(k): return R[k]['name'] if k in R else k

# ============================================================== stages in site order
STAGES = OrderedDict([
 ('S1', ('Electrical first fix: wires, DBs and protection',
         'Wires pulled into the grey conduits, DBs fitted and AC copper pipes run - before false ceilings and putty.')),
 ('S2', ('Solar PV and battery storage',
         'Frames and panels on the grey plinths once the roof is clear; inverter and battery wired when the DBs are in; net-metering applied for at the end.')),
 ('S3', ('False ceilings',
         'GI frame and gypsum boards after wiring and AC pipes, before wall putty and floor tiles.')),
 ('S4', ('Floor and wall tiles: rooms, lobbies, kitchens, laundry',
         'After the ceilings and the first putty coat; skirting goes in with the floor tiles.')),
 ('S5', ('Marble and granite: stairs, sills, thresholds, external steps',
         'Stairs and thresholds with the floor tiles; window sills before the aluminium frames.')),
 ('S6', ('Bathrooms',
         'Waterproofing and concealed valves first, then tiles; sanitary ware, mirrors and screens after the final paint coats.')),
 ('S7', ('Kitchens and wardrobes',
         'Cabinets and counters after the floor tiles; hobs, hoods and sinks last.')),
 ('S8', ('Doors',
         'Diyar chowkats are fixed before plaster, so buy them first; shutters, hardware and polish after the floor tiles.')),
 ('S9', ('Windows, glazing, fly-nets and grills',
         'Aluminium frames and glass after the first paint coats; grills before the final coats.')),
 ('S10', ('Paint and colour scheme',
          'Putty and primer before tiling; final coats after doors, windows and kitchens; exterior and boundary walls last.')),
 ('S11', ('Electrical second fix: switches, lights, fans, ACs, Wi-Fi, CCTV, EV charger',
          'After the final paint coats.')),
 ('S12', ('External works: paving, gates, railings, roof tank and pump',
          'Last, so heavy deliveries do not damage the paving (tank and pump can be bought early for site water).')),
])
SNUM = {s: i + 1 for i, s in enumerate(STAGES)}      # stage number 1-12
SECNO = {s: i + 3 for i, s in enumerate(STAGES)}     # Word section number 3-14

# ============================================================== rates
# rate = Rs per base unit; size = base units per buying unit; show='buy' prints the price per buying unit
RATES = OrderedDict()
def rate(k, name, unit, r, src='estimated', size=1, buy=None, show='base'):
    assert k not in RATES, k
    RATES[k] = dict(name=name, unit=unit, rate=float(r), src=src, size=size, buy=buy or unit, show=show)

PCL = 'Pakistan Cables retail list, 01-09-2026'
PCLD = 'Pakistan Cables list 01-09-2026 (per m, +10% cut length)'
COL = OrderedDict([('R', 'red'), ('Y', 'yellow'), ('B', 'blue'), ('K', 'black'), ('G', 'green')])
for sz, imp, price in [(1.5, '3/.029', 10850), (2.5, '7/.029', 17690), (4.0, '7/.036', 27575)]:
    for c, cn in COL.items():
        rate('W%g%s' % (sz, c), 'Copper wire %g mm2 (%s), single core, %s' % (sz, imp, cn), 'm', price / 90.0, PCL,
             size=90, buy='coil (90 m)', show='buy')
for sz, imp, price in [(6.0, '7/.044', 40970), (10.0, '10 mm2', 70820)]:
    for c, cn in COL.items():
        rate('W%g%s' % (sz, c), 'Copper wire %g mm2 (%s), single core, %s - cut length' % (sz, imp, cn), 'm',
             round(price / 90.0 * 1.10), PCLD)
rate('W16G', 'Earth wire 16 mm2 copper, green/yellow, cut length', 'm', round(16 * 70820 / 900.0 * 1.10), 'derived from Pakistan Cables list 01-09-2026')
rate('CAB416', 'Cable 4-core 16 mm2 copper, PVC/SWA armoured (meter to main DB)', 'm', 5800, 'estimated (Pakistan Cables per-mm2 price + armour)')
rate('CAT6', 'Cat6 UTP data cable (Pollo PLN-UTP6-305P or equal)', 'm', 33550 / 305.0, 'w11stop.com, 21-07-2026', size=305, buy='box (305 m)', show='buy')
rate('RJ45', 'RJ45 Cat6 connectors', 'nos', 28, size=100, buy='pack (100)', show='buy')
rate('KEYST', 'Cat6 keystone jack with 1-gang data plate', 'nos', 650)
rate('DB36', 'Distribution board 3-phase TPN 12-way (36 modules), metal, flush, with busbars and N/E bars', 'nos', 15500)
rate('DB24', 'Distribution board 3-phase TPN 8-way (24 modules), metal, flush', 'nos', 11500)
rate('DB8S', 'Distribution board single-phase SPN 8-way, metal, flush', 'nos', 3800)
rate('DBCR', 'LESS: empty DB enclosures already priced in grey Rev 1 (item 14.D: 12/8/8/6/4/4-way) - replaced by the boards above', 'set', -17700, 'grey estimate Rev 1 rates')
rate('MCCB63', 'MCCB 4-pole 63 A, 25 kA (Chint NXM or equal) - main incomer', 'nos', 14500)
rate('MCB4P40', 'MCB 4-pole 40 A C-curve (Chint NXB)', 'nos', 3400, 'estimated (Chint TP Rs 2,500-2,890, w11stop Jul 2026)')
rate('MCB4P32', 'MCB 4-pole 32 A C-curve (Chint NXB)', 'nos', 3300, 'estimated (Chint TP Rs 2,500-2,890, w11stop Jul 2026)')
rate('MCBDP', 'MCB double-pole 20-32 A (Chint)', 'nos', 1720, 'w11stop.com, Jul 2026')
rate('MCBSP', 'MCB single-pole 6-20 A, B/C-curve (Chint NXB)', 'nos', 1090, 'w11stop.com, Jul 2026')
rate('RCCB4', 'RCCB 4-pole 40 A, 30 mA (Chint NXBLE)', 'nos', 6200, 'estimated (Chint 4P 25 A Rs 4,950, powerhouseexpress 2026)')
rate('RCCB2', 'RCCB 2-pole 40 A, 30 mA (Chint)', 'nos', 3800)
rate('RCBOA', 'RCBO 40 A Type A, 30 mA (EV charger circuit)', 'nos', 7500)
rate('SPD4', 'Surge protector Type 2, 4-pole (3P+N) 40 kA, 385 V AC (Chint NU6-II)', 'nos', 9500, 'estimated within Chint SPD list range Rs 3,500-11,000')
rate('CHO', 'Changeover switch 4-pole 63 A, manual I-0-II (inverter bypass)', 'nos', 9000)
rate('ISO40', 'Isolator 40 A double-pole for the EV charger (in the grey EV box)', 'nos', 3500)
rate('DBACC', 'DB sundries: comb busbars, links, DIN rail, blanks, labels, lugs, glands, ferrules, ties', 'set', 18000)
rate('ACK15', 'AC pipe set 1.5 t: concealed copper pair with insulation, drain hose, interconnect cable, outdoor bracket (about 15 ft beyond the supplied kit)', 'set', 24000)
rate('ACK20', 'AC pipe set 2 t: as above, larger copper pair', 'set', 28000)
# ---- solar
rate('PV650', 'Solar panel 650 W N-type bifacial, tier-1 (Longi Hi-MO X10 / Jinko / JA) at Rs 44/W', 'nos', 650 * 44, 'icons.com.pk solar prices, 01-04-2026 (Longi Hi-MO X10 Rs 44-49.25/W)')
rate('INV12', 'Hybrid inverter 12 kW 3-phase, 48 V battery, 2 MPPT (Deye SUN-12K-SG04LP3 or equal)', 'nos', 380000, 'paksolarpanelprices.com, 2026 (Rs 320,000-420,000)')
rate('NAB5', 'Sodium-ion battery module 48 V class, about 5.3 kWh, BMS with CAN/RS485 (Rs 55,000/kWh)', 'nos', 291500, 'estimated (no retail listing; LFP 10 kWh Rs 447,200, w11stop 21-07-2026)')
rate('BRACK', 'Battery rack/cabinet for 3 modules, parallel busbars and communication cables', 'set', 25000)
rate('BDC', 'Battery DC breaker 250 A + 2 x 70 mm2 flexible cables with lugs', 'set', 18000)
rate('MNT', 'Mounting frame per panel, galvanised steel, 15 deg tilt (GI frame)', 'nos', 8500, 'w11stop.com, Jul 2026 (GI mounting frame)')
rate('PLB', 'Base plate, nuts and washers per plinth (on the grey cast-in J-bolts)', 'nos', 1200)
rate('PVR', 'DC solar cable 6 mm2, red', 'm', 29500 / 90.0, 'w11stop.com, 2026 (GM DC 6 mm2, 90 m coil Rs 29,500)', size=90, buy='coil (90 m)', show='buy')
rate('PVK', 'DC solar cable 6 mm2, black', 'm', 29500 / 90.0, 'w11stop.com, 2026 (GM DC 6 mm2, 90 m coil Rs 29,500)', size=90, buy='coil (90 m)', show='buy')
rate('MC4', 'MC4 connector pair (IP67)', 'pair', 450)
rate('DCBOX', 'PV DC combiner box: 1,000 V DC isolator, Type 2 DC surge protector, gPV fuses (2 strings)', 'nos', 22000, 'estimated (Chint DC SPD Rs 3,500-11,000)')
rate('ACBOX', 'Inverter AC box: grid and load 4-pole 40 A MCBs, AC surge protector', 'nos', 16000)
rate('NETM', 'FESCO 3-phase bi-directional (net-billing) meter', 'nos', 25000, 'FESCO / NEPRA Prosumer Regulations 2026 (meter Rs 10,000-25,000)')
rate('NETF', 'FESCO net-billing application, meter testing and connection allowance', 'set', 15000)
# ---- false ceiling
rate('GB125', 'Gypsum board 12.5 mm standard, 4 ft x 8 ft (Gyproc / Knauf)', 'sheet', 2450)
rate('GBMR', 'Gypsum board 12.5 mm moisture-resistant (green), 4 ft x 8 ft', 'sheet', 3450)
rate('GCS', 'GI ceiling section (furring channel), 3.66 m', 'm', 520 / 3.66, size=3.66, buy='length (3.66 m)', show='buy')
rate('GIC', 'GI intermediate (main) channel, 3.66 m', 'm', 650 / 3.66, size=3.66, buy='length (3.66 m)', show='buy')
rate('GPC', 'GI perimeter channel, 3.66 m', 'm', 390 / 3.66, size=3.66, buy='length (3.66 m)', show='buy')
rate('GHG', 'Hanger set: GI angle drop with soffit cleat', 'nos', 140)
rate('GANC', 'Anchor fasteners 6 x 40 mm', 'nos', 16, size=100, buy='box (100)', show='buy')
rate('GCLP', 'Connecting clips', 'nos', 15, size=100, buy='bag (100)', show='buy')
rate('GSCR', 'Drywall screws 25 mm', 'nos', 1.9, size=1000, buy='box (1,000)', show='buy')
rate('GWSC', 'Wafer-head frame screws', 'nos', 1.5, size=1000, buy='box (1,000)', show='buy')
rate('GJC', 'Gypsum jointing compound', 'kg', 3600 / 25.0, size=25, buy='bag (25 kg)', show='buy')
rate('GTAPE', 'Paper joint tape', 'm', 6, size=75, buy='roll (75 m)', show='buy')
rate('GBEAD', 'Corner / edge bead 3 m (cove edges)', 'nos', 250)
rate('GAP', 'Access panel 600 x 600 mm with frame', 'nos', 3500)
# ---- tiles and setting materials
TILE_SRC = 'estimated (market Rs 140-800/sft, Aug-Sep 2026)'
rate('T24P', 'Porcelain tile 2 ft x 4 ft (600 x 1200), polished glazed, light marble look, grade A, Chinese import - 2 pcs = 15.5 sft per box', 'sft', 320, TILE_SRC, size=15.5, buy='box')
rate('T24M', 'Porcelain tile 2 ft x 4 ft (600 x 1200), matt finish, same series (kitchens) - 15.5 sft per box', 'sft', 320, TILE_SRC, size=15.5, buy='box')
rate('T60M', 'Porcelain tile 600 x 600, matt anti-slip (R10) - 4 pcs = 15.5 sft per box', 'sft', 260, TILE_SRC, size=15.5, buy='box')
rate('T36W', 'Glazed porcelain wall tile 300 x 600, plain - 8 pcs = 15.5 sft per box', 'sft', 230, TILE_SRC, size=15.5, buy='box')
rate('T36F', 'Glazed porcelain wall tile 300 x 600, feature/decor design - 15.5 sft per box', 'sft', 280, TILE_SRC, size=15.5, buy='box')
rate('T36K', 'Glazed porcelain wall tile 300 x 600, kitchen backsplash design - 15.5 sft per box', 'sft', 250, TILE_SRC, size=15.5, buy='box')
rate('ADH', 'Tile adhesive, polymer-modified cement C2TE ("tile bond")', 'kg', 1450 / 20.0, size=20, buy='bag (20 kg)', show='buy')
rate('GRT', 'Tile grout, polymer cement, colour matched ("joint filler")', 'kg', 450)
rate('CLIP', 'Tile levelling clips (large-format floors)', 'nos', 12, size=100, buy='bag (100)', show='buy')
rate('WEDGE', 'Tile levelling wedges (reusable)', 'nos', 15, size=100, buy='bag (100)', show='buy')
rate('SPC', 'Tile spacers 2 mm (walls)', 'nos', 1.5, size=100, buy='bag (100)', show='buy')
rate('TRIM', 'Aluminium tile edge trim 10 mm, 2.5 m length', 'nos', 650)
rate('CEM', 'Cement OPC 50 kg bag (Lucky / Bestway / Maple Leaf)', 'bag', 1560, 'grey estimate Rev 1 (ARY News 15-08-2026 and brand list Sep 2026)')
rate('SNDM', 'Ravi sand ("ret") for bedding mortar', 'cft', 40, 'grey estimate Rev 1 (estimated)')
rate('SNDC', 'Chenab sand (paver bedding and joints)', 'cft', 65, 'grey estimate Rev 1 (toolsfluent.com 2026)')
rate('WPRF', 'Cementitious 2-component waterproofing, 25 kg set (Sika 107 / Fosroc Brushbond class)', 'kg', 11500 / 25.0, size=25, buy='set (25 kg)', show='buy')
rate('WPTP', 'Waterproofing reinforcing tape for corners and drains, 10 m roll', 'roll', 1800)
rate('FTRAP', 'SS 304 floor-trap grating with anti-odour insert, 5 in x 5 in (trap bodies are in grey 11.F)', 'nos', 1800)
# ---- stone
rate('GRN20', 'Granite 20 mm polished (Tropical / Black Galaxy class)', 'sft', 650, 'estimated (zameen.com: Jet Black ~Rs 400, Snow White ~Rs 570/sft)')
rate('ZW20', 'Ziarat White marble 20 mm, stair grade', 'sft', 500, 'icons.com.pk marble prices, 10-09-2026 (Rs 480-520/sft)')
rate('WCEM', 'White cement for stone joints, 40 kg bag', 'bag', 3600)
rate('SEAL', 'Stone sealer (granite / marble), 1 litre', 'litre', 3500)
# ---- bathrooms
rate('WC1P', 'WC one-piece, floor-mounted, with soft-close seat (Porta / Master)', 'nos', 63000, 'Daraz.pk listing, 2026 (Porta one-piece)')
rate('MSH', 'Muslim shower (health faucet) with hose, holder and angle valve', 'set', 3800)
rate('AVLV', 'Angle valve 1/2 in, chrome-plated brass', 'nos', 1250)
rate('FLEX', 'Flexible connector 1/2 in x 18 in', 'nos', 650)
rate('BSNV', 'Counter-top (vessel) wash basin, ceramic (Porta / Master)', 'nos', 12500)
rate('BSNW', 'Wall-hung wash basin with half pedestal (powder room)', 'nos', 9500)
rate('BMIXT', 'Basin mixer, single lever, tall (for counter-top basin) - Sonex / Faisal / Master', 'nos', 13500)
rate('BMIX', 'Basin mixer, single lever, standard (powder room)', 'nos', 9500)
rate('BWST', 'Basin pop-up waste with chrome bottle trap', 'set', 3500)
rate('SHMX', 'Concealed 2-way diverter mixer, body + trim (Sonex / Faisal / Master)', 'set', 17500, 'OLX.com.pk listings, 2026 (Rs 15,000-20,000)')
rate('RAIN', 'Rain shower 8 in with wall arm', 'set', 6500)
rate('HSH', 'Hand shower with hose and holder', 'set', 3500)
rate('GLS8', 'Toughened glass 8 mm, clear, cut and edge-polished (shower screens)', 'sft', 650)
rate('GLSH', 'Shower-screen fixings: SS U-channel, wall profile, support bar', 'set', 7500)
rate('HMR18', 'HDHMR / moisture-resistant board 18 mm, pre-laminated, 8 ft x 4 ft', 'sheet', 9500)
rate('HMR6', 'HDHMR / moisture-resistant board 6 mm (back panels), 8 ft x 4 ft', 'sheet', 3800)
rate('ACRY', 'Acrylic-faced 18 mm shutter board, high gloss, 8 ft x 4 ft', 'sheet', 18500)
rate('HPL', 'Decorative HPL laminate 1 mm, 8 ft x 4 ft', 'sheet', 4500)
rate('LINER', 'Liner laminate 0.8 mm (inside face of shutters), 8 ft x 4 ft', 'sheet', 1600)
rate('HETH', 'Hettich soft-close concealed hinge', 'nos', 850)
rate('DRW', 'Hettich soft-close telescopic drawer runners, pair', 'pair', 4800)
rate('BSKT', 'Pull-out SS basket (cutlery / plate / bottle)', 'nos', 6500)
rate('HNDL', 'Cabinet handle (aluminium profile)', 'nos', 600)
rate('WHND', 'Wardrobe long profile handle', 'nos', 900)
rate('WHNS', 'Loft shutter handle', 'nos', 350)
rate('WROD', 'Wardrobe hanging rod (SS oval) with supports', 'nos', 1200)
rate('WLOCK', 'Cupboard lock', 'nos', 600)
rate('EDGE', 'PVC edge band 22 mm, 0.8-2 mm', 'm', 2500 / 50.0, size=50, buy='roll (50 m)', show='buy')
rate('EDGA', 'Acrylic edge band 2 mm (to match shutters)', 'm', 4500 / 50.0, size=50, buy='roll (50 m)', show='buy')
rate('LEG', 'Adjustable cabinet leg', 'nos', 120)
rate('HANG', 'Wall-cabinet hanger, pair', 'pair', 450)
rate('KSKT', 'Aluminium kitchen plinth (skirting) 4 in', 'rft', 350)
rate('FIX', 'Fixings, confirmat screws, glue and silicone (per kitchen / wardrobe / vanity group)', 'set', 3000)
rate('VBRK', 'Vanity wall-hanging brackets and fixings', 'set', 1500)
rate('ACCS', 'Bath accessory set, SS 304, 6 pieces (towel rail, ring, 2 robe hooks, paper holder, soap shelf)', 'set', 25000, 'ideal.house price guide, Jan 2026 (mid sets Rs 25,000-35,000)')
rate('ACCP', 'Powder-room accessory set, SS 304, 3 pieces', 'set', 12000)
rate('MIRL', 'LED mirror 900 x 750 mm, touch switch and demister', 'nos', 16500, 'estimated (600 mm LED mirror Rs 10,125, Daraz.pk 2026)')
rate('MIRS', 'LED mirror 600 mm round (powder room)', 'nos', 10125, 'Daraz.pk listing, 2026')
rate('GEY35', 'Geyser hybrid gas/electric 35 gallon (Nasgas DEG-35 Super Deluxe)', 'nos', 48000, 'Nasgas listing, 05-08-2026')
rate('GEY15', 'Geyser hybrid gas/electric 15 gallon (Nasgas / Canon)', 'nos', 34000)
rate('GEYF', 'Geyser fittings: safety and pressure-relief valves, gas cock, flexible connectors, unions', 'set', 5500)
# ---- kitchen appliances
rate('SINK2', 'Stainless-steel double-bowl sink with drain board', 'nos', 19900, 'OLX.com.pk listing, 2026')
rate('SMIX', 'Sink mixer, neck type (Sonex)', 'nos', 19500, 'OLX.com.pk listing, 2026')
rate('SWST', 'Double-bowl sink waste kit with traps', 'set', 3500)
rate('HOB5', 'Built-in gas hob 5 burners (Nasgas DG-GN5 555)', 'nos', 26250, 'Nasgas listing, 2026')
rate('HOODI', 'Island chimney hood (local make: Nasgas / Canon / Signature)', 'nos', 52000)
rate('HOODW', 'Wall chimney hood (Nasgas)', 'nos', 30000, 'Nasgas listing, 05-08-2026 (Rs 27,300-35,000)')
rate('DUCT', 'Hood duct 6 in aluminium flexible with wall cap', 'set', 3500)
# ---- doors
rate('DIYAR', 'Diyar (deodar) wood, seasoned ("lakri")', 'cft', 9500, 'Faisalabad/Lahore timber rates 2026 (Rs 8,500-10,000/cft)', size=0.5, buy='cft')
rate('PLY25', 'Commercial plyboard 25 mm (door core strips), 8 ft x 4 ft', 'sheet', 9800)
rate('PLY6', 'Commercial ply 6 mm (door skins), 8 ft x 4 ft', 'sheet', 3000)
rate('VEN', 'Decorative veneer (Diyar / ash / teak), 0.5 mm', 'sft', 150)
rate('PU', 'PU polish materials: sealer, 2 PU top coats, thinner, filler, sandpaper (per sft polished)', 'sft', 75)
rate('DGLUE', 'Door glue, nails, wood filler (per door)', 'set', 1200)
rate('WPCD', 'WPC door with WPC frame, factory finished, 2 ft 6 in x 8 ft class', 'set', 28000)
rate('STD', 'Insulated steel security door with frame, powder coated, lock-prepared, up to 3 ft 6 in x 8 ft', 'nos', 68000)
rate('LKMAIN', 'Yale / Dorma heavy mortise lock, lever handle set and euro cylinder (main door)', 'set', 24000)
rate('LKEXT', 'Yale / Dorma mortise lock, lever handle set and cylinder (external doors)', 'set', 16500)
rate('CLOSER', 'Door closer (Dorma TS-68 / Yale), main door', 'nos', 12500)
rate('HBB5', 'SS ball-bearing hinge 5 in, heavy ("kabza")', 'nos', 1100)
rate('FBOLT', 'Flush bolt pair, top and bottom (inactive leaf)', 'pair', 1600)
rate('STOPH', 'Floor door stopper, heavy', 'nos', 950)
rate('VIEWER', 'Door viewer (eye) 200 deg', 'nos', 1500)
rate('LKINT', 'Mortise lock with lever handles, good local make', 'set', 4800)
rate('LKBATH', 'Bathroom privacy lock with thumb-turn/indicator and lever handles', 'set', 4200)
rate('HSS4', 'SS hinge 4 in ("kabza")', 'nos', 450)
rate('STOP', 'Floor door stopper', 'nos', 650)
rate('TBOLT', 'SS tower bolt 6 in ("chitkani")', 'nos', 450)
# ---- windows
rate('ALU', 'Aluminium sections, medium local series, powder coated charcoal (RAL 7016)', 'kg', 1450)
rate('WACS', 'Sliding window hardware: rollers, crescent lock, handles, brush seal, gaskets, end caps', 'set', 3200)
rate('WACF', 'Fixed + top-hung vent hardware: friction stays, handle, gaskets', 'set', 1800)
rate('WACV', 'Top-hung ventilator hardware: friction stays, handle, gaskets', 'set', 1400)
rate('WACSF', 'Storefront glazing kit: gaskets, glazing beads, screws, anchors', 'set', 2500)
rate('WACD', 'Sliding door hardware: heavy rollers, lock, handles, seals', 'set', 6500)
rate('G5C', 'Float glass 5 mm clear', 'sft', 215, 'estimated (zameen.com Mar 2023 Rs 142/sft, escalated to 2026)')
rate('G5F', 'Float glass 5 mm frosted / obscure (bathroom ventilators)', 'sft', 250, 'estimated (zameen.com Mar 2023 basis, escalated)')
rate('G66L', 'Laminated glass 6+6 mm clear (12.76 mm, PVB)', 'sft', 1050)
rate('G6T', 'Toughened glass 6 mm clear (sliding door D27)', 'sft', 520)
rate('SIL', 'Silicone sealant, neutral cure, black, 300 ml', 'nos', 1100)
rate('MESH', 'Fly-net mesh, fibreglass, charcoal ("jaali")', 'sft', 55)
rate('MS', 'MS square bars 12 mm and flats 1 1/4 x 1/4 in for grills', 'kg', 285, 'estimated (steel bars Rs 228-232/kg, Feb 2026, + section premium)')
rate('RAWL', 'Rawl bolt 10 mm', 'nos', 60)
# ---- paint (Dulux, AkzoNobel Pakistan)
rate('PUTTY', 'Wall putty, Dulux ("putti")', 'kg', 2850 / 20.0, 'Dulux wall putty 20 kg Rs 2,850 (2026 listing)', size=20, buy='bag (20 kg)', show='buy')
rate('PRIMI', 'Interior wall primer / sealer (alkali resistant), 3.64 L', 'gal', 2650, 'shop.berger.com.pk 2026 (Top Super Primer Plus Rs 2,565-2,700)')
rate('PRIME', 'Exterior alkali-resistant primer, 3.64 L', 'gal', 3335, 'shop.berger.com.pk 2026 (Elegance Ultra Seal Rs 3,335)')
EMUL_SRC = 'estimated (gallon emulsions Rs 3,600-4,000, shop.berger.com.pk 2026)'
WS_SRC = 'estimated (undated ICI list Rs 4,065, escalated)'
rate('TEX', 'Exterior texture coating, acrylic, tinted (roller/trowel grade)', 'kg', 7800 / 20.0, size=20, buy='bucket (20 kg)', show='buy')
rate('ROX', 'Red-oxide metal primer, 3.64 L', 'gal', 3000)
rate('ENAM', 'Enamel gloss, charcoal to match RAL 7016, 3.64 L', 'gal', 4800, 'icons.com.pk paint prices 29-07-2026 (enamel Rs 1,200-2,000 per litre)')
rate('PSUND', 'Paint sundries: sandpaper, masking tape, filler', 'set', 15000)
# ---- electrical second fix
rate('SW1', 'Switch 1-way 10 A, modular, good local make (Orange / Clopal)', 'nos', 280)
rate('SW2', 'Switch 2-way 10 A, modular', 'nos', 420)
rate('SKT5', 'Socket 5/6 A, 3-pin universal, modular', 'nos', 450)
rate('SKT15', 'Socket 15 A switched (Orange Akoya)', 'nos', 1390, 'w11stop.com, Jul 2026')
rate('DP20', 'Switch 20 A double-pole with neon (AC and geyser points)', 'nos', 1250)
rate('PLATE', 'Switch-board plate with frame, 6-12 module', 'nos', 700)
rate('PLATES', 'Plate with frame, 1-2 module (single sockets, DP switches)', 'nos', 300)
rate('WPCOV', 'Weatherproof IP55 cover for outdoor sockets', 'nos', 600)
rate('BELL', 'Call bell push with chime', 'set', 3500)
rate('DL12', 'LED downlight / slim panel 12 W, 3000-4000 K (Coarts or equal)', 'nos', 1220, 'w11stop.com, 26-06-2026')
rate('STRC', 'LED strip 24 V SMD, 5 m reel (cove)', 'nos', 3200)
rate('STRP', 'COB LED strip 24 V, 5 m reel (profiles) - Mux', 'nos', 9100, 'Mux LED strip listing, 2026')
rate('DRV', 'LED driver 24 V, 100 W', 'nos', 3500)
rate('PROF', 'Aluminium recessed profile 2 m with diffuser and end caps', 'nos', 2600)
rate('PROFX', 'Outdoor LED profile IP67, with strip (per m)', 'm', 3500)
rate('CHAND', 'Chandelier - prime-cost allowance (owner to choose)', 'nos', 35000)
rate('PENDL', 'Double-height pendant - prime-cost allowance', 'nos', 25000)
rate('PENDC', 'Dining pendant cluster - prime-cost allowance', 'nos', 15000)
rate('PEND', 'Pendant light - prime-cost allowance', 'nos', 12000)
rate('WLT', 'Stair wall light LED', 'nos', 4500)
rate('UCAB', 'Under-cabinet LED kit (kitchen)', 'set', 6000)
rate('TVL', 'TV-wall LED wash kit', 'set', 5000)
rate('PORCH', 'Porch ceiling light LED 18 W, IP54', 'nos', 2000)
rate('OWL', 'Outdoor wall light LED 12 W, IP65', 'nos', 3200)
rate('LAWN', 'Lawn spike light LED 7 W', 'nos', 2600)
rate('PIL', 'Gate-pillar lantern LED', 'nos', 5500)
rate('BULK', 'Bulkhead light LED 12 W, IP65', 'nos', 2200)
rate('PHOTO', 'Photocell / timer switch for outdoor lights', 'nos', 2500)
rate('FAN', 'Ceiling fan DC inverter 56 in, 35-40 W, with remote (Pak Fan Deluxe Eco Max)', 'nos', 11900, 'powerhouseexpress.com.pk, 2026')
rate('EXH8', 'Exhaust fan 8 in (GFC), bathroom', 'nos', 5400, 'GFC listing, 2026 (from Rs 5,400)')
rate('EXH12', 'Exhaust fan 12 in, metal, kitchen', 'nos', 7500)
rate('AC15', 'Split AC 1.5 t DC inverter, heat and cool (Gree Pular GS-18PIT10W)', 'nos', 178860, 'Pakistani retailer listings (japanelectronics / w11stop), Jul-Aug 2026')
rate('AC20', 'Split AC 2 t DC inverter, heat and cool (Gree Pular GS-24PITH11W)', 'nos', 229900, 'japanelectronics.com.pk, Jul-Aug 2026')
rate('DECO3', 'Wi-Fi 6 mesh TP-Link Deco X50, 3-pack', 'set', 72000, 'Pakistani retailer listing, 2026')
rate('DECO1', 'Wi-Fi 6 mesh TP-Link Deco X50, 1-pack (4th node)', 'nos', 24199, 'qeemat.com.pk (Daraz), 2026')
rate('GSW8', 'Gigabit switch 8-port (router / NVR position)', 'nos', 6500)
rate('NVR8', 'NVR 8-channel with 8 PoE ports, 4K (Hikvision DS-7608NI-Q1/8P)', 'nos', 36000)
rate('IPC4', 'IP camera 4 MP, IR, IP67 (Hikvision DS-2CD1043G2-I or equal)', 'nos', 15000, 'w11stop.com Hikvision listings, 2026 (Rs 14,000-17,000)')
rate('HDD2', 'Surveillance hard disk 2 TB', 'nos', 19000)
rate('EVC', 'EV wall charger 7.4 kW single-phase, Type 2 (RNR)', 'nos', 108000, 'w11stop.com, 13-08-2026')
# ---- external works
rate('TUF60', 'Tuff tiles (interlocking pavers) 60 mm, grey with charcoal border', 'sft', 95)
rate('TUF80', 'Tuff tiles 80 mm (car tracks and ramps)', 'sft', 120)
rate('GSTL', 'MS for gates: 2 x 4 in 14 g frame pipe, 1 1/2 in 16 g members, 16 g sheet', 'kg', 300)
rate('GHWM', 'Main-gate hardware: bearing hinges, tower bolts, aldrop, stopper, wicket lock', 'set', 18000)
rate('GHWS', 'Side-gate hardware: bearing hinges, tower bolts, aldrop, stopper', 'set', 9000)
rate('PCOAT', 'Powder coating of gates, RAL 7016 (material and process)', 'sft', 85)
rate('SSPOST', 'SS 304 railing post 50 mm with base plate, 3 ft 6 in', 'nos', 4500)
rate('SSTR', 'SS 304 top rail 50 mm', 'rft', 650)
rate('G12T', 'Toughened glass 12 mm clear, edge-polished (railings)', 'sft', 1150)
rate('GCLMP', 'SS glass clamp', 'nos', 900)
rate('TANK', 'Plastic water tank 500 gallon, triple layer (roof "tanki")', 'nos', 42000)
rate('TANKF', 'Tank fittings: float valve, overflow, bulkhead connectors, gate valves', 'set', 6000)
rate('PUMP', 'Water pump Pedrollo 1 HP (PKm 80) ("motor")', 'nos', 52000)
rate('PCTRL', 'Automatic water-level controller with float switches and dry-run cut-off', 'set', 6500)
rate('PFIT', 'Pump fittings: non-return valve, gate valves, unions, foot valve', 'set', 5500)

# paint colours (Dulux / AkzoNobel colour codes)
CLR = OrderedDict([
 ('BW', ('Brilliant White', 'ready-mixed white (no tint)')),
 ('JW', ('Jasmine White', '67YY 88/044')),
 ('EC', ('Egyptian Cotton', '40YY 65/061')),
 ('NH', ('Natural Hessian', '14YY 69/082')),
 ('TD', ('Tranquil Dawn', '45GY 55/052')),
 ('DD', ('Denim Drift', '87BG 27/077')),
 ('TM', ('Thai Magic 3', '30YR 41/263')),
 ('CS', ('Chic Shadow', '00NN 53/000')),
 ('NJ', ('Night Jewels 5', '00NN 62/000')),
 ('UO', ('Urban Obsession', '00NN 25/000')),
])
def cname(c): return '%s %s' % (CLR[c][0], CLR[c][1]) if c != 'BW' else CLR[c][0]
for c in CLR:
    rate('EM' + c, 'Dulux standard interior emulsion, %s (2 coats)' % cname(c), 'gal', 3800, EMUL_SRC)
    rate('WS' + c, 'Dulux Weathershield exterior emulsion, %s (2 coats)' % cname(c), 'gal', 5900, WS_SRC)

# ============================================================== BOQ lines
LINES = OrderedDict((s, []) for s in STAGES)
def add(stage, key, net, w=0.0, desc=None):
    r = RATES[key]
    gross = net * (1 + w)
    size = r['size']
    if gross >= 0:
        units = math.ceil(gross / size - 1e-9) if gross > 1e-9 else 0
    else:
        units = -math.ceil(-gross / size - 1e-9)
    buy = units * size
    LINES[stage].append(dict(ref='%d.%02d' % (SNUM[stage], len(LINES[stage]) + 1), key=key, desc=desc or r['name'],
                             net=net, w=w, gross=gross, units=units, buy=buy, amt=round(buy * r['rate'])))
def stage_total(s): return sum(l['amt'] for l in LINES[s])

# ============================================================== AC sizing (room size and orientation)
# front (road) = south as in the grey solar layout; left = west, right = east, rear = north
ORI = {'N': -0.05, 'E': 0.0, 'S': 0.05, 'W': 0.10}
ORIN = {'N': 'north', 'E': 'east', 'S': 'south', 'W': 'west'}
SQFT_PER_TON = 125.0
AC_IN = [  # room, main exposure, shaded, second exposed wall, roof above, glass sft, living room, open to [(room, share)], reading of the plan
 ('G03', 'N', True, False, False, 49.0, False, [], 'W01 on the rear (north) wall under the rear-passage shade; east wall is the party wall'),
 ('G06', 'W', True, False, False, 49.0, False, [], 'W02 faces the 3\'-3" west passage, shaded by the 7 ft boundary wall'),
 ('G09', 'E', True, False, False, 22.75, True, [('G11', 0.30)], 'small east window W03 on the patio; open to the open kitchen through the 6\'-6" arch'),
 ('G13', 'S', False, True, False, 80.75, True, [], 'south double-height glazing W06 (lower part); west wall on the side passage'),
 ('G14', 'S', True, False, False, 42.0, True, [], 'front window W05 shaded by the car-porch slab; east wall is the party wall'),
 ('F04', 'N', True, False, True, 49.0, False, [], 'W10 on the north wall under a sunshade; terrace roof above'),
 ('F07', 'W', False, False, True, 49.0, False, [], 'W11 on the west wall above boundary-wall height; terrace roof above'),
 ('F10', 'E', True, False, True, 56.0, True, [('F02', 0.30), ('F03', 0.30)], 'W13 on the 3\'-6" open shaft; one side open to the FF lobby; roof above'),
 ('F13', 'W', False, True, True, 121.25, False, [], 'corner room: W12 west + W06 upper part south (72 sft); roof above'),
 ('S02', 'N', False, True, True, 35.0, False, [], 'mumty room on the roof: W15 north, south wall faces the open terrace; roof above'),
]
AC = []
for (k, ori, shaded, wall2, roof, glass, living, opento, reading) in AC_IN:
    a = R[k]['area']; a_eff = a + sum(sh * R[j]['area'] for j, sh in opento)
    base = a_eff / SQFT_PER_TON
    c_or = ORI[ori] / 2 if (shaded and ORI[ori] > 0) else ORI[ori]
    c_roof = 0.15 if roof else 0.0
    c_w2 = 0.05 if wall2 else 0.0
    c_gl = max(0.0, (glass - 50.0) / 25.0 * 0.05)
    c_pp = 0.10 if living else 0.0
    need = base * (1 + c_or + c_roof + c_w2 + c_gl + c_pp)
    sel = next((s for s in (1.0, 1.5, 2.0) if need <= 1.10 * s), 2.0)
    AC.append(dict(k=k, ori=ori, shaded=shaded, a=a, a_eff=a_eff, base=base, c_or=c_or, c_roof=c_roof, c_w2=c_w2, c_gl=c_gl,
                   c_pp=c_pp, need=need, sel=sel, over=need > 1.10 * sel, opento=opento, glass=glass, reading=reading,
                   step_a=EP[k][4]))
assert len(AC) == 10 and all(EP[x['k']][4] for x in AC)
N15 = sum(1 for x in AC if x['sel'] == 1.5); N20 = sum(1 for x in AC if x['sel'] == 2.0); N10 = sum(1 for x in AC if x['sel'] == 1.0)
assert N10 + N15 + N20 == 10
AC_KW_NEW = N10 * A['AC_KW'][1.0] + N15 * A['AC_KW'][1.5] + N20 * A['AC_KW'][2.0]
AC_KW_OLD = sum(l[1] for l in A['LOADS'] if l[0].startswith('10 inverter ACs')) / 1000.0
MD_NEW = A['MD'] + (AC_KW_NEW - AC_KW_OLD) * 1000 * A['DF']['ac']
I_NEW = MD_NEW / (math.sqrt(3) * 400 * 0.9)

# ============================================================== STAGE 1: circuits, wires, DBs
def floor_pts(fl):
    d = defaultdict(int)
    for k, (dl, deco, fan, ex, ac, s5, p15, lv, sb, note) in EP.items():
        if R[k]['fl'] != fl: continue
        d['DL'] += dl; d['FAN'] += fan; d['EX'] += ex; d['S5'] += s5; d['P15'] += p15; d['SB'] += sb; d['LV'] += lv
        d['DECO'] += (3 if k == 'F01' else (1 if deco else 0))
        d['AC'] += 1 if ac else 0
    return d
FP = {fl: floor_pts(fl) for fl in FLOORS}
RT = dict(DL=2.0, FAN=5.0, EX=4.0, DECO=4.0, SB=6.0, S5=3.0, HR=12.0, P15C=17.0, EXTL=7.0)
STRAP = {'GF': 2 * 8.0 + 2 * 2 * 5.0, 'FF': 2 * 8.0 + 3 * 2 * 5.0, '2F': 2 * 5.0}   # 2-way strappers: stairs + bed-head
AC_RUN = {'GF': 45 * 0.3048 + 1.5, 'FF': 30 * 0.3048 + 1.5, '2F': 40 * 0.3048 + 1.5}  # grey conduit runs + terminations
DBN = OrderedDict([('GF-M', 'GF main DB (grid side)'), ('GF-B', 'GF backup DB (inverter load port)'),
                   ('FF-M', 'FF main DB'), ('FF-B', 'FF backup DB'), ('2F-M', 'Mumty main DB'), ('2F-B', 'Mumty backup DB')])
CIRC = []
def circ(db, name, pts, size, esize, route, load, mcb, n=1):
    for i in range(n):
        CIRC.append(dict(db=db, name=name, pts=pts, size=size, esize=esize, route=route, load=load, mcb=mcb, ph=None))
ac_by_fl = defaultdict(list)
for x in AC: ac_by_fl[R[x['k']]['fl']].append(x)
for fl in FLOORS:
    p = FP[fl]
    lpts = p['DL'] + p['FAN'] + p['EX'] + p['DECO']
    nl = math.ceil(lpts / 12)
    route = p['DL'] * RT['DL'] + p['FAN'] * RT['FAN'] + p['EX'] * RT['EX'] + p['DECO'] * RT['DECO'] + p['SB'] * RT['SB'] + STRAP[fl]
    dbb, dbm = fl + '-B', fl + '-M'
    circ(dbb, 'Lighting, fans and exhausts', '%d in total' % lpts, 1.5, 1.5, route / nl, lpts / nl * 20, '10 A B', nl)
    ns = math.ceil(p['S5'] / 8)
    circ(dbb, '5 A sockets (RCD)', '%d in total' % p['S5'], 2.5, 1.5, (p['S5'] * RT['S5'] + ns * RT['HR']) / ns, 800, '16 A B', ns)
    if fl == '2F':
        circ(dbm, '15 A power point - room', '1', 4.0, 2.5, 12.0, 1500, '20 A B')
        circ(dbm, '15 A power point - washing machine', '1', 4.0, 2.5, 8.0, 2200, '20 A B')
    else:
        npw = math.ceil(p['P15'] / 2)
        circ(dbm, '15 A power points (RCD)', '%d in total' % p['P15'], 4.0, 2.5, RT['P15C'], 2000, '20 A B', npw)
    for x in ac_by_fl[fl]:
        circ(dbm, 'AC %g t - %s' % (x['sel'], rn(x['k'])), '1', 4.0, 2.5, AC_RUN[fl], A['AC_KW'][x['sel']] * 1000, '20 A C')
    circ(dbm, 'Geyser electric element (hybrid geyser)', '1', 4.0, 2.5, 15.0, 600, '20 A B')
ext_route = (cnt['EXTL'] * RT['EXTL'] + 2 * 15.0 + 1 * RT['FAN']) / 2
circ('GF-B', 'External lighting + porch fan (photocell)', '%d lights in total' % cnt['EXTL'], 1.5, 1.5, ext_route, 220, '10 A B', 2)
circ('GF-B', 'External 5 A sockets, weatherproof (RCD)', '6', 2.5, 1.5, 6 * 4.0 + 12.0, 600, '16 A B')
circ('GF-B', 'Water pump 1 HP (underground tank)', '1', 2.5, 1.5, 20.0, 750, '16 A C')
circ('GF-B', 'Wi-Fi router, NVR, cameras', '1', 2.5, 1.5, 15.0, 150, '10 A B')
circ('GF-M', 'EV charger 7.4 kW', '1', 6.0, 6.0, 12.0, 7400, 'RCBO 40 A Type A')
BELL_M = 2 * 13.0          # 2 call bells from the external-lighting circuit (live + neutral, no earth)
# phase balancing: TPN boards greedy by load; single-phase mumty boards on one phase each
SPN_PHASE = {'2F-M': 'B', '2F-B': 'Y'}
for db in DBN:
    cs = sorted([c for c in CIRC if c['db'] == db], key=lambda c: -c['load'])
    if db in SPN_PHASE:
        for c in cs: c['ph'] = SPN_PHASE[db]
        continue
    load = {'R': 0.0, 'Y': 0.0, 'B': 0.0}
    for c in cs:
        ph = min(load, key=lambda q: (load[q], 'RYB'.index(q)))
        c['ph'] = ph; load[ph] += c['load']
SUBMAINS = [  # name, from, to, conductors (size), earth size, route m, phases
 ('GF main DB to FF main DB (3-phase)', 10.0, 6.0, 9.0, 'RYB', '4P MCB 40 A'),
 ('GF main DB to inverter grid port (mumty laundry)', 10.0, 6.0, 15.0, 'RYB', '4P MCB 40 A'),
 ('Inverter load port to GF backup DB', 10.0, 6.0, 15.0, 'RYB', '4P MCB 40 A (in inverter AC box)'),
 ('GF backup DB to FF backup DB (3-phase)', 6.0, 6.0, 7.5, 'RYB', '4P MCB 32 A'),
 ('FF main DB to mumty main DB (phase B)', 6.0, 6.0, 11.0, 'B', 'DP MCB 32 A'),
 ('FF backup DB to mumty backup DB (phase Y)', 4.0, 2.5, 11.0, 'Y', 'DP MCB 20 A'),
]
WL = defaultdict(float)      # (size, colour) -> metres (net)
for c in CIRC:
    WL[(c['size'], c['ph'])] += c['route']; WL[(c['size'], 'K')] += c['route']; WL[(c['esize'], 'G')] += c['route']
first_gf_light = [c for c in CIRC if c['db'] == 'GF-B' and c['name'].startswith('External lighting')][0]
WL[(1.5, first_gf_light['ph'])] += BELL_M; WL[(1.5, 'K')] += BELL_M
for (nm, sz, es, rt_, phs, brk) in SUBMAINS:
    for ph in phs: WL[(sz, ph)] += rt_
    WL[(sz, 'K')] += rt_; WL[(es, 'G')] += rt_
EARTH_LEADS = (25 + 45 + 55) * 0.3048 + 3 * 2.0      # grey conduit runs from the 3 earth pits + terminations
METER_RUN = 20.0
WIRE_W = 0.10
for sz in (1.5, 2.5, 4.0, 6.0, 10.0):
    for c, cn in COL.items():
        m = WL.get((sz, c), 0.0)
        if m > 0:
            use = {1.5: 'lighting, fans, exhausts, bells', 2.5: 'sockets, pump, Wi-Fi/CCTV', 4.0: 'ACs, 15 A points, geysers, mumty backup feed',
                   6.0: 'EV charger, backup and mumty sub-mains', 10.0: '3-phase sub-mains and inverter'}[sz]
            euse = {1.5: 'lighting and socket circuits', 2.5: '4 mm2 circuits', 6.0: 'EV charger and sub-mains'}.get(sz, '')
            role = 'phase' if c in 'RYB' else ('neutral' if c == 'K' else 'earth')
            add('S1', 'W%g%s' % (sz, c), m, WIRE_W, 'Wire ("taar") %g mm2 %s - %s of %s (net %s m)' % (sz, cn, role, euse if c == 'G' else use, f0(m)))
add('S1', 'W16G', EARTH_LEADS, WIRE_W, 'Earth leads 16 mm2 green/yellow from the 3 grey earth pits to the DB and inverter (net %s m)' % f0(EARTH_LEADS))
add('S1', 'CAB416', METER_RUN, 0.05, 'Incomer: FESCO meter (front) to GF main DB, 4-core 16 mm2 armoured')
CAT6_M = (2 * 35 + 2 * 45 + 60 + 7 * 50) * 0.3048 * 1.2
add('S1', 'CAT6', CAT6_M, 0.0, 'Cat6 to 4 Wi-Fi nodes and 7 cameras (grey data conduits, +20%% loops) - %s m' % f0(CAT6_M))
add('S1', 'RJ45', 40, 0.0, 'RJ45 connectors (cameras, nodes, patching)')
add('S1', 'KEYST', 6, 0.0)
NDB = OrderedDict([('DB36', 2), ('DB24', 2), ('DB8S', 2)])
for k, n in NDB.items(): add('S1', k, n)
add('S1', 'DBCR', 1)
NSP = sum(1 for c in CIRC if not c['mcb'].startswith('RCBO'))
for k, n in [('MCCB63', 1), ('MCB4P40', 4), ('MCB4P32', 2), ('MCBDP', 4), ('MCBSP', NSP), ('RCCB4', 4), ('RCCB2', 2),
             ('RCBOA', 1), ('SPD4', 1), ('CHO', 1), ('ISO40', 1), ('DBACC', 1)]:
    add('S1', k, n)
add('S1', 'ACK15', N15, 0.0, RATES['ACK15']['name'] + ' - %d units' % N15)
add('S1', 'ACK20', N20, 0.0, RATES['ACK20']['name'] + ' - %d units' % N20)

# ============================================================== STAGE 2: solar and storage
N_PANEL, N_PLINTH = 23, 34
add('S2', 'PV650', N_PANEL, 0.0, RATES['PV650']['name'] + ' - 23 nos = 14.95 kWp')
add('S2', 'INV12', 1)
N_BAT = 2
add('S2', 'NAB5', N_BAT, 0.0, RATES['NAB5']['name'] + ' - 2 now (about 10.6 kWh); a 3rd module later gives about 16 kWh')
add('S2', 'BRACK', 1); add('S2', 'BDC', 1)
add('S2', 'MNT', N_PANEL); add('S2', 'PLB', N_PLINTH)
PV_HOME = 32.0; PV_JUMP = 8.0          # per string: roof run to the inverter + inter-row jumpers
PV_M = 2 * (PV_HOME + PV_JUMP)
add('S2', 'PVR', PV_M, 0.10, 'DC solar cable 6 mm2 red - 2 strings x %s m (net %s m)' % (f0(PV_HOME + PV_JUMP), f0(PV_M)))
add('S2', 'PVK', PV_M, 0.10, 'DC solar cable 6 mm2 black - 2 strings x %s m (net %s m)' % (f0(PV_HOME + PV_JUMP), f0(PV_M)))
add('S2', 'MC4', 10); add('S2', 'DCBOX', 1); add('S2', 'ACBOX', 1)
add('S2', 'W6G', 30.0, 0.10, 'Frame bonding 6 mm2 green to the solar earth pit (net 30 m)')
add('S2', 'NETM', 1); add('S2', 'NETF', 1)

# ============================================================== STAGE 3: false ceilings
COVE_ROOMS = ['G06', 'G13', 'G14', 'F07', 'F10']          # drawing, both lounges, both master bedrooms (Q27)
COVE_DEPTH = 1.75                                          # ft of board per rft of cove (drop 9" + soffit 12" + lip 3")
FC = OrderedDict()
for k, r in R.items():
    kind = 'MR' if r['cat'] in ('BATH', 'WET') else 'STD'
    cove = 2 * (r['L'] + r['W']) if k in COVE_ROOMS else 0.0
    FC[k] = dict(a=A['FC_AREA'][k], kind=kind, cove=cove, perim=r['perim'])
FC_STD = sum(v['a'] for v in FC.values() if v['kind'] == 'STD')
FC_MR = sum(v['a'] for v in FC.values() if v['kind'] == 'MR')
COVE_RFT = sum(v['cove'] for v in FC.values())
COVE_SFT = COVE_RFT * COVE_DEPTH
FC_ALL = FC_STD + FC_MR
FC_M2 = FC_ALL * 0.092903
PERIM_M = sum(v['perim'] for v in FC.values()) * 0.3048
COVE_M = COVE_RFT * 0.3048
add('S3', 'GB125', (FC_STD + COVE_SFT) / 32.0, 0.07, 'Gypsum board 12.5 mm standard: %s sft ceilings + %s sft cove boxes (%s rft x %s ft)' % (
    f0(FC_STD), f0(COVE_SFT), f0(COVE_RFT), COVE_DEPTH))
add('S3', 'GBMR', FC_MR / 32.0, 0.10, 'Gypsum board 12.5 mm moisture-resistant: baths, powder room, laundry %s sft' % f0(FC_MR))
add('S3', 'GCS', FC_M2 * 1.7 + COVE_M * 2.5, 0.05, 'Ceiling section at 600 mm (1.7 m per m2) + cove framing 2.5 m per m')
add('S3', 'GIC', FC_M2 * 0.85, 0.05, 'Intermediate channel at 1,200 mm (0.85 m per m2)')
add('S3', 'GPC', PERIM_M, 0.05, 'Perimeter channel on all room walls (%s m)' % f0(PERIM_M))
add('S3', 'GHG', FC_M2 * 0.7, 0.05, 'Hangers at 1.2 m x 1.2 m (0.7 per m2); drops 12-30 in')
add('S3', 'GANC', FC_M2 * 0.7 + PERIM_M * 1.7, 0.05, 'Anchor fasteners: hangers + perimeter channel at 600 mm')
add('S3', 'GCLP', FC_M2 * 2.0, 0.05)
add('S3', 'GSCR', (FC_M2 + COVE_SFT * 0.092903) * 14, 0.10, 'Board screws, 14 per m2')
add('S3', 'GWSC', FC_M2 * 4, 0.10, 'Frame screws, 4 per m2')
add('S3', 'GJC', (FC_M2 + COVE_SFT * 0.092903) * 0.35, 0.10, 'Jointing compound 0.35 kg per m2')
add('S3', 'GTAPE', FC_M2 * 1.5 + COVE_M * 2, 0.10, 'Joint tape 1.5 m per m2 + 2 m per m of cove')
add('S3', 'GBEAD', math.ceil(COVE_M * 2 / 3.0), 0.0, 'Edge bead on cove lips (2 lines per cove)')
add('S3', 'GAP', 9, 0.0, 'Access panels: 7 baths, laundry, 1 spare (AC / junctions)')

# ============================================================== STAGE 4: floor and wall tiles
BOX = 15.5
def boxes(sft, w): return math.ceil(sft * (1 + w) / BOX - 1e-9)
SK_YIELD = 7.75 / (5 * 1200 / 304.8)          # sft of 2'x4' tile per rft of 4" skirting (5 strips per tile)
skirt = defaultdict(float)
for k, r in R.items(): skirt[(r['fl'], r['cat'])] += r['skirt']
T24_ROOMS = {fl: sum(r['area'] for r in R.values() if r['fl'] == fl and r['cat'] in ('T24', 'HALL')) for fl in FLOORS}
T24_SK = {fl: skirt[(fl, 'T24')] + skirt[(fl, 'HALL')] for fl in FLOORS}
KIT = ['G11', 'G12', 'F12']
KIT_SK = sum(R[k]['skirt'] for k in KIT)
W_FLOOR, W_SK, W_SMALL, W_WALL = 0.08, 0.10, 0.10, 0.10
T24P_FLOOR = sum(T24_ROOMS.values()); T24P_SK = sum(T24_SK.values()) * SK_YIELD
T24M_FLOOR = sum(R[k]['area'] for k in KIT); T24M_SK = KIT_SK * SK_YIELD
LAUN_F = R['S04']['area']; LAUN_W = A['WALLT']['S04']['net']
add('S4', 'T24P', T24P_FLOOR, W_FLOOR, '2\'x4\' polished porcelain - rooms, lobbies, dresses, store, stair-hall landings %s sft (8%% cutting)' % f1(T24P_FLOOR))
add('S4', 'T24P', T24P_SK, W_SK, '2\'x4\' polished porcelain cut into 4" skirting strips - %s rft (5 strips per tile = %s sft)' % (
    f0(sum(T24_SK.values())), f1(T24P_SK)))
add('S4', 'T24M', T24M_FLOOR, W_FLOOR, '2\'x4\' matt porcelain - 3 kitchens %s sft' % f1(T24M_FLOOR))
add('S4', 'T24M', T24M_SK, W_SK, '2\'x4\' matt porcelain cut into 4" skirting - %s rft' % f0(KIT_SK))
add('S4', 'T60M', LAUN_F, W_SMALL, '600 x 600 matt anti-slip - laundry floor %s sft' % f1(LAUN_F))
add('S4', 'T36W', LAUN_W, W_WALL, '300 x 600 glazed - laundry dado 4 ft on two walls %s sft' % f1(LAUN_W))
BED_C, BED_S = 0.01693, 0.0847                  # cement bags and sand cft per sft of 1" 1:4 bed (dry volume x 1.27)
S4_BED = T24P_FLOOR + T24M_FLOOR + LAUN_F
add('S4', 'CEM', S4_BED * BED_C, 0.05, 'Cement for 1" semi-dry 1:4 bed under %s sft of floor tiles (1.7 bags per 100 sft)' % f0(S4_BED))
add('S4', 'SNDM', S4_BED * BED_S, 0.10, 'Ravi sand for the same bed (8.5 cft per 100 sft)')
ADH_FLOOR, ADH_WALL = 0.30, 0.35                # kg per sft: bond coat on floors / walls and skirting
S4_ADH = S4_BED * ADH_FLOOR + (T24P_SK + T24M_SK + LAUN_W) * ADH_WALL
add('S4', 'ADH', S4_ADH, 0.05, 'Tile adhesive: floors 0.30 kg/sft (bond coat, back-buttered), skirting and dado 0.35 kg/sft')
S4_GRT = (T24P_FLOOR + T24M_FLOOR) * 0.015 + LAUN_F * 0.02 + (T24P_SK + T24M_SK + LAUN_W) * 0.03
add('S4', 'GRT', S4_GRT, 0.10, 'Grout 2 mm joints: 0.015 kg/sft (2\'x4\'), 0.02 (600 x 600), 0.03 (skirting, dado)')
add('S4', 'CLIP', (T24P_FLOOR + T24M_FLOOR) * 0.40 + LAUN_F * 0.5, 0.05, 'Levelling clips: 0.4 per sft (2\'x4\'), 0.5 per sft (600 x 600)')
add('S4', 'WEDGE', 200, 0.0, 'Levelling wedges, reusable (2 bags)')
add('S4', 'SPC', LAUN_W * 0.6 + 50, 0.0, 'Spacers for dado and skirting')
add('S4', 'TRIM', 2, 0.0, 'Edge trim on the laundry dado top')
LAUN_WP = LAUN_F + (5.125 + 6.5) * 1.0
add('S4', 'WPRF', LAUN_WP * 0.28, 0.10, 'Waterproofing under laundry tiles: floor + 1 ft upturn = %s sft at 3 kg/m2 (2 coats)' % f0(LAUN_WP))
add('S4', 'FTRAP', 1, 0.0, 'Floor-trap grating, laundry')

# ============================================================== STAGE 5: marble and granite
NT, NR, WST = A['N_TREAD'], A['N_RISER'], A['W_ST']
TREAD_SFT = 2 * NT * WST * (10.5 + 1.0) / 12          # 10 1/2" going + 1" nosing
LAND_SFT = A['st_land']
RISER_SFT = A['st_riser']
SKIRT_STAIR_RFT = A['st_skirt']
SKIRT_STAIR_SFT = SKIRT_STAIR_RFT * 4 / 12
EXT_T = sum(n * w for _, n, w in A['EXT_STEPS']) * (12 + 1) / 12.0
EXT_R = A['ext_riser']
SILL_D = 11 / 12.0
SILLS = []
for x in WROWS:
    if x['ref'] == 'W07': continue                      # above the main door, no sill
    SILLS.append((x['ref'], x['n'], x['w'] + 0.33, SILL_D))
SILL_SFT = sum(n * l * d for _, n, l, d in SILLS)
THR = []
for (ref, fl, ra, rb, w, h, swing, typ, flag) in DOORS:
    if typ.startswith('Bathroom'): THR.append((ref, w, 0.5))
    elif ref in ('D01', 'D02', 'D12', 'D28', 'D27'): THR.append((ref, w, SILL_D))
THR_SFT = sum(w * d for _, w, d in THR)
add('S5', 'GRN20', TREAD_SFT + LAND_SFT, 0.10, 'Granite treads with 3 anti-slip grooves (cut by the supplier) - 42 treads 11 1/2" x 3\'-6" + 2 mid landings ("paidan")')
add('S5', 'ZW20', RISER_SFT, 0.10, 'White marble risers ("uthan") - 44 risers 6.57" x 3\'-6"')
add('S5', 'ZW20', SKIRT_STAIR_SFT, 0.20, 'White marble 4" stepped skirting, both sides of both flights - %s rft' % f0(SKIRT_STAIR_RFT))
add('S5', 'GRN20', EXT_T + EXT_R, 0.10, 'External steps (4 sets, 14 risers): granite treads with nosing + granite risers')
add('S5', 'GRN20', SILL_SFT, 0.15, 'Window and ventilator sills 11" deep with 2" horns - %d openings' % sum(n for _, n, _, _ in SILLS))
add('S5', 'GRN20', THR_SFT, 0.15, 'Door thresholds ("dehleez"): 7 bath doors, D01, D02, D12, D28 and sliding door D27')
S5_BED = TREAD_SFT + LAND_SFT + EXT_T + EXT_R + RISER_SFT + SILL_SFT + THR_SFT + SKIRT_STAIR_SFT
add('S5', 'CEM', S5_BED * BED_C, 0.05, 'Cement for 1" 1:4 bedding of all stone (%s sft)' % f0(S5_BED))
add('S5', 'SNDM', S5_BED * BED_S, 0.10)
add('S5', 'WCEM', 1, 0.0)
add('S5', 'SEAL', 2, 0.0)

# ============================================================== STAGE 6: bathrooms
BATHS = [k for k, r in R.items() if r['cat'] == 'BATH']
POWDER = 'G10'
FULL = [k for k in BATHS if k != POWDER]
BT = OrderedDict()
for k in BATHS:
    r = R[k]
    wall = A['WALLT'][k]['net']
    feat = min(r['L'], r['W']) * r['fc']
    wp = r['area'] + r['perim'] * 1.0 + (36.0 if k in FULL else 0.0)
    BT[k] = dict(floor=r['area'], wall=wall, feat=feat, plain=wall - feat, wp=wp)
B_FLOOR = sum(v['floor'] for v in BT.values()); B_PLAIN = sum(v['plain'] for v in BT.values()); B_FEAT = sum(v['feat'] for v in BT.values())
B_WP = sum(v['wp'] for v in BT.values())
add('S6', 'WPRF', B_WP * 0.28, 0.10, 'Waterproofing under tiles, 2 coats (3 kg/m2): floors + 1 ft upturn + shower walls 6 ft high = %s sft' % f0(B_WP))
add('S6', 'WPTP', len(BATHS), 0.0, 'Reinforcing tape at corners, floor traps and pipe entries (1 roll per bath)')
add('S6', 'T60M', B_FLOOR, W_SMALL, '600 x 600 matt anti-slip floor tiles - 7 baths %s sft (10%% cutting for falls)' % f1(B_FLOOR))
add('S6', 'T36W', B_PLAIN, W_WALL, '300 x 600 glazed wall tiles, plain - to false ceiling %s sft' % f1(B_PLAIN))
add('S6', 'T36F', B_FEAT, W_WALL, '300 x 600 feature tiles - one wall per bath %s sft' % f1(B_FEAT))
BED_C_B, BED_S_B = BED_C * 1.25, BED_S * 1.25    # 1 1/4" average bed with falls
add('S6', 'CEM', B_FLOOR * BED_C_B, 0.05, 'Cement for 1 1/4" average bed with falls to the traps')
add('S6', 'SNDM', B_FLOOR * BED_S_B, 0.10)
add('S6', 'ADH', B_FLOOR * ADH_FLOOR + (B_PLAIN + B_FEAT) * ADH_WALL, 0.05, 'Tile adhesive: floors 0.30, walls 0.35 kg/sft')
add('S6', 'GRT', B_FLOOR * 0.02 + (B_PLAIN + B_FEAT) * 0.03, 0.10)
add('S6', 'CLIP', B_FLOOR * 0.5, 0.05)
add('S6', 'SPC', (B_PLAIN + B_FEAT) * 0.6, 0.0)
add('S6', 'TRIM', 3 * len(BATHS), 0.0, 'Edge trims: niches, ventilator reveals and external corners (3 per bath)')
N_TRAP = 2 * len(FULL) + 1
add('S6', 'FTRAP', N_TRAP, 0.0, 'Floor-trap gratings: shower + general in 6 baths, 1 in the powder room')
add('S6', 'WC1P', len(BATHS)); add('S6', 'MSH', len(BATHS))
add('S6', 'AVLV', 3 * len(BATHS), 0.0, 'Angle valves: WC cistern + basin hot and cold')
add('S6', 'FLEX', 3 * len(BATHS))
add('S6', 'BSNV', len(FULL)); add('S6', 'BSNW', 1)
add('S6', 'BMIXT', len(FULL)); add('S6', 'BMIX', 1); add('S6', 'BWST', len(BATHS))
add('S6', 'SHMX', len(FULL)); add('S6', 'RAIN', len(FULL)); add('S6', 'HSH', len(FULL))
SCREEN = 3.0 * 6.5
add('S6', 'GLS8', SCREEN * len(FULL), 0.0, 'Shower screens 8 mm toughened, fixed, 3\'-0" x 6\'-6" in 6 baths (made to size)')
add('S6', 'GLSH', len(FULL))
VAN_SHEET = 0.75
add('S6', 'HMR18', VAN_SHEET * len(FULL), 0.10, 'Wall-hung vanity cabinets 2\'-6" wide, HDHMR 18 mm - 0.75 sheet each')
add('S6', 'HETH', 2 * len(FULL)); add('S6', 'HNDL', len(FULL))
add('S6', 'EDGE', 8.0 * len(FULL), 0.0, 'Edge band for vanities (8 m each)')
add('S6', 'VBRK', len(FULL))
VAN_TOP = 3.0 * (22 / 12.0) + 3.0 * 0.25
add('S6', 'GRN20', VAN_TOP * len(FULL), 0.15, 'Granite vanity tops 3\'-0" x 1\'-10" with 3" upstand, basin cut-out (6 nos)')
add('S6', 'ACCS', len(FULL)); add('S6', 'ACCP', 1)
add('S6', 'MIRL', len(FULL)); add('S6', 'MIRS', 1)
add('S6', 'GEY35', 2, 0.0, RATES['GEY35']['name'] + ' - GF and FF')
add('S6', 'GEY15', 1, 0.0, RATES['GEY15']['name'] + ' - mumty bath and laundry')
add('S6', 'GEYF', 3)

# ============================================================== STAGE 7: kitchens and wardrobes
KR = OrderedDict([  # kitchen, wall counter runs (rft), island (base rft, top L x W), sink, hob, hood
 ('G11', dict(runs=[('rear wall', 5.25), ('side wall', 6.0)], island=(4.5, 5.0, 2.5), hob=True, hood='island')),
 ('G12', dict(runs=[('L-counter', 7.0), ('L-counter', 9.0)], island=None, hob=False, hood=None)),
 ('F12', dict(runs=[('L-counter', 13.0), ('L-counter', 6.0)], island=None, hob=True, hood='wall')),
])
K_WALLRUN = sum(sum(l for _, l in v['runs']) for v in KR.values())
K_ISL = sum(v['island'][0] for v in KR.values() if v['island'])
K_BASE = K_WALLRUN + K_ISL
K_WALLCAB = 0.70 * K_WALLRUN
K_CARC = K_BASE * 9.0 + K_WALLCAB * 6.0
K_BACK = K_BASE * 2.8 + K_WALLCAB * 2.5
K_SHUT = K_BASE * 2.6 + K_WALLCAB * 2.4 + K_ISL * 2.8
N_SHUT = math.ceil(K_BASE / 1.5) + math.ceil(K_WALLCAB / 1.5)
N_DRW = 15
K_GRAN = K_WALLRUN * (25 / 12.0) + sum(v['island'][1] * v['island'][2] for v in KR.values() if v['island']) \
    + (K_WALLRUN + 2 * 5.0 + 2 * 2.5) * 0.15
K_BS = sum(A['WALLT'][k]['net'] for k in KR)
add('S7', 'HMR18', K_CARC / 32.0, 0.10, 'Kitchen carcass HDHMR 18 mm: base %s rft (incl. island) x 9 sft + wall cabinets %s rft x 6 sft = %s sft' % (
    f1(K_BASE), f1(K_WALLCAB), f0(K_CARC)))
add('S7', 'HMR6', K_BACK / 32.0, 0.10, 'Kitchen back panels 6 mm: %s sft' % f0(K_BACK))
add('S7', 'ACRY', K_SHUT / 32.0, 0.10, 'Acrylic shutters and island side panels: %s sft (%d shutters)' % (f0(K_SHUT), N_SHUT))
add('S7', 'EDGA', N_SHUT * 2 * (1.5 + 2.5) * 0.3048, 0.10, 'Acrylic edge band on shutters')
add('S7', 'EDGE', (K_BASE + K_WALLCAB) * 4 * 0.3048, 0.10, 'PVC edge band on carcass fronts')
add('S7', 'HETH', 2 * N_SHUT, 0.0, 'Hettich soft-close hinges, 2 per shutter')
add('S7', 'DRW', N_DRW, 0.0, 'Soft-close drawer runners: 3 stacks of 3 drawers + 6 in the FF kitchen')
add('S7', 'BSKT', 6); add('S7', 'HNDL', N_SHUT + N_DRW)
add('S7', 'LEG', 2 * K_BASE, 0.0); add('S7', 'HANG', math.ceil(K_WALLCAB / 1.5))
add('S7', 'KSKT', K_WALLRUN + 2 * 4.5 + 2 * 2.0, 0.05, 'Aluminium plinth on wall runs and island')
add('S7', 'FIX', 3, 0.0, 'Kitchen fixings, screws, glue, silicone (3 kitchens)')
add('S7', 'GRN20', K_GRAN, 0.15, 'Granite counters 20 mm with 40 mm built-up front edge: %s rft x 2\'-1" + island top 5\'-0" x 2\'-6"' % f1(K_WALLRUN))
add('S7', 'SINK2', 3); add('S7', 'SMIX', 3); add('S7', 'SWST', 3)
add('S7', 'AVLV', 6, 0.0, 'Angle valves under sinks (hot and cold)'); add('S7', 'FLEX', 6)
add('S7', 'HOB5', 2, 0.0, RATES['HOB5']['name'] + ' - open-kitchen island and FF kitchen')
add('S7', 'HOODI', 1, 0.0, RATES['HOODI']['name'] + ' - over the open-kitchen island hob')
add('S7', 'HOODW', 1, 0.0, RATES['HOODW']['name'] + ' - FF kitchen')
add('S7', 'DUCT', 2)
add('S7', 'T36K', K_BS, W_WALL, '300 x 600 backsplash 2\'-0" high: open kitchen, raw kitchen, FF kitchen %s sft' % f1(K_BS))
add('S7', 'ADH', K_BS * ADH_WALL, 0.05); add('S7', 'GRT', K_BS * 0.03, 0.10); add('S7', 'SPC', 100, 0.0); add('S7', 'TRIM', 6)
WR = OrderedDict([('G04', ('Bed-1 dress (GF)', 4.0, 'straight, on the bottom wall')), ('G07', ('Master dress (GF)', 4.5, 'straight')),
                  ('F05', ('Bed-1 dress (FF)', 4.0, 'straight')), ('F08', ('Master dress (FF)', 4.5, 'straight')),
                  ('F14', ('Front-bed dress (FF)', 5.25 + 6.0 - 2.0, 'L-shaped 5\'-3" + 6\'-0" less corner')),
                  ('F11', ('Store (FF)', 13.0 + 6.0 - 2.0, 'L-shaped 13\'-0" + 6\'-0" less corner'))])
W_RUN = sum(v[1] for v in WR.values())
W_H = 10.0
N_WSH = math.ceil(W_RUN / 2.0)
add('S7', 'HMR18', W_RUN * 18.0 / 32.0, 0.10, 'Wardrobe carcass 18 mm pre-laminated: %s rft x 18 sft (8 ft + 2 ft loft, 2 ft deep)' % f1(W_RUN))
add('S7', 'HMR6', W_RUN * 10.0 / 32.0, 0.10, 'Wardrobe back panels 6 mm')
add('S7', 'HMR18', W_RUN * 10.0 / 32.0, 0.10, 'Wardrobe shutter boards 18 mm: %s sft' % f0(W_RUN * 10))
add('S7', 'HPL', W_RUN * 10.0 / 32.0, 0.10, 'Decorative laminate 1 mm on shutters (outside face)')
add('S7', 'LINER', W_RUN * 10.0 / 32.0, 0.10, 'Liner laminate on shutters (inside face)')
add('S7', 'HETH', N_WSH * 4 + N_WSH * 2, 0.0, 'Hettich soft-close hinges: %d tall shutters x 4 + %d loft shutters x 2' % (N_WSH, N_WSH))
add('S7', 'WHND', N_WSH); add('S7', 'WHNS', N_WSH)
add('S7', 'WROD', math.ceil(N_WSH / 2)); add('S7', 'DRW', 2 * len(WR), 0.0, 'Drawer runners, 2 drawers per wardrobe')
add('S7', 'WLOCK', len(WR))
add('S7', 'EDGE', (N_WSH * 2 * (2 + 8) + N_WSH * 2 * (2 + 2) + W_RUN * 10.5) * 0.3048, 0.10, 'Edge band on shutters and carcass fronts')
add('S7', 'FIX', len(WR), 0.0, 'Wardrobe fixings (6 locations)')

# ============================================================== STAGE 8: doors
INT_IDS = [d[0] for d in DOORS if d[7].startswith(('Internal', 'Store', 'Kitchen'))]
BATH_IDS = [d[0] for d in DOORS if d[7].startswith('Bathroom')]
EXT_IDS = ['D02', 'D12', 'D28']
assert len(INT_IDS) == 17 and len(BATH_IDS) == 7
DD = {d[0]: d for d in DOORS}
def door_int(w, h):
    ch_rft = 2 * (h + 0.25) + (w + 0.5)
    sw, sh = w - 0.33, h - 0.17
    fr_len = 2 * sh + 3 * (sw - 0.67)
    infill = max(0.0, (sw - 0.67) * (sh - 1.0))
    ar_rft = 2 * (2 * (h + 0.2) + (w + 0.4))
    return dict(ch_rft=ch_rft, ch=ch_rft * 4.5 * 2.5 / 144, sh=fr_len * 4 * 1.5 / 144, core=0.5 * infill, skin=2 * sw * sh,
                ven=2 * sw * sh, ar=ar_rft * 2.5 * 0.75 / 144,
                pu=2 * sw * sh + 2 * (sw + sh) * 1.5 / 12 + ch_rft * (4.5 + 2 * 2.5) / 12 + ar_rft * (2.5 + 2 * 0.75) / 12,
                size='%s x %s' % (ftin(sw), ftin(sh)))
def door_main(w, h):
    ch_rft = 2 * (h + 0.25) + (w + 0.5)
    sw, sh = w - 0.42, h - 0.21
    ar_rft = 2 * (2 * (h + 0.3) + (w + 0.6))
    return dict(ch_rft=ch_rft, ch=ch_rft * 7 * 3 / 144, sh=sw * sh * 2.5 / 12 * 0.85, ar=ar_rft * 3.5 * 1.0 / 144,
                pu=2 * sw * sh + 4 * (sw / 2 + sh) * 2.5 / 12 + ch_rft * (7 + 2 * 3) / 12 + ar_rft * (3.5 + 2 * 1.0) / 12,
                size='2 leaves %s x %s' % (ftin(sw / 2), ftin(sh)))
DW = OrderedDict()
d1 = DD['D01']; DW['D01'] = door_main(d1[4], d1[5])
for i in INT_IDS: DW[i] = door_int(DD[i][4], DD[i][5])
CH_CFT = sum(v['ch'] for v in DW.values())
SH_INT = sum(DW[i]['sh'] for i in INT_IDS)
AR_CFT = sum(v['ar'] for v in DW.values())
W_WOOD = 0.25
add('S8', 'DIYAR', CH_CFT, W_WOOD, 'Diyar chowkats: main door 7" x 3" (%s cft) + 17 internal doors 4 1/2" x 2 1/2" (%s cft) - buy before plaster' % (
    f2(DW['D01']['ch']), f1(CH_CFT - DW['D01']['ch'])))
add('S8', 'DIYAR', DW['D01']['sh'], W_WOOD, 'Diyar for the main-door leaves, solid panelled 2 1/2" (%s cft)' % f2(DW['D01']['sh']))
add('S8', 'DIYAR', SH_INT, W_WOOD, 'Diyar stiles and rails 4" x 1 1/2" for 17 semi-solid shutters (%s cft)' % f1(SH_INT))
add('S8', 'DIYAR', AR_CFT, W_WOOD, 'Diyar architraves both faces: main door 3 1/2" x 1", internal 2 1/2" x 3/4" (%s cft)' % f2(AR_CFT))
add('S8', 'PLY25', sum(DW[i]['core'] for i in INT_IDS) / 32.0, 0.10, 'Ply core strips 25 mm at 50% fill, 17 shutters')
add('S8', 'PLY6', sum(DW[i]['skin'] for i in INT_IDS) / 32.0, 0.10, 'Ply skins 6 mm both faces, 17 shutters')
add('S8', 'VEN', sum(DW[i]['ven'] for i in INT_IDS), 0.15, 'Veneer both faces, 17 shutters')
add('S8', 'DGLUE', 18, 0.0, 'Glue, nails, filler: main door + 17 internal doors')
PU_SFT = sum(v['pu'] for v in DW.values())
add('S8', 'PU', PU_SFT, 0.05, 'PU polish on shutters, edges, chowkats and architraves (18 doors) %s sft' % f0(PU_SFT))
add('S8', 'WPCD', len(BATH_IDS), 0.0, RATES['WPCD']['name'] + ' - 7 bathroom doors')
add('S8', 'STD', len(EXT_IDS), 0.0, RATES['STD']['name'] + ' - D02, D12, D28')
add('S8', 'LKMAIN', 1); add('S8', 'CLOSER', 1); add('S8', 'HBB5', 8, 0.0, 'SS ball-bearing hinges, 4 per leaf (main door)')
add('S8', 'FBOLT', 1); add('S8', 'STOPH', 2 + len(EXT_IDS), 0.0, 'Heavy floor stoppers: main door 2 + external doors 3'); add('S8', 'VIEWER', 1)
add('S8', 'LKEXT', len(EXT_IDS))
add('S8', 'LKINT', len(INT_IDS)); add('S8', 'LKBATH', len(BATH_IDS))
add('S8', 'HSS4', 3 * (len(INT_IDS) + len(BATH_IDS)), 0.0, 'SS hinges 4", 3 per door (17 internal + 7 bath)')
add('S8', 'STOP', len(INT_IDS) + len(BATH_IDS)); add('S8', 'TBOLT', len(INT_IDS))

# ============================================================== STAGE 9: windows, glass, nets, grills
def gtype(ref):
    if ref in ('W06', 'W07', 'W09'): return 'G66L'
    if ref.startswith('V'): return 'G5F'
    return 'G5C'
WINR = []
for x in WROWS:
    t = x['t']; w, h = x['w'], x['h']
    if t == 'SLT': net = (w / 2) * (h - 2.0)
    elif t == 'SL': net = (w / 2) * h
    else: net = 0.0
    hw = {'SLT': 'WACS', 'SL': 'WACS', 'FXT': 'WACF', 'TH': 'WACV', 'SF': 'WACSF'}[t]
    vents = 2 if (t == 'SF' and h > 15) else 0
    WINR.append(dict(ref=x['ref'], fl=x['fl'], room=x['room'], elev=x['elev'], w=w, h=h, t=t, n=x['n'], kg=x['kg'],
                     glass=x['glass'], g=gtype(x['ref']), net=net, hw=hw, vents=vents))
d27 = DD['D27']
WINR.append(dict(ref='D27', fl='FF', room='F12', elev='Front (terrace)', w=d27[4], h=d27[5], t='SD', n=1, kg=A['kg_sd'], glass=A['gl_sd'],
                 g='G6T', net=(d27[4] / 2) * d27[5], hw='WACD', vents=0))
GRILL = ['W01', 'W02', 'W03', 'W04', 'W05', 'V01', 'V02', 'V03', 'W08', 'W14']
GRILL_KG_SFT = 1.5
for x in WINR:
    x['grill'] = x['w'] * x['h'] * x['n'] if x['ref'] in GRILL else 0.0
ALU_KG = sum(x['kg'] * x['n'] for x in WINR)
assert abs(ALU_KG - A['ALU_TOTAL']) < 0.01
add('S9', 'ALU', ALU_KG, 0.05, 'Aluminium sections for 17 windows, 7 ventilators and sliding door D27: %s kg (Step A weight model)' % f0(ALU_KG))
for hk in ('WACS', 'WACF', 'WACV', 'WACSF', 'WACD'):
    n = sum(x['n'] for x in WINR if x['hw'] == hk) + (sum(x['vents'] for x in WINR) if hk == 'WACV' else 0)
    if n: add('S9', hk, n)
for gk, lab in [('G5C', 'clear windows'), ('G5F', 'bathroom ventilators'), ('G66L', 'tall units W06, W07, W09'), ('G6T', 'sliding door D27')]:
    s = sum(x['glass'] * x['n'] for x in WINR if x['g'] == gk)
    add('S9', gk, s, 0.05 if gk in ('G5C', 'G5F') else 0.0, '%s - %s %s sft' % (RATES[gk]['name'], lab, f1(s)))
PERIM_FT = sum(2 * (x['w'] + x['h']) * x['n'] for x in WINR)
add('S9', 'SIL', PERIM_FT / 15.0, 0.10, 'Silicone: outside perimeter of all frames %s rft (15 rft per cartridge)' % f0(PERIM_FT))
NET_SFT = sum(x['net'] * x['n'] for x in WINR)
add('S9', 'MESH', NET_SFT, 0.10, 'Fly-net sashes on all sliding windows and D27: %s sft' % f1(NET_SFT))
GR_SFT = sum(x['grill'] for x in WINR)
add('S9', 'MS', GR_SFT * GRILL_KG_SFT, 0.07, 'MS grills inside GF windows, GF bath vents and stair windows: %s sft x 1.5 kg/sft' % f1(GR_SFT))
N_GRILL = sum(x['n'] for x in WINR if x['grill'])
add('S9', 'RAWL', 6 * N_GRILL, 0.0, 'Rawl bolts, 6 per grill (%d grills)' % N_GRILL)

# ============================================================== STAGE 10: paint
PUTTY_2C, PUTTY_1C = 0.085, 0.045        # kg per sft
PRIM_COV, EMUL_COV, WS_COV, PRIME_COV = 350.0, 180.0, 150.0, 300.0   # sft per gallon (emulsion / Weathershield: 2 coats)
TEX_KG = 0.15
ACCENT = {'G03': ('TD', 13.0 * 10.0), 'F13': ('TD', 14.0 * 10.0), 'G06': ('DD', 12.0 * 10.0), 'F07': ('DD', 14.0 * 10.0),
          'F04': ('TM', 12.0 * 10.0), 'S02': ('TM', 11.0 * 8.5)}
TVW = {'G13': 15.0 * 10.0, 'F10': 14.75 * 10.0}
LIVING = ('G02', 'G09', 'G13', 'G14', 'G15', 'F02', 'F03', 'F10')
INT = []     # (room, area, colour, note)
for k, v in A['PAINT'].items():
    if k == 'STAIR':
        INT.append(('STAIR', v['net'], 'NH', 'stair well walls, GF to mumty ceiling')); continue
    base = 'EC' if k in LIVING else 'JW'
    rest = v['net']
    if k in ACCENT:
        c, a = ACCENT[k]; INT.append((k, a, c, 'accent wall (bed-head wall)')); rest -= a
    if k in TVW:
        INT.append((k, TVW[k], 'CS', 'TV wall')); rest -= TVW[k]
    INT.append((k, rest, base, 'other walls'))
INT_WALLS = sum(a for _, a, _, _ in INT)
assert abs(INT_WALLS - A['int_tot']) < 0.01
SOFF_ST = A['STAIR_SOFFIT']
CEIL = FC_ALL + COVE_SFT
EXT = []     # (surface, area, colour, system)
for e, v in A['EXTP'].items():
    band = sum(v['lens'].values()) * 1.0
    plinth = v['lens'].get('GF', 0.0) * 1.75
    EXT.append((e + ' - walls', v['net'] - band - plinth, 'JW', 'WS'))
    if plinth: EXT.append((e + ' - exposed plinth ("kursi") 1\'-9"', plinth, 'UO', 'WS'))
    EXT.append((e + ' - slab-edge bands 1\'-0"', band, 'UO', 'TEX'))
PAR = A['PARAPET']
EXT.append(('Parapets - outer face', PAR * 0.45, 'JW', 'WS'))
EXT.append(('Parapets - inner face and top', PAR * 0.55, 'NJ', 'WS'))
EXT.append(('External soffits (porch, canopy, chajjas)', A['SOFFIT'], 'BW', 'WS'))
PIL_FACE = 7 * (13.5 / 12) * 6.5 * 2 + 3 * 4.0 * 6.5 * 2
PIL_TEX = PIL_FACE + A['pillars_extra']
BW_IN = A['bin_'] + A['coping_top'] + A['pillars_extra'] / 2
BW_OUT = A['bout'] + A['pillars_extra'] / 2
BW_NEI = A['bnei']
EXT.append(('Boundary walls - inside faces', BW_IN - PIL_TEX / 2 - A['coping_top'], 'NJ', 'WS'))
EXT.append(('Boundary walls - street and gali faces', BW_OUT - PIL_TEX / 2 - BW_NEI, 'NJ', 'WS'))
EXT.append(('Boundary walls - coping top', A['coping_top'], 'UO', 'WS'))
EXT.append(('Boundary pillars (10) - all faces', PIL_TEX, 'UO', 'TEX'))
EXT_ALL = sum(a for _, a, _, _ in EXT)
assert abs(EXT_ALL - (A['ext_tot'] + BW_IN + BW_OUT - BW_NEI)) < 0.01
GRILL_PAINT = GR_SFT * 1.2
PUTTY_KG = (INT_WALLS + SOFF_ST) * PUTTY_2C + CEIL * PUTTY_1C
add('S10', 'PUTTY', PUTTY_KG, 0.05, 'Putty: 2 coats on %s sft of walls and stair soffits (0.085 kg/sft), 1 skim coat on %s sft of gypsum ceilings' % (
    f0(INT_WALLS + SOFF_ST), f0(CEIL)))
add('S10', 'PRIMI', (INT_WALLS + SOFF_ST + CEIL) / PRIM_COV, 0.05, 'Interior primer 1 coat on %s sft (350 sft/gal)' % f0(INT_WALLS + SOFF_ST + CEIL))
EM = defaultdict(float)
for _, a, c, _ in INT: EM[c] += a
EM['BW'] += CEIL + SOFF_ST
for c in CLR:
    if EM.get(c): add('S10', 'EM' + c, EM[c] / EMUL_COV, 0.05, 'Emulsion %s - %s sft, 2 coats (180 sft/gal)' % (cname(c), f0(EM[c])))
EXT_PRIM = EXT_ALL
add('S10', 'PRIME', EXT_PRIM / PRIME_COV, 0.05, 'Exterior primer 1 coat on %s sft (300 sft/gal)' % f0(EXT_PRIM))
WS = defaultdict(float); TX = defaultdict(float)
for _, a, c, s in EXT:
    (WS if s == 'WS' else TX)[c] += a
for c in CLR:
    if WS.get(c): add('S10', 'WS' + c, WS[c] / WS_COV, 0.05, 'Weathershield %s - %s sft, 2 coats (150 sft/gal)' % (cname(c), f0(WS[c])))
TEX_SFT = sum(TX.values())
add('S10', 'TEX', TEX_SFT * TEX_KG, 0.05, 'Texture coat tinted %s on bands and boundary pillars - %s sft at 0.15 kg/sft' % (cname('UO'), f0(TEX_SFT)))
add('S10', 'ROX', GRILL_PAINT / 400.0, 0.05, 'Red-oxide primer on grills %s sft (400 sft/gal)' % f0(GRILL_PAINT))
add('S10', 'ENAM', GRILL_PAINT / 200.0, 0.05, 'Enamel 2 coats on grills (200 sft/gal for 2 coats)')
add('S10', 'PSUND', 1)

# ============================================================== STAGE 11: electrical second fix
SWR = OrderedDict()
for k, (dl, deco, fan, ex, ac, s5, p15, lv, sb, note) in EP.items():
    ls = (math.ceil(dl / 4) if dl else 0) + (1 if deco else 0) + fan + ex + (2 if k in COVE_ROOMS else 0)
    tw = {'G01': 1, 'F01': 2, 'S01': 1}.get(k, 0) + (2 if k in ('G03', 'G06', 'F04', 'F07', 'F13', 'S02') else 0)
    SWR[k] = dict(sw1=ls, sw2=tw, s5=s5, p15=p15, sb=sb, dp=(1 if ac else 0))
N_SW1 = sum(v['sw1'] for v in SWR.values()) + 8
N_SW2 = sum(v['sw2'] for v in SWR.values())
N_S5 = sum(v['s5'] for v in SWR.values()) + cnt['S5ext']
N_P15 = sum(v['p15'] for v in SWR.values())
N_DP = 10 + 3
N_PLATE = cnt['SB'] + cnt['SBext']
N_PLATES = max(0, N_S5 + N_P15 - N_PLATE) + N_DP
add('S11', 'SW1', N_SW1, 0.0, 'Switches 1-way: lights, fans, exhausts, cove and profile circuits + 8 outdoor')
add('S11', 'SW2', N_SW2, 0.0, 'Switches 2-way: stairs and bed-heads')
add('S11', 'SKT5', N_S5, 0.0, 'Sockets 5 A: %d indoor + %d outdoor' % (N_S5 - cnt['S5ext'], cnt['S5ext']))
add('S11', 'SKT15', N_P15); add('S11', 'DP20', N_DP, 0.0, 'DP switches 20 A: 10 ACs + 3 geysers')
add('S11', 'PLATE', N_PLATE, 0.0, 'Switch-board plates: %d indoor + %d outdoor boards' % (cnt['SB'], cnt['SBext']))
add('S11', 'PLATES', N_PLATES); add('S11', 'WPCOV', cnt['S5ext']); add('S11', 'BELL', 2)
LT = OrderedDict()
for k, (dl, deco, fan, ex, ac, s5, p15, lv, sb, note) in EP.items():
    cove = prof = 0.0
    if k in COVE_ROOMS:
        cove = 2 * (R[k]['L'] + R[k]['W']) * 0.3048
        prof = 2 * (R[k]['L'] - 3.0) * 0.3048
    LT[k] = dict(dl=dl, cove=cove, prof=prof, fan=fan, ex=ex, deco='')
DECO_FIT = {'G02': ('CHAND', 'chandelier'), 'G14': ('CHAND', 'chandelier'), 'G09': ('PENDC', 'pendant cluster over the table'),
            'G15': ('PENDL', 'double-height pendant'), 'F03': ('PEND', 'pendant at the front glazing'), 'F01': ('WLT', '3 stair wall lights'),
            'G11': ('UCAB', 'under-cabinet LED'), 'F12': ('UCAB', 'under-cabinet LED'), 'G13': ('TVL', 'TV-wall LED wash'), 'F10': ('TVL', 'TV-wall LED wash')}
for k, (key, lab) in DECO_FIT.items(): LT[k]['deco'] = lab
for k in BATHS: LT[k]['deco'] = 'LED mirror (Stage 6)'
COVE_TOT = sum(v['cove'] for v in LT.values()); PROF_TOT = sum(v['prof'] for v in LT.values())
N_DRV = sum(math.ceil(v['cove'] * 9.6 / 80) + 1 for k, v in LT.items() if k in COVE_ROOMS) + 1
add('S11', 'DL12', cnt['DL'], 0.0, 'LED downlights 12 W, %d nos (warm white 3000 K in bedrooms, 4000 K elsewhere)' % cnt['DL'])
add('S11', 'STRC', COVE_TOT / 5.0, 0.05, 'Cove LED strip: %s m in 5 rooms (drawing, 2 lounges, 2 master bedrooms)' % f1(COVE_TOT))
add('S11', 'PROF', PROF_TOT / 2.0, 0.05, 'Recessed aluminium profiles: 2 lines per cove room, %s m' % f1(PROF_TOT))
add('S11', 'STRP', PROF_TOT / 5.0, 0.05, 'COB strip inside the profiles')
add('S11', 'DRV', N_DRV, 0.0, 'LED drivers 24 V 100 W: cove (1 per 8 m) + profiles + front elevation')
for key in ('CHAND', 'PENDL', 'PENDC', 'PEND'):
    n = sum(1 for k, v in DECO_FIT.items() if v[0] == key)
    add('S11', key, n)
add('S11', 'WLT', 3); add('S11', 'UCAB', 2); add('S11', 'TVL', 2)
EXT_FIT = [('Front car porch', 'PORCH', 4), ('Rear car porch + rear passage', 'BULK', 3), ('Left passage + lawn', 'OWL', 5),
           ('Left passage + lawn', 'LAWN', 3), ('Gates and boundary pillars', 'PIL', 4), ('Terrace and mumty roof', 'BULK', 4),
           ('Front balcony (FF kitchen terrace)', 'OWL', 1)]
EXTF = defaultdict(int)
for _, kk, n in EXT_FIT: EXTF[kk] += n
for kk in ('PORCH', 'BULK', 'OWL', 'LAWN', 'PIL'): add('S11', kk, EXTF[kk])
PROFX_M = 3 * 3.0
add('S11', 'PROFX', PROFX_M, 0.0, 'Front-elevation LED profiles, 3 runs of 3 m (sheet 09)')
add('S11', 'PHOTO', 2)
add('S11', 'FAN', cnt['F'], 0.0, RATES['FAN']['name'] + ' - %d rooms + front porch' % (cnt['F'] - 1))
add('S11', 'EXH8', len(BATHS), 0.0, RATES['EXH8']['name'] + ' - 6 baths + powder room')
add('S11', 'EXH12', 2, 0.0, RATES['EXH12']['name'] + ' - raw kitchen and FF kitchen')
add('S11', 'AC15', N15, 0.0, RATES['AC15']['name'] + ' - %d rooms' % N15)
add('S11', 'AC20', N20, 0.0, RATES['AC20']['name'] + ' - %d rooms' % N20)
add('S11', 'DECO3', 1); add('S11', 'DECO1', 1); add('S11', 'GSW8', 1)
add('S11', 'NVR8', 1); add('S11', 'IPC4', A['CCTV_N']); add('S11', 'HDD2', 1)
add('S11', 'EVC', 1)

# ============================================================== STAGE 12: external works
A_FP, A_RP = A['OUT_AREAS'][0][1], A['OUT_AREAS'][1][1]
A_PASS, A_RAMP, A_PATIO = A['OUT_AREAS'][2][1], A['OUT_AREAS'][3][1], A['OUT_AREAS'][4][1]
TRK_FP = 0.5 * A_FP                       # wheel tracks of 2 cars + driveway strip (half the front porch)
TRK_RP = 2 * 2.0 * 16.8                   # 2 tracks x 2'-0" x 16'-9 1/2" (one car)
PAVE = [('Front car porch + driveway strip - car tracks', TRK_FP, 'TUF80'), ('Front car porch - rest', A_FP - TRK_FP, 'TUF60'),
        ('Rear car porch - car tracks', TRK_RP, 'TUF80'), ('Rear car porch - rest', A_RP - TRK_RP, 'TUF60'),
        ('Ramps at main and side gates (both used by cars)', A_RAMP, 'TUF80'), ('Left and rear passages', A_PASS, 'TUF60'),
        ('Patio beside the dining', A_PATIO, 'TUF60')]
T60 = sum(a for _, a, k in PAVE if k == 'TUF60'); T80 = sum(a for _, a, k in PAVE if k == 'TUF80')
add('S12', 'TUF60', T60, 0.05, 'Tuff tiles 60 mm: porch areas off the tracks, passages, patio %s sft' % f1(T60))
add('S12', 'TUF80', T80, 0.05, 'Tuff tiles 80 mm: car tracks and both ramps %s sft' % f1(T80))
add('S12', 'SNDC', (T60 + T80) * (2 / 12.0 + 0.01), 0.10, 'Chenab sand: 2" bedding + joint filling')
def gate_kg(w, h, leaves, wicket):
    lw = w / leaves
    frame = leaves * 2 * (lw + h) * 0.3048 * 4.7
    members = leaves * 4 * lw * 0.3048 * 1.9 + leaves * h * 0.3048 * 1.9
    wick = 2 * (3.0 + 6.0) * 0.3048 * 3.5 if wicket else 0.0
    sheet = w * h * 0.092903 * 11.8
    return (frame + members + wick + sheet) * 1.10
GATE = [('Main gate 12\'-9" x 6\'-6", 2 leaves with pedestrian wicket', 12.75, 6.5, 2, True, 'GHWM', A['GATES'][0]),
        ('Side gate 7\'-8 1/4" x 7\'-0", 2 leaves', 7.69, 7.0, 2, False, 'GHWS', A['GATES'][1])]
GKG = [gate_kg(w, h, lv, wk) for _, w, h, lv, wk, _, _ in GATE]
add('S12', 'GSTL', sum(GKG), 0.07, 'MS for gates: main %s kg + side %s kg (2"x4" 14 g frames, 1 1/2" 16 g members at 18", 16 g sheet one face)' % (
    f0(GKG[0]), f0(GKG[1])))
add('S12', 'GHWM', 1); add('S12', 'GHWS', 1)
G_PC = sum(2 * g[1] * g[2] * 1.1 for g in GATE)
add('S12', 'PCOAT', G_PC, 0.0, 'Powder coating both faces of both gates, RAL 7016 anthracite - %s sft' % f0(G_PC))
RAIL = [('Stair-well guard rail at the mumty floor edge', 14.0, 3.0, 2.5), ('Front balcony (FF kitchen terrace)', 15.0, 3.5, 3.0)]
N_POST = sum(math.ceil(L / 4.0) + 1 for _, L, _, _ in RAIL)
N_PANEL_G = sum(math.ceil(L / 4.0) for _, L, _, _ in RAIL)
G12_SFT = sum(L * gh for _, L, _, gh in RAIL)
add('S12', 'SSPOST', N_POST, 0.0, 'SS 304 posts at 4 ft maximum (%d)' % N_POST)
add('S12', 'SSTR', sum(L for _, L, _, _ in RAIL), 0.05)
add('S12', 'G12T', G12_SFT, 0.0, 'Toughened glass 12 mm panels made to size: %s sft' % f1(G12_SFT))
add('S12', 'GCLMP', 4 * N_PANEL_G, 0.0, 'Glass clamps, 4 per panel (%d panels)' % N_PANEL_G)
add('S12', 'RAWL', 4 * N_POST, 0.0, 'Anchor bolts, 4 per post')
add('S12', 'TANK', 1); add('S12', 'TANKF', 1)
add('S12', 'PUMP', 1); add('S12', 'PCTRL', 1); add('S12', 'PFIT', 1)

# ============================================================== totals
ST = OrderedDict((s, stage_total(s)) for s in STAGES)
TOTAL = sum(ST.values())
TOTAL_CHECK = sum(l['amt'] for s in STAGES for l in LINES[s])
assert TOTAL == TOTAL_CHECK
EST_AMT = sum(l['amt'] for s in STAGES for l in LINES[s] if RATES[l['key']]['src'].startswith('estimated'))

# ============================================================== optional items (not in total)
STAIR_HR = 2 * (R0.g1 + R0.g2)
OPT = [
 ('TV feature walls in both lounges (297.5 sft): 2\'x4\' porcelain slab or WPC fluted panels instead of paint', 297.5 * 1.1 * 420),
 ('Front-elevation "wooden tile" cladding on sheet 09 (about 96 sft)', 96 * 1.1 * 450),
 ('Lockable louvred aluminium door / screen for the laundry (protects the inverter and battery)', 55000),
 ('Solar water heater 150 litres on the mumty roof (cuts geyser gas and electricity)', 95000),
 ('Lightning conductor on the mumty roof with Type 1 surge protector (earth pit is in grey)', 45000),
 ('Paint on the neighbour-facing boundary faces (%s sft)' % f0(BW_NEI), BW_NEI * (1 / 300.0 * 3335 + 1 / 150.0 * 5900) * 1.05),
 ('SS wall-mounted handrail on both stair flights (%s rft)' % f0(STAIR_HR), STAIR_HR * 1200),
 ('Curtain track or glass partition at the FF TV lounge open side (helps the 2-ton AC)', 25000),
 ('Philips / Ledvance downlights instead of good local make (133 nos)', 133 * 800),
 ('3-burner built-in hob for the raw kitchen (Canon)', 18000),
]
LFP_SAVING = RATES['NAB5']['rate'] * N_BAT - 447200

# ============================================================== document blocks
B = []
def blk(**k): B.append(k)
def row(*c, kind=''): return dict(cells=[str(x) for x in c], kind=kind)
def table(header, widths, rows, align=None, font=8):
    blk(type='table', header=header, widths=widths, rows=rows, align=align or [], font=font)
PW, LW = 9906, 15038

def rate_str(r):
    if r['show'] == 'buy' and r['size'] != 1:
        return '%s per %s' % (f0(r['rate'] * r['size']), r['buy'].split(' (')[0])
    rr = r['rate']
    return '%s per %s' % (f0(rr) if (rr >= 100 or abs(rr - round(rr)) < 0.005) else f2(rr), r['unit'])
def buy_str(l):
    r = RATES[l['key']]
    if r['size'] == 1 or r['buy'] == r['unit']:
        u = r['unit']
        if u in ('set', 'sheet', 'pair', 'roll', 'litre', 'bag', 'coil') and abs(l['buy']) != 1: u += 's'
        return '%s %s' % (fq(l['buy']), u)
    head = r['buy'].split(' (')[0]; rest = r['buy'][len(head):]
    if abs(l['units']) != 1: head += 'es' if head.endswith(('x', 'ch', 'sh')) else 's'
    return '%s %s%s = %s %s' % (f0(l['units']), head, rest, fq(l['buy']), r['unit'])
def src_str(r):
    return 'estimated' if r['src'] == 'estimated' else r['src']
def boq(s, title=None):
    rows = []
    for l in LINES[s]:
        r = RATES[l['key']]
        rows.append(row(l['ref'], l['desc'], fq(l['net']), r['unit'], pct(l['w']), buy_str(l), rate_str(r), f0(l['amt']), src_str(r)))
    rows.append(row('', 'Stage %d total (purchase quantities x rates)' % SNUM[s], '', '', '', '', '', f0(ST[s]), '', kind='total'))
    blk(type='h2', text=title or '%d.%d Priced materials (wastage included, rounded up to buying units)' % (SECNO[s], 9))
    table(['Ref', 'Material, specification and where used', 'Net qty', 'Unit', 'Waste', 'Buy (buying units)', 'Rate (Rs)', 'Amount (Rs)', 'Rate source and date'],
          [550, 5200, 800, 500, 550, 2150, 1250, 1150, 2888], rows, ['C', 'L', 'R', 'C', 'C', 'L', 'R', 'R', 'L'], font=7)
def h1(s):
    blk(type='h1', text='%d. Stage %d - %s' % (SECNO[s], SNUM[s], STAGES[s][0]), newpage=True)
    blk(type='note', text='On site: ' + STAGES[s][1])

# ---------------------------------------------------------------- title and summary (portrait)
blk(type='section', orientation='PORTRAIT')
blk(type='title', title='House No. 79/K, WAPDA City, Faisalabad', size=34, before=0,
    subtitle='FINISHING estimate - Step B: priced materials, no labour  |  Faisalabad / Lahore rates, Oct 2026')
blk(type='keys', keys=[('Finishing materials', 'Rs %s' % f0(TOTAL), '12 site stages, wastage included'),
                       ('Per sft covered area', 'Rs %s' % f0(TOTAL / COVERED), 'on %s sft' % f0(COVERED)),
                       ('Grey + finishing', 'Rs %s' % f0(TOTAL + GREY_TOTAL), 'grey Rev 1 Rs %s' % f0(GREY_TOTAL)),
                       ('Combined per sft', 'Rs %s' % f0((TOTAL + GREY_TOTAL) / COVERED), 'materials only')])
blk(type='h1', text='1. Summary: cost by category (in site order)')
sr = []
for s in STAGES:
    sr.append(row(SNUM[s], STAGES[s][0], f0(ST[s]), '%.1f%%' % (100 * ST[s] / TOTAL), f0(ST[s] / COVERED)))
sr.append(row('', 'GRAND TOTAL - finishing materials', f0(TOTAL), '100%', f0(TOTAL / COVERED), kind='total'))
table(['Stage', 'Category', 'Amount (Rs)', 'Share', 'Rs per sft'], [700, 5306, 1600, 1000, 1300], sr, ['C', 'L', 'R', 'R', 'R'], font=9)
blk(type='bullets', size=17, items=[
    'Material only: no labour, fabrication, fixing, transport or tools. Retail prices for Faisalabad / Lahore, October 2026; GST is included in the prices.',
    'Quantities are the Step A measurements with stated cutting/handling wastage, rounded UP to buying units (boxes, coils, bags, gallons, sheets, lengths).',
    'Every rate shows its source and date; %d%% of the total (Rs %s) rests on rates marked "estimated" - get 2-3 quotations for those before buying.' % (
        round(100 * EST_AMT / TOTAL), f0(EST_AMT)),
    'All 40 questionnaire answers are applied (Section 16). Optional items are listed in Section 15 and are NOT in the total.',
    'As instructed on 3 Oct 2026, this estimate is issued as this Word file only (no Excel workbook).'])

# ---------------------------------------------------------------- 2. basis and site order
blk(type='h1', text='2. Basis and site order', newpage=True)
blk(type='h2', text='2.1 Inputs')
blk(type='bullets', size=17, items=[
    'Measurements: Finishing Step A (schedules of 35 rooms, 30 doors + arch, 17 windows + 7 ventilators, tiles, paint, false ceilings, electrical points, solar).',
    'Owner\'s answers to the 40 Step A questions (answered file of 3 Oct 2026); blank answers = the recommended default.',
    'Binding grey decisions (Rev 1): floor finish within 1 1/2" over the 3" PCC; no ceiling plaster (all ceilings are false ceilings); roof tiles, conduits, back boxes, '
    'earth pits, solar plinths, UPVC floor-trap bodies, PPR and gas pipes are already in the grey estimate and are not repeated here.',
    'Orientation: front (road) side taken as south, as in the grey solar layout. It drives the AC sizing and the panel direction.'])
blk(type='h2', text='2.2 Site order of the 12 stages')
so = [row(SNUM[s], STAGES[s][0], STAGES[s][1]) for s in STAGES]
table(['Stage', 'Work', 'When on site'], [700, 3900, 5306], so, ['C', 'L', 'L'], font=8)
blk(type='note', text='Stages overlap on site. Each one is placed where its first material is needed. Buy the Diyar chowkats (Stage 8) and the DB boards (Stage 1) '
    'before the internal plaster, because they are fixed into the walls.')
blk(type='h2', text='2.3 How quantities become purchases')
blk(type='bullets', size=17, items=[
    'Net qty = measured quantity. Gross = net x (1 + wastage). Purchase = gross rounded UP to whole buying units. Amount = purchase x rate.',
    'Tile boxes: 2\'x4\' (600 x 1200) 2 pcs, 600 x 600 4 pcs and 300 x 600 8 pcs all hold 1.44 m2 = 15.5 sft per box.',
    'Cutting wastage: large floor tiles 8%, skirting strips, bath and wall tiles 10%, stone 10-20%, wire 10%, paint 5%, Diyar wood 25% (conversion and planing), gypsum boards 7-10%.',
    'Wire is bought in 90 m coils for 1.5, 2.5 and 4 mm2 (each colour separately); 6, 10 and 16 mm2 are bought as cut lengths.'])

# ---------------------------------------------------------------- STAGE 1 (landscape)
blk(type='section', orientation='LANDSCAPE')
s = 'S1'; h1(s)
blk(type='p', size=17, text='Scheme: wires ("taar") in the grey conduits; FESCO 3-phase supply, meter at the front; 4-core 16 mm2 armoured cable to the GF main DB (grid side) with a 63 A 4-pole MCCB, '
    'Type 2 surge protector and 30 mA RCCBs. The main DBs feed the ACs, 15 A power points, geysers, EV charger and the hybrid inverter\'s grid port. The inverter\'s '
    'load (backup) port feeds the GF, FF and mumty backup DBs (lights, fans, 5 A sockets, fridges, pump, Wi-Fi and cameras), as in grey Register J5. A manual 4-pole '
    'changeover lets the backup DBs run straight from the grid when the inverter is serviced.')
blk(type='p', size=17, text='Maximum demand with the AC sizes worked out in Stage 11: %s kW (Step A %s kW) = %s A per phase at 400 V, 0.9 p.f. The 63 A incomer '
    'and 4 x 16 mm2 cable remain adequate. The hybrid geysers\' electric elements are a winter load and do not coincide with the AC peak.' % (
        f1(MD_NEW / 1000), f1(A['MD'] / 1000), f0(I_NEW)))
blk(type='h2', text='%d.1 Circuit list by DB' % SECNO[s])
cr = []
for db, dbn in DBN.items():
    cr.append(row(dbn, kind='section'))
    groups = OrderedDict()
    for c in CIRC:
        if c['db'] != db: continue
        key = (c['name'], c['size'], c['esize'], c['mcb'])
        g = groups.setdefault(key, dict(n=0, pts=c['pts'], route=0.0, ph=[]))
        g['n'] += 1; g['route'] += c['route']; g['ph'].append(c['ph'])
    for (nm, sz, es, mcb), g in groups.items():
        cr.append(row(nm, g['n'], g['pts'], '%g + %g mm2 earth' % (sz, es), mcb, ', '.join(g['ph']), f0(g['route'])))
cr.append(row('Sub-mains and feeders', kind='section'))
for (nm, sz, es, rt_, phs, brk) in SUBMAINS:
    cr.append(row(nm, 1, '-', '%d x %g + %g mm2 earth' % (len(phs) + 1, sz, es), brk, phs if len(phs) > 1 else phs, f0(rt_)))
cr.append(row('FESCO meter to GF main DB', 1, '-', '4-core 16 mm2 armoured', 'MCCB 63 A 4-pole', 'RYB', f0(METER_RUN)))
cr.append(row('Earth leads from the 3 grey earth pits', 3, '-', '16 mm2 green/yellow', '-', '-', f0(EARTH_LEADS)))
cr.append(row('Final circuits', len(CIRC), '', '', '', '', f0(sum(c['route'] for c in CIRC)), kind='total'))
table(['Circuit', 'No.', 'Points', 'Cable (live + neutral, earth)', 'Breaker', 'Phase', 'Route (m)'], [5100, 600, 1700, 2700, 2200, 1100, 1638], cr,
      ['L', 'C', 'C', 'L', 'L', 'C', 'R'], font=7)
blk(type='note', text='Route lengths: downlights 2.0 m, fans 5 m, exhausts and decorative points 4 m, switch-board loops 6 m, sockets 3 m + 12 m home run per circuit, '
    '15 A circuits 17 m, ACs on the grey conduit runs (GF 45 ft, FF 30 ft, mumty 40 ft), 2-way strappers on stairs and bed-heads. Each route carries live + neutral + earth.')
blk(type='h2', text='%d.2 Wire by size and colour, in coils' % SECNO[s])
blk(type='p', size=17, text='Recommended brand: Pakistan Cables "registered" single-core PVC copper, 450/750 V (Fast Cables or Newage are equal alternatives, Q28). '
    'Colours: phases red / yellow / blue (each circuit keeps the colour of its phase, so a mixed-phase board is visible at once), neutral black, earth green. '
    'Quantities include 10% for loops, drops and terminations.')
wr_ = []
for sz in (1.5, 2.5, 4.0, 6.0, 10.0):
    cells = []
    tot_m = 0.0; tot_c = 0
    for c in COL:
        l = [x for x in LINES['S1'] if x['key'] == 'W%g%s' % (sz, c)]
        if l:
            l = l[0]
            if sz <= 4.0:
                cells.append('%s m' % f0(l['gross']) + LS + '%d coils' % l['units']); tot_c += l['units']
            else:
                cells.append('%s m' % f0(l['buy']))
            tot_m += l['gross']
        else:
            cells.append('-')
    buy = ('%d coils x 90 m' % tot_c) if sz <= 4.0 else '%s m cut' % f0(sum(x['buy'] for x in LINES['S1'] if x['key'].startswith('W%g' % sz) and x['key'][len('W%g' % sz):] in COL))
    wr_.append(row('%g mm2' % sz, *cells, f0(tot_m), buy))
wr_.append(row('16 mm2', '-', '-', '-', '-', 'g/y %s m' % f0(EARTH_LEADS * 1.1), f0(EARTH_LEADS * 1.1), 'cut length'))
table(['Size', 'Red', 'Yellow', 'Blue', 'Black', 'Green', 'Total m (gross)', 'Buy'], [1100, 1800, 1800, 1800, 1800, 1800, 1700, 3238], wr_,
      ['C', 'C', 'C', 'C', 'C', 'C', 'R', 'L'], font=7.5)
blk(type='h2', text='%d.3 DBs and protection' % SECNO[s])
dbr = [
 row('GF main (grid side)', 'TPN 12-way, 36 modules', 'MCCB 63 A 4P + Type 2 SPD 4P', '4P RCCB 40 A 30 mA on 15 A power', 'ACs 5, power 5, geyser 1 (SP MCBs); EV RCBO 40 A Type A; 4P 40 A to FF main; 4P 40 A to inverter grid port'),
 row('GF backup (inverter load port)', 'TPN 12-way, 36 modules', '4P MCB 40 A + 4P changeover 63 A (bypass)', '4P RCCB 40 A 30 mA on sockets', 'lighting 7, sockets 5, outdoor 3, pump 1, Wi-Fi/CCTV 1; 4P 32 A to FF backup'),
 row('FF main', 'TPN 8-way, 24 modules', '4P MCB 40 A', '4P RCCB 40 A 30 mA on 15 A power', 'ACs 4, power 3, geyser 1; DP 32 A to mumty main'),
 row('FF backup', 'TPN 8-way, 24 modules', '4P MCB 32 A', '4P RCCB 40 A 30 mA on sockets', 'lighting 7, sockets 4; DP 20 A to mumty backup'),
 row('Mumty main (phase B)', 'SPN 8-way', 'DP MCB 32 A', '2P RCCB 40 A 30 mA', 'AC 1, room power 1, washing machine 1, geyser 1'),
 row('Mumty backup (phase Y)', 'SPN 8-way', 'DP MCB 20 A', '2P RCCB 40 A 30 mA', 'lighting 2, sockets 1'),
]
table(['DB', 'Board', 'Incomer', 'Earth-leakage protection', 'Outgoing ways'], [2600, 2200, 3000, 2800, 4438], dbr, ['L', 'L', 'L', 'L', 'L'], font=7.5)
blk(type='note', text='The grey estimate (Rev 1, item 14.D) priced smaller empty enclosures (12/8/4-way main, 8/6/4-way backup). They are too small for this circuit list, '
    'so the boards above replace them and the grey allowance is credited in line %s. Fix these enclosures before plaster. Breakers: Chint NXB / NXBLE or equal (Q28).' % (
        [l['ref'] for l in LINES['S1'] if l['key'] == 'DBCR'][0]))
boq(s, '%d.4 Priced materials - Stage 1' % SECNO[s])

# ---------------------------------------------------------------- STAGE 2
s = 'S2'; h1(s)
blk(type='kv', lw=3400, size=17, lines=[
    ('Panels', '23 x 650 W N-type bifacial, tier-1 (Longi Hi-MO X10 / Jinko Tiger Neo / JA) = 14.95 kWp; two strings of 12 + 11; facing the road side (south), tilt 15 deg.'),
    ('Mounting structure', 'Galvanised steel tables bolted to the 34 grey RCC plinths (2 cast-in M12 J-bolts each) with base plates; layout as in grey Section 7.'),
    ('Hybrid inverter', '1 x 12 kW three-phase hybrid, 48 V battery, 2 MPPT (Deye SUN-12K-SG04LP3 class). DC/AC ratio 1.25. Grid port to the GF main DB; load port to the backup DBs.'),
    ('Battery (Q33)', 'Sodium-ion, 48 V class: 2 modules of about 5.3 kWh = about 10.6 kWh now, in a 3-slot rack with busbars sized for 3 modules; '
                      'add the 3rd module later for about 16 kWh. Sizing (Step A): essential night load 8.07 kWh -> 9.7 kWh needed; with one bedroom AC 12.97 kWh -> 15.7 kWh.'),
    ('DC side', '6 mm2 DC solar cable red/black, MC4 connectors, DC combiner box with 1,000 V isolator, Type 2 DC surge protector and gPV fuses.'),
    ('AC side and protection', 'Inverter AC box (grid and load 4P 40 A MCBs, AC surge protector); 10 mm2 sub-mains are in Stage 1; frames bonded to the solar earth pit (grey J7).'),
    ('FESCO net-metering', '3-phase bi-directional meter and application/testing allowance. Under the NEPRA Prosumer Regulations 2026 exported units are credited at the '
                           'net-billing rate (about Rs 10-11 per kWh), so the design favours self-use and battery storage.'),
])
blk(type='note', text='Sodium-ion packs are new in Pakistan and no retail price was found: Rs 55,000 per kWh is used (about 23%% above branded LFP). '
    'The pack\'s BMS must be on the inverter\'s approved list. If no compatible sodium-ion pack is available, a 10 kWh LFP pack (Rs 447,200, w11stop.com, Jul 2026) '
    'is the fall-back and saves about Rs %s.' % f0(LFP_SAVING))
boq(s, '%d.1 Priced materials - Stage 2' % SECNO[s])

# ---------------------------------------------------------------- STAGE 3
s = 'S3'; h1(s)
blk(type='p', size=17, text='System (Q27): 12.5 mm gypsum board on a GI frame (ceiling sections at 600 mm on intermediate channels at 1,200 mm, perimeter channel, '
    'hangers to the slab); moisture-resistant (green) board in the 7 baths and the laundry. Cove boxes with LED strips and recessed profile lights only in the drawing room, '
    'both TV lounges and both master bedrooms. Ceiling height 10\'-0" in GF/FF rooms, 8\'-6" in wet areas and the mumty.')
fr_ = []
for fl in FLOORS:
    fr_.append(row(FLN[fl], kind='section'))
    for k, v in FC.items():
        if R[k]['fl'] != fl: continue
        fr_.append(row(k, rn(k), ftin(R[k]['fc']), 'moisture-resistant' if v['kind'] == 'MR' else 'standard', f1(v['a']),
                       f1(v['cove']) if v['cove'] else '-', 'cove + profiles' if v['cove'] else ''))
fr_.append(row('', 'Standard board ceilings', '', '', f1(FC_STD), '', '', kind='subtotal'))
fr_.append(row('', 'Moisture-resistant board ceilings', '', '', f1(FC_MR), '', '', kind='subtotal'))
fr_.append(row('', 'All false ceilings (= Step A)', '', '', f1(FC_ALL), f1(COVE_RFT), '', kind='total'))
table(['Id', 'Room', 'Height', 'Board', 'Area (sft)', 'Cove (rft)', 'Lights'], [700, 4200, 1300, 2200, 1500, 1500, 3638], fr_,
      ['C', 'L', 'C', 'L', 'R', 'R', 'L'], font=7)
boq(s, '%d.1 Priced materials - Stage 3' % SECNO[s])

# ---------------------------------------------------------------- STAGE 4
s = 'S4'; h1(s)
blk(type='p', size=17, text='Floor ("farsh") tiles (Q1, Q2, Q3, Q6, Q7): one 2\'x4\' polished light marble-look porcelain everywhere except wet areas; the same series in matt in the 3 kitchens; '
    '4" skirting cut from the floor tile; 600 x 600 matt anti-slip in baths and laundry. Setting: 1" semi-dry 1:4 bed with a polymer-modified C2TE adhesive bond coat '
    '(back-buttering on 2\'x4\'), levelling clips, 2 mm joints with polymer grout. This fits the 1 1/2" floor-finish allowance over the grey PCC.')
blk(type='h2', text='%d.1 Tile schedule per area (all tile areas in the house)' % SECNO[s])
tr_ = []
def trow(area, tile, net, w, where):
    tr_.append(row(area, tile, f1(net), pct(w), f1(net * (1 + w)), '15.5', boxes(net, w), where))
for fl in FLOORS:
    trow('%s: rooms, lobbies, dresses, store, hall landing' % FLN[fl], '2\'x4\' polished', T24_ROOMS[fl], W_FLOOR, 'Stage 4')
    trow('%s: 4" skirting %s rft' % (FLN[fl], f0(T24_SK[fl])), '2\'x4\' polished (strips)', T24_SK[fl] * SK_YIELD, W_SK, 'Stage 4')
for k in KIT:
    trow('Kitchen floor - %s' % rn(k), '2\'x4\' matt', R[k]['area'], W_FLOOR, 'Stage 4')
trow('Kitchen skirting %s rft' % f0(KIT_SK), '2\'x4\' matt (strips)', KIT_SK * SK_YIELD, W_SK, 'Stage 4')
trow('Laundry floor', '600 x 600 matt anti-slip', LAUN_F, W_SMALL, 'Stage 4')
trow('Laundry dado 4 ft', '300 x 600 glazed', LAUN_W, W_WALL, 'Stage 4')
for k, v in BT.items():
    trow('%s - floor' % rn(k), '600 x 600 matt anti-slip', v['floor'], W_SMALL, 'Stage 6')
for k, v in BT.items():
    trow('%s - walls (plain %s + feature %s)' % (rn(k), f0(v['plain']), f0(v['feat'])), '300 x 600 glazed', v['wall'], W_WALL, 'Stage 6')
for k in KR:
    trow('%s - backsplash 2\'-0"' % rn(k), '300 x 600 glazed', A['WALLT'][k]['net'], W_WALL, 'Stage 7')
table(['Area', 'Tile', 'Net (sft)', 'Cutting waste', 'Gross (sft)', 'sft/box', 'Boxes', 'Priced in'], [5300, 2400, 1150, 1100, 1150, 900, 900, 2138], tr_,
      ['L', 'L', 'R', 'C', 'R', 'C', 'R', 'C'], font=7)
blk(type='note', text='Box counts per area are for issuing tiles on site; each purchase line rounds the whole quantity once. Skirting: 5 strips of 4" are cut from '
    'each 600 x 1200 tile (19.7 rft per tile). Stairs and thresholds are stone (Stage 5); porches, passages and ramps are tuff tiles (Stage 12).')
boq(s, '%d.2 Priced materials - Stage 4' % SECNO[s])

# ---------------------------------------------------------------- STAGE 5
s = 'S5'; h1(s)
blk(type='p', size=17, text='Q4 and Q38: granite treads with three anti-slip grooves (cut by the stone supplier) and white Ziarat marble risers and stepped skirting; '
    'granite 20 mm (Tropical / Black Galaxy class) for window sills, door thresholds and the external steps. Vanity tops (Stage 6) and kitchen counters (Stage 7) are also '
    'granite and are listed here for completeness only.')
str_ = []
str_.append(row('Stair treads, 42 nos', 'Granite 20 mm, grooved', '11 1/2" x 3\'-6" (10 1/2" going + 1" nosing)', f1(TREAD_SFT), '10%', 'Stage 5'))
str_.append(row('Mid landings, 2 nos', 'Granite 20 mm', '8\'-3" x 3\'-6"', f1(LAND_SFT), '10%', 'Stage 5'))
str_.append(row('Stair risers, 44 nos', 'White marble 20 mm', '6.57" x 3\'-6"', f1(RISER_SFT), '10%', 'Stage 5'))
str_.append(row('Stepped skirting', 'White marble 20 mm', '%s rft x 4"' % f0(SKIRT_STAIR_RFT), f1(SKIRT_STAIR_SFT), '20%', 'Stage 5'))
str_.append(row('External steps (4 sets)', 'Granite 20 mm', 'treads 13" deep + risers 6"', f1(EXT_T + EXT_R), '10%', 'Stage 5'))
str_.append(row('Window and vent sills, %d nos' % sum(n for _, n, _, _ in SILLS), 'Granite 20 mm', ', '.join('%s%s' % (r_, ' x%d' % n if n > 1 else '') for r_, n, _, _ in SILLS),
                f1(SILL_SFT), '15%', 'Stage 5'))
str_.append(row('Door thresholds, %d nos' % len(THR), 'Granite 20 mm', ', '.join(t[0] for t in THR), f1(THR_SFT), '15%', 'Stage 5'))
str_.append(row('Vanity tops, 6 nos', 'Granite 20 mm', '3\'-0" x 1\'-10" + 3" upstand', f1(VAN_TOP * len(FULL)), '15%', 'Stage 6'))
str_.append(row('Kitchen counters + island', 'Granite 20 mm', '%s rft x 2\'-1" + island 5\'-0" x 2\'-6" + edge strips' % f1(K_WALLRUN), f1(K_GRAN), '15%', 'Stage 7'))
table(['Item', 'Stone', 'Size / members', 'Net (sft)', 'Waste', 'Priced in'], [3000, 2000, 5838, 1400, 1000, 1800], str_, ['L', 'L', 'L', 'R', 'C', 'C'], font=7.5)
boq(s, '%d.1 Priced materials - Stage 5' % SECNO[s])

# ---------------------------------------------------------------- STAGE 6
s = 'S6'; h1(s)
blk(type='p', size=17, text='Answers applied: floor-mounted one-piece WC in all 7 baths (Q9); concealed diverter mixer + 8" rain shower + hand shower in the 6 baths with showers (Q10); '
    'counter-top basin on a granite top with a wall-hung HDHMR cabinet, SS 304 accessories and LED mirror, wall-hung basin in the powder room (Q11); 8 mm toughened fixed '
    'glass screens (Q12); 600 x 600 anti-slip floors and 300 x 600 walls to the false ceiling with one feature wall each (Q7, Q8); hybrid gas/electric geysers (Q32); '
    'cementitious waterproofing under all bath tiles. Bath exhaust fans are in Stage 11.')
br_ = []
for k, v in BT.items():
    full = k in FULL
    br_.append(row(k, rn(k), f1(v['floor']), '%s / %s' % (f0(v['plain']), f0(v['feat'])), f0(v['wp']), 'one-piece', 'counter-top + granite top' if full else 'wall-hung + half pedestal',
                   'concealed mixer, rain + hand shower' if full else '-', '8 mm screen' if full else '-', 2 if full else 1,
                   'HDHMR vanity, LED mirror 900 x 750, 6-pc set' if full else 'LED mirror 600, 3-pc set'))
br_.append(row('', 'Total', f1(B_FLOOR), '%s / %s' % (f0(B_PLAIN), f0(B_FEAT)), f0(B_WP), len(BATHS), len(BATHS), len(FULL), len(FULL), N_TRAP, '', kind='total'))
table(['Id', 'Bath', 'Floor (sft)', 'Wall tiles plain / feature (sft)', 'Waterproofing (sft)', 'WC', 'Basin', 'Shower', 'Screen', 'Traps', 'Vanity, mirror, accessories'],
      [600, 2100, 900, 1500, 1200, 900, 1700, 1700, 1000, 700, 2738], br_, ['C', 'L', 'R', 'C', 'R', 'C', 'L', 'L', 'C', 'C', 'L'], font=7)
blk(type='note', text='Feature wall = the shorter wall behind the WC and vanity. Geysers: 2 x 35-gallon hybrid (GF and FF) + 1 x 15-gallon hybrid for the mumty bath and laundry; '
    'electric elements on their own 20 A circuits (Stage 1). Floor-trap bodies are in grey (item 11.F); only SS gratings are priced here.')
boq(s, '%d.1 Priced materials - Stage 6' % SECNO[s])

# ---------------------------------------------------------------- STAGE 7
s = 'S7'; h1(s)
blk(type='p', size=17, text='Kitchens (Q13-Q15): HDHMR carcass, high-gloss acrylic shutters, Hettich soft-close hinges and runners; granite counters in all three kitchens; '
    'built-in 5-burner hobs with chimney hoods in the open kitchen (hob on the island as drawn, so an island hood) and the FF kitchen; stainless double-bowl sinks with mixers '
    'in all three. Wardrobes ("almari", Q39): HDHMR carcass with laminate shutters and Hettich fittings, full height (8\'-0" + 2\'-0" loft) in the 5 dresses and the FF store as drawn.')
kr_ = []
for k, v in KR.items():
    runs = ' + '.join('%s %s' % (ftin(l), n) for n, l in v['runs'])
    isl = 'island %s base, top %s x %s' % (ftin(v['island'][0]), ftin(v['island'][1]), ftin(v['island'][2])) if v['island'] else '-'
    kr_.append(row(k, rn(k), runs, isl, f1(0.7 * sum(l for _, l in v['runs'])), 'double-bowl + mixer', '5-burner' if v['hob'] else 'none (see assumptions)',
                   {'island': 'island chimney', 'wall': 'wall chimney', None: 'exhaust fan'}[v['hood']], f1(A['WALLT'][k]['net'])))
table(['Id', 'Kitchen', 'Wall counter runs', 'Island', 'Wall cabinets (rft)', 'Sink', 'Hob', 'Hood', 'Backsplash (sft)'],
      [600, 1800, 2800, 2600, 1300, 1700, 1700, 1300, 1238], kr_, ['C', 'L', 'L', 'L', 'R', 'L', 'L', 'L', 'R'], font=7.5)
wr2 = [row(k, v[0], ftin(v[1]), v[2], '8\'-0" + 2\'-0" loft', math.ceil(v[1] / 2.0)) for k, v in WR.items()]
wr2.append(row('', 'Total wardrobe run', f1(W_RUN) + ' rft', '', '', N_WSH, kind='total'))
table(['Id', 'Location', 'Run', 'Shape', 'Height', 'Shutters (2 ft)'], [700, 4000, 1800, 4500, 2200, 1838], wr2, ['C', 'L', 'C', 'L', 'C', 'C'], font=7.5)
blk(type='note', text='Board take-off per rft: kitchen base 9 sft carcass + 2.8 sft back + 2.6 sft shutter; wall cabinet 6 + 2.5 + 2.4 sft; wardrobe 18 sft carcass + 10 sft back '
    '+ 10 sft shutter. Wall cabinets over 70% of the wall counter runs (windows and hoods excluded). No wardrobe is drawn in the mumty room.')
boq(s, '%d.1 Priced materials - Stage 7' % SECNO[s])

# ---------------------------------------------------------------- STAGE 8
s = 'S8'; h1(s)
blk(type='p', size=17, text='Answers applied: solid Diyar main door with 2 1/2" leaves and PU polish (Q16; its glazed fanlight is W07, Stage 9); 17 semi-solid internal doors - '
    'Diyar stiles and rails, ply core, veneer both faces, PU polish, solid Diyar chowkat - door frame (Q17); shutters ("palla") as below; WPC doors and frames in the 7 baths (Q18); insulated steel security doors '
    'for D02, D12 and D28 (Q19); Yale/Dorma locks on the main and external doors, good local locks with SS hinges inside (Q20); store door D14 included, master-dress opening '
    'D09 left open (Q40).')
dr_ = []
HSET = {'MAIN': 'H1', 'INT': 'H3', 'BATH': 'H4', 'EXT': 'H2'}
for (ref, fl, ra, rb, w, h, swing, typ, flag) in DOORS:
    size = '%s x %s' % (ftin(w), ftin(h))
    if ref == 'D01':
        v = DW[ref]
        dr_.append(row(ref, rn(ra), size, 'Diyar 7" x 3"' + LS + f2(v['ch']) + ' cft', 'Solid Diyar panelled 2 1/2", 2 leaves' + LS + f2(v['sh']) + ' cft',
                       f2(v['ch'] + v['sh'] + v['ar']), 'H1', 'PU polish ' + f0(v['pu']) + ' sft'))
    elif ref in INT_IDS:
        v = DW[ref]
        dr_.append(row(ref, rn(ra) + ' / ' + (rn(rb) if not rb.startswith('EXT') else rb), size, 'Diyar 4 1/2" x 2 1/2"' + LS + f2(v['ch']) + ' cft',
                       'Semi-solid 1 1/2": Diyar 4" x 1 1/2" frame (' + f2(v['sh']) + ' cft), 25 mm ply core, 6 mm ply + veneer both faces',
                       f2(v['ch'] + v['sh'] + v['ar']), 'H3', 'PU polish ' + f0(v['pu']) + ' sft'))
    elif ref in BATH_IDS:
        dr_.append(row(ref, rn(ra), size, 'WPC frame (with door)', 'WPC door 1 1/4", factory finished', '-', 'H4', 'factory finish'))
    elif ref in EXT_IDS:
        dr_.append(row(ref, rn(ra) + ' to outside', size, 'Steel frame (with door)', 'Insulated steel security door 2", powder coated', '-', 'H2', 'factory powder coat'))
    elif ref == 'D27':
        dr_.append(row(ref, rn(ra), size, 'Aluminium (Stage 9)', '2-panel sliding, 6 mm toughened glass', '-', 'Stage 9', 'powder coat'))
    elif ref == 'D09':
        dr_.append(row(ref, rn(ra), size, '-', 'No leaf - opening left open (Q40)', '-', '-', 'paint'))
    else:
        dr_.append(row(ref, rn(ra) + ' / ' + rn(rb), size, '-', 'Open arch - no door', '-', '-', 'paint'))
WOOD_NET = CH_CFT + DW['D01']['sh'] + SH_INT + AR_CFT
dr_.append(row('', 'Diyar wood, net (architraves included)', '', f2(CH_CFT) + ' cft', f2(DW['D01']['sh'] + SH_INT) + ' cft', f2(WOOD_NET), '',
               'gross %s cft with 25%%' % f1(WOOD_NET * 1.25), kind='total'))
table(['Ref', 'Room', 'Opening', 'Frame (chowkat)', 'Shutter and thickness', 'Wood cft incl. architraves', 'Hardware', 'Finish'],
      [600, 3200, 1300, 2000, 3900, 1300, 900, 1838], dr_, ['C', 'L', 'C', 'L', 'L', 'R', 'C', 'L'], font=7)
hs = [row('H1', 'Main door D01', 'Yale/Dorma heavy mortise lock + lever set + euro cylinder; door closer (Dorma TS-68 / Yale); 8 SS ball-bearing hinges 5"; flush bolts; 2 heavy floor stoppers; door viewer'),
      row('H2', 'External doors D02, D12, D28', 'Yale/Dorma mortise lock + lever set + cylinder; heavy floor stopper (hinges come with the door)'),
      row('H3', '17 internal doors', 'Good local mortise lock with lever handles; 3 SS hinges 4"; floor stopper; SS tower bolt 6"'),
      row('H4', '7 bathroom doors', 'Privacy lock with thumb-turn and indicator; 3 SS hinges 4"; floor stopper')]
table(['Set', 'Doors', 'Hardware'], [700, 3000, 11338], hs, ['C', 'L', 'L'], font=7.5)
blk(type='note', text='Chowkat lengths include 3" horns; internal shutters are 4" smaller than the opening in width and 2" in height. PU polish area covers both faces and edges '
    'of the shutters, the exposed chowkat faces and both architraves. Diyar wastage 25% covers sawing and planing.')
boq(s, '%d.1 Priced materials - Stage 8' % SECNO[s])

# ---------------------------------------------------------------- STAGE 9
s = 'S9'; h1(s)
blk(type='p', size=17, text='Windows ("khirki"). Answers applied: local medium aluminium series (frames about 1.2-1.4 mm wall), powder coated charcoal (RAL 7016), 3-track sliding with fly-net sash '
    '(Q21); fly-net ("jaali"); single 5 mm clear glass, frosted in the bath ventilators, 6+6 mm laminated only for the tall units W06, W07 and W09 (Q22); MS grills inside all GF windows, '
    'GF bath ventilators and stair windows (Q23).')
wnr = []
WROOM = {'G13/F13': 'TV lounge (GF) + Front bed (FF)', 'G15/F03': 'Entrance foyer + FF front lobby', 'F01/S01': 'Stair hall FF + mumty'}
WTYPE = {'SLT': 'Sliding 3-track + fixed top light', 'SL': 'Sliding 3-track', 'FXT': 'Fixed + top-hung vent', 'TH': 'Top-hung ventilator',
         'SF': 'Fixed storefront (45 mm)', 'SD': 'Sliding door, heavy series'}
GN = {'G5C': '5 mm clear', 'G5F': '5 mm frosted', 'G66L': '6+6 laminated', 'G6T': '6 mm toughened'}
for x in WINR:
    tname = WTYPE[x['t']]
    gr = '%s / %s' % (f0(x['grill']), f0(x['grill'] * GRILL_KG_SFT)) if x['grill'] else '-'
    wnr.append(row(x['ref'], x['fl'], rn(x['room']) if x['room'] in R else WROOM.get(x['room'], x['room']), '%s x %s' % (ftin(x['w']), ftin(x['h'])), tname, x['n'],
                   f1(x['kg'] * x['n']), GN[x['g']], f1(x['glass'] * x['n']), f1(x['net'] * x['n']) if x['net'] else '-', gr,
                   'granite' if x['ref'] != 'W07' else '-'))
wnr.append(row('', '', 'TOTAL', '', '', sum(x['n'] for x in WINR), f1(ALU_KG), '', f1(sum(x['glass'] * x['n'] for x in WINR)), f1(NET_SFT),
               '%s / %s' % (f0(GR_SFT), f0(GR_SFT * GRILL_KG_SFT)), '', kind='total'))
blk(type='h2', text='%d.1 Window schedule: aluminium, glass, fly-nets and grills per window' % SECNO[s])
table(['Ref', 'Floor', 'Room', 'Size', 'Type', 'Nos', 'Alu kg', 'Glass', 'Glass sft', 'Net sft', 'Grill sft / kg', 'Sill'],
      [600, 750, 2300, 1300, 3300, 500, 900, 1300, 950, 900, 1300, 938], wnr, ['C', 'C', 'L', 'C', 'L', 'C', 'R', 'L', 'R', 'R', 'C', 'C'], font=7)
SER = [('SLT', 'Sliding windows W01-W05, W10-W13, W15', 'Local medium 3-track sliding series, frame 1.2-1.4 mm, sash 1.2 mm', 'frame 1.10, glass sash 0.65, net sash 0.40, top-light frame 0.80, transom 0.90'),
       ('SL', 'Sliding window W04', 'Same series without top light', 'frame 1.10, sash 0.65, net sash 0.40'),
       ('FXT', 'Stair windows W08, W14 (x2 each)', 'Fixed frame + top-hung vent, 1.2 mm', 'frame 0.80, transom 0.90, vent sash 0.70'),
       ('TH', 'Bath ventilators V01-V07', 'Top-hung ventilator, 1.2 mm', 'frame 0.75 + sash 0.70'),
       ('SF', 'Tall units W06, W07, W09', '45 mm storefront series, 1.6-2.0 mm, mullions at 4\'-6", transoms at 6\'-0"', 'frame and bars 1.80; vents 0.70'),
       ('SD', 'Sliding door D27', 'Heavy sliding-door series, 1.6 mm', 'frame 1.60, sash 1.10, net sash 0.50')]
ser_r = [row(q[1], q[2], q[3], f1(sum(x['kg'] * x['n'] for x in WINR if x['t'] == q[0]))) for q in SER]
ser_r.append(row('Total', '', '', f1(ALU_KG), kind='total'))
blk(type='h2', text='%d.2 Aluminium section series and gauge' % SECNO[s])
table(['Openings', 'Series and wall thickness (gauge)', 'Section weights used (kg/m)', 'Aluminium kg'], [3800, 5000, 4638, 1600], ser_r, ['L', 'L', 'L', 'R'], font=7.5)
blk(type='note', text='Aluminium weights use the Step A model (sliding frame 1.10 kg/m, glass sash 0.65, net sash 0.40, fixed frame 0.80, transom 0.90, vent frame 0.75 + sash 0.70, '
    'storefront 1.80 kg/m). Ask the fabricator for catalogue weights; the material rate is per kg of powder-coated section. Grills: 12 mm square bars at 5" with a '
    '1 1/4" x 1/4" flat frame, about 1.5 kg per sft, painted charcoal (Stage 10).')
boq(s, '%d.3 Priced materials - Stage 9' % SECNO[s])

# ---------------------------------------------------------------- STAGE 10
s = 'S10'; h1(s)
blk(type='p', size=17, text='Paint ("rang"). Brand and system (Q24): Dulux (AkzoNobel Pakistan) standard range, not the top-premium lines. Inside: 2 coats of wall putty, 1 coat of primer and 2 coats '
    'of emulsion; gypsum ceilings get 1 skim coat of putty. Outside: alkali-resistant primer and 2 coats of Weathershield. Texture coat on the slab-edge feature bands and the '
    'boundary pillars (Q26). Gates are powder coated (Stage 12); aluminium is factory powder coated; grills get red-oxide primer and 2 coats of enamel.')
blk(type='h2', text='%d.1 Paint per area (net areas; gallons are 3.64 L)' % SECNO[s])
pr_ = []
def prow(area, sft, putty_coats, primer, finish, colour):
    putty = sft * (PUTTY_2C if putty_coats == 2 else (PUTTY_1C if putty_coats == 1 else 0))
    pg = sft / (PRIM_COV if primer == 'int' else PRIME_COV) if primer else 0
    if finish == 'EM': fin = '%s gal (%s L) emulsion' % (f1(sft / EMUL_COV), f0(sft / EMUL_COV * 3.64))
    elif finish == 'WS': fin = '%s gal (%s L) Weathershield' % (f1(sft / WS_COV), f0(sft / WS_COV * 3.64))
    else: fin = '%s kg texture' % f0(sft * TEX_KG)
    pr_.append(row(area, f0(sft), ('%s kg = %s bags' % (f0(putty), f1(putty / 20))) if putty else '-', ('%s gal' % f1(pg)) if pg else '-', fin, colour))
for fl in FLOORS:
    for k in [k for k in A['PAINT'] if k != 'STAIR' and R[k]['fl'] == fl]:
        parts = [(a, c) for (kk, a, c, _) in INT if kk == k]
        prow('%s - walls' % rn(k), sum(a for a, _ in parts), 2, 'int', 'EM', ' + '.join('%s %s sft' % (CLR[c][0], f0(a)) for a, c in parts))
prow('Stair well walls (3 storeys)', A['PAINT']['STAIR']['net'], 2, 'int', 'EM', CLR['NH'][0])
prow('Stair soffits (flights and landings)', SOFF_ST, 2, 'int', 'EM', CLR['BW'][0])
for fl in FLOORS:
    a = sum(FC[k]['a'] + FC[k]['cove'] * COVE_DEPTH for k in FC if R[k]['fl'] == fl)
    prow('%s - false ceilings incl. cove boxes' % FLN[fl], a, 1, 'int', 'EM', CLR['BW'][0])
for (nm, a, c, sys_) in EXT:
    prow(nm, a, 0, 'ext', sys_, cname(c))
prow('Grills (both faces of the bars)', GRILL_PAINT, 0, None, 'EM', 'enamel charcoal (RAL 7016) - see Stage 10 lines')
pr_[-1] = row('Grills (both faces of the bars)', f0(GRILL_PAINT), '-', '%s gal red oxide' % f1(GRILL_PAINT / 400), '%s gal enamel' % f1(GRILL_PAINT / 200), 'charcoal to match RAL 7016')
table(['Area', 'Net sft', 'Putty', 'Primer', 'Finish coats', 'Colour'], [5000, 1000, 1900, 1300, 2600, 3238], pr_, ['L', 'R', 'C', 'C', 'L', 'L'], font=7)
blk(type='note', text='Coverage used: putty 0.085 kg/sft for 2 coats (0.045 for 1 skim coat), primer 350 sft/gal inside and 300 outside, emulsion 180 sft/gal and Weathershield 150 sft/gal '
    'for 2 coats, texture 0.15 kg/sft. Paint areas: interior walls %s sft (Step A, openings deducted by IS 1200), exterior %s sft (Step A incl. parapets and soffits) and '
    'boundary walls %s sft (street, gali and inside faces; neighbour faces optional).' % (f0(INT_WALLS), f0(A['ext_tot']), f0(BW_IN + BW_OUT - BW_NEI)))
blk(type='h2', text='%d.2 Colour scheme - Dulux (AkzoNobel Pakistan) colour names and codes' % SECNO[s])
cs_ = [row('All false ceilings, stair soffits, porch soffits', 'Brilliant White', 'ready-mixed white', 'one bright ceiling plane throughout'),
       row('Lobbies, foyer, dining, drawing room, both TV lounges', 'Egyptian Cotton', CLR['EC'][1], 'warm greige for the living areas'),
       row('Bedrooms (3 walls), dresses, kitchens, store, laundry, mumty room', 'Jasmine White', CLR['JW'][1], 'soft warm white, the quiet base'),
       row('Stair well, GF to mumty', 'Natural Hessian', CLR['NH'][1], 'slightly deeper warm neutral for the tall wall'),
       row('Accent wall: GF Bed-1 and FF Front bed', 'Tranquil Dawn', CLR['TD'][1], 'muted sage'),
       row('Accent wall: GF and FF master bedrooms', 'Denim Drift', CLR['DD'][1], 'dusty blue-grey'),
       row('Accent wall: FF Bed-1 and mumty room', 'Thai Magic 3', CLR['TM'][1], 'soft clay'),
       row('TV walls in both lounges', 'Chic Shadow', CLR['CS'][1], 'mid grey behind the screen')]
table(['Room / surface', 'Colour', 'Code', 'Role'], [5600, 2400, 2400, 4638], cs_, ['L', 'L', 'C', 'L'], font=7.5)
ce_ = [row('Front (road)', 'Jasmine White', 'Urban Obsession texture', 'Urban Obsession', 'Brilliant White soffits; main door natural Diyar polish; frames RAL 7016'),
       row('Left (side passage)', 'Jasmine White', 'Urban Obsession texture', 'Urban Obsession', 'charcoal grills and frames'),
       row('Rear (rear passage / porch)', 'Jasmine White', 'Urban Obsession texture', 'Urban Obsession', 'steel doors powder coated to match'),
       row('Right (patio, open shaft)', 'Jasmine White', 'Urban Obsession texture', 'Urban Obsession', '-'),
       row('Mumty walls', 'Jasmine White', 'Urban Obsession texture', '-', 'parapet inner faces and tops Night Jewels 5'),
       row('Boundary walls', 'Night Jewels 5 (light grey)', 'pillars: Urban Obsession texture', 'coping: Urban Obsession', 'gates RAL 7016 anthracite')]
table(['Elevation', 'Body', 'Feature bands / pillars', 'Plinth / coping', 'Other'], [2800, 2600, 3200, 2400, 4038], ce_, ['L', 'L', 'L', 'L', 'L'], font=7.5)
blk(type='p', size=17, text='How the palette holds together: every wall colour comes from one warm family (yellow-based neutrals Jasmine White, Egyptian Cotton and Natural Hessian, '
    'codes 14YY-67YY) under one white ceiling, so rooms flow into each other without breaks. Each bedroom adds only one muted accent wall, and the three accents (sage, '
    'dusty blue, clay) share the same soft, greyed strength, so they never compete. One neutral grey line (Night Jewels 5 -> Chic Shadow -> Urban Obsession, all 00NN) '
    'links inside and out: TV walls, house bands, boundary walls and pillars, and the charcoal of the windows, grills and gates (RAL 7016). Natural Diyar polish on the doors '
    'is the wood-tone accent. Confirm every code on the dealer\'s Dulux tinting machine and approve a 1 sft sample on site before ordering.')
boq(s, '%d.3 Priced materials - Stage 10' % SECNO[s])

# ---------------------------------------------------------------- STAGE 11
s = 'S11'; h1(s)
blk(type='h2', text='%d.1 Switches and sockets (Q28: good local modular make, no smart switches)' % SECNO[s])
sw_ = []
for fl in FLOORS:
    ks = [k for k in SWR if R[k]['fl'] == fl]
    sw_.append(row(FLN[fl], sum(SWR[k]['sw1'] for k in ks), sum(SWR[k]['sw2'] for k in ks), sum(SWR[k]['s5'] for k in ks), sum(SWR[k]['p15'] for k in ks),
                   sum(SWR[k]['dp'] for k in ks) + 1, sum(SWR[k]['sb'] for k in ks)))
sw_.append(row('External', 8, 0, cnt['S5ext'], 0, 0, cnt['SBext']))
sw_.append(row('Total', N_SW1, N_SW2, N_S5, N_P15, N_DP, N_PLATE, kind='total'))
table(['Floor', '1-way switches', '2-way switches', '5 A sockets', '15 A sockets', 'DP 20 A (ACs, geysers)', 'Switch-board plates'],
      [3600, 1800, 1800, 1700, 1700, 2400, 2038], sw_, ['L', 'C', 'C', 'C', 'C', 'C', 'C'], font=7.5)
blk(type='h2', text='%d.2 Light fittings, fans and exhausts, room by room' % SECNO[s])
lt_ = []
for fl in FLOORS:
    lt_.append(row(FLN[fl], kind='section'))
    for k, v in LT.items():
        if R[k]['fl'] != fl: continue
        lt_.append(row(k, rn(k), v['dl'] or '-', f1(v['cove']) if v['cove'] else '-', f1(v['prof']) if v['prof'] else '-', v['deco'] or '-',
                       v['fan'] or '-', v['ex'] or '-', ('%g t' % [x['sel'] for x in AC if x['k'] == k][0]) if any(x['k'] == k for x in AC) else '-'))
lt_.append(row('External', kind='section'))
for nm, kk, n in EXT_FIT:
    lt_.append(row('', nm, '-', '-', '-', '%d x %s' % (n, RATES[kk]['name'].split(',')[0]), 1 if nm == 'Front car porch' else '-', '-', '-'))
lt_.append(row('', 'Front elevation (sheet 09)', '-', '-', '%s m outdoor' % f1(PROFX_M), '3 profile runs', '-', '-', '-'))
lt_.append(row('', 'Total', cnt['DL'], f1(COVE_TOT), f1(PROF_TOT), '%d decorative + %d outdoor' % (len(DECO_FIT) + 2, sum(n for _, _, n in EXT_FIT)),
               cnt['F'], cnt['EX'], '%d ACs' % len(AC), kind='total'))
table(['Id', 'Room', '12 W downlights', 'Cove strip (m)', 'Profile (m)', 'Decorative / outdoor fittings', 'Fan', 'Exhaust', 'AC'],
      [600, 3600, 1300, 1300, 1300, 3838, 900, 1000, 1200], lt_, ['C', 'L', 'C', 'C', 'C', 'L', 'C', 'C', 'C'], font=7)
blk(type='note', text='Q29: 12 W downlights, 3000 K in bedrooms and 4000 K in living areas, kitchens and baths. Cove (LED strip in the gypsum cove) and recessed aluminium profiles '
    'with COB strip only in the drawing room, both TV lounges and both master bedrooms (Q27). Chandeliers and pendants are prime-cost allowances. Q31: DC inverter fans, '
    '35-40 W, with remote.')
blk(type='h2', text='%d.3 Air-conditioners: tonnage from room size and orientation (Q30)' % SECNO[s])
blk(type='p', size=17, text='Method: base = conditioned area / 125 sft per ton (GF room, 10\'-0" false ceiling, north light, 2 people). Additions: roof above +15%; main window '
    'or wall facing west +10%, south +5%, east 0, north -5% (half of a positive addition where a passage wall, porch or shaft shades it); second exposed wall +5%; +5% per '
    '25 sft of glass above 50 sft; living, drawing and dining rooms +10%. Open-plan rooms carry 30% of the un-air-conditioned area open to them. Choose the smallest '
    'standard size within 10% of the need (a DC inverter unit boosts for the peak hours). Front (road) side = south.')
acr = []
for x in AC:
    corr = []
    if x['c_roof']: corr.append('roof +15%')
    if x['c_or']: corr.append('%s %+g%%' % (ORIN[x['ori']], round(x['c_or'] * 100, 1)))
    if x['c_w2']: corr.append('2nd wall +5%')
    if x['c_gl']: corr.append('glass +%g%%' % round(x['c_gl'] * 100, 1))
    if x['c_pp']: corr.append('living +10%')
    area = f1(x['a']) + (' + 30%% of %s' % ' + '.join(rn(j) for j, _ in x['opento']) if x['opento'] else '')
    remark = x['reading']
    if x['over']: remark += '. Need exceeds 2 t: see note below'
    acr.append(row(rn(x['k']), area, f1(x['a_eff']), '%s (%s)' % (ORIN[x['ori']], 'shaded' if x['shaded'] else 'open'), f0(x['glass']), f2(x['base']),
                   ', '.join(corr) or '-', f2(x['need']), '%g t' % x['sel'], '%g t' % x['step_a'], remark))
acr.append(row('Total', '', '', '', '', '', '', '', '%d x 1.5 t + %d x 2 t' % (N15, N20), '', 'Gree Pular DC inverter (Gree / Haier / Orient allowed, Q30)', kind='total'))
table(['Room', 'Area (sft)', 'Cond. area', 'Main exposure', 'Glass sft', 'Base t', 'Additions', 'Need t', 'Selected', 'Step A', 'Reading of the plan'],
      [1900, 1700, 900, 1200, 700, 700, 2100, 700, 1100, 700, 3338], acr, ['L', 'L', 'R', 'L', 'R', 'R', 'L', 'R', 'C', 'C', 'L'], font=7)
blk(type='note', text='Changes from the Step A trial sizes: dining 1 -> 1.5 t (open to the kitchen), mumty room 1 -> 1.5 t (roof and two exposed walls), FF master 1.5 -> 2 t '
    '(roof and west window), FF front bed 1.5 -> 2 t (roof, west window and 72 sft of south glass). The FF TV lounge and the FF front bedroom calculate at about 2.4-2.5 t: '
    '2 t is the largest wall-mounted split in this range, so fit blinds on the tall glazing (front bed) and a curtain or partition on the lounge\'s open side (optional item), '
    'or accept 1-2 deg C warmer on peak afternoons. AC pipe sets are in Stage 1.')
blk(type='h2', text='%d.4 Wi-Fi mesh, CCTV and EV charger' % SECNO[s])
blk(type='bullets', size=17, items=[
    'Wi-Fi (grey Register J2 positions): TP-Link Deco X50 (Wi-Fi 6) mesh, 4 nodes with wired Cat6 backhaul: GF TV lounge (main node at the router/NVR point), GF lobby, FF lobby, '
    'mumty stair hall (covers the terrace). An 8-port gigabit switch at the router position links the nodes.',
    'CCTV: Hikvision 8-channel PoE NVR with a 2 TB surveillance disk and 7 x 4 MP IP cameras (main gate, side gate, front porch, rear porch, back gali, two passages), '
    'powered over the Cat6 runs in the grey conduits. Viewing on phones and the TV; no separate monitor.',
    'EV charger (Q34): 7.4 kW single-phase Type 2 wall box (RNR) at the front car porch, on its own 6 mm2 circuit with a 40 A Type A RCBO and a 40 A isolator (Stage 1).'])
boq(s, '%d.5 Priced materials - Stage 11' % SECNO[s])

# ---------------------------------------------------------------- STAGE 12
s = 'S12'; h1(s)
pv_ = [row(nm, f1(a), '80 mm' if k == 'TUF80' else '60 mm') for nm, a, k in PAVE]
pv_.append(row('Total paving (= Step A external areas)', f1(T60 + T80), '60 mm %s + 80 mm %s sft' % (f0(T60), f0(T80)), kind='total'))
table(['Area', 'Net (sft)', 'Tuff tile'], [8000, 2000, 5038], pv_, ['L', 'R', 'C'], font=7.5)
gr_ = [row(g[0], f0(kg), 'MS frame, 16 g sheet, powder coated RAL 7016', 'bearing hinges, tower bolts, aldrop, stopper' + (', wicket lock' if g[4] else ''))
       for g, kg in zip(GATE, GKG)]
gr_ += [row(nm, '%s rft x %s' % (f0(L), ftin(h)), 'SS 304 posts at 4 ft + 50 mm top rail, 12 mm toughened glass %s high' % ftin(gh), '4 clamps per panel, anchor bolts')
        for nm, L, h, gh in RAIL]
table(['Item', 'MS weight (kg) / size', 'Construction', 'Hardware'], [4500, 2200, 5000, 3338], gr_, ['L', 'C', 'L', 'L'], font=7.5)
blk(type='bullets', size=17, items=[
    'Paving (Q5): 60 mm tuff tiles with 80 mm under the car tracks (wheel paths in both porches and both ramps, since both gates take cars), laid on 2" of sand over the grey sub-base.',
    'Gates (Q36): MS frame with 16-gauge sheet, powder coated, pedestrian wicket in the main gate. Railings ("jangla", Q37): SS 304 posts and 12 mm toughened glass at the stair-well '
    'edge on the mumty floor and on the FF front balcony.',
    'Water (Q35): 500-gallon triple-layer plastic roof tank ("tanki") on the grey platform with fittings; Pedrollo 1 HP pump ("motor") at the underground tank with an automatic '
    'level controller (float switches + dry-run cut-off). A pressure switch does not suit a pump that fills an open roof tank (see Remaining assumptions).'])
boq(s, '%d.1 Priced materials - Stage 12' % SECNO[s])

# ---------------------------------------------------------------- 15. exclusions, optional, assumptions (portrait)
blk(type='section', orientation='PORTRAIT')
blk(type='h1', text='15. Exclusions, optional items and remaining assumptions')
blk(type='h2', text='15.1 Exclusions (not in the total)')
blk(type='bullets', size=17, items=[
    'All labour: electrician, tile and stone fixing, false-ceiling fixing, carpentry and polishing, aluminium and gate fabrication and fixing, painting, plumbing second fix. '
    'Allow roughly 25-35% of the material cost for fabricated items (aluminium, joinery, gates).',
    'Transport and cartage, scaffolding, tools, site water and electricity, cleaning, contractor\'s overheads and profit, contingency.',
    'FESCO new 3-phase connection charges and security deposit, SNGPL gas connection, internet connection.',
    'Loose furniture, curtains and blinds, appliances (fridges, oven, microwave, washing machine, TV), water filter, landscaping and lawn soil.',
    'Everything already priced in the grey estimate Rev 1: conduits, back boxes, earth pits, solar plinths, UPVC floor-trap bodies, PPR and gas pipes, roof tiles, plaster.'])
blk(type='h2', text='15.2 Optional items (estimated, NOT in the total)')
ot = [row(i + 1, a, f0(b)) for i, (a, b) in enumerate(OPT)]
ot.append(row('', 'Saving if a 10 kWh LFP battery replaces the sodium-ion modules', '-' + f0(LFP_SAVING)))
table(['No.', 'Item', 'Approx. Rs'], [600, 7606, 1700], ot, ['C', 'L', 'R'], font=8)
blk(type='h2', text='15.3 Remaining assumptions (leftover doubts, flagged)')
RA = [
 'Front (road) side taken as south (as in the grey solar layout). If north differs, re-check the AC tonnage of the west-facing rooms and the panel direction.',
 'AC sizes are worked out here (Stage 11) and differ from the Step A trial sizes: 6 x 1.5 t + 4 x 2 t. The FF TV lounge and FF front bedroom need about 2.4-2.5 t; 2 t units are priced with blinds/curtains advised.',
 'Maximum demand rises to %s kW (%s A per phase); the 63 A incomer and 4-core 16 mm2 cable stay adequate. FESCO sanctioned load about 30 kW.' % (f1(MD_NEW / 1000), f0(I_NEW)),
 'DB boards: the grey Rev 1 empty enclosures are too small; the TPN/SPN boards here replace them (credit applied). They must be fixed before plaster.',
 'Wire lengths come from average route lengths per point (no wiring route drawing exists), likely within +/-15%. Earth is run to every point, lights included.',
 'Sodium-ion battery price is estimated (no retail listing). BMS compatibility with the chosen inverter must be confirmed before ordering; LFP is the fall-back.',
 'Open-kitchen island 4\'-6" x 2\'-0" with the hob on it, as drawn on sheet 01, so an island hood is priced. The raw kitchen has no built-in hob or hood (Q15 named only the open and FF kitchens); an exhaust fan is provided.',
 'Geysers: 2 x 35-gallon hybrid (GF, FF) + 1 x 15-gallon hybrid for the mumty bath and laundry, each with its own 20 A circuit.',
 'Pump control: an automatic level controller with float switches replaces the pressure switch in Q35, because the pump fills an open roof tank.',
 'Sliding door D27 is a door, not a window, so it gets 6 mm toughened safety glass (Q22 covered windows only).',
 'Grills are not fitted to the fixed laminated units W06, W07 and W09; the 6+6 laminated glass is the security layer there.',
 'Wardrobes as drawn on sheets 01-02: 5 dresses + FF store = %s rft, full height 10\'-0" with loft; none in the mumty room.' % f1(W_RUN),
 'Bath feature wall = the shorter wall behind the WC and vanity; powder room has no shower or screen.',
 'Floor bedding: 1" semi-dry 1:4 bed + adhesive bond coat (1 1/4" with falls in baths) fits the 1 1/2" finish allowance; if the PCC is level within 5 mm, adhesive alone can replace the bed.',
 '80 mm tuff tiles under the wheel tracks of both porches and on both ramps; 60 mm elsewhere.',
 'External steps (4 sets) in granite treads and risers (not asked in the questionnaire).',
 'Main-door fanlight = storefront glazing W07 (Stage 9). Door closer only on the main door.',
 'Paint coverage rates are typical for good plaster; rough plaster can use 10-15% more putty and paint. Neighbour-facing boundary faces are optional.',
 'Colour codes are AkzoNobel (Dulux) codes; Thai Magic 3 is used as the clay accent. Confirm each code on the dealer\'s tinting machine.',
 'Step A sizes not shown on the drawings remain as assumed there: lobby lengths, foyer depth, store S-A and door D14, W04 sill, main-door leaf height, false-ceiling heights, '
 'counter runs, exterior wall lengths per elevation and gate heights.',
 'Rates marked "estimated" (%d%% of the total) have no published October 2026 price; prices are retail incl. GST and can move 5-10%% between dealers.' % round(100 * EST_AMT / TOTAL),
]
blk(type='numbers', size=16, items=RA)

# ---------------------------------------------------------------- 16. final check
blk(type='h1', text='16. Final check', newpage=True)
n_rooms_used = len(set(k for k in FC) | set(k for k in A['PAINT'] if k != 'STAIR'))
chk = [
 ('Rooms', 'All %d Step A rooms appear in the false-ceiling schedule (Stage 3), floor tiles or stone (Stages 4-6), paint or wall tiles (Stages 6, 10) and the light schedule (Stage 11).' % len(R), 'PASS'),
 ('Doors', 'All 30 doors + arch A01 are in the door schedule: 1 main, 17 semi-solid, 7 WPC, 3 steel, D27 aluminium (Stage 9), D09 open, A01 arch.', 'PASS'),
 ('Windows', '17 windows (W01-W15, W08 and W14 x2) + 7 ventilators + D27 in the window schedule; aluminium %s kg and glass %s sft equal Step A.' % (f0(ALU_KG), f0(sum(x['glass'] * x['n'] for x in WINR))), 'PASS'),
 ('Tiles', 'Floor areas %s + %s + %s + %s sft, skirting %s rft, bath walls %s sft, backsplash %s sft and laundry dado %s sft all used once.' % (
     f1(T24P_FLOOR), f1(T24M_FLOOR), f1(B_FLOOR), f1(LAUN_F), f0(sum(T24_SK.values()) + KIT_SK), f1(B_PLAIN + B_FEAT), f1(K_BS), f1(LAUN_W)), 'PASS'),
 ('Stairs, sills', '42 treads, 44 risers, 2 landings, stepped skirting, 4 external step sets, %d sills and %d thresholds in Stage 5.' % (sum(n for _, n, _, _ in SILLS), len(THR)), 'PASS'),
 ('Paint', 'Interior %s sft + stair soffits %s + ceilings %s; exterior %s (incl. parapets, soffits); boundary %s sft. Equal to Step A.' % (
     f0(INT_WALLS), f0(SOFF_ST), f0(CEIL), f0(A['ext_tot']), f0(BW_IN + BW_OUT - BW_NEI)), 'PASS'),
 ('False ceiling', '%s sft (standard %s + moisture-resistant %s) = Step A.' % (f1(FC_ALL), f1(FC_STD), f1(FC_MR)), 'PASS'),
 ('Electrical', '%d downlights, %d fans, %d exhausts, 10 ACs, %d + %d sockets, %d cameras, 4 Wi-Fi nodes, EV charger - same point counts as Step A.' % (
     cnt['DL'], cnt['F'], cnt['EX'], N_S5, N_P15, A['CCTV_N']), 'PASS'),
 ('Solar', '23 x 650 W on the 34 grey plinths, 12 kW 3-phase hybrid, 10 kWh sodium-ion expandable to 16 kWh (Q33).', 'PASS'),
 ('Answers', 'All 40 answers applied, including the 7 changed answers (Q9, Q14, Q20, Q22, Q24, Q28, Q33); see the table below.', 'PASS'),
 ('Site order', 'Sections 3-14 follow the site sequence of Section 2.2 (first fix -> solar -> ceilings -> tiles -> stone -> baths -> kitchens -> doors -> windows -> paint -> second fix -> external).', 'PASS'),
 ('Totals', 'Summary total Rs %s = sum of the 12 stage totals = sum of %d priced lines (re-added independently).' % (f0(TOTAL), sum(len(v) for v in LINES.values())), 'PASS'),
 ('Word vs Excel', 'No Excel workbook was produced, on the owner\'s instruction of 3 Oct 2026; all figures are in this file.', 'N/A'),
 ('Exclusions', 'Labour and the optional items are outside the total (Section 15).', 'PASS'),
]
table(['Check', 'Result', ''], [1700, 7206, 1000], [row(a, b, c, kind='pass') for a, b, c in chk], ['L', 'L', 'C'], font=7.5)
ANS = [
 (1, 'Imported Chinese polished porcelain 2\'x4\', grade A', 'Stage 4: T24P tile'),
 (2, 'Polished light marble-look, one tile throughout', 'Stage 4: one series in all rooms, lobbies, halls'),
 (3, '4" skirting cut from the floor tile', 'Stage 4: skirting strips, 5 per tile'),
 (4, 'Granite treads with anti-slip grooves + white marble risers', 'Stage 5'),
 (5, '60 mm tuff tiles, 80 mm under car tracks', 'Stage 12 paving split'),
 (6, 'Kitchen floors same 2\'x4\' tile, matt', 'Stage 4: T24M'),
 (7, 'Baths 600 x 600 matt anti-slip', 'Stage 6 (laundry too, Stage 4)'),
 (8, '300 x 600 glazed walls, one feature wall per bath', 'Stage 6'),
 (9, 'CHANGED: floor-mounted one-piece WC in all 7 baths', 'Stage 6: 7 one-piece WCs, no concealed cisterns'),
 (10, 'Local premium brass concealed mixer + rain + hand shower', 'Stage 6: 6 shower sets'),
 (11, 'Stone-top basin + HDHMR vanity, SS accessories, LED mirror; wall-hung basin in powder room', 'Stages 6 and 5'),
 (12, '8 mm toughened fixed glass screen', 'Stage 6: 6 screens'),
 (13, 'Kitchen cabinets in scope: HDHMR, acrylic, Hettich', 'Stage 7'),
 (14, 'CHANGED: granite in all three kitchens', 'Stage 7: granite counters, no quartz'),
 (15, 'Local hob + hood in open and FF kitchens; SS sinks with mixer', 'Stage 7'),
 (16, 'Solid Diyar main door, polish, 2 1/2" leaf, glazed fanlight', 'Stage 8 (fanlight W07 in Stage 9)'),
 (17, 'Semi-solid internal doors, Diyar chowkat, veneer, PU', 'Stage 8: 17 doors'),
 (18, 'WPC bath doors and frames', 'Stage 8: 7 sets'),
 (19, 'Insulated steel security doors D02, D12, D28', 'Stage 8'),
 (20, 'CHANGED: Dorma/Yale on main + 3 external doors; local hardware + SS hinges inside', 'Stage 8: hardware sets H1-H4'),
 (21, 'Local medium aluminium, charcoal, 3-track with fly-net', 'Stage 9'),
 (22, 'CHANGED: single 5 mm glass (frosted in baths); 6+6 laminated only W06, W07, W09', 'Stage 9 glass lines'),
 (23, 'MS grills on all GF and stair windows', 'Stage 9 (not on fixed laminated units)'),
 (24, 'CHANGED: Dulux/Berger standard range; 2 putty + primer + 2 emulsion; Weathershield 2 coats', 'Stage 10'),
 (25, 'Recommended colour scheme', 'Stage 10 colour scheme, Dulux codes'),
 (26, 'Texture coat on feature bands and pillars', 'Stage 10 texture lines'),
 (27, 'Gypsum 12.5 mm on GI frame, MR in wet areas; cove/profile in drawing, lounges, master beds', 'Stage 3 + Stage 11'),
 (28, 'CHANGED: Pakistan Cables / Fast / Newage; Chint breakers; good local switches; no smart switches', 'Stages 1 and 11'),
 (29, '12 W LED downlights 3000-4000 K, cove and profile strips', 'Stage 11'),
 (30, 'ACs in scope: DC inverter Gree / Haier / Orient', 'Stage 11: tonnage worked out, Gree Pular'),
 (31, 'DC inverter fans 35-40 W', 'Stage 11: 12 fans'),
 (32, 'Hybrid gas/electric geysers', 'Stage 6: 2 x 35 gal + 1 x 15 gal'),
 (33, 'CHANGED: 15 kWp + 12 kW 3-phase hybrid + 10 kWh sodium-ion, expandable to 16 kWh', 'Stage 2'),
 (34, '7.4 kW single-phase EV wall box', 'Stage 11 + circuit in Stage 1'),
 (35, 'Pedrollo 1 HP + pressure switch; 500-gal triple-layer tank', 'Stage 12 (level controller - see assumptions)'),
 (36, 'MS + 16 g sheet gates, powder coated, wicket', 'Stage 12'),
 (37, 'SS 304 + 12 mm toughened glass railings', 'Stage 12'),
 (38, 'Granite 20 mm sills and thresholds', 'Stage 5 (+ vanity tops Stage 6)'),
 (39, 'Wardrobes in scope: HDHMR + laminate, Hettich', 'Stage 7'),
 (40, 'Store door only; master-dress opening open', 'Stage 8: D14 priced, D09 no leaf'),
]
blk(type='h2', text='16.1 Questionnaire answers and where they are applied')
table(['Q', 'Answer', 'Applied in'], [600, 5806, 3500], [row('Q%d' % q, a, w) for q, a, w in ANS], ['C', 'L', 'L'], font=7.5)
blk(type='h2', text='16.2 Your request list and where each item is')
REQ = [('1. One-page summary', 'Section 1'), ('2. Electrical: wire, DBs, MCBs, RCBO/RCD, surge, changeover', 'Section 3 (Stage 1)'),
       ('2. Electrical: switches, lights room by room, fans, ACs with tonnage, Wi-Fi, CCTV, EV', 'Section 13 (Stage 11)'),
       ('3. Solar and storage', 'Section 4 (Stage 2)'), ('4. Tiles per area with boxes and wastage', 'Section 6 (Stage 4) schedule for all tile areas'),
       ('5. Bathrooms', 'Section 8 (Stage 6)'), ('6. Kitchen', 'Section 9 (Stage 7)'), ('7. Doors per door', 'Section 10 (Stage 8)'),
       ('8. Windows per window', 'Section 11 (Stage 9)'), ('9. Paint and colour scheme', 'Section 12 (Stage 10)'), ('10. False ceilings', 'Section 5 (Stage 3)'),
       ('11. Marble / granite', 'Section 7 (Stage 5)'), ('12. Railings, gates, tank, pump, fixtures', 'Section 14 (Stage 12)'),
       ('13. Exclusions, optional items, remaining assumptions', 'Section 15'), ('Final check', 'Section 16')]
table(['Requested', 'Where'], [5906, 4000], [row(a, b) for a, b in REQ], ['L', 'L'], font=7.5)

json.dump(B, open(OUT, 'w'), indent=0, ensure_ascii=False)
print('TOTAL', f0(TOTAL), 'per sft', f0(TOTAL / COVERED), 'lines', sum(len(v) for v in LINES.values()), 'estimated share', round(100 * EST_AMT / TOTAL, 1))
for s_ in STAGES: print(s_, STAGES[s_][0][:40], f0(ST[s_]))
print('AC', [(x['k'], round(x['need'], 2), x['sel']) for x in AC], 'MD', round(MD_NEW / 1000, 1), round(I_NEW, 1))
