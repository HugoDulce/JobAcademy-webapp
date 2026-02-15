import { Component, type ReactNode } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import AppLayout from './components/layout/AppLayout';
import DashboardPage from './pages/DashboardPage';
import CardBrowserPage from './pages/CardBrowserPage';
import CardEditorPage from './pages/CardEditorPage';
import KnowledgeGraphPage from './pages/KnowledgeGraphPage';
import DrillSessionPage from './pages/DrillSessionPage';
import FIReInspectorPage from './pages/FIReInspectorPage';
import SyncPanelPage from './pages/SyncPanelPage';

class ErrorBoundary extends Component<{ children: ReactNode }, { error: Error | null }> {
  state = { error: null as Error | null };
  static getDerivedStateFromError(error: Error) { return { error }; }
  render() {
    if (this.state.error) {
      return (
        <div style={{ padding: 24, color: '#dc2626', fontFamily: 'monospace', whiteSpace: 'pre-wrap' }}>
          <h2>Page Error</h2>
          <p>{this.state.error.message}</p>
          <pre style={{ fontSize: 12, marginTop: 8 }}>{this.state.error.stack}</pre>
        </div>
      );
    }
    return this.props.children;
  }
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<AppLayout />}>
          <Route path="/" element={<ErrorBoundary><DashboardPage /></ErrorBoundary>} />
          <Route path="/cards" element={<ErrorBoundary><CardBrowserPage /></ErrorBoundary>} />
          <Route path="/cards/new" element={<ErrorBoundary><CardEditorPage /></ErrorBoundary>} />
          <Route path="/cards/:cardId/edit" element={<ErrorBoundary><CardEditorPage /></ErrorBoundary>} />
          <Route path="/graph" element={<ErrorBoundary><KnowledgeGraphPage /></ErrorBoundary>} />
          <Route path="/drill/:nodeId" element={<ErrorBoundary><DrillSessionPage /></ErrorBoundary>} />
          <Route path="/drill" element={<ErrorBoundary><DrillSessionPage /></ErrorBoundary>} />
          <Route path="/fire" element={<ErrorBoundary><FIReInspectorPage /></ErrorBoundary>} />
          <Route path="/sync" element={<ErrorBoundary><SyncPanelPage /></ErrorBoundary>} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
