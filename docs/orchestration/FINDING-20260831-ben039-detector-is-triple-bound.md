# FINDING 2026-08-31 — the BEN-039 detector is bound on THREE axes, so the class it names is
# instrumented in principle and unreachable in practice; folded into `OI-179`, not filed as a new class

**CITABLE FOR:** the measured behaviour of `audit_gates_that_cannot_fail.py` and its
`tautological-datum` detector; the three binding constraints in §2 and the positive control that makes
those nulls meaningful; the acceptance criterion in §4; and the reasoning for folding rather than
filing. **NOT CITABLE FOR:** any gate movement; closure of `OI-179`; authorization to write a
detector, edit the audit tool, or edit any test; `OI-177`; leg 6; the M(ii) family; or adoption.
**Gate 2 remains FAIL.** No compute is authorized or affected by this document.

## 0. The filing decision, and why it is NOT a new row

Joseph, 2026-08-31: *"its your choice whetehr to take a new OI block or fold it into OI-179."*
**Folded into `OI-179`.** Three reasons, in order of weight:

1. **`OI-179`'s remaining open content already IS this.** The row is held open by defect 3 alone — no
   launcher, gate or instrument emits environment provenance. §3 below shows the `mkdir` half of this
   finding is *unreachable by any source-line detector*, so its only possible instrument is a
   recorded-and-compared environment. **That is defect 3.** A separate row would carry the same next
   action as an open one.
2. **The class does not need naming again.** It was named on 2026-08-07 as **BEN-039** and
   instrumented as `d_tautological_datum`, whose own report text is *"it cannot disagree with that
   input, so it is not evidence."* Filing "unfalsifiable guards" would be a third statement of a
   class already stated twice — a rule retyped as a second implementation, committed against the very
   instrument that owns the rule.
3. **Both alternatives cost the same ceremony and buy nothing.** A new `OI-*` ten-block and a new
   `BEN-*` ten-block each require, per `FINDINGS.md`, *"a fetched-remote freeness check and a closed
   ten-block claimed with its first filing"*. This identity's `120-139 / 170-179` block is exhausted,
   so either route opens a block for one row that belongs to an existing one.

## 1. The instrument exists and is healthy — this is not a missing-tool finding

`docs/orchestration/audit_gates_that_cannot_fail.py`, `--power-only`: **rc 0**, and all seven
detectors FIRE on reconstructions of their real pre-fix source — `unreachable-trigger`,
`absolute-floor-in-tolerance`, `scale-blind-epsilon`, `size-only-completeness`, `nonemptiness-gate`,
`strong-name-weak-body`, `tautological-datum`. *"power test PASSED for all detectors."* The suite is
self-proving and its design argument is correct.

`--severity ALL`: **rc 0**, and a case-insensitive grep of the whole report for
`ambient|pathcheck|SYSTEM_PREFIXES|test_k0_launcher` returns **0**. It is blind to `OI-179` defect 2.

## 2. WHY it is blind — three binding constraints, and a positive control

```python
_TAUT_NAME = re.compile(
    r"^\s*(\w*(?:achieved|measured|class_ratio|_ratio|realized)\w*)\s*=\s*"
    r"(?:\w+)\.get\(|^\s*\w+\[[\"'](\w*(?:achieved|measured|class_ratio)\w*)[\"']\]\s*=\s*\w+\[")
```

Measured by importing the module and calling `d_tautological_datum` on single-line probes. **The
control FIRES, which is what makes the nulls evidence rather than absence:**

| probe | result |
|---|---|
| `MNV_ENV_SYSTEM_PREFIXES = self._ambient_prefixes()` | **SILENT** |
| `env["MNV_ENV_SYSTEM_PREFIXES"] = env["PATH"]` | **SILENT** |
| `measured_prefixes = self._ambient_prefixes()` | **SILENT** |
| `class_ratio = target_meta.get("step1_class_ratio")` | **FIRES** ← positive control |

**Three independent bindings, and naming only one licenses a fix that repairs only one:**

- **SPAN.** It matches one line, so a tautology crossing fixture → subprocess → guard cannot fit.
  Defect 2's does: `good_env()` at `:269` sets the allowlist from `_ambient_prefixes()` at
  `:231-245`, which reads `os.environ`; the value then travels through a subprocess environment into
  the guard that checks it.
- **LEFT-HAND VOCABULARY.** The assigned name must contain `achieved`, `measured`, `class_ratio`,
  `_ratio` or `realized` — the vocabulary of the single instance the detector was built from.
- **RIGHT-HAND SHAPE.** The value must come from `<name>.get(` or one dict index assigned from
  another. **This is the constraint that has been missed in discussion, and row 3 of the table is the
  proof:** supplying BEN-039's own vocabulary is *still* not enough, because
  `self._ambient_prefixes()` is a method call, not `.get(`.

So the detector generalises over neither syntax nor naming. It recognises **one dialect of one
instance**.

## 3. The `mkdir` half is unreachable by ANY source-line detector, and that is a decision not a concession

`OI-179` defect 1's cause was that `/etc/profile:171` adds `$HOME/bin` to `PATH` conditionally on the
directory existing, and `~/bin` was created 2026-08-26 01:40:39 PDT — three days after the packet
that documented the allowlist. **There is no source to scan.** The recipe's correctness depended on
unversioned filesystem state. No regex, no dataflow analysis and no AST pass can observe it.

**Therefore defect 3 stops being audit hygiene and becomes the only mechanism that can detect this
class at all.** It is now load-bearing for two distinct failures, not one.

## 4. THE ACCEPTANCE CRITERION for any detector written later

The tool's own docstring supplies it: *"Every real instance above is now FIXED, so a sweep of the
current tree cannot demonstrate the detectors work."* So:

> **Any new detector MUST be added to `POWER` and MUST FIRE on a synthetic reconstruction of
> pre-`b512760d` `nd-unfolding/tests/test_k0_launcher_two_roots.py`** — `good_env()` at `:269` taking
> `_ambient_prefixes()` at `:231-245`.

**A detector shipped without a power arm would itself be a gate that cannot fail, inside the
instrument built to find gates that cannot fail.** That is the one outcome this document exists to
prevent.

**And the generalisation must be STRUCTURAL, not lexical**, or the next instance arrives in a fourth
dialect and is invisible again: *a value that flows out of the system under test and into the
expectation it is compared against.* Names are evidence for that shape, never its definition. In
practice: a test-side symbol assigned from `os.environ`, from a subprocess of the system under test,
from a file the system under test wrote, or from a re-invocation of the same function — and then used
to build an expected value, an allowlist, a tolerance or a reference.

## 5. Provenance of the reasoning, since it was not one lane's

The span constraint and the change of recommendation away from a new class row are this lane's. The
**vocabulary** constraint was identified by the personal-account producer session (`5d`), which also
supplied the structural generalisation in §4 and the argument that naming only the span would license
a span-only fix. The **right-hand-shape** constraint and the positive control in §2 are this lane's,
and they correct `5d`'s statement that collapsing defect 2 onto one line fails *because of*
vocabulary: it fails on vocabulary **and** on call shape independently, which row 3 of the table
isolates. A sweep for further instances is in flight on a separate account and is not superseded by
this document.

**Nothing here is authorization.** No detector is written, no test is edited, no audit tool is
changed, and `OI-179` is not closed.
