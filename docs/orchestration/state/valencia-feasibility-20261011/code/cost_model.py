#!/usr/bin/env python3
"""Cost of the later matched-predecessor comparison, from the pilot's measurements.

Configurations: Valencia 2020 predecessor, corrected nominal (Re Sigma_Delta^eff = 0),
and the two corrected endpoints (-50 and +30 rho/rho0 MeV): four MEC samples on 12C,
truth level, with NuWro transport. Measured inputs come from the ledger and the R2
analysis; every other input is an explicit, labelled assumption.
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
ledger = {r["run_id"]: r for r in map(json.loads, (HERE / "logs/budget_ledger.jsonl").read_text().splitlines())}
r2 = json.loads((HERE / "results/R2/analysis.json").read_text())

measured = {
    # per-run measured values: total CPU (setup included) / sampled events, i.e. an upper bound
    # on the per-event cost of THAT run on THAT machine; not a certified cap
    "mec_cpu_s_per_trial_upper_R2_flux": ledger["R2-mefhc-flux"]["cpu_charged_s"] / ledger["R2-mefhc-flux"]["events_charged"],
    "mec_cpu_s_per_trial_upper_R1_1GeV": ledger["R1-bench-1GeV"]["cpu_charged_s"] / ledger["R1-bench-1GeV"]["events_charged"],
    "fullmodel_cpu_s_per_trial_R3": ledger["R3-fullmodel-throughput"]["cpu_charged_s"] / ledger["R3-fullmodel-throughput"]["events_charged"],
    "kish_neff_over_n_R2": r2["kish_neff_over_n"],
    "wmax_over_wmean_R2": r2["wmax_over_wmean"],
    "signal_acceptance_R2": r2["signal_acceptance"][0],
    "kish_neff_per_trial_by_signal_eavail_bin": {
        f"{b['bin_GeV'][0]}-{b['bin_GeV'][1]}": b["kish_neff_signal"] / r2["n_sampled"] for b in r2["eavail_bins"][:5]},
}

N_CONFIG = 4
TARGETS = {"1pct": 10_000, "2pct": 2_500}  # effective events per E_avail bin (memo's precision scale)
KISH_UNCERTAINTY_FACTOR = 3.0  # assumption: Kish estimates from 4,000 heavy-tailed weights are uncertain by up to x3
limiting_bin = min((v, k) for k, v in measured["kish_neff_per_trial_by_signal_eavail_bin"].items())
cpu_hi = max(measured["mec_cpu_s_per_trial_upper_R2_flux"], measured["mec_cpu_s_per_trial_upper_R1_1GeV"])
gen = {}
for name, neff in TARGETS.items():
    trials = neff / limiting_bin[0]
    gen[name] = {
        "limiting_bin_GeV": limiting_bin[1], "trials_per_config": trials,
        "trials_total": N_CONFIG * trials,
        "core_hours_extrapolated": N_CONFIG * trials * cpu_hi / 3600,
        "core_hours_extrapolated_with_kish_factor": N_CONFIG * trials * cpu_hi * KISH_UNCERTAINTY_FACTOR / 3600,
    }

# Full-model baseline (QEL, RES, DIS, COH + predecessor MEC), needed once for a matched
# total prediction. Throughput measured per weighted trial with a uniform channel mix;
# the unweighting factor of the full model was NOT measured. Assumed 1-50: the MEC
# channel alone measured w_max/<w> = 42 at this flux (REVIEW.md, finding 5).
baseline = {"events_assumed": 2_000_000, "unweighting_factor_assumed": [1, 50]}
baseline["core_hours_extrapolated"] = [baseline["events_assumed"] * f * measured["fullmodel_cpu_s_per_trial_R3"] / 3600
                          for f in baseline["unweighting_factor_assumed"]]

memo_assumption = {"events": 3_000_000, "cpu_s_per_event": [0.1, 1.0]}
memo_assumption["core_hours"] = [memo_assumption["events"] * c / 3600 for c in memo_assumption["cpu_s_per_event"]]

# Every projection is a linear extrapolation of runs of 200-4,000 events to millions of
# trials on the same Apple M1 Pro core. It is not a certified bound: no run of that size was
# made, and the campaign launcher's per-run CPU limits were not aggregate caps (REPAIR.md).
out = {"basis": "projections are linear extrapolations of measured per-run CPU; not certified bounds",
       "measured": measured, "generation_mec_four_configs": gen, "fullmodel_baseline": baseline,
       "memo_assumption_for_comparison": memo_assumption,
       "not_costed_unmeasured": [
           "a microscopic exclusive sampler for the corrected model (Kasturi et al. 2026): no code available",
           "MINERvA detector simulation and reconstruction for detector-level predictions",
           "obtaining corrected tensor tables (requires the authors; outside this authorization)"]}
(HERE / "results/cost.json").write_text(json.dumps(out, indent=1) + "\n")
print(json.dumps(out, indent=1))
