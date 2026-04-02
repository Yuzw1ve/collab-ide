import React, { useEffect, useState, useRef } from 'react';
import { useParams, useSearchParams, Navigate } from 'react-router-dom';
import { SocketService } from '../services/ws';
import { api } from '../services/api';
import EditorPane from '../components/EditorPane';
import ParticipantsPanel from '../components/ParticipantsPanel';
import EventLogPanel from '../components/EventLogPanel';
import AIReviewPanel from '../components/AIReviewPanel';
import RunOutputPanel from '../components/RunOutputPanel';
import LeaderboardPanel from '../components/LeaderboardPanel';

export default function RoomPage() {
  const { roomId } = useParams();
  const [searchParams] = useSearchParams();
  const username = searchParams.get('username');
  const displayName = searchParams.get('displayName') || username;

  const [content, setContent] = useState('');
  const [language, setLanguage] = useState('python');
  const [participants, setParticipants] = useState([]);
  const [events, setEvents] = useState([]);
  const [cursors, setCursors] = useState({});
  const [review, setReview] = useState(null);
  const [isReviewLoading, setIsReviewLoading] = useState(false);
  const [output, setOutput] = useState(null);
  const [leaderboard, setLeaderboard] = useState([]);

  const ws = useRef(null);
  const version = useRef(0);
  const reviewTimeoutRef = useRef(null);

  const loadLeaderboard = async () => {
    if (!roomId) return;

    try {
      const res = await api.getLeaderboard(roomId);
      setLeaderboard(res.leaderboard || []);
    } catch (error) {
      console.error('Failed to load leaderboard:', error);
    }
  };

  useEffect(() => {
    if (!roomId || !username) return;

    ws.current = new SocketService(roomId, username, displayName, (data) => {
      switch (data.type) {
        case 'room_state':
          setContent(data.content || '');
          setParticipants(data.participants || []);
          setEvents(data.events || []);
          version.current = data.version || 0;
          loadLeaderboard();
          break;

        case 'content_update':
          version.current = data.version || version.current;
          if (data.updatedBy !== username) {
            setContent(data.content || '');
          }
          break;

        case 'participants_update':
          setParticipants(data.participants || []);
          break;

        case 'cursor_update':
          setCursors((prev) => ({
            ...prev,
            [data.username]: data.position,
          }));
          break;

        case 'event':
          if (data.event) {
            setEvents((prev) => [data.event, ...prev]);
            loadLeaderboard();
          }
          break;

        case 'ai_review':
          setReview(data.review || null);
          break;

        case 'run_output':
          setOutput(data);
          loadLeaderboard();
          break;

        default:
          break;
      }
    });

    return () => {
      ws.current?.close();
      if (reviewTimeoutRef.current) {
        clearTimeout(reviewTimeoutRef.current);
      }
    };
  }, [roomId, username, displayName]);

  useEffect(() => {
    if (!roomId) return;
    loadLeaderboard();
  }, [roomId]);

  useEffect(() => {
    if (!roomId) return;

    const trimmed = content.trim();

    if (reviewTimeoutRef.current) {
      clearTimeout(reviewTimeoutRef.current);
    }

    if (!trimmed) return;

    reviewTimeoutRef.current = setTimeout(async () => {
      try {
        setIsReviewLoading(true);
        const res = await api.aiReview(roomId, content, language, events.slice(0, 5));
        setReview(res);
      } catch (error) {
        console.error('Auto AI review failed:', error);
      } finally {
        setIsReviewLoading(false);
      }
    }, 2500);

    return () => {
      if (reviewTimeoutRef.current) {
        clearTimeout(reviewTimeoutRef.current);
      }
    };
  }, [content, language, roomId]);

  if (!username) {
    return <Navigate to="/" replace />;
  }

  const handleEdit = (newContent) => {
    if (newContent === content) return;

    setContent(newContent);
    version.current += 1;

    ws.current?.send({
      type: 'edit',
      username,
      content: newContent,
      version: version.current,
      timestamp: Math.floor(Date.now() / 1000),
    });
  };

  const handleCursor = (pos) => {
    ws.current?.send({
      type: 'cursor',
      username,
      position: pos,
    });
  };

  const requestReview = async () => {
    try {
      setIsReviewLoading(true);
      const res = await api.aiReview(roomId, content, language, events.slice(0, 5));
      setReview(res);
    } catch (error) {
      setReview({
        summary: 'AI review failed',
        issues: [],
        suggestions: [],
        mergeSuggestion: error.message || 'Unknown error',
      });
    } finally {
      setIsReviewLoading(false);
    }
  };

  const requestRun = async () => {
    try {
      const res = await api.runCode(roomId, username, language, content);
      setOutput(res);

      ws.current?.send({
        type: 'run',
        username,
        language,
        content,
      });

      loadLeaderboard();
    } catch (error) {
      setOutput({
        stdout: '',
        stderr: error.message || 'Run failed',
        exitCode: 1,
      });
    }
  };

  return (
    <div className="app-container">
      <EditorPane
        content={content}
        language={language}
        setLanguage={setLanguage}
        onEdit={handleEdit}
        onCursor={handleCursor}
      />

      <div className="sidebar">
        <ParticipantsPanel participants={participants} cursors={cursors} />
        <LeaderboardPanel leaderboard={leaderboard} />
          <EventLogPanel events={events} participants={participants} />        <AIReviewPanel
          review={review}
          onReviewRequested={requestReview}
          isReviewLoading={isReviewLoading}
        />
        <RunOutputPanel output={output} onRunRequested={requestRun} />
      </div>
    </div>
  );
}