import { useState } from 'react';

function App() {
  const [riskScore, setRiskScore] = useState(50);
  const [timeOfDay, setTimeOfDay] = useState('');
  const [routeName, setRouteName] = useState('');
  const [locationLabel, setLocationLabel] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const analyzeSafety = async () => {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await fetch('http://localhost:8000/safety/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          risk_score: parseInt(riskScore),
          time_of_day: timeOfDay || null,
          route_name: routeName || null,
          location_label: locationLabel || null,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const getRiskColor = (level) => {
    if (level === 'low') return '#10b981';
    if (level === 'medium') return '#f59e0b';
    if (level === 'high') return '#ef4444';
    return '#6b7280';
  };

  return (
    <div style={{ minHeight: '100vh', background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', padding: '40px 20px' }}>
      <div style={{ maxWidth: '600px', margin: '0 auto', background: 'white', borderRadius: '16px', padding: '40px', boxShadow: '0 20px 60px rgba(0,0,0,0.3)' }}>
        <h1 style={{ fontSize: '32px', fontWeight: 'bold', marginBottom: '8px', color: '#1f2937', textAlign: 'center' }}>
          🛡️ Safety Route Analyzer
        </h1>
        <p style={{ color: '#6b7280', textAlign: 'center', marginBottom: '32px' }}>
          AI-powered safety assessment for your routes
        </p>

        <div style={{ marginBottom: '24px' }}>
          <label style={{ display: 'block', fontWeight: '600', marginBottom: '8px', color: '#374151' }}>
            Risk Score (0-100)
          </label>
          <input
            type="range"
            min="0"
            max="100"
            value={riskScore}
            onChange={(e) => setRiskScore(e.target.value)}
            style={{ width: '100%', marginBottom: '8px' }}
          />
          <div style={{ textAlign: 'center', fontSize: '24px', fontWeight: 'bold', color: '#667eea' }}>
            {riskScore}
          </div>
        </div>

        <div style={{ marginBottom: '16px' }}>
          <label style={{ display: 'block', fontWeight: '600', marginBottom: '8px', color: '#374151' }}>
            Time of Day
          </label>
          <input
            type="text"
            value={timeOfDay}
            onChange={(e) => setTimeOfDay(e.target.value)}
            placeholder="e.g., 10:30 PM"
            style={{ width: '100%', padding: '12px', border: '2px solid #e5e7eb', borderRadius: '8px', fontSize: '14px' }}
          />
        </div>

        <div style={{ marginBottom: '16px' }}>
          <label style={{ display: 'block', fontWeight: '600', marginBottom: '8px', color: '#374151' }}>
            Route Name
          </label>
          <input
            type="text"
            value={routeName}
            onChange={(e) => setRouteName(e.target.value)}
            placeholder="e.g., Main Street Route"
            style={{ width: '100%', padding: '12px', border: '2px solid #e5e7eb', borderRadius: '8px', fontSize: '14px' }}
          />
        </div>

        <div style={{ marginBottom: '24px' }}>
          <label style={{ display: 'block', fontWeight: '600', marginBottom: '8px', color: '#374151' }}>
            Location Label
          </label>
          <input
            type="text"
            value={locationLabel}
            onChange={(e) => setLocationLabel(e.target.value)}
            placeholder="e.g., Downtown Area"
            style={{ width: '100%', padding: '12px', border: '2px solid #e5e7eb', borderRadius: '8px', fontSize: '14px' }}
          />
        </div>

        <button
          onClick={analyzeSafety}
          disabled={loading}
          style={{
            width: '100%',
            padding: '14px',
            background: loading ? '#9ca3af' : 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            fontSize: '16px',
            fontWeight: '600',
            cursor: loading ? 'not-allowed' : 'pointer',
            transition: 'transform 0.2s',
          }}
          onMouseEnter={(e) => !loading && (e.target.style.transform = 'scale(1.02)')}
          onMouseLeave={(e) => (e.target.style.transform = 'scale(1)')}
        >
          {loading ? 'Analyzing...' : 'Analyze Safety'}
        </button>

        {error && (
          <div style={{ marginTop: '24px', padding: '16px', background: '#fee2e2', border: '2px solid #ef4444', borderRadius: '8px' }}>
            <p style={{ color: '#991b1b', fontWeight: '600', marginBottom: '4px' }}>Error</p>
            <p style={{ color: '#7f1d1d', fontSize: '14px' }}>{error}</p>
          </div>
        )}

        {result && (
          <div style={{ marginTop: '24px', padding: '24px', background: '#f9fafb', borderRadius: '12px', border: '2px solid #e5e7eb' }}>
            <div style={{ display: 'flex', alignItems: 'center', marginBottom: '16px' }}>
              <div
                style={{
                  width: '12px',
                  height: '12px',
                  borderRadius: '50%',
                  background: getRiskColor(result.risk_level),
                  marginRight: '12px',
                }}
              />
              <span style={{ fontSize: '20px', fontWeight: 'bold', color: '#1f2937', textTransform: 'uppercase' }}>
                {result.risk_level} Risk
              </span>
            </div>

            <div style={{ marginBottom: '16px' }}>
              <p style={{ fontWeight: '600', color: '#374151', marginBottom: '8px' }}>Explanation</p>
              <p style={{ color: '#6b7280', lineHeight: '1.6' }}>{result.explanation}</p>
            </div>

            <div>
              <p style={{ fontWeight: '600', color: '#374151', marginBottom: '8px' }}>Recommendation</p>
              <p style={{ color: '#6b7280', lineHeight: '1.6' }}>{result.recommendation}</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
