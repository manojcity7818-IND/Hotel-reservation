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
    assert "Bundle and save!" in html
    assert "Coupons &amp; Deals" in html
    assert "Airport transfer" in html
    assert "Day Use" in html
    assert "occupancy" in html


def test_app_calls_all_microservices() -> None:
    js = (PUBLIC / "app.js").read_text(encoding="utf-8")
    assert "/api/v1/hotels" in js
    assert "/api/v1/rooms" in js
    assert "/api/v1/payments" in js
    assert "/api/v1/bookings" in js
    assert "/api/v1/notifications" in js
    assert 'method: "POST"' in js
    assert 'method: "DELETE"' in js
    assert "Top destinations in India" in js or "dest-card" in js
    assert "Mysore" in js
    assert "Udaipur" in js
    assert "localhost:8025" in js


def test_styles_exist() -> None:
    css = (PUBLIC / "styles.css").read_text(encoding="utf-8")
    assert ".promo-hero" in css
    assert ".search-panel" in css
    assert ".dest-card" in css
    assert "--agoda-pink" in css
    assert ".hotel-row" in css
    assert "/images/hero-background.png" in css
    assert "#home-page" in css
    assert ".occupancy" in css
    assert ".nav-dropdown" in css


def test_nginx_proxies_every_service() -> None:
    nginx = (PUBLIC.parent / "nginx.conf").read_text(encoding="utf-8")
    assert "http://hotel-service:8000" in nginx
    assert "http://room-service:8000" in nginx
    assert "http://booking-service:8000" in nginx
    assert "http://payment-service:8000" in nginx
    assert "http://notification-service:8000" in nginx
    assert "/api/v1/notifications" in nginx


def test_app_covers_booking_email_and_occupancy() -> None:
    js = (PUBLIC / "app.js").read_text(encoding="utf-8")
    html = (PUBLIC / "index.html").read_text(encoding="utf-8")
    assert "bindOccupancy" in js
    assert "data-stay" in js
    assert "renderNotifications" in js
    assert "notifications?booking_id" in js
    assert "#/coupons" in js or "coupons" in js
    assert "#/bundle" in js or "bundle" in js
    assert "http://localhost:8025" in html or "localhost:8025" in html
    assert "Mailpit" in html or "8025" in html
