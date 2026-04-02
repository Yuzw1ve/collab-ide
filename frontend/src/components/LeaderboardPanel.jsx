import React from 'react';

export default function LeaderboardPanel({ leaderboard }) {
  return (
    <div className="panel">
      <h3>Leaderboard</h3>

      {leaderboard && leaderboard.length > 0 ? (
        <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
          {leaderboard.map((item, index) => {
            const visibleName = item.displayName || item.username;

            return (
              <li
                key={item.username}
                style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  padding: '8px 0',
                  borderBottom: '1px solid #333',
                }}
              >
                <span>
                  #{index + 1} {visibleName}
                </span>
                <strong>{item.score} pts</strong>
              </li>
            );
          })}
        </ul>
      ) : (
        <p style={{ margin: 0, color: '#999' }}>No activity yet</p>
      )}
    </div>
  );
}