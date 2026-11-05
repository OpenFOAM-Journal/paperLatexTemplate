"""The template generations of docs/FINGERPRINTS.md, section 2, as data.

To add a generation when the template changes: append an entry, move
CURRENT to it, and set CATALOGUE_COMMIT to the newest template commit that
the catalogue has been checked against.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from typing import List, Optional, Tuple

# Newest template commit (master, first parent) that the catalogue covers.
CATALOGUE_COMMIT = "cd2b7f280daab59828fd67c99919726d87f49847"


@dataclass(frozen=True)
class Generation:
    id: str
    first: str              # first commit of the generation on master (first parent)
    start: str              # date it landed on master
    end: Optional[str]      # last day it was current; None = still current
    commit: str             # representative commit (reference PDF)
    title: str
    summary: str


GENERATIONS: List[Generation] = [
    Generation("G01", "b1d669b", "2021-04-28", "2021-08-29", "eb037cd", "Initial template",
               "US Letter, narrow AMS margins, copyright 'OpenFOAM Journal'"),
    Generation("G02", "15fc5c2", "2021-08-30", "2022-03-01", "b5edfcf", "A4",
               "A4 with 2.5 cm margins, black links, 'Received: 14 Juntember 2022' placeholder, ISSN TBD"),
    Generation("G03", "62dec8d", "2022-03-02", "2022-05-03", "f532bdd", "CC BY-SA",
               "Copyright 'The Authors ... CC BY-SA 4.0', cite package"),
    Generation("G04", "48b3c92", "2022-05-04", "2022-11-07", "029028a", "ISSN",
               "ISSN 2753-8168, 'Volume 2 [Enter correct Journal Section here]', vector logo"),
    Generation("G05", "8647056", "2022-11-08", "2023-01-29", "e88d246", "Makefile and review mode",
               "Makefile, numbered footnotes, review mode, \\autoref with default names"),
    Generation("G06", "d69512b", "2023-01-30", "2023-02-07", "f004fab", "parts/ split",
               "Sections in parts/, examples.tex, line numbers only in review mode"),
    Generation("G07", "3178e65", "2023-02-08", "2023-04-29", "0fc4ddf", "Bold headings",
               "Class files in today's state: bold headings, mixed-case authors, "
               "'Results with version(s)'; \\autoref as Tab./Fig./Eqn.; \\xspace"),
    Generation("G08", "4f17267", "2023-04-30", "2025-01-10", "4f17267", "Author contributions inline",
               "Author contributions moved into the main file"),
    Generation("G09", "431cc52", "2025-01-11", "2026-01-01", "e489934", "Title case",
               "'Use Title Case' title placeholder, copyright 2024"),
    Generation("G10", "66b2f6a", "2026-01-02", "2026-03-30", "66b2f6a", "Copyright 2026",
               "Copyright year 2026"),
    Generation("G11", "cd2b7f2", "2026-03-31", None, "cd2b7f2", "\\ref conventions",
               "\\autoref replaced by Eqn.~\\ref, Tab.~\\ref, Fig.~\\ref, Lst.~\\ref"),
]

CURRENT = GENERATIONS[-1].id
_INDEX = {g.id: i for i, g in enumerate(GENERATIONS)}


def by_id(gen_id: str) -> Generation:
    return GENERATIONS[_INDEX[gen_id]]


def index(gen_id: str) -> int:
    return _INDEX[gen_id]


def span(first: Optional[str], last: Optional[str]) -> List[Generation]:
    """Generations from ``first`` to ``last`` inclusive (None = open end)."""
    lo = index(first) if first else 0
    hi = index(last) if last else len(GENERATIONS) - 1
    return GENERATIONS[lo:hi + 1]


def commit_generations(first_parent: List[Tuple[str, str]]) -> List[str]:
    """Generation of each commit in a first-parent history [(sha, date), ...], oldest first.

    Generations start at their ``first`` commit; commits after the newest one belong to it.
    If a start commit is missing (rewritten history), dates are used instead."""
    starts = {}
    for g in GENERATIONS:
        pos = next((i for i, (sha, _) in enumerate(first_parent) if sha.startswith(g.first)), None)
        if pos is None:
            return [for_period(day, None)[0] for _, day in first_parent]
        starts[pos] = g.id
    result, current = [], GENERATIONS[0].id
    for i in range(len(first_parent)):
        current = starts.get(i, current)
        result.append(current)
    return result


def includes_current(first: Optional[str], last: Optional[str]) -> bool:
    return last is None or last == CURRENT


def for_period(start: str, end_exclusive: Optional[str]) -> Tuple[str, Optional[str]]:
    """Generations during which something valid from ``start`` until ``end_exclusive``
    (ISO dates; None = still valid) was on master. Returns (first, last); last None = current."""
    d0 = date.fromisoformat(start)
    d1 = date.fromisoformat(end_exclusive) - timedelta(days=1) if end_exclusive else None
    if d1 is not None and d1 < d0:
        d1 = d0                                  # replaced on the same day it landed
    hits = [g for g in GENERATIONS
            if (d1 is None or date.fromisoformat(g.start) <= d1)
            and (g.end is None or date.fromisoformat(g.end) >= d0)]
    if not hits:
        return GENERATIONS[0].id, GENERATIONS[0].id
    last = hits[-1]
    return hits[0].id, (None if last.end is None and d1 is None else last.id)


def describe(first: Optional[str], last: Optional[str]) -> str:
    gens = span(first, last)
    if not gens:
        return "no known generation"
    a, b = gens[0], gens[-1]
    period = f"{a.start} to {b.end or 'today'}"
    return f"{a.id}" + (f"-{b.id}" if b is not a else "") + f" ({period})"
