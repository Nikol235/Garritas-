-- One-time ownership transfer; old rows remain untouched in Envio as an archive.
BEGIN;
SET LOCAL standard_conforming_strings = on;
LOCK TABLE despachos IN SHARE ROW EXCLUSIVE MODE;
INSERT INTO despachos(id,id_venta,id_cliente,direccion_entrega,transportista,estado,fecha_envio,fecha_entrega_estimada)
SELECT id,id_venta,id_cliente,direccion_entrega,transportista,estado,fecha_envio,fecha_entrega_estimada
FROM jsonb_to_recordset('__LEGACY_JSON__'::jsonb)
AS e(id bigint,id_venta bigint,id_cliente varchar,direccion_entrega varchar,transportista varchar,estado varchar,fecha_envio timestamp,fecha_entrega_estimada timestamp)
ON CONFLICT(id_venta) DO NOTHING;
SELECT setval(pg_get_serial_sequence('despachos','id'),COALESCE((SELECT max(id) FROM despachos),1),EXISTS(SELECT 1 FROM despachos));
COMMIT;
