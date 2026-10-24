ALTER TABLE ventas ALTER COLUMN id_cliente TYPE VARCHAR(100) USING id_cliente::text;
ALTER TABLE ventas ADD COLUMN metodo_pago VARCHAR(20) NOT NULL DEFAULT 'TARJETA';
ALTER TABLE ventas ADD COLUMN idempotency_key UUID;
CREATE UNIQUE INDEX uk_venta_request ON ventas(id_cliente,idempotency_key);
ALTER TABLE detalle_ventas ADD CONSTRAINT ck_detalle_cantidad CHECK (cantidad>0);
