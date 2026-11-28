1. Event accounting and conservation — no defect.
2. Baseline reproduction and POT/exposure scaling — no defect.
3. Figure 5 comparison — no defect.
4. Consistency of `chi2/205` and `column ratio` across rows — no defect.
5. **The all-in-grid replay lets two truth bins with zero generated events absorb reconstructed yield.** `compare.py:25–26` and `compare.py:127` normalize the response by selected migration counts, so the two columns enter all ten iterations. `compare.py:129` then zeros their efficiency-corrected yields. The receipt’s `inputs/replay/replay.py:41–46` uses the generated denominator and zeros those response columns before iterating. The late zeroing changes the yields in other bins and affects both `all_in_grid_true_muons` rows.

   | Numerator | Printed → receipt-normalized `chi2/205` | Printed → receipt-normalized column ratio |
   |---|---:|---:|
   | `in_grid` | 0.34931797 → 0.34925865 | 1.09367494 → 1.09367341 |
   | `anywhere` | 0.37269833 → 0.37259493 | 1.02573160 → 1.02573016 |