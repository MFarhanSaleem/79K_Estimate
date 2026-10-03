#!/usr/bin/env bash
# Rebuilds the finishing Step B Word estimate from the take-off engine (Word only, no Excel).
#   OUT      : output folder (default: repo root)
#   WORK     : scratch folder for intermediate files (default: /tmp/stepB_build)
#   NODE_PATH: folder containing the 'docx' npm package
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
OUT="${OUT:-$HERE/../..}"
WORK="${WORK:-/tmp/stepB_build}"
mkdir -p "$WORK"
cd "$HERE"
python3 stepB.py "$WORK/blocks_stepB.json"                  # Step A take-off + answers + rates -> document blocks
node build_docx_stepB.js "$WORK/blocks_stepB.json" "$WORK/estimate_stepB.docx"
cp "$WORK/estimate_stepB.docx" "$OUT/House_79K_Finishing_Estimate.docx"
echo "done -> $OUT"
