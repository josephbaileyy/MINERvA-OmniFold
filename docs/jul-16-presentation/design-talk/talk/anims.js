// anims.js — the four winning animation candidates from the design project's
// anims/ review (A1 variant 2, A3, A6 variants 1+2, A8 variant 1), ported from
// the x-dc candidate pages to plain canvas JS so the deck is self-contained.
// Toy palette moved to the dark deck ground (the candidates drew light plates
// to match the old white matplotlib figures; the figures are dark now).
// Color semantics preserved: data = ink points · unweighted sim = cool blue ·
// reweighted sim = warm red · per-event weight = point size.
(() => {
  'use strict';

  const C = {
    data: '#e9e9ed',
    cool: '#5B8ED6', coolFill: 'rgba(91,142,214,0.30)',
    warm: '#D96C6C', warmFill: 'rgba(217,108,108,0.24)',
    ink: '#e9e9ed', dim: '#9aa0b4', faint: '#3f424d',
    panel: '#1b1e2e', panelEdge: '#2e3148', empty: '#232532',
    accent: '#9184d9',
  };

  // ——— toolkit (port of anims/toolkit.js) ———
  function mulberry32(seed) {
    let a = seed >>> 0;
    return function () {
      a |= 0; a = (a + 0x6D2B79F5) | 0;
      let t = Math.imul(a ^ (a >>> 15), 1 | a);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }
  function gauss(rng) {
    const u = Math.max(rng(), 1e-9), v = rng();
    return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v);
  }
  const clamp = (v, a, b) => Math.min(b, Math.max(a, v));
  const lerp = (a, b, t) => a + (b - a) * t;
  const easeInOut = (t) => t < 0.5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2;
  const phase = (t, t0, t1) => easeInOut(clamp((t - t0) / (t1 - t0), 0, 1));

  function makeHist(vals, weights, lo, hi, n) {
    const h = new Array(n).fill(0);
    const dw = (hi - lo) / n;
    for (let i = 0; i < vals.length; i++) {
      const b = Math.floor((vals[i] - lo) / dw);
      if (b >= 0 && b < n) h[b] += weights ? weights[i] : 1;
    }
    return h;
  }
  function roundRectPath(ctx, x, y, w, h, r) {
    ctx.beginPath();
    ctx.moveTo(x + r, y);
    ctx.arcTo(x + w, y, x + w, y + h, r);
    ctx.arcTo(x + w, y + h, x, y + h, r);
    ctx.arcTo(x, y + h, x, y, r);
    ctx.arcTo(x, y, x + w, y, r);
    ctx.closePath();
  }
  function drawPanel(ctx, x, y, w, h) {
    ctx.save();
    ctx.fillStyle = C.panel;
    roundRectPath(ctx, x, y, w, h, 14);
    ctx.fill();
    ctx.restore();
    ctx.strokeStyle = C.panelEdge;
    ctx.lineWidth = 1.5;
    roundRectPath(ctx, x, y, w, h, 14);
    ctx.stroke();
  }
  function drawStepHist(ctx, hist, x0, x1, ybase, yscale, color, opts = {}) {
    const n = hist.length, dw = (x1 - x0) / n;
    ctx.save();
    if (opts.alpha != null) ctx.globalAlpha = opts.alpha;
    if (opts.fill) {
      ctx.beginPath();
      ctx.moveTo(x0, ybase);
      for (let i = 0; i < n; i++) {
        const y = ybase - hist[i] * yscale;
        ctx.lineTo(x0 + i * dw, y);
        ctx.lineTo(x0 + (i + 1) * dw, y);
      }
      ctx.lineTo(x1, ybase);
      ctx.closePath();
      ctx.fillStyle = opts.fill;
      ctx.fill();
    }
    ctx.beginPath();
    ctx.moveTo(x0, ybase - hist[0] * yscale);
    for (let i = 0; i < n; i++) {
      const y = ybase - hist[i] * yscale;
      ctx.lineTo(x0 + i * dw, y);
      ctx.lineTo(x0 + (i + 1) * dw, y);
    }
    ctx.strokeStyle = color;
    ctx.lineWidth = opts.width || 2.5;
    if (opts.dash) ctx.setLineDash(opts.dash);
    ctx.stroke();
    ctx.restore();
  }
  function drawDataPoints(ctx, hist, x0, x1, ybase, yscale, r = 5) {
    const n = hist.length, dw = (x1 - x0) / n;
    ctx.save();
    ctx.fillStyle = C.data;
    ctx.strokeStyle = C.data;
    ctx.lineWidth = 2;
    for (let i = 0; i < n; i++) {
      if (hist[i] <= 0) continue;
      const cx = x0 + (i + 0.5) * dw;
      const cy = ybase - hist[i] * yscale;
      ctx.beginPath();
      ctx.arc(cx, cy, r, 0, Math.PI * 2);
      ctx.fill();
      const e = Math.sqrt(hist[i]) * yscale * 0.5;
      ctx.beginPath();
      ctx.moveTo(cx, cy - e);
      ctx.lineTo(cx, cy + e);
      ctx.stroke();
    }
    ctx.restore();
  }
  function label(ctx, text, x, y, opts = {}) {
    ctx.save();
    ctx.fillStyle = opts.color || C.ink;
    ctx.font = `${opts.weight || 500} ${opts.size || 26}px Inter, system-ui, sans-serif`;
    ctx.textAlign = opts.align || 'left';
    ctx.textBaseline = opts.baseline || 'alphabetic';
    if (opts.alpha != null) ctx.globalAlpha = opts.alpha;
    ctx.fillText(text, x, y);
    ctx.restore();
  }

  // ——— runner: autoplay on slide activation, controls, static final frame ———
  class Anim {
    constructor(host, spec) {
      this.spec = spec;
      this.t = spec.duration;      // parked on the final frame (print/thumbnail safe)
      this.playing = false;
      this.played = false;

      this.canvas = document.createElement('canvas');
      this.canvas.width = 1600; this.canvas.height = 900;
      this.canvas.className = 'anim-canvas';
      host.appendChild(this.canvas);

      const bar = document.createElement('div');
      bar.className = 'anim-bar';
      const btn = (txt, fn, title) => {
        const b = document.createElement('button');
        b.type = 'button'; b.textContent = txt; b.title = title || '';
        b.addEventListener('click', (e) => { e.stopPropagation(); fn(); });
        bar.appendChild(b); return b;
      };
      this.playBtn = btn('pause', () => this.toggle(), 'play/pause');
      btn('‹ beat', () => this.step(-1), 'previous beat');
      btn('beat ›', () => this.step(1), 'next beat');
      btn('restart', () => { this.t = 0; this.play(); }, 'restart');
      btn('final', () => { this.pause(); this.t = this.spec.duration; this.render(); }, 'static final frame');
      this.scrub = document.createElement('input');
      this.scrub.type = 'range'; this.scrub.min = 0; this.scrub.max = Math.round(spec.duration * 1000);
      this.scrub.addEventListener('input', (e) => { this.pause(); this.t = +e.target.value / 1000; this.render(); });
      this.scrub.addEventListener('click', (e) => e.stopPropagation());
      bar.appendChild(this.scrub);
      if (spec.variants) {
        spec.variants.forEach((name, i) => {
          const b = btn(name, () => {
            this.spec.variant = i;
            bar.querySelectorAll('.vbtn').forEach((x, k) => x.classList.toggle('on', k === i));
            this.t = 0; this.play();
          });
          b.classList.add('vbtn');
          if (i === (spec.variant || 0)) b.classList.add('on');
        });
      }
      this.caption = document.createElement('p');
      this.caption.className = 'anim-caption';
      host.appendChild(bar);
      host.appendChild(this.caption);

      // autoplay the first time the slide becomes the active one
      const slide = host.closest('section');
      if (slide) {
        const mo = new MutationObserver(() => {
          const active = slide.hasAttribute('data-deck-active');
          if (active && !this.played) { this.played = true; this.t = 0; this.play(); }
          if (!active) this.pause();
        });
        mo.observe(slide, { attributes: true });
        if (slide.hasAttribute('data-deck-active')) { this.played = true; this.t = 0; this.play(); }
      }
      this.render();
    }
    play() {
      if (this.playing) return;
      this.playing = true;
      this.playBtn.textContent = 'pause';
      this.last = performance.now();
      const loop = (now) => {
        if (!this.playing) return;
        this.raf = requestAnimationFrame(loop);
        const dt = Math.min(0.05, (now - this.last) / 1000);
        this.last = now;
        this.t += dt;
        if (this.t >= this.spec.duration) { this.t = this.spec.duration; this.pause(); }
        this.render();
      };
      this.raf = requestAnimationFrame(loop);
    }
    pause() {
      this.playing = false;
      this.playBtn.textContent = 'play';
      cancelAnimationFrame(this.raf);
    }
    toggle() {
      if (this.playing) this.pause();
      else { if (this.t >= this.spec.duration) this.t = 0; this.play(); }
    }
    step(dir) {
      const sn = this.spec.snaps || [0, this.spec.duration];
      this.pause();
      if (dir > 0) {
        const nxt = sn.find((s) => s > this.t + 0.01);
        this.t = nxt != null ? Math.min(nxt, this.spec.duration) : this.spec.duration;
      } else {
        const prev = sn.filter((s) => s < this.t - 0.01);
        this.t = prev.length ? prev[prev.length - 1] : 0;
      }
      this.render();
    }
    render() {
      const ctx = this.canvas.getContext('2d');
      ctx.clearRect(0, 0, 1600, 900);
      this.spec.draw(ctx, this.t, this.spec.variant || 0);
      this.scrub.value = Math.round(this.t * 1000);
      if (this.spec.caption) this.caption.textContent = this.spec.caption(this.t, this.spec.variant || 0);
    }
  }

  // ═══════════ A1 — the dimensionality wall (variant 2: three-panel ticker) ═══════════
  function specA1() {
    const rng = mulberry32(31);
    const ev = [];
    for (let i = 0; i < 600; i++) {
      const x = clamp(0.5 + 0.19 * gauss(rng), 0.02, 0.98);
      const xr = clamp(x + 0.07 * gauss(rng), 0.02, 0.98);
      const y = clamp(0.42 + 0.17 * gauss(rng) + 0.3 * (x - 0.5), 0.02, 0.98);
      const yr = clamp(y + 0.07 * gauss(rng), 0.02, 0.98);
      ev.push({ x, xr, y, yr, jx: rng(), jy: rng() });
    }
    function occ(n, useY) {
      const g = new Array(n * n).fill(0);
      for (const e of ev) {
        const a = Math.min(n - 1, Math.floor(e.x * n)), b = Math.min(n - 1, Math.floor(e.xr * n));
        if (!useY) g[b * n + a]++;
        else {
          const c = Math.min(n - 1, Math.floor(e.y * n)), d = Math.min(n - 1, Math.floor(e.yr * n));
          g[((b + d * n) % n) * n + ((a + c * n) % n)]++;
        }
      }
      return g;
    }
    const grids = {};
    function heat(ctx, x0, y0, size, n, grid, alpha, maxRef) {
      const cell = size / n;
      const mx = maxRef || Math.max(...grid, 1);
      ctx.save();
      ctx.globalAlpha = alpha;
      for (let j = 0; j < n; j++) for (let i = 0; i < n; i++) {
        const v = grid[j * n + i] / mx;
        ctx.fillStyle = v === 0 ? C.empty : `rgba(91,142,214,${0.18 + 0.82 * Math.pow(v, 0.6)})`;
        ctx.fillRect(x0 + i * cell + 0.5, y0 + size - (j + 1) * cell + 0.5, cell - 1, cell - 1);
      }
      ctx.strokeStyle = C.faint;
      ctx.lineWidth = 1;
      ctx.strokeRect(x0, y0, size, size);
      ctx.restore();
    }
    return {
      duration: 21,
      snaps: [0, 4.5, 9.5, 13.5, 21],
      draw(ctx, t) {
        drawPanel(ctx, 30, 20, 1540, 860);
        const panels = [
          { x: 120, on: phase(t, 0.5, 2), n: 8, title: '1 observable', cells: '8 × 8 = 64 cells', occ: '≈ 9 events / cell', use2: false },
          { x: 620, on: phase(t, 4.5, 6), n: 26, title: '2 observables', cells: '4,096 cells', occ: '≈ 0.15 events / cell', use2: true },
          { x: 1120, on: phase(t, 9.5, 11), n: 26, title: '3 observables', cells: '262,144 cells', occ: 'statistics starve', use2: true, ghost: true },
        ];
        for (const p of panels) {
          if (p.on <= 0) continue;
          const key = `g_${p.n}_${p.use2}_${p.ghost ? 1 : 0}`;
          if (!grids[key]) {
            let g = occ(p.n, p.use2);
            if (p.ghost) g = g.map((v, i) => (i * 13) % 17 === 0 ? v : 0);
            grids[key] = g;
          }
          heat(ctx, p.x, 120, 360, p.n, grids[key], p.on, p.use2 ? 4 : null);
          label(ctx, p.title, p.x, 100, { size: 26, color: C.ink, weight: 600, alpha: p.on });
          label(ctx, p.cells, p.x, 530, { size: 24, color: C.cool, weight: 600, alpha: p.on });
          label(ctx, p.occ, p.x, 566, { size: 22, color: C.dim, alpha: p.on });
        }
        const pc = phase(t, 13.5, 17);
        if (pc > 0) {
          ctx.save();
          for (const e of ev) {
            ctx.globalAlpha = 0.8 * Math.min(1, Math.max(0, pc * 1.3 - e.jy * 0.3));
            ctx.fillStyle = C.cool;
            ctx.beginPath();
            ctx.arc(140 + e.x * 1320, 680 + (e.jx - 0.5) * 90 + (e.y - 0.5) * 60, 3.4, 0, Math.PI * 2);
            ctx.fill();
          }
          ctx.restore();
          label(ctx, 'unbinned: the same 600 events, comfortably dense in any dimension', 800, 830, { size: 26, color: C.dim, align: 'center', alpha: phase(t, 16, 17.5) });
        }
        const pTag = phase(t, 18, 19.5);
        if (pTag > 0) label(ctx, 'The events were never the problem — the bins were.', 800, 70, { size: 34, color: C.ink, align: 'center', weight: 600, alpha: pTag });
      },
      caption(t) {
        if (t < 4.5) return 'A healthy 1D response matrix: 64 truth × reco cells, each well populated by the toy sample.';
        if (t < 9.5) return 'Add one observable and the cell count multiplies — 4,096 cells for the same events. Occupancy collapses.';
        if (t < 13.5) return 'Hint at a third observable: 262,144 cells, almost all empty. Migration statistics starve — this is the wall.';
        if (t < 18) return 'The grid dissolves — and the identical statistics reappear as a cloud of individual events, comfortably dense.';
        return 'The events were never the problem — the bins were.';
      },
    };
  }

  // ═══════════ A3 — one OmniFold iteration → convergence (central animation) ═══════════
  function specA3() {
    const rng = mulberry32(20260716);
    const N = 280, B = 18;
    const mix = (r, m1, s1, m2, s2, f) => {
      const g = gauss(r);
      return r() < f ? clamp(m1 + s1 * g, 0.02, 0.98) : clamp(m2 + s2 * g, 0.02, 0.98);
    };
    const smear = (tt) => clamp(tt + 0.055 * gauss(rng), 0, 1);
    const simT = [], simR = [], datR = [], datT = [], jit = [];
    for (let i = 0; i < N; i++) {
      const tt = mix(rng, 0.35, 0.07, 0.70, 0.05, 0.60);
      simT.push(tt); simR.push(smear(tt));
    }
    for (let i = 0; i < N; i++) {
      const tt = mix(rng, 0.33, 0.075, 0.72, 0.055, 0.42);
      datT.push(tt); datR.push(smear(tt));
    }
    for (let i = 0; i < N; i++) jit.push(rng());
    const bin = (v) => clamp(Math.floor(v * B), 0, B - 1);
    const datH = makeHist(datR, null, 0, 1, B);
    const A = [new Array(N).fill(1)];
    const S = [];
    for (let k = 0; k < 4; k++) {
      const W = A[k];
      const simH = makeHist(simR, W, 0, 1, B);
      const Ws = W.map((w, i) => {
        const b = bin(simR[i]);
        const f = clamp((datH[b] + 0.25) / (simH[b] + 0.25), 0.15, 6);
        return w * f;
      });
      S.push(Ws);
      const num = new Array(B).fill(0), den = new Array(B).fill(0);
      for (let i = 0; i < N; i++) { const b = bin(simT[i]); num[b] += Ws[i]; den[b] += 1; }
      const nu = num.map((s, b) => den[b] ? s / den[b] : 1);
      A.push(simT.map((tt) => nu[bin(tt)]));
    }
    const datHT = makeHist(datT, null, 0, 1, B);

    // Dynamic vertical scale: the truth/reco baselines sit at y=380/800 and the
    // panel top is y=20, so a bin has ~330px of headroom before it clips. Take
    // the tallest bin over every weight snapshot (data + all A/S in both zones)
    // and cap hScale so even the peak fits. Same scale for both zones.
    let _peak = 0;
    const _scan = (h) => { for (let b = 0; b < h.length; b++) if (h[b] > _peak) _peak = h[b]; };
    _scan(datH); _scan(datHT);
    for (const W of A) { _scan(makeHist(simR, W, 0, 1, B)); _scan(makeHist(simT, W, 0, 1, B)); }
    for (const W of S) { _scan(makeHist(simR, W, 0, 1, B)); _scan(makeHist(simT, W, 0, 1, B)); }
    const hScaleDyn = Math.min(7.2, 330 / Math.max(_peak, 1));

    function weightsAt(t) {
      const li = (Wa, Wb, p) => Wa.map((w, i) => lerp(w, Wb[i], p));
      let truthW = A[0], recoW = A[0];
      for (let k = 0; k < 4; k++) {
        const s1a = 4 + 5 * k, s1b = s1a + 2.4, s2b = s1a + 5;
        if (t < s1a) break;
        const p1 = phase(t, s1a, s1b), p2 = phase(t, s1b, s2b);
        recoW = p2 > 0 ? li(S[k], A[k + 1], p2) : li(A[k], S[k], p1);
        truthW = li(A[k], A[k + 1], p2);
      }
      return { truthW, recoW, warm: phase(t, 4, 6.4) };
    }
    const mixC = (a, b, p) => {
      const pa = parseInt(a.slice(1), 16), pb = parseInt(b.slice(1), 16);
      const ch = (sh) => Math.round(lerp((pa >> sh) & 255, (pb >> sh) & 255, p));
      return `rgb(${ch(16)},${ch(8)},${ch(0)})`;
    };

    return {
      duration: 28,
      snaps: [0, 4, 6.4, 9, 11.4, 14, 16.4, 19, 21.4, 24, 28],
      draw(ctx, t) {
        drawPanel(ctx, 30, 20, 1540, 860);
        const x0 = 130, x1 = 1470;
        const tBase = 380, rBase = 800, hScale = hScaleDyn;
        const { truthW, recoW, warm } = weightsAt(t);
        const simColor = mixC(C.cool, C.warm, warm);
        const simFill = warm < 0.5 ? C.coolFill : C.warmFill;

        label(ctx, 'TRUTH LEVEL', 70, 78, { size: 22, color: C.dim, weight: 600 });
        label(ctx, 'RECO (DETECTOR) LEVEL', 70, 470, { size: 22, color: C.dim, weight: 600 });
        let iterTxt = '';
        for (let k = 0; k < 4; k++) if (t >= 4 + 5 * k) iterTxt = `iteration ${k + 1} / 4`;
        // below the legend row (y=68) so it doesn't collide with "sim (reweighted)"
        if (iterTxt) label(ctx, iterTxt, 1530, 104, { size: 24, color: C.accent, align: 'right', weight: 600 });

        const nLines = 90;
        ctx.save();
        ctx.strokeStyle = 'rgba(147,151,171,0.14)';
        ctx.lineWidth = 1;
        for (let i = 0; i < nLines; i++) {
          const xa = x0 + simT[i] * (x1 - x0), xb = x0 + simR[i] * (x1 - x0);
          ctx.beginPath(); ctx.moveTo(xa, tBase + 14 + jit[i] * 26); ctx.lineTo(xb, rBase - 40 + jit[i] * 26); ctx.stroke();
        }
        ctx.restore();
        for (let k = 0; k < 4; k++) {
          const s1b = 4 + 5 * k + 2.4, s2b = 4 + 5 * k + 5;
          if (t > s1b && t < s2b) {
            const p = easeInOut(clamp((t - s1b) / (s2b - s1b), 0, 1));
            ctx.save();
            ctx.fillStyle = C.accent;
            for (let i = 0; i < nLines; i += 2) {
              const xa = x0 + simT[i] * (x1 - x0), xb = x0 + simR[i] * (x1 - x0);
              const ya = tBase + 14 + jit[i] * 26, yb = rBase - 40 + jit[i] * 26;
              ctx.globalAlpha = 0.55 * Math.sin(Math.PI * p);
              ctx.beginPath(); ctx.arc(lerp(xb, xa, p), lerp(yb, ya, p), 4, 0, Math.PI * 2); ctx.fill();
            }
            ctx.restore();
          }
        }

        // reco zone
        ctx.save(); ctx.strokeStyle = C.faint; ctx.lineWidth = 1;
        ctx.beginPath(); ctx.moveTo(x0, rBase); ctx.lineTo(x1, rBase); ctx.stroke(); ctx.restore();
        const simHR = makeHist(simR, recoW, 0, 1, B);
        drawStepHist(ctx, simHR, x0, x1, rBase, hScale, simColor, { fill: simFill });
        drawDataPoints(ctx, datH, x0, x1, rBase, hScale, 5);
        for (let i = 0; i < N; i++) {
          const x = x0 + simR[i] * (x1 - x0), y = rBase - 40 + jit[i] * 26;
          const r = clamp(3.6 * Math.sqrt(recoW[i]), 1.4, 11);
          ctx.save(); ctx.globalAlpha = 0.5; ctx.fillStyle = simColor;
          ctx.beginPath(); ctx.arc(x, y, r, 0, Math.PI * 2); ctx.fill(); ctx.restore();
        }

        // truth zone
        ctx.save(); ctx.strokeStyle = C.faint; ctx.lineWidth = 1;
        ctx.beginPath(); ctx.moveTo(x0, tBase); ctx.lineTo(x1, tBase); ctx.stroke(); ctx.restore();
        const simHT = makeHist(simT, truthW, 0, 1, B);
        drawStepHist(ctx, simHT, x0, x1, tBase, hScale, simColor, { fill: simFill });
        for (let i = 0; i < N; i++) {
          const x = x0 + simT[i] * (x1 - x0), y = tBase + 14 + jit[i] * 26;
          const r = clamp(3.6 * Math.sqrt(truthW[i]), 1.4, 11);
          ctx.save(); ctx.globalAlpha = 0.5; ctx.fillStyle = simColor;
          ctx.beginPath(); ctx.arc(x, y, r, 0, Math.PI * 2); ctx.fill(); ctx.restore();
        }
        const rev = phase(t, 24, 26);
        if (rev > 0) {
          drawStepHist(ctx, datHT, x0, x1, tBase, hScale, C.data, { dash: [10, 8], width: 3, alpha: rev });
          label(ctx, 'true spectrum (revealed)', x1, tBase - 300, { size: 24, color: C.data, align: 'right', alpha: rev });
        }

        for (let k = 0; k < 4; k++) {
          const s1a = 4 + 5 * k, s1b = s1a + 2.4, s2b = s1a + 5;
          if (t >= s1a && t < s1b) label(ctx, 'Step 1 — learn per-event weights (a likelihood ratio)', 800, 855, { size: 26, color: C.warm, align: 'center', weight: 600 });
          else if (t >= s1b && t < s2b) label(ctx, 'Step 2 — pull weights back to truth through the pairing', 800, 855, { size: 26, color: C.accent, align: 'center', weight: 600 });
        }
        if (t < 4) label(ctx, 'Simulated events are (truth, reco) pairs — data exists at reco level only', 800, 855, { size: 26, color: C.dim, align: 'center' });
        if (t >= 24) label(ctx, 'Corrections have shrunk away — bin the weighted truth ensemble however you like', 800, 855, { size: 26, color: C.ink, align: 'center', weight: 600 });

        // legend
        ctx.save();
        ctx.fillStyle = C.data; ctx.beginPath(); ctx.arc(1010, 68, 5, 0, Math.PI * 2); ctx.fill();
        label(ctx, 'data', 1024, 76, { size: 22, color: C.dim });
        ctx.strokeStyle = C.cool; ctx.lineWidth = 3; ctx.beginPath(); ctx.moveTo(1090, 68); ctx.lineTo(1130, 68); ctx.stroke();
        label(ctx, 'sim (unweighted)', 1140, 76, { size: 22, color: C.dim });
        ctx.strokeStyle = C.warm; ctx.beginPath(); ctx.moveTo(1310, 68); ctx.lineTo(1350, 68); ctx.stroke();
        label(ctx, 'sim (reweighted)', 1360, 76, { size: 22, color: C.dim });
        ctx.restore();
      },
      caption(t) {
        if (t < 4) return 'Setup: simulation is a set of paired (truth, reco) events — faint lines are the pairing. Data (ink points) exists at reco level only. Nothing has been learned yet.';
        for (let k = 0; k < 4; k++) {
          const s1a = 4 + 5 * k, s1b = s1a + 2.4, s2b = s1a + 5;
          if (t < s1b) return `Iteration ${k + 1} · Step 1 — reweight simulated events at reco level so the weighted ensemble matches the data. Point size = learned weight (a likelihood ratio).`;
          if (t < s2b) return `Iteration ${k + 1} · Step 2 — each weight travels up its own pairing line to the truth-level partner. No response matrix: the pairing itself does the unfolding.`;
        }
        return 'After four iterations the corrections have shrunk away, and the weighted truth ensemble matches the true spectrum (dashed) — never shown to the algorithm. Bin it however you like.';
      },
    };
  }

  // ═══════════ A6 — marginalization as validation (variants 1 + 2) ═══════════
  function specA6() {
    const rng = mulberry32(6);
    const ev = [];
    for (let i = 0; i < 420; i++) {
      const g = gauss(rng);
      const x = clamp(rng() < 0.55 ? 0.34 + 0.09 * g : 0.66 + 0.08 * g, 0.02, 0.98);
      const y = clamp(0.42 + 0.17 * gauss(rng) + 0.28 * (x - 0.5), 0.02, 0.98);
      const z = clamp(0.35 + 0.2 * Math.abs(gauss(rng)), 0.02, 0.98);
      const w = clamp(0.6 + 0.9 * x, 0.3, 2.0);
      ev.push({ x, y, z, w, j: rng() });
    }
    const B = 14;
    const anchor = makeHist(ev.map(e => e.x), ev.map(e => e.w), 0, 1, B);
    return {
      duration: 16,
      snaps: [0, 4, 9, 12.5, 16],
      variants: ['3D volume collapses', 'E_avail slices sum'],
      variant: 0,
      draw(ctx, t, variant) {
        drawPanel(ctx, 30, 20, 1540, 860);
        const pCol = phase(t, 4, 8.5);
        const pCmp = phase(t, 9, 11);
        const pTag = phase(t, 12.5, 14);

        if (variant === 0) {
          const ox = 220, oy = 640, sx = 620, sy = 420, szx = 300, szy = 200;
          const zf = 1 - pCol;
          const P = (x, y, z) => [ox + x * sx + z * zf * szx, oy - y * sy - z * zf * szy];
          ctx.save();
          ctx.strokeStyle = C.faint; ctx.lineWidth = 1.5;
          const corners = [[0, 0], [1, 0], [1, 1], [0, 1]];
          for (const zc of [0, 1]) {
            ctx.globalAlpha = zc === 1 ? 0.5 * (0.2 + 0.8 * zf) : 1;
            ctx.beginPath();
            corners.forEach(([cxx, cyy], i) => { const [px, py] = P(cxx, cyy, zc); i ? ctx.lineTo(px, py) : ctx.moveTo(px, py); });
            ctx.closePath(); ctx.stroke();
          }
          ctx.globalAlpha = 0.5 * (0.2 + 0.8 * zf);
          for (const [cxx, cyy] of corners) {
            const [ax, ay] = P(cxx, cyy, 0), [bx, by] = P(cxx, cyy, 1);
            ctx.beginPath(); ctx.moveTo(ax, ay); ctx.lineTo(bx, by); ctx.stroke();
          }
          ctx.restore();
          label(ctx, 'p_T', ox + sx / 2, oy + 46, { size: 22, color: C.dim, align: 'center' });
          ctx.save(); ctx.translate(ox - 36, oy - sy / 2); ctx.rotate(-Math.PI / 2);
          label(ctx, 'p_∥', 0, 0, { size: 22, color: C.dim, align: 'center' }); ctx.restore();
          if (zf > 0.05) {
            const [ex, ey] = P(1.04, 0, 0.7);
            label(ctx, 'E_avail (new axis)', ex, ey, { size: 22, color: C.accent, alpha: zf });
          }
          ctx.save();
          for (const e of ev) {
            const [px, py] = P(e.x, e.y, e.z);
            ctx.globalAlpha = 0.55;
            ctx.fillStyle = C.warm;
            ctx.beginPath(); ctx.arc(px, py, clamp(2.4 * Math.sqrt(e.w), 1.2, 6), 0, Math.PI * 2); ctx.fill();
          }
          ctx.restore();
          if (pCol > 0 && pCol < 1) label(ctx, 'integrate out E_avail — every event keeps its weight', 540, 780, { size: 24, color: C.accent, align: 'center' });

          const hx0 = 1030, hx1 = 1500, hyb = 560;
          const marg = makeHist(ev.map(e => e.x), ev.map(e => e.w), 0, 1, B);
          const mAlpha = Math.max(0.15, pCol);
          drawStepHist(ctx, marg, hx0, hx1, hyb, 0.9 * 4.4, C.warm, { fill: C.warmFill, alpha: mAlpha });
          label(ctx, 'marginalized (p_T shown)', hx0, 220, { size: 22, color: C.warm, alpha: mAlpha });
          if (pCmp > 0) {
            drawDataPoints(ctx, anchor, hx0, hx1, hyb, 0.9 * 4.4, 5);
            label(ctx, 'established 2D anchor', hx0, 258, { size: 22, color: C.data, alpha: pCmp });
            const fl = Math.sin(Math.PI * clamp((t - 9) / 1.2, 0, 1));
            if (fl > 0) {
              ctx.save(); ctx.globalAlpha = 0.25 * fl; ctx.strokeStyle = C.accent; ctx.lineWidth = 6;
              ctx.strokeRect(hx0 - 24, 180, hx1 - hx0 + 48, 420); ctx.restore();
            }
            label(ctx, '✓ clicks into alignment', hx0, hyb + 52, { size: 24, color: C.accent, weight: 600, alpha: pCmp });
          }
        } else {
          const slices = 4, sw = 300, sx0 = 120, sy0 = 150, syb = 420;
          const perSlice = Array.from({ length: slices }, (_, s) =>
            makeHist(ev.filter(e => Math.floor(Math.min(0.999, e.z) * slices) === s).map(e => e.x),
                     ev.filter(e => Math.floor(Math.min(0.999, e.z) * slices) === s).map(e => e.w), 0, 1, B));
          const mx0 = 480, mx1 = 1140, myb = 800;
          for (let s = 0; s < slices; s++) {
            const gx = sx0 + s * (sw + 60);
            const p = pCol;
            const x0 = lerp(gx, mx0, p), x1 = lerp(gx + sw, mx1, p);
            const yb = lerp(syb, myb, p);
            drawStepHist(ctx, perSlice[s], x0, x1, yb, 5.5, C.warm, { alpha: p < 1 ? 0.85 : 0.25, width: 2 });
            if (pCol < 0.5) label(ctx, `E_avail slice ${s + 1}`, gx, sy0 - 16, { size: 20, color: C.dim, alpha: 1 - pCol * 2 });
          }
          const total = makeHist(ev.map(e => e.x), ev.map(e => e.w), 0, 1, B);
          if (pCol > 0.6) {
            const a = (pCol - 0.6) / 0.4;
            drawStepHist(ctx, total, mx0, mx1, myb, 4.2, C.warm, { fill: C.warmFill, alpha: a });
            label(ctx, 'sum over the new axis', mx0, myb - 400, { size: 22, color: C.warm, alpha: a });
          }
          if (pCmp > 0) {
            drawDataPoints(ctx, anchor, mx0, mx1, myb, 4.2, 5);
            label(ctx, 'established 2D anchor (ink points)', mx0 + 380, myb - 400, { size: 22, color: C.data, alpha: pCmp });
            label(ctx, '✓ clicks into alignment', 1240, 500, { size: 26, color: C.accent, weight: 600, alpha: pCmp });
          }
        }

        if (t < 4) label(ctx, 'the 5D unfold, seen in three of its axes — weights already learned', 800, 855, { size: 26, color: C.dim, align: 'center' });
        if (pTag > 0) label(ctx, 'every new dimension carries its own cross-check', 800, 80, { size: 34, color: C.ink, align: 'center', weight: 600, alpha: pTag });
      },
      caption(t) {
        if (t < 4) return 'Same events, more columns: the higher-dimensional unfold viewed in (p_T, p_∥, E_avail). Each event carries the weight it learned — nothing here is re-unfolded.';
        if (t < 9) return 'Collapse along the new axis: integrating out E_avail is just summing the same weighted events. The unfold does not change — only the view does.';
        if (t < 12.5) return 'The marginal clicks into alignment with the established 2D anchor (ink points). If it did not, the higher-dimensional unfold would be wrong — a built-in falsifiable check.';
        return 'Every new dimension carries its own cross-check — the real check is the next slide’s pull figure; this sets up how to read it.';
      },
    };
  }

  // ═══════════ A8 — localizing an excess (variant 1: 1D fans out into the plane) ═══════════
  function specA8() {
    const g = (x, m, s) => Math.exp(-0.5 * ((x - m) / s) ** 2);
    const n = 40;
    const xs = Array.from({ length: n }, (_, i) => (i + 0.5) / n);
    const sim = xs.map(x => 1.1 * Math.exp(-x * 2.6) + 0.12 * g(x, 0.5, 0.2));
    const exc = xs.map(x => 0.10 * (1 / (1 + Math.exp(-(x - 0.55) / 0.09))));
    const dat = xs.map((v, i) => sim[i] + exc[i]);
    const PB = 14;
    const plane = [];
    for (let j = 0; j < PB; j++) for (let i = 0; i < PB; i++) {
      const ea = (i + 0.5) / PB, w = (j + 0.5) / PB;
      const blob = 0.32 * Math.exp(-(((ea - 0.82) / 0.16) ** 2 + ((w - 0.8) / 0.18) ** 2));
      const noise = 0.02 * Math.sin(i * 12.3 + j * 7.7);
      plane.push(1 + blob + noise);
    }
    return {
      duration: 16,
      snaps: [0, 4, 8, 12, 16],
      draw(ctx, t) {
        drawPanel(ctx, 30, 20, 1540, 860);
        const pPlane = phase(t, 4, 7.5);
        const pLoc = phase(t, 8, 10);
        const pTag = phase(t, 12, 13.5);

        const lx0 = lerp(260, 120, pPlane);
        const lx1 = lerp(1340, 620, pPlane);
        const lyb = 700, lysc = 420;
        ctx.save();
        ctx.strokeStyle = C.faint; ctx.lineWidth = 1;
        ctx.beginPath(); ctx.moveTo(lx0, lyb); ctx.lineTo(lx1, lyb); ctx.stroke();
        ctx.restore();
        const step = (ys, color, fill, alpha) => {
          ctx.save();
          if (alpha != null) ctx.globalAlpha = alpha;
          ctx.beginPath();
          const dw = (lx1 - lx0) / n;
          ctx.moveTo(lx0, lyb - ys[0] * lysc);
          for (let i = 0; i < n; i++) {
            const y = lyb - ys[i] * lysc;
            ctx.lineTo(lx0 + i * dw, y); ctx.lineTo(lx0 + (i + 1) * dw, y);
          }
          if (fill) {
            ctx.lineTo(lx1, lyb); ctx.lineTo(lx0, lyb); ctx.closePath();
            ctx.fillStyle = fill; ctx.fill();
            ctx.beginPath();
            ctx.moveTo(lx0, lyb - ys[0] * lysc);
            for (let i = 0; i < n; i++) {
              const y = lyb - ys[i] * lysc;
              ctx.lineTo(lx0 + i * dw, y); ctx.lineTo(lx0 + (i + 1) * dw, y);
            }
          }
          ctx.strokeStyle = color; ctx.lineWidth = 2.5; ctx.stroke();
          ctx.restore();
        };
        step(sim, C.cool, C.coolFill, 1);
        ctx.save();
        ctx.fillStyle = C.data;
        for (let i = 1; i < n; i += 3) {
          const cx = lx0 + xs[i] * (lx1 - lx0), cy = lyb - dat[i] * lysc;
          ctx.beginPath(); ctx.arc(cx, cy, 5, 0, Math.PI * 2); ctx.fill();
          ctx.fillRect(cx - 1, cy - 10, 2, 20);
        }
        ctx.restore();
        if (t > 1.5) {
          const a = phase(t, 1.5, 3) * (1 - pLoc * 0.6);
          ctx.save();
          ctx.globalAlpha = 0.35 * a;
          const dw = (lx1 - lx0) / n;
          ctx.fillStyle = C.warm;
          for (let i = 0; i < n; i++) {
            if (exc[i] < 0.01) continue;
            ctx.fillRect(lx0 + i * dw, lyb - dat[i] * lysc, dw, exc[i] * lysc);
          }
          ctx.restore();
          label(ctx, 'a broad excess above every generator', (lx0 + lx1) / 2 + 100, lyb - 260, { size: 23, color: C.warm, align: 'center', alpha: a, weight: 600 });
        }
        label(ctx, 'E_avail →', (lx0 + lx1) / 2, lyb + 42, { size: 22, color: C.dim, align: 'center' });
        label(ctx, 'data', lx0 + 14, 200, { size: 21, color: C.data });
        label(ctx, 'generators', lx0 + 14, 234, { size: 21, color: C.cool });

        if (pPlane > 0) {
          const px = 760, py = 150, ps = 560;
          const cell = ps / PB;
          ctx.save();
          ctx.globalAlpha = pPlane;
          for (let j = 0; j < PB; j++) for (let i = 0; i < PB; i++) {
            const v = plane[j * PB + i];
            const d = clamp((v - 1) / 0.32, -1, 1);
            ctx.fillStyle = d >= 0 ? `rgba(217,108,108,${0.08 + 0.8 * d})` : `rgba(91,142,214,${0.08 - 0.8 * d})`;
            ctx.fillRect(px + i * cell + 0.5, py + ps - (j + 1) * cell + 0.5, cell - 1, cell - 1);
          }
          ctx.strokeStyle = C.faint;
          ctx.strokeRect(px, py, ps, ps);
          ctx.restore();
          label(ctx, 'E_avail →', px + ps / 2, py + ps + 40, { size: 22, color: C.dim, align: 'center', alpha: pPlane });
          ctx.save(); ctx.translate(px - 24, py + ps / 2); ctx.rotate(-Math.PI / 2);
          label(ctx, 'W (new axis) →', 0, 0, { size: 22, color: C.accent, align: 'center', alpha: pPlane }); ctx.restore();
          label(ctx, 'data / simulation', px, py - 20, { size: 21, color: C.dim, alpha: pPlane });

          if (pPlane > 0.3 && pPlane < 1) {
            ctx.save();
            ctx.globalAlpha = 0.35 * Math.sin(Math.PI * pPlane);
            ctx.strokeStyle = C.warm; ctx.lineWidth = 2;
            for (let k = 0; k < 8; k++) {
              const sx = lx0 + (0.6 + k * 0.05) * (lx1 - lx0);
              ctx.beginPath();
              ctx.moveTo(sx, lyb - dat[Math.floor((0.6 + k * 0.05) * n)] * lysc);
              ctx.bezierCurveTo(sx + 100, 300, px + ps * 0.6, py + ps * 0.5, px + ps * 0.85, py + ps * 0.22);
              ctx.stroke();
            }
            ctx.restore();
          }
          if (pLoc > 0) {
            ctx.save();
            ctx.globalAlpha = pLoc;
            ctx.strokeStyle = C.warm;
            ctx.lineWidth = 4;
            ctx.setLineDash([10, 8]);
            ctx.strokeRect(px + ps * 0.62, py + ps * 0.02, ps * 0.36, ps * 0.36);
            ctx.restore();
            label(ctx, 'the DIS corner: high E_avail AND high W', px + ps * 0.8, py - 52, { size: 23, color: C.warm, align: 'center', alpha: pLoc, weight: 600 });
          }
        }

        if (t < 4) label(ctx, 'in one dimension the discrepancy is broad and unlocalized', 800, 855, { size: 26, color: C.dim, align: 'center' });
        else if (t < 8) label(ctx, 'open a second axis: W — same weighted events, one more column', 800, 855, { size: 26, color: C.dim, align: 'center' });
        else if (pTag <= 0) label(ctx, 'the broad 1D excess resolves into a compact corner of the plane', 800, 855, { size: 26, color: C.dim, align: 'center' });
        if (pTag > 0) label(ctx, 'central-value observation — significance pending the corrected-covariance requote', 800, 855, { size: 27, color: C.ink, align: 'center', weight: 600, alpha: pTag });
      },
      caption(t) {
        if (t < 4) return 'One dimension: the unfolded data sit broadly above the generator prediction across the high-E_avail tail — real, but shapeless. Where does it live?';
        if (t < 8) return 'Open a second axis, W. No re-unfold — the same weighted events, viewed in the (E_avail, W) plane.';
        if (t < 12) return 'The broad discrepancy resolves into a compact region: high E_avail AND high W — the DIS corner. All four generators underpredict there.';
        return 'Labeled honestly: central-value observation; significance pending the corrected-covariance requote. No Nσ is claimed anywhere.';
      },
    };
  }

  const SPECS = { a1: specA1, a3: specA3, a6: specA6, a8: specA8 };
  const boot = () => {
    document.querySelectorAll('[data-anim]').forEach((host) => {
      if (host._animMounted) return;
      host._animMounted = true;
      const make = SPECS[host.getAttribute('data-anim')];
      if (make) new Anim(host, make());
    });
  };
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot);
  else boot();
})();
