import React, {useEffect, useState} from 'react'

export default function App(){
  const [metrics, setMetrics] = useState(null)
  const [reports, setReports] = useState([])
  const [error, setError] = useState(null)
  useEffect(()=>{
    fetch('/api/metrics')
      .then(r=> r.ok ? r.json() : Promise.reject(new Error('metrics http '+r.status)))
      .then(setMetrics)
      .catch(e=>{ console.error(e); setError('Failed to load metrics') })
    fetch('/api/reports')
      .then(r=> r.ok ? r.json() : Promise.reject(new Error('reports http '+r.status)))
      .then(data=> setReports(Array.isArray(data) ? data : (data.reports || [])))
      .catch(e=>{ console.error(e); setError('Failed to load reports') })
  },[])
  return (
    <div style={{padding:20,fontFamily:'system-ui,Segoe UI,Roboto,Arial'}}>
      <h1>SecureWatch Dashboard</h1>
      {error && <p style={{color:'#b00'}}>{error}</p>}
      {metrics ?
        <div>
          <p><strong>Last run:</strong> {metrics.last_run || 'N/A'}</p>
          <p><strong>Total events:</strong> {metrics.total_events}</p>
          <h3>By Severity</h3>
          <ul>
            {Object.entries(metrics.by_severity).map(([sev,count])=> (
              <li key={sev}>Severity {sev}: {count}</li>
            ))}
          </ul>
        </div>
        : <p>Loading metrics…</p>
      }
      <h2>Reports</h2>
      <ul>
        {reports.map(r=> {
          const id = r.report_id || r.id
          const total = r.total || (r.summary && r.summary.total)
          return (
            <li key={id}>{id} — {total} events — <a href={`/api/reports/${id}`} target="_blank" rel="noreferrer">view raw JSON</a></li>
          )
        })}
      </ul>
    </div>
  )
}