import { Component, inject, input, output, signal } from "@angular/core";
import { CurrencyPipe } from "@angular/common";
import { FormsModule } from "@angular/forms";
import { DomainApi, Cobertura } from "../../core/domain-api";
import { CartStore } from "./cart-store";

@Component({
  selector: "app-cart-panel",
  imports: [CurrencyPipe, FormsModule],
  templateUrl: "./cart-panel.html",
})
export class CartPanel {
  readonly cart = inject(CartStore);
  readonly busy = input(false);
  readonly authenticated = input(false);
  readonly checkout = output<void>();
  readonly login = output<void>();
  readonly message = signal("");
  private readonly api = inject(DomainApi);
  readonly shippingError = signal("");
  constructor() {
    this.refreshShipping();
  }
  refreshShipping() {
    this.shippingError.set("");
    this.api.get<Cobertura[]>("/coberturas").subscribe({
      next: (c) => this.cart.coberturas.set(c.filter((x) => x.activo)),
      error: () => {
        this.cart.coberturas.set([]);
        this.shippingError.set(
          "No pudimos consultar las tarifas. Puedes reintentar o elegir recojo en sede.",
        );
      },
    });
  }
  change(id: number, value: number, input: HTMLInputElement) {
    const accepted = this.cart.setQuantity(id, value);
    this.message.set(
      accepted
        ? ""
        : "Introduce una cantidad entera entre 1 y el stock disponible.",
    );
    input.value = String(this.cart.quantity(id));
  }
}
