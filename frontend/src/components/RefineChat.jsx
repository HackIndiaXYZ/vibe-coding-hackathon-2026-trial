import { useState, useEffect, useRef } from 'react';
import styles from './RefineChat.module.css';
import { API_BASE } from '../utils/api';

export default function RefineChat({ lessonId, activeSection, onSectionUpdated }) {
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [history, setHistory] = useState([]);
  const historyRef = useRef(null);

  // Scroll history to bottom whenever it grows
  useEffect(() => {
    if (historyRef.current) {
      historyRef.current.scrollTop = historyRef.current.scrollHeight;
    }
  }, [history]);

  async function handleSend() {
    const instruction = input.trim();
    if (!instruction || loading) return;

    setInput('');
    setHistory(h => [...h, { type: 'instruction', text: instruction, section: activeSection }]);
    setLoading(true);

    try {
      const res = await fetch(`${API_BASE}/refine`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          lesson_id: lessonId,
          section: activeSection.toLowerCase(),
          instruction,
        }),
      });

      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        throw new Error(body.detail || `Server error ${res.status}`);
      }

      const data = await res.json();
      onSectionUpdated(data.section, data.updated_content);
      setHistory(h => [...h, { type: 'success', text: `Updated ✓  (${data.section})` }]);
    } catch (err) {
      setHistory(h => [...h, { type: 'error', text: err.message || 'Something went wrong.' }]);
    } finally {
      setLoading(false);
    }
  }

  function handleKeyDown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }

  return (
    <div className={styles.panel}>
      <div className={styles.sectionLabel}>
        Refining: <span>{activeSection}</span>
      </div>

      {history.length > 0 && (
        <div className={styles.history} ref={historyRef}>
          {history.map((msg, i) => (
            <div
              key={i}
              className={
                msg.type === 'instruction' ? styles.msgInstruction
                : msg.type === 'success'    ? styles.msgSuccess
                :                            styles.msgError
              }
            >
              {msg.text}
            </div>
          ))}
        </div>
      )}

      <div className={styles.inputRow}>
        <input
          className={styles.input}
          type="text"
          placeholder="e.g. Make the quiz harder / Add an India example to slide 3"
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={loading}
        />
        <button
          className={styles.sendBtn}
          onClick={handleSend}
          disabled={loading || !input.trim()}
        >
          {loading ? <span className={styles.spinner} /> : null}
          {loading ? 'Sending…' : 'Send'}
        </button>
      </div>
    </div>
  );
}
