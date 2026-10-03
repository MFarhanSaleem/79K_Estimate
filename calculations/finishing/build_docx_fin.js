// Renders blocks_stepA.json (written by stepA.py) into the finishing Step A Word file.
// usage: NODE_PATH=<dir with docx> node build_docx_fin.js blocks_stepA.json out.docx
const fs = require('fs');
const path = require('path');
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, WidthType, AlignmentType,
  HeadingLevel, ShadingType, BorderStyle, PageOrientation, Header, Footer, PageNumber,
  LevelFormat, TableLayoutType, VerticalAlign, PageBreak, ImageRun
} = require('docx');

const BLOCKS = process.argv[2] || path.join(__dirname, 'blocks_stepA.json');
const OUT = process.argv[3] || path.join(__dirname, 'House_79K_Finishing_StepA_Schedules_and_Questions.docx');
const blocks = JSON.parse(fs.readFileSync(BLOCKS, 'utf8'));

const NAVY = '1F3864', BLUE = '2E5597', GREY = '595959';
const FONT = 'Calibri';
const A4W = 11906, A4H = 16838;
const MARG = { PORTRAIT: 1000, LANDSCAPE: 900 };
const LS = ' ';                       // line break inside a table cell

const border = { style: BorderStyle.SINGLE, size: 4, color: 'A6A6A6' };
const borders = { top: border, bottom: border, left: border, right: border };
const noB = { style: BorderStyle.NONE, size: 0, color: 'FFFFFF' };
const ALIGN = { L: AlignmentType.LEFT, R: AlignmentType.RIGHT, C: AlignmentType.CENTER };

let numInstance = 0;

function runs(text, opts = {}) {
  return [new TextRun({ text: String(text), font: FONT, size: opts.size || 20, bold: !!opts.bold,
    italics: !!opts.italics, color: opts.color || undefined })];
}
function para(text, opts = {}) {
  return new Paragraph({ children: runs(text, opts), alignment: opts.align || AlignmentType.LEFT, keepNext: !!opts.keepNext,
    spacing: { before: opts.before ?? 60, after: opts.after ?? 100, line: opts.line || 264 } });
}
// A line starting with '§' is bold (used for the location line in BOQ cells).
function cellPara(text, align, size, bold, color) {
  return String(text).split(LS).map(t => {
    const b = t.startsWith('§');
    return new Paragraph({ children: runs(b ? t.slice(1) : t, { size, bold: bold || b, color }), alignment: align,
      spacing: { before: 10, after: 10, line: 228 } });
  });
}
function makeTable(b, contentWidth) {
  const widths = b.widths.slice();
  const sum = widths.reduce((a, c) => a + c, 0);
  if (sum !== contentWidth) widths[1] += contentWidth - sum;   // absorb rounding in 2nd column
  const size = Math.round((b.font || 9) * 2);
  const header = new TableRow({
    tableHeader: true, cantSplit: true,
    children: b.header.map((h, i) => new TableCell({
      width: { size: widths[i], type: WidthType.DXA }, borders,
      shading: { fill: NAVY, type: ShadingType.CLEAR, color: 'auto' },
      margins: { top: 40, bottom: 40, left: 50, right: 50 }, verticalAlign: VerticalAlign.CENTER,
      children: cellPara(h, AlignmentType.CENTER, size, true, 'FFFFFF') }))
  });
  const rows = [header];
  let band = 0;
  b.rows.forEach(r => {
    const kind = r.kind || '';
    let fill = band % 2 === 1 ? 'F3F6FB' : 'FFFFFF';
    let bold = false;
    if (kind === 'section') { fill = 'D9E2F3'; bold = true; band = 0; }
    else if (kind === 'subtotal') { fill = 'EDEDED'; bold = true; }
    else if (kind === 'gross') { fill = 'F7F7F7'; }
    else if (kind === 'total') { fill = 'C6D9F1'; bold = true; }
    else if (kind === 'pass') { fill = 'E2EFDA'; }
    else band += 1;
    if (kind === 'section') {
      rows.push(new TableRow({ cantSplit: true, children: [new TableCell({
        columnSpan: widths.length, width: { size: contentWidth, type: WidthType.DXA }, borders,
        shading: { fill, type: ShadingType.CLEAR, color: 'auto' }, margins: { top: 40, bottom: 40, left: 60, right: 60 },
        children: cellPara(r.cells[0], AlignmentType.LEFT, size + 2, true, NAVY) })] }));
      return;
    }
    rows.push(new TableRow({ cantSplit: true, children: r.cells.map((c, i) => new TableCell({
      width: { size: widths[i], type: WidthType.DXA }, borders,
      shading: { fill, type: ShadingType.CLEAR, color: 'auto' },
      margins: { top: 30, bottom: 30, left: 50, right: 50 }, verticalAlign: VerticalAlign.TOP,
      children: cellPara(c, ALIGN[(b.align || [])[i] || 'L'], size, bold) })) }));
  });
  return new Table({ width: { size: contentWidth, type: WidthType.DXA }, columnWidths: widths,
    layout: TableLayoutType.FIXED, rows });
}
function keyBoxes(b, cw) {
  const out = [];
  const n = b.keys.length;
  const kw = Math.floor(cw / n);
  const kws = b.keys.map((_, i) => i === n - 1 ? cw - kw * (n - 1) : kw);
  const wb = { style: BorderStyle.SINGLE, size: 18, color: 'FFFFFF' };
  const keyRow = new TableRow({ children: b.keys.map((k, i) => new TableCell({
    width: { size: kws[i], type: WidthType.DXA }, borders: { top: wb, bottom: wb, left: wb, right: wb },
    shading: { fill: i % 2 ? BLUE : NAVY, type: ShadingType.CLEAR, color: 'auto' },
    margins: { top: 100, bottom: 100, left: 70, right: 70 },
    children: [
      new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 30 }, children: [new TextRun({ text: k[0], font: FONT, size: 17, color: 'DCE6F2' })] }),
      new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 20 }, children: [new TextRun({ text: k[1], font: FONT, size: 28, bold: true, color: 'FFFFFF' })] }),
      new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: k[2], font: FONT, size: 15, color: 'DCE6F2' })] })] })) });
  out.push(new Table({ width: { size: cw, type: WidthType.DXA }, columnWidths: kws, layout: TableLayoutType.FIXED, rows: [keyRow] }));
  out.push(para('', { before: 0, after: 60, size: 8 }));
  return out;
}
function kvTable(b, cw) {
  const lw = b.lw || 2600, rw = cw - lw;
  const bb = { top: border, bottom: border, left: noB, right: noB };
  return new Table({ width: { size: cw, type: WidthType.DXA }, columnWidths: [lw, rw], layout: TableLayoutType.FIXED,
    rows: b.lines.map(([k, v]) => new TableRow({ cantSplit: true, children: [
      new TableCell({ width: { size: lw, type: WidthType.DXA }, borders: bb, margins: { top: 50, bottom: 50, left: 60, right: 100 },
        children: cellPara(k, AlignmentType.LEFT, b.size || 19, true, NAVY) }),
      new TableCell({ width: { size: rw, type: WidthType.DXA }, borders: bb, margins: { top: 50, bottom: 50, left: 100, right: 60 },
        children: cellPara(v, AlignmentType.LEFT, b.size || 19, false) })] })) });
}

// ---- split into sections
const sections = [];
let cur = null;
for (const b of blocks) {
  if (b.type === 'section') { cur = { orientation: b.orientation, blocks: [] }; sections.push(cur); continue; }
  cur.blocks.push(b);
}
const docSections = sections.map(s => {
  const land = s.orientation === 'LANDSCAPE';
  const m = land ? MARG.LANDSCAPE : MARG.PORTRAIT;
  const cw = (land ? A4H : A4W) - 2 * m;
  const children = [];
  for (const b of s.blocks) {
    if (b.type === 'title') {
      children.push(new Paragraph({ spacing: { before: b.before ?? 120, after: 80 }, children: [new TextRun({ text: b.title, font: FONT, size: b.size || 40, bold: true, color: NAVY })] }));
      children.push(new Paragraph({ spacing: { before: 0, after: 160 }, border: { bottom: { style: BorderStyle.SINGLE, size: 12, color: BLUE, space: 6 } },
        children: [new TextRun({ text: b.subtitle, font: FONT, size: 23, color: BLUE })] }));
    }
    else if (b.type === 'keys') children.push(...keyBoxes(b, cw));
    else if (b.type === 'kv') { children.push(kvTable(b, cw)); children.push(para('', { before: 0, after: 80, size: 8 })); }
    else if (b.type === 'pagebreak') children.push(new Paragraph({ children: [new PageBreak()] }));
    else if (b.type === 'h1') children.push(new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun({ text: b.text })],
                                   spacing: { before: 200, after: 100 }, keepNext: true, pageBreakBefore: !!b.newpage }));
    else if (b.type === 'h2') children.push(new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun({ text: b.text })],
                                   spacing: { before: 160, after: 70 }, keepNext: true }));
    else if (b.type === 'p') children.push(para(b.text, { size: b.size, bold: b.bold, keepNext: b.keepNext }));
    else if (b.type === 'note') children.push(para(b.text, { italics: true, size: b.size || 17, color: GREY, before: 40, after: 80 }));
    else if (b.type === 'bullets') b.items.forEach(t => children.push(new Paragraph({ numbering: { reference: 'bullets', level: 0 },
                                   children: runs(t, { size: b.size || 19 }), spacing: { before: 10, after: 40, line: 247 } })));
    else if (b.type === 'numbers') { numInstance += 1; const inst = numInstance;
      b.items.forEach(t => children.push(new Paragraph({ numbering: { reference: 'numbers', level: 0, instance: inst },
                                   children: runs(t, { size: b.size || 19 }), spacing: { before: 10, after: 40, line: 247 } }))); }
    else if (b.type === 'table') { children.push(makeTable(b, cw)); children.push(para('', { before: 0, after: 60, size: 8 })); }
    else if (b.type === 'image') {
      const data = fs.readFileSync(b.path);
      children.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 60, after: 60 },
        children: [new ImageRun({ type: 'png', data, transformation: { width: b.width, height: b.height },
          altText: { title: b.alt || 'figure', description: b.alt || 'figure', name: 'figure' } })] }));
    }
    else throw new Error('unknown block type ' + b.type);
  }
  return {
    properties: { page: { size: { width: A4W, height: A4H, orientation: land ? PageOrientation.LANDSCAPE : PageOrientation.PORTRAIT },
                          margin: { top: 950, bottom: 850, left: m, right: m, header: 450, footer: 420 } } },
    headers: { default: new Header({ children: [new Paragraph({ alignment: AlignmentType.RIGHT,
      border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: 'BFBFBF', space: 4 } },
      children: [new TextRun({ text: 'Finishing - Step A: schedules and questions  |  House No. 79/K (Mr. Saleem)  |  Measurement only, not priced', font: FONT, size: 16, color: GREY })] })] }) },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER,
      children: [new TextRun({ children: ['Page ', PageNumber.CURRENT, ' of ', PageNumber.TOTAL_PAGES], font: FONT, size: 16, color: GREY })] })] }) },
    children
  };
});

const doc = new Document({
  creator: 'Estimate for Mr. Saleem', title: 'Finishing Step A - House 79/K',
  description: 'Finishing schedules, measurements and questionnaire',
  styles: {
    default: { document: { run: { font: FONT, size: 20 } } },
    paragraphStyles: [
      { id: 'Heading1', name: 'Heading 1', basedOn: 'Normal', next: 'Normal', quickFormat: true,
        run: { size: 28, bold: true, font: FONT, color: NAVY }, paragraph: { spacing: { before: 200, after: 100 }, outlineLevel: 0 } },
      { id: 'Heading2', name: 'Heading 2', basedOn: 'Normal', next: 'Normal', quickFormat: true,
        run: { size: 22, bold: true, font: FONT, color: BLUE }, paragraph: { spacing: { before: 160, after: 70 }, outlineLevel: 1 } },
    ]
  },
  numbering: { config: [
    { reference: 'bullets', levels: [{ level: 0, format: LevelFormat.BULLET, text: '•', alignment: AlignmentType.LEFT,
        style: { paragraph: { indent: { left: 500, hanging: 260 } } } }] },
    { reference: 'numbers', levels: [{ level: 0, format: LevelFormat.DECIMAL, text: '%1.', alignment: AlignmentType.LEFT,
        style: { paragraph: { indent: { left: 560, hanging: 380 } }, run: { size: 15 } } }] },
  ] },
  sections: docSections
});
Packer.toBuffer(doc).then(buf => { fs.writeFileSync(OUT, buf); console.log('written', OUT, buf.length, 'bytes'); });
