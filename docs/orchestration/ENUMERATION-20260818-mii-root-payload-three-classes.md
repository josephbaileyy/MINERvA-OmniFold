# `M(ii)` stage-1 ROOT-side payload enumeration — R3's three classes applied to four artifacts

**Lane B, 2026-08-18.** Produced because C ruled that **stage 1 cannot gate until this exists**.

**PROVENANCE SPLIT, stated first because it bounds every claim below.**
- **Key listings from the ARCHIVE** are the mediator's, read on the cluster this turn. `import ROOT`
  fails on this machine, so I cannot read a `.root` file at all and have not tried to.
- **Key listings from the WRITERS** are mine, read from source at the shas cited, in this worktree.
- **These two are not the same set, and the gap is this document's principal finding.** Neither party
  could have found it alone: the mediator had the archive without the writers, I had the writers
  without the archive.

---

## 0. THE HEADLINE — THE ARCHIVE PREDATES ITS OWN WRITERS' PROVENANCE BLOCKS

Every one of the four artifacts is written today with **more keys than the archive's copy contains**,
for reasons that **have nothing to do with the estimator seed**:

| artifact | archive keys (mediator) | current writer emits | extra in a member |
|---|---|---|---|
| `uq_5d/unified_throw_cov_5d.root` | **9** | **14** | **5** |
| `..._uthrow.root` (892 MB, adopted) | **4** | **10–13** | **6–9** |
| `..._uthrow_cvcentered.root` (892 MB) | **4** | **10–13** | **6–9** |
| sweep universe `5d_xsec_*_uni_full_*.root` | **4** | **7** | **3** |

**Consequence for stage 1, and it is a blocker rather than a caveat.** R3 says *any unmatched key
fails closed*. A `k=0` anchor member built from today's tree therefore fails the bit-exact comparison
against the archive on **3 to 9 keys per artifact** — and it fails for the **right** reason under the
rule as written and the **wrong** reason in substance. The anchor would be correct and the gate would
red.

**This is not a tolerance question and must not be resolved by one.** The extra keys are individually
identifiable and their arrival is dated in git, so the correct instrument is an **explicit
archive-side key map** — the same instrument gate 4 already reserves for `seed` →
(`estimator_seed`, `draw_seed`). **What this enumeration establishes is that gate 4's map is not one
rename. It is a family, and it is enumerable.**

### 0a. The dated causes, so the map is derivable rather than negotiated

| extra key | writer | landed | why the archive lacks it |
|---|---|---|---|
| `fixed_seed_null_checked` | `unified_throw_cov.py` | 2026-08-11, null-as-absent closure | archive built before the flag existed |
| `estimator_seed`, `draw_seed` | `unified_throw_cov.py` | gate 1, this campaign | the two-role split did not exist |
| `est_seed_offset{,_declared}` | `unified_throw_cov.py`, `sweep_bank_5d.py` | lane D, 2026-08-18 | the member axis did not exist |
| `estimator_seed` | `sweep_bank_5d.py` | this campaign | the sweep seed was hardcoded `42` |
| `*_checked` ×3, `upstream_*` ×3, `centering_convention`, `uthrow_source`, `combined_source` | `adopt_unified_5d.py` | **`5856eeb1`**, BEN-106, 2026-08-11 | *"Before 2026-08-11 this file wrote only the two sqrt-traces above"* — the writer's own comment |

**`5856eeb1` is quotable against itself:** the commit that added the adoption stamps says in its own
comment that every adopted product before it carried none. The archive's 4-key adopted roots are
exactly that population.

**One derivation the map can make rather than assume.** `fixed_seed_null_checked` is absent from the
archive, but `fixed_seed_null_norm` **is present** — and the writer only emits the norm when the
check ran. So the archive's `checked` value is **derivable as 1**, not unknown. That is a real
inference from the writer's own conditional structure, and it is the shape every row of the map
should take: *derive from a dated writer property, or declare the key unmatched and fail.*

---

## 1. THE STAMP GAP IS THREE WRITERS, NOT ONE — AND IT IS WORST AT THE TERMINUS

The mediator reported *"neither ROOT file carries a seed stamp"* and proposed a fifth gate. **Its
archive measurement is right. The inference does not carry to a member**, and the correction runs in
both directions, which is why it needs stating rather than accepting.

Measured across every ROOT writer on a member's chain (`TParameter("int")` writes of the four
identity keys):

| writer | member product | seed/offset stamps |
|---|---|---|
| `sweep_bank_5d.py` | 169 vertical universes | **3** — `estimator_seed`, `est_seed_offset{,_declared}` |
| `unified_throw_cov.py` | `unified_throw_cov_5d.root` | **4** — all, both roles |
| `unfold_nd_omnifold_unbinned.py` | **19 lateral + CV** | **0** |
| `adopt_unified_5d.py` | **the two 892 MB adopted roots** | **0** |
| `analyze_universes_5d.py` | the 41.44 GB intermediate | **0** (pure `TH2D`; no scalars at all) |

**So remedy (A) is two-fifths done, and the missing three are the ones that matter most.**

- **`unfold_nd_omnifold_unbinned.py` is the sharpest.** This is the lateral+CV leg that gate 1
  item 7(a) added to coherence group **g1 at baseline 42**, and it is the only leg whose flag is
  natively `--seed` rather than `--estimator-seed`. It received the **seed plumbing** and none of the
  **provenance**. That is a pattern worth naming: *the leg that came in through a different door got
  wired and not stamped*, and it is the same leg that broke the driver's flag-name assumption and had
  no `LEG_BASELINES` entry. Three defects, one cause — it was added last and checked against
  assumptions written for the other six.
- **`adopt_unified_5d.py` is the most consequential.** The adopted roots are the **citable artifact**
  whose digests `MVFINAL_j` binds, and they carry no seed identity at all. A reader holding the
  published member cannot tell which member it is from the file. The stamps travel one hop and stop
  one hop short of the thing anybody quotes.
- **`analyze_universes_5d.py`'s intermediate** is the one place where "no stamp" is defensible on
  C's own retention ruling — it is deleted after `ADOPT_j` consumes it. But note the interaction:
  **an artifact that is both unstamped and deleted can never be audited after the fact**, so its
  correctness has to be established by its inputs and outputs, never by itself.

**Remedy (B) — never resume a ROOT product — I endorse and it is correctly ordered first, because it
needs no writer change.** But its scope should be read off the table above rather than from the
archive: it must cover **all five** writers today, and it may narrow to **three** once (A) lands, and
to **one** (the deleted intermediate) once adoption stamps too.

**One thing I will not do here.** Whether (A) is required for stage 1 or the ensemble receipt's
digest binding suffices is C's call and the mediator asked me not to pre-empt it. Nothing above
decides it; what it does is replace *"neither file is stamped"* with the actual per-writer map, which
is the input that decision needs.

---

## 2. THE CLASSIFICATION

Classes already ruled by C and **not re-litigated here** — recorded so this document is
self-contained, with the ruling attributed:

- **PAYLOAD WITH MANDATORY RECOMPUTATION** (BEN-077, as C treated `total_xsec`):
  `sqrt_tr_unified`, `sqrt_tr_block`, `sqrt_tr_old`, `sqrt_tr_new`, `joint_mean_shift_norm`,
  `fixed_seed_null_norm`, `globalCompleteness`.
- **CONFIGURATION** (equal, difference = hard failure): `n_throws`, `ndim`, **and `dataPOT`** — C
  corrected the mediator's PROVENANCE call, because it enters the arithmetic and a member normalised
  to a different POT would have **passed** as provenance.
- **C's heuristic, which I am adopting for every row I add below:** *a scalar that enters the
  arithmetic looks like a stamp because it is recorded once and never varies. Constancy is not
  circumstance. Ask what breaks if it changes, not how often it changes.*
- **PROVENANCE means "may differ from the archive". It does NOT mean "may be absent from the
  member."** The offset stamp is provenance for the comparison and **mandatory for admission** — two
  checks, one key.

### 2a. Full enumeration

**`uq_5d/unified_throw_cov_5d.root`** — writer `unified_throw_cov.py:520-560`

| key | type | class | note |
|---|---|---|---|
| `C_unified`, `C_blocksum`, `C_cross` | TH2D | PAYLOAD | bit-exact at `k=0` |
| `hJointMeanShift` | TH1D | PAYLOAD | |
| `sqrt_tr_unified`, `sqrt_tr_block` | double | PAYLOAD + **recompute** | derived from `C_unified`/`C_blocksum` in the same file — BEN-077 applies |
| `joint_mean_shift_norm` | double | PAYLOAD + **recompute** | `‖mean_shift‖`, and `hJointMeanShift` is its ingredient |
| `fixed_seed_null_norm` | double | PAYLOAD + **recompute** | present only when `--null` ran |
| `fixed_seed_null_checked` | int | **CONFIGURATION** | absent from archive; **derive 1** from the norm's presence (§0a) |
| `n_throws` | int | CONFIGURATION | `=160`, third corroboration of the throw population |
| `estimator_seed` | int | **PROVENANCE, mandatory** | `1000+k`; MUST differ for `k≠0` |
| `draw_seed` | int | **CONFIGURATION** | pinned `1000` for every member — see §3 |
| `est_seed_offset`, `est_seed_offset_declared` | int | **PROVENANCE, mandatory** | absent from archive by construction |

**The two 892 MB adopted roots** — writer `adopt_unified_5d.py:169-215`

| key | type | class | note |
|---|---|---|---|
| `hCov_combined5d_total_uthrow` | TH2D | PAYLOAD | |
| `hInflation_g` | TH1D | PAYLOAD | **already the winner mask** — see §4 |
| `sqrt_tr_old` | double | PAYLOAD + **recompute** | **the predeclared bar's operand**, `4.357790406860002e-38` |
| `sqrt_tr_new` | double | PAYLOAD + **recompute** | |
| `upstream_{fixed_seed_null_norm,joint_mean_shift_norm,n_throws}` | double/double/int | inherit upstream's class | **CONFIGURATION** for `n_throws`; PAYLOAD+recompute for the two norms |
| `{...}_checked` ×3 | int | **CONFIGURATION** | written unconditionally; absent from archive |
| `centering_convention` | TNamed | **CONFIGURATION** | `"cv-centered"` vs `"mean-centered"` distinguishes the two 892 MB files from each other; a swap here is silent |
| `uthrow_source`, `combined_source` | TNamed | **CONFIGURATION** | see §3 — these are why member-root-first matters |

**Sweep universe `5d_xsec_*_uni_full_*.root`** — writer `sweep_bank_5d.py:279-295`

| key | type | class | note |
|---|---|---|---|
| `hXSecND_flat` | TH1D | PAYLOAD | 65,856 bins |
| `globalCompleteness` | double | PAYLOAD + **recompute** | and see §5 |
| `dataPOT` | double | **CONFIGURATION** | C's correction |
| `ndim` | int | CONFIGURATION | `=5` |
| `estimator_seed` | int | **PROVENANCE, mandatory** | `42+k` |
| `est_seed_offset{,_declared}` | int | **PROVENANCE, mandatory** | |

**The 19 lateral + CV** — writer `unfold_nd_omnifold_unbinned.py:1012+`: `dataPOT`,
`globalCompleteness`, `ndim`, `hXSecND_flat`, per-axis `hXSec_*`, and a `hXSec2D` marginal. Classes as
above. **No identity key of any kind** (§1).

---

## 3. THREE ROWS WHERE THE CLASS IS NOT THE OBVIOUS ONE

**(a) `draw_seed` is CONFIGURATION, not provenance, and this is the row I would most want checked.**
It looks like a stamp — an integer recorded once, never varying. C's heuristic asks what breaks if it
changes: spec (B) requires the throw *realizations* to be **common across all 50 members** so the
scan varies the estimator and nothing else. A member that drew different throws is not a member of
this scan. So `draw_seed` must be **equal to 1000 in every member and in the archive**, and a
difference is a hard failure — which is precisely CONFIGURATION. Classifying it as provenance
because it happens to be a seed would let the one difference that invalidates the whole scan pass.
**The word "seed" in a key name predicts nothing about its class here; the two roles land in two
different classes.**

**(b) `uthrow_source` / `combined_source` are CONFIGURATION and they pass only because of the path
shape ruled yesterday.** They store `os.path.basename()` of the inputs. Under **member-root-first**
(`mii/member_k001200/uq_5d/...`) the basenames are **byte-identical to the archive's** — only
directories change — so an equality check is meaningful. Under a filename-suffix scheme
(`..._k001200.root`) every member would differ here, and the difference would be
**indistinguishable from a genuine wrong-input mismatch**, which is the failure this key exists to
catch. **A third independent argument for C's ruling, arrived at from the ROOT keys rather than from
globs or from the preflight.** I did not anticipate it and it is not in C's ruling.

**(c) `centering_convention` is the cheapest silent-swap detector in the set.** The two 892 MB
adopted roots differ in *exactly* this key and in their payload; `sqrt_tr_new` is
`5.807716496958672e-38` vs `6.236702327843976e-38`. Comparing the wrong pair across members yields a
plausible number, and equality on this key is what stops it.

---

## 4. `hInflation_g` — CONFIRMING THE MEDIATOR'S R4 READ, AND ONE CONSEQUENCE IT DID NOT DRAW

The mediator's reading of `adopt_unified_5d.py:108-113` is correct and I verified it independently at
`origin/main`: `g == 1` ⇒ `vb` won, `g > 1` ⇒ `vu` won and `vu = g²·vb`. **The mask is a shipped
product.** So R4 shrinks to shipping `vb` and `vu`, and no mask writer should be built.

**The consequence worth adding: `hInflation_g` is PAYLOAD, and it is a payload key whose comparison
is unusually informative.** Because `g` is a per-bin *max* selector, a member whose winner set moved
differs from the archive in `g` **structurally, not just numerically** — the set of bins where
`g == 1` changes. That makes `hInflation_g` a **cheap, early, whole-vector detector of a real
estimator-seed effect**, computable from an already-shipped key with no new writer. It is not a
substitute for `C_ML`, and I am not proposing it as the measurement; it is a free cross-check that
stage 0's distinctness question already wants.

**And I am taking the mediator's 230× sizing correction as binding on my own work:** the 5D flat
length is **65,856**, so a per-bin array is **0.527 MB**, not ~2 KB. Nothing in this document is
sized off the 285-bin extended-FPS grid, and §2a records 65,856 explicitly so the next reader cannot
inherit the wrong number from me.

---

## 5. ONE ROW WHERE THE ENUMERATION CHANGED MY OWN CODE

`globalCompleteness` is PAYLOAD+recompute per C. **Enumerating it caught that I had been skipping it
entirely.** `analyze_universes_5d.load_flat` passed `require_completeness=False`, justified as *"this
family does not always write globalCompleteness"* — and that claim is **false of the family**: both
writers emit it unconditionally, in the same straight-line block as `hXSecND_flat`
(`sweep_bank_5d.py:289`, `unfold_nd_omnifold_unbinned.py:1014`). Worse, the flag skips the
**presence/NaN** half too, and `NaN` is reachable with a known cause — `denom_nd.sum() <= 0` at
`sweep_bank_5d.py:265` and `unfold_nd_omnifold_unbinned.py:999`. A universe with a zero-integral
denominator was being folded into the 188-universe covariance silently.

Fixed at `aae49f2a`: presence and finiteness required, the FPS `0.50` floor deliberately **not**
inherited (that floor is not a measurement about this family, and the 188-universe distribution is
unmeasured — stated so the gap is falsifiable), and universes now checked against the CV's own bin
count. **The mediator asked for a real absent case or a tightening; the answer was that no absent
case exists, which is stronger than either branch it offered.**

---

## 6. WHAT THIS DOCUMENT DOES NOT ESTABLISH

- **I have not read a single ROOT file.** Every archive key count is the mediator's; every writer key
  set is mine. A reader who wants one party's account of both will not find it here.
- **The comparator does not exist** (B2). This is the *specification* it must implement.
- **No key is verified to be bit-reproducible at `k=0`.** That is stage 1's job, and §0 says why it
  cannot pass as currently specified.
- **Classes for `upstream_*` are inherited by argument, not measured.** I assert they take their
  referent's class; nobody has checked that adoption copies the value rather than recomputing it.
- **The lateral writer's full key list is from source, and its per-axis `hXSec_*` set is
  binning-dependent** — I did not enumerate those individually.

---

## 7. THE TABLE IS ALSO CODE, AND MAKING IT CODE CAUGHT TWO DEFECTS IN THIS DOCUMENT

`nd-unfolding/mii_root_payload_classes.py` carries every row above as data plus `classify()`,
`compare()` and `anchor_identity()`. `CLAUDE.md`'s rule is the reason: *a document costs tokens in
every future session forever; a check costs zero and cannot be skipped.* A classification table is
the most skippable kind of prose there is — long, tabular, easy to skim-agree with — and the most
consequential to get wrong, because B2's comparator either reads a machine-checkable table or
re-derives one from memory.

**Within seconds of being runnable it found two defects that §§1–6 above state confidently and
wrongly.**

**(a) `draw_seed` was CONFIGURATION with no enforceable comparison.** §3(a) argues at length that it
must be **equal** across archive and members. The argument is right. But `compare()` reported the
contradiction immediately: **the archive carries no `draw_seed` key, and no `seed` key either** — the
mediator's 9-key read has neither. *"Must equal the archive"* was **unenforceable against the
archive**, and my table asserted a check that could never run. The prose read fine; running it did
not.

The fix is **a third kind of map entry I had not anticipated**: not *derive from the archive's other
keys*, not *member-only provenance*, but **a declared constant external to both files**. The
archive's draw seed is `1000` because every g2 launcher pins the literal — sourced from
`seed_offset_policy.LEG_BASELINES` rather than retyped, so there is one place it can be wrong.

**(b) The comparator could not see a missing mandatory stamp — the exact invariant it enforces.**
`compare()` iterated `set(archive_keys) | set(member_keys)`, so a key absent from **both** never
entered the loop. **`est_seed_offset_declared` is never in the archive by construction**, so a member
that omitted its own offset stamp was **invisible**: verdict `INCOMPLETE`, which reads as *nearly
fine*. That is C's invariant broken by the check written to enforce it — *every layer that could
satisfy a member from pre-existing bytes must fail closed on an absent positive declaration; an
absent stamp is not a weak yes, it is a no.*

**The general form is worth more than the fix: the union of two files cannot express a requirement,
because a requirement is about what SHOULD be there.** The table is the iteration domain. Only
PROVENANCE keys are mandatory-present — `fixed_seed_null_norm` is legitimately absent when `--null`
did not run, which is what its `_checked` companion exists to make readable.

**Both were found by my own tests, and neither was findable by reading.** I wrote §3(a) and the
absent-stamp requirement in the same sitting and believed both.

### 7a. Three verdicts, not two

`compare()` returns **`PASS` / `INCOMPLETE` / `FAIL`**. A correct `k=0` anchor is **`INCOMPLETE`**:
no mismatch, and still not a pass, because **9 keys are derived from other keys in the same file and
nothing has recomputed them** (BEN-077). Folding that into `FAIL` invites a reader to treat a real
mismatch and an unfinished comparator as one state; folding it into `PASS` is worse, because the
pressure at stage 1 is toward green. `INCOMPLETE` names what is missing rather than how bad it is.

### 7b. And the measurement table re-derives itself

`STAMP_COVERAGE`'s five numbers are re-counted from the writers' source by
`test_the_stamp_coverage_table_MATCHES_THE_WRITERS`, because **a claim about code is dated unless
something re-reads the code** — and §1's whole argument is a claim about five files that lane D and
gate 1 are actively editing.

---

## 8. B2 EXISTS — AND WRITING IT FOUND THAT MOST "MANDATORY RECOMPUTATION" KEYS CANNOT BE RECOMPUTED

`nd-unfolding/mii_anchor_comparator.py`. It applies §2a's classes to two real ROOT files and adds the
half the table can only *demand*: recomputing every derived scalar from the ingredients in its own file.
The ROOT reader is **injected** (`read_keys` is a callable) because ROOT is absent here — every decision
is exercised against stubs and nothing about PyROOT's behaviour is claimed.

**C classified seven scalars as PAYLOAD WITH MANDATORY RECOMPUTATION. Four can be recomputed from the
file that carries them.** Derived from the writers, not assumed:

| key | ingredient | where |
|---|---|---|
| `sqrt_tr_unified` | `trace(C_unified)` | **in file** |
| `sqrt_tr_block` | `trace(C_blocksum)` | **in file** |
| `joint_mean_shift_norm` | `norm(hJointMeanShift)` | **in file** |
| `sqrt_tr_new` | `trace(hCov_combined5d_total_uthrow)` | **in file** |
| `upstream_*` (×2) | the throw root's scalars | cross-file |
| `fixed_seed_null_norm` | `norm(x_cv2 - base)` | **neither is written** |
| `globalCompleteness` | `of_in.sum()/denom_nd.sum()` | **neither is written**, and `sweep_bank_5d.py` writes **no** completeness histogram |
| **`sqrt_tr_old`** | `trace(hCov_combined5d_total)` | **the deleted intermediate — see below** |

### 8a. THE BAR'S OPERAND IS NOT RECOMPUTABLE FROM RETAINED BYTES

`sqrt_tr_old` is **the predeclared bar's operand** (`4.357790406860002e-38`). Its sole ingredient is
`hCov_combined5d_total`, read at `adopt_unified_5d.py:124-127` from `--combined`, whose value is set at
`sbatch_adopt_stamped_footing.sh:33` to
`uq_5d/universe_stage2_5d_bkgaware/uq_universe_5d_covariance_combined_bkgaware.root` — **the 41.44 GB
intermediate C ruled need not be retained.**

So after deletion the **scalar survives** in a retained 892 MB root and **its ingredient does not**, and
BEN-077's rule can never again be satisfied for it from retained bytes.

**C's argument was that "the bar's operands live downstream of it in the 892 MB adopted roots." That is
true of `sqrt_tr_new` and false of `sqrt_tr_old`** — the trace established that the operands are
downstream without distinguishing the two operands, and only one of them is. This is not an objection to
the retention ruling; it is one key the ruling did not separate.

**THE REMEDY IS 0.527 MB AND THE HELPER ALREADY EXISTS.** `trace(C) == sum(diag(C))`, so shipping
`diag(C_old)` as a TH1D makes the bar's operand recomputable from retained bytes forever.
`adopt_unified_5d.py:53`'s `_diag()` already reads a square TH2D's diagonal without materializing it,
and this composes with R4's `vb`/`vu` — **three per-bin arrays, 1.58 MB against a 4.46 GB retained
member.** I have **not** made that change: it alters a receipt-bound writer's output and the retention
ruling is C's. Flagged, costed, left.

*(`hCov_combined5d_total` has a third consumer, `p4_build_components.py:115`, so the intermediate's
deletion touches more than adoption.)*

### 8b. Two things the comparator does that the table cannot

- **A `sqrt`-trace is computed from the DIAGONAL, never the matrix.** One 65,856² float64 TH2D is
  34.7 GB. `read_keys_pyroot` extracts diagonals for exactly this reason.
- **`rtol` defaults to `0.0`.** This is the gate that decides whether the archive was reproduced; a
  silent `1e-9` would make *"reproduced"* mean something nobody chose. A tolerance is a decision.

### 8c. And the adopted root cannot reach the gate at all

`adopt_unified_5d.py` stamps **no** identity key, so a member's adopted root **fails `anchor_identity`
upstream of every payload and recomputation question**. The comparator shows the fifth gate is
**unreachable** today, not merely unverified. The table therefore has **no rows** for
`estimator_seed`/`est_seed_offset{,_declared}` on that artifact, and `classify()` refuses them — which
is correct, and will start demanding a decision the moment remedy (A) lands.

### 8d. And I committed BEN-482's defect inside B2 itself

The first version computed its verdict with `any("!=" in l or "ABSENT" in l for l in lines)` — greping
its **own diagnostics**. A verdict derived from its own prose can be changed by rewording a message, and
`"ABSENT"` matches both a mandatory key missing and the word in an unrelated sentence. Verdicts are now
decided by explicit flags. **Fourth instance today, this one inside the tool built to enforce rigour.**

---

## 9. C's RULING: `recomputable: yes | no` AS A REQUIRED ATTRIBUTE ON PAYLOAD — NO FOURTH CLASS

C's reason is structural and it corrected my framing: **each of the three classes names a COMPARISON
RULE** — bit-exact, equal, superset — and *"not recomputable"* is not one, **because those keys still
compare bit-exact.** What differs is whether the *ingredient check* is available. So it is an attribute,
not a class.

Four requirements, all implemented in `mii_anchor_comparator.py`:

1. **Declared here, never discovered at comparison time.** `assert_reasons_are_stated()` runs before any
   file is opened.
2. **A `no` requires a stated reason; a bare `no` is the fail-closed case.**
3. **The reason must distinguish a WRITER GAP from a MATHEMATICAL IMPOSSIBILITY.** Recording which kind
   it is *determines whether anyone can ever close it* — a bare *"not recomputable"* reads as a law of
   nature and freezes a writer gap forever.
4. **`--acknowledge-unrecomputable` takes an EXPLICIT KEY LIST that must equal the declared `no` set
   exactly.** A blanket flag lets a future `no` ride in silently: someone adds a key, declares it
   unrecomputable, and every existing invocation swallows it without anyone deciding. **This is the same
   defect as §7(b)** — a check whose domain is narrower than the requirement it enforces. Subset and
   superset are both rejected, and the error names which keys are missing or extra.

### 9a. All three of today's `no`s are WRITER GAPS, i.e. all three are closable

| key | kind | what would close it |
|---|---|---|
| `globalCompleteness` | WRITER_GAP | `of_in`/`denom_nd` unwritten, **and** `sweep_bank_5d.py` emits no completeness histogram (0 occurrences of `hCompleteness`, while `unfold_nd_omnifold_unbinned.py` has one). Writing either closes it. |
| `fixed_seed_null_norm` | WRITER_GAP | `x_cv2` and `base` are ordinary per-bin vectors `unified_throw_cov.py` does not write. |
| `sqrt_tr_old` | WRITER_GAP | C's **11g**: ship `diag(C_old)` before any member intermediate is released. The mediator found it is **already in memory** at `adopt_unified_5d.py:128` (`diag_comb`), so the remedy is a **write**, not a computation, and not even an extra read of the 41 GB file. |

**`sqrt_tr_old` stays `no` until that write lands**, because the declared set describes the tree as it
is, not as it is about to be.

### 9b. C's 11g, and the general defect it names

*Nothing accepted without a stamp, nothing deleted without one, **and nothing deleted before the
survivors' ingredients are retained elsewhere**.*

C's generalisation, which it rates above the fix: **a retention policy must be tested against every
derived quantity that SURVIVES the deletion, not against the ones the deletion is for.** The question
asked was *"are the bar's operands downstream of the intermediate?"*; the question never asked was *"are
the SURVIVING SCALARS' ingredients downstream too?"* Only the second is about deletion.

Two scope constraints that bind any implementation: **11g releases MEMBER intermediates only — the
archive's 41.44 GB file is frozen and no ruling may delete an archive product**, so
`p4_build_components.py:114` is unaffected and *"delete the 41 GB file"* must never be implemented as
reaching the archive. And **a release must enumerate every reader, not only those on the member DAG** —
the third consumer's harmlessness was luck; the rule is completeness.

Costing, confirmed both ways: `diag_comb + vb + vu` = 3 × 65,856 doubles = **1.58 MB**, 0.035 % of a
retained member, a **26,219 : 1** trade against 41.44 GB.

### 9c. And the line C asked for, beside the key

**39 of 188 archive universes have `globalCompleteness` ABOVE UNITY, max 1.0241.** A *"completeness"*
exceeding 1 means **it is not a completeness fraction** — so the guard is **floor-only, with no
ceiling**. Anyone reading the name will assume `[0,1]` and may add a ceiling that **rejects 39 good
universes**. C's framing, better than mine: **a hygiene floor and a quality gate have opposite
calibrations** — hygiene catches corruption and wants a wide margin; quality judges physics and wants a
tight one. Floor `0.90`: spread `0.0521`, so `0.95` sits `0.42` spread-widths below the minimum and
`0.90` sits `1.38`.
