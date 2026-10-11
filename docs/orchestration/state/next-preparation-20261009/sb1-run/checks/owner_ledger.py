#!/usr/bin/env python3
"""Owner's recomputation of SB1 charge, queue time and the S2-S4 ratios from the FRESH sacct.

    python3 owner_ledger.py ../evidence/scheduler/sacct-final.psv

Independent of ``sb1_verify.py``: it reads the post-run ``sacct-final.psv`` (taken after H1 ended),
not H1's in-job ``sacct.psv``, which was written while H1 itself was still running. Charge is
billing / 256 x ElapsedRaw (a regular node bills 256). Queue time is measured from each job's
Eligible time (its dependency release), separately from its charged elapsed time.
"""

import datetime
import sys

GB = 1e9
KIB = 1024


def rows(path):
    lines = [x for x in open(path).read().splitlines() if x and not x.startswith("#")]
    head = lines[0].split("|")
    return [dict(zip(head, x.split("|"))) for x in lines[1:]]


def t(text):
    return datetime.datetime.strptime(text, "%Y-%m-%dT%H:%M:%S")


def kib(text):
    return float(text.rstrip("K")) * KIB


def main(path):
    rs = rows(path)
    alloc = [r for r in rs if "." not in r["JobID"]]
    batch = {r["JobID"].split(".")[0]: r for r in rs if r["JobID"].endswith(".batch")}
    total_nh = total_q = total_e = 0
    print(f"{'job':6} {'id':9} {'state':10} {'bill':>4} {'elapsed_s':>9} {'node_h':>9} "
          f"{'queue_s':>8} {'maxrss_GB':>9} {'diskread_GB':>11}")
    m = {}
    for r in alloc:
        tres = dict(kv.split("=", 1) for kv in r["AllocTRES"].split(","))
        bill, el = int(tres["billing"]), int(r["ElapsedRaw"])
        nh = bill / 256 * el / 3600
        q = int((t(r["Start"]) - t(r["Eligible"])).total_seconds())
        b = batch[r["JobID"]]
        rss, dr = kib(b["MaxRSS"]) / GB, kib(b["MaxDiskRead"]) / GB
        name = r["JobName"].replace("sb1_", "")
        m[name] = dict(el=el, rss=rss, dr=dr)
        total_nh += nh
        total_q += q
        total_e += el
        print(f"{name:6} {r['JobID']:9} {r['State']:10} {bill:4d} {el:9d} {nh:9.6f} {q:8d} "
              f"{rss:9.3f} {dr:11.3f}")
    first = min(t(r["Submit"]) for r in alloc)
    last = max(t(r["End"]) for r in alloc)
    print(f"charged total {total_nh:.6f} node-h (cap 2.0; headroom {2.0 - total_nh:.6f})")
    print(f"charged elapsed {total_e} s; queue after eligibility {total_q} s; "
          f"first submit -> last end {int((last - first).total_seconds())} s")
    ul, sl = m["UL"], m["SL"]
    print(f"S2 disk  SL {sl['dr']:.4f} GB <= 10 and <= 0.1 x UL {ul['dr']:.4f}: ratio "
          f"{sl['dr'] / ul['dr']:.5f} -> {'PASS' if sl['dr'] <= 10 and sl['dr'] <= 0.1 * ul['dr'] else 'FAIL'}")
    print(f"S3 rss   SL {sl['rss']:.4f} GB <= 30 and <= 0.5 x UL {ul['rss']:.4f}: ratio "
          f"{sl['rss'] / ul['rss']:.5f} -> {'PASS' if sl['rss'] <= 30 and sl['rss'] <= 0.5 * ul['rss'] else 'FAIL'}")
    print(f"S4 time  SL {sl['el']} s <= 0.5 x UL {ul['el']} s: ratio {sl['el'] / ul['el']:.5f} -> "
          f"{'PASS' if sl['el'] <= 0.5 * ul['el'] else 'FAIL'}")


if __name__ == "__main__":
    main(sys.argv[1])
