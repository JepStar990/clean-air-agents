import React, { useState } from 'react'
import { fetchCity, analyzeCity } from './api'

export default function App() {
  const [city, setCity] = useState('Johannesburg')
  const [country, setCountry] = useState('ZA')
  const [model, setModel] = useState('llama3.1:latest')
  const [results, setResults] = useState(null)
  const [analysis, setAnalysis] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const run = async (fn) => {
    setLoading(true); setError(null)
    try {
      const data = await fn()
      return data
    } catch (e) {
      setError(String(e))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ padding: 20, maxWidth: 900, margin: '0 auto', fontFamily: 'system-ui' }}>
      <h2>CleanAir Agents — Johannesburg-first (global-ready)</h2>

      <div style={{ display: 'flex', gap: 8, alignItems: 'center', flexWrap: 'wrap' }}>
        <label>City</label>
        <input value={city} onChange={e => setCity(e.target.value)} />
        <label>Country</label>
        <input value={country} onChange={e => setCountry(e.target.value)} style={{ width: 80 }} />
        <label>Model</label>
        <input value={model} onChange={e => setModel(e.target.value)} style={{ width: 180 }} />
        <button
          onClick={async () => {
            const data = await run(() => fetchCity(city, country, 'pm25', 50))
            setResults(data || null)
          }}
        >
          Fetch (OpenAQ v3)
        </button>
        <button
          onClick={async () => {
            const data = await run(() => analyzeCity(city, country, model))
            setAnalysis(data || null)
          }}
        >
          Analyze (LLM)
        </button>
        {loading && <span>Loading…</span>}
        {error && <span style={{ color: 'crimson' }}>{error}</span>}
      </div>

      <h3 style={{ marginTop: 24 }}>OpenAQ results</h3>
      <pre style={{ background: '#f6f8fa', padding: 12, borderRadius: 6, overflowX: 'auto' }}>
        {results ? JSON.stringify(results, null, 2) : 'No results yet.'}
      </pre>

      <h3 style={{ marginTop: 24 }}>Analysis + Policy</h3>
      <pre style={{ background: '#f6f8fa', padding: 12, borderRadius: 6, overflowX: 'auto' }}>
        {analysis ? JSON.stringify(analysis, null, 2) : 'No analysis yet.'}
      </pre>

      <p style={{ marginTop: 12, color: '#555' }}>
        Data via OpenAQ v3 (requires API key). For bulk fallback, try <code>/api/openaq-bulk</code>.
      </p>
    </div>
  )
}

