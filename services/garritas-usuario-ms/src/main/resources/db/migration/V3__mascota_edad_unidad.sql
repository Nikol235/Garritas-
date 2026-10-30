ALTER TABLE mascotas ADD COLUMN edad_unidad VARCHAR(5) NOT NULL DEFAULT 'MESES';
UPDATE mascotas SET edad = edad * 12 WHERE edad IS NOT NULL;
ALTER TABLE mascotas ADD CONSTRAINT mascota_edad_unidad CHECK (edad_unidad IN ('DIAS','MESES'));
ALTER TABLE mascotas ADD CONSTRAINT mascota_edad_limite CHECK (edad IS NULL OR edad BETWEEN 0 AND 36500);
