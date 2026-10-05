#!/usr/bin/env python3
"""Week 3 · Task 3 — Find the same pairs without comparing everything.

Textbook §3.4.

`BruteForce` compares every pair. On 3,000 documents that is 4.5 million
comparisons and it is completely correct. On 3 million documents it is 4.5
trillion and it is completely useless.

Beat it. Find the same near-duplicate pairs while making far fewer comparisons.

    python3 bench.py
    python3 bench.py --yours

The harness counts every call you make to `similarity()`. That is your score.
It also checks **recall** - which of the truly similar pairs you found. Skipping
comparisons is easy; skipping comparisons without losing the pairs is the task.
"""
import random

from task1_minhash import minhash_signatures, lsh_candidates

# A Mersenne prime. (a*r + b) mod P with 0 < a < P is a bijection on 0..P-1, so
# for any row count below 2^31 it is a legitimate "random permutation" stand-in
# (§3.3.3) with no collisions between distinct rows.
PRIME = 2 ** 31 - 1


class BruteForce:
    """Correct, and quadratic."""

    def __init__(self, threshold):
        self.threshold = threshold

    def find(self, docs, similarity):
        """docs is [set_of_shingles, ...]. Return {(i, j), ...} with i < j."""
        out = set()
        for i in range(len(docs)):
            for j in range(i + 1, len(docs)):
                if similarity(docs[i], docs[j]) >= self.threshold:
                    out.add((i, j))
        return out


def make_hashes(n, seed):
    """n universal hash functions r -> (a*r + b) mod PRIME, fixed by `seed`."""
    rng = random.Random(seed)
    hashes = []
    for _ in range(n):
        a = rng.randrange(1, PRIME)
        b = rng.randrange(0, PRIME)
        hashes.append(lambda r, a=a, b=b: (a * r + b) % PRIME)
    return hashes


def candidate_probability(s, n_hashes, bands):
    """§3.4.2: P(a pair at similarity s shares a bucket in >= 1 band)."""
    r = n_hashes / bands
    return 1 - (1 - s ** r) ** bands


def step(n_hashes, bands):
    """Where the S-curve's step sits: (1/b)^(1/r)."""
    return (1 / bands) ** (bands / n_hashes)


class YourFinder:
    """Minhash + banded LSH, reusing the Task 1 code.

        __init__(threshold)
        find(docs, similarity) -> {(i, j), ...}

    `similarity(a, b)` is the only way to compare two documents, and every call
    is counted. Everything else - signatures, banding, bucketing - is free, in
    the sense that the harness does not charge you for it. That is deliberate:
    it is also roughly true at scale, where the comparison is the expensive
    part and the hashing is linear.

    The two knobs, and the arithmetic (§3.4.2) behind the defaults
    ----------------------------------------------------------------
        n = 128 hashes, b = 32 bands, r = n/b = 4 rows per band

        P(candidate | s) = 1 - (1 - s^4)^32       step at (1/32)^(1/4) = 0.420

    The threshold is 0.6, so the step is put well *below* it, on purpose:

        s      0.006   0.30   0.40   0.50   0.60   0.62   0.70   0.80
        P      4e-8    0.23   0.56   0.87   0.988  0.994  0.9997 1.000

    - A pair just above the threshold (the planted pairs bottom out near
      s = 46/74 = 0.62) is caught with probability 0.99, so recall holds.
    - A random pair here sits at s ≈ 0.006 (60 shingles from a 5,000
      vocabulary), and 4e-8 × 2.2 million pairs is well under one false
      candidate, so the comparisons saved stay at 99.99%.
    - What the low step *costs* is the band 0.42 - 0.60: anything there is
      compared and then rejected. This data has nothing there; real data would.

    Putting the step *at* the threshold (b = 8, r = 16 → 0.88, or b = 16,
    r = 8 → 0.71) drops most of the pairs between 0.62 and 0.8. Putting it far
    below (b = 128, r = 1 → 0.008) keeps recall and throws away the savings.
    The numbers for both are in out/observation.md.

    `n_hashes` and `bands` can be overridden so those experiments are one line.
    """

    N_HASHES = 128
    BANDS = 32
    SEED = 3

    def __init__(self, threshold, n_hashes=None, bands=None, seed=None):
        self.threshold = threshold
        self.n_hashes = n_hashes or self.N_HASHES
        self.bands = bands or self.BANDS
        self.seed = self.SEED if seed is None else seed

    def find(self, docs, similarity):
        # 1. shingles -> dense row numbers, one pass over the 1s. The
        #    characteristic matrix is then `columns`: a set of rows per doc.
        row_of = {}
        columns = [{row_of.setdefault(s, len(row_of)) for s in d} for d in docs]
        n_rows = len(row_of)

        # 2. signatures: Task 1's one-pass-over-the-rows minhash
        hashes = make_hashes(self.n_hashes, self.seed)
        sigs = minhash_signatures(columns, hashes, n_rows)

        # 3. banding: Task 1's LSH - pairs that share a bucket in >= 1 band
        cands = lsh_candidates(sigs, self.bands)

        # 4. only the candidates are ever compared - this is the charged part
        thr = self.threshold
        return {(i, j) for i, j in cands
                if similarity(docs[i], docs[j]) >= thr}
