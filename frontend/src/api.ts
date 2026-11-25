export const base=import.meta.env.DEV?'/api':'';
export async function request<T>(path:string,token:string,body?:unknown,method?:string):Promise<T>{
 const r=await fetch(base+path,{method:method??(body===undefined?'GET':'POST'),headers:{'Content-Type':'application/json',...(token?{Authorization:'Bearer '+token}:{})},body:body===undefined?undefined:JSON.stringify(body)});
 const value=await r.json();if(!r.ok)throw new Error(typeof value.detail==='string'?value.detail:JSON.stringify(value.detail));return value as T;
}
export function parseFrame(frame:string):{event:string;data:unknown}|null{const rows=frame.split('\n');const payload=rows.find(x=>x.startsWith('data: '));if(!payload)return null;return {event:rows.find(x=>x.startsWith('event: '))?.slice(7)??'message',data:JSON.parse(payload.slice(6))};}
export function validPreference(key:string,value:string){return /^[a-zA-Z0-9_ -]{1,64}$/.test(key)&&value.trim().length>0&&value.length<=500;}
