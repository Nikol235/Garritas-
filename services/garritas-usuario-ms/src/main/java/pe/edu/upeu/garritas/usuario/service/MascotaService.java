package pe.edu.upeu.garritas.usuario.service;

import pe.edu.upeu.garritas.usuario.dto.MascotaRequest;
import pe.edu.upeu.garritas.usuario.dto.MascotaResponse;
import pe.edu.upeu.garritas.usuario.entity.Mascota;
import pe.edu.upeu.garritas.usuario.exception.ResourceNotFoundException;
import pe.edu.upeu.garritas.usuario.mapper.MascotaMapper;
import pe.edu.upeu.garritas.usuario.repository.MascotaRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
@RequiredArgsConstructor
public class MascotaService {

    private final MascotaRepository mascotaRepository;
    private final MascotaMapper mascotaMapper;
    private final UsuarioService usuarioService;

    public List<MascotaResponse> listarPorUsuario(Long usuarioId) {
        return mascotaRepository.findByUsuarioId(usuarioId).stream()
                .map(mascotaMapper::toResponse)
                .toList();
    }

    public MascotaResponse crear(Long usuarioId, MascotaRequest request) {
        Mascota mascota = mascotaMapper.toEntity(request);
        mascota.setUsuario(usuarioService.buscarOFallar(usuarioId));
        return mascotaMapper.toResponse(mascotaRepository.save(mascota));
    }

    public MascotaResponse actualizar(Long id, MascotaRequest request) {
        Mascota mascota = buscarOFallar(id);
        mascota.setNombre(request.getNombre());
        mascota.setEspecie(request.getEspecie());
        mascota.setRaza(request.getRaza());
        mascota.setEdad(request.getEdad());
        return mascotaMapper.toResponse(mascotaRepository.save(mascota));
    }

    public void eliminar(Long id) {
        mascotaRepository.delete(buscarOFallar(id));
    }

    private Mascota buscarOFallar(Long id) {
        return mascotaRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Mascota no encontrada: " + id));
    }
}
