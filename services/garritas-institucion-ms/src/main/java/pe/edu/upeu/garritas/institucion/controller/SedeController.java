package pe.edu.upeu.garritas.institucion.controller;

import pe.edu.upeu.garritas.institucion.dto.SedeRequest;
import pe.edu.upeu.garritas.institucion.dto.SedeResponse;
import pe.edu.upeu.garritas.institucion.service.SedeService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/v1/sedes")
@RequiredArgsConstructor
public class SedeController {

    private final SedeService sedeService;

    @GetMapping
    public List<SedeResponse> listar() {
        return sedeService.listar();
    }

    @GetMapping("/{id}")
    public SedeResponse obtener(@PathVariable Long id) {
        return sedeService.obtener(id);
    }

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    public SedeResponse crear(@Valid @RequestBody SedeRequest request) {
        return sedeService.crear(request);
    }

    @PutMapping("/{id}")
    public SedeResponse actualizar(@PathVariable Long id, @Valid @RequestBody SedeRequest request) {
        return sedeService.actualizar(id, request);
    }

    @DeleteMapping("/{id}")
    @ResponseStatus(HttpStatus.NO_CONTENT)
    public void eliminar(@PathVariable Long id) {
        sedeService.eliminar(id);
    }
}
