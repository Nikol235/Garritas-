import { Component, inject, signal } from "@angular/core";
import { FormsModule } from "@angular/forms";
import { CurrencyPipe } from "@angular/common";
import { forkJoin } from "rxjs";
import { DomainApi, Feedback } from "../../core/domain-api";
import { Producto, Categoria } from "../../core/api";
@Component({
  selector: "app-admin-productos",
  imports: [FormsModule, CurrencyPipe],
  templateUrl: "./productos.component.html",
})
export class ProductosComponent extends Feedback {
  private readonly api = inject(DomainApi);
  readonly productos = signal<Producto[]>([]);
  readonly categorias = signal<Categoria[]>([]);
  id: number | undefined;
  model = {
    nombre: "",
    descripcion: "",
    precio: 0,
    stock: 0,
    activo: true,
    categoriaId: 0,
  };
  constructor() {
    super();
    this.load();
  }
  load() {
    forkJoin({
      p: this.api.get<Producto[]>("/productos"),
      c: this.api.get<Categoria[]>("/categorias"),
    }).subscribe({
      next: (r) => {
        this.productos.set(r.p);
        this.categorias.set(r.c);
      },
      error: (e) => this.report(e),
    });
  }
  edit(p: Producto) {
    this.id = p.id;
    this.model = {
      nombre: p.nombre,
      descripcion: p.descripcion ?? "",
      precio: p.precio,
      stock: p.stock,
      activo: p.activo,
      categoriaId: p.categoria.id,
    };
  }
  reset() {
    this.id = undefined;
    this.model = {
      nombre: "",
      descripcion: "",
      precio: 0,
      stock: 0,
      activo: true,
      categoriaId: 0,
    };
  }
  save() {
    this.send(
      this.id
        ? this.api.put<Producto>("/productos/" + this.id, this.model)
        : this.api.post<Producto>("/productos", this.model),
      () => {
        this.reset();
        this.load();
      },
    );
  }
  deactivate(p: Producto) {
    if (confirm("¿Desactivar " + p.nombre + "?"))
      this.send(this.api.delete("/productos/" + p.id), () => this.load());
  }
}
