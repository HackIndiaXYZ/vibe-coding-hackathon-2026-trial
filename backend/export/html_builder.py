"""
Generates a self-contained HTML slide deck from lesson data.
Navigate with arrow keys or on-screen buttons.
Each slide gets an SVG diagram matched to its diagram_type.
"""

import html
from typing import Any

# ── helpers ───────────────────────────────────────────────────────────────────

def _e(text: str) -> str:
    return html.escape(str(text))


# ── SVG diagram renderers ─────────────────────────────────────────────────────

def _svg_process(items: list[str], colors: list[str]) -> str:
    """Horizontal A → B → C flow."""
    n = min(len(items), 5)
    items = items[:n]
    W, H = 560, 160
    box_w, box_h = 90, 60
    gap = (W - n * box_w) // (n + 1)
    parts = [f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" '
             f'style="width:100%;max-width:{W}px">']
    for i, item in enumerate(items):
        x = gap + i * (box_w + gap)
        cy = H // 2
        c = colors[i % len(colors)]
        parts.append(
            f'<rect x="{x}" y="{cy - box_h//2}" width="{box_w}" height="{box_h}" '
            f'rx="10" fill="{c}" opacity="0.9"/>'
        )
        words = item.split()
        line1 = " ".join(words[:3])
        line2 = " ".join(words[3:6]) if len(words) > 3 else ""
        parts.append(
            f'<text x="{x + box_w//2}" y="{cy - 6}" text-anchor="middle" '
            f'font-size="11" fill="white" font-weight="600">{_e(line1)}</text>'
        )
        if line2:
            parts.append(
                f'<text x="{x + box_w//2}" y="{cy + 10}" text-anchor="middle" '
                f'font-size="10" fill="white">{_e(line2)}</text>'
            )
        if i < n - 1:
            ax = x + box_w + 4
            parts.append(
                f'<polygon points="{ax},{cy} {ax+12},{cy-7} {ax+12},{cy+7}" fill="#94a3b8"/>'
            )
    parts.append('</svg>')
    return "".join(parts)


def _svg_cycle(items: list[str], colors: list[str]) -> str:
    """Circular cycle of stages."""
    import math
    n = min(len(items), 6)
    items = items[:n]
    W = H = 300
    cx = cy = W // 2
    r_node = 36
    r_orbit = 100
    parts = [f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" '
             f'style="width:100%;max-width:{W}px">']
    # center label
    parts.append(f'<circle cx="{cx}" cy="{cy}" r="38" fill="#1e293b" stroke="#38bdf8" stroke-width="2"/>')
    parts.append(f'<text x="{cx}" y="{cy+5}" text-anchor="middle" font-size="11" '
                 f'fill="#38bdf8" font-weight="700">CYCLE</text>')
    for i, item in enumerate(items):
        angle = math.radians(360 / n * i - 90)
        nx = cx + r_orbit * math.cos(angle)
        ny = cy + r_orbit * math.sin(angle)
        c = colors[i % len(colors)]
        # arrow toward next node
        next_angle = math.radians(360 / n * ((i + 1) % n) - 90)
        nx2 = cx + r_orbit * math.cos(next_angle)
        ny2 = cy + r_orbit * math.sin(next_angle)
        # draw arc line
        parts.append(
            f'<line x1="{nx:.1f}" y1="{ny:.1f}" x2="{nx2:.1f}" y2="{ny2:.1f}" '
            f'stroke="#475569" stroke-width="1.5" stroke-dasharray="4,3"/>'
        )
        parts.append(f'<circle cx="{nx:.1f}" cy="{ny:.1f}" r="{r_node}" fill="{c}" opacity="0.9"/>')
        words = item.split()
        line1 = " ".join(words[:2])
        line2 = " ".join(words[2:4]) if len(words) > 2 else ""
        parts.append(
            f'<text x="{nx:.1f}" y="{ny - 4 if line2 else ny + 4:.1f}" '
            f'text-anchor="middle" font-size="10" fill="white" font-weight="600">{_e(line1)}</text>'
        )
        if line2:
            parts.append(
                f'<text x="{nx:.1f}" y="{ny + 10:.1f}" '
                f'text-anchor="middle" font-size="9" fill="white">{_e(line2)}</text>'
            )
    parts.append('</svg>')
    return "".join(parts)


def _svg_comparison(left_label: str, right_label: str,
                    left_items: list[str], right_items: list[str]) -> str:
    """Two-column compare/contrast."""
    W, row_h = 560, 32
    n = max(len(left_items), len(right_items), 1)
    H = 60 + n * row_h + 20
    parts = [f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" '
             f'style="width:100%;max-width:{W}px">']
    # headers
    parts.append(f'<rect x="10" y="8" width="255" height="36" rx="8" fill="#0ea5e9"/>')
    parts.append(f'<rect x="295" y="8" width="255" height="36" rx="8" fill="#a855f7"/>')
    parts.append(f'<text x="137" y="32" text-anchor="middle" font-size="14" '
                 f'fill="white" font-weight="700">{_e(left_label)}</text>')
    parts.append(f'<text x="422" y="32" text-anchor="middle" font-size="14" '
                 f'fill="white" font-weight="700">{_e(right_label)}</text>')
    # VS divider
    parts.append(f'<text x="{W//2}" y="34" text-anchor="middle" font-size="13" '
                 f'fill="#94a3b8" font-weight="700">VS</text>')
    for i in range(n):
        y = 56 + i * row_h
        bg = "#0f1f35" if i % 2 == 0 else "#0d1b2e"
        parts.append(f'<rect x="10" y="{y}" width="255" height="{row_h - 2}" rx="4" fill="{bg}"/>')
        parts.append(f'<rect x="295" y="{y}" width="255" height="{row_h - 2}" rx="4" fill="{bg}"/>')
        if i < len(left_items):
            parts.append(
                f'<text x="22" y="{y + 20}" font-size="11" fill="#cbd5e1">{_e(left_items[i])}</text>'
            )
        if i < len(right_items):
            parts.append(
                f'<text x="307" y="{y + 20}" font-size="11" fill="#cbd5e1">{_e(right_items[i])}</text>'
            )
    parts.append('</svg>')
    return "".join(parts)


def _svg_timeline(items: list[str]) -> str:
    """Horizontal timeline."""
    n = min(len(items), 6)
    items = items[:n]
    W, H = 560, 140
    parts = [f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" '
             f'style="width:100%;max-width:{W}px">']
    # spine
    parts.append(f'<line x1="40" y1="70" x2="{W-40}" y2="70" stroke="#38bdf8" stroke-width="2"/>')
    step = (W - 80) // max(n - 1, 1)
    COLORS = ["#38bdf8", "#a78bfa", "#34d399", "#fb923c", "#f472b6", "#facc15"]
    for i, item in enumerate(items):
        x = 40 + i * step
        c = COLORS[i % len(COLORS)]
        # dot
        parts.append(f'<circle cx="{x}" cy="70" r="8" fill="{c}"/>')
        # label above/below alternating
        above = (i % 2 == 0)
        ty = 52 if above else 96
        words = item.split()
        line1 = " ".join(words[:3])
        line2 = " ".join(words[3:6]) if len(words) > 3 else ""
        parts.append(
            f'<text x="{x}" y="{ty}" text-anchor="middle" font-size="10" '
            f'fill="{c}" font-weight="600">{_e(line1)}</text>'
        )
        if line2:
            parts.append(
                f'<text x="{x}" y="{ty + 13}" text-anchor="middle" font-size="9" '
                f'fill="#94a3b8">{_e(line2)}</text>'
            )
    parts.append('</svg>')
    return "".join(parts)


def _svg_labeled(center: str, labels: list[str], colors: list[str]) -> str:
    """Central concept with surrounding labels."""
    import math
    n = min(len(labels), 6)
    labels = labels[:n]
    W = H = 320
    cx = cy = W // 2
    r_orbit = 110
    parts = [f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" '
             f'style="width:100%;max-width:{W}px">']
    # center
    parts.append(f'<circle cx="{cx}" cy="{cy}" r="46" fill="#0ea5e9" opacity="0.9"/>')
    words = center.split()
    line1 = " ".join(words[:2])
    line2 = " ".join(words[2:4]) if len(words) > 2 else ""
    parts.append(
        f'<text x="{cx}" y="{cy - 4 if line2 else cy + 5}" text-anchor="middle" '
        f'font-size="12" fill="white" font-weight="700">{_e(line1)}</text>'
    )
    if line2:
        parts.append(
            f'<text x="{cx}" y="{cy + 12}" text-anchor="middle" '
            f'font-size="11" fill="white">{_e(line2)}</text>'
        )
    for i, label in enumerate(labels):
        angle = math.radians(360 / n * i - 90)
        lx = cx + r_orbit * math.cos(angle)
        ly = cy + r_orbit * math.sin(angle)
        c = colors[i % len(colors)]
        # connector
        parts.append(
            f'<line x1="{cx:.1f}" y1="{cy:.1f}" x2="{lx:.1f}" y2="{ly:.1f}" '
            f'stroke="#334155" stroke-width="1.5"/>'
        )
        parts.append(f'<circle cx="{lx:.1f}" cy="{ly:.1f}" r="28" fill="{c}" opacity="0.85"/>')
        words = label.split()
        l1 = " ".join(words[:2])
        l2 = " ".join(words[2:4]) if len(words) > 2 else ""
        parts.append(
            f'<text x="{lx:.1f}" y="{ly - 3 if l2 else ly + 4:.1f}" text-anchor="middle" '
            f'font-size="9" fill="white" font-weight="600">{_e(l1)}</text>'
        )
        if l2:
            parts.append(
                f'<text x="{lx:.1f}" y="{ly + 10:.1f}" text-anchor="middle" '
                f'font-size="8" fill="white">{_e(l2)}</text>'
            )
    parts.append('</svg>')
    return "".join(parts)


def _build_diagram(slide: dict[str, Any]) -> str:
    dtype = slide.get("diagram_type", "none").lower().strip()
    kp = slide.get("key_points", [])
    title = slide.get("title", "")
    ex = slide.get("examples", [])
    COLORS = ["#0ea5e9", "#a78bfa", "#34d399", "#fb923c", "#f472b6", "#facc15"]

    if dtype == "process":
        items = kp if kp else [title]
        return _svg_process(items, COLORS)
    elif dtype == "cycle":
        items = kp if kp else [title]
        return _svg_cycle(items, COLORS)
    elif dtype == "comparison":
        mid = len(kp) // 2 or 1
        return _svg_comparison(
            kp[0] if kp else "Option A",
            kp[mid] if len(kp) > mid else "Option B",
            kp[1:mid],
            kp[mid + 1:],
        )
    elif dtype == "timeline":
        items = kp if kp else ex
        return _svg_timeline(items)
    elif dtype == "labeled":
        return _svg_labeled(title, kp, COLORS)
    return ""  # none


# ── CSS ───────────────────────────────────────────────────────────────────────

_CSS = """
* { box-sizing: border-box; margin: 0; padding: 0; }

body {
  font-family: 'Segoe UI', system-ui, sans-serif;
  background: #060d1a;
  color: #e2e8f0;
  height: 100vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

/* ── progress bar ── */
#progress-bar {
  height: 3px;
  background: linear-gradient(90deg, #38bdf8, #818cf8);
  width: 0%;
  transition: width 0.4s ease;
  flex-shrink: 0;
}

/* ── slide container ── */
#deck {
  flex: 1;
  position: relative;
  overflow: hidden;
}

.slide {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  padding: 48px 64px 32px;
  opacity: 0;
  pointer-events: none;
  transform: translateX(60px);
  transition: opacity 0.35s ease, transform 0.35s ease;
}

.slide.active {
  opacity: 1;
  pointer-events: all;
  transform: translateX(0);
}

.slide.exit-left {
  opacity: 0;
  transform: translateX(-60px);
}

/* ── title slide ── */
.slide-title-slide {
  justify-content: center;
  align-items: flex-start;
  background: radial-gradient(ellipse at 20% 50%, #0c2340 0%, #060d1a 70%);
}

.title-eyebrow {
  font-size: 0.85rem;
  font-weight: 600;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: #38bdf8;
  margin-bottom: 16px;
}

.title-main {
  font-size: clamp(2.2rem, 5vw, 3.8rem);
  font-weight: 800;
  line-height: 1.1;
  color: #f1f5f9;
  margin-bottom: 24px;
  max-width: 800px;
}

.title-divider {
  width: 80px;
  height: 4px;
  background: linear-gradient(90deg, #38bdf8, #818cf8);
  border-radius: 4px;
  margin-bottom: 24px;
}

.title-sub {
  font-size: 1.1rem;
  color: #94a3b8;
  max-width: 600px;
  line-height: 1.6;
}

/* ── content slide ── */
.slide-content {
  display: grid;
  grid-template-rows: auto 1fr;
  gap: 24px;
  height: 100%;
}

.slide-top {
  display: flex;
  align-items: center;
  gap: 16px;
  border-bottom: 1px solid #1e3a5f;
  padding-bottom: 16px;
}

.slide-num-badge {
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  color: #0ea5e9;
  background: #0c2340;
  border: 1.5px solid #0ea5e9;
  padding: 3px 10px;
  border-radius: 999px;
  white-space: nowrap;
}

.slide-heading {
  font-size: clamp(1.3rem, 3vw, 2rem);
  font-weight: 700;
  color: #f1f5f9;
  line-height: 1.2;
}

/* ── body layout: left column + right diagram ── */
.slide-body {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 32px;
  align-items: start;
  overflow: hidden;
}

.slide-left {
  display: flex;
  flex-direction: column;
  gap: 14px;
  overflow: hidden;
}

/* ── key points ── */
.points-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.point-item {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  background: #0d1e35;
  border: 1px solid #1e3a5f;
  border-left: 3px solid #38bdf8;
  border-radius: 8px;
  padding: 10px 14px;
  font-size: 0.88rem;
  line-height: 1.5;
  color: #cbd5e1;
  animation: fadeUp 0.4s ease both;
}

.point-item:nth-child(1) { animation-delay: 0.05s; }
.point-item:nth-child(2) { animation-delay: 0.10s; }
.point-item:nth-child(3) { animation-delay: 0.15s; }
.point-item:nth-child(4) { animation-delay: 0.20s; }
.point-item:nth-child(5) { animation-delay: 0.25s; }
.point-item:nth-child(6) { animation-delay: 0.30s; }

.point-icon {
  color: #38bdf8;
  font-size: 0.75rem;
  margin-top: 3px;
  flex-shrink: 0;
}

/* ── info boxes ── */
.info-row {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.info-box {
  flex: 1;
  min-width: 160px;
  border-radius: 8px;
  padding: 10px 12px;
  font-size: 0.82rem;
  line-height: 1.5;
}

.info-box-label {
  font-size: 0.65rem;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  margin-bottom: 4px;
}

.box-example {
  background: #0a1f10;
  border: 1.5px solid #166534;
}
.box-example .info-box-label { color: #4ade80; }
.box-example p { color: #86efac; }

.box-discuss {
  background: #0f1e3d;
  border: 1.5px solid #1d4ed8;
}
.box-discuss .info-box-label { color: #60a5fa; }
.box-discuss p { color: #bfdbfe; }

/* ── diagram panel ── */
.diagram-panel {
  width: 320px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.diagram-label {
  font-size: 0.65rem;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: #475569;
}

.diagram-panel svg text {
  font-family: 'Segoe UI', system-ui, sans-serif;
}

/* ── teacher note bar ── */
.teacher-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: #0a1628;
  border-top: 1px solid #1e3a5f;
  padding: 0 64px;
  height: 0;
  overflow: hidden;
  transition: height 0.3s ease;
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 0.82rem;
  color: #94a3b8;
}

.teacher-bar.open {
  height: 52px;
}

.teacher-bar-label {
  font-size: 0.65rem;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: #f59e0b;
  white-space: nowrap;
}

/* ── nav controls ── */
#controls {
  position: fixed;
  bottom: 16px;
  right: 24px;
  display: flex;
  align-items: center;
  gap: 10px;
  z-index: 100;
}

.nav-btn {
  background: #0d1e35;
  border: 1.5px solid #1e3a5f;
  color: #94a3b8;
  width: 38px;
  height: 38px;
  border-radius: 50%;
  cursor: pointer;
  font-size: 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s;
}

.nav-btn:hover:not(:disabled) {
  background: #1e3a5f;
  color: #f1f5f9;
  border-color: #38bdf8;
}

.nav-btn:disabled {
  opacity: 0.3;
  cursor: default;
}

#slide-counter {
  font-size: 0.78rem;
  color: #475569;
  min-width: 48px;
  text-align: center;
}

.note-btn {
  background: #0d1e35;
  border: 1.5px solid #1e3a5f;
  color: #f59e0b;
  font-size: 0.72rem;
  font-weight: 600;
  padding: 6px 12px;
  border-radius: 20px;
  cursor: pointer;
  letter-spacing: 0.05em;
  transition: all 0.15s;
}

.note-btn:hover {
  background: #1e3a5f;
}

/* ── animations ── */
@keyframes fadeUp {
  from { opacity: 0; transform: translateY(10px); }
  to   { opacity: 1; transform: translateY(0); }
}

/* ── fullscreen hint ── */
#fs-hint {
  position: fixed;
  top: 12px;
  right: 16px;
  font-size: 0.7rem;
  color: #334155;
  cursor: pointer;
  transition: color 0.2s;
}
#fs-hint:hover { color: #94a3b8; }

/* ── download button inside deck ── */
#dl-btn {
  position: fixed;
  top: 12px;
  left: 16px;
  background: #0d1e35;
  border: 1.5px solid #1e3a5f;
  color: #94a3b8;
  font-size: 0.7rem;
  font-weight: 600;
  padding: 5px 11px;
  border-radius: 20px;
  cursor: pointer;
  letter-spacing: 0.05em;
  transition: all 0.15s;
  z-index: 100;
}
#dl-btn:hover {
  border-color: #38bdf8;
  color: #38bdf8;
}
"""

# ── JS ────────────────────────────────────────────────────────────────────────

_JS = """
const slides = document.querySelectorAll('.slide');
const counter = document.getElementById('slide-counter');
const prevBtn = document.getElementById('prev-btn');
const nextBtn = document.getElementById('next-btn');
const bar     = document.getElementById('progress-bar');
const teacherBar = document.getElementById('teacher-bar');
const noteBtn = document.getElementById('note-btn');
let current = 0;

function goto(idx) {
  if (idx < 0 || idx >= slides.length) return;
  slides[current].classList.remove('active');
  slides[current].classList.add('exit-left');
  setTimeout(() => slides[current].classList.remove('exit-left'), 400);
  current = idx;
  slides[current].classList.add('active');
  counter.textContent = current + ' / ' + (slides.length - 1);
  prevBtn.disabled = current === 0;
  nextBtn.disabled = current === slides.length - 1;
  bar.style.width = (current / (slides.length - 1) * 100) + '%';
  // close teacher bar on slide change
  teacherBar.classList.remove('open');
}

prevBtn.addEventListener('click', () => goto(current - 1));
nextBtn.addEventListener('click', () => goto(current + 1));

noteBtn.addEventListener('click', () => {
  teacherBar.classList.toggle('open');
});

document.addEventListener('keydown', e => {
  if (e.key === 'ArrowRight' || e.key === 'ArrowDown' || e.key === ' ') goto(current + 1);
  if (e.key === 'ArrowLeft'  || e.key === 'ArrowUp')                     goto(current - 1);
  if (e.key === 'f' || e.key === 'F') document.documentElement.requestFullscreen?.();
  if (e.key === 'n' || e.key === 'N') teacherBar.classList.toggle('open');
  if (e.key === 'Escape') teacherBar.classList.remove('open');
});

document.getElementById('fs-hint').addEventListener('click', () =>
  document.documentElement.requestFullscreen?.()
);

document.getElementById('dl-btn').addEventListener('click', () => {
  const html = '<!DOCTYPE html>' + document.documentElement.outerHTML;
  const blob = new Blob([html], { type: 'text/html' });
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = document.title.replace(/[^a-z0-9]/gi, '_') + '.html';
  a.click();
  URL.revokeObjectURL(a.href);
});

// init
goto(0);
"""

# ── slide HTML builders ───────────────────────────────────────────────────────

def _title_slide_html(lesson: dict[str, Any]) -> str:
    topic   = _e(lesson.get("topic", "Lesson"))
    grade   = _e(lesson.get("grade", ""))
    subject = _e(lesson.get("subject", ""))
    n       = len(lesson.get("slides", []))
    return f"""
<div class="slide slide-title-slide">
  <div class="title-eyebrow">{subject} &nbsp;·&nbsp; {grade}</div>
  <h1 class="title-main">{topic}</h1>
  <div class="title-divider"></div>
  <p class="title-sub">AI-Generated Lesson Pack &nbsp;·&nbsp; {n} slides<br>
    <span style="font-size:0.85rem;color:#475569;margin-top:6px;display:block">
      Press <kbd style="background:#1e293b;padding:1px 6px;border-radius:4px;font-size:0.8em">→</kbd>
      or click Next to begin
    </span>
  </p>
</div>"""


def _content_slide_html(slide: dict[str, Any], note_text: str) -> str:
    num    = slide.get("slide_number", "")
    title  = _e(slide.get("title", ""))
    points = slide.get("key_points", [])
    ex     = slide.get("examples", [])
    dq     = slide.get("discussion_question", "")

    points_html = "".join(
        f'<div class="point-item"><span class="point-icon">▶</span><span>{_e(p)}</span></div>'
        for p in points
    )

    ex_html = ""
    if ex:
        ex_items = " &nbsp;·&nbsp; ".join(_e(e) for e in ex)
        ex_html = f"""
        <div class="info-box box-example">
          <div class="info-box-label">Real-world examples</div>
          <p>{ex_items}</p>
        </div>"""

    dq_html = ""
    if dq:
        dq_html = f"""
        <div class="info-box box-discuss">
          <div class="info-box-label">💬 Discussion</div>
          <p>{_e(dq)}</p>
        </div>"""

    diagram_svg = _build_diagram(slide)
    diagram_html = ""
    if diagram_svg:
        diagram_html = f"""
      <div class="diagram-panel">
        <div class="diagram-label">Visual</div>
        {diagram_svg}
      </div>"""

    return f"""
<div class="slide slide-content" data-note="{_e(note_text)}">
  <div class="slide-top">
    <span class="slide-num-badge">SLIDE {num}</span>
    <h2 class="slide-heading">{title}</h2>
  </div>
  <div class="slide-body">
    <div class="slide-left">
      <div class="points-list">{points_html}</div>
      <div class="info-row">{ex_html}{dq_html}</div>
    </div>
    {diagram_html}
  </div>
</div>"""


# ── main entry point ──────────────────────────────────────────────────────────

def build_html(lesson: dict[str, Any]) -> str:
    topic = lesson.get("topic", "Lesson")

    slides_html = _title_slide_html(lesson)
    for s in lesson.get("slides", []):
        note = s.get("teacher_note", "")
        slides_html += _content_slide_html(s, note)

    # teacher bar note text driven by active slide data-note
    teacher_bar = """
<div id="teacher-bar" class="teacher-bar">
  <span class="teacher-bar-label">Teacher note</span>
  <span id="teacher-bar-text"></span>
</div>"""

    # extend JS to update teacher bar text per slide
    extra_js = """
const origGoto = goto;
function gotoWrapped(idx) {
  origGoto(idx);
  const activeSlide = slides[idx];
  const note = activeSlide.dataset.note || '';
  document.getElementById('teacher-bar-text').textContent = note;
  if (!note) teacherBar.classList.remove('open');
}
// override button listeners
prevBtn.replaceWith(prevBtn.cloneNode(true));
nextBtn.replaceWith(nextBtn.cloneNode(true));
document.getElementById('prev-btn').addEventListener('click', () => gotoWrapped(current - 1));
document.getElementById('next-btn').addEventListener('click', () => gotoWrapped(current + 1));
"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>{_e(topic)} — Lesson Slides</title>
<style>{_CSS}</style>
</head>
<body>
<div id="progress-bar"></div>
<div id="deck">
{slides_html}
</div>
{teacher_bar}
<div id="controls">
  <button class="note-btn" id="note-btn">📋 Note</button>
  <button class="nav-btn" id="prev-btn" disabled>&#8592;</button>
  <span id="slide-counter">0 / 0</span>
  <button class="nav-btn" id="next-btn">&#8594;</button>
</div>
<div id="fs-hint" title="Press F or click for fullscreen">&#x26F6; Fullscreen</div>
<button id="dl-btn" title="Download this slide deck as HTML">&#8595; Download</button>
<script>
{_JS}
{extra_js}
</script>
</body>
</html>"""
