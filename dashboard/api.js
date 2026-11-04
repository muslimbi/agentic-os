const API_ROOT = "/api";

async function get(path) {
  const response = await fetch(`${API_ROOT}${path}`, {
    headers: { Accept: "application/json" },
  });
  if (!response.ok) {
    throw new Error(`API request failed (${response.status}).`);
  }
  return response.json();
}

export const api = {
  health: () => get("/health"),
  dashboard: () => get("/dashboard"),
  features: () => get("/features"),
  feature: (featureId) => get(`/features/${encodeURIComponent(featureId)}`),
};
