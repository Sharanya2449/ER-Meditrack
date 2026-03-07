INSERT INTO hospitals (name, address, phone, trauma_level, latitude, longitude, is_trauma_er)
VALUES ('City Trauma Center', '101 Main St', '111-222-3333', 1, 19.0760000, 72.8777000, 'Y');

INSERT INTO hospitals (name, address, phone, trauma_level, latitude, longitude, is_trauma_er)
VALUES ('Metro General Hospital', '202 Central Ave', '222-333-4444', 2, 19.0728000, 72.8826000, 'Y');

INSERT INTO hospitals (name, address, phone, trauma_level, latitude, longitude, is_trauma_er)
VALUES ('Community Care Hospital', '303 West Rd', '333-444-5555', 3, 19.0822000, 72.8745000, 'Y');

INSERT INTO er_status (hospital_id, total_beds, occupied_beds, avg_wait_minutes)
SELECT hospital_id, 10, 7, 25 FROM hospitals WHERE name='City Trauma Center';

INSERT INTO er_status (hospital_id, total_beds, occupied_beds, avg_wait_minutes)
SELECT hospital_id, 8, 8, 40 FROM hospitals WHERE name='Metro General Hospital';

INSERT INTO er_status (hospital_id, total_beds, occupied_beds, avg_wait_minutes)
SELECT hospital_id, 6, 2, 15 FROM hospitals WHERE name='Community Care Hospital';

INSERT INTO trauma_library (title, keywords, description, urgency_level, recommendation)
VALUES
('Possible Fracture', 'fracture broken bone swelling severe pain deformity', 'Severe pain, swelling, bruising, deformity, or inability to bear weight.', 'High', 'Immobilize the area, apply cold pack, and seek urgent medical evaluation.'),
('Concussion / Head Injury', 'concussion head injury dizziness nausea confusion headache', 'Headache, dizziness, confusion, nausea, light sensitivity, memory issues.', 'High', 'Rest and seek medical evaluation; urgent if symptoms worsen or repeated vomiting.'),
('Minor Sprain', 'sprain twist mild swelling pain ankle', 'Mild swelling and pain after twist injury with some ability to walk.', 'Medium', 'RICE: Rest, Ice, Compression, Elevation. If persistent/worse, consult clinician.'),
('Deep Cut / Laceration', 'cut laceration bleeding stitches wound deep', 'Deep wound or bleeding that does not stop with pressure.', 'High', 'Apply pressure, keep clean, and visit urgent care/ER if bleeding persists.');
-- Insert 3 demo hospitals only if they don't exist
INSERT OR IGNORE INTO hospital_sites
(hospital_id, name, address, phone, email, latitude, longitude, about, emergency_text, services)
VALUES
(1, 'MediTrack Trauma Center – Chembur', 'Chembur, Mumbai', '+91-90000-00001', 'chembur@meditrack.demo',
 19.0596, 72.9005,
 'A tertiary-care trauma facility with 24×7 emergency services and critical care support.',
 '24×7 Emergency • Ambulance support • Trauma team on call',
 'Trauma • Orthopedics • ICU • Radiology • General Surgery'),

(2, 'MediTrack Emergency Hospital – Byculla', 'Byculla, Mumbai', '+91-90000-00002', 'byculla@meditrack.demo',
 18.9767, 72.8328,
 'Emergency-first hospital designed for rapid triage and stabilization.',
 '24×7 ER • Fast triage • Stabilization and referrals',
 'Emergency Medicine • Neuro • ICU • Diagnostics'),

(3, 'MediTrack MultiCare – Sanpada', 'Sanpada, Navi Mumbai', '+91-90000-00003', 'sanpada@meditrack.demo',
 19.0606, 73.0140,
 'Community hospital providing emergency support and specialty consults.',
 '24×7 Emergency • Priority triage • On-call specialists',
 'Emergency • Pediatrics • Medicine • Diagnostics');

-- Add status rows if missing
INSERT OR IGNORE INTO hospital_status (hospital_id, total_beds, occupied_beds, avg_wait_minutes)
VALUES
(1, 10, 6, 20),
(2, 8, 5, 25),
(3, 12, 9, 15);