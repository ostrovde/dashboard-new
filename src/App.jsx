// APPLE_DASHBOARD_UI
import React,{useEffect,useState}from'react';
import'./style/theme.css';
import MetricsBar from'./components/StatsBar';
import MapPanel from'./components/MapPanel';
import HeatmapPanel from'./components/HeatmapPanel';
import AnalyticsPanel from'./components/analytics/AnalyticsPanel';
import DataTable from'./components/table/DataTable';
export default function App(){
const[rows,setRows]=useState([]);
useEffect(()=>{
fetch('/data/yield.csv').then(r=>r.text()).then(t=>{
const [h,...l]=t.trim().split(/\r?\n/);
const c=h.split(',');
setRows(l.map(x=>{
const v=x.split(',');const o={};
c.forEach((k,i)=>o[k]=v[i]);o.Yield=+o.Yield;o.Lat=+o.Lat;o.Lng=+o.Lng;return o;
}));
});
},[]);
return(<div><div className="card"><h1>РАЙАГРО ДАШБОРД</h1></div>
<MetricsBar rows={rows}/>
<div className="card"><MapPanel rows={rows}/></div>
<div className="card"><HeatmapPanel rows={rows}/></div>
<div className="card"><AnalyticsPanel rows={rows}/></div>
<div className="card"><DataTable rows={rows}/></div></div>);
}
