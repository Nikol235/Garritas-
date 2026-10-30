package pe.edu.upeu.garritas.envio.controller;

import jakarta.validation.Valid;
import java.util.*;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;
import pe.edu.upeu.garritas.envio.dto.*;
import pe.edu.upeu.garritas.envio.entity.*;
import pe.edu.upeu.garritas.envio.service.LogisticaService;

@RestController
@RequestMapping("/api/v1")
@RequiredArgsConstructor
public class LogisticaController {
  private final LogisticaService service;

  @GetMapping("/transportistas")
  public List<TransportistaResponse> transportistas() {
    return service.transportistas();
  }

  @PostMapping("/transportistas")
  @ResponseStatus(HttpStatus.CREATED)
  public TransportistaResponse crearT(@Valid @RequestBody TransportistaRequest r) {
    return service.guardarTransportista(null, r);
  }

  @PutMapping("/transportistas/{id}")
  public TransportistaResponse editarT(
      @PathVariable Long id, @Valid @RequestBody TransportistaRequest r) {
    return service.guardarTransportista(id, r);
  }

  @DeleteMapping("/transportistas/{id}")
  @ResponseStatus(HttpStatus.NO_CONTENT)
  public void borrarT(@PathVariable Long id) {
    service.borrarTransportista(id);
  }

  @GetMapping("/zonas")
  public List<ZonaResponse> zonas() {
    return service.zonas();
  }

  @PostMapping("/zonas")
  @ResponseStatus(HttpStatus.CREATED)
  public ZonaResponse crearZ(@Valid @RequestBody ZonaRequest r) {
    return service.guardarZona(null, r);
  }

  @PutMapping("/zonas/{id}")
  public ZonaResponse editarZ(@PathVariable Long id, @Valid @RequestBody ZonaRequest r) {
    return service.guardarZona(id, r);
  }

  @DeleteMapping("/zonas/{id}")
  @ResponseStatus(HttpStatus.NO_CONTENT)
  public void borrarZ(@PathVariable Long id) {
    service.borrarZona(id);
  }

  @GetMapping("/coberturas")
  public List<CoberturaResponse> coberturas() {
    return service.coberturas();
  }

  @PutMapping("/coberturas")
  public CoberturaResponse guardar(@Valid @RequestBody CoberturaRequest r) {
    return service.guardarCobertura(r);
  }

  @DeleteMapping("/coberturas/{id}")
  @ResponseStatus(HttpStatus.NO_CONTENT)
  public void borrarC(@PathVariable Long id) {
    service.borrarCobertura(id);
  }

  @GetMapping("/transportistas/{t}/zonas/{z}")
  public CoberturaResponse cobertura(@PathVariable Long t, @PathVariable Long z) {
    return service.cobertura(t, z);
  }
}
