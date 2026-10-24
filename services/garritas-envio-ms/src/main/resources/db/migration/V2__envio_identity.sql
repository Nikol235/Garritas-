ALTER TABLE envios ADD COLUMN id_cliente VARCHAR(100);
ALTER TABLE envios ADD CONSTRAINT uk_envio_venta UNIQUE(id_venta);
