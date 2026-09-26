from pytest import MonkeyPatch

from app.core.config import Settings


def test_cors_origins_accept_comma_separated_environment_value(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setenv("BACKEND_CORS_ORIGINS", "https://app.example.com,https://admin.example.com")
    settings = Settings(_env_file=None)
    assert settings.backend_cors_origins == [
        "https://app.example.com",
        "https://admin.example.com",
    ]
