"""Generate the remaining COV2D-G2R unfold connects from connect-g2r-D_Ub.sh (4142a188): names, LOG, bound-<job>, the
submit argument, the awk and THIS; for a G18/AR23 job, also the realization block (its own section in the package)."""
import hashlib, sys
src = open("connect-g2r-D_Ub.sh").read()
assert hashlib.sha256(src.encode()).hexdigest().startswith("4142a188")
JOBS = {"D_Uc": ("08:54:00", "8.9", None), "D_Ud": ("09:18:00", "9.3", None)}
for t, rd, rf in (("G18", "G18/b", "data_5721000.root"), ("AR23", "AR23-a2/b", "data_5731000.root")):
    for s in "abcd":
        JOBS[f"{t}_U{s}"] = ("08:54:00", "8.9", (t, rd, rf))
NOATIME = """'import hashlib, os, sys
fd = os.open(sys.argv[1], os.O_RDONLY | os.O_NOATIME); h = hashlib.sha256()
while True:
    b = os.read(fd, 1 << 20)
    if not b: break
    h.update(b)
os.close(fd); print(h.hexdigest())'"""
def rep(s, a, b, n=1):
    assert s.count(a) == n, (a, s.count(a)); return s.replace(a, b)
for job, (lim, this, real) in JOBS.items():
    s = src
    s = rep(s, """# COV2D-G2R connect D_Ub (addendum J1 §2; COV2D-G2R-BINDING-1.md addendum J1): the second unfold job, templated from
# the D_Ua connect (46005ade).""", f"""# COV2D-G2R connect {job} (addendum J1 §2; COV2D-G2R-BINDING-1.md addendum J1): an unfold job, templated from the
# D_Ub connect (4142a188).""")
    s = rep(s, "It runs beside D_Ua. On a login node it runs:", "It may run beside other cov2dg2r- jobs. On a login node it runs:")
    s = rep(s, "#     coverage-5b-audit GO on #1123) lets the LL5D bulk run beside D_Ub;", f"#     coverage-5b-audit GO on #1123) lets the LL5D bulk run beside {job};")
    s = rep(s, "D_Ub's four inputs", f"{job}'s four inputs")
    s = rep(s, "#   - then the bound g2r_submit.sh, once: D_Ub.", f"#   - then the bound g2r_submit.sh, once: {job}.")
    s = rep(s, "/dev/shm/josephrb-g2r-D_Ub.sh", f"/dev/shm/josephrb-g2r-{job}.sh")
    s = rep(s, "CAP=110.0; THIS=8.9                                # D_Ub's limit 08:54:00 (jobs_g2r.tsv), one node",
            f"CAP=110.0; THIS={this}                                # {job}'s limit {lim} (jobs_g2r.tsv), one node")
    s = rep(s, "LOG=/dev/shm/josephrb-g2r-D_Ub.log", f"LOG=/dev/shm/josephrb-g2r-{job}.log")
    s = rep(s, "bound-D_Ub.sha256", f"bound-{job}.sha256", 4)
    s = rep(s, "(stat only; not a D_Ub input)", f"(stat only; not a {job} input)")
    s = rep(s, 'g2r_submit.sh" "$C" "$M" D_Ub; rc=$?; echo "submit D_Ub rc=$rc"', f'g2r_submit.sh" "$C" "$M" {job}; rc=$?; echo "submit {job} rc=$rc"')
    s = rep(s, "id=$(awk '/ job=D_Ub / {", f"id=$(awk '/ job={job} / {{")
    if real:
        t, rd, rf = real
        s = rep(s, "#   - then the bound g2r_submit.sh, once:", f"""#   - {t}'s realization ($D/{rf}, the file every run of {job} reads with --data-file): its sha256, read through
#     O_NOATIME, equal to {t}'s step-B record at M (the file g2r_jobs.check reads, G8; here a mismatch costs no node-h),
#     and its stat (size and atime) printed;
#   - then the bound g2r_submit.sh, once:""")
        s = rep(s, "# --- the one submission\n", f"""# --- {t}'s realization against its committed step-B record (G8), O_NOATIME, and its stat
TRUTH={t}; RD=$P/cov2d-run-20261104/pseudo/{rd}; RF={rf}
SB=$C/docs/orchestration/state/measurement-paper/5d-community-20261024/fd/receipts-cov2d/pseudo/$TRUTH/pseudo_b.json
want=$(python3 -c 'import json, os, sys
r = json.load(open(sys.argv[1]))
print(" ".join(f["sha256"] for f in r["files"] if os.path.basename(f["path"]) == sys.argv[2]))' "$SB" "$RF" 2>/dev/null)
rs=$(python3 -c {NOATIME} "$RD/$RF" 2>/dev/null)
echo "realization $RD/$RF sha256=${{rs:-unread}} (O_NOATIME) step-B record $TRUTH sha256=${{want:-absent}}"
[ -n "$rs" ] && [ "$rs" = "$want" ] || stop "the realization's sha256 is not $TRUTH's step-B record's (G8)"
s=$(stat --printf '%s %X' "$RD/$RF" 2>/dev/null) || stop "$RD/$RF is missing"
echo "input $RD/$RF size=${{s% *}} atime=$(date -u -d "@${{s#* }}" +%FT%TZ)"
# --- the one submission
""")
    assert s.count("D_Ub") == 1 and "the\n# D_Ub connect (4142a188)" in s, job   # only the template reference
    open(f"connect-g2r-{job}.sh", "w").write(s)
    print(job, hashlib.sha256(s.encode()).hexdigest())
