import os
import sqlite3
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / os.getenv("DATABASE", "meditrack.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    schema_path = BASE_DIR / "schema.sql"
    seed_path = BASE_DIR / "seed.sql"

    with get_connection() as conn:
        conn.executescript(schema_path.read_text(encoding="utf-8"))
        conn.executescript(seed_path.read_text(encoding="utf-8"))
        conn.commit()


def get_hospitals_with_status():
    sql = """
    SELECT
      h.hospital_id, h.name, h.address, h.phone, h.trauma_level,
      h.latitude, h.longitude, h.is_trauma_er,
      s.total_beds, s.occupied_beds,
      (s.total_beds - s.occupied_beds) AS available_beds,
      s.avg_wait_minutes
    FROM hospitals h
    JOIN er_status s ON s.hospital_id = h.hospital_id
    WHERE h.is_trauma_er = 'Y'
    """
    with get_connection() as conn:
        rows = conn.execute(sql).fetchall()
        return [dict(r) for r in rows]


def search_trauma_library(q: str):
    q = (q or "").strip().lower()
    if not q:
        return []

    like = f"%{q}%"
    sql = """
    SELECT id, title, description, urgency_level, recommendation
    FROM trauma_library
    WHERE lower(title) LIKE ?
       OR lower(keywords) LIKE ?
       OR lower(description) LIKE ?
    ORDER BY
      CASE urgency_level WHEN 'High' THEN 1 WHEN 'Medium' THEN 2 WHEN 'Low' THEN 3 ELSE 4 END,
      title ASC
    """
    with get_connection() as conn:
        rows = conn.execute(sql, (like, like, like)).fetchall()
        return [dict(r) for r in rows]


def log_search(lat=None, lng=None, query_text=None):
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO search_logs (patient_lat, patient_lng, query_text) VALUES (?, ?, ?)",
            (lat, lng, query_text),
        )
        conn.commit()


def update_er_status(hospital_id: int, total_beds: int, occupied_beds: int, avg_wait_minutes: int):
    sql = """
    UPDATE er_status
    SET total_beds = ?, occupied_beds = ?, avg_wait_minutes = ?, last_updated = CURRENT_TIMESTAMP
    WHERE hospital_id = ?
    """
    with get_connection() as conn:
        conn.execute(sql, (total_beds, occupied_beds, avg_wait_minutes, hospital_id))
        conn.commit()
def get_hospital_site(hospital_id: int):
    """
    Returns hospital portal info + live status for a given hospital_id from hospital_sites + hospital_status.
    """
    sql ="""
    SELECT
      s.hospital_id,
      s.name,
      s.address,
      s.phone,
      s.email,
      s.latitude,
      s.longitude,
      s.about,
      s.emergency_text,
      s.services,
      st.total_beds,
      st.occupied_beds,
      (st.total_beds - st.occupied_beds) AS available_beds,
      st.avg_wait_minutes,
      st.last_updated
    FROM hospital_sites s
    LEFT JOIN hospital_status st ON st.hospital_id = s.hospital_id
    WHERE s.hospital_id = ?
    """
    with get_connection() as conn:
        row = conn.execute(sql, (hospital_id,)).fetchone()
        return dict(row) if row else None


def update_hospital_status(hospital_id: int, total_beds: int, occupied_beds: int, avg_wait_minutes: int):
    """
    Staff portal updater: inserts/updates status and bumps last_updated.
    """
    sql = """
    INSERT INTO hospital_status (hospital_id, total_beds, occupied_beds, avg_wait_minutes, last_updated)
    VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
    ON CONFLICT(hospital_id) DO UPDATE SET
      total_beds=excluded.total_beds,
      occupied_beds=excluded.occupied_beds,
      avg_wait_minutes=excluded.avg_wait_minutes,
      last_updated=CURRENT_TIMESTAMP
    """
    with get_connection() as conn:
        conn.execute(sql, (hospital_id, total_beds, occupied_beds, avg_wait_minutes))
        conn.commit()

def get_hospital_sites_with_status():
    sql = """
    SELECT
      s.hospital_id,
      s.name,
      s.address,
      s.phone,
      s.latitude,
      s.longitude,
      st.total_beds,
      st.occupied_beds,
      (st.total_beds - st.occupied_beds) AS available_beds,
      st.avg_wait_minutes,
      st.last_updated
    FROM hospital_sites s
    LEFT JOIN hospital_status st ON st.hospital_id = s.hospital_id
    """
    with get_connection() as conn:
        rows = conn.execute(sql).fetchall()
        return [dict(r) for r in rows]