import { Component, inject, signal } from "@angular/core";
import { switchMap } from "rxjs";
import { FormsModule } from "@angular/forms";
import { DomainApi, Feedback, Perfil, Mascota } from "../../core/domain-api";
@Component({
  selector: "app-cuenta",
  imports: [FormsModule],
  templateUrl: "./cuenta.component.html",
})
export class CuentaComponent extends Feedback {
  private readonly api = inject(DomainApi);
  readonly loading = signal(true);
  readonly loadFailed = signal(false);
  readonly guardado = signal(false);
  readonly perfil = signal<Perfil | null>(null);
  readonly mascotas = signal<Mascota[]>([]);
  model = { nombre: "", email: "", telefono: "", direccion: "", dni: "" };
  pet = {
    nombre: "",
    especie: "Perro",
    raza: "",
    edad: 0,
    edadUnidad: "MESES" as "DIAS" | "MESES",
  };
  petId: number | undefined;
  constructor() {
    super();
    this.load();
  }
  load() {
    this.loading.set(true);
    this.loadFailed.set(false);
    this.api.get<Perfil>("/usuarios/me").subscribe({
      next: (p) => {
        this.perfil.set(p);
        this.model = {
          nombre: p.nombre,
          email: p.email,
          telefono: p.telefono ?? "",
          direccion: p.direccion ?? "",
          dni: p.dni ?? "",
        };
        this.loading.set(false);
        this.loadPets();
      },
      error: (e) => {
        this.loading.set(false);
        if (e.status !== 404) {
          this.loadFailed.set(true);
          this.report(e);
        }
      },
    });
  }
  loadPets() {
    this.api.get<Mascota[]>("/usuarios/me/mascotas").subscribe({
      next: (p) => this.mascotas.set(p),
      error: (e) => this.report(e),
    });
  }
  save() {
    if (this.loading() || this.loadFailed()) return;
    const value = {
      ...this.model,
      nombre: this.model.nombre.trim(),
      email: this.model.email.trim(),
    };
    this.guardado.set(false);
    // Confirm with a persisted GET, not only the form's local values.
    this.send(
      this.api
        .put<Perfil>("/usuarios/me", value)
        .pipe(switchMap(() => this.api.get<Perfil>("/usuarios/me"))),
      (p) => {
        this.perfil.set(p);
        this.model = {
          nombre: p.nombre,
          email: p.email,
          telefono: p.telefono ?? "",
          direccion: p.direccion ?? "",
          dni: p.dni ?? "",
        };
        this.guardado.set(true);
        this.message.set(
          "Tu perfil se guardó correctamente. Ya puedes gestionar tus mascotas.",
        );
        this.loadPets();
      },
    );
  }
  edadValida() {
    return (
      Number.isInteger(this.pet.edad) &&
      this.pet.edad >= 0 &&
      this.pet.edad <= 36500
    );
  }
  savePet() {
    if (!this.edadValida()) {
      this.error.set("La edad debe ser un número entero de días o meses.");
      return;
    }
    this.send(
      this.petId
        ? this.api.put<Mascota>("/usuarios/me/mascotas/" + this.petId, this.pet)
        : this.api.post<Mascota>("/usuarios/me/mascotas", this.pet),
      () => {
        this.petId = undefined;
        this.pet = {
          nombre: "",
          especie: "Perro",
          raza: "",
          edad: 0,
          edadUnidad: "MESES" as "DIAS" | "MESES",
        };
        this.loadPets();
      },
    );
  }
  edit(p: Mascota) {
    this.petId = p.id;
    this.pet = {
      nombre: p.nombre,
      especie: p.especie,
      raza: p.raza ?? "",
      edad: p.edad ?? 0,
      edadUnidad: p.edadUnidad,
    };
  }
  remove(p: Mascota) {
    if (confirm("¿Eliminar a " + p.nombre + " de tus mascotas?"))
      this.send(this.api.delete("/usuarios/me/mascotas/" + p.id), () =>
        this.loadPets(),
      );
  }
}
