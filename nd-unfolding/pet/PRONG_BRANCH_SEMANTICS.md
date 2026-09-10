# MasterAnaDev prong branch semantics and PET implications

## Source and evidence scope

Recorded 2026-09-10 from Carlos Pernas's reply in the email thread
"MINERvA Open Data Product Documentation Request: MasterAnaDev prong_part_*
branch semantics", supplied by Joseph Bailey for preservation and PET planning.
The reply describes an inspection of reconstruction software, including
`Particle.h`. Its own sent timestamp and original mail file were not supplied;
2026-09-10 is the recording date, not an asserted email date. Addresses,
signatures, and the earlier correspondence are omitted. This is a curated
semantic record, not a byte-identical email archive or independently obtained
producer source. Quoted passages below are verbatim excerpts; tables and
implications are summaries.

This is attributed reconstruction-side documentation. It is distinct from the
[fixed-sample measurements](../../docs/orchestration/PACKET-20260901-pet-typed-descriptor-semantic-evidence.md)
and their independent artifact review. Agreement between those measurements
and this explanation is not a new independent measurement. The supplied
definitions resolve the earlier interpretation conflict at the correspondence
level; exact release applicability and implementation verification remain open.

## Definitions stated in the reply

### Reconstruction PID enumeration

> These codes are actually NOT the same as the MC PDG codes you may be familiar with, so Rik was actually mistaken when he mentioned that 13 is a muon.

| Raw code | Reconstruction hypothesis |
|---|---|
| 0 | Unknown |
| 1 | Photon |
| 2 | Electron |
| 3 | Muon |
| 4 | Tau |
| 5 | Pion |
| 6 | PiZero |
| 7 | Kaon |
| 8 | Proton |
| 9 | Neutron |
| 10 | HeavyBaryon |
| 11 | CharmMeson |
| 12 | StrangeMeson |
| 13 | EMLikeShower |
| 14 | HadronLikeShower |
| 15 | Higgs |
| 16 | Other |
| -999 | Unfilled |

Enumeration membership is not evidence that a code is emitted in the released
tuples. Carlos writes:

> I believe, in the current tuples, the only values you should see are -999, 0, 3, 8, and 13.

Treat that expected support as tentative, not as a release-wide invariant or a
reason to discard an unexpected code. In particular, code 9 has an enumeration
meaning but its emission is not established. `Unknown` is explicitly set;
Carlos has not fully established why a candidate is left unfilled instead.
Pion reconstruction can be stored in dedicated pion branches without being
copied into these general containers. These codes are not truth labels and the
prong set is not a complete identified-particle census.

### Field definitions

| Branch | Definition stated by Carlos | Important qualification |
|---|---|---|
| `prong_part_pos` | Candidate start-point `(x, y, z, t)` in `(mm, mm, mm, ns)` | Time is relative to the beginning of a 10 microsecond beam gate; the stated 10,000 ns upper bound has not been checked across our sources. |
| `prong_part_E` | Candidate four-momentum `(px, py, pz, E)` in `(MeV/c, MeV/c, MeV/c, MeV)` | Candidate-hypothesis kinematics, not a truth four-vector. |
| `prong_part_score` | Tool-dependent score of the best-hypothesis particle | No common calibration across particle types is supplied. |
| `prong_part_mass` | Assumed hypothesis mass, reported in MeV | A hypothesis assignment, not an independent mass measurement. |
| `prong_part_charge` | Candidate charge-sign code | Useful for muon candidates; non-muon zero fills do not establish neutral charge. |
| `prong_dEdXMean` | Total prong energy divided by prong length, in MeV/mm | Carlos recommends more specific branch groups where available; this scalar is not the proton dE/dx profile fit. |
| `prong_nParticles` | Number of candidate hypotheses associated with a prong | Not physical particle multiplicity; values can exceed five. |

| PID | Score | Mass | Charge |
|---|---|---|---|
| -999 | -1, unfilled | -1, undefined | -999, unfilled |
| 0 | 0, fixed | -1, undefined | 0, uninformative fill |
| 3 | 1, fixed | 105.658 MeV | 0 undetermined; 1 positive; 2 negative |
| 8 | 0 to 1, proton dE/dx-profile fit | 938.272 MeV | 0, uninformative fill |
| 13 | 0 to 1, EM-like shower classifier | -1, undefined | 0, uninformative fill |

The EM score uses a k-nearest-neighbors classifier with endpoint energy
fraction, median transverse width, and mean dE/dx. Carlos points to Jeremy
Wolcott's thesis, chapter 6 around page 111, for details. That pointer is not
verification of the precise classifier/configuration used for these tuples.
An EM-like shower can originate from a photon or electron; mass -1 does not
identify it as massless. The dedicated `MasterAnaDev_proton_*` branches have a
score threshold whose value and algorithm Carlos has not confirmed.

### Ordering and hypothesis selection

> Note that for every event, the prongs are arranged such that the first prong (prong_part_*[0]) is the primary lepton prong, either a muon or an electron. Then any other reconstructed particles will come after, in no particular order as far as I'm aware.

The primary-lepton role is stated explicitly; the absence of a further ordering
rule is qualified. It must be checked for the exact tuple sources before
becoming a production invariant.

> As for how exactly each prong picks its best particle, this was pretty difficult to confirm exactly... but I believe it simply picks the particle with the highest score as the best.

Highest-score selection is a hypothesis, not a confirmed algorithm. Carlos's
suggestion that a muon hypothesis would therefore win is also tentative. Do not
implement that rule or infer cross-tool score comparability from it. Obtain the
selection and tuple-filling functions, including priorities, ties and defaults.

### Tuple and software provenance

> The current tuples in the public area are P7, although we have recently produced a P8 with some minor changes and additional information that we plan to replace them with once they're fully validated.

This describes the public area at the time of the reply. It does not bind our
downloaded data and MC files to P7, identify a reconstruction configuration, or
establish that P8 is now released. Carlos explains that public GitHub code is
downstream analysis code, while tuple-producing reconstruction is not public.
He offers to investigate sharing specific source files with spokesperson
permission; no such files accompany the reply. An analysis-code commit is not
a substitute for tuple-production provenance.

## Consequences for the current implementation

The code observations below refer to repository base
`d147880fc7e4a4078e5b2d5e51aa4334d0e1736f`.

- [The contract](typed_descriptors.py) stores raw PID categories without physical
  labels. The downstream mapping conflict did not become a `13 = muon` rule in
  this implementation. A bijective category relabeling alone does not add or
  remove model information.
- Its raw charge vocabulary is `(-1, 0, 1)`, so code 2 uses the generic
  unknown-code channel. The next contract should preserve raw codes `0, 1, 2`
  and distinguish muon charge applicability from non-muon fills. A signed
  physical-charge representation would require an explicit conversion.
- The default sentinels mask -999 and -9999. Mass -1 and score -1 currently
  remain valid continuous inputs. Undefined mass and unfilled score need
  field-specific masks. Valid unknown PID 0, score 0, and undetermined muon
  charge 0 must not all be erased by a blanket zero rule.
- Prong units can now be documented from this source. The source mapper already
  splits the vectors in the stated component order. Unit definitions do not
  settle detector calibration, training normalization, or photon/blob semantics.
- Score use must be conditioned on hypothesis/tool type. Hypothesis mass is
  largely redundant with PID; neither should be described as an independent
  calibrated particle measurement.
- [The mapper](typed_descriptor_source_smoke.py) retains all `n_prongs` rows.
  The pooled descriptor has no primary-prong role field. Explicitly decide how
  prong zero relates to the existing event-level muon before production use.
  This reply does not choose between raw-row retention and filtered membership.
- `prong_nParticles` is not currently loaded. Adding it would be a new feature
  proposal, not a repair required to interpret existing columns.

These are contract and interpretation issues in an untrained adapter, not
evidence of a new defect in the completed scalar central-value campaigns.

## Future PET studies and follow-up questions

Prefer dedicated muon information; investigate dedicated proton and pion
branches when those candidates matter. Generic prongs are useful for EM-like
showers and potentially proton candidates within their documented limitations.
Before combining prong, photon and blob families, establish their associations
and overlap. Neither this reply nor the presence of separate branch groups
proves that their energy deposits are disjoint.

Questions to resolve with the reconstruction owner:

1. Can the `Particle.h` enumeration and best-particle selection/tuple-filling
   functions be published or shared with a version identifier? What are the
   tool priorities, tie rules, and unfilled-versus-unknown conditions?
2. Which exact data and MC files/releases do these definitions cover? What
   changed from P7 to P8, and how can a downloaded file be assigned its version?
3. How do generic prongs associate with dedicated muon/proton/pion candidates
   and photon/blob collections? What proton threshold governs the dedicated
   branches, and how does it relate to generic proton candidates?

Preserve source identities and checksums before any P8 migration. A migration
requires its own validation; do not silently mix versions. Added features
should subsequently be evaluated through matched controls and family ablations,
including sensitivity to detector modeling and missingness. Better semantics
alone do not establish improved unfolding or uncertainty coverage.

## Next step and publication boundary

The next bounded implementation task and its acceptance criteria are in
[TYPED_DESCRIPTOR_STATUS.md](TYPED_DESCRIPTOR_STATUS.md#next-bounded-task).
This record supplies documentation and planning, not a new scientific run.

PET remains diagnostic/method-development under
[OI-126](../../docs/OPEN_ITEMS.md). Its existing `C_stat` construction remains
unverified and is not paired with P5A; no PET total covariance is adopted.
The correspondence provides no estimator-equivalence or coverage evidence.
It changes neither the scalar-5D covariance adoption task nor completed scalar
central values. It does not authorize ROOT access, training, Gate-6 work,
`C_ML` construction, or a publication claim. Read the exact Gate-6 restrictions
in [the governing receipt](../../docs/orchestration/state/gate6-member-trajectories-result-56847059.json)
before any separately authorized Gate-6 action.
