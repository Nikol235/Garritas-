import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { provideHttpClientTesting, HttpTestingController } from '@angular/common/http/testing';
import { CuentaComponent } from './cuenta.component';
import { Config } from '../../core/config';
import { describe, it, expect, afterEach } from 'vitest';

describe('Cuenta: carga del perfil antes de editar', () => {
  afterEach(() => TestBed.inject(HttpTestingController).verify());
  function setup() {
    TestBed.configureTestingModule({
      imports: [CuentaComponent],
      providers: [provideHttpClient(), provideHttpClientTesting(),
        { provide: Config, useValue: { value: { apiUrl: '/api/v1' } } }],
    });
    const fixture = TestBed.createComponent(CuentaComponent);
    fixture.detectChanges();
    return { fixture, http: TestBed.inject(HttpTestingController) };
  }
  it('no permite editar mientras una respuesta tardía pueda reemplazar los campos', async () => {
    const { fixture, http } = setup();
    expect(fixture.nativeElement.querySelector('input[name="email"]')).toBeNull();
    http.expectOne('/api/v1/usuarios/me').flush({ id: 1, nombre: 'Ana', email: 'ana@example.test' });
    http.expectOne('/api/v1/usuarios/me/mascotas').flush([]);
    fixture.detectChanges();
    await fixture.whenStable();
    expect(fixture.nativeElement.querySelector('input[name="email"]').value).toBe('ana@example.test');
    fixture.componentInstance.model.email = 'nuevo@example.test';
    fixture.componentInstance.save();
    const save = http.expectOne('/api/v1/usuarios/me');
    expect(save.request.method).toBe('PUT');
    expect(save.request.body.email).toBe('nuevo@example.test');
    save.flush({ id: 1, nombre: 'Ana', email: 'nuevo@example.test' });
    http.expectOne('/api/v1/usuarios/me/mascotas').flush([]);
  });
  it('habilita el formulario vacío cuando todavía no existe perfil', async () => {
    const { fixture, http } = setup();
    http.expectOne('/api/v1/usuarios/me').flush({}, { status: 404, statusText: 'Not Found' });
    fixture.detectChanges();
    await fixture.whenStable();
    expect(fixture.nativeElement.querySelector('input[name="email"]')).not.toBeNull();
    expect(fixture.componentInstance.error()).toBe('');
  });
});
