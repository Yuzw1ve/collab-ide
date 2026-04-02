import React from 'react';

export default function EventLogPanel({ events, participants = [] }) {
  const getVisibleName = (username) => {
    if (!username) return 'System';
    const participant = participants.find((p) => p.username === username);
    return participant?.displayName || username;
  };

  return (
    <div className="panel">
      <div className="panel-title">Event Log</div>
      <div style={{ maxHeight: '150px', overflowY: 'auto' }}>
        {events.map((ev, i) => (
          <div key={i} className="log-item">
            <strong>{getVisibleName(ev.username)}:</strong> {ev.details || ev.type}
          </div>
        ))}
      </div>
    </div>
  );
}