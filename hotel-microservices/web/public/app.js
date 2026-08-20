const app = document.getElementById("app");
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
  if (parts[0] === "hotels" && parts[1]) {
    return { name: "hotel", id: Number(parts[1]), query };
  }
  if (parts[0] === "hotels") return { name: "hotels", query };
  if (parts[0] === "book" && parts[1]) {
    return { name: "book", roomId: Number(parts[1]), hotelId: Number(parts[2] || 0), query };
  }
  if (parts[0] === "bookings") return { name: "bookings", query };
  return { name: "home", query };
}

function searchBox(defaults = {}) {
  const checkIn = defaults.check_in || isoDate(10);
  const checkOut = defaults.check_out || isoDate(12);
  const destination = defaults.city || defaults.q || "";
  return `
    <form class="search-card" id="search-form">
      <div class="search-tabs">
        <button type="button" class="search-tab active">Hotels</button>
        <button type="button" class="search-tab">Flights</button>
        <button type="button" class="search-tab">Homes &amp; Apts</button>
        <button type="button" class="search-tab">Flight + Hotel</button>
        <button type="button" class="search-tab">Activities</button>
        <button type="button" class="search-tab">Airport transfer</button>
      </div>
      <div class="stay-toggles">
        <button type="button" class="pill active" data-stay="overnight">Overnight Stays</button>
        <button type="button" class="pill" data-stay="dayuse">Day Use Stays</button>
      </div>
      <div class="search-grid">
        <label class="search-field">
          <span>⌕</span>
          <input name="q" value="${destination}" placeholder="Enter a destination or property" required />
        </label>
        <div class="date-row">
          <label class="search-field">
            <span>📅</span>
            <input name="check_in" type="date" value="${checkIn}" required />
          </label>
          <label class="search-field">
            <span>📅</span>
            <input name="check_out" type="date" value="${checkOut}" required />
          </label>
          <label class="search-field">
            <span>👤</span>
            <input name="guests" value="2 adults, 1 room" />
          </label>
        </div>
      </div>
      <div class="search-actions">
        <label class="checkbox">
          <input type="checkbox" name="homes_only" />
          Show me only entire homes and apartments
        </label>
        <span style="color:var(--blue);font-weight:700">+ Add a flight</span>
      </div>
      <button class="search-btn" type="submit">SEARCH</button>
    </form>
  `;
}

function bindSearch(form) {
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

async function renderHome() {
  app.innerHTML = `
    <section class="hero">
      <p class="hero-kicker">MEGA SALE</p>
      <p class="hero-sub">Up to 60% Off!</p>
    </section>
    ${searchBox()}
    <section class="section">
      <h2>Top destinations in India</h2>
      <div class="dest-row" id="destinations"><p class="muted">Loading destinations…</p></div>
    </section>
    <section class="section">
      <h2>Popular hotels on Aryanstays</h2>
      <div class="hotel-list" id="popular-hotels"><p class="muted">Loading hotels…</p></div>
    </section>
  `;
  bindSearch(document.getElementById("search-form"));
  try {
    const [hotels, rooms] = await Promise.all([api("/api/v1/hotels"), api("/api/v1/rooms")]);
    renderDestinations(hotels);
    renderHotelList("#popular-hotels", hotels.slice(0, 6), rooms);
  } catch (error) {
    document.getElementById("destinations").innerHTML = `<div class="error">${error.message}</div>`;
  }
}

function renderDestinations(hotels) {
  const counts = hotels.reduce((acc, hotel) => {
    acc[hotel.city] = (acc[hotel.city] || 0) + 1;
    return acc;
  }, {});
  document.getElementById("destinations").innerHTML = TOP_CITIES.map((city) => {
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

function lowestPrice(hotelId, rooms) {
  const prices = rooms.filter((room) => room.hotel_id === hotelId).map((room) => room.price_per_night);
  return prices.length ? Math.min(...prices) : null;
}

function renderHotelList(selector, hotels, rooms) {
  const target = document.querySelector(selector);
  if (!hotels.length) {
    target.innerHTML = `<div class="empty">No hotels match that destination. Try Bangalore, Mumbai, New Delhi, Hyderabad or Goa.</div>`;
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
            <p><span class="rating-pill">${hotel.rating.toFixed(1)}</span> ${hotel.city}</p>
            <p class="muted">Free cancellation on selected rooms · Breakfast available</p>
          </div>
          <div class="hotel-price">
            <span class="muted">From</span>
            <strong>${price ? money(price) : "—"}</strong>
            <a class="btn" href="#/hotels/${hotel.id}">Select room</a>
          </div>
        </article>
      `;
    })
    .join("");
}

async function renderHotels(query) {
  const q = query.get("q") || query.get("city") || "";
  const checkIn = query.get("check_in") || isoDate(10);
  const checkOut = query.get("check_out") || isoDate(12);
  app.innerHTML = `
    <section class="hero">
      <p class="hero-kicker">MEGA SALE</p>
      <p class="hero-sub">Up to 60% Off!</p>
    </section>
    ${searchBox({ q, city: q, check_in: checkIn, check_out: checkOut })}
    <section class="section">
      <h2>${q ? `Hotels in ${q}` : "All hotels"}</h2>
      <p class="results-meta" id="results-meta">Searching Aryanstays…</p>
      <div class="hotel-list" id="hotel-results"></div>
    </section>
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
  app.innerHTML = `<section class="section"><p class="muted">Loading property…</p></section>`;
  try {
    const [hotel, rooms] = await Promise.all([
      api(`/api/v1/hotels/${hotelId}`),
      api(`/api/v1/rooms/hotel/${hotelId}`),
    ]);
    app.innerHTML = `
      <section class="hero">
        <p class="hero-kicker">${hotel.city}</p>
        <p class="hero-sub">${hotel.name}</p>
      </section>
      <section class="section">
        <p><span class="rating-pill">${hotel.rating.toFixed(1)}</span> Excellent location in ${hotel.city}</p>
        <h2>Choose your room</h2>
        <div class="room-grid">
          ${
            rooms.length
              ? rooms
                  .map(
                    (room) => `
            <article class="card">
              <div class="hotel-photo ${cityClass(hotel.city)}" style="min-height:110px">${room.room_type}</div>
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
    app.innerHTML = `<section class="section"><div class="error">${error.message}</div></section>`;
  }
}

async function renderBook(roomId, hotelId) {
  app.innerHTML = `<section class="section"><p class="muted">Loading booking…</p></section>`;
  try {
    const [room, hotel] = await Promise.all([
      api(`/api/v1/rooms/${roomId}`),
      api(`/api/v1/hotels/${hotelId || room.hotel_id}`),
    ]);
    const saved = new URLSearchParams(sessionStorage.getItem("aryanstaysSearch") || "");
    const checkIn = saved.get("check_in") || isoDate(10);
    const checkOut = saved.get("check_out") || isoDate(12);
    app.innerHTML = `
      <section class="section">
        <h2>Book ${hotel.name}</h2>
        <p class="muted">${hotel.city} · Room ${room.room_number} · ${room.room_type} · ${money(room.price_per_night)} / night</p>
        <form class="form" id="booking-form">
          <label>Full name
            <input name="customer_name" required placeholder="Aryan Kumar" />
          </label>
          <label>Email
            <input name="customer_email" type="email" required placeholder="aryan@example.com" />
          </label>
          <label>Check-in
            <input name="check_in" type="date" required min="${isoDate(0)}" value="${checkIn}" />
          </label>
          <label>Check-out
            <input name="check_out" type="date" required min="${isoDate(0)}" value="${checkOut}" />
          </label>
          <button class="btn" type="submit">Confirm booking</button>
        </form>
      </section>
    `;
    document.getElementById("booking-form").addEventListener("submit", async (event) => {
      event.preventDefault();
      const form = new FormData(event.target);
      const payload = Object.fromEntries(form.entries());
      payload.hotel_id = hotel.id;
      payload.room_id = room.id;
      const button = event.target.querySelector("button");
      button.disabled = true;
      try {
        await api("/api/v1/bookings", {
          method: "POST",
          body: JSON.stringify(payload),
        });
        showToast("Booking confirmed on Aryanstays");
        window.location.hash = "#/bookings";
      } catch (error) {
        showToast(error.message);
        button.disabled = false;
      }
    });
  } catch (error) {
    app.innerHTML = `<section class="section"><div class="error">${error.message}</div></section>`;
  }
}

async function renderBookings() {
  app.innerHTML = `<section class="section"><h2>My bookings</h2><p class="muted">Loading…</p></section>`;
  try {
    const bookings = await api("/api/v1/bookings");
    app.innerHTML = `
      <section class="section">
        <h2>My bookings</h2>
        ${
          bookings.length
            ? `<div class="hotel-list">${bookings
                .map(
                  (booking) => `
          <article class="card">
            <div class="card-body">
              <p class="row">
                <strong>Booking #${booking.booking_id}</strong>
                <span class="badge ${booking.status === "CANCELLED" ? "cancelled" : ""}">${booking.status}</span>
              </p>
              <p>${booking.customer_name} · ${booking.customer_email}</p>
              <p class="muted">${booking.check_in} to ${booking.check_out}</p>
              <p class="muted">Hotel ${booking.hotel_id} · Room ${booking.room_id}</p>
              ${
                booking.status === "CONFIRMED"
                  ? `<button class="btn danger" data-cancel="${booking.booking_id}">Cancel booking</button>`
                  : ""
              }
            </div>
          </article>`
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
    app.innerHTML = `<section class="section"><div class="error">${error.message}</div></section>`;
  }
}

function render() {
  const current = parseRoute();
  if (current.name === "hotels") return renderHotels(current.query);
  if (current.name === "hotel") return renderHotel(current.id);
  if (current.name === "book") return renderBook(current.roomId, current.hotelId);
  if (current.name === "bookings") return renderBookings();
  return renderHome();
}

window.addEventListener("hashchange", render);
render();
