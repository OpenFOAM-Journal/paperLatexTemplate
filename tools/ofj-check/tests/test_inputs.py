import io
import tarfile
import tempfile
import unittest
import zipfile
from pathlib import Path

from helpers import MAIN_TEX, write_files, write_minimal_pdf

from ofjcheck.inputs import InputError, detect_submission, document_class


class InputDetectionTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def test_pdf_only(self):
        pdf = write_minimal_pdf(self.tmp / "paper.pdf")
        sub = detect_submission(pdf)
        self.assertEqual(sub.mode, "pdf")
        self.assertEqual(sub.pdf, pdf.resolve())
        self.assertIsNone(sub.main_tex)

    def test_folder_with_sources_and_pdf_prefers_manuscript_over_figures(self):
        write_files(self.tmp, {"paper.tex": MAIN_TEX,
                               "paper-review.tex": "\\def\\review{1} \\input{paper.tex}\n",
                               "parts/intro.tex": "\\section{Intro}\n"})
        write_minimal_pdf(self.tmp / "figures" / "big_figure.pdf")
        write_minimal_pdf(self.tmp / "OpenFOAMJournal.pdf")
        write_minimal_pdf(self.tmp / "paper_FullPaper-review.pdf")
        sub = detect_submission(self.tmp)
        self.assertEqual(sub.mode, "both")
        self.assertEqual(sub.main_tex.name, "paper.tex")
        self.assertEqual(sub.pdf.name, "paper_FullPaper-review.pdf")
        self.assertEqual(len(sub.other_pdfs), 2)
        self.assertEqual(sub.notes, [])

    def test_only_figure_pdfs_gives_latex_mode(self):
        write_files(self.tmp, {"main.tex": MAIN_TEX})
        write_minimal_pdf(self.tmp / "figures" / "f.pdf")
        sub = detect_submission(self.tmp)
        self.assertEqual(sub.mode, "latex")
        self.assertIsNone(sub.pdf)
        self.assertTrue(any("no manuscript PDF" in n for n in sub.notes))

    def test_ofj_class_preferred_and_commented_documentclass_ignored(self):
        write_files(self.tmp, {
            "a_other.tex": "\\documentclass{article}\n\\begin{document}x\\end{document}\n",
            "z_paper.tex": "% \\documentclass{article}\n" + MAIN_TEX,
            "notes.tex": "% \\documentclass{article}\n% \\begin{document}\n"})
        sub = detect_submission(self.tmp)
        self.assertEqual(sub.main_tex.name, "z_paper.tex")
        self.assertEqual(document_class(sub.main_tex), "ofj")
        self.assertIsNone(document_class(self.tmp / "notes.tex"))
        self.assertTrue(any("Several main .tex files" in n for n in sub.notes))

    def test_single_tex_file(self):
        write_files(self.tmp, {"paper.tex": MAIN_TEX})
        sub = detect_submission(self.tmp / "paper.tex")
        self.assertEqual(sub.mode, "latex")
        self.assertEqual(sub.root, self.tmp.resolve())

    def test_zip_is_unpacked_and_unsafe_entries_skipped(self):
        archive = self.tmp / "submission.zip"
        pdf_bytes = write_minimal_pdf(self.tmp / "src.pdf").read_bytes()
        with zipfile.ZipFile(archive, "w") as zf:
            zf.writestr("sub/paper.tex", MAIN_TEX)
            zf.writestr("sub/paper.pdf", pdf_bytes)
            zf.writestr("../evil.tex", "x")
        sub = detect_submission(archive)
        unpacked = sub.root
        self.assertEqual(sub.mode, "both")
        self.assertEqual(sub.archive, "submission.zip")
        self.assertEqual(sub.display(sub.main_tex), "sub/paper.tex")
        self.assertTrue(any("evil.tex" in n for n in sub.notes))
        self.assertFalse((self.tmp.parent / "evil.tex").exists())
        sub.cleanup()
        self.assertFalse(unpacked.exists())

    def test_tar_symlinks_are_skipped(self):
        archive = self.tmp / "submission.tar.gz"
        with tarfile.open(archive, "w:gz") as tf:
            data = MAIN_TEX.encode()
            info = tarfile.TarInfo("paper.tex")
            info.size = len(data)
            tf.addfile(info, io.BytesIO(data))
            link = tarfile.TarInfo("link.tex")
            link.type = tarfile.SYMTYPE
            link.linkname = "/etc/passwd"
            tf.addfile(link)
        with detect_submission(archive) as sub:
            self.assertEqual(sub.mode, "latex")
            self.assertFalse((sub.root / "link.tex").exists())
            self.assertTrue(any("link.tex" in n for n in sub.notes))

    def test_forced_modes(self):
        write_files(self.tmp, {"src/paper.tex": MAIN_TEX})
        with self.assertRaises(InputError):          # 'both' but no PDF
            detect_submission(self.tmp / "src", mode="both")
        pdf = write_minimal_pdf(self.tmp / "src" / "paper.pdf")
        with self.assertRaises(InputError):          # 'latex' but only a PDF given
            detect_submission(pdf, mode="latex")
        self.assertIsNone(detect_submission(self.tmp / "src", mode="latex").pdf)
        self.assertIsNone(detect_submission(self.tmp / "src", mode="pdf").main_tex)

    def test_explicit_pdf_relative_to_folder(self):
        write_files(self.tmp, {"paper.tex": MAIN_TEX})
        write_minimal_pdf(self.tmp / "out" / "whatever.pdf")
        write_minimal_pdf(self.tmp / "paper.pdf")
        sub = detect_submission(self.tmp, pdf=Path("out/whatever.pdf"))
        self.assertEqual(sub.pdf.name, "whatever.pdf")

    def test_errors(self):
        with self.assertRaises(InputError):
            detect_submission(self.tmp / "missing.pdf")
        (self.tmp / "paper.docx").write_bytes(b"x")
        with self.assertRaises(InputError):
            detect_submission(self.tmp / "paper.docx")
        (self.tmp / "empty").mkdir()
        with self.assertRaises(InputError):
            detect_submission(self.tmp / "empty")


if __name__ == "__main__":
    unittest.main()
