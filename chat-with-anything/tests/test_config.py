import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from cwa.config import Config, display_config_value, load, save, set_value


class ConfigTests(unittest.TestCase):
    def test_config_round_trip_uses_utf8_json(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir)
            config_path = config_dir / "config.json"
            with patch("cwa.config._config_dir", return_value=config_dir), patch(
                "cwa.config._config_path", return_value=config_path
            ):
                original = Config(model="本地模型", api_key="secret")
                save(original)
                loaded = load()

                self.assertEqual(loaded.model, "本地模型")
                self.assertTrue(loaded.configured)
                self.assertEqual(loaded.data_dir, str(config_dir / "indexes"))

    def test_set_value_rejects_unknown_keys(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir)
            with patch("cwa.config._config_dir", return_value=config_dir), patch(
                "cwa.config._config_path", return_value=config_dir / "config.json"
            ):
                set_value("model", "test-model")
                self.assertEqual(load().model, "test-model")
                with self.assertRaises(KeyError):
                    set_value("not_a_config_key", "value")

    def test_display_config_value_redacts_api_keys(self):
        secret = "api-key-value-secret"
        masked = display_config_value("api_key", secret)

        self.assertEqual(masked, "api-ke...cret")
        self.assertNotIn(secret, masked)
        self.assertEqual(display_config_value("api_key", "short"), "****")
        self.assertEqual(display_config_value("model", "local-model"), "local-model")


if __name__ == "__main__":
    unittest.main()
