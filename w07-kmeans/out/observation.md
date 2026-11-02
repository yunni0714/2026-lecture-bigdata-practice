# Week 7 · Observations

Machine: Intel Core Ultra X7 358H laptop, 31.4 GB RAM, Windows 11, Python 3.15.0, plugged in. Details in `curse.md`.

## Task 1 · k-means, and the thing that decides the answer

- **R3:** an empty cluster keeps its old centroid, the same rule as task 3's `NaiveKMeans`. It happened in 3 of 40 random seeds, and each time the cluster stayed empty, leaving 2 real clusters (SSE 96.12). Moving it to the point farthest from its centroid instead rescued all 3: 27/40 seeds found the blobs instead of 24/40.
- Over 40 seeds random init found the three blobs **24 times (60%)**, k-means++ **40 times**. A bad start puts two centroids in one blob, and k-means cannot fix that, because a centroid only moves to the mean of its own points (SSE 96.1 vs 0.12).
- ++ measures every point against every new centroid before iteration 1 (n·k distances, the same as one full pass). It buys a spread-out start, because far points are likely to be picked. I would skip it when I already have good starting centroids (e.g. last run's), when k is large and its k passes one after another are slow, or when there are outliers, since it likes far points.
- SSE by k (best of 40 ++ runs): 256.1, 96.1, **0.12**, 0.09, 0.06 … 0 at k = 9. It always drops, and k = n gives 0 with every point alone, which means nothing. I would pick the k where the drop suddenly gets small (the elbow): 3 here.

## Task 2 · Watch distance stop meaning anything

- Contrast fell below **1 at about d = 50** (40: 1.31, 50: 0.98) and below 0.5 at about d = 140, with 20,000 sampled pairs. The sd of the distances stays 0.24 at every d while the mean grows like √(d/6), so the nearest–farthest gap stays the same size while the distances grow.
- **A6: n matters.** At d = 50, 20 points (190 different pairs) gave 0.58 and 1,000,000 pairs of 20,000 points gave 1.37. More pairs means more extreme pairs, so a bigger dataset needs more dimensions before contrast drops below 1. rel. sd did not move (0.078–0.084), so I think it measures the curse better.
- **A8:** week 3's LSH is not threatened. Near-duplicates are not random points: planted pairs had Jaccard ≥ 0.62 and random pairs ≈ 0.006, and LSH's bucket chance 1 − (1 − s^r)^b depends only on s, not on the number of shingles. The curse would only matter if every pair were about equally similar, and then there would be nothing to find.

## Task 3 · The same clustering, with far fewer distances

- Elkan's bounds. Per point: an upper bound on the distance to its own centroid, 12 lower bounds (one per centroid) and a flag, so **13 extra floats per point**, 260,000 in total. Each iteration also measures 66 centroid–centroid distances and how far each centroid moved: 2,998 of my 338,547 calls (0.9%). Result **96.7% cut**, 17.2 s → 1.8 s.
- **R5:** the per-centroid **lower bounds** were the single biggest test: the first to rule out 48% of the (point, other centroid) pairs. The centroid–centroid tests ruled out 49% together (25% as whole points at once). The lower bounds cost 12 floats per point, and every iteration all 240,000 of them must be lowered by how far each centroid moved. With only one lower bound per point (Hamerly) I got 88.8%.
- **SSE difference: exactly 0.** Labels and centroids are identical to the baseline (43 iterations both). It had to be: a distance is only skipped when the triangle inequality proves the point cannot move, every distance that is measured is the same number, and the centroids come from the same `_means` on the same labels.
- **Iteration 1 was 50.7% of my calls** (171,729). It is not zero pruning: if d(c_a, c_j) ≥ 2 d(x, c_a), c_j cannot be nearer, which skipped 28% of iteration 1's 240,000 pairs. The last iterations needed only a few hundred calls.
