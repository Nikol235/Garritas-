package pe.edu.upeu.garritas.usuario.controller;

import pe.edu.upeu.garritas.usuario.dto.MascotaRequest;
import pe.edu.upeu.garritas.usuario.dto.MascotaResponse;
import pe.edu.upeu.garritas.usuario.service.MascotaService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/v1/usuarios/{usuarioId}/mascotas")
@RequiredArgsConstructor
public class MascotaController {

    private final MascotaService mascotaService;

    @GetMapping
    public List<MascotaResponse> listar(@PathVariable Long usuarioId) {
        return mascotaService.listarPorUsuario(usuarioId);
    }

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    public MascotaResponse crear(@PathVariable Long usuarioId, @Valid @RequestBody MascotaRequest request) {
        return mascotaService.crear(usuarioId, request);
    }

    @PutMapping("/{id}")
    public MascotaResponse actualizar(@PathVariable Long usuarioId, @PathVariable Long id, @Valid @RequestBody MascotaRequest request) {
        return mascotaService.actualizar(id, request);
    }

    @DeleteMapping("/{id}")
    @ResponseStatus(HttpStatus.NO_CONTENT)
    public void eliminar(@PathVariable Long usuarioId, @PathVariable Long id) {
        mascotaService.eliminar(id);
    }
}
