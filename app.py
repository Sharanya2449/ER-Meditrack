import math
import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

from db import (
    init_db,
    search_trauma_library,
    log_search,
    get_hospital_site,
    update_hospital_status,
    get_hospital_sites_with_status,
)

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-secret")
ADMIN_KEY = os.getenv("ADMIN_KEY", "1234")


def haversine_km(lat1, lng1, lat2, lng2):
    R = 6371.0
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lng2 - lng1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


# ---------- BASIC PAGES ----------
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/er")
def er_page():
    return render_template("index.html")


@app.route("/init-db")
def init_database():
    init_db()
    return "Database initialized ✅"


@app.route("/whoami")
def whoami():
    return "UPDATED APP RUNNING ✅"


# ---------- HOSPITAL WEBSITE PAGES ----------
@app.route("/h/<int:hospital_id>/home")
def hospital_home(hospital_id):
    h = get_hospital_site(hospital_id)
    if not h:
        return "Hospital not found", 404
    return render_template("hospital_home.html", h=h)


@app.route("/h/<int:hospital_id>/emergency")
def hospital_emergency(hospital_id):
    h = get_hospital_site(hospital_id)
    if not h:
        return "Hospital not found", 404
    return render_template("hospital_emergency.html", h=h)


@app.route("/h/<int:hospital_id>/services")
def hospital_services(hospital_id):
    h = get_hospital_site(hospital_id)
    if not h:
        return "Hospital not found", 404
    return render_template("hospital_services.html", h=h)


@app.route("/h/<int:hospital_id>/contact")
def hospital_contact(hospital_id):
    h = get_hospital_site(hospital_id)
    if not h:
        return "Hospital not found", 404
    return render_template("hospital_contact.html", h=h)


@app.route("/h/<int:hospital_id>/staff")
def hospital_staff(hospital_id):
    h = get_hospital_site(hospital_id)
    if not h:
        return "Hospital not found", 404
    return render_template("hospital_staff.html", h=h)


@app.route("/api/h/<int:hospital_id>/staff/update", methods=["POST"])
def hospital_staff_update(hospital_id):
    data = request.get_json(force=True)

    if data.get("admin_key") != ADMIN_KEY:
        return jsonify({"ok": False, "error": "Invalid admin key"}), 401

    total_beds = int(data["total_beds"])
    occupied_beds = int(data["occupied_beds"])
    wait = int(data.get("avg_wait_minutes", 0))

    if occupied_beds > total_beds:
        return jsonify({"ok": False, "error": "Occupied beds cannot exceed total beds"}), 400

    update_hospital_status(hospital_id, total_beds, occupied_beds, wait)
    return jsonify({"ok": True})


# ---------- ER SEARCH API (PATIENT) ----------
@app.route("/api/search", methods=["POST"])
def api_search():
    data = request.get_json(force=True)
    user_lat = float(data["lat"])
    user_lng = float(data["lng"])

    hospitals = get_hospital_sites_with_status()

    for h in hospitals:
        h["distance_km"] = round(
            haversine_km(user_lat, user_lng, float(h["latitude"]), float(h["longitude"])),
            2
        )
        h["website_url"] = f"/h/{h['hospital_id']}/home"

    within_radius = [h for h in hospitals if h["distance_km"] <= 25.0]

    with_vacancy = [
        h for h in within_radius
        if h.get("available_beds") is not None and h["available_beds"] > 0
    ]

    pool = with_vacancy if with_vacancy else within_radius

    ranked = sorted(
        pool,
        key=lambda x: (
            0 if x.get("available_beds") is not None else 1,
            x["distance_km"],
            x.get("avg_wait_minutes", 9999)
        )
    )[:3]

    return jsonify({
        "user": {"lat": user_lat, "lng": user_lng},
        "results": ranked
    })


@app.route("/search")
def search_page():
    q = request.args.get("q", "")
    results = search_trauma_library(q) if q else []
    log_search(query_text=q if q else None)
    return render_template("search.html", q=q, results=results)


@app.route("/hospitals")
def hospitals_directory():
    q = (request.args.get("q") or "").strip().lower()

    hospitals = get_hospital_sites_with_status()

    if q:
        hospitals = [
            h for h in hospitals
            if q in (h.get("name", "").lower() + " " + (h.get("address") or "").lower())
        ]

    for h in hospitals:
     h["home_url"] = f"/h/{h['hospital_id']}/home"
     h["staff_url"] = f"/h/{h['hospital_id']}/staff"

    avail = h.get("available_beds")
    if avail is None:
        h["status_label"] = "Not reported"
        h["status_class"] = "bg-secondary"
    elif int(avail) <= 0:
        h["status_label"] = "Full"
        h["status_class"] = "bg-danger"
    else:
        h["status_label"] = f"{avail} beds"
        h["status_class"] = "bg-success"

    return render_template("hospitals.html", hospitals=hospitals, q=q)


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)