import { Injectable, isDevMode } from '@angular/core';
export interface RuntimeConfig {apiUrl:string;keycloakUrl:string;realm:string;clientId:string;}
@Injectable({providedIn:'root'})
export class Config {
  value!:RuntimeConfig;
  async load(){
    const file=isDevMode() ? '/config.dev.json' : '/config.json';
    const response=await fetch(file);
    if(!response.ok)throw new Error('No se pudo cargar la configuración');
    this.value=await response.json();
  }
}
