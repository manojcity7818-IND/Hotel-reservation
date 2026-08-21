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

const CITY_MAP = {
  "New Delhi": { x: 48, y: 18 },
  Jaipur: { x: 40, y: 26 },
  Udaipur: { x: 36, y: 34 },
  Ahmedabad: { x: 28, y: 38 },
  Mumbai: { x: 30, y: 52 },
  Pune: { x: 34, y: 56 },
  Goa: { x: 32, y: 68 },
  Bangalore: { x: 44, y: 78 },
  Mysore: { x: 40, y: 82 },
  Chennai: { x: 56, y: 80 },
  Hyderabad: { x: 48, y: 62 },
  Kochi: { x: 42, y: 90 },
  Kolkata: { x: 72, y: 42 },
};

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

function formatShortDate(value) {
  return new Date(`${value}T00:00:00`).toLocaleDateString("en-IN", {
    day: "2-digit",
    month: "short",
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

function ratingLabel(rating) {
  if (rating >= 4.7) return "Excellent";
  if (rating >= 4.3) return "Very good";
  if (rating >= 4) return "Good";
  return "Pleasant";
}

function hotelAmenities(hotel) {
  const id = hotel.id || 0;
  const name = hotel.name || "";
  return {
    wifi: true,
    breakfast: id % 2 === 0 || /suites|heritage|palace|grand|resort/i.test(name),
    pool: id % 3 !== 0 || /beach|lake|palace|grand|resort/i.test(name),
    parking: id % 4 !== 1,
    gym: id % 5 === 0 || /business|tech|corporate/i.test(name),
    freeCancel: id % 7 !== 0,
  };
}

function amenityLines(hotel) {
  const a = hotelAmenities(hotel);
  const lines = [];
  if (a.freeCancel) lines.push("Free cancellation");
  if (a.breakfast) lines.push("Breakfast included");
  if (a.pool) lines.push("Swimming pool");
  if (a.parking) lines.push("Parking");
  if (a.wifi) lines.push("Wi-Fi");
  if (a.gym) lines.push("Gym");
  return lines;
}

function favoriteIds() {
  try {
    return new Set(JSON.parse(localStorage.getItem("aryanstaysFavorites") || "[]"));
  } catch {
    return new Set();
  }
}

function toggleFavorite(hotelId) {
  const ids = favoriteIds();
  if (ids.has(hotelId)) ids.delete(hotelId);
  else ids.add(hotelId);
  localStorage.setItem("aryanstaysFavorites", JSON.stringify([...ids]));
  return ids.has(hotelId);
}

function searchDates() {
  const saved = new URLSearchParams(sessionStorage.getItem("aryanstaysSearch") || "");
  return {
    checkIn: saved.get("check_in") || isoDate(10),
    checkOut: saved.get("check_out") || isoDate(12),
    guests: saved.get("guests") || "2 Adults · 1 Room",
    q: saved.get("q") || "",
  };
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
  if (parts[0] === "review" && parts[1]) {
    return { name: "review", roomId: Number(parts[1]), hotelId: Number(parts[2] || 0), query };
  }
  if (parts[0] === "pay" && parts[1]) return { name: "pay", bookingId: Number(parts[1]), query };
  if (parts[0] === "confirmed" && parts[1]) return { name: "confirmed", bookingId: Number(parts[1]), query };
  if (parts[0] === "bookings" || parts[0] === "trips") return { name: "bookings", query };
  if (
    [
      "flights",
      "homes",
      "activities",
      "transfers",
      "coupons",
      "transport",
      "esim",
      "guides",
      "bundle",
      "notifications",
    ].includes(parts[0])
  ) {
    return { name: parts[0], query };
  }
  return { name: "home", query };
}

function occupancyMarkup(guests = "2 Adults · 1 Room") {
  return `
    <div class="occupancy">
      <button type="button" class="field occupancy-trigger" aria-expanded="false">
        <span class="field-icon">👤</span>
        <span>
          <span class="field-label">Guests &amp; rooms</span>
          <strong class="occupancy-label">${guests}</strong>
        </span>
      </button>
      <input type="hidden" name="guests" value="${guests}" />
      <div class="occupancy-menu" hidden>
        <div class="step-row"><span>Adults</span><div><button type="button" data-step="adults" data-dir="-1">−</button><strong data-count="adults">2</strong><button type="button" data-step="adults" data-dir="1">+</button></div></div>
        <div class="step-row"><span>Children</span><div><button type="button" data-step="children" data-dir="-1">−</button><strong data-count="children">0</strong><button type="button" data-step="children" data-dir="1">+</button></div></div>
        <div class="step-row"><span>Rooms</span><div><button type="button" data-step="rooms" data-dir="-1">−</button><strong data-count="rooms">1</strong><button type="button" data-step="rooms" data-dir="1">+</button></div></div>
        <button type="button" class="btn occupancy-apply">Done</button>
      </div>
    </div>
  `;
}

function quickFiltersMarkup(active = "") {
  const chips = [
    ["popular", "🔥 Popular"],
    ["free_cancel", "Free cancellation"],
    ["breakfast", "Breakfast included"],
    ["4star", "4★ &amp; above"],
    ["pool", "Pool"],
    ["parking", "Parking"],
  ];
  return `<div class="quick-filters">${chips
    .map(
      ([key, label]) =>
        `<button type="button" class="chip${active === key ? " active" : ""}" data-filter="${key}">${label}</button>`
    )
    .join("")}</div>`;
}

function searchPanel(defaults = {}, formId = "search-form") {
  const checkIn = defaults.check_in || isoDate(10);
  const checkOut = defaults.check_out || isoDate(12);
  const destination = defaults.q || defaults.city || "Bangalore";
  const guests = defaults.guests || "2 Adults · 1 Room";
  const filter = defaults.filter || "";
  return `
    <form class="search-panel" id="${formId}">
      <div class="search-tabs">
        <button type="button" class="search-tab active" data-tab="hotels">Hotels</button>
        <button type="button" class="search-tab" data-tab="homes">Homes &amp; Apts</button>
        <button type="button" class="search-tab" data-tab="flights">Flights</button>
        <button type="button" class="search-tab" data-tab="activities">Activities</button>
        <button type="button" class="search-tab" data-tab="transfers">Airport transfer</button>
      </div>
      <div class="stay-row">
        <button type="button" class="stay-pill active" data-stay="overnight">Overnight Stays</button>
        <button type="button" class="stay-pill" data-stay="dayuse">Day Use</button>
      </div>
      <label class="field field-wide">
        <span class="field-icon">🔍</span>
        <span>
          <span class="field-label">Where are you going?</span>
          <input name="q" value="${destination}" placeholder="Bangalore, Goa, Hyderabad..." />
        </span>
      </label>
      <div class="field-row">
        <label class="field"><span class="field-label">Check-in</span>
          <input name="check_in" type="date" value="${checkIn}" />
        </label>
        <label class="field checkout-field"><span class="field-label">Check-out</span>
          <input name="check_out" type="date" value="${checkOut}" />
        </label>
        ${occupancyMarkup(guests)}
      </div>
      <div class="search-extra">
        <label class="check"><input type="checkbox" name="homes_only" ${defaults.homes_only === "1" ? "checked" : ""} /> Show me only entire homes and apartments</label>
        <button type="button" class="text-link add-flight">+ Add a flight</button>
      </div>
      <button class="search-cta" type="submit">SEARCH HOTELS</button>
      ${quickFiltersMarkup(filter)}
      <input type="hidden" name="filter" value="${filter}" />
    </form>
  `;
}

function formatGuests(counts) {
  const adults = `${counts.adults} Adult${counts.adults === 1 ? "" : "s"}`;
  const children = counts.children ? ` · ${counts.children} Child${counts.children === 1 ? "" : "ren"}` : "";
  const rooms = `${counts.rooms} Room${counts.rooms === 1 ? "" : "s"}`;
  return `${adults}${children} · ${rooms}`;
}

function bindOccupancy(form) {
  const root = form.querySelector(".occupancy");
  if (!root) return;
  const menu = root.querySelector(".occupancy-menu");
  const trigger = root.querySelector(".occupancy-trigger");
  const hidden = root.querySelector("input[name=guests]");
  const label = root.querySelector(".occupancy-label");
  const counts = { adults: 2, children: 0, rooms: 1 };
  const sync = () => {
    root.querySelector('[data-count="adults"]').textContent = String(counts.adults);
    root.querySelector('[data-count="children"]').textContent = String(counts.children);
    root.querySelector('[data-count="rooms"]').textContent = String(counts.rooms);
    const text = formatGuests(counts);
    hidden.value = text;
    label.textContent = text;
  };
  trigger.addEventListener("click", () => {
    menu.hidden = !menu.hidden;
    trigger.setAttribute("aria-expanded", String(!menu.hidden));
  });
  root.querySelectorAll("[data-step]").forEach((button) => {
    button.addEventListener("click", () => {
      const key = button.dataset.step;
      const min = key === "adults" || key === "rooms" ? 1 : 0;
      counts[key] = Math.max(min, counts[key] + Number(button.dataset.dir));
      sync();
    });
  });
  root.querySelector(".occupancy-apply").addEventListener("click", () => {
    menu.hidden = true;
    trigger.setAttribute("aria-expanded", "false");
  });
}

function bindQuickFilters(form) {
  const hidden = form.querySelector("input[name=filter]");
  form.querySelectorAll("[data-filter]").forEach((chip) => {
    chip.addEventListener("click", () => {
      const already = chip.classList.contains("active");
      form.querySelectorAll("[data-filter]").forEach((item) => item.classList.remove("active"));
      if (!already) chip.classList.add("active");
      if (hidden) hidden.value = already ? "" : chip.dataset.filter;
    });
  });
}

function bindSearch(form) {
  if (!form || form.dataset.bound === "true") return;
  form.dataset.bound = "true";
  bindOccupancy(form);
  bindQuickFilters(form);
  form.querySelectorAll("[data-stay]").forEach((pill) => {
    pill.addEventListener("click", () => {
      form.querySelectorAll("[data-stay]").forEach((item) => item.classList.remove("active"));
      pill.classList.add("active");
      const hero = form.closest(".promo-hero");
      if (hero) hero.classList.toggle("dayuse", pill.dataset.stay === "dayuse");
      if (pill.dataset.stay === "dayuse" && form.check_out && form.check_in) {
        form.check_out.value = form.check_in.value;
      }
    });
  });
  form.querySelectorAll("[data-tab]").forEach((tab) => {
    tab.addEventListener("click", () => {
      form.querySelectorAll("[data-tab]").forEach((item) => item.classList.remove("active"));
      tab.classList.add("active");
      const dest = tab.dataset.tab;
      if (dest && dest !== "hotels" && dest !== "homes") {
        window.location.hash = `#/${dest}`;
      }
    });
  });
  const addFlight = form.querySelector(".add-flight");
  if (addFlight) {
    addFlight.addEventListener("click", () => {
      window.location.hash = "#/bundle";
    });
  }
  form.addEventListener("submit", (event) => {
    event.preventDefault();
    const data = new FormData(form);
    const homesOnly = form.querySelector("[name=homes_only]")?.checked ? "1" : "";
    const params = new URLSearchParams({
      q: String(data.get("q") || "").trim(),
      check_in: String(data.get("check_in") || ""),
      check_out: String(data.get("check_out") || ""),
      guests: String(data.get("guests") || "2 Adults · 1 Room"),
    });
    const filter = String(data.get("filter") || form.querySelector(".chip.active")?.dataset.filter || "");
    if (filter) params.set("filter", filter);
    if (homesOnly) params.set("homes_only", "1");
    sessionStorage.setItem("aryanstaysSearch", params.toString());
    window.location.hash = `#/hotels?${params.toString()}`;
  });
}

function syncAuthUi() {
  const signedIn = localStorage.getItem("aryanstaysUser") === "1";
  const signIn = document.getElementById("sign-in-btn");
  const create = document.getElementById("create-account-btn");
  if (signIn) signIn.textContent = signedIn ? "Signed in" : "Sign in";
  if (create) create.hidden = signedIn;
}

function bindHeader() {
  document.querySelectorAll(".nav-dropdown").forEach((dropdown) => {
    const button = dropdown.querySelector(".nav-drop-btn");
    if (!button || button.dataset.bound === "true") return;
    button.dataset.bound = "true";
    button.addEventListener("click", (event) => {
      event.stopPropagation();
      document.querySelectorAll(".nav-dropdown.open").forEach((item) => {
        if (item !== dropdown) item.classList.remove("open");
      });
      dropdown.classList.toggle("open");
      button.setAttribute("aria-expanded", String(dropdown.classList.contains("open")));
    });
  });
  document.querySelectorAll("[data-lang]").forEach((button) => {
    button.addEventListener("click", () => {
      const lang = document.querySelector(".lang-btn");
      if (lang) lang.textContent = button.dataset.lang;
      showToast(`Language set to ${button.textContent}`);
    });
  });
  document.querySelectorAll("[data-currency]").forEach((button) => {
    button.addEventListener("click", () => {
      const currency = document.querySelector(".currency-btn");
      if (currency) currency.textContent = button.dataset.currency;
      showToast(`Prices shown in ${button.textContent}`);
    });
  });
  const signIn = document.getElementById("sign-in-btn");
  const create = document.getElementById("create-account-btn");
  if (signIn && signIn.dataset.bound !== "true") {
    signIn.dataset.bound = "true";
    signIn.addEventListener("click", () => {
      const next = localStorage.getItem("aryanstaysUser") !== "1";
      localStorage.setItem("aryanstaysUser", next ? "1" : "0");
      syncAuthUi();
      showToast(next ? "Signed in. Open My Trips to see Booking Service stays." : "Signed out.");
      if (next) window.location.hash = "#/trips";
    });
  }
  if (create && create.dataset.bound !== "true") {
    create.dataset.bound = "true";
    create.addEventListener("click", () => {
      localStorage.setItem("aryanstaysUser", "1");
      syncAuthUi();
      showToast("Account created for this demo. My Trips is now in the navbar.");
      window.location.hash = "#/trips";
    });
  }
  const fab = document.getElementById("help-fab");
  const panel = document.getElementById("help-panel");
  if (fab && panel && fab.dataset.bound !== "true") {
    fab.dataset.bound = "true";
    fab.addEventListener("click", () => {
      panel.hidden = !panel.hidden;
      fab.setAttribute("aria-expanded", String(!panel.hidden));
    });
  }
  syncAuthUi();
}

document.addEventListener("click", (event) => {
  document.querySelectorAll(".nav-dropdown.open").forEach((item) => item.classList.remove("open"));
  const fav = event.target.closest("[data-fav]");
  if (fav) {
    event.preventDefault();
    const on = toggleFavorite(Number(fav.dataset.fav));
    fav.classList.toggle("is-fav", on);
    fav.textContent = on ? "♥" : "♡";
  }
});

function lowestPrice(hotelId, rooms) {
  const prices = rooms.filter((room) => room.hotel_id === hotelId).map((room) => room.price_per_night);
  return prices.length ? Math.min(...prices) : null;
}

function hotelPin(hotel) {
  const base = CITY_MAP[hotel.city] || { x: 50, y: 50 };
  const jitterX = ((hotel.id * 17) % 11) - 5;
  const jitterY = ((hotel.id * 13) % 11) - 5;
  return { x: Math.min(92, Math.max(8, base.x + jitterX)), y: Math.min(92, Math.max(8, base.y + jitterY)) };
}

function filterHotels(hotels, filter) {
  if (!filter) return hotels;
  return hotels.filter((hotel) => {
    const a = hotelAmenities(hotel);
    if (filter === "popular") return hotel.rating >= 4.6;
    if (filter === "free_cancel") return a.freeCancel;
    if (filter === "breakfast") return a.breakfast;
    if (filter === "4star") return hotel.rating >= 4;
    if (filter === "pool") return a.pool;
    if (filter === "parking") return a.parking;
    return true;
  });
}

function hotelCardMarkup(hotel, rooms, options = {}) {
  const price = lowestPrice(hotel.id, rooms);
  const dates = searchDates();
  const nights = nightsBetween(dates.checkIn, dates.checkOut);
  const total = price ? price * nights : null;
  const fav = favoriteIds().has(hotel.id);
  const compact = options.compact;
  const ticks = amenityLines(hotel)
    .slice(0, compact ? 0 : 3)
    .map((line) => `<li>✓ ${line}</li>`)
    .join("");
  return `
    <article class="hotel-row ${compact ? "hotel-card-compact" : ""}" data-hotel-card="${hotel.id}" id="hotel-card-${hotel.id}">
      <div class="hotel-photo ${cityClass(hotel.city)}">
        <span>${hotel.city}</span>
        <button type="button" class="fav-btn ${fav ? "is-fav" : ""}" data-fav="${hotel.id}" aria-label="Save hotel">${fav ? "♥" : "♡"}</button>
      </div>
      <div class="hotel-info">
        <p><span class="rating-pill">⭐ ${hotel.rating.toFixed(1)}</span> ${ratingLabel(hotel.rating)}</p>
        <h3>${hotel.name}</h3>
        <p class="muted">📍 ${hotel.city}</p>
        ${ticks ? `<ul class="amenity-ticks">${ticks}</ul>` : ""}
      </div>
      <div class="hotel-price">
        <strong>${price ? money(price) : "—"}</strong>
        <span class="muted">/ night</span>
        ${total ? `<span class="muted">${money(total)} total</span>` : ""}
        <a class="btn" href="#/hotels/${hotel.id}">View rooms →</a>
      </div>
    </article>
  `;
}

function renderDestinations(hotels) {
  const counts = hotels.reduce((acc, hotel) => {
    acc[hotel.city] = (acc[hotel.city] || 0) + 1;
    return acc;
  }, {});
  const chips = document.getElementById("dest-chips");
  if (chips) {
    chips.innerHTML = TOP_CITIES.map(
      (city) => `<a class="chip dest-chip" href="#/hotels?q=${encodeURIComponent(city.name)}">${city.name}</a>`
    ).join("");
  }
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

function renderHotelList(selector, hotels, rooms, options = {}) {
  const target = document.querySelector(selector);
  if (!target) return;
  if (!hotels.length) {
    target.innerHTML = `<div class="empty">No hotels match that destination. Try Bangalore, Mumbai, Hyderabad, Mysore or Udaipur.</div>`;
    return;
  }
  target.innerHTML = hotels.map((hotel) => hotelCardMarkup(hotel, rooms, options)).join("");
}

function renderRecommended(hotels, rooms) {
  const target = document.getElementById("recommended-stays");
  if (!target) return;
  const preferredCities = ["Hyderabad", "Bangalore", "Goa", "Mumbai"];
  const picks = [];
  preferredCities.forEach((city) => {
    const match = hotels.find((hotel) => hotel.city === city && !picks.includes(hotel));
    if (match) picks.push(match);
  });
  hotels
    .slice()
    .sort((a, b) => b.rating - a.rating)
    .forEach((hotel) => {
      if (picks.length < 4 && !picks.includes(hotel)) picks.push(hotel);
    });
  target.innerHTML = picks
    .map((hotel) => {
      const price = lowestPrice(hotel.id, rooms);
      const fav = favoriteIds().has(hotel.id);
      return `
        <article class="recommend-card">
          <div class="hotel-photo ${cityClass(hotel.city)}">
            <span>⭐ ${hotel.rating.toFixed(1)}</span>
            <button type="button" class="fav-btn ${fav ? "is-fav" : ""}" data-fav="${hotel.id}" aria-label="Save hotel">${fav ? "♥" : "♡"}</button>
          </div>
          <div class="recommend-body">
            <h3>${hotel.name}</h3>
            <p class="muted">📍 ${hotel.city}</p>
            <p><strong>${price ? money(price) : "—"}</strong> <span class="muted">/night</span></p>
            <a class="btn" href="#/hotels/${hotel.id}">View rooms</a>
          </div>
        </article>
      `;
    })
    .join("");
}

function renderMap(hotels) {
  return `
    <aside class="results-map" id="results-map">
      <h3>MAP</h3>
      <p class="muted">Click a marker to highlight the corresponding hotel.</p>
      <div class="india-map" role="img" aria-label="Hotel map">
        ${hotels
          .slice(0, 40)
          .map((hotel) => {
            const pin = hotelPin(hotel);
            return `<button type="button" class="map-pin" style="left:${pin.x}%;top:${pin.y}%" data-pin="${hotel.id}" title="${hotel.name}">📍</button>`;
          })
          .join("")}
      </div>
    </aside>
  `;
}

function bindMap(root, hotels) {
  root.querySelectorAll("[data-pin]").forEach((pin) => {
    pin.addEventListener("click", () => {
      const id = pin.dataset.pin;
      root.querySelectorAll("[data-pin]").forEach((item) => item.classList.remove("is-active"));
      root.querySelectorAll("[data-hotel-card]").forEach((item) => item.classList.remove("is-active"));
      pin.classList.add("is-active");
      const card = root.querySelector(`[data-hotel-card="${id}"]`);
      if (card) {
        card.classList.add("is-active");
        card.scrollIntoView({ behavior: "smooth", block: "center" });
      }
      const hotel = hotels.find((item) => String(item.id) === String(id));
      if (hotel) showToast(`${hotel.name} · ${hotel.city}`);
    });
  });
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
    renderRecommended(hotels, rooms);
    renderHotelList("#popular-hotels", hotels.slice(0, 6), rooms);
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
  const filter = query.get("filter") || "";
  app.innerHTML = `
    <section class="promo-hero">
      <div class="promo-copy">
        <p class="promo-kicker">Limited-time deal</p>
        <h1>MEGA SALE</h1>
        <p class="promo-off">Up to 60% Off!</p>
      </div>
      ${searchPanel({ q, check_in: checkIn, check_out: checkOut, guests: query.get("guests"), filter, homes_only: query.get("homes_only") })}
    </section>
    <div class="results-layout">
      <section>
        <h2>${q ? `Hotels in ${q}` : "All hotels"}</h2>
        <p class="muted" id="results-meta">Searching Aryanstays…</p>
        <div class="results-split">
          <div class="hotel-list" id="hotel-results"></div>
          ${renderMap([])}
        </div>
      </section>
    </div>
  `;
  bindSearch(document.getElementById("search-form"));
  try {
    const path = q ? `/api/v1/hotels?q=${encodeURIComponent(q)}` : "/api/v1/hotels";
    const [hotels, rooms] = await Promise.all([api(path), api("/api/v1/rooms")]);
    const homesOnly = query.get("homes_only") === "1";
    let visible = homesOnly
      ? hotels.filter((hotel) => /home|apt|apartment|suites|stay|residency/i.test(`${hotel.name} ${hotel.city}`))
      : hotels;
    visible = filterHotels(visible, filter);
    document.getElementById("results-meta").textContent =
      `${visible.length} properties found · ${formatLongDate(checkIn)} – ${formatLongDate(checkOut)}${homesOnly ? " · entire homes filter on" : ""}${filter ? ` · ${filter}` : ""}`;
    const split = app.querySelector(".results-split");
    split.innerHTML = `<div class="hotel-list" id="hotel-results"></div>${renderMap(visible)}`;
    renderHotelList("#hotel-results", visible, rooms);
    bindMap(app, visible);
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
    const amenities = amenityLines(hotel);
    const fav = favoriteIds().has(hotel.id);
    const backQuery = sessionStorage.getItem("aryanstaysSearch") || "";
    app.innerHTML = `
      <section class="page-width hotel-details">
        <a class="text-link" href="#/hotels?${backQuery}">← Back to search</a>
        <div class="details-head">
          <div>
            <h1>${hotel.name}</h1>
            <p><span class="rating-pill">⭐ ${hotel.rating.toFixed(1)}</span> ${ratingLabel(hotel.rating)}</p>
            <p class="muted">📍 ${hotel.city}</p>
          </div>
          <button type="button" class="fav-btn large ${fav ? "is-fav" : ""}" data-fav="${hotel.id}" aria-label="Save hotel">${fav ? "♥" : "♡"}</button>
        </div>
        <div class="hero-photo hotel-photo ${cityClass(hotel.city)}">${hotel.name}</div>
        <div class="details-grid">
          <article class="card"><div class="card-body">
            <h2>About this hotel</h2>
            <p>${hotel.name} in ${hotel.city} is sourced from Hotel Service. Room types and live availability come from Room Service.</p>
          </div></article>
          <article class="card"><div class="card-body">
            <h2>Amenities</h2>
            <ul class="amenity-grid">${amenities.map((item) => `<li>✓ ${item}</li>`).join("")}</ul>
          </div></article>
        </div>
        <h2>Available rooms</h2>
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
                  <strong>${room.room_type}</strong>
                  <span class="badge ${room.available ? "" : "busy"}">${room.available ? "Available" : "Reserved"}</span>
                </p>
                <p class="muted">${room.capacity || 2} Guests · Room ${room.room_number}</p>
                <p><strong>${money(room.price_per_night)}</strong> <span class="muted">/night</span></p>
                ${
                  room.available
                    ? `<a class="btn" href="#/book/${room.id}/${hotel.id}">Select room</a>`
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

function guestDraft() {
  try {
    return JSON.parse(sessionStorage.getItem("aryanstaysGuest") || "{}");
  } catch {
    return {};
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
    const saved = searchDates();
    const draft = guestDraft();
    app.innerHTML = `
      <section class="page-width checkout-flow">
        <ol class="steps">
          <li class="done">Select room</li>
          <li class="current">Guest details</li>
          <li>Review booking</li>
          <li>Payment</li>
          <li>Confirmation</li>
        </ol>
        <h2>Guest details</h2>
        <p class="muted">${hotel.name} · ${hotel.city} · ${room.room_type} · ${money(room.price_per_night)} / night</p>
        <form class="form" id="booking-form">
          <label>Full name <input name="customer_name" required placeholder="Aryan Kumar" value="${draft.customer_name || ""}" /></label>
          <label>Email <input name="customer_email" type="email" required placeholder="aryan@example.com" value="${draft.customer_email || ""}" /></label>
          <label>Check-in <input name="check_in" type="date" required min="${isoDate(0)}" value="${draft.check_in || saved.checkIn}" /></label>
          <label>Check-out <input name="check_out" type="date" required min="${isoDate(0)}" value="${draft.check_out || saved.checkOut}" /></label>
          <button class="btn" type="submit">Continue to review</button>
        </form>
      </section>
    `;
    document.getElementById("booking-form").addEventListener("submit", (event) => {
      event.preventDefault();
      const payload = Object.fromEntries(new FormData(event.target).entries());
      sessionStorage.setItem("aryanstaysGuest", JSON.stringify(payload));
      window.location.hash = `#/review/${room.id}/${hotel.id}`;
    });
  } catch (error) {
    app.innerHTML = `<section class="page-width"><div class="error">${error.message}</div></section>`;
  }
}

async function renderReview(roomId, hotelId) {
  showHome(false);
  app.innerHTML = `<section class="page-width"><p class="muted">Loading review…</p></section>`;
  try {
    const [room, hotel] = await Promise.all([
      api(`/api/v1/rooms/${roomId}`),
      api(`/api/v1/hotels/${hotelId || room.hotel_id}`),
    ]);
    const draft = guestDraft();
    const checkIn = draft.check_in || searchDates().checkIn;
    const checkOut = draft.check_out || searchDates().checkOut;
    const nights = nightsBetween(checkIn, checkOut);
    const amount = nights * room.price_per_night;
    app.innerHTML = `
      <section class="page-width checkout-flow">
        <ol class="steps">
          <li class="done">Select room</li>
          <li class="done">Guest details</li>
          <li class="current">Review booking</li>
          <li>Payment</li>
          <li>Confirmation</li>
        </ol>
        <h2>Review booking</h2>
        <article class="card"><div class="card-body">
          <h3>${hotel.name}</h3>
          <p>${room.room_type} · ${hotel.city}</p>
          <p>${formatShortDate(checkIn)} → ${formatShortDate(checkOut)} · ${nights} night${nights === 1 ? "" : "s"}</p>
          <p>${draft.customer_name || ""} · ${draft.customer_email || ""}</p>
          <p class="muted">${searchDates().guests}</p>
          <p><strong>${money(amount)}</strong></p>
          <button class="btn" id="confirm-review">Continue to payment</button>
        </div></article>
      </section>
    `;
    document.getElementById("confirm-review").addEventListener("click", async (event) => {
      const button = event.target;
      button.disabled = true;
      try {
        const booking = await api("/api/v1/bookings", {
          method: "POST",
          body: JSON.stringify({
            customer_name: draft.customer_name,
            customer_email: draft.customer_email,
            check_in: checkIn,
            check_out: checkOut,
            hotel_id: hotel.id,
            room_id: room.id,
            amount,
          }),
        });
        showToast("Room reserved. A confirmation email was sent — open http://localhost:8025 to read it.");
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
      window.location.hash = `#/confirmed/${booking.booking_id}`;
      return;
    }
    app.innerHTML = `
      <section class="page-width checkout-flow">
        <ol class="steps">
          <li class="done">Select room</li>
          <li class="done">Guest details</li>
          <li class="done">Review booking</li>
          <li class="current">Payment</li>
          <li>Confirmation</li>
        </ol>
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
        showToast("Payment successful. Confirmation email sent — check http://localhost:8025");
        window.location.hash = `#/confirmed/${booking.booking_id}`;
      } catch (error) {
        showToast(error.message);
        button.disabled = false;
      }
    });
  } catch (error) {
    app.innerHTML = `<section class="page-width"><div class="error">${error.message}</div></section>`;
  }
}

function downloadConfirmation(booking, hotel, room) {
  const html = `<!DOCTYPE html><html><head><title>Booking ${booking.booking_id}</title></head><body>
    <h1>Booking Confirmed</h1>
    <p>Booking #HTL-${booking.booking_id}</p>
    <p>${hotel ? hotel.name : "Hotel " + booking.hotel_id}</p>
    <p>${room ? room.room_type : "Room " + booking.room_id}</p>
    <p>${booking.check_in} → ${booking.check_out}</p>
    <p>${money(booking.amount)}</p>
  </body></html>`;
  const blob = new Blob([html], { type: "text/html" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = `aryanstays-HTL-${booking.booking_id}.html`;
  link.click();
  URL.revokeObjectURL(url);
}

async function renderConfirmed(bookingId) {
  showHome(false);
  app.innerHTML = `<section class="page-width"><p class="muted">Loading confirmation…</p></section>`;
  try {
    const booking = await api(`/api/v1/bookings/${bookingId}`);
    let hotel = null;
    let room = null;
    try {
      hotel = await api(`/api/v1/hotels/${booking.hotel_id}`);
      room = await api(`/api/v1/rooms/${booking.room_id}`);
    } catch {
      hotel = null;
      room = null;
    }
    app.innerHTML = `
      <section class="page-width confirm-screen">
        <ol class="steps">
          <li class="done">Select room</li>
          <li class="done">Guest details</li>
          <li class="done">Review booking</li>
          <li class="done">Payment</li>
          <li class="current">Confirmation</li>
        </ol>
        <div class="confirm-card">
          <div class="confirm-check">✓</div>
          <h1>Booking Confirmed!</h1>
          <p class="booking-ref">Booking #HTL-${booking.booking_id}</p>
          <h2>${hotel ? hotel.name : `Hotel ${booking.hotel_id}`}</h2>
          <p>${room ? room.room_type : `Room ${booking.room_id}`}</p>
          <p>${formatShortDate(booking.check_in)} → ${formatShortDate(booking.check_out)}</p>
          <p>${searchDates().guests}</p>
          <p class="confirm-amount">${money(booking.amount)}</p>
          <p class="muted">Notification Service emailed this booking. Open Mailpit at http://localhost:8025.</p>
          <a class="btn" href="#/trips">View booking</a>
          <button type="button" class="btn ghost-btn" id="download-confirm">Download confirmation</button>
        </div>
      </section>
    `;
    document.getElementById("download-confirm").addEventListener("click", () => downloadConfirmation(booking, hotel, room));
  } catch (error) {
    app.innerHTML = `<section class="page-width"><div class="error">${error.message}</div></section>`;
  }
}

function tripBucket(booking) {
  const today = isoDate(0);
  if (booking.status === "CANCELLED" || booking.check_out < today) return "past";
  return "upcoming";
}

async function renderBookings() {
  showHome(false);
  app.innerHTML = `<section class="page-width"><h2>My Trips</h2><p class="muted">Loading…</p></section>`;
  try {
    const [bookings, hotels, rooms] = await Promise.all([
      api("/api/v1/bookings"),
      api("/api/v1/hotels"),
      api("/api/v1/rooms"),
    ]);
    const hotelMap = Object.fromEntries(hotels.map((hotel) => [hotel.id, hotel]));
    const roomMap = Object.fromEntries(rooms.map((room) => [room.id, room]));
    const upcoming = bookings.filter((booking) => tripBucket(booking) === "upcoming");
    const past = bookings.filter((booking) => tripBucket(booking) === "past");
    const card = (booking) => {
      const hotel = hotelMap[booking.hotel_id];
      const room = roomMap[booking.room_id];
      return `
        <article class="card trip-card"><div class="card-body">
          <p class="row"><strong>${hotel ? hotel.name : `Hotel ${booking.hotel_id}`}</strong>
          <span class="badge ${booking.status === "CANCELLED" ? "cancelled" : ""}">${booking.status}</span></p>
          <p class="muted">${hotel ? hotel.city : ""}</p>
          <p>${formatShortDate(booking.check_in)} → ${formatShortDate(booking.check_out)}</p>
          <p class="muted">Booking #HTL-${booking.booking_id}${room ? ` · ${room.room_type}` : ""} · ${money(booking.amount)}</p>
          <div class="notice-list" data-notes="${booking.booking_id}"></div>
          <div class="trip-actions">
            <a class="btn" href="#/confirmed/${booking.booking_id}">View details</a>
            ${booking.status === "PENDING_PAYMENT" ? `<a class="btn" href="#/pay/${booking.booking_id}">Pay now</a>` : ""}
            ${booking.status === "CONFIRMED" || booking.status === "PENDING_PAYMENT" ? `<button class="btn danger" data-cancel="${booking.booking_id}">Cancel</button>` : ""}
          </div>
        </div></article>`;
    };
    app.innerHTML = `
      <section class="page-width trips-page">
        <h2>My Trips</h2>
        <p class="muted">Upcoming and past stays from Booking Service.</p>
        <h3>Upcoming</h3>
        <hr />
        ${upcoming.length ? `<div class="hotel-list">${upcoming.map(card).join("")}</div>` : `<div class="empty">No upcoming trips. Search hotels to book your next stay.</div>`}
        <h3>Past trips</h3>
        <hr />
        ${past.length ? `<div class="hotel-list">${past.map(card).join("")}</div>` : `<div class="empty">No past trips yet.</div>`}
      </section>
    `;
    app.querySelectorAll("[data-notes]").forEach(async (target) => {
      try {
        const notes = await api(`/api/v1/notifications?booking_id=${target.dataset.notes}`);
        target.innerHTML = notes.length
          ? notes
              .map(
                (note) =>
                  `<p class="muted">${note.event} · ${note.status} · emailed to ${note.recipient}<br>${note.subject}${note.error ? ` · ${note.error}` : ""}</p>`
              )
              .join("")
          : `<p class="muted">No alerts yet for this booking.</p>`;
      } catch {
        target.innerHTML = "";
      }
    });
    app.querySelectorAll("[data-cancel]").forEach((button) => {
      button.addEventListener("click", async () => {
        button.disabled = true;
        try {
          await api(`/api/v1/bookings/${button.dataset.cancel}`, { method: "DELETE" });
          showToast("Booking cancelled. Cancellation email sent — check http://localhost:8025");
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

function renderFeaturePage(title, body) {
  showHome(false);
  app.innerHTML = `<section class="feature-page"><h2>${title}</h2>${body}</section>`;
}

async function renderNotifications() {
  showHome(false);
  app.innerHTML = `<section class="feature-page"><h2>Booking notifications</h2><p class="muted">Loading alerts from Notification Service…</p></section>`;
  try {
    const notes = await api("/api/v1/notifications");
    app.innerHTML = `
      <section class="feature-page">
        <h2>Booking notifications</h2>
        <p>Notification Service now sends real SMTP email for each booking change.</p>
        <p class="muted">Open the local inbox at <a href="http://localhost:8025" target="_blank" rel="noreferrer">http://localhost:8025</a> (Mailpit). Gmail/Outlook only receive mail if you set SMTP_HOST, SMTP_USER and SMTP_PASSWORD in docker-compose.</p>
        ${
          notes.length
            ? `<div class="notice-list">${notes
                .map(
                  (note) => `
              <article class="notice-card">
                <strong>${note.event}</strong>
                <span class="badge ${note.status === "FAILED" ? "cancelled" : ""}">${note.status}</span>
                <p>${note.subject}</p>
                <p class="muted">${note.channel} · ${note.recipient} · booking #${note.booking_id}</p>
                <p>${note.message}</p>
                ${note.error ? `<p class="error">${note.error}</p>` : ""}
              </article>`
                )
                .join("")}</div>`
            : `<div class="empty">No notifications yet. Create a booking to send the first email.</div>`
        }
      </section>
    `;
  } catch (error) {
    app.innerHTML = `<section class="feature-page"><div class="error">${error.message}</div></section>`;
  }
}

function render() {
  const current = parseRoute();
  if (current.name === "hotels") return renderHotels(current.query);
  if (current.name === "hotel") return renderHotel(current.id);
  if (current.name === "book") return renderBook(current.roomId, current.hotelId);
  if (current.name === "review") return renderReview(current.roomId, current.hotelId);
  if (current.name === "pay") return renderPay(current.bookingId);
  if (current.name === "confirmed") return renderConfirmed(current.bookingId);
  if (current.name === "bookings") return renderBookings();
  if (current.name === "notifications") return renderNotifications();
  if (current.name === "flights") {
    return renderFeaturePage(
      "Flights",
      "<p>Search one-way or return flights, then add a hotel with Flight + Hotel to bundle and save.</p><p class='muted'>This demo keeps live inventory in Hotel and Room services. Use SEARCH HOTELS on the homepage for stays.</p>"
    );
  }
  if (current.name === "homes") {
    return renderFeaturePage(
      "Homes &amp; apartments",
      "<p>Entire homes and apartments are included in the same Hotel Service catalog. Tick <strong>Show me only entire homes and apartments</strong> on search, then SEARCH HOTELS.</p>"
    );
  }
  if (current.name === "activities") {
    return renderFeaturePage(
      "Activities",
      "<p>City walks, fort tickets and sunset cruises can be added after you book a stay. Start with a hotel search to lock dates first.</p>"
    );
  }
  if (current.name === "transfers") {
    return renderFeaturePage(
      "Airport transfer",
      "<p>Private cars and shared shuttles from the airport to your hotel. Book a stay first so the driver has your hotel address.</p>"
    );
  }
  if (current.name === "transport") {
    const mode = current.query.get("mode") || "all";
    return renderFeaturePage(
      "Transport",
      `<p>Browse ${mode} options: flights, buses, trains, ferries, airport transfers and car rentals.</p><p class='muted'>Hotel stays remain the live booking path in this demo.</p>`
    );
  }
  if (current.name === "coupons") {
    return renderFeaturePage(
      "Coupons &amp; Deals",
      `<div class="coupon-grid">
        <article class="coupon-card"><strong>MEGA60</strong><p>Up to 60% off selected city hotels this week.</p></article>
        <article class="coupon-card"><strong>BUNDLE12</strong><p>Extra 12% off when you add a flight to your hotel.</p></article>
        <article class="coupon-card"><strong>DAYUSE</strong><p>Day Use stays from 9:00 to 17:00 in business districts.</p></article>
      </div>`
    );
  }
  if (current.name === "esim") {
    return renderFeaturePage(
      "eSIM",
      "<p>Buy a local data eSIM before you fly. Pair it with a hotel booking so you have maps ready at landing.</p>"
    );
  }
  if (current.name === "guides") {
    return renderFeaturePage(
      "Travel Guides",
      "<p>Neighborhood tips for Bangalore, Mumbai, Goa, Jaipur, Mysore and Udaipur. Open a city from Popular destinations to see live hotels.</p>"
    );
  }
  if (current.name === "bundle") {
    return renderFeaturePage(
      "Flight + Hotel",
      "<p>Bundle and save: add a flight to your hotel search. Dates stay in sync with the occupancy picker on the homepage.</p><p><a class='btn' href='#/'>SEARCH HOTELS</a></p>"
    );
  }
  return renderHome();
}

bindHeader();
window.addEventListener("hashchange", render);
render();
