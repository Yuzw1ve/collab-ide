import React from 'react';

export default function AIReviewPanel({ review, onReviewRequested }) {
  return (
    <div className="panel">
      <div className="panel-title">
        AI Review 
        <button onClick={onReviewRequested} style={{ padding: '2px 8px', fontSize: '0.7rem' }}>Review</button>
      </div>
      {review ? (
        <div style={{ fontSize: '0.85rem' }}>
          <p><strong>Summary:</strong> {review.summary}</p>
          {review.issues?.map((is, i) => (
            <div key={i} className="issue-item">L{is.line}: {is.message}</div>
          ))}
          <p style={{ fontStyle: 'italic', color: '#aaa' }}>{review.mergeSuggestion}</p>
        </div>
      ) : <p style={{ fontSize: '0.8rem', color: '#666' }}>No review yet</p>}
    </div>
  );
}