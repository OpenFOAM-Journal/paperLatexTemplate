"""Every state of the template ever published on master must be recognised as its own generation.

Needs the template's history: $OFJ_TEMPLATE_REPO, the template repository this tool is part
of, or ofj-check's cached copy. Skipped otherwise.
"""
import io
import subprocess
import tarfile
import tempfile
import unittest
from pathlib import Path

from helpers import find_template_repo

from ofjcheck import generations
from ofjcheck.analyze import run_checks
from ofjcheck.inputs import detect_submission
from ofjcheck.template_repo import obtain_template

VERSION_KINDS = ("consistent", "outdated")


def _git_dir(path):
    p = Path(path)
    return p / ".git" if (p / ".git").exists() else p


REPO = find_template_repo()


@unittest.skipUnless(REPO, "no clone of the OFJ template available")
class HistorySnapshotTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.git_dir = _git_dir(REPO)
        cls.repo, cls.status = obtain_template(template_dir=Path(REPO)) if (Path(REPO) / ".git").exists() \
            else cls._bare()
        log = subprocess.run(["git", f"--git-dir={cls.git_dir}", "log", "--first-parent", "--reverse",
                              "--date=short", "--format=%H %h %ad", generations.CATALOGUE_COMMIT],
                             check=True, capture_output=True, text=True).stdout.split("\n")
        cls.commits = [line.split() for line in log if line]
        cls.gens = generations.commit_generations([(c[0], c[2]) for c in cls.commits])

    @classmethod
    def _bare(cls):
        from ofjcheck.template_repo import TemplateRepo, TemplateStatus
        repo = TemplateRepo(cls.git_dir)
        head = repo.commit_info(generations.CATALOGUE_COMMIT)
        return repo, TemplateStatus(url=REPO, ref="master", path=cls.git_dir, head=head,
                                    source="cache", last_fetch=None)

    def check_commit(self, sha):
        return self.report_commit(sha).findings

    def report_commit(self, sha):
        data = subprocess.run(["git", f"--git-dir={self.git_dir}", "archive", sha],
                              check=True, capture_output=True).stdout
        with tempfile.TemporaryDirectory() as tmp:
            with tarfile.open(fileobj=io.BytesIO(data)) as tf:
                for m in tf.getmembers():
                    if m.isfile():
                        target = Path(tmp) / m.name
                        target.parent.mkdir(parents=True, exist_ok=True)
                        target.write_bytes(tf.extractfile(m).read())
            with detect_submission(Path(tmp), mode="latex") as sub:
                return run_checks(sub, self.repo, self.status)

    def test_every_master_state_matches_its_generation(self):
        self.assertGreater(len(self.commits), 40)
        for (full, short, day), gen in zip(self.commits, self.gens):
            with self.subTest(commit=short, date=day, generation=gen):
                report = self.report_commit(full)
                v = report.verdict
                self.assertEqual(v.kind, "current" if gen == generations.CURRENT else "outdated", v.headline)
                lo = generations.index(v.range_from)
                hi = generations.index(v.range_to) if v.range_to else len(generations.GENERATIONS) - 1
                self.assertTrue(lo <= generations.index(gen) <= hi, f"verdict range {v.range_from}-{v.range_to}")
                for f in report.findings:
                    if f.excludes_from or f.excludes_to:
                        self.assertFalse(generations.index(f.excludes_from) <= generations.index(gen)
                                         <= generations.index(f.excludes_to), f"{f.rule_id} excludes {gen}")
                    if f.kind not in VERSION_KINDS or (f.implies_from is None and f.implies_to is None):
                        continue
                    lo = generations.index(f.implies_from) if f.implies_from else 0
                    hi = generations.index(f.implies_to) if f.implies_to else len(generations.GENERATIONS) - 1
                    self.assertTrue(lo <= generations.index(gen) <= hi,
                                    f"{f.rule_id} '{f.title}' points to "
                                    f"{generations.describe(f.implies_from, f.implies_to)}")

    def test_current_template_has_no_outdated_findings(self):
        findings = self.check_commit(generations.CATALOGUE_COMMIT)
        self.assertEqual([f.title for f in findings if f.kind == "outdated"], [])

    def test_every_older_generation_is_detected(self):
        for g in generations.GENERATIONS[:-1]:
            with self.subTest(generation=g.id):
                outdated = [f for f in self.check_commit(g.commit) if f.kind == "outdated"]
                self.assertTrue(outdated, f"{g.id} ({g.commit}) not recognised as outdated")


if __name__ == "__main__":
    unittest.main()
