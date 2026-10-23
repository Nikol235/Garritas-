import { Component, DestroyRef, inject, signal } from '@angular/core';
import { CurrencyPipe, DatePipe } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { timer, EMPTY, exhaustMap, catchError } from 'rxjs';
import { HttpErrorResponse } from '@angular/common/http';
import { Auth } from './core/auth';
import { Api, Categoria, Producto, Venta, Pago, pending } from './core/api';
@Component({selector:'app-root',imports:[FormsModule,CurrencyPipe,DatePipe],templateUrl:'./app.html'})
export class App {
  readonly auth=inject(Auth);private readonly api=inject(Api);private readonly destroy=inject(DestroyRef);
  readonly productos=signal<Producto[]>([]);readonly categorias=signal<Categoria[]>([]);readonly ventas=signal<Venta[]>([]);
  readonly pagos=signal<Record<number,Pago>>({});readonly error=signal('');readonly busy=signal(false);readonly view=signal('catalogo');
  readonly cart=signal<Record<number,number>>({});readonly pending=pending;
  metodo='TARJETA';nombre='';descripcion='';categoriaId:number|undefined;
  private key=crypto.randomUUID();private fingerprint='';
  constructor(){
    this.refreshCatalogo();
    if(this.auth.loggedIn())this.refreshVentas();
    timer(3000,3000).pipe(exhaustMap(()=>{
      if(!this.auth.loggedIn() || !this.ventas().some(v=>pending(v.estado)))return EMPTY;
      return this.api.ventas().pipe(catchError(e=>{this.fail(e);return EMPTY;}));
    }),takeUntilDestroyed(this.destroy)).subscribe(ventas=>{this.ventas.set(ventas);if(!ventas.some(v=>pending(v.estado)))this.refreshCatalogo();});
  }
  refreshCatalogo(){this.api.productos().subscribe({next:p=>this.productos.set(p),error:e=>this.fail(e)});this.api.categorias().subscribe({next:c=>this.categorias.set(c),error:e=>this.fail(e)});}
  refreshVentas(){this.api.ventas().subscribe({next:v=>this.ventas.set(v),error:e=>this.fail(e)});}
  cantidad(p:Producto){return this.cart()[p.id]??0;}
  change(p:Producto,value:number){this.cart.update(c=>({...c,[p.id]:Math.max(0,Math.min(p.stock,Math.trunc(value||0)))}));}
  total(){return this.productos().reduce((s,p)=>s+p.precio*this.cantidad(p),0);}
  checkout(){
    this.error.set('');
    const detalles=Object.entries(this.cart()).filter(([,n])=>n>0).map(([id,cantidad])=>({idProducto:Number(id),cantidad}));
    if(!detalles.length){this.error.set('Selecciona al menos un producto.');return;}
    const body={metodoPago:this.metodo,detalles};const fingerprint=JSON.stringify(body);
    if(fingerprint!==this.fingerprint){this.key=crypto.randomUUID();this.fingerprint=fingerprint;}
    this.busy.set(true);
    this.api.crearVenta(body,this.key).subscribe({next:v=>{
      this.busy.set(false);this.cart.set({});this.key=crypto.randomUUID();this.fingerprint='';this.view.set('pedidos');this.refreshVentas();
    },error:e=>{this.busy.set(false);this.fail(e);}});
  }
  consultarPago(id:number){this.api.pago(id).subscribe({next:p=>this.pagos.update(all=>({...all,[id]:p})),error:e=>this.fail(e)});}
  edit(c:Categoria){this.categoriaId=c.id;this.nombre=c.nombre;this.descripcion=c.descripcion??'';}
  save(){this.api.guardarCategoria({nombre:this.nombre,descripcion:this.descripcion},this.categoriaId).subscribe({next:()=>{this.nombre='';this.descripcion='';this.categoriaId=undefined;this.refreshCatalogo();},error:e=>this.fail(e)});}
  remove(c:Categoria){if(confirm('¿Eliminar categoría '+c.nombre+'?'))this.api.borrarCategoria(c.id).subscribe({next:()=>this.refreshCatalogo(),error:e=>this.fail(e)});}
  private fail(e:HttpErrorResponse){this.error.set(e.status===401?'La sesión expiró. Inicia sesión de nuevo.':e.status===403?'No tienes permiso para esta operación.':e.error?.detail??e.error?.message??'No se pudo completar la operación. Inténtalo de nuevo.');}
}
