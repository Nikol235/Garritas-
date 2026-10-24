package pe.edu.upeu.garritas.common;

import org.springframework.dao.DataIntegrityViolationException;
import org.springframework.dao.OptimisticLockingFailureException;
import org.springframework.http.HttpStatus;
import org.springframework.http.ProblemDetail;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;
import org.springframework.web.server.ResponseStatusException;

@RestControllerAdvice
public class DomainErrors {
  @ExceptionHandler(ResponseStatusException.class)
  ProblemDetail status(ResponseStatusException ex) {
    return ProblemDetail.forStatusAndDetail(
        ex.getStatusCode(),
        ex.getReason() == null ? "No se pudo completar la operación" : ex.getReason());
  }

  @ExceptionHandler({
    DataIntegrityViolationException.class,
    OptimisticLockingFailureException.class
  })
  ProblemDetail conflict(Exception ex) {
    return ProblemDetail.forStatusAndDetail(
        HttpStatus.CONFLICT,
        "El registro ya existe, está relacionado con otros datos o cambió durante la operación");
  }

  @ExceptionHandler(MethodArgumentNotValidException.class)
  ProblemDetail invalid(MethodArgumentNotValidException ex) {
    String message =
        ex.getBindingResult().getFieldErrors().stream()
            .map(e -> e.getField() + ": " + e.getDefaultMessage())
            .findFirst()
            .orElse("Revisa los datos enviados");
    return ProblemDetail.forStatusAndDetail(HttpStatus.BAD_REQUEST, message);
  }
}
