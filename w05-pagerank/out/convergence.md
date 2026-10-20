# Task 2 · How long PageRank takes to converge

All numbers come from `python3 task2_convergence.py` on 2026-10-20, between
13:25 and 13:29, in eight invocations. The raw rows are in `convergence.json`
(28 runs). PageRank is Task 1's `pagerank`: uniform start, uniform teleport,
dead-end rank spread over all n nodes, stop when the L1 change between two
iterations drops below `tol`.

One change to the script: a `--max-iter` flag (default still 500) and the cap
recorded in each row, in case beta = 0.99 needed more than 500 iterations. It
never did, and why it did not is most of A3.

## A7 · The machine

| | |
|---|---|
| CPU | Intel Core Ultra X7 358H, 16 cores / 16 threads (laptop), 18 MB L3 cache |
| RAM | 31.4 GB, 10.8 GB free before the run |
| OS / Python | Windows 11 Home 10.0.26200, CPython 3.14.7 |
| Power | on AC power, battery at 86% |
| Also running | Discord, Steam, Opera, the Claude desktop app. CPU load ~8% before the run |
| Graph | `bench.build()`: power-law out-degrees, 12 dead ends, one planted 2-node trap |

Times under 0.05 s are single runs and carry a few milliseconds of noise.
Iteration counts are exact and do not depend on the machine.

## A1, A2 · Iterations against beta (1,200 nodes, tol 1e-10)

| beta | iterations | seconds | textbook bound ⌈ln tol / ln β⌉ | measured rate per iteration |
|---:|---:|---:|---:|---:|
| 0.50 | 14 | 0.006 | 34 | 0.183 = β × 0.366 |
| 0.55 | 14 | 0.006 | 39 | |
| 0.60 | 15 | 0.007 | 46 | |
| 0.65 | 16 | 0.007 | 54 | |
| 0.70 | 17 | 0.008 | 65 | 0.286 = β × 0.408 |
| 0.75 | 18 | 0.009 | 81 | |
| 0.80 | 19 | 0.008 | 104 | |
| 0.85 | 20 | 0.009 | 142 | 0.373 = β × 0.439 |
| 0.90 | 21 | 0.010 | 219 | |
| 0.95 | 23 | 0.010 | 449 | 0.410 = β × 0.432 |
| 0.99 | **24** | 0.011 | **2,292** | 0.428 = β × 0.432 |

"Rate" is the ratio of two successive L1 changes once the iteration has
settled, measured separately for five betas (snippet under A3).

## A3 · The shape, and why

**It barely grows: 14 iterations at 0.5, 24 at 0.99.** The textbook's bound,
error ≤ β^k, says 34 and 2,292. On this graph the error shrinks by
**β × 0.43** per iteration, not by β.

The error after k iterations is e_k = β^k · M^k · e_0. Two things shrink it:
β (each step keeps only a β share of the old distribution) and M itself.
Where M has an eigenvalue of size 1, only β is left, and that is the β^k
bound. This graph has two such places, both closed groups of pages (spider
traps):

- the planted trap p01198 ↔ p01199 (eigenvalues +1 and −1)
- **the 10 seed nodes p00000–p00009**, which only link to each other. The
  generator starts every link list from them, so they form a 10-node trap of
  their own

Neither slows anything down here, because **the start vector is the teleport
vector** (both uniform). Then e_0 = u − r*, and its component along an
eigenvector of M with eigenvalue λ is c · β(1 − λ)/(1 − βλ), which is **zero
for λ = 1**. The −1 mode would make the two trap pages swing back and forth,
but a uniform start gives them equal rank and nothing ever makes them
unequal. What is left is the next eigenvalue, about 0.43: the graph is almost
a DAG (only 26 of 5,877 edges point to a later page), so rank reaches the
seeds within a few hops.

**Check: start everything on p01199 instead.** Same graph, same betas:

| beta | uniform start | all rank on p01199 | rate with that start |
|---:|---:|---:|---:|
| 0.50 | 14 | 36 | 0.500 |
| 0.70 | 17 | 68 | 0.700 |
| 0.85 | 20 | 147 | 0.850 |
| 0.95 | 23 | 464 | 0.950 |
| 0.99 | 24 | **2,362** | 0.990 |

```python
r = {v: 0.0 for v in g}; r["p01199"] = 1.0    # instead of 1/n each
# then Task 1's update loop, unchanged, until the L1 change < 1e-10
```

Now the rate is exactly β, and the count follows ln(tol)/ln(β) ≈
ln(1/tol)/(1 − β): **it blows up like 1/(1 − β) as β → 1.** The textbook is
right about the worst case; the uniform start just never meets it on this
graph. The real web has many groups that are *almost* closed (λ close to 1
but not equal), and for those the factor β(1 − λ)/(1 − βλ) is not zero, so
a beta near 1 does cost iterations there.

β → 1 also makes traps win. The 10-seed trap holds **34.5%** of all rank at
0.5, **75.8%** at 0.85 and **98.1%** at 0.99. That, more than speed, is the
case against a beta near 1.

## A4 · Graph size (tol 1e-10)

Expectation before running: the iteration count would not move, because the
rate is set by β and the shape of the graph, not by how many pages it has;
the time would grow with the edge count, because every iteration visits every
edge once.

| nodes | × | edges | it. β=0.5 | it. β=0.85 | it. β=0.99 | seconds β=0.85 | ms / iteration | ns per (node + edge) |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1,200 | 1 | 5,877 | 14 | 20 | 24 | 0.009 | 0.45 | 64 |
| 6,000 | 5 | 30,433 | 14 | 22 | 25 | 0.051 | 2.32 | 64 |
| 20,000 | 16.7 | 101,665 | 14 | 21 | 25 | 0.179 | 8.52 | 70 |
| 100,000 | 83 | 509,332 | – | 20 | – | 1.117 | 55.9 | 92 |

- **Iterations: flat** (20–22 at β = 0.85 over 83×). The count is how many
  times the error has to be multiplied by ~0.37 to get under 1e-10. That is a
  dimensionless number, and the bigger graphs have the same seed trap and the
  same near-DAG shape, so the same rate.
- **Time: linear in the edges.** 124× the time for 87× the edges. Per edge and
  per iteration it is constant up to 20,000 nodes and 40% dearer at 100,000.
  The likely cause (not measured) is that the graph and the two rank dicts,
  tens of MB of Python objects at that size, no longer fit in the 18 MB L3
  cache.

They differ because one counts *multiplications* and the other the *cost of
one multiplication*. Size only enters the second.

## A5 · Tolerance (1,200 nodes)

| tol | iterations β=0.85 | iterations β=0.99 |
|---:|---:|---:|
| 1e-4 | 9 | 10 |
| 1e-6 | 12 | 13 |
| 1e-8 | 16 | 18 |
| 1e-10 | 20 | 24 |
| 1e-12 | 25 | 29 |

**Each extra digit costs a fixed number of iterations: 2.0 at β = 0.85 and
2.4 at β = 0.99** (from 1e-4 to 1e-12). That is what geometric convergence
means: the error is multiplied by the same rate every iteration, so one
digit costs 1/log10(1/rate) iterations, 2.3 and 2.7 for the measured rates.
The textbook bound would charge 14.2 and 229 per digit.

`tol` bounds the change between two iterations, not the distance to the
answer, which is about change × rate / (1 − rate). At rate 0.43 the two are
close: stopping at 1e-10 with β = 0.99 left a true L1 error of 1.6e-11. At a
rate of 0.99 the true error would be 99× the change, so the same `tol` would
promise far less than it seems to.

## A6 · Does the top 10 move?

**The same ten pages at every beta and every size: the 10 seed nodes.** One
change of order, and only one: p00000 and p00004 swap 7th and 8th place
between β = 0.50 and 0.55. Bisecting the crossing puts it at **β = 0.5445**.
Places 1–6 and 9–10 never change.

| beta | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
|---|---|---|---|---|---|---|---|---|---|---|
| 0.50 | p00009 | p00001 | p00006 | p00005 | p00003 | p00002 | **p00000** | **p00004** | p00007 | p00008 |
| 0.55 – 0.99 | p00009 | p00001 | p00006 | p00005 | p00003 | p00002 | **p00004** | **p00000** | p00007 | p00008 |

The top is stable because it *is* the trap: every link list started from
these ten pages. Below the top β matters more. The planted 2-node trap is
**98th** at β = 0.5, 39th at 0.85 and **12th** at 0.99. It does not gain
rank (0.0017 at every beta: nothing links into it, so it lives on teleport
alone); everyone else outside the seeds loses rank to the seed trap, and the
small trap overtakes them.

So the head of the ranking can be trusted whoever chose β. The boundaries
(7th vs 8th, who is 11th) and anything shaped like a trap are a consequence
of the 0.85 somebody picked.
