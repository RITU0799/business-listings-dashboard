import { useEffect, useMemo, useState } from 'react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend
} from 'recharts';
import { Activity, Building2, MapPinned, Layers3, Database, RefreshCw, Search, AlertCircle } from 'lucide-react';

const API = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';
const PIE_COLORS = ['#6366f1', '#06b6d4', '#10b981', '#f59e0b', '#f472b6', '#8b5cf6', '#fb7185', '#14b8a6'];

function StatCard({ label, value, hint, icon: Icon }) {
  return <article className="stat-card">
    <div className="stat-top"><span>{label}</span><span className="stat-icon"><Icon size={18}/></span></div>
    <div className="stat-value">{Number(value || 0).toLocaleString('en-IN')}</div>
    <div className="stat-hint">{hint}</div>
  </article>;
}

function ChartCard({ title, subtitle, children, action }) {
  return <section className="panel">
    <div className="panel-heading"><div><h2>{title}</h2><p>{subtitle}</p></div>{action}</div>
    {children}
  </section>;
}

function EmptyChart({ loading, error }) {
  return <div className="chart-empty">{loading ? 'Loading dashboard data…' : error ? 'Could not load data. Check that the API and MySQL are running.' : 'No data yet. Import a CSV using scripts/import_csv.py.'}</div>;
}

export default function App() {
  const [summary, setSummary] = useState(null);
  const [cities, setCities] = useState([]);
  const [categories, setCategories] = useState([]);
  const [sources, setSources] = useState([]);
  const [listings, setListings] = useState([]);
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  async function loadDashboard() {
    setLoading(true);
    setError('');
    try {
      const paths = [
        '/api/dashboard/summary',
        '/api/dashboard/city-counts?limit=10',
        '/api/dashboard/category-counts?limit=10',
        '/api/dashboard/source-counts?limit=10',
        '/api/listings?limit=100'
      ];
      const responses = await Promise.all(paths.map(p => fetch(`${API}${p}`)));
      const bad = responses.find(r => !r.ok);
      if (bad) throw new Error(`API request failed (${bad.status})`);
      const [s, c, cat, src, list] = await Promise.all(responses.map(r => r.json()));
      setSummary(s); setCities(c); setCategories(cat); setSources(src); setListings(list);
    } catch (e) {
      setError(e.message || 'Could not connect to the API.');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { loadDashboard(); }, []);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return listings;
    return listings.filter(r => [r.business_name, r.category, r.city, r.source].some(v => (v || '').toLowerCase().includes(q)));
  }, [listings, query]);

  const chartTooltip = { contentStyle: { background: '#101a2d', border: '1px solid #29364d', borderRadius: 12, color: '#f8fafc' } };

  return <div className="app-shell">
    <aside className="sidebar">
      <div className="brand"><div className="brand-mark"><Building2 size={22}/></div><div><strong>ListingIQ</strong><span>BUSINESS INTELLIGENCE</span></div></div>
      <div className="side-label">WORKSPACE</div>
      <div className="nav-item active"><Activity size={17}/> Overview</div>
      <div className="side-note"><span className="status-dot"/> API dashboard</div>
      <div className="sidebar-bottom"><div className="mini-db"><Database size={17}/><div><b>Data source</b><span>FastAPI · MySQL</span></div></div><span className="version">Internship Assignment · v1.0</span></div>
    </aside>

    <main className="main-content">
      <header className="topbar">
        <div><div className="eyebrow">BUSINESS DIRECTORY ANALYTICS</div><h1>Listings overview</h1><p className="page-subtitle">A clear view of your business directory data.</p></div>
        <button className="refresh-btn" onClick={loadDashboard} disabled={loading}><RefreshCw size={16} className={loading ? 'spin' : ''}/> Refresh data</button>
      </header>

      {error && <div className="error-banner"><AlertCircle size={18}/><div><b>Connection issue</b><span>{error} Start FastAPI and check the MySQL connection, then refresh.</span></div></div>}

      <div className="stats-grid">
        <StatCard label="Total listings" value={summary?.total_listings} hint="Records stored in MySQL" icon={Building2}/>
        <StatCard label="Cities covered" value={summary?.distinct_cities} hint="Distinct city names" icon={MapPinned}/>
        <StatCard label="Categories" value={summary?.distinct_categories} hint="Business categories" icon={Layers3}/>
        <StatCard label="Data sources" value={summary?.distinct_sources} hint="Source labels in database" icon={Database}/>
      </div>

      <div className="charts-grid">
        <ChartCard title="City-wise distribution" subtitle="Top cities by number of listings">
          {loading || error || !cities.length ? <EmptyChart loading={loading} error={error}/> :
            <ResponsiveContainer width="100%" height={285}>
              <BarChart data={cities} margin={{top: 12, right: 8, left: -16, bottom: 8}}>
                <CartesianGrid strokeDasharray="3 3" stroke="#263247" vertical={false}/>
                <XAxis dataKey="label" tick={{fill:'#8f9db2',fontSize:11}} axisLine={false} tickLine={false}/>
                <YAxis tick={{fill:'#8f9db2',fontSize:11}} axisLine={false} tickLine={false}/>
                <Tooltip {...chartTooltip} formatter={(v) => [v, 'Listings']}/>
                <Bar dataKey="count" fill="#818cf8" radius={[6,6,0,0]} maxBarSize={42}/>
              </BarChart>
            </ResponsiveContainer>}
        </ChartCard>

        <ChartCard title="Category mix" subtitle="Share of listings by category">
          {loading || error || !categories.length ? <EmptyChart loading={loading} error={error}/> :
            <ResponsiveContainer width="100%" height={285}>
              <PieChart>
                <Pie data={categories} dataKey="count" nameKey="label" cx="50%" cy="46%" innerRadius={62} outerRadius={96} paddingAngle={3}>
                  {categories.map((entry, index) => <Cell key={entry.label} fill={PIE_COLORS[index % PIE_COLORS.length]}/>)}
                </Pie>
                <Tooltip {...chartTooltip} formatter={(v) => [v, 'Listings']}/>
                <Legend verticalAlign="bottom" height={44} formatter={(value) => <span className="legend-text">{value}</span>}/>
              </PieChart>
            </ResponsiveContainer>}
        </ChartCard>

        <ChartCard title="Source breakdown" subtitle="Where the listing records came from">
          {loading || error || !sources.length ? <EmptyChart loading={loading} error={error}/> :
            <div className="source-list">{sources.map((item, i) => {
              const total = summary?.total_listings || 1;
              return <div className="source-row" key={item.label}>
                <div className="source-meta"><span><i style={{background: PIE_COLORS[i % PIE_COLORS.length]}}/>{item.label}</span><b>{item.count.toLocaleString('en-IN')}</b></div>
                <div className="progress-track"><div style={{width: `${Math.min(100, item.count / total * 100)}%`, background: PIE_COLORS[i % PIE_COLORS.length]}}/></div>
                <small>{(item.count / total * 100).toFixed(1)}% of all records</small>
              </div>;
            })}</div>}
        </ChartCard>

        <ChartCard title="Recently added listings" subtitle="Latest 100 records returned by the API" action={<span className="record-count">{filtered.length} shown</span>}>
          <div className="table-tools"><div className="search-box"><Search size={15}/><input value={query} onChange={e => setQuery(e.target.value)} placeholder="Search name, city, category…"/></div></div>
          <div className="table-wrap"><table><thead><tr><th>Business</th><th>Category</th><th>City</th><th>Source</th></tr></thead>
            <tbody>{filtered.slice(0, 12).map(row => <tr key={row.id}><td className="business-cell">{row.business_name}</td><td><span className="category-pill">{row.category}</span></td><td>{row.city}</td><td className="source-cell">{row.source}</td></tr>)}
            {!loading && !error && filtered.length === 0 && <tr><td colSpan="4" className="no-results">No matching listings.</td></tr>}
            </tbody></table></div>
        </ChartCard>
      </div>
      <footer><span>ListingIQ · Business Listings Dashboard</span><span>React · FastAPI · MySQL</span></footer>
    </main>
  </div>;
}
