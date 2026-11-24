CREATE TABLE IF NOT EXISTS turn_revisions(
 piece text NOT NULL REFERENCES turn_models(piece), code text NOT NULL,
 target_page int NOT NULL CHECK(target_page BETWEEN 2 AND 200),
 lead real NOT NULL CHECK(lead BETWEEN 0 AND 30),
 hands_busy bool NOT NULL, trial_passes integer NOT NULL CHECK(trial_passes BETWEEN 0 AND 3),
 failure_probability numeric(8,6) NOT NULL CHECK(failure_probability BETWEEN 0 AND 1),
 PRIMARY KEY(piece,code)
);
CREATE TABLE IF NOT EXISTS turn_release(
 piece text PRIMARY KEY REFERENCES turn_pieces(code), revision text NOT NULL,
 programme text NOT NULL, signer text NOT NULL,
 FOREIGN KEY(piece,revision) REFERENCES turn_revisions(piece,code)
);
