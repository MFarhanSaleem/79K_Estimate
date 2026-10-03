#!/usr/bin/env bash
# Rebuilds both Rev 1 deliverables from the take-off engine.
#   OUT      : output folder (default: repo root)
#   WORK     : scratch folder for intermediate files (default: /tmp/rev1_build)
#   NODE_PATH: folder containing the 'docx' npm package
#   RECALC   : path to the xlsx skill's recalc.py (LibreOffice recalculation)
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
OUT="${OUT:-$HERE/../..}"
WORK="${WORK:-/tmp/rev1_build}"
mkdir -p "$WORK"
cd "$HERE"
python3 export_rev1.py                                   # take-off engine -> rev1.json
python3 solar_fig.py "$WORK/solar_layout.png"            # schematic solar layout
python3 build_xlsx.py "$WORK/boq_rev1.xlsx"              # Excel with live formulas
python3 "$RECALC" "$WORK/boq_rev1.xlsx" 280 | tee "$WORK/recalc.json"
python3 content_rev1.py "$WORK/boq_rev1.xlsx" "$WORK/recalc.json" "$WORK/solar_layout.png" "$WORK/blocks_rev1.json"
node build_docx_rev1.js "$WORK/blocks_rev1.json" "$WORK/estimate_rev1.docx"
cp "$WORK/boq_rev1.xlsx" "$OUT/House_79K_Grey_Structure_BOQ_Rev1.xlsx"
cp "$WORK/estimate_rev1.docx" "$OUT/House_79K_Grey_Structure_Estimate_Rev1.docx"
echo "done -> $OUT"
