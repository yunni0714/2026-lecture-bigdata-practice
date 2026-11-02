# Task 2 · The curse of dimensionality

I ran `python3 task2_curse.py` on 2026-11-02 (19:02–19:05), 13 times with
different options. All 21 rows are in `curse.json`. I did not change the script.

Every run samples random pairs of uniform points in the unit cube. "pairs" below
is how many distances were measured (pairs with i = j are dropped).

## A7 · Machine

| | |
|---|---|
| CPU | Intel Core Ultra X7 358H, 16 cores (laptop) |
| RAM | 31.4 GB (11.5 GB free) |
| OS / Python | Windows 11, Python 3.15.0 |
| Power | plugged in |
| Other apps | Claude app, GitHub Desktop, Opera |

Largest run: **1,000,000 pairs at d = 50 on 20,000 points, 3.9 s.**
Highest dimension: d = 1000 (2,000 points, 20,000 pairs), 1.4 s.
Time grows with pairs × d. Nothing here came near the memory limit.

## A1, A2 · Contrast vs dimension

1,000 points and 20,000 pairs, except d = 500 and 1000 (2,000 points).
Contrast = (max − min) / min. sd = standard deviation of the distances.

| dim | mean | sd | min | max | **contrast** | rel. sd | mean / √d | seconds |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2 | 0.521 | 0.248 | 0.003 | 1.326 | **488.6** | 0.476 | 0.368 | 0.01 |
| 5 | 0.884 | 0.249 | 0.111 | 1.687 | **14.26** | 0.282 | 0.395 | 0.02 |
| 10 | 1.274 | 0.245 | 0.438 | 2.159 | **3.93** | 0.193 | 0.403 | 0.02 |
| 20 | 1.815 | 0.245 | 0.821 | 2.670 | **2.25** | 0.135 | 0.406 | 0.04 |
| 30 | 2.228 | 0.243 | 1.220 | 3.126 | **1.56** | 0.109 | 0.407 | 0.05 |
| 40 | 2.575 | 0.241 | 1.545 | 3.566 | **1.31** | 0.093 | 0.407 | 0.06 |
| 50 | 2.867 | 0.238 | 1.909 | 3.785 | **0.98** | 0.083 | 0.406 | 0.07 |
| 70 | 3.397 | 0.240 | 2.465 | 4.357 | **0.77** | 0.071 | 0.406 | 0.09 |
| 100 | 4.068 | 0.243 | 3.206 | 4.954 | **0.55** | 0.060 | 0.407 | 0.14 |
| 120 | 4.470 | 0.243 | 3.476 | 5.457 | **0.57** | 0.054 | 0.408 | 0.16 |
| 150 | 4.990 | 0.246 | 4.064 | 5.955 | **0.47** | 0.049 | 0.407 | 0.20 |
| 200 | 5.776 | 0.239 | 4.871 | 6.682 | **0.37** | 0.041 | 0.408 | 0.27 |
| 500 | 9.126 | 0.241 | 8.099 | 10.176 | **0.26** | 0.026 | 0.408 | 0.71 |
| 1000 | 12.909 | 0.240 | 11.970 | 13.806 | **0.15** | 0.019 | 0.408 | 1.36 |

## A3 · What happens to contrast

It falls fast. At d = 2 the farthest pair is 489× farther than the nearest. At
d = 1000 it is only 15% farther.

- **Below 1** between d = 40 (1.31) and d = 50 (0.98): about **d ≈ 50**.
- **Below 0.5** between d = 120 (0.57) and d = 150 (0.47): about **d ≈ 140**.

Contrast went *up* from 100 to 120 (0.55 → 0.57). It depends on one minimum and
one maximum, so it is noisy.

Why it falls: look at the sd column. **The spread stays at 0.24 at every d**,
while the mean keeps growing. With 20,000 pairs, min and max are about
3.9 sd below and above the mean, so the gap max − min stays about 1.8–2.0 from
d = 20 on, and it becomes small next to distances that keep growing.

That also predicts where it crosses. Contrast < 1 when mean > 3 × 3.9 × 0.24 = 2.8,
which is d ≈ 47. Contrast < 0.5 when mean > 5 × 3.9 × 0.24 = 4.7, which is
d ≈ 131. Measured: about 50 and 140.

## A4 · How the mean grows

**Like √d, not like d.** From d = 100 to 1000 (10× more) the mean went from
4.07 to 12.91, which is 3.17×. √10 = 3.16.

The theory: for two uniform numbers in [0, 1], (x − y)² is 1/6 on average, so
the squared distance is about d/6 and the distance about √(d/6) = 0.408 √d.
The `mean / √d` column is 0.407–0.408 from d = 30 on.

At small d it is lower (0.368 at d = 2). That is because the mean of a square
root is smaller than the square root of the mean, and the gap is large when the
squared distance has a big spread compared to its size, which happens at small d.
With that correction the theory gives √(d/6) × (1 − 0.175/d): 0.527 at d = 2
(measured 0.521) and 1.268 at d = 10 (measured 1.274). By d = 200 the
correction is under 0.1%.

## A5 · Relative standard deviation

rel. sd = sd / mean. It falls like **0.59 / √d**: sd stays 0.24 and the mean
grows like 0.408 √d. Prediction 0.084 at d = 50, 0.042 at 200, 0.019 at 1000.
Measured 0.083, 0.041, 0.019.

**Which is the better measure? I think rel. sd.**

- It describes all the distances, not just the two most extreme ones. That is
  why it falls smoothly while contrast jumps (100 → 120).
- It does not depend on how many points or pairs you look at (A6: 0.078–0.084
  for every point count, while contrast went from 0.58 to 1.37).
- It says what actually breaks "nearest": almost all distances are about the
  same. At d = 200 a typical distance is 5.78 ± 4%, so the nearest centroid and
  the second nearest are often only a few percent apart.

Contrast is still useful as what one nearest-neighbour query feels, but it
mixes up d with the size of the sample.

## A6 · Point count at d = 50

| points | different pairs possible | pairs sampled | min | max | **contrast** | rel. sd |
|---:|---:|---:|---:|---:|---:|---:|
| 20 | 190 | 19,006 | 2.111 | 3.332 | **0.58** | 0.084 |
| 50 | 1,225 | 19,598 | 2.085 | 3.609 | **0.73** | 0.078 |
| 200 | 19,900 | 19,902 | 1.906 | 3.692 | **0.94** | 0.082 |
| 1,000 | 499,500 | 19,977 | 1.909 | 3.785 | **0.98** | 0.083 |
| 5,000 | 12.5 M | 19,997 | 1.971 | 3.698 | **0.88** | 0.084 |
| 20,000 | 200 M | 19,997 | 1.785 | 3.802 | **1.13** | 0.084 |
| 5,000 | 12.5 M | 199,962 | 1.797 | 4.030 | **1.24** | 0.084 |
| 20,000 | 200 M | 999,937 | 1.694 | 4.010 | **1.37** | 0.084 |

**Yes, contrast depends on n**, through the number of different pairs you look at.

- With 20 points there are only 190 different pairs, so the min is not very
  small and the max not very large: contrast 0.58.
- With more pairs it rises: 0.94 with 200 points, 1.24 with 200,000 pairs,
  1.37 with 1,000,000 pairs.
- From 200 to 20,000 points with the default 20,000 pairs it stays around
  0.88–1.13. The script always samples 20,000 pairs, so beyond ~200 points n
  barely changes what it sees. The 0.88 at 5,000 is noise.
- It grows slowly: 50× more pairs (20,000 → 1,000,000) only moved it from 0.98
  to 1.37. The min is about mean − z × sd, and z grows only like √(2 ln N).

What it means: "contrast drops below 1 at d = 50" is a statement about my
sample size, not about d alone. A bigger dataset always has a few very close and
very far pairs, so it needs more dimensions before contrast falls below 1. My
estimate for all 200 M pairs of 20,000 points (z ≈ 5.7) is d ≈ 100. I did not
measure that.

rel. sd did not move with n at all (0.078–0.084). The typical distance does not
care how many points there are.

## A8 · Does this threaten week 3's LSH?

**No, not in a way that hurts it.**

1. **The data is not uniform random.** The curse is about points whose
   coordinates are independent noise. Near-duplicate documents share most of
   their shingles because one was copied from the other. In week 3 the planted
   pairs had Jaccard ≥ 0.62 and random pairs about 0.006. That gap does not
   shrink when the shingle vocabulary (the "dimension") gets bigger.
2. **Random pairs do concentrate, and it does not matter.** Almost every random
   pair of documents has Jaccard near 0, which is the curse showing up. But LSH
   does not ask "which of these similar-looking pairs is nearest"; it asks
   "which pairs are above s = 0.6", and the pairs we want are far from the crowd.
3. **LSH never uses the dimension.** The chance two documents land in the same
   bucket is 1 − (1 − s^r)^b, which depends only on their similarity s. The
   minhash error depends on the number of hashes (≈ 0.47 / √n), not on the
   number of shingles.

Where it would hurt: if every pair had about the same similarity, the S-curve
could not separate near from far because nothing would be near. LSH would then
correctly find no pairs, but "the nearest document" would mean nothing, just
like a nearest point at d = 1000 here.
