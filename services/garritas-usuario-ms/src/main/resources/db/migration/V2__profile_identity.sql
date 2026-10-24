ALTER TABLE usuarios ADD COLUMN subject VARCHAR(100) UNIQUE;
ALTER TABLE mascotas ADD CONSTRAINT ck_mascota_edad CHECK(edad IS NULL OR edad>=0);
