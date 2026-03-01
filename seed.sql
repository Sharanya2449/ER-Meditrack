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