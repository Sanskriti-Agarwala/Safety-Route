import { API_BASE_URL, ENDPOINTS } from '../config/api';

// Helper function for API calls
async function apiCall(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`;
  
  const defaultOptions = {
    headers: {
      'Content-Type': 'application/json',
    },
  };
  
  const config = { ...defaultOptions, ...options };
  
  try {
    const response = await fetch(url, config);
    
    if (!response.ok) {
      throw new Error(`API Error: ${response.status} ${response.statusText}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('API call failed:', error);
    throw error;
  }
}

// API Methods
export const api = {
  // Health Check
  async checkHealth() {
    return apiCall(ENDPOINTS.health);
  },
  
  // Route Planning
  async planRoute(startLocation, endLocation, preferences = {}) {
    return apiCall(ENDPOINTS.planRoute, {
      method: 'POST',
      body: JSON.stringify({
        start_location: startLocation,
        end_location: endLocation,
        user_preferences: preferences,
      }),
    });
  },
  
  // Safety Reports
  async submitReport(reportData) {
    return apiCall(ENDPOINTS.submitReport, {
      method: 'POST',
      body: JSON.stringify(reportData),
    });
  },
  
  async getNearbyReports(lat, lon, radiusKm = 1.0, hoursAgo = 24) {
    const params = new URLSearchParams({
      lat: lat.toString(),
      lon: lon.toString(),
      radius_km: radiusKm.toString(),
      hours_ago: hoursAgo.toString(),
    });
    
    return apiCall(`${ENDPOINTS.getNearbyReports}?${params}`);
  },
  
  // SOS
  async triggerSOS(location, emergencyContacts, message = null) {
    return apiCall(ENDPOINTS.triggerSOS, {
      method: 'POST',
      body: JSON.stringify({
        latitude: location.latitude,
        longitude: location.longitude,
        emergency_contacts: emergencyContacts,
        message: message,
      }),
    });
  },
  
  // Geocoding
  async geocodeAddress(address) {
    return apiCall(ENDPOINTS.geocode, {
      method: 'POST',
      body: JSON.stringify({ address }),
    });
  },
  
  async reverseGeocode(lat, lon) {
    const params = new URLSearchParams({
      lat: lat.toString(),
      lon: lon.toString(),
    });
    return apiCall(`${ENDPOINTS.reverseGeocode}?${params}`);
  },
  
  async searchPlaces(query, limit = 5) {
    const params = new URLSearchParams({
      query,
      limit: limit.toString(),
    });
    return apiCall(`${ENDPOINTS.searchPlaces}?${params}`);
  },
};

export default api;