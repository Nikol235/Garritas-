package pe.edu.upeu.garritas.envio.service;

import java.util.*;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.server.ResponseStatusException;
import pe.edu.upeu.garritas.common.CurrentUser;
import pe.edu.upeu.garritas.envio.dto.*;
import pe.edu.upeu.garritas.envio.entity.*;
import pe.edu.upeu.garritas.envio.repository.*;

@Service
@RequiredArgsConstructor
@Transactional
public class LogisticaService {
  private final TransportistaRepository transportistas;
  private final ZonaRepository zonas;
  private final CoberturaRepository coberturas;

  public List<TransportistaResponse> transportistas() {
    return transportistas.findAll().stream()
        .filter(t -> CurrentUser.admin() || t.getActivo())
        .sorted(Comparator.comparing(Transportista::getNombre))
        .map(this::responseTransportista)
        .toList();
  }

  public List<ZonaResponse> zonas() {
    return zonas.findAll().stream()
        .filter(z -> CurrentUser.admin() || z.getActivo())
        .sorted(Comparator.comparing(Zona::getNombre))
        .map(this::responseZona)
        .toList();
  }

  public TransportistaResponse guardarTransportista(Long id, TransportistaRequest r) {
    Transportista t = id == null ? new Transportista() : transportista(id);
    t.setNombre(r.nombre().strip());
    t.setTelefono(r.telefono());
    t.setActivo(r.activo());
    return responseTransportista(transportistas.saveAndFlush(t));
  }

  public ZonaResponse guardarZona(Long id, ZonaRequest r) {
    Zona z = id == null ? new Zona() : zona(id);
    z.setNombre(r.nombre().strip());
    z.setCiudad(r.ciudad().strip());
    z.setActivo(r.activo());
    return responseZona(zonas.saveAndFlush(z));
  }

  public void borrarTransportista(Long id) {
    transportista(id).setActivo(false);
  }

  public void borrarZona(Long id) {
    zona(id).setActivo(false);
  }

  public List<CoberturaResponse> coberturas() {
    return coberturas.findAll().stream()
        .map(this::response)
        .filter(c -> CurrentUser.admin() || c.activo())
        .toList();
  }

  public CoberturaResponse cobertura(Long t, Long z) {
    CoberturaResponse c =
        response(
            coberturas
                .findByTransportistaIdAndZonaId(t, z)
                .orElseThrow(() -> error(404, "Sin cobertura para esa zona")));
    if (!c.activo()) throw error(409, "Cobertura no disponible");
    return c;
  }

  public CoberturaResponse guardarCobertura(CoberturaRequest r) {
    Transportista t = transportista(r.transportistaId());
    Zona z = zona(r.zonaId());
    if (r.activo() && (!t.getActivo() || !z.getActivo()))
      throw error(409, "Activa primero transportista y zona");
    Cobertura c =
        coberturas.findByTransportistaIdAndZonaId(t.getId(), z.getId()).orElseGet(Cobertura::new);
    c.setTransportista(t);
    c.setZona(z);
    c.setTarifa(r.tarifa());
    c.setDiasEstimados(r.diasEstimados());
    c.setActivo(r.activo());
    return response(coberturas.saveAndFlush(c));
  }

  public void borrarCobertura(Long id) {
    coberturas
        .findById(id)
        .orElseThrow(() -> error(404, "Cobertura no encontrada"))
        .setActivo(false);
  }

  private Transportista transportista(Long id) {
    return transportistas.findById(id).orElseThrow(() -> error(404, "Transportista no encontrado"));
  }

  private Zona zona(Long id) {
    return zonas.findById(id).orElseThrow(() -> error(404, "Zona no encontrada"));
  }

  private CoberturaResponse response(Cobertura c) {
    return new CoberturaResponse(
        c.getId(),
        c.getTransportista().getId(),
        c.getZona().getId(),
        c.getTransportista().getNombre(),
        c.getZona().getNombre(),
        c.getTarifa(),
        c.getDiasEstimados(),
        c.getActivo() && c.getTransportista().getActivo() && c.getZona().getActivo());
  }

  private ResponseStatusException error(int s, String m) {
    return new ResponseStatusException(HttpStatus.valueOf(s), m);
  }

  private TransportistaResponse responseTransportista(Transportista p) {
    return new TransportistaResponse(p.getId(), p.getNombre(), p.getTelefono(), p.getActivo());
  }

  private ZonaResponse responseZona(Zona p) {
    return new ZonaResponse(p.getId(), p.getNombre(), p.getCiudad(), p.getActivo());
  }
}
