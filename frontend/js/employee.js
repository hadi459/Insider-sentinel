/**
 * Insider Sentinel — employee.js
 * Employee portal: tasks, chat simulation, phishing link tracking.
 */

/** Escape HTML special characters to prevent XSS. */
function escHtml(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

/* ============================================================
   Employee Dashboard
   ============================================================ */
const EmployeeDashboard = {
  tasks:          [],
  completedTasks: new Set(),
  chatInterval:   null,
  phishInterval:  null,
  _phishTimestamp: null,  // when the current phishing link appeared

  // Simulated chat participants
  CHATTERS: ['Alex (IT)', 'Sarah (HR)', 'Mike (Finance)', 'Bot 🤖'],

  CHAT_MESSAGES: [
    "Hey, did you check the updated Q4 report?",
    "The server maintenance is scheduled for tonight.",
    "Can you review the PR I just sent?",
    "Don't forget the all-hands meeting at 3 PM.",
    "The deployment went smoothly. ✅",
    "Please submit your timesheets by EOD.",
    "Has anyone seen the new security guidelines?",
    "Coffee machine is broken again 😢",
    "The new firewall rules are now active.",
    "Reminder: password rotation is due this week.",
  ],

  PHISHING_LINKS: [
    { url: "http://secure-update.xyz/login", text: "⚠️ Your account needs verification. Click here to verify now." },
    { url: "http://payroll-portal.net/claim", text: "💰 Your bonus is ready! Click to claim your $500 reward." },
    { url: "http://it-support.help/fix", text: "🔧 IT Support: Action required — click to fix security issue." },
    { url: "http://sharepoint-docs.co/view", text: "📄 Someone shared a confidential document with you." },
  ],

  BROWSER_PAGES: [
    { url: "https://intranet.company.local/home",    title: "Company Intranet",    content: "Welcome to the company intranet. Check announcements, HR policies, and internal resources." },
    { url: "https://intranet.company.local/projects", title: "Project Dashboard", content: "Current projects: Q4 Budget Review, System Migration v2, Security Audit 2024. All on track." },
    { url: "https://intranet.company.local/hr",      title: "HR Portal",          content: "HR Policies · Benefits · Time-off requests · Performance reviews · Training calendar." },
  ],

  async init() {
    if (!Auth.requireAuth('employee')) return;
    await this.loadDashboard();
    await this.loadTasks();
    this.startChat();
    this.startPhishingSimulation();
    this.rotateBrowser();
    this.updateActivityStatus('Monitoring active — all interactions are being logged.');
  },

  async loadDashboard() {
    const res = await API.get('/employee/dashboard');
    if (!res || !res.ok) return;
    const d = res.data.data;

    // Greeting
    const greetEl = document.getElementById('greeting');
    if (greetEl) greetEl.textContent = `Hello, ${d.name} 👋`;

    const deptEl = document.getElementById('empDept');
    if (deptEl) deptEl.textContent = `${d.department} · ${d.job_title}`;

    const riskEl = document.getElementById('myRiskScore');
    if (riskEl) riskEl.innerHTML = `Risk Level: ${UI.riskBadge(d.risk_level)}`;

    if (d.is_blocked) {
      Toast.error('Your account has been suspended. Contact your administrator.', 8000);
    }
  },

  async loadTasks() {
    const res = await API.get('/employee/tasks');
    if (!res || !res.ok) return;
    this.tasks = res.data.data.tasks || [];
    this.renderTasks();
  },

  renderTasks() {
    const el = document.getElementById('taskList');
    if (!el) return;
    if (!this.tasks.length) {
      el.innerHTML = '<p class="text-muted">No tasks assigned.</p>';
      return;
    }
    el.innerHTML = this.tasks.map(t => {
      const done = this.completedTasks.has(t.task_id);
      return `
        <div class="task-item ${done ? 'completed' : ''}" id="task-${t.task_id}">
          <div class="task-priority ${t.priority}"></div>
          <span class="task-title">${t.title}</span>
          <span class="task-time">${t.priority}</span>
          ${!done
            ? `<button class="btn btn-sm btn-success" onclick="EmployeeDashboard.completeTask(${t.task_id}, '${t.title.replace(/'/g,'\\\'')}')" >✔ Done</button>`
            : '<span class="badge badge-active">Completed</span>'}
        </div>`;
    }).join('');
  },

  async completeTask(taskId, taskTitle) {
    this.completedTasks.add(taskId);
    this.renderTasks();
    const res = await API.post('/employee/task/complete', { task_id: taskId, task_title: taskTitle });
    if (res && res.ok) {
      Toast.success(`Task completed: ${taskTitle}`);
      this.updateActivityStatus(`Logged: Task completion — ${taskTitle}`);
    } else {
      Toast.error('Failed to log task');
    }
  },

  // -- Chat Simulation ---------------------------------------------------------

  startChat() {
    this.addSystemMessage('Welcome to internal chat. Messages are monitored for security compliance.');
    // Messages every 5–10 seconds
    const scheduleMessage = () => {
      const delay = (5 + Math.random() * 5) * 1000;
      this.chatInterval = setTimeout(async () => {
        this.addChatMessage();
        await this.logChatActivity();
        scheduleMessage();
      }, delay);
    };
    scheduleMessage();
  },

  addSystemMessage(text) {
    const el = document.getElementById('chatMessages');
    if (!el) return;
    const div = document.createElement('div');
    div.style.cssText = 'text-align:center;font-size:.78rem;color:var(--text-muted);margin:.5rem 0';
    div.textContent = text;
    el.appendChild(div);
    el.scrollTop = el.scrollHeight;
  },

  addChatMessage(isPhishing = false, phishData = null) {
    const el = document.getElementById('chatMessages');
    if (!el) return;

    const sender = this.CHATTERS[Math.floor(Math.random() * this.CHATTERS.length)];
    const now    = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    const div    = document.createElement('div');

    if (isPhishing && phishData) {
      this._phishTimestamp = Date.now();
      div.className = 'chat-message phishing';
      div.innerHTML = `
        <div class="sender">⚠️ ${sender} <span style="font-size:.7rem;opacity:.6">${now}</span></div>
        <div>${phishData.text}</div>
        <div style="margin-top:.4rem">
          <span class="phishing-link" data-url="${phishData.url}" onclick="EmployeeDashboard.handlePhishClick(this, '${phishData.url}')">
            🔗 ${phishData.url}
          </span>
        </div>
        <div class="link-timer" id="phishTimer-${Date.now()}"></div>`;
      // Countdown display
      let secs = 0;
      const timerId = div.querySelector('[id^="phishTimer-"]');
      const tick = setInterval(() => {
        secs++;
        if (timerId) timerId.textContent = `⏱ ${secs}s since link appeared`;
      }, 1000);
      div._timerInterval = tick;
    } else {
      const text = this.CHAT_MESSAGES[Math.floor(Math.random() * this.CHAT_MESSAGES.length)];
      div.className = 'chat-message received';
      div.innerHTML = `
        <div class="sender">${sender} <span style="font-size:.7rem;opacity:.6">${now}</span></div>
        <div>${text}</div>`;
    }

    el.appendChild(div);
    el.scrollTop = el.scrollHeight;
  },

  async handlePhishClick(linkEl, url) {
    const responseMs = this._phishTimestamp ? Date.now() - this._phishTimestamp : null;
    linkEl.style.pointerEvents = 'none';
    linkEl.style.opacity = '0.5';

    // Log to backend
    const res = await API.post('/employee/link-clicked', { url, response_time_ms: responseMs });
    if (res && res.ok) {
      Toast.warning(`⚠️ Phishing link click logged! Response time: ${UI.formatMs(responseMs)}`);
      this.updateActivityStatus(`⚠️ ALERT: Phishing link clicked — response time ${UI.formatMs(responseMs)}`);
    }

    // Show feedback in chat
    const feedbackDiv = document.createElement('div');
    feedbackDiv.className = 'chat-message received';
    feedbackDiv.style.borderLeft = '3px solid var(--alert)';
    feedbackDiv.innerHTML = `
      <div class="sender">🔒 Security System</div>
      <div style="color:var(--alert)">⚠️ This was a simulated phishing test. Response time: <strong>${UI.formatMs(responseMs)}</strong>.</div>`;
    linkEl.closest('.chat-message').after(feedbackDiv);
    document.getElementById('chatMessages').scrollTop = 99999;
  },

  async logChatActivity() {
    await API.post('/employee/chat/message', { message: 'simulated chat interaction' });
    this.updateActivityStatus('Logging: chat activity');
  },

  // -- Phishing simulation ------------------------------------------------------

  startPhishingSimulation() {
    const schedulePhish = () => {
      const delay = (30 + Math.random() * 30) * 1000;
      this.phishInterval = setTimeout(() => {
        const link = this.PHISHING_LINKS[Math.floor(Math.random() * this.PHISHING_LINKS.length)];
        this.addChatMessage(true, link);
        this.updateActivityStatus('⚠️ Simulated phishing link sent to chat');
        schedulePhish();
      }, delay);
    };
    schedulePhish();
  },

  // -- Browser rotation ---------------------------------------------------------

  rotateBrowser() {
    let idx = 0;
    const urlBar     = document.getElementById('browserUrl');
    const content    = document.getElementById('browserContent');
    const titleEl    = document.getElementById('browserTitle');

    const updateBrowser = () => {
      const page = this.BROWSER_PAGES[idx % this.BROWSER_PAGES.length];
      if (urlBar)   urlBar.textContent   = page.url;
      if (titleEl)  titleEl.textContent  = page.title;
      if (content)  content.innerHTML    = `
        <h4 style="margin-bottom:.75rem">${page.title}</h4>
        <p style="color:var(--text-secondary);font-size:.9rem">${page.content}</p>
        <div style="margin-top:1rem;display:flex;gap:.5rem;flex-wrap:wrap">
          <span class="badge badge-active">Internal</span>
          <span class="badge badge-low">Secure</span>
          <span class="badge badge-medium">Intranet Only</span>
        </div>`;
      idx++;
    };

    updateBrowser();
    setInterval(updateBrowser, 15000);
  },

  // -- Status bar ---------------------------------------------------------------

  updateActivityStatus(msg) {
    const el = document.getElementById('activityStatusMsg');
    if (el) el.textContent = msg;
  },

  // -- Manual send chat ---------------------------------------------------------

  async sendChatMessage() {
    const input = document.getElementById('chatInput');
    if (!input || !input.value.trim()) return;
    const text = input.value.trim();
    input.value = '';

    // Render as sent
    const el  = document.getElementById('chatMessages');
    const div = document.createElement('div');
    div.className = 'chat-message sent';
    div.innerHTML = `
      <div class="sender">You <span style="font-size:.7rem;opacity:.6">${new Date().toLocaleTimeString([], {hour:'2-digit',minute:'2-digit'})}</span></div>
      <div>${text}</div>`;
    el.appendChild(div);
    el.scrollTop = el.scrollHeight;

    await API.post('/employee/chat/message', { message: text });
    this.updateActivityStatus('Logged: chat message sent');
  },
};

/* ============================================================
   Employee Activity Log
   ============================================================ */
const EmployeeActivityLog = {
  async init() {
    if (!Auth.requireAuth('employee')) return;
    await this.loadActivities();
    this.bindFilters();
  },

  async loadActivities(actType = '', limit = 50) {
    UI.showLoading('activityList');
    let path = `/employee/activity-log?limit=${limit}`;
    if (actType) path += `&type=${actType}`;

    const res = await API.get(path);
    if (!res || !res.ok) {
      UI.showError('activityList', 'Failed to load activities');
      return;
    }
    this.renderActivities(res.data.data.activities || []);
  },

  renderActivities(activities) {
    const el = document.getElementById('activityList');
    if (!el) return;
    if (!activities.length) {
      el.innerHTML = '<p class="text-center text-muted mt-3">No activities found.</p>';
      return;
    }
    const suspicious = new Set(['link_clicked', 'privilege_escalation', 'failed_login', 'data_export']);
    el.innerHTML = `<div class="timeline">` + activities.map(a => `
      <div class="timeline-item ${suspicious.has(a.activity_type) ? 'suspicious' : 'success'}">
        <div class="timeline-time">${UI.formatDate(a.timestamp)}</div>
        <div class="timeline-desc">
          <strong>${a.activity_type.replace(/_/g, ' ')}</strong>: ${a.description || '—'}
        </div>
      </div>`).join('') + `</div>`;
  },

  bindFilters() {
    const typeFilter = document.getElementById('typeFilter');
    typeFilter?.addEventListener('change', () => this.loadActivities(typeFilter.value));

    const exportBtn = document.getElementById('exportBtn');
    exportBtn?.addEventListener('click', () => this.exportActivities());
  },

  async exportActivities() {
    const res = await API.get('/employee/activity-log?limit=200');
    if (!res || !res.ok) { Toast.error('Export failed'); return; }
    const activities = res.data.data.activities || [];
    const csv = [
      'Timestamp,Type,Description',
      ...activities.map(a => `"${a.timestamp}","${a.activity_type}","${a.description.replace(/"/g,'""')}"`)
    ].join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url  = URL.createObjectURL(blob);
    const a    = document.createElement('a');
    a.href = url; a.download = 'my-activity-log.csv'; a.click();
    URL.revokeObjectURL(url);
  },
};

window.EmployeeDashboard   = EmployeeDashboard;
window.EmployeeActivityLog = EmployeeActivityLog;
