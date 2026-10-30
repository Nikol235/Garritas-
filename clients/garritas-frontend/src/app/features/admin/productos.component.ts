import { Component, inject, signal } from "@angular/core";
import { FormsModule } from "@angular/forms";
import { CurrencyPipe } from "@angular/common";
import { DomainApi, Feedback, PageResponse } from "../../core/domain-api";
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

  // Modal flotante para crear / editar producto
  readonly showProductModal = signal(false);

  // Search & Pagination
  readonly search = signal("");
  readonly selectedCatFilter = signal(0);
  readonly page = signal(0);
  readonly pageSize = signal(10);
  readonly totalPages = signal(1);
  readonly totalElements = signal(0);

  id: number | undefined;
  model: {
    nombre: string;
    descripcion: string;
    precio: number;
    stock: number;
    activo: boolean;
    categoriaIds: number[];
  } = {
    nombre: "",
    descripcion: "",
    precio: 0,
    stock: 0,
    activo: true,
    categoriaIds: [],
  };

  constructor() {
    super();
    this.loadCategorias();
    this.load();
  }

  loadCategorias() {
    this.api.get<Categoria[]>("/categorias").subscribe({
      next: (c) => this.categorias.set(c),
      error: (e) => this.report(e),
    });
  }

  load() {
    const q = this.search().trim();
    const cat = this.selectedCatFilter();
    let url = `/productos?page=${this.page()}&size=${this.pageSize()}`;
    if (q) url += `&q=${encodeURIComponent(q)}`;
    if (cat > 0) url += `&categoriaId=${cat}`;

    this.api.get<PageResponse<Producto> | Producto[]>(url).subscribe({
      next: (res) => {
        if ("content" in res) {
          this.productos.set(res.content);
          this.totalPages.set(res.totalPages || 1);
          this.totalElements.set(res.totalElements || 0);
        } else {
          this.productos.set(res);
          this.totalPages.set(1);
          this.totalElements.set(res.length);
        }
      },
      error: (e) => this.report(e),
    });
  }

  onFilterChange() {
    this.page.set(0);
    this.load();
  }

  goToPage(p: number) {
    if (p >= 0 && p < this.totalPages()) {
      this.page.set(p);
      this.load();
    }
  }

  openNewProductModal() {
    this.reset();
    this.showProductModal.set(true);
  }

  openEditProductModal(p: Producto) {
    this.edit(p);
    this.showProductModal.set(true);
  }

  closeProductModal() {
    this.showProductModal.set(false);
    this.reset();
  }

  toggleCategoria(id: number) {
    if (this.model.categoriaIds.includes(id)) {
      this.model.categoriaIds = this.model.categoriaIds.filter((cid) => cid !== id);
    } else {
      this.model.categoriaIds = [...this.model.categoriaIds, id];
    }
  }

  edit(p: Producto) {
    this.id = p.id;
    const catIds =
      p.categorias && p.categorias.length > 0
        ? p.categorias.map((c) => c.id)
        : p.categoria
          ? [p.categoria.id]
          : [];

    this.model = {
      nombre: p.nombre,
      descripcion: p.descripcion ?? "",
      precio: p.precio,
      stock: p.stock,
      activo: p.activo,
      categoriaIds: catIds,
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
      categoriaIds: [],
    };
  }

  save() {
    const payload = {
      ...this.model,
      categoriaId: this.model.categoriaIds[0] || 0,
    };

    this.send(
      this.id
        ? this.api.put<Producto>("/productos/" + this.id, payload)
        : this.api.post<Producto>("/productos", payload),
      () => {
        this.closeProductModal();
        this.load();
      },
    );
  }

  deactivate(p: Producto) {
    if (confirm("¿Desactivar " + p.nombre + "?")) {
      this.send(this.api.delete("/productos/" + p.id), () => this.load());
    }
  }
}
