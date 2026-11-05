"""Production versions, style findings and verdict refinements, learned from checking real
submissions. Synthetic data only."""
import unittest

from ofjcheck.filematch import normalise, production_data
from ofjcheck.model import CONVENTION, COSMETIC, INFO, MEDIUM, REQUIRED, STRONG, WEAK, Evidence, Finding
from ofjcheck.pdf_rules import rule_production_pdf
from ofjcheck.verdict import apply_context, channel_range, decide

CLASS = r"""\issueinfo{2 [Enter correct Journal Section here]}% volume number%JN: change  this number
  {1}%        % issue number
  {Xxxx}%     % month
  {XXXX}%     % year
\pagespan{1}{999}%JN: change  these values
\ifx\@classname\@tempb
  \newcommand{\datename}{\textit{Date}:}
\else
  \newcommand{\datename}{$^{*}$ Corresponding author\par Received: 14 Juntember 2022, Accepted: 29 Januaril 2022, Published: 17 Decemby 2022}%JN: change dates here
\fi
\def\section{\@startsection{section}{1}{\normalfont\bf\centering}}
"""
PRODUCTION = (CLASS.replace("2 [Enter correct Journal Section here]", "7 [Full Papers]")
              .replace(r"\pagespan{1}{999}", r"\pagespan{12}{30}")
              .replace("Received: 14 Juntember 2022, Accepted: 29 Januaril 2022, Published: 17 Decemby 2022",
                       "Received: 1 May 2026, Accepted: 2 June 2026, Published: 3 July 2026"))


def f(rule, kind, rng=(None, None), importance=INFO, reliability=STRONG, title=None):
    return Finding(rule, title or rule.lower(), kind=kind, importance=importance, reliability=reliability,
                   message="", evidence=[Evidence("x", "y")], implies_from=rng[0], implies_to=rng[1],
                   advice="do something")


class ProductionTest(unittest.TestCase):
    def test_production_data(self):
        self.assertEqual(production_data(CLASS), {})
        self.assertEqual(production_data(PRODUCTION),
                         {"volume": "7 [Full Papers]", "pages": "12-30", "received": "1 May 2026",
                          "accepted": "2 June 2026", "published": "3 July 2026"})

    def test_editorial_lines_ignored_only_on_request(self):
        a, b = CLASS.encode(), PRODUCTION.encode()
        self.assertNotEqual(normalise(a, "ofjart.cls"), normalise(b, "ofjart.cls"))
        self.assertEqual(normalise(a, "ofjart.cls", editorial=True), normalise(b, "ofjart.cls", editorial=True))
        changed = PRODUCTION.replace("\\bf\\centering", "\\scshape\\centering").encode()
        self.assertNotEqual(normalise(a, "ofjart.cls", editorial=True),
                            normalise(changed, "ofjart.cls", editorial=True))

    def test_production_title_page(self):
        class View:
            def __init__(self, text):
                self.text = text

            def compact(self, i):
                return self.text

            def find_line(self, i, pattern):
                return None

        placeholder = "Volume2[EntercorrectJournalSectionhere],Pages1–999 Received:14Juntember2022,"
        self.assertEqual(rule_production_pdf(View(placeholder)), [])
        real = "Volume7[FullPapers],Pages12–30 ... Received:1May2026,Accepted:2June2026,Published:3July2026"
        found = rule_production_pdf(View(real))
        self.assertEqual(found[0].kind, "production")
        self.assertIn("published 3 July 2026", found[0].message)

    def test_context_in_production_versions(self):
        anon = f("PDF14", "anonymity", importance=REQUIRED)
        year = f("PDF09", "outdated", ("G09", "G09"), COSMETIC, MEDIUM, title="Copyright year 2024")
        findings = [anon, year]
        apply_context(findings)                      # no production finding: unchanged
        self.assertEqual((anon.kind, year.kind), ("anonymity", "outdated"))
        findings.append(f("PRD02", "production"))
        apply_context(findings)
        self.assertEqual((anon.kind, anon.importance, anon.advice), ("info", INFO, ""))
        self.assertEqual((year.kind, year.implies_from), ("info", None))
        verdict = decide(findings + [f("PDF03", "consistent", ("G07", None))], rules_run=1)
        self.assertTrue(verdict.remarks[0].startswith("PRODUCTION VERSION"))
        self.assertFalse(any("NOT ANONYMOUS" in r for r in verdict.remarks))


class VerdictRefinementTest(unittest.TestCase):
    def test_style_findings_are_minor(self):
        style = f("PDF12", "style", importance=CONVENTION, reliability=MEDIUM)
        verdict = decide([f("PDF03", "consistent", ("G07", None)), style], rules_run=1)
        self.assertEqual(verdict.kind, "current")
        self.assertIn("(minor) PDF12: pdf12", verdict.triggers)

    def test_outdated_verdict_names_modifications(self):
        verdict = decide([f("SRC10", "outdated", ("G01", "G05"), CONVENTION, MEDIUM),
                          f("CLS01", "modified", importance=REQUIRED)], rules_run=1)
        self.assertTrue(verdict.headline.endswith(", modified"))
        self.assertIn("CLS01: cls01", verdict.triggers)

    def test_weak_signals_do_not_split_channels(self):
        weak_only = [f("PDF03", "consistent", ("G07", None)),
                     Finding("PDF11", "x", kind="consistent", importance=INFO, reliability=WEAK, message="",
                             excludes_from="G06", excludes_to="G10")]
        self.assertEqual(channel_range(weak_only), (6, 10))     # G07..G11: the weak exclusion is ignored


if __name__ == "__main__":
    unittest.main()
