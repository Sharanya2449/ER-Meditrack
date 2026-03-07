// GPS page elements
const btnLocate = document.getElementById("btnLocate");
const statusEl = document.getElementById("status");
const resultsEl = document.getElementById("results");

let lastPayload = null;

// Admin page elements (you can keep, but don't use for demo)
const btnUpdate = document.getElementById("btnUpdate");
const adminStatus = document.getElementById("adminStatus");

function renderResults(payload) {
  const results = payload.results || [];
  if (!resultsEl) return;

  if (results.length === 0) {
    resultsEl.innerHTML = `<div class="alert alert-warning mt-3">
      No hospitals found within <b>25 km</b>.
    </div>`;
    return;
  }

  const userLat = payload.user.lat;
  const userLng = payload.user.lng;

  resultsEl.innerHTML = results.map((h, idx) => {
    const gmaps = `https://www.google.com/maps/dir/?api=1&origin=${userLat},${userLng}&destination=${h.latitude},${h.longitude}&travelmode=driving`;

    let vacancyLine = "";
    if (h.available_beds === null || h.available_beds === undefined) {
      vacancyLine = `<div class="small">Vacancy: <b>Not reported yet</b></div>`;
    } else if (Number(h.available_beds) <= 0) {
      vacancyLine = `<div class="small">Vacancy: <b>Full</b></div>`;
    } else {
      vacancyLine = `<div class="small">Vacancy: <b>${h.available_beds}</b> beds available</div>`;
    }

    const waitLine = (h.avg_wait_minutes === null || h.avg_wait_minutes === undefined)
      ? `<div class="small">Avg wait: <b>Not reported</b></div>`
      : `<div class="small">Avg wait: <b>${h.avg_wait_minutes}</b> min</div>`;

    const updatedLine = h.last_updated
      ? `<div class="small text-muted">Last updated: ${h.last_updated}</div>`
      : `<div class="small text-muted">Last updated: —</div>`;

    const websiteBtn = h.website_url
      ? `<a class="btn btn-outline-secondary w-100 mt-2" href="${h.website_url}" target="_blank" rel="noreferrer">
           View Hospital Website
         </a>`
      : "";

    return `
      <div class="card shadow-sm mb-3 ${idx === 0 ? "border-danger" : ""}">
        <div class="card-body">
          <h5 class="mb-1">${idx + 1}. ${h.name}</h5>
          <div class="small text-muted">${h.address || ""}</div>
          <div class="small">Distance: <b>${h.distance_km} km</b></div>

          ${vacancyLine}
          ${waitLine}
          ${updatedLine}

          <div class="small">Phone: <a href="tel:${h.phone}">${h.phone || ""}</a></div>

          <a class="btn btn-outline-danger w-100 mt-3" href="${gmaps}" target="_blank" rel="noreferrer">
            Get Directions
          </a>

          ${websiteBtn}

          <button class="btn btn-danger w-100 mt-2" onclick="leaveNow(${h.hospital_id})">
            Leave-now guidance
          </button>
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
  lastPayload = payload;

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

// Admin update (optional/legacy)
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
  adminStatus.textContent = "Updated ✅";
}

if (btnUpdate) btnUpdate.addEventListener("click", adminUpdate);

// Leave-now guidance
function leaveNow(hospitalId) {
  const h = (lastPayload?.results || []).find(x => x.hospital_id === hospitalId);
  if (!h) return;

  const etaMins = Math.max(5, Math.round((Number(h.distance_km) / 20) * 60)); // 20 km/h avg city
  const arriveTime = new Date(Date.now() + etaMins * 60000);
  const hh = arriveTime.getHours().toString().padStart(2, "0");
  const mm = arriveTime.getMinutes().toString().padStart(2, "0");

  alert(`Leave now ✅ Estimated travel time: ~${etaMins} min. If you leave now, you may arrive by ${hh}:${mm}.`);
}