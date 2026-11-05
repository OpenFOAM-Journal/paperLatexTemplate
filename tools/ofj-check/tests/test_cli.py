import contextlib
import importlib.util
import io
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from helpers import MAIN_TEX, commit, init_repo, write_files, write_minimal_pdf

from ofjcheck.cli import main
from ofjcheck.model import EXIT_ENVIRONMENT, EXIT_INPUT

HAS_PDFPLUMBER = importlib.util.find_spec("pdfplumber") is not None


def run(*argv):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = main([str(a) for a in argv])
    return code, out.getvalue(), err.getvalue()


@unittest.skipUnless(shutil.which("git"), "git not installed")
class CliTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.template = init_repo(self.tmp / "template")
        commit(self.template, {"ofj.cls": "v1\n"}, "template")

    def tearDown(self):
        self._tmp.cleanup()

    @unittest.skipUnless(HAS_PDFPLUMBER, "pdfplumber not installed")
    def test_check_deps(self):
        code, out, _ = run("--check-deps")
        self.assertEqual(code, 0)
        self.assertIn("All required dependencies are available", out)

    @unittest.skipUnless(HAS_PDFPLUMBER, "pdfplumber not installed")
    def test_pdf_run_writes_reports(self):
        pdf = write_minimal_pdf(self.tmp / "paper.pdf")
        md, js = self.tmp / "r.md", self.tmp / "r.json"
        code, out, _ = run(pdf, "--template-dir", self.template, "--report", md, "--json", js)
        self.assertEqual(code, 2)                         # a blank page is not the OFJ template
        self.assertRegex(out, r"Page size\s+A4")
        self.assertRegex(out, r"Producer\s+pdfTeX")
        self.assertIn("# OFJ template check: paper.pdf", md.read_text(encoding="utf-8"))
        data = json.loads(js.read_text(encoding="utf-8"))
        self.assertEqual(data["submission"]["mode"], "pdf")
        # the toy template lacks the catalogue commit, which must be reported
        self.assertTrue(any("not in this template repository" in w for w in data["warnings"]))

    def test_latex_only_run_needs_no_pdf_library(self):
        write_files(self.tmp / "src", {"paper.tex": MAIN_TEX})
        code, out, _ = run(self.tmp / "src", "--template-dir", self.template, "-q")
        self.assertEqual(code, 1)                         # bare ofj document: no review mode etc.
        self.assertTrue(out.startswith("outdated:"))

    def test_input_error(self):
        code, _, err = run(self.tmp / "missing.pdf", "--template-dir", self.template)
        self.assertEqual(code, EXIT_INPUT)
        self.assertIn("does not exist", err)

    def test_offline_without_cache(self):
        write_files(self.tmp / "src", {"paper.tex": MAIN_TEX})
        code, _, err = run(self.tmp / "src", "--offline", "--cache-dir", self.tmp / "empty-cache")
        self.assertEqual(code, EXIT_ENVIRONMENT)
        self.assertIn("no cached copy", err)


if __name__ == "__main__":
    unittest.main()
