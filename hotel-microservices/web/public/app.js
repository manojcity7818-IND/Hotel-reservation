const app = document.getElementById("app");
const toastEl = document.getElementById("toast");

function coverClass(hotel) {
  const city = (hotel.city || "").toLowerCase();
  if (city.includes("hyderabad")) return "hyderabad";
  if (city.includes("bangalore") || city.includes("bengaluru")) return "bangalore";
  return "generic";
}

function money(value) {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  }).format(value);
}

function stars(rating) {
  const filled = Math.round(rating);
  return "★".repeat(filled) + "☆".repeat(Math.max(0, 5 - filled)) + ` ${rating}`;
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

function route() {
  const hash = window.location.hash || "#/";
  const parts = hash.replace(/^#/, "").split("/").filter(Boolean);
  if (parts.length === 0) return { name: "home" };
  if (parts[0] === "hotels" && parts[1]) return { name: "hotel", id: Number(parts[1]) };
  if (parts[0] === "hotels") return { name: "hotels" };
  if (parts[0] === "book" && parts[1]) {
    return { name: "book", roomId: Number(parts[1]), hotelId: Number(parts[2] || 0) };
  }
  if (parts[0] === "bookings") return { name: "bookings" };
  return { name: "home" };
}

function renderHome() {
  app.innerHTML = `
    <section class="hero">
      <h1>Find a room. Book in minutes.</h1>
      <p>Browse hotels in Hyderabad and Bangalore, check live room availability, and complete a stay through the Booking service.</p>
      <p><a class="btn" href="#/hotels">Browse hotels</a></p>
    </section>
    <section class="section" id="featured">
      <h2>Featured hotels</h2>
      <div class="grid" id="hotel-grid"><p class="muted">Loading hotels…</p></div>
    </section>
  `;
  loadHotels("#hotel-grid");
}

async function loadHotels(selector) {
  const target = document.querySelector(selector);
  try {
    const hotels = await api("/api/v1/hotels");
    if (!hotels.length) {
      target.innerHTML = `<div class="empty">No hotels found.</div>`;
      return;
    }
    target.innerHTML = hotels
      .map(
        (hotel) => `
      <article class="card">
        <div class="cover ${coverClass(hotel)}">${hotel.city}</div>
        <div class="card-body">
          <h3>${hotel.name}</h3>
          <p class="muted">${stars(hotel.rating)}</p>
          <p class="row">
            <span class="muted">Hotel #${hotel.id}</span>
            <a class="btn" href="#/hotels/${hotel.id}">View rooms</a>
          </p>
        </div>
      </article>`
      )
      .join("");
  } catch (error) {
    target.innerHTML = `<div class="error">${error.message}</div>`;
  }
}

function renderHotels() {
  app.innerHTML = `
    <section class="section">
      <h2>All hotels</h2>
      <div class="grid" id="hotel-grid"><p class="muted">Loading hotels…</p></div>
    </section>
  `;
  loadHotels("#hotel-grid");
}

async function renderHotel(hotelId) {
  app.innerHTML = `<section class="section"><p class="muted">Loading hotel…</p></section>`;
  try {
    const [hotel, rooms] = await Promise.all([
      api(`/api/v1/hotels/${hotelId}`),
      api(`/api/v1/rooms/hotel/${hotelId}`),
    ]);
    app.innerHTML = `
      <section class="hero">
        <p class="muted" style="color:#f6f1e8">${hotel.city}</p>
        <h1>${hotel.name}</h1>
        <p>${stars(hotel.rating)}</p>
      </section>
      <section class="section">
        <h2>Available rooms</h2>
        <div class="grid">
          ${
            rooms.length
              ? rooms
                  .map(
                    (room) => `
            <article class="card">
              <div class="card-body">
                <p class="row">
                  <strong>Room ${room.room_number}</strong>
                  <span class="badge ${room.available ? "" : "busy"}">${
                      room.available ? "Available" : "Reserved"
                    }</span>
                </p>
                <p class="muted">${room.room_type}</p>
                <p class="room-price">${money(room.price_per_night)} / night</p>
                <p>
                  ${
                    room.available
                      ? `<a class="btn" href="#/book/${room.id}/${hotel.id}">Book this room</a>`
                      : `<button class="btn" disabled>Currently reserved</button>`
                  }
                </p>
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
  app.innerHTML = `<section class="section"><p class="muted">Loading room…</p></section>`;
  try {
    const [room, hotel] = await Promise.all([
      api(`/api/v1/rooms/${roomId}`),
      api(`/api/v1/hotels/${hotelId || room.hotel_id}`),
    ]);
    const today = new Date().toISOString().slice(0, 10);
    app.innerHTML = `
      <section class="section">
        <h2>Book ${hotel.name}</h2>
        <p class="muted">Room ${room.room_number} · ${room.room_type} · ${money(room.price_per_night)} / night</p>
        <form class="form" id="booking-form">
          <label>Full name
            <input name="customer_name" required placeholder="John Doe" />
          </label>
          <label>Email
            <input name="customer_email" type="email" required placeholder="john@example.com" />
          </label>
          <label>Check-in
            <input name="check_in" type="date" required min="${today}" value="${today}" />
          </label>
          <label>Check-out
            <input name="check_out" type="date" required min="${today}" />
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
        const booking = await api("/api/v1/bookings", {
          method: "POST",
          body: JSON.stringify(payload),
        });
        showToast("Booking confirmed");
        window.location.hash = "#/bookings";
        sessionStorage.setItem("lastBookingId", String(booking.booking_id));
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
            ? `<div class="grid">${bookings
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
            : `<div class="empty">You have no bookings yet. Choose a hotel to get started.</div>`
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
  const current = route();
  if (current.name === "hotels") return renderHotels();
  if (current.name === "hotel") return renderHotel(current.id);
  if (current.name === "book") return renderBook(current.roomId, current.hotelId);
  if (current.name === "bookings") return renderBookings();
  return renderHome();
}

window.addEventListener("hashchange", render);
render();
