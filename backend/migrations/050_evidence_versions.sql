-- 证据版本：封存后每次有效更正都产生一批新证据。
ALTER TABLE turn_pieces ADD COLUMN IF NOT EXISTS evidence_version integer NOT NULL DEFAULT 1;
ALTER TABLE turn_pieces ADD COLUMN IF NOT EXISTS last_correction_at timestamptz;

-- 校样原外键指向 turn_models(piece)，与按版本留存的回验结论冲突，先摘除。
ALTER TABLE turn_revisions DROP CONSTRAINT IF EXISTS turn_revisions_piece_fkey;
ALTER TABLE turn_revisions DROP CONSTRAINT IF EXISTS turn_revisions_basis_fkey;

-- 同一分谱的回验结论按证据版本留存，旧版本用于判定复核员看过的结论是否过期。
ALTER TABLE turn_models DROP CONSTRAINT IF EXISTS turn_models_pkey;
ALTER TABLE turn_models DROP CONSTRAINT IF EXISTS turn_models_piece_version_key;
ALTER TABLE turn_models DROP CONSTRAINT IF EXISTS turn_models_piece_key;
ALTER TABLE turn_models ADD COLUMN IF NOT EXISTS evidence_version integer NOT NULL DEFAULT 1;
ALTER TABLE turn_models ADD CONSTRAINT turn_models_pkey PRIMARY KEY (piece, evidence_version);

-- 校样归属分谱本身；其依据版本必须对应一条真实回验结论。
ALTER TABLE turn_revisions ADD CONSTRAINT turn_revisions_piece_fkey
    FOREIGN KEY (piece) REFERENCES turn_pieces(code);
ALTER TABLE turn_revisions ADD COLUMN IF NOT EXISTS basis_version integer NOT NULL DEFAULT 1;
ALTER TABLE turn_revisions ADD CONSTRAINT turn_revisions_basis_fkey
    FOREIGN KEY (piece, basis_version) REFERENCES turn_models(piece, evidence_version);

-- 已发演出用谱快照签核时的依据，后续更正不改变历史签核。
ALTER TABLE turn_release ADD COLUMN IF NOT EXISTS basis_version integer NOT NULL DEFAULT 1;
ALTER TABLE turn_release ADD COLUMN IF NOT EXISTS signed_risk numeric(8,6);
ALTER TABLE turn_release ADD COLUMN IF NOT EXISTS model_method text;
