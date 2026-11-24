import {api} from './base.js';
const path='/api/page-turns';
export const pieces=()=>api(path);
export const read=(code,part)=>api(`${path}/${code}/${part}`);
export const write=(code,part,body)=>api(`${path}/${code}/${part}`,part==='events'?'PUT':'POST',body);
