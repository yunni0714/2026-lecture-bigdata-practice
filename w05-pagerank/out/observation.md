# Week 5 · Observations

Machine: Intel Core Ultra X7 358H laptop, 31.4 GB RAM, Windows 11, Python 3.14.7, plugged in. Details in `convergence.md`.

## Task 1 · PageRank, and the two ways it breaks

- In the broken version a dead end's rank is just lost, so the total goes 1 → 0.67 → 0.17 → 0. My fix gives a dead end's rank to all n pages equally, as if it linked to every page. (Removing dead ends first, §5.1.4, would also work.)
- A dead end and a trap are both places the surfer cannot leave. Teleporting gives every page a way out, so rank cannot leak away or pile up in one place. (Trap C+D: 1.0 broken, 0.89 fixed.)
- beta is the chance the surfer clicks a link. With 1 − beta they jump to a random page instead, so at 0.85 that happens about every 6.7 clicks.

## Task 2 · What convergence costs

- beta → 1 cost very little here: 14 iterations at 0.5, 24 at 0.99 (book bound: 34 and 2,292). My start vector is uniform like the teleport, so the slow parts from the two traps start at zero. Starting all rank on one trap page gave 2,362 iterations at 0.99, as the book says.
- Size: iterations stayed at 20–22 from 1,200 to 100,000 nodes, but time grew with the edges (0.009 s → 1.12 s). The count depends on beta and the graph's shape; size only changes the cost of one step.
- Top 10: the same pages at every beta, only 7th and 8th swap (at beta ≈ 0.5445). A small trap moves from 98th to 12th. The top is reliable; close places depend on the chosen beta.

## Task 3 · A graph that will not fit as a matrix

- I keep the adjacency list (as int indexes) and two rank lists: 2n = 2,400 floats instead of n² = 1,440,000. 600× less memory and 71× faster.
- R5: teleport adds the same number (1 − beta)/n to every page, and the dead-end share is also the same for every page. So it is one number per step, added in the loop over the pages. No matrix is needed.
- Worst difference from the dense answer: 6.94e-17. It is not zero only because the floats are added in a different order.
