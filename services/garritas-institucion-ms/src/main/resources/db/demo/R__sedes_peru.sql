-- Direcciones ficticias para demostración; no representan establecimientos reales.
INSERT INTO sedes(nombre,direccion,ciudad,telefono,activo)
SELECT n,d,c,t,true FROM (VALUES
 ('Garritas Miraflores','Av. José Larco 1200, Miraflores','Lima','999100001'),
 ('Garritas Los Olivos','Av. Las Palmeras 1200, Los Olivos','Lima','999100002'),
 ('Garritas Cayma','Av. Ejército 800, Cayma','Arequipa','999100003'),
 ('Garritas Trujillo Centro','Av. España 1200, Trujillo','Trujillo','999100004'),
 ('Garritas Wanchaq','Av. de la Cultura 900, Wanchaq','Cusco','999100005'),
 ('Garritas El Tambo','Av. Mariscal Castilla 1500, El Tambo','Huancayo','999100006')
) AS s(n,d,c,t) WHERE NOT EXISTS(SELECT 1 FROM sedes WHERE lower(nombre)=lower(s.n));
