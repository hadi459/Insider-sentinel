# Insider Sentinel

**UI-Centric Insider Threat Monitoring and Behavioral Risk Analysis System**

A full-stack cybersecurity web application that monitors employee behaviour in real-time and surfaces risk scores through an intuitive admin dashboard.

---

## Architecture

```
User Login (Email)
  → JWT-based authentication
  → Role-based routing (Admin / Employee)
  → Admin:   Risk monitoring · Employee management · Reports
  → Employee: Simulated work environment · Activity logging
  → Activity data → Risk Analyzer Engine
  → Risk Scores  → Visualizations (heatmaps, charts, timelines)
```

## Tech Stack

| Layer       | Technology                      |
|-------------|---------------------------------|
| Backend     | Python 3.10+ · Flask · SQLite   |
| Frontend    | HTML5 · CSS3 · Vanilla JS       |
| Charts      | Plotly.js                       |
| Auth        | Token-based (Bearer JWT-style)  |

---

## Quick Start

### 1. Clone & Install

```bash
pip install -r requirements.txt
```

### 2. Initialize Database

```bash
python database_init.py
```

This seeds:
- 2 Admin accounts
- 8 Employee accounts (across 8 departments)
- Sample activity logs with initial risk scores

### 3. Start the Server

```bash
python app.py
```

Visit: **http://localhost:5000**

---

## Demo Credentials

| Role     | Email                  | Password   |
|----------|------------------------|------------|
| Admin    | admin1@insider.com     | Secure@123 |
| Admin    | admin2@insider.com     | Secure@123 |
| Employee | emp1@company.com       | Secure@123 |
| Employee | emp2–emp8@company.com  | Secure@123 |

---

## Features

### Admin Portal
- **Dashboard**: Total employees, high-risk count, active sessions, risk heatmap
- **Employee List**: Sortable/filterable table with risk scores and status
- **Employee Profile**: Per-factor risk breakdown, activity timeline, phishing click history
- **Actions**: Block / Unblock accounts, Force Logout sessions
- **Reports**: Generate downloadable reports (JSON / CSV)
- **Visualizations**: Plotly.js heatmaps, bar charts, trend lines

### Employee Portal
- **Simulated Work Environment**: Internal browser, task manager
- **Task Logging**: Complete tasks; each action is sent to the backend
- **Chat Interface**: Team messages appear every 5–10 seconds
- **Phishing Simulation**: Suspicious links appear every 30–60 seconds
- **Click Speed Tracking**: Millisecond-precision timer from link appearance to click
- **Activity Log**: Personal history with CSV export

### Risk Analyzer (6 Factors)

| Factor           | Weight | Description                                   |
|------------------|--------|-----------------------------------------------|
| Phishing         | 30%    | Link click speed (< 3 s = high risk)          |
| Privilege        | 25%    | Privilege escalation attempts                 |
| Off-Hours        | 15%    | Activity outside 08:00–20:00                  |
| Failed Logins    | 10%    | Authentication failure count                  |
| Data Access      | 10%    | Bulk file access / data exports               |
| Frequency        | 10%    | Abnormal activity rate (last 24 h)            |

### Dark Mode
- Global toggle stored in `localStorage`
- Smooth CSS transitions
- Applied via `[data-theme="dark"]` on the `<html>` element

---

## Project Structure

```
insider-sentinel/
├── backend/
│   ├── __init__.py
│   ├── models.py           # OOP class hierarchy
│   ├── database.py         # SQLite management
│   ├── risk_analyzer.py    # Behavioral scoring engine
│   ├── monitoring_system.py# Central controller
│   └── routes.py           # Flask RESTful API
├── frontend/
│   ├── index.html
│   ├── login.html
│   ├── admin_dashboard.html
│   ├── admin_employee_profile.html
│   ├── admin_reports.html
│   ├── employee_dashboard.html
│   ├── employee_activity_log.html
│   ├── css/
│   │   ├── style.css
│   │   ├── dark-mode.css
│   │   └── responsive.css
│   └── js/
│       ├── app.js          # API client, auth, toasts
│       ├── admin.js        # Admin UI logic
│       ├── employee.js     # Employee portal + simulations
│       └── charts.js       # Plotly.js helpers
├── database/               # Auto-created on first run
│   └── insider_sentinel.db
├── app.py                  # Flask entry point
├── database_init.py        # DB seed script
├── requirements.txt
└── README.md
```

---

## API Endpoints

### Authentication
| Method | Path               | Description              |
|--------|--------------------|--------------------------|
| POST   | /api/auth/login    | Email + password login   |
| POST   | /api/auth/logout   | Invalidate session       |
| GET    | /api/auth/verify   | Verify bearer token      |

### Admin
| Method | Path                                    | Description                    |
|--------|-----------------------------------------|--------------------------------|
| GET    | /api/admin/dashboard                    | Overview stats                 |
| GET    | /api/admin/employees                    | All employees + risk scores    |
| GET    | /api/admin/employee/\<id\>              | Full employee profile          |
| GET    | /api/admin/employee/\<id\>/activities   | Paginated activity log         |
| GET    | /api/admin/employee/\<id\>/risk-profile | Risk breakdown + trend         |
| POST   | /api/admin/employee/\<id\>/block        | Block account                  |
| POST   | /api/admin/employee/\<id\>/unblock      | Unblock account                |
| POST   | /api/admin/employee/\<id\>/force-logout | Terminate all sessions         |
| GET    | /api/admin/reports                      | Available report types         |
| POST   | /api/admin/reports/generate             | Generate custom report         |
| GET    | /api/admin/heatmap-data                 | Risk heatmap matrix data       |

### Employee
| Method | Path                        | Description                        |
|--------|-----------------------------|------------------------------------|
| GET    | /api/employee/dashboard     | Own dashboard data                 |
| GET    | /api/employee/tasks         | Simulated task list                |
| POST   | /api/employee/task/complete | Log task completion                |
| POST   | /api/employee/chat/message  | Log chat activity                  |
| POST   | /api/employee/link-clicked  | Log phishing click + response time |
| GET    | /api/employee/activity-log  | Personal activity history          |

### System
| Method | Path               | Description             |
|--------|--------------------|-------------------------|
| GET    | /api/system/health | Liveness check          |
| GET    | /api/system/stats  | System statistics       |

---

## Color Palette

| Token          | Hex       | Usage              |
|----------------|-----------|--------------------|
| Navy Blue      | `#1a2332` | Primary / Navbar   |
| Slate Gray     | `#4a5568` | Secondary          |
| White          | `#ffffff` | Background         |
| Alert Red      | `#e53e3e` | High-risk / Alerts |
| Success Green  | `#38a169` | Low-risk / OK      |
