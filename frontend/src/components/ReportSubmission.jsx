import { useState } from 'react';
import api from '../services/api';

function ReportSubmission() {
  const [formData, setFormData] = useState({
    latitude: '',
    longitude: '',
    category: 'poor_lighting',
    severity: 3,
    description: ''
  });
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const categories = [
    { value: 'poor_lighting', label: '💡 Poor Lighting' },
    { value: 'harassment', label: '⚠️ Harassment' },
    { value: 'suspicious_activity', label: '👁️ Suspicious Activity' },
    { value: 'unsafe_area', label: '🚫 Unsafe Area' },
    { value: 'accident', label: '🚗 Accident' },
    { value: 'roadblock', label: '🚧 Roadblock' },
    { value: 'crime_incident', label: '🚨 Crime Incident' },
    { value: 'other', label: '📝 Other' },
  ];

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    setResult(null);

    try {
      const response = await api.submitReport({
        latitude: parseFloat(formData.latitude),
        longitude: parseFloat(formData.longitude),
        category: formData.category,
        severity: parseInt(formData.severity),
        description: formData.description || null
      });

      setResult(response);
      
      // Reset form
      setFormData({
        latitude: '',
        longitude: '',
        category: 'poor_lighting',
        severity: 3,
        description: ''
      });
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  };

  const getCurrentLocation = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setFormData(prev => ({
            ...prev,
            latitude: position.coords.latitude.toFixed(6),
            longitude: position.coords.longitude.toFixed(6)
          }));
        },
        (err) => {
          setError('Unable to get your location');
        }
      );
    }
  };

  return (
    <div style={{ padding: '40px 20px' }}>
      <div style={{ maxWidth: '600px', margin: '0 auto', background: 'white', borderRadius: '16px', padding: '40px', boxShadow: '0 4px 20px rgba(0,0,0,0.1)' }}>
        <h2 style={{ fontSize: '28px', fontWeight: 'bold', marginBottom: '8px', color: '#1f2937', textAlign: 'center' }}>
          Report Safety Issue
        </h2>
        <p style={{ color: '#6b7280', textAlign: 'center', marginBottom: '32px' }}>
          Help make routes safer by reporting incidents
        </p>

        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: '20px' }}>
            <label style={{ display: 'block', fontWeight: '600', marginBottom: '8px', color: '#374151' }}>
              Location
            </label>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr auto', gap: '10px' }}>
              <input
                type="number"
                step="any"
                placeholder="Latitude"
                value={formData.latitude}
                onChange={(e) => setFormData({...formData, latitude: e.target.value})}
                required
                style={{ padding: '12px', border: '2px solid #e5e7eb', borderRadius: '8px' }}
              />
              <input
                type="number"
                step="any"
                placeholder="Longitude"
                value={formData.longitude}
                onChange={(e) => setFormData({...formData, longitude: e.target.value})}
                required
                style={{ padding: '12px', border: '2px solid #e5e7eb', borderRadius: '8px' }}
              />
              <button
                type="button"
                onClick={getCurrentLocation}
                style={{
                  padding: '12px',
                  background: '#667eea',
                  color: 'white',
                  border: 'none',
                  borderRadius: '8px',
                  cursor: 'pointer',
                  fontSize: '18px'
                }}
                title="Use current location"
              >
                📍
              </button>
            </div>
          </div>

          <div style={{ marginBottom: '20px' }}>
            <label style={{ display: 'block', fontWeight: '600', marginBottom: '8px', color: '#374151' }}>
              Category
            </label>
            <select
              value={formData.category}
              onChange={(e) => setFormData({...formData, category: e.target.value})}
              style={{ width: '100%', padding: '12px', border: '2px solid #e5e7eb', borderRadius: '8px', fontSize: '14px' }}
            >
              {categories.map(cat => (
                <option key={cat.value} value={cat.value}>{cat.label}</option>
              ))}
            </select>
          </div>

          <div style={{ marginBottom: '20px' }}>
            <label style={{ display: 'block', fontWeight: '600', marginBottom: '8px', color: '#374151' }}>
              Severity: {formData.severity}/5
            </label>
            <input
              type="range"
              min="1"
              max="5"
              value={formData.severity}
              onChange={(e) => setFormData({...formData, severity: e.target.value})}
              style={{ width: '100%' }}
            />
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', color: '#6b7280' }}>
              <span>Minimal</span>
              <span>Critical</span>
            </div>
          </div>

          <div style={{ marginBottom: '24px' }}>
            <label style={{ display: 'block', fontWeight: '600', marginBottom: '8px', color: '#374151' }}>
              Description (Optional)
            </label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData({...formData, description: e.target.value})}
              placeholder="Provide additional details..."
              rows="4"
              style={{ width: '100%', padding: '12px', border: '2px solid #e5e7eb', borderRadius: '8px', fontSize: '14px', fontFamily: 'inherit' }}
            />
          </div>

          <button
            type="submit"
            disabled={submitting}
            style={{
              width: '100%',
              padding: '14px',
              background: submitting ? '#9ca3af' : 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              fontSize: '16px',
              fontWeight: '600',
              cursor: submitting ? 'not-allowed' : 'pointer',
            }}
          >
            {submitting ? 'Submitting...' : 'Submit Report'}
          </button>
        </form>

        {error && (
          <div style={{ marginTop: '20px', padding: '16px', background: '#fee2e2', borderRadius: '8px' }}>
            <p style={{ color: '#991b1b', fontWeight: '600' }}>Error: {error}</p>
          </div>
        )}

        {result && result.success && (
          <div style={{ marginTop: '20px', padding: '16px', background: '#d1fae5', borderRadius: '8px' }}>
            <p style={{ color: '#065f46', fontWeight: '600' }}>✅ {result.message}</p>
            <p style={{ color: '#047857', fontSize: '14px', marginTop: '4px' }}>
              Report ID: {result.report_id}
            </p>
          </div>
        )}
      </div>
    </div>
  );
}

export default ReportSubmission;