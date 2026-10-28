# Step 14 (read-only, login node; FD-F1-BINDING.md section 2 ruling 4): per tune, generated CC events above 50 GeV,
# counted from F1b''s merged gst (tree gst: cc == 1 && Ev > 50), beside all CC and all events. Reads only $OUT/f1b3/gst.
OUT=/pscratch/sd/j/josephrb/fd-f1-20261027
source /pscratch/sd/j/josephrb/MINERvA-OmniFold/setup_salloc_env.sh > /dev/null 2>&1
date -u +%FT%TZ; hostname
for f in $OUT/f1b3/gst/genie_v3_g18_ALL.gst.root $OUT/f1b3/gst/genie_v3_ar23_ALL.gst.root; do
  echo "$(sha256sum $f | cut -c1-64)  $f"
  python3 -c "
import ROOT, sys
f = ROOT.TFile.Open(sys.argv[1]); t = f.Get('gst')
print('entries', t.GetEntries(), 'cc', t.GetEntries('cc==1'), 'cc_Ev_gt_50', t.GetEntries('cc==1 && Ev>50'), 'all_Ev_gt_50', t.GetEntries('Ev>50'))
" $f
done
echo "end $(date -u +%FT%TZ)"
