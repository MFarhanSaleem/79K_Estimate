const fs = require('fs');
const path = require('path');
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, WidthType, AlignmentType,
  HeadingLevel, ShadingType, BorderStyle, PageOrientation, Header, Footer, PageNumber,
  LevelFormat, TableLayoutType, VerticalAlign, PageBreak
} = require('docx');

const blocks = JSON.parse(fs.readFileSync(path.join(__dirname, 'blocks.json'), 'utf8'));
const OUT = process.argv[2] || path.join(__dirname, 'estimate.docx');

const NAVY = '1F3864', BLUE = '2E5597', GREY = '595959';
const FONT = 'Calibri';
const A4W = 11906, A4H = 16838;
const MARG = { PORTRAIT: 1000, LANDSCAPE: 900 };

const border = { style: BorderStyle.SINGLE, size: 4, color: 'A6A6A6' };
const borders = { top: border, bottom: border, left: border, right: border };
const ALIGN = { L: AlignmentType.LEFT, R: AlignmentType.RIGHT, C: AlignmentType.CENTER };

let numInstance = 0;

function runs(text, opts = {}) {
  return [new TextRun({ text: String(text), font: FONT, size: opts.size || 20, bold: !!opts.bold,
    italics: !!opts.italics, color: opts.color || undefined })];
}
function para(text, opts = {}) {
  return new Paragraph({ children: runs(text, opts), alignment: opts.align || AlignmentType.LEFT,
    spacing: { before: opts.before ?? 60, after: opts.after ?? 100, line: opts.line || 264 } });
}
function cellPara(text, align, size, bold, color) {
  const lines = String(text).split(' ');
  return lines.map(t => new Paragraph({ children: runs(t, { size, bold, color }), alignment: align,
    spacing: { before: 20, after: 20, line: 240 } }));
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
      margins: { top: 50, bottom: 50, left: 70, right: 70 }, verticalAlign: VerticalAlign.CENTER,
      children: cellPara(h, AlignmentType.CENTER, size, true, 'FFFFFF') }))
  });
  const rows = [header];
  b.rows.forEach((r, ri) => {
    const kind = r.kind || '';
    let fill = ri % 2 === 1 ? 'F3F6FB' : 'FFFFFF';
    let bold = false;
    if (kind === 'section') { fill = 'D9E2F3'; bold = true; }
    if (kind === 'subtotal') { fill = 'EDEDED'; bold = true; }
    if (kind === 'total') { fill = 'C6D9F1'; bold = true; }
    if (kind === 'section') {
      rows.push(new TableRow({ cantSplit: true, children: [new TableCell({
        columnSpan: widths.length, width: { size: contentWidth, type: WidthType.DXA }, borders,
        shading: { fill, type: ShadingType.CLEAR, color: 'auto' }, margins: { top: 50, bottom: 50, left: 70, right: 70 },
        children: cellPara(r.cells[0], AlignmentType.LEFT, size + 1, true, NAVY) })] }));
      return;
    }
    rows.push(new TableRow({ cantSplit: true, children: r.cells.map((c, i) => new TableCell({
      width: { size: widths[i], type: WidthType.DXA }, borders,
      shading: { fill, type: ShadingType.CLEAR, color: 'auto' },
      margins: { top: 40, bottom: 40, left: 70, right: 70 }, verticalAlign: VerticalAlign.CENTER,
      children: cellPara(c, ALIGN[(b.align || [])[i] || 'L'], size, bold) })) }));
  });
  return new Table({ width: { size: contentWidth, type: WidthType.DXA }, columnWidths: widths,
    layout: TableLayoutType.FIXED, rows });
}
function coverBlocks(b, cw) {
  const out = [];
  out.push(new Paragraph({ spacing: { before: 1400, after: 120 }, alignment: AlignmentType.LEFT,
    children: [new TextRun({ text: b.title, font: FONT, size: 44, bold: true, color: NAVY })] }));
  out.push(new Paragraph({ spacing: { before: 0, after: 360 }, border: { bottom: { style: BorderStyle.SINGLE, size: 12, color: BLUE, space: 8 } },
    children: [new TextRun({ text: b.subtitle, font: FONT, size: 26, color: BLUE })] }));
  // key figures boxes
  const kw = Math.floor(cw / b.keys.length);
  const kws = b.keys.map((_, i) => i === b.keys.length - 1 ? cw - kw * (b.keys.length - 1) : kw);
  const keyRow = new TableRow({ children: b.keys.map((k, i) => new TableCell({
    width: { size: kws[i], type: WidthType.DXA },
    borders: { top: { style: BorderStyle.SINGLE, size: 18, color: 'FFFFFF' }, bottom: { style: BorderStyle.SINGLE, size: 18, color: 'FFFFFF' },
               left: { style: BorderStyle.SINGLE, size: 18, color: 'FFFFFF' }, right: { style: BorderStyle.SINGLE, size: 18, color: 'FFFFFF' } },
    shading: { fill: i % 2 ? BLUE : NAVY, type: ShadingType.CLEAR, color: 'auto' },
    margins: { top: 140, bottom: 140, left: 80, right: 80 },
    children: [
      new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 40 }, children: [new TextRun({ text: k[0], font: FONT, size: 18, color: 'DCE6F2' })] }),
      new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 20 }, children: [new TextRun({ text: k[1], font: FONT, size: 36, bold: true, color: 'FFFFFF' })] }),
      new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: k[2], font: FONT, size: 17, color: 'DCE6F2' })] })] })) });
  out.push(para('Quantities to procure (upper estimate, including wastage)', { size: 20, bold: true, color: GREY, after: 80 }));
  out.push(new Table({ width: { size: cw, type: WidthType.DXA }, columnWidths: kws, layout: TableLayoutType.FIXED, rows: [keyRow] }));
  out.push(para(' ', { after: 200 }));
  const lw = 2600, rw = cw - lw;
  out.push(new Table({ width: { size: cw, type: WidthType.DXA }, columnWidths: [lw, rw], layout: TableLayoutType.FIXED,
    rows: b.lines.map(([k, v]) => new TableRow({ children: [
      new TableCell({ width: { size: lw, type: WidthType.DXA }, borders: { top: border, bottom: border, left: { style: BorderStyle.NONE, size: 0, color: 'FFFFFF' }, right: { style: BorderStyle.NONE, size: 0, color: 'FFFFFF' } },
        margins: { top: 60, bottom: 60, left: 60, right: 100 }, children: cellPara(k, AlignmentType.LEFT, 19, true, NAVY) }),
      new TableCell({ width: { size: rw, type: WidthType.DXA }, borders: { top: border, bottom: border, left: { style: BorderStyle.NONE, size: 0, color: 'FFFFFF' }, right: { style: BorderStyle.NONE, size: 0, color: 'FFFFFF' } },
        margins: { top: 60, bottom: 60, left: 100, right: 60 }, children: cellPara(v, AlignmentType.LEFT, 19, false) })] })) }));
  return out;
}

// ---- split into sections
const sections = [];
let cur = null;
for (const b of blocks) {
  if (b.type === 'section') { cur = { orientation: b.orientation, blocks: [] }; sections.push(cur); continue; }
  cur.blocks.push(b);
}
const docSections = sections.map((s, si) => {
  const land = s.orientation === 'LANDSCAPE';
  const m = land ? MARG.LANDSCAPE : MARG.PORTRAIT;
  const cw = (land ? A4H : A4W) - 2 * m;
  const children = [];
  for (const b of s.blocks) {
    if (b.type === 'cover') children.push(...coverBlocks(b, cw));
    else if (b.type === 'pagebreak') children.push(new Paragraph({ children: [new PageBreak()] }));
    else if (b.type === 'h1') children.push(new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun({ text: b.text })],
                                   spacing: { before: 240, after: 120 }, keepNext: true }));
    else if (b.type === 'h2') children.push(new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun({ text: b.text })],
                                   spacing: { before: 180, after: 80 }, keepNext: true }));
    else if (b.type === 'p') children.push(para(b.text, {}));
    else if (b.type === 'note') children.push(para(b.text, { italics: true, size: 18, color: GREY, before: 80 }));
    else if (b.type === 'bullets') b.items.forEach(t => children.push(new Paragraph({ numbering: { reference: 'bullets', level: 0 },
                                   children: runs(t, { size: 19 }), spacing: { before: 20, after: 60, line: 252 } })));
    else if (b.type === 'numbers') { numInstance += 1; const inst = numInstance;
      b.items.forEach(t => children.push(new Paragraph({ numbering: { reference: 'numbers', level: 0, instance: inst },
                                   children: runs(t, { size: 19 }), spacing: { before: 20, after: 60, line: 252 } }))); }
    else if (b.type === 'table') { children.push(makeTable(b, cw)); children.push(para('', { before: 0, after: 80, size: 8 })); }
  }
  return {
    properties: { page: { size: { width: A4W, height: A4H, orientation: land ? PageOrientation.LANDSCAPE : PageOrientation.PORTRAIT },
                          margin: { top: 1000, bottom: 900, left: m, right: m, header: 500, footer: 450 } } },
    headers: { default: new Header({ children: [new Paragraph({ alignment: AlignmentType.RIGHT,
      border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: 'BFBFBF', space: 4 } },
      children: [new TextRun({ text: 'Grey Structure Material Estimate  |  House No. 79/K (Mr. Saleem)  |  Upper estimate incl. wastage', font: FONT, size: 16, color: GREY })] })] }) },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER,
      children: [new TextRun({ children: ['Page ', PageNumber.CURRENT, ' of ', PageNumber.TOTAL_PAGES], font: FONT, size: 16, color: GREY })] })] }) },
    children
  };
});

const doc = new Document({
  creator: 'Estimate for Mr. Saleem', title: 'Grey Structure Material Estimate - House 79/K',
  description: 'Grey structure quantity estimate from structural and working drawings',
  styles: {
    default: { document: { run: { font: FONT, size: 20 } } },
    paragraphStyles: [
      { id: 'Heading1', name: 'Heading 1', basedOn: 'Normal', next: 'Normal', quickFormat: true,
        run: { size: 30, bold: true, font: FONT, color: NAVY }, paragraph: { spacing: { before: 240, after: 120 }, outlineLevel: 0 } },
      { id: 'Heading2', name: 'Heading 2', basedOn: 'Normal', next: 'Normal', quickFormat: true,
        run: { size: 23, bold: true, font: FONT, color: BLUE }, paragraph: { spacing: { before: 180, after: 80 }, outlineLevel: 1 } },
    ]
  },
  numbering: { config: [
    { reference: 'bullets', levels: [{ level: 0, format: LevelFormat.BULLET, text: '•', alignment: AlignmentType.LEFT,
        style: { paragraph: { indent: { left: 540, hanging: 280 } } } }] },
    { reference: 'numbers', levels: [{ level: 0, format: LevelFormat.DECIMAL, text: '%1.', alignment: AlignmentType.LEFT,
        style: { paragraph: { indent: { left: 620, hanging: 420 } } } }] },
  ] },
  sections: docSections
});
Packer.toBuffer(doc).then(buf => { fs.writeFileSync(OUT, buf); console.log('written', OUT, buf.length, 'bytes'); });
