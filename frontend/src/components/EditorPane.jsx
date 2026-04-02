import React, { useRef } from 'react';
import Editor from '@monaco-editor/react';

export default function EditorPane({ content, language, setLanguage, onEdit, onCursor }) {
  const editorRef = useRef(null);

  const handleEditorDidMount = (editor) => {
    editorRef.current = editor;
    editor.onDidChangeCursorPosition((e) => {
      onCursor({
        lineNumber: e.position.lineNumber,
        column: e.position.column,
      });
    });
  };

  const handleChange = (value) => {
    onEdit(value ?? '');
  };

  return (
    <div style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <div style={{ padding: '10px', background: '#252526', borderBottom: '1px solid #3c3c3c' }}>
        <select value={language} onChange={(e) => setLanguage(e.target.value)}>
          <option value="python">Python</option>
          <option value="javascript">JavaScript</option>
        </select>
      </div>

      <Editor
        height="100%"
        theme="vs-dark"
        language={language}
        value={content}
        onChange={handleChange}
        onMount={handleEditorDidMount}
        options={{ automaticLayout: true, fontSize: 14 }}
      />
    </div>
  );
}