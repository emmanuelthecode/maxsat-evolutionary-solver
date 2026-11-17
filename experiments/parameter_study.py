#!/usr/bin/env python3
"""Parameter study: how population size, mutation rate and crossover rate
affect the number of satisfied clauses.

One parameter is varied at a time, the other two stay at the baseline
(pop 100, mutation 1/n, crossover 0.9). Every setting is repeated on every
instance and the results are saved to CSV and drawn as boxplots.

    python experiments/parameter_study.py instances/*.wcnf --reps 100 --budget 0.2

This is the setup I used for the report (100 reps, 0.2s budget, three
MSE17 instances). A full run takes a while: 3 params x 3 values x 100 reps
x 0.2s is about 3 minutes of search per instance, plus file loading.
"""

import argparse
import csv
import os
import random
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from maxsat import load_file, evo_maxsat  # noqa: E402

BASELINE = {"pop_size": 100, "mut_factor": 1.0, "cross_rate": 0.9}

SWEEPS = {
    "population_size": ("pop_size", [50, 100, 200]),
    "mutation_rate": ("mut_factor", [0.5, 1.0, 2.0]),     # multiples of 1/n
    "crossover_rate": ("cross_rate", [0.6, 0.8, 0.95]),
}


def label(param, value):
    return f"{value}/nvars" if param == "mutation_rate" else str(value)


def run_setting(nvars, clauses, settings, reps, budget):
    out = []
    for _ in range(reps):
        _, nsat, _ = evo_maxsat(nvars, clauses, budget,
                                pop_size=settings["pop_size"],
                                cross_rate=settings["cross_rate"],
                                mut_rate=settings["mut_factor"] / nvars)
        out.append(nsat)
    return out


def boxplot(param, instance, groups, path):
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.boxplot(list(groups.values()), tick_labels=list(groups.keys()))
    ax.set_title(f"{param} on {instance}")
    ax.set_xlabel(param)
    ax.set_ylabel("Satisfied clauses (nsat)")
    fig.tight_layout()
    fig.savefig(path, dpi=100)
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("instances", nargs="+", help="WDIMACS files")
    ap.add_argument("--reps", type=int, default=100)
    ap.add_argument("--budget", type=float, default=0.2, help="seconds per repetition")
    ap.add_argument("--out", default="results")
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    random.seed(args.seed)
    os.makedirs(args.out, exist_ok=True)
    csv_path = os.path.join(args.out, "results.csv")

    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["instance", "parameter", "value", "rep", "nsat"])

        for path in args.instances:
            name = os.path.basename(path)
            nvars, clauses = load_file(path)
            print(f"{name}: {nvars} variables, {len(clauses)} clauses")

            for param, (key, values) in SWEEPS.items():
                groups = {}
                for v in values:
                    settings = dict(BASELINE, **{key: v})
                    scores = run_setting(nvars, clauses, settings, args.reps, args.budget)
                    groups[label(param, v)] = scores
                    for i, s in enumerate(scores):
                        writer.writerow([name, param, v, i, s])
                    med = sorted(scores)[len(scores) // 2]
                    print(f"  {param:16s} {label(param, v):>10s}  median nsat {med}")

                stem = os.path.splitext(name)[0]
                boxplot(param, name, groups, os.path.join(args.out, f"{param}_{stem}.png"))

    print(f"\nsaved {csv_path} and boxplots to {args.out}/")


if __name__ == "__main__":
    main()
