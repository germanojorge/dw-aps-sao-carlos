// Monta o relatório em .docx com o template do ICMC (faixa lateral + logo no cabeçalho + endereço no rodapé).
const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, ImageRun, Header, Footer, AlignmentType, HeadingLevel,
  Table, TableRow, TableCell, WidthType, ShadingType, BorderStyle, PageNumber, PageBreak,
  TableOfContents, LevelFormat, HorizontalPositionRelativeFrom, VerticalPositionRelativeFrom,
  TextWrappingType, VerticalAlign,
} = require("docx");
const sizeOf = (p) => {
  // lê largura/altura de um PNG direto do cabeçalho IHDR
  const b = fs.readFileSync(p);
  return { width: b.readUInt32BE(16), height: b.readUInt32BE(20) };
};

const BLOCOS = JSON.parse(fs.readFileSync("conteudo.json", "utf8"));
const SERIF = "Times New Roman", SANS = "Arial", MONO = "Courier New";
const AZUL = "1F3864", CINZA_RODAPE = "6B809B";

// ---------- geometria da página (A4) ----------
const PT = 20;                       // 1 pt = 20 DXA
const EMU = 12700;                   // 1 pt = 12700 EMU
const PX = (pt) => Math.round(pt * 96 / 72);   // docx-js mede imagens em pixels de 96 dpi
const MARG_ESQ = 85 * PT, MARG_DIR = 80 * PT;
const LARG_UTIL = 11906 - MARG_ESQ - MARG_DIR;  // em DXA
const LARG_UTIL_PT = LARG_UTIL / PT;

// ---------- cabeçalho com o template (posições medidas no PDF do enunciado) ----------
function imagemFlutuante(arquivo, xPt, yPt, wPt, hPt, z) {
  return new ImageRun({
    type: "png",
    data: fs.readFileSync(arquivo),
    transformation: { width: PX(wPt), height: PX(hPt) },
    floating: {
      horizontalPosition: { relative: HorizontalPositionRelativeFrom.PAGE, offset: Math.round(xPt * EMU) },
      verticalPosition: { relative: VerticalPositionRelativeFrom.PAGE, offset: Math.round(yPt * EMU) },
      wrap: { type: TextWrappingType.NONE },
      behindDocument: true, allowOverlap: true, lockAnchor: true, zIndex: z,
    },
  });
}
const cabecalho = () => new Header({
  children: [new Paragraph({
    children: [
      imagemFlutuante("faixa.png", 5.0, 6.0, 69.8, 831.9, 1),
      imagemFlutuante("header.png", 73.6, 21.9, 522.6, 63.6, 2),
    ],
  })],
});
const linhaEndereco = () => new Paragraph({
  alignment: AlignmentType.CENTER,
  children: [new TextRun({
    text: "Av. Trabalhador São-carlense, 400 . centro . São Carlos - SP . cep 13566-590 . Brasil . www.icmc.usp.br",
    font: SANS, size: 16, color: CINZA_RODAPE,
  })],
});
const rodape = () => new Footer({
  children: [
    new Paragraph({
      alignment: AlignmentType.RIGHT, spacing: { after: 60 },
      children: [new TextRun({ children: [PageNumber.CURRENT], font: SANS, size: 16, color: CINZA_RODAPE })],
    }),
    linhaEndereco(),
  ],
});
const rodapeCapa = () => new Footer({ children: [linhaEndereco()] });

// ---------- texto ----------
function runs(rs, extra = {}) {
  return rs.map((r) => new TextRun({
    text: r.t, bold: r.b || extra.bold, italics: r.i || extra.italics,
    font: r.m ? MONO : (extra.font || SERIF), size: r.m ? (extra.monoSize || 21) : extra.size,
    color: extra.color,
  }));
}

function tabela(b) {
  const total = b.w.reduce((a, c) => a + c, 0);
  const cols = b.w.map((w) => Math.floor(LARG_UTIL * w / total));
  cols[cols.length - 1] += LARG_UTIL - cols.reduce((a, c) => a + c, 0);
  const borda = { style: BorderStyle.SINGLE, size: 4, color: "B4B4B4" };
  const bordas = { top: borda, bottom: borda, left: borda, right: borda };
  const nLin = b.rows.length;
  const celula = (rs, i, cab, par, k) => new TableCell({
    width: { size: cols[i], type: WidthType.DXA },
    borders: bordas,
    shading: { type: ShadingType.CLEAR, color: "auto", fill: cab ? AZUL : (par ? "F2F5FA" : "FFFFFF") },
    margins: { top: 50, bottom: 50, left: 90, right: 90 },
    verticalAlign: VerticalAlign.TOP,
    children: [new Paragraph({
      spacing: { after: 0, line: 240 }, keepNext: b.keep && (cab || k < nLin - 1),
      children: runs(rs, cab ? { bold: true, color: "FFFFFF", size: 19, monoSize: 18 } : { size: 19, monoSize: 18 }),
    })],
  });
  const linhas = [new TableRow({ tableHeader: true, cantSplit: true, children: b.head.map((c, i) => celula(c, i, true)) })];
  b.rows.forEach((r, k) => linhas.push(new TableRow({ cantSplit: true, children: r.map((c, i) => celula(c, i, false, k % 2 === 1, k)) })));
  return [
    new Table({ width: { size: LARG_UTIL, type: WidthType.DXA }, columnWidths: cols, rows: linhas }),
    new Paragraph({ spacing: { after: 120 }, children: [] }),
  ];
}

function imagem(b) {
  const { width, height } = sizeOf(b.path);
  const maxW = LARG_UTIL_PT, maxH = b.max_h / 2.54 * 72;
  const esc = Math.min(maxW / width, maxH / height);
  return new Paragraph({
    alignment: AlignmentType.CENTER, keepNext: true, spacing: { before: 60, after: 0 },
    children: [new ImageRun({
      type: "png", data: fs.readFileSync(b.path),
      transformation: { width: PX(width * esc), height: PX(height * esc) },
    })],
  });
}

function bloco(b, i) {
  const prox = BLOCOS[i + 1] || {};
  switch (b.k) {
    case "h1": return new Paragraph({ heading: HeadingLevel.HEADING_1, children: runs(b.r) });
    case "h2": return new Paragraph({ heading: HeadingLevel.HEADING_2, children: runs(b.r) });
    case "h3": return new Paragraph({ heading: HeadingLevel.HEADING_3, children: runs(b.r) });
    case "p": return new Paragraph({ style: "Corpo", children: runs(b.r) });
    case "pbold": return new Paragraph({ style: "Corpo", keepNext: true, spacing: { after: 20 }, children: runs(b.r, { bold: true }) });
    case "bullet": return new Paragraph({ style: "Corpo", numbering: { reference: "marcadores", level: 0 }, children: runs(b.r) });
    case "hier": return new Paragraph({
      indent: { left: 400 }, spacing: { after: 20 }, keepNext: prox.k === "hier",
      children: runs(b.r, { font: MONO, size: 19, monoSize: 19 }),
    });
    case "caption": return new Paragraph({ style: "Legenda", children: runs(b.r, { italics: true }) });
    case "pagebreak": return new Paragraph({ children: [new PageBreak()] });
    case "table": return tabela(b);
    case "img": return imagem(b);
    default: throw new Error("bloco desconhecido: " + b.k);
  }
}

// ---------- capa ----------
const C = (texto, o = {}) => new Paragraph({
  alignment: AlignmentType.CENTER, spacing: { after: o.after ?? 40, before: o.before ?? 0 },
  children: [new TextRun({ text: texto, font: SERIF, bold: o.bold, italics: o.italics, size: o.size || 24, color: o.color })],
});
function tabelaIntegrantes() {
  const w = [6200, 2306];
  const borda = { style: BorderStyle.SINGLE, size: 4, color: "808080" };
  const bs = { top: borda, bottom: borda, left: borda, right: borda };
  const cel = (t, i, cab) => new TableCell({
    width: { size: w[i], type: WidthType.DXA }, borders: bs, margins: { top: 60, bottom: 60, left: 100, right: 100 },
    shading: { type: ShadingType.CLEAR, color: "auto", fill: cab ? "E8EDF5" : "FFFFFF" },
    children: [new Paragraph({ spacing: { after: 0 }, children: [new TextRun({ text: t, font: SERIF, size: 22, bold: cab })] })],
  });
  const rows = [new TableRow({ children: [cel("Integrante", 0, true), cel("Nº USP", 1, true)] })];
  const INTEGRANTES = [["Ivan Sardon Medina", "[Nº USP]"], ["Vinícius Morotti", "[Nº USP]"], ["Germano Antonio Zani Jorge", "[Nº USP]"], ["Matheus Rodrigues", "[Nº USP]"]];
  for (const [nome, nusp] of INTEGRANTES) rows.push(new TableRow({ children: [cel(nome, 0), cel(nusp, 1)] }));
  return new Table({ width: { size: 8506, type: WidthType.DXA }, columnWidths: w, rows, alignment: AlignmentType.CENTER });
}
const capa = [
  C("Departamento de Ciências de Computação – SCC", { bold: true, before: 400 }),
  C("Instituto de Ciências Matemáticas e de Computação – ICMC", { bold: true }),
  C("Universidade de São Paulo – USP", { bold: true }),
  C("Disciplina SCC0245 – Processamento Analítico de Dados", { bold: true, after: 240 }),
  C("Docente Responsável: Profa. Cristina Dutra de Aguiar", { bold: true, after: 1400 }),
  C("Trabalho Prático 1", { bold: true, size: 26, after: 200 }),
  C("Data Warehouse para Análise da Cobertura da Atenção Primária a Saúde em São Carlos", { bold: true, size: 36, color: AZUL, after: 160 }),
  C("Unidades e equipes de saúde, demanda ambulatorial e internações evitáveis", { italics: true, size: 24, after: 1400 }),
  tabelaIntegrantes(),
  C("São Carlos, 29 de Outubro de 2026", { before: 1400 }),
];

// ---------- índice ----------
const indice = [
  new Paragraph({ children: [new PageBreak()] }),
  new Paragraph({ style: "TituloIndice", children: [new TextRun({ text: "Índice" })] }),
  new TableOfContents("Índice", { hyperlink: true, headingStyleRange: "1-2" }),
  new Paragraph({ children: [new PageBreak()] }),
];

const corpo = BLOCOS.flatMap((b, i) => [].concat(bloco(b, i)));

const doc = new Document({
  creator: "Grupo SCC0245", title: "Data Warehouse – Cobertura da Atenção Primária a Saúde em São Carlos",
  features: { updateFields: true },
  styles: {
    default: { document: { run: { font: SERIF, size: 24 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { font: SERIF, size: 32, bold: true, color: AZUL },
        paragraph: { spacing: { before: 120, after: 200 }, keepNext: true, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { font: SERIF, size: 26, bold: true, color: AZUL },
        paragraph: { spacing: { before: 240, after: 120 }, keepNext: true, outlineLevel: 1 } },
      { id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { font: SERIF, size: 24, bold: true },
        paragraph: { spacing: { before: 180, after: 80 }, keepNext: true, outlineLevel: 2 } },
      { id: "Corpo", name: "Corpo do texto", basedOn: "Normal", quickFormat: true,
        run: { font: SERIF, size: 24 },
        paragraph: { alignment: AlignmentType.JUSTIFIED, spacing: { after: 120, line: 288 } } },
      { id: "Legenda", name: "Legenda da figura", basedOn: "Normal", quickFormat: true,
        run: { font: SERIF, size: 20, italics: true },
        paragraph: { alignment: AlignmentType.CENTER, spacing: { before: 60, after: 240 } } },
      { id: "TituloIndice", name: "Título do índice", basedOn: "Normal",
        run: { font: SERIF, size: 32, bold: true, color: AZUL }, paragraph: { spacing: { after: 240 } } },
    ],
  },
  numbering: { config: [{ reference: "marcadores", levels: [{
    level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT,
    style: { paragraph: { indent: { left: 400, hanging: 260 } } } }] }] },
  sections: [{
    properties: {
      titlePage: true,
      page: { size: { width: 11906, height: 16838 },
              margin: { top: 2200, bottom: 1500, left: MARG_ESQ, right: MARG_DIR, header: 300, footer: 500 } },
    },
    headers: { default: cabecalho(), first: cabecalho() },
    footers: { default: rodape(), first: rodapeCapa() },
    children: [...capa, ...indice, ...corpo],
  }],
});

Packer.toBuffer(doc).then((buf) => {
  fs.writeFileSync("bruto.docx", buf);
  console.log("ok", corpo.length, "parágrafos/tabelas");
});
