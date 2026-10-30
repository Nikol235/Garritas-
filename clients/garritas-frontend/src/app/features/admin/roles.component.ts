import { Component, inject, signal } from "@angular/core";
import { FormsModule } from "@angular/forms";
import { DomainApi, Feedback, Rol } from "../../core/domain-api";

@Component({
  selector: "app-roles",
  imports: [FormsModule],
  templateUrl: "./roles.component.html",
})
export class RolesComponent extends Feedback {
  private readonly api = inject(DomainApi);
  readonly roles = signal<Rol[]>([]);
  readonly loading = signal(true);
  readonly showModal = signal(false);
  readonly editingRol = signal<Rol | null>(null);

  model = { nombre: "", descripcion: "" };

  constructor() {
    super();
    this.load();
  }

  load() {
    this.loading.set(true);
    this.api.get<Rol[]>("/usuarios/roles").subscribe({
      next: (r) => {
        this.roles.set(r);
        this.loading.set(false);
      },
      error: (e) => {
        this.loading.set(false);
        this.report(e);
      },
    });
  }

  openNewModal() {
    this.editingRol.set(null);
    this.model = { nombre: "", descripcion: "" };
    this.showModal.set(true);
  }

  openEditModal(r: Rol) {
    this.editingRol.set(r);
    this.model = { nombre: r.nombre, descripcion: r.descripcion || "" };
    this.showModal.set(true);
  }

  closeModal() {
    this.showModal.set(false);
    this.editingRol.set(null);
    this.model = { nombre: "", descripcion: "" };
  }

  save() {
    const edit = this.editingRol();
    const payload = {
      nombre: this.model.nombre.trim(),
      descripcion: this.model.descripcion.trim(),
    };

    if (edit) {
      this.send(
        this.api.put<Rol>(`/usuarios/roles/${edit.id}`, payload),
        () => {
          this.closeModal();
          this.load();
        },
      );
    } else {
      this.send(this.api.post<Rol>("/usuarios/roles", payload), () => {
        this.closeModal();
        this.load();
      });
    }
  }

  remove(r: Rol) {
    if (confirm(`¿Estás seguro de eliminar el rol "${r.nombre}"?`)) {
      this.send(this.api.delete(`/usuarios/roles/${r.id}`), () => this.load());
    }
  }
}
