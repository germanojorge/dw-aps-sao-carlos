// Monta o .pptx a partir do JSON da captura (chamado pelo gerar_pptx.py).
// Uso: node gerar_pptx.js slides.json saida.pptx
const fs = require("fs");
const pptxgen = require("pptxgenjs");

const [, , entrada, saida] = process.argv;
const slides = JSON.parse(fs.readFileSync(entrada, "utf8"));
const PARTES = ["Problema e fontes", "Processos e estrelas", "Constelação e integração", "Consultas OLAP"];

// O deck HTML tem 1920 × 1080 px; o slide WIDE tem 13,333 × 7,5 pol (= 960 × 540 pt).
const POL = (px) => px / 144;   // px → polegadas
const PT = (px) => px / 2;      // px → pontos
const ALINHA = { start: "left", left: "left", center: "center", right: "right", end: "right", justify: "left" };

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";
pres.title = "Atenção primária à saúde em São Carlos";
pres.author = "Grupo SCC0245";
pres.theme = { headFontFace: "Newsreader", bodyFontFace: "Hanken Grotesk" };

let parteAtual = 0;
for (const s of slides) {
  if (s.parte !== parteAtual) {
    parteAtual = s.parte;
    pres.addSection({ title: `${parteAtual}. ${PARTES[parteAtual - 1]}` });
  }
  const slide = pres.addSlide({ sectionTitle: `${parteAtual}. ${PARTES[parteAtual - 1]}` });
  slide.background = { path: s.fundo };

  for (const b of s.blocos) {
    const runs = [];
    b.linhas.forEach((linha, i) => {
      linha.forEach((r, j) => {
        const e = r.e;
        const o = {
          fontFace: e.fonte, fontSize: PT(e.px), bold: e.peso >= 600, italic: e.italico, color: e.cor,
        };
        if (e.sublinhado) o.underline = { style: "sng" };
        if (e.alfa < 0.99) o.transparency = Math.round((1 - e.alfa) * 100);
        if (Math.abs(e.ls) > 0.01) o.charSpacing = PT(e.ls);
        if (j === linha.length - 1 && i < b.linhas.length - 1) o.breakLine = true;
        runs.push({ text: r.t, options: o });
      });
    });
    // Caixa mais larga que o texto medido (sem quebra automática: as quebras vêm do HTML).
    // A altura é a das linhas do HTML, com o texto centrado nela, como o navegador faz.
    // folga extra para o espaçamento entre letras, que cada programa aplica de um jeito
    const maxLs = Math.max(0, ...b.linhas.flat().map((r) => r.e.ls));
    const nChars = Math.max(...b.linhas.map((l) => l.reduce((n, r) => n + r.t.length, 0)));
    const w = b.w * 1.1 + 24 + maxLs * nChars;
    const alinhar = ALINHA[b.alinhar] || "left";
    const x = alinhar === "center" ? b.x - (w - b.w) / 2 : alinhar === "right" ? b.x - (w - b.w) : b.x;
    const h = b.linhas.length * b.lh;
    const y = b.y - (b.lh - b.linhaH) / 2;
    slide.addText(runs, {
      x: POL(x), y: POL(y), w: POL(w), h: POL(h), margin: 0, valign: "middle", align: alinhar,
      wrap: false, fit: "none", lineSpacing: PT(b.lh), isTextBox: true,
    });
  }
  if (s.notas) slide.addNotes(s.notas);
}

pres.writeFile({ fileName: saida }).then(() => console.log("pptx:", saida));
