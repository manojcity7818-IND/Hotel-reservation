from pathlib import Path

PUBLIC = Path(__file__).resolve().parents[1] / "public"


def test_index_contains_app_shell() -> None:
    html = (PUBLIC / "index.html").read_text(encoding="utf-8")
    assert "StayWell" in html
    assert "/app.js" in html
    assert "/styles.css" in html
    assert "#/hotels" in html
    assert "#/bookings" in html


def test_app_calls_all_microservices() -> None:
    js = (PUBLIC / "app.js").read_text(encoding="utf-8")
    assert "/api/v1/hotels" in js
    assert "/api/v1/rooms" in js
    assert "/api/v1/bookings" in js
    assert 'method: "POST"' in js
    assert 'method: "DELETE"' in js


def test_styles_exist() -> None:
    css = (PUBLIC / "styles.css").read_text(encoding="utf-8")
    assert ".hero" in css
    assert ".card" in css
