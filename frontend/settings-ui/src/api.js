const API = import.meta.env.VITE_API_URL || "http://localhost:8000";

async function json(res) {
  if (!res.ok) {
    const msg = await res.text();
    throw new Error(msg || res.statusText);
  }
  return res.status === 204 ? null : res.json();
}

export const api = {
  login(email, password) {
    return fetch(`${API}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({ email, password }),
    }).then(json);
  },

  logout() {
    return fetch(`${API}/auth/logout`, {
      method: "POST",
      credentials: "include",
    }).then(json);
  },

  me() {
    return fetch(`${API}/auth/me`, {
      credentials: "include",
    }).then(json);
  },

  getSettings() {
    return fetch(`${API}/settings`, {
      method: "GET",
      credentials: "include",
    }).then(json);
  },

  saveSettings(settings) {
    return fetch(`${API}/settings`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify(settings),
    }).then(json);
  },

  exportPpt() {
    return fetch(`${API}/export-ppt`, {
      method: "POST",
      credentials: "include",
    }).then(json);
  },

  sendEmail(userEmail) {
    return fetch(`${API}/auth/send-email`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({ email: userEmail }),
    }).then(json);
  },

  scheduleEmail() {
    return fetch(`${API}/schedule-email`, {
      method: "POST",
      credentials: "include",
    }).then(json);
  },
};
