import os
import random
import subprocess
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from maxsat import parse_clause, sat_clause, load_file, count_sat, fit, cross, mut, evo_maxsat  # noqa: E402

EXAMPLE = os.path.join(ROOT, "examples", "example.wcnf")


def cli(*args):
    out = subprocess.run([sys.executable, os.path.join(ROOT, "maxsat.py"), *args],
                         capture_output=True, text=True, check=True)
    return out.stdout.strip()


# Exercise 1 ---------------------------------------------------------------

def test_parse_clause_ignores_weight_and_terminator():
    assert parse_clause("0.5 2 1 -3 -4 0") == [2, 1, -3, -4]


@pytest.mark.parametrize("assignment, expected", [("0000", 1), ("0011", 0), ("0100", 1)])
def test_sat_clause(assignment, expected):
    assert sat_clause("0.5 2 1 -3 -4 0", assignment) == expected


def test_question_1_cli():
    assert cli("-question", "1", "-clause", "0.5 2 1 -3 -4 0", "-assignment", "0000") == "1"
    assert cli("-question", "1", "-clause", "0.5 2 1 -3 -4 0", "-assignment", "0011") == "0"


# Exercise 2 ---------------------------------------------------------------

def test_load_file():
    nvars, clauses = load_file(EXAMPLE)
    assert nvars == 4
    assert clauses == [[1, 2, 3, 4], [-1, -2, 3, -4]]


@pytest.mark.parametrize("assignment, expected", [("0000", 1), ("0001", 2), ("1101", 1), ("0010", 2)])
def test_count_sat(assignment, expected):
    assert count_sat(EXAMPLE, assignment) == expected


def test_question_2_cli():
    assert cli("-question", "2", "-wdimacs", EXAMPLE, "-assignment", "0001") == "2"


# Exercise 3 ---------------------------------------------------------------

def test_operators_keep_length_and_alphabet():
    random.seed(0)
    a, b = "0" * 20, "1" * 20
    c1, c2 = cross(a, b)
    assert len(c1) == len(c2) == 20
    assert c1.count("1") + c2.count("1") == 20       # crossover just swaps material
    m = mut(a, 1.0)
    assert m == "1" * 20                              # rate 1 flips everything


def test_ea_solves_small_instance():
    random.seed(1)
    nvars, clauses = load_file(EXAMPLE)
    t, nsat, xbest = evo_maxsat(nvars, clauses, 0.1)
    assert nsat == 2 == fit(xbest, clauses)
    assert t > 0 and t % 100 == 0


def test_question_3_output_format():
    lines = cli("-question", "3", "-wdimacs", EXAMPLE, "-time_budget", "0.05", "-repetitions", "3").splitlines()
    assert len(lines) == 3
    for line in lines:
        t, nsat, x = line.split("\t")
        assert int(t) > 0 and int(nsat) == 2 and set(x) <= {"0", "1"} and len(x) == 4
