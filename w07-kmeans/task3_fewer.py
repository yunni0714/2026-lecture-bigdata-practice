#!/usr/bin/env python3
"""Week 7 · Task 3 — The same clustering, with far fewer distances.

Textbook §7.3, and §7.1.3 for why distance is the expensive part.

`NaiveKMeans` does what the definition says: every iteration, compare every
point with every centroid. That is n x k distance computations per pass, and on
a real dataset the distance computation is almost the entire cost.

Most of that work is wasted. After the first couple of iterations, most points
do not change cluster, and most centroids barely move. The triangle inequality
lets you prove a point cannot have changed cluster **without measuring it**.

    python3 bench.py
    python3 bench.py --yours

Correctness first: your final SSE must match the baseline's. Fewer distances
with a worse clustering is not an improvement, it is a different algorithm.
"""


class NaiveKMeans:
    """Every point against every centroid, every iteration."""

    def __init__(self, k, max_iter=50):
        self.k, self.max_iter = k, max_iter

    def run(self, points, initial_centroids, distance):
        centroids = list(initial_centroids)
        labels = [None] * len(points)
        for self.iterations in range(1, self.max_iter + 1):
            changed = False
            for i, p in enumerate(points):
                best, bi = None, 0
                for j, c in enumerate(centroids):
                    d = distance(p, c)
                    if best is None or d < best - 1e-12:
                        best, bi = d, j
                if labels[i] != bi:
                    labels[i] = bi
                    changed = True
            centroids = _means(points, labels, self.k, centroids)
            if not changed:
                break
        return labels, centroids


def _means(points, labels, k, previous):
    out = []
    for j in range(k):
        group = [p for p, l in zip(points, labels) if l == j]
        if group:
            out.append(tuple(sum(v) / len(group) for v in zip(*group)))
        else:
            out.append(previous[j])
    return out


class YourKMeans:
    """Your k-means.

        __init__(k, max_iter=50)
        run(points, initial_centroids, distance) -> (labels, centroids)

    Same starting centroids, same `distance` function - which is counted. That
    counter is your score.

    The idea, from §7.3 and the triangle inequality:

        if a point is much closer to its current centroid than that centroid
        moved, and than any other centroid could have come, then it cannot have
        changed cluster, and you do not have to measure anything

    Keeping enough bookkeeping to make that test cheap, without keeping so much
    that the bookkeeping costs more than the distances, is the task.

    You may call `distance` on two centroids, and those calls are counted too -
    which is the correct accounting, since that is real work. There are k of
    them and n points, and k is much smaller than n. That asymmetry is the
    whole opening.
    """

    def __init__(self, k, max_iter=50):
        self.k, self.max_iter = k, max_iter

    def run(self, points, initial_centroids, distance):
        # Elkan's bounds. Per point: one upper bound on the distance to its own
        # centroid, and k lower bounds, one per centroid. Starting with
        # upper = inf makes iteration 1 a full assignment that still skips any
        # centroid the centroid-centroid distances rule out.
        k, n = self.k, len(points)
        centroids = list(initial_centroids)
        labels = [0] * n
        upper = [float("inf")] * n              # >= d(point, own centroid)
        lower = [[0.0] * k for _ in range(n)]   # lower[i][j] <= d(point, c_j)
        loose = [True] * n                      # upper[i] not an exact distance
        for self.iterations in range(1, self.max_iter + 1):
            # k(k-1)/2 distances between centroids. A centroid c_j cannot be
            # nearer than c_a if d(c_a, c_j) >= 2 d(x, c_a).
            cc = [[0.0] * k for _ in range(k)]
            for a in range(k):
                for b in range(a + 1, k):
                    cc[a][b] = cc[b][a] = distance(centroids[a], centroids[b])
            half_nearest = [0.5 * min(row[b] for b in range(k) if b != j)
                            for j, row in enumerate(cc)]

            changed = self.iterations == 1      # the baseline starts from None
            for i, p in enumerate(points):
                a, u = labels[i], upper[i]
                if u <= half_nearest[a]:        # no other centroid can be nearer
                    continue
                li = lower[i]
                for j in range(k):
                    if j == a or u <= li[j] or u <= 0.5 * cc[a][j]:
                        continue
                    if loose[i]:                # tighten before measuring others
                        u = li[a] = distance(p, centroids[a])
                        loose[i] = False
                        if u <= li[j] or u <= 0.5 * cc[a][j]:
                            continue
                    d = li[j] = distance(p, centroids[j])
                    if d < u - 1e-12:           # same tie rule as the baseline
                        a, u = j, d
                if a != labels[i]:
                    labels[i] = a
                    changed = True
                upper[i] = u

            new = _means(points, labels, k, centroids)
            if not changed:
                break
            # k distances: how far each centroid moved. Every bound shifts by it.
            move = [0.0 if c == m else distance(c, m)
                    for c, m in zip(centroids, new)]
            for i in range(n):
                lower[i] = [l - m if l > m else 0.0 for l, m in zip(lower[i], move)]
                upper[i] += move[labels[i]]
                loose[i] = True
            centroids = new
        return labels, centroids
