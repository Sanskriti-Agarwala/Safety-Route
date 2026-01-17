// src/api/backend.js
const BASE_URL = "http://127.0.0.1:8000";

export function startTrip(payload) {
  return fetch(`${BASE_URL}/trip/start`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  }).then(res => res.json());
}

export function getSafety(lat, lon) {
  return fetch(`${BASE_URL}/safety/area?lat=${lat}&lon=${lon}`)
    .then(res => res.json());
}
