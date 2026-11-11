# encoding:utf-8
"""Unit tests for first-turn latency changes: per-key agent init, incremental
skill sync, and shared HTTP session reuse.
"""
import os
import sys
import tempfile
import threading
import time
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from bridge.agent_bridge import AgentBridge
from agent.skills.sync_builtin import sync_builtin_skills_to_workspace, sync_skill_directory
from models.openai import openai_http_client as http_mod
from models.openai.openai_http_client import OpenAIHTTPClient, reset_shared_session, _shared_session


class TestPerKeyInitLock(unittest.TestCase):
    def _runtime(self):
        holder = SimpleNamespace(
            _agents_lock=threading.RLock(),
            _agent_inflight={},
        )
        return holder, {}

    def _get(self, holder, cache, key, build):
        return AgentBridge._get_or_create_runtime(holder, cache, key, build)

    def test_same_key_initializes_once(self):
        holder, cache = self._runtime()
        started = threading.Event()
        release = threading.Event()
        calls = []

        def build():
            calls.append(1)
            started.set()
            self.assertTrue(release.wait(2))
            return SimpleNamespace(id=len(calls))

        results = []
        errors = []

        def worker():
            try:
                results.append(self._get(holder, cache, ("a", "s1"), build))
            except Exception as exc:
                errors.append(exc)

        t1 = threading.Thread(target=worker)
        t2 = threading.Thread(target=worker)
        t1.start()
        self.assertTrue(started.wait(2))
        t2.start()
        release.set()
        t1.join(2)
        t2.join(2)
        self.assertFalse(errors)
        self.assertEqual(len(calls), 1)
        self.assertEqual(len(results), 2)
        self.assertIs(results[0], results[1])

    def test_different_keys_can_init_concurrently(self):
        holder, cache = self._runtime()
        in_build = threading.Barrier(2, timeout=2)

        def build_a():
            in_build.wait()
            return SimpleNamespace(id="a")

        def build_b():
            in_build.wait()
            return SimpleNamespace(id="b")

        results = {}

        def worker(key, fn):
            results[key] = self._get(holder, cache, key, fn)

        t1 = threading.Thread(target=worker, args=(("a", "s1"), build_a))
        t2 = threading.Thread(target=worker, args=(("a", "s2"), build_b))
        t1.start()
        t2.start()
        t1.join(2)
        t2.join(2)
        self.assertEqual(results[("a", "s1")].id, "a")
        self.assertEqual(results[("a", "s2")].id, "b")

    def test_failed_init_can_be_retried(self):
        holder, cache = self._runtime()
        attempts = {"n": 0}

        def build():
            attempts["n"] += 1
            if attempts["n"] == 1:
                raise RuntimeError("boom")
            return SimpleNamespace(id="ok")

        with self.assertRaises(RuntimeError):
            self._get(holder, cache, "k", build)
        agent = self._get(holder, cache, "k", build)
        self.assertEqual(agent.id, "ok")
        self.assertEqual(attempts["n"], 2)

    def test_inflight_is_not_visible_in_cache(self):
        holder, cache = self._runtime()
        started = threading.Event()
        release = threading.Event()

        def build():
            started.set()
            release.wait(2)
            return SimpleNamespace(id="x")

        def worker():
            self._get(holder, cache, "k", build)

        t = threading.Thread(target=worker)
        t.start()
        self.assertTrue(started.wait(2))
        self.assertIsNone(cache.get("k"))
        self.assertIn("k", holder._agent_inflight)
        release.set()
        t.join(2)
        self.assertIsNotNone(cache.get("k"))
        self.assertNotIn("k", holder._agent_inflight)


class TestIncrementalSkillSync(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.src_root = self.tmp / "builtin"
        self.dst_root = self.tmp / "workspace"
        skill = self.src_root / "demo"
        skill.mkdir(parents=True)
        (skill / "SKILL.md").write_text("---\nname: demo\ndescription: d\n---\nbody\n", encoding="utf-8")
        (skill / "helper.txt").write_text("help", encoding="utf-8")

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_second_sync_is_noop_when_unchanged(self):
        copied, skipped = sync_builtin_skills_to_workspace(str(self.src_root), str(self.dst_root))
        self.assertGreater(copied, 0)
        dest = self.dst_root / "demo" / "SKILL.md"
        mtime = dest.stat().st_mtime_ns
        copied2, skipped2 = sync_builtin_skills_to_workspace(str(self.src_root), str(self.dst_root))
        self.assertEqual(copied2, 0)
        self.assertGreater(skipped2, 0)
        self.assertEqual(dest.stat().st_mtime_ns, mtime)

    def test_changed_file_is_updated(self):
        sync_builtin_skills_to_workspace(str(self.src_root), str(self.dst_root))
        time.sleep(0.01)
        (self.src_root / "demo" / "SKILL.md").write_text(
            "---\nname: demo\ndescription: d\n---\nchanged\n", encoding="utf-8"
        )
        copied, _ = sync_builtin_skills_to_workspace(str(self.src_root), str(self.dst_root))
        self.assertGreater(copied, 0)
        self.assertIn("changed", (self.dst_root / "demo" / "SKILL.md").read_text(encoding="utf-8"))

    def test_skills_config_and_extra_files_are_preserved(self):
        sync_builtin_skills_to_workspace(str(self.src_root), str(self.dst_root))
        config = self.dst_root / "skills_config.json"
        config.write_text('{"demo": {"enabled": false}}', encoding="utf-8")
        extra = self.dst_root / "demo" / "user-notes.txt"
        extra.write_text("keep me", encoding="utf-8")
        # A subsequent sync must not rmtree the dest dir.
        dest_inode = (self.dst_root / "demo").stat().st_ino
        sync_builtin_skills_to_workspace(str(self.src_root), str(self.dst_root))
        self.assertEqual(config.read_text(encoding="utf-8"), '{"demo": {"enabled": false}}')
        self.assertEqual(extra.read_text(encoding="utf-8"), "keep me")
        self.assertEqual((self.dst_root / "demo").stat().st_ino, dest_inode)

    def test_does_not_write_config_into_skill_dir(self):
        (self.src_root / "demo" / "skills_config.json").write_text("nope", encoding="utf-8")
        sync_skill_directory(str(self.src_root / "demo"), str(self.dst_root / "demo"))
        self.assertFalse((self.dst_root / "demo" / "skills_config.json").exists())


class TestSharedHttpSession(unittest.TestCase):
    def setUp(self):
        reset_shared_session()

    def tearDown(self):
        reset_shared_session()

    def test_requests_reuse_the_same_session(self):
        seen = []

        class FakeResponse:
            status_code = 200

            def json(self):
                return {"ok": True}

        def fake_post(*args, **kwargs):
            seen.append(_shared_session())
            return FakeResponse()

        client = OpenAIHTTPClient(api_base="http://127.0.0.1:9/v1", timeout=1)
        with mock.patch.object(http_mod, "_shared_session") as shared:
            session = mock.Mock()
            session.post.side_effect = fake_post
            shared.return_value = session
            # call non-stream _request twice
            client._request(
                path="/chat/completions",
                payload={"model": "x"},
                api_key="k",
                api_base="http://127.0.0.1:9/v1",
                timeout=1,
                stream=False,
            )
            client._request(
                path="/chat/completions",
                payload={"model": "x"},
                api_key="k",
                api_base="http://127.0.0.1:9/v1",
                timeout=1,
                stream=False,
            )
            self.assertEqual(session.post.call_count, 2)

        reset_shared_session()
        a = _shared_session()
        b = _shared_session()
        self.assertIs(a, b)


class TestMemoryStorageReuse(unittest.TestCase):
    def setUp(self):
        from agent.memory.storage import MemoryStorage
        self.MemoryStorage = MemoryStorage
        MemoryStorage.reset_instances()
        self.tmp = Path(tempfile.mkdtemp())

    def tearDown(self):
        self.MemoryStorage.reset_instances()
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_for_path_returns_same_instance(self):
        db = self.tmp / "index.db"
        a = self.MemoryStorage.for_path(db)
        b = self.MemoryStorage.for_path(db)
        self.assertIs(a, b)


if __name__ == "__main__":
    unittest.main()
