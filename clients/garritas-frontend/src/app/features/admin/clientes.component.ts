import { Component, inject, signal } from "@angular/core";
import { FormsModule } from "@angular/forms";
import { DomainApi, Feedback, Perfil } from "../../core/domain-api";
@Component({
  selector: "app-clientes",
  imports: [FormsModule],
  templateUrl: "./clientes.component.html",
})
export class ClientesComponent extends Feedback {
  private readonly api = inject(DomainApi);
  readonly clientes = signal<Perfil[]>([]);
  id: number | undefined;
  model = { nombre: "", email: "", telefono: "", direccion: "" };
  constructor() {
    super();
    this.load();
  }
  load() {
    this.api
      .get<Perfil[]>("/usuarios")
      .subscribe({
        next: (p) => this.clientes.set(p),
        error: (e) => this.report(e),
      });
  }
  edit(p: Perfil) {
    this.id = p.id;
    this.model = {
      nombre: p.nombre,
      email: p.email,
      telefono: p.telefono ?? "",
      direccion: p.direccion ?? "",
    };
  }
  save() {
    this.send(
      this.id
        ? this.api.put<Perfil>("/usuarios/" + this.id, this.model)
        : this.api.post<Perfil>("/usuarios", this.model),
      () => {
        this.id = undefined;
        this.model = { nombre: "", email: "", telefono: "", direccion: "" };
        this.load();
      },
    );
  }
  remove(p: Perfil) {
    if (confirm("¿Eliminar el perfil " + p.nombre + " y sus mascotas?"))
      this.send(this.api.delete("/usuarios/" + p.id), () => this.load());
  }
}
