"""Count qualification markers in one-sentence-per-line prose files (output of tex2prose.py).

Usage:
  python3 -I qcount.py table prose/*.txt            # density table (markdown)
  python3 -I qcount.py show FILE N                    # sentence N with its markers marked
  python3 -I qcount.py sample SEED K_OURS K_CORPUS prose/ours.txt prose/<corpus>...  # calibration sample

Lexicon (declared; see REPORT.md sec. 3 for the defence). Matches are taken greedily, longest first,
non-overlapping, with category priority STATUS > COND > SCOPE > HEDGE > CONCESS > NEG, so
"has not been validated" is one STATUS marker, not STATUS + NEG. APPROX is counted but is NOT a
qualifier (it attaches to numbers and is universal in the genre).
"""
import random
import re
import sys

PART = r'(?:established|validated|measured|tested|shown|demonstrated|identified|evaluated|assessed|known|' \
       r'determined|quantified|included|computed|run|studied|verified|resolved|understood|corrected|' \
       r'considered|propagated|taken into account|accounted for)'
LEX = [
    ('STATUS', r"\b(?:is|are|was|were|has|have|had|been|be|being)\s+(?:not|never)\s+(?:(?:been|yet|independently|directly|fully|explicitly)\s+)*" + PART + r"\b"),
    ('STATUS', r"\b(?:does not|do not|did not|cannot|can not|could not|may not|will not)\s+(?:by itself\s+|themselves\s+)?(?:establish|exclude|validate|determine|demonstrate|identify|rule out|guarantee|imply|prove|support|locate|provide)\b"),
    ('STATUS', r"\bun(?:measured|validated|tested|known|established|determined|quantified|corrected|explained|identified|resolved)\b"),
    ('STATUS', r"\bno (?:validated|evidence|calibrated|claim|independent|demonstrated|significance)\b"),
    ('STATUS', r"\bwe (?:claim|make|quote|assign) no\b"),
    ('STATUS', r"\bpost hoc\b"),
    ('STATUS', r"\b(?:descriptive|exploratory)\b"),
    ('COND', r"\bunder the assumptions?\b"),
    ('COND', r"\bassum(?:e|es|ed|ing|ption|ptions)\b"),
    ('COND', r"\bprovided that\b|\bprovided (?:the|it|they|its|that)\b"),
    ('COND', r"\bconditional(?:ly)?\b|\bconditioned\b"),
    ('COND', r"\bto the extent that\b|\binsofar as\b|\bin so far as\b"),
    ('COND', r"\bif\b|\bunless\b"),
    ('COND', r"\bdepend(?:s|ent|ing|ence|encies)? (?:on|upon)\b"),
    ('SCOPE', r"(?<!not )\bonly\b"),
    ('SCOPE', r"\bsolely\b|\bexclusively\b"),
    ('SCOPE', r"\bwithin\b"),
    ('SCOPE', r"\bunder (?:the|these|this|that|its|their|each|which|a|an|any)\b"),
    ('SCOPE', r"\b(?:as|the) tested\b"),
    ('SCOPE', r"\bin this (?:configuration|study|analysis|implementation|paper|work|sample|measurement|setup|case|regime|letter)\b"),
    ('SCOPE', r"\bin simulation\b|\bat nominal truth\b"),
    ('SCOPE', r"\bexcept\b|\bexcluding\b|\bapart from\b|\bother than\b"),
    ('SCOPE', r"\b(?:limited|restricted|confined) to\b"),
    ('SCOPE', r"\bas stated\b|\bin general\b"),
    ('SCOPE', r"\bspecified\b"),
    ('HEDGE', r"\bmay\b|\bmight\b|\bcould\b|\bpossibl[ey]\b|\bpotentially\b|\b(?:un)?likely\b"),
    ('HEDGE', r"\bappear(?:s|ed)?\b|\bsuggest(?:s|ed|ing)?\b|\bseems?\b|\bplausibl[ey]\b|\bpresumably\b|\bperhaps\b"),
    ('HEDGE', r"\btentative(?:ly)?\b|\bin principle\b|\bsomewhat\b|\bpart(?:ly|ially)\b|\bin part\b"),
    ('CONCESS', r"\balthough\b|\bthough\b|\bhowever\b|\bbut\b(?! also)|\bwhereas\b|\bnevertheless\b|\bnonetheless\b"),
    ('NEG', r"\bnot\b|\bno\b|\bnone\b|\bneither\b|\bnor\b|\bcannot\b|n't\b|\bwithout\b|\bnever\b"),
]
APPROX = r"\babout\b|\bapproximately\b|\broughly\b|\bnearly\b|\bof order\b|\baround\b(?= ?[0-9])"
PRIO = {'STATUS': 0, 'COND': 1, 'SCOPE': 2, 'HEDGE': 3, 'CONCESS': 4, 'NEG': 5}
CATS = ['SCOPE', 'COND', 'STATUS', 'HEDGE', 'CONCESS', 'NEG']
COMPILED = [(c, re.compile(p, re.I)) for c, p in LEX]
POINTER = re.compile(r"\b(?:Sec|Secs|Ref|Refs|Fig|Figs|Table|Tables|App|Apps|Eq|Eqs|Section|Sections|Appendix|Figure|Figures)\b\.?|\[N\]")
WORD = re.compile(r"\S*[A-Za-z0-9]\S*")


def markers(s):
    cands = []
    for c, rx in COMPILED:
        for m in rx.finditer(s):
            cands.append((m.start(), -(m.end() - m.start()), PRIO[c], m.end(), c, m.group(0)))
    cands.sort()
    taken, out = [], []
    for st, nl, pr, en, c, g in sorted(cands, key=lambda x: (x[2], x[1], x[0])):
        if any(not (en <= a or st >= b) for a, b in taken):
            continue
        taken.append((st, en))
        out.append((st, en, c, g))
    return sorted(out)


def parentheticals(s):
    out, depth, start = [], 0, None
    for i, ch in enumerate(s):
        if ch == '(':
            if depth == 0:
                start = i
            depth += 1
        elif ch == ')' and depth:
            depth -= 1
            if depth == 0:
                out.append(s[start + 1:i])
    return out


def classify_paren(p):
    if POINTER.search(p):
        stripped = POINTER.sub(' ', p)
        stripped = re.sub(r'\bN\b|MATH|EQ|[,;.:\-0-9 ]', ' ', stripped)
        if len(re.findall(r'[A-Za-z]{3,}', stripped)) <= 2:
            return 'pointer'
    if markers(p) or re.search(r'\bat most\b|\bat least\b', p, re.I):
        return 'restrictive'
    return 'other'


def stats(path):
    sents = [l.strip() for l in open(path, encoding='utf-8') if l.strip()]
    words = sum(len(WORD.findall(s)) for s in sents)
    cat = {c: 0 for c in CATS}
    n2 = n1 = nscope = 0
    approx = 0
    par = {'pointer': 0, 'restrictive': 0, 'other': 0}
    for s in sents:
        ms = markers(s)
        for _, _, c, _ in ms:
            cat[c] += 1
        q = len(ms)
        n1 += q >= 1
        n2 += q >= 2
        nscope += any(c in ('SCOPE', 'COND') for _, _, c, _ in ms)
        approx += len(re.findall(APPROX, s, re.I))
        for p in parentheticals(s):
            par[classify_paren(p)] += 1
    tot = sum(cat.values())
    k = 1000.0 / words
    return dict(words=words, sents=len(sents), msl=words / len(sents), q=tot * k, q_noneg=(tot - cat['NEG']) * k,
                cats={c: cat[c] * k for c in CATS}, ge1=n1 / len(sents), ge2=n2 / len(sents), scope=nscope / len(sents),
                approx=approx * k, par={x: par[x] * k for x in par})


def table(paths):
    hdr = ('| doc | words | sent. | mean sent. len. | Q /1k | Q excl. NEG /1k | SCOPE | COND | STATUS | HEDGE | CONCESS | NEG '
           '| sent. >=2 Q | sent. w/ scope restriction | restrictive paren. /1k | pointer paren. /1k | APPROX /1k |')
    print(hdr)
    print('|' + '|'.join(['---'] * (hdr.count('|') - 1)) + '|')
    rows = []
    for p in paths:
        r = stats(p)
        name = p.rsplit('/', 1)[-1].replace('.txt', '')
        rows.append((name, r))
        c = r['cats']
        print(f"| {name} | {r['words']} | {r['sents']} | {r['msl']:.1f} | {r['q']:.1f} | {r['q_noneg']:.1f} | "
              f"{c['SCOPE']:.1f} | {c['COND']:.1f} | {c['STATUS']:.1f} | {c['HEDGE']:.1f} | {c['CONCESS']:.1f} | {c['NEG']:.1f} | "
              f"{100 * r['ge2']:.0f}% | {100 * r['scope']:.0f}% | {r['par']['restrictive']:.1f} | {r['par']['pointer']:.1f} | {r['approx']:.1f} |")
    corp = [r for n, r in rows if n != 'ours']
    if corp:
        import statistics as st
        def med(key, sub=None):
            v = [(r[key][sub] if sub else r[key]) for r in corp]
            return st.median(v), min(v), max(v)
        print()
        print('corpus median [min, max]:')
        for key, sub, scale in [('msl', None, 1), ('q', None, 1), ('q_noneg', None, 1), ('cats', 'SCOPE', 1), ('cats', 'COND', 1),
                                ('cats', 'STATUS', 1), ('cats', 'HEDGE', 1), ('cats', 'CONCESS', 1), ('cats', 'NEG', 1),
                                ('ge2', None, 100), ('scope', None, 100), ('par', 'restrictive', 1), ('par', 'pointer', 1), ('approx', None, 1)]:
            m, lo, hi = med(key, sub)
            ours = [r for n, r in rows if n == 'ours']
            o = (ours[0][key][sub] if sub else ours[0][key]) * scale if ours else float('nan')
            print(f"  {key}{'.' + sub if sub else ''}: corpus {m * scale:.1f} [{lo * scale:.1f}, {hi * scale:.1f}]; ours {o:.1f}")


def show(path, n):
    s = [l.strip() for l in open(path, encoding='utf-8') if l.strip()][n]
    out, pos = [], 0
    for st, en, c, g in markers(s):
        out.append(s[pos:st] + '[' + g + '|' + c + ']')
        pos = en
    out.append(s[pos:])
    return ''.join(out)


if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'table':
        table(sys.argv[2:])
    elif cmd == 'show':
        print(show(sys.argv[2], int(sys.argv[3])))
    elif cmd == 'sample':
        seed, ko, kc = int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
        ours, corpus = sys.argv[5], sys.argv[6:]
        rng = random.Random(seed)
        n_ours = sum(1 for l in open(ours) if l.strip())
        picks = [(ours, i) for i in rng.sample(range(n_ours), ko)]
        pool = [(p, i) for p in corpus for i in range(sum(1 for l in open(p) if l.strip()))]
        picks += rng.sample(pool, kc)
        for j, (p, i) in enumerate(picks):
            print(f"S{j + 1:02d} {p.rsplit('/', 1)[-1]}:{i}  {show(p, i)}")
