import unittest

from ofjcheck.model import CONVENTION, COSMETIC, INFO, MEDIUM, REQUIRED, STRONG, WEAK, Evidence, Finding
from ofjcheck.report import author_message
from test_report import sample_report
from ofjcheck.verdict import decide, violations


def f(rule, kind, rng=(None, None), importance=INFO, reliability=STRONG, excludes=(None, None), advice=""):
    return Finding(rule, rule.lower(), kind=kind, importance=importance, reliability=reliability,
                   message="", evidence=[Evidence("x", "y")], implies_from=rng[0], implies_to=rng[1],
                   excludes_from=excludes[0], excludes_to=excludes[1], advice=advice)


BOLD = f("PDF03", "consistent", ("G07", None))
HEADER = f("PDF07", "consistent", ("G04", None))
REFS_NUMBER = f("PDF11", "consistent", reliability=WEAK, excludes=("G06", "G10"))
COPY_2026 = f("PDF09", "consistent", ("G10", None), reliability=WEAK)


class VerdictTest(unittest.TestCase):
    def test_violations(self):
        v = violations([BOLD, REFS_NUMBER])
        self.assertEqual(v[0], 3)                  # G01 contradicts the bold headings
        self.assertEqual(v[9], 1)                  # G10 is argued against by the links
        self.assertEqual(v[10], 0)

    def test_current(self):
        verdict = decide([BOLD, HEADER, REFS_NUMBER, COPY_2026], rules_run=1)
        self.assertEqual((verdict.kind, verdict.closest_generation, verdict.confidence),
                         ("current", "G11", "medium"))
        self.assertEqual(verdict.exit_code, 0)

    def test_current_but_indistinguishable(self):
        verdict = decide([BOLD], rules_run=1)
        self.assertEqual(verdict.kind, "current")
        self.assertEqual(verdict.confidence, "low")
        self.assertIn("cannot tell", verdict.explanation)

    def test_outdated_with_closest_generation(self):
        autoref = f("PDF11", "outdated", ("G07", "G10"), CONVENTION)
        year = f("PDF09", "outdated", ("G09", "G09"), COSMETIC, MEDIUM)
        verdict = decide([BOLD, HEADER, autoref, year], rules_run=1)
        self.assertEqual((verdict.kind, verdict.closest_generation, verdict.range_from, verdict.range_to),
                         ("outdated", "G09", "G09", "G09"))
        self.assertEqual(verdict.confidence, "high")
        self.assertEqual(verdict.triggers[0], "PDF11: pdf11")
        self.assertTrue(verdict.triggers[1].startswith("(minor)"))
        self.assertEqual(verdict.exit_code, 1)

    def test_cosmetic_alone_is_not_outdated(self):          # decision D3
        year = f("PDF09", "outdated", ("G09", "G09"), COSMETIC, MEDIUM)
        verdict = decide([BOLD, HEADER, REFS_NUMBER, year], rules_run=1)
        self.assertEqual(verdict.kind, "current")
        self.assertIn("minor differences", verdict.headline)

    def test_mixed_versions(self):
        old_class = f("CLS00", "outdated", ("G04", "G06"), REQUIRED)
        new_title = f("SRC18", "consistent", ("G09", None))
        verdict = decide([old_class, new_title], rules_run=1)
        self.assertEqual(verdict.kind, "outdated")
        self.assertIn("mixed", verdict.headline)
        self.assertEqual(verdict.confidence, "medium")

    def test_not_template_wins(self):
        verdict = decide([f("NOT02", "not-template", importance=REQUIRED), BOLD], rules_run=1)
        self.assertEqual((verdict.kind, verdict.exit_code), ("not-template", 2))
        self.assertEqual(verdict.confidence, "medium")         # some template evidence exists

    def test_modified(self):
        mod = f("CLS01", "modified", importance=REQUIRED)
        verdict = decide([BOLD, HEADER, REFS_NUMBER, mod], rules_run=1)
        self.assertEqual((verdict.kind, verdict.exit_code), ("modified", 1))

    def test_inconclusive_and_remarks(self):
        self.assertEqual(decide([], rules_run=0).kind, "inconclusive")
        self.assertEqual(decide([], rules_run=2).kind, "inconclusive")
        anon = f("PDF14", "anonymity", importance=REQUIRED)
        verdict = decide([BOLD, anon], rules_run=1)
        self.assertTrue(verdict.remarks[0].startswith("NOT ANONYMOUS"))

    def test_author_message(self):
        report = sample_report()
        msg = "\n".join(author_message(report))
        self.assertIn("Dear authors", msg)
        self.assertIn("Fig.~\\ref", msg)
        report.findings = []
        self.assertEqual(author_message(report), [])


if __name__ == "__main__":
    unittest.main()
