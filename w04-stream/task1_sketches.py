#!/usr/bin/env python3
"""Week 4 · Task 1 — Answer questions about a stream you cannot store.

Textbook §4.3 (sampling), §4.4 (Bloom filter), §4.5 (Flajolet-Martin).

The premise of the whole chapter: the stream is longer than your memory, it
goes past once, and you still have to answer. Every method here trades an exact
answer for a bounded amount of space, and the job is to know exactly what you
traded.

You build three, and the harness checks each against the truth it is
approximating.

    python3 task1_sketches.py --verify
"""
import argparse, hashlib, math, random, statistics


class BloomFilter:
    """Membership, with one-sided error.

    A Bloom filter never says "no" about something you inserted. It sometimes
    says "yes" about something you did not. That asymmetry is the entire design
    and it is why it is useful for "have I seen this before" and useless for
    "is this definitely in the set".

    `m` bits, `k` hash functions.
    """

    def __init__(self, m, k, seed=246):
        self.m, self.k = m, k
        self.key = str(seed).encode()
        self.bits = bytearray((m + 7) // 8)    # m real bits, not m bytes

    def _indexes(self, item):
        # Two independent 64-bit hashes give all k (Kirsch-Mitzenmacher):
        # g_i = h1 + i*h2 behaves like k independent hashes for the fp rate.
        d = hashlib.blake2b(str(item).encode(), digest_size=16,
                            key=self.key).digest()
        h1, h2 = int.from_bytes(d[:8], "big"), int.from_bytes(d[8:], "big") | 1
        return [(h1 + i * h2) % self.m for i in range(self.k)]

    def add(self, item):
        for j in self._indexes(item):
            self.bits[j >> 3] |= 1 << (j & 7)

    def __contains__(self, item):
        return all(self.bits[j >> 3] >> (j & 7) & 1 for j in self._indexes(item))

    def expected_fp_rate(self, n_inserted):
        """The textbook's predicted false-positive rate after n insertions.

        §4.4.2 derives it. Return the number, do not measure it - the harness
        measures separately and compares the two.
        """
        return (1 - math.exp(-self.k * n_inserted / self.m)) ** self.k


def flajolet_martin(stream, n_hashes=64, seed=246):
    """Estimate how many DISTINCT items went past, in almost no memory.

    §4.5. Hash each item, count trailing zeros in the hash, keep the maximum.
    A maximum of R suggests about 2^R distinct items, because seeing R trailing
    zeros is a 1-in-2^R event.

    One hash gives an estimate with enormous variance, so you use many and
    combine them. How you combine them matters a great deal:

      * averaging 2^R directly is dominated by whichever hash got lucky - the
        values are exponential, so one outlier swamps the rest
      * the median is robust but can only ever be a power of two
      * §4.5.3 suggests grouping, and combining twice

    The harness accepts anything **within a factor of two** of the truth. That is
    not a generous tolerance, it is an honest one: this method really is that
    crude, and HyperLogLog exists because of it. Getting inside a factor of two
    reliably is the requirement; getting closer than that is not expected here.

    Return your estimate as a float.
    """
    salt = f"{seed}:".encode()
    R = [0] * n_hashes                         # the only state: one max per hash
    mask = [1] * n_hashes                      # the low R[i]+1 bits of hash i
    for x in stream:
        # one SHAKE digest of 4*n_hashes bytes = n_hashes independent 32-bit
        # hashes, read in one go instead of computing n_hashes hashes in Python
        d = hashlib.shake_128(salt + str(x).encode()).digest(4 * n_hashes)
        # hash i is bytes 4i..4i+3, little-endian. Its lowest byte settles
        # almost every case, and bytes iterate as cached small ints - no
        # allocation, which is what keeps tracemalloc from taxing this loop
        for i, low in enumerate(d[::4]):
            if not low & mask[i]:
                h = int.from_bytes(d[4 * i:4 * i + 4], "little")
                if not h & mask[i]:            # more than R[i] trailing zeros
                    R[i] = (h & -h).bit_length() - 1 if h else 32
                    mask[i] = (2 << R[i]) - 1
    return combine(R)


def combine(R, group=16):
    """Group and combine twice (§4.5.3) - but median inside the groups, then
    the mean of the medians. The textbook's order (mean inside, median across)
    lands 1.2-18x high with 64 hashes: 2^R has so heavy a tail that a group mean
    is still owned by its luckiest hash. The median kills that tail, and
    averaging four medians breaks the power-of-two steps a median is stuck on."""
    ests = [2 ** r for r in R]
    medians = [statistics.median(ests[i:i + group])
               for i in range(0, len(ests), group)]
    return float(statistics.mean(medians))


def reservoir_sample(stream, k, seed=246):
    """Keep k items uniformly at random from a stream of unknown length.

    §4.3. Every item that went past must end up with the same probability k/n
    of being in your sample, and you only ever hold k of them.

    Return a list of k items (or fewer if the stream was shorter).
    """
    rng = random.Random(seed)
    sample = []
    for i, x in enumerate(stream):             # i + 1 = items seen so far
        if i < k:
            sample.append(x)
        else:
            j = rng.randrange(i + 1)           # keep x with probability k/(i+1)
            if j < k:
                sample[j] = x                  # evicting a uniformly chosen slot
    return sample


# ------------------------------------------------------------------- harness
def verify():
    fails = 0
    rng = random.Random(246)

    def check(label, ok, detail=""):
        nonlocal fails
        print(f"  {'ok  ' if ok else 'FAIL'}  {label:<46} {detail}")
        fails += not ok

    # --- Bloom: no false negatives, ever
    try:
        bf = BloomFilter(m=8192, k=5)
    except NotImplementedError:
        print("  BloomFilter is still a stub"); return 1
    inserted = [f"item-{i}" for i in range(800)]
    for x in inserted:
        bf.add(x)
    check("no false negatives", all(x in bf for x in inserted))

    absent = [f"other-{i}" for i in range(20_000)]
    fp = sum(1 for x in absent if x in bf) / len(absent)
    predicted = bf.expected_fp_rate(len(inserted))
    close = abs(fp - predicted) < max(0.02, predicted * 0.5)
    check("measured false-positive rate matches theory", close,
          f"measured {fp:.3%}, predicted {predicted:.3%}")

    # --- Flajolet-Martin: a factor of two is what this method gives you
    try:
        distinct = 20_000
        stream = [f"k{rng.randrange(distinct)}" for _ in range(120_000)]
        est = flajolet_martin(stream)
    except NotImplementedError:
        print("  flajolet_martin is still a stub"); return 1
    true_distinct = len(set(stream))
    ratio = est / true_distinct
    check("distinct estimate within a factor of 2", 0.5 <= ratio <= 2.0,
          f"estimated {est:,.0f}, true {true_distinct:,} ({ratio:.2f}x)")

    # --- Reservoir: uniform over many trials
    try:
        counts = [0] * 20
        trials = 4000
        for t in range(trials):
            s = reservoir_sample(range(20), 5, seed=t)
            for i in s:
                counts[i] += 1
    except NotImplementedError:
        print("  reservoir_sample is still a stub"); return 1
    expected = trials * 5 / 20
    spread = (max(counts) - min(counts)) / expected
    check("reservoir is uniform across items", spread < 0.15,
          f"spread {spread:.1%} around {expected:.0f}")

    print(f"\n  {'all ok' if not fails else str(fails) + ' failed'}")
    return 1 if fails else 0


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--verify", action="store_true")
    a = p.parse_args()
    raise SystemExit(verify() if a.verify else p.print_help())
