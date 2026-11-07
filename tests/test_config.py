"""Unit tests for config load/save/delete robustness."""
import json
import os
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config  # noqa: E402


class TestConfig(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        # Redirect the config dir regardless of the host OS.
        patcher = mock.patch.object(
            config, "config_dir", lambda: os.path.join(self._tmp.name, "nnn-countdown")
        )
        patcher.start()
        self.addCleanup(patcher.stop)
        self.addCleanup(self._tmp.cleanup)

    def _write_raw(self, text):
        os.makedirs(config.config_dir(), exist_ok=True)
        with open(config.config_path(), "w", encoding="utf-8") as fh:
            fh.write(text)

    def test_creates_default_file_on_first_load(self):
        cfg, err = config.load_config()
        self.assertIsNone(err)
        self.assertEqual(cfg, config.DEFAULTS)
        self.assertTrue(os.path.exists(config.config_path()))

    def test_roundtrip(self):
        cfg = dict(
            config.DEFAULTS,
            language="ru",
            mode="end",
            losses=3,
            always_on_top=True,
            geometry="1000x700+10+10",
        )
        config.save_config(cfg)
        loaded, err = config.load_config()
        self.assertIsNone(err)
        self.assertEqual(loaded, cfg)

    def test_corrupt_json_resets_to_defaults(self):
        self._write_raw("{not valid json")
        cfg, err = config.load_config()
        self.assertIsNotNone(err)
        self.assertEqual(cfg, config.DEFAULTS)

    def test_non_object_json_resets(self):
        self._write_raw("[1, 2, 3]")
        cfg, err = config.load_config()
        self.assertIsNotNone(err)
        self.assertEqual(cfg, config.DEFAULTS)

    def test_invalid_values_are_sanitized(self):
        self._write_raw(json.dumps({
            "language": "fr",            # unsupported -> default
            "mode": "sideways",          # unsupported -> default
            "geometry": "not-geometry",  # bad format -> default
            "always_on_top": "yes",      # not a bool -> default
            "losses": -5,                # negative -> default
        }))
        cfg, err = config.load_config()
        self.assertIsNone(err)
        self.assertEqual(cfg, config.DEFAULTS)

    def test_bool_is_not_accepted_as_losses(self):
        self._write_raw(json.dumps({"losses": True}))
        cfg, _ = config.load_config()
        self.assertEqual(cfg["losses"], 0)

    def test_delete_config(self):
        config.save_config(dict(config.DEFAULTS))
        self.assertTrue(config.delete_config())
        self.assertFalse(os.path.exists(config.config_path()))
        # Deleting twice is fine too.
        self.assertTrue(config.delete_config())

    def test_unknown_keys_are_dropped_on_save(self):
        config.save_config(dict(config.DEFAULTS, hacker="yes"))
        loaded, _ = config.load_config()
        self.assertNotIn("hacker", loaded)


if __name__ == "__main__":
    unittest.main()
