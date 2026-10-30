import { Injectable, inject, signal } from "@angular/core";
import Keycloak from "keycloak-js";
import { Config } from "./config";

@Injectable({ providedIn: "root" })
export class Auth {
  private readonly config = inject(Config);
  private kc!: Keycloak;
  readonly loggedIn = signal(false);
  readonly name = signal("");
  readonly admin = signal(false);

  async init() {
    await this.config.load();
    const c = this.config.value;
    this.kc = new Keycloak({
      url: c.keycloakUrl,
      realm: c.realm,
      clientId: c.clientId,
    });
    this.kc.onAuthSuccess = () => this.sync();
    this.kc.onAuthRefreshSuccess = () => this.sync();
    this.kc.onAuthLogout = () => this.sync();
    this.kc.onTokenExpired = () => {
      this.token().catch(() => this.kc.clearToken());
    };
    await this.kc.init({
      onLoad: "check-sso",
      pkceMethod: "S256",
      checkLoginIframe: false,
      responseMode: "query",
      redirectUri: location.origin + "/",
    });
    this.sync();
  }

  private sync() {
    this.loggedIn.set(!!this.kc.authenticated);
    this.name.set(this.kc.tokenParsed?.["preferred_username"] ?? "");
    this.admin.set(this.kc.hasRealmRole("ADMIN"));
  }

  login() {
    return this.kc.login({ redirectUri: location.origin + "/" });
  }

  logout() {
    return this.kc.logout({ redirectUri: location.origin + "/" });
  }

  accountUrl() {
    return `${this.config.value.keycloakUrl}/realms/${this.config.value.realm}/account/#/security/signing-in`;
  }

  manageAccount() {
    if (this.kc) {
      this.kc.accountManagement();
    } else {
      window.open(this.accountUrl(), "_blank");
    }
  }

  async token() {
    if (!this.kc.authenticated) return undefined;
    try {
      await this.kc.updateToken(30);
      return this.kc.token;
    } catch (error) {
      this.kc.clearToken();
      this.sync();
      throw error;
    }
  }
}
