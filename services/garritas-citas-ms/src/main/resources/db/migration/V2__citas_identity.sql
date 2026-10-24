ALTER TABLE citas ALTER COLUMN id_cliente TYPE VARCHAR(100) USING id_cliente::text;
ALTER TABLE citas ADD COLUMN id_profesional BIGINT;
ALTER TABLE citas ADD COLUMN nombre_mascota VARCHAR(100);
ALTER TABLE citas ADD COLUMN nombre_sede VARCHAR(100);
ALTER TABLE citas ADD COLUMN nombre_profesional VARCHAR(100);
CREATE UNIQUE INDEX uk_cita_profesional_hora ON citas(id_profesional,fecha_hora) WHERE estado IN ('PROGRAMADA','CONFIRMADA');
