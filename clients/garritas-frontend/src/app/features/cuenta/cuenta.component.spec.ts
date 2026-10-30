import { TestBed } from "@angular/core/testing";
import { provideHttpClient } from "@angular/common/http";
import {
  provideHttpClientTesting,
  HttpTestingController,
} from "@angular/common/http/testing";
import { CuentaComponent } from "./cuenta.component";
import { Config } from "../../core/config";
import { describe, it, expect, afterEach } from "vitest";

describe("Cuenta: carga del perfil antes de editar", () => {
  afterEach(() => TestBed.inject(HttpTestingController).verify());
  function setup() {
    TestBed.configureTestingModule({
      imports: [CuentaComponent],
      providers: [
        provideHttpClient(),
        provideHttpClientTesting(),
        { provide: Config, useValue: { value: { apiUrl: "/api/v1" } } },
      ],
    });
    const fixture = TestBed.createComponent(CuentaComponent);
    fixture.detectChanges();
    return { fixture, http: TestBed.inject(HttpTestingController) };
  }
  it("no permite editar mientras una respuesta tardía pueda reemplazar los campos", async () => {
    const { fixture, http } = setup();
    expect(
      fixture.nativeElement.querySelector('input[name="email"]'),
    ).toBeNull();
    http
      .expectOne("/api/v1/usuarios/me")
      .flush({ id: 1, nombre: "Ana", email: "ana@example.test" });
    http.expectOne("/api/v1/usuarios/me/mascotas").flush([]);
    fixture.detectChanges();
    await fixture.whenStable();
    expect(
      fixture.nativeElement.querySelector('input[name="email"]').value,
    ).toBe("ana@example.test");
    fixture.componentInstance.model.email = "nuevo@example.test";
    fixture.componentInstance.save();
    const save = http.expectOne("/api/v1/usuarios/me");
    expect(save.request.method).toBe("PUT");
    expect(save.request.body.email).toBe("nuevo@example.test");
    save.flush({ id: 1, nombre: "Ana", email: "nuevo@example.test" });
    expect(fixture.componentInstance.guardado()).toBe(false);
    http
      .expectOne("/api/v1/usuarios/me")
      .flush({ id: 1, nombre: "Ana", email: "nuevo@example.test" });
    expect(fixture.componentInstance.guardado()).toBe(true);
    http.expectOne("/api/v1/usuarios/me/mascotas").flush([]);
  });
  it("habilita el formulario vacío cuando todavía no existe perfil", async () => {
    const { fixture, http } = setup();
    http
      .expectOne("/api/v1/usuarios/me")
      .flush({}, { status: 404, statusText: "Not Found" });
    fixture.detectChanges();
    await fixture.whenStable();
    expect(
      fixture.nativeElement.querySelector('input[name="email"]'),
    ).not.toBeNull();
    expect(fixture.componentInstance.error()).toBe("");
  });
  it("no confirma un perfil si el servidor rechaza el correo", () => {
    const { fixture, http } = setup();
    http
      .expectOne("/api/v1/usuarios/me")
      .flush({}, { status: 404, statusText: "Not Found" });
    fixture.componentInstance.model = {
      nombre: "Ana",
      email: "ocupado@example.test",
      telefono: "",
      direccion: "",
    };
    fixture.componentInstance.save();
    http
      .expectOne("/api/v1/usuarios/me")
      .flush(
        { detail: "Ese correo ya está registrado en otro perfil." },
        { status: 409, statusText: "Conflict" },
      );
    expect(fixture.componentInstance.guardado()).toBe(false);
    expect(fixture.componentInstance.error()).toContain("otro perfil");
    expect(fixture.componentInstance.message()).toBe("");
    expect(fixture.componentInstance.busy()).toBe(false);
  });
  it("envía días o meses explícitos y conserva la edad ingresada", () => {
    const { fixture, http } = setup();
    http
      .expectOne("/api/v1/usuarios/me")
      .flush({ id: 1, nombre: "Ana", email: "ana@example.test" });
    http.expectOne("/api/v1/usuarios/me/mascotas").flush([]);
    fixture.componentInstance.pet = {
      nombre: "Luna",
      especie: "Gato",
      raza: "Criolla",
      edad: 45,
      edadUnidad: "DIAS",
    };
    fixture.componentInstance.savePet();
    const request = http.expectOne("/api/v1/usuarios/me/mascotas");
    expect(request.request.body.edad).toBe(45);
    expect(request.request.body.edadUnidad).toBe("DIAS");
    request.flush({ id: 1, nombre: "Luna", edad: 45, edadUnidad: "DIAS" });
    http
      .expectOne("/api/v1/usuarios/me/mascotas")
      .flush([{ id: 1, nombre: "Luna", edad: 45, edadUnidad: "DIAS" }]);
    expect(fixture.componentInstance.mascotas()[0].edadUnidad).toBe("DIAS");
  });
});
