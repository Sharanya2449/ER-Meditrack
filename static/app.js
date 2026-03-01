// GPS page elements
const btnLocate = document.getElementById("btnLocate");
const statusEl = document.getElementById("status");
const resultsEl = document.getElementById("results");

// Admin page elements
const btnUpdate = document.getElementById("btnUpdate");
const adminStatus = document.getElementById("adminStatus");

function renderResults(payload) {
  const results = payload.results || [];
  if (!resultsEl) return;

  if (results.length === 0) {
    resultsEl.innerHTML = `<div class="alert alert-warning mt-3">
      No Trauma ER with vacancy found within 5 km.
    </div>`;
    return;
  }

  const userLat = payload.user.lat;
  const userLng = payload.user.lng;

  resultsEl.innerHTML = results.map((h, idx) => {
    const gmaps = `https://www.google.com/maps/dir/?api=1&origin=${userLat},${userLng}&destination=${h.latitude},${h.longitude}&travelmode=driving`;
    return `
      <div class="card shadow-sm mb-3 ${idx === 0 ? "border-danger" : ""}">
        <div class="card-body">
          <h5 class="mb-1">${idx + 1}. ${h.name}</h5>
          <div class="small text-muted">${h.address || ""}</div>
          <div class="small">Trauma Level: <b>${h.trauma_level}</b> • Distance: <b>${h.distance_km} km</b></div>
          <div class="small">Vacancy: <b>${h.available_beds}</b> beds • Avg wait: <b>${h.avg_wait_minutes}</b> min</div>
          <div class="small">Phone: <a href="tel:${h.phone}">${h.phone || ""}</a></div>
          <a class="btn btn-outline-danger w-100 mt-3" href="${gmaps}" target="_blank" rel="noreferrer">
            Get Directions
          </a>
        </div>
      </div>
    `;
  }).join("");
}

async function searchHospitals(lat, lng) {
  if (statusEl) statusEl.textContent = "Searching hospitals…";
  if (resultsEl) resultsEl.innerHTML = "";

  const resp = await fetch("/api/search", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ lat, lng })
  });

  const payload = await resp.json();
  if (statusEl) statusEl.textContent = "Done.";
  renderResults(payload);
}

function locate() {
  if (!navigator.geolocation) {
    if (statusEl) statusEl.textContent = "GPS not supported.";
    return;
  }

  if (statusEl) statusEl.textContent = "Requesting GPS permission…";
  navigator.geolocation.getCurrentPosition(
    (pos) => {
      const { latitude, longitude } = pos.coords;
      if (statusEl) statusEl.textContent = `Location: ${latitude.toFixed(5)}, ${longitude.toFixed(5)}`;
      searchHospitals(latitude, longitude);
    },
    () => {
      if (statusEl) statusEl.textContent = "Location denied/unavailable. Turn on GPS and allow location.";
    },
    { enableHighAccuracy: true, timeout: 10000 }
  );
}

// Wire GPS button
if (btnLocate) btnLocate.addEventListener("click", locate);

// Admin update
async function adminUpdate() {
  const adminKey = document.getElementById("adminKey")?.value || "";
  const hospitalId = document.getElementById("hospitalId")?.value;
  const totalBeds = document.getElementById("totalBeds")?.value;
  const occupiedBeds = document.getElementById("occupiedBeds")?.value;
  const waitMins = document.getElementById("waitMins")?.value;

  if (!adminStatus) return;

  adminStatus.textContent = "Updating…";

  const resp = await fetch("/api/admin/update", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      admin_key: adminKey,
      hospital_id: hospitalId,
      total_beds: totalBeds,
      occupied_beds: occupiedBeds,
      avg_wait_minutes: waitMins
    })
  });

  const payload = await resp.json();
  if (!payload.ok) {
    adminStatus.textContent = `Error: ${payload.error || "Unknown"}`;
    return;
  }
  adminStatus.textContent = "Updated ✅ Now refresh GPS page to see ranking changes.";
}

if (btnUpdate) btnUpdate.addEventListener("click", adminUpdate);