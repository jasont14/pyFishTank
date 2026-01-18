const API_BASE = 'http://127.0.0.1:5001/api';

async function fetchJson(url, options = {}) {
  const response = await fetch(`${API_BASE}${url}`, {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  });
  if (!response.ok) {
    const error = await response.json().catch(() => ({ error: 'Request failed' }));
    throw new Error(error.error || 'Request failed');
  }
  return response.json();
}

// Tank API
export const tankApi = {
  getAll: () => fetchJson('/tanks'),
  getById: (id) => fetchJson(`/tanks/${id}`),
  create: (data) => fetchJson('/tanks', { method: 'POST', body: JSON.stringify(data) }),
  update: (id, data) => fetchJson(`/tanks/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  delete: (id) => fetchJson(`/tanks/${id}`, { method: 'DELETE' }),
  updateWaterParams: (id, data) => fetchJson(`/tanks/${id}/water-params`, { method: 'PUT', body: JSON.stringify(data) }),
  getWaterParamHistory: (id, limit = 10) => fetchJson(`/tanks/${id}/water-params/history?limit=${limit}`),
};

// Fish API
export const fishApi = {
  getAll: (tankId = null) => fetchJson(`/fish${tankId ? `?tank_id=${tankId}` : ''}`),
  getById: (id) => fetchJson(`/fish/${id}`),
  create: (data) => fetchJson('/fish', { method: 'POST', body: JSON.stringify(data) }),
  update: (id, data) => fetchJson(`/fish/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  delete: (id) => fetchJson(`/fish/${id}`, { method: 'DELETE' }),
  move: (id, tankId) => fetchJson(`/fish/${id}/move`, { method: 'POST', body: JSON.stringify({ tank_id: tankId }) }),
  updateHealth: (id, status) => fetchJson(`/fish/${id}/health`, { method: 'PUT', body: JSON.stringify({ health_status: status }) }),
};

// Maintenance API
export const maintenanceApi = {
  getAll: (params = {}) => {
    const query = new URLSearchParams();
    if (params.tankId) query.set('tank_id', params.tankId);
    if (params.activityType) query.set('activity_type', params.activityType);
    if (params.limit) query.set('limit', params.limit);
    const queryStr = query.toString();
    return fetchJson(`/maintenance${queryStr ? `?${queryStr}` : ''}`);
  },
  create: (data) => fetchJson('/maintenance', { method: 'POST', body: JSON.stringify(data) }),
};

// Reports API
export const reportsApi = {
  getSummary: () => fetchJson('/reports/summary'),
};
