/**
 * Insider Sentinel — app.js
 * Global application controller: API client, auth, dark mode, toasts.
 */

/* ============================================================
   Constants
   ============================================================ */
const API_BASE = "/api";
const TOKEN_KEY = "is_token";
const USER_KEY = "is_user";
const THEME_KEY = "is_theme";

/* ============================================================
   API Client
   ============================================================ */
class APIClient {
  constructor(baseUrl = API_BASE) {
    this.baseUrl = baseUrl;
  }

  _token() {
    return localStorage.getItem(TOKEN_KEY) || "";
  }

  async _request(method, path, body = null) {
    const headers = { "Content-Type": "application/json" };
    const token = this._token();
    if (token) headers["Authorization"] = `Bearer ${token}`;

    const opts = { method, headers };
    if (body !== null) opts.body = JSON.stringify(body);

    try {
      const res = await fetch(this.baseUrl + path, opts);
      const json = await res.json();

      if (res.status === 401 && path !== "/auth/login") {
        // Token expired → redirect to login
        Auth.clear();
        window.location.href = "/login";
        return null;
      }
      return { ok: res.ok, status: res.status, data: json };
    } catch (err) {
      console.error("API Error:", err);
      return { ok: false, status: 0, data: { error: "Network error" } };
    }
  }

  get(path) {
    return this._request("GET", path);
  }
  post(path, body) {
    return this._request("POST", path, body);
  }
  put(path, body) {
    return this._request("PUT", path, body);
  }
  delete(path) {
    return this._request("DELETE", path);
  }
}

/* ============================================================
   Auth
   ============================================================ */
const Auth = {
  save(sessionData) {
    localStorage.setItem(TOKEN_KEY, sessionData.token);
    localStorage.setItem(USER_KEY, JSON.stringify(sessionData));
  },

  clear() {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
  },

  getUser() {
    try {
      return JSON.parse(localStorage.getItem(USER_KEY));
    } catch {
      return null;
    }
  },

  isLoggedIn() {
    return !!localStorage.getItem(TOKEN_KEY);
  },

  isAdmin() {
    const u = this.getUser();
    return u && u.role === "admin";
  },

  isEmployee() {
    const u = this.getUser();
    return u && u.role === "employee";
  },

  requireAuth(role = null) {
    if (!this.isLoggedIn()) {
      window.location.href = "/login";
      return false;
    }
    if (role === "admin" && !this.isAdmin()) {
      window.location.href = "/login";
      return false;
    }
    if (role === "employee" && !this.isEmployee()) {
      window.location.href = "/login";
      return false;
    }
    return true;
  },

  async logout() {
    const api = new APIClient();
    await api.post("/auth/logout", {});
    this.clear();
    window.location.href = "/login";
  },
};

/* ============================================================
   Dark Mode
   ============================================================ */
const DarkMode = {
  init() {
    const saved = localStorage.getItem(THEME_KEY) || "light";
    this.apply(saved);
  },

  apply(theme) {
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem(THEME_KEY, theme);
    // Update toggle button icon
    const icon = document.querySelector(".dark-mode-icon");
    if (icon) icon.textContent = theme === "dark" ? "☀️" : "🌙";
  },

  toggle() {
    const current = localStorage.getItem(THEME_KEY) || "light";
    this.apply(current === "dark" ? "light" : "dark");
  },
};

/* ============================================================
   Toast Notifications
   ============================================================ */
const Toast = {
  _container: null,

  _getContainer() {
    if (!this._container) {
      this._container = document.createElement("div");
      this._container.className = "toast-container";
      document.body.appendChild(this._container);
    }
    return this._container;
  },

  show(message, type = "info", duration = 3500) {
    const icons = { success: "✅", error: "❌", warning: "⚠️", info: "ℹ️" };
    const toast = document.createElement("div");
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `<span>${icons[type] || ""}</span><span>${message}</span>`;
    this._getContainer().appendChild(toast);
    setTimeout(() => {
      toast.style.animation = "none";
      toast.style.opacity = "0";
      toast.style.transform = "translateX(120%)";
      toast.style.transition = "0.3s ease";
      setTimeout(() => toast.remove(), 320);
    }, duration);
  },

  success(msg) {
    this.show(msg, "success");
  },
  error(msg) {
    this.show(msg, "error", 5000);
  },
  warning(msg) {
    this.show(msg, "warning");
  },
  info(msg) {
    this.show(msg, "info");
  },
};

/* ============================================================
   UI Helpers
   ============================================================ */
const UI = {
  /** Returns a colored badge element string for a risk level */
  riskBadge(level) {
    const map = {
      low: "badge-low",
      medium: "badge-medium",
      high: "badge-high",
      critical: "badge-critical",
    };
    return `<span class="badge ${map[level] || "badge-low"}">${level}</span>`;
  },

  /** Returns inline style color for a risk score (0–1) */
  riskColor(score) {
    if (score < 0.25) return "var(--success)";
    if (score < 0.5) return "var(--warning)";
    if (score < 0.75) return "var(--alert)";
    return "#c53030";
  },

  riskClass(level) {
    return (
      { low: "low", medium: "medium", high: "high", critical: "critical" }[
        level
      ] || "low"
    );
  },

  /** Format ISO timestamp to human-readable local time */
  formatDate(ts) {
    if (!ts) return "—";
    try {
      let dStr = ts;
      // SQLite returns 'YYYY-MM-DD HH:MM:SS' without T or Z, and datetime.utcnow() returns without Z
      // The server operates in UTC. Ensure it parses correctly.
      if (typeof dStr === "string") {
        dStr = dStr.replace(" ", "T");
        if (!dStr.endsWith("Z") && !dStr.match(/[+-]\d{2}:\d{2}$/)) {
          dStr += "Z";
        }
      }
      return new Date(dStr).toLocaleString(undefined, {
        year: "numeric",
        month: "short",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      });
    } catch {
      return ts;
    }
  },

  /** Format ms to human-readable */
  formatMs(ms) {
    if (ms == null) return "—";
    if (ms < 1000) return `${ms}ms`;
    return `${(ms / 1000).toFixed(1)}s`;
  },

  /** Percentage from 0–1 score */
  pct(score) {
    return Math.round((score || 0) * 100);
  },

  /** Show/hide a loading spinner in a container */
  showLoading(containerId) {
    const el = document.getElementById(containerId);
    if (el) el.innerHTML = '<div class="spinner"></div>';
  },

  showError(containerId, msg) {
    const el = document.getElementById(containerId);
    if (el) el.innerHTML = `<div class="alert alert-danger">${msg}</div>`;
  },

  /** Inject current user info into navbar */
  populateNavbar() {
    const user = Auth.getUser();
    if (!user) return;
    const nameEl = document.querySelector(".navbar-user-name");
    if (nameEl) nameEl.textContent = user.name;
    const avatarEl = document.querySelector(".navbar-avatar");
    if (avatarEl) avatarEl.textContent = (user.name || "U")[0].toUpperCase();
  },

  /** Confirm modal helper — returns Promise<bool> */
  confirm(message, title = "Confirm") {
    return new Promise((resolve) => {
      const overlay = document.createElement("div");
      overlay.className = "modal-overlay";
      overlay.innerHTML = `
        <div class="modal">
          <div class="modal-header">
            <span class="modal-title">${title}</span>
          </div>
          <p>${message}</p>
          <div class="modal-footer">
            <button class="btn btn-secondary" id="_cancelBtn">Cancel</button>
            <button class="btn btn-danger" id="_confirmBtn">Confirm</button>
          </div>
        </div>`;
      document.body.appendChild(overlay);
      setTimeout(() => overlay.classList.add("show"), 10);
      const close = (val) => {
        overlay.classList.remove("show");
        setTimeout(() => overlay.remove(), 300);
        resolve(val);
      };
      overlay.querySelector("#_confirmBtn").onclick = () => close(true);
      overlay.querySelector("#_cancelBtn").onclick = () => close(false);
    });
  },
};

/* ============================================================
   Sidebar toggle (mobile)
   ============================================================ */
function initSidebarToggle() {
  const toggle = document.getElementById("sidebarToggle");
  const sidebar = document.querySelector(".sidebar");
  if (toggle && sidebar) {
    toggle.addEventListener("click", () => sidebar.classList.toggle("open"));
    document.addEventListener("click", (e) => {
      if (!sidebar.contains(e.target) && !toggle.contains(e.target)) {
        sidebar.classList.remove("open");
      }
    });
  }
}

/* ============================================================
   Global initialisation
   ============================================================ */
document.addEventListener("DOMContentLoaded", () => {
  DarkMode.init();
  UI.populateNavbar();
  initSidebarToggle();

  // Wire up all dark-mode toggles on the page
  document.querySelectorAll("[data-toggle-dark]").forEach((btn) => {
    btn.addEventListener("click", () => DarkMode.toggle());
  });

  // Wire up all logout buttons
  document.querySelectorAll("[data-logout]").forEach((btn) => {
    btn.addEventListener("click", async (e) => {
      e.preventDefault();
      const ok = await UI.confirm("Are you sure you want to logout?", "Logout");
      if (ok) Auth.logout();
    });
  });
});

// Expose globally
window.API = new APIClient();
window.Auth = Auth;
window.DarkMode = DarkMode;
window.Toast = Toast;
window.UI = UI;
