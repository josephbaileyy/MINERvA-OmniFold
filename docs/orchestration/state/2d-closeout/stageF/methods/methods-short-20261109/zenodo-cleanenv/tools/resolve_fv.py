"""Resolve #977's \\fvgroup/\\fvcase variants and \\fvval keys, for reading claims (D6 clean-env claim map).

usage: python3 -I resolve_fv.py <values_fived16.tex> <tex file> [--abstract]
Prints the text with comments stripped, each \\fvgroup reduced to its selected \\fvcase (fvc@key), and each
\\fvval{key} written as [[key=value]]. Read-only; prints to stdout.
"""
import re
import sys


def braced(s, i):
    """s[i] == '{': return (content, index after the closing brace)."""
    assert s[i] == "{", (i, s[i:i + 20])
    depth, j = 0, i
    while j < len(s):
        c = s[j]
        if c == "\\":
            j += 2
            continue
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return s[i + 1:j], j + 1
        j += 1
    raise ValueError("unbalanced")


def load(vpath):
    v = open(vpath).read()
    case, val = {}, {}
    for m in re.finditer(r"\\@namedef\{fvc@([^}]*)\}\{([^}]*)\}", v):
        case[m[1]] = m[2]
    i = 0
    for m in re.finditer(r"\\@namedef\{fv@([^}]*)\}", v):
        try:
            val[m[1]], _ = braced(v, m.end())
        except Exception:
            pass
    return case, val


def resolve(s, case, val):
    out, i = [], 0
    while i < len(s):
        if s.startswith(r"\fvgroup{", i):
            _, j = braced(s, i + 8)
            body, k = braced(s, j)
            out.append(resolve(body, case, val))
            i = k
        elif s.startswith(r"\fvcase{", i):
            key, j = braced(s, i + 7)
            c, j = braced(s, j)
            text, k = braced(s, j)
            if case.get(key) == c:
                out.append(resolve(text, case, val))
            i = k
        elif s.startswith(r"\fvval{", i):
            key, k = braced(s, i + 6)
            out.append(f"[[{key}={val.get(key, '?')}]]")
            i = k
        else:
            out.append(s[i])
            i += 1
    return "".join(out)


def main():
    case, val = load(sys.argv[1])
    s = open(sys.argv[2]).read()
    if "--abstract" in sys.argv:
        s = s[s.index(r"\begin{abstract}"):s.index(r"\end{abstract}")]
    s = re.sub(r"(?m)(?<!\\)%.*$", "", s)
    s = re.sub(r"\n\s*\n+", "\n\n", s)
    print(resolve(s, case, val).strip())


if __name__ == "__main__":
    main()
