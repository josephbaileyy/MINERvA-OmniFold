"""check_numbers.py -- every number in DRAFT.md's fake-data table and note widths/counts, against FD-F0-REPORT.md.
Run from this directory in a repository checkout. Exits 0 only if every value matches at the draft's printed precision.
--self-test plants a wrong chi2, a wrong p and a wrong count in a copy of the draft; each must be caught."""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[7]
REPORT = (ROOT / "docs/orchestration/state/measurement-paper/5d-community-20261024/FD-F0-REPORT.md").read_text()
DRAFT = (Path(__file__).resolve().parent / "DRAFT.md").read_text()
# draft row label -> report row label (FD-F0-REPORT sec. 5.1) and the report's matrix
MAP = {"simulation (Tune v1) prior": ("nominal (1)", "C_total"), "Tune v1, hybrid": ("A7 MnvTune (4)", "C_total"),
       "GENIE 2.12.10 CV, hybrid": ("A7 GENIE CV (4)", "C_total"),
       "GENIE + MEC, hybrid": ("A7 GENIE MEC (4)", "−GENIE+MEC"),
       "GENIE + MEC, $(E_{\\rm avail},W)$ shape": ("W2 (1)", "−GENIE+MEC"),
       "NuWro, hybrid": ("A7 NuWro (4)", "−NuWro"), "NuWro, $E_{\\rm avail}$ shape": ("W1 (1)", "−NuWro"),
       "NuWro, $(p_T,p_\\parallel,E_{\\rm avail})$ shape": ("W3 (1)", "−NuWro"),
       "NuWro, closure (noise-free)": ("closure at NuWro (3)", "−NuWro"),
       "GiBUU, $E_{\\rm avail}$ shape": ("Stage 0c GiBUU (2)", "−GiBUU"), "GiBUU, hybrid": ("A7 GiBUU (4)", "−GiBUU"),
       "synthetic $q_3$ tilt": ("q3 (1)", "C_total")}
MATRIX = {"full": "C_total", "without GENIE + MEC": "−GENIE+MEC", "without NuWro": "−NuWro", "without GiBUU": "−GiBUU"}


def report_row(label):
    for line in REPORT.splitlines():
        if line.startswith(f"| {label} |"):
            return [c.strip() for c in line.strip().strip("|").split("|")]
    raise KeyError(label)


def num(s):
    s = s.replace("$", "").replace("\\times10^{", "e").replace("}", "").replace(" ", "")
    return float(s)


def agrees(draft, rep):
    if "<10^{-30" in draft or "<1e-30" in draft:
        return "< 1e-30" in rep
    d = draft.replace("$", "")
    dv, rv = num(draft), num(rep)
    if "\\times10^" in draft:  # mantissa digits
        mant = draft.replace("$", "").split("\\times")[0]
        dec = len(mant.split(".")[1]) if "." in mant else 0
        exp = int(draft.split("10^{")[1].split("}")[0])
        return abs(dv - rv) <= 0.5 * 10 ** (exp - dec) + 1e-15
    dec = len(d.split(".")[1]) if "." in d else 0
    return abs(dv - rv) <= 0.5 * 10 ** (-dec) + 1e-12


def run(DRAFT):
    fails, n = [], 0
    for line in DRAFT.splitlines():
        m = re.match(r"^\| (\*\*)?(.+?)(\*\*)? \| (\*\*)?(\d+)(\*\*)? \| (\*\*)?(.+?)(\*\*)? \| (\*\*)?(.+?)(\*\*)? \| (\*\*)?(.+?)(\*\*)? \| (\*\*)?(.+?)(\*\*)? \|$", line)
        if not m or m.group(2) not in MAP:
            continue
        label, npe, mat, chi, p, cells = m.group(2), m.group(5), m.group(8), m.group(11), m.group(14), m.group(17)
        rl, rmat = MAP[label]
        r = report_row(rl)  # truth | group | n | matrix | grade chi2 | p | ...
        checks = [("n", npe == r[2]), ("matrix", MATRIX[mat] == rmat == r[3]), ("chi2", agrees(chi, r[4])), ("p", agrees(p, r[5])), ("cells", cells.replace(" ", "") == r[6].replace(" ", ""))]
        for what, ok in checks:
            n += 1
            if not ok:
                fails.append(f"{label}: {what} draft {[npe, mat, chi, p]} report {r[2:6]}")
    rows = sum(1 for l in DRAFT.splitlines() if re.match(r"^\| (\*\*)?[A-Za-z]", l) and any(k in l for k in MAP))
    # widths and counts quoted in sec. 3
    for phrase, rep in [("C_e: 6.45 / 4.05 / 8.47 %", "| C_e | 6.45 | 4.05 | 8.47 |"), ("C_total: 6.74 / 4.14 / 13.69 %", "| C_total | 6.74 | 4.14 | 13.69 |"),
                        ("without GiBUU 6.46 / 4.11 / 8.78 %", "| C_total without GiBUU | 6.46 | 4.11 | 8.78 |"),
                    ("without GENIE + MEC 6.74 / 4.14 / 13.69 %", "| C_total without GENIE+MEC | 6.74 | 4.14 | 13.69 |"),
                    ("without NuWro 6.74 / 4.09 /\n     13.49 %", "| C_total without NuWro | 6.74 | 4.09 | 13.49 |"),
                        ("4 of 192 cells beyond 2σ, against a Gaussian reference of 8.74", "| 12 | 4 of 192 | 8.74 | 4 of 12 | 0.12 |"),
                        ("4 of 12 truths with p < 0.01, against 0.12", "| 12 | 4 of 192 | 8.74 | 4 of 12 | 0.12 |"),
                        ("control 7, χ²_16 = 245.74", "χ²_16 = 245.74"), ("R06 for the GiBUU E_avail shape", "| R06 |"),
                        ("R02, R06 and R07 for the GiBUU prediction", "| R02, R06, R07 |")]:
        n += 1
        if phrase not in DRAFT or rep not in REPORT:
            fails.append(f"phrase/report: {phrase!r} in draft={phrase in DRAFT}, {rep!r} in report={rep in REPORT}")
    print(f"NUMBER-CHECK :: {'PASS' if not fails and rows == 12 else 'FAIL'} ({n} checks, {rows} of 12 table rows found)")
    for f in fails:
        print("  FAIL", f)
    return not fails and rows == 12



if "--self-test" in sys.argv:
    bad = [DRAFT.replace("**246.75**", "**246.85**"), DRAFT.replace("**0.0027**", "**0.0037**"),
           DRAFT.replace("| 17.37 |", "| 17.47 |"), DRAFT.replace("4 of 192 cells", "3 of 192 cells"),
           DRAFT.replace("**R02, R06, R07**", "**R02, R06**")]
    assert all(x != DRAFT for x in bad), "a planted error did not apply"
    caught = [not run(x) for x in bad]
    print(f"SELF-TEST :: {'PASS' if all(caught) else 'FAIL'} ({sum(caught)} of {len(bad)} planted errors caught)")
    sys.exit(0 if all(caught) else 1)
sys.exit(0 if run(DRAFT) else 1)
