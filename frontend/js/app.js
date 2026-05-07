function redirectTo(path) {
  window.location.href = path;
}

function getCurrentUser() {
  try {
    const raw = localStorage.getItem('user');
    return raw ? JSON.parse(raw) : { role: 'guest', name: 'Guest' };
  } catch {
    return { role: 'guest', name: 'Guest' };
  }
}

function requireAuth(requiredRole) {
  const token = localStorage.getItem('token');
  const user = getCurrentUser();

  if (!token || (requiredRole && user.role !== requiredRole)) {
    redirectTo('/');
    return false;
  }
  return true;
}

function debounce(fn, wait) {
  let timeout;
  return (...args) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => fn(...args), wait);
  };
}

function getRiskLevel(score) {
  if (score >= 0.7) return 'High';
  if (score >= 0.4) return 'Medium';
  return 'Low';
}

function getRiskColor(score) {
  if (score >= 0.7) return '#ef4444';
  if (score >= 0.4) return '#f59e0b';
  return '#22c55e';
}

function formatPercent(score) {
  return `${Math.round((Number(score) || 0) * 100)}%`;
}

function formatDate(value) {
  if (!value) return 'N/A';
  const d = new Date(value);
  return Number.isNaN(d.getTime()) ? 'N/A' : d.toLocaleString();
}

function showToast(message) {
  window.alert(message);
}

const api = {
  async get(path) {
    const res = await fetch(path, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token') || ''}`,
      },
    });
    if (!res.ok) throw new Error(`GET ${path} failed`);
    return res.json();
  },

  async post(path, body) {
    const res = await fetch(path, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${localStorage.getItem('token') || ''}`,
      },
      body: JSON.stringify(body || {}),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.error || `POST ${path} failed`);
    }
    return res.json();
  },

  logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    redirectTo('/');
  },
};

document.addEventListener('DOMContentLoaded', () => {
  const loginForm = document.getElementById('loginForm');
  if (!loginForm) return;

  loginForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    const username = document.getElementById('username')?.value || '';
    const password = document.getElementById('password')?.value || '';

    try {
      const result = await api.post('/api/login', { username, password });
      localStorage.setItem('token', result.token);
      localStorage.setItem('user', JSON.stringify(result.user));
      redirectTo('/admin');
    } catch (error) {
      showToast(error.message || 'Login failed');
    }
  });
});
