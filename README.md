# House 79/K (Mr. Saleem): grey structure material estimate

This repo holds the full material take-off for the grey structure of House No. 79/K, Faisalabad. That covers the double-storey house with mumty, the boundary walls, the septic tank, the manholes and the R.C.C overhead water tank. It was measured from:

- the architectural and services working drawings, sheets 01-24, Faisal Associates, 16-08-2026
- the structural drawings, 2026/L-20/S-01 to S-09, Fakhar Associates, 14-08-2026

| File | What it is |
|---|---|
| `House_79K_Grey_Structure_Estimate.docx` | **The estimate report (Word, 25 pages)** |
| `House_79K_Grey_Structure_Estimate.pdf` | The same report as a PDF, for viewing on a phone |
| `calculations/` | Scripts and measured data behind every number in the report |

## Quantities to buy (upper estimate, standard wastage included)

| Material | To procure |
|---|---|
| Cement (OPC, 50 kg bags) | **1,560 bags** |
| Bricks (1st class, 9" x 4½" x 3") | **125,000** |
| Steel Grade 60 | **8,080 kg (8.08 t)**: 10 mm 4,630 kg, 12 mm 2,280 kg, 20 mm 1,030 kg, 6 mm 140 kg, plus binding wire 85 kg |
| Crush (¾" down) | **4,200 cft** |
| Sand | **7,750 cft**: concrete 2,250, mortar and plaster 4,900, sub-floor fill 600 |
| Earth filling (compacted) | 6,450 cft: re-use about 3,200 cft from the excavation, import about 3,250 cft |
| Bitumen (vertical DPC) | 320 kg |
| Sewerage UPVC | 5" 172 ft, 4" 141 ft, 3" 240 ft; rain-water 3" 124 ft |
| Water, hot water and gas | PPR 1"-1¼" 130 ft, ¾" 407 ft, ½" 154 ft; hot ¾" 397 ft, ½" 88 ft; gas 209 ft |
| Electrical PVC conduit | ¾" 3,191 ft, 1" 1,530 ft, 1½" 94 ft |

The report also covers:

- the stage-wise ordering plan
- the detailed bill of quantities with the material breakdown for each item
- the steel schedule
- fittings and electrical boxes
- optional items that are not in the totals (roof treatment, underground tank, paving)
- the assumptions and the points to confirm on site before work starts

## Re-running the calculations

The take-off itself needs only Python 3. Run these from the `calculations/` folder:

```bash
python3 est/export.py                  # runs est/estimate.py and writes est/estimate.json
python3 est/content.py                 # builds the report content (est/blocks.json)
(cd est && npm install)                # installs docx-js
node est/build_docx.js ../House_79K_Grey_Structure_Estimate.docx
```

- **Coefficients, mixes and wastage** are in `est/coeff.py`.
- **Item-by-item quantities** are in `est/estimate.py`.
- **Measured geometry** is in `geo/`:
  - `gf_network.py` is the foundation and ground-floor wall network.
  - `found_areas.json` holds the foundation layer areas.
  - `*_key_ft.json` hold the floor key-plan walls.
  - `bars_*.json` hold the slab bar sets.
  - `sewer_runs.json` and `water_runs.json` hold the pipe runs.
- **Overlay images** for checking the measurements are in `geo/checks/`.

Re-extracting the geometry from the drawings needs `pymupdf`, `opencv-python`, `scipy` and `shapely`. It also needs the working-drawings PDF, whose path goes in `WORKING_DRAWINGS_PDF`.
