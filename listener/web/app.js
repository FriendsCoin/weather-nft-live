// THE LISTENER - Dashboard JavaScript

// Configuration
const API_BASE = 'http://localhost:8000/api';
const WS_URL = 'ws://localhost:8765'; // Real-time neurofeedback WebSocket

// State
let currentView = 'overview';
let currentPage = 0;
let pageSize = 20;
let depthChart, qualityChart, progressChart;
let liveWs = null;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    initializeNavigation();
    initializeFilters();
    loadOverview();
    initializeCharts();
});

// ============================================================
// NAVIGATION
// ============================================================

function initializeNavigation() {
    const navButtons = document.querySelectorAll('.nav-btn');

    navButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const view = btn.dataset.view;
            switchView(view);

            // Update active nav button
            navButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
        });
    });
}

function switchView(view) {
    // Hide all views
    document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));

    // Show selected view
    document.getElementById(`${view}-view`).classList.add('active');

    currentView = view;

    // Load view data
    switch(view) {
        case 'overview':
            loadOverview();
            break;
        case 'sessions':
            loadSessions();
            break;
        case 'live':
            initializeLiveView();
            break;
        case 'gallery':
            loadGallery();
            break;
        case 'statistics':
            loadStatistics();
            break;
    }
}

// ============================================================
// OVERVIEW
// ============================================================

async function loadOverview() {
    try {
        // Load statistics
        const stats = await fetch(`${API_BASE}/statistics`).then(r => r.json());

        document.getElementById('total-sessions').textContent = stats.count || 0;
        document.getElementById('avg-depth').textContent = (stats.avg_depth || 0).toFixed(1);
        document.getElementById('avg-quality').textContent = (stats.avg_quality || 0).toFixed(1);
        document.getElementById('total-time').textContent = ((stats.total_minutes || 0) / 60).toFixed(1);

        // Load trends for charts
        const trends = await fetch(`${API_BASE}/statistics/trends?days=30`).then(r => r.json());
        updateDepthChart(trends.trends);
        updateQualityChart(trends.trends);

        // Load recent sessions
        const sessions = await fetch(`${API_BASE}/sessions?limit=5`).then(r => r.json());
        displayRecentSessions(sessions.sessions);

    } catch (error) {
        console.error('Error loading overview:', error);
    }
}

function displayRecentSessions(sessions) {
    const container = document.getElementById('recent-sessions-list');

    if (!sessions || sessions.length === 0) {
        container.innerHTML = '<p style="color: var(--text-muted);">No sessions yet</p>';
        return;
    }

    container.innerHTML = sessions.map(session => `
        <div class="session-card" onclick="showSessionDetail('${session.session_id}')">
            <div class="session-header">
                <span class="session-id">${session.session_id}</span>
                <span class="session-date">${formatDate(session.recorded_at)}</span>
            </div>
            <div class="session-metrics">
                <div class="session-metric">
                    <span class="session-metric-label">Depth</span>
                    <span class="session-metric-value">${(session.mean_depth || 0).toFixed(1)}</span>
                </div>
                <div class="session-metric">
                    <span class="session-metric-label">Quality</span>
                    <span class="session-metric-value">${(session.quality_score || 0).toFixed(1)}</span>
                </div>
            </div>
        </div>
    `).join('');
}

// ============================================================
// SESSIONS
// ============================================================

function initializeFilters() {
    // Apply filters button
    document.getElementById('apply-filters').addEventListener('click', () => {
        currentPage = 0;
        loadSessions();
    });

    // Clear filters button
    document.getElementById('clear-filters').addEventListener('click', () => {
        document.getElementById('filter-min-depth').value = '';
        document.getElementById('filter-min-quality').value = '';
        document.getElementById('filter-days').value = '';
        document.getElementById('filter-tag').value = '';
        currentPage = 0;
        loadSessions();
    });

    // Pagination
    document.getElementById('prev-page').addEventListener('click', () => {
        if (currentPage > 0) {
            currentPage--;
            loadSessions();
        }
    });

    document.getElementById('next-page').addEventListener('click', () => {
        currentPage++;
        loadSessions();
    });

    // Load tags for filter
    loadTags();
}

async function loadTags() {
    try {
        const data = await fetch(`${API_BASE}/tags`).then(r => r.json());
        const select = document.getElementById('filter-tag');

        data.tags.forEach(tag => {
            const option = document.createElement('option');
            option.value = tag.name;
            option.textContent = `${tag.name} (${tag.session_count})`;
            select.appendChild(option);
        });
    } catch (error) {
        console.error('Error loading tags:', error);
    }
}

async function loadSessions() {
    try {
        // Get filter values
        const minDepth = document.getElementById('filter-min-depth').value;
        const minQuality = document.getElementById('filter-min-quality').value;
        const days = document.getElementById('filter-days').value;
        const tag = document.getElementById('filter-tag').value;

        // Build query
        const params = new URLSearchParams({
            limit: pageSize,
            offset: currentPage * pageSize
        });

        if (minDepth) params.append('min_depth', minDepth);
        if (minQuality) params.append('min_quality', minQuality);
        if (days) params.append('days', days);
        if (tag) params.append('tag', tag);

        // Fetch sessions
        const data = await fetch(`${API_BASE}/sessions?${params}`).then(r => r.json());

        // Display sessions
        const container = document.getElementById('sessions-list');

        if (!data.sessions || data.sessions.length === 0) {
            container.innerHTML = '<p style="color: var(--text-muted);">No sessions found</p>';
            return;
        }

        container.innerHTML = data.sessions.map(session => `
            <div class="session-card" onclick="showSessionDetail('${session.session_id}')">
                <div class="session-header">
                    <span class="session-id">${session.session_id}</span>
                    <span class="session-date">${formatDate(session.recorded_at)}</span>
                </div>
                <div class="session-metrics">
                    <div class="session-metric">
                        <span class="session-metric-label">Depth</span>
                        <span class="session-metric-value">${(session.mean_depth || 0).toFixed(1)}</span>
                    </div>
                    <div class="session-metric">
                        <span class="session-metric-label">Quality</span>
                        <span class="session-metric-value">${(session.quality_score || 0).toFixed(1)}</span>
                    </div>
                    <div class="session-metric">
                        <span class="session-metric-label">Alpha</span>
                        <span class="session-metric-value">${(session.alpha_performance || 0).toFixed(2)}</span>
                    </div>
                    <div class="session-metric">
                        <span class="session-metric-label">Duration</span>
                        <span class="session-metric-value">${formatDuration(session.duration_seconds)}</span>
                    </div>
                </div>
                ${session.rating ? `<div style="text-align: center; margin-top: 0.5rem;">${'⭐'.repeat(session.rating)}</div>` : ''}
            </div>
        `).join('');

        // Update pagination
        document.getElementById('page-info').textContent = `Page ${currentPage + 1}`;

    } catch (error) {
        console.error('Error loading sessions:', error);
    }
}

// ============================================================
// LIVE VIEW
// ============================================================

function initializeLiveView() {
    if (liveWs && liveWs.readyState === WebSocket.OPEN) {
        return; // Already connected
    }

    connectLiveWebSocket();
}

function connectLiveWebSocket() {
    const statusIndicator = document.getElementById('live-status');
    const statusText = statusIndicator.querySelector('.status-text');

    statusText.textContent = 'Connecting...';

    try {
        liveWs = new WebSocket(WS_URL);

        liveWs.onopen = () => {
            statusIndicator.classList.add('connected');
            statusText.textContent = 'Connected';
        };

        liveWs.onmessage = (event) => {
            const state = JSON.parse(event.data);
            updateLiveDisplay(state);
        };

        liveWs.onerror = (error) => {
            console.error('WebSocket error:', error);
            statusText.textContent = 'Error';
        };

        liveWs.onclose = () => {
            statusIndicator.classList.remove('connected');
            statusText.textContent = 'Disconnected';

            // Try to reconnect after 5 seconds
            setTimeout(() => {
                if (currentView === 'live') {
                    connectLiveWebSocket();
                }
            }, 5000);
        };

    } catch (error) {
        console.error('Failed to connect WebSocket:', error);
        statusText.textContent = 'Connection failed';
    }
}

function updateLiveDisplay(state) {
    // Update circle size and color
    const circle = document.getElementById('live-circle');
    const depth = state.depth_smooth || 0;
    const alpha = state.alpha_smooth || 0;

    const size = 50 + (depth / 100) * 350; // 50-400px
    const hue = 240 - ((alpha + 2) / 4) * 180; // Blue to yellow

    circle.style.width = `${size}px`;
    circle.style.height = `${size}px`;
    circle.style.background = `hsl(${hue}, 80%, 60%)`;

    // Update message
    document.getElementById('live-message').textContent = state.state_message || 'Waiting...';

    // Update metrics
    document.getElementById('live-depth').textContent = (depth || 0).toFixed(1);
    document.getElementById('live-quality').textContent = (state.quality || 0).toFixed(1);
    document.getElementById('live-alpha').textContent = (state.alpha_performance || 0).toFixed(2);
    document.getElementById('live-beta').textContent = (state.beta_performance || 0).toFixed(2);
}

// ============================================================
// GALLERY
// ============================================================

async function loadGallery() {
    // TODO: Implement gallery loading from generated_outputs
    const container = document.getElementById('gallery-grid');
    container.innerHTML = '<p style="color: var(--text-muted);">Gallery feature coming soon!</p>';
}

// ============================================================
// STATISTICS
// ============================================================

async function loadStatistics() {
    // Time range buttons
    const timeButtons = document.querySelectorAll('.time-btn');
    timeButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const days = btn.dataset.days;
            timeButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            loadStatisticsForRange(days);
        });
    });

    // Load default (7 days)
    loadStatisticsForRange('7');
}

async function loadStatisticsForRange(days) {
    try {
        const params = days === 'all' ? '' : `?days=${days}`;
        const stats = await fetch(`${API_BASE}/statistics${params}`).then(r => r.json());

        // Display stats
        const container = document.getElementById('session-stats');
        container.innerHTML = `
            <p><strong>Sessions:</strong> ${stats.count}</p>
            <p><strong>Average Depth:</strong> ${(stats.avg_depth || 0).toFixed(1)}/100</p>
            <p><strong>Max Depth:</strong> ${(stats.max_depth || 0).toFixed(1)}/100</p>
            <p><strong>Average Quality:</strong> ${(stats.avg_quality || 0).toFixed(1)}/100</p>
            <p><strong>Total Time:</strong> ${((stats.total_minutes || 0) / 60).toFixed(1)} hours</p>
        `;

        // Load best sessions
        const best = await fetch(`${API_BASE}/statistics/best?limit=5`).then(r => r.json());
        const bestContainer = document.getElementById('best-sessions');
        bestContainer.innerHTML = best.sessions.map(s => `
            <div style="padding: 0.5rem; border-left: 3px solid var(--accent-primary); margin-bottom: 0.5rem;">
                <strong>${s.session_id}</strong><br>
                Depth: ${(s.mean_depth || 0).toFixed(1)} | Quality: ${(s.quality_score || 0).toFixed(1)}
            </div>
        `).join('');

    } catch (error) {
        console.error('Error loading statistics:', error);
    }
}

// ============================================================
// CHARTS
// ============================================================

function initializeCharts() {
    // Depth chart
    const depthCtx = document.getElementById('depth-chart').getContext('2d');
    depthChart = new Chart(depthCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Meditation Depth',
                data: [],
                borderColor: 'rgb(124, 77, 255)',
                backgroundColor: 'rgba(124, 77, 255, 0.1)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    labels: {
                        color: '#e8eaf6'
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    ticks: {
                        color: '#9fa8da'
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    }
                },
                x: {
                    ticks: {
                        color: '#9fa8da'
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    }
                }
            }
        }
    });

    // Quality chart
    const qualityCtx = document.getElementById('quality-chart').getContext('2d');
    qualityChart = new Chart(qualityCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Quality Score',
                data: [],
                borderColor: 'rgb(0, 230, 118)',
                backgroundColor: 'rgba(0, 230, 118, 0.1)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    labels: {
                        color: '#e8eaf6'
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    ticks: {
                        color: '#9fa8da'
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    }
                },
                x: {
                    ticks: {
                        color: '#9fa8da'
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    }
                }
            }
        }
    });
}

function updateDepthChart(trends) {
    if (!depthChart || !trends) return;

    const labels = trends.map(t => formatDate(t.date));
    const data = trends.map(t => t.avg_depth);

    depthChart.data.labels = labels;
    depthChart.data.datasets[0].data = data;
    depthChart.update();
}

function updateQualityChart(trends) {
    if (!qualityChart || !trends) return;

    const labels = trends.map(t => formatDate(t.date));
    const data = trends.map(t => t.avg_quality);

    qualityChart.data.labels = labels;
    qualityChart.data.datasets[0].data = data;
    qualityChart.update();
}

// ============================================================
// MODAL - SESSION DETAIL
// ============================================================

async function showSessionDetail(sessionId) {
    try {
        const session = await fetch(`${API_BASE}/sessions/${sessionId}`).then(r => r.json());

        const modal = document.getElementById('session-modal');
        const content = document.getElementById('session-detail');

        content.innerHTML = `
            <h2>${session.session_id}</h2>
            <p><strong>Date:</strong> ${formatDate(session.recorded_at)}</p>
            <p><strong>Duration:</strong> ${formatDuration(session.duration_seconds)}</p>
            <hr style="margin: 1rem 0; border-color: var(--bg-tertiary);">

            <h3>Metrics</h3>
            <p><strong>Depth:</strong> ${(session.mean_depth || 0).toFixed(1)}/100</p>
            <p><strong>Quality:</strong> ${(session.quality_score || 0).toFixed(1)}/100</p>
            <p><strong>Alpha Performance:</strong> ${(session.alpha_performance || 0).toFixed(2)}</p>
            <p><strong>Beta Performance:</strong> ${(session.beta_performance || 0).toFixed(2)}</p>

            ${session.mood_before ? `
                <hr style="margin: 1rem 0; border-color: var(--bg-tertiary);">
                <h3>Mood Change</h3>
                <p><strong>Stress:</strong> ${session.mood_before.stress} → ${session.mood_after?.stress || '?'}</p>
                <p><strong>Energy:</strong> ${session.mood_before.energy} → ${session.mood_after?.energy || '?'}</p>
                <p><strong>Happiness:</strong> ${session.mood_before.happiness} → ${session.mood_after?.happiness || '?'}</p>
                <p><strong>Focus:</strong> ${session.mood_before.focus} → ${session.mood_after?.focus || '?'}</p>
            ` : ''}

            ${session.journal ? `
                <hr style="margin: 1rem 0; border-color: var(--bg-tertiary);">
                <h3>Journal</h3>
                ${session.journal.notes ? `<p><strong>Notes:</strong> ${session.journal.notes}</p>` : ''}
                ${session.journal.insights ? `<p><strong>Insights:</strong> ${session.journal.insights}</p>` : ''}
                ${session.journal.rating ? `<p><strong>Rating:</strong> ${'⭐'.repeat(session.journal.rating)}</p>` : ''}
            ` : ''}

            ${session.tags && session.tags.length ? `
                <hr style="margin: 1rem 0; border-color: var(--bg-tertiary);">
                <h3>Tags</h3>
                <p>${session.tags.map(t => `<span style="background: var(--accent-primary); padding: 0.2rem 0.5rem; border-radius: 4px; margin-right: 0.5rem;">${t}</span>`).join('')}</p>
            ` : ''}

            ${session.notes ? `
                <hr style="margin: 1rem 0; border-color: var(--bg-tertiary);">
                <p>${session.notes}</p>
            ` : ''}
        `;

        modal.classList.add('active');

        // Close modal
        modal.querySelector('.modal-close').onclick = () => {
            modal.classList.remove('active');
        };

        modal.onclick = (e) => {
            if (e.target === modal) {
                modal.classList.remove('active');
            }
        };

    } catch (error) {
        console.error('Error loading session detail:', error);
    }
}

// ============================================================
// UTILITIES
// ============================================================

function formatDate(dateString) {
    if (!dateString) return 'Unknown';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function formatDuration(seconds) {
    if (!seconds) return '0m';
    const minutes = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${minutes}m ${secs}s`;
}
