# DETERMINATION — the `C_stat^data` route: C's prescribed override CANNOT WORK, and the loader says so itself

**Lane E, 2026-08-17.** Step 2 of the data-only-`C_stat` dispatch: establish the code route to
data-only factors and its pin exposure, and report **what it would cost to BUILD** — not to run.

**Read-only. Nothing submitted, no GPU, no training, no unfolding, nothing inside the promoted arm.
No write to any production file: every probe restored byte-exactly. The 151 A100-h is authorized and
unspent.**

---

## 0. The finding, and it is the third time today the unpinned side turned out not to be the acting side

> **C's constraint — *"the override belongs in the replica driver, NEVER inside
> `coherent_bootstrap_factors`"* — cannot be satisfied for the SIGNAL stream. Setting `sig_factor = 1`
> in the replica driver has NO EFFECT, because the driver never applies it.**

`fullevent_fps_dataloader.py:1321-1325`, inside the `if bootstrap_seed is not None:` branch:

```python
data_factor, sig_factor, bkg_factor = coherent_bootstrap_factors(M, N, n_bkg_full, int(bootstrap_seed))
w_truth = (w_truth_full[imc] * sig_factor[imc]).astype(np.float32)
w_reco  = (w_reco_full[imc]  * sig_factor[imc]).astype(np.float32)
```

**The loader multiplies the signal factor into the training weights itself, before returning.**
`train_fullevent_replica.py:202-211` re-derives the same factors *to verify the loader's* — it asserts
the loader's background factor equals its own replay and raises otherwise. It is a **checker, not an
applier.**

**And the code already documents this, in the one place a reader of the reconciler would meet it.**
`reconcile_gate5_family.py:526-530`, the replay check's own note:

> *"it compares the BUILDER's recomputation to this tool's redraw, so it is **blind to what the LOADER
> applied**."*

**Nor can it be undone afterwards.** 36.8% of Poisson(1) factors are exactly zero (1/e), so
`w * sig_factor` destroys information rather than scaling it — there is no post-hoc division back to
the unthinned weights. This is `BEN-386` again at a third site: **the file the edit lives in is not
the file that does the work.**

---

## 1. Pin exposure, measured DIFFERENTIALLY because the absolute test is unavailable

The condition *"run `verify_hash_bindings.py` and check it passes"* cannot be met: the gate is **red on
the cluster** for two pre-existing reasons and **green locally**, which is `BEN-255` — the same gate
returns different verdicts in different trees. So the test is whether the mismatch set **grows**.

Local baseline: green, mismatch set `{}`. D's cluster baseline (landed at `caa5d4f`, not regenerated
per `BEN-304`): `{std_final5_candidate.root, train_fullevent_nominal.py}`.

| file the route might touch | digest sites | gate set grows? |
|---|---|---|
| `pet/train_fullevent_replica.py` | **0** | no |
| `pet/build_fullevent_replica_target.py` | 5 | no |
| `pet/extract_fullevent_replica.py` | 2 | no |
| `pet/fullevent_fps_dataloader.py` | **25** | **YES** |
| `pet/reconcile_gate5_family.py` | 5 | **YES** |

**Per my own `BEN-386`, none of the "no" rows licenses calling this cheap.** They say those files are
not frozen; they say nothing about whether an edit there achieves the goal — which is exactly the
trap §0 records.

---

## 2. The three routes, costed to BUILD

**ROUTE A — override in the drivers, as C prescribed. DOES NOT WORK.** §0. It would produce a family
whose *receipts* claim unity signal factors while the *training* consumed Poisson-thinned MC — a
receipt asserting something false about the run, which is the class this campaign exists to refuse.
**Worse than expensive: it is silently wrong, and the reconciler cannot catch it** because its replay
is blind to the loader by its own admission.

**ROUTE B — call the loader with `bootstrap_seed=None`. VIABLE, AND ENTIRELY OFF THE PINNED FILES.**
`fullevent_fps_dataloader.py:1332-1334`, the `else` branch, returns genuinely unthinned MC
(`w_truth = w_truth_full[imc]`), and the replica driver **already intercepts the loader call** —
`nominal.fe.build_fullevent_loaders = replica_build` — so the driver can choose. The data stream is
then applied where it is *already* driver-level: `build_fullevent_replica_target.py:216`. **The
loader's helpers already have unity paths** for the measured side (`:696`, `:945-948` default
`data_factor=None` → `np.ones`), so nothing new is needed there.

**What Route B costs to build, and it is not a one-liner:**
1. `train_fullevent_replica.py` — the bootstrap-evidence assertions at `:196-198` raise when
   `meta["bootstrap"]` is `None`, and the artifact-provenance block stamps `sig_bootstrap_factor`,
   `n_sig_full`, `inventory_hashes` out of that dict. Both need a data-only branch that stamps
   **unity explicitly** rather than omitting the field — an absent field reads as "not a bootstrap
   replica", which is the `PB2` null-as-absent trap.
2. `build_fullevent_replica_target.py` — pass unity for the background factor. Clean on the gate;
   5 digest sites to read before writing.
3. `extract_fullevent_replica.py:146` — its replay draws all three; it must expect unity for two.
4. **A new verdict path in `reconcile_gate5_family.py`, which IS pin-exposed** (probe: set grows).

**ROUTE C — add a `sig_factor=None` unity path to the loader.** Cleanest code, **blocked**: the probe
shows the gate set grows on that file, and it is `OI-60`'s 25-site / 151-A100-hour cascade.

---

## 3. The reconciler needs TWO fixes, not one — and C named the second

C flagged `:837-845`: four `_sha_all_distinct` labels, of which `signal_factor` and
`background_factor` would be identical across all 50 by design. Correct. **There is an earlier and
distinct failure:**

`:519-530` **re-draws all three streams from the declared seed and compares hashes** to the receipt's.
A data-only family stamps unity; the reconciler recomputes Poisson; `signal_factor_sha256_REDRAWN` and
`background_factor_sha256_REDRAWN` **mismatch before distinctness is ever evaluated.**

So `C_stat^data` needs its own verdict path covering **both** mechanisms, and — holding C's line —
**not a relaxation of either**, which would leave the three-stream family unprotected against the
failure the guard was written for. C's warning about the shape stands and is sharpened: the profile is
now *2 of 4 distinctness labels plus 2 of 3 replay comparisons*, which is even more inviting of a
short exemption. Do not take it.

---

## 4. What this does NOT establish

- **No cost to RUN is given**, and none is asked for. The 151 A100-h is authorized; this is about
  whether a correct route to it exists.
- **I have not built or run anything.** Route B is *viable on inspection and on the pin axis*. Per my
  own rule, that is the strongest available claim — **a sweep can show an item is expensive and never
  that it is cheap** — and today Route A looked viable on exactly this kind of inspection until the
  loader's own multiply was read.
- **I did not touch the OI-126 measurement legs.** The occupancy check, the `N_eff`-per-cell join and
  the 63-band-cells-reported-separately requirement are a different task; this is the construction
  route only. D's target-leg test is untouched.
- **The data-only-versus-total spec question is not settled here.** C's ruling (A) makes it moot for
  *this* product's existence, but note the asymmetry the mediator raised survives either way: the
  data factors are Poisson(1) too (`:621`), so **only the MC part of the nominal/replica training
  asymmetry is removed** and *"nominal inside implies MC-thinning"* is not a valid inference.
