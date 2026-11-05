"""PDF rules on the reference PDFs of every template generation, and on negative samples.

The reference PDFs (research/reference_pdfs) and a clone of the real template are needed;
tests are skipped when either is missing.
"""
import importlib.util
import re
import tempfile
import unittest
from pathlib import Path

from helpers import NEGATIVE_PDFS, REFERENCE_PDFS, find_template_repo, write_minimal_pdf

from ofjcheck import generations
from ofjcheck.analyze import run_checks
from ofjcheck.inputs import detect_submission
from ofjcheck.template_repo import obtain_template

HAS_PDFPLUMBER = importlib.util.find_spec("pdfplumber") is not None
REPO = find_template_repo()
REFERENCES = sorted(REFERENCE_PDFS.glob("G*.pdf")) if REFERENCE_PDFS.exists() else []


def generation_of(pdf: Path) -> str:
    return re.match(r"(G\d\d)", pdf.name).group(1)


@unittest.skipUnless(HAS_PDFPLUMBER and REPO, "needs pdfplumber and a clone of the OFJ template")
class PdfRulesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.repo, cls.status = obtain_template(template_dir=Path(REPO))
        cls._cache = {}

    def report(self, pdf: Path):
        if pdf not in self._cache:
            with detect_submission(pdf) as sub:
                self._cache[pdf] = run_checks(sub, self.repo, self.status)
        return self._cache[pdf]

    def findings(self, pdf: Path):
        return self.report(pdf).findings

    @unittest.skipUnless(REFERENCES, "reference PDFs not available")
    def test_verdicts_of_reference_pdfs(self):
        for pdf in REFERENCES:
            gen = generation_of(pdf)
            with self.subTest(pdf=pdf.name):
                v = self.report(pdf).verdict
                expected = "current" if gen == generations.CURRENT else "outdated"
                self.assertEqual(v.kind, expected, v.headline)
                lo = generations.index(v.range_from)
                hi = generations.index(v.range_to) if v.range_to else len(generations.GENERATIONS) - 1
                self.assertTrue(lo <= generations.index(gen) <= hi, f"{v.range_from}-{v.range_to}")
                self.assertEqual(v.confidence, "high" if expected == "outdated" else "medium")

    @unittest.skipUnless((NEGATIVE_PDFS / "article_class_same_content.pdf").exists(), "negative sample missing")
    def test_verdict_not_template(self):
        v = self.report(NEGATIVE_PDFS / "article_class_same_content.pdf").verdict
        self.assertEqual((v.kind, v.confidence, v.exit_code), ("not-template", "high", 2))

    @unittest.skipUnless(REFERENCES, "reference PDFs not available")
    def test_reference_pdfs_point_to_their_own_generation(self):
        for pdf in REFERENCES:
            gen = generation_of(pdf)
            with self.subTest(pdf=pdf.name):
                for f in self.findings(pdf):
                    self.assertNotEqual(f.kind, "not-template", f.title)
                    if f.excludes_from or f.excludes_to:
                        lo, hi = generations.index(f.excludes_from), generations.index(f.excludes_to)
                        self.assertFalse(lo <= generations.index(gen) <= hi, f"{f.rule_id} excludes {gen}")
                    if f.implies_from is None and f.implies_to is None:
                        continue
                    lo = generations.index(f.implies_from) if f.implies_from else 0
                    hi = generations.index(f.implies_to) if f.implies_to else len(generations.GENERATIONS) - 1
                    self.assertTrue(lo <= generations.index(gen) <= hi,
                                    f"{f.rule_id} '{f.title}' -> {generations.describe(f.implies_from, f.implies_to)}")

    @unittest.skipUnless(REFERENCES, "reference PDFs not available")
    def test_current_review_build_is_clean(self):
        pdf = next(p for p in REFERENCES if p.name.startswith(generations.CURRENT) and "review" in p.name)
        bad = [f.title for f in self.findings(pdf) if f.kind not in ("consistent", "info")]
        self.assertEqual(bad, [])

    @unittest.skipUnless(REFERENCES, "reference PDFs not available")
    def test_every_older_generation_is_detected_from_the_pdf(self):
        for pdf in REFERENCES:
            if generation_of(pdf) == generations.CURRENT:
                continue
            with self.subTest(pdf=pdf.name):
                self.assertTrue([f for f in self.findings(pdf) if f.kind == "outdated"])

    @unittest.skipUnless(REFERENCES, "reference PDFs not available")
    def test_anonymity(self):
        for pdf in REFERENCES:
            gen = generation_of(pdf)
            with self.subTest(pdf=pdf.name):
                leaks = [f for f in self.findings(pdf) if f.kind == "anonymity"]
                if "review" in pdf.name or gen == "G01":       # G01 had its authors commented out
                    self.assertEqual(leaks, [])
                else:
                    self.assertEqual(len(leaks), 1)
                    self.assertTrue(any("Email address" in e.excerpt or "orcid" in e.excerpt
                                        for e in leaks[0].evidence))

    @unittest.skipUnless((NEGATIVE_PDFS / "article_class_same_content.pdf").exists(), "negative sample missing")
    def test_article_class_is_not_the_template(self):
        findings = self.findings(NEGATIVE_PDFS / "article_class_same_content.pdf")
        self.assertEqual([f.rule_id for f in findings], ["NOT02"])
        self.assertIn("0 of the 5 elements", findings[0].message)

    def test_word_processor_pdf(self):
        with tempfile.TemporaryDirectory() as tmp:
            pdf = write_minimal_pdf(Path(tmp) / "paper.pdf", producer="Microsoft\\256 Word for Microsoft 365",
                                    creator="Microsoft\\256 Word", lines=["A study with OpenFOAM",
                                                                         "Abstract. We simulate.",
                                                                         "1. Introduction"])
            findings = self.findings(pdf)
        ids = sorted(f.rule_id for f in findings)
        self.assertIn("NOT02", ids)
        self.assertIn("NOT01", ids)
        self.assertTrue(all(f.kind in ("not-template", "modified") for f in findings))


@unittest.skipUnless(HAS_PDFPLUMBER, "pdfplumber not installed")
class PdfVersionMarkerTest(unittest.TestCase):
    def test_marker_in_metadata(self):
        import pdfplumber
        from ofjcheck.pdf_rules import rule_pdf_version_marker
        from ofjcheck.pdf_view import PdfView
        for value, kind in (("G09", "outdated"), ("G11", "consistent"), ("2099.1", "info")):
            with self.subTest(value=value), tempfile.TemporaryDirectory() as tmp:
                pdf = write_minimal_pdf(Path(tmp) / "p.pdf", info=f"/Keywords (OFJ-template-version: {value})")
                with pdfplumber.open(str(pdf)) as doc:
                    findings = rule_pdf_version_marker(PdfView(doc))
                self.assertEqual([f.kind for f in findings], [kind])

    def test_no_marker(self):
        import pdfplumber
        from ofjcheck.pdf_rules import rule_pdf_version_marker
        from ofjcheck.pdf_view import PdfView
        with tempfile.TemporaryDirectory() as tmp:
            pdf = write_minimal_pdf(Path(tmp) / "p.pdf", info="/Keywords (OpenFOAM, CFD)")
            with pdfplumber.open(str(pdf)) as doc:
                self.assertEqual(rule_pdf_version_marker(PdfView(doc)), [])


if __name__ == "__main__":
    unittest.main()
