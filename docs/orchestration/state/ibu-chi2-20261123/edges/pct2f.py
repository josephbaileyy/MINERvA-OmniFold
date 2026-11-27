# The release's bin_mapping.txt prints pT edges with two decimals. This shows what %.2f prints for each candidate edge.
for x in (0.07, 0.075, 0.33, 0.325, 0.47, 0.475):
    print(f"{x!r:>6}  stored as {x:.20f}  %.2f -> {x:.2f}")
