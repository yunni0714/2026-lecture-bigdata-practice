# Task 2 · Where exact stopped fitting

All numbers come from `python3 task2_limits.py` on 2026-10-07, on the machine
below, in two invocations: a sweep of five sizes (13:37–13:55) and one push of
the exact set alone with `--exact-only` (13:55–14:01). The raw rows are in
`limits.json` (6 measurements). Times and peaks are what the given loop
measures, which is **with tracemalloc on**; what that costs is measured
separately under A2.

## A6 · The machine

| | |
|---|---|
| CPU | Intel Core Ultra X7 358H, 16 cores / 16 threads (laptop, hybrid P/E cores), 18 MB L3 cache |
| RAM | 31.4 GB, of which 14.7 GB was free before the run |
| OS / Python | Windows 11 Home 10.0.26200, CPython 3.14.7 |
| Power | **on battery**, 64% at the start and 58% at the end. Not plugged in |
| Also running | Opera with many tabs (~5 GB of working set across its processes) and the Claude desktop app. CPU load ~1% before the run |
| Data | `stream(n)`: n keys `key-<i>` drawn from `0.4·n` values, so about 37% of the stream is distinct |
| FM | Task 1's `flajolet_martin`: 64 hashes, median inside groups of 16, mean of the 4 medians |

## A3 · Memory and time against n, both methods

| n | distinct | exact s | µs / item | exact peak | B / distinct | × previous | FM s | µs / item | FM peak | FM estimate | FM / true |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 100,000 | 36,702 | 0.23 | 2.3 | 3.9 MB | 107 | – | 1.3 | 12.9 | 7.18 KB | 51,200 | 1.40× |
| 400,000 | 146,970 | 0.94 | 2.3 | 11.6 MB | 79 | 2.95× | 6.3 | 15.7 | 7.07 KB | 180,224 | 1.23× |
| 1,600,000 | 587,625 | 5.13 | 3.2 | 46.6 MB | 79 | 4.02× | 28.6 | 17.8 | 6.99 KB | 655,360 | 1.12× |
| 6,400,000 | 2,349,909 | 13.17 | 2.1 | 188.3 MB | 80 | 4.04× | 94.4 | 14.8 | 7.04 KB | 2,359,296 | 1.00× |
| 25,600,000 | 9,399,592 | 83.36 | 3.3 | 756.4 MB | 80 | 4.02× | 840.3 | 32.8 | 6.99 KB | 12,582,912 | 1.34× |
| 102,400,000 | 37,596,727 | 347.89 | 3.4 | **3,056.2 MB** | 81 | 4.04× | – | – | – | – | – |

The span is 1,024× (256× for FM). FM was skipped at 102.4M on purpose, see
the last section.

## A4 · Two growth rates

- **Exact set: linear.** Every 4× in n is 4.02–4.04× in peak memory from
  400,000 on; the log-log slope from 400,000 to 25.6M is **1.005**. Each
  distinct key costs a steady **≈ 80 bytes** (a 52-byte `str`, 56 once the
  allocator rounds it, plus 25–30 bytes of the set's hash table), which is ≈ 30 bytes per stream item at this
  distinct ratio. The 100,000 row is the exception at 107 B/distinct: the
  set had just resized and was holding an emptier table.
- **Flajolet-Martin: flat.** 7.18 KB at 100,000 and 6.99 KB at 25.6M, a slope of
  **−0.005** over 256×. Those 7 KB are 64 maxima, 64 masks, one 256-byte
  digest and the loop's temporaries: set by `n_hashes`, not by the data. At
  25.6M the exact set is 108,000× larger.

## A2 · Where it became unpleasant, and what ran out

**102.4M items (37.6M distinct): 5.8 minutes and 3.06 GB. Time gave out first.**
Memory still had room: free RAM was 14.3 GB right after the run.

The 3.06 GB is what tracemalloc reports, not what the process held. The same
job measured separately, with and without tracemalloc, reading the process's
peak working set from Windows:

| n | tracemalloc peak | process peak, traced | process peak, untraced | time traced | time untraced |
|---:|---:|---:|---:|---:|---:|
| 6,400,000 | 188 MB | 475 MB | 218 MB | 21.8 s | 6.2 s |
| 25,600,000 | 757 MB | 1,898 MB | 873 MB | 83.5 s | 24.4 s |

So tracemalloc adds 2.5× in memory (its own record for every live block) and
3.4× in time, and it undercounts the real set by ~15% (allocator overhead).
Scaled to 102.4M: **~7.7 GB of process memory traced, ~3.5 GB untraced.**

The next step is where memory runs out. At **409.6M** the stream has ~150M
distinct keys, ≈ **12 GB** of Python objects at 80 B each: ~30 GB of process
memory under tracemalloc (all of the 31.4 GB RAM), and ~14 GB even without it,
which is all of the free RAM with the browser open. I did not run it: it would
have pushed the laptop into paging rather than measured anything, and at
3.4 µs per item it would have taken ~23 minutes to get there.

## A5 · FM's accuracy at each size

1.40×, 1.23×, 1.12×, 1.00×, 1.34×. **It neither gets better nor worse with n.**
The relative error of FM is set by the number of hashes, not by how much data
went past; 64 hashes give the same spread at 100,000 as at 25.6M. The estimates
also move in steps: each group median is a power of two, so the result is a
mean of four powers of two (12,582,912 = 1.5 × 2²³). Across 40 test streams in
Task 1 the same rule landed between 0.82× and 1.85×.

## Time, which the flat line does not show

FM's memory is flat, but in Python it is **5–10× slower than the exact set**
per item (13–18 µs vs 2–3 µs): every item costs one 256-byte SHAKE digest and
64 checks in the interpreter, while `set.add` is one C call. At 25.6M FM took
14 minutes, the longest single measurement of the session.

That 25.6M FM row is also 2× slower per item than the others (32.8 µs). Re-run
right afterwards, FM was back to 14.5 µs (400,000) and 15.3 µs (1.6M), so the
slowdown belonged to that 14-minute stretch, not to n. The laptop was on battery
under sustained load, and power or thermal throttling is the likely cause; I
did not confirm it.

## Two things about the measurement itself

**1. tracemalloc taxes allocations, and my first FM allocated a lot.** It read
the 64 hashes as Python ints, one new object each (64 per item). Under
tracemalloc that ran at 72 µs per item against 7.9 µs plain, which would have
made the 25.6M FM run half an hour. I rewrote the loop to test the lowest byte
of each hash first (bytes iterate as cached small ints, no allocation) and
build the full int only when that byte passes: 17 µs per item traced, with
**identical estimates**. The method did not change, only how many objects the
loop creates.

**2. `--exact-only` was added to `task2_limits.py`.** At ~15 µs per item, FM at
102.4M would have taken ~26 minutes to show again a flat 7 KB. The 102.4M row
therefore has no FM fields; FM's growth and accuracy rest on the five sizes
above.
