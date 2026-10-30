-- V5: Seed de roles según requerimiento (Secretaria, Ventas, Compras, Reportes, RRHH)
-- y aseguramiento de asignación de rol ADMIN al usuario administrador.

INSERT INTO rol (nombre, descripcion) VALUES
    ('Secretaria', 'Atención y recepción de clientes y citas'),
    ('Ventas', 'Gestión de cotizaciones, pedidos y ventas de la tienda'),
    ('Compras', 'Adquisición de productos y reposición de stock'),
    ('Reportes', 'Generación y análisis de reportes de gestión'),
    ('RRHH', 'Gestión del personal y recursos humanos')
ON CONFLICT (nombre) DO NOTHING;

-- Asignar rol ADMIN a las cuentas administrativas existentes
INSERT INTO usuario_rol (id_usuario, id_rol)
SELECT u.id, r.id 
FROM usuarios u 
CROSS JOIN rol r
WHERE r.nombre = 'ADMIN' 
  AND (u.id = 3 OR u.email LIKE '%admin%' OR u.nombre ILIKE '%admin%')
ON CONFLICT (id_usuario, id_rol) DO NOTHING;

