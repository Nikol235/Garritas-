import { HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { from, switchMap } from 'rxjs';
import { Auth } from './auth';
import { Config } from './config';
export const authInterceptor:HttpInterceptorFn=(req,next)=>{
  const config=inject(Config).value;
  if(!req.url.startsWith(config.apiUrl+'/') && req.url!==config.apiUrl)return next(req);
  const auth=inject(Auth);
  return from(auth.token()).pipe(switchMap(token=>next(req.clone({setHeaders:{'X-Trace-ID':crypto.randomUUID(),...(token?{Authorization:'Bearer '+token}:{})}}))));
};
