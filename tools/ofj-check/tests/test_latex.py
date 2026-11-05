import tempfile
import unittest
from pathlib import Path

from helpers import write_files

from ofjcheck.latex import load_document, mask, strip_comment


class MaskTest(unittest.TestCase):
    def test_comments(self):
        self.assertEqual(strip_comment(r"a 50\% rate % comment"), r"a 50\% rate ")
        self.assertEqual(strip_comment(r"line\\% comment"), "line\\\\")
        self.assertEqual(strip_comment("no comment"), "no comment")

    def test_verbatim_is_blanked_but_lines_kept(self):
        text = "\n".join([r"before \autoref{a}",
                          r"\begin{lstlisting}[caption={c}, label=lst:x]",
                          r"\autoref{inside}",
                          r"\end{lstlisting}",
                          r"inline \verb|\autoref{v}| after % \autoref{c}"])
        masked = mask(text)
        self.assertEqual(len(masked.splitlines()), 5)
        self.assertIn(r"\autoref{a}", masked)
        self.assertIn("label=lst:x", masked)           # listing options stay visible
        self.assertNotIn("inside", masked)
        self.assertNotIn("{v}", masked)
        self.assertNotIn("{c}", masked.splitlines()[4])


class LoadDocumentTest(unittest.TestCase):
    def test_input_tree_preamble_and_locations(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_files(root, {
                "main.tex": "\\documentclass{ofj}\n\\input{macros}\n\\begin{document}\n"
                            "\\input{parts/intro}\n% \\input{parts/commented}\n\\include{missing}\n"
                            "\\end{document}\n",
                "macros.tex": "\\newcommand{\\x}{y}\n",
                "parts/intro.tex": "Text\n\\input{parts/deeper.tex}\n",
                "parts/deeper.tex": "Deep \\autoref{fig}\n",
                "parts/commented.tex": "never\n"})
            doc = load_document(root / "main.tex", root)
            self.assertEqual([f.rel for f in doc.files],
                             ["main.tex", "macros.tex", "parts/intro.tex", "parts/deeper.tex"])
            self.assertTrue(doc.files[1].in_preamble)
            self.assertFalse(doc.files[2].in_preamble)
            self.assertEqual(len(doc.missing_inputs), 1)
            hits = doc.search(r"\\autoref\{")
            self.assertEqual([h.location for h in hits], ["parts/deeper.tex:1"])
            self.assertEqual(doc.search(r"\\newcommand", scope="preamble")[0].location, "macros.tex:1")
            self.assertEqual(doc.search(r"\\newcommand", scope="body"), [])
            self.assertEqual(len(doc.search(r"\\input\{", scope="preamble")), 1)


if __name__ == "__main__":
    unittest.main()
