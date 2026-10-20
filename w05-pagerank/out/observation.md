# Week 5 · Observations

Machine: Intel Core Ultra X7 358H (16 cores, laptop), 31.4 GB RAM, Windows 11, Python 3.14.7, on AC power with Discord, Steam and Opera open. Details in `convergence.md`.

## Task 1 · PageRank, and the two ways it breaks

- **Dead end:** in the broken version its rank is simply dropped (its column of M is all zeros), so the total goes 1 → 0.67 → 0.17 → 0. I send it to all n pages uniformly, as if the dead end linked to every page. Removing dead ends first and ranking them afterwards (§5.1.4) is the other defensible choice.
- **One fix for both:** a dead end has no way out and a trap has no way out of the group; teleporting gives every page a way out to every other page, so rank can neither leak away nor pile up in one place (trap C+D: 1.0000 broken, 0.893 fixed, A and B keep 0.04 and 0.07).
- **beta** is the probability that the surfer clicks a random link on the page. With probability 1 − beta they get bored and type a random URL, so at 0.85 a run of clicks lasts 1/(1 − 0.85) ≈ 6.7 links on average.

## Task 2 · What convergence costs

- **beta → 1 cost almost nothing here: 14 iterations at 0.5, 24 at 0.99** (the β^k bound says 34 and 2,292). The error shrinks by β × 0.43 per step: the two traps (the 10 seed pages and the planted pair) are the slow β-modes, and a uniform start, being equal to the teleport vector, has exactly zero of them. Starting all rank on one trap page brings back the textbook rate β, 36 → **2,362** iterations, the 1/(1 − β) blow-up.
- **A4: iterations flat, time linear.** 20–22 iterations at β = 0.85 from 1,200 to 100,000 pages, while time grew 0.009 s → 1.12 s with the edges (5.9k → 509k). The count is how many times the error must be multiplied by a fixed rate; size only changes the cost of each multiplication.
- **A6: the same 10 pages at every beta**, the 10-page seed trap, and only one swap (7th ↔ 8th, at β = 0.5445). The planted trap climbs from 98th to 12th without gaining rank, because the seed trap drains everyone else (it holds 98% of rank at 0.99). A published top 3 survives any β; who is 8th or 11th is the choice of whoever picked 0.85.

## Task 3 · A graph that will not fit as a matrix

- **What I store:** the given adjacency list as integer indices (E = 5,877 ints, out-degree is just its length) and two rank vectors: **2n = 2,400 floats** against n² = 1,440,000. 600× less memory and 71× faster ("strong").
- **R5:** the teleport term (1 − β)/n and the dead-end term β · (rank on dead ends)/n are the *same number for every page*. So each iteration computes one scalar and adds it while making the O(n) pass over the new vector it already makes; the dense version writes that one number into n² matrix cells (whole columns of 1/n for each dead end).
- **Worst per-node difference: 6.94e-17**, not zero because floating-point addition is done in a different order (the dense code adds each dead end's r/n to every row separately, mine adds their total once). Ranks are ~1e-3, so this is rounding in the last bit or two, not a different answer.
