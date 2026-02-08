import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { GraduationCap, RefreshCw, Library } from 'lucide-react';
import type { DashboardStats } from '../api/dashboard';
import { fetchDashboardStats } from '../api/dashboard';

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchDashboardStats().then(setStats).catch((e) => setError(e.message));
  }, []);

  if (error) return <div className="text-red-600">Error: {error}</div>;
  if (!stats) return <div className="text-gray-500">Loading...</div>;

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Dashboard</h1>
      <div className="grid grid-cols-4 gap-4 mb-8">
        <StatCard label="Total Cards" value={stats.total_cards} />
        <StatCard label="Due Today" value={stats.due_today} color="text-amber-600" />
        <StatCard label="Mastery" value={`${stats.mastery_pct}%`} color="text-green-600" />
        <StatCard label="Reviewed Today" value={stats.reviewed_today} color="text-blue-600" />
      </div>

      <div className="grid grid-cols-2 gap-4 mb-8">
        <div className="bg-white rounded-lg shadow p-4">
          <h3 className="text-sm font-medium text-gray-500 mb-3">Cards by Pillar</h3>
          {Object.entries(stats.cards_by_pillar).map(([k, v]) => (
            <div key={k} className="flex justify-between text-sm py-1">
              <span>{k}</span><span className="font-mono">{v}</span>
            </div>
          ))}
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <h3 className="text-sm font-medium text-gray-500 mb-3">Cards by Layer</h3>
          {Object.entries(stats.cards_by_layer).map(([k, v]) => (
            <div key={k} className="flex justify-between text-sm py-1">
              <span>{k}</span><span className="font-mono">{v}</span>
            </div>
          ))}
        </div>
      </div>

      <h2 className="text-lg font-semibold mb-3">Quick Actions</h2>
      <div className="flex gap-3">
        <Link to="/drill" className="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700">
          <GraduationCap size={18} /> Start Review
        </Link>
        <Link to="/sync" className="flex items-center gap-2 px-4 py-2 bg-gray-700 text-white rounded-md hover:bg-gray-800">
          <RefreshCw size={18} /> Sync Pipeline
        </Link>
        <Link to="/cards" className="flex items-center gap-2 px-4 py-2 bg-gray-200 text-gray-800 rounded-md hover:bg-gray-300">
          <Library size={18} /> Browse Cards
        </Link>
      </div>
    </div>
  );
}

function StatCard({ label, value, color = 'text-gray-900' }: { label: string; value: string | number; color?: string }) {
  return (
    <div className="bg-white rounded-lg shadow p-4">
      <p className="text-sm text-gray-500">{label}</p>
      <p className={`text-2xl font-bold ${color}`}>{value}</p>
    </div>
  );
}
