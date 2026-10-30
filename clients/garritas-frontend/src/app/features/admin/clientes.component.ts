import { Component, inject, signal } from "@angular/core";
import { FormsModule } from "@angular/forms";
import {
  DomainApi,
  Feedback,
  Perfil,
  Mascota,
  PageResponse,
  Rol,
} from "../../core/domain-api";

@Component({
  selector: "app-clientes",
  imports: [FormsModule],
  templateUrl: "./clientes.component.html",
})
export class ClientesComponent extends Feedback {
  private readonly api = inject(DomainApi);

  readonly clientes = signal<Perfil[]>([]);
  readonly loading = signal(true);
  readonly search = signal("");
  readonly page = signal(0);
  readonly pageSize = signal(10);
  readonly totalPages = signal(0);
  readonly totalElements = signal(0);

  // Modal 1: Crear / Editar Cliente
  readonly showClientModal = signal(false);
  id: number | undefined;
  model = {
    nombre: "",
    email: "",
    telefono: "",
    direccion: "",
    dni: "",
    roleIds: [] as number[],
  };

  // Modal 2: Mascotas del Cliente
  readonly showPetModal = signal(false);
  activeClient = signal<Perfil | null>(null);
  clientPets = signal<Mascota[]>([]);
  petModel = {
    nombre: "",
    especie: "Perro",
    raza: "",
    edad: 0,
    edadUnidad: "MESES" as "DIAS" | "MESES",
  };
  editingPetId: number | undefined;

  clienteRoleId: number | undefined;

  constructor() {
    super();
    this.api.get<Rol[]>("/usuarios/roles").subscribe({
      next: (roles) => {
        const found = roles.find((r) => r.nombre.toUpperCase() === "CLIENTE");
        if (found) this.clienteRoleId = found.id;
      },
    });
    this.load();
  }

  load() {
    this.loading.set(true);
    const q = this.search().trim();
    const p = this.page();
    const s = this.pageSize();

    // Filtra exclusivamente usuarios con rol CLIENTE
    let url = `/usuarios?rol=CLIENTE&page=${p}&size=${s}`;
    if (q) url += `&q=${encodeURIComponent(q)}`;

    this.api.get<PageResponse<Perfil>>(url).subscribe({
      next: (resp) => {
        this.clientes.set(resp.content || []);
        this.totalPages.set(resp.totalPages || 0);
        this.totalElements.set(resp.totalElements || 0);
        this.loading.set(false);
      },
      error: (e) => {
        this.loading.set(false);
        this.report(e);
      },
    });
  }

  onSearchChange(val: string) {
    this.search.set(val);
    this.page.set(0);
    this.load();
  }

  goToPage(p: number) {
    if (p >= 0 && p < this.totalPages()) {
      this.page.set(p);
      this.load();
    }
  }

  // --- Modal Cliente ---
  openNewClientModal() {
    this.id = undefined;
    this.model = {
      nombre: "",
      email: "",
      telefono: "",
      direccion: "",
      dni: "",
      roleIds: this.clienteRoleId ? [this.clienteRoleId] : [],
    };
    this.showClientModal.set(true);
  }

  openEditClientModal(p: Perfil) {
    this.id = p.id;
    this.model = {
      nombre: p.nombre,
      email: p.email,
      telefono: p.telefono ?? "",
      direccion: p.direccion ?? "",
      dni: p.dni ?? "",
      roleIds: (p.roles || []).map((r) => r.id),
    };
    if (
      this.clienteRoleId &&
      !this.model.roleIds.includes(this.clienteRoleId)
    ) {
      this.model.roleIds.push(this.clienteRoleId);
    }
    this.showClientModal.set(true);
  }

  closeClientModal() {
    this.showClientModal.set(false);
    this.id = undefined;
  }

  save() {
    const payload = {
      nombre: this.model.nombre.trim(),
      email: this.model.email.trim(),
      telefono: this.model.telefono.trim(),
      direccion: this.model.direccion.trim(),
      dni: this.model.dni.trim(),
      roleIds:
        this.model.roleIds.length > 0
          ? this.model.roleIds
          : this.clienteRoleId
            ? [this.clienteRoleId]
            : [],
    };

    if (this.id) {
      this.send(this.api.put<Perfil>(`/usuarios/${this.id}`, payload), () => {
        this.closeClientModal();
        this.load();
      });
    } else {
      this.send(this.api.post<Perfil>("/usuarios", payload), () => {
        this.closeClientModal();
        this.load();
      });
    }
  }

  remove(p: Perfil) {
    if (
      confirm(`¿Eliminar al cliente "${p.nombre}" y sus mascotas asociadas?`)
    ) {
      this.send(this.api.delete(`/usuarios/${p.id}`), () => this.load());
    }
  }

  // --- Modal Mascotas ---
  openPetModal(p: Perfil) {
    this.activeClient.set(p);
    this.editingPetId = undefined;
    this.petModel = {
      nombre: "",
      especie: "Perro",
      raza: "",
      edad: 0,
      edadUnidad: "MESES" as "DIAS" | "MESES",
    };
    this.showPetModal.set(true);
    this.loadClientPets(p.id);
  }

  closePetModal() {
    this.showPetModal.set(false);
    this.activeClient.set(null);
    this.clientPets.set([]);
    this.editingPetId = undefined;
  }

  loadClientPets(userId: number) {
    this.api.get<Mascota[]>(`/usuarios/${userId}/mascotas`).subscribe({
      next: (pets) => this.clientPets.set(pets || []),
      error: (e) => this.report(e),
    });
  }

  editPet(m: Mascota) {
    this.editingPetId = m.id;
    this.petModel = {
      nombre: m.nombre,
      especie: m.especie,
      raza: m.raza ?? "",
      edad: m.edad ?? 0,
      edadUnidad: m.edadUnidad,
    };
  }

  cancelEditPet() {
    this.editingPetId = undefined;
    this.petModel = {
      nombre: "",
      especie: "Perro",
      raza: "",
      edad: 0,
      edadUnidad: "MESES" as "DIAS" | "MESES",
    };
  }

  savePet() {
    const c = this.activeClient();
    if (!c) return;

    const payload = {
      nombre: this.petModel.nombre.trim(),
      especie: this.petModel.especie,
      raza: this.petModel.raza.trim(),
      edad: Number(this.petModel.edad),
      edadUnidad: this.petModel.edadUnidad,
    };

    if (this.editingPetId) {
      this.send(
        this.api.put<Mascota>(
          `/usuarios/${c.id}/mascotas/${this.editingPetId}`,
          payload,
        ),
        () => {
          this.cancelEditPet();
          this.loadClientPets(c.id);
        },
      );
    } else {
      this.send(
        this.api.post<Mascota>(`/usuarios/${c.id}/mascotas`, payload),
        () => {
          this.cancelEditPet();
          this.loadClientPets(c.id);
        },
      );
    }
  }

  removePet(m: Mascota) {
    const c = this.activeClient();
    if (!c) return;
    if (confirm(`¿Eliminar a la mascota "${m.nombre}"?`)) {
      this.send(this.api.delete(`/usuarios/${c.id}/mascotas/${m.id}`), () =>
        this.loadClientPets(c.id),
      );
    }
  }
}
