"""Tests for configuration management."""

import json


class TestLoadConfig:
    """Tests for load_config function."""

    def test_load_config_returns_defaults_when_no_file(self, tmp_path, monkeypatch, default_config):
        """When config.json doesn't exist, should return default config."""
        import jobpacker

        # Point CONFIG_PATH to non-existent file
        monkeypatch.setattr(jobpacker, "CONFIG_PATH", tmp_path / "nonexistent.json")

        config = jobpacker.load_config()

        assert config == default_config

    def test_load_config_reads_existing_file(self, tmp_path, monkeypatch, custom_config):
        """When config.json exists, should load and return it."""
        import jobpacker

        config_path = tmp_path / "config.json"
        with open(config_path, "w") as f:
            json.dump(custom_config, f)

        monkeypatch.setattr(jobpacker, "CONFIG_PATH", config_path)

        config = jobpacker.load_config()

        assert config["default_search"] == custom_config["default_search"]
        assert config["default_location"] == custom_config["default_location"]
        assert config["results_per_site"] == custom_config["results_per_site"]
        assert config["remote_only"] == custom_config["remote_only"]
        assert config["job_type"] == custom_config["job_type"]
        assert config["job_boards"] == custom_config["job_boards"]

    def test_load_config_merges_with_defaults(self, tmp_path, monkeypatch, default_config):
        """When config has missing keys, should merge with defaults."""
        import jobpacker

        # Config with only some keys
        partial_config = {"default_search": "test search", "results_per_site": 50}

        config_path = tmp_path / "config.json"
        with open(config_path, "w") as f:
            json.dump(partial_config, f)

        monkeypatch.setattr(jobpacker, "CONFIG_PATH", config_path)

        config = jobpacker.load_config()

        # Should have the custom values
        assert config["default_search"] == "test search"
        assert config["results_per_site"] == 50
        # Should have defaults for missing keys
        assert config["default_location"] == default_config["default_location"]
        assert config["remote_only"] == default_config["remote_only"]
        assert config["job_type"] == default_config["job_type"]
        assert config["job_boards"] == default_config["job_boards"]

    def test_load_config_handles_corrupted_json(self, tmp_path, monkeypatch, default_config):
        """When config.json is corrupted, should return defaults."""
        import jobpacker

        config_path = tmp_path / "config.json"
        with open(config_path, "w") as f:
            f.write("{ invalid json }")

        monkeypatch.setattr(jobpacker, "CONFIG_PATH", config_path)

        config = jobpacker.load_config()

        assert config == default_config

    def test_load_config_handles_empty_file(self, tmp_path, monkeypatch, default_config):
        """When config.json is empty, should return defaults."""
        import jobpacker

        config_path = tmp_path / "config.json"
        config_path.touch()

        monkeypatch.setattr(jobpacker, "CONFIG_PATH", config_path)

        config = jobpacker.load_config()

        assert config == default_config


class TestSaveConfig:
    """Tests for save_config function."""

    def test_save_config_writes_file(self, tmp_path, monkeypatch, custom_config):
        """Should write config to file as JSON."""
        import jobpacker

        config_path = tmp_path / "config.json"
        monkeypatch.setattr(jobpacker, "CONFIG_PATH", config_path)

        jobpacker.save_config(custom_config)

        assert config_path.exists()
        with open(config_path) as f:
            saved = json.load(f)
        assert saved == custom_config

    def test_save_config_overwrites_existing(self, tmp_path, monkeypatch):
        """Should overwrite existing config file."""
        import jobpacker

        config_path = tmp_path / "config.json"
        with open(config_path, "w") as f:
            json.dump({"old": "data"}, f)

        monkeypatch.setattr(jobpacker, "CONFIG_PATH", config_path)

        new_config = {"new": "config", "results_per_site": 100}
        jobpacker.save_config(new_config)

        with open(config_path) as f:
            saved = json.load(f)
        assert saved == new_config
        assert "old" not in saved

    def test_save_config_creates_indented_json(self, tmp_path, monkeypatch, custom_config):
        """Should write pretty-printed JSON with indent=2."""
        import jobpacker

        config_path = tmp_path / "config.json"
        monkeypatch.setattr(jobpacker, "CONFIG_PATH", config_path)

        jobpacker.save_config(custom_config)

        with open(config_path) as f:
            content = f.read()
        # Check for indentation (pretty printed JSON has newlines and spaces)
        assert "\n" in content
        assert "  " in content


class TestConfigRoundTrip:
    """Integration tests for config save/load cycle."""

    def test_config_roundtrip(self, tmp_path, monkeypatch, custom_config):
        """Save then load should return same config."""
        import jobpacker

        config_path = tmp_path / "config.json"
        monkeypatch.setattr(jobpacker, "CONFIG_PATH", config_path)

        jobpacker.save_config(custom_config)
        loaded = jobpacker.load_config()

        assert loaded == custom_config

    def test_config_roundtrip_with_none_values(self, tmp_path, monkeypatch):
        """Should handle None values correctly."""
        import jobpacker

        config_path = tmp_path / "config.json"
        monkeypatch.setattr(jobpacker, "CONFIG_PATH", config_path)

        config_with_nones = {
            "default_search": "",
            "default_location": "USA",
            "results_per_site": 15,
            "remote_only": False,
            "job_type": None,
            "job_boards": ["indeed"],
        }

        jobpacker.save_config(config_with_nones)
        loaded = jobpacker.load_config()

        assert loaded["job_type"] is None
