#!/bin/bash
# Write diffs/<copy>.diff: each RE-2 part C copy against its committed original (RE2-DECLARATION-C.md §2.1).
# test_re2c.py fails if a committed diff is stale.
set -eo pipefail
cd "$(dirname "$0")"
R=../../..
S=docs/orchestration/state/2d-closeout
mkdir -p diffs
while read -r copy orig; do
    diff -u --label "$orig" --label "2d-unfolding/re2/partc/$copy" "$R/$orig" "$copy" > "diffs/$copy.diff" || [ $? = 1 ]
done <<LIST
re2c_analyze.py $S/stageC/production/analyze_prod.py
re2c_rollup.py $S/stageC/production/s5_rollup.py
re2c_export_cov.py $S/playlist-spread-20261014/coverage/scripts/export_cov.py
re2c_periods.py $S/period-unfold-20261014/scripts/periods.py
re2c_analyze_periods.py $S/period-unfold-20261014/scripts/analyze_periods.py
re2c_playlist_term.py $S/playlist-term/scripts/playlist_term.py
re2c_combine.py $S/playlist-term/scripts/combine_s5.py
re2c_build_q.py $S/stageF/rebuild/scripts/build_q_products.py
re2c_fig1.py $S/stageF/rebuild/scripts/make_fig1_q.py
LIST
wc -l diffs/*.diff
