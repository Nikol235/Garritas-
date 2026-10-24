import { beforeEach, describe, expect, it } from "vitest";
import { Producto } from "../../core/api";
import { CART_STORAGE_KEY, CartStore } from "./cart-store";

const food: Producto = {
  id: 1,
  nombre: "Alimento para perro",
  descripcion: "",
  precio: 10.1,
  stock: 3,
  activo: true,
  categoria: { id: 1, nombre: "Alimentos", descripcion: "" },
};
const toy: Producto = { ...food, id: 2, nombre: "Pelota", precio: 20.2 };
const catalog = [food, toy];
const sedes = [
  {
    id: 1,
    nombre: "Miraflores",
    direccion: "Dirección de ejemplo",
    ciudad: "Lima",
    telefono: "999100001",
    activo: true,
  },
];
function ready(cart: CartStore) {
  cart.setSedes(sedes);
  cart.selectSede(1);
  return cart;
}

describe("Carrito de compras", () => {
  beforeEach(() => localStorage.clear());

  it("agrupa productos iguales y calcula totales monetarios sin errores de coma flotante", () => {
    const cart = ready(new CartStore());
    cart.reconcile(catalog);
    cart.add(food);
    cart.add(food);
    cart.add(toy);
    expect(cart.count()).toBe(3);
    expect(cart.lines()).toHaveLength(2);
    expect(cart.total()).toBe(40.4);
    expect(cart.valid()).toBe(true);
  });

  it("rechaza cantidades fraccionarias, no numéricas, negativas y superiores al stock", () => {
    const cart = ready(new CartStore());
    cart.reconcile(catalog);
    cart.add(food);
    for (const value of [0, -1, 1.5, 4, NaN, Infinity])
      expect(cart.setQuantity(food.id, value)).toBe(false);
    expect(cart.quantity(food.id)).toBe(1);
    expect(cart.setQuantity(food.id, 3)).toBe(true);
    expect(cart.add(food)).toBe(false);
    expect(cart.quantity(food.id)).toBe(3);
  });

  it("quita productos y vacía el pedido actualizando cantidades y total", () => {
    const cart = ready(new CartStore());
    cart.reconcile(catalog);
    cart.add(food);
    cart.add(toy);
    cart.remove(food.id);
    expect(cart.total()).toBe(20.2);
    cart.clear();
    expect(cart.count()).toBe(0);
    expect(cart.total()).toBe(0);
    expect(cart.valid()).toBe(false);
  });

  it("conserva el carrito al recargar, pero usa los precios actuales de la API", () => {
    const cart = ready(new CartStore());
    cart.reconcile(catalog);
    cart.add(food);
    cart.setPayment("YAPE");
    const restored = new CartStore();
    restored.setSedes(sedes);
    expect(restored.count()).toBe(1);
    expect(restored.valid()).toBe(false);
    restored.reconcile([{ ...food, precio: 15.5 }]);
    expect(restored.total()).toBe(15.5);
    expect(restored.metodo()).toBe("YAPE");
    expect(restored.payload()).toEqual({
      sedeId: 1,
      metodoPago: "YAPE",
      detalles: [{ idProducto: 1, cantidad: 1 }],
    });
    expect(localStorage.getItem(CART_STORAGE_KEY)).not.toContain("precio");
  });

  it("bloquea la compra si el stock baja o el producto deja de estar disponible", () => {
    const cart = ready(new CartStore());
    cart.reconcile(catalog);
    cart.add(food);
    cart.setQuantity(1, 3);
    cart.reconcile([{ ...food, stock: 1 }]);
    expect(cart.valid()).toBe(false);
    cart.setQuantity(1, 1);
    expect(cart.valid()).toBe(true);
    cart.reconcile([{ ...food, activo: false }]);
    expect(cart.valid()).toBe(false);
    cart.reconcile([]);
    expect(cart.valid()).toBe(false);
    expect(cart.count()).toBe(1);
  });

  it("mantiene la clave al reintentar incluso tras recargar y la cambia al editar el pedido", () => {
    const cart = ready(new CartStore());
    cart.reconcile(catalog);
    cart.add(food);
    const key = cart.checkoutKey();
    expect(cart.checkoutKey()).toBe(key);
    const restored = new CartStore();
    restored.setSedes(sedes);
    restored.reconcile(catalog);
    expect(restored.checkoutKey()).toBe(key);
    restored.setQuantity(1, 2);
    const changed = restored.checkoutKey();
    expect(changed).not.toBe(key);
    restored.setPayment("PLIN");
    expect(restored.checkoutKey()).not.toBe(changed);
  });

  it("se recupera de datos guardados corruptos y descarta entradas inválidas", () => {
    localStorage.setItem(CART_STORAGE_KEY, "not JSON");
    expect(new CartStore().count()).toBe(0);
    localStorage.setItem(
      CART_STORAGE_KEY,
      JSON.stringify({
        version: 1,
        items: [
          { id: 1, cantidad: 2 },
          { id: 1, cantidad: 3 },
          { id: 2, cantidad: -1 },
          { id: "3", cantidad: 1 },
        ],
        metodo: "INVALIDO",
      }),
    );
    const cart = ready(new CartStore());
    expect(cart.count()).toBe(2);
    expect(cart.metodo()).toBe("TARJETA");
  });
});

it("no confirma una compra sin sede activa y cambia la clave cuando cambia la sede", () => {
  localStorage.clear();
  const cart = new CartStore();
  cart.reconcile(catalog);
  cart.add(food);
  expect(cart.valid()).toBe(false);
  cart.setSedes(sedes);
  cart.selectSede(1);
  expect(cart.valid()).toBe(true);
  const key = cart.checkoutKey();
  cart.selectSede(2);
  expect(cart.valid()).toBe(false);
  expect(cart.checkoutKey()).not.toBe(key);
});
