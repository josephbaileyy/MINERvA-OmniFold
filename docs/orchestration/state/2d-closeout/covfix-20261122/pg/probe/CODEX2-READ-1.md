# PG probe: codex-school2 read 1 (NO-GO) and the rev 2 dispositions

cov2d ran codex-school2's read of the rev 1 probe (`b062a78c`: pg-probe.py `866c5ea0…`, launcher `87da6d0e…`). The
reader saw the probe directory, declaration §4, FD-F1-REPORT.md, gen5d_v3.py and FD-F1-DECLARATION.md:60–100.
The report is `~/cov2d-work/reads-for-director/codex2-tgprobe-b062a78c-r1-REPORT.md`, sha256
`19a8792a8e8923e075f2d0b5b438b243a98bd5c10881082e7c961a14f752a2c3`, and it has 8 blocking items. They are restated
below by the PG session, not quoted, and each one's disposition is the PG session's. Rev 2 rewrites `pg-probe.py` and
replaces `pg-probe-launch.sh` with `pg-probe-launch.py`.

**GENIE facts used.** These are from GENIE-MC/Generator at tag `R-3_04_00`, read through a web fetch on 2026-11-24.
- `XmlParserUtils` `GetXMLFilePath` takes the first match on `GetXMLPathList(add_tune = true)`. The list is the
  `--xml-path` option, `$GXMLPATH`, `$GXMLPATHS`, `$GALGCONF`, then the tune directory and the CMC directory, then
  `$GENIE/config`. There is no merge.
- `TuneId`: `CMCDirectory` is base/`<CMC>`, and `TuneDirectory` is that plus `/<tune>`.
- `AlgConfigPool` `LoadGlobalParamLists` reads `ModelConfiguration.xml` with root `global_param_list` and returns
  only the param_set named by `GUSERPHYSOPT`, or `Default`. `LoadRegistries` trims values.
- An `alg` value splits on `/` into class and config, and any other count is fatal.
- The tag's CMC files give these classes:

| tune | QEL-CC | MEC-CC |
|---|---|---|
| G18_10a | `NievesQELCCPXSec/Dipole` | `NievesSimoVacasMECPXSec2016` |
| AR23_20i | `NievesQELCCPXSec/ZExp` | `SuSAv2MECPXSec` |
| G21_11b | `HybridXSecAlgorithm/SuSAv2-QEL` | `SuSAv2MECPXSec` |
| G18_02b and G18_02a | `LwlynSmithQELCCPXSec/Dipole` | `EmpiricalMECPXSec2015` |

- No tune directory of these five tunes holds a `ModelConfiguration.xml`.
- `HybridXSecAlgorithm.xml`'s set `SuSAv2-QEL` has `DefaultXSecAlg` `SuSAv2QELPXSec/Default`, plus free-nucleon
  `XSecAlg@Interaction` entries using `LwlynSmithQELCCPXSec/Dipole`.
- The CVMFS build can differ from the tag. The probe reads CVMFS, and the tag sets the spent-tune control's
  expectation.

**A correction this turned up.** FD-F1-REPORT.md §1.3's "`NievesSimoVacasMECPXSec`" came from F1's probe12, a
`grep -o "Nieves[A-Za-z]*"`, which stops at a digit. The class is `NievesSimoVacasMECPXSec2016`. Rev 1's spent-class
control expected the grep token, so on the real files it would have stopped. Rev 2 expects the tag's class.
`test_f1_report_names_are_grep_prefixes_of_the_classes` checks that the report's token is that class's alphabetic
prefix. The report itself is F1's record, and the PG session has not edited it.

| # | finding, restated | rev 2 |
|---|---|---|
| 1 | the regex parser can give a false GO: a blank value counted as novel, a character reference hid a spent class, malformed XML and inactive sets supplied values, and every XML file in a tune directory counted as an override | **Fixed.** Parsing is structural (ElementTree). A DOCTYPE or ENTITY declaration is refused. Character references decode, so a disguised spent class is caught. GENIE's file selection is the first `ModelConfiguration.xml` of tune dir, CMC dir, `config/`; other files are never overrides. The root must be `global_param_list` and the set exactly one `Default`. The probe STOPs on a duplicate name, an empty value, a non-`alg` type or a value not of the form `genie::<Class>[/<config>]`. The genie UPS table must not mention `GXMLPATH`, `GXMLPATHS`, `GALGCONF` or `GUSERPHYSOPT`. `HybridXSecAlgorithm` is resolved one level through `master_config.xml`, and every effective value records its file, set and raw text. Tests: the `Config` class |
| 2 | 02b "absent" can come from a failed lookup; a wrong-tune or empty spline can count as complete | **Fixed.** absent means the listing and the UPS table were both read and neither declares the qualifier. present needs both, plus `GENIE_XSEC_TUNE` = the tune in the table, a non-empty spline whose own `<genie_tune name>` is the tune, and one README version line naming the qualifier. Anything else is unresolved, and an unresolved 02b is a STOP with no fallback. Tests: the `Catalog` class |
| 3 | the receipt misstates eligibility (02a "qualifies" after 02b's exclusion; 02a recorded as chosen after a mismatch STOP); overlap compared by slot | **Fixed.** `novelty` (intrinsic, by class and by component) is kept separate from `eligibility` (per slot, after every rule). 02a is "not considered" when 02b is present, and is chosen only when eligible after the premise check. Overlap is against the pooled spent classes and components. A class-versus-component disagreement is a STOP for the director |
| 4 | the read boundary is unenforced: links can escape, and non-regular files can be opened | **Fixed.** Every read resolves beneath the two approved CVMFS product roots and opens with `O_NOFOLLOW \| O_NONBLOCK`. It must `fstat` as a regular file. Listings must be directories. Tests: the `Boundary` class (links out of the roots, a directory, a FIFO) |
| 5 | the launcher does not verify the node or the environment | **Fixed.** The probe's first step is an identity check: hostname `login<NN>`, `/pscratch`, `/global/common` and the CVMFS tree. Nothing is read if it fails. ssh runs with `-F /dev/null` and explicit options: the NERSC key and certificate, `StrictHostKeyChecking=yes` against `~/.ssh/known_hosts`, no agent, X11 or port forwarding, no control socket, no local command. That matters because the user's config has `ForwardAgent yes` for `*.nersc.gov`. The remote command is `env -i PATH=/usr/bin:/bin LC_ALL=C /usr/bin/python3.11 -I -S -B -`, and gpg is called only by approved absolute paths |
| 6 | the hashed bytes and the sent bytes can differ; the output check is racy and follows links; writes are unchecked; GO is not tied to a valid result | **Fixed.** One read is hashed and sent. The output is reserved with `O_CREAT\|O_EXCL\|O_NOFOLLOW`, and every write is checked and fsynced. A receipt is valid only with exactly one result line, last, as JSON, whose verdict matches the rc. Otherwise the launcher exits 4 and keeps the file as the failure receipt. Tests: the `Launcher` class |
| 7 | GPG confinement is unproven: the temp parent is implicit, ~/.gnupg is walked, and agents are matched over the whole UID | **Fixed.** The parent is an explicit `/tmp`, which must be node-local by `/proc/mounts`. HOME and GNUPGHOME are both the fresh mode-700 directory, in a minimal environment. `gpgconf --list-dirs` must put homedir and agent socket inside it, or the socket in gpg's per-homedir `/run/user/<uid>/gnupg/d.*`, which is then removed. The probe's own agent is identified by `gpg-connect-agent --no-autostart 'getinfo pid'` and must be gone after `gpgconf --kill` exits 0. Nothing else is read or swept. ~/.gnupg is no longer read at all, since HOME is the throwaway dir |
| 8 | the negative controls accept crashes, and a midpoint flip may fail before the integrity check | **Fixed.** The ciphertext must be SKESK + SEIPD v1, with partial body lengths followed, as gpg 2.4 writes them. The tamper flips the SEIPD body's last byte, which is inside the encrypted MDC. Tamper must exit 2 with "encrypted message has been manipulated", and a wrong passphrase must exit 2 with "Bad session key". A signal (negative rc) or missing evidence fails. The real local gpg 2.4.8 passes, and fakes that crash, refuse without evidence, or emit a non-SEIPD packet each fail |
| non-blocking 1 | add the counterexamples; say what stays unverified on Perlmutter | done (tests above; `LINE-TRACE.md` "Limits") |
| non-blocking 2 | the stdin frame belongs to the bound binary; the docs disagreed on the temp location | the probe tests only the fd-3 handoff, now stated. `/tmp` is stated everywhere |

**Open for the director.** gpg puts the agent socket under `/run/user/<uid>/gnupg/d.*` whenever `/run/user/<uid>`
exists and the homedir is not the default. No option or environment variable avoids it. Rev 2 accepts that
directory only in its exact per-homedir form, and requires it removed after the kill. If sockets must be strictly
inside the throwaway directory, the probe would STOP on such a node.
