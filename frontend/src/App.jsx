import { useState } from 'react';
import InputForm from './components/InputForm';
import LessonDashboard from './components/LessonDashboard';
import './App.css';

const pageStyle = { minHeight: '100vh', background: '#f3f4f6', padding: '48px 16px' };
const backBtnStyle = {
  display: 'inline-flex', alignItems: 'center', gap: 6,
  marginBottom: 24, padding: '8px 16px', cursor: 'pointer',
  borderRadius: 8, border: '1.5px solid #d1d5db',
  background: '#fff', fontSize: '0.875rem', color: '#374151',
};

function App() {
  const [lesson, setLesson] = useState(null);

  return (
    <div style={pageStyle}>
      {!lesson ? (
        <InputForm onLessonReady={setLesson} />
      ) : (
        <div style={{ maxWidth: 900, margin: '0 auto' }}>
          <button style={backBtnStyle} onClick={() => setLesson(null)}>
            ← New lesson
          </button>
          <LessonDashboard lessonData={lesson} />
        </div>
      )}
    </div>
  );
}

export default App;
