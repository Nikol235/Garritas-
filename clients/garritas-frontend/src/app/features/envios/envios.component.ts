import { Component, inject, signal, input, OnInit } from "@angular/core";
import { FormsModule } from "@angular/forms";
import { DatePipe } from "@angular/common";
import { forkJoin } from "rxjs";
import { Auth } from "../../core/auth";
import { Venta } from "../../core/api";
import { DomainApi, Feedback, Envio, stateLabel } from "../../core/domain-api";
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
  readonly label = stateLabel;
  model = { idVenta: 0, direccionEntrega: "", transportista: "" };
  ngOnInit() {
    this.model.idVenta = this.initialVenta();
    this.load();
  }
  load() {
    forkJoin({
      e: this.api.get<Envio[]>("/envios"),
      v: this.api.get<Venta[]>("/ventas"),
    }).subscribe({
      next: (r) => {
        this.envios.set(r.e);
        this.ventas.set(r.v);
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
  save() {
    this.send(this.api.post<Envio>("/envios", this.model), () => {
      this.model = { idVenta: 0, direccionEntrega: "", transportista: "" };
      this.load();
    });
  }
  action(e: Envio, action: string) {
    this.send(this.api.post<Envio>("/envios/" + e.id + "/" + action), () =>
      this.load(),
    );
  }
}
