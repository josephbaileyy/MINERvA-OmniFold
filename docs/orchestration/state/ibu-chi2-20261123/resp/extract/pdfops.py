"""Minimal PDF content-stream reader for this paper (no third-party deps).

Extracts, per page, every filled rectangle (with the exact fill operands as
written in the PDF), every stroked line segment, and every text show with its
device-space origin.  Coordinates are PDF user space in points, y up.
"""
import re
import zlib

NUM = re.compile(rb'[+-]?(?:\d+\.?\d*|\.\d+)')


def load_objects(path):
    data = open(path, 'rb').read()
    objs = {}
    for m in re.finditer(rb'(?<![0-9])(\d+) 0 obj(.*?)endobj', data, re.S):
        objs[int(m.group(1))] = m.group(2)
    return data, objs


def stream_of(objs, n):
    b = objs[n]
    hdr = b[:b.find(b'stream')]
    s = b[b.find(b'stream') + 6:].lstrip(b'\r\n')
    s = s[:s.rfind(b'endstream')]
    if b'FlateDecode' in hdr:
        s = zlib.decompressobj().decompress(s)
    return s


def page_content(path, pageno):
    """pageno is 1-based."""
    data, objs = load_objects(path)
    kids = re.search(rb'/Type\s*/Pages\s*/Kids\s*\[(.*?)\]', data, re.S).group(1)
    pages = [int(x) for x in re.findall(rb'(\d+) 0 R', kids)]
    pobj = objs[pages[pageno - 1]]
    c = re.search(rb'/Contents\s*(\d+) 0 R', pobj)
    return stream_of(objs, int(c.group(1)))


def tokenize(s):
    i, n = 0, len(s)
    while i < n:
        ch = s[i:i + 1]
        if ch in b' \t\r\n\f\x00':
            i += 1
        elif ch == b'%':
            j = s.find(b'\n', i)
            i = n if j < 0 else j
        elif ch == b'(':
            depth, j, out = 1, i + 1, bytearray()
            while depth:
                c = s[j:j + 1]
                if c == b'\\':
                    out += s[j:j + 2]
                    j += 2
                    continue
                if c == b'(':
                    depth += 1
                elif c == b')':
                    depth -= 1
                    if depth == 0:
                        break
                out += c
                j += 1
            yield ('str', bytes(out))
            i = j + 1
        elif ch == b'[':
            yield ('[', None)
            i += 1
        elif ch == b']':
            yield (']', None)
            i += 1
        elif ch == b'/':
            m = re.match(rb'/[^\s/\[\]()<>]*', s[i:i + 128])
            yield ('name', m.group(0))
            i += len(m.group(0))
        elif ch == b'<' and s[i:i + 2] != b'<<':
            j = s.find(b'>', i)
            yield ('hex', s[i + 1:j])
            i = j + 1
        elif ch in b'<>':
            yield ('dict', s[i:i + 2])
            i += 2
        else:
            m = NUM.match(s, i)
            if m and m.end() > i:
                yield ('num', m.group(0))
                i = m.end()
            else:
                m = re.match(rb'[^\s/\[\]()<>%]+', s[i:i + 64])
                yield ('op', m.group(0))
                i += len(m.group(0))


def mul(a, b):
    """Matrix product a*b for PDF 6-tuples (row-vector convention)."""
    return (a[0] * b[0] + a[1] * b[2], a[0] * b[1] + a[1] * b[3],
            a[2] * b[0] + a[3] * b[2], a[2] * b[1] + a[3] * b[3],
            a[4] * b[0] + a[5] * b[2] + b[4], a[4] * b[1] + a[5] * b[3] + b[5])


def apply(m, x, y):
    return (m[0] * x + m[2] * y + m[4], m[1] * x + m[3] * y + m[5])


def unescape(b):
    out, i = bytearray(), 0
    while i < len(b):
        if b[i:i + 1] == b'\\' and i + 1 < len(b):
            out += b[i + 1:i + 2]
            i += 2
        else:
            out += b[i:i + 1]
            i += 1
    return out.decode('latin-1')


def interpret(s):
    ctm = (1, 0, 0, 1, 0, 0)
    stack = []
    fill = ('g', (b'0',))
    stroke = ('G', (b'0',))
    operands = []
    path = []          # list of subpaths; each a list of points (device space)
    rects = []         # (x0, y0, x1, y1, fillop, op_index)
    lines = []         # stroked polylines (device space)
    texts = []         # (x, y, string, fontsize)
    tm = tlm = (1, 0, 0, 1, 0, 0)
    tl = 0.0
    fsize = 0.0
    arr = None
    opi = 0
    path_is_rect = []
    for kind, val in tokenize(s):
        if kind == '[':
            arr = []
            continue
        if kind == ']':
            operands.append(('arr', arr))
            arr = None
            continue
        if arr is not None:
            arr.append((kind, val))
            continue
        if kind != 'op':
            operands.append((kind, val))
            continue
        op = val
        opi += 1
        nums = [float(v) for k, v in operands if k == 'num']
        raw = tuple(v for k, v in operands if k == 'num')
        if op == b'q':
            stack.append((ctm, fill, stroke))
        elif op == b'Q':
            ctm, fill, stroke = stack.pop()
        elif op == b'cm':
            ctm = mul(tuple(nums), ctm)
        elif op in (b'rg', b'g', b'k'):
            fill = (op.decode(), raw)
        elif op in (b'RG', b'G', b'K'):
            stroke = (op.decode(), raw)
        elif op == b're':
            x, y, w, h = nums
            pts = [apply(ctm, x, y), apply(ctm, x + w, y),
                   apply(ctm, x + w, y + h), apply(ctm, x, y + h)]
            path.append(pts)
            path_is_rect.append(True)
        elif op == b'm':
            path.append([apply(ctm, *nums)])
            path_is_rect.append(False)
        elif op == b'l':
            path[-1].append(apply(ctm, *nums))
        elif op == b'c':
            path[-1].append(apply(ctm, nums[4], nums[5]))
            path_is_rect[-1] = False
        elif op == b'h':
            pass
        elif op in (b'f', b'f*', b'F', b'B', b'B*', b'S', b's', b'n', b'b', b'b*'):
            if op in (b'f', b'f*', b'F', b'B', b'B*', b'b', b'b*'):
                for sp, isr in zip(path, path_is_rect):
                    xs = [p[0] for p in sp]
                    ys = [p[1] for p in sp]
                    if isr:
                        rects.append((min(xs), min(ys), max(xs), max(ys), fill, opi))
            if op in (b'S', b's', b'B', b'B*', b'b', b'b*'):
                for sp in path:
                    lines.append((sp, stroke))
            path, path_is_rect = [], []
        elif op == b'BT':
            tm = tlm = (1, 0, 0, 1, 0, 0)
        elif op == b'Tf':
            fsize = nums[-1]
        elif op == b'Tm':
            tm = tlm = tuple(nums)
        elif op in (b'Td', b'TD'):
            tlm = mul((1, 0, 0, 1, nums[0], nums[1]), tlm)
            tm = tlm
            if op == b'TD':
                tl = -nums[1]
        elif op == b'TL':
            tl = nums[0]
        elif op == b'T*':
            tlm = mul((1, 0, 0, 1, 0, -tl), tlm)
            tm = tlm
        elif op in (b'Tj', b'TJ', b"'"):
            if op == b"'":
                tlm = mul((1, 0, 0, 1, 0, -tl), tlm)
                tm = tlm
            parts = []
            for k, v in operands:
                if k == 'str':
                    parts.append(unescape(v))
                elif k == 'arr':
                    for k2, v2 in v:
                        if k2 == 'str':
                            parts.append(unescape(v2))
                        elif k2 == 'num' and float(v2) < -800:
                            parts.append(' | ')
            m = mul(tm, ctm)
            x, y = apply(m, 0, 0)
            texts.append((x, y, ''.join(parts), fsize * abs(m[3]) if m[3] else fsize))
        operands = []
    return rects, lines, texts
