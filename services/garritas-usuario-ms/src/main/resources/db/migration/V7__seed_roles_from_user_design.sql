-- Internal staff classifications; these never grant JWT permissions.
INSERT INTO rol(nombre,descripcion) VALUES
 ('SECRETARIA','Atención y recepción de clientes y citas'),
 ('VENTAS','Gestión de pedidos y ventas'),
 ('COMPRAS','Reposición de productos'),
 ('REPORTES','Consulta de reportes de gestión'),
 ('RRHH','Gestión del personal') ON CONFLICT(nombre) DO NOTHING;
-- Preserve existing profiles in the customer list; ADMIN is synchronized only from a verified JWT.
INSERT INTO usuario_rol(id_usuario,id_rol) SELECT u.id,r.id FROM usuarios u CROSS JOIN rol r WHERE r.nombre='CLIENTE' AND NOT EXISTS(SELECT 1 FROM usuario_rol ur WHERE ur.id_usuario=u.id) ON CONFLICT DO NOTHING;
