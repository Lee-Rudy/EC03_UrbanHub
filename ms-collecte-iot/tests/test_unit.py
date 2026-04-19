from app.main import health


def test_health_returns_ok():
    result = health()
    assert result["status"] == "ok"


def test_health_returns_correct_service():
    result = health()
    assert result["service"] == "ms-collecte-iot"
