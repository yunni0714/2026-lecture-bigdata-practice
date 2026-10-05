#!/usr/bin/env python3
"""Week 3 · Task 2 — Find the crossover on your own machine.

Textbook §3.4.

Everybody knows brute force is quadratic and LSH is not. That is not the
interesting question. The interesting question is **where, on the machine in
front of you, does it start to matter** - and that answer is yours alone. It
depends on your CPU, your memory, and how big your shingle sets are.

This script gives you the timing loop. The two methods are yours: import them
from Task 1 and Task 3.

    python3 task2_crossover.py --sizes 500,1000,2000,4000
    python3 task2_crossover.py --sizes 8000,16000          # keep going
    python3 task2_crossover.py --table                     # markdown of out/crossover.json

Write down where it hurts. That is the deliverable.

What I changed in the loop, and why
-----------------------------------
* `bench.build()[:n]` silently caps at 2,120 documents - that is all
  bench.build() ever makes - so every size above 2,120 measured the same
  2,120 documents (n=4000 gave 2,246,140 comparisons, exactly n=2120's). The
  quadratic check in A4 is what exposed it. `build_docs(n)` below makes n
  documents with bench's own recipe (same seed, vocabulary, shingle count and
  ~6% planted near-duplicates), so the curve really is a curve in n.
* `--repeat k` runs each size k times and keeps the fastest wall time
  (peak memory is the max). Small sizes are tens of milliseconds and noisy.
* `--note` records what else was running (A6). The machine block now also
  has the CPU model, core count and RAM, not just the platform string.
* `--plain` times without tracemalloc. Profiling showed tracemalloc slows the
  allocation-heavy LSH ~4.5x and brute force only ~1.2x, so the crossover the
  given loop reports is a crossover *under tracemalloc*. Both are recorded,
  tagged by a "tracemalloc" field, and `--table` prints them separately.
"""
import argparse, json, os, platform, random, time, tracemalloc

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")


# ---------------------------------------------------------------- machine
def cpu_name():
    system = platform.system()
    try:
        if system == "Windows":
            import winreg
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                 r"HARDWARE\DESCRIPTION\System\CentralProcessor\0")
            return winreg.QueryValueEx(key, "ProcessorNameString")[0].strip()
        if system == "Linux":
            for line in open("/proc/cpuinfo"):
                if line.lower().startswith("model name"):
                    return line.split(":", 1)[1].strip()
        if system == "Darwin":
            import subprocess
            return subprocess.check_output(
                ["sysctl", "-n", "machdep.cpu.brand_string"], text=True).strip()
    except Exception:
        pass
    return platform.processor() or platform.machine()


def ram_gb():
    try:
        if platform.system() == "Windows":
            import ctypes
            class MemoryStatus(ctypes.Structure):
                _fields_ = [("dwLength", ctypes.c_ulong),
                            ("dwMemoryLoad", ctypes.c_ulong),
                            ("ullTotalPhys", ctypes.c_ulonglong),
                            ("ullAvailPhys", ctypes.c_ulonglong),
                            ("ullTotalPageFile", ctypes.c_ulonglong),
                            ("ullAvailPageFile", ctypes.c_ulonglong),
                            ("ullTotalVirtual", ctypes.c_ulonglong),
                            ("ullAvailVirtual", ctypes.c_ulonglong),
                            ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
            ms = MemoryStatus()
            ms.dwLength = ctypes.sizeof(MemoryStatus)
            ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(ms))
            return round(ms.ullTotalPhys / 2 ** 30, 1)
        if hasattr(os, "sysconf"):
            return round(os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES") / 2 ** 30, 1)
    except Exception:
        pass
    return None


def machine(note=None):
    info = {
        "platform": platform.platform(),
        "processor": cpu_name(),
        "cores": os.cpu_count(),
        "ram_gb": ram_gb(),
        "python": platform.python_version(),
    }
    if note:
        info["note"] = note
    return info


# ------------------------------------------------------------------ data
def build_docs(n, seed=None):
    """n documents by bench.build()'s recipe, but n of them.

    bench.build() makes exactly N_DOCS + PLANTED = 2,120 documents, so
    `bench.build()[:n]` stops growing at 2,120. Same ingredients here - the
    same seed, SHINGLES-sized sets from a VOCAB-sized vocabulary, and the same
    PLANTED/N_DOCS share of near-duplicates cloned with 4-14 edits - so the
    Task 3 numbers at n=2,120 are still comparable, and n=16,000 is 16,000.
    """
    import bench
    rng = random.Random(bench.SEED if seed is None else seed)
    planted = round(n * bench.PLANTED / (bench.N_DOCS + bench.PLANTED))
    base = n - planted
    docs = [set(rng.sample(range(bench.VOCAB), bench.SHINGLES)) for _ in range(base)]
    for _ in range(planted):
        i = rng.randrange(base)
        clone = set(docs[i])
        for _ in range(rng.randint(4, 14)):
            clone.discard(rng.choice(list(clone)))
            clone.add(rng.randrange(bench.VOCAB))
        docs.append(clone)
    rng.shuffle(docs)
    return docs


# ---------------------------------------------------------------- timing
def timed(fn, *args, trace=True):
    """Wall time and peak memory of one call.

    tracemalloc is not a neutral observer: it charges every allocation, and
    LSH allocates far more often than brute force (a 128-int list per 1 in the
    matrix vs. two temporary sets per comparison). Profiled on this machine it
    slows LSH about 4.5x and brute force about 1.2x, which moves the crossover.
    `trace=False` (the --plain flag) measures wall time alone; peak is None.
    """
    if trace:
        tracemalloc.start()
    t0 = time.perf_counter()
    result = fn(*args)
    elapsed = time.perf_counter() - t0
    peak = None
    if trace:
        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
    return result, elapsed, peak


def timed_best_of(repeat, make_finder, docs, threshold, trace=True):
    """Fastest wall time over `repeat` runs, the largest peak, and the calls."""
    import bench
    best_t, worst_m, calls = None, None, None
    for _ in range(repeat):
        sim = bench.Counter()
        _, t, m = timed(make_finder(threshold).find, docs, sim, trace=trace)
        best_t = t if best_t is None else min(best_t, t)
        if m is not None:
            worst_m = m if worst_m is None else max(worst_m, m)
        calls = sim.calls
    return best_t, calls, worst_m


# ----------------------------------------------------------------- table
def _fmt_bytes(b):
    if b is None:
        return "-"
    return f"{b / 1024:,.0f} KB" if b < 2 ** 20 else f"{b / 2 ** 20:,.1f} MB"


def table(path):
    """out/crossover.json as markdown tables with the A4 doubling ratios.

    One table per measuring mode: with tracemalloc (the loop as given) and
    plain wall time (--plain). Within a mode the last measurement of a size wins.
    """
    data = json.load(open(path))
    modes = {}
    for r in data["runs"]:
        modes.setdefault(r.get("tracemalloc", True), {})[r["n"]] = r
    for traced in sorted(modes, reverse=True):
        by_n = modes[traced]
        print(f"### {'with tracemalloc (time and peak memory, as the given loop measures)' if traced else 'plain wall time (--plain, no tracemalloc)'}\n")
        print("| n | brute s | brute cmp | t(n)/t(n/2) | brute peak | LSH s | LSH cmp | LSH peak | faster |")
        print("|---:|---:|---:|---:|---:|---:|---:|---:|:---|")
        for n in sorted(by_n):
            r = by_n[n]
            half = by_n.get(n // 2)
            ratio = f"{r['brute_s'] / half['brute_s']:.2f}x" if half else "-"
            lsh = ("lsh_s" in r)
            faster = ("brute" if not lsh or r["brute_s"] < r["lsh_s"] else "LSH")
            print(f"| {n:,} | {r['brute_s']:.3f} | {r['brute_calls']:,} | {ratio} "
                  f"| {_fmt_bytes(r['brute_peak_bytes'])} "
                  + (f"| {r['lsh_s']:.3f} | {r['lsh_calls']:,} | {_fmt_bytes(r['lsh_peak_bytes'])} "
                     if lsh else "| - | - | - ")
                  + f"| {faster} |")
        print()
    m = data.get("machine", {})
    print()
    print(f"machine: {m.get('processor')} | {m.get('cores')} cores | {m.get('ram_gb')} GB | "
          f"{m.get('platform')} | Python {m.get('python')}"
          + (f" | {m['note']}" if m.get("note") else ""))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--sizes", default="250,500,1000,2000",
                   help="comma-separated document counts to try")
    p.add_argument("--threshold", type=float, default=0.6)
    p.add_argument("--repeat", type=int, default=1,
                   help="runs per size; the fastest wall time is kept")
    p.add_argument("--note", default=None,
                   help="what else was running (A6), stored with the machine")
    p.add_argument("--plain", action="store_true",
                   help="wall time only, no tracemalloc (see timed())")
    p.add_argument("--table", action="store_true",
                   help="print out/crossover.json as a markdown table and exit")
    a = p.parse_args()
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, "crossover.json")

    if a.table:
        return table(path)

    from task3_scale import BruteForce
    try:
        from task3_scale import YourFinder
    except Exception:
        YourFinder = None

    rows = []
    for n in [int(x) for x in a.sizes.split(",")]:
        docs = build_docs(n)
        trace = not a.plain
        t_brute, c_brute, m_brute = timed_best_of(a.repeat, BruteForce, docs,
                                                  a.threshold, trace)

        row = {"n": n, "docs": len(docs), "repeat": a.repeat, "tracemalloc": trace,
               "brute_s": t_brute, "brute_calls": c_brute,
               "brute_peak_bytes": m_brute}

        if YourFinder is not None:
            try:
                t_lsh, c_lsh, m_lsh = timed_best_of(a.repeat, YourFinder, docs,
                                                    a.threshold, trace)
                row.update({"lsh_s": t_lsh, "lsh_calls": c_lsh,
                            "lsh_peak_bytes": m_lsh})
            except NotImplementedError:
                pass

        rows.append(row)
        line = f"  n={n:>6}  brute {t_brute:>8.2f}s  {c_brute:>12,} cmp"
        if "lsh_s" in row:
            line += f"   |  lsh {row['lsh_s']:>7.2f}s  {row['lsh_calls']:>9,} cmp"
        print(line, flush=True)

        # append after every size, so a run that is killed keeps what it had
        prior = json.load(open(path)) if os.path.exists(path) else {"runs": []}
        prior["machine"] = machine(a.note) if a.note else {**machine(), **{
            k: v for k, v in prior.get("machine", {}).items() if k == "note"}}
        prior["runs"].append(row)
        json.dump(prior, open(path, "w"), indent=2)

    total = len(json.load(open(path))["runs"])
    print(f"\n  -> out/crossover.json  ({total} measurement(s))")
    print("  Keep raising --sizes until something becomes unpleasant. Record where.")


if __name__ == "__main__":
    main()
