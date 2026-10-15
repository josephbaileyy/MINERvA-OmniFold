"""Join the remote (dCache) and local (fresh full-read) adler32 values for the 450 listed MC AnaTuples.

Usage: python3 -I compare.py OUTPUTS_DIR Q2_OUTPUTS_DIR

Reads (all in OUTPUTS_DIR unless noted):
  filelist_450.txt         the population: 448 1B-1P files + 2 1A controls
  mc_stat_pre_read.tsv     local relpath, bytes, mtime, atime, ctime (dtn01, before any read)
  remote_adler.tsv         remote_adler.sh rows
  local_adler.tsv          local_adler.sh rows
  Q2_OUTPUTS_DIR/remote_ls_*.txt   the current public sizes (xrdfs ls -l, 2026-10-14)
Writes checksum_table.tsv and checksum_summary.json in OUTPUTS_DIR.

Verdicts: MATCH (both OK, equal); MISMATCH (both OK, different); ERROR (a side has no OK row,
or a local read did not reach st_size). A row is never dropped: every listed path gets a verdict.
"""
import glob
import json
import os
import sys

LOCAL_ROOT = "/pscratch/sd/j/josephrb/minerva/minerva_large_files/MC/StandardMC"
REMOTE_ROOT = ("root://fndca1.fnal.gov:1095//pnfs/fnal.gov/usr/minerva/persistent/OpenData/"
               "MediumEnergy_FHC/MC/StandardMC")


def ok_rows(path, adler_col=1):
    """Last OK row per relpath, plus the set of relpaths with any ERR row."""
    ok, err = {}, {}
    with open(path) as fh:
        for line in fh:
            if line.startswith("#") or not line.strip():
                continue
            f = line.rstrip("\n").split("\t")
            if f[2] == "OK":
                ok[f[0]] = f
            else:
                err.setdefault(f[0], []).append(f)
    return ok, err


def main(out, q2):
    rels = [ln.strip() for ln in open(os.path.join(out, "filelist_450.txt")) if ln.strip()]
    assert len(rels) == len(set(rels)) == 450, len(rels)
    stat = {}
    for ln in open(os.path.join(out, "mc_stat_pre_read.tsv")):
        f = ln.rstrip("\n").split("\t")
        stat[f[0]] = f
    rsize = {}
    for fn in glob.glob(os.path.join(q2, "remote_ls_*.txt")):
        for ln in open(fn):
            f = ln.split()
            if len(f) >= 5 and "/StandardMC/" in f[4]:
                rsize[f[4].split("/StandardMC/", 1)[1]] = int(f[3])
    rok, rerr = ok_rows(os.path.join(out, "remote_adler.tsv"))
    lok, lerr = ok_rows(os.path.join(out, "local_adler.tsv"))

    rows, counts = [], {}
    for rel in rels:
        pop = "1A-control" if rel.startswith("Playlist1A/") else "1B-1P"
        lsz = int(stat[rel][1]) if rel in stat else None
        ra = rok[rel][1] if rel in rok else None
        la, nread = None, None
        if rel in lok:
            raw = lok[rel][6].split(" ")
            la, nread = lok[rel][1], int(raw[1])
            if nread != lsz:
                la = None
        if ra is None or la is None:
            verdict = "ERROR"
        else:
            verdict = "MATCH" if ra == la else "MISMATCH"
        counts.setdefault(pop, {}).setdefault(verdict, 0)
        counts[pop][verdict] += 1
        rows.append({
            "local_path": f"{LOCAL_ROOT}/{rel}",
            "remote_url": f"{REMOTE_ROOT}/{rel}",
            "population": pop,
            "local_bytes": lsz,
            "remote_bytes": rsize.get(rel),
            "local_bytes_read": nread,
            "remote_adler32": ra or "-",
            "local_adler32": la or "-",
            "verdict": verdict,
            "remote_err_rows": len(rerr.get(rel, [])),
            "local_err_rows": len(lerr.get(rel, [])),
        })

    cols = list(rows[0])
    with open(os.path.join(out, "checksum_table.tsv"), "w") as fh:
        fh.write("\t".join(cols) + "\n")
        for r in rows:
            fh.write("\t".join("-" if r[c] is None else str(r[c]) for c in cols) + "\n")
    pop = [r for r in rows if r["population"] == "1B-1P"]
    summary = {
        "population_1B_1P_files": len(pop),
        "population_1B_1P_bytes_local": sum(r["local_bytes"] for r in pop),
        "population_1B_1P_bytes_read": sum(r["local_bytes_read"] or 0 for r in pop),
        "size_equal_local_vs_remote_1B_1P": sum(r["local_bytes"] == r["remote_bytes"] for r in pop),
        "counts": counts,
        "not_match": [r for r in rows if r["verdict"] != "MATCH"],
        "remote_rows_err_total": sum(len(v) for v in rerr.values()),
        "local_rows_err_total": sum(len(v) for v in lerr.values()),
        "inputs": {k: os.path.abspath(os.path.join(out, k)) for k in
                   ("filelist_450.txt", "mc_stat_pre_read.tsv", "remote_adler.tsv", "local_adler.tsv")},
        "q2_remote_ls": sorted(os.path.abspath(p) for p in glob.glob(os.path.join(q2, "remote_ls_*.txt"))),
        "table": os.path.abspath(os.path.join(out, "checksum_table.tsv")),
    }
    with open(os.path.join(out, "checksum_summary.json"), "w") as fh:
        json.dump(summary, fh, indent=1)
    print(json.dumps({k: summary[k] for k in summary if k not in ("not_match", "inputs", "q2_remote_ls")},
                     indent=1))
    for r in summary["not_match"]:
        print("NOT-MATCH", r["population"], r["verdict"], r["local_path"], r["remote_adler32"], r["local_adler32"])


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
