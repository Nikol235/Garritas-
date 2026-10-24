ALTER TABLE pagos ADD COLUMN id_cliente VARCHAR(100);
-- Do not silently delete pre-existing duplicate payments: review them before applying this migration.
ALTER TABLE pagos ADD CONSTRAINT uk_pago_venta UNIQUE(id_venta);
