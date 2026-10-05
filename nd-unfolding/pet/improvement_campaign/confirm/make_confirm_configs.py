"""Write the frozen, hashed RunConfigs of V1's infrastructure runs (`configs/`) and print hashes.

Both derive from B2's H recipe at K = 10 (`phase_b/pet/configs/b2e3-H-K10-s1.json`: the historical
as-executed `ours` recipe, seed 1) and change ONLY the iteration count and the name. Every seed of a
fit depends on (step seed, step, iteration) alone (`run_unfold.derive_seed`, B2's `seed_step`), so
iterations 0..K-1 of these runs are the same computation as those of the K = 10 run:

* `v1ctl-H-K3-s1` -- positive control 5(a): the historical halves forced in, K = 3; its pushes
  must be bit-identical to `b2e3-H-K10-s1`'s iterations 0-2 and its scores equal B2's.
* `v1mech-H-K2-s1` -- item 6: one pool-S replicate, K = 2, for wall time and the receipt.

The candidate configs of PILOT/FINAL are frozen by the orchestrator (protocol Amendment 2), not here.
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from recipe import RunConfig  # noqa: E402

SOURCE = HERE.parent / "phase_b" / "pet" / "configs" / "b2e3-H-K10-s1.json"
RUNS = {"v1ctl-H-K3-s1": (3, "V1 positive control: B2 H seed 1 (b2e3-H-K10-s1) at K=3 on the "
                             "historical halves through the replicate path"),
        "v1mech-H-K2-s1": (2, "V1 mechanics: B2 H seed 1 at K=2 on one pool-S replicate")}


def main() -> None:
    base = RunConfig.from_json(SOURCE.read_text())
    for name, (k, note) in RUNS.items():
        config = base.replace(name=name, iterations=k, note=note)
        config.validate()
        (HERE / "configs" / f"{name}.json").write_text(config.to_json(indent=1) + "\n")
        print(name, config.content_hash())


if __name__ == "__main__":
    main()
