-- 封存后按原事件编号补更正；同一 request_id 的重试不重复落库、不重复排队。
CREATE TABLE IF NOT EXISTS event_corrections(
 id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 piece text NOT NULL REFERENCES turn_pieces(code),
 event text NOT NULL,
 request_id text NOT NULL,
 sample text NOT NULL CHECK(sample IN('fit','check')),
 lead real NOT NULL CHECK(lead BETWEEN 0 AND 30),
 hands_busy bool NOT NULL,
 missed bool NOT NULL,
 evidence_version integer NOT NULL CHECK(evidence_version > 0),
 received_at timestamptz NOT NULL DEFAULT now(),
 UNIQUE(piece, event, request_id)
);
CREATE INDEX IF NOT EXISTS event_corrections_piece ON event_corrections (piece, id);
