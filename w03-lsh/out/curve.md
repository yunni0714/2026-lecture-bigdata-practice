# Task 2 · The curve, and where it broke

All numbers below come from one clean sweep of `python3 task2_crossover.py` on
2026-10-05, 13:57–14:22, on the machine below. The raw rows are in
`crossover.json` (31 measurements), and the tables are what
`python3 task2_crossover.py --table` prints, plus a µs-per-comparison column.
An earlier session, measured with a game running, is kept in
`crossover_run1.json` and compared under A4. That comparison is the most
useful thing in this file.

## A6 · The machine

| | |
|---|---|
| CPU | Intel Core Ultra X7 358H, 16 cores / 16 threads (laptop, hybrid P/E cores), 18 MB L3 cache |
| RAM | 31.4 GB |
| OS / Python | Windows 11 Home 10.0.26200, CPython 3.14.7 |
| Power | plugged in (AC). The laptop was on battery at 30% just before, and was plugged in for the run on purpose |
| Also running | idle background apps only: Claude Code and ChatGPT desktop apps, OneDrive and Google Drive sync, Logitech Options+. CPU load was ~1% before the run. No game, nothing else used during the 25 minutes |
| Data | `build_docs(n)`: n sets of 60 shingles from a 5,000-word vocabulary, ~6% of them planted near-duplicates with 4–14 edits, same seed and recipe as `bench.py` |
| Timing | best of 3 runs for n ≤ 1,000 (traced) and n ≤ 2,000 (plain), one run above that. LSH = `YourFinder` from Task 3 (128 hashes, 32 bands) |

## First, two things that were wrong with the measurement

**1. The given loop never measured more than 2,120 documents.** The original
`task2_crossover.py` built its data with `bench.build()[:n]`, and `bench.build()`
makes exactly 2,120 documents. Every size above that silently measured the same
2,120. The A4 check is what exposed it, on the very first run of the unmodified
script (first session):

| n asked | brute s | comparisons | t(n)/t(n/2) |
|---:|---:|---:|---:|
| 1,000 | 2.94 | 499,500 | – |
| 2,000 | 11.91 | 1,999,000 | 4.05x |
| 4,000 | 13.53 | **2,246,140** | **1.14x** |

2,246,140 is C(2120, 2). The fix is `build_docs(n)` in `task2_crossover.py`,
which makes n documents by the same recipe.

**2. `tracemalloc` is not a neutral observer.** The given `timed()` keeps
tracemalloc on while timing, and tracemalloc charges every allocation. The same
sizes with and without it, from this sweep:

| n | LSH plain | LSH traced | slowdown | brute plain | brute traced | slowdown |
|---:|---:|---:|---:|---:|---:|---:|
| 50 | 44 ms | 260 ms | **5.9x** | 4.0 ms | 5.0 ms | 1.25x |
| 500 | 188 ms | 816 ms | 4.3x | 0.40 s | 0.49 s | 1.22x |
| 2,000 | 486 ms | 1,567 ms | 3.2x | 6.49 s | 8.15 s | 1.26x |
| 16,000 | 3.32 s | 8.94 s | 2.7x | 512.9 s | 582.7 s | 1.14x |

Brute force allocates two temporary sets per comparison; LSH allocates a
128-int list for every 1 in the matrix. So LSH pays 3–6x and brute force about
1.2x, and the crossover the given loop reports is a crossover *under
tracemalloc*, more than twice as far out as the real one. I kept the given loop
(it is the only way to get A5's peak memory), added `--plain`, and report both.

## A3 · Time against n, both methods

### With tracemalloc, as the given loop measures (time and peak memory)

| n | brute s | brute cmp | t(n)/t(n/2) | µs / cmp | brute peak | LSH s | LSH cmp | LSH peak | faster |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|:---|
| 50 | 0.005 | 1,225 | - | 4.04 | 7 KB | 0.260 | 3 | 720 KB | brute |
| 100 | 0.019 | 4,950 | 3.93x | 3.93 | 8 KB | 0.420 | 6 | 1.2 MB | brute |
| 150 | 0.044 | 11,175 | - | 3.90 | 8 KB | 0.521 | 8 | 1.5 MB | brute |
| 200 | 0.077 | 19,900 | 3.94x | 3.86 | 8 KB | 0.597 | 12 | 1.9 MB | brute |
| 250 | 0.122 | 31,125 | - | 3.92 | 8 KB | 0.635 | 15 | 2.1 MB | brute |
| 300 | 0.176 | 44,850 | 4.03x | 3.92 | 8 KB | 0.691 | 17 | 2.4 MB | brute |
| 400 | 0.321 | 79,800 | 4.18x | 4.02 | 9 KB | 0.742 | 24 | 2.9 MB | brute |
| 500 | 0.489 | 124,750 | 4.00x | 3.92 | 9 KB | 0.816 | 29 | 3.3 MB | brute |
| 600 | 0.713 | 179,700 | 4.06x | 3.97 | 9 KB | 0.875 | 34 | 3.8 MB | brute |
| 650 | 0.841 | 210,925 | - | 3.98 | 9 KB | 0.910 | 37 | 4.0 MB | brute |
| 700 | 0.967 | 244,650 | - | 3.95 | 9 KB | 0.914 | 40 | 4.2 MB | LSH |
| 750 | 1.109 | 280,875 | - | 3.95 | 9 KB | 0.935 | 42 | 4.4 MB | LSH |
| 1,000 | 1.952 | 499,500 | 3.99x | 3.91 | 9 KB | 1.058 | 59 | 5.4 MB | LSH |
| 2,000 | 8.149 | 1,999,000 | 4.17x | 4.08 | 26 KB | 1.567 | 117 | 9.3 MB | LSH |
| 4,000 | 32.810 | 7,998,000 | 4.03x | 4.10 | 30 KB | 2.451 | 244 | 17.0 MB | LSH |
| 8,000 | 140.533 | 31,996,000 | 4.28x | 4.39 | 64 KB | 4.603 | 517 | 32.1 MB | LSH |
| 16,000 | **582.713** | 127,992,000 | 4.15x | 4.55 | 93 KB | 8.936 | 1,160 | 62.1 MB | LSH |

### Plain wall time (`--plain`, no tracemalloc)

| n | brute s | brute cmp | t(n)/t(n/2) | µs / cmp | LSH s | LSH cmp | faster |
|---:|---:|---:|---:|---:|---:|---:|:---|
| 50 | 0.004 | 1,225 | - | 3.23 | 0.044 | 3 | brute |
| 100 | 0.016 | 4,950 | 4.06x | 3.25 | 0.078 | 6 | brute |
| 150 | 0.036 | 11,175 | - | 3.24 | 0.100 | 8 | brute |
| 200 | 0.064 | 19,900 | 3.97x | 3.20 | 0.117 | 12 | brute |
| 250 | 0.099 | 31,125 | - | 3.19 | 0.132 | 15 | brute |
| 300 | 0.145 | 44,850 | 4.01x | 3.24 | 0.146 | 17 | brute |
| 350 | 0.195 | 61,075 | - | 3.20 | 0.162 | 21 | LSH |
| 400 | 0.257 | 79,800 | 4.03x | 3.22 | 0.172 | 24 | LSH |
| 500 | 0.399 | 124,750 | 4.02x | 3.20 | 0.188 | 29 | LSH |
| 1,000 | 1.618 | 499,500 | 4.05x | 3.24 | 0.290 | 59 | LSH |
| 2,000 | 6.488 | 1,999,000 | 4.01x | 3.25 | 0.486 | 117 | LSH |
| 4,000 | 26.310 | 7,998,000 | 4.06x | 3.29 | 0.892 | 244 | LSH |
| 8,000 | 114.298 | 31,996,000 | 4.34x | 3.57 | 1.761 | 517 | LSH |
| 16,000 | **512.924** | 127,992,000 | 4.49x | 4.01 | 3.320 | 1,160 | LSH |

Peak memory is not measured in this mode.

Read as a picture: brute force is a parabola that passes 1 s near n = 700
(traced) or n = 800 (plain) and 8.5–10 minutes at 16,000. LSH is close to a
line, 0.04 s at 50 documents and 3.3 s at 16,000 (plain, 1.89x per doubling at
the top), and after the crossover the two never meet again.

## A4 · Is brute force actually quadratic?

Doubling n should quadruple the time. The exact count is n(n−1)/2, so the
ideal ratio is 3.92 at 50 → 100 and 4.00 from a few hundred up. Computed from
the tables, not asserted:

| doubling | traced | plain |
|---|---:|---:|
| 50 → 100 | 3.93x | 4.06x |
| 100 → 200 | 3.94x | 3.97x |
| 150 → 300 | 4.03x | 4.01x |
| 200 → 400 | 4.18x | 4.03x |
| 250 → 500 | 4.00x | 4.02x |
| 300 → 600 | 4.06x | – |
| 500 → 1,000 | 3.99x | 4.05x |
| 1,000 → 2,000 | 4.17x | 4.01x |
| 2,000 → 4,000 | 4.03x | 4.06x |
| 4,000 → 8,000 | 4.28x | 4.34x |
| 8,000 → 16,000 | 4.15x | 4.49x |

**It holds.** Up to 4,000 every ratio is 3.93–4.18, and the cost per
comparison is flat: 3.86–4.10 µs traced, 3.19–3.29 µs plain.

The last two doublings come out a little above 4 because each comparison got
more expensive, 3.29 → 3.57 → 4.01 µs plain. That could be the documents no
longer fitting in the CPU cache, or the laptop slowing down over a long run.
To separate the two I timed the same ~2 million comparisons in short
alternating bursts, plain:

| burst | µs per comparison |
|---|---:|
| n = 2,000, all rows | 3.30 |
| n = 16,000, first 125 rows | 3.76 |
| n = 2,000 again | 3.26 |
| n = 16,000 again | 3.79 |

The cost goes back down every time n goes back down, so it depends on **n,
not on time**: the document sets take about 3.8 KB each, which is 7 MB at
2,000 and 14 MB at 4,000 (inside the 18 MB L3) but 29 MB at 8,000 and 58 MB at
16,000 (outside it). That explains ~15% of extra cost per comparison; the
remaining few percent in the 8.5-minute 16,000 run is within normal drift for
one long run. The algorithm is quadratic; the hardware adds a small step when
the data leaves the cache.

### Compared with the first session

I measured the same sweep once before, with a game (Balatro, about one core of
CPU plus the GPU) running during the later sizes, over about an hour of
continuous load (`crossover_run1.json`):

| | first session (game running) | re-run (clean, AC power) |
|---|---:|---:|
| traced 8,000 brute | 199.9 s (6.25 µs/cmp) | 140.5 s (4.39 µs/cmp) |
| traced 16,000 brute | 1,011.6 s (7.90 µs/cmp) | 582.7 s (4.55 µs/cmp) |
| traced 8,000 → 16,000 | **5.06x** | **4.15x** |
| plain 2,000 → 4,000 | **6.35x** (one bad point) | 4.06x |
| crossover, traced / plain | ≈ 680 / ≈ 300 | ≈ 680 / ≈ 300 |

In the first session the same 8,000-document burst cost 6.1 µs per comparison
and then 12.1 µs four minutes later: the slowdown depended on *time under
load*, which is the laptop sharing its power budget with the game. That made
two doublings look non-quadratic (5.06x, 6.35x). The clean re-run brings both
back to 4x, and the remaining excess depends on n, not on time. The same
16,000 run took 1.7x longer in the first session.

What did **not** change is the crossover: absolute times moved by up to 1.7x,
but both methods slowed down together, so the point where they cross stayed at
≈ 680 / ≈ 300. Absolute times describe the machine's state at the moment;
ratios and the crossover describe the algorithms. That is what A6 is for.

## A5 · Peak memory at the largest n (16,000, traced)

| | brute force | LSH |
|---|---:|---:|
| peak traced allocation | 93 KB | 62.1 MB |
| what it is | the result set and two temporary sets per comparison | signature matrix 16,000 × 128 Python ints (~28 B each + 8 B pointer ≈ 59 MB), plus the row → columns index and the bucket dicts |

Brute force is essentially memory-free: the documents were built before the
timer and it allocates nothing that survives a comparison. LSH pays for its
speed in memory, linearly: 720 KB at 50, 5.4 MB at 1,000, 62 MB at 16,000, i.e.
about 3.9 KB per document at 128 hashes. These numbers are identical to the
first session to the KB: allocation, unlike time, does not depend on the
machine's state. On this 31 GB machine that is nowhere near pressure, and it
would reach 1 GB around 260,000 documents (or a quarter of that with 32-bit
ints instead of Python objects).

## A2 · Where it became unpleasant

**Brute force passed a minute at n = 8,000** (140.5 s traced, 114.3 s plain),
and **n = 16,000 took 582.7 s = 9.7 minutes traced, 512.9 s = 8.5 minutes
plain**, for 128 million comparisons. What ran out was **time, not memory**:
brute force never used more than 93 KB, LSH 62 MB, against 31 GB available. At
the measured ~4.2x per doubling, 32,000 would take about 40 minutes and 100,000
about 6 hours, so I stopped at 16,000. LSH did 16,000 in 8.9 s traced and 3.3 s
plain, and could have gone on for another two orders of magnitude before
either time or memory hurt.

## A7 · The crossover

| | brute faster up to | LSH faster from | crossover n |
|---|---:|---:|---:|
| traced (given loop) | 650 (0.841 s vs 0.910 s) | 700 (0.967 s vs 0.914 s) | **≈ 680** |
| plain wall time | 300 (0.145 s vs 0.146 s, a tie) | 350 (0.195 s vs 0.162 s) | **≈ 300** |

Interpolating the gap between brute and LSH linearly gives 678 traced and 302
plain. The fixed part of LSH is what moves: 0.04 s plain vs 0.26 s traced at
n = 50. Either way, below a few hundred documents on this machine you should
just compare everything.

## A8 · Why LSH loses at small n, specifically

LSH does its work before it compares anything, and at small n that work is
almost all there is. Each stage timed separately (plain, best of 5):

| stage | n = 50 | n = 500 | n = 2,000 | what it is |
|---|---:|---:|---:|---|
| distinct shingles (rows) | 2,182 | 4,989 | 5,000 | |
| ones in the matrix | 3,000 | 29,996 | 119,991 | 60 per document |
| shingle → row map | 0.2 ms | 2.1 ms | 10.2 ms | one pass over the 1s |
| evaluate 128 hash functions on every row | **29.5 ms** | 71.0 ms | 68.9 ms | 128 × rows `(a·r + b) mod p` calls |
| min-updates | 9.2 ms | 91.6 ms | 355.7 ms | 128 mins for each 1 in the matrix |
| banding and buckets | 0.2 ms | 2.6 ms | 10.9 ms | 32 tuple slices per document |
| compare the candidates | 0.01 ms | 0.13 ms | 0.53 ms | 3 / 29 / 117 pairs |
| **LSH total** | **41 ms** | 180 ms | 459 ms | |
| **brute force, all pairs** | **3.8 ms** | 398 ms | 6,482 ms | 1,225 / 124,750 / 1,999,000 pairs |

So at 50 documents LSH spends 30 ms hashing rows and 9 ms updating signatures
to avoid 4 ms of comparisons. The row-hashing cost is per *distinct shingle*,
not per document, so it barely shrinks with n: 30 ms at 50 documents, then
flat at about 70 ms once all 5,000 vocabulary rows are present. The
min-update cost is per 1 in the matrix (about 3 µs each), which is linear in n.
Brute force pays neither; its only work is comparisons, which are quadratic but
cheap (3.2 µs each), so at n = 50 all 1,225 of them cost less than hashing the
rows once. Under tracemalloc the same accounting holds, but every small
allocation in LSH is taxed (5.9x at n = 50), which is why the traced crossover
is at 680 rather than 300.
