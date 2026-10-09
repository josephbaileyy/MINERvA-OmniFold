"""Event identity, the hash split and the contamination tests of DESIGN-20261008 §4 (C1-C6).

Not specific to N2: any held-out design on an identity-carrying rebuild (a transfer test, a
redesigned validation) needs the same keys, split and tests.

A table is a mapping of column name to equal-length array. The identity of an MC row is
``(source, mc_run, mc_subrun, mc_nthEvtInFile)``; ``source`` is the playlist. Row order is never an
identity. A missing identity column, a missing or negative value, or a repeated key inside one tree
is refused: B §4 makes any MC duplicate a stop condition, so ``occurrence`` is never used to rescue
one. Every check raises ``IdentityError`` and returns nothing on success, so a check cannot be
"passed" by ignoring a return value.
"""

import hashlib
import json

import numpy as np

KEY = ("source", "mc_run", "mc_subrun", "mc_nthEvtInFile")
TREES = ("mc_signal_reco", "mc_truth_denom", "mc_background")
FOLDS = ("development", "reservoir", "training")


class IdentityError(ValueError):
    """An identity, split or contamination requirement failed."""


def keys(table, tree):
    """The rows' identity keys as a list of tuples, refusing missing or malformed identities."""
    missing = [c for c in KEY if c not in table]
    if missing:
        raise IdentityError(f"{tree}: no identity column(s) {missing}")
    n = {len(table[c]) for c in KEY}
    if len(n) != 1:
        raise IdentityError(f"{tree}: identity columns have unequal lengths {sorted(n)}")
    out = []
    for i, row in enumerate(zip(*(table[c] for c in KEY))):
        source, numbers = row[0], row[1:]
        if source is None or str(source) == "" or any(
                v is None or (isinstance(v, float) and not np.isfinite(v)) or int(v) != v or v < 0
                for v in numbers):
            raise IdentityError(f"{tree}: row {i} has a missing or invalid identity {row}")
        out.append((str(source), *(int(v) for v in numbers)))
    if len(set(out)) != len(out):
        seen, dup = set(), None
        for k in out:
            if k in seen:
                dup = k
                break
            seen.add(k)
        raise IdentityError(f"{tree}: identity {dup} repeats; an MC duplicate is a stop condition")
    return out


def fold_coordinate(salt, key):
    """``u = int(sha256(salt|source|run|subrun|nth)[:16], 16) / 2**64``.

    The ``|`` separator and decimal integers are this module's encoding; B §4 writes the
    concatenation without fixing one, so the registration must name this function.
    """
    text = "|".join([salt, *map(str, key)])
    return int(hashlib.sha256(text.encode()).hexdigest()[:16], 16) / 2.0 ** 64


def assign(salt, key, thresholds):
    """Fold of one key: development ``[0, d)``, reservoir ``[d, d + rho)``, training the rest."""
    d, rho = thresholds["development"], thresholds["reservoir"]
    u = fold_coordinate(salt, key)
    return FOLDS[0] if u < d else FOLDS[1] if u < d + rho else FOLDS[2]


def _check_thresholds(salt, thresholds):
    if not salt:
        raise IdentityError("the split needs a registered salt")
    d, rho = thresholds["development"], thresholds["reservoir"]
    if not (0 <= d and 0 < rho and d + rho < 1):
        raise IdentityError(f"invalid thresholds {thresholds}")


def materialize(tables, salt, thresholds):
    """``{fold: {tree: table}}``: the R1 step, selecting each tree's rows by their key's fold.

    A key lands in one fold in every tree, which is the whole-event grouping.
    """
    _check_thresholds(salt, thresholds)
    out = {f: {} for f in FOLDS}
    for tree in TREES:
        if tree not in tables:
            raise IdentityError(f"no {tree} table")
        fold = np.array([assign(salt, k, thresholds) for k in keys(tables[tree], tree)])
        for f in FOLDS:
            out[f][tree] = {c: np.asarray(v)[fold == f] for c, v in tables[tree].items()}
    return out


def fold_keys(fold_tables):
    """``{tree: {fold: set(keys)}}`` of MATERIALIZED folds, refusing missing or repeated IDs.

    The contamination tests take this, never a split recomputed from the rule: a recomputed split
    is disjoint by construction, so testing it would pass whatever was actually handed over.
    """
    out = {t: {} for t in TREES}
    for f in FOLDS:
        for t in TREES:
            if t not in fold_tables.get(f, {}):
                raise IdentityError(f"fold {f} has no {t} table")
            out[t][f] = set(keys(fold_tables[f][t], f"{f}/{t}"))
    return out


def check_rule(folds, salt, thresholds):
    """Every materialized key sits in the fold the registered rule assigns it."""
    _check_thresholds(salt, thresholds)
    for t, fs in folds.items():
        for f, ks in fs.items():
            wrong = [k for k in ks if assign(salt, k, thresholds) != f]
            if wrong:
                raise IdentityError(f"{t}/{f}: {len(wrong)} identities the rule assigns elsewhere, "
                                    f"e.g. {sorted(wrong)[0]}")


def _digest(key_set):
    return hashlib.sha256("".join(f"{'|'.join(map(str, k))}\n"
                                  for k in sorted(key_set)).encode()).hexdigest()


def manifest(folds, salt, thresholds):
    """The split manifest: the rule plus per-(tree, fold) counts and key-list digests."""
    body = {"salt": salt, "thresholds": thresholds, "key": list(KEY),
            "encoding": "sha256('|'.join([salt, source, run, subrun, nth]))[:16] / 2**64",
            "folds": {t: {f: {"n": len(s), "sha256": _digest(s)} for f, s in fs.items()}
                      for t, fs in folds.items()}}
    body["manifest_sha256"] = hashlib.sha256(json.dumps(body, sort_keys=True).encode()).hexdigest()
    return body


def verify_manifest(recorded, folds):
    """Refuse unless the materialized folds are exactly the ones the manifest records."""
    body = {k: v for k, v in recorded.items() if k != "manifest_sha256"}
    if hashlib.sha256(json.dumps(body, sort_keys=True).encode()).hexdigest() != \
            recorded.get("manifest_sha256"):
        raise IdentityError("split manifest digest does not match its contents")
    fresh = manifest(folds, recorded["salt"], recorded["thresholds"])
    if fresh["folds"] != recorded["folds"]:
        raise IdentityError("the materialized folds differ from the recorded split manifest")


def check_c1_disjoint(folds):
    """C1: fold identity sets pairwise disjoint, within and across trees."""
    union = {f: set().union(*(folds[t][f] for t in folds)) for f in FOLDS}
    for i, a in enumerate(FOLDS):
        for b in FOLDS[i + 1:]:
            both = union[a] & union[b]
            if both:
                raise IdentityError(f"C1: {len(both)} identities in both {a} and {b}, "
                                    f"e.g. {sorted(both)[0]}")


def check_c2_bijection(folds):
    """C2: within each fold the signal and truth-denominator identity sets are equal."""
    for f in FOLDS:
        a, b = folds["mc_signal_reco"][f], folds["mc_truth_denom"][f]
        if a != b:
            raise IdentityError(f"C2: {f}: {len(a - b)} signal-only and {len(b - a)} "
                                "denominator-only identities")


def check_c3_signal_background(folds):
    """C3: no identity is in both the signal and the background tree."""
    sig = set().union(*folds["mc_signal_reco"].values())
    bkg = set().union(*folds["mc_background"].values())
    if sig & bkg:
        raise IdentityError(f"C3: {len(sig & bkg)} identities in both signal and background")


def check_c4_rows_equal(production, rebuilt, branches):
    """C4: every shared branch equal row by row, bit for bit (R0 is production plus identity)."""
    for br in branches:
        a, b = np.asarray(production[br]), np.asarray(rebuilt[br])
        if a.shape != b.shape or a.dtype != b.dtype or a.tobytes() != b.tobytes():
            raise IdentityError(f"C4: branch {br} differs between production and rebuild")


def check_c5_fractions(fold_tables, thresholds, weight="w_truth", n_sigma=5.0):
    """C5: per tree and source, realized row and ``sum(weight)`` fractions of each fold within
    ``n_sigma`` binomial sigma of the design (the weight sigma uses the Kish effective size)."""
    target = {"development": thresholds["development"], "reservoir": thresholds["reservoir"]}
    target["training"] = 1 - target["development"] - target["reservoir"]
    for tree in TREES:
        src = {f: np.asarray(fold_tables[f][tree]["source"]).astype(str) for f in FOLDS}
        w = {f: (np.asarray(fold_tables[f][tree][weight], float)
                 if weight in fold_tables[f][tree] else np.ones(len(src[f]))) for f in FOLDS}
        for s in sorted(set().union(*(set(v) for v in src.values()))):
            n = {f: int((src[f] == s).sum()) for f in FOLDS}
            ws = {f: w[f][src[f] == s] for f in FOLDS}
            allw = np.concatenate(list(ws.values()))
            n_eff = allw.sum() ** 2 / (allw * allw).sum()
            for f, p in target.items():
                for label, frac, size in (("rows", n[f] / sum(n.values()), sum(n.values())),
                                          (weight, ws[f].sum() / allw.sum(), n_eff)):
                    sigma = np.sqrt(p * (1 - p) / size)
                    if abs(frac - p) > n_sigma * sigma:
                        raise IdentityError(f"C5: {tree} {s} {f} {label} fraction {frac:.4f}, "
                                            f"design {p:.4f} +- {n_sigma:g} x {sigma:.4f}")


def check_c6_sidecar(folds, sidecar, intended):
    """C6: every identity in a member's sidecar lies in the fold its role requires.

    ``sidecar`` maps a role (``bank``, ``pseudo_data``, ``background``) to the keys of the rows that
    member handed to OmniFold; ``intended`` maps each role to its fold.
    """
    for role, fold in intended.items():
        if role not in sidecar:
            raise IdentityError(f"C6: the sidecar has no {role} identities")
        allowed = set().union(*(folds[t][fold] for t in folds))
        got = {tuple(k) for k in sidecar[role]}
        stray = got - allowed
        if stray:
            raise IdentityError(f"C6: {len(stray)} {role} identities outside {fold}, "
                                f"e.g. {sorted(stray)[0]}")


def run_all(fold_tables, recorded_manifest):
    """The table checks on MATERIALIZED folds: IDs, the manifest, the rule, C1, C2, C3 and C5.

    C4 takes the production file and C6 each member's sidecar; C7 is a review, not a function.
    """
    folds = fold_keys(fold_tables)
    verify_manifest(recorded_manifest, folds)
    check_rule(folds, recorded_manifest["salt"], recorded_manifest["thresholds"])
    check_c1_disjoint(folds)
    check_c2_bijection(folds)
    check_c3_signal_background(folds)
    check_c5_fractions(fold_tables, recorded_manifest["thresholds"])
    return folds
