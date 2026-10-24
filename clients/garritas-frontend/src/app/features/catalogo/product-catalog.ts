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
  readonly add = output<Producto>();
  readonly search = signal("");
  readonly category = signal(0);
  readonly filtered = computed(() => {
    const normalize = (value: string) =>
      value
        .normalize("NFD")
        .replace(/[\u0300-\u036f]/g, "")
        .toLowerCase();
    const query = normalize(this.search().trim());
    return this.productos().filter(
      (p) =>
        p.activo &&
        (!this.category() || p.categoria.id === Number(this.category())) &&
        normalize(p.nombre + " " + (p.descripcion ?? "")).includes(query),
    );
  });
  icon(producto: Producto) {
    const category = producto.categoria.nombre.toLowerCase();
    if (category.includes("alimento")) return "🥣";
    if (category.includes("higiene")) return "🧼";
    if (category.includes("juguete")) return "🎾";
    if (category.includes("hábitat")) return "🏠";
    return "🐾";
  }
}
