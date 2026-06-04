import { jsPDF } from 'jspdf';

// ── Plain-text formatters ────────────────────────────────────────────────────

function slidesToText(slides) {
  return slides.map(s =>
    `Slide ${s.slide_number}: ${s.title}\n` +
    s.key_points.map(p => `  • ${p}`).join('\n') +
    (s.teacher_note ? `\n  Teacher note: ${s.teacher_note}` : '')
  ).join('\n\n');
}

function quizToText(questions) {
  return questions.map((q, i) =>
    `Q${i + 1}: ${q.question}\n` +
    q.options.join('  ') +
    `\nAnswer: ${q.answer}` +
    (q.explanation ? `\n${q.explanation}` : '')
  ).join('\n\n');
}

function assignmentToText(a) {
  return (
    `${a.title}\n\nObjective: ${a.objective}\n\n` +
    `Instructions:\n${a.instructions.map((s, i) => `${i + 1}. ${s}`).join('\n')}\n\n` +
    `Submission: ${a.submission_format}\nEstimated time: ${a.estimated_time}`
  );
}

function rubricToText(rubric) {
  return rubric.map(r =>
    `${r.criterion}\n` +
    `  Excellent: ${r.excellent}\n` +
    `  Good: ${r.good}\n` +
    `  Needs Improvement: ${r.needs_improvement}`
  ).join('\n\n');
}

function faqToText(faq) {
  return faq.map((f, i) => `Q${i + 1}: ${f.question}\nA: ${f.answer}`).join('\n\n');
}

const FORMATTERS = {
  slides:     slidesToText,
  quiz:       quizToText,
  assignment: assignmentToText,
  rubric:     rubricToText,
  faq:        faqToText,
};

// ── Public API ───────────────────────────────────────────────────────────────

/**
 * Copy a section's content to clipboard as readable plain text.
 * @param {string} section  One of: slides, quiz, assignment, rubric, faq
 * @param {Array|Object} content
 * @returns {Promise<void>}
 */
export function copySection(section, content) {
  const key = section.toLowerCase();
  const format = FORMATTERS[key];
  const text = format ? format(content) : JSON.stringify(content, null, 2);
  return navigator.clipboard.writeText(text);
}

// ── PDF helpers ──────────────────────────────────────────────────────────────

const MARGIN = 18;        // mm from left/right edges
const PAGE_W = 210;       // A4 width mm
const PAGE_H = 297;       // A4 height mm
const CONTENT_W = PAGE_W - MARGIN * 2;
const BODY_TOP = 28;      // y below section header

function slug(str) {
  return str.toLowerCase().replace(/[^a-z0-9]+/g, '_').replace(/^_|_$/g, '');
}

/** Write a page header bar and return the y cursor below it. */
function pageHeader(doc, title, pageNum) {
  doc.setFillColor(79, 70, 229);
  doc.rect(0, 0, PAGE_W, 16, 'F');
  doc.setTextColor(255, 255, 255);
  doc.setFontSize(10);
  doc.setFont('helvetica', 'bold');
  doc.text(title, MARGIN, 10.5);
  doc.setFont('helvetica', 'normal');
  doc.text(`${pageNum}`, PAGE_W - MARGIN, 10.5, { align: 'right' });
  doc.setTextColor(30, 30, 30);
  return BODY_TOP;
}

/** Write wrapped text; returns new y. Adds a page if needed. */
function wrappedText(doc, text, x, y, maxWidth, lineHeight, boldFirst = false) {
  const lines = doc.splitTextToSize(text, maxWidth);
  lines.forEach((line, i) => {
    if (y > PAGE_H - 20) { doc.addPage(); y = BODY_TOP; }
    if (boldFirst && i === 0) doc.setFont('helvetica', 'bold');
    doc.text(line, x, y);
    if (boldFirst && i === 0) doc.setFont('helvetica', 'normal');
    y += lineHeight;
  });
  return y;
}

// ── Section renderers ────────────────────────────────────────────────────────

function renderTitlePage(doc, lessonData) {
  // Background
  doc.setFillColor(245, 243, 255);
  doc.rect(0, 0, PAGE_W, PAGE_H, 'F');

  // Top accent bar
  doc.setFillColor(79, 70, 229);
  doc.rect(0, 0, PAGE_W, 40, 'F');

  // App name
  doc.setTextColor(255, 255, 255);
  doc.setFontSize(13);
  doc.setFont('helvetica', 'normal');
  doc.text('ClassroomAgent', PAGE_W / 2, 18, { align: 'center' });

  // Topic
  doc.setFontSize(26);
  doc.setFont('helvetica', 'bold');
  doc.text(lessonData.topic, PAGE_W / 2, 70, { align: 'center' });

  // Meta pills (drawn as text rows)
  doc.setFontSize(12);
  doc.setFont('helvetica', 'normal');
  doc.setTextColor(79, 70, 229);
  doc.text(`${lessonData.grade}  •  ${lessonData.subject}`, PAGE_W / 2, 90, { align: 'center' });

  // Generated date
  doc.setFontSize(9);
  doc.setTextColor(120, 120, 120);
  const date = lessonData.generated_at
    ? new Date(lessonData.generated_at).toLocaleDateString('en-IN', { day: 'numeric', month: 'long', year: 'numeric' })
    : new Date().toLocaleDateString();
  doc.text(`Generated on ${date}`, PAGE_W / 2, 108, { align: 'center' });

  // Table of contents
  doc.setTextColor(55, 65, 81);
  doc.setFontSize(10);
  doc.setFont('helvetica', 'bold');
  doc.text('Contents', MARGIN, 145);
  doc.setFont('helvetica', 'normal');
  const toc = ['Slides', 'Quiz', 'Assignment', 'Rubric', 'FAQ'];
  toc.forEach((item, i) => {
    doc.text(`${i + 2}.  ${item}`, MARGIN + 6, 157 + i * 10);
  });
}

function renderSlides(doc, slides, startPage) {
  let pg = startPage;
  slides.forEach((slide) => {
    if (slide.slide_number > 1) doc.addPage();
    let y = pageHeader(doc, `Slides  —  ${slide.slide_number} of ${slides.length}`, pg++);

    // Slide title
    doc.setFontSize(14);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(79, 70, 229);
    y = wrappedText(doc, slide.title, MARGIN, y, CONTENT_W, 7);
    doc.setTextColor(30, 30, 30);
    y += 3;

    // Key points
    doc.setFontSize(10);
    doc.setFont('helvetica', 'normal');
    slide.key_points.forEach(pt => {
      y = wrappedText(doc, `• ${pt}`, MARGIN + 4, y, CONTENT_W - 4, 6);
      y += 1;
    });

    // Teacher note
    if (slide.teacher_note) {
      y += 5;
      doc.setFillColor(249, 250, 251);
      // measure height before drawing box
      const noteLines = doc.splitTextToSize(`Teacher note: ${slide.teacher_note}`, CONTENT_W - 8);
      const boxH = noteLines.length * 5.5 + 6;
      if (y + boxH > PAGE_H - 20) { doc.addPage(); y = BODY_TOP; pg++; }
      doc.roundedRect(MARGIN, y, CONTENT_W, boxH, 2, 2, 'F');
      doc.setTextColor(107, 114, 128);
      doc.setFontSize(9);
      doc.setFont('helvetica', 'italic');
      y = wrappedText(doc, `Teacher note: ${slide.teacher_note}`, MARGIN + 4, y + 4.5, CONTENT_W - 8, 5.5);
      doc.setFont('helvetica', 'normal');
      doc.setTextColor(30, 30, 30);
    }
  });
  return pg;
}

function renderQuiz(doc, questions, startPage) {
  doc.addPage();
  let pg = startPage;
  let y = pageHeader(doc, 'Quiz', pg++);
  doc.setFontSize(10);

  questions.forEach((q, i) => {
    if (y > PAGE_H - 50) { doc.addPage(); y = pageHeader(doc, 'Quiz (continued)', pg++); }

    // Question
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(30, 30, 30);
    y = wrappedText(doc, `Q${i + 1}. ${q.question}`, MARGIN, y, CONTENT_W, 6, false);
    doc.setFont('helvetica', 'normal');
    y += 2;

    // Options
    const correctLetter = q.answer?.charAt(0).toUpperCase();
    q.options.forEach(opt => {
      const letter = opt.charAt(0).toUpperCase();
      const isCorrect = letter === correctLetter;
      if (isCorrect) {
        doc.setTextColor(22, 101, 52);
        doc.setFont('helvetica', 'bold');
      } else {
        doc.setTextColor(75, 85, 99);
      }
      y = wrappedText(doc, `  ${opt}${isCorrect ? '  ✓' : ''}`, MARGIN + 4, y, CONTENT_W - 4, 5.5);
      doc.setFont('helvetica', 'normal');
      doc.setTextColor(30, 30, 30);
    });

    // Explanation
    if (q.explanation) {
      y += 1;
      doc.setTextColor(107, 114, 128);
      doc.setFontSize(8.5);
      y = wrappedText(doc, `Explanation: ${q.explanation}`, MARGIN + 4, y, CONTENT_W - 4, 5);
      doc.setFontSize(10);
      doc.setTextColor(30, 30, 30);
    }
    y += 5;
  });
  return pg;
}

function renderAssignment(doc, assignment, startPage) {
  doc.addPage();
  let pg = startPage;
  let y = pageHeader(doc, 'Assignment', pg++);

  doc.setFontSize(15);
  doc.setFont('helvetica', 'bold');
  doc.setTextColor(30, 30, 30);
  y = wrappedText(doc, assignment.title, MARGIN, y, CONTENT_W, 8);
  y += 2;

  doc.setFontSize(10);
  doc.setFont('helvetica', 'normal');
  doc.setTextColor(75, 85, 99);
  y = wrappedText(doc, assignment.objective, MARGIN, y, CONTENT_W, 6);
  y += 5;

  doc.setFont('helvetica', 'bold');
  doc.setTextColor(30, 30, 30);
  doc.text('Instructions', MARGIN, y); y += 6;
  doc.setFont('helvetica', 'normal');
  assignment.instructions.forEach((step, i) => {
    y = wrappedText(doc, `${i + 1}.  ${step}`, MARGIN + 4, y, CONTENT_W - 4, 6);
    y += 1;
  });

  y += 5;
  doc.setFont('helvetica', 'bold');
  doc.text('Submission format:', MARGIN, y); y += 6;
  doc.setFont('helvetica', 'normal');
  doc.setTextColor(75, 85, 99);
  y = wrappedText(doc, assignment.submission_format, MARGIN + 4, y, CONTENT_W - 4, 6);
  y += 4;

  doc.setFont('helvetica', 'bold');
  doc.setTextColor(30, 30, 30);
  doc.text('Estimated time:', MARGIN, y); y += 6;
  doc.setFont('helvetica', 'normal');
  doc.setTextColor(75, 85, 99);
  doc.text(assignment.estimated_time, MARGIN + 4, y);
  return pg;
}

function renderRubric(doc, rubric, startPage) {
  doc.addPage();
  let pg = startPage;
  let y = pageHeader(doc, 'Rubric', pg++);

  const colW = [44, 46, 46, 46];
  const cols = ['Criterion', 'Excellent', 'Good', 'Needs Improvement'];
  const rowH = 8;

  // Header row
  doc.setFillColor(79, 70, 229);
  doc.rect(MARGIN, y, CONTENT_W, rowH, 'F');
  doc.setTextColor(255, 255, 255);
  doc.setFontSize(9);
  doc.setFont('helvetica', 'bold');
  let cx = MARGIN + 2;
  cols.forEach((h, i) => { doc.text(h, cx, y + 5.5); cx += colW[i]; });
  y += rowH;

  // Data rows
  doc.setFont('helvetica', 'normal');
  rubric.forEach((row, ri) => {
    const cells = [row.criterion, row.excellent, row.good, row.needs_improvement];
    // measure max lines in this row for height
    const lineH = 5;
    const lineCounts = cells.map((c, ci) => doc.splitTextToSize(c, colW[ci] - 4).length);
    const maxLines = Math.max(...lineCounts);
    const rh = Math.max(rowH, maxLines * lineH + 4);

    if (y + rh > PAGE_H - 20) { doc.addPage(); y = BODY_TOP; pg++; }

    doc.setFillColor(ri % 2 === 0 ? 249 : 255, ri % 2 === 0 ? 250 : 255, ri % 2 === 0 ? 251 : 255);
    doc.rect(MARGIN, y, CONTENT_W, rh, 'F');

    doc.setTextColor(ri % 2 === 0 ? 17 : 30, ri % 2 === 0 ? 24 : 30, ri % 2 === 0 ? 39 : 30);
    cx = MARGIN + 2;
    cells.forEach((cell, ci) => {
      if (ci === 0) doc.setFont('helvetica', 'bold');
      const lines = doc.splitTextToSize(cell, colW[ci] - 4);
      lines.forEach((l, li) => doc.text(l, cx, y + 5 + li * lineH));
      if (ci === 0) doc.setFont('helvetica', 'normal');
      cx += colW[ci];
    });

    // row border
    doc.setDrawColor(229, 231, 235);
    doc.line(MARGIN, y + rh, MARGIN + CONTENT_W, y + rh);
    y += rh;
  });
  doc.setTextColor(30, 30, 30);
  return pg;
}

function renderFAQ(doc, faq, startPage) {
  doc.addPage();
  let pg = startPage;
  let y = pageHeader(doc, 'FAQ', pg++);
  doc.setFontSize(10);

  faq.forEach((item, i) => {
    if (y > PAGE_H - 30) { doc.addPage(); y = pageHeader(doc, 'FAQ (continued)', pg++); }

    doc.setFont('helvetica', 'bold');
    doc.setTextColor(30, 30, 30);
    y = wrappedText(doc, `Q${i + 1}: ${item.question}`, MARGIN, y, CONTENT_W, 6);
    doc.setFont('helvetica', 'normal');
    doc.setTextColor(75, 85, 99);
    y = wrappedText(doc, `A: ${item.answer}`, MARGIN + 4, y, CONTENT_W - 4, 6);
    doc.setTextColor(30, 30, 30);
    y += 5;
  });
  return pg;
}

// ── Public API ───────────────────────────────────────────────────────────────

/**
 * Generate and download the full lesson pack as a PDF.
 * @param {Object} lessonData  Full lesson pack from /generate
 */
export function downloadLessonAsPDF(lessonData) {
  const doc = new jsPDF({ unit: 'mm', format: 'a4' });

  renderTitlePage(doc, lessonData);

  let pg = 2;
  doc.addPage();
  pg = renderSlides(doc, lessonData.slides, pg);
  pg = renderQuiz(doc, lessonData.quiz, pg);
  pg = renderAssignment(doc, lessonData.assignment, pg);
  pg = renderRubric(doc, lessonData.rubric, pg);
  renderFAQ(doc, lessonData.faq, pg);

  const filename = `classroomagent_${slug(lessonData.topic)}_${slug(lessonData.grade)}.pdf`;
  doc.save(filename);
}
