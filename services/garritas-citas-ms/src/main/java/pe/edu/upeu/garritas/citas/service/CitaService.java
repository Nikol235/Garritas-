package pe.edu.upeu.garritas.citas.service;

import pe.edu.upeu.garritas.citas.dto.CitaRequest;
import pe.edu.upeu.garritas.citas.dto.CitaResponse;
import pe.edu.upeu.garritas.citas.entity.Cita;
import pe.edu.upeu.garritas.citas.entity.EstadoCita;
import pe.edu.upeu.garritas.citas.exception.ResourceNotFoundException;
import pe.edu.upeu.garritas.citas.mapper.CitaMapper;
import pe.edu.upeu.garritas.citas.repository.CitaRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
@RequiredArgsConstructor
public class CitaService {

    private final CitaRepository citaRepository;
    private final CitaMapper citaMapper;

    public List<CitaResponse> listar() {
        return citaRepository.findAll().stream()
                .map(citaMapper::toResponse)
                .toList();
    }

    public CitaResponse obtener(Long id) {
        return citaMapper.toResponse(buscarOFallar(id));
    }

    public CitaResponse crear(CitaRequest request) {
        Cita cita = citaMapper.toEntity(request);
        return citaMapper.toResponse(citaRepository.save(cita));
    }

    public CitaResponse confirmar(Long id) {
        Cita cita = buscarOFallar(id);
        cita.setEstado(EstadoCita.CONFIRMADA);
        return citaMapper.toResponse(citaRepository.save(cita));
    }

    public CitaResponse atender(Long id) {
        Cita cita = buscarOFallar(id);
        cita.setEstado(EstadoCita.ATENDIDA);
        return citaMapper.toResponse(citaRepository.save(cita));
    }

    public CitaResponse cancelar(Long id) {
        Cita cita = buscarOFallar(id);
        cita.setEstado(EstadoCita.CANCELADA);
        return citaMapper.toResponse(citaRepository.save(cita));
    }

    private Cita buscarOFallar(Long id) {
        return citaRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Cita no encontrada: " + id));
    }
}
