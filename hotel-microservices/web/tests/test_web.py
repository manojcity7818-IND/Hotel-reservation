from pathlib import Path

PUBLIC = Path(__file__).resolve().parents[1] / "public"


def test_index_contains_app_shell() -> None:
    html = (PUBLIC / "index.html").read_text(encoding="utf-8")
    assert "Aryanstays" in html
    assert "MEGA SALE" in html
    assert "Enter a destination or property" in html
    assert "Top destinations in India" in html
    assert "Overnight Stays" in html
    assert "/app.js" in html
    assert "/styles.css" in html
    assert "#/hotels" in html
    assert "#/bookings" in html
    assert "/images/hero-background.png" in html


def test_app_calls_all_microservices() -> None:
    js = (PUBLIC / "app.js").read_text(encoding="utf-8")
    assert "/api/v1/hotels" in js
    assert "/api/v1/rooms" in js
    assert "/api/v1/payments" in js
    assert "/api/v1/bookings" in js
    assert 'method: "POST"' in js
    assert 'method: "DELETE"' in js
    assert "Top destinations in India" in js or "dest-card" in js
    assert "Mysore" in js
    assert "Udaipur" in js


def test_styles_exist() -> None:
    css = (PUBLIC / "styles.css").read_text(encoding="utf-8")
    assert ".promo-hero" in css
    assert ".search-panel" in css
    assert ".dest-card" in css
    assert "--agoda-pink" in css
    assert ".hotel-row" in css
    assert "/images/hero-background.png" in css
    assert "#home-page" in css
    assert (PUBLIC / "images" / "hero-background.png").is_file()
