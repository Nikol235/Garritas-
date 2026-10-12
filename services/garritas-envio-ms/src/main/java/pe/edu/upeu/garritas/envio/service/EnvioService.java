package pe.edu.upeu.garritas.envio.service;

import pe.edu.upeu.garritas.envio.dto.EnvioRequest;
import pe.edu.upeu.garritas.envio.dto.EnvioResponse;
import pe.edu.upeu.garritas.envio.entity.EstadoEnvio;
import pe.edu.upeu.garritas.envio.entity.Envio;
import pe.edu.upeu.garritas.envio.exception.ResourceNotFoundException;
import pe.edu.upeu.garritas.envio.mapper.EnvioMapper;
import pe.edu.upeu.garritas.envio.repository.EnvioRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.time.Instant;
import java.util.List;

@Service
@RequiredArgsConstructor
public class EnvioService {

    private final EnvioRepository envioRepository;
    private final EnvioMapper envioMapper;

    public List<EnvioResponse> listar() {
        return envioRepository.findAll().stream()
                .map(envioMapper::toResponse)
                .toList();
    }

    public EnvioResponse obtener(Long id) {
        return envioMapper.toResponse(buscarOFallar(id));
    }

    public EnvioResponse crear(EnvioRequest request) {
        Envio envio = envioMapper.toEntity(request);
        return envioMapper.toResponse(envioRepository.save(envio));
    }

    public EnvioResponse marcarEnTransito(Long id) {
        Envio envio = buscarOFallar(id);
        envio.setEstado(EstadoEnvio.EN_TRANSITO);
        return envioMapper.toResponse(envioRepository.save(envio));
    }

    public EnvioResponse marcarEntregado(Long id) {
        Envio envio = buscarOFallar(id);
        envio.setEstado(EstadoEnvio.ENTREGADO);
        return envioMapper.toResponse(envioRepository.save(envio));
    }

    public EnvioResponse cancelar(Long id) {
        Envio envio = buscarOFallar(id);
        envio.setEstado(EstadoEnvio.CANCELADO);
        return envioMapper.toResponse(envioRepository.save(envio));
    }

    private Envio buscarOFallar(Long id) {
        return envioRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Envio no encontrado: " + id));
    }
}
