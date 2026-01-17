// API Configuration
const API_CONFIG = {
  development: {
    baseURL: 'http://localhost:8000',
  },
  production: {
    baseURL: 'https://your-backend-url.com', // Update when deployed
  }
};

const environment = process.env.NODE_ENV || 'development';
export const API_BASE_URL = API_CONFIG[environment].baseURL;

export const ENDPOINTS = {
  // Routes
  planRoute: '/routes/plan',
  getRoute: (id) => `/routes/${id}`,
  
  // Reports
  submitReport: '/reports/report',
  getNearbyReports: '/reports/report/nearby',
  
  // SOS
  triggerSOS: '/sos/sos',
  getSOSHistory: '/sos/history',
  
  // Geocoding
  geocode: '/geocoding/geocode',
  reverseGeocode: '/geocoding/reverse',
  searchPlaces: '/geocoding/search',
  
  // Health
  health: '/health',
};

fetch("http://127.0.0.1:8000/ping")
  .then(res => res.json())
  .then(data => {
    console.log("CONNECTED:", data);
    alert("Backend connected!");
  })
  .catch(err => {
    console.error("FAILED:", err);
  });
