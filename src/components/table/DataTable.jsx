// TABLE
import React,{useState,useMemo}from'react';
export default function DataTable({rows}){
const[q,setQ]=useState('');
const filtered=useMemo(()=>rows.filter(r=>(r.Hybrid||'').toLowerCase().includes(q.toLowerCase())),[rows,q]);
return(<div><input value={q}onChange={e=>setQ(e.target.value)}placeholder="Поиск"style={{padding:8,width:'100%'}}/>
<div style={{maxHeight:300,overflow:'auto'}}><table style={{width:'100%'}}><thead><tr>
{['Hybrid','Region','Year','Yield'].map(h=><th key={h}>{h}</th>)}</tr></thead><tbody>
{filtered.map((r,i)=><tr key={i}><td>{r.Hybrid}</td><td>{r.Region}</td><td>{r.Year}</td><td>{r.Yield}</td></tr>)}
</tbody></table></div></div>);
}
