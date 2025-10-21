// ANALYTICS
import React from'react';
import{BarChart,Bar,XAxis,YAxis,CartesianGrid,Tooltip,ResponsiveContainer}from'recharts';
export default function AnalyticsPanel({rows}){
const data=rows.slice(0,20).map(r=>({Hybrid:r.Hybrid,Yield:r.Yield}));
return(<div><h3>Стабильность по годам</h3>
<ResponsiveContainer width="100%"height={260}>
<BarChart data={data}><CartesianGrid strokeDasharray="3 3"/><XAxis dataKey="Hybrid"/><YAxis/><Tooltip/>
<Bar dataKey="Yield"fill="#4c73c1"/></BarChart></ResponsiveContainer></div>);
}
