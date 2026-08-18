#!/usr/bin/env python3
"""Generate the C_stat^data divergence manifest against the PINNED training validator.

WHAT THIS IS FOR. Lane C's ruling (`BEN-426`) drops the "wrapper contains zero check logic" claim for
this validator -- 55 of its 77 static check sites cannot execute on a data-only artifact, and 71%
reimplementation is not delegation -- and replaces it with an ACCOUNTING obligation: every static check
site lands in EXACTLY ONE of four buckets, and the four counts must SUM TO THE MODULE'S OWN STATIC SITE
COUNT.

    V1 made DIVERGENCE unrepresentable by delegation; the partition makes OMISSION unrepresentable by
    ACCOUNTING.

So the sum is the load-bearing part and it is DERIVED here, by walking the pinned module's AST, never
typed. If a site is added to the pinned module and not classified, the total stops matching and this
script fails.

WHY IT IS WRITTEN NOW, BEFORE THE WRAPPER EXISTS. A manifest derived from a finished wrapper records
what was written rather than what was predicted, and the middle clause of the verdict -- "manifest
checks FAILED EXACTLY AS PREDICTED" -- degenerates to a tautology. The ordering requirement is
therefore load-bearing, and this script ASSERTS it rather than asking to be trusted: it refuses to run
if a data-only validator/wrapper module is present in the tree.

WHAT IT IS NOT. This is a DIVERGENCE control, not a correctness control. It pins the data-only path's
relationship to the coherent one. If the coherent validator is wrong, everything here propagates that
error with a green light.
"""
import ast
import hashlib
import json
import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]   # state/ -> orchestration/ -> docs/ -> repo root
PINNED = REPO / "nd-unfolding/pet/validate_gate5_training_artifacts.py"
PREDICATES = REPO / "nd-unfolding/pet/cstat_data_only.py"
TRAIN_DRIVER = REPO / "nd-unfolding/pet/train_fullevent_replica.py"

# The wrapper must not exist yet. Named explicitly so the assertion is falsifiable rather than a claim
# about the author's intentions.
FORBIDDEN_YET = [
    REPO / "nd-unfolding/pet/validate_gate5_data_only_artifacts.py",
    REPO / "nd-unfolding/pet/validate_gate5_training_artifacts_data_only.py",
]

# --------------------------------------------------------------------------------------------------
# BUCKET 1 -- DELEGATED. Executes byte-identically from the pinned module and is predicted to PASS.
# BUCKET 2 -- UNEXECUTED-BY-CONSTRUCTION. Cannot run because the early return fires first; each needs a
#             NAMED replacement, or is marked REPLACEMENT-REQUIRED with the gap stated.
# BUCKET 3 -- MANIFEST. Executes and is predicted to FAIL, with a DISCRIMINATING predicted `got`.
# BUCKET 4 -- ADDITIONAL. Assertions the data-only path makes that no pinned site performs.
# --------------------------------------------------------------------------------------------------

MANIFEST = {
    # site -> (predicted got, want, why the got is discriminating, replacement)
    217: {
        "check": "required_npz_keys_missing",
        "predicted_got": ["bootstrap_seed"],
        "want": [],
        "discriminating": (
            "A sorted one-element list naming exactly `bootstrap_seed` is reached by ONE artifact "
            "state: a data-only artifact carrying all 26 other required keys and withholding that "
            "one. A second missing key changes the value, and a present-but-wrong `bootstrap_seed` "
            "would make the list empty. Contrast `-1`, which lane C ruled INADMISSIBLE as a predicted "
            "got because `int(r.get('bootstrap_seed', -1))` yields it for both a stamped and a lost "
            "field -- the discriminating power is a property of the predicted VALUE, not the clause."),
        "replacement": "cstat_data_only.assert_pinned_required_keys",
        "consequence": (
            "THIS ENTRY IS WHY BUCKET 2 EXISTS. This site's failure triggers the early return at :218, "
            "so the 55 sites after it never execute. The entry is not one failure among many; it is "
            "the cause of 55 absences."),
    },
    176: {
        "check": "receipt_array_job",
        "predicted_got": "DEFERRED-TO-SUBMISSION",
        "want": "56857233",
        "discriminating": (
            "RUN-BOUND, not product-bound. `ARRAY_JOB_ID = \"56857233\"` (:27) names ONE campaign run, "
            "so this site fails for ANY other array -- a three-stream re-run included. Its predicted "
            "got is the new array's job id, which does not exist until `sbatch` returns."),
        "replacement": "submission-time addendum, written before any artifact exists",
        "consequence": (
            "The ordering requirement is BEFORE THE ARTIFACT EXISTS, not before the run is submitted. "
            "A job id recorded between `sbatch` and the first task's write is still not read off a "
            "finished product, so the anti-tautology property survives the deferral. Stating it the "
            "other way round would make the entry unwritable rather than merely late."),
    },
    178: {
        "check": "receipt_runtime_head",
        "predicted_got": "DEFERRED-TO-TRAINING-DEPLOYMENT",
        "want": "b82ac63f9c5685c9cc05df059d2bbb4ae42d3258",
        "discriminating": (
            "RUN-BOUND via `EXPECTED_HEAD` (:30). The got is the full sha of the TRAINING deployment's "
            "detached HEAD, which is knowable the moment that deployment is cut and not before -- and "
            "it is deliberately NOT the target deployment's, because the two are cut separately."),
        "replacement": "submission-time addendum, written before any artifact exists",
    },
    190: {
        "check": "receipt_code_sha256[<role>]",
        "realizes": 3,
        "predicted_got": {
            "replica_driver": "MEASURED-AT-GENERATION-TIME",
            "nominal_driver_unmodified": "PASSES",
            "loader": "PASSES",
        },
        "want": "EXPECTED_CODE (:33-37)",
        "discriminating": (
            "One static site realizing three checks, and they SPLIT -- which is why this site is in "
            "MANIFEST with its passing subset named rather than being silently averaged. "
            "`replica_driver` fails because the data-only work edited that file; its predicted got is "
            "the digest of the deployed file, which is a property of one specific version and is "
            "therefore discriminating."),
        "replacement": "none needed for the failing role: the pinned check still runs and still means "
                       "what it says; only its `want` belongs to the other campaign",
        "load_bearing_passes": (
            "*** THE TWO PASSING ROLES ARE THE CROSS-BLOCK LOADER EVIDENCE, AND THEY ARE ALREADY "
            "PINNED. *** `receipt_code_sha256[loader]` compares this family's recorded loader digest "
            "against a CONSTANT from the coherent campaign, so its passing establishes "
            "gen2-loader == coherent-loader directly. That is stronger than asserting the target and "
            "training blocks equal EACH OTHER, which passes if both drift together. Recommended form "
            "of C's fourth-bucket requirement: compare BOTH blocks to the same pinned third value."),
    },
}

# Bucket 2. Each site names a covering predicate, or REPLACEMENT-REQUIRED with the gap stated.
# A name here is CHECKED to exist below -- the manifest cannot cite a replacement that does not.
UNEXECUTED = {
    221: "cstat_data_only.CAMPAIGN_ROLES via validate_data_only_artifact",
    223: "validate_data_only_artifact replica_index check",
    224: "cstat_data_only.assert_data_only_streams",              # P6, under data_bootstrap_seed
    225: "cstat_data_only_readback.assert_artifact_policy_scalars",
    227: "cstat_data_only_readback.assert_artifact_policy_scalars",
    228: "cstat_data_only_readback.assert_artifact_policy_scalars",
    229: "cstat_data_only_readback.assert_artifact_policy_scalars",
    230: "cstat_data_only_readback.assert_artifact_policy_scalars",
    231: "cstat_data_only_readback.assert_artifact_policy_scalars",
    236: "cstat_data_only.assert_data_only_streams",              # n_sig_full
    237: "cstat_data_only.assert_data_only_streams",              # n_data_full
    238: "cstat_data_only.assert_data_only_streams",              # n_bkg_full
    239: "cstat_data_only_readback.assert_inventory_identity_agree_with_target",
    241: "cstat_data_only_readback.assert_inventory_identity_agree_with_target",
    248: "cstat_data_only_readback.assert_subsample_geometry",
    251: "cstat_data_only.assert_data_only_streams",              # P2 full-length shape
    252: "cstat_data_only_readback.assert_subsample_geometry",
    253: "train_fullevent_replica.replica_atomic_data_only write-time restriction assertion",
    255: "cstat_data_only_readback.assert_subsample_geometry",
    257: "cstat_data_only.assert_data_only_streams",              # P3 full-length shape
    # CLOSED. The replacement asserts INEQUALITY on the MC legs -- the positive form of "left
    # unthinned" -- and EQUALITY on the shared data leg, so it is not a blanket inversion. Called from
    # BOTH readers, one home, and it refuses the degenerate case where a canonical digest equals the
    # unity digest, because there no inequality can distinguish "left unthinned" from "nothing to thin".
    262: "cstat_data_only.assert_unthinned_mc_evidence",
    263: "cstat_data_only.assert_unthinned_mc_evidence",
    265: "cstat_data_only.assert_unthinned_mc_evidence",
    267: "cstat_data_only.assert_unthinned_mc_evidence",
    272: "extract_fullevent_replica.factor_meta data-only branch comparison",
    275: "cstat_data_only_readback.assert_target_binding",
    276: "cstat_data_only_readback.assert_target_binding",
    278: "cstat_data_only_readback.assert_target_binding",
    282: "cstat_data_only_readback.assert_target_meta_fields",
    283: "cstat_data_only.assert_data_only_target_is_this_replicas",   # F1/F3
    284: "cstat_data_only_readback.assert_target_meta_fields",
    285: "cstat_data_only_readback.assert_target_meta_fields",
    286: "cstat_data_only.assert_data_only_target_is_this_replicas",   # F2, family position
    292: "cstat_data_only_readback.assert_lr_policy_realized",
    293: "cstat_data_only_readback.assert_lr_policy_realized",
    294: "cstat_data_only_readback.assert_lr_policy_realized",
    295: "cstat_data_only_readback.assert_lr_policy_realized",
    298: "cstat_data_only_readback.assert_lr_policy_realized",
    300: "cstat_data_only_readback.assert_lr_policy_realized",
    304: "cstat_data_only_readback.assert_weights_push_sane",
    305: "cstat_data_only_readback.assert_weights_push_sane",
    306: "cstat_data_only_readback.assert_weights_push_sane",
    315: "cstat_data_only_readback.assert_checkpoints_and_contract",
    318: "cstat_data_only_readback.assert_checkpoints_and_contract",
    320: "cstat_data_only_readback.assert_checkpoints_and_contract",
    324: "cstat_data_only_readback.assert_checkpoints_and_contract",
    326: "cstat_data_only_readback.assert_checkpoints_and_contract",
    333: "cstat_data_only_readback.assert_member_logs",
    334: "cstat_data_only_readback.assert_member_logs",
    337: "cstat_data_only_readback.assert_member_logs",
    339: "cstat_data_only_readback.assert_member_logs",
    340: "cstat_data_only_readback.assert_member_logs",
    342: "cstat_data_only_readback.assert_member_logs",
    343: "cstat_data_only_readback.assert_member_logs",
    345: "cstat_data_only_readback.assert_member_logs",
}

# Bucket 4 -- ADDITIONAL: what the data-only path asserts that NO pinned site does. Each names its gap.
ADDITIONAL = [
    {"assertion": "P1 cstat_product tag", "closes":
     "the pinned validator has no notion of a product tag, so nothing there distinguishes the two "
     "families at all"},
    {"assertion": "P5a bit-exact zero pattern on the MC legs", "closes":
     "no pinned site asserts that NOTHING happened to the MC legs; bit-exactness is required because "
     "an absence has no rounding (BEN-409)"},
    {"assertion": "P5b / measured-leg closure at 4 float32 eps", "closes":
     "no pinned site knows the measured normalization was rescaled driver-side"},
    {"assertion": "P7 ratio-provenance block", "closes":
     "the loader's own R stamp is left unmodified and the applied R recorded beside it; no pinned site "
     "can tell those apart"},
    {"assertion": "P8 loader stamp unmodified", "closes":
     "no pinned site checks that a loader-written field was not overwritten"},
    {"assertion": "F2 family-position target derivation", "closes":
     "every pinned target check binds the file to ITS OWN receipt; only a family-position route "
     "notices a self-consistent stray copy"},
    {"assertion": "L2 tag-matches-root, both ways", "closes":
     "no pinned site relates an artifact's product to the family root it sits in"},
    {"assertion": "the nominal-extractor routing refusal", "closes":
     "extract_fullevent_fps.py:178 accepts bootstrap_seed == -1 as proof of nominal AND returns -1 as "
     "its absent default, so a data-only artifact satisfies it whether the field is stamped or "
     "missing -- a guard that cannot be satisfied honestly must never be REACHED (BEN-426)"},
    {"assertion": "the withheld-key both-directions check", "closes":
     "no pinned site asserts a key's ABSENCE, and a present-but-None bootstrap_seed would clear the "
     "required-key gate and then raise TypeError from :224's int() -- a traceback where a named "
     "failure belongs"},
]


def static_sites(path):
    tree = ast.parse(path.read_text())
    fn = next(n for n in tree.body
              if isinstance(n, ast.FunctionDef) and n.name == "validate_member")
    early = None
    for n in ast.walk(fn):
        if isinstance(n, ast.If) and isinstance(n.test, ast.BinOp) \
                and "required_keys" in ast.unparse(n.test) \
                and any(isinstance(b, ast.Return) for b in n.body):
            early = n.lineno
    if early is None:
        raise SystemExit("could not locate the required-key early return")
    out = []
    for n in ast.walk(fn):
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) \
                and n.func.attr in ("eq", "truth", "close") \
                and isinstance(n.func.value, ast.Name) and n.func.value.id == "checks":
            out.append({"line": n.lineno, "kind": n.func.attr,
                        "check": ast.unparse(n.args[0]).strip() if n.args else "?",
                        "phase": "executed" if n.lineno < early else "unexecuted"})
    out.sort(key=lambda s: s["line"])
    return early, out


def main():
    for f in FORBIDDEN_YET:
        if f.exists():
            raise SystemExit(
                f"[manifest] {f} EXISTS. This manifest must be written before the wrapper, or its "
                f"predictions record what was written rather than what was predicted and the verdict's "
                f"middle clause is a tautology. Refusing to regenerate.")

    early, sites = static_sites(PINNED)
    by_line = {s["line"]: s for s in sites}
    executed = [s for s in sites if s["phase"] == "executed"]
    unexecuted = [s for s in sites if s["phase"] == "unexecuted"]

    manifest_lines = set(MANIFEST)
    delegated = [s for s in executed if s["line"] not in manifest_lines]

    # --- the accounting obligation, DERIVED ---
    counts = {
        "DELEGATED": len(delegated),
        "UNEXECUTED_BY_CONSTRUCTION": len(unexecuted),
        "MANIFEST": len(manifest_lines),
        "ADDITIONAL": len(ADDITIONAL),
    }
    partitioned = counts["DELEGATED"] + counts["UNEXECUTED_BY_CONSTRUCTION"] + counts["MANIFEST"]
    if partitioned != len(sites):
        raise SystemExit(f"[manifest] partition sums to {partitioned}, not {len(sites)}: every static "
                         f"site must land in exactly one bucket")
    missing = sorted(set(s["line"] for s in unexecuted) - set(UNEXECUTED))
    if missing:
        raise SystemExit(f"[manifest] unclassified unexecuted sites: {missing}")
    stray = sorted(set(UNEXECUTED) - set(s["line"] for s in unexecuted))
    if stray:
        raise SystemExit(f"[manifest] UNEXECUTED names sites that are not unexecuted: {stray}")
    if any(ln not in by_line for ln in manifest_lines):
        raise SystemExit("[manifest] MANIFEST names a line with no check site")

    # every non-REPLACEMENT-REQUIRED replacement must actually exist
    # Every module a replacement may be cited from, read as text. A citation that names a symbol none
    # of these contains is an error here rather than a promise in a document.
    sources = "\n".join(p.read_text() for p in (
        PREDICATES, TRAIN_DRIVER, REPO / "nd-unfolding/pet/extract_fullevent_replica.py",
        REPO / "nd-unfolding/pet/cstat_data_only_readback.py"))
    unresolved = []
    for line, repl in sorted(UNEXECUTED.items()):
        if repl.startswith("REPLACEMENT-REQUIRED"):
            continue
        symbol = repl.split(".")[-1].split(" ")[0]
        if symbol not in sources:
            unresolved.append((line, symbol))
    if unresolved:
        raise SystemExit(f"[manifest] cited replacements that do not exist: {unresolved}")

    needed = sorted(l for l, r in UNEXECUTED.items() if r.startswith("REPLACEMENT-REQUIRED"))
    covered = sorted(l for l, r in UNEXECUTED.items() if not r.startswith("REPLACEMENT-REQUIRED"))

    # === EXISTING IS NOT WIRED, AND `0 REQUIRED` MUST NOT BE READ AS `VALIDATED` ===
    #
    # A cited replacement can EXIST and be called by NOBODY. `n_required == 0` is then true of the
    # PREDICATE INVENTORY and false of the validation: the family still cannot be graded, because no
    # caller invokes the set over its 50 members. That distinction is the whole difference between "the
    # checks are written" and "the checks run", which is `BEN-416`'s lesson from this same session --
    # so it is measured here rather than left for a reader to assume.
    #
    # Detection is by CALL SITE, not by substring: a symbol's name appears in the module that DEFINES
    # it, and a mention is not a use.
    # The rule is deliberately the SIMPLE one -- a symbol is CALLED if any Call node names it in any of
    # these modules, including the one that defines it. A more clever rule (calls from OTHER modules
    # only) reported `validate_data_only_artifact` as uncalled because its caller is its own module,
    # which is a false alarm; and reachability-from-main is a bigger analysis than the question needs.
    # None of these predicates is recursive, so a self-call cannot mask a genuinely dead one.
    #
    # NON-FUNCTION citations (`CAMPAIGN_ROLES`, `factor_meta`) are excluded: they are data and a variable
    # read is not a call, so scoring them as uncalled would inflate the gap with entries that are fine.
    called = set()
    all_defined = set()
    for mod in (PREDICATES, TRAIN_DRIVER,
                REPO / "nd-unfolding/pet/extract_fullevent_replica.py",
                REPO / "nd-unfolding/pet/cstat_data_only_readback.py"):
        tree = ast.parse(mod.read_text())
        all_defined |= {n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)}
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                f = node.func
                name = f.attr if isinstance(f, ast.Attribute) else getattr(f, "id", None)
                if name:
                    called.add(name)
        # AND A BARE NAME LOAD COUNTS AS WIRING, because this campaign's idiom is SUBSTITUTION rather
        # than direct invocation: `nominal.atomic_savez_compressed = replica_atomic_data_only` and
        # `validator = validate_data_only_artifact` wire a predicate in without ever producing a Call
        # node at that site. Counting only calls reported both of those as dead, which is a false alarm
        # of exactly the kind this field exists to avoid producing.
        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                called.add(node.id)
    cited = {}
    for line, repl in UNEXECUTED.items():
        if repl.startswith("REPLACEMENT-REQUIRED"):
            continue
        sym = repl.split(".")[-1].split(" ")[0]
        cited.setdefault(sym, []).append(line)
    uncalled = {sym: sorted(lines) for sym, lines in sorted(cited.items())
                if sym in all_defined and sym not in called}
    n_sites_uncalled = sum(len(v) for v in uncalled.values())

    doc = {
        "schema": "gate5-cstat-data-only-divergence-manifest-v1",
        "what_this_is": "A DIVERGENCE control, not a correctness control. It pins the data-only path's "
                        "relationship to the coherent one and establishes nothing about whether the "
                        "coherent validator is correct; if that one is wrong, this propagates the "
                        "error with a green light.",
        "written_before_the_wrapper_exists": True,
        "what_the_ordering_assertion_protects": (
            "The PREDICTIONS -- bucket 3's got/want -- which are frozen at the sha that committed them. "
            "It does NOT and cannot freeze the replacement BOOKKEEPING, which is meant to track work as "
            "predicates land, so `covered`/`REPLACEMENT_REQUIRED` move between regenerations by design. "
            "Said explicitly because the two live in the same JSON and an assertion that appears to "
            "freeze more than it does is worse than one that freezes less and says so."),
        "written_before_assertion": [str(f.relative_to(REPO)) for f in FORBIDDEN_YET],
        "pinned_module": {
            "path": str(PINNED.relative_to(REPO)),
            "sha256": hashlib.sha256(PINNED.read_bytes()).hexdigest(),
            "why_the_digest": "so a legitimate re-issue of the pinned module is distinguishable from "
                              "this manifest breaking, in one comparison. Without it a re-issue "
                              "produces a loud failure whose tempting resolution is to refresh the "
                              "manifest -- the read-off-the-finished-artifact defect through the back "
                              "door.",
            "static_check_sites": len(sites),
            "early_return_line": early,
            "executed_on_a_data_only_artifact": len(executed),
            "unexecuted_on_a_data_only_artifact": len(unexecuted),
        },
        "partition_counts": counts,
        "partition_sums_to": partitioned,
        "correction_to_the_spec": (
            "The ruling says every one of the 77 sites lands in exactly one of FOUR buckets and the "
            "counts must sum to 77. Those two clauses cannot both hold: ADDITIONAL is defined as "
            "assertions the data-only path makes that NO pinned site performs, so its members are not "
            "pinned check sites and cannot be part of a partition of them. Buckets 1-3 partition the "
            "77 and are checked to sum to it; ADDITIONAL is disjoint by construction and is reported "
            "beside the sum, not inside it. Folding it in would inflate the total by the number of "
            "assertions I chose to add, which is the one number in this document that its author "
            "controls -- and a total an author can raise is not a floor."),
        "v4_floor": {
            "floor_on": "executed check sites (n_passed + n_failed), NOT manifest size",
            "why": "a floor on manifest size is authored by the same party as the manifest, so it "
                   "cannot see 55 checks that never ran. C's improvement: the executed count must "
                   "EQUAL what the coherent partition observes, so the operand comes from the other "
                   "path rather than from the manifest's author.",
            "expected_executed_static_sites": len(executed),
        },
        "buckets": {
            "DELEGATED": [dict(s, note="executes byte-identically from the pinned module") for s in delegated],
            "MANIFEST": {str(k): dict(v, site=by_line[k]) for k, v in MANIFEST.items()},
            "UNEXECUTED_BY_CONSTRUCTION": [
                dict(by_line[l], replacement=UNEXECUTED[l]) for l in sorted(UNEXECUTED)],
            "ADDITIONAL": ADDITIONAL,
        },
        "replacement_status": {
            "covered_by_an_existing_predicate": covered,
            "REPLACEMENT_REQUIRED": needed,
            "n_covered": len(covered),
            "n_required": len(needed),
            "honesty_note": "The REPLACEMENT_REQUIRED count is the real measure of remaining work and "
                            "is deliberately NOT hidden behind invented names. A manifest that named a "
                            "replacement for all 55 would assert coverage it does not have, which is "
                            "the exact defect the partition exists to make unrepresentable.",
            "written_but_UNCALLED": uncalled,
            "n_sites_whose_replacement_no_caller_INVOKES": n_sites_uncalled,
            "why_this_field_exists":
                "`REPLACEMENT_REQUIRED == 0` is true of the PREDICATE INVENTORY and does NOT mean the "
                "family can be validated. A cited replacement can exist and be called by nobody, and "
                "the family is graded only when a caller invokes the set over its 50 members. "
                "'The checks are written' and 'the checks run' are different claims -- BEN-416, from "
                "this same session -- so the gap is measured rather than left to be assumed. Detected "
                "by CALL SITE and not by substring, because a symbol's name appears in the module that "
                "defines it and a mention is not a use.",
        },
    }
    out = REPO / "docs/orchestration/state/DIVERGENCE-MANIFEST-20260818-cstat-data-only.json"
    out.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n")
    print(f"{len(sites)} static sites = {counts['DELEGATED']} DELEGATED "
          f"+ {counts['UNEXECUTED_BY_CONSTRUCTION']} UNEXECUTED + {counts['MANIFEST']} MANIFEST")
    print(f"ADDITIONAL (not part of the sum, by construction): {counts['ADDITIONAL']}")
    print(f"replacements: {len(covered)} covered, {len(needed)} REQUIRED")
    print(f"of the covered, {n_sites_uncalled} site(s) have a replacement NO CALLER INVOKES "
          f"({len(uncalled)} predicate(s): {sorted(uncalled)})")
    print(f"wrote {out.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
