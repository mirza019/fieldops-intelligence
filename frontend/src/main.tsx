import React from 'react';
import { createRoot } from 'react-dom/client';
import { QueryClient, QueryClientProvider, useQuery } from '@tanstack/react-query';
import './styles.css';

type KPI = {
  id: string;
  name: string;
  value: number | null;
  unit: string;
  target: number;
};

const api = import.meta.env.VITE_API_URL ?? 'http://localhost:8000';

const navigation = [
  'Executive Overview',
  'Operational Analytics',
  'Technical Performance',
  'Service Orders',
  'Equipment Performance',
  'Cost & Efficiency',
  'Spare Parts & Supply',
  'Lean Improvement',
  'Data Quality & Governance',
  'What-if Simulation',
];

const metricConfig: Record<string, { label: string; suffix: string; tone: 'positive' | 'warning' | 'neutral'; }> = {
  'KPI-001': { label: 'SLA Compliance', suffix: '%', tone: 'positive' },
  'KPI-002': { label: 'First-Time Fix Rate', suffix: '%', tone: 'positive' },
  'KPI-003': { label: 'Technician Utilization', suffix: '%', tone: 'neutral' },
  'KPI-004': { label: 'Avg. Resolution Time', suffix: 'd', tone: 'warning' },
  'KPI-005': { label: 'Backlog', suffix: '', tone: 'warning' },
  'KPI-008': { label: 'Service Cost', suffix: '€', tone: 'positive' },
};

function formatValue(value: number | null, unit: string) {
  if (value === null) return 'N/A';
  if (unit === '%') return `${(value * 100).toFixed(1)}%`;
  if (unit === 'days') return `${value.toFixed(1)} days`;
  if (unit === 'currency') return `€ ${value.toLocaleString(undefined, { maximumFractionDigits: 1 })}`;
  return value.toLocaleString(undefined, { maximumFractionDigits: 1 });
}

function App() {
  const { data, error, isLoading } = useQuery<KPI[]>({
    queryKey: ['kpis'],
    queryFn: () =>
      fetch(`${api}/api/kpis`, {
        headers: { 'x-demo-role': 'data_analyst' },
      }).then((r) => {
        if (!r.ok) throw Error('API unavailable');
        return r.json();
      }),
  });

  const cards = (data ?? [])
    .filter((kpi) => kpi.id in metricConfig)
    .slice(0, 6)
    .map((kpi) => {
      const config = metricConfig[kpi.id];
      const target = kpi.unit === '%' ? `${(kpi.target * 100).toFixed(0)}%` : kpi.target.toString();
      const delta = kpi.value === null ? '—' : kpi.unit === '%' ? `${(kpi.value * 100 - kpi.target * 100).toFixed(1)} pts` : `${(kpi.value - kpi.target).toFixed(1)}`;
      return {
        ...kpi,
        config,
        target,
        delta,
      };
    });

  const chartBars = [72, 68, 82, 61, 74, 88, 81, 76, 66, 59, 71, 78];
  const orderTypes = [
    { label: 'Preventive', value: 38, color: '#2f7ef9' },
    { label: 'Corrective', value: 32, color: '#f2b21a' },
    { label: 'Inspection', value: 14, color: '#4bb881' },
    { label: 'Retrofit', value: 8, color: '#ff7d4d' },
    { label: 'Emergency', value: 5, color: '#6d6d8f' },
    { label: 'Other', value: 3, color: '#d5dfe6' },
  ];

  return (
    <main className="app-shell">
      <aside className="sidebar">
        <div className="brand-block">
          <div className="brand-mark">F</div>
          <div>
            <h1>FieldOps Intelligence</h1>
            <small>Field Service Performance &amp; Digital Transformation</small>
          </div>
        </div>

        <nav className="nav-panel">
          {navigation.map((item, index) => (
            <button key={item} className={index === 0 ? 'nav-item active' : 'nav-item'}>
              {item}
            </button>
          ))}
        </nav>

        <div className="filter-panel">
          <h3>Filters</h3>
          <label>
            <span>Date Range</span>
            <select defaultValue="Last 12 months">
              <option>Last 12 months</option>
              <option>Last 6 months</option>
              <option>Quarter to date</option>
            </select>
          </label>
          <label>
            <span>Region</span>
            <select defaultValue="All">
              <option>All</option>
              <option>Europe</option>
              <option>North America</option>
            </select>
          </label>
          <label>
            <span>Service Type</span>
            <select defaultValue="All">
              <option>All</option>
              <option>Maintenance</option>
              <option>Commissioning</option>
            </select>
          </label>
        </div>
      </aside>

      <section className="content">
        <header className="topbar">
          <div>
            <h2>Executive Overview</h2>
          </div>
          <div className="topbar-actions">
            <div className="date-chip">Jan 2024 — Dec 2024</div>
            <div className="date-chip muted">Last 12 months</div>
            <div className="company-badge">Siemens Energy (Example)</div>
          </div>
        </header>

        <div className="kpi-grid">
          {cards.map((kpi) => {
            const value = kpi.value === null ? 'N/A' : formatValue(kpi.value, kpi.unit);
            const isPositive = kpi.config.tone === 'positive';
            const isWarning = kpi.config.tone === 'warning';
            return (
              <article key={kpi.id} className="metric-card">
                <div className="metric-header">
                  <span className={`metric-icon ${kpi.config.tone}`} />
                  <span className="metric-label">{kpi.config.label}</span>
                </div>
                <div className="metric-value">{value}</div>
                <div className="metric-meta">
                  <span className={isPositive ? 'trend positive' : isWarning ? 'trend warning' : 'trend neutral'}>
                    {kpi.delta}
                  </span>
                  <span>Target: {kpi.target}</span>
                </div>
              </article>
            );
          })}
        </div>

        <div className="panel-grid">
          <section className="panel panel-wide">
            <div className="panel-header">
              <h3>SLA Compliance Trend</h3>
            </div>
            <div className="trend-line">
              {chartBars.map((bar, index) => (
                <span key={index} style={{ height: `${bar}%` }} />
              ))}
            </div>
            <div className="trend-labels">
              {['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'].map((item) => (
                <span key={item}>{item}</span>
              ))}
            </div>
          </section>

          <section className="panel">
            <div className="panel-header">
              <h3>Service Orders by Type</h3>
            </div>
            <div className="donut-wrap">
              <div className="donut-chart">
                <div className="donut-center">
                  <strong>4,862</strong>
                  <span>Total</span>
                </div>
              </div>
              <ul className="legend">
                {orderTypes.map((item) => (
                  <li key={item.label}>
                    <span className="legend-dot" style={{ background: item.color }} />
                    {item.label}
                    <strong>{item.value}%</strong>
                  </li>
                ))}
              </ul>
            </div>
          </section>

          <section className="panel">
            <div className="panel-header">
              <h3>Service Orders by Region</h3>
            </div>
            <div className="region-map">
              <div className="region-block region-1" />
              <div className="region-block region-2" />
              <div className="region-block region-3" />
              <div className="region-block region-4" />
            </div>
          </section>

          <section className="panel">
            <div className="panel-header">
              <h3>Service Orders Trend</h3>
            </div>
            <div className="mini-bars">
              {chartBars.map((bar, index) => (
                <div key={index} className="mini-bar" style={{ height: `${bar}%` }} />
              ))}
            </div>
          </section>

          <section className="panel">
            <div className="panel-header">
              <h3>Open Service Orders by Aging</h3>
            </div>
            <div className="aging-grid">
              {[
                { label: '< 7 days', value: 342 },
                { label: '7–30 days', value: 318 },
                { label: '31–90 days', value: 218 },
                { label: '> 90 days', value: 186 },
              ].map((item) => (
                <div key={item.label} className="aging-item">
                  <div className="aging-bar" style={{ height: `${Math.max((item.value / 400) * 100, 20)}%` }} />
                  <span>{item.label}</span>
                  <strong>{item.value}</strong>
                </div>
              ))}
            </div>
          </section>

          <section className="panel">
            <div className="panel-header">
              <h3>Key Insights</h3>
            </div>
            <ul className="insights-list">
              <li>SLA compliance improved by 4.1% compared to last quarter.</li>
              <li>Average resolution time reduced by 10%.</li>
              <li>Technician utilization is 1.8% below target.</li>
              <li>Emergency services represent 18% higher than planned.</li>
            </ul>
          </section>
        </div>

        <div className="bottom-grid">
          <section className="panel table-panel">
            <div className="panel-header">
              <h3>Technician Performance</h3>
            </div>
            <table>
              <thead>
                <tr>
                  <th>Technician</th>
                  <th>Region</th>
                  <th>Utilization</th>
                  <th>First-Time Fix</th>
                  <th>Avg. Resolution</th>
                </tr>
              </thead>
              <tbody>
                {[
                  ['Tech-012', 'Germany', '82%', '86%', '4.1 days'],
                  ['Tech-028', 'France', '76%', '81%', '5.2 days'],
                  ['Tech-037', 'UK', '71%', '79%', '6.0 days'],
                  ['Tech-044', 'Italy', '68%', '77%', '6.8 days'],
                ].map((row) => (
                  <tr key={row[0]}>
                    {row.map((cell) => <td key={cell}>{cell}</td>)}
                  </tr>
                ))}
              </tbody>
            </table>
          </section>

          <section className="panel table-panel">
            <div className="panel-header">
              <h3>Recent Service Orders</h3>
            </div>
            <table>
              <thead>
                <tr>
                  <th>Order ID</th>
                  <th>Customer</th>
                  <th>Equipment</th>
                  <th>Priority</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {[
                  ['SO-100452', 'Plant A', 'Gas Turbine', 'High', 'Open'],
                  ['SO-100438', 'Plant B', 'Generator', 'Medium', 'In Progress'],
                  ['SO-100421', 'Plant C', 'Compressor', 'High', 'Open'],
                  ['SO-100399', 'Plant D', 'Steam Turbine', 'Medium', 'Completed'],
                ].map((row) => (
                  <tr key={row[0]}>
                    {row.map((cell) => <td key={cell}>{cell}</td>)}
                  </tr>
                ))}
              </tbody>
            </table>
          </section>
        </div>
      </section>
    </main>
  );
}

createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <QueryClientProvider client={new QueryClient()}>
      <App />
    </QueryClientProvider>
  </React.StrictMode>,
);

