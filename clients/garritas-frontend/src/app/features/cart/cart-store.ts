import { Injectable, computed, signal } from "@angular/core";
import { Sede } from "../../core/domain-api";
import { Producto } from "../../core/api";

export interface CartEntry {
  id: number;
  cantidad: number;
}
export interface CartLine extends CartEntry {
  producto: Producto | undefined;
  disponible: boolean;
  subtotal: number;
}
export const CART_STORAGE_KEY = "garritas-cart-v1";
const METHODS = ["TARJETA", "YAPE", "PLIN", "TRANSFERENCIA"];

@Injectable({ providedIn: "root" })
export class CartStore {
  private readonly items = signal<CartEntry[]>([]);
  private readonly catalog = signal<Producto[]>([]);
  private readonly loaded = signal(false);
  private readonly payment = signal("TARJETA");
  readonly sedes = signal<Sede[]>([]);
  private readonly selectedSede = signal(0);
  readonly sedeId = this.selectedSede.asReadonly();
  private request: { key: string; signature: string } | undefined;
  readonly metodo = this.payment.asReadonly();
  readonly entries = this.items.asReadonly();
  readonly count = computed(() =>
    this.items().reduce((total, item) => total + item.cantidad, 0),
  );
  readonly lines = computed<CartLine[]>(() =>
    this.items().map((item) => {
      const producto = this.catalog().find((p) => p.id === item.id);
      const disponible =
        this.loaded() &&
        !!producto?.activo &&
        item.cantidad <= (producto?.stock ?? 0);
      return {
        ...item,
        producto,
        disponible,
        subtotal: producto
          ? (Math.round(producto.precio * 100) * item.cantidad) / 100
          : 0,
      };
    }),
  );
  readonly total = computed(
    () =>
      this.lines().reduce(
        (sum, line) => sum + Math.round(line.subtotal * 100),
        0,
      ) / 100,
  );
  readonly valid = computed(
    () =>
      this.loaded() &&
      this.sedes().some((s) => s.id === this.sedeId() && s.activo) &&
      this.lines().length > 0 &&
      this.total() > 0 &&
      this.lines().every((l) => l.disponible),
  );

  constructor() {
    this.restore();
  }

  reconcile(productos: Producto[]) {
    this.catalog.set(productos);
    this.loaded.set(true);
  }

  setSedes(sedes: Sede[]) {
    this.sedes.set(sedes);
  }
  selectSede(id: number) {
    this.selectedSede.set(id);
    this.persist();
  }

  add(producto: Producto): boolean {
    if (!producto.activo || producto.stock < 1) return false;
    const current =
      this.items().find((i) => i.id === producto.id)?.cantidad ?? 0;
    if (current >= producto.stock) return false;
    this.set(producto.id, current + 1);
    return true;
  }

  quantity(id: number): number {
    return this.items().find((i) => i.id === id)?.cantidad ?? 0;
  }

  setQuantity(id: number, value: number): boolean {
    const producto = this.catalog().find((p) => p.id === id);
    if (
      !Number.isFinite(value) ||
      !Number.isInteger(value) ||
      value < 1 ||
      !producto?.activo ||
      value > producto.stock
    )
      return false;
    this.set(id, value);
    return true;
  }

  remove(id: number) {
    this.items.update((items) => items.filter((i) => i.id !== id));
    this.persist();
  }
  clear() {
    this.items.set([]);
    this.request = undefined;
    this.persist();
  }
  setPayment(method: string) {
    if (METHODS.includes(method)) {
      this.payment.set(method);
      this.persist();
    }
  }

  payload() {
    return {
      sedeId: this.sedeId(),
      metodoPago: this.metodo(),
      detalles: this.items()
        .map((i) => ({ idProducto: i.id, cantidad: i.cantidad }))
        .sort((a, b) => a.idProducto - b.idProducto),
    };
  }

  checkoutKey(): string {
    const signature = JSON.stringify(this.payload());
    if (this.request?.signature !== signature)
      this.request = { key: crypto.randomUUID(), signature };
    this.persist();
    return this.request!.key;
  }

  private set(id: number, cantidad: number) {
    this.items.update((items) =>
      [...items.filter((i) => i.id !== id), { id, cantidad }].sort(
        (a, b) => a.id - b.id,
      ),
    );
    this.persist();
  }

  private persist() {
    // Product IDs/quantities only. Prices and identity always come from the API/JWT.
    try {
      localStorage.setItem(
        CART_STORAGE_KEY,
        JSON.stringify({
          version: 1,
          items: this.items(),
          sedeId: this.sedeId(),
          metodo: this.metodo(),
          request: this.request,
        }),
      );
    } catch {
      /* Private browsing or full storage: the in-memory cart remains usable. */
    }
  }

  private restore() {
    try {
      const saved = JSON.parse(
        localStorage.getItem(CART_STORAGE_KEY) ?? "null",
      );
      if (saved?.version !== 1 || !Array.isArray(saved.items)) return;
      const entries: CartEntry[] = [];
      for (const item of saved.items.slice(0, 50)) {
        if (
          Number.isSafeInteger(item?.id) &&
          item.id > 0 &&
          Number.isInteger(item.cantidad) &&
          item.cantidad > 0 &&
          item.cantidad <= 10000 &&
          !entries.some((i) => i.id === item.id)
        )
          entries.push({ id: item.id, cantidad: item.cantidad });
      }
      this.items.set(entries);
      if (Number.isSafeInteger(saved.sedeId) && saved.sedeId > 0)
        this.selectedSede.set(saved.sedeId);
      if (METHODS.includes(saved.metodo)) this.payment.set(saved.metodo);
      if (
        typeof saved.request?.key === "string" &&
        /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(
          saved.request.key,
        ) &&
        typeof saved.request.signature === "string"
      )
        this.request = saved.request;
    } catch {
      /* A corrupt saved cart must not prevent the shop from opening. */
    }
  }
}
