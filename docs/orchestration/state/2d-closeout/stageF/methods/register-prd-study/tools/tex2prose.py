"""Convert a LaTeX paper to body prose, one sentence per line.

Usage: python3 -I tex2prose.py MAIN.tex OUT.txt [--keep-floats]

The same rules apply to every paper (ours and the corpus), so the counts are comparable:
  * \\input/\\include are expanded (files under MAIN's directory only);
  * comments, comment environments and \\iffalse blocks are removed;
  * the region kept runs from the abstract to the first of: acknowledgments, \\appendix,
    bibliography, supplementary-material part, \\end{document}; appendices and supplements
    are therefore NOT body prose;
  * floats (figure, table, their starred forms, tabular) are removed, captions with them;
  * display math becomes one token 'EQ', inline math one token 'MATH';
  * \\cite -> '[N]', \\ref-like -> 'N', section headings removed, footnote text kept in place
    inside parentheses;
  * formatting commands keep their argument; any other bare macro becomes 'MAC' (one word:
    in our paper these are mostly value macros, i.e. numbers);
  * sentences are split at [.?!] + space + capital/digit/bracket, with a protected list of
    abbreviations (Ref., Fig., Sec., Eq., Tab., App., e.g., i.e., et al., vs., cf., No.).
"""
import os
import re
import sys

KEEP_ARG = ['emph', 'textit', 'textbf', 'textrm', 'textsf', 'textsc', 'textsl', 'texttt', 'text',
            'mbox', 'hbox', 'underline', 'uline', 'mathrm', 'mathit', 'mathbf', 'boldsymbol',
            'textnormal', 'textup', 'ensuremath', 'enquote', 'mathcal', 'mathsf', 'textmd', 'it', 'bf',
            'omnifold', 'protect', 'xspace']
DROP_ARG = ['label', 'vspace', 'hspace', 'vskip', 'hskip', 'graphicspath', 'bibliographystyle',
            'setlength', 'addcontentsline', 'pagestyle', 'thispagestyle', 'newcommand', 'renewcommand',
            'linenumbers', 'nolinenumbers', 'phantomsection', 'pubhold']
SECTION = ['section', 'subsection', 'subsubsection', 'paragraph', 'subparagraph', 'part', 'chapter']
CITE = ['cite', 'citep', 'citet', 'Cite', 'onlinecite', 'citealp', 'citeauthor', 'autocite', 'parencite',
        'textcite', 'supercite']
REF = ['ref', 'eqref', 'autoref', 'cref', 'Cref', 'pageref', 'Ref', 'Fig', 'Eq', 'Sec', 'Tab']
FLOATS = ['figure', 'figure*', 'table', 'table*', 'tabular', 'tabular*', 'wrapfigure', 'sidewaystable',
          'longtable', 'subfigure', 'tabularx', 'threeparttable']
DISPLAY = ['equation', 'equation*', 'align', 'align*', 'eqnarray', 'eqnarray*', 'gather', 'gather*',
           'multline', 'multline*', 'displaymath', 'flalign', 'flalign*', 'alignat', 'alignat*', 'split',
           'subequations', 'math']
DROPENV = ['comment', 'thebibliography', 'verbatim', 'lstlisting', 'tikzpicture']
ABBREV = ['Ref.', 'Refs.', 'Fig.', 'Figs.', 'Sec.', 'Secs.', 'Eq.', 'Eqs.', 'Tab.', 'App.', 'Apps.', 'e.g.',
          'i.e.', 'et al.', 'vs.', 'cf.', 'No.', 'Nos.', 'approx.', 'resp.', 'Ch.', 'Sect.', 'Tabs.', 'viz.',
          'Phys.', 'Rev.', 'Lett.', 'Nucl.', 'Instrum.', 'Meth.', 'Eur.', 'Inst.', 'Dept.', 'Prof.', 'Dr.',
          'ca.', 'incl.', 'excl.', 'stat.', 'syst.', 'thr.', 'Conf.']


def read_expanded(path, root, depth=0):
    text = open(path, encoding='utf-8', errors='replace').read()
    text = strip_comments(text)
    text = re.sub(r'(?m)^\s*\\(re)?newcommand.*$', ' ', text)
    text = re.sub(r'(?m)^\s*\\def\\.*$', ' ', text)

    def repl(m):
        name = m.group(2).strip()
        cand = os.path.join(root, name)
        for c in (cand, cand + '.tex'):
            if os.path.isfile(c) and depth < 6 and not c.endswith('.bbl'):
                return read_expanded(c, root, depth + 1)
        return ' '
    return re.sub(r'\\(input|include)\s*\{([^}]*)\}', repl, text)


def strip_comments(text):
    text = re.sub(r'(?<!\\)%[^\n]*', '', text)
    text = re.sub(r'\\iffalse.*?\\fi\b', ' ', text, flags=re.S)
    return text


def find_group(s, i):
    """s[i] == '{'; return index just past the matching '}'."""
    depth = 0
    for j in range(i, len(s)):
        c = s[j]
        if c == '\\':
            continue
        if c == '{' and (j == 0 or s[j - 1] != '\\'):
            depth += 1
        elif c == '}' and (j == 0 or s[j - 1] != '\\'):
            depth -= 1
            if depth == 0:
                return j + 1
    return len(s)


def drop_env(s, names, token=' '):
    for n in names:
        pat = re.compile(r'\\begin\{' + re.escape(n) + r'\}.*?\\end\{' + re.escape(n) + r'\}', re.S)
        s = pat.sub(token, s)
    return s


def region(s):
    starts = [m.start() for m in re.finditer(r'\\begin\{abstract\}|\\abstract\s*\{|\\AtlasAbstract\s*\{', s)]
    start = starts[0] if starts else 0
    ends = [m.start() for m in re.finditer(
        r'\\begin\{acknowledge?ments?\}|\\section\*?\{\s*Acknowledge?ments?|\\acknowledge?ments?\b|\\appendix\b|'
        r'\\bibliography\{|\\printbibliography|\\begin\{thebibliography\}|\\part\*?\{Supplement|\\end\{document\}',
        s) if m.start() > start]
    end = min(ends) if ends else len(s)
    body = s[start:end]
    # ATLAS-style: the abstract macro sits in the preamble; drop preamble-only matter between it and \begin{document}
    if '\\begin{document}' in body:
        a_end = find_group(body, body.index('{'))
        abstract = body[:a_end]
        rest = body[body.index('\\begin{document}'):]
        body = abstract + '\n\n' + rest
    return body


def replace_cmd_args(s, names, fn, nargs=1):
    pat = re.compile(r'\\(' + '|'.join(re.escape(n) for n in names) + r')\*?(\s*\[[^\]]*\])*\s*(?=\{)')
    out, pos = [], 0
    while True:
        m = pat.search(s, pos)
        if not m:
            out.append(s[pos:])
            break
        out.append(s[pos:m.start()])
        j = m.end()
        args = []
        for _ in range(nargs):
            while j < len(s) and s[j] in ' \n':
                j += 1
            if j < len(s) and s[j] == '{':
                k = find_group(s, j)
                args.append(s[j + 1:k - 1])
                j = k
        out.append(fn(m.group(1), args))
        pos = j
    return ''.join(out)


def convert(s, full=False):
    s = drop_env(s, DROPENV)
    if full:
        s = drop_env(s, ['tabular', 'tabular*', 'tabularx', 'longtable'], ' ')
        s = replace_cmd_args(s, ['caption'], lambda n, a: '\n\n' + (a[0] if a else '') + '\n\n')
    else:
        s = drop_env(s, FLOATS, ' ')
    s = drop_env(s, DISPLAY, ' EQ ')
    s = re.sub(r'\\\[.*?\\\]', ' EQ ', s, flags=re.S)
    s = re.sub(r'\$\$.*?\$\$', ' EQ ', s, flags=re.S)
    s = re.sub(r'(?<!\\)\$.*?(?<!\\)\$', ' MATH ', s, flags=re.S)
    s = re.sub(r'\\\(.*?\\\)', ' MATH ', s, flags=re.S)
    # our paper's pointer macros
    s = replace_cmd_args(s, ['nsec'], lambda n, a: 'Ref. [N], Sec. N')
    s = replace_cmd_args(s, ['napp'], lambda n, a: 'Ref. [N], App. N')
    s = replace_cmd_args(s, ['SI'], lambda n, a: (a[0] + ('%' if 'percent' in a[1] else ' ' + re.sub(r'\\', '', a[1])))
                         if len(a) == 2 else ' '.join(a), nargs=2)
    s = replace_cmd_args(s, ['SIrange'], lambda n, a: (a[0] + ' to ' + a[1] + ('%' if 'percent' in a[2] else ' unit'))
                         if len(a) == 3 else ' ', nargs=3)
    s = replace_cmd_args(s, ['num', 'si'], lambda n, a: a[0] if a else '')
    s = replace_cmd_args(s, CITE, lambda n, a: '[N]')
    s = replace_cmd_args(s, REF, lambda n, a: 'N')
    s = re.sub(r'\\ref\*', r'\\ref', s)
    s = replace_cmd_args(s, REF, lambda n, a: 'N')
    s = replace_cmd_args(s, SECTION, lambda n, a: '\n\n')
    s = replace_cmd_args(s, ['footnote'], lambda n, a: ' (' + (a[0] if a else '') + ') ')
    s = replace_cmd_args(s, ['textcolor', 'href', 'colorbox'], lambda n, a: a[1] if len(a) == 2 else '', nargs=2)
    s = replace_cmd_args(s, ['url'], lambda n, a: 'URL')
    s = replace_cmd_args(s, DROP_ARG, lambda n, a: ' ')
    for _ in range(3):
        s = replace_cmd_args(s, KEEP_ARG, lambda n, a: a[0] if a else '')
    s = re.sub(r'\\(begin|end)\{[^}]*\}', '\n', s)
    s = re.sub(r'\\item\b(\[[^\]]*\])?', '\n', s)
    s = re.sub(r'\\(abstract|AtlasAbstract)\b', ' ', s)
    s = s.replace('~', ' ').replace('\\,', ' ').replace('\\;', ' ').replace('\\ ', ' ').replace('\\\\', '\n')
    s = s.replace('\\%', '%').replace('\\&', '&').replace('\\_', '_').replace('\\#', '#')
    s = s.replace('``', '"').replace("''", '"').replace('---', ' -- ').replace('\\-', '')
    s = re.sub(r"\\['`^\"~=.][{]?([A-Za-z])[}]?", r'\1', s)  # accents
    drop = r'noindent|centering|small|footnotesize|scriptsize|large|Large|normalsize|medskip|bigskip|smallskip|' \
           r'clearpage|newpage|maketitle|raggedbottom|par|indent|hfill|vfill|break|linebreak|newline|it|bf|rm|sc|' \
           r'em|sl|tt|relax|null|xspace|protect|onecolumngrid|twocolumngrid|selectfont|bibliographystyle|' \
           r'frenchspacing|sloppy|nopagebreak|pagebreak|leavevmode|unskip|ignorespaces|tableofcontents|' \
           r'checkoddpage|FloatBarrier|allowbreak|nobreak|quad|qquad|left|right'
    s = re.sub(r'\\(' + drop + r')\b\*?', ' ', s)
    s = re.sub(r'\\[A-Za-z]+\*?', ' MAC ', s)
    s = re.sub(r'[{}]', '', s)
    s = re.sub(r'\[[0-9a-z]+\]\s*(?=\n)', ' ', s)  # leftover optional args at line ends
    s = re.sub(r'(MAC\s+)+', 'MAC ', s)
    return s


def sentences(text):
    paras = re.split(r'\n\s*\n', text)
    out = []
    for p in paras:
        p = re.sub(r'\s+', ' ', p).strip()
        if len(re.findall(r'[A-Za-z]{2,}', p)) < 3:
            continue
        q = p
        for i, a in enumerate(ABBREV):
            q = re.sub(r'(?<![A-Za-z])' + re.escape(a), a.replace('.', '<DOT>'), q)
        q = re.sub(r'\b([A-MO-Z])\.(?= [A-Z][a-z])', r'\1<DOT>', q)  # initials (not N: N is a reference number)
        parts = re.split(r'(?<=[.?!])\s+(?=[A-Z0-9\[("])', q)
        for s in parts:
            s = s.replace('<DOT>', '.').strip()
            if len(re.findall(r'[A-Za-z]{2,}', s)) >= 3:
                out.append(s)
    return out


def main():
    src, dst = sys.argv[1], sys.argv[2]
    full = '--full' in sys.argv
    root = os.path.dirname(os.path.abspath(src))
    s = read_expanded(src, root)
    if full:
        st = [m.start() for m in re.finditer(r'\\begin\{abstract\}|\\abstract\s*\{|\\AtlasAbstract\s*\{', s)]
        body = s[st[0] if st else 0:]
    else:
        body = region(s)
    prose = convert(body, full)
    sents = sentences(prose)
    with open(dst, 'w', encoding='utf-8') as f:
        f.write('\n'.join(sents) + '\n')
    words = sum(len(re.findall(r'\S*[A-Za-z0-9]\S*', x)) for x in sents)
    print(f'{src}: {len(sents)} sentences, {words} words -> {dst}')


if __name__ == '__main__':
    main()
