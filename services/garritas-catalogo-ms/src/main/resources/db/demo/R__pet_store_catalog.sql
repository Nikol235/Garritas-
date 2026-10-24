-- Local demonstration catalog. Never resets stock, prices or products already managed by a user.
-- Only enabled by the DEV Flyway locations and the local integration Compose.
INSERT INTO categorias(nombre, descripcion)
SELECT seed.nombre, seed.descripcion
FROM (VALUES
    ('Alimentos', 'Nutrición para perros, gatos, aves y pequeños animales'),
    ('Higiene', 'Limpieza y cuidado diario de tus mascotas'),
    ('Juguetes', 'Diversión y estimulación para perros y gatos'),
    ('Accesorios', 'Paseo, descanso y comodidad'),
    ('Hábitats', 'Espacios y equipamiento para pequeños animales')
) AS seed(nombre, descripcion)
WHERE NOT EXISTS (SELECT 1 FROM categorias c WHERE lower(c.nombre) = lower(seed.nombre));

INSERT INTO productos(nombre, descripcion, precio, stock, activo, id_categoria, version)
SELECT seed.nombre, seed.descripcion, seed.precio, seed.stock, true,
       (SELECT min(c.id) FROM categorias c WHERE lower(c.nombre) = lower(seed.categoria)), 0
FROM (VALUES
    ('Alimento para perro adulto 3 kg', 'Alimento seco completo para perros adultos. Bolsa de 3 kg.', 59.90, 30, 'Alimentos'),
    ('Alimento para cachorro 1 kg', 'Nutrición para el crecimiento de cachorros. Bolsa de 1 kg.', 29.90, 25, 'Alimentos'),
    ('Alimento para gato adulto 1 kg', 'Alimento seco para gatos adultos. Bolsa de 1 kg.', 34.90, 30, 'Alimentos'),
    ('Bocaditos para perro 100 g', 'Premios para entrenamiento y paseos. Bolsa de 100 g.', 12.50, 40, 'Alimentos'),
    ('Mezcla de semillas para aves 1 kg', 'Mezcla de semillas para aves domésticas. Bolsa de 1 kg.', 18.90, 20, 'Alimentos'),
    ('Heno para conejo 500 g', 'Heno para conejos y pequeños herbívoros. Bolsa de 500 g.', 24.90, 18, 'Alimentos'),
    ('Arena sanitaria para gato 5 kg', 'Arena aglomerante para el arenero de tu gato. Bolsa de 5 kg.', 32.90, 28, 'Higiene'),
    ('Champú para perro 250 ml', 'Champú de uso externo para la limpieza del pelaje. Frasco de 250 ml.', 19.90, 24, 'Higiene'),
    ('Bolsas para paseo, 6 rollos', 'Bolsas para recoger desechos durante el paseo.', 14.90, 35, 'Higiene'),
    ('Pelota resistente para perro', 'Pelota de juego para acompañar la actividad diaria de tu perro.', 15.90, 25, 'Juguetes'),
    ('Caña de juego para gato', 'Juguete interactivo con plumas para gatos. Usar con supervisión.', 18.50, 20, 'Juguetes'),
    ('Correa ajustable de paseo', 'Correa para perro con agarre cómodo. Largo de 1.5 m.', 29.90, 22, 'Accesorios'),
    ('Plato de acero inoxidable', 'Comedero o bebedero lavable para perros y gatos. Capacidad de 500 ml.', 22.90, 30, 'Accesorios'),
    ('Cama lavable mediana', 'Cama acolchada con funda lavable para el descanso de tu mascota.', 89.90, 12, 'Accesorios'),
    ('Rascador para gato', 'Rascador compacto con poste de sisal para gatos.', 69.90, 15, 'Accesorios'),
    ('Bebedero para pequeños animales', 'Bebedero de 250 ml para jaulas de conejos y roedores.', 17.90, 18, 'Hábitats')
) AS seed(nombre, descripcion, precio, stock, categoria)
WHERE NOT EXISTS (SELECT 1 FROM productos p WHERE lower(p.nombre) = lower(seed.nombre));
