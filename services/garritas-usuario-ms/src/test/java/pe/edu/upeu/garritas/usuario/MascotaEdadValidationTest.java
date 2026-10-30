package pe.edu.upeu.garritas.usuario;

import static org.junit.jupiter.api.Assertions.*;

import jakarta.validation.Validation;
import java.math.BigDecimal;
import org.junit.jupiter.api.Test;
import pe.edu.upeu.garritas.usuario.dto.MascotaRequest;
import pe.edu.upeu.garritas.usuario.entity.UnidadEdad;

class MascotaEdadValidationTest {
  @Test
  void rejectsFractionalAgeBeforeMappingToInteger() {
    try (var factory = Validation.buildDefaultValidatorFactory()) {
      var validator = factory.getValidator();
      MascotaRequest r = new MascotaRequest();
      r.setNombre("Luna");
      r.setEspecie("Gato");
      r.setEdadUnidad(UnidadEdad.DIAS);
      r.setEdad(new BigDecimal("1.5"));
      assertFalse(validator.validate(r).isEmpty());
      r.setEdad(new BigDecimal("45"));
      assertTrue(validator.validate(r).isEmpty());
      r.setEdadUnidad(UnidadEdad.MESES);
      r.setEdad(new BigDecimal("2"));
      assertTrue(validator.validate(r).isEmpty());
    }
  }
}
