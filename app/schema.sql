DROP TABLE IF EXISTS google_credentials;

CREATE TABLE google_credentials (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  token TEXT NOT NULL,
  refresh_token TEXT,
  token_uri TEXT NOT NULL,
  client_id TEXT NOT NULL,
  client_secret TEXT NOT NULL,
  scopes TEXT NOT NULL
);
