import { ApplicationConfig, inject, provideAppInitializer, provideBrowserGlobalErrorListeners } from '@angular/core';
import { provideHttpClient, withInterceptors } from '@angular/common/http';
import { Auth } from './core/auth';
import { authInterceptor } from './core/interceptor';
export const appConfig:ApplicationConfig={providers:[provideBrowserGlobalErrorListeners(),provideHttpClient(withInterceptors([authInterceptor])),provideAppInitializer(()=>inject(Auth).init())]};
