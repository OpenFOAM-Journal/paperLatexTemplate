import shutil
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from helpers import commit, init_repo

from ofjcheck.template_repo import (TemplateError, catalogue_coverage_warnings, obtain_template,
                                    template_changes_since)


@unittest.skipUnless(shutil.which("git"), "git not installed")
class TemplateRepoTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.origin = init_repo(self.tmp / "origin")
        self.c1 = commit(self.origin, {"ofj.cls": "v1\n"}, "first template", "2023-01-01T12:00:00")
        self.c2 = commit(self.origin, {"README.md": "docs\n"}, "readme only", "2023-02-01T12:00:00")
        self.url = self.origin.as_uri()
        self.cache = self.tmp / "cache"
        self.t0 = datetime(2026, 11, 5, 12, tzinfo=timezone.utc)

    def tearDown(self):
        self._tmp.cleanup()

    def obtain(self, **kw):
        kw.setdefault("url", self.url)
        kw.setdefault("cache_dir", self.cache)
        kw.setdefault("now", self.t0)
        return obtain_template(**kw)

    def test_clone_then_cache_then_update(self):
        repo, st = self.obtain()
        self.assertEqual(st.source, "cloned")
        self.assertEqual(st.head.sha, self.c2)
        self.assertEqual(repo.read_file(st.head.sha, "ofj.cls"), b"v1\n")

        c3 = commit(self.origin, {"ofj.cls": "v2\n"}, "change class", "2023-03-01T12:00:00")
        _, st = self.obtain(now=self.t0 + timedelta(hours=1))
        self.assertEqual(st.source, "cache")              # still fresh: no fetch
        self.assertEqual(st.head.sha, self.c2)

        _, st = self.obtain(now=self.t0 + timedelta(hours=13))
        self.assertEqual(st.source, "updated")
        self.assertEqual(st.head.sha, c3)

    def test_force_update(self):
        self.obtain()
        c3 = commit(self.origin, {"ofj.cls": "v2\n"}, "change class")
        _, st = self.obtain(force_update=True)
        self.assertEqual((st.source, st.head.sha), ("updated", c3))

    def test_offline(self):
        with self.assertRaises(TemplateError):
            self.obtain(offline=True)
        self.obtain()
        _, st = self.obtain(offline=True, now=self.t0 + timedelta(days=3))
        self.assertEqual(st.source, "cache")
        self.assertTrue(any("3 days old" in w for w in st.warnings))

    def test_unreachable_remote_falls_back_to_cache(self):
        self.obtain()
        self.origin.rename(self.tmp / "moved-away")
        _, st = self.obtain(now=self.t0 + timedelta(days=1))
        self.assertEqual(st.source, "cache-stale")
        self.assertTrue(any("Could not update" in w for w in st.warnings))

    def test_bad_url_without_cache(self):
        with self.assertRaises(TemplateError):
            self.obtain(url=(self.tmp / "nowhere").as_uri())

    def test_local_template_dir(self):
        _, st = self.obtain(template_dir=self.origin)
        self.assertEqual(st.source, "local")
        self.assertEqual(st.head.sha, self.c2)
        with self.assertRaises(TemplateError):
            self.obtain(template_dir=self.tmp)

    def test_unknown_ref(self):
        with self.assertRaises(TemplateError):
            self.obtain(ref="no-such-branch")

    def test_catalogue_coverage(self):
        repo, st = self.obtain()
        self.assertEqual(catalogue_coverage_warnings(repo, self.c1, st.head), [])  # README only
        c3 = commit(self.origin, {"parts/x.tex": "x\n"}, "template change")
        repo, st = self.obtain(force_update=True)
        self.assertEqual([c.sha for c in template_changes_since(repo, self.c1, st.head.sha)], [c3])
        warnings = catalogue_coverage_warnings(repo, self.c1, st.head)
        self.assertEqual(len(warnings), 1)
        self.assertIn("1 change(s)", warnings[0])
        self.assertIn("template change", warnings[0])
        self.assertEqual(catalogue_coverage_warnings(repo, c3, st.head), [])
        commit(self.origin, {"tools/ofj-check/README.md": "tool\n"}, "editor tool only")
        repo, st = self.obtain(force_update=True)
        self.assertEqual(catalogue_coverage_warnings(repo, c3, st.head), [])   # tools/ is not the template
        self.assertIn("not in this template repository",
                      catalogue_coverage_warnings(repo, "0" * 40, st.head)[0])


if __name__ == "__main__":
    unittest.main()
