#!/usr/bin/env python3
"""Make a random k-SAT instance in WDIMACS format.

Handy for trying the solver without downloading the MSE17 benchmarks.
Around 4.26 clauses per variable is where random 3-SAT gets hardest.

    python experiments/generate_instance.py 200 852 -o examples/random3sat_200.wcnf
"""

import argparse
import random


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("nvars", type=int)
    ap.add_argument("nclauses", type=int)
    ap.add_argument("-k", type=int, default=3, help="literals per clause")
    ap.add_argument("-o", "--output", required=True)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    rng = random.Random(args.seed)
    with open(args.output, "w") as f:
        f.write(f"c random {args.k}-SAT, seed {args.seed}\n")
        f.write(f"p wcnf {args.nvars} {args.nclauses}\n")
        for _ in range(args.nclauses):
            variables = rng.sample(range(1, args.nvars + 1), args.k)
            lits = [v if rng.random() < 0.5 else -v for v in variables]
            f.write("1 " + " ".join(map(str, lits)) + " 0\n")


if __name__ == "__main__":
    main()
