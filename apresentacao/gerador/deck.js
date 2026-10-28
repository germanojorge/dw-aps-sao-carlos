/* ===========================================================
   PARTES DA APRESENTAÇÃO e integrantes (os nomes só aparecem na capa)
   =========================================================== */
const PARTES = [
  { titulo: 'Problema e fontes',        pessoa: 'Ivan Medina' },
  { titulo: 'Processos e estrelas',     pessoa: 'Vinícius Morotti' },
  { titulo: 'Constelação e integração', pessoa: 'Germano Jorge' },
  { titulo: 'Consultas OLAP',           pessoa: 'Matheus Rodrigues' },
];

/* ===========================================================
   CROMO DOS SLIDES: rótulo da parte e nº da página
   e decorações próprias de cada tema
   =========================================================== */
const slides = [...document.querySelectorAll('.slide')];
slides.forEach((s, i) => {
  const parte = PARTES[(+s.dataset.part || 1) - 1];
  const n = String(i + 1).padStart(2, '0');
  const cromo = document.createElement('div');
  cromo.className = 'cromo';
  cromo.innerHTML =
    `<span class="cr-l">${s.dataset.part.padStart(2, '0')} · ${parte.titulo}</span>` +
    `<span class="cr-n">${n} / ${slides.length}</span>`;
  s.prepend(cromo);
  const deco = document.createElement('div');
  deco.className = 'deco';
  s.prepend(deco);
});
const capaNomes = document.getElementById('capaNomes');
if (capaNomes) capaNomes.textContent = PARTES.map(p => p.pessoa).join('  ·  ');

/* ===========================================================
   CONSULTA 1 (roll-up): células de mês, trimestre e ano
   =========================================================== */
(function rollup() {
  const M = ['J', 'F', 'M', 'A', 'M', 'J', 'J', 'A', 'S', 'O', 'N', 'D'];
  const mk = (id, items, base) => {
    const el = document.getElementById(id);
    if (el) el.innerHTML = items.map((t, i) => `<span style="--i:${i};--b:${base}">${t}</span>`).join('');
  };
  mk('ruMeses', [...M, ...M], 0);
  mk('ruTris', ['T1', 'T2', 'T3', 'T4', 'T1', 'T2', 'T3', 'T4'], 1);
  mk('ruAnos', ['2023', '2024'], 2);
})();

/* ===========================================================
   CONTROLADOR DA APRESENTAÇÃO
   Setas, espaço, PageUp/Down, Home/End, roda do mouse, toque.
   N = notas do apresentador · F = tela cheia · E = edição
   =========================================================== */
class SlidePresentation {
  constructor() {
    this.slides = slides;
    this.i = 0;
    this.stage = document.getElementById('deckStage');
    this.notes = document.getElementById('notes');
    this.progress = document.getElementById('progress');
    this.scale();
    addEventListener('resize', () => this.scale());
    this.keys();
    this.touch();
    this.wheel();
    const h = parseInt(location.hash.slice(1), 10);
    this.show(Number.isFinite(h) ? h - 1 : 0);
  }
  scale() {
    const f = Math.min(innerWidth / 1920, innerHeight / 1080);
    this.stage.style.transform = `translate(${(innerWidth - 1920 * f) / 2}px, ${(innerHeight - 1080 * f) / 2}px) scale(${f})`;
  }
  show(n) {
    this.i = Math.max(0, Math.min(n, this.slides.length - 1));
    this.slides.forEach((s, k) => {
      const on = k === this.i;
      s.classList.toggle('active', on);
      if (on) { s.classList.remove('visible'); void s.offsetWidth; s.classList.add('visible'); }
      else s.classList.remove('visible');
    });
    this.progress.style.width = `${(this.i + 1) / this.slides.length * 100}%`;
    this.notes.textContent = this.slides[this.i].dataset.notes || '';
    history.replaceState(null, '', '#' + (this.i + 1));
    contar(this.slides[this.i]);
  }
  next() { this.show(this.i + 1); }
  prev() { this.show(this.i - 1); }
  keys() {
    addEventListener('keydown', e => {
      if (e.target.isContentEditable) return;
      if (['ArrowRight', 'ArrowDown', ' ', 'PageDown', 'Enter'].includes(e.key)) { e.preventDefault(); this.next(); }
      else if (['ArrowLeft', 'ArrowUp', 'PageUp', 'Backspace'].includes(e.key)) { e.preventDefault(); this.prev(); }
      else if (e.key === 'Home') this.show(0);
      else if (e.key === 'End') this.show(this.slides.length - 1);
      else if (e.key === 'n' || e.key === 'N') this.notes.classList.toggle('on');
      else if (e.key === 'f' || e.key === 'F') document.fullscreenElement ? document.exitFullscreen() : document.documentElement.requestFullscreen();
    });
  }
  touch() {
    let x0 = null;
    addEventListener('touchstart', e => { x0 = e.touches[0].clientX; }, { passive: true });
    addEventListener('touchend', e => {
      if (x0 === null) return;
      const dx = e.changedTouches[0].clientX - x0;
      if (Math.abs(dx) > 50) dx < 0 ? this.next() : this.prev();
      x0 = null;
    });
  }
  wheel() {
    let t = 0;
    addEventListener('wheel', e => {
      if (editor.isActive) return;
      const now = Date.now();
      if (now - t < 700 || Math.abs(e.deltaY) < 20) return;
      t = now;
      e.deltaY > 0 ? this.next() : this.prev();
    }, { passive: true });
  }
}

/* contador animado dos números grandes (data-count) */
function contar(slide) {
  slide.querySelectorAll('[data-count]').forEach(el => {
    const alvo = +el.dataset.count, t0 = Date.now(), dur = 1400;
    clearInterval(el._timer);
    el._timer = setInterval(() => {
      const p = Math.min(1, (Date.now() - t0) / dur), v = Math.round(alvo * (1 - Math.pow(1 - p, 3)));
      el.textContent = v.toLocaleString('pt-BR');
      if (p >= 1) clearInterval(el._timer);
    }, 30);
  });
}

/* ===========================================================
   EDIÇÃO INLINE: E ou canto superior esquerdo; Ctrl+S salva o .html
   =========================================================== */
const editor = {
  isActive: false,
  sel: '.slide h1, .slide h2, .slide h3, .slide p, .slide b, .slide span:not(.cromo span), .slide code, .slide em',
  toggle() {
    this.isActive = !this.isActive;
    document.body.classList.toggle('editing', this.isActive);
    document.getElementById('editToggle').classList.toggle('active', this.isActive);
    document.querySelectorAll(this.sel).forEach(el => {
      if (el.closest('svg')) return;
      this.isActive ? el.setAttribute('contenteditable', 'true') : el.removeAttribute('contenteditable');
    });
  },
  salvar() {
    if (this.isActive) this.toggle();
    const clone = document.documentElement.cloneNode(true);
    clone.querySelectorAll('.cromo, .deco').forEach(n => n.remove());   // são recriados ao abrir
    clone.querySelectorAll('.slide').forEach(s => s.classList.remove('active', 'visible'));
    const blob = new Blob(['<!DOCTYPE html>\n' + clone.outerHTML], { type: 'text/html' });
    const a = Object.assign(document.createElement('a'), { href: URL.createObjectURL(blob), download: location.pathname.split('/').pop() || 'apresentacao.html' });
    a.click();
  },
};
const toggleBtn = document.getElementById('editToggle');
const hot = document.querySelector('.edit-hotzone');
let hideT = null;
const mostrar = () => { clearTimeout(hideT); toggleBtn.classList.add('show'); };
const esconder = () => { hideT = setTimeout(() => { if (!editor.isActive) toggleBtn.classList.remove('show'); }, 400); };
hot.addEventListener('mouseenter', mostrar); hot.addEventListener('mouseleave', esconder);
toggleBtn.addEventListener('mouseenter', mostrar); toggleBtn.addEventListener('mouseleave', esconder);
hot.addEventListener('click', () => editor.toggle());
toggleBtn.addEventListener('click', () => editor.toggle());
addEventListener('keydown', e => {
  if ((e.key === 'e' || e.key === 'E') && !e.target.isContentEditable) editor.toggle();
  if ((e.ctrlKey || e.metaKey) && e.key === 's') { e.preventDefault(); editor.salvar(); }
});

const deck = new SlidePresentation();
