package pe.edu.upeu.garritas.pago.service;

import pe.edu.upeu.garritas.pago.dto.PagoRequest;
import pe.edu.upeu.garritas.pago.dto.PagoResponse;
import pe.edu.upeu.garritas.pago.entity.EstadoPago;
import pe.edu.upeu.garritas.pago.entity.Pago;
import pe.edu.upeu.garritas.pago.exception.ResourceNotFoundException;
import pe.edu.upeu.garritas.pago.mapper.PagoMapper;
import pe.edu.upeu.garritas.pago.repository.PagoRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.UUID;

@Service
@RequiredArgsConstructor
public class PagoService {

    private final PagoRepository pagoRepository;
    private final PagoMapper pagoMapper;

    public List<PagoResponse> listar() {
        return pagoRepository.findAll().stream()
                .map(pagoMapper::toResponse)
                .toList();
    }

    public PagoResponse obtener(Long id) {
        return pagoMapper.toResponse(buscarOFallar(id));
    }

    public PagoResponse procesar(PagoRequest request) {
        Pago pago = pagoMapper.toEntity(request);
        pago.setEstado(EstadoPago.APROBADO);
        pago.setReferenciaExterna(UUID.randomUUID().toString());
        return pagoMapper.toResponse(pagoRepository.save(pago));
    }

    public PagoResponse reembolsar(Long id) {
        Pago pago = buscarOFallar(id);
        pago.setEstado(EstadoPago.REEMBOLSADO);
        return pagoMapper.toResponse(pagoRepository.save(pago));
    }

    private Pago buscarOFallar(Long id) {
        return pagoRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Pago no encontrado: " + id));
    }
}
