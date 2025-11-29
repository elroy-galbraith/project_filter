export default function TranscriptCompact({ call }) {
  if (!call) return null;

  const confidence = Math.round(call.confidence * 100);
  const confidenceLevel = confidence < 50 ? 'low' : confidence < 80 ? 'medium' : 'high';

  return (
    <div className="transcript-compact">
      <h4 className="compact-header">📝 TRANSCRIPT</h4>

      <div className={`transcript-text ${call.is_distress ? 'distress' : 'normal'}`}>
        {call.transcript}
      </div>

      <div className="transcript-meta">
        <span className={`confidence-badge ${confidenceLevel}`}>
          {confidence}% confidence
        </span>
        {call.is_distress && (
          <span className="warning-badge">⚠️ Low Confidence - Partial Transcription</span>
        )}
      </div>

      <div className="audio-player-compact">
        <audio controls src={`/${call.audio_file}`} />
      </div>
    </div>
  );
}
