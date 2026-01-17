import { useState } from 'react';
import SafetyAnalyzer from './components/SafetyAnalyzer';
import RoutePlanner from './components/RoutePlanner';
import ReportSubmission from './components/ReportSubmission';
import SOSPanel from './components/SOSPanel';
import 'leaflet/dist/leaflet.css';
import './App.css';

function App() {
  const [activeTab, setActiveTab] = useState('route-planner');

  const tabs = [
    { id: 'route-planner', label: '🗺️ Route Planner', component: RoutePlanner },
    { id: 'safety-analyzer', label: '🛡️ Safety Analyzer', component: SafetyAnalyzer },
    { id: 'report', label: '⚠️ Report Issue', component: ReportSubmission },
    { id: 'sos', label: '🚨 SOS', component: SOSPanel },
  ];

  const ActiveComponent = tabs.find(tab => tab.id === activeTab)?.component || RoutePlanner;

  return (
    <div style={{ minHeight: '100vh', background: '#f3f4f6' }}>
      {/* Header */}
      <header style={{
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        padding: '20px',
        boxShadow: '0 2px 10px rgba(0,0,0,0.1)'
      }}>
        <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
          <h1 style={{ color: 'white', margin: '0 0 20px 0', fontSize: '28px', fontWeight: 'bold' }}>
            🛡️ Safety Route
          </h1>
          
          {/* Tab Navigation */}
          <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
            {tabs.map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                style={{
                  padding: '10px 20px',
                  background: activeTab === tab.id ? 'white' : 'rgba(255,255,255,0.2)',
                  color: activeTab === tab.id ? '#667eea' : 'white',
                  border: 'none',
                  borderRadius: '8px',
                  fontSize: '14px',
                  fontWeight: '600',
                  cursor: 'pointer',
                  transition: 'all 0.3s',
                }}
              >
                {tab.label}
              </button>
            ))}
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main>
        <ActiveComponent />
      </main>
    </div>
  );
}

export default App;