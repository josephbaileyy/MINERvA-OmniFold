#!/usr/bin/env python3
"""P3S/P3F acceptance audit + receipt: enumerate the 5x2x12 active-universe endpoint ROOTs for a mode,
validate each against the acceptance checks, and emit a compact machine-readable summary + downstream
file map for the commit gate.

Per-file acceptance checks (retained):
  four-tree schema, finite positive POT, event counts, native-miss metadata, ENDPOINT IDENTITY
  (metadata band/idx match the filename), truth-authoritative completeness, point-cloud branches, and
  the FOUR migration-census TParameters (activeUniverse{Truth,Reco}{Entrants,Exits}) read+validated+
  aggregated. In historical mode every present file is also bound by SHA-256 (mandatory) and to exactly
  one production PRODUCER LOG.

Provenance modes (--provenance):
  observation (default): current-HEAD / current-binary / current-launcher convenience view, CLEARLY
    labeled observation-time (NOT production).
  historical: FAIL-CLOSED production provenance with PER-FILE producer binding. --hash-files is
    MANDATORY (cannot exit 0 / complete=true without it). Each expected ROOT is bound to exactly ONE
    producer log from an explicit allow-list of producer jobs (55961845, 55972324): the log name parses
    with a strict regex, contains an unambiguous `[active-fps] wrote <that exact path>` (skip-only logs
    are NOT producers), the validated binary MD5, and the `MNV101_FULL_PHASE_SPACE set` runtime message;
    the log task index maps to the file's band/endpoint/playlist; and that (job,task) is terminal
    COMPLETED/0:0 in accounting. Missing/duplicate/wrong producers fail closed. The FPS launcher was
    uncommitted at submit, so its content is recorded ONLY as an observation-time candidate (production
    launcher content/source_commit = unknown/null); runtime behavior is bound through the per-file logs.

Publication (historical): no-clobber (mkstemp + fsync + hard-link to an ABSENT final + unlink temp),
same-filesystem; publishes ONLY to a preflight namespace and REFUSES an existing final; the canonical
p3s_<mode>_manifest.json is never overwritten by a historical run (even via --out). Promotion is a
separate orchestrator gate.

Usage: p3s_manifest_summary.py [--mode standard|fps] [--provenance observation|historical]
          [--hash-files] [--out <json under preflight/>]
Exit 0 iff 120/120 complete AND every file passes; 2 on validation failure; 3 EVIDENCE-BLOCKED.
"""
import argparse, glob, hashlib, json, math, os, re, subprocess, sys, tempfile

BANDS = ["BeamAngleX", "BeamAngleY", "MuonResolution",
         "Muon_Energy_MINERvA", "Muon_Energy_MINOS"]
PLAYLISTS = ["1A", "1B", "1C", "1D", "1E", "1F", "1G", "1L", "1M", "1N", "1O", "1P"]
TREES = ["mc_truth_denom", "mc_signal_reco", "mc_background", "data"]
SIG_PC = ["part_gen_E", "part_gen_pdg", "part_reco_E", "part_reco_pos", "part_reco_z"]
RECO_PC = ["part_reco_E", "part_reco_pos", "part_reco_z"]
CENSUS = ["activeUniverseTruthEntrants", "activeUniverseTruthExits",
          "activeUniverseRecoEntrants", "activeUniverseRecoExits"]
LAUNCHERS = {"standard": "nd-unfolding/sbatch_evloop_array_5d_active_laterals.sh",
             "fps": "nd-unfolding/sbatch_evloop_array_5d_active_laterals_fps.sh"}
INTERFACE_MD5_FILE = "nd-unfolding/active_universe_5d/INTERFACE_VALIDATION.md"
BINARY_REL = "MINERvA101/opt/bin/runEventLoopOmniFold"

# explicit allow-list of production producer jobs (do NOT discover arbitrary jobs)
PRODUCER_JOBS = ("55961845", "55972324")
LOG_NAME_RE = re.compile(r"^ev5d_active_fps_(\d+)_(\d+)\.out$")          # strict: (job)_(task)
WROTE_RE = re.compile(r"\[active-fps\] wrote (\S+)")                      # unambiguous producer marker
BINMD5_RE = re.compile(r"binary fingerprint OK \(md5 ([0-9a-f]{32})\)")
FPS_RUNTIME_MSG = "MNV101_FULL_PHASE_SPACE set"


class HistoricalEvidenceError(Exception):
    """Raised when a historical production fact cannot be established from durable evidence."""


def _sh(cmd):
    try:
        return subprocess.check_output(cmd, shell=True, universal_newlines=True,
                                       stderr=subprocess.DEVNULL).strip()
    except Exception:
        return None


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def get_val(f, name):
    o = f.Get(name)
    if o is None:
        return None
    if hasattr(o, "GetVal"):
        return o.GetVal()
    if hasattr(o, "GetTitle"):
        return o.GetTitle()
    return None


# ---- pure predicates (ROOT-free, unit-testable) ----
def identity_ok(aBand, aIdx, aEn, aLat, band, ep):
    try:
        return (aBand == band and aIdx is not None and int(aIdx) == ep
                and int(aEn) == 1 and int(aLat) == 1)
    except (TypeError, ValueError):
        return False


def census_present(cen):
    return all(cen.get(c) is not None for c in CENSUS)


def aggregate_census(cen_dicts):
    agg = {c: 0 for c in CENSUS}
    for cen in cen_dicts:
        for c in CENSUS:
            agg[c] += int(cen.get(c) or 0)
    return agg


def _committed_at_submit(first_commit_epoch, submit_epoch):
    if not first_commit_epoch or not submit_epoch:
        return None
    return int(first_commit_epoch) <= int(submit_epoch)


def inventory_complete(present, missing, bad, extras):
    return present == 120 and not missing and not bad and not extras


def parse_log_name(basename):
    """Strict parse of a producer log filename -> (job, task) or None (underscore-split is WRONG)."""
    m = LOG_NAME_RE.match(basename)
    return (m.group(1), m.group(2)) if m else None


def parse_sacct_state(output):
    """Parse the primary line of `sacct -o State,ExitCode -P --noheader` -> (state, exitcode) or None."""
    if not output:
        return None
    lines = [l for l in output.strip().splitlines() if l.strip()]
    if not lines:
        return None
    parts = lines[0].split("|")
    if len(parts) < 2:
        return None
    return parts[0].strip(), parts[1].strip()


def expected_task_for(band, ep, playlist):
    """Inverse of the launcher mapping: T = band_index*24 + ep*12 + playlist_index."""
    return BANDS.index(band) * 24 + ep * 12 + PLAYLISTS.index(playlist)


def require_no_extra_files(base):
    """Every endpoint dir must contain EXACTLY its 12 expected playlist ROOTs -- no extras."""
    extras = []
    for band in BANDS:
        for ep in (0, 1):
            d = os.path.join(base, f"{band}_{ep}")
            expected = {f"runEventLoopOmniFold_5D_{pl}_active_{band}_{ep}.root" for pl in PLAYLISTS}
            if os.path.isdir(d):
                actual = {f for f in os.listdir(d) if f.endswith(".root")}
                extras += [f"{band}_{ep}/{f}" for f in sorted(actual - expected)]
    return extras


def index_producers(logs_dir, allow_jobs=PRODUCER_JOBS):
    """Index abs-wrote-path -> [producer records] from allow-listed jobs only. Skip-only logs (no
    `[active-fps] wrote`) are excluded. Each record carries (job,task), log path+sha256, the binary
    md5s cited, and whether the FPS runtime message is present."""
    index = {}
    for lp in sorted(glob.glob(os.path.join(logs_dir, "ev5d_active_fps_*.out"))):
        nm = parse_log_name(os.path.basename(lp))
        if not nm:
            continue
        job, task = nm
        if job not in allow_jobs:
            continue
        txt = open(lp, errors="replace").read()
        wrote = WROTE_RE.findall(txt)
        if not wrote:
            continue                                   # skip-only / non-producer
        rec = {"producer_job": job, "producer_task": int(task),
               "log_path": lp, "log_sha256": sha256_file(lp),
               "md5s": BINMD5_RE.findall(txt), "has_fps": FPS_RUNTIME_MSG in txt}
        for w in wrote:
            index.setdefault(os.path.realpath(w), []).append(rec)
    return index


def bind_producer(root_abs, band, ep, playlist, index, expected_md5):
    """Bind a ROOT to EXACTLY ONE producer log; verify md5, FPS message, and task<->path mapping.
    Raises HistoricalEvidenceError on missing/duplicate/wrong producer."""
    recs = index.get(os.path.realpath(root_abs), [])
    if not recs:
        raise HistoricalEvidenceError(f"no producer log wrote {os.path.basename(root_abs)}")
    if len(recs) > 1:
        who = ",".join(f"{r['producer_job']}_{r['producer_task']}" for r in recs)
        raise HistoricalEvidenceError(f"duplicate producers for {os.path.basename(root_abs)}: {who}")
    r = recs[0]
    if expected_md5 not in r["md5s"]:
        raise HistoricalEvidenceError(f"producer {r['producer_job']}_{r['producer_task']} lacks md5 {expected_md5}")
    if not r["has_fps"]:
        raise HistoricalEvidenceError(f"producer {r['producer_job']}_{r['producer_task']} lacks '{FPS_RUNTIME_MSG}'")
    exp_task = expected_task_for(band, ep, playlist)
    if r["producer_task"] != exp_task:
        raise HistoricalEvidenceError(
            f"producer task {r['producer_task']} != expected {exp_task} for {band}_{ep}/{playlist}")
    return {"producer_job": r["producer_job"], "producer_task": r["producer_task"],
            "log_path": os.path.relpath(r["log_path"], os.getcwd()) if os.path.isabs(r["log_path"]) else r["log_path"],
            "log_sha256": r["log_sha256"]}


def terminal_ok(state, exitcode):
    """Pure accounting predicate: terminal success == COMPLETED with 0:0."""
    return state == "COMPLETED" and exitcode == "0:0"


def require_terminal_completed(job, task):
    """sacct the exact producer (job,task); require terminal COMPLETED/0:0. Reject running/failed/
    missing/nonzero/ambiguous."""
    out = _sh(f"sacct -j {job}_{task} -o State,ExitCode -P --noheader")
    st = parse_sacct_state(out)
    if st is None:
        raise HistoricalEvidenceError(f"no accounting record for {job}_{task}")
    state, exitcode = st
    if not terminal_ok(state, exitcode):
        raise HistoricalEvidenceError(f"{job}_{task} accounting {state}/{exitcode} != COMPLETED/0:0")
    return {"state": state, "exitcode": exitcode}


# ---- provenance ----
def parse_interface_md5(path):
    if not os.path.exists(path):
        raise HistoricalEvidenceError(f"interface record absent: {path}")
    for line in open(path, errors="replace"):
        m = re.search(r"md5\s*`?([0-9a-f]{32})`?", line)
        if m:
            return m.group(1)
    raise HistoricalEvidenceError(f"no md5 found in interface record {path}")


def build_historical_provenance(repo, mode, interface_file, allow_jobs=PRODUCER_JOBS):
    """Establish the EXPECTED production binary md5 (fail-closed) + the launcher-as-observation-candidate
    (production content unknown: uncommitted at submit). Per-file producer binding is done in the loop."""
    expected_md5 = parse_interface_md5(interface_file)
    launcher_rel = LAUNCHERS[mode]
    launcher_abs = os.path.join(repo, launcher_rel)
    obs_candidate = {
        "launcher": launcher_rel,
        "observation_content_sha256": sha256_file(launcher_abs) if os.path.exists(launcher_abs) else None,
        "observation_git_blob": _sh(f"cd {repo} && git hash-object {launcher_rel}"),
        "observation_mtime": _sh(f"stat -c '%y' {launcher_abs}") if os.path.exists(launcher_abs) else None,
        "first_commit": _sh(f"cd {repo} && git log --reverse --format='%H %cI' -- {launcher_rel} | head -1"),
        "note": "observation-time candidate ONLY; launcher was uncommitted at array submit",
    }
    production = {
        "provenance_mode": "historical",
        "allowed_producer_jobs": list(allow_jobs),
        "binary_md5_expected": expected_md5,
        "binary_md5_source": os.path.relpath(interface_file, repo),
        "production_launcher_content": "unknown (uncommitted at submit)",
        "production_launcher_source_commit": None,
        "production_launcher_binding": "per-file producer logs ([active-fps] wrote PATH + md5 + FPS msg + task map)",
        "expected_full_phase_space": (mode == "fps"),
    }
    observation = {
        "provenance_mode": "observation-time (NOT production)",
        "observed_head": _sh(f"cd {repo} && git rev-parse HEAD"),
        "observed_binary_md5": _sh(f"md5sum {os.path.join(repo, BINARY_REL)} | cut -d' ' -f1"),
        "observed_utc": _sh("date -u '+%Y-%m-%dT%H:%M:%SZ'"),
        "observation_launcher_candidate": obs_candidate,
        "note": "observation-time facts; MUST NOT be read as production provenance",
    }
    return production, observation, expected_md5


def observation_provenance(repo, mode):
    launcher = LAUNCHERS[mode]
    binpath = os.path.join(repo, BINARY_REL)
    return {
        "provenance_mode": "observation-time (NOT production)", "mode": mode,
        "observed_head": _sh(f"cd {repo} && git rev-parse HEAD"),
        "observed_binary_md5": _sh(f"md5sum {binpath} | cut -d' ' -f1"),
        "observed_binary_mtime": _sh(f"stat -c '%y' {binpath}"),
        "launcher": launcher, "launcher_git_blob": _sh(f"cd {repo} && git hash-object {launcher}"),
        "expected_full_phase_space": (mode == "fps"),
        "note": "observation-time convenience view; use --provenance historical for production facts",
    }


def publish_receipt_noclobber(path, obj):
    """No-clobber, same-filesystem, fsync'd publish: mkstemp in the target dir + fsync + hard-link to an
    ABSENT final + unlink temp. Refuses (raises) if the final already exists."""
    d = os.path.dirname(path) or "."
    os.makedirs(d, exist_ok=True)
    if os.path.lexists(path):
        raise HistoricalEvidenceError(f"refuse to clobber existing final receipt: {path}")
    fd, tmp = tempfile.mkstemp(dir=d, prefix=".p3s_", suffix=".tmp")
    try:
        with os.fdopen(fd, "w") as fh:
            json.dump(obj, fh, indent=2)
            fh.flush()
            os.fsync(fh.fileno())
        os.link(tmp, path)                              # atomic no-clobber; fails if final appeared
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def resolve_historical_out(base, mode, out_arg):
    """Historical runs publish ONLY under <base>/preflight/ and NEVER the canonical manifest."""
    preflight = os.path.join(base, "preflight")
    canonical = os.path.realpath(os.path.join(base, f"p3s_{mode}_manifest.json"))
    out = out_arg or os.path.join(preflight, f"p3s_{mode}_manifest_historical.json")
    rp = os.path.realpath(out)
    if rp == canonical:
        raise HistoricalEvidenceError("historical run may not target the canonical manifest")
    if os.path.realpath(os.path.dirname(rp)) != os.path.realpath(preflight):
        raise HistoricalEvidenceError(f"historical --out must live under {preflight}/")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", default="standard", choices=["standard", "fps"])
    ap.add_argument("--provenance", default="observation", choices=["observation", "historical"])
    ap.add_argument("--hash-files", action="store_true",
                    help="bind every present file by SHA-256 (MANDATORY in historical mode; ~744GB for FPS)")
    ap.add_argument("--repo", default="/pscratch/sd/j/josephrb/MINERvA-OmniFold")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    base = os.path.join(a.repo, "nd-unfolding", "active_universe_5d", a.mode)
    logs_dir = os.path.join(base, "logs")

    historical = (a.provenance == "historical")
    observation = None
    try:
        if historical:
            if a.mode == "standard":
                raise HistoricalEvidenceError(
                    "historical provenance explicitly unsupported for standard mode")
            if not a.hash_files:
                raise HistoricalEvidenceError("historical mode REQUIRES --hash-files (per-file SHA-256)")
            out = resolve_historical_out(base, a.mode, a.out)
            if os.path.lexists(out):
                raise HistoricalEvidenceError(f"refuse to clobber existing final receipt: {out}")
            prov, observation, expected_md5 = build_historical_provenance(
                a.repo, a.mode, os.path.join(a.repo, INTERFACE_MD5_FILE))
            index = index_producers(logs_dir)
            if not index:
                raise HistoricalEvidenceError(f"no producer logs found in {logs_dir}")
        else:
            out = a.out or os.path.join(base, f"p3s_{a.mode}_manifest.json")
            prov, expected_md5, index = observation_provenance(a.repo, a.mode), None, None
    except HistoricalEvidenceError as e:
        print(f"EVIDENCE-BLOCKED :: {e}", file=sys.stderr)
        sys.exit(3)

    extras = require_no_extra_files(base)                # exact inventory: zero extra ROOTs

    import ROOT                                          # lazy: only for the per-file numeric checks

    files, present, missing, bad = [], 0, [], []
    endpoints = {}
    for band in BANDS:
        for ep in (0, 1):
            key = f"{band}_{ep}"
            agg = {"playlists_present": 0, "size_bytes": 0, "entries": {t: 0 for t in TREES},
                   "mcPOT": 0.0, "dataPOT": 0.0, "nMisses": 0, "isLateral": None, "identity_ok": 0,
                   "census": {c: 0 for c in CENSUS}}
            for pl in PLAYLISTS:
                p = os.path.join(base, key, f"runEventLoopOmniFold_5D_{pl}_active_{band}_{ep}.root")
                rec = {"band": band, "endpoint": ep, "playlist": pl,
                       "path": os.path.relpath(p, a.repo),
                       "exists": os.path.exists(p) and os.path.getsize(p) > 0}
                if not rec["exists"]:
                    missing.append(f"{key}/{pl}"); files.append(rec); continue
                rec["size"] = os.path.getsize(p)
                if a.hash_files:
                    rec["sha256"] = sha256_file(p)
                f = ROOT.TFile.Open(p)
                if not f or f.IsZombie():
                    rec["readable"] = False; bad.append(f"{key}/{pl}:zombie"); files.append(rec); continue
                rec["readable"] = True
                checks, ent = {}, {}
                for t in TREES:
                    tr = f.Get(t); ent[t] = int(tr.GetEntries()) if tr else -1
                rec["entries"] = ent
                checks["schema_4trees"] = all(f.Get(t) for t in TREES)
                checks["counts_positive"] = ent["mc_truth_denom"] > 0 and ent["mc_signal_reco"] > 0
                mcPOT, dataPOT = get_val(f, "mcPOTUsed"), get_val(f, "dataPOTUsed")
                checks["pot_finite"] = (mcPOT is not None and dataPOT is not None
                                        and math.isfinite(mcPOT) and math.isfinite(dataPOT)
                                        and mcPOT > 0 and dataPOT > 0)
                nMiss, hasMiss = get_val(f, "nTruthOnlyMisses"), get_val(f, "hasTruthOnlyMisses")
                checks["misses_meta"] = (nMiss is not None and hasMiss is not None)
                aBand, aIdx = get_val(f, "activeUniverseBand"), get_val(f, "activeUniverseIndex")
                aEn, aLat = get_val(f, "hasActiveUniverse"), get_val(f, "activeUniverseIsLateral")
                checks["identity"] = identity_ok(aBand, aIdx, aEn, aLat, band, ep)
                rec["identity"] = {"band": aBand, "idx": aIdx, "hasActive": aEn, "isLateral": aLat}
                td, sg = ent["mc_truth_denom"], ent["mc_signal_reco"]
                comp = (sg / td) if td else None
                rec["completeness"] = comp
                checks["completeness"] = (comp is not None and abs(comp - 1.0) < 0.02)
                sigtr, bkgtr, datr = f.Get("mc_signal_reco"), f.Get("mc_background"), f.Get("data")
                checks["pc_signal"] = all(sigtr and sigtr.GetBranch(b) for b in SIG_PC)
                checks["pc_bkg"] = all(bkgtr and bkgtr.GetBranch(b) for b in RECO_PC)
                checks["pc_data"] = all(datr and datr.GetBranch(b) for b in RECO_PC)
                cen = {c: get_val(f, c) for c in CENSUS}
                checks["census_meta"] = census_present(cen)
                rec["census"] = cen
                f.Close()
                if historical:
                    checks["hashed"] = ("sha256" in rec)
                    try:
                        pb = bind_producer(p, band, ep, pl, index, expected_md5)
                        pb.update(require_terminal_completed(pb["producer_job"], pb["producer_task"]))
                        rec["producer"] = pb
                        checks["producer_bound"] = True
                        checks["producer_terminal"] = True
                    except HistoricalEvidenceError as e:
                        checks["producer_bound"] = False
                        rec.setdefault("producer_error", str(e))
                rec["checks"] = checks
                rec["pass"] = all(checks.values())
                files.append(rec)
                if rec["pass"]:
                    present += 1; agg["playlists_present"] += 1; agg["size_bytes"] += rec["size"]
                    for t in TREES:
                        if ent[t] > 0:
                            agg["entries"][t] += ent[t]
                    agg["mcPOT"] += mcPOT or 0.0; agg["dataPOT"] += dataPOT or 0.0
                    agg["nMisses"] += int(nMiss or 0)
                    if aLat is not None:
                        agg["isLateral"] = int(aLat)
                    agg["identity_ok"] += 1
                    for c in CENSUS:
                        agg["census"][c] += int(cen[c] or 0)
                else:
                    bad.append(f"{key}/{pl}:" + ",".join(k for k, v in checks.items() if not v))
            td, sg = agg["entries"]["mc_truth_denom"], agg["entries"]["mc_signal_reco"]
            agg["completeness_sig_over_td"] = (sg / td) if td else None
            agg["migration_abs_total"] = sum(abs(v) for v in agg["census"].values())
            endpoints[key] = agg

    complete = inventory_complete(present, missing, bad, extras) and (a.hash_files if historical else True)
    summary = {"provenance": prov, "observation_time": observation, "hashed": bool(a.hash_files),
               "expected": 120, "present_and_passing": present, "complete": complete,
               "missing": missing, "extras": extras, "failing": bad, "endpoints": endpoints}
    payload = {"summary": summary, "files": files}
    if historical:
        try:
            publish_receipt_noclobber(out, payload)     # no-clobber; refuses existing final
        except HistoricalEvidenceError as e:
            print(f"EVIDENCE-BLOCKED :: {e}", file=sys.stderr); sys.exit(3)
    else:
        tmp = out + ".tmp"                               # observation: plain atomic replace
        os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
        with open(tmp, "w") as fh:
            json.dump(payload, fh, indent=2)
        os.replace(tmp, out)

    print(f"[audit {a.mode}/{a.provenance}] passing={present}/120 complete={complete} "
          f"missing={len(missing)} extras={len(extras)} failing={len(bad)} hashed={a.hash_files}")
    if historical:
        print(f"[prov historical] expected_md5={prov['binary_md5_expected']} "
              f"allowed_jobs={prov['allowed_producer_jobs']} launcher_content=unknown source_commit=null")
    if extras:
        print("EXTRAS:", "; ".join(extras[:12]))
    if bad:
        print("FAILING:", "; ".join(bad[:12]))
    print(f"summary -> {out}")
    sys.exit(0 if complete else 2)


if __name__ == "__main__":
    main()
