/**
 * AEGIS Frontend — vanilla JS, no framework needed
 */

/* ═══════════════════════════════════════════════════════════
   STATE
   ═══════════════════════════════════════════════════════════ */
const S = {
  transcript:      [],
  analysis:        null,
  history:         [],    // [{step, score, risk}]
  scenarios:       {},    // {id: scenario}
  scenarioId:      null,
  demoStep:        0,
  autoTimer:       null,
  useMock:         false,
  activeSpeaker:   'caller',

  // voice
  recognition:     null,
  isRecording:     false,
  interimBuffer:   '',
  analysisTimer:   null,
};

/* ═══════════════════════════════════════════════════════════
   CONSTANTS
   ═══════════════════════════════════════════════════════════ */
const VECTORS = [
  { key: 'belief_installation',      label: '🧠 Belief Installation' },
  { key: 'verification_suppression', label: '🔒 Verif. Suppression' },
  { key: 'urgency_fabrication',      label: '⏱️ Urgency Fabrication' },
  { key: 'authority_hijacking',      label: '🎭 Authority Hijacking' },
  { key: 'emotional_flooding',       label: '🌊 Emotional Flooding' },
  { key: 'exit_path_closure',        label: '🚪 Exit Path Closure' },
];

const RISK_ICONS = { LOW: '✅', MEDIUM: '⚠️', HIGH: '🔶', CRITICAL: '🚨' };

const GAUGE_CIRC = Math.PI * 80; // half-circle arc length ≈ 251.3

/* ═══════════════════════════════════════════════════════════
   INIT
   ═══════════════════════════════════════════════════════════ */
document.addEventListener('DOMContentLoaded', () => {
  initTimeline();
  fetchStatus();
  fetchScenarios();
  setInterval(fetchStatus, 8000);
});

/* ═══════════════════════════════════════════════════════════
   STATUS
   ═══════════════════════════════════════════════════════════ */
async function fetchStatus() {
  try {
    const r = await fetch('/api/status');
    const d = await r.json();
    const dot  = document.getElementById('statusDot');
    const text = document.getElementById('statusText');

    if (d.model) {
      dot.className  = 'status-dot active';
      text.textContent = 'AEGIS Model Active';
    } else if (d.ollama) {
      dot.className  = 'status-dot warning';
      text.textContent = 'Ollama Running — Model Loading';
    } else {
      dot.className  = 'status-dot offline';
      text.textContent = 'Ollama Offline — Mock Mode';
      S.useMock = true;
      syncMockBtn();
    }
  } catch { /* ignore */ }
}

/* ═══════════════════════════════════════════════════════════
   SCENARIOS
   ═══════════════════════════════════════════════════════════ */
async function fetchScenarios() {
  const r = await fetch('/api/scenarios');
  const list = await r.json();
  const sel  = document.getElementById('scenarioSelect');
  sel.innerHTML = '';
  list.forEach(s => {
    const opt = document.createElement('option');
    opt.value = s.id;
    opt.textContent = `${s.icon}  ${s.name}`;
    sel.appendChild(opt);
  });
  if (list.length) {
    S.scenarioId = list[0].id;
    await loadScenario(S.scenarioId);
  }
}

async function loadScenario(id) {
  const r  = await fetch(`/api/scenario/${id}`);
  const sc = await r.json();
  S.scenarios[id]  = sc;
  S.scenarioId     = id;
  S.demoStep       = 0;
  updateScenarioMeta(sc);
}

function handleScenarioChange() {
  const id = document.getElementById('scenarioSelect').value;
  stopAutoPlay();
  resetState();
  loadScenario(id);
}

function updateScenarioMeta(sc) {
  const meta = document.getElementById('scenarioMeta');
  meta.style.display = 'flex';
  document.getElementById('metaVictim').textContent = `👤 ${sc.victim_profile}`;
  document.getElementById('metaType').textContent   = `📋 ${sc.type}`;
  updateStepTag();
  document.getElementById('scenarioDesc').textContent = sc.description || '';
  document.getElementById('progressWrap').style.display = 'flex';
  updateProgress();
}

function updateStepTag() {
  const sc = S.scenarios[S.scenarioId];
  const total = sc ? sc.turns.length : 0;
  document.getElementById('metaStep').textContent = `Step ${S.demoStep}/${total}`;
}

function updateProgress() {
  const sc = S.scenarios[S.scenarioId];
  if (!sc) return;
  const pct = Math.round((S.demoStep / sc.turns.length) * 100);
  const bar  = document.getElementById('progressBar');
  bar.style.setProperty('--pct', pct + '%');
  document.getElementById('progressLabel').textContent = pct + '%';
}

/* ═══════════════════════════════════════════════════════════
   DEMO NAVIGATION
   ═══════════════════════════════════════════════════════════ */
async function nextTurn() {
  const sc = S.scenarios[S.scenarioId];
  if (!sc || S.demoStep >= sc.turns.length) {
    stopAutoPlay();
    return false;
  }

  const turn = sc.turns[S.demoStep];
  S.demoStep++;

  appendTurn(turn);
  updateStepTag();
  updateProgress();

  // Show active badge
  document.getElementById('callBadge').style.display = 'inline';

  // Analyze after caller turns (and system turn 0)
  if (turn.speaker === 'caller') {
    await runAnalysis();
  }

  return S.demoStep < sc.turns.length;
}

function toggleAutoPlay() {
  if (S.autoTimer) {
    stopAutoPlay();
  } else {
    startAutoPlay();
  }
}

function startAutoPlay() {
  const btn = document.getElementById('btnAuto');
  btn.textContent = '⏸ Pause';
  btn.classList.add('active');

  const step = async () => {
    const hasMore = await nextTurn();
    if (hasMore) {
      S.autoTimer = setTimeout(step, 2600);
    } else {
      stopAutoPlay();
    }
  };
  S.autoTimer = setTimeout(step, 400);
}

function stopAutoPlay() {
  if (S.autoTimer) { clearTimeout(S.autoTimer); S.autoTimer = null; }
  const btn = document.getElementById('btnAuto');
  btn.textContent = '⚡ Auto Play';
  btn.classList.remove('active');
}

function resetDemo() {
  stopAutoPlay();
  resetState();
  const sc = S.scenarios[S.scenarioId];
  if (sc) updateScenarioMeta(sc);
}

function resetState() {
  S.transcript = [];
  S.analysis   = null;
  S.history    = [];
  S.demoStep   = 0;

  // DOM
  document.getElementById('transcript').innerHTML =
    `<div class="transcript-empty" id="transcriptEmpty">
       <div class="empty-icon">📞</div>
       <div class="empty-title">No call in progress</div>
       <div class="empty-sub">Select a demo scenario below or use Live Analysis</div>
     </div>`;

  document.getElementById('callBadge').style.display = 'none';
  showEmpty();
  resetTimeline();
  updateStepTag();
  updateProgress();
}

/* ═══════════════════════════════════════════════════════════
   LIVE MODE
   ═══════════════════════════════════════════════════════════ */
function setSpeaker(sp) {
  S.activeSpeaker = sp;
  document.getElementById('btnCaller').className   = 'speaker-btn' + (sp === 'caller'   ? ' speaker-active' : '');
  document.getElementById('btnReceiver').className = 'speaker-btn' + (sp === 'receiver' ? ' speaker-active' : '');
}

async function addLiveTurn() {
  const input = document.getElementById('liveInput');
  const text  = input.value.trim();
  if (!text) { input.focus(); return; }

  const turn = { speaker: S.activeSpeaker, text };
  appendTurn(turn);
  input.value = '';
  input.focus();

  await runAnalysis();
}

async function analyzeNow() {
  if (!S.transcript.length) return;
  await runAnalysis();
}

async function quickLoad(id) {
  stopAutoPlay();
  resetState();

  // Switch to demo tab visually
  switchTab('demo');

  const sel = document.getElementById('scenarioSelect');
  sel.value = id;
  await loadScenario(id);

  // Load first 5 turns
  const sc = S.scenarios[id];
  if (!sc) return;
  const slice = sc.turns.slice(0, 5);
  for (const t of slice) {
    S.demoStep++;
    appendTurn(t);
  }
  updateStepTag();
  updateProgress();
  document.getElementById('callBadge').style.display = 'inline';
  await runAnalysis();
}

/* ═══════════════════════════════════════════════════════════
   ANALYSIS
   ═══════════════════════════════════════════════════════════ */
async function runAnalysis() {
  const callerTurns = S.transcript.filter(t => t.speaker === 'caller');
  if (!callerTurns.length) return;

  // Show spinner on right panel
  showAnalyzing();

  try {
    const r = await fetch('/api/analyze', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ transcript: S.transcript, use_mock: S.useMock }),
    });
    const data = await r.json();
    S.analysis = data.analysis;

    S.history.push({
      step:  S.history.length + 1,
      score: S.analysis.integrity_score,
      risk:  S.analysis.risk_level,
    });

    renderAnalysis(data.analysis, data.tools || []);
    updateTimeline();
  } catch (e) {
    console.error('Analysis error:', e);
    hideAnalyzing();
  }
}

/* ═══════════════════════════════════════════════════════════
   RENDER: TRANSCRIPT
   ═══════════════════════════════════════════════════════════ */
function appendTurn(turn) {
  // Remove empty state
  const empty = document.getElementById('transcriptEmpty');
  if (empty) empty.remove();

  S.transcript.push({ ...turn, ts: formatTs(S.transcript.length) });

  const box = document.getElementById('transcript');
  const el  = document.createElement('div');
  const sp  = turn.speaker;

  if (sp === 'system') {
    el.className = 'turn-system';
    el.textContent = '📞 ' + turn.text;
  } else {
    el.className = sp === 'caller' ? 'turn-caller' : 'turn-receiver';
    const icon  = sp === 'caller' ? '🎭 Caller' : '👤 Receiver';
    const ts    = formatTs(S.transcript.length - 1);
    el.innerHTML = `
      <div class="turn-speaker">
        ${icon}
        <span class="turn-ts">${ts}</span>
      </div>
      <div class="turn-text">${escHtml(turn.text)}</div>`;
  }

  box.appendChild(el);
  box.scrollTop = box.scrollHeight;
}

function formatTs(idx) {
  const s = idx * 15;
  const m = String(Math.floor(s / 60)).padStart(2, '0');
  const sec = String(s % 60).padStart(2, '0');
  return `${m}:${sec}`;
}

function escHtml(s) {
  return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

/* ═══════════════════════════════════════════════════════════
   RENDER: ANALYSIS PANEL
   ═══════════════════════════════════════════════════════════ */
function renderAnalysis(a, tools) {
  document.getElementById('analysisEmpty').classList.add('hidden');
  document.getElementById('analysisContent').classList.remove('hidden');
  document.getElementById('analyzing').classList.add('hidden');

  updateGauge(a.integrity_score, a.risk_level);
  renderVectors(a);
  renderAlert(a);

  const showTools = document.getElementById('showTools')?.checked !== false;
  if (showTools && tools.length) {
    renderTools(tools);
  } else {
    document.getElementById('toolsSection').style.display = 'none';
  }
}

/* ─── Gauge ─── */
function updateGauge(score, risk) {
  const progress = (score / 100) * GAUGE_CIRC;
  const gap      = GAUGE_CIRC - progress;
  const color    = scoreColor(score);

  const fill      = document.getElementById('gaugeFill');
  const scoreEl   = document.getElementById('gaugeScore');
  const badgeEl   = document.getElementById('riskBadge');

  fill.setAttribute('stroke-dasharray', `${progress.toFixed(1)} ${gap.toFixed(1)}`);
  fill.setAttribute('stroke', color);
  scoreEl.textContent    = score;
  scoreEl.setAttribute('fill', color);
  badgeEl.textContent    = `${RISK_ICONS[risk] || ''} ${risk}`;
  badgeEl.className      = `risk-badge risk-${risk}`;
}

function scoreColor(s) {
  if (s >= 70) return '#00ff87';
  if (s >= 45) return '#ffcc00';
  if (s >= 20) return '#ff8800';
  return '#ff2d55';
}

function barColor(v) {
  if (v >= 80) return '#ff2d55';
  if (v >= 60) return '#ff6600';
  if (v >= 40) return '#ffaa00';
  if (v >= 20) return '#80cc00';
  return '#00cc66';
}

/* ─── Vectors ─── */
function renderVectors(a) {
  const vecs     = a.manipulation_vectors || {};
  const evidence = a.evidence || {};
  const showEv   = document.getElementById('showEvidence')?.checked;
  const box      = document.getElementById('vectors');

  box.innerHTML = VECTORS.map(({ key, label }) => {
    const score = vecs[key] || 0;
    const color = barColor(score);
    const ev    = evidence[key] || '';
    const evRow = (showEv && ev && ev !== 'None detected')
      ? `<div class="vector-evidence">→ ${escHtml(ev)}</div>` : '';
    return `
      <div class="vector-row">
        <div class="vector-label">${label}</div>
        <div class="vector-track">
          <div class="vector-fill" style="width:${score}%;background:linear-gradient(90deg,${color}88,${color})"></div>
        </div>
        <div class="vector-score" style="color:${color}">${score}</div>
      </div>${evRow}`;
  }).join('');
}

/* ─── Alert ─── */
function renderAlert(a) {
  const risk   = a.risk_level || 'LOW';
  const icon   = RISK_ICONS[risk] || '';
  const labels = {
    LOW:      'No Significant Threat',
    MEDIUM:   'Manipulation Patterns Detected',
    HIGH:     'High Manipulation Risk',
    CRITICAL: 'CRITICAL — Epistemic Attack In Progress',
  };

  document.getElementById('alertBox').innerHTML = `
    <div class="alert-box alert-${risk}">
      <div class="alert-title">${icon} ${labels[risk] || risk}</div>
      <div class="alert-body">${escHtml(a.explanation || '')}</div>
      <div class="alert-action">
        <div class="alert-action-label">Recommended Action</div>
        <div class="alert-action-text">${escHtml(a.recommended_action || '')}</div>
      </div>
    </div>`;
}

/* ─── Tools ─── */
function renderTools(tools) {
  if (!tools || !tools.length) {
    document.getElementById('toolsSection').style.display = 'none';
    return;
  }
  document.getElementById('toolsSection').style.display = 'block';
  document.getElementById('toolsList').innerHTML = tools.map(t => {
    const d = t.data || {};
    if (t.type === 'authority') {
      const cls = d.is_suspicious ? 'risk-critical' : 'risk-low';
      return `<div class="tool-card ${cls}">
        <div class="tool-card-title">Authority Check · ${escHtml(d.organization || '')}</div>
        <div class="tool-card-body">${escHtml(d.warning || '')} ${escHtml(d.verified_fact || '')}</div>
        <div class="tool-card-link">Safe contact: <strong>${escHtml(d.safe_contact || '')}</strong></div>
      </div>`;
    }
    if (t.type === 'payment') {
      const rl  = (d.risk_level || '').toLowerCase();
      const cls = rl === 'critical' ? 'risk-critical' : rl === 'high' ? 'risk-high' : 'risk-low';
      return `<div class="tool-card ${cls}">
        <div class="tool-card-title">Payment Risk · ${escHtml(d.payment_method || '')}</div>
        <div class="tool-card-body">${escHtml(d.warning || d.reason || '')}</div>
      </div>`;
    }
    if (t.type === 'verification') {
      return `<div class="tool-card">
        <div class="tool-card-title">Verification Guide</div>
        <div class="tool-card-body">${escHtml(d.action || '')}</div>
        <div class="tool-card-link">${escHtml(d.key_fact || '')}</div>
      </div>`;
    }
    return '';
  }).join('');
}

/* ─── States ─── */
function showEmpty() {
  document.getElementById('analysisEmpty').classList.remove('hidden');
  document.getElementById('analysisContent').classList.add('hidden');
  document.getElementById('analyzing').classList.add('hidden');
}

function showAnalyzing() {
  document.getElementById('analysisEmpty').classList.add('hidden');
  document.getElementById('analysisContent').classList.add('hidden');
  document.getElementById('analyzing').classList.remove('hidden');
}

function hideAnalyzing() {
  document.getElementById('analyzing').classList.add('hidden');
}

/* ═══════════════════════════════════════════════════════════
   TIMELINE (Chart.js)
   ═══════════════════════════════════════════════════════════ */
let chart = null;

function initTimeline() {
  const ctx = document.getElementById('timelineChart').getContext('2d');
  chart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: [],
      datasets: [{
        label: 'EIS',
        data:   [],
        borderColor:     '#00d4ff',
        backgroundColor: 'rgba(0,212,255,.05)',
        pointBackgroundColor: [],
        pointBorderColor:     '#060b18',
        pointBorderWidth:     2,
        pointRadius:          6,
        fill:     true,
        tension:  0.4,
        borderWidth: 2.5,
      }],
    },
    options: {
      responsive:          true,
      maintainAspectRatio: false,
      animation: { duration: 500 },
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: '#0d1422',
          borderColor:     '#1a2845',
          borderWidth:     1,
          titleColor:      '#c9d1e0',
          bodyColor:       '#6080a0',
          callbacks: {
            label: ctx => ` EIS: ${ctx.raw}`,
          },
        },
      },
      scales: {
        y: {
          min: 0, max: 105,
          grid:  { color: '#0d1a30' },
          ticks: { color: '#405060', font: { size: 10 } },
        },
        x: {
          grid:  { color: '#0a1020' },
          ticks: { color: '#405060', font: { size: 10 } },
        },
      },
    },
  });

  // Danger zone annotation lines via afterDraw plugin
  Chart.register({
    id: 'dangerZones',
    afterDraw(ch) {
      const { ctx: c, chartArea: { left, right, top, bottom }, scales: { y } } = ch;
      const lines = [
        { val: 20, color: '#ff2d5560', label: 'CRITICAL' },
        { val: 45, color: '#ff880040', label: 'HIGH' },
        { val: 70, color: '#ffcc0030', label: 'MEDIUM' },
      ];
      lines.forEach(({ val, color, label }) => {
        const yPos = y.getPixelForValue(val);
        c.save();
        c.beginPath();
        c.setLineDash([4, 4]);
        c.strokeStyle = color;
        c.lineWidth   = 1;
        c.moveTo(left, yPos); c.lineTo(right, yPos);
        c.stroke();
        c.fillStyle  = color;
        c.font       = '9px Inter,sans-serif';
        c.fillText(label, left + 4, yPos - 3);
        c.restore();
      });
    },
  });
}

function updateTimeline() {
  if (S.history.length < 2) return;

  document.getElementById('timelineSection').classList.remove('hidden');

  const riskColors = { LOW:'#00ff87', MEDIUM:'#ffcc00', HIGH:'#ff8800', CRITICAL:'#ff2d55' };

  chart.data.labels                              = S.history.map(h => `Step ${h.step}`);
  chart.data.datasets[0].data                   = S.history.map(h => h.score);
  chart.data.datasets[0].pointBackgroundColor   = S.history.map(h => riskColors[h.risk] || '#6080a0');
  chart.update('active');
}

function resetTimeline() {
  chart.data.labels                             = [];
  chart.data.datasets[0].data                  = [];
  chart.data.datasets[0].pointBackgroundColor  = [];
  chart.update();
  document.getElementById('timelineSection').classList.add('hidden');
}

/* ═══════════════════════════════════════════════════════════
   TABS
   ═══════════════════════════════════════════════════════════ */
function switchTab(name) {
  document.querySelectorAll('.tab').forEach(t =>
    t.classList.toggle('tab-active', t.dataset.tab === name));
  document.getElementById('tab-demo').classList.toggle('hidden', name !== 'demo');
  document.getElementById('tab-live').classList.toggle('hidden', name !== 'live');
}

/* ═══════════════════════════════════════════════════════════
   MOCK TOGGLE
   ═══════════════════════════════════════════════════════════ */
function toggleMock() {
  S.useMock = !S.useMock;
  syncMockBtn();
}

function syncMockBtn() {
  const btn = document.getElementById('btnMock');
  btn.textContent = S.useMock ? '🤖 Mock: ON' : '🔮 Live AI';
  btn.title = S.useMock
    ? 'Using pre-computed mock results (instant)'
    : 'Using live AEGIS model via Ollama';
}

/* ═══════════════════════════════════════════════════════════
   VOICE — Web Speech API
   Works in Chrome and Edge. Zero install, zero cost.
   ═══════════════════════════════════════════════════════════ */

function initSpeech() {
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SR) {
    showSpeechUnsupported();
    return false;
  }

  const r = new SR();
  r.continuous      = true;   // keep listening across pauses
  r.interimResults  = true;   // show words as they come in
  r.lang            = 'en-US';
  r.maxAlternatives = 1;

  r.onresult = (e) => {
    let interim = '';
    let finalText = '';

    for (let i = e.resultIndex; i < e.results.length; i++) {
      const t = e.results[i][0].transcript;
      if (e.results[i].isFinal) {
        finalText += t;
      } else {
        interim += t;
      }
    }

    // Show live preview
    if (interim) {
      showInterim(interim);
    }

    // Commit a final utterance
    if (finalText.trim()) {
      hideInterim();
      commitSpeech(finalText.trim());
    }
  };

  r.onerror = (e) => {
    if (e.error === 'no-speech') return;   // normal timeout, just restart
    console.warn('Speech error:', e.error);
    if (e.error === 'not-allowed') {
      showSpeechUnsupported('Microphone permission denied. Allow mic access and try again.');
      stopRecording();
    }
  };

  // Auto-restart so it stays live (continuous mode can still stop on its own)
  r.onend = () => {
    if (S.isRecording) {
      try { r.start(); } catch (_) { /* already started */ }
    }
  };

  S.recognition = r;
  return true;
}

function toggleRecording() {
  if (S.isRecording) {
    stopRecording();
  } else {
    startRecording();
  }
}

function startRecording() {
  // Switch to Live tab first
  switchTab('live');

  if (!S.recognition && !initSpeech()) return;

  S.isRecording = true;
  try { S.recognition.start(); } catch (_) { /* already running */ }

  // UI
  const btn = document.getElementById('btnMic');
  btn.classList.add('recording');
  document.getElementById('micLabel').textContent    = 'Stop';
  document.getElementById('micStatus').textContent   = '● Recording';
  document.getElementById('micSub').textContent      = `Speaking as ${S.activeSpeaker === 'caller' ? '🎭 Caller' : '👤 Receiver'}`;
  document.getElementById('micWaves').classList.remove('hidden');
  document.getElementById('callBadge').style.display = 'inline';
}

function stopRecording() {
  S.isRecording = false;
  if (S.recognition) {
    try { S.recognition.stop(); } catch (_) {}
  }

  // Flush any partial interim as a final turn
  const interim = document.getElementById('interimText')?.textContent?.trim();
  if (interim) {
    hideInterim();
    commitSpeech(interim);
  }

  // UI
  const btn = document.getElementById('btnMic');
  btn.classList.remove('recording');
  document.getElementById('micLabel').textContent  = 'Speak';
  document.getElementById('micStatus').textContent = 'Voice Input';
  document.getElementById('micSub').textContent    = 'Chrome / Edge · speaks directly into transcript';
  document.getElementById('micWaves').classList.add('hidden');
}

function commitSpeech(text) {
  if (!text) return;

  // Add to transcript
  appendTurn({ speaker: S.activeSpeaker, text });

  // Auto-switch speaker after each commit (caller → receiver → caller…)
  const next = S.activeSpeaker === 'caller' ? 'receiver' : 'caller';
  setSpeaker(next);

  // Debounce analysis — wait 1.2 s after last speech before calling API
  clearTimeout(S.analysisTimer);
  S.analysisTimer = setTimeout(() => runAnalysis(), 1200);
}

function showInterim(text) {
  const box = document.getElementById('interimBox');
  box.classList.remove('hidden');
  document.getElementById('interimSpeaker').textContent =
    S.activeSpeaker === 'caller' ? '🎭 Caller' : '👤 Receiver';
  document.getElementById('interimText').textContent = text;
}

function hideInterim() {
  document.getElementById('interimBox').classList.add('hidden');
  document.getElementById('interimText').textContent = '';
}

function showSpeechUnsupported(msg) {
  const existing = document.getElementById('speechWarning');
  if (existing) return;
  const el = document.createElement('div');
  el.id        = 'speechWarning';
  el.className = 'speech-unsupported';
  el.textContent = msg || '⚠️ Voice input requires Chrome or Edge. Use the text box below instead.';
  document.getElementById('btnMic').closest('.mic-row').insertAdjacentElement('afterend', el);
}
