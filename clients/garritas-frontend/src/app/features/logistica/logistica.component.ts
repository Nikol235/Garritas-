import { Component, inject, signal } from "@angular/core";
import { FormsModule } from "@angular/forms";
import { CurrencyPipe } from "@angular/common";
import { forkJoin } from "rxjs";
import {
  DomainApi,
  Feedback,
  Transportista,
  Zona,
  Cobertura,
} from "../../core/domain-api";
@Component({
  selector: "app-logistica",
  imports: [FormsModule, CurrencyPipe],
  templateUrl: "./logistica.component.html",
})
export class LogisticaComponent extends Feedback {
  private readonly api = inject(DomainApi);
  readonly transportistas = signal<Transportista[]>([]);
  readonly zonas = signal<Zona[]>([]);
  readonly coberturas = signal<Cobertura[]>([]);
  tid: number | undefined;
  zid: number | undefined;
  t = { nombre: "", telefono: "", activo: true };
  z = { nombre: "", ciudad: "", activo: true };
  c = {
    transportistaId: 0,
    zonaId: 0,
    tarifa: 10,
    diasEstimados: 1,
    activo: true,
  };
  constructor() {
    super();
    this.load();
  }
  load() {
    forkJoin({
      t: this.api.get<Transportista[]>("/transportistas"),
      z: this.api.get<Zona[]>("/zonas"),
      c: this.api.get<Cobertura[]>("/coberturas"),
    }).subscribe({
      next: (r) => {
        this.transportistas.set(r.t);
        this.zonas.set(r.z);
        this.coberturas.set(r.c);
      },
      error: (e) => this.report(e),
    });
  }
  editT(t: Transportista) {
    this.tid = t.id;
    this.t = { nombre: t.nombre, telefono: t.telefono ?? "", activo: t.activo };
  }
  editZ(z: Zona) {
    this.zid = z.id;
    this.z = { nombre: z.nombre, ciudad: z.ciudad, activo: z.activo };
  }
  editC(c: Cobertura) {
    this.c = {
      transportistaId: c.transportistaId,
      zonaId: c.zonaId,
      tarifa: c.tarifa,
      diasEstimados: c.diasEstimados,
      activo: c.activo,
    };
  }
  saveT() {
    this.send(
      this.tid
        ? this.api.put("/transportistas/" + this.tid, this.t)
        : this.api.post("/transportistas", this.t),
      () => {
        this.resetT();
        this.load();
      },
    );
  }
  saveZ() {
    this.send(
      this.zid
        ? this.api.put("/zonas/" + this.zid, this.z)
        : this.api.post("/zonas", this.z),
      () => {
        this.resetZ();
        this.load();
      },
    );
  }
  saveC() {
    this.send(this.api.put("/coberturas", this.c), () => this.load());
  }
  resetT() {
    this.tid = undefined;
    this.t = { nombre: "", telefono: "", activo: true };
  }
  resetZ() {
    this.zid = undefined;
    this.z = { nombre: "", ciudad: "", activo: true };
  }
  remove(path: string, name: string) {
    if (confirm("¿Desactivar " + name + "?"))
      this.send(this.api.delete(path), () => this.load());
  }
}
