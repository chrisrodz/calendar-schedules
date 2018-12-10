-- DROP TABLE IF EXISTS google_credentials;
DROP TABLE IF EXISTS appointments;

-- CREATE TABLE google_credentials (
--   id INTEGER PRIMARY KEY AUTOINCREMENT,
--   token TEXT NOT NULL,
--   refresh_token TEXT,
--   token_uri TEXT NOT NULL,
--   client_id TEXT NOT NULL,
--   client_secret TEXT NOT NULL,
--   scopes TEXT NOT NULL
-- );

CREATE TABLE appointments (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  start_ms TEXT NOT NULL,
  end_ms TEXT NOT NULL,
  name TEXT NOT NULL,
  phone_number TEXT NOT NULL,
  insurance TEXT NOT NULL,
  gcal_event_id TEXT NOT NULL,
  is_confirmed BOOLEAN NOT NULL,
  is_canceled BOOLEAN NOT NULL
);
