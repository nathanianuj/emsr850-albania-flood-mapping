#!/bin/bash
# Phase 8 — Sentinel-1 SAR preprocessing using ESA SNAP 13
# Output: BEAM-DIMAP format with Sigma0_VV_db and Sigma0_VH_db bands

GPT=/root/snap/bin/gpt
S1_DIR=~/project_EMSR850/data/sentinel1
OUT_DIR=~/project_EMSR850/processing
GRAPH=~/emsr850-albania-flood-mapping/config/s1_flood_graph.xml

mkdir -p $OUT_DIR

PRE_SAFE="$S1_DIR/S1A_IW_GRDH_1SDV_20251117T164126_20251117T164151_061920_07BE4E_AD55.SAFE"
POST_SAFE="$S1_DIR/S1C_IW_GRDH_1SDV_20251130T163212_20251130T163237_005246_00A69C_CF66.SAFE"

echo "=== Processing PRE-event scene ==="
$GPT $GRAPH \
  -Pinput="$PRE_SAFE" \
  -Poutput="$OUT_DIR/S1_PRE_processed.dim" \
  2>&1 | tee $OUT_DIR/pre_processing.log
echo "PRE exit code: $?"

echo "=== Processing POST-event scene ==="
$GPT $GRAPH \
  -Pinput="$POST_SAFE" \
  -Poutput="$OUT_DIR/S1_POST_processed.dim" \
  2>&1 | tee $OUT_DIR/post_processing.log
echo "POST exit code: $?"

echo "=== Done ==="
ls -lh $OUT_DIR/
