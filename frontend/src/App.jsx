import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import JoinPage from './pages/JoinPage';
import RoomPage from './pages/RoomPage';
import './styles.css';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<JoinPage />} />
        <Route path="/room/:roomId" element={<RoomPage />} />
        <Route path="*" element={<Navigate to="/" />} />
      </Routes>
    </BrowserRouter>
  );
}