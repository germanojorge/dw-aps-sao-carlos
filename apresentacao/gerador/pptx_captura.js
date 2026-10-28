/* Injetado numa cópia do deck pelo gerar_pptx.py (não faz parte dos slides).
   MODO "texto": mede cada bloco de texto (posição, linhas, estilo de cada trecho) e grava o JSON em #__saida.
   MODO "fundo": deixa os textos transparentes, para a captura do fundo (formas, ícones, gráficos). */
(function () {
  const MODO = document.documentElement.dataset.captura;
  const naSvg = (n) => !!(n.nodeType === 1 ? n : n.parentElement).closest('svg');
  // bloco = vira caixa de texto própria: tudo que não é inline e também os inline "encaixotados"
  // (etiquetas com borda, espaçamento ou margem), senão uma fila de etiquetas viraria um texto só
  const bloco = (el) => {
    const cs = getComputedStyle(el);
    if (cs.display !== 'inline') return true;
    return ['paddingLeft', 'borderLeftWidth', 'marginLeft', 'marginRight'].some((k) => parseFloat(cs[k]) > 0);
  };
  const textos = (raiz) => {
    const w = document.createTreeWalker(raiz, NodeFilter.SHOW_TEXT);
    const out = [];
    for (let n; (n = w.nextNode());) if (n.textContent.trim() && !naSvg(n)) out.push(n);
    return out;
  };

  if (MODO === 'fundo') {
    for (const s of document.querySelectorAll('.slide')) {
      for (const n of textos(s)) {
        // elemento próprio (não <span>): seletores do deck como ".tags span" não podem pegá-lo
        const span = document.createElement('x-texto');
        span.style.color = 'transparent';
        n.replaceWith(span);
        span.appendChild(n);
      }
    }
    return;
  }

  // ---------- MODO texto ----------
  const rgba = (c) => { const m = c.match(/[\d.]+/g).map(Number); return [m[0], m[1], m[2], m.length > 3 ? m[3] : 1]; };
  // fundo sólido atrás do elemento: primeiro ancestral com cor de fundo opaca (senão, o fundo da página)
  const fundoDe = (el) => {
    for (let e = el; e; e = e.parentElement) {
      const b = rgba(getComputedStyle(e).backgroundColor);
      if (b[3] > 0.9) return b;
    }
    return rgba(getComputedStyle(document.body).backgroundColor);
  };
  // texto semitransparente vira a cor já misturada com o fundo: PowerPoint, Google Slides e LibreOffice
  // tratam transparência de texto cada um de um jeito, cor sólida sai igual em todos
  const corSolida = (el, cs) => {
    const [r, g, b, a0] = rgba(cs.color), a = a0 * parseFloat(cs.opacity || 1), f = fundoDe(el);
    return [r, g, b].map((v, i) => Math.round(v * a + f[i] * (1 - a)).toString(16).padStart(2, '0')).join('');
  };
  const transformar = (t, tt) => tt === 'uppercase' ? t.toUpperCase() : tt === 'lowercase' ? t.toLowerCase() : t;
  // o bloco dono de um texto é o ancestral não inline mais próximo
  const dono = (n) => { let e = n.parentElement; while (e && !bloco(e)) e = e.parentElement; return e; };

  const slides = [...document.querySelectorAll('.slide')].map((s, idx) => {
    // coordenadas relativas ao slide, na escala de 1920 px (o palco é escalado conforme a janela)
    const sr = s.getBoundingClientRect(), k = sr.width / 1920;
    const blocos = new Map();
    for (const n of textos(s)) {
      const b = dono(n);
      if (!blocos.has(b)) blocos.set(b, []);
      blocos.get(b).push(n);
    }
    const saida = [];
    for (const [b, nos] of blocos) {
      const cb = getComputedStyle(b);
      const linhas = [];          // [{top, h, runs:[{t, estilo}]}]
      let r = { left: 1e9, top: 1e9, right: -1e9, bottom: -1e9 };
      for (const n of nos) {
        const el = n.parentElement, cs = getComputedStyle(el);
        const estilo = {
          fonte: cs.fontFamily.split(',')[0].replace(/["']/g, '').trim(),
          px: parseFloat(cs.fontSize), peso: parseInt(cs.fontWeight, 10), italico: cs.fontStyle === 'italic',
          sublinhado: !!el.closest('u'), cor: corSolida(el, cs), alfa: 1,
          ls: cs.letterSpacing === 'normal' ? 0 : parseFloat(cs.letterSpacing),
        };
        const tt = cs.textTransform;
        // mede palavra a palavra para reproduzir as quebras de linha do navegador
        const txt = n.textContent;
        const re = /\S+\s*|\s+/g;
        for (let m; (m = re.exec(txt));) {
          const rg = document.createRange();
          rg.setStart(n, m.index); rg.setEnd(n, m.index + m[0].length);
          const rects = [...rg.getClientRects()].filter((q) => q.width > 0 || q.height > 0);
          if (!rects.length) continue;
          const q = rects[0];
          let lin = linhas.find((L) => Math.abs(L.top - q.top) < q.height * 0.5);
          if (!lin) { lin = { top: q.top, h: q.height, runs: [] }; linhas.push(lin); }
          const ult = lin.runs[lin.runs.length - 1];
          const t = transformar(m[0], tt);
          if (ult && JSON.stringify(ult.e) === JSON.stringify(estilo)) ult.t += t; else lin.runs.push({ t, e: estilo });
          for (const q2 of rects) {
            r = { left: Math.min(r.left, q2.left), top: Math.min(r.top, q2.top),
                  right: Math.max(r.right, q2.right), bottom: Math.max(r.bottom, q2.bottom) };
          }
        }
      }
      if (!linhas.length) continue;
      linhas.sort((a, b2) => a.top - b2.top);
      for (const L of linhas) { const u = L.runs[L.runs.length - 1]; u.t = u.t.replace(/\s+$/, ''); L.runs[0].t = L.runs[0].t.replace(/^\s+/, ''); }
      const lh = cb.lineHeight === 'normal' ? linhas[0].h : parseFloat(cb.lineHeight);
      saida.push({ x: (r.left - sr.left) / k, y: (r.top - sr.top) / k, w: (r.right - r.left) / k, h: (r.bottom - r.top) / k,
                   alinhar: cb.textAlign, lh, linhaH: linhas[0].h / k, linhas: linhas.map((L) => L.runs) });
    }
    return { n: idx + 1, parte: +s.dataset.part || 1, notas: s.dataset.notes || '', blocos: saida };
  });
  const pre = document.createElement('pre');
  pre.id = '__saida';
  pre.textContent = JSON.stringify(slides);
  document.body.appendChild(pre);
})();
