/**
 * Insider Sentinel — charts.js
 * Plotly.js-based visualization helpers.
 */

const Charts = {
  /**
   * Render a risk heatmap.
   * @param {string} containerId  - DOM element id
   * @param {Array}  heatmapData  - array from /api/admin/heatmap-data
   */
  renderHeatmap(containerId, heatmapData) {
    if (!window.Plotly) { console.warn('Plotly not loaded'); return; }
    if (!heatmapData || !heatmapData.length) {
      document.getElementById(containerId).innerHTML =
        '<p class="text-center text-muted mt-3">No heatmap data available</p>';
      return;
    }

    const categories = ['Phishing', 'Off-Hours', 'Privilege', 'Access', 'Failed Login', 'Frequency'];
    const names = heatmapData.map(d => d.name);
    const z = heatmapData.map(d => [
      d.phishing, d.off_hours, d.privilege, d.access, d.failed_login, d.frequency,
    ]);

    const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
    const paperBg = isDark ? '#1e2a3b' : '#ffffff';
    const plotBg  = isDark ? '#1e2a3b' : '#ffffff';
    const fontColor = isDark ? '#e2e8f0' : '#1a202c';

    Plotly.newPlot(containerId, [{
      type: 'heatmap',
      z,
      x: categories,
      y: names,
      colorscale: [
        [0,    '#38a169'],
        [0.25, '#d69e2e'],
        [0.5,  '#e53e3e'],
        [1,    '#c53030'],
      ],
      zmin: 0,
      zmax: 1,
      hoverongaps: false,
      colorbar: {
        title: 'Risk Score',
        titlefont: { color: fontColor },
        tickfont:  { color: fontColor },
      },
    }], {
      paper_bgcolor: paperBg,
      plot_bgcolor:  plotBg,
      margin: { l: 130, r: 20, t: 20, b: 80 },
      font: { color: fontColor, family: 'Inter, sans-serif', size: 12 },
      xaxis: { tickangle: -30 },
      yaxis: { automargin: true },
    }, { responsive: true, displayModeBar: false });
  },

  /**
   * Render a bar chart of risk factor breakdown for one employee.
   */
  renderRiskBreakdown(containerId, riskProfile) {
    if (!window.Plotly || !riskProfile) return;

    const categories = ['Phishing', 'Off-Hours', 'Privilege', 'Access', 'Failed Login', 'Frequency'];
    const values = [
      riskProfile.phishing_score,
      riskProfile.off_hours_score,
      riskProfile.privilege_score,
      riskProfile.access_score,
      riskProfile.failed_login_score,
      riskProfile.frequency_score,
    ];

    const colors = values.map(v =>
      v >= 0.75 ? '#c53030' :
      v >= 0.5  ? '#e53e3e' :
      v >= 0.25 ? '#d69e2e' : '#38a169'
    );

    const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
    const paperBg = isDark ? '#1e2a3b' : '#ffffff';
    const fontColor = isDark ? '#e2e8f0' : '#1a202c';

    Plotly.newPlot(containerId, [{
      type: 'bar',
      x: categories,
      y: values,
      marker: { color: colors },
      text: values.map(v => (v * 100).toFixed(0) + '%'),
      textposition: 'outside',
    }], {
      paper_bgcolor: paperBg,
      plot_bgcolor:  paperBg,
      margin: { l: 40, r: 20, t: 20, b: 80 },
      font: { color: fontColor, family: 'Inter, sans-serif', size: 12 },
      yaxis: { range: [0, 1.1], tickformat: '.0%' },
      xaxis: { tickangle: -20 },
    }, { responsive: true, displayModeBar: false });
  },

  /**
   * Render a risk score trend line chart.
   */
  renderRiskTrend(containerId, trendData) {
    if (!window.Plotly || !trendData || !trendData.length) return;

    const dates  = trendData.map(d => d.date);
    const scores = trendData.map(d => d.overall_score);

    const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
    const paperBg = isDark ? '#1e2a3b' : '#ffffff';
    const fontColor = isDark ? '#e2e8f0' : '#1a202c';

    Plotly.newPlot(containerId, [{
      type: 'scatter',
      mode: 'lines+markers',
      x: dates,
      y: scores,
      line:   { color: '#3182ce', width: 2 },
      marker: { size: 6, color: '#3182ce' },
    }], {
      paper_bgcolor: paperBg,
      plot_bgcolor:  paperBg,
      margin: { l: 50, r: 20, t: 20, b: 60 },
      font: { color: fontColor, family: 'Inter, sans-serif', size: 12 },
      yaxis: { range: [0, 1], tickformat: '.0%', title: 'Risk Score' },
      xaxis: { title: 'Date' },
    }, { responsive: true, displayModeBar: false });
  },

  /**
   * Render activity type distribution as a donut chart.
   */
  renderActivityDonut(containerId, activities) {
    if (!window.Plotly || !activities || !activities.length) return;

    const counts = {};
    activities.forEach(a => {
      counts[a.activity_type] = (counts[a.activity_type] || 0) + 1;
    });

    const labels = Object.keys(counts);
    const values = Object.values(counts);

    const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
    const paperBg = isDark ? '#1e2a3b' : '#ffffff';
    const fontColor = isDark ? '#e2e8f0' : '#1a202c';

    Plotly.newPlot(containerId, [{
      type: 'pie',
      hole: 0.5,
      labels,
      values,
      textinfo: 'label+percent',
      textfont: { size: 11 },
    }], {
      paper_bgcolor: paperBg,
      margin: { l: 20, r: 20, t: 20, b: 20 },
      font: { color: fontColor, family: 'Inter, sans-serif', size: 12 },
      showlegend: false,
    }, { responsive: true, displayModeBar: false });
  },

  /** Re-render all charts on dark mode change */
  onThemeChange() {
    // Charts will be re-rendered on next page load or explicitly by each page's code
  },
};

window.Charts = Charts;
