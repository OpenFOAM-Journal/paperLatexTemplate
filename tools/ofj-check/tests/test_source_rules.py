"""Source rules on small synthetic submissions, against a toy template repository."""
import shutil
import tempfile
import unittest
from pathlib import Path

from helpers import commit, init_repo, write_files

from ofjcheck.analyze import run_checks
from ofjcheck.inputs import detect_submission
from ofjcheck.template_repo import obtain_template

CLASS_V1 = "% ofj class\n\\ProvidesClass{ofj}\n\\def\\a{1}\n"
CLASS_V2 = "% ofj class\n\\ProvidesClass{ofj}\n\\def\\a{2}\n"
HEAD_MAIN = "\\copyrightinfo{2026}{The Authors.}\n"

PREAMBLE = r"""\documentclass[e-only,10pt,reqno]{ofj}
\usepackage[hang,flushmargin]{footmisc}
\usepackage{orcidlink}
\usepackage{cite}
\usepackage{xspace}
\usepackage[colorlinks=true,linkcolor=black]{hyperref}
\newcommand{\authorcontributions}[1]{\textbf{Author Contributions:} #1}
\copyrightinfo{2026}{The Authors. CC BY-SA 4.0}
\newcommand{\OF}[0]{OpenFOAM\textsuperscript{\textregistered}\xspace}
\OpenFOAMversions{\OF v2312}
\ifdefined\review
\Repository{}
\else
\Repository{https://github.com/me/case}
\fi
\DOI{TBD}
\ifdefined\review
  \doublespacing
\fi
"""

BODY = r"""\begin{document}
\maketitle
\ifdefined\review
  \linenumbers
\else
\fi
See Fig.~\ref{fig:a}.
\ifdefined\review
\else
\authorcontributions{Everything, A.B.}
\fi
\bibliographystyle{IEEEtran}
\bibliography{refs}
\end{document}
"""


@unittest.skipUnless(shutil.which("git"), "git not installed")
class SourceRulesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory()
        tmp = Path(cls._tmp.name)
        cls.template = init_repo(tmp / "template")
        commit(cls.template, {"ofj.cls": CLASS_V1, "ofj-template.tex": "\\copyrightinfo{2022}{x}\n"},
               "old", "2023-03-01T12:00:00")
        commit(cls.template, {"ofj.cls": CLASS_V2, "ofj-template.tex": HEAD_MAIN}, "new",
               "2026-02-01T12:00:00")
        cls.repo, cls.status = obtain_template(template_dir=cls.template)

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    def check(self, files, head_main=None):
        with tempfile.TemporaryDirectory() as tmp:
            write_files(Path(tmp), files)
            with detect_submission(Path(tmp), mode="latex") as sub:
                if head_main is not None:
                    from ofjcheck import analyze
                    original = analyze.Context.head_main_tex
                    analyze.Context.head_main_tex = property(lambda self: head_main)
                    try:
                        return run_checks(sub, self.repo, self.status).findings
                    finally:
                        analyze.Context.head_main_tex = original
                return run_checks(sub, self.repo, self.status).findings

    @staticmethod
    def ids(findings, kind=None):
        return sorted(f.rule_id for f in findings if kind is None or f.kind == kind)

    def test_clean_current_submission(self):
        findings = self.check({"paper.tex": PREAMBLE + BODY})
        self.assertEqual(self.ids(findings, "outdated"), [])
        self.assertEqual(self.ids(findings, "modified"), [])
        self.assertEqual(self.ids(findings, "placeholder"), [])
        self.assertIn("SRC04", self.ids(findings, "consistent"))

    def test_not_the_template(self):
        findings = self.check({"paper.tex": "\\documentclass{article}\n\\begin{document}\\autoref{x}\\end{document}\n"})
        self.assertEqual([(f.rule_id, f.kind) for f in findings], [("SRC01", "not-template")])

    def test_old_conventions(self):
        old = PREAMBLE.replace("\\xspace}", " }").replace("2026", "2024") \
            + "\\def\\figureautorefname{Fig.}\n"
        body = BODY.replace("Fig.~\\ref{fig:a}", "\\autoref{fig:a} and Eq.\\ \\ref{e}") \
            .replace("\\ifdefined\\review\n  \\linenumbers\n\\else\n\\fi\n", "\\linenumbers\n")
        findings = self.check({"paper.tex": old + body})
        outdated = self.ids(findings, "outdated")
        for rule in ("SRC02", "SRC03", "SRC05", "SRC07", "SRC08", "SRC11"):
            self.assertIn(rule, outdated)
        src07 = next(f for f in findings if f.rule_id == "SRC07")
        self.assertEqual((src07.importance, src07.implies_from, src07.implies_to), ("cosmetic", "G09", "G09"))

    def test_eq_abbreviation_is_style_but_figure_at_sentence_start_is_fine(self):
        body = BODY.replace("See Fig.~\\ref{fig:a}.", "Figure~\\ref{fig:a} shows it. See Eq.~\\ref{e}.")
        findings = self.check({"paper.tex": PREAMBLE + body})
        style = [x for x in findings if x.kind == "style"]
        self.assertEqual([x.rule_id for x in style], ["SRC28"])
        self.assertEqual(len(style[0].evidence), 1)
        self.assertNotIn("SRC05", self.ids(findings))

    def test_masking_ignores_comments_and_listings(self):
        body = BODY.replace("See Fig.~\\ref{fig:a}.",
                            "% \\autoref{x}\n\\begin{lstlisting}\n\\autoref{y}\n\\end{lstlisting}")
        self.assertNotIn("SRC03", self.ids(self.check({"paper.tex": PREAMBLE + body})))

    def test_class_files(self):
        findings = self.check({"paper.tex": PREAMBLE + BODY, "ofj.cls": CLASS_V1})
        cls00 = next(f for f in findings if f.rule_id == "CLS00")
        self.assertEqual((cls00.kind, cls00.importance, cls00.implies_to), ("outdated", "required", "G07"))
        findings = self.check({"paper.tex": PREAMBLE + BODY, "ofj.cls": CLASS_V2.replace("\n", "\r\n")})
        self.assertEqual(next(f for f in findings if f.rule_id == "CLS00").kind, "consistent")
        findings = self.check({"paper.tex": PREAMBLE + BODY, "ofj.cls": CLASS_V2 + "\\def\\mine{}\n"})
        cls01 = next(f for f in findings if f.rule_id == "CLS01")
        self.assertEqual(cls01.kind, "modified")
        self.assertIn("1 line(s) added", cls01.message)
        self.assertTrue(any("\\def\\mine" in e.excerpt for e in cls01.evidence))

    def test_placeholders_and_missing_parts(self):
        body = BODY.replace("\\authorcontributions{Everything, A.B.}\n", "")
        pre = PREAMBLE.replace("v2312", "v20xx").replace("\\usepackage{cite}\n", "")
        findings = self.check({"paper.tex": pre + body})
        plc = next(f for f in findings if f.rule_id == "PLC01")
        self.assertIn("v20xx", plc.message)
        self.assertIn("SRC13", self.ids(findings, "modified"))
        self.assertIn("SRC15", self.ids(findings, "outdated"))

    def test_cleveref_and_bibliography_style(self):
        body = BODY.replace("Fig.~\\ref{fig:a}", "\\cref{fig:a}").replace("{IEEEtran}", "{plain}")
        modified = self.ids(self.check({"paper.tex": PREAMBLE + body}), "modified")
        self.assertIn("SRC26", modified)
        self.assertIn("SRC23", modified)
        cleveref_head = HEAD_MAIN + "\\usepackage[nameinlink]{cleveref}\n"
        self.assertNotIn("SRC26", self.ids(self.check({"paper.tex": PREAMBLE + body}, cleveref_head)))

    def test_version_marker(self):
        for value, kind in (("G09", "outdated"), ("G11", "consistent"), ("2026-04-02", "consistent"),
                            ("x1", "info")):
            with self.subTest(value=value):
                pre = PREAMBLE + f"\\newcommand{{\\ofjtemplateversion}}{{{value}}}\n"
                ver = [f for f in self.check({"paper.tex": pre + BODY}) if f.rule_id == "VER01"]
                self.assertEqual([f.kind for f in ver], [kind])

    def test_version_marker_in_class_file(self):
        cls = CLASS_V2 + "\\newcommand{\\ofjtemplateversion}{2026-04-02}\n"
        ver = [f for f in self.check({"paper.tex": PREAMBLE + BODY, "ofj.cls": cls}) if f.rule_id == "VER01"]
        self.assertEqual([(f.kind, f.evidence[0].location) for f in ver], [("consistent", "ofj.cls:4")])

    def test_ai_declaration_becomes_mandatory_when_template_has_it(self):
        head = HEAD_MAIN + "\\input{parts/aiDeclaration.tex}\n"
        self.assertNotIn("SRC30", self.ids(self.check({"paper.tex": PREAMBLE + BODY})))
        findings = self.check({"paper.tex": PREAMBLE + BODY}, head)
        self.assertEqual([f.importance for f in findings if f.rule_id == "SRC30"], ["required"])
        body = BODY.replace("\\bibliographystyle", "\\section*{Declaration on the Use of Artificial "
                            "Intelligence}\nNone.\n\\bibliographystyle")
        self.assertNotIn("SRC30", self.ids(self.check({"paper.tex": PREAMBLE + body}, head)))


if __name__ == "__main__":
    unittest.main()
