# FINDING 2026-08-13 — A "reference implementation" was never dated against the paper it is taken to implement

**`BEN-217`.** Lane A block (`210-219`). Measured, live. Physics consequences:
`ADVISORY-20260813-eavail-published-conventions.md` §3–§4; affected item `OI-56`.

## The setup

`OI-56` is frozen at rerun scale (**+212.18 MeV/event**, **4.837% of events change truth bin**,
**−10.99% out of bin 1**) on the strength of a comparison to what the row calls **"MINERvA's own
reference implementation"** — `GENIEXSecExtract/src/XSec.cxx`, `case kEAvail:`. Our
`GetEAvailableTrue()` disagrees with it on four species, and `CVUniverse.h:163` cites
**arXiv:2312.16631 Eq. 4** as the authority for our version.

**That file WAS opened and read correctly.** Lane `dc` extracted its species list accurately; the table
in the advisory matches the code I fetched line for line. **Its history was not read**, and the row is
about what that concealed.

## Measured: the reference post-dates the paper by four months

| event | UTC |
|---|---|
| **Ascencio v1 submitted** (arXiv:2110.13372) | **2021-10-26T03:01:17Z** |
| `case kEAvail:` first exists at all | 2021-11-26T10:14:03Z — **a month later**, and **four species only** |
| kaons / strange baryons / antibaryons added | **2022-03-07T22:15:44Z** |
| neutron skip + `max(0.0, ·)` clamp added | 2022-03-08T15:51:41Z |
| **Ascencio v2 submitted** | **2022-07-25T11:46:21Z** |

**So `kEAvail` cannot have produced Ascencio v1's numbers — it did not exist — and the species list
`OI-56` measures us against is four months younger than that submission.** Whether v2 was regenerated
against it is not knowable from outside, and nothing here claims it was.

## And the species extension is a νe artifact by an author of the paper we cite

`2f0097bde564`, the commit that added the strange-baryon (`pdg>=2000` → `E − m_p`), antibaryon
(`pdg<-2000` → `E + m_p`) and kaon/eta (`else` → total `E`) branches, is titled:

> **"adding NuE low recoil"**

Its other file is `apps/runCCIncForNuEMEC.cpp` (+342/−0). The author, **Hang Su**, is an author of
**arXiv:2312.16631** — the e-ν / e-ν̄ low-recoil paper that our own `CVUniverse.h:163` names as the
authority for `GetEAvailableTrue()`.

**The chain closes on itself.** Our cited authority and the "independent reference implementation" we are
being measured against are the same νe analysis, one person, one week in March 2022. That is not a
convention two parties arrived at; it is one realization, and `OI-56` reads it as the former.

**It also explains a verdict that is otherwise puzzling.** `kEAvail` skips `abs(pdg)==11 || abs(pdg)==13`
— *"do nothing. don't count charged lepton"* — added in the same three-commit window. **In a νe analysis
the primary electron IS the charged lepton and must be excluded.** Rodrigues 2016, a νμ analysis,
explicitly *includes* electron total energy. So our e± exclusion follows the νe-era code and not the νμ
paper, which inverts the advisory's *"on e± we are RIGHT and minerva-ml is wrong."* (Temporal association
measured; motive inferred — stated at that strength in the advisory §5.)

## How solid the "reference" is, measured rather than assumed

As committed at `2f0097bde564`, the four pre-existing species tests were left as bare `if`s while the new
block was an `if/else if/…/else` chain. So for a photon: the first `if` adds total `E`, then the chain's
`else` fires and **adds it again**. Same for π±, π⁰ and protons — **every already-handled species was
double-counted.** It also did not compile (`3238bc435c83`, *"forgot ;"*, +12 min). Fixed 1 h 31 m later by
`30a4edf2b65a` *"Corrected EAvail"*, then again the next day by `23ff7c0ac438` *"EAvail fix again"*.

**Recorded not as a jab but because `OI-56` treats this code as a stable reference convention.** It was
under active, error-prone construction in March 2022, and its species list has never been reviewed by
anyone but its author.

## The mechanism, and why `BEN-172` does not cover it

`BEN-172` is *cite-without-opening*, caught by "read your source." **Here the source was opened, read
accurately, and quoted correctly.** What was missing is that a code artifact has a *dimension a paper does
not*: it has a history, and any claim of the form *"this implements published convention P"* is a claim
about a **relationship between two dated objects**.

A file read at `HEAD` presents itself as timeless. There is nothing in `case kEAvail:` that says "the
strange-baryon branch is four months younger than the paper you think this implements, and was written for
a different beam." **The information exists, is one command away, and the artifact gives you no reason to
ask for it** — which is why this fails for readers who are doing everything else right.

It also has a distinctive consequence: **a reference implementation can post-date, and disagree with, the
paper it is taken to implement.** Both happened here, and the disagreement (Rodrigues 2016's closed list
vs Ascencio 2022's open one, §4 of the advisory) was invisible until the dates were laid out.

## The check

- **When treating code as the authoritative realization of a published convention, `git log --follow` the
  FUNCTION and put its dates beside the paper's submission dates.** If the code is younger, it is a
  *later* realization and cannot be evidence about what the paper meant.
- **Read the commit MESSAGES of the branches you are relying on**, not only the code. *"adding NuE low
  recoil"* is the whole finding, and it is free.
- **Check whether the paper's own authors wrote the code.** Here they did, which makes the artifact
  *authoritative* about the νe paper and *not independent* of it — the opposite of how it was being used.
- **Get the arXiv version dates.** `https://arxiv.org/abs/<id>` lists every `v1, v2, …` with timestamps;
  Ascencio's `v1` 2021-10-26 vs `v2` 2022-07-25 is what makes the March-2022 code window legible at all.
- **A published convention may not be one convention.** Two papers in one lineage disagreed here. Read
  every paper you are comparing against, not the most recent one.

## Related

`BEN-215` — same pass, same repo, the commit-as-string failure that sent me into the history in the first
place. `BEN-206` — the interesting result outrunning the boring check; the dates were the boring check.
