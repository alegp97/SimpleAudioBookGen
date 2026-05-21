from audiobook_gen.config import Settings


def test_tts_language_is_saved_and_loaded(tmp_path):
    config_path = tmp_path / "config.yaml"
    settings = Settings()
    settings.tts.engine = "piper"
    settings.tts.language = "English"
    settings.tts.voice = "en_US-lessac-medium"
    settings.normalization_rules_path = "custom_rules.yaml"

    settings.save_yaml(config_path)
    loaded = Settings.from_yaml(config_path)

    assert loaded.tts.engine == "piper"
    assert loaded.tts.language == "English"
    assert loaded.tts.voice == "en_US-lessac-medium"
    assert loaded.normalization_rules_path == "custom_rules.yaml"
