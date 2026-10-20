# MP3-B attempt 1: NuWro on a free proton STOPPED at generation

**By** the measurement session, 2026-10-19/20, under the frozen MP3-B specification (PLAN.md §4.3;
BINDING-PHASE1-20261019 §2, D6). Code: `measurement-paper/phase1/mp3b/`; staging: [`PREP.md`](PREP.md).

**CITABLE FOR:** the failure mode, where it occurred, the rough abort rates, and the charge.
**NOT CITABLE FOR:** any NuWro-on-CH number, any gate verdict, anything about A7, or any claim.

## 1. What ran

- **Staging at GO.** Staged blobs matched the worktree by `git hash-object`; `gen/` and `out/` were absent; every
  input sha256 in `gen/input_sha256.txt` equals PREP.md.
- **Binary and cards.** CVMFS NuWro v21_09_1 e20-debug, the production build, for both samples. Declared seeds
  63001 / 64001, N 250,000 / 25,000, and the `proton.txt` target lines.
- **Outcome.**
  - H main (0.5–50 GeV) aborted with rc 134 (SIGABRT) after 1:47 wall. H supp (50–100 GeV) aborted with rc 134 after
    0:19 wall. Both printed `E=1.19e+03 mass=1.19e+03` (MeV) and then failed
    `src/particle.h:227: void particle::set_energy(double): Assertion 'E>=_mass'`.
  - The C1 parity re-conversion of the frozen C12 files completed (rc 0/0). Its bitwise comparison happens in the build
    step, which never ran.
  - The job stopped at its own guard (`STOP: generation or conversion failed`, exit 5). Build and eval never ran.

## 2. Where it failed

- **Both runs completed their 50k test events.** The channel plan:

  | sample | RES | DIS | ν–e |
  |---|---:|---:|---:|
  | H main | 97,037 | 152,872 | 91 |
  | H supp | 1,007 | 23,916 | 77 |

  QEL, COH and MEC were 0, as in the phase-0 probe.
- **Both aborted while generating DIS (dyn 4) events.** H main stopped at 27.6% of its DIS events (about 42k of 153k);
  H supp at 25.0% (about 6k of 24k). The partial files agree: H main part 1 holds 98,146 entries (the finished RES set)
  and part 2 holds 25,480; H supp part 1 holds 1,063 and its part 2 is unreadable.
- **The particle is a Σ hyperon** (1.19 GeV: Σ⁺ 1.1894 or Σ⁰ 1.1926).
- **Candidate code sites.**
  - The only `set_energy` calls on hyperons are in the cascade, at entry (`kaskada7.cc:151-152`, `E + his_fermi`) and
    exit (`:302-304`, `E - his_fermi`).
  - The cascade runs whenever `kaskada_on = 1` (`nuwro.cc:513`), including on the free target; the production card
    leaves it on.
  - Which site fired, and why only on hydrogen, is **not established**. C12 production made 1.27M CC DIS events, and its
    supplement 96k, without this abort.
- **Rate.** About one abort per 42k DIS events at 0.5–50 GeV (≈ 2.4e-5) and one per 6k at 50–100 GeV (≈ 1.7e-4). Each
  rests on a single event.

## 3. Gates

| gate | status |
|---|---|
| C0, C1, B1, B2, B3, B4 | NOT EVALUATED: the job stops before the build when generation fails |
| readout and replay | not computed; A7 unchanged and not re-examined |

## 4. Jobs and charge

| job | QOS | State | ExitCode | ElapsedRaw | AllocTRES | CPU node-h |
|---|---|---|---|---:|---|---:|
| 60017813 | shared (-c 8) | CANCELLED (held by the coordinator; scancel 2026-10-19T20:53:32 PDT) | 0:0 | 0 | never started | 0 |
| 60022605 | debug (full node) | FAILED | 5:0 | 275 | billing=256,cpu=256,energy=78188,mem=487802M,node=1 | 0.076389 |

- **Why debug.** 60017813 sat PENDING (Resources) for about 5 h while shared_milan drained ahead of
  maintenance_20261021. The coordinator held it and resubmitted the identical staged script (sha256 `a699b9b5…`) with
  `sbatch -q debug -t 00:30:00`.
- **Writes.** Only under `/pscratch/sd/j/josephrb/measurement-paper/phase1/mp3b/`, about 0.14 GB, all partial files
  and parity flats. Nothing on CFS.

## 5. The director's ruling (message, 2026-10-20)

- **(A) approved:** chunked generation with declared seeds, under three conditions.
  1. An aborted chunk is discarded whole and rerun with up to two declared alternates, else dropped, with N_total
     reduced.
  2. Per-chunk abort and DIS counts, and the excluded fraction stated as an approximation, flagged if above ≈ 1e-4.
  3. Gates C0–B4 unchanged; the frozen Σ w r / N_total over completed chunks.
- **(C) approved** as a variant labelled "mixed: NuWro carbon + GENIE hydrogen; not NuWro-on-CH".
- **(B), a NuWro patch, not approved.**
- A cascade-off card for H (`kaskada_on = 0`) was raised with the director afterwards and is not run unless ruled.

## 6. UNCONFIRMED

- Which `set_energy` call fires, and why only for a single-nucleon target.
- The abort rates, which rest on two events.
- The soundness of the partial `.part` files, which are not used.
