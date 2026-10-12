package pe.edu.upeu.garritas.venta.service;

import pe.edu.upeu.garritas.venta.dto.VentaRequest;
import pe.edu.upeu.garritas.venta.dto.VentaResponse;
import pe.edu.upeu.garritas.venta.entity.EstadoVenta;
import pe.edu.upeu.garritas.venta.entity.Venta;
import pe.edu.upeu.garritas.venta.exception.ResourceNotFoundException;
import pe.edu.upeu.garritas.venta.mapper.VentaMapper;
import pe.edu.upeu.garritas.venta.repository.VentaRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
@RequiredArgsConstructor
public class VentaService {

    private final VentaRepository ventaRepository;
    private final VentaMapper ventaMapper;

    public List<VentaResponse> listar() {
        return ventaRepository.findAll().stream()
                .map(ventaMapper::toResponse)
                .toList();
    }

    public VentaResponse obtener(Long id) {
        return ventaMapper.toResponse(buscarOFallar(id));
    }

    public VentaResponse crear(VentaRequest request) {
        Venta venta = ventaMapper.toEntity(request);
        return ventaMapper.toResponse(ventaRepository.save(venta));
    }

    public VentaResponse confirmar(Long id) {
        Venta venta = buscarOFallar(id);
        venta.setEstado(EstadoVenta.CONFIRMADA);
        return ventaMapper.toResponse(ventaRepository.save(venta));
    }

    public VentaResponse cancelar(Long id) {
        Venta venta = buscarOFallar(id);
        venta.setEstado(EstadoVenta.CANCELADA);
        return ventaMapper.toResponse(ventaRepository.save(venta));
    }

    public void eliminar(Long id) {
        ventaRepository.delete(buscarOFallar(id));
    }

    private Venta buscarOFallar(Long id) {
        return ventaRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Venta no encontrada: " + id));
    }
}
