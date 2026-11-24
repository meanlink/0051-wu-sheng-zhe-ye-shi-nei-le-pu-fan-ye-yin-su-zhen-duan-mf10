CREATE TABLE IF NOT EXISTS turn_pieces(
 code text PRIMARY KEY, title text NOT NULL, part text NOT NULL,
 legacy_page integer NOT NULL, legacy_lead real NOT NULL CHECK(legacy_lead BETWEEN 0 AND 30),
 legacy_hands_busy bool NOT NULL,
 stage text NOT NULL DEFAULT 'recording' CHECK(stage IN('recording','frozen','graded','released'))
);
