import { useEffect, useRef, useState } from 'react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { api, setToken, getToken } from './api'

// ---------- Login ----------
function Login({ onLoggedIn }) {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const res = await api.login(username, password)
      setToken(res.access_token)
      onLoggedIn()
    } catch (err) {
      setError('Access denied. Check your credentials.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-bg scanlines flex items-center justify-center font-mono">
      <div className="w-full max-w-sm">
        <div className="mb-6 text-center">
          <div className="text-amber text-xs tracking-[0.3em] uppercase mb-2">Restricted Access</div>
          <div className="text-ink text-xl font-semibold">HONEYNET CONSOLE</div>
        </div>
        <form onSubmit={handleSubmit} className="bg-surface border border-border rounded-lg p-6 slide-in">
          <label className="block text-muted text-xs uppercase tracking-wider mb-1">Operator ID</label>
          <input
            className="w-full bg-surface2 border border-border rounded px-3 py-2 mb-4 text-ink outline-none focus:border-amber"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            autoFocus
          />
          <label className="block text-muted text-xs uppercase tracking-wider mb-1">Passphrase</label>
          <input
            type="password"
            className="w-full bg-surface2 border border-border rounded px-3 py-2 mb-4 text-ink outline-none focus:border-amber"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          {error && <div className="text-critical text-sm mb-4">{error}</div>}
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-amber text-bg font-semibold rounded py-2 hover:brightness-110 transition disabled:opacity-50"
          >
            {loading ? 'Authenticating…' : 'Enter Console'}
          </button>
        </form>
      </div>
    </div>
  )
}

// ---------- Small building blocks ----------
function StatCard({ label, value, accent = 'text-ink' }) {
  return (
    <div className="bg-surface border border-border rounded-lg p-4 slide-in">
      <div className="text-muted text-[11px] uppercase tracking-wider mb-1">{label}</div>
      <div className={`text-2xl font-mono font-semibold ${accent}`}>{value}</div>
    </div>
  )
}

function riskColor(score) {
  if (score >= 0.7) return 'text-critical'
  if (score >= 0.4) return 'text-amber'
  return 'text-safe'
}

// ---------- Live Threat Terminal (signature element) ----------
function ThreatTerminal({ events }) {
  const containerRef = useRef(null)
  useEffect(() => {
    const el = containerRef.current
    if (el) el.scrollTop = el.scrollHeight
  }, [events])

  return (
    <div className="bg-[#05070A] border border-border rounded-lg overflow-hidden flex flex-col h-[420px]">
      <div className="flex items-center gap-2 px-4 py-2 border-b border-border bg-surface2">
        <span className="w-2.5 h-2.5 rounded-full bg-critical" />
        <span className="w-2.5 h-2.5 rounded-full bg-amber" />
        <span className="w-2.5 h-2.5 rounded-full bg-safe" />
        <span className="ml-3 text-muted text-xs font-mono">live-threat-feed — decoy-network</span>
      </div>
      <div ref={containerRef} className="flex-1 overflow-y-auto terminal-scroll px-4 py-3 font-mono text-sm space-y-1.5">
        {events.length === 0 && (
          <div className="text-muted italic">No activity yet. The decoys are waiting patiently.</div>
        )}
        {events.map((e) => (
          <div key={e.id} className="slide-in">
            <span className="text-muted">[{new Date(e.timestamp).toLocaleTimeString()}]</span>{' '}
            <span className="text-muted">session#{e.session_id}</span>{' '}
            <span className={riskColor(e.risk_score)}>{e.event_type}</span>{' '}
            <span className="text-ink">{e.payload}</span>{' '}
            <span className="text-muted">risk={e.risk_score.toFixed(2)}</span>
          </div>
        ))}
        <div className="text-amber cursor">▊</div>
      </div>
    </div>
  )
}

// ---------- Decoy status nodes ----------
function DecoyList({ decoys }) {
  return (
    <div className="bg-surface border border-border rounded-lg p-4 h-[420px] overflow-y-auto terminal-scroll">
      <div className="text-muted text-[11px] uppercase tracking-wider mb-3">Active Decoys</div>
      <div className="space-y-3">
        {decoys.length === 0 && (
          <div className="text-muted text-sm italic">No decoys registered yet. Start your sensor script.</div>
        )}
        {decoys.map((d) => {
          const adapted = d.adaptive_profile?.last_adaptation === 'triggered'
          return (
            <div
              key={d.id}
              className="border border-border rounded-md p-3 flex items-center justify-between bg-surface2"
            >
              <div>
                <div className="font-mono text-sm text-ink">{d.name}</div>
                <div className="text-muted text-xs">{d.service_type} · {d.ip}:{d.port}</div>
              </div>
              <div className="flex items-center gap-2">
                <span
                  className={`w-2 h-2 rounded-full ${adapted ? 'bg-critical pulse-critical' : 'bg-safe pulse-armed'}`}
                />
                <span className={`text-xs font-mono ${adapted ? 'text-critical' : 'text-safe'}`}>
                  {adapted ? 'high-interaction' : 'low-interaction'}
                </span>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

// ---------- Alerts feed ----------
function AlertsFeed({ alerts, onResolve }) {
  const severityColor = { critical: 'text-critical', high: 'text-critical', medium: 'text-amber', low: 'text-safe' }
  return (
    <div className="bg-surface border border-border rounded-lg p-4">
      <div className="text-muted text-[11px] uppercase tracking-wider mb-3">Alerts</div>
      <div className="space-y-2 max-h-[280px] overflow-y-auto terminal-scroll">
        {alerts.length === 0 && (
          <div className="text-muted text-sm italic">Quiet. No alerts — enjoy it while it lasts.</div>
        )}
        {alerts.map((a) => (
          <div key={a.id} className="flex items-center justify-between border border-border rounded-md p-2.5 bg-surface2">
            <div>
              <span className={`font-mono text-xs uppercase mr-2 ${severityColor[a.severity] || 'text-ink'}`}>
                {a.severity}
              </span>
              <span className="text-sm text-ink">{a.message}</span>
            </div>
            {!a.resolved && (
              <button
                onClick={() => onResolve(a.id)}
                className="text-xs font-mono text-muted hover:text-amber border border-border rounded px-2 py-1"
              >
                Resolve
              </button>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}

// ---------- Attack volume chart ----------
function AttackChart({ data }) {
  return (
    <div className="bg-surface border border-border rounded-lg p-4">
      <div className="text-muted text-[11px] uppercase tracking-wider mb-3">Attack Volume (7 days)</div>
      <ResponsiveContainer width="100%" height={220}>
        <LineChart data={data}>
          <CartesianGrid stroke="#232A35" strokeDasharray="3 3" />
          <XAxis dataKey="day" stroke="#7C8798" fontSize={11} />
          <YAxis stroke="#7C8798" fontSize={11} allowDecimals={false} />
          <Tooltip
            contentStyle={{ background: '#171C25', border: '1px solid #232A35', borderRadius: 6 }}
            labelStyle={{ color: '#E4E9F0' }}
          />
          <Line type="monotone" dataKey="count" stroke="#FFB020" strokeWidth={2} dot={{ r: 3 }} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}

// ---------- Top attackers ----------
function TopAttackers({ attackers }) {
  return (
    <div className="bg-surface border border-border rounded-lg p-4">
      <div className="text-muted text-[11px] uppercase tracking-wider mb-3">Most Persistent Attackers</div>
      <div className="space-y-2">
        {attackers.length === 0 && <div className="text-muted text-sm italic">Nobody's knocked yet.</div>}
        {attackers.map((a, i) => (
          <div key={a.ip} className="flex items-center justify-between font-mono text-sm">
            <span className="text-ink">{i + 1}. {a.ip}</span>
            <span className="text-muted">{a.attempts} attempt{a.attempts !== 1 ? 's' : ''}</span>
          </div>
        ))}
      </div>
    </div>
  )
}

// ---------- Dashboard ----------
function Dashboard({ onLogout }) {
  const [overview, setOverview] = useState(null)
  const [events, setEvents] = useState([])
  const [decoys, setDecoys] = useState([])
  const [alerts, setAlerts] = useState([])
  const [timeseries, setTimeseries] = useState([])

  async function refresh() {
    try {
      const [ov, ev, dc, al, ts] = await Promise.all([
        api.overview(), api.events(), api.decoys(), api.alerts(), api.timeseries(7),
      ])
      setOverview(ov)
      setEvents(ev.slice(-30))
      setDecoys(dc)
      setAlerts(al.slice(0, 15))
      setTimeseries(ts)
    } catch (err) {
      console.error('Refresh failed', err)
    }
  }

  useEffect(() => {
    refresh()
    const interval = setInterval(refresh, 3000)
    return () => clearInterval(interval)
  }, [])

  async function handleResolve(id) {
    await api.resolveAlert(id)
    refresh()
  }

  return (
    <div className="min-h-screen bg-bg scanlines font-sans text-ink">
      <header className="flex items-center justify-between px-6 py-4 border-b border-border">
        <div className="flex items-center gap-3">
          <span className="w-2.5 h-2.5 rounded-full bg-safe pulse-armed" />
          <span className="font-mono text-sm tracking-wide">HONEYNET // ADAPTIVE DECEPTION CONSOLE</span>
        </div>
        <div className="flex items-center gap-4">
          <span className="font-mono text-xs text-safe uppercase tracking-widest">Status: Armed</span>
          <button onClick={onLogout} className="text-xs text-muted hover:text-ink font-mono">Log out</button>
        </div>
      </header>

      <main className="p-6 max-w-7xl mx-auto space-y-6">
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          <StatCard label="Decoys Active" value={overview ? `${overview.active_decoys}/${overview.total_decoys}` : '—'} />
          <StatCard label="Sessions" value={overview?.total_sessions ?? '—'} />
          <StatCard label="Events Logged" value={overview?.total_events ?? '—'} />
          <StatCard label="Open Alerts" value={overview?.open_alerts ?? '—'} accent={overview?.open_alerts > 0 ? 'text-critical' : 'text-safe'} />
          <StatCard label="Top Attacker" value={overview?.top_attackers?.[0]?.ip ?? '—'} />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <ThreatTerminal events={events} />
          </div>
          <DecoyList decoys={decoys} />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <AttackChart data={timeseries} />
          </div>
          <TopAttackers attackers={overview?.top_attackers ?? []} />
        </div>

        <AlertsFeed alerts={alerts} onResolve={handleResolve} />
      </main>
    </div>
  )
}

// ---------- App root ----------
export default function App() {
  const [loggedIn, setLoggedIn] = useState(!!getToken())

  if (!loggedIn) return <Login onLoggedIn={() => setLoggedIn(true)} />
  return <Dashboard onLogout={() => { setToken(null); setLoggedIn(false) }} />
}