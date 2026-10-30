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
  Oferta,
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
  readonly ofertas = signal<Oferta[]>([]);
  readonly label = stateLabel;
  model = {
    idMascota: 0,
    idSede: Number(
      sessionStorage.getItem("garritas-cita-sede") ?? this.cart.sedeId(),
    ),
    prestacionIds: [] as number[],
    profesionalId: Number(sessionStorage.getItem("garritas-profesional") ?? 0),
    fechaHora: "",
    motivo: "",
  };
  constructor() {
    super();
    this.load();
    this.loadOfertas();
  }
  load() {
    this.api.get<Cita[]>("/citas").subscribe({
      next: (c) => this.citas.set(c),
      error: (e) => this.report(e),
    });
    this.api.get<Sede[]>("/sedes").subscribe({
      next: (s) => this.sedes.set(s.filter((x) => x.activo)),
      error: (e) => this.report(e),
    });
    this.api.get<Profesional[]>("/especialistas").subscribe({
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
  loadOfertas() {
    this.ofertas.set([]);
    this.model.prestacionIds = [];
    if (!this.model.idSede) return;
    this.api
      .get<Oferta[]>("/sedes/" + this.model.idSede + "/prestaciones")
      .subscribe({
        next: (ofertas) => {
          this.ofertas.set(ofertas.filter((o) => o.activo));
          const selected = Number(
            sessionStorage.getItem("garritas-cita-prestacion") ?? 0,
          );
          if (ofertas.some((o) => o.prestacionId === selected && o.activo))
            this.model.prestacionIds = [selected];
          sessionStorage.removeItem("garritas-cita-prestacion");
          sessionStorage.removeItem("garritas-cita-sede");
        },
        error: (e) => this.report(e),
      });
  }
  changeSede() {
    this.model.profesionalId = 0;
    this.loadOfertas();
  }
  toggle(id: number) {
    this.model.prestacionIds = this.model.prestacionIds.includes(id)
      ? this.model.prestacionIds.filter((x) => x !== id)
      : [...this.model.prestacionIds, id];
  }
  selected() {
    return this.ofertas().filter((o) =>
      this.model.prestacionIds.includes(o.prestacionId),
    );
  }
  total() {
    return this.selected().reduce((n, o) => n + o.precio, 0);
  }
  duration() {
    return this.selected().reduce((n, o) => n + o.duracionMinutos, 0);
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
      !this.model.profesionalId ||
      !this.model.prestacionIds.length
    )
      return;
    const date = new Date(this.model.fechaHora);
    if (
      !Number.isFinite(date.getTime()) ||
      date.getTime() <= Date.now() ||
      date.getMinutes() % 30 !== 0
    ) {
      this.error.set("Elige una fecha futura a las :00 o :30.");
      return;
    }
    if (this.duration() > 480) {
      this.error.set("La cita no puede superar ocho horas.");
      return;
    }
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
