"""PDF + sources submitted together: is the PDF made from these sources?"""
import importlib.util
import io
import shutil
import subprocess
import tarfile
import tempfile
import unittest
from pathlib import Path

from helpers import REFERENCE_PDFS, find_template_repo

from ofjcheck.analyze import run_checks
from ofjcheck.inputs import detect_submission
from ofjcheck.template_repo import obtain_template

REPO = find_template_repo()
G11_PDF = REFERENCE_PDFS / "G11_2026-03-31_cd2b7f2_review.pdf"
G05_PDF = REFERENCE_PDFS / "G05_2022-12-27_e88d246_review.pdf"


@unittest.skipUnless(REPO and importlib.util.find_spec("pdfplumber") and G11_PDF.exists() and G05_PDF.exists(),
                     "needs pdfplumber, a template clone and the reference PDFs")
class CrossCheckTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.repo, cls.status = obtain_template(template_dir=Path(REPO))

    def check(self, pdf: Path, title: str = None):
        git_dir = Path(REPO) / ".git" if (Path(REPO) / ".git").exists() else Path(REPO)
        data = subprocess.run(["git", f"--git-dir={git_dir}", "archive", "cd2b7f2"],
                              check=True, capture_output=True).stdout
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with tarfile.open(fileobj=io.BytesIO(data)) as tf:
                for m in tf.getmembers():
                    if m.isfile():
                        (root / m.name).parent.mkdir(parents=True, exist_ok=True)
                        (root / m.name).write_bytes(tf.extractfile(m).read())
            if title:
                main = root / "ofj-template.tex"
                text = main.read_text(encoding="utf-8").replace(
                    "{\\OF Journal Publication - Use Title Case}", "{" + title + "}")
                main.write_text(text, encoding="utf-8")
            shutil.copy(pdf, root / "paper-review.pdf")
            with detect_submission(root, pdf=Path("paper-review.pdf")) as sub:
                self.assertEqual(sub.mode, "both")
                return run_checks(sub, self.repo, self.status)

    def test_matching_pdf_and_sources(self):
        report = self.check(G11_PDF)
        self.assertEqual([f.rule_id for f in report.findings if f.rule_id.startswith("XCHK")], [])
        self.assertEqual(report.verdict.kind, "current")

    def test_pdf_from_older_template(self):
        report = self.check(G05_PDF)
        self.assertIn("XCHK02", [f.rule_id for f in report.findings])
        self.assertEqual(report.verdict.kind, "outdated")
        self.assertTrue(any("different template generations" in r for r in report.verdict.remarks))

    def test_pdf_with_another_title(self):
        report = self.check(G11_PDF, title="Turbulent Combustion Modelling of Hydrogen Flames")
        self.assertIn("XCHK01", [f.rule_id for f in report.findings])


if __name__ == "__main__":
    unittest.main()
