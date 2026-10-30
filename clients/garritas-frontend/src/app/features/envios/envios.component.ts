import { Component, inject, signal, input, OnInit } from "@angular/core";
import { FormsModule } from "@angular/forms";
import { DatePipe } from "@angular/common";
import { forkJoin } from "rxjs";
import { Auth } from "../../core/auth";
import { Venta } from "../../core/api";
import {
  DomainApi,
  Feedback,
  Envio,
  Cobertura,
  stateLabel,
} from "../../core/domain-api";
@Component({
  selector: "app-envios",
  imports: [FormsModule, DatePipe],
  templateUrl: "./envios.component.html",
})
export class EnviosComponent extends Feedback implements OnInit {
  readonly auth = inject(Auth);
  private readonly api = inject(DomainApi);
  readonly initialVenta = input(0);
  readonly envios = signal<Envio[]>([]);
  readonly ventas = signal<Venta[]>([]);
  readonly coberturas = signal<Cobertura[]>([]);
  readonly label = stateLabel;
  model = { idVenta: 0, direccionEntrega: "", zonaId: 0, transportistaId: 0 };
  ngOnInit() {
    this.model.idVenta = this.initialVenta();
    this.load();
  }
  load() {
    forkJoin({
      e: this.api.get<Envio[]>("/envios"),
      v: this.api.get<Venta[]>("/ventas"),
      c: this.api.get<Cobertura[]>("/coberturas"),
    }).subscribe({
      next: (r) => {
        this.envios.set(r.e);
        this.ventas.set(r.v);
        this.coberturas.set(r.c.filter((c) => c.activo));
      },
      error: (e) => this.report(e),
    });
  }
  available() {
    return this.ventas().filter(
      (v) =>
        v.estado === "PAGADA" && !this.envios().some((e) => e.idVenta === v.id),
    );
  }
  zonas() {
    return [
      ...new Map(
        this.coberturas().map((c) => [
          c.zonaId,
          { id: c.zonaId, nombre: c.zona },
        ]),
      ).values(),
    ];
  }
  carriers() {
    return this.coberturas().filter((c) => c.zonaId === this.model.zonaId);
  }
  cobertura() {
    return this.carriers().find(
      (c) => c.transportistaId === this.model.transportistaId,
    );
  }
  save() {
    this.send(this.api.post<Envio>("/envios", this.model), () => {
      this.model = {
        idVenta: 0,
        direccionEntrega: "",
        zonaId: 0,
        transportistaId: 0,
      };
      this.load();
    });
  }
  action(e: Envio, action: string) {
    this.send(this.api.post<Envio>("/envios/" + e.id + "/" + action), () =>
      this.load(),
    );
  }
}
