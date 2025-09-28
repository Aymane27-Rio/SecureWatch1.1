import React, {useEffect, useState} from 'react'

export default function App(){
  const [metrics, setMetrics] = useState(null)
  const [reports, setReports] = useState([])
  useEffect(()=>{
    fetch('http://localhost:8000/api/metrics').then(r=>r.json()).then(setMetrics).catch(e=>console.error(e))
    fetch('http://localhost:8000/api/reports').then(r=>r.json()).then(setReports).catch(e=>console.error(e))
  },[])
  return (
    <div style={{padding:20,fontFamily:'system-ui,Segoe UI,Roboto,Arial'}}>
      <h1>SecureWatch Dashboard</h1>
      {metrics ?
        <div>
          <p><strong>Last run:</strong> {metrics.last_run || 'N/A'}</p>
          <p><strong>Total events:</strong> {metrics.total_events}</p>
          <h3>By Severity</h3>
          <ul>
            {Object.entries(metrics.by_severity).map(([sev,count])=>(
              <li key={sev}>Severity {sev}: {count}</li>
            ))}
          </ul>
        </div>
        : <p>Loading metrics…</p>
      }
      <h2>Reports</h2>
      <ul>
        {reports.map(r=>(
          <li key={r.id}>{r.id} — {r.summary.total} events — <a href={`http://localhost:8000/api/reports/${r.id}`} target="_blank" rel="noreferrer">view raw JSON</a></li>
        ))}
      </ul>
    </div>
  )
}