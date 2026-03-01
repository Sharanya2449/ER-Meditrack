DROP TABLE IF EXISTS search_logs;
DROP TABLE IF EXISTS patients;
DROP TABLE IF EXISTS trauma_library;
DROP TABLE IF EXISTS er_status;
DROP TABLE IF EXISTS hospitals;

CREATE TABLE hospitals (
  hospital_id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  address TEXT,
  phone TEXT,
  trauma_level INTEGER NOT NULL CHECK (trauma_level IN (1,2,3)),
  latitude REAL NOT NULL,
  longitude REAL NOT NULL,
  is_trauma_er TEXT DEFAULT 'Y' NOT NULL CHECK (is_trauma_er IN ('Y','N')),
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE TABLE er_status (
  hospital_id INTEGER PRIMARY KEY,
  total_beds INTEGER NOT NULL,
  occupied_beds INTEGER NOT NULL,
  avg_wait_minutes INTEGER DEFAULT 0 NOT NULL,
  last_updated DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
  FOREIGN KEY (hospital_id) REFERENCES hospitals(hospital_id) ON DELETE CASCADE
);

CREATE TABLE trauma_library (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT NOT NULL,
  keywords TEXT NOT NULL,
  description TEXT NOT NULL,
  urgency_level TEXT NOT NULL CHECK (urgency_level IN ('High','Medium','Low')),
  recommendation TEXT NOT NULL
);

CREATE TABLE patients (
  patient_id INTEGER PRIMARY KEY AUTOINCREMENT,
  full_name TEXT,
  phone TEXT,
  emergency_notes TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE TABLE search_logs (
  log_id INTEGER PRIMARY KEY AUTOINCREMENT,
  patient_lat REAL,
  patient_lng REAL,
  query_text TEXT,
  searched_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL
);