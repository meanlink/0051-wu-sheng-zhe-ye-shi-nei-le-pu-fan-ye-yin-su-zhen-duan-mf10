CREATE TABLE IF NOT EXISTS turn_events(
 piece text NOT NULL REFERENCES turn_pieces(code), event text NOT NULL,
 sample text NOT NULL CHECK(sample IN('fit','check')),
 lead real NOT NULL CHECK(lead BETWEEN 0 AND 30), hands_busy bool NOT NULL, missed bool NOT NULL,
 PRIMARY KEY(piece,event)
);
