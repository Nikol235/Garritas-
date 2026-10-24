import { Component, inject, signal, output } from "@angular/core";
import { FormsModule } from "@angular/forms";
import { forkJoin } from "rxjs";
import { Auth } from "../../core/auth";
import {
  DomainApi,
  Feedback,
  Sede,
  Especialidad,
  Profesional,
} from "../../core/domain-api";
@Component({
  selector: "app-especialistas",
  imports: [FormsModule],
  templateUrl: "./especialistas.component.html",
})
export class EspecialistasComponent extends Feedback {
  readonly auth = inject(Auth);
  private readonly api = inject(DomainApi);
  readonly reservar = output<number>();
  readonly profesionales = signal<Profesional[]>([]);
  readonly especialidades = signal<Especialidad[]>([]);
  readonly sedes = signal<Sede[]>([]);
  id: number | undefined;
  especialidadId: number | undefined;
  model = {
    nombre: "",
    email: "",
    telefono: "",
    sedeId: 0,
    activo: true,
    especialidadIds: [] as number[],
  };
  esp = { nombre: "", descripcion: "", activo: true };
  constructor() {
    super();
    this.load();
  }
  load() {
    forkJoin({
      p: this.api.get<Profesional[]>("/especialistas"),
      e: this.api.get<Especialidad[]>("/especialidades"),
      s: this.api.get<Sede[]>("/sedes"),
    }).subscribe({
      next: (r) => {
        this.profesionales.set(r.p);
        this.especialidades.set(r.e);
        this.sedes.set(r.s);
      },
      error: (e) => this.report(e),
    });
  }
  sede(id: number | null) {
    return (
      this.sedes().find((s) => s.id === id)?.nombre ??
      "Atención en nuestras sedes"
    );
  }
  edit(p: Profesional) {
    this.id = p.id;
    this.model = {
      nombre: p.nombre,
      email: p.email,
      telefono: p.telefono,
      sedeId: p.sedeId ?? 0,
      activo: p.activo,
      especialidadIds: p.especialidades.map((e) => e.id),
    };
  }
  toggle(id: number) {
    this.model.especialidadIds = this.model.especialidadIds.includes(id)
      ? this.model.especialidadIds.filter((x) => x !== id)
      : [...this.model.especialidadIds, id];
  }
  save() {
    const data = { ...this.model, sedeId: this.model.sedeId || null };
    this.send(
      this.id
        ? this.api.put<Profesional>("/especialistas/" + this.id, data)
        : this.api.post<Profesional>("/especialistas", data),
      () => {
        this.id = undefined;
        this.model = {
          nombre: "",
          email: "",
          telefono: "",
          sedeId: 0,
          activo: true,
          especialidadIds: [],
        };
        this.load();
      },
    );
  }
  deactivate(p: Profesional) {
    if (confirm("¿Desactivar a " + p.nombre + "?"))
      this.send(this.api.delete("/especialistas/" + p.id), () => this.load());
  }
  editEsp(e: Especialidad) {
    this.especialidadId = e.id;
    this.esp = {
      nombre: e.nombre,
      descripcion: e.descripcion,
      activo: e.activo,
    };
  }
  saveEsp() {
    this.send(
      this.especialidadId
        ? this.api.put<Especialidad>(
            "/especialidades/" + this.especialidadId,
            this.esp,
          )
        : this.api.post<Especialidad>("/especialidades", this.esp),
      () => {
        this.especialidadId = undefined;
        this.esp = { nombre: "", descripcion: "", activo: true };
        this.load();
      },
    );
  }
  deleteEsp(e: Especialidad) {
    if (confirm("¿Eliminar la especialidad " + e.nombre + "?"))
      this.send(this.api.delete("/especialidades/" + e.id), () => this.load());
  }
}
