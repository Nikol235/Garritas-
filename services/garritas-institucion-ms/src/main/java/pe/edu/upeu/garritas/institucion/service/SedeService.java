package pe.edu.upeu.garritas.institucion.service;

import pe.edu.upeu.garritas.institucion.dto.SedeRequest;
import pe.edu.upeu.garritas.institucion.dto.SedeResponse;
import pe.edu.upeu.garritas.institucion.entity.Sede;
import pe.edu.upeu.garritas.institucion.exception.ResourceNotFoundException;
import pe.edu.upeu.garritas.institucion.mapper.SedeMapper;
import pe.edu.upeu.garritas.institucion.repository.SedeRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
@RequiredArgsConstructor
public class SedeService {

    private final SedeRepository sedeRepository;
    private final SedeMapper sedeMapper;

    public List<SedeResponse> listar() {
        return sedeRepository.findAll().stream()
                .map(sedeMapper::toResponse)
                .toList();
    }

    public SedeResponse obtener(Long id) {
        return sedeMapper.toResponse(buscarOFallar(id));
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
        sedeRepository.delete(buscarOFallar(id));
    }

    private Sede buscarOFallar(Long id) {
        return sedeRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Sede no encontrada: " + id));
    }
}
