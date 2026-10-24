-- Nombres y datos ficticios, exclusivamente de demostración.
INSERT INTO especialidades(nombre,descripcion,activo) SELECT n,d,true FROM (VALUES
 ('Medicina general','Consulta preventiva y evaluación general'),('Nutrición','Orientación nutricional para mascotas'),('Dermatología','Cuidado de piel y pelaje'),('Animales exóticos','Atención orientada a aves y pequeños animales')
) AS s(n,d) WHERE NOT EXISTS(SELECT 1 FROM especialidades WHERE nombre=s.n);
INSERT INTO profesionales(nombre,email,telefono,activo) SELECT n,e,t,true FROM (VALUES
 ('Camila Torres','camila.demo@example.test','999200001'),('Diego Rojas','diego.demo@example.test','999200002'),('Valeria Quispe','valeria.demo@example.test','999200003')
) AS s(n,e,t) WHERE NOT EXISTS(SELECT 1 FROM profesionales WHERE email=s.e);
INSERT INTO profesional_especialidad(id_profesional,id_especialidad)
SELECT p.id,e.id FROM (VALUES
 ('camila.demo@example.test','Medicina general'),('camila.demo@example.test','Nutrición'),('diego.demo@example.test','Medicina general'),('diego.demo@example.test','Dermatología'),('valeria.demo@example.test','Animales exóticos'),('valeria.demo@example.test','Nutrición')
) AS s(email,especialidad) JOIN profesionales p ON p.email=s.email JOIN especialidades e ON e.nombre=s.especialidad ON CONFLICT DO NOTHING;
