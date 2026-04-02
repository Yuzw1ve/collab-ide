const BASE_URL = '/api';

export const api = {
  getRoom: (roomId) => fetch(`${BASE_URL}/rooms/${roomId}`).then(r => r.json()),

  getLeaderboard: (roomId) =>
    fetch(`${BASE_URL}/rooms/${roomId}/leaderboard`).then(r => r.json()),

  runCode: (roomId, username, language, content) =>
    fetch(`${BASE_URL}/run`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ roomId, username, language, content })
    }).then(r => r.json()),

  aiReview: (roomId, content, language, recentEvents) =>
    fetch(`${BASE_URL}/ai/review`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ roomId, content, language, recentEvents })
    }).then(r => r.json()),
};