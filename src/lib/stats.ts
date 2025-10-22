export type Num = number;
const round01=(x:Num)=>Math.round(x*10)/10;
export function mean(xs:Num[]):Num{ const n=xs.length; if(!n) return NaN; return xs.reduce((a,b)=>a+b,0)/n; }
export function sd(xs:Num[]):Num{ const m=mean(xs); if(!isFinite(m)) return NaN; const v=mean(xs.map(x=>(x-m)**2)); return Math.sqrt(v); }
export function cvp(xs:Num[]):Num{ const m=mean(xs); const s=sd(xs); return m===0?NaN:round01(100*s/m); }
export function waasbProxy(xs:Num[]):Num{ const c=cvp(xs); if(!isFinite(c)||c<=0) return 100; return round01(Math.min(100, Math.max(0, 10000/c))); }
export function summarize(xs:Num[]){ const M=round01(mean(xs)); const S=round01(sd(xs)); const C=cvp(xs); const W=waasbProxy(xs); return {mean:M, sd:S, cvp:C, waasb_proxy:W}; }
