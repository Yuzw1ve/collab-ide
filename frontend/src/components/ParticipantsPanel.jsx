import React from 'react';
import { getInitials, stringToColor } from '../utils/formatters';

export default function ParticipantsPanel({ participants, cursors }) {
  return (
    <div className="panel">
      <div className="panel-title">Participants ({participants.length})</div>

      {participants.map((p) => {
        const visibleName = p.displayName || p.username;

        return (
          <div key={p.username} className="participant-item">
            <div
              className="avatar"
              style={{ backgroundColor: stringToColor(visibleName) }}
            >
              {getInitials(visibleName)}
            </div>

            <span>{visibleName}</span>

            {cursors[p.username] && (
              <span style={{ fontSize: '0.7rem', color: '#888' }}>
                {cursors[p.username].lineNumber}:{cursors[p.username].column}
              </span>
            )}
          </div>
        );
      })}
    </div>
  );
}