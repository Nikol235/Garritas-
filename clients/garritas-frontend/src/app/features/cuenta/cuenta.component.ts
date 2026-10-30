import { Component, inject, signal } from "@angular/core";
import { FormsModule } from "@angular/forms";
import { DomainApi, Feedback, Perfil, Mascota } from "../../core/domain-api";
import { Auth } from "../../core/auth";

@Component({
  selector: "app-cuenta",
  imports: [FormsModule],
  templateUrl: "./cuenta.component.html",
})
export class CuentaComponent extends Feedback {
  readonly auth = inject(Auth);
  private readonly api = inject(DomainApi);
  readonly loading = signal(true);
  readonly perfil = signal<Perfil | null>(null);
  readonly mascotas = signal<Mascota[]>([]);

  model = { nombre: "", email: "", telefono: "", direccion: "", dni: "" };
  pet = { nombre: "", especie: "Perro", raza: "", edad: 0 };
  petId: number | undefined;

  constructor() {
    super();
    this.load();
  }

  load() {
    this.loading.set(true);
    this.api.get<Perfil>("/usuarios/me").subscribe({
      next: (p) => {
        this.perfil.set(p);
        this.model = {
          nombre: p.nombre || "",
          email: p.email || "",
          telefono: p.telefono ?? "",
          direccion: p.direccion ?? "",
          dni: p.dni ?? "",
        };
        this.loading.set(false);
        if (this.esCliente()) {
          this.loadPets();
        }
      },
      error: (e) => {
        this.loading.set(false);
        if (e.status !== 404) this.report(e);
      },
    });
  }

  esCliente(): boolean {
    if (this.auth.admin()) {
      return false;
    }
    const roles = this.perfil()?.roles;
    if (!roles || roles.length === 0) return true;
    return roles.some((r) => r.nombre.toUpperCase() === "CLIENTE");
  }

  loadPets() {
    this.api.get<Mascota[]>("/usuarios/me/mascotas").subscribe({
      next: (p) => this.mascotas.set(p),
      error: (e) => this.report(e),
    });
  }

  save() {
    this.send(this.api.put<Perfil>("/usuarios/me", this.model), (p) => {
      this.perfil.set(p);
      if (this.esCliente()) {
        this.loadPets();
      }
    });
  }

  savePet() {
    this.send(
      this.petId
        ? this.api.put<Mascota>("/usuarios/me/mascotas/" + this.petId, this.pet)
        : this.api.post<Mascota>("/usuarios/me/mascotas", this.pet),
      () => {
        this.petId = undefined;
        this.pet = { nombre: "", especie: "Perro", raza: "", edad: 0 };
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
    };
  }

  cancelPet() {
    this.petId = undefined;
    this.pet = { nombre: "", especie: "Perro", raza: "", edad: 0 };
  }

  remove(p: Mascota) {
    if (confirm("¿Eliminar a " + p.nombre + " de tus mascotas?")) {
      this.send(this.api.delete("/usuarios/me/mascotas/" + p.id), () =>
        this.loadPets(),
      );
    }
  }
}
