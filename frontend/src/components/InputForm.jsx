import { useState, useRef } from 'react';
import styles from './InputForm.module.css';
import { API_BASE } from '../utils/api';

const GRADES = Array.from({ length: 12 }, (_, i) => `Class ${i + 1}`);
const SUBJECTS = ['Science', 'Mathematics', 'English', 'History', 'Geography', 'Computer Science'];

export default function InputForm({ onLessonReady }) {
  const [topic, setTopic] = useState('');
  const [grade, setGrade] = useState(GRADES[0]);
  const [subject, setSubject] = useState(SUBJECTS[0]);
  const [struggleAreas, setStruggleAreas] = useState([]);
  const [tagDraft, setTagDraft] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const tagInputRef = useRef(null);

  function addTag() {
    const trimmed = tagDraft.trim();
    if (trimmed && !struggleAreas.includes(trimmed)) {
      setStruggleAreas(prev => [...prev, trimmed]);
    }
    setTagDraft('');
  }

  function removeTag(tag) {
    setStruggleAreas(prev => prev.filter(t => t !== tag));
  }

  function handleTagKeyDown(e) {
    if (e.key === 'Enter') {
      e.preventDefault();
      addTag();
    } else if (e.key === 'Backspace' && tagDraft === '' && struggleAreas.length > 0) {
      setStruggleAreas(prev => prev.slice(0, -1));
    }
  }

  async function handleSubmit(e) {
    e.preventDefault();
    if (!topic.trim()) {
      setError('Please enter a topic.');
      return;
    }
    setError('');
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ topic: topic.trim(), grade, subject, struggle_areas: struggleAreas }),
      });
      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        throw new Error(body.detail || `Server error ${res.status}`);
      }
      const data = await res.json();
      onLessonReady(data);
    } catch (err) {
      setError(err.message || 'Something went wrong. Please try again.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className={styles.card}>
      <h1 className={styles.title}>ClassroomAgent</h1>
      <p className={styles.subtitle}>Generate a full lesson plan in seconds.</p>

      <form onSubmit={handleSubmit} noValidate>
        <div className={styles.field}>
          <label className={styles.label}>Topic</label>
          <input
            className={styles.input}
            type="text"
            placeholder="e.g. Water cycle"
            value={topic}
            onChange={e => setTopic(e.target.value)}
            disabled={loading}
          />
        </div>

        <div className={styles.field}>
          <label className={styles.label}>Grade</label>
          <select
            className={styles.select}
            value={grade}
            onChange={e => setGrade(e.target.value)}
            disabled={loading}
          >
            {GRADES.map(g => <option key={g}>{g}</option>)}
          </select>
        </div>

        <div className={styles.field}>
          <label className={styles.label}>Subject</label>
          <select
            className={styles.select}
            value={subject}
            onChange={e => setSubject(e.target.value)}
            disabled={loading}
          >
            {SUBJECTS.map(s => <option key={s}>{s}</option>)}
          </select>
        </div>

        <div className={styles.field}>
          <label className={styles.label}>Struggle Areas</label>
          <div
            className={styles.tagBox}
            onClick={() => tagInputRef.current?.focus()}
          >
            {struggleAreas.map(tag => (
              <span key={tag} className={styles.tag}>
                {tag}
                <button
                  type="button"
                  className={styles.tagRemove}
                  onClick={e => { e.stopPropagation(); removeTag(tag); }}
                  aria-label={`Remove ${tag}`}
                >
                  ×
                </button>
              </span>
            ))}
            <input
              ref={tagInputRef}
              className={styles.tagInput}
              type="text"
              placeholder={struggleAreas.length === 0 ? 'Type a concept and press Enter…' : ''}
              value={tagDraft}
              onChange={e => setTagDraft(e.target.value)}
              onKeyDown={handleTagKeyDown}
              onBlur={addTag}
              disabled={loading}
            />
          </div>
          <span className={styles.hint}>Press Enter to add each concept.</span>
        </div>

        <button className={styles.button} type="submit" disabled={loading}>
          {loading && <span className={styles.spinner} />}
          {loading ? 'Generating lesson…' : 'Generate Lesson'}
        </button>

        {error && <div className={styles.error}>{error}</div>}
      </form>
    </div>
  );
}
