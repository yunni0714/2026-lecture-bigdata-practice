# Week 4 · Observations

Machine: Intel Core Ultra X7 358H (16 cores, laptop), 31.4 GB RAM, Windows 11, Python 3.14.7. Task 2 ran on battery with Opera open; details in `limits.md`.

## Task 1 · Three sketches

- **Bloom:** bits are only ever set, never cleared, so an inserted item's k bits stay set and it is always found. Predicted 0.860%, measured 0.790% (158 vs 172 ± 13 of 20,000, within noise).
- **FM:** median inside 4 groups of 16 hashes, then the mean of the medians: 0.82–1.85× over 40 streams. Mean of 2^R gave 2–39× and the textbook's mean-then-median 1.2–18× (2^R's tail is too heavy for means); a plain median gave 0.82–2.05×.
- **Reservoir:** `j = rng.randrange(i + 1)` uses only the count so far, so after every item each one seen is kept with probability k/(i + 1), and the sample is uniform wherever the stream stops.

## Task 2 · Find where exact stops fitting

- **Unbearable at 102.4M items: 5.8 min and 3.06 GB. Time gave out first** (14 GB still free); 409.6M would need ~12 GB of objects, ~30 GB under tracemalloc.
- **Exact set: 4.0× memory per 4× n**, ≈ 80 B per distinct key (linear). **FM: flat at ~7 KB** over 256×, set by its 64 hashes. FM's ratio did not improve with n (1.00–1.40×), and in Python it was 5–10× slower per item.
- **2× is enough** for "roughly how many visitors today" (10k and 100k never get confused), **not** for per-user billing or a 10% day-over-day change, which the error alone can fake.

## Task 3 · Same memory, fewer mistakes

- **k: 1 → 7.** The derivative of (1 − e^(−kn/m))^k is zero at k = (m/n) ln 2 = 6.93.
- **Floor:** (1/2)^k = 0.6185^10 = **0.819%**. Reached **0.831%** with 0 false negatives in exactly 80,000 bits, 91.3% fewer false positives than the baseline.
- **Unknown n:** too low and it overfills (16,000 items here → 13.8%, worse than the baseline); too high wastes bits (sized for 16,000, the real 8,000 get 1.74%). Fix: a scalable Bloom filter, adding a 2× larger filter with a tighter rate whenever the current one is half full, and querying all of them.
