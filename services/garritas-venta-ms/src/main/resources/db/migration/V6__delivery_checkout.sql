ALTER TABLE ventas ADD COLUMN tipo_entrega VARCHAR(8) NOT NULL DEFAULT 'RECOJO' CHECK(tipo_entrega IN ('RECOJO','ENVIO'));
ALTER TABLE ventas ADD COLUMN costo_envio NUMERIC(10,2) NOT NULL DEFAULT 0 CHECK(costo_envio>=0);
ALTER TABLE ventas ADD COLUMN direccion_entrega VARCHAR(255);
ALTER TABLE ventas ADD COLUMN zona_id BIGINT;
ALTER TABLE ventas ADD COLUMN transportista_id BIGINT;
ALTER TABLE ventas ADD COLUMN transportista_nombre VARCHAR(100);
ALTER TABLE ventas ADD COLUMN dias_entrega INTEGER;
ALTER TABLE ventas ADD CONSTRAINT entrega_completa CHECK(tipo_entrega='RECOJO' OR (direccion_entrega IS NOT NULL AND zona_id IS NOT NULL AND transportista_id IS NOT NULL AND dias_entrega>0));
