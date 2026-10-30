ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS dni VARCHAR(20);
CREATE INDEX IF NOT EXISTS idx_usuarios_dni ON usuarios(dni);

