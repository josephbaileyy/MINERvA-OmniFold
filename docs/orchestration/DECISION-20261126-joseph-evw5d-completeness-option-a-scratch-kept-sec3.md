# DECISION 2026-11-26 — Joseph: EVW5D completeness reading (a), the scratch products kept, and the Sec. 3 sentence

**Recorded by** the director. It adds to `DECISION-20261125c-joseph-zenodo-weights-purity-out-deletions.md` (#1346).
Joseph gave every item below directly to the director, in the director's session, on 2026-11-25 (Pacific), late
evening. Quoted words are Joseph's.

## 1. EVW5D's C-COMPLETE finding: option (a)

EVW5D attempt 2 (`fd/evw5d-20261125/EVW5D-BINDING-2.md`, receipts in #1353) found the stored per-fine-cell
completeness c ≠ 1 beyond 1e-5 in 32 of 65,856 fine cells. These are 16 adjacent pairs, each off by at most 4.1e-4
and equal and opposite. That is consistent with 16 events binned across an edge, because the signal histogram is
filled from float32-cast truth and the denominator from float64 truth. Setting c = 1 moves the sixteen published cell
integrals by at most 3.3e-6. The weights and the published result are unchanged.

The director put two options to Joseph: (a) state that the denominator is the saved rows themselves (eavail step 0b's
multiset equality), so c = 1 by construction, and disclose the 16 edge events; or (b) build an event-level
denominator sidecar. Joseph: "I like (a)". He asked whether the finding needs to be kept in mind for later work. The
director's answer: it is negligible for physics, but it is a property of the float32 inputs that any future work
binning the stored inputs at fine-cell level will meet again, so it is recorded here and in EVW5D's FOLLOWUPS. (b)
stays on the later-work list.

The App. D wording that follows from (a) is Joseph's. JE drafts it. The draft says readers may rebin freely within
the fiducial box, since the flux is one integrated value, and that v1 releases central values only.

## 2. EVW5D's scratch products are kept

Joseph, on `/pscratch/sd/j/josephrb/evw5d-20261125-r2`: "keep for now." The products also exist on HPSS
(`/home/j/josephrb/mnv-evw5d-20261125-r2/evw5d-20261125-r2.tar`) and in the deposit copy on Joseph's Mac.

## 3. The Sec. 3 sentence from the readability rewrite

The rewrite (#1348) changed the sentence after Joseph's approved "differ by 0.005 GeV/c" sentence to: "The
central-value comparisons below use an unfolding on MINERvA's exact edges. The OmniFold uncertainties are available
only on our analysis grid, which we use for comparisons that include them." Joseph: "sounds good."

## 4. The GENIE 2.12.10 question goes to rewrite-helper

The rewrite asked why GENIE 2.12.10 was chosen for the standalone Valencia comparison. Joseph: "I'm not sure, can you
ask rewrite helper to look into it?" The director assigned it to rewrite-helper, from the records only.

**CITABLE FOR:** what Joseph decided, and when. **NOT CITABLE FOR:** any number beyond those quoted from the cited
records, or any note wording beyond the quoted sentence.
