import { Component, DestroyRef, inject, signal } from "@angular/core";
import { CurrencyPipe, DatePipe } from "@angular/common";
import { FormsModule } from "@angular/forms";
import { takeUntilDestroyed } from "@angular/core/rxjs-interop";
import { timer, EMPTY, exhaustMap, catchError } from "rxjs";
import { HttpErrorResponse } from "@angular/common/http";
import { Auth } from "./core/auth";
import { Api, Categoria, Producto, Venta, Pago, pending } from "./core/api";
import { CartStore } from "./features/cart/cart-store";
import { CartPanel } from "./features/cart/cart-panel";
import { ProductCatalog } from "./features/catalogo/product-catalog";

@Component({
  selector: "app-root",
  imports: [FormsModule, CurrencyPipe, DatePipe, CartPanel, ProductCatalog],
  templateUrl: "./app.html",
})
export class App {
  readonly auth = inject(Auth);
  readonly cart = inject(CartStore);
  private readonly api = inject(Api);
  private readonly destroy = inject(DestroyRef);
  readonly productos = signal<Producto[]>([]);
  readonly categorias = signal<Categoria[]>([]);
  readonly ventas = signal<Venta[]>([]);
  readonly pagos = signal<Record<number, Pago>>({});
  readonly error = signal("");
  readonly notice = signal("");
  readonly busy = signal(false);
  readonly loading = signal(true);
  readonly view = signal(this.cart.count() > 0 ? "nueva-orden" : "catalogo");
  readonly pending = pending;
  nombre = "";
  descripcion = "";
  categoriaId: number | undefined;

  constructor() {
    this.refreshCatalogo();
    if (this.auth.loggedIn()) this.refreshVentas();
    timer(3000, 3000)
      .pipe(
        exhaustMap(() => {
          if (
            !this.auth.loggedIn() ||
            !this.ventas().some((v) => pending(v.estado))
          )
            return EMPTY;
          return this.api.ventas().pipe(
            catchError((e) => {
              this.fail(e);
              return EMPTY;
            }),
          );
        }),
        takeUntilDestroyed(this.destroy),
      )
      .subscribe((ventas) => {
        this.ventas.set(ventas);
        if (!ventas.some((v) => pending(v.estado))) this.refreshCatalogo();
      });
  }

  refreshCatalogo() {
    this.loading.set(true);
    this.api.productos().subscribe({
      next: (p) => {
        this.productos.set(p);
        this.cart.reconcile(p);
        this.loading.set(false);
      },
      error: (e) => {
        this.loading.set(false);
        this.fail(e);
      },
    });
    this.api
      .categorias()
      .subscribe({
        next: (c) => this.categorias.set(c),
        error: (e) => this.fail(e),
      });
  }
  refreshVentas() {
    this.api
      .ventas()
      .subscribe({
        next: (v) => this.ventas.set(v),
        error: (e) => this.fail(e),
      });
  }
  add(producto: Producto) {
    if (this.busy()) return;
    this.error.set("");
    if (this.cart.add(producto))
      this.notice.set(producto.nombre + " añadido al carrito.");
    else
      this.error.set(
        "Ya tienes en el carrito todas las unidades disponibles de este producto.",
      );
  }
  checkout() {
    if (this.busy()) return;
    this.error.set("");
    if (!this.auth.loggedIn()) {
      this.auth.login();
      return;
    }
    if (!this.cart.valid()) {
      this.error.set(
        "Revisa los productos y las cantidades de tu carrito antes de confirmar.",
      );
      return;
    }
    this.busy.set(true);
    this.api
      .crearVenta(this.cart.payload(), this.cart.checkoutKey())
      .subscribe({
        next: (venta) => {
          this.busy.set(false);
          this.cart.clear();
          this.notice.set(
            "Pedido #" +
              venta.id +
              " registrado. Estamos verificando el inventario y el pago.",
          );
          this.view.set("pedidos");
          this.refreshVentas();
          this.refreshCatalogo();
        },
        error: (e) => {
          this.busy.set(false);
          this.fail(e);
          if (e.status === 409) this.refreshCatalogo();
        },
      });
  }
  consultarPago(id: number) {
    this.api
      .pago(id)
      .subscribe({
        next: (p) => this.pagos.update((all) => ({ ...all, [id]: p })),
        error: (e) => this.fail(e),
      });
  }
  edit(c: Categoria) {
    this.categoriaId = c.id;
    this.nombre = c.nombre;
    this.descripcion = c.descripcion ?? "";
  }
  save() {
    this.api
      .guardarCategoria(
        { nombre: this.nombre, descripcion: this.descripcion },
        this.categoriaId,
      )
      .subscribe({
        next: () => {
          this.nombre = "";
          this.descripcion = "";
          this.categoriaId = undefined;
          this.refreshCatalogo();
        },
        error: (e) => this.fail(e),
      });
  }
  remove(c: Categoria) {
    if (confirm("¿Eliminar categoría " + c.nombre + "?"))
      this.api
        .borrarCategoria(c.id)
        .subscribe({
          next: () => this.refreshCatalogo(),
          error: (e) => this.fail(e),
        });
  }
  private fail(e: HttpErrorResponse) {
    this.error.set(
      e.status === 401
        ? "La sesión expiró. Inicia sesión de nuevo."
        : e.status === 403
          ? "No tienes permiso para esta operación."
          : e.status === 0
            ? "No se pudo contactar al servidor. Tu carrito se conserva; puedes reintentar la compra sin duplicarla."
            : (e.error?.detail ??
              e.error?.message ??
              "No se pudo completar la operación. Inténtalo de nuevo."),
    );
  }
}
