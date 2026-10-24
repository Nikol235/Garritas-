import { Injectable, inject } from "@angular/core";
import { HttpClient } from "@angular/common/http";
import { Config } from "./config";
export interface Categoria {
  id: number;
  nombre: string;
  descripcion: string;
}
export interface Producto {
  id: number;
  nombre: string;
  descripcion: string;
  precio: number;
  stock: number;
  activo: boolean;
  categoria: Categoria;
}
export interface Venta {
  sedeId: number | null;
  id: number;
  idCliente: string;
  fecha: string;
  estado: string;
  total: number;
  detalles: { idProducto: number; cantidad: number; precioUnitario: number }[];
}
export interface Pago {
  id: number;
  idVenta: number;
  estado: string;
  monto: number;
}
@Injectable({ providedIn: "root" })
export class Api {
  private readonly http = inject(HttpClient);
  private readonly config = inject(Config);
  private get url() {
    return this.config.value.apiUrl;
  }
  productos() {
    return this.http.get<Producto[]>(this.url + "/productos");
  }
  categorias() {
    return this.http.get<Categoria[]>(this.url + "/categorias");
  }
  guardarCategoria(
    value: { nombre: string; descripcion: string },
    id?: number,
  ) {
    return id
      ? this.http.put<Categoria>(this.url + "/categorias/" + id, value)
      : this.http.post<Categoria>(this.url + "/categorias", value);
  }
  borrarCategoria(id: number) {
    return this.http.delete(this.url + "/categorias/" + id);
  }
  ventas() {
    return this.http.get<Venta[]>(this.url + "/ventas");
  }
  crearVenta(
    body: {
      sedeId: number;
      metodoPago: string;
      detalles: { idProducto: number; cantidad: number }[];
    },
    key: string,
  ) {
    return this.http.post<Venta>(this.url + "/ventas", body, {
      headers: { "Idempotency-Key": key },
    });
  }
  pago(id: number) {
    return this.http.get<Pago>(this.url + "/pagos/venta/" + id);
  }
}
export function pending(estado: string) {
  return ["PENDIENTE_STOCK", "PENDIENTE_PAGO", "COMPENSANDO"].includes(estado);
}
