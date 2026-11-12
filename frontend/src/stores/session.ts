import type {User} from '../types/entities';
export function savedUser():User|null {try{return JSON.parse(sessionStorage.getItem('citation-user')||'null')}catch{return null}}
export function saveSession(token:string,user:User){sessionStorage.setItem('citation-token',token);sessionStorage.setItem('citation-user',JSON.stringify(user))}
export function clearSession(){sessionStorage.removeItem('citation-token');sessionStorage.removeItem('citation-user')}
