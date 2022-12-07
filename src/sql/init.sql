BEGIN TRANSACTION;

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- trigger for updated_at
CREATE OR REPLACE FUNCTION trigger_set_timestamp()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- event type
CREATE TYPE event_type AS ENUM('enter', 'leave');

-- netping events table
CREATE TABLE
netping_events
(
  uid             uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  details         json NOT NULL,
  type            event_type NOT NULL,
  is_syncronized  boolean NOT NULL DEFAULT false,
  created_at      timestamptz NOT NULL DEFAULT NOW(),
  updated_at      timestamptz NOT NULL DEFAULT NOW()
);

-- details
-- {
--     "sensor": {"name": string},
--     "io_port": {"name": string, "value": integer},
--     "dt": datetime
-- }

CREATE INDEX ON netping_events((details->'sensor'->>'name'));
CREATE INDEX ON netping_events('type');
CREATE INDEX ON netping_events('is_syncronized');


CREATE TRIGGER set_timestamp
BEFORE UPDATE ON netping_events
FOR EACH ROW
EXECUTE PROCEDURE trigger_set_timestamp();


CREATE TABLE
trassir_servers
(
  uid   uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  name  varchar(250) NOT NULL,
  guid  varchar(250) NOT NULL
);


CREATE TABLE
trassir_channels
(
  uid         uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  name        varchar(250) NOT NULL,
  guid        varchar(250) NOT NULL
);


CREATE TABLE
trassir_events
(
  server_uid    uuid NOT NULL,
  channel_uid   uuid NOT NULL,
  type          event_type NOT NULL,
  details       json NOT NULL,
  is_syncronized  boolean NOT NULL DEFAULT false,
  created_at      timestamptz NOT NULL DEFAULT NOW(),
  updated_at      timestamptz NOT NULL DEFAULT NOW(),
  CONSTRAINT event_server_fk
    FOREIGN KEY server_uid
    REFERENCES trassir_servers(uid),
  CONSTRAINT event_channel_fk
    FOREIGN KEY channel_uid
    REFERENCES trassir_channels(uid)
);

-- details
-- {
--   "plate_number": "A111AA77",
--   "dt": ISO 8601,
--   "screenshot": jpg bytes
-- }

CREATE INDEX ON trassir_events('type');
CREATE INDEX ON trassir_events('is_syncronized');


CREATE TRIGGER set_timestamp
BEFORE UPDATE ON trassir_events
FOR EACH ROW
EXECUTE PROCEDURE trigger_set_timestamp();


COMMIT;