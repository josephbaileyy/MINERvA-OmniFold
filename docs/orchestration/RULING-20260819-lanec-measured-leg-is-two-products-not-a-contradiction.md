# RULING — the "measured-leg self-contradiction" is **NOT a contradiction**: the note describes **TWO REAL, LIVE, DELIBERATELY DIFFERENT C_stat PRODUCTS** and names neither. **No passage is false. Site C is RIGHT — and my own first reading of it was wrong.**

**By:** lane C (PET), on the mediator's dispatch, 2026-08-19, at `b8f74fbe`. **Settled from the CODE, which
is where the estimator lives — lane D is right that the documents cannot resolve it, and that is a true
statement about the search space, not about the question.**

| | | |
|---|---|---|
| **Is one of the two arguments unsound?** | **NO. The dispatch's premise does not hold.** Both are sound *in their own scope*. | **RULED.** |
| **`app_statmethods:143-160` (Site A)** | **Describes a TWO-stream contract — which is neither full-event product.** Correct for the recoil-only/2D demonstrator. | **MEASURED.** |
| **`:861-864` (Site B)** | **SOUND.** Its rebuttal inherits Site A's scope, where MC *is* drawn. | **RULED.** |
| **`:1472-1481` (Site C, `app:cstatlimit`)** | **CORRECT.** It accurately describes `data-only-v1`. | **MEASURED.** |
| **The actual defect** | **No site names its PRODUCT**, so Site B's "both data and MC" is carried into Site C's full-event covariance, where it is false by design. | **RULED.** |
| **Remedy** | **LABELLING, not correction.** No number changes and no argument is withdrawn. | **RULED.** |

> **THE ONE-LINE FORM:** *there are two committed C_stat products — `three-stream-v1` and `data-only-v1` — and
> `data-only-v1` resamples the data stream ALONE **on purpose**, so that the published `σ_stat` is not ~88% MC
> statistics and is profileable against MINERvA's own, T2K, MicroBooNE and NOvA. The note is not
> self-contradictory; it is **product-ambiguous**, which is a documentation defect with a physics
> consequence.*

---

## 0. ⚠ I FIRST CONCLUDED THE OPPOSITE, AND THE CHECK THAT REVERSED IT IS THE POINT

I read `coherent_bootstrap_factors` (`fullevent_fps_dataloader.py:614-625`), found it draws **three** Poisson
streams over data / signal-MC / background-MC, and was about to rule that **Site C was the false passage** —
that "bootstrap of the measured leg" misdescribed a construction which demonstrably resamples MC too.

**That would have been wrong, and wrong in this campaign's signature shape:** I would have measured one
function and asserted it of a product that does not use it. The check that caught it was asking whether the
full-event family has *one* construction or more. **It has two, both named, both live** — so a function
belonging to one is not evidence about the other. **Recorded rather than tidied away, because the wrong
answer was one command from being committed as a ruling.**

---

## 1. THE MEASUREMENT — TWO PRODUCTS, BOTH COMMITTED, NEITHER SUPERSEDED

`nd-unfolding/pet/cstat_data_only.py:51-53`:

```
CSTAT_THREE_STREAM = "three-stream-v1"
CSTAT_DATA_ONLY    = "data-only-v1"
CSTAT_PRODUCTS     = (CSTAT_THREE_STREAM, CSTAT_DATA_ONLY)
```

And the module's own header (`:33-36`) states the *purpose* of the split, which is the physics content of this
ruling:

> *"`data-only-v1` builds the COMPARABLE statistical covariance: **the data stream alone is resampled**, so
> the published `sigma_stat` is **not ~88% MC statistics** and is profileable against MINERvA's own, T2K,
> MicroBooNE and NOvA. **The three-stream family is NOT superseded, NOT discarded and NOT re-verdicted**
> (lane C, `BEN-404`)."*

**So "measured leg alone" is not a lapse in the note — it is the defining property of a named product**, and
the reason it exists is precisely that a covariance dominated by MC statistics is not comparable to other
experiments' `σ_stat`. **Both products are live simultaneously and by decision.**

The three-stream construction, for contrast — `fullevent_fps_dataloader.py:614-625`:

```
data_factor = rng(seed).poisson(1.0, n_data)
sig_factor  = mc_poisson_factor(n_sig, seed)        # rng(seed + 10_000_000)
bkg_factor  = rng(seed + 20_000_000).poisson(1.0, n_bkg)
```

— *"Three GLOBAL Poisson(1) factors over the full data / signal-MC / background-MC inventories."*

---

## 2. THE STREAM COUNT SETTLES WHICH SITE DESCRIBES WHICH, WITHOUT NEEDING ANY PASSAGE TO SAY SO

**This is the argument lane D lacked, and it is arithmetic rather than interpretation.** The three
constructions in play have **different numbers of Poisson streams**:

| Construction | Streams | Seeding |
|---|---|---|
| recoil-only / 2D replica contract | **2** | data `rng(k)` + MC `rng(k + 10^7)` |
| `three-stream-v1` (full-event) | **3** | `rng(k)`, `rng(k + 10^7)`, `rng(k + 2·10^7)` |
| `data-only-v1` (full-event) | **1** | data only |

**Site A (`:151-158`) describes exactly TWO streams** — *"two independent sub-RNGs (a data RNG seeded from
$k$, and an MC RNG seeded from $k + 10^{7}$)"*. **Two is not three and not one, so Site A CANNOT be
describing either full-event product.** It is the recoil-only/2D contract, and the `+10^7` offset confirms it:
`coherent_bootstrap_factors`' own docstring says the signal stream *"reuses the canonical
`pet_bootstrap.mc_poisson_factor` (`rng(seed+10_000_000)`) **so the full-event contract is bit-consistent with
the recoil-only replica contract**"* — the shared offset is deliberate lineage, not identity.

**Lane D's hypothesis is therefore CONFIRMED from the code side:** the two-stream passages are the
demonstrator's material and `app:cstatlimit` is full-event. D was right that nothing at any of the three
sites says so; the resolution came from counting streams in the loader, not from the prose.

**Site C (`:1472-1481`) matches `data-only-v1` on every stated particular:** *"full-event"*, *"50-member
replica family"*, *"background-subtracted target construction"*, *"an independent Poisson(1) bootstrap of the
measured leg"*, *"a member's target is the nominal target multiplied by that draw"*. **One stream, measured
leg, 50 members, full-event. It is correct.** It even flags itself as a method choice and says so explicitly.

---

## 3. RULED — SITE B IS SOUND, AND WOULD BE UNSOUND ONLY IF MOVED

Site B (`:861-864`) rebuts a missing-MC-statistical-term objection with *"our bootstrap already draws
independent Poisson(1) multipliers on **both** data and MC per replica"*, **citing `\S\ref{sec:bootstrap}`** —
i.e. Site A. **It inherits Site A's scope by its own citation**, and within that scope the claim is true and
the rebuttal is valid: the comparison it is making is against the published binned D'Agostini result, which
is the demonstrator's comparison.

**RULED: no argument in the note becomes unsound, and the dispatch's premise — that resolving this must
invalidate one of the two — does not hold.** It rested on the assumption that the three passages describe one
construction. They describe two, and each is true of its own.

**BUT THE EXPOSURE IS REAL AND IT IS THE ONE THAT MATTERS.** Site B's sentence is a general-sounding claim
about *"our bootstrap"* sitting ~600 lines before a section titled *"The full-event statistical covariance:
what it is, and what it is not"*. **A reader who carries "both data and MC" forward into `app:cstatlimit`
concludes that the published full-event `σ_stat` includes MC statistics. It does not, by design.** That is not
a documentation nicety: it is the difference between a covariance that is profileable against other
experiments and one that is ~88% MC statistics, which is the stated reason the product exists.

**So the defect is a scope leak, not a factual error** — and it is the more dangerous kind, because every
sentence survives being checked individually.

---

## 4. RULED — THE REMEDY IS LABELLING, AND WHAT IT MUST SATISFY

**No number changes. No argument is withdrawn. No result is retracted.** I am not authorised to edit the tex
and I have not; the mediator states the edit routes separately, and this ruling is its input.

**Conditions the edit must satisfy, in priority order:**
1. **Every one of the three sites must name its product** — `three-stream-v1`, `data-only-v1`, or the
   recoil-only/2D demonstrator contract. **A passage about "our bootstrap" with no product named is the
   defect itself**, and fixing only Site C would leave Site B free to leak forward again.
2. **`app:cstatlimit` must state that MC statistics are EXCLUDED BY DESIGN, with the reason** (comparability;
   not ~88% MC statistics; profileable against MINERvA's own, T2K, MicroBooNE, NOvA). **Stating the exclusion
   without the reason invites a reader to file it as an omission** — which is exactly the objection Site B was
   written to rebut, arriving in the other direction.
3. **Site B must be scoped in place**, not deleted. Its rebuttal is sound and the objection it answers is
   real; it needs the words *"for the recoil-only comparison"* (or the correct product name), not a strike.
4. **Site A must say which contract it specifies**, and — if it is intended to cover the full-event pipeline
   at all — its **two**-stream description is incomplete for `three-stream-v1`, which has a third
   background-MC stream at `rng(k + 2·10^7)`. **I have not determined Site A's intended scope**, only that
   two streams matches neither full-event product.

**And one thing the edit must NOT do: it must not present `data-only-v1` as a correction OF, or a replacement
FOR, `three-stream-v1`.** The code says in terms that the three-stream family is *"NOT superseded, NOT
discarded and NOT re-verdicted"*. **They are two products with different objects, and the note should read
that way.**

---

## 5. WHAT THIS RULING DOES NOT DO

- **It authorises no tex edit and no push.** It is note-build scope, and the mediator is right that the
  paper receipt does not cover it. **It is a ruling, not a receipt.**
- **It does not determine which product the note's HEADLINE `σ_stat` is built from.** §2 places
  `app:cstatlimit` on `data-only-v1`; whether every downstream number in the note traces to that product is a
  separate audit I did not run, and **anyone acting on point 2 above should establish it rather than assume
  §2 settles it.** `app:cstatlimit` is one section.
- **It does not touch `OI-121`/`OI-122`**, the Gate-6 prohibitions, or any pin, receipt, watch or Slurm job.
- **It does not re-verdict either product**, and per `BEN-404` it must not be read as doing so.

## 6. WHY THIS RECURS, AND THE CHEAP GUARD

**Two live products with one noun.** The note says *"our bootstrap"* and *"the statistical covariance"* as if
each were unique; the code has had two named products with an explicit `CSTAT_PRODUCTS` tuple. **Prose has no
type system, so a distinction the code makes by dispatching on a tag is carried in prose by adjacency and
memory — and adjacency does not survive a 600-line separation.**

The guard is cheap and is the same shape as §9 of my `448fe5ec` ruling: **before writing "our X" about a
quantity the code names, grep for the plural.**

```
grep -n 'CSTAT_PRODUCTS' nd-unfolding/pet/cstat_data_only.py    # a tuple => more than one product
```

*Filed by lane C. §1's constants and §2's stream counts are read from the tree at `b8f74fbe`; §0 records a
conclusion I reversed before committing it. I edited no tex and no control-plane source.*
