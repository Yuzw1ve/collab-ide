import React from 'react';

export default function RunOutputPanel({ output, onRunRequested }) {
  return (
    <div className="panel" style={{ borderBottom: 'none' }}>
      <div className="panel-title">
        Run Output
        <button onClick={onRunRequested} style={{ padding: '2px 8px', fontSize: '0.7rem', background: '#28a745' }}>Run</button>
      </div>
      {output ? (
        <div className="output-pre">
          {output.stdout && <div style={{ color: '#afffdf' }}>{output.stdout}</div>}
          {output.stderr && <div style={{ color: '#ffafaf' }}>{output.stderr}</div>}
          <div style={{ color: '#888', marginTop: '5px' }}>Exit code: {output.exitCode}</div>
        </div>
      ) : <p style={{ fontSize: '0.8rem', color: '#666' }}>Press Run to execute code</p>}
    </div>
  );
}