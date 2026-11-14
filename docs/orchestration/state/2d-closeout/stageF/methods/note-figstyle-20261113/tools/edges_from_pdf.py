"""Recover Fig. 1's bin edges from the committed PDF (note figure style, group C, family 1; director 2026-11-14).

usage: python3 edges_from_pdf.py docs/analysis-note/figures/control_plots.pdf     (needs PyMuPDF)
Each panel's stack outline (the #2F4B7C path) gives its bin edges as the x of its vertices, in page points. They are
mapped to data units by a linear fit to that panel's x tick labels (the row of numbers under its ratio panel, the
compressed "100" excluded). Printed to 0.001; the recovered values sit within 0.001 of round numbers, which is the
tolerance taken (the PDF stores coordinates to about 0.01 pt, about 0.0003 data units on the widest axis).
The PDF read: sha256 1191cc0cdf89358c4ed0bd51ae137e330779c549e2657ec3045f9da7cb9a43c6, as committed at 1b2925259 (2026-07-09) and unchanged since.
"""
import sys, warnings, pymupdf as fitz, numpy as np
warnings.filterwarnings("ignore")
pg=fitz.open(sys.argv[1])[0]
outl=[p for p in pg.get_drawings() if p.get("color") and tuple(round(c,3) for c in p["color"])==(0.184,0.294,0.486)]
words=pg.get_text("words")
for p in sorted(outl,key=lambda q:(round(q["rect"].y0,-1),q["rect"].x0)):
    r=p["rect"]; xs=[]
    for it in p["items"]:
        if it[0]=="l": xs+=[it[1].x,it[2].x]
        elif it[0]=="re": xs+=[it[1].x0,it[1].x1]
        elif it[0]=="c": xs+=[it[1].x,it[4].x]
    xs=sorted(set(round(x,3) for x in xs))
    nums=[]
    for w in words:
        cx=(w[0]+w[2])/2
        if r.x0-10<=cx<=r.x1+15 and w[1]>r.y1 and w[1]<r.y1+260:
            try: nums.append((cx,float(w[4]),round(w[1])))
            except ValueError: pass
    from collections import Counter
    rowy=Counter(y for _,_,y in nums).most_common(1)[0][0]
    ticks=sorted((x,v) for x,v,y in nums if y==rowy)
    lin=[(x,v) for x,v in ticks if v<99]
    a,b=np.polyfit([x for x,_ in lin],[v for _,v in lin],1)
    print("panel",round(r.x0),round(r.y0),"ticks",[v for _,v in ticks],"n_vertices",len(xs))
    print("   edges:",[round(a*x+b,3) for x in xs])
