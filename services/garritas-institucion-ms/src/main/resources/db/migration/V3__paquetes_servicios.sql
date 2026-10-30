CREATE TABLE prestacion_componentes(id_paquete BIGINT NOT NULL REFERENCES prestaciones(id),id_componente BIGINT NOT NULL REFERENCES prestaciones(id),PRIMARY KEY(id_paquete,id_componente),CHECK(id_paquete<>id_componente));
CREATE INDEX ON prestacion_componentes(id_componente);
