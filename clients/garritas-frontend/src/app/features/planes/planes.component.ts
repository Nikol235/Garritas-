import { Component, inject, signal, output } from "@angular/core";
import { FormsModule } from "@angular/forms";
import { CurrencyPipe, DatePipe } from "@angular/common";
import { Auth } from "../../core/auth";
import { DomainApi, Feedback, Plan, Suscripcion } from "../../core/domain-api";
@Component({
  selector: "app-planes",
  imports: [FormsModule, CurrencyPipe, DatePipe],
  templateUrl: "./planes.component.html",
})
export class PlanesComponent extends Feedback {
  readonly auth = inject(Auth);
  private readonly api = inject(DomainApi);
  readonly cuenta = output<void>();
  readonly planes = signal<Plan[]>([]);
  readonly suscripciones = signal<Suscripcion[]>([]);
  readonly needsProfile = signal(false);
  readonly myProfileId = signal(0);
  private keys = new Map<string, string>();
  id: number | undefined;
  model = {
    nombre: "",
    descripcion: "",
    precio: 29.9,
    duracionDias: 30,
    activo: true,
  };
  constructor() {
    super();
    this.load();
  }
  load() {
    this.api.get<{ id: number }>("/usuarios/me").subscribe({
      next: (p) => {
        this.myProfileId.set(p.id);
        this.needsProfile.set(false);
      },
      error: (e) => {
        if (e.status === 404) this.needsProfile.set(true);
        else this.report(e);
      },
    });
    this.api
      .get<Plan[]>("/planes")
      .subscribe({
        next: (p) => this.planes.set(p),
        error: (e) => this.report(e),
      });
    this.api.get<Suscripcion[]>("/suscripciones").subscribe({
      next: (s) => {
        this.suscripciones.set(s);
      },
      error: (e) => {
        if (e.status === 404) {
          this.needsProfile.set(true);
          this.suscripciones.set([]);
        } else this.report(e);
      },
    });
  }
  edit(p: Plan) {
    this.id = p.id;
    this.model = {
      nombre: p.nombre,
      descripcion: p.descripcion ?? "",
      precio: p.precio,
      duracionDias: p.duracionDias,
      activo: p.activo,
    };
  }
  reset() {
    this.id = undefined;
    this.model = {
      nombre: "",
      descripcion: "",
      precio: 29.9,
      duracionDias: 30,
      activo: true,
    };
  }
  save() {
    this.send(
      this.id
        ? this.api.put("/planes/" + this.id, this.model)
        : this.api.post("/planes", this.model),
      () => {
        this.reset();
        this.load();
      },
    );
  }
  remove(p: Plan) {
    if (confirm("¿Desactivar " + p.nombre + "?"))
      this.send(this.api.delete("/planes/" + p.id), () => this.load());
  }
  active(p: Plan) {
    return this.suscripciones().some(
      (s) =>
        s.planId === p.id &&
        s.usuarioId === this.myProfileId() &&
        s.estado === "ACTIVA",
    );
  }
  operation(path: string, body: unknown, signature: string) {
    if (!this.keys.has(signature))
      this.keys.set(signature, crypto.randomUUID());
    this.send(
      this.api.post<Suscripcion>(path, body, this.keys.get(signature)),
      () => {
        this.keys.delete(signature);
        this.message.set(
          "Operación registrada. Revisa el período y su importe en el historial.",
        );
        this.load();
      },
    );
  }
  contratar(p: Plan) {
    if (
      confirm(
        "¿Contratar " +
          p.nombre +
          " por S/ " +
          p.precio +
          " durante " +
          p.duracionDias +
          " días? Es una operación de demostración sin cobro bancario.",
      )
    )
      this.operation("/suscripciones", { planId: p.id }, "alta:" + p.id);
  }
  renovar(s: Suscripcion) {
    if (
      confirm(
        "¿Renovar " +
          s.nombrePlan +
          " con el precio y duración actuales del plan?",
      )
    )
      this.operation(
        "/suscripciones/" + s.id + "/renovar",
        {},
        "renovar:" + s.id,
      );
  }
  cancelar(s: Suscripcion) {
    if (
      confirm(
        "¿Cancelar " +
          s.nombrePlan +
          "? Se conserva el historial y no se simula un reembolso.",
      )
    )
      this.send(this.api.post("/suscripciones/" + s.id + "/cancelar"), () =>
        this.load(),
      );
  }
}
