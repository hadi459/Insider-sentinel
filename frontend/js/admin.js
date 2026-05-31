/**
 * Insider Sentinel — admin.js
 * Admin-specific logic: employee list, monitoring, risk display.
 */

/** Escape HTML special characters to prevent XSS. */
function escAdminHtml(str) {
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

/* ============================================================
   Admin Dashboard
   ============================================================ */
const AdminDashboard = {
  employees: [],
  filtered: [],

  async init() {
    if (!Auth.requireAuth("admin")) return;
    await this.loadStats();
    await this.loadEmployees();
    this.bindFilters();
    this.bindRefresh();
  },

  async loadStats() {
    const res = await API.get("/admin/dashboard");
    if (!res || !res.ok) return;
    const d = res.data.data;
    document.getElementById("statTotal") &&
      (document.getElementById("statTotal").textContent =
        d.total_employees ?? "—");
    document.getElementById("statHighRisk") &&
      (document.getElementById("statHighRisk").textContent =
        d.high_risk_count ?? "—");
    document.getElementById("statSessions") &&
      (document.getElementById("statSessions").textContent =
        d.active_sessions ?? "—");
  },

  async loadEmployees() {
    UI.showLoading("employeeTableBody");
    const res = await API.get("/admin/employees");
    if (!res || !res.ok) {
      UI.showError("employeeTableBody", "Failed to load employees");
      return;
    }
    this.employees = res.data.data.employees || [];
    this.filtered = [...this.employees];
    this.renderTable();
  },

  renderTable() {
    const tbody = document.getElementById("employeeTableBody");
    if (!tbody) return;

    if (!this.filtered.length) {
      tbody.innerHTML =
        '<tr><td colspan="6" class="text-center text-muted" style="padding:2rem">No employees found</td></tr>';
      return;
    }

    tbody.innerHTML = this.filtered
      .map(
        (emp) => `
      <tr>
        <td>
          <div style="display:flex;align-items:center;gap:.6rem">
            <div class="avatar" style="background:var(--navy)">${escAdminHtml((emp.name || "U")[0].toUpperCase())}</div>
            <div>
              <div style="font-weight:600;color:var(--text-primary)">${escAdminHtml(emp.name)}</div>
              <div style="font-size:.8rem;color:var(--text-muted)">${escAdminHtml(emp.email)}</div>
            </div>
          </div>
        </td>
        <td>${escAdminHtml(emp.department || "—")}</td>
        <td>
          <div class="risk-bar-container">
            <div class="risk-bar">
              <div class="risk-bar-fill ${UI.riskClass(emp.risk_level)}"
                   style="width:${UI.pct(emp.risk_score)}%"></div>
            </div>
            <span class="risk-score-text" style="color:${UI.riskColor(emp.risk_score)}">
              ${UI.pct(emp.risk_score)}%
            </span>
          </div>
          ${UI.riskBadge(emp.risk_level)}
        </td>
        <td>
          ${
            emp.is_blocked
              ? '<span class="badge badge-blocked">Blocked</span>'
              : emp.is_logged_in
                ? '<span class="badge badge-active">Active</span>'
                : '<span class="badge" style="background:var(--bg-secondary);color:var(--text-muted);border:1px solid var(--border)">Offline</span>'
          }
        </td>
        <td style="color:var(--text-muted);font-size:.85rem">${UI.formatDate(emp.last_activity)}</td>
        <td>
          <div class="table-actions">
            <a href="/admin/employee/${emp.user_id}" class="btn btn-sm btn-primary">View</a>
            <button class="btn btn-sm btn-warning" data-action="logout" data-emp-id="${emp.user_id}">
              Logout
            </button>
            ${
              emp.is_blocked
                ? `<button class="btn btn-sm btn-success" data-action="unblock" data-emp-id="${emp.user_id}">Unblock</button>`
                : `<button class="btn btn-sm btn-danger"  data-action="block"   data-emp-id="${emp.user_id}">Block</button>`
            }
          </div>
        </td>
      </tr>`,
      )
      .join("");

    // Event delegation for action buttons — avoids interpolating names into onclick strings
    tbody.querySelectorAll("[data-action]").forEach((btn) => {
      btn.addEventListener("click", () => {
        const empId = parseInt(btn.dataset.empId, 10);
        const emp = this.employees.find((e) => e.user_id === empId);
        const name = emp ? emp.name : `Employee ${empId}`;
        const action = btn.dataset.action;
        if (action === "block") this.block(empId, name);
        if (action === "unblock") this.unblock(empId, name);
        if (action === "logout") this.forceLogout(empId, name);
      });
    });
  },

  bindFilters() {
    const search = document.getElementById("searchInput");
    const dept = document.getElementById("deptFilter");
    const risk = document.getElementById("riskFilter");

    const applyFilters = () => {
      let list = [...this.employees];
      const q = (search?.value || "").toLowerCase();
      const d = dept?.value || "";
      const r = risk?.value || "";

      if (q)
        list = list.filter(
          (e) =>
            e.name.toLowerCase().includes(q) ||
            e.email.toLowerCase().includes(q),
        );
      if (d) list = list.filter((e) => e.department === d);
      if (r) list = list.filter((e) => e.risk_level === r);

      this.filtered = list;
      this.renderTable();
    };

    search?.addEventListener("input", applyFilters);
    dept?.addEventListener("change", applyFilters);
    risk?.addEventListener("change", applyFilters);
  },

  bindRefresh() {
    const btn = document.getElementById("refreshBtn");
    btn?.addEventListener("click", async () => {
      btn.disabled = true;
      await this.loadStats();
      await this.loadEmployees();
      btn.disabled = false;
      Toast.success("Dashboard refreshed");
    });
  },

  async block(empId, name) {
    const ok = await UI.confirm(
      `Block ${name}? Their sessions will be terminated.`,
      "Block Employee",
    );
    if (!ok) return;
    const res = await API.post(`/admin/employee/${empId}/block`, {});
    if (res && res.ok) {
      Toast.success(`${name} has been blocked`);
      await this.loadEmployees();
    } else {
      Toast.error(res?.data?.error || "Failed to block employee");
    }
  },

  async unblock(empId, name) {
    const ok = await UI.confirm(`Unblock ${name}?`, "Unblock Employee");
    if (!ok) return;
    const res = await API.post(`/admin/employee/${empId}/unblock`, {});
    if (res && res.ok) {
      Toast.success(`${name} has been unblocked`);
      await this.loadEmployees();
    } else {
      Toast.error(res?.data?.error || "Failed to unblock employee");
    }
  },

  async forceLogout(empId, name) {
    const ok = await UI.confirm(
      `Force logout ${name}? All sessions will be terminated.`,
      "Force Logout",
    );
    if (!ok) return;
    const res = await API.post(`/admin/employee/${empId}/force-logout`, {});
    if (res && res.ok) {
      Toast.success(`${name} has been logged out`);
    } else {
      Toast.error(res?.data?.error || "Failed to force logout");
    }
  },
};

/* ============================================================
   Admin Employee Profile
   ============================================================ */
const AdminEmployeeProfile = {
  empId: null,

  async init(empId) {
    if (!Auth.requireAuth("admin")) return;
    this.empId = empId;
    await this.loadProfile();
  },

  async loadProfile() {
    UI.showLoading("profileContent");
    const res = await API.get(`/admin/employee/${this.empId}`);
    if (!res || !res.ok) {
      UI.showError("profileContent", "Failed to load employee profile");
      return;
    }
    const p = res.data.data;
    this.renderProfile(p);
    this.renderTimeline(p.recent_activities || []);
    await this.loadRiskChart();
  },

  renderProfile(p) {
    const el = document.getElementById("profileContent");
    if (!el) return;
    el.innerHTML = ""; // clear loading

    // Header
    document.getElementById("empName") &&
      (document.getElementById("empName").textContent = p.name);
    document.getElementById("empEmail") &&
      (document.getElementById("empEmail").textContent = p.email);
    document.getElementById("empDept") &&
      (document.getElementById("empDept").textContent =
        `${p.department} · ${p.job_title}`);
    document.getElementById("empStatus") &&
      (document.getElementById("empStatus").innerHTML = p.is_blocked
        ? '<span class="badge badge-blocked">Blocked</span>'
        : p.is_logged_in
          ? '<span class="badge badge-active">Active</span>'
          : '<span class="badge" style="background:var(--bg-secondary);color:var(--text-muted);border:1px solid var(--border)">Offline</span>');
    document.getElementById("empAvatarLetter") &&
      (document.getElementById("empAvatarLetter").textContent = (p.name ||
        "U")[0].toUpperCase());

    // Block/Unblock button
    const blockBtn = document.getElementById("blockBtn");
    if (blockBtn) {
      if (p.is_blocked) {
        blockBtn.textContent = "🔓 Unblock";
        blockBtn.className = "btn btn-success";
        blockBtn.onclick = () => this.unblock(p.user_id, p.name);
      } else {
        blockBtn.textContent = "🔒 Block";
        blockBtn.className = "btn btn-danger";
        blockBtn.onclick = () => this.block(p.user_id, p.name);
      }
    }

    // Risk breakdown bars
    const rp = p.risk_profile || {};
    this.setRiskBar("barOverall", rp.overall_score);
    this.setRiskBar("barPhishing", rp.phishing_score);
    this.setRiskBar("barOffHours", rp.off_hours_score);
    this.setRiskBar("barPrivilege", rp.privilege_score);
    this.setRiskBar("barAccess", rp.access_score);
    this.setRiskBar("barFailed", rp.failed_login_score);
    this.setRiskBar("barFreq", rp.frequency_score);

    // Overall badge
    const badgeEl = document.getElementById("riskLevelBadge");
    if (badgeEl) badgeEl.innerHTML = UI.riskBadge(rp.risk_level || "low");

    // Phishing link clicks
    this.renderLinkClicks(p.link_clicks || []);
  },

  setRiskBar(id, score) {
    const wrapper = document.getElementById(id);
    if (!wrapper) return;
    const pctVal = UI.pct(score);
    const level =
      score >= 0.75
        ? "critical"
        : score >= 0.5
          ? "high"
          : score >= 0.25
            ? "medium"
            : "low";
    wrapper.innerHTML = `
      <div class="risk-bar">
        <div class="risk-bar-fill ${level}" style="width:${pctVal}%"></div>
      </div>
      <span class="risk-score-text" style="color:${UI.riskColor(score)}">${pctVal}%</span>`;
  },

  renderTimeline(activities) {
    const el = document.getElementById("activityTimeline");
    if (!el) return;
    if (!activities.length) {
      el.innerHTML = '<p class="text-muted">No recent activity</p>';
      return;
    }
    const suspicious = new Set([
      "link_clicked",
      "privilege_escalation",
      "failed_login",
      "data_export",
    ]);
    el.innerHTML = activities
      .map((a) => {
        const cls = suspicious.has(a.activity_type) ? "suspicious" : "success";
        return `
        <div class="timeline-item ${cls}">
          <div class="timeline-time">${UI.formatDate(a.timestamp)}</div>
          <div class="timeline-desc">
            ${a.description || a.activity_type}
            ${
              a.activity_type === "link_clicked" && a.metadata?.response_time_ms
                ? `<span class="badge badge-high" style="margin-left:.4rem">⏱ ${UI.formatMs(a.metadata.response_time_ms)}</span>`
                : ""
            }
          </div>
        </div>`;
      })
      .join("");
  },

  renderLinkClicks(clicks) {
    const el = document.getElementById("linkClicksSection");
    if (!el) return;
    if (!clicks.length) {
      el.innerHTML =
        '<p class="text-muted">No phishing link clicks recorded</p>';
      return;
    }
    el.innerHTML = clicks
      .map((c) => {
        const ms = c.metadata?.response_time_ms;
        const speed =
          ms != null
            ? ms < 3000
              ? "🔴 Very fast"
              : ms < 10000
                ? "🟡 Moderate"
                : "🟢 Slow"
            : "—";
        return `
        <div class="task-item">
          <span style="font-size:1.2rem">🎣</span>
          <div style="flex:1">
            <div style="font-size:.85rem;color:var(--text-primary)">${UI.formatDate(c.timestamp)}</div>
            <div style="font-size:.8rem;color:var(--text-muted)">${c.metadata?.url || "Unknown link"}</div>
          </div>
          <div style="text-align:right">
            <div style="font-weight:600;color:var(--alert)">${UI.formatMs(ms)}</div>
            <div style="font-size:.78rem;color:var(--text-muted)">${speed}</div>
          </div>
        </div>`;
      })
      .join("");
  },

  async loadRiskChart() {
    const res = await API.get(`/admin/employee/${this.empId}/risk-profile`);
    if (!res || !res.ok) return;
    const { risk_profile, trend } = res.data.data;
    Charts.renderRiskBreakdown("riskBreakdownChart", risk_profile);
    Charts.renderRiskTrend("riskTrendChart", trend);
  },

  async block(empId, name) {
    const ok = await UI.confirm(`Block ${name}?`, "Block Employee");
    if (!ok) return;
    const res = await API.post(`/admin/employee/${empId}/block`, {});
    if (res && res.ok) {
      Toast.success("Employee blocked");
      location.reload();
    } else Toast.error(res?.data?.error || "Failed");
  },

  async unblock(empId, name) {
    const ok = await UI.confirm(`Unblock ${name}?`, "Unblock Employee");
    if (!ok) return;
    const res = await API.post(`/admin/employee/${empId}/unblock`, {});
    if (res && res.ok) {
      Toast.success("Employee unblocked");
      location.reload();
    } else Toast.error(res?.data?.error || "Failed");
  },

  async forceLogout(empId) {
    const ok = await UI.confirm("Force logout this employee?", "Force Logout");
    if (!ok) return;
    const res = await API.post(`/admin/employee/${empId}/force-logout`, {});
    if (res && res.ok) Toast.success("Employee logged out");
    else Toast.error(res?.data?.error || "Failed");
  },
};

/* ============================================================
   Admin Reports
   ============================================================ */
const AdminReports = {
  async init() {
    if (!Auth.requireAuth("admin")) return;
    const form = document.getElementById("reportForm");
    form?.addEventListener("submit", async (e) => {
      e.preventDefault();
      await this.generate();
    });
  },

  async generate() {
    const reportType = document.getElementById("reportType")?.value;
    const startDate = document.getElementById("startDate")?.value;
    const endDate = document.getElementById("endDate")?.value;
    const empId = document.getElementById("employeeId")?.value;
    const dept = document.getElementById("department")?.value;

    const btn = document.getElementById("generateBtn");
    if (btn) {
      btn.disabled = true;
      btn.textContent = "Generating…";
    }

    const body = { report_type: reportType };
    if (startDate) body.start_date = startDate;
    if (endDate) body.end_date = endDate;
    if (empId) body.employee_id = parseInt(empId);
    if (dept) body.department = dept;

    const res = await API.post("/admin/reports/generate", body);
    if (btn) {
      btn.disabled = false;
      btn.textContent = "Generate Report";
    }

    if (!res || !res.ok) {
      Toast.error(res?.data?.error || "Failed to generate report");
      return;
    }

    this.displayReport(res.data.data.report);
    Toast.success("Report generated");
  },

  displayReport(report) {
    const el = document.getElementById("reportOutput");
    if (!el) return;
    el.style.display = "block";
    el.innerHTML = `
      <div class="card-header">
        <span class="card-title">Report Output</span>
        <button class="btn btn-sm btn-success" onclick="AdminReports.downloadReport()">⬇ Download JSON</button>
      </div>
      <pre style="font-size:.82rem;overflow:auto;max-height:500px;color:var(--text-primary)">${JSON.stringify(report, null, 2)}</pre>`;
    this._lastReport = report;
  },

  downloadReport() {
    if (!this._lastReport) return;
    const blob = new Blob([JSON.stringify(this._lastReport, null, 2)], {
      type: "application/json",
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `insider-sentinel-report-${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  },
};

window.AdminDashboard = AdminDashboard;
window.AdminEmployeeProfile = AdminEmployeeProfile;
window.AdminReports = AdminReports;
