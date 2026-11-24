CREATE TABLE IF NOT EXISTS turn_models(
 piece text PRIMARY KEY REFERENCES turn_pieces(code),
 method text NOT NULL CHECK(method IN('lead','lead_hands')),
 lead_loss numeric(8,6) NOT NULL, combined_loss numeric(8,6) NOT NULL,
 coef real[] NOT NULL CHECK(cardinality(coef) BETWEEN 2 AND 3),
 learned integer NOT NULL CHECK(learned>0), checked integer NOT NULL CHECK(checked>0)
);
