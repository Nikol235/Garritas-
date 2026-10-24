import { Component, inject, signal, output } from "@angular/core";
import { FormsModule } from "@angular/forms";
import { DatePipe } from "@angular/common";
import { Auth } from "../../core/auth";
import {
  DomainApi,
  Feedback,
  Sede,
  Profesional,
  Mascota,
  Cita,
  stateLabel,
} from "../../core/domain-api";
import { CartStore } from "../cart/cart-store";
@Component({
  selector: "app-citas",
  imports: [FormsModule, DatePipe],
  templateUrl: "./citas.component.html",
})
export class CitasComponent extends Feedback {
  readonly auth = inject(Auth);
  readonly cart = inject(CartStore);
  private readonly api = inject(DomainApi);
  readonly cuenta = output<void>();
  readonly citas = signal<Cita[]>([]);
  readonly sedes = signal<Sede[]>([]);
  readonly profesionales = signal<Profesional[]>([]);
  readonly mascotas = signal<Mascota[]>([]);
  readonly needsProfile = signal(false);
  readonly label = stateLabel;
  model = {
    idMascota: 0,
    idSede: this.cart.sedeId(),
    profesionalId: Number(sessionStorage.getItem("garritas-profesional") ?? 0),
    fechaHora: "",
    motivo: "",
  };
  constructor() {
    super();
    this.load();
  }
  load() {
    this.api
      .get<Cita[]>("/citas")
      .subscribe({
        next: (c) => this.citas.set(c),
        error: (e) => this.report(e),
      });
    this.api
      .get<Sede[]>("/sedes")
      .subscribe({
        next: (s) => this.sedes.set(s.filter((x) => x.activo)),
        error: (e) => this.report(e),
      });
    this.api
      .get<Profesional[]>("/especialistas")
      .subscribe({
        next: (p) => this.profesionales.set(p.filter((x) => x.activo)),
        error: (e) => this.report(e),
      });
    this.api.get<Mascota[]>("/usuarios/me/mascotas").subscribe({
      next: (p) => {
        this.mascotas.set(p);
        this.needsProfile.set(false);
      },
      error: (e) => {
        if (e.status === 404) this.needsProfile.set(true);
        else this.report(e);
      },
    });
  }
  available() {
    return this.profesionales().filter(
      (p) => !p.sedeId || p.sedeId === this.model.idSede,
    );
  }
  save() {
    if (
      !this.model.idSede ||
      !this.model.idMascota ||
      !this.model.profesionalId
    )
      return;
    this.send(
      this.api.post<Cita>("/citas", {
        ...this.model,
        fechaHora: new Date(this.model.fechaHora).toISOString(),
      }),
      () => {
        this.model.motivo = "";
        this.model.fechaHora = "";
        this.load();
      },
    );
  }
  action(c: Cita, action: string) {
    this.send(this.api.post<Cita>("/citas/" + c.id + "/" + action), () =>
      this.load(),
    );
  }
}
