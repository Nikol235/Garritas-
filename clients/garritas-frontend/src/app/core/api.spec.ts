import { describe,it,expect } from 'vitest';
import { pending } from './api';
describe('Estados de consistencia eventual',()=>{
 it('sigue consultando hasta confirmar pago o compensación',()=>{for(const state of ['PENDIENTE_STOCK','PENDIENTE_PAGO','COMPENSANDO'])expect(pending(state)).toBe(true);for(const state of ['PAGADA','CANCELADA'])expect(pending(state)).toBe(false);});
});
