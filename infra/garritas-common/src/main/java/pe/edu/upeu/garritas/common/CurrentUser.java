package pe.edu.upeu.garritas.common;

import org.springframework.security.access.AccessDeniedException;
import org.springframework.security.core.context.SecurityContextHolder;

public final class CurrentUser {
  private CurrentUser() {}

  public static String subject() {
    return SecurityContextHolder.getContext().getAuthentication().getName();
  }

  public static boolean admin() {
    return SecurityContextHolder.getContext().getAuthentication().getAuthorities().stream()
        .anyMatch(a -> a.getAuthority().equals("ROLE_ADMIN"));
  }

  public static void requireOwner(String owner) {
    if (!admin() && !subject().equals(owner))
      throw new AccessDeniedException("El recurso pertenece a otro cliente");
  }
}
