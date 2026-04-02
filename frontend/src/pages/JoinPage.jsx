import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

function generateIncognitoName() {
  const random = Math.floor(Math.random() * 1000);
  return `Anonymous-${random}`;
}

export default function JoinPage() {
  const [user, setUser] = useState('');
  const [room, setRoom] = useState('');
  const [incognito, setIncognito] = useState(false);
  const navigate = useNavigate();

  const handleJoin = () => {
    const cleanUser = user.trim();
    const cleanRoom = room.trim();

    if (cleanUser && cleanRoom) {
      const displayName = incognito ? generateIncognitoName() : cleanUser;

      navigate(
        `/room/${encodeURIComponent(cleanRoom)}?username=${encodeURIComponent(cleanUser)}&displayName=${encodeURIComponent(displayName)}`
      );
    }
  };

  return (
    <div className="join-container">
      <div className="join-card">
        <h2 style={{ margin: 0 }}>Join Room</h2>

        <input
          placeholder="Username"
          value={user}
          onChange={e => setUser(e.target.value)}
        />

        <input
          placeholder="Room ID"
          value={room}
          onChange={e => setRoom(e.target.value)}
        />

        <label style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.9rem' }}>
          <input
            type="checkbox"
            checked={incognito}
            onChange={(e) => setIncognito(e.target.checked)}
          />
          Join in incognito mode
        </label>

        <button onClick={handleJoin}>Join Room</button>
      </div>
    </div>
  );
}