#!/usr/bin/env python3
"""Carry apply_fixes.py's substitutions into the fact ledgers (combined and per piece), plus the probe flips."""
import sys, pathlib, importlib.util, re
S = pathlib.Path(sys.argv[1])  # step2 dir
spec = importlib.util.spec_from_file_location('af', S / 'agy/apply_fixes.py')
src = (S / 'agy/apply_fixes.py').read_text()
FIX = eval(src[src.index('FIX = [') + 6: src.index('\n]\n') + 2])
EXTRA = [
 ('For this injection the configuration-(a) estimator recovers the feature.', 'For this injection the configuration-(a) estimator neither removes the injected feature nor creates a spurious one.'),
 ('The recovery is shown for configuration~(a) only', 'That result is shown for configuration~(a) only'),
 ('"we do not claim it matches the published definition" removed as commentary', '"We therefore do not claim that our definition matches the published definition" kept (restored after the agy triage)'),
 ('`X:sec_3d.tex::We therefore do not claim`', '`N:sec_3d.tex::We therefore do not claim that our definition matches`'),
 ('`X:sec_summary.tex::\\pageref`', '`N:sec_summary.tex::\\pageref{sec:execsummary}`'),
 ('(g-04, s-05: page reference removed)', '(g-04, s-05; page references kept, restored after the agy triage)'),
 ('(g-04: page reference removed) | SU8 | REWORDED | page reference dropped', '(g-04; page reference kept, restored after the agy triage) | SU8 | REWORDED | page reference kept'),
 ('`X:app_response_mismatch.tex::absorbed silently`', '`N:app_response_mismatch.tex::absorbed silently`'),
]
for p in [S / 'ledger.md'] + sorted(S.glob('ledger-B*.md')):
    t = p.read_text(); t0 = t
    for o, n in [(o, n) for _, o, n in FIX] + EXTRA:
        t = t.replace(o, n)
    if t != t0: p.write_text(t); print('updated', p.name)
