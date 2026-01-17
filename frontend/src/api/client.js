const API_BASE_URL = 'http://127.0.0.1:8000';

export const api = {
  async planRoute(startLat, startLon, endLat, endLon) {
    const response = await fetch(`${API_BASE_URL}/api/routes/plan`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        start_lat: startLat,
        start_lon: startLon,
        end_lat: endLat,
        end_lon: endLon,
      }),
    });
    return response.json();
  },
};