import { BrowserRouter, Routes, Route } from 'react-router-dom';
import AppLayout from './components/layout/AppLayout';
import DashboardPage from './pages/DashboardPage';
import CardBrowserPage from './pages/CardBrowserPage';
import CardEditorPage from './pages/CardEditorPage';
import KnowledgeGraphPage from './pages/KnowledgeGraphPage';
import DrillSessionPage from './pages/DrillSessionPage';
import FIReInspectorPage from './pages/FIReInspectorPage';
import SyncPanelPage from './pages/SyncPanelPage';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<AppLayout />}>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/cards" element={<CardBrowserPage />} />
          <Route path="/cards/new" element={<CardEditorPage />} />
          <Route path="/cards/:cardId/edit" element={<CardEditorPage />} />
          <Route path="/graph" element={<KnowledgeGraphPage />} />
          <Route path="/drill" element={<DrillSessionPage />} />
          <Route path="/fire" element={<FIReInspectorPage />} />
          <Route path="/sync" element={<SyncPanelPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
