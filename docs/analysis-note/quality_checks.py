#!/usr/bin/env python3
"""Deterministic quality counts for a built analysis note: duplication and figure legibility.

The script reports counts and itemized lists.  It sets no pass or fail and changes no file but its report.
It reads a built ``main_note.pdf`` with the source tree it was built from (the ``.tex`` files, the ``.aux``
and the move manifests in ``history-cuts/``), so it can be rerun on any build.

Checks
------
1a  Text duplication.  12-word runs (and exact sentences of eight or more words) that occur in two different
    (sub)sections of the source, in the order main_note.tex inputs them.  Three classes are set aside, each
    with its reason: an intended copy named by a move-manifest row (its mode or note says the body keeps a
    copy), a row of the definitions table restating its home, and a row of the test index restating its home.
    A restatement counts as "at its home" only when the other occurrence lies in a (sub)section that the row
    itself cites with \\ref.  Everything else is listed with both locations.
1b  Figure duplication.  Three signals per pair of figures: a shared producer script or input (from
    figure-plumbing.md, keyed by label), the overlap of the words and tick labels printed inside the figures
    (the PDF text layer), and the similarity of the rendered panels (a 64-bit difference hash and the
    correlation of 32 x 32 grey thumbnails).
1c  Table duplication.  The distinctive numbers of each table (value macros expanded), and the pairs of
    tables that share them.
2   Figure legibility.  For each figure in the PDF: the smallest, the smallest word-like (three or more
    characters in a run) and the median rendered font size inside its bounding box, the characters under the
    flag size (7 pt by default) with examples, the printed width as a fraction of the text width, the aspect
    ratio, the scale at which the included PDF is drawn and any unequal x and y scaling.  Then a summary of
    how consistent the widths and sizes are.

Usage
-----
    python3 quality_checks.py --pdf build/main_note.pdf --note-dir build/docs/analysis-note \\
        --plumbing ~/codex-reports/note-measurement/figure-plumbing.md --out report.md [--json out.json]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import statistics
import subprocess
import sys
import tempfile
from collections import Counter, defaultdict
from pathlib import Path

# --------------------------------------------------------------------------------------------- source model

HEADING_RE = re.compile(r'\\(section|subsection|subsubsection)\*?\s*(?:\[[^\]]*\])?\s*\{')
HEADING_LEVEL = {'section': 1, 'subsection': 2, 'subsubsection': 3}
LABEL_RE = re.compile(r'\\label\{([^}]*)\}')
REF_RE = re.compile(r'\\(?:[cC]?ref|autoref|eqref|pageref)\{([^}]*)\}')
INPUT_RE = re.compile(r'\\input\{([^}]*)\}')

# Macros dropped from the word stream: layout, fonts and spacing.  Every other macro name is kept as a word, so
# \Eavail and \pT match their copies.
DROP_MACROS = set('''
textbf textit emph texttt textrm textsf mathrm mathbf mathit mathcal mathsf text textnormal small footnotesize
scriptsize tiny normalsize large Large centering raggedright RaggedRight arraybackslash toprule midrule bottomrule
cmidrule addlinespace hline left right quad qquad noindent par newline linebreak smallskip medskip bigskip vspace
hspace phantom hfill vfill nolinebreak allowbreak relax protect displaystyle textstyle scriptstyle mbox hbox makebox
item begin end label caption endfirsthead endhead endfoot endlastfoot multicolumn multirow S SI si num ensuremath
footnote href url hyperref nobreakdash xspace leavevmode cdot times pm mp approx sim simeq le leq ge geq ldots dots
cdots ,
'''.split())


def strip_comment(line: str) -> str:
    """Remove a TeX comment (an unescaped %) from one line."""
    out = []
    i = 0
    while i < len(line):
        ch = line[i]
        if ch == '\\' and i + 1 < len(line):
            out.append(line[i:i + 2])
            i += 2
            continue
        if ch == '%':
            break
        out.append(ch)
        i += 1
    return ''.join(out)


def brace_group(s: str, i: int) -> int:
    """Return the index after the brace group that starts at s[i] == '{' (or i if none)."""
    if i >= len(s) or s[i] != '{':
        return i
    depth = 0
    for j in range(i, len(s)):
        if s[j] == '\\':
            continue
        if s[j] == '{' and (j == 0 or s[j - 1] != '\\'):
            depth += 1
        elif s[j] == '}' and (j == 0 or s[j - 1] != '\\'):
            depth -= 1
            if depth == 0:
                return j + 1
    return len(s)


def input_order(note_dir: Path, main: str = 'main_note.tex') -> list[str]:
    """The files main_note.tex inputs, in order, the main file first (preamble and values files excluded)."""
    order = [main]
    for raw in (note_dir / main).read_text(encoding='utf-8').splitlines():
        line = strip_comment(raw)
        for m in INPUT_RE.finditer(line):
            name = m.group(1)
            if not name.endswith('.tex'):
                name += '.tex'
            if name.startswith(('preamble', 'values')) or not (note_dir / name).exists():
                continue
            order.append(name)
            # one level of nested \input (sec_3d inputs scalar_kinematics, and so on)
            for raw2 in (note_dir / name).read_text(encoding='utf-8').splitlines():
                for m2 in INPUT_RE.finditer(strip_comment(raw2)):
                    sub = m2.group(1) + ('' if m2.group(1).endswith('.tex') else '.tex')
                    if (note_dir / sub).exists() and sub not in order:
                        order.append(sub)
    return order


class Source:
    """The note's source as one word stream, with each word's file, line and (sub)section."""

    TABLE_ENVS = ('table', 'table*', 'xltabular', 'longtable', 'tabularx', 'tabular')

    def __init__(self, note_dir: Path, files: list[str]):
        self.note_dir = note_dir
        self.files = files
        self.lines: dict[str, list[str]] = {}
        self.words: list[str] = []      # normalized words
        self.pos: list[tuple[str, int]] = []   # (file, line) of each word
        self.unit: list[int] = []        # index into self.units
        self.units: list[dict] = []      # {file, line, level, title, end_file, end_line}
        self.labels: dict[str, tuple[str, int]] = {}
        self.label_unit: dict[str, int] = {}
        self.envs: list[dict] = []       # table and figure environments: {kind, file, start, end, labels}
        self._build()

    # A unit is the finest (sub)section a word is in.
    def _build(self):
        cur_unit = self._new_unit(self.files[0], 0, 0, '(main file)')
        in_document = False
        for f in self.files:
            text = (self.note_dir / f).read_text(encoding='utf-8')
            raw_lines = text.splitlines()
            self.lines[f] = raw_lines
            if f != self.files[0]:
                cur_unit = self._new_unit(f, 0, 9, f'(start of {f})')
            env_stack: list[dict] = []
            for ln, raw in enumerate(raw_lines, start=1):
                line = strip_comment(raw)
                if f == self.files[0]:
                    if '\\begin{document}' in line:
                        in_document = True
                    if not in_document:
                        continue
                for m in re.finditer(r'\\(begin|end)\{([^}]*)\}', line):
                    kind = m.group(2)
                    if kind in self.TABLE_ENVS + ('figure', 'figure*'):
                        if m.group(1) == 'begin':
                            env_stack.append({'kind': kind, 'file': f, 'start': ln, 'end': ln, 'labels': []})
                        elif env_stack:
                            env = env_stack.pop()
                            env['end'] = ln
                            # tabular inside table: keep only the outer environment
                            if not env_stack:
                                self.envs.append(env)
                            else:
                                env_stack[-1]['labels'] += env['labels']
                if '\\begin{abstract}' in line:
                    cur_unit = self._new_unit(f, ln, 1, 'Abstract')
                elif '\\end{abstract}' in line:
                    cur_unit = self._new_unit(f, ln, 1, '(main file, after the abstract)')
                hm = HEADING_RE.search(line)
                if hm:
                    end = brace_group(line, hm.end() - 1)
                    title = line[hm.end():end - 1]
                    cur_unit = self._new_unit(f, ln, HEADING_LEVEL[hm.group(1)], title)
                for lm in LABEL_RE.finditer(line):
                    self.labels[lm.group(1)] = (f, ln)
                    self.label_unit[lm.group(1)] = cur_unit
                    if env_stack:
                        env_stack[0]['labels'].append(lm.group(1))
                for w in tokenize(line):
                    self.words.append(w)
                    self.pos.append((f, ln))
                    self.unit.append(cur_unit)
        # unit extents: a unit runs to the next unit of the same or a higher level
        for i, u in enumerate(self.units):
            end = len(self.words)
            for j in range(i + 1, len(self.units)):
                if self.units[j]['level'] <= u['level']:
                    end = self.units[j]['first_word']
                    break
            u['last_word'] = end

    def _new_unit(self, f, ln, level, title):
        self.units.append({'file': f, 'line': ln, 'level': level, 'title': clean_title(title),
                           'first_word': len(self.words)})
        return len(self.units) - 1

    def word_in_label_span(self, k: int, label: str) -> bool:
        """True when word k lies inside the (sub)section that holds \\label{label}, sub-units included."""
        u = self.label_unit.get(label)
        if u is None:
            return False
        unit = self.units[u]
        return unit['first_word'] <= k < unit['last_word']

    def env_of(self, f: str, ln: int):
        for env in self.envs:
            if env['file'] == f and env['start'] <= ln <= env['end']:
                return env
        return None

    def where(self, k: int) -> str:
        f, ln = self.pos[k]
        return f'{f}:{ln}'

    def unit_name(self, u: int) -> str:
        unit = self.units[u]
        return unit['title'] or unit['file']


def clean_title(t: str) -> str:
    t = re.sub(r'\\[a-zA-Z]+\*?', '', t)
    return re.sub(r'[{}$~]', '', t).strip()


def tokenize(line: str) -> list[str]:
    """Normalize one comment-free TeX line to words: refs and cites become REF and CITE, column specs,
    lengths and environment names are dropped, and kept macro names become words."""
    s = line
    s = re.sub(r'\\begin\{(?:tabular|xltabular|tabularx|longtable)\}(\{[^{}]*\})?', ' ', s)
    s = re.sub(r'@\{\}|>\{[^{}]*(\{[^{}]*\}[^{}]*)*\}|p\{[0-9.]+\\(?:text|line|column)width\}', ' ', s)
    s = re.sub(r'\\hsize=[0-9.]+\\hsize', ' ', s)
    s = re.sub(r'[0-9.]+\\(?:textwidth|linewidth|columnwidth|hsize)', ' ', s)
    s = re.sub(r'\\includegraphics(\[[^\]]*\])?\{[^}]*\}', ' ', s)
    s = re.sub(r'\\(?:label|begin|end|input|addcontentsline|setlength|bibliographystyle)\{[^}]*\}(\{[^}]*\})*', ' ', s)
    s = re.sub(r'\\(?:[cC]?ref|autoref|eqref|pageref)\{[^}]*\}', ' REF ', s)
    s = re.sub(r'\\(?:cite[a-z]*|recentry)(\[[^\]]*\])?\{[^}]*\}', ' CITE ', s)
    s = re.sub(r'\[[0-9.]+(?:pt|em|ex|cm|mm|in)\]', ' ', s)
    s = re.sub(r'\\\\', ' ', s)
    out = []
    for m in re.finditer(r'\\([a-zA-Z]+)|([A-Za-z0-9]+(?:\.[0-9]+)?)', s):
        if m.group(1):
            if m.group(1) not in DROP_MACROS:
                out.append(m.group(1).lower())
        else:
            out.append(m.group(2).lower())
    return out


def raw_sentences(text: str) -> list[str]:
    """Split raw TeX text into sentences the way the move manifests hash them (approximately)."""
    return [p.strip() for p in re.split(r'(?<=[.?!])\s+(?=[A-Z\\$(])', text) if p.strip()]


# --------------------------------------------------------------------------------------------- manifests

INTENDED_RE = re.compile(r'\b(a copy|copy|copies|keeps|kept in the body|scope label|repeated|pointer|intended)\b', re.I)


def read_manifests(paths: list[Path]) -> list[dict]:
    rows = []
    for p in paths:
        header = None
        for raw in p.read_text(encoding='utf-8').splitlines():
            if not raw.strip() or raw.startswith('#'):
                continue
            cols = raw.split('\t')
            if cols[0] == 'id':
                header = [c.strip().lower() for c in cols]
                continue
            row = {'file': p.name, 'id': cols[0], 'cols': cols}
            row['shas'] = [c for c in cols if re.fullmatch(r'[0-9a-f]{64}', c.strip())]
            sentence = ''
            if header:
                for name in ('sentence',):
                    if name in header and header.index(name) < len(cols):
                        sentence = cols[header.index(name)]
            else:
                # journal-editor's manifest has no header row: the sentence is the last column
                sentence = cols[-1] if len(cols) >= 7 else ''
            row['sentence'] = sentence
            row['words'] = tokenize(sentence) if sentence else []
            text = ' '.join(cols[1:])
            row['intended'] = bool(INTENDED_RE.search(text))
            row['to'] = next((c for c in cols if re.search(r'sec_limitations|app_devhistory|devhistory|limitations', c)), '')
            row['mode'] = next((c for c in cols if re.match(r'(verbatim|reworded|dedup|move|scope)', c.strip())), '')
            rows.append(row)
    return rows


# --------------------------------------------------------------------------------------------- 1a text

def ngram_runs(src: Source, n: int):
    """Maximal runs of shared n-grams between two occurrences in different units."""
    index: dict[tuple, list[int]] = defaultdict(list)
    W = src.words
    for k in range(len(W) - n + 1):
        index[tuple(W[k:k + n])].append(k)
    diag: dict[tuple[int, int], set[int]] = defaultdict(set)   # (j - i) -> starts i
    for ks in index.values():
        if len(ks) < 2 or len(ks) > 40:
            continue
        for a in range(len(ks)):
            for b in range(a + 1, len(ks)):
                i, j = ks[a], ks[b]
                if src.unit[i] == src.unit[j] and src.unit[i + n - 1] == src.unit[j + n - 1]:
                    continue
                if j - i < n:
                    continue
                diag[j - i].add(i)
    runs = []
    for d, starts in diag.items():
        s = sorted(starts)
        run_start = prev = s[0]
        for i in s[1:] + [None]:
            if i is not None and i == prev + 1:
                prev = i
                continue
            runs.append((run_start, run_start + d, prev - run_start + n))
            if i is not None:
                run_start = prev = i
    runs.sort()
    return runs


def exact_sentence_dups(src: Source, min_words: int, covered: set[int]):
    """Sentences of min_words or more, identical after normalization, in two different units."""
    seen: dict[tuple, list[int]] = defaultdict(list)
    W = src.words
    # sentence ends are not in the word stream, so walk the raw lines again with the same tokenizer
    out = []
    k = 0
    for f in src.files:
        main_skip = f == src.files[0]
        started = not main_skip
        buf: list[int] = []
        for ln, raw in enumerate(src.lines[f], start=1):
            line = strip_comment(raw)
            if main_skip and not started:
                if '\\begin{document}' in line:
                    started = True
                else:
                    continue
            pieces = re.split(r'(?<=[a-z0-9}$)])\.\s+(?=[A-Z\\$])|(?<=[.?!])\s*$', line)
            for pi, piece in enumerate(pieces):
                toks = tokenize(piece)
                for _ in toks:
                    buf.append(k)
                    k += 1
                if pi < len(pieces) - 1 or re.search(r'[.?!]\s*$', line):
                    if len(buf) >= min_words:
                        seen[tuple(W[i] for i in buf)].append(buf[0])
                    buf = []
    for key, ks in seen.items():
        if len(ks) < 2:
            continue
        for a in range(len(ks)):
            for b in range(a + 1, len(ks)):
                i, j = ks[a], ks[b]
                if src.unit[i] == src.unit[j]:
                    continue
                if any(x in covered for x in range(i, i + len(key))):
                    continue
                out.append((i, j, len(key)))
    return out


def row_refs(src: Source, k: int, length: int) -> list[str]:
    """The \\ref labels on the source lines that a span covers (a table row's cited homes)."""
    f = src.pos[k][0]
    lines = sorted({src.pos[x][1] for x in range(k, min(k + length, len(src.pos))) if src.pos[x][0] == f})
    refs = []
    for ln in lines:
        refs += [r for m in REF_RE.finditer(strip_comment(src.lines[f][ln - 1])) for r in m.group(1).split(',')]
    return refs


def check_text(src: Source, manifests: list[dict], n: int, min_sentence: int):
    runs = ngram_runs(src, n)
    covered = set()
    for i, j, L in runs:
        covered.update(range(i, i + L))
        covered.update(range(j, j + L))
    sents = exact_sentence_dups(src, min_sentence, covered)
    W = src.words

    def label_env(k):
        f, ln = src.pos[k]
        env = src.env_of(f, ln)
        return env['labels'] if env else []

    # manifest index: n-grams of manifest sentences, and shas of raw sentences in the source
    man_grams: dict[tuple, list[dict]] = defaultdict(list)
    for row in manifests:
        ws = row['words']
        for q in range(len(ws) - n + 1):
            man_grams[tuple(ws[q:q + n])].append(row)
    sha_rows = defaultdict(list)
    for row in manifests:
        for s in row['shas']:
            sha_rows[s].append(row)
    line_sha_rows: dict[tuple[str, int], list[dict]] = defaultdict(list)
    for f in src.files:
        for ln, raw in enumerate(src.lines[f], start=1):
            for sent in raw_sentences(raw):
                h = hashlib.sha256(sent.encode('utf-8')).hexdigest()
                if h in sha_rows:
                    line_sha_rows[(f, ln)] += sha_rows[h]

    def manifest_rows_for(k, L):
        rows = []
        for q in range(k, k + max(1, L - n + 1)):
            rows += man_grams.get(tuple(W[q:q + n]), [])
        for x in range(k, k + L):
            rows += line_sha_rows.get(src.pos[x], [])
        uniq = {}
        for r in rows:
            uniq[(r['file'], r['id'], r['cols'][1] if len(r['cols']) > 1 else '')] = r
        return list(uniq.values())

    items = []
    for kind, pairs in (('12-gram run' if n == 12 else f'{n}-gram run', runs), ('exact sentence', sents)):
        for i, j, L in pairs:
            item = {'kind': kind, 'a': i, 'b': j, 'len': L, 'class': 'remaining', 'why': ''}
            fa, fb = src.pos[i][0], src.pos[j][0]
            la, lb = label_env(i), label_env(j)
            homes = {'tab:definitions': 'definition', 'tab:test-index': 'test index'}
            for side, other, labs in ((i, j, la), (j, i, lb)):
                for lab, name in homes.items():
                    if lab in labs:
                        refs = row_refs(src, side, L)
                        hit = [r for r in refs if src.word_in_label_span(other, r)]
                        if hit:
                            item['class'] = f'{name} restatement at its home'
                            item['why'] = f'row cites {", ".join(hit)}'
                        else:
                            item['class'] = f'{name} restatement, not at a cited home'
                            item['why'] = 'row cites ' + (', '.join(refs) if refs else 'no \\ref')
            if item['class'] == 'remaining':
                rows = manifest_rows_for(i, L) + manifest_rows_for(j, L)
                in_receiving = any(f in ('sec_limitations.tex', 'app_devhistory.tex') for f in (fa, fb))
                if rows and in_receiving:
                    ids = sorted({r['id'] for r in rows})
                    if any(r['intended'] for r in rows):
                        item['class'] = 'manifest: intended copy'
                        item['why'] = ', '.join(ids) + ' (' + '; '.join(sorted({r['mode'] or '' for r in rows if r['intended']}))[:160] + ')'
                    else:
                        item['why'] = 'matches manifest row ' + ', '.join(ids) + ' (a move, not a copy); the text stands at both locations'
                elif rows:
                    item['why'] = 'manifest row(s) ' + ', '.join(sorted({r['id'] for r in rows}))
            items.append(item)
    return items


def excerpt(src: Source, k: int, L: int, maxw: int = 24) -> str:
    ws = src.words[k:k + min(L, maxw)]
    return ' '.join(ws) + (' …' if L > maxw else '')


def span_where(src: Source, k: int, L: int) -> str:
    f, l0 = src.pos[k]
    f1, l1 = src.pos[min(k + L - 1, len(src.pos) - 1)]
    return f'{f}:{l0}' + (f'-{l1}' if f1 == f and l1 != l0 else '')


# --------------------------------------------------------------------------------------------- aux

def read_aux(aux: Path) -> dict[str, tuple[str, str]]:
    """label -> (printed number, printed page) for every \\newlabel in the aux file."""
    out = {}
    if not aux.exists():
        return out
    for line in aux.read_text(encoding='utf-8', errors='replace').splitlines():
        m = re.match(r'\\newlabel\{([^}]*)\}\{\{([^}]*)\}\{([^}]*)\}', line)
        if m:
            out[m.group(1)] = (m.group(2), m.group(3))
    return out


# --------------------------------------------------------------------------------------------- PDF figures

def load_pdf(pdf: Path):
    """Per page: the captions, the top-level included graphics (LTFigure or LTImage) and their text."""
    import pdfminer.layout as L
    from pdfminer.high_level import extract_pages

    orig = L.LTChar.__init__

    def init(self, matrix, font, fontsize, scaling, rise, *a, **k):
        orig(self, matrix, font, fontsize, scaling, rise, *a, **k)
        # the rendered size: the font size times the length the glyph's vertical unit is drawn at
        self.render_size = fontsize * math.hypot(matrix[2], matrix[3])

    L.LTChar.__init__ = init
    pages = []
    try:
        for pno, page in enumerate(extract_pages(str(pdf), laparams=L.LAParams()), start=1):
            caps, graphics, lines = [], [], []
            for el in page:
                if isinstance(el, L.LTTextContainer):
                    t = el.get_text()
                    lines.append(t)
                    m = re.match(r'\s*(Figure|Table)\s+(\d+):', t)
                    if m:
                        caps.append({'kind': m.group(1), 'num': m.group(2), 'y0': el.y0, 'y1': el.y1,
                                     'x0': el.x0, 'x1': el.x1})
                elif isinstance(el, (L.LTFigure, L.LTImage)):
                    if el.width < 20 or el.height < 20:
                        continue
                    chars = []

                    def walk(node):
                        for c in node:
                            if isinstance(c, L.LTChar):
                                chars.append(c)
                            elif isinstance(c, (L.LTFigure, L.LTContainer)):
                                walk(c)
                    if isinstance(el, L.LTFigure):
                        walk(el)
                    m = getattr(el, 'matrix', (1, 0, 0, 1, 0, 0))
                    graphics.append({
                        'bbox': (el.x0, el.y0, el.x1, el.y1),
                        'sx': math.hypot(m[0], m[1]), 'sy': math.hypot(m[2], m[3]),
                        'chars': [(c.get_text(), round(getattr(c, 'render_size', c.size), 2), c.x0, c.y0, c.x1,
                                   c.y1, bool(getattr(c, 'upright', True))) for c in chars],
                        'raster_only': not chars,
                        'axes': axes_grids(el, L) if isinstance(el, L.LTFigure) else [],
                    })
            pages.append({'n': pno, 'w': page.width, 'h': page.height, 'caps': caps, 'graphics': graphics,
                          'text': ''.join(lines)})
    finally:
        L.LTChar.__init__ = orig
    return pages


AXES_GRID = 40


def axes_grids(fig, L) -> list:
    """The plotted lines of each axes in a graphic, as a 40 x 40 occupancy grid in that axes' own frame.

    An axes is a filled rectangle of at least 40 x 30 pt that is not the figure background.  Its lines are the
    paths that lie wholly inside it, less frame-length horizontal or vertical segments (spines, grid lines) and
    the outer 3% band (ticks).  Two axes that draw the same curves on the same ranges have overlapping grids."""
    import numpy as np
    G = AXES_GRID
    rects, paths = [], []

    def walk(node):
        for c in node:
            if isinstance(c, L.LTFigure):
                walk(c)
            elif isinstance(c, L.LTRect):
                if c.fill and c.width >= 40 and c.height >= 30 and not (
                        c.width > 0.95 * fig.width and c.height > 0.95 * fig.height):
                    rects.append(c)
            elif isinstance(c, (L.LTCurve, L.LTLine)):
                paths.append(c)
    walk(fig)
    grids = []
    for r in rects:
        g = np.zeros((G, G), bool)
        for it in paths:
            pts = list(it.pts)
            if not pts or not all(r.x0 - 0.5 <= x <= r.x1 + 0.5 and r.y0 - 0.5 <= y <= r.y1 + 0.5 for x, y in pts):
                continue
            for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
                if (abs(y1 - y0) < 0.01 and abs(x1 - x0) > 0.9 * r.width) or (
                        abs(x1 - x0) < 0.01 and abs(y1 - y0) > 0.9 * r.height):
                    continue
                span = max(abs(x1 - x0) / r.width, abs(y1 - y0) / r.height)
                for t in np.linspace(0, 1, max(2, int(span * G * 2) + 1)):
                    u = (x0 + (x1 - x0) * t - r.x0) / r.width
                    v = (y0 + (y1 - y0) * t - r.y0) / r.height
                    if 0.03 < u < 0.97 and 0.03 < v < 0.97:
                        g[min(G - 1, int(v * G)), min(G - 1, int(u * G))] = True
        if g.sum() >= 15:
            grids.append(g)
    return grids


def assign_graphics(pages):
    """Figure number -> list of (page, graphic).  A graphic belongs to the nearest figure caption below it on
    its page, or, failing that, the nearest above it."""
    figs = defaultdict(list)
    for p in pages:
        caps = [c for c in p['caps'] if c['kind'] == 'Figure']
        for g in p['graphics']:
            gx0, gy0, gx1, gy1 = g['bbox']
            below = [c for c in caps if c['y1'] <= gy0 + 2]
            above = [c for c in caps if c['y0'] >= gy1 - 2]
            if below:
                c = max(below, key=lambda c: c['y1'])
            elif above:
                c = min(above, key=lambda c: c['y0'])
            else:
                continue
            figs[int(c['num'])].append((p['n'], g))
    return figs


def char_runs(chars):
    """Group a graphic's characters into runs (same baseline and size, adjacent): the printed strings."""
    rows = defaultdict(list)
    for t, s, x0, y0, x1, y1, up in chars:
        key = (round(y0 if up else x0), s, up)
        rows[key].append((x0, x1, t, y0, y1) if up else (y0, y1, t, x0, x1))
    runs = []
    for (base, s, up), cs in rows.items():
        cs.sort()
        cur, first, last, lo, hi = '', None, None, None, None
        for a, b, t, c0, c1 in cs:
            if last is not None and a - last > 0.4 * s:
                runs.append((cur, s, (first, lo, last, hi) if up else (lo, first, hi, last)))
                cur, first, lo, hi = '', None, None, None
            if first is None:
                first = a
            cur += t
            last = b
            lo = c0 if lo is None else min(lo, c0)
            hi = c1 if hi is None else max(hi, c1)
        if cur:
            runs.append((cur, s, (first, lo, last, hi) if up else (lo, first, hi, last)))
    return runs


def text_collisions(runs) -> int:
    """Pairs of printed strings whose boxes overlap by more than 30% of the smaller box."""
    boxes = [b for t, s, b in runs if t.strip()]
    n = 0
    for i in range(len(boxes)):
        ax0, ay0, ax1, ay1 = boxes[i]
        for j in range(i + 1, len(boxes)):
            bx0, by0, bx1, by1 = boxes[j]
            w = min(ax1, bx1) - max(ax0, bx0)
            h = min(ay1, by1) - max(ay0, by0)
            if w > 0 and h > 0:
                small = min((ax1 - ax0) * (ay1 - ay0), (bx1 - bx0) * (by1 - by0))
                if small > 0 and w * h > 0.3 * small:
                    n += 1
    return n


def figure_text_words(chars) -> set[str]:
    words = set()
    for run, *_ in char_runs(chars):
        for w in re.findall(r'[A-Za-z]+|\d+(?:\.\d+)?', run):
            words.add(w.lower())
    return words


def textwidth_pt(note_dir: Path, pages) -> tuple[float, str]:
    pre = ''
    for name in ('preamble.tex', 'main_note.tex'):
        if (note_dir / name).exists():
            pre += (note_dir / name).read_text(encoding='utf-8')
    m = re.search(r'\\usepackage\[[^\]]*margin=([0-9.]+)(in|cm|mm|pt)[^\]]*\]\{geometry\}', pre)
    pw = statistics.median(p['w'] for p in pages)
    if m:
        unit = {'in': 72.0, 'cm': 72 / 2.54, 'mm': 72 / 25.4, 'pt': 72 / 72.27}[m.group(2)]
        return pw - 2 * float(m.group(1)) * unit, f'page width {pw:.0f} pt less two {m.group(1)}{m.group(2)} margins (geometry)'
    return 0.75 * pw, 'assumed 0.75 of the page width (no geometry margin found)'


def render_thumbs(pdf: Path, figs, dpi: int = 50):
    """Grey 32x32 thumbnails and 64-bit difference hashes of each panel, from the built PDF."""
    import numpy as np
    from PIL import Image
    thumbs = {}
    need = sorted({pn for v in figs.values() for pn, _ in v})
    with tempfile.TemporaryDirectory() as td:
        for pn in need:
            stem = Path(td) / f'p{pn}'
            subprocess.run(['pdftoppm', '-f', str(pn), '-l', str(pn), '-r', str(dpi), '-gray', '-png', str(pdf),
                            str(stem)], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        files = {int(re.search(r'-(\d+)\.png$', f.name).group(1)): f for f in Path(td).glob('p*-*.png')}
        cache = {pn: Image.open(files[pn]).convert('L') for pn in need if pn in files}
        for num, panels in figs.items():
            for idx, (pn, g) in enumerate(panels):
                im = cache.get(pn)
                if im is None:
                    continue
                scale = dpi / 72.0
                x0, y0, x1, y1 = g['bbox']
                H = im.height
                box = (int(x0 * scale), int(H - y1 * scale), int(math.ceil(x1 * scale)), int(math.ceil(H - y0 * scale)))
                crop = im.crop(box)
                small = np.asarray(crop.resize((32, 32), Image.BILINEAR), dtype=float)
                d = np.asarray(crop.resize((9, 8), Image.BILINEAR), dtype=float)
                bits = (d[:, 1:] > d[:, :-1]).flatten()
                thumbs[(num, idx)] = (small, int(''.join('1' if b else '0' for b in bits), 2))
    return thumbs


def thumb_corr(a, b) -> float:
    a = a - a.mean()
    b = b - b.mean()
    den = math.sqrt(float((a * a).sum()) * float((b * b).sum()))
    return float((a * b).sum()) / den if den else 0.0


# --------------------------------------------------------------------------------------------- plumbing

def read_plumbing(path: Path | None) -> dict[str, dict]:
    """label -> {'producers': set, 'inputs': set, 'row': old figure number} from figure-plumbing.md."""
    out = {}
    if not path or not path.exists():
        return out
    by_old: dict[str, dict] = {}
    prev = None
    for line in path.read_text(encoding='utf-8').splitlines():
        if not re.match(r'\|\s*\d', line):
            continue
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        if len(cells) < 5:
            continue
        old, labels, _inc, producer, inputs = cells[:5]
        prods = {Path(t).name for t in re.findall(r'`([^`]*\.py)[^`]*`', producer)}
        prods |= {Path(t.split()[0]).name for t in re.findall(r'`([^`]+\.py)', producer)}
        m = re.search(r'as Fig\.\s*(\d+)', producer)
        if m and m.group(1) in by_old:
            prods |= by_old[m.group(1)]['producers']
        ins = {Path(t).name for t in re.findall(r'`([^`]+\.(?:root|npz|json|figpickle|txt))`', inputs)}
        if re.search(r'pickles', inputs):
            ins.add('runs/family4/pickles')
        if not ins and prev is not None and re.match(r'\s*(same|as Fig)', inputs):
            ins = set(prev['inputs'])
        m = re.search(r'as Fig\.\s*(\d+)', inputs)
        if m and m.group(1) in by_old:
            ins |= by_old[m.group(1)]['inputs']
        rec = {'producers': prods, 'inputs': ins, 'row': old}
        for o in re.findall(r'\d+', old):
            by_old[o] = rec
        # labels: "fig:a, fig:b" or "fig:gbdt-recovery, -bias-spread"
        labs = [x.strip().strip('`') for x in labels.split(',')]
        base = None
        for lab in labs:
            if lab.startswith('fig:'):
                base = lab.rsplit('-', 1)[0] if '-' in lab else lab
                out[lab] = rec
            elif lab.startswith('-') and base:
                out[base + lab] = rec
        prev = rec
    return out


def producer_arrays(plumbing: dict[str, dict], repo: Path | None) -> dict[str, set[str]]:
    """label -> the ROOT objects its producer scripts read by name (Get("...")), when a checkout is given."""
    out: dict[str, set[str]] = {}
    if not repo or not plumbing:
        return out
    try:
        listed = subprocess.run(['git', '-C', str(repo), 'ls-files', '*.py'], capture_output=True, text=True,
                                check=True).stdout.split()
    except (OSError, subprocess.CalledProcessError):
        return out
    by_name = defaultdict(list)
    for f in listed:
        by_name[Path(f).name].append(f)
    cache: dict[str, set[str]] = {}
    for lab, rec in plumbing.items():
        names = set()
        for prod in rec['producers']:
            if prod not in cache:
                got = set()
                for f in by_name.get(prod, [])[:1]:
                    text = (repo / f).read_text(encoding='utf-8', errors='replace')
                    got |= set(re.findall(r'\bGet\(\s*[\'"]([^\'"]+)[\'"]\s*\)', text))
                cache[prod] = got
            names |= cache[prod]
        out[lab] = names
    return out


# --------------------------------------------------------------------------------------------- 1c tables

def read_value_macros(note_dir: Path) -> dict[str, str]:
    macros = {}
    for p in sorted(note_dir.glob('values*.tex')):
        s = p.read_text(encoding='utf-8')
        for m in re.finditer(r'\\(?:newcommand|renewcommand|providecommand)\*?\{?\\([A-Za-z]+)\}?(?:\[\d\])?\s*\{', s):
            end = brace_group(s, m.end() - 1)
            macros[m.group(1)] = s[m.end():end - 1]
        for m in re.finditer(r'\\@namedef\{([A-Za-z]+@[^}]*)\}\s*\{', s):
            end = brace_group(s, m.end() - 1)
            macros[m.group(1)] = s[m.end():end - 1]
        for m in re.finditer(r'\\def\\([A-Za-z]+)\s*\{', s):
            end = brace_group(s, m.end() - 1)
            macros[m.group(1)] = s[m.end():end - 1]
    return macros


def expand(s: str, macros: dict[str, str], depth: int = 6) -> str:
    keyed = {'fvval': 'fv@', 'lrval': 'lr@'}
    for _ in range(depth):
        new = re.sub(r'\\(fvval|lrval)\{([^}]*)\}', lambda m: macros.get(keyed[m.group(1)] + m.group(2), m.group(0)), s)
        new = re.sub(r'\\([A-Za-z]+)', lambda m: macros.get(m.group(1), m.group(0)), new)
        if new == s:
            break
        s = new
    return s


NUM_RE = re.compile(r'(?<![A-Za-z0-9.])(\d+(?:\.\d+)?)(?![0-9])')


def sig_digits(num: str) -> int:
    """Significant digits as printed: leading zeros dropped, and an integer's trailing zeros."""
    if '.' in num:
        return len(num.replace('.', '').lstrip('0'))
    return len(num.lstrip('0').rstrip('0'))


def distinctive(num: str) -> bool:
    if '.' in num:
        sig = num.replace('.', '').lstrip('0')
        return len(sig) >= 2
    v = int(num)
    return v >= 100 and not (1900 <= v <= 2099)


def table_numbers(src: Source, env: dict, macros: dict[str, str]) -> Counter:
    lines = src.lines[env['file']][env['start'] - 1:env['end']]
    s = '\n'.join(strip_comment(x) for x in lines)
    # drop the caption, column specs, widths and spacing; keep the cells
    m = re.search(r'\\caption(\[[^\]]*\])?\{', s)
    if m:
        s = s[:m.start()] + s[brace_group(s, m.end() - 1):]
    s = re.sub(r'\\begin\{(?:tabular|xltabular|tabularx|longtable)\}(\{[^{}]*\})?', ' ', s)
    s = re.sub(r'>\{[^{}]*(\{[^{}]*\}[^{}]*)*\}|p\{[0-9.]+\\(?:text|line|column)width\}|@\{\}', ' ', s)
    s = re.sub(r'\\hsize=[0-9.]+\\hsize|[0-9.]+\\(?:textwidth|linewidth|columnwidth|hsize)', ' ', s)
    s = re.sub(r'\[[0-9.\-]+(?:pt|em|ex|cm|mm|in)\]|\{[0-9.\-]+(?:pt|em|ex|cm|mm|in)\}', ' ', s)
    s = re.sub(r'\\(?:[cC]?ref|label|cite[a-z]*|recentry|setlength|LTcapwidth)(\[[^\]]*\])?\{[^}]*\}', ' ', s)
    s = expand(s, macros)
    return Counter(n for n in NUM_RE.findall(s) if distinctive(n))


# --------------------------------------------------------------------------------------------- report

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--pdf', required=True, type=Path)
    ap.add_argument('--note-dir', required=True, type=Path, help='the source tree the PDF was built from')
    ap.add_argument('--aux', type=Path, help='default: main_note.aux beside the PDF, else in --note-dir')
    ap.add_argument('--manifests', nargs='*', type=Path, help='default: history-cuts/move-manifest-*.tsv')
    ap.add_argument('--plumbing', type=Path, help='figure-plumbing.md (producers and inputs by label)')
    ap.add_argument('--repo', type=Path, help='a checkout holding the producer scripts, for the ROOT objects they read')
    ap.add_argument('--ngram', type=int, default=12)
    ap.add_argument('--min-sentence', type=int, default=8)
    ap.add_argument('--min-font', type=float, default=7.0)
    ap.add_argument('--label', default='', help='a name for the build in the report header (a sha)')
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--json', type=Path)
    args = ap.parse_args(argv)

    note_dir = args.note_dir
    aux = args.aux or (args.pdf.with_suffix('.aux') if args.pdf.with_suffix('.aux').exists() else note_dir / 'main_note.aux')
    labels = read_aux(aux)
    files = input_order(note_dir)
    src = Source(note_dir, files)
    man_paths = args.manifests if args.manifests is not None else sorted((note_dir / 'history-cuts').glob('move-manifest-*.tsv'))
    manifests = read_manifests(man_paths)
    R = []   # report lines
    J = {'pdf': str(args.pdf), 'label': args.label}

    # ---- 1a text
    items = check_text(src, manifests, args.ngram, args.min_sentence)
    by_class = Counter(it['class'] for it in items)
    remaining = [it for it in items if it['class'] in ('remaining',) or 'not at a cited home' in it['class']]
    remaining.sort(key=lambda it: (-it['len'], it['a']))
    pair_count = Counter()
    for it in items:
        if it['class'] == 'remaining':
            pair_count[tuple(sorted((src.pos[it['a']][0], src.pos[it['b']][0])))] += 1

    # ---- PDF
    pages = load_pdf(args.pdf)
    figs = assign_graphics(pages)
    tw, tw_how = textwidth_pt(note_dir, pages)
    fig_labels = {}
    for lab, (num, page) in labels.items():
        if lab.startswith('fig:') and num.isdigit():
            fig_labels.setdefault(int(num), []).append(lab)
    plumbing = read_plumbing(args.plumbing)

    # ---- 2 legibility
    leg = []
    for num in sorted(set(figs) | set(fig_labels)):
        panels = figs.get(num, [])
        chars = [c for _, g in panels for c in g['chars']]
        sizes = sorted(c[1] for c in chars if c[0].strip())
        runs = [r for _, g in panels for r in char_runs(g['chars'])]
        wordlike = sorted(s for t, s, _ in runs if len(re.sub(r'\W', '', t)) >= 3)
        small = sorted({(round(s, 1), t.strip()) for t, s, _ in runs if s < args.min_font and t.strip()})
        collisions = sum(text_collisions(char_runs(g['chars'])) for _, g in panels)
        if panels:
            x0 = min(g['bbox'][0] for _, g in panels)
            x1 = max(g['bbox'][2] for _, g in panels)
            widths = [g['bbox'][2] - g['bbox'][0] for _, g in panels]
            aspects = [(g['bbox'][3] - g['bbox'][1]) / (g['bbox'][2] - g['bbox'][0]) for _, g in panels]
            sxs = [g['sx'] for _, g in panels]
            aniso = [g['sy'] / g['sx'] for _, g in panels if g['sx']]
        rec = {
            'fig': num, 'labels': fig_labels.get(num, []), 'pages': sorted({pn for pn, _ in panels}),
            'panels': len(panels), 'raster_only_panels': sum(1 for _, g in panels if g['raster_only']),
            'n_chars': len(sizes),
            'min_pt': sizes[0] if sizes else None,
            'min_wordlike_pt': wordlike[0] if wordlike else None,
            'median_pt': statistics.median(sizes) if sizes else None,
            'p10_pt': sizes[len(sizes) // 10] if sizes else None,
            'text_collisions': collisions,
            'n_axes': sum(len(g['axes']) for _, g in panels),
            'n_chars_below': sum(1 for s in sizes if s < args.min_font),
            'small_examples': [f'{t} ({s} pt)' for s, t in small[:6]],
            'width_frac': (x1 - x0) / tw if panels else None,
            'panel_width_frac': [w / tw for w in widths] if panels else [],
            'aspect_h_over_w': aspects if panels else [],
            'scale': sxs if panels else [],
            'y_over_x_scale': aniso if panels else [],
        }
        leg.append(rec)

    # ---- 1b figures
    import numpy as np
    thumbs = render_thumbs(args.pdf, figs)
    axes = {num: [g2 for _, g in figs[num] for g2 in g['axes']] for num in figs}
    flat = {num: (np.array([a.ravel() for a in axes[num]], dtype=float) if axes[num] else None) for num in figs}
    arrays = producer_arrays(plumbing, args.repo)
    words = {num: figure_text_words([c for _, g in figs[num] for c in g['chars']]) for num in figs}
    fig_pairs = []
    nums = sorted(figs)
    for a_i, a in enumerate(nums):
        for b in nums[a_i + 1:]:
            wa, wb = words[a], words[b]
            jac = len(wa & wb) / len(wa | wb) if (wa | wb) else 0.0
            best_corr, best_ham, best_panels = -1.0, 65, None
            for ia in range(len(figs[a])):
                for ib in range(len(figs[b])):
                    ta, tb = thumbs.get((a, ia)), thumbs.get((b, ib))
                    if ta is None or tb is None:
                        continue
                    c = thumb_corr(ta[0], tb[0])
                    h = bin(ta[1] ^ tb[1]).count('1')
                    if c > best_corr:
                        best_corr, best_ham, best_panels = c, h, (ia + 1, ib + 1)
            shared_prod, shared_in, shared_arr = set(), set(), set()
            for la in fig_labels.get(a, []):
                for lb in fig_labels.get(b, []):
                    pa, pb = plumbing.get(la), plumbing.get(lb)
                    if pa and pb:
                        shared_prod |= pa['producers'] & pb['producers']
                        shared_in |= pa['inputs'] & pb['inputs']
                        if pa['inputs'] & pb['inputs']:
                            shared_arr |= arrays.get(la, set()) & arrays.get(lb, set())
            data_best, data_match = 0.0, (0, 0)
            if flat[a] is not None and flat[b] is not None:
                inter = flat[a] @ flat[b].T
                union = flat[a].sum(1)[:, None] + flat[b].sum(1)[None, :] - inter
                jm = inter / np.maximum(union, 1)
                data_best = float(jm.max())
                data_match = (int((jm.max(1) >= 0.3).sum()), int((jm.max(0) >= 0.3).sum()))
            signals = []
            if data_best >= 0.3:
                signals.append('data' if (shared_arr or shared_in) else 'curves')
            if shared_in or shared_prod:
                signals.append('producer')
            if jac >= 0.5:
                signals.append('text')
            if best_corr >= 0.9 or best_ham <= 8:
                signals.append('image')
            fig_pairs.append({'a': a, 'b': b, 'jaccard': jac, 'corr': best_corr, 'hamming': best_ham,
                              'data_best': data_best, 'data_match': data_match, 'shared_arrays': sorted(shared_arr),
                              'panels': best_panels, 'shared_producers': sorted(shared_prod),
                              'shared_inputs': sorted(shared_in), 'signals': signals})
    content = ('data', 'text', 'image')
    fig_pairs.sort(key=lambda p: (-sum(1 for x in p['signals'] if x in content), 'producer' not in p['signals'],
                                  -p['data_best'], -p['jaccard']))
    groups = defaultdict(set)   # a shared input or producer -> figures
    for num, labs in fig_labels.items():
        for lab in labs:
            rec = plumbing.get(lab)
            if rec:
                for x in rec['inputs']:
                    groups[('input', x)].add(num)
                for x in rec['producers']:
                    groups[('producer', x)].add(num)
                for x in arrays.get(lab, ()):
                    groups[('array', x)].add(num)

    # ---- 1c tables
    macros = read_value_macros(note_dir)
    tables = []
    for env in src.envs:
        tabs = [l for l in env['labels'] if l.startswith('tab:')]
        if not tabs or env['kind'] in ('figure', 'figure*'):
            continue
        lab = tabs[0]
        num = labels.get(lab, ('?', '?'))[0]
        tables.append({'label': lab, 'num': num, 'where': f"{env['file']}:{env['start']}",
                       'numbers': table_numbers(src, env, macros)})
    tab_pairs = []
    for i in range(len(tables)):
        for j in range(i + 1, len(tables)):
            A, B = set(tables[i]['numbers']), set(tables[j]['numbers'])
            shared = A & B
            strong = {x for x in shared if sig_digits(x) >= 3}
            overlap = len(shared) / min(len(A), len(B)) if shared else 0.0
            if len(strong) >= 3 or (len(shared) >= 3 and overlap >= 0.5):
                tab_pairs.append({'a': i, 'b': j, 'shared': sorted(shared, key=float), 'strong': sorted(strong, key=float),
                                  'overlap': overlap})
    tab_pairs.sort(key=lambda p: (-len(p['strong']), -p['overlap']))

    # ================================================================ write
    # 1a: one row per duplicated passage; a passage repeated in k places is one row with k locations
    def in_table(k):
        env = src.env_of(*src.pos[k])
        return env and env['kind'] not in ('figure', 'figure*')

    passages: dict[tuple, dict] = {}
    for it in remaining:
        key = (it['class'], tuple(src.words[it['a']:it['a'] + it['len']]))
        P = passages.setdefault(key, {'class': it['class'], 'len': it['len'], 'locs': {}, 'why': set(), 'kinds': set()})
        for k in (it['a'], it['b']):
            P['locs'][src.pos[k]] = k
        if it['why']:
            P['why'].add(it['why'])
    for P in passages.values():
        ks = sorted(P['locs'].values())
        P['ks'] = ks
        P['tables'] = sum(1 for k in ks if in_table(k))
        P['captions'] = sum(1 for k in ks if (src.env_of(*src.pos[k]) or {}).get('kind') in ('figure', 'figure*'))
    plist = sorted(passages.values(), key=lambda P: (-P['len'] * (len(P['ks']) - 1), P['ks'][0]))
    n_rem = len(plist)
    n_rem_pairs = by_class['remaining']
    n_home = sum(v for k, v in by_class.items() if 'at its home' in k)
    n_nohome = sum(v for k, v in by_class.items() if 'not at a cited home' in k)
    rem_words = sum(P['len'] * (len(P['ks']) - 1) for P in plist if P['class'] == 'remaining')
    under = [r for r in leg if r['n_chars_below']]
    wf = [r['width_frac'] for r in leg if r['width_frac']]
    content_pairs = [p for p in fig_pairs if any(x in ('data', 'text', 'image') for x in p['signals'])]
    shown_pairs = [p for p in fig_pairs if p['signals']]
    pair_best = sorted(p['data_best'] for p in fig_pairs)

    head = args.label or args.pdf.name
    R.append(f'# Deterministic quality counts: {head}')
    R.append('')
    R.append(f'PDF `{args.pdf}` ({len(pages)} pages, sha256 `{hashlib.sha256(args.pdf.read_bytes()).hexdigest()[:16]}…`). '
             f'Source `{note_dir}` ({len(files)} files in input order). Made by `quality_checks.py` '
             f'(sha256 `{hashlib.sha256(Path(__file__).read_bytes()).hexdigest()[:16]}…`). Counts and lists only; '
             'nothing here is a pass or a fail. Figure and table numbers are this build\'s.')
    R.append('')
    R.append('## Counts')
    R.append('')
    R.append('| check | count |')
    R.append('|---|---|')
    R.append(f'| 1a duplicated passages across (sub)sections, remaining | **{sum(1 for P in plist if P["class"] == "remaining")}** '
             f'({n_rem_pairs} location pairs, {rem_words} repeated words) |')
    R.append(f'| 1a … of which wholly inside tables / in figure captions (some location) | '
             f'{sum(1 for P in plist if P["class"] == "remaining" and P["tables"] == len(P["ks"]))} / '
             f'{sum(1 for P in plist if P["class"] == "remaining" and P["captions"])} |')
    R.append(f'| 1a definition / test-index restatements NOT at a cited home (listed) | {n_nohome} |')
    R.append(f'| 1a set aside: manifest intended copies | {by_class["manifest: intended copy"]} |')
    R.append(f'| 1a set aside: definition / test-index restatements at their cited home | {n_home} |')
    R.append(f'| 1b figure pairs with a content signal (data, text or image) | **{len(content_pairs)}** |')
    R.append(f'| 1b … with the data signal (a shared input, and overlapping curves) | **{sum(1 for p in fig_pairs if "data" in p["signals"])}** |')
    R.append(f'| 1b figure pairs sharing a producer input or script | {sum(1 for p in fig_pairs if "producer" in p["signals"])} |')
    R.append(f'| 1b figure pairs with overlapping curves but no shared input (listed, not counted) | {sum(1 for p in fig_pairs if "curves" in p["signals"])} |')
    R.append(f'| 1c table pairs sharing three or more strong numbers (or half the smaller table) | **{len(tab_pairs)}** |')
    R.append(f'| 2 figures found in the PDF / numbered figures in the aux | {len(figs)} / {len(fig_labels)} |')
    R.append(f'| 2 figures with any text under {args.min_font:g} pt | **{len(under)}** |')
    R.append(f'| 2 figures whose 10th-percentile text size is under {args.min_font:g} pt | **{sum(1 for r in leg if r["p10_pt"] is not None and r["p10_pt"] < args.min_font)}** |')
    R.append(f'| 2 figures whose median text size is under {args.min_font:g} pt | **{sum(1 for r in leg if r["median_pt"] is not None and r["median_pt"] < args.min_font)}** |')
    R.append(f'| 2 figures with overlapping printed strings | {sum(1 for r in leg if r["text_collisions"])} |')
    R.append(f'| 2 figures with no text layer in a panel (raster) | {sum(1 for r in leg if r["raster_only_panels"])} |')
    R.append(f'| 2 figures drawn with unequal x and y scale (> 1%) | {sum(1 for r in leg if any(abs(v - 1) > 0.01 for v in r["y_over_x_scale"]))} |')
    R.append(f'| 2 distinct printed widths (fraction of text width, 2 decimals) | {len({round(v, 2) for v in wf})} |')
    R.append('')

    # 1a
    R.append('## 1a. Text duplication')
    R.append('')
    R.append(f'Method: the source in input order as one word stream (comments, column specs, lengths and labels dropped; '
             f'`\\ref` → REF, `\\cite` → CITE; macro names kept as words, so `\\lrval{{x}}` reads "lrval x"). A duplicate '
             f'is a maximal run of shared {args.ngram}-word sequences, or an identical sentence of {args.min_sentence}+ '
             'words, whose occurrences lie in different (sub)sections. One row per passage; a passage in k places has k '
             'locations. Set aside: a move-manifest row whose mode or note says the body keeps a copy, with one copy in '
             'sec_limitations.tex or app_devhistory.tex; and a row of the definitions table or the test index whose other '
             'occurrence lies in a (sub)section the row cites with `\\ref`.')
    R.append('')
    R.append('**Pairs by class:** ' + '; '.join(f'{k}: {v}' for k, v in sorted(by_class.items())))
    R.append('')
    R.append('**Remaining location pairs by file pair:** ' + '; '.join(f'{a} ↔ {b}: {v}' for (a, b), v in pair_count.most_common()))
    R.append('')
    R.append('| # | words | locations (section) | where | note | text (normalized) |')
    R.append('|---|---|---|---|---|---|')
    for q, P in enumerate(plist, start=1):
        locs = '<br>'.join(f'`{span_where(src, k, P["len"])}` ({src.unit_name(src.unit[k])})' for k in P['ks'])
        where = 'all in tables' if P['tables'] == len(P['ks']) else ('caption' if P['captions'] else
                                                                     ('table + prose' if P['tables'] else 'prose'))
        note = (P['class'] + '. ' if P['class'] != 'remaining' else '') + '; '.join(sorted(P['why']))
        R.append(f"| {q} | {P['len']} | {locs} | {where} | {note} | {excerpt(src, P['ks'][0], P['len'], 30)} |")
    R.append('')
    setaside = [it for it in items if it not in remaining]
    R.append(f'**Set aside ({len(setaside)} location pairs):**')
    R.append('')
    R.append('| class | words | A | B | reason |')
    R.append('|---|---|---|---|---|')
    for it in sorted(setaside, key=lambda it: (it['class'], it['a'])):
        R.append(f"| {it['class']} | {it['len']} | `{span_where(src, it['a'], it['len'])}` | `{span_where(src, it['b'], it['len'])}` | {it['why']} |")
    R.append('')

    # 1b
    R.append('## 1b. Figure duplication')
    R.append('')
    R.append('**Shared producers and inputs** (figure-plumbing.md, '
             + (f'`{args.plumbing}`' if plumbing else 'not given')
             + '; keyed by label, so it holds for figures renumbered since it was written'
             + (f'; ROOT objects read by name from the producer scripts in `{args.repo}`' if arrays else '') + '):')
    R.append('')
    missing = [lab for labs in fig_labels.values() for lab in labs if lab not in plumbing]
    if plumbing:
        R.append(f'Labels not in figure-plumbing.md: {", ".join(missing) if missing else "none"}.')
        R.append('')
    R.append('| shared | name | Figs. |')
    R.append('|---|---|---|')
    for (kind, name), nums_ in sorted(groups.items(), key=lambda kv: (kv[0][0] != 'array', -len(kv[1]), kv[0][1])):
        if len(nums_) >= 2:
            R.append(f"| {kind} | `{name}` | {', '.join(map(str, sorted(nums_)))} |")
    R.append('')
    R.append('**Pairs.** **data**: the two figures share a producer input, and an axes of one and an axes of the other '
             'draw overlapping curves in their own frames (occupancy Jaccard ≥ 0.3 on a 40 × 40 grid; "matched" counts the '
             'axes of each figure with such a partner). **curves**: the same overlap with no shared input; generic shapes '
             f'(falling spectra, bands) reach it, so it is listed and not counted. Over all {len(fig_pairs)} pairs the best '
             f'overlap has median {statistics.median(pair_best):.2f} and 95th percentile '
             f'{pair_best[int(0.95 * (len(pair_best) - 1))]:.2f}. **text**: Jaccard ≥ 0.5 of the words and tick labels '
             'printed in the two figures. **image**: the best panel pair has thumbnail correlation ≥ 0.9 or '
             'difference-hash distance ≤ 8 of 64. **producer**: a shared producer script or input. The overlap does not '
             'see a projection redrawn on a different y scale (log against linear), so a shared array with no data signal '
             'can still be the same view.')
    R.append('')
    R.append('| Figs. | labels | signals | data: best Jaccard, axes matched | text Jaccard | image: panels (corr, hash) | shared producer | shared inputs (arrays) |')
    R.append('|---|---|---|---|---|---|---|---|')
    for p in shown_pairs:
        la = ','.join(fig_labels.get(p['a'], []))
        lb = ','.join(fig_labels.get(p['b'], []))
        na, nb = len(axes.get(p['a'], [])), len(axes.get(p['b'], []))
        pan = f"{p['a']}.{p['panels'][0]} vs {p['b']}.{p['panels'][1]} ({p['corr']:.2f}, {p['hamming']})" if p['panels'] else '—'
        arr = f" ({', '.join(p['shared_arrays'])})" if p['shared_arrays'] else ''
        R.append(f"| {p['a']}, {p['b']} | {la}; {lb} | {', '.join(p['signals'])} | {p['data_best']:.2f}, "
                 f"{p['data_match'][0]}/{na} and {p['data_match'][1]}/{nb} | {p['jaccard']:.2f} | {pan} | "
                 f"{', '.join(p['shared_producers']) or '—'} | {(', '.join(p['shared_inputs']) or '—') + arr} |")
    R.append('')

    # 1c
    R.append('## 1c. Table duplication')
    R.append('')
    R.append('Distinctive numbers: a decimal with two or more significant digits, or an integer of 100 or more that is not '
             'a year; value macros from values*.tex expanded (`\\fvval`, `\\lrval` and plain macros); captions, column '
             'specs and lengths dropped.')
    R.append('')
    R.append('A pair is listed when it shares three or more strong numbers (three or more significant digits, which '
             'rarely coincide), or three or more distinctive numbers that make up half the smaller table\'s. Two-digit '
             'decimals (0.16, 0.23) coincide by chance between tables of coefficients, so they are counted but not '
             'listed as strong.')
    R.append('')
    R.append('| Tables | labels | where | strong shared | all shared | overlap (of the smaller) | strong shared numbers |')
    R.append('|---|---|---|---|---|---|---|')
    for p in tab_pairs:
        A, B = tables[p['a']], tables[p['b']]
        nums_ = ', '.join(p['strong'][:14]) + (' …' if len(p['strong']) > 14 else '')
        if not p['strong']:
            nums_ = '(all shared) ' + ', '.join(p['shared'][:14])
        R.append(f"| {A['num']}, {B['num']} | {A['label']}; {B['label']} | `{A['where']}`; `{B['where']}` | "
                 f"{len(p['strong'])} | {len(p['shared'])} | {p['overlap']:.2f} | {nums_} |")
    R.append('')
    R.append(f"Tables read: {len(tables)}; with no distinctive number: {sum(1 for t in tables if not t['numbers'])}.")
    R.append('')

    # 2
    R.append('## 2. Figure legibility')
    R.append('')
    R.append(f'Text width: {tw:.1f} pt ({tw_how}). Sizes are rendered sizes on the page (the font size times the '
             'scale of the included graphic). "Word-like" is the smallest run of three or more characters (it leaves out '
             'most sub- and superscripts, not a subscript such as "avail"); p10 is the 10th percentile over characters. '
             '"Overlaps" counts pairs of printed strings whose boxes overlap by more than 30% of the smaller. Aspect is '
             'height / width of each panel. Scale is the factor the included PDF is drawn at; y/x is 1 unless the panel is '
             f'stretched. ⚑ marks text under {args.min_font:g} pt.')
    R.append('')
    R.append(f'| Fig. | label | page | panels | min pt | min word-like pt | p10 pt | median pt | chars < {args.min_font:g} pt | overlaps | width / textwidth (panels) | aspect h/w | scale | y/x | examples under {args.min_font:g} pt |')
    R.append('|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|')

    def f1(v):
        return '—' if v is None else f'{v:.1f}'
    for r in leg:
        flag = ' ⚑' if r['n_chars_below'] else ''
        raster = f" ({r['raster_only_panels']} raster)" if r['raster_only_panels'] else ''
        widths = '—' if r['width_frac'] is None else format(r['width_frac'], '.2f')
        if r['panels'] > 1:
            widths += ' (' + ', '.join(format(v, '.2f') for v in r['panel_width_frac']) + ')'
        R.append(f"| {r['fig']}{flag} | {', '.join(r['labels'])} | {','.join(map(str, r['pages']))} | {r['panels']}{raster} | "
                 f"{f1(r['min_pt'])} | {f1(r['min_wordlike_pt'])} | {f1(r['p10_pt'])} | {f1(r['median_pt'])} | "
                 f"{r['n_chars_below']}/{r['n_chars']} | {r['text_collisions']} | {widths} | "
                 f"{', '.join(format(v, '.2f') for v in r['aspect_h_over_w'])} | {', '.join(format(v, '.2f') for v in r['scale'])} | "
                 f"{', '.join(format(v, '.2f') for v in r['y_over_x_scale'])} | {'; '.join(r['small_examples'])} |")
    R.append('')
    if wf:
        bins = Counter()
        for v in wf:
            bins['≥ 0.95' if v >= 0.95 else '0.75–0.95' if v >= 0.75 else '0.50–0.75' if v >= 0.5 else '< 0.50'] += 1
        meds = [r['median_pt'] for r in leg if r['median_pt']]
        q = statistics.quantiles(wf, n=4) if len(wf) >= 4 else [min(wf), statistics.median(wf), max(wf)]
        R.append('**Consistency.** Printed width / text width: median '
                 f'{statistics.median(wf):.2f}, quartiles {q[0]:.2f}–{q[-1]:.2f}, range {min(wf):.2f}–{max(wf):.2f}; '
                 + ', '.join(f'{k}: {bins[k]}' for k in ('≥ 0.95', '0.75–0.95', '0.50–0.75', '< 0.50')) + '. '
                 f'Median text size across figures: range {min(meds):.1f}–{max(meds):.1f} pt, median '
                 f'{statistics.median(meds):.1f} pt; {sum(1 for m in meds if m < args.min_font)} of {len(meds)} figures '
                 f'have a median under {args.min_font:g} pt.')
        R.append('')

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text('\n'.join(R) + '\n', encoding='utf-8')
    if args.json:
        J.update({
            'text': [{'class': it['class'], 'why': it['why'], 'len': it['len'], 'a': span_where(src, it['a'], it['len']),
                      'b': span_where(src, it['b'], it['len']), 'excerpt': excerpt(src, it['a'], it['len'], 60)} for it in items],
            'figure_pairs': fig_pairs, 'tables': [{k: (dict(v) if isinstance(v, Counter) else v) for k, v in t.items()} for t in tables],
            'table_pairs': [{'a': tables[p['a']]['label'], 'b': tables[p['b']]['label'], 'shared': p['shared'],
                             'overlap': p['overlap']} for p in tab_pairs],
            'legibility': leg, 'textwidth_pt': tw,
        })
        args.json.write_text(json.dumps(J, indent=1, default=str), encoding='utf-8')
    print(f'1a remaining passages {sum(1 for P in plist if P["class"] == "remaining")} ({n_rem_pairs} pairs); set aside {len(setaside)}; 1b content pairs '
          f'{len(content_pairs)} (data {sum(1 for p in fig_pairs if "data" in p["signals"])}); 1c table pairs {len(tab_pairs)}; '
          f'2 figures {len(figs)}/{len(fig_labels)}, under {args.min_font:g} pt {len(under)}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
