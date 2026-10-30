import { Component, computed, input, output, signal } from "@angular/core";
import { CurrencyPipe } from "@angular/common";
import { FormsModule } from "@angular/forms";
import { Categoria, Producto } from "../../core/api";

@Component({
  selector: "app-product-catalog",
  imports: [CurrencyPipe, FormsModule],
  templateUrl: "./product-catalog.html",
})
export class ProductCatalog {
  readonly productos = input.required<Producto[]>();
  readonly categorias = input<Categoria[]>([]);
  readonly busy = input(false);
  readonly purchasable = input(true);
  readonly add = output<Producto>();

  readonly search = signal("");
  readonly category = signal(0);
  readonly page = signal(0);
  readonly pageSize = signal(8);

  readonly filtered = computed(() => {
    const normalize = (value: string) =>
      value
        .normalize("NFD")
        .replace(/[\u0300-\u036f]/g, "")
        .toLowerCase();
    const query = normalize(this.search().trim());
    const selectedCat = Number(this.category());

    return this.productos().filter((p) => {
      if (!p.activo) return false;
      const matchesCategory =
        !selectedCat ||
        (p.categorias && p.categorias.some((c) => c.id === selectedCat)) ||
        (p.categoria && p.categoria.id === selectedCat);

      if (!matchesCategory) return false;
      if (!query) return true;

      const searchableText = `${p.nombre} ${p.descripcion ?? ""} ${
        p.categorias
          ? p.categorias.map((c) => c.nombre).join(" ")
          : (p.categoria?.nombre ?? "")
      }`;
      return normalize(searchableText).includes(query);
    });
  });

  readonly totalPages = computed(() => {
    return Math.ceil(this.filtered().length / this.pageSize()) || 1;
  });

  readonly paginated = computed(() => {
    const start = this.page() * this.pageSize();
    return this.filtered().slice(start, start + this.pageSize());
  });

  onSearchChange(term: string) {
    this.search.set(term);
    this.page.set(0);
  }

  onCategoryChange(catId: number) {
    this.category.set(catId);
    this.page.set(0);
  }

  goToPage(p: number) {
    if (p >= 0 && p < this.totalPages()) {
      this.page.set(p);
    }
  }

  icon(producto: Producto) {
    const catNames =
      producto.categorias && producto.categorias.length > 0
        ? producto.categorias.map((c) => c.nombre.toLowerCase()).join(" ")
        : (producto.categoria?.nombre?.toLowerCase() ?? "");

    if (catNames.includes("alimento")) return "🥣";
    if (catNames.includes("higiene")) return "🧼";
    if (catNames.includes("juguete")) return "🎾";
    if (catNames.includes("hábitat") || catNames.includes("habitat"))
      return "🏠";
    return "🐾";
  }
}
