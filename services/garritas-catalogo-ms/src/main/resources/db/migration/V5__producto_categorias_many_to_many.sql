CREATE TABLE IF NOT EXISTS producto_categoria (
    id_producto BIGINT NOT NULL REFERENCES productos(id) ON DELETE CASCADE,
    id_categoria BIGINT NOT NULL REFERENCES categorias(id) ON DELETE CASCADE,
    PRIMARY KEY (id_producto, id_categoria)
);

CREATE INDEX IF NOT EXISTS idx_producto_categoria_prod ON producto_categoria(id_producto);
CREATE INDEX IF NOT EXISTS idx_producto_categoria_cat ON producto_categoria(id_categoria);

INSERT INTO producto_categoria (id_producto, id_categoria)
SELECT id, id_categoria FROM productos
WHERE id_categoria IS NOT NULL
ON CONFLICT DO NOTHING;

ALTER TABLE productos ALTER COLUMN id_categoria DROP NOT NULL;

