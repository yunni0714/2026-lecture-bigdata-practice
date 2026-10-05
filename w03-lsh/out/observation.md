# Week 3 · Observations

Machine: Intel Core Ultra X7 358H (16 cores, laptop), 31.4 GB RAM, Windows 11, Python 3.14.7. Task 2 was measured on AC power with only idle background apps (Claude Code, ChatGPT, OneDrive/Google Drive sync); an earlier run with a game open is compared in `curve.md`.

## Task 1 · Minhash and LSH from the matrix up

- **One pass over the rows:** a per-column pass re-reads the whole matrix once per document; the row pass reads it once, computing h1(r)…hn(r) once per row and updating every column that has a 1 there.
- **R5:** leftover rows go one each to the first `n mod b` bands (n=10, b=3 → 4, 3, 3), so no hash work is thrown away and no band is much stricter than the rest; more bands than rows raises `ValueError`.
- **S1–S4 at 1.0 vs 2/3:** with 2 hashes the estimate can only be 0, 0.5 or 1. More hashes narrow it (standard error ≈ 0.47/√n, ±0.047 at 100 hashes), at a cost linear in n in hashing time and signature size.

## Task 2 · Find the crossover on your own machine

- **Crossover ≈ 680 documents** with the given tracemalloc loop (≈ 300 in plain wall time, since tracemalloc taxes LSH's allocations more). Below it LSH loses because it hashes every distinct shingle 128 times first: at n = 50 that is 30 ms of hashing (2,182 shingles) to save 4 ms of comparisons.
- **A4 held:** every doubling up to 4,000 was 3.93–4.18× (ideal ≈ 4×). The last two were 4.15–4.49× because the documents outgrew the 18 MB L3 cache: alternating bursts cost 3.3 µs per comparison at n = 2,000 and 3.8 µs at 16,000. A first run with a game open gave 5.06× from throttling; the clean re-run fixed that, and the crossover did not move.
- **Unpleasant from n = 8,000:** brute force passed a minute there (2.3 min) and took 9.7 minutes at 16,000. Time ran out, not memory: peak 93 KB brute vs 62 MB LSH, out of 31 GB. LSH did the same n in 8.9 s.

## Task 3 · Find the same pairs, comparing far less

- **n = 128, b = 32, r = 4:** step ≈ (1/32)^(1/4) = 0.42, deliberately below the 0.6 threshold. Planted pairs bottom out at s ≈ 0.62, where 1 − (1 − 0.62⁴)³² = 0.994; random pairs (s ≈ 0.006) collide with P ≈ 4 × 10⁻⁸. Result: 124 comparisons, recall 100%, 99.99% avoided.
- **Wrong way:** raising the step above 0.6 lost pairs as the S-curve predicts (b = 16, step 0.71 → recall 81.8%; b = 8, step 0.88 → 18.2%); lowering it to b = 128, r = 1 kept recall but compared 854,608 pairs.
- **Free hashing** is fair only while the quadratic comparison cost dominates (above ~700 documents here). At millions of documents hashing (128 min-updates per shingle, ~4 GB of signatures) is the main cost left: it is linear, not free.
