import { NavLink } from 'react-router-dom';
import { LayoutDashboard, Library, Network, Flame, GraduationCap, RefreshCw } from 'lucide-react';

const links = [
  { to: '/', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/cards', label: 'Cards', icon: Library },
  { to: '/graph', label: 'Knowledge Graph', icon: Network },
  { to: '/drill', label: 'Drill Session', icon: GraduationCap },
  { to: '/fire', label: 'FIRe Inspector', icon: Flame },
  { to: '/sync', label: 'Sync Panel', icon: RefreshCw },
];

export default function Sidebar() {
  return (
    <aside className="w-56 bg-gray-900 text-gray-200 flex flex-col min-h-screen">
      <div className="p-4 border-b border-gray-700">
        <h1 className="text-lg font-bold tracking-tight">JobAcademy</h1>
        <p className="text-xs text-gray-400">Learning Management</p>
      </div>
      <nav className="flex-1 p-2 space-y-1">
        {links.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2 rounded-md text-sm transition-colors ${
                isActive ? 'bg-gray-700 text-white' : 'text-gray-400 hover:bg-gray-800 hover:text-gray-200'
              }`
            }
          >
            <Icon size={18} />
            {label}
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}
