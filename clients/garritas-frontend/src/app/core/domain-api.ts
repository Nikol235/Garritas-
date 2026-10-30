import { Injectable, inject, signal } from "@angular/core";
import { HttpClient, HttpErrorResponse } from "@angular/common/http";
import { Observable } from "rxjs";
import { Config } from "./config";

export interface Sede {
  id: number;
  nombre: string;
  direccion: string;
  ciudad: string;
  telefono: string;
  activo: boolean;
}

export interface Especialidad {
  id: number;
  nombre: string;
  descripcion: string;
  activo: boolean;
}

export interface Profesional {
  id: number;
  nombre: string;
  email: string;
  telefono: string;
  sedeId: number | null;
  activo: boolean;
  especialidades: Especialidad[];
}

export interface Rol {
  id: number;
  nombre: string;
  descripcion: string;
}

export interface Perfil {
  id: number;
  nombre: string;
  email: string;
  telefono: string;
  direccion: string;
  dni?: string;
  roles?: Rol[];
  mascotas?: Mascota[];
}

export interface PageResponse<T> {
  content: T[];
  totalElements: number;
  totalPages: number;
  size: number;
  number: number;
  first: boolean;
  last: boolean;
}

export interface Mascota {
  id: number;
  nombre: string;
  especie: string;
  raza: string;
  edad: number | null;
  edadUnidad: "DIAS" | "MESES";
}

export interface Cita {
  total: number;
  duracionMinutos: number;
  detalles: {
    prestacionId: number;
    componentes?: string;
    nombre: string;
    precio: number;
    duracionMinutos: number;
  }[];
  id: number;
  idMascota: number;
  idSede: number;
  profesionalId: number;
  nombreMascota: string;
  nombreSede: string;
  nombreProfesional: string;
  fechaHora: string;
  motivo: string;
  estado: string;
}

export interface Envio {
  zonaId: number | null;
  transportistaId: number | null;
  tarifa: number | null;
  id: number;
  idVenta: number;
  direccionEntrega: string;
  transportista: string;
  estado: string;
  fechaEnvio: string;
  fechaEntregaEstimada: string;
}

export interface PagoDetalle {
  id: number;
  idVenta: number;
  monto: number;
  metodo: string;
  estado: string;
  fechaPago: string;
}

@Injectable({ providedIn: "root" })
export class DomainApi {
  private readonly http = inject(HttpClient);
  private readonly config = inject(Config);

  get<T>(path: string) {
    return this.http.get<T>(this.config.value.apiUrl + path);
  }
  post<T>(path: string, body: unknown = {}, key?: string) {
    return this.http.post<T>(
      this.config.value.apiUrl + path,
      body,
      key ? { headers: { "Idempotency-Key": key } } : {},
    );
  }

  put<T>(path: string, body: unknown) {
    return this.http.put<T>(this.config.value.apiUrl + path, body);
  }

  delete(path: string) {
    return this.http.delete<void>(this.config.value.apiUrl + path);
  }
}

export function errorMessage(e: HttpErrorResponse) {
  return (
    e.error?.detail ??
    e.error?.message ??
    (e.status === 403
      ? "No tienes permiso para esta operación."
      : e.status === 409
        ? "La operación entra en conflicto con otro registro."
        : e.status === 0
          ? "El servidor no responde. Inténtalo de nuevo."
          : "Revisa los datos e inténtalo de nuevo.")
  );
}

export class Feedback {
  readonly error = signal("");
  readonly message = signal("");
  readonly busy = signal(false);

  send<T>(operation: Observable<T>, done: (value: T) => void) {
    if (this.busy()) return;
    this.error.set("");
    this.message.set("");
    this.busy.set(true);
    operation.subscribe({
      next: (value) => {
        this.busy.set(false);
        this.message.set("Cambios guardados correctamente.");
        done(value);
      },
      error: (e) => {
        this.busy.set(false);
        this.error.set(errorMessage(e));
      },
    });
  }

  report(e: HttpErrorResponse) {
    this.message.set("");
    this.error.set(errorMessage(e));
  }
}

export function stateLabel(state: string) {
  return (
    (
      {
        PAGADA: "Pagada",
        CANCELADA: "Cancelada",
        PENDIENTE_STOCK: "Revisando inventario",
        PENDIENTE_PAGO: "Esperando pago",
        COMPENSANDO: "Devolviendo inventario",
        PROGRAMADA: "Programada",
        CONFIRMADA: "Confirmada",
        ATENDIDA: "Atendida",
        PENDIENTE: "Pendiente",
        EN_TRANSITO: "En tránsito",
        ENTREGADO: "Entregado",
        CANCELADO: "Cancelado",
        APROBADO: "Aprobado",
        RECHAZADO: "Rechazado",
      } as Record<string, string>
    )[state] ?? state
  );
}

export interface Prestacion {
  componentes?: { id: number; nombre: string }[];
  id: number;
  nombre: string;
  descripcion: string;
  activo: boolean;
}
export interface Oferta {
  componentes?: { id: number; nombre: string }[];
  id: number;
  sedeId: number;
  prestacionId: number;
  nombre: string;
  precio: number;
  duracionMinutos: number;
  activo: boolean;
}
export interface Transportista {
  id: number;
  nombre: string;
  telefono: string;
  activo: boolean;
}
export interface Zona {
  id: number;
  nombre: string;
  ciudad: string;
  activo: boolean;
}
export interface Cobertura {
  id: number;
  transportistaId: number;
  zonaId: number;
  transportista: string;
  zona: string;
  tarifa: number;
  diasEstimados: number;
  activo: boolean;
}
export interface Plan {
  id: number;
  nombre: string;
  descripcion: string;
  precio: number;
  duracionDias: number;
  activo: boolean;
}
export interface Suscripcion {
  id: number;
  usuarioId: number;
  cliente: string;
  planId: number;
  nombrePlan: string;
  estado: string;
  fechaInicio: string;
  fechaFin: string;
  totalContratado: number;
  periodos: {
    id: number;
    tipo: string;
    fechaInicio: string;
    fechaFin: string;
    precio: number;
  }[];
}
