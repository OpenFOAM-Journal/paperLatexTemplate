import json
import unittest

from ofjcheck.model import (CONVENTION, COSMETIC, STRONG, Evidence, Fact, Finding, Report,
                            Verdict)
from ofjcheck.report import render_json, render_markdown, render_text


def sample_report() -> Report:
    findings = [
        Finding(rule_id="PDF11", title="Cross-references made with \\autoref", kind="outdated",
                importance=CONVENTION, reliability=STRONG,
                message="Links to figures and tables include the word, as \\autoref produces.",
                evidence=[Evidence("link on p. 2", "Fig. 1 -> figure.1")],
                implies_from="G07", implies_to="G10",
                template_change="2026-03-31 cd2b7f2: \\autoref replaced by Fig.~\\ref",
                advice="Please use Fig.~\\ref{...} as in the current template."),
        Finding(rule_id="PDF09", title="Copyright year 2024", kind="outdated", importance=COSMETIC,
                reliability="medium", message="The footer says 2024.",
                evidence=[Evidence("PDF p. 1", "© 2024 The Authors")]),
    ]
    return Report(tool_version="0.1.0", created="2026-11-05 10:00 UTC",
                  submission={"given": "/x/paper.pdf", "mode": "pdf", "pdf": "", "main_tex": "",
                              "archive": ""},
                  template={"commit": "cd2b7f2"},
                  verdict=Verdict(kind="outdated", headline="Older template", closest_generation="G10",
                                  range_from="G07", range_to="G10", confidence="high",
                                  explanation="Two template changes are missing."),
                  findings=findings, facts=[Fact("pdf", "Pages", "12")],
                  warnings=["a warning"], notes=["a note"])


class ReportTest(unittest.TestCase):
    def test_text(self):
        text = render_text(sample_report())
        self.assertIn("VERDICT: Older template", text)
        self.assertIn("G07-G10 (2023-02-08 to 2026-03-30)", text)
        self.assertIn("[PDF11]", text)
        self.assertIn("evidence: link on p. 2: Fig. 1 -> figure.1", text)
        self.assertIn("template change: 2026-03-31", text)
        self.assertLess(text.index("Template conventions"), text.index("Cosmetic"))

    def test_markdown(self):
        md = render_markdown(sample_report())
        self.assertIn("# OFJ template check: paper.pdf", md)
        self.assertIn("#### PDF11: Cross-references made with \\autoref", md)
        self.assertIn("Suggested note to the authors:", md)
        self.assertIn("| Pages | 12 |", md)

    def test_json(self):
        data = json.loads(render_json(sample_report()))
        self.assertEqual(data["verdict"]["exit_code"], 1)
        self.assertEqual(data["findings"][0]["evidence"][0]["location"], "link on p. 2")

    def test_no_findings(self):
        r = sample_report()
        r.findings = []
        self.assertIn("Findings: none", render_text(r))
        self.assertIn("No findings.", render_markdown(r))


if __name__ == "__main__":
    unittest.main()
