# Garritas Store

Sistema distribuido de tienda y bienestar para mascotas, organizado a partir de la referencia Pagatu.

## Componentes

- **Catálogo:** categorías, productos e inventario.
- **Venta:** carrito confirmado, precios obtenidos del servidor y Saga de compra.
- **Pago:** procesamiento simulado e idempotente por pedido.
- **Institución:** sedes del Perú seleccionables por clientes y gestionadas por administradores.
- **Usuario:** perfiles y mascotas vinculados al `sub` de Keycloak.
- **Citas:** reserva por mascota, sede y profesional; horarios de 30 minutos sin doble reserva activa.
- **Envío:** despacho y entrega de pedidos pagados, con consulta privada por cliente.
- **Bienestar:** profesionales y especialidades relacionados muchos a muchos.

## Guías

- [Ejecución](ejecucion.md)
- [Arquitectura](arquitectura.md)
- [Validación](validacion.md)
