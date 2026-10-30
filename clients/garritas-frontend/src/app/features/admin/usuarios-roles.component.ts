import { Component, inject, signal } from "@angular/core";
import { FormsModule } from "@angular/forms";
import { DomainApi, Feedback, Perfil, Rol, PageResponse } from "../../core/domain-api";

@Component({
  selector: "app-usuarios-roles",
  imports: [FormsModule],
  templateUrl: "./usuarios-roles.component.html",
})
export class UsuariosRolesComponent extends Feedback {
  private readonly api = inject(DomainApi);

  readonly usuarios = signal<Perfil[]>([]);
  readonly roles = signal<Rol[]>([]);
  readonly loading = signal(true);
  readonly search = signal("");
  readonly page = signal(0);
  readonly pageSize = signal(10);
  readonly totalPages = signal(0);
  readonly totalElements = signal(0);

  // Modal 1: Crear / Editar Usuario
  readonly showUserModal = signal(false);
  editingUserId: number | undefined;
  userModel = {
    nombre: "",
    email: "",
    telefono: "",
    direccion: "",
    dni: "",
    roleIds: [] as number[],
  };

  // Modal 2: Asignación dedicada de Roles (Muchos a Muchos: USUARIO_ROL)
  readonly showAssignModal = signal(false);
  assigningUser = signal<Perfil | null>(null);
  selectedRoleIds = signal<number[]>([]);

  constructor() {
    super();
    this.loadRoles();
    this.load();
  }

  loadRoles() {
    this.api.get<Rol[]>("/usuarios/roles").subscribe({
      next: (r) => this.roles.set(r),
      error: (e) => this.report(e),
    });
  }

  load() {
    this.loading.set(true);
    const q = this.search().trim();
    const p = this.page();
    const s = this.pageSize();

    let url = `/usuarios?page=${p}&size=${s}`;
    if (q) url += `&q=${encodeURIComponent(q)}`;

    this.api.get<PageResponse<Perfil>>(url).subscribe({
      next: (resp) => {
        this.usuarios.set(resp.content || []);
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

  // --- Modal Crear/Editar Usuario ---
  openNewUserModal() {
    this.editingUserId = undefined;
    this.userModel = {
      nombre: "",
      email: "",
      telefono: "",
      direccion: "",
      dni: "",
      roleIds: [],
    };
    this.showUserModal.set(true);
  }

  openEditUserModal(u: Perfil) {
    this.editingUserId = u.id;
    this.userModel = {
      nombre: u.nombre,
      email: u.email,
      telefono: u.telefono ?? "",
      direccion: u.direccion ?? "",
      dni: u.dni ?? "",
      roleIds: (u.roles || []).map((r) => r.id),
    };
    this.showUserModal.set(true);
  }

  closeUserModal() {
    this.showUserModal.set(false);
    this.editingUserId = undefined;
  }

  toggleUserModelRole(roleId: number) {
    const list = [...this.userModel.roleIds];
    const idx = list.indexOf(roleId);
    if (idx >= 0) {
      list.splice(idx, 1);
    } else {
      list.push(roleId);
    }
    this.userModel.roleIds = list;
  }

  saveUser() {
    const payload = {
      nombre: this.userModel.nombre.trim(),
      email: this.userModel.email.trim(),
      telefono: this.userModel.telefono.trim(),
      direccion: this.userModel.direccion.trim(),
      dni: this.userModel.dni.trim(),
      roleIds: this.userModel.roleIds,
    };

    if (this.editingUserId) {
      this.send(this.api.put<Perfil>(`/usuarios/${this.editingUserId}`, payload), () => {
        this.closeUserModal();
        this.load();
      });
    } else {
      this.send(this.api.post<Perfil>("/usuarios", payload), () => {
        this.closeUserModal();
        this.load();
      });
    }
  }

  // --- Modal Asignación de Roles (USUARIO_ROL) ---
  openAssignModal(u: Perfil) {
    this.assigningUser.set(u);
    this.selectedRoleIds.set((u.roles || []).map((r) => r.id));
    this.showAssignModal.set(true);
  }

  closeAssignModal() {
    this.showAssignModal.set(false);
    this.assigningUser.set(null);
    this.selectedRoleIds.set([]);
  }

  toggleAssignRole(roleId: number) {
    const current = [...this.selectedRoleIds()];
    const idx = current.indexOf(roleId);
    if (idx >= 0) {
      current.splice(idx, 1);
    } else {
      current.push(roleId);
    }
    this.selectedRoleIds.set(current);
  }

  saveRoleAssignment() {
    const u = this.assigningUser();
    if (!u) return;

    const payload = {
      nombre: u.nombre,
      email: u.email,
      telefono: u.telefono ?? "",
      direccion: u.direccion ?? "",
      dni: u.dni ?? "",
      roleIds: this.selectedRoleIds(),
    };

    this.send(this.api.put<Perfil>(`/usuarios/${u.id}`, payload), () => {
      this.closeAssignModal();
      this.load();
    });
  }

  remove(u: Perfil) {
    if (confirm(`¿Estás seguro de eliminar al usuario "${u.nombre}"?`)) {
      this.send(this.api.delete(`/usuarios/${u.id}`), () => this.load());
    }
  }
}

