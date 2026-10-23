CREATE TABLE reservas_stock (
 id_venta BIGINT PRIMARY KEY, estado VARCHAR(20) NOT NULL, payload TEXT NOT NULL
);
ALTER TABLE productos ADD CONSTRAINT ck_stock_no_negativo CHECK(stock>=0);
