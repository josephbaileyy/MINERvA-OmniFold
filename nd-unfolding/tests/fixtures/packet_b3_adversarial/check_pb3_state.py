#!/usr/bin/env python3
"""Packet PB3 acceptance checker — judges the post-run state of the evidence directory.

Authored by the oversight session, independent of the PB3 fix, per Packet B constraint 3.

WHY A CHECKER AND NOT FIXTURES
------------------------------
PB1's cases were files. PB2's had to be generated because they referenced repo blobs. PB3's
"cases" are neither: what is under test is WHERE FILES LAND after a run, which is an outcome, not
an input. So the split is — the fix author injects the fault (only they can; the stage reads ROOTs
on the cluster) and this checker judges the resulting directory. The independence lives in the
expectations and the assertions, not in the injection mechanics.

Nothing here is blind. The expected states are derivable from the defect and the author stated
three of them in the request; withholding them would be theatre. What this adds is COVERAGE the
request did not ask for — cases 4, 5 and 6 below — and, in case 6, a result that bears on the
open design question.

THE DEFECT (author's reading, verified against p4_evidence.py)
    :402-404  _man_path = consumable if not blockers else .FAILED   <- blockers READ
    :413-415  both sibling receipts written on the same _sfx
    :421-424  verifier_crosscheck enforcement                        <- blockers ADDED
So the five recomputed-vs-observed bindings the stage exists to confirm cannot influence where its
own evidence lands. Repair-6 upgraded them from printed-and-ignored to enforced, and the fix landed
BELOW the writer — ignored-by-nobody became ignored-by-the-writer, which reads as closed in source.

Usage:  python3 check_pb3_state.py --evidence-dir <dir> --case <1..6>
"""
import argparse, json, sys
from pathlib import Path

CONSUMABLE = ("p4_standard_manifest.json", "p4_endpoint_evidence.json", "p4_merged_audit.json")
CROSSCHECK_KEYS = ("central5d", "mask5d", "central4d", "mask4d")

CASES = {
    1: dict(
        inject="exactly ONE of the verifier_crosscheck keys recomputes to DIFF; every other check passes",
        expect="NO consumable product; all three redirected",
        why="the live defect. Pre-fix this writes all three consumable and then registers the blocker.",
    ),
    2: dict(
        inject="nothing — a fully clean run",
        expect="all three consumable present; NO .FAILED sibling of any of them",
        why="over-rejection control, and the one most likely to break under reordering. A partial "
            "write or a lingering .FAILED reads as a blocked run to the next consumer.",
    ),
    3: dict(
        inject="an EARLY blocker only — native-miss census (:195-212); crosscheck passes",
        expect="NO consumable product; all three redirected",
        why="confirms the redirect that already works was not broken by the change. Regression, "
            "not defect.",
    ),
    # --- the three the request did not ask for -------------------------------------------------
    4: dict(
        inject="an early blocker AND a crosscheck DIFF in the same run",
        expect="NO consumable product; all three redirected; exactly one .FAILED per product, "
               "not two, and no name collision or double-write",
        why="interaction case. Two blockers registered at different points in the function; if the "
            "redirect is applied per-blocker rather than per-run, this is where it shows.",
    ),
    5: dict(
        inject="run case 1 (blocked), then WITHOUT cleaning the directory run case 2 (clean)",
        expect="all three consumable present AND no .FAILED sibling remains from the earlier run",
        why="the author named stale-.FAILED-read-as-current as the thing they would most likely "
            "introduce. This is that, as a sequence rather than a state: a valid consumable set "
            "sitting beside a stale .FAILED is ambiguous to every consumer, and 'the run passed' "
            "is not visible from the directory.",
    ),
    6: dict(
        inject="terminate the process between the write block (:413-415) and the crosscheck loop "
               "(:421-424) — e.g. SIGTERM, or a raise injected at :418",
        expect="NO consumable product readable as complete",
        why="THIS CASE DISTINGUISHES THE TWO PROPOSED DESIGNS, and it is why I would not pick "
            "reordering on the grounds that a second mechanism is surface. Under pure reordering a "
            "crash DURING the write still leaves partial consumable files, because the write is "
            "still the last thing that happens and it is not atomic. Under .PENDING + "
            "rename-on-complete a crash at any point leaves a .PENDING, which is self-describing "
            "and cannot be mistaken for a product. The repo already treats write-to-temp + "
            "atomic-rename as the correct resume protocol (BEN-023, and the atomic ROOT publish in "
            "run_p4_unfold_std.sh), so .PENDING is the existing convention rather than a new "
            "mechanism.",
    ),
}


def fail(msg):
    print(f"FAIL :: {msg}")
    return False


def check(evdir: Path, case: int) -> bool:
    present = {n: (evdir / n).exists() for n in CONSUMABLE}
    failed = {n: sorted(p.name for p in evdir.glob(n.replace(".json", "") + "*.FAILED*"))
              for n in CONSUMABLE}
    ok = True

    if case in (1, 3, 4, 6):
        for n, p in present.items():
            if p:
                ok = fail(f"{n} present under its CONSUMABLE name; the run was blocked "
                          f"({'crash' if case == 6 else 'blocker registered'})")
        if case in (1, 3, 4):
            for n, sibs in failed.items():
                if not sibs:
                    ok = fail(f"{n}: no redirected sibling — evidence vanished rather than being "
                              f"quarantined, which is a different defect from the one under test")
        if case == 4:
            for n, sibs in failed.items():
                if len(sibs) > 1:
                    ok = fail(f"{n}: {len(sibs)} redirected siblings {sibs} — redirect applied "
                              f"per-blocker rather than per-run")

    if case in (2, 5):
        for n, p in present.items():
            if not p:
                ok = fail(f"{n} missing under its consumable name on a clean run")
        for n, sibs in failed.items():
            if sibs:
                ok = fail(f"{n}: stale redirected sibling(s) {sibs} beside a valid product — "
                          f"ambiguous to every consumer" + (" (case 5: left by the prior blocked "
                          "run)" if case == 5 else ""))
        for n in CONSUMABLE:
            if present[n]:
                try:
                    json.loads((evdir / n).read_text())
                except Exception as e:
                    ok = fail(f"{n} is not parseable JSON ({e}) — a partial write reads as a product")

    if case == 2 and present[CONSUMABLE[0]]:
        try:
            man = json.loads((evdir / CONSUMABLE[0]).read_text())
            xc = man.get("verifier_crosscheck", {})
            missing = [k for k in CROSSCHECK_KEYS if k not in xc]
            if missing:
                ok = fail(f"manifest omits crosscheck keys {missing} — a clean run must record all "
                          f"of them, or PB3 lets a run pass by not reporting the check")
            bad = [k for k, v in xc.items() if not v]
            if bad:
                ok = fail(f"consumable manifest records failing crosscheck keys {bad} — this is "
                          f"case 1 mislabelled as clean")
        except Exception as e:
            ok = fail(f"could not read manifest crosscheck block: {e}")

    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--evidence-dir", required=True)
    ap.add_argument("--case", required=True, type=int, choices=sorted(CASES))
    ap.add_argument("--describe", action="store_true")
    a = ap.parse_args()

    c = CASES[a.case]
    print(f"PB3 case {a.case}\n  inject: {c['inject']}\n  expect: {c['expect']}\n  why: {c['why']}\n")
    if a.describe:
        return 0
    ok = check(Path(a.evidence_dir), a.case)
    print("RESULT :: PASS" if ok else "RESULT :: FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
