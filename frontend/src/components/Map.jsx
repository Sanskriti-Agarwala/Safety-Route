import React from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline, Circle } from 'react-leaflet';
import L from '../utils/leafletConfig';
import 'leaflet/dist/leaflet.css';

const Map = ({ 
  center = [37.7749, -122.4194], 
  zoom = 13,
  routes = [],
  reports = [],
  height = '500px'
}) => {
  // Custom icons
  const dangerIcon = new L.Icon({
    iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png',
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34],
    shadowSize: [41, 41]
  });

  const warningIcon = new L.Icon({
    iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-orange.png',
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34],
    shadowSize: [41, 41]
  });

  const safeIcon = new L.Icon({
    iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-green.png',
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34],
    shadowSize: [41, 41]
  });

  const getReportIcon = (severity) => {
    if (severity >= 4) return dangerIcon;
    if (severity >= 3) return warningIcon;
    return safeIcon;
  };

  const getRouteColor = (safetyScore) => {
    if (safetyScore >= 70) return '#dc2626';
    if (safetyScore >= 50) return '#f59e0b';
    if (safetyScore >= 30) return '#fbbf24';
    return '#22c55e';
  };

  return (
    <MapContainer
      center={center}
      zoom={zoom}
      style={{ height, width: '100%', borderRadius: '8px' }}
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />

      {/* Routes */}
      {routes.map((route, idx) => (
        <React.Fragment key={`route-${idx}`}>
          <Polyline
            positions={route.route_points?.map(p => [p.latitude, p.longitude]) || []}
            color={getRouteColor(route.safety_score || 50)}
            weight={route.recommended ? 5 : 3}
            opacity={route.recommended ? 0.8 : 0.5}
          >
            <Popup>
              <strong>{route.route_name || `Route ${idx + 1}`}</strong><br />
              Distance: {route.distance_km?.toFixed(2)} km<br />
              Duration: {route.duration_minutes} min<br />
              Safety Score: {route.safety_score || 'N/A'}<br />
              Risk: {route.risk_label || 'Unknown'}
            </Popup>
          </Polyline>

          {/* Start/End Markers */}
          {route.route_points?.[0] && (
            <Marker 
              position={[route.route_points[0].latitude, route.route_points[0].longitude]}
              icon={safeIcon}
            >
              <Popup>Start</Popup>
            </Marker>
          )}
          {route.route_points?.[route.route_points.length - 1] && (
            <Marker 
              position={[
                route.route_points[route.route_points.length - 1].latitude,
                route.route_points[route.route_points.length - 1].longitude
              ]}
            >
              <Popup>Destination</Popup>
            </Marker>
          )}
        </React.Fragment>
      ))}

      {/* Safety Reports */}
      {reports.map((report, idx) => (
        <React.Fragment key={`report-${report.id || idx}`}>
          <Marker
            position={[report.latitude, report.longitude]}
            icon={getReportIcon(report.severity)}
          >
            <Popup>
              <strong style={{ textTransform: 'capitalize' }}>
                {report.category?.replace('_', ' ')}
              </strong><br />
              Severity: {report.severity}/5<br />
              {report.description && <>{report.description}<br /></>}
              {report.age_hours && <>Reported: {report.age_hours.toFixed(1)}h ago</>}
            </Popup>
          </Marker>

          {report.severity >= 4 && (
            <Circle
              center={[report.latitude, report.longitude]}
              radius={200}
              color="#dc2626"
              fillColor="#dc2626"
              fillOpacity={0.1}
            />
          )}
        </React.Fragment>
      ))}
    </MapContainer>
  );
};

export default Map;