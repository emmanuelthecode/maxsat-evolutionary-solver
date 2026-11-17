#!/usr/bin/env python3
"""Evolutionary algorithm for unweighted MAXSAT.

Three modes, picked with -question:

  1  check whether one clause is satisfied by an assignment
  2  load a WDIMACS file and count satisfied clauses for an assignment
  3  run the EA with a time budget, once per repetition

The CLI matches the format the coursework marker expected, so outputs are
tab-separated and nothing else gets printed.
"""

import argparse
import random
import time


# ---------------------------------------------------------------------------
# Clauses and instances
# ---------------------------------------------------------------------------

def parse_clause(clause):
    """'w l1 l2 ... 0' -> [l1, l2, ...]. The leading weight is ignored."""
    lits = []
    for tok in clause.split()[1:]:
        n = int(tok)
        if n == 0:
            break
        lits.append(n)
    return lits


def sat_clause(clause, bits):
    """1 if the clause string is satisfied by the bitstring, else 0."""
    for lit in parse_clause(clause):
        i = abs(lit) - 1
        if lit > 0 and bits[i] == '1':
            return 1
        if lit < 0 and bits[i] == '0':
            return 1
    return 0


def load_file(path):
    """Read a WDIMACS file. Returns (number of variables, list of clauses)."""
    clauses = []
    nvars = 0

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("c"):
                continue
            if line.startswith("p"):
                nvars = int(line.split()[2])
                continue
            clauses.append(parse_clause(line))

    return nvars, clauses


def count_sat(path, bits):
    _, clauses = load_file(path)
    return fit(bits, clauses)


# ---------------------------------------------------------------------------
# Evolutionary algorithm
# ---------------------------------------------------------------------------

def fit(bits, clauses):
    """Fitness = number of satisfied clauses."""
    score = 0
    for clause in clauses:
        for lit in clause:
            i = abs(lit) - 1
            if (lit > 0 and bits[i] == '1') or (lit < 0 and bits[i] == '0'):
                score += 1
                break
    return score


def rand_bits(n):
    return ''.join(random.choice('01') for _ in range(n))


def pick(pop, scores, k=3):
    """Tournament selection of size k."""
    best = random.randrange(len(pop))
    for _ in range(k - 1):
        j = random.randrange(len(pop))
        if scores[j] > scores[best]:
            best = j
    return pop[best]


def cross(a, b):
    """One-point crossover."""
    if len(a) < 2:
        return a, b
    cut = random.randint(1, len(a) - 1)
    return a[:cut] + b[cut:], b[:cut] + a[cut:]


def mut(bits, rate):
    """Flip each bit independently with probability `rate`."""
    out = list(bits)
    for i in range(len(out)):
        if random.random() < rate:
            out[i] = '0' if out[i] == '1' else '1'
    return ''.join(out)


def evo_maxsat(nvars, clauses, tlim, pop_size=100, cross_rate=0.9, mut_rate=None):
    """Run the EA until `tlim` seconds have passed.

    Returns (t, nsat, xbest) where t = generations * population size.
    """
    if mut_rate is None:
        mut_rate = 1.0 / nvars

    pop = [rand_bits(nvars) for _ in range(pop_size)]
    scores = [fit(x, clauses) for x in pop]

    best_i = max(range(pop_size), key=lambda i: scores[i])
    best, best_score = pop[best_i], scores[best_i]

    gens = 0
    start = time.perf_counter()

    while time.perf_counter() - start < tlim:
        new_pop = [best]   # elitism: the best-so-far always survives

        while len(new_pop) < pop_size:
            p1 = pick(pop, scores)
            p2 = pick(pop, scores)

            if random.random() < cross_rate:
                c1, c2 = cross(p1, p2)
            else:
                c1, c2 = p1, p2

            new_pop.append(mut(c1, mut_rate))
            if len(new_pop) < pop_size:
                new_pop.append(mut(c2, mut_rate))

        pop = new_pop
        scores = [fit(x, clauses) for x in pop]
        gens += 1

        gen_best_i = max(range(pop_size), key=lambda i: scores[i])
        if scores[gen_best_i] > best_score:
            best_score = scores[gen_best_i]
            best = pop[gen_best_i]

    return gens * pop_size, best_score, best


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("-question", type=int, required=True, choices=[1, 2, 3])
    ap.add_argument("-clause", type=str)
    ap.add_argument("-assignment", type=str)
    ap.add_argument("-wdimacs", type=str)
    ap.add_argument("-time_budget", type=float)
    ap.add_argument("-repetitions", type=int)

    # tuning knobs (used for the parameter study)
    ap.add_argument("-pop_size", type=int, default=100)
    ap.add_argument("-cross_rate", type=float, default=0.9)
    ap.add_argument("-mut_rate", type=float, default=None)

    args = ap.parse_args()

    if args.question == 1:
        print(sat_clause(args.clause, args.assignment))

    elif args.question == 2:
        print(count_sat(args.wdimacs, args.assignment))

    elif args.question == 3:
        nvars, clauses = load_file(args.wdimacs)
        for _ in range(args.repetitions):
            t, nsat, xbest = evo_maxsat(nvars, clauses, args.time_budget,
                                        pop_size=args.pop_size,
                                        cross_rate=args.cross_rate,
                                        mut_rate=args.mut_rate)
            print(f"{t}\t{nsat}\t{xbest}")


if __name__ == "__main__":
    main()
