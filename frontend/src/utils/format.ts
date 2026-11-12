export const number=(x:number|null,d=4)=>x===null?'不可估':x.toFixed(d);export const shortHash=(s:string)=>s.slice(0,16)+'…';
