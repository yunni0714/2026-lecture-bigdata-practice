# Task 2 · Convergence

I ran `python3 task2_convergence.py` on 2026-10-20 (13:25–13:29), 8 times with
different options. All 28 rows are in `convergence.json`.

I added a `--max-iter` option (default is still 500) in case beta 0.99 needed
more than 500 iterations. It never did.

## A7 · Machine

| | |
|---|---|
| CPU | Intel Core Ultra X7 358H, 16 cores (laptop) |
| RAM | 31.4 GB (10.8 GB free) |
| OS / Python | Windows 11, Python 3.14.7 |
| Power | plugged in |
| Other apps | Discord, Steam, Opera, Claude app (CPU ~8% before the run) |

Times under 0.05 s are from one run, so they are a bit noisy.
Iteration counts do not depend on the machine.

## A1, A2 · Iterations vs beta (1,200 nodes, tol 1e-10)

| beta | iterations | seconds | book bound (β^k ≤ tol) |
|---:|---:|---:|---:|
| 0.50 | 14 | 0.006 | 34 |
| 0.55 | 14 | 0.006 | 39 |
| 0.60 | 15 | 0.007 | 46 |
| 0.65 | 16 | 0.007 | 54 |
| 0.70 | 17 | 0.008 | 65 |
| 0.75 | 18 | 0.009 | 81 |
| 0.80 | 19 | 0.008 | 104 |
| 0.85 | 20 | 0.009 | 142 |
| 0.90 | 21 | 0.010 | 219 |
| 0.95 | 23 | 0.010 | 449 |
| 0.99 | 24 | 0.011 | 2,292 |

## A3 · Shape

The count grows very slowly: 14 at 0.5, 24 at 0.99.
The book's bound says 34 and 2,292, so a big jump near 1 was possible. It did not happen.

Why: here the error goes down by about **β × 0.43** each step, not by β.
The slow part of PageRank comes from closed groups of pages (traps).
This graph has two: the 10 seed pages (p00000–p00009 only link to each other)
and the planted pair p01198/p01199.
But my start vector is uniform, the same as the teleport vector, so these slow
parts start at zero and never show up.

Check: I started with all rank on p01199 instead. Then the error goes down by
exactly β each step:

| beta | uniform start | all rank on p01199 |
|---:|---:|---:|
| 0.50 | 14 | 36 |
| 0.70 | 17 | 68 |
| 0.85 | 20 | 147 |
| 0.95 | 23 | 464 |
| 0.99 | 24 | **2,362** |

So the book is right about the worst case: as β → 1 the count grows like
1/(1 − β). The uniform start just avoids it on this graph.

High β also makes traps stronger. The 10 seed pages hold 34.5% of all rank at
0.5, 75.8% at 0.85 and 98.1% at 0.99.

## A4 · Graph size (tol 1e-10)

Prediction from the theory:

- **Iterations should not change with size.** The error is cut by a fixed rate
  each step, and that rate comes from β and the shape of the graph, not from
  the number of pages.
- **Time should grow with the number of edges.** One step visits every edge once.

Result: both held (table below). The surprise in this task was β (A3), not size.

| nodes | edges | it. β=0.5 | it. β=0.85 | it. β=0.99 | seconds β=0.85 | ms per iteration |
|---:|---:|---:|---:|---:|---:|---:|
| 1,200 | 5,877 | 14 | 20 | 24 | 0.009 | 0.45 |
| 6,000 | 30,433 | 14 | 22 | 25 | 0.051 | 2.32 |
| 20,000 | 101,665 | 14 | 21 | 25 | 0.179 | 8.52 |
| 100,000 | 509,332 | – | 20 | – | 1.117 | 55.9 |

- **Iterations: almost the same** (20–22 at β = 0.85) from 1,200 to 100,000 nodes.
- **Time: grows with the edges.** 0.009 s → 1.12 s for 87× more edges.

They are different questions. The iteration count is how many times the error
has to be cut down, and that depends on β and the shape of the graph, not its
size. Size only changes how long one step takes, because one step visits every
edge once. At 100,000 nodes one edge cost about 40% more per step, probably
because the data no longer fits in the CPU cache (I did not check this).

## A5 · Tolerance (1,200 nodes)

| tol | iterations β=0.85 | iterations β=0.99 |
|---:|---:|---:|
| 1e-4 | 9 | 10 |
| 1e-6 | 12 | 13 |
| 1e-8 | 16 | 18 |
| 1e-10 | 20 | 24 |
| 1e-12 | 25 | 29 |

Each extra digit costs about 2 iterations (2.0 at β = 0.85, 2.4 at β = 0.99).
The cost per digit stays the same, because the error is cut by the same factor
every step.

Note: `tol` is the change between two steps, not the real error. Here they are
close: at β = 0.99, stopping at 1e-10 left a real error of 1.6e-11.

## A6 · Does the top 10 move?

The top 10 is **the same 10 pages** at every β and every size (the 10 seed pages).
Only one change: p00000 and p00004 swap 7th and 8th place between β = 0.50 and
0.55. The exact point is about β = 0.5445.

| beta | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
|---|---|---|---|---|---|---|---|---|---|---|
| 0.50 | p00009 | p00001 | p00006 | p00005 | p00003 | p00002 | **p00000** | **p00004** | p00007 | p00008 |
| 0.55 – 0.99 | p00009 | p00001 | p00006 | p00005 | p00003 | p00002 | **p00004** | **p00000** | p00007 | p00008 |

Lower in the list, β matters more. The planted trap pair is 98th at β = 0.5,
39th at 0.85 and 12th at 0.99. Its own rank does not change (0.0017); it moves up
because everyone else loses rank to the seed trap.

So the top of a ranking is safe to trust. Close places (7th vs 8th, who is 11th)
depend on whoever chose 0.85.
