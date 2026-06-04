import { useState } from 'react';
import styles from './LessonDashboard.module.css';
import RefineChat from './RefineChat';
import { copySection, downloadLessonAsPDF } from '../utils/export';

const TABS = ['Slides', 'Quiz', 'Assignment', 'Rubric', 'FAQ'];

// ── Slides ──────────────────────────────────────────────────────────────────

function SlideCard({ slide }) {
  const [noteOpen, setNoteOpen] = useState(false);
  return (
    <div className={styles.slideCard}>
      <div className={styles.slideHeader}>
        <span className={styles.slideNum}>Slide {slide.slide_number}</span>
        <h3 className={styles.slideTitle}>{slide.title}</h3>
      </div>

      {/* Key points */}
      <ul className={styles.bulletList}>
        {slide.key_points.map((pt, i) => <li key={i}>{pt}</li>)}
      </ul>

      {/* Body explanation */}
      {slide.body && (
        <p className={styles.slideBody}>{slide.body}</p>
      )}

      {/* Examples */}
      {slide.examples?.length > 0 && (
        <div className={styles.slideSection}>
          <span className={styles.slideSectionLabel}>Examples</span>
          <ul className={styles.exampleList}>
            {slide.examples.map((ex, i) => <li key={i}>{ex}</li>)}
          </ul>
        </div>
      )}

      <div className={styles.slideBottomRow}>
        {/* Discussion question */}
        {slide.discussion_question && (
          <div className={styles.discussionBox}>
            <span className={styles.discussionIcon}>💬</span>
            <span>{slide.discussion_question}</span>
          </div>
        )}

        {/* Visual suggestion */}
        {slide.visual_suggestion && (
          <div className={styles.visualBox}>
            <span className={styles.visualIcon}>🖼</span>
            <span>{slide.visual_suggestion}</span>
          </div>
        )}
      </div>

      {/* Teacher note */}
      {slide.teacher_note && (
        <>
          <button className={styles.teacherNoteToggle} onClick={() => setNoteOpen(o => !o)}>
            {noteOpen ? '▲' : '▼'} Teacher note
          </button>
          {noteOpen && <div className={styles.teacherNote}>{slide.teacher_note}</div>}
        </>
      )}
    </div>
  );
}

function SlidesTab({ slides }) {
  return <>{slides.map((s, i) => <SlideCard key={i} slide={s} />)}</>;
}

// ── Quiz ─────────────────────────────────────────────────────────────────────

function QuizTab({ questions }) {
  return (
    <>
      {questions.map((q, i) => {
        const correctLetter = q.answer?.charAt(0).toUpperCase();
        return (
          <div key={i} className={styles.questionBlock}>
            <p className={styles.questionText}>
              <span className={styles.questionNum}>{i + 1}.</span>
              {q.question}
            </p>
            <ul className={styles.optionList}>
              {q.options.map((opt, j) => {
                const letter = String.fromCharCode(65 + j);
                const isCorrect = letter === correctLetter;
                return (
                  <li key={j} className={`${styles.option} ${isCorrect ? styles.optionCorrect : ''}`}>
                    <span className={`${styles.optionDot} ${isCorrect ? styles.optionDotCorrect : ''}`} />
                    {opt}
                  </li>
                );
              })}
            </ul>
            {q.explanation && <p className={styles.explanation}>💡 {q.explanation}</p>}
          </div>
        );
      })}
    </>
  );
}

// ── Assignment ────────────────────────────────────────────────────────────────

function AssignmentTab({ assignment }) {
  return (
    <div className={styles.assignmentBlock}>
      <h2 className={styles.assignmentTitle}>{assignment.title}</h2>
      <p className={styles.assignmentObjective}>{assignment.objective}</p>

      <p className={styles.sectionLabel}>Instructions</p>
      <ol className={styles.stepList}>
        {assignment.instructions.map((step, i) => <li key={i}>{step}</li>)}
      </ol>

      <div className={styles.metaRow}>
        <span className={styles.metaItem}>
          <strong>Submission:</strong> {assignment.submission_format}
        </span>
        <span className={styles.metaItem}>
          <strong>Estimated time:</strong> {assignment.estimated_time}
        </span>
      </div>
    </div>
  );
}

// ── Rubric ────────────────────────────────────────────────────────────────────

function RubricTab({ rubric }) {
  return (
    <table className={styles.rubricTable}>
      <thead>
        <tr>
          <th>Criterion</th>
          <th>Excellent</th>
          <th>Good</th>
          <th>Needs Improvement</th>
        </tr>
      </thead>
      <tbody>
        {rubric.map((row, i) => (
          <tr key={i}>
            <td className={styles.criterionCell}>{row.criterion}</td>
            <td>{row.excellent}</td>
            <td>{row.good}</td>
            <td>{row.needs_improvement}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

// ── FAQ ───────────────────────────────────────────────────────────────────────

function FAQTab({ faq }) {
  const [openIdx, setOpenIdx] = useState(null);
  return (
    <>
      {faq.map((item, i) => {
        const isOpen = openIdx === i;
        return (
          <div key={i} className={styles.faqItem}>
            <button className={styles.faqQuestion} onClick={() => setOpenIdx(isOpen ? null : i)}>
              <span>{item.question}</span>
              <svg
                className={`${styles.faqChevron} ${isOpen ? styles.faqChevronOpen : ''}`}
                width="16" height="16" viewBox="0 0 16 16" fill="none"
              >
                <path d="M3 6l5 5 5-5" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            </button>
            {isOpen && <div className={styles.faqAnswer}>{item.answer}</div>}
          </div>
        );
      })}
    </>
  );
}

// ── CopyButton ─────────────────────────────────────────────────────────────────

const SECTION_KEY = { Slides: 'slides', Quiz: 'quiz', Assignment: 'assignment', Rubric: 'rubric', FAQ: 'faq' };

function CopyButton({ tab, data }) {
  const [copied, setCopied] = useState(false);

  async function handleCopy() {
    await copySection(SECTION_KEY[tab], data[SECTION_KEY[tab]]);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }

  return (
    <button
      className={`${styles.copyBtn} ${copied ? styles.copySuccess : ''}`}
      onClick={handleCopy}
    >
      {copied ? '✓ Copied!' : `Copy ${tab}`}
    </button>
  );
}

// ── Dashboard ─────────────────────────────────────────────────────────────────

export default function LessonDashboard({ lessonData: initialData }) {
  const [activeTab, setActiveTab] = useState('Slides');
  const [data, setData] = useState(initialData);

  function handleSectionUpdated(section, updatedContent) {
    setData(prev => ({ ...prev, [section]: updatedContent }));
  }

  function renderContent() {
    switch (activeTab) {
      case 'Slides':     return <SlidesTab slides={data.slides} />;
      case 'Quiz':       return <QuizTab questions={data.quiz} />;
      case 'Assignment': return <AssignmentTab assignment={data.assignment} />;
      case 'Rubric':     return <RubricTab rubric={data.rubric} />;
      case 'FAQ':        return <FAQTab faq={data.faq} />;
      default:           return null;
    }
  }

  return (
    <div className={styles.wrapper}>
      <div className={styles.metaRow}>
        <div className={styles.meta}>
          <span className={styles.badge}>{data.topic}</span>
          <span className={styles.badge}>{data.grade}</span>
          <span className={styles.badge}>{data.subject}</span>
        </div>
        <div className={styles.exportBtns}>
          <button
            className={styles.slidesBtn}
            onClick={() => window.open(`http://localhost:8000/export/slides/${data.lesson_id}`, '_blank')}
          >
            ▶ View Slides
          </button>
          <a
            className={styles.slidesDownloadBtn}
            href={`http://localhost:8000/export/slides/${data.lesson_id}/download`}
            download
          >
            ↓ Download Slides
          </a>
          <button
            className={styles.pdfBtn}
            onClick={() => downloadLessonAsPDF(data)}
          >
            ↓ Download PDF
          </button>
        </div>
      </div>

      <div className={styles.tabBar}>
        {TABS.map(tab => (
          <button
            key={tab}
            className={`${styles.tab} ${activeTab === tab ? styles.tabActive : ''}`}
            onClick={() => setActiveTab(tab)}
          >
            {tab}
          </button>
        ))}
      </div>

      <div>
        {renderContent()}

        <div className={styles.sectionFooter}>
          <CopyButton tab={activeTab} data={data} />
          <RefineChat
            lessonId={data.lesson_id}
            activeSection={activeTab}
            onSectionUpdated={handleSectionUpdated}
          />
        </div>
      </div>
    </div>
  );
}
