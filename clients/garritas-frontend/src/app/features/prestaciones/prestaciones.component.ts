import { Component, inject, signal, output } from "@angular/core";
import { FormsModule } from "@angular/forms";
import { CurrencyPipe } from "@angular/common";
import { forkJoin } from "rxjs";
import { Auth } from "../../core/auth";
import {
  DomainApi,
  Feedback,
  Sede,
  Prestacion,
  Oferta,
} from "../../core/domain-api";
@Component({
  selector: "app-prestaciones",
  imports: [FormsModule, CurrencyPipe],
  templateUrl: "./prestaciones.component.html",
})
export class PrestacionesComponent extends Feedback {
  readonly auth = inject(Auth);
  private readonly api = inject(DomainApi);
  readonly reservar = output<{ sedeId: number; prestacionId: number }>();
  readonly sedes = signal<Sede[]>([]);
  readonly prestaciones = signal<Prestacion[]>([]);
  readonly ofertas = signal<Oferta[]>([]);
  sedeId = Number(sessionStorage.getItem("garritas-servicios-sede") ?? 0);
  id: number | undefined;
  model = {
    nombre: "",
    descripcion: "",
    activo: true,
    componenteIds: [] as number[],
  };
  oferta = { prestacionId: 0, precio: 60, duracionMinutos: 30, activo: true };
  constructor() {
    super();
    this.load();
  }
  load() {
    forkJoin({
      s: this.api.get<Sede[]>("/sedes"),
      p: this.api.get<Prestacion[]>("/prestaciones"),
    }).subscribe({
      next: (r) => {
        this.sedes.set(r.s);
        this.prestaciones.set(r.p);
        sessionStorage.removeItem("garritas-servicios-sede");
        if (
          !r.s.some(
            (s) => s.id === this.sedeId && (s.activo || this.auth.admin()),
          )
        )
          this.sedeId = 0;
        if (!this.sedeId) this.sedeId = r.s.find((s) => s.activo)?.id ?? 0;
        this.loadOfertas();
      },
      error: (e) => this.report(e),
    });
  }
  loadOfertas() {
    this.ofertas.set([]);
    const selected = this.sedeId;
    if (this.sedeId)
      this.api
        .get<Oferta[]>("/sedes/" + this.sedeId + "/prestaciones")
        .subscribe({
          next: (o) => {
            if (this.sedeId === selected) this.ofertas.set(o);
          },
          error: (e) => this.report(e),
        });
  }
  edit(p: Prestacion) {
    this.id = p.id;
    this.model = {
      nombre: p.nombre,
      descripcion: p.descripcion ?? "",
      activo: p.activo,
      componenteIds: (p.componentes ?? []).map((c) => c.id),
    };
  }
  reset() {
    this.id = undefined;
    this.model = {
      nombre: "",
      descripcion: "",
      activo: true,
      componenteIds: [] as number[],
    };
  }
  individuales() {
    return this.prestaciones().filter(
      (p) => p.id !== this.id && !p.componentes?.length && p.activo,
    );
  }
  toggleComponente(id: number) {
    this.model.componenteIds = this.model.componenteIds.includes(id)
      ? this.model.componenteIds.filter((x) => x !== id)
      : [...this.model.componenteIds, id];
  }
  save() {
    this.send(
      this.id
        ? this.api.put("/prestaciones/" + this.id, this.model)
        : this.api.post("/prestaciones", this.model),
      () => {
        this.reset();
        this.load();
      },
    );
  }
  remove(p: Prestacion) {
    if (confirm("¿Desactivar " + p.nombre + "?"))
      this.send(this.api.delete("/prestaciones/" + p.id), () => this.load());
  }
  editOferta(o: Oferta) {
    this.oferta = {
      prestacionId: o.prestacionId,
      precio: o.precio,
      duracionMinutos: o.duracionMinutos,
      activo: o.activo,
    };
  }
  saveOferta() {
    this.send(
      this.api.put("/sedes/" + this.sedeId + "/prestaciones", this.oferta),
      () => this.loadOfertas(),
    );
  }
}
