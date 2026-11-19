#!/usr/bin/env python3
"""Apply the structural skeleton of the compression outline (DECISION-20261119c) to the note's source tree.

usage: skeleton_compression.py [--check] [--manifest OUT.tsv]   (run in docs/analysis-note)

The skeleton only moves and re-levels. Every block moves byte for byte to its new file, every \\label stays, and the
only edits to the moved text are heading commands, which go down one level where an old section becomes part of a
new top-level part. The new part files hold a part heading and \\input lines, and nothing else. Each move is printed
as a move-manifest row (sha256 of the block's bytes), so a reviewer can re-derive every move from the base tree.

Placement (COMPRESSION-OUTLINE.md; the director's rulings of 2026-11-19):
  Part 1  Introduction                        sec_intro, sec_execsummary
  Part 2  Data, simulation and method         sec:eavailw-definitions (first), sec_experiment, sec_method, with
                                              tab:config-key placed after tab:estimators-matrix
  Part 3  Reproducing the MINERvA measurement sec_results, sec:tension (App. A), sec_systematics, sec_validation
  Part 4  Extending to five observables       sec_3d, sec_eavailw, sec_fived16, then the comparison with generators:
                                              sec:fived16-gen (with sec:fived16-gen-target), sec_joint
  Part 5  What the validation shows           sec_5d, sec:fived16-fd, -prr, -ibu, sec:3d-closure, sec:3d-classifier,
                                              App. A's sec:closure, App. B's five-dimensional pseudo-experiments
  Part 6  Results and their validity          tab:what-is-measured (from sec_front), sec_limitations, sec_summary
  App. A  app_statmethods, then app_statmethods_nd one level down
  App. B  app_negweight
  App. C  Further studies: app_response_mismatch, sec_fps
  App. D  Release package and code: app_release, app_codebase, then the definitions (tab:definitions, from sec_front)
  App. E  app_devhistory, then sec:cov1b-gate (App. A), app_landscape and app_pet_pointer, parked for their records move
  App. F  app_verification
"""
from __future__ import annotations

import argparse
import hashlib
import re
import sys
from pathlib import Path

HEAD = re.compile(r'^(\s*)\\(section|subsection|subsubsection)(\*?)(?=[\[{])')
LEVEL = {'section': 1, 'subsection': 2, 'subsubsection': 3}
NAME = {v: k for k, v in LEVEL.items()}
NAME[4] = 'paragraph'


def level_of(line: str) -> int | None:
    m = HEAD.match(line)
    return LEVEL[m.group(2)] if m else None


def demote(text: str, by: int = 1) -> tuple[str, int]:
    """Lower every heading command at a line start by `by` levels (comment lines untouched); starred headings keep
    their star and their \\addcontentsline level follows."""
    out, n = [], 0
    for line in text.split('\n'):
        m = HEAD.match(line)
        if m:
            new = NAME[LEVEL[m.group(2)] + by]
            line = f'{m.group(1)}\\{new}{m.group(3)}' + line[m.end():]
            n += 1
        am = re.match(r'^(\\addcontentsline\{toc\}\{)(section|subsection)(\})', line)
        if am:
            line = am.group(1) + NAME[LEVEL[am.group(2)] + by] + am.group(3) + line[am.end():]
            n += 1
        out.append(line)
    return '\n'.join(out), n


class Tree:
    def __init__(self, root: Path):
        self.root = root
        self.text: dict[str, str] = {}
        self.moves: list[tuple[str, str, str, str]] = []   # (id, from, to, sha256)

    def get(self, f: str) -> str:
        if f not in self.text:
            self.text[f] = (self.root / f).read_text(encoding='utf-8')
        return self.text[f]

    def put(self, f: str, s: str):
        self.text[f] = s

    def cut(self, f: str, start: int, end: int, what: str) -> str:
        """Remove lines [start, end) (0-based) of f and return them, ending in a newline."""
        lines = self.get(f).split('\n')
        block = '\n'.join(lines[start:end]) + '\n'
        self.put(f, '\n'.join(lines[:start] + lines[end:]))
        return block

    def section_block(self, f: str, label: str) -> tuple[int, int]:
        """The heading that carries \\label{label}, to the next heading of the same or a higher level."""
        lines = self.get(f).split('\n')
        li = [i for i, l in enumerate(lines) if f'\\label{{{label}}}' in l and not l.lstrip().startswith('%')]
        assert len(li) == 1, (f, label, li)
        h = li[0]
        while level_of(lines[h]) is None:
            h -= 1
            assert h >= 0, (f, label)
        lev = level_of(lines[h])
        e = h + 1
        while e < len(lines) and not (level_of(lines[e]) is not None and level_of(lines[e]) <= lev):
            e += 1
        return h, e

    def env_block(self, f: str, label: str, env: str = 'table') -> tuple[int, int]:
        lines = self.get(f).split('\n')
        li = [i for i, l in enumerate(lines) if f'\\label{{{label}}}' in l]
        assert len(li) == 1, (f, label)
        s = li[0]
        while not lines[s].lstrip().startswith(f'\\begin{{{env}}}'):
            s -= 1
        e = li[0]
        while not lines[e].lstrip().startswith(f'\\end{{{env}}}'):
            e += 1
        return s, e + 1

    def move(self, mid: str, f: str, span: tuple[int, int], dest: str, what: str) -> str:
        nlines = len(self.get(f).rstrip('\n').split('\n'))
        block = self.cut(f, span[0], span[1], what)
        sha = hashlib.sha256(block.encode('utf-8')).hexdigest()
        self.moves.append((mid, f'{f}:{span[0] + 1}-{min(span[1], nlines)} ({what})', dest, sha))
        return block


def part(title: str, label: str, inputs: list[str], comment: str, body: str = '') -> str:
    s = f'% {comment}\n\\section{{{title}}}\n\\label{{{label}}}\n\n'
    if body:
        s += body + '\n'
    s += ''.join(f'\\input{{{i}}}\n' for i in inputs)
    return s


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--manifest', type=Path)
    a = ap.parse_args(argv)
    T = Tree(Path('.'))
    new: dict[str, str] = {}

    # ---- blocks that leave their file (taken bottom-up within each file, so earlier spans stay valid)
    gt = T.move('SK-01', 'sec_fived16.tex', T.section_block('sec_fived16.tex', 'sec:fived16-gen-target'),
                'sec_fived16_gen.tex', 'sec:fived16-gen-target')
    gen = T.move('SK-02', 'sec_fived16.tex', T.section_block('sec_fived16.tex', 'sec:fived16-gen'),
                 'sec_fived16_gen.tex', 'sec:fived16-gen')
    ibu = T.move('SK-03', 'sec_fived16.tex', T.section_block('sec_fived16.tex', 'sec:fived16-ibu'),
                 'sec_q3_fived16.tex', 'sec:fived16-ibu')
    prr = T.move('SK-04', 'sec_fived16.tex', T.section_block('sec_fived16.tex', 'sec:fived16-prr'),
                 'sec_q3_fived16.tex', 'sec:fived16-prr')
    fd = T.move('SK-05', 'sec_fived16.tex', T.section_block('sec_fived16.tex', 'sec:fived16-fd'),
                'sec_q3_fived16.tex', 'sec:fived16-fd')
    cls = T.move('SK-06', 'sec_3d.tex', T.section_block('sec_3d.tex', 'sec:3d-classifier'),
                 'sec_q3_3d.tex', 'sec:3d-classifier')
    clo = T.move('SK-07', 'sec_3d.tex', T.section_block('sec_3d.tex', 'sec:3d-closure'),
                 'sec_q3_3d.tex', 'sec:3d-closure')
    defs5 = T.move('SK-08', 'sec_eavailw.tex', T.section_block('sec_eavailw.tex', 'sec:eavailw-definitions'),
                   'sec_observables.tex', 'sec:eavailw-definitions')
    closure = T.move('SK-09', 'app_statmethods.tex', T.section_block('app_statmethods.tex', 'sec:closure'),
                     'sec_q3_closure.tex', 'sec:closure')
    tension = T.move('SK-10', 'app_statmethods.tex', T.section_block('app_statmethods.tex', 'sec:tension'),
                     'sec_tension.tex', 'sec:tension')
    gate = T.move('SK-11', 'app_statmethods_nd.tex', T.section_block('app_statmethods_nd.tex', 'sec:cov1b-gate'),
                  'app_cov1b_gate.tex', 'sec:cov1b-gate')
    nw5 = T.move('SK-12', 'app_negweight.tex', T.section_block('app_negweight.tex', 'sec:val-negweight-5d')
                 if '\\label{sec:val-negweight-5d}' in T.get('app_negweight.tex') else _last_subsection(T, 'app_negweight.tex'),
                 'sec_q3_negweight.tex', 'App. B five-dimensional pseudo-experiments')
    # sec_front: the config key, then the definitions section (to its end), then the box with its sources
    ck = T.move('SK-13', 'sec_front.tex', T.env_block('sec_front.tex', 'tab:config-key'), 'sec_method.tex',
                'tab:config-key')
    defs = T.move('SK-14', 'sec_front.tex', T.section_block('sec_front.tex', 'sec:front-definitions'),
                  'app_terminology.tex', 'sec:front-definitions with tab:definitions')
    fr = T.get('sec_front.tex').split('\n')
    b0 = [i for i, l in enumerate(fr) if l.startswith('Table~\\ref{tab:what-is-measured} lists')]
    assert len(b0) == 1
    b1 = len(fr)
    while fr[b1 - 1].strip() == '':
        b1 -= 1
    box = T.move('SK-15', 'sec_front.tex', (b0[0], b1), 'sec_validity_table.tex', 'tab:what-is-measured, its lead '
                 'sentence and its sources comment')

    # ---- the config key goes after tab:estimators-matrix, in sec_method
    sm = T.get('sec_method.tex').split('\n')
    s, e = T.env_block('sec_method.tex', 'tab:estimators-matrix')
    T.put('sec_method.tex', '\n'.join(sm[:e] + ['', ck.rstrip('\n')] + sm[e:]))

    # ---- re-levelled pieces
    new['sec_fived16_gen.tex'] = gen + demote(gt)[0]          # gen-target one level below the comparison
    new['sec_q3_fived16.tex'] = fd + prr + ibu
    new['sec_q3_3d.tex'] = clo + cls
    new['sec_observables.tex'] = defs5
    new['sec_q3_closure.tex'] = closure
    new['sec_tension.tex'] = tension
    new['app_cov1b_gate.tex'] = gate
    new['sec_q3_negweight.tex'] = nw5
    new['app_terminology.tex'] = demote(defs)[0]
    new['sec_validity_table.tex'] = box

    for f in ('sec_intro.tex', 'sec_execsummary.tex', 'sec_experiment.tex', 'sec_method.tex', 'sec_results.tex',
              'sec_systematics.tex', 'sec_validation.tex', 'sec_3d.tex', 'sec_eavailw.tex', 'sec_fived16.tex',
              'sec_joint.tex', 'sec_5d.tex', 'sec_limitations.tex', 'sec_summary.tex', 'app_statmethods_nd.tex',
              'app_response_mismatch.tex', 'sec_fps.tex', 'app_release.tex', 'app_codebase.tex',
              'app_landscape.tex', 'app_pet_pointer.tex'):
        T.put(f, demote(T.get(f))[0])

    C = 'Compression skeleton (DECISION-20261119c): this part\'s heading and its inputs only; the lanes write its opening.'
    new['part1_intro.tex'] = part('Introduction', 'sec:part-intro', ['sec_intro', 'sec_execsummary'], C)
    new['part2_method.tex'] = part('Data, simulation and method', 'sec:part-method',
                                   ['sec_observables', 'sec_experiment', 'sec_method'], C)
    new['part3_reproduction.tex'] = part('Reproducing the MINERvA measurement', 'sec:part-q1',
                                         ['sec_results', 'sec_tension', 'sec_systematics', 'sec_validation'], C)
    new['part4_fivedim.tex'] = part('Extending to five observables', 'sec:part-q2',
                                    ['sec_3d', 'sec_eavailw', 'sec_fived16', 'sec_fived16_gen', 'sec_joint'], C)
    new['part5_validation.tex'] = part('What the validation shows', 'sec:part-q3',
                                       ['sec_5d', 'sec_q3_fived16', 'sec_q3_3d', 'sec_q3_closure', 'sec_q3_negweight'], C)
    new['part6_validity.tex'] = part('Results and their validity; outlook', 'sec:part-validity',
                                     ['sec_validity_table', 'sec_limitations', 'sec_summary'], C)
    new['appC_further.tex'] = part('Further studies', 'app:further', ['app_response_mismatch', 'sec_fps'], C)
    new['appD_release.tex'] = part('Release package and code', 'app:release-code',
                                   ['app_release', 'app_codebase', 'app_terminology'], C)
    new['appE_history.tex'] = ('% ' + C + '\n\\input{app_devhistory}\n\\input{app_cov1b_gate}\n'
                               '% Parked for their records move (the outline: the dimensionality survey and the point-cloud work).\n'
                               '\\input{app_landscape}\n\\input{app_pet_pointer}\n')

    # ---- main_note.tex: the body and appendix inputs in the new order
    mn = T.get('main_note.tex')
    old_body = ['sec_intro', 'sec_experiment', 'sec_method', 'sec_systematics', 'sec_validation', 'sec_results',
                'sec_3d', 'sec_eavailw', 'sec_fived16', 'sec_5d', 'sec_joint', 'sec_limitations', 'sec_summary']
    lines = mn.split('\n')
    idx = [i for i, l in enumerate(lines) if re.fullmatch(r'\\input\{(%s)\}' % '|'.join(old_body), l.strip())]
    assert len(idx) == len(old_body), idx
    first, last = idx[0], idx[-1]
    lines[first:last + 1] = ['\\input{part1_intro}', '\\input{part2_method}', '\\input{part3_reproduction}',
                             '\\input{part4_fivedim}', '\\input{part5_validation}', '\\input{part6_validity}']
    mn = '\n'.join(lines)
    assert mn.count('\\input{sec_execsummary}') == 1
    mn = mn.replace('\\input{sec_execsummary}\n', '', 1)
    app_old = ['app_response_mismatch', 'app_landscape', 'app_pet_pointer', 'app_release', 'app_codebase',
               'app_devhistory', 'sec_fps']
    lines = mn.split('\n')
    for name in app_old:
        k = [i for i, l in enumerate(lines) if l.strip() == f'\\input{{{name}}}']
        assert len(k) == 1, name
        lines[k[0]] = {'app_response_mismatch': '\\input{appC_further}', 'app_release': '\\input{appD_release}',
                       'app_devhistory': '\\input{appE_history}'}.get(name, '%SKELETON-DROP%')
    mn = '\n'.join(l for l in lines if l != '%SKELETON-DROP%')
    T.put('main_note.tex', mn)

    for f, s in T.text.items():
        (Path('.') / f).write_text(s, encoding='utf-8')
    for f, s in new.items():
        assert not (Path('.') / f).exists() or f in T.text, f
        (Path('.') / f).write_text(s, encoding='utf-8')
    rows = [f'{mid}\tskeleton-move\t{src}\t{dst}\t{sha}\t-\tverbatim; heading levels as the skeleton sets them'
            for mid, src, dst, sha in T.moves]
    print('\n'.join(rows))
    if a.manifest:
        a.manifest.write_text('\n'.join(rows) + '\n', encoding='utf-8')


def _last_subsection(T: Tree, f: str) -> tuple[int, int]:
    lines = T.get(f).split('\n')
    hs = [i for i, l in enumerate(lines) if level_of(l) == 2]
    assert hs and 'Five-dimensional pseudo-experiments' in lines[hs[-1]], lines[hs[-1]] if hs else None
    return hs[-1], len(lines)


if __name__ == '__main__':
    sys.exit(main())
