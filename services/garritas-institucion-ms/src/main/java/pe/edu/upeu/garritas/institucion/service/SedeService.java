package pe.edu.upeu.garritas.institucion.service;

import java.util.List;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import pe.edu.upeu.garritas.institucion.dto.SedeRequest;
import pe.edu.upeu.garritas.institucion.dto.SedeResponse;
import pe.edu.upeu.garritas.institucion.entity.Sede;
import pe.edu.upeu.garritas.institucion.exception.ResourceNotFoundException;
import pe.edu.upeu.garritas.institucion.mapper.SedeMapper;
import pe.edu.upeu.garritas.institucion.repository.SedeRepository;

@org.springframework.transaction.annotation.Transactional
@Service
@RequiredArgsConstructor
public class SedeService {

  private final SedeRepository sedeRepository;
  private final SedeMapper sedeMapper;

  public List<SedeResponse> listar() {
    return sedeRepository.findAll().stream()
        .filter(s -> pe.edu.upeu.garritas.common.CurrentUser.admin() || s.getActivo())
        .sorted(java.util.Comparator.comparing(Sede::getCiudad).thenComparing(Sede::getNombre))
        .map(sedeMapper::toResponse)
        .toList();
  }

  public SedeResponse obtener(Long id) {
    Sede sede = buscarOFallar(id);
    if (!sede.getActivo() && !pe.edu.upeu.garritas.common.CurrentUser.admin())
      throw new org.springframework.web.server.ResponseStatusException(
          org.springframework.http.HttpStatus.NOT_FOUND, "Sede no disponible");
    return sedeMapper.toResponse(sede);
  }

  public SedeResponse crear(SedeRequest request) {
    Sede sede = sedeMapper.toEntity(request);
    return sedeMapper.toResponse(sedeRepository.save(sede));
  }

  public SedeResponse actualizar(Long id, SedeRequest request) {
    Sede sede = buscarOFallar(id);
    sede.setNombre(request.getNombre());
    sede.setDireccion(request.getDireccion());
    sede.setCiudad(request.getCiudad());
    sede.setTelefono(request.getTelefono());
    sede.setActivo(request.getActivo());
    return sedeMapper.toResponse(sedeRepository.save(sede));
  }

  public void eliminar(Long id) {
    Sede sede = buscarOFallar(id);
    sede.setActivo(false);
    sedeRepository.save(sede);
  }

  private Sede buscarOFallar(Long id) {
    return sedeRepository
        .findById(id)
        .orElseThrow(() -> new ResourceNotFoundException("Sede no encontrada: " + id));
  }
}
