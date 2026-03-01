import math
import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from db import init_db, get_hospitals_with_status, search_trauma_library, log_search, update_er_status

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-secret")
ADMIN_KEY = os.getenv("ADMIN_KEY", "")


def haversine_km(lat1, lng1, lat2, lng2):
    R = 6371.0
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lng2 - lng1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/search")
def search_page():
    q = request.args.get("q", "")
    results = search_trauma_library(q) if q else []
    log_search(query_text=q if q else None)
    return render_template("search.html", q=q, results=results)


@app.route("/admin")
def admin_page():
    return render_template("admin.html")


@app.route("/init-db")
def init_database():
    init_db()
    return "Database initialized ✅"


@app.route("/api/search", methods=["POST"])
def api_search():
    data = request.get_json(force=True)
    user_lat = float(data["lat"])
    user_lng = float(data["lng"])

    hospitals = get_hospitals_with_status()

    for h in hospitals:
        h["distance_km"] = round(
            haversine_km(user_lat, user_lng, float(h["latitude"]), float(h["longitude"])), 2
        )

    within_25 =[h for h in hospitals if h["distance_km"] <= 25.0]
    with_vacancy = [h for h in within_25 if (h["available_beds"] is not None and h["available_beds"] > 0)]

    ranked = sorted(within_25, key=lambda x: (x["trauma_level"], x["distance_km"], x["avg_wait_minutes"]))[:3]

    log_search(lat=user_lat, lng=user_lng, query_text="GPS_SEARCH")
    return jsonify({"user": {"lat": user_lat, "lng": user_lng}, "results": ranked})


@app.route("/api/admin/update", methods=["POST"])
def api_admin_update():
    data = request.get_json(force=True)
    if data.get("admin_key") != ADMIN_KEY:
        return jsonify({"ok": False, "error": "Invalid admin key"}), 401

    hospital_id = int(data["hospital_id"])
    total_beds = int(data["total_beds"])
    occupied_beds = int(data["occupied_beds"])
    avg_wait_minutes = int(data["avg_wait_minutes"])

    if occupied_beds > total_beds:
        return jsonify({"ok": False, "error": "occupied_beds cannot exceed total_beds"}), 400

    update_er_status(hospital_id, total_beds, occupied_beds, avg_wait_minutes)
    return jsonify({"ok": True})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))