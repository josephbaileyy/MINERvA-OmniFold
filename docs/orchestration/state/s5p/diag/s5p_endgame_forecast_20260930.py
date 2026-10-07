#!/usr/bin/env python3
"""s5p production end-game forecast (2026-09-30T19:47Z): the meter's reservation rule and the runners' drain/retry.

MEASURES (a projection, not a rule): when each lane finishes and whether a submission is refused, under the frozen
queue logic. An open batch is charged at its 8.5 CPU node-h reservation until it closes. A submission is admitted
iff charged + 8.5 <= the production cap. On refusal the lane drains (polls every 300 s until no s5p cal/pow job is
queued) and retries once; a second refusal writes a terminal 'budget' final status. The first draining lane to poll
retries; the others see its job queued and keep waiting (serialized). Inputs are the measured batch durations and
costs to 19:47Z. CANNOT AUTHORIZE: any change (budget, schedule, rule); it prices the owner's options.
"""
import datetime as dt
import heapq

Z = dt.datetime.fromisoformat
CLOSED = 56.293  # 12 closed production batches, measured (meter-measure-batch1-report-20260930T1947Z.json)
DUR = {"pow": 22.8, "MnvTune": 23.4, "CV": 26.2, "MEC": 22.7, "NuWro": 28.4, "GiBUU": 27.6}  # latest batch, h
CUR = {"pow": ("2026-09-30T12:30", 2), "MnvTune": ("2026-09-30T14:40", 2), "CV": ("2026-09-30T17:49", 2),
       "MEC": ("2026-09-30T09:49", 2), "NuWro": ("2026-09-30T19:44", 2), "GiBUU": ("2026-09-30T19:34", 2)}


def sim(c, need, cap, res=8.5):
    closed, ev, open_, drain, log, ends, tnow = CLOSED, [], set(), [], [], {}, None
    for k, (t, b) in CUR.items():
        heapq.heappush(ev, (Z(t) + dt.timedelta(hours=DUR[k]), k, b))
        open_.add(k)
    while ev or drain:
        if not ev:
            k, b = drain.pop(0)
            if closed + res * len(open_) + res <= cap:
                open_.add(k)
                heapq.heappush(ev, (tnow + dt.timedelta(hours=DUR[k]), k, b))
                log.append((tnow, k, "retry admitted"))
            else:
                log.append((tnow, k, f"retry REFUSED -> terminal budget at {b} batches"))
                ends[k] = tnow
            continue
        tnow, k, b = heapq.heappop(ev)
        open_.discard(k)
        closed += c
        if b + 1 >= need[k]:
            ends[k] = tnow
            continue
        if closed + res * len(open_) + res <= cap:
            open_.add(k)
            heapq.heappush(ev, (tnow + dt.timedelta(hours=DUR[k]), k, b + 1))
        else:
            drain.append((k, b + 1))
            log.append((tnow, k, "refused -> drain"))
    return max(ends.values()), closed, log


if __name__ == "__main__":
    for cap in (200.0, 209.647):
        for c in (4.69, 4.83, 4.95):
            for nw in (7, 6):
                need = {"pow": 6, "MnvTune": 7, "CV": 7, "MEC": 7, "NuWro": nw, "GiBUU": 7}
                t, cl, log = sim(c, need, cap)
                ev = "; ".join(f"{e[0]:%m-%dT%HZ} {e[1]} {e[2]}" for e in log) or "no refusal"
                print(f"cap {cap:.3f} cost/batch {c:.2f} NuWro batches {nw}: terminal {t:%m-%dT%HZ}, production measured {cl:.1f} | {ev}")
    need = {"pow": 6, "MnvTune": 7, "CV": 7, "MEC": 7, "NuWro": 7, "GiBUU": 7}
    print("no cap binding:", f"{max(Z(t) + dt.timedelta(hours=DUR[k] * (need[k] - b)) for k, (t, b) in CUR.items()):%m-%dT%HZ}")
