package pe.edu.upeu.garritas.envio.controller;

import pe.edu.upeu.garritas.envio.dto.EnvioRequest;
import pe.edu.upeu.garritas.envio.dto.EnvioResponse;
import pe.edu.upeu.garritas.envio.service.EnvioService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/v1/envios")
@RequiredArgsConstructor
public class EnvioController {

    private final EnvioService envioService;

    @GetMapping
    public List<EnvioResponse> listar() {
        return envioService.listar();
    }

    @GetMapping("/{id}")
    public EnvioResponse obtener(@PathVariable Long id) {
        return envioService.obtener(id);
    }

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    public EnvioResponse crear(@Valid @RequestBody EnvioRequest request) {
        return envioService.crear(request);
    }

    @PostMapping("/{id}/en-transito")
    public EnvioResponse marcarEnTransito(@PathVariable Long id) {
        return envioService.marcarEnTransito(id);
    }

    @PostMapping("/{id}/entregado")
    public EnvioResponse marcarEntregado(@PathVariable Long id) {
        return envioService.marcarEntregado(id);
    }

    @PostMapping("/{id}/cancelar")
    public EnvioResponse cancelar(@PathVariable Long id) {
        return envioService.cancelar(id);
    }
}
