/**
 * Insider Sentinel - Admin-specific JavaScript
 * Handles admin dashboard functionality
 */

class AdminDashboard {
    constructor() {
        this.token = localStorage.getItem('token');
        this.user = getCurrentUser();
        this.employees = [];
        this.refreshInterval = null;
        
        if (!this.token || this.user.role !== 'admin') {
            redirectTo('/');
        }
    }

    async init() {
        this.setupEventListeners();
        await this.loadDashboard();
        
        // Auto-refresh every 30 seconds
        this.refreshInterval = setInterval(() => this.loadDashboard(), 30000);
    }

    setupEventListeners() {
        // Search and filter
        const searchInput = document.getElementById('searchInput');
        if (searchInput) {
            searchInput.addEventListener('input', 
                debounce(() => this.filterEmployees(), 300)
            );
        }

        const filterSelect = document.getElementById('filterRisk');
        if (filterSelect) {
            filterSelect.addEventListener('change', () => this.filterEmployees());
        }

        // Logout button
        const logoutBtn = document.getElementById('logoutBtn');
        if (logoutBtn) {
            logoutBtn.addEventListener('click', () => this.logout());
        }

        // Display admin name
        const adminName = document.getElementById('adminName');
        if (adminName) {
            adminName.textContent = `Admin: ${this.user.name}`;
        }
    }

    async loadDashboard() {
        try {
            // Load stats
            const dashboardData = await api.get('/admin/dashboard');
            if (dashboardData) {
                this.updateStats(dashboardData);
            }

            // Load employees
            const employeesData = await api.get('/admin/employees');
            if (employeesData) {
                this.employees = employeesData.employees || [];
                this.displayEmployees(this.employees);
            }

            // Load heatmap
            const heatmapData = await api.get('/admin/heatmap-data');
            if (heatmapData) {
                this.renderHeatmap(heatmapData);
            }
        } catch (error) {
            console.error('Dashboard load error:', error);
        }
    }

    updateStats(data) {
        const elements = {
            'totalEmployees': data.total_employees,
            'highRiskCount': data.high_risk_count,
            'activeSessions': data.active_sessions
        };

        for (const [id, value] of Object.entries(elements)) {
            const el = document.getElementById(id);
            if (el) el.textContent = value || 0;
        }
    }

    displayEmployees(employees) {
        const tbody = document.getElementById('employeesTableBody');
        if (!tbody) return;

        tbody.innerHTML = '';

        employees.forEach(emp => {
            const row = document.createElement('tr');
            const riskLevel = getRiskLevel(emp.risk_score);
            const riskColor = getRiskColor(emp.risk_score);

            row.innerHTML = `
                <td><strong>${emp.name}</strong></td>
                <td>${emp.department || 'N/A'}</td>
                <td>
                    <span style="color: ${riskColor}; font-weight: bold;">
                        ${formatPercent(emp.risk_score)}
                    </span>
                </td>
                <td>
                    <span class="risk-badge ${riskLevel.toLowerCase()}">
                        ${riskLevel}
                    </span>
                </td>
                <td>${formatDate(emp.last_activity)}</td>
                <td>
                    <button class="btn-small" onclick="adminDashboard.viewProfile(${emp.user_id})">
                        Profile
                    </button>
                    <button class="btn-small btn-danger" onclick="adminDashboard.blockEmployee(${emp.user_id})">
                        Block
                    </button>
                </td>
            `;
            tbody.appendChild(row);
        });
    }

    filterEmployees() {
        const searchTerm = document.getElementById('searchInput')?.value.toLowerCase() || '';
        const riskFilter = document.getElementById('filterRisk')?.value || '';

        const filtered = this.employees.filter(emp => {
            const matchesSearch = emp.name.toLowerCase().includes(searchTerm) ||
                                emp.email.toLowerCase().includes(searchTerm) ||
                                emp.department.toLowerCase().includes(searchTerm);

            const matchesRisk = !riskFilter || getRiskLevel(emp.risk_score).toLowerCase() === riskFilter;

            return matchesSearch && matchesRisk;
        });

        this.displayEmployees(filtered);
    }

    renderHeatmap(data) {
        const container = document.getElementById('heatmapChart');
        if (!container || typeof Plotly === 'undefined') return;

        try {
            const trace = {
                z: data.risk_matrix || [],
                type: 'heatmap',
                colorscale: 'RdYlGn_r',
                colorbar: {
                    title: 'Risk Score'
                }
            };

            const layout = {
                title: 'Employee Risk Heatmap',
                xaxis: { title: 'Time Period' },
                yaxis: { title: 'Employees' },
                height: 400
            };

            Plotly.newPlot(container, [trace], layout, { responsive: true });
        } catch (error) {
            console.error('Heatmap render error:', error);
        }
    }

    async viewProfile(empId) {
        redirectTo(`/admin/employee/${empId}`);
    }

    async blockEmployee(empId) {
        if (!confirm('Are you sure you want to block this employee?')) return;

        const result = await api.post(`/admin/employee/${empId}/block`, {});
        if (result && result.success) {
            showToast('Employee blocked successfully', 'success');
            await this.loadDashboard();
        }
    }

    logout() {
        clearInterval(this.refreshInterval);
        api.logout();
    }

    destroy() {
        clearInterval(this.refreshInterval);
    }
}

// Initialize on page load
let adminDashboard;
document.addEventListener('DOMContentLoaded', () => {
    if (requireAuth('admin')) {
        adminDashboard = new AdminDashboard();
        adminDashboard.init();
    }
});

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (adminDashboard) {
        adminDashboard.destroy();
    }
});
