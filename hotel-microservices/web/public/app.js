const app = document.getElementById("app");
const homePage = document.getElementById("home-page");
const toastEl = document.getElementById("toast");

const TOP_CITIES = [
  { name: "Bangalore", className: "city-bangalore" },
  { name: "Mumbai", className: "city-mumbai" },
  { name: "New Delhi", className: "city-newdelhi" },
  { name: "Hyderabad", className: "city-hyderabad" },
  { name: "Chennai", className: "city-chennai" },
  { name: "Goa", className: "city-goa" },
  { name: "Jaipur", className: "city-jaipur" },
  { name: "Pune", className: "city-pune" },
  { name: "Kolkata", className: "city-kolkata" },
  { name: "Kochi", className: "city-kochi" },
  { name: "Mysore", className: "city-mysore" },
  { name: "Udaipur", className: "city-udaipur" },
];

function cityClass(city) {
  return (
    {
      bangalore: "city-bangalore",
      mumbai: "city-mumbai",
      "new delhi": "city-newdelhi",
      hyderabad: "city-hyderabad",
      chennai: "city-chennai",
      goa: "city-goa",
      jaipur: "city-jaipur",
      pune: "city-pune",
      kolkata: "city-kolkata",
      kochi: "city-kochi",
      mysore: "city-mysore",
      udaipur: "city-udaipur",
    }[(city || "").toLowerCase()] || "city-pune"
  );
}

function isoDate(offsetDays) {
  const date = new Date();
  date.setDate(date.getDate() + offsetDays);
  return date.toISOString().slice(0, 10);
}

function formatLongDate(value) {
  return new Date(`${value}T00:00:00`).toLocaleDateString("en-IN", {
    weekday: "long",
    day: "numeric",
    month: "short",
    year: "numeric",
  });
}

function nightsBetween(checkIn, checkOut) {
  const start = new Date(`${checkIn}T00:00:00`);
  const end = new Date(`${checkOut}T00:00:00`);
  return Math.max(1, Math.round((end - start) / 86400000));
}

function money(value) {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  }).format(value);
}

function showToast(message) {
  toastEl.hidden = false;
  toastEl.textContent = message;
  clearTimeout(showToast.timer);
  showToast.timer = setTimeout(() => {
    toastEl.hidden = true;
  }, 2800);
}

function showHome(isHome) {
  homePage.hidden = !isHome;
  app.hidden = isHome;
}

async function api(path, options = {}) {
  const response = await fetch(path, {
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options,
  });
  if (response.status === 204) return null;
  let body = null;
  try {
    body = await response.json();
  } catch {
    body = null;
  }
  if (!response.ok) {
    const detail = body && body.detail ? body.detail : `Request failed (${response.status})`;
    throw new Error(detail);
  }
  return body;
}

function parseRoute() {
  const raw = (window.location.hash || "#/").replace(/^#/, "");
  const [pathPart, queryPart] = raw.split("?");
  const parts = pathPart.split("/").filter(Boolean);
  const query = new URLSearchParams(queryPart || "");
  if (parts.length === 0) return { name: "home", query };
  if (parts[0] === "hotels" && parts[1]) return { name: "hotel", id: Number(parts[1]), query };
  if (parts[0] === "hotels") return { name: "hotels", query };
  if (parts[0] === "book" && parts[1]) {
    return { name: "book", roomId: Number(parts[1]), hotelId: Number(parts[2] || 0), query };
  }
  if (parts[0] === "pay" && parts[1]) return { name: "pay", bookingId: Number(parts[1]), query };
  if (parts[0] === "bookings") return { name: "bookings", query };
  return { name: "home", query };
}

function searchPanel(defaults = {}, formId = "search-form") {
  const checkIn = defaults.check_in || isoDate(10);
  const checkOut = defaults.check_out || isoDate(12);
  const destination = defaults.q || defaults.city || "Bangalore";
  return `
    <form class="search-panel" id="${formId}">
      <div class="search-tabs">
        <button type="button" class="search-tab active">Hotels</button>
        <button type="button" class="search-tab">Flights</button>
        <button type="button" class="search-tab">Homes &amp; Apts</button>
        <button type="button" class="search-tab">Flight + Hotel</button>
        <button type="button" class="search-tab">Activities</button>
        <button type="button" class="search-tab">Airport transfer</button>
      </div>
      <div class="stay-row">
        <button type="button" class="stay-pill active" data-stay="overnight">Overnight Stays</button>
        <button type="button" class="stay-pill" data-stay="dayuse">Day Use Stays</button>
      </div>
      <label class="field field-wide">
        <span class="field-icon">⌕</span>
        <input name="q" value="${destination}" placeholder="Enter a destination or property" />
      </label>
      <div class="field-row">
        <label class="field"><span class="field-label">Check-in</span>
          <input name="check_in" type="date" value="${checkIn}" />
        </label>
        <label class="field"><span class="field-label">Check-out</span>
          <input name="check_out" type="date" value="${checkOut}" />
        </label>
        <label class="field"><span class="field-label">Guests</span>
          <input name="guests" value="${defaults.guests || "2 adults, 1 room"}" />
        </label>
      </div>
      <div class="search-extra">
        <label class="check"><input type="checkbox" /> Show me only entire homes and apartments</label>
        <button type="button" class="text-link">+ Add a flight</button>
      </div>
      <button class="search-cta" type="submit">SEARCH</button>
    </form>
  `;
}

function bindSearch(form) {
  if (!form || form.dataset.bound === "true") return;
  form.dataset.bound = "true";
  form.querySelectorAll("[data-stay]").forEach((pill) => {
    pill.addEventListener("click", () => {
      form.querySelectorAll("[data-stay]").forEach((item) => item.classList.remove("active"));
      pill.classList.add("active");
    });
  });
  form.addEventListener("submit", (event) => {
    event.preventDefault();
    const data = new FormData(form);
    const params = new URLSearchParams({
      q: String(data.get("q") || "").trim(),
      check_in: String(data.get("check_in") || ""),
      check_out: String(data.get("check_out") || ""),
      guests: String(data.get("guests") || "2 adults, 1 room"),
    });
    sessionStorage.setItem("aryanstaysSearch", params.toString());
    window.location.hash = `#/hotels?${params.toString()}`;
  });
}

function lowestPrice(hotelId, rooms) {
  const prices = rooms.filter((room) => room.hotel_id === hotelId).map((room) => room.price_per_night);
  return prices.length ? Math.min(...prices) : null;
}

function renderDestinations(hotels) {
  const counts = hotels.reduce((acc, hotel) => {
    acc[hotel.city] = (acc[hotel.city] || 0) + 1;
    return acc;
  }, {});
  const target = document.getElementById("destinations");
  if (!target) return;
  target.innerHTML = TOP_CITIES.map((city) => {
    const count = counts[city.name] || 0;
    return `
      <a class="dest-card" href="#/hotels?q=${encodeURIComponent(city.name)}">
        <div class="dest-photo ${city.className}">${city.name}</div>
        <h3>${city.name}</h3>
        <p>${count} hotel${count === 1 ? "" : "s"}</p>
      </a>
    `;
  }).join("");
}

function renderHotelList(selector, hotels, rooms) {
  const target = document.querySelector(selector);
  if (!target) return;
  if (!hotels.length) {
    target.innerHTML = `<div class="empty">No hotels match that destination. Try Bangalore, Mumbai, Hyderabad, Mysore or Udaipur.</div>`;
    return;
  }
  target.innerHTML = hotels
    .map((hotel) => {
      const price = lowestPrice(hotel.id, rooms);
      return `
        <article class="hotel-row">
          <div class="hotel-photo ${cityClass(hotel.city)}">${hotel.city}</div>
          <div class="hotel-info">
            <h3>${hotel.name}</h3>
            <p><span class="rating-pill">${hotel.rating.toFixed(1)}</span> Excellent · ${hotel.city}</p>
            <p class="muted">Free cancellation on selected rooms · Breakfast available · Pay at hotel</p>
          </div>
          <div class="hotel-price">
            <span class="muted">From</span>
            <strong>${price ? money(price) : "—"}</strong>
            <span class="muted">per night</span>
            <a class="btn" href="#/hotels/${hotel.id}">Select room</a>
          </div>
        </article>
      `;
    })
    .join("");
}

async function renderHome() {
  showHome(true);
  const homeForm = document.getElementById("home-search-form");
  if (homeForm) {
    homeForm.check_in.value = homeForm.check_in.value || isoDate(10);
    homeForm.check_out.value = homeForm.check_out.value || isoDate(12);
    bindSearch(homeForm);
  }
  try {
    const [hotels, rooms] = await Promise.all([api("/api/v1/hotels"), api("/api/v1/rooms")]);
    renderDestinations(hotels);
    renderHotelList("#popular-hotels", hotels.slice(0, 8), rooms);
  } catch (error) {
    const dest = document.getElementById("destinations");
    if (dest) dest.innerHTML = `<div class="error">${error.message}</div>`;
  }
}

async function renderHotels(query) {
  showHome(false);
  const q = query.get("q") || query.get("city") || "";
  const checkIn = query.get("check_in") || isoDate(10);
  const checkOut = query.get("check_out") || isoDate(12);
  app.innerHTML = `
    <section class="promo-hero">
      <div class="promo-copy">
        <p class="promo-kicker">Limited-time deal</p>
        <h1>MEGA SALE</h1>
        <p class="promo-off">Up to 60% Off!</p>
      </div>
      ${searchPanel({ q, check_in: checkIn, check_out: checkOut, guests: query.get("guests") })}
    </section>
    <div class="results-layout">
      <aside class="filters">
        <h3>Filter by</h3>
        <label><input type="checkbox" checked /> Hotels</label>
        <label><input type="checkbox" checked /> Homes &amp; apartments</label>
        <label><input type="checkbox" /> Free breakfast</label>
        <label><input type="checkbox" /> Free cancellation</label>
        <p class="muted">Results are loaded from Hotel Service and priced from Room Service.</p>
      </aside>
      <section>
        <h2>${q ? `Hotels in ${q}` : "All hotels"}</h2>
        <p class="muted" id="results-meta">Searching Aryanstays…</p>
        <div class="hotel-list" id="hotel-results"></div>
      </section>
    </div>
  `;
  bindSearch(document.getElementById("search-form"));
  try {
    const path = q ? `/api/v1/hotels?q=${encodeURIComponent(q)}` : "/api/v1/hotels";
    const [hotels, rooms] = await Promise.all([api(path), api("/api/v1/rooms")]);
    document.getElementById("results-meta").textContent =
      `${hotels.length} properties found · ${formatLongDate(checkIn)} – ${formatLongDate(checkOut)}`;
    renderHotelList("#hotel-results", hotels, rooms);
  } catch (error) {
    document.getElementById("hotel-results").innerHTML = `<div class="error">${error.message}</div>`;
  }
}

async function renderHotel(hotelId) {
  showHome(false);
  app.innerHTML = `<section class="page-width"><p class="muted">Loading property…</p></section>`;
  try {
    const [hotel, rooms] = await Promise.all([
      api(`/api/v1/hotels/${hotelId}`),
      api(`/api/v1/rooms/hotel/${hotelId}`),
    ]);
    app.innerHTML = `
      <section class="promo-hero">
        <div class="promo-copy">
          <p class="promo-kicker">${hotel.city}</p>
          <h1>${hotel.name}</h1>
          <p class="promo-off"><span class="rating-pill">${hotel.rating.toFixed(1)}</span> Excellent location</p>
        </div>
      </section>
      <section class="page-width">
        <h2>Choose your room</h2>
        <div class="room-grid">
          ${
            rooms.length
              ? rooms
                  .map(
                    (room) => `
            <article class="card">
              <div class="hotel-photo ${cityClass(hotel.city)}">${room.room_type}</div>
              <div class="card-body">
                <p class="row">
                  <strong>Room ${room.room_number}</strong>
                  <span class="badge ${room.available ? "" : "busy"}">${room.available ? "Available" : "Reserved"}</span>
                </p>
                <p class="muted">${room.room_type}</p>
                <p><strong>${money(room.price_per_night)}</strong> <span class="muted">/ night</span></p>
                ${
                  room.available
                    ? `<a class="btn" href="#/book/${room.id}/${hotel.id}">Book now</a>`
                    : `<button class="btn" disabled>Currently reserved</button>`
                }
              </div>
            </article>`
                  )
                  .join("")
              : `<div class="empty">No rooms listed for this hotel.</div>`
          }
        </div>
      </section>
    `;
  } catch (error) {
    app.innerHTML = `<section class="page-width"><div class="error">${error.message}</div></section>`;
  }
}

async function renderBook(roomId, hotelId) {
  showHome(false);
  app.innerHTML = `<section class="page-width"><p class="muted">Loading booking…</p></section>`;
  try {
    const [room, hotel] = await Promise.all([
      api(`/api/v1/rooms/${roomId}`),
      api(`/api/v1/hotels/${hotelId || room.hotel_id}`),
    ]);
    const saved = new URLSearchParams(sessionStorage.getItem("aryanstaysSearch") || "");
    const checkIn = saved.get("check_in") || isoDate(10);
    const checkOut = saved.get("check_out") || isoDate(12);
    app.innerHTML = `
      <section class="page-width" style="padding-top:32px">
        <h2>Book ${hotel.name}</h2>
        <p class="muted">${hotel.city} · Room ${room.room_number} · ${room.room_type} · ${money(room.price_per_night)} / night</p>
        <form class="form" id="booking-form">
          <label>Full name <input name="customer_name" required placeholder="Aryan Kumar" /></label>
          <label>Email <input name="customer_email" type="email" required placeholder="aryan@example.com" /></label>
          <label>Check-in <input name="check_in" type="date" required min="${isoDate(0)}" value="${checkIn}" /></label>
          <label>Check-out <input name="check_out" type="date" required min="${isoDate(0)}" value="${checkOut}" /></label>
          <button class="btn" type="submit">Continue to payment</button>
        </form>
      </section>
    `;
    document.getElementById("booking-form").addEventListener("submit", async (event) => {
      event.preventDefault();
      const form = new FormData(event.target);
      const payload = Object.fromEntries(form.entries());
      payload.hotel_id = hotel.id;
      payload.room_id = room.id;
      payload.amount = nightsBetween(payload.check_in, payload.check_out) * room.price_per_night;
      const button = event.target.querySelector("button");
      button.disabled = true;
      try {
        const booking = await api("/api/v1/bookings", { method: "POST", body: JSON.stringify(payload) });
        showToast("Room reserved. Complete payment to confirm.");
        window.location.hash = `#/pay/${booking.booking_id}`;
      } catch (error) {
        showToast(error.message);
        button.disabled = false;
      }
    });
  } catch (error) {
    app.innerHTML = `<section class="page-width"><div class="error">${error.message}</div></section>`;
  }
}

async function renderPay(bookingId) {
  showHome(false);
  app.innerHTML = `<section class="page-width"><p class="muted">Loading payment…</p></section>`;
  try {
    const [booking, methods] = await Promise.all([
      api(`/api/v1/bookings/${bookingId}`),
      api("/api/v1/payments/methods"),
    ]);
    if (booking.status === "CONFIRMED") {
      window.location.hash = "#/bookings";
      return;
    }
    app.innerHTML = `
      <section class="page-width" style="padding-top:32px">
        <h2>Pay for booking #${booking.booking_id}</h2>
        <p class="muted">Amount payable: <strong>${money(booking.amount)}</strong></p>
        <form class="form" id="payment-form">
          <div class="pay-methods">
            ${methods
              .map(
                (item, index) => `
              <label class="pay-method">
                <input type="radio" name="method" value="${item.method}" ${index === 0 ? "checked" : ""} />
                <strong>${item.label}</strong>
                <span>${item.description}</span>
              </label>`
              )
              .join("")}
          </div>
          <label>Payer name <input name="payer_name" required value="${booking.customer_name}" /></label>
          <div id="method-fields"></div>
          <button class="btn" type="submit">Pay ${money(booking.amount)}</button>
        </form>
      </section>
    `;
    const form = document.getElementById("payment-form");
    const fields = document.getElementById("method-fields");
    const renderFields = () => {
      const method = form.method.value;
      if (method === "UPI") {
        fields.innerHTML = `<label>UPI ID <input name="upi_id" required placeholder="name@upi" /></label>`;
      } else if (method === "CARD") {
        fields.innerHTML = `
          <label>Card holder <input name="card_holder" required /></label>
          <label>Card number <input name="card_number" required placeholder="4111 1111 1111 1111" /></label>
        `;
      } else if (method === "NET_BANKING") {
        fields.innerHTML = `<label>Bank name <input name="bank_name" required placeholder="HDFC, SBI, ICICI" /></label>`;
      } else {
        fields.innerHTML = `<label>Wallet <input name="wallet_name" required placeholder="Paytm, Amazon Pay" /></label>`;
      }
    };
    form.querySelectorAll("input[name=method]").forEach((input) => input.addEventListener("change", renderFields));
    renderFields();
    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      const data = Object.fromEntries(new FormData(form).entries());
      data.booking_id = booking.booking_id;
      data.amount = booking.amount;
      const button = form.querySelector("button");
      button.disabled = true;
      try {
        const payment = await api("/api/v1/payments", { method: "POST", body: JSON.stringify(data) });
        await api(`/api/v1/bookings/${booking.booking_id}/pay`, {
          method: "POST",
          body: JSON.stringify({ payment_id: payment.payment_id }),
        });
        showToast("Payment successful. Booking confirmed.");
        window.location.hash = "#/bookings";
      } catch (error) {
        showToast(error.message);
        button.disabled = false;
      }
    });
  } catch (error) {
    app.innerHTML = `<section class="page-width"><div class="error">${error.message}</div></section>`;
  }
}

async function renderBookings() {
  showHome(false);
  app.innerHTML = `<section class="page-width"><h2>My bookings</h2><p class="muted">Loading…</p></section>`;
  try {
    const bookings = await api("/api/v1/bookings");
    app.innerHTML = `
      <section class="page-width" style="padding-top:32px">
        <h2>My bookings</h2>
        ${
          bookings.length
            ? `<div class="hotel-list">${bookings
                .map(
                  (booking) => `
          <article class="card"><div class="card-body">
            <p class="row"><strong>Booking #${booking.booking_id}</strong>
            <span class="badge ${booking.status === "CANCELLED" ? "cancelled" : ""}">${booking.status}</span></p>
            <p>${booking.customer_name} · ${booking.customer_email}</p>
            <p class="muted">${booking.check_in} to ${booking.check_out}</p>
            <p class="muted">Hotel ${booking.hotel_id} · Room ${booking.room_id}</p>
            ${
                booking.status === "PENDING_PAYMENT"
                  ? `<a class="btn" href="#/pay/${booking.booking_id}">Pay now</a>`
                  : ""
              }
            ${booking.status === "CONFIRMED" || booking.status === "PENDING_PAYMENT" ? `<button class="btn danger" data-cancel="${booking.booking_id}">Cancel booking</button>` : ""}
          </div></article>`
                )
                .join("")}</div>`
            : `<div class="empty">You have no bookings yet. Search a destination to get started.</div>`
        }
      </section>
    `;
    app.querySelectorAll("[data-cancel]").forEach((button) => {
      button.addEventListener("click", async () => {
        button.disabled = true;
        try {
          await api(`/api/v1/bookings/${button.dataset.cancel}`, { method: "DELETE" });
          showToast("Booking cancelled and room released");
          renderBookings();
        } catch (error) {
          showToast(error.message);
          button.disabled = false;
        }
      });
    });
  } catch (error) {
    app.innerHTML = `<section class="page-width"><div class="error">${error.message}</div></section>`;
  }
}

function render() {
  const current = parseRoute();
  if (current.name === "hotels") return renderHotels(current.query);
  if (current.name === "hotel") return renderHotel(current.id);
  if (current.name === "book") return renderBook(current.roomId, current.hotelId);
  if (current.name === "pay") return renderPay(current.bookingId);
  if (current.name === "bookings") return renderBookings();
  return renderHome();
}

window.addEventListener("hashchange", render);
render();
