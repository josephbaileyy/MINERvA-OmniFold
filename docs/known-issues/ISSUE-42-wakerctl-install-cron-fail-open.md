## RESOLVED 2026-08-25 — `wakerctl install-cron` formerly failed OPEN on `scrontab -l` errors

`read_scrontab()` now routes through the tri-state `read_scrontab_lines()` and raises
`WakerError` when the table cannot be read. Unit coverage proves that a failed listing
causes no `scrontab <file>` write. The save/install/diff operator procedure below remains
mandatory defense in depth for cluster recovery.

`install_cron` (`docs/orchestration/wakerctl.py`) is `strip_managed_block(read_scrontab(ctx))` →
`extend(scrontab_lines(...))` → `write_scrontab(...)`, and `write_scrontab` replaces the **entire** table via
`scrontab <tempfile>`. But `read_scrontab` returns `[]` when `scrontab -l` exits non-zero:

    def read_scrontab(ctx) -> list[str]:
        result = ctx.runner(["scrontab", "-l"])
        if result.returncode != 0:
            return []
        return result.stdout.splitlines()

So if the listing fails for any reason — transient Slurm error, auth blip, quota — `install-cron` writes a
scrontab containing **only** the managed block, deleting every entry outside the
`# BEGIN/END wakerctl managed block` markers, and reports success. Fail-open data loss on shared
infrastructure: either lane can run `install-cron`, and the entries destroyed could be the other lane's.

**The safe procedure, and it is not optional:**

1. `scrontab -l` and **check the exit code**, saving the output to a file;
2. confirm which lines lie inside the markers and note anything outside;
3. only then `install-cron`;
4. `scrontab -l` again and diff against the saved listing — the managed block may differ, nothing else may.

If step 1 fails, do **not** run `install-cron`; the listing failure is the thing to fix.

**Not fixed here** because `wakerctl.py` is one of the four known pre-existing submit-time hash drifts
(pinned by `p3f-pet-gate3-queue-latency-reconciliation-56169838.json`), so editing it moves a sha that a
receipt cites. The fix when someone owns that re-issue: distinguish "empty table" from "listing failed" —
raise `WakerError` on non-zero rather than returning `[]`.

> **CORRECTION 2026-08-11 — the stated reason above is void. The pin LAPSED on 2026-07-20.** Editing
> `wakerctl.py` today moves no live sha, so the pin is not what blocks this fix; ownership and a test are.
> Canonical account, including the three fixes declined on this false premise:
> **"The `wakerctl.py` pin in the Gate-3 queue-latency receipt LAPSED on 2026-07-20"**, below in this file.

**Related, and the reason this was found:** a HELD scrontab entry cannot be recovered with
`scontrol release` — Slurm refuses with *"Cannot modify scrontab jobs through scontrol."* The recovery **is**
`install-cron`, because it replaces the table rather than releasing a job. Verified 2026-08-10: held
`56160911` → fresh `56585597`, and a real tick at `2026-08-10T22:00:13Z`. Identified by the oversight session
reading the code; verified here against the file before running.

