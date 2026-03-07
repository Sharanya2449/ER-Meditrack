const btn = document.getElementById("btnSave");
const statusEl = document.getElementById("staffStatus");

async function saveUpdate() {
  if (!btn) return;

  const hospitalId = btn.dataset.hospitalId;
  const adminKey = document.getElementById("adminKey").value;
  const totalBeds = document.getElementById("totalBeds").value;
  const occupiedBeds = document.getElementById("occupiedBeds").value;
  const waitMins = document.getElementById("waitMins").value;

  if (statusEl) statusEl.textContent = "Saving...";

  const resp = await fetch(`/api/h/${hospitalId}/staff/update`, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({
      admin_key: adminKey,
      total_beds: totalBeds,
      occupied_beds: occupiedBeds,
      avg_wait_minutes: waitMins
    })
  });

  const data = await resp.json();
  if (!data.ok) {
    if (statusEl) statusEl.textContent = `Error: ${data.error || "Unknown"}`;
    return;
  }

  if (statusEl) statusEl.textContent = "Saved ✅ Now refresh the hospital home page or ER MediTrack.";
}

if (btn) btn.addEventListener("click", saveUpdate);