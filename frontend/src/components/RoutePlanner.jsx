import React, { useState } from 'react';
import Map from './Map';
import LocationSearch from './LocationSearch';
import api from '../services/api';

const RoutePlanner = () => {
  const [startLocation, setStartLocation] = useState(null);
  const [endLocation, setEndLocation] = useState(null);
  const [routes, setRoutes] = useState([]);
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handlePlanRoute = async () => {
    if (!startLocation || !endLocation) {
      alert('Please select both start and end locations');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // Get nearby reports
      const reportsResponse = await api.getNearbyReports(
        startLocation.latitude,
        startLocation.longitude,
        5.0,
        24
      );
      
      setReports(reportsResponse.reports || []);

      // Plan route
      const routeResponse = await api.planRoute(
        { latitude: startLocation.latitude, longitude: startLocation.longitude },
        { latitude: endLocation.latitude, longitude: endLocation.longitude }
      );

      if (routeResponse.success && routeResponse.routes) {
        const processedRoutes = routeResponse.routes.map((route, idx) => ({
          ...route,
          recommended: idx === routeResponse.recommended_route_index
        }));
        setRoutes(processedRoutes);
      }
    } catch (err) {
      setError('Failed to plan route. Please try again.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const mapCenter = startLocation 
    ? [startLocation.latitude, startLocation.longitude]
    : [37.7749, -122.4194];

  return (
    <div style={{ padding: '20px', maxWidth: '1200px', margin: '0 auto' }}>
      <h1>🛡️ Safety Route Planner</h1>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '20px' }}>
        <div>
          <label style={{ display: 'block', marginBottom: '8px', fontWeight: '500' }}>
            Start Location
          </label>
          <LocationSearch
            placeholder="Enter start location..."
            onLocationSelect={setStartLocation}
          />
          {startLocation && (
            <div style={{ fontSize: '12px', color: '#666', marginTop: '4px' }}>
              ✓ {startLocation.address}
            </div>
          )}
        </div>

        <div>
          <label style={{ display: 'block', marginBottom: '8px', fontWeight: '500' }}>
            Destination
          </label>
          <LocationSearch
            placeholder="Enter destination..."
            onLocationSelect={setEndLocation}
          />
          {endLocation && (
            <div style={{ fontSize: '12px', color: '#666', marginTop: '4px' }}>
              ✓ {endLocation.address}
            </div>
          )}
        </div>
      </div>

      <button
        onClick={handlePlanRoute}
        disabled={loading || !startLocation || !endLocation}
        style={{
          padding: '12px 24px',
          fontSize: '16px',
          fontWeight: '600',
          backgroundColor: loading ? '#ccc' : '#2563eb',
          color: 'white',
          border: 'none',
          borderRadius: '8px',
          cursor: loading ? 'not-allowed' : 'pointer',
          marginBottom: '20px'
        }}
      >
        {loading ? 'Planning Route...' : 'Find Safest Route 🛡️'}
      </button>

      {error && (
        <div style={{ 
          padding: '12px', 
          backgroundColor: '#fee2e2', 
          color: '#dc2626',
          borderRadius: '8px',
          marginBottom: '20px'
        }}>
          {error}
        </div>
      )}

      <Map
        center={mapCenter}
        zoom={13}
        routes={routes}
        reports={reports}
        height="600px"
      />

      {routes.length > 0 && (
        <div style={{ marginTop: '20px' }}>
          <h2>Route Options</h2>
          {routes.map((route, idx) => (
            <div
              key={idx}
              style={{
                padding: '16px',
                border: route.recommended ? '2px solid #22c55e' : '1px solid #ddd',
                borderRadius: '8px',
                marginBottom: '12px',
                backgroundColor: route.recommended ? '#f0fdf4' : 'white'
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <div>
                  <h3 style={{ margin: 0 }}>
                    {route.route_name}
                    {route.recommended && (
                      <span style={{ marginLeft: '8px', fontSize: '12px', color: '#22c55e' }}>
                        ✓ RECOMMENDED
                      </span>
                    )}
                  </h3>
                  <div style={{ fontSize: '14px', color: '#666' }}>
                    {route.distance_km?.toFixed(2)} km · {route.duration_minutes} min
                  </div>
                </div>
                <div style={{ textAlign: 'right' }}>
                  <div style={{ fontSize: '24px', fontWeight: '700' }}>
                    {route.safety_score || 'N/A'}
                  </div>
                  <div style={{ fontSize: '12px', color: '#666' }}>
                    {route.risk_label}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default RoutePlanner;